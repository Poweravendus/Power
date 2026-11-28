"""Build PASUPTAC_Model_v1.xlsx (historicals) and PASUPTAC_Model_v2.xlsx (forecast) for Pasupati Acrylon Ltd.
Usage: python3 pal_build_model.py <out_dir> [v1|v2|both]
Rs. crore unless stated (annual report Rs. lakh / 100). Standalone basis (no subsidiaries). FY = April-March.
Colours: blue = document input, black = formula, green = link to another sheet, red = check, yellow fill = key driver.
"""
import sys, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as CL
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pal_data as D

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
MODE = sys.argv[2] if len(sys.argv) > 2 else 'both'
BLUE, BLACK, GREEN, RED = '0000FF', '000000', '008000', 'FF0000'
YEL = PatternFill('solid', fgColor='FFFF00'); GREY = PatternFill('solid', fgColor='D9D9D9')
F = lambda c=BLACK, b=False, i=False: Font(name='Arial', size=9, color=c, bold=b, italic=i)
PCT, NUM, NUM2, INT = '0.0%', '#,##0.0', '#,##0.00', '#,##0'
H = list('BCDEFGHIJK')            # FY17A..FY26A
FC = list('LMNO')                 # FY27E..FY30E
DV = list('CDEF')                 # Drivers year columns = FY27E..FY30E
YH = [y + 'A' for y in D.YRS]; YF = ['FY27E', 'FY28E', 'FY29E', 'FY30E']
SRC = 'Q'
cr = lambda x: None if x is None else round(x / 100.0, 4)


def put(ws, ref, v, c=BLACK, b=False, fmt=None, fill=None, i=False, wrap=False):
    x = ws[ref]; x.value = v; x.font = F(c, b, i)
    if fmt: x.number_format = fmt
    if fill: x.fill = fill
    if wrap: x.alignment = Alignment(wrap_text=True, vertical='top')
    return x


def inp(ws, ref, v, fmt=NUM2, key=False): return put(ws, ref, v, BLUE, fmt=fmt, fill=YEL if key else None)
def fx(ws, ref, f, fmt=NUM2, c=BLACK, b=False): return put(ws, ref, f, c, b, fmt)
def lab(ws, r, t, b=False, c=BLACK, col='A', i=False): put(ws, f'{col}{r}', t, c, b, i=i)
def src(ws, r, t, col=SRC): put(ws, f'{col}{r}', t, i=True)


def hdr(ws, r, labels, start=2):
    for i, l in enumerate(labels):
        c = ws.cell(row=r, column=start + i, value=l); c.font = F(BLACK, True); c.fill = GREY; c.alignment = Alignment(horizontal='center')


def widths(ws, w):
    for k, v in w.items(): ws.column_dimensions[k].width = v


def prev(c): return CL(ord(c) - 65)


def build(version):
    v2 = version == 'v2'
    YRS = YH + (YF if v2 else []); ALL = H + (FC if v2 else [])
    wb = Workbook()
    # =========================================================== P&L
    pl = wb.active; pl.title = 'P&L'
    put(pl, 'A1', 'Pasupati Acrylon Ltd (BSE 500456 | NSE PASUPTAC) - standalone P&L, Rs. crore. FY = April-March. FY17A = Ind AS restated comparative.', b=True)
    hdr(pl, 2, YRS); put(pl, 'A2', 'Profit and loss', b=True); put(pl, f'{SRC}2', 'Source (annual report printed pages)', b=True)
    keys = ['revg', 'excd', 'rev', 'g', 'rm', 'pur', 'inv', 'mat', 'matp', 'emp', 'pf', 'othrep', 'othx', 'ebitda', 'ebm', 'dep', 'ebit', 'oi', 'fin', 'exc',
            'pbt', 'chk_pbt', 'tax', 'taxr', 'pat', 'chk_pat', 'patm', 'sh', 'eps', 'chk_eps', 'div', 'payout']
    R = {k: 3 + i for i, k in enumerate(keys)}
    L = {'revg': 'Revenue from operations (as reported; incl. excise duty before GST)', 'excd': 'less: excise duty (inside other expenses before Jul-2017)',
         'rev': 'Revenue from operations (net of excise)', 'g': '  growth', 'rm': 'Cost of materials consumed', 'pur': 'Purchase of stock in trade',
         'inv': 'Change in inventories of FG and WIP (+ = release)', 'mat': 'Materials cost', 'matp': '  materials % of revenue',
         'emp': 'Employee benefits expense', 'pf': 'Power and fuel', 'othrep': 'Other expenses as reported (incl. power & fuel and excise)',
         'othx': 'Other expenses (excl. power & fuel and excise)', 'ebitda': 'EBITDA (excl. other income)', 'ebm': '  EBITDA margin',
         'dep': 'Depreciation', 'ebit': 'EBIT', 'oi': 'Other income', 'fin': 'Finance costs', 'exc': 'Exceptional items (charge)',
         'pbt': 'Profit before tax', 'chk_pbt': 'CHECK: PBT vs reported (should be 0)', 'tax': 'Tax expense', 'taxr': '  tax rate',
         'pat': 'PAT', 'chk_pat': 'CHECK: PAT vs reported (should be 0)', 'patm': '  PAT margin', 'sh': 'Shares outstanding (crore)',
         'eps': 'EPS (Rs.)', 'chk_eps': 'CHECK: EPS vs reported (rounding < 0.01)', 'div': 'Dividends paid', 'payout': '  payout'}
    for k in keys: lab(pl, R[k], L[k], b=k in ('rev', 'ebitda', 'pat', 'eps'), c=RED if k.startswith('chk') else BLACK)
    P = D.PL
    for i, c in enumerate(H):
        inp(pl, f'{c}{R["revg"]}', cr(P['rev_gross'][i])); inp(pl, f'{c}{R["excd"]}', cr(P['excise'][i]))
        inp(pl, f'{c}{R["rm"]}', cr(P['rm'][i])); inp(pl, f'{c}{R["pur"]}', cr(P['purch'][i])); inp(pl, f'{c}{R["inv"]}', cr(P['inv'][i]))
        inp(pl, f'{c}{R["emp"]}', cr(P['emp'][i])); inp(pl, f'{c}{R["pf"]}', cr(P['pf'][i])); inp(pl, f'{c}{R["othrep"]}', cr(P['oth_tot'][i]))
        fx(pl, f'{c}{R["othx"]}', f'={c}{R["othrep"]}-{c}{R["pf"]}-{c}{R["excd"]}')
        inp(pl, f'{c}{R["dep"]}', cr(P['dep'][i])); inp(pl, f'{c}{R["oi"]}', cr(P['oi'][i])); inp(pl, f'{c}{R["fin"]}', cr(P['fin'][i]))
        inp(pl, f'{c}{R["exc"]}', cr(P['exc'][i])); inp(pl, f'{c}{R["tax"]}', cr(P['tax'][i]))
        fx(pl, f'{c}{R["chk_pbt"]}', f'=ROUND({c}{R["pbt"]}-{cr(P["pbt_rep"][i])},2)', c=RED)
        fx(pl, f'{c}{R["chk_pat"]}', f'=ROUND({c}{R["pat"]}-{cr(P["pat_rep"][i])},2)', c=RED)
        fx(pl, f'{c}{R["chk_eps"]}', f'=ROUND({c}{R["eps"]}-{P["eps_rep"][i]},1)', c=RED)
        inp(pl, f'{c}{R["sh"]}', D.SHARES, '0.0000'); inp(pl, f'{c}{R["div"]}', 0)
    for j, c in enumerate(ALL):
        if j > 0: fx(pl, f'{c}{R["g"]}', f'={c}{R["rev"]}/{prev(c)}{R["rev"]}-1', PCT)
        fx(pl, f'{c}{R["rev"]}', f'={c}{R["revg"]}-{c}{R["excd"]}', b=True)
        fx(pl, f'{c}{R["mat"]}', f'={c}{R["rm"]}+{c}{R["pur"]}+{c}{R["inv"]}'); fx(pl, f'{c}{R["matp"]}', f'={c}{R["mat"]}/{c}{R["rev"]}', PCT)
        fx(pl, f'{c}{R["ebitda"]}', f'={c}{R["rev"]}-{c}{R["mat"]}-{c}{R["emp"]}-{c}{R["pf"]}-{c}{R["othx"]}', b=True)
        fx(pl, f'{c}{R["ebm"]}', f'={c}{R["ebitda"]}/{c}{R["rev"]}', PCT)
        fx(pl, f'{c}{R["ebit"]}', f'={c}{R["ebitda"]}-{c}{R["dep"]}')
        fx(pl, f'{c}{R["pbt"]}', f'={c}{R["ebit"]}+{c}{R["oi"]}-{c}{R["fin"]}-{c}{R["exc"]}')
        fx(pl, f'{c}{R["taxr"]}', f'={c}{R["tax"]}/{c}{R["pbt"]}', PCT)
        fx(pl, f'{c}{R["pat"]}', f'={c}{R["pbt"]}-{c}{R["tax"]}', b=True); fx(pl, f'{c}{R["patm"]}', f'={c}{R["pat"]}/{c}{R["rev"]}', PCT)
        fx(pl, f'{c}{R["eps"]}', f'={c}{R["pat"]}/{c}{R["sh"]}', '0.00', b=True)
        fx(pl, f'{c}{R["payout"]}', f'={c}{R["div"]}/{c}{R["pat"]}', PCT)
    src(pl, R['revg'], 'P&L: ' + '; '.join(f'{y} {D.SRC_PL[y]}' for y in D.YRS))
    src(pl, R['excd'], D.PL_SRC_EXTRA['excise']); src(pl, R['pf'], D.PL_SRC_EXTRA['pf']); src(pl, R['exc'], D.PL_SRC_EXTRA['exc'])
    src(pl, R['rm'], 'FY19 AR p.46 shows 65,155.81 lakh; FY20 AR restates FY19 to 65,227.64 (and other expenses lower by 71.84) - FY19 AR used.')
    src(pl, R['div'], 'No dividend in any year FY15-FY26 ("Board decided not to recommend any dividend": AR FY26 p.9, AR FY18 p.7).')
    src(pl, R['sh'], '8,91,33,121 shares of Rs.10 (AR FY26 p.67); unchanged throughout.')
    src(pl, R['ebitda'], 'Company "EBIDTA" in the board report includes other income (Rs.119.22 cr FY26, AR FY26 p.9); CARE PBILDT Rs.111.21 cr FY26 matches this line.')

    # =========================================================== BS
    bs = wb.create_sheet('BS')
    put(bs, 'A1', 'Balance sheet (as at 31-Mar), Rs. crore. Summary rows are formulas on the detail inputs below (history) or on Drivers (forecast).', b=True)
    hdr(bs, 2, YRS); put(bs, 'A2', 'Summary', b=True); put(bs, f'{SRC}2', 'Source', b=True)
    bk = ['nfa', 'onca', 'invy', 'recv', 'oca', 'liq', 'ta', 'scap', 'oeq', 'teq', 'borr', 'tp', 'ol', 'tl', 'tel', 'chk_bs', 'chk_ta', 'netdebt']
    B = {k: 3 + i for i, k in enumerate(bk)}
    BL = {'nfa': 'Net fixed assets (PPE + CWIP)', 'onca': 'Other non-current assets', 'invy': 'Inventories', 'recv': 'Trade receivables',
          'oca': 'Other current assets', 'liq': 'Cash, bank balances and current investments (liquid funds)', 'ta': 'Total assets',
          'scap': 'Equity share capital', 'oeq': 'Other equity', 'teq': 'Total equity', 'borr': 'Borrowings (long + short term)', 'tp': 'Trade payables',
          'ol': 'Other liabilities and provisions (incl. deferred tax)', 'tl': 'Total liabilities', 'tel': 'Total equity and liabilities',
          'chk_bs': 'CHECK: assets - equity and liabilities (should be 0)', 'chk_ta': 'CHECK: total assets vs reported (history)', 'netdebt': 'Net debt (borrowings - liquid funds; negative = net cash)'}
    for k in bk: lab(bs, B[k], BL[k], b=k in ('ta', 'teq', 'tel'), c=RED if k.startswith('chk') else BLACK)
    d0 = B['netdebt'] + 3
    lab(bs, d0, 'Detail inputs (history) - reported lines grouped as described in the source column', b=True); hdr(bs, d0, YH)
    det = [('ppe', 'Property, plant and equipment'), ('cwip', 'Capital work in progress'), ('onca', 'Other non-current assets (fin. assets, DTA, inv. property)'),
           ('invy', 'Inventories'), ('cinv', 'Current investments (mutual funds)'), ('recv', 'Trade receivables'), ('cash', 'Cash and cash equivalents'),
           ('bank', 'Other bank balances'), ('oca', 'Other current assets (incl. current tax, other fin. assets)'), ('scap', 'Equity share capital'),
           ('oeq', 'Other equity'), ('ltb', 'Long-term borrowings'), ('stb', 'Short-term borrowings incl. current maturities'), ('tp', 'Trade payables'),
           ('ncl', 'Non-current provisions + deferred tax + other NCL'), ('ocl', 'Other current liabilities + provisions + current tax'), ('ta_rep', 'Reported total assets')]
    DR = {}
    for i, (k, t) in enumerate(det):
        r = d0 + 1 + i; DR[k] = r; lab(bs, r, t)
        for j, c in enumerate(H): inp(bs, f'{c}{r}', cr(D.BS[k][j]))
    src(bs, d0, D.BS_NOTE); src(bs, d0 + 1, 'BS: ' + '; '.join(f'{y} {D.SRC_BS[y]}' for y in D.YRS))
    src(bs, DR['oeq'], 'FY26 AR shows FY25 capital 8,913.31 + other equity 27,500.70 lakh (forfeited shares regrouped); FY25 AR figures used for FY25.')
    s = lambda c, ks: '=' + '+'.join(f'{c}{DR[k]}' for k in ks)
    for c in H:
        fx(bs, f'{c}{B["nfa"]}', s(c, ['ppe', 'cwip'])); fx(bs, f'{c}{B["onca"]}', s(c, ['onca'])); fx(bs, f'{c}{B["invy"]}', s(c, ['invy']))
        fx(bs, f'{c}{B["recv"]}', s(c, ['recv'])); fx(bs, f'{c}{B["oca"]}', s(c, ['oca'])); fx(bs, f'{c}{B["liq"]}', s(c, ['cinv', 'cash', 'bank']))
        fx(bs, f'{c}{B["scap"]}', s(c, ['scap'])); fx(bs, f'{c}{B["oeq"]}', s(c, ['oeq'])); fx(bs, f'{c}{B["borr"]}', s(c, ['ltb', 'stb']))
        fx(bs, f'{c}{B["tp"]}', s(c, ['tp'])); fx(bs, f'{c}{B["ol"]}', s(c, ['ncl', 'ocl']))
        fx(bs, f'{c}{B["chk_ta"]}', f'=ROUND({c}{B["ta"]}-{c}{DR["ta_rep"]},1)', c=RED)
    for c in ALL:
        fx(bs, f'{c}{B["ta"]}', f'={c}{B["nfa"]}+{c}{B["onca"]}+{c}{B["invy"]}+{c}{B["recv"]}+{c}{B["oca"]}+{c}{B["liq"]}', b=True)
        fx(bs, f'{c}{B["teq"]}', f'={c}{B["scap"]}+{c}{B["oeq"]}', b=True)
        fx(bs, f'{c}{B["tl"]}', f'={c}{B["borr"]}+{c}{B["tp"]}+{c}{B["ol"]}'); fx(bs, f'{c}{B["tel"]}', f'={c}{B["teq"]}+{c}{B["tl"]}', b=True)
        fx(bs, f'{c}{B["chk_bs"]}', f'=ROUND({c}{B["ta"]}-{c}{B["tel"]},3)', c=RED); fx(bs, f'{c}{B["netdebt"]}', f'={c}{B["borr"]}-{c}{B["liq"]}')
    src(bs, B['liq'], 'Forecast: the plug (equity and liabilities less all other assets).')
    src(bs, B['borr'], 'Indian Bank term loan Rs.108 cr for the ethanol plant at 10.25-10.50%, 28 rising quarterly instalments from Mar-2026 (AR FY26 p.69-70).')

    # =========================================================== CF
    cf = wb.create_sheet('CF')
    put(cf, 'A1', 'Cash flow, Rs. crore. History as reported (cash = cash and cash equivalents only); forecast closing = liquid funds (cash + bank + current investments).', b=True)
    hdr(cf, 2, YRS); put(cf, f'{SRC}2', 'Source', b=True)
    ck = ['pat', 'dep', 'wc', 'cfo', 'capex', 'fcf', 'int', 'borr', 'div', 'othi', 'othf', 'net', 'open', 'close', 'chk']
    C = {k: 3 + i for i, k in enumerate(ck)}
    CLB = {'pat': 'PAT', 'dep': 'Depreciation', 'wc': 'Working capital, tax and other adjustments (history: balancing)', 'cfo': 'Cash from operations (CFO)',
           'capex': 'Capex (PPE, capital advances, investment property)', 'fcf': 'Free cash flow (CFO + capex)', 'int': 'Interest paid (financing)',
           'borr': 'Net borrowings', 'div': 'Dividends paid', 'othi': 'Other investing (treasury, interest received, deposits)', 'othf': 'Other financing',
           'net': 'Net change in cash', 'open': 'Opening cash', 'close': 'Closing cash', 'chk': 'CHECK: closing cash vs balance sheet (should be 0)'}
    for k in ck: lab(cf, C[k], CLB[k], b=k in ('cfo', 'fcf'), c=RED if k == 'chk' else BLACK)
    for i, c in enumerate(H):
        fx(cf, f'{c}{C["pat"]}', f"='P&L'!{c}{R['pat']}", c=GREEN); fx(cf, f'{c}{C["dep"]}', f"='P&L'!{c}{R['dep']}", c=GREEN)
        inp(cf, f'{c}{C["cfo"]}', cr(D.CF['cfo'][i])); fx(cf, f'{c}{C["wc"]}', f'={c}{C["cfo"]}-{c}{C["pat"]}-{c}{C["dep"]}')
        inp(cf, f'{c}{C["capex"]}', cr(D.CF['capex'][i])); inp(cf, f'{c}{C["int"]}', cr(D.CF['int_paid'][i])); inp(cf, f'{c}{C["borr"]}', cr(D.CF['net_borr'][i]))
        inp(cf, f'{c}{C["div"]}', 0)
        fx(cf, f'{c}{C["othi"]}', f'={cr(D.CF["cfi"][i])}-{c}{C["capex"]}')
        fx(cf, f'{c}{C["othf"]}', f'={cr(D.CF["cff"][i])}-{c}{C["int"]}-{c}{C["borr"]}-{c}{C["div"]}')
        fx(cf, f'{c}{C["net"]}', f'={c}{C["cfo"]}+{c}{C["capex"]}+{c}{C["int"]}+{c}{C["borr"]}+{c}{C["div"]}+{c}{C["othi"]}+{c}{C["othf"]}')
        if i == 0: inp(cf, f'{c}{C["open"]}', 3.2351)
        else: fx(cf, f'{c}{C["open"]}', f'={prev(c)}{C["close"]}')
        fx(cf, f'{c}{C["close"]}', f'={c}{C["open"]}+{c}{C["net"]}')
        fx(cf, f'{c}{C["chk"]}', f'=ROUND({c}{C["close"]}-BS!{c}{DR["cash"]},1)', c=RED)
    for c in ALL: fx(cf, f'{c}{C["fcf"]}', f'={c}{C["cfo"]}+{c}{C["capex"]}', b=True)
    src(cf, C['cfo'], 'CF: ' + '; '.join(f'{y} {D.SRC_CF[y]}' for y in D.YRS) + '. Later restatements: FY21 CFO 13.76 cr (AR FY22), FY23 27.35 cr (AR FY24), FY24 71.81 cr (AR FY25).')
    src(cf, C['open'], 'FY17 opening cash Rs.3.24 cr (Ind AS, AR FY18 p.38).')
    src(cf, C['othi'], 'Reported investing cash flow less capex: mutual-fund purchases/sales, interest received, deposits.')

    # =========================================================== Ratios
    ra = wb.create_sheet('Ratios')
    put(ra, 'A1', 'Working capital and ratios', b=True); hdr(ra, 2, YRS)
    rk = ['idays', 'rdays', 'pdays', 'nwc', 'nwcp', 'roe', 'roce', 'nde', 'cfoe', 'capexp', 'fat', 'bvps', 'pe_hist']
    RR = {k: 3 + i for i, k in enumerate(rk)}
    RLB = {'idays': 'Inventory days (on materials cost)', 'rdays': 'Receivable days (on revenue)', 'pdays': 'Payable days (on materials cost)',
           'nwc': 'Net working capital (inventory + receivables + other CA - payables)', 'nwcp': '  NWC % of revenue', 'roe': 'ROE (PAT / average equity)',
           'roce': 'ROCE (EBIT / average equity + borrowings)', 'nde': 'Net debt / EBITDA (x)', 'cfoe': 'CFO / EBITDA', 'capexp': 'Capex % of revenue',
           'fat': 'Fixed asset turnover (revenue / net fixed assets)', 'bvps': 'Book value per share (Rs.)', 'pe_hist': 'memo: P/E on average price of the year (x)'}
    for k in rk: lab(ra, RR[k], RLB[k])
    avgpx = {'FY17': 25.7, 'FY18': 26.3, 'FY19': 21.1, 'FY20': 13.6, 'FY21': 10.5, 'FY22': 31.1, 'FY23': 34.2, 'FY24': 36.2, 'FY25': 44.1, 'FY26': 49.1}
    for j, c in enumerate(ALL):
        p = prev(c)
        fx(ra, f'{c}{RR["idays"]}', f"=BS!{c}{B['invy']}/'P&L'!{c}{R['mat']}*365", INT)
        fx(ra, f'{c}{RR["rdays"]}', f"=BS!{c}{B['recv']}/'P&L'!{c}{R['rev']}*365", INT)
        fx(ra, f'{c}{RR["pdays"]}', f"=BS!{c}{B['tp']}/'P&L'!{c}{R['mat']}*365", INT)
        fx(ra, f'{c}{RR["nwc"]}', f'=BS!{c}{B["invy"]}+BS!{c}{B["recv"]}+BS!{c}{B["oca"]}-BS!{c}{B["tp"]}')
        fx(ra, f'{c}{RR["nwcp"]}', f"={c}{RR['nwc']}/'P&L'!{c}{R['rev']}", PCT)
        if j > 0:
            fx(ra, f'{c}{RR["roe"]}', f"='P&L'!{c}{R['pat']}/AVERAGE(BS!{p}{B['teq']},BS!{c}{B['teq']})", PCT)
            fx(ra, f'{c}{RR["roce"]}', f"='P&L'!{c}{R['ebit']}/AVERAGE(BS!{p}{B['teq']}+BS!{p}{B['borr']},BS!{c}{B['teq']}+BS!{c}{B['borr']})", PCT)
        fx(ra, f'{c}{RR["nde"]}', f"=BS!{c}{B['netdebt']}/'P&L'!{c}{R['ebitda']}", '0.0')
        fx(ra, f'{c}{RR["cfoe"]}', f"=CF!{c}{C['cfo']}/'P&L'!{c}{R['ebitda']}", PCT)
        fx(ra, f'{c}{RR["capexp"]}', f"=-CF!{c}{C['capex']}/'P&L'!{c}{R['rev']}", PCT)
        fx(ra, f'{c}{RR["fat"]}', f"='P&L'!{c}{R['rev']}/BS!{c}{B['nfa']}", '0.0')
        fx(ra, f'{c}{RR["bvps"]}', f"=BS!{c}{B['teq']}/'P&L'!{c}{R['sh']}", '0.0')
    for j, c in enumerate(H):
        y = D.YRS[j]; inp(ra, f'{c}{RR["pe_hist"]}', None); fx(ra, f'{c}{RR["pe_hist"]}', f"={avgpx[y]}/'P&L'!{c}{R['eps']}", '0.0')
    src(ra, RR['pe_hist'], 'Average weekly close in the fiscal year (Screener price series, raw/PASUPTAC_price_history.csv) / EPS. Median FY17-FY26 = 7.6x.')
    src(ra, RR['idays'], 'CARE reports inventory 102 days FY24, 80 FY25, 49 FY26 (on its own basis; CARE Jun-2026 p.3).')

    # =========================================================== Segments
    sg = wb.create_sheet('Segments')
    put(sg, 'A1', 'Segments and operating data (Ind AS 108: Acrylic fibre, CPP film, Ethanol). Rs. crore unless stated. Per kg / per litre in Rs.', b=True)
    hdr(sg, 2, YRS); put(sg, f'{SRC}2', 'Source', b=True)
    S = {}; r = 3
    def row(k, t, b=False, c=BLACK):
        nonlocal r; S[k] = r; lab(sg, r, t, b=b, c=c); r += 1
    def sec(t):
        nonlocal r; r += 1; lab(sg, r, t, b=True); r += 1
    row('rf', 'Revenue - Acrylic fibre (FY17-FY18 net of excise)'); row('rc', 'Revenue - CPP film'); row('re', 'Revenue - Ethanol (distillery, incl. DDGS)')
    row('rt', 'Total segment revenue', b=True); row('chk_r', 'CHECK: segments vs P&L revenue (should be 0)', c=RED)
    row('sf', '  fibre share'); row('sc', '  CPP share'); row('se', '  ethanol share')
    row('xf', 'Segment result - fibre (PBIT incl. allocated other income)'); row('xc', 'Segment result - CPP'); row('xe', 'Segment result - ethanol')
    row('chk_x', 'CHECK: segment results vs PBT + finance + exceptional (should be 0)', c=RED)
    row('mf', '  fibre PBIT margin'); row('mc', '  CPP PBIT margin'); row('me', '  ethanol PBIT margin')
    row('df', 'Depreciation - fibre'); row('dc', 'Depreciation - CPP'); row('de', 'Depreciation - ethanol')
    row('ef', 'Segment EBITDA - fibre (result + dep - other income allocated on revenue)'); row('ec', 'Segment EBITDA - CPP'); row('ee', 'Segment EBITDA - ethanol')
    row('af', 'Segment assets - fibre'); row('ac', 'Segment assets - CPP'); row('ae', 'Segment assets - ethanol')
    row('rocf', '  fibre PBIT / segment assets'); row('rocc', '  CPP PBIT / segment assets'); row('roce', '  ethanol PBIT / segment assets')
    sec('Acrylic staple fibre, tow and tops (Thakurdwara, Moradabad, UP)')
    row('fcap', 'Capacity (MT a year)'); row('fprod', 'Production (MT)'); row('fsale', 'Sales (MT)'); row('futil', '  utilisation (sales / capacity)')
    row('fexp', 'Exports (MT)'); row('freal', 'Realisation (Rs./kg sold)'); row('facn', 'ACN consumed (Rs. crore)'); row('facnkg', 'ACN cost per kg of fibre produced (Rs./kg)')
    row('facnpx', 'Implied ACN price (Rs./kg) = ACN cost per kg / 0.889 kg ACN per kg fibre'); row('fspr', 'Spread: realisation - ACN per kg (Rs./kg)', b=True)
    row('febitkg', 'Fibre PBIT per kg (Rs.)'); row('febitdakg', 'Fibre EBITDA per kg (Rs.)', b=True); row('fconv', 'Conversion cost per kg = spread - EBITDA/kg (Rs.)')
    row('fvam', 'VAM consumed (Rs. crore)')
    sec('CPP film (cast polypropylene; 5,000 MT from Sep-2017, 10,000 MT from Mar-2019)')
    row('ccap', 'Capacity (MT, time-weighted)'); row('cprod', 'Production (MT)'); row('csale', 'Sales (MT)'); row('cutil', '  utilisation (sales / capacity)')
    row('creal', 'Realisation (Rs./kg)'); row('cpoly', 'Homo-polymer (PP) cost per kg produced (Rs.)'); row('cspr', 'Spread over polymer (Rs./kg)', b=True)
    row('cebitkg', 'CPP PBIT per kg (Rs.)'); row('cebitdakg', 'CPP EBITDA per kg (Rs.)', b=True)
    sec('Ethanol (grain distillery, 150 KLPD from 25-Mar-2025; consents for 180 KLPD)')
    row('ecap', 'Capacity (KL a year)'); row('eprod', 'Production (KL)'); row('esale', 'Sales (KL)'); row('eutil', '  utilisation (production / capacity)')
    row('ereal', 'Realisation per litre incl. DDGS (Rs.)'); row('egrain', 'Grain cost per litre produced (Rs.)'); row('espr', 'Spread over grain (Rs./litre)', b=True)
    row('eebitdal', 'Ethanol EBITDA per litre (Rs.)', b=True)
    sec('Other operating data')
    row('pfkg', 'Power and fuel (Rs. crore)'); row('emp', 'Employees (permanent, on rolls; FY26 average)'); row('revemp', 'Revenue per employee (Rs. crore)')
    row('gin', 'Revenue - within India'); row('gout', 'Revenue - outside India'); row('chk_g', 'CHECK: geography vs revenue (should be 0)', c=RED); row('top10', 'Top-10 customers share of sales')
    sec('Mid-cycle check (FY17-FY26)')
    row('mc_febit', '10-year average fibre PBIT per kg (Rs.)'); row('mc_fm', '10-year average fibre PBIT margin'); row('mc_ebm', '10-year average company EBITDA margin')
    row('mc_spr', '10-year average fibre spread over ACN (Rs./kg)'); row('mc_h1', 'H1FY27 fibre PBIT margin (Quarterly sheet)'); row('mc_h1e', 'H1FY27 company EBITDA margin')
    row('mc_read', 'Read')
    SG, O = D.SEG, D.OPS
    for i, c in enumerate(H):
        inp(sg, f'{c}{S["rf"]}', cr(SG['rev_fib'][i])); inp(sg, f'{c}{S["rc"]}', cr(SG['rev_cpp'][i])); inp(sg, f'{c}{S["re"]}', cr(SG['rev_eth'][i]))
        inp(sg, f'{c}{S["xf"]}', cr(SG['res_fib'][i])); inp(sg, f'{c}{S["xc"]}', cr(SG['res_cpp'][i])); inp(sg, f'{c}{S["xe"]}', cr(SG['res_eth'][i]))
        fx(sg, f'{c}{S["chk_x"]}', f"=ROUND({c}{S['xf']}+{c}{S['xc']}+{c}{S['xe']}-('P&L'!{c}{R['pbt']}+'P&L'!{c}{R['fin']}+'P&L'!{c}{R['exc']}),1)", c=RED)
        for k, kk in [('df', 'dep_fib'), ('dc', 'dep_cpp'), ('de', 'dep_eth'), ('af', 'ass_fib'), ('ac', 'ass_cpp'), ('ae', 'ass_eth')]:
            if SG[kk][i] is not None: inp(sg, f'{c}{S[k]}', cr(SG[kk][i]))
        if i == 0:
            fx(sg, f'{c}{S["ef"]}', f"='P&L'!{c}{R['ebitda']}", c=GREEN)
        elif SG['dep_fib'][i] is not None:
            for k, x, d_, rv in [('ef', 'xf', 'df', 'rf'), ('ec', 'xc', 'dc', 'rc'), ('ee', 'xe', 'de', 're')]:
                fx(sg, f'{c}{S[k]}', f"={c}{S[x]}+{c}{S[d_]}-'P&L'!{c}{R['oi']}*{c}{S[rv]}/'P&L'!{c}{R['rev']}")
        for k, a_, x in [('rocf', 'af', 'xf'), ('rocc', 'ac', 'xc'), ('roce', 'ae', 'xe')]:
            if (SG['ass_' + {'af': 'fib', 'ac': 'cpp', 'ae': 'eth'}[a_]][i]) is not None: fx(sg, f'{c}{S[k]}', f'={c}{S[x]}/{c}{S[a_]}', PCT)
        inp(sg, f'{c}{S["fcap"]}', O['fib_cap'][i], INT); inp(sg, f'{c}{S["fprod"]}', O['fib_prod'][i], INT); inp(sg, f'{c}{S["fsale"]}', O['fib_sale'][i], INT)
        if O['fib_exp'][i] is not None: inp(sg, f'{c}{S["fexp"]}', O['fib_exp'][i], INT)
        inp(sg, f'{c}{S["facn"]}', cr(O['acn'][i])); inp(sg, f'{c}{S["fvam"]}', cr(O['vam'][i]))
        fx(sg, f'{c}{S["facnkg"]}', f'={c}{S["facn"]}*1E4/{c}{S["fprod"]}', NUM)
        fx(sg, f'{c}{S["facnpx"]}', f'={c}{S["facnkg"]}/{D.ACN_FACTOR}', NUM)
        fx(sg, f'{c}{S["febitkg"]}', f'={c}{S["xf"]}*1E4/{c}{S["fsale"]}', NUM)
        if i == 0 or SG['dep_fib'][i] is not None:
            fx(sg, f'{c}{S["febitdakg"]}', f'={c}{S["ef"]}*1E4/{c}{S["fsale"]}', NUM, b=True)
            fx(sg, f'{c}{S["fconv"]}', f'={c}{S["fspr"]}-{c}{S["febitdakg"]}', NUM)
        if O['cpp_cap'][i]: inp(sg, f'{c}{S["ccap"]}', O['cpp_cap'][i], INT)
        if O['cpp_prod'][i]:
            inp(sg, f'{c}{S["cprod"]}', O['cpp_prod'][i], INT); inp(sg, f'{c}{S["csale"]}', O['cpp_sale'][i], INT)
            fx(sg, f'{c}{S["cutil"]}', f'={c}{S["csale"]}/{c}{S["ccap"]}', PCT); fx(sg, f'{c}{S["creal"]}', f'={c}{S["rc"]}*1E4/{c}{S["csale"]}', NUM)
            fx(sg, f'{c}{S["cebitkg"]}', f'={c}{S["xc"]}*1E4/{c}{S["csale"]}', NUM)
            if O['homo'][i]:
                fx(sg, f'{c}{S["cpoly"]}', f'={cr(O["homo"][i])}*1E4/{c}{S["cprod"]}', NUM); fx(sg, f'{c}{S["cspr"]}', f'={c}{S["creal"]}-{c}{S["cpoly"]}', NUM, b=True)
            if SG['dep_cpp'][i] is not None: fx(sg, f'{c}{S["cebitdakg"]}', f'={c}{S["ec"]}*1E4/{c}{S["csale"]}', NUM, b=True)
        if O['eth_sale'][i] > 1000:
            inp(sg, f'{c}{S["ecap"]}', O['eth_cap_kl'][i], INT); inp(sg, f'{c}{S["eprod"]}', O['eth_prod'][i], INT); inp(sg, f'{c}{S["esale"]}', O['eth_sale'][i], INT)
            fx(sg, f'{c}{S["eutil"]}', f'={c}{S["eprod"]}/{c}{S["ecap"]}', PCT); fx(sg, f'{c}{S["ereal"]}', f'={c}{S["re"]}*1E4/{c}{S["esale"]}', NUM2)
            fx(sg, f'{c}{S["egrain"]}', f'={cr(O["grain"][i])}*1E4/{c}{S["eprod"]}', NUM2); fx(sg, f'{c}{S["espr"]}', f'={c}{S["ereal"]}-{c}{S["egrain"]}', NUM2, b=True)
            fx(sg, f'{c}{S["eebitdal"]}', f'={c}{S["ee"]}*1E4/{c}{S["esale"]}', NUM2, b=True)
        elif O['eth_sale'][i]:
            inp(sg, f'{c}{S["ecap"]}', O['eth_cap_kl'][i], INT); inp(sg, f'{c}{S["eprod"]}', O['eth_prod'][i], INT); inp(sg, f'{c}{S["esale"]}', O['eth_sale'][i], INT)
        fx(sg, f'{c}{S["pfkg"]}', f"='P&L'!{c}{R['pf']}", c=GREEN); inp(sg, f'{c}{S["emp"]}', O['emp_no'][i], INT)
        fx(sg, f'{c}{S["revemp"]}', f"='P&L'!{c}{R['rev']}/{c}{S['emp']}", NUM2)
        if SG['geo_in'][i] is not None:
            inp(sg, f'{c}{S["gin"]}', cr(SG['geo_in'][i])); inp(sg, f'{c}{S["gout"]}', cr(SG['geo_out'][i]))
            fx(sg, f'{c}{S["chk_g"]}', f"=ROUND({c}{S['gin']}+{c}{S['gout']}-'P&L'!{c}{R['rev']},1)", c=RED)
        if O['top10'][i] is not None: inp(sg, f'{c}{S["top10"]}', O['top10'][i], PCT)
    for c in ALL:
        fx(sg, f'{c}{S["rt"]}', f'={c}{S["rf"]}+{c}{S["rc"]}+{c}{S["re"]}', b=True)
        fx(sg, f'{c}{S["chk_r"]}', f"=ROUND({c}{S['rt']}-'P&L'!{c}{R['rev']},1)", c=RED)
        for k, rv in [('sf', 'rf'), ('sc', 'rc'), ('se', 're')]: fx(sg, f'{c}{S[k]}', f'={c}{S[rv]}/{c}{S["rt"]}', PCT)
        if c in H:
            fx(sg, f'{c}{S["mf"]}', f'={c}{S["xf"]}/{c}{S["rf"]}', PCT)
            fx(sg, f'{c}{S["mc"]}', f'=IF({c}{S["rc"]}>0,{c}{S["xc"]}/{c}{S["rc"]},"")', PCT); fx(sg, f'{c}{S["me"]}', f'=IF({c}{S["re"]}>10,{c}{S["xe"]}/{c}{S["re"]},"")', PCT)
        fx(sg, f'{c}{S["futil"]}', f'={c}{S["fsale"]}/{c}{S["fcap"]}', PCT); fx(sg, f'{c}{S["freal"]}', f'={c}{S["rf"]}*1E4/{c}{S["fsale"]}', NUM)
        fx(sg, f'{c}{S["fspr"]}', f'={c}{S["freal"]}-{c}{S["facnkg"]}', NUM, b=True)
    srcs = {'rf': 'Segment note: ' + '; '.join(f'{y} {D.SEG_SRC[y]}' for y in D.YRS), 'xf': 'Same pages. Segment results add up to PBT + finance cost + exceptional, so other income sits inside segments.',
            'ef': 'EBITDA by segment is our derivation: the company does not allocate other income separately; we allocate it on revenue share.',
            'df': 'Segment depreciation disclosed from FY21 (AR FY22 p.84 onwards).', 'af': 'Segment assets: same segment notes; FY24 ethanol = CWIP.',
            'fcap': D.OPS_SRC['fib_prod'] + '. Capacity 42,000 MTPA (AR FY26 p.11; CARE). AR FY23 p.10 says 45,000 MTPA (conflict). FY19 production 43,462 MT exceeded 42,000.',
            'fsale': D.OPS_SRC['fib_sale'], 'fexp': D.OPS_SRC['fib_exp'], 'facn': D.OPS_SRC['acn'],
            'facnpx': 'ACN factor 0.889 kg/kg calibrated on CARE ACN prices Rs.97.47/kg FY21 and Rs.171.57/kg FY22 (CARE Aug-2022 p.2): implied 97.4 and 171.5. ' + D.CARE_KG['acn_usd'],
            'freal': 'CARE: ASF realisation Rs.145.47/kg FY21, 218.53 FY22, 205.12 FY23, 157 FY24 (CARE Aug-2022 p.2, Aug-2023 p.2, Jul-2024 p.2) - matches.',
            'ccap': D.OPS_SRC['cpp'], 'creal': 'CARE: CPP Rs.126.3/kg FY21, 160.85 FY22, 143.42 FY23, 120.12 FY24 - matches.',
            'ecap': D.OPS_SRC['eth'] + '. FY26 capacity shown at 150 KLPD x 330 days.', 'egrain': 'Grain consumed (AR FY26 p.73) / KL produced.',
            'emp': D.OPS_SRC['emp_no'], 'gin': 'Geographical segment: AR FY24 p.86, FY25 p.85, FY26 p.81. AR FY26 p.81 prints FY25 as 57,719.70 + 5,423.48 lakh, which adds to 1,000 lakh more than FY25 revenue (document error): AR FY25 figures used.', 'top10': D.OPS_SRC['top10'],
            'pfkg': 'FY23 power and fuel spike (Rs.92 cr) = imported coal prices; FY26 includes the distillery boiler.'}
    for k, t in srcs.items(): src(sg, S[k], t)
    fx(sg, f'K{S["mc_febit"]}', f'=AVERAGE(B{S["febitkg"]}:K{S["febitkg"]})', NUM); fx(sg, f'K{S["mc_fm"]}', f'=AVERAGE(B{S["mf"]}:K{S["mf"]})', PCT)
    fx(sg, f'K{S["mc_ebm"]}', f"=AVERAGE('P&L'!B{R['ebm']}:'P&L'!K{R['ebm']})", PCT); fx(sg, f'K{S["mc_spr"]}', f'=AVERAGE(B{S["fspr"]}:K{S["fspr"]})', NUM)

    # =========================================================== Quarterly
    q = wb.create_sheet('Quarterly')
    put(q, 'A1', 'Quarterly results, Rs. crore (standalone; quarters as reported in the results PDFs - scanned, read from page images)', b=True)
    QC = [CL(2 + i) for i in range(len(D.Q))]   # B..M
    hdr(q, 2, D.Q + ['H1FY26', 'H1FY27', 'TTM Sep-26']); put(q, 'Q2', 'Source', b=True)
    qk = ['rev', 'oi', 'rm', 'inv', 'emp', 'fin', 'dep', 'oth', 'ebitda', 'ebm', 'exc', 'pbt', 'pbtrep', 'chk', 'tax', 'pat', 'eps', 'yoy',
          'rf', 'rc', 're', 'chk_r', 'xf', 'xc', 'xe', 'chk_x', 'mf', 'mc', 'me']
    QR = {k: 3 + i for i, k in enumerate(qk)}
    QL = {'rev': 'Revenue from operations', 'oi': 'Other income', 'rm': 'Cost of materials consumed (incl. stock in trade)', 'inv': 'Change in inventories',
          'emp': 'Employee benefits', 'fin': 'Finance costs', 'dep': 'Depreciation', 'oth': 'Other expenses', 'ebitda': 'EBITDA (excl. other income)',
          'ebm': '  EBITDA margin', 'exc': 'Exceptional items', 'pbt': 'PBT (built up)', 'pbtrep': 'PBT (reported)', 'chk': 'CHECK: PBT built vs reported (should be 0)',
          'tax': 'Tax', 'pat': 'PAT', 'eps': 'EPS (Rs.)', 'yoy': '  revenue growth y-o-y', 'rf': 'Segment revenue - fibre', 'rc': 'Segment revenue - CPP film',
          're': 'Segment revenue - ethanol (distillery)', 'chk_r': 'CHECK: segment revenue vs revenue', 'xf': 'Segment result - fibre', 'xc': 'Segment result - CPP',
          'xe': 'Segment result - ethanol', 'chk_x': 'CHECK: segment results vs PBT + finance + exceptional', 'mf': '  fibre PBIT margin', 'mc': '  CPP PBIT margin', 'me': '  ethanol PBIT margin'}
    for k in qk: lab(q, QR[k], QL[k], b=k in ('rev', 'ebitda', 'pat'), c=RED if k.startswith('chk') else BLACK)
    idx = {'rev': 0, 'oi': 1, 'rm': 2, 'inv': 3, 'emp': 4, 'fin': 5, 'dep': 6, 'oth': 7, 'exc': 8, 'pbtrep': 9, 'tax': 10, 'rf': 12, 'rc': 13, 're': 14, 'xf': 15, 'xc': 16, 'xe': 17}
    for i, qq in enumerate(D.Q):
        c = QC[i]; v = D.QD[qq]
        for k, ix in idx.items(): inp(q, f'{c}{QR[k]}', v[ix])
    allq = QC + ['N', 'O', 'P']
    for c in allq:
        fx(q, f'{c}{QR["ebitda"]}', f'={c}{QR["rev"]}-{c}{QR["rm"]}-{c}{QR["inv"]}-{c}{QR["emp"]}-{c}{QR["oth"]}', b=True)
        fx(q, f'{c}{QR["ebm"]}', f'={c}{QR["ebitda"]}/{c}{QR["rev"]}', PCT)
        fx(q, f'{c}{QR["pbt"]}', f'={c}{QR["ebitda"]}-{c}{QR["dep"]}+{c}{QR["oi"]}-{c}{QR["fin"]}-{c}{QR["exc"]}')
        fx(q, f'{c}{QR["chk"]}', f'=ROUND({c}{QR["pbt"]}-{c}{QR["pbtrep"]},2)', c=RED)
        fx(q, f'{c}{QR["pat"]}', f'={c}{QR["pbt"]}-{c}{QR["tax"]}', b=True); fx(q, f'{c}{QR["eps"]}', f'={c}{QR["pat"]}/{D.SHARES}', '0.00')
        fx(q, f'{c}{QR["chk_r"]}', f'=ROUND({c}{QR["rf"]}+{c}{QR["rc"]}+{c}{QR["re"]}-{c}{QR["rev"]},2)', c=RED)
        fx(q, f'{c}{QR["chk_x"]}', f'=ROUND({c}{QR["xf"]}+{c}{QR["xc"]}+{c}{QR["xe"]}-({c}{QR["pbt"]}+{c}{QR["fin"]}+{c}{QR["exc"]}),2)', c=RED)
        fx(q, f'{c}{QR["mf"]}', f'={c}{QR["xf"]}/{c}{QR["rf"]}', PCT); fx(q, f'{c}{QR["mc"]}', f'={c}{QR["xc"]}/{c}{QR["rc"]}', PCT)
        fx(q, f'{c}{QR["me"]}', f'=IF({c}{QR["re"]}>5,{c}{QR["xe"]}/{c}{QR["re"]},"")', PCT)
    for i in range(4, len(QC)): fx(q, f'{QC[i]}{QR["yoy"]}', f'={QC[i]}{QR["rev"]}/{QC[i-4]}{QR["rev"]}-1', PCT)
    sumk = [k for k in idx]
    for k in sumk:
        fx(q, f'N{QR[k]}', f'=H{QR[k]}+I{QR[k]}'); fx(q, f'O{QR[k]}', f'=L{QR[k]}+M{QR[k]}'); fx(q, f'P{QR[k]}', f'=SUM(J{QR[k]}:M{QR[k]})')
    fx(q, f'O{QR["yoy"]}', f'=O{QR["rev"]}/N{QR["rev"]}-1', PCT)
    src(q, QR['rev'], '; '.join(f'{k} {v}' for k, v in D.QSRC.items()), col='Q')
    src(q, QR['rm'], 'Q1FY26 and Q2FY26 do not show the Rs.0.10 cr stock-in-trade purchase that appears in H1FY26 (Res Q2FY27 p.2): immaterial.', col='Q')
    QS = QR
    # Sep-2026 balance sheet memo
    m0 = QR['me'] + 2; lab(q, m0, 'Balance sheet 30-Sep-2026 (Res Q2FY27 p.4) vs 31-Mar-2026', b=True); hdr(q, m0, ['Sep-26', 'Mar-26', 'change'])
    for i, (k, t) in enumerate([('invy', 'Inventories'), ('recv', 'Trade receivables'), ('cinv', 'Current investments'), ('cash', 'Cash'), ('bank', 'Other bank balances'),
                                ('ltb', 'Long-term borrowings'), ('stb', 'Short-term borrowings'), ('tp', 'Trade payables'), ('oeq', 'Other equity')]):
        rr = m0 + 1 + i; lab(q, rr, t); inp(q, f'B{rr}', D.BS_SEP26[k]); fx(q, f'C{rr}', f'=BS!K{DR[k]}', c=GREEN); fx(q, f'D{rr}', f'=B{rr}-C{rr}')
    src(q, m0 + 1, 'Inventory up Rs.91 cr in six months while liquid funds fell Rs.57 cr: working capital absorbed most of H1 profit.', col='Q')
    fx(sg, f'K{S["mc_h1"]}', f'=Quarterly!O{QR["mf"]}', PCT, GREEN); fx(sg, f'K{S["mc_h1e"]}', f'=Quarterly!O{QR["ebm"]}', PCT, GREEN)
    put(sg, f'B{S["mc_read"]}', 'Today is well ABOVE mid-cycle: H1FY27 fibre margin ~2x the 10-year average, company EBITDA margin ~2x the 10-year average.', i=True)

    # =========================================================== Sources
    so = wb.create_sheet('Sources')
    put(so, 'A1', 'Documents used (pack: raw/ in Pasupati-Investor-Docs.zip). Printed page = PDF page - 3 (AR FY17-FY24) or - 4 (AR FY25-FY26).', b=True)
    hdr(so, 2, ['Document', 'Period / date', 'Printed-page offset', 'Where from', 'Used for'], start=1)
    docs = [('AR_FY17 .. AR_FY24', 'FY17-FY24', 'printed = PDF - 3', 'bseindia.com (AttachHis / bseplus)', 'P&L, BS, CF, segments, volumes, RM heads, employees'),
            ('AR_FY25, AR_FY26', 'FY25-FY26', 'printed = PDF - 4', 'bseindia.com AttachHis', 'same + ethanol, related parties, remuneration, borrowings'),
            ('RES_Q*.pdf (27 files)', 'Q1FY22 - Q2FY27', 'PDF pages', 'pasupatiacrylon.com/investors', 'Quarterly P&L and segments (scanned; read from images)'),
            ('CARE_2022-08 .. CARE_2026-06', 'Aug-2022 - Jun-2026', 'PDF pages', 'careratings.com', 'ACN price, realisation per kg, top-10 customers, project cost, 240 KLPD plan'),
            ('ANN_2026-11-13 ethanol allocation', '13-Nov-2026', 'p.1-2', 'BSE AnnPdfOpen', '50,745 KL for ESY 2026-27, Rs.334 cr'),
            ('ANN_2026-11-27 postal ballot', '26/27-Nov-2026', 'p.2-14', 'BSE AnnPdfOpen', 'MD remuneration above Rs.5 cr'),
            ('ANN ethanol COD / update', 'Mar-2025', 'p.1', 'company website', 'COD 24-Mar-2025'),
            ('ANN fire incident', '14-Jun-2025', 'p.1-2', 'company website', 'fire 13-Jun-2025, insured'),
            ('ANN promoter group merger / inter-se', 'Sep / Dec-2025', 'p.1-2', 'company website', 'promoter entities merged into Arihant Exports'),
            ('SHP_2025-03 .. SHP_2026-03', 'quarterly', '-', 'company website', 'promoter 65.87%, no pledge'),
            ('PASUPTAC_price_history.csv', '2005 - 27-Nov-2026', '-', 'Screener chart API (weekly; daily last 12 months)', 'CMP, P/E history'),
            ('Screener company pages (web/)', '28-Nov-2026', '-', 'screener.in', 'peer prices and P/E (to be checked on Bloomberg)')]
    for i, row_ in enumerate(docs):
        for j, v in enumerate(row_): put(so, f'{CL(1 + j)}{3 + i}', v)
    put(so, 'A17', 'Conflicts recorded', b=True)
    conf = ['Fibre capacity 45,000 MTPA in AR FY23 p.10 vs 42,000 MTPA in AR FY24-FY26 and all CARE reports: 42,000 used.',
            'FY18 fibre sales 38,811 MT (AR FY18 p.7) vs 38,590 MT (AR FY19 p.7): FY18 AR used.',
            'FY18 revenue 57,949.01 lakh (AR FY18) vs 57,414.66 lakh in AR FY19 (freight netted, 534.35): AR FY18 used.',
            'FY19 materials 65,155.81 (AR FY19) vs 65,227.64 (AR FY20 restated): AR FY19 used.',
            'FY21 CFO 1,349.50 (AR FY21) vs 1,375.98 (AR FY22); FY23 3,002.35 vs 2,735.46 (AR FY24); FY24 7,271.22 vs 7,180.79 (AR FY25): own-year AR used.',
            'FY25 equity capital 8,914.10 (AR FY25) vs 8,913.31 (AR FY26, forfeited shares moved to other equity): own-year AR used.',
            'FY25 geography: AR FY26 p.81 comparatives (57,719.70 India + 5,423.48 exports) add to 63,143.18 vs revenue 62,143.18 lakh - a printing error; AR FY25 p.85 (56,513.08 + 5,630.10) used.',
            'FY17: Indian GAAP AR FY17 (revenue 46,086.62 lakh net of excise, PAT 3,403.97) vs Ind AS comparative in AR FY18 (PAT 3,422.31): Ind AS used.']
    for i, t in enumerate(conf): put(so, f'A{18 + i}', t)
    widths(so, {'A': 44, 'B': 20, 'C': 18, 'D': 36, 'E': 70})

    for ws in (pl, bs, cf, ra, sg, q):
        widths(ws, {'A': 62, **{c: 9.5 for c in H + FC}, 'P': 10, SRC: 110})
    widths(q, {'A': 50, **{CL(2 + i): 9 for i in range(15)}, 'Q': 100})
    for ws in wb.worksheets: ws.freeze_panes = 'B3'
    if not v2:
        return wb, None

    # =========================================================== Drivers (v2)
    dv = wb.create_sheet('Drivers', 0)
    put(dv, 'A1', 'Drivers: every assumption is a blue input with a tag in column H: [A] actual, [M] management, [E] our estimate. Rs. crore unless stated.', b=True)
    put(dv, 'A3', 'Scenario selector (1 bear, 2 base, 3 bull; 4 = floor memo, used only by the runner)', b=True); inp(dv, 'C3', 2, '0', key=True)
    put(dv, 'D3', '=CHOOSE(C3,"BEAR","BASE","BULL","FLOOR")', b=True)
    hdr(dv, 5, YF, start=3); put(dv, 'B5', 'unit', b=True); put(dv, 'H5', 'Tag and source', b=True)
    X = {}; rr = [6]
    def nxt():
        rr[0] += 1; return rr[0]
    def section(t):
        r_ = nxt(); r_ = nxt(); lab(dv, r_, t, b=True)
    def single(k, t, unit, vals, note, fm=NUM2, key=False):
        r_ = nxt(); X[k] = r_; lab(dv, r_, t); put(dv, f'B{r_}', unit)
        for j, v in enumerate(vals):
            if v is not None: inp(dv, f'{DV[j]}{r_}', v, fm, key)
        put(dv, f'H{r_}', note); return r_
    def scen(k, t, unit, bear, base, bull, floor, note, fm=NUM2, key=True):
        r0 = nxt(); lab(dv, r0, t, b=True); put(dv, f'B{r0}', unit); put(dv, f'H{r0}', note)
        rows_ = []
        for nm, vals in [('bear', bear), ('base', base), ('bull', bull), ('floor', floor)]:
            r_ = nxt(); lab(dv, r_, f'    {nm}'); rows_.append(r_)
            for j, v in enumerate(vals): inp(dv, f'{DV[j]}{r_}', v, fm, key and nm == 'base')
        for j, c in enumerate(DV):
            fx(dv, f'{c}{r0}', f'=CHOOSE($C$3,{c}{rows_[0]},{c}{rows_[1]},{c}{rows_[2]},{c}{rows_[3]})', fm, b=True)
        X[k] = r0; return r0
    def calc(k, t, unit, f, fm=NUM2, b=False, note=''):
        r_ = nxt(); X[k] = r_; lab(dv, r_, t, b=b); put(dv, f'B{r_}', unit)
        for j, c in enumerate(DV): fx(dv, f'{c}{r_}', f(j, c), fm, b=b)
        if note: put(dv, f'H{r_}', note)
        return r_

    section('A. Acrylic fibre: volume x (ACN pass-through + spread)')
    single('fcap', 'Fibre capacity', 'MT', [42000] * 4, '[A] 42,000 MTPA (AR FY26 p.11; CARE Jun-2026 p.3). No fibre expansion announced.', INT)
    scen('futil', 'Fibre utilisation (sales / capacity)', '%', [0.85, 0.80, 0.82, 0.85], [0.93, 0.92, 0.92, 0.93], [0.95, 0.95, 0.95, 0.95], [0.90, 0.90, 0.90, 0.90],
         '[A] 90% FY26, 81% FY25, 75% FY24, 84% FY23; 106% FY19 peak; H1FY27 fibre revenue +14% y-o-y (Res Q2FY27 p.3). [E] base ~92%; bear = imports rise (no anti-dumping duty) and volume falls to the FY24-FY25 range; floor = FY26 volume.', PCT)
    calc('fvol', 'Fibre sales volume', 'MT', lambda j, c: f'={c}{X["fcap"]}*{c}{X["futil"]}', INT)
    scen('acn', 'ACN price (feedstock, imported, USD-linked)', 'Rs./kg', [95, 92, 95, 98], [104, 104, 105, 106], [108, 110, 112, 114], [104, 104, 105, 106],
         '[A] implied Rs.104/kg FY26, 114 FY25, 113 FY24, 136 FY23, 172 FY22, 97 FY21 (Segments; CARE Aug-2022 p.2). Passed through to fibre price with a ~5-month lag (CARE Jun-2026 p.2). [E] base flat; bear = ACN falls (inventory losses sit in the spread line).', NUM)
    single('afac', 'kg ACN per kg fibre', 'kg/kg', [D.ACN_FACTOR] * 4, '[E] 0.889, calibrated on CARE ACN prices FY21-FY22 (Segments row note).', '0.000')
    calc('acnkg', 'ACN cost per kg of fibre', 'Rs./kg', lambda j, c: f'={c}{X["acn"]}*{c}{X["afac"]}', NUM)
    scen('fspr', 'Fibre spread over ACN (realisation - ACN per kg)', 'Rs./kg', [66, 55, 55, 57], [72, 68, 67, 68], [77, 77, 78, 80], [70, 64.4, 66.3, 68.3],
         '[A] Rs.62 FY26, 58 FY25, 56 FY24, 83 FY23, 66 FY22, 59 FY21, 49 FY20, 48 FY19, 46 FY18, 53 FY17 (Segments). H1FY27 ~Rs.74 implied (fibre PBIT Rs.57.6 cr, margin 18.3%). [E] base: H2FY27 eases, FY28-30 back towards mid-cycle EBITDA/kg; bull holds today; bear = trough (FY20/FY24 EBITDA ~Rs.6/kg); floor = mid-cycle EBITDA Rs.15/kg from FY28.', NUM)
    calc('freal', 'Fibre realisation (ACN cost + spread)', 'Rs./kg', lambda j, c: f'={c}{X["acnkg"]}+{c}{X["fspr"]}', NUM, b=True)
    single('fconv', 'Fibre conversion cost (VAM, DMF, power, staff, freight, other)', 'Rs./kg', [46.6, 48.0, 49.4, 50.9], '[A] Rs.45.3/kg FY26, 44.8 FY25, 50.2 FY24, 67.3 FY23 (coal spike), 49.1 FY22, 41.7 FY21 (Segments). [E] +3% a year.', NUM)
    calc('febkg', 'Fibre EBITDA per kg', 'Rs./kg', lambda j, c: f'={c}{X["fspr"]}-{c}{X["fconv"]}', NUM, b=True,
         note='[A] Rs.17.0 FY26, 12.9 FY25, 6.0 FY24, 15.7 FY23, 17.0 FY22, 17.3 FY21, 16.8 FY17; ~Rs.29 implied H1FY27. Mid-cycle ~Rs.15.')
    calc('frev', 'Fibre revenue', 'Rs cr', lambda j, c: f'={c}{X["fvol"]}*{c}{X["freal"]}/1E4', NUM, b=True)
    calc('facnc', 'Fibre ACN cost', 'Rs cr', lambda j, c: f'={c}{X["fvol"]}*{c}{X["acnkg"]}/1E4', NUM)
    calc('feb', 'Fibre EBITDA', 'Rs cr', lambda j, c: f'={c}{X["fvol"]}*{c}{X["febkg"]}/1E4', NUM, b=True)
    single('add', 'memo: anti-dumping duty on acrylic fibre imports (China, Peru, Thailand)', 'flag', [0, 0, 0, 0],
           '[A]/[E] DGTR final findings 18-Aug-2025 recommended USD 34-920/t for 5 years on applications by Indian Acrylics and Pasupati (DGTR/press, KNN 22-Aug-2025). Not notified: Indian Acrylics AR FY26 (Sep-2026, PDF p.13, 21) says the Ministry of Finance has not issued the notification and dumping continues. 0 = not in force (check CBIC). Bull spread assumes support (duty or tight supply); bear = no duty and imports rise. Earlier petition turned down (AR FY18 p.7).', '0')

    section('B. CPP film: volume x (polymer pass-through + spread)')
    single('ccap', 'CPP capacity', 'MT', [10000] * 4, '[A] 10,000 MTPA since 26-Mar-2019 (AR FY19 p.7; AR FY26 p.11).', INT)
    scen('cutil', 'CPP utilisation', '%', [0.75, 0.70, 0.72, 0.75], [0.85, 0.86, 0.87, 0.88], [0.92, 0.95, 0.95, 0.95], [0.76, 0.76, 0.76, 0.76],
         '[A] 76% FY26, 64% FY25, 65% FY24, 76% FY23, 62% FY22, 39% FY21; H1FY27 CPP revenue +31% y-o-y. [E]', PCT)
    calc('cvol', 'CPP sales volume', 'MT', lambda j, c: f'={c}{X["ccap"]}*{c}{X["cutil"]}', INT)
    single('cpoly', 'Polymer (PP homo-polymer) cost per kg of film', 'Rs./kg', [66.3, 67.0, 67.5, 68.0], '[A] Rs.66.3 FY26, 71.3 FY25, 67.7 FY24, 83.7 FY23 (Segments). [E] near flat; passed through.', NUM)
    scen('cspr', 'CPP spread over polymer', 'Rs./kg', [62, 56, 57, 58], [70, 68.5, 69.5, 70.5], [74, 74.5, 75.5, 76.5], [64.0, 65.4, 66.8, 68.3],
         '[A] Rs.63.5 FY26, 54.6 FY25, 52.4 FY24, 58.5 FY23; H1FY27 CPP margin 12.2% (Res Q2FY27 p.3). [E] base EBITDA ~Rs.13-17/kg; floor = FY26 Rs.12.5/kg; bear = FY23-FY25 losses come back.', NUM)
    single('cconv', 'CPP conversion cost', 'Rs./kg', [52.5, 54.1, 55.7, 57.4], '[A] Rs.51.0/kg FY26 (spread 63.5 - EBITDA 12.5). [E] +3% a year.', NUM)
    calc('cebkg', 'CPP EBITDA per kg', 'Rs./kg', lambda j, c: f'={c}{X["cspr"]}-{c}{X["cconv"]}', NUM, b=True, note='[A] Rs.12.5 FY26, 1.5 FY25, -4.4 FY24, -7.3 FY23, 15.9 FY22, 14.2 FY21.')
    calc('crev', 'CPP revenue', 'Rs cr', lambda j, c: f'={c}{X["cvol"]}*({c}{X["cpoly"]}+{c}{X["cspr"]})/1E4', NUM, b=True)
    calc('cpolyc', 'CPP polymer cost', 'Rs cr', lambda j, c: f'={c}{X["cvol"]}*{c}{X["cpoly"]}/1E4', NUM)
    calc('ceb', 'CPP EBITDA', 'Rs cr', lambda j, c: f'={c}{X["cvol"]}*{c}{X["cebkg"]}/1E4', NUM, b=True)

    section('C. Ethanol (grain distillery): KLPD x days x utilisation x (grain + spread); OMC-set prices')
    scen('eklpd', 'Ethanol capacity', 'KLPD', [180] * 4, [180] * 4, [180, 180, 240, 240], [180] * 4,
         '[A] 150 KLPD built; consents for 180 KLPD received (AR FY26 p.11; CARE Jun-2026 p.3). [M/CARE] 240 KLPD "envisaged" (CARE Jun-2026 p.2) - no board approval, cost or date disclosed: bull only, from FY29E. [E]', INT)
    single('edays', 'Operating days a year', 'days', [330] * 4, '[E] industry norm; FY26 production 41,923 KL = 254 days at 165 KLPD average.', INT)
    scen('eutil', 'Ethanol utilisation', '%', [0.58, 0.65, 0.65, 0.65], [0.64, 0.82, 0.83, 0.84], [0.66, 0.90, 0.92, 0.92], [0.64, 0.50, 0.50, 0.50],
         '[A] FY26 41,923 KL; H1FY27 distillery revenue Rs.133 cr (~17,000 KL) vs Rs.171 cr H1FY26 (Res Q2FY27 p.3). OMC allocation ESY 2026-27 = 50,745 KL = 85% of 180 KLPD x 330 (BSE 13-Nov-2026). [E] base 82-84% (slightly below allocation); floor = only the allocated quantity (7 months of ESY27 in FY28, nothing assumed beyond); bear = allocations cut (India capacity ~2,000 cr litres vs ~1,100 cr litres demand, AR FY26 p.12).', PCT)
    calc('evol', 'Ethanol sales volume', 'KL', lambda j, c: f'={c}{X["eklpd"]}*{c}{X["edays"]}*{c}{X["eutil"]}', INT)
    scen('ereal', 'Ethanol realisation per litre incl. DDGS', 'Rs./litre', [78, 77, 77, 78], [80, 80.5, 81.5, 82.5], [81, 82, 83.5, 85], [80, 80.5, 81.5, 82.5],
         '[A] Rs.78.8/l FY26 (segment revenue / KL sold). ESY27 allocation = Rs.334 cr / 50,745 KL = Rs.65.8/l for ethanol alone (BSE 13-Nov-2026); DDGS by-product adds the rest. Prices set by OMCs (AR FY26 p.12). [E]', NUM2)
    scen('egrain', 'Grain cost per litre', 'Rs./litre', [55, 57, 57, 57.5], [53.5, 54, 55, 56], [53, 53.5, 54, 55], [53.5, 54, 55, 56],
         '[A] Rs.53.4/l FY26 (grain Rs.223.9 cr / 41,923 KL, AR FY26 p.73). Maize/broken rice; monsoon and FCI policy risk (CARE Jul-2025 p.2). [E]', NUM2)
    single('econv', 'Ethanol conversion cost (power, chemicals, staff)', 'Rs./litre', [16.8, 17.3, 17.8, 18.4], '[A] Rs.16.3/l FY26 (realisation - grain - EBITDA). [E] +3% a year.', NUM2)
    calc('eebl', 'Ethanol EBITDA per litre', 'Rs./litre', lambda j, c: f'={c}{X["ereal"]}-{c}{X["egrain"]}-{c}{X["econv"]}', NUM2, b=True, note='[A] Rs.9.0/l FY26; ~Rs.11 implied H1FY27.')
    calc('erev', 'Ethanol revenue', 'Rs cr', lambda j, c: f'={c}{X["evol"]}*{c}{X["ereal"]}/1E4', NUM, b=True)
    calc('egrc', 'Ethanol grain cost', 'Rs cr', lambda j, c: f'={c}{X["evol"]}*{c}{X["egrain"]}/1E4', NUM)
    calc('eeb', 'Ethanol EBITDA', 'Rs cr', lambda j, c: f'={c}{X["evol"]}*{c}{X["eebl"]}/1E4', NUM, b=True)
    single('alloc', 'memo: OMC allocation, ethanol supply year (Nov-Oct)', 'KL', [50745, None, None, None], '[A] ESY 2026-27, BSE 13-Nov-2026. Later years not allocated yet.', INT)

    section('D. Totals and checks against guidance / floor')
    calc('rev', 'Revenue from operations', 'Rs cr', lambda j, c: f'={c}{X["frev"]}+{c}{X["crev"]}+{c}{X["erev"]}', NUM, b=True)
    calc('eb', 'EBITDA (sum of segments)', 'Rs cr', lambda j, c: f'={c}{X["feb"]}+{c}{X["ceb"]}+{c}{X["eeb"]}', NUM, b=True)
    calc('ebm', '  EBITDA margin', '%', lambda j, c: f'={c}{X["eb"]}/{c}{X["rev"]}', PCT)
    single('omat', 'Other materials (VAM, DMF, chemicals, stock in trade) % of revenue', '%', [0.072] * 4, '[A] 7.2% FY26 (AR FY26 p.73: VAM 22.1, DMF 3.3, others 47.6, traded 0.2 cr).', PCT)
    single('sh_emp', 'Split of conversion costs: employees', '%', [0.184] * 4, '[A] FY26 employees 35.0 / (35.0 + power 82.9 + other 71.9) cr.', PCT)
    single('sh_pf', 'Split of conversion costs: power and fuel', '%', [0.437] * 4, '[A] FY26.', PCT)
    # guidance (bull) and floor memo rows filled by the runner (pasted values)
    gr = nxt(); X['g_rev'] = gr; lab(dv, gr, 'Bull revenue (stated capacities at target utilisation; pasted by runner)'); put(dv, f'B{gr}', 'Rs cr')
    ge = nxt(); X['g_eb'] = ge; lab(dv, ge, 'Bull EBITDA (pasted)'); put(dv, f'B{ge}', 'Rs cr')
    flr = nxt(); X['f_rev'] = flr; lab(dv, flr, 'Floor revenue (pasted)'); put(dv, f'B{flr}', 'Rs cr')
    fle = nxt(); X['f_eb'] = fle; lab(dv, fle, 'Floor EBITDA (pasted)'); put(dv, f'B{fle}', 'Rs cr')
    calc('chk_g', 'CHECK: live revenue vs bull (base must be < 0)', '%', lambda j, c: f'=IF(ISNUMBER({c}{gr}),{c}{X["rev"]}/{c}{gr}-1,"")', PCT)
    calc('chk_ge', 'CHECK: live EBITDA margin minus bull margin (base must be < 0)', '%', lambda j, c: f'=IF(ISNUMBER({c}{gr}),{c}{X["ebm"]}-{c}{ge}/{c}{gr},"")', PCT)
    calc('pos', 'Live EBITDA position between floor (0%) and bull (100%)', '%', lambda j, c: f'=IF(ISNUMBER({c}{ge}),({c}{X["eb"]}-{c}{fle})/({c}{ge}-{c}{fle}),"")', PCT,
         note='Rule of thumb: base 40-75% of the way from floor to bull. Management gives no numbers (no calls or presentations), so bull = stated capacity plans at target utilisation.')
    for k in ('chk_g', 'chk_ge'):
        put(dv, f'A{X[k]}', dv[f'A{X[k]}'].value, RED)

    section('E. Below EBITDA, balance sheet and cash')
    single('dep', 'Depreciation % of opening net fixed assets', '%', [0.051] * 4, '[A] Rs.12.49 cr FY26 on Rs.250.25 cr opening = 5.0%; H1FY27 Rs.6.40 cr (Res Q2FY27 p.2).', PCT)
    scen('capex', 'Capex', 'Rs cr', [12, 12, 13, 14], [16, 13, 14, 15], [16, 40, 30, 15], [16, 13, 14, 15],
         '[A] Rs.12.3 cr FY26 (segment capex, AR FY26 p.81); CWIP Rs.17.5 cr at Sep-26 (Res Q2FY27 p.4). [E] maintenance ~Rs.13-15 cr. Bull adds ~Rs.66 cr for 150/180 to 240 KLPD over FY28-29 (Rs.1.1 cr per KLPD vs Rs.182.6 cr for the 150 KLPD plant incl. 4 MW cogen, CARE Aug-2023 p.3).', NUM)
    single('repay', 'Term-loan repayment', 'Rs cr', [10.53, 12.47, 13.85, 16.04], '[A] Repayment schedule, AR FY26 p.69-70 (current maturities Rs.10.53 cr; then 12.47, 13.85, 16.04).', NUM2)
    single('intr', 'Interest rate on opening borrowings', '%', [0.105] * 4, '[A] 10.25-10.50% (AR FY26 p.69).', PCT)
    single('bchg', 'Bank and finance charges (LC, BG)', 'Rs cr', [2.2] * 4, '[A] Rs.2.19 cr FY26 (AR FY26 p.75).', NUM2)
    single('oiy', 'Other income: yield on opening liquid funds', '%', [0.065] * 4, '[A] Rs.8.67 cr FY26 on Rs.116.8 cr opening = 7.4% (incl. fair-value gains, claims).', PCT)
    single('tax', 'Tax rate', '%', [0.255] * 4, '[A] 25.9% FY26, 25.8% FY25, 25.0% H1FY27.', PCT)
    single('payout', 'Dividend payout', '%', [0, 0, 0, 0], '[A] No dividend in 12 years. [E] none assumed.', PCT)
    single('idays', 'Inventory days (on materials cost)', 'days', [70, 65, 65, 65], '[A] 53 FY26, 103 FY25, 97 FY24, 112 FY23 (Ratios); Sep-26 inventory Rs.195 cr (~2x Mar-26). [E]', INT)
    single('rdays', 'Receivable days (on revenue)', 'days', [32, 30, 30, 30], '[A] 28 FY26, 29 FY25, 35 FY24; Rs.105 cr at Sep-26. [E]', INT)
    single('pdays', 'Payable days (on materials cost)', 'days', [40, 40, 40, 40], '[A] 29 FY26 (LC acceptances low at year-end, CARE Jun-2026 p.2), 69 FY25, 85 FY24. [E]', INT)
    single('ocap', 'Other current assets % of revenue', '%', [0.036] * 4, '[A] 3.6% FY26.', PCT)
    single('sh', 'Shares outstanding', 'crore', [D.SHARES] * 4, '[A] AR FY26 p.67.', '0.0000')
    widths(dv, {'A': 66, 'B': 9, **{c: 10 for c in DV}, 'G': 2, 'H': 150})
    dv.freeze_panes = 'C6'

    # ---------------- P&L / BS / CF forecast formulas ----------------
    for j, c in enumerate(FC):
        d = DV[j]; p = prev(c); dl = lambda k: f'Drivers!{d}{X[k]}'
        fx(pl, f'{c}{R["revg"]}', f'={dl("rev")}', c=GREEN); put(pl, f'{c}{R["excd"]}', 0, BLUE, fmt=NUM2)
        fx(pl, f'{c}{R["rm"]}', f'={dl("facnc")}+{dl("cpolyc")}+{dl("egrc")}+{c}{R["rev"]}*{dl("omat")}')
        put(pl, f'{c}{R["pur"]}', 0, BLUE, fmt=NUM2); put(pl, f'{c}{R["inv"]}', 0, BLUE, fmt=NUM2)
        conv = f'({c}{R["rev"]}-{c}{R["mat"]}-{dl("eb")})'
        fx(pl, f'{c}{R["emp"]}', f'={conv}*{dl("sh_emp")}'); fx(pl, f'{c}{R["pf"]}', f'={conv}*{dl("sh_pf")}')
        fx(pl, f'{c}{R["othx"]}', f'={conv}*(1-{dl("sh_emp")}-{dl("sh_pf")})'); fx(pl, f'{c}{R["othrep"]}', f'={c}{R["pf"]}+{c}{R["othx"]}')
        fx(pl, f'{c}{R["dep"]}', f'=BS!{p}{B["nfa"]}*{dl("dep")}')
        fx(pl, f'{c}{R["oi"]}', f'=BS!{p}{B["liq"]}*{dl("oiy")}')
        fx(pl, f'{c}{R["fin"]}', f'=BS!{p}{B["borr"]}*{dl("intr")}+{dl("bchg")}')
        put(pl, f'{c}{R["exc"]}', 0, BLUE, fmt=NUM2)
        fx(pl, f'{c}{R["tax"]}', f'={c}{R["pbt"]}*{dl("tax")}')
        fx(pl, f'{c}{R["sh"]}', f'={dl("sh")}', '0.0000', GREEN); fx(pl, f'{c}{R["div"]}', f'={c}{R["pat"]}*{dl("payout")}')
        # BS
        fx(bs, f'{c}{B["nfa"]}', f"={p}{B['nfa']}+{dl('capex')}-'P&L'!{c}{R['dep']}")
        fx(bs, f'{c}{B["onca"]}', f'={p}{B["onca"]}')
        fx(bs, f'{c}{B["invy"]}', f"='P&L'!{c}{R['mat']}*{dl('idays')}/365")
        fx(bs, f'{c}{B["recv"]}', f"='P&L'!{c}{R['rev']}*{dl('rdays')}/365")
        fx(bs, f'{c}{B["oca"]}', f"='P&L'!{c}{R['rev']}*{dl('ocap')}")
        fx(bs, f'{c}{B["scap"]}', f'={p}{B["scap"]}')
        fx(bs, f'{c}{B["oeq"]}', f"={p}{B['oeq']}+'P&L'!{c}{R['pat']}-'P&L'!{c}{R['div']}")
        fx(bs, f'{c}{B["borr"]}', f'=MAX(0,{p}{B["borr"]}-{dl("repay")})')
        fx(bs, f'{c}{B["tp"]}', f"='P&L'!{c}{R['mat']}*{dl('pdays')}/365")
        fx(bs, f'{c}{B["ol"]}', f'={p}{B["ol"]}')
        fx(bs, f'{c}{B["liq"]}', f'={c}{B["tel"]}-{c}{B["nfa"]}-{c}{B["onca"]}-{c}{B["invy"]}-{c}{B["recv"]}-{c}{B["oca"]}')
        # CF
        fx(cf, f'{c}{C["pat"]}', f"='P&L'!{c}{R['pat']}", c=GREEN); fx(cf, f'{c}{C["dep"]}', f"='P&L'!{c}{R['dep']}", c=GREEN)
        fx(cf, f'{c}{C["wc"]}', f'=-(BS!{c}{B["invy"]}-BS!{p}{B["invy"]})-(BS!{c}{B["recv"]}-BS!{p}{B["recv"]})-(BS!{c}{B["oca"]}-BS!{p}{B["oca"]})+(BS!{c}{B["tp"]}-BS!{p}{B["tp"]})+(BS!{c}{B["ol"]}-BS!{p}{B["ol"]})-(BS!{c}{B["onca"]}-BS!{p}{B["onca"]})')
        fx(cf, f'{c}{C["cfo"]}', f'={c}{C["pat"]}+{c}{C["dep"]}+{c}{C["wc"]}', b=True)
        fx(cf, f'{c}{C["capex"]}', f'=-{dl("capex")}'); put(cf, f'{c}{C["int"]}', 0, BLUE, fmt=NUM2)
        fx(cf, f'{c}{C["borr"]}', f'=BS!{c}{B["borr"]}-BS!{p}{B["borr"]}'); fx(cf, f'{c}{C["div"]}', f"=-'P&L'!{c}{R['div']}")
        put(cf, f'{c}{C["othi"]}', 0, BLUE, fmt=NUM2); put(cf, f'{c}{C["othf"]}', 0, BLUE, fmt=NUM2)
        fx(cf, f'{c}{C["net"]}', f'={c}{C["cfo"]}+{c}{C["capex"]}+{c}{C["int"]}+{c}{C["borr"]}+{c}{C["div"]}+{c}{C["othi"]}+{c}{C["othf"]}')
        fx(cf, f'{c}{C["open"]}', f'=BS!{p}{B["liq"]}'); fx(cf, f'{c}{C["close"]}', f'={c}{C["open"]}+{c}{C["net"]}')
        fx(cf, f'{c}{C["chk"]}', f'=ROUND({c}{C["close"]}-BS!{c}{B["liq"]},3)', c=RED)
        # P&L check rows not applicable in forecast
        for k in ('chk_pbt', 'chk_pat', 'chk_eps'): put(pl, f'{c}{R[k]}', None)
        # Segments forecast
        fx(sg, f'{c}{S["rf"]}', f'={dl("frev")}', c=GREEN); fx(sg, f'{c}{S["rc"]}', f'={dl("crev")}', c=GREEN); fx(sg, f'{c}{S["re"]}', f'={dl("erev")}', c=GREEN)
        fx(sg, f'{c}{S["ef"]}', f'={dl("feb")}', c=GREEN); fx(sg, f'{c}{S["ec"]}', f'={dl("ceb")}', c=GREEN); fx(sg, f'{c}{S["ee"]}', f'={dl("eeb")}', c=GREEN)
        fx(sg, f'{c}{S["fcap"]}', f'={dl("fcap")}', INT, GREEN); fx(sg, f'{c}{S["fsale"]}', f'={dl("fvol")}', INT, GREEN)
        fx(sg, f'{c}{S["fprod"]}', f'={c}{S["fsale"]}', INT); fx(sg, f'{c}{S["facn"]}', f'={dl("facnc")}', c=GREEN)
        fx(sg, f'{c}{S["facnkg"]}', f'={dl("acnkg")}', NUM, GREEN); fx(sg, f'{c}{S["facnpx"]}', f'={dl("acn")}', NUM, GREEN)
        fx(sg, f'{c}{S["febitdakg"]}', f'={dl("febkg")}', NUM, GREEN); fx(sg, f'{c}{S["fconv"]}', f'={dl("fconv")}', NUM, GREEN)
        fx(sg, f'{c}{S["ccap"]}', f'={dl("ccap")}', INT, GREEN); fx(sg, f'{c}{S["csale"]}', f'={dl("cvol")}', INT, GREEN)
        fx(sg, f'{c}{S["cutil"]}', f'={c}{S["csale"]}/{c}{S["ccap"]}', PCT); fx(sg, f'{c}{S["creal"]}', f'={c}{S["rc"]}*1E4/{c}{S["csale"]}', NUM)
        fx(sg, f'{c}{S["cpoly"]}', f'={dl("cpoly")}', NUM, GREEN); fx(sg, f'{c}{S["cspr"]}', f'={dl("cspr")}', NUM, GREEN)
        fx(sg, f'{c}{S["cebitdakg"]}', f'={dl("cebkg")}', NUM, GREEN)
        fx(sg, f'{c}{S["ecap"]}', f'={dl("eklpd")}*{dl("edays")}', INT); fx(sg, f'{c}{S["esale"]}', f'={dl("evol")}', INT, GREEN)
        fx(sg, f'{c}{S["eutil"]}', f'={c}{S["esale"]}/{c}{S["ecap"]}', PCT); fx(sg, f'{c}{S["ereal"]}', f'={dl("ereal")}', NUM2, GREEN)
        fx(sg, f'{c}{S["egrain"]}', f'={dl("egrain")}', NUM2, GREEN); fx(sg, f'{c}{S["espr"]}', f'={c}{S["ereal"]}-{c}{S["egrain"]}', NUM2)
        fx(sg, f'{c}{S["eebitdal"]}', f'={dl("eebl")}', NUM2, GREEN)
    # EBITDA tie check in forecast
    ck = nxt(); ck = nxt(); X['chk_eb'] = ck; lab(dv, ck, 'CHECK: P&L EBITDA vs sum of segment EBITDA (should be 0)', c=RED)
    for j, c in enumerate(DV): fx(dv, f'{c}{ck}', f"=ROUND('P&L'!{FC[j]}{R['ebitda']}-{c}{X['eb']},3)", c=RED)

    # =========================================================== TAM
    tm = wb.create_sheet('TAM', 1)
    put(tm, 'A1', 'Markets and share (industry numbers from the annual report MD&A and CARE; capacities of peers from Screener key insights - to be checked)', b=True)
    hdr(tm, 3, ['Market measure', 'Growth', 'PAL today', 'PAL share', 'Our base growth FY26-30', 'Source'], start=2); put(tm, 'A3', 'Segment', b=True)
    rows_t = [('Acrylic fibre - global demand', 'growth 3.5-4.0% CAGR to 2035', 0.0375, f"=Segments!K{S['fsale']}", None, f"=(Segments!O{S['fsale']}/Segments!K{S['fsale']})^(1/4)-1", 'AR FY26 p.10 (MD&A)'),
              ('Acrylic fibre - Indian capacity (PAL 42,000 + Vardhman 21,000 + Indian Acrylics 45,000 MT)', 108000, None, f"=Segments!K{S['fcap']}", '=D5/B5', None, 'CARE Jun-2026 p.2 (three domestic makers); Vardhman and Indian Acrylics capacities from Screener key insights (to be checked)'),
              ('CPP film - global market USD 8,742 mn by 2033', 'growth 5% CAGR', 0.05, f"=Segments!K{S['csale']}", None, f"=(Segments!O{S['csale']}/Segments!K{S['csale']})^(1/4)-1", 'AR FY26 p.10; Indian CPP industry "growing 7-8% a year" (AR FY19 p.8)'),
              ('Ethanol - India blending demand ~1,100 crore litres (capacity ~2,000 crore litres)', 11000000, 0.0, f"=Segments!K{S['esale']}", '=D7/B7', f"=(Segments!O{S['esale']}/Segments!K{S['esale']})^(1/4)-1", 'AR FY26 p.12 (KL); demand flat after E20 [E]; global ethanol 6.8% CAGR 2023-32 (AR FY26 p.10)')]
    for i, (t, a, g_, d_, e_, f_, s_) in enumerate(rows_t):
        r_ = 4 + i; lab(tm, r_, t)
        if isinstance(a, str): put(tm, f'B{r_}', a)
        else: inp(tm, f'B{r_}', a, INT)
        if g_ is not None: inp(tm, f'C{r_}', g_, PCT)
        fx(tm, f'D{r_}', d_, INT, GREEN)
        if e_: fx(tm, f'E{r_}', e_, PCT)
        if f_: fx(tm, f'F{r_}', f_, PCT)
        put(tm, f'G{r_}', s_, i=True)
    put(tm, 'A10', 'Read: fibre is a slow-growth commodity (market ~4%), PAL already runs at ~90%; growth must come from price/spread, CPP fill-up and ethanol. Ethanol is an over-built industry: allocation, not demand, sets volume.', i=True)
    put(tm, 'A12', 'Industry growth table for the note (segment, market growth, source, our base, management guidance)', b=True)
    hdr(tm, 13, ['Market growth', 'Our base volume CAGR FY26-30', 'Management guidance', 'Source'], start=2)
    for i, (t, mg, bref, gd, s_) in enumerate([('Acrylic fibre', '=C4', '=F4', 'none (capacity 42,000 MT, no expansion)', 'AR FY26 p.10'),
                                               ('CPP film', '=C6', '=F6', 'none ("expected to improve more")', 'AR FY26 p.11'),
                                               ('Ethanol', '=C7', '=F7', '180 KLPD consented; 240 KLPD envisaged (CARE)', 'AR FY26 p.11; CARE Jun-2026 p.2')]):
        r_ = 14 + i; lab(tm, r_, t); fx(tm, f'B{r_}', mg, PCT); fx(tm, f'C{r_}', bref, PCT); put(tm, f'D{r_}', gd); put(tm, f'E{r_}', s_, i=True)
    widths(tm, {'A': 80, 'B': 16, 'C': 12, 'D': 14, 'E': 14, 'F': 16, 'G': 90})

    # =========================================================== Unit economics
    ue = wb.create_sheet('Unit_Economics', 2)
    put(ue, 'A1', 'Unit economics: what one kg of fibre, one kg of film and one litre of ethanol earn (Rs.). History from Segments; FY27E-FY28E live scenario.', b=True)
    cols_u = ['FY21A', 'FY22A', 'FY23A', 'FY24A', 'FY25A', 'FY26A', 'FY27E', 'FY28E']
    srcc = ['F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']
    hdr(ue, 3, cols_u); put(ue, 'J3', 'Note', b=True)
    ur = [('Fibre: realisation per kg', 'freal', NUM), ('Fibre: ACN cost per kg', 'facnkg', NUM), ('Fibre: spread over ACN per kg', 'fspr', NUM),
          ('Fibre: conversion cost per kg', 'fconv', NUM), ('Fibre: EBITDA per kg', 'febitdakg', NUM), ('Fibre: implied ACN price per kg', 'facnpx', NUM),
          ('CPP: realisation per kg', 'creal', NUM), ('CPP: polymer cost per kg', 'cpoly', NUM), ('CPP: spread per kg', 'cspr', NUM), ('CPP: EBITDA per kg', 'cebitdakg', NUM),
          ('Ethanol: realisation per litre', 'ereal', NUM2), ('Ethanol: grain cost per litre', 'egrain', NUM2), ('Ethanol: spread per litre', 'espr', NUM2), ('Ethanol: EBITDA per litre', 'eebitdal', NUM2),
          ('Revenue per employee (Rs. crore)', 'revemp', NUM2)]
    for i, (t, k, fm) in enumerate(ur):
        r_ = 4 + i; lab(ue, r_, t)
        for j, c in enumerate(srcc):
            fx(ue, f'{CL(2 + j)}{r_}', f'=IF(ISNUMBER(Segments!{c}{S[k]}),Segments!{c}{S[k]},"")', fm, GREEN)
    put(ue, 'J5', 'Raw material is ~0.89 kg of ACN per kg of fibre; the fibre price follows ACN with a ~5-month lag (CARE).', i=True)
    put(ue, 'J8', 'Mid-cycle fibre EBITDA ~Rs.15/kg; H1FY27 ~Rs.29/kg implied (fibre PBIT Rs.57.6 cr, H1 volume not disclosed).', i=True)
    put(ue, 'J17', 'ESY27 OMC price ~Rs.65.8/l (allocation value / KL); DDGS adds ~Rs.13/l.', i=True)
    p0 = 21
    put(ue, f'A{p0}', 'Peers (latest full year FY26; Screener 28-Nov-2026; per-kg only where capacity is public - TO BE CHECKED ON BLOOMBERG)', b=True)
    hdr(ue, p0 + 1, ['Segment', 'FY26 sales Rs cr', 'OPM', 'Est. volume MT', 'Revenue/kg', 'EBITDA/kg', 'P/E (x)', 'Mcap Rs cr', 'Note'])
    peers_u = [('Pasupati Acrylon - fibre', 'Acrylic fibre', f"=Segments!K{S['rf']}", f"=Segments!K{S['ef']}/Segments!K{S['rf']}", f"=Segments!K{S['fsale']}", None),
               ('Vardhman Acrylics', 'Acrylic fibre', 319, 0.05, 21000, 'volume = 21,000 TPA at 100% (Screener key insight); to be checked'),
               ('Indian Acrylics', 'Acrylic fibre + yarn', 352, -0.003, 15869, 'FY26 sales 8,728 t fibre + 7,141 t yarn (Indian Acrylics AR FY26, BSE filing 2-Sep-2026, PDF p.13); fibre output 14,116 t on 45,000 t capacity'),
               ('Pasupati Acrylon - CPP', 'CPP film', f"=Segments!K{S['rc']}", f"=Segments!K{S['ec']}/Segments!K{S['rc']}", f"=Segments!K{S['csale']}", None),
               ('Cosmo First', 'BOPP/CPP/BOPET films', 3356, 0.09, None, 'volumes not in our documents: to be checked on Bloomberg'),
               ('Jindal Poly Films', 'Films', 697, -0.81, None, 'losses; not meaningful'), ('Polyplex Corp', 'PET films', 1497, 0.05, None, 'to be checked on Bloomberg'),
               ('Uflex', 'Films + packaging', 7778, 0.11, None, 'to be checked on Bloomberg'),
               ('Pasupati Acrylon - ethanol', 'Grain ethanol', f"=Segments!K{S['re']}", f"=Segments!K{S['ee']}/Segments!K{S['re']}", f"=Segments!K{S['esale']}", 'volume in KL; per litre'),
               ('Gulshan Polyols', 'Grain ethanol + chemicals', 2312, 0.10, None, 'to be checked on Bloomberg'), ('Globus Spirits', 'Grain ethanol + alcohol', 2708, 0.10, None, 'to be checked on Bloomberg')]
    pe_map = {p[0]: (p[3], p[2]) for p in D.PEERS}
    for i, (nm, seg_, sales, opm, vol, note) in enumerate(peers_u):
        r_ = p0 + 2 + i; lab(ue, r_, nm); put(ue, f'B{r_}', seg_)
        (fx if isinstance(sales, str) else inp)(ue, f'C{r_}', sales, NUM)
        (fx if isinstance(opm, str) else inp)(ue, f'D{r_}', opm, PCT)
        if vol is not None:
            (fx if isinstance(vol, str) else inp)(ue, f'E{r_}', vol, INT)
            fx(ue, f'F{r_}', f'=C{r_}*1E4/E{r_}', NUM); fx(ue, f'G{r_}', f'=C{r_}*D{r_}*1E4/E{r_}', NUM)
        key = nm.split(' - ')[0]
        if nm in pe_map:
            pe, mc = pe_map[nm]
            if pe is not None: inp(ue, f'H{r_}', pe, '0.0')
            else: put(ue, f'H{r_}', 'n.m.')
            inp(ue, f'I{r_}', mc, INT)
        if note: put(ue, f'J{r_}', note, i=True)
    put(ue, f'A{p0 + 14}', 'What the bull case needs per unit (FY28E, bull row on Drivers)', b=True)
    for i, (t, f_) in enumerate([('Bull fibre EBITDA per kg vs best year since FY17 (FY21 Rs.17.3)', f"=Drivers!D{X['fspr']+3}-Drivers!D{X['fconv']}"),
                                 ('Bull CPP EBITDA per kg vs best year (FY22 Rs.15.9)', f"=Drivers!D{X['cspr']+3}-Drivers!D{X['cconv']}"),
                                 ('Bull ethanol EBITDA per litre vs FY26 Rs.9.0', f"=Drivers!D{X['ereal']+3}-Drivers!D{X['egrain']+3}-Drivers!D{X['econv']}")]):
        r_ = p0 + 15 + i; lab(ue, r_, t); fx(ue, f'B{r_}', f_, NUM)
    put(ue, f'C{p0 + 15}', 'Bull asks fibre to earn ~1.7x its best full year for two years running - possible only if today\'s H1FY27 conditions persist.', i=True)
    widths(ue, {'A': 46, **{CL(2 + i): 11 for i in range(8)}, 'J': 90})

    # =========================================================== Valuations
    va = wb.create_sheet('Valuations', 3)
    put(va, 'A1', 'What the price is paying for (P/E on FY28E EPS; same multiple in every scenario)', b=True)
    V = {}
    def vrow(k, r_, t, f_, fm=NUM2, c=BLACK, b=False, isin=False, key=False):
        V[k] = r_; lab(va, r_, t, b=b)
        if isin: inp(va, f'C{r_}', f_, fm, key)
        else: fx(va, f'C{r_}', f_, fm, c, b)
    vrow('cmp', 3, f'CMP (Rs., close {D.CMP_DATE}; replace with Bloomberg)', D.CMP, NUM2, isin=True, key=True)
    vrow('sh', 4, 'Shares (crore)', f"='P&L'!K{R['sh']}", '0.0000', GREEN)
    vrow('mcap', 5, 'Market cap (Rs. crore)', '=C3*C4', NUM)
    vrow('pe', 6, 'P/E multiple (x) - same for bear, base, bull', 7.5, '0.0', isin=True, key=True)
    vrow('eps28', 7, 'FY28E EPS, live scenario (Rs.)', f"='P&L'!M{R['eps']}", '0.00', GREEN)
    vrow('tp', 8, 'Target price (Rs.)', '=C6*C7', NUM, b=True)
    vrow('up', 9, 'Upside', '=C8/C3-1', PCT, b=True)
    vrow('rating', 10, 'Rating on the base target (BUY > +15%, HOLD -5% to +15%, SELL < -5%)', '=IF(C9>0.15,"BUY",IF(C9>=-0.05,"HOLD","SELL"))', None, b=True)
    vrow('dist', 11, 'Distance to the nearest rating line (points)', '=MIN(ABS(C9-0.15),ABS(C9+0.05))*100', '0.0')
    vrow('bord', 12, 'Borderline? (within 3 points)', '=IF(C11<3,"borderline","no")', None)
    put(va, 'E6', 'Multiple: Vardhman Acrylics 7.1x and Gulshan Polyols 5.8x (closest pure peers), Cosmo First 15.5x (films); PAL own median 7.6x on FY17-FY26 (Ratios). Peer P/Es from Screener 28-Nov-2026: to be checked on Bloomberg.', i=True)
    # EV/EBITDA cross-check
    vrow('ndebt27', 14, 'Net debt FY27E (year before valuation year; negative = net cash)', f'=BS!L{B["netdebt"]}', NUM, GREEN)
    vrow('ebitda28', 15, 'FY28E EBITDA (live)', f"='P&L'!M{R['ebitda']}", NUM, GREEN)
    vrow('ev_now', 16, 'EV today = market cap + FY27E net debt', '=C5+C14', NUM)
    vrow('evm_now', 17, 'EV / FY28E EBITDA at CMP (x)', '=C16/C15', '0.0')
    vrow('evm', 18, 'EV/EBITDA multiple for cross-check (x)', 4.5, '0.0', isin=True)
    vrow('ev_tp', 19, 'EV/EBITDA cross-check target (Rs.)', '=(C18*C15-C14)/C4', NUM, b=True)
    put(va, 'E18', '[E] 4.5x: implied by 7.5x P/E for a business with ~25% tax and low leverage; Vardhman Acrylics/Gulshan to be checked on Bloomberg.', i=True)
    vrow('rev_pat', 21, 'Reverse check: FY28E PAT the price implies at the same P/E (Rs. crore)', '=C5/C6', NUM)
    vrow('base_pat', 22, 'FY28E PAT, live scenario', f"='P&L'!M{R['pat']}", NUM, GREEN)
    vrow('rev_gap', 23, 'Price-implied PAT vs live PAT', '=C21/C22-1', PCT)
    vrow('mid_pat', 24, 'memo: FY26A PAT (Rs.69.9 cr) vs TTM Sep-26 PAT', f'=Quarterly!P{QR["pat"]}', NUM, GREEN)
    # Scenario table (pasted)
    t0 = 26; lab(va, t0, 'Scenario table (values pasted by the runner after switching Drivers!C3; FY28E unless stated)', b=True)
    hdr(va, t0 + 1, ['Floor (memo)', 'Bear', 'Base', 'Bull'], start=3)
    tl = ['FY28E revenue', 'FY28E EBITDA', 'FY28E EBITDA margin', 'FY28E PAT', 'FY28E EPS (Rs.)', 'Target at the same P/E (Rs.)', 'Upside vs CMP',
          'FY27E revenue', 'FY27E PAT', 'FY30E revenue', 'FY30E PAT', 'Max balance-sheet check (should be 0)']
    for i, t in enumerate(tl): lab(va, t0 + 2 + i, t)
    V['tab'] = t0 + 2
    ch = t0 + 2 + len(tl) + 1
    vrow('chance', ch, "Chance of management's plan (bull) already in the price = (CMP - base target) / (bull target - base target)", f'=(C3-E{t0+7})/(F{t0+7}-E{t0+7})', PCT, b=True)
    put(va, f'E{ch}', 'Negative = the price sits below our base target, i.e. none of the bull case is paid for; above 100% = more than the bull case is in the price.', i=True)
    # Multiple sensitivity
    s0 = ch + 2; lab(va, s0, 'Target price at other P/E multiples (FY28E EPS from the pasted table)', b=True)
    hdr(va, s0 + 1, ['Floor', 'Bear', 'Base', 'Bull'], start=3)
    for i, m in enumerate([5, 6, 7, 7.5, 8, 9, 10]):
        r_ = s0 + 2 + i; inp(va, f'B{r_}', m, '0.0')
        for j, c in enumerate('CDEF'): fx(va, f'{c}{r_}', f'=IF(ISNUMBER({c}${t0+6}),B{r_}*{c}${t0+6},"")', NUM)
    put(va, f'A{s0+2}', 'P/E (x)')
    # mid-cycle valuation memo
    m0 = s0 + 11; lab(va, m0, 'Mid-cycle check', b=True)
    for i, (t, f_, fm) in enumerate([('10-year average company EBITDA margin (FY17-FY26)', f"=Segments!K{S['mc_ebm']}", PCT),
                                     ('H1FY27 EBITDA margin', f'=Quarterly!O{QR["ebm"]}', PCT),
                                     ('FY28E EBITDA margin, live scenario', f"='P&L'!M{R['ebm']}", PCT),
                                     ('FY28E PAT at 10-year average margin on live FY28E revenue (rough: same D&A, interest, OI, tax)', f"=('P&L'!M{R['rev']}*C{m0+1}-'P&L'!M{R['dep']}+'P&L'!M{R['oi']}-'P&L'!M{R['fin']})*(1-Drivers!D{X['tax']})", NUM),
                                     ('Mid-cycle value per share at the same P/E (Rs.)', f'=C{m0+4}/C4*C6', NUM)]):
        r_ = m0 + 1 + i; lab(va, r_, t); fx(va, f'C{r_}', f_, fm, GREEN if i < 3 else BLACK)
    V['mid'] = m0
    # peers
    pp = m0 + 8; lab(va, pp, 'Peer multiples (Screener 28-Nov-2026; to be checked on Bloomberg)', b=True)
    hdr(va, pp + 1, ['Segment', 'Mcap Rs cr', 'P/E (x)', 'FY26 OPM', 'Note'], start=2)
    for i, (nm, seg_, mc, pe, sales, opm, note) in enumerate(D.PEERS):
        r_ = pp + 2 + i; lab(va, r_, nm); put(va, f'B{r_}', seg_); inp(va, f'C{r_}', mc, INT)
        if pe is None: put(va, f'D{r_}', 'n.m.')
        else: inp(va, f'D{r_}', pe, '0.0')
        inp(va, f'E{r_}', opm, PCT); put(va, f'F{r_}', note, i=True)
    widths(va, {'A': 78, 'B': 22, 'C': 12, 'D': 12, 'E': 12, 'F': 12})
    return wb, {'R': R, 'B': B, 'C': C, 'S': S, 'X': X, 'V': V, 'QR': QR}


if __name__ == '__main__':
    import json
    os.makedirs(OUT, exist_ok=True)
    if MODE in ('v1', 'both'):
        wb, _ = build('v1'); wb.save(os.path.join(OUT, 'PASUPTAC_Model_v1.xlsx')); print('v1 saved')
    if MODE in ('v2', 'both'):
        wb, maps = build('v2'); wb.save(os.path.join(OUT, 'PASUPTAC_Model_v2.xlsx'))
        json.dump(maps, open(os.path.join(OUT, 'scripts', 'model_map.json') if os.path.isdir(os.path.join(OUT, 'scripts')) else os.path.join(OUT, 'model_map.json'), 'w'), indent=0)
        print('v2 saved')
