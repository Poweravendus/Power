"""Independent audit of the recalculated PGInvIT model against source data."""
import json, sys, datetime as dt, openpyxl
sys.path.insert(0, '.')
from core import SPVS, A_START, A_BLOCK, a_row, acol, scol, SEN, valuer_data, RTM_PV
from rest import ccol
SP = '/tmp/claude-0/-home-user-Power/562dd684-59fa-5b19-94f2-822ecbb92d34/scratchpad'
wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
wf = openpyxl.load_workbook(sys.argv[1])
V = valuer_data(json.load(open(f'{SP}/build/vr26.json')))
A, L, C, S = wb['Assumption'], wb['AssetLevelEst'], wb['Consolidated'], wb['Sensitivity_Bajaj']
H = json.load(open(f'{SP}/agentA/consolidated_history.json'))
fails = []
def chk(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + (f'  [{detail}]' if detail else ''))
    if not ok: fails.append(name)

# 1. SPV revenue and FCFF equal the valuer's projections every year
mx_rev = mx_fcff = 0
for i, s in enumerate(SPVS):
    r0 = A_START + A_BLOCK * i
    for fy, row in V[s]['rows'].items():
        mx_rev = max(mx_rev, abs(L[f'{acol(fy)}{r0 + 1}'].value - row['rev']))
        mx_fcff = max(mx_fcff, abs(L[f'{acol(fy)}{r0 + 9}'].value - row['fcff']))
chk('SPV revenue = valuer revenue (all SPVs, all years)', mx_rev < 0.01, f'max diff {mx_rev:.4f} cr')
chk('SPV FCFF = valuer FCFF (all SPVs, all years)', mx_fcff < 0.002, f'max diff {mx_fcff:.4f} cr')

# 2. EV per SPV vs valuer
for i, s in enumerate(SPVS):
    r0 = A_START + A_BLOCK * i
    d, e = L[f'D{r0 + 18}'].value, L[f'E{r0 + 18}'].value
    chk(f'{s} EV within 0.5% of valuer', abs(d / e - 1) < 0.005, f'{d:,.1f} vs {e:,.1f}')

# 3. Independent AUM roll-forward (excludes the year's own cash flow)
def aum(s, t):
    v = V[s]; w = 0.08; k = t - 2026
    pv = sum(r['fcff'] / (1 + w) ** (r['per'] - k) for fy, r in v['rows'].items() if fy > t)
    tv = v['tv_fcff'] / w
    pv += tv / (1 + w) ** (v['tv_per'] - k) if v['last_fy'] > t else tv
    end = {'KATL': 2049, 'PPTL': 2051}.get(s, 2027)
    pv += RTM_PV.get(s, 0) * max(0, min(1, (end - t) / (end - 2026)))
    return pv
for t in (2026, 2027, 2030, 2040, 2054):
    mine = sum(aum(s, t) for s in SPVS)
    model = A[f'{acol(t)}{a_row("AUM (Rs. cr)")}'].value
    chk(f'AUM FY{t % 100} independent recompute', abs(mine - model) < 0.5, f'{mine:,.1f} vs model {model:,.1f}')

# 4. Consolidated identities, all forecast years
yrs = range(2027, 2055)
cv = lambda r, fy: C[f'{ccol(fy)}{r}'].value or 0
chk('Revenue = sum of SPV revenue', all(abs(cv(6, fy) - A[f'{acol(fy)}{a_row("Revenue")}'].value) < 0.01 for fy in yrs))
chk('Balance sheet balances FY22-FY54', all(abs(cv(115, fy)) < 0.01 for fy in range(2022, 2055)))
chk('Abridged CF ties to CF statement FY22-FY54', all(abs(cv(208, fy)) < 0.01 for fy in range(2022, 2055)))
chk('Closing cash (CF) = balance sheet cash', all(abs(cv(179, fy) - cv(102, fy)) < 0.01 for fy in yrs))
chk('Cash never negative', all(cv(102, fy) >= -0.01 for fy in yrs), f'min {min(cv(102, fy) for fy in yrs):,.1f}')
chk('Debt nil from FY52 and never negative', all(cv(76, fy) < 0.01 for fy in range(2052, 2055)) and all(cv(76, fy) >= -0.01 for fy in yrs))
chk('No interest once debt is repaid', all(cv(28, fy) < 0.01 for fy in range(2053, 2055)))
chk('Net block and intangibles never negative', all(cv(87, fy) >= -0.01 and cv(91, fy) >= -0.01 for fy in yrs))
allyrs = range(2022, 2055)
chk('NDCF Generated = distributions received + Trust lines (FY22-FY54)', all(abs(cv(222, fy) + sum(cv(r, fy) for r in range(224, 232)) - cv(232, fy)) < 0.01 for fy in allyrs))
chk('NDCF at SPV = sum of five SPVs (FY22-FY54)', all(abs(sum(cv(r, fy) for r in range(213, 218)) - cv(218, fy)) < 0.01 for fy in allyrs))
chk('Historical NDCF Generated = reported NDCF (FY22-FY26)', all(abs(cv(233, fy)) < 0.05 for fy in range(2022, 2027)), str([round(cv(233, fy), 3) for fy in range(2022, 2027)]))
chk('Historical NDCF Generated = annual report NDCF', all(abs(cv(232, 2000 + int(k[2:])) - v) < 0.05 for k, v in H['ndcf']['ndcf_trust_level'].items()))
ppt = {218: 1212.6, 219: 669.0, 220: 269.1, 221: 251.9, 224: -15.3, 225: 6.6, 228: -74.1, 229: -8.3, 230: -8.3, 232: 1090.6}
chk('FY26 NDCF bridge = investor presentation (Rs cr, +/-0.15)', all(abs(cv(r, 2026) - v) < 0.15 for r, v in ppt.items()), str({r: round(cv(r, 2026), 1) for r in ppt}))
q = wb['Qtrly']
qchk = [r for r in range(1, q.max_row + 1) if q.cell(r, 2).value == 'Check']
chk('Qtrly NDCF ties to reported every quarter', qchk and all(abs(q.cell(qchk[0], k).value or 0) < 0.05 for k in range(3, 24)))
chk('NDCF = NDCF before capex + capex + net debt', all(abs(cv(235, fy) + cv(236, fy) + cv(237, fy) - cv(238, fy)) < 0.01 for fy in yrs))
chk('Distribution >= 90% of NDCF (SEBI)', all(cv(246, fy) >= 0.9 * cv(238, fy) - 0.01 for fy in yrs))
chk('Distribution never exceeds opening cash + cash available', all(cv(246, fy) <= cv(178, fy) + cv(240, fy) + 0.01 for fy in yrs))
chk('Proposed = min(90% NDCF, DPU x units) from FY28', all(abs(cv(244, fy) - max(0, min(0.9 * cv(238, fy), cv(243, fy) * cv(56, fy)))) < 0.01 for fy in range(2028, 2055)))
chk('DPU x units = distribution', all(abs(cv(58, fy) * cv(56, fy) - cv(59, fy)) < 0.01 for fy in yrs))
chk('FY27 DPU = Rs 12.00', abs(cv(58, 2027) - 12) < 1e-6)
chk('NAV = AUM - net debt', all(abs(cv(249, fy) - cv(250, fy) - cv(251, fy)) < 0.01 for fy in yrs))
chk('FY26 NAV within Rs 0.05 of reported 90.79', abs(cv(252, 2026) - 90.79) < 0.05, f'{cv(252, 2026):.2f}')
cf = wb['Cashflows_Bajaj']
chk('Cashflows_Bajaj NDCF = Consolidated NDCF', all(abs(cf.cell(25, 3 + k).value or 0) < 0.01 for k in range(28)))
chk('Tax in NDCF = consolidated tax', all(abs(A[f'{acol(fy)}{a_row("EBITDA")}'].value - sum(cv(r, fy) for r in range(213, 218)) - cv(227, fy) - cv(40, fy)) < 0.01 for fy in yrs))

# 5. History in Consolidated = audited figures
P, B = H['pnl'], H['bs']
for fy in ('FY22', 'FY24', 'FY26'):
    y = 2000 + int(fy[2:])
    chk(f'{fy} revenue / PAT / net assets match audited', abs(cv(6, y) - P['revenue_from_operations'][fy]) < 0.01 and abs(cv(43, y) - P['profit_after_tax'][fy]) < 0.2
        and abs(cv(114, y) - (B['total_assets'][fy] - (B['total_current_liabilities'][fy] - (B['current_maturities'][fy] or 0)))) < 0.5, f'rev {cv(6, y):,.1f} PAT {cv(43, y):,.1f} TA {cv(114, y):,.1f}')

# 6. Effective tariff history = reported SPV revenue
spv = json.load(open(f'{SP}/agentC/spv_history.json'))['spvs']
mx = max(abs((S[f'{scol(2000 + int(k[2:]))}{SEN["eff"] + i}'].value or 0) - v) for i, s in enumerate(SPVS) for k, v in spv[s]['revenue'].items() if v is not None and int(k[2:]) >= 21)
chk('Historical effective tariff = reported SPV revenue', mx < 0.01, f'max diff {mx:.4f}')

# 7. Investor returns recomputed independently
def xirr(cfs, ds):
    d0 = ds[0]; f = lambda x: sum(c / (1 + x) ** ((d - d0).days / 365) for c, d in zip(cfs, ds))
    lo, hi = -0.9, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if f(m) > 0 else (lo, m)
    return m
irr = wb['IRR Calculation_Bajaj']
row = [irr.cell(9, k).value for k in range(2, 31)]
import numpy as np
def irr_(v):
    lo, hi = -0.9, 1.0
    f = lambda x: sum(c / (1 + x) ** t for t, c in enumerate(v))
    for _ in range(200):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if f(m) > 0 else (lo, m)
    return m
chk('IRR Calculation_Bajaj recomputes', abs(irr_(row) - irr['B11'].value) < 1e-4, f'{irr_(row):.4%} vs {irr["B11"].value:.4%}')

# 8. No hard-coded numbers in Consolidated forecast columns except driver zeros
hard = []
for fy in yrs:
    for rr in range(4, 260):
        c = wf['Consolidated'][f'{ccol(fy)}{rr}']
        if isinstance(c.value, (int, float)) and c.value != 0 and rr != 242:
            hard.append(c.coordinate)
chk('No non-zero hard-codes in Consolidated forecast', not hard, ', '.join(hard[:10]))
print('\nFAILED:', fails if fails else 'none')
