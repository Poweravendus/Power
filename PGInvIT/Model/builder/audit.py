"""Independent audit of the recalculated PGInvIT model against source data."""
import json, sys, datetime as dt, openpyxl
sys.path.insert(0, '.')
from core import SPVS, A_START, A_BLOCK, a_row, acol, scol, SEN, valuer_data, RTM_PV, VAL_T, EV_MAR26
from rest import ccol
SP = '/tmp/claude-0/-home-user-Power/562dd684-59fa-5b19-94f2-822ecbb92d34/scratchpad'
wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
wf = openpyxl.load_workbook(sys.argv[1])
V = valuer_data(json.load(open(f'{SP}/build/vr27.json')))
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
chk('SPV FCFF = valuer FCFF (all SPVs, all years; FY27 annualised)', mx_fcff < 0.002, f'max diff {mx_fcff:.4f} cr')
mx_pv = max(abs(L[f'{acol(2027)}{A_START + A_BLOCK * i + 14}'].value - V[s]['rows'][2027]['fcff_val'] / (1 + V[s]['wacc']) ** V[s]['rows'][2027]['per']) for i, s in enumerate(SPVS))
chk('FY27 PV uses only the post-valuation-date cash flow (H2 FY27)', mx_pv < 0.01, f'max diff {mx_pv:.4f} cr')

# 2. EV per SPV vs valuer
for i, s in enumerate(SPVS):
    r0 = A_START + A_BLOCK * i
    d, e = L[f'D{r0 + 18}'].value, L[f'E{r0 + 18}'].value
    chk(f'{s} EV within 0.5% of valuer', abs(d / e - 1) < 0.005, f'{d:,.1f} vs {e:,.1f}')


# 2b. Sep-26 valuation report reconciliation (IndiaAppraisers): PV of explicit period, PV of TV, RTM, WACC, tax inputs, SPV loans
VR = json.load(open(f'{SP}/build/vr27.json'))
from core import SPV_LOAN_SEP26, VR_NAME
As = wb['Assumption']
for name, b in VR.items():
    s = VR_NAME[name.split()[0]]; i = SPVS.index(s); r0 = A_START + A_BLOCK * i
    pv_e, pv_t = L[f'D{r0 + 15}'].value, L[f'D{r0 + 16}'].value
    chk(f'{s} PV explicit / PV TV / WACC = valuer', abs(pv_e - b['pv_explicit'] / 10) < 0.05 and abs(pv_t - b['pv_tv'] / 10) < 0.05 and abs(L[f'D{r0 + 19}'].value - 0.0736) < 1e-9,
        f"{pv_e:,.1f}/{b['pv_explicit'] / 10:,.1f}  {pv_t:,.1f}/{b['pv_tv'] / 10:,.1f}")
    lr = a_row('Loan from PGInvIT (closing)', i)
    chk(f'{s} tax rate 28.60% and Sep-26 loan balance = valuer', abs(As[f'AK{lr}'].value - 0.286) < 1e-9 and abs(As[f'AN{lr}'].value - SPV_LOAN_SEP26[s]) < 1e-6)
chk('RTM project values = valuer (KATL Rs 26.9 cr, PPTL Rs 12.6 cr)', abs(RTM_PV['KATL'] - (VR['Kala Amb Transmission Limited']['rtm_pv_explicit'] + VR['Kala Amb Transmission Limited']['rtm_pv_tv'] + VR['Kala Amb Transmission Limited']['rtm_borrowings']) / 10) < 0.01
    and abs(RTM_PV['PPTL'] - (VR['Parli Power Transmission Limited']['rtm_pv_explicit'] + VR['Parli Power Transmission Limited']['rtm_pv_tv'] + VR['Parli Power Transmission Limited']['rtm_borrowings']) / 10) < 0.01)
# 3. Independent AUM roll-forward (excludes the year's own cash flow)
def aum(s, t):
    v = V[s]; w = v['wacc']; k = t - VAL_T
    pv = sum(r['fcff'] / (1 + w) ** (r['per'] - k) for fy, r in v['rows'].items() if fy > t)
    tv = v['tv_fcff'] / w
    pv += tv / (1 + w) ** (v['tv_per'] - k) if v['last_fy'] > t else tv
    end = {'KATL': 2049, 'PPTL': 2051}.get(s, 2027)
    pv += RTM_PV.get(s, 0) * max(0, min(1, (end - t) / (end - VAL_T)))
    return pv
chk('FY26 AUM = valuer EV at 31-Mar-26 (Rs 8,672 cr)', abs(A[f'{acol(2026)}{a_row("AUM (Rs. cr)")}'].value - sum(EV_MAR26.values())) < 0.01)
ev_d = sum(L[f'D{A_START + A_BLOCK * i + 18}'].value for i in range(5)); ev_v = sum(V[s]['ev'] for s in SPVS)
chk('Derived EV at 30-Sep-26 = valuer EV (Rs 8,732 cr) within 0.1%', abs(ev_d / ev_v - 1) < 0.001, f'{ev_d:,.1f} vs {ev_v:,.1f}')
for t in (2027, 2030, 2040, 2054):
    mine = sum(aum(s, t) for s in SPVS)
    model = A[f'{acol(t)}{a_row("AUM (Rs. cr)")}'].value
    chk(f'AUM FY{t % 100} independent recompute', abs(mine - model) < 0.5, f'{mine:,.1f} vs model {model:,.1f}')

# 4. Consolidated identities, all forecast years
yrs = range(2027, 2055)
cv = lambda r, fy: C[f'{ccol(fy)}{r}'].value or 0
chk('Revenue = sum of SPV revenue', all(abs(cv(6, fy) - A[f'{acol(fy)}{a_row("Revenue")}'].value) < 0.01 for fy in yrs))
chk('Balance sheet balances FY22-FY54', all(abs(cv(128, fy)) < 0.01 for fy in range(2022, 2055)))
chk('BS detail: unitholders funds, DTL, net block, cash, current liabilities re-add (FY22-FY54)', all(
    abs(sum(cv(r, fy) for r in range(64, 68)) - cv(68, fy)) < 0.01 and abs(sum(cv(r, fy) for r in range(80, 83)) - cv(83, fy)) < 0.01
    and abs(cv(90, fy) - cv(91, fy) - cv(92, fy) - cv(93, fy)) < 0.01 and abs(sum(cv(r, fy) for r in range(109, 112)) - cv(112, fy)) < 0.01
    and abs(sum(cv(r, fy) for r in range(117, 123)) - cv(123, fy)) < 0.01 for fy in range(2022, 2055)))
for fy_ in ('FY22', 'FY23', 'FY24', 'FY25', 'FY26'):
    y_ = 2000 + int(fy_[2:]); Bs = H['bs']
    chk(f'{fy_} BS lines = annual report (equity, DTL, net block, intangibles, cash, CA, CL)',
        abs(cv(68, y_) - Bs['unitholders_equity'][fy_]) < 0.02 and abs(cv(83, y_) - Bs['deferred_tax_liability_net'][fy_]) < 0.02
        and abs(cv(93, y_) - Bs['net_block_ppe'][fy_]) < 0.02 and abs(cv(98, y_) - Bs['intangibles'][fy_]) < 0.02
        and abs(cv(115, y_) - Bs['total_current_assets'][fy_]) < 0.02
        and abs(cv(123, y_) + Bs['current_maturities'][fy_] - Bs['total_current_liabilities'][fy_]) < 0.02
        and abs(cv(105, y_) + cv(93, y_) + cv(94, y_) - Bs['total_non_current_assets'][fy_]) < 0.02,
        f"eq {cv(68, y_):,.1f}/{Bs['unitholders_equity'][fy_]:,.1f} CA {cv(115, y_):,.1f}/{Bs['total_current_assets'][fy_]:,.1f}")
chk('Abridged CF ties to CF statement FY22-FY54', all(abs(cv(221, fy)) < 0.01 for fy in range(2022, 2055)))
chk('Closing cash (CF) = balance sheet cash', all(abs(cv(192, fy) - cv(112, fy)) < 0.01 for fy in yrs))
chk('Cash never negative', all(cv(112, fy) >= -0.01 for fy in yrs), f'min {min(cv(112, fy) for fy in yrs):,.1f}')
chk('Debt nil from FY52 and never negative', all(cv(78, fy) < 0.01 for fy in range(2052, 2055)) and all(cv(78, fy) >= -0.01 for fy in yrs))
chk('No interest once debt is repaid', all(cv(28, fy) < 0.01 for fy in range(2053, 2055)))
chk('Net block and intangibles never negative', all(cv(93, fy) >= -0.01 and cv(98, fy) >= -0.01 for fy in yrs))
allyrs = range(2022, 2055)
chk('NDCF (PGInvIT) = sum of waterfall lines (FY22-FY54)', all(abs(sum(cv(r, fy) for r in range(233, 241)) - cv(241, fy)) < 0.01 for fy in allyrs))
chk('SPVs NDCF = sum of five SPVs (FY22-FY54)', all(abs(sum(cv(r, fy) for r in range(226, 231)) - cv(231, fy)) < 0.01 for fy in allyrs))
chk('Forecast: interest + dividend + repayment of capital = SPVs NDCF', all(abs(sum(cv(r, fy) for r in (234, 235, 236)) - cv(231, fy)) < 0.01 for fy in yrs))
chk('Forecast dividend never negative', all(cv(235, fy) >= -0.01 for fy in yrs), f'min {min(cv(235, fy) for fy in yrs):,.1f}')
chk('Historical NDCF (PGInvIT) = reported NDCF (FY22-FY26)', all(abs(cv(242, fy)) < 0.05 for fy in range(2022, 2027)), str([round(cv(242, fy), 3) for fy in range(2022, 2027)]))
chk('Historical NDCF (PGInvIT) = annual report NDCF', all(abs(cv(241, 2000 + int(k[2:])) - v) < 0.05 for k, v in H['ndcf']['ndcf_trust_level'].items()))
ppt = {231: 1212.6, 233: -15.3, 234: 669.0, 235: 269.1, 236: 251.9, 237: 6.6, 238: -74.1, 239: -8.3, 240: -8.3, 241: 1090.6}
chk('FY26 waterfall = investor presentation (Rs cr, +/-0.15)', all(abs(cv(r, 2026) - v) < 0.15 for r, v in ppt.items()), str({r: round(cv(r, 2026), 1) for r in ppt}))
chk('Waterfall NDCF = distribution-section NDCF (forecast)', all(abs(cv(241, fy) - cv(251, fy)) < 0.01 for fy in yrs))
q = wb['Qtrly']
qchk = [r for r in range(1, q.max_row + 1) if q.cell(r, 2).value == 'Check']
chk('Qtrly NDCF ties to reported every quarter', qchk and all(abs(q.cell(qchk[0], k).value or 0) < 0.05 for k in range(3, 3 + len(json.load(open(f'{SP}/agentB/quarterly_history.json'))['quarters']))))
chk('NDCF = NDCF before capex + capex + net debt', all(abs(cv(248, fy) + cv(249, fy) + cv(250, fy) - cv(251, fy)) < 0.01 for fy in yrs))
chk('Distribution >= 90% of NDCF (SEBI)', all(cv(259, fy) >= 0.9 * cv(251, fy) - 0.01 for fy in yrs))
chk('Distribution never exceeds opening cash + cash available', all(cv(259, fy) <= cv(191, fy) + cv(253, fy) + 0.01 for fy in yrs))
chk('Proposed = min(100% NDCF, DPU x units) from FY28', all(abs(cv(257, fy) - max(0, min(cv(251, fy), cv(256, fy) * cv(56, fy)))) < 0.01 for fy in range(2028, 2055)))
chk('DPU x units = distribution', all(abs(cv(58, fy) * cv(56, fy) - cv(59, fy)) < 0.01 for fy in yrs))
chk('FY27 DPU = Rs 12.00', abs(cv(58, 2027) - 12) < 1e-6)
chk('NAV = AUM - net debt', all(abs(cv(262, fy) - cv(263, fy) - cv(264, fy)) < 0.01 for fy in yrs))
chk('FY26 NAV within Rs 0.05 of reported 90.79', abs(cv(265, 2026) - 90.79) < 0.05, f'{cv(265, 2026):.2f}')
cf = wb['Cashflows_Bajaj']
chk('Cashflows_Bajaj NDCF = Consolidated NDCF', all(abs(cf.cell(25, 3 + k).value or 0) < 0.01 for k in range(28)))
chk('Tax in NDCF = consolidated tax', all(abs(A[f'{acol(fy)}{a_row("EBITDA")}'].value - sum(cv(r, fy) for r in range(226, 231)) + C['AK233'].value - cv(40, fy)) < 0.01 for fy in yrs))

# 5. History in Consolidated = audited figures
P, B = H['pnl'], H['bs']
for fy in ('FY22', 'FY24', 'FY26'):
    y = 2000 + int(fy[2:])
    chk(f'{fy} revenue / PAT / net assets match audited', abs(cv(6, y) - P['revenue_from_operations'][fy]) < 0.01 and abs(cv(43, y) - P['profit_after_tax'][fy]) < 0.2
        and abs(cv(127, y) - (B['total_assets'][fy] - (B['total_current_liabilities'][fy] - (B['current_maturities'][fy] or 0)))) < 0.5, f'rev {cv(6, y):,.1f} PAT {cv(43, y):,.1f} TA {cv(127, y):,.1f}')

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
    for rr in range(4, 273):
        c = wf['Consolidated'][f'{ccol(fy)}{rr}']
        if isinstance(c.value, (int, float)) and c.value != 0 and rr != 255:
            hard.append(c.coordinate)
chk('No non-zero hard-codes in Consolidated forecast', not hard, ', '.join(hard[:10]))
print('\nFAILED:', fails if fails else 'none')
