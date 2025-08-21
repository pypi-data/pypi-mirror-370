# (C) Quantum Computing Inc., 2024.
import os
import sys
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

from eqc_models.ml.classifierqsvm import QSVMClassifierDual as QSVMClassifier

# Set parameters
TEST_SIZE = 0.2
SOLVER_ACCESS = "cloud"
IP_ADDR = os.environ.get("DEVICE_IP_ADDRESS", "172.18.41.58")
PORT = os.environ.get("DEVICE_PORT", "50051")

# Read dataset
iris = datasets.load_iris()
X = iris.data
y = iris.target

# Pre-Process
scaler = MinMaxScaler()
X = scaler.fit_transform(X)

for i in range(len(y)):
    if y[i] == 0:
        y[i] = -1
    elif y[i] == 2:
        y[i] = 1

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=42,
)
print(Counter(y_train))
print(X_train.shape)
print(y_train.shape)

print(Counter(y_test))
print(X_test.shape)
print(y_test.shape)

# Get QSVM model
obj = QSVMClassifier(
    relaxation_schedule=1,
    num_samples=1,
    solver_access=SOLVER_ACCESS,
    ip_addr=IP_ADDR,
    port=PORT,            
    upper_limit=1.0,
    gamma=1.0,
    eta=1.0,
    zeta=1.0,
)

# Train
obj.fit(X_train, y_train)

y_train_prd = obj.predict(X_train)
y_test_prd = obj.predict(X_test)

print(Counter(y_train_prd))
print(Counter(y_test_prd))

print(
    "Train precision:",
    precision_score(y_train, y_train_prd, labels=[-1, 1], pos_label=1),
)
print(
    "Train recall:",
    recall_score(y_train, y_train_prd, labels=[-1, 1], pos_label=1),
)
print(
    "Train accuracy:",
    accuracy_score(y_train, y_train_prd),
)
print(
    "Train confusion matrix:",
    confusion_matrix(y_train, y_train_prd, labels=[-1, 1]),
)

print(
    "Test precision:",
    precision_score(y_test, y_test_prd, labels=[-1, 1], pos_label=1),
)
print(
    "Test recall:",
    recall_score(y_test, y_test_prd, labels=[-1, 1], pos_label=1),
)
print(
    "Test accuracy:",
    accuracy_score(y_test, y_test_prd),
)
print(
    "Test confusion matrix:",
    confusion_matrix(y_test, y_test_prd, labels=[-1, 1]),
)
