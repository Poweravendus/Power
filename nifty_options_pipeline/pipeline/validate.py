"""Validation report (markdown) for the built dataset. Flags, does not fix."""
from __future__ import annotations

import datetime as dt
import logging
import random

import numpy as np
import pandas as pd

from . import config
from .build import load_fo
from .download import KIND_FO_OLD, KIND_FO_UDIFF, KIND_INDEX, MANIFEST_FO, MANIFEST_INDEX
from .holidays import holiday_calendar
from .manifest import Manifest
from .parse import parse_old, parse_udiff

log = logging.getLogger(__name__)

FLAG = "**FLAG**"


def md_table(df: pd.DataFrame, floatfmt: str = "{:,.2f}") -> str:
    if df.empty:
        return "_(none)_\n"
    cols = list(df.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, row in df.iterrows():
        cells = []
        for v in row:
            if isinstance(v, (float, np.floating)):
                cells.append("" if pd.isna(v) else floatfmt.format(v))
            elif isinstance(v, (pd.Timestamp, dt.datetime)):
                cells.append(v.strftime("%Y-%m-%d"))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def _weekday_dates(start: dt.date, end: dt.date) -> list[dt.date]:
    return [start + dt.timedelta(days=i) for i in range((end - start).days + 1)
            if (start + dt.timedelta(days=i)).weekday() < 5]


def section_calendar(fo: pd.DataFrame, spot: pd.DataFrame, fo_m: Manifest, idx_m: Manifest, flags: list[str]) -> str:
    out = ["## 1. Trading-day calendar\n"]
    fo_days = sorted(set(fo["trade_date"].dt.date))
    idx_days = sorted(set(spot["trade_date"].dt.date))
    start, end = fo_days[0], fo_days[-1]
    hol = holiday_calendar(try_api=True)
    hol_map = dict(zip(hol["date"], hol["description"]))
    hol_src = hol["source"].value_counts().to_dict()
    out.append(f"Date range with F&O files: **{start} .. {end}**. Holiday list sources: {hol_src} "
               f"(the NSE holiday API is attempted every run; when it is unreachable only the bundled, "
               f"hand-entered list is used).\n")

    rows = []
    for y in range(start.year, end.year + 1):
        ys, ye = max(start, dt.date(y, 1, 1)), min(end, dt.date(y, 12, 31))
        wd = _weekday_dates(ys, ye)
        fo_y = [d for d in fo_days if d.year == y]
        idx_y = [d for d in idx_days if d.year == y]
        missing = [d for d in wd if d not in set(fo_y)]
        unexplained = [d for d in missing if d not in hol_map]
        weekend_sessions = [d for d in fo_y if d.weekday() >= 5]
        rows.append({"year": y, "fo_trading_days": len(fo_y), "index_days": len(idx_y),
                     "weekdays_without_fo_file": len(missing), "of_which_listed_holidays": len(missing) - len(unexplained),
                     "of_which_NOT_listed": len(unexplained), "weekend_sessions_with_data": len(weekend_sessions)})
    out.append(md_table(pd.DataFrame(rows)))

    all_wd = _weekday_dates(start, end)
    fo_set = set(fo_days)
    unexplained = [d for d in all_wd if d not in fo_set and d not in hol_map]
    out.append("\n### 1a. Weekdays with no F&O file that are NOT in the holiday list\n")
    if unexplained:
        flags.append(f"{len(unexplained)} weekday(s) have no F&O bhavcopy and are not in the holiday list (section 1a)")
        recs = []
        for d in unexplained:
            e_old, e_new, e_idx = fo_m.get(KIND_FO_OLD, d), fo_m.get(KIND_FO_UDIFF, d), idx_m.get(KIND_INDEX, d)
            recs.append({"date": d, "weekday": d.strftime("%a"),
                         "fo_old": e_old.status if e_old else "-", "fo_udiff": e_new.status if e_new else "-",
                         "index_file": e_idx.status if e_idx else "-",
                         "note": "index file exists -> market was open, F&O file missing!" if (e_idx and e_idx.status == "ok")
                                 else "no index file either -> probably a holiday missing from the list"})
        out.append(f"{FLAG} these need a look: either the bundled holiday list is incomplete, or NSE has a gap.\n\n")
        out.append(md_table(pd.DataFrame(recs)))
    else:
        out.append("None. Every weekday without a file is a listed holiday.\n")

    out.append("\n### 1b. Listed holidays that DO have an F&O file (special sessions, or a wrong holiday entry)\n")
    recs = [{"date": d, "weekday": d.strftime("%a"), "holiday_list_entry": hol_map[d],
             "note": hol.loc[hol["date"] == d, "note"].iloc[0]} for d in fo_days if d in hol_map]
    out.append(md_table(pd.DataFrame(recs)))

    out.append("\n### 1c. Weekend dates with an F&O file (special / Muhurat / budget sessions)\n")
    recs = [{"date": d, "weekday": d.strftime("%a"), "option_rows": int((fo["trade_date"].dt.date == d).sum())}
            for d in fo_days if d.weekday() >= 5]
    out.append(md_table(pd.DataFrame(recs)))

    only_fo = sorted(fo_set - set(idx_days))
    only_idx = sorted(set(idx_days) - fo_set)
    out.append("\n### 1d. Days present in only one of the two sources\n")
    out.append(f"- F&O file but no index file: {len(only_fo)} {[str(d) for d in only_fo][:30]}\n")
    out.append(f"- Index file but no F&O file: {len(only_idx)} {[str(d) for d in only_idx][:30]}\n")
    if only_fo:
        flags.append(f"{len(only_fo)} F&O days have no index close file (section 1d) - underlying/vix will be missing there")
    if only_idx:
        flags.append(f"{len(only_idx)} index-file days have no F&O file (section 1d)")
    return "\n".join(out)


def section_formats(fo: pd.DataFrame, fo_m: Manifest, flags: list[str]) -> str:
    out = ["## 2. Row counts per year, per source format\n"]
    old_ok = [e.date for e in fo_m.ok_entries(KIND_FO_OLD)]
    new_ok = [e.date for e in fo_m.ok_entries(KIND_FO_UDIFF)]
    old_404_wd = [e.date for e in fo_m.entries_for(KIND_FO_OLD) if e.status == "404" and e.date.weekday() < 5]
    first_udiff_only = next((d for d in sorted(new_ok) if d in set(old_404_wd)), None)
    out.append(f"- Last date with an old-format file: **{max(old_ok) if old_ok else None}**\n")
    out.append(f"- First date with a UDiFF file: **{min(new_ok) if new_ok else None}** (NSE back-filled UDiFF for 2024)\n")
    out.append(f"- First weekday where only UDiFF exists (observed cutover): **{first_udiff_only}**\n")
    out.append(f"- Configured cutover: old format up to {config.OLD_FORMAT_LAST_DATE}, UDiFF from {config.UDIFF_FIRST_DATE}\n")
    if old_ok and max(old_ok) != config.OLD_FORMAT_LAST_DATE:
        flags.append(f"observed last old-format date {max(old_ok)} != configured {config.OLD_FORMAT_LAST_DATE}")
    if first_udiff_only != config.UDIFF_FIRST_DATE:
        flags.append(f"observed cutover {first_udiff_only} != configured {config.UDIFF_FIRST_DATE}")
    g = fo.groupby([fo["trade_date"].dt.year, "source_format", "instrument"]).size().unstack(["source_format", "instrument"]).fillna(0).astype(int)
    g.columns = [f"{a}_{b}" for a, b in g.columns]
    g.index.name = "year"
    g["trading_days"] = fo.groupby(fo["trade_date"].dt.year)["trade_date"].nunique()
    g["opt_rows_per_day"] = (g.filter(like="_OPT").sum(axis=1) / g["trading_days"]).round(0)
    out.append("\n" + md_table(g.reset_index(), floatfmt="{:,.0f}"))
    errors = [e for k in (KIND_FO_OLD, KIND_FO_UDIFF) for e in fo_m.entries_for(k) if e.status == "error"]
    if errors:
        flags.append(f"{len(errors)} F&O downloads ended in 'error' status (re-run download to retry)")
        out.append(f"\n{FLAG} download errors: {[(e.kind, str(e.date)) for e in errors][:20]}\n")
    return "\n".join(out)


def section_expiries(fo: pd.DataFrame, flags: list[str]) -> str:
    out = ["## 3. Expiry calendar\n"]
    opt = fo[fo["instrument"] == "OPT"]
    cal = (opt.groupby("expiry").agg(first_seen=("trade_date", "min"), last_seen=("trade_date", "max"),
                                     is_monthly=("is_monthly_expiry", "first")).reset_index())
    cal["weekday"] = cal["expiry"].dt.day_name()
    monthly = cal[cal["is_monthly"]]
    out.append("Monthly expiry = last expiry date observed in each calendar month (from option listings).\n")
    out.append("\n### 3a. Monthly expiry dates by year\n")
    for y, grp in monthly.groupby(monthly["expiry"].dt.year):
        items = [f"{d:%Y-%m-%d} ({d:%a})" for d in grp["expiry"]]
        out.append(f"- **{y}** ({len(items)}): " + ", ".join(items) + "\n")

    out.append("\n### 3b. Expiry weekday by year (shows NSE moving the expiry day)\n")
    traded = cal[cal["expiry"] <= fo["trade_date"].max()]
    wk = traded.groupby([traded["expiry"].dt.year, "is_monthly", "weekday"]).size().unstack("weekday").fillna(0).astype(int)
    out.append(md_table(wk.reset_index().rename(columns={"expiry": "year"}), floatfmt="{:.0f}"))

    out.append("\n### 3c. Consistency checks\n")
    fut_exp = set(fo.loc[fo["instrument"] == "FUT", "expiry"].dt.date)
    mon_set = set(monthly["expiry"].dt.date)
    not_monthly_fut = sorted(fut_exp - mon_set)
    out.append(f"- Futures expiries not flagged as monthly: {len(not_monthly_fut)} {[str(d) for d in not_monthly_fut][:20]}\n")
    if not_monthly_fut:
        flags.append(f"{len(not_monthly_fut)} futures expiries are not the last option expiry of their month (section 3c)")
    # months in the traded range without a monthly expiry
    months = pd.period_range(fo["trade_date"].min(), fo["trade_date"].max(), freq="M")
    have = set(pd.to_datetime(monthly["expiry"]).dt.to_period("M"))
    missing_months = [str(m) for m in months if m not in have]
    out.append(f"- Months in range without any option expiry: {missing_months or 'none'}\n")
    if missing_months:
        flags.append(f"months without any expiry: {missing_months}")
    # monthly expiries that are the only expiry in a month and far in the future are long-dated contracts
    far = monthly[monthly["expiry"] > fo["trade_date"].max() + pd.Timedelta(days=120)]
    out.append(f"- Long-dated (quarterly/half-yearly) expiries beyond the data end, flagged monthly by construction: "
               f"{[f'{d:%Y-%m-%d}' for d in far['expiry']]}\n")
    # expiry-day shift: monthly expiry not on the same weekday as the week's regular weekly expiries
    bad_dte = int((fo["dte"] < 0).sum())
    out.append(f"- Rows with expiry before trade date (dte < 0): {bad_dte}\n")
    if bad_dte:
        flags.append(f"{bad_dte} rows with negative dte")
    return "\n".join(out)


def section_liquidity(fo: pd.DataFrame) -> str:
    out = ["## 4. Illiquid strikes: share of option rows with zero contracts traded\n"]
    opt = fo[(fo["instrument"] == "OPT") & fo["underlying"].notna()].copy()
    opt["moneyness_pct"] = (opt["strike"] / opt["underlying"] - 1.0) * 100
    bins = [-np.inf, -20, -10, -5, -2.5, -1, 1, 2.5, 5, 10, 20, np.inf]
    labels = ["< -20%", "-20..-10%", "-10..-5%", "-5..-2.5%", "-2.5..-1%", "-1..+1% (ATM)", "+1..2.5%", "+2.5..5%", "+5..10%", "+10..20%", "> +20%"]
    opt["bucket"] = pd.cut(opt["moneyness_pct"], bins=bins, labels=labels)
    opt["zero_vol"] = opt["contracts_traded"] == 0
    g = opt.groupby("bucket", observed=True).agg(rows=("zero_vol", "size"), zero_volume_share=("zero_vol", "mean")).reset_index()
    g["zero_volume_share"] = (g["zero_volume_share"] * 100).round(1)
    g = g.rename(columns={"bucket": "strike vs underlying", "zero_volume_share": "zero-volume share %"})
    out.append("All years, all expiries, distance = strike / underlying - 1:\n\n" + md_table(g, floatfmt="{:,.1f}"))
    out.append("\nBy year, zero-volume share % (all strikes / within ±2.5% of spot / dte <= 7):\n")
    yr = opt.groupby(opt["trade_date"].dt.year).apply(lambda d: pd.Series({
        "all_strikes": d["zero_vol"].mean() * 100,
        "within_2.5pct": d.loc[d["moneyness_pct"].abs() <= 2.5, "zero_vol"].mean() * 100,
        "dte_le_7": d.loc[d["dte"] <= 7, "zero_vol"].mean() * 100,
        "dte_gt_60": d.loc[d["dte"] > 60, "zero_vol"].mean() * 100,
    }), include_groups=False).round(1).reset_index().rename(columns={"trade_date": "year"})
    out.append(md_table(yr, floatfmt="{:,.1f}"))
    stale = opt[opt["zero_vol"] & (opt["close"] != opt["settle"])]
    out.append(f"\nNote: on zero-volume rows `close` is NSE's last traded price (possibly days old) while `settle` is the "
               f"exchange settlement price; they differ on {len(stale):,} of {int(opt['zero_vol'].sum()):,} zero-volume rows "
               f"({len(stale) / max(1, int(opt['zero_vol'].sum())) * 100:.1f}%). Use `settle` for illiquid strikes.\n")
    return "\n".join(out)


def _atm_pair(day: pd.DataFrame, expiry) -> tuple[float, float, float] | None:
    o = day[(day["instrument"] == "OPT") & (day["expiry"] == expiry)]
    ce = o[o["option_type"] == "CE"].set_index("strike")["close"]
    pe = o[o["option_type"] == "PE"].set_index("strike")["close"]
    strikes = ce.index.intersection(pe.index)
    if len(strikes) == 0:
        return None
    S = float(day["underlying"].iloc[0])
    K = float(strikes[np.argmin(np.abs(strikes - S))])
    return K, float(ce[K]), float(pe[K])


def section_spot_checks(fo: pd.DataFrame, seed: int, flags: list[str]) -> str:
    out = ["## 5. Spot checks: ATM call/put vs underlying and put-call parity vs the same-expiry future\n"]
    out.append("Parity used: C - P = (F - K) * exp(-r*T) with r = 6.5%; `implied_fwd` = K + (C - P) * exp(r*T). "
               "Residual is reported in index points and as % of spot. Only monthly expiries have a same-expiry future; "
               "for the nearest weekly expiry the implied forward is compared with spot instead.\n")
    rng = random.Random(seed)
    days = sorted(set(fo.loc[fo["underlying"].notna(), "trade_date"]))
    picks = sorted(rng.sample(days, 5))
    r = 0.065
    rows_m, rows_w = [], []
    for d in picks:
        day = fo[fo["trade_date"] == d]
        S = float(day["underlying"].iloc[0])
        futs = day[(day["instrument"] == "FUT") & (day["dte"] >= 1)].sort_values("expiry")
        if futs.empty:
            continue
        f = futs.iloc[0]
        pair = _atm_pair(day, f["expiry"])
        if pair:
            K, C, P = pair
            T = f["dte"] / 365
            resid = (C - P) - (f["close"] - K) * np.exp(-r * T)
            rows_m.append({"trade_date": d, "spot": S, "expiry": f["expiry"], "dte": int(f["dte"]), "atm_strike": K,
                           "call_close": C, "put_close": P, "future_close": f["close"],
                           "implied_fwd": K + (C - P) * np.exp(r * T),
                           "parity_resid_pts": resid, "resid_pct_spot": resid / S * 100,
                           "atm_call_pct_spot": C / S * 100})
            if abs(resid) / S * 100 > 0.5:
                flags.append(f"put-call parity residual {resid:.1f} pts ({resid / S * 100:.2f}% of spot) on {d:%Y-%m-%d} (section 5)")
        wk = day[(day["instrument"] == "OPT") & (~day["is_monthly_expiry"]) & (day["dte"] >= 1)]
        if not wk.empty:
            e = wk["expiry"].min()
            pair = _atm_pair(day, e)
            if pair:
                K, C, P = pair
                T = int((e - d).days) / 365
                fwd = K + (C - P) * np.exp(r * T)
                rows_w.append({"trade_date": d, "spot": S, "weekly_expiry": e, "dte": int((e - d).days), "atm_strike": K,
                               "call_close": C, "put_close": P, "implied_fwd": fwd,
                               "fwd_minus_spot_pct": (fwd / S - 1) * 100, "next_monthly_future": f["close"]})
    out.append("\n### 5a. Nearest monthly expiry (future exists)\n" + md_table(pd.DataFrame(rows_m)))
    out.append("\n### 5b. Nearest weekly expiry (no same-expiry future; implied forward vs spot)\n" + md_table(pd.DataFrame(rows_w)))
    out.append("\nWhat 'roughly holds' means here: a residual within about 0.1-0.3% of spot is normal (bid-ask, "
               "stale closes, dividend/rate assumptions). Weekly implied forwards sit slightly above spot by the carry; "
               "a weekly implied forward far from spot or from the monthly future would be a flag.\n")
    return "\n".join(out)


def section_spot_vix(fo: pd.DataFrame, spot: pd.DataFrame, flags: list[str]) -> str:
    out = ["## 6. NIFTY 50 spot and India VIX series\n"]
    s = spot.sort_values("trade_date").reset_index(drop=True)
    n = len(s)
    na_spot = s[s["spot_close"].isna() | (s["spot_close"] <= 0)]
    na_vix = s[s["vix_close"].isna() | (s["vix_close"] <= 0)]
    out.append(f"- Index-file days: {n}; days with missing/zero Nifty 50 close: {len(na_spot)}; missing/zero India VIX close: {len(na_vix)}\n")
    if len(na_spot):
        flags.append(f"{len(na_spot)} index-file days with no Nifty 50 close (section 6)")
        out.append(md_table(na_spot[["trade_date", "spot_close", "vix_close"]]))
    if len(na_vix):
        flags.append(f"{len(na_vix)} index-file days with no India VIX close (section 6)")
        out.append(md_table(na_vix[["trade_date", "spot_close", "vix_close"]]))
    fo_days = sorted(set(fo["trade_date"]))
    miss_u = sorted(set(fo.loc[fo["underlying"].isna(), "trade_date"]))
    miss_v = sorted(set(fo.loc[fo["vix_close"].isna(), "trade_date"]))
    out.append(f"- F&O days with no underlying at all: {len(miss_u)} {[f'{d:%Y-%m-%d}' for d in miss_u][:20]}\n")
    out.append(f"- F&O days with no VIX close: {len(miss_v)} {[f'{d:%Y-%m-%d}' for d in miss_v][:20]}\n")
    if miss_u:
        flags.append(f"{len(miss_u)} F&O days have no underlying (section 6)")
    if miss_v:
        flags.append(f"{len(miss_v)} F&O days have no VIX close (section 6)")
    # big jumps
    s["spot_ret_pct"] = s["spot_close"].pct_change() * 100
    s["vix_chg_pct"] = s["vix_close"].pct_change() * 100
    s["gap_days"] = s["trade_date"].diff().dt.days
    big = s[(s["spot_ret_pct"].abs() > 7) | (s["vix_chg_pct"].abs() > 40)]
    out.append("\n### 6a. Large day-over-day moves (|spot| > 7% or |VIX| > 40%) - check these are real events\n")
    out.append(md_table(big[["trade_date", "spot_close", "spot_ret_pct", "vix_close", "vix_chg_pct"]]))
    gaps = s[s["gap_days"] > 5]
    out.append("\n### 6b. Gaps of more than 5 calendar days between consecutive index-file days\n")
    out.append(md_table(gaps[["trade_date", "gap_days"]], floatfmt="{:.0f}"))
    if len(gaps):
        flags.append(f"{len(gaps)} gaps > 5 calendar days in the spot/VIX series (section 6b)")
    # UDiFF underlying vs index close
    ud = fo[(fo["source_format"] == "udiff") & (fo["underlying_source"] == "file")]
    if not ud.empty:
        per_day = ud.groupby("trade_date")["underlying"].first().to_frame("file_underlying").join(
            s.set_index("trade_date")["spot_close"])
        per_day["diff"] = per_day["file_underlying"] - per_day["spot_close"]
        bad = per_day[per_day["diff"].abs() > 0.5]
        out.append(f"\n### 6c. UDiFF `UndrlygPric` vs Nifty 50 close from the index file\n- days compared: {len(per_day)}; "
                   f"days differing by > 0.5 pts: {len(bad)}\n")
        if len(bad):
            flags.append(f"{len(bad)} days where UDiFF underlying != index close (section 6c)")
            out.append(md_table(bad.reset_index().head(20)))
        nuniq = ud.groupby("trade_date")["underlying"].nunique()
        multi = nuniq[nuniq > 1]
        out.append(f"- days where UDiFF rows carry more than one underlying value for NIFTY: {len(multi)}\n")
        if len(multi):
            flags.append(f"{len(multi)} days with several UndrlygPric values for NIFTY (section 6c)")
    return "\n".join(out)


def section_overlap(fo_m: Manifest, flags: list[str]) -> str:
    out = ["## 7. Old-format vs UDiFF reconciliation on overlap dates (Jan-Jul 2024)\n"]
    old = {e.date: e for e in fo_m.ok_entries(KIND_FO_OLD)}
    new = {e.date: e for e in fo_m.ok_entries(KIND_FO_UDIFF)}
    both = sorted(set(old) & set(new))
    out.append(f"Dates with both files: {len(both)}" + (f" ({both[0]} .. {both[-1]})" if both else "") + "\n")
    if not both:
        return "\n".join(out)
    key = ["instrument", "expiry", "strike", "option_type"]
    cols = ["open", "high", "low", "close", "settle", "contracts_traded", "open_interest"]
    recs, mism_total = [], 0
    for d in both:
        try:
            a = parse_old(config.ROOT / old[d].path, d)
            b = parse_udiff(config.ROOT / new[d].path, d)
        except Exception as e:  # noqa: BLE001
            recs.append({"date": d, "error": str(e)})
            continue
        m = a.merge(b, on=key, how="outer", suffixes=("_o", "_n"), indicator=True)
        only_old = int((m["_merge"] == "left_only").sum())
        only_new = int((m["_merge"] == "right_only").sum())
        inner = m[m["_merge"] == "both"]
        mism = {c: int(((inner[c + "_o"] - inner[c + "_n"]).abs() > 0.011).sum()) for c in cols}
        tot = sum(mism.values()) + only_old + only_new
        mism_total += tot
        recs.append({"date": d, "rows_old": len(a), "rows_udiff": len(b), "only_in_old": only_old, "only_in_udiff": only_new,
                     **{f"diff_{c}": v for c, v in mism.items()}})
    df = pd.DataFrame(recs)
    out.append(f"Total contract-days with any difference: **{mism_total}**\n\n")
    summary = df.drop(columns="date").sum(numeric_only=True).to_frame("total").T
    out.append(md_table(summary, floatfmt="{:,.0f}"))
    bad = df[(df.drop(columns=["date", "rows_old", "rows_udiff"], errors="ignore").sum(axis=1, numeric_only=True) > 0)]
    if len(bad):
        flags.append(f"{len(bad)} overlap dates where old-format and UDiFF files disagree (section 7)")
        out.append("\nDates with differences:\n" + md_table(bad, floatfmt="{:,.0f}"))
    return "\n".join(out)


def section_integrity(fo: pd.DataFrame, flags: list[str]) -> str:
    out = ["## 8. Row-level integrity\n"]
    key = ["trade_date", "instrument", "expiry", "strike", "option_type"]
    dups = int(fo.duplicated(key).sum())
    out.append(f"- Duplicate contract-days: {dups}\n")
    if dups:
        flags.append(f"{dups} duplicate contract-day rows (section 8)")
    opt = fo[fo["instrument"] == "OPT"]
    bad_ot = int((~opt["option_type"].isin(["CE", "PE"])).sum())
    bad_fut_ot = int((fo.loc[fo["instrument"] == "FUT", "option_type"] != "").sum())
    out.append(f"- Option rows with option_type not CE/PE: {bad_ot}; futures rows with a non-blank option_type: {bad_fut_ot}\n")
    if bad_ot or bad_fut_ot:
        flags.append("option_type anomalies (section 8)")
    neg = int((fo[["open", "high", "low", "close", "settle"]] < 0).any(axis=1).sum())
    out.append(f"- Rows with a negative price: {neg}\n")
    hl = fo[(fo["contracts_traded"] > 0) & ((fo["high"] < fo["low"]) | (fo["close"] > fo["high"] + 1e-9) | (fo["close"] < fo["low"] - 1e-9))]
    out.append(f"- Traded rows where close is outside [low, high] or high < low: {len(hl)}\n")
    if len(hl):
        flags.append(f"{len(hl)} traded rows with close outside the day's range (section 8)")
    zero_close_oi = int(((fo["close"] <= 0) & (fo["open_interest"] > 0)).sum())
    out.append(f"- Rows with close <= 0 but open interest > 0: {zero_close_oi}\n")
    zs = opt[opt["settle"] <= 0]
    zs_expiry = zs[zs["dte"] == 0]
    zs_dead = zs[(zs["dte"] > 0) & (zs["open_interest"] == 0) & (zs["contracts_traded"] == 0)]
    zs_live = zs[(zs["dte"] > 0) & ((zs["open_interest"] > 0) | (zs["contracts_traded"] > 0))]
    out.append(f"- Option rows with settle <= 0: {len(zs):,} = expiry-day rows expiring worthless {len(zs_expiry):,} "
               f"(expected) + untraded zero-OI strikes before expiry {len(zs_dead):,} (old format leaves settle at 0 "
               f"for strikes nobody holds; `close` there is a stale last-traded price) + rows WITH OI or volume but "
               f"settle 0 before expiry {len(zs_live):,}\n")
    if len(zs_live):
        share_novol = (zs_live["contracts_traded"] == 0).mean() * 100
        flags.append(f"{len(zs_live)} option rows with open interest/volume but settle = 0 before expiry "
                     f"({share_novol:.0f}% of them untraded that day, so `close` is a stale print there) (section 8)")
        out.append(md_table(zs_live.groupby(zs_live["trade_date"].dt.year).size().to_frame("rows").reset_index()
                            .rename(columns={"trade_date": "year"}), floatfmt="{:.0f}"))
    if len(zs_dead):
        flags.append(f"{len(zs_dead):,} pre-expiry option rows have settle = 0 (untraded, zero OI; mostly old format). "
                     f"Treat settle=0 as 'no price', not a price (section 8)")
    nans = fo[["open", "high", "low", "close", "settle", "contracts_traded", "open_interest"]].isna().sum()
    out.append(f"- NaN counts: {nans[nans > 0].to_dict() or 'none'}\n")
    fut_per_day = fo[fo["instrument"] == "FUT"].groupby("trade_date").size()
    out.append(f"- Futures rows per day: min {fut_per_day.min()}, max {fut_per_day.max()} (NSE lists 3 monthly futures)\n")
    if fut_per_day.min() < 3 or fut_per_day.max() > 3:
        flags.append(f"days with != 3 NIFTY futures rows: {int((fut_per_day != 3).sum())} (section 8)")
    # strike grid sanity
    opt_live = opt[opt["dte"] <= 35]
    step = opt_live.groupby(["trade_date", "expiry"])["strike"].apply(lambda s: np.diff(np.sort(s.unique())).min() if s.nunique() > 1 else np.nan)
    out.append(f"- Minimum strike step on near expiries by year: {step.groupby(level=0).min().groupby(lambda d: d.year).min().to_dict()}\n")
    out.append("- Units: `contracts_traded` is in contracts (lots); `open_interest` is in units of underlying "
               "(lots x lot size) in BOTH formats, consistent with each other on the overlap dates. Lot size changed over "
               "time (75 -> 50 -> 25 -> 75), so OI is not comparable across years without dividing by lot size.\n")
    probs = config.PROCESSED_DIR / "build_problems.csv"
    if probs.exists():
        p = pd.read_csv(probs)
        flags.append(f"{len(p)} files had parse problems during build (see data/processed/build_problems.csv)")
        out.append("\n" + FLAG + " build problems:\n" + md_table(p.head(30)))
    return "\n".join(out)


def write_report(seed: int = 42) -> None:
    fo = load_fo()
    spot = pd.read_parquet(config.SPOT_VIX_PARQUET)
    fo_m, idx_m = Manifest(MANIFEST_FO), Manifest(MANIFEST_INDEX)
    flags: list[str] = []
    sections = [
        section_calendar(fo, spot, fo_m, idx_m, flags),
        section_formats(fo, fo_m, flags),
        section_expiries(fo, flags),
        section_liquidity(fo),
        section_spot_checks(fo, seed, flags),
        section_spot_vix(fo, spot, flags),
        section_overlap(fo_m, flags),
        section_integrity(fo, flags),
    ]
    head = [f"# NIFTY options data validation report\n",
            f"Generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M UTC}. Rows: {len(fo):,}; "
            f"trade dates: {fo['trade_date'].nunique():,} ({fo['trade_date'].min():%Y-%m-%d} .. {fo['trade_date'].max():%Y-%m-%d}); "
            f"spot-check seed {seed}.\n",
            "## 0. Flags\n"]
    head.append("\n".join(f"- {FLAG} {f}" for f in flags) + "\n" if flags else "No flags raised.\n")
    config.REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    config.REPORT_MD.write_text("\n".join(head + sections))
    log.info("report written to %s (%d flags)", config.REPORT_MD, len(flags))
