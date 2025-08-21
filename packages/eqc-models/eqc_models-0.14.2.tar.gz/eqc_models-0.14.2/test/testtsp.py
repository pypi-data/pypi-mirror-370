# (C) Quantum Computing Inc., 2024.
from unittest import TestCase
import numpy as np
from eqc_models.sequence import MTZTSPModel
from eqc_models.base.operators import Polynomial, QUBO

class MTZTSPTestCase(TestCase):

    def setUp(self):
        self.D = D = {(1, 2): 1, (2, 1): 1, (1, 3): 2, (3, 1): 2, (2, 3): 3, (3, 2): 3}
        self.model = model = MTZTSPModel(D)
        model.penalty_multiplier = 10
        self.solution = np.array([1, 0, 0, 1, 1, 0, 1, 2, 3, 4, 4, 2, 5])
        self.infeasible1 = np.array([0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 4, 2, 5])
        self.infeasible2 = 1 - np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    
    def testDistance(self):
        self.assertEqual(self.model.distance(1, 2), 1)
        self.assertEqual(self.model.distance(3, 2), 3)

    def testSolutionCost(self):
        
        self.assertEqual(self.model.cost(self.solution), 6)
        
    def checkConstraints(self):
        lhs, rhs = self.model.constraints
        self.assertTrue((lhs@self.solution - rhs == 0).all(), "Incorrect constraints for feasible solution")

    def checkPolynomialOperator(self):
        self.model.penalty_multiplier *= 1
        poly = self.model.polynomial
        # This should equal the cost function
        evaluated = poly.evaluate(self.solution) + self.model.alpha * self.model.offset
        self.assertEqual(evaluated, 6.0, "Polynomial evaluation does not match cost")

    def testInfeasibleRoute(self):
        # test a couple infeasible solutions
        infeasible = self.infeasible1
        lhs, rhs = self.model.constraints
        Pl, Pq = -2 * rhs.T@lhs, lhs.T@lhs
        evaluated = Pl.T@infeasible + infeasible.T@Pq@infeasible + self.model.offset
        self.assertGreater(evaluated, 0, "Penalty not positive for infeasible solution")
        
    def testInfeasibleOnes(self):
        self.model.penalty_multiplier *= 1
        infeasible = self.infeasible2
        poly = self.model.polynomial
        evaluated = poly.evaluate(infeasible) + self.model.alpha * self.model.offset
        self.assertGreater(evaluated, 6, "Infeasible solution giving value lower than optimal solution")

    def testMultiplier(self):
        # Test that the multiplier has the expected effect
        self.model.penalty_multiplier *= 1
        infeasible = self.infeasible2
        poly = self.model.polynomial
        val1 = poly.evaluate(infeasible) + self.model.alpha * self.model.offset
        self.model.penalty_multiplier *= 2
        poly2 = self.model.polynomial
        val2 = poly2.evaluate(infeasible) + self.model.alpha * self.model.offset
        self.assertLess(val1, val2)
