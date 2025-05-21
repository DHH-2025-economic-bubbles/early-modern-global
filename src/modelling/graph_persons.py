import json
from matplotlib import pyplot as plt
import networkx as nx
from itertools import combinations
from pathlib import Path
from tqdm import tqdm

from settings import DATA_FOLDER


def main():
    input_file = DATA_FOLDER / "articles_India/articles_India_with_persons.jsonl"
    output_file = DATA_FOLDER / "articles_India/articles_Indiapersons_filtered_graph.gexf"
    
    G = nx.Graph()
    
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in tqdm(file, desc="Building graph"):
            data = json.loads(line)
            persons = data.get("persons", [])
            
            if len(persons) >= 2:
                for person1, person2 in combinations(persons, 2):
                    if G.has_edge(person1, person2):
                        G[person1][person2]['weight'] += 1
                    else:
                        G.add_edge(person1, person2, weight=1)
    
    print(f"Original graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Filter nodes with minimum connections
    min_connections = 50  # Adjust this threshold as needed
    nodes_to_remove = [node for node in G.nodes() if G.degree(node) < min_connections]
    G.remove_nodes_from(nodes_to_remove)
    
    print(f"Filtered graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Add degree as node attribute for visualization in Gephi
    for node in G.nodes():
        G.nodes[node]['degree'] = G.degree(node)
        G.nodes[node]['weighted_degree'] = sum(data['weight'] for _, _, data in G.edges(node, data=True))
    
    # Export filtered graph to GEXF for Gephi
    nx.write_gexf(G, output_file)
    print(f"Filtered graph saved to {output_file} - Ready to be opened in Gephi")
    
    top_nodes = sorted(G.nodes(), key=lambda x: G.degree(x, weight='weight'), reverse=True)[:10]
    print("\nTop 10 connected persons in filtered graph:")
    for person in top_nodes:
        weight = sum(data['weight'] for _, _, data in G.edges(person, data=True))
        print(f"{person}: {G.degree(person)} connections, total weight: {weight}")

if __name__ == "__main__":
    main()