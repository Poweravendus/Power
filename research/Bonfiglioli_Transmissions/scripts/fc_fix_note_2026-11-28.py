"""Final check 28-Nov-2026: run-level fixes to Bonfiglioli_Transmissions_Note_v1.docx (formatting kept).
Usage: python3 fc_fix_note_2026-11-28.py <note.docx>"""
import docx, sys, copy
from docx.oxml.ns import qn
fn = sys.argv[1]
d = docx.Document(fn)
log = []

def all_paragraphs(doc):
    for p in doc.paragraphs: yield p
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs: yield p
    for s in doc.sections:
        for p in s.header.paragraphs + s.footer.paragraphs: yield p
        for t in s.header.tables + s.footer.tables:
            for r in t.rows:
                for c in r.cells:
                    for p in c.paragraphs: yield p

def replace_in_par(p, old, new):
    full = ''.join(r.text for r in p.runs)
    i = full.find(old)
    if i < 0: return False
    j = i + len(old); pos = 0; first = True
    for r in p.runs:
        a, b = pos, pos + len(r.text); pos = b
        if b <= i or a >= j: continue
        s, e = max(i, a) - a, min(j, b) - a
        if first:
            r.text = r.text[:s] + new + r.text[e:]; first = False
        else:
            r.text = r.text[:s] + r.text[e:]
    return True

def rep(old, new, count=1, where=None):
    n = 0; seen = set(); keep = []
    for p in (where if where is not None else all_paragraphs(d)):
        if id(p._p) in seen: continue
        seen.add(id(p._p)); keep.append(p._p)
        while n < count and replace_in_par(p, old, new): n += 1
    assert n == count, f'expected {count} x "{old}", replaced {n}'
    log.append(f'"{old}" -> "{new}" ({n}x)')

def cell_set(table, row, col, value):
    c = table.rows[row].cells[col]; p = c.paragraphs[0]
    old = p.text
    keep = [r for r in p.runs if r.text] or p.runs   # write into the formatted (non-empty) run
    tgt = keep[0]
    for r in p.runs: r.text = ''
    tgt.text = value
    log.append(f'table cell r{row}c{col}: "{old}" -> "{value}"')

T = d.tables
# --- HIGH: peer table, Elecon and Shanthi values swapped in rows 1-4 (Pros p.119: Elecon 23,660.50 mn, 22.11%, ROCE 19.28%, FAT 3.90; Shanthi 5,187.20 mn, 20.03%, 24.85%, 4.19)
peer = [t for t in T if t.rows[0].cells[0].text.startswith('FY26 (Mar) / FY25 (Dec)')][0]
hdr = [c.text for c in peer.rows[0].cells]; ie, ish = hdr.index('Elecon'), hdr.index('Shanthi Gears')
for r, (el, sh) in zip(range(1, 5), [('2,366', '519'), ('22.1%', '20.0%'), ('19%', '25%'), ('3.9', '4.2')]):
    assert {peer.rows[r].cells[ie].text, peer.rows[r].cells[ish].text} == {el, sh}, r
    cell_set(peer, r, ie, el); cell_set(peer, r, ish, sh)

# --- MEDIUM
rep('Our check (Drivers sheet) shows the management plan would need about 90% of today\'s hours by FY28 without that expansion',
    'Our check shows the management plan would need about 107% of FY25 machine hours by FY28 without that expansion (Unit_Economics sheet), and about 91% even with the machine additions we assume (Drivers sheet)')
rep('most of it after the September-quarter results', 'about a third of it after the September-quarter results (Rs.722 on 12-Nov, Rs.795 on 13-Nov)')
rep("FY27E the year to Dec-2027", "FY27E the year to Dec-2027. Quarters follow the same calendar, so Q3 FY26 means July-September 2026, which the company calls Q3CY26")
rep('a licence that costs 6% of sales of licensed products (4.4% of all sales)',
    'a licence that costs 6% of net sales of licensed products, excluding sales to the parent itself (4.4% of all sales; Prospectus p.253)')
rep('Auditor: S.R. Batliboi (EY network).',
    'Auditor: S.R. Batliboi (EY network). In December 2025 BTL bought the gear-components business of a sister company, Bonfiglioli Drive Solutions (BDSPL), for Rs.21.4 crore under a business transfer agreement of 15-Dec-2025 (a slump sale: the whole business bought as a going concern for one price, set by a valuer). Because the parent controls both companies it was booked as a "business under common control": past accounts were restated as if the two had always been one (Prospectus p.252, note 46 p.341; results note 7).')

# --- LOW
rep('(clause 7.4)', '(licence clause 7.4, p.5)')
rep("before 31 December (clause 9.2)", "before 31 December (clause 9.2, licence p.6; Prospectus p.25, p.253)")
rep("abroad only to group companies with consent (clause 7.2)",
    "abroad only to group companies with consent (clause 7.2, licence p.5; the prospectus summary on p.253 says any other country with the parent's consent)")
pnl = [t for t in T if t.rows[0].cells[0].text == 'Rs. crore' and len(t.columns) == 8][0]
assert pnl.rows[5].cells[0].text == 'PAT'; cell_set(pnl, 5, 0, 'PAT (reported)')
rep('Source: Prospectus p.285-286 (restated, continuing operations);',
    'Source: Prospectus p.285-286 (restated; EPS on continuing operations, which exclude Rs.1.8 crore in FY23 and Rs.3.6 crore in FY24 from the IT/R&D unit sold to a group company in 2024);')
qt = [t for t in T if t.rows[0].cells[0].text == 'Rs. crore' and t.rows[0].cells[1].text == 'Q3 FY25'][0]
hq = [c.text for c in qt.rows[0].cells]; iq1 = hq.index('Q1 FY26')
assert qt.rows[4].cells[0].text == 'PAT' and qt.rows[4].cells[iq1].text == '73'; cell_set(qt, 4, iq1, '74')
rep('(64% to 71% of materials)', '(65% to 71% of materials, p.237)')
rep('9.9% India; ~5% global', '9.9% India; ~6% global')
rep('Materials, % of sales', 'Materials, % of core sales')
rep('FY27E EPS would be about 9% higher', 'FY27E EPS would be about 9.5% higher')
rep('weeks before the IPO', 'months before the IPO')
rep('Rolled forward to our FY27E year at about 9% a year',
    'Rolled forward to our FY27E year (January-December 2027, the next full year and the closest match to the April 2027-March 2028 "FY28E" we use for March year-end companies) at about 9% a year')
rep('call 13-Nov-2026 p.7, 10-13, 16', 'call 13-Nov-2026 p.7, 10-14, 16')
rep('Mcap Rs.15,101cr', 'Mcap Rs.15,101 crore')
tam = [t for t in T if t.rows[0].cells[0].text.startswith('India market')][0]
for ci, c in enumerate(tam.rows[0].cells):
    if c.text.endswith(', Rs. cr'): cell_set(tam, 0, ci, c.text + 'ore')
rep('Rs.10/45/90 cr FY28-30', 'Rs.10/45/90 crore FY28-30')
rep('Rs.100 / 150 cr', 'Rs.100 / 150 crore')
rep('Rs.70-80 cr spent', 'Rs.70-80 crore spent')

# --- layout: keep every table on one page (scenario table was cut across pages 5-6)
for t in T:
    for r in t.rows[:-1]:
        for c in r.cells:
            for p in c.paragraphs: p.paragraph_format.keep_with_next = True
    for r in t.rows:
        trPr = r._tr.get_or_add_trPr()
        if trPr.find(qn('w:cantSplit')) is None:
            trPr.append(trPr.makeelement(qn('w:cantSplit'), {}))
log.append('keep_with_next + cantSplit on all table rows')
d.save(fn)
print('\n'.join(log))
