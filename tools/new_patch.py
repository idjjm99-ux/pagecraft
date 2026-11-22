"""새 패치 뼈대 만들기.
usage: python3 -I tools/new_patch.py <기준 Lite.html> <새 버전 예: 12.49.0> "<한 줄 요약>"
→ patch/patch_v12490.py (기준 버전 검사·이미 적용 검사·R/cut 도우미·버전 문자열 2곳)
→ tests/t_v49.js (열기 도우미·버전 검사·PASS/FAIL·마지막 '== n/m 통과')
→ docs/CHANGELOG.md 끝에 한 줄
"""
import sys, os, re
base, ver, title = sys.argv[1], sys.argv[2], sys.argv[3]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(base, encoding='utf-8').read()
m = re.search(r"const BUILD_VERSION='(PageCraft v(\d+\.\d+\.\d+) · [^']*)';", html)
assert m, 'BUILD_VERSION 없음'
old_full, old_ver = m.group(1), m.group(2)
assert re.fullmatch(r'\d+\.\d+\.\d+', ver), '버전 형식: 12.49.0'
tag = ver.replace('.', '')            # 12490
short = ver.split('.')[1]              # 49
dst = os.path.join(root, 'patch', f'patch_v{tag}.py')
tst = os.path.join(root, 'tests', f't_v{short}.js')
for f in (dst, tst): assert not os.path.exists(f), f'이미 있음: {f}'
sig = re.search(r'Jungmin Jo · PageCraft v[\d.]+</span>', html).group(0)
marker = f'pc-v{tag}'
new_full = f'PageCraft v{ver} · {title}'

code = f'''"""PageCraft v{ver} — {title}
기준: v{old_ver} Lite.
 1) (할 일 적기)
Usage: python3 -I patch/patch_v{tag}.py <PageCraft_v{old_ver}_Lite.html> <out.html>"""
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
# 새 JS에는 주석 /*{marker}*/ 를 넣어 '이미 적용' 검사가 작동하게 할 것.

# ── 버전 문자열(BUILD_VERSION·하단 서명. <title>은 v12.46부터 문서 제목이라 안 건드림) ──
R({("const BUILD_VERSION=" + repr(old_full) + ";")!r}, {("const BUILD_VERSION=" + repr(new_full) + ";")!r})
R({sig!r}, {f"Jungmin Jo · PageCraft v{ver}</span>"!r})
open(out, 'w', encoding='utf-8').write(html); print('patched', out, len(html))
'''

test = f'''// v{ver} 시험(노드 Playwright): node tests/t_v{short}.js <PageCraft_v{ver}_Lite.html>
// {title}
const {{ chromium }} = require('playwright'); const path = require('path');
let pass = 0, fail = 0;
const ok = (c, m, x = '') => {{ c ? pass++ : fail++; console.log((c ? 'PASS ' : 'FAIL ') + m + ' ' + (x || '')); }};
const file = path.resolve(process.argv[2]);
async function open(f, vp = {{ width: 1500, height: 950 }}) {{
  const b = await chromium.launch(); const ctx = await b.newContext({{ viewport: vp, acceptDownloads: true }});
  await ctx.grantPermissions(['clipboard-read', 'clipboard-write']);
  const p = await ctx.newPage(); p.errs = []; p.on('pageerror', e => p.errs.push(e.message)); p.on('dialog', d => d.accept());
  await p.goto('file://' + f); await p.waitForTimeout(1500);
  await p.locator('#presentation button', {{ hasText: '편집' }}).first().click(); await p.waitForTimeout(1200);
  await p.addStyleTag({{ content: '.rv-guide{{display:none!important;pointer-events:none!important}}' }});
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  return {{ b, ctx, p }};
}}
// 버전: 파일 이름의 버전(없으면 앱 자신)과 BUILD_VERSION·서명이 같은지
const pcVer = async (p, file) => {{ const bv = await p.evaluate(() => Revival.buildVersion()), v = (path.basename(file).match(/v(\\d+\\.\\d+\\.\\d+)/) || [])[1] || (bv.match(/v(\\d+\\.\\d+\\.\\d+)/) || [])[1], sig = await p.locator('#rv-app-signature').textContent(); return {{ v, bv, sig, okV: bv.startsWith('PageCraft v' + v), okSig: sig.includes('v' + v) }}; }};
(async () => {{
  const {{ b, p }} = await open(file);
  {{ const r = await pcVer(p, file); ok(r.okV, '버전 = 파일 이름 v' + r.v, r.bv); ok(r.okSig, '서명 버전', r.sig); }}
  // ── 1) (시험 적기) ──
  ok(!p.errs.length, '오류 없음', JSON.stringify(p.errs));
  await b.close();
  console.log(`== ${{pass}}/${{pass + fail}} 통과`); process.exit(fail ? 1 : 0);
}})().catch(e => {{ console.log('FAIL 예외 ' + e.message); console.log(`== ${{pass}}/${{pass + fail + 1}} 통과`); process.exit(1); }});
'''
open(dst, 'w', encoding='utf-8').write(code)
open(tst, 'w', encoding='utf-8').write(test)
with open(os.path.join(root, 'docs', 'CHANGELOG.md'), 'a', encoding='utf-8') as f:
    f.write(f'- v{ver}: python3 -I patch/patch_v{tag}.py PageCraft_v{old_ver}_Lite.html PageCraft_v{ver}_Lite.html ({title}). 시험 node tests/t_v{short}.js\n')
print(dst); print(tst)
