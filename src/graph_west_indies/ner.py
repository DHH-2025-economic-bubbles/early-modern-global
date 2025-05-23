import json
import pandas as pd
import spacy
import multiprocessing as mp
from pathlib import Path
from tqdm import tqdm
from functools import partial


# get the list of people
# put titles in front
# redo a detection on the dataset

from settings import DATA_FOLDER


df = pd.read_csv(
DATA_FOLDER / "baby-names.csv")
names_list = df["name"].tolist()
names_list = [s.lower() for s in names_list]
df = None

def clean_persons(list_persons):

    cleaned = []

    for person in list_persons:
        if person == "fort william":
            continue

        if len(person) < 4:
            continue
        if person in names_list:
            continue
        cleaned.append(person)


    return cleaned

def process_file(json_file, nlp_model):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    texts = data.get("texts", [])
    all_persons = []
    
    for text in texts:
        doc = nlp_model(text)
        persons_in_text = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        
        persons_in_text = clean_persons(persons_in_text)
        if persons_in_text:
            all_persons.extend(persons_in_text)
    
    unique_persons = []
    [unique_persons.append(p) for p in all_persons if p not in unique_persons]
    
    data["persons"] = unique_persons
    
    return data

def main():
    articles_folder = DATA_FOLDER / "articles_west_indies"
    output_file = DATA_FOLDER / "articles_west_indies/articles_west_indies_with_persons.jsonl"
    
    json_files = list(articles_folder.glob("*.json"))
    print(f"Found {len(json_files)} JSON files to process")
    
    nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "lemmatizer"])
    
    num_processes = max(1, mp.cpu_count() - 2)
    print(f"Using {num_processes} processes")
    
    with mp.Pool(processes=num_processes) as pool:
        process_func = partial(process_file, nlp_model=nlp)
        
        results = list(tqdm(
            pool.imap(process_func, json_files),
            total=len(json_files),
            desc="Processing files"
        ))
    
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for data in results:
            out_file.write(json.dumps(data) + '\n')
    
    print(f"Processing complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()