"""Consolidated sheet: P&L, balance sheet, cash flow, NDCF, distribution and NAV (FY22-FY26 actual, FY27E-FY54E)."""
from common import *
from core import SPVS, a_row, acol, FYN, SEN, scol
from rest import CR, ccol, clabel, C_FY0, C_HIST_LAST

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
    62: ('Balance Sheet', 'h'), 63: ("Unitholders' Funds", 'b'), 64: ('Unit Capital', ''), 65: ('Other Equity / Reserves', ''),
    66: ("Unitholders' Funds", 'b'), 68: ('Minority Interest', ''), 70: ('Long Term Borrowings', ''), 71: ('Short Term Borrowings', ''),
    72: ('Current Maturities of Long Term', ''), 73: ('Opening Debt', ''), 74: ('Addition', ''), 75: ('Repayment', ''),
    76: ('Closing Balance', 'b'), 78: ('Deferred Tax liability (net)', ''), 79: ('Other long term liabilities', ''),
    80: ('Long term provisions', ''), 81: ('Non Current Liabilities', 'b'), 83: ("Total Liabilities and Unitholders' Funds", 'b'),
    85: ('Gross Block', ''), 86: ('Acc. Depreciation and impairment', ''), 87: ('Net Block', 'b'), 88: ('CWIP', ''),
    91: ('Intangible Assets', ''), 92: ('Goodwill', ''), 93: ('Non-Current Investments', ''), 95: ('Other Non-Current Assets', ''),
    96: ('Non Current Assets (excl. block)', 'b'), 98: ('Inventories', ''), 99: ('Trade Receivables', ''),
    100: ('Other bank balances (term deposits)', ''), 101: ('Cash and cash equivalents', ''), 102: ('Cash & Cash Equivalents (incl. investments)', 'b'),
    104: ('Other Current Assets', ''), 105: ('Current Assets', 'b'), 107: ('Trade Payables', ''), 108: ('Other Current Liabilities', ''),
    109: ('Provisions', ''), 110: ('Current Liabilities', 'b'), 112: ('Working Capital Including Cash', 'b'), 114: ('Total Assets (net of current liabilities)', 'b'),
    115: ('Diff', 'g'),
    117: ('Cash Flow Statement (INR cr.)', 'h'), 118: ('A. CASH FLOW FROM OPERATING ACTIVITIES', 'b'), 119: ('Profit before tax', ''),
    121: ('Depreciation and amortisation expense', ''), 123: ('Impairment / (reversal of impairment)', ''), 129: ('Finance costs', ''),
    130: ('Interest and other income (shown in investing)', ''), 133: ('Other non-cash adjustments', ''),
    134: ('Operating profit before change in assets and liabilities', 'b'), 136: ('Inventories', ''), 137: ('Trade receivables', ''),
    139: ('Other current and non-current assets / liabilities', ''), 140: ('Trade payables', ''),
    143: ('Changes in assets and liabilities', 'b'), 144: ('Cash flow generated from operations', 'b'), 145: ('Direct taxes (paid) / refund', ''),
    146: ('Net cash flows generated from operating activities', 'b'), 147: ('B. CASH FLOW FROM INVESTING ACTIVITIES', 'b'),
    148: ('Purchase of PPE (incl. CWIP)', ''), 152: ('Acquisition of SPVs / non-controlling interest', ''), 156: ('Interest and other income received', ''),
    160: ('Other investing (deposits, mutual funds, net)', ''), 161: ('Net cash flow (used in) investing activities', 'b'),
    162: ('C. CASH FLOW FROM FINANCING ACTIVITIES', 'b'), 163: ('Proceeds from issue of unit capital', ''), 166: ('Proceeds of borrowings', ''),
    167: ('Repayment of borrowings', ''), 171: ('Other financing', ''), 172: ('Interest paid', ''), 174: ('Payment of distributions to unitholders', ''),
    175: ('Net cash flow generated from / (used in) financing activities', 'b'), 177: ('Net change in cash and cash equivalents', 'b'),
    178: ('Cash and cash equivalents at beginning', ''), 179: ('Cash and cash equivalents at end', 'b'),
    181: ('Working Capital', 'h'), 182: ('Receivable Days', ''), 183: ('Inventory Days', ''), 184: ('Payable Days', ''),
    185: ('Working Capital Days', 'b'), 187: ('Abridged Cash Flow', 'h'), 188: ('Sources of Funds', 'b'),
    189: ('Operating Cashflows before WC', ''), 190: ('Interest and other income received', ''), 192: ('Equity', ''),
    193: ('Net Debt', ''), 194: ('Total Sources of Funds', 'b'), 196: ('Application of Funds (positive number indicates outflow)', 'b'),
    197: ('Working Capital', ''), 198: ('Tax', ''), 199: ('CAPEX', ''), 200: ('Investments in SPVs / Acquisitions', ''),
    201: ('Bank Deposits', ''), 202: ('Interest', ''), 203: ('Distributions to Unitholders', ''), 204: ('Others', ''),
    205: ('Total Application of Funds', 'b'), 207: ('Net Cash', 'b'), 208: ('Check (vs cash flow statement)', 'g'),
    210: ('FCF (CFO + capex)', 'b'),
    212: ('NDCF, Rs. cr', 'h'), 213: ('EBITDA at SPV', ''), 214: ('Finance Income', ''), 215: ('WC Movement', ''),
    216: ('Capex related movement', ''), 217: ('Tax at SPV', ''), 218: ('NDCF at SPV', 'b'), 219: ('Expenses at Trust (IM fee and Trust costs)', ''),
    220: ('Finance cost at Trust', ''), 221: ('MTM', ''), 222: ('DSRA', ''), 223: ('Retained at SPV / other adjustments', ''), 224: ('Tax at Trust', ''),
    225: ('Debt drawdown / (repayment)', ''), 226: ('NDCF Generated', 'b'), 228: ('Add: opening cash above minimum cash', ''),
    229: ('Cash available before paying Distribution', 'b'), 235: ('DPU Growth, % (target)', 'p'), 236: ('DPU target, Rs./ unit', ''),
    237: ('Proposed Distribution', ''), 238: ('Net Cash retained / (drawn)', ''), 239: ('Actual Distribution', 'b'),
    240: ('Check: distribution >= 90% of NDCF (SEBI floor)', ''), 241: ('AUM / Value of InvIT Assets - Enterprise Value', 'b'),
    242: ('Less: Net Debt', ''), 243: ('Equity (NAV)', 'b'), 244: ('NAV / unit, Rs.', 'b'), 245: ('Net Debt / AUM', 'p'),
    249: ('Capital Raise', 'h'), 250: ('Rs. cr', ''), 251: ('Price at which dilution happens (prior-year NAV)', ''), 252: ('Additional Units Issued, cr', ''),
}
DRIVERS = {9: ('Escalation of IM fee, % p.a.', 0.05, PCT), 14: ('Trust-level expenses, FY26 base (Rs. cr)', None, NUM1),
           21: ('Yield on opening cash', None, PCT2), 24: ('D&A rate on average gross block', None, PCT2),
           27: ('Interest rate on borrowings', None, PCT2), 74: ('New borrowings', 0.0, NUM), 75: ('Debt fully repaid by FY (straight line)', 2052, '0'),
           91: ('Annual amortisation of intangibles', 14.8, NUM1),
           224: ('Tax at Trust, Rs. cr p.a. (FY26 actual)', 3.06, NUM1), 228: ('Minimum cash balance (Rs. cr)', None, NUM), 239: ('Pay DPU target up to FY', 2027, '0'), 235: ('DPU growth target, % p.a.', 0.0, PCT),
           236: ('DPU target (Rs./unit)', 12.0, NUM2)}


def build_consolidated(ws, H, drivers):
    """H: {row: {fy: value}} historical inputs (Rs cr). drivers: overrides for DRIVERS defaults."""
    std_sheet(ws, colA=2.57, widths={'B': 46, 'AK': 10, 'AL': 52})
    hist = range(C_FY0, C_HIST_LAST + 1)
    fut = range(C_HIST_LAST + 1, FYN + 1)
    for r, (lab, kind) in ROWS.items():
        put(ws, f'B{r}', lab, bold=kind in ('h', 'b'), color=RED if kind == 'g' else None, border_b=kind == 'h')
    for r in (3, 62, 117, 181, 187, 212):
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
             66: f'={c}64+{c}65', 73: f'={c}70+{c}71+{c}72', 76: f'={c}73', 81: f'={c}76+{c}78+{c}79+{c}80',
             83: f'={c}66+{c}68+{c}81', 87: f'={c}85-{c}86', 96: f'=SUM({c}90:{c}95)', 102: f'={c}100+{c}101',
             105: f'={c}98+{c}99+{c}102+{c}103+{c}104', 110: f'=SUM({c}107:{c}109)', 112: f'={c}105-{c}110',
             114: f'={c}96+{c}112+{c}88+{c}87', 115: f'={c}83-{c}114',
             182: f'=IF({c}6=0,"",{c}99/{c}6*365)', 183: f'=IF({c}15=0,"",{c}98/{c}15*365)', 184: f'=IF({c}15=0,"",{c}107/{c}15*365)',
             185: f'=IF({c}182="","",{c}182+{c}183-{c}184)', 210: f'={c}146+{c}148', 243: f'=IF({c}244="","",{c}244*{c}56)',
             242: f'={c}76-{c}102', 134: f'=SUM({c}119:{c}133)', 143: f'=SUM({c}136:{c}142)', 144: f'={c}134+{c}143',
             146: f'={c}144+{c}145', 161: f'=SUM({c}148:{c}160)', 175: f'=SUM({c}163:{c}174)', 177: f'={c}146+{c}161+{c}175',
             179: f'={c}177+{c}178', 59: f'={c}58*{c}56', 218: f'=SUM({c}213:{c}217)' if H.get(213, {}).get(fy) is not None else None,
             241: f'={c}243+{c}242' if fy < C_HIST_LAST else None}
        f = {k: v for k, v in f.items() if v is not None}
        if 58 not in H or H[58].get(fy) is None:
            f[58] = f'=IF({c}56=0,"",{c}59/{c}56)'
        for r, form in f.items():
            if H.get(r, {}).get(fy) is None:
                put(ws, f'{c}{r}', form, fmt=PCT if r in (18, 41, 53) else NUM1, bold=ROWS.get(r, ('', ''))[1] == 'b')
        if p:
            for r, base in ((7, 6), (19, 17), (54, 52), (57, 58)):
                put(ws, f'{c}{r}', f'=IFERROR({c}{base}/{p}{base}-1,"")', fmt=PCT, color=RED)
    G = ccol(C_HIST_LAST)
    put(ws, f'{G}241', f'=Assumption!{acol(2026)}{a_row("AUM (Rs. cr)")}', fmt=NUM1, bold=True)
    put(ws, f'{G}243', f'={G}241-{G}242', fmt=NUM1, bold=True)
    put(ws, f'{G}244', f'={G}243/{G}56', fmt=NUM2, bold=True)
    put(ws, f'{G}245', f'={G}242/{G}241', fmt=PCT)
    put(ws, f'{G}236', f'={G}58', fmt=NUM2)

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
            21: '=$AK$21', 22: f'={c}21*{p}102', 23: f'=MIN({c}24*AVERAGE({p}85,{c}85),{p}87+{c}85-{p}85)+({p}91-{c}91)', 24: '=$AK$24',
            26: f'={c}17+{c}22-{c}23', 27: '=$AK$27', 28: f'={c}27*AVERAGE({c}73,{c}76)', 29: 0,
            31: f'={c}26-{c}28-{c}29', 32: 0, 34: f'={c}31+{c}32', 37: f'={A("Taxation (levered, used for NDCF)")}+$AK$224', 38: 0, 39: 0,
            40: f'=SUM({c}37:{c}39)', 41: f'=IF({c}34=0,"",{c}40/{c}34)', 43: f'={c}34-{c}40', 45: 0, 47: f'={c}43+{c}45',
            49: 0, 52: f'={c}43-{c}49', 53: f'=IF({c}6=0,"",{c}52/{c}6)', 54: f'=IFERROR({c}52/{p}52-1,"")',
            56: f'={p}56+{c}252', 57: f'=IFERROR({c}58/{p}58-1,"")', 58: f'={c}59/{c}56', 59: f'={c}239',
            60: f'=IF({c}226>={c}59,"Yes","No")',
            64: f'={p}64+{c}163', 65: f'={p}65+{c}52-{c}59', 66: f'={c}64+{c}65', 68: f'={p}68',
            73: f'={p}76', 74: '=$AK$74', 75: f'=IF({fy}>$AK$75,0,{c}73/($AK$75-{fy}+1))', 76: f'={c}73+{c}74-{c}75',
            78: f'={p}78', 79: f'={p}79', 80: f'={p}80', 81: f'={c}76+{c}78+{c}79+{c}80', 83: f'={c}66+{c}68+{c}81',
            85: f'={p}85+{A("Capex")}', 86: f'={p}86+{c}23-({p}91-{c}91)+{c}29', 87: f'={c}85-{c}86', 88: f'={p}88',
            91: f'=MAX(0,{p}91-$AK$91)', 92: f'={p}92', 93: f'={p}93', 95: f'={p}95', 96: f'=SUM({c}90:{c}95)',
            98: f'={c}183*{c}15/365', 99: f'={c}182*{c}6/365', 100: f'={p}100', 101: f'={c}102-{c}100', 102: f'={c}179',
            104: f'={p}104', 105: f'={c}98+{c}99+{c}102+{c}103+{c}104', 107: f'={c}184*{c}15/365', 108: f'={p}108', 109: f'={p}109',
            110: f'=SUM({c}107:{c}109)', 112: f'={c}105-{c}110', 114: f'={c}96+{c}112+{c}88+{c}87', 115: f'={c}83-{c}114',
            119: f'={c}34', 121: f'={c}23', 123: f'={c}29', 129: f'={c}28', 134: f'=SUM({c}119:{c}133)',
            136: f'={p}98-{c}98', 137: f'={p}99-{c}99',
            139: f'={p}96-{c}96-({p}91-{c}91)+{p}104-{c}104+{c}108-{p}108+{c}109-{p}109+{c}78-{p}78+{c}79-{p}79+{c}80-{p}80',
            140: f'={c}107-{p}107', 143: f'=SUM({c}136:{c}142)', 144: f'={c}134+{c}143', 145: f'=-{c}40', 146: f'={c}144+{c}145',
            148: f'=-({c}85-{p}85+{c}88-{p}88)', 161: f'=SUM({c}148:{c}160)', 163: f'={c}250', 166: f'={c}74', 167: f'=-{c}75',
            172: f'=-{c}28', 174: f'=-{c}59', 175: f'=SUM({c}163:{c}174)', 177: f'={c}146+{c}161+{c}175',
            178: f'={p}102', 179: f'={c}177+{c}178',
            182: f'=Sensitivity_Bajaj!{scol(fy)}{SEN["wc"]}', 183: f'=Sensitivity_Bajaj!{scol(fy)}{SEN["wc"] + 1}',
            184: f'=Sensitivity_Bajaj!{scol(fy)}{SEN["wc"] + 2}', 185: f'={c}182+{c}183-{c}184', 210: f'={c}146+{c}148',
            213: f'={A("EBITDA")}', 214: f'={c}22', 215: f'={c}143', 216: f'={c}148', 217: f'=-{A("Taxation (levered, used for NDCF)")}',
            218: f'=SUM({c}213:{c}217)', 219: f'={c}17-{c}213', 220: f'=-{c}28', 221: 0, 222: 0, 223: 0, 224: '=-$AK$224',
            225: f'={c}74-{c}75', 226: f'=SUM({c}218:{c}225)', 228: f'=MAX(0,{p}102-$AK$228)', 229: f'={c}226+{c}228',
            235: '=$AK$235', 236: (f'=$AK$236' if fy == C_HIST_LAST + 1 else f'={p}236*(1+{c}235)'),
            237: f'=MAX(0.9*{c}226,MIN({c}236*{c}56,{c}229))', 238: f'={c}226-{c}239', 239: f'=IF({fy}<=$AK$239,{c}236*{c}56,MAX(0,{c}237))',
            240: f'=IF({c}239>=0.9*{c}226-0.001,"ok","below 90% floor")',
            241: f'={A("AUM (Rs. cr)")}', 242: f'={c}76-{c}102', 243: f'={c}241-{c}242', 244: f'={c}243/{c}56',
            245: f'=IF({c}241=0,"",{c}242/{c}241)', 250: 0, 251: f'={p}244', 252: f'=IFERROR({c}250/{c}251,0)',
        }
        for r, form in f.items():
            kind = ROWS.get(r, ('', ''))[1]
            fmt = PCT if kind in ('g', 'p') or r in (18, 41, 53) else (NUM2 if r in (56, 58, 236, 244, 251, 252) else NUM1)
            if r in (21, 24, 27):
                fmt = PCT2
            put(ws, f'{c}{r}', form, fmt=fmt, bold=kind in ('b',), color=RED if kind == 'g' else None)
    for fy in range(C_FY0, FYN + 1):
        c = ccol(fy)
        ab = {189: f'={c}134', 190: f'=N({c}156)', 192: f'=N({c}163)+N({c}164)', 193: f'=N({c}165)+N({c}166)+N({c}167)',
              194: f'=SUM({c}189:{c}193)', 197: f'=-{c}143', 198: f'=-{c}145', 199: f'=-{c}148', 200: f'=-N({c}152)',
              201: f'=-N({c}160)', 202: f'=-{c}172', 203: f'=-{c}174', 204: f'=-N({c}171)', 205: f'=SUM({c}197:{c}204)',
              207: f'={c}194-{c}205', 208: f'={c}207-{c}177'}
        for r, form in ab.items():
            put(ws, f'{c}{r}', form, fmt=NUM1, bold=r in (194, 205, 207))
    for r in (115, 208):
        for fy in range(C_FY0, FYN + 1):
            ws[f'{ccol(fy)}{r}'].fill = CHK_FILL
    put(ws, 'B246', 'Check: FY26 NAV / unit vs valuer NAV (Rs. 90.79)', italic=True)
    put(ws, f'{G}246', f'={G}244-90.79', fmt=NUM2, fill=CHK_FILL)
