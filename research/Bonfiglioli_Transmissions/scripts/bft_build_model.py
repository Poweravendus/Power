"""Build BONFIG_Model_v1.xlsx (historicals) and BONFIG_Model_v2.xlsx (forecast) for Bonfiglioli Transmissions Ltd.
Usage: python3 bft_build_model.py <out_dir> [v1|v2|both]
Rs. crore unless stated (document Rs. million / 10). Fiscal year = calendar year (FY25A = year to 31-Dec-2025).
Colours: blue = input from documents, black = formula, green = link to another sheet, red = check, yellow fill = key driver.
"""
import sys, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bft_data as D

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
MODE = sys.argv[2] if len(sys.argv) > 2 else 'both'

BLUE, BLACK, GREEN, RED = '0000FF', '000000', '008000', 'FF0000'
YELLOW = PatternFill('solid', fgColor='FFFF00')
GREY = PatternFill('solid', fgColor='D9D9D9')
F = lambda color=BLACK, bold=False, italic=False: Font(name='Arial', size=9, color=color, bold=bold, italic=italic)
cr = lambda x: None if x is None else round(x / 10.0, 4)   # Rs mn -> Rs crore

HIST = ['B', 'C', 'D']                 # FY23A FY24A FY25A on P&L
FC = ['E', 'F', 'G', 'H', 'I']         # FY26E..FY30E on P&L
DRV = ['C', 'D', 'E', 'F', 'G']        # same years on Drivers
YRS = ['FY23A', 'FY24A', 'FY25A', 'FY26E', 'FY27E', 'FY28E', 'FY29E', 'FY30E']


def put(ws, ref, val, color=BLACK, bold=False, fmt=None, fill=None, italic=False, wrap=False):
    c = ws[ref]
    c.value = val
    c.font = F(color, bold, italic)
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    if wrap: c.alignment = Alignment(wrap_text=True, vertical='top')
    return c


def inp(ws, ref, val, fmt='#,##0.00', key=False):
    return put(ws, ref, val, BLUE, fmt=fmt, fill=YELLOW if key else None)


def fx(ws, ref, formula, fmt='#,##0.00', color=BLACK, bold=False):
    return put(ws, ref, formula, color, bold, fmt)


def header(ws, row, labels, start='B', bold=True):
    col = ord(start) - 64
    for i, l in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=l)
        c.font = F(BLACK, True); c.fill = GREY; c.alignment = Alignment(horizontal='center')


def label(ws, row, text, bold=False, color=BLACK, col='A', italic=False):
    put(ws, f'{col}{row}', text, color, bold, italic=italic)


def src(ws, row, text, col='J'):
    put(ws, f'{col}{row}', text, BLACK, italic=True)


def widths(ws, w):
    for k, v in w.items(): ws.column_dimensions[k].width = v


PCT = '0.0%'
NUM = '#,##0.0'
NUM2 = '#,##0.00'

# ====================================================================================================
def build(version):
    v2 = version == 'v2'
    wb = Workbook()
    pl = wb.active; pl.title = 'P&L'
    R = {}
    # ------------------------------------------------------------------ P&L
    put(pl, 'A1', 'Bonfiglioli Transmissions Ltd (NSE: BONFIG | BSE: 544996) - standalone, Rs. crore. Fiscal year = calendar year (FY25A = 12 months to 31-Dec-2025).', bold=True)
    put(pl, 'J1', 'Blue = document input, black = formula, green = link, red = check, yellow = key driver. Standalone is the only basis: the company has no subsidiaries (Pros p.253).', italic=True)
    header(pl, 2, YRS if v2 else YRS[:3]); put(pl, 'A2', 'P&L (restated, continuing operations)', bold=True); put(pl, 'J2', 'Source (printed pages)', bold=True)
    rows = ['rev', 'g', 'rm', 'inv', 'mat', 'matp', 'emp', 'roy', 'prof', 'othx', 'oth', 'ebitda', 'ebm', 'dep', 'ebit', 'oi', 'fin', 'pbt', 'tax', 'taxr',
            'patc', 'patd', 'pat', 'patm', 'sh', 'eps', 'div', 'payout', 'chk_e', 'chk_p', 'oneoff', 'ebitda_x']
    for i, k in enumerate(rows): R[k] = 3 + i
    L = {'rev': 'Revenue from operations', 'g': '  growth', 'rm': 'Cost of raw materials and components consumed', 'inv': 'Change in inventories of FG and WIP (+ = release)',
         'mat': 'Materials cost (raw materials + change in stock)', 'matp': '  materials cost % of revenue', 'emp': 'Employee benefits expense',
         'roy': 'Royalty to Bonfiglioli S.p.A. (6% of licensed-product sales)', 'prof': 'Professional fees (mainly group cost-sharing under the service agreement)',
         'othx': 'Other expenses (all other)', 'oth': 'Total other expenses', 'ebitda': 'EBITDA (excl. other income)', 'ebm': '  EBITDA margin',
         'dep': 'Depreciation and amortisation', 'ebit': 'EBIT', 'oi': 'Other income', 'fin': 'Finance costs', 'pbt': 'Profit before tax (continuing)',
         'tax': 'Tax expense', 'taxr': '  effective tax rate', 'patc': 'PAT from continuing operations', 'patd': 'PAT from discontinued operations (IT/R&D unit sold to group 2024)',
         'pat': 'PAT (reported)', 'patm': '  PAT margin (on revenue)', 'sh': 'Shares outstanding (crore, after 1:2 bonus Jan-2026)', 'eps': 'EPS, continuing (Rs., bonus-adjusted)',
         'div': 'Dividends paid (Rs. crore, cash)', 'payout': '  dividends paid / PAT', 'chk_e': 'CHECK: EBITDA vs company-reported EBITDA (should be 0)',
         'chk_p': 'CHECK: PBT built up vs reported PBT (should be 0)', 'oneoff': 'memo: one-off transfer-pricing income inside revenue', 'ebitda_x': 'memo: EBITDA excluding that one-off'}
    for k in rows: label(pl, R[k], L[k], bold=k in ('rev', 'ebitda', 'pat', 'eps'), color=RED if k.startswith('chk') else BLACK)
    for i, c in enumerate(HIST):
        inp(pl, f'{c}{R["rev"]}', cr(D.PL['rev'][0][i]))
        inp(pl, f'{c}{R["rm"]}', cr(D.PL['rm'][0][i]))
        inp(pl, f'{c}{R["inv"]}', cr(D.PL['inv_chg'][0][i]))
        fx(pl, f'{c}{R["mat"]}', f'={c}{R["rm"]}+{c}{R["inv"]}')
        inp(pl, f'{c}{R["emp"]}', cr(D.PL['emp'][0][i]))
        inp(pl, f'{c}{R["roy"]}', cr(D.PL['royalty'][0][i]))
        inp(pl, f'{c}{R["prof"]}', cr(D.PL['prof'][0][i]))
        inp(pl, f'{c}{R["othx"]}', round(cr(D.PL['oth_tot'][0][i]) - cr(D.PL['royalty'][0][i]) - cr(D.PL['prof'][0][i]), 4))
        fx(pl, f'{c}{R["dep"]}', None); inp(pl, f'{c}{R["dep"]}', cr(D.PL['dep'][0][i]))
        inp(pl, f'{c}{R["oi"]}', cr(D.PL['oi'][0][i]))
        inp(pl, f'{c}{R["fin"]}', cr(D.PL['fin'][0][i]))
        inp(pl, f'{c}{R["tax"]}', cr(D.PL['tax'][0][i]))
        inp(pl, f'{c}{R["patd"]}', cr(D.PL['pat_disc'][0][i]))
        inp(pl, f'{c}{R["sh"]}', round(D.SHARES_POST / 1e7, 6), fmt='0.0000')
        inp(pl, f'{c}{R["div"]}', cr(-D.CF['div'][0][i]))
        fx(pl, f'{c}{R["chk_e"]}', f'={c}{R["ebitda"]}-{cr(D.PL["ebitda_rep"][0][i])}', color=RED)
        fx(pl, f'{c}{R["chk_p"]}', f'={c}{R["pbt"]}-{cr(D.PL["pbt"][0][i])}', color=RED)
        inp(pl, f'{c}{R["oneoff"]}', cr(D.PL['tp_secadj'][0][i]))
    srcs = {'rev': D.PL['rev'][1], 'rm': D.PL['rm'][1], 'inv': D.PL['inv_chg'][1] + '. Sign: + = inventory release adds to cost.', 'emp': D.PL['emp'][1],
            'roy': D.PL['royalty'][1] + '; Pros RPT p.82 shows royalty paid to BSPA of 741.26/813.32/888.08 mn (small gap, recorded on Sources).',
            'prof': D.PL['prof'][1] + '; RPT p.79: BSPA 441.21/420.33/427.76 mn.', 'othx': 'Pros note 30 p.318: total other expenses less royalty and professional fees.',
            'dep': D.PL['dep'][1], 'oi': D.PL['oi'][1], 'fin': D.PL['fin'][1] + ' (mostly early-payment discount on receivables: no borrowings since Dec-2024)',
            'tax': D.PL['tax'][1], 'patd': D.PL['pat_disc'][1], 'sh': 'Pros p.287: 187,995,834 shares after 62,665,278 bonus shares (Jan-2026); OFS added no shares.', 'eps': 'EPS on today\'s 18.80 crore shares in every year (comparable per share). Company restated EPS 7.57 / 10.08 / 12.65 (Pros p.285) uses weighted shares before the May-2024 buyback; FY25 matches.',
            'div': 'Pros p.286 (cash flow); declared: FY23 655.60, FY24 689.30, FY25 927.45, H1FY26 1,099.78 mn (p.280).',
            'chk_e': 'Company EBITDA excl. other income: Pros p.209.', 'chk_p': 'Pros p.285.', 'oneoff': D.PL['tp_secadj'][1] + '; MD&A p.367, 372.'}
    for k, s in srcs.items(): src(pl, R[k], s)
    allc = HIST + (FC if v2 else [])
    for j, c in enumerate(allc):
        p = CL(ord(c) - 65) if c != 'B' else None
        if p: fx(pl, f'{c}{R["g"]}', f'={c}{R["rev"]}/{p}{R["rev"]}-1', PCT)
        fx(pl, f'{c}{R["matp"]}', f'={c}{R["mat"]}/{c}{R["rev"]}', PCT)
        fx(pl, f'{c}{R["oth"]}', f'={c}{R["roy"]}+{c}{R["prof"]}+{c}{R["othx"]}')
        fx(pl, f'{c}{R["ebitda"]}', f'={c}{R["rev"]}-{c}{R["mat"]}-{c}{R["emp"]}-{c}{R["oth"]}', bold=True)
        fx(pl, f'{c}{R["ebm"]}', f'={c}{R["ebitda"]}/{c}{R["rev"]}', PCT)
        fx(pl, f'{c}{R["ebit"]}', f'={c}{R["ebitda"]}-{c}{R["dep"]}')
        fx(pl, f'{c}{R["pbt"]}', f'={c}{R["ebit"]}+{c}{R["oi"]}-{c}{R["fin"]}')
        fx(pl, f'{c}{R["taxr"]}', f'={c}{R["tax"]}/{c}{R["pbt"]}', PCT)
        fx(pl, f'{c}{R["patc"]}', f'={c}{R["pbt"]}-{c}{R["tax"]}')
        fx(pl, f'{c}{R["pat"]}', f'={c}{R["patc"]}+{c}{R["patd"]}', bold=True)
        fx(pl, f'{c}{R["patm"]}', f'={c}{R["pat"]}/{c}{R["rev"]}', PCT)
        fx(pl, f'{c}{R["eps"]}', f'={c}{R["patc"]}/{c}{R["sh"]}', '0.00', bold=True)
        fx(pl, f'{c}{R["payout"]}', f'={c}{R["div"]}/{c}{R["pat"]}', PCT)
        fx(pl, f'{c}{R["ebitda_x"]}', f'={c}{R["ebitda"]}-{c}{R["oneoff"]}')

    # ---------------- Balance sheet ----------------
    b0 = R['ebitda_x'] + 2
    label(pl, b0, 'BALANCE SHEET (as at 31-Dec; restated)', bold=True); header(pl, b0, YRS if v2 else YRS[:3])
    bsr = ['nfa', 'onca', 'invy', 'recv', 'cash', 'oca', 'ta', 'scap', 'oeq', 'teq', 'borr', 'lease', 'tp', 'ol', 'tl', 'tel', 'chk_bs', 'chk_ta']
    for i, k in enumerate(bsr): R[k] = b0 + 1 + i
    BL = {'nfa': 'Net fixed assets (PPE + CWIP + intangibles + right-of-use)', 'onca': 'Other non-current assets (loans, deposits, deferred tax, tax)',
          'invy': 'Inventories', 'recv': 'Trade receivables', 'cash': 'Cash and bank balances (incl. deposits)', 'oca': 'Other current assets (loans, other financial, other)',
          'ta': 'Total assets', 'scap': 'Equity share capital', 'oeq': 'Other equity', 'teq': 'Total equity', 'borr': 'Borrowings', 'lease': 'Lease liabilities',
          'tp': 'Trade payables', 'ol': 'Other liabilities and provisions', 'tl': 'Total liabilities', 'tel': 'Total equity and liabilities',
          'chk_bs': 'CHECK: assets - equity and liabilities (should be 0)', 'chk_ta': 'CHECK: total assets vs reported total assets (history)'}
    for k in bsr: label(pl, R[k], BL[k], bold=k in ('ta', 'teq', 'tel'), color=RED if k.startswith('chk') else BLACK)
    # detail block (history inputs)
    d0 = 140
    label(pl, d0, 'Balance sheet detail (history inputs, Rs. crore) - Pros p.284', bold=True); header(pl, d0, YRS[:3])
    det = [('ppe', 'Property, plant and equipment'), ('cwip', 'Capital work-in-progress'), ('intang', 'Intangible assets'), ('iaud', 'Intangibles under development'),
           ('rou', 'Right-of-use asset'), ('inv_nc', 'Investments'), ('loan_nc', 'Loans (non-current, to BTSPL)'), ('ofa_nc', 'Other financial assets (NC)'),
           ('dta', 'Deferred tax assets'), ('nctax', 'Non-current tax assets'), ('onca', 'Other non-current assets'), ('inventory', 'Inventories'),
           ('recv', 'Trade receivables'), ('cash', 'Cash and cash equivalents'), ('bank', 'Other bank balances (deposits)'), ('loan_c', 'Loans (current, to BTSPL)'),
           ('ofa_c', 'Other financial assets (current)'), ('ctax_a', 'Current tax assets'), ('oca', 'Other current assets'), ('sharecap', 'Equity share capital'),
           ('oeq', 'Other equity'), ('borrow', 'Borrowings'), ('lease_nc', 'Lease liabilities (NC)'), ('lease_c', 'Lease liabilities (current)'),
           ('tp_msme', 'Trade payables - MSME'), ('tp_oth', 'Trade payables - others'), ('ofl_nc', 'Other financial liabilities (NC)'), ('prov_nc', 'Provisions (NC)'),
           ('contract', 'Contract liabilities'), ('ofl_c', 'Other financial liabilities (current)'), ('ctax_l', 'Current tax liability'), ('ocl', 'Other current liabilities'),
           ('prov_c', 'Provisions (current)'), ('total_assets', 'Reported total assets')]
    DR = {}
    for i, (k, t) in enumerate(det):
        r = d0 + 1 + i; DR[k] = r; label(pl, r, t)
        for j, c in enumerate(HIST): inp(pl, f'{c}{r}', cr(D.BS[k][j]))
        src(pl, r, D.BS_SRC)
    s = lambda c, ks: '=' + '+'.join(f'{c}{DR[k]}' for k in ks)
    for c in HIST:
        fx(pl, f'{c}{R["nfa"]}', s(c, ['ppe', 'cwip', 'intang', 'iaud', 'rou']))
        fx(pl, f'{c}{R["onca"]}', s(c, ['inv_nc', 'loan_nc', 'ofa_nc', 'dta', 'nctax', 'onca']))
        fx(pl, f'{c}{R["invy"]}', f'={c}{DR["inventory"]}'); fx(pl, f'{c}{R["recv"]}', f'={c}{DR["recv"]}')
        fx(pl, f'{c}{R["cash"]}', s(c, ['cash', 'bank'])); fx(pl, f'{c}{R["oca"]}', s(c, ['loan_c', 'ofa_c', 'ctax_a', 'oca']))
        fx(pl, f'{c}{R["scap"]}', f'={c}{DR["sharecap"]}'); fx(pl, f'{c}{R["oeq"]}', f'={c}{DR["oeq"]}')
        fx(pl, f'{c}{R["borr"]}', f'={c}{DR["borrow"]}'); fx(pl, f'{c}{R["lease"]}', s(c, ['lease_nc', 'lease_c']))
        fx(pl, f'{c}{R["tp"]}', s(c, ['tp_msme', 'tp_oth'])); fx(pl, f'{c}{R["ol"]}', s(c, ['ofl_nc', 'prov_nc', 'contract', 'ofl_c', 'ctax_l', 'ocl', 'prov_c']))
        fx(pl, f'{c}{R["chk_ta"]}', f'={c}{R["ta"]}-{c}{DR["total_assets"]}', color=RED)
    for c in allc:
        fx(pl, f'{c}{R["ta"]}', f'={c}{R["nfa"]}+{c}{R["onca"]}+{c}{R["invy"]}+{c}{R["recv"]}+{c}{R["cash"]}+{c}{R["oca"]}', bold=True)
        fx(pl, f'{c}{R["teq"]}', f'={c}{R["scap"]}+{c}{R["oeq"]}', bold=True)
        fx(pl, f'{c}{R["tl"]}', f'={c}{R["borr"]}+{c}{R["lease"]}+{c}{R["tp"]}+{c}{R["ol"]}')
        fx(pl, f'{c}{R["tel"]}', f'={c}{R["teq"]}+{c}{R["tl"]}', bold=True)
        fx(pl, f'{c}{R["chk_bs"]}', f'={c}{R["ta"]}-{c}{R["tel"]}', color=RED)
    src(pl, R['nfa'], 'Sum of detail rows below (Pros p.284). Forecast: opening + capex - D&A.')
    src(pl, R['cash'], 'Cash and cash equivalents + other bank balances. Forecast: the plug (= equity and liabilities less all other assets).')

    # ---------------- Cash flow ----------------
    c0 = R['chk_ta'] + 2
    label(pl, c0, 'CASH FLOW', bold=True); header(pl, c0, YRS if v2 else YRS[:3])
    cfr = ['cf_pat', 'cf_dep', 'cf_wc', 'cfo', 'capex', 'fcf', 'cf_onca', 'cf_div', 'cf_bb', 'cf_borr', 'cf_lease', 'cf_oth', 'cf_net', 'cf_close', 'chk_cf']
    for i, k in enumerate(cfr): R[k] = c0 + 1 + i
    CLB = {'cf_pat': 'PAT', 'cf_dep': 'Depreciation and amortisation', 'cf_wc': 'Change in working capital (history: after tax paid adjustments)', 'cfo': 'Cash from operations (CFO)',
           'capex': 'Capex (purchase of PPE and intangibles)', 'fcf': 'Free cash flow (CFO - capex)', 'cf_onca': 'Change in other non-current assets',
           'cf_div': 'Dividends paid', 'cf_bb': 'Share buyback', 'cf_borr': 'Net borrowings', 'cf_lease': 'Lease payments (principal)',
           'cf_oth': 'Other (deposits, interest received, loans to group, BDSPL adjustments)', 'cf_net': 'Net change in cash', 'cf_close': 'Closing cash (history: cash equivalents only; forecast: cash and bank)',
           'chk_cf': 'CHECK: closing cash vs balance sheet (should be 0)'}
    for k in cfr: label(pl, R[k], CLB[k], bold=k in ('cfo', 'fcf'), color=RED if k == 'chk_cf' else BLACK)
    for j, c in enumerate(HIST):
        fx(pl, f'{c}{R["cf_pat"]}', f'={c}{R["pat"]}')
        fx(pl, f'{c}{R["cf_dep"]}', f'={c}{R["dep"]}')
        inp(pl, f'{c}{R["cfo"]}', cr(D.CF['cfo'][0][j]))
        fx(pl, f'{c}{R["cf_wc"]}', f'={c}{R["cfo"]}-{c}{R["cf_pat"]}-{c}{R["cf_dep"]}')
        inp(pl, f'{c}{R["capex"]}', cr(D.CF['capex'][0][j]))
        inp(pl, f'{c}{R["cf_div"]}', cr(D.CF['div'][0][j])); inp(pl, f'{c}{R["cf_bb"]}', cr(D.CF['buyback'][0][j]))
        inp(pl, f'{c}{R["cf_borr"]}', cr(D.CF['net_borrow'][0][j]))
        inp(pl, f'{c}{R["cf_net"]}', cr(D.CF['net_chg'][0][j]))
        fx(pl, f'{c}{R["cf_oth"]}', f'={c}{R["cf_net"]}-{c}{R["cfo"]}-{c}{R["capex"]}-{c}{R["cf_div"]}-{c}{R["cf_bb"]}-{c}{R["cf_borr"]}')
        inp(pl, f'{c}{R["cf_close"]}', cr(D.CF['cash_close'][0][j]))
        fx(pl, f'{c}{R["chk_cf"]}', f'={c}{R["cf_close"]}-{c}{DR["cash"]}', color=RED)
    for c in allc: fx(pl, f'{c}{R["fcf"]}', f'={c}{R["cfo"]}+{c}{R["capex"]}', bold=True)
    src(pl, R['cfo'], 'Pros p.286 (restated cash flow); CFO includes discontinued operations.')
    src(pl, R['capex'], D.CF['capex'][1]); src(pl, R['cf_div'], D.CF['div'][1]); src(pl, R['cf_bb'], D.CF['buyback'][1])
    src(pl, R['cf_net'], D.CF['net_chg'][1]); src(pl, R['cf_close'], 'Pros p.286; forecast includes other bank balances.')

    # ---------------- Ratios ----------------
    r0 = R['chk_cf'] + 2
    label(pl, r0, 'WORKING CAPITAL AND RATIOS', bold=True); header(pl, r0, YRS if v2 else YRS[:3])
    rr = ['rdays', 'idays', 'pdays', 'nwc', 'nwcp', 'netcash', 'roe', 'roce', 'fat', 'cfo_e', 'fcf_p', 'cash_ret', 'grp_drain', 'capex_rev']
    for i, k in enumerate(rr): R[k] = r0 + 1 + i
    RL = {'rdays': 'Receivable days (on revenue)', 'idays': 'Inventory days (on materials cost)', 'pdays': 'Payable days (on materials cost)',
          'nwc': 'Net working capital (inventory + receivables + other CA - payables - other liabilities)', 'nwcp': '  NWC % of revenue',
          'netcash': 'Net cash (cash and bank - borrowings - leases)', 'roe': 'ROE (PAT / average equity)', 'roce': 'ROCE (EBIT / average equity + debt + leases)',
          'fat': 'Fixed asset turnover (revenue / net fixed assets)', 'cfo_e': 'CFO / EBITDA', 'fcf_p': 'FCF / PAT', 'cash_ret': 'Dividends + buyback / PAT',
          'grp_drain': 'Royalty + group fees % of revenue', 'capex_rev': 'Capex % of revenue'}
    for k in rr: label(pl, R[k], RL[k])
    for j, c in enumerate(allc):
        p = CL(ord(c) - 65) if c != 'B' else None
        fx(pl, f'{c}{R["rdays"]}', f'={c}{R["recv"]}/{c}{R["rev"]}*365', '0')
        fx(pl, f'{c}{R["idays"]}', f'={c}{R["invy"]}/{c}{R["mat"]}*365', '0')
        fx(pl, f'{c}{R["pdays"]}', f'={c}{R["tp"]}/{c}{R["mat"]}*365', '0')
        fx(pl, f'{c}{R["nwc"]}', f'={c}{R["invy"]}+{c}{R["recv"]}+{c}{R["oca"]}-{c}{R["tp"]}-{c}{R["ol"]}')
        fx(pl, f'{c}{R["nwcp"]}', f'={c}{R["nwc"]}/{c}{R["rev"]}', PCT)
        fx(pl, f'{c}{R["netcash"]}', f'={c}{R["cash"]}-{c}{R["borr"]}-{c}{R["lease"]}')
        if p:
            fx(pl, f'{c}{R["roe"]}', f'={c}{R["patc"]}/AVERAGE({p}{R["teq"]},{c}{R["teq"]})', PCT)
            fx(pl, f'{c}{R["roce"]}', f'={c}{R["ebit"]}/AVERAGE({p}{R["teq"]}+{p}{R["borr"]}+{p}{R["lease"]},{c}{R["teq"]}+{c}{R["borr"]}+{c}{R["lease"]})', PCT)
        fx(pl, f'{c}{R["fat"]}', f'={c}{R["rev"]}/{c}{R["nfa"]}', '0.0')
        fx(pl, f'{c}{R["cfo_e"]}', f'={c}{R["cfo"]}/{c}{R["ebitda"]}', PCT)
        fx(pl, f'{c}{R["fcf_p"]}', f'={c}{R["fcf"]}/{c}{R["pat"]}', PCT)
        fx(pl, f'{c}{R["cash_ret"]}', f'=-({c}{R["cf_div"]}+{c}{R["cf_bb"]})/{c}{R["pat"]}', PCT)
        fx(pl, f'{c}{R["grp_drain"]}', f'=({c}{R["roy"]}+{c}{R["prof"]})/{c}{R["rev"]}', PCT)
        fx(pl, f'{c}{R["capex_rev"]}', f'=-{c}{R["capex"]}/{c}{R["rev"]}', PCT)
    src(pl, R['rdays'], 'Company reports 89/80/94 days (Pros p.210, same basis).')
    src(pl, R['roe'], 'Company ROE 19.21/23.05/25.66% (Pros p.209-210).')

    # ================================================================ Quarterly
    q = wb.create_sheet('Quarterly')
    put(q, 'A1', 'Quarterly and half-year results, Rs. crore (unaudited quarters; Q3FY25 and 9MFY25 restated for the BDSPL business, Res p.2 notes 5 and 7)', bold=True)
    qcols = ['Q3FY25', 'Q4FY25 (derived)', 'Q1FY26 (derived)', 'Q2FY26', 'Q3FY26', 'H1FY25', 'H1FY26', '9MFY25', '9MFY26']
    header(q, 2, qcols); put(q, 'K2', 'Source', bold=True)
    qr = ['rev', 'rm', 'inv', 'mat', 'emp', 'oth', 'ebitda', 'ebm', 'dep', 'oi', 'fin', 'pbt', 'tax', 'pat', 'patm', 'eps', 'yoy_rev', 'yoy_pat',
          'v_ia', 'v_ohm', 'v_wind', 'v_oth', 'chk_q', 'gap_rev', 'gap_pat', 'roy', 'prof']
    QR = {k: 3 + i for i, k in enumerate(qr)}
    QL = {'rev': 'Revenue from operations', 'rm': 'Raw materials consumed', 'inv': 'Change in inventories (+ = release)', 'mat': 'Materials cost', 'emp': 'Employee cost',
          'oth': 'Other expenses', 'ebitda': 'EBITDA (excl. other income)', 'ebm': '  EBITDA margin', 'dep': 'Depreciation', 'oi': 'Other income', 'fin': 'Finance costs',
          'pbt': 'PBT', 'tax': 'Tax', 'pat': 'PAT', 'patm': '  PAT margin', 'eps': 'EPS (Rs., not annualised)', 'yoy_rev': 'Revenue growth YoY', 'yoy_pat': 'PAT growth YoY',
          'v_ia': 'Industry & Automation revenue', 'v_ohm': 'Off-Highway Mobility revenue', 'v_wind': 'Wind revenue', 'v_oth': 'Others (scrap, incentives, components)',
          'chk_q': 'CHECK: Q1FY26 + Q2FY26 = H1FY26; Q4FY25 + 9MFY25 = FY25 (should be 0)',
          'gap_rev': 'memo: H1FY25 (Prospectus) + Q3FY25 (results) less 9MFY25 (results) - revenue', 'gap_pat': 'memo: same gap - PAT (company says Q3FY25 is a balancing figure after subsequent-event adjustments)',
          'roy': 'Royalty (H1 only, Pros note 30)', 'prof': 'Professional fees (H1 only)'}
    for k in qr: label(q, QR[k], QL[k], bold=k in ('rev', 'ebitda', 'pat'), color=RED if k == 'chk_q' else BLACK)
    # inputs: B Q3FY25, E Q2FY26, F Q3FY26, I 9MFY25, J 9MFY26 from Res; G H1FY25, H H1FY26 from Pros
    qmap = {'B': 0, 'E': 1, 'F': 2, 'I': 3, 'J': 4}
    for c, i in qmap.items():
        for k, dk in [('rev', 'rev'), ('rm', 'rm'), ('inv', 'inv_chg'), ('emp', 'emp'), ('oth', 'oth'), ('dep', 'dep'), ('oi', 'oi'), ('fin', 'fin'), ('tax', 'tax')]:
            inp(q, f'{c}{QR[k]}', cr(D.Q[dk][i]))
        inp(q, f'{c}{QR["eps"]}', D.Q['eps'][i])
    for c, i in {'G': 0, 'H': 1}.items():
        for k, dk in [('rev', 'rev'), ('rm', 'rm'), ('inv', 'inv_chg'), ('emp', 'emp'), ('oth', 'oth'), ('dep', 'dep'), ('oi', 'oi'), ('fin', 'fin'), ('tax', 'tax'),
                      ('roy', 'royalty'), ('prof', 'prof')]:
            inp(q, f'{c}{QR[k]}', cr(D.H1[dk][i]))
        fx(q, f'{c}{QR["eps"]}', f'={c}{QR["pat"]}/\'P&L\'!D{R["sh"]}', '0.00', color=GREEN)
    # derived quarters
    for k in ['rev', 'rm', 'inv', 'emp', 'oth', 'dep', 'oi', 'fin', 'tax']:
        fx(q, f'C{QR[k]}', f"='P&L'!D{R[{'inv':'inv'}.get(k,k)] if k!='oth' else R['oth']}-I{QR[k]}", color=GREEN)
        fx(q, f'D{QR[k]}', f'=H{QR[k]}-E{QR[k]}')
    fx(q, f'C{QR["eps"]}', f'=C{QR["pat"]}/\'P&L\'!D{R["sh"]}', '0.00', color=GREEN)
    fx(q, f'D{QR["eps"]}', f'=D{QR["pat"]}/\'P&L\'!D{R["sh"]}', '0.00', color=GREEN)
    for c in 'BCDEFGHIJ':
        fx(q, f'{c}{QR["mat"]}', f'={c}{QR["rm"]}+{c}{QR["inv"]}')
        fx(q, f'{c}{QR["ebitda"]}', f'={c}{QR["rev"]}-{c}{QR["mat"]}-{c}{QR["emp"]}-{c}{QR["oth"]}', bold=True)
        fx(q, f'{c}{QR["ebm"]}', f'={c}{QR["ebitda"]}/{c}{QR["rev"]}', PCT)
        fx(q, f'{c}{QR["pbt"]}', f'={c}{QR["ebitda"]}-{c}{QR["dep"]}+{c}{QR["oi"]}-{c}{QR["fin"]}')
        fx(q, f'{c}{QR["pat"]}', f'={c}{QR["pbt"]}-{c}{QR["tax"]}', bold=True)
        fx(q, f'{c}{QR["patm"]}', f'={c}{QR["pat"]}/{c}{QR["rev"]}', PCT)
    fx(q, f'F{QR["yoy_rev"]}', f'=F{QR["rev"]}/B{QR["rev"]}-1', PCT); fx(q, f'F{QR["yoy_pat"]}', f'=F{QR["pat"]}/B{QR["pat"]}-1', PCT)
    fx(q, f'H{QR["yoy_rev"]}', f'=H{QR["rev"]}/G{QR["rev"]}-1', PCT); fx(q, f'H{QR["yoy_pat"]}', f'=H{QR["pat"]}/G{QR["pat"]}-1', PCT)
    fx(q, f'J{QR["yoy_rev"]}', f'=J{QR["rev"]}/I{QR["rev"]}-1', PCT); fx(q, f'J{QR["yoy_pat"]}', f'=J{QR["pat"]}/I{QR["pat"]}-1', PCT)
    # verticals: Q3FY25 (B), Q3FY26 (F), H1 (G,H), 9M (I,J)
    for k, dk in [('v_ia', 'ia'), ('v_ohm', 'ohm'), ('v_wind', 'wind')]:
        vals = D.VERT[dk]
        inp(q, f'G{QR[k]}', cr(vals[3])); inp(q, f'H{QR[k]}', cr(vals[4])); inp(q, f'I{QR[k]}', cr(vals[5])); inp(q, f'J{QR[k]}', cr(vals[6]))
        inp(q, f'B{QR[k]}', cr(vals[7])); inp(q, f'F{QR[k]}', cr(vals[8]))
        fx(q, f'C{QR[k]}', f"=Segments!D{5 + ['v_ia','v_ohm','v_wind'].index(k)}-I{QR[k]}", color=GREEN)
    inp(q, f'G{QR["v_oth"]}', cr(D.VERT['oth'][3])); inp(q, f'H{QR["v_oth"]}', cr(D.VERT['oth'][4]))
    for c in 'BCFIJ': fx(q, f'{c}{QR["v_oth"]}', f'={c}{QR["rev"]}-{c}{QR["v_ia"]}-{c}{QR["v_ohm"]}-{c}{QR["v_wind"]}')
    fx(q, f'B{QR["chk_q"]}', f'=ABS(D{QR["rev"]}+E{QR["rev"]}-H{QR["rev"]})+ABS(D{QR["pat"]}+E{QR["pat"]}-H{QR["pat"]})+ABS(C{QR["rev"]}+I{QR["rev"]}-\'P&L\'!D{R["rev"]})+ABS(C{QR["pat"]}+I{QR["pat"]}-\'P&L\'!D{R["patc"]})', color=RED)
    fx(q, f'B{QR["gap_rev"]}', f'=G{QR["rev"]}+B{QR["rev"]}-I{QR["rev"]}'); fx(q, f'B{QR["gap_pat"]}', f'=G{QR["pat"]}+B{QR["pat"]}-I{QR["pat"]}')
    put(q, f'K{QR["rev"]}', 'Q3FY25, Q2FY26, Q3FY26, 9MFY25, 9MFY26: Res p.1. H1: Pros p.285. Q4FY25 = FY25 (Pros p.285) - 9MFY25. Q1FY26 = H1FY26 - Q2FY26.', italic=True)
    put(q, f'K{QR["v_ia"]}', 'H1: Pros p.207. Q3 and 9M: PPT slides 7-8 (Rs. mn, rounded). Q4FY25 = FY25 (Segments) - 9MFY25.', italic=True)
    put(q, f'K{QR["gap_rev"]}', 'Not a model error: the Prospectus H1FY25 plus the results Q3FY25 do not add to the results 9MFY25 (revenue gap = the Rs.8.0 cr transfer-pricing one-off; PAT gap ~Rs.10.5 cr). The 9MFY26 PAT growth of 40.7% is on the lower 9MFY25 base; on H1+Q3 it is ~32%.', italic=True)
    put(q, f'K{QR["eps"]}', 'Res p.1 (Q, 9M); H1 = PAT / 18.80 crore shares.', italic=True)
    widths(q, {'A': 58, **{c: 11 for c in 'BCDEFGHIJ'}, 'K': 90})

    # ================================================================ Segments
    sg = wb.create_sheet('Segments')
    put(sg, 'A1', 'Segment and operating data, Rs. crore unless stated (the company reports one Ind AS 108 segment; vertical data are management splits in the Prospectus and PPT)', bold=True)
    scol = ['FY23A', 'FY24A', 'FY25A', 'H1FY25', 'H1FY26'] + (['FY26E', 'FY27E', 'FY28E', 'FY29E', 'FY30E'] if v2 else [])
    header(sg, 3, scol); put(sg, 'A3', 'A. Revenue by vertical', bold=True); put(sg, 'L3' if v2 else 'G3', 'Source', bold=True)
    SC = ['B', 'C', 'D', 'E', 'F']; SF = ['G', 'H', 'I', 'J', 'K']
    srcol = 'L' if v2 else 'G'
    S = {}
    rowsS = [('ia', 'Industry & Automation (I&A)'), ('ohm', 'Off-Highway Mobility (OHM)'), ('wind', 'Wind (yaw and pitch drives)'), ('oth', 'Others (scrap, incentives, components)')]
    for i, (k, t) in enumerate(rowsS):
        r = 5 + i; S[k] = r; label(sg, r, t)
        for j in range(5): inp(sg, f'{SC[j]}{r}', cr(D.VERT[k][j]))
        put(sg, f'{srcol}{r}', 'Pros p.207 / p.219-220', italic=True)
    S['hd_new'] = 9; label(sg, 9, 'New heavy-duty plant, Talegaon (forecast only)')
    S['tot'] = 10; label(sg, 10, 'Total revenue from operations', bold=True)
    S['chk'] = 11; label(sg, 11, 'CHECK: verticals vs P&L revenue (should be 0)', color=RED)
    for j, c in enumerate(SC):
        fx(sg, f'{c}10', f'=SUM({c}5:{c}9)', bold=True)
    for j, c in enumerate(SC[:3]): fx(sg, f'{c}11', f"={c}10-'P&L'!{HIST[j]}{R['rev']}", color=RED)
    fx(sg, 'E11', f"=E10-Quarterly!G{QR['rev']}", color=RED); fx(sg, 'F11', f"=F10-Quarterly!H{QR['rev']}", color=RED)
    S['g0'] = 12
    for i, (k, t) in enumerate(rowsS[:3]):
        r = 12 + i; label(sg, r, f'  growth: {t.split(" (")[0]}')
        for j, c in enumerate(['C', 'D']): fx(sg, f'{c}{r}', f'={c}{S[k]}/{CL(ord(c)-65)}{S[k]}-1', PCT)
        fx(sg, f'F{r}', f'=F{S[k]}/E{S[k]}-1', PCT)
    S['mix0'] = 15
    for i, (k, t) in enumerate(rowsS[:3]):
        r = 15 + i; label(sg, r, f'  share of revenue: {t.split(" (")[0]}')
        for c in SC: fx(sg, f'{c}{r}', f'={c}{S[k]}/{c}10', PCT)
    # I&A split
    label(sg, 19, 'B. Industry & Automation split (Pros p.222)', bold=True)
    label(sg, 20, 'Low and medium-duty gear motors (<15 kNm)'); label(sg, 21, 'Heavy-duty gearboxes (existing, inside I&A)'); label(sg, 22, '  heavy-duty share of I&A')
    for j in range(5):
        inp(sg, f'{SC[j]}20', cr(D.IA_SPLIT['lmd'][j])); inp(sg, f'{SC[j]}21', cr(D.IA_SPLIT['hd'][j])); fx(sg, f'{SC[j]}22', f'={SC[j]}21/({SC[j]}20+{SC[j]}21)', PCT)
    put(sg, f'{srcol}20', 'Pros p.222', italic=True)
    # product
    label(sg, 24, 'C. Product mix of revenue from contracts (Pros note 36 p.322)', bold=True)
    for i, (k, t) in enumerate([('gearbox', 'Gearboxes'), ('gearmotor', 'Gear motors'), ('others', 'Others (spares, motors, inverters)')]):
        r = 25 + i; label(sg, r, t)
        for j in range(5): inp(sg, f'{SC[j]}{r}', cr(D.PRODUCT[k][j]))
    # geography
    label(sg, 29, 'D. Geography of revenue from contracts (Pros p.227-228, note 36 p.322)', bold=True)
    for i, k in enumerate(D.GEO):
        r = 30 + i; label(sg, r, k)
        for j in range(5): inp(sg, f'{SC[j]}{r}', cr(D.GEO[k][j]))
    label(sg, 36, 'Total revenue from contracts', bold=True); label(sg, 37, '  exports share'); label(sg, 38, '  USA share of revenue from contracts')
    label(sg, 39, 'CHECK: geography sum vs reported total (should be 0)', color=RED)
    for j, c in enumerate(SC):
        fx(sg, f'{c}36', f'=SUM({c}30:{c}35)', bold=True); fx(sg, f'{c}37', f'=1-{c}30/{c}36', PCT); fx(sg, f'{c}38', f'={c}31/{c}36', PCT)
        fx(sg, f'{c}39', f'={c}36-{cr(D.GEO_TOT[j])}', color=RED)
    # channel
    label(sg, 41, 'E. Sales channel (Pros p.208, p.228; FY24 inter-company 2,775.09 mn per p.228 - p.208 prints 2,755.09, which does not add up; see Sources)', bold=True)
    for i, (k, t) in enumerate([('dealer', 'Dealer sales (I&A)'), ('direct', 'Direct sales to OEMs'), ('interco', 'Inter-company sales to Bonfiglioli group'), ('others', 'Others')]):
        r = 42 + i; label(sg, r, t)
        for j in range(5): inp(sg, f'{SC[j]}{r}', cr(D.CHANNEL[k][j]))
    label(sg, 46, '  inter-company share of revenue');
    for c in SC: fx(sg, f'{c}46', f'={c}44/{c}10', PCT)
    label(sg, 47, 'CHECK: channel sum vs revenue (should be 0)', color=RED)
    for c in SC: fx(sg, f'{c}47', f'=SUM({c}42:{c}45)-{c}10', color=RED)
    # capacity
    label(sg, 48, 'F. Capacity (machine hours) and utilisation by plant (Pros p.233)', bold=True)
    caprows = [('tmv_ms', 'Thirumudivakkam machine shop (OHM, Wind)'), ('tmv_as', 'Thirumudivakkam assembly (OHM, Wind)'), ('man_as', 'Mannur assembly (I&A)'),
               ('man_ms', 'Mannur machine shop (from BDSPL, Dec-2025)'), ('tal_as', 'Talegaon (Pune) assembly (I&A)')]
    r = 49
    for k, t in caprows:
        label(sg, r, t + ' - available hours'); label(sg, r + 1, t + ' - utilised hours'); label(sg, r + 2, '  utilisation')
        for j in range(5):
            inp(sg, f'{SC[j]}{r}', D.CAP[k + '_av'][j], '#,##0'); inp(sg, f'{SC[j]}{r+1}', D.CAP[k + '_ut'][j], '#,##0')
            fx(sg, f'{SC[j]}{r+2}', f'=IFERROR({SC[j]}{r+1}/{SC[j]}{r},0)', PCT)
        r += 3
    S['cap_av'] = r; S['cap_ut'] = r + 1; S['cap_u'] = r + 2
    label(sg, r, 'Total available hours', bold=True); label(sg, r + 1, 'Total utilised hours', bold=True); label(sg, r + 2, '  aggregate utilisation (company: 64.22% FY23, 73.71% FY25, 75.04% H1FY26, p.216)')
    for c in SC:
        fx(sg, f'{c}{r}', f'={c}49+{c}52+{c}55+{c}58+{c}61', '#,##0'); fx(sg, f'{c}{r+1}', f'={c}50+{c}53+{c}56+{c}59+{c}62', '#,##0')
        fx(sg, f'{c}{r+2}', f'={c}{r+1}/{c}{r}', PCT)
    r += 4
    S['ops0'] = r
    label(sg, r, 'G. People, units, concentration', bold=True)
    ops = [('Employees on roll (period end)', D.EMP['onroll'], 'Pros p.239', '#,##0'), ('Total headcount incl. contract (period end)', D.EMP['headcount'], 'Pros p.373 (968, 987), p.370 (943 Jun-25, 1,032 Jun-26)', '#,##0'),
           ('SKUs produced', D.SKUS['produced'], 'Pros p.233', '#,##0'), ('Top-10 customers % of revenue from contracts', [x / 100 for x in D.TOP10_CUST], 'Pros p.230 (p.207 text says "less than 31.72%" in every period - contradicts this table)', PCT),
           ('Largest customer % (GE Vernova per Call p.11)', [x / 100 for x in D.TOP1_CUST], 'Pros p.27, p.229', PCT), ('Domestic share of raw materials consumed', [x / 100 for x in D.DOMESTIC_PURCH], 'Pros p.237', PCT)]
    S['emp_onroll'] = r + 1; S['headcount'] = r + 2
    for i, (t, vals, s_, fm) in enumerate(ops):
        rr_ = r + 1 + i; label(sg, rr_, t); put(sg, f'{srcol}{rr_}', s_, italic=True)
        for j in range(5):
            if vals[j] is not None: inp(sg, f'{SC[j]}{rr_}', vals[j], fm)
    S['units'] = r + 7; label(sg, S['units'], 'Gear motors and gearboxes manufactured (units)'); inp(sg, f'D{S["units"]}', D.UNITS_FY25, '#,##0'); put(sg, f'{srcol}{S["units"]}', 'Pros p.209 (FY25 only; no other year disclosed)', italic=True)
    widths(sg, {'A': 62, **{c: 11 for c in 'BCDEFGHIJK'}, srcol: 70})

    # ================================================================ Group vs third party
    gp = wb.create_sheet('Group_vs_ThirdParty')
    put(gp, 'A1', 'Group vs third-party: where the revenue comes from and where the money goes (Rs. crore unless stated)', bold=True)
    put(gp, 'A2', 'The parent (Bonfiglioli S.p.A., Italy) owns the IP and the brand, sells BTL parts, buys BTL products for its own sales companies, charges royalty and service fees and receives dividends. Margins by customer type are NOT disclosed: section D is a sensitivity, not a fact.', italic=True)
    header(gp, 4, ['FY23A', 'FY24A', 'FY25A', 'H1FY25', 'H1FY26']); put(gp, 'G4', 'Source', bold=True)
    put(gp, 'A4', 'A. Revenue: group vs third party', bold=True)
    GC = ['B', 'C', 'D', 'E', 'F']
    G = {}
    def grow(r, t, vals=None, f=None, fm=NUM2, s_=None, bold=False, color=BLACK):
        label(gp, r, t, bold=bold, color=color)
        for j, c in enumerate(GC):
            if vals is not None and vals[j] is not None: inp(gp, f'{c}{r}', vals[j], fm)
            elif f is not None: fx(gp, f'{c}{r}', f(c, j), fm, color=color)
        if s_: put(gp, f'G{r}', s_, italic=True)
    grow(5, 'Revenue from operations', f=lambda c, j: f'=Segments!{c}10', s_='Segments sheet')
    for c in GC: gp[f'{c}5'].font = F(GREEN)
    grow(6, 'Inter-company sales to Bonfiglioli group companies', f=lambda c, j: f'=Segments!{c}44', s_='Pros p.208 (sale of finished goods, e.g. yaw and swing drives, for onward sale)')
    for c in GC: gp[f'{c}6'].font = F(GREEN)
    grow(7, 'Third-party revenue', f=lambda c, j: f'={c}5-{c}6', bold=True)
    grow(8, '  group share of revenue', f=lambda c, j: f'={c}6/{c}5', fm=PCT)
    grow(9, 'Exports (revenue from contracts outside India)', f=lambda c, j: f'=Segments!{c}36-Segments!{c}30', s_='Pros p.227-228')
    grow(10, '  of which to group companies (= inter-company sales)', f=lambda c, j: f'={c}6')
    grow(11, '  of which to third parties abroad (mainly GE Vernova, USA)', f=lambda c, j: f'={c}9-{c}10')
    grow(12, '  group share of exports', f=lambda c, j: f'={c}10/{c}9', fm=PCT)
    label(gp, 13, 'Call p.10 (13-Nov-2026): "Exports to group entities around 21%, and 30.6% is the total exports" (9MFY26).', italic=True)
    put(gp, 'A15', 'B. FY25 sales to group companies by entity (Pros RPT summary p.73-75)', bold=True)
    for i, (n, v) in enumerate(D.GROUP_SALES_FY25):
        label(gp, 16 + i, n); inp(gp, f'D{16+i}', cr(v))
    rg = 16 + len(D.GROUP_SALES_FY25)
    label(gp, rg, 'Sum of entity sales', bold=True); fx(gp, f'D{rg}', f'=SUM(D16:D{rg-1})', bold=True)
    label(gp, rg + 1, 'CHECK-ish: entity sum vs channel inter-company (difference = classification; not forced to 0)', color=RED); fx(gp, f'D{rg+1}', f'=D{rg}-D6', color=RED)
    label(gp, rg + 2, 'USA: total vs Bonfiglioli USA -> third-party US (GE)'); fx(gp, f'D{rg+2}', f'=Segments!D31-D16')
    label(gp, rg + 3, 'Germany: total vs Bonfiglioli Deutschland (all of it is group)'); fx(gp, f'D{rg+3}', f'=Segments!D33-D18')
    g0 = rg + 5
    put(gp, f'A{g0}', 'C. Money paid to / received from the group', bold=True); header(gp, g0, ['FY23A', 'FY24A', 'FY25A', 'H1FY25', 'H1FY26'])
    pays = [('Royalty to BSPA (licence, 6% of licensed-product sales)', 'royalty_bspa', 'Pros p.82'), ('Service fees to BSPA (intercompany service agreement)', 'prof_bspa', 'Pros p.79'),
            ('Sales commission to Bonfiglioli USA', 'sales_commission_usa', 'Pros p.80'), ('Purchases from Bonfiglioli Riduttori (largest supplier)', 'purch_riduttori', 'Pros p.79'),
            ('Dividends to BSPA (paid/payable)', 'dividend_bspa', 'Pros p.82'), ('Buyback from group (BSPA 32.45 + Vectron 39.55)', 'buyback_group', 'Pros p.82'),
            ('Transfer-pricing secondary adjustment received from BSPA', 'tp_secadj_recv', 'Pros p.78; p.367, 372')]
    G['pay0'] = g0 + 1
    for i, (t, k, s_) in enumerate(pays):
        grow(g0 + 1 + i, t, vals=[cr(x) for x in D.RPT[k]], s_=s_)
    r = g0 + 1 + len(pays)
    G['fees'] = r; grow(r, 'Royalty + service fees + commission (recurring charges)', f=lambda c, j: f'={c}{g0+1}+{c}{g0+2}+{c}{g0+3}', bold=True)
    grow(r + 1, '  as % of revenue', f=lambda c, j: f'={c}{r}/{c}5', fm=PCT)
    grow(r + 2, '  as % of EBITDA before these charges', f=lambda c, j: (f"={c}{r}/('P&L'!{HIST[j]}{R['ebitda']}+{c}{r})" if j < 3 else f'={c}{r}/(Quarterly!{"G" if j==3 else "H"}{QR["ebitda"]}+{c}{r})'), fm=PCT)
    grow(r + 3, 'Recurring charges + dividends + buyback to group', f=lambda c, j: f'={c}{r}+{c}{g0+5}+{c}{g0+6}', bold=True)
    grow(r + 4, '  as % of PAT', f=lambda c, j: (f"={c}{r+3}/'P&L'!{HIST[j]}{R['pat']}" if j < 3 else f'={c}{r+3}/Quarterly!{"G" if j==3 else "H"}{QR["pat"]}'), fm=PCT)
    grow(r + 5, 'Royalty base implied (royalty / 6%)', f=lambda c, j: (f"='P&L'!{HIST[j]}{R['roy']}/0.06" if j < 3 else f'=Quarterly!{"G" if j==3 else "H"}{QR["roy"]}/0.06'))
    grow(r + 6, '  licensed-product sales as % of revenue', f=lambda c, j: f'={c}{r+5}/{c}5', fm=PCT, s_='Call p.13: "effective royalty works out to 4.4%, 4.5% of our sales"')
    grow(r + 7, 'Group receivables at period end (Dec-23, Dec-24, Dec-25, Jun-25, Jun-26)', vals=[cr(x) for x in D.GROUP_RECV], s_='Pros p.330 (sum of holding + fellow subsidiaries)')
    grow(r + 8, '  days of group sales outstanding', f=lambda c, j: f'={c}{r+7}/{c}6*{365 if j<3 else 181}', fm='0', s_='Third-party receivable days are in row below; group customers pay much later')
    grow(r + 9, '  third-party receivable days', f=lambda c, j: (f"=('P&L'!{HIST[j]}{R['recv']}-{c}{r+7})/{c}7*365" if j < 3 else None), fm='0')
    grow(r + 10, 'Group payables at period end (BSPA + Riduttori + others)', vals=[cr(x) for x in D.GROUP_PAY], s_='Pros p.330')
    grow(r + 11, 'Loan to Bonfiglioli Technology Space (BTSPL), outstanding', vals=[cr(x) for x in D.RPT['loan_to_btspl_out']], s_='Pros p.330 (interest-bearing loan to a fellow subsidiary)')
    G['sens'] = r + 13
    put(gp, f'A{r+13}', 'D. Sensitivity (FY25): if group sales earn X% EBITDA margin, what do third-party sales earn? (not disclosed; transfer prices are "arm\'s length", Pros p.232)', bold=True)
    for i, m in enumerate([0.08, 0.12, 0.16, 0.20, 0.24]):
        rr_ = r + 14 + i
        label(gp, rr_, f'Group sales at {m:.0%} EBITDA margin -> implied third-party EBITDA margin')
        inp(gp, f'B{rr_}', m, PCT); fx(gp, f'D{rr_}', f"=('P&L'!D{R['ebitda']}-D6*B{rr_})/D7", PCT)
    G['grp'] = r + 20
    put(gp, f'A{r+20}', 'E. India inside the Bonfiglioli group (Call p.4; Pros p.205)', bold=True)
    label(gp, r + 21, 'Group revenue FY25 (EUR 1,172.94 mn = Rs.115.56 bn), Rs. crore'); inp(gp, f'D{r+21}', 11556.0)
    label(gp, r + 22, 'BTL share of group revenue (management: ~15%)'); inp(gp, f'D{r+22}', 0.15, PCT)
    label(gp, r + 23, 'BTL share of group EBITDA (management: ~32%)'); inp(gp, f'D{r+23}', 0.32, PCT)
    label(gp, r + 24, 'Implied group EBITDA, Rs. crore'); fx(gp, f'D{r+24}', f"='P&L'!D{R['ebitda']}/D{r+23}")
    label(gp, r + 25, 'Implied group EBITDA margin'); fx(gp, f'D{r+25}', f'=D{r+24}/D{r+21}', PCT)
    label(gp, r + 26, 'Implied rest-of-group EBITDA margin (excl. India)'); fx(gp, f'D{r+26}', f"=(D{r+24}-'P&L'!D{R['ebitda']})/(D{r+21}-'P&L'!D{R['rev']})", PCT)
    label(gp, r + 27, 'BTL EBITDA margin FY25'); fx(gp, f'D{r+27}', f"='P&L'!D{R['ebm']}", PCT, color=GREEN)
    put(gp, f'A{r+28}', 'Read: India earns about twice the margin of the rest of the group and pays ~6.5% of revenue back as royalty and fees. The licence lets BTL sell only in India, Nepal, Bangladesh, Pakistan and Sri Lanka; outside that, only to group companies and with BSPA consent (LicAgr clause 1.1 "Territory" p.2, clause 7.2 p.5). Group companies are in the same business and there is no non-compete (Pros p.408).', italic=True)
    widths(gp, {'A': 72, **{c: 11 for c in 'BCDEF'}, 'G': 70})

    # ================================================================ Sources
    so = wb.create_sheet('Sources')
    put(so, 'A1', 'Sources, page conventions and conflicts', bold=True)
    lines = [
        ('Identity', 'Bonfiglioli Transmissions Ltd, CIN U29309TN1998PLC040717 (L... after listing), Plot AC7-AC11 SIDCO Industrial Estate, Thirumudivakkam, Chennai. NSE: BONFIG, BSE scrip 544996 (BSE/NSE letters 13-Nov-2026). Listed 23-Oct-2026 (PPT slide 3; Res p.2 note 4).'),
        ('Basis', 'Standalone. The company has no subsidiaries, associates or JVs (Pros p.253), so standalone = consolidated. Fiscal year = calendar year (Pros p.205).'),
        ('Offer documents', 'DRHP (SEBI, Feb-2026; restated FY22-FY24 and 9MFY25); RHP 9-Oct-2026; Prospectus 19-Oct-2026 (restated FY23-FY25, H1FY25, H1FY26). Printed page = PDF page - 5 in the RHP and Prospectus; DRHP PDF page = printed + 5 as well.'),
        ('FY23-FY25', 'Prospectus restated statements: BS p.284, P&L p.285, CF p.286, SOCE p.287, notes p.288-344 (revenue note 23 p.316, other expenses note 30 p.318, segment note 36 p.322, related parties note 38 p.327-331, contingent liabilities note 42 p.338, business combination note 46 p.341).'),
        ('Audited vs restated (conflict log)', 'Audited PAT FY23 149.53 cr, FY24 194.69 cr, FY25 237.87 cr vs restated 148.49 / 195.16 / 237.87 cr; audited equity 805.34 / 853.09 / 992.99 cr vs restated 801.36 / 860.95 / 992.99 cr (Pros p.345). The only difference is the pooling of the BDSPL business bought from a group company on 15-Dec-2025 (common-control accounting restates earlier years). FY25 audited = restated. We use restated for all years so the series is like-for-like; audited CY23/CY24 statements are in the pack (signed financials, scanned).'),
        ('Quarters', 'Results for quarter and nine months to 30-Sep-2026 (board 12-Nov-2026, limited review by S.R. Batliboi): Res p.1. Q2FY26 was not reviewed by the auditor (Res p.2 note 3). Q3FY25 is a balancing figure after "adjustments for subsequent events" (Res p.2 note 5).'),
        ('Guidance', 'PR p.2, PPT slide 5, Call p.7, p.10-12: FY26 revenue growth ~20%; FY26-FY28 revenue CAGR ~15% (Call p.16: "Our guidance for the next two years is 15% CAGR"); EBITDA margin "in the vicinity of 18.5%" over the period, not a yearly target. Capex Rs.100 cr FY26, Rs.150 cr FY27 (Call p.8, p.13).'),
        ('Conflict 1', 'FY24 inter-company sales: Rs.2,755.09 mn (Pros p.208, p.358) vs Rs.2,775.09 mn (p.228, p.34). Only 2,775.09 makes the channel table add to revenue (3,535.58 + 11,756.65 + 2,775.09 + 474.51 = 18,541.83), so the model uses 2,775.09; p.208 looks like a typo.'),
        ('Conflict 2', 'Royalty: other-expense note shows 752.35 / 822.09 / 895.87 mn (p.318) vs royalty paid to BSPA 741.26 / 813.32 / 888.08 mn in related-party tables (p.82). Gap ~1% (likely withholding/timing); model uses p.318 (P&L).'),
        ('Conflict 3', 'Top-10 customers: text says "less than 31.72%" in every period (p.207, 215, 229, 358) but the table shows 36.28% (H1FY25), 35.58% (FY25), 32.48% (FY24) (p.230) and the risk factor shows 37.83% / 36.60% / 34.38% / 32.82% for top-10 OEMs (p.26).'),
        ('Conflict 4', 'Quarterly series: PPT slide 9 quarterly EBITDA/PAT for Q1-Q2FY25 do not add to the Prospectus H1FY25; Prospectus H1FY25 + results Q3FY25 do not add to results 9MFY25 (Quarterly sheet memo rows).'),
        ('Prices', 'CMP Rs.803.25 = close 26-Nov-2026; listing-day close Rs.574.50 (23-Oct-2026), from the Screener daily price series (NSE blocked from this container). Replace with Bloomberg.'),
        ('Peers', 'Prospectus Basis for Offer Price p.112 (P/E at 28-Sep-2026 prices) and KPI tables p.116-121. Any other peer multiple: to be checked on Bloomberg.'),
        ('Industry', 'Frost & Sullivan report 28-Sep-2026 summarised in Pros Industry Overview p.131-204: India gear motors <15 kNm p.155-157; India gearboxes >15 kNm p.150-153; India off-highway drives p.167-169; India wind drives p.176-178; global markets p.139-174.'),
    ]
    for i, (a, b) in enumerate(lines):
        put(so, f'A{3+i}', a, bold=True); put(so, f'B{3+i}', b, wrap=True)
    widths(so, {'A': 26, 'B': 160})

    if v2:
        build_v2(wb, pl, R, q, QR, sg, S, gp, G)

    widths(pl, {'A': 62, **{c: 11 for c in 'BCDEFGHI'}, 'J': 90})
    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False
        ws.freeze_panes = 'B3' if ws.title in ('P&L', 'Quarterly') else None
    fn = os.path.join(OUT, f'BONFIG_Model_{version}.xlsx')
    wb.save(fn)
    print('saved', fn)
    return R


# ====================================================================================================
def build_v2(wb, pl, R, q, QR, sg, S, gp, G):
    dv = wb.create_sheet('Drivers', 1)
    put(dv, 'A1', 'Forecast drivers (Rs. crore unless stated). Engine: revenue by vertical = industry growth (F&S, Prospectus) + share gain shown, haircut for delivery; new heavy-duty plant priced on its own economics. FY26E = 9 months actual + Q4 estimate.', bold=True)
    put(dv, 'A2', 'Blue = input, black = formula, green = link, yellow = the inputs that move the answer most. Tags: [A] actual / offer document, [M] management (PR/PPT 12-Nov-2026, call 13-Nov-2026), [E] analyst estimate. Fiscal year = calendar year.', italic=True)
    put(dv, 'A3', 'SCENARIO SELECTOR: 1 = bear, 2 = base, 3 = bull', bold=True); inp(dv, 'C3', 2, '0', key=True)
    fx(dv, 'D3', '=CHOOSE($C$3,"Bear","Base","Bull")')
    put(dv, 'H3', 'Base (26-Nov-2026) = most likely: each vertical grows at its F&S market rate plus the share gain it has shown, less a haircut (last three years grew <10%; wind depends on GE). Margin 18.2%: below the 18.5% guidance, above the 17.5% floor. Bull = guidance in full (FY26 +20%, FY27-FY28 +15% a year, extended to FY30; 18.5% margin). Bear = wind slump (US/GE, tariffs) + OHM cycle + margin back to FY24 levels.', wrap=True)
    header(dv, 5, ['Unit', 'FY26E', 'FY27E', 'FY28E', 'FY29E', 'FY30E']); put(dv, 'A5', 'Driver', bold=True); put(dv, 'H5', 'Source / basis', bold=True)
    X = {}
    r = [6]

    def nxt():
        r[0] += 1; return r[0]

    def section(t):
        rr = nxt(); put(dv, f'A{rr}', t, bold=True); return rr

    def scen(name, unit, bear, base, bull, s_, fm=PCT, key=False):
        rows = []
        for tag, vals in (('Bear', bear), ('Base', base), ('Bull', bull)):
            rr = nxt(); label(dv, rr, f'   {name} - {tag}'); put(dv, f'B{rr}', unit)
            for j, c in enumerate(DRV):
                if vals[j] is not None: inp(dv, f'{c}{rr}', vals[j], fm, key=key and tag == 'Base')
            rows.append(rr)
        put(dv, f'H{rows[0]}', s_, wrap=False)
        rr = nxt(); label(dv, rr, f'{name} - LIVE', bold=True); put(dv, f'B{rr}', unit)
        for c in DRV: fx(dv, f'{c}{rr}', f'=CHOOSE($C$3,{c}{rows[0]},{c}{rows[1]},{c}{rows[2]})', fm)
        return rr, rows

    def single(name, unit, vals, s_, fm=PCT, key=False):
        rr = nxt(); label(dv, rr, name); put(dv, f'B{rr}', unit)
        for j, c in enumerate(DRV):
            if vals[j] is not None: inp(dv, f'{c}{rr}', vals[j], fm, key=key)
        put(dv, f'H{rr}', s_)
        return rr

    section('A. Revenue by vertical')
    vinfo = [('ia', 'I&A (existing products)', 'v_ia'), ('ohm', 'Off-Highway Mobility', 'v_ohm'), ('wind', 'Wind', 'v_wind')]
    gro = {
        'ia': ([0.08, 0.05, 0.06, 0.07, 0.07], [0.15, 0.085, 0.085, 0.085, 0.085], [0.15, 0.14, 0.14, 0.13, 0.13],
               '[A] I&A +5.2% FY24, +7.8% FY25, +23.3% H1FY26, +25.8% 9MFY26, +30.5% Q3 (Segments; PPT slide 7-8). [A] F&S: India gear motors <15 kNm Rs.2,965 cr FY26 -> Rs.4,350 cr FY31, 8.0% CAGR (Pros p.156-157); BTL has ~25% share (p.206). BTL grew below the market FY23-FY25 (6.5% vs 7.0%) then well above in 2026 (industrial recovery). Base: market 8.0% + 0.5 point share gain. Bull: calibrated so total = guidance. FY26E column = Q4 growth YoY on Q4FY25.'),
        'ohm': ([0.10, 0.03, 0.05, 0.07, 0.07], [0.22, 0.14, 0.11, 0.11, 0.11], [0.25, 0.18, 0.17, 0.15, 0.15],
                '[A] OHM +2.3% FY24, +16.4% FY25, +36.4% H1FY26, +43.0% 9MFY26, +54.9% Q3. [M] new programmes (John Deere and others) added ~5% to 9M growth; "growth will continue ... from a higher base" (Call p.13, 15-16). [A] F&S India off-highway drives Rs.1,950 cr FY26 -> Rs.3,090 cr FY31, 9.6% CAGR (Pros p.168); BTL share ~32% (p.206). Base: market + programme ramp fading to market. Bear: construction-equipment downcycle.'),
        'wind': ([-0.15, -0.10, 0.0, 0.05, 0.05], [0.0, 0.09, 0.08, 0.09, 0.09], [0.01, 0.13, 0.12, 0.14, 0.14],
                 '[A] Wind +19.7% FY24, +5.9% FY25, +0.1% H1FY26, +2.8% 9MFY26, +8.0% Q3. [M] GE (largest customer FY25) down ~30% in 9MFY26, other wind customers +22%; GE gave positive Q1-Q2FY27 schedules (Call p.11). [A] F&S India wind drives Rs.935 cr FY26 -> Rs.1,500 cr FY31, 9.9% CAGR (p.178); global wind drives USD 1.0 bn -> 1.4 bn CY25-31, ~5% (p.174). ~35-40% of wind sales go to the US. Base: India market growth blended with slower exports, partial GE recovery. Bear: US tariffs / GE cut.'),
    }
    for k, t, qk in vinfo:
        r9 = nxt(); label(dv, r9, f'{t}: 9MFY26 actual'); put(dv, f'B{r9}', 'Rs cr'); fx(dv, f'C{r9}', f'=Quarterly!J{QR[qk]}', NUM2, GREEN); put(dv, f'H{r9}', 'PPT slide 8')
        r4 = nxt(); label(dv, r4, f'{t}: Q4FY25 base (FY25 less 9MFY25)'); put(dv, f'B{r4}', 'Rs cr'); fx(dv, f'C{r4}', f'=Quarterly!C{QR[qk]}', NUM2, GREEN)
        bear, base, bull, s_ = gro[k]
        live, rows = scen(f'{t} growth (FY26E = Q4 YoY)', '%', bear, base, bull, s_, key=True)
        rv = nxt(); X[k] = rv; label(dv, rv, f'{t} revenue', bold=True); put(dv, f'B{rv}', 'Rs cr')
        fx(dv, f'C{rv}', f'=C{r9}+C{r4}*(1+C{live})', NUM2)
        for j in range(1, 5): fx(dv, f'{DRV[j]}{rv}', f'={DRV[j-1]}{rv}*(1+{DRV[j]}{live})', NUM2)
    # heavy-duty plant
    section('B. New heavy-duty gearbox plant, Talegaon (priced on its own economics)')
    hd_live, _ = scen('New heavy-duty plant revenue', 'Rs cr', [0, 0, 0, 15, 35], [0, 0, 10, 45, 90], [0, 0, 20, 70, 130],
                      '[M] Construction starts Q2 2027, "intent to complete in one year"; heavy duty "will contribute more meaningfully after CY28" (Call p.7, 9, 13-14). [A] India heavy-duty (>15 kNm) gearbox market Rs.4,040 cr FY26 -> Rs.5,790 cr FY31, 7.5% CAGR; BTL holds ~2% vs Elecon/Premium/Flender/Shanthi 77% (Pros p.151-153). BTL heavy-duty sales today Rs.89.8 cr (FY25, p.222). Base: Rs.90 cr by FY30 = ~1.5 points more share. Bull: Rs.130 cr. No customer named.', fm=NUM2)
    X['hd'] = hd_live
    X['hd_mat'] = single('Heavy-duty plant: materials % of its revenue', '%', [0.66] * 5, '[E] Heavy-duty gearboxes are casting/forging heavy; set 3-4 points above the company average (62%).')
    X['hd_fix'] = single('Heavy-duty plant: fixed cost (staff, overheads) per year once open', 'Rs cr', [0, 0, 6, 12, 14], '[E] Not disclosed. ~Rs.12-14 cr a year at Rs.40-80 cr revenue means a loss/low margin in the first two years (ramp).', fm=NUM2)
    X['hd_oth'] = single('Heavy-duty plant: variable other costs % of its revenue', '%', [0.08] * 5, '[E] Freight, power, consumables; royalty charged separately below.')
    # others and totals
    section('C. Totals')
    oth9 = nxt(); label(dv, oth9, 'Others revenue (scrap, incentives, component sales)'); put(dv, f'B{oth9}', 'Rs cr')
    fx(dv, f'C{oth9}', f'=Quarterly!J{QR["v_oth"]}+Quarterly!C{QR["v_oth"]}', NUM2)
    X['othp'] = single('  Others as % of vertical revenue (FY27E on)', '%', [None, 0.02, 0.02, 0.02, 0.02], '[A] 2.0% FY23, 2.9% FY24, 2.3% FY25, 1.9% 9MFY26 (incl. one-offs in FY24-25). FY26E = 9M actual + Q4FY25 level.')
    for j in range(1, 5): fx(dv, f'{DRV[j]}{oth9}', f'=({DRV[j]}{X["ia"]}+{DRV[j]}{X["ohm"]}+{DRV[j]}{X["wind"]}+{DRV[j]}{X["hd"]})*{DRV[j]}{X["othp"]}', NUM2)
    X['oth'] = oth9
    tot = nxt(); X['rev'] = tot; label(dv, tot, 'Revenue from operations', bold=True); put(dv, f'B{tot}', 'Rs cr')
    for c in DRV: fx(dv, f'{c}{tot}', f'={c}{X["ia"]}+{c}{X["ohm"]}+{c}{X["wind"]}+{c}{X["hd"]}+{c}{X["oth"]}', NUM2, bold=True)
    gr = nxt(); X['g'] = gr; label(dv, gr, '  growth'); fx(dv, f'C{gr}', f"=C{tot}/'P&L'!D{R['rev']}-1", PCT)
    for j in range(1, 5): fx(dv, f'{DRV[j]}{gr}', f'={DRV[j]}{tot}/{DRV[j-1]}{tot}-1', PCT)
    gg = nxt(); X['guide_g'] = gg; label(dv, gg, 'Management guidance: revenue growth'); put(dv, f'B{gg}', '%')
    for j, v in enumerate([0.20, 0.15, 0.15, 0.15, 0.15]): inp(dv, f'{DRV[j]}{gg}', v, PCT)
    put(dv, f'H{gg}', '[M] FY26 ~20%; FY26-FY28 CAGR ~15% ("next two years is 15% CAGR", Call p.16; PR p.2). FY29-FY30: no guidance - bull extends 15% (2009-25 record 14.5% a year, Call p.4). [E]')
    gv = nxt(); X['guide_rev'] = gv; label(dv, gv, 'Management guidance: revenue', bold=True); put(dv, f'B{gv}', 'Rs cr')
    fx(dv, f'C{gv}', f"='P&L'!D{R['rev']}*(1+C{gg})", NUM2)
    for j in range(1, 5): fx(dv, f'{DRV[j]}{gv}', f'={DRV[j-1]}{gv}*(1+{DRV[j]}{gg})', NUM2)
    mg = nxt(); X['vs_guide'] = mg; label(dv, mg, 'CHECK: live revenue vs guidance (base must be < 0; bull ~0)', color=RED)
    for c in DRV: fx(dv, f'{c}{mg}', f'={c}{tot}/{c}{gv}-1', PCT, color=RED)
    fl = nxt(); X['floor_rev'] = fl; label(dv, fl, 'Floor revenue (memo): 9M actual + Q4 flat, then 7% a year (F&S market growth less a point, no share gain)'); put(dv, f'B{fl}', 'Rs cr')
    fx(dv, f'C{fl}', f"=Quarterly!J{QR['rev']}+Quarterly!C{QR['rev']}", NUM2)
    for j in range(1, 5): fx(dv, f'{DRV[j]}{fl}', f'={DRV[j-1]}{fl}*1.07', NUM2)
    pos = nxt(); X['pos'] = pos; label(dv, pos, 'Live revenue position between floor (0%) and guidance (100%)')
    for c in DRV: fx(dv, f'{c}{pos}', f'=({c}{tot}-{c}{fl})/({c}{gv}-{c}{fl})', PCT)
    put(dv, f'H{pos}', 'Rule of thumb for the base: 40-75% of the way from floor to guidance.')
    ind = nxt(); X['ind'] = ind; label(dv, ind, 'Memo: F&S market growth, revenue-weighted (gear motors 8.0%, off-highway 9.6%, wind 9.9%, FY26-31)'); put(dv, f'B{ind}', '%')
    for c in DRV[1:]: fx(dv, f'{c}{ind}', f"=(0.08*Segments!D5+0.096*Segments!D6+0.099*Segments!D7)/(Segments!D5+Segments!D6+Segments!D7)", PCT)
    put(dv, f'H{ind}', '[A] Pros p.156-157, 168, 178. FY25 vertical weights.')

    section('D. Costs (core business; heavy-duty plant costs added from section B)')
    mat_live, _ = scen('Materials cost % of core revenue', '%', [0.613, 0.641, 0.646, 0.646, 0.646], [0.611, 0.6235, 0.6230, 0.6215, 0.6210], [0.610, 0.6205, 0.6195, 0.6185, 0.6180],
                       '[A] 64.2% FY23, 63.6% FY24, 62.1% FY25, 61.0% H1FY26, 61.1% 9MFY26 (P&L, Quarterly). [M] 9M margin helped by forex and price increases ahead of cost (lag), "expect it to temper down slightly" (Call p.11-12). This line sets the margin: base ~62.2-62.4% = ~18.2% total EBITDA margin (after the heavy-duty plant ramp); bull ~61.8-62.1% = ~18.5% guidance; bear 64.6% = 16.0% (FY24 was 15.9%). FY26E = 9M + Q4 at ~19%.', key=True)
    X['mat'] = mat_live
    X['emp'] = single('Employee cost % of core revenue', '%', [0.0515, 0.0525, 0.0525, 0.0525, 0.0525], '[A] 5.3% FY23-FY25, 5.2% H1FY26, 5.1% 9MFY26 (headcount 1,032 Jun-26 vs 943 Jun-25, p.370).')
    X['roysh'] = single('Licensed-product sales as % of revenue (royalty base)', '%', [0.742] * 5, '[A] Royalty / 6% = 74.2% of revenue FY25, 74.0% FY24, 74.3% FY23 (Group_vs_ThirdParty). [M] "fixed rate of 6% royalty on specified products, effective royalty works out to 4.4%, 4.5%" and "no plans to change" (Call p.13).')
    X['royr'] = single('Royalty rate on licensed-product sales', '%', [0.06] * 5, '[A] LicAgr clause 5.2 p.4 (6% of net sales of Products; sales to the Licensor excluded); Pros p.232, 253. Annual auto-renewal; either side can end it with 3 months notice before 31-Dec (LicAgr clause 9.2 p.6).', key=True)
    X['prof'] = single('Professional fees (group service fees + others) % of revenue', '%', [0.0245, 0.0240, 0.0240, 0.0240, 0.0240], '[A] 2.8% FY23, 2.4% FY24, 2.4% FY25, 2.5% H1FY26. Service fee = 30-100% of BSPA cost + 5% mark-up (Pros p.253); income-tax officers disallowed part of these charges in several years (Pros p.338).')
    X['othx'] = single('Other expenses (rest) % of core revenue', '%', [0.0700, 0.0735, 0.0735, 0.0735, 0.0735], '[A] 8.4% FY23, 8.4% FY24, 7.4% FY25 (note 30 less royalty and fees). 9MFY26 total other expenses 14.1% of revenue incl. royalty and fees (Res p.1).')
    em = nxt(); X['ebm'] = em; label(dv, em, 'memo: EBITDA margin (live)'); put(dv, f'B{em}', '%')
    for j, c in enumerate(DRV): fx(dv, f'{c}{em}', f"='P&L'!{FC[j]}{R['ebm']}", PCT, GREEN)
    eg = nxt(); X['guide_m'] = eg; label(dv, eg, 'Management guidance: EBITDA margin'); put(dv, f'B{eg}', '%')
    for j, c in enumerate(DRV[1:]): inp(dv, f'{c}{eg}', 0.185, PCT)
    put(dv, f'H{eg}', '[M] "EBITDA margin in the vicinity of 18.5%" for FY26-FY28 as a whole; no FY26 margin guidance (Call p.7, 11-12). Guidance is BELOW the evidence: 18.4% FY25, 19.7% 9MFY26. Base is still kept below it.')
    ec = nxt(); X['chk_m'] = ec; label(dv, ec, 'CHECK: live margin minus guidance (base must be < 0)', color=RED)
    for c in DRV[1:]: fx(dv, f'{c}{ec}', f'={c}{em}-{c}{eg}', PCT, color=RED)

    section('E. Below EBITDA, balance sheet and cash')
    X['dep'] = single('Depreciation % of opening net fixed assets', '%', [0.17] * 5, '[A] 15.3% FY25 (Rs.47.8 cr on Rs.313 cr), 9MFY26 run-rate ~17% (Rs.40.3 cr in 9 months on Rs.313 cr).')
    X['capex'] = single('Capex', 'Rs cr', [100, 150, 130, 125, 135], '[M] ~Rs.100 cr FY26 (Rs.70-80 cr spent by Sep), ~Rs.150 cr FY27 incl. heavy-duty plant start (Call p.8, 13); "3%-4% every year" (Call p.13). FY28-30 [E] ~3.5-4% of base revenue. Same in all scenarios (committed).', fm=NUM2, key=True)
    X['oiy'] = single('Other income: yield on opening cash and bank', '%', [0.06] * 5, '[A] FY25 Rs.10.1 cr on Rs.144.8 cr opening cash = 7.0% (incl. FX gain); bank interest Rs.6.9 cr. FY26E = 9M actual Rs.10.5 cr + one quarter at this yield.')
    X['intr'] = single('Interest rate on opening borrowings', '%', [0.09] * 5, '[A] No borrowings since Dec-2024 (Pros p.284, 366). Kept for completeness.')
    X['finp'] = single('Other borrowing costs (early-payment discounts on receivables) % of revenue', '%', [0.0035] * 5, '[A] Rs.7.0 cr FY25 = 0.35% of revenue; finance cost Rs.6.4 cr in 9MFY26 (Pros p.317, 370; Res p.1).')
    X['tax'] = single('Tax rate', '%', [0.257, 0.255, 0.255, 0.255, 0.255], '[A] 26.9% FY25 (incl. Rs.6.1 cr earlier years), 25.7% 9MFY26 (Res p.1). New-regime 25.17% + disallowances.')
    X['payout'] = single('Dividend payout (dividends paid / PAT)', '%', [None, 0.40, 0.40, 0.40, 0.40], '[A] 44% FY23, 35% FY24 (+Rs.72 cr buyback), 39% FY25. FY26E: Rs.110 cr interim already paid to the parent before the IPO (Pros p.280). [E] 40% from FY27.')
    X['div26'] = single('FY26E dividends paid (actual, pre-IPO interim)', 'Rs cr', [109.978, None, None, None, None], '[A] Pros p.280, 286.', fm=NUM2)
    X['rdays'] = single('Receivable days (on revenue)', 'days', [92, 92, 92, 92, 92], '[A] 89 FY23, 80 FY24, 94 FY25, 85 H1FY26 (Pros p.210). Group customers take ~140-150 days (Group_vs_ThirdParty).', fm='0')
    X['idays'] = single('Inventory days (on materials cost)', 'days', [100, 98, 98, 98, 98], '[A] 112 FY23, 100 FY24, 93 FY25, 99 H1FY26 (Pros p.210); H1FY26 build-up of imported parts (p.377-378).', fm='0')
    X['pdays'] = single('Payable days (on materials cost)', 'days', [95, 95, 95, 95, 95], '[A] 121 FY23, 97 FY24, 97 FY25, 90 H1FY26 (Pros p.210).', fm='0')
    X['ocap'] = single('Other current assets % of revenue', '%', [0.045] * 5, '[A] 4.5% FY25 (incl. Rs.5 cr loan to BTSPL).')
    X['olp'] = single('Other liabilities and provisions % of revenue', '%', [0.056] * 5, '[A] 5.6% FY25.')
    X['sh'] = single('Shares outstanding', 'crore', [18.7996] * 5, '[A] 187,995,834 shares (Pros p.287). OFS: no new shares.', fm='0.0000')

    section('F. Capacity check (machine hours; is there room for the volumes?)')
    hr = nxt(); X['rev_hr'] = hr; label(dv, hr, 'Revenue per utilised hour, FY25 (Rs.)'); fx(dv, f'C{hr}', f"='P&L'!D{R['rev']}*1e7/Segments!D{S['cap_ut']}", '#,##0', GREEN)
    put(dv, f'H{hr}', '[A] Rs.2,013.5 cr / 888,814 utilised hours (Pros p.233).')
    X['pmix'] = single('Price and mix uplift per hour, a year', '%', [0.03] * 5, '[M] 3.5 points of 9MFY26 growth from price (Call p.16); larger OHM/wind drives raise value per hour. [E] 3%.')
    X['capg'] = single('Available hours growth (machine additions from capex)', '%', [0.04, 0.05, 0.05, 0.12, 0.06], '[A] Available hours +6% FY24, +5% FY25 (Segments). FY29 jump = heavy-duty plant and Mannur moving to Talegaon (Call p.14). [E]')
    hn = nxt(); X['hrs_need'] = hn; label(dv, hn, 'Hours needed (core revenue / revenue per hour after uplift)'); put(dv, f'B{hn}', 'hours')
    ha = nxt(); X['hrs_av'] = ha; label(dv, ha, 'Hours available'); put(dv, f'B{ha}', 'hours')
    hu = nxt(); X['util'] = hu; label(dv, hu, 'Implied utilisation (company says 75% in H1FY26; >85% is tight)', bold=True)
    for j, c in enumerate(DRV):
        core = f'({c}{X["ia"]}+{c}{X["ohm"]}+{c}{X["wind"]})'
        fx(dv, f'{c}{hn}', f'={core}*1e7/($C${hr}*(1+{c}{X["pmix"]})^{j+1})', '#,##0')
        prev = f'Segments!D{S["cap_av"]}' if j == 0 else f'{DRV[j-1]}{ha}'
        fx(dv, f'{c}{ha}', f'={prev}*(1+{c}{X["capg"]})', '#,##0')
        fx(dv, f'{c}{hu}', f'={c}{hn}/{c}{ha}', PCT, bold=True)
    widths(dv, {'A': 70, 'B': 8, **{c: 11 for c in 'CDEFG'}, 'H': 120})

    # ---------------- P&L forecast formulas ----------------
    for j, c in enumerate(FC):
        d = DRV[j]; p = CL(ord(c) - 65)
        core = f'(Drivers!{d}{X["rev"]}-Drivers!{d}{X["hd"]})'
        hd = f'Drivers!{d}{X["hd"]}'
        fx(pl, f'{c}{R["rev"]}', f'=Drivers!{d}{X["rev"]}', color=GREEN)
        fx(pl, f'{c}{R["mat"]}', f'={core}*Drivers!{d}{X["mat"]}+{hd}*Drivers!{d}{X["hd_mat"]}')
        fx(pl, f'{c}{R["emp"]}', f'={core}*Drivers!{d}{X["emp"]}+Drivers!{d}{X["hd_fix"]}')
        fx(pl, f'{c}{R["roy"]}', f'={c}{R["rev"]}*Drivers!{d}{X["roysh"]}*Drivers!{d}{X["royr"]}')
        fx(pl, f'{c}{R["prof"]}', f'={c}{R["rev"]}*Drivers!{d}{X["prof"]}')
        fx(pl, f'{c}{R["othx"]}', f'={core}*Drivers!{d}{X["othx"]}+{hd}*Drivers!{d}{X["hd_oth"]}')
        fx(pl, f'{c}{R["dep"]}', f'={p}{R["nfa"]}*Drivers!{d}{X["dep"]}')
        if j == 0: fx(pl, f'{c}{R["oi"]}', f'=Quarterly!J{QR["oi"]}+{p}{R["cash"]}*Drivers!{d}{X["oiy"]}/4')
        else: fx(pl, f'{c}{R["oi"]}', f'={p}{R["cash"]}*Drivers!{d}{X["oiy"]}')
        fx(pl, f'{c}{R["fin"]}', f'={p}{R["borr"]}*Drivers!{d}{X["intr"]}+{c}{R["rev"]}*Drivers!{d}{X["finp"]}')
        fx(pl, f'{c}{R["tax"]}', f'={c}{R["pbt"]}*Drivers!{d}{X["tax"]}')
        put(pl, f'{c}{R["patd"]}', 0, BLUE, fmt=NUM2)
        fx(pl, f'{c}{R["sh"]}', f'=Drivers!{d}{X["sh"]}', '0.0000', GREEN)
        if j == 0: fx(pl, f'{c}{R["div"]}', f'=Drivers!{d}{X["div26"]}', color=GREEN)
        else: fx(pl, f'{c}{R["div"]}', f'={c}{R["pat"]}*Drivers!{d}{X["payout"]}')
        put(pl, f'{c}{R["oneoff"]}', 0, BLUE, fmt=NUM2)
        # BS
        fx(pl, f'{c}{R["nfa"]}', f'={p}{R["nfa"]}+Drivers!{d}{X["capex"]}-{c}{R["dep"]}')
        fx(pl, f'{c}{R["onca"]}', f'={p}{R["onca"]}')
        fx(pl, f'{c}{R["invy"]}', f'={c}{R["mat"]}*Drivers!{d}{X["idays"]}/365')
        fx(pl, f'{c}{R["recv"]}', f'={c}{R["rev"]}*Drivers!{d}{X["rdays"]}/365')
        fx(pl, f'{c}{R["oca"]}', f'={c}{R["rev"]}*Drivers!{d}{X["ocap"]}')
        fx(pl, f'{c}{R["scap"]}', f'={c}{R["sh"]}*10')
        fx(pl, f'{c}{R["oeq"]}', f'={p}{R["oeq"]}+{p}{R["scap"]}-{c}{R["scap"]}+{c}{R["pat"]}-{c}{R["div"]}')
        put(pl, f'{c}{R["borr"]}', 0, BLUE, fmt=NUM2)
        fx(pl, f'{c}{R["lease"]}', f'={p}{R["lease"]}')
        fx(pl, f'{c}{R["tp"]}', f'={c}{R["mat"]}*Drivers!{d}{X["pdays"]}/365')
        fx(pl, f'{c}{R["ol"]}', f'={c}{R["rev"]}*Drivers!{d}{X["olp"]}')
        fx(pl, f'{c}{R["cash"]}', f'={c}{R["tel"]}-{c}{R["nfa"]}-{c}{R["onca"]}-{c}{R["invy"]}-{c}{R["recv"]}-{c}{R["oca"]}')
        # CF
        fx(pl, f'{c}{R["cf_pat"]}', f'={c}{R["pat"]}'); fx(pl, f'{c}{R["cf_dep"]}', f'={c}{R["dep"]}')
        fx(pl, f'{c}{R["cf_wc"]}', f'=-({c}{R["invy"]}-{p}{R["invy"]})-({c}{R["recv"]}-{p}{R["recv"]})-({c}{R["oca"]}-{p}{R["oca"]})+({c}{R["tp"]}-{p}{R["tp"]})+({c}{R["ol"]}-{p}{R["ol"]})')
        fx(pl, f'{c}{R["cfo"]}', f'={c}{R["cf_pat"]}+{c}{R["cf_dep"]}+{c}{R["cf_wc"]}', bold=True)
        fx(pl, f'{c}{R["capex"]}', f'=-Drivers!{d}{X["capex"]}')
        fx(pl, f'{c}{R["cf_onca"]}', f'=-({c}{R["onca"]}-{p}{R["onca"]})')
        fx(pl, f'{c}{R["cf_div"]}', f'=-{c}{R["div"]}'); put(pl, f'{c}{R["cf_bb"]}', 0, BLUE, fmt=NUM2)
        fx(pl, f'{c}{R["cf_borr"]}', f'={c}{R["borr"]}-{p}{R["borr"]}'); fx(pl, f'{c}{R["cf_lease"]}', f'={c}{R["lease"]}-{p}{R["lease"]}')
        put(pl, f'{c}{R["cf_oth"]}', 0, BLUE, fmt=NUM2)
        fx(pl, f'{c}{R["cf_net"]}', f'={c}{R["cfo"]}+{c}{R["capex"]}+{c}{R["cf_onca"]}+{c}{R["cf_div"]}+{c}{R["cf_bb"]}+{c}{R["cf_borr"]}+{c}{R["cf_lease"]}+{c}{R["cf_oth"]}')
        prevc = f'{p}{R["cash"]}'  # opening = BS cash and bank
        fx(pl, f'{c}{R["cf_close"]}', f'={prevc}+{c}{R["cf_net"]}')
        fx(pl, f'{c}{R["chk_cf"]}', f'={c}{R["cf_close"]}-{c}{R["cash"]}', color=RED)
    src(pl, R['mat'], 'Forecast: Drivers (core revenue x materials % + heavy-duty plant revenue x its materials %).')

    # ---------------- Segments forecast ----------------
    for j, c in enumerate(SF := ['G', 'H', 'I', 'J', 'K']):
        d = DRV[j]
        for k, key in [('ia', 'ia'), ('ohm', 'ohm'), ('wind', 'wind'), ('oth', 'oth')]:
            fx(sg, f'{c}{S[k]}', f'=Drivers!{d}{X[key]}', color=GREEN)
        fx(sg, f'{c}9', f'=Drivers!{d}{X["hd"]}', color=GREEN)
        fx(sg, f'{c}10', f'=SUM({c}5:{c}9)', bold=True)
        fx(sg, f'{c}11', f"={c}10-'P&L'!{FC[j]}{R['rev']}", color=RED)
        for i, k in enumerate(['ia', 'ohm', 'wind']):
            prev = 'D' if j == 0 else SF[j - 1]
            fx(sg, f'{c}{12+i}', f'={c}{S[k]}/{prev}{S[k]}-1', PCT)
            fx(sg, f'{c}{15+i}', f'={c}{S[k]}/{c}10', PCT)

    # ---------------- TAM ----------------
    tm = wb.create_sheet('TAM', 2)
    put(tm, 'A1', 'Addressable markets (Frost & Sullivan report 28-Sep-2026, as printed in the Prospectus Industry Overview). India markets in Rs. crore (Indian fiscal years to March); global in USD bn (calendar years).', bold=True)
    header(tm, 3, ['FY23', 'FY26', 'FY31F', 'CAGR FY26-31', 'BTL FY25 revenue', 'BTL share', 'Leaders / note']); put(tm, 'A3', 'India market', bold=True)
    tams = [('Industrial gear motors <15 kNm (BTL I&A core)', 2420, 2965, 4350, 'Segments!D20', 'BTL ~25%, #1 (Pros p.206); vs SEW, NORD, Premium (Call p.9). Pros p.155-157.'),
            ('Industrial gearboxes >15 kNm (heavy duty)', 3326, 4040, 5790, 'Segments!D21', 'Elecon, Premium, Flender, Shanthi = 77%; BTL ~2% (Pros p.151-153).'),
            ('Off-highway mobility drives', 1550, 1950, 3090, 'Segments!D6', 'BTL ~32% among non-captive suppliers (p.206); vs Comer, Dana, PMP (Call p.9). Pros p.167-169.'),
            ('Wind turbine yaw and pitch drives (India)', 725, 935, 1500, 'Segments!D7', 'BTL 67.9% of domestic makers (p.206). BTL wind revenue includes US/EU exports. Pros p.176-178.')]
    for i, (t, a, b, c_, ref, n) in enumerate(tams):
        rr = 4 + i; label(tm, rr, t)
        inp(tm, f'B{rr}', a, '#,##0'); inp(tm, f'C{rr}', b, '#,##0'); inp(tm, f'D{rr}', c_, '#,##0')
        fx(tm, f'E{rr}', f'=(D{rr}/C{rr})^(1/5)-1', PCT); fx(tm, f'F{rr}', f'={ref}', NUM, GREEN); fx(tm, f'G{rr}', f'=F{rr}/C{rr}', PCT); put(tm, f'H{rr}', n, italic=True)
    label(tm, 8, 'Total India addressable', bold=True)
    for c in 'BCDF': fx(tm, f'{c}8', f'=SUM({c}4:{c}7)', '#,##0', bold=True)
    fx(tm, 'E8', '=(D8/C8)^(1/5)-1', PCT); fx(tm, 'G8', '=F8/C8', PCT)
    put(tm, 'H8', 'BTL wind share overstated (includes exports); I&A core share ~25% matches the F&S statement.', italic=True)
    header(tm, 10, ['CY22', 'CY25', 'CY31F', 'CAGR CY25-31', '', '', 'Note']); put(tm, 'A10', 'Global market (USD bn)', bold=True)
    gl = [('Industrial gear motors <15 kNm', 4.9, 5.6, 7.6, 'Pros p.144'), ('Industrial gearboxes >15 kNm', 8.1, 9.1, 12.1, 'Pros p.139-140'),
          ('Off-highway mobility drives', 4.0, 4.6, 6.6, 'Pros p.161-162'), ('Wind turbine drives', 0.9, 1.0, 1.4, 'Pros p.174; Bonfiglioli group #1 with 21% (PPT slide 13)')]
    for i, (t, a, b, c_, n) in enumerate(gl):
        rr = 11 + i; label(tm, rr, t); inp(tm, f'B{rr}', a, '0.0'); inp(tm, f'C{rr}', b, '0.0'); inp(tm, f'D{rr}', c_, '0.0'); fx(tm, f'E{rr}', f'=(D{rr}/C{rr})^(1/6)-1', PCT); put(tm, f'H{rr}', n, italic=True)
    put(tm, 'A16', 'Base case growth vs market (FY27E-FY30E CAGR, live scenario)', bold=True)
    header(tm, 17, ['Market CAGR', 'Our base (live)', 'Mgmt guidance', 'Gap vs market', '', '', 'Read'])
    cmp_ = [('I&A existing', 'E4', 'ia'), ('Off-Highway Mobility', 'E6', 'ohm'), ('Wind', 'E7', 'wind')]
    for i, (t, mref, k) in enumerate(cmp_):
        rr = 18 + i; label(tm, rr, t); fx(tm, f'B{rr}', f'={mref}', PCT)
        fx(tm, f'C{rr}', f'=(Drivers!G{X[k]}/Drivers!C{X[k]})^(1/4)-1', PCT, GREEN)
        put(tm, f'D{rr}', 'no split', italic=True); fx(tm, f'E{rr}', f'=C{rr}-B{rr}', PCT)
    rr = 21; label(tm, rr, 'Company total', bold=True); fx(tm, f'B{rr}', f'=Drivers!D{X["ind"]}', PCT, GREEN)
    fx(tm, f'C{rr}', f'=(Drivers!G{X["rev"]}/Drivers!C{X["rev"]})^(1/4)-1', PCT, GREEN); fx(tm, f'D{rr}', f'=(Drivers!G{X["guide_rev"]}/Drivers!C{X["guide_rev"]})^(1/4)-1', PCT, GREEN)
    fx(tm, f'E{rr}', f'=C{rr}-B{rr}', PCT)
    put(tm, 'H21', 'Guidance needs ~6 points a year above the market for five years; BTL beat the market by ~1 point a year in FY23-FY25 and by ~10 points in 2026.', italic=True)
    widths(tm, {'A': 48, **{c: 13 for c in 'BCDEFG'}, 'H': 95})

    # ---------------- Unit economics ----------------
    ue = wb.create_sheet('Unit_Economics', 3)
    put(ue, 'A1', 'Unit economics: what one gearbox, one machine-hour and one employee earn (FY25 unless stated)', bold=True)
    header(ue, 3, ['BTL FY25', 'Shanthi Gears FY26', 'Elecon FY26', 'Timken India FY26', 'Schaeffler India FY25', '', 'Source / note'])
    put(ue, 'A3', 'Metric', bold=True)
    U = [('Revenue (Rs. crore)', f"='P&L'!D{R['rev']}", 518.72, 2366.05, 3478.03, 9685.85, 'BTL Pros p.285; peers Pros p.112/119'),
         ('EBITDA margin', f"='P&L'!D{R['ebm']}", 0.2003, 0.2211, 0.1818, 0.1820, 'Pros p.119'),
         ('Units made (gear motors + gearboxes)', f'=Segments!D{S["units"]}', None, None, None, None, 'Pros p.209; peers do not disclose units'),
         ('Revenue per unit (Rs.)', '=B4*1e7/B6', None, None, None, None, 'Average across a Rs.13 Nm worm box and a 3,000 kNm track drive - a blend, not a price'),
         ('EBITDA per unit (Rs.)', '=B7*B5', None, None, None, None, ''),
         ('Utilised machine hours', f'=Segments!D{S["cap_ut"]}', None, None, None, None, 'Pros p.233'),
         ('Revenue per utilised hour (Rs.)', '=B4*1e7/B9', None, None, None, None, ''),
         ('Employees on roll', f'=Segments!D{S["emp_onroll"]}', 479, None, None, None, 'BTL Pros p.239; Shanthi AR FY26 (479 permanent). Elecon/Timken/Schaeffler: to be checked on Bloomberg'),
         ('Revenue per on-roll employee (Rs. crore)', '=B4/B11', '=C4/C11', None, None, None, ''),
         ('Total headcount incl. contract', f'=Segments!D{S["headcount"]}', None, None, None, None, 'Pros p.373'),
         ('Revenue per head incl. contract (Rs. crore)', '=B4/B13', None, None, None, None, ''),
         ('Fixed asset turnover (x)', f"='P&L'!D{R['fat']}", 4.19, 3.90, 2.87, 4.23, 'Pros p.119 (company definition: PPE + CWIP)'),
         ('ROCE', 0.3405, 0.2485, 0.1928, 0.1900, 0.2608, 'Pros p.119 (company definitions)'),
         ('Royalty + group fees % of revenue', f"='P&L'!D{R['grp_drain']}", None, None, None, None, 'Peers with foreign parents (Timken, Schaeffler) also pay royalty/fees: to be checked on Bloomberg')]
    for i, row in enumerate(U):
        rr = 4 + i; label(ue, rr, row[0])
        for j, v in enumerate(row[1:6]):
            c = 'BCDEF'[j]
            if v is None: continue
            fm = PCT if ('margin' in row[0] or row[0] in ('ROCE', 'Royalty + group fees % of revenue')) else ('0.0' if '(x)' in row[0] else ('#,##0' if 'Rs.)' in row[0] or 'hours' in row[0] or 'Units' in row[0] or 'Employees' in row[0] or 'headcount' in row[0] else NUM2))
            if isinstance(v, str): fx(ue, f'{c}{rr}', v, fm, GREEN if '!' in v else BLACK)
            else: inp(ue, f'{c}{rr}', v, fm)
        put(ue, f'H{rr}', row[6], italic=True)
    put(ue, 'A20', "What management's plan needs per unit (live scenario vs bull)", bold=True)
    header(ue, 21, ['FY25A', 'FY28E live', 'FY28E bull (guidance)', '', '', '', 'Read'])
    lines = [('Revenue (Rs. crore)', f"='P&L'!D{R['rev']}", f"='P&L'!G{R['rev']}", f'=Drivers!E{X["guide_rev"]}'),
             ('Revenue per unit, +3% a year price/mix (Rs.)', '=B7', '=B7*1.03^3', '=B7*1.03^3'),
             ('Units needed', '=B22*1e7/B23', '=C22*1e7/C23', '=D22*1e7/D23'),
             ('  growth in units vs FY25', None, '=C24/$B$24-1', '=D24/$B$24-1'),
             ('Machine hours needed at FY25 revenue/hour + 3% a year', '=B9', '=C22*1e7/(B10*1.03^3)', '=D22*1e7/(B10*1.03^3)'),
             ('Utilisation on FY25 available hours (1,205,748)', f'=B26/Segments!D{S["cap_av"]}', f'=C26/Segments!$D${S["cap_av"]}', f'=D26/Segments!$D${S["cap_av"]}')]
    for i, (t, a, b, c_) in enumerate(lines):
        rr = 22 + i; label(ue, rr, t)
        for col, v in zip('BCD', (a, b, c_)):
            if v: fx(ue, f'{col}{rr}', v, PCT if ('growth' in t or 'Utilisation' in t) else '#,##0', GREEN if '!' in v else BLACK)
    put(ue, 'H27', 'Guidance volumes need ~95-100% of FY25 machine hours by FY28 unless the Rs.250 cr FY26-27 capex adds capacity: the heavy-duty/Talegaon expansion is not optional for the bull case.', italic=True)
    widths(ue, {'A': 52, **{c: 15 for c in 'BCDEFG'}, 'H': 90})

    # ---------------- Group sheet forecast block ----------------
    rr = G['grp'] + 30
    put(gp, f'A{rr}', 'F. Forecast of charges to the group (live scenario), Rs. crore', bold=True)
    header(gp, rr, ['FY26E', 'FY27E', 'FY28E', 'FY29E', 'FY30E'])
    label(gp, rr + 1, 'Royalty'); label(gp, rr + 2, 'Professional / service fees'); label(gp, rr + 3, 'Dividends to promoter (77%)'); label(gp, rr + 4, 'Total value to the group'); label(gp, rr + 5, '  % of EBITDA + royalty + fees')
    for j, c in enumerate('BCDEF'):
        pc = FC[j]
        fx(gp, f'{c}{rr+1}', f"='P&L'!{pc}{R['roy']}", color=GREEN); fx(gp, f'{c}{rr+2}', f"='P&L'!{pc}{R['prof']}", color=GREEN)
        fx(gp, f'{c}{rr+3}', f"='P&L'!{pc}{R['div']}*IF({j}=0,1,0.77)")
        fx(gp, f'{c}{rr+4}', f'={c}{rr+1}+{c}{rr+2}+{c}{rr+3}', bold=True)
        fx(gp, f'{c}{rr+5}', f"={c}{rr+4}/('P&L'!{pc}{R['ebitda']}+{c}{rr+1}+{c}{rr+2})", PCT)
    put(gp, f'G{rr+3}', 'FY26E: the Rs.110 cr interim was paid to BSPA as 100% owner before the IPO.', italic=True)

    # ---------------- Valuations ----------------
    va = wb.create_sheet('Valuations')
    put(va, 'A1', 'Valuation (Rs.). Fiscal year = calendar year: FY27E = year to Dec-2027, the same 12-month window that "FY28E" covers for March-year companies in our other notes.', bold=True)
    V = {}
    vrows = [
        ('cmp', 'CMP (Rs.) - close 26-Nov-2026 (Screener daily series); replace with Bloomberg', D.CMP, '0.00', True),
        ('sh', 'Shares (crore)', f'=Drivers!C{X["sh"]}', '0.0000', False),
        ('mcap', 'Market cap (Rs. crore)', '=C2*C3', '#,##0', False),
        ('ipo', 'IPO price (Rs.), OFS 15-19 Oct-2026; listed 23-Oct-2026 (close Rs.574.50)', D.OFS_PRICE, '0.00', True),
        ('netcash25', 'Net cash 31-Dec-2025 (Rs. crore)', f"='P&L'!D{R['netcash']}", NUM, False),
        ('ev', 'Enterprise value (market cap - net cash Dec-25)', '=C4-C6', '#,##0', False),
        ('ttm_pat', 'TTM PAT (Q4FY25 + 9MFY26), Rs. crore', f'=Quarterly!C{QR["pat"]}+Quarterly!J{QR["pat"]}', NUM, False),
        ('ttm_eb', 'TTM EBITDA, Rs. crore', f'=Quarterly!C{QR["ebitda"]}+Quarterly!J{QR["ebitda"]}', NUM, False),
        ('pe_ttm', 'P/E on TTM PAT (x)', '=C4/C8', '0.0', False),
        ('ev_ttm', 'EV / TTM EBITDA (x)', '=C7/C9', '0.0', False),
        ('pe25', 'P/E on FY25A EPS (x)  [IPO was 46.3x, Pros p.110]', f"=C2/'P&L'!D{R['eps']}", '0.0', False),
        ('pb', 'Price / book (Jun-26 NAV Rs.55.02, Pros p.111)', '=C2/55.02', '0.0', False),
    ]
    for i, (k, t, v, fm, is_inp) in enumerate(vrows):
        rr = 2 + i; V[k] = rr; put(va, f'B{rr}', t)
        if is_inp: inp(va, f'C{rr}', v, fm, key=(k == 'cmp'))
        else: fx(va, f'C{rr}', v, fm, GREEN if '!' in str(v) else BLACK)
    base = 15
    put(va, f'B{base}', 'VALUATION - live scenario:', bold=True); fx(va, f'C{base}', '=Drivers!D3', color=GREEN)
    vr2 = [('peer', 'Peer P/E: Prospectus peer average (Elecon, Shanthi, Schaeffler, Timken), trailing, 28-Sep-2026', D.PEER_PE_AVG, '0.00', True),
           ('roll', 'Roll-forward: peers\' trailing year ends Mar-26; FY27E ends Dec-27 (~1.75 years later) at ~9% a year EPS growth -> divide by', 1.15, '0.00', True),
           ('tpe', 'Target P/E on FY27E EPS (x) - same in bear, base and bull', 45, '0.0', True),
           ('eps27', 'FY27E EPS (Rs.)', f"='P&L'!F{R['eps']}", '0.00', False),
           ('eps28', 'FY28E EPS (Rs.)', f"='P&L'!G{R['eps']}", '0.00', False),
           ('tp', 'Target price (Rs.) = target P/E x FY27E EPS', '=C18*C19', '0', False),
           ('up', 'Upside / (downside) vs CMP', '=C21/C2-1', PCT, False),
           ('rating', 'Rating (BUY > +15%, HOLD -5% to +15%, SELL < -5%)', '=IF(C22>0.15,"BUY",IF(C22>=-0.05,"HOLD","SELL"))', None, False),
           ('dist', 'Distance to the nearest rating line (points)', '=MIN(ABS(C22-0.15),ABS(C22+0.05))*100', '0.0', False),
           ('border', 'Borderline? (within 3 points)', '=IF(C24<3,"borderline","no")', None, False)]
    for i, (k, t, v, fm, is_inp) in enumerate(vr2):
        rr = 16 + i; V[k] = rr; put(va, f'B{rr}', t)
        if is_inp: inp(va, f'C{rr}', v, fm, key=(k == 'tpe'))
        else:
            c = fx(va, f'C{rr}', v, fm or 'General', GREEN if '!' in str(v) else BLACK)
    put(va, 'J16', 'Pros p.110 and p.112: Elecon 31.63x, Shanthi Gears 63.39x, Schaeffler India 53.74x, Timken India 57.66x; average 51.61x (trailing FY26/CY25 EPS). Current peer multiples and SKF/Siemens/ABB motion units: to be checked on Bloomberg.', italic=True)
    put(va, 'J18', '51.6x / 1.15 = 44.9x, rounded to 45x. No premium: 6.5% of revenue leaves as royalty and fees, the parent owns the IP and sets the territory, wind depends on one US customer. No discount: ROCE 34% and net cash beat every peer (Pros p.119). The IPO was priced at 46.3x FY25 EPS.', italic=True)
    put(va, 'B27', 'Cross-check: EV / EBITDA', bold=True)
    vr3 = [('eb27', 'FY27E EBITDA (Rs. crore)', f"='P&L'!F{R['ebitda']}", NUM), ('evm', 'EV / EBITDA multiple (x)', 29, '0.0'),
           ('evv', 'Enterprise value (Rs. crore)', '=C28*C29', '#,##0'), ('nd26', 'Net cash at FY26E year end (Rs. crore; year before the valuation year)', f"='P&L'!E{R['netcash']}", NUM),
           ('eqv', 'Equity value (Rs. crore)', '=C30+C31', '#,##0'), ('vps', 'Value per share (Rs.)', '=C32/C3', '0'), ('vcmp', 'vs CMP', '=C33/C2-1', PCT)]
    for i, (k, t, v, fm) in enumerate(vr3):
        rr = 28 + i; V[k] = rr; put(va, f'B{rr}', t)
        if k == 'evm': inp(va, f'C{rr}', v, fm)
        else: fx(va, f'C{rr}', v, fm, GREEN if '!' in str(v) else BLACK)
    put(va, 'J29', 'The IPO was priced at 29.7x FY25 EV/EBITDA (Pros p.51). 29x on FY27E is consistent with 45x P/E at a ~66% PAT/EBITDA ratio. Peer EV/EBITDA: to be checked on Bloomberg.', italic=True)
    put(va, 'B36', 'Reverse check: what the CMP needs', bold=True)
    vr4 = [('Market cap at CMP (Rs. crore)', '=C4', '#,##0'), ('FY27E PAT the CMP implies at 45x (Rs. crore)', '=C37/C18', NUM),
           ('Model FY27E PAT, live scenario (Rs. crore)', f"='P&L'!F{R['patc']}", NUM), ('Model PAT vs implied', '=C39/C38-1', PCT),
           ('FY27E EPS the CMP implies (Rs.)', '=C2/C18', '0.00'), ('P/E at CMP on FY26E / FY27E / FY28E EPS (x)', f"=C2/'P&L'!E{R['eps']}", '0.0'),
           ('Implied FY25-FY27 PAT CAGR at 45x', f"=(C38/'P&L'!D{R['patc']})^(1/2)-1", PCT)]
    for i, (t, v, fm) in enumerate(vr4):
        rr = 37 + i; put(va, f'B{rr}', t); fx(va, f'C{rr}', v, fm, GREEN if '!' in v else BLACK)
    fx(va, 'D42', '=C2/C19', '0.0'); fx(va, 'E42', '=C2/C20', '0.0')
    put(va, 'B45', 'Scenario results (values pasted from model runs by brun.py on 26-Nov-2026; re-run after changing drivers)', bold=True)
    hdr = ['Scenario', 'FY27E revenue', 'FY27E EBITDA', 'FY27E PAT', 'FY27E EPS', 'Target (45x)', 'Upside', 'Rating', 'EV/EBITDA value', 'FY28E EPS']
    for i, h in enumerate(hdr): c = va.cell(row=46, column=2 + i, value=h); c.font = F(BLACK, True); c.fill = GREY
    for i, nm in enumerate(['Bear', 'Base', 'Bull']): put(va, f'B{47+i}', nm)
    put(va, 'B50', 'CHECK: live target minus pasted target for the live scenario', color=RED); fx(va, 'C50', '=C21-INDEX(G47:G49,Drivers!C3)', '0.00', RED)
    put(va, 'B52', 'Floor (memo, pasted): committed/visible only - 9M actual + Q4 flat, then 7% a year, 17.5% EBITDA margin', bold=True)
    for i, h in enumerate(['Rs. crore', 'FY26E', 'FY27E', 'FY28E', 'FY29E', 'FY30E']): c = va.cell(row=53, column=2 + i, value=h); c.font = F(BLACK, True); c.fill = GREY
    for i, t in enumerate(['Revenue', 'EBITDA (excl. other income)', 'PAT', 'EPS (Rs.)']): put(va, f'B{54+i}', t)
    put(va, 'B58', 'Floor target (Rs.) = 45x floor FY27E EPS'); put(va, 'B59', 'Floor upside vs CMP'); put(va, 'B60', 'Floor rating')
    put(va, 'B62', "Chance of management's plan already in the price", bold=True)
    put(va, 'B63', 'Base target (Rs.)'); fx(va, 'C63', '=G48', '0')
    put(va, 'B64', 'Bull target (Rs.) = management plan'); fx(va, 'C64', '=G49', '0')
    put(va, 'B65', 'Bear target (Rs.)'); fx(va, 'C65', '=G47', '0')
    put(va, 'B66', '(CMP - base target) / (bull target - base target)'); fx(va, 'C66', '=(C2-C63)/(C64-C63)', PCT)
    put(va, 'B67', 'Read: above 100% = the price already pays for more than management promises; below 0% = the price is under our base.', italic=True)
    put(va, 'B69', 'Target at other multiples (live scenario FY27E EPS; and FY28E EPS for reference)', bold=True)
    for i, h in enumerate(['P/E (x)', 'Target on FY27E', 'vs CMP', 'Target on FY28E', 'vs CMP']): c = va.cell(row=70, column=2 + i, value=h); c.font = F(BLACK, True); c.fill = GREY
    for i, m in enumerate([35, 40, 45, 50, 55, 60]):
        rr = 71 + i; inp(va, f'B{rr}', m, '0'); fx(va, f'C{rr}', f'=B{rr}*$C$19', '0'); fx(va, f'D{rr}', f'=C{rr}/$C$2-1', PCT)
        fx(va, f'E{rr}', f'=B{rr}*$C$20', '0'); fx(va, f'F{rr}', f'=E{rr}/$C$2-1', PCT)
    put(va, 'B78', 'OFS: who sold, at what price (Pros cover p.2, p.51, p.106-111)', bold=True)
    ofs = [('Seller', 'Bonfiglioli S.p.A. (the promoter); 100% owner before the IPO, 77.0% after'), ('Shares sold', D.OFS_SHARES), ('Price (Rs.)', D.OFS_PRICE),
           ('Proceeds to the seller (Rs. crore)', D.OFS_AMOUNT_MN / 10), ('Money to the company (Rs. crore)', 0), ('Offer expenses borne by the seller (Rs. crore)', D.OFS_EXPENSES_MN / 10 if hasattr(D, 'OFS_EXPENSES_MN') else D.OFFER_EXPENSES_MN / 10),
           ("Promoter's average cost per share (Rs.)", D.WACA), ('Offer price / Jun-26 book value per share (x)', '=C81/55.02'), ('Offer P/E on FY25 EPS (x)', D.OFFER_PE),
           ('Offer EV/EBITDA on FY25 (x)', D.OFFER_EV_EBITDA), ('Pre-IPO cash taken out by the parent in FY23-H1FY26 (dividends + buyback, Rs. crore)', "=SUM(Group_vs_ThirdParty!B%d:D%d)+SUM(Group_vs_ThirdParty!F%d:F%d)" % (G['pay0'] + 4, G['pay0'] + 5, G['pay0'] + 4, G['pay0'] + 5))]
    for i, (t, v) in enumerate(ofs):
        rr = 79 + i; put(va, f'B{rr}', t)
        if isinstance(v, str) and v.startswith('='): fx(va, f'C{rr}', v, '#,##0.00')
        elif isinstance(v, str): put(va, f'C{rr}', v)
        else: inp(va, f'C{rr}', v, '#,##0.00')
    widths(va, {'A': 3, 'B': 82, **{c: 13 for c in 'CDEFGHIJK'}, 'J': 13})
    va.column_dimensions['J'].width = 14
    return X


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if MODE in ('v1', 'both'): build('v1')
    if MODE in ('v2', 'both'): build('v2')
