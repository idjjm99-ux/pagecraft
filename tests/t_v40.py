# v12.40: 닌텐도 빨강·하양 / 좁은 세로 그래프 이름 기울이기·건너뛰기 / 원·도넛 6개('기타')
import asyncio, sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from h import H
R = []
def ok(n, c, i=None): R.append(c); print(('OK  ' if c else 'FAIL'), n, '' if i is None else str(i)[:260])
MON = [f'{i}월' for i in range(1, 13)]
def chart(id, t, n, w, h, x=40, y=40, extra=None):
    d = {'type': t, 'labels': MON[:n] if n <= 12 else [f'항목{i}' for i in range(1, n + 1)], 'series': [{'id': 's1', 'name': '접수', 'color': '#337CB3', 'values': [(i * 37 % 11 + 3) * 100 for i in range(n)]}], 'showValues': True, 'highlight': -1}
    if extra: d.update(extra)
    return {'id': id, 'kind': 'chart', 'role': 'user', 'x': x, 'y': y, 'w': w, 'h': h, 'z': 600, 'locked': False, 'text': '', 'style': {'fill': '#FFFFFF', 'stroke': 'transparent', 'fontFamily': 'Pretendard', 'fontSize': 24}, 'chart': d}
INFO = """id=>{const svg=document.querySelector(`#stageHost [data-object-id='${id}'] svg`);const c=[...svg.querySelectorAll('[data-chart-label=category]')];const lg=[...svg.querySelectorAll('[data-chart-label=pie]')].map(t=>t.textContent);
  const ts=[...svg.querySelectorAll('text')];const Q=ts.map(t=>{const b=t.getBBox();if(!b.width)return null;const m=t.getScreenCTM();const P=(x,y)=>({x:m.a*x+m.c*y+m.e,y:m.b*x+m.d*y+m.f});return [P(b.x+.5,b.y+.5),P(b.x+b.width-.5,b.y+.5),P(b.x+b.width-.5,b.y+b.height-.5),P(b.x+.5,b.y+b.height-.5)]}).filter(Boolean);
  const sep=(A,B)=>{for(const S of [A,B])for(let i=0;i<4;i++){const p=S[i],q=S[(i+1)%4],nx=q.y-p.y,ny=p.x-q.x;const pa=A.map(v=>v.x*nx+v.y*ny),pb=B.map(v=>v.x*nx+v.y*ny);if(Math.max(...pa)<=Math.min(...pb)||Math.max(...pb)<=Math.min(...pa))return true}return false};
  let ov=0;for(let i=0;i<Q.length;i++)for(let j=i+1;j<Q.length;j++)if(!sep(Q[i],Q[j]))ov++;const box=svg.getBoundingClientRect();const out=ts.map(t=>t.getBoundingClientRect()).filter(r=>r.width&&(r.left<box.left-1||r.right>box.right+1||r.bottom>box.bottom+1)).length;
  return {n:c.length,tilt:c.filter(t=>t.dataset.tilt==='45').length,texts:c.map(t=>[...t.childNodes].filter(n=>n.nodeName!=='title').map(n=>n.textContent).join('')),titles:svg.querySelectorAll('rect title,circle title').length,ov,out,legend:lg,slices:svg.querySelectorAll('path,circle').length}}"""
async def main(path):
    h = H(); pg = await h.start(path, 1500, 950); ev = h.ev
    pal = await ev("()=>JSON.parse(document.querySelector('#revival-palettes').textContent)")
    P = {p['id']: p for p in pal}['nintendo-light']
    cols = {P[k].upper() for k in ('bg', 'panel', 'accent', 'accent2', 'highlight', 'soft', 'categoryCardFill', 'categoryBorder')}
    ok('닌텐도 테마: 빨강 #E70012·하양 #FFFFFF만(본문 글자 검정 제외)', cols == {'#E70012', '#FFFFFF'}, cols)
    css = await ev("()=>[...document.querySelectorAll('style')].map(s=>s.textContent).join('').match(/nintendo-light[^}]*#E60012/)")
    ok('닌텐도 전용 CSS도 #E70012', css is None)
    objs = [chart('b12', 'bar', 12, 320, 420), chart('l12', 'line', 12, 340, 440, 420), chart('b12w', 'bar', 12, 1000, 380, 40, 520), chart('b8', 'bar', 8, 320, 420, 800)]
    await ev("o=>{const p=Revival.getProject();const pg=p.pages[p.pages.length-1];pg.objects.push(...o);Revival.importProject(p);Revival.go(pg.id)}", objs); await pg.wait_for_timeout(600)
    b12, l12, wide, b8 = [await ev(INFO, i) for i in ('b12', 'l12', 'b12w', 'b8')]
    ok('좁은 세로 막대 12개: 이름 45° 기울임 + 한 칸씩 건너뜀(1·3·5…월)', b12['tilt'] == b12['n'] and 4 <= b12['n'] < 12 and b12['texts'][:2] == ['1월', '3월'], b12)
    ok('좁은 선 그래프 12개도 같음', l12['tilt'] == l12['n'] > 0, l12)
    ok('건너뛴 이름도 막대·점에 마우스 올리면 보임(title 12개)', b12['titles'] >= 12 and l12['titles'] >= 12, [b12['titles'], l12['titles']])
    ok('좁은 그래프 글씨 겹침·넘침 없음', b12['ov'] == 0 and l12['ov'] == 0 and b12['out'] == 0 and l12['out'] == 0, [b12['ov'], l12['ov'], b12['out'], l12['out']])
    ok('넓은 그래프 12개는 그대로(기울임 없음·12개 모두)', wide['tilt'] == 0 and wide['n'] == 12, wide)
    ok('8개 이하는 그대로(기울임 없음)', b8['tilt'] == 0 and b8['n'] == 8, b8)
    hb = [chart('h20', 'hbar', 20, 760, 380, 40, 40)]
    await ev("o=>{const p=Revival.getProject();const pg=p.pages[p.pages.length-1];pg.objects=pg.objects.filter(x=>!/^(b12|l12|b12w|b8)$/.test(x.id));pg.objects.push(...o);Revival.importProject(p);Revival.go(pg.id)}", hb); await pg.wait_for_timeout(500)
    x = await ev(INFO, 'h20')
    ok('가로 막대 20개(낮은 칸): 이름 건너뜀·겹침 없음', 0 < x['n'] < 20 and x['ov'] == 0, x)
    # 원·도넛
    pies = [chart('p8', 'pie', 8, 600, 380, 40, 440), chart('d12', 'donut', 12, 600, 380, 680, 440), chart('p5', 'pie', 5, 500, 340, 900, 40), chart('pn', 'pie', 8, 400, 300, 40, 40, {'series': [{'id': 's1', 'name': 'a', 'color': '#337CB3', 'values': [5, -1, 3, 4, 5, 6, 7, 8]}]})]
    await ev("o=>{const p=Revival.getProject();const pg=p.pages[p.pages.length-1];pg.objects=pg.objects.filter(x=>x.id!=='h20');pg.objects.push(...o);Revival.importProject(p);Revival.go(pg.id)}", pies); await pg.wait_for_timeout(500)
    p8, d12, p5, pn = [await ev(INFO, i) for i in ('p8', 'd12', 'p5', 'pn')]
    ok('원 8개 → 6칸(앞 5 + 기타)', len(p8['legend']) == 6 and p8['legend'][-1].startswith('기타') and p8['legend'][0].startswith('1월'), p8['legend'])
    tip = await ev("()=>[...document.querySelectorAll(`#stageHost [data-object-id='p8'] svg path title`)].map(t=>t.textContent).pop()")
    exp = sum((i * 37 % 11 + 3) * 100 for i in range(5, 8))
    ok("'기타' 값 = 나머지 합", tip and tip.startswith('기타') and f'{exp:,}' in tip, [tip, exp])
    ok('도넛 12개 → 6칸', len(d12['legend']) == 6, d12['legend'])
    ok('원 5개는 그대로', len(p5['legend']) == 5)
    ok('음수 있으면 합치지 않고 경고 유지', len(pn['legend']) == 0, pn)
    d = await ev("()=>{const o=Revival.getCurrentPage().objects.find(o=>o.id==='p8');return o.chart.labels.length}")
    ok('저장 데이터는 그대로(8개 유지)', d == 8, d)
    await ev("()=>Revival.selectOne('p5')"); await pg.wait_for_timeout(400)
    await ev("()=>{const d=document.querySelector('#inspector details[data-accordion=chart]')||[...document.querySelectorAll('#inspector details')].find(x=>x.textContent.includes('그래프 전용'));if(d)d.open=true}"); await pg.wait_for_timeout(200)
    a = await ev("()=>{const b=document.querySelector('#inspector [data-action=chartAddPoint]');return {dis:b?.disabled,tip:document.querySelector('#inspector').textContent.includes(\"'기타'로 합침\")}}")
    await pg.click('#inspector [data-action=chartAddPoint]'); await pg.wait_for_timeout(300)
    a2 = await ev("()=>({n:Revival.getCurrentPage().objects.find(o=>o.id==='p5').chart.labels.length,dis:document.querySelector('#inspector [data-action=chartAddPoint]')?.disabled})")
    ok('원 5개 → + 항목 한 번 가능, 6개에서 막힘 + 안내 문구', a['dis'] is False and a['tip'] and a2 == {'n': 6, 'dis': True}, [a, a2])
    await h.shot('v40_pies')
    ok('오류 없음', not h.errs, h.errs[:3])
    await h.close()
    print('TOTAL', sum(R), '/', len(R))
asyncio.run(main(sys.argv[1]))
