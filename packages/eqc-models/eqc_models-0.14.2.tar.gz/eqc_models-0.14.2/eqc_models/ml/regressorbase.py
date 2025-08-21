# (C) Quantum Computing Inc., 2024.
# Import libs
import os
import sys
import time
import datetime
import json
import warnings
from functools import wraps
import numpy as np

from eqc_models import QuadraticModel
from eqc_models.solvers.qciclient import Dirac3CloudSolver
from eqc_models.solvers.eqcdirect import Dirac3DirectSolver

class RegressorBase(QuadraticModel):
    def __init__(
        self,
        relaxation_schedule=2,
        num_samples=1,
        solver_access="cloud",
        ip_addr=None,
        port=None,            
    ):

        super(self).__init__(None, None, None)

        assert solver_access in ["cloud", "direct"]
        
        self.relaxation_schedule = relaxation_schedule
        self.num_samples = num_samples
        self.solver_access = solver_access
        self.ip_addr = ip_addr
        self.port = port        
        self.params = None

    def predict(self, X: np.array):
        pass

    def get_hamiltonian(
        self,
        X: np.array,
        y: np.array,
    ):
        pass

    def set_model(self, J, C, sum_constraint):
        
        # Set hamiltonians
        self._C = C
        self._J = J
        self._H = C, J
        self._sum_constraint = sum_constraint

        # Set domains
        num_variables = C.shape[0]
        self.domains = sum_constraint * np.ones((num_variables,))
        
        return

    def solve(self):
        if self.solver_access == "direct":
            solver = Dirac3DirectSolver()
            solver.connect(self.ip_addr, self.port)
        else:
            solver = Dirac3CloudSolver()
            
        response = solver.solve(
            self,
            sum_constraint=self._sum_constraint,
            relaxation_schedule=self.relaxation_schedule,
            num_samples=self.num_samples,
        )

        if self.solver_access == "cloud":
            energies = response["results"]["energies"]
            solutions = response["results"]["solutions"]
        elif self.solver_access == "direct":
            energies = response["energy"]
            solutions = response["solution"]
            
        min_id = np.argmin(energies)
        sol = solutions[min_id]

        print(response)
        
        return sol

    def convert_sol_to_params(self, sol):
        pass

    def fit(self, X, y):
        return self
    
    def get_dynamic_range(self):
        C = self._C
        J = self._J

        if C is None:
            return

        if J is None:
            return

        absc = np.abs(C)
        absj = np.abs(J)
        minc = np.min(absc[absc > 0])
        maxc = np.max(absc)
        minj = np.min(absj[absj > 0])
        maxj = np.max(absj)

        minval = min(minc, minj)
        maxval = max(maxc, maxj)

        return 10 * np.log10(maxval / minval)
