# v12.40.0 Lite -> v12.41.0 Lite. 치환만, 원문 일치 개수 검사.
import sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    n=s.count(old)
    if n!=count: raise SystemExit(f'일치 {n}개(기대 {count}): {old[:80]!r}')
    s=s.replace(old,new)

# 0. 버전
rep('페이지공방 v12.40.0 · 닌텐도 색·그래프 이름','페이지공방 v12.41.0 · 테마별 목차 칸')
rep('Jungmin Jo · PageCraft v12.40.0','Jungmin Jo · PageCraft v12.41.0')
rep("BUILD_VERSION='PageCraft v12.40.0 · 닌텐도 색·그래프 이름'","BUILD_VERSION='PageCraft v12.41.0 · 테마별 목차 칸'")

# 1. 테마별 목차 칸 모양 (양식 04·07)
helper=r"""// v12.41: 양식 04·07 목차 칸 — 고정 파스텔 대신 테마별 칸 모양(강조 방식·모서리). 파스텔 기본색일 때만 적용 → 사용자가 바꾼 색·테두리·모서리는 그대로.
const PC_TOC_PASTEL=new Set(['#DDEAF7','#E2F2ED','#F4E8D7','#E8E2F3','#E5F0FA','#E8F2EB','#F1E8F4','#FAEFDE']);
const PC_CARD_DEFAULT={mode:'top',w:5,r:10};
const PC_CARD_STYLE={'nintendo-light':{mode:'border',w:2,r:18},'krafton-light':{mode:'left',w:5,r:2},'pro-ivory-brick':{mode:'top',w:4,r:0},'google-light':{mode:'border',w:1.5,r:16},'kakao-bank-light':{mode:'top',w:8,r:18},'zara-editorial':{mode:'top',w:3,r:0},'malfoy-v122-archive':{mode:'border',w:1.5,r:0}};
function pcThemeCard(o,page,palettes){
 if(!o||o.kind!=='shape'||o.role!=='toc-entry'||!page||![4,7].includes(Number(page.templateId)))return null;
 const s=o.style||{};if(s.gradient||typeof s.fill!=='string'||!PC_TOC_PASTEL.has(s.fill.toUpperCase()))return null;
 const p=paletteFor(page,palettes)||{},c=bgObj(page,palettes),cfg=PC_CARD_STYLE[page.themeId]||PC_CARD_DEFAULT;
 const dark=M.isHex(c.paper)&&ratio(c.paper,'#000000')<4.2;
 const fill=M.isHex(p.categoryCardFill)?p.categoryCardFill:(dark?c.soft:c.paper);
 const radius=(!o.shapeType||o.shapeType==='rect')?cfg.r:null; // 기본 직사각형일 때만 테마 모서리, '둥근 사각형' 등으로 바꾸면 사용자 값
 const border=s.borderWidth==null&&(!s.stroke||s.stroke==='transparent'||String(s.stroke).toUpperCase()==='#BFD3E6');
 return {fill,mode:cfg.mode,w:cfg.w,radius,border,accent:c.accent,rule:c.rule};
}
function resolveToken(v,colors){"""
rep('function resolveToken(v,colors){',helper)

# 1a. 글자색 자동 계산이 실제 칸 색을 보도록
rep("const colors=bgObj(page,palettes),fill=resolveToken(o.style?.fill,colors),opacity=Number(o.style?.bgTransparency||0);",
    "const colors=bgObj(page,palettes),fill=pcThemeCard(o,page,palettes)?.fill||resolveToken(o.style?.fill,colors),opacity=Number(o.style?.bgTransparency||0);")
rep("  const color=resolveToken(q.style?.fill,colors)||resolveToken(q.frameFill,colors);\n  if(M.isHex(color))return color;",
    "  const color=pcThemeCard(q,page,palettes)?.fill||resolveToken(q.style?.fill,colors)||resolveToken(q.frameFill,colors);\n  if(M.isHex(color))return color;")
rep(" const token=resolveToken(objFill,colors);\n"," const token=pcThemeCard(o,page,palettes)?.fill||resolveToken(objFill,colors);\n")

# 1b. 그리기 (편집·발표·썸네일·인쇄·PPT 모두 같은 그리기 사용)
rep("if(o.role==='template-frame'&&o.shapeType!=='circle')n.classList.add('rv-full-card-band');\n",
    "if(o.role==='template-frame'&&o.shapeType!=='circle')n.classList.add('rv-full-card-band');\n"
    " {const tc=pcThemeCard(o,page,palettes);if(tc){n.classList.add('pc-theme-card');n.dataset.cardMode=tc.mode;n.style.setProperty('--rv-fill-bg',tc.fill);if(tc.radius!=null)n.style.borderRadius=tc.radius+'px';"
    "if(tc.border){n.style.borderStyle='solid';n.style.borderColor=tc.rule;n.style.borderWidth='1px';"
    "if(tc.mode==='border'){n.style.borderColor=tc.accent;n.style.borderWidth=tc.w+'px';}else if(tc.mode==='top'){n.style.borderTopColor=tc.accent;n.style.borderTopWidth=tc.w+'px';}else if(tc.mode==='left'){n.style.borderLeftColor=tc.accent;n.style.borderLeftWidth=tc.w+'px';}}}}\n")

# 2. 상단 띠 공통화: 05 구분선 목록 목차 · 07 사분면 허브 목차 · 16 타임라인
bar='<rect fill=\\"var(--accent)\\" height=\\"7\\" rx=\\"0\\" width=\\"1120\\" x=\\"0\\" y=\\"0\\" />'
for name in ['구분선 목록 목차','사분면 허브 목차','타임라인']:
    head='aria-label=\\"'+name+'\\" role=\\"img\\" viewBox=\\"0 0 1120 790\\">'
    rep(head,head+bar)

open(dst,'w',encoding='utf-8').write(s)
print('ok',len(s))
