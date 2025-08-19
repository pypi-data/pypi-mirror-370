from jax.numpy import ones, vstack
from jax.numpy.linalg import lstsq
from streamfitter.fitter_protocol import FitterProtocol
from nef_pipelines.lib.interface import FitType


class LinearLeastSquares(FitterProtocol):
    @property
    def type(self):
        return FitType.LINEAR

    def function(self, slope, y_intercept, xs):
        return (xs * slope) + y_intercept

    def fit(self, xs, ys):
        A = vstack([xs, ones(len(xs))]).T

        slope, y_intercept = lstsq(A, ys)[0]

        result = {'slope': slope, 'y_intercept': y_intercept}

        return result
