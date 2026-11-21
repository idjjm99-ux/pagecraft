# 단축키 동작 비교: 상태 × 키 조합마다 결과(문서·선택·발표·편집·포커스·창·상태줄·내려받기)를 기록
# 사용: python3 -I keytest.py <html> <out.json>
import sys, json, asyncio, re, os
from playwright.async_api import async_playwright

SNAP = r"""()=>{const P=Revival.getProject();let j=JSON.stringify(P.pages.map(p=>({t:p.templateId,th:p.themeId,o:p.objects.map(o=>({...o}))})));
 const ids=new Map();j=j.replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/g,m=>{if(!ids.has(m))ids.set(m,'#'+ids.size);return ids.get(m);});
 let h=2166136261;for(let i=0;i<j.length;i++){h^=j.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}
 const canon=x=>String(x).replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/g,m=>ids.has(m)?ids.get(m):'#new');
 const a=document.activeElement;
 return {doc:h.toString(36)+':'+P.pages.length+':'+P.pages.reduce((n,p)=>n+p.objects.length,0),
  page:canon(Revival.getCurrentPage().id),sel:Revival.getSelected().map(canon).join(','),
  present:!document.querySelector('#presentation').hidden,presentId:canon(Revival.navigationSnapshot().presentId||''),
  editing:!!document.querySelector('#stageHost [contenteditable=true]'),
  focus:a?(a.tagName+(a.id?'#'+a.id:'')+(a.dataset?.tableRow!=null?'cell'+a.dataset.tableRow+'/'+a.dataset.tableCol:'')):'',
  dialogs:[...document.querySelectorAll('dialog[open],[role=dialog]:not([hidden])')].filter(d=>d.offsetParent||d.open).map(d=>d.id||d.className).join(','),
  pickers:['#symbolPicker','#placementPicker','#rvVolumePopover','#pcTcPanel','#pcCcPanel','#quickBar'].map(s=>{const e=document.querySelector(s);return e&&!e.hidden&&e.offsetParent?1:0}).join(''),
  eraser:!!document.querySelector('.eraser-mode,.rv-eraser-on,body.rv-erasing,[data-action=toggleEraser].active,[data-action=toggleEraser][aria-pressed=true]'),
  flowSel:document.querySelectorAll('#stageHost .rv-flow-node.rv-flow-node-selected').length,
  status:canon((document.querySelector('#saveStatus')?.textContent||'').trim()).slice(0,80),
  badge:!!document.querySelector('#rvDragBadge')};}"""

SETUP = {
 'none': "()=>{}",
 'locked': "()=>{const P=Revival.getProject();Revival.go(P.pages[0].id);Revival.selectOne(P.pages[0].objects.find(o=>o.locked).id)}",
 'unlocked': "()=>{const P=Revival.getProject();for(const p of P.pages){const o=p.objects.find(o=>!o.locked&&!o.unplaced&&o.kind!=='flow');if(o){Revival.go(p.id);Revival.selectOne(o.id);return}}}",
 'chart': "()=>{const P=Revival.getProject();for(const p of P.pages){const o=p.objects.find(o=>o.kind==='chart');if(o){Revival.go(p.id);Revival.selectOne(o.id);return}}}",
 'table': "()=>{const P=Revival.getProject();for(const p of P.pages){const o=p.objects.find(o=>o.kind==='table');if(o){Revival.go(p.id);Revival.selectOne(o.id);return}}}",
 'flow': "()=>{const P=Revival.getProject();for(const p of P.pages){const o=p.objects.find(o=>o.kind==='flow');if(o){Revival.go(p.id);Revival.selectOne(o.id);return}}}",
 'present': "()=>{document.querySelector('[data-action=present]').click()}",
 'tpl': "()=>{document.querySelector('[data-action=addPage]').click()}",
}
# 클릭이 필요한 상태: (설정 JS, 클릭할 CSS, 클릭 종류)
CLICK = {
 'cell': ('table', '#stageHost [data-cell-editable]', 'click'),
 'flownode': ('flow', '#stageHost .rv-flow-node', 'click'),
 'editing': ('unlocked_text', None, None),
 'find': (None, '#pcFindInput', 'focus'),
 'eraser': (None, '[data-action=toggleEraser]', 'click'),
}
KEYS = ['Escape', 'Delete', 'Backspace', 'Enter', 'F2', 'Tab', 'Shift+Tab', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
        'Shift+ArrowRight', 'Control+c', 'Control+v', 'Control+z', 'Control+y', 'Control+Shift+z', 'Control+d', 'Control+s',
        'Control+Enter', '0', '1', '2', 'a']
STATES = ['none', 'locked', 'unlocked', 'chart', 'table', 'cell', 'flow', 'flownode', 'editing', 'present', 'tpl', 'find', 'eraser']

GUIDE_DONE = False
async def prep(ctx, path, state):
    pg = await ctx.new_page(); errs = []; dl = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: d.dismiss()); pg.on('download', lambda d: dl.append(1))
    await pg.goto('file://' + path); await pg.wait_for_function("()=>window.Revival&&Revival.getProject"); await pg.wait_for_timeout(1200)
    global GUIDE_DONE
    if not GUIDE_DONE:
        try: await pg.wait_for_selector('.rv-guide', timeout=8000)
        except Exception: errs.append('no-guide')
        GUIDE_DONE = True
    for _ in range(2):
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
    for _ in range(3):
        if not await pg.evaluate("()=>!!document.querySelector('.rv-guide')"): break
        await pg.wait_for_timeout(700); await pg.keyboard.press('Escape')
    await pg.wait_for_timeout(300)
    if await pg.evaluate("()=>!!document.querySelector('.rv-guide')"):
        errs.append('guide-stuck'); await pg.evaluate("()=>document.querySelectorAll('.rv-guide').forEach(e=>e.remove())")
    if state in SETUP: await pg.evaluate(SETUP[state])
    elif state == 'editing':
        await pg.evaluate("""()=>{const P=Revival.getProject();for(const p of P.pages){const o=p.objects.find(o=>!o.locked&&o.kind==='text');if(o){Revival.go(p.id);Revival.selectOne(o.id);return}}
          const p=P.pages[0];Revival.go(p.id);Revival.selectOne(p.objects.find(o=>o.kind==='text').id)}""")
        await pg.wait_for_timeout(200)
        el = await pg.evaluate_handle("()=>document.querySelector('#stageHost .rv-object.rv-selected')")
        await el.as_element().dblclick(); await pg.wait_for_timeout(300)
    else:
        pre, sel, how = CLICK[state]
        if pre: await pg.evaluate(SETUP[pre])
        await pg.wait_for_timeout(250)
        if how == 'focus': await pg.evaluate(f"()=>document.querySelector('{sel}')?.focus()")
        else:
            loc = pg.locator(sel).first
            try: await loc.click(timeout=3000)
            except Exception as e: errs.append('setup-click ' + str(e)[:60])
    await pg.wait_for_timeout(400)
    return pg, errs, dl

async def main(path, out):
    res = {}
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path=next(p for p in [__import__('os').environ.get('PC_CHROME',''),'/usr/bin/google-chrome','/opt/pw-browsers/chromium'] if p and __import__('os').path.exists(p)), args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width': 1500, 'height': 950}, accept_downloads=True)
        for state in (os.environ['KT_STATES'].split(',') if os.environ.get('KT_STATES') else STATES):
            pg, errs, dl = await prep(ctx, path, state)
            res[state + '|before'] = await pg.evaluate(SNAP); await pg.close()
            for k in (os.environ['KT_KEYS'].split(',') if os.environ.get('KT_KEYS') else KEYS):
                pg, errs, dl = await prep(ctx, path, state)
                await pg.keyboard.press(k); await pg.wait_for_timeout(650)
                r = await pg.evaluate(SNAP); r['downloads'] = len(dl); r['errors'] = [re.sub(r'[0-9a-f-]{36}', '#', e)[:80] for e in errs]
                res[state + '|' + k] = r; await pg.close()
            print(state, flush=True)
        await b.close()
    json.dump(res, open(out, 'w'), ensure_ascii=False, indent=0)

asyncio.run(main(sys.argv[1], sys.argv[2]))
