"""Exhibit 1: fibre PBIT per kg FY17-FY26 and H1FY27 vs 10-year average; Exhibit 2: revenue by segment FY17-FY26 + FY27E-FY30E base.
Usage: python3 pal_exhibit.py <model_v2.xlsx> <out_dir>"""
import sys, openpyxl, json, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fn, out = sys.argv[1], sys.argv[2]
M = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model_map.json')))
wb = openpyxl.load_workbook(fn, data_only=True); sg = wb['Segments']; S = M['S']; q = wb['Quarterly']; QR = M['QR']
H = list('BCDEFGHIJK'); A = H + list('LMNO')
yrs = [f'FY{y}' for y in range(17, 27)]
ebkg = [sg[f'{c}{S["febitkg"]}'].value for c in H]
avg = sum(ebkg) / len(ebkg)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8})
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.6))
x = yrs + ['H1FY27 est.']
h1 = q[f'O{QR["xf"]}'].value * 1e4 / 19650   # H1FY27 volume not disclosed: ~19,650 t at Rs.160/kg (estimate)
ax[0].bar(x, ebkg + [h1], color=['#4C72B0'] * 10 + ['#DD8452'])
ax[0].axhline(avg, color='black', lw=1, ls='--'); ax[0].text(0, avg + 0.8, f'10-yr avg Rs.{avg:.1f}/kg', fontsize=7)
ax[0].set_title('Fibre PBIT per kg (Rs.)', fontsize=8); ax[0].tick_params(axis='x', rotation=90, labelsize=7)
for s in ('top', 'right'): ax[0].spines[s].set_visible(False)
labs = [f'FY{y}' for y in range(17, 31)]
f = [sg[f'{c}{S["rf"]}'].value for c in A]; cp = [sg[f'{c}{S["rc"]}'].value for c in A]; e = [sg[f'{c}{S["re"]}'].value for c in A]
ax[1].bar(labs, f, color='#4C72B0', label='Fibre'); ax[1].bar(labs, cp, bottom=f, color='#55A868', label='CPP film')
ax[1].bar(labs, e, bottom=[a + b for a, b in zip(f, cp)], color='#C44E52', label='Ethanol')
ax[1].axvline(9.5, color='grey', lw=0.8, ls=':'); ax[1].set_ylim(0, 1350); ax[1].text(9.7, 1260, 'base case', fontsize=7)
ax[1].set_title('Revenue by segment (Rs. crore)', fontsize=8); ax[1].tick_params(axis='x', rotation=90, labelsize=7); ax[1].legend(fontsize=7, frameon=False)
for s in ('top', 'right'): ax[1].spines[s].set_visible(False)
plt.tight_layout(); os.makedirs(out, exist_ok=True); p = os.path.join(out, 'exhibit1_fibre_and_segments.png'); plt.savefig(p, dpi=200); print(p, round(avg, 1), round(h1, 1))
