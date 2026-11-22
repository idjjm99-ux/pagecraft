# 사용: python3 -I css45_build.py <in.html> <out.html> [valid.json]
# valid.json 없으면 브라우저(크롬)로 CSS.supports 검사해 만듦
import sys, os, re, json, asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import css45

KEEP_IN_PLACE = {'rv-startup-no-editor-flash', 'pc-step3-00_embedded-fonts', 'rv-v12220-fonts'}

def check_valid(pairs, path):
    from playwright.async_api import async_playwright
    async def run():
        async with async_playwright() as pw:
            b = await pw.chromium.launch(executable_path=next(c for c in (__import__('os').environ.get('PC_CHROME'),'/usr/bin/google-chrome','/opt/pw-browsers/chromium') if c and __import__('os').path.exists(c)), args=['--no-sandbox'])
            pg = await b.new_page(); await pg.set_content('<html></html>')
            r = await pg.evaluate("ps=>ps.map(([p,v])=>CSS.supports(p,v))", [list(x) for x in pairs])
            await b.close(); return r
    res = asyncio.run(run())
    d = {p + ':' + v: ok for (p, v), ok in zip(pairs, res)}
    json.dump(d, open(path, 'w'), ensure_ascii=False, indent=0); return d

def main(src, dst, vpath):
    s = open(src, encoding='utf-8').read()
    blocks = css45.real_style_blocks(s)
    merge = [b for b in blocks if b['id'] not in KEEP_IN_PLACE]
    assert len(blocks) == 40 and len(merge) == 37, (len(blocks), len(merge))
    parts = []
    for b in merge:
        tag = b['id'] or '(이름 없음)'
        parts.append(f'\n/* ══════ 원래 블록: {tag} ══════ */\n' + b['css'].strip('\n') + '\n')
    merged = ''.join(parts)
    if os.path.exists(vpath): valid = json.load(open(vpath))
    else: valid = check_valid(css45.candidates(merged), vpath)
    cleaned, ndead = css45.apply(merged, valid)
    head = ('\n/* PageCraft v12.45 · 화면 CSS 한 곳 정리본.\n'
            ' * v12.17~v12.44 패치 블록 37개를 원래 순서 그대로 합침(적용 우선순위 동일).\n'
            ' * 같은 선택자·같은 속성에서 뒤 선언에 완전히 덮여 적용되지 않던 선언 %d개 제거.\n'
            ' * 새 수정은 맨 아래가 아니라 해당 원래 블록 구역에 넣을 것. */' % ndead)
    new_tag = '<style id="pc-ui-css">' + head + cleaned + '</style>'
    out = s; first = merge[0]
    for b in reversed(merge):           # 뒤에서부터 지우고, 첫 블록 자리에 합친 블록
        out = out[:b['start']] + (new_tag if b is first else '') + out[b['end']:]
    open(dst, 'w', encoding='utf-8').write(out)
    imp_before = sum(b['css'].count('!important') for b in merge)
    print(f'merged {len(merge)} blocks · dead decls removed {ndead} · '
          f'!important {imp_before}->{cleaned.count("!important")} · '
          f'CSS {sum(len(b["css"]) for b in merge)//1000}KB->{len(cleaned)//1000}KB')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'valid45.json'))
