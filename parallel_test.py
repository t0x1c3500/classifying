import asyncio
import openai
import aiohttp
import time
import json

openai.api_key = ("sk-proj-zGDtmNeqhraacL4u-df0Ss3cotBYokc2C8l42FGHq_ekVQEQ"
                  "-rWlPEohUoaZivg6TvpiDy9Gs7T3BlbkFJWUERsgDuMB3pKL8DubJPC0bw6rvUAgmmyjgtMzWyRBRZUjodrMX_3j_"
                  "8A715wD6aPMCdYVa70A")


async def fetch_with_retry(session, prompt, product_titles, website, max_retries=5):
    print(f"Processing {website}")
    for attempt in range(max_retries):
        try:
            async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": "gpt-4",
                        "messages": [
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": "\n".join(product_titles)}
                        ],
                        "max_tokens": 1,
                        "temperature": 0.0,
                    },
                    headers={"Authorization": f"Bearer {openai.api_key}"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    with open(f"./list_1/results/{website}.txt", 'w') as write_s:
                        write_s.write(f"{result['choices'][0]['message']['content'].strip()}")
                    return website, result['choices'][0]['message']['content'].strip()
                elif response.status == 429:
                    print("Rate limit hit. Retrying...")
                    await asyncio.sleep(2 ** attempt)
                else:
                    response.raise_for_status()
        except Exception as e:
            print(f"Error: {e}")
    return website, None


# Main asynchronous function
async def main(prompts, products_l, websites_l, concurrency=10):
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(concurrency)

        async def sem_fetch(prompt, product, store_id):
            async with semaphore:
                await asyncio.sleep(1)
                return await fetch_with_retry(session, prompt, product, store_id)

        tasks = [sem_fetch(prompt, products_l[x], websites_l[x]) for x, prompt in enumerate(prompts)]
        return await asyncio.gather(*tasks)


with open('./list_1-input-corrected.json', 'r') as read_json:
    stores_data = json.loads(read_json.read())
products_only = [product_list for x, product_list in stores_data.items()]
websites_only = [x for x, product_list in stores_data.items()]


single_prompt = ("Given the list of products sold by an online store, rate the likelihood that this store is selling "
                 "diverse and inhomogeneous products. Please return an integer from 0 to 100, where 0 indicates very "
                 "similar or homogeneous products and 100 indicates a highly diverse, divergent range of products and "
                 "product that are more likely used for dropshipping, modern and trendy type of products")
prompts = [single_prompt] * len(products_only)


start_time = time.time()
results = asyncio.run(main(prompts, products_only, websites_only, concurrency=3))
end_time = time.time()

print(f"Time taken: {end_time - start_time} seconds")