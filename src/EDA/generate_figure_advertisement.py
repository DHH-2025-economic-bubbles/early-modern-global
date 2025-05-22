## This is used with the random ad sample 

import os
import json
import matplotlib.pyplot as plt
from collections import Counter
import re
from settings import FOLDER_ARTICLES, DATA_FOLDER
from pathlib import Path


def clean_text(text):
    cleaned = re.sub(r'\s+', ' ', text)
    cleaned = re.sub(r'[^\w\s-]', '', cleaned)
    return cleaned.lower()


def load_articles(folder_path):
    articles = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    articles.append(data)
            except json.JSONDecodeError as e:
                print(f"Error loading {file_name}: {e}")
            except Exception as e:
                print(f"Unexpected error with {file_name}: {e}")
    return articles


def count_keyword_per_decade(articles, keyword):
    yearly_counts = Counter()
    for article in articles:
        date = article.get('meta_issue_date_start', '')
        text = article.get('text', '')
        if date:
            cleaned_text = clean_text(text)
            year = int(date.split('-')[0])
            if 1620 <= year <= 1799:
                decade = int(str(year)[:3] + "0")
                if re.search(rf'\b{keyword.lower()}\b', cleaned_text):
                    count = len(re.findall(rf'\b{keyword.lower()}\b', cleaned_text))
                    yearly_counts[decade] += count
    return yearly_counts




def plot_keyword_trend_decade(keyword_counts1, keyword_counts2, articles_per_decade, keyword1, keyword2):
    decades = sorted(set(keyword_counts1.keys()).union(set(keyword_counts2.keys())))
    frequencies1 = [keyword_counts1.get(decade, 0) for decade in decades]
    frequencies2 = [keyword_counts2.get(decade, 0) for decade in decades]
    normalized1 = [freq / articles_per_decade.get(decade, 1) for freq, decade in zip(frequencies1, decades)]
    normalized2 = [freq / articles_per_decade.get(decade, 1) for freq, decade in zip(frequencies2, decades)]

    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    plt.plot(decades, frequencies1, marker='o', linestyle='-', color='blue', label=f'Absolute Frequency: {keyword1}')
    plt.plot(decades, frequencies2, marker='x', linestyle='-', color='red', label=f'Absolute Frequency: {keyword2}')
    plt.title(f'Keyword Comparison: "{keyword1}" vs "{keyword2}"')
    plt.xlabel('Decade')
    plt.ylabel('Frequency')
    plt.xticks(decades, rotation=45)
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(decades, normalized1, marker='o', linestyle='--', color='blue', label=f'Normalized Frequency: {keyword1}')
    plt.plot(decades, normalized2, marker='x', linestyle='--', color='red', label=f'Normalized Frequency: {keyword2}')
    plt.xlabel('Decade')
    plt.ylabel('Normalized Frequency')
    plt.xticks(decades, rotation=45)
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()




def count_articles_by_decade(articles, start_year=1660, end_year=1800):
    articles_per_decade = Counter()
    for article in articles:
        date = article.get('meta_issue_date_start', '')
        if date:
            try:
                year = int(date.split('-')[0])
                if start_year <= year <= end_year:
                    decade = (year // 10) * 10
                    articles_per_decade[decade] += 1
            except ValueError:
                continue  # Skip if date format is invalid
    article_counts = dict(sorted(articles_per_decade.items()))
    out_path = DATA_FOLDER / "article_counts.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(article_counts, f, indent=4)



def main():
    folder_path = DATA_FOLDER / "ad"
    articles = load_articles(folder_path)
    article_counts = count_articles_by_decade(articles)

    sugar_count = count_keyword_per_decade(articles, "sugar")
    n1 = count_keyword_per_decade(articles, "negro")
    n2 = count_keyword_per_decade(articles, "negroes")

    n = {}
    for key, value in n1.items():
        n[key] = n.get(key, 0) + value
    for key, value in n2.items():
        n[key] = n.get(key, 0) + value
    n = dict(sorted(n.items()))

    plot_keyword_trend_decade(n, sugar_count, article_counts, "sugar", "slavery-related advertisement")



if __name__=="__main__":
    main()