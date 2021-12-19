import requests
import json
import config

url = config.AERISWEATHER_API_URL+"39.15,-84.88"
response = requests.request("GET", url, headers=config.AERIS_API_HEADERS)

# print(response.text)

# with open('forecast.json', 'w', encoding='utf-8') as f:
#     json.dump(response.text, f, ensure_ascii=False, indent=4)