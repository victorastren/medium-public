#!/usr/bin/env python3
r"""
Generate conceptual figure:
"Horizon Entry of Cosmological Perturbations"

Figure for Section "Radiation Domination and Horizon Entry" of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design specifications:
- Canvas: 1890 x 1092 px (13.5 x 7.80 in at 140 DPI), preserving the exact
  font size hierarchy (18.0 pt main title, 14.5 pt axis titles, 14.0-14.2 pt
  primary labels, 13.5 pt sub-labels and ticks).
- Two-regime Comoving Hubble radius curve c/(aH):
  - Rises as c/(aH) \propto a during radiation domination
  - Smoothly transitions around matter-radiation equality (a_eq) to
    c/(aH) \propto a^{1/2} during matter domination
- Three representative comoving wavelengths (\lambda_1 < \lambda_2 < \lambda_3):
  - \lambda_1: Short-wavelength mode (earliest entry, well before equality)
  - \lambda_2: Longer-wavelength mode (still enters during radiation domination)
  - \lambda_3: Sufficiently long-wavelength mode (enters after matter-radiation equality)
- Visual ordering on the horizontal axis:
  a_{enter,1} < a_{enter,2} < a_{eq} < a_{enter,3}
"""

from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "horizon_entry_perturbations.png"


def hubble_curve(x, x_eq=5.20, y_eq=5.85, m_rad=1.10, m_mat=0.55, width=0.40):
    """
    Smooth two-slope comoving Hubble radius curve in log-log coordinates:
    asymptotic slope m_rad for x << x_eq and m_mat = 0.5 * m_rad for x >> x_eq,
    passing through (x_eq, y_eq) with a gently rounded transition around equality.
    """
    dx = (x - x_eq) / width
    blend = width * np.log(np.cosh(dx))
    return y_eq + 0.5 * (m_rad + m_mat) * (x - x_eq) - 0.5 * (m_rad - m_mat) * blend


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure mathtext and typography (preserving exact font size hierarchy)
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    # Canvas: 1890 x 1092 px at 140 DPI (13.5 x 7.80 in)
    fig_w, fig_h = 13.5, 7.80
    dpi = 140
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'          # Hero headings & primary axes
    DARK_SLATE = '#1e293b'    # Primary labels
    SLATE = '#475569'         # Secondary text
    AXIS_COLOR = '#334155'    # Axis spines and arrowheads
    BORDER_COLOR = '#cbd5e1'  # Card borders
    CARD_BG = '#f8fafc'       # Header background
    EQ_COLOR = '#475569'      # Matter-radiation equality line & label

    # Comoving Hubble Radius (Blue)
    BLUE_DEEP = '#1e3a8a'
    BLUE_DARK = '#1d4ed8'
    BLUE = '#2563eb'

    # Short-wavelength mode \lambda_1 (Red)
    RED_DEEP = '#991b1b'
    RED_DARK = '#dc2626'
    RED = '#e11d48'

    # Longer-wavelength mode \lambda_2 (Green/Teal)
    GREEN_DEEP = '#065f46'
    GREEN_DARK = '#059669'

    # Sufficiently long-wavelength mode \lambda_3 (Purple/Indigo)
    PURPLE_DEEP = '#5b21b6'
    PURPLE_DARK = '#7c3aed'

    # Era header bands
    RAD_BG = '#fffbeb'
    RAD_BORDER = '#fde68a'
    RAD_TEXT = '#92400e'

    MAT_BG = '#eff6ff'
    MAT_BORDER = '#bfdbfe'
    MAT_TEXT = '#1e3a8a'

    # Region shading tints (separated by the Hubble radius curve)
    OUTSIDE_TINT = '#ffedd5'  # Warm soft amber/peach tint above the curve (\lambda > c/aH)
    INSIDE_TINT = '#e0f2fe'   # Cool soft sky-blue tint below the curve (\lambda < c/aH)

    # -------------------------------------------------------------------------
    # 1. Top Header Banner (y: 0.892 - 0.978)
    # -------------------------------------------------------------------------
    ax_head = fig.add_axes([0.030, 0.892, 0.940, 0.086])
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)
    ax_head.axis('off')

    title_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.009",
                               mutation_aspect=(0.940 * fig_w) / (0.086 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_head.add_patch(title_box)
    ax_head.text(0.50, 0.65, "HORIZON ENTRY OF COSMOLOGICAL PERTURBATIONS",
                 color=NAVY, fontsize=18.0, fontweight='bold', ha='center', va='center')
    ax_head.text(0.50, 0.27,
                 "As the comoving Hubble radius grows with expansion, shorter wavelengths enter earlier than longer wavelengths",
                 color=SLATE, fontsize=14.0, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 2. Era Header Bands Above the Plotting Region (y: 0.825 - 0.873)
    # -------------------------------------------------------------------------
    plot_left = 0.125
    plot_right = 0.955
    plot_w = plot_right - plot_left

    x_min, x_max = 0.0, 10.0
    y_min, y_max = 0.0, 10.0
    x_eq = 5.20  # Matter-radiation equality (~52% of horizontal plotting range)

    ax_era = fig.add_axes([plot_left, 0.825, plot_w, 0.048])
    ax_era.set_xlim(x_min, x_max)
    ax_era.set_ylim(0, 1)
    ax_era.axis('off')

    gap = 0.06
    era_aspect = ((plot_w * fig_w) / (x_max - x_min)) / (0.048 * fig_h)
    rad_box = FancyBboxPatch((0.02, 0.08), x_eq - gap - 0.02, 0.84,
                             boxstyle="round,pad=0.0,rounding_size=0.065",
                             mutation_aspect=era_aspect,
                             facecolor=RAD_BG, edgecolor=RAD_BORDER, linewidth=1.4)
    mat_box = FancyBboxPatch((x_eq + gap, 0.08), x_max - (x_eq + gap) - 0.02, 0.84,
                             boxstyle="round,pad=0.0,rounding_size=0.065",
                             mutation_aspect=era_aspect,
                             facecolor=MAT_BG, edgecolor=MAT_BORDER, linewidth=1.4)
    ax_era.add_patch(rad_box)
    ax_era.add_patch(mat_box)

    ax_era.text((x_eq - gap) / 2.0, 0.50, "Radiation-dominated era",
                color=RAD_TEXT, fontsize=14.0, fontweight='bold', ha='center', va='center')
    ax_era.text(x_eq + gap + (x_max - x_eq - gap) / 2.0, 0.50, "Matter-dominated era",
                color=MAT_TEXT, fontsize=14.0, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 3. Main Plotting Area (y: 0.148 - 0.812)
    # -------------------------------------------------------------------------
    ax = fig.add_axes([plot_left, 0.148, plot_w, 0.664])
    ax.set_facecolor('#ffffff')
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # -------------------------------------------------------------------------
    # 4. Two Subtle Background Tints Separated by the Two-Regime Hubble Curve
    # -------------------------------------------------------------------------
    x_grid = np.linspace(x_min, x_max, 500)
    y_grid = hubble_curve(x_grid, x_eq=x_eq)

    # Above the blue curve: Outside the Hubble radius (\lambda > c/aH)
    ax.fill_between(x_grid, np.clip(y_grid, y_min, y_max), y_max,
                    facecolor=OUTSIDE_TINT, alpha=0.60, zorder=0)

    # Below the blue curve: Inside the Hubble radius (\lambda < c/aH)
    ax.fill_between(x_grid, y_min, np.clip(y_grid, y_min, y_max),
                    facecolor=INSIDE_TINT, alpha=0.65, zorder=0)

    # -------------------------------------------------------------------------
    # 5. Matter-Radiation Equality Vertical Dashed Line (a_eq)
    # -------------------------------------------------------------------------
    ax.plot([x_eq, x_eq], [y_min, y_max],
            color=EQ_COLOR, linestyle='--', linewidth=2.2, alpha=0.85, zorder=3)

    # Compact label near the top of the equality line
    ax.text(x_eq, 9.18,
            "Matter–radiation equality\n" + r"$a_{\mathrm{eq}}$",
            fontsize=13.5, fontweight='bold', color=DARK_SLATE,
            ha='center', va='center', linespacing=1.28,
            bbox=dict(boxstyle='round,pad=0.26,rounding_size=0.16',
                      facecolor='#ffffff', edgecolor='#94a3b8', linewidth=1.3, alpha=0.96),
            zorder=8)

    # -------------------------------------------------------------------------
    # 6. Comoving Hubble Radius Curve (Blue, Slope 1 -> Slope 1/2)
    # -------------------------------------------------------------------------
    x_line = np.linspace(0.14, 9.86, 400)
    y_line = hubble_curve(x_line, x_eq=x_eq)
    ax.plot(x_line, y_line, color=BLUE, linewidth=4.6, solid_capstyle='round', zorder=5)

    # Main Hubble-radius label near the upper right of the blue curve
    x_target_h = 9.05
    y_target_h = float(hubble_curve(x_target_h, x_eq=x_eq))
    ax.text(8.30, 9.38, "Comoving Hubble radius",
            fontsize=14.2, fontweight='bold', color=BLUE_DEEP, ha='center', va='center', zorder=8)
    ax.text(8.30, 8.56, r"$\dfrac{c}{aH}$",
            fontsize=14.2, fontweight='bold', color=BLUE_DEEP, ha='center', va='center', zorder=8)
    ax.annotate(
        "",
        xy=(x_target_h, y_target_h), xytext=(8.52, 8.18),
        arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.8,
                        connectionstyle="arc3,rad=-0.10", shrinkA=2, shrinkB=5),
        zorder=8
    )

    # Two small unobtrusive slope annotations near the two segments of the blue curve
    # Radiation-era segment
    ax.text(1.50, 0.82,
            r"$\dfrac{c}{aH} \propto a$",
            fontsize=13.8, fontweight='bold', color=BLUE_DEEP,
            ha='left', va='center', zorder=7)

    # Matter-era segment
    ax.text(5.38, 4.95,
            r"$\dfrac{c}{aH} \propto a^{1/2}$",
            fontsize=13.8, fontweight='bold', color=BLUE_DEEP,
            ha='left', va='center', zorder=8)

    # -------------------------------------------------------------------------
    # 7. Three Representative Perturbation Wavelengths (\lambda_1, \lambda_2, \lambda_3)
    # -------------------------------------------------------------------------
    # Compute exact crossings on the smooth Hubble curve:
    # \lambda_1: crosses well before equality
    x_enter1 = 2.25
    y_lam1 = float(hubble_curve(x_enter1, x_eq=x_eq))

    # \lambda_2: crosses before equality
    x_enter2 = 3.78
    y_lam2 = float(hubble_curve(x_enter2, x_eq=x_eq))

    # \lambda_3: crosses after equality
    x_enter3 = 6.92
    y_lam3 = float(hubble_curve(x_enter3, x_eq=x_eq))

    modes = [
        (x_enter1, y_lam1, -0.14, RED, RED_DARK, RED_DEEP,
         "Short-wavelength mode " + r"$(\lambda_1)$",
         "earlier entry"),
        (x_enter2, y_lam2, -0.15, GREEN_DARK, GREEN_DARK, GREEN_DEEP,
         "Longer-wavelength mode " + r"$(\lambda_2)$",
         "still enters during radiation domination"),
        (x_enter3, y_lam3, -0.34, PURPLE_DARK, PURPLE_DARK, PURPLE_DEEP,
         "Sufficiently long-wavelength mode " + r"$(\lambda_3)$",
         "enters after matter–radiation equality"),
    ]

    for x_ent, y_lam, dy_lbl, col_line, col_sub, col_text, title_lbl, sub_lbl in modes:
        # Uniform horizontal line across the plotting region
        ax.plot([0.20, 9.80], [y_lam, y_lam],
                color=col_line, linestyle='-', linewidth=3.4, solid_capstyle='round', zorder=4)

        # Dotted vertical guide down to the x-axis
        ax.plot([x_ent, x_ent], [y_min, y_lam],
                color=col_sub, linestyle=':', linewidth=1.8, alpha=0.82, zorder=2)

        # Filled circle at the horizon-entry crossing
        ax.scatter([x_ent], [y_lam], s=155, color=col_line,
                   edgecolor='#ffffff', linewidth=2.4, zorder=9)

        # Mode label right-aligned just below each mode line
        ax.text(9.78, y_lam + dy_lbl,
                f"{title_lbl}\n{sub_lbl}",
                fontsize=13.6, fontweight='bold', color=col_text,
                ha='right', va='top', linespacing=1.28,
                bbox=dict(boxstyle='round,pad=0.12', facecolor='#ebf7fe',
                          edgecolor='none', alpha=1.0),
                zorder=7)

    # -------------------------------------------------------------------------
    # 8. Region Annotations Directly Inside the Shaded Areas
    # -------------------------------------------------------------------------
    # Upper-left shaded area (above the blue curve, where \lambda > c/(aH))
    ax.text(2.15, 9.35,
            "Outside the Hubble radius",
            fontsize=14.2, fontweight='bold', color='#7c2d12', ha='center', va='center', zorder=6)
    ax.text(2.15, 8.52,
            r"$\lambda > \dfrac{c}{aH}$",
            fontsize=14.2, fontweight='bold', color='#7c2d12', ha='center', va='center', zorder=6)
    ax.text(2.15, 7.68,
            r"$\mathcal{R}$" + " approximately conserved for adiabatic modes",
            fontsize=13.5, color='#9a3412', ha='center', va='center', zorder=6)

    # Lower-right shaded area (below the blue curve, where \lambda < c/(aH))
    # Positioned across the a_eq line (x_eq = 5.20) so vertical lines pass between words
    ax.text(5.11, 0.80,
            "Inside the",
            fontsize=14.2, fontweight='bold', color=BLUE_DEEP, ha='right', va='center',
            zorder=6)
    ax.text(5.29, 0.80,
            "Hubble radius",
            fontsize=14.2, fontweight='bold', color=BLUE_DEEP, ha='left', va='center',
            zorder=6)
    ax.text(7.02, 0.80,
            r"$\lambda < \dfrac{c}{aH}$",
            fontsize=14.2, fontweight='bold', color=BLUE_DEEP, ha='left', va='center', zorder=6)

    # -------------------------------------------------------------------------
    # 9. Axes Spines, Arrowheads, Ticks & Labels
    # -------------------------------------------------------------------------
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_edgecolor(AXIS_COLOR)
    ax.spines['left'].set_linewidth(2.0)
    ax.spines['bottom'].set_edgecolor(AXIS_COLOR)
    ax.spines['bottom'].set_linewidth(2.0)

    # Add crisp arrowheads at the tips of the x-axis (10, 0) and y-axis (0, 10)
    ax.plot(1.0, 0.0, ">", transform=ax.transAxes, color=AXIS_COLOR,
            markersize=10, clip_on=False, zorder=10)
    ax.plot(0.0, 1.0, "^", transform=ax.transAxes, color=AXIS_COLOR,
            markersize=10, clip_on=False, zorder=10)

    ax.set_xticks([x_enter1, x_enter2, x_eq, x_enter3])
    ax.set_xticklabels([
        r"$a_{\mathrm{enter},1}$",
        r"$a_{\mathrm{enter},2}$",
        r"$a_{\mathrm{eq}}$",
        r"$a_{\mathrm{enter},3}$",
    ], fontsize=13.5, fontweight='bold')

    for tick_label, col in zip(ax.get_xticklabels(), [RED_DEEP, GREEN_DEEP, DARK_SLATE, PURPLE_DEEP]):
        tick_label.set_color(col)

    ax.set_yticks([y_lam1, y_lam2, y_lam3])
    ax.set_yticklabels([
        r"$\lambda_1$",
        r"$\lambda_2$",
        r"$\lambda_3$",
    ], fontsize=13.5, fontweight='bold')
    for tick_label, col in zip(ax.get_yticklabels(), [RED_DEEP, GREEN_DEEP, PURPLE_DEEP]):
        tick_label.set_color(col)

    ax.tick_params(axis='x', pad=7, length=6, width=1.6, colors=AXIS_COLOR)
    ax.tick_params(axis='y', pad=7, length=6, width=1.6, colors=AXIS_COLOR)

    # Vertical axis label (logarithmic Comoving scale, >= 14 pt)
    fig.text(0.040, 0.480,
             "Comoving scale (log)",
             fontsize=14.5, fontweight='bold', color=NAVY,
             ha='center', va='center', rotation=90)
    fig.text(0.066, 0.480,
             r"$(c/aH,\ \lambda)$",
             fontsize=13.5, color=SLATE,
             ha='center', va='center', rotation=90)

    # Horizontal axis label (Scale factor, log a, >= 14 pt)
    ax.text(0.46, -0.112,
            "Scale factor " + r"$(\log a)$",
            transform=ax.transAxes, fontsize=14.5, fontweight='bold', color=NAVY,
            ha='center', va='top')

    ax.text(0.995, -0.112,
            "increasing expansion " + r"$\longrightarrow$",
            transform=ax.transAxes, fontsize=13.5, color=SLATE,
            ha='right', va='top')

    # Save figure
    fig.savefig(output_path, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    print(f"[OK] Generated {output_path} ({fig_w * dpi:.0f} x {fig_h * dpi:.0f} px)")


if __name__ == "__main__":
    create_figure()
