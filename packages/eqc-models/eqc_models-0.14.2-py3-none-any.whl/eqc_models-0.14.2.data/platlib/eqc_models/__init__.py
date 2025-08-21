# (C) Quantum Computing Inc., 2024.
"""
eqc-models package for high-level optimization modeling for EQC and other devices

"""

from .base import QuadraticModel, PolynomialModel
from .solvers import (Dirac1CloudSolver, Dirac3CloudSolver, Dirac3DirectSolver)
from .allocation import AllocationModel, AllocationModelX, ResourceRuleEnum
from .assignment import QAPModel
from .combinatorics import SetCoverModel, SetPartitionModel

__all__ = ["QuadraticModel", "PolynomialModel", "Dirac1CloudSolver", 
           "Dirac3CloudSolver", "AllocationModel", "AllocationModelX",
           "Dirac3DirectSolver", "ResourceRuleEnum",
           "QAPModel", "SetPartitionModel", "SetCoverModel"]
