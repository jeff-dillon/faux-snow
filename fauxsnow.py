from flask  import abort
from dataclasses import dataclass, field
import requests
import json
import datetime
import numpy
import os
import re

@dataclass
class Forecast:
    resort_id : str
    forecast_date: datetime
    periods : list = field(init=False, compare=False, default_factory=list)

    
@dataclass
class ForecastPeriod:
    period_date : datetime
    min_temp : int
    max_temp : int
    snow_in : float
    weather : str
    weather_coded : str
    humidity : int
    conditions : str

    def conditions_are_good(self) -> bool:
        """Return whether or not the temperature and relative humidity are 
        favorable for snow making
        
        Keyword arguments: 
        T -- the temperature in Celcius 
        rh -- the relative humidity
        """
        
        conditions_are_good = False

        if self.min_temp <= 20:
            conditions_are_good =  True
        elif self.min_temp <= 21 and self.humidity <= 94:
            conditions_are_good =  True
        elif self.min_temp <= 22 and self.humidity <= 85:
            conditions_are_good =  True
        elif self.min_temp <= 23 and self.humidity <= 76:
            conditions_are_good =  True
        elif self.min_temp <= 24 and self.humidity <= 66:
            conditions_are_good =  True
        elif self.min_temp <= 25 and self.humidity <= 54:
            conditions_are_good =  True
        elif self.min_temp <= 26 and self.humidity <= 39:
            conditions_are_good =  True
        elif self.min_temp <= 27 and self.humidity <= 25:
            conditions_are_good =  True
        elif self.min_temp <= 28 and self.humidity <= 15:
            conditions_are_good =  True
        elif self.min_temp <= 29 and self.humidity <= 10:
            conditions_are_good =  True
        else:
            conditions_are_good = False
        
        return conditions_are_good

@dataclass
class Resort:
    resort_id : str
    name : str
    logo : str
    state : str
    state_short : str
    address : str
    lat : float
    long : float
    main_url : str
    conditions_url : str
    map_url : str
    acres : int
    trails : int
    lifts : int
    vertical : int
    forecast : Forecast = field(init=False, compare=False)

class ResortModel:

    SKI_RESORTS_FILE = 'data/ski_resorts.json'

    def get_all_resorts(self, file=SKI_RESORTS_FILE) -> list:
        """Returns a list of ski resorts
        
        """
        resorts = []
        f = open(file)
        try:
            resort_list = json.load(f)
            for resort in resort_list:
                r = Resort(
                    resort['text_id'],
                    resort['name'],
                    resort['logo'],
                    resort['location']['state'],
                    resort['location']['state_short'],
                    resort['location']['address'],
                    resort['location']['lat'],
                    resort['location']['long'],
                    resort['links']['main_url'],
                    resort['links']['conditions_url'],
                    resort['links']['map_url'],
                    resort['stats']['acres'],
                    resort['stats']['trails'],
                    resort['stats']['lifts'],
                    resort['stats']['vertical'])
            
                forecast_model = ForecastModel()
                forecast = forecast_model.get_forecast_by_resort_id(r.resort_id)
                r.forecast = forecast
                resorts.append(r)
        finally:
            f.close()
        
        return resorts

    def get_resort_by_id(self, text_id:str, file=SKI_RESORTS_FILE) -> Resort:
        """Return forecast data from a file
        
        Keyword arguments: 
        text_id -- the code name of the resort to be returned 
        """

        resorts = self.get_all_resorts()
        for resort in resorts:
            if resort.resort_id == text_id:
                return resort
        
        return None



class ForecastModel:
    FORECASTS_FILE = 'data/forecasts.json'

    def get_all_forecasts(self, file:str=FORECASTS_FILE) -> list:
        """Return forecast data from a file
        """
        forecasts = []
        forecast_file = open(file)
        try:
            forecast_data = json.load(forecast_file)
            for forecast_item in forecast_data:
                forecast = Forecast(
                    forecast_item['text_id'],
                    datetime.datetime.now().strftime("%d/%m/%Y %I:%M %p")
                )
                
                for period in forecast_item['periods']:
                    forecast.periods.append(ForecastPeriod(
                        period['date'],
                        period['minTemp'],
                        period['maxTemp'],
                        period['snowIN'],
                        period['weather'],
                        period['weatherCoded'],
                        period['humidity'],
                        period['conditions']
                    ))

                forecasts.append(forecast)

        finally:
            forecast_file.close()

        return forecasts

    def get_forecast_by_resort_id(self, text_id, file=FORECASTS_FILE) -> list:
        """Return forecast data from a file
        """
        forecasts = self.get_all_forecasts()
        for forecast in forecasts:
            if forecast.resort_id == text_id:
                return forecast
        
        return None

class ForecastAPILoader:

    def fetch_forecast(self, lat, lon) -> dict:
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
    
    def load_forecasts_from_api(self, resorts) -> list:
        """load the weather forecast json to a list of dict objects. 
        Returns None if we have reached the api call limit
        
        Keyword arguments: 
        resorts -- a list of resort dict objects
        """
        forecasts = []
        for resort in resorts:
            forecast = self.fetch_forecast(
                resort['location']['lat'], 
                resort['location']['long'])
            response = forecast.get('response')
            
            # if the api call doesn't return a response value, 
            # exit the function and return None
            if response:
                self.save_forecast(forecast['response'][0], resort['text_id'])

                forecastsdata = {
                    "text_id" : resort["text_id"],
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
                        elif (ForecastPeriod.conditions_are_good() 
                            and match.group() in [':CL',':FW',':SC',':BK',':OV',':BS',':S',':SW',':WM']): 
                            conditions = 'Faux'
                    
                    forecastsdata['periods'].append({
                        'date' : str(
                            datetime.datetime.strptime(period['validTime'], 
                            '%Y-%m-%dT%H:%M:%S%z').date().strftime('%a %d')),
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

    def save_forecasts(forecasts):
        """save the weather forecast json to a text file
        
        Keyword arguments: 
        f -- the forecast data
        id -- the is of the ski resort
        """
        with open(f'data/forecasts.json', 'w') as outfile:
            json.dump(forecasts, outfile, indent=4)

    def save_forecast(forecast, file_name):
        """save the weather forecast json to a text file
        
        Keyword arguments: 
        forecast -- the forecast data
        file_name -- the name of the ski resort
        """
        with open(f'data/'+file_name+'.json', 'w') as outfile:
            json.dump(forecast, outfile, indent=4)

class FauxSnow:

    def calc_celcius(self, Tf) -> int:
        """Return a temperature converted from Fahrenheit to Celcius
        
        Keyword arguments:
        Tf -- the temperature in Fahrenheit
        """
        return round((Tf - 32) * (5/9))

    def calc_fahrenheit(self, Tc) -> int:
        """Return a temperature converted from Celcius to Fharenheit
        
        Keyword arguments:
        Tc -- the temperature in Celcius
        """
        return round((Tc * (9/5)) + 32)

    # Function immplemented but not in use. 
    # Easier to just test the boundaries of the temp/rel. humidity matrix.
    def calc_wet_bulb(self, T, rh) -> float:
        """Return a wet-bulb temperature based on Temperature and Relative Humidity
        
        Keyword arguments:
        T -- the temperature in Celcius
        rh -- the relative humidity
        """
        T = self.calc_celcius(T)   
        rh /= 100             
        Tw = (T * numpy.arctan([0.151977 * (rh + 8.313659)**(1/2)])[0] + 
            numpy.arctan([T + rh])[0] - 
            numpy.arctan([rh - 1.676331])[0] + 0.00391838 *(rh)**(3/2) * 
            numpy.arctan([0.023101 * rh])[0] - 4.686035)
        return self.calc_fahrenheit(Tw) 


    def combine_resorts_forecasts(self, resorts, forecasts) -> list:
        combined = []
        for resort in resorts:
            forecast_match = {}
            try:
                forecast_match = next(fo for fo in forecasts \
                    if fo['text_id'] == resort['text_id'])
            except StopIteration:
                pass
            combined.append({
                "text_id" : resort['text_id'],
                "resort" : resort,
                "forecast" : forecast_match
            })
        return combined

    def combine_resort_forecast(self, resort, forecast, resort_id) -> dict:
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

