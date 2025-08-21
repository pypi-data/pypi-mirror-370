import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from eqc_models.ml.clustering import GraphClustering

import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

# Add edges for carbon-carbon bonds with alternating single and double bond weights
carbon_carbon_edges = [
    (0, 1, 1),
    (1, 2, 2),
    (2, 3, 1),
    (3, 4, 2),
    (4, 5, 1),
    (5, 0, 2),
]
# Add edges for carbon-hydrogen bonds (single bonds, weight = 1)
carbon_hydrogen_edges = [
    (0, 6, 1),
    (1, 7, 1),
    (2, 8, 1),
    (3, 9, 1),
    (4, 10, 1),
    (5, 11, 1),
]

# Combine edges
edges = carbon_carbon_edges + carbon_hydrogen_edges

# Add the weighted edges to the graph
G.add_weighted_edges_from(edges)

# Cluster
obj = GraphClustering(
    relaxation_schedule=2,
    num_samples=1,
    graph=G,
    num_clusters=3,
    alpha=10.0,
)

labels = obj.fit_predict()

print(labels)

# Draw the custom labels
label_hash = {}
for i in range(len(labels)):
    label_hash[i] = str(labels[i])


# Define a function to create hexagonal layout
def hexagonal_layout():
    angle_step = 2 * np.pi / 6  # 360 degrees divided by 6 carbon atoms
    positions = {}
    for i in range(6):
        angle = i * angle_step
        positions[i] = np.array(
            [np.cos(angle), np.sin(angle)]
        )  # Carbon atoms in a hexagon
        positions[i + 6] = 1.5 * np.array(
            [np.cos(angle), np.sin(angle)]
        )  # Hydrogen atoms slightly outward
    return positions


# Get symmetrical positions for the graph
pos = hexagonal_layout()

# Draw the graph with node labels using the label_hash dictionary
nx.draw(
    G,
    pos,
    with_labels=True,
    labels=label_hash,
    node_color="lightblue",
    node_size=500,
    font_size=14,
    edge_color="black",
)

# Add the edge weights as labels
labels = nx.get_edge_attributes(G, "weight")
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

plt.show()
