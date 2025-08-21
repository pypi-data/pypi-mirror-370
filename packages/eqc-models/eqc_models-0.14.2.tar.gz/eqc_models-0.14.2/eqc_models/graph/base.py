# (C) Quantum Computing Inc., 2024.
from typing import List, Set
import networkx as nx
from ..base import QuadraticModel

class GraphModel(QuadraticModel):
    """ """
    def __init__(self, G : nx.Graph):
        self.G = G
        super(GraphModel, self).__init__(*self.costFunction())

    @property
    def linear_objective(self):
        """Return linear terms as a vector."""
        return self._H[0]

    @property
    def quad_objective(self):
        """Return quadratic terms as a matrix."""
        return self._H[1]

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
        raise NotImplementedError("GraphModel does not implement costFunction")


class NodeModel(GraphModel):
    """ 
    Base class for a model where the decision variables correspond to
    the graph nodes. 
    
    """

    @property
    def variables(self) -> List[str]:
        """ Provide a variable name to index lookup; order enforced by sorting the list before returning """
        names = [node for node in self.G.nodes]
        names.sort()
        return names
    
    def modularity(self, partition : Set[Set]) -> float:
        """ Calculate modularity from a partition (set of communities) """
        
        return nx.community.modularity(self.G, partition)

class TwoPartitionModel(NodeModel):
    """ 
    Base class for a generic graph paritioning model. Override the
    cost function and evaluation methods to implement a two-partition
    algorithm.
    
    """

class EdgeMixin:

    @property
    def variables(self) -> List[str]:
        """ Provide a variable name to index lookup; order enforced by sorting the list before returning """
        names = [(u, v) for u, v in self.G.edges]
        names.sort()
        return names

class EdgeModel(EdgeMixin, GraphModel):
    """ Create a model where the variables are edge-based """

    
