# (C) Quantum Computing Inc., 2024.
import numpy as np
from eqc_models.base import ConstrainedQuadraticModel

class QAPModel(ConstrainedQuadraticModel):
    """ 
    Parameters
    ----------

    A : np.array
        matrix of distances or costs between locations
    B : np.array
        matrix of flows between facilities
    C : np.array
        matrix pf fixed costs of assigning facilities to locations


    Formulates a quadratic programming model from three inputs. The inputs are composed of:
    a matrix which describes the unit cost of moving a single asset between locations. This
    matrix can describe asynchronous costs that differ by direction of flow; a matrix which
    describes the quantity of flow between facilities. This matrix describes the quantity 
    in the direction of flow; a matrix which desribes the fixed cost of assigning a facility
    to a location.

    Using these flows and costs, an optimization problem is formulated to determine a
    solution which minimizes the total cost for positioning facilities at locations. The 
    facilities do not have to be buildings or campuses and the locations do not have to be
    geographical locations. See Beckmann and and Koopmans (1957) for the original reference.

    >>> A = np.array([[0, 5, 8, 0, 1],
    ...               [0, 0, 0, 10, 15],
    ...               [0, 0, 0, 13, 18],
    ...               [0, 0, 0, 0, 0.],
    ...               [0, 0, 0, 1, 0.]])
    >>> B = np.array([[0, 8.54, 6.4, 10, 8.94],
    ...               [8.54, 0, 4.47, 5.39, 6.49],
    ...               [6.4, 4.47, 0, 3.61, 3.0],
    ...               [10, 5.39, 3.61, 0, 2.0],
    ...               [8.94, 6.49, 3.0, 2.0, 0.]])
    >>> C = np.array([[2, 3, 6, 3, 7],
    ...               [3, 9, 2, 5, 9],
    ...               [2, 6, 4, 1, 2],
    ...               [7, 5, 8, 5, 7],
    ...               [1, 9, 2, 9, 2.]])
    >>> model = QAPModel(A, B, C)
    >>> model.penalty_multiplier = 105.625
    >>> Q = model.qubo.Q
    >>> np.sum(Q)
    24318.03

    """

    def __init__(self, A : np.ndarray, B : np.ndarray, C: np.ndarray):
        
        self.A = A
        self.B = B
        self.C = C
        # N is the number of facilities (same as locations)
        # n is the number of variables (N ** 2)
        self.N = N = A.shape[0]
        self.upper_bound = np.ones((N**2,), dtype=np.int64)

        # objective 
        A = self.A
        B = self.B
        C = self.C
        n = self.N ** 2
        
        objective = np.kron(A, B) + np.diag(C.reshape((n, )))
        objective += objective.T
        objective /= 2.
        self.quad_objective = objective
        self.linear_objective = np.zeros((n,))
        # G
        m = 2 * self.N
        G = np.zeros((m, n), dtype=np.float32)
        for i in range(self.N):
            G[i, i::self.N] = 1
            G[self.N + i, i*self.N:(i+1)*self.N] = 1
        h = np.ones((m,))
        self.lhs = G
        self.rhs = h
