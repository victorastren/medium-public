#!/usr/bin/env python3
r"""
Generate editorial figure:
"Understanding the Primordial Power Spectrum"

Figure for Section 2 of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design specifications:
- Canvas: 1920 x 1140 px (16.0 x 9.5 in at 120 DPI).
- Typography: ALL text >= 14.0 pt across all labels, annotations, ticks, and math.
- Top banner: Hero title and conceptual subtitle.
- Panel A (left): Exact scale-invariant spectrum (n_s = 1.0, Harrison–Zel'dovich).
  Horizontal dimensionless spectrum with shaded equal-width logarithmic intervals,
  illustrating equal contributions to fluctuation variance (\Delta\sigma^2 = const).
  Normalized comoving wavenumber and wavelength directional indicators.
- Panel B (right): Nearly scale-invariant spectrum (n_s = 0.965, Planck 2018).
  Comparison with n_s = 1 reference, showing the authentic Planck-inferred "red tilt"
  where larger scales carry slightly more dimensionless power, normalized at pivot scale k_*.
  Pivot-scale marker with explicit Planck convention (k_* = 0.05 Mpc^-1).
- Uncluttered visual hierarchy: Clean, unboxed annotations in open whitespace,
  letting the curves, shaded intervals, and pivot scale communicate with maximum clarity.
- Bottom footnote banner: Concise note on normalization and inflationary interpretation.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "primordial_power_spectrum.png"


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure mathtext and typography
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    # Canvas: 1920 x 1140 px at 120 DPI (16.0 x 9.5 in)
    fig_w, fig_h = 16.0, 9.5
    dpi = 120
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'          # Hero headings
    DARK_SLATE = '#1e293b'    # Panel titles & primary labels
    SLATE = '#475569'         # Secondary text
    LIGHT_SLATE = '#64748b'   # Grid lines & subtle notes
    BORDER_COLOR = '#cbd5e1'  # Card borders
    CARD_BG = '#f8fafc'       # Banner & card backgrounds

    # Accents - Panel A: Scale-Invariant (Sky Blue)
    BLUE = '#0284c7'
    BLUE_DARK = '#0369a1'
    BLUE_BG = '#f0f9ff'
    BLUE_LIGHT = '#e0f2fe'
    BLUE_BORDER = '#bae6fd'

    # Accents - Panel B: Red Tilt (Warm Rose / Crimson)
    RED = '#e11d48'
    RED_DARK = '#be123c'
    RED_BG = '#fff1f2'
    RED_LIGHT = '#ffe4e6'
    RED_BORDER = '#fecdd3'

    # Reference Gray
    REF_GRAY = '#64748b'

    # -------------------------------------------------------------------------
    # 1. Top Header Banner (y: 0.900 - 0.982, height ~93 px)
    # -------------------------------------------------------------------------
    ax_head = fig.add_axes([0.025, 0.900, 0.950, 0.082])
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)
    ax_head.axis('off')

    title_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.009",
                               mutation_aspect=(0.950 * fig_w) / (0.082 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_head.add_patch(title_box)
    ax_head.text(0.50, 0.65, "UNDERSTANDING THE PRIMORDIAL POWER SPECTRUM",
                 color=NAVY, fontsize=21.0, fontweight='bold', ha='center', va='center')
    ax_head.text(0.50, 0.27, "Dimensionless curvature perturbation spectrum: scale-invariant model vs. observed red tilt",
                 color=SLATE, fontsize=15.5, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 2. Main Outer Panels (y: 0.035 - 0.880, height ~803 px)
    # -------------------------------------------------------------------------
    # Left Outer Panel Frame
    ax_frame_l = fig.add_axes([0.025, 0.035, 0.465, 0.845])
    ax_frame_l.set_facecolor('#ffffff')
    for spine in ax_frame_l.spines.values():
        spine.set_edgecolor(BORDER_COLOR)
        spine.set_linewidth(1.4)
    ax_frame_l.set_xticks([])
    ax_frame_l.set_yticks([])

    # Right Outer Panel Frame
    ax_frame_r = fig.add_axes([0.510, 0.035, 0.465, 0.845])
    ax_frame_r.set_facecolor('#ffffff')
    for spine in ax_frame_r.spines.values():
        spine.set_edgecolor(BORDER_COLOR)
        spine.set_linewidth(1.4)
    ax_frame_r.set_xticks([])
    ax_frame_r.set_yticks([])

    # -------------------------------------------------------------------------
    # 3. Panel Headers (inside frames at top)
    # -------------------------------------------------------------------------
    # Left Header Badge
    ax_top_l = fig.add_axes([0.038, 0.800, 0.439, 0.065])
    ax_top_l.set_xlim(0, 1)
    ax_top_l.set_ylim(0, 1)
    ax_top_l.axis('off')
    top_box_l = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.014",
                               mutation_aspect=(0.439 * fig_w) / (0.065 * fig_h),
                               clip_on=False,
                               facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.2)
    ax_top_l.add_patch(top_box_l)
    ax_top_l.text(0.50, 0.67, r"A. Scale-Invariant Spectrum ($n_s = 1$)",
                  color=BLUE_DARK, fontsize=17.5, fontweight='bold', ha='center', va='center')
    ax_top_l.text(0.50, 0.26, "Harrison–Zel'dovich: equal variance per logarithmic interval",
                  color=DARK_SLATE, fontsize=14.5, ha='center', va='center')

    # Right Header Badge
    ax_top_r = fig.add_axes([0.523, 0.800, 0.439, 0.065])
    ax_top_r.set_xlim(0, 1)
    ax_top_r.set_ylim(0, 1)
    ax_top_r.axis('off')
    top_box_r = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.014",
                               mutation_aspect=(0.439 * fig_w) / (0.065 * fig_h),
                               clip_on=False,
                               facecolor=RED_BG, edgecolor=RED_BORDER, linewidth=1.2)
    ax_top_r.add_patch(top_box_r)
    ax_top_r.text(0.50, 0.67, r"B. Nearly Scale-Invariant Spectrum ($n_s \simeq 0.965$)",
                  color=RED_DARK, fontsize=17.5, fontweight='bold', ha='center', va='center')
    ax_top_r.text(0.50, 0.26, r"Power-law model: slightly greater power on large cosmic scales",
                  color=DARK_SLATE, fontsize=14.5, ha='center', va='center')

    # -------------------------------------------------------------------------
    # 4. Plotting Area - Left Panel (Panel A)
    # -------------------------------------------------------------------------
    # Frame is x: 0.025 to 0.490. Plot: x: 0.098 to 0.463 (width 0.365)
    # y: 0.180 to 0.765 (height 0.585)
    ax_plot_l = fig.add_axes([0.098, 0.180, 0.365, 0.585])
    ax_plot_l.set_facecolor('#ffffff')

    y_min, y_max = 0.60, 1.30
    ax_plot_l.set_xlim(-2.0, 2.0)
    ax_plot_l.set_ylim(y_min, y_max)

    # Shaded equal logarithmic intervals (Decades: [-2, -1], [-1, 0], [0, 1], [1, 2])
    decades = [
        (-2.0, -1.0, '#e0f2fe', '#bae6fd', r"$\Delta\sigma_1^2$"),
        (-1.0,  0.0, '#f0f9ff', '#93c5fd', r"$\Delta\sigma_2^2$"),
        ( 0.0,  1.0, '#e0f2fe', '#bae6fd', r"$\Delta\sigma_3^2$"),
        ( 1.0,  2.0, '#f0f9ff', '#93c5fd', r"$\Delta\sigma_4^2$")
    ]

    for (x0, x1, fill_c, edge_c, label) in decades:
        # Shaded column from y_min to 1.0
        ax_plot_l.fill_between([x0, x1], [y_min, y_min], [1.0, 1.0],
                               facecolor=fill_c, edgecolor=edge_c, linewidth=1.2, alpha=0.85, zorder=1)
        # Vertical boundary dashed line
        ax_plot_l.axvline(x1, ymin=0, ymax=(1.0 - y_min)/(y_max - y_min),
                          color=BLUE_BORDER, linestyle='--', linewidth=1.2, zorder=2)

        # Variance label in each shaded interval (clean, unboxed text at y = 0.68)
        mid_x = 0.5 * (x0 + x1)
        ax_plot_l.text(mid_x, 0.68, label, color=BLUE_DARK, fontsize=15.0,
                       fontweight='bold', ha='center', va='center', zorder=4)

    # Boundary at x = -2
    ax_plot_l.axvline(-2.0, ymin=0, ymax=(1.0 - y_min)/(y_max - y_min),
                      color=BLUE_BORDER, linestyle='--', linewidth=1.2, zorder=2)

    # Horizontal spectrum line (n_s = 1)
    ax_plot_l.plot([-2.0, 2.0], [1.0, 1.0], color=BLUE, linewidth=3.5, zorder=5)

    # Note above spectrum line: 2 clean lines matching Panel B layout
    ax_plot_l.text(-1.85, 1.25, r"$\mathbf{Flat\ spectrum}\ (n_s = 1)$" + "\n" +
                   r"$\text{Equal power across all spatial scales}$",
                   fontsize=14.0, color=BLUE_DARK, ha='left', va='top', zorder=5)

    # Pivot point marker at (0, 1) -> k = k_*
    ax_plot_l.scatter([0.0], [1.0], color=BLUE_DARK, s=95, zorder=6, edgecolor='#ffffff', linewidth=1.5)

    # Pivot scale callout in Panel A
    ax_plot_l.annotate(r"$\mathbf{Pivot\ scale}\ k_*$" + "\n" +
                       r"$\mathcal{P}_{\mathcal{R}}(k_*) \equiv A_s\ (\mathbf{normalization})$",
                       xy=(0.0, 1.0), xytext=(0.0, 0.84),
                       ha='center', va='center', fontsize=14.0, fontweight='bold', color=DARK_SLATE,
                       arrowprops=dict(arrowstyle="->", color=DARK_SLATE, lw=1.3, shrinkA=4, shrinkB=6),
                       bbox=dict(boxstyle="round,pad=0.22,rounding_size=0.15",
                                 facecolor='#ffffff', edgecolor=BORDER_COLOR, lw=1.2),
                       zorder=7)

    # Ticks & labels
    ax_plot_l.set_xticks([-2.0, -1.0, 0.0, 1.0, 2.0])
    ax_plot_l.set_xticklabels([r"$10^{-2}$", r"$10^{-1}$", r"$10^{0}\ (k_*)$", r"$10^{1}$", r"$10^{2}$"],
                              fontsize=14.5, color=DARK_SLATE)
    ax_plot_l.set_yticks([0.6, 0.8, 1.0, 1.2])
    ax_plot_l.set_yticklabels([r"$0.6\,A_s$", r"$0.8\,A_s$", r"$1.0\,A_s$", r"$1.2\,A_s$"],
                              fontsize=14.5, color=DARK_SLATE)
    ax_plot_l.set_ylabel(r"Dimensionless Power $\mathcal{P}_{\mathcal{R}}(k)$",
                         fontsize=15.5, fontweight='bold', color=DARK_SLATE, labelpad=10)
    ax_plot_l.minorticks_off()
    ax_plot_l.grid(True, which='major', linestyle=':', linewidth=1.0, alpha=0.55, color=BORDER_COLOR, zorder=0)

    # Secondary scale indicator under X-axis (Panel A)
    ax_plot_l.text(0.50, -0.110, r"$\mathbf{Normalized\ Comoving\ Wavenumber}\ k / k_*\ (\mathbf{logarithmic\ scale})$",
                   transform=ax_plot_l.transAxes, fontsize=14.5, fontweight='bold', color=DARK_SLATE, ha='center', va='top')
    ax_plot_l.text(0.50, -0.175,
                   r"$\longleftarrow\ \mathbf{Larger\ scales}\ (\lambda \propto 1/k)\qquad\qquad\qquad \mathbf{Smaller\ scales}\ \longrightarrow$",
                   transform=ax_plot_l.transAxes, fontsize=14.0, fontweight='bold', color=SLATE, ha='center', va='top')

    # -------------------------------------------------------------------------
    # 5. Plotting Area - Right Panel (Panel B)
    # -------------------------------------------------------------------------
    # Frame is x: 0.510 to 0.975. Plot: x: 0.583 to 0.948 (width 0.365)
    # y: 0.180 to 0.765 (height 0.585)
    ax_plot_r = fig.add_axes([0.583, 0.180, 0.365, 0.585])
    ax_plot_r.set_facecolor('#ffffff')

    # Data: n_s = 0.965 => n_s - 1 = -0.035
    k_log = np.linspace(-2.0, 2.0, 500)
    p_tilt = 10.0**(-0.035 * k_log)

    ax_plot_r.set_xlim(-2.0, 2.0)
    ax_plot_r.set_ylim(y_min, y_max)

    # Reference line n_s = 1 (dashed)
    ax_plot_r.plot([-2.0, 2.0], [1.0, 1.0], color=REF_GRAY, linestyle='--', linewidth=2.0,
                   label=r"Scale-invariant reference ($n_s = 1$)", zorder=3)

    # Shaded gap between reference and observed tilt
    # Large scales (k < k_*, k_log < 0): tilt > 1 (Pink fill)
    k_sub0 = k_log[k_log <= 0.0]
    p_tilt_sub0 = p_tilt[k_log <= 0.0]
    ax_plot_r.fill_between(k_sub0, 1.0, p_tilt_sub0, facecolor=RED_LIGHT, edgecolor='none', alpha=0.65, zorder=2)

    # Small scales (k > k_*, k_log >= 0): tilt < 1 (Light slate fill)
    k_sup0 = k_log[k_log >= 0.0]
    p_tilt_sup0 = p_tilt[k_log >= 0.0]
    ax_plot_r.fill_between(k_sup0, p_tilt_sup0, 1.0, facecolor='#f1f5f9', edgecolor='none', alpha=0.75, zorder=2)

    # Power-law model curve (n_s = 0.965)
    ax_plot_r.plot(k_log, p_tilt, color=RED, linewidth=3.5,
                   label=r"Power-law model ($n_s \simeq 0.965$)", zorder=5)

    # Note above curve: "Slightly red-tilted" on 2 clean lines positioned over large scales
    ax_plot_r.text(-1.85, 1.25, r"$\mathbf{Slightly\ red\text{-}tilted\ spectrum}\ (n_s \simeq 0.965)$" + "\n" +
                   r"$\text{More power on large scales}\ (k < k_*)$",
                   fontsize=14.0, color=RED_DARK, ha='left', va='top', zorder=5)

    # Pivot point marker at (0, 1) -> k = k_*
    ax_plot_r.scatter([0.0], [1.0], color=RED_DARK, s=95, zorder=6, edgecolor='#ffffff', linewidth=1.5)

    # Pivot scale callout badge (clean, didactic, NO numerical clutter!)
    ax_plot_r.annotate(r"$\mathbf{Pivot\ scale}\ k_*$" + "\n" +
                       r"$\mathcal{P}_{\mathcal{R}}(k_*) \equiv A_s\ (\mathbf{normalization})$",
                       xy=(0.0, 1.0), xytext=(0.0, 0.84),
                       ha='center', va='center', fontsize=14.0, fontweight='bold', color=DARK_SLATE,
                       arrowprops=dict(arrowstyle="->", color=DARK_SLATE, lw=1.3, shrinkA=4, shrinkB=6),
                       bbox=dict(boxstyle="round,pad=0.22,rounding_size=0.15",
                                 facecolor='#ffffff', edgecolor=BORDER_COLOR, lw=1.2),
                       zorder=7)

    # Legend in Panel B - placed at lower left with high clarity
    leg_r = ax_plot_r.legend(loc='lower left', fontsize=14.0, framealpha=0.95, facecolor='#ffffff',
                             edgecolor=BORDER_COLOR)
    leg_r.set_zorder(7)

    # Ticks & labels
    ax_plot_r.set_xticks([-2.0, -1.0, 0.0, 1.0, 2.0])
    ax_plot_r.set_xticklabels([r"$10^{-2}$", r"$10^{-1}$", r"$10^{0}\ (k_*)$", r"$10^{1}$", r"$10^{2}$"],
                              fontsize=14.5, color=DARK_SLATE)
    ax_plot_r.set_yticks([0.6, 0.8, 1.0, 1.2])
    ax_plot_r.set_yticklabels([r"$0.6\,A_s$", r"$0.8\,A_s$", r"$1.0\,A_s$", r"$1.2\,A_s$"],
                              fontsize=14.5, color=DARK_SLATE)
    ax_plot_r.set_ylabel(r"Dimensionless Power $\mathcal{P}_{\mathcal{R}}(k)$",
                         fontsize=15.5, fontweight='bold', color=DARK_SLATE, labelpad=10)
    ax_plot_r.minorticks_off()
    ax_plot_r.grid(True, which='major', linestyle=':', linewidth=1.0, alpha=0.55, color=BORDER_COLOR, zorder=0)

    # Secondary scale indicator under X-axis (Panel B)
    ax_plot_r.text(0.50, -0.110, r"$\mathbf{Normalized\ Comoving\ Wavenumber}\ k / k_*\ (\mathbf{logarithmic\ scale})$",
                   transform=ax_plot_r.transAxes, fontsize=14.5, fontweight='bold', color=DARK_SLATE, ha='center', va='top')
    ax_plot_r.text(0.50, -0.175,
                   r"$\longleftarrow\ \mathbf{Larger\ scales}\ (\lambda \propto 1/k)\qquad\qquad\qquad \mathbf{Smaller\ scales}\ \longrightarrow$",
                   transform=ax_plot_r.transAxes, fontsize=14.0, fontweight='bold', color=SLATE, ha='center', va='top')

    # Save figure
    fig.savefig(output_path, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    print(f"[OK] Generated {output_path} ({fig_w * dpi:.0f} x {fig_h * dpi:.0f} px)")


if __name__ == "__main__":
    create_figure()
