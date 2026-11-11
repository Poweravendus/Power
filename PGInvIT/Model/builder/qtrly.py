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


NDCF_LINES = ['NDCF at SPV - VTL', 'NDCF at SPV - KATL', 'NDCF at SPV - PPTL', 'NDCF at SPV - WTL', 'NDCF at SPV - JPTL', 'NDCF at SPV',
              'Interest income from SPVs', 'Dividend income from SPVs', 'Repayment of capital (SPV debt)', 'Distributions received from SPVs',
              'Retained at SPVs', 'Cash flow from operating activities at Trust', 'Other income', 'WC movement', 'Tax at Trust',
              'Finance cost on borrowing', 'Debt repayment', 'Capex', 'DSRA / other adjustments', 'NDCF Generated', 'NDCF (as reported)', 'Check']
NDCF_BOLD = {'NDCF at SPV', 'Distributions received from SPVs', 'NDCF Generated'}


def ndcf_block(ws, Q, col, r0):
    """Quarterly NDCF in the layout of the investor presentation bridge (same lines as Consolidated)."""
    N, S = Q['ndcf'], Q['standalone']
    qs = Q['quarters']
    rows = {lab: r0 + k for k, lab in enumerate(NDCF_LINES)}
    v = lambda key, q: N.get(key, {}).get(q) or 0
    for lab, r in rows.items():
        put(ws, f'B{r}', lab, bold=lab in NDCF_BOLD, italic=lab == 'Check')
    for k, q in enumerate(qs):
        c = col[q]
        old = k < 12   # SEBI old NDCF framework up to 4QFY24, revised framework from 1QFY25
        fw = 'old_framework' if old else 'new_framework'
        vals = {f'NDCF at SPV - {s}': v(f'spv.{s}.{fw}.ndcf', q) for s in ('VTL', 'KATL', 'PPTL', 'WTL', 'JPTL')}
        fin = S['finance_costs'].get(q) or 0
        if old:
            vals.update({'Interest income from SPVs': v('trust.old_framework.interest_received', q),
                         'Dividend income from SPVs': v('trust.old_framework.dividend_received', q),
                         'Repayment of capital (SPV debt)': v('trust.old_framework.spv_debt_repayment_received', q),
                         'Cash flow from operating activities at Trust': f'={round(v("trust.old_framework.fees_interest_expenses", q), 4)}+{round(fin, 4)}',
                         'Other income': v('trust.old_framework.other_income', q),
                         'Tax at Trust': v('trust.old_framework.income_tax', q),
                         'Finance cost on borrowing': f'=-{round(fin, 4)}',
                         'Debt repayment': v('trust.old_framework.external_debt_repayment', q),
                         'DSRA / other adjustments': sum(v(f'trust.old_framework.{x}', q) for x in (
                             'dsra', 'invested_in_portfolio', 'other_adjustment', 'ipo_expense_reimbursement', 'provision_reserve',
                             'proceeds_reinvested', 'fresh_issuance', 'capital_reduction', 'sale_proceeds', 'sale_costs')),
                         'NDCF (as reported)': v('trust.old_framework.ndcf', q)})
        else:
            intr = S['interest_on_loans_to_spvs'].get(q) or 0
            div = v('trust.new_framework.dividend_post_period', q)
            vals.update({'Interest income from SPVs': intr, 'Dividend income from SPVs': div,
                         'Repayment of capital (SPV debt)': v('trust.new_framework.spv_distributions_received', q) - intr - div,
                         'Cash flow from operating activities at Trust': v('trust.new_framework.cfo', q),
                         'Other income': v('trust.new_framework.treasury_income', q),
                         'Finance cost on borrowing': v('trust.new_framework.finance_cost', q),
                         'Debt repayment': v('trust.new_framework.debt_repayment', q),
                         'Capex': v('trust.new_framework.capex', q),
                         'DSRA / other adjustments': v('trust.new_framework.reserve', q) + v('trust.new_framework.sale_proceeds', q),
                         'NDCF (as reported)': v('trust.new_framework.ndcf', q)})
        for lab, x in vals.items():
            if isinstance(x, str) or abs(x) > 1e-9:
                put(ws, f'{c}{rows[lab]}', x if isinstance(x, str) else round(x, 4), fmt=NUM1, color=RED)
        R = rows
        put(ws, f'{c}{R["NDCF at SPV"]}', f'=SUM({c}{R["NDCF at SPV - VTL"]}:{c}{R["NDCF at SPV - JPTL"]})', fmt=NUM1, bold=True)
        put(ws, f'{c}{R["Distributions received from SPVs"]}', f'=SUM({c}{R["Interest income from SPVs"]}:{c}{R["Repayment of capital (SPV debt)"]})', fmt=NUM1, bold=True)
        put(ws, f'{c}{R["Retained at SPVs"]}', f'={c}{R["Distributions received from SPVs"]}-{c}{R["NDCF at SPV"]}', fmt=NUM1)
        put(ws, f'{c}{R["NDCF Generated"]}', f'={c}{R["Distributions received from SPVs"]}+SUM({c}{R["Cash flow from operating activities at Trust"]}:{c}{R["DSRA / other adjustments"]})', fmt=NUM1, bold=True)
        put(ws, f'{c}{R["Check"]}', f'={c}{R["NDCF Generated"]}-{c}{R["NDCF (as reported)"]}', fmt=NUM1)
    return r0 + len(NDCF_LINES) + 1, rows
