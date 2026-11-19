
import numpy as np
import pytest

from src.black_scholes import black_scholes


def test_benchmark_prices():
    call = black_scholes(100, 100, 1, 0.05, 0.20, "call")
    put = black_scholes(100, 100, 1, 0.05, 0.20, "put")

    np.testing.assert_allclose(call, 10.4505835722, rtol=1e-9)
    np.testing.assert_allclose(put, 5.5735260223, rtol=1e-9)


def test_put_call_parity():
    S = np.linspace(50, 150, 100)
    K, T, r, sigma = 100, 1, 0.05, 0.20

    call = black_scholes(S, K, T, r, sigma, "call")
    put = black_scholes(S, K, T, r, sigma, "put")

    expected = S - K * np.exp(-r * T)

    np.testing.assert_allclose(call - put, expected, atol=1e-10)


def test_at_maturity():
    call = black_scholes(110, 100, 0, 0.05, 0.20, "call")
    put = black_scholes(110, 100, 0, 0.05, 0.20, "put")

    assert call == 10
    assert put == 0


def test_zero_volatility():
    call = black_scholes(100, 100, 1, 0.05, 0, "call")
    put = black_scholes(100, 100, 1, 0.05, 0, "put")

    np.testing.assert_allclose(call, 100 - 100 * np.exp(-0.05))
    assert put == 0


@pytest.mark.parametrize("S, K, T, r, sigma", [
    (-100, 100, 1, 0.05, 0.20),
    (100, 0, 1, 0.05, 0.20),
    (100, 100, -1, 0.05, 0.20),
    (100, 100, 1, 0.05, -0.20),
    (100, 100, 1, np.nan, 0.20)
])
def test_invalid_inputs(S, K, T, r, sigma):
    with pytest.raises(ValueError):
        black_scholes(S, K, T, r, sigma)
