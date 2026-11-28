"""Final check 28-Nov-2026: add CHECK rows on the Quarterly sheet tying the four quarters of FY25 and FY26 to the annual
P&L / segment notes (columns G and K) and the half-years to the reported H1 figures (columns N and O; Res Q2FY27 p.2-3).
Usage: python3 fc_model_fix.py <model.xlsx>  (then recalc)"""
import sys, copy, openpyxl
fn = sys.argv[1]; wb = openpyxl.load_workbook(fn); q = wb['Quarterly']
assert q['A44'].value is None, 'rows already added'
src_lab, src_val = q['A28'], q['B28']
def style(c, s):
    c.font = copy.copy(s.font); c.number_format = s.number_format; c.alignment = copy.copy(s.alignment)
q['A44'] = 'Checks: four quarters vs annual (G = FY25, K = FY26) and half-years vs reported H1 (N = H1FY26, O = H1FY27; Res Q2FY27 p.2-3)'
q['A44'].font = copy.copy(q['A33'].font)
# (label, quarterly row, P&L/Segments ref for FY25, FY26, reported H1FY26, H1FY27)
rows = [
    ('CHECK: revenue', 3, "'P&L'!J5", "'P&L'!K5", 496.30, 513.00),
    ('CHECK: PAT', 18, "'P&L'!J27", "'P&L'!K27", 17.95, 59.40),
    ('CHECK: segment revenue - fibre', 21, 'Segments!J3', 'Segments!K3', 275.10, 314.37),
    ('CHECK: segment revenue - CPP film', 22, 'Segments!J4', 'Segments!K4', 49.89, 65.30),
    ('CHECK: segment revenue - ethanol', 23, 'Segments!J5', 'Segments!K5', 171.31, 133.33),
    ('CHECK: segment result - fibre', 25, 'Segments!J11', 'Segments!K11', 17.03, 57.57),
    ('CHECK: segment result - CPP film', 26, 'Segments!J12', 'Segments!K12', 1.33, 7.94),
    ('CHECK: segment result - ethanol', 27, 'Segments!J13', 'Segments!K13', 12.75, 17.56),
]
for i, (lab, r, a25, a26, h26, h27) in enumerate(rows):
    rr = 45 + i
    q[f'A{rr}'] = lab + ' (should be 0)'; style(q[f'A{rr}'], src_lab)
    q[f'G{rr}'] = f'=ROUND(SUM(D{r}:G{r})-{a25},1)'
    q[f'K{rr}'] = f'=ROUND(SUM(H{r}:K{r})-{a26},1)'
    q[f'N{rr}'] = f'=ROUND(N{r}-{h26},2)'
    q[f'O{rr}'] = f'=ROUND(O{r}-{h27},2)'
    for c in 'GKNO': style(q[f'{c}{rr}'], src_val)
wb.save(fn); print('added rows 44-52')
