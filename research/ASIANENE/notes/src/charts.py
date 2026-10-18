"""Charts for the ASIANENE investor note. Static PNGs, 18.4cm wide at 200 dpi."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from openpyxl import load_workbook
import numpy as np, os

OUT = '/tmp/claude-0/-home-user-Power/60a0aeb2-ff4d-5285-880d-cdbf2095261c/scratchpad/note'
BLUE, ORANGE, AQUA, YELLOW = '#2a78d6', '#eb6834', '#1baf7a', '#eda100'
INK, INK2, MUTED, GRID, BASE = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': BASE, 'axes.labelcolor': INK2,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': 'white', 'axes.facecolor': 'white'})
W = 18.4 / 2.54

m = load_workbook('/home/user/Power/research/ASIANENE/ASIANENE_Model_v1.xlsx', data_only=True)['P&L']
years = [m.cell(2, c).value for c in range(2, 24)]
def row(r): return [m.cell(r, c).value for c in range(2, 24)]
sales, ebitda, ebm = row(3), row(19), row(21)
pat, cfo = row(33), row(124)
debtors, stla, cash, curinv, td = row(82), row(85), row(83), row(80), row(199)

def style(ax, pct=False):
    ax.grid(axis='y', color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    ax.tick_params(length=0)
    if pct: ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:.0f}%'))

# ---------- Chart 1: revenue and EBITDA margin by cycle (FY09-FY26, consolidated) ----------
i0 = years.index('FY09'); yrs = years[i0:]; s = sales[i0:]; mg = [e * 100 for e in ebm[i0:]]
fig, (a1, a2) = plt.subplots(2, 1, figsize=(W, 4.6), sharex=True, gridspec_kw={'height_ratios': [2.2, 1], 'hspace': 0.08})
x = np.arange(len(yrs))
cycles = [('FY09', 'FY13', 'Seismic drift', '#f4f7fb'), ('FY14', 'FY16', 'Kurdistan', '#fdf3ee'), ('FY17', 'FY20', 'Oilmax rebuild', '#f4f7fb'),
          ('FY21', 'FY23', 'Stall, collapse', '#fdf3ee'), ('FY24', 'FY26', 'CHP, Kuiper', '#f4f7fb')]
for a in (a1, a2):
    for s0, s1, lab, col in cycles:
        l, r = yrs.index(s0) - 0.5, yrs.index(s1) + 0.5
        a.axvspan(l, r, color=col, zorder=0)
for s0, s1, lab, col in cycles:
    l, r = yrs.index(s0) - 0.5, yrs.index(s1) + 0.5
    a1.text((l + r) / 2, 975, lab, ha='center', va='top', fontsize=7.5, color=INK2)
a1.bar(x, s, width=0.62, color=BLUE, zorder=2)
for xi, v in zip(x, s):
    if v >= 100: a1.text(xi, v + 12, f'{v:.0f}', ha='center', va='bottom', fontsize=7, color=INK2)
a1.set_ylim(0, 1000); a1.set_ylabel('Revenue, Rs. crore'); style(a1)
a2.axhline(0, color=BASE, linewidth=0.8)
a2.plot(x, mg, color=ORANGE, linewidth=2, marker='o', markersize=4, zorder=3)
for xi, v in zip(x, mg):
    if yrs[xi] in ('FY16', 'FY20', 'FY22', 'FY23', 'FY26'): a2.text(xi, v + (6 if v >= 0 else -6), f'{v:.0f}%', ha='center', va='bottom' if v >= 0 else 'top', fontsize=7, color=INK2)
a2.set_ylim(-40, 35); a2.set_ylabel('EBITDA margin'); style(a2, pct=True)
a2.set_xticks(x); a2.set_xticklabels(yrs, rotation=45, ha='right', fontsize=7.5)
a1.set_title('Revenue and EBITDA margin by business cycle, consolidated (FY10 is a nine-month year)', loc='left', fontsize=9.5, color=INK, pad=8)
fig.savefig(f'{OUT}/chart_cycles.png', dpi=200, bbox_inches='tight'); plt.close(fig)

# ---------- Chart 2: cash conversion FY17-FY26 ----------
i0 = years.index('FY17'); yrs2 = years[i0:]; p = pat[i0:]; c = cfo[i0:]; x = np.arange(len(yrs2))
fig, ax = plt.subplots(figsize=(W, 3.4))
ax.bar(x - 0.19, p, width=0.36, color=BLUE, label='PAT attributable to owners', zorder=2)
ax.bar(x + 0.19, c, width=0.36, color=AQUA, label='Operating cash flow', zorder=2)
ax.axhline(0, color=BASE, linewidth=0.8)
for xi, v in zip(x, c):
    ax.text(xi + 0.19, v + (2 if v >= 0 else -2), f'{v:.0f}', ha='center', va='bottom' if v >= 0 else 'top', fontsize=7, color=INK2)
ax.set_xticks(x); ax.set_xticklabels(yrs2); ax.set_ylabel('Rs. crore'); style(ax)
ax.legend(frameon=False, loc='upper left', fontsize=8)
ax.set_title('Profit versus cash: operating cash flow has trailed profit in each of the last three years', loc='left', fontsize=9.5, color=INK, pad=8)
fig.savefig(f'{OUT}/chart_cash.png', dpi=200, bbox_inches='tight'); plt.close(fig)

# ---------- Chart 3: segment revenue and result FY21-FY26 ----------
seg_y = ['FY21', 'FY22', 'FY23', 'FY24', 'FY25', 'FY26']
og = [221.9, 188.9, 63.2, 191.9, 192.4, 632.7]; mn = [6.9, 71.6, 46.7, 113.2, 272.6, 158.4]
ogr = [77.8, 54.5, -0.3, 41.0, 33.1, 102.0]; mnr = [-3.8, 33.0, 6.7, 18.6, 58.9, 31.6]
kuiper = [0, 0, 0, 0, 0, 299.4]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 3.3), gridspec_kw={'width_ratios': [1.3, 1], 'wspace': 0.25})
x = np.arange(len(seg_y))
a1.bar(x, mn, width=0.6, color=YELLOW, label='Mineral and other energy (coal CHP)', zorder=2)
a1.bar(x, [o - k for o, k in zip(og, kuiper)], width=0.6, bottom=mn, color=BLUE, label='Oil and gas, India', zorder=2)
a1.bar(x, kuiper, width=0.6, bottom=[o - k + mm for o, k, mm in zip(og, kuiper, mn)], color=AQUA, label='Oil and gas, Kuiper (outside India)', zorder=2)
for xi, t in zip(x, [o + mm for o, mm in zip(og, mn)]): a1.text(xi, t + 10, f'{t:.0f}', ha='center', fontsize=7, color=INK2)
a1.set_xticks(x); a1.set_xticklabels(seg_y); a1.set_ylabel('Segment revenue, Rs. crore'); style(a1); a1.set_ylim(0, 880)
a1.legend(frameon=False, fontsize=7.5, loc='upper left')
a1.set_title('Segment revenue', loc='left', fontsize=9.5, color=INK)
a2.plot(x, [r / v * 100 if v else np.nan for r, v in zip(ogr, og)], color=BLUE, marker='o', markersize=4, linewidth=2, label='Oil and gas')
a2.plot(x, [r / v * 100 if v > 20 else np.nan for r, v in zip(mnr, mn)], color=YELLOW, marker='o', markersize=4, linewidth=2, label='Mineral (FY21 n.m.)')
a2.axhline(0, color=BASE, linewidth=0.8); a2.set_xticks(x); a2.set_xticklabels(seg_y); style(a2, pct=True); a2.set_ylim(-10, 50)
a2.legend(frameon=False, fontsize=7.5, loc='upper right'); a2.set_title('Segment result margin (before D&A and corporate cost)', loc='left', fontsize=9.5, color=INK)
fig.savefig(f'{OUT}/chart_segments.png', dpi=200, bbox_inches='tight'); plt.close(fig)

# ---------- Chart 4: order book versus trailing revenue ----------
ob = [('Jun-19', 850, 194), ('Dec-19', 997, 250), ('Aug-22', 500, 260), ('Nov-23', 900, 110), ('Jun-24', 1033, 305), ('Sep-24', 997, 360), ('Dec-24', 1150, 400),
      ('Mar-25', 973, 465), ('Aug-25', 1688, 520), ('Nov-25', 2005, 525), ('Mar-26', 1750, 492), ('Aug-26', 1754, 526)]
fig, ax = plt.subplots(figsize=(W, 3.2)); x = np.arange(len(ob))
ax.bar(x, [o[1] for o in ob], width=0.6, color=BLUE, label='Order book (standalone, ex-GST where disclosed)', zorder=2)
ax.plot(x, [o[2] for o in ob], color=ORANGE, marker='o', markersize=4, linewidth=2, label='Trailing 12-month revenue', zorder=3)
for xi, o in zip(x, ob): ax.text(xi, o[1] + 25, f'{o[1]:,}', ha='center', fontsize=7, color=INK2)
ax.set_xticks(x); ax.set_xticklabels([o[0] for o in ob], fontsize=7.5); ax.set_ylabel('Rs. crore'); style(ax); ax.set_ylim(0, 2300)
ax.legend(frameon=False, fontsize=8, loc='upper left')
ax.set_title('Order book against trailing revenue: the 2019 book carried foreign contracts that never converted', loc='left', fontsize=9.5, color=INK, pad=8)
fig.savefig(f'{OUT}/chart_orderbook.png', dpi=200, bbox_inches='tight'); plt.close(fig)

# ---------- Chart 5: share price (yearly close, BSE) with business annotations ----------
st = load_workbook('/root/.claude/uploads/60a0aeb2-ff4d-5285-880d-cdbf2095261c/424f436a-Asian_Energy_Ace_Equity_Data.xlsx', data_only=True).worksheets[0]
pr = {}
for c in range(2, 31):
    d = st.cell(6, c).value; v = st.cell(45, c).value; h = st.cell(46, c).value; lo = st.cell(47, c).value
    if hasattr(d, 'year') and v: pr[f'FY{d.year % 100:02d}'] = (v, h, lo)
py = [y for y in years if y in pr and pr[y][0]]
close = [pr[y][0] for y in py]; hi = [pr[y][1] or pr[y][0] for y in py]; lo = [pr[y][2] or pr[y][0] for y in py]
py.append('Oct-26'); close.append(455); hi.append(513.75); lo.append(239)
fig, ax = plt.subplots(figsize=(W, 4.0)); x = np.arange(len(py))
ax.fill_between(x, lo, hi, color='#cde2fb', alpha=0.8, linewidth=0, label='Year high-low range')
ax.plot(x, close, color=BLUE, linewidth=2, marker='o', markersize=4, label='Year-end close (BSE)', zorder=3)
ann = {'FY08': 'Rs.446 high, 15-month year', 'FY16': 'Net worth Rs.10cr', 'FY17': 'Oilmax takes control', 'FY20': 'Best year, P/E 9x', 'FY23': 'Revenue -58%', 'FY25': 'Warrants at Rs.335', 'Oct-26': 'Merger sanctioned'}
for y, t in ann.items():
    if y in py:
        i = py.index(y); ax.annotate(t, (i, close[i]), xytext=(0, -24 if y == 'FY20' else (26 if y == 'FY16' else 14)), textcoords='offset points', ha='center', fontsize=7, color=INK2, arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.6))
ax.set_xticks(x); ax.set_xticklabels(py, rotation=45, ha='right', fontsize=7.5); ax.set_ylabel('Rs. per share'); style(ax); ax.set_ylim(0, 560)
ax.legend(frameon=False, fontsize=8, loc='upper left')
ax.set_title('Share price: three peaks (FY08, FY18, FY25), each followed by a 65-85% fall within two years', loc='left', fontsize=9.5, color=INK, pad=8)
fig.savefig(f'{OUT}/chart_price.png', dpi=200, bbox_inches='tight'); plt.close(fig)

# ---------- Chart 6: working capital: receivables + unbilled vs revenue ----------
i0 = years.index('FY19'); yrs6 = years[i0:]; x = np.arange(len(yrs6))
rec = [d + s_ for d, s_ in zip(debtors[i0:], stla[i0:])]; rev = sales[i0:]
fig, ax = plt.subplots(figsize=(W, 3.0))
ax.bar(x - 0.19, rev, width=0.36, color=BLUE, label='Revenue', zorder=2)
ax.bar(x + 0.19, rec, width=0.36, color=ORANGE, label='Trade receivables + unbilled and advances (year-end)', zorder=2)
for xi, r_, v in zip(x, rec, rev): ax.text(xi + 0.19, r_ + 8, f'{r_ / v * 365:.0f}d', ha='center', fontsize=7, color=INK2)
ax.set_xticks(x); ax.set_xticklabels(yrs6); ax.set_ylabel('Rs. crore'); style(ax); ax.legend(frameon=False, fontsize=8, loc='upper left')
ax.set_title('Receivables and unbilled work against revenue (labels: year-end days of sales)', loc='left', fontsize=9.5, color=INK, pad=8)
fig.savefig(f'{OUT}/chart_wc.png', dpi=200, bbox_inches='tight'); plt.close(fig)
print('charts written:', [f for f in os.listdir(OUT) if f.endswith('.png')])
