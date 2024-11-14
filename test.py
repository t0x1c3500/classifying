import json

with open('./list_6/inputs/list_6-input.json', 'r') as r_json:
    needed_test = json.loads(r_json.read())

print(len(needed_test))