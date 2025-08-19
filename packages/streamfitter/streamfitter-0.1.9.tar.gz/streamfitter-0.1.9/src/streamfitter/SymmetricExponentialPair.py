from jax.numpy import hstack, hsplit, array, mean, abs
from lmfit import Parameters

from streamfitter.ExponentialDecay3Parameter import ExponentialDecay3ParameterFitter
from streamfitter.fitter_protocol import FitterProtocol


class SymmetricExponentialPairFitter(FitterProtocol):
    def __init__(self):
        self._count = 2
        self._base_function = ExponentialDecay3ParameterFitter()

    def estimate(self, xs, ys):
        approximate_amplitudes = []
        approximate_time_constants = []
        approximate_offsets = []

        xs_list = hsplit(xs, self._count)
        ys_list = hsplit(ys, self._count)

        for xs, ys in zip(xs_list, ys_list):
            values = self._base_function.estimate(xs, ys)
            approximate_time_constants.append(values['time_constant'])
            approximate_amplitudes.append(values['amplitude'])
            approximate_offsets.append(values['offset'])

        return {
            'amplitude': mean(abs(array(approximate_amplitudes))),
            'time_constant': mean(array(approximate_time_constants)),
            'offset': mean(array(approximate_offsets)),
        }

    def function(self, amplitude, time_constant, offset, xs):
        xs_1, xs_2 = hsplit(xs, self._count)

        ys_1 = self._base_function.function(amplitude, time_constant, offset, xs_1)
        ys_2 = self._base_function.function(-amplitude, time_constant, offset, xs_2)

        return hstack((ys_1, ys_2))

    def get_wrapped_function(self):
        return SymmetricExponentialMultiFunctionWrapper(self._base_function, 2)

    def get_wrapped_jacobian(self):
        return SymmetricExponentialMultiJacobianWrapper(self._base_function, 2)


class SymmetricExponentialMultiFunctionWrapper:
    def __init__(self, func, count):
        self._func = func
        self._count = count

    def __call__(self, pars, xs, data=None):
        pars = [pars[par] for par in pars]
        amplitude, time_constant, offset = pars

        parameters_1 = Parameters()
        parameters_1.add(amplitude.name, amplitude.value)
        parameters_1.add(time_constant.name, time_constant.value)
        parameters_1.add(offset.name, offset.value)

        parameters_2 = Parameters()
        parameters_2.add(amplitude.name, -amplitude.value)
        parameters_2.add(time_constant.name, time_constant.value)
        parameters_2.add(offset.name, offset.value)

        split_pars = parameters_1, parameters_2
        split_xs = hsplit(xs, self._count)
        split_data = hsplit(data, self._count) if data is not None else [None] * self._count

        values = []
        function_wrapper = self._func.get_wrapped_function()
        for one_pars, one_xs, one_data in zip(split_pars, split_xs, split_data):
            values.append(function_wrapper(one_pars, one_xs, one_data))

        return hstack(values)


class SymmetricExponentialMultiJacobianWrapper:
    def __init__(self, func, count):
        self._func = func
        self._count = count

    def __call__(self, pars, xs, data=None):
        pars = [pars[par] for par in pars]
        amplitude, time_constant, offset = pars

        parameters_1 = Parameters()
        parameters_1.add(amplitude.name, amplitude.value)
        parameters_1.add(time_constant.name, time_constant.value)
        parameters_1.add(offset.name, offset.value)

        parameters_2 = Parameters()
        parameters_2.add(amplitude.name, -amplitude.value)
        parameters_2.add(time_constant.name, time_constant.value)
        parameters_2.add(offset.name, offset.value)

        split_pars = parameters_1, parameters_2
        split_xs = hsplit(xs, self._count)
        split_data = hsplit(data, self._count) if data is not None else [None] * self._count

        jacs = []
        function_wrapper = self._func.get_wrapped_jacobian()
        for one_pars, one_xs, one_data in zip(split_pars, split_xs, split_data):
            jacs.append(function_wrapper(one_pars, one_xs, one_data))

        result = array(
            [hstack([jacs[0][0], -jacs[1][0]]), hstack([jacs[0][1], jacs[1][1]]), hstack([jacs[0][2], jacs[1][2]])]
        )

        return result
