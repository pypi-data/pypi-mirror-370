# (C) Quantum Computing Inc., 2025.
import logging
from typing import Dict

try:
    from eqc_direct.client import EqcClient
except ModuleNotFoundError:
    # Only warn here to try to disrupt package behavior as least as possible.
    logging.warning("eqc-direct package not available")

    class EqcClient:
        """This is a stub for unsupported EqcClient."""

        def __init__(*_, **__) -> None:
            """Raise exception when client cannot be created."""
            raise ModuleNotFoundError(
                "eqc-direct package not available, likely because Python version is 3.11+"
            )

from eqc_models.base.base import EqcModel, ModelSolver
from eqc_models.base.results import SolutionResults

log = logging.getLogger(name=__name__)


class Dirac3DirectSolver(ModelSolver):
    ip_addr: str = "localhost"
    port: str = "50051"
    cert_file: str = None

    def solve(
        self,
        model,
        sum_constraint,
        relaxation_schedule=1,
        num_samples=1,
        mean_photon_number=None,
        quantum_fluctuation_coefficient=None,
    ):
        polynomial = model.polynomial
        coefficients = polynomial.coefficients
        indices = polynomial.indices
        num_variables = 0
        for i in range(len(indices)):
            if max(indices[i]) > num_variables:
                num_variables = max(indices[i])
        # add machine slacks
        num_variables += model.machine_slacks
        print("Num variables:", num_variables)

        client = self.client
        lock_id, startts, endts = client.wait_for_lock()

        # assert lock["status_code"] == 0

        # lock_id = lock["lock_id"]
        response = None
        try:
            response = client.solve_sum_constrained(
                coefficients,
                indices,
                num_variables,
                num_samples=num_samples,
                lock_id=lock_id,
                relaxation_schedule=relaxation_schedule,
                sum_constraint=sum_constraint,
                mean_photon_number=mean_photon_number,
                quantum_fluctuation_coefficient=quantum_fluctuation_coefficient,
            )
        finally:
            client.release_lock(lock_id=lock_id)

        return response

    def connect(self, ip_addr: str, port: str, cert_file: str = None):
        self.ip_addr = ip_addr
        self.port = port
        self.cert_file = cert_file
        client = self.client

        return client.system_status()

    @property
    def client(self) -> EqcClient:
        """Return a new client from eqc-direct based on class config."""

        return EqcClient(self.ip_addr, self.port, cert_file=self.cert_file)

    def makeResults(self, model : EqcModel, response : Dict):
        """ Builds the results object """

        return SolutionResults.from_eqcdirect_response(model, response, self)
