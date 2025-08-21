import networkx as nx
import numpy as np
from eqc_models.graph.partition import GraphPartitionModel

# Example graph
G = nx.Graph()
G.add_edges_from([(0, 1, {"weight": 1.0}), (1, 2, {"weight": 1.0}), (2, 0, {"weight": 1.0})])

# Instantiate the model
partition_model = GraphPartitionModel(G, k=3, alpha=1.0, gamma=1.0)

# Get linear and quadratic components
h, J = partition_model.costFunction()

# Example solution vector for 3 partitions
solution = np.random.randint(0, 2, size=(partition_model.num_nodes * 3,))
decoded_solution = partition_model.decode(solution)

print("Objective Matrix:\n", partition_model.objective_matrix.toarray())
print("Linear Term (h):", h)
print("Decoded Solution:", decoded_solution)
