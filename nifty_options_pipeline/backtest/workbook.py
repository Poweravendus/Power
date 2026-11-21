"""Excel workbook, charts (PNG) and one-page markdown summary."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .costs import schedule_table
from .report import OUT_DIR, STRESS_WINDOWS, TAX_FO, TAX_LTCG

FONT = "Arial"
BLUE, ORANGE = "#2a78d6", "#eb6834"
SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"

METRIC_ROWS = [
    ("Period start", "period_start", "date"), ("Period end", "period_end", "date"),
    ("Trades (closed)", "trades", "int"), ("Winning trades", "wins", "int"), ("Win rate", "win_rate", "pct"),
    ("Average win (pts/unit, net)", "avg_win_pts", "num"), ("Average loss (pts/unit, net)", "avg_loss_pts", "num"),
    ("Expectancy per trade (pts/unit, net)", "expectancy_pts", "num"), ("Expectancy per trade (Rs/lot, net)", "expectancy_rs", "rs"),
    ("Breakeven win rate implied by exit rules", "breakeven_win_rate_rules", "pct"),
    ("Breakeven win rate from realised avg win/loss", "breakeven_win_rate_empirical", "pct"),
    ("Total P&L (pts/unit, net)", "total_pts", "num"), ("Total P&L (Rs/lot, net)", "total_rs", "rs"),
    ("Years in period", "years", "num"), ("Annual P&L (Rs/lot, net)", "annual_rs", "rs"),
    ("Max drawdown (Rs/lot, mark-to-market)", "max_dd_rs", "rs"),
    ("Capital at risk (Rs/lot) = max defined loss x max concurrent", "capital_rs", "rs"),
    ("Max drawdown as % of capital at risk", "max_dd_pct_capital", "pct"),
    ("Worst single trade (Rs/lot)", "worst_trade_rs", "rs"), ("Worst month", "worst_month", "str"),
    ("Worst month P&L (Rs/lot)", "worst_month_rs", "rs"), ("Longest losing streak (trades)", "longest_losing_streak", "int"),
    ("Exits priced on an untraded leg (%)", "exits_untraded_pct", "num"),
    ("Exits priced on an interpolated (suspect-value) leg (%)", "exits_interp_pct", "num"),
    ("Daily exit checks that used an interpolated leg", "checks_interp_total", "int"),
    ("Average credit at entry (pts/unit)", "avg_credit_pts", "num"), ("Average days held", "avg_days_held", "num"),
    ("Max concurrent positions", "max_concurrent", "int"),
    ("Nifty return over period", "nifty_return", "pct"),
    ("Strategy P&L after 30% tax (Rs/lot)", "strat_after_tax_rs", "rs"),
    ("Nifty fund P&L on same capital after 12.5% LTCG (Rs/lot capital)", "bench_after_tax_rs", "rs"),
    ("Strategy CAGR after tax on capital at risk", "strat_cagr_after_tax", "pct"),
    ("Nifty fund CAGR after tax", "bench_cagr_after_tax", "pct"),
]
FMT = {"date": "yyyy-mm-dd", "int": "#,##0", "pct": "0.0%", "num": "#,##0.00;(#,##0.00);-", "rs": "#,##0;(#,##0);-", "str": "@"}

LOG_COLS = ["run_id", "trade_id", "entry_date", "expiry", "dte_at_entry", "short_put", "long_put", "short_call", "long_call",
            "short_put_delta", "short_call_delta", "iv_put", "iv_call", "entry_spot", "entry_future", "entry_vix", "credit_pts",
            "legs_traded_at_entry", "exit_date", "exit_reason", "days_held", "exit_vix", "buyback_pts", "legs_traded_at_exit",
            "untraded_legs_at_exit", "exit_on_interpolated_leg", "exit_checks_skipped", "exit_checks_interpolated", "gross_pnl_pts", "slippage_pts", "costs_rs", "net_pnl_pts", "net_pnl_rs", "max_loss_pts"]


def _style_header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = Font(name=FONT, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E78")
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def _set_font(ws):
    for row in ws.iter_rows():
        for cell in row:
            if cell.font is None or not cell.font.bold:
                cell.font = Font(name=FONT, size=10, bold=cell.font.bold if cell.font else False, color=cell.font.color if cell.font else None)


def _autowidth(ws, minw=8, maxw=60):
    widths = {}
    for row in ws.iter_rows():
        for cell in row:
            if cell.value is not None:
                widths[cell.column] = max(widths.get(cell.column, 0), min(maxw, len(str(cell.value)) + 2))
    for c, w in widths.items():
        ws.column_dimensions[get_column_letter(c)].width = max(minw, w)


def write_df(ws, df: pd.DataFrame, start_row=1, start_col=1, formats: dict | None = None):
    for j, col in enumerate(df.columns):
        ws.cell(row=start_row, column=start_col + j, value=str(col))
    _style_header(ws, start_row, start_col + len(df.columns) - 1)
    for i, (_, r) in enumerate(df.iterrows(), start=1):
        for j, col in enumerate(df.columns):
            v = r[col]
            if isinstance(v, (np.floating, float)) and not np.isfinite(v):
                v = None
            elif isinstance(v, np.generic):
                v = v.item()
            elif isinstance(v, pd.Timestamp):
                v = v.date()
            cell = ws.cell(row=start_row + i, column=start_col + j, value=v)
            if formats and col in formats:
                cell.number_format = formats[col]
            elif isinstance(v, dt.date):
                cell.number_format = "yyyy-mm-dd"
    return start_row + len(df)


# ----------------------------------------------------------------------------- charts
def equity_chart(results: dict, variant: str, path: Path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True, gridspec_kw={"height_ratios": [2, 1]},
                                   facecolor=SURFACE)
    for key, color, label in [(f"{variant}_ON", BLUE, "VIX filter ON"), (f"{variant}_OFF", ORANGE, "VIX filter OFF")]:
        eq = results[key]["equity"]
        x = pd.to_datetime(eq["date"])
        ax1.plot(x, eq["equity_rs"], color=color, lw=2, label=label)
        ax2.fill_between(x, eq["drawdown_rs"], 0, color=color, alpha=0.12, lw=0)
        ax2.plot(x, eq["drawdown_rs"], color=color, lw=1.5, label=label)
    name = "Put credit spread" if variant == "PCS" else "Iron condor"
    ax1.set_title(f"{name}: mark-to-market equity, Rs per lot (lot = 65), net of costs and slippage", loc="left",
                  color=INK, fontsize=11)
    ax2.set_title("Drawdown from peak, Rs per lot", loc="left", color=INK, fontsize=10)
    for ax in (ax1, ax2):
        ax.set_facecolor(SURFACE)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color("#d0cfcb"); ax.spines["bottom"].set_color("#d0cfcb")
        ax.grid(axis="y", color="#e6e5e1", lw=0.8)
        ax.tick_params(colors=INK2, labelsize=9)
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
        ax.axhline(0, color="#b5b4ae", lw=0.8)
    ax1.legend(frameon=False, loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


# ----------------------------------------------------------------------------- workbook
def build_workbook(results: dict, mets: dict, holdout: dict, holdout_mets: dict, grid: pd.DataFrame,
                   slip: pd.DataFrame, trade_log: pd.DataFrame, stress: pd.DataFrame, stress_eq: pd.DataFrame,
                   base_cfg, data_end: dt.date, path: Path):
    wb = Workbook()

    # ---- Assumptions
    wa = wb.active; wa.title = "Assumptions"
    wa["A1"] = "Parameter"; wa["B1"] = "Value"; wa["C1"] = "Note"; _style_header(wa, 1, 3)
    rows = [("Lot size (units) used for all Rs figures", base_cfg.lot, "Today's NIFTY lot; past lot sizes ignored so years are comparable"),
            ("Risk-free rate (Black-76)", base_cfg.r, "annual, continuous"),
            ("Short strike target delta", base_cfg.target_delta, "closest |delta| from Black-76 on `value` with same-expiry future as forward"),
            ("Wing width (points)", base_cfg.width, "protective option this far further OTM"),
            ("Take profit", base_cfg.take_profit, "exit when buyback <= (1 - TP) x gross credit"),
            ("Stop loss multiple", base_cfg.stop_mult, "exit when buyback - credit >= multiple x gross credit (whole position for IC)"),
            ("Time exit (calendar dte)", base_cfg.time_exit_dte, "exit at first close with dte <= this"),
            ("Entry dte window", f"{base_cfg.dte_min}-{base_cfg.dte_max}", "nearest monthly expiry with a listed future"),
            ("Entry day", "first trading day of each ISO week", "one new position per week; ladder"),
            ("VIX filter threshold", base_cfg.vix_min, "skip entries when India VIX close < threshold (filter ON runs)"),
            ("Slippage (pts per leg per trade)", base_cfg.slippage_pts, "entry and exit; doubled when India VIX > 25 that day"),
            ("Price column", "value", "settle before expiry, intrinsic on expiry day; never raw settle/close"),
            ("Suspect values", "value_suspect -> value_interp", "rows whose settle violates strike monotonicity are never used for entry; on exit checks they are replaced by the interpolation between clean neighbours and counted. The *_RAW runs ignore this and use raw value everywhere."),
            ("Entry liquidity rule", "both legs traded", "else nearest traded strike to the target-delta strike whose wing also traded; else skip"),
            ("2021-03-30", "no prices", "no entries, no exit checks; positions carried"),
            ("Credit used for exit thresholds", "gross credit at value", "slippage is charged separately as a cost"),
            ("Tax on F&O profits (summary only)", TAX_FO, "business income, assumed 30%"),
            ("Tax on Nifty fund gains (summary only)", TAX_LTCG, "LTCG, assumed 12.5%, no exemption, no dividends"),
            ("Data end", data_end, "latest NSE bhavcopy")]
    for i, (a, b, c) in enumerate(rows, start=2):
        wa.cell(row=i, column=1, value=a); wa.cell(row=i, column=2, value=b); wa.cell(row=i, column=3, value=c)
        wa.cell(row=i, column=2).font = Font(name=FONT, color="0000FF")
    wa["B2"].comment = Comment("User assumption: convert points to Rs at today's lot of 65.", "backtest")
    r0 = len(rows) + 4
    wa.cell(row=r0 - 1, column=1, value="Cost schedule (verified 2026-11-21; sources in SUMMARY.md)").font = Font(name=FONT, bold=True)
    write_df(wa, pd.DataFrame(schedule_table()), start_row=r0, formats={"rate": "0.00000%"})
    for i in range(r0 + 1, r0 + 1 + len(schedule_table())):
        if wa.cell(row=i, column=1).value.startswith("Brokerage"):
            wa.cell(row=i, column=3).number_format = "#,##0.00"
    _autowidth(wa); wa.column_dimensions["C"].width = 90

    # ---- Trade log (with formulas for net P&L)
    wl = wb.create_sheet("Trade log")
    for j, col in enumerate(LOG_COLS, start=1):
        wl.cell(row=1, column=j, value=col)
    _style_header(wl, 1, len(LOG_COLS))
    ci = {c: i + 1 for i, c in enumerate(LOG_COLS)}
    for i, (_, r) in enumerate(trade_log.iterrows(), start=2):
        for col in LOG_COLS:
            if col in ("net_pnl_pts", "net_pnl_rs"):
                continue
            v = r[col]
            if isinstance(v, (float, np.floating)) and not np.isfinite(v):
                v = None
            elif isinstance(v, np.generic):
                v = v.item()
            elif isinstance(v, pd.Timestamp):
                v = v.date()
            cell = wl.cell(row=i, column=ci[col], value=v)
            if isinstance(v, dt.date):
                cell.number_format = "yyyy-mm-dd"
            elif col in ("credit_pts", "buyback_pts", "gross_pnl_pts", "slippage_pts", "costs_rs", "max_loss_pts", "entry_spot", "entry_future"):
                cell.number_format = "#,##0.00"
            elif col in ("short_put_delta", "short_call_delta", "iv_put", "iv_call"):
                cell.number_format = "0.000"
        g, s, c = (get_column_letter(ci[k]) for k in ("gross_pnl_pts", "slippage_pts", "costs_rs"))
        wl.cell(row=i, column=ci["net_pnl_pts"], value=f"={g}{i}-{s}{i}-{c}{i}/Assumptions!$B$2").number_format = "#,##0.00;(#,##0.00);-"
        n = get_column_letter(ci["net_pnl_pts"])
        wl.cell(row=i, column=ci["net_pnl_rs"], value=f"={n}{i}*Assumptions!$B$2").number_format = "#,##0;(#,##0);-"
    wl.freeze_panes = "C2"
    _autowidth(wl, maxw=18)
    nlog = len(trade_log) + 1
    rng = lambda col: f"'Trade log'!${get_column_letter(ci[col])}$2:${get_column_letter(ci[col])}${nlog}"  # noqa: E731

    # ---- Summary
    ws = wb.create_sheet("Summary", 0)
    ws["A1"] = "Defined-risk monthly option selling on NIFTY: weekly ladder, 16-delta short, 300-pt wings, TP 50%, SL 1.5x, time exit 7 dte"
    ws["A1"].font = Font(name=FONT, bold=True, size=12)
    ws["A2"] = ("Net of brokerage, STT, exchange/SEBI/stamp charges, GST and slippage. Points per unit converted at lot = 65. "
                "Trades, win rate, averages and totals are formulas over the Trade log sheet; drawdown, streak and worst-month "
                "figures come from the daily mark-to-market equity curve computed in Python.")
    ws["A2"].alignment = Alignment(wrap_text=True); ws.merge_cells("A2:I2"); ws.row_dimensions[2].height = 45
    run_keys = [k for k in results]  # ordered
    ws.cell(row=4, column=1, value="Metric")
    for j, k in enumerate(run_keys, start=2):
        m = mets[k]
        ws.cell(row=4, column=j, value=f"{'Put credit spread' if m['variant']=='PCS' else 'Iron condor'}\nVIX filter {m['vix_filter']}\n{m['period_start'].year}-{m['period_end'].year}"
                + ("\nRAW value, no suspect filter" if k.endswith("_RAW") else ""))
    _style_header(ws, 4, 1 + len(run_keys)); ws.row_dimensions[4].height = 48
    formula_rows = {"trades", "wins", "win_rate", "avg_win_pts", "avg_loss_pts", "expectancy_pts", "expectancy_rs", "total_pts", "total_rs", "annual_rs"}
    for i, (label, key, fmt) in enumerate(METRIC_ROWS, start=5):
        ws.cell(row=i, column=1, value=label)
        for j, k in enumerate(run_keys, start=2):
            m = mets[k]
            rid = k
            col = get_column_letter(j)
            if key in formula_rows and k in set(trade_log["run_id"]):
                f = {
                    "trades": f'=COUNTIFS({rng("run_id")},"{rid}")',
                    "wins": f'=COUNTIFS({rng("run_id")},"{rid}",{rng("net_pnl_pts")},">0")',
                    "win_rate": f"=IF({col}{i-2}=0,0,{col}{i-1}/{col}{i-2})",
                    "avg_win_pts": f'=IFERROR(AVERAGEIFS({rng("net_pnl_pts")},{rng("run_id")},"{rid}",{rng("net_pnl_pts")},">0"),0)',
                    "avg_loss_pts": f'=IFERROR(AVERAGEIFS({rng("net_pnl_pts")},{rng("run_id")},"{rid}",{rng("net_pnl_pts")},"<=0"),0)',
                    "expectancy_pts": f'=IFERROR(AVERAGEIFS({rng("net_pnl_pts")},{rng("run_id")},"{rid}"),0)',
                    "expectancy_rs": f"={col}{i-1}*Assumptions!$B$2",
                    "total_pts": f'=SUMIFS({rng("net_pnl_pts")},{rng("run_id")},"{rid}")',
                    "total_rs": f"={col}{i-1}*Assumptions!$B$2",
                    "annual_rs": f"={col}{i-1}/{col}{i+1}",
                }[key]
                cell = ws.cell(row=i, column=j, value=f)
            else:
                v = m.get(key)
                if isinstance(v, (float, np.floating)) and not np.isfinite(v):
                    v = None
                cell = ws.cell(row=i, column=j, value=v)
            cell.number_format = FMT[fmt]
    r = 5 + len(METRIC_ROWS) + 1
    ws.cell(row=r, column=1, value="Exit reasons (count)").font = Font(name=FONT, bold=True)
    for reason in ("take_profit", "stop_loss", "time_exit", "expiry"):
        r += 1; ws.cell(row=r, column=1, value=reason)
        for j, k in enumerate(run_keys, start=2):
            if k in set(trade_log["run_id"]):
                ws.cell(row=r, column=j, value=f'=COUNTIFS({rng("run_id")},"{k}",{rng("exit_reason")},"{reason}")')
            else:
                ws.cell(row=r, column=j, value=mets[k]["exit_reasons"].get(reason, 0))
    r += 2
    ws.cell(row=r, column=1, value="Net P&L by year (Rs/lot, by exit date)").font = Font(name=FONT, bold=True)
    years = sorted({y for k in run_keys for y in mets[k]["pnl_by_year"]})
    for y in years:
        r += 1; ws.cell(row=r, column=1, value=str(y))
        for j, k in enumerate(run_keys, start=2):
            if k in set(trade_log["run_id"]):
                ws.cell(row=r, column=j, value=f'=SUMIFS({rng("net_pnl_rs")},{rng("run_id")},"{k}",{rng("exit_date")},">={y}-01-01",{rng("exit_date")},"<={y}-12-31")').number_format = FMT["rs"]
            else:
                ws.cell(row=r, column=j, value=mets[k]["pnl_by_year"].get(y)).number_format = FMT["rs"]
    r += 2
    ws.cell(row=r, column=1, value="Exits priced on an untraded leg, % of exits by year").font = Font(name=FONT, bold=True)
    for y in years:
        r += 1; ws.cell(row=r, column=1, value=str(y))
        for j, k in enumerate(run_keys, start=2):
            v = mets[k]["untraded_exit_pct_by_year"].get(y)
            ws.cell(row=r, column=j, value=v).number_format = "0.0"
    r += 2
    ws.cell(row=r, column=1, value="Skipped entry weeks (reason: count)").font = Font(name=FONT, bold=True)
    for j, k in enumerate(run_keys, start=2):
        ws.cell(row=r + 1, column=j, value="; ".join(f"{a}: {b}" for a, b in mets[k]["skipped_entries"].items())).alignment = Alignment(wrap_text=True)
    ws.row_dimensions[r + 1].height = 60
    ws.column_dimensions["A"].width = 58
    for j in range(2, 2 + len(run_keys)):
        ws.column_dimensions[get_column_letter(j)].width = 20
    ws.freeze_panes = "B5"

    # ---- Stress periods
    wst = wb.create_sheet("Stress periods")
    wst["A1"] = "Trades open at any point inside each window (base case, full-period runs). Net P&L is the whole trade's result, not only the part inside the window."
    wst["A1"].font = Font(name=FONT, bold=True)
    r = 3
    r = write_df(wst, stress_eq, start_row=r, formats={"equity_change_in_window_rs": FMT["rs"]}) + 2
    cols = ["window", "run_id", "trade_id", "entry_date", "expiry", "short_put", "long_put", "short_call", "long_call", "credit_pts",
            "entry_vix", "exit_date", "exit_reason", "exit_vix", "buyback_pts", "legs_traded_at_exit", "gross_pnl_pts", "slippage_pts",
            "costs_rs", "net_pnl_pts", "net_pnl_rs"]
    write_df(wst, stress[cols], start_row=r, formats={"net_pnl_rs": FMT["rs"], "net_pnl_pts": "#,##0.00", "credit_pts": "#,##0.00",
                                                       "buyback_pts": "#,##0.00", "gross_pnl_pts": "#,##0.00", "costs_rs": "#,##0.00"})
    _autowidth(wst, maxw=22)

    # ---- Sensitivity (in-sample only)
    wsen = wb.create_sheet("Sensitivity")
    wsen["A1"] = f"In-sample grid only ({mets[run_keys[0]]['period_start'].year}-2024). Base case: delta 0.16, width 300, SL 1.5x, TP 50%. Holdout was NOT used here."
    wsen["A1"].font = Font(name=FONT, bold=True)
    r = write_df(wsen, grid, start_row=3, formats={"win_rate": "0.0%", "expectancy_rs": FMT["rs"], "total_rs": FMT["rs"], "annual_rs": FMT["rs"],
                                                   "max_dd_rs": FMT["rs"], "max_dd_pct_capital": "0.0%", "capital_rs": FMT["rs"], "exits_untraded_pct": "0.0",
                                                   "delta": "0.00", "take_profit": "0%"})
    r += 2
    wsen.cell(row=r, column=1, value="Slippage sensitivity, base-case rules, FULL period (doubled when VIX > 25)").font = Font(name=FONT, bold=True)
    write_df(wsen, slip, start_row=r + 1, formats={"win_rate": "0.0%", "expectancy_rs": FMT["rs"], "total_rs": FMT["rs"], "annual_rs": FMT["rs"], "max_dd_rs": FMT["rs"]})
    _autowidth(wsen, maxw=20)
    for j in range(1, 16):
        for i in range(4, 4 + len(grid)):
            c = wsen.cell(row=i, column=j)
            if grid.columns[j - 1] in ("delta", "width", "stop_mult", "take_profit") and \
               (abs(float(grid.iloc[i - 4]["delta"]) - 0.16) < 1e-9 and grid.iloc[i - 4]["width"] == 300 and grid.iloc[i - 4]["stop_mult"] == 1.5 and abs(grid.iloc[i - 4]["take_profit"] - 0.5) < 1e-9):
                c.fill = PatternFill("solid", fgColor="FFF2CC")

    # ---- Holdout
    wh = wb.create_sheet("Holdout")
    wh["A1"] = f"Base-case rules run ONCE on the holdout ({HOLDOUT_START_STR} to {data_end}). Not re-tuned."
    wh["A1"].font = Font(name=FONT, bold=True)
    hkeys = list(holdout)
    wh.cell(row=3, column=1, value="Metric")
    for j, k in enumerate(hkeys, start=2):
        m = holdout_mets[k]
        wh.cell(row=3, column=j, value=f"{'Put credit spread' if m['variant']=='PCS' else 'Iron condor'}\nVIX filter {m['vix_filter']}")
    _style_header(wh, 3, 1 + len(hkeys)); wh.row_dimensions[3].height = 36
    for i, (label, key, fmt) in enumerate(METRIC_ROWS, start=4):
        wh.cell(row=i, column=1, value=label)
        for j, k in enumerate(hkeys, start=2):
            m = holdout_mets[k]; col = get_column_letter(j)
            if key in formula_rows:
                f = {
                    "trades": f'=COUNTIFS({rng("run_id")},"{k}")',
                    "wins": f'=COUNTIFS({rng("run_id")},"{k}",{rng("net_pnl_pts")},">0")',
                    "win_rate": f"=IF({col}{i-2}=0,0,{col}{i-1}/{col}{i-2})",
                    "avg_win_pts": f'=IFERROR(AVERAGEIFS({rng("net_pnl_pts")},{rng("run_id")},"{k}",{rng("net_pnl_pts")},">0"),0)',
                    "avg_loss_pts": f'=IFERROR(AVERAGEIFS({rng("net_pnl_pts")},{rng("run_id")},"{k}",{rng("net_pnl_pts")},"<=0"),0)',
                    "expectancy_pts": f'=IFERROR(AVERAGEIFS({rng("net_pnl_pts")},{rng("run_id")},"{k}"),0)',
                    "expectancy_rs": f"={col}{i-1}*Assumptions!$B$2",
                    "total_pts": f'=SUMIFS({rng("net_pnl_pts")},{rng("run_id")},"{k}")',
                    "total_rs": f"={col}{i-1}*Assumptions!$B$2",
                    "annual_rs": f"={col}{i-1}/{col}{i+1}",
                }[key]
                cell = wh.cell(row=i, column=j, value=f)
            else:
                v = m.get(key)
                if isinstance(v, (float, np.floating)) and not np.isfinite(v):
                    v = None
                cell = wh.cell(row=i, column=j, value=v)
            cell.number_format = FMT[fmt]
    wh.column_dimensions["A"].width = 58
    for j in range(2, 2 + len(hkeys)):
        wh.column_dimensions[get_column_letter(j)].width = 20

    # ---- Capital note
    wc = wb.create_sheet("Capital note")
    wc["A1"] = "Capital needed per lot = max defined loss per position x max number of concurrent positions"
    wc["A1"].font = Font(name=FONT, bold=True)
    wc["A2"] = ("Max defined loss per position = (wing width - credit received) x lot, taken as the largest value across the run's trades. "
                "Capital at risk is the SIMULTANEOUS exposure; cumulative losses over several years can exceed it, which is why drawdown % can exceed 100%. "
                "For an iron condor only one side can be breached, so the width of one side applies. "
                "This is NOT broker margin: NSE SPAN + exposure margin on a short spread is typically lower than the full defined loss for a "
                "hedged spread but is recalculated daily, rises in high-VIX regimes, and the broker may demand more; actual blocked margin will differ.")
    wc["A2"].alignment = Alignment(wrap_text=True); wc.merge_cells("A2:F2"); wc.row_dimensions[2].height = 75
    hdr = ["run_id", "variant", "vix_filter", "period", "max defined loss per position (Rs/lot)", "max concurrent positions", "capital at risk (Rs/lot)", "max drawdown (Rs/lot)", "drawdown % of capital"]
    for j, h in enumerate(hdr, start=1):
        wc.cell(row=4, column=j, value=h)
    _style_header(wc, 4, len(hdr)); wc.row_dimensions[4].height = 36
    all_keys = list(results) + list(holdout)
    for i, k in enumerate(all_keys, start=5):
        m = mets.get(k) or holdout_mets[k]
        wc.cell(row=i, column=1, value=k); wc.cell(row=i, column=2, value=m["variant"]); wc.cell(row=i, column=3, value=m["vix_filter"])
        wc.cell(row=i, column=4, value=f"{m['period_start']} to {m['period_end']}")
        wc.cell(row=i, column=5, value=f'=_xlfn.MAXIFS({rng("max_loss_pts")},{rng("run_id")},"{k}")*Assumptions!$B$2').number_format = FMT["rs"]
        wc.cell(row=i, column=6, value=m["max_concurrent"])
        wc.cell(row=i, column=7, value=f"=E{i}*F{i}").number_format = FMT["rs"]
        wc.cell(row=i, column=8, value=m["max_dd_rs"]).number_format = FMT["rs"]
        wc.cell(row=i, column=9, value=f"=IF(G{i}=0,0,-H{i}/G{i})").number_format = "0.0%"
    _autowidth(wc, maxw=30)

    # ---- Charts
    wch = wb.create_sheet("Charts")
    row = 1
    for variant in ("PCS", "IC"):
        p = OUT_DIR / f"equity_{variant}.png"
        equity_chart(results, variant, p)
        img = XLImage(str(p)); img.width, img.height = 900, 585
        wch.add_image(img, f"A{row}")
        row += 32

    for sh in wb.worksheets:
        for rw in sh.iter_rows():
            for cell in rw:
                f = cell.font
                cell.font = Font(name=FONT, size=f.size or 10, bold=f.bold, color=f.color)
    wb.save(path)


HOLDOUT_START_STR = "2025-01-01"
