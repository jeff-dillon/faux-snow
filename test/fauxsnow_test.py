from typing import Counter
import unittest
from fauxsnow import Resort, ResortModel, Forecast, ForecastPeriod, ForecastModel, ForecastAPILoader

class TestFS(unittest.TestCase):

    TEST_FORECASTS_FILE = 'test/test_forecasts_data.json'
    TEST_SKI_RESORTS_FILE = 'data/ski_resorts.json'

    def test_get_all_resorts(self):
        model = ResortModel()
        resorts = model.get_all_resorts(self.TEST_SKI_RESORTS_FILE)
        self.assertIsInstance(resorts, list)
        self.assertEqual(len(resorts), 25)
        for r in resorts:
            self.assertIsInstance(r, Resort)
    
    def test_get_resort_by_id(self):
        model = ResortModel()
        resort = model.get_resort_by_id('snowshoe', self.TEST_SKI_RESORTS_FILE)
        self.assertIsInstance(resort, Resort)
        self.assertEqual(resort.state, "West Virginia")
    
    def test_get_all_forecasts(self):
        model = ForecastModel()
        forecasts = model.get_all_forecasts(self.TEST_FORECASTS_FILE)
        self.assertIsInstance(forecasts, list)
        self.assertEqual(len(forecasts), 11)
        for f in forecasts:
            self.assertIsInstance(f, Forecast)
            self.assertIsInstance(f.periods, list)
            self.assertEqual(len(f.periods), 7)
            for p in f.periods:
                self.assertIsInstance(p, ForecastPeriod)
                
    def test_get_forecast_by_id(self):
        model = ForecastModel()
        forecast = model.get_forecast_by_resort_id('snowshoe',self.TEST_FORECASTS_FILE)
        self.assertIsInstance(forecast, Forecast)
        self.assertEqual(forecast.resort_id, 'snowshoe')
        self.assertIsInstance(forecast.periods, list)
        self.assertEqual(len(forecast.periods), 7)
        for p in forecast.periods:
            self.assertIsInstance(p, ForecastPeriod)


    # def resort_data_tester(self,resort):
    #     self.assertIsInstance(resort, dict)
    #     self.assertEqual(resort['id'], '1')
    #     self.assertEqual(resort['name'], 'Perfect North Slopes')
    #     self.assertEqual(resort['logo'], 'perfect-north-logo.png')
    #     self.assertEqual(resort['text_id'], 'perfect-north-slopes')
        
    #     first_resort_location = resort['location']
    #     self.assertIsInstance(first_resort_location, dict)
    #     self.assertEqual(first_resort_location['state'],'Indiana')
    #     self.assertEqual(first_resort_location['state_short'],'IN')
    #     self.assertEqual(first_resort_location['address'],'19074 Perfect Lane, Lawrenceburg, IN 47025')
    #     self.assertEqual(first_resort_location['lat'],'39.15107924069298')
    #     self.assertEqual(first_resort_location['long'],'-84.8858208026754')
        
    #     first_resort_links = resort['links']
    #     self.assertIsInstance(first_resort_links, dict)
    #     self.assertEqual(first_resort_links['main_url'],'https://www.perfectnorth.com/')
    #     self.assertEqual(first_resort_links['conditions_url'],'https://www.perfectnorth.com/snow-report')
    #     self.assertEqual(first_resort_links['map_url'],'https://goo.gl/maps/M9rqdn9arLbXF52o8')

    #     first_resort_stats = resort['stats']
    #     self.assertIsInstance(first_resort_stats, dict)
    #     self.assertEqual(first_resort_stats['acres'],'100')
    #     self.assertEqual(first_resort_stats['trails'],'23')
    #     self.assertEqual(first_resort_stats['lifts'],'7')
    #     self.assertEqual(first_resort_stats['vertical'],'400')
    
    # def forecast_data_tester(self, forecast):
    #     self.assertIsInstance(forecast, dict)
    #     self.assertEqual(forecast['text_id'],'perfect-north-slopes')
    #     self.assertEqual(forecast['forecast_date'],'25/12/2021 11:39 PM')

    #     first_forecast_periods = forecast['periods']
    #     self.assertIsInstance(first_forecast_periods, list)
    #     self.assertEqual(len(first_forecast_periods), 7)

    #     first_forecast_periods_first_period = first_forecast_periods[0]
    #     self.assertIsInstance(first_forecast_periods_first_period, dict)
    #     self.assertEqual(first_forecast_periods_first_period['date'],'25-Dec')
    #     self.assertEqual(first_forecast_periods_first_period['minTemp'],40)
    #     self.assertEqual(first_forecast_periods_first_period['maxTemp'],67)
    #     self.assertEqual(first_forecast_periods_first_period['snowIN'],0)
    #     self.assertEqual(first_forecast_periods_first_period['weather'],"Showers")
    #     self.assertEqual(first_forecast_periods_first_period['weatherCoded'],"D::RW")
    #     self.assertEqual(first_forecast_periods_first_period['humidity'],83)
    #     self.assertEqual(first_forecast_periods_first_period['conditions'],"")

    # def test_load_ski_resorts(self):
        
    #     resorts = fauxsnow.load_ski_resorts(self.TEST_SKI_RESORTS_FILE)
    #     self.assertIsInstance(resorts, list)
    #     self.assertEqual(len(resorts), 11)
        
    #     first_resort = resorts[0]
    #     self.resort_data_tester(first_resort)
        
    # def test_load_ski_resort(self):
    #     resort = fauxsnow.load_ski_resort("perfect-north-slopes")
    #     self.resort_data_tester(resort)

    # def test_load_forecasts_from_file(self):
    #     forecasts = fauxsnow.load_forecasts_from_file(self.TEST_FORECASTS_FILE)
    #     self.assertIsInstance(forecasts, list)
    #     self.assertEqual(len(forecasts), 11)

    #     first_forecast = forecasts[0]
    #     self.forecast_data_tester(first_forecast)

    # def test_load_forecast_from_file(self):
    #     forecast = fauxsnow.load_forecast_from_file('perfect-north-slopes', self.TEST_FORECASTS_FILE)
    #     self.forecast_data_tester(forecast)

    # def test_calc_celcius(self):
    #     self.assertEquals(fauxsnow.calc_celcius(41), 5)
    #     self.assertEquals(fauxsnow.calc_celcius(32), 0)
    #     self.assertEquals(fauxsnow.calc_celcius(20), -7)
    
    # def test_calc_fahrenheit(self):
    #     self.assertEquals(fauxsnow.calc_fahrenheit(5), 41)
    #     self.assertEquals(fauxsnow.calc_fahrenheit(0), 32)
    #     self.assertEquals(fauxsnow.calc_fahrenheit(-7), 19)

    # def test_is_good_conditions(self):
        # self.assertTrue(fauxsnow.is_good_conditions(18,5))
        # self.assertFalse(fauxsnow.is_good_conditions(50,100))