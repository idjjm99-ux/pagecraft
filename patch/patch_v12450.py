"""PageCraft v12.45.0 — 코드 정리(B안). 보이는 동작·화면은 그대로.
기준: v12.44.0 Lite.
 1) CSS 한 곳: v12.17~v12.44 화면 CSS 블록 37개 → <style id="pc-ui-css"> 1개 (원래 순서 그대로 이어붙여 적용 우선순위 동일)
    · 같은 맥락·같은 선택자·같은 속성에서 뒤 선언에 완전히 덮여 적용되지 않던 선언 제거(이기는 쪽 값이 크롬에서 유효할 때만)
    · 시작 화면 블록(맨 앞)·글꼴 블록 2개는 제자리
 2) 단축키 한 곳: 흩어져 있던 편집기 키보드 처리 3곳(흐름도 칸 키·방향키 이동·편집기 단축키)을
    '단축키 한 곳'(PC_KEYS)으로 모음. 실행 순서·단계(캡처/버블) 그대로, 단축키 표(PC_KEYMAP)·Revival.keymap()
    · 발표 중엔 도달할 수 없던 죽은 분기 2개 삭제(편집기 Esc 안 발표 닫기, 편집기 방향키 안 발표 넘기기)
Usage: python3 -I patch_v12450.py <PageCraft_v12.44.0_Lite.html> <out.html> [valid45.json]"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import css45
src, out = sys.argv[1], sys.argv[2]
vpath = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'valid45.json')
html = open(src, encoding='utf-8').read()
def R(old, new, n=1):
    global html
    c = html.count(old); assert c == n, f'expected {n} got {c}: {old[:80]!r}'
    html = html.replace(old, new)
def cut(a, b):
    """html에서 a로 시작해 b로 끝나는 유일한 구간을 잘라 돌려줌(제거)"""
    global html
    assert html.count(a) == 1, ('start', a[:60]); i = html.index(a)
    j = html.index(b, i) + len(b); seg = html[i:j]; html = html[:i] + html[j:]; return seg, i
assert "BUILD_VERSION='PageCraft v12.44.0 · 레일·구분선 테마색, 원 유지'" in html, 'needs v12.44.0'
assert 'PC_KEYS' not in html and 'pc-ui-css' not in html, 'already patched'

# ── 2) 단축키 한 곳 ─────────────────────────────────────────────
# 2-a) 편집기 단축키 본체(UI 이벤트 모듈) → 꺼내서 앱으로
A_head = "  function installKeyboard(){\n document.addEventListener('keydown',e=>{\n"
A_tail = " if(e.key==='Delete'||e.key==='Backspace'){e.preventDefault();deleteObject()} });\n  }\n"
seg, at = cut(A_head, A_tail)
A_body = seg[len(A_head):-len(" });\n  }\n")] + '\n'
html = html[:at] + "  function installKeyboard(){} // v12.45: 편집기 단축키는 앱의 '단축키 한 곳'(PC_KEYS)으로 옮김\n" + html[at:]
dead1 = "if(!$('#presentation').hidden){closePresentation();return}"
dead2 = " if(!$('#presentation').hidden){if(e.key==='ArrowRight'||e.key==='ArrowDown')stepPresentation(1);else if(e.key==='ArrowLeft'||e.key==='ArrowUp')stepPresentation(-1);return;}\n"
assert A_body.count(dead1) == 1 and A_body.count(dead2) == 1
A_body = A_body.replace(dead1, '').replace(dead2, '')
R(" uiEventsCore.installKeyboard();\n", "")

# 2-b) 흐름도 칸 키(문서 캡처) → 꺼냄
B_head = "document.addEventListener('keydown',e=>{\n if(!st.flowNode||e.isComposing)return;"
seg, at = cut(B_head, "\n},true);\n")
B_body = seg[len("document.addEventListener('keydown',e=>{\n"):-len("},true);\n")]
html = html[:at] + "// v12.45: 흐름도 칸 단축키 → '단축키 한 곳'(PC_KEYS, 방향키 이동 아래)\n" + html[at:]

# 2-c) 방향키 이동(문서 버블) 자리에 '단축키 한 곳'
C_head = "document.addEventListener('keydown',e=>{\n if(!/^Arrow(Left|Right|Up|Down)$/.test(e.key)||e.defaultPrevented"
seg, at = cut(C_head, "\n clearTimeout(NUDGE.timer);NUDGE.timer=setTimeout(nudgeCommit,400);\n});\n")
C_body = seg[len("document.addEventListener('keydown',e=>{\n"):-len("});\n")]
KEYS = r"""// ══════ v12.45 · 단축키 한 곳 ══════════════════════════════════════════════
// 편집기 키보드 동작은 여기서 연결. 처리 순서(먼저 → 나중):
//  [창 캡처]        사용법 안내 키(guideKeys) · Shift 미리보기 · 방향키 묶음 마감(nudgeCommit) · geoFlush  ← 관찰만
//  [문서 캡처]      ① pcKeyFlow 흐름도 칸 → 찾기 칸 · 글씨색 창 · 칸색 창 · 음량 창(각 창이 스스로 처리)
//  [#stageHost 캡처] 표 셀 Enter·F2·Esc·Tab (installStageTableEvents)
//  [문서 버블]      ② pcKeyNudge 방향키 이동 → ③ pcKeyEditor 편집기·발표 단축키
//  붙여넣기: Ctrl+V 키 → 표·그래프 하나 선택이면 paste 이벤트(pcGridPasteTarget 쪽)로 넘김, 아니면 개체 붙여넣기
// 같은 목록 안 처리기는 따로 등록했을 때처럼 모두 실행(오류도 서로 안 막음), stopImmediatePropagation이면 거기서 멈춤.
function pcKeyFlow(e){
__B__}
function pcKeyNudge(e){
__C__}
function pcKeyEditor(e){
__A__}
const PC_KEYMAP=Object.freeze([
 {keys:'Ctrl+S',when:'언제나(글 편집 중 포함)',does:'HTML로 저장',where:'pcKeyEditor'},
 {keys:'Ctrl+C / Ctrl+V',when:'개체 선택',does:'복사 / 마우스 위치에 붙여넣기 (표·그래프 선택 중이면 엑셀·시트 칸 붙여넣기)',where:'pcKeyEditor · paste 이벤트'},
 {keys:'Ctrl+Z / Ctrl+Y·Ctrl+Shift+Z',when:'편집 화면',does:'되돌리기 / 다시 하기',where:'pcKeyEditor'},
 {keys:'Ctrl+D',when:'개체 선택',does:'복제',where:'pcKeyEditor'},
 {keys:'Delete·Backspace',when:'개체 선택',does:'삭제',where:'pcKeyEditor'},
 {keys:'방향키 (Shift: 10px)',when:'개체 선택',does:'1px 이동, 잠긴 개체는 안내만',where:'pcKeyNudge'},
 {keys:'Esc',when:'편집 화면',does:'지우개 그리기 → 지우개 끄기 → 기호 창 → 배치 취소 → 글 편집 끝 → 메뉴 닫기 (앞에서부터 하나만)',where:'pcKeyEditor'},
 {keys:'Ctrl+Enter',when:'글 편집 중',does:'편집 마침',where:'pcKeyEditor'},
 {keys:'Delete / Esc / Enter·F2',when:'흐름도 칸 선택',does:'칸 삭제 / 칸 선택 해제 / 칸 글 편집',where:'pcKeyFlow'},
 {keys:'Enter·F2 / Esc / Tab·Shift+Tab',when:'표 셀',does:'셀 편집 / 취소 / 다음·이전 셀',where:'installStageTableEvents'},
 {keys:'→ / ← / ↑ / ↓·1~9 / 0',when:'발표',does:'다음 / 이전 / 위 단계 / 하위 상자 / 처음',where:'pcKeyEditor'},
 {keys:'Esc',when:'발표',does:'음량 창 닫기, 없으면 발표 끝',where:'pcKeyEditor'}
]);
const PC_KEYS=Object.freeze({capture:[['흐름도 칸',pcKeyFlow]],bubble:[['방향키 이동',pcKeyNudge],['편집기 단축키',pcKeyEditor]]});
function pcKeyRun(list,e){
 let halted=false;const stop=e.stopImmediatePropagation;e.stopImmediatePropagation=function(){halted=true;return stop.call(this);};
 for(const [,fn] of list){if(halted)break;try{fn(e);}catch(err){setTimeout(()=>{throw err;});}}
}
document.addEventListener('keydown',e=>pcKeyRun(PC_KEYS.capture,e),true);
document.addEventListener('keydown',e=>pcKeyRun(PC_KEYS.bubble,e));
// ═══════════════════════════════════════════════════════════════════════════
"""
KEYS = KEYS.replace('__B__', B_body).replace('__C__', C_body).replace('__A__', A_body)
html = html[:at] + KEYS + html[at:]
R("window.Revival={tableCellSelection:", "window.Revival={keymap:()=>PC_KEYMAP.map(x=>({...x})),keyHandlers:()=>({capture:PC_KEYS.capture.map(x=>x[0]),bubble:PC_KEYS.bubble.map(x=>x[0])}),tableCellSelection:")

# ── 1) CSS 한 곳 ────────────────────────────────────────────────
KEEP = {'rv-startup-no-editor-flash', 'pc-step3-00_embedded-fonts', 'rv-v12220-fonts'}
blocks = css45.real_style_blocks(html)
merge = [b for b in blocks if b['id'] not in KEEP]
assert len(blocks) == 40 and len(merge) == 37, (len(blocks), len(merge))
merged = ''.join(f"\n/* ══════ 원래 블록: {b['id'] or '(이름 없음)'} ══════ */\n" + b['css'].strip('\n') + '\n' for b in merge)
valid = json.load(open(vpath))
cleaned, ndead = css45.apply(merged, valid)
assert ndead == 233, ndead
head = ('\n/* PageCraft v12.45 · 화면 CSS 한 곳.\n'
        ' * v12.17~v12.44 패치 블록 37개를 원래 순서 그대로 합침(적용 우선순위 동일). 구역마다 원래 블록 이름 표시.\n'
        ' * 같은 선택자·같은 속성에서 뒤 선언에 완전히 덮여 적용되지 않던 선언 233개 제거.\n'
        ' * 새 수정은 맨 아래에 덧붙이지 말고 해당 구역의 규칙을 직접 고칠 것(!important 덧칠 금지). */')
tag = '<style id="pc-ui-css">' + head + cleaned + '</style>'
for b in reversed(merge):
    html = html[:b['start']] + (tag if b is merge[0] else '') + html[b['end']:]

# ── 버전
R("const BUILD_VERSION='PageCraft v12.44.0 · 레일·구분선 테마색, 원 유지';", "const BUILD_VERSION='PageCraft v12.45.0 · 코드 정리(CSS·단축키 한 곳)';")
R('<title>페이지공방 v12.44.0 · 레일·구분선 테마색, 원 유지</title>', '<title>페이지공방 v12.45.0 · 코드 정리(CSS·단축키 한 곳)</title>')
open(out, 'w', encoding='utf-8').write(html); print('patched', out, len(html))
