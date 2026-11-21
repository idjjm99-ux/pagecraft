# 화면 결과 비교용: 여러 상태에서 모든 요소의 계산된 스타일·위치를 해시로 기록
# 사용: python3 -I cssdump.py <html> <out.json> [quick]
import sys, json, asyncio, os
from playwright.async_api import async_playwright

DUMP = r"""(rootSel)=>{
 for(const a of document.getAnimations()){try{const t=a.effect?.getComputedTiming?.();if(t&&t.endTime!==Infinity)a.finish();else{a.pause();a.currentTime=0;}}catch(e){}}
 const roots=rootSel?[...document.querySelectorAll(rootSel)]:[document.documentElement];
 const out=[];const h=s=>{let x=2166136261;for(let i=0;i<s.length;i++){x^=s.charCodeAt(i);x=Math.imul(x,16777619)>>>0;}return x.toString(36)};
 const U=/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/g;const ser=cs=>{const a=[];for(let i=0;i<cs.length;i++){const p=cs[i];a.push(p+':'+cs.getPropertyValue(p));}a.sort();return a.join(';').replace(U,'U')};
 for(const root of roots){const all=[root,...root.querySelectorAll('*')];
  for(const el of all){const t=el.tagName;if(t==='SCRIPT'||t==='STYLE'||t==='HEAD'||t==='META'||t==='TITLE'||t==='LINK')continue;
   if(el.closest('head'))continue;
   if(!window.__THUMBS&&el.closest('.thumb-stage'))continue;
   const r=el.getBoundingClientRect();
   const s=h(ser(getComputedStyle(el)))+','+h(ser(getComputedStyle(el,'::before')))+','+h(ser(getComputedStyle(el,'::after')))+',R'+[r.x,r.y,r.width,r.height].map(v=>Math.round(v*10)/10).join('/');
   out.push(t+(el.id?'#'+el.id.replace(U,'U'):'')+'.'+String(el.className?.baseVal??el.className).slice(0,40)+'='+s);}}
 return out;}"""

DETAIL = r"""([rootSel,idx])=>{const roots=rootSel?[...document.querySelectorAll(rootSel)]:[document.documentElement];const els=[];
 for(const root of roots)for(const el of [root,...root.querySelectorAll('*')]){const t=el.tagName;if(t==='SCRIPT'||t==='STYLE'||t==='HEAD'||t==='META'||t==='TITLE'||t==='LINK'||el.closest('head'))continue;els.push(el);}
 const el=els[idx];if(!el)return null;const o={};for(const [k,cs] of [['',getComputedStyle(el)],['::before',getComputedStyle(el,'::before')],['::after',getComputedStyle(el,'::after')]])for(let i=0;i<cs.length;i++)o[k+cs[i]]=cs.getPropertyValue(cs[i]);
 const r=el.getBoundingClientRect();o.rect=[r.x,r.y,r.width,r.height].join(',');o.html=el.outerHTML.slice(0,200);return o;}"""

async def settle(pg, ms=350):
    await pg.wait_for_timeout(ms)
    await pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")

async def main(path, out, quick=False):
    res = {}
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox', '--font-render-hinting=none'])
        for (W, H) in ([(1500, 950), (1024, 700)] if quick else [(1500, 950), (1366, 768), (1024, 700)]):
            ctx = await b.new_context(viewport={'width': W, 'height': H})
            pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: d.dismiss())
            await pg.goto('file://' + path); await pg.wait_for_timeout(2500)
            await pg.evaluate("()=>document.fonts.ready")
            tag = f'{W}x{H}'
            async def dump(name, sel=None, ms=350):
                await settle(pg, ms); res[f'{tag}|{name}'] = await pg.evaluate(DUMP, sel)
                res[f'{tag}|{name}|root'] = await pg.evaluate("()=>{const cs=getComputedStyle(document.documentElement);let o=[];for(let i=0;i<cs.length;i++)o.push(cs[i]+':'+cs.getPropertyValue(cs[i]));return o.sort().join(';').replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/g,'U')}")
                if os.environ.get('DSTATE') == name:
                    res['DETAIL'] = [await pg.evaluate(DETAIL, [sel, int(i)]) for i in os.environ['DIDX'].split(',')]
                    if os.environ.get('DSTOP'): raise SystemExit(json.dump(res, open(out, 'w')))
            await dump('guide-ask', ms=900)               # 처음 오셨네요 창
            await pg.keyboard.press('Escape'); await dump('guide-help', ms=900)
            await pg.keyboard.press('Escape'); await settle(pg, 600)
            if await pg.evaluate("()=>!!document.querySelector('.rv-guide')"):
                await pg.evaluate("()=>document.querySelectorAll('.rv-guide').forEach(e=>e.remove())")
            await dump('start', ms=900)
            pages = await pg.evaluate("()=>Revival.getProject().pages.map(p=>p.id)")
            for i, p in enumerate(pages):
                await pg.evaluate(f"()=>Revival.go('{p}')"); await dump(f'ex{i}')
            # 개체 종류별 선택 (간편바·설정 칸)
            kinds = await pg.evaluate("""()=>{const m={};for(const p of Revival.getProject().pages)for(const o of p.objects){const k=o.kind+'/'+(o.role||'');if(!m[k]&&!o.unplaced)m[k]=[p.id,o.id];}return m}""")
            for k, (p, o) in sorted(kinds.items()):
                await pg.evaluate(f"()=>{{Revival.go('{p}');Revival.selectOne('{o}')}}"); await dump('sel:' + k)
            await pg.keyboard.press('Escape')
            # 양식 선택 창
            await pg.click('[data-action=addPage]'); await dump('tpl-open', ms=800)
            cats = await pg.evaluate("()=>[...document.querySelectorAll('[data-template-category],[data-category]')].map((e,i)=>i)")
            for i in cats:
                await pg.evaluate(f"()=>[...document.querySelectorAll('[data-template-category],[data-category]')][{i}]?.click()"); await dump(f'tpl-cat{i}')
            if not quick:
                for th in (await pg.evaluate("()=>[...document.querySelectorAll('#templateThemeSelect option')].map(o=>o.value)"))[:50:7]:
                    await pg.select_option('#templateThemeSelect', th); await dump('tpl-theme:' + th, ms=600)
            # 양식 하나 고른 상태(아래 작업줄)
            await pg.evaluate("()=>document.querySelector('#templateGrid [data-template]')?.click()"); await dump('tpl-picked')
            await pg.click('[data-action=closeTemplates]'); await settle(pg)
            # 여러 개 선택 간편바
            await pg.evaluate("()=>{const P=Revival.getProject();for(const p of P.pages){const os=p.objects.filter(o=>!o.locked&&!o.unplaced&&o.kind!=='flow');if(os.length>1){Revival.go(p.id);window.__ms=os.slice(0,2).map(o=>o.id);return}}}")
            ms = await pg.evaluate("()=>window.__ms||[]")
            for i, oid in enumerate(ms):
                try: await pg.locator(f'#stageHost .rv-object[data-object-id="{oid}"]').first.click(modifiers=['Shift'] if i else [], timeout=3000, force=True)
                except Exception as e: res.setdefault(f'{tag}|warn', []).append('multi ' + str(e)[:50])
            await dump('multi-select')
            await pg.keyboard.press('Escape'); await settle(pg)
            # 페이지 잠금 메뉴
            try:
                await pg.locator('[data-action=pageLockMenu]').first.click(timeout=3000); await dump('page-lock-menu')
            except Exception as e: res.setdefault(f'{tag}|warn', []).append('lock ' + str(e)[:50])
            await pg.keyboard.press('Escape'); await settle(pg)
            # 연결 지도
            await pg.evaluate("()=>Revival.showLinkMap()"); await dump('link-map', ms=800)
            await pg.evaluate("()=>document.querySelector('[data-action=closeMap]')?.click()"); await settle(pg)
            # 사용법 둘러보기 3단계
            try:
                await pg.locator('[data-action=showGuide]').first.click(timeout=3000); await dump('guide-tour0', ms=800)
                for i in (1, 2):
                    await pg.evaluate("()=>document.querySelector('.rv-guide [data-guide=next],.rv-guide .rv-guide-next')?.click()"); await dump(f'guide-tour{i}', ms=800)
                await pg.evaluate("()=>document.querySelector('.rv-guide [data-guide=skip]')?.click()"); await settle(pg, 600)
                await pg.evaluate("()=>document.querySelectorAll('.rv-guide').forEach(e=>e.remove())")
            except Exception as e: res.setdefault(f'{tag}|warn', []).append('guide ' + str(e)[:50])
            # 발표: 도구줄 접기·음량 창
            await pg.click('[data-action=present]'); await dump('present-ui', ms=1200)
            await pg.evaluate("()=>document.querySelector('[data-action=presentVolumeMenuToggle]')?.click()"); await dump('present-volume', ms=500)
            await pg.keyboard.press('Escape'); await settle(pg, 300)
            await pg.evaluate("()=>document.querySelector('[data-action=presentToolbarToggle]')?.click()"); await dump('present-collapsed', ms=800)
            await pg.evaluate("()=>document.querySelector('[data-action=presentToolbarToggle]')?.click()"); await settle(pg, 500)
            for _ in range(4):
                if await pg.evaluate("()=>document.querySelector('#presentation').hidden"): break
                await pg.keyboard.press('Escape'); await settle(pg, 700)
            # 자동저장본 복구 창: 고친 뒤 다시 열기
            await pg.evaluate("()=>{const P=Revival.getProject();for(const p of P.pages){const o=p.objects.find(o=>!o.locked&&!o.unplaced);if(o){Revival.go(p.id);Revival.selectOne(o.id);return}}}")
            await pg.keyboard.press('Delete'); await pg.wait_for_timeout(2500)
            await pg.reload(); await pg.wait_for_timeout(3000); await dump('recovery', ms=800)
            await pg.evaluate("()=>document.querySelector('#recoveryPrompt button')?.click()"); await settle(pg, 800)
            for _ in range(4):
                if await pg.evaluate("()=>document.querySelector('#presentation').hidden"): break
                await pg.keyboard.press('Escape'); await settle(pg, 700)
            if tag != '1500x950':
                await ctx.close(); continue
            # 모든 양식 페이지 추가
            await pg.click('[data-action=addPage]'); await settle(pg, 800)
            ids = await pg.evaluate("()=>[...new Set([...document.querySelectorAll('#templateGrid [data-template]')].map(e=>e.dataset.template))]")
            for t in ids:
                await pg.evaluate(f"""()=>document.querySelector('#templateGrid [data-template="{t}"]').click()""")
            await pg.click('#confirmTemplate'); await settle(pg, 2500)
            pages = await pg.evaluate("()=>Revival.getProject().pages.map(p=>p.id)")
            res[f'{tag}|npages'] = [str(len(pages)), str(len(ids))]
            themes = await pg.evaluate("()=>[...document.querySelectorAll('#themeSelect option')].map(o=>o.value)")
            await pg.select_option('#themeScope', 'document')
            for th in (themes[:6] if quick else themes):
                await pg.select_option('#themeSelect', th); await settle(pg, 500)
                for i, p in enumerate(pages):
                    await pg.evaluate(f"()=>Revival.go('{p}')")
                    await settle(pg, 30); res[f'{tag}|th:{th}|p{i}'] = await pg.evaluate(DUMP, '#stageHost')
            await pg.wait_for_timeout(3000); await pg.evaluate("()=>window.__THUMBS=1"); await dump('thumbs', '.thumb-stage', ms=500); await pg.evaluate("()=>window.__THUMBS=0")
            await dump('editor-final')
            # 발표
            await pg.evaluate(f"()=>Revival.go('{pages[0]}')"); await pg.click('[data-action=present]'); await dump('present0', ms=1200)
            for k in ['ArrowDown', 'ArrowRight', '1', '0']:
                await pg.keyboard.press(k); await dump('present-' + k, '#presentation', ms=900)
            await pg.keyboard.press('Escape'); await settle(pg, 800)
            # 인쇄
            await pg.emulate_media(media='print'); await pg.evaluate("()=>window.dispatchEvent(new Event('beforeprint'))")
            await dump('print', ms=1500)
            await pg.emulate_media(media='screen')
            res[f'{tag}|errors'] = errs
            await ctx.close()
        await b.close()
    json.dump(res, open(out, 'w'))
    print('states', len(res), 'elements', sum(len(v) for v in res.values()))

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1], sys.argv[2], len(sys.argv) > 3))
