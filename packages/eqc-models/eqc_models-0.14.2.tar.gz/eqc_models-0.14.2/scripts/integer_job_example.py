# (C) Quantum Computing Inc., 2024.
import numpy as np
from eqc_models.solvers.qciclient import Dirac3IntegerCloudSolver
from eqc_models import QuadraticModel, PolynomialModel

# solve a basic QUBO

J = np.array([[0, 1], [1, 0]], dtype=np.float32)
c = np.array([-1, -1], dtype=np.float32)

model = QuadraticModel(c, J)
model.upper_bound = np.array([1, 1])
solver = Dirac3IntegerCloudSolver()

response = solver.solve(model, num_samples=5, relaxation_schedule=1)

print(response["results"])

# solve the same QUBO, but specified as a polynomial

coefficients = np.array([-1, -1, 2,])
indices = np.array([(0, 1), (0, 2), (1, 2),])
model = PolynomialModel(coefficients, indices)
model.upper_bound = np.array([1, 1])
# use the Dirac-3 solver, but specify some additional parameters to control
# the sampling
# mean_photon_number values of 0.1 and 0.3 have tested well for certain problems
# normalized_loss_rate values of 4 to 7 have tested well for certain problems
response = solver.solve(model, num_samples=5, relaxation_schedule=2,
                        mean_photon_number=0.0066, quantum_fluctuation_coefficient=4)
print(response["results"])

# get the job metrics for the previous job
metrics = solver.client.get_job_metrics(job_id=response["job_info"]["job_id"])
print(metrics)
