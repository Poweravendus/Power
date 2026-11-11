"""Build the PGInvIT model workbook mirroring the IndiGrid model structure."""
import json, sys, datetime as dt, os
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from core import *
from core import build_sensitivity, build_assetlevel, build_assumption
from rest import build_sens_returns, build_cashflows, build_irr, CR, ccol
from consolidated import build_consolidated
from keysheet import build_keysheet
from map_hist import build_H
from opex import build_opex

SP = '/tmp/claude-0/-home-user-Power/562dd684-59fa-5b19-94f2-822ecbb92d34/scratchpad'
OUT = sys.argv[1] if len(sys.argv) > 1 else f'{SP}/build/PGInvIT_Model.xlsx'
PRICE, ENTRY, FIRST_PAY = 105.64, dt.datetime(2026, 11, 11), dt.datetime(2026, 11, 30)
UNITS = 909999200

V, opex, margins, _ = build_opex(f'{SP}/build/vr26.json', f'{SP}/agentC/spv_history.json', f'{SP}/agentA/consolidated_history.json')
S = json.load(open(f'{SP}/agentC/spv_history.json'))['spvs']
H, CJ = build_H(f'{SP}/agentA/consolidated_history.json')
hist = {'avail': {s: S[s]['availability_annual'] for s in SPVS},
        'rev': {s: S[s]['revenue'] for s in SPVS},
        'margin': {s: {k: v for k, v in (S[s].get('ebitda_margin') or {}).items() if v is not None} for s in SPVS}}

wb = openpyxl.Workbook(); wb.remove(wb.active)
from openpyxl.styles import NamedStyle
for st in wb._named_styles:
    if st.name == 'Normal':
        st.font = font()
names = ['Key Sheet New', 'Sensitivity_Bajaj', 'Cashflows_Bajaj', 'IRR Calculation_Bajaj', 'Consolidated', 'Qtrly', 'Assumption', 'AssetLevelEst']
W = {n: wb.create_sheet(n) for n in names}

build_sensitivity(W['Sensitivity_Bajaj'], V, hist, margins, PRICE, ENTRY)
# working-capital days (hist from Consolidated, forecast = FY26 actual held flat)
ws = W['Sensitivity_Bajaj']; r = SEN['wc']
put(ws, f'B{r - 2}', 'WORKING CAPITAL  -  DAYS (consolidated)', bold=True)
put(ws, f'B{r - 1}', 'Days', bold=True, border_b=True)
for fy in range(S_FY0, FYN + 1):
    put(ws, f'{scol(fy)}{r - 1}', fy_label(fy, fy > 2026), bold=True, align='right', border_b=True)
for k, (lab, crow) in enumerate([('Receivable Days', 182), ('Inventory Days', 183), ('Payable Days', 184)]):
    put(ws, f'B{r + k}', lab)
    for fy in range(2022, FYN + 1):
        c = scol(fy)
        if fy <= 2026:
            put(ws, f'{c}{r + k}', f'=Consolidated!{ccol(fy)}{crow}', fmt=NUM1, color=RED)
        else:
            put(ws, f'{c}{r + k}', f'=$H{r + k}' if fy > 2027 else f'=H{r + k}', fmt=NUM1, color=BLUE)
put(ws, f'B{r + 3}', 'Working Capital Days', bold=True)
for fy in range(2022, FYN + 1):
    c = scol(fy)
    put(ws, f'{c}{r + 3}', f'={c}{r}+{c}{r + 1}-{c}{r + 2}', fmt=NUM1, bold=True)
build_sens_returns(ws, ENTRY, FIRST_PAY)
ws.freeze_panes = 'C8'

ainfo = build_assetlevel(W['AssetLevelEst'], V, margins, hist)
W['AssetLevelEst'].freeze_panes = 'D3'
build_assumption(W['Assumption'], V, ainfo)
W['Assumption'].freeze_panes = 'D3'

spv_opex27 = sum(opex[s][2027] for s in SPVS)
nonim26 = sum(H[r][2026] for r in (10, 11, 12, 13, 14))
drivers = {14: round(nonim26 - spv_opex27, 3), 21: 0.055, 24: f'=G23/AVERAGE(F85,G85)', 27: f'=G28/AVERAGE(F76,G76)', 228: '=G102'}
build_consolidated(W['Consolidated'], H, drivers)
W['Consolidated'].freeze_panes = 'C4'
build_cashflows(W['Cashflows_Bajaj']); W['Cashflows_Bajaj'].freeze_panes = 'C4'
build_irr(W['IRR Calculation_Bajaj'], UNITS, ENTRY)
build_keysheet(W['Key Sheet New'], S, V)

qpath = f'{SP}/agentB/quarterly_history.json'
if os.path.exists(qpath):
    from qtrly import build_qtrly
    build_qtrly(W['Qtrly'], json.load(open(qpath)))
else:
    put(W['Qtrly'], 'B2', 'Quarterly data pending', italic=True)

for n in names:
    finish_sheet(W[n])
wb.save(OUT)
print('saved', OUT, '| trust-level expense base', drivers[14], '| SPV opex FY27', round(spv_opex27, 2))
