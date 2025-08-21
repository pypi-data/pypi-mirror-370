import logging
import numpy as np
from eqc_models.base.base import EqcModel
from eqc_models.base.binaries import make_binary_penalty
from eqc_models.base.polynomial import PolynomialModel

log = logging.getLogger(name=__name__)

class MIPMixin:
    """
    Implements a solve method which intercepts the operator and builds a new
    model with added terms for restriction of discrete variables with an 
    upper bound of 1 to take on only values 0 or 1 at minima.

    Following the submission of a new model with the added penalties,
    the solutions are updated to exclude added slack variables.

    This is only supported with continuous-capable devices.

    """

    def solve(self, model : EqcModel, *args, **kwargs):
        if model.is_discrete is None:
            raise ValueError("Model solved with an MIP solver must have certain variables labeled discrete")
        elif len([b for b in model.is_discrete if b])==0:
            raise ValueError("Model solved with an MIP solver must have certain variables labeled discrete")
        if kwargs.get("sum_constraint", None) is None:
            raise ValueError("sum_constraint must be specified for MIP model sampling")
        # get a polynomial
        poly = model.polynomial
        if hasattr(poly.coefficients, "tolist"):
            coefficients = poly.coefficients.tolist()
        else:
            coefficients = list(poly.coefficients)
        indices = poly.indices
        old_n = model.n
        log.debug("Model coefficients %d", len(coefficients))
        log.debug("Model indices %d", len(indices))
        log.debug("Model size %d", old_n)
        if "penalty_multiplier" in kwargs:
            penalty_multiplier = kwargs["penalty_multiplier"]
            del kwargs["penalty_multiplier"]
        else:
            penalty_multiplier = getattr(model, "penalty_multiplier", 1)
        log.debug("Binary enforcement penalty multiplier %f", penalty_multiplier)
        bin_slacks = []
        offset = 0
        variables = model.variables
        addtl_upper_bound = []
        for i, v in enumerate(model.variables):
            if model.is_discrete[i]:
                bin_slacks.append(f"bin_slacks_{v}")
                penalty_coeff, penalty_indices, penalty_offset = make_binary_penalty(i+1, len(variables)+len(bin_slacks), penalty_multiplier=penalty_multiplier)
                log.debug("Adding penalties coeff: %s indices %s offset %s", penalty_coeff, penalty_indices, penalty_offset)
                coefficients += penalty_coeff
                indices += penalty_indices
                offset += penalty_offset
                addtl_upper_bound.append(1)
                assert len(coefficients) == len(indices)
        variables = variables + bin_slacks
        log.debug("New model binary penalty slacks: %s", bin_slacks)
        new_model = PolynomialModel(coefficients, indices)
        new_model.variables = variables
        log.debug("New model variables: %s", variables)
        new_model.upper_bound = np.array(model.upper_bound.tolist() + addtl_upper_bound)
        new_model.machine_slacks = model.machine_slacks
        coefficients, indices = new_model.H
        log.debug("New model coefficients %d", len(coefficients))
        log.debug("New model indices %d", len(indices))
        log.debug("New model size: %d", new_model.n)
        response = super().solve(new_model, *args, **kwargs)
        # translate the response into results
        results = self.makeResults(new_model, response)
        log.debug(results)
        # update the results to relect the original model
        solutions = results.solutions
        for i in range(len(solutions)):
            log.debug("SolutionResults solution: %s", solutions[i])
        if hasattr(model, "evaluateObjective"):
            new_objectives = np.zeros((len(solutions),), dtype=np.float32)
        else:
            new_objectives = None
        if hasattr(model, "evaluatePenalties"):
            new_penalties = np.zeros((len(solutions),), dtype=np.float32)
        else:
            new_penalties = None
        new_solutions = []
        new_energies = []
        num_vars = len(solutions[0]) - len(bin_slacks)
        log.debug("Num_vars %f", num_vars)
        machine_slacks = model.machine_slacks
        for i, solution in enumerate(solutions):
            log.debug("%d - Raw solution %s", i, solution)
            new_sol = [v for v in solution[:num_vars]]
            new_sol = np.array(new_sol)
            if machine_slacks > 0:
                new_sol[-machine_slacks:] = solution[-machine_slacks:]
            log.debug("%d - New solution %s", i, new_sol)
            if new_objectives is not None:
                try:
                    new_objectives[i:i+1] = model.evaluateObjective(new_sol)
                except NotImplementedError as err:
                    pass
            if new_penalties is not None:
                try:
                    new_penalties[i:i+1] = model.evaluatePenalties(new_sol)
                except NotImplementedError as err:
                    pass
            new_solutions.append(new_sol)
            new_energies.append(model.evaluate(new_sol))
        results.solutions = new_solutions
        results.penalties = new_penalties
        results.objectives = new_objectives
        results.energies = new_energies
        return results
