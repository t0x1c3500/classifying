import json
from openai import OpenAI
import time
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

system_prompt = (
    "Given the list of products sold by an online store, rate the likelihood that this store is selling diverse and "
    "inhomogeneous products. Please return an integer from 0 to 100, where 0 indicates very similar or homogeneous "
    "products and 100 indicates a highly diverse, divergent range of products and product that are more likely used"
    "for dropshipping, modern and trendy type of products"
)


def analyze_store(store_id, product_titles):
    """Analyzes a single store's product titles and returns the dropshipping likelihood percentage."""
    try:
        # Run a completion request with the product titles
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "\n".join(product_titles)}
            ],
            max_tokens=1,
            temperature=0.0,
        )
        response_message = response.choices[0].message.content
        likelihood = int(response_message.strip())
        return store_id, likelihood

    except Exception as e:
        print(f"Error analyzing store {store_id}: {e}")
        return store_id, None


# Batch processing for 40,000 stores with store ID tracking
def batch_process(stores_data):
    results = []
    for idx, product_titles in stores_data.items():
        store_id, likelihood = analyze_store(idx, product_titles)
        results.append((store_id, likelihood))

        time.sleep(0.05)

        print(f"Processed {idx}")

    return results


with open('./list_1-formatted.json', 'r') as read_json:
    stores_data = json.loads(read_json.read())

results = batch_process(stores_data)

for store_id, likelihood in results:
    print(f"Store {store_id}: Dropshipping Likelihood = {likelihood}%")
    with open(f"./list_1/processed/{store_id}.txt", 'w') as write_store:
        write_store.write(f"{likelihood}")