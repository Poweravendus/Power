"""Scenario runner for PASUPTAC_Model_v2.xlsx.
Usage: python3 pal_run.py <model.xlsx> <model_map.json> <out.json>
Switches Drivers!C3 to 1 bear, 2 base, 3 bull, 4 floor; recalculates with LibreOffice; reads results and every CHECK row;
pastes the scenario table and the floor memo into Valuations and the bull/floor rows into Drivers (values); sets the selector
back to 2 and recalculates. Balance sheet must balance in every scenario.
"""
import openpyxl, subprocess, json, sys
RECALC = '/root/.claude/skills/synced/593953b5-e569-4bc3-b4b6-3872b98e3292_8cf91ca0-2d35-4644-8101-30affa8a602c/xlsx/scripts/recalc.py'
FN, MAP, OUTJ = sys.argv[1:4]
M = json.load(open(MAP)); R, B, C, X, V, S, QR = M['R'], M['B'], M['C'], M['X'], M['V'], M['S'], M['QR']
ALLC = list('BCDEFGHIJKLMNO'); FC = list('LMNO')


def recalc():
    o = subprocess.run(['python3', RECALC, FN, '90'], capture_output=True, text=True).stdout
    return json.loads(o[o.index('{'):])


def set_sel(v):
    wb = openpyxl.load_workbook(FN); wb['Drivers']['C3'].value = v; wb.save(FN)


def read():
    wb = openpyxl.load_workbook(FN, data_only=True)
    pl, bs, cf, dv, va, sg, q = (wb[n] for n in ['P&L', 'BS', 'CF', 'Drivers', 'Valuations', 'Segments', 'Quarterly'])
    g = lambda ws, r, cols: [ws[f'{c}{r}'].value for c in cols]
    o = {k: g(pl, R[k], ALLC) for k in ['rev', 'ebitda', 'ebm', 'pat', 'eps', 'dep', 'fin', 'oi']}
    o['cfo'] = g(cf, C['cfo'], ALLC); o['fcf'] = g(cf, C['fcf'], ALLC); o['netdebt'] = g(bs, B['netdebt'], ALLC); o['liq'] = g(bs, B['liq'], ALLC)
    for k in ['frev', 'crev', 'erev', 'feb', 'ceb', 'eeb', 'fvol', 'cvol', 'evol', 'febkg', 'cebkg', 'eebl', 'fspr', 'freal', 'rev', 'eb', 'capex']:
        o['d_' + k] = g(dv, X[k], 'CDEF')
    o['pos'] = g(dv, X['pos'], 'CDEF'); o['chk_g'] = g(dv, X['chk_g'], 'CDEF'); o['chk_ge'] = g(dv, X['chk_ge'], 'CDEF')
    for k in ['tp', 'up', 'rating', 'dist', 'bord', 'ev_tp', 'evm_now', 'rev_pat', 'base_pat', 'rev_gap', 'mcap', 'chance']:
        o[k] = va[f'C{V[k]}'].value
    o['mid'] = [va[f'C{V["mid"] + i}'].value for i in range(1, 6)]
    checks = []
    for ws, lab in [(pl, 'P&L'), (bs, 'BS'), (cf, 'CF'), (sg, 'Segments')]:
        for r in range(1, ws.max_row + 1):
            a = ws[f'A{r}'].value
            if a and str(a).startswith('CHECK'):
                checks += [(lab, a, c, ws[f'{c}{r}'].value) for c in ALLC if isinstance(ws[f'{c}{r}'].value, (int, float))]
    for r in range(1, q.max_row + 1):
        a = q[f'A{r}'].value
        if a and str(a).startswith('CHECK'):
            checks += [('Q', a, c, q[f'{c}{r}'].value) for c in 'BCDEFGHIJKLMNOP' if isinstance(q[f'{c}{r}'].value, (int, float))]
    checks += [('Drivers', 'EBITDA tie', c, dv[f'{c}{X["chk_eb"]}'].value) for c in 'CDEF']
    o['max_check'] = max(abs(x[3]) for x in checks)
    o['bad_checks'] = [x for x in checks if abs(x[3]) > 0.05]
    o['bs_max'] = max(abs(bs[f'{c}{B["chk_bs"]}'].value or 0) for c in ALLC)
    return o


res = {}
for sel, nm in [(4, 'floor'), (1, 'bear'), (3, 'bull'), (2, 'base')]:
    set_sel(sel); rc = recalc(); res[nm] = read(); res[nm]['errors'] = rc.get('total_errors')
    print(nm, 'errors', rc.get('total_errors'), 'max_check', round(res[nm]['max_check'], 4), 'bs', res[nm]['bs_max'], 'EPS28', round(res[nm]['eps'][11], 2), 'TP', round(res[nm]['tp'], 1))

# paste values
wb = openpyxl.load_workbook(FN)
va, dv = wb['Valuations'], wb['Drivers']
from openpyxl.styles import Font
t0 = V['tab']
for j, nm in enumerate(['floor', 'bear', 'base', 'bull']):
    r = res[nm]; col = 'CDEF'[j]
    vals = [r['rev'][11], r['ebitda'][11], r['ebm'][11], r['pat'][11], r['eps'][11], r['tp'], r['up'], r['rev'][10], r['pat'][10], r['rev'][13], r['pat'][13], r['bs_max']]
    fm = ['#,##0.0', '#,##0.0', '0.0%', '#,##0.0', '0.00', '#,##0.0', '0.0%', '#,##0.0', '#,##0.0', '#,##0.0', '#,##0.0', '0.000']
    for i, v in enumerate(vals):
        c = va[f'{col}{t0 + i}']; c.value = v; c.number_format = fm[i]; c.font = Font(name='Arial', size=9, color='0000FF')
for j, col in enumerate('CDEF'):
    for k, nm, key in [('g_rev', 'bull', 'd_rev'), ('g_eb', 'bull', 'd_eb'), ('f_rev', 'floor', 'd_rev'), ('f_eb', 'floor', 'd_eb')]:
        c = dv[f'{col}{X[k]}']; c.value = res[nm][key][j]; c.number_format = '#,##0.0'; c.font = Font(name='Arial', size=9, color='0000FF')
dv['C3'].value = 2
wb.save(FN)
rc = recalc(); res['base'] = read(); res['base']['errors'] = rc.get('total_errors')
print('final base errors', rc.get('total_errors'), 'max_check', res['base']['max_check'], 'pos', res['base']['pos'], 'chk_g', res['base']['chk_g'], 'chk_ge', res['base']['chk_ge'], 'chance', res['base']['chance'])
json.dump(res, open(OUTJ, 'w'), indent=1, default=str)
