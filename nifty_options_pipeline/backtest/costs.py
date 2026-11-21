"""Indian F&O transaction-cost schedule for NIFTY index options, applied by trade date.

Rates verified 2026-11-21 against broker/exchange notices (see SUMMARY.md sources):
  * STT, sell side, on premium: 0.0625% -> 0.10% from 2024-10-01 -> 0.15% from 2026-04-01.
    STT on exercise (ITM long legs held to expiry): 0.125% of settlement value -> 0.15% from 2026-04-01.
  * NSE transaction charge on premium: 0.05% (Rs 5,000/crore; brokers were on 0.0495%-0.05% slabs)
    -> 0.03503% from 2024-10-01 (SEBI "true to label" circular).
  * SEBI turnover fee: Rs 10 per crore of premium (0.0001%) throughout. (It was Rs 5/crore for
    FY2020-21; the difference is Rs 0.05 per lakh and is ignored.)
  * Stamp duty, buy side, on premium: 0.003% from 2020-07-01 (uniform stamp duty); before that
    Maharashtra charged 0.002%. The pre-July-2020 rate is used for earlier dates.
  * GST 18% on brokerage + exchange transaction charge + SEBI fee.
  * Brokerage: flat Rs 20 per order per leg (discount-broker style), user assumption.
  * IPFT (Rs 0.50 per lakh) and Core SGF contributions are ignored (< Rs 1 per trade).
"""
from __future__ import annotations

import datetime as dt

BROKERAGE_PER_ORDER = 20.0
GST = 0.18
SEBI_FEE = 10.0 / 1e7          # Rs 10 per crore of premium

STT_SELL = [(dt.date(1900, 1, 1), 0.000625), (dt.date(2024, 10, 1), 0.001), (dt.date(2026, 4, 1), 0.0015)]
STT_EXERCISE = [(dt.date(1900, 1, 1), 0.00125), (dt.date(2026, 4, 1), 0.0015)]
NSE_TXN = [(dt.date(1900, 1, 1), 0.0005), (dt.date(2024, 10, 1), 0.0003503)]
STAMP_BUY = [(dt.date(1900, 1, 1), 0.00002), (dt.date(2020, 7, 1), 0.00003)]


def _rate(schedule, d: dt.date) -> float:
    rate = schedule[0][1]
    for eff, r in schedule:
        if d >= eff:
            rate = r
    return rate


def order_cost_rs(d: dt.date, premium_pts: float, is_sell: bool, lot: int) -> dict:
    """Cost in rupees of ONE order for one leg of `lot` units at `premium_pts` per unit."""
    turnover = max(premium_pts, 0.0) * lot
    brokerage = BROKERAGE_PER_ORDER
    stt = turnover * _rate(STT_SELL, d) if is_sell else 0.0
    txn = turnover * _rate(NSE_TXN, d)
    sebi = turnover * SEBI_FEE
    stamp = turnover * _rate(STAMP_BUY, d) if not is_sell else 0.0
    gst = GST * (brokerage + txn + sebi)
    total = brokerage + stt + txn + sebi + stamp + gst
    return {"brokerage": brokerage, "stt": stt, "exchange": txn, "sebi": sebi, "stamp": stamp, "gst": gst, "total": total}


def exercise_cost_rs(d: dt.date, settlement_value_pts: float, lot: int) -> dict:
    """Long ITM option held to expiry: STT on exercise on the settlement value; no brokerage."""
    stt = max(settlement_value_pts, 0.0) * lot * _rate(STT_EXERCISE, d)
    return {"brokerage": 0.0, "stt": stt, "exchange": 0.0, "sebi": 0.0, "stamp": 0.0, "gst": 0.0, "total": stt}


def schedule_table() -> list[dict]:
    rows = []
    for name, sched, note in [
        ("STT on sold option premium", STT_SELL, "sell side only"),
        ("STT on exercise (ITM long leg at expiry)", STT_EXERCISE, "on settlement value"),
        ("NSE transaction charge on premium", NSE_TXN, "both sides"),
        ("Stamp duty on premium", STAMP_BUY, "buy side only"),
    ]:
        for eff, r in sched:
            rows.append({"charge": name, "effective_from": "start" if eff.year == 1900 else eff.isoformat(),
                         "rate": r, "applies_to": note})
    rows.append({"charge": "SEBI turnover fee", "effective_from": "start", "rate": SEBI_FEE, "applies_to": "both sides, Rs 10 per crore"})
    rows.append({"charge": "GST", "effective_from": "start", "rate": GST, "applies_to": "on brokerage + exchange charge + SEBI fee"})
    rows.append({"charge": "Brokerage (Rs per order per leg)", "effective_from": "start", "rate": BROKERAGE_PER_ORDER, "applies_to": "flat, user assumption"})
    return rows
