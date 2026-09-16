"""Resumable pooled download of the same read-only public capture.
Requires aiohttp and lxml only when refreshing; deployment has no dependencies.
"""
import asyncio
import hashlib
import json
import mimetypes
import urllib.parse as up
from pathlib import Path
import aiohttp
import mirror as m

queued=set()
queue=asyncio.PriorityQueue()
done=0

async def add(url,page=False,priority=2):
    key=(url,page)
    if key in queued:return
    queued.add(key)
    await queue.put((priority,url,page))

async def get(session,url,page):
    table=m.state['pages' if page else 'assets']
    path=m.path_for(url,page)
    target=m.CACHE/path
    if target.exists() and target.stat().st_size:
        data=target.read_bytes()
        if url not in table:
            canonical=up.urlunsplit(up.urlsplit(url)._replace(query=''))
            entry=table.get(canonical)
            table[url]=dict(entry) if entry else {'path':path,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':mimetypes.guess_type(path)[0] or '', 'source':'live-demo','status':200}
        return data
    for attempt in range(2):
        try:
            async with session.get(url) as response:
                data=await response.read()
                content_type=response.headers.get('Content-Type','')
                if response.status>=400 and not (page and response.status==404 and b'wp-theme-floka' in data):
                    m.state['failures'][url]=f'HTTP {response.status}'
                    return None
                if not page and 'text/html' in content_type:
                    m.state['failures'][url]='Asset returned HTML';return None
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
                table[url]={'path':path,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':content_type,'source':'live-demo','status':response.status}
                m.state['failures'].pop(url,None)
                return data
        except (asyncio.TimeoutError,aiohttp.ClientError) as e:
            m.state['failures'][url]=str(e) or type(e).__name__
    return None

async def worker(session):
    global done
    while True:
        priority,url,page=await queue.get()
        try:
            data=await get(session,url,page)
            if data:
                if page:
                    pages,assets=m.inspect_page(data,url)
                    for p in pages:await add(p,True,1)
                    for a in assets:await add(a,False,0 if url==m.ORIGIN+'/' else 2)
                elif '.css' in up.urlsplit(url).path or up.urlsplit(url).netloc=='fonts.googleapis.com':
                    for a in m.urls_in_text(data.decode('utf-8',errors='replace'),url):await add(a,False,0)
            done+=1
            if done%25==0:
                m.save_state();print(f"Complete {done}; pages {len(m.state['pages'])}; assets {len(m.state['assets'])}; queued {queue.qsize()}; failures {len(m.state['failures'])}",flush=True)
        finally:queue.task_done()

async def main():
    m.package_assets()
    await add(m.ORIGIN+'/',True,0)
    timeout=aiohttp.ClientTimeout(total=45,connect=20)
    async with aiohttp.ClientSession(trust_env=True,timeout=timeout,headers={'User-Agent':'FlokaLicensedFrontendExport/1.0'},connector=aiohttp.TCPConnector(limit=12)) as session:
        workers=[asyncio.create_task(worker(session)) for _ in range(12)]
        await queue.join()
        for task in workers:task.cancel()
    m.save_state()
    print(f"FINISHED {len(m.state['pages'])} pages / {len(m.state['assets'])} asset references / {len(m.state['failures'])} unresolved",flush=True)

if __name__=='__main__':asyncio.run(main())
