"""
Script to generate diagnostic figure for the article:
images/spatial_psf_field_grid.png:
An 8x8 regular focal-plane grid showing PSF stamps and ellipticity glyphs.
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.cm as cm

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from simulation.dataset import SmoothMoffatFieldGenerator
from validation.moments import measure_psf_batch


def generate_spatial_psf_field_grid():
    images_dir = BASE_DIR / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    generator = SmoothMoffatFieldGenerator(seed=100, beta=3.5, base_fwhm=3.5)

    print("Generating images/spatial_psf_field_grid.png ...")
    n_grid = 8
    g_coords = np.linspace(0.08, 0.92, n_grid)
    MOS_X, MOS_Y = np.meshgrid(g_coords, g_coords, indexing="xy")
    mos_pts = np.column_stack([MOS_X.ravel(), MOS_Y.ravel()])
    mos_psfs = generator.generate_psf_batch(mos_pts, stamp_size=48)
    me1, me2, mr2 = measure_psf_batch(mos_psfs, sigma_w=3.5)
    me_mag = np.sqrt(me1**2 + me2**2)
    m_theta = 0.5 * np.arctan2(me2, me1)

    # Figure with identical square panel dimensions and matched coordinates
    fig = plt.figure(figsize=(17.0, 8.5), dpi=260)

    # Geometry: fig_w = 17.0, fig_h = 8.5 -> aspect ratio = 2.0
    # For an exact square, width W must equal height H * (8.5 / 17.0) = 0.5 * H
    H = 0.70
    W = 0.35
    y0 = 0.15
    x_left = 0.075
    x_right = 0.515
    cbar_pad = 0.018
    cbar_w = 0.020

    # Add left and right axes with identical physical square dimensions
    ax_left = fig.add_axes([x_left, y0, W, H])
    ax_right = fig.add_axes([x_right, y0, W, H])
    cax = fig.add_axes([x_right + W + cbar_pad, y0, cbar_w, H])

    # Left panel: Individual stellar PSF images at matching (x, y) focal-plane positions
    ax_left.set_facecolor("#000000")
    zoom_half = 11
    c_idx = 24
    half_w = 0.046

    for i in range(len(mos_pts)):
        x_pt, y_pt = mos_pts[i]
        core = mos_psfs[i, c_idx - zoom_half:c_idx + zoom_half, c_idx - zoom_half:c_idx + zoom_half]
        core_norm = core / np.max(core)
        ax_left.imshow(core_norm, cmap="inferno", origin="lower",
                       extent=[x_pt - half_w, x_pt + half_w, y_pt - half_w, y_pt + half_w],
                       interpolation="bicubic", zorder=2)

    ax_left.set_xlim(0, 1)
    ax_left.set_ylim(0, 1)
    ax_left.set_title("Simulated PSFs Across the Focal Plane", fontsize=22, fontweight="bold", pad=16)
    ax_left.set_xlabel("Focal-plane $x$", color="#111111", fontsize=19, fontweight="bold", labelpad=10)
    ax_left.set_ylabel("Focal-plane $y$", color="#111111", fontsize=19, fontweight="bold", labelpad=10)
    ax_left.tick_params(colors="#111111", labelsize=16, width=1.5, length=6)
    for spine in ax_left.spines.values():
        spine.set_color("#444444")
        spine.set_linewidth(1.4)

    # Right panel: Ellipticity and size glyph field
    ax_right.set_facecolor("#000000")

    for i in range(len(mos_pts)):
        x_pt, y_pt = mos_pts[i]
        mag = me_mag[i]
        ang_deg = np.degrees(m_theta[i])

        # Width and height of ellipse glyph
        scale = 0.075
        a_axis = scale * (1.0 + 2.5 * mag)
        b_axis = scale * (1.0 - 2.5 * mag)

        # Color mapped by size R^2
        r_val = mr2[i]
        norm_r = (r_val - np.min(mr2)) / (np.max(mr2) - np.min(mr2) + 1e-6)
        color = plt.cm.plasma(norm_r)

        ellipse = Ellipse((x_pt, y_pt), width=a_axis, height=b_axis, angle=ang_deg,
                          facecolor=color, edgecolor="white", alpha=0.9, linewidth=0.8)
        ax_right.add_patch(ellipse)

    ax_right.set_xlim(0, 1)
    ax_right.set_ylim(0, 1)
    ax_right.set_title("PSF Ellipticity and Size", fontsize=22, fontweight="bold", pad=16)
    ax_right.set_xlabel("Focal-plane $x$", color="#111111", fontsize=19, fontweight="bold", labelpad=10)
    ax_right.set_ylabel("Focal-plane $y$", color="#111111", fontsize=19, fontweight="bold", labelpad=10)
    ax_right.tick_params(colors="#111111", labelsize=16, width=1.5, length=6)
    for spine in ax_right.spines.values():
        spine.set_color("#444444")
        spine.set_linewidth(1.4)

    # Colorbar for glyph size R^2
    sm = cm.ScalarMappable(cmap="plasma", norm=plt.Normalize(vmin=np.min(mr2), vmax=np.max(mr2)))
    sm.set_array([])
    cbar = plt.colorbar(sm, cax=cax)
    cbar.set_label(r"PSF Squared Size $R^2\;(\mathrm{pixels}^2)$", color="#111111", fontsize=19, fontweight="bold", labelpad=16)
    cbar.ax.yaxis.set_tick_params(color="#111111", labelcolor="#111111", labelsize=16, width=1.5, length=6)
    cbar.outline.set_edgecolor('#666666')
    cbar.outline.set_linewidth(1.2)

    fig_path = images_dir / "spatial_psf_field_grid.png"
    plt.savefig(fig_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved {fig_path}")


if __name__ == "__main__":
    generate_spatial_psf_field_grid()
