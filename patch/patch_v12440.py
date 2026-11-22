"""PageCraft v12.44.0 — v12.43 두 갈래 합치기 + 남은 결정 2건.
기준: v12.43.0(18:00, 영상 칸 장식 ▶ 없앰) Lite.
 1) 17:10 판 v12.43.0의 06 레일 선·점 테마색(patch_v12430 레일 부분) 그대로 이식
 2) 크래프톤 테마: 원 도형이 테마 CSS(.rv-shape 모서리 2px)에 눌려 네모로 보이던 것 → 원은 다른 테마처럼 원형 유지
 3) 05 목차 구분선 고정 회색(#97A8B8·#C2CAD4) → 테마 구분선색(rule). 너무 흐리면(대비<1.5) 글자색 쪽으로 섞어 보정
    기본 회색일 때만, 저장 데이터 불변, 복사·Ctrl+D한 선도 유지
Usage: python3 -I patch_v12440.py <PageCraft_v12.43.0_Lite.html(▶ 없앰 판)> <out.html>"""
import sys
src,out=sys.argv[1],sys.argv[2]
html=open(src,encoding='utf-8').read()
def R(old,new,n=1):
    global html
    c=html.count(old);assert c==n,f'expected {n} got {c}: {old[:80]!r}'
    html=html.replace(old,new)
assert "BUILD_VERSION='PageCraft v12.43.0 · 영상 칸 장식 ▶ 없앰'" in html,'needs v12.43.0 (▶ 없앰 판)'
assert 'pcRailColor' not in html,'already patched'

# 1) 레일색 (patch_v12430과 같은 코드) + 3) 구분선색
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
  "function pcSepColor(c){\n"
  " // v12.44: 05 구분선 — 테마 구분선색(rule). 바탕과 너무 비슷하면(대비<1.5) 글자색 쪽으로 섞음\n"
  " const base=M.isHex(c.rule)?c.rule:null;if(!M.isHex(c.paper)||!M.isHex(c.ink))return base||'#C2CAD4';\n"
  " if(base&&ratio(base,c.paper)>=1.5)return base;\n"
  " const from=base||c.paper;\n"
  " for(let k=.1;k<=1.001;k+=.1){const m='#'+[1,3,5].map(i=>Math.round(parseInt(from.slice(i,i+2),16)*(1-k)+parseInt(c.ink.slice(i,i+2),16)*k).toString(16).padStart(2,'0')).join('').toUpperCase();if(ratio(m,c.paper)>=1.5)return m;}\n"
  " return c.ink;\n"
  "}\n"
  "function pcThemeSep(o,page,palettes){\n"
  " if(!o||!page||o.kind!=='line'||o.style?.gradient)return null;const role=o.pcCardRole||o.role,tpl=Number(o.pcCardTpl??page.templateId);\n"
  " if(role!=='toc-separator'||tpl!==5)return null;\n"
  " return ['#97A8B8','#C2CAD4'].includes(String(o.style?.stroke||'').toUpperCase())?pcSepColor(bgObj(page,palettes)):null;\n"
  "}\n"
  "function pcThemeCard(o,page,palettes){\n if(!o||!page||o.kind!=='shape')return null;\n"
  " {const rc=pcThemeRail(o,page,palettes);if(rc)return {fill:rc,mode:'fill',border:false,radius:null};}\n")

# 선 그리기: 레일 선·05 구분선이면 테마색
R("line.setAttribute('stroke',s.stroke&&s.stroke!=='transparent'?s.stroke:'#327CB4');",
  "line.setAttribute('stroke',pcThemeRail(o,page,palettes)||pcThemeSep(o,page,palettes)||(s.stroke&&s.stroke!=='transparent'?s.stroke:'#327CB4'));")

# 복사·Ctrl+D로 붙인 레일 선·점·구분선도 원래 역할 표시
R("st.objectClipboard=items.map(item=>{const c=M.clone(item);if(['toc-entry','timeline-step'].includes(item.role))",
  "st.objectClipboard=items.map(item=>{const c=M.clone(item);if(['toc-entry','timeline-step','toc-rail','template-decor','toc-separator'].includes(item.role))")
R("const copy=M.clone(o);copy.id=ids.get(o.id);if(['toc-entry','timeline-step'].includes(o.role))",
  "const copy=M.clone(o);copy.id=ids.get(o.id);if(['toc-entry','timeline-step','toc-rail','template-decor','toc-separator'].includes(o.role))")

# 2) 원 도형 표시 → 크래프톤 테마 모서리 2px 규칙에서 원은 제외
R("n.dataset.kind=o.kind;","n.dataset.kind=o.kind;if(o.kind==='shape'&&o.shapeType==='circle')n.dataset.shapeType='circle';else delete n.dataset.shapeType;")
R('[data-theme-id="krafton-light"] .rv-shape {border-radius:2px!important;box-shadow:none!important;}',
  '[data-theme-id="krafton-light"] .rv-shape {border-radius:2px!important;box-shadow:none!important;}[data-theme-id="krafton-light"] .rv-shape[data-shape-type="circle"] {border-radius:50%!important;}')

R("const BUILD_VERSION='PageCraft v12.43.0 · 영상 칸 장식 ▶ 없앰';","const BUILD_VERSION='PageCraft v12.44.0 · 레일·구분선 테마색, 원 유지';")
R('<title>페이지공방 v12.43.0 · 영상 칸 장식 ▶ 없앰</title>','<title>페이지공방 v12.44.0 · 레일·구분선 테마색, 원 유지</title>')
R('Jungmin Jo · PageCraft v12.43.0</span>','Jungmin Jo · PageCraft v12.44.0</span>')
open(out,'w',encoding='utf-8').write(html);print('patched',out,len(html))
