import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

def fix_date_format(date_str):
    if not date_str:
        return date_str
    
    if re.search(r'-00$', date_str):
        return re.sub(r'-00$', '-01', date_str)
    
    return date_str

with open('/home/cedric/repos/early-modern-global/data/articles_west_indies/articles_west_indies_with_persons.jsonl', 'r') as f:
    data = [json.loads(line) for line in f if line.strip()]

extracted_data = []
for article in data:
    date_start = fix_date_format(article.get('meta_issue_date_start'))
    date_end = fix_date_format(article.get('meta_issue_date_end'))
    
    extracted_data.append({
        'persons': article.get('persons', []),
        'date_start': date_start,
        'date_end': date_end,
        'articleType': article.get('articleType'),
        'newspaperTitle': article.get('meta_newspaper_title'),
        'num_persons': len(article.get('persons', []))
    })

df = pd.DataFrame(extracted_data)

df['date_start'] = pd.to_datetime(df['date_start'], errors='coerce')
df['date_end'] = pd.to_datetime(df['date_end'], errors='coerce')

df['year'] = df['date_start'].dt.year
df['month'] = df['date_start'].dt.month

article_type_person_counts = df.groupby('articleType')['num_persons'].sum()
print("Persons by Article Type:")
print(article_type_person_counts)

person_records = []
for _, row in df.iterrows():
    for person in row['persons']:
        person_records.append({
            'person': person,
            'date_start': row['date_start'],
            'date_end': row['date_end'],
            'year': row['year'],
            'articleType': row['articleType'],
            'newspaperTitle': row['newspaperTitle']
        })

person_df = pd.DataFrame(person_records)

print("\nPeople mentioned by year:")
year_counts = person_df.groupby('year').size()
print(year_counts)

# Top mentioned people overall
top_people = person_df['person'].value_counts().head(100)
print("\nTop 100 Most Mentioned People:")
for people in list(top_people.keys()):
    print(people)
