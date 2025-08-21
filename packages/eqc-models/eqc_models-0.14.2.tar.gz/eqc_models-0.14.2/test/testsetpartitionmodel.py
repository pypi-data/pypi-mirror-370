# (C) Quantum Computing Inc., 2024.
from unittest import TestCase
import numpy as np
from eqc_models.assignment.setpartition import SetPartitionModel
from eqc_models.base.operators import QUBO

class SetPartitionModelTestCase(TestCase):
    def test_initialization(self):
        # Test initialization with sample data
        subsets = [{"A", "B"}, {"B", "C"}, {"C", "D"}, {"A", "D"}]
        weights = [1.0, 2.0, 3.0, 4.0]
        model = SetPartitionModel(subsets=subsets, weights=weights)

        # Check that the universal set is correctly initialized
        assert model.universal_set == {"A", "B", "C", "D"}, "Universal set should contain all unique elements"

        # Check that the constraints matrix (A) and vector (b) have correct dimensions
        A, b = model.constraints
        assert A.shape == (len(model.universal_set), len(subsets)), "Constraints matrix A has incorrect dimensions"
        assert b.shape == (len(model.universal_set),), "Constraints vector b has incorrect dimensions"
        assert np.all(b == 1), "Constraints vector b should be all ones"

    def test_polynomial_terms(self):
        # Test polynomial term construction
        subsets = [{"A", "B"}, {"B", "C"}]
        weights = [1.0, 2.0]
        model = SetPartitionModel(subsets=subsets, weights=weights)

        # Construct expected values for polynomial terms
        # A, b = model.constraints
        # J = A.T @ A
        # h = -2 * b.T @ A
        # expected_indices, expected_coefficients = model._construct_polynomial_terms(h.reshape(-1, 1), J)
        expected_indices, expected_coefficients = model._construct_polynomial_terms(
            np.array(weights).reshape(-1, 1), np.zeros((len(weights), len(weights))))

        # Validate polynomial terms
        assert np.all(model.coefficients == expected_coefficients), "Polynomial coefficients do not match expected values"
        assert np.all(model.indices == expected_indices), "Polynomial indices do not match expected values"

    def test_H_property(self):
        # Test the H property to ensure it returns the correct Hamiltonian format
        subsets = [{"A"}, {"B"}]
        weights = [1.0, 1.0]
        model = SetPartitionModel(subsets=subsets, weights=weights)

        # Check if H returns the correct tuple of coefficients and indices
        coefficients, indices = model.H
        assert isinstance(coefficients, list), "H should return a list of coefficients"
        assert isinstance(indices, list), "H should return a list of indices"
        assert len(coefficients) == len(indices), "H should return equal-length lists for coefficients and indices"

    def test_evaluate_objective(self):
        # Test the objective function evaluation
        subsets = [{"A", "B"}, {"B", "C"}, {"C", "D"}, {"A", "D"}]
        weights = [1.0, 2.0, 3.0, 4.0]
        model = SetPartitionModel(subsets=subsets, weights=weights)

        # Define a solution vector and calculate the expected objective value
        solution = np.array([1, 0, 1, 0])  # Selects subsets 1 and 3
        expected_value = weights[0] + weights[2]
        assert model.evaluateObjective(solution) == expected_value, "Objective function evaluation is incorrect"

    def test_penalty_multiplier(self):
        # Test setting and getting the penalty multiplier
        subsets = [{"A"}, {"B"}]
        weights = [1.0, 1.0]
        model = SetPartitionModel(subsets=subsets, weights=weights)
        model.penalty_multiplier = 1.5

        # Verify penalty multiplier is set correctly
        assert model.penalty_multiplier == 1.5, "Penalty multiplier should be initialized to the given alpha"

        # Change penalty multiplier and verify
        model.penalty_multiplier = 2.5
        assert model.penalty_multiplier == 2.5, "Penalty multiplier should be updated to the new value"

    def test_qubo_property(self):
        # Test the H property to ensure it returns the correct Hamiltonian format
        subsets = [{"A"}, {"B"}]
        weights = [1.0, 1.0]
        model = SetPartitionModel(subsets=subsets, weights=weights)
        model.upper_bound = np.ones(len(subsets))

        # Check if H returns the correct tuple of coefficients and indices
        qubo = model.qubo
        assert isinstance(qubo, QUBO), "qubo should return a QUBO operator"
