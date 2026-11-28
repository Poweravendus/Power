"""Final check 28-Nov-2026: run selector 1..4 on a COPY of the model, recalc, collect every CHECK row and
compare the pasted scenario tables (Valuations rows 28-39, Drivers bull/floor rows) with live output.
Usage: python3 -I fc_scenarios.py <model.xlsx> <workdir> <out.json>"""
import openpyxl, subprocess, json, sys, shutil, os
RECALC = '/root/.claude/skills/synced/593953b5-e569-4bc3-b4b6-3872b98e3292_8cf91ca0-2d35-4644-8101-30affa8a602c/xlsx/scripts/recalc.py'
src, wd, outj = sys.argv[1:4]
os.makedirs(wd, exist_ok=True)
ALLC = list('BCDEFGHIJKLMNOP')
res = {}
for sel, nm in [(1, 'bear'), (2, 'base'), (3, 'bull'), (4, 'floor')]:
    fn = os.path.join(wd, f'sc_{nm}.xlsx'); shutil.copy(src, fn)
    wb = openpyxl.load_workbook(fn); wb['Drivers']['C3'].value = sel; wb.save(fn)
    o = subprocess.run(['python3', RECALC, fn, '90'], capture_output=True, text=True).stdout
    rc = json.loads(o[o.index('{'):])
    wb = openpyxl.load_workbook(fn, data_only=True)
    checks = []
    for ws in wb:
        for r in range(1, ws.max_row + 1):
            a = ws[f'A{r}'].value
            if a and str(a).upper().startswith('CHECK'):
                for c in ALLC:
                    v = ws[f'{c}{r}'].value
                    if isinstance(v, (int, float)): checks.append((ws.title, r, str(a)[:60], c, v))
    pl, va, dv = wb['P&L'], wb['Valuations'], wb['Drivers']
    # 'CHECK: live vs bull' rows on Drivers are signed tests, not zero tests
    zero = [x for x in checks if not (x[0] == 'Drivers' and x[1] in (97, 98))]
    live = dict(rev28=pl['M5'].value, eb28=pl['M16'].value, ebm28=pl['M17'].value, pat28=pl['M27'].value, eps28=pl['M31'].value,
                tp=va['C8'].value, up=va['C9'].value, rev27=pl['L5'].value, pat27=pl['L27'].value, rev30=pl['O5'].value, pat30=pl['O27'].value,
                rating=va['C10'].value, drev=[dv[f'{c}87'].value for c in 'CDEF'], deb=[dv[f'{c}88'].value for c in 'CDEF'],
                eps=[pl[f'{c}31'].value for c in 'LMNO'], pat=[pl[f'{c}27'].value for c in 'LMNO'], ebitda=[pl[f'{c}16'].value for c in 'LMNO'],
                rev=[pl[f'{c}5'].value for c in 'LMNO'], netdebt=[wb['BS'][f'{c}20'].value for c in 'KLMNO'],
                cfo=[wb['CF'][f'{c}6'].value for c in 'LMNO'], midval=va['C59'].value, mid_m=va['C55'].value,
                febkg=[dv[f'{c}30'].value for c in 'CDEF'], fspr=[dv[f'{c}23'].value for c in 'CDEF'],
                diag97=[dv[f'{c}97'].value for c in 'CDEF'], diag98=[dv[f'{c}98'].value for c in 'CDEF'], pos=[dv[f'{c}99'].value for c in 'CDEF'])
    col = {'floor': 'C', 'bear': 'D', 'base': 'E', 'bull': 'F'}[nm]
    keys = ['rev28', 'eb28', 'ebm28', 'pat28', 'eps28', 'tp', 'up', 'rev27', 'pat27', 'rev30', 'pat30']
    pasted = {k: va[f'{col}{28 + i}'].value for i, k in enumerate(keys)}
    diff = {k: (live[k] - pasted[k]) for k in keys}
    res[nm] = dict(errors=rc.get('total_errors'), n_checks=len(zero), max_abs_check=max(abs(x[4]) for x in zero),
                   bad=[x for x in zero if abs(x[4]) > 0.05], live=live, pasted=pasted, diff=diff, signed=[x for x in checks if x not in zero])
    if nm == 'bull': res[nm]['drv_paste'] = dict(g_rev=[dv[f'{c}93'].value for c in 'CDEF'], g_eb=[dv[f'{c}94'].value for c in 'CDEF'])
    if nm == 'floor': res[nm]['drv_paste'] = dict(f_rev=[dv[f'{c}95'].value for c in 'CDEF'], f_eb=[dv[f'{c}96'].value for c in 'CDEF'])
    print(nm, 'errors', rc.get('total_errors'), 'checks', len(zero), 'max|check|', round(res[nm]['max_abs_check'], 4), 'bad', len(res[nm]['bad']),
          'EPS28 %.3f TP %.2f up %.3f %s' % (live['eps28'], live['tp'], live['up'], live['rating']),
          'max paste diff', round(max(abs(v) for v in diff.values()), 4))
json.dump(res, open(outj, 'w'), indent=1, default=str)
