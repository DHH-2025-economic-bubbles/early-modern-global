import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


all_meta_df = pd.read_csv('data/bl_newspapers_meta.csv')
all_meta_df['decade'] = all_meta_df['issue_date_start'].str[:3] + "0"
all_meta_df['decade'] = all_meta_df['decade'].astype(int)
decade_article_counts = all_meta_df['decade'].value_counts().reset_index()
decade_article_counts.rename({'count': 'articles'}, axis=1, inplace=True)
issues_df = all_meta_df.drop_duplicates('issue_id')
decade_issue_counts = issues_df['decade'].value_counts().reset_index()
decade_issue_counts.rename({'count': 'issues'}, axis=1, inplace=True)
all_counts = decade_article_counts.merge(decade_issue_counts, on='decade')
all_counts.sort_values('decade', inplace=True)


sns.lineplot(data=all_counts,
             x="decade", y='articles')
plt.tight_layout()
plt.savefig(f'findings/article_count_whole_dataset.png')
plt.close('all')

sns.lineplot(data=all_counts,
             x="decade", y='issues')
plt.tight_layout()
plt.savefig(f'findings/issue_count_whole_dataset.png')
plt.close('all')
