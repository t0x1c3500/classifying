import json

with open('./list_2/inputs/list_2-input.json', 'r') as r_json:
    needed_test = json.loads(r_json.read())

print(len(needed_test))