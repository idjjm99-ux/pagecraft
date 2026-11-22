"""PageCraft v12.46.0 — 쓰기 편하게(사용자 입장 불편 4가지).
기준: v12.45.0 Lite.
 1) 버전·탭 제목: 탭 제목에 개발 메모 대신 '<문서 제목> · 페이지공방'(저장본에도 그대로),
    화면 아래 서명 v12.44.0 → BUILD_VERSION에서 자동으로 가져옴(다시 어긋나지 않게)
 2) 첫 안내: '괜찮아요'(또는 Esc) → 창 바로 닫힘 + [? 사용법] 단추가 3초 깜빡임. 막는 창 2번 → 0번
 3) 저장 메뉴: 머리줄 HTML 저장·PPT 저장·인쇄·PDF·자료 저장 + 리본 '임시저장 복구' → [저장 ▾] 하나.
    단추는 그대로 옮겨 data-action·id·이벤트 유지. 방향키·Esc·바깥 클릭으로 닫힘. 저장본 다시 열 때 중복 정리
 4) 작은 화면(1280~1439px 폭): 테마 칸 폭·지우개 '크기' 글자 줄여 도구줄 3줄 → 2줄(편집 화면 높이 확보)
Usage: python3 -I patch_v12460.py <PageCraft_v12.45.0_Lite.html> <out.html>"""
import sys
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
def R(old, new, n=1):
    global html
    c = html.count(old); assert c == n, f'expected {n} got {c}: {old[:80]!r}'
    html = html.replace(old, new)
assert "BUILD_VERSION='PageCraft v12.45.0 · 코드 정리(CSS·단축키 한 곳)'" in html, 'needs v12.45.0'
assert 'pcSaveMenu' not in html, 'already patched'

# ── 1) 버전·탭 제목 ──────────────────────────────────────────────
R("<title>페이지공방 v12.45.0 · 코드 정리(CSS·단축키 한 곳)</title>", "<title>페이지공방</title>")
R("BUILD_VERSION='PageCraft v12.45.0 · 코드 정리(CSS·단축키 한 곳)'",
  "BUILD_VERSION='PageCraft v12.46.0 · 쓰기 편하게(저장 메뉴·첫 안내·작은 화면)'")
R('title="프로그램 정보">Jungmin Jo · PageCraft v12.44.0</span>',
  'title="프로그램 정보">Jungmin Jo · PageCraft v12.46.0</span>')
# 탭 제목 = 문서 제목 · 페이지공방 (renderAll 때와 제목 입력 때)
R("$('#projectTitle').value=st.project.title;",
  "$('#projectTitle').value=st.project.title;window.pcSyncTitle?.();")

# ── 2) 첫 안내: '괜찮아요' 한 번에 닫힘 ─────────────────────────────
R("function guideHelp(){",
  "function guideLater(){closeGuide();const b=document.querySelector('.header-actions [data-action=showGuide]');"
  "if(b){b.classList.remove('pc-pulse');void b.offsetWidth;b.classList.add('pc-pulse');setTimeout(()=>b.classList.remove('pc-pulse'),3300);}"
  "status('사용법은 오른쪽 위 [? 사용법]에서 언제든 다시 볼 수 있습니다.');}\n"
  "function guideHelp(){")
R("guideMode==='ask'?guideHelp():closeGuide();}", "guideMode==='ask'?guideLater():closeGuide();}")
R("else if(a==='later')guideHelp();", "else if(a==='later')guideLater();")

# 안내 단계: 인쇄·PDF 단추가 저장 메뉴 안으로 → 메뉴 단추를 짚음
R("{target:'.header-actions [data-action=printDeck]',title:'PDF 내보내기',body:'<b>인쇄 · PDF</b>를 누르고 대상을 <b>PDF로 저장</b>으로 고르면 나눠 줄 파일이 됩니다.',ex:'배포는 PDF, 발표는 이 프로그램으로'},",
  "{target:'#pcSaveMenu .pc-save-toggle',title:'저장 · PDF',body:'<b>저장 ▾</b>에 모여 있습니다. 이어서 고칠 땐 <b>HTML 저장</b>(Ctrl+S), 나눠 줄 땐 <b>인쇄 · PDF</b>.',ex:'PDF: 인쇄 창 대상에서 PDF로 저장'},")

# ── 3) 저장 메뉴 (시작 시 한 번, 저장본 다시 열 때도 안전) ─────────────
ANCHOR = "document.querySelector('.header-actions')?.append(editorPrint);"
SAVE_MENU = r"""
(function pcSaveMenu(){const ha=document.querySelector('.header-actions');if(!ha)return;
 let wrap=document.getElementById('pcSaveMenu');
 if(!wrap){wrap=document.createElement('div');wrap.id='pcSaveMenu';wrap.className='pc-save-menu';
  wrap.innerHTML='<button type="button" class="ui-btn pc-save-toggle" aria-haspopup="menu" aria-expanded="false" aria-controls="pcSavePanel" title="저장 · PPT · PDF · 복구">저장 <span aria-hidden="true">▾</span></button><div class="pc-save-panel" id="pcSavePanel" role="menu" aria-label="저장" hidden></div>';
  const before=ha.querySelector(':scope > [data-action=previewCurrentVideo]');before?ha.insertBefore(wrap,before):ha.append(wrap);}
 const tog=wrap.querySelector('.pc-save-toggle'),panel=wrap.querySelector('.pc-save-panel');
 const spec=[['saveHTML','HTML 저장','이어서 고치고 발표할 때 · Ctrl+S'],['exportPptx','PPT 저장','PowerPoint에서 고칠 때'],['printDeck','인쇄 · PDF','나눠 줄 파일'],null,['saveJSON','자료만 저장 (JSON)','글·배치만 · 영상 제외'],['#manualRecoveryBtn','임시저장본 복구','이 브라우저에 남은 이전 작업']];
 const items=[];
 for(const s of spec){if(!s){items.push(null);continue;}
  const all=s[0][0]==='#'?[document.getElementById(s[0].slice(1))]:[...ha.querySelectorAll('[data-action='+s[0]+']')];
  const el=all[0];if(!el)continue;all.slice(1).forEach(x=>x?.remove());
  el.className='pc-save-item';el.type='button';el.setAttribute('role','menuitem');el.tabIndex=-1;el.disabled=false;el.innerHTML='<b>'+s[1]+'</b><small>'+s[2]+'</small>';items.push(el);}
 panel.replaceChildren(...items.map(el=>{if(el)return el;const hr=document.createElement('div');hr.className='pc-save-sep';hr.setAttribute('role','separator');return hr;}));
 const list=()=>[...panel.querySelectorAll('.pc-save-item')];
 const open=v=>{panel.hidden=!v;tog.setAttribute('aria-expanded',String(!!v));wrap.classList.toggle('is-open',!!v);if(v)list()[0]?.focus();};
 open(false);
 tog.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();open(panel.hidden);});
 window.addEventListener('click',e=>{if(panel.hidden)return;if(!wrap.contains(e.target)||e.target.closest('.pc-save-item'))open(false);},true);
 window.addEventListener('keydown',e=>{if(panel.hidden)return;const L=list(),i=L.indexOf(document.activeElement);
  if(e.key==='Escape'){open(false);tog.focus();}
  else if(e.key==='ArrowDown')L[(i+1)%L.length]?.focus();else if(e.key==='ArrowUp')L[(i-1+L.length)%L.length]?.focus();
  else if(e.key==='Home')L[0]?.focus();else if(e.key==='End')L[L.length-1]?.focus();
  else if(e.key==='Tab'){open(false);return;}else return;
  e.preventDefault();e.stopImmediatePropagation();},true);
 window.addEventListener('resize',()=>open(false));
})();
window.pcSyncTitle=function(){const t=(document.getElementById('projectTitle')?.value||'').trim();document.title=!t?'페이지공방':/페이지\s?공방/.test(t)?t:t+' · 페이지공방';};
document.getElementById('projectTitle')?.addEventListener('input',window.pcSyncTitle);window.pcSyncTitle();
{const sig=document.getElementById('rv-app-signature');if(sig)sig.textContent='Jungmin Jo · '+BUILD_VERSION.split(' · ')[0];}
"""
R(ANCHOR, ANCHOR + SAVE_MENU)
# 저장본 다시 열 때 인쇄 단추가 또 붙지 않게(이미 있으면 새로 만들지 않음)
R("document.querySelector('.header-actions')?.append(editorPrint);" + SAVE_MENU,
  "if(!document.querySelector('.header-actions [data-action=printDeck]'))document.querySelector('.header-actions')?.append(editorPrint);" + SAVE_MENU)

# ── CSS (pc-ui-css 안) ─────────────────────────────────────────
# 4) 작은 화면 도구줄: 테마 칸 규칙 구역에서 직접
R("#app .ribbon select#themeScope{width:104px!important;min-width:104px!important;max-width:104px!important;font-size:12px}\n",
  "#app .ribbon select#themeScope{width:104px!important;min-width:104px!important;max-width:104px!important;font-size:12px}\n"
  "@media(max-width:1439px){#app .ribbon select#themeSelect{min-width:170px;max-width:170px}#app .ribbon select#themeScope{width:96px!important;min-width:96px!important;max-width:96px!important;font-size:11px}#app .ribbon .eraser-size-control{font-size:0;gap:0}}\n")
# 저장 메뉴·사용법 깜빡임(새 기능 구역)
CSS = """/* ══════ v12.46: 저장 메뉴 · 사용법 깜빡임 ══════ */
.pc-save-menu{position:relative;display:inline-flex}
.pc-save-menu.is-open .pc-save-toggle{background:#EEF4FF;border-color:#9DB6E3}
.pc-save-panel{position:absolute;top:calc(100% + 6px);right:0;z-index:9700;min-width:264px;padding:6px;background:#fff;border:1px solid #D5DEEA;border-radius:12px;box-shadow:0 14px 36px rgba(15,23,42,.18);display:flex;flex-direction:column;gap:2px}
.pc-save-panel[hidden]{display:none}
.pc-save-item{display:flex;flex-direction:column;align-items:flex-start;gap:2px;width:100%;min-height:44px;padding:8px 12px;border:0;border-radius:8px;background:transparent;text-align:left;cursor:pointer;font:inherit;color:#1D314B}
.pc-save-item b{font-size:13px;font-weight:700}
.pc-save-item small{font-size:11.5px;color:#5B6B7D;font-weight:500}
.pc-save-item:hover,.pc-save-item:focus-visible{background:#EEF4FF;outline:none}
.pc-save-item:focus-visible{box-shadow:inset 0 0 0 2px #1D4ED8}
.pc-save-item[data-action=saveHTML] b::after{content:'권장';margin-left:6px;padding:1px 6px;border-radius:999px;background:#DBEAFE;color:#1D4ED8;font-size:10.5px;vertical-align:1px}
.pc-save-item:disabled{opacity:.55;cursor:progress}
.pc-save-sep{height:1px;margin:4px 8px;background:#E5EAF1}
@keyframes pc-pulse{0%,100%{box-shadow:0 0 0 0 rgba(29,78,216,.55)}50%{box-shadow:0 0 0 7px rgba(29,78,216,0)}}
.header-actions .rv-guide-btn.pc-pulse{animation:pc-pulse 1.1s ease-out 3}
@media(prefers-reduced-motion:reduce){.header-actions .rv-guide-btn.pc-pulse{animation:none;outline:3px solid #93C5FD}}
"""
R("</style><script id=\"embedded-font-license\"", CSS + "</style><script id=\"embedded-font-license\"")

open(out, 'w', encoding='utf-8').write(html)
print('ok', out, len(html))
