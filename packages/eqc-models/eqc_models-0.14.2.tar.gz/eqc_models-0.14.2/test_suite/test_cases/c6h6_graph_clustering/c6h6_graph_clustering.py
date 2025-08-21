import sys
import numpy as np
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
    num_clusters = 3
    
    G = nx.Graph()

    carbon_carbon_edges = [
        (0, 1, 1),
        (1, 2, 2),
        (2, 3, 1),
        (3, 4, 2),
        (4, 5, 1),
        (5, 0, 2),
    ]
    carbon_hydrogen_edges = [
        (0, 6, 1),
        (1, 7, 1),
        (2, 8, 1),
        (3, 9, 1),
        (4, 10, 1),
        (5, 11, 1),
    ]
    
    edges = carbon_carbon_edges + carbon_hydrogen_edges

    G.add_weighted_edges_from(edges)

    obj = GraphClustering(
        relaxation_schedule=1,
        num_samples=num_samples,
        solver_access=solver_access,
        ip_addr=ip_addr,
        port=port,                                
        graph=G,
        num_clusters=num_clusters,
        alpha=10.0,
    )

    response = obj.fit()

    energy = get_dirac3_energy(response)        
    merit = obj.get_modularity()
    runtime = get_dirac3_runtime(response)

    try:
        assert energy is not None, "The energy could not be computed!"
        assert merit is not None, "The merit could not be computed!"
        assert runtime is not None, "The runtime could not be computed!"        
    except AssertionError as exc:
        print(exc)
        sys.exit(1)

    return energy, merit, runtime
