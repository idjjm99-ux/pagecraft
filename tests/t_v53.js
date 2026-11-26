// v12.53.0 시험(노드 Playwright): node tests/t_v53.js <PageCraft_v12.53.0_Lite.html>
// 발표에서 숨기기 · 레이저 포인터 · 등장 효과(애니메이션)
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs'); const os = require('os');
let pass = 0, fail = 0;
const ok = (c, m, x = '') => { c ? pass++ : fail++; console.log((c ? 'PASS ' : 'FAIL ') + m + ' ' + (x || '')); };
const file = path.resolve(process.argv[2]);
async function open(f, vp = { width: 1500, height: 950 }) {
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: vp, acceptDownloads: true });
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
  const { b, ctx, p } = await open(file);
  { const r = await pcVer(p, file); ok(r.okV, '버전 = 파일 이름 v' + r.v, r.bv); ok(r.okSig, '서명 버전', r.sig); }
  const statusText = () => p.evaluate(() => document.querySelector('#saveStatus').textContent);
  const proj = () => p.evaluate(() => Revival.getProject());
  const hist = () => p.evaluate(() => Revival.getState().historyLength);
  const info = () => p.evaluate(() => Revival.presentInfo()); const presentId = async () => (await info()).presentId;
  const km = await p.evaluate(() => Revival.keymap().map(k => k.keys + ' ' + k.does).join('|'));
  ok(/\|L /.test(km) && km.includes('PageDown') && km.includes('레이저'), '단축키 표: L·Space/PageDown·레이저');
  const pr0 = await proj();
  ok(!pr0.pages.some(q => 'hidden' in q || q.objects.some(o => 'anim' in o)), '옛 문서: 새 필드 없음');

  // 시험용 일자(선형) 문서: 예시 문서에서 연결(linkTo)을 빼고 앞 6페이지
  await p.evaluate(() => { const P = Revival.getProject(); P.pages = P.pages.slice(0, 6); for (const q of P.pages) for (const o of q.objects) { o.linkTo = null; } P.currentPageId = P.pages[0].id; Revival.importProject(P); }); await p.waitForTimeout(600);
  const ids = (await proj()).pages.map(q => q.id);
  ok(ids.length === 6 && !(await p.evaluate(() => Object.keys(Revival.navigationSnapshot().parent || {}).length)), '시험 문서: 6페이지 · 연결 없음');

  // ───── 1) 발표에서 숨기기 ─────
  ok(await p.evaluate(() => document.querySelectorAll('#pageList [data-action=pageHide]').length === 6), '페이지 목록: 페이지마다 [숨김] 단추');
  let h0 = await hist();
  await p.locator(`#pageList .page-row[data-page-id="${ids[1]}"]`).hover(); await p.click(`#pageList [data-action=pageHide][data-page-id="${ids[1]}"]`); await p.waitForTimeout(400);
  let P1 = await proj();
  ok(P1.pages[1].hidden === true && (await hist()) === h0 + 1, '[숨김]: 2쪽 hidden=true · 되돌리기 한 단계');
  ok(/2번 페이지를 발표에서 숨김/.test(await statusText()), '안내', await statusText());
  ok(await p.evaluate(id => { const r = document.querySelector(`#pageList .page-row[data-page-id="${id}"]`); return r.classList.contains('pc-pg-hidden') && r.querySelector('[data-action=pageHide]').textContent === '보임' && getComputedStyle(r.querySelector('.thumb-viewport')).opacity < .5; }, ids[1]), '썸네일 흐림 · 단추 "보임"');
  ok(P1.pages.filter(q => 'hidden' in q).length === 1, '숨긴 페이지만 hidden 필드');
  // 페이지 설정 칸: 체크 상자
  await p.evaluate(id => Revival.go(id), ids[1]); await p.waitForTimeout(300);
  await p.evaluate(() => { document.querySelector('#inspectorTabs [data-inspector-tab=page]')?.click(); }); await p.waitForTimeout(200);
  await p.evaluate(() => { const d = document.querySelector('#inspector [data-accordion=page]'); if (d) d.open = true; }); await p.waitForTimeout(200);
  ok(await p.evaluate(() => document.querySelector('#pcPgHide')?.checked === true), '페이지 설정: "발표에서 이 페이지 숨기기" 체크됨');
  // 4쪽도 설정 칸으로 숨김
  await p.evaluate(id => Revival.go(id), ids[3]); await p.waitForTimeout(300);
  await p.evaluate(() => { const d = document.querySelector('#inspector [data-accordion=page]'); if (d) d.open = true; }); await p.waitForTimeout(150);
  await p.locator('#pcPgHide').check(); await p.waitForTimeout(400);
  ok((await proj()).pages[3].hidden === true, '설정 칸 체크: 4쪽 숨김');
  // 발표: 1 → 3 → 5 → 6, 거꾸로 6 → 5 → 3 → 1
  await p.evaluate(id => Revival.go(id), ids[0]); await p.waitForTimeout(200);
  await p.evaluate(() => { document.activeElement?.blur(); Revival.startPresentation(); }); await p.waitForTimeout(800);
  const seq = [await presentId()];
  for (const k of ['ArrowRight', 'Space', 'PageDown', 'ArrowRight']) { await p.keyboard.press(k); await p.waitForTimeout(250); seq.push(await presentId()); }
  ok(seq.join() === [ids[0], ids[2], ids[4], ids[5], ids[5]].join(), '발표 → · Space · PageDown: 숨긴 2·4쪽 건너뜀', seq.map(s => ids.indexOf(s) + 1).join('→'));
  ok(await p.evaluate(() => document.querySelector('#presentation [data-action=nextSlide]').disabled), '마지막: [뒷페이지] 꺼짐');
  const back = [];
  for (const k of ['ArrowLeft', 'PageUp', 'ArrowLeft']) { await p.keyboard.press(k); await p.waitForTimeout(250); back.push(await presentId()); }
  ok(back.join() === [ids[4], ids[2], ids[0]].join(), '← · PageUp: 거꾸로도 건너뜀', back.map(s => ids.indexOf(s) + 1).join('→'));
  ok(await p.evaluate(() => document.querySelector('#presentation [data-action=prevSlide]').disabled), '첫 페이지: [앞페이지] 꺼짐');
  ok((await info()).nextId === ids[2], '발표자 보기 "다음" 미리보기도 건너뜀');
  await p.keyboard.press('Escape'); await p.waitForTimeout(400);
  // 1쪽을 숨기면 '처음(0)'·첫 발표는 첫 보이는 페이지
  await p.locator(`#pageList .page-row[data-page-id="${ids[0]}"]`).hover(); await p.click(`#pageList [data-action=pageHide][data-page-id="${ids[0]}"]`); await p.waitForTimeout(300);
  ok((await info()).firstShown === ids[2], '첫 보이는 페이지 = 3쪽');
  await p.evaluate(id => Revival.go(id), ids[5]); await p.evaluate(() => (document.activeElement?.blur(), Revival.startPresentation())); await p.waitForTimeout(600);
  await p.keyboard.press('0'); await p.waitForTimeout(300);
  ok(await presentId() === ids[2], '발표 0(처음): 숨긴 1쪽 건너 3쪽', String(ids.indexOf(await presentId()) + 1));
  await p.keyboard.press('Escape'); await p.waitForTimeout(400);
  // 숨긴 페이지에서 발표 시작: 그 페이지부터(지금 페이지에서 시작)
  await p.evaluate(id => Revival.go(id), ids[1]); await p.evaluate(() => (document.activeElement?.blur(), Revival.startPresentation())); await p.waitForTimeout(600);
  ok(await presentId() === ids[1], '숨긴 페이지에서 ▶: 그 페이지부터 보임');
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(250);
  ok(await presentId() === ids[2], '거기서 →: 다음 보이는 페이지');
  await p.keyboard.press('Escape'); await p.waitForTimeout(400);
  // 인쇄: 숨긴 3장 빼고 3장
  ok(await p.evaluate(() => Revival.printPageCount()) === 3, '인쇄: 숨긴 페이지 빼고 3장');
  // PPT: 6장 모두, 숨긴 1·2·4쪽은 show="0"
  const pptB64 = await p.evaluate(async () => { const { blob } = await RvPptx.build(); const buf = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000)); return btoa(s); });
  const pptx = path.join(os.tmpdir(), 'v53.pptx'); fs.writeFileSync(pptx, Buffer.from(pptB64, 'base64'));
  const { execSync } = require('child_process'); const xdir = path.join(os.tmpdir(), 'v53x'); execSync(`rm -rf ${xdir} && mkdir -p ${xdir} && cd ${xdir} && unzip -oq ${pptx}`);
  const shows = [1, 2, 3, 4, 5, 6].map(i => { const f = path.join(xdir, `ppt/slides/slide${i}.xml`); return fs.existsSync(f) ? (fs.readFileSync(f, 'utf8').includes(' show="0"') ? 'H' : 'S') : '-'; }).join('');
  ok(shows === 'HHSHSS', 'PPT: 6장 모두 · 숨긴 1·2·4쪽은 숨긴 슬라이드(show=0)', shows);
  // 모두 숨기기 막기
  await p.evaluate(([a, b]) => { Revival.setPageHidden(a, true); Revival.setPageHidden(b, true); }, [ids[2], ids[4]]); await p.waitForTimeout(300);
  ok(!(await proj()).pages[5].hidden && await p.evaluate(id => Revival.setPageHidden(id, true), ids[5]) === false && /모든 페이지를 숨길 수는 없습니다/.test(await statusText()), '마지막 보이는 페이지는 숨길 수 없음', await statusText());
  // 되돌리기 · 다시 보이기 → 필드 없음
  await p.keyboard.press('Control+z'); await p.waitForTimeout(300);
  ok(!(await proj()).pages[4].hidden, 'Ctrl+Z: 5쪽 숨김 되돌림');
  await p.evaluate(ids => { for (const id of ids) Revival.setPageHidden(id, false); }, ids); await p.waitForTimeout(300);
  ok(!(await proj()).pages.some(q => 'hidden' in q), '모두 다시 보이면 hidden 필드 없음');
  ok(await p.evaluate(() => { const P = Revival.getProject(); P.pages[2].hidden = 'yes'; P.pages[3].hidden = 0; Revival.importProject(P); const Q = Revival.getProject(); return Q.pages[2].hidden === true && !('hidden' in Q.pages[3]); }), '불러올 때 정리 (참이면 true, 거짓이면 필드 없음)');
  await p.evaluate(id => Revival.setPageHidden(id, false), ids[2]); await p.waitForTimeout(200);

  // ───── 3) 등장 효과 ─────
  await p.evaluate(id => Revival.go(id), ids[0]); await p.waitForTimeout(300);
  const mk = async kind => { await p.evaluate(k => Revival.makeObject(k), kind); await p.waitForTimeout(250); await p.keyboard.press('Control+Enter'); await p.waitForTimeout(150); return (await p.evaluate(() => Revival.getSelected()))[0]; };
  const A = await mk('text'), B = await mk('shape'), C = await mk('text');
  await p.evaluate(([A, B, C]) => { const P = Revival.getProject(), pg = P.pages[0], f = id => pg.objects.find(o => o.id === id); Object.assign(f(A), { x: 120, y: 200, w: 260, h: 90 }); Object.assign(f(B), { x: 420, y: 200, w: 260, h: 140 }); Object.assign(f(C), { x: 720, y: 200, w: 260, h: 90 }); Revival.importProject(P); Revival.go(pg.id); }, [A, B, C]); await p.waitForTimeout(400);
  const openAnim = async id => { await p.evaluate(id => Revival.selectOne(id), id); await p.waitForTimeout(200); await p.evaluate(() => { document.querySelector('#inspectorTabs [data-inspector-tab=object]')?.click(); }); await p.waitForTimeout(150); await p.evaluate(() => { const d = document.querySelector('#inspector [data-accordion=anim]'); if (d) d.open = true; }); await p.waitForTimeout(150); };
  await openAnim(A);
  ok(await p.evaluate(() => !!document.querySelector('#pcAnFx') && document.querySelector('#pcAnStep').disabled && document.querySelector('[data-pc-an-preview]').disabled), '설정 칸 "등장 효과 · 발표": 처음엔 없음·순서 꺼짐');
  h0 = await hist();
  await p.selectOption('#pcAnFx', 'up'); await p.waitForTimeout(300);
  let oA = (await proj()).pages[0].objects.find(o => o.id === A);
  ok(JSON.stringify(oA.anim) === '{"fx":"up","step":1}' && (await hist()) === h0 + 1, '효과 고르기: anim={fx:up,step:1} · 되돌리기 한 단계', JSON.stringify(oA.anim));
  ok(/아래에서 떠오르기 · 순서 1/.test(await statusText()), '안내', await statusText());
  ok(await p.evaluate(id => document.querySelector(`#stageHost .rv-stage>.rv-object[data-object-id="${id}"]`).getAnimations().length > 0, A), '고르면 편집 화면에서 미리 보기');
  await openAnim(B); await p.selectOption('#pcAnFx', 'fade'); await p.waitForTimeout(300);
  await openAnim(C); await p.selectOption('#pcAnFx', 'zoom'); await p.waitForTimeout(300);
  let objs = (await proj()).pages[0].objects; const st3 = [A, B, C].map(id => objs.find(o => o.id === id).anim.step).join();
  ok(st3 === '1,2,3', '다음 개체는 순서 다음 번호 (1,2,3)', st3);
  await p.fill('#pcAnStep', '2'); await p.press('#pcAnStep', 'Tab'); await p.waitForTimeout(300);
  objs = (await proj()).pages[0].objects;
  ok(objs.find(o => o.id === C).anim.step === 2, '순서 번호 바꾸기: C = 2 (B와 함께)');
  const badges = await p.evaluate(() => [...document.querySelectorAll('#stageHost .pc-an-badge')].map(b => b.textContent).sort().join());
  ok(badges === '1,2,2', '편집 화면 번호 배지', badges);
  ok(await p.evaluate(() => !document.querySelector('#pageList .pc-an-badge,#pageList .pc-an-wait')), '썸네일엔 배지·숨김 없음(다 나타난 모습)');
  await p.click('[data-pc-an-preview]'); await p.waitForTimeout(50);
  ok(await p.evaluate(id => document.querySelector(`#stageHost .rv-stage>.rv-object[data-object-id="${id}"]`).getAnimations().length > 0, C), '▶ 미리 보기');
  // 발표
  await p.evaluate(() => (document.activeElement?.blur(), Revival.startPresentation())); await p.waitForTimeout(900);
  const vis = () => p.evaluate(ids => ids.map(id => { const n = document.querySelector(`#presentationViewport > .rv-stage:not([data-rv-exiting])>.rv-object[data-object-id="${id}"]`); return n ? (getComputedStyle(n).visibility === 'visible' ? 1 : 0) : '-'; }).join(''), [A, B, C]);
  ok(await vis() === '000', '발표 시작: 효과 개체는 안 보임', await vis());
  ok(await p.evaluate(() => { const b = document.querySelector('#presentation [data-action=nextSlide]'); return !b.disabled && /등장 효과/.test(b.title); }), '[뒷페이지] = 다음 등장 효과');
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(60);
  ok(await presentId() === ids[0] && await vis() === '100', '→: 1번(A) 나타남, 같은 페이지', await vis());
  ok(await p.evaluate(id => document.querySelector(`#presentationViewport .rv-object[data-object-id="${id}"]`).getAnimations().length > 0, A), '나타날 때 움직임(애니메이션)');
  await p.waitForTimeout(600);
  await p.keyboard.press('Space'); await p.waitForTimeout(700);
  ok(await vis() === '111', 'Space: 2번(B·C) 함께', await vis());
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(900);
  ok(await presentId() === ids[1], '효과 다 나온 뒤 →: 다음 페이지');
  await p.keyboard.press('ArrowLeft'); await p.waitForTimeout(900);
  ok(await presentId() === ids[0] && await vis() === '111', '←로 돌아오면 다 나타난 모습', await vis());
  await p.keyboard.press('ArrowLeft'); await p.waitForTimeout(200);
  ok(await presentId() === ids[0] && await vis() === '100', '←: 효과 하나씩 되돌림(B·C 숨음)', await vis());
  await p.click('#presentation [data-action=prevSlide]'); await p.waitForTimeout(200);
  ok(await vis() === '000' && await p.evaluate(() => document.querySelector('#presentation [data-action=prevSlide]').disabled), '[앞페이지]: A도 숨음 · 첫 페이지라 꺼짐', await vis());
  await p.click('#presentation [data-action=nextSlide]'); await p.waitForTimeout(700);
  ok(await vis() === '100', '[뒷페이지]: 효과 먼저', await vis());

  // ───── 2) 레이저 포인터 ─────
  const lz = () => p.evaluate(() => { const d = document.querySelector('#pcLaser'); return { on: document.querySelector('#presentation').classList.contains('pc-laser-on'), pressed: document.querySelector('#presentation [data-action=presentLaser]').getAttribute('aria-pressed'), shown: !!d && !d.hidden, t: d?.style.translate || '' }; });
  ok((await lz()).pressed === 'false' && !(await lz()).on, '처음엔 레이저 꺼짐 · 도구줄 [레이저]');
  await p.keyboard.press('l'); await p.waitForTimeout(150);
  await p.mouse.move(600, 500, { steps: 3 }); await p.waitForTimeout(100);
  let L = await lz(); ok(L.on && L.pressed === 'true' && L.shown && L.t === '600px 500px', 'L: 켬 · 마우스 자리에 빨간 점', JSON.stringify(L));
  ok(await p.evaluate(() => getComputedStyle(document.querySelector('#presentationViewport')).cursor === 'none'), '레이저 켜면 화면 커서 숨김');
  const tb = await p.locator('#presentation [data-action=presentLaser]').boundingBox();
  await p.mouse.move(tb.x + tb.width / 2, tb.y + tb.height / 2, { steps: 3 }); await p.waitForTimeout(100);
  ok(!(await lz()).shown, '도구줄 위에선 점 숨김');
  await p.keyboard.press('Escape'); await p.waitForTimeout(200);
  L = await lz(); ok(!L.on && !L.shown && await p.evaluate(() => !document.querySelector('#presentation').hidden), 'Esc: 레이저만 끔(발표 계속)');
  await p.click('#presentation [data-action=presentLaser]'); await p.waitForTimeout(150);
  ok((await lz()).on, '[레이저] 단추로 켬');
  // 발표자 보기: L·[레이저], '지금 화면' 위 움직임 → 청중 화면 같은 자리
  const [pv] = await Promise.all([ctx.waitForEvent('page'), p.click('#presentation [data-action=presenterView]')]); await pv.waitForTimeout(900);
  ok(await pv.evaluate(() => document.querySelector('#pvLaser')?.getAttribute('aria-pressed') === 'true' && document.body.classList.contains('pv-laser-on')), '발표자 보기: [레이저] 켜진 상태 같이');
  ok(await pv.evaluate(() => /효과 1\/2/.test(document.querySelector('#pvCount').textContent) && /같은 페이지 · 효과 2\/2/.test(document.querySelector('#pvNextTitle').textContent)), '발표자 보기: 효과 1/2 · 다음 = 같은 페이지 효과 2', await pv.evaluate(() => document.querySelector('#pvCount').textContent + ' | ' + document.querySelector('#pvNextTitle').textContent));
  ok(await pv.evaluate(ids => { const s = document.querySelector('#pvCur .rv-stage'), n = id => s.querySelector(`.rv-object[data-object-id="${id}"]`); return getComputedStyle(n(ids[1])).visibility === 'visible' && +getComputedStyle(n(ids[1])).opacity < .5 && +getComputedStyle(n(ids[0])).opacity > .9; }, [A, B, C]), '발표자 "지금 화면": 아직 안 나온 개체는 흐리게');
  const cur = await pv.locator('#pvCur .rv-stage').boundingBox();
  await pv.mouse.move(cur.x + cur.width * .25, cur.y + cur.height * .5, { steps: 3 }); await p.waitForTimeout(150);
  const ms = await p.locator('#presentationViewport > .rv-stage').first().boundingBox(); L = await lz();
  const [lx, ly] = L.t.split(' ').map(parseFloat);
  ok(L.shown && Math.abs(lx - (ms.x + ms.width * .25)) < 4 && Math.abs(ly - (ms.y + ms.height * .5)) < 4, '발표자 화면 위 움직임 → 청중 화면 같은 자리에 점', `${L.t} vs ${(ms.x + ms.width * .25).toFixed(0)} ${(ms.y + ms.height * .5).toFixed(0)}`);
  await pv.keyboard.press('l'); await pv.waitForTimeout(150);
  ok(!(await lz()).on && await pv.evaluate(() => document.querySelector('#pvLaser').getAttribute('aria-pressed') === 'false'), '발표자 창 L: 레이저 끔(두 창 같이)');
  await pv.keyboard.press('ArrowRight'); await p.waitForTimeout(700);
  ok(await vis() === '111' && await pv.evaluate(() => /효과 2\/2/.test(document.querySelector('#pvCount').textContent)), '발표자 창 →: 청중 화면 효과 진행', await vis());
  await pv.click('#pvLaser'); await p.waitForTimeout(150);
  ok((await lz()).on, '발표자 창 [레이저] 단추');
  await p.keyboard.press('Escape'); await p.waitForTimeout(200); await p.keyboard.press('Escape'); await p.waitForTimeout(600);
  ok(await p.evaluate(() => document.querySelector('#presentation').hidden) && !(await lz()).on, 'Esc 두 번: 레이저 끔 → 발표 끝');
  await p.evaluate(() => (document.activeElement?.blur(), Revival.startPresentation())); await p.waitForTimeout(500);
  ok(!(await lz()).on, '다시 발표: 레이저는 꺼진 채 시작');
  await p.keyboard.press('Escape'); await p.waitForTimeout(500);

  // 효과 없애기 · 정리 · 복제
  await openAnim(B); await p.selectOption('#pcAnFx', ''); await p.waitForTimeout(300);
  ok(!('anim' in (await proj()).pages[0].objects.find(o => o.id === B)), '"없음": anim 필드 지움');
  await p.keyboard.press('Control+z'); await p.waitForTimeout(300);
  ok((await proj()).pages[0].objects.find(o => o.id === B).anim?.fx === 'fade', 'Ctrl+Z: 효과 돌아옴');
  await p.evaluate(id => Revival.selectOne(id), A); await p.keyboard.press('Control+d'); await p.waitForTimeout(300);
  ok((await proj()).pages[0].objects.filter(o => o.anim?.fx === 'up').length === 2, 'Ctrl+D 복제: 효과 같이');
  ok(await p.evaluate(() => { const P = Revival.getProject(), o = P.pages[0].objects; o[0].anim = { fx: 'spin', step: 1 }; o[1].anim = { fx: 'wipe', step: 500 }; o[2].anim = null; Revival.importProject(P); const Q = Revival.getProject().pages[0].objects; return !('anim' in Q[0]) && Q[1].anim.step === 99 && !('anim' in Q[2]); }), '불러올 때 정리 (모르는 효과·빈 값 지움, 순서 1~99)');
  await openAnim(A);
  const nAll = (await proj()).pages[0].objects.filter(o => o.anim).length;
  await p.click('[data-pc-an-clear]'); await p.waitForTimeout(300);
  ok(nAll > 0 && !(await proj()).pages[0].objects.some(o => 'anim' in o) && !(await p.evaluate(() => document.querySelector('#stageHost .pc-an-badge'))), '"이 페이지 효과 모두 없애기"', String(nAll));
  // 설정 찾기
  ok(await p.evaluate(() => { const i = document.querySelector('#pcFindInput'); if (!i) return false; i.value = '애니메이션'; i.dispatchEvent(new Event('input', { bubbles: true })); return [...document.querySelectorAll('#pcFindList *')].some(n => /등장 효과/.test(n.textContent)); }), '설정 찾기: "애니메이션" → 등장 효과');
  ok(p.errs.length === 0, '오류 없음', JSON.stringify(p.errs));
  await b.close();

  // ───── 좁은·낮은 화면: 발표 도구줄 [레이저]·페이지 목록 [숨김] 화면 안 ─────
  for (const vp of [{ width: 1024, height: 700 }, { width: 1093, height: 491 }, { width: 1280, height: 597 }, { width: 1920, height: 1080 }]) {
    const o2 = await open(file, vp); const q = o2.p;
    const r1 = await q.evaluate(() => { const row = document.querySelector('#pageList .page-row.active'), h = row.querySelector('[data-action=pageHide]').getBoundingClientRect(), d = row.querySelector('[data-action=pageDelete]').getBoundingClientRect(), pane = document.querySelector('#pageList').getBoundingClientRect();
      return { inPane: h.left >= pane.left - .5 && d.right <= pane.right + .5 && h.width > 16, oneLine: Math.abs(h.top - d.top) < 2 && [...row.querySelectorAll('.page-actions button')].every(x => x.getBoundingClientRect().height < 28) }; });
    ok(r1.inPane && r1.oneLine, `${vp.width}×${vp.height}: 페이지 단추 5개 한 줄(글자 안 꺾임)·칸 안`, JSON.stringify(r1));
    await q.evaluate(() => (document.activeElement?.blur(), Revival.startPresentation())); await q.waitForTimeout(700);
    const r2 = await q.evaluate(() => { const bs = [...document.querySelectorAll('#presentation .presentation-top button')].filter(b => b.offsetParent), l = document.querySelector('#presentation [data-action=presentLaser]').getBoundingClientRect();
      return { all: bs.every(b => { const r = b.getBoundingClientRect(); return r.right <= innerWidth + .5 && r.left >= -.5 && r.bottom <= innerHeight; }), lz: l.width > 20 && l.right <= innerWidth, sw: document.documentElement.scrollWidth <= innerWidth }; });
    ok(r2.all && r2.lz && r2.sw, `${vp.width}×${vp.height}: 발표 도구줄 단추 모두 화면 안 ([레이저] 포함)`, JSON.stringify(r2));
    ok(q.errs.length === 0, `${vp.width}×${vp.height}: 오류 없음`, JSON.stringify(q.errs));
    await o2.b.close();
  }
  console.log(`== ${pass}/${pass + fail} 통과`); process.exit(fail ? 1 : 0);
})().catch(e => { console.log('FAIL 예외 ' + e.message); console.log(`== ${pass}/${pass + fail + 1} 통과`); process.exit(1); });
