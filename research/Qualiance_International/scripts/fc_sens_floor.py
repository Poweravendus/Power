"""Final check 28-Nov-2026: re-run the base sensitivities (Valuations rows 90-95) and rebuild the
re-based floor (Valuations rows 57-65) on a COPY of the model. Usage: fc_sens_floor.py <model> <workdir>"""
import openpyxl, subprocess, json, sys, shutil, os
R = '/root/.claude/skills/synced/593953b5-e569-4bc3-b4b6-3872b98e3292_8cf91ca0-2d35-4644-8101-30affa8a602c/xlsx/scripts/recalc.py'
src, wd = sys.argv[1], sys.argv[2]
cases = {
  'base': {},
  'price1400': {f'{c}164': 1400 for c in 'CDEF'},
  'price1600': {f'{c}164': 1600 for c in 'CDEF'},
  'price1960_brandcost': {f'{c}164': 1960 for c in 'CDEF'},
  'mgmt_fill_1100': {'D19': 0.325, 'E19': 0.6, 'F19': 0.9},
  # floor: committed-only fill, existing 80% FY27 then 82%, Rs.1,975, new unit Rs.1,100 at 54/22
  'floor': {'C9': 0.80, 'D9': 0.82, 'E9': 0.82, 'F9': 0.82, 'D19': 0.12, 'E19': 0.25, 'F19': 0.40},
}
res = {}
for k, ch in cases.items():
    F = os.path.join(wd, f'sens_{k}.xlsx'); shutil.copy(src, F)
    wb = openpyxl.load_workbook(F); d = wb['Drivers']; d['C3'] = 2
    for ref, v in ch.items(): d[ref] = v
    wb.save(F)
    o = subprocess.run(['python3', R, F, '60'], capture_output=True, text=True).stdout
    j = json.loads(o[o.index('{'):])
    wv = openpyxl.load_workbook(F, data_only=True); p = wv['P&L']; v = wv['Valuations']
    r = dict(err=j['total_errors'], rev=[round(p[f'{c}3'].value, 2) for c in 'FGHI'],
             ebitda=[round(p[f'{c}15'].value, 2) for c in 'FGHI'], pat=[round(p[f'{c}27'].value, 2) for c in 'FGHI'],
             eps=[round(p[f'{c}33'].value, 3) for c in 'FGHI'], tp=round(v['C26'].value, 2),
             up=round(v['C26'].value / v['C2'].value - 1, 4), ebm28=round(p['G17'].value, 4))
    res[k] = r; print(k, r)
json.dump(res, open(os.path.join(wd, 'sens_floor.json'), 'w'), indent=1)
