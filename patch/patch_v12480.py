"""PageCraft v12.48.0 — PPT·구글 슬라이드에 있는 기능 2가지(지난 표 6·5번, 추천 순서 6 → 5).
기준: v12.47.0 Lite (브랜치 ccr-d0973cf5-o0uei2 판: 글자 맞춤·그림 붙여넣기·화살표·페이지 끌기).
 6) 개체 회전: 글상자·도형·그림·선. 고른 개체 아래쪽 동그란 손잡이를 끌어 돌리기(Shift: 15° 단위, 0·90·180° 근처는 붙음),
    상세 설정 '회전' 칸(숫자·↺90°·↻90°·0°). 저장값 rotation(도, -180~180) — 돌리지 않은 개체엔 필드 없음(기존 문서 데이터 불변).
    돌린 개체도 크기 손잡이로 반대쪽 고정 크기 조절, 지우개 위치 맞음. 화면·썸네일·발표·인쇄는 같은 그림(CSS rotate),
    PPT는 글자·그림을 PowerPoint 회전 개체로, 상자 꾸밈은 돌린 그대로 그림으로.
 5) 발표자 보기: 발표 도구줄 [발표자 보기] → 새 창에 지금 화면·다음 페이지·발표 메모·지난 시간·시각.
    그 창에서 → ← ↑ ↓·Space·PageUp/Down·숫자키로 넘기기, 메모 글씨 크기 조절, 시간 멈춤·0부터. 발표를 끝내면 같이 닫힘.
    팝업이 막히면 발표 화면 아래에 메모 칸을 띄움.
Usage: python3 -I patch_v12480.py <PageCraft_v12.47.0_Lite.html> <out.html>"""
import sys
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
def R(old, new, n=1):
    global html
    c = html.count(old); assert c == n, f'expected {n} got {c}: {old[:80]!r}'
    html = html.replace(old, new)
assert "BUILD_VERSION='PageCraft v12.47.0 · 기본 기능(글자 맞춤·그림 붙여넣기·화살표·페이지 끌기)'" in html, 'needs v12.47.0'
assert 'pcRotHandle' not in html, 'already patched'

R("BUILD_VERSION='PageCraft v12.47.0 · 기본 기능(글자 맞춤·그림 붙여넣기·화살표·페이지 끌기)'",
  "BUILD_VERSION='PageCraft v12.48.0 · 회전·발표자 보기'")
R('title="프로그램 정보">Jungmin Jo · PageCraft v12.47.0</span>',
  'title="프로그램 정보">Jungmin Jo · PageCraft v12.48.0</span>')

# ── 6) 회전: 데이터(모델 정리·속성 명령) ─────────────────────────────
ROT_KINDS = "['text','shape','image','line']"
R("if('lineArrow' in c&&!['end','start','both'].includes(c.lineArrow))delete c.lineArrow;",
  "if('lineArrow' in c&&!['end','start','both'].includes(c.lineArrow))delete c.lineArrow;"
  "if('rotation' in c){let r=Number(c.rotation);r=Number.isFinite(r)?Math.round((((r%360)+540)%360-180)*10)/10:0;if(!r||!" + ROT_KINDS + ".includes(c.kind))delete c.rotation;else c.rotation=r;}")
R("case 'shapeType':o.shapeType=",
  "case 'rotation':{if(o.locked||!" + ROT_KINDS + ".includes(o.kind))return;let r=Number(value);r=Number.isFinite(r)?Math.round((((r%360)+540)%360-180)*10)/10:0;if(r)o.rotation=r;else delete o.rotation;break;}\n case 'shapeType':o.shapeType=")
# 그리기(편집·썸네일·발표·인쇄·PPT 모두 같은 함수): transform과 따로 노는 CSS rotate 속성
R("n.style.left=o.x+'px';n.style.top=o.y+'px';n.style.width=o.w+'px';n.style.height=o.h+'px';n.style.zIndex=o.z||0;",
  "n.style.left=o.x+'px';n.style.top=o.y+'px';n.style.width=o.w+'px';n.style.height=o.h+'px';n.style.zIndex=o.z||0;"
  "{const rot=Number(o.rotation)||0;if(rot&&" + ROT_KINDS + ".includes(o.kind)){n.style.rotate=rot+'deg';n.dataset.rotation=String(rot);}}")

# ── 6) 회전: 손잡이·크기 조절·지우개 ────────────────────────────────
R("e.querySelectorAll('.rv-obj-handle').forEach(h=>h.remove());",
  "e.querySelectorAll('.rv-obj-handle,.pc-rot-handle').forEach(h=>h.remove());")
R("for(const [corner,x,y] of [['nw',0,0],['n',.5,0],['ne',1,0],['e',1,.5],['se',1,1],['s',.5,1],['sw',0,1],['w',0,.5]]){",
  "pcRotHandle(e,o);\n  for(const [corner,x,y] of [['nw',0,0],['n',.5,0],['ne',1,0],['e',1,.5],['se',1,1],['s',.5,1],['sw',0,1],['w',0,.5]]){")
# 돌린 개체 크기 조절: 마우스 움직임을 개체 축으로 바꿔, 잡은 쪽 반대편이 제자리에 있게
R("else if(d.corner){if(d.corner.includes('e'))w=old.w+dx;if(d.corner.includes('s'))h=old.h+dy;if(d.corner.includes('w')){x=old.x+dx;w=old.w-dx;}if(d.corner.includes('n')){y=old.y+dy;h=old.h-dy;}}",
  "else if(d.corner&&d.frames.length===1&&Number(o.rotation)){const q=pcRotResize(old,d.corner,dx,dy,Number(o.rotation));x=q.x;y=q.y;w=q.w;h=q.h;}\n"
  " else if(d.corner){if(d.corner.includes('e'))w=old.w+dx;if(d.corner.includes('s'))h=old.h+dy;if(d.corner.includes('w')){x=old.x+dx;w=old.w-dx;}if(d.corner.includes('n')){y=old.y+dy;h=old.h-dy;}}")
R("if(!pcG&&st.snapEnabled&&!p.alt&&d.corner&&d.frames.length)",
  "if(!pcG&&st.snapEnabled&&!p.alt&&d.corner&&d.frames.length&&!(d.frames.length===1&&Number(obj(d.frames[0].id)?.rotation)))")
R("function eraserPoint(e,el){const r=el.getBoundingClientRect();return [",
  "function eraserPoint(e,el){const pr=pcRotLocal(e,el);if(pr)return pr;const r=el.getBoundingClientRect();return [")

# ── 6) 회전: 상세 설정 칸 ───────────────────────────────────────────
GRID = ".map(([k])=>`<label>${{x:'가로 위치',y:'세로 위치',w:'너비',h:'높이'}[k]}<input type=\"number\" data-prop=\"${k}\" value=\"${Math.round(o[k])}\" min=\"0\" max=\"1120\" ${o.locked?'disabled':''}></label>`).join('')}</div>"
R(GRID, GRID + "${pcRotRow(o)}")
R("case 'bold':formatText('bold');break;",
  "case 'bold':formatText('bold');break;case 'rotateLeft90':pcRotateBy(-90);break;case 'rotateRight90':pcRotateBy(90);break;case 'rotateReset':pcRotateBy(null);break;case 'presenterView':pcPresenterOpen();break;")

# ── 6) 회전: PPT 저장 ───────────────────────────────────────────────
# 글자·그림은 회전을 뺀 자리에서 재고 PowerPoint 회전값(rotate)을 붙임. 꾸밈 그림은 돌린 그대로 잘라 넣음
R("let decor=true;const natives=[];",
  "let decor=true;const natives=[];const pxRot=pxRotOf(o);if(pxRot)el.style.rotate='none';")
R("if(decor){const er=pxGrow(box,10);",
  "if(pxRot){el.style.rotate=pxRot+'deg';pxRotNatives(natives,o,pxRot);}\n   if(decor){const er=pxGrow(box,10);")

# ── 5) 발표자 보기: 단추·연결 ───────────────────────────────────────
R('<button data-action="printDeck" title="전체 슬라이드 인쇄 · PDF 저장"',
  '<button data-action="presenterView" class="pc-pv-btn" title="발표자 보기 — 새 창에 메모·다음 페이지·시간 (이 창은 청중 화면)" aria-label="발표자 보기" type="button">'
  '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="11" height="9" rx="1.5"/><path d="M17 5h4M17 9h4M17 13h4M3 17h18M3 20h12"/></svg>'
  '<span class="rv-tb-label-wide">발표자 보기</span><span class="rv-tb-label-short">메모</span></button>'
  '<button data-action="printDeck" title="전체 슬라이드 인쇄 · PDF 저장"')
R("'presentVolumeMenuToggle','printDeck']).has(action))return;",
  "'presentVolumeMenuToggle','printDeck','presenterView']).has(action))return;")
R("function renderPresentation(first){", "function renderPresentation(first){queueMicrotask(pcPresenterSync);")
R("function closePresentation(){", "function closePresentation(){pcPresenterClose();")
R("<label class=\"prop-row multi\"><span>발표 메모</span><textarea data-prop=\"notes\">${V.esc(p.notes||'')}</textarea></label>",
  "<label class=\"prop-row multi\"><span>발표 메모</span><textarea data-prop=\"notes\">${V.esc(p.notes||'')}</textarea></label><p class=\"inspector-tip\">발표할 때 [발표자 보기]를 누르면 새 창에 이 메모가 보입니다(청중 화면엔 안 보임).</p>")
R("{keys:'Esc',when:'발표',does:'음량 창 닫기, 없으면 발표 끝',where:'pcKeyEditor'}",
  "{keys:'Esc',when:'발표',does:'음량 창 닫기, 없으면 발표 끝',where:'pcKeyEditor'},\n"
  " {keys:'→ ← ↑ ↓ · Space · PageUp/PageDown · 1~9 / 0',when:'발표자 보기 창',does:'발표 화면 넘기기 (Esc: 발표 끝)',where:'pcPresenterKeys'}")

NEW_JS = r"""// ═══ v12.48: 개체 회전 · 발표자 보기 ═══
// (함수 선언만 쓰고 상태는 var: 첫 화면 그리기가 이 코드보다 먼저 돌아도 안전)
function pcRotKind(o){return !!o&&['text','shape','image','line'].includes(o.kind);}
function pcRotNorm(r){r=Number(r);if(!Number.isFinite(r))return 0;return Math.round((((r%360)+540)%360-180)*10)/10;}
function pcRotHandle(el,o){if(!pcRotKind(o))return;const h=document.createElement('div');h.className='pc-rot-handle'+(o.y+o.h>M.H-50&&o.y>=50?'':' pc-rot-below');h.title='끌어서 돌리기 (Shift: 15° 단위)';h.setAttribute('aria-hidden','true');
 const k=1/(st.zoom||1);h.style.setProperty('--pc-rot-s',Math.round(M.clamp(20*k,20,40))+'px');h.style.setProperty('--pc-rot-l',Math.round(M.clamp(16*k,16,34))+'px');
 h.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 4v7h-7"/></svg>';el.append(h);}
function pcRotRow(o){if(!pcRotKind(o))return '';const dis=o.locked?' disabled':'',r=Number(o.rotation)||0;
 return '<div class="pc-rot-row"><label class="pc-rot-field">회전<span><input type="number" data-prop="rotation" value="'+r+'" min="-180" max="180" step="1"'+dis+' aria-label="회전 각도(도)"><i>°</i></span></label>'
  +'<button type="button" class="inspect-button" data-action="rotateLeft90" title="왼쪽으로 90° 돌리기"'+dis+'>↺ 90°</button><button type="button" class="inspect-button" data-action="rotateRight90" title="오른쪽으로 90° 돌리기"'+dis+'>↻ 90°</button><button type="button" class="inspect-button" data-action="rotateReset" title="회전 없애기"'+dis+(r?'':' aria-pressed="true"')+'>0°</button></div>'
  +'<p class="inspector-tip pc-rot-tip">고른 개체 아래 동그란 손잡이를 끌어도 돌아갑니다 · Shift: 15° 단위</p>';}
function pcRotateBy(delta){const list=selected().filter(o=>pcRotKind(o)&&!o.locked);if(!list.length){status('돌릴 수 있는 개체(글상자·도형·그림·선)를 먼저 고르세요.');return false;}
 const ok=mutate(()=>{for(const o of list){const r=delta==null?0:pcRotNorm((Number(o.rotation)||0)+delta);if(r)o.rotation=r;else delete o.rotation;}});
 if(ok!==false)status(delta==null?'회전 없앰':'회전 '+(list.length===1?(Number(list[0].rotation)||0)+'°':list.length+'개 '+(delta>0?'+':'')+delta+'°')+' · Ctrl+Z로 되돌리기');return ok!==false;}
// 돌린 개체 크기 조절: f=잡을 때 틀, 마우스 이동(dx,dy)을 개체 축으로 돌려 계산하고 반대쪽이 제자리에 있게 가운데를 옮김
function pcRotResize(f,corner,dx,dy,deg){const t=deg*Math.PI/180,c=Math.cos(t),s=Math.sin(t),lx=dx*c+dy*s,ly=-dx*s+dy*c;
 let l=0,tp=0,r=f.w,b=f.h;if(corner.includes('e'))r=f.w+lx;if(corner.includes('w'))l=lx;if(corner.includes('s'))b=f.h+ly;if(corner.includes('n'))tp=ly;
 if(r-l<45){if(corner.includes('w'))l=r-45;else r=l+45;}if(b-tp<30){if(corner.includes('n'))tp=b-30;else b=tp+30;}
 const w=Math.min(M.W,r-l),h=Math.min(M.H,b-tp),ox=(l+r)/2-f.w/2,oy=(tp+b)/2-f.h/2,cx=f.x+f.w/2+ox*c-oy*s,cy=f.y+f.h/2+ox*s+oy*c;
 return {x:cx-w/2,y:cy-h/2,w,h};}
// 지우개: 화면 점 → 돌린 개체 안쪽 비율 좌표
function pcRotLocal(e,el){const o=obj(el?.dataset?.objectId),rot=Number(o?.rotation)||0;if(!rot||!pcRotKind(o))return null;
 const r=el.getBoundingClientRect(),k=st.zoom||1,t=rot*Math.PI/180,dx=e.clientX-(r.left+r.width/2),dy=e.clientY-(r.top+r.height/2);
 return [M.clamp(.5+(dx*Math.cos(t)+dy*Math.sin(t))/Math.max(1,el.offsetWidth*k),0,1),M.clamp(.5+(-dx*Math.sin(t)+dy*Math.cos(t))/Math.max(1,el.offsetHeight*k),0,1)];}
var PC_ROT=null;
window.addEventListener('pointerdown',e=>{const h=e.button===0&&e.target.closest?.('#stageHost .pc-rot-handle');if(!h)return;e.preventDefault();e.stopImmediatePropagation();
 const host=h.closest('.rv-object'),o=obj(host?.dataset.objectId),stage=$('#stageHost .rv-stage');if(!o||o.locked||st.editing||!stage)return;
 const sr=stage.getBoundingClientRect(),k=sr.width/M.W,cx=sr.left+(o.x+o.w/2)*k,cy=sr.top+(o.y+o.h/2)*k;
 PC_ROT={id:o.id,pid:e.pointerId,cx,cy,a0:Math.atan2(e.clientY-cy,e.clientX-cx)*180/Math.PI,r0:Number(o.rotation)||0,r:Number(o.rotation)||0,moved:false};
 tryPointerCapture(h,e.pointerId);hideMenus();document.documentElement.classList.add('pc-rotating');},true);
window.addEventListener('pointermove',e=>{const d=PC_ROT;if(!d||e.pointerId!==d.pid)return;e.preventDefault();
 let r=d.r0+Math.atan2(e.clientY-d.cy,e.clientX-d.cx)*180/Math.PI-d.a0;
 if(e.shiftKey)r=Math.round(r/15)*15;else{r=Math.round(r);for(const t of [-180,-90,0,90,180,270,-270])if(Math.abs(r-t)<=3)r=t;}
 r=pcRotNorm(r);d.r=r;d.moved=true;const el=dragElement(d.id);if(el){el.style.rotate=r?r+'deg':'';el.classList.add('rv-drag-moving');}
 const q=$('#quickBar');if(q)q.hidden=true;moveBadge(r+'°',e.clientX+16,e.clientY+20);},{capture:true,passive:false});
function pcRotEnd(e,cancel){const d=PC_ROT;if(!d||(e.type!=='keydown'&&e.pointerId!==d.pid))return;PC_ROT=null;document.documentElement.classList.remove('pc-rotating');$('#rvDragBadge')?.remove();
 const o=obj(d.id),el=dragElement(d.id);el?.classList.remove('rv-drag-moving');
 if(!o||cancel||!d.moved||d.r===d.r0){if(el)el.style.rotate=d.r0?d.r0+'deg':'';updateQuickBar();if(cancel&&d.moved)status('돌리기를 취소했습니다.');return;}
 mutate(()=>{if(d.r)o.rotation=d.r;else delete o.rotation;});status('회전 '+d.r+'° · Shift: 15° 단위 · Ctrl+Z로 되돌리기');}
window.addEventListener('pointerup',e=>pcRotEnd(e,false),true);window.addEventListener('pointercancel',e=>pcRotEnd(e,true),true);
window.addEventListener('keydown',e=>{if(PC_ROT&&e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();pcRotEnd(e,true);}},true);
// 손잡이는 개체 아래쪽(간편편집바는 보통 위쪽). 편집바가 손잡이를 덮으면 손잡이만 반대쪽으로(편집바 자리는 그대로)
EXT.on('afterQuickBar',()=>{const bar=$('#quickBar'),hd=$('#stageHost .pc-rot-handle');if(!bar||bar.hidden||!hd||st.drag)return;
 const hit=(a,b)=>a.left<b.right+4&&a.right>b.left-4&&a.top<b.bottom+4&&a.bottom>b.top-4;if(!hit(bar.getBoundingClientRect(),hd.getBoundingClientRect()))return;
 hd.classList.toggle('pc-rot-below');if(hit(bar.getBoundingClientRect(),hd.getBoundingClientRect()))hd.classList.toggle('pc-rot-below');});
// PPT: 회전값·회전 중심(개체 가운데) 맞추기
function pxRotOf(o){const r=Number(o.rotation)||0;return r&&pcRotKind(o)?r:0;}
function pxRotNatives(list,o,deg){const t=deg*Math.PI/180,c=Math.cos(t),s=Math.sin(t),X=o.x+o.w/2,Y=o.y+o.h/2;
 for(const n of list){const q=n.opts;if(!q||q.x==null||q.y==null)continue;const w=(q.sizing?.w??q.w)*96,h=(q.sizing?.h??q.h)*96,px=q.x*96+w/2,py=q.y*96+h/2,dx=px-X,dy=py-Y;
  q.x=(X+dx*c-dy*s-w/2)/96;q.y=(Y+dx*s+dy*c-h/2)/96;q.rotate=((deg%360)+360)%360;}}

// 5) 발표자 보기 — 별도 창(같은 출처 빈 창)에 이 창의 그리기 함수로 그림. 넘기기는 이 창의 발표 함수를 그대로 부름
var PC_PV={win:null,timer:0,t0:0,paused:0,acc:0,font:22};
const PC_PV_CSS=`html,body{margin:0;height:100%;background:#0B1220;color:#E5EAF2;font-family:Pretendard,"Malgun Gothic",system-ui,sans-serif;overflow:hidden}
*{box-sizing:border-box}button{font:inherit;color:inherit;cursor:pointer}
.pv{display:grid;grid-template-rows:auto 1fr;height:100%;gap:12px;padding:12px 16px 16px}
.pv-top{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.pv-time{display:flex;align-items:center;gap:8px;padding:6px 8px 6px 14px;border-radius:12px;background:#121B2E;border:1px solid #22304A}
.pv-time b{font-size:28px;font-weight:700;font-variant-numeric:tabular-nums;letter-spacing:.02em;min-width:94px}
.pv-time.paused b{color:#F5B83D}
.pv-btn{border:1px solid #2C3B57;background:#17223A;border-radius:9px;padding:7px 12px;font-size:14px;line-height:1.1}
.pv-btn:hover{background:#1F2D4A}.pv-btn:focus-visible{outline:2px solid #60A5FA;outline-offset:2px}
.pv-btn.primary{background:#2563EB;border-color:#2563EB;color:#fff}.pv-btn.primary:hover{background:#1D4ED8}
.pv-count{font-size:15px;color:#9FB0C8;font-variant-numeric:tabular-nums}
.pv-count b{color:#E5EAF2;font-size:18px}
.pv-spacer{flex:1}.pv-clock{font-size:18px;color:#C9D4E5;font-variant-numeric:tabular-nums}
.pv-main{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(300px,1fr);gap:16px;min-height:0}
.pv-col{display:flex;flex-direction:column;gap:8px;min-height:0}
.pv-label{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:600;color:#8EA0BA;letter-spacing:.02em;min-height:28px}
.pv-label span{color:#E5EAF2;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pv-frame{position:relative;border-radius:10px;overflow:hidden;background:#111A2C;box-shadow:0 0 0 1px #22304A}
.pv-cur{flex:1;min-height:0}.pv-next{aspect-ratio:1120/790;flex:none}
.pv-frame .rv-stage{pointer-events:none}
.pv-nav{display:flex;gap:8px;justify-content:center}.pv-nav .pv-btn{min-width:120px;padding:10px 16px;font-size:16px}
.pv-end{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;gap:6px;padding:16px 18px;color:#C9D4E5;font-size:14px;overflow:auto}
.pv-end b{font-size:16px;color:#E5EAF2}.pv-end kbd{display:inline-block;min-width:22px;margin-right:8px;padding:1px 6px;border-radius:6px;background:#22304A;color:#E5EAF2;text-align:center;font:600 12px/1.6 inherit}
.pv-notes{flex:1;min-height:0;overflow:auto;padding:14px 16px;border-radius:10px;background:#F8FAFC;color:#0F172A;line-height:1.6;white-space:pre-wrap;word-break:keep-all;overflow-wrap:anywhere}
.pv-notes.empty{color:#64748B;font-size:15px!important;background:#E8EDF4}
.pv-font{margin-left:auto;display:flex;gap:4px}.pv-font .pv-btn{padding:3px 9px;font-size:13px}
.pv-poster{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:#172B43;color:#fff;font-size:20px}
@media (max-width:820px){.pv-main{grid-template-columns:1fr;grid-template-rows:minmax(0,1fr) auto}.pv-next{display:none}}`;
function pcPvEl(id){return PC_PV?.win&&!PC_PV.win.closed?PC_PV.win.document.getElementById(id):null;}
function pcPresentNextId(){const id=st.presentId,P=st.project.pages,tree=navigationTree();if(!tree.hasEdges){const i=P.findIndex(p=>p.id===id);return P[i+1]?.id||null;}
 if((tree.depth.get(id)||0)<2)return null;const sib=tree.children.get(tree.parent.get(id))||[];return sib[sib.indexOf(id)+1]||null;}
function pcPvStage(host,p){const s=V.renderPage(p,CATALOG,PALETTES,'present');
 for(const m of [...s.querySelectorAll('video,audio')]){m.removeAttribute('autoplay');m.autoplay=false;m.preload='none';try{m.pause();}catch(e){}
  const ph=host.ownerDocument.createElement('div');ph.className='pv-poster';if(m.tagName==='VIDEO'&&m.poster){const img=host.ownerDocument.createElement('img');img.src=m.poster;img.alt='';img.style.cssText='width:100%;height:100%;object-fit:contain';ph.append(img);}else ph.textContent=m.tagName==='VIDEO'?'▶ 영상':'♪ 음악';m.replaceWith(ph);}
 try{navigationNumberLabels(s,p);decorateCourtMainIcons(s,p);}catch(e){}
 host.replaceChildren(s);try{fitSampleText(s,p);}catch(e){}pcPvFit(host);}
function pcPvFit(host){const s=host?.querySelector(':scope > .rv-stage');if(!s)return;const W=host.clientWidth,H=host.clientHeight,k=Math.max(.05,Math.min(W/M.W,H/M.H));
 s.style.cssText+=`;position:absolute;left:${((W-M.W*k)/2).toFixed(1)}px;top:${((H-M.H*k)/2).toFixed(1)}px;width:${M.W}px;height:${M.H}px;translate:none;transform-origin:0 0;transform:scale(${k.toFixed(4)})`;}
function pcPvTime(){const ms=PC_PV.acc+(PC_PV.paused?0:performance.now()-PC_PV.t0),s=Math.floor(ms/1000),h=Math.floor(s/3600),m=Math.floor(s/60)%60,ss=String(s%60).padStart(2,'0');
 return h?h+':'+String(m).padStart(2,'0')+':'+ss:String(m).padStart(2,'0')+':'+ss;}
function pcPvTick(){const w=PC_PV.win;if(!w||w.closed){pcPresenterGone();return;}const t=pcPvEl('pvElapsed');if(t)t.textContent=pcPvTime();
 const c=pcPvEl('pvClock');if(c)c.textContent=new Date().toLocaleTimeString('ko-KR',{hour:'numeric',minute:'2-digit'});}
function pcPresenterSync(){if(!PC_PV||!st.presentId||$('#presentation').hidden)return;pcNotesDockSync();const w=PC_PV.win;if(!w||w.closed){if(w)pcPresenterGone();return;}
 const d=w.document,P=st.project.pages,p=P.find(x=>x.id===st.presentId);if(!p)return;const i=P.indexOf(p);
 d.title='발표자 보기 · '+(i+1)+'/'+P.length+' '+(p.title||'');
 d.getElementById('pvCount').innerHTML='<b>'+(i+1)+'</b> / '+P.length;d.getElementById('pvCurTitle').textContent=p.title||'';
 pcPvStage(d.getElementById('pvCur'),p);
 const nid=pcPresentNextId(),np=nid&&P.find(x=>x.id===nid),nx=d.getElementById('pvNext');
 if(np){pcPvStage(nx,np);d.getElementById('pvNextTitle').textContent=np.title||'';}
 else{const g=navigationGroups(p).slice(0,NAV.MAX),box=d.createElement('div');box.className='pv-end';
  box.innerHTML=g.length?'<b>이 페이지에서 고르기</b>'+g.map((x,k)=>'<div><kbd>'+(k+1)+'</kbd>'+V.esc(P.find(q=>q.id===x.target)?.title||'')+'</div>').join(''):'<b>마지막 페이지</b><div>다음 페이지가 없습니다</div>';
  nx.replaceChildren(box);d.getElementById('pvNextTitle').textContent='';}
 const notes=String(p.notes||'').trim(),nn=d.getElementById('pvNotes');nn.classList.toggle('empty',!notes);nn.style.fontSize=PC_PV.font+'px';
 nn.textContent=notes||'이 페이지에는 발표 메모가 없습니다.\n편집 화면 › 페이지 설정 › 페이지 배경 · 전환 · 메모 › 발표 메모에 적으면 여기에 보입니다.';nn.scrollTop=0;pcPvTick();}
function pcPresenterKeys(e){const k=e.key;if(e.ctrlKey||e.metaKey||e.altKey||e.target?.closest?.('input,textarea,select'))return;
 if(k==='Escape'){e.preventDefault();closePresentation();return;}
 if(k==='ArrowRight'||k==='PageDown'||k===' '){e.preventDefault();if(e.target?.closest?.('button')&&k===' ')return;navigateSibling(1);return;}
 if(k==='ArrowLeft'||k==='PageUp'){e.preventDefault();navigateSibling(-1);return;}
 if(k==='ArrowUp'){e.preventDefault();navigateParent();return;}if(k==='ArrowDown'){e.preventDefault();navigateBox(1);return;}
 if(/^[0-9]$/.test(k)){e.preventDefault();if(!e.repeat)(k==='0'?navigateHome():navigateBox(Number(k)));}}
function pcPresenterOpen(){if($('#presentation').hidden)return false;
 if(PC_PV.win&&!PC_PV.win.closed){PC_PV.win.focus();pcPresenterSync();return true;}
 let w=null;try{w=window.open('','pcPresenterView','popup=yes,width=1280,height=800');}catch(e){w=null;}
 if(!w){pcNotesDock(true);status('팝업이 막혀 발표자 보기 창을 열지 못했습니다. 주소창의 팝업 차단을 허용하면 새 창으로 열립니다. 지금은 화면 아래에 메모를 띄웠습니다.');return false;}
 const d=w.document;d.open();d.write('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>발표자 보기</title></head><body></body></html>');d.close();
 for(const s of document.querySelectorAll('style')){if(s.closest('svg')||s.closest('.rv-stage'))continue;const c=d.createElement('style');c.textContent=s.textContent;d.head.append(c);}
 const own=d.createElement('style');own.textContent=PC_PV_CSS;d.head.append(own);
 d.body.innerHTML='<div class="pv" role="application" aria-label="발표자 보기"><header class="pv-top"><div class="pv-time" id="pvTime"><b id="pvElapsed" aria-label="지난 시간">00:00</b><button class="pv-btn" id="pvPause" type="button">멈춤</button><button class="pv-btn" id="pvReset" type="button" title="시간을 0부터 다시">0부터</button></div>'
  +'<div class="pv-count" id="pvCount"></div><div class="pv-spacer"></div><div class="pv-clock" id="pvClock" aria-label="지금 시각"></div><button class="pv-btn" id="pvExit" type="button" title="발표 끝내기 (Esc)">발표 끝</button></header>'
  +'<main class="pv-main"><section class="pv-col"><div class="pv-label">지금 화면 <span id="pvCurTitle"></span></div><div class="pv-frame pv-cur" id="pvCur"></div><div class="pv-nav"><button class="pv-btn" id="pvPrev" type="button" title="이전 (←)">‹ 이전</button><button class="pv-btn primary" id="pvNextBtn" type="button" title="다음 (→ · Space)">다음 ›</button></div></section>'
  +'<aside class="pv-col"><div class="pv-label">다음 <span id="pvNextTitle"></span></div><div class="pv-frame pv-next" id="pvNext"></div><div class="pv-label">발표 메모<div class="pv-font"><button class="pv-btn" id="pvFontDown" type="button" title="메모 글씨 작게" aria-label="메모 글씨 작게">가−</button><button class="pv-btn" id="pvFontUp" type="button" title="메모 글씨 크게" aria-label="메모 글씨 크게">가＋</button></div></div><div class="pv-notes" id="pvNotes" tabindex="0" aria-live="polite"></div></aside></main></div>';
 PC_PV.win=w;PC_PV.t0=performance.now();PC_PV.acc=0;PC_PV.paused=0;
 const on=(id,f)=>d.getElementById(id).addEventListener('click',f);
 on('pvNextBtn',()=>navigateSibling(1));on('pvPrev',()=>navigateSibling(-1));on('pvExit',()=>closePresentation());
 on('pvPause',()=>{if(PC_PV.paused){PC_PV.paused=0;PC_PV.t0=performance.now();}else{PC_PV.acc+=performance.now()-PC_PV.t0;PC_PV.paused=1;}d.getElementById('pvPause').textContent=PC_PV.paused?'계속':'멈춤';d.getElementById('pvTime').classList.toggle('paused',!!PC_PV.paused);pcPvTick();});
 on('pvReset',()=>{PC_PV.acc=0;PC_PV.t0=performance.now();pcPvTick();});
 const font=k=>{PC_PV.font=M.clamp(PC_PV.font+k,14,48);d.getElementById('pvNotes').style.fontSize=PC_PV.font+'px';};on('pvFontDown',()=>font(-2));on('pvFontUp',()=>font(2));
 d.addEventListener('keydown',pcPresenterKeys);
 w.addEventListener('resize',()=>{pcPvFit(d.getElementById('pvCur'));pcPvFit(d.getElementById('pvNext'));});
 w.addEventListener('pagehide',()=>{if(PC_PV.win===w)pcPresenterGone();});
 clearInterval(PC_PV.timer);PC_PV.timer=setInterval(pcPvTick,500);pcNotesDock(false);
 pcPresenterSync();d.fonts?.ready?.then(()=>{if(PC_PV.win===w)pcPresenterSync();});
 $('#presentation [data-action=presenterView]')?.setAttribute('aria-pressed','true');status('발표자 보기를 새 창에 열었습니다. 이 창은 청중 화면(프로젝터)으로 쓰세요.');return true;}
function pcPresenterGone(){clearInterval(PC_PV.timer);PC_PV.timer=0;PC_PV.win=null;$('#presentation [data-action=presenterView]')?.setAttribute('aria-pressed','false');}
function pcPresenterClose(){if(!PC_PV)return;const w=PC_PV.win;pcPresenterGone();try{if(w&&!w.closed)w.close();}catch(e){}pcNotesDock(false);}
window.addEventListener('pagehide',()=>{try{PC_PV?.win?.close();}catch(e){}});
// 팝업이 막혔을 때: 발표 화면 아래 메모 칸
function pcNotesDock(show){let dock=$('#pcNotesDock');if(!show){if(dock)dock.hidden=true;return;}
 if(!dock){dock=document.createElement('div');dock.id='pcNotesDock';dock.className='pc-notes-dock';dock.setAttribute('role','region');dock.setAttribute('aria-label','발표 메모');
  dock.innerHTML='<div class="pc-notes-head"><strong>발표 메모</strong><span>청중 화면에도 보이니 연습할 때 쓰세요</span><button type="button" class="pc-notes-close" aria-label="메모 닫기" title="메모 닫기">✕</button></div><div class="pc-notes-body"></div>';
  dock.querySelector('.pc-notes-close').addEventListener('click',()=>{dock.hidden=true;});$('#presentation').append(dock);}
 dock.hidden=false;pcNotesDockSync();}
function pcNotesDockSync(){const dock=$('#pcNotesDock');if(!dock||dock.hidden)return;const p=st.project.pages.find(x=>x.id===st.presentId),t=String(p?.notes||'').trim();
 const b=dock.querySelector('.pc-notes-body');b.textContent=t||'이 페이지에는 발표 메모가 없습니다.';b.classList.toggle('empty',!t);}
"""
R("// Fonts may finish loading after the first layout pass.", NEW_JS + "// Fonts may finish loading after the first layout pass.")

CSS = """/* ══════ v12.48: 개체 회전 · 발표자 보기 ══════ */
#stageHost .pc-rot-handle{--pc-rot-s:20px;--pc-rot-l:16px;position:absolute;left:calc(50% - var(--pc-rot-s)/2);top:calc(-1*(var(--pc-rot-s) + var(--pc-rot-l)));width:var(--pc-rot-s);height:var(--pc-rot-s);border-radius:50%;background:#fff;border:calc(var(--pc-rot-s)/10) solid #1882c3;color:#1882c3;box-shadow:0 2px 6px #233a4c33;z-index:9001;cursor:grab;display:flex;align-items:center;justify-content:center;touch-action:none}
#stageHost .pc-rot-handle::after{content:'';position:absolute;left:50%;top:100%;width:calc(var(--pc-rot-s)/10);height:var(--pc-rot-l);transform:translateX(-50%);background:#1882c3;pointer-events:none}
#stageHost .pc-rot-handle.pc-rot-below{top:auto;bottom:calc(-1*(var(--pc-rot-s) + var(--pc-rot-l)))}
#stageHost .pc-rot-handle.pc-rot-below::after{top:auto;bottom:100%}
#stageHost .pc-rot-handle svg{width:62%;height:62%;display:block;pointer-events:none}
#stageHost .pc-rot-handle:hover{background:#EAF4FB}
html.pc-rotating,html.pc-rotating *{cursor:grabbing!important;user-select:none}
.pc-rot-row{display:flex;align-items:flex-end;gap:5px;margin-top:10px;flex-wrap:nowrap}
.pc-rot-row .pc-rot-field{display:flex;flex-direction:column;gap:3px;font-size:12px;color:#475569;margin-right:1px;flex:none}
.pc-rot-row .pc-rot-field>span{display:inline-flex;align-items:center;gap:2px}
.pc-rot-row .pc-rot-field input{width:58px}
.pc-rot-row .pc-rot-field i{font-style:normal;color:#64748B}
.pc-rot-row .inspect-button{flex:1 1 0;min-width:0;padding-left:2px;padding-right:2px;white-space:nowrap;font-size:12.5px}
.pc-rot-row .inspect-button[aria-pressed="true"]{background:#EAF1FE;color:#1D4ED8;border-color:#BCD0F5}
.inspector-tip.pc-rot-tip{margin-top:4px}
#presentation [data-action=presenterView] svg{width:16px;height:16px;flex:none}
#presentation [data-action=presenterView][aria-pressed="true"]{box-shadow:inset 0 0 0 2px var(--rv-present-accent,#376BA6)}
#presentation .pc-notes-dock{position:fixed;left:50%;bottom:14px;transform:translateX(-50%);width:min(880px,calc(100vw - 32px));max-height:32vh;display:flex;flex-direction:column;border-radius:12px;background:rgba(15,23,42,.94);color:#F1F5F9;box-shadow:0 10px 30px rgba(2,6,23,.35);z-index:60;overflow:hidden}
#presentation .pc-notes-dock[hidden]{display:none}
#presentation .pc-notes-head{display:flex;align-items:center;gap:10px;padding:8px 10px 8px 16px;border-bottom:1px solid rgba(148,163,184,.25);font-size:13px}
#presentation .pc-notes-head span{color:#94A3B8;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#presentation .pc-notes-close{border:0;background:transparent;color:#CBD5E1;width:30px;height:30px;border-radius:8px;font-size:15px;cursor:pointer}
#presentation .pc-notes-close:hover{background:rgba(148,163,184,.18)}
#presentation .pc-notes-body{padding:12px 16px 14px;overflow:auto;font-size:18px;line-height:1.6;white-space:pre-wrap;word-break:keep-all;overflow-wrap:anywhere}
#presentation .pc-notes-body.empty{color:#94A3B8;font-size:15px}
"""
R("</style><script id=\"embedded-font-license\"", CSS + "</style><script id=\"embedded-font-license\"")

open(out, 'w', encoding='utf-8').write(html)
print('ok', out, len(html))
