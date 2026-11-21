"""Assemble the standard-schema dataset from cached raw files.

Steps: parse every cached F&O file (old format up to the cutover, UDiFF after), parse the
index close files into a spot/VIX series, join, derive is_monthly_expiry and dte, and write
Parquet partitioned by year plus one month as a CSV sample.
"""
from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from . import config
from .download import KIND_FO_MKT, KIND_FO_OLD, KIND_FO_UDIFF, KIND_INDEX, MANIFEST_FO, MANIFEST_INDEX
from .manifest import Manifest
from .parse import ParseError, parse_index_close, parse_mkt_report, parse_old, parse_udiff

log = logging.getLogger(__name__)


def chosen_fo_files(manifest: Manifest) -> list[tuple[dt.date, str, Path]]:
    """One (date, kind, path) per trading day: old format up to OLD_FORMAT_LAST_DATE, UDiFF after.

    Inside the overlap window both files exist; the old format is the primary source there
    (it is what the pre-2024 history comes from) and the UDiFF copy is only used by the
    validation report for reconciliation.
    """
    old = {e.date: e for e in manifest.ok_entries(KIND_FO_OLD)}
    new = {e.date: e for e in manifest.ok_entries(KIND_FO_UDIFF)}
    mkt = {e.date: e for e in manifest.ok_entries(KIND_FO_MKT)}
    out = []
    for d in sorted(set(old) | set(new) | set(mkt)):
        if d <= config.OLD_FORMAT_LAST_DATE and d in old:
            out.append((d, KIND_FO_OLD, config.ROOT / old[d].path))
        elif d in new:
            out.append((d, KIND_FO_UDIFF, config.ROOT / new[d].path))
        elif d in old:  # old-format file after the cutover date: unexpected, use it but say so
            log.warning("%s only has an old-format file although it is after the cutover", d)
            out.append((d, KIND_FO_OLD, config.ROOT / old[d].path))
        else:
            log.warning("%s: no bhavcopy in NSE's archive, filling from the market-activity report (no settle)", d)
            out.append((d, KIND_FO_MKT, config.ROOT / mkt[d].path))
    return out


def build_spot_vix(manifest: Manifest | None = None) -> pd.DataFrame:
    manifest = manifest or Manifest(MANIFEST_INDEX)
    rows = []
    for e in manifest.ok_entries(KIND_INDEX):
        try:
            rows.append(parse_index_close(config.ROOT / e.path, e.date))
        except ParseError as err:
            log.error("%s", err)
    df = pd.DataFrame(rows)
    if "date_format_note" not in df.columns:
        df["date_format_note"] = None
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df.sort_values("trade_date").reset_index(drop=True)


def expiry_status(opt: pd.DataFrame, tolerance_days: int = 7) -> pd.DataFrame:
    """One row per option expiry with first/last listing date and a status.

    status = 'expired' (listed through to expiry), 'active' (listed on the last trade date,
    expiry still ahead) or 'removed' (vanished from the listings well before its expiry date:
    NSE re-dated long-dated contracts when it moved the expiry weekday, and the old dates
    linger in the history). Removed expiries must not decide which expiry is the monthly one.
    """
    cal = (opt.groupby("expiry").agg(first_seen=("trade_date", "min"), last_seen=("trade_date", "max"),
                                     rows=("close", "size")).reset_index())
    last_trade = opt["trade_date"].max()
    horizon = cal["expiry"].clip(upper=last_trade)
    alive = cal["last_seen"] >= horizon - pd.Timedelta(days=tolerance_days)
    cal["status"] = np.where(~alive, "removed", np.where(cal["expiry"] > last_trade, "active", "expired"))
    return cal


def last_in_month_flags(cal: pd.DataFrame) -> set[dt.date]:
    """Literal rule: the last expiry date seen in each calendar month (ignoring 'removed' ones)."""
    ex = pd.to_datetime(cal.loc[cal["status"] != "removed", "expiry"])
    last = ex.groupby([ex.dt.year, ex.dt.month]).max()
    return {d.date() for d in last}


def monthly_expiry_flags(cal: pd.DataFrame, fut_expiries: set[dt.date]) -> set[dt.date]:
    """Monthly expiry = an option expiry date on which a NIFTY future also expires (NSE lists
    futures only for monthly expiries). Beyond the horizon of listed futures (long-dated
    options) fall back to the last-in-month rule.

    The literal last-in-month rule is kept as a separate column because it is wrong whenever a
    weekly from the following month is pulled back across the month boundary by a holiday
    (e.g. the 1 May 2025 weekly expired on 30 April 2025), and when a monthly is re-dated at
    short notice (June 2023 appears under both 2023-06-29 and 2023-06-28).
    """
    last_in_month = last_in_month_flags(cal)
    horizon = max(fut_expiries)
    out = set()
    for e in pd.to_datetime(cal["expiry"]).dt.date:
        if e in fut_expiries:
            out.add(e)
        elif e > horizon and e in last_in_month:
            out.add(e)
    return out


def option_value(fo: pd.DataFrame) -> pd.Series:
    """Option value usable for marking a book: `settle` before expiry, intrinsic value against
    `underlying` on expiry day. On dte == 0 NSE's settle column does not hold option values:
    from Feb 2020 it carries the index final settlement price for every strike, and in 2019 /
    Jan 2020 it is 0 for every strike. Futures keep settle (on expiry day that is the index
    final settlement price, which is the right value). Raw `settle` is left untouched."""
    intrinsic_ce = (fo["underlying"] - fo["strike"]).clip(lower=0)
    intrinsic_pe = (fo["strike"] - fo["underlying"]).clip(lower=0)
    intrinsic = np.where(fo["option_type"] == "CE", intrinsic_ce, intrinsic_pe)
    on_expiry_opt = (fo["dte"] == 0) & (fo["instrument"] == "OPT")
    return pd.Series(np.where(on_expiry_opt, intrinsic, fo["settle"]), index=fo.index, dtype="float64")


def build(years: list[int] | None = None, sample_month: str = "2024-07") -> None:
    fo_manifest = Manifest(MANIFEST_FO)
    files = chosen_fo_files(fo_manifest)
    if years:
        files = [f for f in files if f[0].year in years]
    log.info("parsing %d F&O files", len(files))

    frames, problems = [], []
    for d, kind, path in files:
        parser = {KIND_FO_OLD: parse_old, KIND_FO_UDIFF: parse_udiff, KIND_FO_MKT: parse_mkt_report}[kind]
        try:
            df = parser(path, d)
        except (ParseError, Exception) as err:  # noqa: BLE001
            log.error("%s %s: %s", kind, d, err)
            problems.append({"trade_date": d, "kind": kind, "error": str(err)})
            continue
        if df.attrs.get("actual_expiry_mismatches"):
            problems.append({"trade_date": d, "kind": kind,
                             "error": f"{df.attrs['actual_expiry_mismatches']} rows where FininstrmActlXpryDt != XpryDt"})
        frames.append(df)
    fo = pd.concat(frames, ignore_index=True)
    fo["trade_date"] = pd.to_datetime(fo["trade_date"])
    fo["expiry"] = pd.to_datetime(fo["expiry"])

    spot = build_spot_vix()
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    spot.to_parquet(config.SPOT_VIX_PARQUET, index=False)
    log.info("spot/vix series: %d days -> %s", len(spot), config.SPOT_VIX_PARQUET)

    fo = fo.merge(spot[["trade_date", "spot_close", "vix_close"]], on="trade_date", how="left")
    has_file_underlying = fo["underlying"].notna() & (fo["underlying"] > 0)
    fo["underlying_source"] = np.where(has_file_underlying, "file", "spot_join")
    fo["underlying"] = np.where(has_file_underlying, fo["underlying"], fo["spot_close"])
    fo.loc[fo["underlying"].isna(), "underlying_source"] = "missing"

    # Monthly-expiry flag from option expiries only (futures only ever list monthlies, and
    # the validation report checks that every futures expiry is flagged monthly).
    cal = expiry_status(fo[fo["instrument"] == "OPT"])
    fut_expiries = set(fo.loc[fo["instrument"] == "FUT", "expiry"].dt.date)
    monthly = monthly_expiry_flags(cal, fut_expiries)
    last_in_month = last_in_month_flags(cal)
    fo["is_monthly_expiry"] = fo["expiry"].dt.date.isin(monthly)
    fo["is_last_expiry_in_month"] = fo["expiry"].dt.date.isin(last_in_month)
    fo["dte"] = (fo["expiry"] - fo["trade_date"]).dt.days.astype("int32")
    fo["value"] = option_value(fo)
    fo["traded"] = fo["contracts_traded"] > 0
    fo["year"] = fo["trade_date"].dt.year

    fo = fo[config.SCHEMA_COLUMNS + ["year"]].sort_values(
        ["trade_date", "instrument", "expiry", "strike", "option_type"]).reset_index(drop=True)

    config.FO_PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    for y, part in fo.groupby("year"):
        out_dir = config.FO_PARQUET_DIR / f"year={y}"
        out_dir.mkdir(parents=True, exist_ok=True)
        part.drop(columns="year").to_parquet(out_dir / "nifty_fo.parquet", index=False)
        log.info("year %d: %d rows -> %s", y, len(part), out_dir)

    # expiry calendar, handy for the strategy code and for eyeballing
    cal["is_monthly_expiry"] = cal["expiry"].dt.date.isin(monthly)
    cal["is_last_expiry_in_month"] = cal["expiry"].dt.date.isin(last_in_month)
    cal["has_future"] = cal["expiry"].dt.date.isin(fut_expiries)
    cal["weekday"] = cal["expiry"].dt.day_name()
    cal.to_csv(config.EXPIRY_CALENDAR_CSV, index=False)

    # CSV sample for eyeballing
    config.SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    sm = pd.Period(sample_month, freq="M")
    sample = fo[fo["trade_date"].dt.to_period("M") == sm].drop(columns="year")
    sample_path = config.SAMPLE_DIR / f"nifty_fo_sample_{sample_month}.csv"
    sample.to_csv(sample_path, index=False)
    log.info("sample month %s: %d rows -> %s", sample_month, len(sample), sample_path)

    if problems:
        pd.DataFrame(problems).to_csv(config.PROCESSED_DIR / "build_problems.csv", index=False)
        log.warning("%d files had problems, see build_problems.csv", len(problems))
    elif (config.PROCESSED_DIR / "build_problems.csv").exists():
        (config.PROCESSED_DIR / "build_problems.csv").unlink()


def load_fo(years: list[int] | None = None) -> pd.DataFrame:
    parts = sorted(config.FO_PARQUET_DIR.glob("year=*/nifty_fo.parquet"))
    if years:
        parts = [p for p in parts if int(p.parent.name.split("=")[1]) in years]
    df = pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)
    return df
