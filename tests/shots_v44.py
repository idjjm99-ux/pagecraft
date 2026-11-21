import asyncio,sys
sys.path.insert(0,'/home/claude/tests')
from h import H
from PIL import Image
TH=['v07-navy-orchid','v07-sage-gold','pro-night-teal','renewal-after-dark','krafton-light','nintendo-light','original','user-white-sky-hotpink']
async def main(path):
    h=H();pg=await h.start(path,1700,1100);ev=h.ev
    await pg.click('[data-action=addPage]');await pg.wait_for_timeout(700)
    for t in [5,6]:await pg.click(f'#templateGrid [data-template="{t}"]');await pg.wait_for_timeout(200)
    await pg.click('#confirmTemplate');await pg.wait_for_timeout(1500)
    await pg.select_option('#themeScope','document')
    pid={t:i for i,t in await ev("()=>Revival.getProject().pages.map(p=>[p.id,p.templateId])")}
    ims=[]
    for th in TH:
        await pg.select_option('#themeSelect',th);await pg.wait_for_timeout(400)
        row=[]
        for t in (5,6):
            await ev(f"()=>Revival.go('{pid[t]}')");await pg.wait_for_timeout(450)
            p=f'/tmp/s_{th}_{t}.png';await pg.locator('#stageHost .rv-stage').screenshot(path=p);row.append(Image.open(p).convert('RGB'))
        ims.append(row)
    w=460;hh=int(w*row[0].height/row[0].width)
    out=Image.new('RGB',(w*4+30,(hh+10)*4),'white')
    for i,row in enumerate(ims):
        for j,im in enumerate(row):
            x=(i%2)*(2*w+20)+j*w+ (5 if j else 0);y=(i//2)*(hh+10)
            out.paste(im.resize((w-5,hh)),(x,y))
    out.save('/home/claude/tests/shots_v44.png');await h.close()
asyncio.run(main(sys.argv[1]))
