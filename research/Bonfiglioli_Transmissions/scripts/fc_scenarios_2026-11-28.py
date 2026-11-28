"""Final check 28-Nov-2026: run scenarios 1/2/3 on a COPY of the model, collect every CHECK row on every sheet,
compare live outputs with the pasted Valuations table (rows 47-49) and floor memo, then report.
Usage: python3 fc_scenarios_2026-11-28.py <model.xlsx> <workdir>"""
import openpyxl, subprocess, json, sys, shutil, os
RECALC = '/root/.claude/skills/synced/593953b5-e569-4bc3-b4b6-3872b98e3292_8cf91ca0-2d35-4644-8101-30affa8a602c/xlsx/scripts/recalc.py'
src, wd = sys.argv[1], sys.argv[2]
os.makedirs(wd, exist_ok=True)
def recalc(fn):
    o = subprocess.run(['python3', RECALC, fn, '90'], capture_output=True, text=True).stdout
    return json.loads(o[o.index('{'):])
SKIP = ('CHECK: live revenue vs guidance', 'CHECK: live margin minus guidance', 'CHECK-ish')
out = {}
for sc in (1, 2, 3):
    fn = os.path.join(wd, f'sc{sc}.xlsx'); shutil.copy(src, fn)
    wb = openpyxl.load_workbook(fn); wb['Drivers']['C3'] = sc; wb.save(fn)
    j = recalc(fn)
    wv = openpyxl.load_workbook(fn, data_only=True)
    checks = []
    for ws in wv.worksheets:
        for r in range(1, ws.max_row + 1):
            for col in ('A', 'B'):
                lab = ws[f'{col}{r}'].value
                if isinstance(lab, str) and lab.strip().upper().startswith('CHECK') and not lab.startswith(SKIP):
                    vals = [ws.cell(row=r, column=c).value for c in range(2 if col == 'A' else 3, ws.max_column + 1)]
                    nums = [v for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool)]
                    checks.append((ws.title, r, lab[:60], max([abs(x) for x in nums], default=None), len(nums)))
    p, v, d = wv['P&L'], wv['Valuations'], wv['Drivers']
    live = dict(rev=p['F3'].value, ebitda=p['F14'].value, pat=p['F23'].value, eps=p['F28'].value, tp=v['C21'].value,
                up=v['C22'].value, rating=v['C23'].value, ev=v['C33'].value, eps28=p['G28'].value)
    pasted = dict(zip(['rev', 'ebitda', 'pat', 'eps', 'tp', 'up', 'rating', 'ev', 'eps28'],
                      [v.cell(row=46 + sc, column=c).value for c in range(3, 12)]))
    diff = {k: (live[k] - pasted[k] if isinstance(live[k], (int, float)) else (live[k] == pasted[k])) for k in live}
    out[sc] = dict(errors=j['total_errors'], scen=d['D3'].value, checks=checks, live=live, diff=diff,
                   vsG=[d.cell(row=44, column=c).value for c in range(3, 8)], mvsG=[d.cell(row=60, column=c).value for c in range(4, 8)],
                   rev=[p.cell(row=3, column=c).value for c in range(2, 10)], ebm=[p.cell(row=15, column=c).value for c in range(2, 10)],
                   eps=[p.cell(row=28, column=c).value for c in range(2, 10)], netcash=[p.cell(row=79, column=c).value for c in range(2, 10)])
    print(f'--- scenario {sc} {d["D3"].value}: formula errors {j["total_errors"]}')
    for c in checks: print('   ', c)
    print('   live', {k: (round(x, 3) if isinstance(x, float) else x) for k, x in live.items()})
    print('   live-pasted', {k: (round(x, 6) if isinstance(x, float) else x) for k, x in diff.items()})
    print('   rev vs guidance', [round(x, 4) for x in out[sc]['vsG']], 'margin vs guidance', [round(x, 4) for x in out[sc]['mvsG']])
json.dump(out, open(os.path.join(wd, 'scenarios.json'), 'w'), indent=1, default=str)
