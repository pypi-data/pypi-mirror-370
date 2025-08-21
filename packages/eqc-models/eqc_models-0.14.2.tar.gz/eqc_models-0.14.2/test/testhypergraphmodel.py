import unittest
import numpy as np
import pandas as pd
from eqc_models.graph.hypergraph import HypergraphModel


class TestHypergraphModel(unittest.TestCase):

    def test_list_of_lists(self):
        data = [['A', 'B', 'C'], ['A', 'D'], ['C', 'D', 'E']]
        model = HypergraphModel(data)

        coefficients, indices = model.H
        expected_coefficients = np.array([1.0, 1.0, 1.0])
        expected_indices = np.array([[0, 1, 4], [1, 2, 3], [3, 4, 5]])

        np.testing.assert_array_equal(coefficients, expected_coefficients)
        np.testing.assert_array_equal(indices, expected_indices)

    def test_dict_of_tuples(self):
        data = {0: ('A', 'B'), 1: ('B', 'C', 'D'), 2: ('D', 'E')}
        model = HypergraphModel(data)

        coefficients, indices = model.H
        expected_coefficients = np.array([1.0, 1.0, 1.0])
        expected_indices = np.array([[0, 1, 2], [0, 4, 5], [2, 3, 4]])

        np.testing.assert_array_equal(coefficients, expected_coefficients)
        np.testing.assert_array_equal(indices, expected_indices)

    def test_numpy_array(self):
        data = np.array([['G1', 'A'], ['G1', 'B'], ['G2', 'C'], ['G2', 'D'], ['G3', 'E']])
        model = HypergraphModel(data)

        coefficients, indices = model.H
        expected_coefficients = np.array([1.0, 1.0, 1.0])
        expected_indices = np.array([[0, 5], [1, 2], [3, 4]])

        np.testing.assert_array_equal(coefficients, expected_coefficients)
        np.testing.assert_array_equal(indices, expected_indices)

    def test_pandas_dataframe(self):
        data = pd.DataFrame({
            'Edge': ['E1', 'E1', 'E1', 'E2', 'E2', 'E3', 'E3'],
            'Node': ['A', 'B', 'C', 'D', 'B', 'C', 'E'],
            'weight': [1.0, 2.0, 1.5, 2.5, 1.0, 0.5, 3.0]
        })
        model = HypergraphModel(data)

        coefficients, indices = model.H
        expected_coefficients = np.array([2.5, 0.5, 1.0])
        expected_indices = np.array([[0, 2, 4], [0, 3, 5], [1, 2, 3]])

        np.testing.assert_array_equal(coefficients, expected_coefficients)
        np.testing.assert_array_equal(indices, expected_indices)

    def test_evaluate_objective(self):
        data = [['A', 'B'], ['B', 'C']]
        lhs = np.array([[1, -1, 0], [0, -1, 1], [1, -1, 1]])
        rhs = np.array([0, 0, 0])
        model = HypergraphModel(data, lhs=lhs, rhs=rhs, alpha=2.0)

        solution = np.array([1, 1, 0])
        objective_value = model.evaluateObjective(solution)
        self.assertAlmostEqual(objective_value, 1.0)  # Expected objective value based on data

    def test_evaluate(self):
        data = [['A', 'B'], ['B', 'C']]
        lhs = np.array([[1, -1, 0], [0, -1, 1], [1, -1, 1]])
        rhs = np.array([0, 0, 0])
        model = HypergraphModel(data, lhs=lhs, rhs=rhs, alpha=2.0)

        solution = np.array([1, 1, 0])
        total_value = model.evaluate(solution, includeoffset=True)
        self.assertAlmostEqual(total_value, 3.0)  # Check total evaluation with penalties


if __name__ == '__main__':
    unittest.main()
