from dataclasses import dataclass, field
from typing import List
import requests, json, datetime, numpy, os, re


@dataclass
class ForecastPeriod:
    """
    A class to represent a weather forecast period.

    Attributes
    ___________
    period_date : datetime
        the date for which the forecast is valid
    min_temp : int
        the lowest temperature in the period (F)
    max_temp : int
        the highest temperature in the period (F)
    snow_in : float
        the amount of snow accumulation in inches
    weather : str
        human-readable weather description
    weather_coded : str
        coded weather description
    humidity : int
        relative humidity in the period
    conditions : str
        Faux, Snow, or ""
    """
    period_date : str
    min_temp : int
    max_temp : int
    snow_in : float
    weather : str
    weather_coded : str
    humidity : int
    conditions : str


@dataclass
class Forecast:
    """
    A class to represent a weather forecast.

    Atttributes
    ___________
    resort_id : str
        the text_id of the resort for this forecast
    forecast_date : datetime
        the date the forecast was retrieved
    periods : list
        a list of ForecastPeriod objects with weather forecast details
    """
    resort_id : str
    forecast_date: datetime
    periods : List[ForecastPeriod] = field(init=False, compare=False, default_factory=list)

    def to_dict(self):
        output = {}
        output['resort_id'] = self.resort_id
        output['forecast_date'] = self.forecast_date
        output['periods'] = []

        for period in self.periods:
            period_output = {}
            period_output['date'] = period.period_date
            period_output['minTemp'] = period.min_temp
            period_output['maxTemp'] = period.max_temp
            period_output['snowIN'] = period.snow_in
            period_output['weather'] = period.weather
            period_output['weatherCoded'] = period.weather_coded
            period_output['humidity'] = period.humidity
            period_output['conditions'] = period.conditions
            output['periods'].append(period_output)

        return output
    

@dataclass
class Resort:
    """
    A class to represent a ski resort.

    Attributes
    __________
    resort_id : str
        text_id of the resort
    name : str
        name of the resort
    logo : str
        filename for resort logo image
    state : str
        state where the resort is located
    state_short : str
        abbreviated state
    address : str
        street address of the resort
    lat : float
        lattitude of the resort
    long : float
        longitude of the resort
    main_url : str
        link to resort main website
    conditions_url : str
        link to conditions page on resort website
    map_url : str
        link to google map of resort address
    acres : int
        number of skiable acres
    trails : int
        number of trails
    lifts : int
        number of lifts
    vertical : int
        vertical drop in feet
    forecast : Forecast
        Forecast object of the resort
    """
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
    """
    Class that retrieves one or more resorts from json or database.

    Methods:
    ________
    get_all_resorts()
        returns a list of all available Resort objects
    get_resort_by_id(resort_id)
        returns a Resort object based on id
    """
    SKI_RESORTS_FILE = 'data/ski_resorts.json'

    def get_all_resorts(self, load_forecasts=True, file=SKI_RESORTS_FILE) -> list:
        """
         Returns a list of all avaialable ski resorts.
        """
        resorts = []
        f = open(file)
        forecast_model = ForecastModel()
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
                
                if load_forecasts:
                    forecast = forecast_model.get_forecast_by_resort_id(r.resort_id)
                    r.forecast = forecast
                resorts.append(r)
        finally:
            f.close()
        
        return resorts

    def get_resort_by_id(self, resort_id:str, file=SKI_RESORTS_FILE) -> Resort:
        """
        Returns a ski resort based on id.
        
        Keyword arguments: 
        resort_id -- the code name of the resort to be returned 
        """

        resorts = self.get_all_resorts()
        for resort in resorts:
            if resort.resort_id == resort_id:
                return resort
        
        return None


class ForecastModel:
    """
    Class that retreives one or more Forecasts from json or database.

    Methods:
    ________
    get_all_forecasts()
        returns a list of all available Forecast objects
    get_forecast_by_resort_id(resort_id)
        returns a Forecast object based on the resort_id
    """
    FORECASTS_FILE = 'data/forecasts.json'

    def get_all_forecasts(self, file:str=FORECASTS_FILE) -> list:
        """
        Return all available forecast data from a file.
        """
        forecasts = []
        forecast_file = open(file)
        try:
            forecast_data = json.load(forecast_file)
            for forecast_item in forecast_data:
                forecast = Forecast(
                    forecast_item['resort_id'],
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
        except TypeError:
            pass
        except KeyError:
            pass
        finally:
            forecast_file.close()

        return forecasts

    def get_forecast_by_resort_id(self, resort_id, file=FORECASTS_FILE) -> list:
        """
        Return forecast data based on a resort_id.
        """
        forecasts = self.get_all_forecasts()
        for forecast in forecasts:
            if forecast.resort_id == resort_id:
                return forecast
        
        return None
    
    def save_forecasts(self, forecasts:list):
        """save the weather forecast json to a text file
        
        Keyword arguments: 
        forecasts -- list of Forecast objects
        """
        forecasts_output = []
        for forecast in forecasts:
            forecasts_output.append(forecast.to_dict())

        with open(f'data/forecasts.json', 'w') as outfile:
            json.dump(forecasts_output, outfile, indent=4)



class ForecastAPILoader:
    """
    Class that retreives Forecast data from external API

    Methods:
    ________
    fetch_forecast(lat, long)
        request weather data based on lat/long from external API
    load_forecasts_from_api(resorts)
        load weather data for each resort in resorts
    """
    API_URL = "https://aerisweather1.p.rapidapi.com/forecasts/"
    API_KEY = os.environ.get('API_KEY')
    API_HEADER = {
                'x-rapidapi-host': "aerisweather1.p.rapidapi.com",
                'x-rapidapi-key': API_KEY
                }

    def fetch_forecast(self, lat, lon) -> dict:
        """
        Requeset weather data from external API based on lat/long and return json text.
        
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
        
        request_url = (self.API_URL+lat+','+lon+'?fields='+','.join(response_fields))
        response = requests.request("GET", request_url, headers=self.API_HEADER)
        data = json.loads(response.text)
        return data
    
    def load_forecasts_from_api(self, resorts) -> list:
        """updates the Foreecast object for each resort
        
        Keyword arguments: 
        resorts -- a list of resort dict objects
        """

        forecasts = []
        fs = FauxSnow()
        for resort in resorts:
            forecast_data = self.fetch_forecast(resort.lat, resort.long)
            response = forecast_data.get('response')
            
            # if the api call doesn't return a response value, 
            # exit the function and return None
            if response:
                forecast = Forecast(
                    resort.resort_id,
                    datetime.datetime.now().strftime("%d/%m/%Y %I:%M %p")
                )

                for period_data in forecast_data['response'][0]['periods']:
                    forecast_period = ForecastPeriod(
                        datetime.datetime.strptime(period_data['validTime'], 
                            '%Y-%m-%dT%H:%M:%S%z').strftime("%a %-d"),
                        period_data['minTempF'],
                        period_data['maxTempF'],
                        period_data['snowIN'],
                        period_data['weatherPrimary'],
                        period_data['weatherPrimaryCoded'],
                        period_data['minHumidity'],
                        fs.calc_conditions(
                            period_data['weatherPrimaryCoded'],
                            period_data['snowIN'],
                            period_data['minTempF'],
                            period_data['minHumidity'])
                    )
                    forecast.periods.append(forecast_period)
                forecasts.append(forecast)
        return forecasts


class FauxSnow:
    """
    Class with library functions for dealing with weather data

    Methods:
    ________

    calc_celcius()
        converts from Fahrenheit to Celcius
    calc_fahrenheit()
        converts from Celcius to Fahrenheit
    calc_wet_bulb()
        calculates the wet bulb temp based on temp and relative humidity
    conditions_are_good()
        determines if conditions are good for snow making
    calc_coditions()
        calculates whether the conditions are good for faux-snow or real snow or no snow
    """
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
    
    def conditions_are_good(self, min_temp, humidity) -> bool:
        """Return whether or not the temperature and relative humidity are 
        favorable for snow making
        
        Keyword arguments: 
        period -- the forecast period in question 
        """
        
        conditions_are_good = False

        if min_temp <= 20:
            conditions_are_good =  True
        elif min_temp <= 21 and humidity <= 94:
            conditions_are_good =  True
        elif min_temp <= 22 and humidity <= 85:
            conditions_are_good =  True
        elif min_temp <= 23 and humidity <= 76:
            conditions_are_good =  True
        elif min_temp <= 24 and humidity <= 66:
            conditions_are_good =  True
        elif min_temp <= 25 and humidity <= 54:
            conditions_are_good =  True
        elif min_temp <= 26 and humidity <= 39:
            conditions_are_good =  True
        elif min_temp <= 27 and humidity <= 25:
            conditions_are_good =  True
        elif min_temp <= 28 and humidity <= 15:
            conditions_are_good =  True
        elif min_temp <= 29 and humidity <= 10:
            conditions_are_good =  True
        else:
            conditions_are_good = False
        
        return conditions_are_good

    def calc_conditions(self, weather_coded:str, snow_in:float, temp:int, rh:int):
        """
        calculates whether the conditions are good for faux-snow or real snow or no snow.
        """
        match = re.search(r':[A-Z]+$',weather_coded)
        conditions = ''

        if match:
            # check for Blowing Snow, Snow, Snow Showers, or Wintry Mix
            # and a snow accumulation of more that 1/4 inch
            if (match.group() in [':BS',':S',':SW',':WM'] and snow_in > .25): 
                conditions = 'Snow'
            # check for a cloud code - indicates absence of non-snow 
            # weather (ice, rain, etc.)
            elif (self.conditions_are_good(temp, rh) 
                and match.group() in [':CL',':FW',':SC',':BK',':OV',':BS',':S',':SW',':WM']): 
                conditions = 'Faux'
        return conditions