# (C) Quantum Computing Inc., 2024.
import numpy as np

# setting EPSILON to the most precise value Dirac devices can currently achieve 
EPSILON = 0.0001

class BisectionMixin:

    def decode(self, solution):
        """ Use a bisection method to determine the a binary solution from fractional values """
        model = self.model

        lower = np.min(solution)
        upper = np.max(solution)

        while upper - lower > EPSILON:
            middle = (upper + lower) / 2
            test_solution = (np.where(solution>=middle).astype(np.int32))
            # test feasibility
            # if model.is_feasible(test_solution):