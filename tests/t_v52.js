// v12.52.0 시험(노드 Playwright): node tests/t_v52.js <PageCraft_v12.52.0_Lite.html>
// 눈금자·안내선 · 자동 쪽 번호 · 개체 이름
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs'); const os = require('os');
let pass = 0, fail = 0;
const ok = (c, m, x = '') => { c ? pass++ : fail++; console.log((c ? 'PASS ' : 'FAIL ') + m + ' ' + (x || '')); };
const file = path.resolve(process.argv[2]);
async function open(f, vp = { width: 1500, height: 950 }, ctxIn) {
  const b = ctxIn ? null : await chromium.launch(); const ctx = ctxIn || await b.newContext({ viewport: vp, acceptDownloads: true });
  const p = await ctx.newPage(); p.errs = []; p.on('pageerror', e => p.errs.push(e.message)); p.on('dialog', d => d.accept());
  await p.setViewportSize(vp);
  await p.goto('file://' + f); await p.waitForTimeout(1500);
  await p.locator('#presentation button', { hasText: '편집' }).first().click(); await p.waitForTimeout(1200);
  await p.addStyleTag({ content: '.rv-guide{display:none!important;pointer-events:none!important}' });
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  return { b, ctx, p };
}
const pcVer = async (p, file) => { const bv = await p.evaluate(() => Revival.buildVersion()), v = (path.basename(file).match(/v(\d+\.\d+\.\d+)/) || [])[1] || (bv.match(/v(\d+\.\d+\.\d+)/) || [])[1], sig = await p.locator('#rv-app-signature').textContent(); return { v, bv, sig, okV: bv.startsWith('PageCraft v' + v), okSig: sig.includes('v' + v) }; };
(async () => {
  const { b, ctx, p } = await open(file);
  { const r = await pcVer(p, file); ok(r.okV, '버전 = 파일 이름 v' + r.v, r.bv); ok(r.okSig, '서명 버전', r.sig); }
  const statusText = () => p.evaluate(() => document.querySelector('#saveStatus').textContent);
  const proj = () => p.evaluate(() => Revival.getProject());
  const hist = () => p.evaluate(() => Revival.getState().historyLength);
  const km = await p.evaluate(() => Revival.keymap().map(k => k.keys).join('|'));
  ok(km.includes('Alt+F9') && km.includes('F2'), '단축키 표에 Alt+F9·F2');
  const pr0 = await proj();
  ok(!('guides' in pr0) && !('pageNumbers' in pr0) && !pr0.pages.some(q => q.objects.some(o => 'name' in o)), '옛 문서: 새 필드 없음');

  // ───── 4) 눈금자·안내선 ─────
  ok(await p.evaluate(() => !document.querySelector('#stageHost>.pc-ruler') && document.querySelector('#pcRulerBtn')?.getAttribute('aria-pressed') === 'false'), '처음엔 눈금자 꺼짐 · [눈금자] 단추');
  await p.keyboard.press('Alt+F9'); await p.waitForTimeout(300);
  ok(await p.evaluate(() => document.querySelectorAll('#stageHost>.pc-ruler').length === 3 && document.querySelector('#pcRulerBtn').getAttribute('aria-pressed') === 'true'), 'Alt+F9: 눈금자 켬', await statusText());
  ok(await p.evaluate(() => localStorage.getItem('pc-ruler-v1') === '1'), '눈금자 보기는 이 PC에 기억');
  ok(!('guides' in await proj()), '눈금자만 켜면 문서는 그대로');
  const labels = await p.evaluate(() => [...document.querySelectorAll('#stageHost>.pc-ruler-top text')].map(t => +t.textContent));
  ok(labels.length >= 5 && labels.every((v, i) => !i || v > labels[i - 1]), '위 눈금자 숫자 (페이지 단위)', labels.join(','));
  const vb = async () => ({ top: await p.locator('#stageHost>.pc-ruler-top').boundingBox(), left: await p.locator('#stageHost>.pc-ruler-left').boundingBox(), st: await p.locator('#stageHost>.rv-stage').boundingBox(), vp: await p.locator('#stageViewport').boundingBox(), z: await p.evaluate(() => Revival.getState().zoom) });
  let G = await vb();
  ok(G.top.y >= G.vp.y && G.left.x >= G.vp.x && Math.abs(G.top.width - G.st.width) < 2 && Math.abs(G.left.height - G.st.height) < 2, '눈금자: 화면 안 · 페이지 폭·높이와 같음', JSON.stringify([G.top.y, G.vp.y, G.left.x, G.vp.x]));
  // 위 눈금자에서 끌어 가로 안내선(y=200)
  const yOf = v => G.st.y + v * G.z, xOf = v => G.st.x + v * G.z;
  let h0 = await hist();
  await p.mouse.move(G.top.x + 300, G.top.y + 9); await p.mouse.down(); await p.mouse.move(G.top.x + 300, yOf(120), { steps: 4 });
  ok(await p.evaluate(() => /Y \d+/.test(document.querySelector('#rvDragBadge')?.textContent || '') && !!document.querySelector('.pc-ug-live')), '끄는 동안 선·위치 표시');
  await p.mouse.move(G.top.x + 300, yOf(200), { steps: 4 }); await p.mouse.up(); await p.waitForTimeout(300);
  let g = (await proj()).guides; ok(g && g.y && Math.abs(g.y[0] - 200) <= 1 && !g.x, '가로 안내선 생김 (y≈200)', JSON.stringify(g));
  ok((await hist()) === h0 + 1 && /안내선/.test(await statusText()), '안내선 = 되돌리기 한 단계 · 안내', await statusText());
  ok(await p.evaluate(() => document.querySelectorAll('#stageHost .pc-ug-y').length === 1 && !document.querySelector('#rvDragBadge')), '화면에 안내선 1개 · 위치 표시 사라짐');
  // 왼쪽 눈금자 → 세로 안내선, 가운데(560) 근처면 붙음
  await p.mouse.move(G.left.x + 9, G.left.y + 200); await p.mouse.down(); await p.mouse.move(xOf(557), G.left.y + 200, { steps: 5 }); await p.mouse.up(); await p.waitForTimeout(300);
  g = (await proj()).guides; ok(g.x && g.x[0] === 560, '세로 안내선: 페이지 가운데에 붙음 (557→560)', JSON.stringify(g));
  // 안내선 옮기기
  let ug = await p.locator('#stageHost .pc-ug-y').boundingBox();
  await p.mouse.move(ug.x + 200, ug.y + ug.height / 2); await p.mouse.down(); await p.mouse.move(ug.x + 200, yOf(300), { steps: 4 }); await p.mouse.up(); await p.waitForTimeout(300);
  g = (await proj()).guides; ok(Math.abs(g.y[0] - 300) <= 1 && g.y.length === 1, '안내선 끌어 옮기기 (200→300)', JSON.stringify(g));
  // Esc 취소
  ug = await p.locator('#stageHost .pc-ug-y').boundingBox();
  await p.mouse.move(ug.x + 200, ug.y + ug.height / 2); await p.mouse.down(); await p.mouse.move(ug.x + 200, yOf(500), { steps: 3 }); await p.keyboard.press('Escape'); await p.mouse.up(); await p.waitForTimeout(300);
  g = (await proj()).guides; ok(Math.abs(g.y[0] - 300) <= 1, '끄는 중 Esc: 그대로', JSON.stringify(g));
  // 개체가 안내선에 붙음: 글상자 하나를 위쪽 가장자리가 y=300 근처가 되게 끌기
  await p.evaluate(() => Revival.go(Revival.getProject().pages[10].id)); await p.waitForTimeout(400); G = await vb();
  await p.evaluate(() => Revival.makeObject('text')); await p.waitForTimeout(250); await p.keyboard.press('Control+Enter'); await p.waitForTimeout(150);
  const T = (await p.evaluate(() => Revival.getSelected()))[0];
  await p.evaluate(id => { const P = Revival.getProject(), pg = P.pages[10], o = pg.objects.find(o => o.id === id); Object.assign(o, { x: 100, y: 450, w: 300, h: 80 }); Revival.importProject(P); Revival.go(pg.id); Revival.selectOne(id); }, T); await p.waitForTimeout(400);
  const objBox = async id => p.locator(`#stageHost [data-object-id="${id}"]`).boundingBox();
  let ob = await objBox(T);
  // 위쪽 가장자리를 304로: 450 → 304 (Δ -146), 안내선 300에서 4px → 붙음
  await p.mouse.move(ob.x + 40, ob.y + 30); await p.mouse.down(); await p.mouse.move(ob.x + 40, ob.y + 30 - 146 * G.z, { steps: 8 });
  ok(await p.evaluate(() => !!document.querySelector('#stageHost .pc-guides .pc-gh')), '옮기는 중 안내선 맞춤 표시');
  await p.mouse.up(); await p.waitForTimeout(400);
  let to = (await proj()).pages[10].objects.find(o => o.id === T); ok(to.y === 300, '개체 위쪽이 안내선(300)에 붙음', 'y=' + to.y);
  // 세로 안내선(560)에 가운데 맞춤
  ob = await objBox(T);
  await p.mouse.move(ob.x + 40, ob.y + 30); await p.mouse.down(); await p.mouse.move(ob.x + 40 + (562 - 250) * G.z, ob.y + 30, { steps: 8 }); await p.mouse.up(); await p.waitForTimeout(400);
  to = (await proj()).pages[10].objects.find(o => o.id === T); ok(to.x + to.w / 2 === 560 || to.x === 560 || to.x + to.w === 560, '개체가 세로 안내선(560)에 붙음', `x=${to.x} w=${to.w}`);
  // 크기 조절도 붙음: 오른쪽 손잡이를 560 근처로
  await p.evaluate(id => { const P = Revival.getProject(), pg = P.pages[10], o = pg.objects.find(o => o.id === id); Object.assign(o, { x: 100, y: 450, w: 300, h: 80 }); Revival.importProject(P); Revival.go(pg.id); Revival.selectOne(id); }, T); await p.waitForTimeout(400);
  const hd = await p.locator(`#stageHost [data-object-id="${T}"] .rv-obj-handle[data-corner=e]`).boundingBox().catch(() => null);
  if (hd) { await p.mouse.move(hd.x + hd.width / 2, hd.y + hd.height / 2); await p.mouse.down(); await p.mouse.move(hd.x + hd.width / 2 + 157 * G.z, hd.y + hd.height / 2, { steps: 8 }); await p.mouse.up(); await p.waitForTimeout(400);
    to = (await proj()).pages[10].objects.find(o => o.id === T); ok(to.x + to.w === 560, '크기 조절: 오른쪽 끝이 안내선(560)에 붙음', `x=${to.x} w=${to.w}`); }
  else ok(false, '크기 조절 손잡이 찾기');
  // 눈금자 끄면: 안내선 안 보이고 안 붙음, 문서엔 남음
  await p.click('#pcRulerBtn'); await p.waitForTimeout(300);
  ok(await p.evaluate(() => !document.querySelector('#stageHost .pc-ug') && !document.querySelector('#stageHost>.pc-ruler')), '[눈금자] 끄면 눈금자·안내선 숨김');
  ok(((await proj()).guides?.y || []).length === 1, '끄어도 안내선은 문서에 남음');
  await p.evaluate(id => { const P = Revival.getProject(), pg = P.pages[10], o = pg.objects.find(o => o.id === id); Object.assign(o, { x: 100, y: 450, w: 300, h: 80 }); Revival.importProject(P); Revival.go(pg.id); Revival.selectOne(id); }, T); await p.waitForTimeout(400);
  ob = await objBox(T); await p.mouse.move(ob.x + 40, ob.y + 30); await p.mouse.down(); await p.mouse.move(ob.x + 40, ob.y + 30 - 146 * G.z, { steps: 8 }); await p.mouse.up(); await p.waitForTimeout(400);
  to = (await proj()).pages[10].objects.find(o => o.id === T); ok(to.y === 304, '꺼져 있으면 안내선에 안 붙음', 'y=' + to.y);
  await p.click('#pcRulerBtn'); await p.waitForTimeout(300);
  // 안내선 지우기: 밖으로 끌기 / 두 번 누르기 / 모두 지우기 / Ctrl+Z
  G = await vb(); ug = await p.locator('#stageHost .pc-ug-y').boundingBox();
  await p.mouse.move(ug.x + 200, ug.y + ug.height / 2); await p.mouse.down(); await p.mouse.move(ug.x + 200, G.top.y + 5, { steps: 5 });
  ok(/지움/.test(await p.evaluate(() => document.querySelector('#rvDragBadge')?.textContent || '')), '밖으로 끄는 중 "놓으면 지움"');
  await p.mouse.up(); await p.waitForTimeout(300);
  g = (await proj()).guides; ok(g && !g.y && g.x?.length === 1, '눈금자로 끌어 놓으면 지워짐', JSON.stringify(g));
  await p.keyboard.press('Control+z'); await p.waitForTimeout(300);
  ok(((await proj()).guides?.y || []).length === 1, 'Ctrl+Z: 지운 안내선 돌아옴');
  const ux = await p.locator('#stageHost .pc-ug-x').boundingBox(); await p.mouse.dblclick(ux.x + ux.width / 2, ux.y + 300); await p.waitForTimeout(300);
  g = (await proj()).guides; ok(g && !g.x && g.y?.length === 1, '두 번 누르면 지워짐', JSON.stringify(g));
  ok(!(await p.evaluate(() => Revival.getState().editing)), '두 번 눌러도 글 편집 안 열림');
  await p.evaluate(() => { const P = Revival.getProject(); P.guides = { x: [100, 100, 2000, 'a'], y: [] }; Revival.importProject(P); }); await p.waitForTimeout(300);
  ok(JSON.stringify((await proj()).guides) === '{"x":[100,1120]}', '불러올 때 안내선 정리(중복·범위·빈 칸)', JSON.stringify((await proj()).guides));
  await p.evaluate(() => { document.querySelector('#inspectorTabs [data-inspector-tab=page]')?.click(); }); await p.waitForTimeout(250);
  await p.evaluate(() => { const d = document.querySelector('#inspector [data-accordion=viewOptions]'); if (d) d.open = true; }); await p.waitForTimeout(200);
  const clr = p.locator('#inspector [data-pc-guides-clear]');
  ok(await clr.count() === 1 && /\(2\)/.test(await clr.textContent()), '보기 설정: 안내선 모두 지우기 (2)');
  await clr.click(); await p.waitForTimeout(300);
  ok(!('guides' in await proj()), '모두 지우면 guides 필드 없음');
  ok(await p.evaluate(() => document.querySelector('#pcRulerToggle')?.checked === true), '보기 설정 칸 눈금자 체크 = 켬');

  // ───── 5) 자동 쪽 번호 ─────
  await p.evaluate(() => Revival.go(Revival.getProject().pages[0].id)); await p.waitForTimeout(300);
  await p.evaluate(() => { document.querySelector('#inspectorTabs [data-inspector-tab=page]')?.click(); }); await p.waitForTimeout(200);
  await p.evaluate(() => { const d = document.querySelector('#inspector [data-accordion=pageNum]'); if (d) d.open = true; }); await p.waitForTimeout(200);
  ok(await p.locator('#pcPnOn').count() === 1 && await p.locator('#pcPnFmt').isDisabled(), '쪽 번호 칸: 꺼짐 · 모양 칸 잠김');
  h0 = await hist(); await p.locator('#pcPnOn').check(); await p.waitForTimeout(500);
  let pn = (await proj()).pageNumbers; const N = (await proj()).pages.length;
  ok(pn && pn.fmt === 'nN' && ['right', 'left', 'center'].includes(pn.pos) && (await hist()) === h0 + 1, '켜기: pageNumbers 저장 · 되돌리기 한 단계', JSON.stringify(pn) + ' ' + await statusText());
  ok(pn.pos !== 'right', '오른쪽 아래가 양식 번호(01 등)와 겹쳐 다른 자리 고름', pn.pos + ' · ' + await statusText());
  let stTxt = await p.evaluate(() => document.querySelector('#stageHost .pc-pagenum')?.textContent);
  ok(stTxt === `1 / ${N}`, '편집 화면: "1 / N"', stTxt);
  const thumbs = await p.evaluate(() => [...document.querySelectorAll('#pageList .thumb-viewport .pc-pagenum')].map(n => n.textContent));
  ok(thumbs.length === N && thumbs[2] === `3 / ${N}`, '썸네일마다 번호', thumbs.slice(0, 4).join(','));
  // 대비: 어두운 테마 페이지(9쪽)의 번호 색은 밝음
  await p.evaluate(() => { const P = Revival.getProject(); const pg = P.pages[8], base = pg.objects.find(o => o.kind === 'shape') || pg.objects[0]; pg.objects.push({ ...JSON.parse(JSON.stringify(base)), id: 'dark-band-test', kind: 'shape', role: undefined, text: '', textHtml: null, parentId: null, locked: false, x: 0, y: 700, w: 1120, h: 90, z: 1, style: { ...base.style, fill: '#101820', stroke: 'transparent', gradient: null, bgTransparency: 0 } }); Revival.importProject(P); Revival.go(P.pages[0].id); }); await p.waitForTimeout(600);
  const lum = await p.evaluate(() => { const n = [...document.querySelectorAll('#pageList .thumb-viewport .pc-pagenum')][8]; const m = getComputedStyle(n).color.match(/\d+/g).map(Number); return (m[0] * 299 + m[1] * 587 + m[2] * 114) / 1000; });
  const lum1 = await p.evaluate(() => { const n = document.querySelector('#stageHost .pc-pagenum'); const m = getComputedStyle(n).color.match(/\d+/g).map(Number); return (m[0] * 299 + m[1] * 587 + m[2] * 114) / 1000; });
  ok(lum > 150 && lum1 < 130, '번호 색: 밝은 바탕은 어둡게, 어두운 띠(#101820) 위는 밝게', `${lum1|0} / ${lum|0}`);
  // 모양·위치·첫 페이지
  await p.evaluate(() => { document.querySelector('#inspectorTabs [data-inspector-tab=page]')?.click(); const d = document.querySelector('#inspector [data-accordion=pageNum]'); if (d) d.open = true; }); await p.waitForTimeout(250);
  await p.locator('#pcPnFmt').selectOption('n'); await p.waitForTimeout(300);
  ok(await p.evaluate(() => document.querySelector('#stageHost .pc-pagenum')?.textContent) === '1', '모양 "3"');
  await p.locator('#pcPnPos').selectOption('right'); await p.waitForTimeout(300);
  const posR = await p.evaluate(() => { const n = document.querySelector('#stageHost .pc-pagenum'), s = n.closest('.rv-stage'); const a = n.getBoundingClientRect(), b = s.getBoundingClientRect(); return { r: (b.right - a.right) / (b.width / 1120), btm: (b.bottom - a.bottom) / (b.height / 790), pos: n.dataset.pos }; });
  ok(posR.pos === 'right' && Math.abs(posR.r - 32) < 2 && Math.abs(posR.btm - 20) < 2, '위치: 오른쪽 아래 (32·20px)', JSON.stringify(posR));
  ok(await p.locator('#inspector .pc-pn-warn').count() === 0, '"3" 한 글자는 양식 "01"과 안 겹침 → 경고 없음');
  await p.locator('#pcPnFmt').selectOption('nN'); await p.waitForTimeout(250);
  ok(await p.locator('#inspector .pc-pn-warn').count() === 1, '"1 / 11"은 겹침 → 칸에 경고', await p.locator('#inspector .pc-pn-warn').textContent().catch(() => ''));
  await p.locator('#pcPnSkip').check(); await p.waitForTimeout(300);
  ok(await p.evaluate(() => !document.querySelector('#stageHost .pc-pagenum') && [...document.querySelectorAll('#pageList .thumb-viewport')][1].querySelector('.pc-pagenum')?.textContent.startsWith('2 / ')), '첫 페이지 숨김: 1쪽 없음 · 2쪽은 "2 / N"');
  ok((await proj()).pageNumbers.skipFirst === true, 'skipFirst 저장');
  // 페이지 추가·순서 바꾸기 → 번호 저절로
  await p.evaluate(() => Revival.go(Revival.getProject().pages[1].id)); await p.waitForTimeout(250);
  await p.evaluate(() => Revival.clonePage()); await p.waitForTimeout(600);
  const N2 = (await proj()).pages.length;
  const th2 = await p.evaluate(() => [...document.querySelectorAll('#pageList .thumb-viewport')].map(v => v.querySelector('.pc-pagenum')?.textContent || ''));
  ok(N2 === N + 1 && th2[1] === `2 / ${N2}` && th2[N2 - 1] === `${N2} / ${N2}`, '페이지 더하면 전체 수 바뀜 (썸네일도)', th2.slice(0, 3).join(',') + ' … ' + th2[N2 - 1]);
  // 발표
  await p.evaluate(() => Revival.startPresentation()); await p.waitForTimeout(900);
  const prs = await p.evaluate(() => document.querySelector('#presentation .rv-stage .pc-pagenum')?.textContent || '');
  ok(/^\d+ \/ \d+$/.test(prs), '발표 화면에 번호', prs);
  await p.keyboard.press('Escape'); await p.waitForTimeout(500);
  // PPT: 진짜 글상자
  const pptB64 = await p.evaluate(async () => { const { blob } = await RvPptx.build(); const buf = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000)); return btoa(s); });
  const pptx = path.join(os.tmpdir(), 'v52.pptx'); fs.writeFileSync(pptx, Buffer.from(pptB64, 'base64'));
  const { execSync } = require('child_process'); const xdir = path.join(os.tmpdir(), 'v52x'); execSync(`rm -rf ${xdir} && mkdir -p ${xdir} && cd ${xdir} && unzip -oq ${pptx}`);
  const s1 = fs.readFileSync(path.join(xdir, 'ppt/slides/slide1.xml'), 'utf8'), s3 = fs.readFileSync(path.join(xdir, 'ppt/slides/slide3.xml'), 'utf8');
  ok(s3.includes(`>3 / ${N2}<`) && !s1.includes(` / ${N2}<`), 'PPT: 3쪽에 "3 / N" 글상자, 1쪽(숨김)엔 없음');
  // 끄기 → 필드 없음, Ctrl+Z
  await p.evaluate(() => { document.querySelector('#inspectorTabs [data-inspector-tab=page]')?.click(); }); await p.waitForTimeout(200);
  await p.evaluate(() => { const d = document.querySelector('#inspector [data-accordion=pageNum]'); if (d) d.open = true; }); await p.waitForTimeout(200);
  await p.locator('#pcPnOn').uncheck(); await p.waitForTimeout(300); await p.evaluate(() => document.activeElement?.blur());
  ok(!('pageNumbers' in await proj()) && !(await p.evaluate(() => document.querySelector('.pc-pagenum'))), '끄면 pageNumbers 없음 · 번호 사라짐');
  await p.keyboard.press('Control+z'); await p.waitForTimeout(400);
  ok(!!(await proj()).pageNumbers && await p.evaluate(() => document.querySelectorAll('#pageList .pc-pagenum').length > 3), 'Ctrl+Z: 다시 켜짐');
  // 양식 미리보기(문서 밖 페이지)엔 번호 없음
  ok(await p.evaluate(() => typeof pcPageNumberFor === 'function' && pcPageNumberFor({ id: 'nope' }) === null), '문서 밖 페이지엔 번호 없음');

  // ───── 6) 개체 이름 ─────
  await p.evaluate(() => Revival.go(Revival.getProject().pages[3].id)); await p.waitForTimeout(300);
  await p.evaluate(() => Revival.makeObject('text')); await p.waitForTimeout(250); await p.keyboard.press('Control+Enter'); await p.waitForTimeout(150);
  const A = (await p.evaluate(() => Revival.getSelected()))[0];
  await p.evaluate(() => Revival.makeObject('shape')); await p.waitForTimeout(250); await p.keyboard.press('Control+Enter'); await p.waitForTimeout(150);
  const S = (await p.evaluate(() => Revival.getSelected()))[0];
  await p.evaluate(([A, S]) => { const P = Revival.getProject(), pg = P.pages[3], f = id => pg.objects.find(o => o.id === id); Object.assign(f(A), { x: 600, y: 300, w: 300, h: 120 }); Object.assign(f(S), { x: 650, y: 340, w: 300, h: 160 }); Revival.importProject(P); Revival.go(pg.id); Revival.selectOne(A); }, [A, S]); await p.waitForTimeout(400);
  await p.evaluate(() => document.querySelector('#stageViewport').focus());
  await p.keyboard.press('F2'); await p.waitForTimeout(250);
  ok(await p.evaluate(() => document.activeElement?.closest('#pcRenameBox') !== null), 'F2: 이름 칸 열림·글쇠 위치');
  await p.keyboard.type('  제목   상자  '); await p.keyboard.press('Delete'); await p.keyboard.press('Enter'); await p.waitForTimeout(300);
  let oa = (await proj()).pages[3].objects.find(o => o.id === A);
  ok(oa && oa.name === '제목 상자', 'Enter: 이름 저장(띄어쓰기 정리) · Delete는 개체 안 지움', JSON.stringify(oa?.name));
  ok(await p.evaluate(() => document.querySelector('#inspector .pc-objname')?.textContent.includes('제목 상자')), '선택 머리에 이름');
  ok(/이름: 제목 상자/.test(await statusText()), '안내', await statusText());
  // 겹친 개체 목록: 이름 표시 · 두 번 눌러 바꾸기
  await p.evaluate(() => { document.querySelector('#inspectorTabs [data-inspector-tab=layers]')?.click(); }); await p.waitForTimeout(250);
  await p.evaluate(() => { const d = document.querySelector('#inspector [data-accordion=layers]'); if (d) d.open = true; }); await p.waitForTimeout(200);
  const rowA = p.locator(`#inspector [data-layer-select="${A}"]`);
  ok(await rowA.count() === 1 && (await rowA.textContent()).includes('제목 상자'), '겹친 개체 목록에 이름');
  const rowS = p.locator(`#inspector [data-layer-select="${S}"]`); await rowS.dblclick(); await p.waitForTimeout(300);
  ok(await p.evaluate(() => !!document.querySelector('#pcRenameBox input') && document.activeElement === document.querySelector('#pcRenameBox input')), '목록 이름 두 번 누르기: 이름 칸');
  await p.keyboard.type('배경 카드'); await p.keyboard.press('Escape'); await p.waitForTimeout(250);
  ok(!('name' in (await proj()).pages[3].objects.find(o => o.id === S)) && !(await p.evaluate(() => document.querySelector('#pcRenameBox'))), 'Esc: 취소(이름 없음)');
  await p.locator(`#inspector [data-layer-select="${S}"]`).dblclick(); await p.waitForTimeout(300);
  await p.keyboard.type('배경 카드 이름이 아주 길어서 마흔 글자를 넘기는 경우에는 잘라서 저장합니다 끝'); await p.keyboard.press('Enter'); await p.waitForTimeout(300);
  const os2 = (await proj()).pages[3].objects.find(o => o.id === S);
  ok(os2.name && os2.name.length <= 40 && os2.name.startsWith('배경 카드'), '40자까지', os2.name);
  ok((await p.evaluate(() => Revival.getSelected())).join() === S, '이름 바꾼 개체가 선택됨');
  // ✎ 단추 · 비우면 이름 지움 · Ctrl+Z
  h0 = await hist();
  await p.evaluate(() => { document.querySelector('#inspectorTabs [data-inspector-tab=object]')?.click(); }); await p.waitForTimeout(250);
  await p.click('#inspector [data-pc-rename-btn]'); await p.waitForTimeout(250);
  await p.keyboard.press('Control+a'); await p.keyboard.press('Backspace'); await p.keyboard.press('Enter'); await p.waitForTimeout(300);
  ok(!('name' in (await proj()).pages[3].objects.find(o => o.id === S)) && (await hist()) === h0 + 1, '✎ → 비우고 Enter: 이름 필드 지움(자동 이름)');
  await p.keyboard.press('Control+z'); await p.waitForTimeout(300);
  ok((await proj()).pages[3].objects.find(o => o.id === S).name?.startsWith('배경 카드'), 'Ctrl+Z: 이름 돌아옴');
  // 머리 이름 두 번 누르기 · 바깥 누르면 저장
  await p.evaluate(id => Revival.selectOne(id), A); await p.waitForTimeout(200);
  await p.locator('#inspector .pc-objname').dblclick({ position: { x: 8, y: 6 } }); await p.waitForTimeout(250);
  ok(await p.evaluate(() => document.querySelector('#pcRenameBox input')?.value === '제목 상자'), '머리 이름 두 번 누르기: 지금 이름 채워 열림');
  await p.keyboard.press('End'); await p.keyboard.type(' 2'); await p.mouse.click(5, 900); await p.waitForTimeout(300);
  ok((await proj()).pages[3].objects.find(o => o.id === A).name === '제목 상자 2', '칸 밖을 누르면 저장');
  // 복제·저장/불러오기에도 이름 유지, 이름 없는 개체엔 필드 없음
  await p.evaluate(id => Revival.selectOne(id), A); await p.keyboard.press('Control+d'); await p.waitForTimeout(300);
  const cl = (await proj()).pages[3].objects.filter(o => o.name === '제목 상자 2').length; ok(cl === 2, 'Ctrl+D 복제: 이름 같이', String(cl));
  await p.evaluate(() => { const P = Revival.getProject(); P.pages[3].objects[0].name = '   '; Revival.importProject(P); }); await p.waitForTimeout(300);
  ok(!('name' in (await proj()).pages[3].objects[0]), '불러올 때 빈 이름은 필드 지움');
  const nNamed = (await proj()).pages.flatMap(q => q.objects).filter(o => 'name' in o).length; ok(nNamed === 3, '이름 붙인 개체만 name 필드', String(nNamed));
  await p.evaluate(() => Revival.selectOne(null)); await p.waitForTimeout(150); await p.keyboard.press('F2'); await p.waitForTimeout(150);
  ok(!(await p.evaluate(() => document.querySelector('#pcRenameBox'))), '선택 없으면 F2 무시');
  // 설정 찾기
  ok(await p.evaluate(() => { const i = document.querySelector('#pcFindInput'); if (!i) return false; i.value = '쪽 번호'; i.dispatchEvent(new Event('input', { bubbles: true })); return [...document.querySelectorAll('#pcFindList *')].some(n => /쪽 번호/.test(n.textContent)); }), '설정 찾기: "쪽 번호"');
  ok(p.errs.length === 0, '오류 없음', JSON.stringify(p.errs));
  await b.close();

  // ───── 좁은·낮은 화면: [눈금자] 단추·눈금자 화면 안 ─────
  for (const vp of [{ width: 1024, height: 700 }, { width: 1093, height: 491 }, { width: 1280, height: 597 }]) {
    const o2 = await open(file, vp); const q = o2.p;
    await q.keyboard.press('Alt+F9'); await q.waitForTimeout(300); await q.click('[data-action=zoomFit]'); await q.waitForTimeout(300);
    const r = await q.evaluate(() => { const bt = document.querySelector('#pcRulerBtn').getBoundingClientRect(), nav = document.querySelector('.stage-nav').getBoundingClientRect(), vpE = document.querySelector('#stageViewport').getBoundingClientRect(), t = document.querySelector('#stageHost>.pc-ruler-top').getBoundingClientRect(), l = document.querySelector('#stageHost>.pc-ruler-left').getBoundingClientRect();
      return { btnIn: bt.right <= nav.right + .5 && bt.left >= nav.left && bt.width > 20, rulIn: t.top >= vpE.top - .5 && l.left >= vpE.left - .5, sw: document.documentElement.scrollWidth <= innerWidth, sh: document.documentElement.scrollHeight <= innerHeight }; });
    ok(r.btnIn && r.rulIn && r.sw && r.sh, `${vp.width}×${vp.height}: [눈금자] 단추·눈금자 화면 안 · 전체 스크롤 없음`, JSON.stringify(r));
    ok(q.errs.length === 0, `${vp.width}×${vp.height}: 오류 없음`, JSON.stringify(q.errs));
    await o2.b.close();
  }
  console.log(`== ${pass}/${pass + fail} 통과`); process.exit(fail ? 1 : 0);
})().catch(e => { console.log('FAIL 예외 ' + e.message); console.log(`== ${pass}/${pass + fail + 1} 통과`); process.exit(1); });
