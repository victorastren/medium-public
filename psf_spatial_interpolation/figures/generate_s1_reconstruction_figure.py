"""
Generate three-panel scientific figure for Section 'Reconstructing the PSF'.

Displays:
1. Exact simulated reference PSF (Scenario S1)
2. Reconstructed PSF using PCA (K=9) and Universal Kriging (quadratic drift)
3. Signed pixel residual ΔP(x) = P_reconstructed(x) - P_reference(x)

Selected at a representative held-out test position (index 195, error ~ median).
Exported to images/s1_psf_reconstruction_residual.png.
Typography and styling matched to publication figures (spatial_psf_field_grid.png).
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from simulation.dataset import load_dataset
from representation.pca import PSFRepresentation
from interpolation.kriging import UniversalKrigingInterpolator
from reconstruction.psf import reconstruct_psfs_from_coefficients


def generate_s1_reconstruction_figure(
    dataset_dir: str = "data/field_s1",
    output_path: str = "images/s1_psf_reconstruction_residual.png",
    test_index: int = 195,
    n_components: int = 9,
    dpi: int = 160
):
    dataset_path = BASE_DIR / dataset_dir
    out_file = BASE_DIR / output_path
    out_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading dataset from {dataset_path}...")
    dataset = load_dataset(str(dataset_path))

    print(f"Fitting PCA (K={n_components}) on {len(dataset.psfs_train_observed)} training stars...")
    pca = PSFRepresentation(n_components_max=n_components)
    pca.fit(dataset.psfs_train_observed)
    train_coeffs = pca.transform(dataset.psfs_train_observed, n_components=n_components)

    print("Fitting Universal Kriging with quadratic drift...")
    uk = UniversalKrigingInterpolator(trend="quadratic")
    uk.fit(dataset.positions_train, train_coeffs)

    print(f"Predicting coefficients and reconstructing PSF for test star #{test_index}...")
    pred_coeffs = uk.predict(dataset.positions_test)
    rec_psfs = reconstruct_psfs_from_coefficients(pred_coeffs, pca, physical_adjustment=True)
    true_psfs = dataset.psfs_test_true

    ref = true_psfs[test_index]
    rec = rec_psfs[test_index]
    # Explicit residual convention: P_reconstructed - P_reference
    res = rec - ref

    pos = dataset.positions_test[test_index]
    rel_err = np.linalg.norm(res) / np.linalg.norm(ref) * 100.0
    abs_res_max = np.max(np.abs(res))

    print(f"Selected test position: ({pos[0]:.2f}, {pos[1]:.2f})")
    print(f"Relative reconstruction error: {rel_err:.4f}%")
    print(f"Peak reference intensity: {ref.max():.5f}, Reconstructed peak: {rec.max():.5f}")
    print(f"Maximum residual amplitude: {abs_res_max:.4e}")

    # Geometry: fig_w = 15.0, fig_h = 6.6
    # To have exact square panels: width W = H * (6.6 / 15.0) = 0.44 * H
    fig = plt.figure(figsize=(15.0, 6.6), dpi=dpi)

    H = 0.57
    W = H * (6.6 / 15.0)  # 0.2508

    y_bottom = 0.33
    x0 = 0.065
    x1 = 0.380
    x2 = 0.695

    ax0 = fig.add_axes([x0, y_bottom, W, H])
    ax1 = fig.add_axes([x1, y_bottom, W, H])
    ax2 = fig.add_axes([x2, y_bottom, W, H])

    vmin = 5e-5
    vmax = 0.09
    res_lim = 3.5e-5

    # Panel 1: Reference PSF
    im0 = ax0.imshow(ref, norm=LogNorm(vmin=vmin, vmax=vmax), cmap="magma", origin="lower")
    ax0.set_title("Reference PSF", fontsize=18, fontweight="bold", pad=12)
    ax0.set_xlabel("Pixel $x$", fontsize=15, fontweight="bold", labelpad=8)
    ax0.set_ylabel("Pixel $y$", fontsize=15, fontweight="bold", labelpad=8)

    # Panel 2: Reconstructed PSF
    im1 = ax1.imshow(rec, norm=LogNorm(vmin=vmin, vmax=vmax), cmap="magma", origin="lower")
    ax1.set_title("Reconstructed PSF", fontsize=18, fontweight="bold", pad=12)
    ax1.set_xlabel("Pixel $x$", fontsize=15, fontweight="bold", labelpad=8)
    ax1.set_ylabel("Pixel $y$", fontsize=15, fontweight="bold", labelpad=8)

    # Panel 3: Residual (ΔP) - simplified title
    im2 = ax2.imshow(res, cmap="bwr", vmin=-res_lim, vmax=res_lim, origin="lower")
    ax2.set_title(r"Residual ($\Delta P$)", fontsize=18, fontweight="bold", pad=12)
    ax2.set_xlabel("Pixel $x$", fontsize=15, fontweight="bold", labelpad=8)
    ax2.set_ylabel("Pixel $y$", fontsize=15, fontweight="bold", labelpad=8)

    for ax in [ax0, ax1, ax2]:
        ax.set_xticks([0, 10, 20, 30, 40])
        ax.set_yticks([0, 10, 20, 30, 40])
        ax.tick_params(labelsize=13.5, width=1.3, length=5)

    # Colorbars with font size 15 matching Axes labels
    y_cbar = 0.13
    h_cbar = 0.048

    # Shared colorbar spanning from x0 to x1 + W
    w_cbar01 = (x1 + W) - x0
    cax01 = fig.add_axes([x0, y_cbar, w_cbar01, h_cbar])
    cb01 = fig.colorbar(im0, cax=cax01, orientation="horizontal")
    cb01.set_label("Normalized Intensity (logarithmic scale)", fontsize=15, fontweight="bold", labelpad=8)
    cb01.ax.tick_params(labelsize=15, width=1.3, length=5)

    # Residual colorbar spanning from x2 to x2 + W
    cax2 = fig.add_axes([x2, y_cbar, W, h_cbar])
    cb2 = fig.colorbar(im2, cax=cax2, orientation="horizontal")
    cb2.set_label(r"Intensity Difference $\Delta P\;(\times 10^{-5})$", fontsize=15, fontweight="bold", labelpad=8)
    cb2.set_ticks([-3e-5, -2e-5, -1e-5, 0, 1e-5, 2e-5, 3e-5])
    cb2.set_ticklabels(["−3", "−2", "−1", "0", "+1", "+2", "+3"])
    cb2.ax.tick_params(labelsize=15, width=1.3, length=5)

    plt.savefig(out_file)
    plt.close(fig)
    print(f"[OK] Saved figure to {out_file} ({out_file.stat().st_size} bytes)")


if __name__ == "__main__":
    generate_s1_reconstruction_figure()
