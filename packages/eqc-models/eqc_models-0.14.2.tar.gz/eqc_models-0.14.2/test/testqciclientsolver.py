# (C) Quantum Computing Inc., 2024.
from unittest import TestCase
import numpy as np
import os
from qci_client import QciClient
from eqc_models import QuadraticModel, PolynomialModel
from eqc_models.base.operators import OperatorNotAvailableError
from eqc_models.solvers import Dirac1CloudSolver, Dirac3CloudSolver

class Dirac1CloudSolverTestCase(TestCase):
    """ Test the file uploat, but not solving """

    def setUp(self):
        J = np.array([[0.0, -1.0],
                           [-1.0, 0.0]])
        C = np.array([[1.0], [1.0]])
        self.model = QuadraticModel(C, J)
        self.model.upper_bound = np.array([1, 1])
        self.file_id = None

    def testQUBO(self):
        pass

    def testUpload(self):
        # test for configured environment, otherwise pass without testing
        # a better approach would be to not include this test in the first place
        if os.environ.get("QCI_API_URL"):
            solver = Dirac1CloudSolver()
            client = QciClient()
            solver.uploadJobFiles(client, self.model)
        else:
            self.skipTest("Skipping test due to lack of configuration")

    def testPolynomialFail(self):
        # this must fail because qubo conversion from 3rd-order is not implemented
        indices = [(0, 0, 1),(0, 1, 2), (1, 1, 1)]
        coeff = [-1, 1, -1]
        model = PolynomialModel(coeff, indices)
        model.upper_bound = np.array([3, 3])
        solver = Dirac1CloudSolver()
        raised = True
        with self.assertRaises(ValueError) as context:
            solver.checkModel(model)
            raised = False
        assert context.exception is not None
        assert raised, "No exception raised for qubo property"

class Dirac3CloudSolverTestCase(TestCase):
    """ Test uploading polynomial file """

    def setUp(self):
        coeffs = np.array([1.0, 1.0, -2.0])
        indices = np.array([(0, 1), (0, 2), (1, 2)])
        self.model = PolynomialModel(coeffs, indices)
        self.model.upper_bound = np.array([1, 1])

    def testUpload(self):
        # test for configured environment, otherwise pass without testing
        # a better approach would be to not include this test in the first place
        if os.environ.get("QCI_API_URL"):
            solver = Dirac3CloudSolver()
            client = QciClient()
            solver.uploadJobFiles(client, self.model)
