# (C) Quantum Computing Inc., 2024.
import os
from collections import Counter
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    accuracy_score,
)

from eqc_models.ml.classifierqboost import QBoostClassifier

# Parameters
TEST_SIZE = 0.2
SOLVER_ACCESS = "cloud"
IP_ADDR = os.environ.get("DEVICE_IP_ADDRESS", "172.18.41.58")
PORT = os.environ.get("DEVICE_PORT", "50051")

# Read dataset
iris = datasets.load_iris()
X = iris.data
y = iris.target

# Preprocess: binary classification (class 0 → -1, class 2 → 1)
mask = y != 1
X = X[mask]
y = y[mask]
y = np.where(y == 0, -1, 1)

scaler = MinMaxScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=42,
)

# Weak classifier options and parameters
weak_cls_options = {
    "dct": {"max_depth": 3},
    "nb": {},
    "lg": {"solver": "liblinear", "max_iter": 200},
    "gp": {"max_iter_predict": 100},
    "knn": {"n_neighbors": 3},
    "lda": {
        "solver": "svd",
        "shrinkage": None,
        "tol": 1.0e-4,
    },
    "qda": {
        "reg_param": 0.0,
        "store_covariance": False,
        "tol": 1.0e-4,
    },
    "lgb": {"n_estimators": 10, "verbosity": -1},
    "xgb": {
        "n_estimators": 10,
        "verbosity": 0,
    },
}

summary = []

# Loop over all weak classifiers
for weak_cls_type, weak_cls_params in weak_cls_options.items():
    print(f"\n--- Testing weak_cls_type: {weak_cls_type.upper()} ---")

    obj = QBoostClassifier(
        relaxation_schedule=2,
        num_samples=1,
        solver_access=SOLVER_ACCESS,
        ip_addr=IP_ADDR,
        port=PORT,
        lambda_coef=0.0,
        weak_cls_schedule=2,
        weak_cls_type=weak_cls_type,
        weak_cls_params=weak_cls_params,
        weak_cls_strategy="sequential",
    )

    obj.fit(X_train, y_train)

    y_train_prd = obj.predict(X_train)
    y_test_prd = obj.predict(X_test)

    print(Counter(y_train_prd))
    print(Counter(y_test_prd))

    print(
        "Train precision:",
        precision_score(y_train, y_train_prd, pos_label=1),
    )
    print("Train recall:", recall_score(y_train, y_train_prd, pos_label=1))
    print("Train accuracy:", accuracy_score(y_train, y_train_prd))
    print(
        "Train confusion matrix:\n",
        confusion_matrix(y_train, y_train_prd, labels=[-1, 1]),
    )

    print(
        "Test precision:", precision_score(y_test, y_test_prd, pos_label=1)
    )
    print("Test recall:", recall_score(y_test, y_test_prd, pos_label=1))
    print("Test accuracy:", accuracy_score(y_test, y_test_prd))
    print(
        "Test confusion matrix:\n",
        confusion_matrix(y_test, y_test_prd, labels=[-1, 1]),
    )

    summary.append(
        {
            "weak_cls_type": weak_cls_type,
            "train_accuracy": accuracy_score(y_train, y_train_prd),
            "train_precision": precision_score(
                y_train, y_train_prd, pos_label=1
            ),
            "train_recall": recall_score(
                y_train, y_train_prd, pos_label=1
            ),
            "test_accuracy": accuracy_score(y_test, y_test_prd),
            "test_precision": precision_score(
                y_test, y_test_prd, pos_label=1
            ),
            "test_recall": recall_score(y_test, y_test_prd, pos_label=1),
        }
    )

# Summary table
print("\n=== Summary ===")
df_summary = pd.DataFrame(summary)
print(df_summary.to_string(index=False))
