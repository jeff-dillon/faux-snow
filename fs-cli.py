import fauxsnow
from rich import print
from rich.console import Console
from rich.table import Table
import argparse

def refresh():
    """get the weather forecast from the weather API for each 
        ski resort and save it to file

    """
    resorts = fauxsnow.load_ski_resorts()
    forecasts = fauxsnow.load_forecasts_from_api(resorts)
    # if the api call returns None, fail gracefully.
    if forecasts:
        fauxsnow.save_forecasts(forecasts)
        print('Updated forecasts')
    else:
        print('could not update forecasts')

def forecast():
    """read the ski resorts and weather forecasts from file and 
        print a summary to the screen

    """
    forecasts = fauxsnow.load_forecasts_from_file()
    resorts = fauxsnow.load_ski_resorts()

    table = Table(title="Faux-Snow Forecast")

    table.add_column("ID", 
        justify="left", 
        style="cyan", 
        no_wrap=True)

    table.add_column("Resort", 
        justify="left", 
        style="cyan", 
        no_wrap=True)

    for day in forecasts[0]['periods']:
        table.add_column(
            day['date'], 
            justify="center",
            style="cyan", 
            no_wrap=True)

    for resort in resorts:

        forecast_match = next((
            fo for fo in forecasts 
            if fo['text_id'] == resort['text_id']))
        periods = forecast_match['periods']

        table.add_row(resort['text_id'], 
            "(" + resort['location']['state'] + ") " + resort['name'], 
            periods[0]['conditions'],
            periods[1]['conditions'],
            periods[2]['conditions'],
            periods[3]['conditions'],
            periods[4]['conditions'],
            periods[5]['conditions'],
            periods[6]['conditions'],
        )

    console = Console()
    console.print(table)
    


def detail(resort_id):
    """read the ski resorts from file and print the details of 
        one resort to the screen
    
    Keyword arguments: 
    resort_id -- the id of the ski resort
    """
    resorts = fauxsnow.load_ski_resorts()
    forecasts = fauxsnow.load_forecasts_from_file()

    try:
        resort_match = next((
            res for res in resorts 
            if res['text_id'] == resort_id))
        forecast_match = next((
            fo for fo in forecasts 
            if fo['text_id'] == resort_id))
    
        resort_table = Table(title="Ski Resort Details")

        resort_table.add_column(resort_match['name'], 
            justify="left", 
            style="cyan", 
            no_wrap=True)

        resort_table.add_column(resort_match['location']['address'], 
            justify="left", 
            style="cyan", 
            no_wrap=True)

        resort_table.add_row("Links", 
            resort_match['links']['conditions_url'])

        resort_table.add_row("Skiable Terrain", 
            resort_match['stats']['acres'] + " acres")

        resort_table.add_row("# Lifts", 
            resort_match['stats']['lifts'])

        resort_table.add_row("# Trails", 
            resort_match['stats']['trails'])

        resort_table.add_row("Vertical Drop", 
            resort_match['stats']['vertical'] + " feet")
        
        console = Console()
        console.print(resort_table)


        forecast_table = Table(title="Forecast Details")

        forecast_table.add_column("Date", 
            justify="left", 
            style="cyan", 
            no_wrap=True)

        forecast_table.add_column("Conditions", 
            justify="left", 
            style="cyan", 
            no_wrap=True)

        forecast_table.add_column("Weather", 
            justify="left", 
            style="cyan", 
            no_wrap=True)

        forecast_table.add_column("Min Temp", 
            justify="left", 
            style="cyan", 
            no_wrap=True)

        forecast_table.add_column("Max Temp", 
            justify="left", 
            style="cyan", 
            no_wrap=True)

        forecast_table.add_column("Humidity", 
            justify="left", 
            style="cyan", 
            no_wrap=True)

        forecast_table.add_column("Snow (IN)", 
            justify="left", 
            style="cyan", 
            no_wrap=True)

        for period in forecast_match['periods']:
            forecast_table.add_row(
                period['date'],
                period['conditions'],
                period['weather'],
                str(period['minTemp']),
                str(period['maxTemp']),
                str(period['humidity']),
                str(period['snowIN'])
            )

        console.print(forecast_table)
 
    except StopIteration:
        print('invalid id')        

# controller function for the command line interface
def main():
    parser = argparse.ArgumentParser(description='Faux Snow Forecast app')
    parser.add_argument('--refresh',  
        action = 'store_true', 
        help='Refresh the forecast data')

    parser.add_argument('--forecast',  
        action = 'store_true', 
        help='Display the forecast data')

    parser.add_argument('--detail',  
        action = 'store_true', 
        help='Display the resort details')

    parser.add_argument('id', 
        type=str, 
        nargs = '?', 
        help='ID of the resort to display')

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
