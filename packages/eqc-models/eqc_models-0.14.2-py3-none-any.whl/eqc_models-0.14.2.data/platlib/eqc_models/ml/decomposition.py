# (C) Quantum Computing Inc., 2024.
# Import libs
import os
import sys
import time
import datetime
import json
import warnings
from functools import wraps
import numpy as np

from qci_client import QciClient

from eqc_models import QuadraticModel
from eqc_models.solvers.qciclient import (
    Dirac3CloudSolver,
)
from eqc_models.solvers.eqcdirect import Dirac3DirectSolver

class DecompBase(QuadraticModel):
    """An Base class for decomposition algorithms.

    Parameters
    ----------

    relaxation_schedule: Relaxation schedule used by Dirac-3; default:
    2.

    num_samples: Number of samples used by Dirac-3; default: 1.

    solver_access: Solver access type: cloud or direct; default: cloud.

    ip_addr: IP address of the device when direct access is used; default: None.

    port: Port number of the device when direct access is used; default: None.    
    """

    def __init__(
        self,
        relaxation_schedule=2,
        num_samples=1,
        solver_access="cloud",
        ip_addr=None,
        port=None,                        
    ):
        super(self).__init__(None, None, None)

        assert solver_access in ["cloud", "direct"]
        
        self.relaxation_schedule = relaxation_schedule
        self.num_samples = num_samples
        self.solver_access = solver_access
        self.ip_addr = ip_addr
        self.port = port

    def _get_hamiltonian(
        self,
        X: np.array,
    ):
        pass

    def _set_model(self, J, C, sum_constraint):
        # Set hamiltonians
        self._C = C
        self._J = J
        self._H = C, J
        self._sum_constraint = sum_constraint

        # Set upper_bound
        num_variables = C.shape[0]
        self.upper_bound = sum_constraint * np.ones((num_variables,))

        return

    def _solve(self):

        if self.solver_access == "direct":
            solver = Dirac3DirectSolver()
            solver.connect(self.ip_addr, self.port)
        else:
            solver = Dirac3CloudSolver()
                
        response = solver.solve(
            self,
            sum_constraint=self._sum_constraint,
            relaxation_schedule=self.relaxation_schedule,
            num_samples=self.num_samples,
        )

        if self.solver_access == "cloud":
            energies = response["results"]["energies"]
            solutions = response["results"]["solutions"]
        elif self.solver_access == "direct":
            energies = response["energy"]
            solutions = response["solution"]
            
        min_id = np.argmin(energies)
        sol = solutions[min_id]
            
        print(response)

        return sol, response

    def _solve_d1_test(self):
        qubo = self._J

        # Make sure matrix is symmetric to machine precision
        qubo = 0.5 * (qubo + qubo.transpose())

        # Instantiate
        qci = QciClient()

        # Create json objects
        qubo_json = {
            "file_name": "qubo_tutorial.json",
            "file_config": {
                "qubo": {"data": qubo, "num_variables": qubo.shape[0]},
            },
        }

        response_json = qci.upload_file(file=qubo_json)
        qubo_file_id = response_json["file_id"]

        # Setup job json
        job_params = {
            "device_type": "dirac-1",
            "alpha": 1.0,
            "num_samples": 20,
        }
        job_json = qci.build_job_body(
            job_type="sample-qubo",
            job_params=job_params,
            qubo_file_id=qubo_file_id,
            job_name="tutorial_eqc1",
            job_tags=["tutorial_eqc1"],
        )
        print(job_json)

        # Run the job
        job_response_json = qci.process_job(
            job_body=job_json,
        )

        print(job_response_json)

        results = job_response_json["results"]
        energies = results["energies"]
        samples = results["solutions"]

        if True:
            print("Energies:", energies)

        sol = np.array(samples[0])

        print(sol)

        return sol

    def fit(self, X):
        pass

    def transform(self, X: np.array):
        pass

    def fit_transform(self, X):
        pass

    def get_dynamic_range(self):
        C = self._C
        J = self._J

        if C is None:
            return

        if J is None:
            return

        absc = np.abs(C)
        absj = np.abs(J)
        minc = np.min(absc[absc > 0])
        maxc = np.max(absc)
        minj = np.min(absj[absj > 0])
        maxj = np.max(absj)

        minval = min(minc, minj)
        maxval = max(maxc, maxj)

        return 10 * np.log10(maxval / minval)


class PCA(DecompBase):
    """An implementation of Principal component analysis (PCA) that
    uses QCi's Dirac-3.

    Linear dimensionality reduction using Singular Value
    Decomposition of the data to project it to a lower dimensional
    space.

    Parameters
    ----------

    n_components: Number of components to keep; if n_components is not
    set all components are kept; default: None.

    relaxation_schedule: Relaxation schedule used by Dirac-3; default:
    2.

    num_samples: Number of samples used by Dirac-3; default: 1.

    solver_access: Solver access type: cloud or direct; default: cloud.

    ip_addr: IP address of the device when direct access is used; default: None.

    port: Port number of the device when direct access is used; default: None.
    
    mode: Compute the largest or smallest principal components,
    largest_components vs. smallest_components; default:
    largest_components.

    Examples
    -----------

    >>> from sklearn import datasets
    >>> iris = datasets.load_iris()
    >>> X = iris.data
    >>> from sklearn.preprocessing import StandardScaler
    >>> scaler = StandardScaler()
    >>> X = scaler.fit_transform(X)
    >>> from eqc_models.ml.decomposition import PCA
    >>> from contextlib import redirect_stdout
    >>> import io
    >>> f = io.StringIO()
    >>> with redirect_stdout(f):
    ...    obj = PCA(
    ...        n_components=4,
    ...        relaxation_schedule=2,
    ...        num_samples=1,
    ...    )
    ...    X_pca = obj.fit_transform(X)

    """

    def __init__(
        self,
        n_components=None,
        relaxation_schedule=2,
        num_samples=1,
        solver_access="cloud",
        ip_addr=None,
        port=None,                        
        mode="largest_components",
    ):

        assert solver_access in ["cloud", "direct"]
        assert mode in ["largest_components", "smallest_components"], (
            "Invalid value of mode <%s>" % mode
        )
        
        self.n_components = n_components
        self.relaxation_schedule = relaxation_schedule
        self.num_samples = num_samples
        self.solver_access = solver_access
        self.ip_addr = ip_addr
        self.port = port        
        self.mode = mode
        self.X = None
        self.X_pca = None

    def _get_hamiltonian(
        self,
        X: np.array,
    ):
        num_records = X.shape[0]
        num_features = X.shape[1]

        J = np.matmul(X.transpose(), X)

        assert J.shape[0] == num_features
        assert J.shape[1] == num_features

        C = -np.sum(J, axis=1)

        assert C.shape[0] == num_features

        C = C.reshape((num_features, 1))

        if self.mode == "largest_components":
            J = -J
            C = -C

        return J, C

    def _get_first_component(self, X):
        J, C = self._get_hamiltonian(X)

        assert J.shape[0] == J.shape[1], "Inconsistent hamiltonian size!"
        assert J.shape[0] == C.shape[0], "Inconsistent hamiltonian size!"

        sum_constraint = 0.5 * (1.0 + C.shape[0])
        
        self._set_model(J, C, 1.0)

        sol, response = self._solve()

        assert len(sol) == C.shape[0], "Inconsistent solution size!"

        sol = np.array(sol)
        sol = 2.0 * sol - 1.0
        
        fct = np.linalg.norm(sol)
        if fct > 0:
            fct = 1.0 / fct

        v0 = fct * np.array(sol)
        v0 = v0.reshape((v0.shape[0], 1))

        lambda0 = np.matmul(np.matmul(v0.transpose(), -J), v0)[0][0]

        assert lambda0 >= 0, "Unexpected negative eigenvalue!"

        fct = np.sqrt(lambda0)
        if fct > 0:
            fct = 1.0 / fct

        u0 = fct * np.matmul(X, v0)
        u0 = u0.reshape(-1)

        fct = np.linalg.norm(u0)
        if fct > 0:
            fct = 1.0 / fct

        u0 = fct * u0

        return u0, response

    def fit(self, X):
        """
        Build a PCA object from the training set X.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
        The training input samples.

        Returns
        -------
        responses.
        A dirct containing Dirac responses.
        """

        num_features = X.shape[1]
        if self.n_components is None:
            n_components = num_features
        else:
            n_components = self.n_components

        n_components = min(n_components, num_features)

        self.X = X.copy()
        self.X_pca = []
        resp_hash = {}
        for i in range(n_components):
            u, resp = self._get_first_component(X)
            self.X_pca.append(u)
            u = u.reshape((u.shape[0], 1))

            X = X - np.matmul(
                u,
                np.matmul(u.transpose(), X),
            )

            assert X.shape == self.X.shape, "Inconsistent size!"

            resp_hash["component_%d_response" % (i + 1)] = resp

        self.X_pca = np.array(self.X_pca).transpose()

        assert self.X_pca.shape[0] == self.X.shape[0]
        assert self.X_pca.shape[1] == n_components

        return resp_hash

    def transform(self, X: np.array):
        """
        Apply dimensionality reduction to X.

        X is projected on the first principal components previously extracted
        from a training set.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
        New data, where `n_samples` is the number of samples
        and `n_features` is the number of features.

        Returns
        -------
        X_new : array-like of shape (n_samples, n_components)
        Projection of X in the first principal components, where `n_samples`
        is the number of samples and `n_components` is the number of the components.
        """
        if self.X is None:
            return

        return self.X_pca

    def fit_transform(self, X):
        """
        Fit the model with X and apply the dimensionality reduction on X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
        Training data, where `n_samples` is the number of samples
        and `n_features` is the number of features.

        Returns
        -------
        X_new : ndarray of shape (n_samples, n_components)
        Transformed values.
        """

        self.fit(X)

        return self.transform(X)
