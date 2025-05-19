from preprocessing.utils import read_gpkg_to_dict
from settings import DATA_FOLDER

import json
from typing import Dict, List, Set, Optional, Any
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from nltk.stem import PorterStemmer

STEMMER: PorterStemmer = PorterStemmer()
LIST_WORDS: List[str] = [
    "furs",
    "tobacco",
    "rice",
    "indigo",
    "sugar",
    "rum",
    "molasses",
    "negroes"
]

gpkg_path: Path = DATA_FOLDER / "filtered_places.gpkg" 
places_data: Dict[str, tuple[float, float]] = read_gpkg_to_dict(gpkg_path)
places_names: List[str] = list(places_data.keys())

LIST_WORDS.extend(places_names)

LIST_WORDS = [word.lower() for word in LIST_WORDS]


def detect_words_json_files(json_file: Path) -> Optional[Dict[str, Any]]:
    with open(json_file, 'r', encoding='utf-8') as f:
        data: dict = json.load(f)
        words_data: Set[str] = set(data['text'].lower().split())
        
        found_words: List[str] = []
        for word in LIST_WORDS:
            if word in words_data:
                found_words.append(word)
        
        if not found_words:
            return None

        data["found_words"] = found_words
        
        del data['text']
                
        return data

def create_frequency_json(folder_articles: Path) -> None:
    json_files: List[Path] = list(folder_articles.glob("*.json"))
    print(f"Number of JSON files: {len(json_files)}")

    all_results: List[Dict[str, Any]] = []

    with ProcessPoolExecutor() as executor:
        for file_result in executor.map(detect_words_json_files, json_files):
            if file_result is not None:
                all_results.append(file_result)

    DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    output_path: Path = DATA_FOLDER / "detect_words.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"Word counts saved to {output_path}")

def main() -> None:
    print("Creating frequency JSON...")
    articles_files: Path = DATA_FOLDER / "cleaned_articles"
    create_frequency_json(articles_files)
  

if __name__ == "__main__":
    main()