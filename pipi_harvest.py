import json
import os
from pipiharvest.make_request import req
from pipiharvest.misc import check_timestamp_and_parse, chunk_list
import concurrent.futures

with open('./pipi/accounts.json', 'r') as all_accounts_read:
    all_accounts = json.loads(all_accounts_read.read())
    all_accounts = all_accounts[3000:]

all_targets = []
for filename in os.listdir('./list_16/products'):
    if filename.endswith('.json'):
        file_path = os.path.join('./list_16/products', filename)
        domain_name = filename.replace('.json', '')
        all_targets.append(domain_name)


def process_search(processing_target_chunk, index):
    processing_account = all_accounts[index]

    login_payload = {
        "email": processing_account['email_id'],
        "password": processing_account['password'],
        "device_id": processing_account['device_id'],
    }
    del processing_account['email_id']
    del processing_account['password']
    del processing_account['status']
    del processing_account['session_id']
    if login_request := req('https://www.pipiads.com/v1/api/member/login', 'PUT', login_payload, processing_account):
        access_token = json.loads(login_request.content.decode('utf-8')).get('access_token', False)
        if access_token:
            processing_account['access_token'] = access_token
            processing_account['referer'] = ('https://www.pipiads.com/ad-search?plat_type=1&search_type=1&sort=2'
                                             '&sort_type=desc&current_page=1')

            for processing_target in processing_target_chunk:
                search_payload = {
                    "search_type": 1,
                    "extend_keywords": [
                        {
                            "type": 1,
                            "keyword": processing_target
                        }
                    ],
                    "sort": 2,
                    "sort_type": "desc",
                    "current_page": 1,
                    "page_size": 20
                }
                if search_request := req('https://www.pipiads.com/v3/api/at/video/search', 'POST',
                                         search_payload, processing_account, login_request.cookies):
                    ads_count = 0
                    ad_targets = []
                    last_active = False
                    is_active = False

                    ads_content_object = search_request.json()
                    ads_exists = ads_content_object.get('result', {}).get('page', {}).get('total_count', -1)
                    if ads_exists:
                        ads_count = ads_exists
                        [is_active, last_active] = check_timestamp_and_parse(
                            ads_content_object['result']['data'][0]['last_put_time'])
                        ad_targets = ads_content_object['result']['data'][0]['fetch_region']

                    with open(f"./pipi/list_16/{processing_target}.json", 'w') as processing_store:
                        processing_store.write(json.dumps({
                            'store': processing_target,
                            'ads': ads_count,
                            'active': is_active,
                            'last_active': last_active,
                            'targets': ad_targets
                        }))

                    print(f"[SUCCESS] {processing_target}")
                else:
                    print(f"[FAILED-PROCESSING] {processing_target}")
        else:
            print(f"[FAILED-ACCESS_TOKEN] {login_payload['email']}")
    else:
        print(f"[FAILED-LOGIN] {login_payload['email']}")


filtered_targets = all_targets
processing_targets = filtered_targets[:len(all_accounts) * 10]
chunked_targets = chunk_list(processing_targets, 10)

print("Got Accounts, Now starting the process !!")
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    futures = []
    for i, i_targets in enumerate(chunked_targets):
        futures.append(executor.submit(process_search, i_targets, i))

    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"Error occurred: {e}")
