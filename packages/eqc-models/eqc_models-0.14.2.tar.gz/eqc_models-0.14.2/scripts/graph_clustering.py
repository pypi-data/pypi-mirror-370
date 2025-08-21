import os
import networkx as nx
import matplotlib.pyplot as plt
from eqc_models.ml.clustering import GraphClustering

# Set parameters
SOLVER_ACCESS = "cloud"
IP_ADDR = os.eviron.get("DEVICE_IP_ADDRESS", "172.18.41.58")
PORT = os.environ.get("DEVICE_PORT", "50051")

# Create an empty graph
G = nx.Graph()

# Add nodes and weighted edges to create three distinct partitions
# Partition 1
G.add_edge(1, 2, weight=5)
G.add_edge(2, 3, weight=3)
G.add_edge(1, 3, weight=4)

# Partition 2
G.add_edge(4, 5, weight=6)
G.add_edge(5, 6, weight=2)
G.add_edge(4, 6, weight=7)

# Partition 3
G.add_edge(7, 8, weight=8)
G.add_edge(8, 9, weight=1)
G.add_edge(7, 9, weight=5)

# Add a few edges with lower weights between the partitions to maintain separateness
G.add_edge(3, 4, weight=0.5)
G.add_edge(6, 7, weight=0.5)

# Cluster
obj = GraphClustering(
    relaxation_schedule=2,
    num_samples=1,
    solver_access=SOLVER_ACCESS,
    ip_addr=IP_ADDR,
    port=PORT,    
    graph=G,
    num_clusters=3,
    alpha=10.0,
    device="dirac-3",    
)

labels = obj.fit_predict()

print(labels)

# Draw the graph
pos = nx.spring_layout(G)
edges = G.edges(data=True)

# Draw nodes and edges with weight labels
nx.draw(
    G,
    pos,
    with_labels=True,
    node_color="skyblue",
    node_size=1000,
    edge_color="gray",
    linewidths=1.5,
    font_size=15,
)
nx.draw_networkx_edge_labels(
    G, pos, edge_labels={(u, v): d["weight"] for u, v, d in edges}
)

# Draw the custom labels
label_hash = {}
for i in range(len(labels)):
    label_hash[i + 1] = str(labels[i])
label_pos = {
    node: (pos[node][0] + 0.05, pos[node][1] + 0.05) for node in pos
}

nx.draw_networkx_labels(
    G, label_pos, label_hash, font_size=20, font_color="red"
)

plt.show()
