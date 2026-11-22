"""Parse the H1 FY27 (30-Sep-2026, IndiaAppraisers) valuation report into the same JSON layout as vr26.json."""
import re, json, sys, math, datetime as dt
txt = open(sys.argv[1]).read().split('\f')
out = sys.argv[2]
NAMES = {'VTL': 'Vizag Transmission Limited', 'KATL': 'Kala Amb Transmission Limited', 'PPTL': 'Parli Power Transmission Limited',
         'WTL': 'Warora Transmission Limited', 'JPTL': 'Jabalpur Power Transmission Limited'}
MON = {m: i + 1 for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}
def num(s):
    s = s.strip().replace(',', '').replace('₹', '').replace('`', '').strip()
    if s in ('-', '–', ''): return 0.0
    if s.startswith('(') and s.endswith(')'): s = '-' + s[1:-1]
    return float(s)
N = r'(\(?-?[\d,]+\.\d+\)?|-)'
row_re = re.compile(r'^\s*(\d+)\s+(\d+|End of Contract)\s+(\d\d-[A-Za-z]{3}-\d\d)\s+(.*)$')
TOK = r'\(?-?[\d,]+(?:\.\d+)?\)?|-'
tv_re = re.compile(r'^\s*\d+\s+Terminal year\s+(\d\d-[A-Za-z]{3}-\d\d)\s+(.*)$')
wacc = {}
res = {}
full = '\f'.join(txt)
for spv, name in NAMES.items():
    # DCF summary
    blk = re.search(r'DCF SUMMARY\s*[-–]\s*' + spv + r'\b(.*?)Number of Equity', full, re.S).group(1)
    def grab(lab, which=0):
        v = re.findall(lab + r'\s+[₹`]?\s*([\d,]+\.\d+)', blk)
        return num(v[which]) if len(v) > which else None
    b = {'name': name, 'pv_explicit': grab('PV of explicit-period FCFF'), 'pv_tv': grab('PV of Terminal Value'),
         'rtm_pv_explicit': grab('PV of explicit-period FCFF', 1), 'rtm_pv_tv': grab('PV of Terminal Value', 1),
         'rtm_borrowings': grab('Add Borrowings'), 'ev': grab('Enterprise Value')}
    # DCF working rows
    pg = re.search(r'DCF Working\s*[–-]\s*' + spv + r'\b(.*?)(?:Sensitivity Analysis|\Z)', full, re.S).group(1)
    rows, tv = [], None
    for l in pg.splitlines():
        r = row_re.match(l)
        if r and 'Terminal' not in l:
            g = r.groups()
            d, mo, y = g[2].split('-')
            date = dt.date(2000 + int(y), MON[mo], int(d))
            if g[1].isdigit():
                months = int(g[1])
            else:   # contract-end stub: months from 1 April of that fiscal year
                fy_start = dt.date(date.year if date.month >= 4 else date.year - 1, 4, 1)
                months = round((date - fy_start).days / 30.4375)
            toks = [(m.group(0), m.end()) for m in re.finditer(TOK, g[3])]
            vals = [num(x) for x, _ in toks]
            rev, nopat, dep = vals[:3]
            fcff, yf, pvf, pv = vals[-4:]
            mid = toks[3:-4]
            capex = dwc = 0.0
            if len(mid) == 2:
                capex, dwc = num(mid[0][0]), num(mid[1][0])
            elif len(mid) == 1 and num(mid[0][0]) != 0:
                # single figure: capex column ends ~65% of the way between depreciation and FCFF
                pos = (mid[0][1] - toks[2][1]) / (toks[-4][1] - toks[2][1])
                capex, dwc = (num(mid[0][0]), 0.0) if pos < 0.55 else (0.0, num(mid[0][0]))
                print('  single mid figure', spv, g[2], mid[0][0], 'pos', round(pos, 2))
            rows.append(dict(n=int(g[0]), months=months, date=date.strftime('%d-%m-%Y'), revenue=rev, nopat=nopat, dep=dep,
                             capex=capex, dwc=dwc, fcff=fcff, yearfrac=yf, pvf=pvf, pv=pv))
            continue
        t = tv_re.match(l)
        if t:
            v = [num(x) for x in re.findall(r'\(?-?[\d,]+\.\d+\)?', t.group(2))]
            tv = dict(revenue=v[0], nopat=v[1], dep=v[2], capex=v[3], fcff=v[1] + v[2] + v[3])
    b['rows'], b['wacc'] = rows, 0.0736
    # TV discounting period implied by the valuer's PV of TV (g = 0%)
    tvu = tv['fcff'] / 0.0736
    tv['yearfrac'] = round(math.log(tvu / b['pv_tv']) / math.log(1.0736), 4)
    tv['dwc'], tv['pvf'], tv['pv'] = 0.0, b['pv_tv'] / tvu, b['pv_tv']
    b['tv'] = tv
    res[name] = b
json.dump(res, open(out, 'w'), indent=1)
for n, b in res.items():
    r = b['rows']
    pv = sum(x['fcff'] / 1.0736 ** x['yearfrac'] for x in r)
    rtm = (b['rtm_pv_explicit'] or 0) + (b['rtm_pv_tv'] or 0) + (b['rtm_borrowings'] or 0)
    print(f"{n[:32]:32s} rows={len(r)} {r[0]['date']} m={r[0]['months']} .. {r[-1]['date']} m={r[-1]['months']} pv_exp {b['pv_explicit']} recomputed {pv:,.2f} "
          f"tvper {b['tv']['yearfrac']} lastper {r[-1]['yearfrac']} EV {b['ev']} = {b['pv_explicit'] + b['pv_tv'] + rtm:,.2f} rtm {rtm:.2f} fcff_err {max(abs(x['nopat']+x['dep']+x['capex']+x['dwc']-x['fcff']) for x in r):.3f}")
print('Total EV (Rs cr)', round(sum(b['ev'] for b in res.values()) / 10, 2))
