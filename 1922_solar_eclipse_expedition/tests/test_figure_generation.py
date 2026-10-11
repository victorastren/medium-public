#!/usr/bin/env python3
"""
Unit test suite for the generation of scientific illustrations and astrophysics in:
The 1922 Solar Eclipse: A More Precise Test of General Relativity

Compatible with both Python standard library unittest and pytest:
    python3 -m unittest tests/test_figure_generation.py
    pytest tests/ -v

Validates:
1. Physical and mathematical foundations of gravitational starlight deflection:
   - Einstein general-relativistic deflection formula at the solar limb (1.75″).
   - Newtonian corpuscular deflection formula (0.87″).
   - Theoretical factor of 2.0 between GR and Newtonian deflection.
   - Hyperbolic inverse radial fall-off with distance from solar center (δθ ∝ 1/ρ).
   - Statistical consistency of Wallal 1923 and 1928 empirical results with GR.
2. Isolated generation of all 6 scientific figures/infographics into a temporary directory:
   - Verifies PNG format, magic byte header (\x89PNG\r\n\x1a\n).
   - Non-zero file size exceeding minimum threshold.
   - Proper pixel dimensions and aspect ratios (including 680px Medium layout and 2x Retina versions).
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

# Ensure code directory is in sys.path
TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
CODE_DIR = PROJECT_DIR / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

# Import generator routines
from generate_light_deflection_diagram import generate_deflection_diagram
from generate_predictions_comparison import generate_comparison_diagram
from generate_wallal_experimental_design import create_schematic as create_experimental_design
from generate_wallal_cameras_schematic import create_schematic as create_cameras_schematic
from generate_plate_measurement_schematic import generate_schematic as generate_plate_schematic
from generate_deflection_results import create_results_plot


class TestLightDeflectionAstrophysics(unittest.TestCase):
    """Unit tests for the astronomical and physical invariants underlying the figures."""

    def setUp(self):
        # Fundamental physical constants (SI units)
        self.G = 6.67430e-11           # m^3 kg^-1 s^-2
        self.M_sun = 1.98847e30        # kg
        self.c = 299792458.0           # m s^-1
        self.R_sun = 6.957e8           # m (nominal solar radius)
        self.rad_to_arcsec = 180.0 * 3600.0 / np.pi

    def test_einstein_starlight_deflection_formula(self):
        """Verify Einstein's 1915 general-relativistic limb deflection: delta_theta = 4GM / (c^2 R)."""
        theta_rad = (4.0 * self.G * self.M_sun) / (self.c**2 * self.R_sun)
        theta_arcsec = theta_rad * self.rad_to_arcsec
        # Expected value is ~1.751 arcseconds
        self.assertAlmostEqual(theta_arcsec, 1.751, delta=0.01,
                               msg="General relativistic limb deflection should be approximately 1.75 arcseconds.")

    def test_newtonian_deflection_formula(self):
        """Verify Newtonian / 1911 equivalence-principle deflection: delta_theta = 2GM / (c^2 R)."""
        theta_rad = (2.0 * self.G * self.M_sun) / (self.c**2 * self.R_sun)
        theta_arcsec = theta_rad * self.rad_to_arcsec
        # Expected value is ~0.876 arcseconds
        self.assertAlmostEqual(theta_arcsec, 0.876, delta=0.01,
                               msg="Newtonian / 1911 deflection should be approximately 0.87 arcseconds.")

    def test_gr_to_newtonian_exact_ratio(self):
        """Verify that general relativity predicts exactly twice the Newtonian deflection."""
        theta_gr = (4.0 * self.G * self.M_sun) / (self.c**2 * self.R_sun)
        theta_newton = (2.0 * self.G * self.M_sun) / (self.c**2 * self.R_sun)
        ratio = theta_gr / theta_newton
        self.assertAlmostEqual(ratio, 2.0, places=7,
                               msg="GR to Newtonian light deflection ratio must be exactly 2.0.")

    def test_radial_deflection_falloff(self):
        """Verify hyperbolic fall-off: delta_theta(rho) = delta_theta_limb * (R_sun / rho)."""
        theta_limb = 1.75
        radii = np.array([1.0, 1.5, 2.0, 3.0, 4.0, 5.0])
        deflections = theta_limb / radii

        # Must be strictly monotonically decreasing
        self.assertTrue(np.all(np.diff(deflections) < 0),
                        "Deflection must decrease monotonically with increasing distance from Sun.")
        # At 2 solar radii, deflection should be exactly half of limb deflection
        self.assertAlmostEqual(deflections[2], 1.75 / 2.0, places=5)
        # At 4 solar radii, deflection should be one-quarter
        self.assertAlmostEqual(deflections[4], 1.75 / 4.0, places=5)

    def test_wallal_observational_data_consistency(self):
        """Verify statistical significance of Wallal measurements relative to GR and Newtonian predictions."""
        gr_pred = 1.75
        newton_pred = 0.87

        # 1923 Campbell & Trumpler 15-foot camera result: 1.72" +/- 0.11"
        obs_1923 = 1.72
        err_1923 = 0.11
        z_gr_1923 = abs(obs_1923 - gr_pred) / err_1923
        z_newton_1923 = abs(obs_1923 - newton_pred) / err_1923
        self.assertLess(z_gr_1923, 0.5, "1923 Wallal result must be within 0.5 sigma of Einstein GR prediction.")
        self.assertGreater(z_newton_1923, 7.0, "1923 Wallal result must reject Newtonian prediction by > 7 sigma.")

        # 1928 Trumpler final combined Wallal result: 1.75" +/- 0.09"
        obs_1928 = 1.75
        err_1928 = 0.09
        z_gr_1928 = abs(obs_1928 - gr_pred) / err_1928
        z_newton_1928 = abs(obs_1928 - newton_pred) / err_1928
        self.assertAlmostEqual(z_gr_1928, 0.0, places=5, msg="1928 final Wallal result exactly matches GR prediction.")
        self.assertGreater(z_newton_1928, 9.0, msg="1928 final Wallal result must reject Newtonian prediction by > 9 sigma.")


class TestFigureGeneration(unittest.TestCase):
    """Unit tests validating isolated generation of all article illustrations."""

    def _verify_png_image(self, file_path, min_w=500, min_h=200, min_size_kb=20):
        """Helper to verify file existence, PNG magic header, Pillow validity, and dimensions."""
        file_path = Path(file_path)
        self.assertTrue(file_path.exists(), f"Output file does not exist: {file_path}")
        self.assertTrue(file_path.is_file(), f"Output is not a regular file: {file_path}")

        # Check file size
        size_bytes = file_path.stat().st_size
        self.assertGreater(size_bytes, min_size_kb * 1024,
                           f"File {file_path.name} is smaller than expected: {size_bytes} bytes")

        # Verify PNG 8-byte magic header
        with open(file_path, "rb") as f:
            header = f.read(8)
        self.assertEqual(header, b"\x89PNG\r\n\x1a\n",
                         f"File {file_path.name} does not have valid PNG magic header.")

        # Verify PIL can open and decode the image
        with Image.open(file_path) as img:
            self.assertEqual(img.format, "PNG", f"{file_path.name} format must be PNG.")
            self.assertIn(img.mode, ("RGB", "RGBA"), f"{file_path.name} mode must be RGB or RGBA.")
            w, h = img.size
            self.assertGreaterEqual(w, min_w,
                                    f"{file_path.name} width {w}px is less than minimum {min_w}px.")
            self.assertGreaterEqual(h, min_h,
                                    f"{file_path.name} height {h}px is less than minimum {min_h}px.")
            return w, h

    def test_generate_light_deflection_diagram(self):
        """Verify gravitational light deflection geometry diagram generator (680px and 2x)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            prefix = "test_light_deflection"
            generate_deflection_diagram(out_dir=tmp_dir, filename_prefix=prefix)

            out_1x = Path(tmp_dir) / f"{prefix}.png"
            out_2x = Path(tmp_dir) / f"{prefix}_2x.png"

            w1, h1 = self._verify_png_image(out_1x, min_w=680, min_h=300, min_size_kb=30)
            w2, h2 = self._verify_png_image(out_2x, min_w=2000, min_h=1000, min_size_kb=100)

            self.assertEqual(w1, 680)
            self.assertEqual(w2, 2400)

    def test_generate_predictions_comparison(self):
        """Verify light-deflection predictions comparison diagram generator (680px and 2x)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            prefix = "test_predictions_comparison"
            generate_comparison_diagram(out_dir=tmp_dir, filename_prefix=prefix)

            out_1x = Path(tmp_dir) / f"{prefix}.png"
            out_2x = Path(tmp_dir) / f"{prefix}_2x.png"

            w1, h1 = self._verify_png_image(out_1x, min_w=680, min_h=400, min_size_kb=50)
            w2, h2 = self._verify_png_image(out_2x, min_w=2000, min_h=1400, min_size_kb=150)

            self.assertEqual(w1, 680)
            self.assertEqual(w2, 2400)

    def test_generate_wallal_experimental_design(self):
        """Verify Tahiti and Wallal experimental design schematic generator."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_1x = Path(tmp_dir) / "wallal_experimental_design.png"
            create_experimental_design(output_path=out_1x)

            w, h = self._verify_png_image(out_1x, min_w=1900, min_h=1000, min_size_kb=60)
            self.assertEqual(w, 2040)
            self.assertEqual(h, 1130)

    def test_generate_wallal_cameras_schematic(self):
        """Verify twin cameras optical and equatorial schematic generator."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_1x = Path(tmp_dir) / "wallal_twin_cameras_schematic.png"
            create_cameras_schematic(output_path=out_1x)

            w, h = self._verify_png_image(out_1x, min_w=1900, min_h=1100, min_size_kb=80)
            self.assertEqual(w, 2040)
            self.assertEqual(h, 1240)

    def test_generate_plate_measurement_schematic(self):
        """Verify intermediate plate measurement schematic generator (680px and 2040px 2x)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_1x = Path(tmp_dir) / "wallal_plate_measurement_method.png"
            out_2x = Path(tmp_dir) / "wallal_plate_measurement_method_2x.png"
            generate_plate_schematic(output_path=out_1x, output_path_2x=out_2x)

            w1, h1 = self._verify_png_image(out_1x, min_w=680, min_h=400, min_size_kb=50)
            w2, h2 = self._verify_png_image(out_2x, min_w=2000, min_h=1300, min_size_kb=150)

            self.assertEqual(w1, 680)
            self.assertEqual(w2, 2040)

    def test_generate_deflection_results(self):
        """Verify Wallal deflection results editorial plot generator (680px and 2200px 2x)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_1x = Path(tmp_dir) / "wallal_deflection_results.png"
            out_2x = Path(tmp_dir) / "wallal_deflection_results_2x.png"
            create_results_plot(out_1x=out_1x, out_2x=out_2x)

            w1, h1 = self._verify_png_image(out_1x, min_w=680, min_h=400, min_size_kb=30)
            w2, h2 = self._verify_png_image(out_2x, min_w=2000, min_h=1300, min_size_kb=80)

            self.assertEqual(w1, 680)
            self.assertEqual(w2, 2200)


if __name__ == "__main__":
    unittest.main()
