"""Portfolio-level simulation of the core-template deep dive signals.

Implements the position management taught in the transcripts:
  - max 5 concurrent names ("five seven names, first come first serve")
  - 20% of current equity allocated per trade
  - 5% initial stop with the R-ladder exits already simulated per trade
  - variant B additionally respects the environment filter: no new entries
    while breadth <=35% AND the midcap index is below its 20DMA

Open positions are marked to market daily at the close (partial ladder
exits are ignored intraday; the final P&L is settled exactly at exit,
matching the per-trade simulation). Benchmark = Nifty Midcap 50 index.

Output: equity curves (PNG), drawdown/stat table (markdown + stdout).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RES = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results")
CACHE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data")
STOP_PCT = int(sys.argv[3]) if len(sys.argv) > 3 else 5     # 2/3/5/8
MODE = sys.argv[4] if len(sys.argv) > 4 else "core"         # core | loose

ALLOC = 0.20
MAX_POS = 5
STOP = STOP_PCT / 100


def undercut_ok(t):
    if t.cause_gain <= 0.5:
        return t.undercut10
    if t.cause_gain <= 1.0:
        return t.undercut20
    return t.undercut50


def load_trades():
    tr = pd.read_parquet(RES / "trades.parquet")
    tr["undercut_rule_ok"] = tr.apply(undercut_ok, axis=1)
    if MODE == "loose":
        mask = ((tr["cons_dd"] <= 0.20) & tr["undercut_rule_ok"]
                & (tr["relvol_entry"] >= 1.2))
    else:
        mask = ((tr["cons_dd"] <= 0.20) & tr["prior_narrow"] & (~tr["purple_red_10d"])
                & tr["undercut_rule_ok"] & (tr["relvol_entry"] >= 1.2)
                & (tr["cause_gain"] <= 1.0))
    tr = tr[mask].sort_values("entry_date").reset_index(drop=True)
    tr["ret"] = tr[f"r_{STOP_PCT}"] * STOP    # return on allocated capital
    tr["hold"] = tr[f"days_{STOP_PCT}"].astype(int)
    return tr


def run(tr, calendar, closes, env, gated):
    date_pos = {d: k for k, d in enumerate(calendar)}
    equity = 1.0
    curve = np.full(len(calendar), np.nan)
    open_pos = []                          # dicts: exit_k, capital, ret, symbol, entry, entry_k
    taken = skipped_slots = skipped_env = 0
    by_date = {d: g for d, g in tr.groupby("entry_date")}
    for k, d in enumerate(calendar):
        # settle exits
        still = []
        for p in open_pos:
            if k >= p["exit_k"]:
                equity += p["capital"] * p["ret"]
            else:
                still.append(p)
        open_pos = still
        # new entries
        if d in by_date:
            weak = gated and d in env.index and \
                (env.loc[d, "breadth"] <= 0.35 and not env.loc[d, "idx_above20"])
            for _, t in by_date[d].iterrows():
                if weak:
                    skipped_env += 1
                    continue
                if len(open_pos) >= MAX_POS:
                    skipped_slots += 1
                    continue
                open_pos.append(dict(exit_k=k + max(1, t["hold"]),
                                     capital=ALLOC * equity, ret=t["ret"],
                                     symbol=t["symbol"], entry=t["entry"],
                                     entry_k=k))
                taken += 1
        # mark to market
        mtm = equity
        for p in open_pos:
            px = closes.get(p["symbol"])
            if px is not None and d in px.index:
                mtm += p["capital"] * (px.loc[d] / p["entry"] - 1)
        curve[k] = mtm
    return pd.Series(curve, index=calendar).ffill(), dict(
        taken=taken, skipped_slots=skipped_slots, skipped_env=skipped_env)


def stats(curve, label):
    years = (curve.index[-1] - curve.index[0]).days / 365.25
    cagr = curve.iloc[-1] ** (1 / years) - 1
    dd = curve / curve.cummax() - 1
    return dict(strategy=label, final=round(curve.iloc[-1], 2),
                cagr_pct=round(cagr * 100, 1),
                max_dd_pct=round(dd.min() * 100, 1),
                time_in_dd_pct=round((dd < -0.01).mean() * 100, 1))


def main():
    tr = load_trades()
    idx = pd.read_parquet(CACHE / "NIFTY_MIDCAP50.parquet")
    env = pd.read_parquet(RES / "environment.parquet")
    start = tr["entry_date"].min() - pd.Timedelta(days=5)
    calendar = idx.index[idx.index >= start]
    closes = {}
    for s in tr["symbol"].unique():
        f = CACHE / f"{s.replace('&','_')}.parquet"
        if f.exists():
            closes[s] = pd.read_parquet(f)["close"]

    curveA, infoA = run(tr, calendar, closes, env, gated=False)
    curveB, infoB = run(tr, calendar, closes, env, gated=True)
    bench = idx.loc[calendar, "close"]
    bench = bench / bench.iloc[0]

    rows = [stats(curveA, "Deep dive portfolio (always trade)"),
            stats(curveB, "Deep dive + environment filter"),
            stats(bench, "Nifty Midcap 50 buy & hold")]
    md = pd.DataFrame(rows).to_markdown(index=False)
    info = (f"\nSignals: {len(tr)} · taken A/B: {infoA['taken']}/{infoB['taken']} · "
            f"skipped (slots full) A/B: {infoA['skipped_slots']}/{infoB['skipped_slots']} · "
            f"skipped by env filter B: {infoB['skipped_env']}")
    print(md + info)
    (RES / f"portfolio_stats_{MODE}_{STOP_PCT}.md").write_text(md + info + "\n")

    # ---- chart (dataviz spec: 2px lines, recessive grid, direct labels) ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    C_A, C_B, C_BENCH = "#2a78d6", "#eb6834", "#8a8985"
    INK, INK2, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"
    fig, ax = plt.subplots(figsize=(11, 6), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.plot(curveA.index, curveA, color=C_A, lw=2)
    ax.plot(curveB.index, curveB, color=C_B, lw=2)
    ax.plot(bench.index, bench, color=C_BENCH, lw=1.6, alpha=0.9)
    ax.set_yscale("log")
    yt = [1, 2, 5, 10, 20, 50]
    ax.set_yticks(yt)
    ax.set_yticklabels([f"{v}x" for v in yt], color=INK2, fontsize=9)
    ax.tick_params(axis="x", colors=INK2, labelsize=9)
    ax.grid(axis="y", color="#e4e2dd", lw=0.7)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#d8d6d0")
    series = [(curveA, C_A, "Deep dive portfolio"),
              (curveB, C_B, "With environment filter"),
              (bench, C_BENCH, "Nifty Midcap 50")]
    # dodge end labels: enforce a minimum gap in log space
    series.sort(key=lambda s: s[0].iloc[-1])
    min_gap = 0.09                       # in log10 units
    ys = [np.log10(s[0].iloc[-1]) for s in series]
    for j in range(1, len(ys)):
        ys[j] = max(ys[j], ys[j - 1] + min_gap)
    for (curve, col, label), y in zip(series, ys):
        ax.annotate(f" {label}  {curve.iloc[-1]:.1f}x",
                    xy=(curve.index[-1], 10 ** y),
                    color=col if col != C_BENCH else INK2,
                    fontsize=10, fontweight="bold", va="center")
    ax.set_xlim(calendar[0], calendar[-1] + pd.Timedelta(days=1250))
    ax.set_title(f"Deep dive portfolio ({MODE} signals, {STOP_PCT}% stop), 2015–2026",
                 color=INK, fontsize=13, fontweight="bold", loc="left", pad=14)
    ax.text(0, 1.005, f"20% of equity per trade · max 5 positions · {STOP_PCT}% stop, R-ladder exits · "
            f"{MODE} signal set · log scale",
            transform=ax.transAxes, color=INK2, fontsize=9)
    fig.tight_layout()
    fig.savefig(RES / f"equity_curve_{MODE}_{STOP_PCT}.png", facecolor=SURFACE,
                bbox_inches="tight")
    print("wrote", RES / f"equity_curve_{MODE}_{STOP_PCT}.png")


if __name__ == "__main__":
    main()
