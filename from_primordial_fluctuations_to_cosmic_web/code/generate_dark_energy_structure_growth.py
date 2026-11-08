#!/usr/bin/env python3
r"""
Generate two-panel scientific figure:
"Dark Energy and the Suppression of Structure Growth"

Figure for Section "Dark Energy and the Slowing of Structure Growth" of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design & Scientific Specifications:
- Canvas: 1890 x 1120 px at 140 DPI (13.5 x 8.00 in), matching the exact
  typography and font size hierarchy of `matter_transfer_function_power_spectrum.png`,
  `cdm_baryon_perturbation_evolution.png`, and `anisotropic_collapse_cosmic_web.png`:
  - 18.0 pt bold main title
  - 14.0 pt bold subtitle
  - 15.5 pt bold panel header titles ("A  Changing cosmic composition", "B  Suppression of linear growth")
  - 14.5 pt bold axis titles
  - 14.0-14.2 pt bold primary curve/region labels
  - 13.5-13.8 pt secondary annotations, formulas, and tick labels
- Representative spatially flat \Lambda CDM model (\Omega_{m,0} = 0.3, \Omega_{\Lambda,0} = 0.7),
  explicitly labelled as illustrative.
- Panel A ("A  Changing cosmic composition"):
  - Horizontal axis: Scale factor a from 0.1 to 1.0
  - Vertical axis: Density parameter \Omega from 0 to 1
  - Curves: \Omega_m(a) and \Omega_\Lambda(a), directly labelled
  - Distinguishes two key late-time transitions:
    1. Vertical dashed line at a \simeq 0.60: "Accelerated expansion begins"
    2. Intersection of the two curves at a \simeq 0.75: "\Omega_m = \Omega_\Lambda"
- Panel B ("B  Suppression of linear growth"):
  - Horizontal axis: Scale factor a from 0.1 to 1.0 (aligned with Panel A)
  - Vertical axis: Linear growth factor D(a), with both models normalized to the
    same amplitude early in matter domination (at a = 0.1)
  - Curves:
    1. Matter-only universe: D(a) \propto a
    2. \Lambda CDM growing mode
  - Same vertical dashed marker at a \simeq 0.60 ("Accelerated expansion begins")
"""

from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "dark_energy_structure_growth.png"


def compute_cosmology_curves(a_grid, omega_m0=0.3, omega_l0=0.7, a_norm=0.1):
    r"""
    Compute exact flat-\Lambda CDM background density fractions \Omega_m(a), \Omega_\Lambda(a)
    and exact linear growth factor D(a) (via Heath 1977 integral), normalized to match
    the matter-only growing mode D_{\mathrm{matter}}(a) = a at a = a_norm.
    """
    a = np.asarray(a_grid, dtype=float)
    rho_m_rel = omega_m0 * (a ** -3)
    e2 = rho_m_rel + omega_l0
    omega_m = rho_m_rel / e2
    omega_l = omega_l0 / e2

    # Compute exact Heath (1977) linear growth factor integral on a fine grid from a_min_int -> 1
    n_int = 4000
    a_int = np.linspace(1e-5, 1.05, n_int)
    e_int = np.sqrt(omega_m0 * (a_int ** -3) + omega_l0)
    integrand = 1.0 / ((a_int * e_int) ** 3)
    # Cumulative trapezoidal integration
    cum_int = np.zeros_like(a_int)
    da = np.diff(a_int)
    cum_int[1:] = np.cumsum(0.5 * (integrand[:-1] + integrand[1:]) * da)
    d_raw = 2.5 * omega_m0 * e_int * cum_int

    # Interpolate onto a_grid and normalize so D_{\Lambda CDM}(a_norm) = a_norm
    d_norm_val = float(np.interp(a_norm, a_int, d_raw))
    d_lcdm = np.interp(a, a_int, d_raw) * (a_norm / d_norm_val)
    d_matter = a.copy()

    return omega_m, omega_l, d_matter, d_lcdm


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure mathtext and typography (matching matter_transfer_function_power_spectrum.png)
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    # Canvas: 1890 x 1120 px at 140 DPI (13.5 x 8.00 in)
    fig_w, fig_h = 13.5, 8.00
    dpi = 140
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Curated Editorial Palette (matching earlier figures in the article)
    NAVY = '#0f172a'          # Hero headings, axis titles
    DARK_SLATE = '#1e293b'    # Primary text & matter curve
    SLATE = '#475569'         # Secondary text
    AXIS_COLOR = '#334155'    # Axis spines and arrowheads
    BORDER_COLOR = '#cbd5e1'  # Card borders
    CARD_BG = '#f8fafc'       # Header background

    # Curve & annotation colors
    BLUE_DEEP = '#1e3a8a'
    BLUE_DARK = '#1d4ed8'
    BLUE = '#2563eb'          # \Omega_\Lambda(a) and \Lambda CDM growth curve
    BLUE_LIGHT = '#bfdbfe'
    BLUE_BG = '#eff6ff'

    MATTER_ONLY_COLOR = '#dc2626'  # Dashed crimson reference for matter-only D(a) \propto a
    MATTER_ONLY_DEEP = '#991b1b'

    ACC_COLOR = '#92400e'     # Warm amber-brown for onset of accelerated expansion
    ACC_BG = '#fffbeb'
    ACC_BORDER = '#fde68a'

    # -------------------------------------------------------------------------
    # 1. Top Header Banner (y: 0.894 - 0.980)
    # -------------------------------------------------------------------------
    ax_head = fig.add_axes([0.025, 0.894, 0.950, 0.086])
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)
    ax_head.axis('off')

    title_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.009",
                               mutation_aspect=(0.950 * fig_w) / (0.086 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_head.add_patch(title_box)
    ax_head.text(0.50, 0.65, "DARK ENERGY AND THE SUPPRESSION OF STRUCTURE GROWTH",
                 color=NAVY, fontsize=18.0, fontweight='bold', ha='center', va='center')
    ax_head.text(0.50, 0.26,
                 "Illustrative spatially flat " + r"$\Lambda\mathrm{CDM}$"
                 + " cosmology (" + r"$\Omega_{m,0} = 0.3,\ \Omega_{\Lambda,0} = 0.7$" + ")",
                 color=SLATE, fontsize=14.0, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 2. Outer Card Frames & Compact Panel Header Badges (Panel A & Panel B)
    # -------------------------------------------------------------------------
    card_bottom = 0.030
    card_height = 0.844
    card_w = 0.464
    left_x = 0.025
    right_x = 0.511

    # Left Card Frame (Panel A)
    ax_card_a = fig.add_axes([left_x, card_bottom, card_w, card_height], zorder=0)
    ax_card_a.set_xlim(0, 1)
    ax_card_a.set_ylim(0, 1)
    ax_card_a.axis('off')
    ax_card_a.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0,
                                  facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4))
    hdr_a = FancyBboxPatch((0.026, 0.924), 0.948, 0.054,
                           boxstyle="round,pad=0.0,rounding_size=0.012",
                           mutation_aspect=(card_w * fig_w) / (card_height * fig_h),
                           facecolor=BLUE_BG, edgecolor=BLUE_LIGHT, linewidth=1.3)
    ax_card_a.add_patch(hdr_a)
    ax_card_a.text(0.50, 0.951,
                   "A  Changing cosmic composition",
                   color=BLUE_DEEP, fontsize=15.5, fontweight='bold', ha='center', va='center')

    # Right Card Frame (Panel B)
    ax_card_b = fig.add_axes([right_x, card_bottom, card_w, card_height], zorder=0)
    ax_card_b.set_xlim(0, 1)
    ax_card_b.set_ylim(0, 1)
    ax_card_b.axis('off')
    ax_card_b.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0,
                                  facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4))
    hdr_b = FancyBboxPatch((0.026, 0.924), 0.948, 0.054,
                           boxstyle="round,pad=0.0,rounding_size=0.012",
                           mutation_aspect=(card_w * fig_w) / (card_height * fig_h),
                           facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.3)
    ax_card_b.add_patch(hdr_b)
    ax_card_b.text(0.50, 0.951,
                   "B  Suppression of linear growth",
                   color=NAVY, fontsize=15.5, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 3. Cosmological Curves & Transition Scales
    # -------------------------------------------------------------------------
    omega_m0, omega_l0 = 0.3, 0.7
    a_min, a_max = 0.1, 1.0
    a_axis_max = 1.035  # Small right margin so endpoint dots at a = 1 are unclipped

    # Exact transition scale factors:
    # 1. Accelerated expansion begins (\ddot{a} = 0 => \Omega_m = 2\Omega_\Lambda):
    a_acc = (omega_m0 / (2.0 * omega_l0)) ** (1.0 / 3.0)  # ~ 0.5984
    # 2. Matter-\Lambda equality (\Omega_m = \Omega_\Lambda = 0.5):
    a_eq_l = (omega_m0 / omega_l0) ** (1.0 / 3.0)         # ~ 0.7539

    a = np.linspace(a_min, a_max, 600)
    omega_m, omega_l, d_matter, d_lcdm = compute_cosmology_curves(
        a, omega_m0=omega_m0, omega_l0=omega_l0, a_norm=0.1
    )

    # Identical plot width and relative horizontal offset inside each card
    plot_rel_left = 0.082
    plot_w = 0.356
    plot_bottom = 0.152
    plot_h = 0.632

    ax_a = fig.add_axes([left_x + plot_rel_left, plot_bottom, plot_w, plot_h], zorder=2)
    ax_b = fig.add_axes([right_x + plot_rel_left, plot_bottom, plot_w, plot_h], zorder=2)

    # =========================================================================
    # PANEL A: CHANGING COSMIC COMPOSITION (\Omega_m(a) and \Omega_\Lambda(a))
    # =========================================================================
    ax_a.set_facecolor('#ffffff')
    ax_a.set_xlim(a_min, a_axis_max)
    ax_a.set_ylim(0.0, 1.06)

    # Subtle background shading before vs after onset of acceleration (a_acc)
    ax_a.axvspan(a_min, a_acc, facecolor='#f8fafc', alpha=0.65, zorder=0)
    ax_a.axvspan(a_acc, a_max, facecolor='#eff6ff', alpha=0.42, zorder=0)

    # Faint horizontal reference lines at \Omega = 0.5 and \Omega = 1.0
    ax_a.axhline(1.0, color='#cbd5e1', linestyle=':', linewidth=1.4, zorder=1)
    ax_a.axhline(0.5, color='#cbd5e1', linestyle=':', linewidth=1.3, zorder=1)

    # Vertical dashed line at onset of accelerated expansion (a \simeq 0.60)
    ax_a.plot([a_acc, a_acc], [0.0, 1.06],
              color=ACC_COLOR, linestyle='--', linewidth=2.3, alpha=0.90, zorder=3)

    # Plot \Omega_m(a) and \Omega_\Lambda(a)
    ax_a.plot(a, omega_m, color=DARK_SLATE, linewidth=4.3, solid_capstyle='round', zorder=5)
    ax_a.plot(a, omega_l, color=BLUE, linewidth=4.3, solid_capstyle='round', zorder=5)

    # Present-day endpoint dots at a = 1.0
    ax_a.scatter([1.0], [omega_m0], s=85, color=DARK_SLATE, edgecolor='#ffffff', linewidth=1.8, zorder=7)
    ax_a.scatter([1.0], [omega_l0], s=85, color=BLUE, edgecolor='#ffffff', linewidth=1.8, zorder=7)

    # Intersection dot at \Omega_m = \Omega_\Lambda (a \simeq 0.75, \Omega = 0.5)
    ax_a.scatter([a_eq_l], [0.5], s=105, color=NAVY, edgecolor='#ffffff', linewidth=2.0, zorder=8)

    # Direct curve label 1: Matter \Omega_m(a) (placed in open upper-left space below the curve)
    ax_a.text(0.30, 0.73,
              "Matter\n" + r"$\Omega_m(a)$",
              color=DARK_SLATE, fontsize=14.0, fontweight='bold',
              ha='center', va='center', linespacing=1.18,
              bbox=dict(boxstyle='round,pad=0.22,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.2, alpha=0.96),
              zorder=8)
    a_m_arr = 0.34
    om_m_arr = float(np.interp(a_m_arr, a, omega_m))
    ax_a.annotate(
        "",
        xy=(a_m_arr, om_m_arr - 0.015), xytext=(0.315, 0.815),
        arrowprops=dict(arrowstyle="->", color=DARK_SLATE, lw=1.8,
                        connectionstyle="arc3,rad=-0.08", shrinkA=2, shrinkB=3),
        zorder=8
    )

    # Direct curve label 2: Cosmological constant \Omega_\Lambda(a)
    # 3-line compact box in open middle-left space so it stays well clear of both the y-axis and the rising curve
    ax_a.text(0.285, 0.34,
              "Cosmological\nconstant\n" + r"$\Omega_\Lambda(a)$",
              color=BLUE_DEEP, fontsize=13.6, fontweight='bold',
              ha='center', va='center', linespacing=1.16,
              bbox=dict(boxstyle='round,pad=0.22,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor=BLUE_LIGHT, linewidth=1.2, alpha=0.96),
              zorder=8)
    a_l_arr = 0.33
    om_l_arr = float(np.interp(a_l_arr, a, omega_l))
    ax_a.annotate(
        "",
        xy=(a_l_arr, om_l_arr + 0.012), xytext=(0.30, 0.225),
        arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.8,
                        connectionstyle="arc3,rad=0.08", shrinkA=2, shrinkB=3),
        zorder=8
    )

    # Transition 1 annotation: Accelerated expansion begins (a \simeq 0.60)
    # Compact 3-line box in upper-right of Panel A, cleanly to the right of a = 0.60
    ax_a.annotate(
        "",
        xy=(a_acc + 0.007, 0.885), xytext=(0.855, 0.885),
        arrowprops=dict(arrowstyle="->", color=ACC_COLOR, lw=1.9, shrinkA=0, shrinkB=2),
        zorder=7
    )
    ax_a.text(0.855, 0.885,
              "Accelerated\nexpansion begins\n" + r"$a \simeq 0.60$",
              color=ACC_COLOR, fontsize=13.2, fontweight='bold',
              ha='center', va='center', linespacing=1.18,
              bbox=dict(boxstyle='round,pad=0.20,rounding_size=0.14',
                        facecolor=ACC_BG, edgecolor=ACC_BORDER, linewidth=1.2, alpha=1.0),
              zorder=9)

    # Transition 2 annotation: Matter-\Lambda equality (\Omega_m = \Omega_\Lambda at a \simeq 0.75)
    ax_a.text(0.754, 0.145,
              r"$\Omega_m = \Omega_\Lambda$" + "\n" + r"$(a \simeq 0.75)$",
              color=NAVY, fontsize=13.5, fontweight='bold',
              ha='center', va='center', linespacing=1.18,
              bbox=dict(boxstyle='round,pad=0.20,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.2, alpha=0.96),
              zorder=8)
    ax_a.annotate(
        "",
        xy=(a_eq_l, 0.475), xytext=(0.754, 0.232),
        arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.8, shrinkA=2, shrinkB=3),
        zorder=8
    )

    # Subtle present-day value labels at a = 1.0
    ax_a.text(0.985, 0.725, r"$0.7$",
              color=BLUE_DEEP, fontsize=13.5, fontweight='bold', ha='right', va='bottom', zorder=8)
    ax_a.text(0.985, 0.265, r"$0.3$",
              color=DARK_SLATE, fontsize=13.5, fontweight='bold', ha='right', va='top', zorder=8)

    # Panel A Spines, Arrowheads, Ticks & Labels
    ax_a.spines['top'].set_visible(False)
    ax_a.spines['right'].set_visible(False)
    ax_a.spines['left'].set_edgecolor(AXIS_COLOR)
    ax_a.spines['left'].set_linewidth(2.0)
    ax_a.spines['bottom'].set_edgecolor(AXIS_COLOR)
    ax_a.spines['bottom'].set_linewidth(2.0)

    ax_a.plot(1.0, 0.0, ">", transform=ax_a.transAxes, color=AXIS_COLOR,
              markersize=9, clip_on=False, zorder=10)
    ax_a.plot(0.0, 1.0, "^", transform=ax_a.transAxes, color=AXIS_COLOR,
              markersize=9, clip_on=False, zorder=10)

    ax_a.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax_a.set_yticklabels(['0', '0.2', '0.4', '0.6', '0.8', '1'],
                         fontsize=13.5, fontweight='bold', color=DARK_SLATE)
    ax_a.set_xticks([0.1, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax_a.set_xticklabels(['0.1', '0.2', '0.4', '0.6', '0.8', '1'],
                         fontsize=13.5, fontweight='bold', color=DARK_SLATE)
    ax_a.tick_params(axis='both', pad=6, length=6, width=1.6, colors=AXIS_COLOR)

    ax_a.set_ylabel("Density parameter " + r"$\Omega$",
                    fontsize=14.5, fontweight='bold', color=NAVY, labelpad=10)
    ax_a.set_xlabel("Scale factor " + r"$a$",
                    fontsize=14.5, fontweight='bold', color=NAVY, labelpad=10)

    # =========================================================================
    # PANEL B: SUPPRESSION OF LINEAR STRUCTURE GROWTH D(a)
    # =========================================================================
    ax_b.set_facecolor('#ffffff')
    ax_b.set_xlim(a_min, a_axis_max)
    ax_b.set_ylim(0.0, 1.06)

    # Subtle background shading before vs after onset of acceleration (aligned with Panel A)
    ax_b.axvspan(a_min, a_acc, facecolor='#f8fafc', alpha=0.65, zorder=0)
    ax_b.axvspan(a_acc, a_max, facecolor='#eff6ff', alpha=0.42, zorder=0)

    # Vertical dashed line at onset of accelerated expansion (a \simeq 0.60)
    ax_b.plot([a_acc, a_acc], [0.0, 1.06],
              color=ACC_COLOR, linestyle='--', linewidth=2.3, alpha=0.90, zorder=3)

    # Shaded suppression wedge between Matter-only (D \propto a) and \Lambda CDM
    ax_b.fill_between(a, d_lcdm, d_matter,
                      facecolor='#fee2e2', alpha=0.28, zorder=1)

    # Solid \Lambda CDM linear growth factor curve D(a)
    ax_b.plot(a, d_lcdm, color=BLUE, linewidth=4.4, solid_capstyle='round', zorder=5)

    # Dashed reference curve: Matter-only universe D(a) \propto a
    ax_b.plot(a, d_matter, color=MATTER_ONLY_COLOR, linestyle='--', linewidth=3.1,
              dashes=(5, 4), zorder=6)

    # Common normalization marker at a = 0.1 and endpoint markers at a = 1.0
    ax_b.scatter([0.1], [0.1], s=95, color=NAVY, edgecolor='#ffffff', linewidth=2.0, zorder=8)
    ax_b.scatter([1.0], [1.0], s=80, color=MATTER_ONLY_COLOR, edgecolor='#ffffff', linewidth=1.8, zorder=7)
    ax_b.scatter([1.0], [d_lcdm[-1]], s=85, color=BLUE, edgecolor='#ffffff', linewidth=1.8, zorder=7)

    # Top-left badge: "Same early-time normalization"
    ax_b.text(0.33, 0.90,
              "Same early-time\nnormalization",
              color=DARK_SLATE, fontsize=13.5, fontweight='bold',
              ha='center', va='center', linespacing=1.20,
              bbox=dict(boxstyle='round,pad=0.22,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.2, alpha=0.96),
              zorder=8)

    # Direct curve label 1: Matter-only universe: D(a) \propto a
    # Placed at (0.345, 0.665) cleanly left of a = 0.60, with arrow starting outside the right edge of the box
    ax_b.text(0.345, 0.665,
              "Matter-only\nuniverse:\n" + r"$D(a) \propto a$",
              color=MATTER_ONLY_DEEP, fontsize=13.6, fontweight='bold',
              ha='center', va='center', linespacing=1.16,
              bbox=dict(boxstyle='round,pad=0.20,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor='#fecaca', linewidth=1.2, alpha=0.96),
              zorder=8)
    a_mo_arr = 0.72
    ax_b.annotate(
        "",
        xy=(a_mo_arr, a_mo_arr + 0.008), xytext=(0.482, 0.69),
        arrowprops=dict(arrowstyle="->", color=MATTER_ONLY_COLOR, lw=1.8,
                        connectionstyle="arc3,rad=-0.06", shrinkA=2, shrinkB=3),
        zorder=8
    )

    # Direct curve label 2: \Lambda CDM curve (compact 2-line box cleanly inside [0.64, 0.99])
    ax_b.text(0.835, 0.46,
              r"$\Lambda\mathrm{CDM}$" + "\n(slower growth)",
              color=BLUE_DEEP, fontsize=13.8, fontweight='bold',
              ha='center', va='center', linespacing=1.18,
              bbox=dict(boxstyle='round,pad=0.22,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor=BLUE_LIGHT, linewidth=1.2, alpha=0.96),
              zorder=8)
    a_lc_arr = 0.85
    d_lc_arr = float(np.interp(a_lc_arr, a, d_lcdm))
    ax_b.annotate(
        "",
        xy=(a_lc_arr, d_lc_arr - 0.015), xytext=(0.84, 0.545),
        arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.8,
                        connectionstyle="arc3,rad=0.06", shrinkA=2, shrinkB=3),
        zorder=8
    )

    # Transition annotation in Panel B: Accelerated expansion begins (aligned at a \simeq 0.60)
    ax_b.annotate(
        "",
        xy=(a_acc + 0.007, 0.165), xytext=(0.855, 0.165),
        arrowprops=dict(arrowstyle="->", color=ACC_COLOR, lw=1.9, shrinkA=0, shrinkB=2),
        zorder=7
    )
    ax_b.text(0.855, 0.165,
              "Accelerated\nexpansion begins\n" + r"$a \simeq 0.60$",
              color=ACC_COLOR, fontsize=13.2, fontweight='bold',
              ha='center', va='center', linespacing=1.18,
              bbox=dict(boxstyle='round,pad=0.20,rounding_size=0.14',
                        facecolor=ACC_BG, edgecolor=ACC_BORDER, linewidth=1.2, alpha=1.0),
              zorder=9)

    # Panel B Spines, Arrowheads, Ticks & Labels
    ax_b.spines['top'].set_visible(False)
    ax_b.spines['right'].set_visible(False)
    ax_b.spines['left'].set_edgecolor(AXIS_COLOR)
    ax_b.spines['left'].set_linewidth(2.0)
    ax_b.spines['bottom'].set_edgecolor(AXIS_COLOR)
    ax_b.spines['bottom'].set_linewidth(2.0)

    ax_b.plot(1.0, 0.0, ">", transform=ax_b.transAxes, color=AXIS_COLOR,
              markersize=9, clip_on=False, zorder=10)
    ax_b.plot(0.0, 1.0, "^", transform=ax_b.transAxes, color=AXIS_COLOR,
              markersize=9, clip_on=False, zorder=10)

    ax_b.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax_b.set_yticklabels(['0', '0.2', '0.4', '0.6', '0.8', '1'],
                         fontsize=13.5, fontweight='bold', color=DARK_SLATE)
    ax_b.set_xticks([0.1, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax_b.set_xticklabels(['0.1', '0.2', '0.4', '0.6', '0.8', '1'],
                         fontsize=13.5, fontweight='bold', color=DARK_SLATE)
    ax_b.tick_params(axis='both', pad=6, length=6, width=1.6, colors=AXIS_COLOR)

    ax_b.set_ylabel("Linear growth factor " + r"$D(a)$",
                    fontsize=14.5, fontweight='bold', color=NAVY, labelpad=10)
    ax_b.set_xlabel("Scale factor " + r"$a$",
                    fontsize=14.5, fontweight='bold', color=NAVY, labelpad=10)

    # Save figure
    fig.savefig(output_path, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    print(f"[OK] Generated {output_path} ({fig_w * dpi:.0f} x {fig_h * dpi:.0f} px)")


if __name__ == "__main__":
    create_figure()
