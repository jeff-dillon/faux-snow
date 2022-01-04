import unittest
from fauxsnow import Resort, ResortModel, Forecast, ForecastPeriod, ForecastModel, ForecastAPILoader, FauxSnow

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
        self.assertEqual(len(forecasts), 17)
        for f in forecasts:
            self.assertIsInstance(f, Forecast)
            self.assertIsInstance(f.periods, list)
            self.assertEqual(len(f.periods), 7)
            for p in f.periods:
                self.assertIsInstance(p, ForecastPeriod)
                
    def test_get_forecast_by_resort_id(self):
        model = ForecastModel()
        forecast = model.get_forecast_by_resort_id('snowshoe',self.TEST_FORECASTS_FILE)
        self.assertIsInstance(forecast, Forecast)
        self.assertEqual(forecast.resort_id, 'snowshoe')
        self.assertIsInstance(forecast.periods, list)
        self.assertEqual(len(forecast.periods), 7)
        for p in forecast.periods:
            self.assertIsInstance(p, ForecastPeriod)

    def test_calc_celcius(self):
        fs = FauxSnow()
        self.assertEquals(fs.calc_celcius(41), 5)
        self.assertEquals(fs.calc_celcius(32), 0)
        self.assertEquals(fs.calc_celcius(20), -7)
    
    def test_calc_fahrenheit(self):
        fs = FauxSnow()
        self.assertEquals(fs.calc_fahrenheit(5), 41)
        self.assertEquals(fs.calc_fahrenheit(0), 32)
        self.assertEquals(fs.calc_fahrenheit(-7), 19)

    def test_is_good_conditions(self):
        fs = FauxSnow()
        self.assertTrue(fs.conditions_are_good(18,5))
        self.assertFalse(fs.conditions_are_good(50,100))
    
    def test_calc_conditions(self):
        fs = FauxSnow()
        self.assertEqual(fs.calc_conditions("::S",0.2,32,80),"")
        self.assertEqual(fs.calc_conditions("::S",0.2,28,10),"Faux")
        self.assertEqual(fs.calc_conditions("::S",3.2,32,80),"Snow")
