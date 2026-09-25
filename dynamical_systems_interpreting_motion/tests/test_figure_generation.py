#!/usr/bin/env python3
"""
Unit test suite for Dynamical Systems: Interpreting Motion figure generation and physics.
Compatible with both pytest and Python standard library unittest:
    python3 -m unittest tests/test_figure_generation.py
    python3 -m unittest discover tests
    pytest tests/ -v

Validates:
1. Linearized stability and Jacobian eigenvalue analysis for fixed points (center, saddle, node, spiral).
2. Hamiltonian energy conservation, libration turning points, separatrix orbit, and rotation regime.
3. Isolated generation of all 5 publication infographics to verify PNG format,
   non-zero file size, valid magic header, and proper image dimensions.
"""

import sys
import tempfile
import unittest
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import numpy as np
from PIL import Image

# Ensure code directory is in sys.path
TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
CODE_DIR = PROJECT_DIR / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from generate_local_stability_classification import create_figure as generate_stability_classification
from generate_phase_portrait import create_figure as generate_phase_portrait
from generate_state_space_transition import create_figure as generate_state_space_transition
from generate_dissipation_phase_portrait import create_figure as generate_dissipation_phase_portrait
from generate_poincare_return_map import create_figure as generate_poincare_return_map


class TestDynamicalSystemsPhysicsAndFigures(unittest.TestCase):
    """Test suite for dynamical systems theory, nonlinear pendulum physics, and figure rendering."""

    def test_fixed_point_jacobian_and_eigenvalues(self):
        """Verify Jacobian matrices and eigenvalues for downward (center) and inverted (saddle) fixed points."""
        g = 9.81
        ell = 1.0

        # Downward equilibrium (0, 0): J = [[0, 1], [-g/l, 0]]
        J_down = np.array([[0.0, 1.0], [-g / ell, 0.0]])
        eigvals_down = np.linalg.eigvals(J_down)
        self.assertAlmostEqual(eigvals_down[0].real, 0.0, places=7, msg="Center eigenvalues must have zero real part.")
        self.assertAlmostEqual(eigvals_down[1].real, 0.0, places=7, msg="Center eigenvalues must have zero real part.")
        self.assertAlmostEqual(abs(eigvals_down[0].imag), np.sqrt(g / ell), places=5)
        self.assertAlmostEqual(abs(eigvals_down[1].imag), np.sqrt(g / ell), places=5)

        # Inverted equilibrium (pi, 0): J = [[0, 1], [g/l, 0]]
        J_up = np.array([[0.0, 1.0], [g / ell, 0.0]])
        eigvals_up = np.linalg.eigvals(J_up)
        self.assertAlmostEqual(eigvals_up[0].imag, 0.0, places=7, msg="Saddle eigenvalues must be purely real.")
        self.assertAlmostEqual(eigvals_up[1].imag, 0.0, places=7, msg="Saddle eigenvalues must be purely real.")
        self.assertTrue((eigvals_up[0] > 0 and eigvals_up[1] < 0) or (eigvals_up[0] < 0 and eigvals_up[1] > 0),
                        "Saddle must have one positive and one negative eigenvalue.")
        self.assertAlmostEqual(abs(eigvals_up[0]), np.sqrt(g / ell), places=5)

    def test_2d_linear_stability_classification(self):
        """Verify 2D Jacobian eigenvalue signatures across the four canonical portraits in the article."""
        # 1. Stable node (Panel A): lambda1, lambda2 < 0 (real)
        J_node = np.array([[-2.0, 0.0], [0.0, -1.0]])
        eigs_node = np.linalg.eigvals(J_node)
        self.assertTrue(all(e.real < 0 and e.imag == 0 for e in eigs_node), "Stable node must have real negative eigenvalues.")

        # 2. Saddle (Panel B): lambda1 < 0 < lambda2 (real)
        J_saddle = np.array([[1.5, 0.0], [0.0, -1.5]])
        eigs_saddle = np.linalg.eigvals(J_saddle)
        self.assertTrue(min(eigs_saddle) < 0 < max(eigs_saddle), "Saddle must have one positive and one negative real eigenvalue.")

        # 3. Center (Panel C): purely imaginary +/- i*beta
        J_center = np.array([[0.0, 2.0], [-2.0, 0.0]])
        eigs_center = np.linalg.eigvals(J_center)
        self.assertAlmostEqual(eigs_center[0].real, 0.0, places=7)
        self.assertNotEqual(eigs_center[0].imag, 0.0)

        # 4. Stable spiral (Panel D): alpha +/- i*beta with alpha < 0
        J_spiral = np.array([[-0.5, 2.0], [-2.0, -0.5]])
        eigs_spiral = np.linalg.eigvals(J_spiral)
        self.assertLess(eigs_spiral[0].real, 0.0, "Stable spiral must have negative real part.")
        self.assertNotEqual(eigs_spiral[0].imag, 0.0, "Stable spiral must have non-zero imaginary part.")

    def test_hamiltonian_energy_and_separatrix(self):
        """Verify dimensionless energy e(theta, omega) = 1/2 omega^2 + (1 - cos(theta)), separatrix, and regimes."""
        def energy(th, om):
            return 0.5 * (om ** 2) + (1.0 - np.cos(th))

        # Downward equilibrium ground energy: e = 0
        self.assertAlmostEqual(energy(0.0, 0.0), 0.0, places=7)

        # Inverted equilibrium separatrix energy: e_sep = 2
        e_sep = energy(np.pi, 0.0)
        self.assertAlmostEqual(e_sep, 2.0, places=7)

        # Separatrix analytical velocity: omega_sep = 2 * cos(theta / 2)
        thetas = np.linspace(-np.pi + 1e-4, np.pi - 1e-4, 50)
        for th in thetas:
            om_exact = 2.0 * np.cos(th / 2.0)
            self.assertAlmostEqual(energy(th, om_exact), e_sep, places=7, msg="Separatrix trajectory must conserve e = 2.")

        # Libration regime (e < 2): turning point theta_max where omega = 0
        for e_val in [0.25, 0.65, 1.15, 1.65]:
            th_max = np.arccos(1.0 - e_val)
            self.assertAlmostEqual(energy(th_max, 0.0), e_val, places=7)
            om_mid = np.sqrt(2.0 * (e_val - (1.0 - np.cos(0.0))))
            self.assertGreater(om_mid, 0.0)

        # Rotation regime (e > 2): velocity never vanishes, minimum at theta = pi
        for e_rot in [2.25, 2.90, 3.85]:
            om_min = np.sqrt(2.0 * (e_rot - (1.0 - np.cos(np.pi))))
            self.assertGreater(om_min, 0.0, msg="Rotational regime angular velocity must remain strictly positive.")
            self.assertAlmostEqual(energy(np.pi, om_min), e_rot, places=7)

    def test_vector_field_energy_conservation(self):
        """Verify dE/dt = 0 along the nonlinear vector field dot(theta) = omega, dot(omega) = -sin(theta)."""
        theta_grid = np.linspace(-2 * np.pi, 2 * np.pi, 20)
        omega_grid = np.linspace(-3.0, 3.0, 20)

        for th in theta_grid:
            for om in omega_grid:
                d_theta = om
                d_omega = -np.sin(th)
                dE_dt = om * d_omega + np.sin(th) * d_theta
                self.assertAlmostEqual(dE_dt, 0.0, places=10, msg="Total energy derivative along flow must be exactly zero.")

    def _verify_single_figure(self, tmp_dir, generator_func, filename, min_w, min_h, min_size_kb=40):
        target_path = Path(tmp_dir) / filename
        result_path = generator_func(target_path)
        if result_path is None:
            result_path = target_path

        self.assertTrue(result_path.exists(), f"File {filename} was not created")
        self.assertTrue(result_path.is_file(), f"{filename} is not a regular file")

        # File size check
        size_bytes = result_path.stat().st_size
        self.assertGreater(size_bytes, min_size_kb * 1024, f"File {filename} size too small: {size_bytes} bytes")

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

    def test_damped_pendulum_stability_and_dissipation(self):
        """Verify damped pendulum Jacobian, stable spiral condition, and non-positive energy derivative."""
        g = 9.81
        ell = 1.0
        gamma = 0.35  # Weak damping parameter

        J_damped = np.array([[0.0, 1.0], [-g / ell, -gamma]])
        tr_damped = np.trace(J_damped)
        det_damped = np.linalg.det(J_damped)
        eigvals = np.linalg.eigvals(J_damped)

        self.assertAlmostEqual(tr_damped, -gamma, places=7, msg="Damped Jacobian trace must be -gamma.")
        self.assertAlmostEqual(det_damped, g / ell, places=7, msg="Damped Jacobian determinant must be g/ell.")
        self.assertLess(tr_damped ** 2 - 4 * det_damped, 0.0, msg="Weak damping condition gamma^2 < 4g/l must hold.")
        self.assertAlmostEqual(eigvals[0].real, -gamma / 2.0, places=7, msg="Eigenvalues real part must be -gamma/2 < 0.")
        self.assertNotEqual(eigvals[0].imag, 0.0, msg="Eigenvalues must have non-zero imaginary part (spiral).")

        m = 1.0
        for om in [0.0, 0.5, 1.2, -2.1]:
            dE_dt = -gamma * m * (ell ** 2) * (om ** 2)
            self.assertLessEqual(dE_dt, 0.0, msg="Dissipative rate dE/dt must be non-positive.")
            if om != 0:
                self.assertLess(dE_dt, 0.0, msg="dE/dt must be strictly negative when moving.")

    def test_01_state_space_transition_generation(self):
        """Verify isolated generation of physical-to-state-space transition infographic."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_state_space_transition, "state_space_transition.png", 2500, 900)

    def test_02_pendulum_phase_portrait_generation(self):
        """Verify isolated generation of nonlinear pendulum phase portrait infographic."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_phase_portrait, "pendulum_phase_portrait.png", 2500, 1000)

    def test_03_local_stability_classification_generation(self):
        """Verify isolated generation of local stability 4-panel classification infographic."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_stability_classification, "local_stability_classification.png", 2000, 2000)

    def test_04_dissipation_phase_portrait_generation(self):
        """Verify isolated generation of 2-panel undamped vs damped phase portrait infographic."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_dissipation_phase_portrait, "dissipation_phase_portrait.png", 2500, 1000)

    def test_05_poincare_return_map_generation(self):
        """Verify isolated generation of Poincaré return map 2-panel infographic."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_poincare_return_map, "poincare_return_map.png", 2500, 1200)


if __name__ == '__main__':
    unittest.main(verbosity=2)
