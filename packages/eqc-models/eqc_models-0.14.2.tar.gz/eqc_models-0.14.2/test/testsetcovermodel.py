from unittest import TestCase
from eqc_models.combinatorics.setcover import SetCoverModel

class SetCoverTestCase(TestCase):
    """ 
    Elements of the super set are sorted within SetCoverModel to ensure 
    consistent output, so tests assume element based output is alphabetical 

    """

    def setUp(self):
        self.X = [{'A', 'B'}, {'B', 'C'}, {'C'}]
        self.weights = [2, 2, 1]
        self.model = SetCoverModel(self.X, self.weights)

    def testConstraints(self):
        lhs, rhs = self.model.constraints
        assert lhs.shape == (3, 5)
        assert rhs.shape == (3,)
        assert (lhs == [[1, 0, 0, 0, 0],[1, 1, 0, -1, 0],[0, 1, 1, 0, -1]]).all()
        assert (rhs == [1, 1, 1]).all()

    def testObjective(self):
        objective = self.model.linear_objective
        assert (objective == [2, 2, 1, 0, 0]).all()
