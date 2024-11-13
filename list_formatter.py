formatted_lines = []
with open('./list_11/inputs/list_11.txt', 'r') as file:
    for line in file:
        formatted_lines.append(f"https://{line.strip()}/collections/all?sort_by=created-descending")

with open('./list_11/inputs/list_11-pre.txt', 'w') as file:
    for line in formatted_lines:
        file.write(line + '\n')