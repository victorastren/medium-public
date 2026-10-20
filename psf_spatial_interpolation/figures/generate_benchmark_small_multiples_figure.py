"""
Generate figure: Benchmark Results Small Multiples.
Compares interpolation methods across Scenarios G1, G2, and S1.
Layout:
Columns: G1 (Smooth Moffat), G2 (Optical + Turbulence), S1 (Space Diffraction).
Rows:
1. Ellipticity Component e1 RMSE (x10^-3)
2. Ellipticity Component e2 RMSE (x10^-3)
3. Squared-Size RMSE R^2 (px^2)
4. Total Image Reconstruction Error E_rec (%)

Each column has independent linear axes, allowing direct, uncrowded method comparisons
within each scenario without compressing G1 into invisibility.

Adheres to RULE 4: Clean Unicode typography, no LaTeX math in captions/text.
"""

import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
results_json = PROJECT_ROOT / "results" / "comprehensive_reconstruction_benchmarks.json"
output_png = PROJECT_ROOT / "images" / "benchmark_small_multiples.png"

with open(results_json, "r", encoding="utf-8") as f:
    benchmark_data = json.load(f)["results"]

# Canonical methods in intuitive logical order
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
    ("G1", r"G1: Smooth Moffat ($K = 5$)"),
    ("G2", r"G2: Ground Optical + Turbulence ($K = 8$)"),
    ("S1", r"S1: Space Diffraction Optics ($K = 9$)"),
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
    "mathtext.fontset": "dejavusans",
    "axes.edgecolor": "#333333",
    "axes.linewidth": 1.15,
    "axes.labelcolor": "#111111",
    "xtick.color": "#222222",
    "ytick.color": "#222222",
})

fig, axes = plt.subplots(4, 3, figsize=(18.0, 13.5), dpi=300)
plt.subplots_adjust(left=0.14, right=0.97, bottom=0.06, top=0.91, wspace=0.28, hspace=0.38)

y_indices = np.arange(len(model_configs))
labels = [name for _, name, _ in model_configs]
colors = [c for _, _, c in model_configs]

metric_rows = [
    {
        "row_idx": 0,
        "key": "rmse_e1",
        "scale": 1e3,
        "title": r"Ellipticity Component $e_1$ RMSE",
        "unit": r"$(\times 10^{-3})$",
        "fmt": "{:.3f}",
    },
    {
        "row_idx": 1,
        "key": "rmse_e2",
        "scale": 1e3,
        "title": r"Ellipticity Component $e_2$ RMSE",
        "unit": r"$(\times 10^{-3})$",
        "fmt": "{:.3f}",
    },
    {
        "row_idx": 2,
        "key": "rmse_r2",
        "scale": 1.0,
        "title": r"Squared-Size RMSE ($R^2$)",
        "unit": r"$(\mathrm{px}^2)$",
        "fmt": "{:.4f}",
    },
    {
        "row_idx": 3,
        "key": "e_rec",
        "scale": 100.0,
        "title": r"Total Image Error $E_{\mathrm{rec}}$",
        "unit": "(%)",
        "fmt": "{:.3f}%",
    },
]

for col_idx, (sc_key, sc_title) in enumerate(scenarios):
    for mr in metric_rows:
        row_idx = mr["row_idx"]
        ax = axes[row_idx, col_idx]

        # Extract values
        vals = []
        for full_name, _, _ in model_configs:
            d = find_entry(sc_key, full_name)
            vals.append(d[mr["key"]] * mr["scale"])

        # Horizontal bars
        bars = ax.barh(y_indices, vals, color=colors, height=0.68,
                       edgecolor="#222222", linewidth=0.8, alpha=0.92, zorder=3)

        # Annotations on bars
        max_val = max(vals)
        for bar, val in zip(bars, vals):
            w = bar.get_width()
            # If bar is very small, place text outside
            offset = max_val * 0.02
            ax.text(w + offset, bar.get_y() + bar.get_height() / 2.0,
                    mr["fmt"].format(val),
                    va="center", ha="left", fontsize=9.0, fontweight="bold", color="#222222")

        ax.set_xlim(0, max_val * 1.25)
        ax.set_yticks(y_indices)
        if col_idx == 0:
            ax.set_yticklabels(labels, fontsize=11.5, fontweight="bold")
            ax.set_ylabel(f"{mr['title']}\n{mr['unit']}", fontsize=11.5, fontweight="bold", labelpad=8)
        else:
            ax.set_yticklabels([])

        ax.grid(True, axis="x", linestyle="--", alpha=0.45, color="#c5c5c5", zorder=1)
        ax.tick_params(axis="both", labelsize=10.0)
        ax.invert_yaxis()  # Best on top

        # Column header on top row
        if row_idx == 0:
            ax.set_title(sc_title, fontsize=13.5, fontweight="bold", pad=12, color="#111111")

        # Row label on x-axis
        ax.set_xlabel(f"{mr['unit']}", fontsize=10.0, fontweight="bold", labelpad=4)

# Overarching title
fig.suptitle("PSF Reconstruction Benchmark: Error Breakdown across Observing Scenarios",
             fontsize=17.5, fontweight="bold", x=0.55, y=0.97, color="#111111")

output_png.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(output_png, dpi=300, bbox_inches="tight")
plt.close()
print(f"Benchmark small multiples saved to {output_png}")
