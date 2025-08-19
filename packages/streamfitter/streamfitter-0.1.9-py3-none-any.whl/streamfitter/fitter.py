import logging

import multiprocessing
import time
from dataclasses import dataclass
from datetime import timedelta
from enum import IntEnum
from itertools import combinations
from typing import Dict

from numpy.random import normal

from jax.numpy import array
from numpy import random as numpy_random

from lmfit import Minimizer, Parameters
from lmfit import __version__ as lmfit_version
from jax import __version__ as jax_version
from numpy import __version__ as numpy_version

from streamfitter import __version__ as streamfitter_version

import math

from .ExponentialDecay2Parameter import ExponentialDecay2ParameterFitter
from .mean import Mean
from .SymmetricExponentialPair import SymmetricExponentialPairFitter
from nef_pipelines.lib.interface import FitType, NoiseInfoSource

STREAMFITTER_DEFAULT_SEED = 42


class StreamFitterException(Exception):
    ...


class WrongNumberOfParamsException(StreamFitterException):
    ...


class NoReplicatesException(StreamFitterException):
    ...


class UnevenMatchedXYException(StreamFitterException):
    ...


class NoNEFPipeslinesException(StreamFitterException):
    def __init__(self):
        super().__init__('nef_pipelines was not imported, stream fitter depends on NEF-Pipelines, did you install it?')


class NoSuchFitterException(StreamFitterException):
    ...


@dataclass
class PointAndValue:
    point: float
    value: float
    spectrum_name: str


class LoggingLevels(IntEnum):
    WARNING = 0
    INFO = 1
    DEBUG = 2
    ALL = 3


class RunningStats(object):
    # after http://www.johndcook.com/blog/standard_deviation/ and B. P. Welford
    def __init__(self):
        self.m_n = 0
        self.m_oldM = 0.0
        self.m_newM = 0.0
        self.m_oldS = 0.0
        self.m_newS = 0.0

    def add(self, x):
        self.m_n += 1

        # See Knuth TAOCP vol 2, 3rd edition, page 232
        if self.m_n == 1:
            self.m_oldM = x
            self.m_newM = x
            self.m_oldS = 0.0
        else:
            self.m_newM = self.m_oldM + (x - self.m_oldM) / self.m_n
            self.m_newS = self.m_oldS + (x - self.m_oldM) * (x - self.m_newM)

        # set up for next iteration
        self.m_oldM = self.m_newM
        self.m_oldS = self.m_newS

    def num_values(self):
        return self.m_n

    def mean(self):
        if self.m_n > 0:
            result = self.m_newM
        else:
            result = 0.0

        return result

    def variance(self):
        if self.m_n > 1:
            result = self.m_newS / (self.m_n - 1)
        else:
            result = 0.0
        return result

    def stddev(self):
        return math.sqrt(self.variance())

    def stderr_variance(self):
        """this is  the error in the measured variance as described in
        https://stats.stackexchange.com/questions/156518/what-is-the-standard-error-of-the-sample-standard-deviation
        """

        if self.m_n != 0:
            result = math.sqrt((2.0 * self.stddev() ** 4) / (self.m_n - 1))
        else:
            result = 0.0

        return result

    def stderr_stddev(self):
        """this is  the error in the measured sigma as described in
        https://stats.stackexchange.com/questions/156518/what-is-the-standard-error-of-the-sample-standard-deviation
        and Harding et al Tutorials in Quantitative Methods for Psychology 10(2):107-123 DOI:10.20982/tqmp.10.2.p107
        """
        if self.m_n != 0:
            # result = self.stderr_variance() / self.stdev()*2 same as
            result = self.stddev() / math.sqrt(2.0 * (self.m_n - 1))
        else:
            result = 0.0
        return result


def _calculate_monte_carlo_error(fitter, id_xy_data, fits, noise_level, num_cycles, validate_mc=False):
    if validate_mc:
        replicate_averages = RunningStats()

    mc_fitted_params = {}
    mc_value_stats = {}
    mc_fitted_param_values = {}
    for row_count, (id, fit) in enumerate(fits.items()):
        # jax objects are not hashable
        xs = id_xy_data[id][0]
        xs_as_floats = [float(elem) for elem in xs]
        value_stats = {(id, x): RunningStats() for x in xs_as_floats}

        mc_value_stats[id] = value_stats
        mc_fitted_param_list = []
        mc_fitted_param_values[id] = mc_fitted_param_list

        fitted_params = [value.value for value in fit.params.values()]

        back_calculated = fitter.function(*fitted_params, id_xy_data[id][0])

        mc_keys_and_values = {}

        if num_cycles is not None and num_cycles != 0:
            for i in range(num_cycles):
                fit_key = id, i
                normals = normal(0, noise_level, len(xs_as_floats))
                mc_data = back_calculated + normals
                if validate_mc:
                    print(f'round: {i+1}')
                    print(f'normals: {normals}')
                    print(f'ys: {mc_data}')

                if validate_mc:
                    replicate_values = {}
                    print(xs_as_floats, mc_data)
                    for point, data in zip(xs_as_floats, mc_data):
                        replicate_values.setdefault(point, []).append(float(data))
                    for replicate in replicate_values.values():
                        for combination in combinations(replicate, 2):
                            replicate_averages.add(combination[0] - combination[1])

                mc_keys_and_values[fit_key] = xs, mc_data

        fits, estimates = _fit_series(mc_keys_and_values, fitter)
        if validate_mc:
            for (data_id, round), fitted_values in fits.items():
                print(f'fits: id: {data_id}, round: {round+1} {fitted_values.params}')

        averagers = {name: RunningStats() for name in fitter.params()}
        mc_calculations = 0
        for fit_key, fit in fits.items():
            if fit.success:
                mc_calculations += 1

                mc_fitted_param_list.append(fit.params)

                for name, value in fit.params.items():
                    averagers[name].add(value.value)

                mc_fitted_params_for_backcalc = [value.value for value in fit.params.values()]
                mc_back_calculated = fitter.function(*mc_fitted_params_for_backcalc, xs)
                for back_calculated, averager in zip(mc_back_calculated, value_stats.values()):
                    averager.add(back_calculated)

        if num_cycles is not None and num_cycles != 0:
            errors = {f'{name}_mc_error': averager.stddev() for name, averager in averagers.items()}

            mc_fitted_params[id] = {
                **errors,
                '%mc_failures': (num_cycles - mc_calculations) / num_cycles * 100,
            }

    if validate_mc and num_cycles is not None and num_cycles != 0 and replicate_averages.num_values() > 0:
        print(
            f'replicates validation: mc mean: {replicate_averages.mean()} mc stdev: {replicate_averages.stddev()}  [from {replicate_averages.num_values()} values]'
        )

    return mc_fitted_params, mc_value_stats, mc_fitted_param_values


def td_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ('year', 60 * 60 * 24 * 365),
        ('month', 60 * 60 * 24 * 30),
        ('day', 60 * 60 * 24),
        ('hour', 60 * 60),
        ('minute', 60),
        ('second', 1),
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append('%s %s%s' % (period_value, period_name, has_s))

    return ', '.join(strings)


# this should be build at runtime
FUNCTION_EXPONENTIAL_DECAY_2_PAMETER = 'exponential_function_2_parameter'
FUNCTION_TWO_EXPONENTIAL_DECAYS_2_PAMETER_SHARED_RATE = 'exponential_function_2_parameter_shared_rate'
FUNCTION_MEAN = 'mean'

_FITTERS = {
    FUNCTION_EXPONENTIAL_DECAY_2_PAMETER: ExponentialDecay2ParameterFitter,
    FUNCTION_TWO_EXPONENTIAL_DECAYS_2_PAMETER_SHARED_RATE: SymmetricExponentialPairFitter,
    FUNCTION_MEAN: Mean,
}


def get_function_names():
    return set(_FITTERS.keys())


def get_function(name):
    function_names = get_function_names()
    if name not in function_names:
        fitter_names = [f'{i}. {fitter_name}' for i, fitter_name in enumerate(function_names)]
        fitter_names = '\n'.join(fitter_names)
        msg = f"""
            the fitter called {name} can't be found, ther available fitters are:

            {fitter_names}
        """

        raise NoSuchFitterException(msg)

    return _FITTERS[name]


def fit(
    fitter,
    id_xy_data,
    cycles: int,
    noise_info,
    seed: int = STREAMFITTER_DEFAULT_SEED,
    verbose=0,
) -> Dict:
    _set_verbosity_level(verbose)

    _import_nef_pipelines_or_raise()

    id_xy_data = {id: (array(xs), array(ys)) for id, (xs, ys) in id_xy_data.items()}

    # TODO: this could be a context manager
    start_time = time.time()
    fits, estimates = _fit_series(id_xy_data, fitter)

    monte_carlo_errors = {}
    monte_carlo_value_stats = {}
    monte_carlo_param_values = {}
    if fitter.type == FitType.NON_LINEAR and noise_info and noise_info.source != NoiseInfoSource.NONE:
        numpy_random.seed(seed)

        validate_mc = verbose > 1
        monte_carlo_errors, monte_carlo_value_stats, monte_carlo_param_values = _calculate_monte_carlo_error(
            fitter, id_xy_data, fits, noise_info.noise, cycles, validate_mc=validate_mc
        )

    end_time = time.time()

    time_delta = timedelta(seconds=end_time - start_time)

    versions_string = (
        f'stream_fitter [{streamfitter_version}], lmfit [{lmfit_version}], jax[{jax_version}], numpy[{numpy_version}]'
    )

    results = {
        'fit_type': fitter.type,
        'fits': fits,
        'estimates': estimates,
        'monte_carlo_errors': monte_carlo_errors,
        'monte_carlo_value_stats': monte_carlo_value_stats,
        'monte_carlo_param_values': monte_carlo_param_values,
        'versions': versions_string,
        'calculation_time': time_delta,
        'number of cpus': multiprocessing.cpu_count(),
        'random seed': seed,
        'noise_level': noise_info.noise if noise_info else None,
        'error in noise estimate': noise_info.noise if noise_info else None,
        'source of noise estimate': noise_info.source if noise_info else None,
        'number of replicates': noise_info.num_replicates if noise_info else None,
        'time_start': start_time,
        'time_end': end_time,
        'calculation time': time_delta,
    }

    return results


def _import_nef_pipelines_or_raise():
    try:
        import nef_pipelines  # noqa: F401
    except ImportError:
        raise NoNEFPipeslinesException()


def _get_series_variables_array(id_xy_data):
    return array([xy_data[0] for xy_data in id_xy_data.values()])


def _fit_series(ids_and_values, fitter, debug=False):
    fits = {}
    estimates = {}
    if fitter.type == FitType.NON_LINEAR:
        func = fitter.get_wrapped_function()
        jacobian = fitter.get_wrapped_jacobian()

        for data_id, (xs, ys) in ids_and_values.items():
            params = Parameters()
            estimated_parameters_dict = fitter.estimate(xs, ys)
            estimates[data_id] = estimated_parameters_dict
            for key, value in estimated_parameters_dict.items():
                params.add(key, value=value)

            minimizer = Minimizer(func, params, fcn_args=(xs,), fcn_kws={'data': ys})
            out = minimizer.leastsq(Dfun=jacobian, col_deriv=1)

            if debug:
                print(data_id, out.params)
            fits[data_id] = out
    elif fitter.type == FitType.LINEAR:
        for data_id, (xs, ys) in ids_and_values.items():
            out = fitter.fit(xs, ys)
            fits[data_id] = out
    else:
        all_fitters = ', '.join([fit_type.name for fit_type in FitType])
        raise StreamFitterException(f'fitter type {fitter.type} not recognised it should be one of {all_fitters}')

    return fits, estimates


def _set_verbosity_level(verbose):
    if verbose == LoggingLevels.WARNING:
        logging.getLogger('jax').setLevel(logging.WARNING)
    elif verbose == LoggingLevels.INFO:
        logging.getLogger('jax').setLevel(logging.INFO)
    elif verbose == LoggingLevels.DEBUG:
        logging.getLogger('jax').setLevel(logging.DEBUG)
    else:
        logging.getLogger('jax').setLevel(logging.NOSET)
