"""Consolidated sheet: P&L, balance sheet, cash flow, NDCF, distribution and NAV (FY22-FY26 actual, FY27E-FY54E)."""
from common import *
from core import SPVS, a_row, acol, FYN, SEN, scol
from rest import CR, ccol, clabel, C_FY0, C_HIST_LAST, DEBT_REPAY, DEBT_LAST

ROWS = {  # row: (label, kind)  kind: 'h' header, 'b' bold, '' normal, 'g' growth (red italics), 'p' percent
    2: ('Consolidated', 'h'), 3: ('P&L, Rs. cr', 'h'), 6: ('Revenue from operations', 'b'), 7: ('growth, %', 'g'),
    9: ('Investment manager fees', ''), 10: ('Project manager fees', ''), 11: ('Repairs & maintenance / O&M', ''),
    12: ('Employee benefits expenses', ''), 13: ('Insurance expenses', ''), 14: ('Other expenses', ''),
    15: ('Total Expenses', 'b'), 17: ('EBITDA', 'b'), 18: ('margin, %', 'g'), 19: ('growth, %', 'g'),
    21: ('Other income yield on opening cash, %', 'p'), 22: ('Other Income', ''), 23: ('Depreciation and Amortisation', ''),
    24: ('D&A, % of average gross block', 'p'), 26: ('EBIT', 'b'), 27: ('Interest Rate, %', 'p'), 28: ('Finance Expenses', ''),
    29: ('Impairment / (reversal of impairment)', ''), 31: ('PBT before exceptionals', 'b'), 32: ('Exceptional items', ''),
    34: ('PBT after exceptionals', 'b'), 36: ('Tax', 'b'), 37: ('Current Tax', ''), 38: ('Deferred Tax', ''),
    39: ('Earlier years tax', ''), 40: ('Total Tax', 'b'), 41: ('Effective tax rate, %', 'g'), 43: ('PAT', 'b'),
    45: ('Other comprehensive income', ''), 47: ('Total comprehensive income', 'b'), 49: ('Minority share', ''),
    52: ('PAT after Minority', 'b'), 53: ('margin, %', 'g'), 54: ('growth, %', 'g'), 56: ('No. of units, cr', ''),
    57: ('DPU growth', 'g'), 58: ('DPU, Rs./ unit', 'b'), 59: ('Distribution, Rs. cr', ''),
    60: ('Is NDCF generated higher than Distribution', ''),
    62: ('Balance Sheet', 'h'), 63: ("Unitholders' Funds", 'b'), 64: ('Unit Capital', ''),
    65: ('Distributions - repayment of capital (SPV debt)', ''), 66: ('Capital Reserve', ''), 67: ('Retained Earnings', ''),
    68: ("Unitholders' Funds", 'b'), 70: ('Minority Interest', ''), 72: ('Long Term Borrowings', ''), 73: ('Short Term Borrowings', ''),
    74: ('Current Maturities of Long Term', ''), 75: ('Opening Debt', ''), 76: ('Addition', ''), 77: ('Repayment', ''),
    78: ('Closing Balance', 'b'), 80: ('Deferred tax liability - depreciation difference', ''),
    81: ('Less: Deferred tax asset - MAT credit entitlement', ''), 82: ('Less: Deferred tax asset - unused tax losses and others', ''),
    83: ('Deferred Tax liability (net)', 'b'), 84: ('Other long term liabilities', ''), 85: ('Long term provisions', ''),
    86: ('Non Current Liabilities', 'b'), 88: ("Total Liabilities and Unitholders' Funds", 'b'),
    90: ('Gross Block', ''), 91: ('Acc. Depreciation', ''), 92: ('Impairment', ''), 93: ('Net Block', 'b'), 94: ('CWIP', ''),
    96: ('Intangible Assets - gross', ''), 97: ('Intangible Assets - acc. amortisation and impairment', ''), 98: ('Intangible Assets (net)', ''),
    99: ('Goodwill', ''), 100: ('Non-Current Investments', ''), 101: ('Non-current trade receivables', ''),
    102: ('Other non-current financial assets', ''), 103: ('Non-current tax assets (net)', ''), 104: ('Other Non-Current Assets', ''),
    105: ('Non Current Assets', 'b'), 107: ('Inventories', ''), 108: ('Trade Receivables', ''), 109: ('Current Investments', ''),
    110: ('Cash and cash equivalents', ''), 111: ('Other bank balances (term deposits)', ''),
    112: ('Cash & Cash Equivalents (incl. bank balances)', 'b'), 113: ('Other current financial assets', ''),
    114: ('Other Current Assets', ''), 115: ('Current Assets', 'b'), 117: ('Trade Payables', ''), 118: ('Dues for capital expenditure', ''),
    119: ('Other current financial liabilities', ''), 120: ('Other Current Liabilities', ''), 121: ('Provisions', ''),
    122: ('Current tax liabilities (net)', ''), 123: ('Current Liabilities', 'b'), 125: ('Working Capital Including Cash', 'b'),
    127: ('Total Assets (net of current liabilities)', 'b'), 128: ('Diff', 'g'),
    130: ('Cash Flow Statement (INR cr.)', 'h'), 131: ('A. CASH FLOW FROM OPERATING ACTIVITIES', 'b'), 132: ('Profit before tax', ''),
    134: ('Depreciation and amortisation expense', ''), 136: ('Impairment / (reversal of impairment)', ''), 142: ('Finance costs', ''),
    143: ('Interest and other income (shown in investing)', ''), 146: ('Other non-cash adjustments', ''),
    147: ('Operating profit before change in assets and liabilities', 'b'), 149: ('Inventories', ''), 150: ('Trade receivables', ''),
    152: ('Other current and non-current assets / liabilities', ''), 153: ('Trade payables', ''),
    156: ('Changes in assets and liabilities', 'b'), 157: ('Cash flow generated from operations', 'b'), 158: ('Direct taxes (paid) / refund', ''),
    159: ('Net cash flows generated from operating activities', 'b'), 160: ('B. CASH FLOW FROM INVESTING ACTIVITIES', 'b'),
    161: ('Purchase of PPE (incl. CWIP)', ''), 165: ('Acquisition of SPVs / non-controlling interest', ''), 169: ('Interest and other income received', ''),
    173: ('Other investing (deposits, mutual funds, net)', ''), 174: ('Net cash flow (used in) investing activities', 'b'),
    175: ('C. CASH FLOW FROM FINANCING ACTIVITIES', 'b'), 176: ('Proceeds from issue of unit capital', ''), 179: ('Proceeds of borrowings', ''),
    180: ('Repayment of borrowings', ''), 184: ('Other financing', ''), 185: ('Interest paid', ''), 187: ('Payment of distributions to unitholders', ''),
    188: ('Net cash flow generated from / (used in) financing activities', 'b'), 190: ('Net change in cash and cash equivalents', 'b'),
    191: ('Cash and cash equivalents at beginning', ''), 192: ('Cash and cash equivalents at end', 'b'),
    194: ('Working Capital', 'h'), 195: ('Receivable Days', ''), 196: ('Inventory Days', ''), 197: ('Payable Days', ''),
    198: ('Working Capital Days', 'b'), 200: ('Abridged Cash Flow', 'h'), 201: ('Sources of Funds', 'b'),
    202: ('Operating Cashflows before WC', ''), 203: ('Interest and other income received', ''), 205: ('Equity', ''),
    206: ('Net Debt', ''), 207: ('Total Sources of Funds', 'b'), 209: ('Application of Funds (positive number indicates outflow)', 'b'),
    210: ('Working Capital', ''), 211: ('Tax', ''), 212: ('CAPEX', ''), 213: ('Investments in SPVs / Acquisitions', ''),
    214: ('Bank Deposits', ''), 215: ('Interest', ''), 216: ('Distributions to Unitholders', ''), 217: ('Others', ''),
    218: ('Total Application of Funds', 'b'), 220: ('Net Cash', 'b'), 221: ('Check (vs cash flow statement)', 'g'),
    223: ('FCF (CFO + capex)', 'b'),
    225: ('NDCF (as reported), Rs. cr', 'h'),
    226: ('NDCF at SPV - VTL', ''), 227: ('NDCF at SPV - KATL', ''), 228: ('NDCF at SPV - PPTL', ''), 229: ('NDCF at SPV - WTL', ''),
    230: ('NDCF at SPV - JPTL', ''), 231: ('SPVs NDCF', 'b'), 232: ('Upstreamed to PGInvIT, % of SPVs NDCF', 'g'),
    233: ('Cash flow from operating activities', ''), 234: ('Interest income', ''), 235: ('Dividend income', ''),
    236: ('Repayment of capital (SPV debt)', ''), 237: ('Other income', ''), 238: ('Finance cost on borrowing', ''),
    239: ('Debt repayment', ''), 240: ('CAPEX', ''), 241: ('NDCF (PGInvIT)', 'b'), 242: ('Check vs reported NDCF', 'g'),
    248: ('NDCF before CAPEX and Capital Raise', ''), 249: ('Less: CAPEX', ''), 250: ('Add: Net Debt', ''), 251: ('NDCF', 'b'),
    252: ('Add: Capital Raise', ''), 253: ('Cash available before paying Distribution', 'b'),
    255: ('DPU Growth, %', 'p'), 256: ('DPU, Rs./ unit', ''), 257: ('Proposed Distribution', ''), 258: ('Net Cash', ''),
    259: ('Actual Distribution', 'b'), 260: ('Check', ''),
    262: ('AUM/ Value of InvIT Assets - Enterprise Value', 'b'), 263: ('Less: Net Debt', ''), 264: ('Equity', 'b'), 265: ('Equity/ Share', 'b'),
    266: ('Net Debt/ AUM (D/E)', 'p'),
    269: ('Capital Raise', 'h'), 270: ('Rs. cr', ''), 271: ('Price at which dilution happens (prior-year NAV)', ''), 272: ('Additional Units Issued, cr', ''),
    275: ('Debt Repayment Schedule - HDFC term loans, Rs. cr', 'h'),
    276: ('Tranche 1 (Rs. 575.6 cr, Mar-22) - opening', ''), 277: ('Tranche 1 - repayment', ''), 278: ('Tranche 1 - closing', 'b'),
    279: ('Tranche 2 (Rs. 506.0 cr, Dec-24) - opening', ''), 280: ('Tranche 2 - repayment', ''), 281: ('Tranche 2 - closing', 'b'),
    282: ('Total repayment', 'b'), 283: ('Check: closing vs Closing Balance (row 78)', ''),
}
NDCF_Q = {226: 'NDCF at SPV - VTL', 227: 'NDCF at SPV - KATL', 228: 'NDCF at SPV - PPTL', 229: 'NDCF at SPV - WTL', 230: 'NDCF at SPV - JPTL',
          233: 'Cash flow from operating activities', 234: 'Interest income', 235: 'Dividend income', 236: 'Repayment of capital (SPV debt)',
          237: 'Other income', 238: 'Finance cost on borrowing', 239: 'Debt repayment', 240: 'CAPEX'}
DRIVERS = {9: ('Escalation of IM fee, % p.a.', 0.05, PCT), 14: ('Trust-level expenses, FY26 base (Rs. cr)', None, NUM1),
           21: ('Yield on opening cash', None, PCT2), 24: ('D&A rate on average gross block', None, PCT2),
           27: ('Interest rate on borrowings', None, PCT2), 76: ('New borrowings', 0.0, NUM), 77: ('Repayment: see Debt Repayment Schedule, rows 275-283', None, '0'),
           276: ('Tranche 1 at 31-Mar-26: Q2 FY27 PPT Rs 558.3 cr at 30-Sep-26 + H1 repayment', 560.4, NUM1),
           277: ('64 qtrly instalments of varying amounts, Jun-22 to Mar-38 (FY26 AR, borrowings note)', None, '0'),
           280: ('64 qtrly instalments of varying amounts, Mar-25 to Dec-40; FY27 at actual Rs 2.1 cr/qtr; later years fitted to FY26 AR maturity profile and Q2 FY27 PPT (~69% of repayment after 10 years)', None, '0'),
           98: ('Annual amortisation of intangibles', 14.8, NUM1),
           233: ('Tax at Trust, Rs. cr p.a. (FY26 actual)', 3.06, NUM1)}


def build_consolidated(ws, H, drivers, qcol, qrows):
    """H: {row: {fy: value}} historical inputs (Rs cr). drivers: overrides for DRIVERS defaults."""
    std_sheet(ws, colA=2.57, widths={'B': 46, 'AK': 10, 'AL': 52})
    hist = range(C_FY0, C_HIST_LAST + 1)
    fut = range(C_HIST_LAST + 1, FYN + 1)
    for r, (lab, kind) in ROWS.items():
        put(ws, f'B{r}', lab, bold=kind in ('h', 'b'), color=RED if kind == 'g' else None, border_b=kind == 'h')
    for r in (3, 62, 130, 194, 200, 225):
        for fy in range(C_FY0, FYN + 1):
            put(ws, f'{ccol(fy)}{r}', clabel(fy), bold=True, align='right', border_b=True)
    put(ws, 'AK3', 'Driver', bold=True, border_b=True, align='right')
    put(ws, 'AL3', 'Driver', bold=True, border_b=True)
    for r, (lab, default, fmt) in DRIVERS.items():
        v = drivers.get(r, default)
        put(ws, f'AK{r}', v, fmt=fmt, color=BLUE)
        put(ws, f'AL{r}', lab)

    # ---------------- history -------------------------------------------------------------------
    for r, vals in H.items():
        for fy in hist:
            v = vals.get(fy)
            if v is not None:
                put(ws, f'{ccol(fy)}{r}', v, fmt=NUM2 if r in (56, 58) else NUM1, color=RED)
    for fy in hist:
        c = ccol(fy)
        p = ccol(fy - 1) if fy > C_FY0 else None
        f = {15: f'=SUM({c}9:{c}14)', 17: f'={c}6-{c}15', 18: f'=IF({c}6=0,"",{c}17/{c}6)', 26: f'={c}17+{c}22-{c}23',
             31: f'={c}26-{c}28-{c}29', 34: f'={c}31+{c}32', 40: f'=SUM({c}37:{c}39)', 41: f'=IF({c}34=0,"",{c}40/{c}34)',
             43: f'={c}34-{c}40', 47: f'={c}43+{c}45', 52: f'={c}43-{c}49', 53: f'=IF({c}6=0,"",{c}52/{c}6)',
             68: f'=SUM({c}64:{c}67)', 83: f'=SUM({c}80:{c}82)', 98: f'={c}96-{c}97', 75: f'={c}72+{c}73+{c}74', 78: f'={c}75', 86: f'={c}78+{c}83+{c}84+{c}85',
             88: f'={c}68+{c}70+{c}86', 93: f'={c}90-{c}91-{c}92', 105: f'=SUM({c}98:{c}104)', 112: f'=SUM({c}109:{c}111)',
             115: f'={c}107+{c}108+{c}112+{c}113+{c}114', 123: f'=SUM({c}117:{c}122)', 125: f'={c}115-{c}123',
             127: f'={c}105+{c}125+{c}94+{c}93', 128: f'={c}88-{c}127',
             195: f'=IF({c}6=0,"",{c}108/{c}6*365)', 196: f'=IF({c}15=0,"",{c}107/{c}15*365)', 197: f'=IF({c}15=0,"",{c}117/{c}15*365)',
             198: f'=IF({c}195="","",{c}195+{c}196-{c}197)', 223: f'={c}159+{c}161', 264: f'=IF({c}265="","",{c}265*{c}56)',
             263: f'={c}78-{c}112', 147: f'=SUM({c}132:{c}146)', 156: f'=SUM({c}149:{c}155)', 157: f'={c}147+{c}156',
             159: f'={c}157+{c}158', 174: f'=SUM({c}161:{c}173)', 188: f'=SUM({c}176:{c}187)', 190: f'={c}159+{c}174+{c}188',
             192: f'={c}190+{c}191', 59: f'={c}58*{c}56', 231: f'=SUM({c}226:{c}230)', 232: f'=IFERROR(SUM({c}234:{c}236)/{c}231,"")',
             241: f'=SUM({c}233:{c}240)', 60: f'=IF({c}241>={c}59,"Yes","No")', 262: f'={c}264+{c}263' if fy < C_HIST_LAST else None}
        qc = [qcol[q] for q in qcol if 2000 + int(q[-2:]) == fy]
        for r, lab in NDCF_Q.items():
            f[r] = f'=SUM(Qtrly!{qc[0]}{qrows[lab]}:{qc[-1]}{qrows[lab]})'
        f[242] = f'={c}241-SUM(Qtrly!{qc[0]}{qrows["NDCF (as reported)"]}:{qc[-1]}{qrows["NDCF (as reported)"]})'
        f = {k: v for k, v in f.items() if v is not None}
        if 58 not in H or H[58].get(fy) is None:
            f[58] = f'=IF({c}56=0,"",{c}59/{c}56)'
        for r, form in f.items():
            if H.get(r, {}).get(fy) is None:
                put(ws, f'{c}{r}', form, fmt=PCT if r in (18, 41, 53) else NUM1, bold=ROWS.get(r, ('', ''))[1] == 'b',
                    color=RED if r in (232, 242) else None)
        if p:
            for r, base in ((7, 6), (19, 17), (54, 52), (57, 58)):
                put(ws, f'{c}{r}', f'=IFERROR({c}{base}/{p}{base}-1,"")', fmt=PCT, color=RED)
    G = ccol(C_HIST_LAST)
    put(ws, f'{G}262', f'=Assumption!{acol(2026)}{a_row("AUM (Rs. cr)")}', fmt=NUM1, bold=True)
    put(ws, f'{G}264', f'={G}262-{G}263', fmt=NUM1, bold=True)
    put(ws, f'{G}265', f'={G}264/{G}56', fmt=NUM2, bold=True)
    put(ws, f'{G}266', f'={G}263/{G}262', fmt=PCT)
    put(ws, f'{G}256', f'={G}58', fmt=NUM2)
    for fy in hist:
        if fy < C_HIST_LAST:
            put(ws, f'{ccol(fy)}266', f'={ccol(fy)}263/{ccol(fy)}262', fmt=PCT)

    # ---------------- forecast -------------------------------------------------------------------
    for fy in fut:
        c, p, ac = ccol(fy), ccol(fy - 1), acol(fy)
        A = lambda item: f'Assumption!{ac}{a_row(item)}'
        n = fy - C_HIST_LAST
        f = {
            6: f'={A("Revenue")}', 7: f'={c}6/{p}6-1',
            9: f'={p}9*(1+$AK$9)', 10: 0, 11: 0, 12: 0, 13: 0,
            14: f'={A("Total Expenses")}+$AK$14*(1+$AK$9)^{n}', 15: f'=SUM({c}9:{c}14)',
            17: f'={c}6-{c}15', 18: f'=IF({c}6=0,"",{c}17/{c}6)', 19: f'=IFERROR({c}17/{p}17-1,"")',
            21: '=$AK$21', 22: f'={c}21*{p}112', 23: f'=MIN({c}24*AVERAGE({p}90,{c}90),{p}93+{c}90-{p}90)+({p}98-{c}98)', 24: '=$AK$24',
            26: f'={c}17+{c}22-{c}23', 27: '=$AK$27', 28: f'={c}27*AVERAGE({c}75,{c}78)', 29: 0,
            31: f'={c}26-{c}28-{c}29', 32: 0, 34: f'={c}31+{c}32', 37: f'={A("Taxation (levered, used for NDCF)")}+$AK$233', 38: 0, 39: 0,
            40: f'=SUM({c}37:{c}39)', 41: f'=IF({c}34=0,"",{c}40/{c}34)', 43: f'={c}34-{c}40', 45: 0, 47: f'={c}43+{c}45',
            49: 0, 52: f'={c}43-{c}49', 53: f'=IF({c}6=0,"",{c}52/{c}6)', 54: f'=IFERROR({c}52/{p}52-1,"")',
            56: f'={p}56+{c}272', 57: f'=IFERROR({c}58/{p}58-1,"")', 58: f'={c}59/{c}56', 59: f'={c}259',
            60: f'=IF({c}241>={c}59,"Yes","No")',
            64: f'={p}64+{c}176', 65: f'={p}65', 66: f'={p}66', 67: f'={p}67+{c}52-{c}59', 68: f'=SUM({c}64:{c}67)', 70: f'={p}70',
            75: f'={p}78', 76: '=$AK$76', 77: f'={c}282', 78: f'={c}75+{c}76-{c}77',
            80: f'={p}80', 81: f'={p}81', 82: f'={p}82', 83: f'=SUM({c}80:{c}82)', 84: f'={p}84', 85: f'={p}85', 86: f'={c}78+{c}83+{c}84+{c}85', 88: f'={c}68+{c}70+{c}86',
            90: f'={p}90+{A("Capex")}', 91: f'={p}91+{c}23-({p}98-{c}98)', 92: f'={p}92+{c}29', 93: f'={c}90-{c}91-{c}92', 94: f'={p}94',
            96: f'={p}96', 97: f'={c}96-{c}98', 98: f'=MAX(0,{p}98-$AK$98)', 99: f'={p}99', 100: f'={p}100', 101: f'={p}101', 102: f'={p}102', 103: f'={p}103', 104: f'={p}104', 105: f'=SUM({c}98:{c}104)',
            107: f'={p}107', 108: f'={p}108', 109: f'={p}109', 111: f'={p}111', 110: f'={c}112-{c}111-{c}109', 112: f'={c}192',
            113: f'={p}113', 114: f'={p}114', 115: f'={c}107+{c}108+{c}112+{c}113+{c}114', 117: f'={p}117', 118: f'={p}118', 119: f'={p}119', 120: f'={p}120', 121: f'={p}121', 122: f'={p}122',
            123: f'=SUM({c}117:{c}122)', 125: f'={c}115-{c}123', 127: f'={c}105+{c}125+{c}94+{c}93', 128: f'={c}88-{c}127',
            132: f'={c}34', 134: f'={c}23', 136: f'={c}29', 142: f'={c}28', 147: f'=SUM({c}132:{c}146)',
            149: f'={p}107-{c}107', 150: f'={p}108-{c}108',
            152: f'={p}105-{c}105-({p}98-{c}98)+{p}113-{c}113+{p}114-{c}114+SUM({c}118:{c}122)-SUM({p}118:{p}122)+{c}83-{p}83+{c}84-{p}84+{c}85-{p}85',
            153: f'={c}117-{p}117', 156: f'=SUM({c}149:{c}155)', 157: f'={c}147+{c}156', 158: f'=-{c}40', 159: f'={c}157+{c}158',
            161: f'=-({c}90-{p}90+{c}94-{p}94)', 174: f'=SUM({c}161:{c}173)', 176: f'={c}270', 179: f'={c}76', 180: f'=-{c}77',
            185: f'=-{c}28', 187: f'=-{c}59', 188: f'=SUM({c}176:{c}187)', 190: f'={c}159+{c}174+{c}188',
            191: f'={p}112', 192: f'={c}190+{c}191',
            195: f'=IF({c}6=0,"",{c}108/{c}6*365)', 196: f'=IF({c}15=0,"",{c}107/{c}15*365)',
            197: f'=IF({c}15=0,"",{c}117/{c}15*365)', 198: f'={c}195+{c}196-{c}197', 223: f'={c}159+{c}161',
            **{226 + i: f'=Assumption!{ac}{a_row("EBITDA", i)}-Assumption!{ac}{a_row("Taxation (levered, used for NDCF)", i)}' for i in range(len(SPVS))},
            231: f'=SUM({c}226:{c}230)', 232: f'=IFERROR(SUM({c}234:{c}236)/{c}231,"")',
            233: f'={c}17-{A("EBITDA")}+{c}156-$AK$233',
            234: '=' + '+'.join(f'Assumption!{ac}{a_row("Interest on loan from PGInvIT", i)}' for i in range(len(SPVS))),
            236: '=' + '+'.join(f'Assumption!{acol(fy - 1)}{a_row("Loan from PGInvIT (closing)", i)}-Assumption!{ac}{a_row("Loan from PGInvIT (closing)", i)}' for i in range(len(SPVS))),
            235: f'={c}231-{c}234-{c}236', 237: f'={c}22', 238: f'=-{c}28', 239: f'={c}179+{c}180', 240: f'={c}161',
            241: f'=SUM({c}233:{c}240)',
            248: f'={c}241-{c}249-{c}250', 249: f'={c}161', 250: f'={c}179+{c}180', 251: f'=SUM({c}248:{c}250)', 252: f'={c}176',
            253: f'={c}251+{c}252', 255: 0, 256: f'={p}256*(1+{c}255)',
            257: (f'={c}256*{c}56' if fy == C_HIST_LAST + 1 else f'=MAX(0,MIN({c}251,{c}256*{c}56))'),
            258: f'={c}253-{c}257', 259: f'=IF(MIN({c}257,{c}191+{c}253)<0,0,MIN({c}257,{c}191+{c}253))',
            260: f'=IF(AND(ROUND({c}251-{c}259,2)>=0,{c}259/{c}251>=0.9),"ok","not ok")',
            262: f'={A("AUM (Rs. cr)")}', 263: f'={c}78-{c}112', 264: f'={c}262-{c}263', 265: f'={c}264/{c}56',
            266: f'=IF({c}262=0,"",{c}263/{c}262)', 270: 0, 271: f'={p}265', 272: f'=IFERROR({c}270/{c}271,0)',
            276: (f'=$AK$276' if fy == C_HIST_LAST + 1 else f'={p}278'), 277: (f'={c}276' if fy == DEBT_LAST['T1'] else DEBT_REPAY['T1'].get(fy, 0)),
            278: f'={c}276-{c}277',
            279: (f'={p}78-{c}276' if fy == C_HIST_LAST + 1 else f'={p}281'), 280: (f'={c}279' if fy == DEBT_LAST['T2'] else DEBT_REPAY['T2'].get(fy, 0)),
            281: f'={c}279-{c}280', 282: f'={c}277+{c}280', 283: f'=ROUND({c}278+{c}281-{c}78,3)',
        }
        for r, form in f.items():
            kind = ROWS.get(r, ('', ''))[1]
            fmt = PCT if kind in ('g', 'p') or r in (18, 41, 53) else (NUM2 if r in (56, 58, 256, 265, 271, 272) else NUM1)
            if r in (21, 24, 27):
                fmt = PCT2
            put(ws, f'{c}{r}', form, fmt=fmt, bold=kind in ('b',), color=RED if kind == 'g' else None)
    for fy in range(C_FY0, FYN + 1):
        c = ccol(fy)
        ab = {202: f'={c}147', 203: f'=N({c}169)', 205: f'=N({c}176)+N({c}177)', 206: f'=N({c}178)+N({c}179)+N({c}180)',
              207: f'=SUM({c}202:{c}206)', 210: f'=-{c}156', 211: f'=-{c}158', 212: f'=-{c}161', 213: f'=-N({c}165)',
              214: f'=-N({c}173)', 215: f'=-{c}185', 216: f'=-{c}187', 217: f'=-N({c}184)', 218: f'=SUM({c}210:{c}217)',
              220: f'={c}207-{c}218', 221: f'={c}220-{c}190'}
        for r, form in ab.items():
            put(ws, f'{c}{r}', form, fmt=NUM1, bold=r in (194, 205, 207))
    for r in (128, 221):
        for fy in range(C_FY0, FYN + 1):
            ws[f'{ccol(fy)}{r}'].fill = CHK_FILL
    put(ws, 'B267', 'Check: FY26 NAV / unit vs valuer NAV (Rs. 90.79)', italic=True)
    put(ws, f'{G}267', f'={G}265-90.79', fmt=NUM2, fill=CHK_FILL)
    for fy in hist:
        ws[f'{ccol(fy)}242'].fill = CHK_FILL
