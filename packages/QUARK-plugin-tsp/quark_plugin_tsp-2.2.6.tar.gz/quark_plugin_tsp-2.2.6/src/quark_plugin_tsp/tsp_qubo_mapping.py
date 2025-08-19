import logging
from dataclasses import dataclass
from typing import override

import numpy as np
from quark.core import Core, Data, Result
from quark.interface_types import Graph, Other, Qubo


@dataclass
class TspQuboMapping(Core):
    """A module for mapping a TSP graph to a QUBO problem."""

    lagrange_multiplier: float = 0.0

    @override
    def preprocess(self, data: Graph) -> Result:
        self.matrix = data.as_adjacency_matrix()
        n = len(self.matrix)
        q = np.zeros((n * n, n * n), dtype=float)
        if self.lagrange_multiplier == 0.0:
            # Set a default value for the lagrange multiplier if not set
            # This default value is chosen to be the average distance between nodes * number of nodes
            total = 0
            count = 0
            for i in range(n):
                for j in range(n):
                    if i > j:
                        total += self.matrix[i][j]
                        count += 1
            self.lagrange_multiplier = float(total * n / count)
        # Create the QUBO matrix
        # Note that the design of a QUBO matrix is delicate and depends on the specific problem.
        # This implementation is tailored for the TSP problem and inspired by the tsp qubo formulation used by D-Wave.
        # https://dnx.readthedocs.io/en/latest/_modules/dwave_networkx/algorithms/tsp.html#traveling_salesperson_qubo
        for i in range(n*n):
            for j in range(n*n):
                if i == j:
                    # Diagonal elements are set to
                    # - 2 * lagrange_multiplier + distance from this city to all other cities
                    q[i][j] = -2 * self.lagrange_multiplier  + np.sum(self.matrix, axis=0)[i // n]
                else:
                    # Off-diagonal elements represent different cases

                    # Blocks of n indices (0 to n-1, n to n+n-1, and so on) represent one city at n different time steps.

                    # Combinations of indices within one block cannot be part of a valid path
                    # (because it corresponds to not moving between two time steps).
                    # Such combinations are penalized by setting the corresponding QUBO matrix element
                    # to 2 * lagrange_multiplier.
                    if i // n == j // n:
                        # Same city, different time steps
                        q[i][j] += 2 * self.lagrange_multiplier

                    # Combinations of indices between different blocks represent moving from one city to another
                    # at a specific time step (depending on the relative positions in the two blocks).

                    # If the relative position of the indices in the two blocks is 0, the respective combination
                    # cannot be part of a valid path (because it means the move happens within zero time steps) and
                    # the corresponding QUBO matrix element is set to the lagrange_multiplier.
                    elif abs(i % n - j % n) == 0:
                        # Different cities, same time step
                        q[i][j] += self.lagrange_multiplier

                    # If the relative position of the indices in the two blocks is greater than 1,
                    # the respective combination cannot be part of a valid path (because it means the move happens
                    # between non-consecutive time steps) and the corresponding QUBO matrix element is set to 0.
                    elif abs(i % n - j % n) > 1:
                        # Different cities, non-consecutive time steps
                        q[i][j] += 0

                    # If the relative position of the indices in the two blocks is 1,
                    # the corresponding matrix element is set to the distance between the two cities.
                    elif abs(i % n - j % n) == 1:
                        # Different cities, consecutive time steps
                        q[i][j] = self.matrix[i // n][j // n]
                    else:
                        raise ValueError("Unexpected case in QUBO matrix construction.")
        return Data(Qubo.from_matrix(q))

    @override
    def postprocess(self, data: Other) -> Result:
        d = data.data
        # Only keep the tuples corresponding to |1> qubits
        tuples = (item[0] for item in d.items() if item[1])
        # Sort in order of time steps
        sorted_tuples = sorted(tuples, key=lambda x: x[1])

        path = [x[0] for x in sorted_tuples]
        time_steps = [x[1] for x in sorted_tuples]
        if time_steps != list(range(len(self.matrix))):
            logging.warn("Invalid route")
            return Data(None)
        return Data(Other(path))
