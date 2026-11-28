"""Final check 28-Nov-2026: run-level fixes to Qualiance_International_Note_v3.docx (formatting kept).
Usage: fc_fix_note.py <note.docx>"""
import docx, sys
F = sys.argv[1]
d = docx.Document(F); P = d.paragraphs; T = d.tables
log = []
def set_cell(t, r, c, old, new):
    cell = T[t].rows[r].cells[c]
    runs = [ru for p in cell.paragraphs for ru in p.runs]
    assert cell.text.strip() == old, (t, r, c, cell.text)
    runs[0].text = new
    for ru in runs[1:]: ru.text = ''
    log.append(f'T{t} r{r} c{c}: {old} -> {new}')
def replace_para(i, old_start, new_text):
    p = P[i]; assert p.text.startswith(old_start), (i, p.text[:60])
    runs = p.runs; runs[-1].text = new_text if len(runs) == 1 else new_text
    log.append(f'P{i} rewritten')
def append_para(i, must_end, extra):
    p = P[i]; assert p.text.endswith(must_end), (i, p.text[-60:])
    p.runs[-1].text = p.runs[-1].text + extra
    log.append(f'P{i} + "{extra.strip()}"')
# numbers
assert T[0].rows[6].cells[0].text.startswith('Depreciation and interest')
set_cell(0, 6, 1, '123', '124')
assert T[11].rows[8].cells[0].text.startswith('Old plant labour per piece FY28E')
set_cell(11, 8, 2, '435', '420'); set_cell(11, 8, 3, '435', '420')
nd = [i for i, r in enumerate(T[12].rows) if r.cells[0].text.startswith('Net debt')][0]
set_cell(12, nd, 4, '11.2', '11.3')
set_cell(16, 1, 3, '-23%', '-24%'); set_cell(16, 2, 3, '-18%', '-19%'); set_cell(16, 3, 3, '-10%', '-9%')
# headcount: 255 is the RHP's own June-2026 payroll figure excluding management
replace_para(32, 'People. The company had 283 employees',
    'People. The company had 283 employees in March 2026 including management; the RHP and the latest presentation give 255 payroll staff '
    'excluding management (June 2026), and management spoke of about 340 workers. The RHP adds that contract labour is used for stitching '
    'and finishing (RHP p.114). Staff turnover was 64% in FY24, 30% in FY25 and 32% in FY26. Hiring and training several hundred tailors '
    'for the new plant is a real task.')
replace_para(122, 'What is the true headcount',
    'What is the true headcount (283 at March 2026 including management, 255 payroll staff excluding management at June 2026, about 340 in '
    'the meeting), how many are contract workers, and how will the company hire and keep about 1,000 tailors with 30%+ turnover?')
# red flags: document and printed page
append_para(30, 'win premium brand orders.', ' (RHP p.72)')
append_para(70, 'Companies Act.', ' Source: RHP p.182 (loans note) and p.189 (related parties); 1HFY27 results filing (cash flow).')
append_para(71, 'at the CMP.', ' Source: RHP p.61-62 and cash flow note p.158.')
append_para(72, 'pre-tax profit.', ' Source: RHP related-party note p.189-190.')
append_para(73, 'at the same price.', ' Source: RHP p.63, p.65-66 and p.83.')
append_para(74, 'fees.', ' Source: 1HFY27 results filing (cash flow); Prospectus p.69 (estimate).')
append_para(75, 'after Mehta Doshi.', ' Source: RHP p.156 and p.166 (restatement reconciliation), p.56 and p.151 (auditors).')
d.save(F)
print('\n'.join(log))
