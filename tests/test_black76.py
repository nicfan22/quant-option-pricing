
import numpy as np
import pytest

from src.black76 import black76_price, implied_vol_black76


# Test 1 - Put-call parity
@pytest.mark.parametrize(
    "F,K,T,D,sigma",
    [
        (6500, 6500, 49/365, 0.994219, 0.15),
        (6500, 6200, 32/365, 0.995925, 0.20),
        (6500, 6800, 84/365, 0.989542, 0.25),
    ]
)
def test_put_call_parity(F, K, T, D, sigma):

    call = black76_price(F, K, T, D, sigma, "C")
    put = black76_price(F, K, T, D, sigma, "P")

    expected = D * (F - K)

    assert np.isclose(
        call - put, expected, atol=1e-9
    )


# Test 2 - Implied volatility recovery
@pytest.mark.parametrize("option_type", ["C", "P"])
@pytest.mark.parametrize(
    "F,K,sigma",
    [
        (6500, 6500, 0.15),
        (6500, 6200, 0.20),
        (6500, 6800, 0.25),
    ]
)
def test_implied_volatility_recovery(
    option_type, F, K, sigma
):

    T = 49 / 365
    D = 0.994219

    price = black76_price(
        F, K, T, D, sigma, option_type
    )

    recovered = implied_vol_black76(
        price, F, K, T, D, option_type
    )

    assert np.isclose(
        recovered, sigma, atol=1e-10
    )


# Test 3 - Prices outside no-arbitrage bounds
@pytest.mark.parametrize("option_type", ["C", "P"])
def test_invalid_market_price(option_type):

    recovered = implied_vol_black76(
        market_price=0.0,
        F=6500,
        K=6500,
        T=49/365,
        D=0.994219,
        option_type=option_type
    )

    assert np.isnan(recovered)


# Test 4 - Invalid option type
def test_invalid_option_type():

    with pytest.raises(ValueError):
        black76_price(
            6500, 6500, 1, 0.95, 0.20, "X"
        )


# Test 5 - Invalid model parameters
def test_invalid_parameters():

    with pytest.raises(ValueError):
        black76_price(
            -6500, 6500, 1, 0.95, 0.20, "C"
        )
