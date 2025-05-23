import json
import random
import os
from pathlib import Path
import re

# Define paths
DATA_FOLDER = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data"))
clusters_file = DATA_FOLDER / "articles_west_indies/clustering_west_indies.jsonl"
articles_file = DATA_FOLDER / "articles_west_indies/articles_west_indies_with_persons.jsonl"
output_file = DATA_FOLDER / "articles_west_indies/articles_west_indies_clusters_with_texts.json"

# Load clusters data
clusters = {}
with open(clusters_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            cluster_data = json.loads(line)
            clusters[cluster_data['community_id']] = cluster_data['nodes']

# Load articles data
articles = []
with open(articles_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            articles.append(json.loads(line))

# Function to find texts containing a person
def find_person_texts(person, article):
    matching_texts = []
    
    if 'texts' in article:
        for text in article['texts']:
            if re.search(person, text, re.IGNORECASE):
                # Create a copy of article without the 'texts' field
                article_without_texts = {k: v for k, v in article.items() if k != 'texts'}
                
                # Add text with metadata
                text_info = {
                    'text': text,
                    'date': article.get('meta_issue_date_start', 'Unknown'),
                    'newspaper': article.get('meta_newspaper_title', 'Unknown'),
                    'article_type': article.get('articleType', 'Unknown'),
                    'person': person,
                    #'article_metadata': article_without_texts  # Include all other fields
                }
                matching_texts.append(text_info)
    
    return matching_texts

# Process each cluster and collect text samples
enriched_clusters = []

for cluster_id, persons in clusters.items():
    cluster_info = {
        'cluster_id': cluster_id,
        'persons': persons,
        'text_samples': []
    }
    
    # Get texts for this cluster
    all_texts = []
    
    # Process each person in the cluster
    for person in persons:
        # Find articles containing this person
        for article in articles:
            if person in article.get('persons', []):
                # Find texts in the article containing this person
                person_texts = find_person_texts(person, article)
                all_texts.extend(person_texts)
    
    # Select 10 random texts (or all if less than 10)
    if len(all_texts) > 20:
        # Remove duplicates based on 'text' field
        unique_texts = []
        seen_texts = set()
        
        for text_info in all_texts:
            # Use the 'text' field as the unique identifier
            if text_info['text'] not in seen_texts:
                seen_texts.add(text_info['text'])
                unique_texts.append(text_info)
        
        # Take sample from unique texts
        sample_size = min(20, len(unique_texts))
        cluster_info['text_samples'] = random.sample(unique_texts, sample_size)
    else:
        # For smaller sets, still remove duplicates
        unique_texts = []
        seen_texts = set()
        
        for text_info in all_texts:
            if text_info['text'] not in seen_texts:
                seen_texts.add(text_info['text'])
                unique_texts.append(text_info)
        
        cluster_info['text_samples'] = unique_texts
    
    # Add count of total texts found
    cluster_info['total_texts_found'] = len(all_texts)
    
    enriched_clusters.append(cluster_info)

# Save to output file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(enriched_clusters, f, indent=2)

print(f"Saved enriched cluster data to {output_file}")
print(f"Processed {len(clusters)} clusters")