import json, datetime as dt, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MultipleLocator, MaxNLocator
d = json.load(open(sys.argv[1]))['chart']['result'][0]
q = d['indicators']['quote'][0]
rows = [(dt.datetime.utcfromtimestamp(t + 19800), c, v or 0) for t, c, v in zip(d['timestamp'], q['close'], q['volume']) if c is not None]
print(len(rows), rows[0][0].date(), rows[-1][0].date(), rows[-1][1])
ds = [r[0] for r in rows]; px = [r[1] for r in rows]; vol = [r[2] for r in rows]
sm = [sum(px[max(0, i - 2):i + 3]) / len(px[max(0, i - 2):i + 3]) for i in range(len(px))]
plt.rcParams['font.family'] = 'DejaVu Sans'
fig = plt.figure(figsize=(16.96, 6.34), dpi=100)
ax = fig.add_axes([0.075, 0.1, 0.875, 0.84])
ax.bar(ds, vol, width=1.6, color='#c5d6f7', linewidth=0)
ax.set_ylabel('Volume', color='#808080', fontsize=13)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{int(v / 1000)}k' if v else '0'))
ax.tick_params(axis='y', colors='#555555', labelsize=12, length=0)
ax.set_ylim(0, max(vol) * 1.12)
ax.yaxis.set_major_locator(MaxNLocator(7))
ax2 = ax.twinx()
ax2.plot(ds, sm, color='#5b5bf0', linewidth=1.8)
ax2.set_ylabel('Price on NSE', color='#808080', fontsize=13, rotation=270, labelpad=18)
ax2.tick_params(axis='y', colors='#555555', labelsize=12, length=0)
ax2.set_ylim(70, 145)
ax2.yaxis.set_major_locator(MultipleLocator(10))
ax2.grid(axis='y', color='#e6e6e6', linewidth=1)
for a in (ax, ax2):
    for s in ('top', 'left', 'right'):
        a.spines[s].set_visible(False)
    a.spines['bottom'].set_color('#bbbbbb')
ax.set_zorder(ax2.get_zorder() - 1); ax2.patch.set_visible(False)
ax.xaxis.set_major_locator(mdates.YearLocator(month=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('Jan %Y'))
ax.tick_params(axis='x', colors='#555555', labelsize=12)
ax.set_xlim(ds[0] - dt.timedelta(days=20), ds[-1] + dt.timedelta(days=20))
fig.savefig(sys.argv[2], dpi=100, facecolor='white')
