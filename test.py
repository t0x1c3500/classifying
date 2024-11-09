import json

with open('./list_1-input-corrected.json', 'r') as r_json:
    needed_test = json.loads(r_json.read())

print(len(needed_test))