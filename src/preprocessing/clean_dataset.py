import json
import multiprocessing
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import polars as pl

from preprocessing.utils import clean_text, regroup_texts
from settings import DATA_FOLDER, FOLDER_ARTICLES, CLEANED_DATA_FOLDER

BL_NEWSPAPERS_META: Path = DATA_FOLDER / "bl_newspapers_meta.csv"
os.makedirs(CLEANED_DATA_FOLDER, exist_ok=True)

# FOLDER_ARTICLES = Path("/home/cedric/repos/early-modern-global/data/test_preprocessing")
# CLEANED_DATA_FOLDER = Path("/home/cedric/repos/early-modern-global/data/cleaned_articles_test")

print(f"{multiprocessing.cpu_count()} are available for processing")

WORKER_META_DICT: Optional[Dict[str, Dict[str, Any]]] = None

def init_worker(meta_dict_lookup: Dict[str, Dict[str, Any]]) -> None:
    global WORKER_META_DICT
    WORKER_META_DICT = meta_dict_lookup

def process_file(file_path: Path) -> List[Dict[str, Any]]:
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data: List[Dict[str, Any]] = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"cannot process the json: {file_path}, full error: {e}")
        
        return [record for record in data]

def enrich_article(article: Dict[str, Any]):
    global WORKER_META_DICT
    
    issue_id: str = article.get("issueID", "unknown")
    article_id: str = article.get("articleID", "unknown")
    newspaper_id: Optional[str] = article.get("articleID")

    exploded_texts = regroup_texts(article["text"])

    if newspaper_id is not None and WORKER_META_DICT is not None and newspaper_id in WORKER_META_DICT:
        meta_dict: Dict[str, Any] = WORKER_META_DICT[newspaper_id]
        for key, value in meta_dict.items():
            article[f"meta_{key}"] = value

    cleaned_texts = [clean_text(text) for text in exploded_texts]
    if len(cleaned_texts) == 0:
        return
    article.pop("text")  
    filename: str = f"{issue_id}_{article_id}.json"
    filepath: Path = CLEANED_DATA_FOLDER / filename
    article["file_name"] = filename
    article["texts"] = cleaned_texts

    with open(filepath, "w", encoding="utf-8") as f_out:
        json.dump(article, f_out, ensure_ascii=False, indent=2)



def main() -> None:
    json_files: List[Path] = list(FOLDER_ARTICLES.glob("*.json"))
    print(f"number of jsons: {len(json_files)}")
    
    number_batches: int = 100
    chunk_size: int = len(json_files) // number_batches
    batches: List[List[Path]] = [json_files[i:i + chunk_size] for i in range(0, len(json_files), chunk_size)]
    
    if len(batches) > number_batches:
        batches[number_batches-1].extend(batches[number_batches])
        batches = batches[:number_batches]
    
    print("Reading metadata CSV...")
    meta_df: pl.DataFrame = pl.read_csv(BL_NEWSPAPERS_META,
                          schema_overrides={"issue_no": pl.Utf8})

    print("Converting metadata to dictionary lookup...")
    meta_dict_lookup: Dict[str, Dict[str, Any]] = {}
    for row_dict in meta_df.to_dicts():
        article_id: str = row_dict['article_id']
        meta_dict_lookup[article_id] = row_dict
    
    meta_df = None
    
    print(f"Metadata dictionary created with {len(meta_dict_lookup)} entries")
    
    for i, batch in enumerate(batches, 1):
        print(f"Processing chunk {i}/{number_batches} with {len(batch)} files...")
        
        with multiprocessing.Pool() as pool:
            chunk_results: List[List[Dict[str, Any]]] = pool.map(process_file, batch)
        
        print("Finished getting the news items")

        chunk_results_flat: List[Dict[str, Any]] = [record for sublist in chunk_results for record in sublist]
        
        print(f"Chunk {i} produced {len(chunk_results_flat)} articles")
        
        with multiprocessing.Pool(initializer=init_worker, 
                                  initargs=(meta_dict_lookup,)) as pool:
            pool.map(enrich_article, chunk_results_flat)
    
    
if __name__ == "__main__":
    main()
