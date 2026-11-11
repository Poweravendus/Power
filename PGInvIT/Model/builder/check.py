import openpyxl, sys, collections
sys.path.insert(0, '.')
from core import SPVS, A_START, A_BLOCK, a_row, SEN
from rest import ccol
wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
errs = collections.Counter(); ex = {}
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith('#') or (isinstance(c.value, str) and c.value in ('#VALUE!', '#REF!', '#NAME?', '#DIV/0!', '#N/A', 'Err:502', 'Err:504')):
                errs[ws.title] += 1; ex.setdefault(ws.title, []).append(f'{c.coordinate}={c.value}')
print('errors:', dict(errs), {k: v[:8] for k, v in ex.items()})
l = wb['AssetLevelEst']
for i, s in enumerate(SPVS):
    r0 = A_START + A_BLOCK * i
    print(f'{s}: EV {l[f"D{r0+18}"].value:,.2f} vs valuer {l[f"E{r0+18}"].value:,.2f} ({l[f"F{r0+18}"].value:.3%})')
from core import A_ITEMS
a = wb['Assumption']; print('AUM check FY26 - valuer EV:', round(a.cell(a_row(A_ITEMS[-1]) + 4, 4).value, 3)); print('levered tax FY27..FY35:', [round(a.cell(a_row('Taxation (levered, used for NDCF)'), k).value) for k in range(5, 14)], 'unlevered:', [round(a.cell(a_row('Taxation'), k).value) for k in range(5, 14)])
c = wb['Consolidated']
yrs = range(2022, 2036)
def row(r, fmt='{:,.1f}'):
    return ' '.join((fmt.format(c[f'{ccol(fy)}{r}'].value) if isinstance(c[f'{ccol(fy)}{r}'].value, (int, float)) else str(c[f'{ccol(fy)}{r}'].value)) for fy in yrs)
print('years      ', ' '.join(f'FY{fy%100}' for fy in yrs))
for lab, r, f in [('Revenue', 6, '{:,.0f}'), ('EBITDA', 17, '{:,.0f}'), ('PAT', 43, '{:,.0f}'), ('Tax', 40, '{:,.0f}'), ('NDCF gen', 232, '{:,.0f}'), ('NDCF', 238, '{:,.0f}'), ('Prop', 244, '{:,.0f}'), ('Distrib', 246, '{:,.0f}'),
                  ('DPU', 58, '{:,.2f}'), ('BS diff', 115, '{:,.2f}'), ('Cash', 102, '{:,.0f}'), ('Debt', 76, '{:,.0f}'), ('AUM', 249, '{:,.0f}'), ('NAV/unit', 252, '{:,.2f}'), ('Check', 247, '{}')]:
    print(f'{lab:10s}', row(r, f))
print('FY26 NAV check vs 90.79:', c['G254'].value)
cf = wb['Cashflows_Bajaj']; print('Cashflows check row (FY27..):', [round(cf.cell(25, k).value or 0, 2) for k in range(3, 12)])
s = wb['Sensitivity_Bajaj']; print('Sensitivity B3/C3 (should be empty):', s['B3'].value, s['C3'].value)
irr = wb['IRR Calculation_Bajaj']; print('IRR calc:', irr['B11'].value, '| C9', irr['C9'].value, '| yields', [round(irr.cell(15,k).value,4) for k in range(3,8)])
