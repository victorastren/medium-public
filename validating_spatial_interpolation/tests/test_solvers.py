"""
Unit tests for spatial interpolation solvers:
- PolynomialSurface
- InverseDistanceWeighting
- RadialBasisFunctions2D (Thin-Plate Spline)
- OrdinaryKriging2D (Spherical Semivariogram)
"""

import os
import sys
import unittest
import numpy as np

# Add code directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'code')))

from solvers import (
    PolynomialSurface,
    InverseDistanceWeighting,
    RadialBasisFunctions2D,
    OrdinaryKriging2D,
    spherical_variogram
)


class TestSolvers(unittest.TestCase):

    def setUp(self):
        # Deterministic sample dataset for testing
        np.random.seed(42)
        self.n_pts = 30
        self.x = np.random.uniform(-0.9, 0.9, self.n_pts)
        self.y = np.random.uniform(-0.9, 0.9, self.n_pts)
        # Synthetic quadratic + noise
        self.z = 25.0 - 2.0 * self.x + 1.5 * self.y + 0.5 * self.x**2 - 0.8 * self.y**2 + np.random.normal(0, 0.1, self.n_pts)

    def test_polynomial_surface_exact_quadratic_recovery(self):
        # A noiseless quadratic surface should be recovered to machine precision
        x = np.linspace(-1, 1, 20)
        y = np.linspace(-1, 1, 20)
        X, Y = np.meshgrid(x, y)
        Z = 10.0 + 2.0 * X - 3.0 * Y + 1.5 * X**2 - 0.5 * X * Y + 2.0 * Y**2

        model = PolynomialSurface(X.ravel(), Y.ravel(), Z.ravel(), degree=2)
        
        # Test predictions at test coordinates
        x_test = np.array([0.1, -0.3, 0.5])
        y_test = np.array([-0.2, 0.4, -0.1])
        z_expected = 10.0 + 2.0 * x_test - 3.0 * y_test + 1.5 * x_test**2 - 0.5 * x_test * y_test + 2.0 * y_test**2
        z_pred = model(x_test, y_test)

        np.testing.assert_allclose(z_pred, z_expected, rtol=1e-5, atol=1e-5)

    def test_polynomial_surface_shapes(self):
        model = PolynomialSurface(self.x, self.y, self.z)
        
        # Scalar
        val = model(0.0, 0.0)
        self.assertTrue(np.isscalar(val) or val.ndim == 0)
        
        # Vector
        vec = model(np.array([0.1, 0.2]), np.array([0.3, 0.4]))
        self.assertEqual(vec.shape, (2,))
        
        # Grid
        grid = model(np.zeros((5, 5)), np.ones((5, 5)))
        self.assertEqual(grid.shape, (5, 5))

    def test_idw_exact_coincidence(self):
        # IDW must return exact observation value when evaluated at training points
        model = InverseDistanceWeighting(self.x, self.y, self.z, power=2.0)
        
        # Evaluate at exact training points
        z_pred_at_obs = model(self.x, self.y)
        np.testing.assert_allclose(z_pred_at_obs, self.z, atol=1e-8)

    def test_idw_midpoint_symmetry(self):
        # Two points: (0, 0) with z=10 and (2, 0) with z=20.
        # Midpoint is (1, 0), distance is equal, so value should be exactly 15.0
        x = np.array([0.0, 2.0])
        y = np.array([0.0, 0.0])
        z = np.array([10.0, 20.0])
        model = InverseDistanceWeighting(x, y, z, power=2.0)
        
        val = model(1.0, 0.0)
        self.assertAlmostEqual(val, 15.0, places=6)

    def test_rbf_exact_interpolation(self):
        # Thin-Plate Spline with smoothing=0.0 must interpolate observations exactly
        model = RadialBasisFunctions2D(self.x, self.y, self.z, smoothing=0.0)
        z_pred_at_obs = model(self.x, self.y)
        np.testing.assert_allclose(z_pred_at_obs, self.z, atol=1e-5)

    def test_rbf_drift_constraints(self):
        # TPS weights w must satisfy: sum(w) = 0, sum(w * x) = 0, sum(w * y) = 0
        model = RadialBasisFunctions2D(self.x, self.y, self.z, smoothing=0.0)
        self.assertAlmostEqual(np.sum(model.w), 0.0, places=6)
        self.assertAlmostEqual(np.sum(model.w * self.x), 0.0, places=6)
        self.assertAlmostEqual(np.sum(model.w * self.y), 0.0, places=6)

    def test_spherical_variogram(self):
        c0, c, a = 0.1, 1.0, 0.5
        # h = 0 -> 0
        self.assertAlmostEqual(spherical_variogram(0.0, c0, c, a), 0.0)
        # h = a -> c0 + c
        self.assertAlmostEqual(spherical_variogram(a, c0, c, a), c0 + c, places=6)
        # h > a -> c0 + c
        self.assertAlmostEqual(spherical_variogram(1.0, c0, c, a), c0 + c, places=6)
        # 0 < h < a -> intermediate value
        gamma_half = spherical_variogram(0.25, c0, c, a)
        self.assertGreater(gamma_half, c0)
        self.assertLess(gamma_half, c0 + c)

    def test_ordinary_kriging_fitting_and_prediction(self):
        # Fit Ordinary Kriging on sample data
        model = OrdinaryKriging2D(self.x, self.y, self.z)
        
        # Variogram parameters must be positive
        self.assertGreaterEqual(model.c0, 0.0)
        self.assertGreater(model.c, 0.0)
        self.assertGreater(model.a, 0.0)
        
        # Prediction over test points
        x_test = np.array([0.0, 0.2, -0.2])
        y_test = np.array([0.0, -0.1, 0.3])
        z_pred = model(x_test, y_test)
        
        self.assertEqual(len(z_pred), 3)
        self.assertFalse(np.any(np.isnan(z_pred)), "Kriging predictions must not contain NaN.")
        self.assertFalse(np.any(np.isinf(z_pred)), "Kriging predictions must not contain Inf.")


if __name__ == '__main__':
    unittest.main()
