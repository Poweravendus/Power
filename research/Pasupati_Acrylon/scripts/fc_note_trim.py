"""Final check 28-Nov-2026, second pass: shorten section 6 wording so its sources line does not spill onto an empty page."""
import sys, docx
fn = sys.argv[1]; d = docx.Document(fn)
E = [
 ("DGTR (the commerce ministry's trade-remedies arm) in August 2025 had still not been notified by the Finance Ministry when Indian Acrylics published its FY26 annual report in September 2026 (PDF p.13, 21).",
  "DGTR (the trade-remedies directorate) in August 2025 was still not notified by the Finance Ministry in September 2026 (Indian Acrylics AR FY26 PDF p.13, 21)."),
 (" (CARE Jun-2026 p.2; postal ballot notice p.15);", ";"),
 ("(a) MD pay of Rs.4.76 crore in FY26, up 90%, mostly commission (AR FY26 p.26, p.36), a postal ballot to allow more than Rs.5 crore a year (postal ballot notice 26-Nov-2026 p.2-3) and no dividend (AR FY26 p.9);",
  "(a) MD pay Rs.4.76 crore in FY26, up 90% (AR FY26 p.26, p.36), a postal ballot to allow over Rs.5 crore (notice 26-Nov-2026 p.3) and no dividend (AR FY26 p.9);"),
 ("Quirks, not flags: fibre capacity shown as 45,000 tonnes in the FY23 report and 42,000 elsewhere; FY19 output (43,462 t) above rated capacity; no investor calls or presentations at all.",
  "Quirks: capacity 45,000 t in the FY23 report vs 42,000 t elsewhere; FY19 output above capacity; no investor calls."),
 ("postal ballot notice 26-Nov-2026 p.2-14; SHP Mar-2026;", "postal ballot notice 26-Nov-2026 p.2-15; CARE Jun-2026 p.2; SHP Mar-2026;"),
]

E2 = [
 ("None of these causes is permanent.", "None is permanent."),
 ("(commercial production from 1990)", "(production from 1990)"),
 ("and is worth watching at renewal.", "(watch at renewal)."),
 ("On 26-Nov-2026 the board asked shareholders, by postal ballot closing 31-Dec-2026, to allow pay", "A postal ballot of 26-Nov-2026 (closing 31-Dec-2026) asks shareholders to allow pay"),
 ("Suresh Kumar Mittal & Co. (FY18-FY22): a normal rotation.", "Suresh Kumar Mittal & Co. (FY18-FY22): normal rotation."),
]
for o, n in (E2 if len(sys.argv) > 2 else E):
    hits = [p for p in d.paragraphs if o in p.text]
    assert len(hits) == 1, o
    rs = [r for r in hits[0].runs if o in r.text]; assert len(rs) == 1, o
    rs[0].text = rs[0].text.replace(o, n)
d.save(fn); print('trimmed', len(E))
