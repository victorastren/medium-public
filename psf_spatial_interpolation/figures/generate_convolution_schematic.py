"""
Generate schematic illustration of astronomical image formation
via convolution: Intrinsic galaxy * PSF = Observed galaxy.
Designed for Section 1 of 'Interpolating Stars' for Medium publication (680px width).
"""

from pathlib import Path
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def generate_convolution_schematic():
    images_dir = PROJECT_ROOT / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    out_path = images_dir / "galaxy_psf_convolution_schematic.png"

    # 1. Isotropic square pixel grid
    N = 320
    L = 3.6
    x = np.linspace(-L, L, N)
    y = np.linspace(-L, L, N)
    X, Y = np.meshgrid(x, y)

    # 2. Intrinsic Galaxy: inclined elliptical profile (angle ~25 degrees)
    theta = np.radians(25)
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    Xr = X * cos_t + Y * sin_t
    Yr = -X * sin_t + Y * cos_t

    q = 0.38  # b/a axis ratio
    r_gal = np.sqrt(Xr**2 + (Yr / q)**2)
    # Smooth Sersic-like exponential profile with luminous core
    I_gal = np.exp(-1.35 * (r_gal / 1.3)**0.82)

    # 3. PSF: circular Moffat profile
    r_psf = np.sqrt(X**2 + Y**2)
    alpha = 0.70
    beta = 2.8
    I_psf = (1.0 + (r_psf / alpha)**2)**(-beta)
    # Normalize PSF for convolution (energy conservation)
    I_psf_norm = I_psf / np.sum(I_psf)

    # 4. Observed Galaxy: 2D FFT convolution (G * P)
    I_obs = scipy.signal.fftconvolve(I_gal, I_psf_norm, mode="same")

    # Display normalization: power scaling for astronomical contrast
    def disp_norm(img, p=0.72):
        clipped = np.clip(img, 0, None)
        return np.power(clipped / np.max(clipped), p)

    I_gal_disp = disp_norm(I_gal, 0.72)
    I_psf_disp = disp_norm(I_psf, 0.68)
    I_obs_disp = disp_norm(I_obs, 0.72)

    # Colormap matching astronomical deep-sky palette:
    # Deep midnight navy (#090f1e) -> slate blue -> soft ice -> bright white core
    colors = [
        (0.00, "#090f1e"),
        (0.12, "#101a2f"),
        (0.26, "#203454"),
        (0.44, "#3c5a81"),
        (0.64, "#6a8fb7"),
        (0.82, "#b0cbe3"),
        (0.94, "#e4f0f8"),
        (1.00, "#ffffff"),
    ]
    galaxy_cmap = LinearSegmentedColormap.from_list("galaxy_convolution", colors)

    # Canvas: 14.2 x 3.95 inches at 240 DPI (snug top and bottom margins)
    fig_w = 14.2
    fig_h = 3.95
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240)
    fig.patch.set_facecolor("#ffffff")

    # Outer light card container: snug framing
    outer_ax = fig.add_axes([0.012, 0.020, 0.976, 0.960])
    outer_ax.axis("off")
    outer_card = FancyBboxPatch(
        (0, 0),
        1,
        1,
        boxstyle="round,pad=0,rounding_size=0.038",
        facecolor="#ffffff",
        edgecolor="#e2e8f0",
        linewidth=1.5,
        transform=outer_ax.transAxes,
        zorder=0,
    )
    outer_ax.add_patch(outer_card)

    # Dark boxes: 3.1 x 3.1 inches (true square stamps)
    box_in = 3.1
    w_box = box_in / fig_w
    h_box = box_in / fig_h

    # Snug top margin (0.22 inches from figure top)
    y_box_top = (fig_h - 0.22) / fig_h
    y_box = y_box_top - h_box

    x_g = 0.065
    gap = 0.110
    x_p = x_g + w_box + gap
    x_o = x_p + w_box + gap

    axes_boxes = [
        fig.add_axes([x_g, y_box, w_box, h_box]),
        fig.add_axes([x_p, y_box, w_box, h_box]),
        fig.add_axes([x_o, y_box, w_box, h_box]),
    ]
    imgs = [I_gal_disp, I_psf_disp, I_obs_disp]

    for ax, img in zip(axes_boxes, imgs):
        ax.set_facecolor("#090f1e")
        box = FancyBboxPatch(
            (0, 0),
            1,
            1,
            boxstyle="round,pad=0,rounding_size=0.10",
            facecolor="#090f1e",
            edgecolor="#1e2b45",
            linewidth=1.8,
            transform=ax.transAxes,
            zorder=1,
        )
        ax.add_patch(box)

        im = ax.imshow(
            img,
            cmap=galaxy_cmap,
            origin="lower",
            extent=[0, 1, 0, 1],
            vmin=0.0,
            vmax=1.0,
            zorder=2,
        )
        im.set_clip_path(box)
        ax.axis("off")

    # Labels below boxes: snug placement
    fig.text(
        x_g + w_box / 2,
        y_box - 0.046,
        "Intrinsic galaxy",
        ha="center",
        va="top",
        fontsize=17,
        fontweight="bold",
        color="#1e293b",
    )
    fig.text(
        x_p + w_box / 2,
        y_box - 0.046,
        "PSF",
        ha="center",
        va="top",
        fontsize=17,
        fontweight="bold",
        color="#1e293b",
    )
    fig.text(
        x_o + w_box / 2,
        y_box - 0.046,
        "Observed galaxy",
        ha="center",
        va="top",
        fontsize=17,
        fontweight="bold",
        color="#1e293b",
    )

    # Mathematical operators
    x_op1 = x_g + w_box + gap / 2
    x_op2 = x_p + w_box + gap / 2
    y_op = y_box + h_box / 2

    fig.text(
        x_op1,
        y_op,
        "∗",
        ha="center",
        va="center",
        fontsize=38,
        fontweight="bold",
        color="#1e293b",
    )
    fig.text(
        x_op2,
        y_op,
        "=",
        ha="center",
        va="center",
        fontsize=38,
        fontweight="bold",
        color="#1e293b",
    )

    plt.savefig(out_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[OK] Saved {out_path}")


if __name__ == "__main__":
    generate_convolution_schematic()
