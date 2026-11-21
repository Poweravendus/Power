"""Parse the two NSE F&O bhavcopy formats and the index close file into the standard schema.

Standard F&O columns produced here (before spot/VIX join and derived columns):
  trade_date, symbol, instrument (OPT|FUT), expiry, strike, option_type (CE|PE|''),
  open, high, low, close, settle, contracts_traded, open_interest, underlying (NaN for the
  old format, which has no underlying column), source_format ('old'|'udiff').
"""
from __future__ import annotations

import datetime as dt
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from . import config

NUMERIC = ["open", "high", "low", "close", "settle", "contracts_traded", "open_interest", "underlying"]
BASE_COLUMNS = ["trade_date", "symbol", "instrument", "expiry", "strike", "option_type", *NUMERIC, "source_format"]


class ParseError(ValueError):
    pass


def _read_zip_csv(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        name = z.namelist()[0]
        with z.open(name) as f:
            return pd.read_csv(io.TextIOWrapper(f, encoding="utf-8", errors="replace"), dtype=str)


def _finish(df: pd.DataFrame, file_date: dt.date, fmt: str) -> pd.DataFrame:
    for c in NUMERIC:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["strike"] = pd.to_numeric(df["strike"], errors="coerce").astype(float)
    df["symbol"] = df["symbol"].str.strip()
    df["option_type"] = df["option_type"].fillna("").str.strip()
    df["source_format"] = fmt
    df["expiry"] = pd.to_datetime(df["expiry"]).dt.date
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date
    bad_dates = df["trade_date"] != file_date
    if bad_dates.any():
        raise ParseError(f"{fmt} file for {file_date}: {int(bad_dates.sum())} rows carry a different trade date "
                         f"({sorted(df.loc[bad_dates, 'trade_date'].unique())[:3]})")
    df = df[BASE_COLUMNS].reset_index(drop=True)
    df.loc[df["instrument"] == "FUT", "strike"] = 0.0
    return df


def parse_old(path: Path, file_date: dt.date, symbol: str = config.SYMBOL) -> pd.DataFrame:
    """Old format: INSTRUMENT,SYMBOL,EXPIRY_DT,STRIKE_PR,OPTION_TYP,OPEN,HIGH,LOW,CLOSE,SETTLE_PR,
    CONTRACTS,VAL_INLAKH,OPEN_INT,CHG_IN_OI,TIMESTAMP,(trailing empty column)."""
    raw = _read_zip_csv(path)
    raw.columns = [c.strip() for c in raw.columns]
    required = ["INSTRUMENT", "SYMBOL", "EXPIRY_DT", "STRIKE_PR", "OPTION_TYP", "OPEN", "HIGH", "LOW",
                "CLOSE", "SETTLE_PR", "CONTRACTS", "OPEN_INT", "TIMESTAMP"]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise ParseError(f"old-format file {path.name} missing columns {missing}; has {list(raw.columns)}")
    sel = raw[(raw["SYMBOL"].str.strip() == symbol) & (raw["INSTRUMENT"].isin(["OPTIDX", "FUTIDX"]))].copy()
    df = pd.DataFrame({
        "trade_date": pd.to_datetime(sel["TIMESTAMP"].str.strip(), format="%d-%b-%Y"),
        "symbol": sel["SYMBOL"],
        "instrument": np.where(sel["INSTRUMENT"] == "OPTIDX", "OPT", "FUT"),
        "expiry": pd.to_datetime(sel["EXPIRY_DT"].str.strip(), format="%d-%b-%Y"),
        "strike": sel["STRIKE_PR"],
        "option_type": sel["OPTION_TYP"].replace({"XX": ""}),
        "open": sel["OPEN"], "high": sel["HIGH"], "low": sel["LOW"], "close": sel["CLOSE"],
        "settle": sel["SETTLE_PR"],
        "contracts_traded": sel["CONTRACTS"],
        "open_interest": sel["OPEN_INT"],
        "underlying": np.nan,
    })
    return _finish(df, file_date, "old")


def parse_udiff(path: Path, file_date: dt.date, symbol: str = config.SYMBOL) -> pd.DataFrame:
    """UDiFF format (FinInstrmTp IDO = index option, IDF = index future)."""
    raw = _read_zip_csv(path)
    raw.columns = [c.strip() for c in raw.columns]
    required = ["TradDt", "FinInstrmTp", "TckrSymb", "XpryDt", "StrkPric", "OptnTp", "OpnPric", "HghPric",
                "LwPric", "ClsPric", "SttlmPric", "UndrlygPric", "OpnIntrst", "TtlTradgVol"]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise ParseError(f"UDiFF file {path.name} missing columns {missing}; has {list(raw.columns)}")
    sel = raw[(raw["TckrSymb"].str.strip() == symbol) & (raw["FinInstrmTp"].isin(["IDO", "IDF"]))].copy()
    df = pd.DataFrame({
        "trade_date": pd.to_datetime(sel["TradDt"], format="%Y-%m-%d"),
        "symbol": sel["TckrSymb"],
        "instrument": np.where(sel["FinInstrmTp"] == "IDO", "OPT", "FUT"),
        "expiry": pd.to_datetime(sel["XpryDt"], format="%Y-%m-%d"),
        "strike": sel["StrkPric"],
        "option_type": sel["OptnTp"],
        "open": sel["OpnPric"], "high": sel["HghPric"], "low": sel["LwPric"], "close": sel["ClsPric"],
        "settle": sel["SttlmPric"],
        "contracts_traded": sel["TtlTradgVol"],
        "open_interest": sel["OpnIntrst"],
        "underlying": sel["UndrlygPric"],
    })
    df = _finish(df, file_date, "udiff")
    # NSE carries a second expiry column; they have matched in every file inspected, but a
    # mismatch would matter for dte, so surface it instead of silently using XpryDt.
    if "FininstrmActlXpryDt" in sel.columns:
        actual = pd.to_datetime(sel["FininstrmActlXpryDt"], errors="coerce").dt.date
        listed = pd.to_datetime(sel["XpryDt"]).dt.date
        n = int((actual.notna() & (actual != listed)).sum())
        df.attrs["actual_expiry_mismatches"] = n
    return df


def parse_index_close(path: Path, file_date: dt.date) -> dict:
    """Return {'trade_date','spot_open','spot_high','spot_low','spot_close','vix_close',
    'vix_open','vix_high','vix_low'} with NaN where an index row is absent."""
    raw = pd.read_csv(path, dtype=str)
    raw.columns = [c.strip() for c in raw.columns]
    out = {"trade_date": file_date}
    for key, name in (("spot", config.INDEX_NAME_SPOT), ("vix", config.INDEX_NAME_VIX)):
        rows = raw[raw["Index Name"].str.strip().str.casefold() == name.casefold()]
        if rows.empty:
            for f in ("open", "high", "low", "close"):
                out[f"{key}_{f}"] = np.nan
            continue
        r = rows.iloc[0]
        out[f"{key}_open"] = pd.to_numeric(r["Open Index Value"], errors="coerce")
        out[f"{key}_high"] = pd.to_numeric(r["High Index Value"], errors="coerce")
        out[f"{key}_low"] = pd.to_numeric(r["Low Index Value"], errors="coerce")
        out[f"{key}_close"] = pd.to_numeric(r["Closing Index Value"], errors="coerce")
        d = pd.to_datetime(r["Index Date"], format="%d-%m-%Y", errors="coerce")
        if pd.isna(d) or d.date() != file_date:
            raise ParseError(f"index file {path.name}: '{name}' row dated {r['Index Date']}, expected {file_date}")
        if len(rows) > 1:
            closes = pd.to_numeric(rows["Closing Index Value"], errors="coerce").nunique()
            if closes > 1:
                raise ParseError(f"index file {path.name}: {len(rows)} '{name}' rows with different closes")
    return out
