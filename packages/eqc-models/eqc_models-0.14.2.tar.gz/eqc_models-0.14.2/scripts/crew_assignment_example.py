import os
import numpy as np
from eqc_models.assignment import ResourceAssignmentModel
from eqc_models.solvers.qciclient import (Dirac1CloudSolver, Dirac3ContinuousCloudSolver)
from eqc_models.base.results import SolutionResults

crews = [
         {"name": "Crew 1", "skills": ["A", "B"], "capacity": 4, "cost": 2},
         {"name": "Crew 2", "skills": ["A", "C"], "capacity": 5, "cost": 3},
         {"name": "Crew 3", "skills": ["B", "C"], "capacity": 5, "cost": 3},
         {"name": "Crew 4", "skills": ["A", "W"], "capacity": 4, "cost": 4},
         {"name": "Crew 5", "skills": ["W"], "capacity": 3, "cost": 3}
        ]
tasks = [
         {"name": "Task 1", "skill_need": "A", "load": 1},
         {"name": "Task 2", "skill_need": "B", "load": 2},
         {"name": "Task 3", "skill_need": "C", "load": 2},
         {"name": "Task 4", "skill_need": "W", "load": 2},
         {"name": "Task 5", "skill_need": "A", "load": 1},
         {"name": "Task 6", "skill_need": "B", "load": 2},
         {"name": "Task 7", "skill_need": "C", "load": 2},
         {"name": "Task 8", "skill_need": "W", "load": 2}
        ]
model = ResourceAssignmentModel(crews, tasks)
for alpha in [1, 5, 10, 20, 40]:
    model.penalty_multiplier = alpha
    print("Penalty multiplier", alpha, "dynamic range", model.dynamic_range)
print("Upper Bounds", model.upper_bound)
print("Model size", model.n)
if os.environ.get("EQC_DEVICE","DIRAC1").upper() == "DIRAC1":
    # Dirac-1 
    solver = Dirac1CloudSolver()
    response = solver.solve(model, num_samples=10)
else:
    # Dirac-3
    solver = Dirac3ContinuousCloudSolver()
    response = solver.solve(model, sum_constraint=model.sum_constraint, num_samples=15, relaxation_schedule=1)
results = SolutionResults.from_cloud_response(model, response, solver)
solution = results.solutions[0]
print("Sample device time:", results.device_time)
print("Penalty Value (positive indicates infeasible)", results.penalties[0])
print("Raw Objective Value:", results.objectives[0])
crew_assignments = model.decode(solution)
cost = 0
for i, ca in enumerate(crew_assignments):
    crew = crews[i]
    ttl_load = sum(item["load"] for item in ca)
    capacity = crew["capacity"]
    cost += sum([item["load"]*crew["cost"] for item in ca])
    print(crew["name"], "with capacity", capacity, "has load", ttl_load)
print("Computed Cost:", cost)
