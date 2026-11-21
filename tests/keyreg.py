# 실행 중 keydown/keyup/paste 리스너 등록 순서·대상·단계 기록
import sys, asyncio, json
from playwright.async_api import async_playwright
INIT = r"""(()=>{const orig=EventTarget.prototype.addEventListener;window.__KREG=[];
EventTarget.prototype.addEventListener=function(t,f,o){if(['keydown','keyup','paste','copy','keypress'].includes(t)){
 const cap=typeof o==='boolean'?o:!!(o&&o.capture);const who=this===window?'window':this===document?'document':(this.id?'#'+this.id:this.tagName||'?');
 const line=(new Error().stack.split('\n')[2]||'').replace(/.*\.html:/,'');window.__KREG.push([t,who,cap,line,String(f).slice(0,60)]);}
 return orig.call(this,t,f,o);};})();"""
async def main(p):
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path=next(p for p in [__import__('os').environ.get('PC_CHROME',''),'/usr/bin/google-chrome','/opt/pw-browsers/chromium'] if p and __import__('os').path.exists(p)), args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1500, 'height': 950}); await pg.add_init_script(INIT)
        await pg.goto('file://' + p); await pg.wait_for_timeout(2500)
        for r in await pg.evaluate('()=>window.__KREG'): print(r)
        await b.close()
asyncio.run(main(sys.argv[1]))
