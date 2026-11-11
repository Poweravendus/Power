"""Shared helpers for the PGInvIT model builder (mirrors the IndiGrid model conventions)."""
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L, column_index_from_string as CI

NUM = '#,##0_);(#,##0)'
NUM1 = '#,##0.0_);(#,##0.0)'
NUM2 = '#,##0.00_);(#,##0.00)'
PCT = '0.0%'
PCT2 = '0.00%'
FYFMT = '"FY"0000"E"'

RED = 'FFFF0000'      # historical hard-coded input
BLUE = 'FF0033CC'     # forecast hard-coded input / assumption
GREEN = 'FF008000'    # link to another sheet (memo)
WHITE = 'FFFFFFFF'
HDR_FILL = PatternFill('solid', fgColor='FF1F4E79')
SEC_FILL = PatternFill('solid', fgColor='FFBFBFBF')
SUB_FILL = PatternFill('solid', fgColor='FFD9D9D9')
ROW_FILL = PatternFill('solid', fgColor='FFDCE6F1')
CHK_FILL = PatternFill('solid', fgColor='FFFFFF00')
THIN = Side(style='thin')


def font(bold=False, color=None, italic=False):
    kw = dict(name='Arial', size=9, bold=bold, italic=italic)
    if color:
        kw['color'] = color
    return Font(**kw)


def put(ws, ref, value, fmt=None, bold=False, color=None, fill=None, align=None, italic=False, border_b=False):
    c = ws[ref]
    c.value = value
    c.font = font(bold, color, italic)
    if fmt:
        c.number_format = fmt
    elif isinstance(value, (int, float)) or (isinstance(value, str) and value.startswith('=')):
        c.number_format = NUM
    if fill:
        c.fill = fill
    if align:
        c.alignment = Alignment(horizontal=align, vertical='center', wrap_text=False)
    if border_b:
        c.border = Border(bottom=THIN)
    return c


def std_sheet(ws, colA=2.0, col_default=8.0, widths=None):
    """Standard format: Arial 9, row height 12, col width 8, col A 2, gridlines off."""
    ws.sheet_view.showGridLines = False
    ws.sheet_format.defaultRowHeight = 12
    ws.sheet_format.customHeight = True
    ws.sheet_format.baseColWidth = 8
    ws.sheet_format.defaultColWidth = col_default
    ws.column_dimensions['A'].width = colA
    for k, v in (widths or {}).items():
        ws.column_dimensions[k].width = v


def finish_sheet(ws):
    """Apply Arial 9 to any cell left without a font and fix row heights to 12."""
    for row in ws.iter_rows():
        for c in row:
            if c.value is not None and (c.font is None or c.font.name != 'Arial'):
                c.font = font()
    for r in range(1, ws.max_row + 1):
        ws.row_dimensions[r].height = 12


def fy_label(fy, est=False):
    return f'FY{fy % 100:02d}' + ('E' if est else '')
