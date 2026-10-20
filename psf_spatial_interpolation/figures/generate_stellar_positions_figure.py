"""
Generate single-panel figure of simulated stellar positions
for Section 2 of 'Interpolating Stars'.
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

def generate_stellar_positions_figure():
    data_dir = BASE_DIR / "data" / "field_000"
    images_dir = BASE_DIR / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    pos_train = np.load(data_dir / "positions_train.npy")
    pos_val = np.load(data_dir / "positions_validation.npy")
    pos_test = np.load(data_dir / "positions_test.npy")

    # Matched typography and styling with spatial_psf_field_grid.png
    fig, ax = plt.subplots(figsize=(8.5, 8.5), dpi=260)

    # Clean background with subtle grid
    ax.set_facecolor("#ffffff")
    ax.grid(True, linestyle="--", alpha=0.35, color="#cccccc", zorder=0)

    # Plot the three sets with distinct symbols
    ax.scatter(
        pos_train[:, 0], pos_train[:, 1],
        c="#1f77b4", s=38, alpha=0.8, marker="o", edgecolors="none",
        label=f"Training ({len(pos_train)})", zorder=2
    )
    ax.scatter(
        pos_val[:, 0], pos_val[:, 1],
        c="#2ca02c", s=52, alpha=0.9, marker="^", edgecolors="none",
        label=f"Validation ({len(pos_val)})", zorder=3
    )
    ax.scatter(
        pos_test[:, 0], pos_test[:, 1],
        c="#d62728", s=34, alpha=0.75, marker="x", linewidths=1.5,
        label=f"Test ({len(pos_test)})", zorder=4
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")

    # Font sizes matched to spatial_psf_field_grid.png
    ax.set_title("Simulated Stellar Positions", fontsize=22, fontweight="bold", pad=16, color="#111111")
    ax.set_xlabel("Focal-plane $x$", color="#111111", fontsize=19, fontweight="bold", labelpad=10)
    ax.set_ylabel("Focal-plane $y$", color="#111111", fontsize=19, fontweight="bold", labelpad=10)

    ax.tick_params(colors="#111111", labelsize=16, width=1.5, length=6)
    for spine in ax.spines.values():
        spine.set_color("#444444")
        spine.set_linewidth(1.4)

    # Legend with "Validation" fully spelled out
    leg = ax.legend(
        loc="upper right",
        fontsize=16,
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#bbbbbb",
        framealpha=0.95,
        borderpad=0.8,
        labelspacing=0.6
    )
    for text in leg.get_texts():
        text.set_color("#111111")
        text.set_fontweight("medium")

    plt.tight_layout()

    out_path = images_dir / "simulated_stellar_positions.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved {out_path}")

if __name__ == "__main__":
    generate_stellar_positions_figure()
