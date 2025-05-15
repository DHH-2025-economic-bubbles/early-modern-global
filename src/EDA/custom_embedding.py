"""
This script creates a CSV file from JSON files containing articles.
It filters the articles based on the presence of a 'text' field and 
adds a column indicating if the article is related to colonialism.
"""

import json
import spacy

import pandas as pd
from settings import FOLDER_ARTICLES, DATA_FOLDER

DF_COLS = ["issue_id", "title", "text", "is_colonial"]

def clean_text(text: str) -> str:
    """Wrapper function to clean text by replacing quotes and escaping newlines."""
    # we want to get rid of newlines
    text = text.replace("\n", " ")
    return text

def main():
    #json_files = list(FOLDER_ARTICLES.glob("*.json"))
    json_files = [FOLDER_ARTICLES / "035_N0000007.json"] 
    print(f"Number of JSON files: {len(json_files)}")

    rows = []
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data: list[dict] = json.load(f)
            for issue in data:
                if 'text' in issue:
                    rows.append({
                        "issue_id": issue['issueID'],
                        "title": issue['title'],
                        "text": clean_text(issue['text']),
                        "is_colonial": False
                    })
                else:
                    print(f"File: {issue['title']} does not have a text field.")
    
    df = pd.DataFrame(rows, columns=DF_COLS)

    df.to_csv(DATA_FOLDER / "filtered_articles_by_topic.csv", index=False, encoding='utf-8', sep="@")




if __name__ == "__main__":
    main()