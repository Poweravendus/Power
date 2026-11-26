"""Exhibit 1 for the note: revenue (base vs guidance) and EBITDA margin, two panels (no dual axis)."""
import json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); CO = os.path.dirname(HERE)
R = json.load(open(os.path.join(HERE, 'run_results_26Nov2026.json')))
B = R['2']
yrs = ['FY23', 'FY24', 'FY25', 'FY26E', 'FY27E', 'FY28E', 'FY29E', 'FY30E']
rev, ebm, guide = B['rev'], B['ebm'], [None] * 3 + B['guide_rev']
BLUE, LIGHT, ORANGE, INK, INK2, GRID = '#257de0', '#84b9f3', '#f47230', '#191919', '#666666', '#e6e6e6'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.5), dpi=200)
x = range(len(yrs))
a1.bar(x, rev, width=0.6, color=[BLUE] * 3 + [LIGHT] * 5, edgecolor='white', linewidth=1, label='Revenue, our base (light = estimate)')
gx = [i for i in x if guide[i]]; a1.plot(gx, [guide[i] for i in gx], 'o', color=ORANGE, markersize=5, markeredgecolor='white', label='Management guidance path')
for i in (0, 2, 7): a1.text(i, rev[i] + 40, f'{rev[i]:,.0f}', ha='center', color=INK, fontsize=7)
a1.set_title('Revenue, Rs. crore', loc='left', color=INK, fontsize=9)
a1.legend(frameon=False, fontsize=6.5, loc='upper left')
a2.plot(x, [m * 100 for m in ebm], color=BLUE, linewidth=2, marker='o', markersize=4)
a2.axhline(18.5, color=ORANGE, linewidth=1, linestyle='--'); a2.text(7.3, 18.75, 'guidance 18.5%', color=INK2, fontsize=6.5, ha='right', va='bottom')
for i, dy, ha in ((0, -0.2, 'left'), (2, 0.35, 'right'), (3, 0.35, 'center'), (4, -0.75, 'center')): a2.text(i + (0.15 if ha == 'left' else (-0.1 if ha == 'right' else 0)), ebm[i] * 100 + dy, f'{ebm[i]*100:.1f}%', ha=ha, color=INK, fontsize=7)
a2.set_title('EBITDA margin (base), %', loc='left', color=INK, fontsize=9); a2.set_ylim(13, 21.5)
for a in (a1, a2):
    a.set_xticks(list(x)); a.set_xticklabels(yrs, fontsize=6.5, color=INK2)
    for s in ('top', 'right'): a.spines[s].set_visible(False)
    a.spines['left'].set_color(GRID); a.spines['bottom'].set_color(GRID); a.tick_params(colors=INK2, labelsize=6.5)
    a.grid(axis='y', color=GRID, linewidth=0.6); a.set_axisbelow(True)
fig.tight_layout()
os.makedirs(os.path.join(CO, 'exhibits'), exist_ok=True)
fig.savefig(os.path.join(CO, 'exhibits', 'exhibit1_revenue_margin.png'))
print('ok')
