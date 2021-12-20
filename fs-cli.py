import requests
import json
import config
import numpy

# helper function to translate fahrenheit to celcius
def calc_celcius(Tf):
    return (Tf - 32) * (5/9)

# helper function to translate celcius to fahrenheit
def calc_fahrenheit(Tc):
    return (Tc * (9/5)) + 32

# calculate the wet bulb temperature
# takes the temperature (T) in Fahrenheit and the Relative Humitidy (rh) 
# returns the wet-bulb temperature in Fahrenheit
def calc_wet_bulb(T, rh):
    T = calc_celcius(T)   # convert temp to celcius
    rh /= 100             # convert to percentage
    Tw = T * numpy.arctan([0.151977 * (rh + 8.313659)**(1/2)])[0] + numpy.arctan([T + rh])[0] - numpy.arctan([rh - 1.676331])[0] + 0.00391838 *(rh)**(3/2) * numpy.arctan([0.023101 * rh])[0] - 4.686035
    return calc_fahrenheit(Tw)

# loads the ski resorts data from a file and returns the json
def load_ski_resorts():
    f = open(f'data/ski-resorts.json')
    try:
        data = json.load(f)
    finally:
        f.close()
    return data

# loads the forecast data from a file and returns the json
def load_forecast_file():
    f = open('data/forecast.json')
    try:
        data = json.load(f)
    finally:
        f.close()
    return data

# loads the weather forecast for a given lat / lon coordinate
def load_forecast(lat, lon):
    url = config.AERISWEATHER_API_URL+lat+','+lon
    response = requests.request("GET", url, headers=config.AERIS_API_HEADERS)
    data = json.loads(response.text)
    return data

# save the weather forecast json to a text file
def save_forecast(f, id):
    with open(f'data/forecast-{id}.json', 'w') as outfile:
        json.dump(f, outfile, indent=4)

def refresh():
    resorts = load_ski_resorts()
    for ski_resort in resorts['resorts']:
        forecast = load_forecast(ski_resort['location']['lat'], ski_resort['location']['long'])
        save_forecast(forecast, ski_resort['id'])

def forecast():
    pass
    # print("==========================================================")
    # print("ID: ", ski_resort['id'])
    # print("Resort: ", ski_resort['name'])
    # # print(forecast['response'])
    # for period in forecast['response'][0]['periods']:
    #     # print(period)
    #     print("Date: ", period['validTime'])
    #     print("Min Temp F: ", period['minTempF'])
    #     print("Max Temp F: ", period['maxTempF'])
    #     print("Min Humidity: ", period['minHumidity'])
    #     print("Max Humidity: ", period['maxHumidity'])
    #     print("Min Wet Bulb Temp F: ", round(calc_wet_bulb(int(period['minTempF']), int(period['minHumidity']))))
    #     print("Max Wet Bulb Temp F: ", round(calc_wet_bulb(int(period['maxTempF']), int(period['maxHumidity']))))
    #     print('\n')

def detail(resort_id):
    pass

def main():
    refresh()

main()
