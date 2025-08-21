import logging
from unittest import TestCase
import numpy as np
import networkx as nx
from eqc_models.graph.shortestpath import ShortestPathModel

def solution_from_sequence(sequence, variables):
    test_path = {}
    n = len(variables)
    solution = np.zeros((n,), dtype=np.float32)
    for i in range(1, len(sequence)):
        edge = (sequence[i-1], sequence[i])
        test_path[sequence[i-1]] = sequence[i]
        idx = variables.index(edge)
        solution[idx] = 1 + 0.4 * np.random.random()
    return solution, test_path

class SmallPathTestCase(TestCase):

    def setUp(self):
        self.G = G = nx.DiGraph()
        G.add_node("s")
        G.add_node("t")
        G.add_node("A")
        G.add_node("B")
        edges = [("s", "A", 10), ("s", "B", 20), ("A", "B", 10),
                 ("A", "t", 40), ("B", "t", 5)]
        for u, v, cost in edges:
            G.add_edge(u, v, weight=cost)
        self.model = model = ShortestPathModel(G, "s", "t")
        model.upper_bound = np.array([1 for x in model.variables])
        model.machine_slacks = 1
        model.penalty_multiplier = 20

    def testPenalties(self):
        G = self.G
        model = self.model
        c, j = model.penalties
        self.assertEqual(c.shape, (5,))
        self.assertEqual(j.shape, (5, 5))
        path = ('s', 'A', 't')
        solution, test_path = solution_from_sequence(path, model.variables)
        solution = np.floor(solution)
        self.assertEqual(sum(solution), 2)
        penalty = c.T@solution + solution.T@j@solution + model.offset
        self.assertAlmostEqual(penalty, 0)

    def testDecodeSolution(self):
        model = self.model
        variables = model.variables
        test_path = ['s', 'A', 'B', 't']
        solution, dict_path = solution_from_sequence(test_path, variables)
        path = model.decode(solution)
        self.assertTrue(path==test_path, f"{path} DNE {test_path}")

