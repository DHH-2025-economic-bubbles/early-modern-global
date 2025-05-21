import csv
import nltk
from collections import defaultdict
from settings import FOLDER_ARTICLES, DATA_FOLDER
from pathlib import Path

def generate_noun_adj_lists(file_path):
    noun_dict = {}
    adj_dict = {}

    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader) 
        terms = [(row[0], int(float(row[1]))) for row in reader]

    words = [word for word,_ in terms]
    tags = nltk.pos_tag(words)

    for (word, tag), (_, count) in zip(tags, terms):
        if tag.startswith('NN'):
            noun_dict[word] = count
        elif tag.startswith('JJ'):
            adj_dict[word] = count

    return noun_dict,adj_dict

def main():

    ngram_files = list(DATA_FOLDER.rglob("*ngrams.csv"))
    for ngram_file in ngram_files:
        noun_dict,adj_dict=generate_noun_adj_lists(ngram_file)
        save_filtered_dict(ngram_file,noun_dict,adj_dict)

import pandas as pd

def save_filtered_dict(ngram_file, noun_dict, adj_dict):
    ngram_path = Path(ngram_file)
    
    # Create new filenames
    noun_file = ngram_path.with_name(ngram_path.stem + "_noun.csv")
    adj_file = ngram_path.with_name(ngram_path.stem + "_adj.csv")
    
    # Save to CSV
    pd.DataFrame(noun_dict.items(), columns=["term", "count"]).to_csv(noun_file, index=False)
    pd.DataFrame(adj_dict.items(), columns=["term", "count"]).to_csv(adj_file, index=False)
    
    print(f"Saved nouns to: {noun_file}")
    print(f"Saved adjectives to: {adj_file}")




if __name__=="__main__":
    import nltk

    nltk.download('averaged_perceptron_tagger_eng')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('punkt')

    main()