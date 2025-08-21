# (C) Quantum Computing Inc., 2024.
import os
import sys
from collections import Counter
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.preprocessing import normalize
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA as PCA_cls
from eqc_models.ml.decomposition import PCA

# Set parameters
N_COMPONENTS = 4
SOLVER_ACCESS = "cloud"
IP_ADDR = os.environ.get("DEVICE_IP_ADDRESS", "172.18.41.58")
PORT = os.environ.get("DEVICE_PORT", "50051")

# Read dataset
iris = datasets.load_iris()
X = iris.data

scaler = StandardScaler()
X = scaler.fit_transform(X)

print("Input data shape:", X.shape)

# Apply PCA using QCi's model
obj = PCA(
    n_components=N_COMPONENTS,
    relaxation_schedule=2,
    num_samples=1,
    solver_access=SOLVER_ACCESS,
    ip_addr=IP_ADDR,
    port=PORT,            
)
X_pca = obj.fit_transform(X)

# Apply PCA using sklearn model
obj = PCA_cls(
    n_components=N_COMPONENTS,
)
X_pca_cls = obj.fit_transform(X)

# Compare QCi to sklearn
X_pca = normalize(X_pca, axis=0, norm="l2")
X_pca_cls = normalize(X_pca_cls, axis=0, norm="l2")

print(abs(np.diag(np.matmul(X_pca.transpose(), X_pca_cls))))
