
import numpy as np
import pytest

from src.black_scholes import black_scholes
from src import implied_volatility as iv


# Test both root-finding algorithms
@pytest.mark.parametrize("solver", [iv.implied_volatility_brent,iv.implied_volatility_newton])
@pytest.mark.parametrize("option_type", ["call", "put"])
@pytest.mark.parametrize("S, K, T, r, sigma_true", [
    (100, 100, 1, 0.05, 0.20),
    (100, 110, 1, 0.03, 0.25),
    (110, 100, 2, 0.02, 0.35)])
def test_recover_volatility(
    solver, option_type, S, K, T, r, sigma_true):

    # Generate a synthetic option price
    market_price = black_scholes(
        S, K, T, r, sigma_true, option_type)

    # Recover implied volatility
    recovered_sigma = solver(
        market_price, S, K, T, r, option_type)

    # Compare recovered and original volatility
    np.testing.assert_allclose(recovered_sigma,sigma_true,rtol=0,atol=1e-9)


# Zero volatility boundary
@pytest.mark.parametrize("solver", [iv.implied_volatility_brent,iv.implied_volatility_newton])
@pytest.mark.parametrize("option_type", ["call", "put"])
def test_zero_volatility(solver, option_type):

    market_price = black_scholes(100, 100, 1, 0.05, 0, option_type)

    recovered_sigma = solver(market_price, 100, 100, 1, 0.05, option_type)

    np.testing.assert_allclose(recovered_sigma, 0)


# Prices at the unattainable upper bounds
@pytest.mark.parametrize("solver", [iv.implied_volatility_brent,iv.implied_volatility_newton])
@pytest.mark.parametrize("option_type", ["call", "put"])
def test_invalid_market_price(solver, option_type):

    S, K, T, r = 100, 100, 1, 0.05

    if option_type == "call":
        invalid_price = S
    else:
        invalid_price = K * np.exp(-r * T)

    with pytest.raises(ValueError):
        solver(invalid_price, S, K, T, r, option_type)


# Invalid option type
@pytest.mark.parametrize("solver", [iv.implied_volatility_brent,iv.implied_volatility_newton])
def test_invalid_option_type(solver):

    with pytest.raises(ValueError):
        solver(10, 100, 100, 1, 0.05, "invalid")


# Brent: search interval does not contain the root
def test_brent_invalid_bracket():

    market_price = black_scholes(
        100, 100, 1, 0.05, 0.35, "call")

    with pytest.raises(ValueError):
        iv.implied_volatility_brent(
            market_price, 100, 100, 1, 0.05,
            sigma_upper=0.10)


# Newton: initial volatility must be positive
def test_newton_invalid_initial_guess():

    with pytest.raises(ValueError):
        iv.implied_volatility_newton(
            10, 100, 100, 1, 0.05,
            sigma_initial=0)
