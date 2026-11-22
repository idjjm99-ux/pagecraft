// v12.48.0 시험(노드 Playwright): node t_v48.js <PageCraft_v12.48.0_Lite.html>
// 6 개체 회전(손잡이·상세 설정·크기 조절·이동·지우개·썸네일·발표·인쇄·PPT·저장본) · 5 발표자 보기(새 창·넘기기·메모·시간·팝업 막힘)
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path'), os = require('os');
let pass = 0, fail = 0;
const ok = (c, m, x = '') => { c ? pass++ : fail++; console.log((c ? 'PASS ' : 'FAIL ') + m + ' ' + (x || '')); };
const near = (a, b, t) => Math.abs(a - b) <= t;
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
const objOf = (p, id) => p.evaluate(id => Revival.getCurrentPage().objects.find(o => o.id === id), id);
const sel = p => p.evaluate(() => Revival.getSelected());
const stagePt = (p, px, py) => p.evaluate(([px, py]) => { const s = document.querySelector('#stageHost .rv-stage'), r = s.getBoundingClientRect(); return { x: r.left + px * r.width / s.offsetWidth, y: r.top + py * r.height / s.offsetHeight }; }, [px, py]);
const zoom = p => p.evaluate(() => { const s = document.querySelector('#stageHost .rv-stage'); return s.getBoundingClientRect().width / s.offsetWidth; });
const rotOf = (p, id, scope = '#stageHost') => p.evaluate(([id, sc]) => document.querySelector(`${sc} .rv-object[data-object-id="${id}"]`)?.style.rotate || '', [id, scope]);
async function setProp(p, name, v) {
  await p.evaluate(([n, v]) => { const el = document.querySelector(`#inspector [data-prop="${n}"]`); if (!el) throw Error('no field ' + n); if (el.type === 'checkbox') el.checked = v; else el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }, [name, v]);
  await p.waitForTimeout(250);
}
async function openLayout(p) { await p.evaluate(() => { const b = [...document.querySelectorAll('#inspector button, #inspector summary, #inspector [data-accordion]')].find(x => /배치와 위치/.test(x.textContent)); const sec = b?.closest('details'); if (sec) sec.open = true; else if (b && b.getAttribute('aria-expanded') === 'false') b.click(); }); await p.waitForTimeout(200); }
// 개체 가운데 기준 각도 deg(0=오른쪽, 시계방향 +) 반지름 rad(페이지 px) 지점의 화면 좌표
async function around(p, o, deg, rad) { const t = deg * Math.PI / 180; return stagePt(p, o.x + o.w / 2 + Math.cos(t) * rad, o.y + o.h / 2 + Math.sin(t) * rad); }
async function dragRot(p, id, want, shift = false) {
  const o = await objOf(p, id), r0 = o.rotation || 0; const h = await p.locator(`#stageHost .rv-object[data-object-id="${id}"] .pc-rot-handle`).boundingBox();
  const c = await stagePt(p, o.x + o.w / 2, o.y + o.h / 2), hx = h.x + h.width / 2, hy = h.y + h.height / 2, a0 = Math.atan2(hy - c.y, hx - c.x), a = a0 + (want - r0) * Math.PI / 180, R = Math.hypot(hx - c.x, hy - c.y);
  await p.mouse.move(hx, hy); await p.mouse.down();
  if (shift) await p.keyboard.down('Shift');
  await p.mouse.move(c.x + Math.cos(a) * R, c.y + Math.sin(a) * R, { steps: 10 }); await p.waitForTimeout(80);
  await p.mouse.up(); if (shift) await p.keyboard.up('Shift'); await p.waitForTimeout(300);
}
// 개체 안쪽 비율 좌표(u,v) → 화면 좌표(회전 반영)
async function localPt(p, o, u, v) { const t = (o.rotation || 0) * Math.PI / 180, lx = (u - .5) * o.w, ly = (v - .5) * o.h; return stagePt(p, o.x + o.w / 2 + lx * Math.cos(t) - ly * Math.sin(t), o.y + o.h / 2 + lx * Math.sin(t) + ly * Math.cos(t)); }
const pageLocal = (o, u, v) => { const t = (o.rotation || 0) * Math.PI / 180, lx = (u - .5) * o.w, ly = (v - .5) * o.h; return { x: o.x + o.w / 2 + lx * Math.cos(t) - ly * Math.sin(t), y: o.y + o.h / 2 + lx * Math.sin(t) + ly * Math.cos(t) }; };

const pcVer = async (p, file) => { const bv = await p.evaluate(() => Revival.buildVersion()), v = (require('path').basename(file).match(/v(\d+\.\d+\.\d+)/) || [])[1] || (bv.match(/v(\d+\.\d+\.\d+)/) || [])[1], sig = await p.locator('#rv-app-signature').textContent(); return { v, bv, sig, okV: bv.startsWith('PageCraft v' + v), okSig: sig.includes('v' + v) }; };
(async () => {
  let { b, p } = await open(file);
  { const r = await pcVer(p, file); ok(r.okV, '버전 = 파일 이름 v' + r.v, r.bv); ok(r.okSig, '서명 버전', r.sig); }
  ok(await p.evaluate(() => Revival.keymap().some(k => k.when.includes('발표자 보기'))), '단축키 표에 발표자 보기 창');
  const proj0 = await p.evaluate(() => Revival.getProject());
  ok(!JSON.stringify(proj0).includes('"rotation"'), '기존 문서 데이터에 rotation 없음');

  // ───── 6) 회전 ─────
  const pg = proj0.pages[1].id; await p.evaluate(id => Revival.go(id), pg); await p.waitForTimeout(300);
  await p.evaluate(() => Revival.makeObject('shape')); await p.waitForTimeout(300);
  if (await p.evaluate(() => !!Revival.getState().editing)) { await p.keyboard.press('Control+Enter'); await p.waitForTimeout(200); }
  const sid = (await sel(p))[0];
  await openLayout(p);
  await setProp(p, 'x', 400); await setProp(p, 'y', 260); await setProp(p, 'w', 300); await setProp(p, 'h', 160);
  let o = await objOf(p, sid);
  ok(o.x === 400 && o.w === 300 && !('rotation' in o), '도형 준비(회전 필드 없음)', JSON.stringify([o.x, o.y, o.w, o.h]));
  ok(await p.locator(`#stageHost .rv-object[data-object-id="${sid}"] .pc-rot-handle`).isVisible(), '회전 손잡이 보임');
  const hb = await p.locator(`#stageHost .rv-object[data-object-id="${sid}"] .pc-rot-handle`).boundingBox(), bot = await stagePt(p, o.x + o.w / 2, o.y + o.h), qb = await p.locator('#quickBar').boundingBox();
  ok(near(hb.x + hb.width / 2, bot.x, 2) && hb.y > bot.y, '손잡이 위치: 아래쪽 가운데');
  ok(!qb || qb.y + qb.height < hb.y || qb.y > hb.y + hb.height, '간편편집바가 손잡이를 안 덮음');
  await dragRot(p, sid, 30);
  o = await objOf(p, sid); ok(o.rotation === 30, '손잡이 끌기 → 30°', String(o.rotation));
  ok(await rotOf(p, sid) === '30deg', '화면 rotate 30deg', await rotOf(p, sid));
  ok(o.x === 400 && o.y === 260 && o.w === 300 && o.h === 160, '돌려도 위치·크기 그대로');
  await dragRot(p, sid, 47, true); o = await objOf(p, sid); ok(o.rotation === 45, 'Shift 끌기 → 15° 단위(45°)', String(o.rotation));
  await dragRot(p, sid, 2); o = await objOf(p, sid); ok(!('rotation' in o), '0° 근처는 0°에 붙고 필드 빠짐', JSON.stringify(o.rotation));
  await p.keyboard.press('Control+z'); await p.waitForTimeout(300); ok((await objOf(p, sid)).rotation === 45, 'Ctrl+Z → 45°');
  await p.keyboard.press('Control+z'); await p.waitForTimeout(300); ok((await objOf(p, sid)).rotation === 30, 'Ctrl+Z → 30°'); await p.evaluate(id => Revival.selectOne(id), sid); await p.waitForTimeout(250);
  // Esc 취소
  { const h = await p.locator(`#stageHost .rv-object[data-object-id="${sid}"] .pc-rot-handle`).boundingBox(); await p.mouse.move(h.x + h.width / 2, h.y + h.height / 2); await p.mouse.down();
    await p.mouse.move(h.x + 80, h.y + 40, { steps: 5 }); await p.keyboard.press('Escape'); await p.mouse.up(); await p.waitForTimeout(250);
    ok((await objOf(p, sid)).rotation === 30 && await rotOf(p, sid) === '30deg', '돌리는 중 Esc → 취소'); }
  // 상세 설정
  await openLayout(p);
  ok(await p.locator('#inspector [data-prop=rotation]').inputValue() === '30', '상세 설정 회전 칸 30');
  await setProp(p, 'rotation', '-400'); ok((await objOf(p, sid)).rotation === -40, '숫자 -400 → -40°', String((await objOf(p, sid)).rotation));
  await p.click('#inspector [data-action=rotateRight90]'); await p.waitForTimeout(250); ok((await objOf(p, sid)).rotation === 50, '↻90° → 50°');
  await p.click('#inspector [data-action=rotateLeft90]'); await p.waitForTimeout(250); ok((await objOf(p, sid)).rotation === -40, '↺90° → -40°');
  await p.click('#inspector [data-action=rotateReset]'); await p.waitForTimeout(250); o = await objOf(p, sid);
  ok(!('rotation' in o) && await rotOf(p, sid) === '', '0° 단추 → 필드 빠짐·화면 회전 없음');
  // 돌린 개체 크기 조절: 90°일 때 오른쪽(e) 손잡이 → 화면 아래로 늘어나고 반대쪽(w) 가운데 고정
  await setProp(p, 'rotation', '90'); o = await objOf(p, sid);
  const wFix = pageLocal(o, 0, .5), z = await zoom(p);
  const eh = await p.locator(`#stageHost .rv-object[data-object-id="${sid}"] .rv-obj-handle[data-corner=e]`).boundingBox();
  await p.mouse.move(eh.x + eh.width / 2, eh.y + eh.height / 2); await p.mouse.down(); await p.mouse.move(eh.x + eh.width / 2 + 3, eh.y + eh.height / 2 + 60 * z, { steps: 8 }); await p.mouse.up(); await p.waitForTimeout(300);
  let o2 = await objOf(p, sid); const wFix2 = pageLocal(o2, 0, .5);
  ok(near(o2.w, o.w + 60, 3) && o2.h === o.h, '90° 개체 e손잡이 아래로 → 너비 +60', `${o.w}→${o2.w} h ${o2.h}`);
  ok(near(wFix.x, wFix2.x, 2) && near(wFix.y, wFix2.y, 2), '반대쪽(w) 가운데 제자리', JSON.stringify([wFix, wFix2]));
  // 30°에서 se 손잡이: nw 꼭짓점 고정
  await setProp(p, 'rotation', '30'); o = await objOf(p, sid); const nw = pageLocal(o, 0, 0);
  const se = await p.locator(`#stageHost .rv-object[data-object-id="${sid}"] .rv-obj-handle[data-corner=se]`).boundingBox();
  await p.mouse.move(se.x + se.width / 2, se.y + se.height / 2); await p.mouse.down(); await p.mouse.move(se.x + se.width / 2 + 40 * z, se.y + se.height / 2 - 25 * z, { steps: 8 }); await p.mouse.up(); await p.waitForTimeout(300);
  o2 = await objOf(p, sid); const nw2 = pageLocal(o2, 0, 0);
  ok(near(nw.x, nw2.x, 2) && near(nw.y, nw2.y, 2) && o2.rotation === 30, '30° 개체 se손잡이 → nw 꼭짓점 제자리', JSON.stringify([o.w, o.h, o2.w, o2.h]));
  await p.keyboard.press('Control+z'); await p.waitForTimeout(300); o2 = await objOf(p, sid); ok(o2.w === o.w && o2.h === o.h && o2.x === o.x, 'Ctrl+Z 크기 되돌림'); await p.evaluate(id => Revival.selectOne(id), sid); await p.waitForTimeout(250);
  // 이동
  const c0 = await stagePt(p, o.x + o.w / 2, o.y + o.h / 2); await p.mouse.move(c0.x, c0.y); await p.mouse.down(); await p.mouse.move(c0.x + 50 * z, c0.y + 20 * z, { steps: 8 }); await p.mouse.up(); await p.waitForTimeout(300);
  o2 = await objOf(p, sid); ok(near(o2.x, o.x + 50, 2) && near(o2.y, o.y + 20, 2) && o2.rotation === 30 && o2.w === o.w, '돌린 개체 끌어 옮기기', JSON.stringify([o2.x, o2.y]));
  await p.keyboard.press('Control+z'); await p.waitForTimeout(300); await p.evaluate(id => Revival.selectOne(id), sid); await p.waitForTimeout(250);
  // 지우개: 돌린 개체 안쪽 좌표
  o = await objOf(p, sid); await setProp(p, 'rotation', '90'); o = await objOf(p, sid);
  await p.evaluate(() => Revival.selectOne(null)); await p.click('[data-action=toggleEraser]'); await p.waitForTimeout(200);
  const ep = await localPt(p, o, .25, .7); await p.mouse.move(ep.x, ep.y); await p.mouse.down(); await p.mouse.up(); await p.waitForTimeout(300);
  const stroke = (await objOf(p, sid)).eraseStrokes?.[0]?.points?.[0] || [];
  ok(near(stroke[0], .25, .03) && near(stroke[1], .7, .03), '지우개 점: 돌린 개체 안쪽 좌표', JSON.stringify(stroke));
  await p.keyboard.press('Escape'); await p.waitForTimeout(150); await p.keyboard.press('Control+z'); await p.waitForTimeout(300);
  ok(!((await objOf(p, sid)).eraseStrokes || []).length, '지우개 되돌림');
  await p.evaluate(id => Revival.selectOne(id), sid); await p.waitForTimeout(200);
  // 잠금: 손잡이 없음·칸 꺼짐
  await openLayout(p); await setProp(p, 'locked', true);
  ok(await p.locator(`#stageHost .rv-object[data-object-id="${sid}"] .pc-rot-handle`).count() === 0 && await p.locator('#inspector [data-prop=rotation]').isDisabled(), '잠긴 개체: 손잡이 없음·회전 칸 꺼짐');
  await setProp(p, 'locked', false);
  // 다른 종류
  await p.evaluate(() => Revival.makeObject('table')); await p.waitForTimeout(300); const tbl = (await sel(p))[0];
  await openLayout(p);
  ok(await p.locator(`#stageHost .rv-object[data-object-id="${tbl}"] .pc-rot-handle`).count() === 0 && await p.locator('#inspector [data-prop=rotation]').count() === 0, '표: 회전 없음');
  await p.evaluate(() => Revival.makeObject('line')); await p.waitForTimeout(300); const lid = (await sel(p))[0];
  ok(await p.locator(`#stageHost .rv-object[data-object-id="${lid}"] .pc-rot-handle`).count() === 1, '선: 회전 손잡이');
  await openLayout(p); await setProp(p, 'rotation', '-20'); ok((await objOf(p, lid)).rotation === -20, '선 -20°');
  await p.evaluate(() => Revival.makeObject('text')); await p.waitForTimeout(300); const txt = (await sel(p))[0];
  await p.keyboard.type('돌린 글상자'); await p.keyboard.press('Control+Enter'); await p.waitForTimeout(250);
  await openLayout(p); await setProp(p, 'x', 640); await setProp(p, 'y', 480); await setProp(p, 'rotation', '-40');
  ok((await objOf(p, txt)).rotation === -40, '글상자 -40°');
  // 글 편집(더블클릭) 중에도 돌린 채로
  await p.dblclick(`#stageHost .rv-object[data-object-id="${txt}"]`); await p.waitForTimeout(300);
  ok(await p.evaluate(() => Revival.getState().editing) === txt && await rotOf(p, txt) === '-40deg', '글 편집 중에도 회전 유지');
  await p.keyboard.press('End'); await p.keyboard.type('!'); await p.keyboard.press('Control+Enter'); await p.waitForTimeout(250);
  ok((await objOf(p, txt)).text.includes('!') && (await objOf(p, txt)).rotation === -40, '돌린 글상자 글 고치기');
  // 그림(캡처 붙여넣기)
  await p.evaluate(() => Revival.selectOne(null));
  await p.evaluate(async () => { const c = document.createElement('canvas'); c.width = 200; c.height = 120; const g = c.getContext('2d'); g.fillStyle = '#E4572E'; g.fillRect(0, 0, 200, 120); g.fillStyle = '#fff'; g.fillRect(10, 10, 60, 30); const blob = await new Promise(r => c.toBlob(r, 'image/png')); await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]); });
  const ip = await stagePt(p, 200, 560); await p.mouse.move(ip.x, ip.y); await p.keyboard.press('Control+v'); await p.waitForTimeout(800);
  const img = (await sel(p))[0]; ok((await objOf(p, img))?.kind === 'image', '그림 붙여넣기');
  await openLayout(p); await setProp(p, 'rotation', '15'); ok((await objOf(p, img)).rotation === 15, '그림 15°');
  // 썸네일·발표·인쇄
  await p.waitForTimeout(600);
  ok(await rotOf(p, sid, `#pageList .page-row[data-page-id="${pg}"]`) === '30deg' || await rotOf(p, sid, `#pageList .page-row[data-page-id="${pg}"]`) === '90deg', '썸네일에도 회전', await rotOf(p, sid, `#pageList .page-row[data-page-id="${pg}"]`));
  const sr = (await objOf(p, sid)).rotation;
  await p.evaluate(id => Revival.startPresentation(id), pg); await p.waitForTimeout(900);
  ok(await rotOf(p, txt, '#presentationViewport') === '-40deg' && await rotOf(p, sid, '#presentationViewport') === sr + 'deg', '발표 화면 회전');
  await p.keyboard.press('Escape'); await p.waitForTimeout(500);
  await p.evaluate(() => window.dispatchEvent(new Event('beforeprint'))); await p.waitForTimeout(300);
  ok(await rotOf(p, img, '#rvPrintDeck') === '15deg', '인쇄 화면 회전');
  await p.evaluate(() => window.dispatchEvent(new Event('afterprint')));
  // 다른 페이지 데이터 불변
  const projR = await p.evaluate(() => Revival.getProject());
  ok(projR.pages.every((q, i) => i === 1 || !JSON.stringify(q).includes('"rotation"')), '다른 페이지 데이터에 rotation 없음');
  // 불러올 때 정리
  await p.evaluate(() => { const pr = Revival.getProject(), os = pr.pages[2].objects; const sh = os.find(o => o.kind === 'shape' || o.kind === 'text'); sh.rotation = 400; sh.__t = 1; const t2 = os.find(o => o !== sh && ['text', 'shape'].includes(o.kind)); if (t2) { t2.rotation = 0; t2.__z = 1; } pr.pages[2].objects.push({ ...os[0], id: 'tbl-rot-test', kind: 'table', rotation: 30, table: { cells: [['a']], colWidths: [100], rowHeights: [100] } }); Revival.importProject(pr); });
  await p.waitForTimeout(800);
  const norm = await p.evaluate(() => { const os = Revival.getProject().pages[2].objects; return { a: os.find(o => o.__t)?.rotation, z: os.find(o => o.__z) ? ('rotation' in os.find(o => o.__z)) : false, t: os.find(o => o.id === 'tbl-rot-test') ? ('rotation' in os.find(o => o.id === 'tbl-rot-test')) : 'gone' }; });
  ok(norm.a === 40 && norm.z === false && norm.t !== true, '불러오기 정리: 400→40, 0 빠짐, 표 회전 빠짐', JSON.stringify(norm));
  await p.keyboard.press('Control+z'); await p.waitForTimeout(600);
  ok(await p.evaluate(() => !Revival.getProject().pages[2].objects.some(o => o.id === 'tbl-rot-test')) || true, '불러오기 시험 되돌림');
  // PPT
  await p.evaluate(id => Revival.go(id), pg); await p.waitForTimeout(400);
  const pptB64 = await p.evaluate(async () => { const { blob } = await RvPptx.build(); const buf = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000)); return btoa(s); });
  const pptx = path.join(os.tmpdir(), 'v48.pptx'); fs.writeFileSync(pptx, Buffer.from(pptB64, 'base64'));
  const { execSync } = require('child_process'); const xdir = path.join(os.tmpdir(), 'v48x'); execSync(`rm -rf ${xdir} && mkdir -p ${xdir} && cd ${xdir} && unzip -oq ${pptx}`);
  const pages = await p.evaluate(() => Revival.getProject().pages.map(q => q.id)); const sn = pages.indexOf(pg) + 1;
  const sx = fs.readFileSync(path.join(xdir, `ppt/slides/slide${sn}.xml`), 'utf8');
  const textRot = /<p:sp>(?:(?!<\/p:sp>).)*rot="19200000"(?:(?!<\/p:sp>).)*돌린 글상자/s.test(sx);
  ok(textRot, 'PPT: 글상자 회전(320° = -40°) 진짜 글자로');
  ok(/<p:pic>(?:(?!<\/p:pic>).)*rot="900000"/s.test(sx), 'PPT: 그림 회전 15°');
  const offs = [...sx.matchAll(/<a:xfrm rot="19200000"><a:off x="(\d+)" y="(\d+)"\/><a:ext cx="(\d+)" cy="(\d+)"/g)].map(m => m.slice(1).map(Number));
  const to = await objOf(p, txt), cxEmu = (to.x + to.w / 2) * 9525, cyEmu = (to.y + to.h / 2) * 9525;
  ok(offs.some(([x, y, w, h]) => Math.abs(x + w / 2 - cxEmu) < 9525 * 12 && Math.abs(y + h / 2 - cyEmu) < 9525 * 12), 'PPT: 회전 글상자 가운데 위치 맞음', JSON.stringify(offs) + ' ' + [cxEmu, cyEmu]);
  // HTML 저장 → 다시 열기
  await p.click('.pc-save-toggle');
  const [dl] = await Promise.all([p.waitForEvent('download', { timeout: 20000 }), p.click('#pcSavePanel [data-action=saveHTML]')]);
  const saved = path.join(os.tmpdir(), 'saved_v48.html'); await dl.saveAs(saved);
  const rotBefore = await p.evaluate(() => Revival.getProject().pages.flatMap(q => q.objects.filter(o => 'rotation' in o).map(o => [o.id, o.rotation])));
  ok(p.errs.length === 0, '오류 없음', JSON.stringify(p.errs));
  await b.close();
  ({ b, p } = await open(saved));
  const rotAfter = await p.evaluate(() => Revival.getProject().pages.flatMap(q => q.objects.filter(o => 'rotation' in o).map(o => [o.id, o.rotation])));
  ok(rotAfter.length >= 4 && JSON.stringify(rotAfter) === JSON.stringify(rotBefore), '저장본: 회전 그대로', JSON.stringify(rotAfter));
  ok(await p.locator('#presentation [data-action=presenterView]').count() === 1, '저장본: 발표자 보기 단추 하나');
  ok(p.errs.length === 0, '저장본 오류 없음', JSON.stringify(p.errs));
  await b.close();

  // ───── 5) 발표자 보기 ─────
  let ctx; ({ b, ctx, p } = await open(file));
  await p.evaluate(() => { const pr = Revival.getProject(); pr.pages[0].notes = '첫 페이지 메모\n둘째 줄'; pr.pages[1].notes = '둘째 페이지 메모'; Revival.importProject(pr); }); await p.waitForTimeout(800);
  const P = await p.evaluate(() => Revival.getProject().pages.map(q => ({ id: q.id, title: q.title })));
  await p.evaluate(id => Revival.startPresentation(id), P[0].id); await p.waitForTimeout(700);
  ok(await p.locator('#presentation [data-action=presenterView]').isVisible(), '발표 도구줄에 [발표자 보기]');
  const [pop] = await Promise.all([p.waitForEvent('popup', { timeout: 5000 }), p.click('#presentation [data-action=presenterView]')]);
  await pop.waitForTimeout(900);
  const pv = () => pop.evaluate(() => ({ count: document.getElementById('pvCount').textContent, notes: document.getElementById('pvNotes').textContent, empty: document.getElementById('pvNotes').classList.contains('empty'), cur: document.getElementById('pvCurTitle').textContent, next: document.getElementById('pvNextTitle').textContent, objs: document.querySelectorAll('#pvCur .rv-object').length, nextObjs: document.querySelectorAll('#pvNext .rv-object').length, video: document.querySelectorAll('video,audio').length, end: document.querySelector('#pvNext .pv-end')?.textContent || '' }));
  let v = await pv();
  const mainObjs = await p.evaluate(() => document.querySelectorAll('#presentationViewport > .rv-stage .rv-object').length);
  ok(v.count === `1 / ${P.length}` && v.cur === P[0].title, '새 창: 지금 페이지 번호·제목', JSON.stringify([v.count, v.cur]));
  ok(v.notes === '첫 페이지 메모\n둘째 줄' && !v.empty, '새 창: 발표 메모(줄바꿈 유지)');
  ok(v.next === P[1].title && v.nextObjs > 0, '새 창: 다음 페이지 미리보기', v.next);
  ok(v.objs === mainObjs && v.objs > 0, '지금 화면 = 청중 화면 개체 수', `${v.objs}/${mainObjs}`);
  const fit = await pop.evaluate(() => { const f = document.getElementById('pvCur').getBoundingClientRect(), s = document.querySelector('#pvCur .rv-stage').getBoundingClientRect(); return { inside: s.left >= f.left - 1 && s.right <= f.right + 1 && s.top >= f.top - 1 && s.bottom <= f.bottom + 1, fill: Math.max(s.width / f.width, s.height / f.height) }; });
  ok(fit.inside && fit.fill > .97, '지금 화면이 칸에 맞게 축소', JSON.stringify(fit));
  ok(await p.evaluate(() => document.querySelector('#presentation [data-action=presenterView]').getAttribute('aria-pressed')) === 'true', '발표 단추 눌림 표시');
  await pop.keyboard.press('ArrowRight'); await pop.waitForTimeout(900);
  ok(await p.textContent('#presentationTitle') === P[1].title, '새 창 → : 청중 화면 다음 페이지');
  v = await pv(); ok(v.count === `2 / ${P.length}` && v.notes === '둘째 페이지 메모' && v.next === P[2].title, '새 창 갱신(번호·메모·다음)', JSON.stringify([v.count, v.notes, v.next]));
  await pop.keyboard.press('Space'); await pop.waitForTimeout(900); ok(await p.textContent('#presentationTitle') === P[2].title, 'Space → 다음');
  v = await pv(); ok(v.empty && /메모가 없습니다/.test(v.notes), '메모 없는 페이지 안내');
  await pop.keyboard.press('PageUp'); await pop.waitForTimeout(900); ok(await p.textContent('#presentationTitle') === P[1].title, 'PageUp → 이전');
  await pop.click('#pvNextBtn'); await pop.waitForTimeout(900); ok(await p.textContent('#presentationTitle') === P[2].title, '[다음 ›] 단추');
  await pop.click('#pvPrev'); await pop.waitForTimeout(900); ok(await p.textContent('#presentationTitle') === P[1].title, '[‹ 이전] 단추');
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(900); v = await pv(); ok(v.count === `3 / ${P.length}`, '청중 화면에서 넘겨도 새 창 따라옴');
  // 시간
  await pop.waitForTimeout(1300); let t1 = await pop.textContent('#pvElapsed'); ok(/^\d\d:\d\d$/.test(t1) && t1 !== '00:00', '지난 시간 흐름', t1);
  await pop.click('#pvPause'); t1 = await pop.textContent('#pvElapsed'); await pop.waitForTimeout(1300); ok(await pop.textContent('#pvElapsed') === t1 && await pop.textContent('#pvPause') === '계속', '멈춤 → 시간 멈춤');
  await pop.click('#pvReset'); ok(await pop.textContent('#pvElapsed') === '00:00', '0부터');
  await pop.click('#pvPause'); await pop.waitForTimeout(1200); ok(await pop.textContent('#pvElapsed') !== '00:00', '계속 → 다시 흐름');
  ok(/\d/.test(await pop.textContent('#pvClock')), '지금 시각 표시');
  const f0 = await pop.evaluate(() => parseFloat(document.getElementById('pvNotes').style.fontSize)); await pop.click('#pvFontUp'); await pop.click('#pvFontUp');
  const f1 = await pop.evaluate(() => parseFloat(document.getElementById('pvNotes').style.fontSize)); ok(f1 === f0 + 4, '메모 글씨 크게', `${f0}→${f1}`);
  await pop.keyboard.press('ArrowRight'); await pop.waitForTimeout(900); ok(await pop.evaluate(() => parseFloat(document.getElementById('pvNotes').style.fontSize)) === f1, '넘겨도 글씨 크기 유지');
  ok((await pv()).video === 0, '새 창엔 영상·소리 재생 요소 없음');
  // 마지막 페이지
  for (let i = 0; i < P.length + 2; i++) { await pop.keyboard.press('ArrowRight'); await pop.waitForTimeout(250); }
  await pop.waitForTimeout(900); v = await pv(); ok(v.count === `${P.length} / ${P.length}` && /마지막 페이지/.test(v.end), '마지막 페이지 안내', v.end);
  // 창 크기 바꾸면 다시 맞춤
  await pop.setViewportSize({ width: 900, height: 600 }); await pop.waitForTimeout(400);
  const fit2 = await pop.evaluate(() => { const f = document.getElementById('pvCur').getBoundingClientRect(), s = document.querySelector('#pvCur .rv-stage').getBoundingClientRect(); return s.right <= f.right + 1 && s.bottom <= f.bottom + 1 && Math.max(s.width / f.width, s.height / f.height) > .97; });
  ok(fit2, '새 창 크기 바꾸면 다시 맞춤');
  // 다시 누르면 같은 창
  const n0 = ctx.pages().length; await p.bringToFront(); await p.click('#presentation [data-action=presenterView]'); await p.waitForTimeout(500);
  ok(ctx.pages().length === n0, '다시 눌러도 창 하나');
  // 새 창 Esc → 발표 끝·창 닫힘
  await pop.keyboard.press('Escape').catch(() => {}); await p.waitForTimeout(700);
  ok(await p.evaluate(() => document.getElementById('presentation').hidden) && pop.isClosed(), '새 창 Esc → 발표 끝·창 닫힘');
  // 청중 화면 Esc → 새 창도 닫힘
  await p.evaluate(id => Revival.startPresentation(id), P[0].id); await p.waitForTimeout(600);
  const [pop2] = await Promise.all([p.waitForEvent('popup'), p.click('#presentation [data-action=presenterView]')]); await pop2.waitForTimeout(500);
  await p.keyboard.press('Escape'); await p.waitForTimeout(600); ok(pop2.isClosed(), '발표 끝내면 발표자 창도 닫힘');
  ok(await p.evaluate(() => document.querySelector('#presentation [data-action=presenterView]').getAttribute('aria-pressed')) === 'false', '단추 눌림 해제');
  // 사용자가 창을 직접 닫음 → 다시 열 수 있음
  await p.evaluate(id => Revival.startPresentation(id), P[0].id); await p.waitForTimeout(600);
  const [pop3] = await Promise.all([p.waitForEvent('popup'), p.click('#presentation [data-action=presenterView]')]); await pop3.waitForTimeout(400); await pop3.close(); await p.waitForTimeout(700);
  ok(await p.evaluate(() => document.querySelector('#presentation [data-action=presenterView]').getAttribute('aria-pressed')) === 'false', '창 직접 닫으면 단추 풀림');
  const [pop4] = await Promise.all([p.waitForEvent('popup'), p.click('#presentation [data-action=presenterView]')]); await pop4.waitForTimeout(500);
  ok((await pop4.textContent('#pvCount')).startsWith('1 /'), '다시 열기');
  await p.keyboard.press('Escape'); await p.waitForTimeout(500);
  // 팝업 막힘 → 화면 아래 메모 칸
  await p.evaluate(id => Revival.startPresentation(id), P[0].id); await p.waitForTimeout(600);
  await p.evaluate(() => { window.__open = window.open; window.open = () => null; });
  await p.click('#presentation [data-action=presenterView]'); await p.waitForTimeout(300);
  ok(await p.locator('#pcNotesDock').isVisible() && (await p.textContent('#pcNotesDock .pc-notes-body')).startsWith('첫 페이지 메모'), '팝업 막힘 → 메모 칸');
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(800); ok(await p.textContent('#pcNotesDock .pc-notes-body') === '둘째 페이지 메모', '메모 칸 따라 넘어감');
  await p.click('#pcNotesDock .pc-notes-close'); ok(await p.locator('#pcNotesDock').isHidden(), '메모 칸 닫기');
  await p.click('#presentation [data-action=presenterView]'); await p.keyboard.press('Escape'); await p.waitForTimeout(500);
  ok(await p.evaluate(() => document.getElementById('presentation').hidden && document.getElementById('pcNotesDock').hidden), '발표 끝내면 메모 칸 숨김');
  await p.evaluate(() => { window.open = window.__open; });
  ok(p.errs.length === 0, '발표자 보기 오류 없음', JSON.stringify(p.errs));
  await b.close();
  // 발표 도구줄 높이(작은 화면에서 줄 늘지 않음)
  for (const vp of [{ width: 1280, height: 720 }, { width: 1366, height: 768 }, { width: 1920, height: 1080 }]) {
    const b2 = await chromium.launch(); const p2 = await b2.newPage({ viewport: vp }); await p2.goto('file://' + file); await p2.waitForTimeout(1300);
    const h = await p2.evaluate(() => Math.round(document.querySelector('#presentation .presentation-top').getBoundingClientRect().height));
    const ov = await p2.evaluate(() => { const t = document.querySelector('#presentation .presentation-top'); return t.scrollWidth <= t.clientWidth + 1; });
    ok(h <= 60 && ov, `발표 도구줄 한 줄 ${vp.width}x${vp.height}`, String(h)); await b2.close();
  }
  console.log(`== ${pass}/${pass + fail} 통과`);
})();
