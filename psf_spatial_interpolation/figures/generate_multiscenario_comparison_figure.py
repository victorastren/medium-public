"""
Generate figure comparing reconstruction errors across
Scenarios G1 (Smooth Moffat), G2 (Moffat + Turbulence), and S1 (Space Diffraction).
Arranged vertically (2 panels stacked) for Medium 680px layout.
Cosmetics: Larger method label font size, 2-line split for long method names.
Complies with RULE 4: No LaTeX math in captions or figure text; clean Unicode typography.
"""

import sys
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Load benchmark results
results_dir = BASE_DIR / "results"
with open(results_dir / "baseline_reconstruction_benchmark.json") as f:
    res_g1 = json.load(f)
with open(results_dir / "g2_benchmark_k8.json") as f:
    res_g2 = json.load(f)
with open(results_dir / "s1_benchmark_k9.json") as f:
    res_s1 = json.load(f)

# Models to display in order of presentation
model_keys = [
    ("Polynomial (POLY)", "Polynomial"),
    ("Radial Basis Function (RBF - TPS)", "RBF\nSpline"),
    ("Ordinary Kriging (OK)", "Ordinary\nKriging"),
    ("Universal Kriging - Quadratic (UK-Quad)", "Universal\nKriging"),
    ("Multilayer Perceptron (MLP)", "MLP"),
    ("Inverse Distance Weighting (IDW)", "IDW")
]

algorithms_display = [display for _, display in model_keys]

def extract_metric(res_list, full_name, metric_key):
    for r in res_list:
        if r["model_name"] == full_name:
            return r[metric_key]
    raise ValueError(f"Model {full_name} not found")

# Extract metrics
e_rmse_g1 = [extract_metric(res_g1, full, "test_e_rmse") * 1e3 for full, _ in model_keys]
e_rmse_g2 = [extract_metric(res_g2, full, "test_e_rmse") * 1e3 for full, _ in model_keys]
e_rmse_s1 = [extract_metric(res_s1, full, "test_e_rmse") * 1e3 for full, _ in model_keys]

erec_g1 = [extract_metric(res_g1, full, "test_rec_error") * 100 for full, _ in model_keys]
erec_g2 = [extract_metric(res_g2, full, "test_rec_error") * 100 for full, _ in model_keys]
erec_s1 = [extract_metric(res_s1, full, "test_rec_error") * 100 for full, _ in model_keys]

# Figure styling
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "axes.edgecolor": "#333333",
    "axes.linewidth": 1.15,
})

# Vertical 2-panel figure optimized for 680px reading column
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.4, 11.4), dpi=300)

n_models = len(algorithms_display)
x = np.arange(n_models)
bar_width = 0.25

# Curated harmonious color palette
c_g1 = "#20639b"  # Deep Classic Blue
c_g2 = "#d95f02"  # Terracotta / Amber Orange
c_s1 = "#2ca25f"  # Forest Sea Green

# Panel 1: Ellipticity RMSE (log scale)
bars1_g1 = ax1.bar(x - bar_width, e_rmse_g1, width=bar_width, color=c_g1,
                   label=r"G1: Smooth Moffat ($K=5$)", alpha=0.92, edgecolor="#ffffff", linewidth=0.8)
bars1_g2 = ax1.bar(x, e_rmse_g2, width=bar_width, color=c_g2,
                   label=r"G2: Ground Optical + Turbulence ($K=8$)", alpha=0.92, edgecolor="#ffffff", linewidth=0.8)
bars1_s1 = ax1.bar(x + bar_width, e_rmse_s1, width=bar_width, color=c_s1,
                   label=r"S1: Space Diffraction Optics ($K=9$)", alpha=0.92, edgecolor="#ffffff", linewidth=0.8)

ax1.set_yscale("log")
ax1.set_ylim(0.025, 60.0)
ax1.set_ylabel(r"Ellipticity RMSE $(\times 10^{-3})$", fontsize=13.0, fontweight="bold", color="#111111")
ax1.set_title("PSF Shape Reconstruction Error across Scenarios", fontsize=14.0, fontweight="bold", pad=12, color="#111111")
ax1.set_xticks(x)
ax1.set_xticklabels(algorithms_display, fontsize=13.5, fontweight="bold", linespacing=1.05)
ax1.grid(axis="y", linestyle="--", alpha=0.45, color="#bbbbbb")
ax1.tick_params(axis="y", labelsize=11.5)

# Annotate values on Panel 1
for bars in [bars1_g1, bars1_g2, bars1_s1]:
    for bar in bars:
        h = bar.get_height()
        if h < 0.1:
            lbl = f"{h:.2f}"
        elif h < 1.0:
            lbl = f"{h:.2f}"
        elif h < 10.0:
            lbl = f"{h:.1f}"
        else:
            lbl = f"{h:.1f}"
        ax1.text(bar.get_x() + bar.get_width() / 2.0, h * 1.25, lbl,
                 ha="center", va="bottom", fontsize=9.2, color="#222222", fontweight="medium")

# Panel 2: Relative Image Reconstruction Error E_rec (%) (log scale)
bars2_g1 = ax2.bar(x - bar_width, erec_g1, width=bar_width, color=c_g1,
                   label=r"G1: Smooth Moffat ($K=5$)", alpha=0.92, edgecolor="#ffffff", linewidth=0.8)
bars2_g2 = ax2.bar(x, erec_g2, width=bar_width, color=c_g2,
                   label=r"G2: Ground Optical + Turbulence ($K=8$)", alpha=0.92, edgecolor="#ffffff", linewidth=0.8)
bars2_s1 = ax2.bar(x + bar_width, erec_s1, width=bar_width, color=c_s1,
                   label=r"S1: Space Diffraction Optics ($K=9$)", alpha=0.92, edgecolor="#ffffff", linewidth=0.8)

ax2.set_yscale("log")
ax2.set_ylim(0.008, 18.0)
ax2.set_ylabel(r"Relative Reconstruction Error $E_{\mathrm{rec}}$ (%)", fontsize=13.0, fontweight="bold", color="#111111")
ax2.set_title("Relative PSF Image Reconstruction Error across Scenarios", fontsize=14.0, fontweight="bold", pad=12, color="#111111")
ax2.set_xticks(x)
ax2.set_xticklabels(algorithms_display, fontsize=13.5, fontweight="bold", linespacing=1.05)
ax2.grid(axis="y", linestyle="--", alpha=0.45, color="#bbbbbb")
ax2.tick_params(axis="y", labelsize=11)

for bars in [bars2_g1, bars2_g2, bars2_s1]:
    for bar in bars:
        h = bar.get_height()
        if h < 0.05:
            lbl = f"{h:.3f}%"
        elif h < 1.0:
            lbl = f"{h:.2f}%"
        else:
            lbl = f"{h:.1f}%"
        ax2.text(bar.get_x() + bar.get_width() / 2.0, h * 1.22, lbl,
                 ha="center", va="bottom", fontsize=8.8, color="#222222", fontweight="medium")

# Single shared legend placed cleanly at the top above both panels
fig.legend([bars1_g1, bars1_g2, bars1_s1],
           [r"G1: Smooth Moffat ($K=5$)", r"G2: Ground Optical + Turbulence ($K=8$)", r"S1: Space Diffraction Optics ($K=9$)"],
           loc="upper center", bbox_to_anchor=(0.5, 0.993), ncol=3,
           fontsize=11.0, framealpha=0.95, edgecolor="#cccccc")

plt.tight_layout(rect=[0.0, 0.0, 1.0, 0.955])

# Save publication figure
out_fig = BASE_DIR / "images" / "multiscenario_reconstruction_comparison.png"
plt.savefig(out_fig, bbox_inches="tight")
plt.close(fig)

print(f"[OK] Saved refined vertical multi-scenario comparison figure with larger labels to: {out_fig}")
