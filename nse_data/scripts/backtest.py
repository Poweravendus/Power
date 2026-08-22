"""
Backtest: "Open = Low" entry with a 3% stop below the open and a 15% target.

Entry rules (all must hold on the signal day)
  1. Open == Low  -- the stock never traded below its open all session
  2. the day's up-move is less than 3%          (see UP_MOVE_DEFS -- two readings)
  3. entry is taken at that day's Close

Exit rules (checked from the NEXT session onward)
  Stop loss : Low_signal * (1 - 0.03)   i.e. 3% below the open=low level
  Target    : Entry * (1 + 0.15)
  Whichever is touched first ends the trade. Intraday sequence is unknowable
  from daily bars, so when a single bar touches both, the STOP is assumed to
  have come first (conservative). Those bars are counted and reported.
  Gaps are honoured: a bar opening beyond a level exits at the open, not at
  the level.
  Trades still live at the end of the data are marked to the last close.
"""

import argparse
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "output", "nse_ohlcv_master.csv")
OUT = os.path.join(ROOT, "backtest")

# Rule 2, the two defensible readings of "below 3% up that day".
UP_MOVE_DEFS = {
    "vs_prev_close": lambda d: (d["Close"] / d["Prev_Close"] - 1) * 100,
    "vs_open": lambda d: (d["Close"] / d["Open"] - 1) * 100,
}


def load():
    d = pd.read_csv(CSV, parse_dates=["Date"])
    return d.sort_values(["Symbol", "Date"]).reset_index(drop=True)


def signals(d, up_def, max_up_pct, tol_pct):
    """Rows meeting rules 1 and 2."""
    open_eq_low = (d["Open"] - d["Low"]).abs() <= d["Open"] * (tol_pct / 100.0)
    up = UP_MOVE_DEFS[up_def](d)
    return d.index[open_eq_low & (up < max_up_pct)], up


def run(d, sig_idx, up, sl_pct, tgt_pct, max_hold=None, risk_from_entry=None):
    """Walk each signal forward bar by bar until stop, target, or data end."""
    arrays = {}
    for sym, g in d.groupby("Symbol", sort=False):
        arrays[sym] = (
            g.index.to_numpy(),
            g["Date"].to_numpy(),
            g["Open"].to_numpy(),
            g["High"].to_numpy(),
            g["Low"].to_numpy(),
            g["Close"].to_numpy(),
        )
    pos_in_sym = {}
    for sym, (idx, *_rest) in arrays.items():
        for j, i in enumerate(idx):
            pos_in_sym[i] = (sym, j)

    trades = []
    for i in sig_idx:
        sym, j = pos_in_sym[i]
        _idx, dates, o, h, l, c = arrays[sym]
        entry = c[j]
        # Default stop is anchored to the signal bar's low (= its open).
        # risk_from_entry instead places it a fixed % under the entry, which is
        # what makes a benchmark against other days apples-to-apples.
        if risk_from_entry is None:
            stop = l[j] * (1 - sl_pct / 100.0)
        else:
            stop = entry * (1 - risk_from_entry / 100.0)
        target = entry * (1 + tgt_pct / 100.0)

        outcome, exit_price, exit_j, ambiguous = "OPEN", None, None, False
        last = len(dates) - 1 if max_hold is None else min(j + max_hold, len(dates) - 1)
        for k in range(j + 1, last + 1):
            if o[k] <= stop:                      # gapped through the stop
                outcome, exit_price, exit_j = "SL", o[k], k
                break
            if o[k] >= target:                    # gapped through the target
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
            exit_j = last
            exit_price = c[last]
            if max_hold is not None and last == j + max_hold:
                outcome = "TIME"

        trades.append({
            "Symbol": sym,
            "Signal_Date": dates[j],
            "Entry_Price": entry,
            "Signal_Open": o[j],
            "Signal_Low": l[j],
            "Up_Move_Pct": up.loc[i],
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


def non_overlapping(tr):
    """Keep only trades taken when that symbol had no live position."""
    keep, busy_until = [], {}
    for _, t in tr.sort_values("Signal_Date").iterrows():
        if t["Signal_Date"] >= busy_until.get(t["Symbol"], pd.Timestamp.min):
            keep.append(t)
            busy_until[t["Symbol"]] = t["Exit_Date"]
    return pd.DataFrame(keep).reset_index(drop=True)


def stats(tr, label):
    if tr.empty:
        return {"Variant": label, "Trades": 0}
    n = len(tr)
    wins = tr[tr["Return_Pct"] > 0]
    losses = tr[tr["Return_Pct"] <= 0]
    closed = tr[tr["Outcome"].isin(["SL", "TARGET"])]
    gross_win = wins["Return_Pct"].sum()
    gross_loss = abs(losses["Return_Pct"].sum())
    return {
        "Variant": label,
        "Trades": n,
        "Target_Hit": int((tr["Outcome"] == "TARGET").sum()),
        "Stopped": int((tr["Outcome"] == "SL").sum()),
        "Still_Open": int((tr["Outcome"] == "OPEN").sum()),
        "Timed_Out": int((tr["Outcome"] == "TIME").sum()),
        "Win_Rate_Pct": len(wins) / n * 100,
        "Target_Rate_Closed_Pct": (closed["Outcome"] == "TARGET").mean() * 100 if len(closed) else np.nan,
        "Avg_Return_Pct": tr["Return_Pct"].mean(),
        "Median_Return_Pct": tr["Return_Pct"].median(),
        "Avg_Win_Pct": wins["Return_Pct"].mean() if len(wins) else np.nan,
        "Avg_Loss_Pct": losses["Return_Pct"].mean() if len(losses) else np.nan,
        "Profit_Factor": gross_win / gross_loss if gross_loss else np.inf,
        "Expectancy_Pct": tr["Return_Pct"].mean(),
        "Avg_Hold_Days": tr["Hold_Days"].mean(),
        "Avg_Hold_Win": wins["Hold_Days"].mean() if len(wins) else np.nan,
        "Avg_Hold_Loss": losses["Hold_Days"].mean() if len(losses) else np.nan,
        "Avg_Risk_Pct": tr["Risk_Pct"].mean(),
        "Best_Pct": tr["Return_Pct"].max(),
        "Worst_Pct": tr["Return_Pct"].min(),
        "Same_Bar_Both": int(tr["Same_Bar_Both"].sum()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sl", type=float, default=3.0)
    ap.add_argument("--target", type=float, default=15.0)
    ap.add_argument("--max-up", type=float, default=3.0)
    ap.add_argument("--tol", type=float, default=0.0, help="Open==Low tolerance, %")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    d = load()

    # ---- headline: both readings of rule 2 -------------------------------
    rows, books = [], {}
    for up_def in UP_MOVE_DEFS:
        idx, up = signals(d, up_def, args.max_up, args.tol)
        tr = run(d, idx, up, args.sl, args.target)
        books[up_def] = tr
        rows.append(stats(tr, f"rule2 = {up_def} (all signals)"))
        rows.append(stats(non_overlapping(tr), f"rule2 = {up_def} (no overlap)"))
    summary = pd.DataFrame(rows)

    print("=" * 100)
    print(f"OPEN=LOW  |  entry at close  |  stop {args.sl}% below open=low  |  target +{args.target}%")
    print(f"universe 51 NSE symbols, {d['Date'].nunique()} sessions "
          f"{d['Date'].min():%Y-%m-%d} to {d['Date'].max():%Y-%m-%d}")
    print("=" * 100)
    with pd.option_context("display.width", 200, "display.max_columns", 50):
        print(summary.round(2).to_string(index=False))

    # ---- sensitivity grid -------------------------------------------------
    grid = []
    for up_def in UP_MOVE_DEFS:
        for sl in (2, 3, 5, 8):
            for tgt in (8, 10, 15, 20, 25):
                idx, up = signals(d, up_def, args.max_up, args.tol)
                s = stats(run(d, idx, up, sl, tgt), f"{up_def}")
                s.update({"Rule2": up_def, "SL_Pct": sl, "Target_Pct": tgt})
                grid.append(s)
    grid = pd.DataFrame(grid)

    # ---- reference: same signals, plain time exits ------------------------
    hold = []
    for up_def in UP_MOVE_DEFS:
        idx, up = signals(d, up_def, args.max_up, args.tol)
        for n in (1, 3, 5, 10, 20, 40):
            # stop at zero and target effectively unreachable => pure time exit
            tr = run(d, idx, up, 100.0, 1e6, max_hold=n)
            hold.append({"Rule2": up_def, "Hold_Days": n, "Trades": len(tr),
                         "Avg_Return_Pct": tr["Return_Pct"].mean(),
                         "Win_Rate_Pct": (tr["Return_Pct"] > 0).mean() * 100})
    hold = pd.DataFrame(hold)

    # ---- risk-matched benchmark ------------------------------------------
    # The strategy's stop sits under the signal bar's low. On an ordinary day
    # the low is further below the close, so the same "3% under the low" rule
    # would hand non-signal days a WIDER stop and fewer stop-outs. To isolate
    # what the Open=Low filter is actually worth, both sets are re-run with an
    # identical stop distance from entry (the signal set's average risk).
    bench = []
    for up_def in UP_MOVE_DEFS:
        sig_idx, up_all = signals(d, up_def, args.max_up, args.tol)
        risk = abs(run(d, sig_idx, up_all, args.sl, args.target)["Risk_Pct"].mean())
        other = d.index.difference(pd.Index(sig_idx))
        bench.append(stats(run(d, sig_idx, up_all, args.sl, args.target, risk_from_entry=risk),
                           f"{up_def}: SIGNAL days, stop {risk:.2f}% under entry"))
        bench.append(stats(run(d, other, up_all, args.sl, args.target, risk_from_entry=risk),
                           f"{up_def}: ALL OTHER days, stop {risk:.2f}% under entry"))
    bench = pd.DataFrame(bench)

    # ---- portfolio: Rs 1,00,000 per signal, sequential equity -------------
    CAPITAL = 100_000
    ports, curves = [], {}
    for up_def, tr in books.items():
        t = tr.sort_values("Exit_Date").copy()
        t["PnL"] = CAPITAL * t["Return_Pct"] / 100.0
        t["Cum_PnL"] = t["PnL"].cumsum()
        curve = t.groupby("Exit_Date")["PnL"].sum().cumsum()
        curves[up_def] = curve
        peak = curve.cummax()
        ports.append({
            "Rule2": up_def,
            "Trades": len(t),
            "Capital_Per_Trade": CAPITAL,
            "Total_PnL": t["PnL"].sum(),
            "Total_Deployed": CAPITAL * len(t),
            "Return_On_Deployed_Pct": t["PnL"].sum() / (CAPITAL * len(t)) * 100,
            "Max_Concurrent_Positions": int(max(
                ((t["Signal_Date"].values[:, None] <= t["Exit_Date"].values[None, :]) &
                 (t["Exit_Date"].values[:, None] >= t["Exit_Date"].values[None, :])).sum(axis=0))),
            "Max_Drawdown_Rs": float((curve - peak).min()),
            "Best_Trade_Rs": t["PnL"].max(),
            "Worst_Trade_Rs": t["PnL"].min(),
        })
    ports = pd.DataFrame(ports)

    # ---- monthly breakdown -------------------------------------------------
    monthly = {}
    for up_def, tr in books.items():
        m = tr.copy()
        m["Month"] = m["Signal_Date"].dt.to_period("M").astype(str)
        monthly[up_def] = (m.groupby("Month")
                             .agg(Signals=("Return_Pct", "size"),
                                  Target=("Outcome", lambda s: (s == "TARGET").sum()),
                                  Stopped=("Outcome", lambda s: (s == "SL").sum()),
                                  Avg_Return_Pct=("Return_Pct", "mean"))
                             .reset_index())

    # ---- universe buy & hold for context ----------------------------------
    bh = []
    for sym, g in d.groupby("Symbol"):
        g = g.sort_values("Date")
        bh.append(g["Close"].iloc[-1] / g["Close"].iloc[0] - 1)
    buyhold = np.mean(bh) * 100

    with pd.ExcelWriter(os.path.join(OUT, "Backtest_Results.xlsx"), engine="xlsxwriter",
                        datetime_format="yyyy-mm-dd") as w:
        summary.to_excel(w, sheet_name="Headline", index=False)
        grid.to_excel(w, sheet_name="Sensitivity_Grid", index=False)
        hold.to_excel(w, sheet_name="Fixed_Hold_Reference", index=False)
        bench.to_excel(w, sheet_name="Benchmark_NonSignal", index=False)
        ports.to_excel(w, sheet_name="Portfolio", index=False)
        for k, m in monthly.items():
            m.to_excel(w, sheet_name=f"Monthly_{k}"[:31], index=False)
        for k, tr in books.items():
            tr.to_excel(w, sheet_name=f"Trades_{k}", index=False)
            per_sym = (tr.groupby("Symbol")
                         .agg(Trades=("Return_Pct", "size"),
                              Target=("Outcome", lambda s: (s == "TARGET").sum()),
                              Stopped=("Outcome", lambda s: (s == "SL").sum()),
                              Avg_Return_Pct=("Return_Pct", "mean"),
                              Total_Return_Pct=("Return_Pct", "sum"))
                         .sort_values("Total_Return_Pct", ascending=False))
            per_sym.to_excel(w, sheet_name=f"PerSymbol_{k}")

    print("\n--- sensitivity: avg return %% per trade (rows SL, cols target) ---")
    for up_def in UP_MOVE_DEFS:
        g = grid[grid.Rule2 == up_def]
        print(f"\nrule2 = {up_def}")
        print(g.pivot(index="SL_Pct", columns="Target_Pct", values="Avg_Return_Pct").round(2).to_string())

    print("\n--- reference: same signals, fixed holding period, no stop/target ---")
    print(hold.round(2).to_string(index=False))

    print("\n--- risk-matched benchmark: does Open=Low add anything? ---")
    print(bench[["Variant", "Trades", "Target_Hit", "Stopped", "Win_Rate_Pct",
                 "Avg_Return_Pct", "Profit_Factor", "Avg_Hold_Days"]].round(2).to_string(index=False))

    print("\n--- portfolio, Rs 1,00,000 per signal ---")
    print(ports.round(0).to_string(index=False))
    print(f"\nContext: equal-weight buy & hold of the 51 names over the window = {buyhold:+.1f}%")

    print("\n--- monthly (rule2 = vs_prev_close) ---")
    print(monthly["vs_prev_close"].round(2).to_string(index=False))

    for k, tr in books.items():
        tr.to_csv(os.path.join(OUT, f"trades_{k}.csv"), index=False, date_format="%Y-%m-%d")
    print(f"\nWrote {OUT}/Backtest_Results.xlsx and per-variant trade logs")


if __name__ == "__main__":
    main()
