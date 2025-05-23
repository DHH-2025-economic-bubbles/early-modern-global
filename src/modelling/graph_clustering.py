from itertools import combinations
import json
import networkx as nx
import community as community_louvain
import random

from settings import DATA_FOLDER
input_file = DATA_FOLDER / "articles_India/articles_India_with_persons.jsonl"
output_file = DATA_FOLDER/ "articles_India/clustering_india.jsonl"

# Load the GEXF file
# Build the graph directly from JSONL
G = nx.Graph()

with open(input_file, 'r', encoding='utf-8') as file:
    for line in file:
        data = json.loads(line)
        persons = data.get("persons", [])
        
        if len(persons) >= 2:
            for person1, person2 in combinations(persons, 2):
                if G.has_edge(person1, person2):
                    G[person1][person2]['weight'] += 1
                else:
                    G.add_edge(person1, person2, weight=1)

# Filter nodes with minimum connections
min_connections = 3  # Threshold for number of connections
min_avg_weight = 2    # Threshold for average edge weight - adjust as needed
avg_weights = {}
for node in G.nodes():
    weights = [data['weight'] for _, _, data in G.edges(node, data=True)]
    avg_weights[node] = max(weights)
nodes_to_remove = [node for node in G.nodes() if G.degree(node) < min_connections]
G.remove_nodes_from(nodes_to_remove)

nodes_to_remove = [node for node in G.nodes() if avg_weights[node] < min_avg_weight]
G.remove_nodes_from(nodes_to_remove)

nodes_to_remove = [node for node in G.nodes() if G.degree(node) < 2]
G.remove_nodes_from(nodes_to_remove)
print(f"Filtered graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

# Add attributes
for node in G.nodes():
    G.nodes[node]['label'] = node  # Ensure label attribute exists
    G.nodes[node]['degree'] = G.degree(node)
    G.nodes[node]['weighted_degree'] = sum(data['weight'] for _, _, data in G.edges(node, data=True))

# Convert to undirected graph if needed (Louvain works on undirected graphs)
if nx.is_directed(G):
    G = G.to_undirected()

# Randomize the node order
nodes = list(G.nodes())
random.shuffle(nodes)

# Apply community detection with resolution parameter
resolution = 1
partition = community_louvain.best_partition(G)#, weight='weighted_degree', resolution=resolution, random_state=random.randint(0, 2**32 - 1))

# Organize nodes by community
communities = {}
for node, community_id in partition.items():
    if community_id not in communities:
        communities[community_id] = []
    communities[community_id].append(node)  # Use node as label since we know it's the person's name

# Output each community and its nodes
for community_id, node_labels in communities.items():
    print(f"Community {community_id}:")
    print(node_labels)

# Save communities to file
with open(output_file, 'w', encoding='utf-8') as f:
    for community_id, nodes in communities.items():
        community_data = {
            "community_id": community_id,
            "nodes": nodes
        }
        f.write(json.dumps(community_data) + '\n')

