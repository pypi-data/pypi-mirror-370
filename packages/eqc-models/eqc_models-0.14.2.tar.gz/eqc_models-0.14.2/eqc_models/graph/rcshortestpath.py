import logging
from typing import (Any, Dict, Tuple, List)
import networkx as nx
import numpy as np
from eqc_models.graph.shortestpath import ShortestPathModel

log = logging.getLogger(name=__name__)

class RCShortestPathModel(ShortestPathModel):
    """ 
    Model for resource constrained shortest path problems.
    Use a shortest path base model to implement the routing 
    constraints and objective function. Add resource constraints.
    
    """

    def __init__(self, G : nx.DiGraph, s : Any, t : Any, T : int, resource_key : str="resource"):
        if T <= 0:
            raise ValueError("T must be positive")
        elif round(T, 0) != T:
            raise ValueError("T must be integer-valued")
        self.T = T
        self.resource_key = resource_key
        # determine shortest path by weight
        nx_path = nx.shortest_path(G, s, t)
        path_length = len(nx_path)
        self.resource_mult = resource_mult = 2 * path_length / self.T
        super(RCShortestPathModel, self).__init__(G, s, t)
        upper_bound = np.ones(len(self.variables))
        upper_bound[-1] = np.ceil(resource_mult * T)
        self.upper_bound = upper_bound
        is_discrete = [True for i in range(upper_bound.shape[0])]
        is_discrete[-1] = False
        self.is_discrete = is_discrete

    @property
    def variables(self):
        variables = super(RCShortestPathModel, self).variables
        return variables + ["resource_slack"]

    def buildConstraints(self) -> Tuple[np.ndarray,np.ndarray]:
        lhs, rhs = super(RCShortestPathModel, self).buildConstraints()
        # add a single constraint
        G = self.G
        n = len(self.variables)
        resource_lhs = np.zeros((1, n), dtype=np.float32)
        resource_mult = self.resource_mult
        log.debug("Resource multiplier %f", resource_mult)
        for i in range(len(G.edges)):
            (u, v) = self.variables[i]
            # find the time to traverse the arc
            resource_cost = G.edges[(u, v)][self.resource_key]
            resource_cost *= resource_mult
            log.debug(f"Adding resource %s for edge %s", resource_cost, (u, v))
            resource_lhs[0, i] = resource_cost
        resource_lhs[0, -1] = 1
        lhs = self._stackLHS(lhs, resource_lhs)
        rhs = np.hstack([rhs, [self.T*resource_mult]])
        log.debug("LHS shape %s RHS shape %s", lhs.shape, rhs.shape)
        return lhs, rhs

    def pathCost(self, path):
        """ sum the cost of all legs in the path """
        assert self.s in path
        G = self.G
        node = self.s
        max_len = len(self.G.nodes) - 1
        path_len = 0
        path_cost = 0
        path_resources = 0
        while node != t:
            edge = (node, path[node])
            if edge not in G.edges:
                raise ValueError(f"Edge {edge} not found")
            path_len += 1
            path_cost += G.edges[edge]["weight"]
            path_resources += G.edges[edge][self.resource_key]
            if path_len > max_len:
                raise ValueError("Invalid path. Describes a cycle.")
        return path_cost, path_resources

