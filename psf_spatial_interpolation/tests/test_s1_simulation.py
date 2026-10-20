"""
Unit tests for Scenario S1 simulation (diffraction-based space telescope optical PSF).
"""

import unittest
from pathlib import Path
import numpy as np

from simulation.optics import (
    MatrixFourierTransform,
    SpaceOpticsPupil,
    SpaceDiffractionFieldGenerator
)
from simulation.dataset import load_dataset
from validation.moments import compute_weighted_moments


class TestS1Simulation(unittest.TestCase):
    def setUp(self):
        self.generator = SpaceDiffractionFieldGenerator(
            c4_base=0.02,
            a_def=0.08,
            a_ast=0.04,
            a_coma=0.05,
            c11_base=0.02,
            n_pupil=128,
            stamp_size=48,
            subpixel_factor=4,
            sampling_s=2.5,
            obscuration_ratio=0.30,
            strut_width=0.025
        )

    def test_s1_determinism(self):
        """Identical inputs must yield identical PSF images to machine precision."""
        psf1 = self.generator.generate_psf(0.25, 0.75)
        psf2 = self.generator.generate_psf(0.25, 0.75)
        np.testing.assert_array_equal(psf1, psf2)

    def test_s1_flux_normalization_and_positivity(self):
        """PSF must be strictly non-negative, finite, and have unit total flux."""
        psf = self.generator.generate_psf(0.85, 0.15)
        self.assertEqual(psf.shape, (48, 48))
        self.assertAlmostEqual(float(np.sum(psf)), 1.0, places=7)
        self.assertTrue(np.all(psf >= 0.0))
        self.assertGreater(float(np.min(psf)), 0.0)

    def test_s1_centering(self):
        """On-axis star at (0.5, 0.5) must have centroid very close to (23.5, 23.5)."""
        psf_center = self.generator.generate_psf(0.5, 0.5)
        m = compute_weighted_moments(psf_center, sigma_w=3.5)
        self.assertAlmostEqual(m.x_bar, 23.5, places=1)
        self.assertAlmostEqual(m.y_bar, 23.5, places=1)

    def test_s1_diffraction_spikes_presence(self):
        """Spider struts must create distinct diffraction spikes elevating flux along primary axes."""
        gen_no_struts = SpaceDiffractionFieldGenerator(strut_width=0.0)
        psf_struts = self.generator.generate_psf(0.5, 0.5)
        psf_no_struts = gen_no_struts.generate_psf(0.5, 0.5)

        y_idx, x_idx = np.indices((48, 48))
        dx = x_idx - 23.5
        dy = y_idx - 23.5
        spike_mask = ((np.abs(dy) <= 1.0) | (np.abs(dx) <= 1.0)) & (np.sqrt(dx**2 + dy**2) >= 15)

        flux_with = float(np.mean(psf_struts[spike_mask]))
        flux_without = float(np.mean(psf_no_struts[spike_mask]))
        self.assertGreater(flux_with, 1.4 * flux_without, "Diffraction spikes should elevate outer axis flux")

    def test_s1_dataset_loading(self):
        """S1 dataset directory data/field_s1 should load correctly."""
        data_dir = Path(__file__).resolve().parent.parent / "data" / "field_s1"
        if data_dir.exists():
            ds = load_dataset(str(data_dir))
            self.assertEqual(len(ds.positions_train), 320)
            self.assertEqual(len(ds.positions_val), 80)
            self.assertEqual(len(ds.positions_test), 200)
            self.assertEqual(ds.psfs_train_true.shape, (320, 48, 48))


if __name__ == "__main__":
    unittest.main()
