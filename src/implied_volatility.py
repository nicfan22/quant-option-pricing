
import numpy as np
from scipy.optimize import brentq, newton

from src.black_scholes import black_scholes
from src.greeks import analytical_vega


def _validate_inputs(market_price, S, K, T, r, option_type):
    """Validate model inputs and no-arbitrage price bounds."""

    params = [market_price, S, K, T, r]

    try:
        valid = all(np.isscalar(x) and np.isfinite(x)
            for x in params)
    except TypeError:
        valid = False

    if not valid:
        raise ValueError("Inputs must be finite scalars")

    if S <= 0 or K <= 0 or T <= 0:
        raise ValueError("S, K and T must be positive")

    if option_type not in ("call", "put"):
        raise ValueError("Invalid option type")

    discounted_K = K * np.exp(-r * T)

    if option_type == "call":
        lower_bound = max(S - discounted_K, 0)
        upper_bound = S
    else:
        lower_bound = max(discounted_K - S, 0)
        upper_bound = discounted_K

    if not (lower_bound <= market_price < upper_bound):
        raise ValueError("Price violates implied volatility bounds")

    return lower_bound


def implied_volatility_brent(
    market_price, S, K, T, r,
    option_type="call",
    sigma_upper=5.0):
    """Recover implied volatility using Brent's method."""

    lower_bound = _validate_inputs(
        market_price, S, K, T, r, option_type)

    if not np.isscalar(sigma_upper) or not np.isfinite(sigma_upper):
        raise ValueError("Invalid sigma_upper")

    if sigma_upper <= 0:
        raise ValueError("sigma_upper must be positive")

    if market_price == lower_bound:
        return 0.0

    def objective(sigma):
        return (black_scholes(S, K, T, r, sigma, option_type)
            - market_price)

    if objective(sigma_upper) < 0:
        raise ValueError("Increase sigma_upper")

    implied_sigma = brentq(
        objective, 0.0, sigma_upper, xtol=1e-12)

    return float(implied_sigma)


def implied_volatility_newton(
    market_price, S, K, T, r,
    option_type="call",
    sigma_initial=0.30):
    """Recover implied volatility using Newton-Raphson."""

    lower_bound = _validate_inputs(
        market_price, S, K, T, r, option_type)

    if not np.isscalar(sigma_initial) or not np.isfinite(sigma_initial):
        raise ValueError("Invalid sigma_initial")

    if sigma_initial <= 0:
        raise ValueError("sigma_initial must be positive")

    if market_price == lower_bound:
        return 0.0

    def objective(sigma):
        if sigma <= 0:
            raise ValueError("Newton generated non-positive volatility")

        return (black_scholes(S, K, T, r, sigma, option_type)
            - market_price)

    def derivative(sigma):
        if sigma <= 0:
            raise ValueError("Newton generated non-positive volatility")

        vega = analytical_vega(S, K, T, r, sigma)

        if vega < 1e-10:
            raise ValueError("Vega too close to zero")

        return vega

    implied_sigma = newton(
        func=objective,
        x0=sigma_initial,
        fprime=derivative,
        tol=1e-12,
        maxiter=50)

    return float(implied_sigma)
