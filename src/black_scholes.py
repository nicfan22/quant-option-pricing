
import numpy as np
from scipy.stats import norm


def black_scholes(S, K, T, r, sigma, option_type="call"):
    """
    Price a European call or put under Black-Scholes.

    Supports scalar and NumPy array inputs.
    Assumes no dividends and continuous compounding.
    """

    # Convert inputs to compatible NumPy arrays
    S, K, T, r, sigma = np.broadcast_arrays(
        np.asarray(S, dtype=float),
        np.asarray(K, dtype=float),
        np.asarray(T, dtype=float),
        np.asarray(r, dtype=float),
        np.asarray(sigma, dtype=float)
    )

    # Input validation
    for name, value in [
        ("S", S), ("K", K), ("T", T),
        ("r", r), ("sigma", sigma)
    ]:
        if not np.all(np.isfinite(value)):
            raise ValueError(f"{name} must contain finite values")

    if np.any(S <= 0):
        raise ValueError("Stock price must be positive")

    if np.any(K <= 0):
        raise ValueError("Strike price must be positive")

    if np.any(T < 0):
        raise ValueError("Time to maturity cannot be negative")

    if np.any(sigma < 0):
        raise ValueError("Volatility cannot be negative")

    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")

    # Discounted strike
    discounted_K = K * np.exp(-r * T)

    # Initialize output
    price = np.empty(S.shape, dtype=float)

    # Regular Black-Scholes cases
    regular = (T > 0) & (sigma > 0)

    if np.any(regular):
        d1 = (
            np.log(S[regular] / K[regular])
            + (r[regular] + 0.5 * sigma[regular]**2) * T[regular]
        ) / (sigma[regular] * np.sqrt(T[regular]))

        d2 = d1 - sigma[regular] * np.sqrt(T[regular])

        if option_type == "call":
            price[regular] = (
                S[regular] * norm.cdf(d1)
                - discounted_K[regular] * norm.cdf(d2)
            )
        else:
            price[regular] = (
                discounted_K[regular] * norm.cdf(-d2)
                - S[regular] * norm.cdf(-d1)
            )

    # Boundary cases: T = 0 or sigma = 0
    boundary = ~regular

    if option_type == "call":
        price[boundary] = np.maximum(
            S[boundary] - discounted_K[boundary], 0
        )
    else:
        price[boundary] = np.maximum(
            discounted_K[boundary] - S[boundary], 0
        )

    # Return a scalar for scalar inputs
    return price.item() if price.ndim == 0 else price
