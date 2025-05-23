import json
import csv
import random
from fa2_modified import ForceAtlas2
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from pathlib import Path
import pandas as pd
from collections import defaultdict

# Import settings
from settings import DATA_FOLDER

to_add_manually = ["philip francis", "john scott"]


# Define file paths
graph_file = DATA_FOLDER / "articles_India/articles_India_with_persons.jsonl"
clustering_file = DATA_FOLDER / "articles_India/clustering_india.jsonl"
cluster_names_file = DATA_FOLDER / "articles_India/clustering.csv"
output_visualization = DATA_FOLDER / "articles_India/india_network_visualization.png"

# Load the graph from JSONL
def load_graph_from_jsonl(file_path):
    G = nx.Graph()
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line)
            persons = data.get("persons", [])
            
            if len(persons) >= 2:
                for i in range(len(persons)):
                    for j in range(i+1, len(persons)):
                        person1, person2 = persons[i], persons[j]
                        if G.has_edge(person1, person2):
                            G[person1][person2]['weight'] += 1
                        else:
                            G.add_edge(person1, person2, weight=1)
    
    # Filter nodes with minimum connections
    avg_weights = {}
    for node in G.nodes():
        weights = [data['weight'] for _, _, data in G.edges(node, data=True)]
        avg_weights[node] = max(weights)
    min_connections = 30  # Threshold for number of connections
    min_avg_weight = 2    # Threshold for average edge weight - adjust as needed
    
    nodes_to_remove = [node for node in G.nodes() if G.degree(node) < min_connections]
    G.remove_nodes_from(nodes_to_remove)

    nodes_to_remove = [node for node in G.nodes() if avg_weights[node] < min_avg_weight]
    G.remove_nodes_from(nodes_to_remove)
    
    # Add attributes
    for node in G.nodes():
        G.nodes[node]['label'] = node
        G.nodes[node]['degree'] = G.degree(node)
        G.nodes[node]['weighted_degree'] = sum(data['weight'] for _, _, data in G.edges(node, data=True))
    
    return G

# Load community data
def load_communities(file_path):
    communities = {}
    node_to_community = {}
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line)
            community_id = data["community_id"]
            nodes = data["nodes"]
            communities[community_id] = nodes
            
            for node in nodes:
                node_to_community[node] = community_id
    
    return communities, node_to_community

# Load cluster names from CSV
def load_cluster_names(file_path):
    cluster_names = {}
    
    try:
        # Try pandas first for more robust CSV handling
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            cluster_names[int(row['Cluster ID'])] = row['Cluster Name']
    except (FileNotFoundError, KeyError) as e:
        print(f"Warning: Could not load cluster names: {e}")
        print("Creating visualization without cluster names.")
    
    return cluster_names

def apply_community_based_layout(G, node_to_community, iterations=4000):
    """
    Apply ForceAtlas2 layout algorithm with community-aware settings.
    
    Parameters:
    -----------
    G : networkx.Graph
        The input graph
    node_to_community : dict
        Dictionary mapping nodes to their community IDs
    iterations : int, default=2000
        Number of iterations for the ForceAtlas2 algorithm
    
    Returns:
    --------
    dict
        Dictionary of node positions (x, y) indexed by node name
    """
    print("Applying ForceAtlas2 layout...")
    
    # Initialize ForceAtlas2 with community-friendly settings
    forceatlas2 = ForceAtlas2(
        # Behavior alternatives
        outboundAttractionDistribution=True,   # Helps distribute hubs to borders
        linLogMode=False,                      # Keep linear mode for community structure
        adjustSizes=False,                     # Not implemented in fa2
        edgeWeightInfluence=1.0,              # Use edge weights if available
        
        # Performance settings
        jitterTolerance=1.0,                  # Standard tolerance
        barnesHutOptimize=True,               # Enable for better performance on large graphs
        barnesHutTheta=1.2,                   # Good balance of speed vs accuracy
        multiThreaded=False,                  # Not implemented in fa2
        
        # Tuning for community structure - MODIFIED FOR BETTER SEPARATION
        scalingRatio=10.0,                     # INCREASED: Stronger repulsion pushes communities apart
        strongGravityMode=False,              # Let communities form naturally
        gravity=0.3,                          # REDUCED: Less gravity allows communities to spread out
        
        # Logging
        verbose=True                          # Show progress
    )
    
    # Get initial positions using a quick spring layout
    print("Generating initial positions...")
    initial_pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    # Apply ForceAtlas2 layout
    positions = forceatlas2.forceatlas2_networkx_layout(
        G, 
        pos=initial_pos,
        iterations=iterations
    )
    
    print(f"Layout completed with {iterations} iterations")
    return positions

# Main visualization function
def visualize_graph_with_communities():
    # Load data
    print("Loading graph...")
    G = load_graph_from_jsonl(graph_file)
    print(f"Graph loaded with {len(G.nodes())} nodes and {len(G.edges())} edges")
    
    print("Loading communities...")
    communities, node_to_community = load_communities(clustering_file)
    print(f"Loaded {len(communities)} communities")
    
    print("Loading cluster names...")
    cluster_names = load_cluster_names(cluster_names_file)
    
    # Apply community information to nodes
    for node in G.nodes():
        if node in node_to_community:
            G.nodes[node]['community'] = node_to_community[node]
        else:
            G.nodes[node]['community'] = -1  # No community assigned
    
    # Calculate layout using modified spring layout
    print("Calculating layout using community-based layout...")
    pos = apply_community_based_layout(G, node_to_community)
    
    # Setup visualization
    print("Creating visualization...")
    plt.figure(figsize=(20, 20))
    
    # Generate colors for communities
    num_communities = len(communities)
    colors = cm.rainbow(np.linspace(0, 1, num_communities))
    community_colors = {comm_id: colors[i] for i, comm_id in enumerate(communities.keys())}
    
    # Draw edges with transparency based on weight
    max_weight = max([d['weight'] for _, _, d in G.edges(data=True)])
    for u, v, d in G.edges(data=True):
        alpha = 0.1 + 0.9 * (d['weight'] / max_weight)  # Scale alpha between 0.1 and 1.0
        width = 0.5 + 4.5 * (d['weight'] / max_weight)  # Scale width between 0.5 and 5.0
        plt.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                 color='gray', alpha=alpha, linewidth=width, zorder=1)
    
    # Draw nodes colored by community
    for comm_id, nodes in communities.items():
        # Get nodes that both exist in the graph and in this community
        community_nodes = [node for node in nodes if node in G.nodes()]
        if not community_nodes:
            continue
        
        # Draw nodes for this community
        node_size = [20 + G.nodes[node]['weighted_degree'] / 10 for node in community_nodes]
        nx.draw_networkx_nodes(G, pos, 
                              nodelist=community_nodes,
                              node_size=node_size,
                              node_color=[community_colors[comm_id]],
                              alpha=0.8,
                              #zorder=2
                              )
    
    # Draw node labels for high-degree nodes only
    degree_threshold = max([G.nodes[node]['degree'] for node in G.nodes()]) / 3
    labels = {node: G.nodes[node]['label'] for node in G.nodes() 
            if G.nodes[node]['degree'] > degree_threshold or node in to_add_manually}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold') #zorder=3)
    
    # Draw community labels
    for comm_id, nodes in communities.items():
        community_nodes = [node for node in nodes if node in G.nodes()]
        if not community_nodes:
            continue
            
        # Calculate the centroid of the community
        centroid_x = sum(pos[node][0] for node in community_nodes) / len(community_nodes)
        centroid_y = sum(pos[node][1] for node in community_nodes) / len(community_nodes)
        
        # Get cluster name if available
        cluster_name = cluster_names.get(comm_id, f"Community {comm_id}")
        cluster_name  = f"{comm_id}: {cluster_name}"
        
        # Add a background box for better visibility
        plt.text(centroid_x, centroid_y, cluster_name, 
                 fontsize=14, fontweight='bold', 
                 ha='center', va='center',
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor=community_colors[comm_id], boxstyle='round,pad=0.5'),
                 zorder=4)
    
    # Set plot properties
    plt.title("India News Network - Person Co-occurrences", fontsize=20)
    plt.axis('off')
    plt.tight_layout()
    
    # Save the figure
    print(f"Saving visualization to {output_visualization}...")
    plt.savefig(output_visualization, dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualization complete!")

if __name__ == "__main__":
    visualize_graph_with_communities()