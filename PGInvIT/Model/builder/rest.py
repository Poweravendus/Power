"""Investor sheets (Sensitivity debt schedule, Cashflows_Bajaj, IRR Calculation_Bajaj)."""
import datetime as dt
from common import *
from core import SPVS, SEN, scol, FYN, S_FY0, a_row, acol, FY0

C_FY0, C_HIST_LAST = 2022, 2026     # Consolidated: C = FY22 ... G = FY26, H = FY27E ... AI = FY54E
CR = dict(hdr=3, rev=6, im=9, pm=10, om=11, emp=12, ins=13, oth=14, texp=15, ebitda=17, oi_yld=21, oi=22, da=23, da_rate=24,
          ebit=26, int_rate=27, fin=28, imp=29, pbt=31, pbt2=34, tax=40, pat=43, pat_after=47, mi=49, pat_min=52,
          units=56, dpu=58, dist=59, nav=252, aum=249, netdebt=250, ndcf=238, debt_open=73, debt_add=74, debt_rep=75,
          debt_close=76, cash=102, capex_cf=148, wc_cf=143, tax_cf=145, int_cf=172, fy_end=3)


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
    """Annual NDCF to the Trust, 3/4 of the entry year, IRR() on the row; yield = NDCF / amount invested."""
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
        put(ws, f'{c}9', f'=Cashflows_Bajaj!{c}23/4*3' if fy == 2027 else f'=Cashflows_Bajaj!{c}23', fmt=NUM)
        put(ws, f'{c}14', f'={c}8', bold=True, align='center')
        put(ws, f'{c}15', f'={c}9/(-$B$9)', fmt=PCT)
    put(ws, 'C9', ws['C9'].value, fmt=NUM)
    put(ws, 'A11', 'IRR', bold=True)
    put(ws, 'B11', f'=IRR(B9:{last}9)', fmt=PCT, bold=True)
    put(ws, 'A14', 'Distribution Yield % on CMP', bold=True)
    put(ws, 'A15', 'Bajaj Life Projection', bold=True)
