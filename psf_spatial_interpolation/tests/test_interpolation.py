"""
Unit tests for spatial interpolator algorithms:
- PolynomialInterpolator (exact polynomial recovery)
- IDWInterpolator (exact coincidence & symmetry)
- RBFInterpolator (TPS interpolation)
- OrdinaryKrigingInterpolator (multi-component kriging)
- RandomForestInterpolator
- MLPInterpolator
"""

import unittest
import numpy as np
from interpolation.classical import PolynomialInterpolator, IDWInterpolator, RBFInterpolator
from interpolation.kriging import OrdinaryKrigingInterpolator, UniversalKrigingInterpolator
from interpolation.ml import RandomForestInterpolator, MLPInterpolator


class TestSpatialInterpolation(unittest.TestCase):

    def setUp(self):
        rng = np.random.default_rng(42)
        self.n_pts = 40
        self.positions = rng.uniform(0.05, 0.95, (self.n_pts, 2))
        self.test_positions = rng.uniform(0.1, 0.9, (15, 2))

    def test_polynomial_exact_linear_recovery(self):
        """Degree 1 polynomial regression must recover a linear field to machine precision."""
        x, y = self.positions[:, 0], self.positions[:, 1]
        c1 = 5.0 + 2.0 * x - 3.0 * y
        c2 = -1.0 - 4.0 * x + 7.0 * y
        coeffs = np.column_stack([c1, c2])

        model = PolynomialInterpolator(degree=1)
        model.fit(self.positions, coeffs)

        tx, ty = self.test_positions[:, 0], self.test_positions[:, 1]
        expected = np.column_stack([
            5.0 + 2.0 * tx - 3.0 * ty,
            -1.0 - 4.0 * tx + 7.0 * ty
        ])
        pred = model.predict(self.test_positions)
        np.testing.assert_allclose(pred, expected, rtol=1e-10, atol=1e-10)

    def test_polynomial_exact_quadratic_recovery(self):
        """Degree 2 polynomial regression must recover quadratic field to machine precision."""
        x, y = self.positions[:, 0], self.positions[:, 1]
        c = 2.0 + 3.0 * x - 1.5 * y + 4.0 * (x**2) - 2.5 * x * y + 3.0 * (y**2)
        coeffs = c[:, None]

        model = PolynomialInterpolator(degree=2)
        model.fit(self.positions, coeffs)

        tx, ty = self.test_positions[:, 0], self.test_positions[:, 1]
        expected = (2.0 + 3.0 * tx - 1.5 * ty + 4.0 * (tx**2) - 2.5 * tx * ty + 3.0 * (ty**2))[:, None]
        pred = model.predict(self.test_positions)
        np.testing.assert_allclose(pred, expected, rtol=1e-10, atol=1e-10)

    def test_universal_kriging_exact_quadratic_recovery(self):
        """Quadratic Universal Kriging must recover a quadratic trend field."""
        x, y = self.positions[:, 0], self.positions[:, 1]
        c = 2.0 + 3.0 * x - 1.5 * y + 4.0 * (x**2) - 2.5 * x * y + 3.0 * (y**2)
        coeffs = c[:, None]

        model = UniversalKrigingInterpolator(trend="quadratic")
        model.fit(self.positions, coeffs)

        tx, ty = self.test_positions[:, 0], self.test_positions[:, 1]
        expected = (2.0 + 3.0 * tx - 1.5 * ty + 4.0 * (tx**2) - 2.5 * tx * ty + 3.0 * (ty**2))[:, None]
        pred = model.predict(self.test_positions)
        np.testing.assert_allclose(pred, expected, rtol=1e-6, atol=1e-6)

    def test_universal_kriging_exact_linear_recovery(self):
        """Linear Universal Kriging must recover a linear trend field."""
        x, y = self.positions[:, 0], self.positions[:, 1]
        c = 1.5 + 4.0 * x - 2.0 * y
        coeffs = c[:, None]

        model = UniversalKrigingInterpolator(trend="linear")
        model.fit(self.positions, coeffs)

        tx, ty = self.test_positions[:, 0], self.test_positions[:, 1]
        expected = (1.5 + 4.0 * tx - 2.0 * ty)[:, None]
        pred = model.predict(self.test_positions)
        np.testing.assert_allclose(pred, expected, rtol=1e-6, atol=1e-6)

    def test_idw_exact_coincidence(self):
        """IDW must return exact observation value when evaluated at training points."""
        rng = np.random.default_rng(123)
        coeffs = rng.normal(0, 1, (self.n_pts, 3))

        model = IDWInterpolator(power=2.0)
        model.fit(self.positions, coeffs)

        pred_at_train = model.predict(self.positions)
        np.testing.assert_allclose(pred_at_train, coeffs, atol=1e-10)

    def test_rbf_exact_interpolation(self):
        """Thin-Plate Spline with zero smoothing must interpolate training points."""
        rng = np.random.default_rng(456)
        coeffs = rng.normal(0, 1, (self.n_pts, 2))

        model = RBFInterpolator(smoothing=0.0)
        model.fit(self.positions, coeffs)

        pred_at_train = model.predict(self.positions)
        np.testing.assert_allclose(pred_at_train, coeffs, atol=1e-6)

    def test_constant_field_all_interpolators(self):
        """Every interpolator must reproduce a constant field."""
        const_val = np.array([[3.14, -2.71]])
        coeffs = np.repeat(const_val, self.n_pts, axis=0)

        interpolators = [
            ("POLY", PolynomialInterpolator(degree=1)),
            ("IDW", IDWInterpolator(power=2.0)),
            ("RBF", RBFInterpolator(smoothing=1e-8)),
            ("OK", OrdinaryKrigingInterpolator()),
            ("UK_lin", UniversalKrigingInterpolator(trend="linear")),
            ("UK_quad", UniversalKrigingInterpolator(trend="quadratic")),
            ("RF", RandomForestInterpolator(n_estimators=30, random_state=42)),
            ("MLP", MLPInterpolator(hidden_layer_sizes=(16,), alpha=0.001, random_state=42)),
        ]

        for name, model in interpolators:
            with self.subTest(method=name):
                model.fit(self.positions, coeffs)
                pred = model.predict(self.test_positions)
                # Should predict close to constant vector
                np.testing.assert_allclose(pred[:, 0], 3.14, rtol=0.05, atol=0.05)
                np.testing.assert_allclose(pred[:, 1], -2.71, rtol=0.05, atol=0.05)


if __name__ == "__main__":
    unittest.main()

