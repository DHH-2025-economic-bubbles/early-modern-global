import glob
import os
from preprocessing.utils import read_gpkg_to_dict
from settings import DATA_FOLDER

import json
from typing import Dict, List, Set, Optional, Any
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from nltk.stem import PorterStemmer
from flashtext.keyword import KeywordProcessor

from nltk.stem import PorterStemmer

STEMMER: PorterStemmer = PorterStemmer()
LIST_WORDS: List[str] = [
    "furs",
    "tobacco",
    "rice",
    "indigo",
    "sugar",
    "molasses",
    "negroes",
    "silk",
    "peltry"
]

gpkg_path: Path = DATA_FOLDER / "filtered_places.gpkg" 
places_data: Dict[str, tuple[float, float]] = read_gpkg_to_dict(gpkg_path)
places_names: List[str] = list(places_data.keys())

places_with_space = [s for s in places_names if " " in s]
places_without_space = [s.replace(" ", "") for s in places_with_space]

places_names = [s for s in places_names if s not in places_with_space]

places_with_space_dict = {}
for place_without_space, place_with_space in sorted(zip(places_without_space, places_with_space)):
    places_with_space_dict[place_without_space] = place_with_space

LIST_WORDS.extend(places_names)

LIST_WORDS = [word.lower() for word in LIST_WORDS]

OUTPUT_PATH: Path = DATA_FOLDER / "detect_words.jsonl"

#OUTPUT_PATH = DATA_FOLDER / "detect_words_test.jsonl"

keyword_processor = KeywordProcessor()
for k, w in zip(places_with_space, places_without_space):
    keyword_processor.add_keyword(k, w)


def get_json_files(root_folder:Path)->List[Path]:
    # Using glob with recursive=True to find all JSON files
    json_pattern = os.path.join(root_folder, '**', '*.json')
    json_files = glob.glob(json_pattern, recursive=True)
    
    return json_files


def detect_words_json_files(json_file: Path) -> Optional[Dict[str, Any]]:
    with open(json_file, 'r', encoding='utf-8') as f:
        data: dict = json.load(f)

        data["found_words"] = []
        for text in data['texts']:
            text = keyword_processor.replace_keywords(text)
            words_data: Set[str] = set(text.lower().split())
            
            found_words: List[str] = []
            for word in LIST_WORDS:
                if word in words_data:
                    found_words.append(word)
            for word in places_without_space:
                if word in words_data:
                    found_words.append(places_with_space_dict[word])
            
            if not found_words:
                continue
            data["found_words"].append(found_words)

        if not data["found_words"]:
            return None  
        
        del data['texts']

        return data
        
def create_frequency_json(folder_articles: Path) -> None:

    json_files: List[Path] = list(folder_articles.glob("*.json"))
    total_files = len(json_files)
    print(f"Number of JSON files: {total_files}")
    
    # Calculate batch size
    batch_size = max(1, total_files // 100)
    
    
    
    # Create empty output file if it doesn't exist
    if not OUTPUT_PATH.exists():
        OUTPUT_PATH.touch()
    else:
        OUTPUT_PATH.unlink()
    
    # Process in batches
    for batch_num in range(100):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, total_files)
        
        if start_idx >= total_files:
            break
            
        batch_files = json_files[start_idx:end_idx]

        print(f"Processing batch {batch_num+1}/100: {len(batch_files)} files")
        
        batch_results = []
        with ProcessPoolExecutor() as executor:
            for file_result in executor.map(detect_words_json_files, batch_files):

                if file_result is not None:
                    batch_results.append(file_result)

        # for file in json_files:
            
        #     data = detect_words_json_files(file)
        #     if not data:
        #         continue
        #     with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
        #         f.write(json.dumps(data, ensure_ascii=False) + "\n")

    
        # Append new batch results directly to the file, one JSON object per line
        with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
            for result in batch_results:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        
        print(f"Batch {batch_num+1} completed: Added {len(batch_results)} files")
        
        # Clear memory
        del batch_results
    
    print(f"All batches completed. Results saved to {OUTPUT_PATH}")


def main() -> None:
    print("Creating frequency JSON...")
    articles_files: Path = DATA_FOLDER / "cleaned_articles"
    #articles_files = Path(Path("/home/cedric/repos/early-modern-global/data/cleaned_articles_test"))
    create_frequency_json(articles_files)
  

if __name__ == "__main__":
    main()