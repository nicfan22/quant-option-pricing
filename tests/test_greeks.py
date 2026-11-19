
import numpy as np
import pytest

from src import greeks as gr


@pytest.mark.parametrize("option_type", ["call", "put"])
def test_delta(option_type):
    analytical = gr.analytical_delta(
        100, 100, 1, 0.05, 0.20, option_type
    )
    numerical = gr.numerical_delta(
        100, 100, 1, 0.05, 0.20, option_type
    )

    np.testing.assert_allclose(analytical, numerical, atol=1e-6)


@pytest.mark.parametrize("option_type", ["call", "put"])
def test_gamma(option_type):
    analytical = gr.analytical_gamma(100, 100, 1, 0.05, 0.20)
    numerical = gr.numerical_gamma(
        100, 100, 1, 0.05, 0.20, option_type
    )

    np.testing.assert_allclose(analytical, numerical, atol=1e-6)


@pytest.mark.parametrize("option_type", ["call", "put"])
def test_vega(option_type):
    analytical = gr.analytical_vega(100, 100, 1, 0.05, 0.20)
    numerical = gr.numerical_vega(
        100, 100, 1, 0.05, 0.20, option_type
    )

    np.testing.assert_allclose(analytical, numerical, atol=1e-5)


@pytest.mark.parametrize("option_type", ["call", "put"])
def test_theta(option_type):
    analytical = gr.analytical_theta(
        100, 100, 1, 0.05, 0.20, option_type
    )
    numerical = gr.numerical_theta(
        100, 100, 1, 0.05, 0.20, option_type
    )

    np.testing.assert_allclose(analytical, numerical, atol=1e-5)


@pytest.mark.parametrize("option_type", ["call", "put"])
def test_rho(option_type):
    analytical = gr.analytical_rho(
        100, 100, 1, 0.05, 0.20, option_type
    )
    numerical = gr.numerical_rho(
        100, 100, 1, 0.05, 0.20, option_type
    )

    np.testing.assert_allclose(analytical, numerical, atol=1e-5)


def test_put_call_greek_parity():
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.20

    # Delta parity
    delta_c = gr.analytical_delta(S, K, T, r, sigma, "call")
    delta_p = gr.analytical_delta(S, K, T, r, sigma, "put")
    np.testing.assert_allclose(delta_c - delta_p, 1)

    # Gamma and Vega equality
    gamma = gr.analytical_gamma(S, K, T, r, sigma)
    vega = gr.analytical_vega(S, K, T, r, sigma)

    assert gamma > 0
    assert vega > 0

    # Theta parity
    theta_c = gr.analytical_theta(S, K, T, r, sigma, "call")
    theta_p = gr.analytical_theta(S, K, T, r, sigma, "put")
    np.testing.assert_allclose(
        theta_c - theta_p,
        -r * K * np.exp(-r * T)
    )

    # Rho parity
    rho_c = gr.analytical_rho(S, K, T, r, sigma, "call")
    rho_p = gr.analytical_rho(S, K, T, r, sigma, "put")
    np.testing.assert_allclose(
        rho_c - rho_p,
        K * T * np.exp(-r * T)
    )


@pytest.mark.parametrize("option_type", ["invalid", "CALL", ""])
def test_invalid_option_type(option_type):
    with pytest.raises(ValueError):
        gr.analytical_delta(
            100, 100, 1, 0.05, 0.20, option_type)
