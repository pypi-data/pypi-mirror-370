import sys
import numpy as np
import networkx as nx

from eqc_models.ml.clusteringbase import ClusteringBase


class GraphClustering(ClusteringBase):
    """
    A clustering approach on a graph based on maximizing modularity.

    Parameters
    ----------
    
    graph: A NetwrokX graph object representing the data.
    num_clusters: Number of clusters.
    
    alpha: A penalty term multilplier; default: 1.0.
    
    relaxation_schedule: Relaxation schedule used by Dirac-3; default:
    2.
    
    num_samples: Number of samples used by Dirac-3; default: 1.
    
    device: The device used, dirac-1 or dirac-3; default: dirac-3.

    solver_access: Solver access type: cloud or direct; default: cloud.

    ip_addr: IP address of the device when direct access is used; default: None.

    port: Port number of the device when direct access is used; default: None.
    
    Examples
    ---------

    >>> import networkx as nx
    >>> G = nx.Graph()
    >>> G.add_edge(1, 2, weight=5)
    >>> G.add_edge(2, 3, weight=3)
    >>> G.add_edge(1, 3, weight=4)
    >>> G.add_edge(4, 5, weight=6)
    >>> G.add_edge(5, 6, weight=2)
    >>> G.add_edge(4, 6, weight=7)
    >>> G.add_edge(7, 8, weight=8)
    >>> G.add_edge(8, 9, weight=1)
    >>> G.add_edge(7, 9, weight=5)
    >>> G.add_edge(3, 4, weight=0.5)
    >>> G.add_edge(6, 7, weight=0.5)
    >>> from eqc_models.ml.clustering import GraphClustering    
    >>> from contextlib import redirect_stdout
    >>> import io
    >>> f = io.StringIO()
    >>> with redirect_stdout(f):
    ...     obj = GraphClustering(
    ...         relaxation_schedule=2,
    ...         num_samples=1,
    ...         graph=G,
    ...         num_clusters=3,
    ...         alpha=10.0,
    ...         device="dirac-3",    
    ...     )
    ...     labels = obj.fit_predict()
    """

    def __init__(
        self,
        graph: nx.Graph,
        num_clusters: int,
        alpha: float = 1.0,
        relaxation_schedule=2,
        num_samples=1,
        device="dirac-3",
        solver_access="cloud",
        ip_addr=None,
        port=None,            
    ):
        super(GraphClustering).__init__()

        assert device in ["dirac-1", "dirac-3"]

        assert solver_access in ["cloud", "direct"]
        
        self.graph = graph
        self.num_nodes = graph.number_of_nodes()
        self.num_edges = graph.number_of_edges()
        self.num_clusters = num_clusters
        self.alpha = alpha
        self.relaxation_schedule = relaxation_schedule
        self.num_samples = num_samples
        self.device = device
        self.solver_access = solver_access
        self.ip_addr = ip_addr
        self.port = port        
        self.labels = None

    def get_hamiltonian(self):
        adj_mat_sparse = nx.adjacency_matrix(self.graph)
        A = adj_mat_sparse.toarray()

        assert A.shape[0] == A.shape[1], "Inconsistent size!"
        assert A.shape[0] == self.num_nodes, "Inconsistent size!"

        num_clusters = self.num_clusters
        num_nodes = self.num_nodes

        J = np.zeros(
            shape=(num_nodes * num_clusters, num_nodes * num_clusters),
            dtype=np.float64,
        )
        C = np.zeros(
            shape=(num_nodes * num_clusters),
            dtype=np.float64,
        )

        for i in range(num_nodes):
            for j in range(num_nodes):
                for c in range(num_clusters):
                    for d in range(num_clusters):
                        if c == d:
                            J[i * num_clusters + c][
                                j * num_clusters + d
                            ] += -(
                                A[i][j]
                                - np.sum(A[i]) * np.sum(A[j]) / np.sum(A)
                            )
                        if i == j:
                            J[i * num_clusters + c][
                                j * num_clusters + d
                            ] += self.alpha

        for i in range(num_nodes):
            for c in range(num_clusters):
                C[i * num_clusters + c] += -2.0 * self.alpha

        return J, C, num_nodes

    def get_labels(self, sol: np.array):
        labels = np.empty(shape=(self.num_nodes), dtype=np.int32)

        for i in range(self.num_nodes):
            vec = sol[i * self.num_clusters : (i + 1) * self.num_clusters]
            labels[i] = np.argmax(vec) + 1

        return labels

    def fit(self):
        """
        Fit clustering.
        """
        J, C, sum_constraint = self.get_hamiltonian()

        assert J.shape[0] == J.shape[1], "Inconsistent hamiltonian size!"
        assert J.shape[0] == C.shape[0], "Inconsistent hamiltonian size!"

        self.set_model(J, C, sum_constraint)

        sol, response = self.solve()
        
        assert len(sol) == C.shape[0], "Inconsistent solution size!"
        assert len(sol) == self.num_clusters * self.num_nodes

        self.labels = self.get_labels(sol)

        return response

    def fit_predict(self):
        """
        Fit clustering and return cluster labels for all nodes.
        """

        self.fit()

        return self.labels

    def get_modularity(self):
        if self.labels is None:
            return

        clusters = [set() for i in range(self.num_clusters)]
        nodes = list(self.graph.nodes())
        for i in range(self.num_nodes):
            clusters[self.labels[i] - 1].add(nodes[i])

        return nx.community.modularity(self.graph, clusters)


class Clustering(ClusteringBase):
    """A clustering approach based on QCi's Dirac machines.

    Parameters
    ----------
    
    num_clusters: Number of clusters.
    
    alpha: A penalty term multilplier; default: 1.0.
    
    relaxation_schedule: Relaxation schedule used by Dirac-3; default:
    2.
    
    num_samples: Number of samples used by Dirac-3; default: 1.
    
    distance_func: Distance function used; default: squared_l2_norm.
    
    device: The device used, dirac-1 or dirac-3; default: dirac-3.

    solver_access: Solver access type: cloud or direct; default: cloud.

    ip_addr: IP address of the device when direct access is used; default: None.

    port: Port number of the device when direct access is used; default: None.
    
    Examples
    ---------

    >>> np.random.seed(42)
    >>> cluster1 = np.random.randn(15, 2) * 0.5 + np.array([2, 2])
    >>> cluster2 = np.random.randn(15, 2) * 0.5 + np.array([8, 3])
    >>> cluster3 = np.random.randn(15, 2) * 0.5 + np.array([5, 8])
    >>> X = np.vstack((cluster1, cluster2, cluster3))
    >>> from eqc_models.ml.clustering import Clustering    
    >>> from contextlib import redirect_stdout
    >>> import io
    >>> f = io.StringIO()
    >>> with redirect_stdout(f):
    ...    obj = Clustering(
    ...        num_clusters=3,
    ...        relaxation_schedule=1,
    ...        num_samples=1,
    ...        alpha=500.0,
    ...        distance_func="squared_l2_norm",
    ...        device="dirac-3",
    ...    )
    ...    labels = obj.fit_predict(X)

    """

    def __init__(
        self,
        num_clusters: int,
        alpha: float = 1.0,
        relaxation_schedule: int = 2,
        num_samples: int = 1,
        distance_func: str = "squared_l2_norm",
        device: str = "dirac-3",
        solver_access="cloud",
        ip_addr=None,
        port=None,            
    ):
        super(Clustering).__init__()

        assert device in ["dirac-1", "dirac-3"]

        assert solver_access in ["cloud", "direct"]
        
        self.num_clusters = num_clusters
        self.alpha = alpha
        self.relaxation_schedule = relaxation_schedule
        self.num_samples = num_samples
        self.distance_func = distance_func
        self.device = device
        self.solver_access = solver_access
        self.ip_addr = ip_addr
        self.port = port        
        self.labels = None

        assert distance_func in ["squared_l2_norm"], (
            "Unknown distance function <%s>!" % distance_func
        )

    def get_hamiltonian(self, X: np.array):
        num_items = X.shape[0]
        num_clusters = self.num_clusters

        if self.distance_func == "squared_l2_norm":
            dist = lambda u, v: np.linalg.norm(u - v) ** 2

        J = np.zeros(
            shape=(num_items * num_clusters, num_items * num_clusters),
            dtype=np.float64,
        )
        C = np.zeros(
            shape=(num_items * num_clusters),
            dtype=np.float64,
        )

        for i in range(num_items):
            for j in range(num_items):
                for c in range(num_clusters):
                    for d in range(num_clusters):
                        if c == d:
                            J[i * num_clusters + c][
                                j * num_clusters + d
                            ] += dist(X[i], X[j])

                        if i == j:
                            J[i * num_clusters + c][
                                j * num_clusters + d
                            ] += self.alpha

        for i in range(num_items):
            for c in range(num_clusters):
                C[i * num_clusters + c] += -2.0 * self.alpha

        return J, C, num_items

    def get_labels(self, sol: np.array, num_items: int):
        labels = np.empty(shape=(num_items), dtype=np.int32)

        for i in range(num_items):
            vec = sol[i * self.num_clusters : (i + 1) * self.num_clusters]
            labels[i] = np.argmax(vec) + 1

        return labels

    def fit(self, X: np.array):
        """
        Fit clustering.

        Parameters
        ----------
        X: Dataset; an array of shape (num_items, num_dims).
        """
        num_items = X.shape[0]
        J, C, sum_constraint = self.get_hamiltonian(X)

        assert J.shape[0] == J.shape[1], "Inconsistent hamiltonian size!"
        assert J.shape[0] == C.shape[0], "Inconsistent hamiltonian size!"

        self.set_model(J, C, sum_constraint)

        sol, response = self.solve()

        assert len(sol) == C.shape[0], "Inconsistent solution size!"
        assert len(sol) == self.num_clusters * num_items

        self.labels = self.get_labels(sol, num_items)

        return response

    def fit_predict(self, X: np.array):
        """
        Fit clustering and return cluster labels for all records.

        Parameters
        ----------
        X: Dataset; an array of shape (num_items, num_dims).
        """

        self.fit(X)

        return self.labels
