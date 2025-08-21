import unittest
import numpy as np
import networkx as nx
from scipy.sparse import isspmatrix_csr
from eqc_models.graph.partition import GraphPartitionModel


class TestGraphPartitionModel(unittest.TestCase):
    def setUp(self):
        """Set up a small test graph for partitioning."""
        self.G = nx.Graph()
        self.G.add_edges_from([
            (0, 1, {"weight": 1.0}),
            (1, 2, {"weight": 2.0}),
            (2, 0, {"weight": 3.0}),
            (2, 3, {"weight": 4.0}),
        ])
        self.k = 3
        self.alpha = 1.0
        self.gamma = 1.0
        self.beta_obj = 1.0
        self.model = GraphPartitionModel(G=self.G, k=self.k, alpha=self.alpha, gamma=self.gamma)

    def test_initialization(self):
        """Test that the model is initialized correctly."""
        self.assertEqual(self.model._k, self.k)
        self.assertEqual(self.model._alpha, self.alpha)
        self.assertEqual(self.model._gamma, self.gamma)
        self.assertEqual(self.model._num_nodes, self.G.number_of_nodes())
        self.assertTrue(isspmatrix_csr(self.model._laplacian), "Laplacian matrix is not a CSR sparse matrix.")

    def test_objective_matrix(self):
        """Test that the objective matrix is created correctly."""
        self.assertTrue(isspmatrix_csr(self.model._objective_matrix), "Objective matrix is not a CSR sparse matrix.")
        self.assertEqual(self.model._objective_matrix.shape[0], self.model._num_nodes * self.k)

    def test_balanced_partition_term(self):
        """Test the creation of the balanced partition term."""
        balance_term = self.model.get_balanced_partition_term()
        self.assertTrue(isspmatrix_csr(balance_term), "Balanced partition term is not a CSR sparse matrix.")
        self.assertEqual(balance_term.shape, (self.model._num_nodes * self.k, self.model._num_nodes * self.k))
        self.assertGreater(self.model._balanced_partition_offset, 0)

    def test_constraints(self):
        """Test the creation of the constraints matrix."""
        constraints = self.model.get_constraints()
        self.assertTrue(isspmatrix_csr(constraints), "Constraints term is not a CSR sparse matrix.")
        self.assertEqual(constraints.shape, (self.model._num_nodes * self.k, self.model._num_nodes * self.k))
        self.assertGreater(self.model._constraints_offset, 0)

    def test_evaluate(self):
        """Test the evaluation of the objective function."""
        solution = np.random.randint(0, 2, size=(self.model._num_nodes * self.k,))
        value = self.model.evaluate(solution)
        self.assertIsInstance(value, float, "Objective value is not a float.")

    def test_decode(self):
        """Test the decoding of the solution vector."""
        solution = np.array([0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0])
        decoded = self.model.decode(solution)
        self.assertIsInstance(decoded, dict, "Decoded solution is not a dictionary.")
        self.assertEqual(len(decoded), self.model._num_nodes, "Decoded solution does not include all nodes.")

    def test_two_partition_qubo(self):
        """Test the QUBO matrix generation for two partitions."""
        model_two_partition = GraphPartitionModel(G=self.G, k=2, alpha=self.alpha, gamma=self.gamma)
        qubo_matrix = model_two_partition.get_two_partition_qubo()
        self.assertTrue(isspmatrix_csr(qubo_matrix), "Two-partition QUBO matrix is not a CSR sparse matrix.")
        self.assertEqual(qubo_matrix.shape, (self.G.number_of_nodes(), self.G.number_of_nodes()))

    def test_cost_function(self):
        """Test the cost function generation."""
        h, J = self.model.costFunction()
        self.assertIsInstance(h, np.ndarray, "Linear term h is not a numpy array.")
        self.assertEqual(len(h), self.model._num_nodes * self.k, "Linear term h has incorrect length.")
        self.assertTrue(isspmatrix_csr(J), "Quadratic term J is not a CSR sparse matrix.")

    def test_invalid_k(self):
        """Test that invalid values of k raise an exception."""
        with self.assertRaises(AssertionError):
            GraphPartitionModel(G=self.G, k=1, alpha=self.alpha, gamma=self.gamma)

    def test_invalid_solution(self):
        """Test that invalid solutions raise an exception."""
        invalid_solution = np.random.randint(0, 2, size=(self.model._num_nodes * self.k - 1,))
        with self.assertRaises(AssertionError):
            self.model.evaluate(invalid_solution)

    def test_k_equals_two(self):
        """Test GraphPartitionModel for k=2 (two-partition case)."""
        k = 2
        model = GraphPartitionModel(G=self.G, k=k, alpha=self.alpha, beta_obj=self.beta_obj, gamma=self.gamma)

        # Check initialization
        self.assertEqual(model._k, k, "Number of partitions (k) should be 2.")
        self.assertEqual(model._num_nodes, self.G.number_of_nodes(), "Number of nodes mismatch.")
        self.assertTrue(isspmatrix_csr(model._objective_matrix), "Objective matrix should be a CSR sparse matrix.")

        # Test the QUBO matrix for k=2
        qubo_matrix = model.get_two_partition_qubo()
        self.assertTrue(isspmatrix_csr(qubo_matrix), "QUBO matrix should be a CSR sparse matrix.")
        self.assertEqual(qubo_matrix.shape, (self.G.number_of_nodes(), self.G.number_of_nodes()),
                         "QUBO matrix dimensions should match the number of nodes.")

        # Check diagonal values
        adjacency = nx.to_scipy_sparse_matrix(self.G, weight="weight")
        degrees = adjacency.sum(axis=1).A1  # Convert to 1D array
        for i in range(self.G.number_of_nodes()):
            self.assertAlmostEqual(
                qubo_matrix[i, i],
                self.beta_obj * degrees[i] - self.alpha * (self.G.number_of_nodes() - 1),
                msg=f"Diagonal value mismatch at node {i}."
            )

        # Check off-diagonal values
        for i in range(self.G.number_of_nodes()):
            for j in range(self.G.number_of_nodes()):
                if i != j:
                    expected_value = (self.alpha - self.beta_obj * adjacency[i, j])
                    self.assertAlmostEqual(
                        qubo_matrix[i, j],
                        expected_value,
                        msg=f"Off-diagonal value mismatch at ({i}, {j})."
                    )

    def test_k_equals_two_solution_evaluation(self):
        """Test solution evaluation for k=2 case."""
        k = 2
        model = GraphPartitionModel(G=self.G, k=k, alpha=self.alpha, beta_obj=self.beta_obj, gamma=self.gamma)

        # Example solution for k=2 (binary assignment)
        solution = np.array([0, 1, 1, 0])  # Assign nodes to two partitions
        objective_value = model.evaluate(solution)

        # Check that the objective value is computed as expected
        expected_value = float(solution.T @ model._objective_matrix @ solution)
        self.assertAlmostEqual(objective_value, expected_value, "Objective value mismatch for k=2 solution.")

        # Test decoding of solution
        decoded_solution = model.decode(solution)
        self.assertIsInstance(decoded_solution, dict, "Decoded solution should be a dictionary.")
        self.assertEqual(len(decoded_solution), model._num_nodes, "Decoded solution should have entries for all nodes.")
        self.assertSetEqual(set(decoded_solution.values()), {0, 1}, "Partitions should only contain 0 or 1 for k=2.")


if __name__ == "__main__":
    unittest.main()
