from pathlib import Path
import json
import string

from pathlib import Path
import json


def clean_text(issue_path: Path) -> list[dict]:
    with open(issue_path, "r") as f:
        issue = json.loads(f.read())
        cleaned_issue = []
        for article in issue:
            new_article = {}
            new_article["file_name"] = Path(f.name).name
            new_article["issue_id"] = article["issueID"]
            new_article["article_id"] = article["articleID"]
            new_article["text"] = article["text"].translate(str.maketrans('', '', string.punctuation)).lower().replace("\n", "")
            cleaned_issue.append(new_article)
        return cleaned_issue


