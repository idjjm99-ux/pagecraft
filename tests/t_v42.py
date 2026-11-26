# v12.42: 05·06 목차 칸·16 타임라인 단계 → 테마 바탕 면
import sys; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__))); from pcenv import ver_ok, CHROME, HERE; import os
import asyncio,sys
from h import H
R=[]
def ok(n,c,i=None):R.append(c);print(('OK  ' if c else 'FAIL'),n,'' if i is None else str(i)[:200])
async def main(path):
    h=H();pg=await h.start(path,1700,1100);ev=h.ev
    ok('버전',ver_ok(await ev("()=>Revival.buildVersion()")))
    await pg.click('[data-action=addPage]');await pg.wait_for_timeout(700)
    for t in [5,6,16,4]:
        await pg.click(f'#templateGrid [data-template="{t}"]');await pg.wait_for_timeout(200)
    await pg.click('#confirmTemplate');await pg.wait_for_timeout(1200)
    await pg.select_option('#themeScope','document')
    pid={t:i for i,t in await ev("()=>Revival.getProject().pages.map(p=>[p.id,p.templateId])")}
    q="(r)=>[...document.querySelectorAll(`#stageHost .rv-stage .rv-object[data-role='${r}']`)].map(n=>[n.dataset.cardMode||'',getComputedStyle(n,'::before').backgroundColor,getComputedStyle(n).borderRadius,n.querySelector('.rv-text-content')?getComputedStyle(n.querySelector('.rv-text-content')).color:''])"
    exp={'pro-night-teal':'rgb(27, 49, 66)','nintendo-light':'rgb(253, 232, 234)','kakao-bank-light':'rgb(255, 249, 214)','krafton-light':'rgb(242, 242, 242)'}
    for th,col in exp.items():
        await pg.select_option('#themeSelect',th);await pg.wait_for_timeout(600)
        for t,role in ((5,'toc-entry'),(6,'toc-entry'),(16,'timeline-step')):
            await ev(f"()=>Revival.go('{pid[t]}')");await pg.wait_for_timeout(350)
            r=await ev(q,role)
            ok(f'{th} 양식 {t:02d} 칸 = 테마 면',r and all(x[0]=='fill' and x[1]==col for x in r),r[:1])
            if th=='pro-night-teal':ok(f'{th} 양식 {t:02d} 글자 흰색',all(x[3]=='rgb(255, 255, 255)' for x in r),r[:1])
    await pg.select_option('#themeSelect','pro-sage-ink');await pg.wait_for_timeout(600)
    await ev(f"()=>Revival.go('{pid[16]}')");await pg.wait_for_timeout(300)
    r=await ev(q,'timeline-step');ok('16 단계 둥근 모양 유지(12px)',all(x[2]=='12px' for x in r),r[:1])
    d=await ev(f"()=>Revival.getProject().pages.find(p=>p.id==='{pid[16]}').objects.filter(o=>o.role==='timeline-step').map(o=>o.style.fill)")
    ok('저장 데이터 그대로',set(d)=={'#E8F1F7'},d)
    P=await ev("()=>Revival.getProject()")
    for p in P['pages']:
        if p['id']==pid[5]:
            [o for o in p['objects'] if o.get('role')=='toc-entry'][0]['style']['fill']='#FFCC00'
    await ev("p=>Revival.importProject(p)",P);await pg.wait_for_timeout(1000)
    await ev(f"()=>Revival.go('{pid[5]}')");await pg.wait_for_timeout(350)
    r=await ev(q,'toc-entry');ok('사용자 색 칸은 그대로',r[0][0]=='' and r[0][1]=='rgb(255, 204, 0)' and r[1][0]=='fill',r[:2])
    await ev(f"()=>Revival.go('{pid[4]}')");await pg.wait_for_timeout(350)
    r=await ev(q,'toc-entry');ok('04 테마 칸(v12.41) 그대로',r and all(x[0]=='top' for x in r),r[:1])

    # ── 복사·붙여넣기 (Ctrl+C / Ctrl+V)
    await pg.select_option('#themeSelect','pro-sage-ink');await pg.wait_for_timeout(500)
    await ev(f"()=>Revival.go('{pid[4]}')");await pg.wait_for_timeout(400)
    rect=await ev("()=>{const r=document.querySelector('#stageHost .rv-stage').getBoundingClientRect();return [r.left,r.top,r.width,r.height]}")
    z=rect[2]/1120
    cid=await ev("()=>Revival.getCurrentPage().objects.filter(o=>o.role==='toc-entry')[2].id")
    n=await ev(f"()=>{{const r=document.querySelector(`#stageHost [data-object-id='{cid}']`).getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}}")
    await pg.mouse.click(n[0],n[1]);await pg.wait_for_timeout(300)
    src=await ev(f"()=>Revival.getCurrentPage().objects.find(o=>o.id==='{cid}')")
    cnt=lambda:ev("()=>Revival.getCurrentPage().objects.length")
    c0=await cnt()
    await pg.keyboard.press('Control+c')
    P=(300,250);await pg.mouse.move(rect[0]+P[0]*z,rect[1]+P[1]*z);await pg.mouse.move(rect[0]+P[0]*z+1,rect[1]+P[1]*z)
    await pg.keyboard.press('Control+v');await pg.wait_for_timeout(400)
    sel=lambda:ev("()=>{const s=Revival.getSelected();return Revival.getCurrentPage().objects.filter(o=>s.includes(o.id)).map(o=>({x:o.x,y:o.y,w:o.w,h:o.h,id:o.id}))}")
    a=(await sel())[0]
    ok('Ctrl+V 개체 붙여넣기 됨',await cnt()==c0+1,[c0,await cnt()])
    ok('마우스 위치(가운데 기준)에 붙음',abs(a['x']+a['w']/2-P[0])<=3 and abs(a['y']+a['h']/2-P[1])<=3,a)
    await pg.keyboard.press('Control+v');await pg.wait_for_timeout(300);b=(await sel())[0]
    ok('같은 자리 또 붙이면 20씩 비켜 놓음',b['x']-a['x']==20 and b['y']-a['y']==20,[a,b])
    await pg.mouse.move(rect[0]+1110*z,rect[1]+780*z);await pg.mouse.move(rect[0]+1112*z,rect[1]+782*z)
    await pg.keyboard.press('Control+v');await pg.wait_for_timeout(300);c=(await sel())[0]
    ok('구석에 붙이면 크기 그대로 안쪽으로 밀어 넣음',c['x']+c['w']<=1120 and c['y']+c['h']<=790 and c['w']==src['w'] and c['h']==src['h'],c)
    cls=await ev(f"()=>document.querySelector(`#stageHost [data-object-id='{c['id']}']`).classList.contains('pc-theme-card')")
    ok('붙인 칸도 테마 칸(파스텔 안 나옴)',cls)
    await ev("()=>{const b=[...document.querySelectorAll('#inspector [data-action=pasteSelection]')][0];b&&b.scrollIntoView()}")
    btn=await ev("()=>{const b=document.querySelector('#inspector [data-action=pasteSelection]');if(!b)return null;const r=b.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}")
    if btn:
        await pg.mouse.move(btn[0],btn[1]);await pg.mouse.click(btn[0],btn[1]);await pg.wait_for_timeout(300);d=(await sel())[0]
        ok('[붙여넣기] 버튼은 원래 자리 옆(+28)',d['x']==src['x']+28 and d['y']==src['y']+28,[d,src['x'],src['y']])
    else: ok('[붙여넣기] 버튼 찾기',False)
    # 표 선택 중 Ctrl+V는 엑셀 붙여넣기 쪽으로(개체 안 붙음)
    tid=await ev("""()=>{const P=Revival.getProject();const src=P.pages.flatMap(p=>p.objects).find(o=>o.kind==='table');const cur=P.pages.find(p=>p.id===P.currentPageId);const t=JSON.parse(JSON.stringify(src));t.id='tbl-test';t.x=60;t.y=60;t.z=900;t.locked=false;cur.objects.push(t);Revival.importProject(P);Revival.go(cur.id);return t.id}""")
    await pg.wait_for_timeout(500);await ev("()=>Revival.selectOne('tbl-test')");await pg.wait_for_timeout(300)
    tb=await ev("()=>{const s=Revival.getSelected();const o=Revival.getCurrentPage().objects.find(o=>s.includes(o.id));return o?o.kind:null}")
    if tb=='table':
        ok('표 선택 중 Ctrl+V 키 처리 오류 없음',not h.errs,h.errs[:2])
        await ev("()=>{const dt=new DataTransfer();dt.setData('text/plain','가\\t나\\n1\\t2');document.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true}))}");await pg.wait_for_timeout(400)
        cells=await ev("()=>{const s=Revival.getSelected();const o=Revival.getCurrentPage().objects.find(o=>s.includes(o.id));return JSON.stringify(o?.table||{}).includes('나')}")
        ok('표 엑셀 붙여넣기 그대로 됨',cells)
    else: ok('표 넣기(시험 준비)',False,tb)
    ok('오류 없음',not h.errs,h.errs[:3])
    await h.close();print('TOTAL',sum(R),'/',len(R))
asyncio.run(main(sys.argv[1]))
