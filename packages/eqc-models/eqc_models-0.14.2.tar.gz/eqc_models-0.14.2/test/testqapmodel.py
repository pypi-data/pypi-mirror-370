# (C) Quantum Computing Inc., 2024.
from unittest import TestCase
import numpy as np
from eqc_models.assignment import QAPModel
from eqc_models.base.operators import Polynomial, QUBO

class QAPModelTestCase(TestCase):

    def setUp(self):
        """ 
        Create a trivial model, but with numbers that make the 
        steps interesting to test 
        
        """
        A = [[0, 1],
             [1, 0]]
        B = [[0, 2],
             [1, 0]]
        C = [[1, 2],
             [3, 4]]
        self.A = np.array(A, dtype=np.float32)
        self.B = np.array(B, dtype=np.float32)
        self.C = np.array(C, dtype=np.float32)
        self.model = QAPModel(self.A, self.B, self.C)
        self.model.penalty_multiplier = 1
    
    def testConstraints(self):

        lhs, rhs = self.model.constraints
        assert (lhs == np.array([[1, 0, 1, 0],
                                 [0, 1, 0, 1],
                                 [1, 1, 0, 0],
                                 [0, 0, 1, 1]])).all()
        assert (rhs == np.array([1, 1, 1, 1])).all()

    def testHamiltonian(self):
    
        self.model.penalty_multiplier = 1
        C, J = self.model.H
        self.assertTrue((J == np.array([[3. , 1. , 1. , 1.5],
                                        [1. , 4. , 1.5, 1. ],
                                        [1. , 1.5, 5. , 1. ],
                                        [1.5, 1. , 1. , 6. ]])).all(), "Unconstrained formulation is incorrect (quadratic)")
        self.assertTrue((C == np.array([-4, -4, -4, -4])).all(), "Unconstrained formulation is incorrect (linear)")
        
    def testQUBO(self):
        """ Verify that the qubo member returns a QUBO operator object """

        self.assertTrue(isinstance(self.model.qubo, QUBO), "qubo member must be a QUBO operator object")

    def testPolynomial(self):
        """ Verify that the polynomial member returns a Polynomial operator object """

        self.assertTrue(isinstance(self.model.polynomial, Polynomial), "polynomial member must be a Polynomial operator")
