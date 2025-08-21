# (C) Quantum Computing Inc., 2024.
import numpy as np
from eqc_models.solvers.qciclient import Dirac1CloudSolver
from eqc_models import QuadraticModel

# solve a basic QUBO
J = np.array([[0, 1], [1, 0]], dtype=np.float32)
c = np.array([-1, -1], dtype=np.float32)

model = QuadraticModel(c, J)
model.upper_bound = np.array([1, 1])
solver = Dirac1CloudSolver()

response = solver.solve(model, num_samples=5)

print(response["results"])

# get the job metrics for the previous job
metrics = solver.client.get_job_metrics(
    job_id=response["job_info"]["job_id"]
)
print(metrics)
