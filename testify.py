links = []

with open('list_1.txt', 'r') as file:
    # Loop over each line in the file
    for line in file:
        line = line.strip()
        if line.startswith("http"):
            links.append(line)

print(links)