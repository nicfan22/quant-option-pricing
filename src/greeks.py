
import numpy as np
from scipy.stats import norm

from src.black_scholes import black_scholes


def _d1_d2(S, K, T, r, sigma):
    """Calculate Black-Scholes d1 and d2."""

    d1 = (
        np.log(S / K) + (r + 0.5 * sigma**2) * T
    ) / (sigma * np.sqrt(T))

    d2 = d1 - sigma * np.sqrt(T)

    return d1, d2


def analytical_delta(S, K, T, r, sigma, option_type="call"):

    d1, _ = _d1_d2(S, K, T, r, sigma)

    if option_type == "call":
        return norm.cdf(d1)
    elif option_type == "put":
        return norm.cdf(d1) - 1
    else:
        raise ValueError("Invalid option type")


def analytical_gamma(S, K, T, r, sigma):

    d1, _ = _d1_d2(S, K, T, r, sigma)

    return norm.pdf(d1) / (S * sigma * np.sqrt(T))


def analytical_vega(S, K, T, r, sigma):

    d1, _ = _d1_d2(S, K, T, r, sigma)

    return S * norm.pdf(d1) * np.sqrt(T)


def analytical_theta(S, K, T, r, sigma, option_type="call"):

    d1, d2 = _d1_d2(S, K, T, r, sigma)

    first_term = -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))

    if option_type == "call":
        return first_term - r * K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        return first_term + r * K * np.exp(-r * T) * norm.cdf(-d2)
    else:
        raise ValueError("Invalid option type")


def analytical_rho(S, K, T, r, sigma, option_type="call"):

    _, d2 = _d1_d2(S, K, T, r, sigma)

    if option_type == "call":
        return K * T * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        return -K * T * np.exp(-r * T) * norm.cdf(-d2)
    else:
        raise ValueError("Invalid option type")


def numerical_delta(S, K, T, r, sigma,
                    option_type="call", h=0.01):

    return (
        black_scholes(S + h, K, T, r, sigma, option_type)
        - black_scholes(S - h, K, T, r, sigma, option_type)
    ) / (2 * h)


def numerical_gamma(S, K, T, r, sigma,
                    option_type="call", h=0.1):

    return (
        black_scholes(S + h, K, T, r, sigma, option_type)
        - 2 * black_scholes(S, K, T, r, sigma, option_type)
        + black_scholes(S - h, K, T, r, sigma, option_type)
    ) / h**2


def numerical_vega(S, K, T, r, sigma,
                   option_type="call", h=0.0001):

    return (
        black_scholes(S, K, T, r, sigma + h, option_type)
        - black_scholes(S, K, T, r, sigma - h, option_type)
    ) / (2 * h)


def numerical_theta(S, K, T, r, sigma,
                    option_type="call", h=0.0001):

    return -(
        black_scholes(S, K, T + h, r, sigma, option_type)
        - black_scholes(S, K, T - h, r, sigma, option_type)
    ) / (2 * h)


def numerical_rho(S, K, T, r, sigma,
                  option_type="call", h=0.0001):

    return (
        black_scholes(S, K, T, r + h, sigma, option_type)
        - black_scholes(S, K, T, r - h, sigma, option_type)
    ) / (2 * h)
