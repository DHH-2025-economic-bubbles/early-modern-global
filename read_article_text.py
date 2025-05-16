import json
import sys


if len(sys.argv) < 2:
    print("Provide articleID as argument.")
    exit()

article_id = sys.argv[1]

# article_id = "NICNF0328-C00000-N0000013-00020-001"
ai_split = article_id.split('-')
thisfile = ai_split[0][-3:] + "_" + ai_split[2] + ".json"
# thisfile = "328_N0000013.json"
floc = 'data/json_res/' + thisfile

with open(floc, 'r') as jsonfile:
    jsondata = json.load(jsonfile)

for item in jsondata:
    if item['articleID'] == article_id:
        print(item['text'])

