# (C) Quantum Computing Inc., 2024.
"""
This subpackage contains the building blocks for formulating and solving models
with EQC devices. Many well known models in the space of quantum computing use
quadratic operators. Two generally accepted formats for quadratic models are
Ising Hamiltonian and QUBO operators. Ising models are not explicitly supported
because of the simple equivalence to QUBO models. Converters from Ising to QUBO
are readily available and may be added as a utility function in the future, but
for now are left out of the package. Other quadratic models, such as integer
or floating point models are supported using the domain and upper bound of the
model variables and the solver choice. 

Polynomial models are used to support higher order interactions between 
variables. These models are defined over non-negative variables with the 
highest power interaction being the only restriction on variable interactions.
This is also known as all-to-all connectivity.

Subpackages
-----------

constraints 
    This module defines support for linear equality and inequality constraints.
    It can be paired with the penalty multiplier algorithm to choose multiplier
    values which satisfy the enforcement of constraints as penalties. The mixin
    pattern is used to allow more complex classes to be built from these bases.

    - ConstraintMixIn
    - ConstraintModel
    - InequalitiesMixIn
    - InequalityConstraintModel

quadratic
    This module defines the methods required to convert a linear vector and 
    quadratic matrix into the required operator, either QUBO or Polynomial, for
    solving with EQC. The support for constraints is also incorporated.

    - ConstrainedQuadraticModel
    - QuadraticModel

polynomial
    This module defines the classes and methods for conversion from arrays of
    coefficients and indices to operators for solving with EQC. The support for
    constriants is also incorporated.

    - PolynomialModel
    - ConstrainedPolynomialModel

base
    This module defines abstract base classes for models and solvers.

    - EqcModel
    - ModelSolver

operators
    This module defines the operator types to use for passing problems to EQC
    devices.

    - Polynomial
    - QUBO

"""
from .constraints import (ConstraintModel, ConstraintsMixIn, InequalitiesMixin, 
                          InequalityConstraintModel)
from .quadratic import (ConstrainedQuadraticModel, QuadraticModel)
from .polynomial import (PolynomialModel, ConstrainedPolynomialModel)
from .base import (ModelSolver, EqcModel)
from .operators import (QUBO, Polynomial)
from .results import SolutionResults

__all__ = ["ConstraintsMixIn", "ConstraintModel", "ConstrainedQuadraticModel", 
           "QuadraticModel", "PolynomialModel", "ConstrainedPolynomialModel",
           "InequalitiesMixin", "InequalityConstraintModel",
           "EqcModel", "ModelSolver", "QUBO", "Polynomial",
           "SolutionResults"]
