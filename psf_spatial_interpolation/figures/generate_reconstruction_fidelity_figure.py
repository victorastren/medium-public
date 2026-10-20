"""
Generate figure: Reference versus Reconstructed PSF Properties.
Focuses on Scenario G2 (Optical aberrations + atmospheric turbulence, K=8).
Compares three representative methods:
1. Radial Basis Function (RBF Spline) - Minimal bias, tight scatter
2. Ordinary Kriging (OK) - Moderate smoothing/attenuation
3. Polynomial (POLY) - Severe multiplicative attenuation and large scatter

Adheres to RULE 4: Clean Unicode typography, no LaTeX math in captions/text.
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

PROJECT_ROOT = Path(__file__).resolve().parent.parent
data_path = PROJECT_ROOT / "results" / "per_position_test_predictions.npz"
output_png = PROJECT_ROOT / "images" / "reconstruction_fidelity_g2.png"

# Load data
data = np.load(data_path)
true_e1 = data["G2_true_e1"]
true_e2 = data["G2_true_e2"]
true_r2 = data["G2_true_r2"]

# Selected models
models_config = [
    {
        "key": "radial",
        "name": "RBF Spline",
        "color": "#1f77b4",
        "marker": "o",
        "size": 15,
        "alpha": 0.65,
        "edge": "#0b559f",
        "lw": 2.3,
    },
    {
        "key": "uk_quad",
        "name": "Universal Kriging",
        "color": "#8b5cf6",
        "marker": "D",
        "size": 13,
        "alpha": 0.75,
        "edge": "#5b21b6",
        "lw": 2.2,
    },
    {
        "key": "polynomial",
        "name": "Polynomial (deg 3)",
        "color": "#dc2626",
        "marker": "s",
        "size": 11,
        "alpha": 0.50,
        "edge": "#991b1b",
        "lw": 2.2,
    },
]

# Set styling
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "axes.edgecolor": "#333333",
    "axes.linewidth": 1.3,
    "axes.labelcolor": "#111111",
    "xtick.color": "#222222",
    "ytick.color": "#222222",
})

fig, axes = plt.subplots(1, 3, figsize=(18.2, 6.4), dpi=300)
plt.subplots_adjust(left=0.065, right=0.985, bottom=0.13, top=0.85, wspace=0.20)

panels = [
    {
        "ax": axes[0],
        "true": true_e1,
        "title": r"PSF Ellipticity Component $e_1$",
        "unit": "",
        "lims": (-0.058, 0.048),
        "prop_name": "e1",
        "scale_fac": 100.0,
        "has_ylabel": True,
    },
    {
        "ax": axes[1],
        "true": true_e2,
        "title": r"PSF Ellipticity Component $e_2$",
        "unit": "",
        "lims": (-0.050, 0.045),
        "prop_name": "e2",
        "scale_fac": 100.0,
        "has_ylabel": False,
    },
    {
        "ax": axes[2],
        "true": true_r2,
        "title": r"Squared PSF Size $R^2$",
        "unit": r" $(\mathrm{px}^2)$",
        "lims": (4.2, 6.9),
        "prop_name": "r2",
        "scale_fac": 100.0,
        "has_ylabel": True,
    },
]

for p in panels:
    ax = p["ax"]
    true_vals = p["true"]
    lims = p["lims"]
    prop = p["prop_name"]

    # 1:1 Identity line
    ax.plot(lims, lims, linestyle="--", color="#555555", linewidth=1.8, zorder=2)

    legend_elements = [
        Line2D([0], [0], color="#555555", lw=1.8, linestyle="--", label=r"Ideal recovery ($y = x$)")
    ]

    # Plot each model
    for mc in models_config:
        pred_vals = data[f"G2_{mc['key']}_pred_{prop}"]

        # Fit OLS line: pred = (1+m)*true + c
        poly_fit = np.polyfit(true_vals, pred_vals, 1)
        slope, intercept = poly_fit[0], poly_fit[1]
        m = (slope - 1.0) * p["scale_fac"]

        # Scatter
        ax.scatter(
            true_vals, pred_vals,
            color=mc["color"],
            marker=mc["marker"],
            s=mc["size"],
            alpha=mc["alpha"],
            edgecolors=mc["edge"],
            linewidths=0.45,
            zorder=3,
        )

        # Regression line
        x_grid = np.linspace(lims[0], lims[1], 100)
        y_grid = slope * x_grid + intercept
        ax.plot(x_grid, y_grid, color=mc["color"], linewidth=mc["lw"], linestyle="-", zorder=4)

        if prop == "r2":
            label_text = f"{mc['name']}: " + r"$\mathrm{slope} = " + f"{slope:.3f}$"
        else:
            label_text = f"{mc['name']}: " + r"$m = " + f"{m:+.2f}\\%" + "$"

        legend_elements.append(
            Line2D([0], [0], color=mc["color"], lw=mc["lw"], marker=mc["marker"],
                   markersize=7.5, markerfacecolor=mc["color"], markeredgecolor=mc["edge"],
                   label=label_text)
        )

    # Subplot formatting
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(p["title"], fontsize=16.5, fontweight="bold", pad=12, color="#111111")
    ax.set_xlabel(f"Reference Value{p['unit']}", fontsize=14.5, fontweight="bold", labelpad=8)
    if p["has_ylabel"]:
        ax.set_ylabel(f"Reconstructed Value{p['unit']}", fontsize=14.5, fontweight="bold", labelpad=8)
    else:
        ax.set_ylabel("")

    ax.grid(True, linestyle="--", alpha=0.45, color="#c5c5c5", zorder=1)
    ax.tick_params(axis="both", labelsize=12.5)

    # Legend
    legend = ax.legend(handles=legend_elements, loc="upper left",
                       fontsize=11.8, framealpha=0.92, facecolor="#ffffff",
                       edgecolor="#cccccc")

# Overarching figure title
fig.suptitle("Reference vs. Reconstructed PSF Properties: Ground-based Optical and Atmospheric Model (G2)",
             fontsize=18.5, fontweight="bold", y=0.96, color="#111111")

output_png.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(output_png, dpi=300, bbox_inches="tight")
plt.close()
print(f"Figure saved to {output_png}")
