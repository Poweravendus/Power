"""Position engine for the weekly-ladder monthly credit-spread / iron-condor strategy.

All prices come from the `value` column (settle before expiry, intrinsic on expiry day).
Everything is computed in index points per unit; rupee figures use LOT units per lot.
"""
from __future__ import annotations

import datetime as dt
import logging
from dataclasses import dataclass, field, asdict

import numpy as np
import pandas as pd

from pipeline import config as pcfg
from .costs import exercise_cost_rs, order_cost_rs
from .pricing import black76_delta, implied_vol

log = logging.getLogger(__name__)

LOT = 65
RISK_FREE = 0.065
VIX_HIGH = 25.0   # slippage doubles above this


@dataclass
class Config:
    variant: str = "PCS"            # "PCS" put credit spread | "IC" iron condor
    vix_filter: bool = True         # skip entries when VIX < vix_min
    vix_min: float = 11.0
    target_delta: float = 0.16
    width: float = 300.0
    stop_mult: float = 1.5          # stop when loss >= stop_mult * credit
    take_profit: float = 0.50       # exit when buyback <= (1 - take_profit) * credit
    time_exit_dte: int = 7
    dte_min: int = 28
    dte_max: int = 45
    slippage_pts: float = 1.0       # per leg per trade (entry and exit), doubled when VIX > 25
    start: dt.date = dt.date(2019, 1, 1)
    end: dt.date = dt.date(2100, 1, 1)
    lot: int = LOT
    r: float = RISK_FREE
    use_raw_value: bool = False     # True = ignore value_suspect (price everything off raw `value`)

    def label(self) -> str:
        return (f"{self.variant}_vix{'ON' if self.vix_filter else 'OFF'}_d{int(round(self.target_delta * 100))}"
                f"_w{int(self.width)}_sl{self.stop_mult:g}_tp{int(self.take_profit * 100)}_slip{self.slippage_pts:g}"
                + ("_raw" if self.use_raw_value else ""))


def _key(d_ord: int, e_ord: int, strike: float, is_call: bool) -> int:
    return (d_ord * 1_000_000 + e_ord) * 1_000_000 + int(round(strike * 10)) + (0 if is_call else 1)


class MarketData:
    """Loads the Parquet once and exposes fast lookups."""

    def __init__(self, fo: pd.DataFrame | None = None):
        if fo is None:
            from pipeline.build import load_fo
            fo = load_fo()
        fo = fo.copy()
        fo["d_ord"] = fo["trade_date"].map(dt.datetime.toordinal).astype(np.int64)
        fo["e_ord"] = fo["expiry"].map(dt.datetime.toordinal).astype(np.int64)
        self.days: list[dt.date] = sorted(set(fo["trade_date"].dt.date))
        self.day_index = {d: i for i, d in enumerate(self.days)}
        spot = pd.read_parquet(pcfg.SPOT_VIX_PARQUET)
        self.vix = dict(zip(spot["trade_date"].dt.date, spot["vix_close"]))
        self.spot = dict(zip(spot["trade_date"].dt.date, spot["spot_close"]))

        opt = fo[fo["instrument"] == "OPT"]
        keys = (opt["d_ord"].to_numpy() * 1_000_000 + opt["e_ord"].to_numpy()) * 1_000_000 \
            + np.round(opt["strike"].to_numpy() * 10).astype(np.int64) + np.where(opt["option_type"].to_numpy() == "CE", 0, 1)
        self.opt_value = dict(zip(keys.tolist(), opt["value"].to_numpy().tolist()))
        self.opt_traded = dict(zip(keys.tolist(), opt["traded"].to_numpy().tolist()))
        sus = opt["value_suspect"].to_numpy()
        self.opt_suspect = set(keys[sus].tolist())
        self.opt_interp = dict(zip(keys[sus].tolist(), opt.loc[sus, "value_interp"].to_numpy().tolist()))
        fut = fo[fo["instrument"] == "FUT"]
        self.fut_value = dict(zip(zip(fut["trade_date"].dt.date, fut["expiry"].dt.date), fut["value"]))
        # monthly expiries (with a future) sorted
        self.monthly = sorted(set(fut["expiry"].dt.date))
        # option chains for entry selection: (date, expiry) -> DataFrame slice
        self._chain_groups = {k: v for k, v in opt.groupby(["d_ord", "e_ord"])}
        self._delta_cache: dict = {}
        self.missing_value_days = sorted(set(fo.loc[fo["value"].isna(), "trade_date"].dt.date))

    # -- helpers -------------------------------------------------------------------------
    def value(self, d: dt.date, e: dt.date, strike: float, is_call: bool):
        return self.opt_value.get(_key(d.toordinal(), e.toordinal(), strike, is_call))

    def traded(self, d: dt.date, e: dt.date, strike: float, is_call: bool) -> bool:
        return bool(self.opt_traded.get(_key(d.toordinal(), e.toordinal(), strike, is_call), False))

    def suspect(self, d: dt.date, e: dt.date, strike: float, is_call: bool) -> bool:
        return _key(d.toordinal(), e.toordinal(), strike, is_call) in self.opt_suspect

    def price(self, d: dt.date, e: dt.date, strike: float, is_call: bool, use_raw: bool):
        """(price, interpolated) per policy: raw value, or the interpolation on suspect rows.
        None when the row is missing, NaN, or suspect without an interpolation."""
        k = _key(d.toordinal(), e.toordinal(), strike, is_call)
        v = self.opt_value.get(k)
        if v is None or not np.isfinite(v):
            return None, False
        if not use_raw and k in self.opt_suspect:
            vi = self.opt_interp.get(k)
            if vi is None or not np.isfinite(vi):
                return None, False
            return vi, True
        return v, False

    def nearest_monthly(self, d: dt.date, dte_min: int, dte_max: int) -> dt.date | None:
        for e in self.monthly:
            dte = (e - d).days
            if dte > dte_max:
                break
            # require a future listed for this expiry on this date (NSE re-dated some
            # contracts mid-life; the old date must not be picked after the change)
            if dte_min <= dte <= dte_max and (d, e) in self.fut_value:
                return e
        return None

    def delta_table(self, d: dt.date, e: dt.date, r: float, use_raw: bool = False) -> pd.DataFrame | None:
        """IV and delta for every strike of (d, e) from value and the same-expiry future.
        Suspect rows are excluded unless use_raw."""
        key = (d, e, use_raw)
        if key in self._delta_cache:
            return self._delta_cache[key]
        chain = self._chain_groups.get((d.toordinal(), e.toordinal()))
        F = self.fut_value.get((d, e))
        if chain is None or F is None or not np.isfinite(F) or F <= 0:
            self._delta_cache[key] = None
            return None
        if not use_raw:
            chain = chain[~chain["value_suspect"]]
        T = (e - d).days / 365.0
        is_call = (chain["option_type"].to_numpy() == "CE")
        iv = implied_vol(chain["value"].to_numpy(), F, chain["strike"].to_numpy(), T, r, is_call)
        delta = black76_delta(F, chain["strike"].to_numpy(), T, r, iv, is_call)
        tab = pd.DataFrame({"strike": chain["strike"].to_numpy(), "is_call": is_call, "value": chain["value"].to_numpy(),
                            "traded": chain["traded"].to_numpy(), "iv": iv, "delta": delta})
        tab.attrs["F"] = F
        self._delta_cache[key] = tab
        return tab


@dataclass
class Leg:
    is_call: bool
    strike: float
    short: bool                  # True = sold, False = bought (protection)
    entry_value: float
    traded_at_entry: bool
    exit_value: float = np.nan
    traded_at_exit: bool = False
    interp_at_exit: bool = False


@dataclass
class Position:
    pid: int
    entry_date: dt.date
    expiry: dt.date
    legs: list[Leg]
    credit: float                      # gross credit in points (sum short values - long values)
    width: float
    short_put_delta: float = np.nan
    short_call_delta: float = np.nan
    iv_put: float = np.nan
    iv_call: float = np.nan
    entry_vix: float = np.nan
    entry_spot: float = np.nan
    entry_future: float = np.nan
    entry_slippage_pts: float = 0.0
    entry_cost_rs: float = 0.0
    exit_date: dt.date | None = None
    exit_reason: str = ""
    buyback: float = np.nan
    exit_slippage_pts: float = 0.0
    exit_cost_rs: float = 0.0
    exit_vix: float = np.nan
    checks_skipped: int = 0
    checks_interpolated: int = 0

    def side_sign(self):
        return np.array([1.0 if l.short else -1.0 for l in self.legs])


class Backtest:
    def __init__(self, md: MarketData, cfg: Config):
        self.md, self.cfg = md, cfg
        self.trades: list[Position] = []
        self.open: list[Position] = []
        self.equity_rows: list[dict] = []
        self._pid = 0
        self.skipped_entries: dict[str, int] = {}

    # -- selection ---------------------------------------------------------------------
    def _select_side(self, d: dt.date, e: dt.date, is_call: bool):
        """Returns (short_strike, long_strike, short_value, long_value, short_traded, long_traded,
        short_delta, iv) or None. Target strike = |delta| closest to target among all strikes
        with a solvable IV; executed strike = nearest strike to the target whose own row AND
        whose wing row traded that day."""
        cfg = self.cfg
        tab = self.md.delta_table(d, e, cfg.r, cfg.use_raw_value)
        if tab is None:
            return None, "no chain/future"
        side = tab[(tab["is_call"] == is_call) & np.isfinite(tab["delta"])]
        if side.empty:
            return None, "no solvable IV"
        target_row = side.iloc[(side["delta"].abs() - cfg.target_delta).abs().argmin()]
        target_strike = float(target_row["strike"])
        wing_offset = cfg.width if is_call else -cfg.width
        traded_short = side[side["traded"]]
        candidates = []
        for _, row in traded_short.iterrows():
            k = float(row["strike"])
            wing_ok = self.md.traded(d, e, k + wing_offset, is_call) and \
                (cfg.use_raw_value or not self.md.suspect(d, e, k + wing_offset, is_call))
            if wing_ok:
                candidates.append((abs(k - target_strike), k, row))
        if not candidates:
            return None, "no traded strike pair"
        _, k, row = min(candidates, key=lambda t: (t[0], t[1]))
        wing = k + wing_offset
        return (k, wing, float(row["value"]), float(self.md.value(d, e, wing, is_call)),
                True, True, float(row["delta"]), float(row["iv"])), None

    def _slippage(self, d: dt.date, n_legs: int) -> float:
        vix = self.md.vix.get(d, np.nan)
        mult = 2.0 if (np.isfinite(vix) and vix > VIX_HIGH) else 1.0
        return self.cfg.slippage_pts * n_legs * mult

    def _try_entry(self, d: dt.date):
        cfg = self.cfg
        vix = self.md.vix.get(d, np.nan)
        if cfg.vix_filter and (not np.isfinite(vix) or vix < cfg.vix_min):
            self.skipped_entries["vix filter"] = self.skipped_entries.get("vix filter", 0) + 1
            return
        e = self.md.nearest_monthly(d, cfg.dte_min, cfg.dte_max)
        if e is None:
            self.skipped_entries["no monthly in window"] = self.skipped_entries.get("no monthly in window", 0) + 1
            return
        put, why = self._select_side(d, e, is_call=False)
        if put is None:
            self.skipped_entries[f"put side: {why}"] = self.skipped_entries.get(f"put side: {why}", 0) + 1
            return
        legs = [Leg(False, put[0], True, put[2], put[4]), Leg(False, put[1], False, put[3], put[5])]
        call = None
        if cfg.variant == "IC":
            call, why = self._select_side(d, e, is_call=True)
            if call is None:
                self.skipped_entries[f"call side: {why}"] = self.skipped_entries.get(f"call side: {why}", 0) + 1
                return
            legs += [Leg(True, call[0], True, call[2], call[4]), Leg(True, call[1], False, call[3], call[5])]
        credit = sum(l.entry_value if l.short else -l.entry_value for l in legs)
        if credit <= 0:
            self.skipped_entries["non-positive credit"] = self.skipped_entries.get("non-positive credit", 0) + 1
            return
        self._pid += 1
        pos = Position(self._pid, d, e, legs, credit, cfg.width,
                       short_put_delta=put[6], iv_put=put[7],
                       short_call_delta=call[6] if call else np.nan, iv_call=call[7] if call else np.nan,
                       entry_vix=vix, entry_spot=self.md.spot.get(d, np.nan), entry_future=self.md.fut_value.get((d, e), np.nan))
        pos.entry_slippage_pts = self._slippage(d, len(legs))
        pos.entry_cost_rs = sum(order_cost_rs(d, l.entry_value, is_sell=l.short, lot=cfg.lot)["total"] for l in legs)
        self.open.append(pos)

    # -- exits --------------------------------------------------------------------------
    def _leg_values(self, d: dt.date, pos: Position):
        vals, interp = [], []
        for l in pos.legs:
            v, used_interp = self.md.price(d, pos.expiry, l.strike, l.is_call, self.cfg.use_raw_value)
            if v is None:
                return None, None
            vals.append(v); interp.append(used_interp)
        return np.array(vals), interp

    def _close(self, d: dt.date, pos: Position, vals: np.ndarray, reason: str, interp: list[bool]):
        cfg = self.cfg
        pos.exit_date, pos.exit_reason = d, reason
        pos.buyback = float(np.sum(pos.side_sign() * vals))
        pos.exit_vix = self.md.vix.get(d, np.nan)
        for l, v, ip in zip(pos.legs, vals, interp):
            l.exit_value = float(v)
            l.traded_at_exit = self.md.traded(d, pos.expiry, l.strike, l.is_call)
            l.interp_at_exit = bool(ip)
        if reason == "expiry":
            pos.exit_slippage_pts = 0.0
            pos.exit_cost_rs = sum(exercise_cost_rs(d, l.exit_value, cfg.lot)["total"] for l in pos.legs if not l.short)
        else:
            pos.exit_slippage_pts = self._slippage(d, len(pos.legs))
            pos.exit_cost_rs = sum(order_cost_rs(d, l.exit_value, is_sell=not l.short, lot=cfg.lot)["total"] for l in pos.legs)
        self.trades.append(pos)

    def _check_exits(self, d: dt.date):
        cfg = self.cfg
        still_open, unrealised = [], 0.0
        for pos in self.open:
            dte = (pos.expiry - d).days
            vals, interp = self._leg_values(d, pos)
            if vals is None:
                pos.checks_skipped += 1
                still_open.append(pos)
                continue
            if any(interp):
                pos.checks_interpolated += 1
            buyback = float(np.sum(pos.side_sign() * vals))
            pnl = pos.credit - buyback
            if buyback <= (1.0 - cfg.take_profit) * pos.credit:
                self._close(d, pos, vals, "take_profit", interp)
            elif -pnl >= cfg.stop_mult * pos.credit:
                self._close(d, pos, vals, "stop_loss", interp)
            elif dte <= cfg.time_exit_dte and dte > 0:
                self._close(d, pos, vals, "time_exit", interp)
            elif dte <= 0:
                self._close(d, pos, vals, "expiry", interp)
            else:
                unrealised += pnl
                still_open.append(pos)
        self.open = still_open
        return unrealised

    # -- main loop ----------------------------------------------------------------------
    def run(self):
        cfg = self.cfg
        days = [d for d in self.md.days if cfg.start <= d <= cfg.end]
        realised = 0.0
        seen_weeks = set()
        for d in days:
            if d in self.md.missing_value_days:
                # no prices: no exits, no entries; carry positions
                for pos in self.open:
                    pos.checks_skipped += 1
                self.equity_rows.append({"date": d, "realised_pts": realised, "unrealised_pts": np.nan, "n_open": len(self.open)})
                continue
            n_before = len(self.trades)
            unrealised = self._check_exits(d)
            for pos in self.trades[n_before:]:
                realised += net_pnl_pts(pos, cfg.lot)
            wk = d.isocalendar()[:2]
            if wk not in seen_weeks:
                seen_weeks.add(wk)
                self._try_entry(d)
            self.equity_rows.append({"date": d, "realised_pts": realised, "unrealised_pts": unrealised, "n_open": len(self.open)})
        # positions still open at the end are left open (not counted as trades)
        return self

    def trades_frame(self) -> pd.DataFrame:
        rows = []
        for p in self.trades:
            rows.append(trade_row(p, self.cfg))
        df = pd.DataFrame(rows)
        return df

    def equity_frame(self) -> pd.DataFrame:
        eq = pd.DataFrame(self.equity_rows)
        eq["unrealised_pts"] = eq["unrealised_pts"].ffill().fillna(0.0)
        eq["equity_pts"] = eq["realised_pts"] + eq["unrealised_pts"]
        eq["equity_rs"] = eq["equity_pts"] * self.cfg.lot
        eq["peak_rs"] = eq["equity_rs"].cummax()
        eq["drawdown_rs"] = eq["equity_rs"] - eq["peak_rs"]
        return eq


def net_pnl_pts(p: Position, lot: int) -> float:
    gross = p.credit - p.buyback
    return gross - p.entry_slippage_pts - p.exit_slippage_pts - (p.entry_cost_rs + p.exit_cost_rs) / lot


def trade_row(p: Position, cfg: Config) -> dict:
    gross = p.credit - p.buyback
    slip = p.entry_slippage_pts + p.exit_slippage_pts
    cost = p.entry_cost_rs + p.exit_cost_rs
    net = gross - slip - cost / cfg.lot
    puts = [l for l in p.legs if not l.is_call]
    calls = [l for l in p.legs if l.is_call]
    sp = next(l for l in puts if l.short); lp = next(l for l in puts if not l.short)
    sc = next((l for l in calls if l.short), None); lc = next((l for l in calls if not l.short), None)
    return {
        "trade_id": p.pid, "entry_date": p.entry_date, "expiry": p.expiry, "dte_at_entry": (p.expiry - p.entry_date).days,
        "short_put": sp.strike, "long_put": lp.strike,
        "short_call": sc.strike if sc else np.nan, "long_call": lc.strike if lc else np.nan,
        "short_put_delta": p.short_put_delta, "short_call_delta": p.short_call_delta,
        "iv_put": p.iv_put, "iv_call": p.iv_call,
        "entry_spot": p.entry_spot, "entry_future": p.entry_future, "entry_vix": p.entry_vix,
        "credit_pts": p.credit,
        "legs_traded_at_entry": all(l.traded_at_entry for l in p.legs),
        "exit_date": p.exit_date, "exit_reason": p.exit_reason, "days_held": (p.exit_date - p.entry_date).days,
        "exit_vix": p.exit_vix, "buyback_pts": p.buyback,
        "legs_traded_at_exit": all(l.traded_at_exit for l in p.legs),
        "untraded_legs_at_exit": sum(not l.traded_at_exit for l in p.legs),
        "exit_on_interpolated_leg": any(l.interp_at_exit for l in p.legs),
        "exit_checks_skipped": p.checks_skipped, "exit_checks_interpolated": p.checks_interpolated,
        "gross_pnl_pts": gross, "slippage_pts": slip, "costs_rs": cost,
        "net_pnl_pts": net, "net_pnl_rs": net * cfg.lot,
        "max_loss_pts": p.width - p.credit,
    }
