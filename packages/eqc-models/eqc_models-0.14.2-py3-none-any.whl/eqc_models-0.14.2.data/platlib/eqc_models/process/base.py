import networkx as nx
from eqc_models.base import ConstrainedPolynomialModel

class ProcessModel:
    """
    Given a directed graph $G$ that describes a process flow, optimize the 
    flow.

    """
    def __init__(self, G : nx.DiGraph):
        self.G = G

    @staticmethod
    def process_constraints(G : nx.DiGraph):
        """ Build process constraints from the graph """

    def constraints(self) -> Tuple[np.ndarray]:
        pass
