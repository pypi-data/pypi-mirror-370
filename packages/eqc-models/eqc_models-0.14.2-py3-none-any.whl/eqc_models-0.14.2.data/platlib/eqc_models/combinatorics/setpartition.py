from typing import List, Tuple, Dict, Union
import numpy as np
from eqc_models.base import ConstraintsMixIn, PolynomialModel
from eqc_models.base.polynomial import ConstrainedPolynomialModel

class SetPartitionModel(ConstrainedPolynomialModel):
    """
    This class represents a set partitioning model for optimization problems that require selecting subsets
    to partition a universal set while minimizing an objective function defined by weights. Given a collection
    of subsets, a weight is assigned to each subset, and the goal is to determine an optimal selection of subsets
    to fully cover the universal set with minimized total weight.

    Parameters
    ----------

    subsets : List of sets
        List of sets (subsets) defining the collection to partition.
        Each element in this list represents a subset containing elements from the universal set.

    weights : List of floats
        List of weights corresponding to each subset. The length of this list should be equal to
        the number of subsets, with each weight indicating the cost or weight associated with selecting
        a particular subset.

    Attributes
    ----------

    H : tuple of np.ndarray
        Tuple containing the linear (h) and quadratic (J) coefficients for the Hamiltonian representation
        of the quadratic problem formulation.

    penalty_multiplier : float
        Value for weighting the penalties formed from the equality constraints.

    polynomial : Polynomial
        Polynomial operator representation for the model, constructed from the penalty terms
        to encode the set partition constraints.

    linear_objective : np.ndarray
        Array representing the linear objective function coefficients based on the weights of subsets.

    quad_objective : np.ndarray
        Quadratic objective function matrix initialized as zeros (no quadratic terms for objective).

    constraints : tuple of np.ndarray
        Matrix `A` and vector `b` representing constraints for the set partition problem:
        - `A`: Binary matrix indicating subset membership of elements in the universal set.
        - `b`: Vector of ones, enforcing full coverage of the universal set by the selected subsets.

    universal_set : set
        Set containing all unique elements present across the input subsets, representing the elements
        that must be fully covered in the partition solution.

    Example
    --------

    Given a list of subsets representing a set partition problem, each with an associated weight:

    >>> import numpy as np
    >>> np.random.seed(21)
    >>> subsets = [{"A", "B", "C"}, {"D", "E", "F"}, {"A", "F"}, {"B", "E"}, {"C", "D"}, {"A"},
                   {"B"}, {"C", "D", "E"}, {"B", "C"}]
    >>> weights = [100 * np.random.random() for _ in subsets]

    We can construct and use the `SetPartitionModel` as follows:

    >>> model = SetPartitionModel(subsets=subsets, weights=weights)
    >>> solution = np.random.randint(0, 2, len(subsets))  # Random binary solution vector
    >>> print("Objective Value:", model.evaluateObjective(solution))  # Evaluate solution cost

    This approach builds the constraints matrix and penalties automatically, enabling efficient
    optimization using solvers like `Dirac3CloudSolver`.
    """
    def __init__(self, subsets: List[set], weights: List[float]) -> None:
        # Combine subsets to form the universal set
        self.universal_set = set()
        for subset in subsets:
            self.universal_set = self.universal_set.union(subset)

        # Create the constraint matrix A and vector b
        A = []
        for x in self.universal_set:
            row = [1 if x in subset else 0 for subset in subsets]
            A.append(row)
        A = np.array(A)
        b = np.ones((A.shape[0],))
        n = A.shape[1]

        self.upper_bound = np.ones((n,), np.int32)

        # Define the linear objective function based on subset weights
        self.linear_objective = np.array(weights).reshape((n, 1))
        self.quad_objective = np.zeros((n, n)) #np.zeros_like(J)

        # Initialize PolynomialModel with J and h, properly formatted as indices and coefficients
        indices, coefficients = self._construct_polynomial_terms(self.linear_objective, self.quad_objective)
        super().__init__(coefficients, indices, A, b)

    def _construct_polynomial_terms(self, h: np.ndarray, J: np.ndarray) -> Tuple[List[List[int]], List[np.ndarray]]:
        """
        Constructs the polynomial terms (indices and coefficients) needed for the quadratic
        Hamiltonian representation of the problem.

        Parameters
        ----------
        h : np.ndarray
            Linear term of the penalty function as a 1D array.

        J : np.ndarray
            Quadratic term of the penalty function as a 2D array.

        Returns
        -------
        Tuple[List[List[int]], List[float]]
            A tuple where:
            - The first element is a list of index lists, representing terms in polynomial format.
            - The second element is a list of float coefficients corresponding to each term.
        """
        indices = []
        coefficients = []

        # Linear terms
        for i in range(h.shape[0]):
            if h[i, 0] != 0:
                indices.append([0, i + 1])  # 1-based index
                coefficients.append(h[i, 0])

        # Quadratic terms
        for i in range(J.shape[0]):
            for j in range(i, J.shape[1]):
                if J[i, j] != 0:
                    indices.append([i + 1, j + 1])  # 1-based indices
                    coefficients.append(J[i, j])

        return indices, coefficients

    def evaluateObjective(self, solution: np.ndarray) -> float:
        """
        Evaluate the objective function by calculating the weighted sum of selected subsets.

        Parameters
        ----------
        solution : np.ndarray
            Binary array where each element indicates if a subset is selected (1) or not (0).

        Returns
        -------
        float
            The value of the objective function, representing the total weight of selected subsets.
        """
        return float(np.squeeze(solution).T @ np.squeeze(self.linear_objective))
