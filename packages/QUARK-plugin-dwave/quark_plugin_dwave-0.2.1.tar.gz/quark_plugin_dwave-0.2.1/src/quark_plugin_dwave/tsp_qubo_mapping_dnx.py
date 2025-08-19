import logging
from dataclasses import dataclass
from typing import override

import dwave_networkx as dnx
import numpy as np
from quark.core import Core, Data, Result
from quark.interface_types import Graph, Other, Qubo


@dataclass
class TspQuboMappingDnx(Core):
    """A module for mapping a graph to a QUBO formalism for the TSP problem."""

    @override
    def preprocess(self, data: Graph) -> Result:
        self._graph = data.as_nx_graph()
        q = dnx.traveling_salesperson_qubo(self._graph)
        return Data(Qubo.from_dnx_qubo(q, len(data.as_adjacency_matrix())))

    @override
    def postprocess(self, data: Other) -> Result:
        d = data.data
        # Only keep the tuples corresponding to |1> qubits
        tuples = (item[0] for item in d.items() if item[1])
        # Sort in order of time steps
        sorted_tuples = sorted(tuples, key=lambda x: x[1])

        path = [x[0] for x in sorted_tuples]
        time_steps = [x[1] for x in sorted_tuples]

        if time_steps != list(range(self._graph.number_of_nodes())):
            logging.warn("Invalid route")
            return Data(None)
        return Data(Other(path))
