"""PageCraft v12.51.0 — CSS 우선순위 정리 2
기준: v12.50.0 Lite.
 1) (할 일 적기)
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

# ── 버전 문자열(BUILD_VERSION·하단 서명. <title>은 v12.46부터 문서 제목이라 안 건드림) ──
R("const BUILD_VERSION='PageCraft v12.50.0 · 배율 화면·겹침 이름·CSS 우선순위 정리';", "const BUILD_VERSION='PageCraft v12.51.0 · CSS 우선순위 정리 2';")
R('Jungmin Jo · PageCraft v12.50.0</span>', 'Jungmin Jo · PageCraft v12.51.0</span>')
open(out, 'w', encoding='utf-8').write(html); print('patched', out, len(html))
