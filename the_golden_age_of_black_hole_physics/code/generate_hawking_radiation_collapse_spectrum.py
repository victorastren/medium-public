#!/usr/bin/env python3
r"""
Generate two-panel static scientific illustration:
"From Gravitational Collapse to Hawking Radiation"

Figure for Section "Hawking Radiation (1974)" -> "Quantum Fields and Particle Creation" of:
"The Golden Age of Black Hole Physics (1963–1974)"

Design & Scientific Specifications:
- Format: Static, two-panel scientific illustration (light scientific style)
- Resolution: 1800 x 900 px at 140 DPI (12.857 x 6.429 in, 2:1 aspect ratio)
- Panel proportions: Equal 50/50 split (left_w = right_w = 0.472)
- Typography & font size hierarchy matching existing figures:
  - 17.8 pt bold main title (dark navy #0f172a)
  - 13.2 pt bold subtitle (slate #475569)
  - 14.8 pt bold panel headers:
    - "A · Gravitational collapse and redshift"
    - "B · Thermal radiation and greybody factors"
  - 11.5 pt bold panel subheaders
  - 13.8–14.0 pt bold axis titles
  - 12.2–13.0 pt bold tick labels and callouts
- Panel A (Left): Consistent Finkelstein-style collapse spacetime diagram
  (horizon-penetrating time coordinate vertically, radial distance r horizontally):
  - Regular stellar center (r = 0) before collapse completes (0 <= t < t_sing)
  - Collapsing star interior and surface trajectory R(t) crossing r = r_s at finite
    horizon-penetrating time and reaching r = 0 at t = t_sing
  - Event horizon originates at r = 0 inside the collapsing star (not pre-existing!),
    grows outward to meet the stellar surface at r = r_s, and remains at r = r_s
    thereafter
  - Future spacelike/Finkelstein curvature singularity at r = 0 forms ONLY once the
    stellar surface reaches r = 0 (for t >= t_sing), never extending into the regular
    early star interior
  - Three outgoing null rays outside the horizon: rays reaching the distant observer
    at progressively later times trace backward ever closer to the forming event
    horizon, undergoing strongly increasing gravitational redshift
- Panel B (Right): Schematic radiation spectra:
  - Header: "B · Thermal radiation and greybody factors"
  - Subheader: "Schematic spectra before and after exterior scattering"
  - Explicit "Schematic spectra" badge inside the plot
  - Dashed blue curve: "Ideal thermal spectrum (blackbody at temperature T_H)"
  - Solid orange curve: "Predicted spectrum at infinity (modified by greybody factors)"
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
import numpy as np
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_IMAGES = SCRIPT_DIR.parent / "images" / "hawking_radiation_collapse_spectrum.png"


def create_figure(output_path=None):
    if output_path is None:
        output_path = OUT_IMAGES
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 13.5,
    })

    dpi = 140
    fig_w, fig_h = 1800.0 / dpi, 900.0 / dpi
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Unified Editorial Palette
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#475569'
    AXIS_COLOR = '#334155'
    BORDER_COLOR = '#cbd5e1'
    PANEL_BG = '#f8fafc'
    BG_WHITE = '#ffffff'

    BLUE_MAIN = '#1d4ed8'
    BLUE_DARK = '#1e3a8a'
    BLUE_LIGHT = '#93c5fd'
    BLUE_BG = '#eff6ff'
    BLUE_BORDER = '#bfdbfe'

    TEAL_MAIN = '#0d9488'
    TEAL_DARK = '#0f766e'
    TEAL_BG = '#f0fdfa'
    TEAL_BORDER = '#5eead4'

    ORANGE_MAIN = '#d97706'
    ORANGE_DARK = '#b45309'
    ORANGE_BG = '#fffbeb'
    ORANGE_BORDER = '#fcd34d'

    RED_LATE = '#c2410c'

    # =========================================================================
    # 1. TOP HEADER BANNER
    # =========================================================================
    title_box = FancyBboxPatch(
        (0.020, 0.876), 0.960, 0.104,
        boxstyle="round,pad=0.002,rounding_size=0.008",
        facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.4,
    )
    ax.add_patch(title_box)
    ax.text(
        0.50, 0.948, "FROM GRAVITATIONAL COLLAPSE TO HAWKING RADIATION",
        color=NAVY, fontsize=17.8, fontweight='bold', ha='center', va='center',
    )
    ax.text(
        0.50, 0.898,
        "Horizon redshift of outgoing field modes and the predicted greybody-modified thermal spectrum",
        color=SLATE, fontsize=13.2, fontweight='bold', ha='center', va='center',
    )

    # =========================================================================
    # 2. TWO EQUAL PANEL CARDS (50/50 split matching Penrose & Bekenstein)
    # =========================================================================
    p_y = 0.020
    p_h = 0.835
    p_w = 0.472
    left_x = 0.020
    right_x = 0.508

    pad_x = 0.009
    pad_y = 0.012
    hdr_h = 0.088
    vp_h = p_h - hdr_h - 0.032

    for px, p_title, p_sub, is_right in [
        (left_x, "A  ·  Gravitational collapse and redshift",
         "Schematic time–radius diagram of a collapsing star", False),
        (right_x, "B  ·  Thermal radiation and greybody factors",
         "Ideal thermal spectrum and greybody-modified radiation", True),
    ]:
        card = FancyBboxPatch(
            (px, p_y), p_w, p_h,
            boxstyle="round,pad=0.002,rounding_size=0.008",
            facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=1,
        )
        ax.add_patch(card)

        viewport = FancyBboxPatch(
            (px + pad_x, p_y + pad_y), p_w - 2 * pad_x, vp_h,
            boxstyle="round,pad=0.002,rounding_size=0.006",
            facecolor=BG_WHITE, edgecolor='#e2e8f0', linewidth=1.0, zorder=1.5,
        )
        ax.add_patch(viewport)

        hdr_y = p_y + p_h - hdr_h - 0.012
        hdr_box = FancyBboxPatch(
            (px + pad_x, hdr_y), p_w - 2 * pad_x, hdr_h,
            boxstyle="round,pad=0.002,rounding_size=0.006",
            facecolor=BG_WHITE if not is_right else ORANGE_BG,
            edgecolor=BORDER_COLOR if not is_right else ORANGE_BORDER,
            linewidth=1.2, zorder=2,
        )
        ax.add_patch(hdr_box)

        ax.text(
            px + 0.5 * p_w, hdr_y + 0.058, p_title,
            color=NAVY if not is_right else ORANGE_DARK,
            fontsize=14.8, fontweight='bold', ha='center', va='center', zorder=3,
        )
        ax.text(
            px + 0.5 * p_w, hdr_y + 0.022, p_sub,
            color=SLATE if not is_right else DARK_SLATE,
            fontsize=11.5, fontweight='bold', ha='center', va='center', zorder=3,
        )

    # =========================================================================
    # 3. PANEL A — CONSISTENT COLLAPSE SPACETIME DIAGRAM
    # =========================================================================
    ax_a = fig.add_axes([left_x + 0.058, p_y + 0.118, p_w - 0.082, vp_h - 0.135], zorder=3)
    ax_a.set_facecolor(BG_WHITE)

    r_max = 10.0
    t_max = 10.0
    ax_a.set_xlim(0.0, r_max)
    ax_a.set_ylim(0.0, t_max)

    # Clean axes styling with arrowheads
    ax_a.spines['top'].set_visible(False)
    ax_a.spines['right'].set_visible(False)
    ax_a.spines['left'].set_edgecolor(AXIS_COLOR)
    ax_a.spines['left'].set_linewidth(1.8)
    ax_a.spines['bottom'].set_edgecolor(AXIS_COLOR)
    ax_a.spines['bottom'].set_linewidth(1.8)
    ax_a.tick_params(axis='x', pad=6, length=5, width=1.5, colors=AXIS_COLOR)
    ax_a.tick_params(axis='y', pad=6, length=5, width=1.5, colors=AXIS_COLOR)

    ax_a.plot(1.0, 0.0, ">", transform=ax_a.transAxes, color=AXIS_COLOR,
              markersize=8.5, clip_on=False, zorder=10)
    ax_a.plot(0.0, 1.0, "^", transform=ax_a.transAxes, color=AXIS_COLOR,
              markersize=8.5, clip_on=False, zorder=10)

    r_h = 2.45  # Event horizon radius r_s in schematic units
    ax_a.set_xticks([0.0, r_h])
    ax_a.set_xticklabels([r"$0$", r"$r_s$"], fontsize=13.0, fontweight='bold')
    ax_a.get_xticklabels()[1].set_color(TEAL_DARK)

    ax_a.set_yticks([])
    ax_a.set_xlabel(r"Radial distance,  $r$", fontsize=13.8, fontweight='bold', color=NAVY, labelpad=8)
    ax_a.set_ylabel(r"Time,  $t$", fontsize=13.8, fontweight='bold', color=NAVY, labelpad=10)

    # -------------------------------------------------------------------------
    # A.1 Collapsing stellar surface R(t) and interior shading
    # -------------------------------------------------------------------------
    # Schematic time-radius diagram of spherical gravitational collapse:
    # - For 0 <= t < t_sing (t_sing = 5.45), the center r = 0 is regular inside the star.
    # - The stellar surface starts at R_0 = 4.52 at t = 0, crosses r = r_s = 2.45 at
    #   t_cross = 3.35, and reaches r = 0 at t_sing = 5.45 where the future singular
    #   boundary begins.
    t_cross = 3.35
    t_sing = 5.45
    R_0 = 4.52
    t_star = np.linspace(0.0, t_sing, 400)
    p_exp = np.log(1.0 - r_h / R_0) / np.log(t_cross / t_sing)
    r_star = R_0 * (1.0 - (t_star / t_sing) ** p_exp)

    star_poly_pts = np.vstack([
        np.column_stack([r_star, t_star]),
        [[0.0, t_sing], [0.0, 0.0]],
    ])
    ax_a.add_patch(Polygon(star_poly_pts, closed=True, facecolor='#cbd5e1',
                           edgecolor='none', alpha=0.65, zorder=1.5))

    # -------------------------------------------------------------------------
    # A.2 Event Horizon Originating Inside the Collapsing Star & BH Interior
    # -------------------------------------------------------------------------
    # Crucially, there is NO horizon for t < t_form = 1.35!
    # The event horizon originates at the regular center r = 0 at t = t_form = 1.35,
    # expands outward through the collapsing star along an outgoing null ray to meet
    # the stellar surface at (r_h, t_cross = 3.35), and remains at r = r_h for t >= 3.35.
    t_form = 1.35
    t_eh_grow = np.linspace(t_form, t_cross, 120)
    r_eh_grow = r_h * ((t_eh_grow - t_form) / (t_cross - t_form)) ** 0.90
    t_eh_stat = np.linspace(t_cross, 9.45, 100)
    r_eh_stat = np.full_like(t_eh_stat, r_h)

    t_eh_full = np.concatenate([t_eh_grow, t_eh_stat])
    r_eh_full = np.concatenate([r_eh_grow, r_eh_stat])

    # Subtle light-teal wash inside the event horizon
    bh_poly_pts = np.vstack([
        np.column_stack([r_eh_full, t_eh_full]),
        [[0.0, 9.45], [0.0, t_form]],
    ])
    ax_a.add_patch(Polygon(bh_poly_pts, closed=True, facecolor='#ccfbf1',
                           edgecolor='none', alpha=0.34, zorder=1.8))

    # Subtle vertical dotted reference line from r_s tick up to horizon-crossing point (r_h, t_cross)
    ax_a.plot([r_h, r_h], [0.0, t_cross], color='#cbd5e1', linestyle=':', linewidth=1.2, zorder=2.0)

    # Plot collapsing stellar surface trajectory R(t)
    ax_a.plot(r_star, t_star, color='#334155', linewidth=3.0, linestyle='-', zorder=4)

    # Mark the point where the forming horizon meets the stellar surface at (r_h, t_cross)
    ax_a.scatter([r_h], [t_cross], s=58, color=TEAL_DARK, edgecolors=BG_WHITE, linewidths=1.5, zorder=6.5)

    # Plot Event Horizon (distinctive teal-navy dashed curve originating at r=0, t=t_form)
    ax_a.plot(r_eh_full, t_eh_full, color=TEAL_DARK, linewidth=2.9, linestyle='--', zorder=5)

    # Mark horizon formation at center (0, t_form)
    ax_a.scatter([0.0], [t_form], s=48, color=TEAL_DARK, edgecolors=BG_WHITE, linewidths=1.3, zorder=6.5)

    # Label inside collapsing star (lower left)
    ax_a.text(1.22, 1.05, "Collapsing\nstar",
              color=DARK_SLATE, fontsize=11.8, fontweight='bold',
              ha='center', va='center', linespacing=1.16, zorder=6)

    # Label for collapsing stellar surface (placed in open exterior with long clear arrow shaft)
    ax_a.annotate(
        "Stellar surface",
        xy=(3.54, 1.95), xytext=(6.25, 2.12),
        arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.24",
                        color=DARK_SLATE, lw=1.9, shrinkA=2, shrinkB=3),
        fontsize=11.4, fontweight='bold', color=DARK_SLATE, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.20', facecolor=PANEL_BG, edgecolor=BORDER_COLOR, lw=1.1),
        zorder=8,
    )

    # Small two-line label explicitly noting the Schwarzschild (nonrotating) assumption in Panel A,
    # fitting cleanly between the stellar surface (R_0 = 4.52) and distant observer (r_obs = 8.65)
    ax_a.text(
        6.58, 0.72,
        "Nonrotating black hole\n(Schwarzschild)",
        color=SLATE, fontsize=9.8, fontweight='bold',
        ha='center', va='center', linespacing=1.15,
        bbox=dict(boxstyle='round,pad=0.18', facecolor=PANEL_BG, edgecolor=BORDER_COLOR, lw=1.1),
        zorder=8,
    )

    # Label for Event horizon moved slightly up and right so the green arrow is clearly visible
    # while maintaining clear separation from the blue box above and red ray below
    ax_a.annotate(
        "Event horizon\n" + r"($r = r_s$)",
        xy=(r_h, 7.02), xytext=(4.12, 7.02),
        arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.24",
                        color=TEAL_DARK, lw=1.9, shrinkA=2, shrinkB=3),
        fontsize=11.3, fontweight='bold', color=TEAL_DARK, ha='center', va='center',
        linespacing=1.16,
        bbox=dict(boxstyle='round,pad=0.20', facecolor=TEAL_BG, edgecolor=TEAL_BORDER, lw=1.2),
        zorder=8,
    )

    # -------------------------------------------------------------------------
    # A.4 Distant Observer Worldline & Outgoing Light Rays (Peeling / Redshift)
    # -------------------------------------------------------------------------
    r_obs = 8.65
    ax_a.plot([r_obs, r_obs], [0.25, 9.18], color=SLATE, linestyle='-.', linewidth=2.0, zorder=3)
    ax_a.text(r_obs, 9.52, "Distant observer",
              color=DARK_SLATE, fontsize=11.8, fontweight='bold',
              ha='center', va='bottom', zorder=7)

    # Three outgoing light rays outside the horizon:
    # Traced backward from the distant observer, later-arriving rays pass progressively
    # closer to the forming event horizon (peeling behavior near r = r_s).
    ray_specs = [
        # (r_start, t_start, scale_log, lin_slope, color)
        (2.92, 1.95, 0.34, 0.32, BLUE_MAIN),
        (2.60, 2.62, 0.44, 0.29, ORANGE_MAIN),
        (2.475, 3.08, 0.51, 0.26, RED_LATE),
    ]

    for r_0, t_0, scale_log, lin_slope, col in ray_specs:
        r_pts = np.linspace(r_0, r_obs, 300)
        t_pts = t_0 + lin_slope * (r_pts - r_0) + scale_log * np.log((r_pts - r_h) / (r_0 - r_h))
        ax_a.plot(r_pts, t_pts, color=col, linewidth=2.6, zorder=6)

        # Directional arrow along each ray around r = 5.45
        i_mid = np.argmin(np.abs(r_pts - 5.45))
        ax_a.annotate(
            '',
            xy=(r_pts[i_mid + 8], t_pts[i_mid + 8]),
            xytext=(r_pts[i_mid], t_pts[i_mid]),
            arrowprops=dict(arrowstyle='-|>,head_length=0.45,head_width=0.24',
                            color=col, lw=2.2),
            zorder=7,
        )

        # Arrival dot on distant observer worldline
        t_arr = t_pts[-1]
        ax_a.scatter([r_obs], [t_arr], s=54, color=col, edgecolors=BG_WHITE, linewidths=1.3, zorder=8)

    # Callout highlighting the outgoing rays & exponentially growing redshift (left-aligned content,
    # positioned with clear margin from both r = r_s on the left and Distant observer on the right)
    ax_a.text(
        2.82, 8.65,
        "Outgoing field modes\nLater arrival  " + r"$\Rightarrow$" + "  closer to horizon\n"
        + r"$\Rightarrow$" + "  increasing redshift",
        color=BLUE_DARK, fontsize=10.5, fontweight='bold',
        ha='left', va='center', linespacing=1.18,
        bbox=dict(boxstyle='round,pad=0.20', facecolor=BLUE_BG, edgecolor=BLUE_BORDER, lw=1.2),
        zorder=9,
    )

    # Redshift progression indicator next to observer line
    ax_a.annotate(
        '',
        xy=(r_obs + 0.48, 7.28),
        xytext=(r_obs + 0.48, 4.38),
        arrowprops=dict(arrowstyle='-|>,head_length=0.45,head_width=0.24',
                        color=RED_LATE, lw=2.2),
        zorder=7,
    )
    ax_a.text(
        r_obs + 0.66, 5.83,
        "Increasing\nredshift",
        color=RED_LATE, fontsize=11.4, fontweight='bold',
        ha='left', va='center', rotation=90, linespacing=1.15, zorder=7,
    )

    # =========================================================================
    # 4. PANEL B — THERMAL RADIATION AND GREYBODY FACTORS (SCHEMATIC SPECTRA)
    # =========================================================================
    ax_b = fig.add_axes([right_x + 0.068, p_y + 0.118, p_w - 0.092, vp_h - 0.135], zorder=3)
    ax_b.set_facecolor(BG_WHITE)

    # Dimensionless frequency x = \hbar \omega / (k_B T_H)
    x = np.linspace(0.04, 9.5, 600)
    # Ideal Planck blackbody particle number flux spectrum: x^2 / (exp(x) - 1)
    flux_thermal = (x ** 2) / (np.exp(x) - 1.0)
    flux_peak = np.max(flux_thermal)
    flux_thermal_norm = flux_thermal / flux_peak  # Normalized so ideal peak = 1.0

    # Frequency-dependent greybody transmission factor \Gamma(\omega)
    gamma_w = (x ** 2.1) / (x ** 2.1 + 1.85 ** 2.1)
    flux_greybody_norm = flux_thermal_norm * gamma_w

    ax_b.set_xlim(0.0, 9.5)
    ax_b.set_ylim(0.0, 1.24)

    ax_b.spines['top'].set_visible(False)
    ax_b.spines['right'].set_visible(False)
    ax_b.spines['left'].set_edgecolor(AXIS_COLOR)
    ax_b.spines['left'].set_linewidth(1.8)
    ax_b.spines['bottom'].set_edgecolor(AXIS_COLOR)
    ax_b.spines['bottom'].set_linewidth(1.8)
    ax_b.tick_params(axis='x', pad=6, length=5, width=1.5, colors=AXIS_COLOR)
    ax_b.tick_params(axis='y', pad=6, length=5, width=1.5, colors=AXIS_COLOR)

    ax_b.plot(1.0, 0.0, ">", transform=ax_b.transAxes, color=AXIS_COLOR,
              markersize=8.5, clip_on=False, zorder=10)
    ax_b.plot(0.0, 1.0, "^", transform=ax_b.transAxes, color=AXIS_COLOR,
              markersize=8.5, clip_on=False, zorder=10)

    ax_b.set_xticks([0, 2, 4, 6, 8])
    ax_b.set_xticklabels([r"$0$", r"$2$", r"$4$", r"$6$", r"$8$"], fontsize=12.6, fontweight='bold')
    ax_b.set_yticks([0.0, 0.5, 1.0])
    ax_b.set_yticklabels([r"$0$", r"$0.5$", r"$1.0$"], fontsize=12.6, fontweight='bold')

    ax_b.set_xlabel(r"Dimensionless frequency,  $\hbar\omega / (k_B T_H)$",
                    fontsize=13.8, fontweight='bold', color=NAVY, labelpad=8)
    ax_b.set_ylabel("Spectral particle flux  (arb. units)",
                    fontsize=13.8, fontweight='bold', color=NAVY, labelpad=8)

    # Shaded gap between ideal thermal and greybody-modified spectrum (scattering reduction)
    ax_b.fill_between(
        x, flux_greybody_norm, flux_thermal_norm,
        color=BLUE_LIGHT, alpha=0.22, zorder=2,
    )
    ax_b.fill_between(
        x, 0.0, flux_greybody_norm,
        color='#fde68a', alpha=0.25, zorder=1.8,
    )

    # Plot curves:
    # 1) Ideal thermal spectrum (dashed blue)
    ax_b.plot(x, flux_thermal_norm, color=BLUE_MAIN, linestyle='--', linewidth=2.8, zorder=4)
    # 2) Predicted greybody-modified spectrum (solid orange)
    ax_b.plot(x, flux_greybody_norm, color=ORANGE_MAIN, linestyle='-', linewidth=3.4, zorder=5)

    # -------------------------------------------------------------------------
    # Panel B Callouts (clean, non-overlapping)
    # -------------------------------------------------------------------------
    # 1. Ideal thermal spectrum callout (pointing to peak at x ~ 1.59, y = 1.0)
    x_pk_th = x[np.argmax(flux_thermal_norm)]
    ax_b.scatter([x_pk_th], [1.0], s=54, color=BLUE_MAIN, edgecolors=BG_WHITE, linewidths=1.4, zorder=7)
    ax_b.annotate(
        "Ideal thermal spectrum\n" + r"(blackbody at temperature $T_H$)",
        xy=(x_pk_th, 1.0), xytext=(5.25, 0.99),
        arrowprops=dict(arrowstyle="-|>,head_length=0.42,head_width=0.22",
                        color=BLUE_DARK, lw=1.7, shrinkA=2, shrinkB=5),
        fontsize=11.6, fontweight='bold', color=BLUE_DARK, ha='center', va='center',
        linespacing=1.22,
        bbox=dict(boxstyle='round,pad=0.22', facecolor=BLUE_BG, edgecolor=BLUE_BORDER, lw=1.2),
        zorder=8,
    )

    # 2. Predicted greybody-modified spectrum callout (pointing to greybody curve at x ~ 2.95)
    idx_gb = np.argmin(np.abs(x - 2.95))
    ax_b.scatter([x[idx_gb]], [flux_greybody_norm[idx_gb]], s=54, color=ORANGE_MAIN,
                 edgecolors=BG_WHITE, linewidths=1.4, zorder=7)
    ax_b.annotate(
        "Predicted spectrum at infinity\nModified by greybody factors",
        xy=(x[idx_gb], flux_greybody_norm[idx_gb]), xytext=(6.65, 0.72),
        arrowprops=dict(arrowstyle="-|>,head_length=0.42,head_width=0.22",
                        color=ORANGE_DARK, lw=1.7, shrinkA=2, shrinkB=5),
        fontsize=11.6, fontweight='bold', color=ORANGE_DARK, ha='center', va='center',
        linespacing=1.22,
        bbox=dict(boxstyle='round,pad=0.22', facecolor=ORANGE_BG, edgecolor=ORANGE_BORDER, lw=1.2),
        zorder=8,
    )

    # 3. Low-frequency scattering suppression callout (pointing to shaded region around x = 1.18)
    ax_b.annotate(
        "Scattering by exterior\ngravitational potential\nsuppresses low frequencies",
        xy=(1.18, 0.50), xytext=(7.12, 0.40),
        arrowprops=dict(arrowstyle="-|>,head_length=0.42,head_width=0.22",
                        color=SLATE, lw=1.7, shrinkA=2, shrinkB=4,
                        connectionstyle="arc3,rad=-0.08"),
        fontsize=11.0, fontweight='bold', color=DARK_SLATE, ha='center', va='center',
        linespacing=1.20,
        bbox=dict(boxstyle='round,pad=0.20', facecolor=PANEL_BG, edgecolor=BORDER_COLOR, lw=1.2),
        zorder=8,
    )

    # Save figure and normalize to clean 24-bit RGB PNG
    fig.savefig(output_path, dpi=dpi, facecolor=BG_WHITE, edgecolor='none')
    plt.close(fig)

    with Image.open(output_path) as im:
        rgb_im = im.convert("RGB")
        rgb_im.save(output_path, format="PNG", optimize=True)

    size_kb = output_path.stat().st_size / 1024.0
    print(f"[OK] Generated {output_path} ({fig_w * dpi:.0f} x {fig_h * dpi:.0f} px, {size_kb:.1f} KB)")


if __name__ == "__main__":
    create_figure()
