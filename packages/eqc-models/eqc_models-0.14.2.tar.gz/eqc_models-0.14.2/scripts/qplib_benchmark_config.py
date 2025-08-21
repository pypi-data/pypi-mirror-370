# (C) Quantum Computing Inc., 2024.
"""
This script creates the files needed to test QPLIB problems

## Input
qplib file - a file in the qplib format describing a Quadratic Programming problem instance

## Output
coefficient file - a line-per-term file describing only the coefficients of the polynomial
indices file - a line-per-term file describing only the indices of the polynomial terms. will
               be joined to the lines of the coefficient file to produce the terms of the 
               polynomial. The lines of the file must be comma-delimited.
config file - a line-per-settign file with `NAME=value` syntax

"""

import logging
import numpy as np
from eqc_models.utilities.qplib import file_to_model, file_to_polynomial
from eqc_models.solvers import Dirac3CloudSolver
from eqc_models.algorithms import PenaltyMultiplierAlgorithm

if __name__ == "__main__":
    import csv
    import sys
    import os
    import os.path

    logging.basicConfig(level=logging.INFO)
    override_alpha = os.environ.get("MANUAL_ALPHA", None)
    if override_alpha is not None:
        override_alpha = float(override_alpha)
    fname = sys.argv[1]
    print(f"Processing {fname}")
    coefficients, indices, sum_constraint = file_to_polynomial(open(fname))
    noext = os.path.splitext(fname)[0]
    model = file_to_model(open(fname), sum_constraint)
    model.upper_bound = np.array([sum_constraint for i in range(model.linear_objective.shape[0])])
    if override_alpha is None:
        solver = Dirac3CloudSolver()
        print("Running penalty multiplier algorithm (It is safe to Ctrl-C to interrupt)")
        algorithm = PenaltyMultiplierAlgorithm(model, solver)
        maxval = np.max(model.linear_objective)
        maxval2 = np.max(model.quad_objective)
        if maxval2 > maxval:
            maxval = maxval2
        algorithm.upper_bound = model.sum_constraint * maxval
        try:
            algorithm.run(initial_alpha=None, relaxation_schedule=1, num_samples=1)
        except KeyboardInterrupt:
            print("********* INTERRUPTED *********")
        alpha = algorithm.alphas[-1]
    else:
        alpha = override_alpha
    coefficients, indices, sum_constraint = file_to_polynomial(open(fname), penalty_multiplier=alpha)
    settings = {}
    settings["problem"] = os.path.basename(noext).upper()
    settings["formulation"] = "Qudit Hamiltonian"
    settings["hardware"] = "CHANGEME"
    settings["hardware_version"] = "CHANGEME"
    settings["variable_count"] = model.n
    settings["constraint_count"] = "CHANGEME"
    settings["inequality_constraint_count"] = "CHANGEME"
    settings["slack_variable_count"] = "CHANGEME"
    settings["relaxation_schedule"] = "CHANGEME"
    settings["summation_constraint"] = "CHANGEME"
    settings["non_zero_count"] = len(coefficients)
    settings["max_degree"] = len(indices[0])
    settings["number_of_tests"] = "CHANGEME"
    settings["info_link"] = "CHANGEME"
    settings["alpha"] = alpha

    with open(f"{noext}-coefficients.csv", "w") as f1:
        writer = csv.writer(f1)
        for coefficient in coefficients:
            writer.writerow([coefficient])
    with open(f"{noext}-indices.csv", "w") as f1:
        writer = csv.writer(f1)
        for index in indices:
            writer.writerow(index)
    with open(f"{noext}.config", "w") as f1:
        for k, v in settings.items():
            f1.write(f"{k}={v}\n")
