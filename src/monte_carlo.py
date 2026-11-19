
import numpy as np


def monte_carlo_price(S0, K, T, r, sigma,
                      n_simulations=10000,
                      option_type="call",
                      seed=None):
    """
    Price a European option using Monte Carlo simulation
    under the risk-neutral Geometric Brownian Motion.

    Returns the estimated price, standard error,
    and approximate 95% confidence interval.
    """

    # Input validation
    parameters = [S0, K, T, r, sigma]

    if not all(np.isscalar(x) and np.isfinite(x)
               for x in parameters):
        raise ValueError("Model parameters must be finite scalars")

    if S0 <= 0 or K <= 0:
        raise ValueError("Stock price and strike must be positive")

    if T < 0 or sigma < 0:
        raise ValueError("Maturity and volatility cannot be negative")

    if type(n_simulations) not in (int, np.int64, np.int32):
        raise ValueError("n_simulations must be an integer")

    if n_simulations < 2:
        raise ValueError("At least 2 simulations are required")

    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")

    # Generate random shocks
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal(n_simulations)

    # Simulate terminal stock prices
    ST = S0 * np.exp(
        (r - 0.5 * sigma**2) * T
        + sigma * np.sqrt(T) * Z
    )

    # Calculate option payoffs
    if option_type == "call":
        payoffs = np.maximum(ST - K, 0)
    else:
        payoffs = np.maximum(K - ST, 0)

    # Discounted payoffs
    discounted_payoffs = np.exp(-r * T) * payoffs

    # Monte Carlo price
    price = np.mean(discounted_payoffs)

    # Standard error
    standard_error = (
        np.std(discounted_payoffs, ddof=1)
        / np.sqrt(n_simulations)
    )

    # Approximate 95% confidence interval
    margin = 1.96 * standard_error
    ci_lower = price - margin
    ci_upper = price + margin

    return {
        "price": float(price),
        "standard_error": float(standard_error),
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper)}
