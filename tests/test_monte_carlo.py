
import numpy as np
import pytest

from src.monte_carlo import monte_carlo_price
from src.black_scholes import black_scholes


def test_reproducibility():
    # Same seed should produce identical results
    result1 = monte_carlo_price(
        100, 100, 1, 0.05, 0.20,
        n_simulations=10000, seed=42
    )

    result2 = monte_carlo_price(
        100, 100, 1, 0.05, 0.20,
        n_simulations=10000, seed=42
    )

    assert result1 == result2


def test_black_scholes_consistency():
    # Compare Monte Carlo with analytical pricing
    mc = monte_carlo_price(
        100, 100, 1, 0.05, 0.20,
        n_simulations=100000, seed=42
    )

    bs = black_scholes(
        100, 100, 1, 0.05, 0.20, "call"
    )

    # Check whether BS is within 5 standard errors
    error = abs(mc["price"] - bs)

    assert error < 5 * mc["standard_error"]


def test_confidence_interval():
    result = monte_carlo_price(
        100, 100, 1, 0.05, 0.20,
        n_simulations=10000, seed=42
    )

    assert result["ci_lower"] < result["price"]
    assert result["price"] < result["ci_upper"]
    assert result["standard_error"] > 0


def test_at_maturity():
    # At T=0 the payoff is known
    call = monte_carlo_price(
        110, 100, 0, 0.05, 0.20,
        seed=42
    )

    put = monte_carlo_price(
        110, 100, 0, 0.05, 0.20,
        option_type="put", seed=42
    )

    np.testing.assert_allclose(call["price"], 10)
    np.testing.assert_allclose(put["price"], 0)


def test_zero_volatility():
    # At sigma=0 the price is deterministic
    result = monte_carlo_price(
        100, 100, 1, 0.05, 0,
        seed=42
    )

    expected = 100 - 100 * np.exp(-0.05)

    np.testing.assert_allclose(result["price"], expected)


@pytest.mark.parametrize("S0, K, T, r, sigma", [
    (-100, 100, 1, 0.05, 0.20),
    (100, 0, 1, 0.05, 0.20),
    (100, 100, -1, 0.05, 0.20),
    (100, 100, 1, 0.05, -0.20),
    (100, 100, 1, np.nan, 0.20)
])
def test_invalid_inputs(S0, K, T, r, sigma):
    with pytest.raises(ValueError):
        monte_carlo_price(S0, K, T, r, sigma)
