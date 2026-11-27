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
const sel1 = async (pp) => { await pp.evaluate(() => { const pg = Revival.getProject().pages[0]; Revival.go(pg.id); Revival.selectOne(pg.objects.find(o => !o.unplaced).id); }); await pp.waitForTimeout(400); };
(async () => {
  const { b, p } = await open(file);
  { const r = await pcVer(p, file); ok(r.okV, '버전 = 파일 이름 v' + r.v, r.bv); ok(r.okSig, '서명 버전', r.sig); }
  // ── 1) !important 정리 2차: 개수와 대표 스타일(빼기 전과 같은 값) ──
  const n = await p.evaluate(() => document.getElementById('pc-ui-css').textContent.split('!important').length - 1);
  ok(n <= 909, 'pc-ui-css !important 971→909 이하', n);
  const cs = (sel, props) => p.evaluate(([sel, props]) => { const e = document.querySelector(sel); if (!e) return null; const c = getComputedStyle(e); return props.map(k => c.getPropertyValue(k)); }, [sel, props]);
  await sel1(p);
  { const v = await cs('#quickBar [data-action="locked"]', ['display', 'flex-direction']); ok(v && v[0] === 'flex' && v[1] === 'column', '잠금 단추 세로 배치(v12.50과 같음)', JSON.stringify(v)); }
  { const v = await cs('#quickBar [data-action="locked"] .rv-quick-symbol', ['height', 'display']); ok(v && v[0] === '23px' && v[1] === 'grid', '잠금 아이콘 칸 23px(v12.50과 같음)', JSON.stringify(v)); }
  // 선택 테두리(잠김/안 잠김)
  { const v = await p.evaluate(() => { const e = document.querySelector('#stageHost .rv-object.rv-selected'); if (!e) return null; const c = getComputedStyle(e); return [c.outlineStyle, c.outlineWidth, c.outlineColor, e.classList.contains('rv-locked')]; });
    ok(v && v[1] === '2px' && (v[3] ? v[0] === 'dashed' && v[2] === 'rgb(219, 139, 50)' : v[0] === 'solid' && v[2] === 'rgb(33, 134, 199)'), '선택 테두리', JSON.stringify(v)); }
  await p.keyboard.press('Escape'); await p.click('[data-action=addPage]'); await p.waitForTimeout(800);
  { const v = await cs('#templateDialog .template-number', ['color', 'font-size']); ok(v && v[0] === 'rgb(62, 81, 101)' && v[1] === '12px', '양식 번호 글씨', JSON.stringify(v)); }
  { const v = await cs('#templateDialog .modal-head p', ['color', 'font-size']); ok(v && v[0] === 'rgb(63, 83, 104)' && v[1] === '13px', '양식 창 설명 글씨', JSON.stringify(v)); }
  // 좁고 낮은 화면에서도 같은 값
  { const o = await open(file, { width: 1024, height: 600 }); await sel1(o.p); const v = await o.p.evaluate(() => { const c = getComputedStyle(document.querySelector('#quickBar [data-action="locked"] .rv-quick-symbol')); return [c.height, c.display]; });
    ok(v[0] === '23px' && v[1] === 'grid', '1024x600 잠금 아이콘 칸', JSON.stringify(v)); ok(!o.p.errs.length, '1024x600 오류 없음', JSON.stringify(o.p.errs)); await o.b.close(); }
  ok(!p.errs.length, '오류 없음', JSON.stringify(p.errs));
  await b.close();
  console.log(`== ${pass}/${pass + fail} 통과`); process.exit(fail ? 1 : 0);
})().catch(e => { console.log('FAIL 예외 ' + e.message); console.log(`== ${pass}/${pass + fail + 1} 통과`); process.exit(1); });
