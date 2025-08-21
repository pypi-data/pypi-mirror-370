# EQC Models

## Quick Reference

### Installation

Install from the Python Package Index (PyPI) using 
```bash
pip install eqc-models
```

For pre-release and source versions, install `eqc-models` by extracting the source package and running

```bash
pip install -e .
```

from the folder with the `pyproject.toml` file. This will create an editable installation that is local to your user environment.
Certain optimizations require extension modules, in particular `eqc_models.base.polyeval`. This is a C extension produced from
a Cython module which evaluates polynomial expressions. Since there could be thousands of terms, the C extension can greatly 
improve performance of some algorithms. Installing from source with pip will build the module.

### Modeling

Implement a model by selecting from the most appropriate model class from the available models
and pass the required data. The model classes are (in depth first order by hierarchy)

- `eqc_models.base.EQCModel`: a base class for all models
- `eqc_models.ml.classifierbase.ClassifierBase`: a base model for machine learning classifier models
- `eqc_models.ml.classifierqboost.QBoostClassifier`: a machine learning classifier model using QBoost
- `eqc_models.ml.classifierqsvm.QSVMClassifier`: a machine learning classifier model using QSVM
- `eqc_models.ml.communitydetection.CommunityDetectionModel`: a model for modeling community detection problems
- `eqc_models.base.QuadraticModel`: a base class for all models with up to quadratic terms
- `eqc_models.base.ConstrainedQuadraticModel`: a base class for all models with up to quadratic objective functions and linear equality constraints
- `eqc_models.base.PolynomialModel`: a base class for all models that utilize a polynomial formulation (up to fifth order)
- `eqc_models.allocation.AllocationModel`: an allocation model with equality resource constraints
- `eqc_models.allocation.AllocationModelX`: an allocation model with equality and inequality resource constraints
- `eqc_models.allocation.portmomentum.PortMomentum`: a portfolio allocation momentum model
- `eqc_models.portbase.PortBase`: a portfolio allocation base model
- `eqc_models.graph.MaxCutModel`: a maximum cut model
- `eqc_models.assignment.qap.QAPModel`: a quadratic assignment problem model
- `eqc_models.sequence.tsp.TSPModel`: a base class for TSP models
- `eqc_models.sequence.tsp.MTZTSPModel`: a traveling salesman model using the MTZ formulation
- `eqc_models.utilities.qplib.QGLModel`: a model based on `ConstrainedQuadraticModel` to solve problems
  from qplib

### Solvers

The hierarchy of solvers uses `QciClient` from the `qci-client` package. Both Dirac-1 and Dirac-3 can be accessed using these solvers. Specific classes exist for the devices. 

- `eqc_models.qciclientsolver.Dirac1CloudSolver`: A solver class that accesses Dirac-1 via the Qatalyst cloud service
- `eqc_models.qciclientsolver.Dirac3ContinuousCloudSolver`: A solver class for quasi-continuous models that accesses Dirac-3 via the Qatalyst cloud service
- `eqc_models.qciclientsolver.Dirac3IntegerCloudSolver`: A solver class for integer models that accesses Dirac-3 via the Qatalyst cloud service

### Using Classifier Models

Use of classification models is based on the well known pattern of fitting a model, then
using the fitted model to predict classifications. Here is a snippet from the `qsvm_iris_dirac3.py` script:

```python
# Get QSVM model
obj = QSVMClassifier(
    relaxation_schedule=2,
    num_samples=1,
    upper_limit=1.0,
    gamma=1.0,
    eta=1.0,
    zeta=1.0,
)

# Train
obj.fit(X_train, y_train)

y_train_prd = obj.predict(X_train)
y_test_prd = obj.predict(X_test)
```

### Using Decision Optimization Models

Decision optimization models can be utilized by building a model, then passing the model to a solver's `solve` method. The following snippet of code is taken from the `qplib_runner.py` script.

```python
# C, J are the linear and quadratic components of the expression
# A and b are left hand and right hand side values for linear constraints
# R is the summation constraint value for the Dirac-3 requirement
model = QGLModel(C, J, A, b)
domains = [R if types[j] == "REAL" else 1 for j in range(num_variables)]
model.domains = np.array(domains)
model.penalty_multiplier = alpha
# set the machine slacks to 1 to add a dummy variable to capture slack value from the summation constraint
model.machine_slacks = 1
print(f"Constructed model with R={R} alpha={alpha}")
solver = Dirac3CloudSolver()
print(f"Running model with relaxation_schedule={schedule}")
response = solver.solve(model, basename, sum_constraint=R, relaxation_schedule=schedule)
print(f"Energy {response['results']['energies'][0]}")
```

## Design Overview

This package is designed around two central base classes. The first, `EqcModel`, includes the most basic common elements of an 
optimization model. The second, `ModelSolver`, includes the most basic elements of a solver class. While not all classes in this package
inherit from one of these two classes, the core functionality exists in thie hierarchy. Additional things, such as algorithms and
supporting methods take advantage of these classes. Another design choice in the package is to utilize multiple inheritance and class
mixins for construction of functional classes. This design is not intended to impact the end user, who can simply instantiate a certain
model or solver class for usage. If a new model class is desired, the mixin design may be utilized to construct this new class. 
Additionally, a hybrid solver could be implemented using this same design. 

## Troubleshooting Common Errors

**No module named '_bz2'** This error occurs because NetworkX, a dependency of `eqc-models`, requires the bzip 2 library and it has not been found. On some linux environments, the OS package `libbzip2-dev` can be installed with apt or yum, then the python environment must be installed again.

## Further Information

Most of the classes in this package have doctests, see these docstrings for specific concrete examples. Also, the `scripts` and `test` directories have examples on modeling and solving with `eqc-models`.
