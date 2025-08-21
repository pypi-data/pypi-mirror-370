import networkx as nx
from eqc_models.ml.clustering import GraphClustering

# Some parameters
NUM_CLUSTERS = 4
ALPHA = 20.0
DEVICE = "dirac-3"

# Get the graph
G = nx.karate_club_graph()

# Do clustering
model = GraphClustering(
    relaxation_schedule=1,
    num_samples=10,
    graph=G,
    num_clusters=NUM_CLUSTERS,
    alpha=ALPHA,
    device=DEVICE,
)

labels = model.fit_predict()

print(labels)

# Calculate modularity
print("Modularity from eqc models:", model.get_modularity())

# Classical bechmark
cls_clusters = nx.community.louvain_communities(G)
print(
    "Modularity from benchmark model:",
    nx.community.modularity(G, cls_clusters),
)
