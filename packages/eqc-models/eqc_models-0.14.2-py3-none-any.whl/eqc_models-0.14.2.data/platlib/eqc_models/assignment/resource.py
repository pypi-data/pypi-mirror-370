from typing import (Dict, List)
import numpy as np
from eqc_models.base.quadratic import ConstrainedQuadraticModel
from eqc_models.base.constraints import InequalitiesMixin

class ResourceAssignmentModel(InequalitiesMixin, ConstrainedQuadraticModel):
    """
    Resource assignment model

    Parameters
    ------------
    resources : List
    tasks : List
    

    >>> # name is not a required attribute of the resources or tasks
    >>> crews = [{"name": "Maintenance Crew 1", "skills": ["A", "F"], "capacity": 5, "cost": 4},
    ...          {"name": "Baggage Crew 1", "skills": ["B"], "capacity": 4, "cost": 1},
    ...          {"name": "Maintenance Crew 2", "skills": ["A", "F"], "capacity": 5, "cost": 2}]
    >>> tasks = [{"name": "Refuel", "skill_need": "F", "load": 3},
    ...          {"name": "Baggage", "skill_need": "B", "load": 1}]
    >>> model = ResourceAssignmentModel(crews, tasks)
    >>> assignments = model.createAssignmentVars()
    >>> assignments
    [{'resource': 0, 'task': 0}, {'resource': 1, 'task': 1}, {'resource': 2, 'task': 0}]
    >>> A, b, senses = model.constrainAssignments(assignments)
    >>> A
    array([[3., 0., 0.],
           [0., 1., 0.],
           [0., 0., 3.],
           [3., 0., 3.],
           [0., 3., 0.]], dtype=float32)
    >>> b
    array([5., 4., 5., 3., 3.], dtype=float32)
    >>> senses
    ['LE', 'LE', 'LE', 'EQ', 'EQ']
    >>> A, b = model.constraints
    >>> A
    array([[3., 0., 0., 1., 0., 0.],
           [0., 1., 0., 0., 1., 0.],
           [0., 0., 3., 0., 0., 1.],
           [3., 0., 3., 0., 0., 0.],
           [0., 3., 0., 0., 0., 0.]])

    """

    def __init__(self, resources, tasks):
        self.resources = resources
        self.checkTasks(tasks)
        self.tasks = tasks
        self.assignments = assignments = self.createAssignmentVars()
        n = len(assignments) + len(resources)
        self.variables = [f"a{i}" for i in range(len(assignments))]
        self.upper_bound = np.ones((n,))
        self.upper_bound[-len(resources):] = [resource["capacity"] for resource in resources]
        A, b, senses = self.constrainAssignments(assignments)
        J = np.zeros((n, n))
        C = np.zeros((n,), dtype=np.float32)
        # objective is to minimize cost of assignments
        for j, assignment in enumerate(assignments):
            C[j] = resources[assignment["resource"]]["cost"] * tasks[assignment["task"]]["load"]
        super(ResourceAssignmentModel, self).__init__(C, J, A, b)
        self.senses = senses
        # always use a machine slack
        self.machine_slacks = 1

    @classmethod
    def checkTasks(cls, tasks):
        for task in tasks:
            if "skill_need" not in task:
                raise ValueError("All tasks must have the skill_need attribute")
            if "load" not in task:
                raise ValueError("All tasks must have the load attribute")
            
    def createAssignmentVars(self):
        """ Examine all combinatins of possible crew-task assignments """

        assign_vars = []
        resources = self.resources
        tasks = self.tasks
        for i, resource in enumerate(resources):
            skills = resource["skills"]
            for j, task in enumerate(tasks):
                if task["skill_need"] in skills:
                    assign_vars.append({"resource": i, "task": j})
        return assign_vars

    def constrainAssignments(self, assignments : List) -> List:
        """ 
        Examine the assignments to determine the necessary constraints to 
        ensure feasibility of solution.

        """
        # A is sized using the number of crews and the number of assignment variables plus slacks
        m1 = len(self.resources)
        m2 = len(self.tasks)
        n1 = len(assignments)
        m = m1 + m2
        n = n1
        A = np.zeros((m, n), dtype=np.float32)
        b = np.zeros((m,), dtype=np.float32)
        for i, resource in enumerate(self.resources):
            b[i] = resource["capacity"]
            for k, assignment in enumerate(assignments):
                if assignment["resource"] == i:
                    A[i, k] = self.tasks[assignment["task"]]["load"]
        assignment_coeff = np.max(A)
        for i, task in enumerate(self.tasks):
            b[m1+i] = assignment_coeff
            for k, assignment in enumerate(assignments):
                if assignment["task"] == i:
                    A[m1+i, k] = assignment_coeff
        senses = ["LE" for resource in self.resources] + ["EQ" for task in self.tasks]
        return A, b, senses

    @property
    def sum_constraint(self) -> int:
        """ This value is a suggestion which should be used with a machine slack """

        sc = 0
        sc += sum([resource["capacity"] for resource in self.resources])
        sc += len(self.tasks)
        return sc

    def decode(self, solution : np.array) -> List[Dict]:
        """ 
        Convert the binary solution into a list of tasks 

        """

        # ensure solution is array
        solution = np.array(solution)
        resource_assignments = [[] for resource in self.resources]
        vals = [val for val in set(solution) if val <= 1.0]
        # check if there are fractional values less than 1
        if solution[~np.logical_or(solution==0, solution>=1)].size>0:
            # iterate over the values and assign tasks by largest value for tasks 
            # not assigned already            
            remaining_tasks = list(range(len(self.tasks)))
            fltr = self.upper_bound==1
            while len(remaining_tasks) > 0 and solution[fltr].shape[0]>0:
               largest = np.max(solution[fltr])
               indices, = np.where(np.logical_and(fltr, solution == largest))
               for idx in indices:
                   assignment = self.assignments[idx]
                   if assignment["task"] in remaining_tasks:
                       task = self.tasks[assignment["task"]]
                       resource_assignments[assignment["resource"]].append(task)
                       del remaining_tasks[remaining_tasks.index(assignment["task"])]
                       break
               fltr = np.logical_and(fltr, solution < largest)
        else:
            # Use the restriction that a task cannot be assigned more than once
            for j, task in enumerate(self.tasks):
                highest = 0
                best_resource = None
                for a, assignment in zip(solution, self.assignments):
                    if assignment["task"] == j:
                        if a > highest:
                            highest = a
                            best_resource = assignment["resource"]
                assert best_resource is not None, f"solution had no positive assignment values for {task}"
                resource_assignments[best_resource].append(task)

        return resource_assignments
