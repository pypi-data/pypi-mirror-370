from typing import Tuple
import numpy as np
import scipy.sparse as sp
import networkx as nx
from math import modf
from eqc_models.graph.base import GraphModel


class GraphPartitionModel(GraphModel):
    """
    A model for graph partitioning into `k` parts with objective and constraints
    derived from the Laplacian matrix and additional penalties for balance and constraints.
    """

    def __init__(self, G: nx.Graph, k: int = 2, weight: str = "weight", alpha: float = 1.0, beta_obj: float = 1.0,
                 gamma: float = 1.0):
        """
        Parameters:
        -----------
        G : nx.Graph
            The graph to partition.
        k : int
            The number of partitions.
        weight : str
            The key for edge weights in the graph.
        alpha : float
            The penalty multiplier for balance constraints.
        beta_obj : float
            The penalty multiplier for minimizing edge cuts (Laplacian term).
        gamma : float
            The penalty multiplier for assignment constraints.
        """
        self._G = G
        self._k = k
        self._weight = weight
        self._alpha = alpha
        self._beta_obj = beta_obj
        self._gamma = gamma
        self._laplacian = nx.laplacian_matrix(G, weight=weight)
        self._num_nodes = G.number_of_nodes()
        self._sorted_nodes = sorted(G.nodes)
        self._constraints_offset = 0
        self._balanced_partition_offset = 0
        self.set_and_validate_k()
        self._objective_matrix = self.initialize_model()
        super().__init__(self._G)

    def set_and_validate_k(self):
        """
        Sets k and encoding length for a graph problem
        """
        # modf(x) = (fractional, integer) decomposition.
        # Make sure fractional portion is zero. Convert to int if so.
        assert modf(self._k)[0] == 0, "'k' must be an integer."

        # it's an int, so set self.k
        self._k = int(self._k)

        # Verify k >= 2
        assert self._k >= 2, f"ERROR, k={self._k}: k must be greater than or equal to 2."

        # Verify that k makes sense
        assert self._k <= self._num_nodes, (
            f"ERROR, k={self._k}: k must be less than number of nodes or variables. k = {self._k} and "
            f"number of nodes = {self._num_nodes}"
        )

    def initialize_model(self):
        """
        Build the objective matrix and constraints for the k-partition problem.
        """
        if self._k == 2:
            # For 2 partitions, construct a simpler QUBO from the Laplacian matrix
            return self.get_two_partition_qubo()
        else:
            # For k > 2, construct a block-diagonal Laplacian with balance and constraints
            laplacian_blocks = 0.5 * sp.block_diag([self._laplacian] * self._k, format="csr")
            balance_term = self.get_balanced_partition_term()
            constraints = self.get_constraints()
            return (
                self._alpha * balance_term
                + self._gamma * constraints
                + self._beta_obj * laplacian_blocks
            )

    def get_balanced_partition_term(self) -> sp.spmatrix:
        """
        Construct the quadratic penalty term for balanced partitions.
        """
        I_k = sp.identity(self._k)
        Ones_n = np.ones((self._num_nodes, self._num_nodes))
        balanced_partition_term = sp.kron(I_k, Ones_n, format="csr")
        balanced_partition_term -= (
            2 * self._num_nodes / self._k * sp.identity(balanced_partition_term.shape[0])
        )
        self._balanced_partition_offset = self._num_nodes**2 / self._k
        return balanced_partition_term

    def get_constraints(self) -> sp.spmatrix:
        """
        Construct the quadratic penalty term for assignment constraints.
        """
        I_n = sp.identity(self._num_nodes)
        Ones_k = np.ones((self._k, self._k))
        constraints = sp.kron(Ones_k, I_n, format="csr")
        constraints -= 2 * sp.identity(constraints.shape[0])
        self._constraints_offset = self._num_nodes
        return constraints

    def get_two_partition_qubo(self) -> sp.spmatrix:
        """
        Construct the QUBO matrix for two partitions using adjacency and penalties.
        """
        Garr = nx.to_scipy_sparse_matrix(self._G, weight=self._weight, nodelist=self._sorted_nodes)
        Q = (
            self._alpha * np.ones(Garr.shape, dtype=np.float32)
            - self._beta_obj * Garr
        )
        degrees = Garr.sum(axis=1).A1  # Convert sparse matrix to 1D array
        diag = self._beta_obj * degrees - self._alpha * (self._num_nodes - 1)
        np.fill_diagonal(Q, diag)
        return sp.csr_matrix(Q)

    def evaluate(self, solution: np.ndarray) -> float:
        """
        Evaluate the objective function for a given solution.
        """
        assert len(solution) == self._objective_matrix.shape[0], "Solution size mismatch."
        return float(solution.T @ self._objective_matrix @ solution)

    def decode(self, solution: np.ndarray) -> dict:
        """
        Decode the solution vector into a partition assignment.
        """
        if self._k == 2:
            return {node: int(solution[i]) for i, node in enumerate(self._sorted_nodes)}
        else:
            partitions, nodes = np.where(solution.reshape((self._k, self._num_nodes)) == 1)
            return {self._sorted_nodes[node]: int(partition) for partition, node in zip(partitions, nodes)}

    def costFunction(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Return the linear and quadratic components of the objective function.
        """
        Q = self._objective_matrix
        h = Q.diagonal()
        J = 2 * sp.triu(Q, k=1).tocsr() # Extract upper triangular part for quadratic terms
        return h, J
