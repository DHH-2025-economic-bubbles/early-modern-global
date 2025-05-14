import json
import matplotlib.pyplot as plt
from collections import Counter
import multiprocessing
from settings import FINDINGS_FOLDER, FOLDER_ARTICLES
from matplotlib.ticker import FuncFormatter

OUTPUT_IMAGE = FINDINGS_FOLDER / "article_type_frequencies.png"

def extract_article_types(file_path):
    article_types = []
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            article_types.extend(record.get("articleType") for record in data if "articleType" in record)
        except json.JSONDecodeError as e:
            print(f"Failed to read {file_path}: {e}")
    return article_types

def format_thousands(x, _):
    return f"{int(x):,}".replace(",", ".")

def main():
    json_files = list(FOLDER_ARTICLES.glob("*.json"))
    print(f"Number of JSON files: {len(json_files)}")

    with multiprocessing.Pool() as pool:
        results = pool.map(extract_article_types, json_files)

    # Flatten list of lists
    all_article_types = [atype for sublist in results for atype in sublist if atype]

    counter = Counter(all_article_types)

    # Print frequencies
    print("Article Type Frequencies:")
    for k, v in counter.items():
        print(f"{k}: {v}")

    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_thousands))

    # Plot and save to file
    plt.figure(figsize=(10, 6))
    plt.bar(counter.keys(), counter.values(), color='skyblue')
    plt.xlabel("Article Type")
    plt.ylabel("Frequency")
    plt.title("Frequency of Article Types")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE, dpi=300)
    print(f"Plot saved to: {OUTPUT_IMAGE}")

if __name__ == "__main__":
    main()
