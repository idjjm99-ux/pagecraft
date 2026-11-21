"""새 패치 뼈대 만들기.
usage: python3 -I tools/new_patch.py <기준 Lite.html> <새 버전 예: 12.46.0> "<한 줄 요약>"
→ patch/patch_v12460.py 생성(기준 버전 검사·이미 적용 검사·R/cut 도우미·버전 문자열 3곳 갱신)
→ README.md 끝에 사용법 한 줄 추가
"""
import sys, os, re
base, ver, title = sys.argv[1], sys.argv[2], sys.argv[3]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(base, encoding='utf-8').read()
m = re.search(r"const BUILD_VERSION='(PageCraft v(\d+\.\d+\.\d+) · [^']*)';", html)
assert m, 'BUILD_VERSION 없음'
old_full, old_ver = m.group(1), m.group(2)
assert re.fullmatch(r'\d+\.\d+\.\d+', ver), '버전 형식: 12.46.0'
tag = ver.replace('.', '')
dst = os.path.join(root, 'patch', f'patch_v{tag}.py')
assert not os.path.exists(dst), f'이미 있음: {dst}'
old_title = re.search(r'<title>([^<]*)</title>', html).group(1)
sig = re.search(r'Jungmin Jo · PageCraft v[\d.]+</span>', html).group(0)
marker = f'pc-v{tag}'
code = f'''"""PageCraft v{ver} — {title}
기준: v{old_ver} Lite.
 1) (할 일 적기)
Usage: python3 -I patch_v{tag}.py <PageCraft_v{old_ver}_Lite.html> <out.html>"""
import sys
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
def R(old, new, n=1):
    global html
    c = html.count(old); assert c == n, f'expected {{n}} got {{c}}: {{old[:80]!r}}'
    html = html.replace(old, new)
def cut(a, b):
    """a로 시작해 b로 끝나는 유일한 구간을 잘라 돌려줌(제거)"""
    global html
    assert html.count(a) == 1, ('start', a[:60]); i = html.index(a)
    j = html.index(b, i) + len(b); seg = html[i:j]; html = html[:i] + html[j:]; return seg, i
assert {("BUILD_VERSION=" + repr(old_full))!r} in html, 'needs v{old_ver}'
assert {marker!r} not in html, 'already patched'

# ── 1) 변경 ──────────────────────────────────────────────
# CSS는 <style id="pc-ui-css"> 안 해당 구역 규칙을 직접 R()로 고칠 것. 맨 아래 덧붙이기·!important 덧칠 금지.
# 새 JS를 넣을 땐 주석 /*{marker}*/ 를 함께 넣어 '이미 적용' 검사가 작동하게 할 것.

# ── 버전 문자열 ──────────────────────────────────────────
R({("const BUILD_VERSION=" + repr(old_full) + ";")!r}, {("const BUILD_VERSION=" + repr(f"PageCraft v{ver} · {title}") + ";")!r})
R({f"<title>{old_title}</title>"!r}, {f"<title>페이지공방 v{ver} · {title}</title>"!r})
R({sig!r}, {f"Jungmin Jo · PageCraft v{ver}</span>"!r})
open(out, 'w', encoding='utf-8').write(html); print('patched', out, len(html))
'''
open(dst, 'w', encoding='utf-8').write(code)
with open(os.path.join(root, 'README.md'), 'a', encoding='utf-8') as f:
    f.write(f'- v{ver}: python3 -I patch/patch_v{tag}.py PageCraft_v{old_ver}_Lite.html PageCraft_v{ver}_Lite.html ({title}). 시험 tests/t_v{tag[2:4] if len(tag)==5 else tag}.py\n')
print(dst)
