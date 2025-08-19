from jax.numpy import exp, where, log, asarray
from streamfitter.fitter_protocol import FitterProtocol


class ExponentialDecay3ParameterFitter(FitterProtocol):
    def estimate(self, xs, ys):
        x_ys = [(x, y) for x, y in zip(xs, ys)]

        x_ys.sort()

        xs = [x for x, _ in x_ys]
        ys = [y for _, y in x_ys]

        ys = asarray(ys)

        offset = ys[-1]

        ys -= offset

        if xs[0] == 0.0:
            amplitude = ys[0]
        else:
            dy = ys[1] - ys[0]
            dx = xs[1] - xs[0]

            dy_dx = dy / dx

            amplitude = ys[0] - (xs[0] * dy_dx)

        delta_amplitude = ys[0] - ys[-1]
        delta_amplitude_2 = delta_amplitude / 2

        closest = min(ys, key=lambda x: abs(x - delta_amplitude_2))

        index = where(ys == closest)[0][0]

        x = xs[index]
        y = ys[index]

        time_constant = -log((y) / (ys[0])) / x

        result = {'amplitude': amplitude, 'time_constant': time_constant.tolist(), 'offset': offset}

        return result

    def function(self, amplitude, time_constant, offset, xs):
        return offset + amplitude * exp(-time_constant * xs)
