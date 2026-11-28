"""Build daily/weekly close price csv for PASUPTAC from Screener chart API json files.
Usage: python3 -I price_csv.py <long_json (weekly, since 2005)> <daily_json (last 365 days)> <out_csv>
Daily rows replace weekly rows for the last year. Columns: date, close, volume, delivery_pct, frequency."""
import json, sys
lw, ld, out = sys.argv[1:4]
def load(f):
    d = json.load(open(f)); ds = {x['metric']: x['values'] for x in d['datasets']}
    vol = {v[0]: (v[1], (v[2] or {}).get('delivery') if len(v) > 2 else None) for v in ds['Volume']}
    return [(p[0], float(p[1]), *vol.get(p[0], (None, None))) for p in ds['Price']]
W, D = load(lw), load(ld)
start = D[0][0]
rows = [r + ('weekly',) for r in W if r[0] < start] + [r + ('daily',) for r in D]
with open(out, 'w') as f:
    f.write('date,close,volume,delivery_pct,frequency\n')
    for r in rows: f.write(','.join('' if x is None else str(x) for x in r) + '\n')
print(len(rows), rows[0], rows[-1])
