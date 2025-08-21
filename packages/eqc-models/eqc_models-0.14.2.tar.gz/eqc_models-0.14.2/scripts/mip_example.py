import numpy as np
from eqc_models.base.results import SolutionResults

def make_polynomial(n):
    problem_variables = [f"x{i}" for i in range(1, n+1)]
    variables = problem_variables
    coefficients = []
    indices = []
    for x in variables:
        idx1 = variables.index(x) + 1
        coefficients.append(-1 + 2*np.random.random())
        indices.append([idx1, idx1])
    for x1 in variables:
        idx1 = variables.index(x1) + 1
        for x2 in variables:
            idx2 = variables.index(x2) + 1
            if idx2>idx1:
                coefficients.append(-1 + 2*np.random.random())
                indices.append([idx1, idx2])
        
    return np.array(coefficients), np.array(indices), variables

if __name__ == "__main__":
    import sys
    import logging
    from eqc_models.base import PolynomialModel
    from eqc_models.solvers import Dirac3MIPCloudSolver

    logging.basicConfig(level=logging.INFO)
    n = int(sys.argv[1])
    penalty_multiplier = float(sys.argv[2])
    coefficients, indices, variables = make_polynomial(n)
    for idx, val in zip(indices, coefficients):
        print(idx, val)
    model = PolynomialModel(coefficients, indices)
    model.variables = variables
    is_discrete = [True for i in range(n)]
    model.is_discrete = is_discrete
    model.upper_bound = np.ones(n)
    solver = Dirac3MIPCloudSolver()
    # must pass penalty multiplier since PolynomialModel doesn't have the penalty_multiplier attribute
    # n for sum constraint because the auxiliary variables will be 0 or 1, so all variables will sum to n
    response = solver.solve(model, sum_constraint=n, num_samples=5, relaxation_schedule=1, penalty_multiplier=penalty_multiplier)
    for i, solution in enumerate(response.solutions):
        decisions = solution[:n]
        print("Solution number", i, "Energy", response.energies[i])
        print(np.round(decisions, 2))
