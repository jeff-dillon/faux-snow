from flask  import abort
import requests
import json
import datetime
import numpy
import pathlib
import os
import re

SKI_RESORTS_FILE = 'data/ski_resorts.json'
FORECASTS_FILE = 'data/forecasts.json'

def calc_celcius(Tf) -> int:
    """Return a temperature converted from Fahrenheit to Celcius
    
    Keyword arguments:
    Tf -- the temperature in Fahrenheit
    """
    return round((Tf - 32) * (5/9))

def calc_fahrenheit(Tc) -> int:
    """Return a temperature converted from Celcius to Fharenheit
    
    Keyword arguments:
    Tc -- the temperature in Celcius
    """
    return round((Tc * (9/5)) + 32)

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
    Tw = (T * numpy.arctan([0.151977 * (rh + 8.313659)**(1/2)])[0] + 
        numpy.arctan([T + rh])[0] - 
        numpy.arctan([rh - 1.676331])[0] + 0.00391838 *(rh)**(3/2) * 
        numpy.arctan([0.023101 * rh])[0] - 4.686035)
    return calc_fahrenheit(Tw) 

def is_good_conditions(T, rh) -> bool:
    """Return whether or not the temperature and relative humidity are 
       favorable for snow making
    
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

def load_ski_resorts(file=SKI_RESORTS_FILE) -> list:
    """Returns a list of ski resorts
    
    """
    f = open(file)
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
    f = open(SKI_RESORTS_FILE)
    try:
        resort_list = json.load(f)
    finally:
        f.close()

    found_value = [resort for resort in 
        resort_list if resort['text_id'] == text_id]
    return found_value[0]

def load_forecast(lat, lon) -> dict:
    """Return weather foreacast for a given lat/long coordinate
    
    Keyword arguments: 
    lat -- the latitude of the weather forecast coordinates
    long -- the longitude of the weather forecast coordinates
    """
    # list the specific fields we want in the json response so we don't 
    # get a huge json file with fields we don't need
    response_fields = [
        'periods.maxTempF',
        'periods.minTempF',
        'periods.snowIN',
        'periods.minHumidity',
        'periods.weatherPrimary',
        'periods.validTime',
        'periods.weatherPrimaryCoded'
        ]
    
    url = ("https://aerisweather1.p.rapidapi.com/forecasts/"
        +lat+','+lon+'?fields='
        +','.join(response_fields))
    
    api_key = os.environ.get('API_KEY')
    
    header_vals = {
        'x-rapidapi-host': "aerisweather1.p.rapidapi.com",
        'x-rapidapi-key': api_key
    }

    response = requests.request("GET", url, headers=header_vals)
    data = json.loads(response.text)

    return data

def save_forecasts(forecasts):
    """save the weather forecast json to a text file
    
    Keyword arguments: 
    f -- the forecast data
    id -- the is of the ski resort
    """
    with open(f'data/forecasts.json', 'w') as outfile:
        json.dump(forecasts, outfile, indent=4)

def load_forecasts_from_api(resorts) -> list:
    """load the weather forecast json to a list of dict objects. 
    Returns None if we have reached the api call limit
    
    Keyword arguments: 
    resorts -- a list of resort dict objects
    """
    forecasts = []
    for ski_resort in resorts:
        forecast = load_forecast(
            ski_resort['location']['lat'], 
            ski_resort['location']['long'])
        response = forecast.get('response')

        # if the api call doesn't return a response value, 
        # exit the function and return None
        if response:

            forecastsdata = {
                "text_id" : ski_resort["text_id"],
                "forecast_date" : str(
                    datetime.datetime.now().strftime("%d/%m/%Y %I:%M %p")),
                "periods" : []
            }

            for period in forecast['response'][0]['periods']:

                match = re.search(r':[A-Z]+$',period['weatherPrimaryCoded'])

                conditions = ''
                if match:
                    # check for Blowing Snow, Snow, Snow Showers, or Wintry Mix
                    # and a snow accumulation of more that 1/4 inch
                    if (match.group() in [':BS',':S',':SW',':WM'] 
                        and period['snowIN'] > .25): 
                        conditions = 'Snow'
                    # check for a cloud code - indicates absence of non-snow 
                    # weather (ice, rain, etc.)
                    elif (is_good_conditions(
                            period['minTempF'], 
                            period['minHumidity']) 
                        and match in [':CL',':FW',':SC',':BK',':OV',':BS',':S',':SW',':WM']): 
                        conditions = 'Faux'
                
                forecastsdata['periods'].append({
                    'date' : str(
                        datetime.datetime.strptime(period['validTime'], 
                        '%Y-%m-%dT%H:%M:%S-05:00').date().strftime('%a %d')),
                    'minTemp' : period['minTempF'],
                    'maxTemp' : period['maxTempF'],
                    'snowIN' : period['snowIN'],
                    'weather' : period['weatherPrimary'],
                    'weatherCoded' : period['weatherPrimaryCoded'],
                    'humidity' : period['minHumidity'],
                    'conditions' : conditions
                })
            forecasts.append(forecastsdata)
        else:
            return
    
    return forecasts

def load_forecasts_from_file(file=FORECASTS_FILE) -> list:
    """Return forecast data from a file
    """
    f = open(file)
    try:
        data = json.load(f)
    finally:
        f.close()
    return data

def load_forecast_from_file(text_id, file=FORECASTS_FILE) -> list:
    """Return forecast data from a file
    """
    f = open(file)
    try:
        forecasts = json.load(f)
        forecast_match = next(fo for fo in forecasts \
            if fo['text_id'] == text_id)
    finally:
        f.close()
    return forecast_match

def combine_resorts_forecasts(resorts, forecasts) -> list:
    combined = []
    for resort in resorts:
        forecast_match = next(fo for fo in forecasts \
            if fo['text_id'] == resort['text_id'])
        combined.append({
            "text_id" : resort['text_id'],
            "resort" : resort,
            "forecast" : forecast_match
        })
    return combined

def combine_resort_forecast(resort, forecast, resort_id) -> dict:
    combined = {}
    try:
        # resort_match = next(
        #     res for res in resorts if res['text_id'] == resort_id)

        # forecast_match = next(
        #     fo for fo in forecasts if fo['text_id'] == resort_id)

        combined['text_id'] = resort_id
        combined['resort'] = resort
        combined['forecast'] = forecast
        return combined

    except StopIteration:
        abort(404)

def forecasts_date(forecasts) -> str:
    return forecasts[0]['forecast_date']

def forecast_date(forecast) -> str:
    return forecast['forecast_date']