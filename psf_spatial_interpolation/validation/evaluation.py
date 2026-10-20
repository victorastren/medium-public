"""
Comprehensive evaluation and hyperparameter tuning module for PSF reconstruction pipeline.

Functions:
1. Hyperparameter optimization on validation stars (N_val = 80) via composite loss:
   J = (RMSE_e / 0.05)^2 + (RMSE_R2 / 0.20)^2
2. Scientific benchmark on test stars (N_test = 200) across all 6 algorithms:
   - Polynomial Regression (POLY)
   - Inverse Distance Weighting (IDW)
   - Radial Basis Function (RBF - Thin Plate Spline)
   - Ordinary Kriging (OK)
   - Random Forest (RF)
   - Multilayer Perceptron (MLP)
3. Quantitative metrics export and comparison table generation.
"""

from dataclasses import dataclass, asdict
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np

from simulation.dataset import load_dataset
from representation.pca import PSFRepresentation
from reconstruction.psf import reconstruct_psfs_from_coefficients
from validation.moments import measure_psf_batch
from validation.metrics import (
    compute_residual_stats,
    compute_representation_error,
    compute_reconstruction_metrics,
    ReconstructionMetrics
)
from interpolation.classical import PolynomialInterpolator, IDWInterpolator, RBFInterpolator
from interpolation.kriging import OrdinaryKrigingInterpolator, UniversalKrigingInterpolator
from interpolation.ml import RandomForestInterpolator, MLPInterpolator


@dataclass
class ModelBenchmarkResult:
    model_name: str
    category: str
    best_params: dict[str, Any]
    val_loss: float
    val_e_rmse: float
    val_r2_rmse: float
    test_e_rmse: float
    test_e1_bias: float
    test_e1_sem: float
    test_e2_bias: float
    test_e2_sem: float
    test_emag_rmse: float
    test_r2_bias: float
    test_r2_rmse: float
    test_r2_sem: float
    test_r2_rel_rmse: float
    test_pixel_rmse: float
    test_rec_error: float
    fit_time_ms: float
    predict_time_ms: float


def compute_composite_loss(
    pred_e1: np.ndarray,
    pred_e2: np.ndarray,
    pred_r2: np.ndarray,
    true_e1: np.ndarray,
    true_e2: np.ndarray,
    true_r2: np.ndarray,
    e_scale: float = 0.05,
    r2_scale: float = 0.20
) -> tuple[float, float, float]:
    """
    Compute composite scientific validation loss J:
        J = (RMSE_e / e_scale)^2 + (RMSE_R2 / r2_scale)^2
    """
    delta_e1 = pred_e1 - true_e1
    delta_e2 = pred_e2 - true_e2
    delta_r2 = pred_r2 - true_r2

    e_rmse = float(np.sqrt(np.mean(delta_e1 ** 2 + delta_e2 ** 2)))
    r2_rmse = float(np.sqrt(np.mean(delta_r2 ** 2)))
    loss = float((e_rmse / e_scale) ** 2 + (r2_rmse / r2_scale) ** 2)

    return loss, e_rmse, r2_rmse


def tune_and_evaluate_model(
    model_name: str,
    category: str,
    param_grid: list[dict[str, Any]],
    model_factory: Any,
    train_pos: np.ndarray,
    train_coeffs: np.ndarray,
    val_pos: np.ndarray,
    val_moments: dict[str, np.ndarray],
    test_pos: np.ndarray,
    test_moments: dict[str, np.ndarray],
    test_images: np.ndarray,
    pca: PSFRepresentation,
    sigma_w: float = 3.5
) -> ModelBenchmarkResult:
    """
    Tune a model over param_grid using validation stars, then evaluate on test stars.
    """
    best_loss = float("inf")
    best_params: dict[str, Any] = {}
    best_val_e_rmse = float("inf")
    best_val_r2_rmse = float("inf")

    v_e1 = val_moments["e1"]
    v_e2 = val_moments["e2"]
    v_r2 = val_moments["r2"]

    for params in param_grid:
        try:
            model = model_factory(**params)
            model.fit(train_pos, train_coeffs)
            pred_val_coeffs = model.predict(val_pos)
            pred_val_images = reconstruct_psfs_from_coefficients(pred_val_coeffs, pca, physical_adjustment=True)
            p_e1, p_e2, p_r2 = measure_psf_batch(pred_val_images, sigma_w=sigma_w)

            loss, e_rmse, r2_rmse = compute_composite_loss(p_e1, p_e2, p_r2, v_e1, v_e2, v_r2)
            if loss < best_loss:
                best_loss = loss
                best_params = params
                best_val_e_rmse = e_rmse
                best_val_r2_rmse = r2_rmse
        except Exception as err:
            print(f"Warning: model {model_name} with params {params} failed: {err}")

    # Retrain best model and measure fit runtime
    t0 = time.perf_counter()
    best_model = model_factory(**best_params)
    best_model.fit(train_pos, train_coeffs)
    fit_time_ms = (time.perf_counter() - t0) * 1000.0

    # Predict test positions and measure inference runtime
    t1 = time.perf_counter()
    pred_test_coeffs = best_model.predict(test_pos)
    predict_time_ms = (time.perf_counter() - t1) * 1000.0

    # Reconstruct test PSFs
    pred_test_images = reconstruct_psfs_from_coefficients(pred_test_coeffs, pca, physical_adjustment=True)
    p_e1, p_e2, p_r2 = measure_psf_batch(pred_test_images, sigma_w=sigma_w)

    # Compute comprehensive metrics
    t_e1 = test_moments["e1"]
    t_e2 = test_moments["e2"]
    t_r2 = test_moments["r2"]

    metrics: ReconstructionMetrics = compute_reconstruction_metrics(
        true_e1=t_e1,
        true_e2=t_e2,
        true_r2=t_r2,
        pred_e1=p_e1,
        pred_e2=p_e2,
        pred_r2=p_r2,
        true_psfs=test_images,
        pred_psfs=pred_test_images
    )

    rec_err = compute_representation_error(test_images, pred_test_images)

    return ModelBenchmarkResult(
        model_name=model_name,
        category=category,
        best_params=best_params,
        val_loss=best_loss,
        val_e_rmse=best_val_e_rmse,
        val_r2_rmse=best_val_r2_rmse,
        test_e_rmse=metrics.combined_ellipticity_rmse,
        test_e1_bias=metrics.e1_stats.bias,
        test_e1_sem=metrics.e1_stats.sem,
        test_e2_bias=metrics.e2_stats.bias,
        test_e2_sem=metrics.e2_stats.sem,
        test_emag_rmse=metrics.e_mag_stats.rmse,
        test_r2_bias=metrics.r2_stats.bias,
        test_r2_rmse=metrics.r2_stats.rmse,
        test_r2_sem=metrics.r2_stats.sem,
        test_r2_rel_rmse=metrics.r2_rel_stats.rmse,
        test_pixel_rmse=metrics.pixel_rmse,
        test_rec_error=rec_err,
        fit_time_ms=fit_time_ms,
        predict_time_ms=predict_time_ms
    )


def run_full_benchmark(
    dataset_dir: str = "data/field_000",
    n_components: int = 5,
    output_dir: str = "results",
    output_json_name: str = "baseline_reconstruction_benchmark.json",
    output_table_name: str = "benchmark_summary.md"
) -> list[ModelBenchmarkResult]:
    """
    Run the end-to-end benchmark across all 6 spatial interpolation models.
    """
    os.makedirs(output_dir, exist_ok=True)
    dataset = load_dataset(dataset_dir)

    print("--- Running PSF Spatial Interpolation Benchmark ---")
    print(f"Dataset: {dataset_dir}")
    print(f"Training stars: {len(dataset.positions_train)}")
    print(f"Validation stars: {len(dataset.positions_val)}")
    print(f"Test stars: {len(dataset.positions_test)}")
    print(f"PCA components: K = {n_components}\n")

    # 1. Fit PCA basis on training stars
    pca = PSFRepresentation(n_components_max=n_components)
    pca.fit(dataset.psfs_train_observed)

    train_coeffs = pca.transform(dataset.psfs_train_observed, n_components=n_components)

    # Precompute validation moments
    val_e1, val_e2, val_r2 = measure_psf_batch(dataset.psfs_val_true, sigma_w=3.5)
    val_moments = {"e1": val_e1, "e2": val_e2, "r2": val_r2}

    test_moments = {
        "e1": dataset.true_test_e1,
        "e2": dataset.true_test_e2,
        "r2": dataset.true_test_r2
    }

    # Calculate baseline representation error on test stars
    test_rep_psfs = pca.reconstruct(dataset.psfs_test_true, n_components=n_components)
    base_rep_error = compute_representation_error(dataset.psfs_test_true, test_rep_psfs)
    print(f"Theoretical PCA Representation Error limit (K={n_components}): E_rep = {base_rep_error * 100:.4f}%\n")

    # Define hyperparameter candidate grids for all 6 models
    models_to_test = [
        (
            "Polynomial (POLY)",
            "Deterministic / Classical",
            PolynomialInterpolator,
            [{"degree": 1}, {"degree": 2}, {"degree": 3}, {"degree": 4}]
        ),
        (
            "Inverse Distance Weighting (IDW)",
            "Deterministic / Classical",
            IDWInterpolator,
            [{"power": 0.5}, {"power": 1.0}, {"power": 1.5}, {"power": 2.0}, {"power": 2.5}, {"power": 3.0}, {"power": 4.0}]
        ),
        (
            "Radial Basis Function (RBF - TPS)",
            "Deterministic / Spline",
            RBFInterpolator,
            [{"smoothing": 1e-8}, {"smoothing": 1e-6}, {"smoothing": 1e-4}, {"smoothing": 1e-2}, {"smoothing": 0.1}, {"smoothing": 1.0}]
        ),
        (
            "Ordinary Kriging (OK)",
            "Geostatistical (Constant)",
            OrdinaryKrigingInterpolator,
            [{}]
        ),
        (
            "Universal Kriging - Linear (UK-Lin)",
            "Geostatistical (Linear Drift)",
            UniversalKrigingInterpolator,
            [{"trend": "linear"}]
        ),
        (
            "Universal Kriging - Quadratic (UK-Quad)",
            "Geostatistical (Quadratic Drift)",
            UniversalKrigingInterpolator,
            [{"trend": "quadratic"}]
        ),
        (
            "Random Forest (RF)",
            "Machine Learning (Trees)",
            RandomForestInterpolator,
            [
                {"n_estimators": 100, "max_depth": 6, "min_samples_leaf": 2},
                {"n_estimators": 100, "max_depth": 10, "min_samples_leaf": 1},
                {"n_estimators": 200, "max_depth": None, "min_samples_leaf": 2},
                {"n_estimators": 200, "max_depth": 12, "min_samples_leaf": 1}
            ]
        ),
        (
            "Multilayer Perceptron (MLP)",
            "Machine Learning (Neural)",
            MLPInterpolator,
            [
                {"hidden_layer_sizes": (32, 16), "activation": "tanh", "alpha": 0.001},
                {"hidden_layer_sizes": (32, 16), "activation": "tanh", "alpha": 0.01},
                {"hidden_layer_sizes": (64, 32), "activation": "tanh", "alpha": 0.01},
                {"hidden_layer_sizes": (32, 32), "activation": "tanh", "alpha": 0.05},
                {"hidden_layer_sizes": (32, 16), "activation": "relu", "alpha": 0.01}
            ]
        )
    ]

    results: list[ModelBenchmarkResult] = []

    for name, category, factory, grid in models_to_test:
        print(f"Evaluating {name} ({len(grid)} candidate configurations)...")
        res = tune_and_evaluate_model(
            model_name=name,
            category=category,
            param_grid=grid,
            model_factory=factory,
            train_pos=dataset.positions_train,
            train_coeffs=train_coeffs,
            val_pos=dataset.positions_val,
            val_moments=val_moments,
            test_pos=dataset.positions_test,
            test_moments=test_moments,
            test_images=dataset.psfs_test_true,
            pca=pca,
            sigma_w=3.5
        )
        results.append(res)
        print(f"  Best params: {res.best_params}")
        print(f"  Test RMSE(e): {res.test_e_rmse:.5f} | Test RMSE(R²): {res.test_r2_rmse:.5f} px² | Test E_rec: {res.test_rec_error * 100:.3f}%\n")

    # Save benchmark results to JSON
    json_path = os.path.join(output_dir, output_json_name)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    print(f"[OK] Saved metrics to {json_path}")

    # Format Markdown summary table
    md_table = format_markdown_table(results, base_rep_error)
    md_path = os.path.join(output_dir, output_table_name)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_table)
    print(f"[OK] Saved table to {md_path}")
    print("\n" + md_table)

    return results


def format_markdown_table(results: list[ModelBenchmarkResult], base_rep_error: float) -> str:
    """Format benchmark results into a clean publication Markdown table."""
    lines = [
        "### Reconstruction Accuracy Across Spatial Interpolation Algorithms",
        "",
        "| Algorithm | Category | Optimal Hyperparameters | RMSE(e) (×10⁻³) | RMSE(R²) (px²) | Relative Size Error (%) | E_rec (%) | Runtime (ms) |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |"
    ]

    for r in results:
        param_str = ", ".join(f"`{k}={v}`" for k, v in r.best_params.items()) if r.best_params else "Default"
        e_rmse_milli = r.test_e_rmse * 1e3
        rel_size_pct = r.test_r2_rel_rmse * 100.0
        rec_err_pct = r.test_rec_error * 100.0
        total_time = r.fit_time_ms + r.predict_time_ms

        lines.append(
            f"| **{r.model_name}** | {r.category} | {param_str} | **{e_rmse_milli:.3f}** | {r.test_r2_rmse:.4f} | {rel_size_pct:.2f}% | {rec_err_pct:.3f}% | {total_time:.1f} |"
        )

    lines.append("")
    lines.append(f"*Note: Theoretical PCA representation lower bound with K=5 components is E_rep = {base_rep_error * 100:.3f}%. Evaluated on N=200 test stars with Gaussian window σ_w = 3.5 px.*")
    return "\n".join(lines)


if __name__ == "__main__":
    run_full_benchmark()
