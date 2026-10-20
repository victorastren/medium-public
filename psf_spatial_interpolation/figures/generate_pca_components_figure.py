"""
Generate figure showing the Mean PSF and the first four
principal components (PC1, PC2, PC3, PC4) for Section 3 of 'Interpolating Stars'.
Displays the central 24 x 24 pixels for maximum clarity.

Typography and scaling matched to s1_psf_reconstruction_residual.png:
- Panel titles: 18pt bold
- Axes labels: 15pt bold
- Pixel ticks: 13.5pt
- Colorbar ticks: 14.5pt with Unicode minus symbols
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from representation.pca import PSFRepresentation


def generate_pca_components_figure():
    data_dir = BASE_DIR / "data" / "field_000"
    images_dir = BASE_DIR / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load training PSFs and fit PCA
    psf_train = np.load(data_dir / "psf_train_true.npy")
    pca = PSFRepresentation(n_components_max=5)
    pca.fit(psf_train)

    mean_psf = pca.mean_vector.reshape(48, 48)
    pcs = [pca.components[i].reshape(48, 48) for i in range(4)]
    titles = ["Mean PSF", r"$\mathrm{PC}_1$", r"$\mathrm{PC}_2$", r"$\mathrm{PC}_3$", r"$\mathrm{PC}_4$"]

    # 2. Central 24 x 24 crop for publication display
    c, r = 24, 12  # pixels 12 to 36
    crop_mean = mean_psf[c - r : c + r, c - r : c + r]
    crop_pcs = [p[c - r : c + r, c - r : c + r] for p in pcs]

    extent = [12, 36, 12, 36]
    ticks = [12, 24, 36]

    # 3. Setup figure with 5 matched square panels and proportional typography
    fig, axes = plt.subplots(1, 5, figsize=(16.0, 4.6), dpi=260)
    plt.subplots_adjust(wspace=0.18, bottom=0.22, top=0.88, left=0.06, right=0.98)

    for i, (ax, title) in enumerate(zip(axes, titles)):
        if i == 0:
            # Mean PSF: Grayscale (non-negative intensity)
            im = ax.imshow(crop_mean, cmap="gray", origin="lower", extent=extent)
            ax.set_ylabel("Pixel $y$", fontsize=15, fontweight="bold", color="#111111", labelpad=6)
            ax.set_yticks(ticks)
            ax.tick_params(axis="y", labelsize=13.5, colors="#111111", width=1.2, length=4.5)
        else:
            # Principal components: Diverging scale (RdBu_r) centered symmetrically at 0
            pc_sub = crop_pcs[i - 1]
            vmax = max(abs(pc_sub.min()), abs(pc_sub.max()))
            im = ax.imshow(pc_sub, cmap="RdBu_r", vmin=-vmax, vmax=vmax, origin="lower", extent=extent)
            ax.set_yticks([])
            ax.tick_params(axis="y", left=False)

        ax.set_title(title, fontsize=18, fontweight="bold", pad=10, color="#111111")
        ax.set_xlabel("Pixel $x$", fontsize=15, fontweight="bold", color="#111111", labelpad=6)
        ax.set_xticks(ticks)
        ax.tick_params(axis="x", labelsize=13.5, colors="#111111", width=1.2, length=4.5)

        for spine in ax.spines.values():
            spine.set_color("#444444")
            spine.set_linewidth(1.3)

        # Horizontal colorbar underneath each panel
        cbar = plt.colorbar(im, ax=ax, orientation="horizontal", fraction=0.058, pad=0.22)
        cbar.outline.set_edgecolor("#555555")
        cbar.outline.set_linewidth(1.1)

        if i == 0:
            cbar.set_ticks([0.00, 0.03, 0.06])
            cbar.set_ticklabels(["0.00", "0.03", "0.06"])
        elif i == 1:
            cbar.set_ticks([-0.4, 0.0, 0.4])
            cbar.set_ticklabels(["−0.4", "0.0", "+0.4"])
        elif i in [2, 3, 4]:
            cbar.set_ticks([-0.2, 0.0, 0.2])
            cbar.set_ticklabels(["−0.2", "0.0", "+0.2"])

        cbar.ax.tick_params(labelsize=14.5, colors="#111111", width=1.2, length=4)

    out_path = images_dir / "pca_mean_and_components.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved {out_path}")


if __name__ == "__main__":
    generate_pca_components_figure()
