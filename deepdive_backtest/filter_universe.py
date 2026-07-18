"""Build a filtered result set: Nifty MidSmallcap 400 constituents only
(midcap 150 + smallcap 250, no microcaps), liquid names (>=25 crore avg
daily turnover at entry), excluding current F&O (derivatives) stocks.

Re-derives market breadth over the restricted universe and re-attaches it,
then writes a trades/environment parquet pair that analyze.py,
export_excel.py and portfolio_sim.py can consume unchanged.

Caveat: the F&O list is today's — like the constituent lists, membership
changes over time and cannot be reconstructed historically from free data.
"""
import sys
from pathlib import Path

import pandas as pd

RES = Path(sys.argv[1])          # original results dir (trades.parquet)
CACHE = Path(sys.argv[2])        # price cache
FO_CSV = Path(sys.argv[3])       # fo_mktlots.csv
OUT = Path(sys.argv[4])          # filtered results dir
OUT.mkdir(parents=True, exist_ok=True)

INDEX_SYMBOLS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "NIFTYNXT50"}

fo = pd.read_csv(FO_CSV, skipinitialspace=True)
fo.columns = [c.strip() for c in fo.columns]
fo_syms = {s.strip() for s in fo["SYMBOL"].astype(str)} - INDEX_SYMBOLS
print(f"F&O stocks: {len(fo_syms)}")

tr = pd.read_parquet(RES / "trades.parquet")
n0 = len(tr)
tr = tr[tr["segment"].isin(["midcap", "smallcap"])]
n1 = len(tr)
tr = tr[~tr["symbol"].isin(fo_syms)]
n2 = len(tr)
tr = tr[tr["turn20_cr"] >= 25]
n3 = len(tr)
print(f"trades: {n0} -> {n1} (MidSmall 400) -> {n2} (no F&O) -> {n3} (>=25cr)")
print(f"symbols remaining: {tr['symbol'].nunique()}")

# breadth over the restricted universe (MidSmall 400 ex-F&O)
uni = pd.read_csv(CACHE / "universe.csv")
uni = uni[uni["segment"].isin(["midcap", "smallcap"])]
uni = uni[~uni["symbol"].isin(fo_syms)]
cols = {}
for s in uni["symbol"]:
    f = CACHE / f"{s.replace('&','_')}.parquet"
    if f.exists():
        c = pd.read_parquet(f)["close"]
        cols[s] = (c > c.rolling(20).mean()).astype("float32")
breadth = pd.DataFrame(cols).mean(axis=1).rename("breadth")
idx = pd.read_parquet(CACHE / "NIFTY_MIDCAP50.parquet")
idx_above = (idx["close"] > idx["close"].rolling(20).mean()).rename("idx_above20")
env = pd.concat([breadth, idx_above], axis=1).ffill()

tr = tr.drop(columns=["breadth", "idx_above20"]).merge(
    env, left_on="entry_date", right_index=True, how="left")
tr.to_parquet(OUT / "trades.parquet")
env.to_parquet(OUT / "environment.parquet")
print(f"breadth universe: {len(cols)} symbols; wrote {OUT}")
