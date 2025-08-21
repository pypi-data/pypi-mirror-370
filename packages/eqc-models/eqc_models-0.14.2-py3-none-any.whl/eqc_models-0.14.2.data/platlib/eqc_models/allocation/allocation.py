# (C) Quantum Computing Inc., 2024.
from typing import List, Tuple
from enum import Enum
import numpy as np
from eqc_models.base.constraints import InequalitiesMixin
from eqc_models.base.quadratic import ConstrainedQuadraticModel


class AllocationModel(ConstrainedQuadraticModel):
    """
    Parameters
    ----------

    resources: List 
        names of available resources.
    tasks: List
        names of tasks.
    resource_usage: List of Lists or 2D np.ndarray 
        rows represent tasks and columns represent resources,
        specifying the amount of each resource required per task.
    resource_limits: 1D array or List
        specifying the limit on each resource.
    cost_per_task: 1D array List
        specifying the cost per task (or benefit with negative of value).


    Attributes
    ----------

    penalty_multiplier: float
        value for weighting the penalties formed from the equality constraints

    qubo: eqc_models.base.operators.QUBO
        QUBO operator representation

    polynomial: eqc_models.base.operators.Polynomial
        Polynomial operator representation


    This class represents a resource allocation model for maximizing total benefit. In other words,
    Given a list of resources and a list of tasks, allocate the resources among the tasks so as to 
    maximize the economic benefit.

    Here's an example. Five tasks must share 4 resources. Each task can use a different amount of
    each resource. 

    +--------------------+------+------+---------+---------+---------+
    |                    | Spam | Eggs | Coconut | Sparrow | Benefit |
    +--------------------+------+------+---------+---------+---------+
    | Breakfast          | 1    | 2    | 0       | 0       | 3       | 
    +--------------------+------+------+---------+---------+---------+
    | Countryside Stroll | 0    | 0    | 1       | 0       | 1       |
    +--------------------+------+------+---------+---------+---------+
    | Storm Castle       | 0    | 12   | 1       | 1       | 10      | 
    +--------------------+------+------+---------+---------+---------+
    | Availability       | 1    | 12   | 2       | 1       |         |
    +--------------------+------+------+---------+---------+---------+

    >>> resources = ["Spam", "Eggs", "Coconut", "Sparrow"]
    >>> tasks = ["Breakfast", "Countryside Stroll", "Storm Castle"]
    >>> resource_usage = [[1, 2, 0, 0], [0, 0, 1, 0], [0, 12, 1, 1]]
    >>> resource_limits = [1, 12, 2, 1]
    >>> cost_per_task = [-3, -1, -10.] 
    >>> allocation_model = AllocationModel(resources, tasks, resource_usage, resource_limits, cost_per_task)
    >>> allocation_model.penalty_multiplier = 1
    >>> C, J = allocation_model.H 
    >>> C # -3 -2 * (12 * 2 + 1 * 1), -1 -2 * 2*1, -10 -2 * (12 * 12 + 1 * 2 + 1 * 1) 
    ...   # doctest: +NORMALIZE_WHITESPACE
    array([ -53., -5.,     -304.])
    >>> J # doctest: +NORMALIZE_WHITESPACE
    array([[ 5., 0., 24.],
           [ 0., 1.,  1.],
           [ 24., 1., 146.]])

    """

    def __init__(self, resources: List, tasks: List, resource_usage: List, resource_limits: List,
                 cost_per_task: List):
        if not isinstance(resources, list):
            raise TypeError("Argument 'resources' must be a list")
        if not isinstance(tasks, list):
            raise TypeError("Argument 'tasks' must be a list")
        if not isinstance(resource_usage, list):
            raise TypeError("Argument 'resource_usage' must be a list")
        if not isinstance(resource_limits, list):
            raise TypeError("Argument 'resource_limits' must be a list")
        if not isinstance(cost_per_task, list):
            raise TypeError("Argument 'cost_per_task' must be a list")
        # PARENT CLASS MUST HAVE TYPE CHECK
        self.resources = resources
        self.tasks = tasks
        self.resource_usage = np.array(resource_usage)
        self.resource_limits = np.array(resource_limits)
        self.cost_per_task = np.array(cost_per_task)
        super(AllocationModel, self).__init__(self.cost_per_task, np.zeros((len(self.tasks), len(self.tasks))), self.resource_usage.T, self.resource_limits)
        # self.domains = np.array([np.floor(max(self.resource_limits[self.resource_limits != 0]) /
        #                          min(self.resource_usage[self.resource_usage != 0]))] * len(self.tasks), dtype=int)
        # self.upper_bound = [np.floor(max(self.resource_limits[self.resource_limits != 0]) /
        #                          min(self.resource_usage[self.resource_usage != 0]))] * len(self.tasks)
        self._validate_dimensions()
        ### NEED TO MAKE SURE BASE CLASS VALIDATES self.upper_bound ###

    @property
    def upper_bound(self) -> np.array:
        return np.array([np.floor(max(self.resource_limits[self.resource_limits != 0]) /
                                  min(self.resource_usage[self.resource_usage != 0]))] * len(self.tasks), dtype=int)

    @upper_bound.setter
    def upper_bound(self, value: List):
        self._upper_bound = value

    @property
    def variables(self):
        return [(i, j) for i in self.tasks for j in self.resources]

    def _validate_dimensions(self):
        """Raises ValueErrors for inconsistent dimensions."""

        # Check resource_usage dimensions
        num_tasks = len(self.tasks)
        num_resources = len(self.resources)
        # print("RESOURCES", num_resources)
        # print("TASKS", num_tasks)
        # print(self.resource_usage.shape)
        if self.resource_usage.shape != (num_tasks, num_resources):
            raise ValueError("resource_usage matrix dimensions don't match number of tasks and resources")

        # Check resource_limits length
        if self.resource_limits.shape[0] != num_resources:
            raise ValueError("resource_limits length doesn't match number of resources")

        # Check cost_per_task length
        if self.cost_per_task.shape[0] != num_tasks:
            raise ValueError("cost_per_task length doesn't match number of tasks")

    def add_task(self, task: str, task_resource_usage: List, task_cost: float):
        """ 
        task: str
            Name of task to add
        task_resource_usage: List
            Quantity of resource used for task for all tasks
        task_cost: float
            Quantity indicating the cost or benefit (negative) of the task
        
        Add a task to the problem, modifying the resource usage and task cost arrays.

        """
        self.tasks += [task]
        self.resource_usage = np.vstack([self.resource_usage, task_resource_usage])
        self.cost_per_task = np.append(self.cost_per_task, task_cost)

    @property
    def H(self) -> Tuple[np.ndarray,np.ndarray]:
        """ Return linear, quadratic portions of the (quadratic) Hamiltonian """
        Pl, Pq = self.penalties
        alpha = self.penalty_multiplier
        obj_linear, obj_quad = self.linear_objective, self.quad_objective #self._linear_objective(), self._quadratic_objective()
        self._C = obj_linear + alpha * Pl
        self._J = obj_quad + alpha * Pq

        return obj_linear + alpha * Pl, obj_quad + alpha * Pq


class ResourceRuleEnum(Enum):
    """ 
    Enumeration of the allowed resource rules, mapping to the mathematical expression:

    MAXIMUM -> LE (less than or equal to)
    MINIMUM -> GE (greater than or equal to)
    EXACT -> EQ (equal to)

    """
    MAXIMUM = "LE"
    MINIMUM = "GE"
    EXACT = "EQ"

class AllocationModelX(InequalitiesMixin, AllocationModel):
    """ 
    Parameters
    ----------

    resources: List 
        names of available resources.
    tasks: List
        names of tasks.
    resource_usage: List of Lists or 2D np.ndarray 
        rows represent tasks and columns represent resources,
        specifying the amount of each resource required per task.
    resource_limits: 1D array or List
        specifying the limit on each resource.
    resource_rule: List
        ResourceRuleEnum values for each resource
    cost_per_task: 1D array List
        specifying the cost per task (or benefit with negative of value).


    Attributes
    ----------

    penalty_multiplier: float
        value for weighting the penalties formed from the equality constraints

    qubo: eqc_models.base.operators.QUBO
        QUBO oeprator representation

    polynomial: eqc_models.base.operators.Polynomial
        Polynomial operator representation

    variables: List
        names of variables formed from tasks and assignments


    This class represents a resource allocation model for maximizing total benefit. In other words,
    Given a list of resources and a list of tasks, allocate the resources among the tasks so as to 
    maximize the economic benefit.

    Adds resource_rule as an argument. This must be a list of strings specifying
    constraints for each resource (LE, GE, or EQ).

    Here's an example. Five tasks must share 4 resources. Each task can use a different amount of
    each resource. 

    +--------------------+------+------+---------+---------+---------+
    |                    | Spam | Eggs | Coconut | Sparrow | Benefit |
    +--------------------+------+------+---------+---------+---------+
    | Breakfast          | 1    | 2    | 0       | 0       | 3       | 
    +--------------------+------+------+---------+---------+---------+
    | Countryside Stroll | 0    | 0    | 1       | 0       | 1       |
    +--------------------+------+------+---------+---------+---------+
    | Storm Castle       | 0    | 12   | 1       | 1       | 10      | 
    +--------------------+------+------+---------+---------+---------+
    | Availability       | 1    | 12   | 2       | 1       |         |
    +--------------------+------+------+---------+---------+---------+

    >>> resources = ["Spam", "Eggs", "Coconut", "Sparrow"]
    >>> tasks = ["Breakfast", "Countryside Stroll", "Storm Castle"]
    >>> resource_usage = [[1, 2, 0, 0], [0, 0, 1, 0], [0, 12, 1, 1]]
    >>> resource_limits = [1, 12, 2, 1]
    >>> cost_per_task = [-3, -1, -10.] 
    >>> resource_rules = [ResourceRuleEnum.MAXIMUM for i in range(len(resources))]
    >>> allocation_model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rules, cost_per_task)
    >>> allocation_model.penalty_multiplier = 1
    >>> C, J = allocation_model.H 
    >>> C # -3 -2 * (12 * 2 + 1 * 1), -1 -2 * 2*1, -10 -2 * (12 * 12 + 1 * 2 + 1 * 1) 
    ...   # doctest: +NORMALIZE_WHITESPACE
    array([ -53., -5., -304., -2., -24., -4., -2.])
    >>> J # doctest: +NORMALIZE_WHITESPACE
    array([[  5.,  0.,  24., 1.,  2., 0., 0.],
           [  0.,  1.,   1., 0.,  0., 1., 0.],
           [ 24.,  1., 146., 0., 12., 1., 1.],
           [  1.,  0.,   0., 1.,  0., 0., 0.], 
           [  2.,  0.,  12., 0.,  1., 0., 0.], 
           [  0.,  1.,   1., 0.,  0., 1., 0.],
           [  0.,  0.,   1., 0.,  0., 0., 1.]])
    """
    def __init__(self, resources: List, tasks: List, resource_usage: List, resource_limits: List,
                 resource_rule: List[ResourceRuleEnum], cost_per_task: List):
        super().__init__(resources, tasks, resource_usage, resource_limits, cost_per_task)

        if not isinstance(resource_rule, list):
            raise TypeError("Argument 'resource_rule' must be a list")
        elif len(resource_rule) != len(resources):
            raise ValueError("Argument 'resource_rule' must be the same length as 'resources'")

        try:
            check_rule = set([rule.value for rule in resource_rule])
            if not check_rule.issubset({"LE", "GE", "EQ"}):
                raise ValueError("Argument 'resource_rule' must contain only enums 'ResourceRuleEnum.MAXIMUM', "
                                 "'ResourceRuleEnum.MINIMUM' or 'ResourceRuleEnum.EXACT'.")
        except AttributeError as e:
            # Handle the case where elements in resource_rule don't have a 'value' attribute (likely not enums)
            raise TypeError("Argument 'resource_rule' must contain only enums. Elements lack a 'value' "
                            "attribute.") from e

        self.senses = list([rule.value for rule in resource_rule])

    @property
    def upper_bound(self) -> np.array:
        return np.array([np.floor(max(self.resource_limits[self.resource_limits != 0]) /
                                  min(self.resource_usage[self.resource_usage != 0]))] * self.n, dtype=int)

    @upper_bound.setter
    def upper_bound(self, value: List):
        self._upper_bound = value

    @property
    def linear_objective(self) -> np.ndarray:
        """
        Returns a 1D numpy array representing the linear part of the objective function (total profit).
        """
        return np.hstack([self.cost_per_task, np.zeros(self.num_slacks)])

    @linear_objective.setter
    def linear_objective(self, value : np.ndarray):
        
        assert (value[len(self.cost_per_task):]==0).all(), "additional values beyond cost length must be 0"

        self.cost_per_task[:] = value[:len(self.cost_per_task)]

    @property
    def quad_objective(self) -> np.ndarray:
        """
        Returns a 2D numpy array representing the quadratic part of the objective function (always zero in this case).
        """
        # No quadratic term
        n = self.n
        return np.zeros((n, n))

    @quad_objective.setter
    def quad_objective(self, value: np.ndarray):
        """ Don't let anything be passed in except arrays of all 0 """

        # the setting of this gets ignored, but speak if somebody brings a soul
        # that hasn't passed yet (all must be 0)

        assert (value==0).all(), "quadratic terms in objective must be 0"
        
    @property
    def H(self):
        """
        Overrides the parent build method to incorporate slack variables based on resource_rule.
        """
        # Build constraint penalties with slack variables
        Pl, Pq = self.penalties
        alpha = self.penalty_multiplier
        obj_linear, obj_quad = self.linear_objective, self.quad_objective

        self._C = obj_linear + alpha * Pl
        self._J = obj_quad + alpha * Pq

        return obj_linear + alpha * Pl, obj_quad + alpha * Pq

    def checkResources(self, solution):
        """
        Parameters
        ----------
        solution: List or np.ndarray
            solution vector to check for resource violations

        Returns
        -------
        List of violations: (name, rule, violation quantity, message)

        """
        violations = []
        solution = np.array(solution)
        for name, usage, rule, limit in zip(self.resources, self.resource_usage.T,
                                            self.senses, self.resource_limits):
            decision_vars = self.n - self.num_slacks
            value = np.squeeze(usage@solution[:decision_vars])
            if rule == ResourceRuleEnum.MINIMUM:
                mult = -1
            else:
                mult = 1
            if rule == ResourceRuleEnum.EXACT:
                if value - limit != 0:
                    msg = f"{value} of {name} violates {rule} {limit}"
                    violations.append((name, rule, value - limit, msg))
            else:
                if mult * (value - limit) > 0:
                    msg = f"{value} of {name} violates {rule} {limit}"
                    violations.append((name, rule, (value - limit), msg))
        return violations
    
    @property
    def n(self):
        return len(self.tasks) + self.num_slacks
