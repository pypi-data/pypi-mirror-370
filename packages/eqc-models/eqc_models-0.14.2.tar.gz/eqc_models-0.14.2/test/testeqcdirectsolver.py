# (C) Quantum Computing Inc., 2024.
from unittest import TestCase
import numpy as np
# from eqc_models import EqcDirectSolver, QuadraticModel

class SolveTestCase(TestCase):
    """ Not testing solver right now """
    # def setUp(self):
    #     C = np.array([-1, 0]).reshape((2, 1))
    #     J = np.array([[0, 1],
    #                   [1, 0]], dtype=np.float32)
    #     self.model = QuadraticModel(C, J, 10)
    #     self.model.upper_bound = 10*np.ones((2,))
    #     self.solver = EqcDirectSolver()

    # def testSolve(self):
    #     response = self.solver.solve(2, 0.1)
    #     solution = response["solution"]
    #     self.assertEqual(len(solution), 2, "Solution length is incorrect")
