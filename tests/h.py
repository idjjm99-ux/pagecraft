# 최소 시험 도우미 (원본 h.py는 v12.40 Source에 있음 — 이 파일은 같은 인터페이스의 대체본)
from playwright.async_api import async_playwright
class H:
    def __init__(self): self.errs=[]
    async def start(self,path,w=1500,h=950):
        self.pw=await async_playwright().start()
        self.b=await self.pw.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        self.pg=await self.b.new_page(viewport={'width':w,'height':h})
        self.pg.on('pageerror',lambda e:self.errs.append(str(e)))
        self.pg.on('dialog',lambda d:d.dismiss())
        await self.pg.goto('file://'+path); await self.pg.wait_for_timeout(2500)
        await self.pg.add_style_tag(content='.rv-guide{display:none!important;pointer-events:none!important}')
        await self.pg.keyboard.press('Escape'); await self.pg.wait_for_timeout(600)
        return self.pg
    async def ev(self,js,arg=None):
        return await self.pg.evaluate(js,arg) if arg is not None else await self.pg.evaluate(js)
    async def shot(self,name): await self.pg.screenshot(path=f'/home/claude/tests/{name}.png')
    async def close(self): await self.b.close(); await self.pw.stop()
