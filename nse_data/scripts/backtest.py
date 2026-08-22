"""
Backtest: "Open = Low" entry, with a close-strength band and a volume filter.

Entry rules (all must hold on the signal day)
  1. Open == Low  -- the stock never traded below its open all session
  2. Close is UP_MIN%..UP_MAX% above the previous close   (default 3-5%)
  3. Open > previous Close -- the session gapped up
  4. Volume >= VOL_MULT x the average of the prior VOL_WINDOW sessions
     (default 1.5x over 30 sessions; the signal day is excluded from its own
     average, and a symbol needs a full window of history to be eligible)
  5. entry is taken at that day's Close

Rules 1 and 3 together describe a gap up that never filled: the stock opened
above the prior close and spent the whole session at or above that open.

Exit rules (checked from the NEXT session onward)
  Stop loss : Low_signal * (1 - SL%)     -- SL% below the open=low level
  Target    : Entry * (1 + TARGET%)
  Whichever is touched first ends the trade. Intraday sequence is unknowable
  from daily bars, so when a single bar touches both, the STOP is assumed to
  have come first (conservative). Those bars are counted and reported.
  Gaps are honoured: a bar opening beyond a level exits at the open, not at
  the level. Trades still live at the end of the data are marked to the last
  close.

Because the filters are strict the sample is small, so every headline figure
is reported with a bootstrap 95% confidence interval.
"""

import argparse
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "output", "nse_ohlcv_master.csv")
OUT = os.path.join(ROOT, "backtest")

RNG = np.random.default_rng(20260822)


def load(vol_window):
    d = pd.read_csv(CSV, parse_dates=["Date"]).sort_values(["Symbol", "Date"]).reset_index(drop=True)
    d["Up_Pct"] = (d["Close"] / d["Prev_Close"] - 1) * 100
    # trailing average volume, signal day excluded from its own benchmark
    d["Vol_Avg"] = d.groupby("Symbol")["Volume"].transform(
        lambda s: s.shift(1).rolling(vol_window, min_periods=vol_window).mean())
    d["Vol_Ratio"] = d["Volume"] / d["Vol_Avg"]
    return d


def filters(d, up_min, up_max, vol_mult):
    """The four entry conditions, as boolean masks."""
    vm = 1.0 if vol_mult is None else vol_mult   # label only; caller drops rule 4
    return {
        "1 Open=Low": d["Open"] == d["Low"],
        f"2 close +{up_min:g}..{up_max:g}%": d["Up_Pct"].between(up_min, up_max),
        "3 gap up": d["Open"] > d["Prev_Close"],
        f"4 volume >={vm:g}x": d["Vol_Ratio"] >= vm,   # NaN history drops out
    }


def signals(d, up_min, up_max, vol_mult, drop=()):
    """Indices meeting every filter, optionally skipping some by position."""
    f = filters(d, up_min, up_max, vol_mult)
    mask = pd.Series(True, index=d.index)
    for i, m in enumerate(f.values(), start=1):
        if i not in drop:
            mask &= m
    return d.index[mask]


def run(d, sig_idx, sl_pct, tgt_pct, max_hold=None, risk_from_entry=None):
    """Walk each signal forward bar by bar until stop, target, or data end."""
    arrays, pos_in_sym = {}, {}
    for sym, g in d.groupby("Symbol", sort=False):
        arrays[sym] = (g["Date"].to_numpy(), g["Open"].to_numpy(), g["High"].to_numpy(),
                       g["Low"].to_numpy(), g["Close"].to_numpy())
        for j, i in enumerate(g.index):
            pos_in_sym[i] = (sym, j)

    trades = []
    for i in sig_idx:
        sym, j = pos_in_sym[i]
        dates, o, h, l, c = arrays[sym]
        entry = c[j]
        stop = l[j] * (1 - sl_pct / 100.0) if risk_from_entry is None \
            else entry * (1 - risk_from_entry / 100.0)
        target = entry * (1 + tgt_pct / 100.0)

        outcome, exit_price, exit_j, ambiguous = "OPEN", None, None, False
        last = len(dates) - 1 if max_hold is None else min(j + max_hold, len(dates) - 1)
        for k in range(j + 1, last + 1):
            if o[k] <= stop:
                outcome, exit_price, exit_j = "SL", o[k], k
                break
            if o[k] >= target:
                outcome, exit_price, exit_j = "TARGET", o[k], k
                break
            hit_sl, hit_tg = l[k] <= stop, h[k] >= target
            if hit_sl and hit_tg:
                outcome, exit_price, exit_j, ambiguous = "SL", stop, k, True
                break
            if hit_sl:
                outcome, exit_price, exit_j = "SL", stop, k
                break
            if hit_tg:
                outcome, exit_price, exit_j = "TARGET", target, k
                break
        if outcome == "OPEN":
            exit_j, exit_price = last, c[last]
            if max_hold is not None and last == j + max_hold:
                outcome = "TIME"

        row = d.loc[i]
        trades.append({
            "Symbol": sym,
            "Signal_Date": dates[j],
            "Up_Pct": row["Up_Pct"],
            "Vol_Ratio": row["Vol_Ratio"],
            "Entry_Price": entry,
            "Signal_Open": o[j],
            "Stop_Price": stop,
            "Target_Price": target,
            "Risk_Pct": (stop / entry - 1) * 100,
            "Outcome": outcome,
            "Exit_Date": dates[exit_j],
            "Exit_Price": exit_price,
            "Return_Pct": (exit_price / entry - 1) * 100,
            "Hold_Days": exit_j - j,
            "Same_Bar_Both": ambiguous,
        })
    return pd.DataFrame(trades)


def boot_ci(x, n=20000):
    """Bootstrap 95% CI for the mean."""
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return (np.nan, np.nan)
    draws = RNG.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return tuple(np.percentile(draws, [2.5, 97.5]))


def stats(tr, label):
    if tr.empty:
        return {"Variant": label, "Trades": 0, "Avg_Return_Pct": np.nan}
    n = len(tr)
    wins, losses = tr[tr.Return_Pct > 0], tr[tr.Return_Pct <= 0]
    closed = tr[tr.Outcome.isin(["SL", "TARGET"])]
    gl = abs(losses.Return_Pct.sum())
    lo, hi = boot_ci(tr.Return_Pct)
    aw = wins.Return_Pct.mean() if len(wins) else np.nan
    al = losses.Return_Pct.mean() if len(losses) else np.nan
    return {
        "Variant": label,
        "Trades": n,
        "Target_Hit": int((tr.Outcome == "TARGET").sum()),
        "Stopped": int((tr.Outcome == "SL").sum()),
        "Still_Open": int((tr.Outcome == "OPEN").sum()),
        "Win_Rate_Pct": len(wins) / n * 100,
        "Avg_Return_Pct": tr.Return_Pct.mean(),
        "CI95_Low": lo,
        "CI95_High": hi,
        "Median_Return_Pct": tr.Return_Pct.median(),
        "Avg_Win_Pct": aw,
        "Avg_Loss_Pct": al,
        "Breakeven_WR_Pct": abs(al) / (aw + abs(al)) * 100 if len(wins) and len(losses) else np.nan,
        "Profit_Factor": wins.Return_Pct.sum() / gl if gl else np.inf,
        "Avg_Hold_Days": tr.Hold_Days.mean(),
        "Avg_Risk_Pct": tr.Risk_Pct.mean(),
        "Best_Pct": tr.Return_Pct.max(),
        "Worst_Pct": tr.Return_Pct.min(),
        "Same_Bar_Both": int(tr.Same_Bar_Both.sum()),
    }


def non_overlapping(tr):
    keep, busy = [], {}
    for _, t in tr.sort_values("Signal_Date").iterrows():
        if t.Signal_Date >= busy.get(t.Symbol, pd.Timestamp.min):
            keep.append(t)
            busy[t.Symbol] = t.Exit_Date
    return pd.DataFrame(keep).reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sl", type=float, default=3.0)
    ap.add_argument("--target", type=float, default=15.0)
    ap.add_argument("--up-min", type=float, default=3.0)
    ap.add_argument("--up-max", type=float, default=5.0)
    ap.add_argument("--vol-mult", type=float, default=1.5)
    ap.add_argument("--vol-window", type=int, default=30)
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    d = load(args.vol_window)

    hdr = (f"OPEN=LOW  |  close +{args.up_min:g}%..{args.up_max:g}% vs prev  |  "
           f"volume >= {args.vol_mult:g}x {args.vol_window}d avg  |  entry at close  |  "
           f"stop {args.sl:g}% below open=low  |  target +{args.target:g}%")
    print("=" * len(hdr)); print(hdr)
    print(f"universe 51 NSE symbols, {d.Date.nunique()} sessions "
          f"{d.Date.min():%Y-%m-%d} to {d.Date.max():%Y-%m-%d}")
    print("=" * len(hdr))

    # ---- funnel ----------------------------------------------------------
    F = filters(d, args.up_min, args.up_max, args.vol_mult)
    oel, band, gap, vol = F.values()
    print("\n--- signal funnel ---")
    print(f"  all rows                              {len(d):>6,}")
    print(f"  Open == Low                           {int(oel.sum()):>6,}")
    print(f"  + close +{args.up_min:g}%..{args.up_max:g}% vs prev close       {int((oel&band).sum()):>6,}")
    print(f"  + open > prev close (gap up)          {int((oel&band&gap).sum()):>6,}")
    print(f"  + has {args.vol_window}d volume history            "
          f"{int((oel&band&gap&d.Vol_Avg.notna()).sum()):>6,}"
          f"   ({int((oel&band&gap&d.Vol_Avg.isna()).sum())} dropped, listed <{args.vol_window} sessions before signal)")
    print(f"  + volume >= {args.vol_mult:g}x avg                 "
          f"{int((oel&band&gap&vol).sum()):>6,}   <- traded")

    # ---- headline + volume-multiple sweep --------------------------------
    rows, books = [], {}
    sweep = [None, 1.0, 1.25, 1.5, 2.0, 3.0]
    for vm in sweep:
        idx = signals(d, args.up_min, args.up_max, vm,
                      drop=(4,) if vm is None else ())
        tr = run(d, idx, args.sl, args.target)
        lbl = "no volume filter" if vm is None else f"volume >= {vm:g}x"
        books[lbl] = tr
        rows.append(stats(tr, lbl))
    summary = pd.DataFrame(rows)

    print("\n--- volume filter sweep (rule 4 as a sensitivity parameter) ---")
    cols = ["Variant", "Trades", "Target_Hit", "Stopped", "Win_Rate_Pct",
            "Avg_Return_Pct", "CI95_Low", "CI95_High", "Breakeven_WR_Pct",
            "Profit_Factor", "Avg_Hold_Days"]
    with pd.option_context("display.width", 220):
        print(summary[cols].round(2).to_string(index=False))

    head_lbl = f"volume >= {args.vol_mult:g}x"
    head = books[head_lbl]
    print(f"\n--- headline ({head_lbl}), no-overlap check ---")
    print(pd.DataFrame([stats(non_overlapping(head), "one position per symbol")])[cols]
          .round(2).to_string(index=False))

    # ---- does each rule earn its place? ----------------------------------
    # Every combination of the three filters, same stop and target, plus a
    # permutation test of each against the all-days baseline: how often does a
    # random sample of the same size beat this subset's mean?
    names = list(F)
    masks = list(F.values())
    full = masks[0] & masks[1] & masks[2] & masks[3]
    combos = [(f"{n} alone", m) for n, m in F.items()]
    for i in range(4):
        m = pd.Series(True, index=d.index)
        for j in range(4):
            if j != i:
                m &= masks[j]
        combos.append((f"all except {names[i]}", m))
    combos.append(("ALL FOUR (full rule set)", full))
    base_tr = run(d, d.index, args.sl, args.target)
    base = base_tr.Return_Pct.to_numpy()
    layers = []
    for name, mask in combos:
        tr = run(d, d.index[mask], args.sl, args.target)
        st = stats(tr, name)
        if len(tr) >= 2:
            draws = RNG.choice(base, size=(20000, len(tr)), replace=True).mean(axis=1)
            st["P_vs_Baseline"] = float((draws >= tr.Return_Pct.mean()).mean())
        layers.append(st)
    bs = stats(base_tr, "every day (baseline)")
    bs["P_vs_Baseline"] = np.nan
    layers.append(bs)
    layers = pd.DataFrame(layers)
    print("\n--- rule attribution: each alone, each left out, all four ---")
    print("    P_vs_Baseline = share of random same-size samples of all days that beat this subset")
    print(layers[["Variant", "Trades", "Win_Rate_Pct", "Avg_Return_Pct",
                  "CI95_Low", "CI95_High", "Profit_Factor", "P_vs_Baseline"]]
          .round(3).to_string(index=False))

    # ---- SL / target grid at the headline volume filter -------------------
    grid = []
    idx = signals(d, args.up_min, args.up_max, args.vol_mult)
    for sl in (2, 3, 5, 8):
        for tgt in (8, 10, 15, 20, 25):
            s = stats(run(d, idx, sl, tgt), "")
            s.update({"SL_Pct": sl, "Target_Pct": tgt})
            grid.append(s)
    grid = pd.DataFrame(grid)
    print(f"\n--- stop/target grid, avg return % per trade ({head_lbl}, n={len(idx)}) ---")
    print(grid.pivot(index="SL_Pct", columns="Target_Pct", values="Avg_Return_Pct")
          .round(2).to_string())

    # ---- fixed-hold reference --------------------------------------------
    hold = []
    for vm in (None, args.vol_mult):
        idx = signals(d, args.up_min, args.up_max, vm, drop=(4,) if vm is None else ())
        for n in (1, 3, 5, 10, 20, 40):
            tr = run(d, idx, 100.0, 1e6, max_hold=n)   # stop at zero, target unreachable
            hold.append({"Filter": "no vol filter" if vm is None else f">= {vm:g}x",
                         "Hold_Days": n, "Trades": len(tr),
                         "Avg_Return_Pct": tr.Return_Pct.mean(),
                         "Win_Rate_Pct": (tr.Return_Pct > 0).mean() * 100})
    hold = pd.DataFrame(hold)
    print("\n--- same signals, pure time exit, no stop and no target ---")
    print(hold.round(2).to_string(index=False))

    # ---- risk-matched benchmark -------------------------------------------
    idx = signals(d, args.up_min, args.up_max, args.vol_mult)
    risk = abs(run(d, idx, args.sl, args.target).Risk_Pct.mean())
    other = d.index.difference(pd.Index(idx))
    bench = pd.DataFrame([
        stats(run(d, idx, args.sl, args.target, risk_from_entry=risk),
              f"SIGNAL days (n={len(idx)}), stop {risk:.2f}% under entry"),
        stats(run(d, other, args.sl, args.target, risk_from_entry=risk),
              f"ALL OTHER days (n={len(other)}), stop {risk:.2f}% under entry"),
    ])
    print("\n--- risk-matched benchmark ---")
    print(bench[["Variant", "Trades", "Win_Rate_Pct", "Avg_Return_Pct",
                 "CI95_Low", "CI95_High", "Profit_Factor"]].round(2).to_string(index=False))

    # ---- is the best filter just riding the bull market? -------------------
    mid = d.Date.min() + (d.Date.max() - d.Date.min()) / 2
    halves = []
    for name, mask in combos + [("every day (baseline)", pd.Series(True, index=d.index))]:
        tr = run(d, d.index[mask], args.sl, args.target)
        if tr.empty:
            continue
        for half, sel in (("H1", tr.Signal_Date < mid), ("H2", tr.Signal_Date >= mid)):
            t = tr[sel]
            halves.append({"Filter": name, "Half": half, "Trades": len(t),
                           "Avg_Return_Pct": t.Return_Pct.mean() if len(t) else np.nan,
                           "Win_Rate_Pct": (t.Return_Pct > 0).mean() * 100 if len(t) else np.nan})
    halves = pd.DataFrame(halves)
    print(f"\n--- split at {mid:%Y-%m-%d}: does each filter hold up in both halves? ---")
    print(halves.pivot(index="Filter", columns="Half",
                       values=["Trades", "Avg_Return_Pct"]).round(2).to_string())

    # ---- write everything --------------------------------------------------
    with pd.ExcelWriter(os.path.join(OUT, "Backtest_Results.xlsx"), engine="xlsxwriter",
                        datetime_format="yyyy-mm-dd") as w:
        summary.to_excel(w, sheet_name="Volume_Sweep", index=False)
        layers.to_excel(w, sheet_name="Rule_Attribution", index=False)
        halves.to_excel(w, sheet_name="Period_Split", index=False)
        grid.to_excel(w, sheet_name="Sensitivity_Grid", index=False)
        hold.to_excel(w, sheet_name="Fixed_Hold_Reference", index=False)
        bench.to_excel(w, sheet_name="Benchmark_RiskMatched", index=False)
        for k, tr in books.items():
            if not tr.empty:
                tr.to_excel(w, sheet_name=("Trades_" + k.replace(">= ", "").replace(" ", "_"))[:31],
                            index=False)
    head.to_csv(os.path.join(OUT, "trades_headline.csv"), index=False, date_format="%Y-%m-%d")
    books["no volume filter"].to_csv(os.path.join(OUT, "trades_no_vol_filter.csv"),
                                     index=False, date_format="%Y-%m-%d")
    print(f"\nWrote {OUT}/Backtest_Results.xlsx and trade logs")


if __name__ == "__main__":
    main()
