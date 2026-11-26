"""Build Bonfiglioli_Transmissions_Note_v1.docx from the recalculated BONFIG_Model_v2.xlsx (base selected) and
scripts/run_results_26Nov2026.json (scenario runs). Usage: python3 bft_note_v1.py"""
import json, os, openpyxl
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
CO = os.path.dirname(HERE)
M = openpyxl.load_workbook(os.path.join(CO, 'BONFIG_Model_v2.xlsx'), data_only=True)
RUN = json.load(open(os.path.join(HERE, 'run_results_26Nov2026.json')))
B, BE, BU, FL = RUN['2'], RUN['1'], RUN['3'], RUN['floor']
pl, va, q, sg, gp, dv = M['P&L'], M['Valuations'], M['Quarterly'], M['Segments'], M['Group_vs_ThirdParty'], M['Drivers']


def lab(ws, text, col='A'):
    for r in range(1, ws.max_row + 1):
        v = ws[f'{col}{r}'].value
        if isinstance(v, str) and v.strip().startswith(text.strip()): return r
    raise KeyError(text)


def V(ws, text, c, col='A'): return ws[f'{c}{lab(ws, text, col)}'].value
n0 = lambda x: f'{x:,.0f}'
n1 = lambda x: f'{x:,.1f}'
n2 = lambda x: f'{x:,.2f}'
pc = lambda x: f'{x*100:.1f}%'
pc0 = lambda x: f'{x*100:.0f}%'

CMP = va['C2'].value; MCAP = va['C4'].value
TP, UP, RATING = va['C21'].value, va['C22'].value, va['C23'].value
TPB, TPU, TPBE, TPF = va['G48'].value, va['G49'].value, va['G47'].value, va['C58'].value
CHANCE = va['C66'].value
def qv(k, c): return q[f'{c}{lab(q, k)}'].value
TPE = va['C18'].value

doc = Document()
st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
for m in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'): setattr(sec, m, Inches(0.65))
# header / footer
hp = sec.header.paragraphs[0]
hp.text = f'Bonfiglioli Transmissions Ltd  //  November 2026  //  Mcap Rs.{n0(MCAP)}cr\tBONFIG | NSE/BSE'
hp.paragraph_format.tab_stops.add_tab_stop(Inches(7.2), WD_TAB_ALIGNMENT.RIGHT)
for r in hp.runs: r.font.size = Pt(8); r.font.name = 'Arial'
fp = sec.footer.paragraphs[0]
fp.paragraph_format.tab_stops.add_tab_stop(Inches(7.2), WD_TAB_ALIGNMENT.RIGHT)
r = fp.add_run('Strictly Confidential - for internal circulation only\tPage '); r.font.size = Pt(8); r.font.name = 'Arial'
fld = OxmlElement('w:fldSimple'); fld.set(qn('w:instr'), 'PAGE'); rr = OxmlElement('w:r'); t = OxmlElement('w:t'); t.text = '1'; rr.append(t); fld.append(rr); fp._p.append(fld)


def para(text='', size=10, bold=False, italic=False, space_after=4, lead=None, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after); p.paragraph_format.space_before = Pt(0)
    if lead:
        r = p.add_run(lead + ' '); r.bold = True; r.font.size = Pt(size); r.font.name = 'Arial'
    r = p.add_run(text); r.bold = bold; r.italic = italic; r.font.size = Pt(size); r.font.name = 'Arial'
    if align: p.alignment = align
    return p


def head(text): return para(text, 12, True, space_after=3)
def srcline(text): return para(text, 7.5, italic=False, space_after=6)
def bullet(text, lead=None): return para(text, 10, lead=lead, space_after=3)


def shade(cell, color='D9D9D9'):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), color); tcPr.append(shd)


def table(rows, widths=None, first_bold=False):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.text = ''
            p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            run = p.add_run(str(val)); run.font.size = Pt(8.5); run.font.name = 'Arial'
            if i == 0: run.bold = True; shade(c)
            elif first_bold and j == 0: run.bold = False
            if j > 0 and i > 0: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if widths:
        t.autofit = False
        for j, gc in enumerate(t._tbl.tblGrid.gridCol_lst): gc.w = Inches(widths[j])
        for row in t.rows:
            for j, c in enumerate(row.cells): c.width = Inches(widths[j])
    return t


# ------------------------------------------------------------------ title block
para('Bonfiglioli Transmissions Ltd - India\'s gearbox leader, run on a licence from Italy, priced for the plan', 16, True, space_after=4)
para(f'NSE: BONFIG  |  BSE: 544996  |  CMP: Rs.{CMP:,.2f}  |  Market cap: Rs.{n0(MCAP)} crore  |  Rating: {RATING} (borderline)  |  Target price: Rs.{n0(TP)}  |  Upside: {UP*100:+.1f}%  |  Analyst: Dheeraj Kripalani', 9, True, space_after=2)
para('November 2026  |  Version 1 (26-Nov-2026)  |  CMP is the 26-Nov-2026 close, to be replaced with Bloomberg  |  The company\'s year runs January to December: FY25 means the year to 31-Dec-2025, FY27E the year to Dec-2027', 8, italic=True, space_after=8)

# ------------------------------------------------------------------ 1
head('The business in one minute')
para('A gearbox is the gear set of a bicycle for machines. An electric motor spins fast but weakly; the gearbox slows the spin and multiplies the force, so a conveyor belt, a mixer drum, an excavator\'s tracks or the blades of a wind turbine can turn. Bonfiglioli Transmissions (BTL) is the Indian arm of Bonfiglioli of Bologna, Italy, a 70-year-old family group with EUR 1.17 billion of sales. In India since 1998, it made about 3.4 lakh gearboxes and gear motors in FY25 at two plants near Chennai and one at Talegaon, Pune.')
para('Three kinds of buyer. (1) Factories (41% of FY25 sales): small standard gear motors for conveyors, mixers and packing lines, sold through 44 dealers and directly to machine builders; BTL has about a quarter of this Indian market. (2) Makers of construction, mining and farm machines such as JCB, CNH, Schwing Stetter, Ajax and Hyundai (25%): track, swing and drum drives designed together with the customer for each machine model. (3) Wind-turbine makers such as Suzlon, Nordex, Senvion and GE in the US (32%): yaw drives that turn the turbine into the wind and pitch drives that angle the blades.', lead=None)
para('How it gets paid. It invoices on delivery and is paid in about three months; contracts with machine makers carry price-variation clauses that pass on metal costs with a lag. One more party gets paid on every sale: the Italian parent. BTL uses the parent\'s designs and brand under a licence that costs 6% of sales of licensed products (4.4% of all sales) and pays another 2.4% of sales for group services. The parent also sells BTL parts, buys about a fifth of its output for its own sales companies abroad, and still owns 77% of the shares after selling 23% in the October 2026 IPO.')

# ------------------------------------------------------------------ 2
head('How one unit earns money')
rev25 = pl['D3'].value; units = sg[f'D{lab(sg, "Gear motors and gearboxes manufactured")}'].value
rpu = rev25 * 1e7 / units
rows = [['FY25, per average unit', 'Rs. per unit', 'Per Rs.100 of sales'],
        ['Selling price (revenue / 341,133 units)', n0(rpu), '100.0'],
        ['Materials (castings, forgings, gears, bearings, motors)', n0(rpu * pl['D8'].value), n1(pl['D8'].value * 100)],
        ['Employees', n0(rpu * pl['D9'].value / rev25), n1(pl['D9'].value / rev25 * 100)],
        ['Royalty to the Italian parent', n0(rpu * pl['D10'].value / rev25), n1(pl['D10'].value / rev25 * 100)],
        ['Group service fees and other professional fees', n0(rpu * pl['D11'].value / rev25), n1(pl['D11'].value / rev25 * 100)],
        ['Power, sub-contracting, freight, warranty, other', n0(rpu * pl['D12'].value / rev25), n1(pl['D12'].value / rev25 * 100)],
        ['EBITDA (operating profit before depreciation)', n0(rpu * pl['D15'].value), n1(pl['D15'].value * 100)],
        ['Net profit', n0(rpu * pl['D25'].value / rev25), n1(pl['D25'].value / rev25 * 100)]]
table(rows, [3.9, 1.4, 1.6])
srcline('Source: Prospectus p.209 (units), p.285 and note 30 p.318 (costs). The "unit" blends a Rs.5,000 worm gear motor with a multi-lakh wind or track drive, so it is an average, not a price.')
ue = M['Unit_Economics']
para(f'Against peers. Each on-roll employee produced Rs.{ue["B12"].value:.2f} crore of sales in FY25, three times Shanthi Gears (Rs.{ue["C12"].value:.2f} crore, FY26 annual report). Including contract workers, the figure is Rs.{ue["B14"].value:.2f} crore. Sales per rupee of fixed assets were 7.2 times against 2.9-4.2 for Elecon, Shanthi, Schaeffler and Timken (Prospectus p.119). The reason is the model: Chennai machines and heat-treats the big drives, while the factory gear motors are mostly assembled from bought parts, some from the parent.', lead=None)
rows = [['FY26 (Mar) / FY25 (Dec)', 'BTL', 'Elecon', 'Shanthi Gears', 'Timken India', 'Schaeffler India']]
rows.append(['Revenue, Rs. crore'] + [n0(ue[f'{c}4'].value) for c in 'BCDEF'])
rows.append(['EBITDA margin'] + [pc(ue[f'{c}5'].value) for c in 'BCDEF'])
rows.append(['ROCE (company definition)'] + [pc0(ue[f'{c}16'].value) for c in 'BCDEF'])
rows.append(['Sales / fixed assets (x, PPE + CWIP)'] + ['7.2'] + [n1(ue[f'{c}15'].value) for c in 'CDEF'])
rows.append(['Sales per on-roll employee, Rs. crore', n2(ue['B12'].value), 'Bloomberg', n2(ue['C12'].value), 'Bloomberg', 'Bloomberg'])
rows.append(['P/E at 28-Sep-2026 (trailing)', '63x at CMP', '31.6x', '63.4x', '57.7x', '53.7x'])
table(rows, [2.3, 0.9, 0.9, 0.9, 0.9, 1.1])
srcline('Source: Prospectus p.112, p.119 (peer KPIs and P/E); Shanthi Gears annual report FY2025-26 (employees). "Bloomberg" = to be checked on Bloomberg.')
para('Not disclosed: prices or margins by product or vertical (the company reports one segment), the margin on sales to group companies versus outside customers, units for any year other than FY25, and any order book. The licence lists the royalty-bearing products but not their share of each vertical.', lead='What is missing.')

# ------------------------------------------------------------------ 3
head('Who buys and how much')
tm = M['TAM']
rows = [['India market (F&S, Prospectus)', 'FY26, Rs. cr', 'FY31F, Rs. cr', 'Growth a year', 'BTL FY25 sales, Rs. cr', 'BTL share']]
for rr_, nm in [(4, 'Gear motors below 15 kNm (factories)'), (5, 'Heavy-duty gearboxes above 15 kNm'), (6, 'Off-highway machine drives'), (7, 'Wind yaw and pitch drives')]:
    rows.append([nm, n0(tm[f'C{rr_}'].value), n0(tm[f'D{rr_}'].value), pc(tm[f'E{rr_}'].value), n0(tm[f'F{rr_}'].value), pc0(tm[f'G{rr_}'].value) if rr_ != 7 else 'about 68% of local makers'])
table(rows, [2.5, 0.9, 0.9, 0.9, 1.1, 1.2])
srcline('Source: Prospectus p.151-157, 167-169, 176-178, 206 (Frost & Sullivan, paid for by the company). Indian market years end in March. BTL wind sales include exports to the US and Europe, so they exceed its Indian share.')
para(f'Concentration. Ten customers bought {pc(sg["D"+str(lab(sg,"Top-10 customers"))].value)} of FY25 sales and the largest, GE (wind, USA), {pc(sg["D"+str(lab(sg,"Largest customer"))].value)}. The text of the prospectus says the top ten were "less than 31.72%" in every period, which its own table contradicts (p.207 vs p.230). GE cut its orders by about 30% in the first nine months of 2026 (call p.11); other wind customers grew 22%, so wind sales were flat.', lead=None)
rows = [['Rs. crore', 'FY23', 'FY24', 'FY25', '9M FY25', '9M FY26', '9M growth']]
for k, nm in [('Industry & Automation revenue', 'Factories (I&A)'), ('Off-Highway Mobility revenue', 'Off-highway'), ('Wind revenue', 'Wind')]:
    sr = {'Factories (I&A)': 5, 'Off-highway': 6, 'Wind': 7}[nm]
    rows.append([nm] + [n0(sg[f'{c}{sr}'].value) for c in 'BCD'] + [n0(qv(k, 'I')), n0(qv(k, 'J')), pc(qv(k, 'J') / qv(k, 'I') - 1)])
table(rows, [1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8])
srcline('Source: Prospectus p.207; investor presentation slide 8 (9M).')
para('How orders are won. Factory gear motors are catalogue products sold through dealers (36 of 44 exclusive) and direct; no single industry is above 10% of that vertical. Machine and wind drives are designed with the customer over up to 30 months and then supplied for the life of the machine model, which makes them sticky: seven of the top ten machine and wind customers have bought for over ten years (p.214-215). The design rights stay with the Italian parent (p.225-226).')
para(f'Exports. Exports were {pc(1 - sg["D30"].value / sg["D36"].value)} of FY25 sales and 30.6% in the first nine months of 2026. Most go to group sales companies (Bonfiglioli USA, Germany, Italy, UK, Brazil, Spain); the main outside buyer abroad is GE. The licence explains why: BTL may sell licensed products only in India, Pakistan, Bangladesh, Sri Lanka and Nepal, and outside that only to group companies with the parent\'s consent (licence clause 7.2).')

# ------------------------------------------------------------------ 4
head('Can they deliver')
rows = [['FY25, machine hours', 'Available', 'Used', 'Utilisation', 'Makes']]
for i, (nm, mk) in enumerate([('Thirumudivakkam machine shop', 'off-highway, wind'), ('Thirumudivakkam assembly', 'off-highway, wind'), ('Mannur assembly', 'factory gear motors'), ('Mannur machine shop (bought Dec-25)', 'parts'), ('Talegaon (Pune) assembly', 'factory gear motors')]):
    r0 = 49 + 3 * i
    rows.append([nm, n0(sg[f'D{r0}'].value), n0(sg[f'D{r0+1}'].value), pc0(sg[f'D{r0+2}'].value) if sg[f'D{r0}'].value else 'new', mk])
rows.append(['Total', n0(sg[f'D{64}'].value), n0(sg[f'D{65}'].value), pc0(sg[f'D{66}'].value), '75% in H1 2026'])
table(rows, [2.6, 1.0, 1.0, 0.9, 1.6])
srcline('Source: Prospectus p.216, 232-234. Hours = machines x 22.5 hours x 302 days; utilisation is the company\'s own estimate.')
para('Capacity. The machine shop that makes the big drives runs at 81%; assembly has room. Management will spend about Rs.100 crore in 2026 and Rs.150 crore in 2027, mainly a heavy-duty gearbox plant next to the Pune site, built from mid-2027 and useful "after CY28"; the Mannur plant moves to Pune in late 2028 (call p.8, 13-14). Our check (Drivers sheet) shows the management plan would need about 90% of today\'s hours by FY28 without that expansion, so the capex is not optional for the bull case.', lead=None)
para('People and supply chain. 627 employees on roll and 1,032 including contract workers (June 2026). 70% of materials are bought in India; the largest supplier, at 15-20% of purchases, is the parent\'s Italian factory, Bonfiglioli Riduttori (p.21, p.237).')
pl_r = lambda k: lab(pl, k)
para(f'Working capital. Cash is tied up for about 90 days (receivables 94 days, inventory 93, payables 97 in FY25). Group companies pay much later than outside customers: about 150 days against about 84 days (receivables from group Rs.127 crore at Dec-25 and Rs.160 crore at Jun-26, p.330). Cash from operations was only {pc0(pl["D"+str(pl_r("CFO / EBITDA"))].value)} of EBITDA in FY25.', lead=None)
para(f'The IPO money: none of it reached the company. The IPO was a pure offer for sale. The seller was the Italian parent, Bonfiglioli S.p.A., which sold 4.32 crore shares (23%) at Rs.586 for Rs.2,534 crore and also paid the Rs.121 crore of offer costs (Prospectus cover, p.106-107). Its average cost is Rs.6.77 a share (p.51), so it sold at 87 times cost. Rs.586 was 46 times FY25 earnings, 30 times FY25 EV/EBITDA and 10.7 times June-2026 book value (p.51, p.110-111). Before the IPO the parent had already taken Rs.{n0(va["C89"].value)} crore out in 2023-mid 2026 as dividends and a buyback, including a Rs.110 crore interim dividend in the first half of 2026 (p.280). What it implies: the company gains a listing and nothing else; the seller chose the timing and price; and the parent still has to sell at least two more percent to bring public holding to the 25% minimum, an overhang after the six-month lock-in ends in April 2027 (p.100).', lead=None)

# ------------------------------------------------------------------ 5
head('What the numbers say')
cols = ['B', 'C', 'D']
rows = [['Rs. crore', 'FY23', 'FY24', 'FY25', '9M FY25', '9M FY26', 'Q3 FY25', 'Q3 FY26']]
rows.append(['Revenue'] + [n0(pl[f'{c}3'].value) for c in cols] + [n0(qv('Revenue from operations', c)) for c in 'IJBF'])
rows.append(['  growth'] + ['', pc(pl['C4'].value), pc(pl['D4'].value)] + ['', pc(qv('Revenue growth YoY', 'J')), '', pc(qv('Revenue growth YoY', 'F'))])
rows.append(['EBITDA'] + [n0(pl[f'{c}14'].value) for c in cols] + [n0(qv('EBITDA (excl. other income)', c)) for c in 'IJBF'])
rows.append(['  margin'] + [pc(pl[f'{c}15'].value) for c in cols] + [pc(qv('EBITDA margin', c)) for c in 'IJBF'])
rows.append(['PAT'] + [n0(pl[f'{c}25'].value) for c in cols] + [n0(qv('PAT', c)) for c in 'IJBF'])
rows.append(['EPS (Rs., today\'s shares)'] + [n2(pl[f'{c}28'].value) for c in cols] + [n2(qv('EPS', c)) for c in 'IJBF'])
rows.append(['Cash from operations'] + [n0(pl[f'{c}{pl_r("Cash from operations (CFO)")}'].value) for c in cols] + ['', '', '', ''])
rows.append(['Free cash flow'] + [n0(pl[f'{c}{pl_r("Free cash flow (CFO - capex)")}'].value) for c in cols] + ['', '', '', ''])
rows.append(['Return on equity'] + ['', pc0(pl[f'C{pl_r("ROE (PAT")}'].value), pc0(pl[f'D{pl_r("ROE (PAT")}'].value)] + ['', '', '', ''])
table(rows, [1.7, 0.7, 0.7, 0.7, 0.75, 0.75, 0.75, 0.75])
srcline('Source: Prospectus p.285-286 (restated, continuing operations); results for the quarter to 30-Sep-2026 p.1 (9M and Q3 FY25 restated for the BDSPL business bought from a group company). CFO FY26 and later quarters are not reported.')
rows = [['Rs. crore', 'Q3 FY25', 'Q4 FY25', 'Q1 FY26', 'Q2 FY26', 'Q3 FY26']]
for k, f_ in [('Revenue from operations', n0), ('EBITDA (excl. other income)', n0), ('EBITDA margin', pc), ('PAT', n0)]:
    rows.append([k.replace(' from operations', '').replace(' (excl. other income)', '')] + [f_(qv(k, c)) for c in 'BCDEF'])
for k, nm in [('Industry & Automation revenue', 'Factories (I&A)'), ('Off-Highway Mobility revenue', 'Off-highway'), ('Wind revenue', 'Wind')]:
    rows.append([nm] + [n0(qv(k, c)) if qv(k, c) not in (None, '') else '-' for c in 'BCDEF'])
table(rows, [2.2, 0.9, 0.9, 0.9, 0.9, 0.9])
srcline('Source: results p.1; Q4 FY25 = FY25 less 9M FY25; Q1 FY26 = H1 (Prospectus) less Q2. Vertical split from the investor presentation, slides 7-8; quarters not shown are not disclosed.')
doc.add_picture(os.path.join(CO, 'exhibits', 'exhibit1_revenue_margin.png'), width=Inches(7.0))
srcline('Exhibit 1. Source: Prospectus p.285; model base case; guidance path = FY25 revenue grown 20% in FY26 and 15% a year after (earnings release p.2, call p.16), extended to FY30 by us.')
para(f'What changed. Margin rose from 14.5% in FY23 to 18.4% in FY25 and 19.7% in the first nine months of 2026. The company credits buying more parts in India (64% to 71% of materials), bringing machining in-house and scale. 2026 also had help that management says will not repeat: a weaker rupee on 31% exports and price rises that ran ahead of costs (call p.11-12). FY24 and FY25 profits include Rs.14 crore and Rs.8 crore of one-off income from the parent after a transfer-pricing tax settlement (p.316, p.372). Growth was below 10% a year in FY23-FY25, then jumped to 23% in 2026: off-highway +43% on new programmes (John Deere among them), factories +26% on an industrial recovery, wind +3% because GE cut orders.', lead=None)
para('A note on the base. The first nine months of 2025 in the results (Rs.167.5 crore profit) do not equal the prospectus first half plus the results third quarter (Rs.178.0 crore), so the reported 40.7% nine-month profit growth is on a low base; on the higher base it is about 32% (results note 5).', lead=None)

# ------------------------------------------------------------------ 6
head('The people and the money trail')
para('Who owns it. The Bonfiglioli family controls BON-FI S.r.l., which owns Bonfiglioli S.p.A. (BSPA), which owns 77% of BTL. Sonia Bonfiglioli, the group chair and CEO, sits on the board; the managing director (K.V. Kaippally) and CFO (G.A. Balaji) are long-time employees. Short-term pay in FY25 was Rs.2.1 crore for the MD and Rs.1.5 crore for the CFO (p.80). Auditor: S.R. Batliboi (EY network).')
rows = [['Rs. crore', 'FY23', 'FY24', 'FY25', 'H1 FY26']]
gl = lambda k: lab(gp, k)
def gvals(k, fmt=n0): return [fmt(gp[f'{c}{gl(k)}'].value) for c in 'BCDF']
rows.append(['Sales to group companies'] + gvals('Inter-company sales'))
rows.append(['  share of sales'] + gvals('  group share of revenue', pc))
rows.append(['Purchases from Bonfiglioli Riduttori (Italy)'] + gvals('Purchases from Bonfiglioli Riduttori'))
rows.append(['Royalty to BSPA'] + gvals('Royalty to BSPA'))
rows.append(['Service fees to BSPA'] + gvals('Service fees to BSPA'))
rows.append(['Royalty + fees + commission, % of sales'] + gvals('  as % of revenue', pc))
rows.append(['  same, % of EBITDA before these charges'] + gvals('  as % of EBITDA before', pc))
rows.append(['Dividends and buyback paid to the group'] + [n0(gp[f'{c}{gl("Dividends to BSPA")}'].value + gp[f'{c}{gl("Buyback from group")}'].value) for c in 'BCDF'])
rows.append(['Days of group sales still unpaid'] + gvals('  days of group sales outstanding'))
table(rows, [3.2, 0.9, 0.9, 0.9, 0.9])
srcline('Source: Prospectus related-party tables p.73-82 and balances p.330; channel table p.208, 228. Group margins are not disclosed.')
rows = [['Rs. crore', 'FY23', 'FY24', 'FY25', 'H1 FY26']]
rows.append(['Exports (sales outside India)'] + gvals('Exports (revenue'))
rows.append(['  to group companies'] + gvals('  of which to group'))
rows.append(['  to outside buyers abroad (mainly GE)'] + gvals('  of which to third parties'))
rows.append(['Group receivables at period end'] + gvals('Group receivables at period end'))
table(rows, [3.2, 0.9, 0.9, 0.9, 0.9])
srcline('Source: Prospectus p.227-228 (geography), p.208/228 (inter-company), p.330 (balances). Germany and China sales are almost entirely to group companies; in the US, Rs.79 crore of Rs.308 crore went to Bonfiglioli USA in FY25.')
para(f'India inside the group. Management says India was about 15% of group sales but 32% of group EBITDA in 2025 (call p.4). That puts the rest of the group near an 8% EBITDA margin against India\'s 18%. India is the group\'s profit engine, which cuts both ways: the parent wants it to grow, and the parent decides how much of its profit flows back to Italy through royalty, fees and transfer prices. If group sales earned only 8-12% margin, outside sales would be earning about 20%; nobody outside the company can check this (Group_vs_ThirdParty sheet).', lead=None)
para('Red flags (each checked against the page)', 10, True, space_after=2)
bullet('The licence is the business. BSPA owns the designs, the brand and every improvement BTL makes (clause 7.4). The licence renews each year and either side can end it with three months\' notice before 31 December (clause 9.2). BTL may sell licensed products only in South Asia, and abroad only to group companies with consent (clause 7.2). There is no non-compete: every group company except the R&D unit is in the same business (Prospectus p.408).', 'The parent sets the rules.')
bullet('Royalty, service fees and the US sales commission took 6.8% of FY25 sales, 27% of EBITDA before these charges. Income-tax officers disallowed part of the BSPA service charges as above arm\'s length in five assessment years (2015-16 to 2023-24); the company settled under Vivad se Vishwas and BSPA refunded Rs.22 crore, which BTL booked as revenue (p.338, p.367, p.372).', 'Fees the taxman questioned.')
bullet('Group receivables were Rs.160 crore at June 2026, about 128 days of group sales against roughly 84 days for outside customers, and BTL also lends to a fellow group company (Rs.13 crore, p.330). Minority shareholders are financing the group\'s distribution.', 'The group pays late.')
bullet(f'Rs.110 crore of interim dividend went to the parent in the first half of 2026, months before an IPO in which the company raised nothing; the parent then sold 23% at 87 times its cost (p.51, p.280).', 'Cash out before the float.')
bullet('GE was the largest customer in FY25 (11.4% of sales) and cut orders by about 30% in 2026; the US took 15.5% of FY25 sales and the prospectus flags US tariffs as a risk (p.35-36; call p.11).', 'One US customer drives wind.')
para('Quirks, not yet flags', 10, True, space_after=2)
para('The auditor noted that the audit trail was not switched on for all transactions and back-ups were not kept daily on servers in India (p.345-346). Some company records from 1998-2001 cannot be traced at the registrar (p.30). The Mannur lease is not properly stamped or registered (p.240). The second-quarter 2026 results were not reviewed by the auditor (results note 3). The prospectus disagrees with itself on top-ten customer share and on FY24 group sales (2,755 vs 2,775 million, p.208 vs p.228).', space_after=6)

# ------------------------------------------------------------------ 7
head('Our estimates')
para(f'Floor: what is visible now (nine months of 2026 actual, a flat fourth quarter, then 7% a year and a 17.5% margin). Base: the most likely case - each business grows at its market rate from the Frost & Sullivan report plus the share gain it has shown, cut for a record of under-10% growth in FY23-FY25 and for wind\'s dependence on GE; margin 18.2%. Bull: management guidance in full - about 20% growth in 2026, 15% a year in 2027-2028 (extended to 2030) and an 18.5% margin. Bear: GE and US tariffs hit wind, the construction-machine cycle turns, and margin falls back to the FY24 level (16%).')
rows = [['Business', 'Market growth', 'Source', 'Our base FY27-30', 'Guidance']]
rows.append(['Factory gear motors', '8.0% a year', 'Prospectus p.156-157', '8.5% a year', 'no split'])
rows.append(['Off-highway drives', '9.6% a year', 'Prospectus p.168', '14% then 11%', 'no split'])
rows.append(['Wind yaw and pitch drives', '9.9% India; ~5% global', 'Prospectus p.174, 178', '8-9% a year', 'no split'])
rows.append(['New heavy-duty plant', '7.5% a year', 'Prospectus p.151-153', 'Rs.10/45/90 cr FY28-30', 'after CY28'])
rows.append(['Company', f'{pc(dv["D"+str(lab(dv,"Memo: F&S market growth"))].value)}', 'weighted', f'{pc((B["rev"][7]/B["rev"][3])**0.25-1)} a year', '15% a year'])
table(rows, [1.9, 1.3, 1.5, 1.3, 1.0])
srcline('Source: F&S figures as printed in the Prospectus; guidance from the earnings release p.2 and the call of 13-Nov-2026 p.7, 16. Base revenue lands 42-52% of the way from the floor to guidance in FY27-FY30.')
rows = [['Driver (base)', 'FY26E', 'FY27E', 'FY28E', 'FY29E', 'FY30E']]
vr = lambda k: [dv[f'{c}{lab(dv, k)}'].value for c in 'CDEFG']
rows.append(['Factory gear motors growth (FY26E: Q4 year on year)'] + [pc(x) for x in vr('I&A (existing products) growth (FY26E = Q4 YoY) - LIVE')])
rows.append(['Off-highway growth'] + [pc(x) for x in vr('Off-Highway Mobility growth (FY26E = Q4 YoY) - LIVE')])
rows.append(['Wind growth'] + [pc(x) for x in vr('Wind growth (FY26E = Q4 YoY) - LIVE')])
rows.append(['Materials, % of sales'] + [pc(x) for x in vr('Materials cost % of core revenue - LIVE')])
rows.append(['Royalty, % of sales (6% x 74% licensed)'] + [pc(a * b) for a, b in zip(vr('Licensed-product sales'), vr('Royalty rate'))])
rows.append(['Capex, Rs. crore'] + [n0(x) for x in vr('Capex')])
table(rows, [2.6, 0.8, 0.8, 0.8, 0.8, 0.8])
rows = [['Rs. crore (base)', 'FY25A', 'FY26E', 'FY27E', 'FY28E', 'FY29E', 'FY30E']]
rows.append(['Revenue'] + [n0(x) for x in B['rev'][2:]])
rows.append(['  growth'] + [pc(x) for x in B['growth'][2:]])
rows.append(['EBITDA'] + [n0(x) for x in B['ebitda'][2:]])
rows.append(['  margin'] + [pc(x) for x in B['ebm'][2:]])
rows.append(['PAT'] + [n0(x) for x in B['pat'][2:]])
rows.append(['EPS (Rs.)'] + [n2(x) for x in B['eps'][2:]])
rows.append(['Free cash flow'] + [n0(x) for x in B['fcf'][2:]])
rows.append(['Bull EPS (Rs.)'] + [n2(x) for x in BU['eps'][2:]])
rows.append(['Bear EPS (Rs.)'] + [n2(x) for x in BE['eps'][2:]])
table(rows, [1.9, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8])
srcline('Source: BONFIG_Model_v2.xlsx (Drivers and P&L sheets). FY26E includes nine months of actual results.')
HOLD_UP = B['rev'][4] * (0.197 - B['ebm'][4]) * (1 - 0.255) / B['pat'][4]
para(f'Base EPS is flat in FY27E because the margin falls from about {pc(B["ebm"][3])} in 2026 to {pc(B["ebm"][4])}: management itself guides to 18.5% and says the 2026 forex and pricing gains will not repeat. If the nine-month 2026 margin (19.7%) held, FY27E EPS would be about {HOLD_UP:.0%} higher.', lead=None)

# ------------------------------------------------------------------ 8
head('What the price is paying for')
para(f'At Rs.{CMP:,.2f} the stock trades at {va["C10"].value:.0f} times the last twelve months\' profit, {va["C12"].value:.0f} times FY25 profit, {va["C11"].value:.0f} times trailing EV/EBITDA and {va["C13"].value:.1f} times book. It has risen {CMP/586-1:.0%} from the Rs.586 IPO price and {CMP/574.5-1:.0%} from the Rs.574.50 listing-day close, most of it after the September-quarter results.')
para(f'The multiple. We use {TPE:.0f} times FY27E earnings per share (the P/E, price divided by EPS) in every case. The prospectus peers - Elecon, Shanthi Gears, Schaeffler India and Timken India - traded at an average 51.6 times trailing earnings on 28-Sep-2026 (p.110, p.112). Rolled forward to our FY27E year at about 9% a year of earnings growth, that is about 45 times. No premium: 6.8% of sales leaves as royalty and fees, the parent owns the designs and the territory, and wind leans on one US customer. No discount: returns on capital (34%) and net cash beat every peer. Current peer multiples, and SKF, Siemens or ABB motion businesses: to be checked on Bloomberg.', lead=None)
para(f'Reverse check. At {TPE:.0f} times, the price needs FY27E profit of Rs.{n0(va["C38"].value)} crore (EPS Rs.{va["C41"].value:.2f}). Our base gives Rs.{n0(va["C39"].value)} crore; management\'s plan gives Rs.{n0(BU["pat"][4])} crore. The price needs about {va["C43"].value:.0%} a year profit growth from FY25 to FY27.', lead=None)
rows = [['Case', 'FY27E revenue', 'FY27E EBITDA', 'FY27E EPS', f'Target ({TPE:.0f}x)', 'vs CMP', 'Rating']]
for nm, x, tpv in [('Floor (memo)', FL, TPF), ('Bear', BE, TPBE), ('Base', B, TPB), ('Bull = guidance', BU, TPU)]:
    rows.append([nm, n0(x['rev'][4]), n0(x['ebitda'][4]), n2(x['eps'][4]), n0(tpv), f'{tpv/CMP-1:+.1%}', 'BUY' if tpv / CMP - 1 > 0.15 else ('HOLD' if tpv / CMP - 1 >= -0.05 else 'SELL')])
table(rows, [1.5, 1.0, 1.0, 0.9, 1.0, 0.8, 0.7])
srcline(f'Source: Valuations sheet. EV/EBITDA cross-check: 29 times FY27E EBITDA plus FY26E net cash gives Rs.{n0(va["C33"].value)} a share for the base case (the IPO was priced at 29.7 times).')
para(f'How much of management\'s plan is already in the price: about {CHANCE:.0%}. The price sits {CHANCE:.0%} of the way from our base target (Rs.{n0(TPB)}) to the target if management delivers everything it has guided (Rs.{n0(TPU)}). Even full delivery of guidance is worth only {TPU/CMP-1:+.1%} from here at a {TPE:.0f} times multiple.', lead=None)
para(f'Rating: {RATING}, target Rs.{n0(TP)} ({UP*100:+.1f}%). This is borderline: the base target is only {abs(UP*100+5):.1f} points beyond the -5% line between SELL and HOLD. The rating turns on the multiple more than on the business: at 50 times the base target is Rs.{n0(va["C74"].value)} ({va["D74"].value:+.1%}, HOLD).', lead=None)
rows = [['P/E on FY27E', '35x', '40x', '45x', '50x', '55x', '60x'],
        ['Base target (Rs.)'] + [n0(va[f'C{71+i}'].value) for i in range(6)],
        ['vs CMP'] + [f'{va[f"D{71+i}"].value:+.0%}' for i in range(6)]]
table(rows, [1.6] + [0.8] * 6)

# ------------------------------------------------------------------ 9
head('Management guidance vs our cases')
para('Since the prospectus (October 2026) there has been one quarter. Management\'s first public guidance came with it on 12-13 November: about 20% sales growth in 2026, about 15% a year over the next two years, and an EBITDA margin "in the vicinity of 18.5%" over the period, explicitly not a yearly target. Delivered so far: 22.8% growth and a 19.7% margin in nine months, both ahead of the guide. Guidance on margin is below the evidence; management blames forex and price lag for the gap.')
rows = [['', 'Guidance', 'Bull (= guidance)', 'Base', 'Reality check']]
rows.append(['FY26 sales growth', '~20%', pc(BU['growth'][3]), pc(B['growth'][3]), '22.8% in 9M; Q4 needs only +12-13%'])
rows.append(['FY27 sales growth', '~15%', pc(BU['growth'][4]), pc(B['growth'][4]), 'FY23-25 grew 9-10% a year; GE recovery unconfirmed for H2'])
rows.append(['FY28 sales growth', '~15%', pc(BU['growth'][5]), pc(B['growth'][5]), 'Needs the Pune expansion on time'])
rows.append(['EBITDA margin FY27-28', '~18.5%', pc(BU['ebm'][4]), pc(B['ebm'][4]), '18.4% FY25, 19.7% 9M FY26'])
rows.append(['Capex FY26 / FY27', 'Rs.100 / 150 cr', 'same', 'same', 'Rs.70-80 cr spent by Sept'])
rows.append(['Royalty rate', 'no change', '6%', '6%', 'Renews each year at the parent\'s option'])
table(rows, [1.5, 1.0, 1.1, 0.8, 2.6])
srcline('Source: earnings release 12-Nov-2026 p.2; call 13-Nov-2026 p.7, 10-13, 16; model.')

# ------------------------------------------------------------------ 10
head('What would make us wrong')
EPS_UP = BU['eps'][4] + BU['rev'][4] * (0.197 - BU['ebm'][4]) * (1 - 0.255) / BU['pat'][4] * BU['eps'][4]
bullet(f'Wind returns with GE schedules for the second half of 2027 and new European programmes, sales grow as guided and 2026 margins (19.7%) hold. Then FY27E EPS is about Rs.{EPS_UP:.1f} and the stock is worth about Rs.{EPS_UP*45:,.0f} at 45 times ({EPS_UP*45/CMP-1:+.0%}). What would tell us: GE second-half orders (management expects word "in a month"), the December-quarter margin. When: February 2027 results.', '1. Growth and margin both beat.')
bullet('Indian capital-goods MNC subsidiaries (ABB, Siemens, Timken) trade at 50-95 times on Screener; if the market keeps paying that for a 34% ROCE business, 45 times is too low. What would tell us: the stock holding above Rs.800 after the April 2027 lock-in expiry. When: April-May 2027.', '2. The market pays a scarcity multiple.')
bullet('If the parent cuts the royalty, moves more export programmes to India or allows sales outside South Asia, earnings would grow faster than sales. What would tell us: any change to the licence or service agreement at renewal. When: before 31-Dec each year.', '3. The parent shares more.')
bullet('A US tariff on Indian wind parts or a GE cut would remove up to 12% of sales; an off-highway downturn would hit the newest programmes first. The bear case gives Rs.589. What would tell us: wind sales below Rs.150 crore a quarter. When: any quarter.', '4. The bear case arrives.')

# ------------------------------------------------------------------ 11
head('Questions to discuss')
for qq in ['What margin does BTL earn on sales to group companies versus outside customers, and who sets the transfer price?',
           'Why do group companies take about 130-150 days to pay when outside customers take about 84? Is there an interest charge?',
           'Which products carry the 6% royalty, and has the list or the rate changed since 2021? What would the royalty be if the list widened?',
           'Will the parent let BTL sell directly outside South Asia (licence clause 7.2), or will exports stay with group sales companies?',
           'What exactly did the income-tax officers disallow in the BSPA service charges, and is the 2024-26 charge structured differently?',
           'How much of 2027 wind sales depends on GE, and what do the second-half schedules look like? What is the US tariff exposure?',
           'What is the order or programme pipeline in off-highway (John Deere and others) in rupees?',
           'How big is the heavy-duty plant (capex, capacity, revenue at full use) and who are the first customers?',
           'Why pay a Rs.110 crore interim dividend to the parent weeks before the IPO? What is the dividend policy now?',
           'When and how will the parent sell the next 2% to meet the 25% public-holding rule?',
           'How much of the 2026 margin came from the rupee and from price ahead of cost, in rupees?']:
    para('- ' + qq, space_after=2)

# ------------------------------------------------------------------ bottom line
head('Bottom line')
para(f'BTL is a well-run, cash-rich, high-return business that leads all three of its Indian markets, and the first quarter as a listed company was its best ever. But it is a licensee, not an owner: the Italian parent owns the designs, decides where BTL may sell, takes 6.8% of sales in royalty and fees, and has already taken Rs.2,534 crore for 23% of the shares at 87 times its cost. At Rs.{CMP:,.0f} the price already pays for about {CHANCE:.0%} of management\'s plan; our most likely case is worth Rs.{n0(TP)} and even full delivery of guidance is worth Rs.{n0(TPU)}. {RATING}, borderline - a good company at a full price, with the upside depending on the parent being generous.')
para('This note is for internal discussion and does not constitute investment advice.', 8, italic=True)

out = os.path.join(CO, 'Bonfiglioli_Transmissions_Note_v1.docx')
doc.save(out)
print('saved', out)
