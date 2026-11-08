#!/usr/bin/env python3
r"""
Generate conceptual figure:
"Evolution of Dark-Matter and Baryon Perturbations"

Figure for Section "Cold Dark Matter and the Transition to Matter Domination" of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design specifications:
- Canvas: 1890 x 1148 px (13.5 x 8.20 in at 140 DPI), matching the exact
  font size hierarchy of horizon_entry_perturbations.png:
  - 18.0 pt bold main title
  - 14.0 pt bold subtitle & era banner headers
  - 14.5 pt bold axis titles
  - 14.0-14.2 pt bold primary curve/region labels
  - 13.5-13.8 pt secondary annotations, formulas, and tick labels
- Single-panel schematic showing a representative mode that enters the Hubble
  radius during radiation domination:
  - Three dashed vertical markers: a_enter (horizon entry), a_eq
    (matter-radiation equality), and a_rec (recombination)
  - Era header bands at top: Radiation-dominated era (left of a_eq) and
    Matter-dominated era (right of a_eq)
  - Cold dark matter (CDM) curve (dark slate/black):
    - Modest superhorizon rise before a_enter
    - Slow logarithmic growth (\delta_c \propto \ln a, Meszaros effect) between
      a_enter and a_eq
    - Upward-curving rapid growth (\delta_c \propto a) after a_eq
  - Baryon curve (blue):
    - Tracks CDM before a_enter
    - Smooth acoustic oscillations between a_enter and a_rec (remaining below
      the CDM curve and continuing across a_eq because baryons remain tightly
      coupled to photons until recombination)
    - Smooth upward gravitational growth after a_rec as baryons fall into CDM
      potential wells
"""

from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "cdm_baryon_perturbation_evolution.png"


def cdm_curve(x, x_enter=1.55, x_eq=4.95):
    r"""
    Piecewise smooth schematic trajectory for Cold Dark Matter density contrast \delta_c:
    - Before x_enter: gentle rise up to y_enter = 2.95
    - Between x_enter and x_eq: slow logarithmic growth (\delta_c \propto \ln a)
    - After x_eq: steeper upward-curving growth (\delta_c \propto a on log-a axis),
      reaching y ~ 8.85 at x = 9.55 so it stays cleanly inside the plot frame.
    """
    x = np.asarray(x, dtype=float)
    y_enter = 2.95
    A = 1.45
    B = 0.38
    y_eq = y_enter + A * np.log(1.0 + B * (x_eq - x_enter))
    slope_eq = A * B / (1.0 + B * (x_eq - x_enter))

    y = np.zeros_like(x)

    # 1. Pre-entry segment (x <= x_enter)
    mask_pre = x <= x_enter
    dx_pre = x[mask_pre] - x_enter
    y[mask_pre] = y_enter + 0.48 * dx_pre + 0.08 * (dx_pre ** 2)

    # 2. Radiation-dominated subhorizon segment (x_enter < x <= x_eq)
    mask_rad = (x > x_enter) & (x <= x_eq)
    dx_rad = x[mask_rad] - x_enter
    y[mask_rad] = y_enter + A * np.log(1.0 + B * dx_rad)

    # 3. Matter-dominated segment (x > x_eq): curves upward cleanly without clipping y_max=10
    mask_mat = x > x_eq
    dx_mat = x[mask_mat] - x_eq
    y[mask_mat] = y_eq + slope_eq * dx_mat + 0.135 * (dx_mat ** 2) + 0.0055 * (dx_mat ** 3)

    return y


def baryon_curve(x, x_enter=1.55, x_rec=7.40):
    r"""
    Piecewise smooth schematic trajectory for Baryon perturbation amplitude \delta_b:
    - Before x_enter: tracks CDM closely (adiabatic perturbation)
    - Between x_enter and x_rec: 3.5 smooth acoustic oscillation cycles that
      turn downward after horizon entry as radiation pressure resists compression,
      staying strictly below the CDM curve
    - After x_rec: smooth rapid upward growth toward the CDM curve (falling into
      dark-matter gravitational potential wells)
    """
    x = np.asarray(x, dtype=float)
    y_enter = 2.95
    y = np.zeros_like(x)

    # 1. Pre-entry segment (x <= x_enter)
    mask_pre = x <= x_enter
    dx_pre = x[mask_pre] - x_enter
    y[mask_pre] = y_enter + 0.48 * dx_pre + 0.08 * (dx_pre ** 2)

    # 2. Acoustic oscillation segment (x_enter < x <= x_rec)
    mask_osc = (x > x_enter) & (x <= x_rec)
    s = (x[mask_osc] - x_enter) / (x_rec - x_enter)  # normalized [0, 1]
    # At s=0, y = 2.95 (crest of initial compression at horizon entry), then oscillates
    # around a baseline ~2.25 with gently damping amplitude so it stays strictly below CDM
    amp = 0.62 * (1.0 - 0.18 * s)
    baseline = 2.95 - amp * np.cos(0.0) - 0.08 * np.sin(0.5 * np.pi * s)
    # 3.5 cycles: cos(7 * pi * s) starts at +1 (s=0) and ends at -1 (s=1), or 6.5*pi ends at 0
    y[mask_osc] = baseline + amp * np.cos(6.5 * np.pi * s) + 0.08 * np.sin(6.5 * np.pi * s)

    # Value at x_rec (s = 1.0)
    s_end = 1.0
    amp_end = 0.62 * (1.0 - 0.18 * s_end)
    base_end = 2.95 - 0.62 - 0.08 * np.sin(0.5 * np.pi * s_end)
    y_rec = base_end + amp_end * np.cos(6.5 * np.pi * s_end) + 0.08 * np.sin(6.5 * np.pi * s_end)

    # 3. Post-recombination segment (x > x_rec): smooth turn upward toward CDM curve
    mask_post = x > x_rec
    dx_post = x[mask_post] - x_rec
    y[mask_post] = y_rec + 0.58 * dx_post + 0.78 * (dx_post ** 2) - 0.12 * (dx_post ** 3)

    return y


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure mathtext and typography (matching horizon_entry_perturbations.png)
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    # Canvas: 1890 x 1148 px at 140 DPI (13.5 x 8.20 in)
    fig_w, fig_h = 13.5, 8.20
    dpi = 140
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Curated Editorial Palette (matching horizon_entry_perturbations.png)
    NAVY = '#0f172a'          # Hero headings, primary axes & CDM curve
    DARK_SLATE = '#1e293b'    # Primary labels
    SLATE = '#475569'         # Secondary text
    AXIS_COLOR = '#334155'    # Axis spines and arrowheads
    BORDER_COLOR = '#cbd5e1'  # Card borders
    CARD_BG = '#f8fafc'       # Header background

    # Curve colors
    CDM_COLOR = '#1e293b'     # Solid dark slate/charcoal for CDM
    BARYON_BLUE = '#2563eb'   # Vibrant blue for Baryons
    BARYON_DEEP = '#1e3a8a'   # Deep blue for Baryon text labels

    # Vertical marker colors
    ENTER_COLOR = '#475569'
    EQ_COLOR = '#92400e'
    REC_COLOR = '#1e40af'

    # Era header bands
    RAD_BG = '#fffbeb'
    RAD_BORDER = '#fde68a'
    RAD_TEXT = '#92400e'

    MAT_BG = '#eff6ff'
    MAT_BORDER = '#bfdbfe'
    MAT_TEXT = '#1e3a8a'

    # Subtle background tints inside plot
    RAD_TINT = '#fffbeb'
    COUPLED_TINT = '#f8fafc'
    POST_REC_TINT = '#eff6ff'

    # -------------------------------------------------------------------------
    # 1. Top Header Banner (y: 0.896 - 0.980)
    # -------------------------------------------------------------------------
    ax_head = fig.add_axes([0.030, 0.896, 0.940, 0.084])
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)
    ax_head.axis('off')

    title_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.009",
                               mutation_aspect=(0.940 * fig_w) / (0.084 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_head.add_patch(title_box)
    ax_head.text(0.50, 0.65, "EVOLUTION OF COLD DARK MATTER AND BARYON PERTURBATIONS",
                 color=NAVY, fontsize=18.0, fontweight='bold', ha='center', va='center')
    ax_head.text(0.50, 0.27,
                 "Density perturbation entering the Hubble radius during radiation domination",
                 color=SLATE, fontsize=14.0, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 2. Era Header Bands Above the Plotting Region (y: 0.830 - 0.878)
    # -------------------------------------------------------------------------
    plot_left = 0.115
    plot_right = 0.960
    plot_w = plot_right - plot_left

    x_min, x_max = 0.0, 10.0
    y_min, y_max = 0.0, 10.0

    x_enter = 1.55
    x_eq = 4.95
    x_rec = 7.40

    ax_era = fig.add_axes([plot_left, 0.830, plot_w, 0.048])
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
    # 3. Main Plotting Area (y: 0.172 - 0.816)
    # -------------------------------------------------------------------------
    ax = fig.add_axes([plot_left, 0.172, plot_w, 0.644])
    ax.set_facecolor('#ffffff')
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Subtle background era shading
    ax.axvspan(x_min, x_eq, facecolor=RAD_TINT, alpha=0.55, zorder=0)
    ax.axvspan(x_eq, x_rec, facecolor=COUPLED_TINT, alpha=0.75, zorder=0)
    ax.axvspan(x_rec, x_max, facecolor=POST_REC_TINT, alpha=0.55, zorder=0)

    # -------------------------------------------------------------------------
    # 4. Three Structural Vertical Dashed Markers (a_enter, a_eq, a_rec)
    # -------------------------------------------------------------------------
    ax.plot([x_enter, x_enter], [y_min, y_max],
            color=ENTER_COLOR, linestyle='--', linewidth=2.1, alpha=0.80, zorder=2)
    ax.plot([x_eq, x_eq], [y_min, y_max],
            color=EQ_COLOR, linestyle='--', linewidth=2.3, alpha=0.85, zorder=2)
    ax.plot([x_rec, x_rec], [y_min, y_max],
            color=REC_COLOR, linestyle='--', linewidth=2.3, alpha=0.85, zorder=2)

    # Top region banner between a_eq and a_rec reinforcing that equality != recombination
    x_mid_eq_rec = 0.5 * (x_eq + x_rec)
    ax.annotate(
        "",
        xy=(x_rec - 0.08, 9.18), xytext=(x_eq + 0.08, 9.18),
        arrowprops=dict(arrowstyle="<->", color='#475569', lw=1.6),
        zorder=6
    )
    ax.text(x_mid_eq_rec, 9.18,
            "Baryons still coupled\nto photons",
            fontsize=13.5, fontweight='bold', color=DARK_SLATE,
            ha='center', va='center', linespacing=1.22,
            bbox=dict(boxstyle='round,pad=0.24,rounding_size=0.15',
                      facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.2, alpha=0.97),
            zorder=7)

    # -------------------------------------------------------------------------
    # 5. Cold Dark Matter (CDM) and Baryon Perturbation Curves
    # -------------------------------------------------------------------------
    x_baryon_pre = np.linspace(0.22, x_enter, 80)
    x_baryon_osc = np.linspace(x_enter, x_rec, 450)
    x_baryon_post = np.linspace(x_rec, 9.60, 180)

    y_baryon_pre = baryon_curve(x_baryon_pre, x_enter=x_enter, x_rec=x_rec)
    y_baryon_osc = baryon_curve(x_baryon_osc, x_enter=x_enter, x_rec=x_rec)
    y_baryon_post = baryon_curve(x_baryon_post, x_enter=x_enter, x_rec=x_rec)

    # Slight vertical offset on pre-entry baryon line so both dark-gray and blue are visible
    ax.plot(x_baryon_pre, y_baryon_pre - 0.09, color=BARYON_BLUE, linewidth=4.0,
            solid_capstyle='round', zorder=4)
    ax.plot(x_baryon_osc, y_baryon_osc, color=BARYON_BLUE, linewidth=4.2,
            solid_capstyle='round', zorder=5)
    ax.plot(x_baryon_post, y_baryon_post, color=BARYON_BLUE, linewidth=4.4,
            solid_capstyle='round', zorder=5)

    # Plot CDM curve (reaches y ~ 8.70 at x = 9.55, staying well inside y_max = 10)
    x_cdm = np.linspace(0.22, 9.55, 500)
    y_cdm = cdm_curve(x_cdm, x_enter=x_enter, x_eq=x_eq)
    ax.plot(x_cdm, y_cdm, color=CDM_COLOR, linewidth=4.6,
            solid_capstyle='round', zorder=6)

    # Key transition points (filled markers)
    y_ent_val = float(cdm_curve(x_enter, x_enter=x_enter, x_eq=x_eq))
    y_eq_cdm = float(cdm_curve(x_eq, x_enter=x_enter, x_eq=x_eq))
    y_rec_bar = float(baryon_curve(x_rec, x_enter=x_enter, x_rec=x_rec))

    # Marker at horizon entry (a_enter)
    ax.scatter([x_enter], [y_ent_val], s=145, color=CDM_COLOR,
               edgecolor='#ffffff', linewidth=2.3, zorder=9)
    # Marker on CDM curve at matter-radiation equality (a_eq)
    ax.scatter([x_eq], [y_eq_cdm], s=145, color=CDM_COLOR,
               edgecolor='#ffffff', linewidth=2.3, zorder=9)
    # Marker on Baryon curve at recombination (a_rec)
    ax.scatter([x_rec], [y_rec_bar], s=145, color=BARYON_BLUE,
               edgecolor='#ffffff', linewidth=2.3, zorder=9)

    # -------------------------------------------------------------------------
    # 6. Curve Labels & Physical Regime Annotations
    # -------------------------------------------------------------------------
    # A. Pre-entry superhorizon note (left of a_enter)
    ax.text(0.78, 4.15,
            "Superhorizon\nmode",
            fontsize=13.5, fontweight='bold', color=SLATE,
            ha='center', va='center', linespacing=1.22, zorder=7)

    # B. CDM slow logarithmic growth between a_enter and a_eq
    x_mid_rad = 0.5 * (x_enter + x_eq)
    ax.text(x_mid_rad, 6.20,
            "CDM: slow logarithmic growth",
            fontsize=13.8, fontweight='bold', color=CDM_COLOR,
            ha='center', va='center', zorder=7)
    ax.text(x_mid_rad, 5.42,
            "(Mészáros effect)",
            fontsize=13.5, color=SLATE,
            ha='center', va='center', zorder=7)
    ax.text(x_mid_rad, 4.52,
            r"$\delta_c \propto \ln a$",
            fontsize=14.5, fontweight='bold', color=CDM_COLOR,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.20,rounding_size=0.14',
                      facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.1, alpha=0.94),
            zorder=7)

    # C. CDM rapid growth after a_eq
    ax.text(6.18, 6.82,
            "Faster CDM growth",
            fontsize=13.8, fontweight='bold', color=CDM_COLOR,
            ha='center', va='center', zorder=7)
    ax.text(6.18, 5.88,
            r"$\delta_c \propto a$",
            fontsize=14.5, fontweight='bold', color=CDM_COLOR,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.22,rounding_size=0.14',
                      facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.1, alpha=0.94),
            zorder=7)

    # Primary CDM curve title near upper right, cleanly above the curve tip
    ax.text(8.68, 9.35,
            "Cold dark matter (CDM)",
            fontsize=14.2, fontweight='bold', color=CDM_COLOR,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.22,rounding_size=0.14',
                      facecolor='#ffffff', edgecolor='#94a3b8', linewidth=1.2, alpha=0.95),
            zorder=8)

    # D. Baryon acoustic oscillations between a_enter and a_eq (well inside the two dashed lines)
    ax.text(x_mid_rad, 0.85,
            "Photon–baryon\nacoustic oscillations",
            fontsize=13.6, fontweight='bold', color=BARYON_DEEP,
            ha='center', va='center', linespacing=1.24,
            bbox=dict(boxstyle='round,pad=0.22,rounding_size=0.14',
                      facecolor='#ffffff', edgecolor='#bfdbfe', linewidth=1.2, alpha=0.95),
            zorder=7)

    # E. Post-recombination baryon gravitational growth (right of a_rec)
    ax.text(8.15, 4.62,
            "Baryons",
            fontsize=14.2, fontweight='bold', color=BARYON_DEEP,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.20,rounding_size=0.14',
                      facecolor='#ffffff', edgecolor='#93c5fd', linewidth=1.2, alpha=0.95),
            zorder=8)

    ax.text(8.70, 1.35,
            "Baryons begin\ngravitational growth in\nCDM potential wells",
            fontsize=13.5, fontweight='bold', color=BARYON_DEEP,
            ha='center', va='center', linespacing=1.24,
            bbox=dict(boxstyle='round,pad=0.24,rounding_size=0.14',
                      facecolor='#ffffff', edgecolor='#bfdbfe', linewidth=1.2, alpha=0.96),
            zorder=7)

    # Arrow from post-recombination label to rising baryon curve
    x_bar_target = 8.48
    y_bar_target = float(baryon_curve(x_bar_target, x_enter=x_enter, x_rec=x_rec))
    ax.annotate(
        "",
        xy=(x_bar_target, y_bar_target - 0.14), xytext=(8.62, 2.26),
        arrowprops=dict(arrowstyle="->", color=BARYON_BLUE, lw=1.8,
                        connectionstyle="arc3,rad=-0.12", shrinkA=2, shrinkB=4),
        zorder=8
    )

    # -------------------------------------------------------------------------
    # 7. Axes Spines, Arrowheads, Ticks & Labels
    # -------------------------------------------------------------------------
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_edgecolor(AXIS_COLOR)
    ax.spines['left'].set_linewidth(2.0)
    ax.spines['bottom'].set_edgecolor(AXIS_COLOR)
    ax.spines['bottom'].set_linewidth(2.0)

    # Crisp arrowheads at the tips of the x-axis and y-axis
    ax.plot(1.0, 0.0, ">", transform=ax.transAxes, color=AXIS_COLOR,
            markersize=10, clip_on=False, zorder=10)
    ax.plot(0.0, 1.0, "^", transform=ax.transAxes, color=AXIS_COLOR,
            markersize=10, clip_on=False, zorder=10)

    # No numerical y-ticks (purely schematic amplitude)
    ax.set_yticks([])

    # Three key epoch ticks on the horizontal axis
    ax.set_xticks([x_enter, x_eq, x_rec])
    ax.set_xticklabels([
        r"$a_{\mathrm{enter}}$" + "\nhorizon entry",
        r"$a_{\mathrm{eq}}$" + "\nmatter–radiation equality",
        r"$a_{\mathrm{rec}}$" + "\nrecombination",
    ], fontsize=13.5, fontweight='bold', linespacing=1.25)

    for tick_label, col in zip(ax.get_xticklabels(), [DARK_SLATE, RAD_TEXT, BARYON_DEEP]):
        tick_label.set_color(col)

    ax.tick_params(axis='x', pad=7, length=6, width=1.6, colors=AXIS_COLOR)

    # Vertical axis label (matching horizon_entry_perturbations.png font hierarchy)
    fig.text(0.042, 0.494,
             "Perturbation amplitude " + r"$\delta$",
             fontsize=14.5, fontweight='bold', color=NAVY,
             ha='center', va='center', rotation=90)
    fig.text(0.068, 0.494,
             "(density contrast, schematic)",
             fontsize=13.5, color=SLATE,
             ha='center', va='center', rotation=90)

    # Horizontal axis label
    ax.text(0.46, -0.155,
            "Scale factor " + r"$a$" + " (logarithmic axis)",
            transform=ax.transAxes, fontsize=14.5, fontweight='bold', color=NAVY,
            ha='center', va='top')

    ax.text(0.995, -0.155,
            "increasing expansion " + r"$\longrightarrow$",
            transform=ax.transAxes, fontsize=13.5, color=SLATE,
            ha='right', va='top')

    # Save figure
    fig.savefig(output_path, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    print(f"[OK] Generated {output_path} ({fig_w * dpi:.0f} x {fig_h * dpi:.0f} px)")


if __name__ == "__main__":
    create_figure()
