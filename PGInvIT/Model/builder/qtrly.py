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

    nd_rows = {}
    for key, title in (('standalone', 'Standalone (Trust)'), ('consolidated', 'Consolidated'),
                       ('ndcf', 'Quarterly NDCF Build-up'), ('distribution', 'Distribution per unit and components')):
        if key == 'ndcf' and Q.get('ndcf'):
            r, nd_rows = ndcf_block(ws, Q, col, header(title, r))
        elif Q.get(key):
            r = block(title, Q[key], r, fmt=NUM2 if key == 'distribution' else NUM1)
    notes = []
    if notes:
        put(ws, f'B{r}', 'Notes', bold=True)
        for k, n in enumerate(notes[:40]):
            put(ws, f'B{r + 1 + k}', str(n)[:250], italic=True)
    ws.freeze_panes = 'C2'
    return col, nd_rows


NDCF_LINES = ['NDCF at SPV - VTL', 'NDCF at SPV - KATL', 'NDCF at SPV - PPTL', 'NDCF at SPV - WTL', 'NDCF at SPV - JPTL', 'SPVs NDCF',
              'Upstreamed to PGInvIT, % of SPVs NDCF', 'Cash flow from operating activities', 'Interest income', 'Dividend income',
              'Repayment of capital (SPV debt)', 'Other income', 'Finance cost on borrowing', 'Debt repayment', 'CAPEX',
              'NDCF (PGInvIT)', 'NDCF (as reported)', 'Check']
NDCF_BOLD = {'SPVs NDCF', 'NDCF (PGInvIT)'}


def ndcf_block(ws, Q, col, r0):
    """Quarterly NDCF waterfall in the layout of the investor presentation (same lines as Consolidated)."""
    N, S = Q['ndcf'], Q['standalone']
    qs = Q['quarters']
    rows = {lab: r0 + k for k, lab in enumerate(NDCF_LINES)}
    v = lambda key, q: N.get(key, {}).get(q) or 0
    for lab, r in rows.items():
        put(ws, f'B{r}', lab, bold=lab in NDCF_BOLD, italic=lab in ('Check', 'Upstreamed to PGInvIT, % of SPVs NDCF'))
    R = rows
    for k, q in enumerate(qs):
        c = col[q]
        old = k < 12   # SEBI old NDCF framework up to 4QFY24, revised framework from 1QFY25
        fw = 'old_framework' if old else 'new_framework'
        vals = {f'NDCF at SPV - {s}': v(f'spv.{s}.{fw}.ndcf', q) for s in ('VTL', 'KATL', 'PPTL', 'WTL', 'JPTL')}
        fin = S['finance_costs'].get(q) or 0
        if old:
            # old format: Trust fees include interest (split out using the standalone P&L); tax, DSRA and other
            # retentions are Trust-level operating items
            parts = [v('trust.old_framework.fees_interest_expenses', q), fin, v('trust.old_framework.income_tax', q),
                     sum(v(f'trust.old_framework.{x}', q) for x in ('dsra', 'invested_in_portfolio', 'other_adjustment', 'ipo_expense_reimbursement',
                                                                     'provision_reserve', 'proceeds_reinvested', 'fresh_issuance',
                                                                     'capital_reduction', 'sale_proceeds', 'sale_costs'))]
            vals.update({'Cash flow from operating activities': '=' + '+'.join(f'{round(p, 4)}' for p in parts).replace('+-', '-'),
                         'Interest income': v('trust.old_framework.interest_received', q),
                         'Dividend income': v('trust.old_framework.dividend_received', q),
                         'Repayment of capital (SPV debt)': v('trust.old_framework.spv_debt_repayment_received', q),
                         'Other income': v('trust.old_framework.other_income', q),
                         'Finance cost on borrowing': f'=-{round(fin, 4)}',
                         'Debt repayment': v('trust.old_framework.external_debt_repayment', q),
                         'NDCF (as reported)': v('trust.old_framework.ndcf', q)})
        else:
            intr = S['interest_on_loans_to_spvs'].get(q) or 0
            div = v('trust.new_framework.dividend_post_period', q)
            vals.update({'Cash flow from operating activities': v('trust.new_framework.cfo', q) + v('trust.new_framework.reserve', q) + v('trust.new_framework.sale_proceeds', q),
                         'Interest income': intr, 'Dividend income': div,
                         'Repayment of capital (SPV debt)': v('trust.new_framework.spv_distributions_received', q) - intr - div,
                         'Other income': v('trust.new_framework.treasury_income', q),
                         'Finance cost on borrowing': v('trust.new_framework.finance_cost', q),
                         'Debt repayment': v('trust.new_framework.debt_repayment', q),
                         'CAPEX': v('trust.new_framework.capex', q),
                         'NDCF (as reported)': v('trust.new_framework.ndcf', q)})
        for lab, x in vals.items():
            if isinstance(x, str) or abs(x) > 1e-9:
                put(ws, f'{c}{R[lab]}', x if isinstance(x, str) else round(x, 4), fmt=NUM1, color=RED)
        put(ws, f'{c}{R["SPVs NDCF"]}', f'=SUM({c}{R["NDCF at SPV - VTL"]}:{c}{R["NDCF at SPV - JPTL"]})', fmt=NUM1, bold=True)
        put(ws, f'{c}{R["Upstreamed to PGInvIT, % of SPVs NDCF"]}',
            f'=IFERROR(SUM({c}{R["Interest income"]}:{c}{R["Repayment of capital (SPV debt)"]})/{c}{R["SPVs NDCF"]},"")', fmt=PCT)
        put(ws, f'{c}{R["NDCF (PGInvIT)"]}', f'=SUM({c}{R["Cash flow from operating activities"]}:{c}{R["CAPEX"]})', fmt=NUM1, bold=True)
        put(ws, f'{c}{R["Check"]}', f'={c}{R["NDCF (PGInvIT)"]}-{c}{R["NDCF (as reported)"]}', fmt=NUM1)
    return r0 + len(NDCF_LINES) + 1, rows
