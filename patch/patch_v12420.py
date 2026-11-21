"""PageCraft v12.42.0 — 05·06 목차 칸·16 타임라인 단계 고정 밝은 색 → 테마 바탕 면 / Ctrl+V 개체 붙여넣기 고침·마우스 위치에 붙이기(넘치면 안쪽으로).
Usage: python3 -I patch_v12420.py <PageCraft_v12.41.0_Lite.html> <out.html>"""
import sys
src,out=sys.argv[1],sys.argv[2]
html=open(src,encoding='utf-8').read()
def R(old,new,n=1):
    global html
    c=html.count(old);assert c==n,f'expected {n} got {c}: {old[:80]!r}'
    html=html.replace(old,new)
assert 'function pcThemeCard' in html,'needs v12.41'
assert 'pcSurfaceFill' not in html,'already patched'

# 1) 테마 바탕 면: soft·tint 중 페이지와 구분되고(대비 1.04 이상) 채도가 낮은 쪽. 둘 다 안 되면 페이지↔글자색 6% 섞기
R("function pcThemeCard(o,page,palettes){\n if(!o||o.kind!=='shape'||o.role!=='toc-entry'||!page||![4,7].includes(Number(page.templateId)))return null;",
  "function pcSurfaceFill(c){\n"
  " const chroma=h=>{const v=[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));return Math.max(...v)-Math.min(...v);};\n"
  " const ok=[c.soft,c.tint].filter(x=>M.isHex(x)&&M.isHex(c.paper)&&ratio(x,c.paper)>=1.04).sort((a,b)=>chroma(a)-chroma(b));\n"
  " if(ok.length)return ok[0];\n"
  " if(!M.isHex(c.paper)||!M.isHex(c.ink))return c.soft||c.paper;\n"
  " return '#'+[1,3,5].map(i=>Math.round(parseInt(c.paper.slice(i,i+2),16)*.94+parseInt(c.ink.slice(i,i+2),16)*.06).toString(16).padStart(2,'0')).join('').toUpperCase();\n"
  "}\n"
  "function pcThemeCard(o,page,palettes){\n"
  " if(!o||!page||o.kind!=='shape')return null;\n"
  " // v12.42: 복사·복제한 칸은 원래 역할·양식(pcCardRole·pcCardTpl)으로 판단 → 붙여넣어도 파스텔로 안 돌아감\n"
  " const role=o.pcCardRole||o.role,tpl=Number(o.pcCardTpl??page.templateId);\n"
  " // v12.42: 05·06 목차 칸 #F2F6FB, 16 타임라인 단계 #E8F1F7(기본색 그대로일 때만) → 테마 바탕 면. 모양·테두리는 그대로\n"
  " if(!o.style?.gradient&&typeof o.style?.fill==='string'){const F=o.style.fill.toUpperCase();\n"
  "  if((role==='toc-entry'&&[5,6].includes(tpl)&&F==='#F2F6FB')||(role==='timeline-step'&&tpl===16&&F==='#E8F1F7'))return {fill:pcSurfaceFill(bgObj(page,palettes)),mode:'fill',border:false,radius:null};}\n"
  " if(role!=='toc-entry'||![4,7].includes(tpl))return null;")

# 2) Ctrl+V 고침: 키 처리 쪽에서 다른 스크립트의 pcGridPasteTarget를 못 찾아 오류(v12.37~) → 개체 붙여넣기가 안 됐음
R("if(k==='v'){if(pcGridPasteTarget())return;","if(k==='v'){if(window.pcGridPasteTarget?.())return;")
R("function pcGridPasteTarget(){","window.pcGridPasteTarget=pcGridPasteTarget;function pcGridPasteTarget(){")

# 3) 붙여넣기 위치: 마우스가 페이지 위에 있으면 그 자리(묶음 가운데). 같은 자리에 또 붙이면 20씩 비켜 놓음.
#    페이지 밖으로 넘치면 크기는 그대로 두고 안쪽으로 밀어 넣음(발표·인쇄·PPT에서 잘리는 부분이 없게)
R(" st.objectClipboard=items.map(item=>M.clone(item));status(items.length+'개 객체 복사됨 · Ctrl+V로 붙여넣기');return true;",
  " st.objectClipboard=items.map(item=>{const c=M.clone(item);if(['toc-entry','timeline-step'].includes(item.role)){c.pcCardRole=item.pcCardRole||item.role;c.pcCardTpl=item.pcCardTpl??current().templateId;}return c;});st.pcPasteLast=null;status(items.length+'개 개체 복사됨 · 붙일 곳에 마우스를 두고 Ctrl+V');return true;")
R("""  const top=Math.max(50,...current().objects.map(item=>item.z));
  for(const [i,raw] of st.objectClipboard.entries()){
   const copy=M.clone(raw);copy.id=map.get(raw.id);
   copy.x=M.clamp(raw.x+28,0,M.W-raw.w);copy.y=M.clamp(raw.y+28,0,M.H-raw.h);""",
  """  const top=Math.max(50,...current().objects.map(item=>item.z));
  const C=st.objectClipboard,bx=Math.min(...C.map(o=>o.x)),by=Math.min(...C.map(o=>o.y)),bw=Math.max(...C.map(o=>o.x+o.w))-bx,bh=Math.max(...C.map(o=>o.y+o.h))-by;
  const mp=st.pcMouse&&st.pcMouse.page===current().id?st.pcMouse:null;
  let nx=mp?mp.x-bw/2:bx+28,ny=mp?mp.y-bh/2:by+28;
  const L=st.pcPasteLast;if(L&&L.page===current().id&&Math.abs(L.ax-nx)<1&&Math.abs(L.ay-ny)<1){L.n++;}else st.pcPasteLast={page:current().id,ax:nx,ay:ny,n:0};
  nx+=st.pcPasteLast.n*20;ny+=st.pcPasteLast.n*20;
  nx=M.clamp(nx,0,Math.max(0,M.W-bw));ny=M.clamp(ny,0,Math.max(0,M.H-bh));
  const dx=Math.round(nx-bx),dy=Math.round(ny-by);st.pcPasteWhere=mp?'마우스 위치':'원래 자리 옆';
  for(const [i,raw] of st.objectClipboard.entries()){
   const copy=M.clone(raw);copy.id=map.get(raw.id);
   copy.x=raw.x+dx;copy.y=raw.y+dy;""")
R(" });status(newIds.length+'개 객체 붙여넣기 완료');return true;\n}",
  " });status(newIds.length+'개 개체 붙여넣기 · '+(st.pcPasteWhere||''));return true;\n}\n"
  "// v12.42: 페이지 위 마우스 위치 기억(붙여넣기 자리). 페이지 밖으로 나가면 지움 → 버튼으로 붙이면 원래 자리 옆\n"
  "document.addEventListener('pointermove',e=>{const stg=document.querySelector('#stageHost .rv-stage');if(!stg||!$('#presentation').hidden){st.pcMouse=null;return;}const r=stg.getBoundingClientRect();"
  "if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom||e.target.closest?.('#inspector,.quick-bar,#quickBar,.ribbon,.modal')){st.pcMouse=null;return;}"
  "const p=stagePoint(e);st.pcMouse=p?{x:p.x,y:p.y,page:current().id}:null;},{passive:true,capture:true});")
# Ctrl+D 복제도 칸 역할 표시 유지
R("  const copy=M.clone(o);copy.id=ids.get(o.id);\n  copy.x=M.clamp(o.x+22,0,M.W-o.w);",
  "  const copy=M.clone(o);copy.id=ids.get(o.id);if(['toc-entry','timeline-step'].includes(o.role)){copy.pcCardRole=o.pcCardRole||o.role;copy.pcCardTpl=o.pcCardTpl??current().templateId;}\n  copy.x=M.clamp(o.x+22,0,M.W-o.w);")

R("const BUILD_VERSION='PageCraft v12.41.0 · 테마별 목차 칸';","const BUILD_VERSION='PageCraft v12.42.0 · 목록·타임라인 칸 테마색';")
R('<title>페이지공방 v12.41.0 · 테마별 목차 칸</title>','<title>페이지공방 v12.42.0 · 목록·타임라인 칸 테마색</title>')
R('Jungmin Jo · PageCraft v12.41.0</span>','Jungmin Jo · PageCraft v12.42.0</span>')
open(out,'w',encoding='utf-8').write(html);print('patched',out,len(html))
