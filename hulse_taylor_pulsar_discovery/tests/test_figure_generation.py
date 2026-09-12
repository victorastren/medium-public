#!/usr/bin/env python3
"""
Unit test suite for the Hulse-Taylor Binary Pulsar (PSR B1913+16) figure generation.
Compatible with both pytest and Python standard library unittest:
    python3 -m unittest tests/test_figure_generation.py
    pytest tests/ -v

Validates:
1. Keplerian solver numerical precision and convergence across high eccentricities.
2. Binary pulsar relativistic parameters and mass function calculations.
3. Isolated generation of all 7 scientific infographics to verify PNG format,
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

from generate_pulsar_infographic import generate_pulsar_infographic
from generate_doppler_orbit_infographic import generate_doppler_orbit_infographic
from generate_hulse_discovery_evidence import generate_hulse_discovery_evidence, solve_kepler as solve_kepler_hulse
from generate_keplerian_orbit_infographic import generate_keplerian_orbit_infographic
from generate_radial_velocity_curve import generate_radial_velocity_curve, solve_kepler as solve_kepler_rv
from generate_mass_mass_diagram import generate_mass_mass_diagram, calc_gamma, M_tot
from generate_period_decay_infographic import generate_period_decay_infographic


class TestHulseTaylorPhysicsAndFigures(unittest.TestCase):
    """Test suite for astronomical calculations and figure rendering."""

    def test_kepler_solver_convergence(self):
        """Verify Kepler equation solver solves M = E - e*sin(E) with high precision."""
        eccentricities = [0.0, 0.1, 0.6171334, 0.85, 0.95]
        mean_anomalies = np.linspace(0.01, 2 * np.pi - 0.01, 50)

        for ecc in eccentricities:
            E_sol = solve_kepler_rv(mean_anomalies, ecc)
            residual = np.abs(E_sol - ecc * np.sin(E_sol) - mean_anomalies)
            self.assertLess(np.max(residual), 1e-9, f"Kepler equation residual exceeded tolerance for e = {ecc}")

    def test_mass_parameters_consistency(self):
        """Verify total mass and Einstein delay formulas match theoretical expectations."""
        # Total mass for PSR B1913+16 from periastron advance
        self.assertTrue(np.isclose(M_tot, 2.8284, atol=0.01), f"Total mass {M_tot} deviated from expected 2.8284 M_sun")

        # Einstein delay gamma around canonical masses (m1 ~ 1.44 M_sun, m2 ~ 1.39 M_sun)
        gamma_val = calc_gamma(1.4414, 1.3867)
        self.assertTrue(np.isclose(gamma_val, 0.004294, atol=1e-4), f"Einstein delay {gamma_val} deviated from 4.294 ms")

    def _verify_single_figure(self, tmp_dir, generator_func, filename, min_w, min_h):
        target_path = Path(tmp_dir) / filename
        result_path = generator_func(target_path)

        self.assertTrue(result_path.exists(), f"File {filename} was not created")
        self.assertTrue(result_path.is_file(), f"{filename} is not a regular file")

        # File size must be substantial (> 50 KB for high-res infographics)
        size_bytes = result_path.stat().st_size
        self.assertGreater(size_bytes, 50 * 1024, f"File {filename} size too small: {size_bytes} bytes")

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

    def test_01_pulsar_lighthouse_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_pulsar_infographic, "pulsar_lighthouse_infographic.png", 1800, 1000)

    def test_02_doppler_orbit_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_doppler_orbit_infographic, "binary_orbit_doppler_infographic.png", 1800, 900)

    def test_03_hulse_evidence_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_hulse_discovery_evidence, "hulse_discovery_evidence.png", 1800, 900)

    def test_04_keplerian_orbit_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_keplerian_orbit_infographic, "keplerian_orbit_geometry.png", 2000, 1000)

    def test_05_radial_velocity_curve_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_radial_velocity_curve, "radial_velocity_doppler_curve.png", 2000, 1000)

    def test_06_mass_mass_diagram_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_mass_mass_diagram, "mass_mass_diagram.png", 2000, 1000)

    def test_07_period_decay_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_period_decay_infographic, "psr_period_decay_infographic.png", 2000, 1000)


if __name__ == '__main__':
    unittest.main(verbosity=2)
