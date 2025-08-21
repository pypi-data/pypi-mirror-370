r"""
SetCoverModel solves the mathematical programming problem

$$
\mathrm{minimize}_x \sum_{x_i:X_i \in X} c_i x_i
$$

Subject to

$$
\sum_{i:a\in X_i} x_j \geq 1 \, \forall a \in A}
$$$

and 

$$
x_i \in \{0, 1\} \forall {x_i: X_i \in X}
$$

Where $S$ is a set of all elements, $X$ is a collection of sets $X_i$, and the union of all is equal to $S$. 

"""

from typing import List
import numpy as np
from eqc_models.base import ConstrainedQuadraticModel

class SetCoverModel(ConstrainedQuadraticModel):
    """
    Parameters
    -------------

    subsets : List
        List of sets where the union of all sets is S

    weights : List
        List of weights where each weight is the cost of choosing the subset
        corresponding to the index of the weight.


    >>> X = [set(['A', 'B']), set(['B', 'C']), set(['C'])]
    >>> weights = [2, 2, 1]
    >>> model = SetCoverModel(X, weights)
    >>> model.penalty_multiplier = 8
    >>> lhs, rhs = model.constraints
    >>> lhs
    array([[ 1,  0,  0,  0,  0],
           [ 1,  1,  0, -1,  0],
           [ 0,  1,  1,  0, -1]])
    >>> from eqc_models.solvers import Dirac3IntegerCloudSolver
    >>> solver = Dirac3IntegerCloudSolver()
    >>> response = solver.solve(model, relaxation_schedule=1, num_samples=5) #doctest: +ELLIPSIS
    20...
    >>> solutions = response["results"]["solutions"]
    >>> solutions[0]
    [1, 0, 1, 0, 0]
    >>> selections = model.decode(solutions[0])
    >>> assert {'B', 'A'} in selections
    >>> assert {'C'} in selections
    >>> assert len(selections) == 2

    """

    def __init__(self, subsets, weights):
        # ensure that X is ordered
        self.S = S = list(subsets)
        self.universal_set = U = set()

        for x in subsets:
            U.update(x)
        # elements is sorted to maintain consistent output
        elements = [a for a in U]
        elements.sort()
        # constraints 
        A = []
        b = []
        variables = [f'x_{i}' for i in range(len(S))]
        pos = 0
        num_slacks = 0
        slack_ub = []
        for a in elements:
            num_sets = sum([1 if a in S[i] else 0 for i in range(len(S))])
            assert num_sets >= 1, "Invalid subsets, check the universal set"
            if num_sets > 1:
                num_slacks += 1
            slack_ub.append(num_sets-1)
        for i, a in enumerate(elements):
            constraint = [1 if a in S[j] else 0 for j in range(len(S))]
            slacks = [0 for i in range(num_slacks)]
            if slack_ub[i] > 0:
                variables.append(f"s_{pos}")
                slacks[pos] = -1
                pos += 1
            A.append(constraint + slacks)
            b.append(1)
        n = len(variables)
        J = np.zeros((n, n))
        h = np.zeros((n, ))
        h[:len(weights)] = weights
        # call the superclass constructor with the objective and constraints
        super(SetCoverModel, self).__init__(h, J, np.array(A), np.array(b))
        # set upper bound on the variables to be 1 for x_i and the length of X minus 1 for the slacks
        slack_ub = [val for val in slack_ub if val > 0]
        self.upper_bound = np.array([1 for i in range(len(weights))] + slack_ub)

    def decode(self, solution) -> List:
        xbar = []
        for i in range(len(self.S)):
            if solution[i] > 0.5:
                xbar.append(self.S[i])
        return xbar
