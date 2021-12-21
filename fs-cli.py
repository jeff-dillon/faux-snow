import requests
import json
import datetime
import config
import numpy
from rich import print, style
from rich.console import Console
from rich.table import Table
import argparse

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

def load_ski_resorts() -> dict:
    """Returns the ski resorts data from a file
    
    """
    f = open(f'data/ski-resorts.json')
    try:
        data = json.load(f)
    finally:
        f.close()
    return data

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
    
    for ski_resort in resorts['resorts']:
        
        forecastData = {
                'id' : ski_resort['id'],
                'name' : ski_resort['name'],
                'state' : ski_resort['location']['state-short'],
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

def refresh():
    """get the weather forecast from the weather API for each ski resort and save it to file

    """
    resorts = load_ski_resorts()
    for ski_resort in resorts['resorts']:
        forecast = load_forecast(ski_resort['location']['lat'], ski_resort['location']['long'])
        save_forecast(forecast, ski_resort['id'])
        print('Updated forecast for ', ski_resort['name'])

def forecast():
    """read the ski resorts and weather forecasts from file and print a summary to the screen

    """
    fs = forecast_summary()

    table = Table(title="Faux-Snow Forecast")
    table.add_column("ID", justify="left", style="cyan", no_wrap=True)
    table.add_column("Resort", justify="left", style="cyan", no_wrap=True)
    for day in fs[0]['forecast']:
        table.add_column(day['date'], justify="center", style="cyan", no_wrap=True)

    for resort in fs:
        table.add_row(resort['id'], 
            "(" + resort['state'] + ") " + resort['name'], 
            resort['forecast'][0]['conditions'],
            resort['forecast'][1]['conditions'],
            resort['forecast'][2]['conditions'],
            resort['forecast'][3]['conditions'],
            resort['forecast'][4]['conditions'],
            resort['forecast'][5]['conditions'],
            resort['forecast'][6]['conditions'],
        )

    console = Console()
    console.print(table)
    


def detail(resort_id):
    """read the ski resorts from file and print the details of one resort to the screen
    
    Keyword arguments: 
    resort_id -- the id of the ski resort
    """
    resorts = load_ski_resorts()
    match = 0
    for ski_resort in resorts['resorts']:
        if str(ski_resort['id']) == str(resort_id):
            resort_table = Table(title="Ski Resort Details")
            resort_table.add_column(ski_resort['name'], justify="left", style="cyan", no_wrap=True)
            resort_table.add_column(ski_resort['location']['address'], justify="left", style="cyan", no_wrap=True)
            resort_table.add_row("Links", ski_resort['links']['conditions-url'])
            resort_table.add_row("Skiable Terrain", ski_resort['stats']['acres'] + " acres")
            resort_table.add_row("# Lifts", ski_resort['stats']['lifts'])
            resort_table.add_row("# Trails", ski_resort['stats']['trails'])
            resort_table.add_row("Vertical Drop", ski_resort['stats']['vertical'] + " feet")
            
            console = Console()
            console.print(resort_table)

            forecast_table = Table(title="Forecast Details")
            forecast_table.add_column("Date", justify="left", style="cyan", no_wrap=True)
            forecast_table.add_column("Conditions", justify="left", style="cyan", no_wrap=True)
            forecast_table.add_column("Weather", justify="left", style="cyan", no_wrap=True)
            forecast_table.add_column("Min Temp", justify="left", style="cyan", no_wrap=True)
            forecast_table.add_column("Max Temp", justify="left", style="cyan", no_wrap=True)
            forecast_table.add_column("Humidity", justify="left", style="cyan", no_wrap=True)
            forecast_table.add_column("Snow (IN)", justify="left", style="cyan", no_wrap=True)

            fs = forecast_summary()
            for resort in fs:
                if resort['id'] == str(resort_id):
                    for day in resort['forecast']:
                        forecast_table.add_row(
                            day['date'],
                            day['conditions'],
                            day['weather'],
                            str(day['minTemp']),
                            str(day['maxTemp']),
                            str(day['humidity']),
                            str(day['snowIN'])
                        )

            console.print(forecast_table)
            match = 1

    if match == 0:
        print('invalid id')        

# controller function for the command line interface
def main():
    parser = argparse.ArgumentParser(description='Faux Snow Forecast app')
    parser.add_argument('--refresh',  action = 'store_true', help='Refresh the forecast data')
    parser.add_argument('--forecast',  action = 'store_true', help='Display the forecast data')
    parser.add_argument('--detail',  action = 'store_true', help='Display the resort details')
    parser.add_argument('id', type=int, nargs = '?', help='ID of the resort to display')
    args = parser.parse_args()

    if args.refresh:
        refresh()
    elif args.forecast:
        forecast()
    elif args.detail:
        detail(args.id)
    else:
        parser.format_usage()


main()
