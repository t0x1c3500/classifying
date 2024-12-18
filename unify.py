import os
import json

directory_path = './list_18/products'
all_products_list = {}

for filename in os.listdir(directory_path):
    if filename.endswith('.json'):
        file_path = os.path.join(directory_path, filename)

        try:
            with open(f"./pipi/list_18/{filename}", 'r') as i_file:
                i_data = json.load(i_file)

                if i_data.get('ads', 0):
                    with open(file_path, 'r') as file:
                        try:
                            data = json.load(file)
                            products = [d['product_title'] for d in data if 'product_title' in d]
                            all_products_list[filename.replace('.json', '')] = products
                        except json.JSONDecodeError as e:
                            print(f"Error parsing {filename}: {e}")
        except FileNotFoundError:
            print(f"The file at {file_path} does not exist.")


with open('./list_18/inputs/list_18-input.json', 'w', encoding="utf-8") as write_json:
    write_json.write(json.dumps(all_products_list, ensure_ascii=False))