#!/usr/bin/env python3
"""
Unit and validation test suite for physical invariants, mathematical derivations,
and scientific figure generation in:
"From a Nearly Uniform Universe to Galaxies and the Cosmic Web"

Tests cover:
1. Jeans Instability & Linear Cosmological Perturbations:
   - Jeans dispersion relation omega^2 = c_s^2 k^2 - 4*pi*G*rho_0 and critical scale lambda_J
   - Exact Einstein-de Sitter growing (t^{2/3} ~ a) and decaying (t^{-1} ~ a^{-3/2}) modes
   - Subhorizon radiation-dominated logarithmic growth (Meszaros regime, delta_c ~ ln a)
2. Cosmological Background, Transfer Function, and Heath Growth Factor:
   - Comoving Hubble radius two-slope transition across matter-radiation equality
   - Continuity and qualitative behavior of CDM and baryon evolution curves
   - Matter transfer function T(k) large-scale plateau, equality turnover, and BAO modulation
   - Flat-LambdaCDM closure (Omega_m + Omega_Lambda = 1) and Heath (1977) growth integral
3. Anisotropic Gravitational Collapse (Zel'dovich Approximation):
   - Jacobian determinant det(dx/dq) = (1 - D*lambda_1)(1 - D*lambda_2)(1 - D*lambda_3)
   - Linear limit recovery delta ~ D*(lambda_1 + lambda_2 + lambda_3) and pancake shell crossing
   - 3D oblique projection and Bezier filament sampling
4. Asset Integrity & Figure Generation Pipeline:
   - Verification of observational Planck 2018 data files, source images, pre-rendered figures, and math equations
   - Isolated execution of all 17 scientific diagram and timeline generators into temporary directories
"""

import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import numpy as np
from PIL import Image

TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
CODE_DIR = PROJECT_DIR / "code"
IMAGES_DIR = PROJECT_DIR / "images"

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import generate_anisotropic_collapse_cosmic_web
import generate_cdm_baryon_evolution
import generate_cmb_to_cosmic_web
import generate_cosmic_expansion_coordinates
import generate_cosmic_web_timeline
import generate_cosmological_perturbations_timeline
import generate_dark_energy_structure_growth
import generate_dark_energy_timeline
import generate_horizon_entry
import generate_horizons_and_perturbation_scales
import generate_jeans_dispersion_relation
import generate_matter_transfer_power_spectrum
import generate_perturbation_evolution_timeline
import generate_photon_baryon_acoustic_oscillations
import generate_primordial_fluctuations_timeline
import generate_primordial_power_spectrum
import generate_quantum_fluctuations_inflation
import generate_spatial_curvature_friedmann


class TestJeansAndLinearPerturbations(unittest.TestCase):
    """Test mathematical relations for Jeans instability and linear perturbation growth."""

    def test_jeans_dispersion_and_wavelength(self):
        """Verify omega^2 = c_s^2 k^2 - 4*pi*G*rho_0 vanishes at lambda_J = c_s*sqrt(pi/(G*rho_0))."""
        c_s = 2.5
        G = 6.67430e-11
        rho_0 = 1.0e4

        lambda_J = c_s * np.sqrt(np.pi / (G * rho_0))
        k_J = 2.0 * np.pi / lambda_J

        def omega_sq(k):
            return (c_s ** 2) * (k ** 2) - 4.0 * np.pi * G * rho_0

        self.assertAlmostEqual(omega_sq(k_J), 0.0, places=12)
        self.assertLess(omega_sq(0.5 * k_J), 0.0)
        self.assertGreater(omega_sq(2.0 * k_J), 0.0)

    def test_einstein_de_sitter_growing_and_decaying_modes(self):
        """Verify delta_+(t) = t^{2/3} and delta_-(t) = t^{-1} solve the pressureless growth ODE."""
        t_vals = np.linspace(0.5, 10.0, 50)

        dd_plus = -(2.0 / 9.0) * (t_vals ** (-4.0 / 3.0))
        d_plus = (2.0 / 3.0) * (t_vals ** (-1.0 / 3.0))
        delta_plus = t_vals ** (2.0 / 3.0)
        residual_plus = dd_plus + (4.0 / (3.0 * t_vals)) * d_plus - (2.0 / (3.0 * t_vals ** 2)) * delta_plus
        np.testing.assert_allclose(residual_plus, 0.0, atol=1e-14)

        dd_minus = 2.0 * (t_vals ** -3.0)
        d_minus = -(t_vals ** -2.0)
        delta_minus = t_vals ** -1.0
        residual_minus = dd_minus + (4.0 / (3.0 * t_vals)) * d_minus - (2.0 / (3.0 * t_vals ** 2)) * delta_minus
        np.testing.assert_allclose(residual_minus, 0.0, atol=1e-14)

    def test_meszaros_radiation_era_logarithmic_solution(self):
        """Verify delta_c(t) = C_1 + C_2 * ln(a(t)) solves the subhorizon radiation-dominated limit."""
        t_vals = np.linspace(0.5, 10.0, 50)
        c2 = 0.8
        d_delta = 0.5 * c2 / t_vals
        dd_delta = -0.5 * c2 / (t_vals ** 2)
        H = 0.5 / t_vals
        residual = dd_delta + 2.0 * H * d_delta
        np.testing.assert_allclose(residual, 0.0, atol=1e-14)


class TestCosmologicalBackgroundAndGrowth(unittest.TestCase):
    """Test helper curves and physical solvers in the cosmological figure scripts."""

    def test_hubble_curve_asymptotics(self):
        """Verify hubble_curve passes through equality and matches radiation/matter asymptotic slopes."""
        x_eq, y_eq = 5.20, 5.85
        m_rad, m_mat = 1.10, 0.55
        self.assertAlmostEqual(
            float(generate_horizon_entry.hubble_curve(x_eq, x_eq=x_eq, y_eq=y_eq, m_rad=m_rad, m_mat=m_mat)),
            y_eq,
            places=12,
        )

        x_rad = np.array([0.0, 0.1])
        y_rad = generate_horizon_entry.hubble_curve(x_rad, x_eq=x_eq, y_eq=y_eq, m_rad=m_rad, m_mat=m_mat)
        slope_rad = (y_rad[1] - y_rad[0]) / (x_rad[1] - x_rad[0])
        self.assertAlmostEqual(slope_rad, m_rad, places=5)

        x_mat = np.array([10.0, 10.1])
        y_mat = generate_horizon_entry.hubble_curve(x_mat, x_eq=x_eq, y_eq=y_eq, m_rad=m_rad, m_mat=m_mat)
        slope_mat = (y_mat[1] - y_mat[0]) / (x_mat[1] - x_mat[0])
        self.assertAlmostEqual(slope_mat, m_mat, places=5)

    def test_cdm_and_baryon_evolution_curves(self):
        """Verify continuity, monotonicity of CDM, and acoustic oscillation bounds of baryons."""
        x_enter, x_eq, x_rec = 1.55, 4.95, 7.40
        eps = 1e-7

        for x_join in (x_enter, x_eq):
            y_left = generate_cdm_baryon_evolution.cdm_curve([x_join - eps])[0]
            y_right = generate_cdm_baryon_evolution.cdm_curve([x_join + eps])[0]
            self.assertAlmostEqual(y_left, y_right, places=5)

        y_left = generate_cdm_baryon_evolution.baryon_curve([x_enter - eps])[0]
        y_right = generate_cdm_baryon_evolution.baryon_curve([x_enter + eps])[0]
        self.assertAlmostEqual(y_left, y_right, places=5)

        x_post = np.linspace(x_rec + 0.01, 9.5, 100)
        y_bar_post = generate_cdm_baryon_evolution.baryon_curve(x_post)
        self.assertTrue(np.all(np.diff(y_bar_post) > 0), "Baryons must grow monotonically after recombination.")

        x_grid = np.linspace(0.5, 9.5, 400)
        y_cdm = generate_cdm_baryon_evolution.cdm_curve(x_grid)
        y_bar = generate_cdm_baryon_evolution.baryon_curve(x_grid)
        self.assertTrue(np.all(np.diff(y_cdm) > 0), "CDM curve must be strictly increasing.")
        subhorizon = x_grid > x_enter
        self.assertTrue(np.all(y_bar[subhorizon] < y_cdm[subhorizon]), "Baryon curve must remain below CDM after entry.")

    def test_transfer_function_and_matter_power_spectrum(self):
        """Verify T(k) large-scale normalization, small-scale suppression, and P_m(k) turnover."""
        u = np.linspace(-2.0, 2.0, 500)
        T, T_smooth, y_prim, y_pm = generate_matter_transfer_power_spectrum.compute_transfer_and_power(u)

        self.assertAlmostEqual(T_smooth[0], 1.0, places=12)
        self.assertAlmostEqual(T[0], 1.0, places=4)
        self.assertAlmostEqual(y_pm[0], y_prim[0], places=4)

        self.assertTrue(np.all(np.diff(T_smooth) < 0))
        self.assertLess(T_smooth[-1], 0.05)
        self.assertLess(y_pm[-1], y_prim[-1] - 4.0)

    def test_lcdm_closure_and_heath_growth_factor(self):
        """Verify flat-LambdaCDM closure Omega_m(a) + Omega_Lambda(a) = 1 and Heath growth suppression."""
        a_grid = np.linspace(0.05, 1.0, 200)
        omega_m, omega_l, d_matter, d_lcdm = generate_dark_energy_structure_growth.compute_cosmology_curves(
            a_grid, omega_m0=0.3, omega_l0=0.7, a_norm=0.1
        )

        np.testing.assert_allclose(omega_m + omega_l, 1.0, rtol=1e-14)
        self.assertAlmostEqual(omega_m[-1], 0.3, places=12)
        self.assertAlmostEqual(omega_l[-1], 0.7, places=12)

        idx_norm = np.argmin(np.abs(a_grid - 0.1))
        self.assertAlmostEqual(d_lcdm[idx_norm], d_matter[idx_norm], places=2)

        self.assertLess(d_lcdm[-1], d_matter[-1] * 0.85)
        self.assertGreater(d_lcdm[-1], 0.65)
        self.assertTrue(np.all(np.diff(d_lcdm) > 0))


class TestZeldovichAnisotropicCollapse(unittest.TestCase):
    """Test mathematical properties of the Zel'dovich approximation and 3D projection helpers."""

    def test_zeldovich_jacobian_and_linear_limit(self):
        """Verify Zel'dovich density formula recovers delta ~ D*(lambda_1+lambda_2+lambda_3) at small D."""
        lam1, lam2, lam3 = 0.8, 0.3, -0.2
        D = 1e-4

        rho_ratio = 1.0 / ((1.0 - D * lam1) * (1.0 - D * lam2) * (1.0 - D * lam3))
        delta_exact = rho_ratio - 1.0
        delta_linear = D * (lam1 + lam2 + lam3)

        self.assertAlmostEqual(delta_exact / delta_linear, 1.0, places=3)

        d_cross = 1.0 / lam1
        self.assertAlmostEqual(1.0 - d_cross * lam1, 0.0, places=12)
        self.assertGreater(1.0 - d_cross * lam2, 0.0)
        self.assertGreater(1.0 - d_cross * lam3, 0.0)

    def test_project_3d_and_filament_sampling(self):
        """Verify 3D oblique projection linearity and Bezier filament particle sampling."""
        cx, cy = 5.55, 5.12
        px0, py0 = generate_anisotropic_collapse_cosmic_web.project_3d(0.0, 0.0, 0.0, cx=cx, cy=cy)
        self.assertAlmostEqual(px0, cx, places=12)
        self.assertAlmostEqual(py0, cy, places=12)

        rng = np.random.default_rng(42)
        px, py, tier = generate_anisotropic_collapse_cosmic_web.sample_filament_points(
            rng, p0=(1.0, 1.0), p1=(4.0, 3.0), ctrl=(2.5, 2.2), n_pts=200, w_env=0.3, w_mid=0.15, w_core=0.05
        )
        self.assertEqual(len(px), 200)
        self.assertEqual(len(py), 200)
        self.assertTrue(set(np.unique(tier)).issubset({0, 1, 2}))


class TestAssetsAndMathImages(unittest.TestCase):
    """Verify observational datasets, source images, pre-rendered figures, and math equations."""

    def test_generator_source_dependencies_exist(self):
        """Verify all data files and source images required to reconstruct scientific figures exist."""
        required_files = [
            CODE_DIR / "COM_PowerSpect_CMB-TT-binned_R3.01.txt",
            CODE_DIR / "COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt",
            IMAGES_DIR / "planck_cmb_2018_clean.jpg",
            IMAGES_DIR / "nasa_svs_10118_cosmic_web.jpg",
        ]
        for path in required_files:
            self.assertTrue(path.exists(), f"Required reconstruction asset missing: {path}")
            self.assertGreater(path.stat().st_size, 1000, f"Required asset is unexpectedly small: {path}")

    def test_pre_rendered_figures_and_math_images_exist(self):
        """Verify all 18 scientific/timeline PNGs and all 30 equation PNGs exist on disk."""
        expected_figures = [
            "cmb_to_cosmic_web.png",
            "jeans_instability_dispersion_relation.png",
            "cosmic_expansion_coordinates.png",
            "spatial_curvature_friedmann.png",
            "particle_horizon_hubble_radius.png",
            "cosmological_perturbations_timeline.png",
            "quantum_fluctuations_primordial_perturbations.png",
            "primordial_power_spectrum.png",
            "primordial_fluctuations_timeline.png",
            "horizon_entry_perturbations.png",
            "photon_baryon_acoustic_oscillations.png",
            "cdm_baryon_perturbation_evolution.png",
            "matter_transfer_function_power_spectrum.png",
            "perturbation_evolution_timeline.png",
            "anisotropic_collapse_cosmic_web.png",
            "cosmic_web_timeline.png",
            "dark_energy_structure_growth.png",
            "dark_energy_timeline.png",
        ]
        for fname in expected_figures:
            fpath = IMAGES_DIR / fname
            self.assertTrue(fpath.exists(), f"Missing pre-rendered scientific figure: {fpath}")
            self.assertGreater(fpath.stat().st_size, 5000, f"Pre-rendered figure is too small: {fpath}")

        math_dir = IMAGES_DIR / "math"
        self.assertTrue(math_dir.exists(), f"Missing math directory: {math_dir}")
        math_pngs = list(math_dir.glob("eq_*.png"))
        self.assertEqual(len(math_pngs), 30, f"Expected 30 equation PNGs in {math_dir}, found {len(math_pngs)}")


class TestFigureGenerators(unittest.TestCase):
    """Verify that scientific figure and timeline generators execute cleanly into a temporary directory."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.out_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _verify_png(self, path):
        self.assertTrue(path.exists(), f"Output file does not exist: {path}")
        self.assertGreater(path.stat().st_size, 5000, f"Output file is too small: {path}")

        with open(path, "rb") as f:
            header = f.read(8)
            self.assertEqual(header, b"\x89PNG\r\n\x1a\n", f"Invalid PNG magic bytes for {path}")

        with Image.open(path) as img:
            self.assertEqual(img.format, "PNG")
            self.assertGreater(img.width, 400)
            self.assertGreater(img.height, 200)

    def test_diagram_and_plot_generators(self):
        """Run scientific diagram generators in an isolated temporary folder and verify PNG outputs."""
        generators = [
            (generate_jeans_dispersion_relation.create_figure, "jeans.png"),
            (generate_cosmic_expansion_coordinates.create_figure, "expansion.png"),
            (generate_horizons_and_perturbation_scales.create_figure, "horizons.png"),
            (generate_primordial_power_spectrum.create_figure, "primordial.png"),
            (generate_horizon_entry.create_figure, "horizon_entry.png"),
            (generate_photon_baryon_acoustic_oscillations.create_figure, "bao.png"),
            (generate_cdm_baryon_evolution.create_figure, "cdm_baryon.png"),
            (generate_matter_transfer_power_spectrum.create_figure, "transfer.png"),
            (generate_anisotropic_collapse_cosmic_web.create_figure, "collapse.png"),
            (generate_dark_energy_structure_growth.create_figure, "dark_energy.png"),
            (generate_cmb_to_cosmic_web.create_figure, "cmb_web.png"),
            (generate_quantum_fluctuations_inflation.create_figure, "quantum_fluctuations.png"),
        ]
        for func, filename in generators:
            out_path = self.out_dir / filename
            func(output_path=out_path)
            self._verify_png(out_path)

        fake_eq = Image.new("RGBA", (200, 60), (255, 255, 255, 255))
        with patch.object(
            generate_spatial_curvature_friedmann,
            "generate_latex_equation_image",
            return_value=fake_eq,
        ):
            curv_path = self.out_dir / "spatial_curvature.png"
            generate_spatial_curvature_friedmann.create_figure(output_path=curv_path)
            self._verify_png(curv_path)

    def test_timeline_generators(self):
        """Run all five historical timeline generators in an isolated temporary folder."""
        timelines = [
            (generate_cosmological_perturbations_timeline.create_timeline, "tl_perturbations.png"),
            (generate_primordial_fluctuations_timeline.create_timeline, "tl_primordial.png"),
            (generate_perturbation_evolution_timeline.create_timeline, "tl_evolution.png"),
            (generate_cosmic_web_timeline.create_timeline, "tl_web.png"),
            (generate_dark_energy_timeline.create_timeline, "tl_dark_energy.png"),
        ]
        for func, filename in timelines:
            out_path = self.out_dir / filename
            func(output_path=out_path)
            self._verify_png(out_path)


if __name__ == "__main__":
    unittest.main()