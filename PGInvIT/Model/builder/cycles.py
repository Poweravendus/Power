import openpyxl, re, sys
from openpyxl.utils import column_index_from_string as CI, get_column_letter as L
wb = openpyxl.load_workbook(sys.argv[1])
cells = {}
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith('='):
                cells[(ws.title, c.column, c.row)] = c.value
bycol = {}
for (s, col, r) in cells:
    bycol.setdefault((s, col), []).append(r)
ref = re.compile(r"(?:'([^']+)'|([A-Za-z_][A-Za-z0-9_]*))?!?\$?([A-Z]{1,3})\$?(\d+)?(?::\$?([A-Z]{1,3})\$?(\d+)?)?")
tok = re.compile(r"((?:'[^']+'|[A-Za-z_][A-Za-z0-9_ ]*)!)?(\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?|\$?[A-Z]{1,3}:\$?[A-Z]{1,3})")
def deps(sheet, f):
    f2 = re.sub(r'"[^"]*"', '""', f)
    out = []
    for m in tok.finditer(f2):
        sh = m.group(1)
        s = sh[:-1].strip("'") if sh else sheet
        body = m.group(2).replace('$', '')
        if ':' in body:
            a, b = body.split(':')
            ma, mb = re.match(r'([A-Z]+)(\d*)', a), re.match(r'([A-Z]+)(\d*)', b)
            c1, c2 = CI(ma.group(1)), CI(mb.group(1))
            if ma.group(2) == '':
                for col in range(c1, c2 + 1):
                    for r in bycol.get((s, col), []):
                        out.append((s, col, r))
            else:
                r1, r2 = int(ma.group(2)), int(mb.group(2))
                for col in range(c1, c2 + 1):
                    for r in bycol.get((s, col), []):
                        if r1 <= r <= r2:
                            out.append((s, col, r))
        else:
            mm = re.match(r'([A-Z]+)(\d+)', body)
            k = (s, CI(mm.group(1)), int(mm.group(2)))
            if k in cells:
                out.append(k)
    return out
G = {k: deps(k[0], v) for k, v in cells.items()}
# iterative Tarjan
index, low, on, st, res, idx = {}, {}, set(), [], [], [0]
for v0 in G:
    if v0 in index: continue
    stack = [(v0, iter(G[v0]))]; index[v0] = low[v0] = idx[0]; idx[0] += 1; st.append(v0); on.add(v0)
    while stack:
        v, it = stack[-1]
        for w in it:
            if w not in index:
                index[w] = low[w] = idx[0]; idx[0] += 1; st.append(w); on.add(w); stack.append((w, iter(G.get(w, [])))); break
            elif w in on:
                low[v] = min(low[v], index[w])
        else:
            stack.pop()
            if stack: low[stack[-1][0]] = min(low[stack[-1][0]], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = st.pop(); on.discard(w); comp.append(w)
                    if w == v: break
                if len(comp) > 1 or v in G.get(v, []): res.append(comp)
print('cycles:', len(res))
for comp in res[:5]:
    print(len(comp), sorted(f'{s}!{L(c)}{r}' for s, c, r in comp)[:40])
