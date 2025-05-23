import json
import os
import shutil
import geopandas as gpd
import multiprocessing as mp
from functools import partial

from settings import DATA_FOLDER

CLEANED_ARTICLES_FOLDER = DATA_FOLDER/"cleaned_articles/"
THRESHOLD = 5
PARAGRAPH_THRESHOLD = 3

def process_line(line, country_places, output_dir, cleaned_articles_folder, country_name):
    data = json.loads(line.strip())
    
    place_mentions = []
    found_words_dict = data.get('found_words', {})
    for paragraph_index, words in found_words_dict.items():
        place_mentions.extend(words)

    country_place_count = 0
    country_paragraph_indexes = []
    
    for paragraph_index, words in found_words_dict.items():
        paragraph_count = 0
        for word in words:
            if word in country_places:
                country_place_count += 1
                paragraph_count += 1
        if paragraph_count > PARAGRAPH_THRESHOLD:
            country_paragraph_indexes.append(paragraph_index)
    
    if country_place_count >= THRESHOLD:
        filename = data['file_name']
        
        source_path = cleaned_articles_folder / filename
        with open(source_path, 'r') as source_file:
            source_data = json.load(source_file)
            
            country_texts = []
            for idx_str in country_paragraph_indexes:
                idx = int(idx_str) if isinstance(idx_str, str) else idx_str
                country_texts.append(source_data["texts"][idx])
            
            filtered_data = source_data.copy()
            filtered_data["texts"] = country_texts
            filtered_data["country"] = country_name
            
            dest_path = os.path.join(output_dir, filename)
            with open(dest_path, 'w') as dest_file:
                json.dump(filtered_data, dest_file, indent=2)
            
            return 1

    return 0

def process_files_for_country(gpkg_path, jsonl_file, output_dir, country_name, num_processes=None):
    gdf = gpd.read_file(gpkg_path)
    country_places = set(gdf[gdf['country'] == country_name]['name'].tolist())
    country_places.add(country_name.lower())
    print(f"Found {len(country_places)} places in {country_name} from GPKG")
    
    if num_processes is None:
        num_processes = mp.cpu_count()
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    process_func = partial(
        process_line, 
        country_places=country_places, 
        output_dir=output_dir, 
        cleaned_articles_folder=CLEANED_ARTICLES_FOLDER,
        country_name=country_name
    )
    
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(process_func, lines)
    
    files_copied = sum(results)
    print(f"Total files copied for {country_name}: {files_copied}")
    return files_copied

if __name__ == "__main__":
    countries_of_interest = [
        "Barbados", "Jamaica", "Bahamas", "Trinidad and Tobago", 
        "Saint Kitts and Nevis", "Antigua and Barbuda", 
        "Saint Vincent and the Grenadines", "Grenada", "Saint Lucia", 
        "Dominica", "United States of America", "Ghana", "Nigeria", 
        "Sierra Leone", "Gambia", "Canada"
    ]
    
    gpkg_path = DATA_FOLDER / "filtered_places.gpkg"
    jsonl = DATA_FOLDER / "detect_words.jsonl"
    
    output_dir = DATA_FOLDER / "articles_west_indies"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    total_files = 0
    for country in countries_of_interest:
        files_copied = process_files_for_country(gpkg_path, jsonl, output_dir, country)
        total_files += files_copied
    
    print(f"Grand total files processed: {total_files}")