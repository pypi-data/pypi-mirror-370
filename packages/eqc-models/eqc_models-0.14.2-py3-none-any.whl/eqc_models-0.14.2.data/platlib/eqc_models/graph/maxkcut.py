# (C) Quantum Computing Inc., 2024.
from typing import Tuple
import numpy as np
import networkx as nx
from .base import NodeModel
from eqc_models.base.quadratic import ConstrainedQuadraticModel

class MaxKCutModel(ConstrainedQuadraticModel):
    _objective = None

    def __init__(self, G : nx.Graph, k : int):
        self.G = G
        self.k = k
        A, b = self._build_constraints()
        c, J = self.costFunction()
        ConstrainedQuadraticModel.__init__(self, c, J, A, b)
        if k < 3:
            raise ValueError("k must be greater than 2")
        n = len(G.nodes) * k
        self.upper_bound = np.ones((n,))
        
    def decode(self, solution: np.ndarray) -> np.ndarray:
        """ Override the default decoding to use a the max cut metric to determine a solution """

        # only one partition per node can be selected
        # rather than the same cutoff per node, use the max value per partition
        decoded_solution = np.zeros_like(solution, dtype=np.int32)
        k = self.k
        G = self.G
        for i, u in enumerate(G.nodes):
            idx = slice(k*i, k*(i+1))
            spins = solution[idx]
            mx = np.max(spins)
            for j in range(k):
                if spins[j] == mx:
                    decoded_solution[k*i+j] = 1
                    break
        return decoded_solution
    
    def partition(self, solution):
        """ Return a dictionary with the partition number of each node """
        k = self.k
        G = self.G
        partition_num = {}
        for i, u in enumerate(G.nodes):
            for j in range(k):
                if solution[i*k+j] == 1:
                    partition_num[u] = j+1
        return partition_num
    
    def getCutSize(self, partition):
        cut_size = 0
        for u, v in self.G.edges:
            if partition[u]!=partition[v]:
                cut_size += 1
        return cut_size

    def costFunction(self) -> Tuple:
        
        G = self.G
        node_map = list(G.nodes)
        m = len(G.nodes)
        n = self.k * m
        # construct the quadratic portion of the objective
        # the linear portion is 0
        objective = np.zeros((n, n), dtype=np.float32)
        # increment the joint variable terms indicating the nodes are in different sets
        pairs = [(i, j) for i in range(self.k) for j in range(self.k) if i!=j]
        for u, v in G.edges:
            i = node_map.index(u)
            j = node_map.index(v)
            ibase = i * self.k
            jbase = j * self.k
            for incr1, incr2 in pairs:
                idx1 = ibase + incr1
                idx2 = jbase + incr2
                objective[idx1, idx2] += -1
        return (np.zeros((n, 1)), objective)

    def _build_constraints(self):

        G = self.G
        node_map = list(G.nodes)
        m = len(G.nodes)
        n = self.k * m

        # build the constraints
        A = np.zeros((m, n))
        b = np.ones((m,))
        for u in G.nodes:
            i = node_map.index(u)
            ibase = i * self.k
            A[i, ibase:ibase+self.k] = 1
        return A, b

    @property
    def constraints(self):
        """ Return LHS, RHS in numpy matrix format """

        return self.lhs, self.rhs

    @property
    def objective(self):
        """ Return the quadratic objective as NxN+1 matrix """

        return self._objective

class WeightedMaxKCutModel(MaxKCutModel):

    def __init__(self, G: nx.Graph, k: int, weight_label : str = "weight"):
        super(WeightedMaxCutModel).__init__(G, k)

        self.weight_label = weight_label
    
    def _build_objective(self):
        
        G = self.G
        node_map = list(G.nodes)
        m = len(G.nodes)
        n = self.k * m
        # construct the quadratic portion of the objective
        # the linear portion is 0
        objective = np.zeros((n, n), dtype=np.float32)
        # increment the joint variable terms indicating the nodes are in different sets
        pairs = [(i, j) for i in range(self.k) for j in range(self.k) if i!=j]
        for u, v in G.edges:
            i = node_map.index(u)
            j = node_map.index(v)
            ibase = i * self.k
            jbase = j * self.k
            for incr1, incr2 in pairs:
                idx1 = ibase + incr1
                idx2 = jbase + incr2
                objective[idx1, idx2] += G[u][v][self.weight_label]
        return (np.zeros((n, 1)), objective)

    def getCutSize(self, partition):
        cut_size = 0
        for u, v in self.G.edges:
            if partition[u]!=partition[v]:
                cut_size += self.G[u][v][self.weight_label]
        return cut_size
