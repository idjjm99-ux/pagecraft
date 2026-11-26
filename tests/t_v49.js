// v12.49.0 시험(노드 Playwright): node tests/t_v49.js <PageCraft_v12.49.0_Lite.html>
// 좁은 화면 잘림(머리줄·설정 탭·글꼴 적용 단추·겹침 목록)
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
  ok(!p.errs.length, '오류 없음(1500)', JSON.stringify(p.errs));
  await b.close();
  // 폭마다: 머리줄 단추·상세 설정 탭 글씨·글꼴 적용 단추·겹침 목록이 칸 안에 들어오는지
  const inside = (r, o, t = 1) => r.left >= o.left - t && r.right <= o.right + t;
  for (const w of [1024, 1100, 1101, 1150, 1240, 1280, 1350, 1366, 1920]) {
    const { b, p } = await open(file, { width: w, height: 768 });
    const tab = async t => { await p.click(`#inspectorTabs [data-inspector-tab=${t}]`); await p.waitForTimeout(300); };
    const R = (sel, all = false) => p.evaluate(([s, a]) => { const f = e => { const r = e.getBoundingClientRect(); return { left: r.left, right: r.right, width: r.width, sw: e.scrollWidth, cw: e.clientWidth }; }; return a ? [...document.querySelectorAll(s)].filter(e => e.offsetParent).map(f) : (document.querySelector(s) ? f(document.querySelector(s)) : null); }, [sel, all]);
    // 머리줄: 저장 상태 글씨가 긴 상태(잠긴 개체 고름)에서도 단추가 화면 안
    await p.locator('#stageHost .rv-object').first().click({ force: true }); await p.waitForTimeout(300);
    const hb = await R('.header-actions > *', true);
    ok(hb.length && hb.every(r => r.right <= w + 1), `${w}: 머리줄 단추 화면 안`, hb.length ? Math.round(Math.max(...hb.map(r => r.right))) + '/' + w : '');
    // 탭 작은 글씨가 탭 안
    const tabs = await R('#inspectorTabs [data-inspector-tab]', true), smalls = await R('#inspectorTabs [data-inspector-tab] small', true);
    ok(tabs.length === 3 && smalls.every((s, i) => inside(s, tabs[i])), `${w}: 탭 작은 글씨가 탭 안`, smalls.map((s, i) => Math.round(s.right - tabs[i].right)).join(','));
    // 페이지 설정: 글꼴 적용 단추 2개가 설정 칸 안
    await tab('page');
    const ins = await R('#inspector'), fb = await R('.scope-fonts > .inspect-button', true);
    ok(fb.length >= 2 && fb.every(r => inside(r, ins)), `${w}: [페이지에 적용]·[문서 전체 적용] 칸 안`, fb.map(r => Math.round(r.right - ins.right)).join(','));
    // 겹침·순서: 이름·종류·겹침 표가 이름 단추 안, 이름 칸 넓이 충분
    await tab('layers');
    const rows = await p.evaluate(() => [...document.querySelectorAll('.rv-layer-row')].filter(e => e.offsetParent).map(row => { const n = row.querySelector('.rv-layer-name'), nr = n.getBoundingClientRect(), g = s => { const e = n.querySelector(s); const r = e.getBoundingClientRect(); return { left: r.left, right: r.right, top: r.top, width: r.width }; }; return { btn: { left: nr.left, right: nr.right }, name: g('span:not(.rv-layer-type)'), type: g('.rv-layer-type'), count: g('.rv-overlap-count'), rowR: row.getBoundingClientRect().right, actR: Math.max(...[...row.querySelectorAll('[data-layer-action]')].map(x => x.getBoundingClientRect().right)) }; }));
    ok(rows.length >= 1, `${w}: 겹침 목록 줄 있음`, rows.length);
    ok(rows.every(r => inside(r.type, r.btn) && inside(r.count, r.btn) && inside(r.name, r.btn)), `${w}: 종류·이름·겹침 표가 칸 안`);
    ok(rows.every(r => r.name.width >= 60), `${w}: 이름 칸 넓이 60px 이상`, rows.map(r => Math.round(r.name.width)).join(','));
    ok(rows.every(r => r.count.top > r.name.top + 4), `${w}: 겹침 표는 이름 아래 줄`);
    ok(rows.every(r => r.actR <= r.rowR + 1), `${w}: ↑↓·잠금 단추 줄 안`);
    ok(!p.errs.length, `${w}: 오류 없음`, JSON.stringify(p.errs));
    await b.close();
  }
  // 겹침 목록 동작 그대로: 이름 누르면 고름, ↑/↓로 순서 바뀜, Ctrl+Z
  { const { b, p } = await open(file, { width: 1024, height: 768 });
    await p.click('#inspectorTabs [data-inspector-tab=layers]'); await p.waitForTimeout(300);
    const id = await p.locator('.rv-layer-row').first().getAttribute('data-layer-id');
    await p.locator('.rv-layer-row .rv-layer-name').first().click(); await p.waitForTimeout(250);
    ok(await p.locator(`.rv-layer-row[data-layer-id="${id}"].is-selected`).count() === 1, '1024: 이름 누르면 그 개체 고름');
    const zOf = () => p.evaluate(i => document.querySelector(`#stageHost .rv-object[data-object-id="${i}"]`)?.style.zIndex, id);
    const z0 = await zOf(); const btn = p.locator(`.rv-layer-row[data-layer-id="${id}"] [data-layer-action]:not([disabled])`).first();
    if (await btn.count()) { await btn.click(); await p.waitForTimeout(300); const z1 = await zOf(); ok(z1 !== z0, '1024: ↑/↓ 누르면 순서 바뀜', z0 + '→' + z1);
      await p.keyboard.press('Control+z'); await p.waitForTimeout(300); ok(await zOf() === z0, '1024: Ctrl+Z로 되돌림'); }
    else ok(false, '1024: 누를 수 있는 ↑/↓ 단추');
    ok(!p.errs.length, '1024 동작: 오류 없음', JSON.stringify(p.errs)); await b.close(); }
  console.log(`== ${pass}/${pass + fail} 통과`); process.exit(fail ? 1 : 0);
})().catch(e => { console.log('FAIL 예외 ' + e.message); console.log(`== ${pass}/${pass + fail + 1} 통과`); process.exit(1); });
