import fauxsnow
from rich import print
from rich.console import Console
from rich.table import Table
import argparse

def refresh():
    """get the weather forecast from the weather API for each ski resort and save it to file

    """
    resorts = fauxsnow.load_ski_resorts()
    forecasts = fauxsnow.load_forecasts_from_api(resorts)
    fauxsnow.save_forecasts(forecasts)
    print('Updated forecasts')

def forecast():
    """read the ski resorts and weather forecasts from file and print a summary to the screen

    """
    forecasts = fauxsnow.load_forecasts_from_file()
    resorts = fauxsnow.load_ski_resorts()

    table = Table(title="Faux-Snow Forecast")
    table.add_column("ID", justify="left", style="cyan", no_wrap=True)
    table.add_column("Resort", justify="left", style="cyan", no_wrap=True)
    for day in forecasts[0]['periods']:
        table.add_column(day['date'], justify="center", style="cyan", no_wrap=True)

    for resort in resorts:
        periods = []
        for forecast in forecasts:
            if forecast['text_id'] == resort['text_id']:
                periods = forecast['periods']
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
    """read the ski resorts from file and print the details of one resort to the screen
    
    Keyword arguments: 
    resort_id -- the id of the ski resort
    """
    resorts = fauxsnow.load_ski_resorts()
    forecasts = fauxsnow.load_forecasts_from_file()
    match = 0
    for ski_resort in resorts:
        if str(ski_resort['text_id']) == str(resort_id):
            resort_table = Table(title="Ski Resort Details")
            resort_table.add_column(ski_resort['name'], justify="left", style="cyan", no_wrap=True)
            resort_table.add_column(ski_resort['location']['address'], justify="left", style="cyan", no_wrap=True)
            resort_table.add_row("Links", ski_resort['links']['conditions_url'])
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

            for forecast in forecasts:
                if forecast['text_id'] == str(resort_id):
                    for period in forecast['periods']:
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
            match = 1

    if match == 0:
        print('invalid id')        

# controller function for the command line interface
def main():
    parser = argparse.ArgumentParser(description='Faux Snow Forecast app')
    parser.add_argument('--refresh',  action = 'store_true', help='Refresh the forecast data')
    parser.add_argument('--forecast',  action = 'store_true', help='Display the forecast data')
    parser.add_argument('--detail',  action = 'store_true', help='Display the resort details')
    parser.add_argument('id', type=str, nargs = '?', help='ID of the resort to display')
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
