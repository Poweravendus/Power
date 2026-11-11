"""Key Sheet New: SPV register (static data, valuation and contracted tariff)."""
import datetime as dt
from openpyxl.styles import Alignment, Border, Side
from common import *
from core import SPVS, A_START, A_BLOCK

DG = PatternFill('solid', fgColor='FFD9D9D9')
TOP = Border(top=Side(style='thin'))
N0 = '#,##0;\\(#,##0\\)'


def d2s(s):
    return dt.date.fromisoformat(s).strftime('%b-%Y') if s else ''


def build_keysheet(ws, S, V):
    widths = {'B': 4, 'C': 8, 'D': 34, 'E': 30, 'F': 11, 'G': 28, 'H': 78, 'I': 9, 'J': 9, 'K': 10, 'L': 30,
              'M': 20, 'N': 12, 'O': 12, 'P': 22, 'Q': 13, 'R': 12, 'S': 11}
    std_sheet(ws, colA=2.57, widths=widths)
    cols = list(widths)
    hdr = ['#', 'Asset', 'Asset Full Name', 'Type of Tariff', 'Stake Holding', 'States', 'Elements', 'ckt kms', 'MVA',
           'COD', 'Acquisition into InvIT', 'Acquired From', 'EV at IPO', 'AUM (EV)', 'Contract Type',
           'Non-Escalable Charge', 'Change-in-law', 'TSA Expiry']
    units = ['', '', '', '', '', '', '', 'kms', 'MVA', 'Date', 'Date', '', 'Rs. cr (Dec-20)', 'Rs. cr (Mar-26)', '',
             'Rs. cr (CY26)', '% of NEC', 'Date']
    put(ws, 'B2', 'Key Sheet  -  Transmission SPVs', bold=True)
    for k, (h, u) in enumerate(zip(hdr, units)):
        c = cols[k]
        right = c in ('I', 'J', 'N', 'O', 'Q', 'R')
        put(ws, f'{c}3', h, bold=True, fill=DG, align='right' if right else 'left')
        put(ws, f'{c}4', u, bold=True, fill=DG, border_b=True, align='right' if right else 'left')
    cil = {'PPTL': 0.0279, 'WTL': 0.0345, 'JPTL': 0.0523}
    for i, s in enumerate(SPVS):
        r = 5 + i
        st = S[s]['static']
        elements = '; '.join(
            (f'{e["kv"]} kV {e.get("circuit") or ""} line {e["ckm"]:,.0f} ckm' if e['type'] == 'line' else
             f'{e["type"].replace("_", " ")} {e["kv"]} kV' + (f' {e["mva"]:,.0f} MVA' if e.get('mva') else ''))
            for e in st['elements'])
        tariff = 'Section 63 (TBCB) - BOOM' + ('; escalable component' if s == 'VTL' else '') + ('; RTM element' if s in ('KATL', 'PPTL') else '')
        vals = {'B': (i + 1, '0'), 'C': (s, None), 'D': (st['full_legal_name'], None), 'E': (tariff, None), 'F': ('100%', None),
                'G': (', '.join(st['states']), None), 'H': (elements, None), 'I': (st['total_ckm'], '#,##0'), 'J': (st['total_mva'] or 0, '#,##0'),
                'K': (d2s(st['project_cod']), None), 'L': (f'74%: {d2s(st["acquired_74pct_date"])}; 26%: {d2s(st["acquired_26pct_date"])}', None),
                'M': ('POWERGRID (Sponsor)', None), 'N': (st.get('enterprise_value_at_ipo_31dec2020_rs_cr'), N0),
                'O': (f'=AssetLevelEst!E{A_START + A_BLOCK * i + 18}', N0), 'P': ('Fixed tariff / ISTS pool', None),
                'Q': (st['tsa_non_escalable_charges_rs_cr_by_contract_year'].get('2026'), N0), 'R': (cil.get(s, 0.0), '0.00%'),
                'S': (d2s(st['tsa_expiry']), None)}
        for c, (v, fmt) in vals.items():
            right = c in ('B', 'I', 'J', 'N', 'O', 'Q', 'R')
            put(ws, f'{c}{r}', v, fmt=fmt or '@', fill=DG, align='right' if right else 'left')
    r = 10
    for c in cols:
        put(ws, f'{c}{r}', None, fill=DG)
        ws[f'{c}{r}'].border = TOP
    put(ws, f'C{r}', 'Total', bold=True, fill=DG)
    ws[f'C{r}'].border = TOP
    for c, fmt in (('I', '#,##0'), ('J', '#,##0'), ('N', N0), ('O', N0), ('Q', N0)):
        put(ws, f'{c}{r}', f'=SUM({c}5:{c}9)', fmt=fmt, bold=True, fill=DG, align='right')
        ws[f'{c}{r}'].border = TOP
    # padding between neighbouring columns: indent text and numbers, centre dates / percentages
    for r in range(3, 11):
        for c in cols:
            cell = ws[f'{c}{r}']
            if c in ('K', 'R', 'S', 'B'):
                cell.alignment = Alignment(horizontal='center')
            elif c in ('I', 'J', 'N', 'O', 'Q'):
                cell.alignment = Alignment(horizontal='right', indent=1)
            else:
                cell.alignment = Alignment(horizontal='left', indent=1)
    for r in range(5, 11):
        for c in ('I', 'J'):
            ws[f'{c}{r}'].number_format = '#,##0;(#,##0);"–"'
    # size each column to its longest entry (headers, units, values)
    for c in cols:
        n = max(len(str(ws[f'{c}{r}'].value)) for r in (3, 4, 5, 6, 7, 8, 9) if ws[f'{c}{r}'].value is not None and not str(ws[f'{c}{r}'].value).startswith('='))
        ws.column_dimensions[c].width = min(max(n * 1.05 + 4, 10), 120)
    ws.column_dimensions['O'].width = 17
    ws.column_dimensions['B'].width = 5
    ws.freeze_panes = 'D5'
