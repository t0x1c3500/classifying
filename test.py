import json

with open('./list_13/inputs/list_13-input.json', 'r') as r_json:
    needed_test = json.loads(r_json.read())

print(len(needed_test))