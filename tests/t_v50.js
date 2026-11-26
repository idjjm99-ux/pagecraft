// v12.50.0 시험(노드 Playwright): node tests/t_v50.js <PageCraft_v12.50.0_Lite.html>
// 배율 화면·겹침 이름·CSS 우선순위 정리
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
  // 넓은 화면은 그대로: 머리줄 65, 도구 단추 세로(아이콘 위·글자 아래) 48
  { const m = await p.evaluate(() => { const t = document.querySelector('#app .ribbon .tool-btn'); return { hdr: document.querySelector('.app-header').getBoundingClientRect().height, btn: t.getBoundingClientRect().height, dir: getComputedStyle(t).flexDirection, nav: document.querySelector('.stage-nav').getBoundingClientRect().height }; });
    ok(m.hdr === 65 && m.btn >= 48 && m.dir === 'column' && m.nav === 53, '1500×950: 머리줄·도구 단추·페이지 막대 그대로', JSON.stringify(m)); }
  ok(!p.errs.length, '오류 없음(1500)', JSON.stringify(p.errs));
  await b.close();

  // ── 1) Windows 배율 화면: 노트북 화면 × 배율 − 작업표시줄·Edge 창틀 ≈ 보이는 칸 ──
  const inside = (r, o, t = 1) => r.left >= o.left - t && r.right <= o.right + t && r.top >= o.top - t && r.bottom <= o.bottom + t;
  const sizes = [[1093, 491, '1366×768@125%'], [1024, 600, '1024×768 창'], [1280, 597, '1920×1080@150%'], [1280, 720, '1920×1080@150% 전체화면'], [1366, 657, '1366×768@100%'], [1536, 737, '1920×1080@125%']];
  for (const [w, h, name] of sizes) {
    const { b, p } = await open(file, { width: w, height: h }); const L = `${w}×${h}(${name})`;
    const m = await p.evaluate(() => {
      const R = e => { const r = e.getBoundingClientRect(); return { left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height }; };
      const vp = { left: 0, top: 0, right: innerWidth, bottom: innerHeight };
      const sv = document.querySelector('#stageViewport'), slide = document.querySelector('#stageHost .rv-stage'), insp = document.querySelector('#inspector');
      const rib = document.querySelector('.ribbon'), ribR = R(rib);
      const ctrls = [...rib.querySelectorAll('button,select,input,label')].filter(e => e.offsetParent).map(R);
      const lb = document.querySelector('.left-pane .pane-head b'), lbs = getComputedStyle(lb);
      const pbtn = [...document.querySelectorAll('.page-list-buttons button')].map(e => ({ h: e.getBoundingClientRect().height, lh: parseFloat(getComputedStyle(e).lineHeight) || 16 }));
      const sig = document.querySelector('#rv-app-signature');
      return { docH: document.documentElement.scrollHeight, docW: document.documentElement.scrollWidth, vp,
        hdr: [...document.querySelectorAll('.header-actions > *')].filter(e => e.offsetParent).map(R),
        ctrlOut: ctrls.filter(r => r.right > innerWidth + 1 || r.bottom > ribR.bottom + 1).length, ribH: ribR.height,
        sv: R(sv), slide: R(slide), zoom: document.querySelector('.zoom-ui')?.innerText.match(/\d+%/)?.[0],
        insH: insp.clientHeight, insScroll: getComputedStyle(insp).overflowY,
        lbH: lb.getBoundingClientRect().height, lbFs: parseFloat(lbs.fontSize), pbtn,
        sigFull: sig.scrollWidth <= sig.clientWidth + 1 && R(sig).right <= innerWidth + 1 };
    });
    ok(m.docH <= h + 1 && m.docW <= w + 1, `${L}: 화면 전체 스크롤 없음`, `${m.docW}×${m.docH}`);
    ok(m.hdr.length && m.hdr.every(r => inside(r, m.vp)), `${L}: 머리줄 단추 화면 안`);
    ok(m.ctrlOut === 0, `${L}: 도구줄 단추 잘림 없음`, 'ribbon ' + Math.round(m.ribH) + 'px');
    ok(inside(m.slide, m.sv, 2) && m.slide.bottom <= h, `${L}: 맞춤 배율에서 슬라이드 전체 보임`, `${m.zoom} 슬라이드 ${Math.round(m.slide.width)}×${Math.round(m.slide.height)}, 칸 ${Math.round(m.sv.top)}~${Math.round(m.sv.bottom)}`);
    ok(m.slide.height >= 150, `${L}: 슬라이드 높이 150px 이상`, Math.round(m.slide.height) + 'px');
    ok(m.insH >= 80 && /auto|scroll/.test(m.insScroll), `${L}: 상세 설정 칸 보이고 스크롤됨`, m.insH + 'px');
    ok(m.lbH <= m.lbFs * 1.6, `${L}: 왼쪽 '페이지' 제목 한 줄`, Math.round(m.lbH) + 'px');
    ok(m.pbtn.every(x => x.h <= x.lh * 1.6 + 12), `${L}: [+ 추가]·[전체 삭제] 글자 한 줄`, m.pbtn.map(x => Math.round(x.h)).join(','));
    ok(m.sigFull, `${L}: 하단 서명(버전) 온전히 보임`);
    // 양식 고르기 창: [추가] 단추가 화면 안
    await p.click('[data-action=addPage]'); await p.waitForTimeout(700);
    await p.evaluate(() => document.querySelector('#templateGrid [data-template]')?.click()); await p.waitForTimeout(300);
    const cf = await p.evaluate(() => { const r = document.querySelector('#confirmTemplate').getBoundingClientRect(); return { b: r.bottom, r: r.right, h: r.height }; });
    ok(cf.h > 0 && cf.b <= h + 1 && cf.r <= w + 1, `${L}: 양식 창 [추가] 단추 화면 안`, `${Math.round(cf.r)},${Math.round(cf.b)}`);
    await p.click('[data-action=closeTemplates]'); await p.waitForTimeout(300);
    // 발표: 슬라이드가 화면 안
    await p.click('[data-action=present]'); await p.waitForTimeout(1200);
    const ps = await p.evaluate(() => { const s = [...document.querySelectorAll('#presentation .rv-stage')].find(e => e.offsetParent); if (!s) return null; const r = s.getBoundingClientRect(); return { l: r.left, t: r.top, r: r.right, b: r.bottom }; });
    ok(ps && ps.l >= -1 && ps.t >= -1 && ps.r <= w + 1 && ps.b <= h + 1, `${L}: 발표 슬라이드 화면 안`, JSON.stringify(ps && Object.fromEntries(Object.entries(ps).map(([k, v]) => [k, Math.round(v)]))));
    for (let i = 0; i < 4; i++) { if (await p.evaluate(() => document.querySelector('#presentation').hidden)) break; await p.keyboard.press('Escape'); await p.waitForTimeout(600); }
    ok(!p.errs.length, `${L}: 오류 없음`, JSON.stringify(p.errs));
    await b.close();
  }
  // 축소 단추: 하한 15%, 줄이다 커지지 않음
  { const { b, p } = await open(file, { width: 1093, height: 491 });
    const z = () => p.evaluate(() => parseInt(document.querySelector('.zoom-ui').innerText.match(/(\d+)%/)[1]));
    let prev = await z(), up = false; for (let i = 0; i < 8; i++) { await p.click('[data-action=zoomOut]'); await p.waitForTimeout(120); const c = await z(); if (c > prev) up = true; prev = c; }
    ok(!up && prev === 15, '축소 단추 하한 15%, 누를수록 커지지 않음', prev + '%');
    await p.click('[data-action=zoomFit]'); await p.waitForTimeout(300); ok(await z() < 28, '[맞춤]은 28% 아래로도 맞춤', (await z()) + '%');
    await b.close(); }

  // ── 2) 겹침·순서 목록: 이름 8글자 줄임 없음 ──
  for (const w of [1920, 1366, 1024]) {
    const { b, p } = await open(file, { width: w, height: 900 });
    await p.click('#inspectorTabs [data-inspector-tab=layers]'); await p.waitForTimeout(300);
    // 시험 조건: 첫 페이지 겹친 글상자 이름을 긴 글(20글자)로
    await p.evaluate(() => { const P = Revival.getProject(); const o = P.pages[0].objects.find(o => o.text === '전자 접수 도입'); o.text = '전자 접수 도입 1년 성과 보고서 요약본'; Revival.importProject(P); Revival.go(P.pages[0].id); });
    await p.click('#inspectorTabs [data-inspector-tab=layers]'); await p.waitForTimeout(400);
    const rows = await p.evaluate(() => [...document.querySelectorAll('.rv-layer-row .rv-layer-name')].filter(e => e.offsetParent).map(n => { const s = n.querySelector('span:not(.rv-layer-type)'); return { t: s.textContent, full: n.title, cut: s.scrollWidth > s.clientWidth + 1, w: s.clientWidth }; }));
    const long = rows.filter(r => [...r.full].length > 8);
    ok(long.length > 0, `${w}: 9글자 넘는 이름 있음(시험 조건)`, long.length + '/' + rows.length);
    ok(rows.every(r => r.t === r.full), `${w}: 목록 글자 = 전체 이름(코드로 자르지 않음)`, rows.filter(r => r.t !== r.full).map(r => r.t).slice(0, 2).join(' | '));
    // 칸 폭만큼 보임: 이름 칸에 9글자 이상 들어가는 폭이면 9글자 이상 보여야 함(예전: 8글자+… 고정)
    const fit = await p.evaluate(() => { const s = [...document.querySelectorAll('.rv-layer-row .rv-layer-name span:not(.rv-layer-type)')].find(e => [...e.textContent].length > 8); const c = document.createElement('canvas').getContext('2d'); c.font = getComputedStyle(s).font; const t = [...s.textContent]; let n = 0; while (n < t.length && c.measureText(t.slice(0, n + 1).join('')).width <= s.clientWidth) n++; return { n, w: s.clientWidth, w9: Math.ceil(c.measureText(t.slice(0, 9).join('')).width) }; });
    ok(fit.w < fit.w9 || fit.n >= 9, `${w}: 이름 칸 폭만큼 보임`, `보이는 글자 ${fit.n} · 칸 ${fit.w}px · 9글자 ${fit.w9}px`);
    const s1 = await p.evaluate(() => { const s = document.querySelector('.rv-layer-row .rv-layer-name span:not(.rv-layer-type)'); const c = getComputedStyle(s); return c.textOverflow + '/' + c.whiteSpace + '/' + c.overflow; });
    ok(s1 === 'ellipsis/nowrap/hidden', `${w}: 넘칠 때만 말줄임(…)`, s1);
    ok(!p.errs.length, `${w}: 오류 없음`, JSON.stringify(p.errs)); await b.close();
  }
  console.log(`== ${pass}/${pass + fail} 통과`); process.exit(fail ? 1 : 0);
})().catch(e => { console.log('FAIL 예외 ' + e.message); console.log(`== ${pass}/${pass + fail + 1} 통과`); process.exit(1); });
