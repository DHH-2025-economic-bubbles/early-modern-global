import json
from collections import defaultdict
from itertools import combinations
from datetime import datetime
from collections import Counter
import ast
from settings import FOLDER_ARTICLES, DATA_FOLDER

def extract_year(entry):
    date_str = entry.get("meta_issue_date_start")
    if date_str:
        try:
            return int(datetime.strptime(date_str, "%Y-%m-%d").year)
        except ValueError:
            pass
    return None


def get_entries_in_interval(entries, start_year, end_year):
    result = []
    for entry in entries:
        year = extract_year(entry)
        if year is not None and start_year <= year <= end_year:
            result.append(entry)
    return result

def generate_cooccurence_csv(path_json):
    goods = [
        "furs",
        "tobacco",
        "rice",
        "indigo",
        "sugar",
        "rum",
        "molasses",
        "negroes"
    ]

    with open(path_json, 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    all_found_words = set()
    for entry in metadata:
        all_found_words.update(entry.get('found_words', []))

    locations = [i for i in all_found_words if i not in goods]
    #print(locations)
    # pairs = list(combinations(list(all_found_words), 2))#1600 1810
    time_intervals = [[start, start + 4] for start in range(1600, 1810, 5)]
    locloc_coocurrence={}
    goodloc_cooccurrence={}
    goodgood_cooccurence={}

    def combo_classifier(combo):
        good=0
        loc=0
        for i in combo:
            if i in goods:
                good+=1
            elif i in locations:
                loc+=1
        if good==1 and loc==1:
            return "goodloc"
        elif good==2:
            return "goodgood"
        elif loc==2:
            return "locloc"

    for interval in time_intervals:
        print(f"Examining {interval}")
        entries = get_entries_in_interval(metadata,interval[0],interval[1])
        if entries:
            print(f"Found {len(entries)} articles")
            tag = str(interval[0]) + "_" + str(interval[1])
            goodloc_cooccurrence[tag] = {}
            goodgood_cooccurence[tag] = {}
            locloc_coocurrence[tag] = {}
            for entry in entries:
                words = entry.get("found_words")
                if len(words)>1:
                    word_combos = [tuple(sorted(pair)) for pair in combinations(list(words), 2)]
                    word_combos_count = Counter(word_combos)


                    for combo, count in word_combos_count.items():
                        combo_type = combo_classifier(combo)
                        if combo_type=="locloc":
                            if repr(combo) not in locloc_coocurrence[tag].keys():
                                locloc_coocurrence[tag][repr(combo)]=1
                            else:
                                locloc_coocurrence[tag][repr(combo)]+=1

                        elif combo_type=="goodloc":
                            if repr(combo) not in goodloc_cooccurrence[tag].keys():
                                goodloc_cooccurrence[tag][repr(combo)]=1
                            else:
                                goodloc_cooccurrence[tag][repr(combo)]+=1
                        elif combo_type=="goodgood":
                            if repr(combo) not in goodgood_cooccurence[tag].keys():
                                goodgood_cooccurence[tag][repr(combo)]=1
                            else:
                                goodgood_cooccurence[tag][repr(combo)]+=1
                        else:
                            print(f"Problematic combo {combo}")


    with open(DATA_FOLDER / 'locloc_counts.json', 'w', encoding='utf-8') as f:
        json.dump(locloc_coocurrence, f, indent=2)
    with open(DATA_FOLDER / 'goodloc_counts.json', 'w', encoding='utf-8') as f:
        json.dump(goodloc_cooccurrence, f, indent=2)
    with open(DATA_FOLDER / 'goodgood_counts.json', 'w', encoding='utf-8') as f:
        json.dump(goodgood_cooccurence, f, indent=2)

if __name__=="__main__":
    generate_cooccurence_csv(FOLDER_ARTICLES / "detect_words.json")