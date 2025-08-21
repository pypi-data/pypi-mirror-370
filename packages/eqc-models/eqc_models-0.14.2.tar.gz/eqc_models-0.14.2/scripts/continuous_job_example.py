# (C) Quantum Computing Inc., 2024.
import numpy as np
from eqc_models.solvers.qciclient import Dirac3ContinuousCloudSolver
from eqc_models import QuadraticModel

# minimize a basic quadratic expression

J = np.array([[1, 1], [1, 1]], dtype=np.float32)
c = np.array([-1, -1], dtype=np.float32)

model = QuadraticModel(c, J)
model.upper_bound = np.array([1, 1])
solver = Dirac3ContinuousCloudSolver()

response = solver.solve(model, num_samples=5, relaxation_schedule=1, sum_constraint=1)

print(response["results"])
