"""Exhibits for the JSW Energy note. Static PNGs for a Word document (light mode only).
Palette: dataviz reference categorical slots 1-4, validated (contrast WARN handled by
direct labels on every exhibit plus a backing table in the note)."""
import csv, datetime as dt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.patches as mpatches
import jswdata as d

C = d.PALETTE
INK, INK2, INK3, GRID = d.INK, d.INK2, d.INK3, d.GRID
DPI = 200

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5,
    "axes.edgecolor": GRID, "axes.linewidth": 0.8,
    "axes.labelcolor": INK2, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2,
    "xtick.major.size": 0, "ytick.major.size": 0,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white",
})


def style(ax, ygrid=True):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    if ygrid:
        ax.yaxis.grid(True, color=GRID, lw=0.7)
        ax.set_axisbelow(True)


def bars(ax, x, y, color, labels=None, fmt="{:,.0f}", pad=0.012):
    b = ax.bar(x, y, color=color, width=0.62, zorder=3)
    rng = max(y) - min(0, min(y))
    for xi, yi in zip(x, y):
        ax.text(xi, yi + rng * pad if yi >= 0 else yi - rng * pad * 2.2,
                fmt.format(yi), ha="center",
                va="bottom" if yi >= 0 else "top", fontsize=7.4, color=INK2)
    return b


def split_marker(ax, pos, label_a="Actuals", label_e="Estimates"):
    ax.axvline(pos, color=INK3, lw=0.9, ls=(0, (3, 3)), zorder=2)
    lo, hi = ax.get_ylim()
    ax.text(pos - 0.12, hi, label_a, ha="right", va="top", fontsize=7.2, color=INK3)
    ax.text(pos + 0.12, hi, label_e, ha="left", va="top", fontsize=7.2, color=INK3)


# ---------------------------------------------------------------- Exhibit 1
def ex1():
    yrs = [y.replace("A", "").replace("E", "E") for y in d.YEARS]
    x = list(range(len(yrs)))
    marg = [e / r * 100 for e, r in zip(d.ebitda, d.revenue)]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.0, 4.4), sharex=True,
                                 gridspec_kw={"height_ratios": [2.05, 1], "hspace": 0.14})
    bars(a1, x, d.revenue, C[0])
    a1.set_ylabel("Revenue (Rs. cr)")
    a1.set_ylim(0, max(d.revenue) * 1.20)
    style(a1); split_marker(a1, 4.5)
    a2.plot(x, marg, color=C[1], lw=2.0, marker="o", ms=5.5, zorder=3,
            markeredgecolor="white", markeredgewidth=1.4)
    for xi, yi in zip(x, marg):
        a2.text(xi, yi + 2.2, f"{yi:.0f}%", ha="center", fontsize=7.4, color=INK2)
    a2.set_ylabel("EBITDA margin")
    a2.set_ylim(min(marg) - 8, max(marg) + 12)
    a2.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.0f}%"))
    style(a2)
    a2.axvline(4.5, color=INK3, lw=0.9, ls=(0, (3, 3)))
    a2.set_xticks(x); a2.set_xticklabels(yrs)
    a1.set_title("Exhibit 2  Revenue and EBITDA margin, FY22A–FY30E",
                 loc="left", fontsize=9.5, color=INK, fontweight="bold", pad=8)
    fig.savefig("ex1_revenue_margin.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- Exhibit 2
def ex2():
    yrs = d.SEG_YEARS
    x = list(range(len(yrs)))
    series = [("Thermal", d.seg_thermal, C[0]), ("Hydro", d.seg_hydro, C[2]),
              ("Renewables", d.seg_renew, C[1]), ("Others / holdco", d.seg_other, C[3])]
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    bot_p = [0] * len(x); bot_n = [0] * len(x)
    for name, vals, col in series:
        b = []
        for i, v in enumerate(vals):
            base = bot_p[i] if v >= 0 else bot_n[i]
            ax.bar(i, v, bottom=base, color=col, width=0.6, zorder=3,
                   edgecolor="white", linewidth=1.6)
            if abs(v) > 700:
                ax.text(i, base + v / 2, f"{v:,.0f}", ha="center", va="center",
                        fontsize=7.2, color="white", fontweight="bold")
            if v >= 0:
                bot_p[i] += v
            else:
                bot_n[i] += v
        b.append(name)
    for i, t in enumerate(d.seg_total):
        ax.text(i, bot_p[i] + 550, f"{t:,.0f}", ha="center", fontsize=7.6,
                color=INK, fontweight="bold")
    ax.set_ylabel("EBITDA (Rs. cr)")
    ax.set_ylim(min(bot_n) - 400, max(bot_p) * 1.16)
    ax.set_xticks(x); ax.set_xticklabels(yrs)
    style(ax); ax.axvline(1.5, color=INK3, lw=0.9, ls=(0, (3, 3)))
    handles = [mpatches.Patch(color=c, label=n) for n, _, c in series]
    ax.legend(handles=handles, frameon=False, ncol=4, fontsize=8,
              loc="upper left", bbox_to_anchor=(0, -0.10), labelcolor=INK2)
    ax.set_title("Exhibit 3  Segment EBITDA mix — renewables become the business",
                 loc="left", fontsize=9.5, color=INK, fontweight="bold", pad=8)
    fig.savefig("ex2_segment_mix.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- Exhibit 3
def ex3():
    yrs = d.CAP_YEARS
    x = list(range(len(yrs)))
    series = [("Thermal", d.cap_thermal, C[0]), ("Hydro", d.cap_hydro, C[2]),
              ("Solar", d.cap_solar, C[3]), ("Wind", d.cap_wind, C[1]),
              ("Hybrid", d.cap_hybrid, C[4])]
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    bot = [0] * len(x)
    for name, vals, col in series:
        ax.bar(x, vals, bottom=bot, color=col, width=0.62, zorder=3,
               edgecolor="white", linewidth=1.6)
        for i, v in enumerate(vals):
            if v > 1100:
                ax.text(i, bot[i] + v / 2, f"{v:,.0f}", ha="center", va="center",
                        fontsize=7.0, color="white", fontweight="bold")
        bot = [b + v for b, v in zip(bot, vals)]
    for i, t in enumerate(d.cap_total):
        ax.text(i, t + 620, f"{t:,.0f}", ha="center", fontsize=7.6, color=INK,
                fontweight="bold")
    ax.set_ylabel("Operational capacity (MW)")
    ax.set_ylim(0, max(d.cap_total) * 1.16)
    ax.set_xticks(x); ax.set_xticklabels(yrs)
    style(ax); ax.axvline(3.5, color=INK3, lw=0.9, ls=(0, (3, 3)))
    handles = [mpatches.Patch(color=c, label=n) for n, _, c in series]
    ax.legend(handles=handles, frameon=False, ncol=5, fontsize=8,
              loc="upper left", bbox_to_anchor=(0, -0.10), labelcolor=INK2)
    ax.set_title("Exhibit 4  Operational capacity build by technology, FY23A–FY30E",
                 loc="left", fontsize=9.5, color=INK, fontweight="bold", pad=8)
    fig.savefig("ex3_capacity.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- Exhibit 4
def ex4():
    labels = ["FY26A\nEBITDA", "Renewables", "Hydro", "Thermal", "Others", "FY30E\nEBITDA"]
    start = d.seg_total[1]
    deltas = [d.seg_renew[5] - d.seg_renew[1], d.seg_hydro[5] - d.seg_hydro[1],
              d.seg_thermal[5] - d.seg_thermal[1], d.seg_other[5] - d.seg_other[1]]
    end = d.seg_total[5]
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    ax.bar(0, start, color=INK2, width=0.6, zorder=3)
    ax.text(0, start + 500, f"{start:,.0f}", ha="center", fontsize=7.8,
            color=INK, fontweight="bold")
    run = start
    for i, v in enumerate(deltas, start=1):
        col = C[2] if v >= 0 else C[1]
        base = run if v >= 0 else run + v
        ax.bar(i, abs(v), bottom=base, color=col, width=0.6, zorder=3)
        ax.plot([i - 0.7, i - 0.3], [run, run], color=INK3, lw=0.8, ls=(0, (2, 2)), zorder=2)
        ax.plot([i + 0.3, i + 0.7], [run + v, run + v], color=INK3, lw=0.8,
                ls=(0, (2, 2)), zorder=2)
        ax.text(i, base + abs(v) + 500, f"{v:+,.0f}", ha="center", fontsize=7.6,
                color=INK2)
        run += v
    ax.bar(5, end, color=INK2, width=0.6, zorder=3)
    ax.text(5, end + 500, f"{end:,.0f}", ha="center", fontsize=7.8, color=INK,
            fontweight="bold")
    ax.set_ylabel("EBITDA (Rs. cr)")
    ax.set_ylim(0, end * 1.18)
    ax.set_xticks(range(6)); ax.set_xticklabels(labels)
    style(ax)
    ax.set_title("Exhibit 5  EBITDA growth bridge FY26A → FY30E — 92% is renewables",
                 loc="left", fontsize=9.5, color=INK, fontweight="bold", pad=8)
    fig.savefig("ex4_bridge.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- Exhibit 5
def ex5():
    yrs = [y.replace("A", "") for y in d.YEARS]
    x = list(range(len(yrs)))
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.0, 4.2), sharex=True,
                                 gridspec_kw={"height_ratios": [1.9, 1], "hspace": 0.14})
    bars(a1, x, d.netdebt, C[0])
    a1.set_ylabel("Net debt (Rs. cr)")
    a1.set_ylim(0, max(d.netdebt) * 1.20)
    style(a1); split_marker(a1, 4.5)
    a2.plot(x, d.nd_ebitda, color=C[1], lw=2.0, marker="o", ms=5.5, zorder=3,
            markeredgecolor="white", markeredgewidth=1.4)
    for xi, yi in zip(x, d.nd_ebitda):
        a2.text(xi, yi + 0.45, f"{yi:.1f}x", ha="center", fontsize=7.4, color=INK2)
    a2.set_ylabel("Net debt / EBITDA")
    a2.set_ylim(0, max(d.nd_ebitda) + 2.6)
    a2.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.0f}x"))
    style(a2); a2.axvline(4.5, color=INK3, lw=0.9, ls=(0, (3, 3)))
    a2.set_xticks(x); a2.set_xticklabels(yrs)
    a1.set_title("Exhibit 6  Net debt and leverage, FY22A–FY30E",
                 loc="left", fontsize=9.5, color=INK, fontweight="bold", pad=8)
    fig.savefig("ex5_leverage.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- Exhibit 6
def ex6():
    dates, vals = [], []
    with open("evband.csv") as f:
        for row in csv.DictReader(f):
            dates.append(dt.datetime.strptime(row["date"], "%Y-%m-%d"))
            vals.append(float(row["fwd_ev_ebitda"]))
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    ax.axhline(d.EV_MEAN, color=INK3, lw=1.1, ls="-")
    ax.axhline(d.EV_SD1, color=INK3, lw=0.9, ls=(0, (4, 3)))
    ax.axhline(d.EV_SD2, color=INK3, lw=0.9, ls=(0, (1, 3)))
    ax.axhline(d.EV_SDM1, color=INK3, lw=0.9, ls=(0, (4, 3)))
    ax.plot(dates, vals, color=C[0], lw=1.4, zorder=3)
    for y, lab in [(d.EV_SD2, f"+2sd {d.EV_SD2:.1f}x"), (d.EV_SD1, f"+1sd {d.EV_SD1:.1f}x")]:
        ax.text(dates[0], y + 0.5, lab, ha="left", fontsize=7.2, color=INK3)
    for y, lab in [(d.EV_MEAN, f"16-yr mean {d.EV_MEAN:.1f}x"), (d.EV_SDM1, f"-1sd {d.EV_SDM1:.1f}x")]:
        ax.text(dates[-1] - dt.timedelta(days=200), y + 0.5, lab, ha="right",
                fontsize=7.2, color=INK3)
    ax.scatter([dates[-1]], [vals[-1]], color=C[1], s=34, zorder=4,
               edgecolor="white", linewidth=1.2)
    ax.annotate(f"23 Jul 26\n{vals[-1]:.1f}x", xy=(dates[-1], vals[-1]),
                xytext=(7, -5), textcoords="offset points", ha="left",
                fontsize=7.6, color=C[1], fontweight="bold")
    ax.set_xlim(dates[0], dates[-1] + dt.timedelta(days=1000))
    ax.set_ylabel("12m forward EV/EBITDA")
    ax.set_ylim(0, 25)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.0f}x"))
    style(ax)
    ax.set_title("Exhibit 7  JSW Energy 12-month forward EV/EBITDA, Mar-2010 to Jul-2026",
                 loc="left", fontsize=9.5, color=INK, fontweight="bold", pad=8)
    fig.savefig("ex6_evband.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- Exhibit 7
def ex7():
    """Indented tree: rows, not free-floating boxes, so nothing can overflow."""
    ROWS = [
        # (depth, colour, name, ownership, what it does / where it sits)
        (0, INK,  "JSW ENERGY LIMITED  —  listed parent (NSE: JSWENERGY)", "",
         "Standalone assets: Ratnagiri 1,200MW · Vijayanagar 860MW · Nandyal 18MW = 2,078MW thermal"),
        (1, C[0], "JSW Energy (Barmer) Ltd", "100%",
         "1,080MW lignite, Rajasthan · RERC-regulated 15% RoE · 30-yr PPA with state discoms"),
        (2, C[3], "Barmer Lignite Mining Co Ltd", "51% JV, RSMML",
         "9 MTPA captive lignite mines feeding Barmer"),
        (1, C[0], "Ind-Barath Energy (Utkal) Ltd", "100%",
         "700MW coal, Odisha · no PPA — fully merchant · Shakti e-auction coal"),
        (1, C[0], "JSW Thermal Energy One Ltd  (KSK Mahanadi)", "74%",
         "1,800MW coal, Chhattisgarh · acquired via NCLT, FY25 · 95% tied to AP/TN/UP"),
        (1, C[2], "JSW Hydro Energy Ltd", "100%",
         "Karcham Wangtoo 1,091MW + Baspa II 300MW, Himachal · PPAs to 2043/2046"),
        (2, C[2], "JSW Energy (Kutehr) Ltd", "step-down",
         "240MW hydro · CoD FY26 · 35+35yr PPA with Haryana at Rs.4.45/unit"),
        (1, C[1], "JSW Neo Energy Ltd  —  renewables & storage holdco", "100%",
         "Holds the entire RE build: 6,165MW operational FY26A → 18,316MW FY30E"),
        (2, C[1], "O2 Power platform", "acquired FY26",
         "4.7GW solar/wind/hybrid/FDRE · EV Rs.12,468cr"),
        (2, C[1], "Mytrah Energy", "acquired FY23",
         "1,753MW operating solar + wind"),
        (2, C[1], "JSW Renew Energy / Renew Two / Renewable (Vijayanagar)", "100%",
         "SECI IX, X, XII wind · captive solar for JSW Steel"),
        (2, C[1], "BESS and pumped-storage vehicles", "100%",
         "3,000MW BESS + 3,300MW PSP under construction · SECI BESS-1 under dispute"),
        (1, C[3], "Jaigad Power Transco Ltd", "74% JV, MSETCL",
         "Two 400kV transmission lines · 14% regulated RoE"),
        (1, C[3], "JSW Power Trading Co Ltd", "100%",
         "Group merchant sales and exchange trading desk"),
        (1, C[3], "South African Coal Mining Holdings", "69%",
         "Legacy overseas coal holding — no material contribution"),
    ]
    n = len(ROWS)
    fig, ax = plt.subplots(figsize=(9.6, 0.33 * n + 1.0))
    ax.set_xlim(0, 100); ax.set_ylim(0, n + 1.9); ax.axis("off")
    xs = {0: 0.6, 1: 4.2, 2: 8.4}
    for i, (dep, col, name, own, desc) in enumerate(ROWS):
        y = n - i + 0.55
        x = xs[dep]
        ax.add_patch(mpatches.Rectangle((x - 2.6, y - 0.30), 1.5, 0.62,
                                        facecolor=col, linewidth=0, zorder=3))
        if dep > 0:
            ax.plot([xs[dep - 1] - 1.85, x - 2.6], [y, y], color=GRID, lw=0.9, zorder=1)
        ax.text(x, y + 0.10, name, fontsize=7.4, color=INK, fontweight="bold", va="center")
        if own:
            ax.text(99.4, y + 0.10, own, fontsize=6.9, color=INK2,
                    va="center", ha="right")
        ax.text(x, y - 0.24, desc, fontsize=6.5, color=INK2, va="center")
    for dep in (1, 2):
        ys = [n - i + 0.55 for i, r in enumerate(ROWS) if r[0] == dep]
        parents = [n - i + 0.55 for i, r in enumerate(ROWS) if r[0] == dep - 1]
        if ys:
            ax.plot([xs[dep - 1] - 1.85] * 2, [max(parents), min(ys)],
                    color=GRID, lw=0.9, zorder=1)
    ax.text(0.6, 0.85, "Where the money actually is — FY26A segment EBITDA incl. other income "
                       "(Rs. cr):  KSK Mahanadi 3,343 · Renewables 3,994 · Standalone 1,957 · "
                       "Hydro 1,077 · Barmer 668 · Ind-Barath 644 · Others –642.",
            fontsize=6.6, color=INK2, va="top")
    ax.text(0.6, 0.30, "The listed standalone entity produced 18% of FY26A segment EBITDA. "
                       "Ownership per FY25 AR / AOC-1 and Q4FY26 filings; capacity per the analyst model.",
            fontsize=6.3, color=INK3, va="top")
    ax.set_title("Exhibit 1  Corporate structure — where the assets and the earnings sit",
                 loc="left", fontsize=9.5, color=INK, fontweight="bold", pad=6)
    fig.savefig("ex7_structure.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


for fn in (ex1, ex2, ex3, ex4, ex5, ex6, ex7):
    fn(); print("built", fn.__name__)
