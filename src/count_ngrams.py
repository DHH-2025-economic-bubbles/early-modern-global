import json
from glob import glob
from nltk.util import ngrams
import re
from collections import Counter
from nltk.corpus import stopwords
import nltk
from tqdm import tqdm
import pandas as pd


#nltk.download('stopwords')


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


#def get_clean_text(article):
#    pattern = re.compile('[\W_]+')
#    text = article['text'].split()
#    processed = list()
#    for item in text:
#        processed_item = pattern.sub('', item.lower())
#        if len(processed_item) > 0:
#            processed.append(processed_item)
#    return processed


def filter_articles(articles, search_term, article_types=None):
    articles_filtered = list()
    for article in articles:
        if article_types is not None:
            if article['articleType'] not in article_types:
                pass
        if search_term in article['text']:
            articles_filtered.append(article)
    return articles_filtered


def get_term_ngram_context(articles, search_term, n_gram_window):
    context_words = list()
    for article in tqdm(articles):
        this_ngrams = list(ngrams(article['text'].split(), n_gram_window))
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


def get_filelist_by_decade(files, filter_decade):
    files_of_interest = list()
    for file in tqdm(files):
        content = get_file_articles(file)
        if (content is None) or (len(content) == 0):
            continue
        if content["meta_issue_date_start"][:3] == filter_decade[:3]:
            files_of_interest.append(file)
    return files_of_interest


# meta_df = pd.read_csv("early-modern-global/bl_newspapers_meta.csv")
# meta_df.loc[(meta_df["issue_date_start"].str[:3] == "171"), ["article_id"]]

jsonfiles = glob("ads_1/1/*.json")

files_of_interest = get_filelist_by_decade(jsonfiles, filter_decade="1700")
articles = get_articles(files_of_interest)

search_term = "tobacco"
articles_f = filter_articles(articles, search_term, ['Classified ads', 'Advertisement'])
sugar_context = get_term_ngram_context(articles_f, search_term, 3)
sugar_df = pd.DataFrame.from_dict(sugar_context, orient='index').reset_index()
sugar_df.rename({'index': 'term', 0: 'count'}, axis=1, inplace=True)
sugar_df.sort_values(by=0, inplace=True, ascending=False)
sugar_df.to_csv("./test.csv", index=False)

