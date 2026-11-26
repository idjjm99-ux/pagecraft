"""PageCraft v12.50.0 — 배율 화면·겹침 이름·Source 정리·!important 정리
기준: v12.49.0 Lite.
 1) Windows 배율 화면(1366×768@125% → 보이는 칸 약 1093×491, 1920×1080@150% → 1280×597): 높이 640 미만에서 화면 전체가 밀려 스크롤,
    ≤1100 폭에선 도구줄 3줄(229px)이라 슬라이드가 120px만 보이고 맞춤 배율 하한(28%) 때문에 아래가 잘림
    → #app 최소 높이 640→460, 높이 660 이하: 머리줄 65→50, 도구줄 단추 아이콘·글자 가로 배치(48→32px), 페이지 막대 53→38, 상태줄 31→24(한 줄),
      설정 칸 머리 설명 숨김, 맞춤 배율 하한 28%→15%(축소 단추 하한도 15%)
 1-b) 1101~1350 폭: 왼쪽 '페이지' 머리(제목이 세로로 '페이/지', 단추 글자 2줄)·글꼴 적용 단추(카드 밖) → ≤1100에서 쓰던 줄바꿈 배치를 ≤1350까지
 2) 겹침·순서 목록 이름: 8글자 줄임 없앰 → 칸 폭만큼 보이고 넘칠 때만 '…'(말풍선 전체 이름 그대로)
Usage: python3 -I patch/patch_v12500.py <PageCraft_v12.49.0_Lite.html> <out.html>"""
import sys
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
def R(old, new, n=1):
    global html
    c = html.count(old); assert c == n, f'expected {n} got {c}: {old[:80]!r}'
    html = html.replace(old, new)
def cut(a, b):
    """a로 시작해 b로 끝나는 유일한 구간을 잘라 돌려줌(제거)"""
    global html
    assert html.count(a) == 1, ('start', a[:60]); i = html.index(a)
    j = html.index(b, i) + len(b); seg = html[i:j]; html = html[:i] + html[j:]; return seg, i
assert "BUILD_VERSION='PageCraft v12.49.0 · 좁은 화면 잘림(설정 칸·겹침 목록)'" in html, 'needs v12.49.0'
assert 'pc-v12500' not in html, 'already patched'

# ── 1) 변경 ──────────────────────────────────────────────
# CSS는 <style id="pc-ui-css"> 안 해당 구역 규칙을 직접 R()로 고칠 것. 맨 아래 덧붙이기·!important 덧칠 금지.
# 새 JS에는 주석 /*pc-v12500*/ 를 넣어 '이미 적용' 검사가 작동하게 할 것.
a = html.find('<style id="pc-ui-css">'); b = html.find('</style>', a); assert a > 0
css = html[a:b]
def C(old, new, n=1):
    global css
    c = css.count(old); assert c == n, f'css expected {n} got {c}: {old[:80]!r}'
    css = css.replace(old, new)
# 1) 최소 높이·낮은 화면(높이 ≤660) 틀: 기초 구역
C("#app{height:100vh;display:flex;flex-direction:column;min-height:640px}",
  "#app{height:100vh;display:flex;flex-direction:column;min-height:460px}")
C(".right-pane #inspector{padding:8px}.modal-head{padding:16px}}",
  ".right-pane #inspector{padding:8px}.modal-head{padding:16px}}"
  "@media(max-height:660px){.app-header{height:50px;min-height:50px}.stage-nav{height:38px;min-height:38px}"
  ".status-line{height:24px;min-height:24px}.status-line>:not(#rv-app-signature){white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}"
  ".pane-head{padding-top:9px;padding-bottom:8px}.right-pane .pane-head small{display:none}}")
# 1) 도구줄: 높이 ≤660이면 단추 아이콘·글자 가로(같은 구역의 #app .ribbon 규칙 바로 뒤)
C("#app .ribbon .opacity-control span{font-weight:500;color:#475569}\n",
  "#app .ribbon .opacity-control span{font-weight:500;color:#475569}\n"
  "/* 낮은 화면(Windows 배율 125·150% 노트북): 단추 아이콘·글자 가로, 줄 높이 48→32 */\n"
  "@media(max-height:660px){#app .ribbon{padding-top:3px;padding-bottom:3px;row-gap:3px}"
  "#app .ribbon .tool-btn{flex-direction:row;min-height:32px;padding:2px 7px;gap:4px}"
  "#app .ribbon .rv-ico,#app .ribbon .rv-ico svg{width:18px;height:18px}"
  "#app .ribbon .ribbon-group:not(.ribbon-format){min-height:32px}"
  "#app .ribbon>.ribbon-format{padding-top:3px;padding-bottom:0;min-height:0;row-gap:3px}"
  "#app .ribbon>.ribbon-format .tool-btn{min-height:32px}"
  "#app .ribbon .color-label{height:32px;flex-direction:row;gap:4px}"
  "#app .ribbon .text-swatches .text-swatch{min-height:32px;padding-top:1px;padding-bottom:1px;gap:0}"
  "#app .ribbon .tool-btn .pc-lock-badge{top:-1px;right:auto;left:17px;min-width:15px;height:15px;font-size:10px;line-height:15px;padding:0 3px}}\n")
# 1-b) 1101~1350: 왼쪽 머리·글꼴 적용 단추 줄바꿈 배치를 ≤1350까지
C("@media(max-width:1100px){\n .workspace{grid-template-columns:186px minmax(360px,1fr) 232px}\n"
  " .left-pane .pane-head{flex-wrap:wrap;align-items:flex-start;gap:6px;padding:10px 8px}\n"
  " .left-pane .pane-head>div{min-width:100%;justify-content:space-between}\n"
  " .left-pane .pane-head b{white-space:nowrap}\n"
  " .page-list-buttons{flex-wrap:wrap;justify-content:flex-start}\n"
  " .scope-fonts{grid-template-columns:minmax(0,1fr);gap:4px 0}\n"
  " .scope-fonts>.inspect-button{margin-top:0;justify-self:end}\n",
  "@media(max-width:1350px){\n"
  " .left-pane .pane-head{flex-wrap:wrap;align-items:flex-start;gap:6px;padding:10px 8px}\n"
  " .left-pane .pane-head>div{min-width:100%;justify-content:space-between}\n"
  " .left-pane .pane-head b{white-space:nowrap}\n"
  " .page-list-buttons{flex-wrap:wrap;justify-content:flex-start}\n"
  " .scope-fonts{grid-template-columns:minmax(0,1fr);gap:4px 0}\n"
  " .scope-fonts>.inspect-button{margin-top:0;justify-self:end}\n"
  "}\n"
  "@media(max-width:1100px){\n .workspace{grid-template-columns:186px minmax(360px,1fr) 232px}\n")
C("#app .ribbon .pc-align-group>small{font-size:11.5px;font-weight:500;color:#475569;line-height:1.15;white-space:nowrap}",
  "#app .ribbon .pc-align-group>small{font-size:11.5px;font-weight:500;color:#475569;line-height:1.15;white-space:nowrap}"
  "@media(max-height:660px){#app .ribbon .pc-align-group{flex-direction:row;gap:4px}}")
# 상태줄: 낮은 화면에서 안내 글만 말줄임, 서명(버전)은 온전히
C("#rv-app-signature{font-size:10px;color:#8D9BA8;white-space:nowrap;margin-left:auto;align-self:center;}",
  "#rv-app-signature{font-size:10px;color:#8D9BA8;white-space:nowrap;margin-left:auto;align-self:center;flex-shrink:0}")
html = html[:a] + css + html[b:]
# 1) 맞춤 배율 하한 28%→15%, 축소 단추 하한 30%→15%
R("const w=Math.max(300,viewport.clientWidth-54),h=Math.max(220,viewport.clientHeight-55);st.zoom=Math.max(.28,Math.min(1.25,w/M.W,h/M.H));",
  "const w=Math.max(300,viewport.clientWidth-54),h=Math.max(120,viewport.clientHeight-55);st.zoom=Math.max(.15,Math.min(1.25,w/M.W,h/M.H));/*pc-v12500*/")
R("st.zoom=M.clamp(Math.round((st.zoom+delta)*100)/100,.3,2.5);", "st.zoom=M.clamp(Math.round((st.zoom+delta)*100)/100,.15,2.5);")
# 2) 겹침 목록 이름: 8글자 줄임 없앰(칸 폭은 CSS 말줄임)
R("label=[...fullLabel].length>8?[...fullLabel].slice(0,8).join('')+'…':fullLabel,", "label=fullLabel,")

# ── 버전 문자열(BUILD_VERSION·하단 서명. <title>은 v12.46부터 문서 제목이라 안 건드림) ──
R("const BUILD_VERSION='PageCraft v12.49.0 · 좁은 화면 잘림(설정 칸·겹침 목록)';", "const BUILD_VERSION='PageCraft v12.50.0 · 배율 화면·겹침 이름·Source 정리·!important 정리';")
R('Jungmin Jo · PageCraft v12.49.0</span>', 'Jungmin Jo · PageCraft v12.50.0</span>')
open(out, 'w', encoding='utf-8').write(html); print('patched', out, len(html))
