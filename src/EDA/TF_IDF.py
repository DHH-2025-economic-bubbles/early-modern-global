from settings import FOLDER_ARTICLES, DATA_FOLDER

import json
import string
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import csr_matrix  
from nltk.stem import PorterStemmer


LIST_OF_WORDS = [
    "tea", "cotton", "coffee", "sugar", "rice", "rubber",
    "petroleum", "silk", "tobacco", "sisal", "tin", "copper",
    "lead", "zinc", "bauxite", "cocoa", "oilseeds", "bananas",
    "citrus", "gold", "silver", "wool", "timber", "wheat", "meat",
    "peanuts", "palm-oil", "cloves", "slave"
]

def clean_text(text: str) -> str:
    return text.translate(str.maketrans('', '', string.punctuation))

ps = PorterStemmer()

def process_file(json_file):
    results = {}
    stemmed_list_of_words = [ps.stem(word) for word in LIST_OF_WORDS]
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data: list[dict] = json.load(f)
            for article in data:
                if 'text' not in article:
                    continue

                words = clean_text(article['text']).split()
                stemmed_words = [ps.stem(word) for word in words]
                word_counts = { word: 0 for word in LIST_OF_WORDS }
                key = article.get("title") or f"{article.get('title', 'untitled')}_{hash(article['text'])}"

                for word, stemmed_word in zip(LIST_OF_WORDS, stemmed_list_of_words):
                    word_mentions = stemmed_words.count(stemmed_word)
                    word_counts[word] = word_mentions
                word_counts["total_words"] = len(stemmed_words)
                word_counts["issue_id"] = article.get("issueID", "unknown")
                word_counts["article_id"] = article.get("articleID", "unknown")
                word_counts["file_name"] = json_file.name
                results[key] = word_counts

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {json_file}: {e}")
    except Exception as e:
        print(f"Unexpected error in file {json_file}: {e}")
    return results

def create_frequency_json():
    json_files = list(FOLDER_ARTICLES.glob("*.json"))
    print(f"Number of JSON files: {len(json_files)}")

    all_rows = {}

    with ProcessPoolExecutor() as executor:
        for file_result in executor.map(process_file, json_files):
            all_rows.update(file_result)

    DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    output_path = DATA_FOLDER / "word_count.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, ensure_ascii=False, indent=2)
    print(f"Word counts saved to {output_path}")

def calculate_tf_idf(df: pd.DataFrame) -> pd.DataFrame:
    id_fields = ["issue_id", "article_id", "file_name"]
    id_data = df[id_fields] if all(field in df.columns for field in id_fields) else None

    if 'total_words' in df.columns:
        df = df.drop(columns=["total_words"])
    df = df.drop(columns=id_fields, errors='ignore')
    df.fillna(0, inplace=True)
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    transformer = TfidfTransformer()
    tfidf_matrix: csr_matrix = transformer.fit_transform(df.values)
    tfidf_array = tfidf_matrix.toarray()

    tfidf_df = pd.DataFrame(tfidf_array, index=df.index, columns=df.columns)
    tfidf_df["tf-idf"] = tfidf_df.sum(axis=1)

    if id_data is not None:
        tfidf_df = pd.concat([tfidf_df, id_data], axis=1)

    return tfidf_df
    
def create_tf_idf_csv():
    df = pd.read_json(DATA_FOLDER / "word_count.json", orient="index")
    df_tf_idf = calculate_tf_idf(df)
    df_tf_idf.to_csv(DATA_FOLDER / "tf_idf.csv", index=True, encoding='utf-8', sep="@")

    # sort by tf-idf value and get top 100
    df_tf_idf.sort_values(by="tf-idf", ascending=False, inplace=True)
    df_tf_idf = df_tf_idf.head(100)
    df_tf_idf.to_csv(DATA_FOLDER / "tf_idf_top_100.csv", index=True, encoding='utf-8', sep=",")

def main():
    print("Creating frequency JSON...")
    create_frequency_json()
    print("Creating TF-IDF CSV...")
    create_tf_idf_csv()    

if __name__ == "__main__":
    main()