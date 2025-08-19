import pytest
from jax.numpy import array, linspace
from pytest import approx

from streamfitter.mean import Mean

DIGITS_10_1s = array([1.1, 0.9, 1.2, 0.8, 1.3, 0.7, 1.4, 0.6, 1.5, 0.5])

EXPECTED_MEAN = 1.0
EXPECT_STANDARD_DEVIATION = 0.3496029493900505


def test_mean_estimate():
    xs = linspace(1, 4, 10)

    fitter = Mean()
    assert fitter.estimate(xs, DIGITS_10_1s) is None


def test_mean_fit():
    xs = linspace(1, 4, 10)

    fitter = Mean()
    results = fitter.fit(xs, DIGITS_10_1s)

    assert approx(EXPECTED_MEAN) == results.params['mean'].value


def test_mean_function():
    xs = linspace(1, 4, 10)

    fitter = Mean()
    with pytest.raises(NotImplementedError):
        fitter.function(DIGITS_10_1s, xs=xs)
