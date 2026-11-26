# v12.43: 06 세로 레일 목차 — 레일 선·점 테마색
import sys; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__))); from pcenv import ver_ok, CHROME, HERE; import os
import asyncio,sys,json
from h import H
R=[]
def ok(n,c,i=None):R.append(c);print(('OK  ' if c else 'FAIL'),n,'' if i is None else str(i)[:220])
LUM="""const L=c=>{const m=c.match(/\\d+(\\.\\d+)?/g).slice(0,3).map(Number).map(x=>x/255).map(x=>x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4));return m[0]*.2126+m[1]*.7152+m[2]*.0722};const CR=(a,b)=>{const x=L(a),y=L(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};"""
async def main(path):
    h=H();pg=await h.start(path,1700,1100);ev=h.ev
    ok('버전',ver_ok(await ev("()=>Revival.buildVersion()")))
    await pg.click('[data-action=addPage]');await pg.wait_for_timeout(700)
    await pg.click('#templateGrid [data-template="6"]');await pg.wait_for_timeout(200)
    await pg.click('#confirmTemplate');await pg.wait_for_timeout(1200)
    await pg.select_option('#themeScope','document')
    pid=[i for i,t in await ev("()=>Revival.getProject().pages.map(p=>[p.id,p.templateId])") if t==6][-1]
    await ev(f"()=>Revival.go('{pid}')");await pg.wait_for_timeout(400)
    q=LUM+"""const st=document.querySelector('#stageHost .rv-stage');
      const rails=[...st.querySelectorAll(".rv-object[data-role='toc-rail'] line")].map(l=>getComputedStyle(l).stroke);
      const dots=[...st.querySelectorAll(".rv-object[data-role='template-decor']")].map(n=>getComputedStyle(n,'::before').backgroundColor);
      const pb=Revival.getProject().pages.find(p=>p.id===Revival.getCurrentPage().id);
      // 바탕: 레일 뒤 실제 페이지 색(레일·점 숨기고 그 자리 픽셀 대신 스테이지 배경 계산값)
      const bg=getComputedStyle(st).backgroundColor;
      return {rails,dots,bg,cr:[...rails,...dots].map(c=>CR(c,bg))};"""
    themes=await ev("()=>[...document.querySelectorAll('#themeSelect option')].map(o=>o.value)")
    ok('테마 목록',len(themes)>=10,len(themes))
    colors={};weak=[];blue=[]
    for th in themes:
        await pg.select_option('#themeSelect',th);await pg.wait_for_timeout(350)
        r=await ev("()=>{"+q+"}")
        colors[th]=r
        if not r['rails'] or not r['dots']:weak.append((th,'없음'));continue
        if len(set(r['rails']+r['dots']))!=1:weak.append((th,'선·점 색 다름',r['rails'][:1],r['dots'][:1]))
        if min(r['cr'])<2.95:weak.append((th,round(min(r['cr']),2),r['dots'][0],r['bg']))
        if r['dots'][0]=='rgb(53, 106, 153)':blue.append(th)
    ok('모든 테마: 레일 선·점 있음·같은 색·바탕 대비≥3',not weak,weak[:4])
    ok('파랑 고정색 아닌 테마 다수',len(blue)<=2,blue)
    exp={'nintendo-light':'rgb(231, 0, 18)'}
    await pg.select_option('#themeSelect','nintendo-light');await pg.wait_for_timeout(400)
    r=await ev("()=>{"+q+"}");ok('닌텐도 = 빨강',r['dots'][0]==exp['nintendo-light'] and r['rails'][0]==exp['nintendo-light'],r['dots'][:1])
    await pg.select_option('#themeSelect','kakao-bank-light');await pg.wait_for_timeout(400)
    r=await ev("()=>{"+q+"}");ok('카카오 = 노랑 그대로 아님(대비 보정)',r['dots'][0]!='rgb(254, 229, 0)' and min(r['cr'])>=2.95,[r['dots'][0],round(min(r['cr']),2)])
    d=await ev(f"()=>Revival.getProject().pages.find(p=>p.id==='{pid}').objects.filter(o=>['toc-rail','template-decor'].includes(o.role)).map(o=>o.kind==='line'?o.style.stroke:o.style.fill)")
    ok('저장 데이터 그대로(#356A99)',set(x.upper() for x in d)=={'#356A99'},d)
    # 사용자 색 보존
    P=await ev("()=>Revival.getProject()")
    for p in P['pages']:
        if p['id']==pid:
            dots=[o for o in p['objects'] if o.get('role')=='template-decor'];dots[0]['style']['fill']='#00AA00'
            [o for o in p['objects'] if o.get('role')=='toc-rail'][0]['style']['stroke']='#AA00AA'
    await ev("p=>Revival.importProject(p)",P);await pg.wait_for_timeout(1000)
    await ev(f"()=>Revival.go('{pid}')");await pg.wait_for_timeout(400)
    r=await ev("()=>{"+q+"}")
    ok('사용자 색은 그대로(점 초록·선 보라)',r['dots'][0]=='rgb(0, 170, 0)' and r['rails'][0]=='rgb(170, 0, 170)' and r['dots'][1]!='rgb(0, 170, 0)',[r['dots'][:2],r['rails']])
    # 점 4개 이상 늘리기(새 점도 테마색)
    await pg.select_option('#themeSelect','nintendo-light');await pg.wait_for_timeout(400)
    # 복사·붙여넣기한 점
    did=await ev("()=>Revival.getCurrentPage().objects.filter(o=>o.role==='template-decor')[2].id")
    await ev(f"()=>Revival.selectOne('{did}')");await pg.wait_for_timeout(200)
    c0=await ev("()=>Revival.getCurrentPage().objects.length")
    await pg.mouse.move(5,5);await pg.keyboard.press('Control+c');await pg.keyboard.press('Control+v');await pg.wait_for_timeout(400)
    new=await ev("()=>{const s=Revival.getSelected();const n=document.querySelector(`#stageHost [data-object-id='${s[0]}']`);return [Revival.getCurrentPage().objects.length,n?getComputedStyle(n,'::before').backgroundColor:null]}")
    ok('붙인 점도 테마색(빨강)',new[0]==c0+1 and new[1]=='rgb(231, 0, 18)',[c0,new])
    await pg.keyboard.press('Control+d');await pg.wait_for_timeout(400)
    new=await ev("()=>{const s=Revival.getSelected();const n=document.querySelector(`#stageHost [data-object-id='${s[0]}']`);return n?getComputedStyle(n,'::before').backgroundColor:null}")
    ok('Ctrl+D 복제한 점도 테마색',new=='rgb(231, 0, 18)',new)
    # 발표 화면
    await ev("()=>Revival.startPresentation()");await pg.wait_for_timeout(900)
    pr=await ev("()=>{const l=document.querySelector(\"#presentation .rv-object[data-role='toc-rail'] line\");return l?getComputedStyle(l).stroke:null}")
    ok('발표 화면 레일도 테마색',pr in ('rgb(231, 0, 18)','rgb(170, 0, 170)') ,pr)
    await pg.keyboard.press('Escape');await pg.wait_for_timeout(500)
    # PPT
    b=await ev("RvPptx.build().then(r=>r.blob.size)")
    ok('PPT 내보내기 됨',b>10000,b)
    await h.shot('t_v43_nintendo')
    ok('오류 없음',not h.errs,h.errs[:3])
    json.dump(colors,open(os.path.join(HERE,'rail_colors_v43.json'),'w'),ensure_ascii=False,indent=1)
    await h.close()
    print(f'== {sum(R)}/{len(R)} 통과')
asyncio.run(main(sys.argv[1]))
