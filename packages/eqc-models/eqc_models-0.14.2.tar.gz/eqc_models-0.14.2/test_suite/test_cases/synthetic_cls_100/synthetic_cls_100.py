# (C) Quantum Computing Inc., 2025.
import sys
import os
import json
import numpy as np
import pandas as pd

from test_utils import get_dirac3_energy, get_dirac3_runtime
from eqc_models import QuadraticModel
from eqc_models.solvers.qciclient import Dirac3CloudSolver
from eqc_models.solvers.eqcdirect import Dirac3DirectSolver

def run_problem(config_dict):
    data_dir = config_dict["data_dir"]
    hamiltonian_size = config_dict["hamiltonian_size"]
    num_samples = int(config_dict["num_samples"])
    solver_access = config_dict["solver_access"]
    ip_addr = config_dict["ip_addr"]
    port = config_dict["port"]
    
    J = np.load(os.path.join(data_dir, "J_8000000_100.npy"))
    C = np.load(os.path.join(data_dir, "C_8000000_100.npy"))
    
    try:
        assert C.shape[0] == hamiltonian_size, "Inconsistent size!"
        assert J.shape[0] == hamiltonian_size, "Inconsistent size!"
        assert J.shape[1] == hamiltonian_size, "Inconsistent size!"        
    except AssertionError as exc:
        print(exc)
        sys.exit(1)

    sum_constraint = 1.0

    model = QuadraticModel(C, J)
    model.upper_bound = np.array([sum_constraint] * C.shape[0])

    if solver_access == "direct":
        solver = Dirac3DirectSolver()
        solver.connect(ip_addr, port)
    else:
        solver = Dirac3CloudSolver()    

    response = solver.solve(
        model,
        sum_constraint=sum_constraint,
        relaxation_schedule=1,
        num_samples=num_samples,
    )

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
