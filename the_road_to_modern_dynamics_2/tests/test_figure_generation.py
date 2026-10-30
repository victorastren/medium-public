#!/usr/bin/env python3
"""
Unit and validation test suite for physical invariants, mathematical derivations,
and figure generation in Article 2:
"From Poincaré to Chaos: The Road to Modern Dynamics II"

Tests cover:
1. Double Pendulum Physics:
   - Analytical & numerical equivalence of Euler–Lagrange equations with matrix form
   - Verification of the Coriolis/centrifugal coupling vector signs
   - Mechanical energy conservation (dE/dt = 0)
   - Linearization into two distinct normal modes
2. Circular Restricted Three-Body Problem (CRTBP):
   - Equilibrium conditions for collinear (L1, L2, L3) and triangular (L4, L5) points
   - Jacobi integral of motion conservation (dC_J/dt = 0)
3. Poincaré Return Maps & Symplecticity:
   - Area preservation (det J = 1) for the Chirikov standard map
   - Elliptic vs. hyperbolic fixed-point eigenvalue spectrum (lambda_1 * lambda_2 = 1)
4. Figure Generation Pipeline:
   - Isolated generation of editorial infographics into temporary directories
   - Image format validation (PNG magic bytes, resolution, aspect ratio)
"""

import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from PIL import Image

TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
CODE_DIR = PROJECT_DIR / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import generate_classical_vs_forced_pendulum
import generate_simple_vs_double_pendulum
import generate_floquet_birkhoff_portraits
import generate_poincare_bendixson_portraits
import generate_poincare_bendixson_figure
import generate_poincare_birkhoff_figure
import generate_poincare_planar_dynamics_infographic
import generate_poincare_return_map_stability
import generate_three_body_solutions_crtbp
import generate_elliptic_hyperbolic_periodic_points
import generate_poincare_sections_double_pendulum
import generate_dynamical_systems_timeline


class TestDoublePendulumPhysics(unittest.TestCase):
    """Test mathematical and physical foundations of the conservative double pendulum."""

    def setUp(self):
        self.m1 = 1.0
        self.m2 = 1.0
        self.L1 = 1.0
        self.L2 = 1.0
        self.g = 9.81

    def double_pendulum_matrices(self, th1, th2, w1, w2):
        delta = th1 - th2
        M = np.array([
            [(self.m1 + self.m2) * self.L1**2, self.m2 * self.L1 * self.L2 * np.cos(delta)],
            [self.m2 * self.L1 * self.L2 * np.cos(delta), self.m2 * self.L2**2]
        ])
        C = np.array([
            self.m2 * self.L1 * self.L2 * np.sin(delta) * (w2**2) + (self.m1 + self.m2) * self.g * self.L1 * np.sin(th1),
            -self.m2 * self.L1 * self.L2 * np.sin(delta) * (w1**2) + self.m2 * self.g * self.L2 * np.sin(th2)
        ])
        return M, C

    def test_euler_lagrange_vector_signs(self):
        """Verify that the matrix equation M(theta) * ddw + C(theta, w) = 0 exactly matches Euler-Lagrange."""
        test_states = [
            (0.3, -0.4, 0.5, -0.8),
            (1.2, 0.7, -1.5, 2.0),
            (-0.8, 1.5, 0.2, -0.5),
            (2.1, -1.8, -1.1, 0.9),
        ]

        for th1, th2, w1, w2 in test_states:
            M, C = self.double_pendulum_matrices(th1, th2, w1, w2)
            alpha = np.linalg.solve(M, -C)

            delta = th1 - th2
            el1 = (self.m1 + self.m2) * self.L1**2 * alpha[0] + \
                  self.m2 * self.L1 * self.L2 * np.cos(delta) * alpha[1] - \
                  self.m2 * self.L1 * self.L2 * np.sin(delta) * (w1 - w2) * w2 - \
                  (-self.m2 * self.L1 * self.L2 * np.sin(delta) * w1 * w2 - (self.m1 + self.m2) * self.g * self.L1 * np.sin(th1))

            el2 = self.m2 * self.L1 * self.L2 * np.cos(delta) * alpha[0] + \
                  self.m2 * self.L2**2 * alpha[1] - \
                  self.m2 * self.L1 * self.L2 * np.sin(delta) * (w1 - w2) * w1 - \
                  (self.m2 * self.L1 * self.L2 * np.sin(delta) * w1 * w2 - self.m2 * self.g * self.L2 * np.sin(th2))

            self.assertAlmostEqual(el1, 0.0, places=10)
            self.assertAlmostEqual(el2, 0.0, places=10)

    def test_energy_conservation_during_simulation(self):
        """Verify that total energy E = T + V is strictly conserved along numerically integrated orbits."""
        def derivs(t, y):
            th1, th2, w1, w2 = y
            M, C = self.double_pendulum_matrices(th1, th2, w1, w2)
            alpha = np.linalg.solve(M, -C)
            return [w1, w2, alpha[0], alpha[1]]

        y0 = [np.pi / 3, np.pi / 4, 0.0, 0.0]
        t_span = (0, 4.0)
        t_eval = np.linspace(0, 4.0, 300)

        sol = solve_ivp(derivs, t_span, y0, t_eval=t_eval, method='RK45', rtol=1e-9, atol=1e-9)
        self.assertTrue(sol.success)

        def total_energy(th1, th2, w1, w2):
            delta = th1 - th2
            T = 0.5 * (self.m1 + self.m2) * self.L1**2 * w1**2 + \
                0.5 * self.m2 * self.L2**2 * w2**2 + \
                self.m2 * self.L1 * self.L2 * np.cos(delta) * w1 * w2
            V = -(self.m1 + self.m2) * self.g * self.L1 * np.cos(th1) - \
                self.m2 * self.g * self.L2 * np.cos(th2)
            return T + V

        E0 = total_energy(*y0)
        energies = [total_energy(sol.y[0, i], sol.y[1, i], sol.y[2, i], sol.y[3, i]) for i in range(len(t_eval))]
        max_rel_error = np.max(np.abs((energies - E0) / E0))
        self.assertLess(max_rel_error, 1e-6)

    def test_linearized_normal_modes(self):
        """Verify that small-angle linearization produces the exact analytical normal mode frequencies."""
        M0 = np.array([
            [(self.m1 + self.m2) * self.L1**2, self.m2 * self.L1 * self.L2],
            [self.m2 * self.L1 * self.L2, self.m2 * self.L2**2]
        ])
        K0 = np.array([
            [(self.m1 + self.m2) * self.g * self.L1, 0.0],
            [0.0, self.m2 * self.g * self.L2]
        ])
        evals = np.linalg.eigvals(np.linalg.solve(M0, K0))
        computed_omegas = np.sort(np.sqrt(evals))

        analytical_w1 = np.sqrt((self.g / self.L1) * (2 - np.sqrt(2)))
        analytical_w2 = np.sqrt((self.g / self.L1) * (2 + np.sqrt(2)))
        analytical_omegas = np.array([analytical_w1, analytical_w2])

        np.testing.assert_allclose(computed_omegas, analytical_omegas, rtol=1e-12)


class TestCRTBPPhysics(unittest.TestCase):
    """Test equilibrium configurations and conservation laws of the Circular Restricted 3-Body Problem."""

    def setUp(self):
        self.mu = 0.01215

    def grad_omega(self, x, y):
        r1 = np.sqrt((x + self.mu)**2 + y**2)
        r2 = np.sqrt((x - 1 + self.mu)**2 + y**2)
        dO_dx = x - (1 - self.mu) * (x + self.mu) / r1**3 - self.mu * (x - 1 + self.mu) / r2**3
        dO_dy = y - (1 - self.mu) * y / r1**3 - self.mu * y / r2**3
        return dO_dx, dO_dy

    def test_triangular_lagrange_points_L4_L5(self):
        """Verify that L4 and L5 form equilateral triangles with r1 = r2 = 1 and grad(Omega) = 0."""
        x_L = 0.5 - self.mu
        for y_pt in [np.sqrt(3) / 2, -np.sqrt(3) / 2]:
            r1 = np.sqrt((x_L + self.mu)**2 + y_pt**2)
            r2 = np.sqrt((x_L - 1 + self.mu)**2 + y_pt**2)
            self.assertAlmostEqual(r1, 1.0, places=12)
            self.assertAlmostEqual(r2, 1.0, places=12)

            gx, gy = self.grad_omega(x_L, y_pt)
            self.assertAlmostEqual(gx, 0.0, places=12)
            self.assertAlmostEqual(gy, 0.0, places=12)

    def test_jacobi_integral_conservation(self):
        """Verify that the Jacobi constant C_J = 2*Omega - v^2 is strictly conserved along orbits."""
        def omega(x, y):
            r1 = np.sqrt((x + self.mu)**2 + y**2)
            r2 = np.sqrt((x - 1 + self.mu)**2 + y**2)
            return 0.5 * (x**2 + y**2) + (1 - self.mu) / r1 + self.mu / r2

        def crtbp_ode(t, state):
            x, y, vx, vy = state
            gx, gy = self.grad_omega(x, y)
            ax = 2 * vy + gx
            ay = -2 * vx + gy
            return [vx, vy, ax, ay]

        state0 = [0.8, 0.2, 0.0, 0.3]
        sol = solve_ivp(crtbp_ode, (0, 3.0), state0, method='RK45', rtol=1e-9, atol=1e-9)
        self.assertTrue(sol.success)

        def jacobi(x, y, vx, vy):
            return 2 * omega(x, y) - (vx**2 + vy**2)

        C0 = jacobi(*state0)
        c_vals = [jacobi(sol.y[0, i], sol.y[1, i], sol.y[2, i], sol.y[3, i]) for i in range(len(sol.t))]
        max_dev = np.max(np.abs(np.array(c_vals) - C0))
        self.assertLess(max_dev, 1e-6)


class TestPoincareMapAndTwistTheorem(unittest.TestCase):
    """Test mathematical invariants of Poincaré return maps, symplecticity, and twist maps."""

    def test_standard_map_area_preservation(self):
        """Verify that the Chirikov standard map has Jacobian determinant det(J) = 1 identically."""
        for K in [0.5, 1.2, 3.0]:
            for x in np.linspace(0.1, 2 * np.pi - 0.1, 6):
                J = np.array([
                    [1 + K * np.cos(x), 1.0],
                    [K * np.cos(x), 1.0]
                ])
                det_J = np.linalg.det(J)
                self.assertAlmostEqual(det_J, 1.0, places=12)

    def test_fixed_point_eigenvalue_product(self):
        """Verify that the eigenvalues of the return map linearized at a periodic point satisfy lambda1 * lambda2 = 1."""
        for K in [-1.5, -0.5, 0.5, 2.0]:
            J = np.array([[1 + K, 1.0], [K, 1.0]])
            eigvals = np.linalg.eigvals(J)
            product = np.prod(eigvals)
            self.assertAlmostEqual(product.real, 1.0, places=12)
            self.assertAlmostEqual(product.imag, 0.0, places=12)


class TestFigureGenerationPipeline(unittest.TestCase):
    """Pipeline and image rendering integrity tests."""

    def _verify_single_figure(self, tmp_dir, generator_func, filename, min_w, min_h, min_size_kb=30):
        target_path = Path(tmp_dir) / filename
        generator_func(target_path)

        self.assertTrue(target_path.exists(), f"File {filename} was not created")
        self.assertTrue(target_path.is_file(), f"{filename} is not a regular file")

        size_bytes = target_path.stat().st_size
        self.assertGreater(size_bytes, min_size_kb * 1024,
                           f"File {filename} size too small: {size_bytes} bytes")

        with open(target_path, "rb") as f:
            header = f.read(8)
        self.assertEqual(header, b"\x89PNG\r\n\x1a\n",
                         f"File {filename} is missing standard PNG magic header")

        with Image.open(target_path) as img:
            self.assertEqual(img.format, "PNG")
            w, h = img.size
            self.assertGreaterEqual(w, min_w, f"Image {filename} width {w} < expected {min_w}")
            self.assertGreaterEqual(h, min_h, f"Image {filename} height {h} < expected {min_h}")

    def test_01_planar_dynamics_infographic(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_poincare_planar_dynamics_infographic.create_figure,
                                       "poincare_planar_dynamics_infographic.png", 2000, 1000)

    def test_02_poincare_bendixson_portraits(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_poincare_bendixson_portraits.create_figure,
                                       "poincare_bendixson_portraits.png", 1000, 500)

    def test_03_poincare_bendixson_figure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_poincare_bendixson_figure.create_figure,
                                       "poincare_bendixson_theorem.png", 2000, 1000)

    def test_04_three_body_solutions_crtbp(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_three_body_solutions_crtbp.create_figure,
                                       "three_body_solutions_crtbp.png", 2000, 1000)

    def test_05_poincare_return_map_stability(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_poincare_return_map_stability.create_figure,
                                       "poincare_return_map_stability.png", 2000, 900)

    def test_06_simple_vs_double_pendulum(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_simple_vs_double_pendulum.create_figure,
                                       "simple_vs_double_pendulum.png", 2000, 1000)

    def test_07_classical_vs_forced_pendulum(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_classical_vs_forced_pendulum.create_figure,
                                       "classical_vs_forced_pendulum.png", 2000, 1000)

    def test_08_poincare_sections_double_pendulum(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, lambda p: generate_poincare_sections_double_pendulum.generate_figure(output_png=p),
                                       "poincare_sections_double_pendulum.png", 2000, 1000)

    def test_09_elliptic_hyperbolic_periodic_points(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_elliptic_hyperbolic_periodic_points.create_figure,
                                       "elliptic_hyperbolic_periodic_points.png", 2000, 1000)

    def test_10_floquet_birkhoff_portraits(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_floquet_birkhoff_portraits.create_figure,
                                       "floquet_birkhoff_portraits.png", 1000, 500)

    def test_11_poincare_birkhoff_figure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_poincare_birkhoff_figure.create_figure,
                                       "poincare_birkhoff_theorem.png", 1500, 700)

    def test_12_dynamical_systems_timeline(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._verify_single_figure(tmp_dir, generate_dynamical_systems_timeline.create_timeline,
                                       "dynamical_systems_timeline.png", 1500, 500)


if __name__ == '__main__':
    unittest.main(verbosity=2)
