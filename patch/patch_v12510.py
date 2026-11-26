"""PageCraft v12.51.0 — 서식 복사·찾아 바꾸기·최근 쓴 색
기준: v12.50.0 Lite.
 1) 서식 복사: Ctrl+Shift+C(선택 개체 1개의 서식) → Ctrl+Shift+V(선택 개체들에 붙임, 한 번에 되돌리기)
    글상자·도형·선. 선↔다른 개체는 선 색·두께만. 붙일 때 글 안쪽 색·크기·글꼴 지정은 지워 바깥 서식이 보이게
 2) 찾아 바꾸기: Ctrl+H 작은 창 — 모든 페이지/이 페이지, 대소문자 구분, [다음]·[바꾸기]·[모두 바꾸기]
    대상: 글상자·도형 글(text·textHtml 둘 다)·표 칸. 글 서식 경계에 걸친 일치는 건너뜀(개수 알림)
 3) 최근 쓴 색: 글씨색·셀 색 창 맨 위에 최근 8색(이 PC에 저장 · 문서 데이터 아님). 다른 색 칸(배경·선 등)에서 고른 색도 기록
Usage: python3 -I patch/patch_v12510.py <PageCraft_v12.50.0_Lite.html> <out.html>"""
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
assert "BUILD_VERSION='PageCraft v12.50.0 · 배율 화면·겹침 이름·CSS 우선순위 정리'" in html, 'needs v12.50.0'
assert 'pc-v12510' not in html, 'already patched'

# ── 1) 변경 ──────────────────────────────────────────────
# CSS는 <style id="pc-ui-css"> 안 해당 구역 규칙을 직접 R()로 고칠 것. 맨 아래 덧붙이기·!important 덧칠 금지.
# 새 JS에는 주석 /*pc-v12510*/ 를 넣어 '이미 적용' 검사가 작동하게 할 것.

# 1·2) 새 JS: 편집기 단축키 바로 앞(같은 스크립트)
NEWJS = r"""/*pc-v12510*/
// ══════ v12.51 · 서식 복사(Ctrl+Shift+C/V) · 찾아 바꾸기(Ctrl+H) · 최근 쓴 색 ══════
const PC_FMT={style:null,kind:null,lineArrow:null},PC_FMT_KINDS=['text','shape','line'];
function pcFmtTargets(){return selected().filter(o=>PC_FMT_KINDS.includes(o.kind)&&o.role!=='template-frame');}
function pcFmtCopy(){const all=selected(),t=pcFmtTargets();
 if(all.length!==1||t.length!==1){status('서식 복사: 글상자·도형·선 하나를 먼저 고르세요.');return false;}
 const o=t[0];PC_FMT.style=JSON.parse(JSON.stringify(o.style||{}));PC_FMT.kind=o.kind;PC_FMT.lineArrow=o.lineArrow||null;
 status('서식을 복사했습니다 · 붙일 개체를 고르고 Ctrl+Shift+V');return true;}
function pcFmtStripInline(o){if(!o.textHtml)return;const tmp=document.createElement('div');tmp.innerHTML=o.textHtml;
 tmp.querySelectorAll('[style]').forEach(n=>{for(const k of ['color','font-size','font-family'])n.style.removeProperty(k);if(!n.getAttribute('style'))n.removeAttribute('style');});
 tmp.querySelectorAll('font').forEach(n=>{n.removeAttribute('color');n.removeAttribute('size');n.removeAttribute('face');});o.textHtml=tmp.innerHTML;}
function pcFmtApply(o){const s=PC_FMT.style;
 if((PC_FMT.kind==='line')!==(o.kind==='line')){if(M.isHex(s.stroke))o.style.stroke=s.stroke;if(s.strokeWidth)o.style.strokeWidth=s.strokeWidth;return;}
 o.style=JSON.parse(JSON.stringify(s));
 if(o.kind==='line'){if(PC_FMT.lineArrow)o.lineArrow=PC_FMT.lineArrow;else delete o.lineArrow;}else pcFmtStripInline(o);}
function pcFmtPaste(){if(!PC_FMT.style){status('먼저 개체 하나를 고르고 Ctrl+Shift+C로 서식을 복사하세요.');return false;}
 const ids=pcFmtTargets().map(o=>o.id);if(!ids.length){status('서식 붙이기: 글상자·도형·선을 고르세요.');return false;}
 const ok=mutate(()=>{for(const o of current().objects)if(ids.includes(o.id))pcFmtApply(o);});
 if(ok){setSelection(ids);status(`서식을 붙였습니다 · ${ids.length}개 · Ctrl+Z로 되돌리기`);}return ok;}

// 찾아 바꾸기: 글상자·도형(text와 textHtml 함께)·표 칸
const PC_FR={pos:-1};
function pcFrRe(q,cs){return new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),cs?'g':'gi');}
function pcFrCount(s,re){re.lastIndex=0;return (String(s||'').match(re)||[]).length;}
function pcFrTextObj(o){return ['text','shape'].includes(o.kind)&&o.role!=='template-frame';}
function pcFrPages(all){return all?st.project.pages:[current()];}
// 일치하는 개체 목록 [{page,o,n}] (페이지·개체 순서)
function pcFrScan(q,cs,all){if(!q)return [];const re=pcFrRe(q,cs),out=[];
 for(const page of pcFrPages(all))for(const o of page.objects){let n=0;
  if(pcFrTextObj(o))n=pcFrCount(o.text,re);
  else if(o.kind==='table'&&Array.isArray(o.table?.cells))for(const row of o.table.cells)for(const c of row||[])n+=pcFrCount(c,re);
  if(n)out.push({page,o,n});}
 return out;}
// 글 서식(textHtml) 안 글자 마디마다 바꿈. 바꾼 수를 돌려줌
function pcFrHtml(html,re,rep){const tmp=document.createElement('div');tmp.innerHTML=html;let n=0;
 const w=document.createTreeWalker(tmp,NodeFilter.SHOW_TEXT),nodes=[];while(w.nextNode())nodes.push(w.currentNode);
 for(const t of nodes){const k=pcFrCount(t.nodeValue,re);if(k){re.lastIndex=0;t.nodeValue=t.nodeValue.replace(re,()=>rep);n+=k;}}
 return {html:tmp.innerHTML,n};}
// 개체 하나 안을 모두 바꿈 → {n, skipped}
function pcFrReplaceIn(o,re,rep){
 if(pcFrTextObj(o)){const n=pcFrCount(o.text,re);if(!n)return {n:0,skipped:0};
  if(o.textHtml){const h=pcFrHtml(o.textHtml,re,rep);if(h.n!==n)return {n:0,skipped:n};o.textHtml=h.html;}
  re.lastIndex=0;o.text=String(o.text).replace(re,()=>rep);return {n,skipped:0};}
 let n=0;if(o.kind==='table'&&Array.isArray(o.table?.cells))o.table.cells=o.table.cells.map(row=>(row||[]).map(c=>{const k=pcFrCount(c,re);if(!k)return c;n+=k;re.lastIndex=0;return String(c).replace(re,()=>rep);}));
 return {n,skipped:0};}
function pcFrVals(){const p=$('#pcFrPanel');return p?{q:p.querySelector('.pc-fr-find').value,rep:p.querySelector('.pc-fr-repl').value,cs:p.querySelector('.pc-fr-case').checked,all:p.querySelector('.pc-fr-all').checked}:null;}
function pcFrInfo(text){const p=$('#pcFrPanel');if(!p)return;const v=pcFrVals(),list=pcFrScan(v.q,v.cs,v.all),total=list.reduce((a,x)=>a+x.n,0);
 p.querySelector('.pc-fr-count').textContent=text||(v.q?(total?`${total}곳 · 개체 ${list.length}개`:'없음'):'');
 p.querySelectorAll('.pc-fr-next,.pc-fr-one,.pc-fr-every').forEach(b=>b.disabled=!total);return list;}
function pcFrNext(){const v=pcFrVals();if(!v)return;const list=pcFrScan(v.q,v.cs,v.all);if(!list.length){pcFrInfo();return;}
 const curId=selected().length===1?selected()[0].id:null,ci=list.findIndex(x=>x.o.id===curId);
 const i=ci>=0?(ci+1)%list.length:(PC_FR.pos+1)%list.length;PC_FR.pos=i;const hit=list[i];
 if(hit.page.id!==current().id)go(hit.page.id);selectOne(hit.o.id);
 const pn=st.project.pages.indexOf(hit.page)+1;pcFrInfo(`${i+1} / ${list.length}개 · ${pn}페이지 · ${hit.n}곳`);}
function pcFrOne(){const v=pcFrVals();if(!v||!v.q)return;const list=pcFrScan(v.q,v.cs,v.all),cur=selected().length===1?selected()[0]:null;
 if(!cur||!list.some(x=>x.o.id===cur.id)){pcFrNext();return;}
 let r={n:0,skipped:0};mutate(()=>{const o=current().objects.find(x=>x.id===cur.id);if(o)r=pcFrReplaceIn(o,pcFrRe(v.q,v.cs),v.rep);});
 if(r.skipped){status(`이 개체의 ${r.skipped}곳은 글자 서식 경계에 걸쳐 바꾸지 못했습니다 · 글 편집으로 고치세요.`);}
 else status(`${r.n}곳 바꿈 · Ctrl+Z로 되돌리기`);
 const rest=pcFrScan(v.q,v.cs,v.all);if(rest.length&&!r.skipped)pcFrNext();else{selectOne(cur.id);pcFrInfo();}}
function pcFrAll(){const v=pcFrVals();if(!v||!v.q)return;const list=pcFrScan(v.q,v.cs,v.all);if(!list.length){pcFrInfo();return;}
 const ids=new Set(list.map(x=>x.o.id)),re=pcFrRe(v.q,v.cs);let n=0,skipped=0,objs=0;
 mutate(()=>{for(const page of pcFrPages(v.all))for(const o of page.objects)if(ids.has(o.id)){const r=pcFrReplaceIn(o,re,v.rep);n+=r.n;skipped+=r.skipped;if(r.n)objs++;}});
 const msg=`${n}곳 바꿈 · 개체 ${objs}개`+(skipped?` · 서식 경계에 걸친 ${skipped}곳은 건너뜀`:'');
 status(msg+' · Ctrl+Z로 한 번에 되돌리기');pcFrInfo(msg);}
function pcFrClose(){$('#pcFrPanel')?.remove();}
function pcFrOpen(){if(st.editing)finishEditing(true);let p=$('#pcFrPanel');
 const seed=(()=>{const s=String(getSelection?.()||'').trim();return s&&s.length<80&&!s.includes('\n')?s:'';})();
 if(p){const f=p.querySelector('.pc-fr-find');if(seed)f.value=seed;f.focus();f.select();pcFrInfo();return;}
 p=document.createElement('div');p.id='pcFrPanel';p.className='pc-tc-panel pc-fr-panel';p.setAttribute('role','dialog');p.setAttribute('aria-label','찾아 바꾸기');
 p.innerHTML=`<div class="pc-tc-head"><b>찾아 바꾸기</b><span class="pc-fr-count"></span></div>
  <label class="pc-fr-field"><span>찾기</span><input class="pc-fr-find" type="text" maxlength="200" aria-label="찾을 말" placeholder="예: 2025"></label>
  <label class="pc-fr-field"><span>바꿀 말</span><input class="pc-fr-repl" type="text" maxlength="200" aria-label="바꿀 말" placeholder="예: 2026"></label>
  <div class="pc-fr-opts"><label><input class="pc-fr-all" type="checkbox" checked> 모든 페이지</label><label><input class="pc-fr-case" type="checkbox"> 대소문자 구분</label></div>
  <div class="pc-tc-actions"><button type="button" class="pc-fr-next">다음</button><button type="button" class="pc-fr-one">바꾸기</button><button type="button" class="pc-tc-ok pc-fr-every">모두 바꾸기</button></div>
  <p class="pc-tc-tip">글상자·도형·표 칸 · Enter 다음 · Esc 닫기</p>`;
 document.body.append(p);const r=($('#stageViewport')||document.body).getBoundingClientRect();
 p.style.left=Math.round(Math.max(8,Math.min(innerWidth-p.offsetWidth-8,r.right-p.offsetWidth-12)))+'px';p.style.top=Math.round(Math.max(8,r.top+12))+'px';
 p.addEventListener('input',()=>{PC_FR.pos=-1;pcFrInfo();});
 p.addEventListener('click',e=>{if(e.target.closest('.pc-fr-next'))pcFrNext();else if(e.target.closest('.pc-fr-one'))pcFrOne();else if(e.target.closest('.pc-fr-every'))pcFrAll();});
 p.addEventListener('keydown',e=>{e.stopPropagation();if(e.key==='Escape'){e.preventDefault();pcFrClose();}
  else if(e.key==='Enter'&&e.target.matches('input[type=text]')){e.preventDefault();pcFrNext();}
  else if((e.ctrlKey||e.metaKey)&&!e.altKey&&e.code==='KeyH'){e.preventDefault();}
  else if((e.ctrlKey||e.metaKey)&&!e.altKey&&e.key.toLowerCase()==='z'&&!e.target.value){e.preventDefault();undo(e.shiftKey);pcFrInfo();}});
 const f=p.querySelector('.pc-fr-find');if(seed)f.value=seed;f.focus();pcFrInfo();}

// 최근 쓴 색: 이 PC에만(문서에 저장 안 함), 앞이 가장 최근
const PC_RECENT={key:'pc-recent-colors-v1',max:8,mem:[]};
function pcRecentGet(){try{const a=JSON.parse(localStorage.getItem(PC_RECENT.key)||'[]');if(Array.isArray(a))return a.filter(c=>M.isHex(c)).slice(0,PC_RECENT.max);}catch(e){}return PC_RECENT.mem.slice();}
function pcRecentAdd(c){if(!M.isHex(c))return;c=String(c).toUpperCase();const a=[c,...pcRecentGet().filter(x=>x!==c)].slice(0,PC_RECENT.max);PC_RECENT.mem=a;try{localStorage.setItem(PC_RECENT.key,JSON.stringify(a));}catch(e){}}
function pcRecentRow(sw){const a=pcRecentGet();return a.length?`<div class="pc-tc-label">최근 쓴 색</div><div class="pc-tc-grid pc-tc-recent">${a.map(sw).join('')}</div>`:'';}
// 다른 색 칸(배경·선·그라데이션 등 브라우저 색 창)에서 고른 색도 기록. 작은 색 창 안 '직접 고르기'는 [확인] 때 기록
document.addEventListener('change',e=>{const t=e.target;if(t?.matches?.('input[type=color]')&&!t.closest('.pc-tc-panel'))pcRecentAdd(t.value);},true);
"""
R("function pcKeyEditor(e){\n", NEWJS + "function pcKeyEditor(e){\n")

# 단축키: Ctrl+H(글 편집 중에도), Ctrl+Shift+C/V(개체 선택)
R(" if(st.editing){if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();finishEditing(true)}return;}\n",
  " if((e.ctrlKey||e.metaKey)&&!e.altKey&&!e.shiftKey&&e.code==='KeyH'&&!e.target.closest?.('#pcFrPanel')){e.preventDefault();if(!e.repeat)pcFrOpen();return;}\n"
  " if(st.editing){if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();finishEditing(true)}return;}\n")
R(" if(e.ctrlKey||e.metaKey){const k=e.key.toLowerCase();if(k==='c'){",
  " if((e.ctrlKey||e.metaKey)&&e.shiftKey&&!e.altKey&&(e.code==='KeyC'||e.code==='KeyV')){e.preventDefault();if(!e.repeat)(e.code==='KeyC'?pcFmtCopy:pcFmtPaste)();return;}\n"
  " if(e.ctrlKey||e.metaKey){const k=e.key.toLowerCase();if(k==='c'){")
R(" {keys:'Ctrl+D',when:'개체 선택',does:'복제',where:'pcKeyEditor'},\n",
  " {keys:'Ctrl+D',when:'개체 선택',does:'복제',where:'pcKeyEditor'},\n"
  " {keys:'Ctrl+Shift+C / Ctrl+Shift+V',when:'개체 선택(글상자·도형·선)',does:'서식 복사 / 서식 붙이기 (글꼴·크기·색·테두리, 여러 개 한 번에)',where:'pcKeyEditor'},\n"
  " {keys:'Ctrl+H',when:'편집 화면(글 편집 중 포함)',does:'찾아 바꾸기 창 (모든 페이지·글상자·도형·표 칸)',where:'pcKeyEditor'},\n")

# 3) 최근 쓴 색: 두 작은 색 창(글씨색·셀 색) 맨 위 + [확인] 때 기록
R("  ${pal.length?`<div class=\"pc-tc-label\">테마 색</div>", "  ${pcRecentRow(sw)}${pal.length?`<div class=\"pc-tc-label\">테마 색</div>", 2)
R(" if(apply&&d)pcTcApply(d.color,d.range);", " if(apply&&d){pcTcApply(d.color,d.range);pcRecentAdd(d.color);}")
R("tableStyleSelection(d.field,d.color);status(", "tableStyleSelection(d.field,d.color);pcRecentAdd(d.color);status(")

# CSS: 작은 색 창 구역(v12.38) 안
a = html.find('<style id="pc-ui-css">'); b = html.find('</style>', a); assert a > 0
css = html[a:b]
def C(old, new, n=1):
    global css
    c = css.count(old); assert c == n, f'css expected {n} got {c}: {old[:80]!r}'
    css = css.replace(old, new)
C(".pc-tc-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}",
  ".pc-tc-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}.pc-tc-grid.pc-tc-recent{grid-template-columns:repeat(8,1fr);gap:4px}.pc-tc-recent .pc-tc-sw{height:22px;border-radius:6px}")
C(".pc-tc-tip{margin:8px 0 0;font-size:11.5px;color:#475569}",
  ".pc-tc-tip{margin:8px 0 0;font-size:11.5px;color:#475569}\n"
  "/* v12.51 찾아 바꾸기 창(작은 색 창 틀을 같이 씀) */\n"
  ".pc-tc-panel.pc-fr-panel{width:300px}.pc-fr-panel .pc-fr-count{font-size:12px;color:#475569}\n"
  ".pc-fr-field{display:grid;grid-template-columns:52px 1fr;align-items:center;gap:6px;margin-top:6px;font-size:12px;color:#334155}"
  ".pc-fr-field input{height:30px;min-width:0;padding:0 8px;border:1px solid #CBD5E1;border-radius:7px;font:inherit;font-size:13px;color:#0F172A}"
  ".pc-fr-field input:focus{outline:2px solid #93C5FD;border-color:#3B82F6}\n"
  ".pc-fr-opts{display:flex;gap:12px;margin-top:8px;font-size:12px;color:#334155}.pc-fr-opts label{display:flex;align-items:center;gap:4px;cursor:pointer}\n"
  ".pc-fr-panel .pc-tc-actions button{white-space:nowrap;padding:0 6px}.pc-fr-panel .pc-tc-actions .pc-fr-every{flex:1.5}.pc-fr-panel .pc-tc-actions button:disabled{opacity:.45;cursor:default}")
html = html[:a] + css + html[b:]

# ── 버전 문자열(BUILD_VERSION·하단 서명. <title>은 v12.46부터 문서 제목이라 안 건드림) ──
R("const BUILD_VERSION='PageCraft v12.50.0 · 배율 화면·겹침 이름·CSS 우선순위 정리';", "const BUILD_VERSION='PageCraft v12.51.0 · 서식 복사·찾아 바꾸기·최근 쓴 색';")
R('Jungmin Jo · PageCraft v12.50.0</span>', 'Jungmin Jo · PageCraft v12.51.0</span>')
open(out, 'w', encoding='utf-8').write(html); print('patched', out, len(html))
