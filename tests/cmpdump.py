import json, sys, collections
a = json.load(open(sys.argv[1])); b = json.load(open(sys.argv[2]))
diff = []; ks = sorted(set(a) | set(b)); cat = collections.Counter()
for k in ks:
    x, y = a.get(k), b.get(k)
    if x == y: continue
    if x is None or y is None: diff.append((k, 'missing')); continue
    if len(x) != len(y): diff.append((k, f'len {len(x)}!={len(y)}')); continue
    bad = [i for i, (p, q) in enumerate(zip(x, y)) if p != q]
    for i in bad:
        P = x[i].split('=')[1].split(','); Q = y[i].split('=')[1].split(',')
        for n, (u, v) in zip(['style', 'before', 'after', 'rect'], zip(P, Q)):
            if u != v: cat[n] += 1
    diff.append((k, f'{len(bad)} el', bad[:4], [x[i] + ' | ' + y[i] for i in bad[:2]]))
print('states', len(ks), 'differ', len(diff), dict(cat))
for d in diff[:int(sys.argv[3]) if len(sys.argv) > 3 else 25]: print(d)
