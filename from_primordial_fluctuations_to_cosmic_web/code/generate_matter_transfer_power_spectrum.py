#!/usr/bin/env python3
r"""
Generate two-panel conceptual figure:
"From the Primordial Spectrum to the Matter Power Spectrum"

Figure for Section 3.4 ("From the Primordial Spectrum to the Matter Power Spectrum") of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design & Scientific Specifications:
- Canvas: 1890 x 1148 px at 140 DPI (13.5 x 8.20 in), matching the exact
  typography and font size hierarchy of `cosmic_expansion_coordinates.png`,
  `horizon_entry_perturbations.png`, and `cdm_baryon_perturbation_evolution.png`:
  - 18.0 pt bold main title
  - 14.0 pt bold subtitle
  - 15.5 pt bold panel header titles (A — Matter transfer function, B — Linear matter power spectrum)
  - 14.5 pt bold axis titles
  - 14.0-14.2 pt bold primary curve/region labels
  - 13.5-13.8 pt secondary annotations, formulas, and tick labels
- Two horizontally aligned panels of equal width sharing an identical logarithmic
  comoving-wavenumber axis k (so the matter-radiation equality scale k_eq appears
  at the exact same relative horizontal position in both panels):
  - Panel A: Matter transfer function T(k), normalized so T(k) -> 1 at small k.
    Shows a genuinely flat large-scale plateau (T(k) \simeq 1), the bending downward
    around k_eq, progressive small-scale suppression toward larger k, and subtle
    baryonic oscillatory features (BAO).
  - Panel B: Linear matter power spectrum P_m(k, a) at a fixed epoch (logarithmic vertical axis),
    together with a dashed reference proportional to k^{n_s} ("Primordial scale dependence \propto k^{n_s}").
    On large scales (left of k_eq where T(k) \simeq 1), the solid P_m(k, a) curve and
    dashed k^{n_s} reference essentially coincide, then P_m(k, a) bends away around k_eq
    as T^2(k) suppresses small-scale power, with subtle BAO oscillations.
"""

from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "matter_transfer_function_power_spectrum.png"


def compute_transfer_and_power(u, u_eq=-0.42, n_s=0.965):
    r"""
    Compute physically shaped schematic matter transfer function T(k) and
    linear matter power spectrum P_m(k, a) on a logarithmic wavenumber variable
    u = log10(k / k_0) spanning [-2.0, 2.0]:
    - T_smooth(u): stays genuinely flat at 1.00 across the large-scale regime
      (u in [-2.0, -0.95]), begins bending downward around u_eq = -0.42, and
      declines progressively toward larger k.
    - Because T_smooth(u) \simeq 1.00 for u < -0.9, log10 T(k) \simeq 0 there,
      so the solid P_m(k, a) curve and the dashed primordial reference (\propto k^{n_s})
      essentially overlap on the large-scale side before bending apart near k_eq.
    - Subtle damped baryonic oscillations superimposed in the intermediate/small-scale
      regime (u in [0.05, 1.38]) so they appear as a secondary modulation rather
      than dominating the broad plateau -> turnover -> suppression shape.
    """
    u = np.asarray(u, dtype=float)
    # Scaled wavenumber relative to the equality turnover scale
    q = 10.0 ** (0.88 * (u - u_eq))

    # Smooth plateau-to-suppression transfer envelope with a sharper knee (exponent 2.35)
    # so that T_smooth > 0.99 for u <= -1.0 (giving true overlap with k^{n_s} on the left)
    # while transitioning smoothly around u_eq and falling off at high k:
    T_smooth = (1.0 + (0.72 * q) ** 2.35) ** (-0.54)
    T_smooth = T_smooth / T_smooth[0]

    # Subtle baryonic oscillatory modulation concentrated in u in [0.05, 1.38],
    # damped at high k by Silk diffusion
    u_osc_center = 0.60
    window = (
        np.exp(-((u - u_osc_center) / 0.46) ** 2)
        * (1.0 / (1.0 + np.exp(-(u - 0.05) / 0.07)))
    )
    # 3.5 gentle cycles across the intermediate/small-scale regime
    phase = 2.0 * np.pi * (u - 0.08) / 0.36
    # Reduced amplitude so BAO is a clean secondary modulation
    T = T_smooth + 0.015 * window * np.sin(phase)

    # Panel B: Logarithmic vertical coordinate for P_m(k, a) in [0, 10.5]
    # 1. Primordial scale dependence reference: \propto k^{n_s} (straight line on log-log plot)
    slope_prim = 1.92 * n_s
    y_prim = 2.65 + slope_prim * (u - (-2.0))

    # 2. Linear matter power spectrum: P_m(k, a) \propto k^{n_s} T^2(k) at fixed a
    # In log space: log P_m = log P_prim + 2 * log T(k)
    suppression_log = 3.55 * np.log10(T_smooth)
    bao_log_wiggle = 0.095 * window * np.sin(phase)
    y_pm = y_prim + suppression_log + bao_log_wiggle

    return T, T_smooth, y_prim, y_pm


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure mathtext and typography (matching cosmic_expansion_coordinates.png & horizon_entry_perturbations.png)
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

    # Curated Editorial Palette (matching earlier figures in the article)
    NAVY = '#0f172a'          # Hero headings, axis titles
    DARK_SLATE = '#1e293b'    # Primary text
    SLATE = '#475569'         # Secondary text
    AXIS_COLOR = '#334155'    # Axis spines and arrowheads
    BORDER_COLOR = '#cbd5e1'  # Card borders
    CARD_BG = '#f8fafc'       # Header background

    # Panel A & B curve colors
    BLUE_DEEP = '#1e3a8a'
    BLUE_DARK = '#1d4ed8'
    BLUE = '#2563eb'
    BLUE_LIGHT = '#bfdbfe'
    BLUE_BG = '#eff6ff'

    PM_COLOR = '#0f172a'      # Solid dark navy/charcoal for P_m(k, a)
    PRIM_COLOR = '#dc2626'    # Crimson dashed reference for primordial \propto k^{n_s}
    PRIM_DEEP = '#991b1b'
    EQ_COLOR = '#92400e'      # Warm amber-brown for matter-radiation equality scale k_eq
    EQ_BG = '#fffbeb'
    EQ_BORDER = '#fde68a'

    # -------------------------------------------------------------------------
    # 1. Top Header Banner (y: 0.896 - 0.980)
    # -------------------------------------------------------------------------
    ax_head = fig.add_axes([0.025, 0.896, 0.950, 0.084])
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)
    ax_head.axis('off')

    title_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.009",
                               mutation_aspect=(0.950 * fig_w) / (0.084 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_head.add_patch(title_box)
    ax_head.text(0.50, 0.65, "FROM THE PRIMORDIAL SPECTRUM TO THE MATTER POWER SPECTRUM",
                 color=NAVY, fontsize=18.0, fontweight='bold', ha='center', va='center')
    ax_head.text(0.50, 0.27,
                 "Scale-dependent evolution of linear matter perturbations",
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
    # Compact panel header badge (height reduced from 0.074 to 0.054 to remove excess vertical whitespace)
    hdr_a = FancyBboxPatch((0.026, 0.924), 0.948, 0.054,
                           boxstyle="round,pad=0.0,rounding_size=0.012",
                           mutation_aspect=(card_w * fig_w) / (card_height * fig_h),
                           facecolor=BLUE_BG, edgecolor=BLUE_LIGHT, linewidth=1.3)
    ax_card_a.add_patch(hdr_a)
    ax_card_a.text(0.50, 0.951,
                   "A — Matter transfer function " + r"$T(k)$",
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
                   "B — Linear matter power spectrum " + r"$P_m(k, a)$",
                   color=NAVY, fontsize=15.5, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 3. Common Wavenumber Grid and Plotting Axes
    # -------------------------------------------------------------------------
    u_min, u_max = -2.0, 2.0
    u_eq = -0.42
    u = np.linspace(u_min, u_max, 700)
    T, T_smooth, y_prim, y_pm = compute_transfer_and_power(u, u_eq=u_eq)

    # Identical plot width and relative horizontal offset inside each card so
    # u_eq appears at the exact same relative position in Panel A and Panel B
    plot_rel_left = 0.078
    plot_w = 0.364
    plot_bottom = 0.168
    plot_h = 0.618

    ax_a = fig.add_axes([left_x + plot_rel_left, plot_bottom, plot_w, plot_h], zorder=2)
    ax_b = fig.add_axes([right_x + plot_rel_left, plot_bottom, plot_w, plot_h], zorder=2)

    # =========================================================================
    # PANEL A: MATTER TRANSFER FUNCTION T(k)
    # =========================================================================
    ax_a.set_facecolor('#ffffff')
    ax_a.set_xlim(u_min, u_max)
    ax_a.set_ylim(0.0, 1.15)

    # Subtle background shading left vs right of k_eq
    ax_a.axvspan(u_min, u_eq, facecolor='#f8fafc', alpha=0.65, zorder=0)
    ax_a.axvspan(u_eq, u_max, facecolor='#eff6ff', alpha=0.45, zorder=0)

    # Faint horizontal reference line at T(k) = 1
    ax_a.axhline(1.0, color='#94a3b8', linestyle=':', linewidth=1.6, zorder=1)

    # Vertical dashed line at matter-radiation equality scale k_eq
    ax_a.plot([u_eq, u_eq], [0.0, 1.15],
              color=EQ_COLOR, linestyle='--', linewidth=2.2, alpha=0.88, zorder=2)

    # Main transfer function curve T(k)
    ax_a.plot(u, T, color=BLUE, linewidth=4.2, solid_capstyle='round', zorder=5)

    # Annotation 1: Vertical 2-line label directly beside the dashed k_eq line (no box)
    # Placed in the clean lower half alongside the dashed line (moved a few pixels farther left
    # so it does not feel squeezed against the dashed line)
    ax_a.text(u_eq - 0.14, 0.36,
              "Matter–radiation\nequality scale " + r"$k_{\mathrm{eq}}$",
              color=EQ_COLOR, fontsize=12.8, fontweight='bold',
              ha='right', va='center', linespacing=1.15, rotation=90, zorder=8)

    # Annotation 2: Left plateau "Large scales: T(k) \simeq 1"
    ax_a.text(-1.28, 0.82,
              "Large scales:\n" + r"$T(k) \simeq 1$",
              color=BLUE_DEEP, fontsize=13.8, fontweight='bold',
              ha='center', va='center', linespacing=1.22,
              bbox=dict(boxstyle='round,pad=0.22,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor=BLUE_LIGHT, linewidth=1.2, alpha=0.96),
              zorder=8)

    # Annotation 3: Right side "Small-scale suppression"
    ax_a.text(1.22, 0.62,
              "Small-scale\nsuppression",
              color=DARK_SLATE, fontsize=13.6, fontweight='bold',
              ha='center', va='center', linespacing=1.20,
              bbox=dict(boxstyle='round,pad=0.22,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.2, alpha=0.96),
              zorder=8)
    # Arrow pointing straight down-right to declining high-k curve
    u_supp_target = 1.48
    T_supp_target = float(np.interp(u_supp_target, u, T))
    ax_a.annotate(
        "",
        xy=(u_supp_target, T_supp_target + 0.025), xytext=(1.32, 0.52),
        arrowprops=dict(arrowstyle="->", color=DARK_SLATE, lw=1.8,
                        connectionstyle="arc3,rad=-0.10", shrinkA=2, shrinkB=3),
        zorder=8
    )

    # Annotation 4: Discreet "Baryonic features (BAO)" marker in open space right of the curve,
    # well above the Small-scale suppression arrow or cleanly below the curve on the left
    ax_a.text(0.58, 0.34,
              "Baryonic\nfeatures (BAO)",
              color=BLUE_DEEP, fontsize=13.5, fontweight='bold',
              ha='center', va='center', linespacing=1.18,
              bbox=dict(boxstyle='round,pad=0.20,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor=BLUE_LIGHT, linewidth=1.1, alpha=0.96),
              zorder=8)
    u_wiggle_a = 0.44
    T_wiggle_a = float(np.interp(u_wiggle_a, u, T))
    ax_a.annotate(
        "",
        xy=(u_wiggle_a + 0.01, T_wiggle_a + 0.015), xytext=(0.52, 0.25),
        arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.8,
                        connectionstyle="arc3,rad=-0.08", shrinkA=2, shrinkB=3),
        zorder=8
    )

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

    ax_a.set_yticks([0.0, 0.5, 1.0])
    ax_a.set_yticklabels(['0', '0.5', '1'], fontsize=13.5, fontweight='bold', color=DARK_SLATE)
    ax_a.set_xticks([u_eq])
    ax_a.set_xticklabels([r"$k_{\mathrm{eq}}$"], fontsize=14.0, fontweight='bold', color=EQ_COLOR)
    ax_a.tick_params(axis='both', pad=6, length=6, width=1.6, colors=AXIS_COLOR)

    ax_a.set_ylabel("Transfer function " + r"$T(k)$",
                    fontsize=14.5, fontweight='bold', color=NAVY, labelpad=10)

    ax_a.text(0.50, -0.112,
              "Comoving wavenumber " + r"$k$" + " (logarithmic axis)",
              transform=ax_a.transAxes, fontsize=14.2, fontweight='bold', color=NAVY,
              ha='center', va='top')
    ax_a.text(0.00, -0.180,
              r"$\longleftarrow$" + " larger scales",
              transform=ax_a.transAxes, fontsize=13.5, color=SLATE,
              ha='left', va='top')
    ax_a.text(1.00, -0.180,
              "smaller scales " + r"$\longrightarrow$",
              transform=ax_a.transAxes, fontsize=13.5, color=SLATE,
              ha='right', va='top')

    # =========================================================================
    # PANEL B: LINEAR MATTER POWER SPECTRUM P_m(k, a) AT A FIXED EPOCH
    # =========================================================================
    ax_b.set_facecolor('#ffffff')
    ax_b.set_xlim(u_min, u_max)
    ax_b.set_ylim(0.0, 10.5)

    # Subtle background shading left vs right of k_eq (matching Panel A)
    ax_b.axvspan(u_min, u_eq, facecolor='#f8fafc', alpha=0.65, zorder=0)
    ax_b.axvspan(u_eq, u_max, facecolor='#eff6ff', alpha=0.45, zorder=0)

    # Vertical dashed line at matter-radiation equality scale k_eq (aligned with Panel A)
    ax_b.plot([u_eq, u_eq], [0.0, 10.5],
              color=EQ_COLOR, linestyle='--', linewidth=2.2, alpha=0.88, zorder=2)

    # Shaded suppression wedge between dashed k^{n_s} reference and actual P_m(k, a)
    mask_right = u >= -0.95
    ax_b.fill_between(u[mask_right], y_pm[mask_right], y_prim[mask_right],
                      facecolor='#fee2e2', alpha=0.25, zorder=1)

    # Solid linear matter power spectrum curve P_m(k, a)
    ax_b.plot(u, y_pm, color=PM_COLOR, linewidth=4.4, solid_capstyle='round', zorder=5)

    # Dashed reference curve: Primordial scale dependence \propto k^{n_s}
    # Drawn at zorder=6 so that on large scales (left of k_eq), where y_pm and y_prim
    # essentially coincide, the alternating red dashes and dark solid segments are both
    # clearly visible right on top of each other before the black curve bends away!
    ax_b.plot(u, y_prim, color=PRIM_COLOR, linestyle='--', linewidth=3.0,
              dashes=(5, 4), zorder=6)

    # Find turnover peak near k_eq (slightly distinct from k_eq) and restore dot marker
    idx_peak = int(np.argmax(y_pm))
    u_peak = float(u[idx_peak])
    y_peak = float(y_pm[idx_peak])
    ax_b.scatter([u_peak], [y_peak], s=115, color=PM_COLOR,
                 edgecolor='#ffffff', linewidth=2.2, zorder=8)

    # Note at top-left (left of k_eq): "Shown at a fixed epoch"
    ax_b.text(-1.38, 9.65,
              "Shown at a\nfixed epoch",
              color=DARK_SLATE, fontsize=13.5, fontweight='bold',
              ha='center', va='center', linespacing=1.20,
              bbox=dict(boxstyle='round,pad=0.20,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.1, alpha=0.96),
              zorder=8)

    # Identical vertical 2-line label directly beside the dashed k_eq line in Panel B (no box)
    # Lowered to y = 2.25 so the top of "Matter-radiation" sits well below the rising curve!
    ax_b.text(u_eq - 0.14, 2.25,
              "Matter–radiation\nequality scale " + r"$k_{\mathrm{eq}}$",
              color=EQ_COLOR, fontsize=12.8, fontweight='bold',
              ha='right', va='center', linespacing=1.15, rotation=90, zorder=8)

    # Label for dashed reference line (cleanly to the right of k_eq, above the dashed line)
    ax_b.text(0.68, 9.25,
              "Primordial scale\ndependence " + r"$\propto k^{n_s}$",
              color=PRIM_DEEP, fontsize=13.5, fontweight='bold',
              ha='center', va='center', linespacing=1.20,
              bbox=dict(boxstyle='round,pad=0.20,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor='#fecaca', linewidth=1.2, alpha=0.96),
              zorder=8)
    u_prim_target = 0.85
    y_prim_target = float(np.interp(u_prim_target, u, y_prim))
    ax_b.annotate(
        "",
        xy=(u_prim_target, y_prim_target + 0.08), xytext=(0.72, 8.35),
        arrowprops=dict(arrowstyle="->", color=PRIM_COLOR, lw=1.8,
                        connectionstyle="arc3,rad=0.10", shrinkA=2, shrinkB=3),
        zorder=8
    )

    # Annotation near maximum: "Turnover" placed just above and slightly left of the peak,
    # with the arrow tip pointing directly to the restored turnover dot!
    ax_b.text(-1.12, 6.75,
              "Turnover",
              color=EQ_COLOR, fontsize=13.8, fontweight='bold',
              ha='center', va='center',
              bbox=dict(boxstyle='round,pad=0.20,rounding_size=0.14',
                        facecolor=EQ_BG, edgecolor=EQ_BORDER, linewidth=1.1, alpha=0.96),
              zorder=8)
    ax_b.annotate(
        "",
        xy=(u_peak - 0.01, y_peak + 0.04), xytext=(-0.78, 6.45),
        arrowprops=dict(arrowstyle="->", color=EQ_COLOR, lw=1.8,
                        connectionstyle="arc3,rad=-0.12", shrinkA=2, shrinkB=2),
        zorder=8
    )

    # Annotation at high k: "Reduced small-scale power" shifted left so it stays strictly
    # inside the right boundary of the shaded plot region while clearing the black curve
    ax_b.text(1.06, 5.75,
              "Reduced\nsmall-scale power",
              color=DARK_SLATE, fontsize=13.4, fontweight='bold',
              ha='center', va='center', linespacing=1.20,
              bbox=dict(boxstyle='round,pad=0.20,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.2, alpha=0.96),
              zorder=8)
    # Downward arrow from below the "Reduced small-scale power" box toward the declining P_m curve
    u_red_arrow = 1.50
    y_pm_arr = float(np.interp(u_red_arrow, u, y_pm))
    ax_b.annotate(
        "",
        xy=(u_red_arrow, y_pm_arr + 0.16), xytext=(1.26, 4.92),
        arrowprops=dict(arrowstyle="->", color=DARK_SLATE, lw=1.9,
                        connectionstyle="arc3,rad=-0.10", shrinkA=2, shrinkB=3),
        zorder=8
    )

    # Discreet "BAO" annotation in lower space pointing directly to the first clearly visible wiggle
    ax_b.text(0.05, 1.85,
              "BAO",
              color=BLUE_DEEP, fontsize=13.8, fontweight='bold',
              ha='center', va='center',
              bbox=dict(boxstyle='round,pad=0.20,rounding_size=0.14',
                        facecolor='#ffffff', edgecolor=BLUE_LIGHT, linewidth=1.2, alpha=0.96),
              zorder=8)
    u_bao_target = 0.44
    y_bao_target = float(np.interp(u_bao_target, u, y_pm))
    ax_b.annotate(
        "",
        xy=(u_bao_target - 0.03, y_bao_target - 0.14), xytext=(0.14, 2.38),
        arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.8,
                        connectionstyle="arc3,rad=-0.10", shrinkA=2, shrinkB=3),
        zorder=8
    )

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

    ax_b.set_yticks([])
    ax_b.set_xticks([u_eq])
    ax_b.set_xticklabels([r"$k_{\mathrm{eq}}$"], fontsize=14.0, fontweight='bold', color=EQ_COLOR)
    ax_b.tick_params(axis='x', pad=6, length=6, width=1.6, colors=AXIS_COLOR)

    ax_b.set_ylabel("Matter power spectrum " + r"$P_m(k, a)$" + "\n(logarithmic axis, schematic)",
                    fontsize=14.2, fontweight='bold', color=NAVY, labelpad=12)

    ax_b.text(0.50, -0.112,
              "Comoving wavenumber " + r"$k$" + " (logarithmic axis)",
              transform=ax_b.transAxes, fontsize=14.2, fontweight='bold', color=NAVY,
              ha='center', va='top')
    ax_b.text(0.00, -0.180,
              r"$\longleftarrow$" + " larger scales",
              transform=ax_b.transAxes, fontsize=13.5, color=SLATE,
              ha='left', va='top')
    ax_b.text(1.00, -0.180,
              "smaller scales " + r"$\longrightarrow$",
              transform=ax_b.transAxes, fontsize=13.5, color=SLATE,
              ha='right', va='top')

    # Save figure
    fig.savefig(output_path, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    print(f"[OK] Generated {output_path} ({fig_w * dpi:.0f} x {fig_h * dpi:.0f} px)")


if __name__ == "__main__":
    create_figure()
