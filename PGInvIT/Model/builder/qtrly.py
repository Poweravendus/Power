import re
ABBR = {'pbt': 'PBT', 'pat': 'PAT', 'epu': 'EPU', 'ndcf': 'NDCF', 'spvs': 'SPVs', 'spv': 'SPV', 'cfo': 'CFO', 'dsra': 'DSRA', 'dpu': 'DPU',
        'om': 'O&M', 'ipo': 'IPO', 'rs': 'Rs.', 'ebitda': 'EBITDA', 'im': 'IM', 'nci': 'NCI', 'a': '(A)', 'b': '(B)', 'pct': '%',
        'incl': 'incl.', 'excl': 'excl.', 'vtl': 'VTL', 'katl': 'KATL', 'pptl': 'PPTL', 'wtl': 'WTL', 'jptl': 'JPTL'}
GROUP = {'trust': 'Trust', 'spv_total': 'All SPVs', 'old_framework': 'SEBI old NDCF framework (1QFY22-4QFY24)',
         'new_framework': 'SEBI revised NDCF framework (1QFY25 onwards)', 'spv': 'SPV'}


def pretty(key):
    words = key.replace('_', ' ').split()
    out = [ABBR.get(w.lower(), w) for w in words]
    s = ' '.join(out)
    return s[:1].upper() + s[1:]


def flatten(data, prefix=()):
    """Yield (group tuple, leaf name, series) from nested dicts and dotted keys."""
    for k, v in data.items():
        parts = prefix + tuple(k.split('.'))
        if isinstance(v, dict) and v and not any(re.match(r'\dQFY\d\d', x) for x in v):
            yield from flatten(v, parts)
        else:
            yield parts[:-1], parts[-1], v


"""Qtrly sheet: quarterly standalone (Trust) P&L, consolidated P&L, NDCF and distributions, as reported (Rs cr)."""
from common import *


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def build_qtrly(ws, Q):
    std_sheet(ws, colA=2.71, widths={'B': 54})
    qs = Q['quarters']
    col = {q: L(3 + k) for k, q in enumerate(qs)}
    r = 2

    def header(title, r):
        put(ws, f'B{r}', title, bold=True, fill=SEC_FILL)
        put(ws, f'B{r + 1}', 'Rs. cr', bold=True, border_b=True)
        for q in qs:
            put(ws, f'{col[q]}{r + 1}', q, bold=True, align='right', border_b=True)
        return r + 2

    def is_series(x):
        return isinstance(x, dict) and any(k in col for k in x)

    def lines(data, r, fmt, indent=''):
        for line, vals in data.items():
            if is_series(vals):
                if not any(_num(vals.get(q)) for q in qs):
                    continue
                lab = indent + line.replace('_', ' ')
                put(ws, f'B{r}', lab, bold=any(k in line.lower() for k in ('total', 'ndcf', 'ebitda', 'pbt', 'pat', 'distributed')))
                for q in qs:
                    v = vals.get(q)
                    if _num(v):
                        put(ws, f'{col[q]}{r}', v, fmt=fmt, color=RED)
                    elif isinstance(v, str) and v:
                        put(ws, f'{col[q]}{r}', v, color=RED, align='right')
                r += 1
            elif isinstance(vals, dict):
                sub = {k: v for k, v in vals.items()}
                has = any(is_series(v) and any(_num(v.get(q)) for q in qs) for v in sub.values()) or any(isinstance(v, dict) and not is_series(v) for v in sub.values())
                if not has:
                    continue
                name = line.replace('_', ' ').replace('old framework', 'SEBI old NDCF framework (1QFY22-4QFY24)').replace('new framework', 'SEBI revised NDCF framework (1QFY25 onwards)')
                put(ws, f'B{r}', indent + name, bold=True, italic=True)
                r = lines(sub, r + 1, fmt, indent + '  ')
        return r

    def block(title, data, r, fmt=NUM1):
        r = header(title, r)
        last_group = None
        for grp, leaf, vals in flatten(data):
            if not is_series(vals) or not any(_num(vals.get(q)) or (isinstance(vals.get(q), str) and vals.get(q)) for q in qs):
                continue
            if grp != last_group and grp:
                name = ' - '.join(GROUP.get(g, g.upper() if g.lower() in ABBR else pretty(g)) for g in grp if g != 'spv')
                put(ws, f'B{r}', name, bold=True, italic=True, border_b=True)
                r += 1
            last_group = grp
            lab = ('  ' if grp else '') + pretty(leaf)
            put(ws, f'B{r}', lab, bold=any(k in leaf.lower() for k in ('total', 'ndcf', 'ebitda', 'pbt', 'pat', 'distributed')) and 'per_unit' not in leaf)
            for q in qs:
                v = vals.get(q)
                if _num(v):
                    put(ws, f'{col[q]}{r}', v, fmt=fmt, color=RED)
                elif isinstance(v, str) and v:
                    put(ws, f'{col[q]}{r}', v, color=RED, align='right')
            r += 1
        return r + 1

    for key, title in (('standalone', 'Standalone (Trust)'), ('consolidated', 'Consolidated'),
                       ('ndcf', 'Quarterly NDCF Build-up'), ('distribution', 'Distribution per unit and components')):
        if Q.get(key):
            r = block(title, Q[key], r, fmt=NUM2 if key == 'distribution' else NUM1)
    notes = []
    if notes:
        put(ws, f'B{r}', 'Notes', bold=True)
        for k, n in enumerate(notes[:40]):
            put(ws, f'B{r + 1 + k}', str(n)[:250], italic=True)
    ws.freeze_panes = 'C2'
