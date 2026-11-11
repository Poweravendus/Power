"""Investor sheets (Sensitivity exit/maturity, Cashflows_Bajaj, IRR Calculation_Bajaj) and Key Sheet New."""
import datetime as dt
from common import *
from core import SPVS, SEN, scol, FYN, S_FY0, a_row, acol, FY0

C_FY0, C_HIST_LAST = 2022, 2026     # Consolidated: C = FY22 ... G = FY26, H = FY27E ... AI = FY54E
CR = dict(hdr=3, rev=6, im=9, pm=10, om=11, emp=12, ins=13, oth=14, texp=15, ebitda=17, oi_yld=21, oi=22, da=23, da_rate=24,
          ebit=26, int_rate=27, fin=28, imp=29, pbt=31, pbt2=34, tax=40, pat=43, pat_after=47, mi=49, pat_min=52,
          units=56, dpu=58, dist=59, nav=244, aum=241, netdebt=242, ndcf=226, debt_open=73, debt_add=74, debt_rep=75,
          debt_close=76, cash=102, capex_cf=148, wc_cf=143, tax_cf=145, int_cf=172, fy_end=3)


def ccol(fy):
    return L(3 + fy - C_FY0)


def clabel(fy):
    return fy_label(fy, fy > C_HIST_LAST)


C_LAST = ccol(FYN)
C_RANGE = lambda r: f'Consolidated!$C${r}:${C_LAST}${r}'


def lookup(row, label_expr):
    return f'INDEX({C_RANGE(row)},MATCH({label_expr},{C_RANGE(CR["hdr"])},0))'


def build_sens_returns(ws, entry_date, first_pay):
    """Hold-to-exit (5 years) and hold-to-maturity unitholder cash flows (quarterly)."""
    r = SEN['exit_hdr']
    put(ws, f'B{r - 1}', 'Amount - Rs. / unit', bold=True)
    put(ws, f'B{r}', 'HOLD TO EXIT   -   5.00 years', bold=True)
    blocks = [(r, 20, True), (SEN['mat_hdr'], (FYN - 2026) * 4 - 1, False)]
    out = {}
    for top, n, is_exit in blocks:
        if not is_exit:
            put(ws, f'B{top}', 'HOLD TO MATURITY  (distributions to FY54E; residual = NAV at 31-Mar-54)', bold=True)
        rl, rd, rp, rdist, rres, rtot = top + 1, top + 2, top + 3, top + 4, top + 5, top + 6
        put(ws, f'B{rl}', 'Financial year (quarter paid for)')
        put(ws, f'B{rd}', 'Payment date')
        put(ws, f'B{rp}', 'Entry price')
        put(ws, f'B{rdist}', 'Distribution  (DPU / 4)')
        put(ws, f'B{rres}', 'Exit NAV' if is_exit else 'Residual NAV at maturity')
        put(ws, f'B{rtot}', 'Total cash', bold=True)
        put(ws, f'C{rl}', 'Entry', align='right')
        put(ws, f'C{rd}', entry_date, fmt='dd-mmm-yy', color=BLUE)
        put(ws, f'C{rp}', '=-$C$2', fmt=NUM2)
        put(ws, f'C{rdist}', 0, fmt=NUM2)
        put(ws, f'C{rres}', 0, fmt=NUM2)
        put(ws, f'C{rtot}', f'=C{rp}+C{rdist}+C{rres}', fmt=NUM2, bold=True)
        for k in range(n):
            c = L(4 + k)
            if k == 0:
                put(ws, f'{c}{rd}', first_pay, fmt='dd-mmm-yy', color=BLUE)
            else:
                put(ws, f'{c}{rd}', f'=EOMONTH({L(3 + k)}{rd},3)', fmt='dd-mmm-yy')
            # quarter paid for ends ~2 months before payment; label = fiscal year of that quarter
            put(ws, f'{c}{rl}', f'="FY"&TEXT(MOD(YEAR(EDATE({c}{rd},-2))+IF(MONTH(EDATE({c}{rd},-2))>=4,1,0),100),"00")&"E"', align='right')
            put(ws, f'{c}{rp}', 0, fmt=NUM2)
            put(ws, f'{c}{rdist}', f'=IFERROR({lookup(CR["dpu"], f"{c}{rl}")}/4,0)', fmt=NUM2)
            put(ws, f'{c}{rres}', 0, fmt=NUM2)
            put(ws, f'{c}{rtot}', f'={c}{rp}+{c}{rdist}+{c}{rres}', fmt=NUM2, bold=True)
        last = L(3 + n)
        if is_exit:
            x = L(4 + n)
            put(ws, f'{x}{rl}', 'Exit', align='right')
            put(ws, f'{x}{rd}', f'=EDATE($C${rd},60)', fmt='dd-mmm-yy')
            put(ws, f'{x}{rp}', 0, fmt=NUM2)
            put(ws, f'{x}{rdist}', 0, fmt=NUM2)
            yr = f'(YEAR({x}{rd})-IF(MONTH({x}{rd})<4,1,0))'
            lab0 = f'"FY"&TEXT(MOD({yr},100),"00")&"E"'
            lab1 = f'"FY"&TEXT(MOD({yr}+1,100),"00")&"E"'
            nav0, nav1 = lookup(CR['nav'], lab0), lookup(CR['nav'], lab1)
            put(ws, f'{x}{rres}', f'={nav0}+({nav1}-{nav0})*({x}{rd}-DATE({yr},3,31))/365', fmt=NUM2)
            put(ws, f'{x}{rtot}', f'={x}{rp}+{x}{rdist}+{x}{rres}', fmt=NUM2, bold=True)
            put(ws, f'{L(5 + n)}{rres}', '<< NAV interpolated between the two 31-Mar NAVs around the exit date', italic=True)
            out['exit'] = (rd, rtot, x)
        else:
            put(ws, f'{last}{rres}', f'={lookup(CR["nav"], chr(34) + clabel(FYN) + chr(34))}', fmt=NUM2)
            put(ws, f'B{rtot + 1}', 'Total cash excl. residual', bold=True)
            put(ws, f'C{rtot + 1}', f'=C{rp}', fmt=NUM2)
            for k in range(n):
                c = L(4 + k)
                put(ws, f'{c}{rtot + 1}', f'={c}{rdist}', fmt=NUM2)
            out['mat'] = (rd, rtot, last)
    rd, rtot, x = out['exit']
    put(ws, 'C3', f'=XIRR(C{rtot}:{x}{rtot},C{rd}:{x}{rd})', fmt=PCT, bold=True)
    rd, rtot, last = out['mat']
    put(ws, 'C4', f'=XIRR(C{rtot + 1}:{last}{rtot + 1},C{rd}:{last}{rd})', fmt=PCT, bold=True)
    put(ws, 'C5', f'=XIRR(C{rtot}:{last}{rtot},C{rd}:{last}{rd})', fmt=PCT, bold=True)
    put(ws, 'D3', '<< entry on the date in row %d; quarterly DPU from Consolidated; exit at modelled NAV' % (SEN['exit_hdr'] + 2), italic=True)

    # debt mirror (as in IndiGrid rows 267-273), linked to Consolidated
    r = SEN['debt']
    put(ws, f'B{r - 1}', 'DEBT  -  Rs. cr (mirror of Consolidated)', bold=True)
    for k, (lab, row) in enumerate([('Opening Debt', CR['debt_open']), ('Addition', CR['debt_add']),
                                     ('Repayment', CR['debt_rep']), ('Closing', CR['debt_close']),
                                     ('Interest Rate', CR['int_rate']), ('Interest Cost', CR['fin'])]):
        put(ws, f'B{r + k}', lab, bold=lab == 'Closing')
        for fy in range(2027, FYN + 1):
            put(ws, f'{scol(fy)}{r + k}', f'=Consolidated!{ccol(fy)}{row}', fmt=PCT2 if 'Rate' in lab else NUM1)


def build_cashflows(ws):
    std_sheet(ws, colA=6, widths={'B': 40})
    put(ws, 'B1', 'Cash flows to the Trust (Rs. cr) - Bajaj Life view; FY27E onwards from Consolidated', italic=True)
    for fy in range(2027, FYN + 1):
        put(ws, f'{L(3 + fy - 2027)}3', f'FY{fy}', bold=True, align='right', border_b=True)
    rows = [(4, None, 'Revenue from operations', CR['rev'], 1), (6, 'Less', 'Investment manager fees', CR['im'], -1),
            (7, 'Less', 'Other expenses (SPV opex and Trust expenses)', None, -1), (9, None, 'EBITDA', None, 0),
            (11, 'Add:', 'Other Income', CR['oi'], 1), (12, 'Less:', 'Tax', CR['tax'], -1), (13, None, 'WC Movement', CR['wc_cf'], 1),
            (14, 'Less', 'Capex', CR['capex_cf'], 1), (15, 'Add:', 'Proceeds of long term borrowings', CR['debt_add'], 1),
            (16, 'Add:', 'Capital Raise', 163, 1), (18, None, 'Cash Available for Debt Servicing', None, 0),
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
    std_sheet(ws, colA=40)
    put(ws, 'A2', 'No. of Units', bold=True)
    put(ws, 'B2', units, fmt='#,##0', color=BLUE)
    put(ws, 'A3', 'Investment date (fixed input; replaces TODAY())', bold=True)
    put(ws, 'B3', val_date, fmt='dd-mmm-yy', color=BLUE)
    put(ws, 'A5', 'Amount Invested (Rs. cr)', bold=True)
    put(ws, 'B5', '=-(B2*Sensitivity_Bajaj!C2)/10000000', fmt=NUM)
    put(ws, 'A7', 'Cash flow date', bold=True)
    put(ws, 'A8', 'Financial year', bold=True)
    put(ws, 'A9', 'NDCF to unitholders (Rs. cr)', bold=True)
    put(ws, 'B7', '=B3', fmt='dd-mmm-yy')
    put(ws, 'B8', 'Entry', align='right')
    put(ws, 'B9', '=B5', fmt=NUM)
    for k, fy in enumerate(range(2027, FYN + 1)):
        c = L(3 + k)
        put(ws, f'{c}7', dt.datetime(fy, 3, 31), fmt='dd-mmm-yy')
        put(ws, f'{c}8', f'FY{fy}', align='right')
        src = f'Cashflows_Bajaj!{L(3 + k)}23'
        if fy == 2027:   # only the part of FY27 after the investment date
            put(ws, f'{c}9', f'={src}*MAX(0,{c}7-$B$3)/365', fmt=NUM)
        else:
            put(ws, f'{c}9', f'={src}', fmt=NUM)
    last = L(3 + FYN - 2027)
    put(ws, 'A11', 'XIRR on NDCF to FY54 (no residual value)', bold=True)
    put(ws, 'B11', f'=XIRR(B9:{last}9,B7:{last}7)', fmt=PCT, bold=True)
    put(ws, 'A12', 'XIRR incl. residual NAV at FY54 (x units)', bold=True)
    put(ws, 'A13', 'Residual NAV at 31-Mar-54 (Rs. cr)')
    put(ws, 'B13', f'={lookup(CR["nav"], chr(34) + clabel(FYN) + chr(34))}*B2/10000000', fmt=NUM)
    put(ws, 'A14', 'NDCF incl. residual (Rs. cr)')
    put(ws, 'B14', '=B9', fmt=NUM)
    for k, fy in enumerate(range(2027, FYN + 1)):
        c = L(3 + k)
        put(ws, f'{c}14', f'={c}9' + ('+$B$13' if fy == FYN else ''), fmt=NUM)
    put(ws, 'B12', f'=XIRR(B14:{last}14,B7:{last}7)', fmt=PCT, bold=True)
    put(ws, 'A16', 'Distribution Yield % on CMP', bold=True)
    put(ws, 'A17', 'Bajaj Life Projection (NDCF / amount invested)')
    for k, fy in enumerate(range(2027, FYN + 1)):
        c = L(3 + k)
        put(ws, f'{c}16', f'FY{fy}', align='right', bold=True)
        put(ws, f'{c}17', f'=Cashflows_Bajaj!{c}23/(-$B$5)', fmt=PCT)
    put(ws, 'A18', 'DPU yield on CMP (DPU / entry price)')
    for k, fy in enumerate(range(2027, FYN + 1)):
        c = L(3 + k)
        put(ws, f'{c}18', f'=Consolidated!{ccol(fy)}{CR["dpu"]}/Sensitivity_Bajaj!$C$2', fmt=PCT)
