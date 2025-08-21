# (C) Quantum Computing Inc., 2024.
import unittest
from unittest import TestCase
import numpy as np
from eqc_models.ml import QBoostClassifier


class CVQBoostClassifierTestCase(TestCase):
    def setUp(self):
        """
        Create a trivial CVQBoost classification model
        """
        X = np.array(
            [
                [1.0, 2.0, 3.0],
                [1.0, 1.0, 4.0],
                [4.0, 2.0, 3.0],
                [3.0, 2.0, 3.0],
                [2.0, 2.0, 3.0],
                [2.0, 1.0, 4.0],
                [1.0, 3.0, 3.0],
                [1.0, 2.0, 4.0],
                [1.0, 0, 3.0],
                [1.0, 2.0, 0],
            ]
        )
        y = np.array(
            [1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0]
        )

        self.X = np.array(X, dtype=np.float32)
        self.y = np.array(y, dtype=np.float32)

        self.model = QBoostClassifier(
            relaxation_schedule=1,
            num_samples=1,
            lambda_coef=0,
        )

    def testHamiltonian(self):
        J, C, sum_constraint = self.model.get_hamiltonian(self.X, self.y)

        assert J.shape[0] == J.shape[0]
        assert J.shape[0] == C.shape[0]
        assert sum_constraint == 1.0


if __name__ == "__main__":
    unittest.main()
