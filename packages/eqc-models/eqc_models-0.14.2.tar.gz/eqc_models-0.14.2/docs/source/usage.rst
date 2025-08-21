.. _usage:

=============
Basic Usage
=============

This example shows how to solve a basic qubo using Dirac-3. The solver setup requires that
environment variables are configured for connection.

.. code-block:: python

    import numpy as np
    from eqc_models.solvers import Dirac3CloudSolver
    from eqc_models.base import QuadraticModel
    J = np.array([[0, 1], [1, 0]])
    C = -1*np.ones((2,), dtype=np.int64)
    model = QuadraticModel(C, J)
    model.upper_bound = np.ones((2,), dtype=np.int64)
    # this will print the quadratic model in QUBO form
    print(model.qubo.Q)
    solver = Dirac3CloudSolver()
    response = solver.solve(model, num_samples=5, relaxation_schedule=1)
    for sol in response["results"]["solutions"]:
        print(sol)
