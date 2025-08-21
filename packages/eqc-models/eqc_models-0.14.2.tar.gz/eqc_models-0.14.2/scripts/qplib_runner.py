# (C) Quantum Computing Inc., 2024.
# (C) Quantum Computing Inc., 2024.
import os.path
import pickle
import numpy as np
from eqc_models.utilities.qplib import QGLModel
from eqc_models.solvers import Dirac3CloudSolver

if __name__ == "__main__":
    import sys
    alpha = float(sys.argv[1])
    R = float(sys.argv[2])
    schedule = int(sys.argv[3])
    fname = sys.argv[4]
    basename = os.path.basename(fname)
    basename = os.path.splitext(fname)[0]
    print(f"Loading model {basename} from {fname}")
    parts = pickle.load(open(fname, "rb"))
    C = parts["C"]
    J = parts["J"]
    A = parts["A"]
    b = parts["b"]
    types = parts["types"]
    num_variables = parts["num_variables"]
    # specify the dictionary as key: value with (index): coefficient
    model = QGLModel(C, J, A, b, R)
    upper_bound = [R if types[j] == "REAL" else 1 for j in range(num_variables)]
    model.upper_bound = np.array(upper_bound)
    model.penalty_multiplier = alpha
    print(f"Constructed model with R={R} alpha={alpha}")
    solver = Dirac3CloudSolver()
    print(f"Running model with relaxation_schedule={schedule}")
    response = solver.solve(model, basename, relaxation_schedule=schedule)
    print(f"Energy {response['results']['energies'][0]}")
