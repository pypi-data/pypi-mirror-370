from dataclasses import dataclass
from typing import override

import dwave_networkx as dnx
from quark.core import Core, Data, Result
from quark.interface_types import Graph, Other, Qubo


@dataclass
class MisQuboMappingDnx(Core):
    """
    A module for mapping a graph to a QUBO formalism for the MIS problem
    """

    @override
    def preprocess(self, data: Graph) -> Result:
        self._graph = data.as_nx_graph()
        q = dnx.maximum_weighted_independent_set_qubo(self._graph)
        return Data(Qubo.from_dict(q))

    @override
    def postprocess(self, data: Other) -> Result:
        d: dict = data.data
        filtered_data = filter(lambda x: x[1] == 1, d.items())
        nodes = map(lambda x: x[0], filtered_data)
        return Data(Other(list(nodes)))
