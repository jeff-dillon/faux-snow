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

# calculate the wet bulb temperature
# takes the temperature (T) in Fahrenheit and the Relative Humitidy (rh) 
# returns the wet-bulb temperature in Fahrenheit
def calc_wet_bulb(T, rh) -> float:
    """Return a wet-bulb temperature based on Temperature and Relative Humidity
    
    Keyword arguments:
    T -- the temperature in Celcius
    rh -- the relative humidity
    """
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
def load_forecast_file(id):
    f = open(f'data/forecast-{id}.json')
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

# returns a list of forecast summaries for all resorts
def forecast_summary():
    forecastSummary = []
    resorts = load_ski_resorts()
    for ski_resort in resorts['resorts']:
        forecastData = {
                'id' : ski_resort['id'],
                'name' : ski_resort['name'],
                'state' : ski_resort['location']['state-short']
            }
        snowDates = ''
        forecast = load_forecast_file(ski_resort['id'])
        for period in forecast['response'][0]['periods']:
            minWetBulbTemp = round(calc_wet_bulb(period['minTempF'], period['minHumidity']))
            maxWetBulbTemp = round(calc_wet_bulb(period['maxTempF'], period['maxHumidity']))
            snow_date = str(datetime.datetime.strptime(period['validTime'], '%Y-%m-%dT%H:%M:%S-05:00').date())
            if minWetBulbTemp <= 20 or maxWetBulbTemp <= 20:
                if len(snowDates) > 0:
                    snowDates += ', '
                snowDates = snowDates + snow_date + " "
        forecastData['snow-days'] = snowDates
        forecastSummary.append(forecastData)
    return forecastSummary

# get the weather forecast for each ski resort and save it to file
def refresh():
    resorts = load_ski_resorts()
    for ski_resort in resorts['resorts']:
        forecast = load_forecast(ski_resort['location']['lat'], ski_resort['location']['long'])
        save_forecast(forecast, ski_resort['id'])

# read the ski resorts and weather forecasts from file and print a summary to the screen
# returns nothing
def forecast():
    fs = forecast_summary()

    table = Table(title="Faux-Snow Forecast")
    table.add_column("ID", justify="left", style="cyan", no_wrap=True)
    table.add_column("Resort", justify="left", style="cyan", no_wrap=True)
    table.add_column("Faux Snow Days", justify="left", style="cyan", no_wrap=True)

    for resort in fs:
        table.add_row(resort['id'], "(" + resort['state'] + ") " + resort['name'], resort['snow-days'])

    console = Console()
    console.print(table)
    

# read the ski resorts from file and print the details of one resort to the screen
# takes a resort id for the requested resort
# returns nothing
def detail(resort_id):
    resorts = load_ski_resorts()
    match = 0
    for ski_resort in resorts['resorts']:
        if str(ski_resort['id']) == str(resort_id):
            table = Table(title="Ski Resort Details")
            table.add_column(ski_resort['name'], justify="left", style="cyan", no_wrap=True)
            table.add_column(ski_resort['location']['address'], justify="left", style="cyan", no_wrap=True)
            table.add_row("Links", ski_resort['links']['conditions-url'])
            table.add_row("Skiable Terrain", ski_resort['stats']['acres'])
            table.add_row("# Lifts", ski_resort['stats']['lifts'])
            table.add_row("# Trails", ski_resort['stats']['trails'])
            table.add_row("Vertical Drop", ski_resort['stats']['vertical'])
            
            console = Console()
            console.print(table)
            
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
