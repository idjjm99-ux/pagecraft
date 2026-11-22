// v12.46.0 시험(노드 Playwright): node t_v46.js <PageCraft_v12.46.0_Lite.html>
// 첫 안내 한 번에 닫기 · 저장 메뉴(열기·키보드·바깥 클릭·항목 5종) · 탭 제목 · 서명 버전 · 저장본 다시 열기 중복 없음 · 화면 4종 도구줄
const L=(()=>{const { chromium } = require('playwright');return {
 open:async(file,vp)=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:vp});const p=await ctx.newPage();p.errs=[];p.on('pageerror',e=>p.errs.push(e.message));p.on('dialog',d=>d.accept());await p.goto('file://'+require('path').resolve(file));await p.waitForTimeout(1200);return {b,p};},
 toEdit:async p=>{await p.locator('#presentation button',{hasText:'편집'}).first().click();await p.waitForTimeout(1200);}}})(); const fs=require('fs');
let pass=0,fail=0;const ok=(c,m,x='')=>{c?pass++:fail++;console.log((c?'PASS ':'FAIL ')+m+' '+(x||''));};
const pcVer = async (p, file) => { const bv = await p.evaluate(() => Revival.buildVersion()), v = (require('path').basename(file).match(/v(\d+\.\d+\.\d+)/) || [])[1] || (bv.match(/v(\d+\.\d+\.\d+)/) || [])[1], sig = await p.locator('#rv-app-signature').textContent(); return { v, bv, sig, okV: bv.startsWith('PageCraft v' + v), okSig: sig.includes('v' + v) }; };
(async()=>{
 const file=process.argv[2];
 const {b,p}=await L.open(file,{width:1366,height:768});
 {const t=await p.title(),v=await p.inputValue('#projectTitle');ok(t===v.trim()&&(t.match(/페이지\s?공방/g)||[]).length===1,'탭 제목 = 문서 제목(페이지공방 한 번)',t);}
 await L.toEdit(p);
 // guide: ask → 괜찮아요 → closes at once
 await p.waitForSelector('.rv-guide',{timeout:8000});
 await p.getByRole('button',{name:'괜찮아요'}).click(); await p.waitForTimeout(400);
 ok(!(await p.locator('.rv-guide').count()),'괜찮아요 한 번에 닫힘');
 ok(await p.locator('.rv-guide-btn.pc-pulse').count()===1,'사용법 단추 깜빡임');
 ok((await p.locator('#saveStatus').textContent()).includes('사용법'),'상태줄 안내');
 await p.waitForTimeout(3500); ok(await p.locator('.rv-guide-btn.pc-pulse').count()===0,'깜빡임 끝남');
 {const r=await pcVer(p,file);ok(r.okSig,'서명 버전 = 파일 이름 v'+r.v,r.sig);}
 // header buttons
 const hdr=await p.evaluate(()=>[...document.querySelectorAll('.header-actions > *')].filter(e=>e.offsetParent).map(e=>(e.dataset.action||e.id||e.className)));
 console.log('header:',hdr.join(' | '));
 ok(!(await p.locator('.ribbon #manualRecoveryBtn').count()),'복구 단추 리본에서 빠짐');
 // menu open
 await p.click('.pc-save-toggle'); await p.waitForTimeout(200);
 ok(await p.locator('#pcSavePanel').isVisible(),'메뉴 열림');
 ok(await p.evaluate(()=>document.activeElement.dataset.action)==='saveHTML','첫 항목 포커스');
 const items=await p.evaluate(()=>[...document.querySelectorAll('#pcSavePanel > *')].map(e=>e.dataset.action||e.id||e.className));
 console.log('menu:',items.join(' | '));
 const pr=await p.evaluate(()=>{const r=document.getElementById('pcSavePanel').getBoundingClientRect();return [r.left,r.right,r.bottom,innerWidth]});
 ok(pr[0]>=0&&pr[1]<=pr[3],'메뉴 화면 안', JSON.stringify(pr.map(Math.round)));
 await p.screenshot({path:'v46_menu_1366.png'});
 await p.keyboard.press('ArrowDown'); ok(await p.evaluate(()=>document.activeElement.dataset.action)==='exportPptx','↓ 이동');
 await p.keyboard.press('ArrowUp'); await p.keyboard.press('ArrowUp'); ok(await p.evaluate(()=>document.activeElement.id)==='manualRecoveryBtn','↑ 순환');
 const before=await p.evaluate(()=>JSON.stringify(Revival.getProject().pages.map(x=>x.objects.map(o=>[o.x,o.y]))));
 await p.keyboard.press('Escape'); await p.waitForTimeout(100);
 ok(await p.locator('#pcSavePanel').isHidden(),'Esc 닫힘');
 ok(await p.evaluate(()=>document.activeElement.classList.contains('pc-save-toggle')),'Esc 후 단추 포커스');
 // outside click
 await p.click('.pc-save-toggle'); await p.mouse.click(700,400); await p.waitForTimeout(100);
 ok(await p.locator('#pcSavePanel').isHidden(),'바깥 클릭 닫힘');
 // save HTML via menu
 await p.click('.pc-save-toggle');
 const [dl]=await Promise.all([p.waitForEvent('download',{timeout:15000}),p.click('#pcSavePanel [data-action=saveHTML]')]);
 const path=require('os').tmpdir()+'/saved_v46.html'; await dl.saveAs(path);
 ok(await p.locator('#pcSavePanel').isHidden(),'항목 누르면 닫힘');
 ok(fs.readFileSync(path,'utf8').includes('pcSaveMenu'),'HTML 저장');
 // JSON
 await p.click('.pc-save-toggle');
 const [dj]=await Promise.all([p.waitForEvent('download',{timeout:15000}),p.click('#pcSavePanel [data-action=saveJSON]')]);
 ok(!!dj,'JSON 저장');
 // PPT
 await p.click('.pc-save-toggle');
 const [dp]=await Promise.all([p.waitForEvent('download',{timeout:60000}),p.click('#pcSavePanel [data-action=exportPptx]')]);
 ok(!!dp,'PPT 저장');
 // print
 await p.evaluate(()=>{window.__printed=0;window.print=()=>{window.__printed++}});
 await p.click('.pc-save-toggle'); await p.click('#pcSavePanel [data-action=printDeck]'); await p.waitForTimeout(2500);
 ok(await p.evaluate(()=>window.__printed)>=1,'인쇄 호출');
 // recovery
 await p.click('.pc-save-toggle'); await p.click('#manualRecoveryBtn'); await p.waitForTimeout(300);
 ok((await p.locator('#saveStatus').textContent()).length>0,'복구 단추 동작', await p.locator('#saveStatus').textContent());
 // title sync
 await p.fill('#projectTitle','분기 보고'); await p.waitForTimeout(100);
 ok(await p.title()==='분기 보고 · 페이지공방','제목 입력 → 탭 제목', await p.title());
 // Ctrl+S
 await p.click('#stageViewport',{position:{x:5,y:5}}).catch(()=>{});
 const [ds]=await Promise.all([p.waitForEvent('download',{timeout:15000}),p.keyboard.press('Control+s')]);
 ok(!!ds,'Ctrl+S 저장');
 ok(p.errs.length===0,'오류 없음',JSON.stringify(p.errs));
 await b.close();
 // reopen saved
 const r=await L.open(path,{width:1366,height:768});
 await L.toEdit(r.p);
 const c=await r.p.evaluate(()=>({menus:document.querySelectorAll('#pcSaveMenu').length,print:document.querySelectorAll('.header-actions [data-action=printDeck]').length,ppt:document.querySelectorAll('[data-action=exportPptx]').length,html:document.querySelectorAll('.header-actions [data-action=saveHTML]').length,rec:document.querySelectorAll('#manualRecoveryBtn').length,guideBtn:document.querySelectorAll('[data-action=showGuide]').length,hidden:document.getElementById('pcSavePanel').hidden,title:document.title,pages:Revival.getProject().pages.length}));
 ok(c.menus===1&&c.print===1&&c.ppt===1&&c.html===1&&c.rec===1&&c.guideBtn===1&&c.hidden,'저장본 다시 열기: 중복 없음',JSON.stringify(c));
 await r.p.keyboard.press('Escape');await r.p.keyboard.press('Escape');
 await r.p.click('.pc-save-toggle'); ok(await r.p.locator('#pcSavePanel').isVisible(),'저장본에서 메뉴 열림');
 ok(r.p.errs.length===0,'저장본 오류 없음',JSON.stringify(r.p.errs));
 await r.b.close();
 for (const vp of [{width:1280,height:720},{width:1366,height:768},{width:1500,height:950},{width:1920,height:1080}]) {
  const {b,p}=await L.open(file,vp); await L.toEdit(p); await p.keyboard.press('Escape'); await p.keyboard.press('Escape');
  const m=await p.evaluate(()=>({rows:new Set([...document.querySelectorAll('.ribbon > *')].map(e=>Math.round(e.getBoundingClientRect().top))).size,zoom:document.querySelector('#zoomLabel').textContent}));
  ok(m.rows<=2,`도구줄 2줄 ${vp.width}x${vp.height}`,JSON.stringify(m)); await b.close();
 }
 console.log(`== ${pass}/${pass+fail} 통과`);process.exit(fail?1:0);
})();
