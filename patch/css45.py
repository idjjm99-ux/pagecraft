# v12.45 CSS 정리 도구: style 블록 합치기 + 확실히 덮인(죽은) 선언 제거
# - 합치기: 시작 화면용(첫 블록)·글꼴 전용 블록은 제자리, 나머지 UI 블록은 원래 순서대로 한 블록으로 (cascade 순서 동일)
# - 제거: 같은 맥락(@media 등)·같은 선택자·같은 속성에서, 더 뒤에 같은 세기 이상(또는 더 센 !important) 선언이
#         있어 절대 적용되지 않는 선언만. 이기는 쪽 값이 브라우저에서 유효할 때만(valid.json, CSS.supports 결과)
import re, json, sys

def real_style_blocks(s):
    scr = [(m.start(), m.end()) for m in re.finditer(r'<script\b[^>]*>.*?</script>', s, re.S)]
    out = []
    for m in re.finditer(r'<style\b([^>]*)>(.*?)</style>', s, re.S):
        if any(a <= m.start() < b for a, b in scr): continue
        idm = re.search(r'id="([^"]+)"', m.group(1))
        out.append(dict(start=m.start(), end=m.end(), attrs=m.group(1), id=idm.group(1) if idm else '', css=m.group(2)))
    return out

# ── 범위(span)를 기억하는 작은 CSS 스캐너
def skip_ws_comments(c, i):
    n = len(c)
    while i < n:
        if c[i].isspace(): i += 1
        elif c.startswith('/*', i):
            j = c.find('*/', i + 2); i = n if j < 0 else j + 2
        else: break
    return i

def find_block_end(c, i):
    """c[i]=='{' → index of matching '}' (strings/comments/parens aware)"""
    depth = 0; n = len(c)
    while i < n:
        ch = c[i]
        if c.startswith('/*', i):
            j = c.find('*/', i + 2); i = n if j < 0 else j + 2; continue
        if ch in '"\'':
            j = i + 1
            while j < n and c[j] != ch:
                j += 2 if c[j] == '\\' else 1
            i = j + 1; continue
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0: return i
        i += 1
    raise ValueError('unbalanced')

def find_prelude_end(c, i):
    n = len(c); par = 0
    while i < n:
        if c.startswith('/*', i):
            j = c.find('*/', i + 2); i = n if j < 0 else j + 2; continue
        ch = c[i]
        if ch in '"\'':
            j = i + 1
            while j < n and c[j] != ch: j += 2 if c[j] == '\\' else 1
            i = j + 1; continue
        if ch == '(': par += 1
        elif ch == ')': par -= 1
        elif par == 0 and ch in '{;': return i
        i += 1
    return n

def split_decls(c, a, b):
    """declarations inside c[a:b] → list of (start,end,name,value,important); None if nested blocks"""
    out = []; i = a; par = 0; st = a
    def flush(e):
        seg = c[st:e]
        raw = re.sub(r'/\*.*?\*/', '', seg, flags=re.S).strip()
        if raw.endswith(';'): raw = raw[:-1].strip()
        if raw:
            if ':' not in raw: return 'bad'
            name, val = raw.split(':', 1); name = name.strip(); val = val.strip()
            imp = False
            m = re.search(r'!\s*important\s*$', val, re.I)
            if m: imp = True; val = val[:m.start()].strip()
            out.append((st, e, name, val, imp))
    while i < b:
        if c.startswith('/*', i):
            j = c.find('*/', i + 2); i = j + 2; continue
        ch = c[i]
        if ch in '"\'':
            j = i + 1
            while j < b and c[j] != ch: j += 2 if c[j] == '\\' else 1
            i = j + 1; continue
        if ch == '(': par += 1
        elif ch == ')': par -= 1
        elif ch == '{' : return None
        elif ch == ';' and par == 0:
            if flush(i + 1) == 'bad': return None
            st = i + 1
        i += 1
    if flush(b) == 'bad': return None
    return out

DEDUPE_AT = ('@media', '@supports', '@layer', '@container')

def walk(c, a, b, ctx, rules):
    i = a
    while True:
        i = skip_ws_comments(c, i)
        if i >= b: return
        pe = find_prelude_end(c, i)
        prelude = re.sub(r'\s+', ' ', re.sub(r'/\*.*?\*/', '', c[i:pe], flags=re.S)).strip()
        if pe >= b or c[pe] == ';':        # @import / @charset 등
            i = pe + 1; continue
        be = find_block_end(c, pe)
        if prelude.startswith('@'):
            kw = prelude.split()[0].split('(')[0].lower()
            if kw in DEDUPE_AT: walk(c, pe + 1, be, ctx + (prelude,), rules)
            # @keyframes·@font-face·@page 등은 손대지 않음
        else:
            decls = split_decls(c, pe + 1, be)
            rules.append(dict(ctx=ctx, sel=prelude, start=i, bstart=pe + 1, bend=be, end=be + 1, decls=decls))
        i = be + 1

def analyse(css):
    rules = []; walk(css, 0, len(css), (), rules); return rules

def dead_spans(css, valid):
    rules = analyse(css)
    flat = []   # (order, key, important, value, span, rule_idx)
    k = 0
    for ri, r in enumerate(rules):
        if r['decls'] is None: continue
        for (s, e, name, val, imp) in r['decls']:
            pn = name if name.startswith('--') else name.lower()
            flat.append(dict(o=k, key=(r['ctx'], r['sel'], pn), imp=imp, val=val, span=(s, e), ri=ri, prop=pn)); k += 1
    by = {}
    for d in flat: by.setdefault(d['key'], []).append(d)
    dead = []
    for key, ds in by.items():
        if len(ds) < 2: continue
        # 이기는 선언: important 우선, 같으면 뒤쪽
        win = max(ds, key=lambda d: (d['imp'], d['o']))
        if not (win['prop'].startswith('--') or valid.get(win['prop'] + ':' + win['val'], False)):
            continue
        for d in ds:
            if d is not win: dead.append(d)
    return rules, dead

def candidates(css):
    """브라우저 유효성 검사가 필요한 (속성,값) 목록"""
    rules = analyse(css); seen = {}
    for r in rules:
        if r['decls'] is None: continue
        for (s, e, name, val, imp) in r['decls']:
            pn = name if name.startswith('--') else name.lower()
            seen.setdefault((r['ctx'], r['sel'], pn), []).append(val)
    out = set()
    for (ctx, sel, pn), vals in seen.items():
        if len(vals) > 1 and not pn.startswith('--'):
            for v in vals: out.add((pn, v))
    return sorted(out)

def apply(css, valid):
    rules, dead = dead_spans(css, valid)
    cut = sorted([d['span'] for d in dead], reverse=True)
    out = css
    for s, e in cut: out = out[:s] + out[e:]
    # 비게 된 규칙 제거 (주석만 남은 것도)
    for _ in range(3):
        rr = analyse(out); changed = False
        for r in sorted(rr, key=lambda r: -r['start']):
            body = re.sub(r'/\*.*?\*/', '', out[r['bstart']:r['bend']], flags=re.S).strip().strip(';').strip()
            if r['decls'] is not None and not body:
                out = out[:r['start']] + out[r['end']:]; changed = True
        if not changed: break
    return out, len(dead)
