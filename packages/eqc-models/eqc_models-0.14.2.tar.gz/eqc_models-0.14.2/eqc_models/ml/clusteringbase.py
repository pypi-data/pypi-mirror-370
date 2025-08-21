# (C) Quantum Computing Inc., 2024.
import sys
import numpy as np

from eqc_models import QuadraticModel
from eqc_models.solvers.qciclient import (
    Dirac1CloudSolver,
    Dirac3CloudSolver,
)
from eqc_models.solvers.eqcdirect import Dirac3DirectSolver

class ClusteringBase(QuadraticModel):
    """
    A base class for clustering algorithms
    """

    def __init__(
        self,
        relaxation_schedule=2,
        num_samples=1,
        device="dirac-3",
        solver_access="cloud",
        ip_addr=None,
        port=None,            
    ):
        super(self).__init__(None, None, None)

        assert device in ["dirac-1", "dirac-3"]

        assert solver_access in ["cloud", "direct"]

        if device == "dirac-1" and solver_access == "direct":
            print("Dirac-1 is only available on cloud")
            solver_access = "cloud"
        
        self.relaxation_schedule = relaxation_schedule
        self.num_samples = num_samples
        self.device = device
        self.solver_access = solver_access
        self.ip_addr = ip_addr
        self.port = port

    def fit(self, X: np.array):
        pass

    def predict(self, X: np.array):
        pass

    def get_hamiltonian(
        self,
        X: np.array,
    ):
        pass

    def set_model(self, J, C, sum_constraint):
        # Set hamiltonians
        self._C = C
        self._J = J
        self._H = C, J
        self._sum_constraint = sum_constraint
        num_variables = C.shape[0]

        if self.device == "dirac-1":
            self.upper_bound = np.ones((num_variables,))
        elif self.device == "dirac-3":
            self.upper_bound = sum_constraint * np.ones((num_variables,))

        return

    def solve(self):
        if self.device == "dirac-1":
            solver = Dirac1CloudSolver()
            response = solver.solve(
                self,
                num_samples=self.num_samples,
            )
        elif self.device == "dirac-3":
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

        return sol, response

    def get_labels(self, sol):
        pass

    def get_energy(self, sol: np.array):
        C = self._C
        J = self._J

        return sol.transpose() @ J @ sol + sol.transpose @ C

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
