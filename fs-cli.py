import requests
import json
import config

# loads the ski resorts data from a file and returns the json
def load_ski_resorts():
    f = open('ski-resorts.json')
    data = json.load(f)
    return data

# loads the weather forecast for a given lat / lon coordinate
def load_forecast(lat, lon):
    url = config.AERISWEATHER_API_URL+lat+','+lon
    response = requests.request("GET", url, headers=config.AERIS_API_HEADERS)
    return response.text

def main():
    resorts = load_ski_resorts()
    
    for r in resorts['resorts']:
        print(r['name'] + ": " + r['location']['state-short'])
        forecast = load_forecast(r['location']['lat'],r['location']['long'])
        # for f in forecast['reponse']['periods']:
        #     print(f['maxTempF'], end=' ')
        print(forecast)
    # print(resorts)

main()


# print(response.text)

# with open('forecast.json', 'w', encoding='utf-8') as f:
#     json.dump(response.text, f, ensure_ascii=False, indent=4)