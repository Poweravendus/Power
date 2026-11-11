"""Pull report figures from the recalculated PGInvIT model."""
import sys, json, openpyxl
MB = '/tmp/claude-0/-home-user-Power/562dd684-59fa-5b19-94f2-822ecbb92d34/scratchpad/build'
sys.path.insert(0, MB)
from core import SPVS, A_START, A_BLOCK, a_row, acol, scol, SEN
from rest import ccol
wb = openpyxl.load_workbook(f'{MB}/out/PGInvIT_Model.xlsx', data_only=True)
A, L, C, S, I = wb['Assumption'], wb['AssetLevelEst'], wb['Consolidated'], wb['Sensitivity_Bajaj'], wb['IRR Calculation_Bajaj']
out = {'spv': {}, 'cons': {}, 'proj': {}}
for i, s in enumerate(SPVS):
    r0 = A_START + A_BLOCK * i
    out['spv'][s] = dict(ev=L[f'E{r0 + 18}'].value, ev_model=L[f'D{r0 + 18}'].value,
                         ebitda27=A[f'{acol(2027)}{a_row("EBITDA", i)}'].value,
                         rev27=A[f'{acol(2027)}{a_row("Revenue", i)}'].value,
                         tariff27=S[f'{scol(2027)}{SEN["tariff"] + i}'].value,
                         rev_path={fy: A[f'{acol(fy)}{a_row("Revenue", i)}'].value for fy in range(2027, 2055)})
for fy in range(2022, 2055):
    c = ccol(fy)
    out['cons'][fy] = {k: C[f'{c}{r}'].value for k, r in dict(rev=6, ebitda=17, pat=43, dpu=58, dist=59, units=56, debt=76, cash=102,
                                                              aum=241, netdebt=242, nav=244, ndcf=226, capex=216, debtflow=225,
                                                              cash_avail=229, dpu_g=57, prop=237, netcash=238, actual=239, tax=40,
                                                              fin=28, oi=22, im=9).items()}
out['irr'] = I['B11'].value
out['price'] = S['C2'].value
json.dump(out, open('modeldata.json', 'w'), indent=1, default=str)
tot_ev = sum(v['ev'] for v in out['spv'].values())
print('EV total', round(tot_ev, 1), '| cons EBITDA FY27', round(out['cons'][2027]['ebitda'], 1), '| SPV EBITDA sum', round(sum(v['ebitda27'] for v in out['spv'].values()), 1))
for s, v in out['spv'].items():
    print(s, 'EV', round(v['ev'], 1), f"{v['ev'] / tot_ev:.1%}", 'EBITDA27', round(v['ebitda27'], 1), f"{v['ebitda27'] / out['cons'][2027]['ebitda']:.1%}", 'tariff27', round(v['tariff27'], 1), 'rev27', round(v['rev27'], 1))
for fy in range(2027, 2032):
    c = out['cons'][fy]
    print(fy, {k: round(c[k], 2) if isinstance(c[k], (int, float)) else c[k] for k in ('ndcf', 'capex', 'debtflow', 'cash_avail', 'dpu', 'dpu_g', 'actual', 'netcash')})
print('IRR', out['irr'], 'price', out['price'])
