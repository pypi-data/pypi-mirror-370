import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from eqc_models.ml.clustering import Clustering

# Set parameters
SOLVER_ACCESS = "cloud"
IP_ADDR = os.environ.get("DEVICE_IP_ADDRESS", "172.18.41.58")
PORT = os.environ.get("DEVICE_PORT", "50051")

# Generate dataset
np.random.seed(42)

cluster1 = np.random.randn(15, 2) * 0.5 + np.array([2, 2])
cluster2 = np.random.randn(15, 2) * 0.5 + np.array([8, 3])
cluster3 = np.random.randn(15, 2) * 0.5 + np.array([5, 8])

X = np.vstack((cluster1, cluster2, cluster3))

# Cluster
obj = Clustering(
    num_clusters=3,
    relaxation_schedule=1,
    num_samples=1,
    solver_access=SOLVER_ACCESS,
    ip_addr=IP_ADDR,
    port=PORT,
    alpha=500.0,
    distance_func="squared_l2_norm",
    device="dirac-3",
)

labels = obj.fit_predict(X)

print(labels)

print(len(labels), X.shape)

# Plot the data points
color_hash = {1: "red", 2: "blue", 3: "green"}

for i in range(X.shape[0]):
    label = labels[i]
    plt.scatter(X[i][0], X[i][1], color=color_hash[label])

title = " ; ".join(
    ["label %s: %s" % (label, color_hash[label]) for label in set(labels)]
)

plt.xlabel("Feature x")
plt.ylabel("Feature y")
plt.title(title)
plt.grid(True)
plt.show()
