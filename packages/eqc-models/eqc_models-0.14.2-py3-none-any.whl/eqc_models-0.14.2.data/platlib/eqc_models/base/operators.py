"""
QUBO and Polynomial operators are used in EQC Models to pass the appropriate 
format to the solver. All models must output one or both of QUBO or Polynomial
types. Each Solver checks for the appropriate type. If a model does not provide
the type, then it must raise OperatorNotAvailableError.

>>> Q = np.array([[1, 2], [0, 1]])
>>> qubo = QUBO(Q)
>>> (qubo.Q == np.array([[1, 1], [1, 1]])).all()
True
>>> coefficients = [1, 1, 2]
>>> indices = [(1, 1), (2, 2), (1, 2)]
>>> poly = Polynomial(coefficients, indices)
>>> indices = [(1, 1), (2, 2), (2, 1)]
>>> poly = Polynomial(coefficients, indices)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: Input data to polynomial is not correct: index order must be monotonic
>>> s = np.array([1, 1])
>>> (poly.evaluate(s)==qubo.evaluate(s)).all()
True
"""
from typing import List
from dataclasses import dataclass
import numpy as np
# polyeval module is a Cython module useful for speeding up computation 
# of an operator's value at a solution. If the Cython module is not 
# available, the poly_eval variable will be set to None, triggering the
# use of a pure Python method for evaluation
try:
    from .polyeval import poly_eval
except ImportError:
    poly_eval = None

class OperatorNotAvailableError(Exception):
    """ General error to raise when an operator type is not implemented """

@dataclass
class QUBO:
    """ 
    Contains a QUBO in a symmetric matrix
    
    If the matrix Q is not symmetric already, it will be after __post_init__

    Parameters
    ----------

    qubo : np.array 
        2d symmetric matrix of values which describe a quadratic unconstrained
        binary optimization problem.
    
    """
    Q: np.ndarray

    def __post_init__(self):
        Q2 = (self.Q + self.Q.T) / 2
        self.Q = Q2

    def evaluate(self, solution : np.ndarray):
        return solution.T@self.Q@solution

@dataclass
class Polynomial:
    """
    Represents an operator and evalute the operator at a point or set of points.
    The operator must be a polynomial, possibly multivariate, with powers of up
    to 5, at the time of this version. The representation of a polynomial uses
    a sparse method with two components per term. A term is described by the 
    coefficient and a tuple of integers which indicate the variable indexes of
    the term. The coefficients can be any value which fits in 32-bit floating
    point representation, but the dynamic range of the coefficients should be 
    within the limit of the hardware's sensitivity for best results. The term
    index tuple length must be consistent across all terms. If a term does not
    have a variable index for all positions, such as with a term which is the
    square of a variable when other terms have third-order powers, then there
    must be a placeholder of 0 for the unused power. The variable indexes must
    be in the tuple in ascending order. Here are some examples (suppose the max
    degree is 4):

    - :math:`x_1^2`: :code:`(0, 0, 1, 1)`
    - :math:`x_1 x_2 x_3`: :code:`(0, 1, 2, 3)`
    - :math:`x_2^2 x_3^2`: :code:`(2, 2, 3, 3)`
    
    while it does not affect the optimiztion, a constant term can be applied to
    the polynomial by using an index of all zeros :code:`(0, 0, 0, 0)`. When 
    listing the coefficients, the position in the array must correspond to the
    position in the array of indexes. Also, the indices must be ordered with
    linear terms first, quadratic terms next and so forth. A polynomial operator
    does not have an explicit domain. It could be evaluated on an array of any
    real numbers.

    Parameters
    ----------

    coefficients : List, np.array
        Floating point values for the coefficients of a polynomial. Must
        correspond to the entries in the indices array.
    indices : List, np.array
        List of tuples or 2d np.array with integer values describing the term
        which the corresponding coefficient value is used for.

    Examples
    -------- 

    >>> coefficients = [-1, -1, 2]
    >>> indices = [(0, 1), (0, 2), (1, 2)]
    >>> polynomial = Polynomial(coefficients, indices)
    >>> test_solution = np.array([1, 1])
    >>> polynomial.evaluate(test_solution)
    [0]
    >>> test_solution = np.array([1, 0])
    >>> polynomial.evaluate(test_solution)
    [-1]
    >>> test_solution = np.array([5, -1])
    >>> polynomial.evaluate(test_solution)
    [-14]
    >>> test_solution = np.array([2.5, -2.5])
    >>> polynomial.evaluate(test_solution)
    [-12.5]

    """
    coefficients : List
    indices : List

    def __post_init__(self):
        issues = set()
        degree_count = None
        if len(self.coefficients)!=len(self.indices):
            issues.add("coefficients and indices must be the same length")
        # ensure indices are not numpy
        self.indices = [[int(val) for val in index] for index in self.indices]
        for i in range(len(self.coefficients)):
            if degree_count is None:
                degree_count = len(self.indices[i])
            elif len(self.indices[i])!=degree_count:
                issues.add("term rank is not consistent")
            for j in range(1, degree_count):
                if self.indices[i][j] < self.indices[i][j-1]:
                    issues.add("index order must be monotonic")
            try:
                coeff = float(self.coefficients[i])
            except TypeError:
                issues.add("coefficient data types must be coercible to float type")
            except ValueError:
                issues.add("coefficient values must be coercible to float values")
        if len(issues) > 0:
            msg = "Input data to polynomial is not correct: "
            msg += "; ".join([issue for issue in issues])
            raise ValueError(msg)
    
    def pure_evaluate(self, solution : np.ndarray) -> np.ndarray:
        """ 
        Evaluation in pure python 

        Parameters
        ----------

        solution : np.array
            Solution to evaluate, is optionally 2-d, which results in multiple evaluations

        Returns
        -------

        np.array

        """

        if len(solution.shape) == 1:
            solution = solution.reshape((1, solution.shape[0]))
        objective = [0 for k in range(solution.shape[0])]
        for k in range(solution.shape[0]):
            for i in range(len(self.coefficients)):
                term = self.coefficients[i]
                for j in self.indices[i]:
                    if j > 0:
                        term *= solution[k, j-1]
                objective[k] += term
        return objective
    
    def evaluate(self, solution: np.ndarray):
        """
        Evaluate the polynomial at the solution point. If the Cython module is available,
        use that for speedup, otherwise evaluate with Python loops.

        Parameters
        ----------

        solution : np.array
            Solution to evaluate. Is optinoally 2-d, which results in multiple exaluations.

        Returns 
        -------

        1-d array of values which match the coerced dtype of the inputs.

        """
        if poly_eval is None:
            return self.pure_evaluate(solution)
        else:
            return poly_eval(np.array(self.coefficients, dtype=np.float64), 
                             np.array(self.indices, dtype=np.int64), solution)
