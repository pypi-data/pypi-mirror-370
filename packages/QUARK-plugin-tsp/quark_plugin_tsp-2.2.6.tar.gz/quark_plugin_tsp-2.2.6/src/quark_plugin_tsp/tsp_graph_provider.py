import logging
import math
from dataclasses import dataclass
from typing import override

import networkx as nx
from quark.core import Core, Data, Result
from quark.interface_types import Graph, InterfaceType, Other


@dataclass
class TspGraphProvider(Core):
    """A module for creating random weighted complete graphs for the TSP problem.

    :param nodes: The number of nodes in the graph
    :param seed: The seed for the random number generator
    """

    nodes: int = 10
    seed: int = 42

    @override
    def preprocess(self, data: InterfaceType) -> Result:
        # Create a random graph without edges
        g = nx.random_geometric_graph(self.nodes, radius=0.0, seed=self.seed)
        pos = nx.get_node_attributes(g, "pos")

        # Add edges with weights equal to the Euclidean distance between the nodes
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dist = math.hypot(pos[i][0] - pos[j][0], pos[i][1] - pos[j][1])
                g.add_edge(i, j, weight=dist)

        self._graph = g
        return Data(Graph.from_nx_graph(self._graph))

    @override
    def postprocess(self, data: Other[list]) -> Result:
        l = data.data
        if any(node not in l for node in self._graph.nodes()):
            logging.warn("Invalid route: Not all nodes were visited")
            return Data(None)
        logging.info(f"All {len(self._graph.nodes())} nodes were visited")

        if len(l) != len(self._graph.nodes()):
            logging.warn(
                "Invalid route: Some nodes were visited more than once",
            )
            return Data(None)
        logging.info("All nodes were visited exactly once")

        distance = 0
        node_id = l[0]
        for next_node_id in l[1:]:
            try:
                edge = self._graph[node_id][next_node_id]
            except KeyError:
                logging.warn(f"Invalid route: Edge {node_id} -> {next_node_id} does not exist")
                return Data(None)

            distance += edge["weight"]
            node_id = next_node_id

        logging.info("Route found!")
        logging.info(f"distance: {distance}")

        return Data(Other(distance))
