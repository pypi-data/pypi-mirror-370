from unittest import TestCase
import numpy as np
from eqc_models.base import ConstraintModel, InequalityConstraintModel

class InequalityConstraintModelTestCase(TestCase):
    def setUp(self):
        self.model = model = InequalityConstraintModel()

        lhs = np.array([[1, 1],
                        [2, 2]])
        rhs = np.array([1, 1])
        senses = ["LE", "GE"]
        model.constraints = lhs, rhs
        model.senses = senses
        model.penalty_multiplier = 1.0

    def testConstraint(self):
        model = self.model
        A, b = model.constraints
        assert (A == np.array([[ 1.,  1.,  1.,  0.],
                               [ 2.,  2.,  0., -1.]])).all()
        assert (b == np.array([1, 1])).all()

    def testPenalty(self):
        model = self.model
        assert model.checkPenalty(np.array([1, 0, 0, 1])) == 0.0
        assert model.checkPenalty(np.array([1, 1, 0, 0])) == 10.0

class ConstraintModelTestCase(TestCase):
    def setUp(self):
        self.model = model = ConstraintModel()

        lhs = np.array([[1, 1],
                        [2, 2]])
        rhs = np.array([1, 2])
        model.constraints = lhs, rhs
        model.penalty_multiplier = 1.0

    def testConstraint(self):
        model = self.model
        A, b = model.constraints
        assert (A == np.array([[ 1.,  1.],
                               [ 2.,  2.]])).all()
        assert (b == np.array([1, 2])).all()

    def testPenalty(self):
        model = self.model
        assert model.checkPenalty(np.array([1, 0,])) == 0.0
        assert model.checkPenalty(np.array([1, 1])) == 5.0
        model.penalty_multiplier = 2
        assert model.checkPenalty(np.array([1, 1])) == 10.0
