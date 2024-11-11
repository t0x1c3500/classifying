import json

with open('./list_3/inputs/list_3-input.json', 'r') as r_json:
    needed_test = json.loads(r_json.read())

print(len(needed_test))