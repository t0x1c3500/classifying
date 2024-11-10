formatted_lines = []
with open('./list_5/inputs/list_5.txt', 'r') as file:
    for line in file:
        formatted_lines.append(f"https://{line.strip()}/collections/all?sort_by=created-descending")

with open('./list_5/inputs/list_5-pre.txt', 'w') as file:
    for line in formatted_lines:
        file.write(line + '\n')