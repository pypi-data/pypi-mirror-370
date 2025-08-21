# (C) Quantum Computing Inc., 2024.
import networkx as nx
import numpy as np
from .base import TwoPartitionModel


class MaxCutModel(TwoPartitionModel):

    def decode(self, solution: np.ndarray) -> np.ndarray:
        """ Override the default decoding to use a the max cut metric to determine a solution """

        Gprime, solution = determine_solution(self.G, solution)
        cut_size = len(self.G.edges) - len(Gprime.edges)
        return solution
    
    @property
    def J(self) -> np.ndarray:
        return self.quad_objective

    @property
    def C(self) -> np.ndarray:
        return self.linear_objective
    
    @property
    def H(self):
        return self.linear_objective, self.quad_objective
    
    def partition(self, solution):
        """ Return a dictionary with the partition number of each node """
        
        partition_num = {}
        for i, u in enumerate(self.node_map):
            if solution[i] == 0:
                partition_num[u] = 1
            else:
                partition_num[u] = 2
        return partition_num
    
    def getCutSize(self, partition):
        cut_size = 0
        for u, v in self.G.edges:
            if partition[u]!=partition[v]:
                cut_size += 1
        return cut_size

    def costFunction(self):
        """ 
        Parameters
        -------------
        
        None
        
        Returns
        --------------
        
        :C: linear operator (vector array of coefficients) for cost function
        :J: quadratic operator (N by N matrix array of coefficients ) for cost function
        
        """
        G = self.G
        self.node_map = list(G.nodes)
        variables = self.variables
        n = len(variables)
        self.upper_bound = np.ones((n,))
        
        J = np.zeros((n, n), dtype=np.float32)
        h = np.zeros((n, 1), dtype=np.float32)
        for u, v in G.edges:
            J[u, v] += 1
            J[v, u] += 1
            h[u, 0] -= 1
            h[v, 0] -= 1
        return h, J


def get_graph(n, d):
    """ Produce a repeatable graph with parameters n and d """

    seed = n * d
    return nx.random_graphs.random_regular_graph(d, n, seed)


def get_partition_graph(G, solution):
    """
    Build the partitioned graph, counting cut size 

    :parameters: G : nx.DiGraph, solution : np.ndarray
    :returns: nx.DiGraph, int
    
    """

    cut_size = 0
    Gprime = nx.DiGraph()
    Gprime.add_nodes_from(G.nodes)
    for i, j in G.edges:
        if solution[i] != solution[j]:
            cut_size += 1
        else:
            Gprime.add_edge(i, j)
    return Gprime, cut_size


def determine_solution(G, solution):
    """
    Use a simple bisection method to determine the binary solution. Uses
    the cut size as the metric.

    Returns the partitioned graph and solution.

    :parameters: G : nx.DiGraph, solution : np.ndarray
    :returns: nx.DiGraph, np.ndarray

    """
    solution = np.array(solution)
    test_vals = np.copy(solution)
    test_vals.sort()
    lower = 0
    upper = solution.shape[0] - 1
    best_cut_size = 0
    best_graph = G
    best_solution = None
    while upper > lower:
        middle = (upper + lower) // 2
        threshold = test_vals[middle]
        test_solution = (solution>=threshold).astype(np.int32)
        Gprime, cut_size = get_partition_graph(G, test_solution)
        if cut_size > best_cut_size:
            best_cut_size = cut_size
            lower = middle
            best_solution = test_solution
            best_graph = Gprime
        else:
            upper = middle
    return best_graph, best_solution

def get_maxcut_H(G, t):
    """ 
    Return a Hamiltonian representing the Maximum Cut Problem. Scale the problem using `t`.
    Automatically adds a slack qudit.
    
    """
    n = len(G.nodes)
    J = np.zeros(shape=(n+1, n+1), dtype=np.float32)
    h = np.zeros(shape=(n+1,1), dtype=np.float32)
    for u, v in G.edges:
        J[u, v] += 1
        J[v, u] += 1
        J[u, u] = 1
        J[v, v] = 1
        h[u] -= 1
        h[v] -= 1
    J *= 1/t**2
    h *= 1/t
    H = np.hstack([h, J])
    return H
