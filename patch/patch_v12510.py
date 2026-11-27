"""PageCraft v12.51.0 — CSS 우선순위 정리 2
기준: v12.50.0 Lite.
 1) !important 정리 2차: @media 없는 구역 4묶음(rv-lock-state-visual-v12171 · rv-v12176~12179 · rv-v12260-themes · rv-v12330~12340)
    원문 206개 중 62개 뺌 — tools/imp_check.js로 1500x950·1024x600 두 화면에서 하나씩·함께 빼도 계산된 스타일 그대로인 것만.
    남긴 것: 다른 구역 !important와 겨루는 것(NEED·COMBO-BAD), 시험 상태에서 안 쓰이는 것(UNMATCHED), :hover 등 상태 선택자, 테마 지정 선택자
    마지막에 cssdump quick으로 옛/새 판 전체 비교
Usage: python3 -I patch/patch_v12510.py <PageCraft_v12.50.0_Lite.html> <out.html>"""
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
assert "BUILD_VERSION='PageCraft v12.50.0 · 배율 화면·겹침 이름·CSS 우선순위 정리'" in html, 'needs v12.50.0'
assert 'pc-v12510' not in html, 'already patched'

# ── 1) 변경 ──────────────────────────────────────────────
# CSS는 <style id="pc-ui-css"> 안 해당 구역 규칙을 직접 R()로 고칠 것. 맨 아래 덧붙이기·!important 덧칠 금지.
# 새 JS에는 주석 /*pc-v12510*/ 를 넣어 '이미 적용' 검사가 작동하게 할 것.
# 1) !important 정리 2차. 줄 단위로 바꿔 무엇이 빠졌는지 보이게 (구역 이름은 주석)
for _old, _new in [
  # rv-lock-state-visual-v12171
  ('#quickBar [data-action="locked"]{display:inline-flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:3px!important;min-width:74px!important;border-radius:7px!important;cursor:pointer!important;transition:background-color .12s,border-color .12s!important}',
   '#quickBar [data-action="locked"]{display:inline-flex;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:3px!important;min-width:74px!important;border-radius:7px!important;cursor:pointer!important;transition:background-color .12s,border-color .12s!important}'),
  ('#quickBar [data-action="locked"] .rv-quick-symbol{height:22px!important;display:grid!important;place-items:center!important}',
   '#quickBar [data-action="locked"] .rv-quick-symbol{height:22px;display:grid;place-items:center}'),
  ('#quickBar [data-action="locked"] .rv-quick-symbol .rv-lock-vector{height:21px!important;width:21px!important;display:block!important}',
   '#quickBar [data-action="locked"] .rv-quick-symbol .rv-lock-vector{height:21px;width:21px;display:block}'),
  ('#quickBar [data-action="locked"] small{font-size:10px!important;font-weight:800!important;line-height:1.2!important;white-space:nowrap!important}',
   '#quickBar [data-action="locked"] small{font-size:10px!important;font-weight:800!important;line-height:1.2!important;white-space:nowrap}'),
  # rv-v12176-patches
  ('#stageHost .rv-object.rv-selected:not(.rv-locked){outline:2px solid #2186C7!important;outline-offset:0;}',
   '#stageHost .rv-object.rv-selected:not(.rv-locked){outline:2px solid #2186C7;outline-offset:0;}'),
  ('#stageHost .rv-object.rv-selected.rv-locked{outline:2px dashed #DB8B32!important;outline-offset:0;}',
   '#stageHost .rv-object.rv-selected.rv-locked{outline:2px dashed #DB8B32;outline-offset:0;}'),
  ('.ribbon .text-swatches .auto-swatch,.quick-bar .auto-swatch{color:#132C45!important;background:#F2F6FB!important;border:1px solid #8CA6BD!important;}',
   '.ribbon .text-swatches .auto-swatch,.quick-bar .auto-swatch{color:#132C45;background:#F2F6FB;border:1px solid #8CA6BD!important;}'),
  ('.ribbon .text-swatches .auto-swatch small,.quick-bar .auto-swatch small{color:#132C45!important;font-weight:800!important;font-size:10px!important;}',
   '.ribbon .text-swatches .auto-swatch small,.quick-bar .auto-swatch small{color:#132C45;font-weight:800;font-size:10px;}'),
  ('.quick-bar .quick-underline{padding-inline:8px!important;min-width:34px;}',
   '.quick-bar .quick-underline{padding-inline:8px;min-width:34px;}'),
  ('.page-actions button{color:#344A60!important;opacity:1!important;font-weight:740!important;}',
   '.page-actions button{color:#344A60;opacity:1;font-weight:740!important;}'),
  ('.page-actions button[data-action="pageClone"]{color:#275B85!important;}',
   '.page-actions button[data-action="pageClone"]{color:#275B85;}'),
  ('.page-actions button[data-action="pageDelete"]{color:#B5323F!important;border-color:#E7C5C9!important;}',
   '.page-actions button[data-action="pageDelete"]{color:#B5323F;border-color:#E7C5C9;}'),
  # rv-v12177-fixes
  ('.rv-cycle-step>.rv-text-content{display:flex;align-items:center;justify-content:center;text-align:center;padding:17% 15%!important;line-height:1.2;}',
   '.rv-cycle-step>.rv-text-content{display:flex;align-items:center;justify-content:center;text-align:center;padding:17% 15%;line-height:1.2;}'),
  ('.close-x,button[data-gradient-close],button[data-action="chartDeleteSeries"],button[data-action="chartDeletePoint"]{display:inline-flex!important;align-items:center!important;justify-content:center!important;padding:0!important;line-height:1!important;flex-shrink:0;vertical-align:middle;}',
   '.close-x,button[data-gradient-close],button[data-action="chartDeleteSeries"],button[data-action="chartDeletePoint"]{display:inline-flex!important;align-items:center;justify-content:center;padding:0;line-height:1;flex-shrink:0;vertical-align:middle;}'),
  # rv-v12178-corners
  ('.rv-card-top-band.rv-corner-accent-surface{background:transparent!important;border:0!important;border-radius:0!important;box-shadow:none!important;}',
   '.rv-card-top-band.rv-corner-accent-surface{background:transparent;border:0;border-radius:0;box-shadow:none;}'),
  # rv-v12179-controls
  ('.rv-gradient-icon{display:inline-block!important;width:20px!important;height:20px!important;min-width:20px;flex:none;border:1px solid #9AA9BD;border-radius:4px;background:linear-gradient(120deg,#25487C 0%,#92C5EE 54%,#FFF1D4 100%);box-shadow:0 1px 2px #17304C26;vertical-align:middle;}',
   '.rv-gradient-icon{display:inline-block;width:20px;height:20px;min-width:20px;flex:none;border:1px solid #9AA9BD;border-radius:4px;background:linear-gradient(120deg,#25487C 0%,#92C5EE 54%,#FFF1D4 100%);box-shadow:0 1px 2px #17304C26;vertical-align:middle;}'),
  ('.ribbon .rv-color-scope input[type=color]{width:27px!important;height:25px!important;padding:1px;border:1px solid #B5C7D8!important;border-radius:4px;box-shadow:none;}',
   '.ribbon .rv-color-scope input[type=color]{width:27px;height:25px;padding:1px;border:1px solid #B5C7D8;border-radius:4px;box-shadow:none;}'),
  ('.page-actions button[data-action="pageDelete"]{min-width:40px!important;font-size:11px!important;font-weight:750;}',
   '.page-actions button[data-action="pageDelete"]{min-width:40px;font-size:11px;font-weight:750;}'),
  ('.rv-table .rv-data-table{border-radius:0!important;box-shadow:none!important;}',
   '.rv-table .rv-data-table{border-radius:0;box-shadow:none;}'),
  ('#quickBar .quick-payload button.quick-underline{display:grid!important;grid-template-rows:22px 12px!important;justify-items:center!important;align-content:center!important;gap:5px!important;min-height:49px!important;text-decoration:none!important;line-height:1!important;}',
   '#quickBar .quick-payload button.quick-underline{display:grid!important;grid-template-rows:22px 12px;justify-items:center;align-content:center;gap:5px!important;min-height:49px;text-decoration:none!important;line-height:1!important;}'),
  ('#quickBar .quick-underline .rv-quick-symbol{display:block!important;width:22px!important;height:22px!important;line-height:1!important;text-decoration:none!important;}',
   '#quickBar .quick-underline .rv-quick-symbol{display:block;width:22px;height:22px;line-height:1!important;text-decoration:none;}'),
  ('#quickBar .quick-underline small{display:block!important;margin:0!important;line-height:12px!important;text-decoration:none!important;}',
   '#quickBar .quick-underline small{display:block;margin:0;line-height:12px!important;text-decoration:none;}'),
  # rv-v12260-themes
  ('#templateDialog .modal-head p{color:#3F5368!important;font-size:13px!important}',
   '#templateDialog .modal-head p{color:#3F5368;font-size:13px}'),
  ('#templateDialog .eyebrow{color:#28557F!important;font-size:12px!important}',
   '#templateDialog .eyebrow{color:#28557F;font-size:12px}'),
  ('#templateDialog .template-number{color:#3E5165!important;font-size:12px!important}',
   '#templateDialog .template-number{color:#3E5165;font-size:12px}'),
  # rv-v12330
  ('#quickBar .pc-step-remove{min-width:34px;padding:0 10px!important;font-size:16px!important}',
   '#quickBar .pc-step-remove{min-width:34px;padding:0 10px;font-size:16px}'),
  # rv-v12340
  ('.rv-stage .rv-media-placeholder{display:flex!important;flex-direction:column;align-items:center;justify-content:center;gap:.55em;line-height:1.3!important;\n font-size:clamp(12px,min(4.2cqw,7.5cqh),30px)!important;white-space:normal!important;padding:.6em;box-sizing:border-box;text-align:center}',
   '.rv-stage .rv-media-placeholder{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.55em;line-height:1.3;\n font-size:clamp(12px,min(4.2cqw,7.5cqh),30px)!important;white-space:normal;padding:.6em;box-sizing:border-box;text-align:center}'),
]:
    R(_old, _new)

# ── 버전 문자열(BUILD_VERSION·하단 서명. <title>은 v12.46부터 문서 제목이라 안 건드림) ──
R("const BUILD_VERSION='PageCraft v12.50.0 · 배율 화면·겹침 이름·CSS 우선순위 정리';", "const BUILD_VERSION='PageCraft v12.51.0 · CSS 우선순위 정리 2';")
R('Jungmin Jo · PageCraft v12.50.0</span>', 'Jungmin Jo · PageCraft v12.51.0</span>')
open(out, 'w', encoding='utf-8').write(html); print('patched', out, len(html))
