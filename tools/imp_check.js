// !important 정리 도우미: pc-ui-css 한 구역의 !important 선언을 하나씩·함께 빼 보며 계산된 스타일이 그대로인지 검사
// 사용: node tools/imp_check.js <Lite.html> "<구역 첫 규칙 선택자(CSSOM 표기)>" "<마지막 규칙 선택자>" <out.json> [WxH, 기본 1500x950]   (약 20~30분)
// 화면 크기 두 가지(1500x950·1024x600) 모두에서 FREE인 것만 뺄 것. 상태 선택자(:hover 등)는 UNMATCHED로 남김
// 결과: FREE/FREE2 = 빼도 됨, NEED = 남김(다른 구역 !important와 겨룸), UNMATCHED = 시험 상태에서 안 쓰여 판정 못 함(빼지 말 것)
// v12.50에서 rv-v12370 구역에 사용. 판정 뒤 cssdump quick으로 옛/새 판 전체 비교 필수
// 2단계: 구역 안 !important 선언(원문 단위)을 함께 빼 보고, 남은 것도 다시 시험, 마지막에 전체 검증
const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
const file=path.resolve(process.argv[2]); const FIRST=process.argv[3], LAST=process.argv[4], OUT=process.argv[5];
const VP=(process.argv[6]||'1500x950').split('x').map(Number); // 화면 크기(v12.51: 1024x600 등 좁은·낮은 화면도 검사)
const SETUP=`(([FIRST,LAST])=>{
  const sh=[...document.styleSheets].find(s=>s.ownerNode&&s.ownerNode.id==='pc-ui-css');
  const all=[]; const walk=(list)=>{for(const r of list){ if(r.cssRules&&!r.selectorText) walk(r.cssRules); else all.push(r);} }; walk(sh.cssRules);
  const i=all.findIndex(r=>r.selectorText===FIRST); let j=-1; for(let k=i;k<all.length;k++) if(all[k].selectorText===LAST){j=k;break;}
  const rules=all.slice(i,j+1).filter(r=>r.style&&r.selectorText);
  // 원문 선언 단위: 규칙 cssText를 다시 파싱하지 않고, 같은 규칙 안 important 긴 이름(longhand)을 짧은 이름으로 묶음
  const decls=[]; rules.forEach((r,ri)=>{ const seen=new Map(); for(let k=0;k<r.style.length;k++){const p=r.style[k]; if(r.style.getPropertyPriority(p)!=='important') continue;
      const sh=(r.cssText.match(new RegExp('(?:^|[;{\\\\s])((?:-webkit-)?[a-z-]+)\\\\s*:[^;]*!important','g'))||[]).map(x=>x.replace(/^[;{\\s]/,'').split(':')[0].trim());
      let key=sh.find(s=>s===p)||sh.find(s=>p.startsWith(s+'-'))||sh.find(s=>(s==='background'&&p.startsWith('background'))||(s==='border'&&p.startsWith('border'))||(s==='padding'&&p.startsWith('padding'))||(s==='border-radius'&&/border-.*-radius/.test(p))||(s==='border-color'&&/border-.*-color/.test(p)))||p;
      if(!seen.has(key)){seen.set(key,decls.length);decls.push({ri,sel:r.selectorText,key,lh:[]});} decls[seen.get(key)].lh.push([p,r.style.getPropertyValue(p)]); } });
  window.__imp={rules,decls}; return decls.map(d=>({sel:d.sel,key:d.key,n:d.lh.length})); })`;
const SNAP=`((sels)=>{ const h=s=>{let x=2166136261;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return x};
  const set=new Set(); for(const sel of sels){ let base=[]; try{ base=[...document.querySelectorAll(sel.replace(/:hover/g,''))]; }catch(e){} for(const e of base){ set.add(e); for(const d of e.querySelectorAll('*')) set.add(d); } }
  const ser=cs=>{let a='';for(let i=0;i<cs.length;i++){a+=cs[i]+':'+cs.getPropertyValue(cs[i])+';'}return a};
  const out=[]; for(const e of set){ out.push(h(ser(getComputedStyle(e))+ser(getComputedStyle(e,'::before'))+ser(getComputedStyle(e,'::after')))); } return {n:set.size,s:out.join(',')}; })`;
const SET=`(([ks,imp])=>{for(const k of ks){const d=__imp.decls[k];for(const [p,v] of d.lh)__imp.rules[d.ri].style.setProperty(p,v,imp?'important':'');}})`;
(async()=>{
  const b=await chromium.launch(); const p=await (await b.newContext({viewport:{width:VP[0],height:VP[1]}})).newPage();
  p.on('dialog',d=>d.dismiss());
  await p.goto('file://'+file); await p.waitForTimeout(1500);
  await p.locator('#presentation button',{hasText:'편집'}).first().click(); await p.waitForTimeout(1200);
  await p.addStyleTag({content:'.rv-guide{display:none!important}'}); await p.keyboard.press('Escape');
  const decls=await p.evaluate(SETUP+'('+JSON.stringify([FIRST,LAST])+')'); console.log('decls',decls.length);
  const states=[];
  const pages=await p.evaluate(()=>Revival.getProject().pages.map(x=>x.id));
  for(const pg of pages) states.push(async()=>{await p.evaluate(i=>Revival.go(i),pg);});
  const kinds=await p.evaluate(()=>{const m={};for(const pg of Revival.getProject().pages)for(const o of pg.objects){const k=o.kind+'/'+(o.role||'');if(!m[k]&&!o.unplaced)m[k]=[pg.id,o.id];}return Object.values(m)});
  for(const [pg,o] of kinds) for(const t of ['object','layers','page']) states.push(async()=>{await p.evaluate(([a,c])=>{Revival.go(a);Revival.selectOne(c)},[pg,o]); await p.click(`#inspectorTabs [data-inspector-tab=${t}]`).catch(()=>{}); });
  states.push(async()=>{await p.click('#inspectorTabs [data-inspector-tab=object]').catch(()=>{}); await p.hover('#inspectorTabs [data-inspector-tab=page]'); });
  for(const acc of ['chart','table','media','flow','toc','timeline','cycle']) states.push(async()=>{ await p.hover(`#inspector details[data-accordion="${acc}"]>summary`,{timeout:500}).catch(()=>{}); });
  states.push(async()=>{await p.hover('#inspector details.accordion>summary').catch(()=>{}); });
  states.push(async()=>{ await p.mouse.move(5,5); await p.keyboard.press('Escape'); await p.click('[data-action=addPage]'); await p.waitForTimeout(800);
    await p.evaluate(()=>{const ids=[...new Set([...document.querySelectorAll('#templateGrid [data-template]')].map(e=>e.dataset.template))];for(const t of ids)document.querySelector(`#templateGrid [data-template="${t}"]`).click();});
    await p.click('#confirmTemplate'); await p.waitForTimeout(2500); });
  for(let i=11;i<80;i++) states.push(async()=>{ await p.evaluate(i=>{const ps=Revival.getProject().pages; if(ps[i]) Revival.go(ps[i].id);},i); });
  // 투명 색 칸 상태: 개체 배경을 투명으로 (가능하면)
  const sels=decls.map(d=>d.sel);
  const allIdx=decls.map((_,k)=>k);
  const matched=new Array(decls.length).fill(false), indivNeed=new Array(decls.length).fill(false);
  const snaps=[]; // 상태별 기준(원본) 스냅샷
  // 1차: 상태마다 기준 기록 + 개별 제거 시험
  for(const st of states){ await st(); await p.waitForTimeout(200);
    const base={}; for(let k=0;k<decls.length;k++){ const r=await p.evaluate(SNAP+'('+JSON.stringify([decls[k].sel])+')'); base[k]=r.s; if(r.n) matched[k]=true;
      if(indivNeed[k]) continue; await p.evaluate(SET+'('+JSON.stringify([[k],false])+')'); const a=await p.evaluate(SNAP+'('+JSON.stringify([decls[k].sel])+')'); await p.evaluate(SET+'('+JSON.stringify([[k],true])+')'); if(a.s!==r.s) indivNeed[k]=true; }
    snaps.push(base); }
  // 2차: 개별로 빠지는 것 모두 뺀 상태에서, 남은 것 하나씩 다시
  // v12.51: :hover·:focus·:active 등 상태 선택자는 상태를 다 재현하지 못하므로 판정하지 않음(남김)
  decls.forEach((d,k)=>{ if(/:(hover|focus|focus-visible|focus-within|active|checked)\b/.test(d.sel)) matched[k]=false; });
  let free=allIdx.filter(k=>matched[k]&&!indivNeed[k]); const need2=new Set();
  const rest=allIdx.filter(k=>matched[k]&&indivNeed[k]);
  await p.reload(); await p.waitForTimeout(1500); await p.locator('#presentation button',{hasText:'편집'}).first().click(); await p.waitForTimeout(1200); await p.addStyleTag({content:'.rv-guide{display:none!important}'}); await p.keyboard.press('Escape');
  await p.evaluate(SETUP+'('+JSON.stringify([FIRST,LAST])+')');
  let bad=new Set();
  for(let si=0;si<states.length;si++){ await states[si](); await p.waitForTimeout(200);
    await p.evaluate(SET+'('+JSON.stringify([free,false])+')');
    for(const k of free){ const a=await p.evaluate(SNAP+'('+JSON.stringify([decls[k].sel])+')'); if(a.s!==snaps[si][k]) bad.add(k); }
    for(const k of rest){ if(need2.has(k)) continue; await p.evaluate(SET+'('+JSON.stringify([[k],false])+')'); const a=await p.evaluate(SNAP+'('+JSON.stringify([decls[k].sel])+')'); await p.evaluate(SET+'('+JSON.stringify([[k],true])+')'); if(a.s!==snaps[si][k]) need2.add(k); }
    await p.evaluate(SET+'('+JSON.stringify([free,true])+')'); }
  const res=decls.map((d,k)=>({...d,matched:matched[k],indivNeed:indivNeed[k],comboBad:bad.has(k),free2:rest.includes(k)&&!need2.has(k)}));
  for(const r of res) console.log((!r.matched?'UNMATCHED ':r.comboBad?'COMBO-BAD ':!r.indivNeed?'FREE ':r.free2?'FREE2 ':'NEED ')+r.sel.slice(0,70)+' { '+r.key+' }');
  fs.writeFileSync(OUT,JSON.stringify(res,null,1)); await b.close();
})();
