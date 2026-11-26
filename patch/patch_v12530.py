"""PageCraft v12.53.0 — 숨기기·레이저·애니메이션
기준: v12.52.0 Lite.
 1) 발표에서 숨기기: 페이지 목록 [숨김]·페이지 설정 칸 → page.hidden=true(보이면 필드 없음). 발표 ←→·Space·처음·발표자 보기 '다음'·인쇄에서 건너뜀.
    편집·썸네일(흐리게+'숨김')·PPT(숨긴 슬라이드 show=0)에는 남음. 연결 상자·숫자키로는 갈 수 있음. 모든 페이지를 숨길 수는 없음
 2) 레이저 포인터: 발표 도구줄 [레이저]·L 키(한글 입력 상태도 e.code) → 마우스 따라 빨간 점, 화면 커서 숨김. Esc = 레이저 끄기 먼저.
    발표자 보기 창: [레이저]·L, '지금 화면' 위에서 움직이면 청중 화면 같은 자리에 점. 문서 데이터 아님
 3) 등장 효과(애니메이션): 선택 개체 '등장 효과 · 발표' 칸 — 효과 5가지(서서히·아래에서·왼쪽에서·확대·닦아내기)·순서 번호(같은 번호 = 함께)·미리 보기.
    발표 → · Space · PageDown · [뒷페이지]: 남은 효과 먼저, ← 는 하나씩 되돌림, 앞 페이지로 돌아오면 다 나타난 모습. 편집 화면 번호 배지.
    발표자 보기: 아직 안 나온 개체는 흐리게, '다음'은 같은 페이지 다음 효과. 썸네일·인쇄·PPT = 다 나타난 모습. 저장값 o.anim={fx,step} — 없으면 필드 없음
 + 발표 화면에서도 Space·PageDown = 다음, PageUp = 이전(발표자 보기 창과 같게, 리모컨 클리커)
Usage: python3 -I patch/patch_v12530.py <PageCraft_v12.52.0_Lite.html> <out.html>"""
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
assert "BUILD_VERSION='PageCraft v12.52.0 · 눈금자·안내선·쪽 번호·개체 이름'" in html, 'needs v12.52.0'
assert 'pc-v12530' not in html, 'already patched'

# ── 1) 변경 ──────────────────────────────────────────────
# CSS는 <style id="pc-ui-css"> 안 해당 구역 규칙을 직접 R()로 고칠 것. 맨 아래 덧붙이기·!important 덧칠 금지.
# 새 JS에는 주석 /*pc-v12530*/ 를 넣어 '이미 적용' 검사가 작동하게 할 것.

# 0) 모델: 새 필드 정리(없거나 기본값이면 필드 없음 → 옛 문서 그대로)
R("if(!['fade','none','slide-left','slide-right','slide-up','slide-down','blur'].includes(p.transition.type))p.transition.type='fade';",
  "if(!['fade','none','slide-left','slide-right','slide-up','slide-down','blur'].includes(p.transition.type))p.transition.type='fade';\n  if(p.hidden)p.hidden=true;else delete p.hidden; /*pc-v12530 발표에서 숨기기*/")
R("if(nm)c.name=nm;else delete c.name;} /*pc-v12520 개체 이름*/",
  "if(nm)c.name=nm;else delete c.name;} /*pc-v12520 개체 이름*/"
  "if('anim' in c){const a=c.anim,fx=a&&['fade','up','left','zoom','wipe'].includes(a.fx)?a.fx:null;if(fx)c.anim={fx,step:Math.round(clamp(Number(a.step)||1,1,99))};else delete c.anim;} /*pc-v12530 등장 효과*/")

# 1) 숨기기: 발표 넘김·다음 미리보기·단추 상태가 숨긴 페이지를 건너뜀
R("function stepLinear(delta){const i=st.project.pages.findIndex(p=>p.id===st.presentId),j=i+delta;if(j>=0&&j<st.project.pages.length)return slideTo(st.project.pages[j].id);return false;}",
  "function stepLinear(delta){const P=st.project.pages.map(p=>p.id),id=pcSkipHidden(P,P.indexOf(st.presentId),delta);if(!id)return false;PC_AN.back=delta<0;try{return slideTo(id);}finally{PC_AN.back=false;}} /*pc-v12530*/")
R("function navigateSibling(delta){\n const tree=navigationTree();",
  "function navigateSibling(delta){\n if(pcAnStep(delta))return true; /*pc-v12530 남은 등장 효과 먼저*/\n const tree=navigationTree();")
R(" const parent=tree.parent.get(st.presentId),siblings=tree.children.get(parent)||[],idx=siblings.indexOf(st.presentId),next=siblings[idx+delta];\n if(next)return slideTo(next,true,{type:delta>0?'slide-left':'slide-right'});",
  " const parent=tree.parent.get(st.presentId),siblings=tree.children.get(parent)||[],idx=siblings.indexOf(st.presentId),next=pcSkipHidden(siblings,idx,delta);\n if(next){PC_AN.back=delta<0;try{return slideTo(next,true,{type:delta>0?'slide-left':'slide-right'});}finally{PC_AN.back=false;}}")
R("const root=st.project.pages[0]?.id;", "const root=navigationTree().hasEdges?st.project.pages[0]?.id:pcFirstShown();")
R("return P[i+1]?.id||null;", "return pcSkipHidden(P.map(p=>p.id),i,1);")
R("return sib[sib.indexOf(id)+1]||null;", "return pcSkipHidden(sib,sib.indexOf(id),1);")
R("canPrev=i>0;canNext=i<st.project.pages.length-1;", "const ids=st.project.pages.map(x=>x.id);canPrev=!!pcSkipHidden(ids,i,-1);canNext=!!pcSkipHidden(ids,i,1);")
R("canPrev=i>0;canNext=i>=0&&i<sib.length-1;", "canPrev=i>=0&&!!pcSkipHidden(sib,i,-1);canNext=i>=0&&!!pcSkipHidden(sib,i,1);")
R(" prev.disabled=!canPrev;next.disabled=!canNext;prev.title=canPrev?'이전 페이지 (←)':(hint||'첫 페이지입니다');next.title=canNext?'다음 페이지 (→)':(hint||'마지막 페이지입니다');",
  " const an=PC_AN.pageId===p.id&&PC_AN.shown<PC_AN.steps.length;if(an)canNext=true;if(PC_AN.pageId===p.id&&PC_AN.shown>0)canPrev=true; /*pc-v12530 등장 효과*/\n"
  " prev.disabled=!canPrev;next.disabled=!canNext;prev.title=canPrev?'이전 페이지 (←)':(hint||'첫 페이지입니다');next.title=canNext?'다음 페이지 (→)':(hint||'마지막 페이지입니다');if(an)next.title='다음 등장 효과 (→ · Space)';")
R("renderAll(); startPresentation(st.project.pages[0].id);", "renderAll(); startPresentation(pcFirstShown());")
# 인쇄: 숨긴 페이지 빼고(전부 숨겼으면 전부)
R(" for(const p of st.project.pages){\n  const sheet=document.createElement('div');sheet.className='rv-print-page';",
  " const pcPrint=(a=>a.length?a:st.project.pages)(st.project.pages.filter(p=>!p.hidden)); /*pc-v12530 숨긴 페이지 빼기*/\n for(const p of pcPrint){\n  const sheet=document.createElement('div');sheet.className='rv-print-page';")
R("if(s&&st.project.pages[i])fitSampleText(s,st.project.pages[i]);}", "if(s&&pcPrint[i])fitSampleText(s,pcPrint[i]);}")
# PPT: 숨긴 슬라이드(PowerPoint와 같은 뜻)
R("const slide=pptx.addSlide();const sr=", "const slide=pptx.addSlide();if(page.hidden)slide.hidden=true;const sr=")
# 페이지 목록: [숨김] 단추 + 흐린 썸네일
R("for(const [a,label]of [['pageUp','↑'],['pageDown','↓'],['pageClone','복사'],['pageDelete','삭제']])",
  "for(const [a,label]of [['pageUp','↑'],['pageDown','↓'],['pageHide','숨김'],['pageClone','복사'],['pageDelete','삭제']])")
R("  row.querySelector('[data-action=\"pageDown\"]').disabled=i===st.project.pages.length-1;\n",
  "  row.querySelector('[data-action=\"pageDown\"]').disabled=i===st.project.pages.length-1;\n"
  "  {const hb=row.querySelector('[data-action=\"pageHide\"]'),hid=!!p.hidden;row.classList.toggle('pc-pg-hidden',hid);hb.textContent=hid?'보임':'숨김';hb.title=hid?'발표에 다시 보이기':'발표에서 이 페이지 숨기기 (편집·PPT에는 남음)';hb.setAttribute('aria-pressed',String(hid));if(hid)btn.setAttribute('aria-label',`${i+1}번 ${p.title} 페이지 이동 (발표에서 숨김)`);} /*pc-v12530*/\n")
R("case 'pageClone':clonePage(id);break;", "case 'pageHide':pcPgHideToggle(id||current().id);break;case 'pageClone':clonePage(id);break;")
# 페이지 설정 칸: 숨기기 칸
R("${p.hideDecor?'양식 장식선 다시 보이기':'양식 장식선 숨기기 (이 페이지)'}</button>`+dropdown('이 페이지로 들어올 때의 전환'",
  "${p.hideDecor?'양식 장식선 다시 보이기':'양식 장식선 숨기기 (이 페이지)'}</button><label class=\"rv-view-outline-toggle\"><input id=\"pcPgHide\" type=\"checkbox\" ${p.hidden?'checked':''}> 발표에서 이 페이지 숨기기 (편집·PPT에는 남음)</label>`+dropdown('이 페이지로 들어올 때의 전환'")

# 2) 레이저: 도구줄 단추·키·발표 끝낼 때 끄기
R('<button data-action="presenterView" class="pc-pv-btn"',
  '<button data-action="presentLaser" class="pc-lz-btn" aria-pressed="false" title="레이저 포인터 (L) — 마우스를 따라 빨간 점 · Esc로 끄기" aria-label="레이저 포인터" type="button"><svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="16" cy="8" r="3.2" fill="currentColor" stroke="none"/><path d="M13.6 10.4 4 20M18.6 3.6l1-1M20.4 5.4l1.4-.4M14.6 2.6l.4-1.4"/></svg><span class="rv-tb-label-wide">레이저</span><span class="rv-tb-label-short">레이저</span></button><button data-action="presenterView" class="pc-pv-btn"')
R("'presentVolumeMenuToggle','printDeck','presenterView']).has(action)", "'presentVolumeMenuToggle','printDeck','presenterView','presentLaser']).has(action)")
R("case 'presenterView':pcPresenterOpen();break;", "case 'presenterView':pcPresenterOpen();break;case 'presentLaser':pcLaserToggle();break;")
R("function closePresentation(){pcPresenterClose();", "function closePresentation(){pcLaserToggle(false);pcPresenterClose();")
# 발표 키: Esc(레이저 먼저)·L·Space·PageDown·PageUp
R("   if(pop&&!pop.hidden){e.preventDefault();pop.hidden=true;$('#rvVolumeMenuToggle')?.setAttribute('aria-expanded','false');return;}\n   e.preventDefault();closePresentation();return;",
  "   if(pop&&!pop.hidden){e.preventDefault();pop.hidden=true;$('#rvVolumeMenuToggle')?.setAttribute('aria-expanded','false');return;}\n"
  "   if(PC_LZ.on){e.preventDefault();pcLaserToggle(false);return;} /*pc-v12530*/\n   e.preventDefault();closePresentation();return;")
R("  if(/^[0-9]$/.test(e.key)){e.preventDefault();if(!e.repeat)(e.key==='0'?navigateHome():navigateBox(Number(e.key)));return;}\n  if(e.key==='ArrowRight'){e.preventDefault();navigateSibling(1);return;}",
  "  if(e.code==='KeyL'&&!e.shiftKey){e.preventDefault();if(!e.repeat)pcLaserToggle();return;} /*pc-v12530 레이저·클리커 키*/\n"
  "  if(e.key===' '||e.key==='PageDown'){if(e.key===' '&&e.target?.closest?.('button,video,audio'))return;e.preventDefault();navigateSibling(1);return;}\n"
  "  if(e.key==='PageUp'){e.preventDefault();navigateSibling(-1);return;}\n"
  "  if(/^[0-9]$/.test(e.key)){e.preventDefault();if(!e.repeat)(e.key==='0'?navigateHome():navigateBox(Number(e.key)));return;}\n  if(e.key==='ArrowRight'){e.preventDefault();navigateSibling(1);return;}")
# 발표자 보기 창: 레이저 단추·키·'지금 화면' 위 움직임 → 청중 화면, 등장 효과 상태
R("function pcPresenterKeys(e){const k=e.key;if(e.ctrlKey||e.metaKey||e.altKey||e.target?.closest?.('input,textarea,select'))return;\n if(k==='Escape'){e.preventDefault();closePresentation();return;}",
  "function pcPresenterKeys(e){const k=e.key;if(e.ctrlKey||e.metaKey||e.altKey||e.target?.closest?.('input,textarea,select'))return;\n"
  " if(k==='Escape'){e.preventDefault();if(PC_LZ.on){pcLaserToggle(false);return;}closePresentation();return;}\n if(e.code==='KeyL'&&!e.shiftKey){e.preventDefault();if(!e.repeat)pcLaserToggle();return;} /*pc-v12530*/")
R("<button class=\"pv-btn primary\" id=\"pvNextBtn\" type=\"button\" title=\"다음 (→ · Space)\">다음 ›</button></div></section>",
  "<button class=\"pv-btn primary\" id=\"pvNextBtn\" type=\"button\" title=\"다음 (→ · Space)\">다음 ›</button><button class=\"pv-btn pv-lz\" id=\"pvLaser\" type=\"button\" aria-pressed=\"false\" title=\"레이저 포인터 (L) — 이 &#39;지금 화면&#39; 위에서 움직이면 청중 화면 같은 자리에 빨간 점\">● 레이저</button></div></section>")
R(" d.addEventListener('keydown',pcPresenterKeys);",
  " d.addEventListener('keydown',pcPresenterKeys);on('pvLaser',()=>pcLaserToggle());{const cur=d.getElementById('pvCur');cur.addEventListener('pointermove',pcLaserFromPv);cur.addEventListener('pointerleave',pcLaserHide);}d.body.classList.toggle('pv-laser-on',PC_LZ.on);d.getElementById('pvLaser').setAttribute('aria-pressed',String(PC_LZ.on)); /*pc-v12530*/")
R("function pcPvStage(host,p){const s=V.renderPage(p,CATALOG,PALETTES,'present');",
  "function pcPvStage(host,p,shown){const s=V.renderPage(p,CATALOG,PALETTES,'present');if(shown!=null)pcAnMark(s,p,shown);")
R(" d.getElementById('pvCount').innerHTML='<b>'+(i+1)+'</b> / '+P.length;d.getElementById('pvCurTitle').textContent=p.title||'';\n pcPvStage(d.getElementById('pvCur'),p);\n const nid=pcPresentNextId(),np=nid&&P.find(x=>x.id===nid),nx=d.getElementById('pvNext');\n if(np){pcPvStage(nx,np);d.getElementById('pvNextTitle').textContent=np.title||'';}",
  " const A=PC_AN.pageId===p.id?PC_AN:{steps:[],shown:0},anLeft=A.shown<A.steps.length; /*pc-v12530 등장 효과*/\n"
  " d.getElementById('pvCount').innerHTML='<b>'+(i+1)+'</b> / '+P.length+(A.steps.length?' <small class=\"pv-an\">효과 '+A.shown+'/'+A.steps.length+'</small>':'');d.getElementById('pvCurTitle').textContent=p.title||'';\n"
  " pcPvStage(d.getElementById('pvCur'),p,A.shown);\n const nid=anLeft?p.id:pcPresentNextId(),np=nid&&P.find(x=>x.id===nid),nx=d.getElementById('pvNext');\n"
  " if(np){pcPvStage(nx,np,anLeft?A.shown+1:0);d.getElementById('pvNextTitle').textContent=anLeft?'같은 페이지 · 효과 '+(A.shown+1)+'/'+A.steps.length:(np.title||'');}")
R(".pv-poster{position:absolute;inset:0;display:flex;",
  ".pv-frame .rv-stage>.rv-object.pc-an-wait{visibility:visible;opacity:.22}.pv-an{font-size:12px;color:#93C5FD;margin-left:6px}\n"
  ".pv-btn.pv-lz[aria-pressed=true]{background:#7F1D1D;border-color:#F87171;color:#FECACA}.pv-laser-on .pv-cur{cursor:crosshair}\n"
  ".pv-poster{position:absolute;inset:0;display:flex;")

# 3) 등장 효과: 발표 그리기 때 상태 준비 · 편집 화면 번호 배지 · 설정 칸
R("const slide=V.renderPage(p,CATALOG,PALETTES,'present');slide.style.transform='scale(1)';",
  "const slide=V.renderPage(p,CATALOG,PALETTES,'present');slide.style.transform='scale(1)';pcAnPrep(slide,p);")
R("markSelection();updateQuickBar();pcRulerRender();}", "markSelection();updateQuickBar();pcRulerRender();pcAnBadges();}")
R("<button class=\"inspect-button\" data-action=\"links\">전체 연결도 보기</button>`);\n }else{html+=accordion('layout','배치와 위치','위치·크기·잠금 설정',false)+accordion('content','콘텐츠 및 꾸밈','대상을 선택하세요.',false)+accordion('transition','화면 연결','대상을 선택하세요.',false);}",
  "<button class=\"inspect-button\" data-action=\"links\">전체 연결도 보기</button>`);\n html+=pcAnAccordion(accordion,p); /*pc-v12530*/\n }else{html+=accordion('layout','배치와 위치','위치·크기·잠금 설정',false)+accordion('content','콘텐츠 및 꾸밈','대상을 선택하세요.',false)+accordion('transition','화면 연결','대상을 선택하세요.',false)+accordion('anim','등장 효과 · 발표','대상을 선택하세요.',false);}")

# 진단(시험·콘솔용): 발표 상태·숨기기·인쇄 장수
R("clonePage,fitZoom,startPresentation,", "clonePage,fitZoom,startPresentation,"
  "presentInfo:()=>({presentId:st.presentId,nextId:st.presentId?pcPresentNextId():null,firstShown:pcFirstShown(),anim:{shown:PC_AN.shown,steps:[...PC_AN.steps]},laser:PC_LZ.on}),"
  "setPageHidden:pcPgHideToggle,printPageCount:()=>{const d=preparePrintableDeck(),n=d.querySelectorAll('.rv-print-page').length;d.remove();return n;},")

# 설정 칸 탭: 등장 효과 칸은 '선택 개체' 탭
R("['layout','content','media','chart','table','transition','line','flow'].includes(accordion)?'object'",
  "['layout','content','media','chart','table','transition','line','flow','anim'].includes(accordion)?'object'")

# 설정 찾기·단축키 표
R(" ['개체 이름 바꾸기','선택 머리 ✎ · 겹친 개체 목록','이름 개체 레이어 F2','','','']];",
  " ['개체 이름 바꾸기','선택 머리 ✎ · 겹친 개체 목록','이름 개체 레이어 F2','','',''],\n"
  " ['등장 효과(애니메이션)','선택 개체 › 등장 효과 · 발표','애니메이션 등장 효과 나타내기 순서 빌드 날아오기','object','anim',''],\n"
  " ['발표에서 페이지 숨기기','페이지 설정 › 페이지 배경 · 전환 · 메모','숨기기 숨김 슬라이드 건너뛰기 빼기','page','page','발표에서 이 페이지'],\n"
  " ['레이저 포인터','발표 도구줄 [레이저] · L 키','레이저 포인터 빨간 점 가리키기','','','']];")
R(" {keys:'→ / ← / ↑ / ↓·1~9 / 0',when:'발표',does:'다음 / 이전 / 위 단계 / 하위 상자 / 처음',where:'pcKeyEditor'},\n {keys:'Esc',when:'발표',does:'음량 창 닫기, 없으면 발표 끝',where:'pcKeyEditor'},",
  " {keys:'→·Space·PageDown / ←·PageUp / ↑ / ↓·1~9 / 0',when:'발표',does:'다음(남은 등장 효과 먼저) / 이전 / 위 단계 / 하위 상자 / 처음 (숨긴 페이지는 건너뜀)',where:'pcKeyEditor'},\n"
  " {keys:'L',when:'발표·발표자 보기 창',does:'레이저 포인터 켜기/끄기',where:'pcKeyEditor · pcPresenterKeys'},\n"
  " {keys:'Esc',when:'발표',does:'음량 창 닫기 → 레이저 끄기 → 발표 끝 (앞에서부터 하나만)',where:'pcKeyEditor'},")
R(" {keys:'→ ← ↑ ↓ · Space · PageUp/PageDown · 1~9 / 0',when:'발표자 보기 창',does:'발표 화면 넘기기 (Esc: 발표 끝)',where:'pcPresenterKeys'}",
  " {keys:'→ ← ↑ ↓ · Space · PageUp/PageDown · 1~9 / 0',when:'발표자 보기 창',does:'발표 화면 넘기기 (Esc: 레이저 끄기, 없으면 발표 끝)',where:'pcPresenterKeys'}")

NEWJS = r"""/*pc-v12530*/
// ══════ v12.53 · 발표에서 숨기기 · 레이저 포인터 · 등장 효과 ══════
// 1) 숨기기: page.hidden=true일 때만. 발표 넘김·처음·발표자 '다음'·인쇄에서 건너뜀(연결 상자·숫자키로는 감)
function pcPgHidden(id){return !!st.project.pages.find(x=>x.id===id)?.hidden;}
function pcSkipHidden(ids,idx,delta){for(let j=idx+delta;j>=0&&j<ids.length;j+=delta)if(!pcPgHidden(ids[j]))return ids[j];return null;}
function pcFirstShown(){const P=st.project.pages;return (P.find(p=>!p.hidden)||P[0]).id;}
function pcPgHideToggle(id,on){const p=st.project.pages.find(x=>x.id===id);if(!p)return false;const v=on??!p.hidden,n=st.project.pages.indexOf(p)+1;if(v===!!p.hidden)return false;
 if(v&&st.project.pages.every(x=>x===p||x.hidden)){status('모든 페이지를 숨길 수는 없습니다. 한 페이지는 발표에 보여야 합니다.');renderAll();return false;}
 const ok=mutate(()=>{const t=st.project.pages.find(x=>x.id===id);if(v)t.hidden=true;else delete t.hidden;});
 if(ok)status(v?`${n}번 페이지를 발표에서 숨김 · 편집·PPT에는 남음 · Ctrl+Z로 되돌리기`:`${n}번 페이지를 다시 발표에 보임 · Ctrl+Z로 되돌리기`);return ok;}

// 3) 등장 효과: o.anim={fx,step}. 발표 → 마다 다음 순서 번호의 개체가 나타남(같은 번호 = 함께)
const PC_AN_FX=[['fade','서서히 나타내기'],['up','아래에서 떠오르기'],['left','왼쪽에서 날아오기'],['zoom','확대'],['wipe','닦아내기 (왼쪽→오른쪽)']];
var PC_AN={pageId:null,steps:[],shown:0,back:false,run:[]};
function pcAnSteps(p){return [...new Set((p?.objects||[]).filter(o=>o.anim&&!o.hidden&&!o.unplaced).map(o=>o.anim.step))].sort((a,b)=>a-b);}
function pcAnNode(stage,id){return stage.querySelector(`:scope>.rv-object[data-object-id="${CSS.escape(id)}"]`);}
function pcAnMark(stage,p,shown){const S=pcAnSteps(p);for(const o of p.objects){if(!o.anim)continue;const n=pcAnNode(stage,o.id);if(n)n.classList.toggle('pc-an-wait',S.indexOf(o.anim.step)>=shown);}return S;}
function pcAnFrames(fx,op){const o=Number(op)>=0?Number(op):1;
 return fx==='up'?[{opacity:0,translate:'0 48px'},{opacity:o,translate:'0 0'}]:fx==='left'?[{opacity:0,translate:'-140px 0'},{opacity:o,translate:'0 0'}]
  :fx==='zoom'?[{opacity:0,scale:'.55'},{opacity:o,scale:'1'}]:fx==='wipe'?[{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0 0 0)'}]:[{opacity:0},{opacity:o}];}
function pcAnPlay(n,fx){if(matchMedia('(prefers-reduced-motion: reduce)').matches)return null;return n.animate(pcAnFrames(fx,getComputedStyle(n).opacity),{duration:fx==='wipe'?650:520,easing:'cubic-bezier(.22,1,.36,1)'});}
function pcAnFinish(){for(const a of PC_AN.run){try{a.finish();}catch(e){}}PC_AN.run=[];}
// 발표 그리기: 앞으로 오면 0개, 뒤로(←) 오면 다 나타난 모습
function pcAnPrep(slide,p){pcAnFinish();PC_AN.pageId=p.id;PC_AN.steps=pcAnSteps(p);PC_AN.shown=PC_AN.back?PC_AN.steps.length:0;PC_AN.back=false;pcAnMark(slide,p,PC_AN.shown);}
function pcAnStep(delta){if($('#presentation').hidden)return false;const p=st.project.pages.find(x=>x.id===st.presentId);if(!p||PC_AN.pageId!==p.id)return false;
 const S=PC_AN.steps;if(delta>0?PC_AN.shown>=S.length:PC_AN.shown<=0)return false;
 const stage=$('#presentationViewport > .rv-stage:not([data-rv-exiting])');if(!stage)return false;pcAnFinish();
 if(delta>0){const step=S[PC_AN.shown++];pcAnMark(stage,p,PC_AN.shown);for(const o of p.objects){if(o.anim?.step!==step)continue;const n=pcAnNode(stage,o.id),a=n&&pcAnPlay(n,o.anim.fx);if(a)PC_AN.run.push(a);}}
 else{PC_AN.shown--;pcAnMark(stage,p,PC_AN.shown);}
 try{syncPresentationStepButtons(p);}catch(e){}pcPresenterSync();return true;}
// 편집 화면: 효과 있는 개체 왼쪽 위 번호 배지(그리기 결과·썸네일·인쇄·PPT에는 없음)
function pcAnBadges(){const stage=$('#stageHost>.rv-stage');if(!stage)return;stage.querySelector(':scope>.pc-an-badges')?.remove();const p=current();if(!p?.objects.some(o=>o.anim))return;
 const wrap=document.createElement('div');wrap.className='pc-an-badges';wrap.setAttribute('aria-hidden','true');wrap.style.setProperty('--gz',1/Math.max(.15,st.zoom||1));
 for(const o of p.objects){if(!o.anim||o.hidden||o.unplaced)continue;const b=document.createElement('span');b.className='pc-an-badge';b.textContent=o.anim.step;b.style.left=o.x+'px';b.style.top=o.y+'px';wrap.append(b);}stage.append(wrap);}
function pcAnLabel(fx){return (PC_AN_FX.find(x=>x[0]===fx)||[])[1]||'없음';}
function pcAnAccordion(accordion,p){const sel=selected();if(!sel.length)return '';const fxs=new Set(sel.map(o=>o.anim?.fx||'')),fx=fxs.size===1?[...fxs][0]:null,a=sel.find(o=>o.anim)?.anim,cnt=p.objects.filter(o=>o.anim).length;
 const opt=(v,t)=>`<option value="${v}" ${v===fx?'selected':''}>${t}</option>`;
 return accordion('anim',`등장 효과 · 발표${a&&fx?' · '+a.step+'번':''}`,`<label class="prop-row"><span>효과</span><select id="pcAnFx">${fx==null?'<option value="" selected disabled>여러 가지</option>':''}${opt('','없음 (처음부터 보임)')}${PC_AN_FX.map(([v,t])=>opt(v,t)).join('')}</select></label>
  <label class="prop-row"><span>순서</span><input id="pcAnStep" type="number" min="1" max="99" step="1" value="${a?a.step:''}" ${a?'':'disabled'} aria-label="등장 순서 번호"></label>
  <div class="inspect-actions"><button type="button" class="inspect-button" data-pc-an-preview ${a?'':'disabled'}>▶ 미리 보기</button>${cnt?`<button type="button" class="inspect-button" data-pc-an-clear>이 페이지 효과 모두 없애기 (${cnt})</button>`:''}</div>
  <p class="inspector-tip">발표 중 → · Space · PageDown · [뒷페이지]를 누를 때마다 순서 번호대로 나타납니다(같은 번호는 함께). ← 는 하나씩 되돌립니다. 썸네일·인쇄·PPT에는 다 나타난 모습으로 나옵니다.</p>`);}
function pcAnPreview(){const sel=selected().filter(o=>o.anim);for(const o of sel){const n=$(`#stageHost>.rv-stage>.rv-object[data-object-id="${CSS.escape(o.id)}"]`);if(n)pcAnPlay(n,o.anim.fx);}}
function pcAnSet(fn,msg){const ids=new Set(selected().map(o=>o.id));if(!ids.size)return;if(mutate(()=>{fn(current().objects.filter(o=>ids.has(o.id)));})){status(msg+' · Ctrl+Z로 되돌리기');setTimeout(pcAnPreview,30);}}
document.addEventListener('change',e=>{const t=e.target;if(!t?.closest?.('#inspector'))return;
 if(t.id==='pcPgHide'){pcPgHideToggle(current().id,t.checked);return;}
 if(t.id==='pcAnFx'){const fx=t.value;if(!fx){pcAnSet(L=>{for(const o of L)delete o.anim;},'등장 효과 없앰');return;}
  const ids=new Set(selected().map(o=>o.id)),others=current().objects.filter(o=>o.anim&&!ids.has(o.id)).map(o=>o.anim.step),step=selected().find(o=>o.anim)?.anim.step||Math.min(99,Math.max(0,...others)+1);
  pcAnSet(L=>{for(const o of L)o.anim={fx,step:o.anim?.step||step};},`등장 효과: ${pcAnLabel(fx)} · 순서 ${step} · 발표에서 → 로 나타남`);return;}
 if(t.id==='pcAnStep'){const v=Math.round(M.clamp(Number(t.value)||1,1,99));pcAnSet(L=>{for(const o of L)if(o.anim)o.anim.step=v;},`등장 순서 ${v}번`);}},true);
document.addEventListener('click',e=>{if(e.target.closest?.('#inspector [data-pc-an-preview]')){e.preventDefault();pcAnPreview();return;}
 if(e.target.closest?.('#inspector [data-pc-an-clear]')){e.preventDefault();const n=current().objects.filter(o=>o.anim).length;if(n&&mutate(()=>{for(const o of current().objects)delete o.anim;}))status(`이 페이지 등장 효과 ${n}개 없앰 · Ctrl+Z로 되돌리기`);}},true);

// 2) 레이저 포인터(문서 데이터 아님): 발표 화면 마우스 → 빨간 점. 발표자 보기 '지금 화면' 위 움직임도 같은 자리로
var PC_LZ={on:false};
function pcLaserToggle(on=!PC_LZ.on){if(on&&$('#presentation').hidden)return;PC_LZ.on=!!on;const host=$('#presentation');host.classList.toggle('pc-laser-on',PC_LZ.on);
 let dot=$('#pcLaser');if(!dot&&PC_LZ.on){dot=document.createElement('div');dot.id='pcLaser';dot.className='pc-laser';dot.setAttribute('aria-hidden','true');dot.hidden=true;host.append(dot);}if(dot&&!PC_LZ.on)dot.hidden=true;
 $('#presentation [data-action=presentLaser]')?.setAttribute('aria-pressed',String(PC_LZ.on));
 const b=typeof pcPvEl==='function'&&PC_PV?pcPvEl('pvLaser'):null;if(b){b.setAttribute('aria-pressed',String(PC_LZ.on));b.ownerDocument.body.classList.toggle('pv-laser-on',PC_LZ.on);}}
function pcLaserAt(x,y){const dot=$('#pcLaser');if(!dot||!PC_LZ.on)return;dot.style.translate=`${Math.round(x)}px ${Math.round(y)}px`;dot.hidden=false;}
function pcLaserHide(){const dot=$('#pcLaser');if(dot)dot.hidden=true;}
function pcLaserFromPv(e){if(!PC_LZ.on)return;const s=e.currentTarget.querySelector(':scope>.rv-stage'),m=$('#presentationViewport > .rv-stage:not([data-rv-exiting])');if(!s||!m){pcLaserHide();return;}
 const r=s.getBoundingClientRect(),fx=(e.clientX-r.left)/r.width,fy=(e.clientY-r.top)/r.height;if(!(fx>=0&&fx<=1&&fy>=0&&fy<=1)){pcLaserHide();return;}const q=m.getBoundingClientRect();pcLaserAt(q.left+fx*q.width,q.top+fy*q.height);}
document.addEventListener('pointermove',e=>{if(!PC_LZ.on||$('#presentation').hidden)return;if(e.target.closest?.('.presentation-top,#pcNotesDock')){pcLaserHide();return;}pcLaserAt(e.clientX,e.clientY);},{passive:true});
document.documentElement.addEventListener('mouseleave',()=>{if(PC_LZ.on)pcLaserHide();});
"""
R("function pcKeyEditor(e){\n", NEWJS + "function pcKeyEditor(e){\n")

# CSS: pc-ui-css 안 해당 구역(페이지 목록 · 발표 화면 · v12.52 쪽 번호 구역 옆 편집 배지)
a = html.find('<style id="pc-ui-css">'); b = html.find('</style>', a); assert a > 0
css = html[a:b]
def C(old, new, n=1):
    global css
    c = css.count(old); assert c == n, f'css expected {n} got {c}: {old[:80]!r}'
    css = css.replace(old, new)
C(".page-actions button{border:1px solid #dfe7ee;border-radius:5px;background:#fff;font-size:10px;padding:3px 7px;}",
  ".page-actions button{border:1px solid #dfe7ee;border-radius:5px;background:#fff;font-size:10px;padding:3px 5px;white-space:nowrap;}")
C(".page-actions .danger:hover{color:#c34b5b;background:#fff5f5}",
  ".page-actions .danger:hover{color:#c34b5b;background:#fff5f5}"
  ".page-row.pc-pg-hidden .thumb-viewport{opacity:.38;filter:grayscale(.6)}.page-row.pc-pg-hidden .page-index{color:#94A3B8}"
  ".page-row.pc-pg-hidden .page-index::after{content:'숨김';display:block;margin-top:3px;font-size:9px;font-weight:700;color:#B45309}"
  ".page-row.pc-pg-hidden .thumb-caption span{color:#94A3B8;text-decoration:line-through}.page-actions [data-action=pageHide][aria-pressed=true]{background:#FEF3C7;border-color:#FCD34D;color:#92400E}")
C(".presentation{position:fixed;inset:0;z-index:20000;background:#111e2c;display:flex;flex-direction:column}",
  ".presentation{position:fixed;inset:0;z-index:20000;background:#111e2c;display:flex;flex-direction:column}"
  ".presentation.pc-laser-on #presentationViewport{cursor:none}"
  ".pc-laser{position:fixed;left:0;top:0;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;pointer-events:none;z-index:2147483000;"
  "background:radial-gradient(circle,#FFF5F5 0 16%,#FF3B3B 38%,#E00000 72%);box-shadow:0 0 6px 2px #FF2A2ACC,0 0 22px 8px #FF000040}"
  ".presentation-top .pc-lz-btn[aria-pressed=true]{background:#7F1D1D;border-color:#F87171;color:#FEE2E2}"
  ".rv-stage>.rv-object.pc-an-wait{visibility:hidden}")
C(".rv-stage>.pc-pagenum[data-pos=right]{right:32px;text-align:right}",
  "/* v12.53 등장 효과 번호 배지(편집 화면만) */\n"
  "#stageHost .rv-stage>.pc-an-badges{position:absolute;inset:0;pointer-events:none;z-index:7999}"
  "#stageHost .rv-stage .pc-an-badge{position:absolute;min-width:20px;height:20px;padding:0 5px;border-radius:10px;background:#7C3AED;color:#fff;font:700 11px/20px Pretendard,'Malgun Gothic',sans-serif;text-align:center;box-shadow:0 1px 3px #0003;transform:translate(-50%,-50%) scale(var(--gz));transform-origin:center}\n"
  ".rv-stage>.pc-pagenum[data-pos=right]{right:32px;text-align:right}")
html = html[:a] + css + html[b:]

# ── 버전 문자열(BUILD_VERSION·하단 서명. <title>은 v12.46부터 문서 제목이라 안 건드림) ──
R("const BUILD_VERSION='PageCraft v12.52.0 · 눈금자·안내선·쪽 번호·개체 이름';", "const BUILD_VERSION='PageCraft v12.53.0 · 숨기기·레이저·애니메이션';")
R('Jungmin Jo · PageCraft v12.52.0</span>', 'Jungmin Jo · PageCraft v12.53.0</span>')
open(out, 'w', encoding='utf-8').write(html); print('patched', out, len(html))
