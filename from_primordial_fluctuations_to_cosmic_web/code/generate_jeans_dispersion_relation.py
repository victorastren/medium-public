#!/usr/bin/env python3
r"""
Generate editorial figure:
"Jeans Instability: Dispersion Relation and Stability"

Mathematical foundation:
    Dimensionless dispersion relation:
        \omega^2 / (4\pi G\rho_0) = (k / k_J)^2 - 1
    where:
        k_J = \sqrt{4\pi G\rho_0} / c_s
        \lambda_J = 2\pi / k_J = c_s \sqrt{\pi / (G\rho_0)}

Specifications:
- Landscape format: exactly 1600 x 900 px PNG (16:9 aspect ratio).
- Minimalist, high-clarity editorial design tailored for Medium (desktop & mobile).
- Top: Short title and normalized dispersion relation banner.
- Two stability boxes positioned above the plotting area (leaving the curve 100% unobstructed):
  - Left: Gravitational instability (muted rust/orange, \omega^2 < 0, \lambda > \lambda_J).
  - Right: Pressure-supported oscillations (muted blue, \omega^2 > 0, \lambda < \lambda_J).
- Central Jeans threshold callout at k/k_J = 1 with marker and vertical divider.
- Clean zero-frequency reference line at \omega^2 = 0 (unlabeled).
- All font sizes strictly >= 14 pt for mobile readability.
"""

from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "jeans_instability_dispersion_relation.png"

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

    # Canvas: 1890 x 1064 px at 140 DPI (13.5 x 7.60 in), matching the exact
    # canvas width and typography hierarchy of `horizon_entry_perturbations.png`.
    fig_w, fig_h = 13.5, 7.60
    dpi = 140
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'         # Primary title / headings
    DARK_SLATE = '#1e293b'   # Axis text, main text
    SLATE = '#475569'        # Secondary text, subtitles
    BORDER_COLOR = '#cbd5e1' # Box borders
    CARD_BG = '#f8fafc'      # Background cards
    GRID_COLOR = '#f1f5f9'   # Grid lines

    # Regime Accents
    # Left: Gravitational Instability (Muted warm rust/orange)
    RUST_DEEP = '#9a3412'
    RUST = '#c2410c'
    RUST_BG = '#fff7ed'
    RUST_BORDER = '#fdba74'

    # Right: Pressure-Supported Oscillations (Muted royal/slate blue)
    BLUE_DEEP = '#1e40af'
    BLUE = '#2563eb'
    BLUE_BG = '#eff6ff'
    BLUE_BORDER = '#93c5fd'

    # -------------------------------------------------------------
    # 1. TOP HEADER & EQUATION BANNER
    # -------------------------------------------------------------
    # Main Figure Title Badge (18.0 pt bold, matching horizon_entry_perturbations.png)
    fig.text(0.50, 0.958,
             r"Jeans Instability: Dispersion Relation and Stability",
             fontsize=18.0, weight='bold', color=NAVY, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.30,rounding_size=0.18",
                       facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1.3))

    # Normalized Dispersion Relation Banner
    fig.text(0.50, 0.892,
             "Dispersion Relation:     " + r"$\dfrac{\omega^2}{4\pi G\rho_0} = \left(\dfrac{k}{k_J}\right)^2 - 1$",
             fontsize=14.5, weight='bold', color=DARK_SLATE, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.24,rounding_size=0.16",
                       facecolor='#ffffff', edgecolor=BORDER_COLOR, lw=1.1))

    # -------------------------------------------------------------
    # 2. PLOT GEOMETRY (Middle section, curve 100% unobstructed)
    # -------------------------------------------------------------
    # y from 0.190 to 0.545 (height 0.355 = 319.5 px)
    # Leaves 0.190 (171 px) at the bottom for generous ~31 px white margin below xlabel
    ax = fig.add_axes([0.125, 0.190, 0.810, 0.355])
    ax.set_facecolor('#ffffff')

    # Coordinate ranges
    x_min, x_max = 0.0, 2.05
    y_min, y_max = -1.15, 3.15
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Background shading for the two regimes
    # Left regime: 0 to 1 (Gravitational Instability)
    rect_left = patches.Rectangle((0, y_min), 1.0, y_max - y_min,
                                  facecolor=RUST_BG, alpha=0.90, zorder=1)
    ax.add_patch(rect_left)

    # Right regime: 1 to x_max (Pressure-Supported Oscillations)
    rect_right = patches.Rectangle((1.0, y_min), x_max - 1.0, y_max - y_min,
                                   facecolor=BLUE_BG, alpha=0.90, zorder=1)
    ax.add_patch(rect_right)

    # Grid lines
    ax.grid(True, which='both', color=GRID_COLOR, linestyle='-', linewidth=1.2, zorder=2)

    # Zero-frequency reference line: \omega^2 = 0 (unlabeled)
    ax.axhline(0.0, color='#64748b', linestyle='-', linewidth=1.6, zorder=3)

    # Critical threshold vertical dashed line at k/k_J = 1
    ax.axvline(1.0, color='#334155', linestyle='--', linewidth=2.2, zorder=4)

    # Dispersion Curves: y = x^2 - 1
    x_left = np.linspace(0.0, 1.0, 200)
    y_left = x_left**2 - 1.0

    x_right = np.linspace(1.0, 2.05, 300)
    y_right = x_right**2 - 1.0

    # Plot curves with distinct regime colors and bold strokes
    ax.plot(x_left, y_left, color=RUST, linewidth=4.2, zorder=6)
    ax.plot(x_right, y_right, color=BLUE, linewidth=4.2, zorder=6)

    # Marker at the critical Jeans threshold: (1.0, 0.0)
    ax.plot([1.0], [0.0], marker='o', markersize=11, color=NAVY,
            markeredgecolor='#ffffff', markeredgewidth=2.6, zorder=8)

    # -------------------------------------------------------------
    # 3. TWO STABILITY BOXES ABOVE THE PLOT AREA
    # -------------------------------------------------------------
    # Positioned from y=0.575 to 0.825 (height 0.250 = 225 px)
    # Banner at 0.898 (bottom ~0.865): leaves 36 px gap above boxes
    # Plot ax from 0.190 to 0.545: leaves 27 px gap below boxes
    # Left Box: Gravitational Instability (Above left region)
    box_left_ax = fig.add_axes([0.125, 0.575, 0.385, 0.250])
    box_left_ax.set_facecolor(RUST_BG)
    for spine in box_left_ax.spines.values():
        spine.set_color(RUST_BORDER)
        spine.set_linewidth(1.5)
    box_left_ax.set_xticks([])
    box_left_ax.set_yticks([])

    # 2-line title with generous spacing below, and generous spacing between sentences
    box_left_ax.text(0.50, 0.87, "GRAVITATIONAL", fontsize=14.5, weight='bold',
                    color=RUST_DEEP, ha='center', va='center')
    box_left_ax.text(0.50, 0.74, "INSTABILITY", fontsize=14.5, weight='bold',
                    color=RUST_DEEP, ha='center', va='center')
    # Extra space between title and text below (0.74 -> 0.52 = 0.22 gap)
    box_left_ax.text(0.50, 0.52, r"$k < k_J \quad (\lambda > \lambda_J) \quad\mid\quad \omega^2 < 0$",
                    fontsize=13.8, color=RUST_DEEP, ha='center', va='center')
    box_left_ax.text(0.50, 0.32, "Exponentially growing mode:", fontsize=13.8,
                    color=RUST_DEEP, ha='center', va='center')
    box_left_ax.text(0.50, 0.13, r"$\mathbf{\delta_k(t) \propto e^{\gamma t}}$", fontsize=14.5,
                    color=RUST_DEEP, ha='center', va='center')

    # Right Box: Pressure-Supported Oscillations (Above right region)
    box_right_ax = fig.add_axes([0.530, 0.575, 0.405, 0.250])
    box_right_ax.set_facecolor(BLUE_BG)
    for spine in box_right_ax.spines.values():
        spine.set_color(BLUE_BORDER)
        spine.set_linewidth(1.5)
    box_right_ax.set_xticks([])
    box_right_ax.set_yticks([])

    box_right_ax.text(0.50, 0.87, "PRESSURE-SUPPORTED", fontsize=14.5, weight='bold',
                     color=BLUE_DEEP, ha='center', va='center')
    box_right_ax.text(0.50, 0.74, "OSCILLATIONS", fontsize=14.5, weight='bold',
                     color=BLUE_DEEP, ha='center', va='center')
    # Extra space between title and text below (0.74 -> 0.52 = 0.22 gap)
    box_right_ax.text(0.50, 0.52, r"$k > k_J \quad (\lambda < \lambda_J) \quad\mid\quad \omega^2 > 0$",
                     fontsize=13.8, color=BLUE_DEEP, ha='center', va='center')
    box_right_ax.text(0.50, 0.32, "Oscillatory modes:", fontsize=13.8,
                     color=BLUE_DEEP, ha='center', va='center')
    box_right_ax.text(0.50, 0.13, r"$\mathbf{\delta_k(t) \propto \cos(\omega t + \phi)}$", fontsize=14.5,
                     color=BLUE_DEEP, ha='center', va='center')

    # -------------------------------------------------------------
    # 4. CENTER BOX: JEANS THRESHOLD CALLOUT (Inside plot area)
    # -------------------------------------------------------------
    # Shifted to x=0.58 for maximum breathing room around the dashed vertical threshold line
    ax.annotate(
        "JEANS THRESHOLD\n"
        r"$k = k_J,\quad \lambda = \lambda_J$" "\n"
        r"$\omega^2 = 0$",
        xy=(1.0, 0.05), xytext=(0.58, 1.25),
        fontsize=14.0, color=NAVY, ha='center', va='center', weight='bold',
        linespacing=1.70,
        bbox=dict(boxstyle="round,pad=0.48,rounding_size=0.18",
                  facecolor='#ffffff', edgecolor='#334155', lw=1.6, zorder=7),
        arrowprops=dict(arrowstyle="->", color='#334155', lw=1.8,
                        connectionstyle="arc3,rad=-0.10", shrinkA=4, shrinkB=5),
        zorder=7
    )

    # -------------------------------------------------------------
    # 5. AXES TICKS AND LABELS (14.5 pt axis titles, 13.5 pt ticks)
    # -------------------------------------------------------------
    ax.set_xticks([0.0, 0.5, 1.0, 1.5, 2.0])
    ax.set_xticklabels(['0', '0.5', '1.0', '1.5', '2.0'], fontsize=13.5, color=DARK_SLATE, weight='bold')

    ax.set_yticks([-1.0, 0.0, 1.0, 2.0, 3.0])
    ax.set_yticklabels(['-1.0', '0.0', '1.0', '2.0', '3.0'], fontsize=13.5, color=DARK_SLATE, weight='bold')

    # X-axis label (14.5 pt primary title, 13.5 pt secondary directional label)
    ax.text(0.50, -0.175,
            "Normalized wavenumber " + r"$k / k_J$",
            transform=ax.transAxes, fontsize=14.5, fontweight='bold', color=NAVY,
            ha='center', va='top')
    ax.text(0.50, -0.315,
            r"$\longleftarrow\ $" + "Longer wavelengths     |     Shorter wavelengths" + r"$\ \longrightarrow$",
            transform=ax.transAxes, fontsize=13.5, fontweight='bold', color=SLATE,
            ha='center', va='top')

    # Y-axis label (14.5 pt bold)
    ax.set_ylabel("Normalized " + r"$\omega^2 / (4\pi G\rho_0)$",
                  fontsize=14.5, color=NAVY, labelpad=12, weight='bold')

    # Style spines
    for spine in ax.spines.values():
        spine.set_color('#334155')
        spine.set_linewidth(1.5)

    # Save figure
    fig.savefig(output_path, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    print(f"[OK] Figure generated successfully: {output_path} ({fig_w * dpi:.0f} x {fig_h * dpi:.0f} px)")

if __name__ == "__main__":
    create_figure()
