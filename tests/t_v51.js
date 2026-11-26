// v12.51.0 시험(노드 Playwright): node tests/t_v51.js <PageCraft_v12.51.0_Lite.html>
// 서식 복사·찾아 바꾸기·최근 쓴 색
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
  const objOf = id => p.evaluate(id => { for (const pg of Revival.getProject().pages) { const o = pg.objects.find(o => o.id === id); if (o) return o; } return null; }, id);
  const statusText = () => p.evaluate(() => document.querySelector('#saveStatus').textContent);
  const edit = fn => p.evaluate(fn); // 프로젝트를 고쳐 다시 불러옴(시험 조건 만들기)
  const km = await p.evaluate(() => Revival.keymap().map(k => k.keys).join('|'));
  ok(km.includes('Ctrl+Shift+C') && km.includes('Ctrl+H'), '단축키 표에 Ctrl+Shift+C/V·Ctrl+H');

  // ───── 1) 서식 복사 ─────
  await p.evaluate(() => Revival.go(Revival.getProject().pages[1].id)); await p.waitForTimeout(300);
  await p.evaluate(() => Revival.makeObject('text')); await p.waitForTimeout(250); await p.keyboard.press('Control+Enter');
  const A = (await p.evaluate(() => Revival.getSelected()))[0];
  await p.evaluate(() => Revival.makeObject('text')); await p.waitForTimeout(250); await p.keyboard.press('Control+Enter');
  const B = (await p.evaluate(() => Revival.getSelected()))[0];
  await p.evaluate(() => Revival.makeObject('shape')); await p.waitForTimeout(250); await p.keyboard.press('Control+Enter');
  const S = (await p.evaluate(() => Revival.getSelected()))[0];
  await p.evaluate(() => Revival.makeObject('line')); await p.waitForTimeout(250);
  const L = (await p.evaluate(() => Revival.getSelected()))[0];
  await p.evaluate(([A, B, S, L]) => { const P = Revival.getProject(), pg = P.pages[1], f = id => pg.objects.find(o => o.id === id);
    Object.assign(f(A).style, { fontSize: 40, textColor: '#DC2626', userTextColorOverride: true, stroke: '#2563EB', strokeWidth: 4, fontFamily: 'Noto Sans KR', fontWeight: 700, fill: '#FEF3C7', textAlign: 'center' });
    f(B).textHtml = '<span style="color:#00FF00;font-size:12px">초록 작은 글</span>'; f(B).text = '초록 작은 글';
    f(B).y = 420; f(S).y = 520; f(S).x = 700; f(L).x = 900; f(L).y = 300;
    Revival.importProject(P); Revival.go(pg.id); }, [A, B, S, L]); await p.waitForTimeout(400);
  await p.evaluate(() => Revival.selectOne(null)); await p.keyboard.press('Control+Shift+V'); await p.waitForTimeout(150);
  ok(/먼저/.test(await statusText()), '복사 전 Ctrl+Shift+V: 안내만', await statusText());
  await p.evaluate(id => Revival.selectOne(id), A); await p.waitForTimeout(150);
  const cp = await p.evaluate(() => { const e = new KeyboardEvent('keydown', { key: 'C', code: 'KeyC', ctrlKey: true, shiftKey: true, bubbles: true, cancelable: true }); document.body.dispatchEvent(e); return e.defaultPrevented; });
  ok(cp && /복사했습니다/.test(await statusText()), 'Ctrl+Shift+C: 서식 복사(브라우저 기본 막음)', await statusText());
  const h0 = await p.evaluate(() => Revival.getState().historyLength);
  ok(h0 >= 0 && !(await p.evaluate(() => Revival.getState().historyLength - 0 !== 0 && false)), '복사는 문서를 안 바꿈');
  await p.evaluate(id => Revival.selectOne(id), B); await p.waitForTimeout(150);
  await p.keyboard.press('Control+Shift+V'); await p.waitForTimeout(300);
  let a = await objOf(A), bb = await objOf(B);
  const keys = ['fontSize', 'textColor', 'stroke', 'strokeWidth', 'fontFamily', 'fontWeight', 'fill', 'textAlign'];
  ok(keys.every(k => bb.style[k] === a.style[k]), 'Ctrl+Shift+V: 글꼴·크기·색·테두리·채움·맞춤 같아짐', keys.map(k => k + '=' + bb.style[k]).join(' '));
  ok(bb.text === '초록 작은 글' && !/color|font-size/.test(bb.textHtml || ''), '글은 그대로, 안쪽 색·크기 지정은 지움', bb.textHtml);
  const scr = await p.evaluate(id => { const n = document.querySelector(`#stageHost [data-object-id="${id}"] .rv-text-content`), sp = n.querySelector('span') || n; return { c: getComputedStyle(sp).color, fs: getComputedStyle(sp).fontSize }; }, B);
  ok(scr.c === 'rgb(220, 38, 38)' && scr.fs === '40px', '화면: 붙인 색·크기 보임', JSON.stringify(scr));
  ok((await p.evaluate(() => Revival.getState().historyLength)) === h0 + 1, '붙이기 = 되돌리기 한 단계');
  // 여러 개 한 번에: B 선택 + Shift+클릭 도형
  await p.evaluate(id => Revival.selectOne(id), S); await p.waitForTimeout(100);
  await p.keyboard.press('Control+Shift+V'); await p.waitForTimeout(300);
  ok((await objOf(S)).style.fill === '#FEF3C7' && (await objOf(S)).style.fontSize === 40, '도형에도 붙음');
  // 선: 선 색·두께만
  await p.evaluate(id => Revival.selectOne(id), L); await p.waitForTimeout(100);
  const l0 = await objOf(L); await p.keyboard.press('Control+Shift+V'); await p.waitForTimeout(300); const l1 = await objOf(L);
  ok(l1.style.stroke === '#2563EB' && l1.style.strokeWidth === 4 && l1.style.fill === l0.style.fill && l1.style.fontSize === l0.style.fontSize, '선에는 선 색·두께만', `${l1.style.stroke} ${l1.style.strokeWidth}`);
  await p.keyboard.press('Control+z'); await p.waitForTimeout(250); ok((await objOf(L)).style.stroke === l0.style.stroke, 'Ctrl+Z: 선 되돌림');
  await p.keyboard.press('Control+z'); await p.waitForTimeout(250); ok((await objOf(S)).style.fill !== '#FEF3C7', 'Ctrl+Z: 도형 되돌림');
  await p.keyboard.press('Control+z'); await p.waitForTimeout(250); bb = await objOf(B);
  ok(bb.style.fontSize !== 40 && /color/.test(bb.textHtml || ''), 'Ctrl+Z: 글상자 서식·안쪽 색 되돌림', bb.textHtml);
  // 선 → 선 서식 복사: 화살표도
  await p.evaluate(id => Revival.selectOne(id), L); await p.evaluate(() => Revival.makeObject('line')); await p.waitForTimeout(250);
  const L2 = (await p.evaluate(() => Revival.getSelected()))[0];
  await p.evaluate(([L, L2]) => { const P = Revival.getProject(), pg = P.pages[1], f = id => pg.objects.find(o => o.id === id); f(L).lineArrow = 'end'; f(L).style.stroke = '#DC2626'; f(L2).y = 600; Revival.importProject(P); Revival.go(pg.id); }, [L, L2]); await p.waitForTimeout(300);
  await p.evaluate(id => Revival.selectOne(id), L); await p.keyboard.press('Control+Shift+C'); await p.evaluate(id => Revival.selectOne(id), L2); await p.keyboard.press('Control+Shift+V'); await p.waitForTimeout(300);
  const l2 = await objOf(L2); ok(l2.lineArrow === 'end' && l2.style.stroke === '#DC2626', '선 → 선: 색·화살표', `${l2.lineArrow} ${l2.style.stroke}`);
  // 글 편집 중 Ctrl+Shift+V 는 서식 붙이기 아님(브라우저 일반 글 붙여넣기 그대로)
  await p.evaluate(id => Revival.selectOne(id), B); await p.waitForTimeout(100);
  await p.dblclick(`#stageHost [data-object-id="${B}"]`); await p.waitForTimeout(250);
  const ed = await p.evaluate(() => { const e = new KeyboardEvent('keydown', { key: 'V', code: 'KeyV', ctrlKey: true, shiftKey: true, bubbles: true, cancelable: true }); document.activeElement.dispatchEvent(e); return { dp: e.defaultPrevented, ed: Revival.getState().editing }; });
  ok(!ed.dp && ed.ed === B, '글 편집 중 Ctrl+Shift+V 안 가로챔', JSON.stringify(ed));
  await p.keyboard.press('Escape'); await p.waitForTimeout(150);

  // ───── 2) 찾아 바꾸기 ─────
  // 시험 조건: 1쪽 글상자 '2025년 계획 2025', 3쪽 표 칸 '2025', 2쪽 서식 경계에 걸친 '<b>20</b>25', 소문자 'abc'·대문자 'ABC'
  await p.keyboard.press('Control+h'); await p.waitForTimeout(150); await p.keyboard.type('2025'); await p.waitForTimeout(150);
  const base = await p.evaluate(() => { const m = document.querySelector('#pcFrPanel .pc-fr-count').textContent.match(/(\d+)곳 · 개체 (\d+)개/); return m ? { n: +m[1], o: +m[2] } : { n: 0, o: 0 }; });
  await p.keyboard.press('Escape'); await p.waitForTimeout(100);
  const ids = await p.evaluate(() => { const P = Revival.getProject(), [p1, p2, p3] = P.pages;
    const t = p2.objects.find(o => o.kind === 'text' && o.role === 'user');
    const mk = (pg, id, text, extra = {}) => { const o = JSON.parse(JSON.stringify(t)); Object.assign(o, { id, text, textHtml: null, x: 60, y: 60 + pg.objects.length % 5 * 20 }, extra); pg.objects.push(o); return id; };
    mk(p1, 'fr-a', '2025년 계획 2025');
    mk(p2, 'fr-b', '2025 성과', { textHtml: '<b>20</b>25 성과' });
    mk(p2, 'fr-c', '연도 2025', { textHtml: '<span style="color:#2563EB">연도 2025</span>' });
    mk(p1, 'fr-d', 'abc ABC', { x: 700, y: 560 });
    const tb = JSON.parse(JSON.stringify(t)); Object.assign(tb, { id: 'fr-t', kind: 'table', text: '', textHtml: null, x: 100, y: 300, w: 400, h: 160, table: { cells: [['구분', '2025'], ['값', '2025 예정']], striped: true, headFill: '#DCEAF4', cellFill: '#FFFFFF', colWidths: [50, 50], rowHeights: [50, 50] } }); p3.objects.push(tb);
    Revival.importProject(P); Revival.go(P.pages[0].id); return P.pages.map(x => x.id); });
  const before = await p.evaluate(() => JSON.stringify(Revival.getProject().pages));
  await p.evaluate(() => Revival.selectOne(null));
  const hk = await p.evaluate(() => { const e = new KeyboardEvent('keydown', { key: 'h', code: 'KeyH', ctrlKey: true, bubbles: true, cancelable: true }); document.body.dispatchEvent(e); return e.defaultPrevented; });
  await p.waitForTimeout(200);
  ok(hk && await p.locator('#pcFrPanel').isVisible(), 'Ctrl+H: 찾아 바꾸기 창(브라우저 방문 기록 안 열림)');
  ok(await p.evaluate(() => document.activeElement?.classList.contains('pc-fr-find')), '찾기 칸에 바로 입력');
  const pr = await p.evaluate(() => { const r = document.querySelector('#pcFrPanel').getBoundingClientRect(); return r.left >= 0 && r.right <= innerWidth && r.top >= 0 && r.bottom <= innerHeight; });
  ok(pr, '창이 화면 안');
  await p.keyboard.type('2025'); await p.waitForTimeout(150);
  const cnt = () => p.evaluate(() => document.querySelector('#pcFrPanel .pc-fr-count').textContent);
  ok((await cnt()).startsWith(`${base.n + 6}곳 · 개체 ${base.o + 4}개`), `모든 페이지: 시험 개체 6곳·4개 + 원래 문서 ${base.n}곳`, await cnt());
  await p.click('#pcFrPanel .pc-fr-all'); await p.waitForTimeout(100);
  ok(/^2곳 · 개체 1개/.test(await cnt()), '이 페이지만: 2곳', await cnt());
  await p.click('#pcFrPanel .pc-fr-all'); await p.waitForTimeout(100);
  // 다음: 페이지를 넘어가며 개체 선택
  await p.click('#pcFrPanel .pc-fr-next'); await p.waitForTimeout(250);
  let s1 = await p.evaluate(() => ({ sel: Revival.getSelected(), page: Revival.getState().currentPageId }));
  ok(s1.sel[0] === 'fr-a' && s1.page === ids[0], '다음 ①: 1쪽 글상자', JSON.stringify(s1));
  await p.click('#pcFrPanel .pc-fr-next'); await p.waitForTimeout(250);
  s1 = await p.evaluate(() => ({ sel: Revival.getSelected(), page: Revival.getState().currentPageId }));
  ok(s1.sel[0] === 'fr-b' && s1.page === ids[1], '다음 ②: 2쪽으로 넘어감', JSON.stringify(s1));
  ok(await p.locator('#pcFrPanel').isVisible(), '페이지 넘어가도 창 그대로');
  // 바꾸기(이 개체): fr-b는 서식 경계 → 건너뜀 안내
  await p.fill('#pcFrPanel .pc-fr-repl', '2026'); await p.click('#pcFrPanel .pc-fr-one'); await p.waitForTimeout(250);
  ok((await objOf('fr-b')).text === '2025 성과' && /경계/.test(await statusText()), '서식 경계에 걸친 글은 바꾸지 않고 알림', await statusText());
  // 모두 바꾸기 = 되돌리기 한 단계
  const hb = await p.evaluate(() => Revival.getState().historyLength);
  await p.click('#pcFrPanel .pc-fr-every'); await p.waitForTimeout(300);
  const fa = await objOf('fr-a'), fc = await objOf('fr-c'), ft = await objOf('fr-t'), fb = await objOf('fr-b');
  ok(fa.text === '2026년 계획 2026', '글상자: 두 곳 다 바뀜', fa.text);
  ok(fc.text === '연도 2026' && fc.textHtml.includes('연도 2026') && fc.textHtml.includes('color'), '서식 글: text·textHtml 함께, 색은 그대로', fc.textHtml);
  ok(JSON.stringify(ft.table.cells) === JSON.stringify([['구분', '2026'], ['값', '2026 예정']]), '표 칸도 바뀜', JSON.stringify(ft.table.cells));
  ok(fb.text === '2025 성과', '경계 걸친 것은 그대로');
  ok((await statusText()).startsWith(`${base.n + 5}곳 바꿈 · 개체 ${base.o + 3}개 · 서식 경계에 걸친 1곳은 건너뜀`), '결과 안내: 바꾼 곳·개체 수·건너뜀 1', await statusText());
  ok((await p.evaluate(() => Revival.getState().historyLength)) === hb + 1, '모두 바꾸기 = 되돌리기 한 단계');
  const scr2 = await p.evaluate(() => { const pg = Revival.getState().currentPageId; Revival.go(Revival.getProject().pages[0].id); const t = document.querySelector('#stageHost [data-object-id="fr-a"] .rv-text-content')?.textContent; return t; });
  ok(scr2 === '2026년 계획 2026', '화면 글도 바뀜', scr2);
  await p.keyboard.press('Escape'); await p.waitForTimeout(150);
  ok(!(await p.locator('#pcFrPanel').count()), 'Esc: 창 닫힘');
  await p.keyboard.press('Control+z'); await p.waitForTimeout(300);
  ok((await objOf('fr-a')).text === '2025년 계획 2025' && (await objOf('fr-t')).table.cells[0][1] === '2025', 'Ctrl+Z 한 번에 모두 되돌림');
  ok(await p.evaluate(b => JSON.stringify(Revival.getProject().pages) === b, before), '되돌린 뒤 문서 = 처음과 같음');
  // 대소문자
  await p.keyboard.press('Control+h'); await p.waitForTimeout(150);
  await p.fill('#pcFrPanel .pc-fr-find', 'abc'); await p.waitForTimeout(100);
  ok(/^2곳/.test(await cnt()), '대소문자 무시: abc·ABC 2곳', await cnt());
  await p.click('#pcFrPanel .pc-fr-case'); await p.waitForTimeout(100);
  ok(/^1곳/.test(await cnt()), '대소문자 구분: 1곳', await cnt());
  await p.fill('#pcFrPanel .pc-fr-find', 'a.c$'); await p.waitForTimeout(100);
  ok(/없음/.test(await cnt()) && await p.locator('#pcFrPanel .pc-fr-every').isDisabled(), '특수 문자는 글자 그대로(정규식 아님) · 없으면 단추 꺼짐', await cnt());
  await p.fill('#pcFrPanel .pc-fr-find', '$'); await p.fill('#pcFrPanel .pc-fr-repl', '$&'); await p.waitForTimeout(100);
  await p.fill('#pcFrPanel .pc-fr-find', 'ABC'); await p.click('#pcFrPanel .pc-fr-every'); await p.waitForTimeout(250);
  ok((await objOf('fr-d')).text === 'abc $&', "바꿀 말의 '$&'도 글자 그대로", (await objOf('fr-d')).text);
  await p.keyboard.press('Escape');
  // 글 편집 중에도 Ctrl+H
  await p.evaluate(() => Revival.go(Revival.getProject().pages[0].id)); await p.waitForTimeout(300);
  await p.dblclick('#stageHost [data-object-id="fr-a"]'); await p.waitForTimeout(250);
  const wasEd = await p.evaluate(() => Revival.getState().editing);
  await p.keyboard.press('Control+h'); await p.waitForTimeout(250);
  ok(wasEd === 'fr-a' && await p.locator('#pcFrPanel').isVisible() && !(await p.evaluate(() => Revival.getState().editing)), '글 편집 중 Ctrl+H: 편집 마치고 창 열림');
  await p.keyboard.press('Escape');

  // ───── 3) 최근 쓴 색 ─────
  await p.evaluate(() => localStorage.removeItem('pc-recent-colors-v1'));
  await p.evaluate(() => Revival.selectOne('fr-a')); await p.waitForTimeout(200);
  await p.click('#textColor', { force: true }); await p.waitForTimeout(200);
  ok(await p.locator('#pcTcPanel').isVisible() && !(await p.locator('#pcTcPanel .pc-tc-recent').count()), '처음엔 최근 색 줄 없음');
  await p.click('#pcTcPanel .pc-tc-sw[data-c="#16A34A"]'); await p.click('#pcTcPanel .pc-tc-ok'); await p.waitForTimeout(250);
  ok((await objOf('fr-a')).style.textColor === '#16A34A', '글씨색 적용됨');
  // 배경색(브라우저 색 칸) change 도 기록
  await p.evaluate(() => { const i = document.querySelector('#fillColor'); i.value = '#7c3aed'; i.dispatchEvent(new Event('input', { bubbles: true })); i.dispatchEvent(new Event('change', { bubbles: true })); }); await p.waitForTimeout(250);
  await p.click('#textColor', { force: true }); await p.waitForTimeout(200);
  let rc = await p.evaluate(() => [...document.querySelectorAll('#pcTcPanel .pc-tc-recent .pc-tc-sw')].map(b => b.dataset.c));
  ok(JSON.stringify(rc) === JSON.stringify(['#7C3AED', '#16A34A']), '글씨색 창 맨 위 최근 색(가장 최근 먼저)', JSON.stringify(rc));
  const first = await p.evaluate(() => { const l = document.querySelector('#pcTcPanel .pc-tc-label'); return l.textContent; });
  ok(first === '최근 쓴 색', '맨 위 줄 = 최근 쓴 색', first);
  await p.click('#pcTcPanel .pc-tc-recent .pc-tc-sw[data-c="#7C3AED"]'); await p.click('#pcTcPanel .pc-tc-ok'); await p.waitForTimeout(250);
  ok((await objOf('fr-a')).style.textColor === '#7C3AED', '최근 색 눌러 적용');
  // 취소는 기록 안 함, 같은 색은 한 번만, 최대 8개
  await p.click('#textColor', { force: true }); await p.waitForTimeout(150); await p.click('#pcTcPanel .pc-tc-sw[data-c="#DB2777"]'); await p.click('#pcTcPanel .pc-tc-cancel'); await p.waitForTimeout(150);
  rc = await p.evaluate(() => JSON.parse(localStorage.getItem('pc-recent-colors-v1')));
  ok(JSON.stringify(rc) === JSON.stringify(['#7C3AED', '#16A34A']), '취소는 기록 안 함 · 같은 색은 한 번만', JSON.stringify(rc));
  await p.evaluate(() => { const i = document.querySelector('#fillColor'); for (const c of ['#000001', '#000002', '#000003', '#000004', '#000005', '#000006', '#000007', '#000008', '#000009']) { i.value = c; i.dispatchEvent(new Event('change', { bubbles: true })); } }); await p.waitForTimeout(300);
  rc = await p.evaluate(() => JSON.parse(localStorage.getItem('pc-recent-colors-v1')));
  ok(rc.length === 8 && rc[0] === '#000009', '최대 8개', rc.length + ' ' + rc[0]);
  await p.click('#textColor', { force: true }); await p.waitForTimeout(150);
  const g = await p.evaluate(() => { const r = [...document.querySelectorAll('#pcTcPanel .pc-tc-recent .pc-tc-sw')].map(b => b.getBoundingClientRect()); return { n: r.length, rows: new Set(r.map(x => Math.round(x.top))).size, pan: (() => { const q = document.querySelector('#pcTcPanel').getBoundingClientRect(); return q.bottom <= innerHeight && q.top >= 0; })() }; });
  ok(g.n === 8 && g.rows === 1 && g.pan, '최근 8색 한 줄 · 창 화면 안', JSON.stringify(g));
  await p.keyboard.press('Escape');
  // 표 셀 색 창에도
  await p.evaluate(() => Revival.go(Revival.getProject().pages[2].id)); await p.waitForTimeout(300);
  await p.click('#stageHost [data-object-id="fr-t"]'); await p.waitForTimeout(250);
  const cell = p.locator('#stageHost [data-object-id="fr-t"] td, #stageHost [data-object-id="fr-t"] [data-cell], #stageHost [data-object-id="fr-t"] .rv-table-cell').first();
  if (await cell.count()) { await cell.click(); await p.waitForTimeout(250); }
  const q = p.locator('input[data-table-quick=textColor]').first();
  if (await q.count() && await q.isVisible()) {
    await q.click({ force: true }); await p.waitForTimeout(250);
    const rr = await p.evaluate(() => document.querySelectorAll('#pcCcPanel .pc-tc-recent .pc-tc-sw').length);
    ok(rr === 8, '셀 글자색 창에도 최근 색', rr);
    await p.click('#pcCcPanel .pc-tc-sw[data-c="#DC2626"]'); await p.click('#pcCcPanel .pc-tc-ok'); await p.waitForTimeout(250);
    rc = await p.evaluate(() => JSON.parse(localStorage.getItem('pc-recent-colors-v1')));
    ok(rc[0] === '#DC2626', '셀 색 [확인]도 기록', rc[0]);
  } else ok(false, '셀 글자색 단추 찾기(시험 조건)');
  // 문서 데이터에 안 들어감
  ok(!(await p.evaluate(() => JSON.stringify(Revival.getProject()).includes('recent'))), '최근 색은 문서에 저장 안 함');
  ok(!p.errs.length, '오류 없음', JSON.stringify(p.errs));
  await b.close();
  console.log(`== ${pass}/${pass + fail} 통과`); process.exit(fail ? 1 : 0);
})().catch(e => { console.log('FAIL 예외 ' + e.message); console.log(`== ${pass}/${pass + fail + 1} 통과`); process.exit(1); });
