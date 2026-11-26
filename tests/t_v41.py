# v12.41 시험: 테마별 목차 칸 · 상단 띠
import sys; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__))); from pcenv import ver_ok, CHROME, HERE; import os
import asyncio,sys,json,base64,zipfile,io
from playwright.async_api import async_playwright
HTML=sys.argv[1]
R=[]
def ok(name,cond,detail=''):R.append((name,bool(cond),detail));print(('PASS' if cond else 'FAIL'),name,detail)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':1700,'height':1100})
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('dialog',lambda d:asyncio.ensure_future(d.dismiss()))
        await pg.goto('file://'+HTML);await pg.wait_for_timeout(2500);await pg.add_style_tag(content='.rv-guide{display:none!important;pointer-events:none!important}')
        ok('버전',ver_ok(await pg.evaluate("Revival.buildVersion()")))
        await pg.keyboard.press('Escape');await pg.wait_for_timeout(600)
        rm="document.querySelectorAll('.rv-guide').forEach(e=>e.remove())"
        await pg.evaluate(rm);await pg.click('[data-action=addPage]');await pg.wait_for_timeout(700)
        for t in [4,7,5,16,8]:
            await pg.evaluate(rm);await pg.click(f'#templateGrid [data-template="{t}"]');await pg.wait_for_timeout(200)
        await pg.evaluate(rm);await pg.click('#confirmTemplate');await pg.wait_for_timeout(1200)
        await pg.select_option('#themeScope','document');await pg.select_option('#themeSelect','nintendo-light');await pg.wait_for_timeout(700)
        pages=await pg.evaluate("Revival.getProject().pages.map(p=>[p.id,p.templateId])")
        pid={t:i for i,t in pages}
        # 저장 데이터는 그대로(파스텔) — 그리기만 테마 칸
        fills=await pg.evaluate(f"Revival.getProject().pages.find(p=>p.id==='{pid[4]}').objects.filter(o=>o.role==='toc-entry').map(o=>o.style.fill)")
        ok('저장 데이터 변경 없음(04)',fills==['#DDEAF7','#E2F2ED','#F4E8D7'],str(fills))
        await pg.evaluate(f"Revival.go('{pid[4]}')");await pg.wait_for_timeout(400)
        q="[...document.querySelectorAll('#stageHost .rv-stage .rv-object[data-role=\"toc-entry\"]')]"
        n=await pg.evaluate(q+".filter(n=>n.classList.contains('pc-theme-card')).length")
        ok('04 칸 3개 테마 칸',n==3,str(n))
        bg=await pg.evaluate(q+".map(n=>getComputedStyle(n,'::before').backgroundColor)")
        ok('닌텐도 칸 하양',set(bg)=={'rgb(255, 255, 255)'},str(set(bg)))
        bd=await pg.evaluate(q+".map(n=>getComputedStyle(n).borderTopColor+'|'+getComputedStyle(n).borderTopWidth)")
        ok('닌텐도 빨강 테두리 2px',set(bd)=={'rgb(231, 0, 18)|2px'},str(set(bd)))
        # 썸네일(페이지 목록)
        th=await pg.evaluate("document.querySelectorAll('#pageList .pc-theme-card').length")
        ok('페이지 목록 썸네일도 적용',th>=7,str(th))
        # 기본 테마로: 윗선
        await pg.select_option('#themeSelect','pro-sage-ink');await pg.wait_for_timeout(700)
        await pg.evaluate(f"Revival.go('{pid[7]}')");await pg.wait_for_timeout(400)
        modes=await pg.evaluate(q+".map(n=>n.dataset.cardMode+'|'+getComputedStyle(n).borderTopWidth+'|'+getComputedStyle(n).borderLeftWidth+'|'+getComputedStyle(n).borderRadius)")
        ok('기본 테마 윗선 5px·옆 1px·모서리 10',set(modes)=={'top|5px|1px|10px'},str(set(modes)))
        # 상단 띠
        for t in [5,7,16]:
            await pg.evaluate(f"Revival.go('{pid[t]}')");await pg.wait_for_timeout(300)
            has=await pg.evaluate("[...document.querySelectorAll('#stageHost .rv-stage .rv-template-background rect')].some(r=>r.getAttribute('y')==='0'&&r.getAttribute('height')==='7'&&r.getAttribute('width')==='1120')")
            ok(f'양식 {t:02d} 상단 띠',has)
        # 사용자 색 보존: 한 칸 색·모서리 바꾸고 다시 불러오기
        proj=await pg.evaluate("Revival.getProject()")
        for pgx in proj['pages']:
            if pgx['id']==pid[4]:
                e=[o for o in pgx['objects'] if o.get('role')=='toc-entry']
                e[0]['style']['fill']='#123456'
                e[1]['shapeType']='rounded';e[1]['style']['radius']=30
        await pg.evaluate("p=>Revival.importProject(p)",proj);await pg.wait_for_timeout(1200)
        await pg.evaluate(f"Revival.go('{pid[4]}')");await pg.wait_for_timeout(500)
        r=await pg.evaluate(q+".map(n=>[n.classList.contains('pc-theme-card'),getComputedStyle(n,'::before').backgroundColor,getComputedStyle(n).borderRadius])")
        ok('사용자가 바꾼 칸 색 그대로',r[0][0]==False and r[0][1]=='rgb(18, 52, 86)',str(r[0]))
        ok('사용자가 바꾼 모서리 그대로',r[1][0]==True and r[1][2]=='30px',str(r[1]))
        ok('나머지 칸은 테마 칸',r[2][0]==True,str(r[2]))
        # 발표 모드
        await pg.evaluate("Revival.startPresentation()");await pg.wait_for_timeout(900)
        pres=await pg.evaluate("document.querySelectorAll('#presentation .pc-theme-card, .rv-present .pc-theme-card').length")
        await pg.keyboard.press('Escape');await pg.wait_for_timeout(500)
        ok('발표 화면 적용',pres>=1,str(pres))
        # PPT 내보내기
        await pg.select_option('#themeSelect','nintendo-light');await pg.wait_for_timeout(700)
        b64=await pg.evaluate("RvPptx.build().then(async r=>{const tot=typeof r.total==='object'?(r.total.slides??r.total.total??JSON.stringify(r.total)):r.total;const a=new Uint8Array(await r.blob.arrayBuffer());let s='';for(let i=0;i<a.length;i+=32768)s+=String.fromCharCode.apply(null,a.subarray(i,i+32768));return btoa(s)+'|'+tot})")
        data,total=b64.split('|')
        z=zipfile.ZipFile(io.BytesIO(base64.b64decode(data)))
        slides=[n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
        open('out_v41.pptx','wb').write(base64.b64decode(data))
        ok('PPT 내보내기',len(slides)>=10,f'{len(slides)}장 / total={total}')
        ok('스크립트 오류 없음',not errs,str(errs[:3]))
        await b.close()
asyncio.run(main())
fail=[r for r in R if not r[1]]
print(f'== {len(R)-len(fail)}/{len(R)} 통과')
