"""PageCraft v12.40.0 — 닌텐도 테마 빨강·하양(#E70012·#FFFFFF), 좁은 세로 그래프 항목 이름 기울이기·건너뛰기, 원·도넛 6개까지('기타' 합침).
Usage: python3 -I patch_v12400.py <PageCraft_v12.39.0_*.html> <out.html>"""
import sys
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
def R(old, new, n=1):
    global html
    c = html.count(old); assert c == n, f'expected {n} got {c}: {old[:80]!r}'
    html = html.replace(old, new)
assert 'data-tilt=' not in html, 'already patched'
assert 'pcResizeSnap' in html, 'needs v12.39'

# 1) 닌텐도 테마: 빨강 #E70012 + 하양만 (사용자 제공 로고 이미지에서 추출, 2026-11-19). 본문 글자는 읽기용 검정 유지
R('{"id":"nintendo-light","name":"닌텐도 · 레드","bg":"#FAFAFA","panel":"#FFFFFF","fg":"#1A1A1A","accent":"#E60012",',
  '{"id":"nintendo-light","name":"닌텐도 · 레드","bg":"#FFFFFF","panel":"#FFFFFF","fg":"#1A1A1A","accent":"#E70012",')
R('"legacyTexture":"linear-gradient(180deg,#E6001207,transparent 28%)","categoryCardFill":"#FFFFFF","categoryBorder":"#E60012","accent2":"#1A1A1A","soft":"#FAFAFA","tint":"#FDECEE","brandSource":"Nintendo Red #E60012(룩북, 공식 HEX 미공개)"}',
  '"legacyTexture":"linear-gradient(180deg,#E7001207,transparent 28%)","categoryCardFill":"#FFFFFF","categoryBorder":"#E70012","accent2":"#E70012","highlight":"#E70012","soft":"#FFFFFF","tint":"#FDE8EA","brandSource":"Nintendo Red #E70012 + White #FFFFFF (닌텐도 스위치 로고 이미지 추출, 2026-11-19)"}')
R('.rv-stage[data-theme-id="nintendo-light"] .rv-court-nav-card{\n  border:2px solid #E60012!important;',
  '.rv-stage[data-theme-id="nintendo-light"] .rv-court-nav-card{\n  border:2px solid #E70012!important;')
R('.rv-stage[data-theme-id="nintendo-light"] .rv-court-nav-card:hover{\n  box-shadow:0 0 0 2px rgba(230,0,18,.16)!important;',
  '.rv-stage[data-theme-id="nintendo-light"] .rv-court-nav-card:hover{\n  box-shadow:0 0 0 2px rgba(231,0,18,.16)!important;')
R('.rv-stage[data-theme-id="nintendo-light"] .rv-navigation-number{background:#E60012}',
  '.rv-stage[data-theme-id="nintendo-light"] .rv-navigation-number{background:#E70012}')

# 2) 원·도넛: 6개까지. 넘으면 앞 5개 + '기타'(나머지 합). 음수가 있으면 합치지 않고 기존 경고 그대로
R("function plotChart(data,thumb=false,options={}){\n const d=data||{},",
  "function plotChart(data,thumb=false,options={}){\n"
  " if(data&&['pie','donut'].includes(data.type)&&(data.labels||[]).length>6){const L=data.labels.slice(0,20),S=Array.isArray(data.series)&&data.series.length?data.series:[{name:'계열 1',color:data.accent||'#347CB4',values:data.values||[]}],v=S[0].values||[];"
  "if(!v.some(x=>Number(x)<0)){const rest=L.slice(5),sum=rest.reduce((a,_,i)=>a+Math.max(0,Number(v[i+5])||0),0);"
  "data={...data,labels:[...L.slice(0,5),'기타'],series:[{...S[0],values:[...v.slice(0,5),sum]},...S.slice(1)],highlight:Number.isInteger(data.highlight)&&data.highlight<5?data.highlight:-1,pieOther:rest};}} // v12.40 원·도넛 6개까지\n"
  " const d=data||{},")
R("<button type=\"button\" data-action=\"chartAddPoint\" ${labels.length>=20?'disabled':''}>+ 항목</button>",
  "<button type=\"button\" data-action=\"chartAddPoint\" ${labels.length>=(['pie','donut'].includes(o.chart?.type)?6:20)?'disabled':''}>+ 항목</button>")
R("원형 그래프는 첫 번째 계열의 0 이상 값만 표시합니다.",
  "원형·도넛은 첫 번째 계열의 0 이상 값만, 6개까지 표시합니다(넘는 항목은 '기타'로 합침).")
R("if(action==='chartAddPoint'&&o.chart.labels.length<20)",
  "if(action==='chartAddPoint'&&o.chart.labels.length<(['pie','donut'].includes(o.chart.type)?6:20))")

# 3) 좁은 세로 그래프: 항목 8개 초과 + 이름이 칸보다 넓으면 45° 기울이고, 그래도 붙으면 한 칸씩 건너뜀(막대·점에 마우스 올리면 전체 이름)
R("labelRows=Math.min(3,Math.max(...rows.map(r=>r.length),1));\n  const bottom=Math.max(top+45,H-12-legendHeight-(d.xLabel?32:0)-labelRows*lineHeight-16),height=bottom-top;",
  "labelRows=Math.min(3,Math.max(...rows.map(r=>r.length),1));\n"
  "  const catFs=F(20),tilt=labels.length>8&&Math.max(...rows.map(r=>Math.max(...r.map(s=>width(s,catFs)))))>xStep-4;let tiltSkip=1,tiltW=0; // v12.40\n"
  "  if(tilt){tiltSkip=Math.max(1,Math.ceil(catFs*1.25/(xStep*.7071)));tiltW=Math.min(Math.max(...labels.map(l=>width(l,catFs))),Math.max(40,H*.26/.7071));}\n"
  "  const labelBlock=tilt?tiltW*.7071+catFs*.9:labelRows*lineHeight;\n"
  "  const bottom=Math.max(top+45,H-12-legendHeight-(d.xLabel?32:0)-labelBlock-16),height=bottom-top;")
R("labels.forEach((label,i)=>{const x=left+xStep*(i+.5),lines=rows[i].slice(0,labelRows);",
  "labels.forEach((label,i)=>{const x=left+xStep*(i+.5);\n"
  "   if(tilt){if(i%tiltSkip)return;const ax=x+catFs*.3,ay=bottom+catFs*.95,mw=Math.min(tiltW,(ax-2)/.7071);svg+=`<text x=\"${ax}\" y=\"${ay}\" transform=\"rotate(-45 ${ax} ${ay})\" text-anchor=\"end\" font-size=\"${catFs}\" font-weight=\"${hl===i?800:600}\" fill=\"${ink}\" data-chart-label=\"category\" data-tilt=\"45\"><title>${esc(label)}</title>${esc(fit(label,mw,catFs))}</text>`;return;}\n"
  "   const lines=rows[i].slice(0,labelRows);")
R("if(d.xLabel)svg+=text((left+right)/2,bottom+labelRows*lineHeight+35,",
  "if(d.xLabel)svg+=text((left+right)/2,bottom+labelBlock+35,")

# 3-2) 가로형(가로 막대·가로 누적·일정)도 항목이 많아 줄 간격이 글씨보다 좁으면 이름 한 칸씩 건너뜀
R("   svg+=text(left-10,yc+6,fit(label,catW-10,tickFont),tickFont,'end',`data-chart-label=\"category\"`)",
  "   if(!(band<tickFont*1.15&&i%Math.ceil(tickFont*1.15/band)))svg+=text(left-10,yc+6,fit(label,catW-10,tickFont),tickFont,'end',`data-chart-label=\"category\"`)")

# 4) 설정 칸을 접으면 내용이 줄어 스크롤 위치가 자동 보정되며 'scroll'이 생김 → 그 직후(0.5초)엔 길잡이 말풍선을 지우지 않음 (사용자 스크롤만 지움)
R("document.addEventListener('toggle',e=>{if(e.target.closest?.('#inspector'))requestAnimationFrame(pcCue);},true);\n$('#inspector')?.addEventListener('scroll',()=>document.querySelector('.pc-cue-bubble')?.remove(),{passive:true});",
  "document.addEventListener('toggle',e=>{if(e.target.closest?.('#inspector')){window.pcCueToggleT=Date.now();requestAnimationFrame(pcCue);}},true);\n$('#inspector')?.addEventListener('scroll',()=>{if(Date.now()-(window.pcCueToggleT||0)>500)document.querySelector('.pc-cue-bubble')?.remove();},{passive:true});")

R("const BUILD_VERSION='PageCraft v12.39.0 · 남은 문제 정리';", "const BUILD_VERSION='PageCraft v12.40.0 · 닌텐도 색·그래프 이름';")
R('<title>페이지공방 v12.39.0 · 남은 문제 정리</title>', '<title>페이지공방 v12.40.0 · 닌텐도 색·그래프 이름</title>')
R('Jungmin Jo · PageCraft v12.39.0</span>', 'Jungmin Jo · PageCraft v12.40.0</span>')
open(out, 'w', encoding='utf-8').write(html); print('patched', out, len(html))
