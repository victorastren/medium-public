"""
Generate forest plot of systematic PSF reconstruction biases:
Multiplicative bias m, additive bias c, and fractional squared-size bias b_R2
across scenarios G1 (Smooth Moffat), G2 (Optical + Turbulence), and S1 (Space Diffraction).

Columns: G1, G2, S1.
Rows:
1. Multiplicative bias m1 and m2 (%) with 95% confidence intervals
2. Additive bias c1 and c2 (x10^-4) with 95% confidence intervals
3. Fractional squared-size bias b_R2 (%) with 95% confidence intervals

Adheres to RULE 4: Clean Unicode typography, no LaTeX math in captions/text.
"""

import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

PROJECT_ROOT = Path(__file__).resolve().parent.parent
results_json = PROJECT_ROOT / "results" / "comprehensive_reconstruction_benchmarks.json"
output_png = PROJECT_ROOT / "images" / "systematic_biases_forest_plot.png"

with open(results_json, "r", encoding="utf-8") as f:
    benchmark_data = json.load(f)["results"]

# Filter and organize models
model_order = [
    ("Polynomial (POLY)", "Polynomial"),
    ("Radial Basis Function (RBF - TPS)", "RBF Spline"),
    ("Universal Kriging - Quadratic (UK-Quad)", "Universal Kriging"),
    ("Ordinary Kriging (OK)", "Ordinary Kriging"),
    ("Multilayer Perceptron (MLP)", "MLP Neural Net"),
    ("Inverse Distance Weighting (IDW)", "IDW"),
    ("Random Forest (RF)", "Random Forest"),
]

scenarios = [
    ("G1", r"G1: Smooth Moffat ($K=5$)"),
    ("G2", r"G2: Ground-based: optical + atmospheric ($K=8$)"),
    ("S1", r"S1: Space Diffraction Optics ($K=9$)"),
]

def find_entry(scenario_key, model_full_name):
    for entry in benchmark_data:
        if entry["scenario"] == scenario_key and entry["model_name"] == model_full_name:
            return entry
    raise KeyError(f"Not found: {scenario_key}, {model_full_name}")

# Styling
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "axes.edgecolor": "#333333",
    "axes.linewidth": 1.15,
    "axes.labelcolor": "#111111",
    "xtick.color": "#222222",
    "ytick.color": "#222222",
})

# Create 3 rows x 3 columns figure with generous top spacing
fig, axes = plt.subplots(3, 3, figsize=(17.4, 12.8), dpi=300)
plt.subplots_adjust(left=0.14, right=0.97, bottom=0.075, top=0.845, wspace=0.28, hspace=0.38)

y_indices = np.arange(len(model_order))
method_labels = [label for _, label in model_order]

# Palette
c_e1 = "#1f77b4"  # Blue for component 1
c_e2 = "#d95f02"  # Terracotta/orange for component 2
c_r2 = "#2ca02c"  # Emerald green for size

# Row 1: Multiplicative bias m (%)
# Row 2: Additive bias c (x10^-4)
# Row 3: Fractional size bias b_R2 (%)

for col_idx, (sc_key, sc_title) in enumerate(scenarios):
    ax_m = axes[0, col_idx]
    ax_c = axes[1, col_idx]
    ax_r = axes[2, col_idx]

    # Column header
    ax_m.set_title(sc_title, fontsize=14.0, fontweight="bold", pad=12, color="#111111")

    # Reference zero lines
    for ax in [ax_m, ax_c, ax_r]:
        ax.axvline(0, color="#555555", linestyle="--", linewidth=1.4, zorder=1)
        ax.grid(True, axis="x", linestyle=":", alpha=0.55, color="#c5c5c5")
        ax.set_yticks(y_indices)
        if col_idx == 0:
            ax.set_yticklabels(method_labels, fontsize=12.0, fontweight="bold")
        else:
            ax.set_yticklabels([])
        ax.tick_params(axis="both", labelsize=10.5)
        ax.invert_yaxis()  # Order from top to bottom

    # Plot data
    for y_pos, (full_name, _) in enumerate(model_order):
        d = find_entry(sc_key, full_name)

        # Multiplicative bias m1 and m2 (in %)
        m1_pct = d["m1"] * 100.0
        ci_m1_pct = [c * 100.0 for c in d["ci_m1_95"]]
        err_m1_left = m1_pct - ci_m1_pct[0]
        err_m1_right = ci_m1_pct[1] - m1_pct

        m2_pct = d["m2"] * 100.0
        ci_m2_pct = [c * 100.0 for c in d["ci_m2_95"]]
        err_m2_left = m2_pct - ci_m2_pct[0]
        err_m2_right = ci_m2_pct[1] - m2_pct

        # Dodge vertically by +/- 0.16
        ax_m.errorbar(m1_pct, y_pos - 0.16, xerr=[[err_m1_left], [err_m1_right]],
                      fmt="o", color=c_e1, ecolor=c_e1, elinewidth=1.8, capsize=3.5,
                      markersize=6.5, zorder=3)
        ax_m.errorbar(m2_pct, y_pos + 0.16, xerr=[[err_m2_left], [err_m2_right]],
                      fmt="D", color=c_e2, ecolor=c_e2, elinewidth=1.8, capsize=3.5,
                      markersize=6.0, zorder=3)

        # Additive bias c1 and c2 (in 10^-4)
        c1_val = d["c1"] * 1e4
        ci_c1_val = [c * 1e4 for c in d["ci_c1_95"]]
        err_c1_left = c1_val - ci_c1_val[0]
        err_c1_right = ci_c1_val[1] - c1_val

        c2_val = d["c2"] * 1e4
        ci_c2_val = [c * 1e4 for c in d["ci_c2_95"]]
        err_c2_left = c2_val - ci_c2_val[0]
        err_c2_right = ci_c2_val[1] - c2_val

        ax_c.errorbar(c1_val, y_pos - 0.16, xerr=[[err_c1_left], [err_c1_right]],
                      fmt="o", color=c_e1, ecolor=c_e1, elinewidth=1.8, capsize=3.5,
                      markersize=6.5, zorder=3)
        ax_c.errorbar(c2_val, y_pos + 0.16, xerr=[[err_c2_left], [err_c2_right]],
                      fmt="D", color=c_e2, ecolor=c_e2, elinewidth=1.8, capsize=3.5,
                      markersize=6.0, zorder=3)

        # Fractional size bias b_R2 (in %)
        b_r2_pct = d["b_r2"] * 100.0
        ci_b_pct = [c * 100.0 for c in d["ci_b_r2_95"]]
        err_b_left = b_r2_pct - ci_b_pct[0]
        err_b_right = ci_b_pct[1] - b_r2_pct

        ax_r.errorbar(b_r2_pct, y_pos, xerr=[[err_b_left], [err_b_right]],
                      fmt="s", color=c_r2, ecolor=c_r2, elinewidth=1.8, capsize=3.5,
                      markersize=6.5, zorder=3)

    # Set tailored x-limits per column for clear visualization
    if sc_key == "G1":
        ax_m.set_xlim(-4.2, 1.2)
        ax_c.set_xlim(-5.0, 25.0)
        ax_r.set_xlim(-0.06, 0.12)
    elif sc_key == "G2":
        ax_m.set_xlim(-46.0, 4.0)
        ax_c.set_xlim(-16.0, 15.0)
        ax_r.set_xlim(-0.35, 0.35)
    elif sc_key == "S1":
        ax_m.set_xlim(-11.0, 1.5)
        ax_c.set_xlim(-3.0, 6.0)
        ax_r.set_xlim(-0.25, 0.05)

    # Set row-specific axis labels (matched to y-axis label font size: 13.0pt bold)
    ax_m.set_xlabel(r"Multiplicative Bias $m$ (%) [95% CI]", fontsize=13.0, fontweight="bold", labelpad=7)
    ax_c.set_xlabel(r"Additive Bias $c$ ($\times 10^{-4}$) [95% CI]", fontsize=13.0, fontweight="bold", labelpad=7)
    ax_r.set_xlabel(r"Fractional Size Bias $b_{R^2}$ (%) [95% CI]", fontsize=13.0, fontweight="bold", labelpad=7)

# Row title labels on leftmost column
axes[0, 0].set_ylabel(r"Multiplicative Bias ($m$)", fontsize=13.0, fontweight="bold", labelpad=10)
axes[1, 0].set_ylabel(r"Additive Bias ($c$)", fontsize=13.0, fontweight="bold", labelpad=10)
axes[2, 0].set_ylabel(r"Squared-Size Bias ($b_{R^2}$)", fontsize=13.0, fontweight="bold", labelpad=10)

# Overarching legend for components e1, e2, and R2 (enlarged font size)
legend_handles = [
    Line2D([0], [0], marker="o", color=c_e1, label=r"Component 1 ($e_1$)", markersize=9,
           linestyle="", markeredgecolor=c_e1),
    Line2D([0], [0], marker="D", color=c_e2, label=r"Component 2 ($e_2$)", markersize=8.5,
           linestyle="", markeredgecolor=c_e2),
    Line2D([0], [0], marker="s", color=c_r2, label=r"Squared Size ($R^2$)", markersize=9,
           linestyle="", markeredgecolor=c_r2),
    Line2D([0], [0], color="#555555", linestyle="--", lw=1.8, label="Unbiased (zero offset)"),
]

fig.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(0.55, 0.942),
           ncol=4, fontsize=15.5, framealpha=0.95, edgecolor="#cccccc", borderpad=0.5,
           handletextpad=0.6, columnspacing=1.8)

# Overarching title
fig.suptitle("Systematic PSF Reconstruction Biases across Observing Scenarios",
             fontsize=17.5, fontweight="bold", x=0.55, y=0.985, color="#111111")

output_png.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(output_png, dpi=300, bbox_inches="tight")
plt.close()
print(f"Forest plot saved to {output_png}")
