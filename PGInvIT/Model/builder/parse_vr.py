import re, json, sys
txt = open(sys.argv[1]).read().splitlines()
out = sys.argv[2]
def num(s):
    s = s.strip().replace(',', '')
    if s in ('-', '–', ''): return 0.0
    if s.startswith('(') and s.endswith(')'): s = '-' + s[1:-1]
    return float(s)
# locate each SPV summary block by "Business enterprise value"
idx = [i for i, l in enumerate(txt) if 'Business enterprise value' in l]
names = []
res = {}
N = r'(-?[\d,]+\.\d+|-)'
rowre = re.compile(r'^\s*(\d+)\s+(\d+)\s+(\d\d-(?:\d\d|[A-Za-z]{3})-\d{2,4})\s+' + r'\s+'.join([N]*6) + r'\s+([\d.]+)\s+([\d.]+)\s+(-?[\d,]+\.\d+)\s*$')
tvre = re.compile(r'^\s*\d+\s+Terminal Year\s+Terminal (?:Value|Year)\s+' + r'\s+'.join([N]*6) + r'\s+([\d.]+)\s+([\d.]+)\s+(-?[\d,]+\.\d+)')
for k, i in enumerate(idx):
    # SPV name: search backwards for "Valuation Date" header line preceded by name
    j = i
    while j > 0 and 'DCF Valuation Analysis' not in txt[j]: j -= 1
    name = txt[j+1].strip()
    block = {'name': name}
    for l in txt[j:i+12]:
        for key, lab in [('pv_explicit','Present value of FCFF for explicit period'),('pv_rtm','Present value of FCFF for explicit period (RTM)'),('pv_tv','Present value of terminal value'),('ev','Business enterprise value'),('cash','Cash and bank balance as on date of valuation'),('debt','Borrowings as on date of valuation'),('equity','Equity value as on date of valuation')]:
            if lab in l:
                m = re.findall(r'-?[\d,]+\.\d+', l)
                if m: block[key] = num(m[-1])
    rows = []; tv = None
    end = idx[k+1] if k+1 < len(idx) else len(txt)
    for l in txt[i:end]:
        m = rowre.match(l)
        if m:
            g = m.groups()
            rows.append(dict(n=int(g[0]), months=int(g[1]), date=g[2], revenue=num(g[3]), nopat=num(g[4]), dep=num(g[5]), capex=num(g[6]), dwc=num(g[7]), fcff=num(g[8]), yearfrac=float(g[9]), pvf=float(g[10]), pv=num(g[11])))
            continue
        m = tvre.match(l)
        if m and tv is None:
            g = m.groups()
            tv = dict(revenue=num(g[0]), nopat=num(g[1]), dep=num(g[2]), capex=num(g[3]), dwc=num(g[4]), fcff=num(g[5]), yearfrac=float(g[6]), pvf=float(g[7]), pv=num(g[8]))
        if tv and rows: pass
        if 'Sensitivity Analysis' in l and rows: break
    block['rows'] = rows; block['tv'] = tv
    res[name] = block
json.dump(res, open(out, 'w'), indent=1)
for n, b in res.items():
    r = b['rows']
    chk_fcff = max(abs(x['nopat'] + x['dep'] + x['capex'] + x['dwc'] - x['fcff']) for x in r) if r else None
    print(f"{n[:40]:40s} rows={len(r):2d} first={r[0]['date'] if r else None} last={r[-1]['date'] if r else None} lastmonths={r[-1]['months'] if r else None} EV={b.get('ev')} PVexp={b.get('pv_explicit')} sumPV={sum(x['pv'] for x in r):.2f} PVTV={b.get('pv_tv')} tv={b['tv'] and (b['tv']['fcff'], b['tv']['yearfrac'])} maxFCFFerr={chk_fcff}")
