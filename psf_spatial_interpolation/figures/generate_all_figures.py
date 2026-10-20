#!/usr/bin/env python3
"""
Master runner script to generate all scientific figures and diagrams for
"Interpolating Stars: Reconstructing a telescope's point spread function at galaxy positions".

Usage:
    python3 figures/generate_all_figures.py
"""

import sys
import time
import subprocess
from pathlib import Path

FIGURES_DIR = Path(__file__).resolve().parent
PROJECT_DIR = FIGURES_DIR.parent
IMAGES_DIR = PROJECT_DIR / "images"

FIGURE_SCRIPTS = [
    ("Galaxy PSF Convolution Schematic", "generate_convolution_schematic.py", "galaxy_psf_convolution_schematic.png"),
    ("Spatial PSF Field Grid (8x8 Anisotropy)", "generate_diagnostic_figures.py", "spatial_psf_field_grid.png"),
    ("Observing Scenarios Galaxy Convolution Comparison", "generate_scenarios_galaxy_convolution_figure.py", "scenarios_galaxy_convolution_comparison.png"),
    ("Simulated Stellar Positions Distribution", "generate_stellar_positions_figure.py", "simulated_stellar_positions.png"),
    ("Mean PSF and Principal Components (EigenPSFs)", "generate_pca_components_figure.py", "pca_mean_and_components.png"),
    ("PCA Explained Variance & Representation Error vs K", "generate_pca_representation_vs_k_figure.py", "pca_representation_vs_k.png"),
    ("Spatial Interpolation Methods Taxonomy", "generate_interpolation_methods_taxonomy_figure.py", "spatial_interpolation_methods_taxonomy.png"),
    ("S1 Space PSF Reconstruction & Residuals", "generate_s1_reconstruction_figure.py", "s1_psf_reconstruction_residual.png"),
    ("Error Decomposition Paths (Representation vs Interpolation)", "generate_error_decomposition_paths_figure.py", "separating_representation_and_interpolation_errors.png"),
    ("Benchmark Ellipticity & Size Breakdown", "generate_benchmark_breakdown_figures.py", "benchmark_ellipticity_breakdown.png"),
    ("Summary Table 3 Image", "generate_table_3_figure.py", "table_3.png"),
    ("G2 Reconstruction Fidelity & Attenuation Scatter", "generate_reconstruction_fidelity_figure.py", "reconstruction_fidelity_g2.png"),
    ("Systematic Biases Forest Plot (m, c, b_R2)", "generate_systematic_biases_forest_plot.py", "systematic_biases_forest_plot.png"),
]


def run_pipeline():
    print("=" * 78)
    print(" Interpolating Stars - Master Figure Generation Pipeline")
    print(f" Output images directory: {IMAGES_DIR}")
    print("=" * 78)

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    total_start = time.time()
    success_count = 0

    for idx, (title, script_name, expected_image) in enumerate(FIGURE_SCRIPTS, start=1):
        script_path = FIGURES_DIR / script_name
        print(f"\n[{idx}/{len(FIGURE_SCRIPTS)}] Running {script_name} ({title})...")
        t0 = time.time()
        res = subprocess.run([sys.executable, str(script_path)], cwd=str(PROJECT_DIR), capture_output=True, text=True)
        dt = time.time() - t0

        if res.returncode == 0:
            target_img = IMAGES_DIR / expected_image
            size_kb = target_img.stat().st_size / 1024.0 if target_img.exists() else 0
            print(f"      ✓ Success in {dt:.2f}s -> {expected_image} ({size_kb:.1f} KB)")
            success_count += 1
        else:
            print(f"      ✗ FAILED ({script_name}):\n{res.stderr}\n{res.stdout}")

    total_time = time.time() - total_start
    print("\n" + "=" * 78)
    print(f" Figure Pipeline Complete: {success_count}/{len(FIGURE_SCRIPTS)} scripts completed in {total_time:.2f}s.")
    print("=" * 78)
    return success_count == len(FIGURE_SCRIPTS)


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
