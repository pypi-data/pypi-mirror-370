# (C) Quantum Computing Inc., 2024.
from typing import Tuple
import warnings
import numpy as np
from eqc_models.base.base import EqcModel
from eqc_models.base.constraints import ConstraintsMixIn
from eqc_models.base.operators import QUBO, Polynomial


class QuadraticMixIn:
    """
    This class provides an instance method and property that
    manage quadratic models.

    """

    @property
    def sparse(self) -> Tuple[np.ndarray, np.ndarray]:
        """ 
        Put the linear and quadratic terms in a sparse (poly) format 
        
        Returns
        ----------
        
        coefficients: List
        indices: List

        """
        C, J = self.H
        C = np.squeeze(C)
        n = self.n
        indices = []
        coefficients = []
        # build a key (ordered tuple of indices) of length 2 for each element
        for i in range(n):
            if C[i] != 0:
                key = (0, i+1)
                indices.append(key)
                coefficients.append(C[i])
        # make J upper triangular
        J = np.triu(J) + np.tril(J, -1).T
        for i in range(n):
            for j in range(i, n):
                val = J[i, j]
                if val != 0:
                    key = (i+1, j+1)
                    indices.append(key)
                    coefficients.append(val)
        
        return np.array(coefficients, dtype=np.float32), np.array(indices, dtype=np.int32)
    
    @property
    def polynomial(self) -> Polynomial:
        coefficients, indices = self.sparse
        return Polynomial(coefficients=coefficients, indices=indices)

    def evaluate(self, solution: np.ndarray) -> float:
        """ 
        Evaluate the solution using the original operator. 
         
        """

        sol = np.array(solution)
        C, J = self.H
        return np.squeeze(sol.T @ J @ sol + C.T @ sol)
    
    @property
    def dynamic_range(self) -> float:
        """
        Dynamic range is a measure in decibels of the ratio of the largest
        magnitude coefficient in a problem to the smallest non-zero magnitude
        coefficient. 

        The possible range of values are all greater than or equal to 0. The
        calculation is performed by finding the lowest non-zero of the 
        absolute value of all the coefficients, which could be empty. The
        values are in two arrays, so the minimum and maximum values of these
        arrays are compared to each other. When there is no non-zero in either
        of the arrays, then an exception is raised indicating that the dynamic
        range of an operator of all zeros is undefined. If the lowest value is 
        positive, then the maximum of the absolute values is divided by the 
        lowest. The base-10 logarithm of that value is taken and multiplied by 
        10. This is the dynamic range.

        Returns
        ----------
        
        float
        
        """
        C, J = self.H
        # if either C or J are all 0, then set min to very large value
        try:
            min_c = np.min(np.abs(C[C!=0]))
        except IndexError:
            min_c = 1e308
        try:
            min_j = np.min(np.abs(J[J!=0]))
        except IndexError:
            min_j = 1e308
        max_c = np.max(np.abs(C))
        max_j = np.max(np.abs(J))
        lowest = min_c if min_c < min_j else min_j
        highest = max_c if max_c > max_j else max_j
        if lowest > highest:
            raise ValueError("Dynamic range of a Hamiltonian of all 0 is undefined")
        return 10*np.log10(highest / lowest)

    @property
    def qubo(self) -> QUBO:
        """
        Transform the model into QUBO form. Use `upper_bound` to determine
        a log-encoding of the variables.
        
        """
        bin_n = 0
        bits = []
        # 
        C, J = self.H
        # upper_bound is an array of the maximum values each variable can take
        upper_bound = self.upper_bound
        if np.sum(upper_bound)!=upper_bound.shape[0]:
            for i in range(upper_bound.shape[0]):
                bits.append(1+np.floor(np.log2(upper_bound[i])))
                bin_n += bits[-1]
            bin_n = int(bin_n)
            Q = np.zeros((bin_n, bin_n), dtype=np.float32)
            Q.shape
            powers = [2**np.arange(bit_count) for bit_count in bits]
            blocks = []
            linear_blocks = []
            for i in range(len(powers)):
                # add the linear terms to the diagonal
                linear_blocks.append(C[i]*powers[i])
                row = []
                for j in range(len(powers)):
                    mult = J[i,j]
                    block = np.outer(powers[i], powers[j])
                    block *= mult
                    row.append(block)
                blocks.append(row)
            Q[:, :] = np.block(blocks)
            linear_operator = np.hstack(linear_blocks)
            Q += np.diag(linear_operator)
        else:
            # in this case, the fomulation already has only binary variables
            Q = np.zeros_like(J)
            Q[:, :] = J
            Q += np.diag(np.squeeze(C))

        return QUBO(Q)

class QuadraticModel(QuadraticMixIn, EqcModel):
    """
    Provides a quadratic operator and device sum constraint support.

    Parameters
    -----------

    J: Quadratic hamiltonian array.
    C: Linear hamiltonian array.

    Examples
    ---------

    >>> C = np.array([1, 2])
    >>> J = np.array([[2, 1], [1, 2]])
    >>> from eqc_models.base.quadratic import QuadraticModel    
    >>> model = QuadraticModel(C, J) 
    >>> model.upper_bound = np.array([1, 1])
    >>> qubo = model.qubo
    >>> qubo.Q # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    array([[3., 1.],
           [1., 4.]])

    """

    def __init__(self, C: np.ndarray, J: np.ndarray):
        self._H = C, J
    
class ConstrainedQuadraticModel(ConstraintsMixIn, QuadraticModel):
    """
    Provides a constrained quadratic operator and device sum constraint support.

    Parameters
    -----------

    J: Quadratic hamiltonian array.
    C: Linear hamiltonian array.
    lhs: Left hand side of the linear constraints.
    rhs: Right hand side of the linear constraints.
    
    Examples
    -------------------

    >>> C = np.array([1, 2])
    >>> J = np.array([[2, 1], [1, 2]])
    >>> lhs = np.array([[1, 1], [1, 1]])
    >>> rhs = np.array([1, 1])    
    >>> from eqc_models.base.quadratic import ConstrainedQuadraticModel    
    >>> model = ConstrainedQuadraticModel(C, J, lhs, rhs)
    >>> model.penalty_multiplier = 1
    >>> model.upper_bound = np.array([1, 1])
    >>> qubo = model.qubo
    >>> qubo.Q # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    array([[1., 3.],
           [3., 2.]])

    """

    def __init__(self, C_obj: np.array, J_obj: np.array, lhs: np.array, rhs: np.array):
        self.quad_objective = J_obj
        self.linear_objective = C_obj
        self.lhs = lhs
        self.rhs = rhs
        self._penalty_multiplier = None

    @property
    def H(self) -> Tuple[np.ndarray, np.ndarray]:
        """ 
        Return a pair of arrays, the linear and quadratic portions of a quadratic 
        operator that has the objective plus penalty functions multiplied by the 
        penalty multiplier. The linear terms are the first array and the quadratic
        are the second.
        
        Returns
        -----------
        
        `np.ndarray, np.nedarray` 
        
        """

        C = self.linear_objective
        J = self.quad_objective
        pC, pJ = self.penalties
        alpha = self.penalty_multiplier
        return C + alpha * pC, J + alpha * pJ
    
    @ConstraintsMixIn.penalty_multiplier.setter
    def penalty_multiplier(self, value):
        ConstraintsMixIn.penalty_multiplier.fset(self, value)

    @property
    def constraints(self):
        return self.lhs, self.rhs
    
    def evaluateObjective(self, solution: np.ndarray) -> float:
        J = np.array(self.quad_objective)
        C = np.array(self.linear_objective)
        return np.squeeze(C.T @ solution + solution.T@J@solution)
