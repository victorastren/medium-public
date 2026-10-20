"""
Evaluate PCA representation performance and truncation error for Scenario G2.
Determines whether K=5 components remain sufficient when moving from G1 to G2.
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
from reconstruction.psf import reconstruct_psfs_from_coefficients
from validation.moments import measure_psf_batch
from validation.metrics import compute_reconstruction_metrics, compute_representation_error


def evaluate_pca_on_field(dataset_dir: str, max_k: int = 15):
    dataset = load_dataset(dataset_dir)
    pca = PSFRepresentation(n_components_max=max_k)
    pca.fit(dataset.psfs_train_observed)

    # Precompute true moments on validation and test sets
    val_e1, val_e2, val_r2 = measure_psf_batch(dataset.psfs_val_true, sigma_w=3.5)
    test_e1, test_e2, test_r2 = measure_psf_batch(dataset.psfs_test_true, sigma_w=3.5)

    results_val = []
    results_test = []

    for k in range(1, max_k + 1):
        var_ratio = float(pca.explained_variance_ratio[k - 1])
        cum_var = float(np.sum(pca.explained_variance_ratio[:k]))

        # Validation set evaluation
        val_coeffs = pca.transform(dataset.psfs_val_true, n_components=k)
        rec_val = reconstruct_psfs_from_coefficients(val_coeffs, pca, physical_adjustment=True)
        e_rep_val = compute_representation_error(dataset.psfs_val_true, rec_val)
        p_val_e1, p_val_e2, p_val_r2 = measure_psf_batch(rec_val, sigma_w=3.5)
        metrics_val = compute_reconstruction_metrics(
            true_e1=val_e1, true_e2=val_e2, true_r2=val_r2,
            pred_e1=p_val_e1, pred_e2=p_val_e2, pred_r2=p_val_r2,
            true_psfs=dataset.psfs_val_true, pred_psfs=rec_val
        )

        results_val.append({
            "k": k,
            "variance_ratio": var_ratio,
            "cumulative_variance": cum_var,
            "e_rep": e_rep_val,
            "rmse_e": metrics_val.combined_ellipticity_rmse,
            "rmse_r2": metrics_val.r2_stats.rmse,
            "rel_rmse_r2": metrics_val.r2_rel_stats.rmse,
            "pixel_rmse": metrics_val.pixel_rmse
        })

        # Test set evaluation
        test_coeffs = pca.transform(dataset.psfs_test_true, n_components=k)
        rec_test = reconstruct_psfs_from_coefficients(test_coeffs, pca, physical_adjustment=True)
        e_rep_test = compute_representation_error(dataset.psfs_test_true, rec_test)
        p_test_e1, p_test_e2, p_test_r2 = measure_psf_batch(rec_test, sigma_w=3.5)
        metrics_test = compute_reconstruction_metrics(
            true_e1=test_e1, true_e2=test_e2, true_r2=test_r2,
            pred_e1=p_test_e1, pred_e2=p_test_e2, pred_r2=p_test_r2,
            true_psfs=dataset.psfs_test_true, pred_psfs=rec_test
        )

        results_test.append({
            "k": k,
            "variance_ratio": var_ratio,
            "cumulative_variance": cum_var,
            "e_rep": e_rep_test,
            "rmse_e": metrics_test.combined_ellipticity_rmse,
            "rmse_r2": metrics_test.r2_stats.rmse,
            "rel_rmse_r2": metrics_test.r2_rel_stats.rmse,
            "pixel_rmse": metrics_test.pixel_rmse
        })

    return results_val, results_test


def main():
    print("================================================================================")
    print("SCENARIO G2: PCA REPRESENTATION CAPACITY EVALUATION")
    print("================================================================================")

    res_val_g2, res_test_g2 = evaluate_pca_on_field(str(BASE_DIR / "data" / "field_g2"), max_k=15)
    res_val_g1, res_test_g1 = evaluate_pca_on_field(str(BASE_DIR / "data" / "field_000"), max_k=10)

    print("\n--- G2 Validation Set (N_val=80) Truncation Accuracy ---")
    print(f"{'K':>2} | {'Var Ratio':>10} | {'Cum Var (%)':>11} | {'E_rep (%)':>10} | {'RMSE(e) x10^3':>14} | {'RMSE(R2)':>10} | {'Rel Size Err':>12}")
    print("-" * 85)
    for r in res_val_g2:
        k = r["k"]
        vr = r["variance_ratio"]
        cv = r["cumulative_variance"] * 100.0
        erep = r["e_rep"] * 100.0
        e_milli = r["rmse_e"] * 1e3
        r2 = r["rmse_r2"]
        rel = r["rel_rmse_r2"] * 100.0
        print(f"{k:2d} | {vr:10.6f} | {cv:10.3f}% | {erep:9.4f}% | {e_milli:14.3f} | {r2:10.5f} | {rel:11.3f}%")

    print("\n--- G1 vs G2 Direct Comparison on Test Stars (N_test=200) ---")
    print(f"{'K':>2} | {'G1 E_rep (%)':>12} | {'G2 E_rep (%)':>12} | {'G1 RMSE(e) x10^3':>17} | {'G2 RMSE(e) x10^3':>17}")
    print("-" * 75)
    for k in range(1, 11):
        r1 = res_test_g1[k - 1]
        r2 = res_test_g2[k - 1]
        print(f"{k:2d} | {r1['e_rep']*100:11.4f}% | {r2['e_rep']*100:11.4f}% | {r1['rmse_e']*1e3:16.3f} | {r2['rmse_e']*1e3:16.3f}")

    # Save summary
    out_path = BASE_DIR / "results" / "g2_pca_representation_evaluation.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "validation_g2": res_val_g2,
            "test_g2": res_test_g2,
            "test_g1": res_test_g1
        }, f, indent=2)
    print(f"\n[OK] Saved evaluation results to {out_path}")


if __name__ == "__main__":
    main()
