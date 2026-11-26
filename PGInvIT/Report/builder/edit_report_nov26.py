import sys, copy, docx
sys.path.insert(0, '/home/user/Power/PGInvIT/Report/builder')
from dx import set_par, clone_par, remove, rows, cells, set_cell
from docx.oxml.ns import qn
d = docx.Document('report_in.docx')
P = d.paragraphs
T = d.tables
assert P[145].text.strip() == 'Key Investment Arguments' and P[152].text.strip() == 'Key Risks' and P[160].text.strip() == 'Key Monitorable'
body_t = P[147]._p      # Normal, justified, Calibri 10
bull_t = P[154]._p      # List Paragraph, bullet (numId 3)
a_anchor, r_anchor, m_anchor = P[146]._p, P[153]._p, P[161]._p
old = [P[i]._p for i in list(range(147, 152)) + list(range(154, 160)) + list(range(162, 167))]

def add(after, tmpl, segs, bold_all=False, space_before=None):
    new = copy.deepcopy(tmpl)
    after.addnext(new)
    set_par(new, [(t, True if bold_all else b) for t, b in segs])
    if space_before is not None:
        ppr = new.find(qn('w:pPr'))
        sp = ppr.find(qn('w:spacing'))
        if sp is None:
            sp = ppr.makeelement(qn('w:spacing'), {}); ppr.insert(0, sp)
        sp.set(qn('w:before'), str(space_before))
    return new

def section(anchor, items):
    prev = anchor
    for kind, segs in items:
        if kind == 'h':
            prev = add(prev, body_t, segs, bold_all=True, space_before=160)
        elif kind == 'p':
            prev = add(prev, body_t, segs)
        else:
            prev = add(prev, bull_t, segs)

H = lambda t: ('h', [(t, True)])
Pp = lambda t: ('p', [(t, False)])
B = lambda lead, t: ('b', [(lead, True), (t, False)])

args = [
 H('1. Pure-play, fully operational inter-state transmission portfolio:'),
 Pp('POWERGRID Infrastructure Investment Trust (PGInvIT), sponsored by Power Grid Corporation of India Limited (POWERGRID), is India’s first InvIT sponsored by a Central Public Sector Enterprise. Settled in September 2020 and listed in May 2021 after a Rs. 7,735 crore IPO at Rs. 100 per unit, it owns 100% of five inter-state transmission SPVs bought from its Sponsor, giving investors contracted cash flows from operating transmission assets.'),
 B('Scale and composition: ', 'As of 30 September 2026, the portfolio comprised five TBCB transmission SPVs with 11 lines of ~3,699 ckm and 3 substations of 6,630 MVA across five states, with an enterprise value of Rs. 8,732 crore. WTL accounts for 27% of EV, VTL and PPTL 24% each, JPTL 21% and KATL 4%; the portfolio is 100% transmission.'),
 B('Established operating track record: ', 'The SPVs were commissioned between February 2017 and January 2019 and have an average operating history of ~8 years, all of it under POWERGRID operation.'),
 B('Long-term revenue visibility: ', 'Each SPV holds a 35-year Transmission Service Agreement on a build-own-operate-maintain basis, with an average residual contract life of ~27 years (to FY2052–FY2054), supporting long-dated, predictable cash flows.'),
 H('2. Stable performance of assets under PGInvIT'),
 Pp('Line availability has stayed above the 98% normative level at every SPV in every year since listing, at 99.87%–100.00% in FY2026 and 99.93%–100.00% in Q2 FY27. This earns close to the maximum incentive (capped at 99.75% availability), about 3.5% above the base charge. Revenue has been flat by design at Rs. 1,258–1,286 crore a year since FY2023, and EBITDA margins have held at 92%–94% (93.1% in FY2026), since costs are small and largely contractual.'),
 H('3. Strong payment security through the inter-state transmission pool'),
 Pp('All of PGInvIT’s revenue is billed and collected by the Central Transmission Utility (CTUIL) through the national ISTS pool, so no SPV depends on a single state discom.'),
 B('Pooled counterparty: ', 'CTUIL raises bills on all users of the inter-state network and pays each licensee its share, so a default by one discom is spread across the pool rather than borne by one SPV.'),
 B('Improving collections: ', 'Receivable days fell from 47 in FY2023 to 21 at 30 September 2026 as discoms cleared arrears under the 2022 Late Payment Surcharge rules, with collection efficiency of 101%–104.5% in FY2024–FY2025.'),
 H('4. High current yield backed by an unbroken distribution record'),
 Pp('The Trust has paid 21 consecutive quarterly distributions totalling Rs. 64.50 per unit since listing, held DPU at Rs. 12.00 for four straight years and guided Rs. 12.00 for FY2027, an 11.4% yield at the current price. FY27E NDCF of ~Rs. 1,090 crore covers the guided payout, and the units have delivered an annualised total return of ~13% since listing. This yield is front-loaded, however: DPU falls with the contracted tariff step-down from FY2028 (see Key Risks).'),
 H('5. Strong Sponsor Profile'),
 Pp('PGInvIT benefits from a strong, Government-controlled sponsor. POWERGRID holds the regulatory minimum 15% of units, is the Project Manager that operates all five SPVs, and owns 100% of the Investment Manager, POWERGRID Unchahar Transmission Limited.'),
 Pp('POWERGRID is a Schedule ‘A’ Maharatna CPSE, 51.34% owned by the Government of India and listed on the NSE and BSE. It operates ~1.88 lakh ckm of transmission lines and 294 substations with ~6.6 lakh MVA of capacity, carries ~84% of India’s inter-regional transfer capacity, reported FY2026 consolidated revenue of Rs. 46,733 crore and PAT of Rs. 15,928 crore, and is rated AAA by CRISIL, ICRA and CARE. Its operating expertise underpins the portfolio’s availability record, although it has stated a preference for securitisation over further InvIT monetisation.'),
 H('6. Strong financial profile with very low leverage'),
 Pp('PGInvIT has one of the lowest-leverage balance sheets among listed InvITs. Gross borrowings were Rs. 1,060 crore at 30 September 2026 against AUM of Rs. 8,732 crore, and net debt to AUM was 4.7% against the 70% regulatory ceiling, leaving debt capacity of ~Rs. 3,000 crore even at a 49% ratio.'),
 Pp('The debt consists of two 16-year HDFC Bank term loans: Rs. 558 crore linked to the 3-month T-bill (6.56%) and Rs. 502 crore linked to the repo rate (7.00%). The average cost of debt was 6.97% in FY2026, ~69% of principal is repayable after ten years, and the Trust is rated AAA by CRISIL, ICRA and CARE. All borrowings are floating-rate, so the book benefits from rate cuts but is exposed to rises (see Key Risks).'),
]
risks = [
 H('1. Contracted tariff step-down from FY2028'),
 Pp('This is the largest single risk. Quoted charges at PPTL, WTL and JPTL fall by ~30% from 1 April 2027, as bid, taking consolidated revenue from ~Rs. 1,253 crore in FY27E to ~Rs. 961 crore in FY28E (-23%). On our model NDCF falls to ~Rs. 798 crore and DPU to ~Rs. 8.77 in FY28E (from Rs. 12.00), declining gradually thereafter. Management has said Rs. 12 cannot be maintained without new assets and declined to give FY28 guidance on the 25-Nov-26 call.'),
 H('2. No acquisitions since listing'),
 Pp('The Sponsor has no right-of-first-offer pipeline for the Trust and prefers securitisation to InvIT monetisation. The only live route, a ~Rs. 500 crore TBCB consortium with POWERGRID, still awaits Ministry of Power and DIPAM approval, and PGInvIT cannot bid alone because it lacks the required construction experience. Replacing the ~Rs. 290 crore annual NDCF gap would need roughly Rs. 6,000 crore of debt-funded acquisitions, above the Trust’s ~Rs. 3,000 crore debt capacity at 49% leverage.'),
 H('3. Low hold-to-maturity return at the current price'),
 Pp('At Rs. 104.9 the units trade at a 14.4% premium to NAV, and our hold-to-maturity XIRR is only 4.7%, below the 7.18% 10-year G-sec yield the Independent Valuer uses as its risk-free rate. Part of each distribution is a return of capital on a finite-life asset base, so the current yield overstates the long-run return.'),
 H('4. Back-ended debt repayment and floating-rate borrowings'),
 Pp('About 69% of HDFC loan principal falls due after ten years, rising to a peak of ~Rs. 276 crore in FY2038. Charged to NDCF, these repayments push DPU down to ~Rs. 4.3 in FY2038 before it recovers to ~Rs. 6.9 once the loans are repaid in FY2041, unless the Trust refinances or uses its cash. All borrowings are floating-rate: a 100 bps rise costs ~Rs. 11 crore a year (~Rs. 0.12 per unit), more if acquisitions are debt-funded.'),
 H('5. Valuation and tax assumptions'),
 Pp('NAV rests on the new valuer’s 4.32% equity risk premium (7.08% previously) and 7.36% WACC; management agreed on the 25-Nov-26 call that a higher premium would lower NAV. NAV has already moved from Rs. 101.1 to Rs. 86.0, Rs. 94.1 and now Rs. 91.74 largely through valuer and WACC changes. SPV tax also rises over time as the interest deduction on Trust loans shrinks, and the valuer’s 28.6% rate (25.17% previously) costs ~0.2 percentage points of IRR.'),
 H('6. Operations and maintenance (O&M) and related-party concentration'),
 Pp('High availability depends entirely on POWERGRID, which operates all five SPVs under O&M agreements (Rs. 33.3 crore in FY2026, under 3% of revenue) and is also Sponsor, owner of the Investment Manager and seller of every asset the Trust owns. The O&M contract was valid until March 2026 and is to be renewed on terms linked to CERC norms, so its pricing and any future Sponsor transaction need scrutiny. The risk is moderated by the routine nature of transmission O&M and POWERGRID’s track record.'),
]
mons = [
 B('FY2028 distribution guidance: ', 'management declined to quantify FY28 DPU on the 25-Nov-26 call and expects to guide later, likely with Q4 FY27 results in May 2027; whether it guides to a lower DPU or uses reserves and debt to bridge the step-down will be key.'),
 B('Acquisitions and the TBCB consortium: ', 'DIPAM and Government approval for the consortium with POWERGRID (pending, no timeline), the first bid outcome, and any third-party or state-asset acquisition, including its price, IRR relative to the Trust’s cost of capital and funding mix.'),
 B('Valuation and tax assumptions: ', 'whether IndiaAppraisers retains its 4.32% equity risk premium, 7.36% WACC and 28.6% SPV tax rate at the March 2027 valuation.'),
 B('O&M contract renewal and costs: ', 'the terms of the renewed O&M agreement with POWERGRID and the trend in O&M and fee expenses as the revenue base shrinks.'),
 B('Interest rates and debt repayment: ', 'T-bill and repo rate movements, which set the floating cost of debt, and how the Trust plans to meet the back-ended HDFC repayments of FY2036–FY2041 (refinancing, cash reserves or lower distributions).'),
 B('Availability and collections: ', 'SPV-level availability against the 99.75% incentive cap, and receivable days and collection efficiency under the CTUIL pool.'),
]
section(a_anchor, args)
section(r_anchor, risks)
section(m_anchor, mons)
for el in old:
    remove(el)

# ---- stale figures elsewhere ----
def rep_par(sub_old, sub_new):
    for p in d.paragraphs:
        if sub_old in p.text:
            full = p.text.replace(sub_old, sub_new)
            first_bold = p.runs[0].bold if p.runs else None
            # keep a bold lead-in if the paragraph starts with one
            lead = ''.join(r.text for r in p.runs if r.bold) if first_bold else ''
            if lead and full.startswith(lead):
                set_par(p._p, [(lead, True), (full[len(lead):], False)])
            else:
                set_par(p._p, [(full, None)])
            return
    raise SystemExit('not found: ' + sub_old[:50])

rep_par('Replacing the ~Rs. 250 crore annual NDCF gap with debt-funded deals would need ~Rs. 5,000 crore of assets, above the ~Rs. 3,000 crore debt capacity. We ascribe no value to acquisitions; the hold-to-maturity return is 4.8%, below the 7.18% G-sec yield.',
        'Replacing the ~Rs. 290 crore annual NDCF gap with debt-funded deals would need ~Rs. 6,000 crore of assets, above the ~Rs. 3,000 crore debt capacity. We ascribe no value to acquisitions; the hold-to-maturity return is 4.7%, below the 7.18% G-sec yield.')
for p in d.paragraphs:
    if p.text.startswith('FY27E NDCF of Rs. 1,090 crore covers the guided Rs. 12'):
        set_par(p._p, [('FY27E NDCF of Rs. 1,090 crore covers the guided Rs. 12 (Rs. 1,092 crore) almost exactly; H1 FY27 NDCF was Rs. 546 crore against Rs. 546 crore distributed. ', True),
            ('From FY28E we assume 100% of NDCF is paid out. NDCF falls 27% with the tariff step-down (we assume no working-capital release as revenue falls), so DPU falls to Rs. 8.77. It holds at Rs. 8.2–8.6 to FY31E and then drifts down as SPV taxes rise (the interest deduction shrinks as SPV loans are repaid) and costs escalate. '
             'The back-ended HDFC repayments, peaking at ~Rs. 276 crore in FY38, are charged to NDCF, so DPU dips to ~Rs. 4.3 in FY38E before recovering to ~Rs. 6.9 once the loans are repaid in FY41; in practice the Trust could refinance or draw on its cash (Rs. 651 crore at 30 September 2026) to smooth this. Holding Rs. 12 from FY28 would need about Rs. 290 crore a year beyond NDCF.', False)])
        break
else:
    raise SystemExit('distribution paragraph not found')

# ---- tables ----
set_cell(cells(rows(T[0]._tbl)[4])[1], '4.7%')
set_cell(cells(rows(T[27]._tbl)[2])[1], '4.7%')
proj = {1: ['1,109', '812', '802', '784', '766'], 2: ['(11)', '(2)', '(6)', '(4)', '(5)'], 3: ['(8)', '(11)', '(13)', '(15)', '(16)'],
        4: ['1,090', '798', '783', '765', '744'], 6: ['1,090', '798', '783', '765', '744'], 7: ['0.0%', '-26.9%', '-1.8%', '-2.4%', '-2.7%'],
        8: ['12.00', '8.77', '8.61', '8.40', '8.18'], 9: ['1,092', '798', '783', '765', '744']}
t25 = rows(T[25]._tbl)
for r, vals in proj.items():
    cs = cells(t25[r])
    assert len(cs) == 6, (r, len(cs))
    for k, val in enumerate(vals):
        set_cell(cs[1 + k], val)
d.save('report_out.docx')
print('saved')
