from os import abort
import config
import requests
import json
import datetime
import numpy
import pathlib

def calc_celcius(Tf) -> float:
    """Return a temperature converted from Fahrenheit to Celcius
    
    Keyword arguments:
    Tf -- the temperature in Fahrenheit
    """
    return (Tf - 32) * (5/9)

def calc_fahrenheit(Tc) -> float:
    """Return a temperature converted from Celcius to Fharenheit
    
    Keyword arguments:
    Tc -- the temperature in Celcius
    """
    return (Tc * (9/5)) + 32

# Function immplemented but not in use. 
# Easier to just test the boundaries of the temp/rel. humidity matrix.
def calc_wet_bulb(T, rh) -> float:
    """Return a wet-bulb temperature based on Temperature and Relative Humidity
    
    Keyword arguments:
    T -- the temperature in Celcius
    rh -- the relative humidity
    """
    T = calc_celcius(T)   
    rh /= 100             
    Tw = T * numpy.arctan([0.151977 * (rh + 8.313659)**(1/2)])[0] + numpy.arctan([T + rh])[0] - numpy.arctan([rh - 1.676331])[0] + 0.00391838 *(rh)**(3/2) * numpy.arctan([0.023101 * rh])[0] - 4.686035
    return calc_fahrenheit(Tw) 

def is_good_conditions(T, rh) -> bool:
    """Return whether or not the temperature and relative humidity are favorable for snow making
    
    Keyword arguments: 
    T -- the temperature in Celcius 
    rh -- the relative humidity
    """
    
    conditions_are_good = False

    if T <= 20:
        conditions_are_good =  True
    elif T <= 21 and rh <= 94:
        conditions_are_good =  True
    elif T <= 22 and rh <= 85:
        conditions_are_good =  True
    elif T <= 23 and rh <= 76:
        conditions_are_good =  True
    elif T <= 24 and rh <= 66:
        conditions_are_good =  True
    elif T <= 25 and rh <= 54:
        conditions_are_good =  True
    elif T <= 26 and rh <= 39:
        conditions_are_good =  True
    elif T <= 27 and rh <= 25:
        conditions_are_good =  True
    elif T <= 28 and rh <= 15:
        conditions_are_good =  True
    elif T <= 29 and rh <= 10:
        conditions_are_good =  True
    else:
        conditions_are_good = False
    
    return conditions_are_good

def load_ski_resorts() -> list:
    """Returns a list of ski resorts
    
    """
    f = open(f'data/ski-resorts.json')
    try:
        data = json.load(f)
    finally:
        f.close()
    return data

def load_ski_resort(text_id) -> dict:
    """Return forecast data from a file
    
    Keyword arguments: 
    text_id -- the code name of the resort to be returned 
    """
    f = open(f'data/ski-resorts.json')
    try:
        resort_list = json.load(f)
    finally:
        f.close()

    found_value = [resort for resort in resort_list if resort['text_id'] == text_id]
    return found_value[0]

def load_forecast_file(id) -> dict:
    """Return forecast data from a file
    
    Keyword arguments: 
    id -- the resort_id to determine which forecast file to pull 
    """
    f = open(f'data/forecast-{id}.json')
    try:
        data = json.load(f)
    finally:
        f.close()
    return data

def load_forecast(lat, lon) -> dict:
    """Return weather foreacast for a given lat/long coordinate
    
    Keyword arguments: 
    lat -- the latitude of the weather forecast coordinates
    long -- the longitude of the weather forecast coordinates
    """
    url = config.AERISWEATHER_API_URL+lat+','+lon
    response = requests.request("GET", url, headers=config.AERIS_API_HEADERS)
    data = json.loads(response.text)
    return data

def save_forecast(f, id):
    """save the weather forecast json to a text file
    
    Keyword arguments: 
    f -- the forecast data
    id -- the is of the ski resort
    """
    with open(f'data/forecast-{id}.json', 'w') as outfile:
        json.dump(f, outfile, indent=4)

def forecast_summary():
    """returns a list of forecast summaries for all resorts

    """
    
    forecastSummary = []
    
    resorts = load_ski_resorts()
    
    for ski_resort in resorts:
        
        forecastData = {
                'id' : ski_resort['id'],
                'text_id' : ski_resort['text_id'],
                'name' : ski_resort['name'],
                'state' : ski_resort['location']['state'],
                'url' : ski_resort['links']['main_url'],
                'conditions_url' : ski_resort['links']['conditions_url'],
                'map_url' : ski_resort['links']['map_url'],
                'logo': ski_resort['logo'],
                'forecast' : []
            }

        forecast = load_forecast_file(ski_resort['id'])
        
        for period in forecast['response'][0]['periods']:
            
            conditions = ''
            if period['snowIN'] != 0: 
                conditions = 'Snow'
            elif is_good_conditions(period['minTempF'],period['minHumidity']):
                conditions = 'Faux'
            
            forecastData['forecast'].append({
                'date' : str(datetime.datetime.strptime(period['validTime'], '%Y-%m-%dT%H:%M:%S-05:00').date().strftime('%d-%b')),
                'minTemp' : period['minTempF'],
                'maxTemp' : period['maxTempF'],
                'snowIN' : period['snowIN'],
                'weather' : period['weather'],
                'humidity' : period['minHumidity'],
                'conditions' : conditions
            })

        forecastSummary.append(forecastData)

    return forecastSummary

def resort_forecast(text_id) -> list:
    """returns a list of forecast summaries for all resorts

    """

    ski_resort = load_ski_resort(text_id)
    forecast = load_forecast_file(ski_resort['id'])
    
    forecastSummary = []

    for period in forecast["response"][0]["periods"]:
        conditions = ''
        if period['snowIN'] != 0: 
            conditions = 'Snow'
        elif is_good_conditions(period['minTempF'],period['minHumidity']):
            conditions = 'Faux'
        forecastSummary.append({
            'date' : str(datetime.datetime.strptime(period['validTime'], '%Y-%m-%dT%H:%M:%S-05:00').date().strftime('%d-%b')),
            'minTemp' : period['minTempF'],
            'maxTemp' : period['maxTempF'],
            'snowIN' : period['snowIN'],
            'weather' : period['weather'],
            'humidity' : period['minHumidity'],
            'conditions' : conditions
        })
    return forecastSummary;

def forecast_date() -> str:
    fname = pathlib.Path('data/forecast-1.json')
    if fname.exists():
        mtime = datetime.datetime.fromtimestamp(fname.stat().st_mtime)
        return str(mtime.strftime('%a, %d %b @ %I:%M %p ET'))