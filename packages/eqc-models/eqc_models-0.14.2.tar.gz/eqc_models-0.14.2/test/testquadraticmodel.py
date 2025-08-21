# (C) Quantum Computing Inc., 2024.
from unittest import TestCase
import numpy as np
from eqc_models import QuadraticModel

class QuadraticModelSimpleTestCase(TestCase):

    def setUp(self):
        C = np.array([-1, 0]).reshape((2, 1))
        J = np.array([[0, 1],
                      [1, 0]], dtype=np.float32)
        self.model = QuadraticModel(C, J)
        self.model.upper_bound = 10*np.ones((2,))
        
    def testCoefficients(self):
        coefficients, indices = self.model.sparse
        self.assertTrue((coefficients==np.array([-1, 2])).all(), "Incorrect coefficients in sparse format")

    def testIndices(self):
        coefficients, indices = self.model.sparse
        self.assertTrue((indices==np.array([[0, 1], [1, 2]])).all(), f"Incorrect indices in sparse format: {indices.tolist()}")

    def testDyanmicRange(self):
        C, J = self.model.H
        C *= 10
        model = QuadraticModel(C, J)
        model.upper_bound = 1*self.model.upper_bound 
        dynamic_range = self.model.dynamic_range
        self.assertEqual(dynamic_range, 10)
