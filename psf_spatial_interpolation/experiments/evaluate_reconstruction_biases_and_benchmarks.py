"""
Comprehensive numerical analysis of PSF reconstruction accuracy and systematic biases:
1. Individual component-wise RMSEs for e1 and e2.
2. Squared-size RMSE for R^2 in pixel^2.
3. Additive biases c1, c2 and multiplicative biases m1, m2 from:
     e_hat_j - e_j = m_j * e_j + c_j + epsilon_j
4. Mean fractional size bias:
     b_R2 = <(R^2_hat - R^2) / R^2>
5. Standard errors and 95% confidence intervals for all bias parameters.
6. Reference variance and distribution metrics across 200 held-out test positions.
7. Evaluated across all three PSF families:
   - G1: Smooth Moffat (K=5)
   - G2: Optical + atmospheric (K=8 validated)
   - S1: Diffraction-based (K=9 validated)
8. Evaluates all spatial interpolation models:
   - Polynomial Regression (POLY)
   - Inverse Distance Weighting (IDW)
   - Radial Basis Function (RBF - Thin Plate Spline)
   - Ordinary Kriging (OK)
   - Universal Kriging - Linear (UK-Lin)
   - Universal Kriging - Quadratic (UK-Quad)
   - Random Forest (RF)
   - Multilayer Perceptron (MLP)
9. Exports:
   - results/comprehensive_reconstruction_benchmarks.json
   - results/per_position_test_predictions.npz
   - results/reconstruction_bias_benchmark_table.md
"""

import json
from pathlib import Path
import sys
from typing import Any
import numpy as np
import scipy.stats as stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.dataset import load_dataset
from representation.pca import PSFRepresentation
from reconstruction.psf import reconstruct_psfs_from_coefficients
from validation.moments import measure_psf_batch
from validation.metrics import compute_representation_error
from interpolation.classical import PolynomialInterpolator, IDWInterpolator, RBFInterpolator
from interpolation.kriging import OrdinaryKrigingInterpolator, UniversalKrigingInterpolator
from interpolation.ml import RandomForestInterpolator, MLPInterpolator


def fit_linear_bias(true_val: np.ndarray, pred_val: np.ndarray) -> dict:
    """
    Fit linear regression:
        (pred_val - true_val) = m * true_val + c + epsilon
    Equivalent to:
        pred_val = (1 + m) * true_val + c + epsilon
    """
    x = np.asarray(true_val, dtype=np.float64)
    y = np.asarray(pred_val - true_val, dtype=np.float64)
    n = len(x)

    x_bar = np.mean(x)
    y_bar = np.mean(y)
    sxx = np.sum((x - x_bar) ** 2)
    sxy = np.sum((x - x_bar) * (y - y_bar))

    if sxx > 1e-15:
        m = float(sxy / sxx)
        c = float(y_bar - m * x_bar)
    else:
        m = 0.0
        c = float(y_bar)

    residuals = y - (m * x + c)
    df = max(n - 2, 1)
    s2 = float(np.sum(residuals ** 2) / df)

    if sxx > 1e-15:
        se_m = float(np.sqrt(s2 / sxx))
        se_c = float(np.sqrt(s2 * (1.0 / n + (x_bar ** 2) / sxx)))
    else:
        se_m = 0.0
        se_c = float(np.sqrt(s2 / n))

    t_crit = float(stats.t.ppf(0.975, df=df))
    ci_m = [float(m - t_crit * se_m), float(m + t_crit * se_m)]
    ci_c = [float(c - t_crit * se_c), float(c + t_crit * se_c)]

    rmse = float(np.sqrt(np.mean((pred_val - true_val) ** 2)))

    return {
        "m": m,
        "se_m": se_m,
        "ci_m_95": ci_m,
        "c": c,
        "se_c": se_c,
        "ci_c_95": ci_c,
        "rmse": rmse,
        "residual_std": float(np.sqrt(s2))
    }


def compute_fractional_size_bias(true_r2: np.ndarray, pred_r2: np.ndarray) -> dict:
    """
    Compute mean fractional size bias:
        b_R2 = <(pred_r2 - true_r2) / true_r2>
    and squared-size RMSE in pixel^2.
    """
    t = np.asarray(true_r2, dtype=np.float64)
    p = np.asarray(pred_r2, dtype=np.float64)
    n = len(t)

    delta_r2 = p - t
    frac_err = delta_r2 / t

    b_r2 = float(np.mean(frac_err))
    df = max(n - 1, 1)
    std_frac = float(np.std(frac_err, ddof=1))
    se_b_r2 = float(std_frac / np.sqrt(n))

    t_crit = float(stats.t.ppf(0.975, df=df))
    ci_b_r2 = [float(b_r2 - t_crit * se_b_r2), float(b_r2 + t_crit * se_b_r2)]

    rmse_r2 = float(np.sqrt(np.mean(delta_r2 ** 2)))
    mean_r2 = float(np.mean(t))
    rel_size_rmse = float(rmse_r2 / mean_r2)

    return {
        "b_r2": b_r2,
        "se_b_r2": se_b_r2,
        "ci_b_r2_95": ci_b_r2,
        "rmse_r2": rmse_r2,
        "rel_size_rmse": rel_size_rmse
    }


def run_comprehensive_analysis():
    print("================================================================================")
    print("PSF SPATIAL INTERPOLATION: ACCURACY & SYSTEMATIC BIAS BENCHMARK")
    print("================================================================================")

    scenarios = [
        {
            "name": "G1",
            "field_dir": "data/field_000",
            "description": "Ground-based (smooth Moffat)",
            "k_eval": 5,
            "models_config": [
                ("Polynomial (POLY)", "Deterministic / Classical", PolynomialInterpolator, {"degree": 2}),
                ("Inverse Distance Weighting (IDW)", "Deterministic / Classical", IDWInterpolator, {"power": 4.0}),
                ("Radial Basis Function (RBF - TPS)", "Deterministic / Spline", RBFInterpolator, {"smoothing": 1e-8}),
                ("Ordinary Kriging (OK)", "Geostatistical (Constant)", OrdinaryKrigingInterpolator, {}),
                ("Universal Kriging - Linear (UK-Lin)", "Geostatistical (Linear Drift)", UniversalKrigingInterpolator, {"trend": "linear"}),
                ("Universal Kriging - Quadratic (UK-Quad)", "Geostatistical (Quadratic Drift)", UniversalKrigingInterpolator, {"trend": "quadratic"}),
                ("Random Forest (RF)", "Machine Learning (Trees)", RandomForestInterpolator, {"n_estimators": 100, "max_depth": 10, "min_samples_leaf": 1}),
                ("Multilayer Perceptron (MLP)", "Machine Learning (Neural)", MLPInterpolator, {"hidden_layer_sizes": (64, 32), "activation": "tanh", "alpha": 0.01})
            ]
        },
        {
            "name": "G2",
            "field_dir": "data/field_g2",
            "description": "Ground-based (optical + atmospheric)",
            "k_eval": 8,
            "models_config": [
                ("Polynomial (POLY)", "Deterministic / Classical", PolynomialInterpolator, {"degree": 3}),
                ("Inverse Distance Weighting (IDW)", "Deterministic / Classical", IDWInterpolator, {"power": 4.0}),
                ("Radial Basis Function (RBF - TPS)", "Deterministic / Spline", RBFInterpolator, {"smoothing": 1e-8}),
                ("Ordinary Kriging (OK)", "Geostatistical (Constant)", OrdinaryKrigingInterpolator, {}),
                ("Universal Kriging - Linear (UK-Lin)", "Geostatistical (Linear Drift)", UniversalKrigingInterpolator, {"trend": "linear"}),
                ("Universal Kriging - Quadratic (UK-Quad)", "Geostatistical (Quadratic Drift)", UniversalKrigingInterpolator, {"trend": "quadratic"}),
                ("Random Forest (RF)", "Machine Learning (Trees)", RandomForestInterpolator, {"n_estimators": 200, "max_depth": 12, "min_samples_leaf": 1}),
                ("Multilayer Perceptron (MLP)", "Machine Learning (Neural)", MLPInterpolator, {"hidden_layer_sizes": (32, 32), "activation": "tanh", "alpha": 0.05})
            ]
        },
        {
            "name": "S1",
            "field_dir": "data/field_s1",
            "description": "Space-based (diffraction)",
            "k_eval": 9,
            "models_config": [
                ("Polynomial (POLY)", "Deterministic / Classical", PolynomialInterpolator, {"degree": 4}),
                ("Inverse Distance Weighting (IDW)", "Deterministic / Classical", IDWInterpolator, {"power": 4.0}),
                ("Radial Basis Function (RBF - TPS)", "Deterministic / Spline", RBFInterpolator, {"smoothing": 1e-8}),
                ("Ordinary Kriging (OK)", "Geostatistical (Constant)", OrdinaryKrigingInterpolator, {}),
                ("Universal Kriging - Linear (UK-Lin)", "Geostatistical (Linear Drift)", UniversalKrigingInterpolator, {"trend": "linear"}),
                ("Universal Kriging - Quadratic (UK-Quad)", "Geostatistical (Quadratic Drift)", UniversalKrigingInterpolator, {"trend": "quadratic"}),
                ("Random Forest (RF)", "Machine Learning (Trees)", RandomForestInterpolator, {"n_estimators": 200, "max_depth": 12, "min_samples_leaf": 1}),
                ("Multilayer Perceptron (MLP)", "Machine Learning (Neural)", MLPInterpolator, {"hidden_layer_sizes": (32, 16), "activation": "tanh", "alpha": 0.001})
            ]
        }
    ]

    all_results = []
    npz_data = {}
    ref_summaries = {}

    for sc in scenarios:
        sc_name = sc["name"]
        field_dir = PROJECT_ROOT / sc["field_dir"]
        k = sc["k_eval"]
        print(f"\n================================================================================")
        print(f"EVALUATING SCENARIO {sc_name} ({sc['description']}) [K = {k}]")
        print(f"================================================================================")

        dataset = load_dataset(str(field_dir))
        pos_train = dataset.positions_train
        pos_test = dataset.positions_test
        psf_train = dataset.psfs_train_observed
        psf_test = dataset.psfs_test_true

        true_e1 = dataset.true_test_e1
        true_e2 = dataset.true_test_e2
        true_r2 = dataset.true_test_r2

        # 1. Reference property distributions
        ref_stats = {
            "e1": {
                "mean": float(np.mean(true_e1)),
                "std": float(np.std(true_e1)),
                "var": float(np.var(true_e1)),
                "min": float(np.min(true_e1)),
                "max": float(np.max(true_e1)),
                "range": float(np.ptp(true_e1))
            },
            "e2": {
                "mean": float(np.mean(true_e2)),
                "std": float(np.std(true_e2)),
                "var": float(np.var(true_e2)),
                "min": float(np.min(true_e2)),
                "max": float(np.max(true_e2)),
                "range": float(np.ptp(true_e2))
            },
            "r2": {
                "mean": float(np.mean(true_r2)),
                "std": float(np.std(true_r2)),
                "var": float(np.var(true_r2)),
                "min": float(np.min(true_r2)),
                "max": float(np.max(true_r2)),
                "range": float(np.ptp(true_r2))
            }
        }
        ref_summaries[sc_name] = ref_stats

        print(f"Reference e1: mean={ref_stats['e1']['mean']:+.4f}, std={ref_stats['e1']['std']:.4f}, var={ref_stats['e1']['var']:.2e}, range=[{ref_stats['e1']['min']:+.4f}, {ref_stats['e1']['max']:+.4f}]")
        print(f"Reference e2: mean={ref_stats['e2']['mean']:+.4f}, std={ref_stats['e2']['std']:.4f}, var={ref_stats['e2']['var']:.2e}, range=[{ref_stats['e2']['min']:+.4f}, {ref_stats['e2']['max']:+.4f}]")
        print(f"Reference R2: mean={ref_stats['r2']['mean']:.4f}, std={ref_stats['r2']['std']:.4f}, var={ref_stats['r2']['var']:.2e}, range=[{ref_stats['r2']['min']:.4f}, {ref_stats['r2']['max']:.4f}]")

        npz_data[f"{sc_name}_pos_test"] = pos_test
        npz_data[f"{sc_name}_true_e1"] = true_e1
        npz_data[f"{sc_name}_true_e2"] = true_e2
        npz_data[f"{sc_name}_true_r2"] = true_r2

        # 2. Fit PCA on training stars
        pca = PSFRepresentation(n_components_max=k)
        pca.fit(psf_train)
        train_coeffs = pca.transform(psf_train, n_components=k)

        # Baseline PCA truncation error (E_rep)
        test_coeffs_direct = pca.transform(psf_test, n_components=k)
        rec_trunc = reconstruct_psfs_from_coefficients(test_coeffs_direct, pca, physical_adjustment=True)
        e_rep_limit = compute_representation_error(psf_test, rec_trunc)
        print(f"PCA representation limit (K={k}): E_rep = {e_rep_limit*100:.4f}%")

        # 3. Evaluate each model
        models_config: list[tuple[str, str, Any, dict[str, Any]]] = sc["models_config"]
        for model_name, category, factory, params in models_config:
            model = factory(**params)
            model.fit(pos_train, train_coeffs)
            pred_coeffs = model.predict(pos_test)

            pred_psfs = reconstruct_psfs_from_coefficients(pred_coeffs, pca, physical_adjustment=True)
            p_e1, p_e2, p_r2 = measure_psf_batch(pred_psfs, sigma_w=3.5)

            rec_error = compute_representation_error(psf_test, pred_psfs)
            pixel_rmse = float(np.sqrt(np.mean((psf_test - pred_psfs) ** 2)))

            bias_e1 = fit_linear_bias(true_e1, p_e1)
            bias_e2 = fit_linear_bias(true_e2, p_e2)
            bias_r2 = compute_fractional_size_bias(true_r2, p_r2)

            rmse_e1 = bias_e1["rmse"]
            rmse_e2 = bias_e2["rmse"]
            combined_rmse_e = float(np.sqrt(rmse_e1 ** 2 + rmse_e2 ** 2))

            # Store per-position predictions for this model
            clean_name = model_name.split()[0].replace("-", "_").lower()
            if "UK" in model_name:
                clean_name = "uk_quad" if "Quadratic" in model_name else "uk_lin"
            key_prefix = f"{sc_name}_{clean_name}"

            npz_data[f"{key_prefix}_pred_e1"] = p_e1
            npz_data[f"{key_prefix}_pred_e2"] = p_e2
            npz_data[f"{key_prefix}_pred_r2"] = p_r2
            npz_data[f"{key_prefix}_delta_e1"] = p_e1 - true_e1
            npz_data[f"{key_prefix}_delta_e2"] = p_e2 - true_e2
            npz_data[f"{key_prefix}_delta_r2"] = p_r2 - true_r2

            res_entry = {
                "scenario": sc_name,
                "scenario_description": sc["description"],
                "k_pca": k,
                "model_name": model_name,
                "category": category,
                "hyperparameters": params,
                "e_rec": rec_error,
                "pixel_rmse": pixel_rmse,
                "rmse_e1": rmse_e1,
                "rmse_e2": rmse_e2,
                "combined_rmse_e": combined_rmse_e,
                "rmse_r2": bias_r2["rmse_r2"],
                "rel_size_rmse": bias_r2["rel_size_rmse"],
                "b_r2": bias_r2["b_r2"],
                "se_b_r2": bias_r2["se_b_r2"],
                "ci_b_r2_95": bias_r2["ci_b_r2_95"],
                "m1": bias_e1["m"],
                "se_m1": bias_e1["se_m"],
                "ci_m1_95": bias_e1["ci_m_95"],
                "c1": bias_e1["c"],
                "se_c1": bias_e1["se_c"],
                "ci_c1_95": bias_e1["ci_c_95"],
                "m2": bias_e2["m"],
                "se_m2": bias_e2["se_m"],
                "ci_m2_95": bias_e2["ci_m_95"],
                "c2": bias_e2["c"],
                "se_c2": bias_e2["se_c"],
                "ci_c2_95": bias_e2["ci_c_95"],
                "ref_variance_e1": ref_stats["e1"]["var"],
                "ref_variance_e2": ref_stats["e2"]["var"],
                "ref_variance_r2": ref_stats["r2"]["var"]
            }
            all_results.append(res_entry)

            print(
                f"  {model_name:<36} | "
                f"RMSE(e)={combined_rmse_e*1000:6.3f}e-3 | "
                f"RMSE(R2)={bias_r2['rmse_r2']:7.4f} px^2 | "
                f"m1={bias_e1['m']:+7.4f}+/-{bias_e1['se_m']:6.4f} | "
                f"c1={bias_e1['c']*1e4:+6.2f}e-4 | "
                f"m2={bias_e2['m']:+7.4f}+/-{bias_e2['se_m']:6.4f} | "
                f"c2={bias_e2['c']*1e4:+6.2f}e-4 | "
                f"b_R2={bias_r2['b_r2']*100:+6.3f}% | "
                f"E_rec={rec_error*100:6.3f}%"
            )

    # 4. Save results to JSON
    results_dir = PROJECT_ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    json_path = results_dir / "comprehensive_reconstruction_benchmarks.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "reference_summaries": ref_summaries,
            "results": all_results
        }, f, indent=2)
    print(f"\n[OK] Saved comprehensive JSON benchmark to {json_path}")

    # 5. Save per-position predictions to NPZ
    npz_path = results_dir / "per_position_test_predictions.npz"
    np.savez_compressed(npz_path, **npz_data)
    print(f"[OK] Saved per-position test predictions ({len(npz_data)} arrays) to {npz_path}")

    # 6. Generate Markdown Tables
    generate_markdown_tables(all_results, ref_summaries, results_dir / "reconstruction_bias_benchmark_table.md")

    return all_results, npz_data


def generate_markdown_tables(results: list[dict], ref_summaries: dict, out_md_path: Path):
    """
    Format publication-ready markdown tables:
    1. Table A: 18 combinations (3 scenarios x 6 canonical interpolation methods).
    2. Table B: Full 24 combinations (all 8 models including UK variants).
    3. Reference variance summary table.
    """
    canonical_models = [
        "Polynomial (POLY)",
        "Radial Basis Function (RBF - TPS)",
        "Universal Kriging - Quadratic (UK-Quad)",
        "Ordinary Kriging (OK)",
        "Multilayer Perceptron (MLP)",
        "Inverse Distance Weighting (IDW)",
        "Random Forest (RF)"
    ]

    lines = []
    lines.append("# Reconstruction Accuracy and Systematic Biases Benchmark\n")
    lines.append("Benchmark evaluating 200 independent test stars across the three observing scenarios:\n")
    lines.append("- **G1**: Ground-based, smooth Moffat field ($K = 5$)")
    lines.append("- **G2**: Ground-based, optical aberrations + correlated atmospheric variations ($K = 8$)")
    lines.append("- **S1**: Space-based, diffraction optics from obscured pupil + Zernike aberrations ($K = 9$)\n")

    lines.append("## 1. Reference PSF Property Distributions (200 Test Positions)\n")
    lines.append("| Scenario | Property | Mean | Std Dev | Variance | Min | Max | Range |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for sc, data in ref_summaries.items():
        lines.append(f"| **{sc}** | $e_1$ | {data['e1']['mean']:+.4f} | {data['e1']['std']:.4f} | {data['e1']['var']:.2e} | {data['e1']['min']:+.4f} | {data['e1']['max']:+.4f} | {data['e1']['range']:.4f} |")
        lines.append(f"| **{sc}** | $e_2$ | {data['e2']['mean']:+.4f} | {data['e2']['std']:.4f} | {data['e2']['var']:.2e} | {data['e2']['min']:+.4f} | {data['e2']['max']:+.4f} | {data['e2']['range']:.4f} |")
        lines.append(f"| **{sc}** | $R^2$ (px²) | {data['r2']['mean']:.4f} | {data['r2']['std']:.4f} | {data['r2']['var']:.2e} | {data['r2']['min']:.4f} | {data['r2']['max']:.4f} | {data['r2']['range']:.4f} |")
    lines.append("\n---\n")

    lines.append("## 2. Benchmark Table: 21 Combinations (3 Scenarios × 7 Interpolation Methods)\n")
    lines.append("| Scenario | Algorithm | $E_{\\mathrm{rec}}$ (%) | $\\mathrm{RMSE}(e_1)$ (×10⁻³) | $\\mathrm{RMSE}(e_2)$ (×10⁻³) | Combined $\\mathrm{RMSE}(e)$ (×10⁻³) | $\\mathrm{RMSE}(R^2)$ (px²) | $m_1$ (×10⁻²) | $c_1$ (×10⁻⁴) | $m_2$ (×10⁻²) | $c_2$ (×10⁻⁴) | $b_{R^2}$ (%) |")
    lines.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    # Filter to 21 combinations
    for sc in ["G1", "G2", "S1"]:
        sc_res = [r for r in results if r["scenario"] == sc and r["model_name"] in canonical_models]
        # Sort by combined RMSE(e)
        sc_res_sorted = sorted(sc_res, key=lambda x: x["combined_rmse_e"])
        for r in sc_res_sorted:
            m_short = r["model_name"].split(" (")[0]
            lines.append(
                f"| **{sc}** | {m_short} "
                f"| {r['e_rec']*100:.3f}% "
                f"| {r['rmse_e1']*1000:.3f} "
                f"| {r['rmse_e2']*1000:.3f} "
                f"| **{r['combined_rmse_e']*1000:.3f}** "
                f"| {r['rmse_r2']:.4f} "
                f"| {r['m1']*100:+.2f} ± {r['se_m1']*100:.2f} "
                f"| {r['c1']*10000:+.2f} ± {r['se_c1']*10000:.2f} "
                f"| {r['m2']*100:+.2f} ± {r['se_m2']*100:.2f} "
                f"| {r['c2']*10000:+.2f} ± {r['se_c2']*10000:.2f} "
                f"| {r['b_r2']*100:+.3f}% ± {r['se_b_r2']*100:.3f}% |"
            )
    lines.append("\n---\n")

    lines.append("## 3. Comprehensive Benchmark Table: All 24 Configurations (Including UK Variants)\n")
    lines.append("| Scenario | Algorithm | Category | $E_{\\mathrm{rec}}$ (%) | $\\mathrm{RMSE}(e)$ (×10⁻³) | $\\mathrm{RMSE}(R^2)$ (px²) | $m_1$ (×10⁻²) | $c_1$ (×10⁻⁴) | $m_2$ (×10⁻²) | $c_2$ (×10⁻⁴) | $b_{R^2}$ (%) |")
    lines.append("| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    for sc in ["G1", "G2", "S1"]:
        sc_res = [r for r in results if r["scenario"] == sc]
        sc_res_sorted = sorted(sc_res, key=lambda x: x["combined_rmse_e"])
        for r in sc_res_sorted:
            lines.append(
                f"| **{sc}** | {r['model_name']} | {r['category']} "
                f"| {r['e_rec']*100:.3f}% "
                f"| **{r['combined_rmse_e']*1000:.3f}** "
                f"| {r['rmse_r2']:.4f} "
                f"| {r['m1']*100:+.2f} ± {r['se_m1']*100:.2f} "
                f"| {r['c1']*10000:+.2f} ± {r['se_c1']*10000:.2f} "
                f"| {r['m2']*100:+.2f} ± {r['se_m2']*100:.2f} "
                f"| {r['c2']*10000:+.2f} ± {r['se_c2']*10000:.2f} "
                f"| {r['b_r2']*100:+.3f}% ± {r['se_b_r2']*100:.3f}% |"
            )

    out_md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Saved markdown comparison table to {out_md_path}")


if __name__ == "__main__":
    run_comprehensive_analysis()
