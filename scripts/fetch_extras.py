"""Capture lazy runtime chunks explicitly named in the original webpack manifest."""
import asyncio
import re
import aiohttp
import capture_async as c

async def main():
    runtime=c.m.CACHE/'wp-content/plugins/elementor/assets/js/webpack.runtime.min.js'
    urls=set()
    for name in re.findall(r'"([\w.-]+\.bundle\.min\.js)"',runtime.read_text()):
        urls.add(c.m.ORIGIN+'/wp-content/plugins/elementor/assets/js/'+name)
    # Names and paths come from AssetsLoader in the captured frontend.js.
    for rel in ('lib/dialog/dialog.min.js','lib/share-link/share-link.min.js','lib/swiper/v8/swiper.min.js','lib/swiper/v8/css/swiper.min.css','css/conditionals/lightbox.min.css','css/conditionals/dialog.min.css'):
        urls.add(c.m.ORIGIN+'/wp-content/plugins/elementor/assets/'+rel)
    urls.add(c.m.ORIGIN+'/wp-content/uploads/elementor/css/custom-lightbox.min.css')
    report=c.m.ROOT/'verification-report.json'
    if report.exists():
        for url in c.json.loads(report.read_text()).get('external_script_or_image_references',[]):
            if 'secure.gravatar.com/avatar/' in url:urls.add(url)
    async with aiohttp.ClientSession(trust_env=True,timeout=aiohttp.ClientTimeout(total=45),connector=aiohttp.TCPConnector(limit=8)) as session:
        await asyncio.gather(*(c.get(session,u,False) for u in urls))
    c.m.save_state()
    print('Lazy chunks captured:',sum(u in c.m.state['assets'] for u in urls),'of',len(urls))

if __name__=='__main__':asyncio.run(main())
