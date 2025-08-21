import numpy as np
from eqc_models.base.binaries import make_binary_penalty
from eqc_models.base.results import SolutionResults

def make_polynomial(n, penalty_multiplier):
    problem_variables = [f"x{i}" for i in range(1, n+1)]
    slack_variables = [f"w{i}" for i in range(1, n+1)]
    variables = problem_variables + slack_variables
    coefficients = []
    indices = []
    offset = 0
    for x, w in zip(problem_variables, slack_variables):
        idx1 = variables.index(x) + 1
        idx2 = variables.index(w) + 1
        coefficients.extend([1, -1])
        indices.extend([[idx1, idx1], [0, idx1]])
        penalty_coefficients, penalty_indices, var_offset = make_binary_penalty(idx1, idx2, penalty_multiplier=penalty_multiplier)
        offset += var_offset
        indices += penalty_indices
        coefficients += penalty_coefficients
    
    return coefficients, indices, offset

if __name__ == "__main__":
    import sys
    from eqc_models.base import PolynomialModel
    from eqc_models.solvers import Dirac3ContinuousCloudSolver
    from hexalyeqc import HexalyContinuousSolver

    n = int(sys.argv[1])
    penalty_multiplier = float(sys.argv[2])
    coefficients, indices, offset = make_polynomial(n, penalty_multiplier)
    for idx, val in zip(indices, coefficients):
        print(idx, val)
    model = PolynomialModel(coefficients, indices)
    model.upper_bound = np.ones(2*n)
    solver = Dirac3ContinuousCloudSolver()
    solver = HexalyContinuousSolver()
    response = solver.solve(model, sum_constraint=n, num_samples=5, relaxation_schedule=2)
    # results = SolutionResults.from_cloud_response(model, response, solver)
    # for i in range(len(results.solutions)):
    #     print(results.solutions[i])
    print(response)
    test_sol = np.zeros(2*n)
    test_sol[:n] = 1
    print(model.evaluate(test_sol) + offset)
