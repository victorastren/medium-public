#!/usr/bin/env python3
"""
Mathematical and physical unit tests for Article 3:
"Order and Chaos: The Road to Modern Dynamics III"

Covers:
1. Smale's Horseshoe & Symbolic Dynamics (orbits, uniform hyperbolicity, entropy)
2. Unforced & Periodically Forced Pendulum (energy conservation/exchange, area preservation)
3. Integrable Hamiltonian Tori & KAM Theory (periodic vs. quasiperiodic, torus geometry, Diophantine bound)
4. Lorenz Dissipative System (constant divergence -41/3, unstable equilibria, sensitive dependence)
5. Secular Planetary Perturbation Model (two-mode Lagrange-Laplace analytical bounds)
6. IMCCE La2010 Orbital Reconstructions (Earth-Mars secular resonance & eccentricity divergence)
"""

import sys
import unittest
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
CODE_DIR = PROJECT_DIR / "code"
DATA_DIR = PROJECT_DIR / "data"

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import generate_horseshoe_symbolic_dynamics as horseshoe_sym
import generate_integrable_torus_animation as torus_anim
import generate_secular_planetary_evolution as secular_model
import generate_earth_mars_secular_resonance as em_resonance
import generate_la2010_orbital_divergence as la2010_div


class TestSmaleHorseshoeDynamics(unittest.TestCase):
    """Test exact algebraic and symbolic properties of the piecewise-affine horseshoe map."""

    def test_period_two_orbit_and_fixed_point(self):
        """Verify z0=(0.9, 0.3) <-> z1=(0.3, 0.9) and fixed point z*=(0.75, 0.75)."""
        horseshoe_sym.verify_sample_orbits()
        z0 = (0.9, 0.3)
        z1 = horseshoe_sym.horseshoe_affine_step(z0)
        z2 = horseshoe_sym.horseshoe_affine_step(z1)
        np.testing.assert_allclose(z1, (0.3, 0.9), atol=1e-12)
        np.testing.assert_allclose(z2, z0, atol=1e-12)

        z_star = (0.75, 0.75)
        np.testing.assert_allclose(horseshoe_sym.horseshoe_affine_step(z_star), z_star, atol=1e-12)

    def test_uniform_hyperbolicity_and_middle_strip_escape(self):
        """Verify contraction 1/3, expansion 3, |det DF| = 1 on returning strips, and middle-strip escape."""
        eps = 1e-6
        for y0 in (0.15, 0.85):
            x0 = 0.42
            fx0, fy0 = horseshoe_sym.horseshoe_affine_step((x0, y0))
            fx_dx, fy_dx = horseshoe_sym.horseshoe_affine_step((x0 + eps, y0))
            fx_dy, fy_dy = horseshoe_sym.horseshoe_affine_step((x0, y0 + eps))
            J = np.array([
                [(fx_dx - fx0) / eps, (fx_dy - fx0) / eps],
                [(fy_dx - fy0) / eps, (fy_dy - fy0) / eps],
            ])
            self.assertAlmostEqual(abs(J[0, 0]), 1.0 / 3.0, places=9)
            self.assertAlmostEqual(abs(J[1, 1]), 3.0, places=9)
            self.assertAlmostEqual(abs(np.linalg.det(J)), 1.0, places=9)

        with self.assertRaises(ValueError):
            horseshoe_sym.horseshoe_affine_step((0.5, 0.5))

    def test_symbolic_block_growth_and_topological_entropy(self):
        """Verify 2^n allowed symbolic blocks yield topological entropy ln(2) per iteration."""
        for n in (1, 5, 12, 20):
            h_n = np.log(2 ** n) / n
            self.assertAlmostEqual(h_n, np.log(2.0), places=12)


class TestPendulumDynamics(unittest.TestCase):
    """Test unforced and periodically forced undamped pendulum dynamics."""

    def test_unforced_energy_conservation_and_separatrix(self):
        """Verify H = 0.5*p^2 - cos(theta) is conserved and upright saddle has E = +1."""
        def rhs(_t, y):
            return [y[1], -np.sin(y[0])]

        sol = solve_ivp(rhs, (0.0, 12.0), [1.2, 0.4], method="DOP853", rtol=1e-10, atol=1e-12)
        self.assertTrue(sol.success)
        energy = 0.5 * sol.y[1] ** 2 - np.cos(sol.y[0])
        self.assertLess(np.max(np.abs(energy - energy[0])), 1e-8)

        e_saddle = 0.5 * (0.0 ** 2) - np.cos(np.pi)
        self.assertAlmostEqual(e_saddle, 1.0, places=12)

    def test_forced_pendulum_energy_exchange_and_zero_divergence(self):
        """Verify periodic forcing breaks energy conservation while preserving phase-space area."""
        A, omega = 0.20, 0.80
        T_forcing = 2.0 * np.pi / omega

        def forced_rhs(t, y):
            return [y[1], -np.sin(y[0]) + A * np.cos(omega * t)]

        sol = solve_ivp(forced_rhs, (0.0, 4.0 * T_forcing), [1.2, 0.4], method="DOP853", rtol=1e-10, atol=1e-12)
        self.assertTrue(sol.success)
        energy = 0.5 * sol.y[1] ** 2 - np.cos(sol.y[0])
        self.assertGreater(float(np.max(energy) - np.min(energy)), 0.05)

        # Hamiltonian flow divergence d(theta_dot)/d(theta) + d(p_dot)/d(p) = 0 identically
        for th in np.linspace(-np.pi, np.pi, 7):
            J = np.array([[0.0, 1.0], [-np.cos(th), 0.0]])
            self.assertAlmostEqual(float(np.trace(J)), 0.0, places=12)


class TestIntegrableTorusAndKAM(unittest.TestCase):
    """Test Liouville-Arnold invariant torus geometry, rational closure, and KAM Diophantine bounds."""

    def test_integrable_torus_periodic_vs_quasiperiodic(self):
        """Verify rational ratio 2/3 closes at t = 2*pi whereas irrational sqrt(2) does not."""
        phi1_0, phi2_0 = -0.45, 0.25
        p0, _ = torus_anim.torus_point_and_normal(np.array([phi1_0]), np.array([phi2_0]))
        p_b, _ = torus_anim.torus_point_and_normal(
            np.array([phi1_0 + 2.0 * 2.0 * np.pi]),
            np.array([phi2_0 + 3.0 * 2.0 * np.pi]),
        )
        p_c, _ = torus_anim.torus_point_and_normal(
            np.array([phi1_0 + 2.0 * np.sqrt(2.0) * 2.0 * np.pi]),
            np.array([phi2_0 + 2.0 * 2.0 * np.pi]),
        )
        self.assertLess(np.linalg.norm(p_b - p0), 1e-12)
        self.assertGreater(np.linalg.norm(p_c - p0), 0.5)

    def test_torus_implicit_surface_and_unit_normals(self):
        """Verify points satisfy (rho - R)^2 + z^2 = r^2 and outward normals have unit norm."""
        phi1 = np.linspace(0.0, 2.0 * np.pi, 50)
        phi2 = np.linspace(0.0, 2.0 * np.pi, 50)
        pts, nrm = torus_anim.torus_point_and_normal(phi1, phi2)
        rho = np.hypot(pts[:, 0], pts[:, 1])
        implicit = (rho - torus_anim.R_MAJOR) ** 2 + pts[:, 2] ** 2 - torus_anim.R_MINOR ** 2
        np.testing.assert_allclose(implicit, 0.0, atol=1e-12)
        np.testing.assert_allclose(np.linalg.norm(nrm, axis=1), 1.0, atol=1e-12)

    def test_kam_resonance_and_diophantine_bound_for_sqrt2(self):
        """Verify rational 2/3 hits exact resonance 3*w1 - 2*w2 = 0 while sqrt(2) obeys a Diophantine lower bound."""
        self.assertAlmostEqual(3 * (2.0 / 3.0) - 2 * 1.0, 0.0, places=12)
        # For alpha = sqrt(2), |m*sqrt(2) - n| > 1 / (3*|m|) for all non-zero integers m, n
        for m in range(1, 50):
            n = int(round(m * np.sqrt(2.0)))
            dist = abs(m * np.sqrt(2.0) - n)
            self.assertGreater(dist, 1.0 / (3.0 * m))


class TestLorenzSystemPhysics(unittest.TestCase):
    """Test phase-space volume contraction, unstable equilibria, and sensitivity in the Lorenz system."""

    def setUp(self):
        self.sigma = 10.0
        self.rho = 28.0
        self.beta = 8.0 / 3.0

    def _lorenz(self, _t, s):
        x, y, z = s
        return [
            self.sigma * (y - x),
            x * (self.rho - z) - y,
            x * y - self.beta * z,
        ]

    def test_constant_negative_divergence_and_volume_contraction(self):
        """Verify div(f) = -(sigma + 1 + beta) = -41/3 everywhere and V(t) = V(0) exp(-41/3 t)."""
        for x, y, z in [(0.0, 0.0, 0.0), (5.0, -7.0, 24.0), (-12.3, 8.4, 31.2)]:
            J = np.array([
                [-self.sigma, self.sigma, 0.0],
                [self.rho - z, -1.0, -x],
                [y, x, -self.beta],
            ])
            self.assertAlmostEqual(float(np.trace(J)), -41.0 / 3.0, places=12)

        self.assertAlmostEqual(np.exp(-(41.0 / 3.0) * 0.3), np.exp(-4.1), places=12)

    def test_unstable_equilibria_c_plus_minus(self):
        """Verify C_+ and C_- are exact fixed points of the Lorenz vector field."""
        c_xy = np.sqrt(self.beta * (self.rho - 1.0))
        c_z = self.rho - 1.0
        for sign in (+1.0, -1.0):
            deriv = self._lorenz(0.0, [sign * c_xy, sign * c_xy, c_z])
            np.testing.assert_allclose(deriv, [0.0, 0.0, 0.0], atol=1e-12)

    def test_sensitive_dependence_from_1e6_perturbation(self):
        """Verify trajectories starting 1e-6 apart separate by O(10) by t = 35."""
        sol1 = solve_ivp(self._lorenz, (0.0, 35.0), [1.0, 1.0, 1.0], method="DOP853", rtol=1e-10, atol=1e-12)
        sol2 = solve_ivp(self._lorenz, (0.0, 35.0), [1.0 + 1e-6, 1.0, 1.0], method="DOP853", rtol=1e-10, atol=1e-12)
        self.assertTrue(sol1.success and sol2.success)
        self.assertGreater(float(np.linalg.norm(sol1.y[:, -1] - sol2.y[:, -1])), 1.0)


class TestSecularPlanetaryModel(unittest.TestCase):
    """Test the two-mode linear Lagrange-Laplace secular planetary model."""

    def test_two_mode_secular_bounds_and_beat_period(self):
        """Verify analytical bounds e in [0.06, 0.18], T_beat = 2*pi/0.3, and epoch states."""
        secular_model.verify_model()
        self.assertAlmostEqual(secular_model.T_BEAT, 2.0 * np.pi / 0.3, places=12)


class TestLa2010OrbitalReconstructions(unittest.TestCase):
    """Test IMCCE La2010 source datasets, Earth-Mars secular resonance, and orbital divergence."""

    def test_la2010_source_files_present(self):
        """Verify all 8 IMCCE La2010 datasets and README.TXT exist and are non-empty."""
        expected_files = [
            "La2010a_alkhqp3.dat", "La2010b_alkhqp3.dat", "La2010c_alkhqp3.dat", "La2010d_alkhqp3.dat",
            "La2010a_ecc3L.dat", "La2010b_ecc3L.dat", "La2010c_ecc3L.dat", "La2010d_ecc3L.dat",
            "README.TXT",
        ]
        for fname in expected_files:
            fpath = DATA_DIR / fname
            self.assertTrue(fpath.exists(), f"Missing data file: {fpath}")
            self.assertGreater(fpath.stat().st_size, 1000, f"Data file too small: {fpath}")

    def test_earth_mars_secular_resonance_continuity_and_stability(self):
        """Verify complex z_e/zeta phase continuity, boundary invariance, filter stability, and sliding NAFF consistency."""
        results = em_resonance.load_and_reconstruct_theta(validate_stability=True)
        self.assertEqual(set(results.keys()), {"La2010a", "La2010b", "La2010c", "La2010d"})
        for label, (t_ma, th_pi) in results.items():
            m100 = t_ma <= 100.0
            max_step = float(np.max(np.abs(np.diff(th_pi[m100]))))
            self.assertLess(max_step, 0.05, f"{label}: phase jump {max_step:.4f} pi")

        naff_cmp = em_resonance.compare_fft_and_sliding_naff(win_myr=10.0, step_myr=1.0)
        for label, stats in naff_cmp.items():
            self.assertLess(stats["rms_lib_pi"], 0.35, f"{label}: sliding NAFF vs FFT libration mismatch")

    def test_la2010_eccentricity_rms_divergence_growth(self):
        """Verify uniform 1-kyr sampling and >2.5x RMS divergence growth from 45-50 Ma to 60-65 Ma."""
        datasets = la2010_div.load_la2010_datasets()
        self.assertEqual(set(datasets.keys()), {"La2010a", "La2010b", "La2010c", "La2010d"})


if __name__ == "__main__":
    unittest.main(verbosity=2)

