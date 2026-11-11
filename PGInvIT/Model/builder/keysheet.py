"""Key Sheet New: SPV register, contracted tariff schedule and revenue strip (linked to Sensitivity, single source)."""
import datetime as dt
from common import *
from core import SPVS, SEN, scol, a_row, acol

STRIP0, STRIPN = 2027, 2056          # revenue strip FY27E..FY56E in T:AW (as IndiGrid)
TSA0, TSAN = 2021, 2054              # contracted non-escalable charges by contract year in AY:BV


def tcol(fy):
    return L(CI('T') + fy - STRIP0)


def kcol(y):
    return L(CI('AY') + y - TSA0)


def d2s(s):
    if not s:
        return ''
    d = dt.date.fromisoformat(s)
    return d.strftime('%b-%Y')


def build_keysheet(ws, S, V):
    std_sheet(ws, colA=2.57, widths={'B': 5.4, 'C': 9, 'D': 34, 'E': 30, 'F': 16, 'G': 22, 'H': 46, 'I': 9, 'J': 9, 'K': 10, 'L': 12,
                                    'M': 18, 'N': 11, 'O': 11, 'P': 18, 'Q': 11, 'R': 11, 'S': 11})
    put(ws, 'B2', 'Transmission', bold=True, fill=SEC_FILL)
    hdr = ['#', 'Asset', 'Asset Full Name', 'Type of Tariff', 'Stake Holding', 'States', 'Elements', 'ckt kms', 'MVA', 'COD',
           'Acquisition into InvIT', 'Acquired From', 'EV at IPO (31-Dec-20)', 'AUM (EV, 31-Mar-26)', 'Contract Type',
           'Non-Escalable Charge', 'Change-in-law uplift', 'TSA expiry']
    units = ['', '', '', '', '', '', '', 'kms', 'MVA', 'Date', 'Date', '', 'Rs. cr', 'Rs. cr', '', 'Rs. cr (CY26)', '% of NEC', 'Date']
    for k, (h, u) in enumerate(zip(hdr, units)):
        c = L(2 + k)
        put(ws, f'{c}3', h, bold=True, color=WHITE, fill=HDR_FILL, border_b=True, align='left')
        put(ws, f'{c}4', u, bold=True, fill=SUB_FILL, align='center')
    put(ws, 'T3', 'Total Tariff / Revenue (incl. incentive) - Rs. cr, linked to Sensitivity_Bajaj', bold=True, color=WHITE, fill=HDR_FILL)
    put(ws, 'AY3', 'Contracted Non-Escalable Charges - Rs. cr, by contract year starting in calendar year (Final Offer Document p.148; excl. change-in-law uplift)',
        bold=True, color=WHITE, fill=HDR_FILL)
    for fy in range(STRIP0, STRIPN + 1):
        put(ws, f'{tcol(fy)}4', fy, fmt=FYFMT, bold=True, fill=SUB_FILL, align='center')
    for y in range(TSA0, TSAN + 1):
        put(ws, f'{kcol(y)}4', y, fmt='0', bold=True, fill=SUB_FILL, align='center')
    put(ws, 'B5', 'Operational', bold=True, fill=SUB_FILL)
    cil = {'PPTL': 0.0279, 'WTL': 0.0345, 'JPTL': 0.0523}
    for i, s in enumerate(SPVS):
        r = 6 + i
        st = S[s]['static']
        elements = '; '.join(
            (f'{e["kv"]} kV {e.get("circuit") or ""} line {e["ckm"]:,.0f} ckm' if e['type'] == 'line' else
             f'{e["type"].replace("_", " ")} {e["kv"]} kV' + (f' {e["mva"]:,.0f} MVA' if e.get('mva') else ''))
            for e in st['elements'])
        acq = f'74%: {d2s(st["acquired_74pct_date"])}; 26%: {d2s(st["acquired_26pct_date"])}'
        vals = [i + 1, s, st['full_legal_name'], 'Section 63 (TBCB) - BOOM' + ('; escalable component' if s == 'VTL' else '') + ('; RTM element' if s in ('KATL', 'PPTL') else ''),
                'Direct 100%', ', '.join(st['states']), elements, st['total_ckm'], st['total_mva'] or 0, d2s(st['project_cod']), acq,
                'POWERGRID (Sponsor)', st.get('enterprise_value_at_ipo_31dec2020_rs_cr'), None, 'Fixed Tariff / ISTS (CTU pool)',
                st['tsa_non_escalable_charges_rs_cr_by_contract_year'].get('2026'), cil.get(s, 0.0), d2s(st['tsa_expiry'])]
        for k, v in enumerate(vals):
            c = L(2 + k)
            fmt = NUM1 if isinstance(v, float) else None
            if c == 'R':
                fmt = PCT2
            put(ws, f'{c}{r}', v, fmt=fmt, fill=ROW_FILL, border_b=True, align='left' if isinstance(v, str) else 'right',
                color=RED if isinstance(v, (int, float)) and c not in ('B',) else None)
        put(ws, f'O{r}', f'=AssetLevelEst!E{3 + 27 * i + 18}', fmt=NUM1, fill=ROW_FILL, border_b=True)
        for fy in range(STRIP0, STRIPN + 1):
            if fy <= 2054:
                put(ws, f'{tcol(fy)}{r}', f'=N(Sensitivity_Bajaj!{scol(fy)}{SEN["eff"] + i})', fmt='#,##0;\\(#,##0\\);"–"')
            else:
                put(ws, f'{tcol(fy)}{r}', 0, fmt='#,##0;\\(#,##0\\);"–"')
        for y in range(TSA0, TSAN + 1):
            v = st['tsa_non_escalable_charges_rs_cr_by_contract_year'].get(str(y))
            if v is not None:
                put(ws, f'{kcol(y)}{r}', v, fmt=NUM1, color=RED)
    r = 11
    put(ws, f'B{r}', 'Sub Total', bold=True, fill=SEC_FILL)
    for c in ['I', 'J', 'N', 'O', 'Q']:
        put(ws, f'{c}{r}', f'=SUM({c}6:{c}10)', fmt=NUM1, bold=True, fill=SUB_FILL)
    for fy in range(STRIP0, STRIPN + 1):
        c = tcol(fy)
        put(ws, f'{c}{r}', f'=SUM({c}6:{c}10)', fmt='#,##0;\\(#,##0\\);"–"', bold=True, fill=SUB_FILL)
    for y in range(TSA0, TSAN + 1):
        c = kcol(y)
        put(ws, f'{c}{r}', f'=SUM({c}6:{c}10)', fmt=NUM1, bold=True, fill=SUB_FILL)
    notes = ['Notes:',
             'VTL is the only SPV with an escalable component (escalated at 4.53% p.a. by the valuer); escalable charges are inside the revenue strip, not the NEC schedule.',
             'PPTL, WTL and JPTL non-escalable charges step down by ~30% on their contract anniversaries (PPTL Jun-27, WTL Jul-27, JPTL Jun-28 per offer document).',
             'The valuer applies JPTL\'s step-down from FY28 (one year earlier than the offer-document schedule) - flagged, model ties to the valuer.',
             'RTM elements (KATL bus reactor, PPTL line bay) are valued separately by the valuer on FCFE; their value is added in AssetLevelEst.',
             'Revenue strip: FY27E-FY54E linked to Sensitivity_Bajaj effective tariff (single source of truth); years after TSA expiry show nil.']
    notes += ['',
              'Fixes vs the IndiGrid template:',
              '1. Year headers are real years (2027...) with an FY format, so year tests and escalation work (IndiGrid stored 202.7 etc.).',
              '2. AUM / NAV exclude the year\'s own cash flow and use each SPV\'s valuer WACC (IndiGrid counted the year\'s FCFF twice at a flat 8.5%).',
              '3. Distribution = MAX(90% of NDCF, MIN(DPU target, cash available)) - 90% is the SEBI floor, not a cap.',
              '4. Investment date is a fixed input (IndiGrid used TODAY(), so the IRR moved daily).',
              '5. No circular references: other income on opening cash; any unit issue priced at prior-year NAV.',
              '6. Distributable cash uses levered SPV tax (after interest on Trust loans); the valuer DCF stays on unlevered tax.']
    for k, t in enumerate(notes):
        put(ws, f'C{13 + k}', t, bold=t in ('Notes:', 'Fixes vs the IndiGrid template:'), italic=t not in ('Notes:', 'Fixes vs the IndiGrid template:'))
    # Segment revenues (as IndiGrid rows 75-90; only operational transmission for PGInvIT)
    put(ws, 'S29', 'Segment Revenues', bold=True)
    put(ws, 'S30', 'Operational - Transmission')
    put(ws, 'S31', 'Under Construction', italic=True)
    put(ws, 'S32', 'Total', bold=True)
    for fy in range(STRIP0, STRIPN + 1):
        c = tcol(fy)
        put(ws, f'{c}29', fy, fmt=FYFMT, bold=True, align='center')
        put(ws, f'{c}30', f'={c}11', fmt='#,##0;\\(#,##0\\);"–"')
        put(ws, f'{c}31', 0, fmt='#,##0;\\(#,##0\\);"–"')
        put(ws, f'{c}32', f'={c}30+{c}31', fmt='#,##0;\\(#,##0\\);"–"', bold=True)
    ws.freeze_panes = 'D5'
