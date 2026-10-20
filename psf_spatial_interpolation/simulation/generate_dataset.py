"""
Generate and save simulated PSF field datasets matching technical specification Section 3.5.
Produces:
- data/field_000/ with all .npy arrays, physical_parameters.npz, and config.json.
- images/dataset_field_000_preview.png showing the spatial sampling and sample PSF stamps.
"""

import os
import sys
from pathlib import Path
import numpy as np

# Ensure root package is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from simulation.dataset import (
    SmoothMoffatFieldGenerator,
    ComplexGroundFieldGenerator,
    build_field_dataset,
    save_field_dataset
)

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def generate_and_save_baseline_dataset(
    output_dir: str = str(BASE_DIR / "data" / "field_000"),
    preview_img_path: str = str(BASE_DIR / "images" / "dataset_field_000_preview.png")
):
    print(f"--- Generating Baseline Dataset (Scenario G1-smooth) -> {output_dir} ---")
    generator = SmoothMoffatFieldGenerator(seed=100, beta=3.5, base_fwhm=3.5)

    dataset = build_field_dataset(
        generator=generator,
        n_train=320,
        n_val=80,
        n_test=200,
        seed=42,
        stamp_size=48,
        subpixel_factor=4
    )

    cfg = {
        "scenario": "G1_smooth",
        "description": "Seeing-dominated smooth Moffat PSF field with quadratic spatial parameter variations",
        "simulation_parameters": {
            "psf_model": "elliptical_moffat",
            "beta": 3.5,
            "base_fwhm_pixels": 3.5,
            "fwhm_variation_amplitude": 0.3,
            "ellipticity_variation_amplitude": 0.06,
            "field_seed": 100,
            "coordinate_sampling_seed": 42
        },
        "dataset_geometry": {
            "stamp_size": 48,
            "subpixel_factor": 4,
            "focal_plane_bounds": [0.0, 1.0, 0.0, 1.0],
            "margin": 0.02,
            "n_train": 320,
            "n_val": 80,
            "n_test": 200,
            "normalization": "unit_total_flux",
            "data_type": "float64"
        },
        "noise_model": {
            "type": "noiseless_reference",
            "note": "psf_train_observed is identical to psf_train_true in this baseline experiment"
        },
        "measurement_parameters": {
            "moment_weight": "circular_gaussian",
            "sigma_w_pixels": 3.5,
            "ellipticity_convention": "GREAT10: e1=(Q11-Q22)/(Q11+Q22), e2=2*Q12/(Q11+Q22), R2=Q11+Q22",
            "fixed_center": [23.5, 23.5]
        }
    }

    save_field_dataset(dataset, output_dir=output_dir, config=cfg)
    print(f"[OK] Saved dataset files to {output_dir}:")
    print(f"  - positions_train.npy:      {dataset.positions_train.shape}")
    print(f"  - positions_validation.npy: {dataset.positions_val.shape}")
    print(f"  - positions_test.npy:       {dataset.positions_test.shape}")
    print(f"  - psf_train_true.npy:       {dataset.psfs_train_true.shape}")
    print(f"  - psf_train_observed.npy:   {dataset.psfs_train_observed.shape}")
    print(f"  - psf_validation_true.npy:  {dataset.psfs_val_true.shape}")
    print(f"  - psf_test_true.npy:        {dataset.psfs_test_true.shape}")
    print(f"  - physical_parameters.npz:  (true_test_e1, true_test_e2, true_test_r2)")
    print(f"  - config.json (enriched with full experimental parameters)")

    # Generate preview figure if matplotlib is available
    if HAS_MATPLOTLIB:
        os.makedirs(os.path.dirname(preview_img_path), exist_ok=True)
        fig, ax = plt.subplots(figsize=(8.5, 8.5), dpi=260)

        ax.set_facecolor("#ffffff")
        ax.grid(True, linestyle="--", alpha=0.35, color="#cccccc", zorder=0)

        ax.scatter(dataset.positions_train[:, 0], dataset.positions_train[:, 1],
                   c="#1f77b4", s=38, alpha=0.8, marker="o", edgecolors="none",
                   label=f"Training ({len(dataset.positions_train)})", zorder=2)
        ax.scatter(dataset.positions_val[:, 0], dataset.positions_val[:, 1],
                   c="#2ca02c", s=52, alpha=0.9, marker="^", edgecolors="none",
                   label=f"Validation ({len(dataset.positions_val)})", zorder=3)
        ax.scatter(dataset.positions_test[:, 0], dataset.positions_test[:, 1],
                   c="#d62728", s=34, alpha=0.75, marker="x", linewidths=1.5,
                   label=f"Test ({len(dataset.positions_test)})", zorder=4)

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")

        ax.set_title("Simulated Stellar Positions", fontsize=22, fontweight="bold", pad=16, color="#111111")
        ax.set_xlabel("Focal-plane x", color="#111111", fontsize=19, fontweight="bold", labelpad=10)
        ax.set_ylabel("Focal-plane y", color="#111111", fontsize=19, fontweight="bold", labelpad=10)

        ax.tick_params(colors="#111111", labelsize=16, width=1.5, length=6)
        for spine in ax.spines.values():
            spine.set_color("#444444")
            spine.set_linewidth(1.4)

        leg = ax.legend(
            loc="upper right",
            fontsize=16,
            frameon=True,
            facecolor="#ffffff",
            edgecolor="#bbbbbb",
            framealpha=0.95,
            borderpad=0.8,
            labelspacing=0.6
        )
        for text in leg.get_texts():
            text.set_color("#111111")

        plt.tight_layout()
        plt.savefig(preview_img_path, bbox_inches="tight")
        # Also save to simulated_stellar_positions.png
        alt_path = Path(preview_img_path).parent / "simulated_stellar_positions.png"
        plt.savefig(alt_path, bbox_inches="tight")
        plt.close(fig)
        print(f"[OK] Saved preview figures to: {preview_img_path} and {alt_path}")


def generate_and_save_g2_dataset(
    output_dir: str = str(BASE_DIR / "data" / "field_g2"),
    preview_img_path: str = str(BASE_DIR / "images" / "dataset_field_g2_preview.png")
):
    print(f"--- Generating Complex Ground-Based Dataset (Scenario G2) -> {output_dir} ---")
    generator = ComplexGroundFieldGenerator(
        seed=500,
        base_fwhm=3.4,
        defocus_coeff=1.2,
        astig_coeff=0.10,
        coma_coeff=0.08,
        beta_base=3.5,
        correlation_length=0.20
    )

    dataset = build_field_dataset(
        generator=generator,
        n_train=320,
        n_val=80,
        n_test=200,
        seed=42,
        stamp_size=48,
        subpixel_factor=4
    )

    cfg = {
        "scenario": "G2_complex_ground",
        "description": "Realistic ground-based PSF field with optical aberrations (defocus, astigmatism, coma) and correlated atmospheric fluctuations",
        "simulation_parameters": {
            "psf_model": "aberrated_elliptical_moffat",
            "base_fwhm_pixels": 3.4,
            "optical_defocus_coeff": 1.2,
            "optical_astigmatism_coeff": 0.10,
            "optical_coma_coeff": 0.08,
            "beta_base": 3.5,
            "matern_nu": 1.5,
            "matern_correlation_length": 0.20,
            "turbulence_std_fwhm": 0.15,
            "turbulence_std_ellipticity": 0.02,
            "turbulence_std_beta": 0.25,
            "field_seed": 500,
            "coordinate_sampling_seed": 42
        },
        "dataset_geometry": {
            "stamp_size": 48,
            "subpixel_factor": 4,
            "focal_plane_bounds": [0.0, 1.0, 0.0, 1.0],
            "margin": 0.02,
            "n_train": 320,
            "n_val": 80,
            "n_test": 200,
            "normalization": "unit_total_flux",
            "data_type": "float64"
        },
        "noise_model": {
            "type": "noiseless_reference",
            "note": "psf_train_observed is identical to psf_train_true in this initial benchmark"
        },
        "measurement_parameters": {
            "moment_weight": "circular_gaussian",
            "sigma_w_pixels": 3.5,
            "ellipticity_convention": "GREAT10: e1=(Q11-Q22)/(Q11+Q22), e2=2*Q12/(Q11+Q22), R2=Q11+Q22",
            "fixed_center": [23.5, 23.5]
        }
    }

    save_field_dataset(dataset, output_dir=output_dir, config=cfg)
    print(f"[OK] Saved G2 dataset files to {output_dir}:")
    print(f"  - positions_train.npy:      {dataset.positions_train.shape}")
    print(f"  - positions_validation.npy: {dataset.positions_val.shape}")
    print(f"  - positions_test.npy:       {dataset.positions_test.shape}")
    print(f"  - psf_train_true.npy:       {dataset.psfs_train_true.shape}")
    print(f"  - psf_train_observed.npy:   {dataset.psfs_train_observed.shape}")
    print(f"  - psf_validation_true.npy:  {dataset.psfs_val_true.shape}")
    print(f"  - psf_test_true.npy:        {dataset.psfs_test_true.shape}")
    print(f"  - physical_parameters.npz:  (true_test_e1, true_test_e2, true_test_r2)")
    print(f"  - config.json (enriched with full experimental parameters)")


def generate_and_save_s1_dataset(
    output_dir: str = str(BASE_DIR / "data" / "field_s1"),
    preview_img_path: str = str(BASE_DIR / "images" / "dataset_field_s1_preview.png")
):
    print(f"--- Generating Space-Based Diffraction Dataset (Scenario S1) -> {output_dir} ---")
    from simulation.optics import SpaceDiffractionFieldGenerator

    generator = SpaceDiffractionFieldGenerator(
        c4_base=0.02,
        a_def=0.08,
        a_ast=0.04,
        a_coma=0.05,
        c11_base=0.02,
        n_pupil=128,
        stamp_size=48,
        subpixel_factor=4,
        sampling_s=2.5,
        obscuration_ratio=0.30,
        strut_width=0.025
    )

    dataset = build_field_dataset(
        generator=generator,
        n_train=320,
        n_val=80,
        n_test=200,
        seed=42,
        stamp_size=48,
        subpixel_factor=4
    )

    cfg = {
        "scenario": "S1_space_diffraction",
        "description": "Diffraction-based space telescope optical PSF with central obscuration, spider struts, and spatially varying optical aberrations",
        "optical_parameters": {
            "optical_model": "Matrix Fourier Transform (MFT, Soummer et al. 2007)",
            "pupil_resolution": 128,
            "central_obscuration_ratio": 0.30,
            "spider_strut_width": 0.025,
            "sampling_s_detector_pixels_per_lambda_over_D": 2.5,
            "zernike_aberrations": {
                "c4_defocus": "0.02 + 0.08 * ((x-0.5)^2 + (y-0.5)^2)",
                "c5_astigmatism_oblique": "2 * 0.04 * (x-0.5) * (y-0.5)",
                "c6_astigmatism_vertical": "0.04 * ((x-0.5)^2 - (y-0.5)^2)",
                "c7_coma_x": "0.05 * (x-0.5)",
                "c8_coma_y": "0.05 * (y-0.5)",
                "c11_spherical": "0.02"
            }
        },
        "dataset_geometry": {
            "stamp_size": 48,
            "subpixel_factor": 4,
            "focal_plane_bounds": [0.0, 1.0, 0.0, 1.0],
            "margin": 0.02,
            "n_train": 320,
            "n_val": 80,
            "n_test": 200,
            "normalization": "unit_total_flux",
            "data_type": "float64"
        },
        "noise_model": {
            "type": "noiseless_reference",
            "note": "psf_train_observed is identical to psf_train_true in this initial benchmark"
        },
        "measurement_parameters": {
            "moment_weight": "circular_gaussian",
            "sigma_w_pixels": 3.5,
            "ellipticity_convention": "GREAT10: e1=(Q11-Q22)/(Q11+Q22), e2=2*Q12/(Q11+Q22), R2=Q11+Q22",
            "fixed_center": [23.5, 23.5]
        }
    }

    save_field_dataset(dataset, output_dir=output_dir, config=cfg)
    print(f"[OK] Saved S1 dataset files to {output_dir}:")
    print(f"  - positions_train.npy:      {dataset.positions_train.shape}")
    print(f"  - positions_validation.npy: {dataset.positions_val.shape}")
    print(f"  - positions_test.npy:       {dataset.positions_test.shape}")
    print(f"  - psf_train_true.npy:       {dataset.psfs_train_true.shape}")
    print(f"  - psf_train_observed.npy:   {dataset.psfs_train_observed.shape}")
    print(f"  - psf_validation_true.npy:  {dataset.psfs_val_true.shape}")
    print(f"  - psf_test_true.npy:        {dataset.psfs_test_true.shape}")
    print(f"  - physical_parameters.npz:  (true_test_e1, true_test_e2, true_test_r2)")
    print(f"  - config.json (enriched with full experimental parameters)")


if __name__ == "__main__":
    generate_and_save_baseline_dataset()
    generate_and_save_g2_dataset()
    generate_and_save_s1_dataset()
