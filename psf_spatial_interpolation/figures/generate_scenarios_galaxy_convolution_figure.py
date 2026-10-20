"""
Generate 6-panel comparison figure for Section 2:
'Constructing a Simulated PSF Field'.

Compares:
- Upper row: Stellar PSFs from G1, G2, and S1 at an identical focal plane position.
- Lower row: An identical intrinsic elliptical galaxy convolved with each scenario's PSF.

Exports to images/scenarios_galaxy_convolution_comparison.png.
"""

from pathlib import Path
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def generate_scenarios_galaxy_convolution_figure(
    output_path: str = "images/scenarios_galaxy_convolution_comparison.png",
    test_index: int = 0,
    dpi: int = 220,
):
    out_file = PROJECT_ROOT / output_path
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # 1. Coordinate grid matching PSF stamp size (48 x 48)
    n_pix = 48
    x = np.arange(n_pix) - (n_pix - 1) / 2.0
    X, Y = np.meshgrid(x, x)

    # 2. Moderately elliptical intrinsic galaxy: exponential disk profile
    # Ellipticity q = 0.52, orientation theta = 35 degrees, effective radius r_e = 4.0 px
    theta = np.radians(35)
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    Xr = X * cos_t + Y * sin_t
    Yr = -X * sin_t + Y * cos_t
    q = 0.52
    r_gal = np.sqrt(Xr**2 + (Yr / q)**2)
    r_e = 4.0
    i_gal = np.exp(-1.678 * (r_gal / r_e)**0.85)

    # 3. Load true PSFs at the chosen representative test position
    psf_g1 = np.load(PROJECT_ROOT / "data" / "field_000" / "psf_test_true.npy")[test_index]
    psf_g2 = np.load(PROJECT_ROOT / "data" / "field_g2" / "psf_test_true.npy")[test_index]
    psf_s1 = np.load(PROJECT_ROOT / "data" / "field_s1" / "psf_test_true.npy")[test_index]

    # 4. Numerically convolve galaxy with each scenario's PSF
    conv_g1 = scipy.signal.fftconvolve(i_gal, psf_g1, mode="same")
    conv_g2 = scipy.signal.fftconvolve(i_gal, psf_g2, mode="same")
    conv_s1 = scipy.signal.fftconvolve(i_gal, psf_s1, mode="same")

    # Consistent stretch per row (asinh tone mapping)
    def asinh_norm(img, a=0.0015, vmax=None):
        if vmax is None:
            vmax = img.max()
        val = np.arcsinh(np.clip(img, 0, None) / a)
        top = np.arcsinh(vmax / a)
        return np.clip(val / top, 0, 1)

    # Row 1 (PSFs): asinh stretch with a = 0.0015
    max_psf = max(psf_g1.max(), psf_g2.max(), psf_s1.max())
    disp_p1 = asinh_norm(psf_g1, a=0.0015, vmax=max_psf)
    disp_p2 = asinh_norm(psf_g2, a=0.0015, vmax=max_psf)
    disp_p3 = asinh_norm(psf_s1, a=0.0015, vmax=max_psf)

    # Row 2 (Convolved galaxies): asinh stretch with a = 0.015
    max_conv = max(conv_g1.max(), conv_g2.max(), conv_s1.max())
    disp_c1 = asinh_norm(conv_g1, a=0.015, vmax=max_conv)
    disp_c2 = asinh_norm(conv_g2, a=0.015, vmax=max_conv)
    disp_c3 = asinh_norm(conv_s1, a=0.015, vmax=max_conv)

    # Astronomical deep-sky colormap matching publication styling
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
    galaxy_cmap = LinearSegmentedColormap.from_list("astronomy_blue", colors)

    # Canvas dimensions: 14.0 x 9.4 inches at 220 DPI (balanced, generous headroom for headers)
    fig_w = 14.0
    fig_h = 9.4
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    fig.patch.set_facecolor("#ffffff")

    # Outer light card container: snug, balanced margins
    outer_ax = fig.add_axes([0.012, 0.018, 0.976, 0.964])
    outer_ax.axis("off")
    outer_card = FancyBboxPatch(
        (0, 0),
        1,
        1,
        boxstyle="round,pad=0,rounding_size=0.03",
        facecolor="#ffffff",
        edgecolor="#e2e8f0",
        linewidth=1.5,
        transform=outer_ax.transAxes,
        zorder=0,
    )
    outer_ax.add_patch(outer_card)

    # Stamps: 3.10 x 3.10 inches (true square stamps)
    stamp_in = 3.10
    stamp_w = stamp_in / fig_w
    stamp_h = stamp_in / fig_h

    # Vertical coordinates in inches
    y_bottom_in = 0.40
    y_r2 = y_bottom_in / fig_h
    row_gap_in = 0.50
    y_r1 = (y_bottom_in + stamp_in + row_gap_in) / fig_h

    # Horizontal coordinates
    x_left_stamp_in = 2.15
    col_gap_in = 0.75
    col_centers_in = [
        x_left_stamp_in + stamp_in / 2.0 + i * (stamp_in + col_gap_in)
        for i in range(3)
    ]
    x_cols = [(c - stamp_in / 2.0) / fig_w for c in col_centers_in]
    x_centers_frac = [c / fig_w for c in col_centers_in]

    y_top_stamp_in = y_bottom_in + stamp_in + row_gap_in + stamp_in

    col_headers_line1 = ["G1", "G2", "S1"]
    col_headers_line2 = [
        "Ground-based\n(smooth Moffat)",
        "Ground-based\n(optical + atmospheric)",
        "Space-based\n(diffraction)",
    ]

    row1_imgs = [disp_p1, disp_p2, disp_p3]
    row2_imgs = [disp_c1, disp_c2, disp_c3]

    # Row labels on the left (centered on rows)
    fig.text(
        0.088,
        y_r1 + stamp_h / 2,
        "PSF",
        ha="center",
        va="center",
        fontsize=23,
        fontweight="bold",
        color="#1e293b",
    )
    fig.text(
        0.088,
        y_r2 + stamp_h / 2,
        "Convolved\nGalaxy",
        ha="center",
        va="center",
        fontsize=20,
        fontweight="bold",
        color="#1e293b",
        linespacing=1.2,
    )

    for i in range(3):
        # Column header line 1: G1, G2, S1 (30pt bold, safely inside rounded card)
        fig.text(
            x_centers_frac[i],
            (y_top_stamp_in + 1.22) / fig_h,
            col_headers_line1[i],
            ha="center",
            va="bottom",
            fontsize=30,
            fontweight="bold",
            color="#1e293b",
        )
        # Column header line 2: Subtitles (doubled font size: 24pt, clear and legible at 680px)
        fig.text(
            x_centers_frac[i],
            (y_top_stamp_in + 0.16) / fig_h,
            col_headers_line2[i],
            ha="center",
            va="bottom",
            fontsize=24,
            fontweight="normal",
            color="#475569",
            linespacing=1.16,
        )

        # Upper stamp: PSF
        ax_top = fig.add_axes([x_cols[i], y_r1, stamp_w, stamp_h])
        ax_top.set_facecolor("#090f1e")
        box_t = FancyBboxPatch(
            (0, 0),
            1,
            1,
            boxstyle="round,pad=0,rounding_size=0.08",
            facecolor="#090f1e",
            edgecolor="#1e2b45",
            linewidth=1.5,
            transform=ax_top.transAxes,
            zorder=1,
        )
        ax_top.add_patch(box_t)
        im_t = ax_top.imshow(
            row1_imgs[i],
            cmap=galaxy_cmap,
            origin="lower",
            extent=[0, 1, 0, 1],
            vmin=0,
            vmax=1,
            interpolation="bicubic",
            zorder=2,
        )
        im_t.set_clip_path(box_t)
        ax_top.axis("off")

        # Lower stamp: Convolved Galaxy
        ax_bot = fig.add_axes([x_cols[i], y_r2, stamp_w, stamp_h])
        ax_bot.set_facecolor("#090f1e")
        box_b = FancyBboxPatch(
            (0, 0),
            1,
            1,
            boxstyle="round,pad=0,rounding_size=0.08",
            facecolor="#090f1e",
            edgecolor="#1e2b45",
            linewidth=1.5,
            transform=ax_bot.transAxes,
            zorder=1,
        )
        ax_bot.add_patch(box_b)
        im_b = ax_bot.imshow(
            row2_imgs[i],
            cmap=galaxy_cmap,
            origin="lower",
            extent=[0, 1, 0, 1],
            vmin=0,
            vmax=1,
            interpolation="bicubic",
            zorder=2,
        )
        im_b.set_clip_path(box_b)
        ax_bot.axis("off")

    plt.savefig(out_file, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[OK] Saved {out_file}")


if __name__ == "__main__":
    generate_scenarios_galaxy_convolution_figure()
