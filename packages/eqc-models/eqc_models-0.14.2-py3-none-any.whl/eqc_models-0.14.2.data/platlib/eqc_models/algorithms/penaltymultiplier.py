# (C) Quantum Computing Inc., 2024.
from typing import Union
import logging
import numpy as np
from eqc_models.base.constraints import ConstraintModel
from eqc_models.base.base import ModelSolver
from eqc_models.algorithms.base import Algorithm

log = logging.getLogger(name=__name__)

class PenaltyMultiplierAlgorithm(Algorithm):
    """
    Parameters
    ----------

    model : ConstraintModel
        Instance of a model to search out a penalty multiplier value, must be constrained model.
    solver : ModelSolver subclass
        Instance of a solver class to use to run the algorithm.


    Properties
    ----------

    upper_bound : float
        Upper bound value for the objective function, this need not be a least upper bound, 
        but the tighter the value, the more efficient the search
    solutions : List
        The solutions found during the algorithm run
    alphas : List
        The values of multiplier found at each algorithm iteration
    penalties : List
        The values for penalties found at each algorithm iteration. A penalty of 0
        indicates algorithm termination.
    penalty_threshold : float
        This value is the cutoff for penalty values that are threated as 0. Default
        is 1e-6. 
    progress_threshold : float
        This value is the cutoff for checking for progress on reducing the penalty
        value. The current penalty is compared to the average of the previous two
        and if the absolute difference is less than this value, then the algorithm
        stops, reporting progress has not been made. The default value is 1e-4.
    dynamic_range : List
        The values for the dynamic range of the unconstrained problem formulation,
        which is useful for identifying difficulty in representation of the problem
        on the analog device.

    The penalty multiplier search algorithm uses an infeasible solution to select the next 
    value for the penalty multiplier. The algorithm depends upon good solutions and only
    guarantees termination when the solution found for a given multiplier is optimal. For
    this reason, the implementation will terminate when no progress is made, thus making
    it a heuristic. Providing an exact solver for the solver instance will guarantee that 
    the algorithm is correct and the penalty mulktiplier found is the minimal multiplier
    capable of enforcing the condition that an unconstrained objective value for a feasible
    solution is less than an unconstrained objective value for an infeasible solution.

    This example uses the quadratic assignment problem and the known multiplier to test 
    the implementation of the algorithm.

    >>> from eqc_models.solvers.qciclient import Dirac3IntegerCloudSolver
    >>> from eqc_models.assignment.qap import QAPModel
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
    >>> solver = Dirac3IntegerCloudSolver() # must be configured with environment variables
    >>> algo = PenaltyMultiplierAlgorithm(model, solver)
    >>> algo.upper_bound = 330.64
    >>> algo.run(relaxation_schedule=2, num_samples=5) # doctest: +ELLIPSIS
    2... RUNNING... COMPLETED...
    >>> algo.alphas[-1] # doctest: +SKIP
    106.25
    >>> algo.penalties[-1] # doctest: +SKIP
    0.0
 
    """

    def __init__(self, model : ConstraintModel, solver : ModelSolver, penalty_threshold:float=1e-6,
                 progress_threshold : float = 1e-4):
        self.model = model
        self.solver = solver
        # ub = np.max(model.quad_objective)
        # if ub < np.max(model.linear_objective):
        #     ub = np.max(model.linear_objective)
        #     ub *= model.sum_constraint
        # else:
        #     ub *= model.sum_constraint ** 2
        self.ub = None # ub
        self.solutions = None
        self.penalties = None
        self.alphas = None
        self.dynamic_range = None
        self.responses = None
        self.penalty_threshold = penalty_threshold
        self.progress_threshold = progress_threshold

    @property
    def upper_bound(self) -> float:
        return self.ub

    @upper_bound.setter
    def upper_bound(self, value : float):
        self.ub = value

    def run(self, initial_alpha : float=None, initial_solution : np.array = None, **kwargs):
        """ Start with a guess at alpha, iterate until alpha is sufficiently large """

        self.solutions = solutions = []
        self.penalties = penalties = []
        self.alphas = alphas = []
        self.dynamic_range = dynamic_range = []
        self.responses = responses = []
        self.energies = energies = []

        model = self.model
        solver = self.solver
        offset = model.offset
        ub = self.ub
        if initial_alpha is None and offset > 0:
            alpha = ub / offset
            log.info("UPPER BOUND %f OFFSET %f  -> ALPHA %f", 
                     ub, offset, alpha)
            if alpha < 1:
                alpha = 1
        elif initial_alpha is not None:
            alpha = initial_alpha
        else:
            log.info("No tricks for initial alpha, setting to 1")
            alpha = 1

        if initial_solution is not None:
            log.debug("INITIAL SOLUTION GIVEN")
            obj_val = model.evaluate(initial_solution, alpha, True)
            penalty = model.evaluatePenalties(initial_solution) + offset
            log.info("INITIAL SOLUTION OBJECTIVE %f PENALTY %f", obj_val, penalty)
            if obj_val < ub:
                alpha += (ub - obj_val) / penalty
            log.info("INITIAL SOLUTION DETERMINED ALPHA %f", alpha)
        else:
            penalty = None
            
        while penalty is None or penalty > self.penalty_threshold:
            log.info("NEW RUN")
            log.info("SETTING MULTIPLIER %f", alpha)
            model.penalty_multiplier = float(alpha)
            log.info("GOT MULTIPLIER %f NEW OFFSET %f", model.penalty_multiplier, 
                     model.penalty_multiplier * model.offset)
            dynamic_range.append(float(model.dynamic_range))
            log.info("CALLING SOLVE WITH ALPHA %f DYNAMIC RANGE %f", alpha, dynamic_range[-1])
            alphas.append(float(alpha))
            response = solver.solve(model, **kwargs)
            responses.append(response)
            results = response["results"]
            solution = np.array(results["solutions"][0])
            solutions.append(solution)
            penalty = model.evaluatePenalties(solution) + offset
            penalties.append(float(penalty))
            obj_val = model.evaluate(solution, alpha, True)
            less_offset = model.evaluate(solution, alpha, False)
            energies.append(results["energies"][0])
            log.info("NEW SOLUTION OBJECTIVE %f LESS OFFSET %f ENERGY %f PENALTY %f", 
                     obj_val, less_offset, energies[-1], penalty)
            if penalty < self.penalty_threshold:
                pass
            elif obj_val < ub:
                alpha += (ub - obj_val) / penalty
            if penalty > self.penalty_threshold and abs(sum(penalties[-2:])/2-penalty) < self.progress_threshold:
                log.warn("SUFFICIENT PROGRESS NOT MADE FOR THREE ITERATIONS, QUITTING")
                break
