"""Aggregate backtest results into the report tables:

- headline stats per stop width
- univariate lift of each template condition (when it works vs not)
- environment splits (breadth x index-vs-20DMA)
- consolidation depth / cause size / base count buckets
- shakeout study (dips below entry before the move pays)
- stop-width trade-off incl. 'winner that stopped you out first' rates
- year-by-year robustness
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RES = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results")
STOPS = (2, 3, 5, 8)


def stats(df, col):
    r = df[col].dropna()
    if len(r) == 0:
        return dict(n=0)
    wins, losses = r[r > 0], r[r <= 0]
    pf = wins.sum() / abs(losses.sum()) if losses.sum() != 0 else np.inf
    return dict(n=len(r), win_rate=round((r > 0).mean() * 100, 1),
                avg_r=round(r.mean(), 3), med_r=round(r.median(), 3),
                profit_factor=round(pf, 2))


def table(rows, cols=None):
    df = pd.DataFrame(rows)
    if cols:
        df = df[cols]
    return df.to_markdown(index=False)


def undercut_ok(t):
    if t.cause_gain <= 0.5:
        return t.undercut10
    if t.cause_gain <= 1.0:
        return t.undercut20
    return t.undercut50


def main():
    tr = pd.read_parquet(RES / "trades.parquet")
    tr["year"] = tr["entry_date"].dt.year
    tr["undercut_rule_ok"] = tr.apply(undercut_ok, axis=1)
    tr["liquid_25cr"] = tr["turn20_cr"] >= 25
    tr["fast_adr"] = tr["adr20"] >= 3.5
    tr["lf_expanded"] = tr["lf_ratio"] >= 1.3
    tr["early_base"] = tr["base_num"] <= 2
    tr["relvol_confirm"] = tr["relvol_entry"] >= 1.2
    tr["clean_cq"] = ~tr["purple_red_10d"]

    conditions = ["shallow", "prior_narrow", "clean_cq", "undercut_rule_ok",
                  "liquid_25cr", "fast_adr", "lf_expanded", "early_base",
                  "relvol_confirm"]
    strict = tr[np.logical_and.reduce([tr[c] for c in conditions])]
    # core template: the conditions that showed real lift univariately
    # (liquidity/ADR floors are execution constraints, not edge — excluded)
    core_mask = (
        (tr["cons_dd"] <= 0.20) & tr["prior_narrow"] & tr["clean_cq"]
        & tr["undercut_rule_ok"] & tr["relvol_confirm"]
        & (tr["cause_gain"] <= 1.0)
    )
    full = tr[core_mask]

    L = []
    L.append("# Deep Dive (Cause -> Consolidation -> Effect) Backtest Results\n")
    L.append(f"Universe: {tr['symbol'].nunique()} NSE mid/small/micro caps · "
             f"{len(tr)} raw entries · {tr['entry_date'].min():%b %Y} – "
             f"{tr['entry_date'].max():%b %Y}\n")

    L.append("\n## 1. Headline: all raw entries vs full-template entries\n")
    rows = []
    for w in STOPS:
        rows.append(dict(stop=f"{w}%", cohort="all entries", **stats(tr, f"r_{w}")))
        rows.append(dict(stop=f"{w}%", cohort="core template", **stats(full, f"r_{w}")))
        rows.append(dict(stop=f"{w}%", cohort="strict (all 9)", **stats(strict, f"r_{w}")))
    L.append(table(rows))
    L.append("\n\ncore template = consolidation <=20% + narrow prior day + clean CQ "
             "+ undercut rule respected + relative volume >=1.2x on entry day "
             "+ cause <=100%.\n")
    strong_env = full[(full["breadth"] > 0.5) & (full["idx_above20"])]
    weak_env = full[(full["breadth"] <= 0.35) & (~full["idx_above20"].astype(bool))]
    L.append("\ncore template split by environment (5% stop):\n")
    L.append(table([dict(env="strong (breadth>50%, index>20DMA)", **stats(strong_env, "r_5")),
                    dict(env="weak (breadth<=35%, index<20DMA)", **stats(weak_env, "r_5"))]))

    L.append("\n\n## 2. When it works vs when it does not (univariate, 5% stop)\n")
    rows = []
    for c in conditions:
        on, off = stats(tr[tr[c]], "r_5"), stats(tr[~tr[c]], "r_5")
        rows.append(dict(condition=c,
                         n_true=on.get("n"), win_true=on.get("win_rate"),
                         avgR_true=on.get("avg_r"), pf_true=on.get("profit_factor"),
                         n_false=off.get("n"), win_false=off.get("win_rate"),
                         avgR_false=off.get("avg_r"), pf_false=off.get("profit_factor")))
    L.append(table(rows))

    L.append("\n\n## 3. Market environment at entry (5% stop, all entries)\n")
    tr["breadth_bucket"] = pd.cut(tr["breadth"], [0, .2, .35, .5, .65, 1],
                                  labels=["<20%", "20-35%", "35-50%", "50-65%", ">65%"])
    rows = []
    for b, g in tr.groupby("breadth_bucket", observed=True):
        for ia, g2 in g.groupby("idx_above20"):
            rows.append(dict(breadth=str(b), index_above_20dma=bool(ia), **stats(g2, "r_5")))
    L.append(table(rows))

    L.append("\n\n## 4. Consolidation depth (5% stop)\n")
    tr["dd_bucket"] = pd.cut(tr["cons_dd"], [0, .10, .15, .20, .25, .40],
                             labels=["0-10%", "10-15%", "15-20%", "20-25%", "25-40%"])
    rows = [dict(consolidation_depth=str(b), **stats(g, "r_5"),
                 mfe_med=round(g["mfe"].median() * 100, 1))
            for b, g in tr.groupby("dd_bucket", observed=True)]
    L.append(table(rows))

    L.append("\n\n## 5. Cause size (5% stop)\n")
    tr["cause_bucket"] = pd.cut(tr["cause_gain"], [.25, .40, .60, 1.0, 10],
                                labels=["25-40%", "40-60%", "60-100%", ">100%"])
    rows = [dict(cause=str(b), **stats(g, "r_5"))
            for b, g in tr.groupby("cause_bucket", observed=True)]
    L.append(table(rows))

    L.append("\n\n## 6. Base count (5% stop)\n")
    tr["base_bucket"] = tr["base_num"].clip(upper=4)
    rows = [dict(base=("4+" if b == 4 else str(b)), **stats(g, "r_5"))
            for b, g in tr.groupby("base_bucket")]
    L.append(table(rows))

    L.append("\n\n## 7. Shakeout study (exit-scheme-free, 40-bar window)\n")
    winners20 = tr[tr["reached_20"]]
    winners10 = tr[tr["reached_10"]]
    rows = []
    for w in (2, 3, 5, 8):
        rows.append(dict(
            dip_threshold=f"-{w}%",
            pct_of_20pct_winners_dipping_first=round(
                (winners20["dip_before_20"] <= -w / 100).mean() * 100, 1),
            pct_of_10pct_winners_dipping_first=round(
                (winners10["dip_before_10"] <= -w / 100).mean() * 100, 1)))
    L.append(table(rows))
    L.append(f"\n- Trades reaching +10% within 40 bars: "
             f"{round(tr['reached_10'].mean()*100,1)}% · reaching +20%: "
             f"{round(tr['reached_20'].mean()*100,1)}%")
    L.append(f"\n- Of trades that reached +10%, fell back to entry before "
             f"reaching +20%: {round(winners10['giveback_after_10'].mean()*100,1)}% "
             f"(the 'losing open gains' noise the training warns about)")
    med_mae_w = round(winners20["mae"].median() * 100, 1)
    L.append(f"\n- Median worst dip (MAE) among eventual +20% winners: {med_mae_w}%")

    L.append("\n\n## 8. Stop width trade-off (all entries)\n")
    rows = []
    for w in STOPS:
        killed = tr[(tr["reached_20"]) & (tr[f"r_{w}"] <= -0.99)]
        rows.append(dict(stop=f"{w}%", **stats(tr, f"r_{w}"),
                         winners_lost_to_stop_pct=round(
                             len(killed) / max(1, tr["reached_20"].sum()) * 100, 1)))
    L.append(table(rows))

    L.append("\n\n## 9. Year by year (5% stop, full template)\n")
    rows = [dict(year=int(y), **stats(g, "r_5"))
            for y, g in full.groupby(full["entry_date"].dt.year)]
    L.append(table(rows))

    (RES / "report.md").write_text("\n".join(L))
    full.to_csv(RES / "full_template_trades.csv", index=False)
    print("\n".join(L))


if __name__ == "__main__":
    main()
