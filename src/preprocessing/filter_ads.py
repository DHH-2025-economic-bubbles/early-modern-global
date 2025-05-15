
import json
import multiprocessing

from settings import DATA_FOLDER, FOLDER_ARTICLES

OUTPUT_FILE = DATA_FOLDER / "filtered_ads.json"

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise("cannot process the json: {file_path}, full error: {e}")

        return [record for record in data if record.get("articleType") in ["Classified ads", "Advertisement", "Advertisements and Notices"]]

def main():
    json_files = list(FOLDER_ARTICLES.glob("*.json"))
    print(f"number of jsons: {len(json_files)}")

    with multiprocessing.Pool() as pool:
        results = pool.map(process_file, json_files)

    # Flatten the results
    filtered_records = [record for sublist in results for record in sublist]

    print(f"number of ads: {len(filtered_records)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        json.dump(filtered_records, f_out, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()