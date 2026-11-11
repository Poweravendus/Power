"""Forward-looking core: Sensitivity_Bajaj (drivers), AssetLevelEst (SPV DCFs), Assumption (aggregation + AUM)."""
import datetime as dt
import re
from common import *

SPVS = ['VTL', 'KATL', 'PPTL', 'WTL', 'JPTL']
VR_NAME = {'Vizag': 'VTL', 'Kala': 'KATL', 'Parli': 'PPTL', 'Warora': 'WTL', 'Jabalpur': 'JPTL'}
FY0, FYN = 2026, 2054            # asset-level / assumption horizon (FY26 actual, FY27-FY54 forecast)
S_FY0 = 2021                     # Sensitivity first column (C = FY21), so H = FY26 as in IndiGrid
# PV of RTM (regulated tariff) projects, valued by the valuer on FCFE at Ke 15.03% incl. RTM debt (Rs cr; report p.55 and p.66)
RTM_PV = {'KATL': 24.145, 'PPTL': 9.018}
MON = {m: i + 1 for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}

# ---- layout constants -------------------------------------------------------------------------
SEN = dict(price=2, xirr5=3, xirr_mat=4, xirr_mat_res=5, avail_hdr=7, avail=8, tariff_hdr=15, tariff=16,
           ladder=24, eff_hdr=31, eff=32, eff_tot=37, marg_hdr=40, marg=41, wc_hdr=48, wc=49,
           exit_hdr=55, mat_hdr=64, debt=74)
A_BLOCK = 27                     # rows per SPV block in AssetLevelEst
A_START = 3


def scol(fy):
    return L(3 + fy - S_FY0)


def acol(fy):
    return L(4 + fy - FY0)


def fy_of(datestr):
    d, m, y = datestr.split('-')
    m = int(m) if m.isdigit() else MON[m]
    y = int(y) if len(y) == 4 else 2000 + int(y)
    return y + 1 if m >= 4 else y, dt.date(y, m, int(d))


def valuer_data(vr):
    """Return {spv: {...}} with per-FY valuer projections in Rs crore."""
    out = {}
    for name, b in vr.items():
        spv = VR_NAME[name.split()[0]]
        rows = {}
        for r in b['rows']:
            fy, d = fy_of(r['date'])
            rows[fy] = dict(rev=r['revenue'] / 10, nopat=r['nopat'] / 10, dep=r['dep'] / 10, capex=-r['capex'] / 10,
                            wc=-r['dwc'] / 10, fcff=r['fcff'] / 10, per=r['yearfrac'], months=r['months'], date=d)
        tv = b['tv']
        out[spv] = dict(name=name, rows=rows, ev=b['ev'] / 10, pv_tv=b['pv_tv'] / 10,
                        rtm=RTM_PV.get(spv, 0.0),
                        tv_fcff=tv['fcff'] / 10, tv_per=tv['yearfrac'], last_fy=max(rows))
    return out


# =================================================================================================
def build_sensitivity(ws, V, hist, margins, price, entry_date):
    std_sheet(ws, colA=2.57, widths={'B': 44})
    lastc = scol(FYN)
    put(ws, 'B2', 'Entry price, Rs./ unit', bold=True)
    put(ws, 'C2', price, fmt=NUM2, bold=True, color=BLUE)
    put(ws, 'D2', '<<Punch In Entry Price (NSE close, 9-Nov-2026)', italic=True)
    put(ws, 'B3', 'XIRR  -  5-year holding period', bold=True)
    put(ws, 'B4', 'XIRR  -  hold to maturity (distributions only)', bold=True)
    put(ws, 'B5', 'XIRR  -  hold to maturity (incl. residual NAV at FY54)', bold=True)

    def year_header(r, title):
        put(ws, f'B{r - 1}', title, bold=True)
        put(ws, f'B{r}', 'Asset', bold=True, border_b=True)
        for fy in range(S_FY0, FYN + 1):
            put(ws, f'{scol(fy)}{r}', fy_label(fy, fy > 2026), bold=True, align='right', border_b=True)

    # --- availability
    year_header(SEN['avail_hdr'], 'TRANSMISSION  -  AVAILABILITY,  %')
    for i, s in enumerate(SPVS):
        r = SEN['avail'] + i
        put(ws, f'B{r}', s)
        for fy in range(S_FY0, FYN + 1):
            if fy <= 2026:
                v = hist.get('avail', {}).get(s, {}).get(f'FY{fy % 100:02d}')
                if v is not None:
                    put(ws, f'{scol(fy)}{r}', v, fmt=PCT2, color=RED)
            elif fy <= V[s]['last_fy']:
                put(ws, f'{scol(fy)}{r}', 0.9975, fmt=PCT2, color=BLUE)
    put(ws, f'B{SEN["avail"] + 5}', 'Forecast = 99.75% (valuer: management expects availability at or above 99.75%)', italic=True)

    # --- ladder assumptions
    r0 = SEN['ladder']
    put(ws, f'B{r0 - 2}', 'TSA PAYMENT LADDER  -  ASSUMPTIONS (TBCB TSA, as described in the valuation report)', bold=True)
    put(ws, f'B{r0 - 1}', 'Parameter', bold=True, border_b=True)
    put(ws, f'C{r0 - 1}', 'Value', bold=True, border_b=True, align='right')
    ladder = [('Target availability', 0.98, '98% target; payment pro-rata below target'),
              ('Incentive per 1%-pt above target, % of ATC', 0.02, 'Incentive = 0.02 x ATC x (Actual - Target), availability in %-pts'),
              ('Incentive cap (availability)', 0.9975, 'No incentive above 99.75%'),
              ('Penalty threshold', 0.95, 'Below 95%: pro-rata payment plus additional penalty'),
              ('Additional penalty per 1%-pt below threshold, % of ATC', 0.02, 'Assumed equal to incentive rate (check TSA)')]
    for k, (lab, v, note) in enumerate(ladder):
        put(ws, f'B{r0 + k}', lab)
        put(ws, f'C{r0 + k}', v, fmt=PCT2, color=BLUE)
        put(ws, f'E{r0 + k}', note, italic=True)
    T, INC, CAP, PEN, PADD = [f'$C${r0 + k}' for k in range(5)]
    cap_factor = 1 + 0.02 * (0.9975 - 0.98) * 100

    # --- tariff (annual transmission charges, before incentive / penalty)
    year_header(SEN['tariff_hdr'], 'TRANSMISSION  -  TARIFF (ANNUAL TRANSMISSION CHARGES, before incentive),  Rs. cr')
    for i, s in enumerate(SPVS):
        r = SEN['tariff'] + i
        put(ws, f'B{r}', s)
        for fy in range(S_FY0, FYN + 1):
            c = scol(fy)
            if fy <= 2026:
                rev = hist.get('rev', {}).get(s, {}).get(f'FY{fy % 100:02d}')
                if rev is not None:   # back out tariff so that effective tariff = reported revenue
                    a = f'{c}{SEN["avail"] + i}'
                    put(ws, f'{c}{r}', f'={rev}/IF({a}>={CAP},1+{INC}*({CAP}-{T})*100,IF({a}>={T},1+{INC}*({a}-{T})*100,IF({a}>={PEN},{a}/{T},{a}/{T}-{PADD}*({PEN}-{a})*100)))',
                        fmt=NUM1, color=RED)
            elif fy in V[s]['rows']:
                put(ws, f'{c}{r}', round(V[s]['rows'][fy]['rev'] / cap_factor, 4), fmt=NUM1, color=BLUE)
    put(ws, f'B{SEN["tariff"] + 5}', 'Forecast = valuer revenue / incentive factor at 99.75% (1.035x); history = reported revenue grossed down at actual availability', italic=True)

    # --- effective tariff
    year_header(SEN['eff_hdr'], 'TRANSMISSION  -  EFFECTIVE TARIFF (REVENUE),  Rs. cr')
    for i, s in enumerate(SPVS):
        r = SEN['eff'] + i
        put(ws, f'B{r}', s)
        for fy in range(S_FY0, FYN + 1):
            c = scol(fy)
            t, a = f'{c}{SEN["tariff"] + i}', f'{c}{SEN["avail"] + i}'
            put(ws, f'{c}{r}', f'=IF(N({t})=0,"",{t}*IF({a}>={CAP},1+{INC}*({CAP}-{T})*100,IF({a}>={T},1+{INC}*({a}-{T})*100,IF({a}>={PEN},{a}/{T},{a}/{T}-{PADD}*({PEN}-{a})*100))))', fmt=NUM1)
    r = SEN['eff_tot']
    put(ws, f'B{r}', 'Total', bold=True)
    for fy in range(S_FY0, FYN + 1):
        c = scol(fy)
        put(ws, f'{c}{r}', f'=SUM({c}{SEN["eff"]}:{c}{SEN["eff"] + 4})', fmt=NUM1, bold=True)

    # --- EBITDA margin
    year_header(SEN['marg_hdr'], 'TRANSMISSION  -  EBITDA MARGIN,  %  (SPV level)')
    for i, s in enumerate(SPVS):
        r = SEN['marg'] + i
        put(ws, f'B{r}', s)
        for fy in range(S_FY0, FYN + 1):
            c = scol(fy)
            if fy <= 2026:
                v = hist.get('margin', {}).get(s, {}).get(f'FY{fy % 100:02d}')
                if v is not None:
                    put(ws, f'{c}{r}', v, fmt=PCT, color=RED)
            elif fy in margins.get(s, {}):
                put(ws, f'{c}{r}', round(margins[s][fy], 4), fmt=PCT, color=BLUE)
    put(ws, f'B{SEN["marg"] + 5}', 'Forecast margins rebuilt from the valuer\'s SPV cost assumptions (O&M, PM fee, insurance, licence fee, KMP, SMOC, audit, admin, contingency, CSR)', italic=True)
    return dict(T=T, INC=INC, CAP=CAP, PEN=PEN, PADD=PADD)


# =================================================================================================
def build_assetlevel(ws, V, margins, hist):
    std_sheet(ws, colA=2.57, widths={'B': 4.57, 'C': 30, 'AH': 34, 'AI': 10})
    put(ws, 'C1', 'Source: Company / Valuation Report (INMACS Valuers, 31-Mar-2026); Rs. cr', italic=True)
    lastc = acol(FYN)
    info = {}
    for i, s in enumerate(SPVS):
        v = V[s]
        r0 = A_START + A_BLOCK * i
        R = lambda k: r0 + k
        put(ws, f'C{R(-1)}', 'Transmission', bold=True, color='FF00008B')
        put(ws, f'B{R(0)}', i + 1)
        put(ws, f'C{R(0)}', s, bold=True, border_b=True)
        for fy in range(FY0, FYN + 1):
            put(ws, f'{acol(fy)}{R(0)}', fy_label(fy), bold=True, align='right', border_b=True)
        labels = ['Revenue', 'Total Expenses', 'EBITDA', 'EBITDA Margin', 'Capex', 'Changes in WC', 'Taxation',
                  'Other adjustments', 'FCFF', 'TV', 'FCFF with TV', 'Discount period (yrs, mid-year)', 'Present value factor',
                  'PV of Cash Flows', 'PV of Cash Flows', 'PV of TV Cash Flows', 'RTM project value (valuer)', 'Enterprise Value', 'WACC',
                  'Memo: Valuer FCFF', 'Check: model FCFF - valuer FCFF', 'Memo: Valuer NOPAT', 'Memo: Valuer book depreciation']
        for k, lab in enumerate(labels, start=1):
            put(ws, f'B{R(k)}', s)
            put(ws, f'C{R(k)}', lab, bold=lab in ('FCFF', 'Enterprise Value'))
        # memo block (AH/AI) -------------------------------------------------------------------
        memo = ['WACC (nominal, post-tax)', 'Terminal growth rate (g) - input', 'Terminal-year FCFF (valuer)',
                'TV discounting period (yrs)', 'Terminal value, undiscounted (TV)', 'TV year (FY)', 'PV of terminal value',
                'PV of explicit period', 'RTM project value (valuer)', 'Enterprise Value (derived)', 'EV per valuer',
                'Variance (derived vs valuer)', 'Memo: TV as % of EV', 'Memo: EV / first-yr EBITDA', 'Memo: first-yr FCFF yield on EV']
        m = {lab: R(k + 1) for k, lab in enumerate(memo)}
        for lab, rr in m.items():
            put(ws, f'AH{rr}', lab)
        put(ws, f'AI{m["WACC (nominal, post-tax)"]}', f'=D{R(19)}', fmt=PCT2, color=GREEN)
        put(ws, f'AI{m["Terminal growth rate (g) - input"]}', 0.0, fmt=PCT2, color=BLUE)
        put(ws, f'AI{m["Terminal-year FCFF (valuer)"]}', round(v['tv_fcff'], 4), fmt=NUM1, color=BLUE)
        put(ws, f'AI{m["TV discounting period (yrs)"]}', v['tv_per'], fmt=NUM2, color=BLUE)
        W, G = f'$AI${m["WACC (nominal, post-tax)"]}', f'$AI${m["Terminal growth rate (g) - input"]}'
        put(ws, f'AI{m["Terminal value, undiscounted (TV)"]}', f'=AI{m["Terminal-year FCFF (valuer)"]}*(1+{G})/({W}-{G})', fmt=NUM1)
        put(ws, f'AI{m["TV year (FY)"]}', v['last_fy'], fmt='0', color=BLUE)
        put(ws, f'AI{m["PV of terminal value"]}', f'=D{R(16)}', fmt=NUM1)
        put(ws, f'AI{m["PV of explicit period"]}', f'=D{R(15)}', fmt=NUM1)
        put(ws, f'AI{m["RTM project value (valuer)"]}', f'=D{R(17)}', fmt=NUM1)
        put(ws, f'AI{m["Enterprise Value (derived)"]}', f'=D{R(18)}', fmt=NUM1)
        put(ws, f'AI{m["EV per valuer"]}', f'=E{R(18)}', fmt=NUM1)
        put(ws, f'AI{m["Variance (derived vs valuer)"]}', f'=AI{m["Enterprise Value (derived)"]}-AI{m["EV per valuer"]}', fmt=NUM2)
        put(ws, f'AI{m["Memo: TV as % of EV"]}', f'=IF(D{R(18)}=0,0,D{R(16)}/D{R(18)})', fmt=PCT)
        put(ws, f'AI{m["Memo: EV / first-yr EBITDA"]}', f'=IF(E{R(3)}=0,0,D{R(18)}/E{R(3)})', fmt='0.0x')
        put(ws, f'AI{m["Memo: first-yr FCFF yield on EV"]}', f'=IF(D{R(18)}=0,0,E{R(9)}/D{R(18)})', fmt=PCT)

        sr_eff, sr_mar = SEN['eff'] + i, SEN['marg'] + i
        for fy in range(FY0, FYN + 1):
            c = acol(fy)
            sc = scol(fy)
            row = v['rows'].get(fy)
            put(ws, f'{c}{R(1)}', f'=N(Sensitivity_Bajaj!{sc}{sr_eff})', fmt=NUM1)
            put(ws, f'{c}{R(4)}', f'=IF(N(Sensitivity_Bajaj!{sc}{sr_mar})=0,"",Sensitivity_Bajaj!{sc}{sr_mar})', fmt=PCT)
            if fy == FY0:
                put(ws, f'{c}{R(2)}', f'=IF(N({c}{R(4)})=0,"",{c}{R(1)}*(1-{c}{R(4)}))', fmt=NUM1)
            elif row:
                put(ws, f'{c}{R(2)}', f'=({round(row["rev"], 4)})*(1-N({c}{R(4)}))', fmt=NUM1)
            else:
                put(ws, f'{c}{R(2)}', 0, fmt=NUM1)
            put(ws, f'{c}{R(3)}', f'=IF({c}{R(2)}="","",{c}{R(1)}-{c}{R(2)})', fmt=NUM1)
            if row:
                ebitda_base = row['rev'] * margins[s][fy]
                tax = ebitda_base - row['nopat'] - row['dep']
                put(ws, f'{c}{R(5)}', round(row['capex'], 4), fmt=NUM1, color=BLUE)
                put(ws, f'{c}{R(6)}', round(row['wc'], 4), fmt=NUM1, color=BLUE)
                put(ws, f'{c}{R(7)}', round(tax, 4), fmt=NUM1, color=BLUE)
                put(ws, f'{c}{R(12)}', row['per'], fmt=NUM2, color=BLUE)
                put(ws, f'{c}{R(20)}', round(row['fcff'], 4), fmt=NUM1, color=BLUE)
                put(ws, f'{c}{R(22)}', round(row['nopat'], 4), fmt=NUM1, color=BLUE)
                put(ws, f'{c}{R(23)}', round(row['dep'], 4), fmt=NUM1, color=BLUE)
            elif fy > FY0:
                for k in (5, 6, 7):
                    put(ws, f'{c}{R(k)}', 0, fmt=NUM1)
                put(ws, f'{c}{R(12)}', 0, fmt=NUM2)
            put(ws, f'{c}{R(8)}', 0, fmt=NUM1)
            if fy == FY0:
                continue          # FY26 is the valuation base year: actuals only, not discounted
            put(ws, f'{c}{R(9)}', f'={c}{R(3)}-{c}{R(5)}-{c}{R(6)}-{c}{R(7)}-{c}{R(8)}', fmt=NUM1, bold=True)
            if fy == v['last_fy']:
                put(ws, f'{c}{R(10)}', f'=$AI${m["Terminal value, undiscounted (TV)"]}', fmt=NUM1)
            else:
                put(ws, f'{c}{R(10)}', 0, fmt=NUM1)
            put(ws, f'{c}{R(11)}', f'={c}{R(9)}+{c}{R(10)}', fmt=NUM1)
            put(ws, f'{c}{R(13)}', f'=IF({c}{R(12)}=0,0,1/(1+$D${R(19)})^{c}{R(12)})', fmt='0.0000')
            put(ws, f'{c}{R(14)}', f'={c}{R(9)}*{c}{R(13)}', fmt=NUM1)
            if row:
                put(ws, f'{c}{R(21)}', f'={c}{R(9)}-{c}{R(20)}', fmt=NUM2)
        E, F = acol(FY0 + 1), lastc
        put(ws, f'D{R(15)}', f'=SUM({E}{R(14)}:{F}{R(14)})', fmt=NUM1)
        put(ws, f'D{R(16)}', f'=SUMPRODUCT({E}{R(10)}:{F}{R(10)},{E}{R(13)}:{F}{R(13)})', fmt=NUM1)
        put(ws, f'D{R(17)}', round(v['rtm'], 4), fmt=NUM1, color=BLUE)
        put(ws, f'D{R(18)}', f'=D{R(15)}+D{R(16)}+D{R(17)}', fmt=NUM1, bold=True)
        put(ws, f'E{R(18)}', round(v['ev'], 3), fmt=NUM1, color=BLUE)
        put(ws, f'F{R(18)}', f'=D{R(18)}/E{R(18)}-1', fmt=PCT2)
        put(ws, f'G{R(18)}', '<< EV per valuer and variance', italic=True)
        put(ws, f'D{R(19)}', 0.08, fmt=PCT2, color=BLUE)
        info[s] = dict(r0=r0, memo=m)
    return info


# =================================================================================================
A_ITEMS = ['Revenue', 'Total Expenses', 'EBITDA', 'EBITDA Margin %', 'Capex', 'Changes in WC', 'Taxation',
           'FCFF', 'TV', 'FCFF with TV', 'Discount period', 'WACC, %', 'AUM (Rs. cr)',
           'Loan from PGInvIT (closing)', 'Interest on loan from PGInvIT', 'Taxation (levered, used for NDCF)']
# SPV loans from the Trust at 31-Mar-26 and FY26 net repayment (Rs cr; eliminated on consolidation, 14.5% p.a.)
SPV_LOAN = {'VTL': (738.688, 29.80), 'KATL': (183.677, 6.39), 'PPTL': (1113.035, 71.37), 'WTL': (1366.007, 80.70), 'JPTL': (1065.495, 55.30)}
A_STEP = 8


def a_row(item, i=None):
    """Row of SPV i (0-4) within an Assumption block; i=None -> total row."""
    base = 4 + A_STEP * A_ITEMS.index(item)
    return base + (5 if i is None else i)


def build_assumption(ws, V, ainfo):
    std_sheet(ws, colA=12, widths={'B': 12, 'C': 24, 'AH': 16})
    put(ws, 'C2', 'Rs. cr', bold=True)
    for fy in range(FY0, FYN + 1):
        c = acol(fy)
        put(ws, f'{c}1', dt.datetime(fy, 3, 31), fmt='mmm-yy', align='right')
        put(ws, f'{c}2', fy_label(fy), bold=True, align='right', border_b=True)
    put(ws, 'AH2', 'Tag (for Consolidated SUMIFS)', bold=True, border_b=True)
    for col, lab in (('AI', 'Annual repayment'), ('AJ', 'Interest rate'), ('AK', 'Tax rate')):
        put(ws, f'{col}{a_row("Loan from PGInvIT (closing)", 0) - 1}', lab, bold=True, border_b=True, align='right')
    asset_label = {'Revenue': 'Revenue', 'Total Expenses': 'Total Expenses', 'EBITDA': 'EBITDA', 'Capex': 'Capex',
                   'Changes in WC': 'Changes in WC', 'Taxation': 'Taxation', 'FCFF': 'FCFF', 'TV': 'TV',
                   'FCFF with TV': 'FCFF with TV', 'Discount period': 'Discount period (yrs, mid-year)'}
    for item in A_ITEMS:
        hr = a_row(item, 0) - 1
        put(ws, f'A{hr}', item, bold=True)
        for i, s in enumerate(SPVS):
            r = a_row(item, i)
            put(ws, f'B{r}', 'Transmission')
            put(ws, f'C{r}', s)
            if item in asset_label:
                put(ws, f'AH{r}', item, italic=True)
            for fy in range(FY0, FYN + 1):
                c = acol(fy)
                if item in asset_label:
                    lab = asset_label[item]
                    f = (f'=IF(COUNTIFS(AssetLevelEst!$B:$B,$C{r},AssetLevelEst!$C:$C,"{lab}")=0,0,'
                         f'SUMIFS(AssetLevelEst!{c}:{c},AssetLevelEst!$B:$B,$C{r},AssetLevelEst!$C:$C,"{lab}"))')
                    put(ws, f'{c}{r}', f, fmt=NUM2 if item == 'Discount period' else NUM1)
                elif item == 'EBITDA Margin %':
                    put(ws, f'{c}{r}', f'=IF(OR({c}{a_row("Revenue", i)}=0,{c}{a_row("EBITDA", i)}=0),"",{c}{a_row("EBITDA", i)}/{c}{a_row("Revenue", i)})', fmt=PCT)
                elif item == 'WACC, %':
                    put(ws, f'{c}{r}', f'=AssetLevelEst!$D${ainfo[s]["r0"] + 19}', fmt=PCT2)
                elif item == 'Loan from PGInvIT (closing)':
                    if fy == FY0:
                        put(ws, f'{c}{r}', SPV_LOAN[s][0], fmt=NUM1, color=RED)
                        put(ws, f'AI{r}', SPV_LOAN[s][1], fmt=NUM1, color=BLUE)
                        put(ws, f'AJ{r}', 0.145, fmt=PCT2, color=BLUE)
                        put(ws, f'AK{r}', 0.2517, fmt=PCT2, color=BLUE)
                    else:
                        put(ws, f'{c}{r}', f'=MAX(0,{L(CI(c) - 1)}{r}-$AI{r})', fmt=NUM1)
                elif item == 'Interest on loan from PGInvIT':
                    lr = a_row('Loan from PGInvIT (closing)', i)
                    if fy > FY0:
                        put(ws, f'{c}{r}', f'=$AJ{lr}*AVERAGE({L(CI(c) - 1)}{lr},{c}{lr})', fmt=NUM1)
                elif item == 'Taxation (levered, used for NDCF)':
                    lr = a_row('Loan from PGInvIT (closing)', i)
                    if fy > FY0:
                        put(ws, f'{c}{r}', f'=MAX(0,{c}{a_row("Taxation", i)}-$AK{lr}*{c}{a_row("Interest on loan from PGInvIT", i)})', fmt=NUM1)
                elif item == 'AUM (Rs. cr)':
                    m = ainfo[s]['memo']
                    fc, per, w = a_row('FCFF', i), a_row('Discount period', i), f'{c}{a_row("WACC, %", i)}'
                    k = f'(YEAR({c}$1)-{FY0})'
                    tv = f'AssetLevelEst!$AI${m["Terminal value, undiscounted (TV)"]}'
                    tvp = f'AssetLevelEst!$AI${m["TV discounting period (yrs)"]}'
                    tvy = f'AssetLevelEst!$AI${m["TV year (FY)"]}'
                    rtm = f'AssetLevelEst!$D${ainfo[s]["r0"] + 17}'
                    f = (f'=SUMPRODUCT(($D$1:$AF$1>{c}$1)*$D{fc}:$AF{fc}*(1+{w})^(-($D{per}:$AF{per}-{k})))'
                         f'+IF({tvy}>YEAR({c}$1),{tv}*(1+{w})^(-({tvp}-{k})),{tv})+{rtm}')
                    put(ws, f'{c}{r}', f, fmt=NUM1)
        tr = a_row(item)
        if item not in ('EBITDA Margin %', 'WACC, %', 'Discount period'):
            put(ws, f'C{tr}', item if item.startswith('Total') else f'Total {item}', bold=True)
            for fy in range(FY0, FYN + 1):
                c = acol(fy)
                put(ws, f'{c}{tr}', f'=SUM({c}{a_row(item, 0)}:{c}{a_row(item, 4)})', fmt=NUM1, bold=True)
        elif item == 'EBITDA Margin %':
            put(ws, f'C{tr}', 'Portfolio EBITDA margin', bold=True)
            for fy in range(FY0, FYN + 1):
                c = acol(fy)
                put(ws, f'{c}{tr}', f'=IF(OR({c}{a_row("Revenue")}=0,{c}{a_row("EBITDA")}=0),"",{c}{a_row("EBITDA")}/{c}{a_row("Revenue")})', fmt=PCT, bold=True)
    note = a_row(A_ITEMS[-1]) + 2
    put(ws, f'C{note - 1}', 'Levered tax = valuer (unlevered) SPV tax less tax shield on interest paid to PGInvIT; floor at nil. Used for NDCF and consolidated tax; AUM stays on the valuer basis.', italic=True)
    put(ws, f'C{note}', 'AUM at each 31-Mar = PV of the SPV\'s FCFF for later years only (the year\'s own cash flow is excluded, fixing the IndiGrid double count),', italic=True)
    put(ws, f'C{note + 1}', 'discounted at each SPV\'s valuer WACC on the valuer\'s mid-year periods, plus the terminal value and RTM project value. FY26 ties to the valuer EV.', italic=True)
    put(ws, f'C{note + 2}', 'Check: FY26 AUM - valuer EV', bold=True)
    put(ws, f'D{note + 2}', '=D{0}-SUM({1})'.format(a_row('AUM (Rs. cr)'), ','.join(f'AssetLevelEst!E{ainfo[s]["r0"] + 18}' for s in SPVS)), fmt=NUM2, fill=CHK_FILL)
    return note + 4
