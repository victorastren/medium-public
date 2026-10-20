#!/usr/bin/env python3
"""
Generate figure:
images/pca_representation_vs_k.png

Two-panel figure showing:
- Top panel: Cumulative Explained Variance vs. number of PCA components K
- Bottom panel: PCA Representation Error vs. number of PCA components K
at held-out test positions across the three observing scenarios (G1, G2, S1).

Matches the visual style of reconstruction_fidelity_g2.png:
- 4-sided boxed frame on both subplots
- Dense dashed/dotted grid across both axes
- Repeated integer x-axis tick labels (1, 2, ..., 17) on both top and bottom plots
- Smooth PCHIP interpolated curves with refined 1.6pt line width
- Prominent markers at adopted K values (K=5 for G1, K=8 for G2, K=9 for S1)
- Clean titles without "A." or "B." prefix
"""

from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, LogLocator, NullFormatter, MultipleLocator
from scipy.interpolate import PchipInterpolator
from matplotlib.lines import Line2D

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.dataset import load_dataset
from representation.pca import PSFRepresentation

DATA_DIR = PROJECT_ROOT / "data"
IMAGES_DIR = PROJECT_ROOT / "images"

SCENARIOS = [
    {
        "key": "G1",
        "name": "G1",
        "label": r"G1 ($K=5$)",
        "path": DATA_DIR / "field_000",
        "k_opt": 5,
        "color": "#1f77b4",  # Blue
    },
    {
        "key": "G2",
        "name": "G2",
        "label": r"G2 ($K=8$)",
        "path": DATA_DIR / "field_g2",
        "k_opt": 8,
        "color": "#d97706",  # Amber / Warm Orange
    },
    {
        "key": "S1",
        "name": "S1",
        "label": r"S1 ($K=9$)",
        "path": DATA_DIR / "field_s1",
        "k_opt": 9,
        "color": "#0d9488",  # Teal
    },
]

K_MAX = 12
KS = np.arange(1, K_MAX + 1)
K_DENSE = np.linspace(1, K_MAX, 350)


def compute_pca_curves():
    results = []
    for sc in SCENARIOS:
        ds = load_dataset(str(sc["path"]))
        pca = PSFRepresentation(n_components_max=K_MAX)
        pca.fit(ds.psfs_train_true)

        # Panel 1: Cumulative explained variance in %
        cum_var = np.cumsum(pca.explained_variance_ratio) * 100.0
        pchip_var = PchipInterpolator(KS, cum_var)
        dense_var = np.clip(pchip_var(K_DENSE), 0.0, 100.0)

        # Panel 2: Relative representation error on held-out test PSFs (200 stars)
        test_psfs = ds.psfs_test_true
        tot_norm_sq = np.sum(test_psfs ** 2)

        rep_errors = []
        for k in KS:
            rec_test = pca.reconstruct(test_psfs, n_components=k, as_images=True)
            res_sq = np.sum((test_psfs - rec_test) ** 2)
            rel_err = 100.0 * np.sqrt(res_sq / tot_norm_sq)
            rep_errors.append(rel_err)
        rep_errors = np.array(rep_errors)

        # Smooth representation error on log scale
        log_err = np.log10(rep_errors)
        pchip_err = PchipInterpolator(KS, log_err)
        dense_err = 10.0 ** pchip_err(K_DENSE)

        results.append({
            **sc,
            "cum_var": cum_var,
            "dense_var": dense_var,
            "rep_errors": rep_errors,
            "dense_err": dense_err,
        })
    return results


def create_figure(output_path=None):
    if output_path is None:
        output_path = IMAGES_DIR / "pca_representation_vs_k.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    curves_data = compute_pca_curves()

    # Styling consistent with reconstruction_fidelity_g2.png & article standards
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "mathtext.fontset": "dejavusans",
        "axes.edgecolor": "#333333",
        "axes.linewidth": 1.3,
        "axes.labelcolor": "#111111",
        "xtick.color": "#222222",
        "ytick.color": "#222222",
    })

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.4, 8.3), dpi=200, sharex=True)
    plt.subplots_adjust(left=0.14, right=0.95, top=0.94, bottom=0.11, hspace=0.36)

    LINE_WIDTH = 1.6
    MARKER_SIZE = 7.0

    # -------------------------------------------------------------------------
    # Panel 1: Cumulative Explained Variance (NO "A.")
    # -------------------------------------------------------------------------
    ax1.set_title(r"Cumulative Explained Variance", fontsize=14, fontweight="bold", pad=10, color="#111111")
    ax1.set_ylabel(r"Explained Variance (%)", fontsize=12.5, fontweight="bold", labelpad=8)
    ax1.set_ylim(35, 102)

    # Dense y-grid: major ticks every 10%, minor every 5%
    ax1.set_yticks([40, 50, 60, 70, 80, 90, 100])
    ax1.yaxis.set_minor_locator(MultipleLocator(5))

    # X-axis ticks (1, 2, ..., 12) repeated on top plot
    ax1.set_xlim(0.8, 12.2)
    ax1.set_xticks(KS)

    # 4-sided boxed frame
    for spine in ax1.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.3)
        spine.set_color("#333333")

    # Dense grid in both X and Y
    ax1.grid(True, which="major", linestyle="--", alpha=0.55, color="#c5c5c5", zorder=1)
    ax1.grid(True, which="minor", linestyle=":", alpha=0.38, color="#dedede", zorder=1)

    for c in curves_data:
        # Smooth PCHIP curve
        ax1.plot(K_DENSE, c["dense_var"], color=c["color"], linewidth=LINE_WIDTH, zorder=3)
        # Prominent marker at adopted K
        k_idx = c["k_opt"] - 1
        ax1.plot(c["k_opt"], c["cum_var"][k_idx], marker="o", markersize=MARKER_SIZE,
                 color=c["color"], markeredgecolor="#ffffff", markeredgewidth=1.0, zorder=5)

    ax1.tick_params(axis="y", which="major", labelsize=11)
    ax1.tick_params(axis="x", which="major", labelbottom=True, labelsize=11)

    # -------------------------------------------------------------------------
    # Panel 2: PCA Representation Error (NO "B.")
    # -------------------------------------------------------------------------
    ax2.set_title(r"PCA Representation Error", fontsize=14, fontweight="bold", pad=10, color="#111111")
    ax2.set_xlabel(r"Number of PCA Components $K$", fontsize=12.5, fontweight="bold", labelpad=8)
    ax2.set_ylabel(r"Representation Error (%)", fontsize=12.5, fontweight="bold", labelpad=8)
    ax2.set_yscale("log")
    ax2.set_ylim(0.00008, 10.0)

    # Dense semilog grid
    ax2.set_yticks([0.0001, 0.001, 0.01, 0.1, 1.0])
    ax2.get_yaxis().set_major_formatter(FormatStrFormatter("%g"))
    ax2.yaxis.set_minor_locator(LogLocator(base=10.0, subs=(0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9), numticks=20))
    ax2.yaxis.set_minor_formatter(NullFormatter())

    # X-axis ticks (1, 2, ..., 12) on bottom plot
    ax2.set_xlim(0.8, 12.2)
    ax2.set_xticks(KS)

    # 4-sided boxed frame
    for spine in ax2.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.3)
        spine.set_color("#333333")

    # Dense grid in both X and Y
    ax2.grid(True, which="major", linestyle="--", alpha=0.55, color="#c5c5c5", zorder=1)
    ax2.grid(True, which="minor", linestyle=":", alpha=0.38, color="#dedede", zorder=1)

    for c in curves_data:
        # Smooth PCHIP curve
        ax2.plot(K_DENSE, c["dense_err"], color=c["color"], linewidth=LINE_WIDTH, zorder=3)
        # Prominent marker at adopted K
        k_idx = c["k_opt"] - 1
        ax2.plot(c["k_opt"], c["rep_errors"][k_idx], marker="o", markersize=MARKER_SIZE,
                 color=c["color"], markeredgecolor="#ffffff", markeredgewidth=1.0, zorder=5)

    ax2.tick_params(axis="both", which="major", labelsize=11)
    ax2.tick_params(axis="x", which="major", labelsize=10.5)

    # -------------------------------------------------------------------------
    # Shared Legend at Bottom with clean boxed frame
    # -------------------------------------------------------------------------
    legend_elements = [
        Line2D([0], [0], color=c["color"], lw=LINE_WIDTH, marker="o", markersize=MARKER_SIZE,
               markeredgecolor="#ffffff", markeredgewidth=1.0, label=c["label"])
        for c in curves_data
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=3,
               framealpha=0.95, facecolor="#ffffff", edgecolor="#cccccc",
               fontsize=11.5, handlelength=2.4, handletextpad=0.7, columnspacing=2.6)

    plt.savefig(output_path, dpi=200)
    plt.close(fig)
    print(f"[OK] Generated {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    create_figure()
