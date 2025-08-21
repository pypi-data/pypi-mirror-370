import unittest
import numpy as np
from datetime import datetime
from daylight_evapotranspiration.daylight_evapotranspiration import daylight_ET_from_instantaneous_LE

class TestDaylightETFromInstantaneous(unittest.TestCase):
    def test_scalar_inputs_datetime(self):
        # Simple test with scalar values and datetime
        LE = 100.0  # W/m^2
        Rn = 200.0  # W/m^2
        G = 20.0    # W/m^2
        day_of_year = 180
        lat = 35.0
        hour_of_day = 12.0
        time_UTC = datetime(2023, 6, 29, 12, 0, 0)
        # Should run without error and return a float or np.ndarray
        result = daylight_ET_from_instantaneous_LE(
            LE_instantaneous_Wm2=LE,
            Rn_instantaneous_Wm2=Rn,
            G_instantaneous_Wm2=G,
            day_of_year=day_of_year,
            lat=lat,
            hour_of_day=hour_of_day,
            time_UTC=time_UTC
        )
        self.assertIsInstance(result, (float, np.floating, np.ndarray))

    def test_scalar_inputs_string_time(self):
        # Test with time as string
        LE = 100.0
        Rn = 200.0
        G = 20.0
        day_of_year = 180
        lat = 35.0
        hour_of_day = 12.0
        time_UTC = '2023-06-29T12:00:00'
        result = daylight_ET_from_instantaneous_LE(
            LE_instantaneous_Wm2=LE,
            Rn_instantaneous_Wm2=Rn,
            G_instantaneous_Wm2=G,
            day_of_year=day_of_year,
            lat=lat,
            hour_of_day=hour_of_day,
            time_UTC=time_UTC
        )
        self.assertIsInstance(result, (float, np.floating, np.ndarray))

    def test_array_inputs(self):
        # Test with numpy arrays
        LE = np.array([100.0, 110.0])
        Rn = np.array([200.0, 210.0])
        G = np.array([20.0, 25.0])
        day_of_year = np.array([180, 181])
        lat = np.array([35.0, 36.0])
        hour_of_day = np.array([12.0, 13.0])
        time_UTC = [datetime(2023, 6, 29, 12, 0, 0), datetime(2023, 6, 30, 13, 0, 0)]
        result = daylight_ET_from_instantaneous_LE(
            LE_instantaneous_Wm2=LE,
            Rn_instantaneous_Wm2=Rn,
            G_instantaneous_Wm2=G,
            day_of_year=day_of_year,
            lat=lat,
            hour_of_day=hour_of_day,
            time_UTC=time_UTC
        )
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (2,))

if __name__ == '__main__':
    unittest.main()
