"""Build the PGInvIT initiating-coverage report by editing the IndiGrid report in place (formatting untouched)."""
import copy, json, sys
import docx
from dx import *
import data as d
from data import f0, f1, f2, pct, SPVS, spv, hist, FULL

SP = d.SP
G = json.load(open(f'{SP}/agentG/governance.json'))
V = json.load(open(f'{SP}/agentV/valuation_history.json'))
OUT = sys.argv[1] if len(sys.argv) > 1 else f'{SP}/report/out/PGInvIT_Initiating_Coverage.docx'

doc = docx.Document(f'{SP}/report/src/IndiGrid.docx')
E = body_elements(doc)
M = d.M
cons = {int(k): v for k, v in M['cons'].items()}
BY_EV = d.BY_EV


def P(i, segs):
    set_par(E[i], segs)


def kill(*idxs):
    for i in idxs:
        if isinstance(i, range):
            for j in i:
                remove(E[j])
        else:
            remove(E[i])


def add_after(src_i, after_el, segs):
    new = clone_par(E[src_i], after=after_el)
    set_par(new, segs)
    return new


def lead(i, text):
    k = text.find('. ') + 1
    P(i, [(text[:k], True), (text[k:], False)])


def footnote(after_el, text):
    new = clone_par(E[56], after=after_el)
    set_par(new, [(text, False)])
    return new


def rebuild(tbl, keep_head, spec):
    """keep_head: number of header rows kept; spec: [(proto_row_idx, [cell values])]"""
    rs = rows(tbl)
    protos = {p: copy.deepcopy(rs[p]) for p, _ in spec}
    for r in rs[keep_head:]:
        tbl.remove(r)
    for p, vals in spec:
        new = copy.deepcopy(protos[p])
        tbl.append(new)
        fill_row(new, vals)


def dash(x, fn=f0):
    return '–' if x is None else fn(x)


def pc(x, dp=1, paren=False):
    if x is None:
        return '–'
    s = f'{abs(x) * 100:.{dp}f}%'
    if float(f'{abs(x) * 100:.{dp}f}') == 0:
        return s
    return (f'({s})' if paren else f'-{s}') if x < 0 else s


# ------------------------------------------------------------------ derived figures
EVH = {}  # company-reported EV (Rs cr) at each March valuation
for v in V['valuations']:
    if v['date'].endswith('03-31'):
        EVH[int(v['date'][:4])] = v['total_ev_mn'] / 10
for fy in range(2022, 2027):
    hist[fy]['aum'] = EVH[fy]
FY26AV = {'VTL': 1.0, 'KATL': 0.9997, 'PPTL': 0.9997, 'WTL': 0.9996, 'JPTL': 0.9987}   # company presentation (Q4 FY26)
for s in SPVS:
    spv[s]['avail']['FY26'] = FY26AV[s]
avg_op = sum(spv[s]['op_hist'] for s in SPVS) / 5
avg_res = sum(spv[s]['resid'] for s in SPVS) / 5
avg_av26 = sum(FY26AV.values()) / 5
tot_ev = sum(spv[s]['ev'] for s in SPVS)
tot_eb = sum(spv[s]['ebitda'] for s in SPVS)
tot_tar = sum(spv[s]['tariff'] for s in SPVS)
nd26 = hist[2026]['netdebt']
eq26 = tot_ev - nd26
dy = 12 / d.PRICE
prem = d.PRICE / hist[2026]['nav'] - 1
irr = M['irr']
c27, c28 = cons[2027], cons[2028]
ipo_ev = sum(spv[s]['ev_ipo'] for s in SPVS)
pp74 = sum(spv[s]['pp74'] for s in SPVS)
pp26b = sum(spv[s]['pp26'] for s in SPVS if s != 'VTL')
debt_sp = sum(spv[s]['debt_sponsor'] for s in SPVS)

# =================================================================== S1: front page
P(0, 'POWERGRID Infrastructure Investment Trust')
t = E[1]
r = rows(t)
fill_row(r[0], [None, 'POWERGRID Infrastructure Investment Trust', None, '11-Nov-26'])
fill_row(r[1], [None, 'InvITs', None, 'xx'])
fill_row(r[2], [None, f1(d.PRICE), None, f0(d.mcap), None, 'xx'])
fill_row(r[3], [None, f'{pct(dy)} for FY2027', None, 'CRISIL AAA / Stable; ICRA AAA (Stable); CARE AAA; Stable', None, 'NA'])
fill_row(r[4], [None, pct(irr)])

P(5, [('POWERGRID Infrastructure Investment Trust', True), (' (PGInvIT), sponsored by ', False),
      ('Power Grid Corporation of India Limited (POWERGRID)', True), (', is India’s first InvIT sponsored by a Central Public Sector Enterprise and a ', False),
      ('pure-play inter-state power transmission', True),
      (' vehicle. Settled in September 2020 and listed on the stock exchanges in May 2021 after a Rs. 7,735 crore IPO – the largest by an Indian InvIT at the time – '
       'the Trust was set up to monetise part of POWERGRID’s tariff-based competitive bidding (TBCB) portfolio while giving unitholders contracted, availability-linked cash flows. '
       'Five years on, the portfolio is unchanged in composition: it still comprises the five TBCB transmission SPVs acquired from the Sponsor at listing. '
       'What has changed is ownership – the Trust bought the balance 26% in VTL in March 2022 and in the other four SPVs in December 2024, and now owns 100% of all five.', False)])
P(6, [(f'As of 31 March 2026, the Trust’s Enterprise Value (AUM) stood at Rs. {f0(tot_ev)} crore, based on the Independent Valuation Report dated 13 May 2026, '
       f'all of which relates to the 5 operational transmission SPVs. Net debt stood at Rs. {f0(nd26)} crore, a net borrowing ratio of ~5% against the 70% regulatory ceiling.', True)])
P(7, 'The operational portfolio as of 31 March 2026 comprises the following assets:')
P(8, 'Transmission:')
states = sorted({x.strip() for s in SPVS for x in d.STATES[s].split(',')})
P(9, [('Portfolio scale: ', True), (f'5 operational TBCB transmission projects, representing 11 transmission lines of approximately {f0(sum(spv[s]["ckm"] for s in SPVS))} ckm '
                                   f'and 3 substations with {f0(sum(spv[s]["mva"] for s in SPVS))} MVA of transformation capacity across {len(states)} states.', False)])
P(10, [('Strong operating track record: ', True), (f'The portfolio has an average operating history of {avg_op:.1f} years as of 31 March 2026, with an average residual contract life of approximately {avg_res:.1f} years under 35-year TSAs.', False)])
P(11, [('Strong Counterparty profile: ', True), (f'100% of AUM, amounting to Rs. {f0(tot_ev)} crore, is inter-state (ISTS) and billed and collected by the Central Transmission Utility (CTUIL) through the national pool; billed receivables were equivalent to ~19 days of billing at 31 March 2026.', False)])
P(12, [('High availability: ', True), (f'Portfolio availability has remained consistently above the 98% normative level, averaging approximately {avg_av26 * 100:.2f}% in FY2026, with every SPV at or above 99.87%.', False)])
kill(range(13, 23))
P(23, 'SPV-wise revenue and AUM – FY2026')
t = E[24]
rv26 = {s: spv[s]['rev'][2026] for s in SPVS}
spec = [(1, [s, f0(rv26[s]), pc(rv26[s] / hist[2026]['rev']), '', f0(spv[s]['ev']), pc(spv[s]['ev_sh'])]) for s in BY_EV]
spec.append((4, ['Total reported – FY2026', f0(hist[2026]['rev']), '100.0%', '', f0(tot_ev), '100.0%']))
fill_row(rows(t)[0], ['SPV'])
rebuild(t, 1, spec)
kill(range(25, 37))
P(38, f'Taken together, an operational base of approximately Rs. {f0(tot_ev)} crore across five inter-state transmission SPVs, with 100% of revenue availability-linked and settled through the CTU pool, '
      f'an average residual TSA life of ~{avg_res:.0f} years and almost no leverage, makes PGInvIT a low-risk annuity. The other side of that annuity is that the portfolio has not added a single asset since listing, '
      'and contracted tariffs at three of the five SPVs step down by roughly 30% from FY2028, so distributions beyond FY2027 depend on acquisitions that have yet to materialise.')
# trust structure
P(42, 'PGInvIT is structured as a SEBI-registered infrastructure investment trust in which the Sponsor also acts as Project Manager and a wholly owned subsidiary of the Sponsor acts as Investment Manager. '
      'The key constituents of the Trust structure as on 31 March 2026 are set out below.')
P(43, [('Sponsor – Power Grid Corporation of India Limited (POWERGRID): ', True),
       ('A Maharatna CPSE under the Ministry of Power (Government of India 51.34%) and India’s largest transmission utility, with ~1.88 lakh ckm of lines and 294 substations. '
        'POWERGRID holds 15.0% of units – the regulatory minimum for a sponsor, unchanged since listing – and owns 100% of the Investment Manager.', False)])
P(44, [('Project Manager – POWERGRID: ', True),
       ('Operations and maintenance of all five SPVs are carried out by POWERGRID under O&M agreements with each SPV and a Project Implementation and Management Agreement (PIMA) dated 23 January 2021. '
        'The Trust has no O&M organisation of its own, so asset performance rests entirely on the Sponsor’s operating capability – a strength on availability, but also a concentration of dependence on one related party.', False)])
P(45, [('Trustee – IDBI Trusteeship Services Limited: ', True),
       ('Registered with SEBI as a debenture trustee and promoted by IDBI Bank, LIC and GIC, the Trustee is independent of both the Sponsor and the Investment Manager and holds the Trust’s assets on behalf of unitholders. '
        'It has acted as Trustee since inception. Its mandate includes overseeing compliance with the InvIT Regulations, unitholder voting and the appointment of the Investment Manager and Project Manager.', False)])
P(46, [('Investment Manager – POWERGRID Unchahar Transmission Limited (PUTL): ', True),
       ('PUTL is a wholly owned subsidiary of the Sponsor and is responsible for investment decisions, financing, distribution policy and overall stewardship of the Trust under an Investment Management Agreement dated 18 December 2020.', False)])
t = E[48]
fill_row(rows(t)[1], ['Operational assets (5)', f0(tot_ev), '', 'Equity', f0(eq26)])
fill_row(rows(t)[2], ['', '', '', 'Debt (net)', f0(nd26)])
fill_row(rows(t)[3], ['Total', f0(tot_ev), '', 'Total', f0(tot_ev)])
P(49, 'Portfolio Overview – at listing (May 2021) and as on 31 March 2026')
t = E[50]
fill_row(rows(t)[0], [None, 'At listing (May 2021)', 'As on 31 March 2026'])
fill_row(rows(t)[1], ['No. of assets', '5', '5'])
fill_row(rows(t)[2], [None, '3,699', '3,699'])
fill_row(rows(t)[3], [None, '6,630', '6,630'])
fill_row(rows(t)[4], ['Trust’s economic interest in SPVs', '74%', '100%'])
fill_row(rows(t)[5], ['Units outstanding (mn)', '910.0', '910.0'])
fill_row(rows(t)[6], ['Enterprise value of SPVs, 100% basis (Rs. crore)', f'{f0(ipo_ev)} (Dec-2020)', f0(tot_ev)])
kill(51, 52)

# =================================================================== S2: portfolio detail (landscape)
P(54, 'Details around the Operational Transmission portfolio – as on 31 March 2026:')
t = E[55]
fill_row(rows(t)[0], [None, None, None, None, None, None, None, None, None, None, None, None, 'Tariff FY27E (Rs. cr p.a. at 98% avail.)', None, None, None, 'EBITDA (% of SPV EBITDA)'])
spec = []
for k, s in enumerate(BY_EV):
    x = spv[s]
    acq = 'May-21'
    spec.append((1, [str(k + 1), s, '100%', d.STATES[s], d.ELEMENTS[s], d.TARIFF_TYPE[s], 'Fixed / Centre', x['cod'].strftime('%b-%Y'), acq,
                     f1(x['op_hist']), f0(x['resid']), f'{FY26AV[s] * 100:.2f}%', f0(x['tariff']), f0(x['ev']), pc(x['ev_sh']), f0(x['ebitda']), pc(x['ebitda_sh'])]))
spec.append((20, ['', 'Sub-total – operational', '', '', f'~{f0(sum(spv[s]["ckm"] for s in SPVS))} ckms; {f0(sum(spv[s]["mva"] for s in SPVS))} MVA', '', '', '', '',
                  f1(avg_op), f1(avg_res), f'{avg_av26 * 100:.2f}%', f0(tot_tar), f0(tot_ev), '100.0%', f'{f0(tot_eb)}*', '100.0%']))
rebuild(t, 1, spec)
P(56, f'* Sum of SPV-level EBITDA; FY27E consolidated EBITDA after Trust-level expenses is Rs. {f0(c27["ebitda"])} crore. FY26 availability as reported by the Trust; VTL includes a 96-hour shutdown for third-party diversion works.')
P(57, [('TBCB', True), (' – Tariff Based Competitive Bidding; ', False), ('BOOM', True), (' – Build, Own, Operate and Maintain; ', False), ('RTM', True), (' – Regulated Tariff Mechanism', False)])
t = E[59]
fill_row(rows(t)[0], [None, None, None, 'Consideration (Rs. crore)', 'Debt raised', 'Paid in cash', 'Unit capital issued', None, None])
spec = [(1, [f'{s} (74%)', 'POWERGRID (Sponsor)', 'May-2021', f0(spv[s]['pp74']), '', '', '', '', '']) for s in BY_EV]
spec += [(1, ['VTL (26%)', 'POWERGRID (Sponsor)', 'Mar-2022', f0(spv['VTL']['pp26']), '', '', '', '', '']),
         (7, ['FY22 – Total', '', '', f0(pp74 + spv['VTL']['pp26']), '576', f0(spv['VTL']['pp26']), '9,100', '100.0', 'IPO (May-2021)*']),
         (8, [''] * 9),
         (9, ['No acquisitions', '', 'FY23', '–', '–', '–', '–', '–', '–']),
         (9, ['No acquisitions', '', 'FY24', '–', '–', '–', '–', '–', '–']),
         (8, [''] * 9)]
spec += [(1, [f'{s} (26%)', 'POWERGRID (Sponsor)', 'Dec-2024', f0(spv[s]['pp26']), '', '', '', '', '']) for s in BY_EV if s != 'VTL']
spec += [(7, ['FY25 – Total', '', '', f0(pp26b), '506', f0(pp26b), '–', '–', 'Term loan (HDFC Bank)']),
         (8, [''] * 9),
         (9, ['No acquisitions', '', 'FY26', '–', '–', '–', '–', '–', '–']),
         (39, ['Grand Total', '', '', f0(pp74 + spv['VTL']['pp26'] + pp26b), '1,082', f0(spv['VTL']['pp26'] + pp26b), '9,100', '–', 'IPO and term loans'])]
rebuild(t, 1, spec)
P(60, '')
footnote(E[59], f'* The 74% stakes were paid for by issuing 410.65 mn units to POWERGRID at Rs. 100; fresh-issue proceeds of Rs. 4,993 crore were lent to the SPVs to repay the Sponsor’s loans of Rs. {f0(debt_sp)} crore. '
      'The balance 26% in KATL, PPTL, WTL and JPTL was bought for Rs. 507 crore against a valuation of Rs. 694 crore.')
kill(range(62, 79))

# =================================================================== S6: milestones
P(79, 'The PGInvIT journey – key milestones since listing')
P(81, 'PGInvIT listed in May 2021 with five TBCB transmission SPVs acquired from its Sponsor and has not added a new asset since. The milestones below are therefore about ownership, financing, governance and distributions rather than portfolio build-out.')
t = E[82]
ms = [('2020', ['•  Trust settled by POWERGRID on 14 September 2020', '•  Investment Management Agreement signed with PUTL (December 2020)']),
      ('2021', ['•  Registered with SEBI as an InvIT (January 2021)', '•  Rs. 7,735 crore IPO at Rs. 100/unit; listed on NSE and BSE on 14 May 2021',
                '•  Acquired 74% in VTL, KATL, PPTL, WTL and JPTL from POWERGRID', '•  Maiden distribution of Rs. 4.50/unit (November 2021)']),
      ('2022', ['•  Acquired balance 26% in VTL for Rs. 331 crore, funded by a 16-year HDFC Bank term loan of Rs. 576 crore (March 2022)',
                '•  Valuer changed from RBSA to INMACS; WACC reset to 9.01% and NAV fell to Rs. 86.0']),
      ('2023', ['•  HDFC loan spread cut by 67 bps in two steps to T-bill + 127 bps', '•  Units included in the Nifty REITs & InvITs Index']),
      ('2024', ['•  KATL 125 MVAr bus reactor commissioned under RTM (February 2024)',
                '•  Acquired balance 26% in KATL, PPTL, WTL and JPTL for Rs. 507 crore, funded by a Rs. 506 crore term loan – Trust now owns 100% of all SPVs']),
      ('2025', ['•  SPVs renamed, dropping the “POWERGRID” prefix', '•  In-principle approval for a consortium with POWERGRID (PGInvIT 74%) to bid for up to two TBCB projects (~Rs. 500 crore)',
                '•  PPTL 400 kV line bay (RTM) charged on schedule (December 2025)']),
      ('2026', ['•  FY26 DPU of Rs. 12.00 – fourth consecutive year at Rs. 12; FY27 guidance of Rs. 12.00', '•  New CEO (June 2026); IndiaAppraisers appointed valuer for FY27–FY28 (August 2026)'])]
rebuild(t, 1, [(1, [y, lines]) for y, lines in ms])

# =================================================================== S7: growth, NAV, DPU
P(86, 'Portfolio growth since listing – FY22 to FY26')
P(87, 'The table below tracks scale, earnings, leverage and the distribution record across the five years since listing, with the commentary that follows drawing out the main movements.')
t = E[88]
delete_grid_cols(t, [1, 2, 3, 4])
yrs = list(range(2022, 2027))
H = hist


def row(label, vals):
    return [label] + vals


aum = [H[y]['aum'] for y in yrs]
navs = [H[y]['nav'] for y in yrs]
vals = [
    row('AUM (Rs. crore)', [f0(x) for x in aum]),
    row('AUM growth (%)', ['–'] + [pc(aum[i] / aum[i - 1] - 1, 0) for i in range(1, 5)]),
    row('No. of operational assets', ['5'] * 5),
    row('Assets added during the year', ['5', '–', '–', '–', '–']),
    row('Revenue from operations (Rs. crore)', [f0(H[y]['rev']) for y in yrs]),
    row('EBITDA (Rs. crore)', [f0(H[y]['ebitda']) for y in yrs]),
    row('Net debt / AUM (%)', [pc(H[y]['netdebt'] / H[y]['aum']) for y in yrs]),
    row('NAV per unit (Rs.)', [f1(x) for x in navs]),
    row('NAV growth (%)', ['+1.1%'] + [('+' if navs[i] >= navs[i - 1] else '') + pc(navs[i] / navs[i - 1] - 1) for i in range(1, 5)]),
    row('Distribution (Rs. crore)', [f0(H[y]['dist']) for y in yrs]),
    row('DPU (Rs./unit)', [f2(H[y]['dpu']) for y in yrs])]
for tr, v in zip(rows(t)[1:], vals):
    fill_row(tr, v)
mg = [H[y]['ebitda'] / H[y]['rev'] for y in yrs]
lead(90, f'AUM has declined since listing, from Rs. {f0(aum[0])} crore at 31 March 2022 to Rs. {f0(aum[-1])} crore at 31 March 2026 – a {pc(1 - aum[-1] / aum[0], 0)} fall. '
      'This is what a closed portfolio of finite-life contracts looks like: every year one more year of contracted cash flow is paid out and nothing is added to replace it. '
      'The path has also been distorted by valuation inputs rather than operations. The 16% drop in FY23 was almost entirely the valuer change and a higher WACC, and the 6% rise in FY25 came from a methodology-led cut in WACC to 8.0%, not from any new asset.')
lead(91, f'Revenue has been flat by design, at roughly Rs. 1,260–1,290 crore a year since FY23 (FY22 covers only 13 May 2021 to 31 March 2022). Tariffs are fixed at bid, so revenue moves only with availability incentives and the quoted tariff profile. '
      'The scheduled step-down in VTL’s quoted charges took about Rs. 40 crore out of revenue between FY22 and FY24, offset by full-year consolidation and change-in-law increments at PPTL, WTL and JPTL.')
lead(92, f'EBITDA margins are among the highest in the sector. EBITDA was Rs. {f0(H[2026]["ebitda"])} crore in FY26, a {pc(mg[-1])} margin, and margins have stayed within {pc(min(mg), 0)}–{pc(max(mg), 0)} throughout. '
      'Operating costs are small and largely contractual – O&M and project management fees paid to POWERGRID and a fixed Investment Manager fee – so there is little operating leverage either way.')
lead(93, 'The portfolio has not changed since listing. The asset count has stayed at five and the network at ~3,699 ckm and 6,630 MVA. The only change has been in ownership: the Trust’s economic interest rose from 74% to 100% through the VTL purchase in March 2022 and the purchase of the other four in December 2024, both debt-funded and both from the Sponsor. '
      'Management has acknowledged that acquisition opportunities are limited and that POWERGRID currently prefers securitisation over further InvIT monetisation.')
lead(94, f'Leverage is negligible. Net debt / AUM was below 1% until FY24 and rose to ~{pc(H[2026]["netdebt"] / H[2026]["aum"], 0)} after the December 2024 term loan. Gross borrowings of Rs. {f0(H[2026]["debt"])} crore compare with a 70% regulatory ceiling, '
      'leaving the Trust a large debt capacity it has so far had no use for. All borrowings are floating-rate (T-bill and repo linked), at an average cost of 6.97% in FY26.')
lead(95, f'NAV per unit has eroded rather than compounded. NAV per unit moved from Rs. 101.1 in FY22 to Rs. {f1(navs[-1])} in FY26, with the large swings driven by valuation inputs. '
      f'DPU, by contrast, has been held flat at Rs. 12.00 every year since FY23, after Rs. 10.50 for the shortened FY22. Aggregate distributions were Rs. {f0(H[2026]["dist"])} crore in FY26, and cumulative distributions since listing have reached Rs. {f2(d.total_dist)} per unit, including the Q1 FY27 payout. '
      'A meaningful share of each DPU is repayment of SPV debt – return of capital rather than income – which is why NAV falls as distributions are paid.')
# NAV drivers
anchor = E[96]
L1, LH, SB = 97, 98, 99   # one-liner, label-only, sub-bullet prototypes
items = [
    ('one', 'FY22 (Rs. 101.1/unit, +1.1% on the Rs. 100 issue price): ', 'The first valuation (RBSA, WACC 7.7%–8.0%) put SPV enterprise value at Rs. 10,230 crore, close to the IPO pricing. No units were issued after the IPO, so per-unit value simply reflected the asset marks.'),
    ('lab', 'FY23 (Rs. 86.0/unit, -14.9%): ', None),
    ('sub', None, 'The valuer changed from RBSA to INMACS, and the new WACC build (comparable-company beta, country-risk-adjusted equity risk premium) took WACC to 9.01% from 7.7%–8.0%.'),
    ('sub', None, 'SPV enterprise value fell from Rs. 10,230 crore to Rs. 8,546 crore and a consolidated impairment of ~Rs. 1,510 crore was booked. It was non-cash, with no effect on distributions, but it reset the NAV base permanently.'),
    ('one', 'FY24 (Rs. 85.3/unit, -0.9%): ', 'WACC eased only slightly to 8.79%, so the modest uplift in the marks was outweighed by another year of cash flows paid out of a finite-life asset base.'),
    ('lab', 'FY25 (Rs. 94.1/unit, +10.4%): ', None),
    ('sub', None, 'The valuer changed its methodology – a five-year POWERGRID beta, 70:30 target leverage and an AAA-based cost of debt – which cut WACC to 8.00% and reversed a large part of the FY23 impairment.'),
    ('sub', None, 'The balance 26% in four SPVs was bought for Rs. 507 crore against a valuation of Rs. 694 crore, fully debt-funded with no new units, so the discount accrued entirely to existing unitholders.'),
    ('lab', 'FY26 (Rs. 90.8/unit, -3.5%): ', None),
    ('sub', None, 'WACC was unchanged at 8.00%, so the decline is the underlying run-off: enterprise value fell from Rs. 9,004 crore to Rs. 8,672 crore as one more year of contracted cash flow was distributed.'),
    ('sub', None, 'A new valuer (IndiaAppraisers) takes over from FY27. Given the history, the first H1 FY27 valuation is a near-term source of NAV volatility in either direction.'),
]
prev = anchor
for kind, lab, txt in items:
    if kind == 'one':
        prev = add_after(L1, prev, [(lab, True), (txt, False)])
    elif kind == 'lab':
        prev = add_after(LH, prev, [(lab, True)])
    else:
        prev = add_after(SB, prev, [(txt, False)])
kill(range(97, 115))
# DPU composition
t = E[116]
byfy = {}
for q, qd, dpu, i_, dv, rp, tr_ in d.dist_q:
    fy = 2000 + int(q[-2:])
    a = byfy.setdefault(fy, [0, 0, 0, 0, 0])
    for k, x in enumerate((i_, dv, rp, tr_, dpu)):
        a[k] += x or 0
spec = [(1, [f'FY{y % 100}' if y < 2027 else 'FY27 (Q1)'] + [f1(x) for x in byfy[y]]) for y in sorted(byfy)]
tot = [sum(byfy[y][k] for y in byfy) for k in range(5)]
spec.append((11, ['Total (incl. Q1 FY27)'] + [f1(x) for x in tot]))
rebuild(t, 1, spec)
P(121, f'The units listed at a premium to NAV and have swung either side of it since. On an average-price basis the premium was widest in FY23 at {pc(d.fy_avg["FY23"] / 86.04 - 1)} – when the valuation reset cut NAV faster than the price – and the units moved to a discount in FY25 as the market priced in the tariff step-down. '
      f'At the current market price the units trade at a {pc(prem)} premium to the March 2026 NAV of Rs. {f2(hist[2026]["nav"])}.')
t = E[122]
delete_grid_cols(t, [1, 2, 3, 4])
mp = [d.fy_avg[f'FY{y % 100}'] for y in yrs] + [d.fy_avg['FY27 YTD']]
nv = navs + [hist[2026]['nav']]
fill_row(rows(t)[1], [None] + [f1(x) for x in mp])
fill_row(rows(t)[2], [None] + [f1(x) for x in nv])
fill_row(rows(t)[3], [None] + [pc(a / b - 1, 1, True) for a, b in zip(mp, nv)])

# =================================================================== S8: unitholding, ratings
UH = G['1_unitholding_pattern']
dates = ['2022-03-31', '2023-03-31', '2024-03-31', '2025-03-31', '2026-03-31']


def u(k):
    return [UH[x].get(k) or 0 for x in dates]


def ps(v):
    return [f'{x:.2f}%' for x in v]


def addv(*vs):
    return [sum(t) for t in zip(*vs)]


cat4 = ['foreign_portfolio_investors', 'financial_institutions_banks', 'alternative_investment_funds', 'bodies_corporate_institutional']
cat6 = ['bodies_corporate_non_institutional', 'nbfcs', 'trusts', 'clearing_members']
t = E[127]
spec = [(1, ['1', 'Sponsor'] + ps(u('sponsor'))), (2, ['', 'Power Grid Corporation of India Limited'] + ps(u('sponsor'))),
        (3, ['2', 'Mutual Fund'] + ps(u('mutual_funds'))), (4, ['', 'Mutual funds'] + ps(u('mutual_funds'))),
        (5, ['3', 'Insurance Company'] + ps(addv(u('insurance_companies'), u('provident_pension_funds')))),
        (6, ['', 'Insurance companies'] + ps(u('insurance_companies'))), (7, ['', 'Provident / pension funds'] + ps(u('provident_pension_funds'))),
        (8, ['4', 'Other Institutional Investors'] + ps(addv(*[u(k) for k in cat4]))),
        (9, ['', 'Foreign portfolio investors (incl. CPP Investments until FY25)'] + ps(u(cat4[0]))), (10, ['', 'Financial institutions / banks'] + ps(u(cat4[1]))),
        (11, ['', 'Alternative investment funds'] + ps(u(cat4[2]))), (11, ['', 'Bodies corporate – institutional'] + ps(u(cat4[3]))),
        (12, ['5', 'Individuals'] + ps(addv(u('individuals'), u('nris')))), (13, ['', 'Individuals'] + ps(u('individuals'))), (14, ['', 'Non-resident Indians'] + ps(u('nris'))),
        (15, ['6', 'Body Corporate and others'] + ps(addv(*[u(k) for k in cat6]))),
        (16, ['', 'Bodies corporate'] + ps(u(cat6[0]))), (17, ['', 'NBFCs registered with RBI'] + ps(u(cat6[1]))), (18, ['', 'Trusts'] + ps(u(cat6[2]))),
        (19, ['', 'Clearing members'] + ps(u(cat6[3]))), (20, ['Total', ''] + ['100%'] * 5)]
rebuild(t, 1, spec)
fill_row(rows(E[129])[1], ['Power Grid Corporation of India Limited (Sponsor)', '100.0%'])
P(130, 'Shareholding Pattern of the Project Manager (POWERGRID)')
t = E[131]
fill_row(rows(t)[1], ['President of India (Government of India)', '51.3%'])
new = clone_row(t, 1)
fill_row(new, ['Public and institutional shareholders', '48.7%'])
t = E[135]
fill_row(rows(t)[1], [None, 'Power Grid Corporation of India Limited', 'CRISIL AAA / Stable; CRISIL A1+', 'ICRA AAA (Stable); ICRA A1+', 'CARE AAA; Stable; CARE A1+', '-'])
fill_row(rows(t)[2], [None, 'POWERGRID Infrastructure Investment Trust', 'CRISIL AAA / Stable', 'ICRA AAA (Stable)', 'CARE AAA; Stable', '-'])
fill_row(rows(t)[3], [None, 'POWERGRID Unchahar Transmission Limited', '-', '-', '-', '-'])

# =================================================================== S9: sponsor, board, management
sp = V['sponsor']
P(140, [('POWERGRID. ', True), (f'Power Grid Corporation of India Limited was incorporated in 1989 and is a Schedule ‘A’ Maharatna CPSE, listed on the NSE and BSE with a market capitalisation of ~Rs. 2.4 lakh crore. '
                              f'It operates ~1.88 lakh ckm of transmission lines and 294 substations with ~6.6 lakh MVA of transformation capacity, carries ~84% of India’s inter-regional transfer capacity, and reported FY26 consolidated revenue of Rs. {f0(sp["fy26_consolidated"]["revenue_from_operations_rs_cr"])} crore and PAT of Rs. {f0(sp["fy26_consolidated"]["pat_rs_cr"])} crore. '
                              'It is rated AAA by CRISIL, ICRA and CARE. Its role in PGInvIT is threefold – Sponsor, Project Manager and 100% owner of the Investment Manager – while its economic interest is limited to the 15% minimum unitholding. '
                              'POWERGRID is investing ~Rs. 35,000–40,000 crore a year in new transmission capacity, so PGInvIT is a small, mature corner of its business, and management has said the Sponsor currently prefers securitisation to further InvIT monetisation.', False)])
P(141, [('Government of India. ', True), ('The Government holds 51.34% of POWERGRID and, through the Ministry of Power, appoints the independent directors on the Investment Manager’s board. '
                                        'Trust governance therefore runs through the public-sector framework: board vacancies wait on ministry orders, and the consortium with POWERGRID to bid for TBCB projects, approved by both boards in 2025, was still awaiting Government approval as of May 2026. '
                                        'The Investment Manager’s board is currently below the SEBI requirement for independent directors (two independent against three non-independent), under a SEBI relaxation extended to 31 December 2026.', False)])
P(142, 'Board of Directors – POWERGRID Unchahar Transmission Limited')
board = [('Shri Naveen Srivastava', 'Chairman; Non-Executive, Non-Independent (POWERGRID)', 'Director (Operations), POWERGRID; ~36 years in transmission O&M and construction; B.Tech (Hons), NIT Durgapur'),
         ('Shri Sanjay Sharma', 'Non-Executive, Non-Independent (POWERGRID)', 'Executive Director (Corporate Planning), POWERGRID; former CEO of PGInvIT; 33+ years'),
         ('Shri Amit Garg', 'Non-Executive, Non-Independent (POWERGRID)', 'Chief General Manager, POWERGRID; CFO of PGInvIT from inception to October 2024; 29 years in corporate finance'),
         ('Dr. Anupam Arora', 'Independent Director', 'Appointed by the Government of India from May 2025; chairs the Audit Committee; PhD in nuclear physics and principal of a post-graduate college'),
         ('Smt. Anita Soren', 'Independent Director', 'Appointed by Ministry of Power order from July 2026; chairs the Nomination & Remuneration and Stakeholders’ Relationship Committees')]
rebuild(E[143], 1, [(2, list(b)) for b in board])
mgmt = [('Shri K. Nagraj Bhat', 'Chief Executive Officer', 'Appointed 23 June 2026. Joined POWERGRID in 1993; Chief General Manager with experience across commercial, O&M, corporate planning and multilateral financing'),
        ('CA Gaurav Malik', 'Chief Financial Officer', 'Since October 2024. Chartered Accountant with ~25 years of experience; previously DGM (Finance), POWERGRID'),
        ('Shri Shwetank Kumar', 'Company Secretary and Compliance Officer', 'Since August 2024. 21+ years of experience; previously DGM (Company Secretariat), POWERGRID')]
rebuild(E[145], 1, [(1, list(m)) for m in mgmt])

# =================================================================== S10: revenue
P(150, 'All five SPVs have a long record of high line availability. Their revenue is driven by their TSAs, which guarantee the quoted transmission charges subject to a normative annual availability of 98%, with an incentive of 2% of charges for each percentage point above 98%, capped at 99.75%. '
       'Availability has been above 99.5% at every SPV in every year since listing, and between 99.87% and 100.00% in FY2026. As a result, the portfolio has earned close to the maximum incentive almost every year.')
_unused = ('The revenue of a transmission SPV is completely delinked from the power demand-supply situation and volatility in electricity prices. Moreover, factors affecting line availability, such as unchecked vegetation, lightning or high ambient temperature causing wear and tear of insulators leading to flashovers, are routine and do not entail significant cost and are easily rectifiable, thereby minimising outage time. Furthermore, any outage due to extreme weather conditions, cyclones or excessive lightning is usually classified as an act of God and is covered under the force majeure clause of the TSA and thus does not impact line availability.')
P(152, 'The flip side of fixed tariffs is that revenue can only move down. Under the bid tariff profile, the quoted non-escalable charges of PPTL, WTL and JPTL fall by roughly 30% from contract year 11. '
       f'The Independent Valuer’s projections place this in FY2028, taking consolidated revenue from ~Rs. {f0(c27["rev"])} crore in FY27E to ~Rs. {f0(c28["rev"])} crore in FY28E (-{pc(1 - c28["rev"] / c27["rev"], 0)}), which is consistent with management’s own guidance of a 23–24% decline.')
P(153, 'Within the operating fleet the portfolio is flat to declining by design, since availability-linked tariffs are fixed at bid and step down on a defined schedule, and the Trust has made no third-party acquisitions to offset it.')
t = E[155]
delete_grid_cols(t, [1, 8, 15])
rs = rows(t)
spec = [(2, None)]
yrs5 = list(range(2022, 2027))
for s in d.BY_REV:
    rv = [spv[s]['rev'][y] for y in yrs5]
    shares = [spv[s]['rev'][y] / hist[y]['rev'] for y in yrs5]
    g = [rv[i] / rv[i - 1] - 1 for i in range(1, 5)]
    spec.append((3, [s] + [f0(x) for x in rv] + [''] + [pc(x, 0) for x in shares] + [''] + [pc(x, 0) for x in g]))
spec.append((54, ['Total reported revenue'] + [f0(hist[y]['rev']) for y in yrs5] + [''] + ['100%'] * 5 + [''] +
             [pc(hist[yrs5[i]]['rev'] / hist[yrs5[i - 1]]['rev'] - 1, 0) for i in range(1, 5)]))
protos = {p: copy.deepcopy(rs[p]) for p, _ in spec}
for r_ in rs[2:]:
    t.remove(r_)
for p, v in spec:
    n = copy.deepcopy(protos[p])
    t.append(n)
    if v:
        fill_row(n, v)
P(156, 'Reason for growth and De-growth in Revenue – SPV Wise:')
t = E[157]
reasons = {
    'WTL': ('FY 2023 – first full year of consolidation (FY 2022 covers 13 May 2021 to 31 March 2022) and change-in-law increment of 3.445%', 'FY 2024–26 – flat by design; quoted charges constant at Rs. 352 crore p.a. until July 2027'),
    'PPTL': ('FY 2023 – first full year of consolidation and change-in-law increment of 2.787%', 'FY 2024–26 – flat by design; quoted charges constant at Rs. 317 crore p.a. until June 2027'),
    'JPTL': ('FY 2023 – change-in-law increment of 5.226% from March 2022', 'FY 2024–26 – flat by design; quoted charges constant at Rs. 244 crore p.a.'),
    'VTL': ('–', 'FY 2023–24 – scheduled step-down in quoted charges (Rs. 290 crore in contract year 2021 to Rs. 208 crore in 2024)'),
    'KATL': ('FY 2025 – RTM bus reactor (commissioned February 2024) added regulated tariff', 'FY 2026 – quoted charges stepped down from Rs. 65 crore to Rs. 57 crore (July 2025 contract year)'),
}
def fy_segs(txt):
    k = txt.find(' – ')
    return [[(txt[:k], True), (txt[k:], False)]] if k > 0 and txt.startswith('FY') else txt
proto = rows(t)[2]
ref = cells(proto)[3].find(W('p'))
for tc in cells(proto)[1:3]:
    for p_ in tc.findall(W('p')):
        tc.remove(p_)
    tc.append(copy.deepcopy(ref))
spec = [(1, None)] + [(2, [s, [[(d.STATES[s], False)]], fy_segs(reasons[s][0]), fy_segs(reasons[s][1])]) for s in d.BY_REV]
rs = rows(t)
protos = {p: copy.deepcopy(rs[p]) for p, _ in spec}
for r_ in rs[1:]:
    t.remove(r_)
for p, v in spec:
    n = copy.deepcopy(protos[p])
    t.append(n)
    if v:
        fill_row(n, v)
P(158, 'Strong payment security for inter-state transmission assets')
P(159, 'All five transmission projects are part of the inter-state transmission system, which enjoys strong payment security. The Central Transmission Utility of India Limited (CTUIL) raises bills and collects payments from all designated ISTS customers under the CERC Sharing Regulations, 2020, and pays licensees their share from the pooled collections. '
       'No SPV has a direct counterparty exposure to any single state distribution utility.')

# =================================================================== S11: counterparty
t = E[162]
delete_grid_cols(t, [1])
fill_row(rows(t)[1], ['Centre (CTU pool)'] + [f0(hist[y]['rev']) for y in yrs5])
fill_row(rows(t)[4], ['Total – transmission'] + [f0(hist[y]['rev']) for y in yrs5])
fill_row(rows(t)[5], ['% Centre'] + ['100.0%'] * 5)
delete_rows(t, [2, 3, 6, 7])
kill(163, 164)
P(166, 'Availability-linked payments under long-term TSAs for transmission assets')
P(168, f'All the transmission SPVs under PGInvIT have low revenue risk, with availability-linked payments under 35-year TSAs signed with the long-term transmission customers. The tariff in the TSAs is fixed (non-escalable) for all five SPVs, with small regulated (RTM) elements at KATL and PPTL. '
       f'The average residual tenure of the TSAs is ~{avg_res:.1f} years, ranging from {min(spv[s]["resid"] for s in SPVS):.1f} years at VTL to {max(spv[s]["resid"] for s in SPVS):.1f} years at JPTL. Because the assets are held on a BOOM basis, they remain with the SPVs after the TSA term.')
P(170, 'Stable performance of assets under PGInvIT')
P(172, 'The line availability for the operational transmission assets remains healthy and above the normative level of 98% for every SPV in every year since listing. FY2026 availability ranged from 99.87% at JPTL to 100.00% at VTL, which included a 96-hour shutdown for third-party diversion works. '
       'O&M is carried out by POWERGRID using preventive maintenance, OEM support and digital asset monitoring. A stable operating performance translates into healthy cash flow in the form of monthly tariffs and incentives for the transmission assets.')
t = E[175]
spec = [(1, None)]
for s in BY_EV:
    av = [spv[s]['avail'].get(f'FY{y}') for y in range(21, 27)]
    spec.append((2, [s] + [f'{x * 100:.2f}%' for x in av] + [f'{sum(av) / 6 * 100:.2f}%']))
rs = rows(t)
protos = {p: copy.deepcopy(rs[p]) for p, _ in spec}
for r_ in rs[1:]:
    t.remove(r_)
for p, v in spec:
    n = copy.deepcopy(protos[p])
    t.append(n)
    if v:
        fill_row(n, v)
footnote(E[175], 'FY2021 is pre-listing (as disclosed in the offer document); FY2026 as reported by the Trust.')

# =================================================================== S13: collections, O&M, debt, returns, projections, peers
P(179, 'All SPVs under PGInvIT are ISTS licensees and fall under the national pool mechanism, in which CTUIL collects monthly transmission charges from all designated ISTS customers on behalf of the licensees and pays each licensee its share from the pooled collections. '
       'This diversifies counterparty risk, since a default or delay by any one customer is spread across all ISTS licensees. The CTU has maintained strong collection efficiency – 101% in FY2024 and 104.5% in FY2025 – reflecting its high bargaining power.')
P(180, 'Receivable days have fallen steadily, from 43 days in FY2022 and 47 days in FY2023 to 25 days in FY2025 and 19 days in FY2026, with billed receivables of Rs. 65 crore at 31 March 2026.')
P(181, 'Payment discipline across the sector has also improved since the Electricity (Late Payment Surcharge and Related Matters) Rules, 2022, which allow supply to be regulated for distribution utilities that default, strengthening the pool from which ISTS licensees are paid.')
P(183, [('First-year O&M: ', True), ('O&M is performed by POWERGRID under O&M agreements with each SPV. Charges paid to POWERGRID, including taxes, were Rs. 33.3 crore in FY2026 (Rs. 32.2 crore in FY2025) – under 3% of revenue.', False)])
P(184, [('Escalation: ', True), ('O&M charges escalate at 3.51% a year under the O&M agreements (the Independent Valuer’s basis). The project manager fee under the PIMA is 15% of aggregate O&M fees, and the Investment Manager fee is Rs. 7.25 crore a year for the initial SPVs, escalating at 6.75% a year.', False)])
P(185, [('Contract renewal: ', True), ('The running O&M contract with POWERGRID was valid until March 2026 and is to be renewed on terms linked to CERC O&M norms. The last extension was on unchanged terms, but the renewal is a related-party contract worth tracking.', False)])
P(186, [('Sponsor dependence: ', True), ('POWERGRID’s ~1.88 lakh ckm network gives the Trust access to spares, crews and protection expertise that a standalone owner of five assets could not afford – the main reason availability has been close to 100%.', False)])
P(187, 'Healthy debt coverage metrics ')
P(188, f'PGInvIT’s financial risk profile is very strong, evident from its negligible leverage. Net debt/AUM was ~{pc(nd26 / tot_ev, 0)} as on March 31, 2026, against the 70% regulatory ceiling. '
       'Leverage has headroom to rise sharply if the Trust finds acquisitions, which management has said will be predominantly debt-funded.')
P(189, f'Gross borrowings stood at Rs. {f0(H[2026]["debt"])} crore as on 31 March 2026, against AUM of Rs. {f0(tot_ev)} crore. The book consists of two 16-year secured rupee term loans from HDFC Bank: Rs. 561 crore linked to the 3-month T-bill (T-bill + 127 bps, drawn March 2022) and Rs. 503 crore linked to the RBI repo rate (repo + 150 bps, drawn December 2024). '
       'Both are 100% floating, the average cost of debt was 6.97% in FY2026, ~73% of principal is repayable after ten years, and the Trust and the loan facility carry AAA ratings.')
P(190, 'Borrowings, leverage and AUM – FY22 to FY26')
t = E[191]
delete_grid_cols(t, [1, 2, 3, 4])
q1d = 1061.96
fill_row(rows(t)[1], [None] + [f0(H[y]['debt']) for y in yrs] + [f0(q1d)])
fill_row(rows(t)[2], [None, '<6.0%', '7.20%', '8.18%*', '7.92%', '6.97%', '~6.7%'])
fill_row(rows(t)[3], [None] + [f0(H[y]['netdebt']) for y in yrs] + [''])
fill_row(rows(t)[4], [None] + [f0(H[y]['aum']) for y in yrs] + [''])
fill_row(rows(t)[5], [None] + [pc(H[y]['netdebt'] / H[y]['aum']) for y in yrs] + ['5.1%'])
footnote(E[191], '* H1 FY24 average; full-year FY24 average not disclosed. FY22 cost is the rate at drawdown.')
t = E[194]
fill_row(rows(t)[1], ['Term loans – HDFC Bank', '100%'])
fill_row(rows(t)[2], ['Tranche 1 – 3-month T-bill + 127 bps (Mar-2022)', '53%'])
fill_row(rows(t)[3], ['Tranche 2 – Repo + 150 bps (Dec-2024)', '47%'])
fill_row(rows(t)[9], ['Total gross borrowings', '100%'])
delete_rows(t, [4, 5, 6, 7, 8])
# holding period returns
t = E[197]
spec = [(1, ['Listing Price', d.LIST_DATE.strftime('%d-%b-%y'), '(100.00)', '(100.00)'])]
for q, qd, dpu, *_ in d.dist_q:
    lab = f'Distribution per Unit – Q{q[0]} FY20{q[-2:]}'
    if q == '2QFY22':
        lab = 'Distribution per Unit – H1 FY2022'
    spec.append((2, [lab, qd.strftime('%d-%b-%y'), f2(dpu), '']))
spec.append((39, ['Latest Price', d.LATEST.strftime('%d-%b-%y'), f2(d.PRICE), f2(d.PRICE)]))
rebuild(t, 1, spec)
fill_row(rows(E[199])[1], [None, pct(d.ret_total), pct(d.ret_cap), pct(d.ret_dist)])
# assumptions
t = E[202]
delete_grid_cols(t, [2, 3])
fill_row(rows(t)[1], [None, 'Availability-linked TSA tariff (quoted non-escalable charges)'])
fill_row(rows(t)[2], ['Availability – FY27E onwards', '99.75% (incentive cap) for all SPVs'])
fill_row(rows(t)[3], [None, 'Contracted TSA schedule, incl. ~30% step-down at PPTL, WTL and JPTL in FY28'])
fill_row(rows(t)[4], [None, 'O&M 3.51% p.a.; Investment Manager fee 6.75% p.a.'])
fill_row(rows(t)[5], [None, '8.0% WACC (Independent Valuer, March 2026)'])
t = E[205]
py = list(range(2027, 2032))
cc = [cons[y] for y in py]
fill_row(rows(t)[1], ['NDCF before capex and debt repayment'] + [f0(c['ndcf'] - c['capex'] - c['debtflow']) for c in cc])
fill_row(rows(t)[2], [None] + [f'({f0(-c["capex"])})' for c in cc])
fill_row(rows(t)[3], ['Less: debt repayment'] + [f'({f0(-c["debtflow"])})' for c in cc])
fill_row(rows(t)[4], [None] + [f0(c['ndcf']) for c in cc])
fill_row(rows(t)[5], [None] + ['–'] * 5)
fill_row(rows(t)[6], [None] + [f0(c['cash_avail']) for c in cc])
fill_row(rows(t)[7], [None] + [pc(c['dpu_g']) for c in cc])
fill_row(rows(t)[8], [None] + [f2(c['dpu']) for c in cc])
fill_row(rows(t)[9], [None] + [f0(c['actual']) for c in cc])
fill_row(rows(t)[10], ['Net cash (drawn from reserves)'] + [d.neg0(c['cash_avail'] - c['actual']) if abs(c['cash_avail'] - c['actual']) > 0.5 else '–' for c in cc])
# peers: reorder to PGInvIT | IndiGrid | Anzen and refresh market data
t = E[208]
for tr in rows(t):
    cs = cells(tr)
    if len(cs) == 4:
        a, b = cell_text(cs[1]), cell_text(cs[2])
        set_cell(cs[1], b)
        set_cell(cs[2], a)
upd = {  # row: (PG, IndiGrid, Anzen)
    3: ('15.00% (Mar-26)', None, None),
    4: ('POWERGRID Unchahar Transmission Limited (100% POWERGRID)', None, None),
    10: ('910.0', '952.6', '336.1'),
    21: (f0(hist[2026]['rev'] + 38.6), None, None),
    24: (f0(hist[2026]['ndcf']), None, None),
    27: (f0(d.mcap), f0(172.55 * 95.256), f0(129.50 * 33.606)),
    29: (f2(d.PRICE), '172.55', '129.50'),
    30: (pc(prem), pc(172.55 / 148.24 - 1), pc(129.50 / 124.78 - 1)),
    31: (f0(H[2026]['debt']), None, None),
    32: (pc(nd26 / tot_ev), None, None),
    33: ('~6.97% (FY26)', None, None),
    37: ('12.00', None, None),
    38: (f2(d.total_dist) + ' (to Q1 FY27)', None, None),
    39: (pct(d.ret_dist), None, None),
    40: (pct(d.ret_cap), None, None),
    41: (pct(d.ret_total), None, None),
    43: ('Consortium with POWERGRID (PGInvIT 74%) to bid for up to 2 TBCB projects (~Rs. 500 crore), awaiting Government approval; no acquisition since IPO', None, None),
}
rs = rows(t)
fill_row(rs[0], [None, 'POWERGRID Infrastructure Investment Trust', 'IndiGrid Infrastructure Trust'])
for k, vals in upd.items():
    fill_row(rs[k], [None] + list(vals))
fill_row(rs[27], ['Market capitalisation (Rs. crore, 09-Nov-26)'])
fill_row(rs[29], ['CMP (Rs. per unit, 09-Nov-26)'])

# =================================================================== key arguments / risks / monitorables
args = [
    ('Contracted, availability-linked revenue with no volume or price exposure. ',
     f'All five SPVs are inter-state TBCB assets on 35-year TSAs, earning quoted charges against a 98% normative availability rather than against power flow. FY2026 availability of 99.87%–100.00% earned close to the maximum incentive. '
     f'Revenue is insensitive to power demand, merchant tariffs and the economic cycle, and the average residual contract life is ~{avg_res:.0f} years.'),
    ('Sovereign-linked sponsor and a AAA balance sheet with almost no debt. ',
     f'POWERGRID (51.34% Government-owned) is Sponsor, Project Manager and owner of the Investment Manager, and the Trust is rated AAA by CRISIL, ICRA and CARE. Net debt is ~{pc(nd26 / tot_ev, 0)} of AUM against a 70% ceiling, leaving debt capacity of ~Rs. 3,000 crore even at a 49% ratio – enough to fund a sizeable acquisition without issuing units.'),
    ('Counterparty risk is pooled, not negotiated. ',
     'Revenue is billed and collected by CTUIL through the national ISTS pool, so no SPV depends on a single state utility. Collection efficiency was 101%–104.5% in FY2024–FY2025, and receivable days have fallen from 43 in FY2022 to 19 in FY2026.'),
    ('A high current yield backed by an unbroken distribution record. ',
     f'The Trust has paid 20 consecutive distributions totalling Rs. {f2(d.total_dist)} per unit since listing, with DPU held at Rs. 12.00 for four straight years and guided at Rs. 12.00 for FY2027 – an {pct(dy)} yield at the current price. Since listing, the units have delivered an annualised total return of {pct(d.ret_total)}, almost all of it from distributions.'),
    ('Optionality from acquisitions and the TBCB consortium – but only optionality. ',
     'A consortium with POWERGRID to bid for up to two TBCB projects (~Rs. 500 crore) has board approvals, and management reports talks with two or three private owners. Combined with the balance-sheet headroom, a single sizeable acquisition would change the DPU outlook. In five years, however, none has been executed, so we ascribe no value to it.'),
]
for i, (lead, txt) in zip(range(212, 217), args):
    P(i, [(lead, True), (txt, False)])
risks = [
    ('Contracted tariff step-down from FY2028 – ', f'the largest single risk. Quoted charges at PPTL, WTL and JPTL fall by ~30% from contract year 11, taking consolidated revenue from ~Rs. {f0(c27["rev"])} crore in FY27E to ~Rs. {f0(c28["rev"])} crore in FY28E. On our model, NDCF falls to ~Rs. {f0(c28["ndcf"])} crore and DPU to ~Rs. {f2(c28["dpu"])} in FY28E (from Rs. 12.00), declining gradually thereafter. Management has said that Rs. 12 cannot be maintained without new assets.'),
    ('No acquisitions since listing – ', 'the Sponsor has no right-of-first-offer pipeline for the Trust and has stated a preference for securitisation over InvIT monetisation. Third-party operating assets have been scarce and keenly priced, and the TBCB consortium still awaits Government approval.'),
    ('Low hold-to-maturity return at the current price – ', f'at Rs. {f1(d.PRICE)} the units trade at a {pc(prem)} premium to NAV, and our hold-to-maturity XIRR is only {pct(irr)}, below the 7.16% risk-free rate used by the Independent Valuer. Without acquisitions, today’s yield overstates the long-run return because part of each distribution is return of capital on a finite-life asset base.'),
    ('Floating-rate debt – ', 'all borrowings are linked to the 3-month T-bill or the repo rate. The book is small, so a 100 bps rise costs only ~Rs. 11 crore a year (~Rs. 0.12 per unit), but any debt-funded acquisition would raise this exposure materially.'),
    ('Valuation volatility from valuer changes – ', 'NAV moved from Rs. 101.1 to Rs. 86.0 and back to Rs. 94.1 largely because of changes in valuer and WACC methodology, with impairments and reversals of over Rs. 1,000 crore. A new valuer takes over from FY2027.'),
    ('Related-party concentration – ', 'the Sponsor is also the Project Manager, O&M contractor, owner of the Investment Manager and the seller of every asset the Trust owns. The O&M contract renewal due from March 2026 and the pricing of any future Sponsor transaction need scrutiny.'),
    ('Governance – ', 'the Investment Manager’s board is below the SEBI independent-director requirement, operating under a relaxation extended to 31 December 2026, and appointments depend on Ministry of Power orders.'),
]
keep_r = list(range(219, 219 + len(risks)))
for i, (lead, txt) in zip(keep_r, risks):
    P(i, [(lead, True), (txt, False)])
kill(range(219 + len(risks), 228))
mons = [
    ('FY2028 distribution guidance – ', 'whether management guides to a lower DPU for FY2028 or uses reserves and debt to bridge the step-down, and whether NDCF covers the distribution without drawing down reserves.'),
    ('Acquisitions and the TBCB consortium – ', 'Government approval for the consortium with POWERGRID, the first bid outcome, and any third-party or state-asset acquisition – its size, IRR versus the Trust’s cost of capital, and funding mix.'),
    ('NAV under the new valuer – ', 'the H1 FY2027 valuation by IndiaAppraisers (due with the 12 November 2026 results) and any change in WACC methodology versus the 8.00% used for FY2026.'),
    ('O&M contract renewal and costs – ', 'the terms of the renewed O&M agreement with POWERGRID and the trend in O&M and fee expenses as the revenue base shrinks.'),
    ('Availability and interest rates – ', 'SPV-level availability against the 99.75% incentive cap, and the T-bill and repo rates that set the Trust’s floating cost of debt.'),
]
for i, (lead, txt) in zip(range(230, 235), mons):
    P(i, [(lead, True), (txt, False)])
t = E[239]
fill_row(rows(t)[1], [None, f1(d.PRICE)])
fill_row(rows(t)[3], [None, pct(irr)])
delete_rows(t, [2])
gl = [('VTL', 'Vizag Transmission Limited (formerly POWERGRID Vizag Transmission Limited)'), ('KATL', 'Kala Amb Transmission Limited (formerly POWERGRID Kala Amb Transmission Limited)'),
      ('PPTL', 'Parli Power Transmission Limited (formerly POWERGRID Parli Transmission Limited)'), ('WTL', 'Warora Transmission Limited (formerly POWERGRID Warora Transmission Limited)'),
      ('JPTL', 'Jabalpur Power Transmission Limited (formerly POWERGRID Jabalpur Transmission Limited)'), ('PGInvIT', 'POWERGRID Infrastructure Investment Trust'),
      ('POWERGRID', 'Power Grid Corporation of India Limited (Sponsor and Project Manager)'), ('PUTL', 'POWERGRID Unchahar Transmission Limited (Investment Manager)'),
      ('CTUIL', 'Central Transmission Utility of India Limited'), ('CERC', 'Central Electricity Regulatory Commission'), ('ISTS', 'Inter-State Transmission System'),
      ('TBCB', 'Tariff Based Competitive Bidding'), ('RTM', 'Regulated Tariff Mechanism'), ('BOOM', 'Build, Own, Operate and Maintain'), ('TSA', 'Transmission Service Agreement'),
      ('PIMA', 'Project Implementation and Management Agreement'), ('NDCF', 'Net Distributable Cash Flows'), ('DPU', 'Distribution per Unit'), ('NAV', 'Net Asset Value'),
      ('AUM', 'Assets Under Management (enterprise value of the SPVs)'), ('EV', 'Enterprise Value'), ('WACC', 'Weighted Average Cost of Capital'), ('ckm', 'Circuit kilometres'),
      ('MVA', 'Mega Volt Ampere'), ('SCOD', 'Scheduled Commercial Operation Date'), ('HTM', 'Hold to maturity'), ('XIRR', 'Internal rate of return on dated cash flows')]
rebuild(E[242], 1, [(1, list(g_)) for g_ in gl])

# =================================================================== images
rel = doc.part.related_parts
rel['rId12']._blob = open(f'{SP}/report/build/structure.png', 'rb').read()
rel['rId19']._blob = open(f'{SP}/report/build/price_chart.png', 'rb').read()
cy = str(int(5925820 / (2880 / 1345)))
for el in E[41].iter():
    if el.tag in (qn('wp:extent'), qn('a:ext')) and el.get('cx') == '5925820':
        el.set('cy', cy)

# =================================================================== strip comments
body = doc.element.body
for tag in ('commentRangeStart', 'commentRangeEnd'):
    for el in list(body.iter(W(tag))):
        el.getparent().remove(el)
for el in list(body.iter(W('commentReference'))):
    r_ = el.getparent()
    r_.getparent().remove(r_)
for rid in [r for r, rl in doc.part.rels.items() if 'comment' in rl.reltype]:
    doc.part.drop_rel(rid)
# strip highlights left in untouched runs
for el in list(body.iter(W('highlight'))):
    el.getparent().remove(el)

doc.core_properties.title = 'POWERGRID Infrastructure Investment Trust – Initiating Coverage'
doc.core_properties.author = ''
doc.core_properties.last_modified_by = ''
doc.save(OUT)
print('saved', OUT)
