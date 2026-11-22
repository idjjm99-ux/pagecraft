// v12.47.0 시험(노드 Playwright): node t_v47.js <PageCraft_v12.47.0_Lite.html>
// 1 글자 맞춤 · 2 캡처 그림 Ctrl+V · 4 선 화살표 · 3 페이지 끌어서 순서 바꾸기 · PPT 저장 · 저장본 다시 열기
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path'), os = require('os');
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
  return { b, p };
}
const cur = p => p.evaluate(() => Revival.getCurrentPage());
const objOf = (p, id) => p.evaluate(id => Revival.getCurrentPage().objects.find(o => o.id === id), id);
const sel = p => p.evaluate(() => Revival.getSelected());
const box = (p, id) => p.locator(`#stageHost .rv-object[data-object-id="${id}"]`).boundingBox();
async function clipImage(p, w, h, color) {
  await p.evaluate(async ([w, h, color]) => {
    const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); g.fillStyle = color; g.fillRect(0, 0, w, h);
    const blob = await new Promise(r => c.toBlob(r, 'image/png')); await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
  }, [w, h, color]);
}
const clipText = (p, t) => p.evaluate(t => navigator.clipboard.writeText(t), t);
const stagePt = (p, px, py) => p.evaluate(([px, py]) => { const s = document.querySelector('#stageHost .rv-stage'), r = s.getBoundingClientRect(); return { x: r.left + px * r.width / s.offsetWidth, y: r.top + py * r.height / s.offsetHeight }; }, [px, py]);

const pcVer = async (p, file) => { const bv = await p.evaluate(() => Revival.buildVersion()), v = (require('path').basename(file).match(/v(\d+\.\d+\.\d+)/) || [])[1] || (bv.match(/v(\d+\.\d+\.\d+)/) || [])[1], sig = await p.locator('#rv-app-signature').textContent(); return { v, bv, sig, okV: bv.startsWith('PageCraft v' + v), okSig: sig.includes('v' + v) }; };
(async () => {
  const { b, p } = await open(file);
  { const r = await pcVer(p, file); ok(r.okV, '버전 = 파일 이름 v' + r.v, r.bv); ok(r.okSig, '서명 버전', r.sig); }
  ok(await p.evaluate(() => Revival.keymap().some(k => k.keys.includes('Ctrl+E'))), '단축키 표에 Ctrl+L·E·R');

  // ───── 1) 글자 맞춤 ─────
  await p.evaluate(() => Revival.go(Revival.getProject().pages[1].id)); await p.waitForTimeout(300);
  await p.evaluate(() => Revival.makeObject('text')); await p.waitForTimeout(300);
  const tid = (await sel(p))[0];
  ok((await p.evaluate(() => Revival.getState().editing)) === tid, '새 글상자는 바로 글 편집'); await p.keyboard.press('Control+Enter'); await p.waitForTimeout(200);
  ok(await p.locator('.ribbon [data-action=textAlignCenter]').isEnabled(), '도구줄 맞춤 단추 켜짐(글상자)');
  await p.click('.ribbon [data-action=textAlignCenter]'); await p.waitForTimeout(200);
  let o = await objOf(p, tid);
  ok(o.style.textAlign === 'center', '도구줄 가운데 → 저장값 center', o.style.textAlign);
  ok(await p.evaluate(id => getComputedStyle(document.querySelector(`#stageHost [data-object-id="${id}"] .rv-text-content`)).textAlign, tid) === 'center', '화면 글자 가운데');
  ok(await p.getAttribute('.ribbon [data-action=textAlignCenter]', 'aria-pressed') === 'true' && await p.getAttribute('.ribbon [data-action=textAlignLeft]', 'aria-pressed') === 'false', '눌린 단추 표시');
  ok(await p.locator('#quickBar [data-action=textAlignRight]').isVisible(), '간편편집바 맞춤 단추');
  await p.click('#quickBar [data-action=textAlignRight]'); await p.waitForTimeout(200);
  ok((await objOf(p, tid)).style.textAlign === 'right', '간편편집바 오른쪽');
  ok(await p.getAttribute('#quickBar [data-action=textAlignRight]', 'aria-pressed') === 'true', '간편편집바 눌림 표시');
  await p.evaluate(() => window.__alive = 1);
  await p.keyboard.press('Control+e'); await p.waitForTimeout(150); ok((await objOf(p, tid)).style.textAlign === 'center', 'Ctrl+E 가운데');
  await p.keyboard.press('Control+l'); await p.waitForTimeout(150); ok((await objOf(p, tid)).style.textAlign === 'left', 'Ctrl+L 왼쪽');
  await p.keyboard.press('Control+r'); await p.waitForTimeout(400); ok((await objOf(p, tid)).style.textAlign === 'right', 'Ctrl+R 오른쪽');
  ok(await p.evaluate(() => window.__alive === 1), 'Ctrl+R 새로고침 안 됨');
  await p.keyboard.press('Control+z'); await p.waitForTimeout(200); ok((await objOf(p, tid)).style.textAlign === 'left', 'Ctrl+Z 되돌리기');
  // 선택 없음: Ctrl+R 은 브라우저 기본 그대로(가로채지 않음)
  await p.evaluate(() => Revival.selectOne(null)); await p.waitForTimeout(150);
  const dp = await p.evaluate(() => { const e = new KeyboardEvent('keydown', { key: 'r', code: 'KeyR', ctrlKey: true, bubbles: true, cancelable: true }); document.body.dispatchEvent(e); return { sel: Revival.getSelected().length, dp: e.defaultPrevented }; });
  ok(dp.sel === 0 && !dp.dp, '선택 없을 때 Ctrl+R 안 가로챔', JSON.stringify(dp));
  // 여러 개 선택(양식 글상자 2개: 클릭 + Shift 클릭)
  await p.evaluate(() => Revival.makeObject('text')); await p.waitForTimeout(300);
  const tid2 = (await sel(p))[0]; await p.keyboard.press('Control+Enter'); await p.waitForTimeout(200);
  const ts = await p.evaluate(() => Revival.getCurrentPage().objects.filter(o => o.kind === 'text' && !o.locked && o.role !== 'user').map(o => o.id).slice(0, 2));
  await p.locator(`#stageHost .rv-object[data-object-id="${ts[0]}"]`).click({ force: true }); await p.waitForTimeout(200);
  await p.locator(`#stageHost .rv-object[data-object-id="${ts[1]}"]`).click({ force: true, modifiers: ['Shift'] }); await p.waitForTimeout(200);
  const s2 = await sel(p);
  if (s2.length === 2) { const orig = [(await objOf(p, ts[0])).style.textAlign, (await objOf(p, ts[1])).style.textAlign];
    await p.click('.ribbon [data-action=textAlignRight]'); await p.waitForTimeout(200);
    ok((await objOf(p, ts[0])).style.textAlign === 'right' && (await objOf(p, ts[1])).style.textAlign === 'right', '여러 개 한꺼번에 오른쪽', JSON.stringify(orig));
    ok((await p.locator('#saveStatus').textContent()).includes('2개'), '상태줄 2개', await p.locator('#saveStatus').textContent());
    await p.keyboard.press('Control+z'); await p.waitForTimeout(200);
    ok(JSON.stringify([(await objOf(p, ts[0])).style.textAlign, (await objOf(p, ts[1])).style.textAlign]) === JSON.stringify(orig), '여러 개 Ctrl+Z 한 번에 되돌림'); }
  else ok(false, '여러 개 선택 준비', JSON.stringify(s2));
  // 글 편집 중
  await p.evaluate(id => Revival.selectOne(id), tid2); await p.waitForTimeout(150);
  const b2 = await box(p, tid2); await p.mouse.dblclick(b2.x + b2.width - 12, b2.y + b2.height - 12); await p.waitForTimeout(300);
  const ed1 = (await p.evaluate(() => Revival.getState().editing));
  await p.keyboard.press('Control+r'); await p.waitForTimeout(150);
  await p.click('#quickBar [data-action=textAlignLeft]').catch(() => {}); await p.waitForTimeout(150);
  await p.keyboard.press('Control+r'); await p.waitForTimeout(150);
  await p.keyboard.type('추가'); await p.waitForTimeout(100);
  const ed2 = await p.evaluate(() => Revival.getState().editing);
  ok(ed1 === tid2 && ed2 === tid2, '글 편집 중 맞춤 → 편집 그대로', ed1 + ' / ' + ed2);
  ok(await p.evaluate(id => getComputedStyle(document.querySelector(`#stageHost [data-object-id="${id}"] .rv-text-content`)).textAlign, tid2) === 'right', '편집 중 화면 오른쪽');
  await p.keyboard.press('Control+Enter'); await p.waitForTimeout(250);
  o = await objOf(p, tid2); ok(o.style.textAlign === 'right' && o.text.includes('추가'), '편집 마친 뒤 맞춤·글 모두 저장', o.style.textAlign + ' ' + JSON.stringify(o.text).slice(0, 40));
  // 선 선택 시 맞춤 단추 꺼짐
  await p.evaluate(() => Revival.makeObject('line')); await p.waitForTimeout(300);
  ok(await p.locator('.ribbon [data-action=textAlignCenter]').isDisabled(), '선 선택 → 맞춤 단추 꺼짐');
  const lid = (await sel(p))[0];

  // ───── 4) 선 화살표 ─────
  ok(await p.locator('#quickBar [data-quick-line-arrow]').isVisible(), '간편편집바 화살표 칸');
  await p.selectOption('#quickBar [data-quick-line-arrow]', 'end'); await p.waitForTimeout(250);
  o = await objOf(p, lid); let heads = await p.locator(`#stageHost [data-object-id="${lid}"] polygon.pc-line-head`).count();
  ok(o.lineArrow === 'end' && heads === 1, '끝 화살표 1개', o.lineArrow + ' ' + heads);
  const tip = await p.evaluate(id => { const n = document.querySelector(`#stageHost [data-object-id="${id}"]`); const pts = n.querySelector('polygon').getAttribute('points').split(' ')[0].split(',').map(Number); const ln = n.querySelector('line'); return { tipX: pts[0], w: Number(n.querySelector('svg').getAttribute('viewBox').split(' ')[2]), x2: Number(ln.getAttribute('x2')) }; }, lid);
  ok(tip.tipX > tip.w - 12 && tip.x2 < tip.tipX, '화살 끝은 오른쪽 끝, 선은 화살 안에서 멈춤', JSON.stringify(tip));
  await p.selectOption('#quickBar [data-quick-line-arrow]', 'both'); await p.waitForTimeout(250);
  heads = await p.locator(`#stageHost [data-object-id="${lid}"] polygon.pc-line-head`).count(); ok(heads === 2, '양쪽 화살표 2개');
  ok(await p.locator(`.page-row.active polygon.pc-line-head`).count() === 2, '썸네일에도 화살표');
  await p.selectOption('#quickBar [data-quick-line-arrow]', 'none'); await p.waitForTimeout(250);
  o = await objOf(p, lid); heads = await p.locator(`#stageHost [data-object-id="${lid}"] polygon.pc-line-head`).count();
  ok(!('lineArrow' in o) && heads === 0, '없음 → 저장값에서 빠짐', JSON.stringify(o.lineArrow));
  await p.keyboard.press('Control+z'); await p.waitForTimeout(200); ok((await objOf(p, lid)).lineArrow === 'both', 'Ctrl+Z 화살표 복원');
  // 상세 설정 칸
  await p.evaluate(id => Revival.selectOne(id), lid); await p.waitForTimeout(300);
  const insp = await p.evaluate(() => { const s = document.querySelector('#inspector select[data-prop=lineArrow]'); return s ? { v: s.value, n: s.options.length } : null; });
  ok(insp && insp.v === 'both' && insp.n === 4, '상세 설정 화살표 칸', JSON.stringify(insp));
  // 도형 고르기 '화살표'
  await p.click('.ribbon [data-action=insert]'); await p.waitForTimeout(250);
  ok(await p.locator('#placementPicker [data-placement-option=line-arrow]').isVisible(), '도형 고르기에 화살표');
  await p.click('#placementPicker [data-placement-option=line-arrow]'); await p.waitForTimeout(200);
  const sp = await stagePt(p, 640, 600); await p.mouse.click(sp.x, sp.y); await p.waitForTimeout(400);
  const nid = (await sel(p))[0]; o = await objOf(p, nid);
  ok(o && o.kind === 'line' && o.lineArrow === 'end' && o.lineDirection === 'h', '화살표 놓기 → 끝 화살표 선', o && (o.kind + ' ' + o.lineArrow + ' ' + o.lineDirection));
  // 기존 문서 데이터 불변: 화살표 없는 선엔 lineArrow 없음
  ok(await p.evaluate(() => Revival.getProject().pages.slice(2).every(pg => pg.objects.every(x => !('lineArrow' in x)))), '다른 페이지 데이터에 lineArrow 없음');

  // ───── 2) 캡처 그림 Ctrl+V ─────
  await p.evaluate(() => Revival.selectOne(null)); await p.waitForTimeout(150);
  let n0 = (await cur(p)).objects.length;
  await clipImage(p, 400, 300, '#E11D48');
  const mp = await stagePt(p, 700, 380); await p.mouse.move(mp.x, mp.y); await p.mouse.move(mp.x + 1, mp.y);
  await p.keyboard.press('Control+v'); await p.waitForTimeout(1200);
  let pg = await cur(p), im;
  const s3 = await sel(p); im = pg.objects.find(x => x.id === s3[0]);
  ok(pg.objects.length === n0 + 1 && im && im.kind === 'image', '그림 Ctrl+V → 그림 개체 1개', pg.objects.length - n0 + ' ' + (im && im.kind));
  if (im) {
    ok(Math.abs(im.w / im.h - 4 / 3) < 0.02, '원래 비율(4:3)', im.w + 'x' + im.h);
    ok(Math.abs(im.x + im.w / 2 - 701) <= 3 && Math.abs(im.y + im.h / 2 - 380) <= 3, '마우스 위치 가운데', `${im.x + im.w / 2},${im.y + im.h / 2}`);
    ok(/^붙여넣은 그림\.png$/.test(im.media?.name || ''), '이름 붙여넣은 그림.png', im.media?.name);
    ok(await p.evaluate(id => !!document.querySelector(`#stageHost [data-object-id="${id}"] img`)?.naturalWidth, im.id), '화면에 그림 보임');
  }
  ok((await p.locator('#saveStatus').textContent()).includes('그림을 붙여넣었습니다'), '상태줄 안내', await p.locator('#saveStatus').textContent());
  // 큰 그림은 페이지 60% 안
  await p.evaluate(() => Revival.selectOne(null));
  await clipImage(p, 3000, 2000, '#2563EB'); await p.mouse.move(mp.x, mp.y);
  await p.keyboard.press('Control+v'); await p.waitForTimeout(1500);
  const bigSel = await sel(p); const bo = await objOf(p, bigSel[0]);
  const PW = await p.evaluate(() => document.querySelector('#stageHost .rv-stage').offsetWidth);
  ok(bo && bo.kind === 'image' && bo.w <= PW * 0.6 + 1 && Math.abs(bo.w / bo.h - 1.5) < 0.02, '큰 그림 축소(폭 60% 이하·비율 유지)', bo && (bo.w + 'x' + bo.h + ' / ' + PW));
  await p.keyboard.press('Control+z'); await p.waitForTimeout(300);
  ok((await cur(p)).objects.length === n0 + 1, 'Ctrl+Z 붙여넣은 그림 없앰');
  // 그림 칸 골라 두면 바꿈
  await p.evaluate(id => Revival.selectOne(id), im.id); await p.waitForTimeout(150);
  const before = (await objOf(p, im.id)).media.assetRef;
  await clipImage(p, 200, 200, '#16A34A'); await p.keyboard.press('Control+v'); await p.waitForTimeout(1200);
  const after = await objOf(p, im.id);
  ok((await cur(p)).objects.length === n0 + 1 && after.media.assetRef !== before, '그림 골라 두고 Ctrl+V → 그 그림 바꿈');
  // 앱 안 개체 복사 → 클립보드 표시 글자 → 개체 붙여넣기
  await p.evaluate(id => Revival.selectOne(id), tid); await p.waitForTimeout(150);
  await p.keyboard.press('Control+c'); await p.waitForTimeout(300);
  const ct = await p.evaluate(() => navigator.clipboard.readText().catch(e => 'ERR ' + e.message));
  ok(/^\[페이지공방 개체 1개 복사/.test(ct), '앱 복사 → 클립보드 표시 글자', ct);
  n0 = (await cur(p)).objects.length; await p.mouse.move(mp.x, mp.y);
  await p.keyboard.press('Control+v'); await p.waitForTimeout(500);
  pg = await cur(p); let ns = await sel(p);
  ok(pg.objects.length === n0 + 1 && pg.objects.find(x => x.id === ns[0])?.kind === 'text', '복사한 개체 붙여넣기(그림 아님)');
  // 그 뒤 캡처 → 그림이 이김
  await clipImage(p, 300, 150, '#F59E0B'); await p.keyboard.press('Control+v'); await p.waitForTimeout(1200);
  pg = await cur(p); ns = await sel(p);
  ok(pg.objects.length === n0 + 2 && pg.objects.find(x => x.id === ns[0])?.kind === 'image', '나중에 캡처한 그림이 붙음');
  // 다른 글자가 클립보드에 있으면 기존처럼 앱 개체 붙여넣기
  await clipText(p, '아무 글자'); await p.keyboard.press('Control+v'); await p.waitForTimeout(500);
  pg = await cur(p); ok(pg.objects.length === n0 + 3, '클립보드 글자 + 앱 복사 → 개체 붙여넣기(기존 동작)');
  // 글 편집 중 그림 → 편집 마치고 그림 개체
  await p.evaluate(id => Revival.selectOne(id), tid); await p.waitForTimeout(150);
  const b3 = await box(p, tid); await p.mouse.dblclick(b3.x + 8, b3.y + b3.height / 2); await p.waitForTimeout(300);
  const edA = await p.evaluate(() => Revival.getState().editing);
  await clipImage(p, 120, 80, '#7C3AED'); await p.keyboard.press('Control+v'); await p.waitForTimeout(1200);
  pg = await cur(p); ns = await sel(p);
  ok(edA === tid && (await p.evaluate(() => Revival.getState().editing)) === null && pg.objects.find(x => x.id === ns[0])?.kind === 'image' && !(pg.objects.find(x => x.id === tid).textHtml || '').includes('<img'), '글 편집 중 그림 → 편집 마치고 그림 개체');
  // 표 선택 + 엑셀 글자 → 표 칸 붙여넣기 그대로
  await p.evaluate(() => Revival.makeObject('table')); await p.waitForTimeout(400); await p.keyboard.press('Escape'); await p.evaluate(() => Revival.selectOne(Revival.getSelected()[0])); await p.waitForTimeout(200);
  const tb = (await sel(p))[0];
  await clipText(p, 'A\tB\n1\t2'); await p.keyboard.press('Control+v'); await p.waitForTimeout(500);
  const tab = (await objOf(p, tb)).table; const cells = JSON.stringify(tab.cells || tab.rows || tab);
  ok(cells.includes('"A"') || cells.includes('A'), '표 선택 + 엑셀 글자 → 표 칸 붙여넣기', cells.slice(0, 80));

  // 앱 복사 표시 글자(다른 창·다시 연 문서에서 남은 것)는 표 칸·제목 칸에 글자로 안 들어감
  await clipText(p, '[페이지공방 개체 2개 복사 abc123]');
  const tabBefore = JSON.stringify((await objOf(p, tb)).table);
  await p.evaluate(id => Revival.selectOne(id), tb); await p.waitForTimeout(200);
  await p.keyboard.press('Control+v'); await p.waitForTimeout(400);
  ok(JSON.stringify((await objOf(p, tb)).table) === tabBefore, '표시 글자 → 표 칸에 안 들어감');
  const title0 = await p.inputValue('#projectTitle'); await p.click('#projectTitle'); await p.keyboard.press('End'); await p.keyboard.press('Control+v'); await p.waitForTimeout(200);
  ok(await p.inputValue('#projectTitle') === title0, '표시 글자 → 제목 칸에 안 들어감'); await p.keyboard.press('Escape');
  // ───── 3) 페이지 끌기 ─────
  for (let i = 0; i < 4; i++) await p.evaluate(() => Revival.clonePage(Revival.getProject().pages.at(-1).id));
  await p.waitForTimeout(500);
  const ids0 = (await p.evaluate(() => Revival.getProject().pages.map(x => x.id)));
  await p.evaluate(id => Revival.go(id), ids0[1]); await p.waitForTimeout(400);
  const rowBox = async id => (await p.locator(`#pageList .page-row[data-page-id="${id}"] .page-select`).boundingBox());
  await p.evaluate(() => document.querySelector('#pageList').scrollTop = 0);
  const a = await rowBox(ids0[2]), t0 = await rowBox(ids0[0]);
  await p.mouse.move(a.x + a.width / 2, a.y + a.height / 2); await p.mouse.down();
  await p.mouse.move(a.x + a.width / 2, a.y + a.height / 2 - 10, { steps: 3 });
  await p.mouse.move(t0.x + t0.width / 2, t0.y + 5, { steps: 8 }); await p.waitForTimeout(100);
  ok(await p.locator('#pageList .page-row.pc-drop-before').count() === 1 && await p.locator('#pageList .page-row.pc-page-dragging').count() === 1, '끄는 중 놓을 자리 표시');
  await p.mouse.up(); await p.waitForTimeout(500);
  let ids1 = await p.evaluate(() => Revival.getProject().pages.map(x => x.id));
  ok(ids1[0] === ids0[2] && ids1[1] === ids0[0] && ids1.length === ids0.length, '3번 → 1번 자리로(위로)', ids1.slice(0, 4).map(x => ids0.indexOf(x) + 1).join(','));
  ok(await p.evaluate(() => Revival.getState().currentPageId) === ids0[1], '끈 뒤 보던 페이지 그대로(클릭으로 안 넘어감)');
  const domOrder = await p.evaluate(() => [...document.querySelectorAll('#pageList > .page-row')].map(r => r.dataset.pageId));
  ok(JSON.stringify(domOrder) === JSON.stringify(ids1), '목록 순서·번호 갱신');
  await p.keyboard.press('Control+z'); await p.waitForTimeout(400);
  ok(JSON.stringify(await p.evaluate(() => Revival.getProject().pages.map(x => x.id))) === JSON.stringify(ids0), 'Ctrl+Z 순서 되돌림');
  // 아래로 끌기(1번 → 3번 뒤)
  const c0 = await rowBox(ids0[0]), c2 = await rowBox(ids0[2]);
  await p.mouse.move(c0.x + 20, c0.y + 20); await p.mouse.down(); await p.mouse.move(c0.x + 20, c0.y + 40, { steps: 3 });
  await p.mouse.move(c2.x + 20, c2.y + c2.height - 4, { steps: 10 }); await p.mouse.up(); await p.waitForTimeout(400);
  ids1 = await p.evaluate(() => Revival.getProject().pages.map(x => x.id));
  ok(ids1[2] === ids0[0] && ids1[0] === ids0[1], '1번 → 3번 자리로(아래로)', ids1.slice(0, 4).map(x => ids0.indexOf(x) + 1).join(','));
  await p.keyboard.press('Control+z'); await p.waitForTimeout(300);
  // Esc 취소
  const e0 = await rowBox(ids0[2]);
  await p.mouse.move(e0.x + 20, e0.y + 20); await p.mouse.down(); await p.mouse.move(e0.x + 20, e0.y - 60, { steps: 6 });
  await p.keyboard.press('Escape'); await p.mouse.up(); await p.waitForTimeout(300);
  ok(JSON.stringify(await p.evaluate(() => Revival.getProject().pages.map(x => x.id))) === JSON.stringify(ids0) && await p.locator('#pageList .pc-drop-before,#pageList .pc-drop-after').count() === 0, 'Esc → 취소, 표시 지움');
  // 조금 움직인 클릭은 이동
  const f0 = await rowBox(ids0[2]); await p.mouse.move(f0.x + 20, f0.y + 20); await p.mouse.down(); await p.mouse.move(f0.x + 22, f0.y + 22); await p.mouse.up(); await p.waitForTimeout(400);
  ok(await p.evaluate(() => Revival.getState().currentPageId) === ids0[2], '살짝 움직인 클릭 → 그 페이지로 이동');
  // ↑↓ 단추 그대로
  await p.click(`#pageList .page-row[data-page-id="${ids0[2]}"] [data-action=pageUp]`); await p.waitForTimeout(300);
  ids1 = await p.evaluate(() => Revival.getProject().pages.map(x => x.id)); ok(ids1[1] === ids0[2], '↑ 단추 그대로'); await p.keyboard.press('Control+z'); await p.waitForTimeout(300);
  // 목록 끝 자동 스크롤
  await p.evaluate(() => document.querySelector('#pageList').scrollTop = 0);
  const lb = await p.locator('#pageList').boundingBox(); const g0 = await rowBox(ids0[0]);
  await p.mouse.move(g0.x + 20, g0.y + 20); await p.mouse.down(); await p.mouse.move(g0.x + 20, g0.y + 50, { steps: 4 });
  await p.mouse.move(g0.x + 20, lb.y + lb.height - 6, { steps: 6 }); await p.waitForTimeout(700);
  const sc = await p.evaluate(() => document.querySelector('#pageList').scrollTop);
  await p.keyboard.press('Escape'); await p.mouse.up(); await p.waitForTimeout(200);
  ok(sc > 40, '목록 아래 끝에서 자동 스크롤', String(sc));

  // ───── PPT 저장 · HTML 저장 ─────
  await p.evaluate(() => Revival.go(Revival.getProject().pages[1].id)); await p.waitForTimeout(400);
  await p.click('.pc-save-toggle');
  const [dpp] = await Promise.all([p.waitForEvent('download', { timeout: 90000 }), p.click('#pcSavePanel [data-action=exportPptx]')]);
  const pptx = path.join(os.tmpdir(), 'v47.pptx'); await dpp.saveAs(pptx);
  const { execSync } = require('child_process'); const xdir = path.join(os.tmpdir(), 'v47x'); execSync(`rm -rf ${xdir} && mkdir -p ${xdir} && cd ${xdir} && unzip -oq ${pptx}`);
  const s2xml = fs.readFileSync(path.join(xdir, 'ppt/slides/slide2.xml'), 'utf8');
  ok(/algn="r"/.test(s2xml) && /algn="ctr"/.test(s2xml), 'PPT: 오른쪽·가운데 맞춤 들어감');
  ok((s2xml.match(/<p:pic>/g) || []).length >= 3, 'PPT: 붙여넣은 그림 들어감', String((s2xml.match(/<p:pic>/g) || []).length));
  await p.click('.pc-save-toggle');
  const [dl] = await Promise.all([p.waitForEvent('download', { timeout: 20000 }), p.click('#pcSavePanel [data-action=saveHTML]')]);
  const saved = path.join(os.tmpdir(), 'saved_v47.html'); await dl.saveAs(saved);
  const projBefore = await p.evaluate(() => Revival.getProject().pages[1].objects.map(o => [o.id, o.kind, o.style?.textAlign, o.lineArrow || '']));
  ok(p.errs.length === 0, '오류 없음', JSON.stringify(p.errs));
  await b.close();
  const r = await open(saved);
  await r.p.evaluate(() => Revival.go(Revival.getProject().pages[1].id)); await r.p.waitForTimeout(500);
  const projAfter = await r.p.evaluate(() => Revival.getProject().pages[1].objects.map(o => [o.id, o.kind, o.style?.textAlign, o.lineArrow || '']));
  ok(JSON.stringify(projAfter) === JSON.stringify(projBefore), '저장본: 맞춤·화살표·그림 그대로');
  const md = await r.p.evaluate(() => Revival.mediaDiagnostics());
  ok(md.missing.length === 0, '저장본: 그림 빠진 것 없음', JSON.stringify(md));
  ok(await r.p.locator('.ribbon .pc-align-group').count() === 1 && await r.p.locator('#pageList').count() === 1, '저장본: 단추 중복 없음');
  ok(r.p.errs.length === 0, '저장본 오류 없음', JSON.stringify(r.p.errs));
  await r.b.close();
  // 도구줄 줄 수(편집 화면 높이)
  for (const vp of [{ width: 1280, height: 720 }, { width: 1366, height: 768 }, { width: 1440, height: 900 }, { width: 1500, height: 950 }, { width: 1920, height: 1080 }]) {
    const { b, p } = await open(file, vp);
    const m = await p.evaluate(() => ({ h: Math.round(document.querySelector('.ribbon').getBoundingClientRect().height), zoom: document.querySelector('#zoomLabel').textContent }));
    const want = { 1280: 166, 1366: 128, 1440: 130, 1500: 130, 1920: 130 }[vp.width];
    ok(m.h <= want, `도구줄 높이 v12.46 이하 ${vp.width}x${vp.height}`, JSON.stringify(m) + ' 기준 ' + want); await b.close();
  }
  console.log(`== ${pass}/${pass + fail} 통과`);
})();
