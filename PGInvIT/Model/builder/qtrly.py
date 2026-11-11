"""Qtrly sheet: quarterly standalone (Trust) P&L, consolidated P&L, NDCF and distributions, as reported (Rs cr)."""
from common import *


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def build_qtrly(ws, Q):
    std_sheet(ws, colA=2.71, widths={'B': 54})
    qs = Q['quarters']
    col = {q: L(3 + k) for k, q in enumerate(qs)}
    r = 2
    put(ws, 'B1', 'Quarterly results as reported (Rs. cr); source: NSE results filings, investor presentations, half-yearly and annual reports', italic=True)

    def header(title, r):
        put(ws, f'B{r}', title, bold=True, fill=SEC_FILL)
        put(ws, f'B{r + 1}', 'Rs. cr', bold=True, border_b=True)
        for q in qs:
            put(ws, f'{col[q]}{r + 1}', q, bold=True, align='right', border_b=True)
        return r + 2

    def block(title, data, r, fmt=NUM1):
        r = header(title, r)
        for line, vals in data.items():
            if not isinstance(vals, dict):
                continue
            put(ws, f'B{r}', line.replace('_', ' '), bold=any(k in line.lower() for k in ('total', 'profit', 'ndcf', 'ebitda', 'pbt', 'pat')))
            for q in qs:
                v = vals.get(q)
                if _num(v):
                    put(ws, f'{col[q]}{r}', v, fmt=fmt, color=RED)
            r += 1
        return r + 1

    for key, title in (('standalone', 'Standalone (Trust)'), ('consolidated', 'Consolidated'),
                       ('ndcf', 'Quarterly NDCF Build-up'), ('distribution', 'Distribution per unit and components')):
        if Q.get(key):
            r = block(title, Q[key], r, fmt=NUM2 if key == 'distribution' else NUM1)
    notes = Q.get('notes') or []
    if notes:
        put(ws, f'B{r}', 'Notes', bold=True)
        for k, n in enumerate(notes[:40]):
            put(ws, f'B{r + 1 + k}', str(n)[:250], italic=True)
    ws.freeze_panes = 'C2'
