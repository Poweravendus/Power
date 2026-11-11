"""Build the PGInvIT model workbook."""
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
drivers = {14: round(nonim26 - spv_opex27, 3), 21: 0.055, 24: f'=(G23-AK91)/AVERAGE(F85,G85)', 27: f'=G28/AVERAGE(F76,G76)', 228: '=G102'}
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

# ---------------- visual conventions on every sheet ----------------
import formatter as F
from core import A_ITEMS, a_row, A_START, A_BLOCK
from rest import ccol as _cc
F.fmt_consolidated(W['Consolidated'], 3, CI(_cc(2026)), CI(_cc(2027)), CI(_cc(FYN)), 252,
                   growth_rows=[7, 18, 19, 41, 53, 54, 57], header_rows=[2, 3, 62, 117, 181, 187, 212, 249])
for ref in [f'{_cc(fy)}{r}' for fy in range(2022, FYN + 1) for r in (115, 208)] + ['G246']:
    F.fill(W['Consolidated'][ref], F.YEL)
if os.path.exists(qpath):
    F.fmt_qtrly(W['Qtrly'], 2 + len(json.load(open(qpath))['quarters']))
F.fmt_sensitivity(W['Sensitivity_Bajaj'], SEN, 3, CI(scol(2026)), CI(scol(FYN)), len(SPVS),
                  exit_last_col=4 + 20, mat_last_col=3 + (FYN - 2026) * 4 - 1)
F.fmt_assetlevel(W['AssetLevelEst'], [A_START + A_BLOCK * i for i in range(len(SPVS))], 4, CI(acol(FYN)), CI('AH'))
item_rows, total_rows = [], []
for it in A_ITEMS:
    item_rows += [a_row(it, i) for i in range(len(SPVS))]
    if W['Assumption'].cell(a_row(it), 3).value:
        total_rows.append(a_row(it))
F.fmt_assumption(W['Assumption'], item_rows, total_rows, 4, CI(acol(FYN)), [CI('AH'), CI('AI'), CI('AJ'), CI('AK'), CI('AL'), CI('AM')])
F.fmt_cashflows(W['Cashflows_Bajaj'], 3 + FYN - 2027, 25)
F.fmt_irr(W['IRR Calculation_Bajaj'], 3 + FYN - 2027)

# collapse long empty bands in Consolidated (keep one spacer row)
wc = W['Consolidated']
empty = [r for r in range(4, 253) if all(wc.cell(r, k).value is None for k in range(2, CI(_cc(FYN)) + 1))]
for r in empty:
    if r - 1 in empty and r + 1 in empty or (r - 1 in empty and r - 2 in empty):
        wc.row_dimensions[r].hidden = True
# widths so dates / large numbers never show ###
for k in range(3, CI(_cc(FYN)) + 1):
    wc.column_dimensions[L(k)].width = 9
wi = W['IRR Calculation_Bajaj']
wi.column_dimensions['A'].width = 46
for k in range(2, 3 + FYN - 2027 + 1):
    wi.column_dimensions[L(k)].width = 11
wsn = W['Sensitivity_Bajaj']
for k in range(3, 3 + (FYN - 2026) * 4 + 2):
    wsn.column_dimensions[L(k)].width = 9.5
wk = W['Key Sheet New']
wq = W['Qtrly']
for k in range(3, 3 + 21):
    wq.column_dimensions[L(k)].width = 9
wq.column_dimensions['B'].width = 52
# ---------------- no-fill spacer rows between sections ----------------
F.unfill_spacers(W['Consolidated'], 2, CI(_cc(FYN)), {62, 117, 181, 187, 210, 212, 249}, 4, 252)
if os.path.exists(qpath):
    wq = W['Qtrly']; lastq = 2 + len(json.load(open(qpath))['quarters'])
    starts = {r for r in range(1, wq.max_row + 1) if wq.cell(r, 2).value in
              ('Standalone (Trust)', 'Consolidated', 'Quarterly NDCF Build-up', 'Distribution per unit and components', 'Notes')}
    F.unfill_spacers(wq, 2, lastq, starts, 2, wq.max_row)
# ---------------- number formats, row by row ----------------
F.nf_assetlevel(W['AssetLevelEst'], [A_START + A_BLOCK * i for i in range(len(SPVS))], 4, CI(acol(FYN)), CI('AH'))
F.nf_sensitivity(W['Sensitivity_Bajaj'], SEN, CI(scol(2026)), CI(scol(FYN)), len(SPVS), 4 + 20, 3 + (FYN - 2026) * 4 - 1)
F.nf_consolidated(W['Consolidated'], 3, CI(_cc(FYN)), 252)
pct_rows = [a_row(it, i) for it in ('EBITDA Margin %', 'WACC, %') for i in range(len(SPVS))] + [a_row('EBITDA Margin %')]
per_rows = [a_row('Discount period', i) for i in range(len(SPVS))]
F.nf_assumption(W['Assumption'], pct_rows, per_rows, 4, CI(acol(FYN)), [CI('AI'), CI('AJ'), CI('AK'), CI('AM')])
if os.path.exists(qpath):
    F.nf_qtrly(W['Qtrly'], 2 + len(json.load(open(qpath))['quarters']))
F.nf_simple(W['Cashflows_Bajaj'], 4, 25, 3, 3 + FYN - 2027, F.N0B)
F.nf_simple(W['IRR Calculation_Bajaj'], 5, 9, 2, 3 + FYN - 2027, F.N0B)
F.nf_simple(W['IRR Calculation_Bajaj'], 11, 11, 2, 2, '0.0%', pct_rows=(11,))
F.nf_simple(W['IRR Calculation_Bajaj'], 15, 15, 3, 3 + FYN - 2027, '0.0%', pct_rows=(15,))
W['IRR Calculation_Bajaj']['B2'].number_format = 'General'
for n in names:
    finish_sheet(W[n])
wb.save(OUT)
print('saved', OUT, '| trust-level expense base', drivers[14], '| SPV opex FY27', round(spv_opex27, 2))
