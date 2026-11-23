
"""Black-76 pricing and implied volatility inversion."""

import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq


def black76_price(F, K, T, D, sigma, option_type="C"):
    """Price a European option using the Black-76 model."""

    if option_type not in ("C", "P"):
        raise ValueError("option_type must be 'C' or 'P'")

    if not np.all(np.isfinite([F, K, T, D, sigma])):
        raise ValueError("Model parameters must be finite")

    if min(F, K, T, D, sigma) <= 0:
        raise ValueError("Model parameters must be positive")

    vol_sqrt_t = sigma * np.sqrt(T)

    d1 = (
        np.log(F / K) + 0.5 * sigma**2 * T
    ) / vol_sqrt_t

    d2 = d1 - vol_sqrt_t

    if option_type == "C":
        price = D * (
            F * norm.cdf(d1) - K * norm.cdf(d2)
        )
    else:
        price = D * (
            K * norm.cdf(-d2) - F * norm.cdf(-d1)
        )

    return float(price)


def implied_vol_black76(
    market_price, F, K, T, D,
    option_type="C",
    sigma_min=1e-6,
    sigma_max=5.0
):
    """Recover Black-76 implied volatility using Brent."""

    if option_type not in ("C", "P"):
        raise ValueError("Invalid option type")

    if not np.all(np.isfinite([F, K, T, D])):
        raise ValueError("Invalid model parameters")

    if min(F, K, T, D) <= 0:
        raise ValueError("Model parameters must be positive")

    if not np.isfinite(market_price):
        return np.nan

    if not (0 < sigma_min < sigma_max):
        raise ValueError("Invalid volatility bracket")

    if option_type == "C":
        lower = D * max(F - K, 0)
        upper = D * F
    else:
        lower = D * max(K - F, 0)
        upper = D * K

    if not (lower < market_price < upper):
        return np.nan

    def objective(sigma):
        return (
            black76_price(F, K, T, D, sigma, option_type)
            - market_price
        )

    if objective(sigma_min) * objective(sigma_max) > 0:
        return np.nan

    return float(
        brentq(
            objective,
            sigma_min,
            sigma_max,
            xtol=1e-12
        )
    )
