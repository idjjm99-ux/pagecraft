# v12.44: 두 갈래 합침(▶ 없앰 + 레일 테마색) / 05 구분선 테마색 / 크래프톤 원 유지
import asyncio,sys,json
sys.path.insert(0,'/home/claude/tests')
from h import H
R=[]
def ok(n,c,i=None):R.append(c);print(('OK  ' if c else 'FAIL'),n,'' if i is None else str(i)[:220])
LUM="""const L=c=>{const m=c.match(/\\d+(\\.\\d+)?/g).slice(0,3).map(Number).map(x=>x/255).map(x=>x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4));return m[0]*.2126+m[1]*.7152+m[2]*.0722};const CR=(a,b)=>{const x=L(a),y=L(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};"""
GRAY={'rgb(151, 168, 184)','rgb(194, 202, 212)'}
async def main(path):
    h=H();pg=await h.start(path,1700,1100);ev=h.ev
    ok('버전',(await ev("()=>Revival.buildVersion()")).startswith('PageCraft v12.4'))
    ok('예시 문서에 장식 ▶ 개체 없음(18:00 판 유지)',await ev("()=>Revival.getProject().pages.flatMap(p=>p.objects).filter(o=>o.role==='template-decor'&&o.decorOriginal==='▶').length")==0)
    await pg.click('[data-action=addPage]');await pg.wait_for_timeout(700)
    for t in [5,6,22,25]:
        await pg.click(f'#templateGrid [data-template="{t}"]');await pg.wait_for_timeout(200)
    await pg.click('#confirmTemplate');await pg.wait_for_timeout(1500)
    await pg.select_option('#themeScope','document')
    pages=await ev("()=>Revival.getProject().pages.map(p=>[p.id,p.templateId])")
    pid={t:i for i,t in pages}
    n=await ev("()=>Revival.getProject().pages.filter(p=>[22,25].includes(p.templateId)).flatMap(p=>p.objects).filter(o=>o.role==='template-decor'&&o.decorOriginal==='▶').length")
    ok('새 22·25 페이지에 장식 ▶ 없음',n==0 and 22 in pid and 25 in pid,n)
    await ev(f"()=>Revival.go('{pid[5]}')");await pg.wait_for_timeout(400)
    q=LUM+"""const st=document.querySelector('#stageHost .rv-stage');
      const seps=[...st.querySelectorAll(".rv-object[data-role='toc-separator'] line")].map(l=>getComputedStyle(l).stroke);
      const pg=Revival.getCurrentPage(),cs=getComputedStyle(st),c={paper:cs.getPropertyValue('--paper').trim(),rule:cs.getPropertyValue('--rule').trim()};
      let bg=pg.pageBgColor||c.paper;const toRgb=h=>/^#[0-9a-f]{6}$/i.test(h)?'rgb('+[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)).join(', ')+')':null;
      const bgr=toRgb(bg)||cs.backgroundColor;
      return {seps,bg,bgr,rule:c.rule,cr:seps.map(s=>CR(s,bgr))};"""
    has=await ev("()=>getComputedStyle(document.querySelector('#stageHost .rv-stage')).getPropertyValue('--paper').trim()")
    ok('테마 바탕색 읽힘(v07 계열은 transparent → 스테이지 배경으로 대체)',bool(has),has)
    themes=await ev("()=>[...document.querySelectorAll('#themeSelect option')].map(o=>o.value)")
    colors={};bad=[];gray=[]
    for th in themes:
        await pg.select_option('#themeSelect',th);await pg.wait_for_timeout(300)
        r=await ev("()=>{"+q+"}");colors[th]=r
        if not r['seps']:bad.append((th,'없음'));continue
        if len(set(r['seps']))!=1:bad.append((th,'색 다름'))
        if min(r['cr'])<1.48:bad.append((th,round(min(r['cr']),2)))
        if r['seps'][0] in GRAY:gray.append(th)
    ok(f'{len(themes)}개 테마: 05 구분선 있음·같은 색·바탕 대비≥1.5',not bad and len(themes)>=10,bad[:4])
    ok('고정 회색 남은 테마 거의 없음',len(gray)<=2,gray)
    dark=colors.get('pro-night-teal')
    ok('어두운 테마(미드나잇 틸) 구분선 = 회색 아님·대비≥1.5',dark and dark['seps'][0] not in GRAY and min(dark['cr'])>=1.48,dark and (dark['seps'][0],dark['bg']))
    d=await ev(f"()=>Revival.getProject().pages.find(p=>p.id==='{pid[5]}').objects.filter(o=>o.role==='toc-separator').map(o=>o.style.stroke.toUpperCase())")
    ok('저장 데이터 그대로(기본 회색)',d and set(d)<={'#97A8B8','#C2CAD4'},d)
    P=await ev("()=>Revival.getProject()")
    for p in P['pages']:
        if p['id']==pid[5]:[o for o in p['objects'] if o.get('role')=='toc-separator'][0]['style']['stroke']='#00AA00'
    await ev("p=>Revival.importProject(p)",P);await pg.wait_for_timeout(1000)
    await ev(f"()=>Revival.go('{pid[5]}')");await pg.wait_for_timeout(400)
    await pg.select_option('#themeSelect','nintendo-light');await pg.wait_for_timeout(400)
    r=await ev("()=>{"+q+"}")
    ok('사용자 색 선은 그대로, 나머지는 테마색',r['seps'][0]=='rgb(0, 170, 0)' and r['seps'][1] not in GRAY|{'rgb(0, 170, 0)'},r['seps'][:2])
    theme_sep=r['seps'][1]
    sid=await ev("()=>Revival.getCurrentPage().objects.filter(o=>o.role==='toc-separator')[1].id")
    await ev(f"()=>Revival.selectOne('{sid}')");await pg.wait_for_timeout(200)
    await pg.mouse.move(5,5);await pg.keyboard.press('Control+c');await pg.keyboard.press('Control+v');await pg.wait_for_timeout(400)
    nw=await ev("()=>{const s=Revival.getSelected();const n=document.querySelector(`#stageHost [data-object-id='${s[0]}'] line`);return n?getComputedStyle(n).stroke:null}")
    ok('붙인 구분선도 테마색',nw==theme_sep,[nw,theme_sep])
    await pg.keyboard.press('Control+d');await pg.wait_for_timeout(400)
    nw=await ev("()=>{const s=Revival.getSelected();const n=document.querySelector(`#stageHost [data-object-id='${s[0]}'] line`);return n?getComputedStyle(n).stroke:null}")
    ok('Ctrl+D 구분선도 테마색',nw==theme_sep,nw)
    # 크래프톤: 원은 원형, 사각형은 2px
    P=await ev("()=>Revival.getProject()")
    for p in P['pages']:
        if p['id']==pid[6]:
            dot=[o for o in p['objects'] if o.get('role')=='template-decor'][0]
            for k,(st,x) in enumerate((('circle',300),('rect',500),('rounded',700))):
                c=json.loads(json.dumps(dot));c.update(id=f'obj-t44-{k}',role=None,decorOriginal=None,decorIndex=None,shapeType=st,x=x,y=650,w=120,h=120);c['style']['fill']='#F6141E';p['objects'].append(c)
    await ev("p=>Revival.importProject(p)",P);await pg.wait_for_timeout(1000)
    await ev(f"()=>Revival.go('{pid[6]}')");await pg.wait_for_timeout(400)
    await pg.select_option('#themeSelect','krafton-light');await pg.wait_for_timeout(500)
    rr=await ev("()=>{const g=id=>getComputedStyle(document.querySelector(`#stageHost [data-object-id='${id}']`)).borderRadius;const dots=[...document.querySelectorAll(\"#stageHost .rv-object[data-role='template-decor']\")].map(n=>getComputedStyle(n).borderRadius);return {c:g('obj-t44-0'),r:g('obj-t44-1'),rd:g('obj-t44-2'),dots}}")
    ok('크래프톤: 원 도형 원형(50%)',rr['c']=='50%',rr)
    ok('크래프톤: 06 레일 점 원형',rr['dots'] and all(x=='50%' for x in rr['dots']),rr['dots'][:2])
    ok('크래프톤: 사각형·둥근사각형은 테마 2px 그대로',rr['r']=='2px' and rr['rd']=='2px',rr)
    await h.shot('t_v44_krafton')
    await pg.select_option('#themeSelect','pro-ivory-brick');await pg.wait_for_timeout(400)
    rr=await ev("()=>getComputedStyle(document.querySelector(`#stageHost [data-object-id='obj-t44-0']`)).borderRadius")
    ok('다른 테마 원도 원형',rr=='50%',rr)
    # 발표
    await ev(f"()=>Revival.go('{pid[5]}')");await pg.wait_for_timeout(300)
    await pg.select_option('#themeSelect','pro-night-teal');await pg.wait_for_timeout(400)
    await ev("()=>Revival.startPresentation()");await pg.wait_for_timeout(900)
    pr=await ev("()=>[...document.querySelectorAll(\"#presentation .rv-object[data-role='toc-separator'] line\")].map(l=>getComputedStyle(l).stroke)")
    ok('발표 화면 구분선도 테마색',pr and any(x not in GRAY|{'rgb(0, 170, 0)'} for x in pr),pr[:2])
    await pg.keyboard.press('Escape');await pg.wait_for_timeout(500)
    b=await ev("RvPptx.build().then(r=>r.blob.size)")
    ok('PPT 내보내기 됨',b>10000,b)
    ok('오류 없음',not h.errs,h.errs[:3])
    json.dump(colors,open('/home/claude/tests/sep_colors_v44.json','w'),ensure_ascii=False,indent=1)
    await h.close()
    print(f'== {sum(R)}/{len(R)} 통과')
asyncio.run(main(sys.argv[1]))
