# (C) Quantum Computing Inc., 2024.
from .eqcdirect import Dirac3DirectSolver
from .qciclient import (Dirac1CloudSolver, Dirac3CloudSolver, QciClientSolver,
                        Dirac3IntegerCloudSolver, Dirac3ContinuousCloudSolver)
from .mip import MIPMixin

class Dirac3MIPCloudSolver(MIPMixin, Dirac3ContinuousCloudSolver):
    pass

class Dirac3MIPDirectSolver(MIPMixin, Dirac3DirectSolver):
    pass

__all__ = ["Dirac3DirectSolver", "Dirac1CloudSolver", "Dirac3CloudSolver", 
           "EqcDirectSolver", "QciClientSolver", "Dirac3IntegerCloudSolver",
           "Dirac3ContinuousCloudSolver", "MIPMixin",
           "Dirac3MIPCloudSolver", "Dirac3MIPDirectSolver"]
