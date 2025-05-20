import json
from glob import glob
from nltk.util import ngrams
import re
from collections import Counter
from nltk.corpus import stopwords
import nltk
from tqdm import tqdm
import pandas as pd


nltk.download('stopwords')


def get_file_articles(floc):
    with open(floc, 'r') as jsonfile:
        res = json.load(jsonfile)
    return res


def get_articles(files_list):
    for file in files_list:
        articles.extend(get_file_articles(file))
    return articles


def get_clean_text(article):
    pattern = re.compile('[\W_]+')
    text = article['text'].split()
    processed = list()
    for item in text:
        processed_item = pattern.sub('', item.lower())
        if len(processed_item) > 0:
            processed.append(processed_item)
    return processed


def filter_articles(articles, search_term, article_types=None):
    articles_filtered = list()
    for article in articles:
        if article_types is not None:
            if article['articleType'] not in article_types:
                pass
        if search_term in article['text'].lower():
            articles_filtered.append(article)
    return articles_filtered


def get_term_ngram_context(articles, search_term, n_gram_window):
    context_words = list()
    for article in tqdm(articles):
        this_ngrams = list(ngrams(get_clean_text(article), n_gram_window))
        ng_filtered = list()
        for ng in this_ngrams:
            if search_term in ng:
                ng_filtered.append(ng)
        res_set = set()
        for ng in ng_filtered:
            for word in ng:
                if (word != search_term) and word not in stopwords.words('english'):
                    res_set.add(word)
        context_words.extend(list(res_set))
    return Counter(context_words)


jsonfiles = glob("data/json_res/*.json")
articles = get_articles(jsonfiles[:10000])
articles_f = filter_articles(articles, 'sugar', ['Classified ads', 'Advertisement'])


search_term = "sugar"
articles_f = filter_articles(articles, search_term, ['Classified ads', 'Advertisement'])
sugar_context = get_term_ngram_context(articles_f, search_term, 3)
sugar_df = pd.DataFrame.from_dict(sugar_context, orient='index').reset_index()

search_term = "tobacco"
articles_f = filter_articles(articles, search_term, ['Classified ads', 'Advertisement'])
tobacco_context = get_term_ngram_context(articles_f, search_term, 3)
tobacco_df = pd.DataFrame.from_dict(tobacco_context, orient='index').reset_index()

search_term = "coffee"
articles_f = filter_articles(articles, search_term, ['Classified ads', 'Advertisement'])
coffee_context = get_term_ngram_context(articles_f, search_term, 3)
coffee_df = pd.DataFrame.from_dict(coffee_context, orient='index').reset_index()


