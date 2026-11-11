"""Apply the model's visual conventions to every sheet of the PGInvIT workbook.

Convention:
  dark grey  D9D9D9  label column and historical columns (white -15%)
  light grey F2F2F2  forecast columns (white -5%)
  mid grey   BFBFBF  total rows on Assumption (white -25%)
  light blue E3ECF6  input / output boxes (accent6 +80%)
  steel blue 336699  Assumption header (accent1), white bold text
  pale blue  D6E0EB  summary labels in AssetLevelEst (accent1 +80%)
  fonts: red FF0000 historical inputs (driver sheet) and growth rows (italic); blue 0033CC forecast inputs;
         green 00B050 carry-forward links; black formulas.
"""
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment
from openpyxl.utils import get_column_letter as L, column_index_from_string as CI

DG, LG, MG, LB, SB, PB = 'FFD9D9D9', 'FFF2F2F2', 'FFBFBFBF', 'FFE3ECF6', 'FF336699', 'FFD6E0EB'
YEL, ORG, HDRB = 'FFFFFF00', 'FFFFC000', 'FFDDEBF7'
RED, BLUE, GREEN, BLACK, WHITE, NAVY = 'FFFF0000', 'FF0033CC', 'FF00B050', 'FF000000', 'FFFFFFFF', 'FF00008B'
THIN, MED = Side(style='thin'), Side(style='medium')


def fill(c, rgb):
    c.fill = PatternFill('solid', fgColor=rgb) if rgb else PatternFill(fill_type=None)


def font(c, color=None, bold=None, italic=None):
    f = c.font
    c.font = Font(name='Arial', size=9, bold=f.b if bold is None else bold, italic=f.i if italic is None else italic,
                  color=color if color else (f.color if f.color is not None and getattr(f.color, 'type', None) == 'rgb' else BLACK))


def is_formula(c):
    return isinstance(c.value, str) and c.value.startswith('=')


def is_input(c):
    return isinstance(c.value, (int, float)) and not isinstance(c.value, bool) or (hasattr(c.value, 'year') and not is_formula(c))


def carry_forward(c):
    """'=G78' style link to the previous column on the same row."""
    if not is_formula(c):
        return False
    prev = L(c.column - 1) + str(c.row)
    return c.value.replace('$', '') == '=' + prev


def band(ws, r1, r2, c1, c2, rgb):
    for r in range(r1, r2 + 1):
        for k in range(c1, c2 + 1):
            fill(ws.cell(r, k), rgb)


def box(ws, r1, r2, c1, c2, side=MED):
    for r in range(r1, r2 + 1):
        for k in range(c1, c2 + 1):
            c = ws.cell(r, k)
            b = c.border
            c.border = Border(top=side if r == r1 else b.top, bottom=side if r == r2 else b.bottom,
                              left=side if k == c1 else b.left, right=side if k == c2 else b.right)


def underline_row(ws, r, c1, c2):
    for k in range(c1, c2 + 1):
        c = ws.cell(r, k)
        c.border = Border(bottom=THIN)
        font(c, bold=True)


def color_values(ws, r1, r2, c1, c2, hist_cols, input_hist=BLACK, input_fcst=BLUE, formula_fcst=BLACK, links_green=False):
    for r in range(r1, r2 + 1):
        for k in range(c1, c2 + 1):
            c = ws.cell(r, k)
            if c.value is None:
                continue
            red_row = c.font.color is not None and getattr(c.font.color, 'rgb', None) == RED and c.font.i
            if red_row:
                continue
            if k in hist_cols:
                if is_input(c):
                    font(c, input_hist)
                else:
                    font(c, BLACK)
            else:
                if is_input(c):
                    font(c, input_fcst)
                elif links_green and carry_forward(c):
                    font(c, GREEN)
                else:
                    font(c, formula_fcst)


# ------------------------------------------------------------------------------------------------
def fmt_consolidated(ws, hist_c1, hist_c2, fc_c1, fc_c2, last_row, growth_rows, header_rows):
    band(ws, 2, last_row, 2, 2, DG)
    band(ws, 2, last_row, hist_c1, hist_c2, DG)
    band(ws, 2, last_row, fc_c1, fc_c2, LG)
    for r in range(2, last_row + 1):
        for k in range(hist_c1, fc_c2 + 1):
            c = ws.cell(r, k)
            if not (isinstance(c.value, str) and not c.value.startswith('=')):
                c.alignment = Alignment(horizontal='right')
    color_values(ws, 4, last_row, hist_c1, fc_c2, set(range(hist_c1, hist_c2 + 1)), input_hist=BLACK, links_green=True)
    for r in growth_rows:
        for k in range(2, fc_c2 + 1):
            c = ws.cell(r, k)
            font(c, RED, italic=True)
    for r in header_rows:
        underline_row(ws, r, 2, fc_c2)
    # driver columns (AK value, AL note)
    for r in range(3, last_row + 1):
        a, b = ws.cell(r, fc_c2 + 2), ws.cell(r, fc_c2 + 3)
        if a.value is not None:
            fill(a, LB)
            font(a, BLUE if not is_formula(a) else BLACK, bold=False)
        if b.value is not None:
            font(b, BLACK, italic=False)
    for k in (fc_c2 + 2, fc_c2 + 3):
        c = ws.cell(3, k)
        fill(c, DG)
        font(c, BLACK, bold=True)


def fmt_qtrly(ws, last_col):
    last = ws.max_row
    notes_row = next((r for r in range(1, last + 1) if ws.cell(r, 2).value == 'Notes'), last + 1)
    band(ws, 2, notes_row - 1, 2, last_col, DG)
    for r in range(2, notes_row):
        b = ws.cell(r, 2)
        if b.font.b and b.fill is not None and ws.cell(r + 1, 2).value == 'Rs. cr':
            underline_row(ws, r, 2, last_col)
        if b.value == 'Rs. cr':
            underline_row(ws, r, 2, last_col)
        for k in range(3, last_col + 1):
            c = ws.cell(r, k)
            if c.value is not None:
                font(c, BLACK)
                c.alignment = Alignment(horizontal='right')
    for r in range(notes_row, last + 1):
        font(ws.cell(r, 2), BLACK)


def fmt_sensitivity(ws, SEN, hist_c1, hist_c2, fc_c2, n_spv, exit_last_col, mat_last_col):
    # top input / output box
    band(ws, 2, 5, 2, 3, LB)
    box(ws, 2, 5, 2, 3)
    font(ws['C2'], BLUE, bold=True)
    font(ws['D2'], RED, italic=True)
    font(ws['D3'], RED, italic=True)
    hist = set(range(hist_c1, hist_c2 + 1))
    for hdr, first in ((SEN['avail_hdr'], SEN['avail']), (SEN['tariff_hdr'], SEN['tariff']), (SEN['eff_hdr'], SEN['eff']),
                       (SEN['marg_hdr'], SEN['marg']), (SEN['wc'] - 1, SEN['wc'])):
        n = 4 if hdr == SEN['wc'] - 1 else (n_spv + 1 if hdr == SEN['eff_hdr'] else n_spv)
        last = first + n - 1
        band(ws, hdr, last, 2, 2, DG)
        band(ws, hdr, last, hist_c1, hist_c2, DG)
        band(ws, hdr, last, hist_c2 + 1, fc_c2, LG)
        underline_row(ws, hdr, 2, fc_c2)
        for r in range(first, last + 1):
            for k in range(hist_c1, fc_c2 + 1):
                c = ws.cell(r, k)
                if c.value is None:
                    continue
                bold = r == SEN['eff_tot'] or (hdr == SEN['wc'] - 1 and r == last)
                font(c, RED if k in hist else BLUE, bold=bold)
        font(ws.cell(hdr - 1, 2), BLACK, bold=True)
        nr = last + 1
        if ws.cell(nr, 2).value:
            font(ws.cell(nr, 2), RED, italic=True)
    # ladder
    r0 = SEN['ladder']
    band(ws, r0 - 1, r0 + 4, 2, 3, DG)
    underline_row(ws, r0 - 1, 2, 3)
    for r in range(r0, r0 + 5):
        font(ws.cell(r, 3), BLUE)
    font(ws.cell(r0 - 2, 2), BLACK, bold=True)
    # hold to exit / maturity blocks
    for top, lastc in ((SEN['exit_hdr'], exit_last_col), (SEN['mat_hdr'], mat_last_col)):
        r1, r2 = top + 1, top + 7 if top == SEN['mat_hdr'] else top + 6
        band(ws, r1, r2, 2, 3, DG)
        band(ws, r1, r2, 4, lastc, LG)
        underline_row(ws, r1, 2, lastc)
        for r in range(r1 + 1, r2 + 1):
            for k in range(3, lastc + 1):
                c = ws.cell(r, k)
                if c.value is None:
                    continue
                font(c, BLUE if (is_input(c) and not is_formula(c)) else RED, bold=r == top + 6)
            font(ws.cell(r, 2), BLACK, bold=r in (top + 6, top + 7))
        font(ws.cell(top, 2), BLACK, bold=True)
    fill(ws.cell(SEN['exit_hdr'] - 1, 2), DG)
    # debt mirror
    d = SEN['debt']
    band(ws, d, d + 5, 2, 2, DG)
    band(ws, d, d + 5, hist_c2 + 1, fc_c2, LG)
    for r in range(d, d + 6):
        for k in range(hist_c2 + 1, fc_c2 + 1):
            c = ws.cell(r, k)
            if c.value is not None:
                font(c, GREEN, bold=r == d + 3)
    font(ws.cell(d - 1, 2), BLACK, bold=True)


def fmt_assetlevel(ws, blocks, first_col, last_col, memo_col):
    """blocks: list of r0 (header row of each SPV block)."""
    summary = {'PV of Cash Flows', 'PV of TV Cash Flows', 'RTM project value (valuer)', 'Enterprise Value', 'WACC'}
    for r0 in blocks:
        font(ws.cell(r0 - 1, 3), NAVY, bold=True)
        band(ws, r0, r0 + 19, 3, last_col, LG)
        underline_row(ws, r0, 3, last_col)
        seen_pv = False
        for r in range(r0 + 1, r0 + 20):
            lab = ws.cell(r, 3).value
            if lab == 'PV of Cash Flows':
                if seen_pv:
                    fill(ws.cell(r, 3), PB)
                seen_pv = True
            elif lab in summary:
                fill(ws.cell(r, 3), PB)
            if isinstance(lab, str) and lab.startswith(('Memo', 'Check')):
                font(ws.cell(r, 3), BLACK, italic=True)
            for k in range(first_col, last_col + 1):
                c = ws.cell(r, k)
                if c.value is None:
                    continue
                font(c, BLUE if is_input(c) else BLACK)
                if not (isinstance(c.value, str) and not c.value.startswith('=')):
                    c.alignment = Alignment(horizontal='right')
            if isinstance(lab, str) and lab.startswith('Check'):
                band(ws, r, r, first_col + 1, last_col, YEL)
        # variance cell and memo block
        fill(ws.cell(r0 + 18, first_col + 2), YEL)
        for r in range(r0 + 1, r0 + 16):
            v = ws.cell(r, memo_col + 1)
            if v.value is None:
                continue
            if is_input(v):
                font(v, BLUE)
            elif isinstance(v.value, str) and '!' not in v.value and v.value.startswith('=D') or (isinstance(v.value, str) and v.value.startswith('=E')):
                font(v, GREEN)
            else:
                font(v, BLACK)
            if 'Variance' in str(ws.cell(r, memo_col).value):
                fill(v, YEL)


def fmt_assumption(ws, item_rows, total_rows, first_col, last_col, extra_cols):
    for k in range(3, last_col + 1):
        c = ws.cell(2, k)
        fill(c, SB)
        font(c, WHITE, bold=True)
    for k in extra_cols:
        c = ws.cell(2, k)
        fill(c, SB)
        font(c, WHITE, bold=True)
    for r in item_rows:
        band(ws, r, r, 3, last_col, LG)
        for k in range(first_col, last_col + 1):
            c = ws.cell(r, k)
            if c.value is not None:
                font(c, BLUE if is_input(c) else BLACK)
        for k in extra_cols:
            c = ws.cell(r, k)
            if c.value is not None:
                fill(c, LB)
                font(c, BLUE if is_input(c) else BLACK, italic=False)
    for r in total_rows:
        band(ws, r, r, 3, last_col, MG)
        for k in range(3, last_col + 1):
            font(ws.cell(r, k), BLACK, bold=True)
    for r in range(1, ws.max_row + 1):
        a = ws.cell(r, 1)
        if a.value:
            font(a, BLACK, bold=True)


def fmt_cashflows(ws, last_col, check_row):
    for k in range(3, last_col + 1):
        c = ws.cell(3, k)
        fill(c, LB)
        font(c, BLACK, bold=True)
        c.alignment = Alignment(horizontal='center')
    fill(ws['B1'], LG)
    font(ws['B1'], BLACK, bold=True, italic=False)
    for r in range(4, check_row + 1):
        for k in range(3, last_col + 1):
            c = ws.cell(r, k)
            if c.value is not None:
                c.alignment = Alignment(horizontal='center')
    band(ws, check_row, check_row, 2, last_col, YEL)


def fmt_irr(ws, last_col):
    for k in range(2, last_col + 1):
        c = ws.cell(8, k)
        fill(c, LG)
        font(c, BLACK, bold=True)
        c.alignment = Alignment(horizontal='center')
    fill(ws['B11'], YEL)
    font(ws['B11'], BLACK, bold=True)
    for ref in ('B2', 'B3'):
        font(ws[ref], BLUE)
    for r in (14, 15):
        a = ws.cell(r, 1)
        fill(a, HDRB if r == 14 else None)
        font(a, BLACK, bold=True)
        for k in range(1, last_col + 1):
            ws.cell(r, k).border = Border(top=THIN, bottom=THIN, left=THIN, right=THIN)
            if k > 1:
                ws.cell(r, k).alignment = Alignment(horizontal='center')
        if r == 14:
            for k in range(3, last_col + 1):
                fill(ws.cell(r, k), LG)
                font(ws.cell(r, k), BLACK, bold=True)
    for k in range(2, last_col + 1):
        ws.cell(9, k).alignment = Alignment(horizontal='center')


def fmt_keysheet(ws, strip_c1, strip_c2, tsa_c1, tsa_c2, seg_rows):
    for k in range(strip_c1, strip_c2 + 1):
        c = ws.cell(11, k)
        fill(c, DG)
    for k in range(tsa_c1, tsa_c2 + 1):
        fill(ws.cell(11, k), DG)
    for r in range(6, 11):
        for k in range(tsa_c1, tsa_c2 + 1):
            c = ws.cell(r, k)
            if c.value is not None:
                font(c, RED)
        for k in range(strip_c1, strip_c2 + 1):
            font(ws.cell(r, k), BLACK)
    r1, r2 = seg_rows
    band(ws, r1, r1, 19, strip_c2, DG)
    band(ws, r2, r2, 19, strip_c2, DG)
    for k in range(19, strip_c2 + 1):
        font(ws.cell(r1, k), BLACK, bold=True)
        font(ws.cell(r2, k), BLACK, bold=True)
    fill(ws['T3'], 'FF1F4E79')
    fill(ws['AY3'], 'FF1F4E79')


DASH = {'#,##0.0_);(#,##0.0)': '#,##0.0_);(#,##0.0);"–"_)', '#,##0_);(#,##0)': '#,##0_);(#,##0);"–"_)',
        '#,##0.00_);(#,##0.00)': '#,##0.00_);(#,##0.00);"–"_)', '0.0%': '0.0%;-0.0%;"–"', '0.00%': '0.00%;-0.00%;"–"'}


def dash_zero(ws):
    """Show zeros as a dash so nil lines read cleanly."""
    for row in ws.iter_rows():
        for c in row:
            if c.value is not None and c.number_format in DASH:
                c.number_format = DASH[c.number_format]


# ================================================================================================
# Number formats, row by row (applied last)
# ================================================================================================
N0A = '#,##0;\\(#,##0\\)'            # AssetLevelEst / Assumption / NAV block
N0B = '#,##0_);(#,##0)'              # Consolidated / Qtrly / Cashflows / Sensitivity debt
N0K = '#,##0;\\(#,##0\\);"–"'        # Key Sheet
N1C = '#,##0.0_);\\(#,##0.0\\)'      # DPU / EPU
BLUE_ALE = 'FF0000FF'


def _nf(c, fmt):
    if c.value is not None and not (isinstance(c.value, str) and not c.value.startswith('=')):
        c.number_format = fmt


def nf_assetlevel(ws, blocks, c1, c2, memo_col):
    bold_rows = {'EBITDA', 'EBITDA Margin', 'FCFF', 'FCFF with TV', 'PV of Cash Flows', 'WACC', 'Enterprise Value'}
    for r0 in blocks:
        for r in range(r0 + 1, r0 + 20):
            lab = ws.cell(r, 3).value
            fmt = {'EBITDA Margin': '0%', 'Present value factor': '#,##0.00', 'Discount period (yrs, mid-year)': '0.0',
                   'WACC': '0.0%'}.get(lab, N0A)
            if lab in bold_rows:
                font(ws.cell(r, 3), BLACK, bold=True)
            for k in range(c1, c2 + 1):
                c = ws.cell(r, k)
                _nf(c, fmt)
                if lab == 'EBITDA Margin' and c.value is not None:
                    font(c, BLUE_ALE, bold=True)
                elif lab in bold_rows - {'WACC', 'Enterprise Value'} and c.value is not None:
                    font(c, bold=True)
            if lab == 'Enterprise Value':
                _nf(ws.cell(r, c1 + 2), '0%')
        for r in range(r0 + 1, r0 + 16):
            lab = str(ws.cell(r, memo_col).value or '')
            v = ws.cell(r, memo_col + 1)
            fmt = ('0.00%' if lab.startswith(('WACC', 'Terminal growth')) else '0.0' if 'period' in lab else '0' if 'TV year' in lab
                   else '0.0\\x' if 'EV /' in lab else '0.0%' if '%' in lab or 'yield' in lab else '#,##0;\\(#,##0\\);\\-')
            _nf(v, fmt)


def nf_sensitivity(ws, SEN, hist_c2, fc_c2, n_spv, exit_last, mat_last):
    _nf(ws['C2'], '#,##0')
    for ref in ('C3', 'C4', 'C5'):
        _nf(ws[ref], '0.0%')
    secs = [(SEN['avail'], n_spv, '0.0%', '0.0%'), (SEN['tariff'], n_spv, '#,##0', '#,##0'),
            (SEN['eff'], n_spv + 1, '#,##0', '#,##0'), (SEN['marg'], n_spv, '0%', '0%'),
            (SEN['wc'], 4, N0B, '#,##0.0')]
    for first, n, fh, ff in secs:
        for r in range(first, first + n):
            for k in range(3, fc_c2 + 1):
                _nf(ws.cell(r, k), fh if k <= hist_c2 else ff)
    for r in range(SEN['ladder'], SEN['ladder'] + 5):
        _nf(ws.cell(r, 3), '0.00%')
    for top, last in ((SEN['exit_hdr'], exit_last), (SEN['mat_hdr'], mat_last)):
        for k in range(3, last + 1):
            _nf(ws.cell(top + 2, k), 'mmm-yy')
            for r in range(top + 3, top + 8):
                _nf(ws.cell(r, k), '#,##0.00')
    d = SEN['debt']
    for r in range(d, d + 6):
        for k in range(3, fc_c2 + 1):
            _nf(ws.cell(r, k), '0.00%' if r == d + 4 else N0B)


CONS_NF = {7: '0%', 18: '0%', 19: '0%', 21: '0%', 24: '0.0%', 27: '0.0%', 41: '0%', 53: '0%', 54: '0%', 57: '0.0%',
           58: N1C, 235: '0.0%', 236: '#,##0.0;\\-#,##0.0', 241: N0A, 242: N0A, 243: N0A, 244: N0A, 245: '0%',
           246: '#,##0.00', 251: N0A, 252: '#,##0.0;\\(#,##0.0\\)'}


def nf_consolidated(ws, c1, c2, last_row):
    for r in range(4, last_row + 1):
        fmt = CONS_NF.get(r, N0B)
        for k in range(c1, c2 + 1):
            _nf(ws.cell(r, k), fmt)
        drv = ws.cell(r, c2 + 2)
        if drv.value is not None:
            _nf(drv, '0.0%' if r in (9, 21, 24, 27, 235) else '0' if r in (75, 239) else N1C if r in (236, 91) else N0B)


def nf_assumption(ws, pct_rows, period_rows, c1, c2, extra_cols):
    for r in range(1, ws.max_row + 1):
        for k in range(c1, c2 + 1):
            c = ws.cell(r, k)
            if r == 1:
                _nf(c, 'mmm-yy')
            elif r in pct_rows:
                _nf(c, '0.0%')
            elif r in period_rows:
                _nf(c, '0.0')
            else:
                _nf(c, N0A)
        for k in extra_cols:
            c = ws.cell(r, k)
            if isinstance(c.value, float) and c.value < 1:
                _nf(c, '0.0%')
            elif c.value is not None:
                _nf(c, N0A)


def nf_qtrly(ws, last_col):
    for r in range(1, ws.max_row + 1):
        lab = str(ws.cell(r, 2).value or '').lower()
        fmt = N1C if ('dpu' in lab or 'epu' in lab) and 'derived' not in lab else '#,##0' if 'number' in lab else N0B
        for k in range(3, last_col + 1):
            _nf(ws.cell(r, k), fmt)


def nf_simple(ws, r1, r2, c1, c2, fmt, pct_rows=()):
    for r in range(r1, r2 + 1):
        for k in range(c1, c2 + 1):
            c = ws.cell(r, k)
            if c.number_format in ('dd-mmm-yy', 'mmm-yy'):
                continue
            _nf(c, '0.0%' if r in pct_rows else fmt)


def nf_keysheet(ws, cols, r1, r2):
    for r in range(r1, r2 + 1):
        for k in cols:
            c = ws.cell(r, k)
            if c.number_format not in ('0.00%', '"FY"0000"E"', '0'):
                _nf(c, N0K)


def unfill_spacers(ws, c1, c2, starts, r1, r2):
    """Clear the fill on empty spacer rows that lead into a new section, so sections separate visually."""
    def empty(r):
        return all(ws.cell(r, k).value is None for k in range(c1, c2 + 1))
    for r in range(r1, r2 + 1):
        if not empty(r):
            continue
        nxt = r + 1
        while nxt <= r2 and empty(nxt):
            nxt += 1
        if nxt in starts:
            for k in range(c1, c2 + 1):
                fill(ws.cell(r, k), None)
