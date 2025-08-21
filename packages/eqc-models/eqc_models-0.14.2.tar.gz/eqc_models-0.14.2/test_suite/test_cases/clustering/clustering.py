import os
import sys
import numpy as np
import pandas as pd

from test_utils import get_dirac3_energy, get_dirac3_runtime
from eqc_models.ml.clustering import Clustering


def run_problem(config_dict):
    data_dir = config_dict["data_dir"]
    hamiltonian_size = config_dict["hamiltonian_size"]
    num_samples = int(config_dict["num_samples"])
    solver_access = config_dict["solver_access"]
    ip_addr = config_dict["ip_addr"]
    port = config_dict["port"]
    
    X = np.load(os.path.join(data_dir, "X.npy"))

    num_clusters = 3
    try:
        assert (
            num_clusters * X.shape[0] == hamiltonian_size
        ), "Inconsistent size!"
    except AssertionError as exc:
        print(exc)
        sys.exit(1)

    obj = Clustering(
        num_clusters=3,
        relaxation_schedule=1,
        num_samples=num_samples,
        solver_access=solver_access,
        ip_addr=ip_addr,
        port=port,                                
        alpha=500.0,
        distance_func="squared_l2_norm",
        device="dirac-3",
    )

    response = obj.fit(X)

    energy = get_dirac3_energy(response)    
    merit = -energy
    runtime = get_dirac3_runtime(response)

    try:
        assert energy is not None, "The energy could not be computed!"
        assert merit is not None, "The merit could not be computed!"
        assert runtime is not None, "The runtime could not be computed!"        
    except AssertionError as exc:
        print(exc)
        sys.exit(1)

    return energy, merit, runtime
