// v12.51.0 시험(노드 Playwright): node tests/t_v51.js <PageCraft_v12.51.0_Lite.html>
// CSS 우선순위 정리 2
const { chromium } = require('playwright'); const path = require('path');
let pass = 0, fail = 0;
const ok = (c, m, x = '') => { c ? pass++ : fail++; console.log((c ? 'PASS ' : 'FAIL ') + m + ' ' + (x || '')); };
const file = path.resolve(process.argv[2]);
async function open(f, vp = { width: 1500, height: 950 }) {
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: vp, acceptDownloads: true });
  await ctx.grantPermissions(['clipboard-read', 'clipboard-write']);
  const p = await ctx.newPage(); p.errs = []; p.on('pageerror', e => p.errs.push(e.message)); p.on('dialog', d => d.accept());
  await p.goto('file://' + f); await p.waitForTimeout(1500);
  await p.locator('#presentation button', { hasText: '편집' }).first().click(); await p.waitForTimeout(1200);
  await p.addStyleTag({ content: '.rv-guide{display:none!important;pointer-events:none!important}' });
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  return { b, ctx, p };
}
// 버전: 파일 이름의 버전(없으면 앱 자신)과 BUILD_VERSION·서명이 같은지
const pcVer = async (p, file) => { const bv = await p.evaluate(() => Revival.buildVersion()), v = (path.basename(file).match(/v(\d+\.\d+\.\d+)/) || [])[1] || (bv.match(/v(\d+\.\d+\.\d+)/) || [])[1], sig = await p.locator('#rv-app-signature').textContent(); return { v, bv, sig, okV: bv.startsWith('PageCraft v' + v), okSig: sig.includes('v' + v) }; };
(async () => {
  const { b, p } = await open(file);
  { const r = await pcVer(p, file); ok(r.okV, '버전 = 파일 이름 v' + r.v, r.bv); ok(r.okSig, '서명 버전', r.sig); }
  // ── 1) (시험 적기) ──
  ok(!p.errs.length, '오류 없음', JSON.stringify(p.errs));
  await b.close();
  console.log(`== ${pass}/${pass + fail} 통과`); process.exit(fail ? 1 : 0);
})().catch(e => { console.log('FAIL 예외 ' + e.message); console.log(`== ${pass}/${pass + fail + 1} 통과`); process.exit(1); });
