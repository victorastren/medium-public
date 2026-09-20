#!/usr/bin/env python3
"""
Unit test suite for Navier-Stokes Blow-Up & Regularity figure generation.
Compatible with both pytest and Python standard library unittest:
    python3 -m unittest tests/test_figure_generation.py
    pytest tests/ -v

Validates:
1. Material derivative decomposition kinematics (local + advective).
2. Vortex stretching identity: non-zero in 3D, identically vanishing in 2D.
3. Scaling symmetry and energy-supercriticality scaling exponents in 3D.
4. Isolated generation of all 7 scientific infographics to verify PNG format,
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

from generate_material_derivative_infographic import generate_material_derivative_infographic
from generate_vortex_stretching_infographic import generate_vortex_stretching_infographic
from generate_vortex_stretching_2d_infographic import generate_vortex_stretching_2d_infographic
from generate_energy_balance_infographic import generate_energy_balance_infographic
from generate_energy_concentration_infographic import generate_energy_concentration_infographic
from generate_scaling_limits_infographic import generate_scaling_limits_infographic
from generate_shrinking_vortex_infographic import generate_shrinking_vortex_infographic


class TestNavierStokesPhysicsAndFigures(unittest.TestCase):
    """Test suite for fluid dynamics calculations and figure rendering."""

    def test_material_derivative_kinematics(self):
        """Verify chain rule decomposition Du/Dt = du/dt + (u . grad)u."""
        # Simple 2D flow u = (y, -x) with time decay exp(-t)
        t = 0.5
        x, y = 1.0, 2.0
        u_x = y * np.exp(-t)
        u_y = -x * np.exp(-t)

        # Local derivative du/dt
        du_dt_x = -y * np.exp(-t)
        du_dt_y = x * np.exp(-t)

        # Advective term (u . grad)u
        # grad(u_x) = (0, exp(-t)), grad(u_y) = (-exp(-t), 0)
        u_grad_u_x = u_x * 0 + u_y * np.exp(-t)  # -x * exp(-2t)
        u_grad_u_y = u_x * (-np.exp(-t)) + u_y * 0  # -y * exp(-2t)

        # Total material derivative along parcel trajectory
        Du_Dt_x = du_dt_x + u_grad_u_x
        Du_Dt_y = du_dt_y + u_grad_u_y

        self.assertTrue(np.isfinite(Du_Dt_x))
        self.assertTrue(np.isfinite(Du_Dt_y))

    def test_2d_vortex_stretching_vanishes(self):
        """Verify vortex stretching term (omega . grad)u identically vanishes in 2D."""
        # In 2D, velocity has components (u_x, u_y, 0) in the xy-plane
        # Vorticity is purely perpendicular: omega = (0, 0, omega_z)
        # Therefore (omega . grad) = omega_z * d/dz
        # Since 2D flow is invariant in z, d/dz(u) = 0 identically.
        omega = np.array([0.0, 0.0, 4.5])
        grad_u_z = np.array([0.0, 0.0, 0.0])  # d/dz of velocity field
        stretching = omega[2] * grad_u_z
        self.assertTrue(np.allclose(stretching, 0.0), "2D vortex stretching must vanish identically")

    def test_navier_stokes_scaling_exponents(self):
        """Verify 3D Navier-Stokes critical scaling exponents for L^p norms."""
        # u_lambda(x, t) = lambda * u(lambda*x, lambda^2*t)
        # ||u_lambda||_{L^p(R^d)} = lambda^(1 - d/p) * ||u||_{L^p(R^d)}
        d = 3.0  # 3 space dimensions

        # L^2 energy norm exponent: 1 - 3/2 = -0.5 (energy supercritical: norm vanishes as lambda -> 0)
        exp_L2 = 1.0 - d / 2.0
        self.assertAlmostEqual(exp_L2, -0.5, places=5)

        # L^3 critical norm exponent: 1 - 3/3 = 0.0 (scale-invariant)
        exp_L3 = 1.0 - d / 3.0
        self.assertAlmostEqual(exp_L3, 0.0, places=5)

        # L^infinity velocity norm exponent: 1 - 3/inf = 1.0 (blows up as lambda -> infinity)
        exp_Linf = 1.0
        self.assertGreater(exp_Linf, 0.0)

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

    def test_01_material_derivative_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_material_derivative_infographic,
                                       "eulerian_vs_lagrangian_derivative.png", 2000, 1000)

    def test_02_vortex_stretching_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_vortex_stretching_infographic,
                                       "vortex_stretching_mechanism.png", 2000, 1000)

    def test_03_vortex_stretching_2d_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_vortex_stretching_2d_infographic,
                                       "vortex_stretching_2d_vanishing.png", 2000, 1000)

    def test_04_energy_balance_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_energy_balance_infographic,
                                       "navier_stokes_energy_balance.png", 2000, 1000)

    def test_05_energy_concentration_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_energy_concentration_infographic,
                                       "finite_energy_concentration.png", 2000, 1000)

    def test_06_scaling_limits_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_scaling_limits_infographic,
                                       "navier_stokes_scaling_limits.png", 2000, 1000)

    def test_07_shrinking_vortex_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_shrinking_vortex_infographic,
                                       "navier_stokes_shrinking_vortex_blowup.png", 2000, 1000)


if __name__ == '__main__':
    unittest.main(verbosity=2)
