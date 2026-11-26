"""PageCraft v12.52.0 — 눈금자·안내선·쪽 번호·개체 이름
기준: v12.51.0 Lite.
 4) 눈금자·안내선: 화면 위·왼쪽 눈금자(page 단위 0~1120·0~790, 배율 따라 눈금 간격). 눈금자에서 끌어 고정 안내선 만들기,
    안내선 끌어 옮기기·페이지 밖(눈금자)으로 끌거나 두 번 눌러 지우기, Esc 취소. 개체 옮기기·크기 조절 때 안내선에 붙음(Alt = 해제)
    켜기/끄기: 화면 위 [눈금자] 단추·Alt+F9·보기 설정 칸(이 PC 기억). 저장값 project.guides={x:[…],y:[…]} — 없으면 필드 없음
 5) 자동 쪽 번호: 페이지 설정 '쪽 번호' 칸 — 모양(3 / 10, 3)·위치(오른쪽·가운데·왼쪽 아래)·첫 페이지 숨김.
    화면·썸네일·발표·발표자 보기·인쇄·PPT(실제 글상자) 같은 그림. 저장값 project.pageNumbers — 끄면 필드 없음
 6) 개체 이름: 선택 머리 이름 두 번 누르기·✎ 단추·F2, 겹친 개체 목록 이름 두 번 누르기 → 이름 칸(Enter 저장·Esc 취소·비우면 자동 이름).
    저장값 o.name(40자) — 이름 없으면 필드 없음. 겹침 목록·선택 머리에 이름 표시
Usage: python3 -I patch/patch_v12520.py <PageCraft_v12.51.0_Lite.html> <out.html>"""
import sys
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
def R(old, new, n=1):
    global html
    c = html.count(old); assert c == n, f'expected {n} got {c}: {old[:80]!r}'
    html = html.replace(old, new)
def cut(a, b):
    """a로 시작해 b로 끝나는 유일한 구간을 잘라 돌려줌(제거)"""
    global html
    assert html.count(a) == 1, ('start', a[:60]); i = html.index(a)
    j = html.index(b, i) + len(b); seg = html[i:j]; html = html[:i] + html[j:]; return seg, i
assert "BUILD_VERSION='PageCraft v12.51.0 · 서식 복사·찾아 바꾸기·최근 쓴 색'" in html, 'needs v12.51.0'
assert 'pc-v12520' not in html, 'already patched'

# ── 1) 변경 ──────────────────────────────────────────────
# CSS는 <style id="pc-ui-css"> 안 해당 구역 규칙을 직접 R()로 고칠 것. 맨 아래 덧붙이기·!important 덧칠 금지.
# 새 JS에는 주석 /*pc-v12520*/ 를 넣어 '이미 적용' 검사가 작동하게 할 것.

# 0) 모델(RModel): 새 필드 정리 — 없는/빈 값은 필드 자체를 지움(옛 문서 데이터 불변)
R("if(!r||!['text','shape','image','line'].includes(c.kind))delete c.rotation;else c.rotation=r;}",
  "if(!r||!['text','shape','image','line'].includes(c.kind))delete c.rotation;else c.rotation=r;}"
  "if('name' in c){const nm=String(c.name??'').replace(/\\s+/g,' ').trim().slice(0,40);if(nm)c.name=nm;else delete c.name;} /*pc-v12520 개체 이름*/")
R("if(!ids.has(project.currentPageId))project.currentPageId=project.pages[0].id;\n return project;\n}",
  "if(!ids.has(project.currentPageId))project.currentPageId=project.pages[0].id;\n"
  " /*pc-v12520 안내선·쪽 번호*/if('guides' in project){const g=project.guides||{},cl=(a,P)=>[...new Set((Array.isArray(a)?a:[]).map(Number).filter(Number.isFinite).map(v=>Math.round(clamp(v,0,P))))].sort((a,b)=>a-b).slice(0,24);const x=cl(g.x,W),y=cl(g.y,H);if(x.length||y.length){project.guides={};if(x.length)project.guides.x=x;if(y.length)project.guides.y=y;}else delete project.guides;}\n"
  " if('pageNumbers' in project){const q=project.pageNumbers;if(!q||typeof q!=='object')delete project.pageNumbers;else project.pageNumbers={fmt:q.fmt==='n'?'n':'nN',pos:['left','center','right'].includes(q.pos)?q.pos:'right',...(q.skipFirst?{skipFirst:true}:{})};}\n"
  " return project;\n}")

# 5) 그리기(RView): 쪽 번호 — 앱이 정한 globalThis.pcPageNumberFor(page)가 글자를 주면 페이지 맨 위에 얹음
R(" for(const o of [...page.objects].sort((a,b)=>a.z-b.z))stage.append(visualObject(o,page,palettes,mode,catalog));\n return stage;\n}",
  " for(const o of [...page.objects].sort((a,b)=>a.z-b.z))stage.append(visualObject(o,page,palettes,mode,catalog));\n"
  " /*pc-v12520 쪽 번호*/{const pn=typeof globalThis.pcPageNumberFor==='function'?globalThis.pcPageNumberFor(page,mode):null;\n"
  "  if(pn){const bw=140,bh=28,bx=pn.pos==='left'?32:pn.pos==='center'?(M.W-bw)/2:M.W-32-bw,by=M.H-20-bh;\n"
  "   const under=sampleTextBackdrop({id:'pc-pagenum',x:bx,y:by,w:bw,h:bh,z:Infinity,style:{}},page,palettes,bx+bw/2,by+bh/2);\n"
  "   const ink=M.isHex(under)?(M.isHex(colors.muted)&&ratio(colors.muted,under)>=4.5?colors.muted:contrastColor(under)):colors.muted;\n"
  "   const n=elt('div','pc-pagenum');n.dataset.pos=pn.pos;n.textContent=pn.text;n.style.color=ink;n.setAttribute('aria-hidden','true');stage.append(n);}}\n"
  " return stage;\n}")

# 썸네일 캐시: 쪽 번호 글자가 바뀌면(페이지 추가·순서·설정) 다시 그림
R("const signature=JSON.stringify(p),previous=thumbCache.get(p.id);",
  "const signature=JSON.stringify(p)+JSON.stringify(pcPnFor(p)),previous=thumbCache.get(p.id);")
# PPT: 쪽 번호는 배경 그림에서 빼고 진짜 글상자로(맨 위)
R("for(const n of [...clone.querySelectorAll('.rv-object')]){if(background||!keep.has(n.dataset.objectId))n.remove();}",
  "for(const n of [...clone.querySelectorAll('.rv-object')]){if(background||!keep.has(n.dataset.objectId))n.remove();}if(background)clone.querySelector('.pc-pagenum')?.remove();")
R("  for(const l of links){slide.addImage(",
  "  {const pn=stage.querySelector('.pc-pagenum'),it=pn&&pxTextItem(pn,rel);if(it){slide.addText(it.runs,it.opts);report.texts++;}} // v12.52 쪽 번호\n"
  "  for(const l of links){slide.addImage(")

# 4) 눈금자: 화면 맞춤 옆 단추 + 그릴 때마다 다시 붙임
R('<button data-action="zoomFit" title="화면 맞춤">맞춤</button></div>',
  '<button data-action="zoomFit" title="화면 맞춤">맞춤</button><button data-action="pcRuler" id="pcRulerBtn" aria-pressed="false" title="눈금자·안내선 보기 (Alt+F9) · 눈금자에서 끌어 안내선 만들기">눈금자</button></div>')
R("case 'zoomFit':fitZoom();break;", "case 'zoomFit':fitZoom();break;case 'pcRuler':pcRulerToggle();break;")
R("markSelection();updateQuickBar();}\nfunction scaleThumbs", "markSelection();updateQuickBar();pcRulerRender();}\nfunction scaleThumbs")
# 개체 옮기기·크기 조절: 안내선도 붙는 자리(눈금자 켜졌을 때만)
R("const cands=[{kind:'page',src:'center',pos:P/2,rank:2}];",
  "const cands=[{kind:'page',src:'center',pos:P/2,rank:2}];for(const g of pcGuideAt(ax))for(const k of ['start','center','end'])cands.push({kind:'guide',src:k,pos:g,rank:0});")
R("if(best.kind!=='page'){", "if(best.kind==='same'||best.kind==='adj'){")
R("if(info.kind==='page'){a=0;b=P;}", "if(info.kind==='page'||info.kind==='guide'){a=0;b=P;}")
R("consider({kind:'page',pos:P/2,rank:2});", "consider({kind:'page',pos:P/2,rank:2});for(const g of pcGuideAt(ax))consider({kind:'guide',pos:g,rank:0});")

# 4) 보기 설정 칸: 눈금자 켜기 + 안내선 모두 지우기
R("모든 개체의 경계를 점선으로 표시</label>",
  "모든 개체의 경계를 점선으로 표시</label>${pcRulerOptions()}")
# 5) 페이지 설정: 쪽 번호 칸(페이지 배경 칸 앞)
R("html+=accordion('page' ,'페이지 배경 · 전환 · 메모',", "html+=pcPnAccordion(accordion);html+=accordion('page' ,'페이지 배경 · 전환 · 메모',")
# 6) 이름: 겹침 목록·선택 머리
R("const fullLabel=String(item.text||item.media?.name||M.TYPE_LABEL[item.kind]||item.kind)",
  "const fullLabel=String(item.name||item.text||item.media?.name||M.TYPE_LABEL[item.kind]||item.kind)")
R("<b style=\"font-size:12px\">${o?V.esc((o.text||o.media?.name||M.TYPE_LABEL[o.kind]).slice(0,27)):'편집할 개체를 선택하세요'}</b>",
  "<b style=\"font-size:12px\" class=\"pc-objname\" ${o&&selectedCount===1?`data-pc-rename=\"${V.esc(o.id)}\" title=\"두 번 눌러 이름 바꾸기 (F2)\"`:''}>${o?V.esc((o.name||o.text||o.media?.name||M.TYPE_LABEL[o.kind]).slice(0,27)):'편집할 개체를 선택하세요'}${o&&selectedCount===1?`<button type=\"button\" class=\"pc-rename-btn\" data-pc-rename-btn=\"${V.esc(o.id)}\" title=\"이름 바꾸기 (F2)\" aria-label=\"개체 이름 바꾸기\">✎</button>`:''}</b>")

# 설정 찾기
R(" ['개체 경계 점선 보기','페이지 설정 › 보기 설정','경계 점선 테두리 보기 안내','page','viewOptions','']];",
  " ['개체 경계 점선 보기','페이지 설정 › 보기 설정','경계 점선 테두리 보기 안내','page','viewOptions',''],\n"
  " ['눈금자·안내선','페이지 설정 › 보기 설정','눈금자 자 안내선 가이드 기준선 눈금','page','viewOptions',''],\n"
  " ['쪽 번호','페이지 설정 › 쪽 번호','쪽번호 페이지 번호 슬라이드 번호 매기기','page','pageNum',''],\n"
  " ['개체 이름 바꾸기','선택 머리 ✎ · 겹친 개체 목록','이름 개체 레이어 F2','','','']];")

# 단축키
R(" {keys:'Ctrl+H',when:'편집 화면(글 편집 중 포함)'",
  " {keys:'Alt+F9',when:'편집 화면',does:'눈금자·안내선 보기 켜기/끄기 (눈금자에서 끌어 안내선 만들기)',where:'pcKeyEditor'},\n"
  " {keys:'F2',when:'개체 하나 선택',does:'개체 이름 바꾸기',where:'pcKeyEditor'},\n"
  " {keys:'Ctrl+H',when:'편집 화면(글 편집 중 포함)'")
R(" if(e.target.closest('input,textarea,select,[contenteditable=true]'))return;\n if((e.ctrlKey||e.metaKey)&&e.shiftKey&&!e.altKey&&(e.code==='KeyC'",
  " if(e.target.closest('input,textarea,select,[contenteditable=true]'))return;\n"
  " if(e.altKey&&!e.ctrlKey&&!e.metaKey&&!e.shiftKey&&e.key==='F9'){e.preventDefault();if(!e.repeat)pcRulerToggle();return;}\n"
  " if(e.key==='F2'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&!e.shiftKey&&st.selected.size===1){e.preventDefault();pcRenameStart([...st.selected][0]);return;}\n"
  " if((e.ctrlKey||e.metaKey)&&e.shiftKey&&!e.altKey&&(e.code==='KeyC'")

NEWJS = r"""/*pc-v12520*/
// ══════ v12.52 · 눈금자·안내선 · 자동 쪽 번호 · 개체 이름 ══════
// 5) 쪽 번호: project.pageNumbers={fmt:'nN'|'n',pos,skipFirst} 있을 때만. 문서 안 페이지만(양식 미리보기 제외)
function pcPnFor(page){const q=st.project?.pageNumbers;if(!q||!page)return null;const P=st.project.pages,i=P.findIndex(x=>x.id===page.id);
 if(i<0||(q.skipFirst&&i===0))return null;return {text:q.fmt==='n'?String(i+1):`${i+1} / ${P.length}`,pos:q.pos||'right'};}
globalThis.pcPageNumberFor=page=>pcPnFor(page);
// 쪽 번호 자리(RView와 같은 셈)가 글·그림 개체와 겹치는 페이지 수 — 켤 때 덜 겹치는 자리 고르기·안내
function pcPnClash(pos,fmt='nN'){const P=st.project.pages;let n=0;P.forEach((pg,i)=>{const t=fmt==='n'?String(i+1):`${i+1} / ${P.length}`,w=Math.min(140,9*t.length+10);
 const x=pos==='left'?32:pos==='center'?560-w/2:1088-w,y=742,h=28;
 if(pg.objects.some(o=>!o.hidden&&!o.unplaced&&o.role!=='template-frame'&&(['image','chart','table','video','flow'].includes(o.kind)||String(o.text||'').trim())&&o.x<x+w&&o.x+o.w>x&&o.y<y+h&&o.y+o.h>y))n++;});return n;}
function pcPnAccordion(accordion){const q=st.project.pageNumbers,on=!!q,v=q||{fmt:'nN',pos:'right'},n=st.project.pages.length,dis=on?'':'disabled';
 const opt=(val,label,cur)=>`<option value="${val}" ${val===cur?'selected':''}>${label}</option>`;
 return accordion('pageNum','쪽 번호 · 문서 전체',`<label class="rv-view-outline-toggle"><input id="pcPnOn" type="checkbox" ${on?'checked':''}> 모든 페이지 아래에 쪽 번호 넣기</label>
  <label class="prop-row"><span>모양</span><select id="pcPnFmt" ${dis}>${opt('nN',`3 / ${n}`,v.fmt)}${opt('n','3',v.fmt)}</select></label>
  <label class="prop-row"><span>위치</span><select id="pcPnPos" ${dis}>${opt('right','오른쪽 아래',v.pos)}${opt('center','가운데 아래',v.pos)}${opt('left','왼쪽 아래',v.pos)}</select></label>
  <label class="rv-view-outline-toggle"><input id="pcPnSkip" type="checkbox" ${v.skipFirst?'checked':''} ${dis}> 첫 페이지(표지)에는 숨기기</label>
  ${on&&pcPnClash(v.pos,v.fmt)?`<p class="inspector-tip pc-pn-warn">이 자리에서 ${pcPnClash(v.pos,v.fmt)}개 페이지의 글·그림과 겹칩니다(양식의 고정 번호 '01' 등). 위치를 바꾸거나 겹치는 글을 지우세요.</p>`:''}<p class="inspector-tip">순서를 바꾸거나 페이지를 더해도 번호가 저절로 맞춰집니다. 화면·발표·인쇄·PPT에 같이 나옵니다 · Ctrl+Z로 되돌리기</p>`);}
function pcPnSet(fn,msg){if(mutate(()=>{fn();}))status(msg+' · Ctrl+Z로 되돌리기');}

// 4) 눈금자·안내선. 보기는 이 PC에 기억(문서 데이터 아님), 안내선 자리는 문서에(project.guides)
var PC_RL={key:'pc-ruler-v1',mem:false,drag:null};
function pcRulerOn(){try{const v=localStorage.getItem(PC_RL.key);if(v!=null)return v==='1';}catch(e){}return PC_RL.mem;}
function pcGuides(){const g=st.project?.guides||{};return {x:Array.isArray(g.x)?g.x:[],y:Array.isArray(g.y)?g.y:[]};}
function pcGuideAt(ax){return pcRulerOn()?pcGuides()[ax]:[];}
function pcRulerToggle(on=!pcRulerOn()){PC_RL.mem=on;try{localStorage.setItem(PC_RL.key,on?'1':'0');}catch(e){}renderCanvas();try{renderInspector();}catch(e){}
 const n=pcGuides().x.length+pcGuides().y.length;status(on?`눈금자 켬 · 위·왼쪽 눈금자에서 끌어 안내선 만들기${n?` · 안내선 ${n}개`:''} · Alt+F9`:'눈금자·안내선 숨김 (안내선은 문서에 그대로) · Alt+F9');}
function pcRulerOptions(){const n=pcGuides().x.length+pcGuides().y.length;
 return `<label class="rv-view-outline-toggle"><input id="pcRulerToggle" type="checkbox" ${pcRulerOn()?'checked':''}> 눈금자·안내선 보기 (Alt+F9)</label><div class="inspect-actions"><button type="button" class="inspect-button" data-pc-guides-clear ${n?'':'disabled'}>안내선 모두 지우기 (${n})</button></div><p class="inspector-tip">눈금자에서 페이지 안으로 끌면 안내선이 생기고, 개체를 옮길 때 안내선에 붙습니다. 안내선을 눈금자 쪽(페이지 밖)으로 끌거나 두 번 누르면 지워집니다.</p>`;}
function pcRulerSvg(len,z,vertical){const major=[50,100,200,500].find(m=>m*z>=48)||500;let minor=major/10;if(minor*z<5)minor=major/5;if(minor*z<5)minor=major/2;
 const L=Math.round(len*z),T=18;let d='',t='';
 for(let v=0;v<=len+.01;v+=minor){const p=Math.round(v*z)+.5,big=Math.abs(v/major-Math.round(v/major))<1e-6,mid=!big&&Math.abs(v/(major/2)-Math.round(v/(major/2)))<1e-6,k=big?T:mid?7:4;
  d+=vertical?`M${T-k} ${p}H${T}`:`M${p} ${T-k}V${T}`;
  if(big&&v>0&&v<len)t+=vertical?`<text x="2" y="${p+10}">${v}</text>`:`<text x="${p+3}" y="10">${v}</text>`;}
 return vertical?`<svg width="${T}" height="${L}" viewBox="0 0 ${T} ${L}" aria-hidden="true"><path d="${d}"/>${t}</svg>`:`<svg width="${L}" height="${T}" viewBox="0 0 ${L} ${T}" aria-hidden="true"><path d="${d}"/>${t}</svg>`;}
function pcRulerRender(){const host=$('#stageHost'),btn=$('#pcRulerBtn'),on=pcRulerOn();btn?.setAttribute('aria-pressed',on?'true':'false');btn?.classList.toggle('is-on',on);
 if(!host)return;host.querySelectorAll(':scope>.pc-ruler').forEach(n=>n.remove());const stage=host.querySelector(':scope>.rv-stage');stage?.querySelector(':scope>.pc-uguides')?.remove();
 $('#stageViewport')?.classList.toggle('pc-ruler-on',on);if(!on||!stage)return;const z=st.zoom||1;
 const top=document.createElement('div');top.className='pc-ruler pc-ruler-top';top.dataset.axis='y';top.title='아래로 끌면 가로 안내선';top.innerHTML=pcRulerSvg(M.W,z,false);
 const left=document.createElement('div');left.className='pc-ruler pc-ruler-left';left.dataset.axis='x';left.title='오른쪽으로 끌면 세로 안내선';left.innerHTML=pcRulerSvg(M.H,z,true);
 const corner=document.createElement('div');corner.className='pc-ruler pc-ruler-corner';corner.setAttribute('aria-hidden','true');host.append(top,left,corner);
 const wrap=document.createElement('div');wrap.className='pc-uguides';wrap.style.setProperty('--gz',1/Math.max(.15,z));const g=pcGuides();
 for(const ax of ['x','y'])g[ax].forEach((v,i)=>{const e=document.createElement('div');e.className='pc-ug pc-ug-'+ax;e.dataset.axis=ax;e.dataset.index=i;e.style[ax==='x'?'left':'top']=v+'px';e.title=`${ax==='x'?'세로':'가로'} 안내선 ${v} · 끌어 옮기기 · 밖으로 끌거나 두 번 눌러 지우기`;wrap.append(e);});
 stage.append(wrap);}
function pcGuidePos(e,ax){const r=$('#stageHost .rv-stage')?.getBoundingClientRect();if(!r)return null;const z=st.zoom||1;return ax==='x'?(e.clientX-r.left)/z:(e.clientY-r.top)/z;}
function pcGuideSet(fn,msg){if(mutate(()=>{const g=pcGuides(),n={x:[...g.x],y:[...g.y]};fn(n);st.project.guides=n;}))status(msg);}
function pcGuideMove(e){const d=PC_RL.drag;if(!d||e.pointerId!==d.pointerId)return;e.preventDefault();const P=d.ax==='x'?M.W:M.H;let v=pcGuidePos(e,d.ax);if(v==null)return;
 v=Math.round(v);const reach=snapReach();let hint='';if(Math.abs(v-P/2)<=reach){v=P/2;hint=' · 가운데';}
 d.out=v<0||v>P;d.v=v;d.el.style[d.ax==='x'?'left':'top']=M.clamp(v,0,P)+'px';d.el.classList.toggle('pc-ug-out',d.out);
 moveBadge(d.out?'놓으면 지움':`${d.ax==='x'?'X':'Y'} ${v}${hint}`,e.clientX+16,e.clientY+20);}
function pcGuideEnd(e,cancel){const d=PC_RL.drag;if(!d||(e&&e.pointerId!==d.pointerId))return;PC_RL.drag=null;
 removeEventListener('pointermove',pcGuideMove,true);removeEventListener('pointerup',pcGuideUp,true);removeEventListener('pointercancel',pcGuideCancel,true);
 $('#rvDragBadge')?.remove();document.documentElement.classList.remove('pc-guide-dragging');
 if(cancel||d.v==null){renderCanvas();if(cancel)status('안내선 끌기 취소');return;}
 const P=d.ax==='x'?M.W:M.H,name=d.ax==='x'?'세로':'가로';
 if(d.index<0){if(d.out){renderCanvas();return;}const have=pcGuides()[d.ax];if(have.includes(d.v)){renderCanvas();status(`${name} 안내선 ${d.v}은 이미 있습니다.`);return;}
  if(have.length>=24){renderCanvas();status('안내선은 방향마다 24개까지입니다.');return;}
  pcGuideSet(n=>n[d.ax].push(d.v),`${name} 안내선 ${d.v} · 개체가 붙습니다 · 밖으로 끌면 지움 · Ctrl+Z로 되돌리기`);return;}
 const old=pcGuides()[d.ax][d.index];
 if(d.out)pcGuideSet(n=>n[d.ax].splice(d.index,1),`${name} 안내선 ${old} 지움 · Ctrl+Z로 되돌리기`);
 else if(d.v!==old)pcGuideSet(n=>{n[d.ax][d.index]=d.v;},`${name} 안내선 ${old} → ${d.v} · Ctrl+Z로 되돌리기`);else d.el.classList.remove('pc-ug-drag','pc-ug-out');} // 제자리 놓기: 다시 그리지 않음(두 번 누르기 살림)
function pcGuideUp(e){pcGuideEnd(e,false);}function pcGuideCancel(e){pcGuideEnd(e,true);}
// 창(window) 잡기 단계: 가려진 손잡이 잡기(v12.39) 등 문서 단계 처리보다 먼저
window.addEventListener('pointerdown',e=>{if(e.button!==0||!pcRulerOn())return;const t=e.target.closest?.('#stageHost .pc-ruler-top,#stageHost .pc-ruler-left,#stageHost .pc-ug');if(!t)return;
 e.preventDefault();e.stopImmediatePropagation();if(st.editing)finishEditing(true);const ax=t.dataset.axis;let el=t,index=-1;
 if(t.classList.contains('pc-ug'))index=Number(t.dataset.index);
 else{const stage=$('#stageHost .rv-stage'),wrap=stage?.querySelector('.pc-uguides');if(!wrap)return;el=document.createElement('div');el.className='pc-ug pc-ug-'+ax+' pc-ug-live';wrap.append(el);}
 PC_RL.drag={ax,index,el,pointerId:e.pointerId,v:null,out:false};el.classList.add('pc-ug-drag');document.documentElement.classList.add('pc-guide-dragging');
 addEventListener('pointermove',pcGuideMove,true);addEventListener('pointerup',pcGuideUp,true);addEventListener('pointercancel',pcGuideCancel,true);pcGuideMove(e);},true);
document.addEventListener('keydown',e=>{if(PC_RL.drag&&e.key==='Escape'){e.preventDefault();e.stopPropagation();pcGuideEnd(null,true);}},true);
window.addEventListener('dblclick',e=>{const t=e.target.closest?.('#stageHost .pc-ug');if(!t)return;e.preventDefault();e.stopImmediatePropagation();const ax=t.dataset.axis,i=Number(t.dataset.index),v=pcGuides()[ax][i];
 if(v!=null)pcGuideSet(n=>n[ax].splice(i,1),`${ax==='x'?'세로':'가로'} 안내선 ${v} 지움 · Ctrl+Z로 되돌리기`);},true);

// 6) 개체 이름: 떠 있는 작은 이름 칸(설정 칸이 다시 그려져도 그대로). Enter 저장 · Esc 취소 · 비우면 자동 이름
var PC_RN={last:null};
function pcRenameStart(id,anchor){const o=current().objects.find(x=>x.id===id);if(!o)return false;if(st.editing)finishEditing(true);$('#pcRenameBox')?.remove();
 const a=anchor||$(`#inspector [data-pc-rename="${CSS.escape(id)}"]`)||$('#inspector .selected-header')||$(`#stageHost [data-object-id="${CSS.escape(id)}"]`);const r=a?.getBoundingClientRect()||{left:innerWidth/2-110,top:120,width:220,height:30};
 const box=document.createElement('div');box.id='pcRenameBox';box.setAttribute('role','dialog');box.setAttribute('aria-label','개체 이름 바꾸기');
 box.innerHTML='<input type="text" maxlength="40" aria-label="개체 이름" placeholder="예: 제목 상자 (비우면 자동 이름)"><small>Enter 저장 · Esc 취소</small>';document.body.append(box);
 const w=Math.max(220,Math.min(320,r.width+24));box.style.width=w+'px';box.style.left=Math.round(M.clamp(r.left-4,8,innerWidth-w-8))+'px';box.style.top=Math.round(M.clamp(r.top-6,8,innerHeight-64))+'px';
 const inp=box.querySelector('input');inp.value=o.name||'';inp.focus();inp.select();let done=false;
 const finish=save=>{if(done)return;done=true;const v=inp.value.replace(/\s+/g,' ').trim().slice(0,40);box.remove();if(!save||v===(o.name||'')){if(!save)status('이름 바꾸기 취소');return;}
  if(mutate(()=>{const t=current().objects.find(x=>x.id===id);if(!t)return;if(v)t.name=v;else delete t.name;})){setSelection([id]);status(v?`이름: ${v} · Ctrl+Z로 되돌리기`:'이름을 지웠습니다 (자동 이름) · Ctrl+Z로 되돌리기');}};
 inp.addEventListener('keydown',e=>{e.stopPropagation();if(e.key==='Enter'){e.preventDefault();finish(true);}else if(e.key==='Escape'){e.preventDefault();finish(false);}});
 inp.addEventListener('blur',()=>finish(true));return true;}
document.addEventListener('click',e=>{const b=e.target.closest?.('#inspector [data-pc-rename-btn]');if(b){e.preventDefault();e.stopPropagation();pcRenameStart(b.dataset.pcRenameBtn,b.closest('.pc-objname'));return;}
 const c=e.target.closest?.('#inspector [data-pc-guides-clear]');if(c){e.preventDefault();e.stopPropagation();const n=pcGuides().x.length+pcGuides().y.length;if(n)pcGuideSet(g=>{g.x=[];g.y=[];},`안내선 ${n}개 모두 지움 · Ctrl+Z로 되돌리기`);return;}
 const l=e.target.closest?.('#inspector [data-layer-select]');if(!l)return;const id=l.dataset.layerSelect,now=performance.now(),last=PC_RN.last;
 if(last&&last.id===id&&now-last.t<450&&Math.hypot(e.clientX-last.x,e.clientY-last.y)<8){PC_RN.last=null;e.preventDefault();e.stopPropagation();pcRenameStart(id,l);return;}
 PC_RN.last={id,t:now,x:e.clientX,y:e.clientY};},true);
document.addEventListener('dblclick',e=>{const t=e.target.closest?.('#inspector .pc-objname[data-pc-rename]');if(!t||e.target.closest('button'))return;e.preventDefault();pcRenameStart(t.dataset.pcRename,t);},true);
// 설정 칸 고르기: 쪽 번호·눈금자
document.addEventListener('change',e=>{const t=e.target;if(!t?.closest?.('#inspector'))return;
 if(t.id==='pcRulerToggle'){pcRulerToggle(t.checked);return;}
 if(t.id==='pcPnOn'){if(t.checked){const pos=['right','left','center'].map(k=>[k,pcPnClash(k)]).sort((a,b)=>a[1]-b[1])[0],nm={right:'오른쪽',left:'왼쪽',center:'가운데'}[pos[0]];
  pcPnSet(()=>{st.project.pageNumbers={fmt:'nN',pos:pos[0]};},`쪽 번호 켬 · ${nm} 아래`+(pos[0]!=='right'?' (오른쪽 아래는 양식 글과 겹쳐서)':'')+(pos[1]?` · ${pos[1]}개 페이지는 글과 겹침`:''));}else pcPnSet(()=>{delete st.project.pageNumbers;},'쪽 번호 끔');return;}
 const q=st.project.pageNumbers;if(!q)return;
 if(t.id==='pcPnFmt')pcPnSet(()=>{st.project.pageNumbers={...q,fmt:t.value==='n'?'n':'nN'};},'쪽 번호 모양 바꿈');
 else if(t.id==='pcPnPos')pcPnSet(()=>{st.project.pageNumbers={...q,pos:t.value};},'쪽 번호 위치 바꿈');
 else if(t.id==='pcPnSkip')pcPnSet(()=>{const n={...q};if(t.checked)n.skipFirst=true;else delete n.skipFirst;st.project.pageNumbers=n;},t.checked?'첫 페이지 쪽 번호 숨김':'첫 페이지에도 쪽 번호');},true);
"""
R("function pcKeyEditor(e){\n", NEWJS + "function pcKeyEditor(e){\n")

# CSS: pc-ui-css 안 해당 구역(v12.27 정렬 안내선 구역 · 겹침 목록 구역 · 바탕 구조)
a = html.find('<style id="pc-ui-css">'); b = html.find('</style>', a); assert a > 0
css = html[a:b]
def C(old, new, n=1):
    global css
    c = css.count(old); assert c == n, f'css expected {n} got {c}: {old[:80]!r}'
    css = css.replace(old, new)
C("#stageHost .rv-stage .pc-gh.pc-gpage{border-top:calc(1px*var(--gz)) dashed var(--pcg)}",
  "#stageHost .rv-stage .pc-gh.pc-gpage{border-top:calc(1px*var(--gz)) dashed var(--pcg)}\n"
  "/* v12.52 눈금자(화면 위·왼쪽, 페이지 단위)·고정 안내선(눈금자에서 끌어 만듦) */\n"
  "#stageHost>.pc-ruler{position:absolute;z-index:3;background:#F8FAFC;color:#64748B;box-shadow:0 0 0 1px #D5DEE8;user-select:none}\n"
  "#stageHost>.pc-ruler svg{display:block;font:500 9px/1 Pretendard,'Malgun Gothic',sans-serif;fill:#64748B}#stageHost>.pc-ruler path{stroke:#94A3B8;stroke-width:1;fill:none}\n"
  "#stageHost>.pc-ruler-top{left:0;right:0;top:-20px;height:18px;cursor:s-resize}#stageHost>.pc-ruler-left{top:0;bottom:0;left:-20px;width:18px;cursor:e-resize}\n"
  "#stageHost>.pc-ruler-corner{left:-20px;top:-20px;width:18px;height:18px}#stageHost>.pc-ruler-top:hover,#stageHost>.pc-ruler-left:hover{background:#EEF4FB}\n"
  "#stageHost .rv-stage>.pc-uguides{position:absolute;inset:0;pointer-events:none;z-index:8000;--pcug:#0891B2}\n"
  "#stageHost .rv-stage .pc-ug{position:absolute;pointer-events:auto}#stageHost .rv-stage .pc-ug::after{content:'';position:absolute;background:var(--pcug);opacity:.75}\n"
  "#stageHost .rv-stage .pc-ug-x{top:0;bottom:0;width:calc(9px*var(--gz));margin-left:calc(-4.5px*var(--gz));cursor:ew-resize}#stageHost .rv-stage .pc-ug-x::after{top:0;bottom:0;left:50%;width:calc(1px*var(--gz));margin-left:calc(-.5px*var(--gz))}\n"
  "#stageHost .rv-stage .pc-ug-y{left:0;right:0;height:calc(9px*var(--gz));margin-top:calc(-4.5px*var(--gz));cursor:ns-resize}#stageHost .rv-stage .pc-ug-y::after{left:0;right:0;top:50%;height:calc(1px*var(--gz));margin-top:calc(-.5px*var(--gz))}\n"
  "#stageHost .rv-stage .pc-ug:hover::after,#stageHost .rv-stage .pc-ug-drag::after{opacity:1;background:#0E7490}#stageHost .rv-stage .pc-ug-out::after{opacity:.3;background:#DC2626}\n"
  ".pc-guide-dragging,.pc-guide-dragging *{cursor:grabbing!important}\n"
  ".stage-viewport.pc-ruler-on{padding-top:25px;padding-left:27px}\n"
  ".zoom-ui #pcRulerBtn{padding:0 8px}.zoom-ui #pcRulerBtn.is-on{background:#E0F2FE;border-color:#7DD3FC;color:#0C4A6E}\n"
  "/* v12.52 자동 쪽 번호(모든 그리기: 화면·썸네일·발표·인쇄·PPT) */\n"
  ".rv-stage>.pc-pagenum{position:absolute;bottom:20px;width:140px;height:28px;line-height:28px;z-index:2147470000;pointer-events:none;font:600 15px/28px Pretendard,'Malgun Gothic',sans-serif;letter-spacing:.02em;font-variant-numeric:tabular-nums;white-space:nowrap}\n"
  ".rv-stage>.pc-pagenum[data-pos=right]{right:32px;text-align:right}.rv-stage>.pc-pagenum[data-pos=center]{left:490px;text-align:center}.rv-stage>.pc-pagenum[data-pos=left]{left:32px;text-align:left}")
# 겹침 목록·선택 머리 구역: 이름 바꾸기 단추 + 떠 있는 이름 칸
C(".rv-layer-name span:last-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}",
  ".rv-layer-name span:last-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}\n"
  "/* v12.52 개체 이름 바꾸기 */\n"
  ".selected-header .pc-objname{display:flex;align-items:center;gap:4px;min-width:0}.pc-objname[data-pc-rename]{cursor:text}\n"
  ".pc-rename-btn{flex:none;border:1px solid #DCE6EF;background:#fff;border-radius:6px;padding:0 5px;height:20px;font-size:11px;line-height:18px;color:#3A6A93}.pc-rename-btn:hover{background:#EEF5FB}\n"
  "#pcRenameBox{position:fixed;z-index:13000;display:grid;gap:3px;padding:6px;background:#fff;border:1px solid #93C5FD;border-radius:9px;box-shadow:0 10px 28px #0F2C4633}\n"
  "#pcRenameBox input{height:30px;min-width:0;padding:0 8px;border:1px solid #CBD5E1;border-radius:7px;font:inherit;font-size:13px;color:#0F172A}#pcRenameBox input:focus{outline:2px solid #93C5FD;border-color:#3B82F6}\n"
  "#pcRenameBox small{font-size:10.5px;color:#475569;padding:0 2px}\n"
  "#inspector .inspector-tip.pc-pn-warn{color:#9A3412;background:#FFF7ED;border-radius:6px;padding:5px 7px}")
html = html[:a] + css + html[b:]

# ── 버전 문자열(BUILD_VERSION·하단 서명. <title>은 v12.46부터 문서 제목이라 안 건드림) ──
R("const BUILD_VERSION='PageCraft v12.51.0 · 서식 복사·찾아 바꾸기·최근 쓴 색';", "const BUILD_VERSION='PageCraft v12.52.0 · 눈금자·안내선·쪽 번호·개체 이름';")
R('Jungmin Jo · PageCraft v12.51.0</span>', 'Jungmin Jo · PageCraft v12.52.0</span>')
open(out, 'w', encoding='utf-8').write(html); print('patched', out, len(html))
