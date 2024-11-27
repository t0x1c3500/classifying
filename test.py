import json

with open('./list_18/inputs/list_18-input.json', 'r') as r_json:
    needed_test = json.loads(r_json.read())

print(len(needed_test))