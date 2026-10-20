"""
Unit tests for PSF simulation (Moffat and spatial fields).
"""

import unittest
import numpy as np
from simulation.moffat import generate_moffat_psf, compute_moffat_alpha
from simulation.spatial_fields import PolynomialField2D, CorrelatedRandomField2D
from validation.moments import compute_weighted_moments


class TestPSFSimulation(unittest.TestCase):

    def test_moffat_normalization_and_finiteness(self):
        """Moffat PSF must be non-negative, finite, and have unit total flux."""
        psf = generate_moffat_psf(fwhm=3.5, beta=3.5, e1=0.05, e2=-0.03, stamp_size=48)
        self.assertEqual(psf.shape, (48, 48))
        self.assertTrue(np.all(np.isfinite(psf)))
        self.assertTrue(np.all(psf >= 0.0))
        self.assertAlmostEqual(float(np.sum(psf)), 1.0, places=6)

    def test_moffat_determinism(self):
        """Identical inputs must yield identical images to machine precision."""
        psf1 = generate_moffat_psf(fwhm=3.8, beta=3.0, e1=0.04, e2=0.02)
        psf2 = generate_moffat_psf(fwhm=3.8, beta=3.0, e1=0.04, e2=0.02)
        np.testing.assert_allclose(psf1, psf2, rtol=1e-14, atol=1e-14)

    def test_circular_moffat_symmetry(self):
        """Circular Moffat (e1=0, e2=0) must yield negligible measured ellipticity."""
        psf = generate_moffat_psf(fwhm=3.5, beta=3.5, e1=0.0, e2=0.0, stamp_size=48)
        moments = compute_weighted_moments(psf, sigma_w=3.5)
        self.assertAlmostEqual(moments.e1, 0.0, delta=1e-5)
        self.assertAlmostEqual(moments.e2, 0.0, delta=1e-5)
        self.assertAlmostEqual(moments.e_mag, 0.0, delta=1e-5)

    def test_elliptical_moffat_orientation(self):
        """Positive e1 elongation along x-axis must result in Q11 > Q22 and positive measured e1."""
        psf = generate_moffat_psf(fwhm=3.5, beta=3.5, e1=0.10, e2=0.0, stamp_size=48)
        moments = compute_weighted_moments(psf, sigma_w=3.5)
        self.assertGreater(moments.q11, moments.q22)
        self.assertGreater(moments.e1, 0.05)
        self.assertAlmostEqual(moments.e2, 0.0, delta=1e-4)

    def test_polynomial_field_eval(self):
        """Polynomial field should evaluate exactly at known points."""
        coeffs = {(0, 0): 2.0, (1, 0): 3.0, (0, 2): -1.5}
        field = PolynomialField2D(degree=2, coefficients=coeffs)
        val = field.evaluate(np.array([2.0]), np.array([3.0]))
        # 2 + 3*(2) - 1.5*(9) = 2 + 6 - 13.5 = -5.5
        self.assertAlmostEqual(float(val[0]), -5.5, places=7)

    def test_correlated_random_field_reproducibility(self):
        """Correlated random field must produce identical evaluations for the same seed."""
        rf1 = CorrelatedRandomField2D(correlation_length=0.2, seed=42)
        rf2 = CorrelatedRandomField2D(correlation_length=0.2, seed=42)
        pts = np.array([[0.2, 0.3], [0.7, 0.8]])
        np.testing.assert_allclose(rf1(pts), rf2(pts), rtol=1e-12)


if __name__ == "__main__":
    unittest.main()
