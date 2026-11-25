"""Investor sheets (Sensitivity debt schedule, Cashflows_Bajaj, IRR Calculation_Bajaj)."""
import datetime as dt
from common import *
from core import SPVS, SEN, scol, FYN, S_FY0, a_row, acol, FY0

C_FY0, C_HIST_LAST = 2022, 2026     # Consolidated: C = FY22 ... G = FY26, H = FY27E ... AI = FY54E
CR = dict(hdr=3, rev=6, im=9, pm=10, om=11, emp=12, ins=13, oth=14, texp=15, ebitda=17, oi_yld=21, oi=22, da=23, da_rate=24,
          ebit=26, int_rate=27, fin=28, imp=29, pbt=31, pbt2=34, tax=40, pat=43, pat_after=47, mi=49, pat_min=52,
          units=56, dpu=58, dist=59, nav=265, aum=262, netdebt=263, ndcf=251, debt_open=75, debt_add=76, debt_rep=77,
          debt_close=78, cash=112, capex_cf=161, wc_cf=156, tax_cf=158, int_cf=185, fy_end=3)


def ccol(fy):
    return L(3 + fy - C_FY0)


def clabel(fy):
    return fy_label(fy, fy > C_HIST_LAST)


C_LAST = ccol(FYN)
C_RANGE = lambda r: f'Consolidated!$C${r}:${C_LAST}${r}'


def lookup(row, label_expr):
    return f'INDEX({C_RANGE(row)},MATCH({label_expr},{C_RANGE(CR["hdr"])},0))'


def build_sens_returns(ws, entry_date=None, first_pay=None):
    """Debt schedule on the driver sheet (linked to Consolidated)."""
    # debt schedule, linked to Consolidated
    r = SEN['debt']
    put(ws, f'B{r - 1}', 'DEBT  -  Rs. cr', bold=True)
    for k, (lab, row) in enumerate([('Opening Debt', CR['debt_open']), ('Addition', CR['debt_add']),
                                     ('Repayment', CR['debt_rep']), ('Closing', CR['debt_close']),
                                     ('Interest Rate', CR['int_rate']), ('Interest Cost', CR['fin'])]):
        put(ws, f'B{r + k}', lab, bold=lab == 'Closing')
        for fy in range(2027, FYN + 1):
            put(ws, f'{scol(fy)}{r + k}', f'=Consolidated!{ccol(fy)}{row}', fmt=PCT2 if 'Rate' in lab else NUM1)


def build_cashflows(ws):
    std_sheet(ws, colA=6, widths={'B': 40})
    put(ws, 'B1', 'Cash flows to the Trust (Rs. cr)', bold=True)
    for fy in range(2027, FYN + 1):
        put(ws, f'{L(3 + fy - 2027)}3', f'FY{fy}', bold=True, align='right', border_b=True)
    rows = [(4, None, 'Revenue from operations', CR['rev'], 1), (6, 'Less', 'Investment manager fees', CR['im'], -1),
            (7, 'Less', 'Other expenses (SPV opex and Trust expenses)', None, -1), (9, None, 'EBITDA', None, 0),
            (11, 'Add:', 'Other Income', CR['oi'], 1), (12, 'Less:', 'Tax', CR['tax'], -1), (13, None, 'WC Movement', CR['wc_cf'], 1),
            (14, 'Less', 'Capex', CR['capex_cf'], 1), (15, 'Add:', 'Proceeds of long term borrowings', CR['debt_add'], 1),
            (16, 'Add:', 'Capital Raise', 176, 1), (18, None, 'Cash Available for Debt Servicing', None, 0),
            (20, 'Less:', 'Interest paid', CR['fin'], -1), (21, 'Less:', 'Repayment of long term borrowings', CR['debt_rep'], -1),
            (23, None, 'NDCF (to Trust, after debt service)', None, 0)]
    for r, pre, lab, src, sign in rows:
        if pre:
            put(ws, f'A{r}', pre)
        put(ws, f'B{r}', lab, bold=lab in ('EBITDA', 'Cash Available for Debt Servicing', 'NDCF (to Trust, after debt service)'))
        for fy in range(2027, FYN + 1):
            c, cc = L(3 + fy - 2027), ccol(fy)
            if lab == 'Other expenses (SPV opex and Trust expenses)':
                f = f'=-SUM(Consolidated!{cc}{CR["pm"]}:{cc}{CR["oth"]})'
            elif lab == 'EBITDA':
                f = f'={c}4+{c}6+{c}7'
            elif lab == 'Cash Available for Debt Servicing':
                f = f'={c}9+{c}11+{c}12+{c}13+{c}14+{c}15+{c}16'
            elif lab.startswith('NDCF'):
                f = f'={c}18+{c}20+{c}21'
            else:
                f = f'={"-" if sign < 0 else ""}Consolidated!{cc}{src}'
            put(ws, f'{c}{r}', f, fmt=NUM, bold=lab in ('EBITDA', 'Cash Available for Debt Servicing') or lab.startswith('NDCF'))
    put(ws, 'B25', 'Check: NDCF here vs Consolidated NDCF generated', italic=True)
    for fy in range(2027, FYN + 1):
        c, cc = L(3 + fy - 2027), ccol(fy)
        put(ws, f'{c}25', f'={c}23-Consolidated!{cc}{CR["ndcf"]}', fmt=NUM1, fill=CHK_FILL)


def build_irr(ws, units, val_date):
    """Annual NDCF to the Trust, 2/4 of the entry year (Q3+Q4 FY27), IRR() on the row; yield = NDCF / amount invested."""
    std_sheet(ws, colA=40)
    last = L(3 + FYN - 2027)
    put(ws, 'A2', 'No. of Units')
    put(ws, 'B2', units, fmt='General', color=BLUE)
    put(ws, 'A3', 'Investment date')
    put(ws, 'B3', val_date, fmt='dd-mmm-yy', color=BLUE)
    put(ws, 'A5', 'Amount Invested')
    put(ws, 'B5', '=-(B2*Sensitivity_Bajaj!C2)/10000000', fmt=NUM)
    put(ws, 'B8', '=B3', fmt='dd-mmm-yy', bold=True)
    put(ws, 'A9', 'Amount Invested')
    put(ws, 'B9', '=B5', fmt=NUM)
    for k, fy in enumerate(range(2027, FYN + 1)):
        c = L(3 + k)
        put(ws, f'{c}8', f'=Cashflows_Bajaj!{c}3', bold=True, align='center')
        # entry 23-Nov-26 is after the Q2 FY27 record date (17-Nov-26): the buyer gets only Q3 and Q4 of FY27
        put(ws, f'{c}9', f'=Cashflows_Bajaj!{c}23/4*2' if fy == 2027 else f'=Cashflows_Bajaj!{c}23', fmt=NUM)
        put(ws, f'{c}14', f'={c}8', bold=True, align='center')
        put(ws, f'{c}15', f'={c}9/(-$B$9)', fmt=PCT)
    put(ws, 'C9', ws['C9'].value, fmt=NUM)
    put(ws, 'A11', 'IRR', bold=True)
    put(ws, 'B11', f'=IRR(B9:{last}9)', fmt=PCT, bold=True)
    put(ws, 'A14', 'Distribution Yield % on CMP', bold=True)
    put(ws, 'A15', 'Bajaj Life Projection', bold=True)


def build_xirr(ws):
    """IndiGrid-style unitholder cash-in-hand XIRR: quarterly DPU/4, exit at NAV (hold to exit) or residual cash (hold to maturity)."""
    import calendar
    qs = [(2027, 3), (2027, 4)] + [(fy, q) for fy in range(2028, FYN + 1) for q in (1, 2, 3, 4)]
    cols = [L(4 + k) for k in range(len(qs))]
    last = cols[-1]
    put(ws, 'B3', 'XIRR  -  hold to exit (exit at NAV)', bold=True)
    put(ws, 'B4', 'XIRR  -  hold to maturity', bold=True)
    put(ws, 'B5', 'Include residual cash at maturity?')
    put(ws, 'C5', 'Yes', color=BLUE, align='right')
    put(ws, 'D5', '<< Yes = cash left on the balance sheet in FY54E is returned to unitholders at the end. No = distributions only', italic=True)
    hdrs = {}
    for name, r0 in (('exit', 64), ('mat', 75)):
        put(ws, f'B{r0 - 1}' if name == 'exit' else f'B{r0 - 1}', 'UNITHOLDER CASH FLOWS  -  Rs. per unit' if name == 'exit' else None, bold=True)
        if name == 'exit':
            put(ws, f'B{r0}', 'HOLD TO EXIT  -  sell at NAV at end of', bold=True)
            put(ws, f'C{r0}', 'FY31E', color=BLUE, bold=True, align='right')
            put(ws, f'D{r0}', f'=YEARFRAC($C${r0 + 3},DATE(2000+VALUE(MID($C${r0},3,2)),3,31))', fmt='0.0" years"', italic=True)
        else:
            put(ws, f'B{r0}', 'HOLD TO MATURITY  -  last TSA ends FY54', bold=True)
        rf, rq, rd, re_, rdist, rex, rtot = r0 + 1, r0 + 2, r0 + 3, r0 + 4, r0 + 5, r0 + 6, r0 + 7
        hdrs[name] = (rd, rtot)
        put(ws, f'B{rf}', 'Financial year', bold=True, border_b=True)
        put(ws, f'C{rf}', 'Entry', bold=True, align='right', border_b=True)
        put(ws, f'B{rq}', 'Quarter (distribution for)')
        put(ws, f'B{rd}', 'Payment date (quarter end)')
        put(ws, f'C{rd}', "='IRR Calculation_Bajaj'!B3", fmt='dd-mmm-yy')
        put(ws, f'B{re_}', 'Entry price')
        put(ws, f'C{re_}', '=-$C$2', fmt=NUM2)
        put(ws, f'B{rdist}', 'Distribution  (DPU / 4)')
        put(ws, f'C{rdist}', 0, fmt=NUM2)
        put(ws, f'B{rex}', 'Exit at NAV' if name == 'exit' else 'Residual cash returned (FY54E closing cash / units)')
        put(ws, f'C{rex}', 0, fmt=NUM2)
        put(ws, f'B{rtot}', 'Total cash', bold=True)
        put(ws, f'C{rtot}', f'=C{re_}+C{rdist}+C{rex}', fmt=NUM2, bold=True)
        for k, ((fy, q), c) in enumerate(zip(qs, cols)):
            put(ws, f'{c}{rf}', fy_label(fy, True), bold=True, align='right', border_b=True)
            put(ws, f'{c}{rq}', f'Q{q}', align='right')
            if k == 0:
                put(ws, f'{c}{rd}', '=DATE(2026,12,31)', fmt='dd-mmm-yy')
            else:
                put(ws, f'{c}{rd}', f'=EOMONTH({cols[k - 1]}{rd},3)', fmt='dd-mmm-yy')
            put(ws, f'{c}{re_}', 0, fmt=NUM2)
            dpu = f'HLOOKUP({c}${rf},Consolidated!$C$3:${C_LAST}${CR["dpu"]},{CR["dpu"] - 2},0)/4'
            if name == 'exit':
                put(ws, f'{c}{rdist}', f'=IF({c}${rd}<=DATE(2000+VALUE(MID($C${r0},3,2)),3,31),{dpu},0)', fmt=NUM2)
                put(ws, f'{c}{rex}', f'=IF(AND({c}${rf}=$C${r0},{c}${rq}="Q4"),HLOOKUP({c}${rf},Consolidated!$C$3:${C_LAST}${CR["nav"]},{CR["nav"] - 2},0),0)', fmt=NUM2)
            else:
                put(ws, f'{c}{rdist}', f'={dpu}', fmt=NUM2)
                put(ws, f'{c}{rex}', f'=IF($C$5="Yes",Consolidated!${C_LAST}${CR["cash"]}/Consolidated!${C_LAST}${CR["units"]},0)' if c == last else 0, fmt=NUM2)
            put(ws, f'{c}{rtot}', f'={c}{re_}+{c}{rdist}+{c}{rex}', fmt=NUM2, bold=True)
    (d1, t1), (d2, t2) = hdrs['exit'], hdrs['mat']
    put(ws, 'C3', f'=XIRR(C{t1}:{last}{t1},C{d1}:{last}{d1})', fmt=PCT, bold=True)
    put(ws, 'C4', f'=XIRR(C{t2}:{last}{t2},C{d2}:{last}{d2})', fmt=PCT, bold=True)


# HDFC term loans (FY26 annual report): T1 Rs 575.59 cr, 64 quarterly instalments of varying amounts from 30-Jun-22 (last Mar-38);
# T2 Rs 506.00 cr, 64 quarterly instalments from 31-Mar-25 (last Dec-40). Instalment amounts are not disclosed: FY27 = actual run-rate
# (Rs 2.1 cr a quarter), FY28-FY31 total and the back-ended tail fitted to the disclosed contractual maturity profile at 31-Mar-26.
DEBT_T1_OPEN = 563.1
DEBT_REPAY = {
    'T1': {2027: 4.2, 2028: 5.6, 2029: 6.4, 2030: 7.3, 2031: 8.2, 2032: 13.0, 2033: 20.5, 2034: 32.5, 2035: 51.4, 2036: 81.4, 2037: 128.8},
    'T2': {2027: 4.2, 2028: 5.7, 2029: 6.6, 2030: 7.4, 2031: 8.3, 2032: 10.9, 2033: 14.3, 2034: 18.9, 2035: 24.8, 2036: 32.6, 2037: 42.9,
           2038: 56.4, 2039: 74.1, 2040: 97.4},
}
DEBT_LAST = {'T1': 2038, 'T2': 2041}


def build_debt_schedule(ws):
    r0 = 86
    put(ws, f'B{r0 - 2}', 'HDFC TERM LOAN REPAYMENT SCHEDULE  -  Rs. cr', bold=True)
    put(ws, f'B{r0 - 1}', 'Tranche 1: Rs. 575.6 cr (Mar-22), 64 qtrly instalments Jun-22 to Mar-38. Tranche 2: Rs. 506.0 cr (Dec-24), 64 qtrly instalments Mar-25 to Dec-40', italic=True)
    put(ws, f'B{r0}', 'Year', bold=True, border_b=True)
    rows = {'T1': (r0 + 1, r0 + 2, r0 + 3), 'T2': (r0 + 4, r0 + 5, r0 + 6)}
    lab = {'T1': 'Tranche 1', 'T2': 'Tranche 2'}
    for t, (ro, rr, rc) in rows.items():
        put(ws, f'B{ro}', f'{lab[t]}  -  opening')
        put(ws, f'B{rr}', f'{lab[t]}  -  repayment')
        put(ws, f'B{rc}', f'{lab[t]}  -  closing', bold=True)
    rtot, rclose, rchk = r0 + 8, r0 + 9, r0 + 10
    put(ws, f'B{rtot}', 'Total repayment  (to Consolidated row 77)', bold=True)
    put(ws, f'B{rclose}', 'Total closing debt', bold=True)
    put(ws, f'B{rchk}', 'Check: vs Consolidated closing debt', italic=True)
    for fy in range(2027, FYN + 1):
        c, pc = scol(fy), scol(fy - 1)
        put(ws, f'{c}{r0}', fy_label(fy, True), bold=True, align='right', border_b=True)
        for t, (ro, rr, rc) in rows.items():
            if fy == 2027:
                put(ws, f'{c}{ro}', DEBT_T1_OPEN if t == 'T1' else f'=Consolidated!{ccol(2026)}{CR["debt_close"]}-{c}{rows["T1"][0]}',
                    fmt=NUM1, color=BLUE if t == 'T1' else None)
            else:
                put(ws, f'{c}{ro}', f'={pc}{rc}', fmt=NUM1)
            if fy == DEBT_LAST[t]:
                put(ws, f'{c}{rr}', f'={c}{ro}', fmt=NUM1)
            elif fy in DEBT_REPAY[t]:
                put(ws, f'{c}{rr}', DEBT_REPAY[t][fy], fmt=NUM1, color=BLUE)
            else:
                put(ws, f'{c}{rr}', 0, fmt=NUM1)
            put(ws, f'{c}{rc}', f'={c}{ro}-{c}{rr}', fmt=NUM1, bold=True)
        put(ws, f'{c}{rtot}', f'={c}{rows["T1"][1]}+{c}{rows["T2"][1]}', fmt=NUM1, bold=True)
        put(ws, f'{c}{rclose}', f'={c}{rows["T1"][2]}+{c}{rows["T2"][2]}', fmt=NUM1, bold=True)
        put(ws, f'{c}{rchk}', f'=ROUND({c}{rclose}-Consolidated!{ccol(fy)}{CR["debt_close"]},3)', fmt=NUM1, fill=CHK_FILL)
    # validation against the disclosed contractual maturity profile (31-Mar-26, principal + interest, Rs. cr)
    v = rchk + 2
    put(ws, f'B{v}', 'Check vs FY26 annual report maturity profile (principal + interest, Rs. cr)', bold=True)
    put(ws, f'C{v}', 'Disclosed', bold=True, align='right'); put(ws, f'D{v}', 'Model', bold=True, align='right'); put(ws, f'E{v}', 'Diff %', bold=True, align='right')
    def span(a, b):
        cols = [(scol(y), ccol(y)) for y in range(a, b + 1)]
        return '+'.join(f'{sc}{rtot}+Consolidated!{cc}{CR["fin"]}' for sc, cc in cols)
    for k, (lab_, disc, a, b) in enumerate([('Within a year (FY27)', 78.849, 2027, 2027), ('1-5 years (FY28-FY31)', 334.442, 2028, 2031),
                                             ('Beyond 5 years (FY32 onwards)', 1451.762, 2032, FYN)]):
        rr = v + 1 + k
        put(ws, f'B{rr}', lab_)
        put(ws, f'C{rr}', disc, fmt=NUM1, color=RED)
        put(ws, f'D{rr}', f'={span(a, b)}', fmt=NUM1)
        put(ws, f'E{rr}', f'=D{rr}/C{rr}-1', fmt=PCT)
