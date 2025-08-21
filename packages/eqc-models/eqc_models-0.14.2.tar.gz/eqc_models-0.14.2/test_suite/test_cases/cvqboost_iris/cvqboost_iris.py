# (C) Quantum Computing Inc., 2025.
import sys
import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score

from test_utils import get_dirac3_energy, get_dirac3_runtime
from eqc_models.ml.classifierqboost import QBoostClassifier


def run_problem(config_dict):
    data_dir = config_dict["data_dir"]
    hamiltonian_size = config_dict["hamiltonian_size"]
    num_samples = int(config_dict["num_samples"])
    solver_access = config_dict["solver_access"]
    ip_addr = config_dict["ip_addr"]
    port = config_dict["port"]
    
    
    X_train = np.load(os.path.join(data_dir, "X_train.npy"))
    y_train = np.load(os.path.join(data_dir, "y_train.npy"))
    X_test = np.load(os.path.join(data_dir, "X_test.npy"))
    y_test = np.load(os.path.join(data_dir, "y_test.npy"))

    try:
        assert X_train.shape[1] == hamiltonian_size, "Inconsistent size!"
    except AssertionError as exc:
        print(exc)
        sys.exit(1)

    try:
        assert X_test.shape[1] == hamiltonian_size, "Inconsistent size!"
    except AssertionError as exc:
        print(exc)
        sys.exit(1)

    obj = QBoostClassifier(
        relaxation_schedule=1,
        num_samples=num_samples,
        solver_access=solver_access,
        ip_addr=ip_addr,
        port=port,
        lambda_coef=0,
    )
    response = obj.fit(X_train, y_train)
    y_train_prd = obj.predict(X_train)
    y_test_prd = obj.predict(X_test)

    energy = get_dirac3_energy(response)
    merit = accuracy_score(y_test, y_test_prd)
    runtime = get_dirac3_runtime(response)

    try:
        assert energy is not None, "The energy could not be computed!"
        assert merit is not None, "The merit could not be computed!"
        assert runtime is not None, "The runtime could not be computed!"        
    except AssertionError as exc:
        print(exc)
        sys.exit(1)

    return energy, merit, runtime


# if __name__ == "__main__":
#    config_dict = json.load(
#        open("test_cases/cvqboost_iris/cvqboost_iris.json", "r")
#    )
#    print(run_problem(config_dict))
