# (C) Quantum Computing Inc., 2024.
# Import libs
import os
import sys
import time
import datetime
import json
import gc
import warnings
from functools import wraps
from multiprocessing import shared_memory, Pool, set_start_method, Manager
from multiprocessing.managers import SharedMemoryManager
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import (
    LinearDiscriminantAnalysis,
    QuadraticDiscriminantAnalysis,
)
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from eqc_models.ml.classifierbase import ClassifierBase

# from eqc_models.ml.cvqboost_hamiltonian import get_hamiltonian_pyx


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


class WeakClassifier:
    def __init__(
        self,
        X_train,
        y_train,
        weak_cls_type,
        weak_cls_params={},
        num_jobs=1,
    ):
        assert X_train.shape[0] == len(y_train)

        self.X_train = X_train
        self.y_train = y_train

        if weak_cls_type == "dct":
            self.clf = DecisionTreeClassifier(**weak_cls_params)
        elif weak_cls_type == "nb":
            self.clf = GaussianNB(**weak_cls_params)
        elif weak_cls_type == "lg":
            self.clf = LogisticRegression(**weak_cls_params)
        elif weak_cls_type == "gp":
            self.clf = GaussianProcessClassifier(**weak_cls_params)
        elif weak_cls_type == "knn":
            self.clf = KNeighborsClassifier(**weak_cls_params)
        elif weak_cls_type == "lda":
            self.clf = LinearDiscriminantAnalysis(**weak_cls_params)
        elif weak_cls_type == "qda":
            self.clf = QuadraticDiscriminantAnalysis(**weak_cls_params)
        elif weak_cls_type == "lgb":
            self.clf = LGBMClassifier(**weak_cls_params)
        elif weak_cls_type == "xgb":
            self.clf = XGBClassifier(**weak_cls_params)
        else:
            assert False, (
                "Unknown weak classifier type <%s>!" % weak_cls_type
            )

    def train(self):
        self.clf.fit(self.X_train, np.where(self.y_train == -1, 0, 1))

    def predict(self, X):
        y_pred = self.clf.predict(X)
        return np.where(y_pred == 0, -1, 1)


class QBoostClassifier(ClassifierBase):
    """An implementation of QBoost classifier that uses QCi's Dirac-3.

    Parameters
    ----------
    relaxation_schedule: Relaxation schedule used by Dirac-3;
    default: 2.

    num_samples: Number of samples used by Dirac-3; default: 1.

    solver_access: Solver access type: cloud or direct; default: cloud.

    ip_addr: IP address of the device when direct access is used; default: None.

    port: Port number of the device when direct access is used; default: None.

    lambda_coef: A penalty multiplier; default: 0.

    weak_cls_schedule: Weak classifier schedule. Is either 1, 2,
    or 3; default: 2.

    weak_cls_type: Type of weak classifier
        - dct: Decison tree classifier
        - nb: Naive Baysian classifier
        - lg: Logistic regression
        - gp: Gaussian process classifier
        - knn: K-nearest neighbors classifier
        - lda: Linear discriminant analysis classifier
        - qda: Quadratic discriminant analysis classifier
        - lgb: Light-GBM classifier
        - xgb: XGBoost classifier

    default: lg.

    weak_cls_params: Dict of weak classifier parameters. Default: {};
    use default parameters.

    weak_cls_strategy: Computation strategy for weak classifier
    training, either "sequential" or "multi_processing". Default:
    "multi_processing".

    weak_cls_num_jobs: Number of jobs when
    weak_cls_strategy="multi_processing". Default: None; use all
    available cores.

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
    >>> from eqc_models.ml.classifierqboost import QBoostClassifier
    >>> obj = QBoostClassifier(
    ...     relaxation_schedule=2,
    ...     num_samples=1,
    ...     lambda_coef=0.0,
    ... )
    >>> from contextlib import redirect_stdout
    >>> import io
    >>> f = io.StringIO()
    >>> with redirect_stdout(f):
    ...    obj.fit(X_train, y_train)
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
        lambda_coef=0,
        weak_cls_schedule=1,
        weak_cls_type="lg",
        weak_cls_params={},
        weak_cls_strategy="multi_processing",
        weak_cls_num_jobs=None,
        weak_cls_pair_count=None,
    ):
        super(QBoostClassifier).__init__()

        assert weak_cls_schedule in [1, 2, 3]
        assert weak_cls_type in [
            "dct",
            "nb",
            "lg",
            "gp",
            "knn",
            "lda",
            "qda",
            "lgb",
            "xgb",
        ]

        assert weak_cls_strategy in [
            "multi_processing",
            "multi_processing_shm",
            "sequential",
        ]
        assert solver_access in ["cloud", "direct"]

        self.relaxation_schedule = relaxation_schedule
        self.num_samples = num_samples
        self.solver_access = solver_access
        self.ip_addr = ip_addr
        self.port = port
        self.lambda_coef = lambda_coef
        self.weak_cls_schedule = weak_cls_schedule
        self.weak_cls_type = weak_cls_type
        self.weak_cls_params = weak_cls_params
        self.weak_cls_strategy = weak_cls_strategy
        if weak_cls_num_jobs is None or weak_cls_num_jobs <= 0:
            self.weak_cls_num_jobs = os.cpu_count()
        else:
            self.weak_cls_num_jobs = int(weak_cls_num_jobs)
        self.weak_cls_pair_count = weak_cls_pair_count

        self.h_list = []
        self.ind_list = []
        self.classes_ = None

    def topNPairs(self, X, n):
        
        assert n <= int(X.shape[1] * (X.shape[1] - 3) /2)
        
        cov = np.corrcoef(X, rowvar=False)
        abscov = np.abs(cov)
        flatcov = []
        for i in range(X.shape[1]):
            for j in range(i+1, X.shape[1]):
                flatcov.append((abscov[i, j], (i, j)))
        flatcov.sort()
        return [idx for val, idx in flatcov[-n:]]

    @timer
    def _build_weak_classifiers_sq(self, X, y):
        n_records = X.shape[0]
        n_dims = X.shape[1]

        assert len(y) == n_records

        self.h_list = []
        self.ind_list = []

        num_workers = self.weak_cls_num_jobs

        tasks = []
        for l in range(n_dims):
            weak_classifier = WeakClassifier(
                X[:, [l]],
                y,
                self.weak_cls_type,
                self.weak_cls_params,
            )
            weak_classifier.train()
            self.ind_list.append([l])
            self.h_list.append(weak_classifier)

        if self.weak_cls_schedule >= 2:
            """
            Use up to weak_cls_pair_count pairs, ordered by absolute covariance

            """
            if self.weak_cls_pair_count is None:
                weak_cls_pair_count = int(n_dims * (n_dims - 3) / 2)
            else:
                weak_cls_pair_count = self.weak_cls_pair_count
            pairs = self.topNPairs(X, weak_cls_pair_count)
            for i, j in pairs:
                weak_classifier = WeakClassifier(
                    X[:, [i, j]],
                    y,
                    self.weak_cls_type,
                    self.weak_cls_params,                    
                )
                weak_classifier.train()
                self.ind_list.append([i, j])
                self.h_list.append(weak_classifier)

        if self.weak_cls_schedule >= 3:
            for i in range(n_dims):
                for j in range(i + 1, n_dims):
                    for k in range(j + 1, n_dims):
                        weak_classifier = WeakClassifier(
                            X[:, [i, j, k]],
                            y,
                            self.weak_cls_type,
                            self.weak_cls_params,
                        )
                        weak_classifier.train()
                        self.ind_list.append([i, j, k])
                        self.h_list.append(weak_classifier)

        return

    def _train_weak_classifier_mp(
        self,
        indices,
        X_subset,
        y,
        n_records,
        n_dims,
        weak_cls_type,
        weak_cls_params,
    ):
        # Train the weak classifier
        weak_classifier = WeakClassifier(
            X_subset,
            y,
            weak_cls_type,
            weak_cls_params,
        )
        weak_classifier.train()

        return indices, weak_classifier

    @timer
    def _build_weak_classifiers_mp(self, X, y):
        n_records = X.shape[0]
        n_dims = X.shape[1]

        assert len(y) == n_records

        self.h_list = []
        self.ind_list = []

        num_workers = self.weak_cls_num_jobs
        print(f"Using {num_workers} workers to build weak classifiers.")

        set_start_method("fork", force=True)

        tasks = []
        for l in range(n_dims):
            tasks.append(
                (
                    [l],
                    X[:, [l]],
                    y,
                    n_records,
                    n_dims,
                    self.weak_cls_type,
                    self.weak_cls_params,
                )
            )

        if self.weak_cls_schedule >= 2:
            for i in range(n_dims):
                for j in range(i + 1, n_dims):
                    tasks.append(
                        (
                            [i, j],
                            X[:, [i, j]],
                            y,
                            n_records,
                            n_dims,
                            self.weak_cls_type,
                            self.weak_cls_params,
                        )
                    )

        if self.weak_cls_schedule >= 3:
            for i in range(n_dims):
                for j in range(i + 1, n_dims):
                    for k in range(j + 1, n_dims):
                        tasks.append(
                            (
                                [i, j, k],
                                X[:, [i, j, k]],
                                y,
                                n_records,
                                n_dims,
                                self.weak_cls_type,
                                self.weak_cls_params,
                            )
                        )

        # Parallel execution using Pool
        with Pool(processes=num_workers) as pool:
            results = pool.starmap(self._train_weak_classifier_mp, tasks)

        pool.join()
        pool.close()

        for indices, weak_classifier in results:
            self.ind_list.append(indices)
            self.h_list.append(weak_classifier)

        return

    def _train_weak_classifier_shm(
        self,
        indices,
        shm_X_name,
        shm_y_name,
        shared_list,
        n_records,
        n_dims,
        weak_cls_type,
        weak_cls_params,
    ):
        """Train a weak classifier using shared memory."""

        shm_X_worker = shared_memory.SharedMemory(name=shm_X_name)
        shm_y_worker = shared_memory.SharedMemory(name=shm_y_name)
        X_shared = np.ndarray(
            (n_records, n_dims), dtype=np.float32, buffer=shm_X_worker.buf
        )
        y_shared = np.ndarray(
            (n_records,), dtype=np.float32, buffer=shm_y_worker.buf
        )
        X_subset = X_shared[:, indices]

        weak_classifier = WeakClassifier(
            X_subset,
            y_shared,
            weak_cls_type,
            weak_cls_params,
        )
        weak_classifier.train()

        shared_list.append((indices, weak_classifier))

        shm_X_worker.close()
        shm_y_worker.close()

    @timer
    def _build_weak_classifiers_shm(self, X, y):
        n_records = X.shape[0]
        n_dims = X.shape[1]

        assert len(y) == n_records

        self.h_list = []
        self.ind_list = []

        num_workers = self.weak_cls_num_jobs
        print(f"Using {num_workers} workers to build weak classifiers.")

        set_start_method("fork", force=True)

        X = np.ascontiguousarray(X, dtype=np.float32)
        y = np.ascontiguousarray(y, dtype=np.float32)

        with SharedMemoryManager() as shm_manager:
            shm_X = shm_manager.SharedMemory(size=X.nbytes)
            shm_y = shm_manager.SharedMemory(size=y.nbytes)

            X_shared = np.ndarray(X.shape, dtype=X.dtype, buffer=shm_X.buf)
            y_shared = np.ndarray(y.shape, dtype=y.dtype, buffer=shm_y.buf)

            np.copyto(X_shared, X)
            np.copyto(y_shared, y)

            with Manager() as manager:
                shared_list = manager.list()
                tasks = []
                for l in range(n_dims):
                    tasks.append(
                        (
                            [l],
                            shm_X.name,
                            shm_y.name,
                            shared_list,
                            n_records,
                            n_dims,
                            self.weak_cls_type,
                            self.weak_cls_params,
                        )
                    )

                if self.weak_cls_schedule >= 2:
                    for i in range(n_dims):
                        for j in range(i + 1, n_dims):
                            tasks.append(
                                (
                                    [i, j],
                                    shm_X.name,
                                    shm_y.name,
                                    shared_list,
                                    n_records,
                                    n_dims,
                                    self.weak_cls_type,
                                    self.weak_cls_params,
                                )
                            )

                if self.weak_cls_schedule >= 3:
                    for i in range(n_dims):
                        for j in range(i + 1, n_dims):
                            for k in range(j + 1, n_dims):
                                tasks.append(
                                    (
                                        [i, j, k],
                                        shm_X.name,
                                        shm_y.name,
                                        shared_list,
                                        n_records,
                                        n_dims,
                                        self.weak_cls_type,
                                        self.weak_cls_params,
                                    )
                                )

                with Pool(processes=num_workers) as pool:
                    results = pool.starmap(
                        self._train_weak_classifier_shm, tasks
                    )
                    pool.close()
                    pool.join()

                for item in list(shared_list):
                    self.ind_list.append(item[0])
                    self.h_list.append(item[1])

            shm_X.close()
            shm_X.unlink()
            shm_y.close()
            shm_y.unlink()

    def _infer_one_weak_classifier(self, cls_ind, X_subset):
        return self.h_list[cls_ind].predict(X_subset)

    def _infer_weak_classifiers(self, X):
        n_classifiers = len(self.h_list)
        num_workers = self.weak_cls_num_jobs
        print(f"Using {num_workers} workers for inference.")

        set_start_method("fork", force=True)

        tasks = []
        for i in range(n_classifiers):
            tasks.append((i, X[:, self.ind_list[i]]))

        with Pool(processes=num_workers) as pool:
            results = pool.starmap(self._infer_one_weak_classifier, tasks)

        return list(results)

    def fit(self, X, y):
        """
        Build a QBoost classifier from the training set (X, y).

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

        self.classes_ = set(y)

        J, C, sum_constraint = self.get_hamiltonian(X, y)

        assert J.shape[0] == J.shape[1], "Inconsistent hamiltonian size!"
        assert J.shape[0] == C.shape[0], "Inconsistent hamiltonian size!"

        self.set_model(J, C, sum_constraint)

        sol, response = self.solve()

        assert len(sol) == C.shape[0], "Inconsistent solution size!"

        self.params = self.convert_sol_to_params(sol)

        assert len(self.params) == len(self.h_list), "Inconsistent size!"

        return response

    def predict_raw(self, X: np.array):
        """
        Predict raw output of the classifier for input X.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)

        Returns
        -------
        y : ndarray of shape (n_samples,)
        The predicted raw output of the classifier.
        """

        n_records = X.shape[0]
        n_classifiers = len(self.h_list)

        y = np.zeros(shape=(n_records), dtype=np.float32)
        h_vals = np.array(
            [
                self.h_list[i].predict(X[:, self.ind_list[i]])
                for i in range(n_classifiers)
            ]
        )

        y = np.tensordot(self.params, h_vals, axes=(0, 0))

        return y

    def predict(self, X: np.array, threshold=0):
        """
        Predict classes for X.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)

        threshold: Prediction threshold.

        Returns
        -------
        y : ndarray of shape (n_samples,)
        The predicted classes.
        """

        y = self.predict_raw(X)

        y[y < threshold] = -1
        y[y >= threshold] = 1

        return y

    @timer
    def get_hamiltonian(
        self,
        X: np.array,
        y: np.array,
    ):
        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=np.float32)

        if self.weak_cls_strategy == "multi_processing":
            self._build_weak_classifiers_mp(X, y)
        elif self.weak_cls_strategy == "multi_processing_shm":
            self._build_weak_classifiers_shm(X, y)
        elif self.weak_cls_strategy == "sequential":
            self._build_weak_classifiers_sq(X, y)

        print("Built %d weak classifiers!" % len(self.h_list))

        n_classifiers = len(self.h_list)
        n_records = X.shape[0]
        h_vals = np.array(
            [
                self.h_list[i].predict(X[:, self.ind_list[i]])
                for i in range(n_classifiers)
            ]
        )

        J = np.tensordot(h_vals, h_vals, axes=(1, 1))
        J = J.astype(np.float64)
        J += np.diag(self.lambda_coef * np.ones((n_classifiers)))
        C = -2.0 * np.tensordot(h_vals, y, axes=(1, 0))

        # J, C = get_hamiltonian_pyx(y, h_vals, self.lambda_coef, n_records)

        C = C.reshape((n_classifiers, 1))

        return J, C, 1.0

    def convert_sol_to_params(self, sol):
        return np.array(sol)
