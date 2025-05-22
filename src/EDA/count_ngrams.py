'''
Script for finding n-grams for keywords in advertisements 
'''

import json
from glob import glob
from nltk.util import ngrams
from collections import Counter
from nltk.corpus import stopwords
from tqdm import tqdm
import pandas as pd
import os
from settings import FOLDER_ARTICLES, DATA_FOLDER
import nltk


def get_file_articles(floc):
    try:
        with open(floc, 'r', encoding='utf-8') as jsonfile:
            res = json.load(jsonfile)
    except json.JSONDecodeError:
        return None
    return res

def get_articles(files_list):
    articles = []
    for file in files_list:
        res = get_file_articles(file)
        if res is not None:
            article_meta = dict()
            for k, v in res.items():
                if k != 'texts':
                    article_meta[k] = v
            for item in res['texts']:
                this_res = article_meta.copy()
                this_res['text'] = item
                articles.append(this_res)
    return articles

def filter_articles(articles, search_term, article_types=None):
    articles_filtered = list()
    for article in articles:
        if article_types is not None and article.get('articleType') not in article_types:
            continue
        if search_term in article['text']:
            articles_filtered.append(article)
    return articles_filtered

def get_term_ngram_context(articles, search_term, n_gram_window):
    context_words = list()
    for article in tqdm(articles):
        this_ngrams = list(ngrams(article['text'].split(), n_gram_window))
        ng_filtered = [ng for ng in this_ngrams if search_term in ng]
        res_set = set()
        for ng in ng_filtered:
            for word in ng:
                if word != search_term and word.lower() not in stopwords.words('english'):
                    res_set.add(word)
        context_words.extend(list(res_set))
    return Counter(context_words)

def get_filelist_by_decade(files, filter_decade):
    files_of_interest = list()
    for file in tqdm(files):
        content = get_file_articles(file)
        if (content is None) or (len(content) == 0):
            continue
        if content.get("meta_issue_date_start", "")[:3] == filter_decade[:3]:
            files_of_interest.append(file)
    return files_of_interest

if __name__=="__main__":
    nltk.download('stopwords')
    json_pattern = os.path.join(DATA_FOLDER, "ads_1", "*", "*", "*.json")
    jsonfiles = glob(json_pattern)
    search_term = "sugar"
    article_types = ['Classified ads', 'Advertisement']
    n_gram_window = 3

    output_folder = "decade_csvs_"+search_term
    output_dir = DATA_FOLDER/output_folder
    os.makedirs(output_dir, exist_ok=True)

    for decade in range(1700, 1800, 10):
        print(f"Verarbeite Jahrzehnt: {decade}")
        files_of_interest = get_filelist_by_decade(jsonfiles, filter_decade=str(decade))
        if not files_of_interest:
            print(f"no file found for {decade}.")
            continue

        articles = get_articles(files_of_interest)
        articles_f = filter_articles(articles, search_term, article_types)
        if not articles_f:
            print(f"no articles found for keyword '{search_term}' for the decade {decade}.")
            continue

        context_counter = get_term_ngram_context(articles_f, search_term, n_gram_window)
        df = pd.DataFrame.from_dict(context_counter, orient='index').reset_index()
        df.rename(columns={'index': 'term', 0: 'count'}, inplace=True)
        #df.sort_values(by='count', inplace=True, ascending=False)

        output_file = os.path.join(output_dir, f"{search_term}_context_{decade}s.csv")
        df.to_csv(output_file, index=False)
        print(f"CSV gespeichert: {output_file}")
