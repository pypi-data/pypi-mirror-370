# (C) Quantum Computing Inc., 2024.
from unittest import TestCase
import numpy as np
from enum import Enum
from eqc_models import AllocationModel, AllocationModelX, ResourceRuleEnum


class AllocationModelTestCase(TestCase):

    def test_init(self):
        """
        Tests initialization of AllocationModel with valid data.
        """
        resources = ["Material", "Labor", "Time"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2, 3], [2, 1, 4]]
        resource_limits = [10, 8, 12]
        cost_per_task = [5, 10]
        

        model = AllocationModel(resources, tasks, resource_usage, resource_limits,
                                cost_per_task)
        model.penalty_multiplier = 1

        self.assertEqual(model.resources, resources)
        self.assertEqual(model.tasks, tasks)
        self.assertTrue(np.array_equal(model.resource_usage, np.array(resource_usage)))
        self.assertTrue(np.array_equal(model.resource_limits, np.array(resource_limits)))
        self.assertTrue(np.array_equal(model.cost_per_task, np.array(cost_per_task)))

    def test_init_invalid_data(self):
        """
        Tests initialization with invalid data types or mismatched shapes.
        """
        resources = ["Material", "Labor", "Time"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2, 3], [2, 1, 4]]
        resource_limits = [10, 8, 12]
        cost_per_task = [5, 10]
        

        # Invalid resource data types
        with self.assertRaises(TypeError):
            AllocationModel("resources", tasks, resource_usage, resource_limits,
                            cost_per_task)

        # Mismatched resource_usage and resource_limits shapes
        invalid_resource_usage = [[1, 2]]
        with self.assertRaises(ValueError):
            AllocationModel(resources, tasks, invalid_resource_usage, resource_limits,
                            cost_per_task)

    def test_linear_objective(self):
        """
        Tests if _linear_objective returns the correct linear part of the objective function (profit).
        """
        resources = ["Material", "Labor"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2], [2, 1]]
        resource_limits = [10, 8]
        cost_per_task = [5, 10]
        

        model = AllocationModel(resources, tasks, resource_usage, resource_limits,
                                cost_per_task)
        model.penalty_multiplier = 1
        expected_objective = np.array(cost_per_task)
        actual_objective = model.linear_objective

        self.assertTrue(np.array_equal(expected_objective, actual_objective))

    def test_quadratic_objective(self):
        """
        Tests if _quadratic_objective returns a zero 2D array (no quadratic term).
        """
        resources = ["Material", "Labor"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2], [2, 1]]
        resource_limits = [10, 8]
        cost_per_task = [5, 10]
        

        model = AllocationModel(resources, tasks, resource_usage, resource_limits,
                                cost_per_task)
        model.penalty_multiplier = 1

        expected_objective = np.zeros((len(model.tasks), len(model.tasks)))
        actual_objective = model.quad_objective

        self.assertTrue(np.array_equal(expected_objective, actual_objective))

    def test_constraints(self):
        """
        Tests if constraints property returns the correct constraint matrix and right-hand side.
        """
        resources = ["Material", "Labor", "Time"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2, 3], [2, 1, 4]]
        resource_limits = [10, 8, 12]
        cost_per_task = [5, 10]
        

        model = AllocationModel(resources, tasks, resource_usage, resource_limits,
                                cost_per_task)
        model.penalty_multiplier = 1

        expected_constraint_matrix = np.array(resource_usage).T
        expected_right_hand_side = np.array(resource_limits)

        actual_constraint_matrix, actual_right_hand_side = model.constraints

        self.assertTrue(np.array_equal(expected_constraint_matrix, actual_constraint_matrix))
        self.assertTrue(np.array_equal(expected_right_hand_side, actual_right_hand_side))

    def test_add_task(self):
        """
        Tests if add_task successfully adds a new task to the model's internal data structures.
        """
        resources = ["Material", "Labor"]
        tasks = ["Task A"]
        resource_usage = [[1, 2]]
        resource_limits = [10, 8]
        cost_per_task = [5]
        

        model = AllocationModel(resources, tasks, resource_usage, resource_limits,
                                cost_per_task)
        model.penalty_multiplier = 1 

        new_task_name = "Task B"
        new_task_usage = [3, 1]
        new_task_profit = 7

        model.add_task(new_task_name, new_task_usage, new_task_profit)

        # Expected updates to internal data structures
        expected_resource_usage = np.vstack([resource_usage, new_task_usage])
        expected_cost_per_task = np.append(cost_per_task, new_task_profit)

        self.assertEqual(model.tasks, tasks)
        self.assertTrue(np.array_equal(model.resource_usage, np.array(expected_resource_usage)))
        self.assertTrue(np.array_equal(model.cost_per_task, np.array(expected_cost_per_task)))

    def test_H(self):
        """
        Tests if build of H returns the linear and quadratic objective portions
        """
        resources = ["Material", "Labor", "Time"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2, 3], [2, 1, 4]]
        resource_limits = [10, 8, 12]
        cost_per_task = [5, 10]
        

        model = AllocationModel(resources, tasks, resource_usage, resource_limits,
                                cost_per_task)
        model.penalty_multiplier = 1

        # Pre-calculated penalty terms
        linear_penalty, quadratic_penalty = model.penalties
        penalty_multiplier = model.penalty_multiplier

        expected_linear_objective = model.linear_objective + penalty_multiplier * linear_penalty
        expected_quadratic_objective = (model.quad_objective +
                                        penalty_multiplier * quadratic_penalty)

        linear_objective, quadratic_objective = model.H

        self.assertTrue(np.array_equal(expected_linear_objective, linear_objective))
        self.assertTrue(np.array_equal(expected_quadratic_objective, quadratic_objective))


class InvalidEnum(Enum):
    """Simple enum class for resource rules (example within a test)."""
    INVALID = "Invalid"


class AllocationModelXTestCase(TestCase):

    def test_init_valid_input(self):
        """Tests initialization with valid input."""
        resources = ["CPU", "Memory", "Power"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2, 3], [2, 1, 4]]
        resource_limits = [10, 8, 12]
        resource_rule = [ResourceRuleEnum.MAXIMUM, ResourceRuleEnum.MINIMUM, ResourceRuleEnum.MAXIMUM]
        resource_rule_values = [rr.value for rr in resource_rule]
        cost_per_task = [5, 10]
        
        alpha = 2.0

        model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rule,
                                 cost_per_task)
        model.penalty_multiplier = alpha
        assert model.resources == resources
        assert model.tasks == tasks
        assert np.array_equal(model.resource_usage, np.array(resource_usage))
        assert np.array_equal(model.resource_limits, np.array(resource_limits))
        assert model.senses == resource_rule_values
        assert np.array_equal(model.cost_per_task, np.array(cost_per_task))

    def test_init_invalid_resource_rule(self):
        """Tests initialization with invalid resource_rule."""
        resources = ["CPU", "Memory", "Power"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2, 3], [2, 1, 4]]
        resource_limits = [10, 8, 12]

        resource_rule = [InvalidEnum.INVALID, ResourceRuleEnum.MINIMUM, ResourceRuleEnum.EXACT]  # Invalid rule
        cost_per_task = [5, 10]
        
        alpha = 2.0

        with self.assertRaises(ValueError):
            model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rule,
                                     cost_per_task)
            model.penalty_multiplier = alpha

    def test_invalid_resource_rule_type(self):
        """
        Test that ValueError is raised for non-enum elements in resource_rule.
        """
        invalid_rule = ["not", "enum"]  # List containing non-enum elements
        with self.assertRaises(TypeError) as cm:
            AllocationModelX(resources=["CPU", "Memory"], tasks=["Task1", "Task2"],
                             resource_usage=[[1, 2], [3, 4]], resource_limits=[10, 20],
                             resource_rule=invalid_rule, cost_per_task=[5, 10])
        self.assertEqual(str(cm.exception),
                         "Argument 'resource_rule' must contain only enums. Elements lack a 'value' attribute.")

    def test_build_constraints_le(self):
        """Tests _build_constraints for less than or equal (LE) constraint."""
        resources = ["CPU"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1], [2]]
        resource_limits = [10]
        resource_rule = [ResourceRuleEnum.MAXIMUM]
        cost_per_task = [5, 10]
        
        alpha = 2.0

        model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rule,
                                 cost_per_task)
        model.penalty_multiplier = alpha

        A, b = model.constraints

        expected_A = np.array([[1, 2, 1]])
        expected_b = np.array([10])

        assert np.allclose(A, expected_A)
        assert np.allclose(b, expected_b)

    def test_build_constraints_ge(self):
        """Tests _build_constraints for greater than or equal (GE) constraint."""
        resources = ["CPU"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1], [2]]
        resource_limits = [5]
        resource_rule = [ResourceRuleEnum.MINIMUM]
        cost_per_task = [5, 10]
        
        alpha = 2.0

        model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rule,
                                 cost_per_task)
        model.penalty_multiplier = alpha

        A, b = model.constraints

        expected_A = np.array([[1, 2, -1]])
        expected_b = np.array([5])

        assert np.allclose(A, expected_A)
        assert np.allclose(b, expected_b)

    def test_build_constraints_eq(self):
        """Tests _build_constraints for equality (EQ) constraint."""
        resources = ["CPU"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1], [2]]
        resource_limits = [8]
        resource_rule = [ResourceRuleEnum.EXACT]
        cost_per_task = [5, 10]
        
        alpha = 2.0

        model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rule,
                                 cost_per_task)
        model.penalty_multiplier = alpha

        A, b = model.constraints
        assert A.shape == (1, 2)
        assert b.shape == (1,)
        expected_A = np.array([[1, 2]])
        expected_b = np.array([8])

        assert np.allclose(A, expected_A)
        assert np.allclose(b, expected_b)

    def test_build_constraints_all_eq(self):
        """Tests _build_constraints for all equality constraints (EQ)."""
        resources = ["CPU", "Memory"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2], [4, 3]]
        resource_limits = [10, 8]
        resource_rule = [ResourceRuleEnum.EXACT, ResourceRuleEnum.EXACT]
        cost_per_task = [5, 10]
        
        alpha = 2.0

        model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rule,
                                 cost_per_task)
        model.penalty_multiplier = alpha

        A, b = model.constraints

        expected_A = np.array([[1, 4], [2, 3]])
        expected_b = np.array([10, 8])

        assert np.allclose(A, expected_A)
        assert np.allclose(b, expected_b)

    def test_build_constraints_all_le(self):
        """Tests _build_constraints for all less than or equal constraints (LE)."""
        resources = ["CPU", "Memory"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 4], [2, 1]]
        resource_limits = [10, 8]
        resource_rule = [ResourceRuleEnum.MAXIMUM, ResourceRuleEnum.MAXIMUM]
        cost_per_task = [5, 10]
        
        alpha = 2.0

        model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rule,
                                 cost_per_task)
        model.penalty_multiplier = alpha

        A, b = model.constraints

        expected_A = np.array([[1, 2, 1, 0], [4, 1, 0, 1]])
        expected_b = np.array([10, 8])

        assert np.allclose(A, expected_A)
        assert np.allclose(b, expected_b)

    def test_build_constraints_all_ge(self):
        """Tests _build_constraints for all greater than or equal constraints (GE)."""
        resources = ["CPU", "Memory"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 4], [2, 1]]
        resource_limits = [5, 3]  # Lower limits for GE constraints
        resource_rule = [ResourceRuleEnum.MINIMUM, ResourceRuleEnum.MINIMUM]
        cost_per_task = [5, 10]
        
        alpha = 2.0

        model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rule,
                                 cost_per_task)
        model.penalty_multiplier = 1

        A, b = model.constraints

        expected_A = np.array([[1, 2, -1, 0], [4, 1, 0, -1]])
        expected_b = np.array([5, 3])

        assert np.allclose(A, expected_A)
        assert np.allclose(b, expected_b)

    def test_build_constraints_mixed(self):
        """Tests _build_constraints for mixed constraints with different combinations."""
        resources = ["CPU", "Memory", "Storage"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2, 3], [2, 1, 1]]
        resource_limits = [10, 8, 6]
        # Mixed rule combinations for 3 resources
        resource_rule = [ResourceRuleEnum.MAXIMUM, ResourceRuleEnum.MINIMUM, ResourceRuleEnum.EXACT]
        cost_per_task = [5, 10]
        
        alpha = 2.0

        model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rule,
                                 cost_per_task)
        model.penalty_multiplier = alpha

        A, b = model.constraints
        assert A.shape == (3, 4)
        assert b.shape == (3,)
        expected_A = np.array([[1, 2, 1, 0], [2, 1, 0, -1], [3, 1, 0, 0]])
        expected_b = np.array([10, 8, 6])

        assert np.allclose(A, expected_A)
        assert np.allclose(b, expected_b)

    def test_linear_objective(self):
        """
        Tests if _linear_objective returns the correct linear part of the objective function (profit).
        """
        resources = ["Material", "Labor"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2], [2, 1]]
        resource_limits = [10, 8]
        resource_rule = [ResourceRuleEnum.MINIMUM, ResourceRuleEnum.MINIMUM]
        cost_per_task = [5, 10]
        

        model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rule,
                                 cost_per_task)
        model.penalty_multiplier = 1

        expected_objective = np.hstack([np.array(cost_per_task), np.zeros(len(resources))])
        actual_objective = model.linear_objective

        self.assertTrue(np.array_equal(expected_objective, actual_objective))

    def test_quadratic_objective(self):
        """
        Tests if _quadratic_objective returns a zero 2D array (no quadratic term).
        """
        resources = ["Material", "Labor"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2], [2, 1]]
        resource_limits = [10, 8]
        resource_rule = [ResourceRuleEnum.MINIMUM, ResourceRuleEnum.MINIMUM]
        cost_per_task = [5, 10]
        

        model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rule,
                                 cost_per_task)
        model.penalty_multiplier = 1
        model.upper_bound = [1, 1]
        expected_objective = np.zeros((len(tasks) + len(resources), len(tasks) + len(resources)))
        actual_objective = model.quad_objective

        self.assertTrue(np.array_equal(expected_objective, actual_objective))

    def test_H(self):
        """
        Tests if build of H returns the linear and quadratic objective portions
        """
        resources = ["Material", "Labor", "Time"]
        tasks = ["Task A", "Task B"]
        resource_usage = [[1, 2, 3], [2, 1, 4]]
        resource_limits = [10, 8, 12]
        resource_rule = [ResourceRuleEnum.MINIMUM, ResourceRuleEnum.MINIMUM, ResourceRuleEnum.MAXIMUM]
        cost_per_task = [5, 10]
        

        model = AllocationModelX(resources, tasks, resource_usage, resource_limits, resource_rule,
                                 cost_per_task)
        model.penalty_multiplier = 1 

        # Pre-calculated penalty terms
        linear_penalty, quadratic_penalty = model.penalties
        penalty_multiplier = model.penalty_multiplier

        expected_linear_objective = model.linear_objective + penalty_multiplier * linear_penalty
        expected_quadratic_objective = (model.quad_objective +
                                        penalty_multiplier * quadratic_penalty)

        linear_objective, quadratic_objective = model.H

        self.assertTrue(np.array_equal(expected_linear_objective, linear_objective))
        self.assertTrue(np.array_equal(expected_quadratic_objective, quadratic_objective))
