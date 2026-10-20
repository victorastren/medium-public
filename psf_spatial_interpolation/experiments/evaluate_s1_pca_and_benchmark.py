"""
Evaluate Scenario S1 PCA representation capacity and select K via end-to-end validation error.
Then run full benchmark across all 6 spatial interpolation models on S1.
"""

import sys
import json
from pathlib import Path
import numpy as np

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from simulation.dataset import load_dataset
from representation.pca import PSFRepresentation
from validation.moments import measure_psf_batch
from validation.evaluation import (
    tune_and_evaluate_model,
    run_full_benchmark,
    compute_composite_loss
)
from validation.metrics import compute_representation_error
from reconstruction.psf import reconstruct_psfs_from_coefficients
from interpolation.classical import PolynomialInterpolator, IDWInterpolator, RBFInterpolator
from interpolation.kriging import OrdinaryKrigingInterpolator, UniversalKrigingInterpolator
from interpolation.ml import RandomForestInterpolator, MLPInterpolator


def evaluate_s1_validation_curve(dataset_dir: str = "data/field_s1", max_k: int = 12):
    dataset = load_dataset(dataset_dir)
    val_e1, val_e2, val_r2 = measure_psf_batch(dataset.psfs_val_true, sigma_w=3.5)
    val_moments = {"e1": val_e1, "e2": val_e2, "r2": val_r2}
    test_moments = {"e1": dataset.true_test_e1, "e2": dataset.true_test_e2, "r2": dataset.true_test_r2}

    print("================================================================================")
    print("SCENARIO S1: PCA SPECTRUM & VALIDATION LOSS VS BASIS DIMENSION K")
    print("================================================================================")

    pca_full = PSFRepresentation(n_components_max=max_k)
    pca_full.fit(dataset.psfs_train_observed)

    # Models to evaluate for K selection
    models = [
        ("RBF Spline", RBFInterpolator, [{"smoothing": 1e-8}, {"smoothing": 1e-4}, {"smoothing": 0.01}]),
        ("UK-Quad", UniversalKrigingInterpolator, [{"trend": "quadratic"}]),
        ("Polynomial", PolynomialInterpolator, [{"degree": 2}, {"degree": 3}])
    ]

    records = []
    print(f"{'K':>2} | {'Var Ratio':>10} | {'Cum Var':>8} | {'E_rep (Val)':>12} | {'RBF Val J':>10} | {'RBF Val e_rmse':>15} | {'UK Val J':>9} | {'Poly Val J':>11}")
    print("-" * 92)

    for k in range(1, max_k + 1):
        vr = float(pca_full.explained_variance_ratio[k - 1])
        cv = float(np.sum(pca_full.explained_variance_ratio[:k])) * 100.0

        # Representation error on validation stars
        val_coeffs_dir = pca_full.transform(dataset.psfs_val_true, n_components=k)
        rec_val_dir = reconstruct_psfs_from_coefficients(val_coeffs_dir, pca_full, physical_adjustment=True)
        e_rep_val = compute_representation_error(dataset.psfs_val_true, rec_val_dir) * 100.0

        pca_k = PSFRepresentation(n_components_max=k)
        pca_k.fit(dataset.psfs_train_observed)
        tr_coeffs = pca_k.transform(dataset.psfs_train_observed, n_components=k)

        # Evaluate RBF
        res_rbf = tune_and_evaluate_model(
            model_name="RBF", category="", param_grid=models[0][2], model_factory=models[0][1],
            train_pos=dataset.positions_train, train_coeffs=tr_coeffs, val_pos=dataset.positions_val,
            val_moments=val_moments, test_pos=dataset.positions_test, test_moments=test_moments,
            test_images=dataset.psfs_test_true, pca=pca_k, sigma_w=3.5
        )

        # Evaluate UK-Quad
        res_uk = tune_and_evaluate_model(
            model_name="UK-Quad", category="", param_grid=models[1][2], model_factory=models[1][1],
            train_pos=dataset.positions_train, train_coeffs=tr_coeffs, val_pos=dataset.positions_val,
            val_moments=val_moments, test_pos=dataset.positions_test, test_moments=test_moments,
            test_images=dataset.psfs_test_true, pca=pca_k, sigma_w=3.5
        )

        # Evaluate Polynomial
        res_poly = tune_and_evaluate_model(
            model_name="Poly", category="", param_grid=models[2][2], model_factory=models[2][1],
            train_pos=dataset.positions_train, train_coeffs=tr_coeffs, val_pos=dataset.positions_val,
            val_moments=val_moments, test_pos=dataset.positions_test, test_moments=test_moments,
            test_images=dataset.psfs_test_true, pca=pca_k, sigma_w=3.5
        )

        records.append({
            "k": k,
            "variance_ratio": vr,
            "cumulative_variance": cv,
            "e_rep_val": e_rep_val,
            "rbf_val_loss": res_rbf.val_loss,
            "rbf_val_e_rmse": res_rbf.val_e_rmse,
            "uk_val_loss": res_uk.val_loss,
            "uk_val_e_rmse": res_uk.val_e_rmse,
            "poly_val_loss": res_poly.val_loss,
            "poly_val_e_rmse": res_poly.val_e_rmse
        })

        print(f"{k:2d} | {vr:10.6f} | {cv:7.2f}% | {e_rep_val:11.4f}% | {res_rbf.val_loss:10.5f} | {res_rbf.val_e_rmse*1000:13.3f}x10^-3 | {res_uk.val_loss:9.5f} | {res_poly.val_loss:11.5f}")

    return records


def main():
    records = evaluate_s1_validation_curve("data/field_s1", max_k=12)

    # Save validation records
    out_json = BASE_DIR / "results" / "s1_validation_k_selection.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"\n[OK] Saved S1 validation records to {out_json}")

    # Determine optimal K based on minimum validation loss among candidate models
    best_k = min(records[2:], key=lambda r: r["rbf_val_loss"])["k"]
    print(f"\nOptimal K based on minimum RBF validation loss: K* = {best_k}")

    # Run full benchmark for K=5 (for comparison with G1/G2 baseline) and validated K*
    print(f"\n--- Running Full Benchmark for S1 with K=5 ---")
    run_full_benchmark(
        dataset_dir="data/field_s1",
        n_components=5,
        output_dir="results",
        output_json_name="s1_benchmark_k5.json",
        output_table_name="s1_benchmark_k5_summary.md"
    )

    if best_k != 5:
        print(f"\n--- Running Full Benchmark for S1 with Validated K* = {best_k} ---")
        run_full_benchmark(
            dataset_dir="data/field_s1",
            n_components=best_k,
            output_dir="results",
            output_json_name=f"s1_benchmark_k{best_k}.json",
            output_table_name=f"s1_benchmark_k{best_k}_summary.md"
        )


if __name__ == "__main__":
    main()
