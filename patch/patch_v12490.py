"""PageCraft v12.49.0 — 좁은 화면 잘림(설정 칸·겹침 목록)
기준: v12.48.0 Lite.
 화면 폭이 좁을 때 오른쪽 상세 설정 칸이 잘리던 것(곁가지 claude/zealous-mendel-3moh1n v12.46.0 수정을 본류로 옮김 + 새로 찾은 1건).
 1) 페이지 설정 [페이지에 적용]·[문서 전체 적용]: 1100px 이하에서 칸 밖으로 29px 넘쳐 잘림 → 글꼴 고르기 아래 줄, 오른쪽 맞춤
 2) 탭 작은 글씨(수치·색·위치·잠금 / 배경·글꼴·전환): 1350px 이하 탭 테두리에 닿거나 잘림 → 좌우 여백 0·10px, 1100px 이하 9px
 3) 겹침·순서 목록: 이름이 '1년 …'처럼 2~3글자만 보이고 1100px 이하에선 아예 안 보이며 '겹침 n' 표도 잘림(모든 폭)
    → 첫 줄 이름(칸 폭 전부) + 둘째 줄 [종류 표][겹침 n]. 1100px 이하 ↑↓·잠금 단추와 두 표 여백 줄임. 이름 8글자 줄임·전체 이름 말풍선은 그대로
 0) 머리줄: 1101~1240px에서 저장 상태 글씨가 길면(예: '배치 잠금 중: …') [▶ 발표]가 화면 밖(최대 63px) → ≤1240에서 상태 글씨·부제 숨김
    (곁가지의 ≤1100 단추 여백 12→8px은 v12.46 [저장 ▾] 메뉴로 필요 없어져 빼냄)
 · CSS는 pc-ui-css 안 해당 구역 규칙을 직접 고침(새 블록·!important 없음). 저장 데이터·동작 변화 없음
Usage: python3 -I patch/patch_v12490.py <PageCraft_v12.48.0_Lite.html> <out.html>"""
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
assert "BUILD_VERSION='PageCraft v12.48.0 · 회전·발표자 보기'" in html, 'needs v12.48.0'
assert 'pc-v12490' not in html, 'already patched'

# ── 1) 변경 ──────────────────────────────────────────────
# CSS는 <style id="pc-ui-css"> 안 해당 구역 규칙을 직접 R()로 고칠 것. 맨 아래 덧붙이기·!important 덧칠 금지.
# 새 JS에는 주석 /*pc-v12490*/ 를 넣어 '이미 적용' 검사가 작동하게 할 것.
a = html.find('<style id="pc-ui-css">'); b = html.find('</style>', a); assert a > 0
css = html[a:b]
def C(old, new):
    global css
    c = css.count(old); assert c == 1, f'css expected 1 got {c}: {old[:80]!r}'
    css = css.replace(old, new)
# 0) 머리줄: 1101~1240px에서 저장 상태 글씨가 길면(예: '배치 잠금 중: …') 단추줄이 화면 밖으로 최대 63px → ≤1240에서도 숨김(≤1100과 같은 처리)
C("@media(max-width:1100px){.brand{gap:8px}.brand small{display:none}.header-actions{gap:4px}.save-status{display:none}",
  "@media(max-width:1240px){.brand small{display:none}.header-actions{gap:4px}.save-status{display:none}}"
  "@media(max-width:1100px){.brand{gap:8px}.brand small{display:none}.header-actions{gap:4px}.save-status{display:none}")
# 1)·2-1100) 1100px 이하 구역(1024 화면 오른쪽 칸 232px)
C(" .page-list-buttons{flex-wrap:wrap;justify-content:flex-start}\n}",
  " .page-list-buttons{flex-wrap:wrap;justify-content:flex-start}\n"
  " .scope-fonts{grid-template-columns:minmax(0,1fr);gap:4px 0}\n"
  " .scope-fonts>.inspect-button{margin-top:0;justify-self:end}\n"
  " #inspectorTabs [data-inspector-tab] small{font-size:9px;letter-spacing:-.04em}\n"
  " .rv-layer-row>button[data-layer-action]{padding:4px 2px;min-width:22px}\n"
  " .rv-layer-row>.rv-layer-name{column-gap:3px;padding-left:3px;padding-right:3px}.rv-layer-row>.rv-layer-name>.rv-layer-type,.rv-layer-row>.rv-layer-name>.rv-overlap-count{padding:0 2px;font-size:9px}\n"
  "}")
# 2) 1350px 이하 구역(오른쪽 칸 270px)
C(".template-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}",
  ".template-grid{grid-template-columns:repeat(4,minmax(0,1fr))}"
  "#inspectorTabs [data-inspector-tab]{padding-left:0;padding-right:0}"
  "#inspectorTabs [data-inspector-tab] small{font-size:10px;letter-spacing:-.03em}}")
# 3) 겹침 목록 줄: 종류 표 | 이름 / 겹침 n
C("/* Layer list: one line, short label, full text on hover */\n"
  ".rv-layer-name>span:not(.rv-layer-type){flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\n"
  ".rv-layer-name{overflow:hidden}\n"
  ".rv-layer-name .rv-overlap-count{flex:none;white-space:nowrap}\n",
  "/* Layer list: short label on its own line, type tag + overlap count under it (v12.49: name was squeezed to 0-3 chars); full text on hover */\n"
  ".rv-layer-name>span:not(.rv-layer-type){grid-area:name;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px}\n"
  ".rv-layer-name{overflow:hidden;display:grid;grid-template-columns:auto minmax(0,1fr);grid-template-areas:'name name' 'type count';column-gap:4px;row-gap:2px;align-items:center}\n"
  ".rv-layer-name>.rv-layer-type{grid-area:type;padding:0 4px;line-height:14px;text-align:center}\n"
  ".rv-layer-name .rv-overlap-count{grid-area:count;justify-self:start;margin-left:0;padding:0 4px;line-height:14px;white-space:nowrap}\n")
html = html[:a] + css.replace('/* Layer list: type tag', '/*pc-v12490*/ /* Layer list: type tag') + html[b:]

# ── 버전 문자열(BUILD_VERSION·하단 서명. <title>은 v12.46부터 문서 제목이라 안 건드림) ──
R("const BUILD_VERSION='PageCraft v12.48.0 · 회전·발표자 보기';", "const BUILD_VERSION='PageCraft v12.49.0 · 좁은 화면 잘림(설정 칸·겹침 목록)';")
R('Jungmin Jo · PageCraft v12.48.0</span>', 'Jungmin Jo · PageCraft v12.49.0</span>')
open(out, 'w', encoding='utf-8').write(html); print('patched', out, len(html))
