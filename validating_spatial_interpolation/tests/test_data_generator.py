"""
Unit tests for data_generator.py and sensors dataset integrity.
"""

import os
import csv
import sys
import unittest
import numpy as np

# Add code directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code")))

from data_generator import is_point_in_lake, get_lake_distance, get_true_temperature


class TestDataGenerator(unittest.TestCase):

    def test_is_point_in_lake_center(self):
        # Center of lake around x = 0.25, y_c = 0.5*(0.25)^2 + 0.3*(0.25) - 0.15 = -0.04375
        self.assertTrue(is_point_in_lake(0.25, -0.04375))
        self.assertTrue(is_point_in_lake(0.0, -0.15))

    def test_is_point_in_lake_outside(self):
        # Clearly outside: Jura mountains (-0.8, 0.8) and Salève (0.8, -0.8)
        self.assertFalse(is_point_in_lake(-0.8, 0.8))
        self.assertFalse(is_point_in_lake(0.8, -0.8))
        self.assertFalse(is_point_in_lake(0.0, 0.5))

    def test_is_point_in_lake_vectorized(self):
        xs = np.array([0.25, -0.8, 0.0])
        ys = np.array([-0.04375, 0.8, -0.15])
        mask = is_point_in_lake(xs, ys)
        self.assertEqual(mask.shape, (3,))
        self.assertTrue(mask[0])
        self.assertFalse(mask[1])
        self.assertTrue(mask[2])

    def test_get_lake_distance_properties(self):
        # Distance is 0 inside lake
        d_inside = get_lake_distance(0.25, -0.04375)
        self.assertAlmostEqual(d_inside, 0.0, places=5)

        # Distance is strictly positive far away
        d_outside = get_lake_distance(-0.8, 0.8)
        self.assertGreater(d_outside, 0.5)

        # Vectorized evaluation
        xs = np.array([0.25, -0.8])
        ys = np.array([-0.04375, 0.8])
        dists = get_lake_distance(xs, ys)
        self.assertEqual(dists.shape, (2,))
        self.assertAlmostEqual(dists[0], 0.0, places=5)
        self.assertGreater(dists[1], 0.5)

    def test_get_true_temperature_lapse_rate(self):
        # Flat valley point near center: (0.0, 0.2)
        t_valley = get_true_temperature(0.0, 0.2)
        # High elevation at Jura: (-1.0, 1.0)
        t_mountain = get_true_temperature(-1.0, 1.0)

        # Temperature at mountain peak must be significantly cooler than valley
        self.assertLess(t_mountain, t_valley)
        self.assertGreater(t_valley, 20.0)
        self.assertLess(t_valley, 35.0)

    def test_sensors_dataset_integrity(self):
        csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "sensors_data.csv")
        self.assertTrue(os.path.exists(csv_path), f"File {csv_path} does not exist.")

        sensors = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sensors.append(row)

        # 1. Check count
        self.assertEqual(len(sensors), 100, "Dataset must contain exactly 100 sensors.")

        # 2. Check coordinates in [-1, 1]
        xs = np.array([float(s['X']) for s in sensors])
        ys = np.array([float(s['Y']) for s in sensors])
        temps = np.array([float(s['Temperature']) for s in sensors])
        elevs = np.array([float(s['Elevation']) for s in sensors])

        self.assertTrue(np.all(xs >= -1.0) and np.all(xs <= 1.0), "All X coords must be in [-1, 1].")
        self.assertTrue(np.all(ys >= -1.0) and np.all(ys <= 1.0), "All Y coords must be in [-1, 1].")
        self.assertTrue(np.all(elevs >= 375.0), "Elevation must be at least base elevation 375m.")

        # 3. No sensor placed in the lake
        lake_mask = is_point_in_lake(xs, ys)
        self.assertFalse(np.any(lake_mask), "No physical sensors should be placed inside Lake Geneva.")

        # 4. Realistic temperatures
        self.assertTrue(np.all(temps >= 15.0) and np.all(temps <= 36.0), "Sensor temperatures should be in realistic bounds.")


if __name__ == '__main__':
    unittest.main()
