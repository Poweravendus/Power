"""Rebuild SPV opex (Rs cr) from the valuer's FY27 cost lines and escalators; returns margins and opex by FY."""
import json
from core import valuer_data, SPVS

def build_opex(vr_path, spv_path, cons_path):
    V = valuer_data(json.load(open(vr_path)))
    S = json.load(open(spv_path))['spvs']
    C = json.load(open(cons_path))
    csr26 = C['pnl']['ox_csr_expenditure']['FY26']
    rev26 = {s: S[s]['revenue']['FY26'] for s in SPVS}
    tot26 = sum(rev26.values())
    opex, margins, detail = {}, {}, {}
    for s in SPVS:
        va = S[s]['valuation_assumptions']
        base, esc = va['opex_FY27_rs_cr'], va['opex_escalation']
        opex[s], margins[s] = {}, {}
        for fy, r in V[s]['rows'].items():
            frac = r['months'] / 12
            n = fy - 2027
            lines = {k: (v or 0) * (1 + (esc.get(k) or 0)) ** n * frac for k, v in base.items()}
            lines['licence_fee'] = 0.0011 * r['rev'] / 1.035
            lines['csr'] = csr26 * rev26[s] / tot26 * (r['rev'] / (V[s]['rows'][2027]['rev'])) * frac / max(frac, 1e-9) * frac
            tot = sum(lines.values())
            opex[s][fy] = tot
            margins[s][fy] = 1 - tot / r['rev'] if r['rev'] else 0
            if fy == 2027:
                detail[s] = lines
    return V, opex, margins, detail

if __name__ == '__main__':
    V, opex, margins, detail = build_opex('vr26.json', '../agentC/spv_history.json', '../agentA/consolidated_history.json')
    tot27 = 0
    for s in SPVS:
        r = V[s]['rows']
        tax = {fy: r[fy]['rev'] * margins[s][fy] - r[fy]['nopat'] - r[fy]['dep'] for fy in r}
        etr = {fy: tax[fy] / (r[fy]['rev'] * margins[s][fy] - r[fy]['dep']) for fy in r}
        tot27 += opex[s][2027]
        print(s, 'FY27 opex', round(opex[s][2027], 2), 'margin FY27/28/40/last', [round(margins[s][fy], 4) for fy in (2027, 2028, 2040, max(r))],
              '| implied tax FY27/28/32/40', [round(tax[fy], 1) for fy in (2027, 2028, 2032, 2040)], '| tax/EBIT', [round(etr[fy], 3) for fy in (2027, 2028, 2032, 2040)],
              '| min tax', round(min(tax.values()), 2))
        print('    lines', {k: round(v, 2) for k, v in detail[s].items()})
    print('Total SPV opex FY27', round(tot27, 1))
