from jax.numpy import array
from pytest import approx

from streamfitter.LinearLeastSquares import LinearLeastSquares

EXPONENTIAL_A_2_5_O_1 = array(
    [
        2.5,
        1.841715953,
        1.47232383,
        1.265041669,
        1.148726534,
        1.083456997,
        1.046831391,
        1.026279152,
        1.014746388,
        1.008274847,
    ]
)

# amplitude = 2.5 time_constant = 1.3
EXPONENTIAL_A_m0_5_O_1 = array(
    [
        -0.5,
        0.158284047,
        0.52767617,
        0.734958331,
        0.851273466,
        0.916543003,
        0.953168609,
        0.973720848,
        0.985253612,
        0.991725153,
    ]
)


def test_estimate():
    fitter = LinearLeastSquares()
    assert fitter.estimate(EXPONENTIAL_A_2_5_O_1, EXPONENTIAL_A_m0_5_O_1) is None


def test_linear_equation():
    fitter = LinearLeastSquares()
    ys = fitter.function(-1.0, 2.0, EXPONENTIAL_A_2_5_O_1)

    assert approx(ys) == EXPONENTIAL_A_m0_5_O_1


def test_linear_fit():
    fitter = LinearLeastSquares()
    results = fitter.fit(EXPONENTIAL_A_2_5_O_1, EXPONENTIAL_A_m0_5_O_1)

    assert approx(-1.0) == results['slope']
    assert approx(2.0) == results['y_intercept']
