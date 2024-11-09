formatted_lines = []
with open('./list_3/inputs/list_3.txt', 'r') as file:
    for line in file:
        formatted_lines.append(f"https://{line.strip()}/collections/all?sort_by=created-descending")

with open('./list_3/inputs/list_3-pre.txt', 'w') as file:
    for line in formatted_lines:
        file.write(line + '\n')