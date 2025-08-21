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
from sklearn.preprocessing import MinMaxScaler

from eqc_models.ml.classifierbase import ClassifierBase


class QSVMClassifier(ClassifierBase):
    """An implementation of QSVM classifier that uses QCi's Dirac-3.

    Parameters
    ----------

    relaxation_schedule: Relaxation schedule used by Dirac-3; default:
    2.

    num_samples: Number of samples used by Dirac-3; default: 1.

    solver_access: Solver access type: cloud or direct; default: cloud.

    ip_addr: IP address of the device when direct access is used; default: None.
    
    port: Port number of the device when direct access is used; default: None.    
    
    lambda_coef: The penalty multipler

    Examples
    -----------

    >>> from sklearn import datasets
    >>> from sklearn.preprocessing import MinMaxScaler
    >>> from sklearn.model_selection import train_test_split
    >>> iris = datasets.load_iris()
    >>> X = iris.data
    >>> y = iris.target
    >>> scaler = MinMaxScaler()
    >>> X = scaler.fit_transform(X)
    >>> for i in range(len(y)):
    ...     if y[i] == 0:
    ...         y[i] = -1
    ...     elif y[i] == 2:
    ...         y[i] = 1
    >>> X_train, X_test, y_train, y_test = train_test_split(
    ...     X,
    ...     y,
    ...     test_size=0.2,
    ...     random_state=42,
    ... )
    >>> from eqc_models.ml.classifierqsvm import QSVMClassifier
    >>> obj = QSVMClassifier(
    ...     relaxation_schedule=2,
    ...     num_samples=1,
    ... )
    >>> from contextlib import redirect_stdout
    >>> import io
    >>> f = io.StringIO()
    >>> with redirect_stdout(f):
    ...    obj = obj.fit(X_train, y_train)
    ...    y_train_prd = obj.predict(X_train)
    ...    y_test_prd = obj.predict(X_test)

    """

    def __init__(
        self,
        relaxation_schedule=1,
        num_samples=1,
        solver_access="cloud",
        ip_addr=None,
        port=None,            
        lambda_coef=1.0,
    ):
        super(QSVMClassifier).__init__()

        assert solver_access in ["cloud", "direct"]
        
        self.relaxation_schedule = relaxation_schedule
        self.num_samples = num_samples
        self.solver_access = solver_access
        self.ip_addr = ip_addr
        self.port = port        
        self.lambda_coef = lambda_coef
        self.fea_scaler = MinMaxScaler(feature_range=(-1, 1))

    def fit(self, X, y):
        """
        Build a QSVM classifier from the training set (X, y).

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
        The training input samples.

        y : array-like of shape (n_samples,)
        The target values.

        Returns
        -------
        Response of Dirac-3 in JSON format.
        """

        assert X.shape[0] == y.shape[0], "Inconsistent sizes!"

        assert set(y) == {-1, 1}, "Target values should be in {-1, 1}"

        X = self.fea_scaler.fit_transform(X)
        
        J, C, sum_constraint = self.get_hamiltonian(X, y)

        assert J.shape[0] == J.shape[1], "Inconsistent hamiltonian size!"
        assert J.shape[0] == C.shape[0], "Inconsistent hamiltonian size!"

        self.set_model(J, C, sum_constraint)

        sol, response = self.solve()

        assert len(sol) == C.shape[0], "Inconsistent solution size!"

        self.params = self.convert_sol_to_params(sol)

        self.X_train = X
        self.y_train = y

        return response

    def predict_raw(self, X: np.array):
        """
        Predict classes for X.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)

        Returns
        -------
        y : ndarray of shape (n_samples,)
        The predicted classes.
        """
        n_records = X.shape[0]
        X = self.fea_scaler.transform(X)        
        X_tilde = np.concatenate((X, np.ones((n_records, 1))), axis=1)

        y = np.einsum("i,ki->k", self.params, X_tilde)

        return y

    def predict(self, X: np.array):
        """
        Predict classes for X.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)

        Returns
        -------
        y : ndarray of shape (n_samples,)
        The predicted classes.
        """

        y = self.predict_raw(X)
        y = np.sign(y)

        return y

    def get_hamiltonian(
        self,
        X: np.array,
        y: np.array,
    ):
        n_records = X.shape[0]
        n_dims = X.shape[1]

        J = np.zeros(shape=(1 + n_dims, 1 + n_dims), dtype=np.float32)
        C = np.zeros(shape=(1 + n_dims,), dtype=np.float32)

        X_tilde = np.concatenate((X, np.ones((n_records, 1))), axis=1)

        J = self.lambda_coef * np.einsum(
            "i,ik,il->kl", y**2, X_tilde, X_tilde
        )

        for k in range(n_dims):
            J[k][k] += 0.5

        C = -2.0 * self.lambda_coef * np.einsum("i,ik->k", y, X_tilde)

        J = 0.5 * (J + J.transpose())
        C = C.reshape((1 + n_dims, 1))

        return J, C, 1.0

    def convert_sol_to_params(self, sol):
        return np.array(sol)


class QSVMClassifierDual(ClassifierBase):
    """An implementation of dual QSVM classifier that uses QCi's Dirac-3.

    Parameters
    ----------

    relaxation_schedule: Relaxation schedule used by Dirac-3; default:
    2.

    num_samples: Number of samples used by Dirac-3; default: 1.

    solver_access: Solver access type: cloud or direct; default: cloud.

    ip_addr: IP address of the device when direct access is used; default: None.
    
    port: Port number of the device when direct access is used; default: None.    
    
    upper_limit: Coefficient upper limit; a regularization parameter;
    default: 1.0.

    gamma: Gaussian kernel parameter; default: 1.0.

    eta: A penalty multiplier; default: 1.0.

    zeta: A penalty multiplier; default: 1.0.

    Examples
    -----------

    >>> from sklearn import datasets
    >>> from sklearn.preprocessing import MinMaxScaler
    >>> from sklearn.model_selection import train_test_split
    >>> iris = datasets.load_iris()
    >>> X = iris.data
    >>> y = iris.target
    >>> scaler = MinMaxScaler()
    >>> X = scaler.fit_transform(X)
    >>> for i in range(len(y)):
    ...     if y[i] == 0:
    ...         y[i] = -1
    ...     elif y[i] == 2:
    ...         y[i] = 1
    >>> X_train, X_test, y_train, y_test = train_test_split(
    ...     X,
    ...     y,
    ...     test_size=0.2,
    ...     random_state=42,
    ... )
    >>> from eqc_models.ml.classifierqsvm import QSVMClassifierDual
    >>> obj = QSVMClassifierDual(
    ...     relaxation_schedule=2,
    ...     num_samples=1,
    ...     upper_limit=1.0,
    ...     gamma=1.0,
    ...     eta=1.0,
    ...     zeta=1.0,
    ... )
    >>> from contextlib import redirect_stdout
    >>> import io
    >>> f = io.StringIO()
    >>> with redirect_stdout(f):
    ...    obj = obj.fit(X_train, y_train)
    ...    y_train_prd = obj.predict(X_train)
    ...    y_test_prd = obj.predict(X_test)

    """

    def __init__(
        self,
        relaxation_schedule=2,
        num_samples=1,
        solver_access="cloud",
        ip_addr=None,
        port=None,            
        upper_limit=1.0,
        gamma=1.0,
        eta=1.0,
        zeta=1.0,
    ):
        super(QSVMClassifierDual).__init__()

        assert solver_access in ["cloud", "direct"]
        
        self.relaxation_schedule = relaxation_schedule
        self.num_samples = num_samples
        self.solver_access = solver_access
        self.ip_addr = ip_addr
        self.port = port        
        self.upper_limit = upper_limit
        self.gamma = gamma
        self.eta = eta
        self.zeta = zeta

    def kernel(self, vec1, vec2):
        return np.exp(-self.gamma * np.linalg.norm(vec1 - vec2) ** 2)

    def fit(self, X, y):
        """
        Build a QSVM classifier from the training set (X, y).

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
        The training input samples.

        y : array-like of shape (n_samples,)
        The target values.

        Returns
        -------
        Response of Dirac-3 in JSON format.
        """

        assert X.shape[0] == y.shape[0], "Inconsistent sizes!"

        assert set(y) == {-1, 1}, "Target values should be in {-1, 1}"

        J, C, sum_constraint = self.get_hamiltonian(X, y)

        assert J.shape[0] == J.shape[1], "Inconsistent hamiltonian size!"
        assert J.shape[0] == C.shape[0], "Inconsistent hamiltonian size!"

        self.set_model(J, C, sum_constraint)

        sol, response = self.solve()

        assert len(sol) == C.shape[0], "Inconsistent solution size!"

        self.params = self.convert_sol_to_params(sol)

        self.X_train = X
        self.y_train = y

        n_records = X.shape[0]
        self.kernel_mat_train = np.zeros(
            shape=(n_records, n_records), dtype=np.float32
        )
        for m in range(n_records):
            for n in range(n_records):
                self.kernel_mat_train[m][n] = self.kernel(X[m], X[n])

        return response

    def predict(self, X: np.array):
        """
        Predict classes for X.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)

        Returns
        -------
        y : ndarray of shape (n_samples,)
        The predicted classes.
        """

        assert self.X_train is not None, "Model not trained yet!"
        assert self.y_train is not None, "Model not trained yet!"

        assert (
            X.shape[1] == self.X_train.shape[1]
        ), "Inconsistent dimensions!"

        n_records = X.shape[0]
        n_records_train = self.X_train.shape[0]
        kernel_mat = np.zeros(
            shape=(n_records, n_records_train), dtype=np.float32
        )
        for m in range(n_records):
            for n in range(n_records_train):
                kernel_mat[m][n] = self.kernel(X[m], self.X_train[n])

        intercept = 0
        tmp_vec1 = np.tensordot(
            self.params * self.y_train, self.kernel_mat_train, axes=(0, 0)
        )
        assert tmp_vec1.shape[0] == n_records_train, "Inconsistent size!"

        tmp1 = np.sum(
            self.params
            * (self.upper_limit - self.params)
            * (self.y_train - tmp_vec1)
        )
        tmp2 = np.sum(self.params * (self.upper_limit - self.params))

        assert tmp2 != 0, "Something went wrong!"

        intercept = tmp1 / tmp2

        y = np.zeros(shape=(n_records), dtype=np.float32)
        y += np.tensordot(
            self.params * self.y_train, kernel_mat, axes=(0, 1)
        )
        y += intercept
        y = np.sign(y)

        return y

    def get_hamiltonian(
        self,
        X: np.array,
        y: np.array,
    ):
        n_records = X.shape[0]
        n_dims = X.shape[1]

        J = np.zeros(
            shape=(2 * n_records, 2 * n_records), dtype=np.float32
        )
        C = np.zeros(shape=(2 * n_records,), dtype=np.float32)

        for n in range(n_records):
            for m in range(n_records):
                J[n][m] = (
                    0.5 * y[n] * y[m] * self.kernel(X[n], X[m])
                    + self.zeta * y[n] * y[m]
                )
            J[n][n] += self.eta
            J[n][n + n_records] = self.eta
            J[n + n_records][n] = self.eta
            J[n + n_records][n + n_records] = self.eta

            C[n] = -1.0 - 2.0 * self.eta * self.upper_limit
            C[n + n_records] = -2.0 * self.eta * self.upper_limit

        C = C.reshape((2 * n_records, 1))
        J = 0.5 * (J + J.transpose())

        return J, C, n_records * self.upper_limit

    def convert_sol_to_params(self, sol):
        assert len(sol) % 2 == 0, "Expected an even solution size!"

        sol = sol[: int(len(sol) / 2)]

        return np.array(sol)
