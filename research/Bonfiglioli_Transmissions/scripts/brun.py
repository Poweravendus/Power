"""Scenario runner for BONFIG_Model_v2.xlsx.
Usage: python3 brun.py <model.xlsx> <out.json> [--paste]
Switches Drivers!C3 to 1/2/3, recalculates with LibreOffice, reads results and checks; with --paste writes the
bear/base/bull table and the floor memo (floor = base rows overridden with committed-only values, run on a temp copy)
into Valuations, then sets the selector back to 2 and recalculates.
"""
import openpyxl, subprocess, json, sys, shutil, os
RECALC = '/root/.claude/skills/synced/593953b5-e569-4bc3-b4b6-3872b98e3292_8cf91ca0-2d35-4644-8101-30affa8a602c/xlsx/scripts/recalc.py'
FN, OUTJ = sys.argv[1], sys.argv[2]
PASTE = '--paste' in sys.argv


def recalc(fn):
    o = subprocess.run(['python3', RECALC, fn, '60'], capture_output=True, text=True).stdout
    return json.loads(o[o.index('{'):])


def rows_by_label(ws, col='A'):
    return {str(ws[f'{col}{r}'].value).strip(): r for r in range(1, ws.max_row + 1) if ws[f'{col}{r}'].value}


def read(fn):
    wb = openpyxl.load_workbook(fn, data_only=True)
    p, d, v, q, s = wb['P&L'], wb['Drivers'], wb['Valuations'], wb['Quarterly'], wb['Segments']
    L = rows_by_label(p); DL = rows_by_label(d)
    g = lambda ws, r, cols: [ws[f'{c}{r}'].value for c in cols]
    FCs = 'EFGHI'
    out = {
        'scenario': d['D3'].value,
        'rev': g(p, L['Revenue from operations'], 'BCDEFGHI'), 'ebitda': g(p, L['EBITDA (excl. other income)'], 'BCDEFGHI'),
        'ebm': g(p, L['EBITDA margin'], 'BCDEFGHI'), 'pat': g(p, L['PAT (reported)'], 'BCDEFGHI'),
        'patc': g(p, L['PAT from continuing operations'], 'BCDEFGHI'), 'eps': g(p, L['EPS, continuing (Rs., bonus-adjusted)'], 'BCDEFGHI'),
        'cfo': g(p, L['Cash from operations (CFO)'], 'BCDEFGHI'), 'fcf': g(p, L['Free cash flow (CFO - capex)'], 'BCDEFGHI'),
        'netcash': g(p, L['Net cash (cash and bank - borrowings - leases)'], 'BCDEFGHI'), 'roe': g(p, L['ROE (PAT / average equity)'], 'BCDEFGHI'),
        'roce': g(p, L['ROCE (EBIT / average equity + debt + leases)'], 'BCDEFGHI'),
        'growth': g(p, L['growth'], 'BCDEFGHI'),
        'tp': v['C21'].value, 'up': v['C22'].value, 'rating': v['C23'].value, 'dist': v['C24'].value, 'ev_tp': v['C33'].value,
        'vs_guide': [d[f'{c}{DL["CHECK: live revenue vs guidance (base must be < 0; bull ~0)"]}'].value for c in 'CDEFG'],
        'pos': [d[f'{c}{DL["Live revenue position between floor (0%) and guidance (100%)"]}'].value for c in 'CDEFG'],
        'm_vs_guide': [d[f'{c}{DL["CHECK: live margin minus guidance (base must be < 0)"]}'].value for c in 'DEFG'],
        'util': [d[f'{c}{DL["Implied utilisation (company says 75% in H1FY26; >85% is tight)"]}'].value for c in 'CDEFG'],
        'guide_rev': [d[f'{c}{DL["Management guidance: revenue"]}'].value for c in 'CDEFG'],
        'floor_rev': [d[f'{c}{DL[[k for k in DL if k.startswith("Floor revenue")][0]]}'].value for c in 'CDEFG'],
        'vert': {k: [d[f'{c}{DL[k]}'].value for c in 'CDEFG'] for k in ['I&A (existing products) revenue', 'Off-Highway Mobility revenue', 'Wind revenue']},
        'hd': [d[f'{c}{DL["New heavy-duty plant revenue - LIVE"]}'].value for c in 'CDEFG'],
    }
    checks = []
    for k in L:
        if k.startswith('CHECK'):
            checks += [abs(x) for x in g(p, L[k], 'BCDEFGHI') if isinstance(x, (int, float))]
    QL = rows_by_label(q)
    checks.append(abs(q[f'B{[r for k, r in QL.items() if k.startswith("CHECK")][0]}'].value or 0))
    SL = rows_by_label(s)
    checks += [abs(x) for x in g(s, SL['CHECK: verticals vs P&L revenue (should be 0)'], 'BCDEFGHIJK') if isinstance(x, (int, float))]
    checks += [abs(x) for x in g(s, SL['CHECK: geography sum vs reported total (should be 0)'], 'BCDEF') if isinstance(x, (int, float))]
    checks += [abs(x) for x in g(s, SL['CHECK: channel sum vs revenue (should be 0)'], 'BCDEF') if isinstance(x, (int, float))]
    out['max_check'] = max(checks)
    out['val_check'] = v['C50'].value
    return out


def set_sel(fn, sval):
    wb = openpyxl.load_workbook(fn); wb['Drivers']['C3'] = sval; wb.save(fn)


res = {}
for sc in (1, 2, 3):
    set_sel(FN, sc)
    j = recalc(FN)
    r = read(FN); r['errors'] = j['total_errors']; r['err_detail'] = j.get('error_summary')
    res[sc] = r
    print(sc, r['scenario'], 'err', j['total_errors'], 'maxchk', round(r['max_check'], 6), 'rev', [round(x, 1) for x in r['rev'][3:]],
          'ebm', [round(x, 4) for x in r['ebm'][3:]], 'eps', [round(x, 2) for x in r['eps'][3:]], 'tp', round(r['tp'], 1), 'up', round(r['up'], 4), r['rating'],
          'vsG', [round(x, 4) for x in r['vs_guide']], 'pos', [round(x, 2) for x in r['pos']], 'util', [round(x, 3) for x in r['util']])

# floor: copy, override base rows with committed-only values, run as scenario 2
tmp = FN.replace('.xlsx', '_floor_tmp.xlsx')
shutil.copy(FN, tmp)
wb = openpyxl.load_workbook(tmp); d = wb['Drivers']
DL = rows_by_label(d)
def base_row(prefix):
    return DL[[k for k in DL if k.strip().startswith(prefix) and k.strip().endswith('- Base')][0]]
for k in ['I&A (existing products) growth', 'Off-Highway Mobility growth', 'Wind growth']:
    r = base_row(k)
    d[f'C{r}'] = 0.0
    for c in 'DEFG': d[f'{c}{r}'] = 0.07
r = base_row('New heavy-duty plant revenue')
for c in 'CDEFG': d[f'{c}{r}'] = 0
r = base_row('Materials cost % of core revenue')
d['C' + str(r)] = 0.614
for c in 'DEFG': d[f'{c}{r}'] = 0.631
d['C3'] = 2
wb.save(tmp); recalc(tmp); fl = read(tmp); os.remove(tmp)
res['floor'] = fl
print('floor rev', [round(x, 1) for x in fl['rev'][3:]], 'ebm', [round(x, 4) for x in fl['ebm'][3:]], 'eps', [round(x, 2) for x in fl['eps'][3:]], 'tp', round(fl['tp'], 1))

if PASTE:
    wb = openpyxl.load_workbook(FN); v = wb['Valuations']
    for i, sc in enumerate((1, 2, 3)):
        r = res[sc]; row = 47 + i
        vals = [r['rev'][4], r['ebitda'][4], r['patc'][4], r['eps'][4], r['tp'], r['up'], r['rating'], r['ev_tp'], r['eps'][5]]
        for j, val in enumerate(vals):
            c = v.cell(row=row, column=3 + j, value=val)
            c.font = openpyxl.styles.Font(name='Arial', size=9, color='0000FF')
            c.number_format = ['#,##0', '#,##0', '#,##0', '0.00', '0', '0.0%', 'General', '0', '0.00'][j]
    for j, c in enumerate('CDEFG'):
        for i, key in enumerate(['rev', 'ebitda', 'patc', 'eps']):
            cell = v[f'{c}{54+i}']; cell.value = fl[key][3 + j]
            cell.font = openpyxl.styles.Font(name='Arial', size=9, color='0000FF'); cell.number_format = '0.00' if key == 'eps' else '#,##0'
    tpf = 45 * fl['eps'][4]
    for ref, val, fm in [('C58', tpf, '0'), ('C59', tpf / v['C2'].value - 1, '0.0%'), ('C60', 'BUY' if tpf / v['C2'].value - 1 > 0.15 else ('HOLD' if tpf / v['C2'].value - 1 >= -0.05 else 'SELL'), 'General')]:
        v[ref] = val; v[ref].font = openpyxl.styles.Font(name='Arial', size=9, color='0000FF'); v[ref].number_format = fm
    wb['Drivers']['C3'] = 2
    wb.save(FN)
    j = recalc(FN); r = read(FN)
    print('after paste: errors', j['total_errors'], 'max_check', r['max_check'], 'val_check', r['val_check'])
    res['final'] = {'errors': j['total_errors'], 'max_check': r['max_check'], 'val_check': r['val_check']}
else:
    set_sel(FN, 2); recalc(FN)
json.dump(res, open(OUTJ, 'w'), indent=1, default=str)
