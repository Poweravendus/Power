"""Build Pasupati_Acrylon_Note_v1.docx from the recalculated PASUPTAC_Model_v2.xlsx (base selected) and
scripts/run_results_28Nov2026.json. Usage: python3 pal_note_v1.py"""
import json, os, openpyxl
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__)); CO = os.path.dirname(HERE)
MAP = json.load(open(os.path.join(HERE, 'model_map.json'))); R, B, C, S, X, V, QR = (MAP[k] for k in ['R', 'B', 'C', 'S', 'X', 'V', 'QR'])
RUN = json.load(open(os.path.join(HERE, 'run_results_28Nov2026.json')))
BA, BE, BU, FL = RUN['base'], RUN['bear'], RUN['bull'], RUN['floor']
M = openpyxl.load_workbook(os.path.join(CO, 'PASUPTAC_Model_v2.xlsx'), data_only=True)
pl, bs, cf, sg, q, va, dv, ra = (M[n] for n in ['P&L', 'BS', 'CF', 'Segments', 'Quarterly', 'Valuations', 'Drivers', 'Ratios'])
H = list('BCDEFGHIJK'); FCc = list('LMNO'); YRS = [f'FY{y}' for y in range(17, 27)]
n0 = lambda x: f'{x:,.0f}'; n1 = lambda x: f'{x:,.1f}'; n2 = lambda x: f'{x:,.2f}'; pc = lambda x: f'{x*100:.1f}%'; pc0 = lambda x: f'{x*100:.0f}%'
g = lambda ws, r, c: ws[f'{c}{r}'].value
CMP, MCAP, PE = g(va, V['cmp'], 'C'), g(va, V['mcap'], 'C'), g(va, V['pe'], 'C')
TP, UP, RATING, DIST = g(va, V['tp'], 'C'), g(va, V['up'], 'C'), g(va, V['rating'], 'C'), g(va, V['dist'], 'C')
CH = g(va, V['chance'], 'C')
t0 = V['tab']
tab = {nm: [g(va, t0 + i, col) for i in range(12)] for nm, col in zip(['floor', 'bear', 'base', 'bull'], 'CDEF')}

doc = Document()
st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10); st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
sec = doc.sections[0]; sec.page_width, sec.page_height = Inches(8.5), Inches(11)
for m in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'): setattr(sec, m, Inches(0.65))
hp = sec.header.paragraphs[0]; hp.style = doc.styles['Normal']
hp.text = f'Pasupati Acrylon Ltd  //  November 2026  //  Mcap Rs.{n0(MCAP)}cr\tPASUPTAC | NSE/BSE'
hp.paragraph_format.tab_stops.add_tab_stop(Inches(7.0), WD_TAB_ALIGNMENT.RIGHT)
for r in hp.runs: r.font.size = Pt(8); r.font.name = 'Arial'
fp = sec.footer.paragraphs[0]; fp.style = doc.styles['Normal']; fp.paragraph_format.tab_stops.add_tab_stop(Inches(7.0), WD_TAB_ALIGNMENT.RIGHT)
r = fp.add_run('Strictly Confidential - for internal circulation only\tPage '); r.font.size = Pt(8); r.font.name = 'Arial'
fld = OxmlElement('w:fldSimple'); fld.set(qn('w:instr'), 'PAGE'); rr = OxmlElement('w:r'); t = OxmlElement('w:t'); t.text = '1'; rr.append(t); fld.append(rr); fp._p.append(fld)


def para(text='', size=10, bold=False, italic=False, space_after=4, lead=None):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(space_after); p.paragraph_format.space_before = Pt(0)
    if lead:
        r = p.add_run(lead + ' '); r.bold = True; r.font.size = Pt(size); r.font.name = 'Arial'
    r = p.add_run(text); r.bold = bold; r.italic = italic; r.font.size = Pt(size); r.font.name = 'Arial'
    return p


def head(text): return para(text, 12, True, space_after=3)
def srcline(text): return para(text, 7.5, space_after=6)


def shade(cell, color='D9D9D9'):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), color); tcPr.append(shd)


def table(rows, widths=None):
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.text = ''; p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            run = p.add_run(str(val)); run.font.size = Pt(8.5); run.font.name = 'Arial'
            if i == 0: run.bold = True; shade(c)
            if j > 0 and i > 0: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            if i < len(rows) - 1: p.paragraph_format.keep_with_next = True
    if widths:
        t.autofit = False
        for j, gc in enumerate(t._tbl.tblGrid.gridCol_lst): gc.w = Inches(widths[j])
        for row in t.rows:
            for j, c in enumerate(row.cells): c.width = Inches(widths[j])
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t


# numbers used repeatedly
rev26, eb26, pat26 = g(pl, R['rev'], 'K'), g(pl, R['ebitda'], 'K'), g(pl, R['pat'], 'K')
h1 = {k: g(q, QR[k], 'O') for k in ['rev', 'ebitda', 'ebm', 'pat', 'rf', 'rc', 're', 'xf', 'xc', 'xe', 'mf', 'mc', 'me']}
h0 = {k: g(q, QR[k], 'N') for k in ['rev', 'ebitda', 'ebm', 'pat', 'rf', 'rc', 're', 'xf', 'xc', 'xe']}
ttm_pat = g(q, QR['pat'], 'P'); ttm_eps = ttm_pat / g(pl, R['sh'], 'K')
seg = lambda k, c='K': g(sg, S[k], c)
mid_ebm, mid_febit, mid_fm = seg('mc_ebm'), seg('mc_febit'), seg('mc_fm')
liq26, borr26 = g(bs, B['liq'], 'K'), g(bs, B['borr'], 'K')
eq26 = g(bs, B['teq'], 'K')
base_fc = {k: [g(pl, R[k], c) for c in FCc] for k in ['rev', 'ebitda', 'ebm', 'pat', 'eps']}

# =============================================================== title block
para('Pasupati Acrylon Ltd - a sweater-fibre maker that added a fuel-ethanol distillery, now earning at the top of its cycle', 15, True, space_after=4)
para(f'NSE: PASUPTAC  |  BSE: 500456  |  CMP: Rs.{CMP:,.2f}  |  Market cap: Rs.{n0(MCAP)} crore  |  Rating: {RATING} (borderline)  |  Target price: Rs.{n0(TP)}  |  Upside: {UP*100:+.1f}%  |  Analyst: Dheeraj Kripalani', 9, True, space_after=2)
para(f'November 2026  |  Version 1 (28-Nov-2026)  |  CMP is the {"27-Nov-2026"} close (to be replaced with Bloomberg)  |  Standalone accounts (no subsidiaries)  |  Rs. crore unless stated', 8, italic=True, space_after=8)

bv = eq26 / g(pl, R['sh'], 'K')
rows = [['Snapshot', 'Value', 'Snapshot', 'Value'],
        ['CMP (27-Nov-2026)', f'Rs.{CMP:,.2f}', '52-week range', 'Rs.40.9 - 84.3'],
        ['Market cap', f'Rs.{n0(MCAP)} cr', 'Promoter holding (pledged)', '65.87% (nil)'],
        ['TTM EPS (Oct-25 to Sep-26)', f'Rs.{n2(ttm_eps)}', 'P/E on TTM', f'{CMP / ttm_eps:.1f}x'],
        ['FY26 EPS', f"Rs.{n2(g(pl, R['eps'], 'K'))}", 'P/E on FY26', f"{CMP / g(pl, R['eps'], 'K'):.1f}x"],
        ['Net cash (Mar-26)', f'Rs.{n0(liq26 - borr26)} cr', 'Book value per share (Mar-26)', f'Rs.{bv:.1f} ({CMP / bv:.1f}x)'],
        ['Dividend', 'none for 12+ years', 'Credit rating', 'CARE A- / A2+ (Jun-2026)']]
table(rows, [1.9, 1.5, 2.1, 1.5])
# =============================================================== 1
head('1. The business in one minute')
para('Think of a small refinery that turns one imported chemical into wool-like fibre. Pasupati Acrylon (PAL) buys acrylonitrile (ACN, a liquid made from crude oil and ammonia) from Asia, spins it into acrylic staple fibre, tow and tops at Thakurdwara near Moradabad in Uttar Pradesh, and sells it to spinning mills that make yarn for sweaters, shawls, blankets and socks. Acrylic is the cheap cousin of wool. The plant can make 42,000 tonnes a year; it sold 37,878 tonnes in FY26. It is one of only three Indian makers, with Vardhman Acrylics and Indian Acrylics.')
para('Two newer businesses sit next door. Since September 2017 a cast polypropylene (CPP) film line makes clear and metallised packaging film for snacks, confectionery and medicines (10,000 tonnes a year; 7,621 tonnes sold in FY26). Note this is CPP only; the company makes no BOPP film. Since 25 March 2025 a grain distillery turns maize and broken rice into fuel ethanol for the oil companies (150 kilolitres a day built, consents for 180). In FY26 the mix of sales was fibre 58%, ethanol 32%, film 10%.')
para('How it gets paid. Fibre prices are reset every month off ACN cost, import prices and the rupee, so the company earns a spread over ACN, not a fixed margin. Mills pay in 15-30 days; the ACN is bought on letters of credit 4-5 months before the fibre is sold, which means profits swing when ACN prices move. Ethanol is sold to Indian Oil, BPCL and HPCL at prices fixed by the government, against yearly allocations; the company cannot raise the price when grain gets dear.')
srcline('Sources: AR FY26 p.10-12 (MD&A), p.81 (segments); CARE Jun-2026 p.1-3; BSE disclosures 24-Mar-2025 and 13-Nov-2026.')

# =============================================================== 2
head('2. How one unit earns money')
fy = ['I', 'J', 'K']
rows = [['Per kg of fibre (Rs.)', 'FY24', 'FY25', 'FY26', 'H1FY27 (est.)', '10-yr avg'],
        ['Selling price', *[n1(seg('freal', c)) for c in fy], '~160', n1(sum(seg('freal', c) for c in H) / 10)],
        ['ACN cost (0.89 kg per kg)', *[n1(seg('facnkg', c)) for c in fy], 'n.d.', n1(sum(seg('facnkg', c) for c in H) / 10)],
        ['Spread over ACN', *[n1(seg('fspr', c)) for c in fy], '~74', n1(seg('mc_spr'))],
        ['Other costs (chemicals, power, staff, freight)', *[n1(seg('fconv', c)) for c in fy], '~45', ''],
        ['EBITDA per kg', *[n1(seg('febitdakg', c)) for c in fy], '~29', ''],
        ['PBIT per kg', *[n1(seg('febitkg', c)) for c in fy], '~29', n1(mid_febit)]]
table(rows, [2.5, 0.8, 0.8, 0.8, 1.0, 0.9])
rows = [['Per kg of CPP film / per litre of ethanol (Rs.)', 'FY24', 'FY25', 'FY26'],
        ['Film: price / polymer cost / spread', *[f"{n1(seg('creal', c))} / {n1(seg('cpoly', c))} / {n1(seg('cspr', c))}" for c in fy]],
        ['Film: EBITDA per kg', *[n1(seg('cebitdakg', c)) for c in fy]],
        ['Ethanol: price incl. DDGS / grain cost per litre', '-', '-', f"{n1(seg('ereal'))} / {n1(seg('egrain'))}"],
        ['Ethanol: EBITDA per litre', '-', '-', n1(seg('eebitdal'))]]
table(rows, [3.3, 1.3, 1.3, 1.3])
para(f'Read it like this. On every kg of fibre the company keeps what is left of the selling price after ACN; in FY26 that spread was about Rs.62, and after about Rs.45 of other costs it earned Rs.17 of EBITDA per kg. The 10-year average profit is Rs.{n1(mid_febit)} per kg (PBIT). In H1FY27 the fibre segment earned Rs.{n1(h1["xf"])} crore, a {pc(h1["mf"])} margin against a 10-year average of {pc(mid_fm)}: roughly Rs.29 per kg, double the norm. Film earns far less per kg and lost money from FY23 to FY25. Ethanol earned about Rs.9 per litre in its first full year, roughly 11% of the selling price.')
para('Not disclosed: volumes and prices by quarter, the ACN price actually paid (we back it out at 0.889 kg of ACN per kg of fibre, which matches the two ACN prices CARE published), the split of the Rs.47.6 crore of "other" raw materials, ethanol price versus DDGS (cattle-feed by-product) revenue, and any customer names.')
srcline('Sources: segment notes and raw-material notes in AR FY24 p.78, 85-86; AR FY25 p.78, 85; AR FY26 p.73, 81; CARE Aug-2022 p.2 (ACN Rs.97.47/kg FY21, Rs.171.57/kg FY22); Res Q2FY27 p.3. H1FY27 per kg assumes ~19,650 tonnes at ~Rs.160/kg (volume not disclosed).')

# =============================================================== 3
head('3. Who buys and how much')
para(f'Fibre goes to yarn spinners; the company keeps its sales office in Ludhiana, the knitwear hub, rented from a promoter company. The top 10 customers took 41% of FY26 sales, down from 59% in FY24-FY25 because ethanol buyers are separate. Exports were 38% of fibre tonnes in FY17 (much of it to Iran, paid in rupees) but only 741 tonnes (2%) in FY26: the business has become almost entirely domestic. Orders are won on price, set monthly against imported fibre from China, Peru and Thailand. Ethanol volume depends on the oil companies\' tender: for the year from November 2026 PAL won 50,745 kilolitres worth Rs.334 crore, about 85% of a 180 KLPD plant.')
tam = M['TAM']
rows = [['Market', 'Size / growth', 'PAL today', 'PAL share', 'Source'],
        ['Acrylic fibre, global demand', '3.5-4.0% a year to 2035', f"{n0(seg('fsale'))} t sold", '-', 'AR FY26 p.10'],
        ['Acrylic fibre, Indian capacity', '~108,000 t (3 makers)', '42,000 t', pc0(42000 / 108000), 'CARE Jun-2026 p.2; Screener (to check)'],
        ['CPP film, global', 'USD 8.7 bn by 2033, 5% a year', f"{n0(seg('csale'))} t", 'tiny', 'AR FY26 p.10; AR FY19 p.8 (India 7-8%)'],
        ['Fuel ethanol, India', 'demand ~1,100 cr litres; capacity ~2,000 cr litres', f"{n0(seg('esale'))} KL", pc(seg('esale') / 11000000), 'AR FY26 p.12']]
table(rows, [1.7, 1.9, 1.0, 0.7, 2.0])
para('The ethanol line is the one to underline: by the company\'s own account India can now make almost twice the ethanol it needs for 20% blending. That is why allocations, not demand, decide how full the distillery runs, and why H1FY27 distillery sales fell to Rs.' + n0(h1['re']) + ' crore from Rs.' + n0(h0['re']) + ' crore a year earlier.')

# =============================================================== 4
head('4. Can they deliver: capacity, supply chain, capex funding and balance sheet')
rows = [['Line', 'Capacity', 'FY24', 'FY25', 'FY26', 'Room left'],
        ['Acrylic fibre (t sold / util.)', '42,000 t', *[f"{n0(seg('fsale', c))} / {pc0(seg('futil', c))}" for c in fy], 'little: ~4,000 t'],
        ['CPP film (t sold / util.)', '10,000 t', *[f"{n0(seg('csale', c))} / {pc0(seg('cutil', c))}" for c in fy], '~2,400 t'],
        ['Ethanol (KL produced)', '150-180 KLPD', '-', '790', n0(seg('eprod')), 'allocation-bound']]
table(rows, [1.9, 1.0, 1.1, 1.1, 1.1, 1.1])
para(f'People and supply. About 540 employees (FY26 average). ACN is fully imported (53% of raw materials by value came from abroad in FY26), bought on 90-180 day letters of credit; the 4-5 month gap from shipment to sale is both the main risk and, when ACN rises, the main source of windfall profits. Polymer for film is bought on long-term contracts; grain is bought locally. A fire at the plant on 13-Jun-2025 disrupted operations briefly; the loss was insured and never quantified to shareholders.')
para(f'Working capital is the swing item. Inventory fell from Rs.135 crore (Mar-25) to Rs.103 crore (Mar-26), then jumped to Rs.195 crore by Sep-26 while liquid funds fell by Rs.57 crore: most of H1FY27 profit went into stock. CFO/EBITDA has averaged about 60% over ten years.')
para(f'Capex funding. The only big project in a decade, the 150 KLPD grain distillery with a 4 MW cogeneration unit, was budgeted at Rs.182.6 crore: Rs.108 crore Indian Bank term loan and the rest from internal cash. Segment capex was Rs.77 crore in FY24 and Rs.180 crore in FY25 (including the CWIP transfer), so cost came in close to budget; it started on 24-Mar-2025, about five months after the October 2024 date CARE was given in July 2024. The loan carries 10.25-10.50% and is repaid in 28 rising quarterly instalments from March 2026 (Rs.10.5 crore in FY27, Rs.16 crore by FY30). At March 2026 borrowings were Rs.{n0(borr26)} crore against Rs.{n0(liq26)} crore of cash, bank deposits and mutual funds: net cash of Rs.{n0(liq26 - borr26)} crore on equity of Rs.{n0(eq26)} crore. CARE upgraded the bank lines to A-/A2+ in June 2026. A move to 240 KLPD is mentioned only by CARE ("envisaged"); no board approval, cost or date has been disclosed, so it is in our bull case only.')
cols5 = ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
rows = [['Balance sheet and cash (Rs. crore)', 'FY22', 'FY23', 'FY24', 'FY25', 'FY26', 'FY27E', 'FY28E', 'FY29E', 'FY30E'],
        ['Borrowings', *[n0(g(bs, B['borr'], c)) for c in cols5]], ['Cash, deposits and mutual funds', *[n0(g(bs, B['liq'], c)) for c in cols5]],
        ['Net debt (negative = net cash)', *[n0(g(bs, B['netdebt'], c)) for c in cols5]], ['Equity', *[n0(g(bs, B['teq'], c)) for c in cols5]],
        ['Inventory days (on materials)', *[n0(g(ra, 3, c)) for c in cols5]], ['CFO', *[n0(g(cf, C['cfo'], c)) for c in cols5]],
        ['Capex', *[n0(-g(cf, C['capex'], c)) for c in cols5]], ['ROE', *[pc0(g(ra, 8, c)) for c in cols5]]]
table(rows, [2.1] + [0.56] * 9)
srcline('Sources: AR FY26 p.12 (employees), p.69-70 (term loan), p.81 (segment capex, imports); CARE Aug-2023 p.3 and Jul-2024 p.2 (project cost, dates); CARE Jun-2026 p.1-3; Res Q2FY27 p.4 (Sep-26 balance sheet); BSE 14-Jun-2025 (fire).')

# =============================================================== 5
head('5. What the numbers say')
rows = [['Rs. crore', *YRS]]
rows.append(['Revenue', *[n0(g(pl, R['rev'], c)) for c in H]])
rows.append(['EBITDA', *[n0(g(pl, R['ebitda'], c)) for c in H]])
rows.append(['EBITDA margin', *[pc(g(pl, R['ebm'], c)) for c in H]])
rows.append(['PAT', *[n0(g(pl, R['pat'], c)) for c in H]])
rows.append(['CFO', *[n0(g(cf, C['cfo'], c)) for c in H]])
rows.append(['Fibre sold (000 t)', *[n1(seg('fsale', c) / 1000) for c in H]])
table(rows, [1.2] + [0.6] * 10)
qc = ['I', 'J', 'K', 'L', 'M']
rows = [['Quarter (Rs. crore)', 'Q2FY26', 'Q3FY26', 'Q4FY26', 'Q1FY27', 'Q2FY27'],
        ['Revenue', *[n0(g(q, QR['rev'], c)) for c in qc]], ['  of which fibre / film / ethanol', *[f"{n0(g(q, QR['rf'], c))}/{n0(g(q, QR['rc'], c))}/{n0(g(q, QR['re'], c))}" for c in qc]],
        ['EBITDA', *[n1(g(q, QR['ebitda'], c)) for c in qc]], ['EBITDA margin', *[pc(g(q, QR['ebm'], c)) for c in qc]],
        ['Fibre PBIT margin', *[pc(g(q, QR['mf'], c)) for c in qc]], ['Ethanol PBIT', *[n1(g(q, QR['xe'], c)) for c in qc]], ['PAT', *[n1(g(q, QR['pat'], c)) for c in qc]]]
table(rows, [2.2, 0.9, 0.9, 0.9, 0.9, 0.9])
sc = ['G', 'H', 'I', 'J', 'K']
rows = [['Segment (Rs. crore)', 'FY22', 'FY23', 'FY24', 'FY25', 'FY26', 'H1FY27'],
        ['Fibre revenue', *[n0(seg('rf', c)) for c in sc], n0(h1['rf'])], ['Fibre PBIT', *[n1(seg('xf', c)) for c in sc], n1(h1['xf'])],
        ['Fibre PBIT margin', *[pc(seg('mf', c)) for c in sc], pc(h1['mf'])],
        ['Film revenue', *[n0(seg('rc', c)) for c in sc], n0(h1['rc'])], ['Film PBIT', *[n1(seg('xc', c)) for c in sc], n1(h1['xc'])],
        ['Ethanol revenue', '-', '-', '-', n1(seg('re', 'J')), n0(seg('re')), n0(h1['re'])], ['Ethanol PBIT', '-', '-', '-', n1(seg('xe', 'J')), n1(seg('xe')), n1(h1['xe'])],
        ['Segment assets: fibre / film / ethanol', *[f"{n0(seg('af', c))}/{n0(seg('ac', c))}/{n0(seg('ae', c)) if seg('ae', c) else '-'}" for c in sc], '351/94/274']]
table(rows, [2.2, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8])
doc.add_picture(os.path.join(CO, 'exhibits', 'exhibit1_fibre_and_segments.png'), width=Inches(7.0))
srcline('Exhibit 1: fibre profit per kg against its 10-year average (H1FY27 estimated on ~19,650 t), and revenue by segment with our base case. Sources: segment notes FY18-FY26 ARs; Res Q2FY27 p.3; model.')
para(f'What changed and why. For ten years this was a single-product fibre company whose profit rose and fell with the ACN cycle: EBITDA margins between {pc(min(g(pl, R["ebm"], c) for c in H))} (FY24, when ACN collapsed to USD 900 a tonne and stock bought dear had to be sold cheap) and {pc(max(g(pl, R["ebm"], c) for c in H))} (FY17), averaging {pc(mid_ebm)}. Three things changed. First, the distillery added Rs.324 crore of sales and Rs.37 crore of EBITDA in FY26. Second, the film line finally turned profitable in FY26 after three loss years. Third, and most important for the price, fibre profit per kg doubled in H1FY27 to roughly Rs.29, so trailing-twelve-month PAT is Rs.{n0(ttm_pat)} crore (EPS Rs.{n2(ttm_eps)}) against Rs.{n0(pat26)} crore in FY26. The company gives no reason (no calls, no presentations). Possible causes are ACN bought cheaply ahead of a price rise, and a weak competitor: Indian Acrylics sold only 8,728 tonnes of fibre in FY26 (11,877 a year earlier) from a 45,000-tonne plant. It is not trade protection: the anti-dumping duty recommended by DGTR in August 2025 was never notified by the Finance Ministry, according to Indian Acrylics\' own FY26 annual report. None of these causes is permanent.')

# =============================================================== 6
head('6. The people and the money trail')
para('Promoters. The company was promoted in 1982 by Vineet Jain (now Managing Director, BBA London) and his family companies; it is not a Jindal-group company. Promoters own 65.87%: Vineet Jain 18.91%, Gurukripa Finvest 10.10%, Sulabh Plantation & Finance 9.26%, Arihant Exports 6.48%, Shubh Exim 5.05%, Sind Wave Finance 4.49%, Prabhat Capital 3.93%, Accurex Traders 1.96%, Vinod Kumar Jain HUF 0.68%, and PICUP, the Uttar Pradesh state industrial investment corporation, 5.03% (classed as a promoter). No shares are pledged. Three small promoter companies were merged into Arihant Exports in September 2025 (no change in total). The MD\'s brother Manish Jain, an executive vice president, died in November 2025.')
para('Related parties. (1) The distillery stands on 20 acres leased for 29 years 11 months from three promoter-linked companies (Vigar Enterprises, Sulabh Plantations, Pasupati Advanced Films) at Rs.5,000 per acre per month, about Rs.12 lakh a year; the same companies mortgaged the land to Indian Bank and gave a Rs.5.6 crore corporate guarantee for the term loan, and Vineet Jain gave a personal guarantee. (2) A Ludhiana office is rented from Prabhat Capital (Rs.15,400 a month). (3) Vigar Enterprises supplies organic groceries for office use (up to Rs.12 lakh a year). All are small and approved; the land lease ties a Rs.250 crore plant to promoter land and is worth watching at renewal.')
para('Pay. Vineet Jain received Rs.4.76 crore in FY26 (salary Rs.0.62 crore, allowances and retirement benefits Rs.0.59 crore, commission Rs.3.55 crore), up 90% and 159 times the median employee, who got 4.7% less. His terms allow commission up to 5% of net profit. On 26-Nov-2026 the board asked shareholders, by postal ballot closing 31-Dec-2026, to allow pay above Rs.5 crore a year until September 2027. At our base FY27E profit, 5% of profit is about Rs.6-7 crore.')
para('Capital allocation. The company went through corporate debt restructuring in 2004 and paid Rs.15 crore of "recompense" to its banks to exit it in FY18-FY19. It has not paid a dividend in at least 12 years; instead cash was parked in mutual funds and then spent on the film line (returns poor: cumulative PBIT of about Rs.11 crore over FY18-FY26 on Rs.75-100 crore of assets) and the distillery (Rs.34 crore PBIT in its first full year on Rs.251 crore of assets, about 13%). Auditors: B.K. Shroff & Co. (to FY17, again from FY23), Suresh Kumar Mittal & Co. (FY18-FY22): a normal rotation.')
para('Red flags (checked against the page images): (a) rising promoter pay with no dividend to minority shareholders; (b) a Rs.91 crore inventory build in H1FY27 that coincides with record fibre margins, with no explanation; (c) a printing error in the FY26 accounts (FY25 sales by geography add up to Rs.10 crore more than revenue, AR FY26 p.81). Quirks, not flags: fibre capacity shown as 45,000 tonnes in the FY23 report and 42,000 elsewhere; FY19 output (43,462 t) above rated capacity; no investor calls or presentations at all.')
srcline('Sources: AR FY26 p.19-20 (contracts with related parties), p.26 and p.36 (pay), p.67-68 (promoters), p.69 (security), p.79 (related-party note); postal ballot notice 26-Nov-2026 p.2-14; SHP Mar-2026; BSE 24-Sep-2025; AR FY18 p.59 and AR FY19 p.7 (CDR).')

# =============================================================== 7
doc.add_page_break()
head('7. Our estimates')
para('Floor = only what is visible now: fibre and film at FY26 volumes and their mid-cycle profit per kg (about Rs.15 and Rs.12.5), ethanol only for the quantity already allocated (nothing assumed after October 2027). Base = most likely: H2FY27 cools from H1, fibre profit per kg drifts back towards mid-cycle by FY29, film stays profitable, ethanol runs a little below its allocation at today\'s per-litre margin. Bull = what the stated plans would deliver: fibre and film at 95% of capacity with today\'s spreads held (for example if the anti-dumping duty recommended in August 2025, so far not notified, is revived), and the distillery at 180 KLPD rising to 240 KLPD from FY29. Management gives no numbers, so the bull case is built from stated capacities at target utilisation. Bear = no duty, imports rise, the fibre spread falls to the FY20/FY24 trough, film returns to losses and ethanol allocations are cut.')
rows = [['Segment', 'Market growth', 'Our base volume CAGR FY26-30', 'Management guidance', 'Source'],
        ['Acrylic fibre', '3.5-4.0%', pc(tam['C14'].value), 'none; no expansion', 'AR FY26 p.10'],
        ['CPP film', '5% (global); 7-8% India', pc(tam['C15'].value), 'none ("expected to improve")', 'AR FY26 p.10-11; AR FY19 p.8'],
        ['Ethanol', 'flat after E20; capacity surplus', pc(tam['C16'].value), '180 KLPD consented; 240 KLPD "envisaged"', 'AR FY26 p.11-12; CARE Jun-2026']]
table(rows, [1.2, 1.5, 1.3, 1.9, 1.6])
dl = lambda k, c: g(dv, X[k], c)
rows = [['FY28E assumptions by scenario', 'Floor', 'Bear', 'Base', 'Bull']]
for lbl_, k, f_ in [('Fibre tonnes sold', 'd_fvol', n0), ('Fibre spread over ACN (Rs./kg)', 'd_fspr', n1), ('Fibre EBITDA per kg (Rs.)', 'd_febkg', n1),
                    ('Film EBITDA per kg (Rs.)', 'd_cebkg', n1), ('Ethanol volume (KL)', 'd_evol', n0), ('Ethanol EBITDA per litre (Rs.)', 'd_eebl', n1),
                    ('EBITDA (Rs. cr)', 'd_eb', n0)]:
    rows.append([lbl_, *[f_(RUN[nm][k][1]) for nm in ['floor', 'bear', 'base', 'bull']]])
table(rows, [2.6, 1.0, 1.0, 1.0, 1.0])

rows = [['Key driver (base)', 'FY27E', 'FY28E', 'FY29E', 'FY30E', 'FY26A'],
        ['Fibre tonnes sold', *[n0(dl('fvol', c)) for c in 'CDEF'], n0(seg('fsale'))],
        ['Fibre spread over ACN (Rs./kg)', *[n1(dl('fspr', c)) for c in 'CDEF'], n1(seg('fspr'))],
        ['Fibre EBITDA per kg (Rs.)', *[n1(dl('febkg', c)) for c in 'CDEF'], n1(seg('febitdakg'))],
        ['ACN price (Rs./kg, passed through)', *[n0(dl('acn', c)) for c in 'CDEF'], n0(seg('facnpx'))],
        ['Film tonnes / EBITDA per kg', *[f"{n0(dl('cvol', c))} / {n1(dl('cebkg', c))}" for c in 'CDEF'], f"{n0(seg('csale'))} / {n1(seg('cebitdakg'))}"],
        ['Ethanol KL / EBITDA per litre', *[f"{n0(dl('evol', c))} / {n1(dl('eebl', c))}" for c in 'CDEF'], f"{n0(seg('esale'))} / {n1(seg('eebitdal'))}"]]
table(rows, [2.3, 1.0, 1.0, 1.0, 1.0, 1.0])
rows = [['Base case (Rs. crore)', 'FY26A', 'FY27E', 'FY28E', 'FY29E', 'FY30E'],
        ['Revenue', n0(rev26), *[n0(x) for x in base_fc['rev']]], ['EBITDA', n0(eb26), *[n0(x) for x in base_fc['ebitda']]],
        ['EBITDA margin', pc(g(pl, R['ebm'], 'K')), *[pc(x) for x in base_fc['ebm']]], ['PAT', n0(pat26), *[n0(x) for x in base_fc['pat']]],
        ['EPS (Rs.)', n2(g(pl, R['eps'], 'K')), *[n2(x) for x in base_fc['eps']]]]
table(rows, [2.3, 1.0, 1.0, 1.0, 1.0, 1.0])
para(f'FY27E profit is high because H1 is already banked (PAT Rs.{n0(h1["pat"])} crore); after that our base falls as fibre margins normalise. The base sits {pc0(BA["pos"][1])} of the way from floor to bull on FY28E EBITDA and below the bull case on revenue and margin in every year; it is nearer the floor in FY29-FY30 because the bull case adds a 240 KLPD distillery that nobody has approved yet.')

# =============================================================== 8
head('8. What the price is paying for')
rows = [['FY28E', 'Floor (memo)', 'Bear', 'Base', 'Bull']]
lbl = ['Revenue', 'EBITDA', 'EBITDA margin', 'PAT', 'EPS (Rs.)', f'Target at {PE:.1f}x (Rs.)', 'Upside vs CMP']
fmt = [n0, n0, pc, n0, n2, n0, lambda x: f'{x*100:+.0f}%']
for i, l in enumerate(lbl): rows.append([l, *[fmt[i](tab[nm][i]) for nm in ['floor', 'bear', 'base', 'bull']]])
table(rows, [2.0, 1.2, 1.2, 1.2, 1.2])
mid = [g(va, V['mid'] + i, 'C') for i in range(1, 6)]
para(f'Multiple. We use {PE:.1f}x FY28E earnings in every case. The closest listed peers trade at about 7x (Vardhman Acrylics 7.1x, a debt-free pure fibre maker) and 6x (Gulshan Polyols 5.8x, grain ethanol); film makers trade higher (Cosmo First 15.5x) but film is only a tenth of PAL. PAL itself has traded at a median 7.6x the year\'s earnings over FY17-FY26. Peer multiples are from Screener and are to be checked on Bloomberg. Today the stock is on {CMP / ttm_eps:.1f}x trailing earnings, which looks cheap only because trailing earnings are at a cyclical peak.')
para(f'Checks. EV/EBITDA: at the CMP the business trades on {g(va, V["evm_now"], "C"):.1f}x FY28E base EBITDA after counting FY27E net cash; at 4.5x the value is Rs.{n0(g(va, V["ev_tp"], "C"))} a share, close to the P/E answer. Reverse check: at {PE:.1f}x the price implies FY28E PAT of Rs.{n0(g(va, V["rev_pat"], "C"))} crore, {abs(g(va, V["rev_gap"], "C"))*100:.0f}% below our base of Rs.{n0(g(va, V["base_pat"], "C"))} crore and roughly where FY26 plus a little ethanol growth would land. Mid-cycle: at the 10-year average EBITDA margin of {pc(mid[0])} the FY28E base revenue earns about Rs.{n0(mid[3])} crore of PAT, worth Rs.{n0(mid[4])} a share at {PE:.1f}x, below the price. So the market is already paying for profits above mid-cycle, but not for today\'s peak.')
para(f'Rating. Base target Rs.{n0(TP)} is {UP*100:+.1f}% from the CMP: HOLD, and borderline ({DIST:.1f} points below the BUY line). "Chance of management\'s plan already in the price" = (CMP - base target) / (bull target - base target) = {CH*100:.0f}%: negative, meaning the price sits below our base and pays nothing for the bull case. The asymmetry is not comfortable, though: the bull case adds Rs.{n0(tab["bull"][5] - TP)} a share, the bear case takes away Rs.{n0(TP - tab["bear"][5])}.')
rows = [['P/E (x)', 'Floor', 'Bear', 'Base', 'Bull']]
for m in [5, 6, 7, 7.5, 8, 9, 10]: rows.append([f'{m}', *[n0(m * tab[nm][4]) for nm in ['floor', 'bear', 'base', 'bull']]])
table(rows, [1.2, 1.1, 1.1, 1.1, 1.1])

# =============================================================== 9
head('9. Management guidance vs our cases')
para('PAL holds no earnings calls and publishes no presentations or targets. What we can test is what lenders were told (via CARE) and what the annual reports promised, against what happened.')
rows = [['Promise (source)', 'Delivered'],
        ['CPP film "shall do well as demand is on the rise" (AR FY19 p.7)', 'Utilisation 39-76%; losses FY23-FY25; first decent profit FY26'],
        ['Ethanol plant from FY25, cost Rs.182.6 cr (CARE Mar-2023, Aug-2023)', 'Started 24-Mar-2025 (last week of FY25); spend close to budget'],
        ['Ethanol start October 2024 (CARE Jul-2024 p.2)', 'About five months late'],
        ['CARE projection: cash accruals ~Rs.75 cr in FY27 (CARE Jun-2026 p.3)', f'H1FY27 PAT + depreciation already Rs.{n0(h1["pat"] + 6.4)} cr: far ahead'],
        ['Capacity 150 to 180 KLPD (AR FY26 p.11)', 'Consents received; H1FY27 volumes fell anyway (allocation)']]
table(rows, [3.8, 3.2])
rows = [['FY28E', 'Stated plan (bull)', 'Our base', 'Reality check'],
        ['Fibre utilisation', '95%', pc0(dl('futil', 'D')), 'Averaged ~85% over FY17-FY26; 90% in FY26'],
        ['Fibre EBITDA per kg', n1(BU['d_febkg'][1]), n1(BA['d_febkg'][1]), f'best full year Rs.17.3 (FY21); 10-yr PBIT avg Rs.{n1(mid_febit)}'],
        ['Ethanol volume (KL)', n0(BU['d_evol'][1]), n0(BA['d_evol'][1]), 'ESY27 allocation 50,745 KL; H1FY27 ~17,000 KL'],
        ['Revenue (Rs. cr)', n0(tab['bull'][0]), n0(tab['base'][0]), 'FY26 Rs.1,010 cr'],
        ['EBITDA margin', pc(tab['bull'][2]), pc(tab['base'][2]), f'10-yr avg {pc(mid_ebm)}; H1FY27 {pc(h1["ebm"])}']]
table(rows, [1.6, 1.4, 1.2, 2.8])

# =============================================================== 10
head('10. What would make us wrong')
risks = [('The fibre windfall lasts.', 'If H1FY27 margins hold for two more years (Indian Acrylics stays down, ACN stays cheap, duty revived), FY28E EPS is nearer Rs.15 and the stock is worth over Rs.110.', 'Q3FY27 and Q4FY27 fibre margin above 15%; a CBIC duty notification.', 'February and May 2027 results.'),
         ('The fibre spread collapses.', 'An ACN price fall leaves 4-5 months of dear stock to sell cheap (as in FY24, PBIT Rs.8 per kg) and imports undercut prices; EPS falls towards Rs.2.', 'Fibre PBIT margin below 8%; inventory staying near Rs.195 crore.', 'Next two quarters.'),
         ('Ethanol allocations shrink.', 'India has nearly twice the capacity it needs; a smaller allocation or a grain-price spike halves ethanol profit.', 'ESY 2027-28 allocation (around November 2027); maize and FCI rice prices.', 'Through FY28.'),
         ('Cash does not reach shareholders.', 'Profits are kept and partly paid out as promoter commission; the stock stays on a low multiple whatever the earnings.', 'Postal ballot result (31-Dec-2026); any dividend; MD pay in the FY27 annual report.', 'Jan-Aug 2027.'),
         ('A new project we have not priced.', 'A 240 KLPD expansion or another diversification could add value or repeat the slow film ramp.', 'Board approval and project cost disclosure.', 'Any time.')]
for t_, how, tell, when in risks:
    para(f'{how} What would tell us: {tell} When: {when}', lead=t_)

# =============================================================== 11
head('11. Questions to discuss')
qs = ['Why did fibre profit per kg double in H1FY27: cheap ACN stock, fewer imports, a competitor\'s outage, or better product mix? How much of it is inventory gain?',
      'Why did inventory rise from Rs.103 crore to Rs.195 crore between March and September 2026? Is it ACN bought ahead of a price rise?',
      'The August 2025 DGTR recommendation for anti-dumping duty was not notified (Indian Acrylics AR FY26). Is the industry appealing, and does PAL plan for a world without the duty?',
      'Why did distillery sales fall to Rs.133 crore in H1FY27 from Rs.171 crore? What was the ESY 2025-26 allocation and how much was supplied?',
      'Is the 240 KLPD expansion real: cost, funding, approvals, date?',
      'What is the true ethanol price versus DDGS revenue per litre, and what grain mix (maize vs FCI rice) is used?',
      'Why has no dividend been paid for 12+ years while the MD\'s commission rose 90% in FY26? What payout policy will the board adopt?',
      'Is fibre capacity 42,000 or 45,000 tonnes, and what does it take to run above 100% as in FY19?',
      'What did the June 2025 fire cost and what insurance was received?',
      'Who are the largest fibre customers, and how much of fibre is sold as tow/tops versus staple fibre?',
      'What returns does management target from the film line, which earned little for seven years?']
for i, x in enumerate(qs): para(f'{i + 1}. {x}', space_after=2)

head('Bottom line')
para(f'Pasupati Acrylon is a well-financed, net-cash commodity spinner with a new ethanol leg, run by a promoter who pays himself well and pays shareholders nothing. Today\'s earnings (trailing EPS Rs.{n2(ttm_eps)}) are roughly double what a normal year produces, and nothing the company has said explains why. Our base case lets those margins fade and still gives FY28E EPS of Rs.{n2(tab["base"][4])}, worth Rs.{n0(TP)} at {PE:.1f}x: {UP*100:+.0f}% from here, a borderline HOLD. The price does not pay for the peak, but it also does not protect you if the spread reverts to the 10-year average (mid-cycle value about Rs.{n0(mid[4])}). This is a stock to own only with a view on the ACN spread and the anti-dumping duty.')
para('This note is for internal discussion and does not constitute investment advice.', 8, italic=True)
out = os.path.join(CO, 'Pasupati_Acrylon_Note_v1.docx'); doc.save(out); print(out)
