"""
Unit tests for weighted moment calculations and dataset consistency.
"""

import os
import unittest
import numpy as np
from pathlib import Path
from validation.moments import compute_weighted_moments, measure_psf_batch
from simulation.moffat import generate_moffat_psf

BASE_DIR = Path(__file__).resolve().parent.parent


class TestMoments(unittest.TestCase):

    def test_saved_dataset_moments_match_images(self):
        """Verify that saved physical_parameters.npz strictly matches recomputed moments from image stamps."""
        data_dir = BASE_DIR / "data" / "field_000"
        if not (data_dir / "psf_test_true.npy").exists():
            self.skipTest("field_000 dataset not yet generated on disk")

        psfs = np.load(data_dir / "psf_test_true.npy")
        params = np.load(data_dir / "physical_parameters.npz")

        re_e1, re_e2, re_r2 = measure_psf_batch(psfs, sigma_w=3.5)

        np.testing.assert_allclose(re_e1, params["true_test_e1"], atol=1e-12)
        np.testing.assert_allclose(re_e2, params["true_test_e2"], atol=1e-12)
        np.testing.assert_allclose(re_r2, params["true_test_r2"], atol=1e-12)

    def test_centroid_convergence(self):
        """Centroid measurement on a centered Moffat image must match image center (23.5, 23.5)."""
        psf = generate_moffat_psf(fwhm=3.5, beta=3.5, stamp_size=48)
        m = compute_weighted_moments(psf, sigma_w=3.5)
        self.assertAlmostEqual(m.x_bar, 23.5, places=5)
        self.assertAlmostEqual(m.y_bar, 23.5, places=5)


if __name__ == "__main__":
    unittest.main()
