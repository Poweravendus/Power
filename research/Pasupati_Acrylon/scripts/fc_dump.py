"""Final check helper: dump sheets (value | formula) for review. Usage: fc_dump.py model.xlsx sheet [maxcol]"""
import openpyxl, sys
fn, sh = sys.argv[1], sys.argv[2]
wf = openpyxl.load_workbook(fn); wv = openpyxl.load_workbook(fn, data_only=True)
f, v = wf[sh], wv[sh]
for r in range(1, f.max_row+1):
    cells = []
    for c in range(1, f.max_column+1):
        x = f.cell(r, c).value; y = v.cell(r, c).value
        if x is None: continue
        L = openpyxl.utils.get_column_letter(c)
        if isinstance(x, str) and x.startswith('='):
            yy = round(y, 3) if isinstance(y, float) else y
            cells.append(f"{L}={yy} [{x}]")
        else:
            cells.append(f"{L}={round(x,3) if isinstance(x,float) else x}")
    if cells: print(r, ' | '.join(cells))
