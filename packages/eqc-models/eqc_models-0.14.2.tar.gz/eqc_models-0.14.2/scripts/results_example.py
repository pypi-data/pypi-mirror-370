from eqc_models.solvers import Dirac3ContinuousCloudSolver
from eqc_models.base import PolynomialModel
from eqc_models.base import SolutionResults

def solve_polynomial(polynomial_coefficients, polynomial_indices, upper_bound, solver, **kwargs):

    model = PolynomialModel(polynomial_coefficients, polynomial_indices)
    model.upper_bound = ub

    response = solver.solve(model, **kwargs)

    results = SolutionResults.from_cloud_response(model, response, solver)

    return results

if __name__ == "__main__":
    import os.path
    import json
    import numpy as np

    coefficients = np.array([-1, -1, 1])
    indices = np.array([[1, 1], [2, 2], [1, 2]])
    ub = [1, 1]
    solver = Dirac3ContinuousCloudSolver()
    results = solve_polynomial(coefficients, indices, ub, solver, num_samples=2, relaxation_schedule=1, sum_constraint=1)

    print("Job results:")
    print("Solution energies:", results.energies)
    print("Solutions:", results.solutions)
    print("Total device time:", results.device_time)
    print("Average device time:", results.device_time / results.total_samples)
