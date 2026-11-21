"""Metrics, stress windows, sensitivity grid, benchmark, Excel workbook, charts, markdown."""
from __future__ import annotations

import datetime as dt
import itertools
import logging
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from .costs import schedule_table
from .engine import Backtest, Config, MarketData

log = logging.getLogger(__name__)

OUT_DIR = Path(__file__).resolve().parent / "output"
TAX_FO, TAX_LTCG = 0.30, 0.125
STRESS_WINDOWS = [("Feb-Apr 2020 (COVID crash)", dt.date(2020, 2, 1), dt.date(2020, 4, 30)),
                  ("3-7 June 2024 (election result)", dt.date(2024, 6, 3), dt.date(2024, 6, 7))]
IN_SAMPLE = (dt.date(2019, 1, 1), dt.date(2024, 12, 31))
HOLDOUT_START = dt.date(2025, 1, 1)


# ----------------------------------------------------------------------------- metrics
def run(md: MarketData, cfg: Config) -> dict:
    bt = Backtest(md, cfg).run()
    tr, eq = bt.trades_frame(), bt.equity_frame()
    return {"cfg": cfg, "trades": tr, "equity": eq, "skipped": bt.skipped_entries, "open_at_end": len(bt.open)}


def longest_losing_streak(net: pd.Series) -> int:
    best = cur = 0
    for v in net:
        cur = cur + 1 if v <= 0 else 0
        best = max(best, cur)
    return best


def metrics(res: dict, md: MarketData) -> dict:
    cfg, tr, eq = res["cfg"], res["trades"], res["equity"]
    lot = cfg.lot
    m = {"variant": cfg.variant, "vix_filter": "ON" if cfg.vix_filter else "OFF",
         "period_start": eq["date"].iloc[0], "period_end": eq["date"].iloc[-1]}
    years = ((m["period_end"] - m["period_start"]).days + 1) / 365.25
    if tr.empty:
        return {**m, "trades": 0}
    net = tr["net_pnl_pts"]
    wins, losses = net[net > 0], net[net <= 0]
    tr_sorted = tr.sort_values("exit_date")
    max_loss_rs = float(tr["max_loss_pts"].max() * lot)
    concurrent = int(eq["n_open"].max())
    capital = max_loss_rs * concurrent
    monthly = eq.set_index(pd.to_datetime(eq["date"]))["equity_rs"].resample("ME").last()
    monthly_pnl = monthly.diff().fillna(monthly.iloc[0])
    by_year = tr.groupby(pd.to_datetime(tr["exit_date"]).dt.year)["net_pnl_rs"].sum()
    untraded = tr.groupby(pd.to_datetime(tr["exit_date"]).dt.year)["legs_traded_at_exit"].apply(lambda s: (~s).mean() * 100)
    m.update({
        "trades": len(tr), "wins": int((net > 0).sum()), "win_rate": float((net > 0).mean()),
        "avg_win_pts": float(wins.mean()) if len(wins) else np.nan,
        "avg_loss_pts": float(losses.mean()) if len(losses) else np.nan,
        "expectancy_pts": float(net.mean()), "expectancy_rs": float(net.mean() * lot),
        "breakeven_win_rate_rules": cfg.stop_mult / (cfg.stop_mult + cfg.take_profit),
        "breakeven_win_rate_empirical": float(-losses.mean() / (wins.mean() - losses.mean())) if len(wins) and len(losses) else np.nan,
        "total_pts": float(net.sum()), "total_rs": float(net.sum() * lot),
        "years": years, "annual_rs": float(net.sum() * lot / years),
        "max_dd_rs": float(eq["drawdown_rs"].min()),
        "max_loss_per_position_rs": max_loss_rs, "max_concurrent": concurrent, "capital_rs": capital,
        "max_dd_pct_capital": float(-eq["drawdown_rs"].min() / capital) if capital else np.nan,
        "worst_trade_rs": float(tr["net_pnl_rs"].min()),
        "worst_month": str(monthly_pnl.idxmin().strftime("%Y-%m")), "worst_month_rs": float(monthly_pnl.min()),
        "longest_losing_streak": longest_losing_streak(tr_sorted["net_pnl_pts"]),
        "exits_untraded_pct": float((~tr["legs_traded_at_exit"]).mean() * 100),
        "exits_interp_pct": float(tr["exit_on_interpolated_leg"].mean() * 100),
        "checks_interp_total": int(tr["exit_checks_interpolated"].sum()),
        "entries_untraded_pct": float((~tr["legs_traded_at_entry"]).mean() * 100),
        "exit_reasons": tr["exit_reason"].value_counts().to_dict(),
        "pnl_by_year": by_year.to_dict(), "untraded_exit_pct_by_year": untraded.to_dict(),
        "avg_credit_pts": float(tr["credit_pts"].mean()), "avg_days_held": float(tr["days_held"].mean()),
        "skipped_entries": res["skipped"],
    })
    # benchmark: Nifty index fund with the same capital over the same period
    s0, s1 = md.spot.get(m["period_start"]), md.spot.get(m["period_end"])
    bench_ret = s1 / s0 - 1
    bench_pnl = capital * bench_ret
    strat_after = m["total_rs"] * (1 - TAX_FO) if m["total_rs"] > 0 else m["total_rs"]
    bench_after = bench_pnl * (1 - TAX_LTCG) if bench_pnl > 0 else bench_pnl
    m.update({"nifty_start": s0, "nifty_end": s1, "nifty_return": bench_ret,
              "bench_pnl_rs": bench_pnl, "bench_after_tax_rs": bench_after, "strat_after_tax_rs": strat_after,
              "strat_cagr_after_tax": (1 + strat_after / capital) ** (1 / years) - 1 if capital and strat_after > -capital else np.nan,
              "bench_cagr_after_tax": (1 + bench_after / capital) ** (1 / years) - 1 if capital else np.nan})
    return m


def stress_trades(res: dict, label: str, w0: dt.date, w1: dt.date) -> pd.DataFrame:
    tr, eq = res["trades"], res["equity"]
    sel = tr[(tr["entry_date"] <= w1) & (tr["exit_date"] >= w0)].copy()
    sel.insert(0, "window", label)
    e = eq[(eq["date"] >= w0) & (eq["date"] <= w1)]
    before = eq[eq["date"] < w0]["equity_rs"]
    sel.attrs["equity_change_rs"] = float(e["equity_rs"].iloc[-1] - (before.iloc[-1] if len(before) else 0.0)) if len(e) else np.nan
    return sel


# ----------------------------------------------------------------------------- grid
def sensitivity_grid(md: MarketData, base: Config) -> pd.DataFrame:
    rows = []
    grid = itertools.product(["PCS", "IC"], [True, False], [0.12, 0.16, 0.20], [200.0, 300.0, 500.0], [1.5, 2.0], [0.50, 0.65])
    for variant, vf, d, w, sl, tp in grid:
        cfg = replace(base, variant=variant, vix_filter=vf, target_delta=d, width=w, stop_mult=sl, take_profit=tp,
                      start=IN_SAMPLE[0], end=IN_SAMPLE[1])
        m = metrics(run(md, cfg), md)
        rows.append({"variant": variant, "vix_filter": "ON" if vf else "OFF", "delta": d, "width": w, "stop_mult": sl,
                     "take_profit": tp, "trades": m.get("trades", 0), "win_rate": m.get("win_rate"),
                     "expectancy_rs": m.get("expectancy_rs"), "total_rs": m.get("total_rs"), "annual_rs": m.get("annual_rs"),
                     "max_dd_rs": m.get("max_dd_rs"), "max_dd_pct_capital": m.get("max_dd_pct_capital"),
                     "capital_rs": m.get("capital_rs"), "exits_untraded_pct": m.get("exits_untraded_pct")})
        log.info("grid %s", rows[-1])
    return pd.DataFrame(rows)


def slippage_sensitivity(md: MarketData, base: Config) -> pd.DataFrame:
    rows = []
    for variant, vf, slip in itertools.product(["PCS", "IC"], [True, False], [0.5, 1.0, 2.0]):
        cfg = replace(base, variant=variant, vix_filter=vf, slippage_pts=slip)
        m = metrics(run(md, cfg), md)
        rows.append({"variant": variant, "vix_filter": "ON" if vf else "OFF", "slippage_pts_per_leg": slip,
                     "trades": m["trades"], "win_rate": m["win_rate"], "expectancy_rs": m["expectancy_rs"],
                     "total_rs": m["total_rs"], "annual_rs": m["annual_rs"], "max_dd_rs": m["max_dd_rs"]})
    return pd.DataFrame(rows)
