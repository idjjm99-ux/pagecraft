# 그래프 글씨 겹침 점검: 9종 x 5크기 x 항목수 x 이름셋
import sys; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__))); from pcenv import CHROME, HERE; import os
import asyncio,sys,json
from h import H
TYPES=['bar','hbar','stack','hstack','combo','line','pie','donut','gantt']
SIZES=[(320,420),(360,520),(520,340),(760,380),(1000,420)]
NS=[int(x) for x in (sys.argv[2] if len(sys.argv)>2 else '5,8,12').split(',')]
MON=[f'{i}월' for i in range(1,21)]
CITY=['서울','부산','대구','인천','광주','대전','울산','세종','경기','강원','충북','충남','전북','전남','경북','경남','제주','수원','창원','청주']
async def main(p):
    h=H(); pg=await h.start(p,1500,950)
    pages=[]
    for t in TYPES:
        for (w,hh) in SIZES:
            objs=[]
            for k,n in enumerate(NS):
                for nm,L in (('m',MON),('c',CITY)):
                    vals=[(i*37%11+3)*100 for i in range(n)]
                    ser=[{'id':'s1','name':'접수','color':'#337CB3','values':vals}]
                    if t in('stack','hstack','combo','gantt'):ser.append({'id':'s2','name':'처리','color':'#D86B20','values':[(i*13%7+2)*50 for i in range(n)]})
                    objs.append({'id':f'c-{t}-{w}-{n}-{nm}','kind':'chart','role':'user','x':20,'y':20,'w':w,'h':hh,'z':10,'locked':False,'text':'','style':{'fill':'#FFFFFF','stroke':'transparent','fontFamily':'Pretendard','fontSize':24},'chart':{'type':t,'labels':L[:n],'series':ser,'showValues':True,'showLegend':True,'highlight':-1}})
            pages.append(objs)
    res=await h.ev("""(pages)=>{const P=Revival.getProject();const base=P.pages[0];P.pages=pages.map((objs,i)=>({...JSON.parse(JSON.stringify(base)),id:'aud'+i,objects:objs}));Revival.importProject(P);return Revival.getProject().pages.length}""",pages)
    out=[]
    for i in range(len(pages)):
        await h.ev(f"()=>Revival.go('aud{i}')"); await pg.wait_for_timeout(120)
        r=await h.ev("""()=>[...document.querySelectorAll('#stageHost .rv-object')].filter(e=>e.querySelector('svg')).map(e=>{const svg=e.querySelector('svg');const ts=[...svg.querySelectorAll('text')].filter(t=>t.getAttribute('opacity')!=='0');
          const Q=ts.map(t=>{const b=t.getBBox();if(!b.width)return null;const m=t.getScreenCTM();const P=(x,y)=>({x:m.a*x+m.c*y+m.e,y:m.b*x+m.d*y+m.f});return [P(b.x+.5,b.y+.5),P(b.x+b.width-.5,b.y+.5),P(b.x+b.width-.5,b.y+b.height-.5),P(b.x+.5,b.y+b.height-.5)];}).filter(Boolean);
          const sep=(A,B)=>{for(const S of [A,B])for(let i=0;i<4;i++){const p=S[i],q=S[(i+1)%4],nx=q.y-p.y,ny=p.x-q.x;const pa=A.map(v=>v.x*nx+v.y*ny),pb=B.map(v=>v.x*nx+v.y*ny);if(Math.max(...pa)<=Math.min(...pb)||Math.max(...pb)<=Math.min(...pa))return true;}return false;};
          let ov=0;for(let i=0;i<Q.length;i++)for(let j=i+1;j<Q.length;j++)if(!sep(Q[i],Q[j]))ov++;
          const bb=ts.map(t=>t.getBoundingClientRect()).filter(r=>r.width>0);
          const box=svg.getBoundingClientRect();const outb=bb.filter(r=>r.left<box.left-1||r.right>box.right+1||r.bottom>box.bottom+1||r.top<box.top-1).length;
          const cats=[...svg.querySelectorAll('[data-chart-label=category]')];
          return {id:e.dataset.objectId,ov,out:outb,cats:cats.length,shown:cats.filter(t=>t.textContent.trim()).length,rot:cats.some(t=>/rotate/.test(t.getAttribute('transform')||'')),slices:svg.querySelectorAll('path,circle').length,pie:svg.querySelectorAll('[data-chart-label=pie]').length}})""")
        out+=r
    await h.close()
    bad=[o for o in out if o['ov'] or o['out']]
    print('CHARTS',len(out),'BAD',len(bad))
    for o in bad: print(' ',o)
    json.dump(out,open('/tmp/chart_audit.json','w'),ensure_ascii=False)
asyncio.run(main(sys.argv[1]))
