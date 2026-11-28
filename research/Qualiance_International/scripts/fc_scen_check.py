"""Final check 28-Nov-2026: run bear/base/bull on a COPY of the model, report formula errors,
every CHECK row on every sheet, and the live outputs vs the pasted Valuations table (rows 51-53)
and the pasted bull revenue (Drivers row 146). Usage: fc_scen_check.py <model.xlsx> <workdir>"""
import openpyxl, subprocess, json, sys, shutil, os
R = '/root/.claude/skills/synced/593953b5-e569-4bc3-b4b6-3872b98e3292_8cf91ca0-2d35-4644-8101-30affa8a602c/xlsx/scripts/recalc.py'
src, wd = sys.argv[1], sys.argv[2]
F = os.path.join(wd, 'scen_copy.xlsx'); shutil.copy(src, F)
out = {}
for s in (1, 2, 3):
    wb = openpyxl.load_workbook(F); wb['Drivers']['C3'] = s; wb.save(F)
    o = subprocess.run(['python3', R, F, '60'], capture_output=True, text=True).stdout
    j = json.loads(o[o.index('{'):])
    wf = openpyxl.load_workbook(F); wv = openpyxl.load_workbook(F, data_only=True)
    checks = {}
    for ws in wf:
        vs = wv[ws.title]
        for row in ws.iter_rows():
            lab = ' '.join(str(c.value) for c in row[:2] if isinstance(c.value, str))
            if 'CHECK' in lab.upper():
                vals = [vs[c.coordinate].value for c in row if isinstance(c.value, str) and c.value.startswith('=')]
                nums = [abs(v) for v in vals if isinstance(v, (int, float))]
                checks[f'{ws.title}!{row[0].row}'] = max(nums) if nums else None
    p = wv['P&L']; v = wv['Valuations']; d = wv['Drivers']
    r = dict(err=j['total_errors'], errs=j.get('error_summary'), checks=checks,
             rev=[p[f'{c}3'].value for c in 'FGHI'], ebitda=[p[f'{c}15'].value for c in 'FGHI'],
             ebm=[p[f'{c}17'].value for c in 'FGHI'], pat=[p[f'{c}27'].value for c in 'FGHI'],
             eps=[p[f'{c}33'].value for c in 'FGHI'], netdebt=[p[f'{c}115'].value for c in 'FGHI'],
             revolver=[p[f'{c}126'].value for c in 'FGHI'], cash=[p[f'{c}67'].value for c in 'FGHI'],
             tp=v['C26'].value, up=v['C27'].value, rating=v['C28'].value, ev_val=v['C36'].value,
             ev_val_fy28nd=(v['C33'].value - p['G115'].value) / v['C4'].value,
             ev_val_sepnc=(v['C33'].value + v['C6'].value) / v['C4'].value,
             pasted=[v.cell(50 + s, c).value for c in range(3, 11)],
             bull_rev_pasted=[d[f'{c}146'].value for c in 'CDEF'], guid=[d[f'{c}140'].value for c in 'CDEF'],
             newrev=[d[f'{c}174'].value for c in 'CDEF'], memo155=d['C155'].value)
    out[s] = r
    print('== scenario', s, 'errors', r['err'], 'max|check|', max(x for x in checks.values() if x is not None))
    for k, vv in r.items():
        if k not in ('checks',):
            print('  ', k, [round(x, 4) if isinstance(x, float) else x for x in vv] if isinstance(vv, list) else vv)
    print('   checks', {k: (round(x, 6) if x is not None else x) for k, x in checks.items()})
json.dump(out, open(os.path.join(wd, 'scen_results.json'), 'w'), indent=1, default=str)
