import json
import multiprocessing
import os
from pathlib import Path
import polars as pl

from settings import ADS_FOLDER, FOLDER_ARTICLES
BL_NEWSPAPERS_META = Path("/home/cedric/repos/early-modern-global/data/bl_newspapers_meta.csv")

# Create ads folder for individual JSON files

os.makedirs(ADS_FOLDER, exist_ok=True)

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"cannot process the json: {file_path}, full error: {e}")

        return [record for record in data if record.get("articleType") in ["Classified ads", "Advertisement", "Advertisements and Notices"]]

def main():
    json_files = list(FOLDER_ARTICLES.glob("*.json"))
    print(f"number of jsons: {len(json_files)}")

    with multiprocessing.Pool() as pool:
        results = pool.map(process_file, json_files)

    # Flatten the results
    results = [record for sublist in results for record in sublist]

    meta_df = pl.read_csv(BL_NEWSPAPERS_META,
                          schema_overrides={"issue_no": pl.Utf8})

    print(f"number of ads: {len(results)}")
    
    # Save each ad as an individual JSON file
    saved_count = 0
    for ad in results:
        issue_id = ad.get("issueID", "unknown")
        article_id = ad.get("articleID", "unknown")

        issue_id = ad.get("issueID")
        newspaper_id = ad.get("articleID")
        matching_meta = meta_df.filter(pl.col('article_id') == newspaper_id)
        
        # Create filename using issueID and articleID
        filename = f"{issue_id}_{article_id}.json"
        filepath = ADS_FOLDER / filename
        
        # Add metadata to the ad json if found
        if not matching_meta.is_empty():
            # Convert the matching metadata to a dictionary
            meta_dict = matching_meta.row(0, named=True) 
            # Add metadata entries to the ad dictionary
            for key, value in meta_dict.items():
                ad[f"meta_{key}"] = value
        else:
            print(f"metadata not found for {filename}")
        
        with open(filepath, "w", encoding="utf-8") as f_out:
            json.dump(ad, f_out, ensure_ascii=False, indent=2)
        saved_count += 1
        if saved_count % 100 == 0:
            print(f"saved {saved_count} ads")
    
    print(f"Saved {saved_count} individual ad files to {ADS_FOLDER}")

if __name__ == "__main__":
    main()