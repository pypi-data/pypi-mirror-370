# (C) Quantum Computing Inc., 2024.
"""
# Traveling Salesman Problem

## Class listing

`class TSPModel` - a base class
`class MTZTSPModel` - a concrete class for the MTZ formulation of a TSP

MTZ has been chosen for a demonstration of the integer capability of the
Dirac devices. A feasible solution will produce the valid sequence of 
visits by simply ordering the nodes by the $s_i$ variables. In the literature,
the ordering variables are named with $u$, but this is avoided because the
graph notation with $u$ being a tail node and $v$ being a head node is used
here. In conjunction with this notation, the variables $x_{ij}$ reference the
node index where the index of node $u$ is $i$ and the index of node $v$ is
$j$.

"""

from typing import (Dict, Tuple)
import numpy as np
from eqc_models.base import ConstrainedPolynomialModel, InequalitiesMixin
from eqc_models.base.operators import Polynomial

class TSPModel(ConstrainedPolynomialModel):
    """ 
    The TSPModel class implements the basics for building different formualtions of 
    TSP models.

    """

    def __init__(self, D : Dict[Tuple[int, int], float]):
        self.D = D
        self.nodes = nodes = set()
        self.edges = edges = set()
        for (u, v) in D.keys():
            nodes.add(u)
            nodes.add(v)
            assert (u, v) not in edges, "Only a single edge from tail to head is allowed"
            edges.add((u, v))
        # set N to the number of nodes
        self.N = len(nodes)
        self.variables = None

    def distance(self, i : int, j : int) -> float:
        """
        Parameters
        ----------
        i: int 
            index of first node
        Returns 
        -------

        float

        Retrieves the distance between nodes at indexes i and j. Supports asymmetric 
        (D[i, j] <> D[j, i]) distances.


        """

        return self.D[i, j]
    
    def cost(self, solution : np.ndarray) -> float:
        """ 
        Solution cost is the sum of all D values where (i,j) is chosen 

        Parameters:
            :solution: np.ndarray - An array of of 0,1 values which describe a route
                       depending on the formulation chosen.
        Returns: float

        """
        raise NotImplementedError("Subclass must implement cost method")
    
class MTZTSPModel(InequalitiesMixin, TSPModel):
    """
    Using the Miller Tucker Zemlin (1960) formulation of TSP, create a model
    instance that contains variables for node order (to eliminate subtours)
    and edge choices.

    >>> D = {(1, 2): 1, (2, 1): 1, (1, 3): 2, (3, 1): 2, (2, 3): 3, (3, 2): 3}
    >>> model = MTZTSPModel(D)
    >>> model.penalty_multiplier = 10
    >>> model.distance(1, 2)
    1
    >>> model.distance(3, 2)
    3
    >>> solution = np.array([1, 0, 0, 1, 1, 0, 1, 2, 3, 2, 2, 2, 5])
    >>> model.cost(solution)
    6
    >>> lhs, rhs = model.constraints
    >>> lhs.shape
    (10, 13)
    >>> model.senses
    ['EQ', 'EQ', 'EQ', 'EQ', 'EQ', 'EQ', 'LE', 'LE', 'LE', 'LE']
    >>> rhs.shape
    (10,)
    >>> (lhs@solution - rhs == 0).all()
    True
    >>> model.upper_bound
    array([1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3])
    >>> poly = model.polynomial
    >>> poly.evaluate(solution) + model.penalty_multiplier * model.offset
    6.0
    >>> infeasible = np.array([0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 4, 2, 5])
    >>> Pl, Pq = -2 * rhs.T@lhs, lhs.T@lhs
    >>> Pl.T@solution + solution.T@Pq@solution + model.offset
    0.0
    >>> Pl.T@infeasible + infeasible.T@Pq@infeasible + model.offset > 0
    True
    >>> poly.evaluate(infeasible) + model.penalty_multiplier * model.offset > 0
    True
    >>> infeasible = np.array([1, 1, 0, 1, 0, 0, 0, 1, 2, 2, 2, 0, 3])
    >>> poly.evaluate(infeasible) + model.penalty_multiplier * model.offset > 6
    True
    >>> val1 = poly.evaluate(infeasible) + model.penalty_multiplier * model.offset
    >>> model.penalty_multiplier *= 2
    >>> poly2 = model.polynomial
    >>> val2 = poly2.evaluate(infeasible) + model.penalty_multiplier * model.offset
    >>> val1 < val2
    True

    """

    def __init__(self, D : Dict[Tuple[int, int], float]) -> None:
        super(MTZTSPModel, self).__init__(D)
        self.variables = variables = []
        coefficients = []
        indices = []
        # choose a depot node
        self.depot = depot = list(self.nodes)[0]
        self.var_ub = var_ub = []
        for (u, v) in D.keys():
            varname = f"x_{u}_{v}"
            varidx = len(variables)
            variables.append(varname)
            var_ub.append(1)
            indices.append((0, varidx+1))
            coefficients.append(D[(u, v)])
        for u in self.nodes:
            variables.append(f"s_{u}")
            var_ub.append(self.N - 1)
        self.coefficients = coefficients
        self.indices = indices
        self.max_order = 2
        # Build the constraints: Two constraints for every node, one for the
        # edge chosen to enter and another for the edge chosen to leave.
        # One constraint for every edge not leading to the depot.

        depot_in = [uv for uv in self.edges if uv[-1] == depot]
        m = 2*self.N+len(self.edges) - len(depot_in)
        n = len(self.variables)
        lhs = np.zeros((m, n), dtype=np.int64)
        rhs = np.zeros((m,), dtype=np.int64)
        senses = ["EQ" for i in range(m)]
        N = self.N
        M = int(np.sqrt(N)) #  N // 2
        # scaling these coefficients
        for idx, node in enumerate(self.nodes):
            rhs[idx] = M
            rhs[self.N + idx] = M
            for (u, v) in self.edges:
                if v == node:
                    varname = f"x_{u}_{v}"
                    varidx = self.variables.index(varname)
                    lhs[idx, varidx] = M
                elif u == node:
                    varname = f"x_{u}_{v}"
                    varidx = self.variables.index(varname)
                    lhs[self.N+idx, varidx] = M
        # build these subtour elimination constraints
        # s_i - s_j + N x_{ij} <= N - 1
        idx = 0
        for (u, v) in self.edges:
            if v != depot:
                varname = f"x_{u}_{v}"
                varidx = self.variables.index(varname)
                senses[2*self.N + idx] = "LE"
                lhs[2*self.N + idx, varidx] = self.N - 1
                vidx = self.variables.index(f"s_{v}")
                lhs[2*self.N + idx, vidx] = -1
                uidx = self.variables.index(f"s_{u}")
                lhs[2*self.N + idx, uidx] = 1
                rhs[2*self.N + idx] = self.N
                idx += 1
        # update the constraint senses
        self.senses = senses
        self.lhs = lhs
        self.rhs = rhs

    def cost(self, solution : np.ndarray) -> float:
        """ 
        Solution cost is the sum of all D values where (i,j) is chosen 

        Parameters:
            :solution: np.ndarray - An array of of 0,1 values which describe a route
                       by setting variables representing active edges to 1.
        Returns: float

        """

        # get the route selection variables
        cost_val = 0
        for (u, v) in self.edges:
            varname = f"x_{u}_{v}"
            varidx = self.variables.index(varname)
            cost_val += solution[varidx] * self.D[(u, v)]
        return cost_val

    @property
    def upper_bound(self) -> np.ndarray:
        """ 
        For all route variables, the domain is {0, 1}. The sequence variables
        can take on values in [0, 1, 2, ..., N-1]. 
        
        """
        slacks = len([sense for sense in self.senses if sense != "EQ"])
        return np.array(self.var_ub + [self.N for i in range(slacks)])

