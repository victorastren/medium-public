#!/usr/bin/env python3
"""
Unit and validation test suite for physical invariants, mathematical derivations,
and scientific figure generation in:
"The Golden Age of Black Hole Physics (1963–1974)"

Tests cover:
1. Kerr Spacetime Geometry & Dynamics:
   - Event horizon radii (r_+, r_-) and extremal Kerr limit (a -> M)
   - Ergosphere boundary r_E(theta) enclosing the outer event horizon
   - Horizon surface area A = 4 * pi * (r_+^2 + a^2) and First Law consistency
   - Oppenheimer-Snyder proper-time cycloid vs. Schwarzschild coordinate-time collapse
   - Optical congruence deformation matrices (expansion, shear, twist, shear-free)
   - Geodesic integrability, Schwarzschild periapsis advance, Kerr nodal precession
   - Boyer-Lindquist / oblate spheroidal coordinate mappings and ergosurface
   - Kerr (2,2,0) quasinormal ringdown parameters and envelope bounds
   - Penrose process 4-momentum conservation, future-directedness, and radial potential
2. Black-Hole Thermodynamics:
   - Bekenstein Generalized Second Law animation state machine
   - Hawking temperature inverse-mass scaling and Bekenstein-Hawking entropy
3. Asset Integrity & Isolated Figure Generation:
   - Presence and validity of all 23 scientific figure and animation files in images/
   - Presence and validity of rendered display-math equations in images/math/
   - Isolated execution of static figure and poster generators into a temp directory
"""

import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
CODE_DIR = PROJECT_DIR / "code"
IMAGES_DIR = PROJECT_DIR / "images"

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import generate_bekenstein_gsl
import generate_black_hole_perturbations_ringdown
import generate_boyer_lindquist_coordinates
import generate_from_curvature_to_kerr_solution
import generate_geodesic_orbits_schwarzschild_kerr
import generate_hawking_area_theorem
import generate_hawking_radiation_collapse_spectrum
import generate_kerr_black_hole_anatomy
import generate_lense_thirring_frame_dragging
import generate_oppenheimer_snyder_collapse
import generate_penrose_process


class TestKerrSpacetimeGeometry(unittest.TestCase):
    """Test geometric invariants and horizon structures of the Kerr solution."""

    def test_kerr_horizon_radii(self):
        """Verify outer (r_+) and inner (r_-) horizon radii for sub-extremal and extremal spin."""
        M = 1.0

        # Sub-extremal case: a = 0.6 M
        a = 0.6
        delta_root = math.sqrt(M**2 - a**2)
        r_plus = M + delta_root
        r_minus = M - delta_root

        self.assertAlmostEqual(r_plus, 1.8, places=7)
        self.assertAlmostEqual(r_minus, 0.2, places=7)
        self.assertGreater(r_plus, r_minus)

        # Extremal Kerr limit: a = M
        a_ext = 1.0
        r_plus_ext = M + math.sqrt(M**2 - a_ext**2)
        r_minus_ext = M - math.sqrt(M**2 - a_ext**2)
        self.assertAlmostEqual(r_plus_ext, M, places=7)
        self.assertAlmostEqual(r_minus_ext, M, places=7)

    def test_ergosphere_encloses_outer_horizon(self):
        """Verify the ergosphere r_E(theta) >= r_+ for all polar angles theta."""
        M = 1.0
        a = 0.8
        r_plus = M + math.sqrt(M**2 - a**2)

        for theta_deg in range(0, 181, 15):
            theta = math.radians(theta_deg)
            r_E = M + math.sqrt(M**2 - a**2 * (math.cos(theta) ** 2))
            self.assertGreaterEqual(r_E, r_plus - 1e-9)

        # At the equator (theta = pi/2), r_E = 2M (Schwarzschild horizon radius)
        r_E_equator = M + math.sqrt(M**2 - a**2 * (math.cos(math.pi / 2) ** 2))
        self.assertAlmostEqual(r_E_equator, 2.0 * M, places=7)

        # At the poles (theta = 0, pi), r_E touches the outer horizon r_+
        r_E_pole = M + math.sqrt(M**2 - a**2 * (math.cos(0.0) ** 2))
        self.assertAlmostEqual(r_E_pole, r_plus, places=7)

    def test_horizon_area_and_first_law(self):
        """Verify Kerr horizon area and differential First Law of Mechanics."""
        M = 1.0
        a = 0.5
        J = a * M
        r_plus = M + math.sqrt(M**2 - a**2)
        r_minus = M - math.sqrt(M**2 - a**2)

        area = 4.0 * math.pi * (r_plus**2 + a**2)
        kappa = (r_plus - r_minus) / (2.0 * (r_plus**2 + a**2))

        # Numerical perturbation: increment M slightly at constant J
        dM = 1e-6
        M_new = M + dM
        a_new = J / M_new
        r_plus_new = M_new + math.sqrt(M_new**2 - a_new**2)
        area_new = 4.0 * math.pi * (r_plus_new**2 + a_new**2)
        dA = area_new - area

        # At constant J (dJ = 0): dM should equal (kappa / (8 * pi)) * dA
        dM_predicted = (kappa / (8.0 * math.pi)) * dA
        self.assertAlmostEqual(dM, dM_predicted, places=6)

    def test_kerr_quasinormal_ringdown_parameters(self):
        """Verify Kerr (2,2,0) QNM period, decay time, and envelope bounds for a/m = 0.8."""
        qnm_mod = generate_black_hole_perturbations_ringdown

        self.assertAlmostEqual(qnm_mod.OMEGA_R, 0.5855, places=4)
        self.assertAlmostEqual(qnm_mod.GAMMA_DECAY, 0.0757, places=4)
        self.assertAlmostEqual(qnm_mod.T_PERIOD, 10.73, places=2)
        self.assertAlmostEqual(qnm_mod.TAU_DECAY, 13.21, places=2)

        t_hat, strain, env_upper, env_lower = qnm_mod.compute_ringdown_waveform(t_hat_max=60.0, n_pts=500)
        self.assertEqual(len(t_hat), 500)
        self.assertAlmostEqual(float(strain[0]), 1.0, places=7)
        for s_val, u_val, l_val in zip(strain, env_upper, env_lower):
            self.assertLessEqual(s_val, u_val + 1e-12)
            self.assertGreaterEqual(s_val, l_val - 1e-12)

    def test_penrose_process_conservation_and_geodesics(self):
        """Verify 4-momentum conservation, mass-shell, future-directedness, and escape/capture for Penrose split."""
        d = generate_penrose_process.precompute_penrose_geodesics()
        m, a, r0 = d["m"], d["a"], d["r0"]
        self.assertGreater(r0, d["r_plus"])
        self.assertLess(r0, d["r_erg"])

        # 1. Exact conservation of E and L_z
        self.assertAlmostEqual(d["E0"], d["E1"] + d["E2"], places=12)
        self.assertAlmostEqual(d["Lz0"], d["Lz1"] + d["Lz2"], places=12)

        # 2. Future-directed local energy and timelike mass-shell
        for k in ("0", "1", "2"):
            self.assertGreater(d[f"Eloc{k}"], 0.0)
            self.assertGreater(d[f"mu{k}"], 0.0)

        # 3. Captured fragment: E_1 < 0, L_{z,1} < 0, horizon-crossing condition E_1 - Omega_H L_{z,1} > 0
        self.assertLess(d["E1"], 0.0)
        self.assertLess(d["Lz1"], 0.0)
        self.assertGreater(d["E1"] - d["Omega_H"] * d["Lz1"], 0.0)

        # 4. Escaping fragment: E_2 > E_0 and E_2 > mu_2, with R_0(r) > 0 and R_2(r) > 0 out to r = 100m
        self.assertGreater(d["E2"], d["E0"])
        self.assertGreater(d["E2"], d["mu2"])
        r_ext = np.linspace(r0, 100.0, 2000)
        D_ext = r_ext**2 - 2.0 * m * r_ext + a**2
        for mu, E, Lz in [(d["mu0"], d["E0"], d["Lz0"]), (d["mu2"], d["E2"], d["Lz2"])]:
            R_val = (E * (r_ext**2 + a**2) - a * Lz) ** 2 - D_ext * (mu**2 * r_ext**2 + (Lz - a * E) ** 2)
            self.assertGreater(float(np.min(R_val)), 0.0)

        # 5. Captured fragment plunges across r_+ = 1.6m with R_1(r) > 0 on [r_+, r_0]
        r_cap = np.linspace(d["r_plus"], r0, 500)
        D_cap = r_cap**2 - 2.0 * m * r_cap + a**2
        R1_cap = (d["E1"] * (r_cap**2 + a**2) - a * d["Lz1"]) ** 2 - D_cap * (
            d["mu1"] ** 2 * r_cap**2 + (d["Lz1"] - a * d["E1"]) ** 2
        )
        self.assertGreater(float(np.min(R1_cap)), 0.0)


class TestCollapseAndKerrDynamics(unittest.TestCase):
    """Test collapse trajectories, Petrov/optical models, Kerr orbits, and coordinate geometry."""

    def test_oppenheimer_snyder_trajectories(self):
        """Verify proper-time horizon crossing and coordinate-time asymptotic freeze."""
        tau, y_tau, tau_h, tau_sing, t, y_t = generate_oppenheimer_snyder_collapse.compute_oppenheimer_snyder_trajectories(
            y0=3.0, n_tau=200, n_t=200
        )
        self.assertAlmostEqual(float(y_tau[0]), 3.0, places=7)
        self.assertAlmostEqual(float(y_tau[-1]), 0.0, places=7)
        self.assertTrue(np.all(np.diff(tau) > 0.0))
        self.assertGreater(tau_h, 0.0)
        self.assertLess(tau_h, tau_sing)
        self.assertAlmostEqual(float(tau_sing), 0.5 * (3.0**1.5) * math.pi, places=7)

        self.assertGreater(float(np.min(y_t)), 1.0)
        self.assertAlmostEqual(float(y_t[-1]), 3.0, places=7)
        self.assertAlmostEqual(float(t[-1]), 0.0, places=7)
        self.assertGreater(float(t[0]), 15.0)

    def test_curvature_optical_models(self):
        """Verify expansion, shear, twist, and shear-free optical deformation matrices."""
        generate_from_curvature_to_kerr_solution.validate_optical_models()

        lam = 2.5
        M_sf = generate_from_curvature_to_kerr_solution.deformation_matrix("shear_free", lam)
        scale = math.exp(generate_from_curvature_to_kerr_solution.ALPHA_SF * lam)
        self.assertTrue(np.allclose(M_sf.T @ M_sf, (scale**2) * np.eye(2), atol=1e-12))

    def test_geodesic_orbits_and_precession(self):
        """Verify planar Schwarzschild rosette and 3D Kerr nodal precession (+19.6 deg/cycle)."""
        data = generate_geodesic_orbits_schwarzschild_kerr.precompute_orbits()
        self.assertGreater(data["delta_omega_s_deg"], 15.0)
        self.assertAlmostEqual(data["delta_Omega_k_deg"], 19.6, delta=0.2)

        _, xs, ys, zs = data["dense_s"]
        _, xk, yk, zk = data["dense_k"]
        normal = np.cross([xs[0], ys[0], zs[0]], [xs[250], ys[250], zs[250]])
        normal = normal / np.linalg.norm(normal)
        pts_s = np.column_stack([xs, ys, zs])
        max_out_of_plane = float(np.max(np.abs(pts_s @ normal)))
        self.assertLess(max_out_of_plane, 1e-6)

        self.assertGreater(float(np.max(np.abs(zk))), 3.0)
        self.assertGreater(len(data["ascending_nodes_k"]), 5)
        for node in data["ascending_nodes_k"]:
            self.assertAlmostEqual(float(node["pos"][2]), 0.0, places=7)

    def test_kerr_anatomy_coordinates(self):
        """Verify Boyer-Lindquist oblate spheroidal coordinate identity and ergosurface bounds."""
        anat = generate_kerr_black_hole_anatomy
        self.assertAlmostEqual(float(anat.r_ergo(0.0)), float(anat.R_PLUS), places=7)
        self.assertAlmostEqual(float(anat.r_ergo(math.pi / 2.0)), 2.0 * anat.M_VAL, places=7)

        r_val = 1.6
        theta = 0.9
        phi = 1.2
        x, y, z = anat.kerr_xyz(r_val, theta, phi)
        self.assertAlmostEqual(
            x**2 + y**2,
            (r_val**2 + anat.A_VAL**2) * (math.sin(theta) ** 2),
            places=7,
        )
        self.assertAlmostEqual(z, r_val * math.cos(theta), places=7)


class TestBlackHoleThermodynamics(unittest.TestCase):
    """Test black-hole thermodynamics formulas and Bekenstein GSL state machine."""

    def test_bekenstein_gsl_animation_state(self):
        """Verify Bekenstein GSL box infall, horizon expansion, and static stage state."""
        s_init = generate_bekenstein_gsl.compute_frame_state(0)
        s_cross = generate_bekenstein_gsl.compute_frame_state(105)
        s_static = generate_bekenstein_gsl.compute_frame_state(0, is_static=True)

        self.assertEqual(s_init["stage"], 1)
        self.assertAlmostEqual(s_init["box_alpha"], 1.0, places=6)
        self.assertAlmostEqual(s_init["grow_frac"], 0.0, places=6)

        self.assertEqual(s_cross["stage"], 2)
        self.assertLess(s_cross["box_alpha"], 1.0)
        self.assertGreater(s_cross["grow_frac"], 0.0)

        self.assertEqual(s_static["stage"], 3)
        self.assertAlmostEqual(s_static["grow_frac"], 1.0, places=6)

    def test_hawking_temperature_and_bekenstein_entropy(self):
        """Verify SI Hawking temperature (~6e-8 K for 1 M_sun) and Bekenstein-Hawking area scaling."""
        hbar = 1.054571817e-34
        c = 2.99792458e8
        G = 6.67430e-11
        k_B = 1.380649e-23
        M_sun = 1.98847e30

        T_1 = (hbar * c**3) / (8.0 * math.pi * G * M_sun * k_B)
        T_2 = (hbar * c**3) / (8.0 * math.pi * G * (2.0 * M_sun) * k_B)
        self.assertAlmostEqual(T_1, 6.17e-8, delta=0.1e-8)
        self.assertAlmostEqual(T_2, 0.5 * T_1, places=14)

        r_s = 2.0 * G * M_sun / (c**2)
        area = 4.0 * math.pi * r_s**2
        ell_p = math.sqrt(hbar * G / (c**3))
        S_BH = k_B * area / (4.0 * ell_p**2)
        self.assertGreater(S_BH, 0.0)


class TestAssetIntegrityAndFigureGeneration(unittest.TestCase):
    """Verify repository scientific image assets and isolated figure rendering."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out_dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _verify_png(self, path: Path, min_bytes: int = 5000):
        self.assertTrue(path.exists(), f"Missing generated image: {path}")
        self.assertGreater(path.stat().st_size, min_bytes, f"Generated image too small: {path}")
        with Image.open(path) as im:
            self.assertEqual(im.format, "PNG")
            self.assertGreater(im.width, 100)
            self.assertGreater(im.height, 100)

    def test_scientific_assets_and_math_equations_present(self):
        """Verify all scientific PNGs, GIF/MP4 animations, and rendered math equations exist."""
        expected_pngs = [
            "oppenheimer_snyder_collapse.png",
            "lense_thirring_frame_dragging.png",
            "from_curvature_to_kerr_solution.png",
            "boyer_lindquist_coordinates.png",
            "kerr_black_hole_anatomy.png",
            "geodesic_orbits_schwarzschild_kerr.png",
            "black_hole_perturbations_ringdown.png",
            "penrose_process.png",
            "hawking_area_theorem.png",
            "bekenstein_gsl.png",
            "hawking_radiation_collapse_spectrum.png",
        ]
        for filename in expected_pngs:
            self._verify_png(IMAGES_DIR / filename, min_bytes=50000)

        expected_animations = [
            "lense_thirring_frame_dragging_animation.gif",
            "lense_thirring_frame_dragging_animation.mp4",
            "from_curvature_to_kerr_solution_animation.gif",
            "from_curvature_to_kerr_solution_animation.mp4",
            "boyer_lindquist_coordinates_animation.gif",
            "boyer_lindquist_coordinates_animation.mp4",
            "geodesic_orbits_schwarzschild_kerr_animation.gif",
            "geodesic_orbits_schwarzschild_kerr_animation.mp4",
            "penrose_process_animation.gif",
            "penrose_process_animation.mp4",
            "bekenstein_gsl_animation.gif",
            "bekenstein_gsl_animation.mp4",
        ]
        for filename in expected_animations:
            fpath = IMAGES_DIR / filename
            self.assertTrue(fpath.exists(), f"Missing animation asset: {fpath}")
            self.assertGreater(fpath.stat().st_size, 50000, f"Animation asset too small: {fpath}")

        math_dir = IMAGES_DIR / "math"
        self.assertTrue(math_dir.is_dir(), "Missing images/math directory")
        eq_files = list(math_dir.glob("eq_*.png"))
        self.assertGreaterEqual(len(eq_files), 30)

    def test_isolated_static_figures_and_posters(self):
        """Verify static figure and animated poster generators render valid PNGs into a temp folder."""
        figures = [
            (generate_oppenheimer_snyder_collapse, "create_figure", "oppenheimer_snyder.png"),
            (generate_lense_thirring_frame_dragging, "create_figure", "lense_thirring.png"),
            (generate_kerr_black_hole_anatomy, "create_figure", "kerr_anatomy.png"),
            (generate_black_hole_perturbations_ringdown, "create_figure", "ringdown.png"),
            (generate_hawking_area_theorem, "create_figure", "area_theorem.png"),
            (generate_hawking_radiation_collapse_spectrum, "create_figure", "hawking_spectrum.png"),
        ]
        for module, fn_name, filename in figures:
            with self.subTest(generator=module.__name__):
                out = self.out_dir / filename
                getattr(module, fn_name)(out)
                self._verify_png(out)

        bl_out = self.out_dir / "boyer_lindquist.png"
        generate_boyer_lindquist_coordinates.render_scene(0.8, is_static=True, output_path=bl_out)
        self._verify_png(bl_out)

        curv_out = self.out_dir / "curvature_to_kerr.png"
        generate_from_curvature_to_kerr_solution.render_frame(
            (generate_from_curvature_to_kerr_solution.N_MOTION_FRAMES - 1, str(curv_out))
        )
        self._verify_png(curv_out)

        bek_out = self.out_dir / "bekenstein_gsl.png"
        generate_bekenstein_gsl.draw_frame(generate_bekenstein_gsl.N_FRAMES - 1, bek_out, is_static=True)
        self._verify_png(bek_out)


if __name__ == "__main__":
    unittest.main()

