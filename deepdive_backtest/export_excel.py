"""Export backtest results to a formatted Excel workbook."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RES = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results")
OUT = RES / "deepdive_backtest_results.xlsx"
STOPS = (2, 3, 5, 8)


def stats(df, col):
    r = df[col].dropna()
    if len(r) == 0:
        return {"trades": 0, "win rate %": None, "avg R": None,
                "median R": None, "profit factor": None}
    losses = r[r <= 0]
    pf = r[r > 0].sum() / abs(losses.sum()) if losses.sum() != 0 else np.inf
    return {"trades": len(r), "win rate %": round((r > 0).mean() * 100, 1),
            "avg R": round(r.mean(), 3), "median R": round(r.median(), 3),
            "profit factor": round(pf, 2)}


def undercut_ok(t):
    if t.cause_gain <= 0.5:
        return t.undercut10
    if t.cause_gain <= 1.0:
        return t.undercut20
    return t.undercut50


tr = pd.read_parquet(RES / "trades.parquet")
tr["undercut_rule_ok"] = tr.apply(undercut_ok, axis=1)
tr["liquid_25cr"] = tr["turn20_cr"] >= 25
tr["fast_adr"] = tr["adr20"] >= 3.5
tr["lf_expanded"] = tr["lf_ratio"] >= 1.3
tr["early_base"] = tr["base_num"] <= 2
tr["relvol_confirm"] = tr["relvol_entry"] >= 1.2
tr["clean_cq"] = ~tr["purple_red_10d"]
core = ((tr["cons_dd"] <= 0.20) & tr["prior_narrow"] & tr["clean_cq"]
        & tr["undercut_rule_ok"] & tr["relvol_confirm"] & (tr["cause_gain"] <= 1.0))
full = tr[core]

sheets = {}

sheets["Read Me"] = pd.DataFrame({
    "Item": [
        "What this file is",
        "Setup tested",
        "Universe / period",
        "Entry rule",
        "Exit rule",
        "R multiple",
        "Win rate",
        "Profit factor",
        "'Core template' cohort",
        "Main caveats",
    ],
    "Explanation": [
        "Backtest results of the deep dive (cause-consolidation-effect) swing setup from the training transcripts.",
        "Cause = 25%+ rise in <=60 days near 6-month high. Consolidation = shallow rest. Effect = next leg (what we trade).",
        "604 NSE mid/small/micro caps (Nifty Midcap 150 + Smallcap 250 + Microcap 250), Feb 2015 - Jul 2026, 11,920 entries.",
        "Day 1-2 of new move: narrow prior day near 10DMA, buy on break of prior day's high, skip if gapping >5%.",
        "As taught: 1/3 sold at +2R, 1/3 at +3R, last 1/3 targets +5R with trailing stop 2R under the highest high. 60-day time stop.",
        "Profit/loss measured in units of initial risk. At a 5% stop, +2R = +10% move. -1R = full stop loss taken.",
        "% of trades with positive R.",
        "Gross profits / gross losses. Above 1.0 = profitable. 1.5+ is a solid edge for a swing system.",
        "Trades passing the filters that showed real edge: consolidation <=20%, narrow prior day, clean CQ, undercut rule, relative volume >=1.2x on entry, cause <=100%. (518 trades)",
        "Survivorship bias (current index members only), daily bars (no intraday entries), no costs/slippage. Absolute numbers optimistic; cohort comparisons robust.",
    ]})

rows = []
for w in STOPS:
    rows.append({"stop": f"{w}%", "cohort": "all entries", **stats(tr, f"r_{w}")})
    rows.append({"stop": f"{w}%", "cohort": "core template", **stats(full, f"r_{w}")})
sheets["1 Headline"] = pd.DataFrame(rows)

conds = ["shallow", "prior_narrow", "clean_cq", "undercut_rule_ok", "liquid_25cr",
         "fast_adr", "lf_expanded", "early_base", "relvol_confirm"]
labels = {"shallow": "Consolidation <=25% deep", "prior_narrow": "Narrow day before entry",
          "clean_cq": "Clean consolidation (no big red volume day)",
          "undercut_rule_ok": "10/20/50 DMA undercut rule respected",
          "liquid_25cr": "Liquidity >=25 crore/day", "fast_adr": "ADR >=3.5% (fast mover)",
          "lf_expanded": "Liquidity factor expanded >=1.3x in cause",
          "early_base": "Base 1 or 2", "relvol_confirm": "Relative volume >=1.2x on entry day"}
rows = []
for c in conds:
    on, off = stats(tr[tr[c]], "r_5"), stats(tr[~tr[c]], "r_5")
    rows.append({"condition": labels[c],
                 "trades (met)": on["trades"], "win % (met)": on["win rate %"],
                 "avg R (met)": on["avg R"], "PF (met)": on["profit factor"],
                 "trades (not met)": off["trades"], "win % (not met)": off["win rate %"],
                 "avg R (not met)": off["avg R"], "PF (not met)": off["profit factor"]})
sheets["2 Condition Lift"] = pd.DataFrame(rows)

tr["breadth_bucket"] = pd.cut(tr["breadth"], [0, .2, .35, .5, .65, 1],
                              labels=["<20%", "20-35%", "35-50%", "50-65%", ">65%"])
rows = [{"breadth (% stocks above 20DMA)": str(b), "index above 20DMA": bool(ia),
         **stats(g2, "r_5")}
        for b, g in tr.groupby("breadth_bucket", observed=True)
        for ia, g2 in g.groupby("idx_above20")]
sheets["3 Environment"] = pd.DataFrame(rows)

tr["dd_bucket"] = pd.cut(tr["cons_dd"], [0, .10, .15, .20, .25, .40],
                         labels=["0-10%", "10-15%", "15-20%", "20-25%", "25-40%"])
sheets["4 Consolidation Depth"] = pd.DataFrame(
    [{"consolidation depth": str(b), **stats(g, "r_5")}
     for b, g in tr.groupby("dd_bucket", observed=True)])

tr["cause_bucket"] = pd.cut(tr["cause_gain"], [.25, .40, .60, 1.0, 10],
                            labels=["25-40%", "40-60%", "60-100%", ">100%"])
sheets["5 Cause Size"] = pd.DataFrame(
    [{"cause size": str(b), **stats(g, "r_5")}
     for b, g in tr.groupby("cause_bucket", observed=True)])

sheets["6 Base Count"] = pd.DataFrame(
    [{"base number": ("4+" if b == 4 else str(int(b))), **stats(g, "r_5")}
     for b, g in tr.groupby(tr["base_num"].clip(upper=4))])

w20, w10 = tr[tr["reached_20"]], tr[tr["reached_10"]]
sheets["7 Shakeouts"] = pd.DataFrame(
    [{"dip below entry": f"-{w}%",
      "% of +20% winners that dipped this deep first":
          round((w20["dip_before_20"] <= -w / 100).mean() * 100, 1),
      "% of +10% winners that dipped this deep first":
          round((w10["dip_before_10"] <= -w / 100).mean() * 100, 1)}
     for w in (2, 3, 5, 8)]
    + [{"dip below entry": "Reached +10% within 40 bars",
        "% of +20% winners that dipped this deep first": round(tr["reached_10"].mean() * 100, 1)},
       {"dip below entry": "Reached +20% within 40 bars",
        "% of +20% winners that dipped this deep first": round(tr["reached_20"].mean() * 100, 1)},
       {"dip below entry": "Reached +10% then fell back to entry before +20%",
        "% of +20% winners that dipped this deep first": round(w10["giveback_after_10"].mean() * 100, 1)}])

rows = []
for w in STOPS:
    killed = tr[(tr["reached_20"]) & (tr[f"r_{w}"] <= -0.99)]
    rows.append({"stop width": f"{w}%", **stats(tr, f"r_{w}"),
                 "% of eventual +20% winners killed by this stop":
                     round(len(killed) / max(1, tr["reached_20"].sum()) * 100, 1)})
sheets["8 Stop Widths"] = pd.DataFrame(rows)

sheets["9 Year by Year"] = pd.DataFrame(
    [{"year": int(y), **stats(g, "r_5")}
     for y, g in full.groupby(full["entry_date"].dt.year)])

trades_cols = ["symbol", "segment", "entry_date", "entry", "cause_gain", "cause_bars",
               "cons_bars", "cons_dd", "lf_ratio", "base_num", "relvol_entry",
               "turn20_cr", "adr20", "mfe", "mae", "r_2", "r_3", "r_5", "r_8",
               "days_5", "breadth", "idx_above20"]
sheets["Core Template Trades"] = full[trades_cols].round(3)
sheets["All Trades"] = tr[trades_cols].round(3)

with pd.ExcelWriter(OUT, engine="openpyxl") as xl:
    for name, df in sheets.items():
        df.to_excel(xl, sheet_name=name, index=False)
        ws = xl.sheets[name]
        ws.freeze_panes = "A2"
        for col_cells in ws.columns:
            width = max(len(str(c.value)) if c.value is not None else 0
                        for c in col_cells[:50])
            ws.column_dimensions[col_cells[0].column_letter].width = min(60, max(10, width + 2))
        for c in ws[1]:
            c.font = c.font.copy(bold=True)
print("wrote", OUT)
