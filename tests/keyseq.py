# 단축키 연속 동작 비교 (붙여넣기·되돌리기 등 이어지는 동작)
import sys; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__))); from pcenv import CHROME, HERE; import os
import sys, json, asyncio, re
import importlib.util
spec = importlib.util.spec_from_file_location('kt', os.path.join(HERE,'keytest.py'))
src = open(os.path.join(HERE,'keytest.py'),encoding='utf-8').read().split('asyncio.run(')[0]
kt = {'__file__': os.path.join(HERE,'keytest.py')}; exec(compile(src, 'keytest', 'exec'), kt)
from playwright.async_api import async_playwright
SEQ = [
 ('unlocked', ['Control+c', 'Control+v']), ('unlocked', ['Control+c', 'Control+v', 'Control+v', 'Control+z']),
 ('unlocked', ['ArrowRight', 'ArrowRight', 'Shift+ArrowDown', 'WAIT', 'Control+z']), ('unlocked', ['ArrowRight', 'Escape', 'Control+z']),
 ('unlocked', ['Delete', 'Control+z']), ('unlocked', ['Delete', 'Control+z', 'Control+y']), ('unlocked', ['Control+d', 'Control+z', 'Control+Shift+z']),
 ('locked', ['Delete', 'Control+z']), ('flownode', ['Delete', 'Control+z']), ('flownode', ['Escape', 'Delete']),
 ('flownode', ['Enter', 'x', 'Enter']), ('editing', ['End', 'x', 'Control+Enter', 'Control+z']), ('editing', ['x', 'Escape']),
 ('cell', ['Enter', 'x', 'Enter']), ('cell', ['Enter', 'x', 'Escape']), ('cell', ['Tab', 'Tab', 'Shift+Tab']),
 ('chart', ['Control+c', 'Control+v']), ('table', ['Control+c', 'Control+v', 'Delete']),
 ('present', ['ArrowRight', 'ArrowRight', 'ArrowLeft']), ('present', ['1', 'ArrowUp', '0']), ('present', ['ArrowDown', 'Escape']),
 ('eraser', ['Escape', 'Escape']), ('tpl', ['Escape', 'Delete']), ('find', ['x', 'Enter', 'Escape']),
 ('none', ['Control+z', 'Control+y']), ('unlocked', ['Tab', 'Delete']),
]
async def main(path, out):
    res = {}
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
        ctx = await b.new_context(viewport={'width': 1500, 'height': 950}, accept_downloads=True)
        await ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
        for i, (state, keys) in enumerate(SEQ):
            pg, errs, dl = await kt['prep'](ctx, path, state)
            await pg.mouse.move(700, 450)
            steps = []
            for k in keys:
                if k == 'WAIT': await pg.wait_for_timeout(700); continue
                await pg.keyboard.press(k); await pg.wait_for_timeout(250)
                steps.append(await pg.evaluate(kt['SNAP']))
            await pg.wait_for_timeout(600); r = await pg.evaluate(kt['SNAP'])
            r['errors'] = [re.sub(r'[0-9a-f-]{36}', '#', e)[:80] for e in errs]
            res[f'{i}:{state}:' + '>'.join(keys)] = {'steps': steps, 'final': r}; await pg.close()
        await b.close()
    json.dump(res, open(out, 'w'), ensure_ascii=False, indent=0); print('done', len(res))
asyncio.run(main(sys.argv[1], sys.argv[2]))
