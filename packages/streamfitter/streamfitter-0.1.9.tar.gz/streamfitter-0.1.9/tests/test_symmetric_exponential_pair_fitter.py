import numpy as np
from jax.numpy import hstack, array
from pytest import approx

from streamfitter.SymmetricExponentialPair import SymmetricExponentialPairFitter
from streamfitter.fitter import fit

RATE_CONSTANT_1_3 = 1.3
AMPLITUDE_1_5 = 1.5
OFFSET = 1.0

# amplitude = 1.5 time_constant = 1.3 asymtote = 1.0
EXPONENTIAL_A_1_5_R_1_3_O_1 = array(
    [
        2.5,
        1.8417159529712340,
        1.47232383032418200,
        1.2650416686348950,
        1.14872653379473800,
        1.08345699741676420,
        1.046831390741846400,
        1.026279152458161000,
        1.014746387903064900,
        1.008274846631141157,
    ]
)

# symmetric partner of above
EXPONENTIAL_A_m1_5_R_1_3_A_1 = array([((y - OFFSET) * -1) + OFFSET for y in EXPONENTIAL_A_1_5_R_1_3_O_1])

SYMMETRIC_EXPONENTIAL = hstack((EXPONENTIAL_A_1_5_R_1_3_O_1, EXPONENTIAL_A_m1_5_R_1_3_A_1))

XS = np.linspace(0, 4, 10)


def test_shared_rate_exponential_estimator():
    xs = np.hstack([XS, XS])
    ys = SYMMETRIC_EXPONENTIAL

    function = SymmetricExponentialPairFitter()
    result = function.estimate(xs, ys)

    assert approx(AMPLITUDE_1_5, abs=0.1) == result['amplitude']
    assert approx(RATE_CONSTANT_1_3, abs=0.1) == result['time_constant']
    assert approx(OFFSET, abs=0.1) == result['offset']


def test_paired_exponential_function():
    xs_2 = hstack((XS, XS))

    function = SymmetricExponentialPairFitter()
    result = function.function(AMPLITUDE_1_5, RATE_CONSTANT_1_3, OFFSET, xs_2)

    assert approx(SYMMETRIC_EXPONENTIAL) == result


def test_fitter_with_paired_exponential():
    # this forces the fitter to do some work as the guess
    # of the initial amplitude will be off as it just uses the largest
    # values in the ys
    ys_1 = EXPONENTIAL_A_1_5_R_1_3_O_1[1:]
    ys_2 = EXPONENTIAL_A_m1_5_R_1_3_A_1[1:]
    xs_1_2 = XS[1:]

    xs = np.hstack([xs_1_2, xs_1_2])
    ys = np.hstack([ys_1, ys_2])

    key = 1

    id_xy_data = {key: [xs, ys]}

    fitter = SymmetricExponentialPairFitter()

    result = fit(fitter, id_xy_data, None, None, 42)

    estimates = result['estimates'][key]

    # this proves that the fitter is doing the work and not the estimator
    estimated_amplitude = estimates['amplitude']
    estimated_time_constant = estimates['time_constant']
    # estimated_offset = estimates['offset'] - not used see below

    assert approx(AMPLITUDE_1_5) != estimated_amplitude
    assert approx(RATE_CONSTANT_1_3) != estimated_time_constant
    # assert approx(OFFSET) != estimated_offset - this can't be tested because the errors in the estimate self cancel

    fits = result['fits'][key]
    amplitude = fits.params['amplitude']
    time_constant = fits.params['time_constant']
    offset = fits.params['offset']

    assert approx(AMPLITUDE_1_5) == amplitude
    assert approx(RATE_CONSTANT_1_3) == time_constant
    assert approx(OFFSET) == offset
