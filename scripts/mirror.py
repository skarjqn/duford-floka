"""Read-only capture of Floka's publicly linked pages and frontend assets.

Never requests admin, checkout mutations, add-to-cart, or form endpoints.
Preserves original markup; build.py only rewrites deployment URLs.
"""
import concurrent.futures as cf
import hashlib
import html as htmlmod
import json
import mimetypes
import os
import re
import threading
import time
import urllib.error
import urllib.parse as up
import urllib.request as ur
from pathlib import Path
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'capture'
ORIGIN = 'https://floka.casethemes.net'
PACKAGE = Path(os.environ.get('FLOKA_PACKAGE_ROOT', str(ROOT/'licensed-package'/'Floka_FullPackage')))
STATE = ROOT / 'capture-manifest.json'
ASSET_EXT = re.compile(r'\.(?:css|js|png|jpg|jpeg|webp|gif|svg|ico|woff2?|ttf|eot|otf|mp4|webm|avif|json)(?:$|[?#])', re.I)
URL_RE = re.compile(r'https?://[^\s"\'<>\\)]+|//(?:fonts\.(?:googleapis|gstatic)\.com|floka\.casethemes\.net)/[^\s"\'<>\\)]+')
FORBIDDEN = ('/wp-admin/', '/wp-json/', '/feed/', '/xmlrpc.php', '/wp-login.php', '/wp-comments-post.php', '/wc-logs/', '/woocommerce_uploads/')
lock = threading.Lock()
state = json.loads(STATE.read_text()) if STATE.exists() else {'pages': {}, 'assets': {}, 'failures': {}, 'excluded': [], 'captured_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}

def clean(url, base=ORIGIN + '/'):
    url = htmlmod.unescape(url.replace('\\/', '/')).strip()
    return up.urljoin(base, url).split('#')[0]

def safe(url):
    p = up.urlsplit(url)
    return p.scheme in ('http','https') and not any(x in p.path for x in FORBIDDEN) and not any(k in up.parse_qs(p.query) for k in ('add-to-cart','wc-ajax','s','replytocom','rest_route'))

def page_url(url, base=ORIGIN+'/'):
    url = clean(url, base)
    p = up.urlsplit(url)
    if p.netloc != 'floka.casethemes.net' or not safe(url) or ASSET_EXT.search(url) or '/wp-content/' in p.path or '/wp-includes/' in p.path:
        return None
    if p.query and not all(k in ('sidebar-blog','blog_layout','blog_sidebar','sidebar','layout','product_count','orderby') for k in up.parse_qs(p.query)):
        return None
    return url

def path_for(url, page=False):
    p = up.urlsplit(url)
    if p.netloc == 'floka.casethemes.net':
        path = p.path.lstrip('/')
        if page:
            if p.query: path = path.rstrip('/') + '/_variant-' + hashlib.sha1(p.query.encode()).hexdigest()[:10] + '/'
            path = path.rstrip('/') + '/index.html' if path else 'index.html'
        return path
    name = Path(p.path).name or 'resource'
    if p.netloc == 'fonts.googleapis.com': name = 'font.css'
    return '_external/' + p.netloc + '/' + hashlib.sha1(url.encode()).hexdigest()[:12] + '/' + name

def save_state():
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False))

def fetch(url, page=False):
    table = state['pages' if page else 'assets']
    if url in table and (CACHE / table[url]['path']).exists():
        return (CACHE / table[url]['path']).read_bytes()
    path = path_for(url,page)
    target = CACHE / path
    canonical = up.urlunsplit(up.urlsplit(url)._replace(query=''))
    if not page and canonical in table and target.exists():
        with lock: table[url]=dict(table[canonical])
        return target.read_bytes()
    try:
        req = ur.Request(url, headers={'User-Agent':'FlokaLicensedFrontendExport/1.0', 'Accept-Encoding':'identity'})
        with ur.urlopen(req, timeout=35) as response:
            data = response.read()
            content_type = response.headers.get('Content-Type','')
            status = response.status
        if not page and ('text/html' in content_type) and not path.endswith('.html'):
            raise ValueError('Asset returned HTML')
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
        entry = {'path':path,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':content_type,'source':'live-demo','status':status}
        with lock:
            table[url] = entry
            state['failures'].pop(url,None)
        return data
    except urllib.error.HTTPError as e:
        if page and e.code == 404:
            data=e.read()
            if b'wp-theme-floka' in data:
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
                with lock: table[url]={'path':path,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':'text/html','source':'live-demo','status':404}
                return data
        with lock: state['failures'][url]=str(e)
    except Exception as e:
        with lock: state['failures'][url]=str(e)
    return None

def urls_in_text(text, base):
    text=htmlmod.unescape(text.replace('\\/', '/'))
    found=set()
    for match in URL_RE.finditer(text):
        u=clean(match.group(),base)
        p=up.urlsplit(u)
        if safe(u) and (ASSET_EXT.search(u) or p.netloc=='fonts.googleapis.com') and p.netloc in ('floka.casethemes.net','fonts.googleapis.com','fonts.gstatic.com','secure.gravatar.com'):
            found.add(u)
    for m in re.finditer(r'url\(\s*["\']?([^\s"\')]+)',text):
        if m[1].startswith(('data:','#')): continue
        u=clean(m[1],base)
        if safe(u) and up.urlsplit(u).netloc in ('floka.casethemes.net','fonts.gstatic.com','fonts.googleapis.com'): found.add(u)
    return found

def inspect_page(data,url):
    doc=html.fromstring(data)
    pages=set();assets=urls_in_text(data.decode('utf-8',errors='replace'),url)
    for el in doc.xpath('//*[@href or @src or @srcset]'):
        tag=el.tag
        for attr in ('src','href','poster','data-src'):
            v=el.get(attr)
            if not v or v.startswith(('#','mailto:','tel:','data:','javascript:')):continue
            u=clean(v,url)
            if tag=='a' and attr=='href':
                pu=page_url(u)
                if pu:pages.add(pu)
            if ASSET_EXT.search(u) or (tag=='link' and 'stylesheet' in el.get('rel','')):
                if safe(u) and up.urlsplit(u).netloc in ('floka.casethemes.net','fonts.googleapis.com','fonts.gstatic.com','secure.gravatar.com'): assets.add(u)
        for part in el.get('srcset','').split(','):
            if part.strip():
                u=clean(part.strip().split()[0],url)
                if ASSET_EXT.search(u) and safe(u):assets.add(u)
    return pages,assets

def package_assets():
    # Existing exact paths are reused byte-for-byte; no replacement typography/effects.
    for prefix,folder in [('wp-content/themes/floka/',PACKAGE/'Theme Install/floka'),('wp-content/plugins/case-addons/',PACKAGE/'Plugins/case-addons')]:
        for src in folder.rglob('*'):
            if not src.is_file() or src.suffix.lower() not in ('.js','.woff','.woff2','.ttf','.eot','.svg','.png','.webp','.jpg'):continue
            rel=prefix+str(src.relative_to(folder))
            target=CACHE/rel
            if target.exists():continue
            data=src.read_bytes();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            state['assets'][ORIGIN+'/'+rel]={'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':mimetypes.guess_type(rel)[0] or '', 'source':'purchased-package'}

def main():
    CACHE.mkdir(parents=True,exist_ok=True)
    package_assets()
    queue={ORIGIN+'/'}
    seen=set(); all_assets=set()
    with cf.ThreadPoolExecutor(max_workers=12) as pool:
        # Make the reference homepage available for early browser comparison.
        first=fetch(ORIGIN+'/',True)
        if first:
            _,primary=inspect_page(first,ORIGIN+'/')
            for wave in range(3):
                more=set()
                fs={pool.submit(fetch,u):u for u in primary}
                for f in cf.as_completed(fs):
                    u=fs[f];data=f.result()
                    if data and ('.css' in up.urlsplit(u).path or up.urlsplit(u).netloc=='fonts.googleapis.com'):
                        more.update(urls_in_text(data.decode('utf-8',errors='replace'),u))
                save_state();print(f'Homepage asset pass {wave+1}: {len(state["assets"])} saved',flush=True)
                primary=more
        while queue:
            batch=sorted(queue-seen);queue=set()
            if not batch:break
            for url in batch:seen.add(url)
            futures={pool.submit(fetch,u,True):u for u in batch}
            for f in cf.as_completed(futures):
                u=futures[f];data=f.result()
                if data:
                    pages,assets=inspect_page(data,u);queue.update(pages-seen);all_assets.update(assets)
                if len(state['pages'])%10==0:save_state();print(f"Pages {len(state['pages'])}; pending {len(queue)}; asset references {len(all_assets)}",flush=True)
            save_state()
            if len(seen)>500:
                state['excluded']+=sorted(queue-seen);break
        seen_assets=set()
        pending=all_assets
        # CSS/font imports recurse. Script public paths are retained for lazy chunks.
        while pending:
            batch=sorted(pending-seen_assets);pending=set()
            if not batch:break
            seen_assets.update(batch)
            futures={pool.submit(fetch,u):u for u in batch}
            done=0
            for f in cf.as_completed(futures):
                u=futures[f];data=f.result();done+=1
                if data and ('.css' in up.urlsplit(u).path or up.urlsplit(u).netloc=='fonts.googleapis.com'):
                    pending.update(urls_in_text(data.decode('utf-8',errors='replace'),u)-seen_assets)
                if done%50==0:save_state();print(f"Assets {done}/{len(batch)}; saved {len(state['assets'])}; failures {len(state['failures'])}",flush=True)
            save_state()
    print(f"Capture finished: {len(state['pages'])} pages, {len(state['assets'])} assets, {len(state['failures'])} failures",flush=True)

if __name__=='__main__': main()
