"""Build Qualiance_International_Note_v3.docx from v2 by editing text and tables (24-Nov-2026)."""
import copy, docx

SRC = '/home/user/Power/research/Qualiance_International/Qualiance_International_Note_v2.docx'
OUT = '/home/user/Power/research/Qualiance_International/Qualiance_International_Note_v3.docx'
doc = docx.Document(SRC)


def P(start):
    hits = [p for p in doc.paragraphs if p.text.strip().startswith(start)]
    assert len(hits) == 1, (start, len(hits))
    return hits[0]


def set_runs(p, parts):
    """parts: list of (text, bold or None). Reuses the first run's formatting."""
    runs = p.runs
    proto = runs[0]._r
    for r in runs:
        r._r.getparent().remove(r._r)
    for text, bold in parts:
        nr = copy.deepcopy(proto)
        p._p.append(nr)
        run = docx.text.run.Run(nr, p)
        run.text = text
        run.bold = bold


def set_text(p, text):
    b = p.runs[0].bold
    set_runs(p, [(text, b)])


def table_after(p):
    el = p._p.getnext()
    while el is not None and not el.tag.endswith('}tbl'):
        el = el.getnext()
    return docx.table.Table(el, p._parent)


def table_before(p):
    el = p._p.getprevious()
    while el is not None and not el.tag.endswith('}tbl'):
        el = el.getprevious()
    return docx.table.Table(el, p._parent)


def set_cell(cell, text):
    par = cell.paragraphs[0]
    if par.runs:
        set_text(par, text)
    else:
        par.add_run(text)


def fill_table(t, rows):
    tr = t._tbl.tr_lst
    while len(t._tbl.tr_lst) < len(rows):
        t._tbl.append(copy.deepcopy(t._tbl.tr_lst[-1]))
    while len(t._tbl.tr_lst) > len(rows):
        t._tbl.remove(t._tbl.tr_lst[-1])
    for r, vals in zip(t.rows, rows):
        assert len(vals) == len(r.cells), (vals, len(r.cells))
        for c, v in zip(r.cells, vals):
            set_cell(c, v)


def clone_par(proto, text, bold=None):
    np_ = copy.deepcopy(proto._p)
    par = docx.text.paragraph.Paragraph(np_, proto._parent)
    set_runs(par, [(text, bold if bold is not None else proto.runs[0].bold)])
    return par


def clone_table(proto_tbl, rows):
    nt = copy.deepcopy(proto_tbl._tbl)
    t = docx.table.Table(nt, proto_tbl._parent)
    fill_table(t, rows)
    return t


# ---------------- title block ----------------
set_text(P('Qualiance International Ltd -'), 'Qualiance International Ltd - Swiss Army jackets from Tiruppur, and a big new factory that must win brand work at much lower prices')
set_text(P('NSE SME: QUALIANCE'), 'NSE SME: QUALIANCE  |  CMP: Rs.137.10  |  Market cap: Rs.184cr  |  Rating: SELL  |  Target price: Rs.94  |  Upside: -31%  |  Analyst: Dheeraj Kripalani')
set_text(P('November 2026  |  Version 2'), 'November 2026  |  Version 3 (24-Nov-2026): management meeting and price-per-piece / per-machine benchmarks added; the new factory is now priced as private-label work; rating moves from HOLD back to SELL  |  CMP as of 8-Nov-2026 (NSE close), to be replaced with Bloomberg')

p = P('The buyer sends a design')
set_text(p, p.text.replace('(40% imported)', '(40% imported per the RHP; management now says about 80%)'))
p = P('Supply chain. Technical fabrics')
set_text(p, p.text.replace('40% of materials are imported', 'the RHP put imports at 40% of materials, while management told us about 80%, mostly paid in cash with 8-9 days of supplier credit'))

# capacity table: blended price row
t = table_before(P('Source: RHP (capacity and production certified'))
last = t.rows[-1]
vals = ['Price per piece, Rs. (blended: old plant Rs.1,975, new plant Rs.1,100)', '1,241', '1,502', '1,936', '1,975', '1,640', '1,485', '1,409']
for c, v in zip(last.cells, vals):
    set_cell(c, v)
set_text(P('Source: RHP (capacity and production certified'), 'Source: RHP (capacity and production certified by a chartered engineer); estimates are the base case in the model. The new unit starts in July 2027 in the base case, so FY28E is a part year. The blended price falls because the new plant sells cheaper brand garments.')
p = P('Management says the first-half FY27 average')
set_text(p, 'Management says the first-half FY27 average was above Rs.2,500 on complicated styles, while sales fell 19%. Its own peak guidance for the new plant implies about Rs.1,960 a piece. The base case holds Rs.1,975 for the old plant only; the new plant is priced separately (next section).')

# ---------------- new sections before "The IPO money" ----------------
anchor = P('The IPO money: what was promised')
head_proto = P('Can they deliver')
body_proto = P('Capacity. The Tiruppur plant')
src_proto = P('Source: RHP (country split')
tbl5 = table_after(P('Who buys and how much'))          # 5-column table proto
tbl3 = table_after(anchor)                                # 3-column table proto
tbl4 = table_after(P('What moves the base target most'))  # 5-column proto (sens)

new_els = []
new_els.append(clone_par(head_proto, 'What the management meeting added (November 2026)'))
for txt in [
    'Who buys. About 60% of sales go to Swiss government bodies (Armasuisse, customs, SBB railways and cantons), 20% to one US buyer of UV-protective (UPF 50) clothing and 20% to smaller Swiss and UK buyers.',
    'How big Switzerland is. Swiss institutions buy about Rs.40-60 crore a year from Qualiance, Rs.50 crore in a typical year. FY26 was Rs.61.5 crore, the top of that range. Management calls this business mature and estimates its share of a ~Rs.200 crore market at 25-30% (its own number).',
    'How tenders work. Bids are scored about 60% on technical merit and 40% on price. Several approved suppliers then share each year\'s orders through further quotes, so a long award does not fix annual volume. Some awards run to 2032; a group comes up for re-tender around 2028.',
    'What is pending. Five SBB railway tenders worth about Rs.10 crore were submitted, with decisions expected in January-February 2027. These are bids, not awards.',
    'What the new factory is for. Large private-label performance-wear programmes. Agilitas and Skechers have given trial business after seeing the plans; there are no signed annual volumes. About 600 machines and 1,000 workers will be added to about 340 workers today; building done around March 2027, commercial output from July 2027, capex about Rs.40 crore.',
    'Cash. Inputs are bought mostly for cash and suppliers give 8-9 days. Swiss programmes buy European fabric in bulk for deliveries spread over up to nine months, which is why stock is high. Brand orders run on about 90-day seasons and should need less stock.',
    'The numbers floated. Broker roadshow estimates of FY28 sales Rs.131 crore and profit Rs.24 crore, and FY29 Rs.202 crore and Rs.40 crore, were discussed, but no customer-wise order bridge was given. They match our bull case, not our base.',
]:
    new_els.append(clone_par(body_proto, txt, None))
new_els.append(clone_par(head_proto, 'Price per piece and per machine: what the new factory can earn'))
new_els.append(clone_par(body_proto, 'We compare Qualiance with listed garment makers on two yardsticks: revenue per garment and revenue per sewing machine.'))
new_els.append(clone_table(tbl5, [
    ['Company (year)', 'Rs. per piece', 'Rs. lakh per machine', 'Pieces per machine', 'What it makes'],
    ['S P Apparels (FY25)', '134', '17.3', '12,800', 'Knitted basics, exports'],
    ['S P / Young Brand (FY25)', 'n.a.', '23.2', 'n.a.', 'Innerwear'],
    ['Maral Overseas (FY26)', 'n.a.', '9.8', 'n.a.', 'Knitted garments'],
    ['KPR Mill garments (FY26)', '175', 'n.a.', 'n.a.', 'Knitted basics'],
    ['Pearl Global (FY26)', '643', 'n.a.', 'n.a.', 'Brand private label'],
    ['Gokaldas, India (FY26)', '765', 'n.a.', 'n.a.', 'Brand private label'],
    ['Banswara garments (FY26)', '831', 'n.a.', 'n.a.', 'Woven garments'],
    ['Qualiance (FY24)', '1,240', '15.4', '1,240', 'Swiss technical'],
    ['Qualiance (FY26)', '1,936', '31.8', '1,640', 'Swiss technical'],
]))
new_els.append(clone_par(src_proto, 'Source: company annual reports and presentations (investor\'s table, November 2026); Qualiance pieces from the RHP. Qualiance\'s 240 machines are an analyst count posted on X, not a company figure; the RHP gives 283 employees and management says about 340 workers.'))
for txt in [
    'Is the high price real? Mostly yes. Value added per piece (price less materials) rose from about Rs.715 to Rs.1,098 between FY24 and FY26, as fast as the price. That is a real shift to Swiss technical garments, not costs passed through. Each machine also made about 30% more pieces, if the machine count is right.',
    'But it is not a factory edge. Qualiance makes about 1,600 garments per machine a year; S P Apparels makes about 12,800 basic knits. Qualiance earns more per machine because each jacket is complex and certified, not because its sewing floor is more efficient. And FY26 may be the peak mix: Swiss sales were above what management calls a typical year.',
    'What it means for the new factory. Management\'s Rs.180 crore peak needs about Rs.1,960 a piece, or about Rs.35 lakh a machine. That is more than today\'s Swiss work and 1.5 to 3.5 times what listed peers earn per machine. Yet the new factory is meant for private-label performance wear, which listed peers sell at Rs.640-830 a piece.',
]:
    new_els.append(clone_par(body_proto, txt, None))
new_els.append(clone_table(tbl5, [
    ['New factory at full use', 'Rs. per piece', 'Revenue, Rs. crore', 'Rs. lakh per machine', 'vs Qualiance FY26 per machine'],
    ['Bear: listed peer price', '800', '86', '14.4', '-55%'],
    ['Base: performance outerwear', '1,100', '119', '19.8', '-38%'],
    ['Management (bull)', '1,960', '212', '35.3', '+11%'],
]))
new_els.append(clone_par(src_proto, '10.8 lakh pieces at full use and 600 machines (RHP objects; presentation 1HFY27). Model sheet Unit_Economics.'))
new_els.append(clone_par(body_proto, 'Our base takes Rs.1,100 a piece: above commodity peers, because performance outerwear is harder to make, but far below Swiss military jackets. At full use that is about Rs.20 lakh a machine, between S P Apparels and its innerwear unit. We also cost the new work like brand work: materials 54% and labour 22% of sales, against about 43% and 23% today.'))
for el in new_els:
    anchor._p.addprevious(el._p if hasattr(el, '_p') else el._tbl)

# ---------------- estimates ----------------
set_text(P('What "base" means now.'), 'What "base" means now. Since 11 November the base case is our most likely outcome, and the old "committed only" case is kept as the floor. In this version the new factory is priced and costed as private-label performance wear, because that is what management told us it is for. The floor is re-based the same way.')
set_text(P('It has done that before.'), 'It has done that before. Revenue grew 29% a year from FY23 to FY26 while Indian textile and garment exports were flat. But that growth came from a Swiss re-equipment wave at high prices. The new factory adds volume at much lower prices, so in rupees the base grows 19% a year to FY30E, against 37% in management\'s plan.')
set_text(P('We set the base about 40%'), 'We keep the new plant\'s fill at 22% / 45% / 65% (management: 30-35% / 60% / 90%). The bigger difference is price: Rs.1,100 a piece against Rs.1,960. With both, the base sits about a quarter of the way from the floor to management\'s plan, below our usual 40%, because the price evidence from listed peers is clear and no brand volume is signed.')
t = table_after(P('Industry growth used for the base'))
fill_table(t, [
    ['Segment', 'Market growth', 'Source', 'Our base', 'Management guidance'],
    ['Existing plant: Swiss government and current buyers', 'About 0%: Swiss wave ending; garment exports -1.4% FY26', 'CITI and GTRI export data; meeting', 'Rs.73 crore FY27E, about Rs.76 crore a year after', 'Rs.76-77 crore FY27; Swiss "mature"'],
    ['New plant: private-label performance wear', '4.1% global apparel; peers sell at Rs.640-830 a piece', 'RHP industry overview; peer annual reports', '22 / 45 / 65% full at Rs.1,100: Rs.26 / 53 / 77 crore', '30-35 / 60 / 90% full at ~Rs.1,960; Rs.180 crore peak'],
    ['Whole company, revenue FY26-30', 'About 0%', 'RHP; export data', '19% a year to Rs.154 crore', '37% a year to Rs.269 crore'],
    ['EBITDA margin', 'Company record: 13% FY24 to 22% FY26, 17% 1HFY27', 'RHP; 1HFY27 results', '19.4% FY27E, then about 16-17% as brand work grows', '21.7%, "same as FY26"'],
])
t = table_before(P('Guidance implied: Rs.76.5 crore'))
fill_table(t, [
    ['Rs. crore', 'FY27E', 'FY28E', 'FY29E', 'FY30E'],
    ['Revenue: floor (re-based)', '71.7', '87.8', '103.4', '121.4'],
    ['Revenue: base', '73.5', '102.5', '130.0', '154.0'],
    ['Revenue: management guidance', '76.5', '145.8', '204.5', '268.5'],
    ['Revenue: bull', '77.2', '149.4', '215.8', '272.0'],
    ['EBITDA margin: base / bull', '19.4% / 22.4%', '16.8% / 22.0%', '16.1% / 22.3%', '16.2% / 23.0%'],
    ['Profit after tax: floor / base / bull', '9.1 / 9.5 / 12.5', '8.0 / 10.5 / 24.0', '8.2 / 12.5 / 35.3', '10.5 / 15.7 / 47.2'],
])
set_text(P('Guidance implied: Rs.76.5 crore'), 'Guidance implied: Rs.76.5 crore from the old plant plus the new plant at management\'s 32.5% / 60% / 90% fill and Rs.1,960 a piece (its Rs.180 crore peak). The bull now uses that price for the new plant, so it sits close to guidance; it is a little higher because the old plant runs at 88% and its price rises 3% a year.')
t = table_after(P('Key drivers'))
fill_table(t, [
    ['Key driver', 'Bear', 'Floor', 'Base', 'Bull', 'Why the base looks like this'],
    ['Existing plant utilisation FY27E / FY28E', '75 / 70%', '80 / 82%', '82 / 85%', '82 / 88%', 'Rs.6 crore of goods held for inspection; plant near full'],
    ['New plant starts', 'Jan 2028', 'Jul 2027', 'Jul 2027', 'Jul 2027', 'Latest company date (meeting and presentation)'],
    ['New plant fill FY28E / FY29E / FY30E', '3/15/25%', '12/25/40%', '22/45/65%', '30/60/85%', 'Share gain, but no brand volume signed'],
    ['Old plant price per piece FY28E, Rs.', '1,850', '1,975', '1,975', '2,140', 'FY26 Rs.1,936; Swiss mix'],
    ['New plant price per piece, Rs.', '800', '1,100', '1,100', '1,960', 'Brand work; peers Rs.640-830'],
    ['Old plant material cost, % of sales', '49%', '46%', '46%', '45%', 'FY26 43%, 1HFY27 49%'],
    ['New plant materials / labour, % of sales', '56 / 25%', '54 / 22%', '54 / 22%', '46 / 24%', 'Brand work, Far East inputs'],
    ['Old plant labour per piece FY28E, Rs.', '420', '435', '435', '470', 'Wage inflation'],
    ['Currency gain, % of exports', '0%', '1%', '1%', '2.5%', 'FY26 4.3%; unhedged'],
    ['Inventory / receivable days', '140 / 80', '110 / 65', '110 / 65', '90 / 60', 'FY26 115 / 76'],
])
t = table_after(P('Key drivers'))
el = t._tbl.getnext()
while not el.tag.endswith('}tbl'):
    el = el.getnext()
t2 = docx.table.Table(el, t._parent)
fill_table(t2, [
    ['Base case, Rs. crore', 'FY26A', 'FY27E', 'FY28E', 'FY29E', 'FY30E'],
    ['Revenue', '76.9', '73.5', '102.5', '130.0', '154.0'],
    ['Growth', '45%', '(4%)', '40%', '27%', '18%'],
    ['EBITDA', '16.9', '14.2', '17.2', '20.9', '25.0'],
    ['EBITDA margin', '21.9%', '19.4%', '16.8%', '16.1%', '16.2%'],
    ['Other income', '4.1', '1.4', '1.8', '1.4', '1.6'],
    ['Profit after tax', '11.9', '9.5', '10.5', '12.5', '15.7'],
    ['EPS, Rs. (FY26 on 0.99 cr shares)', '11.99', '7.08', '7.84', '9.30', '11.67'],
    ['Cash from operations', '7.8', '17.7', '0.5', '3.9', '8.9'],
    ['Free cash flow', '6.3', '(15.8)', '(7.3)', '1.9', '6.9'],
    ['Net debt (negative = net cash)', '27.7', '2.3', '11.4', '11.2', '6.0'],
    ['Return on equity', '40%', '16%', '12%', '13%', '14%'],
])
set_text(P('From FY28E the new plant drives growth'), 'From FY28E the new plant drives growth: revenue rises 40% in FY28E and 27% in FY29E. But brand work earns less per piece and per rupee of sales, so the EBITDA margin slips to about 16-17%, and EPS only passes the FY26 level on post-IPO shares (Rs.8.82) in FY29E. Growth still ties up working capital.')
t = table_after(P('Three scenarios in FY28E'))
fill_table(t, [
    ['FY28E, Rs. crore', 'Bear', 'Floor (re-based)', 'Base', 'Bull'],
    ['Revenue', '61.4', '87.8', '102.5', '149.4'],
    ['EBITDA', '6.7', '13.9', '17.2', '32.9'],
    ['EBITDA margin', '10.9%', '15.8%', '16.8%', '22.0%'],
    ['Profit after tax', '2.7', '8.0', '10.5', '24.0'],
    ['EPS, Rs.', '2.03', '5.93', '7.84', '17.83'],
])
t = table_after(P('What the price is paying for'))
for r in t.rows:
    if r.cells[0].text.startswith('P/E on base FY27E'):
        set_cell(r.cells[1], '19.4x / 17.5x')
p = P('The multiple. We start from the lower peer')
set_text(p, p.text + ' At the peer\'s full 23.2x the base would be worth about Rs.182, so the multiple matters as much as the factory; peer multiples are still to be checked on Bloomberg.')
set_text(P('Reverse check. At 12x'), 'Reverse check. At 12x, today\'s price needs FY28E profit of Rs.15.4 crore (EPS Rs.11.43). The base case has Rs.10.5 crore, the floor Rs.8.0 crore and management\'s plan Rs.24.0 crore. The market is pricing about a third of the way from our base to management\'s plan.')
t = table_before(P('Rating on the base target: BUY above'))
fill_table(t, [
    ['Scenario', 'FY28E EPS, Rs.', 'Target at 12x, Rs.', 'Upside', 'EV/EBITDA cross-check, Rs.', 'Rating'],
    ['Bear', '2.03', '24', '-82%', '31', 'SELL'],
    ['Floor (re-based, memo)', '5.93', '71', '-48%', 'n.a.', 'SELL'],
    ['Base', '7.84', '94', '-31%', '88', 'SELL'],
    ['Bull (management plan)', '17.83', '214', '+56%', '172', 'BUY'],
])
p = P('Rating on the base target: BUY above')
set_text(p, p.text.replace('about Rs.66 a share', 'about Rs.62 a share'))
set_text(P('The base case roughly justifies the price'), 'The base case does not justify the price. Target Rs.94, 31% below the CMP, so the rating goes back to SELL. It was HOLD at Rs.142 in version 2, when the new factory was priced like Swiss garments; that is the single change. The SELL is clear: HOLD would need the price below Rs.99, or the new factory to earn close to management\'s price and margin.')
set_text(P("Chance of management's plan already in the price"), "Chance of management's plan already in the price: about 36%. This is (price minus base target) divided by (bull target minus base target). At 0% the price pays only for our base; at 100% it pays for management's whole plan.")
t = table_after(P('What moves the base target most'))
fill_table(t, [
    ['Change to the base case', 'FY28E EPS, Rs.', 'Target, Rs.', 'Upside', 'Rating'],
    ['New plant price Rs.1,400 a piece', '8.72', '105', '-23%', 'SELL'],
    ['New plant price Rs.1,600 a piece', '9.31', '112', '-18%', 'SELL'],
    ['Management price Rs.1,960, brand-work costs', '10.37', '124', '-10%', 'SELL'],
    ['Management fill 32.5 / 60 / 90% at Rs.1,100', '9.38', '113', '-18%', 'SELL'],
    ['Base at the peer P/E of 23.2x', '7.84', '182', '+33%', 'BUY'],
])
set_text(P('How fast the new plant fills is the whole question'), 'Two things decide the value: what the new factory earns per piece and the multiple. Even at management\'s price per piece, with brand-work costs, the target is Rs.124, still below the price. Only management\'s full plan (price, fill and FY26 margins) or a full peer multiple takes the value above Rs.137.')
p = P('2. The new plant fills at a different pace')
set_runs(p, [('2. The new plant earns more than we assume. ', True), ('How we would lose: brands place technical outerwear at Swiss-like prices, or Swiss railway and customs work moves into the new plant. At management\'s price and margins the stock is worth about Rs.214. What would tell us: the first brand purchase orders with volumes and prices, and the SBB tender results in January-February 2027. When: 4QFY27 to 2QFY28.', None)])

# questions: replace three, add three
set_text(P('Who are the first customers for the new plant'), 'What volumes and prices per piece have Agilitas and Skechers indicated for FY28, for which garments, and is any Swiss work planned for the new plant?')
set_text(P('Why did the plant move from a concrete building'), 'How many sewing machines run in Tiruppur today, how many garments does each make a year, and how many minutes does a typical brand garment take against a Swiss jacket?')
set_text(P('What is the true headcount'), 'What is the true headcount (283 in the RHP, 255 in the presentation, about 340 in the meeting), and how will the company hire and keep about 1,000 tailors with 30%+ turnover?')
q_last = P('Who valued the land and buildings')
for txt in ['Which Swiss awards, by value, come up for re-tender around 2028, and what share of each year\'s orders did Qualiance win in the last quotation rounds?',
            'Imports: the RHP says about 40% of materials, the meeting about 80%. Which is right for FY26, and what does it mean for cash and currency risk?']:
    q_last._p.addnext(clone_par(q_last, txt, None)._p)
    q_last = P(txt[:40])

set_text(P('Qualiance is a real, specialised business'), 'Qualiance is a real, specialised business with a rare customer: the Swiss Army trusts it, and that took twenty years. But the Swiss business is mature and FY26 was a high year, so growth must come from the new factory, and that factory is for brand work that listed peers sell at a third of Qualiance\'s price per piece. Priced that way, the base case is worth Rs.94, 31% below the price: SELL. Management\'s plan is worth Rs.214 and the price already pays for about a third of it. The first brand orders (volume and price per piece) and the January-February 2027 SBB tender results will tell us which way it goes; peer multiples from Bloomberg could also change the answer.')
doc.save(OUT)
print('written', OUT)
