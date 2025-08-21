# (C) Quantum Computing Inc., 2024.
import sys
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.preprocessing import normalize
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA as PCA_cls

from test_utils import get_dirac3_energy, get_dirac3_runtime
from eqc_models.ml.decomposition import PCA


def run_problem(config_dict):
    data_dir = config_dict["data_dir"]
    hamiltonian_size = config_dict["hamiltonian_size"]
    num_samples = int(config_dict["num_samples"])
    solver_access = config_dict["solver_access"]
    ip_addr = config_dict["ip_addr"]
    port = config_dict["port"]
    
    iris = datasets.load_iris()
    X = iris.data

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    try:
        assert X.shape[1] == hamiltonian_size, "Inconsistent size!"
    except AssertionError as exc:
        print(exc)
        sys.exit(1)

    obj = PCA(
        n_components=1,
        relaxation_schedule=1,
        num_samples=num_samples,
        solver_access=solver_access,
        ip_addr=ip_addr,
        port=port,                        
    )
    resp_hash = obj.fit(X)
    X_pca = obj.transform(X)
    X_pca = normalize(X_pca, axis=0, norm="l2")

    obj = PCA_cls(
        n_components=1,
    )
    X_pca_cls = obj.fit_transform(X)
    X_pca_cls = normalize(X_pca_cls, axis=0, norm="l2")

    response = resp_hash["component_1_response"] 
    energy = get_dirac3_energy(response)
    merit = abs(np.diag(np.matmul(X_pca.transpose(), X_pca_cls)))[0]
    runtime = get_dirac3_runtime(response)

    try:
        assert energy is not None, "The energy could not be computed!"
        assert merit is not None, "The merit could not be computed!"
        assert runtime is not None, "The runtime could not be computed!"        
    except AssertionError as exc:
        print(exc)
        sys.exit(1)
    
    return energy, merit, runtime
