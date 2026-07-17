# Deep Dive Backtest — Cause → Consolidation → Effect

A rule-based backtest of the swing-trading setup taught in the training
transcripts: a stock makes a sharp advance (**cause**), rests in a shallow
correction (**consolidation**), then delivers the next leg (**effect**).
Entry is taken on day 1–2 of the effect leg.

## Data

- **Universe:** Nifty Midcap 150 + Smallcap 250 + Microcap 250 constituents
  (current lists from NSE archives), 604 symbols with usable history.
- **Data:** Yahoo Finance daily OHLCV, ~12 years (Feb 2015 – Jul 2026),
  split/bonus adjusted.
- **Sample:** 12,126 setups detected → 11,920 simulated entries.

## Codified template

| Phase | Rule used |
|---|---|
| Cause | ≥25% rise in ≤60 trading days, ending within 5% of the 126-day high |
| Consolidation | 5–60 bars; drawdown ≤40% hard cap (≤20–25% = "shallow" flag); undercut of 10/20/50 DMA required depending on cause size (≤50% → 10DMA, 50–100% → 20DMA, >100% → 50DMA); clean CQ = no >5% down day on volume in last 10 bars |
| Entry | prior day narrow (range ≤ 0.75× ADR20) and near the 10DMA; ≤5% run-up over last 3 closes ("day 1–2" rule); trigger = break of prior day's high; skip if open gaps >5% |
| Exits | taught R-ladder: 1/3 at +2R (stop→breakeven), 1/3 at +3R (stop→+1R), final 1/3 targets +5R with stop trailed 2R under the highest high; 60-bar time stop; same-bar stop-vs-target resolved pessimistically |

Most template conditions are recorded as **flags**, not hard gates, so the
analysis can compare cohorts — that is how "when does it work / when does
it not" is answered. Full tables in [`results/report.md`](results/report.md).

## Key findings

**1. The raw pattern alone is roughly breakeven.** All 11,920 entries at a
5% stop: 34.4% win rate, +0.06R average, profit factor 1.09. The win-rate
band the training claims (30–40%) is exactly what falls out of the data.

**2. The template filters are what create the edge.** The "core template"
cohort (consolidation ≤20% + narrow prior day + clean CQ + undercut rule
respected + ≥1.2× relative volume on entry day + cause ≤100%) — 518 trades:

| stop | win rate | avg R | profit factor |
|---|---|---|---|
| 2% | 40.7% | +0.30R | 1.50 |
| 3% | 46.7% | +0.47R | 1.87 |
| 5% | 43.8% | +0.37R | 1.65 |
| 8% | 46.3% | +0.35R | 1.67 |

Positive expectancy in 11 of 12 years (only 2019 negative).

**3. What matters most (univariate lift at 5% stop):**
- **Relative volume on entry day** is the single strongest condition:
  41.6% win / PF 1.47 with it vs 32.9% / 1.02 without. "All big moves start
  with volume" survives the data.
- **Shallow consolidation** is confirmed and monotonic: 0–10% deep → PF 1.21;
  20–25% → PF 0.81; 25–40% → PF 0.76. The 20% cutoff taught in the
  transcripts is almost exactly where expectancy flips negative.
- **Cause size:** 25–60% causes are the sweet spot (PF ~1.14); stocks already
  up >100% have *negative* expectancy (PF 0.92) — confirms the
  "too extended, wait for the undercut/reset" rule.
- **Undercut rule** (10/20/50 DMA by extension) adds modest but real lift.
- **Narrow prior day** adds modest lift (PF 1.14 vs 1.03).
- **Not confirmed:** base count 1–2 vs 3–4+ showed no lift in this
  daily-bar approximation; the ≥25cr liquidity and ≥3.5% ADR floors are
  execution/velocity constraints, not sources of per-trade edge (slightly
  negative, since illiquid names move more).

**4. Environment filter is confirmed.** Breadth (% of universe above its
20DMA) + index vs 20DMA at entry:
- Strong zone (breadth >65%, index above 20DMA): 37.8% win, PF 1.29
- Weak zone (breadth <20%, index below 20DMA): 27.1% win, PF 0.77
- Core-template trades in strong environment: 46.5% win, PF 1.85.

**5. Shakeouts are the norm, not the exception** (40-bar window,
exit-scheme-free):
- 60.5% of entries reach +10%; 33.5% reach +20%.
- Of eventual +20% winners, **84.6% first dipped ≥2% below entry, 68.2%
  dipped ≥3%, 45.5% dipped ≥5%** — median worst dip among winners is −5.1%.
- A 2% stop kills **76.5%** of eventual +20% winners before they pay;
  a 5% stop kills 41.8%; an 8% stop kills 23.8%.
- Of trades that reached +10%, **41.5% fell all the way back to entry**
  before ever reaching +20% — the "losing your open gains" noise the
  training warns about is a statistical regularity.

The transcript's advice to beginners — start with 5% stops, don't copy the
mentor's 2% stops — is strongly supported: at 2% the raw pattern has PF 0.48
(heavily losing) because the stop sits inside normal winner noise. Tight
stops only work with entry timing precise enough to avoid the initial dip
(intraday technique, which daily bars cannot capture).

## Portfolio simulation

`portfolio_sim.py` trades the 518 core-template signals with the taught
position management (20% of equity per trade, max 5 concurrent names, 5%
stop, R-ladder exits), marked to market daily. 2015–2026:

| strategy | final | CAGR | max drawdown |
|---|---|---|---|
| Deep dive portfolio (always trade) | 4.9x | 14.9% | **−16.6%** |
| Deep dive + environment filter (no entries in weak breadth) | 4.6x | 14.2% | **−10.2%** |
| Nifty Midcap 50 buy & hold | 5.2x | 15.6% | −49.1% |

The system's value is not beating the index on raw return — it is matching
index returns with roughly **one-third of the drawdown**, because it goes
to cash when no qualifying setups exist (e.g., flat through the 2020 crash
while the index halved). The environment filter's main contribution is also
drawdown reduction, not extra return. Note the simulation is unleveraged
and often far below 100% invested. See `results/equity_curve.png`.

**Robustness:** the relative-volume filter (the strongest condition) holds
in both halves of the sample at every threshold tested — PF 1.5–1.9 in
2015–2020 and 1.4–1.7 in 2021–2026 (`results/relvol_stability.md`), so the
edge is not an artifact of one period or a tuned cutoff.

## Caveats

- **Survivorship bias:** universe = *current* index constituents; delisted
  losers are missing. Absolute numbers are optimistic; *relative* cohort
  comparisons are much less affected.
- **Daily bars only:** the taught intraday entries (SVRO/strong-start,
  volume-profile levels) can't be replicated; entry = break of prior day's
  high. Same-bar stop-vs-target ambiguity resolved pessimistically.
- **No costs/slippage/circuit limits** modeled; no portfolio-level position
  sizing — results are per-trade expectancy, not equity curves.
- Pattern rules are one reasonable codification of a discretionary method;
  parameters were set from the transcripts, not optimized (no walk-forward
  tuning was done).

## Files

| file | purpose |
|---|---|
| `fetch_data.py` | download + cache daily OHLCV for the universe (Yahoo) |
| `run_backtest.py` | setup detection state machine + trade simulation |
| `analyze.py` | cohort analysis → `results/report.md` |
| `results/report.md` | full result tables |
| `results/full_template_trades.csv` | the 518 core-template trades |

Reproduce: `python3 fetch_data.py <cache_dir> <lists_dir>` then
`python3 run_backtest.py <cache_dir> <out_dir>` then
`python3 analyze.py <out_dir>`.
