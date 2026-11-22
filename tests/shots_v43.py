import sys; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__))); from pcenv import CHROME, HERE; import os
import asyncio,sys
from h import H
from PIL import Image,ImageDraw,ImageFont
TH=['original','nintendo-light','kakao-bank-light','krafton-light','google-light','pro-night-teal','malfoy-v122-archive','renewal-after-dark']
async def main(p):
    h=H();pg=await h.start(p,1700,1100);ev=h.ev
    await pg.click('[data-action=addPage]');await pg.wait_for_timeout(700)
    await pg.click('#templateGrid [data-template="6"]');await pg.click('#confirmTemplate');await pg.wait_for_timeout(1200)
    await pg.select_option('#themeScope','document')
    ims=[]
    for t in TH:
        await pg.select_option('#themeSelect',t);await pg.wait_for_timeout(500);await ev("()=>Revival.selectOne&&Revival.clearSelection?.()")
        el=await pg.query_selector('#stageHost .rv-stage');f=f'/tmp/s_{t}.png';await el.screenshot(path=f);ims.append((t,Image.open(f)))
    await h.close()
    w=560;hh=int(ims[0][1].height*w/ims[0][1].width)
    out=Image.new('RGB',(w*4,(hh+28)*2),'white');d=ImageDraw.Draw(out)
    try:fnt=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
    except:fnt=None
    for i,(t,im) in enumerate(ims):
        x=(i%4)*w;y=(i//4)*(hh+28);out.paste(im.resize((w,hh)),(x,y+28));d.text((x+8,y+5),t,fill='black',font=fnt)
    out.save(os.path.join(HERE,'shots_v43.png'))
asyncio.run(main(sys.argv[1]))
