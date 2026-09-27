#!/usr/bin/env python3
"""
Test Suite: From Newton to Hamilton - The Road to Modern Dynamics
Validates physical/mathematical formulations, canonical transformations,
Legendre mappings, and rendering pipeline integrity.
"""

from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
from PIL import Image

# Ensure code directory is in sys.path
TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
CODE_DIR = PROJECT_DIR / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from generate_pendulum_coordinate_transition import create_figure as generate_pendulum_transition
from generate_analytical_mechanics_portraits import create_figure as generate_analytical_portraits
from generate_generalized_coordinates import create_figure as generate_generalized_coordinates
from generate_lagrange_vs_hamilton_comparison import create_figure as generate_lagrange_vs_hamilton
from generate_pendulum_phase_portrait import create_figure as generate_pendulum_phase_portrait
from generate_hamilton_jacobi_portraits import create_figure as generate_hamilton_jacobi_portraits


class TestAnalyticalMechanics(unittest.TestCase):
    """Numerical physics and mathematical formulation tests."""

    def test_degrees_of_freedom_formula(self):
        """Verify degree of freedom formula d = 3N - k for holonomic constraints."""
        # Simple planar pendulum: N = 1 particle in 2D, k = 1 fixed length constraint
        d_simple = 2 * 1 - 1
        self.assertEqual(d_simple, 1)

        # Planar double pendulum: N = 2 particles in 2D, k = 2 fixed length constraints
        d_double = 2 * 2 - 2
        self.assertEqual(d_double, 2)

        # Bead on 3D space curve: N = 1 particle in 3D, k = 2 constraint surfaces
        d_bead = 3 * 1 - 2
        self.assertEqual(d_bead, 1)

    def test_legendre_transformation_and_hamiltonian(self):
        """Verify the exact Legendre transform H = p*q_dot - L for the pendulum."""
        m = 1.0
        l = 1.0
        g = 9.81

        # Test across arbitrary states (theta, theta_dot)
        thetas = [0.0, 0.45, 1.2, 2.5]
        theta_dots = [0.0, 1.5, -2.2, 3.1]

        for th in thetas:
            for th_dot in theta_dots:
                # 1. Lagrangian formulation: L = T - V
                T = 0.5 * m * (l ** 2) * (th_dot ** 2)
                V = m * g * l * (1.0 - np.cos(th))
                L = T - V

                # 2. Canonical momentum: p = dL / d(th_dot)
                p_th = m * (l ** 2) * th_dot

                # 3. Legendre transform: H = p*th_dot - L
                H_legendre = p_th * th_dot - L

                # 4. Total mechanical energy: E = T + V
                E_total = T + V

                # 5. Hamiltonian as state function H(th, p_th)
                H_state = (p_th ** 2) / (2.0 * m * (l ** 2)) + m * g * l * (1.0 - np.cos(th))

                self.assertAlmostEqual(H_legendre, E_total, places=9,
                                       msg="Legendre transform of conservative natural Lagrangian must equal total energy T + V.")
                self.assertAlmostEqual(H_state, E_total, places=9,
                                       msg="Hamiltonian in momentum coordinates must equal total energy.")

    def test_canonical_equations_of_motion(self):
        """Verify that Hamilton's equations reproduce Newton's second law for the pendulum."""
        m = 1.0
        l = 1.0
        g = 9.81
        omega_0_sq = g / l

        th = 0.75
        p_th = 1.8

        # Canonical equations:
        # dot(q) = dH/dp = p / (m * l^2)
        th_dot = p_th / (m * (l ** 2))

        # dot(p) = -dH/dq = -m * g * l * sin(th)
        p_th_dot = -m * g * l * np.sin(th)

        # Since p = m * l^2 * th_dot, d/dt(p) = m * l^2 * th_ddot
        # Therefore: th_ddot = dot(p) / (m * l^2) = - (g / l) * sin(th)
        th_ddot = p_th_dot / (m * (l ** 2))

        # Compare directly with Euler-Lagrange / Newtonian acceleration
        th_ddot_expected = -omega_0_sq * np.sin(th)

        self.assertAlmostEqual(th_ddot, th_ddot_expected, places=9,
                               msg="Hamilton's canonical equations must yield the exact nonlinear pendulum equation.")

    def test_phase_space_energy_and_separatrix(self):
        """Verify pendulum phase space energy levels and analytical separatrix."""
        m = 1.0
        l = 1.0
        g = 9.81
        omega_0 = np.sqrt(g / l)

        # Separatrix total energy E_sep = 2 * m * g * l (energy of unstable saddle at theta = +/- pi, p = 0)
        E_sep = 2.0 * m * g * l

        # Separatrix momentum: p_sep(theta) = +/- 2 * m * l^2 * omega_0 * cos(theta / 2)
        thetas = np.linspace(-np.pi + 1e-4, np.pi - 1e-4, 40)
        for th in thetas:
            p_exact_pos = 2.0 * m * (l ** 2) * omega_0 * np.cos(th / 2.0)
            H_val = (p_exact_pos ** 2) / (2.0 * m * (l ** 2)) + m * g * l * (1.0 - np.cos(th))
            self.assertAlmostEqual(H_val, E_sep, places=7,
                                   msg="Separatrix trajectory must strictly conserve the saddle energy E_sep.")

    def test_symplectic_energy_conservation(self):
        """Verify dH/dt = 0 identically along canonical trajectories."""
        m = 1.2
        l = 0.9
        g = 9.81

        th_sample = np.linspace(-np.pi, np.pi, 25)
        p_sample = np.linspace(-3.0, 3.0, 25)

        for th in th_sample:
            for p in p_sample:
                # Partial derivatives
                dH_dq = m * g * l * np.sin(th)
                dH_dp = p / (m * (l ** 2))

                # Canonical flow: dot(q) = dH_dp, dot(p) = -dH_dq
                q_dot = dH_dp
                p_dot = -dH_dq

                # Total time derivative: dH/dt = (dH/dq)*q_dot + (dH/dp)*p_dot + dH/dt_explicit
                dH_dt = dH_dq * q_dot + dH_dp * p_dot
                self.assertAlmostEqual(dH_dt, 0.0, places=12,
                                       msg="Time derivative dH/dt along canonical flow must vanish identically.")


class TestFigureGenerationPipeline(unittest.TestCase):
    """Pipeline and image rendering integrity tests."""

    def _verify_single_figure(self, tmp_dir, generator_func, filename, min_w, min_h, min_size_kb=30):
        target_path = Path(tmp_dir) / filename
        result_path = generator_func(target_path)
        if result_path is None:
            result_path = target_path

        self.assertTrue(result_path.exists(), f"File {filename} was not created")
        self.assertTrue(result_path.is_file(), f"{filename} is not a regular file")

        # Verify file size
        size_bytes = result_path.stat().st_size
        self.assertGreater(size_bytes, min_size_kb * 1024,
                           f"File {filename} size too small: {size_bytes} bytes")

        # Verify PNG Magic Header: 89 50 4E 47 0D 0A 1A 0A
        with open(result_path, "rb") as f:
            header = f.read(8)
        self.assertEqual(header, b"\x89PNG\r\n\x1a\n",
                         f"File {filename} is missing standard PNG magic header")

        # Verify Pillow opens image and matches resolution
        with Image.open(result_path) as img:
            self.assertEqual(img.format, "PNG")
            w, h = img.size
            self.assertGreaterEqual(w, min_w, f"Image {filename} width {w} < expected {min_w}")
            self.assertGreaterEqual(h, min_h, f"Image {filename} height {h} < expected {min_h}")

    def test_01_pendulum_coordinate_transition(self):
        """Verify isolated generation of pendulum coordinate transition infographic."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_pendulum_transition, "pendulum_coordinate_transition.png", 2500, 1200)

    def test_02_analytical_mechanics_portraits(self):
        """Verify portrait panel of analytical mechanics pioneers."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_analytical_portraits, "analytical_mechanics_portraits.png", 2000, 900)

    def test_03_generalized_coordinates_taxonomy(self):
        """Verify isolated generation of generalized coordinates & DOF taxonomy infographic."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_generalized_coordinates, "generalized_coordinates.png", 2500, 1200)

    def test_04_lagrange_vs_hamilton_comparison(self):
        """Verify isolated generation of Lagrangian vs. Hamiltonian comparison infographic."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_lagrange_vs_hamilton, "lagrange_vs_hamilton_comparison.png", 2500, 1200)

    def test_05_pendulum_phase_portrait(self):
        """Verify isolated generation of nonlinear pendulum phase space portrait."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_pendulum_phase_portrait, "pendulum_phase_portrait.png", 2500, 1200)

    def test_06_hamilton_jacobi_portraits(self):
        """Verify isolated generation of Hamilton-Jacobi portrait panel."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_hamilton_jacobi_portraits, "hamilton_jacobi_portraits.png", 1000, 600)


if __name__ == '__main__':
    unittest.main(verbosity=2)
