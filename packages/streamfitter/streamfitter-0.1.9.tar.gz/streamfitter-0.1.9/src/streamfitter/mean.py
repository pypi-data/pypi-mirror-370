from dataclasses import dataclass, field
from typing import Dict

from numpy import mean, std
from streamfitter.fitter_protocol import FitterProtocol
from nef_pipelines.lib.interface import FitType


@dataclass
class Fit:
    params: Dict = field(default_factory=Dict)


@dataclass
class FitParams:
    value: float


class Mean(FitterProtocol):
    @property
    def type(self):
        return FitType.LINEAR

    def fit(self, xs, ys):
        mean_value = mean(ys)
        std_value = std(ys)

        result = Fit({'mean': FitParams(float(mean_value)), 'stddev': FitParams(float(std_value))})

        return result
