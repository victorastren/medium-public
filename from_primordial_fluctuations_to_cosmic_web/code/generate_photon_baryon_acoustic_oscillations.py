#!/usr/bin/env python3
r"""
Generate three-panel vertical figure:
"Photon-Baryon Acoustic Oscillations: Growth, Damping, and Evidence"

Figure for Section 3.2 ("Photon-Baryon Acoustic Oscillations") of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design & Scientific Specifications:
- Single portrait-oriented, three-panel scientific figure arranged vertically (A, B, C).
- Canvas: 1890 x 2730 px at 140 DPI (13.5 x 19.5 in), matching the exact 13.5 in width
  and 140 DPI typography scale of `horizon_entry_perturbations.png` and
  `jeans_instability_dispersion_relation.png` (and the 2:3 portrait ratio of 1400 x 2100).
- Consistent color palette throughout:
  - Orange (#ea580c / #9a3412): Photon-baryon fluid
  - Blue (#2563eb / #1e3a8a): Cold dark matter & theoretical LCDM CMB curve
  - Purple (#7c3aed / #5b21b6): Photon diffusion & Silk damping
  - Dark gray/slate (#1e293b): Published Planck 2018 CMB TT observational data
- Panel A: Acoustic Oscillations and Cold Dark Matter
  - Left: Physical mechanism showing gravitational compression vs. photon-pressure expansion
    connected by curved oscillation-cycle arrows.
  - Right: Schematic evolution of a fixed subhorizon Fourier mode during radiation domination.
- Panel B: Photon Diffusion and Silk Damping
  - Left: Diffusion mechanism with repeated photon scattering, energy transport, and smoothing.
  - Right: Scale-dependent damping of relative acoustic amplitude vs. comoving wavenumber k.
- Panel C: Observational Evidence: CMB Acoustic Peaks
  - Published Planck 2018 binned TT power spectrum (COM_PowerSpect_CMB-TT-binned_R3.01.txt)
    and best-fit LCDM theoretical curve (l = 30 to 2000).
"""

from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "photon_baryon_acoustic_oscillations.png"


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure mathtext and typography (aligned with horizon_entry_perturbations.png)
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 13.5,
    })

    # Portrait 3-panel canvas: 13.5 x 17.2 in at 140 DPI (1890 x 2408 px)
    fig_w, fig_h = 13.5, 17.2
    dpi = 140
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#475569'
    LIGHT_SLATE = '#64748b'
    AXIS_COLOR = '#334155'
    BORDER_COLOR = '#cbd5e1'
    CARD_BG = '#f8fafc'

    # Photon-baryon fluid (Orange)
    ORANGE_DEEP = '#9a3412'
    ORANGE_DARK = '#c2410c'
    ORANGE = '#ea580c'
    ORANGE_LIGHT = '#fdba74'
    ORANGE_BG = '#fff7ed'

    # Cold dark matter & theoretical curve (Blue)
    BLUE_DEEP = '#1e3a8a'
    BLUE_DARK = '#1d4ed8'
    BLUE = '#2563eb'
    BLUE_LIGHT = '#93c5fd'
    BLUE_BG = '#eff6ff'

    # Photon diffusion & Silk damping (Purple)
    PURPLE_DEEP = '#5b21b6'
    PURPLE_DARK = '#6d28d9'
    PURPLE = '#7c3aed'
    PURPLE_LIGHT = '#c4b5fd'
    PURPLE_BG = '#f5f3ff'

    # -------------------------------------------------------------------------
    # 1. Top Header Banner (y: 0.965 - 0.992)
    # -------------------------------------------------------------------------
    ax_head = fig.add_axes([0.025, 0.965, 0.950, 0.027])
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)
    ax_head.axis('off')

    title_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.008",
                               mutation_aspect=(0.950 * fig_w) / (0.027 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_head.add_patch(title_box)
    ax_head.text(0.50, 0.50, "PHOTON–BARYON ACOUSTIC OSCILLATIONS",
                 color=NAVY, fontsize=18.5, fontweight='bold', ha='center', va='center')

    # =========================================================================
    # PANEL A — ACOUSTIC OSCILLATIONS AND COLD DARK MATTER (y: 0.643 - 0.957)
    # =========================================================================
    ax_frame_a = fig.add_axes([0.025, 0.643, 0.950, 0.314])
    ax_frame_a.set_xlim(0, 1)
    ax_frame_a.set_ylim(0, 1)
    ax_frame_a.axis('off')
    frame_a = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                             boxstyle="round,pad=0.0,rounding_size=0.008",
                             mutation_aspect=(0.950 * fig_w) / (0.314 * fig_h),
                             clip_on=False,
                             facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_frame_a.add_patch(frame_a)

    # Panel A Header Badge (compact vertical padding)
    hdr_a = FancyBboxPatch((0.015, 0.908), 0.970, 0.072,
                           boxstyle="round,pad=0.0,rounding_size=0.006",
                           mutation_aspect=(0.950 * fig_w) / (0.314 * fig_h),
                           facecolor=ORANGE_BG, edgecolor=ORANGE_LIGHT, linewidth=1.2)
    ax_frame_a.add_patch(hdr_a)
    ax_frame_a.text(0.032, 0.944, "A — Acoustic Oscillations and Cold Dark Matter",
                    color=ORANGE_DEEP, fontsize=16.0, fontweight='bold', ha='left', va='center')

    # Panel A Internal Explanatory Line (bottom of Panel A)
    ax_frame_a.text(0.50, 0.036,
                    "Baryonic perturbations oscillate, while cold-dark-matter perturbations can grow slowly without photon pressure.",
                    color=DARK_SLATE, fontsize=15.5, style='italic', ha='center', va='center')

    # -------------------------------------------------------------------------
    # Panel A Left: Physical Mechanism Schematic
    # -------------------------------------------------------------------------
    ax_a_left = fig.add_axes([0.040, 0.672, 0.415, 0.246])
    ax_a_left.set_xlim(0, 10)
    ax_a_left.set_ylim(0, 10)
    ax_a_left.axis('off')

    mech_box = FancyBboxPatch((0.1, 0.1), 9.8, 9.8,
                              boxstyle="round,pad=0.0,rounding_size=0.20",
                              mutation_aspect=(0.415 * fig_w) / (0.246 * fig_h),
                              facecolor='#fffaf5', edgecolor='#fed7aa', linewidth=1.2)
    ax_a_left.add_patch(mech_box)

    # Stage 1 (Top): Gravitational compression
    ax_a_left.text(5.0, 9.15, "Gravity: compression",
                   color=ORANGE_DEEP, fontsize=15.0, fontweight='bold', ha='center', va='center')
    ax_a_left.text(5.0, 8.32, "Gravitational attraction",
                   color=SLATE, fontsize=14.2, fontweight='bold', ha='center', va='center')

    c1_x, c1_y = 5.0, 6.45
    ax_a_left.add_patch(Circle((c1_x, c1_y), 1.35, facecolor='#ffedd5', edgecolor=ORANGE_LIGHT, lw=1.4, zorder=2))
    ax_a_left.add_patch(Circle((c1_x, c1_y), 0.82, facecolor='#fdba74', edgecolor=ORANGE, lw=1.4, zorder=3))
    ax_a_left.add_patch(Circle((c1_x, c1_y), 0.38, facecolor=ORANGE, edgecolor=ORANGE_DEEP, lw=1.2, zorder=4))

    # Inward-pointing compression arrows (left, right, top-left, top-right, bottom-left, bottom-right)
    for angle_deg in [0, 60, 120, 180, 240, 300]:
        rad = np.deg2rad(angle_deg)
        r_start, r_end = 1.65, 0.88
        ax_a_left.annotate(
            "",
            xy=(c1_x + r_end * np.cos(rad), c1_y + r_end * np.sin(rad)),
            xytext=(c1_x + r_start * np.cos(rad), c1_y + r_start * np.sin(rad)),
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=2.0, mutation_scale=13),
            zorder=6
        )

    # Stage 2 (Bottom): Photon pressure response
    c2_x, c2_y = 5.0, 2.88
    ax_a_left.add_patch(Circle((c2_x, c2_y), 1.35, facecolor='#fff7ed', edgecolor=ORANGE_LIGHT, lw=1.4, linestyle='--', zorder=2))
    ax_a_left.add_patch(Circle((c2_x, c2_y), 0.72, facecolor='#fed7aa', edgecolor=ORANGE, lw=1.4, zorder=3))

    # Outward-pointing expansion arrows
    for angle_deg in [0, 60, 120, 180, 240, 300]:
        rad = np.deg2rad(angle_deg)
        r_start, r_end = 0.65, 1.55
        ax_a_left.annotate(
            "",
            xy=(c2_x + r_end * np.cos(rad), c2_y + r_end * np.sin(rad)),
            xytext=(c2_x + r_start * np.cos(rad), c2_y + r_start * np.sin(rad)),
            arrowprops=dict(arrowstyle="->", color=ORANGE_DARK, lw=2.0, mutation_scale=13),
            zorder=6
        )

    ax_a_left.text(5.0, 1.12, "Photon pressure: expansion",
                   color=ORANGE_DEEP, fontsize=15.0, fontweight='bold', ha='center', va='center')
    ax_a_left.text(5.0, 0.36, "Radiation pressure",
                   color=SLATE, fontsize=14.2, fontweight='bold', ha='center', va='center')

    # Curved oscillation cycle arrows connecting Stage 1 and Stage 2
    cycle_left = FancyArrowPatch((2.75, 6.20), (2.75, 3.10),
                                 connectionstyle="arc3,rad=0.35",
                                 arrowstyle="->,head_length=7,head_width=5",
                                 color=ORANGE_DEEP, linewidth=2.2, zorder=5)
    cycle_right = FancyArrowPatch((7.35, 3.10), (7.35, 6.20),
                                  connectionstyle="arc3,rad=0.35",
                                  arrowstyle="->,head_length=7,head_width=5",
                                  color=ORANGE_DEEP, linewidth=2.2, zorder=5)
    ax_a_left.add_patch(cycle_left)
    ax_a_left.add_patch(cycle_right)

    ax_a_left.text(1.20, 4.65, "Recurring\noscillation",
                   color=ORANGE_DEEP, fontsize=14.4, fontweight='bold', ha='center', va='center')
    ax_a_left.set_xlim(0, 10)
    ax_a_left.set_ylim(0, 10)

    # -------------------------------------------------------------------------
    # Panel A Right: Evolution of a Representative Fourier Mode
    # -------------------------------------------------------------------------
    ax_a_right = fig.add_axes([0.545, 0.700, 0.405, 0.208])
    ax_a_right.set_facecolor('#ffffff')

    a_vals = np.linspace(0.0, 10.0, 400)
    # Schematic oscillatory photon-baryon contrast (alternating positive and negative)
    delta_b = 0.65 * np.cos(1.38 * a_vals - 0.35)
    # Schematic slowly growing logarithmic CDM density contrast during radiation domination
    delta_cdm = 0.14 + 0.31 * np.log(1.0 + 0.85 * a_vals)

    ax_a_right.set_xlim(0.0, 10.5)
    ax_a_right.set_ylim(-1.16, 1.62)

    # Small indication at top-left that curves show schematic evolution during radiation domination
    ax_a_right.text(0.25, 1.56, "Schematic evolution of one Fourier mode\n(during radiation domination)",
                    color=SLATE, fontsize=14.5, style='italic', linespacing=1.18,
                    ha='left', va='top', zorder=7)

    # Faint zero-density-contrast reference line
    ax_a_right.axhline(0.0, color='#94a3b8', linestyle='--', linewidth=1.5, zorder=2)
    ax_a_right.text(10.35, -0.08, r"$\delta = 0$", color=SLATE, fontsize=14.5,
                    ha='right', va='top', zorder=3)

    # Plot curves
    ax_a_right.plot(a_vals, delta_b, color=ORANGE, linewidth=3.5, zorder=5)
    ax_a_right.plot(a_vals, delta_cdm, color=BLUE, linewidth=3.5, zorder=6)

    # Curve labels (cleanly separated in open whitespace)
    ax_a_right.text(6.95, 0.88, "Cold dark matter — slow growth",
                    color=BLUE_DEEP, fontsize=14.5, fontweight='bold', ha='center', va='bottom', zorder=7)
    ax_a_right.text(4.80, -1.06, "Photon–baryon fluid",
                    color=ORANGE_DEEP, fontsize=14.8, fontweight='bold', ha='center', va='bottom', zorder=7)

    # Directed spines with arrowheads
    ax_a_right.spines['top'].set_visible(False)
    ax_a_right.spines['right'].set_visible(False)
    ax_a_right.spines['left'].set_edgecolor(AXIS_COLOR)
    ax_a_right.spines['left'].set_linewidth(1.8)
    ax_a_right.spines['bottom'].set_edgecolor(AXIS_COLOR)
    ax_a_right.spines['bottom'].set_linewidth(1.8)
    ax_a_right.plot(1.0, 0.0, ">", transform=ax_a_right.transAxes, color=AXIS_COLOR,
                    markersize=8, clip_on=False, zorder=10)
    ax_a_right.plot(0.0, 1.0, "^", transform=ax_a_right.transAxes, color=AXIS_COLOR,
                    markersize=8, clip_on=False, zorder=10)

    ax_a_right.set_xticks([])
    ax_a_right.set_yticks([0.0])
    ax_a_right.set_yticklabels(['0'], fontsize=13.5, fontweight='bold', color=DARK_SLATE)
    ax_a_right.tick_params(axis='y', pad=6, length=5, width=1.5, colors=AXIS_COLOR)

    ax_a_right.set_xlabel("Scale factor " + r"$a \longrightarrow$",
                          fontsize=14.5, fontweight='bold', color=NAVY, labelpad=8)
    ax_a_right.set_ylabel("Density contrast " + r"$\delta$" + "\n(schematic)",
                          fontsize=14.5, fontweight='bold', color=NAVY, labelpad=8)

    # =========================================================================
    # PANEL B — PHOTON DIFFUSION AND SILK DAMPING (y: 0.321 - 0.635)
    # =========================================================================
    ax_frame_b = fig.add_axes([0.025, 0.321, 0.950, 0.314])
    ax_frame_b.set_xlim(0, 1)
    ax_frame_b.set_ylim(0, 1)
    ax_frame_b.axis('off')
    frame_b = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                             boxstyle="round,pad=0.0,rounding_size=0.008",
                             mutation_aspect=(0.950 * fig_w) / (0.314 * fig_h),
                             clip_on=False,
                             facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_frame_b.add_patch(frame_b)

    # Panel B Header Badge (compact vertical padding)
    hdr_b = FancyBboxPatch((0.015, 0.908), 0.970, 0.072,
                           boxstyle="round,pad=0.0,rounding_size=0.006",
                           mutation_aspect=(0.950 * fig_w) / (0.314 * fig_h),
                           facecolor=PURPLE_BG, edgecolor=PURPLE_LIGHT, linewidth=1.2)
    ax_frame_b.add_patch(hdr_b)
    ax_frame_b.text(0.032, 0.944, "B — Photon Diffusion and Silk Damping",
                    color=PURPLE_DEEP, fontsize=16.0, fontweight='bold', ha='left', va='center')

    # Panel B Internal Explanatory Line (bottom of Panel B)
    ax_frame_b.text(0.50, 0.036,
                    "Photon diffusion progressively suppresses short-wavelength acoustic perturbations.",
                    color=DARK_SLATE, fontsize=15.5, style='italic', ha='center', va='center')

    # -------------------------------------------------------------------------
    # Panel B Left: Photon Diffusion Mechanism Schematic
    # -------------------------------------------------------------------------
    ax_b_left = fig.add_axes([0.040, 0.350, 0.415, 0.246])
    ax_b_left.set_xlim(0, 10)
    ax_b_left.set_ylim(0, 10)
    ax_b_left.axis('off')

    diff_box = FancyBboxPatch((0.1, 0.1), 9.8, 9.8,
                              boxstyle="round,pad=0.0,rounding_size=0.20",
                              mutation_aspect=(0.415 * fig_w) / (0.246 * fig_h),
                              facecolor='#faf5ff', edgecolor='#ddd6fe', linewidth=1.2)
    ax_b_left.add_patch(diff_box)

    # Neighboring denser/hotter (left) and less dense/cooler (right) plasma zones
    hot_zone = FancyBboxPatch((0.55, 1.65), 4.15, 6.45,
                              boxstyle="round,pad=0.0,rounding_size=0.18",
                              mutation_aspect=(0.415 * fig_w) / (0.246 * fig_h),
                              facecolor='#ffedd5', edgecolor='#fdba74', linewidth=1.2, zorder=1)
    cool_zone = FancyBboxPatch((5.30, 1.65), 4.15, 6.45,
                               boxstyle="round,pad=0.0,rounding_size=0.18",
                               mutation_aspect=(0.415 * fig_w) / (0.246 * fig_h),
                               facecolor='#f1f5f9', edgecolor='#94a3b8', linewidth=1.2, zorder=1)
    ax_b_left.add_patch(hot_zone)
    ax_b_left.add_patch(cool_zone)

    ax_b_left.text(2.62, 7.55, "Denser / hotter",
                   color=ORANGE_DEEP, fontsize=14.2, fontweight='bold', ha='center', va='center', zorder=3)
    ax_b_left.text(7.38, 7.55, "Less dense / cooler",
                   color=SLATE, fontsize=14.2, fontweight='bold', ha='center', va='center', zorder=3)

    # Top label: Repeated photon scattering
    ax_b_left.text(5.0, 9.10, "Repeated photon scattering",
                   color=PURPLE_DEEP, fontsize=15.0, fontweight='bold', ha='center', va='center')

    # Baryon / electron scattering centers (orange circles)
    scatter_pts = [
        (1.4, 6.2), (2.3, 5.1), (3.4, 6.1), (4.2, 4.8), (5.8, 5.7), (7.1, 4.9),
        (1.6, 3.6), (2.8, 2.7), (3.9, 3.5), (5.0, 2.8), (6.4, 3.6), (7.9, 2.9),
        (1.2, 4.8), (3.1, 4.2), (8.5, 5.6), (8.6, 3.8)
    ]
    for (sx, sy) in scatter_pts:
        ax_b_left.add_patch(Circle((sx, sy), 0.18, facecolor=ORANGE, edgecolor='#ffffff', lw=0.8, zorder=4))

    # Three zigzag photon random-walk paths transporting energy from left to right
    paths = [
        [(1.4, 6.2), (2.3, 5.1), (3.4, 6.1), (4.2, 4.8), (5.8, 5.7), (7.5, 5.0)],
        [(1.6, 3.6), (2.8, 2.7), (3.9, 3.5), (5.0, 2.8), (6.4, 3.6), (8.0, 3.0)],
    ]
    for path in paths:
        px = [p[0] for p in path]
        py = [p[1] for p in path]
        ax_b_left.plot(px[:-1], py[:-1], color=PURPLE, linestyle='--', linewidth=2.4, zorder=5)
        ax_b_left.annotate(
            "",
            xy=path[-1], xytext=path[-2],
            arrowprops=dict(arrowstyle="->", color=PURPLE_DEEP, lw=2.5, mutation_scale=14),
            zorder=6
        )
        # Small purple dots at photon vertices
        ax_b_left.scatter(px[:-1], py[:-1], s=32, color=PURPLE_DEEP, zorder=6)

    # Energy transport label in the center bridge
    ax_b_left.text(5.0, 6.72, "Energy transport " + r"$\longrightarrow$",
                   color=PURPLE_DEEP, fontsize=14.6, fontweight='bold', ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.22,rounding_size=0.15",
                             facecolor='#ffffff', edgecolor=PURPLE_LIGHT, lw=1.1),
                   zorder=7)

    # Bottom label: Smoothing of fluctuations
    ax_b_left.text(5.0, 0.82, "Smoothing of fluctuations",
                   color=DARK_SLATE, fontsize=14.8, fontweight='bold', ha='center', va='center')
    ax_b_left.set_xlim(0, 10)
    ax_b_left.set_ylim(0, 10)

    # -------------------------------------------------------------------------
    # Panel B Right: Scale-Dependent Silk Damping Factor Plot
    # -------------------------------------------------------------------------
    ax_b_right = fig.add_axes([0.545, 0.388, 0.405, 0.200])
    ax_b_right.set_facecolor('#ffffff')

    k_vals = np.linspace(0.0, 10.0, 400)
    k_D = 5.8
    amp_undamped = np.ones_like(k_vals)
    amp_damped = np.exp(-(k_vals / k_D)**2.0)

    ax_b_right.set_xlim(0.0, 10.5)
    ax_b_right.set_ylim(0.0, 1.25)

    # Shade Silk damping region between undamped reference (1) and D_Silk(k)
    ax_b_right.fill_between(k_vals, amp_damped, amp_undamped,
                            facecolor='#ede9fe', alpha=0.70, zorder=1)

    # Characteristic diffusion-damping wavenumber k_D guide line
    y_kD = np.exp(-1.0)
    ax_b_right.plot([k_D, k_D], [0.0, y_kD], color=PURPLE_LIGHT, linestyle=':', linewidth=1.8, zorder=3)
    ax_b_right.scatter([k_D], [y_kD], s=36, color=PURPLE_DEEP, zorder=6)

    # Plot curves
    ax_b_right.plot(k_vals, amp_undamped, color=LIGHT_SLATE, linestyle='--', linewidth=2.6, zorder=4)
    ax_b_right.plot(k_vals, amp_damped, color=PURPLE, linewidth=3.6, zorder=5)

    # Labels on curves: No diffusion damping reference & explicit D_Silk(k) formula
    ax_b_right.text(0.35, 1.05, "No diffusion damping",
                    color=SLATE, fontsize=14.6, fontweight='bold', ha='left', va='bottom', zorder=6)
    ax_b_right.text(2.90, 0.34, r"$D_{\mathrm{Silk}}(k) \sim e^{-(k/k_D)^2}$",
                    color=PURPLE_DEEP, fontsize=16.2, fontweight='bold', ha='center', va='center', zorder=6)

    # Vertical double-arrow and label for Silk damping
    k_mark = 7.7
    y_d_mark = np.exp(-(k_mark / k_D)**2.0)
    ax_b_right.annotate(
        "",
        xy=(k_mark, 0.98), xytext=(k_mark, y_d_mark + 0.02),
        arrowprops=dict(arrowstyle="<->", color=PURPLE_DEEP, lw=2.0, mutation_scale=13),
        zorder=7
    )
    ax_b_right.text(k_mark + 0.25, 0.56, "Silk\ndamping",
                    color=PURPLE_DEEP, fontsize=15.0, fontweight='bold', ha='left', va='center', zorder=7)

    # Directed spines with arrowheads
    ax_b_right.spines['top'].set_visible(False)
    ax_b_right.spines['right'].set_visible(False)
    ax_b_right.spines['left'].set_edgecolor(AXIS_COLOR)
    ax_b_right.spines['left'].set_linewidth(1.8)
    ax_b_right.spines['bottom'].set_edgecolor(AXIS_COLOR)
    ax_b_right.spines['bottom'].set_linewidth(1.8)
    ax_b_right.plot(1.0, 0.0, ">", transform=ax_b_right.transAxes, color=AXIS_COLOR,
                    markersize=8, clip_on=False, zorder=10)
    ax_b_right.plot(0.0, 1.0, "^", transform=ax_b_right.transAxes, color=AXIS_COLOR,
                    markersize=8, clip_on=False, zorder=10)

    ax_b_right.set_xticks([k_D])
    ax_b_right.set_xticklabels([r"$k_D$"], fontsize=15.2, fontweight='bold', color=PURPLE_DEEP)
    ax_b_right.set_yticks([0.0, 1.0])
    ax_b_right.set_yticklabels(['0', '1'], fontsize=13.5, fontweight='bold', color=DARK_SLATE)
    ax_b_right.tick_params(axis='both', pad=5, length=5, width=1.5, colors=AXIS_COLOR)

    ax_b_right.set_ylabel("Relative amplitude\nretained",
                          fontsize=14.5, fontweight='bold', color=NAVY, labelpad=8)
    ax_b_right.text(-0.01, -0.130, "Comoving wavenumber " + r"$k \longrightarrow$",
                    transform=ax_b_right.transAxes, fontsize=14.2, fontweight='bold', color=NAVY,
                    ha='left', va='top')
    ax_b_right.text(1.01, -0.130, "(smaller spatial scales)",
                    transform=ax_b_right.transAxes, fontsize=13.2, color=SLATE,
                    ha='right', va='top')

    # =========================================================================
    # PANEL C — OBSERVATIONAL EVIDENCE: CMB ACOUSTIC PEAKS (y: 0.008 - 0.313)
    # =========================================================================
    ax_frame_c = fig.add_axes([0.025, 0.008, 0.950, 0.305])
    ax_frame_c.set_xlim(0, 1)
    ax_frame_c.set_ylim(0, 1)
    ax_frame_c.axis('off')
    frame_c = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                             boxstyle="round,pad=0.0,rounding_size=0.008",
                             mutation_aspect=(0.950 * fig_w) / (0.305 * fig_h),
                             clip_on=False,
                             facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_frame_c.add_patch(frame_c)

    # Panel C Header Badge (compact vertical padding)
    hdr_c = FancyBboxPatch((0.015, 0.906), 0.970, 0.074,
                           boxstyle="round,pad=0.0,rounding_size=0.006",
                           mutation_aspect=(0.950 * fig_w) / (0.305 * fig_h),
                           facecolor=BLUE_BG, edgecolor=BLUE_LIGHT, linewidth=1.2)
    ax_frame_c.add_patch(hdr_c)
    ax_frame_c.text(0.032, 0.943, "C — Observational Evidence: CMB Acoustic Peaks",
                    color=BLUE_DEEP, fontsize=16.0, fontweight='bold', ha='left', va='center')

    # Panel C Internal Explanatory Line (bottom of Panel C)
    ax_frame_c.text(0.50, 0.036,
                    "The measured CMB acoustic peaks provide strong evidence for oscillations in the early photon–baryon plasma.",
                    color=DARK_SLATE, fontsize=15.5, style='italic', ha='center', va='center')

    # -------------------------------------------------------------------------
    # Panel C Main Plot: Published Planck 2018 Binned TT Power Spectrum
    # -------------------------------------------------------------------------
    ax_c = fig.add_axes([0.132, 0.068, 0.818, 0.202])
    ax_c.set_facecolor('#ffffff')

    binned_file = DATA_DIR / "COM_PowerSpect_CMB-TT-binned_R3.01.txt"
    theory_file = DATA_DIR / "COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt"

    binned = np.loadtxt(binned_file)
    theory = np.loadtxt(theory_file)

    # Filter to l = 30 - 2000
    mask_b = (binned[:, 0] >= 30.0) & (binned[:, 0] <= 2000.0)
    ell_b = binned[mask_b, 0]
    dl_b = binned[mask_b, 1]
    err_minus = binned[mask_b, 2]
    err_plus = binned[mask_b, 3]

    mask_t = (theory[:, 0] >= 30.0) & (theory[:, 0] <= 2000.0)
    ell_t = theory[mask_t, 0]
    dl_t = theory[mask_t, 1]

    ax_c.set_xlim(30, 2000)
    ax_c.set_ylim(0, 6400)

    ax_c.grid(True, which='major', color='#f1f5f9', linestyle='-', linewidth=1.1, zorder=0)

    # Theoretical best-fit cosmological model curve (thin blue curve)
    ax_c.plot(ell_t, dl_t, color=BLUE, linewidth=2.4, label="Best-fit cosmological model", zorder=4)

    # Published Planck 2018 binned measurements with uncertainty bars (dark gray/slate points)
    ax_c.errorbar(ell_b, dl_b, yerr=[err_minus, err_plus],
                  fmt='o', markersize=4.5, color=DARK_SLATE, ecolor=DARK_SLATE,
                  elinewidth=1.4, capsize=2.0, label="Planck 2018 data", zorder=6)

    # Subtle annotation: "Acoustic peaks" pointing to the first three peaks
    ax_c.text(575, 5680, "Acoustic peaks",
              color=BLUE_DEEP, fontsize=15.6, fontweight='bold', ha='center', va='center', zorder=8)

    # Arrows to Peak 1 (l=220, Dl=5730), Peak 2 (l=537, Dl=2594), Peak 3 (l=814, Dl=2542)
    ax_c.annotate("", xy=(245, 5680), xytext=(395, 5680),
                  arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.8,
                                  connectionstyle="arc3,rad=-0.05", shrinkA=4, shrinkB=5),
                  zorder=7)
    ax_c.annotate("", xy=(537, 2720), xytext=(555, 5280),
                  arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.8,
                                  connectionstyle="arc3,rad=0.04", shrinkA=4, shrinkB=5),
                  zorder=7)
    ax_c.annotate("", xy=(814, 2670), xytext=(645, 5280),
                  arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.8,
                                  connectionstyle="arc3,rad=-0.08", shrinkA=4, shrinkB=5),
                  zorder=7)

    # Historical callout box & data key in the upper-right open area (l = 980 - 1970)
    hist_aspect = ((0.818 * fig_w) / 1970.0) / ((0.202 * fig_h) / 6400.0)
    hist_box = FancyBboxPatch((980, 2150), 990, 4050,
                              boxstyle="round,pad=0.0,rounding_size=16",
                              mutation_aspect=hist_aspect,
                              facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.2, zorder=7)
    ax_c.add_patch(hist_box)
    ax_c.text(1475, 5680, "WMAP (2003) " + r"$\longrightarrow$" + " Planck (2018 data)",
              color=NAVY, fontsize=15.2, fontweight='bold', ha='center', va='center', zorder=8)
    ax_c.text(1475, 4720, "Increasingly precise measurements\nof the CMB acoustic peaks",
              color=DARK_SLATE, fontsize=14.5, linespacing=1.28, ha='center', va='center', zorder=8)

    # Subtle divider separating historical context from the two-line data legend
    ax_c.plot([1045, 1905], [3980, 3980], color='#cbd5e1', linewidth=1.0, zorder=8)

    # Two-line legend inside the lower half of the callout box
    ax_c.errorbar([1165], [3420], yerr=[[250], [250]], fmt='o', markersize=5.2,
                  color=DARK_SLATE, ecolor=DARK_SLATE, elinewidth=1.5, capsize=2.2, zorder=8)
    ax_c.text(1210, 3420, "Planck 2018 data",
              color=DARK_SLATE, fontsize=14.4, fontweight='bold', ha='left', va='center', zorder=8)

    ax_c.plot([1135, 1195], [2680, 2680], color=BLUE, linewidth=2.8, zorder=8)
    ax_c.text(1210, 2680, "Best-fit cosmological model",
              color=BLUE_DEEP, fontsize=14.4, fontweight='bold', ha='left', va='center', zorder=8)

    # Axes spines, ticks, and labels
    ax_c.spines['top'].set_visible(False)
    ax_c.spines['right'].set_visible(False)
    ax_c.spines['left'].set_edgecolor(AXIS_COLOR)
    ax_c.spines['left'].set_linewidth(1.8)
    ax_c.spines['bottom'].set_edgecolor(AXIS_COLOR)
    ax_c.spines['bottom'].set_linewidth(1.8)

    ax_c.set_xticks([30, 250, 500, 1000, 1500, 2000])
    ax_c.set_xticklabels(['30', '250', '500', '1000', '1500', '2000'],
                         fontsize=13.5, fontweight='bold', color=DARK_SLATE)
    ax_c.set_yticks([0, 2000, 4000, 6000])
    ax_c.set_yticklabels(['0', '2000', '4000', '6000'],
                         fontsize=13.5, fontweight='bold', color=DARK_SLATE)
    ax_c.tick_params(axis='both', pad=6, length=5, width=1.5, colors=AXIS_COLOR)

    ax_c.set_xlabel("Angular multipole " + r"$\ell$",
                    fontsize=14.5, fontweight='bold', color=NAVY, labelpad=6)
    ax_c.set_ylabel(r"$D_\ell^{\mathrm{TT}} = \ell(\ell + 1)C_\ell^{\mathrm{TT}}/(2\pi)$" + "\n" + r"$[\mu\mathrm{K}^2]$",
                    fontsize=14.2, fontweight='bold', color=NAVY, labelpad=8)

    # Save figure
    fig.savefig(output_path, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    print(f"[OK] Generated {output_path} ({fig_w * dpi:.0f} x {fig_h * dpi:.0f} px)")


if __name__ == "__main__":
    create_figure()
