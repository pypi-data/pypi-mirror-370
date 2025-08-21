# (C) Quantum Computing Inc., 2024.
from unittest import TestCase
from eqc_models import PolynomialModel
import numpy as np

class EvalPolynomialTestCase(TestCase):

    def setUp(self):
        coefficients = [1, 2, 3]
        indices = [[0, 0, 1], [0, 1, 1], [1, 1, 1]]
        self.polynomial = PolynomialModel(coefficients, indices)

    def testEval1(self):
        polynomial = self.polynomial
        solution = [1]
        value = polynomial.evaluate(solution)
        self.assertEqual(value, 6)

    def testEval10(self):
        polynomial = self.polynomial
        solution = [10]
        value = polynomial.evaluate(solution)
        self.assertEqual(value, 1*solution[0]+2*solution[0]**2+3*solution[0]**3)

class PolynomialAttributesTestCase(TestCase):

    def setUp(self):
        self.coefficients = np.array([1, 2, 3])
        self.indices = np.array([[0, 0, 1], [0, 1, 1], [1, 1, 1]])
        self.polynomial = PolynomialModel(self.coefficients, self.indices)

    def testH(self):
        test_c, test_i = self.polynomial.H
        self.assertTrue((test_c==self.coefficients).all())
        self.assertTrue((test_i==self.indices).all())

class QuadraticPolynomialTestCase(TestCase):

    def setUp(self):
        coefficients = [1, 2, 3, 4]
        indices = [[0, 1], [0, 2], [1, 1], [1, 2]]
        self.polynomial = PolynomialModel(coefficients, indices)
        self.polynomial.upper_bound = np.ones(2)

    def test_qubo(self):
        qubo = np.array([[4, 2], [2, 2]])
        self.assertTrue(np.array_equal(self.polynomial.qubo.Q, qubo))

    def test_qubo_log_encoding_uniform_1(self):
        self.polynomial.upper_bound = np.array([2, 2])
        qubo = np.array([[4, 6, 2, 4], [6, 14, 4, 8], [2, 4, 2, 0], [4, 8, 0, 4]])
        self.assertTrue(np.array_equal(self.polynomial.qubo.Q, qubo))

    def test_qubo_log_encoding_uniform_2(self):
        self.polynomial.upper_bound = np.array([3, 3])
        qubo = np.array([[4, 6, 2, 4], [6, 14, 4, 8], [2, 4, 2, 0], [4, 8, 0, 4]])
        self.assertTrue(np.array_equal(self.polynomial.qubo.Q, qubo))

    def test_qubo_log_encoding_non_uniform_1(self):
        self.polynomial.upper_bound = np.array([1, 2])
        qubo = np.array([[4, 2, 4], [2, 2, 0], [4, 0, 4]])
        self.assertTrue(np.array_equal(self.polynomial.qubo.Q, qubo))

    def test_qubo_log_encoding_non_uniform_2(self):
        self.polynomial.upper_bound = np.array([1, 4])
        qubo = np.array([[4, 2, 4, 8], [2, 2, 0, 0], [4, 0, 4, 0], [8, 0, 0, 8]])
        self.assertTrue(np.array_equal(self.polynomial.qubo.Q, qubo))

    def test_equality_of_evaluations_uniform(self):
        """
        Make sure log encoding evaluation returns equivalent evaluation as polynomial format evaluation
        """
        self.polynomial.upper_bound = np.array([3, 3])
        qubo_sol = np.array([1, 0, 1, 1])
        poly_sol = np.array([1, 3])
        qubo_eval = qubo_sol @ self.polynomial.qubo.Q @ qubo_sol
        poly_eval = self.polynomial.evaluate(poly_sol)
        self.assertEqual(qubo_eval, poly_eval)

    def test_equality_of_evaluations_non_uniform(self):
        """
        Make sure log encoding evaluation returns equivalent evaluation as polynomial format evaluation
        """
        self.polynomial.upper_bound = np.array([1, 2])
        qubo_sol = np.array([1, 0, 1])
        poly_sol = np.array([1, 2])
        qubo_eval = qubo_sol @ self.polynomial.qubo.Q @ qubo_sol
        poly_eval = self.polynomial.evaluate(poly_sol)
        self.assertEqual(qubo_eval, poly_eval)
