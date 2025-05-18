import json
import multiprocessing
import os
from pathlib import Path
import polars as pl

from preprocessing.utils import clean_text
from settings import CLEANED_DATA_FOLDER, DATA_FOLDER, FOLDER_ARTICLES

BL_NEWSPAPERS_META = DATA_FOLDER / "bl_newspapers_meta.csv"


CLEANED_DATA_FOLDER = DATA_FOLDER / "cleaned_articles"

os.makedirs(CLEANED_DATA_FOLDER, exist_ok=True)

print(f"{multiprocessing.cpu_count()} are available for processing")

# Global variable for worker processes
WORKER_META_DICT = None

def init_worker(meta_dict_lookup):
    """Initialize worker process with shared metadata dictionary"""
    global WORKER_META_DICT
    WORKER_META_DICT = meta_dict_lookup

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"cannot process the json: {file_path}, full error: {e}")
        
        
        return [record for record in data]

def enrich_article(article):
    """Process and save a single ad with metadata"""
    global WORKER_META_DICT
    
    issue_id = article.get("issueID", "unknown")
    article_id = article.get("articleID", "unknown")
    newspaper_id = article.get("articleID")
    
    # Create filename using issueID and articleID
    filename = f"{issue_id}_{article_id}.json"
    filepath = CLEANED_DATA_FOLDER / filename
    article["file_name"] = filename
    article["text"] = clean_text(article.get("text"))
    # Add metadata to the ad json if found using dictionary lookup
    if newspaper_id in WORKER_META_DICT:
        meta_dict = WORKER_META_DICT[newspaper_id]
        for key, value in meta_dict.items():
            article[f"meta_{key}"] = value
        metadata_found = True
    else:
        metadata_found = False
    
    with open(filepath, "w", encoding="utf-8") as f_out:
        json.dump(article, f_out, ensure_ascii=False, indent=2)
    
    return filename, metadata_found

def main():
    #FOLDER_ARTICLES = Path("/home/cedric/repos/early-modern-global/data/test_preprocessing")
    json_files = list(FOLDER_ARTICLES.glob("*.json"))
    print(f"number of jsons: {len(json_files)}")
    
    number_batches = 100
    chunk_size = len(json_files) // number_batches
    batches = [json_files[i:i + chunk_size] for i in range(0, len(json_files), chunk_size)]
    
    if len(batches) > number_batches:
        batches[number_batches-1].extend(batches[number_batches])
        batches = batches[:number_batches]
    
    print("Reading metadata CSV...")
    meta_df = pl.read_csv(BL_NEWSPAPERS_META,
                          schema_overrides={"issue_no": pl.Utf8})

    print("Converting metadata to dictionary lookup...")
    meta_dict_lookup = {}
    for row_dict in meta_df.to_dicts():
        article_id = row_dict['article_id']
        meta_dict_lookup[article_id] = row_dict
    
    print(f"Metadata dictionary created with {len(meta_dict_lookup)} entries")
    
    
    for i, chunk in enumerate(batches, 1):
        print(f"Processing chunk {i}/{number_batches} with {len(chunk)} files...")
        
        with multiprocessing.Pool() as pool:
            chunk_results = pool.map(process_file, chunk)
        
        print("Finished getting the news items")

        chunk_results = [record for sublist in chunk_results for record in sublist]
        
        print(f"Chunk {i} produced {len(chunk_results)} articles")
        
        with multiprocessing.Pool(#processes=max_workers, 
                                  initializer=init_worker, 
                                  initargs=(meta_dict_lookup,)) as pool:
            pool.map(enrich_article, chunk_results)
    
    
if __name__ == "__main__":
    main()
