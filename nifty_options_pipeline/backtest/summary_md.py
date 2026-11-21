"""One-page markdown summary with the plain verdict against a Nifty index fund."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd

from .report import TAX_FO, TAX_LTCG

SOURCES = [
    ("Zerodha bulletin, STT revision from 1 Apr 2026", "https://zerodha.com/marketintel/bulletin/445377/revision-in-stt-securities-transaction-tax-from-1st-april-2026"),
    ("Business Standard, Budget 2026 STT hike", "https://www.business-standard.com/markets/news/markets-fm-hikes-stt-on-fo-trades-surprise-move-126020100888_1.html"),
    ("Zerodha bulletin, transaction charges from 1 Oct 2024", "https://zerodha.com/marketintel/bulletin/391488/revision-in-transactions-charges-from-1st-october-2024"),
    ("HDFC Securities, exchange charges from 1 Oct 2024", "https://www.hdfcsec.com/blog/details/revised-exchange-transaction-charges-w-e-f-1st-october-2024"),
    ("Zerodha support, how STT is calculated", "https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/how-is-the-securities-transaction-tax-stt-calculated"),
]


def rs(v):
    return f"{v:,.0f}" if pd.notna(v) else "n/a"


def pct(v):
    return f"{v * 100:.1f}%" if pd.notna(v) else "n/a"


def write_summary(mets, holdout_mets, grid, slip, stress_eq, base, data_end, path: Path):
    L = []
    L.append("# NIFTY defined-risk monthly option selling: backtest summary\n")
    L.append(f"Data: NSE bhavcopy 2019-01-01 to {data_end}, prices = `value` (settle before expiry, intrinsic at expiry). "
             f"Rules: one new position on the first trading day of each week in the nearest monthly expiry with 28-45 dte, "
             f"short strike nearest {base.target_delta:.2f} delta (Black-76 on the same-expiry future), wing {base.width:.0f} pts further OTM, "
             f"take profit at {base.take_profit:.0%} of credit, stop at {base.stop_mult}x credit, time exit at {base.time_exit_dte} dte. "
             f"Costs: Rs 20/order/leg, STT, NSE/SEBI/stamp charges, GST, {base.slippage_pts:g} pt slippage per leg per trade (x2 when VIX > 25). "
             f"All rupee figures per lot of {base.lot} units.\n")

    L.append("## Headline results (net of all costs)\n")
    L.append("| Run | Period | Trades | Win rate | Expectancy Rs/trade | Total Rs/lot | Annual Rs/lot | Max DD Rs/lot | DD % capital | Capital at risk Rs/lot |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for k, m in mets.items():
        if k.endswith("_RAW"):
            continue
        L.append(f"| {m['variant']} VIX {m['vix_filter']} | {m['period_start'].year}-{m['period_end'].year} | {m['trades']} | {pct(m['win_rate'])} | "
                 f"{rs(m['expectancy_rs'])} | {rs(m['total_rs'])} | {rs(m['annual_rs'])} | {rs(m['max_dd_rs'])} | {pct(m['max_dd_pct_capital'])} | {rs(m['capital_rs'])} |")
    L.append("")
    L.append("## Holdout (Jan 2025 to latest, base case run once, not re-tuned)\n")
    L.append("| Run | Trades | Win rate | Expectancy Rs/trade | Total Rs/lot | Annual Rs/lot | Max DD Rs/lot |")
    L.append("|---|---|---|---|---|---|---|")
    for k, m in holdout_mets.items():
        L.append(f"| {m['variant']} VIX {m['vix_filter']} | {m['trades']} | {pct(m['win_rate'])} | {rs(m['expectancy_rs'])} | {rs(m['total_rs'])} | {rs(m['annual_rs'])} | {rs(m['max_dd_rs'])} |")
    L.append("")

    L.append(f"## Does it beat doing nothing (a Nifty index fund), after tax?\n")
    L.append(f"F&O profits taxed at {TAX_FO:.0%} as business income; index-fund gains at {TAX_LTCG:.1%} LTCG (no exemption, no dividends, "
             f"which understates the fund by roughly 1-1.5% a year). The fund is assumed to hold the same capital the strategy needs "
             f"(max defined loss x max concurrent positions). Strategy capital is assumed idle; parking it in a liquid fund would add about 6% a year pre-tax to the strategy side.\n")
    L.append("| Run | Period | Strategy after tax Rs/lot | Nifty fund after tax Rs/lot | Strategy CAGR | Nifty CAGR | Verdict |")
    L.append("|---|---|---|---|---|---|---|")
    beats = 0
    for k, m in mets.items():
        if k.endswith("_RAW"):
            continue
        win = m["strat_after_tax_rs"] > m["bench_after_tax_rs"]
        beats += win
        L.append(f"| {m['variant']} VIX {m['vix_filter']} | {m['period_start'].year}-{m['period_end'].year} | {rs(m['strat_after_tax_rs'])} | "
                 f"{rs(m['bench_after_tax_rs'])} | {pct(m['strat_cagr_after_tax'])} | {pct(m['bench_cagr_after_tax'])} | {'beats' if win else 'loses to'} the index fund |")
    L.append("")
    n = len([k for k in mets if not k.endswith("_RAW")])
    if beats == 0:
        verdict = ("**Plain verdict: no.** In none of the headline runs does the strategy beat a Nifty index fund after tax, over the full period or from 2021. "
                   "The exit rules (50% take profit against a 1.5x stop) need a win rate above 75% just to break even before costs, "
                   "and the realised win rate does not clear that bar once costs and slippage are charged.")
    elif beats == n:
        verdict = "**Plain verdict: yes**, in every headline run the strategy beats the Nifty index fund after tax, but read the drawdown and holdout rows before believing it."
    else:
        verdict = (f"**Plain verdict: mixed.** {beats} of {n} headline runs beat the index fund after tax. Treat the result as fragile: it flips with the VIX filter, the period, "
                   "or the slippage assumption, and a strategy that only wins under one setting has not been shown to win.")
    L.append(verdict + "\n")

    L.append("## What drives the result\n")
    pcs = mets.get("PCS_OFF", next(iter(mets.values())))
    L.append(f"- Breakeven win rate implied by the exit rules is {pct(pcs['breakeven_win_rate_rules'])}; realised avg win / avg loss implies "
             f"{pct(pcs['breakeven_win_rate_empirical'])} (put spread, VIX OFF, full period). Realised win rate {pct(pcs['win_rate'])}.")
    L.append(f"- Costs and slippage: average credit {pcs['avg_credit_pts']:.1f} pts; 1 pt slippage per leg per trade is {4 / pcs['avg_credit_pts'] * 100:.0f}% of the credit on a 2-leg spread round trip, more on a condor. See the slippage table: the sign of the result can depend on it.")
    worst = grid.sort_values("total_rs").iloc[0]; best = grid.sort_values("total_rs").iloc[-1]
    L.append(f"- In-sample grid (36 rule combos x 2 variants x 2 filters): best total Rs {rs(best['total_rs'])} "
             f"({best['variant']} VIX {best['vix_filter']}, delta {best['delta']:.2f}, width {best['width']:.0f}, SL {best['stop_mult']}x, TP {best['take_profit']:.0%}); "
             f"worst Rs {rs(worst['total_rs'])}. Share of grid points with positive total: {(grid['total_rs'] > 0).mean():.0%}. The base case was fixed before looking at this grid.")
    for _, r in stress_eq.iterrows():
        if r["run_id"] in ("PCS_OFF", "IC_OFF"):
            L.append(f"- {r['window']}, {r['run_id']}: equity change inside the window Rs {rs(r['equity_change_in_window_rs'])} on {r['trades_touching_window']} trades touching it.")
    L.append("")
    L.append("## Data-quality handling that matters\n")
    raw = {k: v for k, v in mets.items() if k.endswith("_RAW")}
    L.append("About 6% of pre-expiry option rows (5-9% of near-the-money rows, mostly 50-step strikes with no volume) carry an NSE "
             "settlement price that violates strike monotonicity, by a median of ~45 points. They are flagged `value_suspect` in the dataset. "
             "The backtest never enters on such a strike and, when an open leg lands on one, prices that leg by interpolating between the "
             "clean neighbouring strikes and counts it (Summary sheet). The `_RAW` runs below use raw `value` everywhere, as literally specified:\n")
    for k, mm in raw.items():
        L.append(f"- {mm['variant']} VIX OFF, raw value: {mm['trades']} trades, total Rs {rs(mm['total_rs'])}, max DD Rs {rs(mm['max_dd_rs'])} "
                 f"(vs Rs {rs(mets[k.replace('_RAW','')]['total_rs'])} with suspect handling).")
    L.append("")
    L.append("## Caveats you should not ignore\n")
    L.append("- 2019-2020 prices for untraded strikes are NSE theoretical settlement prices, not trades. The 2021+ rows are the ones to trust more; both are reported.")
    L.append("- No bid/ask in bhavcopy: slippage is an assumption. Exits on untraded legs are priced at the settlement value and counted (Summary sheet, by year).")
    L.append("- Stops are checked once a day at the close. An intraday gap through the stop (June 2024, March 2020) is only caught at the close, so real losses on those days can be larger than modelled.")
    L.append("- Capital at risk here is the full defined loss; broker margin is different and changes daily. The CAGR comparison depends entirely on this capital base.")
    L.append("- One position per week with up to several open at once; no position sizing, no compounding, no lot-size history (everything at 65 units).")
    L.append("")
    L.append("## Sources for cost rates\n")
    for name, url in SOURCES:
        L.append(f"- [{name}]({url})")
    path.write_text("\n".join(L) + "\n")
