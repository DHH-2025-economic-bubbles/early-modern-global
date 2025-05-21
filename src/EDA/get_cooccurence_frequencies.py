import json
from collections import defaultdict
from itertools import combinations
from datetime import datetime
from collections import Counter
import ast
from settings import FOLDER_ARTICLES, DATA_FOLDER
import csv
import settings
from collections import defaultdict

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
        "molasses"]
    peoples = ["negroes","slave"]

    with open(path_json, 'r', encoding='utf-8') as file:
        metadata = [json.loads(line) for line in file]

    all_found_words = set()
    for entry in metadata:
        found_words_dict = entry.get('found_words', {})
        for word_list in found_words_dict.values():
            all_found_words.update(word_list)


    locations = [i for i in all_found_words if i not in goods]
    #print(locations)
    # pairs = list(combinations(list(all_found_words), 2))#1600 1810
    time_intervals = [[start, start + 4] for start in range(1600, 1810, 5)]
    locloc_coocurrence={}
    goodloc_cooccurrence={}
    goodgood_cooccurence={}
    peopleloc_coocurrence={}

    def combo_classifier(combo):
        
        good=0
        loc=0
        people=0
        for i in combo:
            if i in goods:
                good+=1
            elif i in peoples:
                people+=1
            elif i in locations:
                loc+=1

        if good==1 and loc==1:
            return "goodloc"
        elif people ==1 and loc==1:
            return "peopleloc"
        elif loc==2:
            return "locloc"
        elif good==1 and people==1 or good==2 or people==2:
            return "goodgood"
        else:
            return "problem"


    for interval in time_intervals:
        print(f"Examining {interval}")
        entries = get_entries_in_interval(metadata,interval[0],interval[1])
        if entries:
            print(f"Found {len(entries)} articles")
            tag = str(interval[0]) + "_" + str(interval[1])
            goodloc_cooccurrence[tag] = {}
            peopleloc_coocurrence[tag] = {}
            goodgood_cooccurence[tag] = {}
            locloc_coocurrence[tag] = {}
            # combo_types = {1:"locloc",2:"peopleloc",3:"goodloc",4:"goodgood"}
            for entry in entries:
                paragraphs = entry.get("found_words")
                for para_idx,para_words in paragraphs.items():
                    if len(para_words)>1:
                        word_combos = [tuple(sorted(pair)) for pair in combinations(list(para_words), 2)]
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
                            elif combo_type=="peopleloc":
                                if repr(combo) not in peopleloc_coocurrence[tag].keys():
                                    peopleloc_coocurrence[tag][repr(combo)]=1
                                else:
                                    peopleloc_coocurrence[tag][repr(combo)]+=1
                            else:
                                print(f"Problematic combo {combo}")


    with open(DATA_FOLDER / 'locloc_counts.json', 'w', encoding='utf-8') as f:
        json.dump(locloc_coocurrence, f, indent=2)
    with open(DATA_FOLDER / 'goodloc_counts.json', 'w', encoding='utf-8') as f:
        json.dump(goodloc_cooccurrence, f, indent=2)
    with open(DATA_FOLDER / 'goodgood_counts.json', 'w', encoding='utf-8') as f:
        json.dump(goodgood_cooccurence, f, indent=2)
    with open(DATA_FOLDER / 'peopleloc_counts.json', 'w', encoding='utf-8') as f:
        json.dump(peopleloc_coocurrence, f, indent=2)

def convert_cooccurrence(coocurrence,exclude_countries=True):
    #convert co occurence into file format as Ila requested to generate geo visualizations

    with open(DATA_FOLDER / f'{coocurrence}_counts.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    PREDEFINED_COUNTRIES=['india',
                'japan',
                'nigeria',
                'guyana',
                'georgia',
                'ghana',
                'jamaica',
                'haiti',
                'canada',
                'nicaragua',
                'panama',
                'france']
    
    PREDEFINED_GOODS = [
                    "furs",
                    "tobacco",
                    "rice",
                    "indigo",
                    "sugar",
                    "rum",
                    "molasses",
                    "people"]
    PREDEFINED_PEOPLE=["negroes","slave"]
    

    goods_data = defaultdict(list)


    for time_interval, co_occurrences in data.items():
        for pair, count in co_occurrences.items():
        
            try:
                item1, item2 = eval(pair)
            except:
                continue

            if item1 in PREDEFINED_PEOPLE:
                item1="people"
            if item2 in PREDEFINED_PEOPLE:
                item2="people"
            good = None
            location = None
            if exclude_countries==True:
                if item1 in PREDEFINED_GOODS and item2 not in PREDEFINED_COUNTRIES and item2 not in PREDEFINED_GOODS:
                    good = item1
                    location = item2
                elif item2 in PREDEFINED_GOODS and item1 not in PREDEFINED_COUNTRIES and item1 not in PREDEFINED_GOODS:
                    good = item2
                    location = item1
                
            elif exclude_countries==False:
                if item1 in PREDEFINED_GOODS and item2 not in PREDEFINED_GOODS:
                    good = item1
                    location = item2
                elif item2 in PREDEFINED_GOODS and item1 not in PREDEFINED_GOODS:
                    good = item2
                    location = item1

            if good and location:
                goods_data[good].append({
                    'time_interval': time_interval,
                    'location': location,
                    'co_occurrence_frequency': count
                })
    for good, rows in goods_data.items():
        filename = f"{good}_co_occurrences.csv"
        sorted_rows = sorted(rows, key=lambda x: (x['time_interval'], x['location']))
        with open(DATA_FOLDER/filename, 'w', newline='') as csvfile:
            fieldnames = ['time_interval', 'location', 'co_occurrence_frequency']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted_rows)

        print(f"Created {filename} with {len(sorted_rows)} rows")
    

if __name__=="__main__":

    generate_cooccurence_csv(DATA_FOLDER / "detect_words.jsonl")
    convert_cooccurrence(coocurrence="goodloc")
    convert_cooccurrence(coocurrence="peopleloc")