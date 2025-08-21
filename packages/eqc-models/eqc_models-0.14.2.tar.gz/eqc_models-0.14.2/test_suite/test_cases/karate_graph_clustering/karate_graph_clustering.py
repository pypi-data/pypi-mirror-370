import sys
import networkx as nx
import pandas as pd

from test_utils import get_dirac3_energy, get_dirac3_runtime
from eqc_models.ml.clustering import GraphClustering


def run_problem(config_dict):
    hamiltonian_size = config_dict["hamiltonian_size"]
    num_samples = int(config_dict["num_samples"])
    solver_access = config_dict["solver_access"]
    ip_addr = config_dict["ip_addr"]
    port = config_dict["port"]    
    num_clusters = 4

    G = nx.karate_club_graph()

    try:
        assert G.number_of_nodes() * num_clusters == hamiltonian_size
    except AssertionError as exc:
        print(exc)
        sys.exit(1)

    model = GraphClustering(
        relaxation_schedule=1,
        num_samples=num_samples,
        solver_access=solver_access,
        ip_addr=ip_addr,
        port=port,                                
        graph=G,
        num_clusters=num_clusters,
        alpha=20.0,
        device="dirac-3",
    )
    response = model.fit()

    energy = get_dirac3_energy(response)        
    merit = model.get_modularity()
    runtime = get_dirac3_runtime(response)

    try:
        assert energy is not None, "The energy could not be computed!"
        assert merit is not None, "The merit could not be computed!"
        assert runtime is not None, "The runtime could not be computed!"        
    except AssertionError as exc:
        print(exc)
        sys.exit(1)

    return energy, merit, runtime
