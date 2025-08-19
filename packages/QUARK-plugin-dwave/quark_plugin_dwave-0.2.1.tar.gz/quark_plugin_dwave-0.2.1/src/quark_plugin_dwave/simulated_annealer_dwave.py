from dataclasses import dataclass
from typing import override

import dwave.samplers
import numpy as np

from quark.core import Core, Data, Result
from quark.interface_types import Other, Qubo


@dataclass
class SimulatedAnnealerDwave(Core):
    """
    A module for solving a qubo problem using simulated annealing

    :param num_reads: The number of reads to perform
    """

    num_reads: int = 100

    _first_run: bool = True

    @override
    def preprocess(self, data: Qubo) -> Result:
        # if self._first_run:
        #     self._first_run = False
        #     return Sleep(data)
        # else:
        #     device = dwave.samplers.SimulatedAnnealingSampler()
        #     self._result = device.sample_qubo(data.as_dict(), num_reads=self.num_reads)
        #     return Data(None)

        device = dwave.samplers.SimulatedAnnealingSampler()
        q = data.as_dnx_qubo()
        self._result = device.sample_qubo(q, num_reads=self.num_reads)
        return Data(None)

    @override
    def postprocess(self, data: Data) -> Result:
        return Data(Other(self._result.lowest().first.sample))  # type: ignore
