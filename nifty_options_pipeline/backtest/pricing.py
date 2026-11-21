"""Black-76 pricing, implied volatility and delta (vectorised, numpy + scipy.special)."""
from __future__ import annotations

import numpy as np
from scipy.special import ndtr  # standard normal CDF

SQRT2 = np.sqrt(2.0)


def black76_price(F, K, T, r, sigma, is_call):
    F, K, T, sigma = (np.asarray(x, dtype=float) for x in (F, K, T, sigma))
    is_call = np.asarray(is_call, dtype=bool)
    df = np.exp(-r * T)
    sT = sigma * np.sqrt(T)
    with np.errstate(divide="ignore", invalid="ignore"):
        d1 = (np.log(F / K) + 0.5 * sigma ** 2 * T) / sT
        d2 = d1 - sT
    call = df * (F * ndtr(d1) - K * ndtr(d2))
    put = df * (K * ndtr(-d2) - F * ndtr(-d1))
    return np.where(is_call, call, put)


def black76_delta(F, K, T, r, sigma, is_call):
    F, K, T, sigma = (np.asarray(x, dtype=float) for x in (F, K, T, sigma))
    df = np.exp(-r * T)
    sT = sigma * np.sqrt(T)
    with np.errstate(divide="ignore", invalid="ignore"):
        d1 = (np.log(F / K) + 0.5 * sigma ** 2 * T) / sT
    return np.where(np.asarray(is_call, dtype=bool), df * ndtr(d1), -df * ndtr(-d1))


def implied_vol(price, F, K, T, r, is_call, lo=0.01, hi=4.0, iters=60):
    """Bisection on Black-76. Returns NaN where the price is below discounted intrinsic
    (no vol reproduces it) or above the no-arbitrage cap."""
    price, F, K, T = (np.asarray(x, dtype=float) for x in (price, F, K, T))
    is_call = np.asarray(is_call, dtype=bool)
    df = np.exp(-r * T)
    intrinsic = df * np.where(is_call, np.maximum(F - K, 0), np.maximum(K - F, 0))
    cap = df * np.where(is_call, F, K)
    ok = (price > intrinsic + 1e-9) & (price < cap - 1e-9) & (T > 0)
    lo_a = np.full(price.shape, lo, dtype=float)
    hi_a = np.full(price.shape, hi, dtype=float)
    for _ in range(iters):
        mid = 0.5 * (lo_a + hi_a)
        pm = black76_price(F, K, T, r, mid, is_call)
        above = pm > price
        hi_a = np.where(above, mid, hi_a)
        lo_a = np.where(above, lo_a, mid)
    iv = 0.5 * (lo_a + hi_a)
    iv = np.where(ok, iv, np.nan)
    # price at the vol bounds means the solver pinned to an edge: treat as unsolved
    iv = np.where((iv <= lo * 1.01) | (iv >= hi * 0.99), np.nan, iv)
    return iv
