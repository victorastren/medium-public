#!/usr/bin/env python3
"""
Generate figures:
1. benchmark_ellipticity_breakdown.png (Figure 1 in article)
2. benchmark_size_image_breakdown.png (Figure 2 in article)
3. benchmark_small_multiples.png (Full 4-row summary)

Uses LaTeX mathtext for all mathematical expressions:
- e1 and e2 -> $e_1$ and $e_2$
- K=5, K=8, K=9 -> $K=5$, $K=8$, $K=9$
- R^2 -> $R^2$
- E_rec -> $E_{\\mathrm{rec}}$
- x10^-3 -> $\\times 10^{-3}$
- px^2 -> $\\mathrm{px}^2$
- matched x and y axis label font sizes (12.5pt bold)
"""

import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
results_json = PROJECT_ROOT / "results" / "comprehensive_reconstruction_benchmarks.json"
images_dir = PROJECT_ROOT / "images"

with open(results_json, "r", encoding="utf-8") as f:
    benchmark_data = json.load(f)["results"]

model_configs = [
    ("Polynomial (POLY)", "Polynomial", "#2b5c8f"),
    ("Radial Basis Function (RBF - TPS)", "RBF Spline", "#1f77b4"),
    ("Universal Kriging - Quadratic (UK-Quad)", "Universal Kriging", "#fdb863"),
    ("Ordinary Kriging (OK)", "Ordinary Kriging", "#e66101"),
    ("Multilayer Perceptron (MLP)", "MLP Neural Net", "#2ca02c"),
    ("Inverse Distance Weighting (IDW)", "IDW", "#d62728"),
    ("Random Forest (RF)", "Random Forest", "#9467bd"),
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

# Global matplotlib styling
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "mathtext.fontset": "dejavusans",
    "axes.edgecolor": "#333333",
    "axes.linewidth": 1.15,
    "axes.labelcolor": "#111111",
    "xtick.color": "#222222",
    "ytick.color": "#222222",
})

y_indices = np.arange(len(model_configs))
labels = [name for _, name, _ in model_configs]
colors = [c for _, _, c in model_configs]

AXIS_LABEL_FONTSIZE = 12.5
TICK_LABEL_FONTSIZE = 10.5
METHOD_LABEL_FONTSIZE = 11.5
BAR_ANNOT_FONTSIZE = 9.5
TITLE_FONTSIZE = 17.5
SUBTITLE_FONTSIZE = 13.5

def plot_2x3_grid(rows_def, super_title, output_filename):
    fig, axes = plt.subplots(2, 3, figsize=(18.0, 7.8), dpi=300)
    plt.subplots_adjust(left=0.14, right=0.97, bottom=0.09, top=0.88, wspace=0.28, hspace=0.36)

    for col_idx, (sc_key, sc_title) in enumerate(scenarios):
        for row_idx, mr in enumerate(rows_def):
            ax = axes[row_idx, col_idx]

            vals = []
            for full_name, _, _ in model_configs:
                d = find_entry(sc_key, full_name)
                vals.append(d[mr["key"]] * mr["scale"])

            bars = ax.barh(y_indices, vals, color=colors, height=0.68,
                           edgecolor="#222222", linewidth=0.8, alpha=0.92, zorder=3)

            max_val = max(vals)
            offset = max_val * 0.02
            for bar, val in zip(bars, vals):
                w = bar.get_width()
                ax.text(w + offset, bar.get_y() + bar.get_height() / 2.0,
                        mr["fmt"].format(val),
                        va="center", ha="left", fontsize=BAR_ANNOT_FONTSIZE, fontweight="bold", color="#111111")

            ax.set_xlim(0, max_val * 1.25)
            ax.set_yticks(y_indices)
            if col_idx == 0:
                ax.set_yticklabels(labels, fontsize=METHOD_LABEL_FONTSIZE, fontweight="bold")
                ax.set_ylabel(mr["y_label"], fontsize=AXIS_LABEL_FONTSIZE, fontweight="bold", labelpad=10)
            else:
                ax.set_yticklabels([])

            ax.grid(True, axis="x", linestyle="--", alpha=0.45, color="#c5c5c5", zorder=1)
            ax.tick_params(axis="both", labelsize=TICK_LABEL_FONTSIZE)
            ax.invert_yaxis()

            if row_idx == 0:
                ax.set_title(sc_title, fontsize=SUBTITLE_FONTSIZE, fontweight="bold", pad=12, color="#111111")

            # X-axis label matching the exact same size as the y-axis label (12.5pt bold)
            ax.set_xlabel(mr["x_label"], fontsize=AXIS_LABEL_FONTSIZE, fontweight="bold", labelpad=6)

    fig.suptitle(super_title, fontsize=TITLE_FONTSIZE, fontweight="bold", x=0.55, y=0.97, color="#111111")

    output_path = images_dir / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Generated {output_path}")

# Figure 1: Ellipticity components e1 and e2
fig1_rows = [
    {
        "key": "rmse_e1",
        "scale": 1e3,
        "y_label": r"Ellipticity Component $e_1$ RMSE" + "\n" + r"$(\times 10^{-3})$",
        "x_label": r"$\mathrm{RMSE}\;(\times 10^{-3})$",
        "fmt": "{:.3f}",
    },
    {
        "key": "rmse_e2",
        "scale": 1e3,
        "y_label": r"Ellipticity Component $e_2$ RMSE" + "\n" + r"$(\times 10^{-3})$",
        "x_label": r"$\mathrm{RMSE}\;(\times 10^{-3})$",
        "fmt": "{:.3f}",
    },
]

# Figure 2: Squared size and relative image error
fig2_rows = [
    {
        "key": "rmse_r2",
        "scale": 1.0,
        "y_label": r"Squared-Size RMSE ($R^2$)" + "\n" + r"$(\mathrm{px}^2)$",
        "x_label": r"Squared-Size RMSE ($R^2$) $(\mathrm{px}^2)$",
        "fmt": "{:.4f}",
    },
    {
        "key": "e_rec",
        "scale": 100.0,
        "y_label": r"Total Image Error $E_{\mathrm{rec}}$" + "\n" + "(%)",
        "x_label": r"Total Image Error $E_{\mathrm{rec}}$ (%)",
        "fmt": "{:.3f}%",
    },
]

if __name__ == "__main__":
    plot_2x3_grid(
        fig1_rows,
        r"PSF Ellipticity Reconstruction Accuracy: $e_1$ and $e_2$ RMSE across Observing Scenarios",
        "benchmark_ellipticity_breakdown.png"
    )
    plot_2x3_grid(
        fig2_rows,
        r"PSF Reconstruction Accuracy: Squared Size and Relative Image Error across Observing Scenarios",
        "benchmark_size_image_breakdown.png"
    )
