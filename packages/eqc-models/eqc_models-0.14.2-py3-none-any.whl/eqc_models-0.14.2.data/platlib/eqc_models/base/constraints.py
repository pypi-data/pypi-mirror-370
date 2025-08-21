# (C) Quantum Computing Inc., 2024.
"""
Four useful classes are provided in this module.

ConstraintsMixin
    Converts equality constraints to penalties. Depends on the value provided
    for penalty_multiplier.

InequalitiesMixin
    Allows inequality constraints, converting to equality constraints before
    penalties by adding slack variables.

ConstraintModel
    An example implementation of the ConstraintsMixin.

InequalityConstraintModel
    An example implementation of the InequalitiesMixin.

>>> lhs = np.array([[1, 1],
...                 [2, 2]])
>>> rhs = np.array([1, 1])
>>> senses = ["LE", "GE"]
>>> model = InequalityConstraintModel()
>>> model.constraints = lhs, rhs
>>> model.senses = senses
>>> A, b = model.constraints
>>> A
array([[ 1.,  1.,  1.,  0.],
       [ 2.,  2.,  0., -1.]])
>>> model.penalty_multiplier = 1.0
>>> model.checkPenalty(np.array([1, 0, 0, 1]))
0.0
>>> model.checkPenalty(np.array([1, 1, 0, 0]))
10.0
"""
from typing import (List, Tuple)
import numpy as np
from eqc_models.base.base import EqcModel


class ConstraintsMixIn:
    """ 
    This mixin class contains methods and attributes which transform 
    linear constraints into penalties.
    
    """
    lhs = None
    rhs = None
# alpha is the internal name for the penalty multiplier
# defaulting to 1 as a user experience enhancement
# while forcing the user to choose a value helps to
# remind of the need, it is not friendly to get a None 
# type error when an attempt to use it is made.
    alpha = 1
    linear_objective = None
    quad_objective = None

    @property
    def penalties(self) -> Tuple[np.ndarray, np.ndarray]:
        """ Returns two numpy arrays, one linear and one quadratic pieces of an operator """
        lhs, rhs = self.constraints
        if lhs is None or rhs is None:
            raise ValueError("Constraints lhs and/or rhs are undefined. " +
                             "Both must be instantiated numpy arrays.")
        Pq = lhs.T @ lhs
        Pl = -2 * rhs.T @ lhs
        return Pl.T, Pq
    
    @property
    def penalty_multiplier(self) -> float:
        return self.alpha
    
    @penalty_multiplier.setter
    def penalty_multiplier(self, value: float):
        self.alpha = value

    @property
    def constraints(self):
        return self.lhs, self.rhs
    
    @constraints.setter
    def constraints(self, value: Tuple[np.ndarray, np.ndarray]):
        self.lhs, self.rhs = value

    @staticmethod
    def _stackLHS(*args):
        """

        >>> m1 = np.array([1, 1, 1])
        >>> m2 = np.array([[2.0, 2.0]])
        >>> m3 = np.array([[0, 3, 3, 1], [1, 0, 1, 0]])
        >>> ConstraintsMixIn._stackLHS(m1, m2, m3)
        array([[1., 1., 1., 0.],
               [2., 2., 0., 0.],
               [0., 3., 3., 1.],
               [1., 0., 1., 0.]])

        """
        n = 0
        m = 0
        dtype = np.int32
        def update_dtype(matrix):
            type_rank = ["int8", "int16", "int32", "int64", "float8", "float16", "float32", "float64"]
            try:
                idx = type_rank.index(str(matrix.dtype))
            except ValueError:
                raise TypeError(f"matrix type {matrix.dtype} not supported")
        new_args = []
        for mat in args:
            if len(mat.shape) == 1:
                mat = mat.reshape((1, mat.size))
            if mat.shape[1] > n:
                n = mat.shape[1]
            m += mat.shape[0]
            dtype = update_dtype(mat)
            new_args.append(mat)
        new_lhs = np.zeros((m, n), dtype=dtype)
        idx = 0
        for mat in new_args:
            new_lhs[idx:idx+mat.shape[0],:mat.shape[1]] = mat
            idx += mat.shape[0]
        return new_lhs

    @property
    def offset(self) -> float:
        """ Calculate the offset due to the conversion of constraints to penalties """

        lhs, rhs = self.constraints

        return np.squeeze(rhs.T@rhs)

    def evaluate(self, solution : np.ndarray, alpha : float = None, includeoffset:bool=False):
        """ 
        Compute the objective value plus penalties for the given solution. Including
        the offset will ensure the penalty contribution is non-negative.

        Parameters
        ----------

        solution : np.array
            The solution vector for the problem.

        alpha : float
            Penalty multiplier, optional. This can be used to test different
            multipliers for determination of sufficiently large values.

        """
        if alpha is None:
            alpha = self.penalty_multiplier
        penalty = self.evaluatePenalties(solution)
        penalty *= alpha
        if includeoffset:
            penalty += alpha * self.offset
        return penalty + self.evaluateObjective(solution)

    def evaluatePenalties(self, solution) -> float:
        """ 
        Evaluate penalty function without alpha or offset 

        Parameters
        ----------

        solution : np.array
            The solution vector for the problem.

        """

        Pl, Pq = self.penalties
        qpart = solution.T@Pq@solution
        lpart = Pl.T@solution
        ttlpart = qpart + lpart
        return ttlpart

    def checkPenalty(self, solution : np.ndarray):
        """ 
        Get the penalty of the solution.

        Parameters
        ----------

        solution : np.array
            The solution vector for the problem.

        """

        penalty = self.evaluatePenalties(solution)
        penalty += self.penalty_multiplier * self.offset
        assert penalty >= 0, "Inconsistent model, penalty cannot be less than 0."

        return penalty
    
class InequalitiesMixin:
    """ 
    This mixin enables inequality constraints by automatically 
    generating slack variables for each inequality 
    
    This mixin adds a `senses` attribute which has a value for each
    constraint. The values are one of 'EQ', 'LE' or 'GE' for equal
    to, less than or equal to or greater than or equal to. The effect
    of the value is to control whether a slack is added and what
    the sign of the slack variable in the constraint is. Negative 
    is used for GE, positive is used for LE and all slack variables
    get a coefficient magnitude of 1.

    The constraints are modified on demand, so the class members, 
    `lhs` and `rhs` remain unmodified.

    """

    _senses = None
    @property
    def senses(self) -> List[str]:
        """ Comparison operator by constraint """

        return self._senses
    
    @senses.setter
    def senses(self, value : List[str]):
        self._senses = value

    @property
    def num_slacks(self) -> int:
        """ 
        The number of slack variables. Will match the number of inequality
        constraints. 

        Returns
        -------

        number : int

        """
        G = self.lhs
        m = G.shape[0]
        senses = self.senses
        num_slacks = sum([0 if senses[i] == "EQ" else 1 for i in range(m)])
        return num_slacks
        
    @property
    def constraints(self) -> Tuple[np.ndarray, np.ndarray]:
        """ 
        Get the general form of the constraints, add slacks where needed
        and return a standard, equality constraint form.
        
        """
        G = self.lhs
        h = self.rhs 
        senses = self.senses

        m = G.shape[0]
        n = G.shape[1]
        num_slacks = self.num_slacks
        # Adjusted dimensions for slack variables
        slack_vars = np.zeros((m, num_slacks)) 
        ii = 0
        for i in range(m):
            rule = senses[i]
            if rule == "LE":
                # Add slack variable for less than or equal constraint
                slack_vars[i, ii] = 1  
                ii += 1
            elif rule == "GE":
                # Add negated slack variable for greater than or equal constraint
                slack_vars[i, ii] = -1 
                ii += 1
        A = np.hstack((G, slack_vars)) 
        b = h

        return A, b
    
    @constraints.setter
    def constraints(self, value : Tuple[np.ndarray, np.ndarray]):
        if len(value) != 2:
            raise ValueError("Constraints must be specified as a 2-tuple")
        self.lhs, self.rhs = value

class ConstraintModel(ConstraintsMixIn, EqcModel):
    """ 
    Abstract class for representing linear constrained optimization problems as 
    EQC models. 
    
    """

class InequalityConstraintModel(InequalitiesMixin, ConstraintModel):
    """
    Abstract class for a linear constrained optimization model with inequality constraints

    """

# class MIPBinaryModel(ConstraintModel):
# 
#     binary_only_variables = None
# 
#     @property
#     def binaries(self) -> List:
#         return self.binary_only_variables
#     
#     @binaries.setter
#     def binaries(self, value : List) -> None:
#     for item in value:
#             assert int(item) == item, "Index of binary variable must be integer"
#         self.binary_only_variables = value
# 
#     @property
#     def penalties(self) -> Tuple[np.ndarray, np.ndarray]:
#         # get the explicit constraint penalties
#         Pl, Pq = super(MIPBinaryModel, self).penalties
#         if self.binary_only_variables is not None:
#             # add penalties which enforce the selection of 0 or 1 for each binar variable
# for idx in self.binaries:
#                 # add the values x(x-1)^2 -> x^3-2x^2+x
#                 indices = [[idx+1, idx+1, idx+1], [0, idx+1, idx+1], [0, 0, idx+1]]
#                 coefficients = [1, -2, 1]
#         
#         return Pl, Pq
