"""Build the captured frontend with portable, local asset and page URLs.

No layout CSS, content, typography, or animation timings are authored here.
"""
import argparse
import hashlib
import html
import json
import re
import shutil
import urllib.parse as up
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://floka.casethemes.net'
parser=argparse.ArgumentParser()
parser.add_argument('--base', default='/', help='GitHub project base, e.g. /floka-clone/')
parser.add_argument('--output', default='site')
args=parser.parse_args()
BASE='/' + args.base.strip('/')+'/' if args.base.strip('/') else '/'
DEST=ROOT/args.output
manifest=json.loads((ROOT/'capture-manifest.json').read_text())
mapping={}
for group in ('pages','assets'):
    for url,entry in manifest[group].items():
        path=entry['path']
        if group=='pages':path=path.removesuffix('index.html')
        mapping[url]=BASE+path
        if group=='assets':
            # Prefer one canonical file for query-string version aliases.
            p=up.urlsplit(url)
            mapping.setdefault(up.urlunsplit(p._replace(query='')),BASE+path)

replacements={}
for url,target in mapping.items():
    replacements[url]=target
    replacements[url.replace('/','\\/')]=target.replace('/','\\/')
    replacements[html.escape(url,quote=False)]=target
    if url.startswith('https://'):
        replacements[url[6:]]=target
trie={}
for url,target in replacements.items():
    branch=trie
    for char in url:branch=branch.setdefault(char,{})
    branch['']=target
starts=re.compile(r'https?:|//|\\/\\/')

def replace_urls(text):
    # Longest-prefix replacement with a trie avoids a huge regex alternation.
    parts=[];position=0
    for match in starts.finditer(text):
        start=match.start()
        if start<position:continue
        branch=trie;cursor=start;replacement=None;end=start
        while cursor<len(text) and text[cursor] in branch:
            branch=branch[text[cursor]];cursor+=1
            if '' in branch:replacement=branch[''];end=cursor
        if replacement is not None:
            parts.extend((text[position:start],replacement));position=end
    parts.append(text[position:])
    return ''.join(parts)

def rewrite(text, rel):
    # Only URL strings are changed. Never unescape slash characters globally:
    # doing so would corrupt original JavaScript regex literals.
    text=replace_urls(text)
    text=text.replace((ORIGIN+'/').replace('/','\\/'),BASE.replace('/','\\/'))
    text=text.replace('//floka.casethemes.net/',BASE)
    text=text.replace(ORIGIN+'/',BASE)
    text=text.replace('http://floka.casethemes.net/',BASE)
    # Root-relative assets and actions. Relative CSS font paths remain untouched.
    if BASE!='/':
        text=re.sub(r'(["\'(=])/(?!/)(?=(?:wp-content|wp-includes|wp-json|wp-admin)/)',lambda m:m[1]+BASE,text)
        text=re.sub(r'(action=["\'])/(?!/)',lambda m:m[1]+BASE,text)
    return text

DEST.mkdir(parents=True,exist_ok=True)
files={}
for group in ('pages','assets'):
    for url,entry in manifest[group].items(): files[entry['path']]=entry
for rel,entry in files.items():
    src=ROOT/'capture'/rel
    if not src.exists():continue
    out=DEST/rel;out.parent.mkdir(parents=True,exist_ok=True)
    if src.suffix.lower() in ('.html','.css','.js','.json','.svg') or 'text/css' in entry.get('content_type',''):
        text=rewrite(src.read_text(errors='replace'),rel)
        if src.suffix=='.html':
            original_url=next(u for u,e in manifest['pages'].items() if e['path']==rel)
            def local_href(match):
                value=html.unescape(match[2])
                if value.startswith(('#','/','http:','https:','mailto:','tel:','javascript:','file:')):return match[0]
                target=mapping.get(up.urljoin(original_url,value))
                return match[1]+target+match[3] if target else match[0]
            text=re.sub(r'(href=["\'])([^"\']+)(["\'])',local_href,text)
            # Original CF7/WooCommerce forms must never submit to the source vendor.
            script=f'<script src="{BASE}_local/backend-boundary.js"></script>'
            text=text.replace('<head>','<head>'+script,1)
        out.write_text(text)
    else:shutil.copyfile(src,out)
local=DEST/'_local';local.mkdir(exist_ok=True)
shutil.copyfile(ROOT/'scripts/backend-boundary.js',local/'backend-boundary.js')
(DEST/'.nojekyll').touch()
notfound=DEST/'404-error/index.html'
if notfound.exists():shutil.copyfile(notfound,DEST/'404.html')
report={'base':BASE,'page_urls':len(manifest['pages']),'page_files':len({e['path'] for e in manifest['pages'].values()}),'asset_files':len({e['path'] for e in manifest['assets'].values()}),'unresolved_fetches':manifest['failures'],'visual_css_overrides':0,'text_replacements':0}
(ROOT/('build-report.json' if args.output=='site' else args.output+'-build-report.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in report.items() if k!='unresolved_fetches'},ensure_ascii=False))
