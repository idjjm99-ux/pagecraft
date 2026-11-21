"""PageCraft v12.43.0 — 양식 06 세로 레일 목차: 레일 선·점 고정 파랑(#356A99) → 테마색.
Usage: python3 -I patch_v12430.py <PageCraft_v12.42.0_Lite.html> <out.html>"""
import sys
src,out=sys.argv[1],sys.argv[2]
html=open(src,encoding='utf-8').read()
def R(old,new,n=1):
    global html
    c=html.count(old);assert c==n,f'expected {n} got {c}: {old[:80]!r}'
    html=html.replace(old,new)
assert 'function pcSurfaceFill' in html,'needs v12.42'
assert 'pcRailColor' not in html,'already patched'

# 1) 레일색: 테마 강조색 → 보조 강조색 순으로, 페이지 바탕과 대비 3 이상(그림 요소 기준)인 것. 둘 다 약하면(카카오 노랑 등) 강조색을 글자색 쪽으로 섞어 3 이상 될 때까지
#    기본 파랑(#356A99) 그대로일 때만 → 사용자가 바꾼 색은 그대로. 저장 데이터는 안 바뀜(화면·발표·인쇄·PPT는 화면 그리기를 그대로 씀)
R("function pcThemeCard(o,page,palettes){\n if(!o||!page||o.kind!=='shape')return null;\n",
  "function pcRailColor(c){\n"
  " for(const x of [c.accent,c.accent2])if(M.isHex(x)&&M.isHex(c.paper)&&ratio(x,c.paper)>=3)return x;\n"
  " if(!M.isHex(c.accent)||!M.isHex(c.paper)||!M.isHex(c.ink))return c.ink||'#356A99';\n"
  " for(let k=.1;k<=1.001;k+=.1){const m='#'+[1,3,5].map(i=>Math.round(parseInt(c.accent.slice(i,i+2),16)*(1-k)+parseInt(c.ink.slice(i,i+2),16)*k).toString(16).padStart(2,'0')).join('').toUpperCase();if(ratio(m,c.paper)>=3)return m;}\n"
  " return c.ink;\n"
  "}\n"
  "function pcIsRail(o,page){if(!o||!page)return false;const role=o.pcCardRole||o.role,tpl=Number(o.pcCardTpl??page.templateId);return tpl===6&&(role==='toc-rail'||(role==='template-decor'&&o.decorOriginal==='dot'));}\n"
  "function pcThemeRail(o,page,palettes){\n"
  " // v12.43: 06 레일 선(stroke)·점(fill) — 기본 파랑일 때만 테마색\n"
  " if(!pcIsRail(o,page)||o.style?.gradient)return null;\n"
  " const v=String(o.kind==='line'?o.style?.stroke:o.style?.fill||'').toUpperCase();\n"
  " return v==='#356A99'?pcRailColor(bgObj(page,palettes)):null;\n"
  "}\n"
  "function pcThemeCard(o,page,palettes){\n if(!o||!page||o.kind!=='shape')return null;\n"
  " {const rc=pcThemeRail(o,page,palettes);if(rc)return {fill:rc,mode:'fill',border:false,radius:null};}\n")

# 2) 선 그리기: 레일 선이면 테마색
R("line.setAttribute('stroke',s.stroke&&s.stroke!=='transparent'?s.stroke:'#327CB4');",
  "line.setAttribute('stroke',pcThemeRail(o,page,palettes)||(s.stroke&&s.stroke!=='transparent'?s.stroke:'#327CB4'));")

# 3) 복사·Ctrl+D로 붙인 레일 선·점도 원래 역할 표시 → 붙여도 파랑으로 안 돌아감
R("st.objectClipboard=items.map(item=>{const c=M.clone(item);if(['toc-entry','timeline-step'].includes(item.role))",
  "st.objectClipboard=items.map(item=>{const c=M.clone(item);if(['toc-entry','timeline-step','toc-rail','template-decor'].includes(item.role))")
R("const copy=M.clone(o);copy.id=ids.get(o.id);if(['toc-entry','timeline-step'].includes(o.role))",
  "const copy=M.clone(o);copy.id=ids.get(o.id);if(['toc-entry','timeline-step','toc-rail','template-decor'].includes(o.role))")

R("const BUILD_VERSION='PageCraft v12.42.0 · 목록·타임라인 칸 테마색';","const BUILD_VERSION='PageCraft v12.43.0 · 레일 목차 테마색';")
R('<title>페이지공방 v12.42.0 · 목록·타임라인 칸 테마색</title>','<title>페이지공방 v12.43.0 · 레일 목차 테마색</title>')
R('Jungmin Jo · PageCraft v12.42.0</span>','Jungmin Jo · PageCraft v12.43.0</span>')
open(out,'w',encoding='utf-8').write(html);print('patched',out,len(html))
