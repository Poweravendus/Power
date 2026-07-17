"""Backtest of the 'deep dive' cause -> consolidation -> effect swing setup.

Codified template (from the training transcripts):

  CAUSE          >=25-30% rise in <=60 trading days, ending near a 6-month
                 high, ideally with liquidity-factor (20d avg turnover)
                 expansion.
  CONSOLIDATION  shallow correction (winners: <20-25%), 5-60 bars, clean
                 quality (no >5% down day on volume near the end), price
                 undercutting the 10/20/50 DMA depending on how extended
                 the cause was, tight/narrow range near the end.
  EFFECT         the next leg. Entry on day 1-2 of the new move: prior-day
                 narrow bar near the 10DMA, trigger = break of prior day
                 high, not already up >5% in the last 3 days.

Most conditions are recorded as FLAGS rather than hard gates so the
analysis can compare cohorts (template respected vs violated) — that is
how we answer "when does it work, when does it not".

Hard gates only: cause >=25% in <=60 bars near 126d high; consolidation
5-60 bars with drawdown <=40% (25-40% kept as a 'too deep' comparison
cohort); entry trigger as above.

Exits follow the taught R-multiple ladder: 1/3 at +2R (stop -> breakeven),
1/3 at +3R (stop -> +1R), final 1/3 targets +5R with a stop trailed 2R
below the highest high. Same-bar ambiguity resolved pessimistically
(stop assumed hit before target). Simulated at 2/3/5/8% stop widths.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

CACHE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("results")
OUT.mkdir(parents=True, exist_ok=True)

CRORE = 1e7

# ---------- template parameters ----------
CAUSE_MIN_GAIN = 0.25          # hard gate; 30%+ recorded as flag
CAUSE_MAX_BARS = 60
NEAR_HI126 = 0.95              # cause high within 5% of 126d high
CONS_MIN_BARS = 5
CONS_MAX_BARS = 60
CONS_MAX_DD = 0.40             # >40% = broken base, abandoned
SHALLOW_DD = 0.25              # template says winners correct <20-25%
GAP_SKIP = 0.05                # skip entry if open gaps >5% above trigger
MAX_RUNUP_3D = 0.05            # "day 1-2" rule: <=5% up over last 3 closes
STOPS = (0.02, 0.03, 0.05, 0.08)
TIME_STOP_BARS = 60
MFE_WINDOW = 40


def prep(df):
    c, h, l, v = df["close"], df["high"], df["low"], df["volume"]
    out = df.copy()
    out["sma10"] = c.rolling(10).mean()
    out["sma20"] = c.rolling(20).mean()
    out["sma50"] = c.rolling(50).mean()
    out["turn20"] = (c * v).rolling(20).mean()
    out["vol20"] = v.rolling(20).mean()
    out["relvol"] = v / out["vol20"]
    out["adr20"] = (h / l - 1).rolling(20).mean()
    out["range_pct"] = (h - l) / c
    out["ret1"] = c.pct_change()
    out["purple_red"] = (out["ret1"] <= -0.05) & (v > 5e5)
    out["hi126"] = h.rolling(126).max()
    return out


def local_peak(high, p, confirm=5):
    lo = max(0, p - confirm)
    return high[p] >= high[lo:p + confirm + 1].max()


def simulate(df, e_idx, entry, stop_w):
    """R-ladder exit simulation. Returns dict of results for one stop width."""
    h, l, o, c = (df[k].to_numpy() for k in ("high", "low", "open", "close"))
    R = entry * stop_w
    stop = entry - R
    t2, t3, t5 = entry + 2 * R, entry + 3 * R, entry + 5 * R
    thirds_open = 3
    realized = 0.0          # in R units, per full position (sum of thirds/3)
    hit2 = hit3 = False
    maxhigh = entry
    n = len(df)
    for i in range(e_idx, min(n, e_idx + TIME_STOP_BARS + 1)):
        op, hi, li = o[i], h[i], l[i]
        if i == e_idx:
            # entry day: if the stop was touched at all, assume stopped
            # (intraday order unknown — pessimistic); otherwise credit
            # target hits, since price must travel up from the fill
            if li <= stop:
                return dict(exit_idx=i, r=-1.0, hit2=False, hit3=False, days=0)
            if hi >= t2:
                hit2 = True
                realized += (1 / 3.0) * 2.0
                thirds_open -= 1
                stop = max(stop, entry)
            if hit2 and hi >= t3:
                hit3 = True
                realized += (1 / 3.0) * 3.0
                thirds_open -= 1
                stop = max(stop, entry + R)
            maxhigh = max(maxhigh, hi)
            continue
        if li <= stop or op < stop:
            px = op if op < stop else stop
            realized += thirds_open * ((px - entry) / R) / 3.0
            return dict(exit_idx=i, r=realized, hit2=hit2, hit3=hit3, days=i - e_idx)
        maxhigh = max(maxhigh, hi)
        if not hit2 and hi >= t2:
            hit2 = True
            realized += (1 / 3.0) * 2.0
            thirds_open -= 1
            stop = max(stop, entry)                        # breakeven
        if hit2 and not hit3 and hi >= t3:
            hit3 = True
            realized += (1 / 3.0) * 3.0
            thirds_open -= 1
            stop = max(stop, entry + R)                    # +1R
        if hit3:
            if hi >= t5:
                realized += (1 / 3.0) * 5.0
                return dict(exit_idx=i, r=realized, hit2=True, hit3=True, days=i - e_idx)
            stop = max(stop, maxhigh - 2 * R)              # trail final third
    # time stop
    i = min(n - 1, e_idx + TIME_STOP_BARS)
    realized += thirds_open * ((c[i] - entry) / R) / 3.0
    return dict(exit_idx=i, r=realized, hit2=hit2, hit3=hit3, days=i - e_idx)


def excursions(df, e_idx, entry):
    """MFE/MAE and shakeout metrics over MFE_WINDOW bars, exit-scheme-free."""
    end = min(len(df), e_idx + MFE_WINDOW + 1)
    h = df["high"].to_numpy()[e_idx:end]
    l = df["low"].to_numpy()[e_idx:end]
    mfe = h.max() / entry - 1 if len(h) else 0.0
    mae = l.min() / entry - 1 if len(l) else 0.0
    out = dict(mfe=mfe, mae=mae)
    for tgt, tag in ((0.10, "10"), (0.20, "20")):
        idx = np.argmax(h >= entry * (1 + tgt)) if (h >= entry * (1 + tgt)).any() else -1
        out[f"reached_{tag}"] = idx >= 0
        pre_l = l[:idx + 1] if idx >= 0 else l
        dip = pre_l.min() / entry - 1 if len(pre_l) else 0.0
        out[f"dip_before_{tag}"] = dip
    # open-gain giveback: after first +10%, does it fall back to entry
    # before ever reaching +20%?
    hit10 = np.argmax(h >= entry * 1.10) if (h >= entry * 1.10).any() else -1
    gaveback = False
    if hit10 >= 0:
        h20 = np.argmax(h >= entry * 1.20) if (h >= entry * 1.20).any() else len(h) + 1
        seg = l[hit10:min(len(l), h20 if h20 <= len(l) else len(l))]
        gaveback = bool(len(seg)) and seg.min() <= entry
    out["giveback_after_10"] = gaveback
    return out


def scan_symbol(sym, df, segment):
    df = prep(df)
    h = df["high"].to_numpy()
    l = df["low"].to_numpy()
    c = df["close"].to_numpy()
    o = df["open"].to_numpy()
    sma10 = df["sma10"].to_numpy()
    sma20 = df["sma20"].to_numpy()
    sma50 = df["sma50"].to_numpy()
    turn20 = df["turn20"].to_numpy()
    relvol = df["relvol"].to_numpy()
    adr20 = df["adr20"].to_numpy()
    range_pct = df["range_pct"].to_numpy()
    purple_red = df["purple_red"].to_numpy()
    hi126 = df["hi126"].to_numpy()
    n = len(df)
    trades, setups = [], []
    peak_history = []           # (peak_idx, cause_gain) for base counting
    i = 130                      # need warmup for hi126/sma50
    while i < n - 1:
        p = i - 5
        if p < 130 or not local_peak(h, p):
            i += 1
            continue
        # cause: lowest low in the 60 bars before the peak
        w0 = max(0, p - CAUSE_MAX_BARS)
        Lrel = np.argmin(l[w0:p + 1])
        L = w0 + Lrel
        cause_gain = h[p] / l[L] - 1
        cause_bars = p - L
        if cause_gain < CAUSE_MIN_GAIN or cause_bars < 3:
            i += 1
            continue
        if h[p] < NEAR_HI126 * hi126[p]:
            i += 1
            continue
        lf_start = turn20[L]
        lf_end = turn20[p]
        lf_ratio = lf_end / lf_start if lf_start and lf_start > 0 else np.nan

        # base count: prior peaks within 250 bars, chain unbroken
        peak_history = [(pp, gg) for pp, gg in peak_history if p - pp <= 250]
        base_num = 1
        for pp, _ in reversed(peak_history):
            seg_min = l[pp:p + 1].min()
            if seg_min / h[pp] - 1 > -0.35:
                base_num += 1
            else:
                break
        peak_history.append((p, cause_gain))

        # ---- consolidation walk ----
        cons_low = h[p]
        undercut10 = undercut20 = undercut50 = False
        entered = False
        outcome = "stale"
        t = p + 1
        end_t = min(n - 1, p + CONS_MAX_BARS)
        while t <= end_t:
            cons_low = min(cons_low, l[t])
            dd = 1 - cons_low / h[p]
            if l[t] < sma10[t]:
                undercut10 = True
            if l[t] < sma20[t]:
                undercut20 = True
            if l[t] < sma50[t]:
                undercut50 = True
            if dd > CONS_MAX_DD:
                outcome = "broken"
                break
            cons_bars = t - p
            if cons_bars >= CONS_MIN_BARS:
                pv = t - 1
                runup3 = c[pv] / c[max(0, pv - 3):pv + 1].min() - 1
                prior_narrow = range_pct[pv] <= 0.75 * adr20[pv]
                near10 = abs(c[pv] / sma10[pv] - 1) <= 0.08 if sma10[pv] > 0 else False
                trigger = h[t] > h[pv] and c[pv] > 0
                gap_ok = o[t] <= h[pv] * (1 + GAP_SKIP)
                if trigger and gap_ok and runup3 <= MAX_RUNUP_3D and near10:
                    entry = max(o[t], h[pv])
                    ex = excursions(df, t, entry)
                    row = dict(
                        symbol=sym, segment=segment,
                        entry_date=df.index[t], entry=entry,
                        cause_gain=cause_gain, cause_bars=cause_bars,
                        cons_bars=cons_bars, cons_dd=dd,
                        lf_ratio=lf_ratio, base_num=base_num,
                        undercut10=undercut10, undercut20=undercut20,
                        undercut50=undercut50,
                        prior_narrow=bool(prior_narrow),
                        relvol_entry=relvol[t],
                        turn20_cr=turn20[pv] / CRORE,
                        adr20=adr20[pv] * 100,
                        purple_red_10d=bool(purple_red[max(0, t - 10):t].any()),
                        shallow=dd <= SHALLOW_DD,
                        **ex,
                    )
                    for w in STOPS:
                        sim = simulate(df, t, entry, w)
                        row[f"r_{int(w*100)}"] = sim["r"]
                        row[f"days_{int(w*100)}"] = sim["days"]
                        row[f"hit2_{int(w*100)}"] = sim["hit2"]
                    trades.append(row)
                    entered = True
                    outcome = "entered"
                    i = max(sim["exit_idx"], t, i) + 1
                    break
                if h[t] > h[p] * 1.02 and not entered:
                    outcome = "breakout_unqualified"
                    break
            t += 1
        setups.append(dict(symbol=sym, peak_date=df.index[p],
                           cause_gain=cause_gain, outcome=outcome))
        if not entered:
            i = max(t, i) + 1
    return trades, setups


def main():
    uni = pd.read_csv(CACHE / "universe.csv")
    all_trades, all_setups = [], []
    closes_above20 = {}
    for k, (_, r) in enumerate(uni.iterrows()):
        if k % 50 == 0:
            print(f"scanning {k}/{len(uni)} ...", flush=True)
        f = CACHE / f"{r['symbol'].replace('&','_')}.parquet"
        if not f.exists():
            continue
        df = pd.read_parquet(f)
        if len(df) < 300:
            continue
        tr, st = scan_symbol(r["symbol"], df, r["segment"])
        all_trades += tr
        all_setups += st
        closes_above20[r["symbol"]] = (df["close"] > df["close"].rolling(20).mean()).astype("float32")

    trades = pd.DataFrame(all_trades)
    setups = pd.DataFrame(all_setups)

    # market breadth (% of universe above its own 20DMA) + index regime
    breadth = pd.DataFrame(closes_above20).mean(axis=1).rename("breadth")
    idx_f = CACHE / "NIFTY_MIDCAP50.parquet"
    if not idx_f.exists():
        idx_f = CACHE / "NIFTY50.parquet"
    idx = pd.read_parquet(idx_f)
    idx_above = (idx["close"] > idx["close"].rolling(20).mean()).rename("idx_above20")
    env = pd.concat([breadth, idx_above], axis=1).ffill()
    trades = trades.merge(env, left_on="entry_date", right_index=True, how="left")

    trades.to_parquet(OUT / "trades.parquet")
    setups.to_parquet(OUT / "setups.parquet")
    env.to_parquet(OUT / "environment.parquet")
    print(f"symbols scanned: {len(closes_above20)}")
    print(f"setups detected: {len(setups)}; outcomes:\n{setups['outcome'].value_counts()}")
    print(f"trades entered: {len(trades)}  ({trades['entry_date'].min():%Y-%m-%d} .. {trades['entry_date'].max():%Y-%m-%d})")
    stats = {}
    for w in STOPS:
        col = f"r_{int(w*100)}"
        stats[col] = dict(win_rate=float((trades[col] > 0).mean()),
                          avg_r=float(trades[col].mean()),
                          med_r=float(trades[col].median()))
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
