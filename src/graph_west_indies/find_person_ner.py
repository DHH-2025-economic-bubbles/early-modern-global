import json
import sys
import re

# Target person from command line argument or default to "edward"
target_person = "andrew haskell"
# khan

# Load the data
with open('/home/cedric/repos/early-modern-global/data/articles_west_indies/articles_west_indies_with_persons.jsonl', 'r') as f:
    data = [json.loads(line) for line in f if line.strip()]

print(f"\nTexts associated with: {target_person}\n")

article_count = 0
for article in data:
    if target_person in article.get('persons', []):
        article_count += 1
        
        # Print article metadata
        print(f"ARTICLE {article_count}:")
        print(f"Date: {article.get('meta_issue_date_start', 'Unknown')}")
        print(f"Newspaper: {article.get('meta_newspaper_title', 'Unknown')}")
        print(f"Article Type: {article.get('articleType', 'Unknown')}")
        
        # Print only text paragraphs containing the person
        if 'texts' in article:
            print("\nText paragraphs containing the person:")
            found_in_text = False
            
            for i, text in enumerate(article['texts']):
                # Case-insensitive search for the person's name
                if re.search(target_person, text, re.IGNORECASE):
                    found_in_text = True
                    print(f"\nParagraph {i+1}:")
                    
                    # Highlight the person's name in the text
                    highlighted_text = re.sub(
                        f'({target_person})', 
                        r'**\1**', 
                        text, 
                        flags=re.IGNORECASE
                    )
                    print(highlighted_text)
            
            if not found_in_text:
                print("Person listed in 'persons' field but not found directly in text paragraphs")
        else:
            print("No text content available")
        
        print("\n" + "=" * 50 + "\n")

if article_count == 0:
    print(f"No articles found mentioning {target_person}")
else:
    print(f"Found {article_count} articles mentioning {target_person}")