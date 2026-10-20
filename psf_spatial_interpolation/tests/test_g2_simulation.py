"""
Unit tests for Scenario G2 simulation:
- Deterministic reproducibility
- Optical aberrations and correlated atmospheric fluctuations
- Dataset serialization and loading
"""

import unittest
from pathlib import Path
import numpy as np

from simulation.dataset import (
    ComplexGroundFieldGenerator,
    build_field_dataset,
    save_field_dataset,
    load_dataset
)
from simulation.moffat import generate_moffat_psf
from validation.moments import compute_weighted_moments


class TestG2Simulation(unittest.TestCase):
    def setUp(self):
        self.generator = ComplexGroundFieldGenerator(
            seed=500,
            base_fwhm=3.4,
            defocus_coeff=1.2,
            astig_coeff=0.10,
            coma_coeff=0.08,
            beta_base=3.5,
            correlation_length=0.20
        )

    def test_g2_determinism(self):
        """Identical inputs must yield identical PSF images to machine precision."""
        psf1 = self.generator.generate_psf(0.35, 0.65)
        psf2 = self.generator.generate_psf(0.35, 0.65)
        np.testing.assert_array_equal(psf1, psf2)

    def test_g2_psf_normalization_and_positivity(self):
        """G2 PSFs must have unit flux, be non-negative, and have valid shape."""
        psf = self.generator.generate_psf(0.8, 0.2)
        self.assertEqual(psf.shape, (48, 48))
        self.assertAlmostEqual(float(np.sum(psf)), 1.0, places=7)
        self.assertTrue(np.all(psf >= 0.0))

    def test_g2_has_correlated_fluctuations_beyond_polynomial(self):
        """Parameters must not be purely polynomial; residuals must be non-zero."""
        coords = np.linspace(0.1, 0.9, 15)
        grid_x, grid_y = np.meshgrid(coords, coords)
        pts = np.column_stack([grid_x.ravel(), grid_y.ravel()])
        params = self.generator.eval_parameters(pts)
        fwhm = params["fwhm"]

        # Fit quadratic polynomial
        x = pts[:, 0]
        y = pts[:, 1]
        A = np.column_stack([np.ones_like(x), x, y, x**2, x*y, y**2])
        coeffs, residuals, _, _ = np.linalg.lstsq(A, fwhm, rcond=None)
        pred = A @ coeffs
        residual_std = np.std(fwhm - pred)
        # Residual std from Matérn turbulence should be ~ 0.15 px
        self.assertGreater(residual_std, 0.05, "G2 FWHM should have non-trivial correlated fluctuations")

    def test_g2_optical_coma_asymmetry(self):
        """Optical coma should produce centroid shift away from geometric center (23.5, 23.5)."""
        # At corner (0.9, 0.9), coma is strong
        psf_corner = self.generator.generate_psf(0.9, 0.9)
        # At center (0.5, 0.5), coma is zero
        psf_center = self.generator.generate_psf(0.5, 0.5)

        m_corner = compute_weighted_moments(psf_corner, sigma_w=3.5)
        m_center = compute_weighted_moments(psf_center, sigma_w=3.5)

        # Center should be centered near 23.5
        self.assertAlmostEqual(m_center.x_bar, 23.5, places=1)
        self.assertAlmostEqual(m_center.y_bar, 23.5, places=1)

        # Corner should exhibit centroid displacement due to optical coma
        dx_corner = abs(m_corner.x_bar - 23.5)
        dy_corner = abs(m_corner.y_bar - 23.5)
        self.assertGreater(dx_corner + dy_corner, 0.01)

    def test_g2_dataset_loading(self):
        """G2 dataset directory data/field_g2 should load correctly."""
        data_dir = Path(__file__).resolve().parent.parent / "data" / "field_g2"
        if data_dir.exists():
            ds = load_dataset(str(data_dir))
            self.assertEqual(len(ds.positions_train), 320)
            self.assertEqual(len(ds.positions_val), 80)
            self.assertEqual(len(ds.positions_test), 200)
            self.assertEqual(ds.psfs_train_true.shape, (320, 48, 48))


if __name__ == "__main__":
    unittest.main()
