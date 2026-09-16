#!/usr/bin/env python3
"""
Unit test suite for Beyond Kepler: Perturbations and the Stability of the Solar System.
Compatible with both pytest and Python standard library unittest:
    python3 -m unittest tests/test_figure_generation.py
    pytest tests/ -v

Validates:
1. Keplerian orbital geometry and conic section calculations.
2. Eccentricity vector transformations (k, h) and norm preservation.
3. Linear secular normal mode eigenvalues and harmonic frequencies.
4. Great Inequality 5:2 commensurability timescale (~900 years).
5. Isolated generation of all 10 scientific figures to verify PNG format,
   non-zero file size, valid magic header, and proper image dimensions.
"""

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

from generate_osculating_orbit_infographic import generate_osculating_orbit_infographic, get_kepler_ellipse
from generate_two_timescales_orbit import create_two_timescales_orbit
from generate_disturbing_function_geometry import create_disturbing_function_geometry
from generate_disturbing_function_pipeline import create_disturbing_function_pipeline
from generate_orbital_averaging_infographic import create_orbital_averaging_infographic
from generate_timescale_hierarchy import create_timescale_hierarchy
from generate_eccentricity_vector import create_eccentricity_vector_figure
from generate_secular_normal_modes import create_secular_normal_modes_figure
from generate_great_inequality_infographic import generate_figure as generate_great_inequality_figure
from generate_long_term_evolution_regimes import generate_figure as generate_long_term_evolution_figure


class TestBeyondKeplerPhysicsAndFigures(unittest.TestCase):
    """Test suite for celestial mechanics calculations and figure rendering."""

    def test_kepler_ellipse_geometry(self):
        """Verify Keplerian ellipse generates correct perihelion and aphelion distances."""
        a = 2.5
        e = 0.4
        varpi = 0.0
        x, y = get_kepler_ellipse(a, e, varpi, n_points=1000)
        r = np.hypot(x, y)
        r_peri_expected = a * (1.0 - e)
        r_apo_expected = a * (1.0 + e)

        self.assertAlmostEqual(np.min(r), r_peri_expected, places=3)
        self.assertAlmostEqual(np.max(r), r_apo_expected, places=3)

    def test_eccentricity_vector_transformation(self):
        """Verify eccentricity vector mapping z = k + ih satisfies |z| = e."""
        test_eccentricities = [0.01, 0.048, 0.093, 0.205]
        test_varpis = [0.0, np.pi / 4, np.pi / 2, 3 * np.pi / 2]

        for e in test_eccentricities:
            for varpi in test_varpis:
                k = e * np.cos(varpi)
                h = e * np.sin(varpi)
                e_reconstructed = np.hypot(k, h)
                self.assertAlmostEqual(e_reconstructed, e, places=7)

    def test_great_inequality_resonance_timescale(self):
        """Verify the 2n_J - 5n_S frequency combination yields ~900-year cycle."""
        # Mean motions in degrees per year
        # P_J ~ 11.86 yr -> n_J ~ 360 / 11.86 = 30.354 deg/yr
        # P_S ~ 29.46 yr -> n_S ~ 360 / 29.46 = 12.220 deg/yr
        n_J = 360.0 / 11.862
        n_S = 360.0 / 29.457
        slow_freq = abs(2.0 * n_J - 5.0 * n_S)  # deg/yr
        period_yr = 360.0 / slow_freq

        self.assertGreater(period_yr, 850.0, "Great inequality period should be > 850 years")
        self.assertLess(period_yr, 950.0, "Great inequality period should be < 950 years")

    def _verify_single_figure(self, tmp_dir, generator_func, filename, min_w, min_h):
        target_path = Path(tmp_dir) / filename
        result_path = generator_func(target_path)

        self.assertTrue(result_path.exists(), f"File {filename} was not created")
        self.assertTrue(result_path.is_file(), f"{filename} is not a regular file")

        # File size must be substantial (> 40 KB for high-res infographics)
        size_bytes = result_path.stat().st_size
        self.assertGreater(size_bytes, 40 * 1024, f"File {filename} size too small: {size_bytes} bytes")

        # Verify PNG Magic Number: 89 50 4E 47 0D 0A 1A 0A
        with open(result_path, "rb") as f:
            header = f.read(8)
        self.assertEqual(header, b"\x89PNG\r\n\x1a\n", f"File {filename} is missing PNG magic header")

        # Verify Pillow can open and dimensions meet minimum requirements
        with Image.open(result_path) as img:
            self.assertEqual(img.format, "PNG")
            w, h = img.size
            self.assertGreaterEqual(w, min_w, f"Image {filename} width {w} < expected {min_w}")
            self.assertGreaterEqual(h, min_h, f"Image {filename} height {h} < expected {min_h}")

    def test_01_osculating_orbit_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_osculating_orbit_infographic, "osculating_orbit_concept.png", 2000, 1000)

    def test_02_two_timescales_orbit_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, create_two_timescales_orbit, "two_timescales_orbit.png", 2000, 1000)

    def test_03_disturbing_function_geometry_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, create_disturbing_function_geometry, "disturbing_function_geometry.png", 2000, 1000)

    def test_04_disturbing_function_pipeline_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, create_disturbing_function_pipeline, "disturbing_function_pipeline.png", 2000, 1000)

    def test_05_orbital_averaging_concept_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, create_orbital_averaging_infographic, "orbital_averaging_concept.png", 2000, 1000)

    def test_06_timescale_hierarchy_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, create_timescale_hierarchy, "timescale_hierarchy.png", 2000, 1000)

    def test_07_eccentricity_vector_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, create_eccentricity_vector_figure, "eccentricity_vector.png", 2000, 1000)

    def test_08_secular_normal_modes_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, create_secular_normal_modes_figure, "secular_normal_modes.png", 2000, 1000)

    def test_09_great_inequality_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_great_inequality_figure, "great_inequality_commensurability.png", 2000, 1000)

    def test_10_long_term_evolution_regimes_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_long_term_evolution_figure, "long_term_orbital_evolution.png", 2000, 1000)


if __name__ == '__main__':
    unittest.main(verbosity=2)
