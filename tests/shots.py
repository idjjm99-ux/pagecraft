import sys; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__))); from pcenv import CHROME, HERE; import os
import asyncio,sys,json
from playwright.async_api import async_playwright
HTML=sys.argv[1]; OUT=sys.argv[2]
THEMES=sys.argv[3].split(',')
TPL=[int(x) for x in (sys.argv[4] if len(sys.argv)>4 else '4,7,5,16').split(',')]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':1700,'height':1100})
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('dialog',lambda d:asyncio.ensure_future(d.dismiss()))
        await pg.goto('file://'+HTML);await pg.wait_for_timeout(2500);await pg.add_style_tag(content='.rv-guide{display:none!important;pointer-events:none!important}')
        await pg.keyboard.press('Escape');await pg.wait_for_timeout(800)
        await pg.evaluate("document.querySelectorAll('.rv-guide').forEach(e=>e.remove())");await pg.click('[data-action=addPage]');await pg.wait_for_timeout(800)
        for t in TPL:
            await pg.evaluate("document.querySelectorAll('.rv-guide').forEach(e=>e.remove())");await pg.click(f'#templateGrid [data-template="{t}"]');await pg.wait_for_timeout(250)
        await pg.evaluate("document.querySelectorAll('.rv-guide').forEach(e=>e.remove())");await pg.click('#confirmTemplate');await pg.wait_for_timeout(1200)
        await pg.select_option('#themeScope','document')
        pages=await pg.evaluate("Revival.getProject().pages.map(p=>[p.id,p.templateId])")
        mine=[(pid,t) for pid,t in pages if t in TPL][-len(TPL):]
        res={}
        for th in THEMES:
            ok=await pg.evaluate(f"[...document.querySelectorAll('#themeSelect option')].some(o=>o.value==='{th}')")
            if not ok:
                await pg.evaluate(f"(()=>{{const s=document.querySelector('#themeSelect');const o=document.createElement('option');o.value='{th}';o.textContent='{th}';s.append(o);}})()")
            await pg.select_option('#themeSelect',th);await pg.wait_for_timeout(700)
            for pid,t in mine:
                await pg.evaluate(f"Revival.go('{pid}')");await pg.wait_for_timeout(450)
                st=pg.locator('#stageHost .rv-stage').first
                await st.screenshot(path=f'{OUT}/{th}_{t}.png')
                info=await pg.evaluate("""[...document.querySelectorAll('#stageHost .rv-stage .rv-object[data-role="toc-entry"]')].map(n=>{const c=getComputedStyle(n);const t=n.querySelector('.rv-text-content');return [n.classList.contains('pc-theme-card'),n.dataset.cardMode||'',getComputedStyle(n,'::before').backgroundColor,c.borderTopWidth+' '+c.borderTopColor,c.borderLeftWidth,c.borderRadius,t?getComputedStyle(t).color:'']})""")
                res[f'{th}_{t}']=info[:2]
        json.dump(res,open(f'{OUT}/info.json','w'),ensure_ascii=False,indent=0)
        print('errors',errs[:5])
        await b.close()
asyncio.run(main())
