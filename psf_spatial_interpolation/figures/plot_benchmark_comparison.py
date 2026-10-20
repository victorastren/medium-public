"""
Plot comparative benchmark results across the spatial interpolation algorithms.
Includes Ordinary Kriging and Universal Kriging (Linear and Quadratic drift).
Produces publication-grade figures for the Medium article with clean typography.
"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
results_json = PROJECT_ROOT / "results" / "baseline_reconstruction_benchmark.json"
output_img = PROJECT_ROOT / "images" / "baseline_algorithm_comparison.png"

with open(results_json, "r", encoding="utf-8") as f:
    data = json.load(f)

label_map = {
    "Polynomial (POLY)": "Polynomial",
    "Radial Basis Function (RBF - TPS)": "RBF\nSpline",
    "Multilayer Perceptron (MLP)": "MLP\nNeural Net",
    "Ordinary Kriging (OK)": "Ordinary\nKriging",
    "Universal Kriging - Linear (UK-Lin)": "UK\n(Linear)",
    "Universal Kriging - Quadratic (UK-Quad)": "UK\n(Quadratic)",
    "Random Forest (RF)": "Random\nForest",
    "Inverse Distance Weighting (IDW)": "IDW"
}

# Sort data by test reconstruction error E_rec ascending
sorted_data = sorted(data, key=lambda x: x["test_rec_error"])

models = [label_map.get(d["model_name"], d["model_name"]) for d in sorted_data]
e_rmse = [d["test_e_rmse"] * 1e3 for d in sorted_data]  # milli
r2_rmse = [d["test_r2_rmse"] for d in sorted_data]
e_rec_pct = [d["test_rec_error"] * 100.0 for d in sorted_data]
base_rep_pct = 0.0147  # E_rep limit

# Color palette by family
palette = {
    "Polynomial": "#2b5c8f",
    "RBF\nSpline": "#1f77b4",
    "MLP\nNeural Net": "#2ca02c",
    "Ordinary\nKriging": "#ff7f0e",
    "UK\n(Linear)": "#d95f02",
    "UK\n(Quadratic)": "#fdb863",
    "IDW": "#d62728",
    "Random\nForest": "#9467bd"
}
colors = [palette.get(m, "#4a7bb0") for m in models]

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(19.0, 7.4), dpi=280)
plt.subplots_adjust(bottom=0.25, top=0.88, wspace=0.32, left=0.06, right=0.97)

# 1. Ellipticity Error
bars1 = ax1.bar(models, e_rmse, color=colors, width=0.60, edgecolor="#222222", linewidth=1.2)
ax1.set_title(r"Ellipticity Error $\mathrm{RMSE}(e)$", fontsize=18, fontweight="bold", pad=14)
ax1.set_ylabel(r"$\mathrm{RMSE}(e)\;(\times 10^{-3})$", fontsize=15, fontweight="bold", labelpad=8)
ax1.tick_params(axis="y", labelsize=13)
ax1.set_xticks(range(len(models)))
ax1.set_xticklabels(models, rotation=25, ha="right", fontsize=13.5, fontweight="bold")
ax1.grid(axis="y", linestyle="--", alpha=0.35)

for idx, bar in enumerate(bars1):
    y = bar.get_height()
    # Stagger slightly if consecutive bars are very close
    offset = 0.05 if idx % 2 == 0 else 0.12
    ax1.text(bar.get_x() + bar.get_width() / 2.0, y + offset, f"{y:.2f}",
             ha="center", va="bottom", fontsize=11.5, fontweight="bold")
ax1.set_ylim(0, max(e_rmse) * 1.20)

# 2. Size Error
bars2 = ax2.bar(models, r2_rmse, color=colors, width=0.60, edgecolor="#222222", linewidth=1.2)
ax2.set_title(r"PSF Size Error $\mathrm{RMSE}(R^2)$", fontsize=18, fontweight="bold", pad=14)
ax2.set_ylabel(r"$\mathrm{RMSE}(R^2)\;(\mathrm{pixels}^2)$", fontsize=15, fontweight="bold", labelpad=8)
ax2.tick_params(axis="y", labelsize=13)
ax2.set_xticks(range(len(models)))
ax2.set_xticklabels(models, rotation=25, ha="right", fontsize=13.5, fontweight="bold")
ax2.grid(axis="y", linestyle="--", alpha=0.35)

for idx, bar in enumerate(bars2):
    y = bar.get_height()
    offset = 0.0004 if idx % 2 == 0 else 0.0010
    ax2.text(bar.get_x() + bar.get_width() / 2.0, y + offset, f"{y:.4f}",
             ha="center", va="bottom", fontsize=11.5, fontweight="bold")
ax2.set_ylim(0, max(r2_rmse) * 1.20)

# 3. Total Reconstruction Error E_rec vs PCA Lower Bound
bars3 = ax3.bar(models, e_rec_pct, color=colors, width=0.60, edgecolor="#222222", linewidth=1.2)
ax3.axhline(base_rep_pct, color="#d62728", linestyle="--", linewidth=2.0,
            label=f"PCA Bound ({base_rep_pct:.3f}%)")
ax3.set_title(r"Total Reconstruction Error $E_{\mathrm{rec}}$", fontsize=18, fontweight="bold", pad=14)
ax3.set_ylabel(r"Normalized $L_2$ Error (%)", fontsize=15, fontweight="bold", labelpad=8)
ax3.tick_params(axis="y", labelsize=13)
ax3.set_xticks(range(len(models)))
ax3.set_xticklabels(models, rotation=25, ha="right", fontsize=13.5, fontweight="bold")
ax3.grid(axis="y", linestyle="--", alpha=0.35)
ax3.legend(loc="upper left", fontsize=13, framealpha=0.92)

for idx, bar in enumerate(bars3):
    y = bar.get_height()
    offset = 0.010 if idx % 2 == 0 else 0.024
    ax3.text(bar.get_x() + bar.get_width() / 2.0, y + offset, f"{y:.3f}%",
             ha="center", va="bottom", fontsize=11.5, fontweight="bold")
ax3.set_ylim(0, max(e_rec_pct) * 1.25)

for ax in (ax1, ax2, ax3):
    for spine in ax.spines.values():
        spine.set_linewidth(1.3)

plt.savefig(output_img, bbox_inches="tight")
plt.close(fig)
print(f"[OK] Saved {output_img}")
