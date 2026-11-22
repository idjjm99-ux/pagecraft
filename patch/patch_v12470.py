"""PageCraft v12.47.0 — PPT·구글 슬라이드에 있는 기본 기능 4가지(추천 순서 1·2·4·3).
기준: v12.46.0 Lite (claude/keen-shannon-uczmhn 판: 저장 메뉴·첫 안내·작은 화면).
 1) 글자 맞춤: 글상자·도형 글자 왼쪽/가운데/오른쪽 — 도구줄 단추 3개 + 간편편집바 단추 3개 + Ctrl+L·E·R.
    여러 개 선택하면 한꺼번에, 글 편집 중이면 편집 그대로 둔 채 상자 전체에. 저장 구조(style.textAlign)는 기존 그대로
 2) 캡처 그림 Ctrl+V: 클립보드에 그림만 있으면(글자 없음) 그림 개체로 넣음. 마우스 위치 가운데, 원래 비율, 페이지 60% 안.
    그림 칸(빈 사진 자리 포함) 하나 골라 두면 그 칸 그림을 바꿈. 글 편집 중이면 편집을 마치고 넣음.
    앱 안 개체 복사(Ctrl+C)는 클립보드에 표시 글자를 남겨, 나중에 한 쪽(복사한 개체/캡처 그림)이 붙도록 함
 4) 선 끝 화살표: 선 개체에 '화살표'(없음/끝/시작/양쪽) — 상세 설정·간편편집바, 도형 고르기에 '화살표' 추가.
    lineArrow 필드는 화살표가 있을 때만 저장(기존 문서 데이터 불변)
 3) 페이지 끌어서 순서 바꾸기: 왼쪽 페이지 목록에서 썸네일을 위아래로 끌기(파란 선 = 놓을 자리, 목록 끝에선 자동 스크롤, Esc 취소)
Usage: python3 -I patch_v12470.py <PageCraft_v12.46.0_Lite.html> <out.html>"""
import sys
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
def R(old, new, n=1):
    global html
    c = html.count(old); assert c == n, f'expected {n} got {c}: {old[:80]!r}'
    html = html.replace(old, new)
assert "BUILD_VERSION='PageCraft v12.46.0 · 쓰기 편하게(저장 메뉴·첫 안내·작은 화면)'" in html, 'needs v12.46.0 (keen-shannon)'
assert 'pcSetTextAlign' not in html, 'already patched'

R("BUILD_VERSION='PageCraft v12.46.0 · 쓰기 편하게(저장 메뉴·첫 안내·작은 화면)'",
  "BUILD_VERSION='PageCraft v12.47.0 · 기본 기능(글자 맞춤·그림 붙여넣기·화살표·페이지 끌기)'")
R('title="프로그램 정보">Jungmin Jo · PageCraft v12.46.0</span>',
  'title="프로그램 정보">Jungmin Jo · PageCraft v12.47.0</span>')

# ── 1) 글자 맞춤 ─────────────────────────────────────────────────
ICON = {
 'left':   'M4 6h16M4 10h10M4 14h16M4 18h10',
 'center': 'M4 6h16M7 10h10M4 14h16M7 18h10',
 'right':  'M4 6h16M10 10h10M4 14h16M10 18h10'}
def svg(k): return ('<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="' + ICON[k] +
                    '" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>')
NAMES = [('Left', 'left', '왼쪽', 'L'), ('Center', 'center', '가운데', 'E'), ('Right', 'right', '오른쪽', 'R')]
ribbon_btns = ''.join(
    f'<button class="tool-btn pc-align-btn" data-action="textAlign{a}" data-target="text" type="button" '
    f'aria-pressed="false" title="글자 {n} 맞춤 (Ctrl+{k})" aria-label="글자 {n} 맞춤">{svg(v)}</button>'
    for a, v, n, k in NAMES)
R('<button class="tool-btn underline" data-action="underline" data-target="text" title="밑줄"><u>U</u><small>밑줄</small></button>',
  '<button class="tool-btn underline" data-action="underline" data-target="text" title="밑줄"><u>U</u><small>밑줄</small></button>'
  '<span class="pc-align-group" role="group" aria-label="글자 맞춤"><span class="pc-align-btns">' + ribbon_btns +
  '</span><small>글자 맞춤</small></span>')
quick_btns = ''.join(
    f'<button class="pc-qalign" data-action="textAlign{a}" type="button" aria-pressed="false" '
    f'title="글자 {n} 맞춤 (Ctrl+{k})" aria-label="글자 {n} 맞춤">{svg(v)}</button>'
    for a, v, n, k in NAMES)
R('<button class="quick-underline" data-action="underline" title="밑줄"><u>U</u></button>',
  '<button class="quick-underline" data-action="underline" title="밑줄"><u>U</u></button>'
  '<span class="pc-qalign-group" role="group" aria-label="글자 맞춤">' + quick_btns + '</span>')
R("case 'bold':formatText('bold');break;",
  "case 'bold':formatText('bold');break;case 'textAlignLeft':pcSetTextAlign('left');break;"
  "case 'textAlignCenter':pcSetTextAlign('center');break;case 'textAlignRight':pcSetTextAlign('right');break;")
# 글 편집 중 단추를 눌러도 편집(커서)이 풀리지 않게
R('button[data-action="bold"],button[data-action="underline"],button[data-action="symbols"],[data-symbol]\'))e.preventDefault();',
  'button[data-action="bold"],button[data-action="underline"],button[data-action="symbols"],button[data-action^="textAlign"],[data-symbol]\'))e.preventDefault();')
# Ctrl+L·E·R (글 편집 중 포함, 입력칸 제외, 고른 글상자·도형 없으면 브라우저 기본 동작 그대로)
R("if(st.editing){if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();finishEditing(true)}return;}",
  "if((e.ctrlKey||e.metaKey)&&!e.altKey&&!e.shiftKey&&PC_ALIGN_KEYS[e.code]&&!e.target.closest?.('input,textarea,select')&&pcAlignTargets().length){e.preventDefault();if(!e.repeat)pcSetTextAlign(PC_ALIGN_KEYS[e.code]);return;}\n"
  " if(st.editing){if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();finishEditing(true)}return;}")
R("{keys:'Ctrl+C / Ctrl+V',when:'개체 선택',does:'복사 / 마우스 위치에 붙여넣기 (표·그래프 선택 중이면 엑셀·시트 칸 붙여넣기)',where:'pcKeyEditor · paste 이벤트'},",
  "{keys:'Ctrl+C / Ctrl+V',when:'개체 선택',does:'복사 / 마우스 위치에 붙여넣기 (표·그래프 선택 중이면 엑셀·시트 칸 붙여넣기, 클립보드에 캡처 그림만 있으면 그림으로)',where:'pcKeyEditor · paste 이벤트(pcPasteRoute)'},\n"
  " {keys:'Ctrl+L / Ctrl+E / Ctrl+R',when:'글상자·도형 선택(글 편집 중 포함)',does:'글자 왼쪽 / 가운데 / 오른쪽 맞춤',where:'pcKeyEditor'},")

# ── 2) 캡처 그림 Ctrl+V ──────────────────────────────────────────
# 키 누름에서 바로 붙이지 않고 paste 이벤트에서 클립보드를 보고 고름(이벤트가 안 오면 150ms 뒤 기존대로 개체 붙여넣기)
R("if(k==='c'){if(copySelectedObjects())e.preventDefault();return}if(k==='v'){if(window.pcGridPasteTarget?.())return;if(pasteSelectedObjects())e.preventDefault();return}",
  "if(k==='c'){if(copySelectedObjects())PC_PASTE.copyAt=performance.now();return}if(k==='v'){if(window.pcGridPasteTarget?.())return;if(st.objectClipboard?.length){clearTimeout(PC_PASTE.timer);PC_PASTE.timer=setTimeout(()=>{PC_PASTE.timer=null;pasteSelectedObjects();},150);}return}")
R("status(items.length+'개 개체 복사됨 · 붙일 곳에 마우스를 두고 Ctrl+V');return true;",
  "PC_PASTE.marker='[페이지공방 개체 '+items.length+'개 복사 '+Date.now().toString(36)+']';try{navigator.clipboard?.writeText?.(PC_PASTE.marker)?.catch?.(()=>{});}catch(err){}"
  "status(items.length+'개 개체 복사됨 · 붙일 곳에 마우스를 두고 Ctrl+V');return true;")
R("async function importMedia(file,id=st.mediaTarget){",
  "async function importMedia(file,id=st.mediaTarget,place=null){")
R("item=M.blankObject(kind,Math.min(880,x),Math.min(610,y),kind==='audio'?360:320,kind==='audio'?100:172);",
  "item=M.blankObject(kind,Math.min(880,x),Math.min(610,y),kind==='audio'?360:320,kind==='audio'?100:172);"
  "if(place&&kind==='image')Object.assign(item,{x:place.x,y:place.y,w:place.w,h:place.h});")

# ── 4) 선 끝 화살표 ─────────────────────────────────────────────
R("c.lineDirection=['h','v','d','anti'].includes(c.lineDirection)?c.lineDirection:'h';",
  "c.lineDirection=['h','v','d','anti'].includes(c.lineDirection)?c.lineDirection:'h';if('lineArrow' in c&&!['end','start','both'].includes(c.lineArrow))delete c.lineArrow;")
ARROW_RENDER = (
 "svg.append(line);"
 "if(['end','start','both'].includes(o.lineArrow)){const sw=Number(s.strokeWidth)||5,L=Math.max(10,sw*2.6+5),Wd=L*.6,col=line.getAttribute('stroke');"
 "const head=(tip,from)=>{const dx=tip[0]-from[0],dy=tip[1]-from[1],len=Math.hypot(dx,dy)||1,ux=dx/len,uy=dy/len,bx=tip[0]-ux*L,by=tip[1]-uy*L;"
 "const poly=document.createElementNS(NS,'polygon');poly.setAttribute('points',[[tip[0],tip[1]],[bx-uy*Wd,by+ux*Wd],[bx+uy*Wd,by-ux*Wd]].map(p=>p.map(v=>v.toFixed(2)).join(',')).join(' '));"
 "poly.setAttribute('fill',col);poly.setAttribute('stroke',col);poly.setAttribute('stroke-width',String(Math.min(2,sw/2)));poly.setAttribute('stroke-linejoin','round');poly.setAttribute('class','pc-line-head');svg.append(poly);return [tip[0]-ux*L*.7,tip[1]-uy*L*.7];};"
 "const A=[points[0],points[1]],B=[points[2],points[3]];"
 "if(o.lineArrow!=='start'){const q=head(B,A);line.setAttribute('x2',q[0]);line.setAttribute('y2',q[1]);}"
 "if(o.lineArrow!=='end'){const q=head(A,B);line.setAttribute('x1',q[0]);line.setAttribute('y1',q[1]);}"
 "svg.style.overflow='visible';svg.dataset.lineArrow=o.lineArrow;}"
 "n.append(svg);")
R("svg.append(line);n.append(svg);", ARROW_RENDER)
R("[['h','수평'],['v','수직'],['d','우상향'],['anti','우하향']])+",
  "[['h','수평'],['v','수직'],['d','우상향'],['anti','우하향']])+dropdown('화살표','lineArrow',o.lineArrow||'none',[['none','없음'],['end','끝에 →'],['start','시작에 ←'],['both','양쪽 ↔']])+")
R("case 'lineDirection':o.lineDirection=value;break;",
  "case 'lineDirection':o.lineDirection=value;break;case 'lineArrow':if(['end','start','both'].includes(value))o.lineArrow=value;else delete o.lineArrow;break;")
# 도형 고르기: '화살표'
R("['line-h','수평선'],['line-d','대각선']]", "['line-h','수평선'],['line-d','대각선'],['line-arrow','화살표']]")
LD = "if(value==='line-d')preview.innerHTML='<svg viewBox=\"0 0 52 38\" aria-hidden=\"true\"><path d=\"M7 31 L45 7\" stroke=\"#4A7493\" stroke-width=\"3\" stroke-linecap=\"round\"/></svg>';"
R(LD, LD + "\n    if(value==='line-arrow')preview.innerHTML='<svg viewBox=\"0 0 52 38\" aria-hidden=\"true\"><path d=\"M5 19 H38\" stroke=\"#4A7493\" stroke-width=\"3\" stroke-linecap=\"round\"/><path d=\"M47 19 L36 12.5 L36 25.5 Z\" fill=\"#4A7493\" stroke=\"#4A7493\" stroke-width=\"1.5\" stroke-linejoin=\"round\"/></svg>';")
R("if(value==='line-h'||value==='line-d'){", "if(value==='line-h'||value==='line-d'||value==='line-arrow'){")
R("hint.textContent=value==='line-h'?'Shift → 수직선':'Shift → 반대 기울기';",
  "hint.textContent=value==='line-d'?'Shift → 반대 기울기':'Shift → 수직선';")
R("if(value==='line-h')beginPlacement('line',{lineDirection:'h'});",
  "if(value==='line-h')beginPlacement('line',{lineDirection:'h'});else if(value==='line-arrow')beginPlacement('line',{lineDirection:'h',lineArrow:'end'});")
R("if(kind==='line')o.lineDirection=pending.lineDirection||'h';",
  "if(kind==='line'){o.lineDirection=pending.lineDirection||'h';if(pending.lineArrow)o.lineArrow=pending.lineArrow;}")

# ── 3) 페이지 끌기 안내 문구 ─────────────────────────────────────
R("클릭하여 이동 · 드래그하지 않아도 순서 버튼으로 정렬", "클릭하여 이동 · 끌어서 순서 바꾸기")

# ── 새 코드(앱 본체 끝, 글꼴 다시 맞춤 앞) ─────────────────────────
NEW_JS = r"""// ═══ v12.47: 글자 맞춤 · 캡처 그림 붙여넣기 · 선 화살표 · 페이지 끌기 ═══
const PC_ALIGN_KEYS=Object.freeze({KeyL:'left',KeyE:'center',KeyR:'right'});
const PC_ALIGN_NAME={left:'왼쪽',center:'가운데',right:'오른쪽'};
function pcAlignTargets(){if(st.editing){const o=obj(st.editing.id);return o&&['text','shape'].includes(o.kind)?[o]:[];}return selected().filter(o=>['text','shape'].includes(o.kind));}
function pcAlignSync(){const L=pcAlignTargets(),v=L.length&&L.every(o=>(o.style.textAlign||'left')===(L[0].style.textAlign||'left'))?(L[0].style.textAlign||'left'):null;
 for(const b of document.querySelectorAll('[data-action^="textAlign"]')){const m=b.dataset.action==='textAlignLeft'?'left':b.dataset.action==='textAlignCenter'?'center':'right';b.setAttribute('aria-pressed',String(m===v));}}
function pcSetTextAlign(v){if(!PC_ALIGN_NAME[v])return false;const list=pcAlignTargets();if(!list.length){status('글상자나 도형을 먼저 고르세요.');return false;}
 const name=PC_ALIGN_NAME[v];
 if(st.editing){const o=list[0],before=JSON.stringify(st.project);o.style.textAlign=v;if(deps.history.commit(st,before))saveLocal();
  const c=$(`#stageHost .rv-object[data-object-id="${CSS.escape(o.id)}"] .rv-text-content`);if(c)c.style.textAlign=v;pcAlignSync();status('글자 '+name+' 맞춤');return true;}
 if(list.every(o=>(o.style.textAlign||'left')===v)){pcAlignSync();status('이미 '+name+' 맞춤입니다');return true;}
 const ok=mutate(()=>{for(const o of list)o.style.textAlign=v;});
 if(ok!==false)status('글자 '+name+' 맞춤'+(list.length>1?' · '+list.length+'개':'')+' · Ctrl+Z로 되돌리기');return ok!==false;}
EXT.on('afterRibbon',pcAlignSync);EXT.on('afterQuickBar',pcAlignSync);

// 2) 붙여넣기 갈래: 캡처 그림(글자 없는 그림) → 그림 개체 / 앱에서 복사한 표시 글자 → 개체 / 그 밖은 기존 그대로
const PC_PASTE={timer:null,marker:'',copyAt:0};
window.addEventListener('copy',e=>{if(!PC_PASTE.copyAt||performance.now()-PC_PASTE.copyAt>1000)return;PC_PASTE.copyAt=0;if(!PC_PASTE.marker||!e.clipboardData)return;e.clipboardData.setData('text/plain',PC_PASTE.marker);e.preventDefault();},true);
function pcClipImage(dt){if(!dt||(dt.getData('text/plain')||'').trim())return null;
 for(const it of dt.items||[])if(it.kind==='file'&&/^image\/(png|jpe?g|gif|webp|bmp)$/i.test(it.type)){const f=it.getAsFile();if(f)return f;}
 for(const f of dt.files||[])if(/^image\/(png|jpe?g|gif|webp|bmp)$/i.test(f.type))return f;return null;}
async function pcPasteImage(file){
 const one=selected().length===1?obj():null,target=one&&one.kind==='image'&&!one.locked?one.id:null;
 let nat=null;try{const bm=await createImageBitmap(file);nat={w:bm.width,h:bm.height};bm.close?.();}catch(err){}
 const ext=(String(file.type).split('/')[1]||'png').replace('jpeg','jpg').replace(/[^a-z0-9]/gi,'');
 const named=new File([file],/^image\.\w+$/i.test(file.name||'image.png')?'붙여넣은 그림.'+ext:file.name,{type:file.type});
 let place=null;const mp=st.pcMouse&&st.pcMouse.page===current().id?st.pcMouse:null;
 if(!target&&nat&&nat.w>0&&nat.h>0){const k=Math.min(1,M.W*.6/nat.w,M.H*.6/nat.h),w=Math.max(40,Math.round(nat.w*k)),h=Math.max(40,Math.round(nat.h*k));const cx=mp?mp.x:M.W/2,cy=mp?mp.y:M.H/2;
  place={x:Math.round(M.clamp(cx-w/2,0,M.W-w)),y:Math.round(M.clamp(cy-h/2,0,M.H-h)),w,h};}
 try{const ok=await importMedia(named,target,place);
  if(ok)status(target?'고른 그림 칸에 붙여넣은 그림을 넣었습니다 · Ctrl+Z로 되돌리기':'그림을 붙여넣었습니다 · '+(mp?'마우스 위치':'페이지 가운데')+' · Ctrl+Z로 되돌리기');return ok;}
 catch(err){alert('그림을 붙여넣지 못했습니다: '+(err?.message||err));return false;}}
const PC_MARK_RE=/^\[페이지공방 개체 \d+개 복사 [0-9a-z]+\]$/;
function pcPasteRoute(e){
 if(!$('#presentation').hidden)return;const t=e.target,dt=e.clipboardData,text=(dt?.getData('text/plain')||'').trim(),mark=PC_MARK_RE.test(text);
 // 앱 복사 표시 글자는 입력칸·글 편집·표 칸에 글자로 들어가지 않게(다시 연 문서·다른 창에서 남은 것 포함)
 if(t?.closest?.('input,textarea,select,dialog')){if(mark){e.preventDefault();e.stopImmediatePropagation();}return;}
 const waited=!!PC_PASTE.timer;clearTimeout(PC_PASTE.timer);PC_PASTE.timer=null;
 const img=pcClipImage(dt);
 if(img){if(document.querySelector('dialog[open]')||(!st.editing&&t?.closest?.('[contenteditable=true]')))return;e.preventDefault();e.stopImmediatePropagation();if(st.editing)finishEditing(true);pcPasteImage(img);return;}
 if(st.editing||t?.closest?.('[contenteditable=true]')){if(mark){e.preventDefault();e.stopImmediatePropagation();status('복사한 개체는 글 편집을 마친 뒤(Esc) Ctrl+V로 붙여넣으세요.');}if(waited)pasteSelectedObjects();return;}
 if(mark){e.preventDefault();e.stopImmediatePropagation();if(st.objectClipboard?.length)pasteSelectedObjects();return;}
 if(waited){e.preventDefault();pasteSelectedObjects();}}
window.addEventListener('paste',pcPasteRoute,true);

// 4) 간편편집바: 선 화살표
document.addEventListener('change',e=>{const sel=e.target.closest?.('[data-quick-line-arrow]');if(!sel)return;e.stopImmediatePropagation();const o=selected().length===1?obj():null;if(!o||o.kind!=='line')return;
 const v=sel.value;mutate(()=>{if(['end','start','both'].includes(v))o.lineArrow=v;else delete o.lineArrow;});status(v==='none'?'화살표 없앰':'화살표: '+({end:'끝',start:'시작',both:'양쪽'})[v]+' · Ctrl+Z로 되돌리기');},true);
EXT.on('afterQuickBar',()=>{const bar=$('#quickBar');bar?.querySelector('.pc-quick-arrow')?.remove();const o=selected().length===1?obj():null;
 if(!bar||bar.hidden||!o||o.kind!=='line'||st.editing)return;const payload=bar.querySelector('.quick-payload');if(!payload)return;const cur=o.lineArrow||'none';
 const label=document.createElement('label');label.className='pc-quick-arrow';label.title='선 끝 화살표';
 label.innerHTML='<select data-quick-line-arrow aria-label="화살표">'+[['none','없음'],['end','끝 →'],['start','시작 ←'],['both','양쪽 ↔']].map(([v,t])=>'<option value="'+v+'"'+(v===cur?' selected':'')+'>'+t+'</option>').join('')+'</select><small>화살표</small>';
 const lock=payload.querySelector('.quick-lock,[data-action="locked"]');if(lock)payload.insertBefore(label,lock);else payload.append(label);});

// 3) 페이지 목록에서 끌어서 순서 바꾸기 (마우스·펜. 터치는 목록 스크롤 그대로)
(function pcPageDrag(){const list=$('#pageList');if(!list)return;let d=null,scrollTimer=null,lastY=0,killClick=0;
 const rows=()=>[...list.querySelectorAll(':scope > .page-row')];
 const clear=()=>{for(const r of rows())r.classList.remove('pc-drop-before','pc-drop-after','pc-page-dragging');document.body.classList.remove('pc-page-drag');clearInterval(scrollTimer);scrollTimer=null;};
 const slotAt=y=>{const R=rows().filter(r=>r!==d.row);let s=R.length;for(let i=0;i<R.length;i++){const b=R[i].getBoundingClientRect();if(y<b.top+b.height/2){s=i;break;}}return {R,s};};
 const show=y=>{for(const r of rows())r.classList.remove('pc-drop-before','pc-drop-after');const {R,s}=slotAt(y);d.slot=s;if(!R.length)return;if(s<R.length)R[s].classList.add('pc-drop-before');else R[R.length-1].classList.add('pc-drop-after');};
 const edgeScroll=()=>{const b=list.getBoundingClientRect(),z=44;let v=0;if(lastY<b.top+z)v=-Math.ceil((b.top+z-lastY)/4);else if(lastY>b.bottom-z)v=Math.ceil((lastY-(b.bottom-z))/4);if(v){list.scrollTop+=M.clamp(v,-18,18);show(lastY);}};
 list.addEventListener('pointerdown',e=>{if(e.button!==0||e.pointerType==='touch'||st.eraserMode)return;const row=e.target.closest('.page-row');if(!row||e.target.closest('.page-actions')||!list.contains(row))return;
  d={row,id:row.dataset.pageId,x:e.clientX,y:e.clientY,pid:e.pointerId,on:false,slot:null};});
 window.addEventListener('pointermove',e=>{if(!d||e.pointerId!==d.pid)return;lastY=e.clientY;
  if(!d.on){if(Math.abs(e.clientY-d.y)<6&&Math.abs(e.clientX-d.x)<6)return;d.on=true;d.row.classList.add('pc-page-dragging');document.body.classList.add('pc-page-drag');scrollTimer=setInterval(edgeScroll,30);}
  e.preventDefault();show(e.clientY);},{passive:false});
 const end=(e,cancel)=>{if(!d||(e&&e.pointerId!==d.pid&&e.type!=='keydown'))return;const was=d;d=null;clear();if(!was.on)return;killClick=performance.now();if(cancel||was.slot==null){status('페이지 옮기기를 취소했습니다.');return;}
  const P=st.project.pages,from=P.findIndex(p=>p.id===was.id);if(from<0)return;const to=was.slot;if(to===from){status('같은 자리입니다.');return;}
  const ok=mutate(()=>{const [pg]=st.project.pages.splice(from,1);st.project.pages.splice(to,0,pg);});
  if(ok!==false){status((from+1)+'번 페이지를 '+(to+1)+'번 자리로 옮겼습니다 · Ctrl+Z로 되돌리기');requestAnimationFrame(()=>list.querySelector(`.page-row[data-page-id="${CSS.escape(was.id)}"]`)?.scrollIntoView({block:'nearest'}));}};
 window.addEventListener('pointerup',e=>end(e,false),true);window.addEventListener('pointercancel',e=>end(e,true),true);
 window.addEventListener('keydown',e=>{if(d?.on&&e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();end(e,true);}},true);
 window.addEventListener('click',e=>{if(killClick&&performance.now()-killClick<400&&list.contains(e.target)){e.preventDefault();e.stopImmediatePropagation();killClick=0;}},true);
})();
"""
R("// Fonts may finish loading after the first layout pass.", NEW_JS + "// Fonts may finish loading after the first layout pass.")

# ── CSS (pc-ui-css 안: 해당 구역 직접 + v12.47 새 기능 구역) ───────────
# 도구줄 폭: 글자 맞춤 단추(+93px)만큼 1499px 이하에서 글꼴 칸·두께 칸·투명도 칸을 줄여 2줄 유지
R("#app .ribbon .ribbon-format select#fontFamily{width:150px}",
  "#app .ribbon .ribbon-format select#fontFamily{width:150px}\n"
  "@media(max-width:1499px){#app .ribbon .ribbon-format select#fontFamily{width:128px}#app .ribbon .rv-stroke-width select{max-width:68px}#app .ribbon .opacity-control{width:100px;min-width:100px}}")
R(".placement-choices .shape-preview.line-h,.placement-choices .shape-preview.line-d,",
  ".placement-choices .shape-preview.line-h,.placement-choices .shape-preview.line-d,.placement-choices .shape-preview.line-arrow,")
CSS = """/* ══════ v12.47: 글자 맞춤 · 선 화살표 · 페이지 끌기 ══════ */
#app .ribbon .pc-align-group{display:inline-flex;flex-direction:column;align-items:center;gap:1px;flex-shrink:0}
#app .ribbon .pc-align-btns{display:inline-flex;gap:1px;padding:1px;border:1px solid #E3E9F0;border-radius:8px;background:#fff}
#app .ribbon .tool-btn.pc-align-btn{min-width:26px;width:26px;min-height:22px;height:22px;padding:0;border-radius:6px}
#app .ribbon>.ribbon-format .tool-btn.pc-align-btn{min-height:22px}
#app .ribbon .pc-align-btn svg{width:17px;height:17px;display:block}
#app .ribbon .pc-align-group>small{font-size:11.5px;font-weight:500;color:#475569;line-height:1.15;white-space:nowrap}
.quick-bar .pc-qalign-group{display:inline-flex;gap:1px;padding:1px;border:1px solid #DCE4EE;border-radius:8px;background:#fff;align-self:center}
.quick-bar .pc-qalign-group .pc-qalign{display:inline-flex;align-items:center;justify-content:center;width:28px;min-width:28px;height:28px;min-height:28px;padding:0;border:0;border-radius:6px;background:transparent;color:#334155}
.quick-bar .pc-qalign-group .pc-qalign svg{width:17px;height:17px;display:block}
.quick-bar .pc-qalign-group .pc-qalign:hover{background:#F3F6FA}
.quick-bar .pc-qalign-group .pc-qalign[aria-pressed="true"]{background:#EAF1FE;color:#1D4ED8;box-shadow:inset 0 0 0 1px #BCD0F5}
.quick-bar .pc-quick-arrow{display:inline-flex;flex-direction:column;align-items:center;gap:1px}
.quick-bar .pc-quick-arrow small{font-size:10.5px;color:#475569}
body.pc-page-drag,body.pc-page-drag *{cursor:grabbing!important;user-select:none}
#pageList .page-row.pc-page-dragging{opacity:.45}
#pageList .page-row.pc-drop-before::before,#pageList .page-row.pc-drop-after::after{content:'';position:absolute;left:2px;right:2px;height:3px;border-radius:2px;background:#2563EB;box-shadow:0 0 0 2px rgba(37,99,235,.18);pointer-events:none;z-index:3}
#pageList .page-row.pc-drop-before::before{top:-4px}
#pageList .page-row.pc-drop-after::after{bottom:-4px}
"""
R("</style><script id=\"embedded-font-license\"", CSS + "</style><script id=\"embedded-font-license\"")

open(out, 'w', encoding='utf-8').write(html)
print('ok', out, len(html))
