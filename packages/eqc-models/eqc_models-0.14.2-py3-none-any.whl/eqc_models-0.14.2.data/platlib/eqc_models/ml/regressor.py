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

from eqc_models.ml.regressorbase import RegressorBase


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        beg_time = time.time()
        val = func(*args, **kwargs)
        end_time = time.time()
        tot_time = end_time - beg_time

        print(
            "Runtime of %s: %0.2f seconds!"
            % (
                func.__name__,
                tot_time,
            )
        )

        return val

    return wrapper


class LinearRegression(RegressorBase):
    """An implementation of linear regression that uses QCi's Dirac-3.

    Parameters
    ----------

    relaxation_schedule: Relaxation schedule used by Dirac-3;
    default: 2.

    num_samples: Number of samples used by Dirac-3; default: 1.

    solver_access: Solver access type: cloud or direct; default: cloud.

    ip_addr: IP address of the device when direct access is used; default: None.

    port: Port number of the device when direct access is used; default: None.
    
    l2_reg_coef: L2 regularization penalty multiplier; default: 0.

    alpha: A penalty multiplier to ensure the correct sign of a
    model parameter; default: 0.

    Examples
    ---------

    >>> X_train = np.array([[1], [2], [3], [4], [5]])
    >>> y_train = np.array([3, 5, 7, 9, 11])
    >>> X_test = np.array([[6], [7], [8]])
    >>> y_test = np.array([13, 15, 17])
    >>> from eqc_models.ml.regressor import LinearRegression
    >>> from contextlib import redirect_stdout    
    >>> import io
    >>> f = io.StringIO()
    >>> with redirect_stdout(f): 
    ...     model = LinearRegression()
    ...     model = model.fit(X_train, y_train)
    ...     y_pred_train = model.predict(X_train)
    ...     y_pred_test = model.predict(X_test)
    """
    
    def __init__(
        self,
        relaxation_schedule=2,
        num_samples=1,
        solver_access="cloud",
        ip_addr=None,
        port=None,            
        l2_reg_coef=0,
        alpha=0,
    ):
        super(LinearRegression).__init__()

        assert solver_access in ["cloud", "direct"]
        
        self.relaxation_schedule = relaxation_schedule
        self.num_samples = num_samples
        self.solver_access = solver_access
        self.ip_addr = ip_addr
        self.port = port        
        self.l2_reg_coef = l2_reg_coef
        self.alpha = alpha
        self.params = None
        self.fit_intercept = None
        self.resp_transformer = None
        self.fea_transformer = None

    @timer
    def fit(self, X, y, fit_intercept=True):
        """Trains a linear regression from the training set (X, y).

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
        The training input samples.

        y : array-like of shape (n_samples,)
        The target values.

        fit_intercept: A boolean indicating whether an intercept
        should be fit; default: True.

        Returns
        -------
        self : object
        Fitted estimator.

        """

        assert X.shape[0] == y.shape[0], "Inconsistent sizes!"

        self.fea_transformer = MinMaxScaler(feature_range=(0, 1))
        X = self.fea_transformer.fit_transform(X)

        self.resp_transformer = MinMaxScaler(feature_range=(0, 1))
        y = self.resp_transformer.fit_transform(y.reshape(-1, 1)).reshape(
            -1
        )

        self.fit_intercept = fit_intercept

        n_records = X.shape[0]
        if fit_intercept:
            X = np.concatenate([X, np.ones((n_records, 1))], axis=1)

        n_features = X.shape[1]

        X = np.concatenate([X, -X], axis=1)

        n_dims = X.shape[1]

        assert n_dims == 2 * n_features, "Internal error!"

        J, C, sum_constraint = self.get_hamiltonian(X, y)

        assert J.shape[0] == J.shape[1], "Inconsistent hamiltonian size!"
        assert J.shape[0] == C.shape[0], "Inconsistent hamiltonian size!"

        self.set_model(J, C, sum_constraint)

        sol = self.solve()

        assert len(sol) == C.shape[0], "Inconsistent solution size!"

        self.params = self.convert_sol_to_params(sol)

        return self

    @timer
    def predict(self, X: np.array):
        """
        Predicts output of the regressor for input X.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)

        Returns
        -------
        y : ndarray of shape (n_samples,)
        The predicted raw output of the classifier.
        """

        if self.params is None:
            return

        X = self.fea_transformer.transform(X)

        n_records = X.shape[0]
        if self.fit_intercept:
            X = np.concatenate([X, np.ones((n_records, 1))], axis=1)

        X = np.concatenate([X, -X], axis=1)

        assert X.shape[1] == len(
            self.params
        ), "Inconsistent dimension of X!"

        y = X @ self.params

        assert y.shape[0] == X.shape[0], "Internal error!"

        y = self.resp_transformer.inverse_transform(
            y.reshape(-1, 1)
        ).reshape(-1)

        return y

    @timer
    def get_hamiltonian(
        self,
        X: np.array,
        y: np.array,
    ):
        n_dims = X.shape[1]

        J = np.zeros(shape=(n_dims, n_dims), dtype=np.float32)
        C = np.zeros(shape=(n_dims,), dtype=np.float32)

        for i in range(n_dims):
            for j in range(n_dims):
                J[i][j] = np.sum(X.swapaxes(0, 1)[i] * X.swapaxes(0, 1)[j])
                if i == j:
                    J[i][j] += self.l2_reg_coef

            C[i] = -2.0 * np.sum(y * X.swapaxes(0, 1)[i])

        C = C.reshape((n_dims, 1))

        # Add sign penalty multiplier
        n_features = int(n_dims / 2)
        for i in range(n_features):
            J[i][i + n_features] += self.alpha
            J[i + n_features][i] += self.alpha

        return J, C, 1.0

    def convert_sol_to_params(self, sol):
        return np.array(sol)
