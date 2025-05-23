import json
import numpy as np
from matplotlib import pyplot as plt
import networkx as nx
from itertools import combinations
from pathlib import Path
from tqdm import tqdm
import pandas as pd

from settings import DATA_FOLDER


def calculate_person_metrics(G, person_of_interest):
    """Calculate comprehensive metrics for a specific person and compare to network averages."""
    if person_of_interest not in G.nodes():
        return None
    
    metrics = {'person': person_of_interest}
    
    # Basic connectivity metrics
    metrics['degree'] = G.degree(person_of_interest)
    metrics['weighted_degree'] = sum(data['weight'] for _, _, data in G.edges(person_of_interest, data=True))
    
    # Centrality measures
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)
    eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
    pagerank = nx.pagerank(G, weight='weight')
    
    metrics['betweenness_centrality'] = betweenness[person_of_interest]
    metrics['closeness_centrality'] = closeness[person_of_interest]
    metrics['eigenvector_centrality'] = eigenvector[person_of_interest]
    metrics['pagerank'] = pagerank[person_of_interest]
    
    # Local clustering
    metrics['clustering_coefficient'] = nx.clustering(G, person_of_interest)
    
    # Connection strength analysis
    edge_weights = [data['weight'] for _, _, data in G.edges(person_of_interest, data=True)]
    if edge_weights:
        metrics['avg_connection_strength'] = np.mean(edge_weights)
        metrics['max_connection_strength'] = max(edge_weights)
        metrics['min_connection_strength'] = min(edge_weights)
        metrics['connection_strength_std'] = np.std(edge_weights)
    else:
        metrics['avg_connection_strength'] = 0
        metrics['max_connection_strength'] = 0
        metrics['min_connection_strength'] = 0
        metrics['connection_strength_std'] = 0
    
    # Network position analysis
    all_degrees = [d for n, d in G.degree()]
    all_weighted_degrees = [sum(data['weight'] for _, _, data in G.edges(node, data=True)) 
                           for node in G.nodes()]
    all_betweenness = list(betweenness.values())
    all_closeness = list(closeness.values())
    all_eigenvector = list(eigenvector.values())
    all_clustering = list(nx.clustering(G).values())
    
    # Percentile rankings
    metrics['degree_percentile'] = (sum(1 for d in all_degrees if d < metrics['degree']) / len(all_degrees)) * 100
    metrics['weighted_degree_percentile'] = (sum(1 for d in all_weighted_degrees if d < metrics['weighted_degree']) / len(all_weighted_degrees)) * 100
    metrics['betweenness_percentile'] = (sum(1 for b in all_betweenness if b < metrics['betweenness_centrality']) / len(all_betweenness)) * 100
    metrics['closeness_percentile'] = (sum(1 for c in all_closeness if c < metrics['closeness_centrality']) / len(all_closeness)) * 100
    metrics['eigenvector_percentile'] = (sum(1 for e in all_eigenvector if e < metrics['eigenvector_centrality']) / len(all_eigenvector)) * 100
    metrics['clustering_percentile'] = (sum(1 for c in all_clustering if c < metrics['clustering_coefficient']) / len(all_clustering)) * 100
    
    # Comparison to network averages
    metrics['degree_vs_avg'] = metrics['degree'] / np.mean(all_degrees)
    metrics['weighted_degree_vs_avg'] = metrics['weighted_degree'] / np.mean(all_weighted_degrees)
    metrics['betweenness_vs_avg'] = metrics['betweenness_centrality'] / np.mean(all_betweenness) if np.mean(all_betweenness) > 0 else 0
    metrics['closeness_vs_avg'] = metrics['closeness_centrality'] / np.mean(all_closeness)
    metrics['eigenvector_vs_avg'] = metrics['eigenvector_centrality'] / np.mean(all_eigenvector) if np.mean(all_eigenvector) > 0 else 0
    metrics['clustering_vs_avg'] = metrics['clustering_coefficient'] / np.mean(all_clustering) if np.mean(all_clustering) > 0 else 0
    
    # Network neighborhood analysis
    neighbors = list(G.neighbors(person_of_interest))
    metrics['num_neighbors'] = len(neighbors)
    
    if neighbors:
        # Analyze the person's neighborhood
        neighbor_degrees = [G.degree(neighbor) for neighbor in neighbors]
        neighbor_weighted_degrees = [sum(data['weight'] for _, _, data in G.edges(neighbor, data=True)) 
                                   for neighbor in neighbors]
        
        metrics['avg_neighbor_degree'] = np.mean(neighbor_degrees)
        metrics['max_neighbor_degree'] = max(neighbor_degrees)
        metrics['avg_neighbor_weighted_degree'] = np.mean(neighbor_weighted_degrees)
        
        # How well-connected are the person's neighbors to each other?
        neighbor_subgraph = G.subgraph(neighbors)
        metrics['neighbor_density'] = nx.density(neighbor_subgraph)
        metrics['neighbor_clustering'] = nx.average_clustering(neighbor_subgraph)
    else:
        metrics['avg_neighbor_degree'] = 0
        metrics['max_neighbor_degree'] = 0
        metrics['avg_neighbor_weighted_degree'] = 0
        metrics['neighbor_density'] = 0
        metrics['neighbor_clustering'] = 0
    
    return metrics



def analyze_person_influence(G, person_of_interest, top_n=10):
    """Analyze a person's influence and key connections in the network."""
    if person_of_interest not in G.nodes():
        return None
    
    analysis = {'person': person_of_interest}
    
    # Get all connections with weights
    connections = []
    for neighbor in G.neighbors(person_of_interest):
        weight = G[person_of_interest][neighbor]['weight']
        neighbor_degree = G.degree(neighbor)
        neighbor_weighted_degree = sum(data['weight'] for _, _, data in G.edges(neighbor, data=True))
        
        connections.append({
            'person': neighbor,
            'connection_strength': weight,
            'neighbor_degree': neighbor_degree,
            'neighbor_weighted_degree': neighbor_weighted_degree,
            'influence_score': weight * neighbor_degree  # Combined metric
        })
    
    # Sort by different criteria
    analysis['strongest_connections'] = sorted(connections, key=lambda x: x['connection_strength'], reverse=True)[:top_n]
    analysis['most_influential_connections'] = sorted(connections, key=lambda x: x['influence_score'], reverse=True)[:top_n]
    analysis['most_connected_neighbors'] = sorted(connections, key=lambda x: x['neighbor_degree'], reverse=True)[:top_n]
    
    # Calculate influence metrics
    total_influence = sum(conn['influence_score'] for conn in connections)
    analysis['total_influence_score'] = total_influence
    analysis['avg_influence_per_connection'] = total_influence / len(connections) if connections else 0
    
    return analysis


def print_person_analysis(person_metrics, influence_analysis, graph_name):
    """Print comprehensive analysis for a person of interest."""
    if person_metrics is None:
        print(f"Person not found in {graph_name} network.")
        return
    
    person = person_metrics['person']
    
    print(f"\n{'='*80}")
    print(f"INDIVIDUAL ANALYSIS: {person} in {graph_name}")
    print(f"{'='*80}")
    
    # Basic connectivity
    print(f"\nBASIC CONNECTIVITY:")
    print(f"• Degree (connections): {person_metrics['degree']}")
    print(f"• Weighted degree: {person_metrics['weighted_degree']}")
    print(f"• Average connection strength: {person_metrics['avg_connection_strength']:.2f}")
    print(f"• Strongest connection: {person_metrics['max_connection_strength']}")
    
    # Network position
    print(f"\nNETWORK POSITION (Percentiles):")
    print(f"• Degree: {person_metrics['degree_percentile']:.1f}th percentile")
    print(f"• Weighted degree: {person_metrics['weighted_degree_percentile']:.1f}th percentile")
    print(f"• Betweenness centrality: {person_metrics['betweenness_percentile']:.1f}th percentile")
    print(f"• Closeness centrality: {person_metrics['closeness_percentile']:.1f}th percentile")
    print(f"• Eigenvector centrality: {person_metrics['eigenvector_percentile']:.1f}th percentile")
    
    # Relative to network average
    print(f"\nCOMPARISON TO NETWORK AVERAGE:")
    print(f"• Degree: {person_metrics['degree_vs_avg']:.2f}x average")
    print(f"• Weighted degree: {person_metrics['weighted_degree_vs_avg']:.2f}x average")
    print(f"• Betweenness centrality: {person_metrics['betweenness_vs_avg']:.2f}x average")
    print(f"• Closeness centrality: {person_metrics['closeness_vs_avg']:.2f}x average")
    print(f"• Clustering coefficient: {person_metrics['clustering_vs_avg']:.2f}x average")
    
    # Neighborhood analysis
    print(f"\nNEIGHBORHOOD ANALYSIS:")
    print(f"• Number of direct neighbors: {person_metrics['num_neighbors']}")
    print(f"• Average neighbor degree: {person_metrics['avg_neighbor_degree']:.1f}")
    print(f"• Most connected neighbor has {person_metrics['max_neighbor_degree']} connections")
    print(f"• Neighborhood density: {person_metrics['neighbor_density']:.3f}")
    print(f"• Neighborhood clustering: {person_metrics['neighbor_clustering']:.3f}")
    
    # Influence analysis
    if influence_analysis:
        print(f"\nINFLUENCE ANALYSIS:")
        print(f"• Total influence score: {influence_analysis['total_influence_score']:.0f}")
        print(f"• Average influence per connection: {influence_analysis['avg_influence_per_connection']:.1f}")
        
        print(f"\nSTRONGEST CONNECTIONS:")
        for i, conn in enumerate(influence_analysis['strongest_connections'][:5], 1):
            print(f"{i:2d}. {conn['person']} (strength: {conn['connection_strength']}, degree: {conn['neighbor_degree']})")
        
        print(f"\nMOST INFLUENTIAL CONNECTIONS:")
        for i, conn in enumerate(influence_analysis['most_influential_connections'][:5], 1):
            print(f"{i:2d}. {conn['person']} (influence: {conn['influence_score']:.0f}, strength: {conn['connection_strength']})")



def build_graph(input_file, min_connections=30, min_avg_weight=2):
    """Build and filter a graph from the input file."""
    G = nx.Graph()
    
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in tqdm(file, desc=f"Building graph from {input_file.name}"):
            data = json.loads(line)
            persons = data.get("persons", [])
            
            if len(persons) >= 2:
                for person1, person2 in combinations(persons, 2):
                    if G.has_edge(person1, person2):
                        G[person1][person2]['weight'] += 1
                    else:
                        G.add_edge(person1, person2, weight=1)
    
    print(f"Original graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Calculate max weights for each node
    avg_weights = {}
    for node in G.nodes():
        weights = [data['weight'] for _, _, data in G.edges(node, data=True)]
        avg_weights[node] = max(weights) if weights else 0
    
    # Filter nodes
    nodes_to_remove = [node for node in G.nodes() if G.degree(node) < min_connections]
    G.remove_nodes_from(nodes_to_remove)

    nodes_to_remove = [node for node in G.nodes() if avg_weights.get(node, 0) < min_avg_weight]
    G.remove_nodes_from(nodes_to_remove)
    
    print(f"Filtered graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Add attributes
    for node in G.nodes():
        G.nodes[node]['degree'] = G.degree(node)
        G.nodes[node]['weighted_degree'] = sum(data['weight'] for _, _, data in G.edges(node, data=True))
    
    return G


def calculate_graph_metrics(G, graph_name):
    """Calculate comprehensive metrics for a graph."""
    metrics = {'graph_name': graph_name}
    
    # Basic metrics
    metrics['num_nodes'] = G.number_of_nodes()
    metrics['num_edges'] = G.number_of_edges()
    
    if metrics['num_nodes'] == 0:
        return metrics
    
    # Density
    metrics['density'] = nx.density(G)
    
    # Connectivity
    metrics['is_connected'] = nx.is_connected(G)
    metrics['num_components'] = nx.number_connected_components(G)
    
    if metrics['is_connected']:
        metrics['diameter'] = nx.diameter(G)
        metrics['avg_path_length'] = nx.average_shortest_path_length(G)
    else:
        # For disconnected graphs, calculate for largest component
        largest_cc = max(nx.connected_components(G), key=len)
        subgraph = G.subgraph(largest_cc)
        metrics['diameter'] = nx.diameter(subgraph)
        metrics['avg_path_length'] = nx.average_shortest_path_length(subgraph)
        metrics['largest_component_size'] = len(largest_cc)
        metrics['largest_component_fraction'] = len(largest_cc) / metrics['num_nodes']
    
    # Degree statistics
    degrees = [d for n, d in G.degree()]
    metrics['avg_degree'] = np.mean(degrees)
    metrics['median_degree'] = np.median(degrees)
    metrics['max_degree'] = max(degrees)
    metrics['min_degree'] = min(degrees)
    metrics['degree_std'] = np.std(degrees)
    
    # Weighted degree statistics
    weighted_degrees = [sum(data['weight'] for _, _, data in G.edges(node, data=True)) 
                       for node in G.nodes()]
    metrics['avg_weighted_degree'] = np.mean(weighted_degrees)
    metrics['median_weighted_degree'] = np.median(weighted_degrees)
    metrics['max_weighted_degree'] = max(weighted_degrees)
    metrics['min_weighted_degree'] = min(weighted_degrees)
    
    # Centralization measures
    # Degree centralization
    max_possible_degree = metrics['num_nodes'] - 1
    degree_centralization_sum = sum(max(degrees) - d for d in degrees)
    max_centralization = (metrics['num_nodes'] - 1) * (max_possible_degree - 1)
    metrics['degree_centralization'] = degree_centralization_sum / max_centralization if max_centralization > 0 else 0
    
    # Centrality measures
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)
    eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
    
    metrics['avg_betweenness'] = np.mean(list(betweenness.values()))
    metrics['max_betweenness'] = max(betweenness.values())
    metrics['avg_closeness'] = np.mean(list(closeness.values()))
    metrics['max_closeness'] = max(closeness.values())
    metrics['avg_eigenvector'] = np.mean(list(eigenvector.values()))
    metrics['max_eigenvector'] = max(eigenvector.values())
    
    # Clustering
    metrics['avg_clustering'] = nx.average_clustering(G)
    metrics['transitivity'] = nx.transitivity(G)
    
    # Edge weight statistics
    edge_weights = [data['weight'] for _, _, data in G.edges(data=True)]
    metrics['avg_edge_weight'] = np.mean(edge_weights)
    metrics['median_edge_weight'] = np.median(edge_weights)
    metrics['max_edge_weight'] = max(edge_weights)
    metrics['total_edge_weight'] = sum(edge_weights)
    
    # Small world properties
    # Compare clustering and path length to random graph
    random_G = nx.erdos_renyi_graph(metrics['num_nodes'], metrics['density'])
    if nx.is_connected(random_G):
        random_clustering = nx.average_clustering(random_G)
        random_path_length = nx.average_shortest_path_length(random_G)
        
        if random_clustering > 0 and random_path_length > 0:
            metrics['small_world_sigma'] = (metrics['avg_clustering'] / random_clustering) / (metrics['avg_path_length'] / random_path_length)
        else:
            metrics['small_world_sigma'] = None
    else:
        metrics['small_world_sigma'] = None
    
    return metrics


def compare_graphs(metrics1, metrics2):
    """Generate comparative analysis between two graphs."""
    comparison = {}
    
    # Basic comparison
    comparison['size_ratio'] = metrics1['num_nodes'] / metrics2['num_nodes']
    comparison['edge_ratio'] = metrics1['num_edges'] / metrics2['num_edges']
    comparison['density_ratio'] = metrics1['density'] / metrics2['density']
    
    # Centralization comparison
    comparison['centralization_diff'] = metrics1['degree_centralization'] - metrics2['degree_centralization']
    
    # Clustering comparison
    comparison['clustering_ratio'] = metrics1['avg_clustering'] / metrics2['avg_clustering']
    
    # Path length comparison (if both are connected or we have largest component data)
    if 'avg_path_length' in metrics1 and 'avg_path_length' in metrics2:
        comparison['path_length_ratio'] = metrics1['avg_path_length'] / metrics2['avg_path_length']
    
    # Degree distribution comparison
    comparison['degree_variance_ratio'] = (metrics1['degree_std'] ** 2) / (metrics2['degree_std'] ** 2)
    
    return comparison


def print_metrics_table(metrics_list):
    """Print metrics in a nice table format."""
    df = pd.DataFrame(metrics_list)
    
    # Select key metrics for display
    key_metrics = [
        'graph_name', 'num_nodes', 'num_edges', 'density', 'is_connected',
        'num_components', 'avg_degree', 'max_degree', 'degree_centralization',
        'avg_clustering', 'transitivity', 'avg_path_length', 'diameter',
        'avg_betweenness', 'max_betweenness', 'small_world_sigma'
    ]
    
    display_df = df[key_metrics].round(4)
    print("\n" + "="*100)
    print("GRAPH COMPARISON METRICS")
    print("="*100)
    print(display_df.to_string(index=False))


def create_visualizations(G1, G2, name1, name2):
    """Create comparative visualizations."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Degree distributions
    degrees1 = [d for n, d in G1.degree()]
    degrees2 = [d for n, d in G2.degree()]
    
    axes[0, 0].hist(degrees1, bins=30, alpha=0.7, label=name1, color='blue')
    axes[0, 0].hist(degrees2, bins=30, alpha=0.7, label=name2, color='red')
    axes[0, 0].set_xlabel('Degree')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Degree Distribution Comparison')
    axes[0, 0].legend()
    axes[0, 0].set_yscale('log')
    
    # Edge weight distributions
    weights1 = [data['weight'] for _, _, data in G1.edges(data=True)]
    weights2 = [data['weight'] for _, _, data in G2.edges(data=True)]
    
    axes[0, 1].hist(weights1, bins=30, alpha=0.7, label=name1, color='blue')
    axes[0, 1].hist(weights2, bins=30, alpha=0.7, label=name2, color='red')
    axes[0, 1].set_xlabel('Edge Weight')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Edge Weight Distribution Comparison')
    axes[0, 1].legend()
    axes[0, 1].set_yscale('log')
    
    # Clustering coefficient distributions
    clustering1 = list(nx.clustering(G1).values())
    clustering2 = list(nx.clustering(G2).values())
    
    axes[1, 0].hist(clustering1, bins=30, alpha=0.7, label=name1, color='blue')
    axes[1, 0].hist(clustering2, bins=30, alpha=0.7, label=name2, color='red')
    axes[1, 0].set_xlabel('Clustering Coefficient')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Clustering Coefficient Distribution')
    axes[1, 0].legend()
    
    # Betweenness centrality distributions
    betweenness1 = list(nx.betweenness_centrality(G1).values())
    betweenness2 = list(nx.betweenness_centrality(G2).values())
    
    axes[1, 1].hist(betweenness1, bins=30, alpha=0.7, label=name1, color='blue')
    axes[1, 1].hist(betweenness2, bins=30, alpha=0.7, label=name2, color='red')
    axes[1, 1].set_xlabel('Betweenness Centrality')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Betweenness Centrality Distribution')
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig(DATA_FOLDER / 'graph_comparison_plots.png', dpi=300, bbox_inches='tight')
    plt.show()


def main():
    # File paths
    west_indies_input = DATA_FOLDER / "articles_west_indies/articles_west_indies_with_persons.jsonl"
    west_indies_output = DATA_FOLDER / "articles_west_indies/articles_west_indies_filtered_graph.gexf"
    
    india_input = DATA_FOLDER / "articles_India/articles_India_with_persons.jsonl"
    india_output = DATA_FOLDER / "articles_India/articles_India_filtered_graph.gexf"
    
    # Build graphs with min_connections = 30
    print("Building West Indies graph...")
    G_west_indies = build_graph(west_indies_input, min_connections=30)
    
    print("\nBuilding India graph...")
    G_india = build_graph(india_input, min_connections=30)
    
    # Save graphs
    nx.write_gexf(G_west_indies, west_indies_output)
    nx.write_gexf(G_india, india_output)
    print(f"\nGraphs saved to {west_indies_output} and {india_output}")
    
    # Calculate metrics
    print("\nCalculating metrics...")
    metrics_west_indies = calculate_graph_metrics(G_west_indies, "West Indies")
    metrics_india = calculate_graph_metrics(G_india, "India")
    
    # Print comparison table
    print_metrics_table([metrics_west_indies, metrics_india])
    
    # Generate comparative analysis
    print("\n" + "="*100)
    print("COMPARATIVE ANALYSIS")
    print("="*100)
    
    comparison = compare_graphs(metrics_west_indies, metrics_india)
    
    print(f"\nStructural Comparison:")
    print(f"• West Indies has {comparison['size_ratio']:.2f}x as many nodes as India")
    print(f"• West Indies has {comparison['edge_ratio']:.2f}x as many edges as India")
    print(f"• West Indies is {comparison['density_ratio']:.2f}x as dense as India")
    
    print(f"\nCentralization and Hierarchy:")
    if comparison['centralization_diff'] > 0:
        print(f"• West Indies is more centralized (difference: {comparison['centralization_diff']:.4f})")
    else:
        print(f"• India is more centralized (difference: {abs(comparison['centralization_diff']):.4f})")
    
    print(f"\nClustering and Community Structure:")
    print(f"• West Indies has {comparison['clustering_ratio']:.2f}x the clustering of India")
    
    if 'path_length_ratio' in comparison:
        print(f"• West Indies has {comparison['path_length_ratio']:.2f}x the average path length of India")
    
    print(f"\nDegree Distribution:")
    print(f"• West Indies has {comparison['degree_variance_ratio']:.2f}x the degree variance of India")
    
    # Print top nodes for each graph
    print(f"\n" + "="*50)
    print("TOP 10 MOST CONNECTED PERSONS")
    print("="*50)
    
    for G, name in [(G_west_indies, "West Indies"), (G_india, "India")]:
        top_nodes = sorted(G.nodes(), key=lambda x: G.degree(x, weight='weight'), reverse=True)[:10]
        print(f"\n{name}:")
        for i, person in enumerate(top_nodes, 1):
            weight = sum(data['weight'] for _, _, data in G.edges(person, data=True))
            print(f"{i:2d}. {person}: {G.degree(person)} connections, total weight: {weight}")
    
    # Create visualizations
    print("\nGenerating visualizations...")
    create_visualizations(G_west_indies, G_india, "West Indies", "India")
    

    person_metrics = calculate_person_metrics(G_west_indies, "john scott")
    influence_analysis = analyze_person_influence(G_west_indies, "john scott")
    print_person_analysis(person_metrics, influence_analysis, "India")




    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()