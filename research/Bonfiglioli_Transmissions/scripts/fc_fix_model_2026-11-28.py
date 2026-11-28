"""Final check 28-Nov-2026: text-only fixes to BONFIG_Model_v2.xlsx (no driver, multiple or formula changes)."""
import openpyxl, sys
fn = sys.argv[1]
wb = openpyxl.load_workbook(fn)
v, ue, q, gt, d = wb['Valuations'], wb['Unit_Economics'], wb['Quarterly'], wb['Group_vs_ThirdParty'], wb['Drivers']
log = []
def sub(ws, ref, old, new):
    s = ws[ref].value
    assert isinstance(s, str) and old in s, (ws.title, ref, old)
    ws[ref].value = s.replace(old, new); log.append(f'{ws.title}!{ref}: "{old}" -> "{new}"')
sub(v, 'A1', 'the same 12-month window that "FY28E" covers for March-year companies in our other notes',
    'the 12-month window closest to "FY28E" (Apr-2027 to Mar-2028; 9 of 12 months overlap) used for March-year companies in our other notes')
sub(ue, 'H27', 'Guidance volumes need ~95-100% of FY25 machine hours by FY28',
    'Guidance (bull) volumes need ~107% of FY25 machine hours by FY28 (base ~97%; D27, C27)')
sub(q, 'A1', 'Quarterly and half-year results, Rs. crore (',
    'Quarterly and half-year results, Rs. crore. Quarter labels follow the calendar fiscal year: Q3FY26 = Jul-Sep 2026, which the company calls Q3CY26 (', )
sub(gt, 'G51', 'Call p.13', 'Call p.14')
if 'Call p.13' in str(d['H54'].value) and '4.4' in str(d['H54'].value):
    sub(d, 'H54', 'Call p.13', 'Call p.14')
wb.save(fn)
print('\n'.join(log))
