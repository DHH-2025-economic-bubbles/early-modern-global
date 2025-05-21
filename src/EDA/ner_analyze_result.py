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

with open('/home/cedric/repos/early-modern-global/data/articles_India/articles_India_with_persons.jsonl', 'r') as f:
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
top_people = person_df['person'].value_counts().head(10)
print("\nTop 10 Most Mentioned People:")
print(top_people)

# Create a bar chart for top 10 people
plt.figure(figsize=(12, 8))
top_people.plot(kind='bar', color='skyblue')
plt.title('Top 10 Most Mentioned People')
plt.xlabel('Person')
plt.ylabel('Number of Mentions')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('top_10_people.png')

# Top mentioned people by year
print("\nTop Mentioned People by Year:")
years = sorted(person_df['year'].dropna().unique())

for year in years:
    year_data = person_df[person_df['year'] == year]
    top_year_people = year_data['person'].value_counts().head(10)
    
    if not top_year_people.empty:  # Check if we have data for this year
        print(f"\nTop people in {int(year)}:")
        print(top_year_people)
        
        # Create a bar chart for top 10 people for this year
        plt.figure(figsize=(12, 8))
        top_year_people.plot(kind='bar', color='lightgreen')
        plt.title(f'Top People Mentioned in {int(year)}')
        plt.xlabel('Person')
        plt.ylabel('Number of Mentions')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f'top_people_{int(year)}.png')

# Heatmap of top 20 people across years
top_20_overall = person_df['person'].value_counts().head(20).index.tolist()

# Create a pivot table for the heatmap
year_person_pivot = pd.pivot_table(
    person_df[person_df['person'].isin(top_20_overall)],
    values='person',
    index='year',
    columns='person',
    aggfunc='count',
    fill_value=0
)

# Plot the heatmap
plt.figure(figsize=(16, 10))
plt.pcolor(year_person_pivot, cmap='YlGnBu')
plt.yticks(np.arange(0.5, len(year_person_pivot.index)), [int(y) for y in year_person_pivot.index])
plt.xticks(np.arange(0.5, len(year_person_pivot.columns)), year_person_pivot.columns, rotation=90)
plt.colorbar(label='Mentions')
plt.title('Top 20 People Mentions Across Years')
plt.tight_layout()
plt.savefig('top_20_people_by_year_heatmap.png')

print("\nSummary Statistics:")
print(f"Total number of articles: {len(df)}")
print(f"Total people mentioned: {len(person_df)}")
print(f"Unique people mentioned: {len(person_df['person'].unique())}")

earliest_date = df['date_start'].min()
latest_date = df['date_end'].max()
print(f"\nDate range: {earliest_date} to {latest_date}")

plt.figure(figsize=(10, 6))
article_type_person_counts.plot(kind='bar')
plt.title('Number of People Mentioned by Article Type')
plt.ylabel('Count')
plt.tight_layout()
plt.savefig('people_by_article_type.png')

plt.figure(figsize=(10, 6))
year_counts.plot(kind='bar')
plt.title('People Mentioned by Year')
plt.ylabel('Count')
plt.tight_layout()
plt.savefig('people_by_year.png')