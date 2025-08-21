import os
import logging
import numpy as np
import networkx as nx
from eqc_models.graph.shortestpath import ShortestPathModel
from eqc_models.graph.rcshortestpath import RCShortestPathModel
from eqc_models.solvers import Dirac3MILPDirectSolver, Dirac3MILPCloudSolver
from eqc_models.solvers.milp import MILPMixin
from eqc_models.base.results import SolutionResults
logging.basicConfig(level=logging.DEBUG)
G = nx.DiGraph()
G.add_node("s")
G.add_node("t")
G.add_node("A")
G.add_node("B")
edges = [("s", "A", 10, 8), ("s", "B", 20, 4), ("A", "B", 10, 10),
         ("A", "t", 40, 10), ("B", "t", 5, 14)]
for u, v, cost, leg_time in edges:
    G.add_edge(u, v, weight=cost, resource=leg_time)

model = ShortestPathModel(G, "s", "t")
model.penalty_multiplier = 95
# model.upper_bound = np.array([1 for x in model.variables])
# model.machine_slacks = 0
# model.is_discrete = [True for x in model.variables]
# model.is_discrete[-1] = False
print("Is Discrete:", model.is_discrete)
# lhs, rhs = model.constraints
# print(lhs)
# print(rhs)
# put a time limit of 20 on the path
rcmodel = RCShortestPathModel(G, "s", "t", 20)
rcmodel.penalty_multiplier = 95
# rcmodel.upper_bound = np.array([1 for x in model.variables])
# rcmodel.upper_bound[-1] = 10
# rcmodel.machine_slacks = 1
# lhs, rhs = rcmodel.constraints
spsum = len(model.G.edges)
rcsum = len(rcmodel.G.edges) + int(rcmodel.upper_bound[-1])
if os.environ.get("EQC_DIRECT", "NO")=="YES":
    ip_addr = os.environ.get("DEVICE_IP_ADDR", "172.18.41.171")
    port = os.environ.get("DEVICE_PORT", "50051")
    solver = Dirac3MILPDirectSolver()
    solver.connect(ip_addr=ip_addr, port=port)
    results = solver.solve(model, sum_constraint=spsum, num_samples=5, relaxation_schedule=1)
    rcresults = solver.solve(rcmodel, sum_constraint=rcsum, num_samples=5, relaxation_schedule=1)
else:
    solver = Dirac3MILPCloudSolver()
    results = solver.solve(model, sum_constraint=spsum, num_samples=5, relaxation_schedule=1)
    solutions = results.solutions
    rcresults = solver.solve(rcmodel, sum_constraint=rcsum, num_samples=5, relaxation_schedule=1)
    rcsolutions = rcresults.solutions

print("***** CHECKING ShortestPath ****")
print(model.variables)
for solution in solutions:
    print(solution)
path = model.decode(solutions[0])
print(path)
print("***** CHECKING RCShortestPath ****")
print(rcmodel.variables)
for solution in rcsolutions:
    print(solution)
rcpath = rcmodel.decode(rcsolutions[0])
print(rcpath)
