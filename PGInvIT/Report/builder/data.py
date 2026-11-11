"""Assemble all PGInvIT figures used in the report (Rs crore unless stated)."""
import json, datetime as dt

SP = '/tmp/claude-0/-home-user-Power/562dd684-59fa-5b19-94f2-822ecbb92d34/scratchpad'
M = json.load(open(f'{SP}/report/build/modeldata.json'))
A = json.load(open(f'{SP}/agentA/consolidated_history.json'))
SPV = json.load(open(f'{SP}/agentC/spv_history.json'))['spvs']
Q = json.load(open(f'{SP}/agentB/quarterly_history.json'))
MK = json.load(open(f'{SP}/agentM/market.json'))

SPVS = ['VTL', 'KATL', 'PPTL', 'WTL', 'JPTL']
FULL = {'VTL': 'Vizag Transmission Limited', 'KATL': 'Kala Amb Transmission Limited', 'PPTL': 'Parli Power Transmission Limited',
        'WTL': 'Warora Transmission Limited', 'JPTL': 'Jabalpur Power Transmission Limited'}
FORMER = {'VTL': 'POWERGRID Vizag Transmission Limited (PVTL)', 'KATL': 'POWERGRID Kala Amb Transmission Limited (PKATL)',
          'PPTL': 'POWERGRID Parli Transmission Limited (PPTL)', 'WTL': 'POWERGRID Warora Transmission Limited (PWTL)',
          'JPTL': 'POWERGRID Jabalpur Transmission Limited (PJTL)'}
STATES = {'VTL': 'Andhra Pradesh, Telangana', 'KATL': 'Himachal Pradesh', 'PPTL': 'Maharashtra',
          'WTL': 'Madhya Pradesh, Maharashtra', 'JPTL': 'Madhya Pradesh'}
ELEMENTS = {'VTL': '2 lines – 957 ckms', 'KATL': '1 line – 2 ckms; 1 substation – 630 MVA; RTM bus reactor',
            'PPTL': '3 lines – 966 ckms; 1 substation – 3,000 MVA; RTM line bay', 'WTL': '4 lines – 1,028 ckms; 1 substation – 3,000 MVA',
            'JPTL': '1 line – 745 ckms'}
TARIFF_TYPE = {'VTL': '(TBCB) – BOOM', 'KATL': '(TBCB) – BOOM; RTM element', 'PPTL': '(TBCB) – BOOM; RTM element',
               'WTL': '(TBCB) – BOOM', 'JPTL': '(TBCB) – BOOM'}
VAL_DATE = dt.date(2026, 3, 31)
UNITS_MN = 909.9992
UNITS_CR = 90.99992
PRICE = M['price']
PRICE_DATE = '09-Nov-26'


def iso(s):
    return dt.date.fromisoformat(s)


def mon(d, long=True):
    return d.strftime('%b-%Y' if long else '%b-%y')


def years_between(a, b):
    return (b - a).days / 365.25


def f0(x):
    return f'{x:,.0f}'


def f1(x):
    return f'{x:,.1f}'


def f2(x):
    return f'{x:,.2f}'


def pct(x, d=1):
    return f'{x * 100:.{d}f}%'


def neg0(x):
    return f'({abs(x):,.0f})' if x < 0 else f'{x:,.0f}'


# ---- SPV level ------------------------------------------------------------------------------------
spv = {}
tot_ev = sum(M['spv'][s]['ev'] for s in SPVS)
tot_ebitda = sum(M['spv'][s]['ebitda27'] for s in SPVS)
for s in SPVS:
    st = SPV[s]['static']
    cod = iso(st['project_cod'])
    exp = iso(st['tsa_expiry'])
    av = SPV[s]['availability_annual']
    spv[s] = dict(cod=cod, expiry=exp, op_hist=years_between(cod, VAL_DATE), resid=years_between(VAL_DATE, exp),
                  avail=av, ev=M['spv'][s]['ev'], ev_sh=M['spv'][s]['ev'] / tot_ev, ebitda=M['spv'][s]['ebitda27'],
                  ebitda_sh=M['spv'][s]['ebitda27'] / tot_ebitda, tariff=M['spv'][s]['tariff27'],
                  acq74=iso(st['acquired_74pct_date']), acq26=iso(st['acquired_26pct_date']),
                  pp74=st['purchase_price_74pct_rs_cr'], pp26=st['purchase_price_26pct_rs_cr'],
                  ev_ipo=st['enterprise_value_at_ipo_31dec2020_rs_cr'], debt_sponsor=st['sponsor_debt_31mar2021_rs_cr'],
                  ckm=st['total_ckm'], mva=st['total_mva'] or 0,
                  rev={fy: A['pnl'][f'rev_{s}'][f'FY{fy % 100}'] for fy in range(2022, 2027)})
BY_EV = sorted(SPVS, key=lambda s: -spv[s]['ev'])
BY_REV = sorted(SPVS, key=lambda s: -spv[s]['rev'][2026])

# ---- consolidated history -------------------------------------------------------------------------
P, B, C, O, N = A['pnl'], A['bs'], A['cf'], A['other'], A['ndcf']
hist = {}
for fy in range(2022, 2027):
    k = f'FY{fy % 100}'
    opex = sum(P[x][k] or 0 for x in ('investment_manager_fees', 'project_manager_fees', 'om_infrastructure_maintenance_charges',
                                      'employee_benefits', 'insurance', 'other_expenses'))
    debt = B['total_borrowings_principal_term_loan'][k]
    cash = (B['cash_and_cash_equivalents'][k] or 0) + (B['other_bank_balances'][k] or 0)
    nav = O['nav_per_unit_fair_value_rs'][k]
    netassets = O['net_assets_attributable_fair_value_rs_crore'][k]
    hist[fy] = dict(rev=P['revenue_from_operations'][k], ebitda=P['revenue_from_operations'][k] - opex, opex=opex,
                    fin=P['finance_costs'][k], debt=debt, cash=cash, netdebt=debt - cash, nav=nav,
                    aum=netassets + (debt - cash), dpu=O['dpu_declared_for_year_rs'][k],
                    dist=O['dpu_declared_for_year_rs'][k] * UNITS_CR, ndcf=N['ndcf_trust_level'][k], pat=P['profit_after_tax'][k],
                    current_tax=P['current_tax'][k])

# ---- distributions by quarter ----------------------------------------------------------------------
D = Q['distribution']
quarters = [q for q in Q['quarters'] if D['dpu_rs'].get(q)]


def q_end(q):
    n, fy = int(q[0]), 2000 + int(q[-2:])
    y = fy - 1 if n <= 3 else fy
    m = {1: 6, 2: 9, 3: 12, 4: 3}[n]
    return dt.date(y, m, 30 if m in (6, 9) else 31)


dist_q = [(q, q_end(q), D['dpu_rs'][q], D['dpu_interest_rs'][q], (D['dpu_taxable_dividend_rs'][q] or 0) + (D['dpu_exempt_dividend_rs'][q] or 0),
           D['dpu_repayment_of_capital_spv_debt_rs'][q], D['dpu_treasury_income_rs'][q]) for q in quarters]
total_dist = sum(x[2] for x in dist_q)


def xirr(cfs, ds):
    d0 = ds[0]
    f = lambda x: sum(c / (1 + x) ** ((d - d0).days / 365) for c, d in zip(cfs, ds))
    lo, hi = -0.9, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if f(m) > 0 else (lo, m)
    return m


LIST_DATE = dt.date(2021, 5, 14)
LATEST = dt.date(2026, 11, 9)
ret_total = xirr([-100] + [x[2] for x in dist_q] + [PRICE], [LIST_DATE] + [x[1] for x in dist_q] + [LATEST])
ret_cap = (PRICE / 100) ** (1 / ((LATEST - LIST_DATE).days / 365)) - 1
ret_dist = ret_total - ret_cap

# ---- market ----------------------------------------------------------------------------------------
fy_avg = MK['fy_avg']
mcap = PRICE * UNITS_CR
