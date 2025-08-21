# (C) Quantum Computing Inc., 2024.
from unittest import TestCase
import numpy as np
import networkx as nx
from eqc_models.graph import MaxCutModel
from eqc_models.base.operators import Polynomial, QUBO

class MaxCutTestCase(TestCase):

    def setUp(self):
        self.G = G = nx.Graph()
        adjacency = [[0, 1, 1, 0, 1, 0],
                     [1, 0, 0, 1, 0, 1],
                     [1, 0, 0, 1, 0, 0],
                     [0, 1, 1, 0, 1, 1],
                     [1, 0, 0, 1, 0, 1],
                     [0, 1, 0, 1, 1, 0]]
        self.adjacency = np.array(adjacency)
        G.add_edges_from(zip(*np.where(self.adjacency==1)))
        self.model = MaxCutModel(G)

    def testQUBO(self):
        """ Verify that the qubo member returns a QUBO operator object """

        self.assertTrue(isinstance(self.model.qubo, QUBO), "qubo member must be a QUBO operator object")

    def testPolynomial(self):
        """ Verify that the polynomial member returns a Polynomial operator object """

        self.assertTrue(isinstance(self.model.polynomial, Polynomial), "polynomial member must be a Polynomial operator")

    def testQUBO(self):
        """ Verify that the qubo member returns a QUBO operator object """

        self.assertTrue(isinstance(self.model.qubo, QUBO), "qubo member must be a QUBO operator object")

    def testPolynomial(self):
        """ Verify that the polynomial member returns a Polynomial operator object """

        self.assertTrue(isinstance(self.model.polynomial, Polynomial), "polynomial member must be a Polynomial operator")

    def testEdges(self):
        assert len(self.G.edges) == 9
        edges = list(self.G.edges)
        edges = [list(pair) for pair in edges]
        for i in range(len(edges)):
            edges[i].sort()
        edges.sort()
        edges = [tuple(pair) for pair in edges]
        assert edges == [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), 
                         (2, 3), (3, 4), (3, 5), (4, 5)]

    def testH(self):
        # since the EQCModel does not have the
        # convenience of combining the quadratic and linear terms
        # for the same variable, it returns the parts separate
        C, J = self.model.H
        # here is the QUBO form of the max cut problem
        qubo = [[-3, 1, 1, 0, 1, 0],
                [1, -3, 0, 1, 0, 1],
                [1, 0, -2, 1, 0, 0],
                [0, 1, 1, -4, 1, 1],
                [1, 0, 0, 1, -3, 1],
                [0, 1, 0, 1, 1, -3]]
        # separate the max cur problem into linear and quadratic portions
        qubo = np.array(qubo)
        testh = np.diag(qubo)
        testJ = 1*qubo
        testJ[np.arange(6), np.arange(6)] = 0
        assert (J == testJ).all()
        assert (np.squeeze(C) == testh.T).all()