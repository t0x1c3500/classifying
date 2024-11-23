import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from urllib.parse import urlparse

links = []

with open('./list_2-1/inputs/list_2-1-pre.txt', 'r') as file:
    for line in file:
        line = line.strip()
        if line.startswith("http"):
            links.append(line)


def format_domain(domain_name):
    domain = urlparse(domain_name).netloc
    if domain.startswith("www."):
        domain = domain[4:]

    return domain


def fix_json_structure(json_like_str):
    json_like_str = re.sub(r'([a-zA-Z0-9_]+):', r'"\1":', json_like_str)
    json_like_str = re.sub(r':\s*([a-zA-Z0-9_]+)([,\}\]])', r': "\1"\2', json_like_str)
    json_like_str = re.sub(r'"\s*(true|false|null)\s*"', r'\1', json_like_str)

    return json_like_str


def check_products(url, index, page=1):
    return_products = []

    try:
        domain = format_domain(url)
        print(f"[{index}-{page}] Processing {domain}\n")
        response = requests.get(f"{url}", timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        scripts = soup.find_all('script')
        found = False

        for script in scripts:
            match = re.search(r'webPixelsManagerAPI\.publish\("collection_viewed", ({"collection":{.+})\);},'
                              r'"https://(www\.)?' + domain + '/cdn"', script.text)
            if match:
                product_details = match.group(1)
                try:
                    json_obj = json.loads(product_details)
                    if len(json_obj.get('collection', {}).get('productVariants', [])):
                        for product_variant in json_obj.get('collection', {}).get('productVariants', []):
                            return_products.append({
                                'product_id': product_variant.get(
                                    'product', {}).get('id', '') if product_variant.get('product') else '',
                                'product_title': product_variant.get(
                                    'product', {}).get('untranslatedTitle', '') if product_variant.get(
                                    'product') else '',
                                'product_variant_title': product_variant.get('untranslatedTitle', ''),
                                'product_price': product_variant.get('price', {}),
                                'product_sku': product_variant.get('sku', ''),
                                'product_link': f"https://{domain}/" + product_variant.get(
                                    'product', {}).get('url', '') if product_variant.get('product') else '',
                                'product_image': product_variant.get('image', {}).get(
                                    'src', '') if product_variant.get('image') else '',
                            })
                    else:
                        return False
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    return False

                return return_products
        if not found:
            return False
    except requests.Timeout:
        return False
    except requests.RequestException as e:
        return False


def check_products_trigger(url, index, pn, all_collected_products=None):
    if all_collected_products is None:
        all_collected_products = []

    if got_new_products := check_products(url, index, pn):
        all_collected_products.extend(got_new_products)
        # check_products_trigger(url, index, pn + 1, all_collected_products)

    return


def process_it(link, index):
    page_number = 1
    final_products = []
    check_products_trigger(link, index, page_number, final_products)

    if len(final_products):
        domain = format_domain(link)
        print(f"Got Final Products For {domain}")
        with open(f"./list_2-1/products/{domain}.json", "w") as link_write:
            link_write.write(json.dumps(final_products))

    return True


def multi_execute(max_workers):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_param = {
            executor.submit(process_it, param, i):
                param for i, param in enumerate(links)}
        for future in as_completed(future_param):
            param = future_param[future]
            try:
                domain = format_domain(param)
                if future.result():
                    print(f"SUCCESS fetching {domain}")
                else:
                    print(f"FAILED fetching {domain}")
            except Exception as e:
                domain = format_domain(param)
                print(f"ERROR fetching {domain} | Exception -> {e}")


multi_execute(1000)
