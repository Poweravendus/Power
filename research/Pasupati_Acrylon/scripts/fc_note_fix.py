"""Final check 28-Nov-2026: run-level fixes to Pasupati_Acrylon_Note_v1.docx (keeps formatting).
Each edit replaces an exact substring inside one run; it fails loudly if the text is not found exactly once.
Usage: python3 fc_note_fix.py <note.docx>"""
import sys, docx
fn = sys.argv[1]
d = docx.Document(fn)

def runs_all():
    for p in d.paragraphs: yield from p.runs
    for t in d.tables:
        for row in t.rows:
            for c in row.cells:
                for p in c.paragraphs: yield from p.runs
    for s in d.sections:
        for p in s.header.paragraphs + s.footer.paragraphs: yield from p.runs

def rep(old, new, count=1):
    exact = old.startswith('=')
    if exact: old = old[1:]
    hits = [r for r in {id(r._r): r for r in runs_all()}.values() if (r.text == old if exact else old in r.text)]
    if len(hits) != count:
        raise SystemExit(f'expected {count} run(s) with {old!r}, found {len(hits)}')
    for r in hits: r.text = r.text.replace(old, new)

E = [
 # header / snapshot units
 ('Mcap Rs.606cr', 'Mcap Rs.606 crore', 1),
 ('=Rs.606 cr', 'Rs.606 crore', 1),
 ('=Rs.43 cr', 'Rs.43 crore', 1),
 ('=52-week range', '52-week range (closes)', 1),
 ('Rs.182.6 cr (CARE', 'Rs.182.6 crore (CARE', 1),
 ('~Rs.75 cr in FY27', '~Rs.75 crore in FY27', 1),
 ('already Rs.66 cr:', 'already Rs.66 crore:', 1),
 ('EBITDA (Rs. cr)', 'EBITDA (Rs. crore)', 1),
 ('Revenue (Rs. cr)', 'Revenue (Rs. crore)', 1),
 # rounding: Q2FY26 EBITDA 27.15 (model shows 27.2)
 ('=27.1', '27.2', 1),
 # jargon explained once
 ('the company makes no BOPP film.', 'the company makes no BOPP (biaxially oriented) film.', 1),
 ('Mills pay in 15-30 days; the ACN', 'Mills pay in advance or through letters of credit that the company discounts (CARE Jun-2026 p.3); the ACN', 1),
 ('it earned Rs.17 of EBITDA per kg. The 10-year average profit is Rs.14.2 per kg (PBIT).',
  'it earned Rs.17 of EBITDA (operating profit before depreciation, interest and tax) per kg. The 10-year average profit is Rs.14.2 per kg (PBIT: segment profit before interest and tax, as the company reports it).', 1),
 ('Rs.57.6 crore, a 18.3% margin', 'Rs.57.6 crore, an 18.3% margin', 1),
 ('CFO/EBITDA has averaged about 60% over ten years.',
  'Cash from operations (CFO) was negative Rs.35 crore in H1FY27 (Res Q2FY27 p.5); over ten years CFO has been about 60% of EBITDA.', 1),
 ('(including the CWIP transfer)', '(including the transfer from capital work in progress, CWIP)', 1),
 # anti-dumping wording matched to the source
 ('the anti-dumping duty recommended by DGTR in August 2025 was never notified by the Finance Ministry, according to Indian Acrylics\' own FY26 annual report.',
  'the anti-dumping duty recommended by DGTR (the commerce ministry\'s trade-remedies arm) in August 2025 had still not been notified by the Finance Ministry when Indian Acrylics published its FY26 annual report in September 2026 (PDF p.13, 21).', 1),
 # promoter history (Vineet Jain born 1969, on the board since 1994)
 ('The company was promoted in 1982 by Vineet Jain (now Managing Director, BBA London) and his family companies;',
  'The company was set up in 1982 (commercial production from 1990) and is promoted by Vineet Jain (Managing Director, BBA London, on the board since 1994) and his family companies (CARE Jun-2026 p.2; postal ballot notice p.15);', 1),
 ('paid Rs.15 crore of "recompense" to its banks to exit it in FY18-FY19.', 'paid Rs.15 crore of "recompense" to its banks in FY19 to exit it (provided for by FY18).', 1),
 ('on Rs.75-100 crore of assets)', 'on Rs.50-100 crore of assets)', 1),
 # floor description matched to the model
 ('fibre and film at FY26 volumes and their mid-cycle profit per kg (about Rs.15 and Rs.12.5), ethanol only for the quantity already allocated (nothing assumed after October 2027).',
  'fibre and film at FY26 volumes and close to mid-cycle profit per kg (FY28E EBITDA about Rs.16.4 per kg for fibre and Rs.11.3 for film), ethanol only for the seven months of the ESY27 allocation that fall in FY28E (the model repeats that volume in FY29E-FY30E).', 1),
 ('Checks. EV/EBITDA: at the CMP', 'Checks. EV/EBITDA (market value plus net debt, divided by EBITDA): at the CMP', 1),
 ('a CBIC duty notification.', 'a CBIC (customs) duty notification.', 1),
 ('ESY 2027-28 allocation (around November 2027)', 'ESY 2027-28 (ethanol supply year, November-October) allocation, around November 2027', 1),
 ('while the MD\'s commission rose 90% in FY26?', 'while the MD\'s pay rose 90% in FY26 (commission Rs.1.30 crore to Rs.3.55 crore; AR FY25 p.41, AR FY26 p.36)?', 1),
 ('The August 2025 DGTR recommendation for anti-dumping duty was not notified (Indian Acrylics AR FY26).',
  'The August 2025 DGTR recommendation for anti-dumping duty was not notified (Indian Acrylics AR FY26 PDF p.13, 21).', 1),
]
for o, n, c in E: rep(o, n, c)

# red flags: every flag with document and page (facts re-verified against the pack on 28-Nov-2026)
RF = ('Red flags (checked against the page images): '
      '(a) MD pay of Rs.4.76 crore in FY26, up 90%, mostly commission (AR FY26 p.26, p.36), a postal ballot to allow more than Rs.5 crore a year '
      '(postal ballot notice 26-Nov-2026 p.2-3) and no dividend (AR FY26 p.9); '
      '(b) fibre PBIT margin of 18.3% in H1FY27 against a 10-year average of 8.9%, with no explanation (Res Q2FY27 p.3); '
      '(c) inventory up from Rs.103 crore to Rs.195 crore between March and September 2026 (Res Q2FY27 p.4), so H1FY27 CFO was negative Rs.35 crore (p.5); '
      '(d) distillery sales of Rs.133 crore in H1FY27 against Rs.171 crore a year earlier despite consents for 180 KLPD (Res Q2FY27 p.3; AR FY26 p.11); '
      '(e) the anti-dumping duty recommended in August 2025 not notified (Indian Acrylics AR FY26 PDF p.13, 21); '
      '(f) the distillery stands on 20 acres leased from promoter companies (AR FY26 p.19-20) and mortgaged to the lender (p.69); '
      '(g) a printing error in the FY26 accounts (FY25 sales by geography add up to Rs.10 crore more than revenue, AR FY26 p.81). '
      'Quirks, not flags: fibre capacity shown as 45,000 tonnes in the FY23 report and 42,000 elsewhere; FY19 output (43,462 t) above rated capacity; no investor calls or presentations at all.')
p = [p for p in d.paragraphs if p.text.startswith('Red flags (checked against the page images)')]
assert len(p) == 1 and len(p[0].runs) == 1
p[0].runs[0].text = RF
d.save(fn)
print('applied', len(E) + 1, 'edits')

# Second pass: scripts/fc_note_trim.py (layout trims) and one table cell "FY26 Rs.1,010 cr" -> "crore" (T16).
