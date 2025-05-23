import json
import os
import shutil
import geopandas as gpd
import multiprocessing as mp
from functools import partial

from settings import DATA_FOLDER

CLEANED_ARTICLES_FOLDER = DATA_FOLDER/"cleaned_articles/"
THRESHOLD = 2
PARAGRAPH_THRESHOLD = 2

def process_line(line, india_places, output_dir, cleaned_articles_folder):
    data = json.loads(line.strip())
    
    # Flatten the found_words list if it contains sublists
    place_mentions = []
    found_words_dict = data.get('found_words', {})
    for paragraph_index, words in found_words_dict.items():
        place_mentions.extend(words)

    india_place_count = 0
    india_paragraph_indexes = []  # Track paragraph indexes with Indian words
    
    for paragraph_index, words in found_words_dict.items():
        paragraph_india_count = 0
        for word in words:
            if word in india_places:
                india_place_count += 1
                paragraph_india_count += 1
                
            
        if paragraph_india_count > PARAGRAPH_THRESHOLD:
            india_paragraph_indexes.append(paragraph_index)

    # Only process the file if it meets or exceeds the threshold
    if india_place_count >= THRESHOLD and india_paragraph_indexes:
        filename = data['file_name']
        
        # Open the source JSON file to extract specific texts
        source_path = cleaned_articles_folder / filename
        with open(source_path, 'r') as source_file:
            source_data = json.load(source_file)
            
            # Extract only texts that contain the Indian words
            indian_texts = []
            for idx_str in india_paragraph_indexes:
                # Convert string index to integer if needed
                idx = int(idx_str) if isinstance(idx_str, str) else idx_str
                indian_texts.append(source_data["texts"][idx])
            
            # Create a new data structure with only the relevant texts
            filtered_data = source_data.copy()
            filtered_data["texts"] = indian_texts
            
            # Write the filtered data to the output directory
            dest_path = os.path.join(output_dir, filename)
            with open(dest_path, 'w') as dest_file:
                json.dump(filtered_data, dest_file, indent=2)
            
            return 1

    return 0

def process_files(gpkg_path, jsonl_file, output_dir, country_of_interest:str, num_processes=None):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read GPKG file and filter for places in the country of interest
    gdf = gpd.read_file(gpkg_path)
    country_places = set(gdf[gdf['country'] == country_of_interest]['name'].tolist())
    country_places.add(country_of_interest.lower())
    print(f"Found {len(country_places)} places in {country_of_interest} from GPKG")
    
    # If num_processes is not specified, use the number of CPU cores
    if num_processes is None:
        num_processes = mp.cpu_count()
    
    # Read all lines from the JSONL file
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Create a partial function with the common arguments
    process_func = partial(
        process_line, 
        india_places=country_places, 
        output_dir=output_dir, 
        cleaned_articles_folder=CLEANED_ARTICLES_FOLDER
    )
    
    # Create a pool of workers and map the processing function to the lines
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(process_func, lines)
    
    # Count the total files copied
    files_copied = sum(results)
    print(f"Total files copied: {files_copied}")

if __name__ == "__main__":
    country_of_interest = "India"
    # Update these paths for your environment
    gpkg_path = DATA_FOLDER / "filtered_places.gpkg"
    jsonl = DATA_FOLDER / "detect_words.jsonl"
    output_dir = DATA_FOLDER / f"articles_{country_of_interest}"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    process_files(gpkg_path, jsonl, output_dir, country_of_interest)