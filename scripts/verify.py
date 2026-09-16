"""Checks real export risks: text/DOM fidelity, local links/assets, script syntax."""
import collections
import hashlib
import json
import re
import subprocess
import urllib.parse as up
from pathlib import Path
from lxml import html

ROOT=Path(__file__).resolve().parents[1]
state=json.loads((ROOT/'capture-manifest.json').read_text())
site=ROOT/'site'
errors=[];missing=collections.Counter();external=set();texts_equal=0;dom_equal=0
def content(doc):
    return [' '.join(t.split()) for t in doc.xpath('//body//text()[not(ancestor::script) and not(ancestor::style)]') if t.strip()]
def shape(doc):
    return [(e.tag,e.get('class',''),e.get('style','').replace('https://floka.casethemes.net/','/')) for e in doc.xpath('//body//*') if e.tag not in ('script','style')]
for url,entry in state['pages'].items():
    raw=html.parse(str(ROOT/'capture'/entry['path']));built=html.parse(str(site/entry['path']))
    if content(raw)==content(built):texts_equal+=1
    else:errors.append({'page':url,'error':'Visible text changed'})
    if shape(raw)==shape(built):dom_equal+=1
    else:errors.append({'page':url,'error':'DOM classes/structure/style changed'})
    for el in built.xpath('//*[@src or @href]'):
        attr='src' if el.get('src') else 'href'
        ref=el.get(attr)
        if not ref or ref.startswith(('#','mailto:','tel:','data:','javascript:')):continue
        p=up.urlsplit(ref)
        if p.scheme in ('https','http') or ref.startswith('//'):
            if attr=='src' or el.tag=='link' and el.get('rel')=='stylesheet':external.add(ref)
            continue
        if '/wp-json/' in ref or '/xmlrpc' in ref or ref.endswith('.php') or '/feed/' in ref:continue
        path=site/p.path.lstrip('/') if ref.startswith('/') else (site/entry['path']).parent/p.path
        if path.is_dir():path=path/'index.html'
        if not path.exists():missing[ref]+=1

scripts=[];json_data_files=[];script_count=0
for p in site.rglob('*.js'):
    try:
        json.loads(p.read_text());json_data_files.append(str(p.relative_to(site)));continue
    except (ValueError,UnicodeError):pass
    script_count+=1
    check=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
    if check.returncode:scripts.append({'file':str(p.relative_to(site)),'error':check.stderr[:500]})

report={'page_count':len(state['pages']),'visible_text_identical':texts_equal,'body_dom_classes_and_inline_styles_identical':dom_equal,'text_or_structure_errors':errors,'missing_html_references':dict(missing),'external_script_or_image_references':sorted(external),'javascript_syntax_errors':scripts,'source_fetch_failures':state['failures'],'largest_files':[{'path':str(p.relative_to(site)),'bytes':p.stat().st_size} for p in sorted((p for p in site.rglob('*') if p.is_file()),key=lambda p:p.stat().st_size,reverse=True)[:10]]}
report['javascript_files_checked']=script_count
report['original_json_icon_catalogs']=json_data_files
(ROOT/'verification-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in report.items() if k not in ('source_fetch_failures','largest_files')},indent=2,ensure_ascii=False))
