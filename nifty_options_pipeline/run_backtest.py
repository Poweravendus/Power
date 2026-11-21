#!/usr/bin/env python3
"""Run the defined-risk monthly option-selling backtest and write the Excel workbook, charts and summary."""
from __future__ import annotations

import datetime as dt
import logging
import sys
import time
from dataclasses import replace
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest.engine import Config, MarketData  # noqa: E402
from backtest.report import (HOLDOUT_START, IN_SAMPLE, OUT_DIR, STRESS_WINDOWS, metrics, run,  # noqa: E402
                             sensitivity_grid, slippage_sensitivity, stress_trades)
from backtest.workbook import build_workbook  # noqa: E402
from backtest.summary_md import write_summary  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("run_backtest")


def main():
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md = MarketData()
    data_end = md.days[-1]
    base = Config()
    log.info("data loaded in %.0fs, %d trading days to %s", time.time() - t0, len(md.days), data_end)

    # headline runs: full period and 2021+, both variants, filter ON/OFF
    results, mets, trade_logs = {}, {}, []
    for variant in ("PCS", "IC"):
        for vf in (True, False):
            for start in (dt.date(2019, 1, 1), dt.date(2021, 1, 1)):
                key = f"{variant}_{'ON' if vf else 'OFF'}" + ("" if start.year == 2019 else "_2021")
                res = run(md, replace(base, variant=variant, vix_filter=vf, start=start))
                results[key] = res; mets[key] = metrics(res, md)
                tl = res["trades"].copy(); tl.insert(0, "run_id", key); trade_logs.append(tl)
                log.info("%s: %d trades, total Rs %.0f, maxDD Rs %.0f", key, mets[key]["trades"], mets[key]["total_rs"], mets[key]["max_dd_rs"])
    # comparison: base case on RAW value (no suspect-value handling), full period, filter OFF
    for variant in ("PCS", "IC"):
        key = f"{variant}_OFF_RAW"
        res = run(md, replace(base, variant=variant, vix_filter=False, use_raw_value=True))
        results[key] = res; mets[key] = metrics(res, md)
        tl = res["trades"].copy(); tl.insert(0, "run_id", key); trade_logs.append(tl)
        log.info("%s: %d trades, total Rs %.0f", key, mets[key]["trades"], mets[key]["total_rs"])
    # holdout (base case once)
    holdout, holdout_mets = {}, {}
    for variant in ("PCS", "IC"):
        for vf in (True, False):
            key = f"HOLDOUT_{variant}_{'ON' if vf else 'OFF'}"
            res = run(md, replace(base, variant=variant, vix_filter=vf, start=HOLDOUT_START))
            holdout[key] = res; holdout_mets[key] = metrics(res, md)
            tl = res["trades"].copy(); tl.insert(0, "run_id", key); trade_logs.append(tl)
            log.info("%s: %d trades, total Rs %.0f", key, holdout_mets[key]["trades"], holdout_mets[key]["total_rs"])
    trade_log = pd.concat(trade_logs, ignore_index=True)

    # stress windows on the four full-period runs
    stress_parts, stress_eq = [], []
    for key in ("PCS_ON", "PCS_OFF", "IC_ON", "IC_OFF"):
        for label, w0, w1 in STRESS_WINDOWS:
            s = stress_trades(results[key], label, w0, w1); s.insert(1, "run_id", key)
            stress_parts.append(s)
            stress_eq.append({"window": label, "run_id": key, "trades_touching_window": len(s),
                              "net_pnl_of_those_trades_rs": float(s["net_pnl_rs"].sum()) if len(s) else 0.0,
                              "equity_change_in_window_rs": s.attrs["equity_change_rs"]})
    stress = pd.concat(stress_parts, ignore_index=True); stress_eq = pd.DataFrame(stress_eq)

    log.info("sensitivity grid (in-sample %s..%s)", *IN_SAMPLE)
    grid = sensitivity_grid(md, base)
    slip = slippage_sensitivity(md, base)

    xlsx = OUT_DIR / "nifty_credit_spread_backtest.xlsx"
    build_workbook(results, mets, holdout, holdout_mets, grid, slip, trade_log, stress, stress_eq, base, data_end, xlsx)
    trade_log.to_csv(OUT_DIR / "trade_log.csv", index=False)
    grid.to_csv(OUT_DIR / "sensitivity_grid.csv", index=False)
    pd.DataFrame([{k: v for k, v in m.items() if not isinstance(v, dict)} | {"run_id": key} for key, m in {**mets, **holdout_mets}.items()]).to_csv(OUT_DIR / "metrics.csv", index=False)
    write_summary(mets, holdout_mets, grid, slip, stress_eq, base, data_end, OUT_DIR / "SUMMARY.md")
    log.info("done in %.0fs -> %s", time.time() - t0, xlsx)


if __name__ == "__main__":
    main()
