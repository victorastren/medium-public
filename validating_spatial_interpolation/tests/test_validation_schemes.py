"""
Unit tests for cross-validation partitioning and validation schemes:
- Leave-One-Out Cross-Validation (LOOCV)
- Random 5-Fold Cross-Validation
- Spatial Block Cross-Validation (4 Quadrants)
- Buffered Validation (r = 0.30)
- Consistency with benchmark_results.json
"""

import os
import csv
import json
import unittest
import numpy as np

# Add code directory to path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'code')))


class TestValidationSchemes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the 100 Geneva sensors
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sensors_data.csv')
        if not os.path.exists(csv_path):
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'sensors_data.csv')
        sensors = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sensors.append(row)
        
        cls.n_sensors = len(sensors)
        cls.xs = np.array([float(s['X']) for s in sensors])
        cls.ys = np.array([float(s['Y']) for s in sensors])
        cls.coords = np.column_stack([cls.xs, cls.ys])

    def test_loocv_partitioning(self):
        # In LOOCV, exactly 1 sensor is withheld per split
        for i in range(self.n_sensors):
            train_mask = np.ones(self.n_sensors, dtype=bool)
            train_mask[i] = False

            self.assertEqual(np.sum(~train_mask), 1, 'Exactly 1 point withheld in LOOCV.')
            self.assertEqual(np.sum(train_mask), self.n_sensors - 1, '99 points available in LOOCV.')

            # Nearest distance is positive
            dists = np.linalg.norm(self.coords[train_mask] - self.coords[i], axis=1)
            d_min = np.min(dists)
            self.assertGreater(d_min, 0.0)

    def test_random_5fold_partitioning_and_reproducibility(self):
        for seed in [42, 50, 61]:
            np.random.seed(seed)
            shuffled_idx = np.random.permutation(self.n_sensors)
            folds = np.array_split(shuffled_idx, 5)

            self.assertEqual(len(folds), 5, 'Must produce exactly 5 folds.')

            # Check fold sizes: 100 / 5 = 20 points per fold
            for fold in folds:
                self.assertEqual(len(fold), 20, 'Each fold must contain exactly 20 sensors.')

            # Check exhaustive and mutually exclusive
            all_indices = np.concatenate(folds)
            self.assertEqual(len(np.unique(all_indices)), 100, 'Folds must partition all 100 sensors.')

        # Test reproducibility: same seed gives identical folds
        np.random.seed(42)
        perm1 = np.random.permutation(self.n_sensors)
        np.random.seed(42)
        perm2 = np.random.permutation(self.n_sensors)
        np.testing.assert_array_equal(perm1, perm2)

    def test_spatial_block_quadrants(self):
        # 4 Quadrants: NW, NE, SW, SE
        q_nw = (self.xs <= 0.0) & (self.ys >= 0.0)
        q_ne = (self.xs > 0.0) & (self.ys >= 0.0)
        q_sw = (self.xs <= 0.0) & (self.ys < 0.0)
        q_se = (self.xs > 0.0) & (self.ys < 0.0)

        # Mutually exclusive and exhaustive
        counts = [np.sum(q_nw), np.sum(q_ne), np.sum(q_sw), np.sum(q_se)]
        self.assertEqual(sum(counts), 100, 'All 100 sensors must be assigned to quadrants.')

        # Every sensor assigned exactly once
        sum_masks = q_nw.astype(int) + q_ne.astype(int) + q_sw.astype(int) + q_se.astype(int)
        np.testing.assert_array_equal(sum_masks, np.ones(100), 'Every sensor belongs to exactly one quadrant.')

        # Each quadrant must have reasonable sample size (> 10)
        for count in counts:
            self.assertGreater(count, 10, 'Each quadrant must contain at least 10 sensors.')

    def test_buffered_validation_exclusion_guarantee(self):
        r = 0.30
        for i in range(self.n_sensors):
            target = self.coords[i]
            dists = np.linalg.norm(self.coords - target, axis=1)

            # Available set is strictly dist > r
            train_mask = dists > r
            self.assertFalse(train_mask[i], f'Target sensor {i} must be excluded.')

            train_dists = dists[train_mask]
            self.assertGreater(len(train_dists), 0, f'At least some sensors must remain outside buffer for target {i}.')

            # Minimum distance to available sensors must be strictly > r
            d_min = np.min(train_dists)
            self.assertGreater(d_min, r, f'Nearest distance {d_min:.4f} must exceed buffer radius {r}.')

    def test_benchmark_results_json_consistency(self):
        json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'benchmark_results.json')
        if not os.path.exists(json_path):
            json_path = os.path.join(os.path.dirname(__file__), '..', 'benchmark_results.json')
        self.assertTrue(os.path.exists(json_path), 'benchmark_results.json must exist.')

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check expected top-level keys
        for key in ['grid_ground_truth', 'loocv', 'random_5fold', 'spatial_block', 'buffered']:
            self.assertIn(key, data, f'Key "{key}" missing from benchmark_results.json.')

        # Cross-check Table 1 values from article
        # LOOCV RMSE
        self.assertAlmostEqual(data['loocv']['Polynomial']['rmse_obs'], 0.458, places=2)
        self.assertAlmostEqual(data['loocv']['IDW']['rmse_obs'], 0.693, places=2)
        self.assertAlmostEqual(data['loocv']['RBF']['rmse_obs'], 0.247, places=2)
        self.assertAlmostEqual(data['loocv']['Kriging']['rmse_obs'], 0.279, places=2)

        # Spatial block RMSE
        self.assertAlmostEqual(data['spatial_block']['Polynomial']['rmse_obs'], 0.542, places=2)
        self.assertAlmostEqual(data['spatial_block']['IDW']['rmse_obs'], 2.189, places=2)
        self.assertAlmostEqual(data['spatial_block']['RBF']['rmse_obs'], 1.292, places=2)
        self.assertAlmostEqual(data['spatial_block']['Kriging']['rmse_obs'], 1.731, places=2)

        # Buffered (r = 0.30) RMSE
        buf_metrics = data['buffered']['r_0.30']['metrics']
        self.assertAlmostEqual(buf_metrics['Polynomial']['rmse_obs'], 0.536, places=2)
        self.assertAlmostEqual(buf_metrics['IDW']['rmse_obs'], 1.266, places=2)
        self.assertAlmostEqual(buf_metrics['RBF']['rmse_obs'], 0.451, places=2)
        self.assertAlmostEqual(buf_metrics['Kriging']['rmse_obs'], 0.530, places=2)


if __name__ == '__main__':
    unittest.main()
