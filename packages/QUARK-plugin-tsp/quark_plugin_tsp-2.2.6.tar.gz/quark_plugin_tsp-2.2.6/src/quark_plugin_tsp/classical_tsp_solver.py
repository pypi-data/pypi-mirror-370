from dataclasses import dataclass
from typing import override

import networkx as nx
from quark.core import Core, Data, Result
from quark.interface_types import Graph, Other


@dataclass
class ClassicalTspSolver(Core):
    """Module for solving the TSP problem using a classical solver."""

    @override
    def preprocess(self, data: Graph) -> Result:
        self._solution = nx.approximation.traveling_salesman_problem(data.as_nx_graph(), cycle=False)
        return Data(None)

    @override
    def postprocess(self, data: None) -> Result:
        return Data(Other(self._solution))
