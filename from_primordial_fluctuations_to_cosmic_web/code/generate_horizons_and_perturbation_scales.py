#!/usr/bin/env python3
r"""
Generate editorial figure:
"Particle Horizon, Hubble Radius, and Perturbation Scales"

Figure for Section 1.2 of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design specifications:
- Canvas: 1800 x 1320 px (15.0 x 11.0 in at 120 DPI).
- Typography: ALL text >= 14.0 pt across all labels and annotations.
- Top banner: Title & subtitle in rounded card.
- Panel A (left): Spacetime diagram showing the particle horizon as the causal limit
  of observation derived from the past light cone in cosmic time and comoving coordinates.
  Unobstructed cone with external callout box pointing directly into the interior.
- Panel B (right): Conceptual scale diagram showing the Hubble radius R_H = c/|H| as a
  characteristic expansion scale. Spacious dual cards (sub-Hubble vs. super-Hubble modes)
  with non-colliding labels and clear origin-to-boundary radius vector.
- Bottom banner: Explicit summary of the key distinction between causal reach and scale comparison.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "particle_horizon_hubble_radius.png"


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

    # Canvas: 1800 x 1320 px at 120 DPI (15.0 x 11.0 in)
    fig_w, fig_h = 15.0, 11.0
    dpi = 120
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'          # Hero headings
    DARK_SLATE = '#1e293b'    # Panel titles & primary labels
    SLATE = '#475569'         # Secondary text
    LIGHT_SLATE = '#64748b'   # Notes & axes
    BORDER_COLOR = '#cbd5e1'  # Card borders
    CARD_BG = '#f8fafc'       # Banner & card backgrounds

    # Accents
    BLUE = '#0284c7'
    BLUE_DARK = '#0369a1'
    BLUE_BG = '#f0f9ff'
    BLUE_LIGHT = '#e0f2fe'
    BLUE_BORDER = '#bae6fd'

    TEAL = '#0d9488'
    TEAL_DARK = '#0f766e'
    TEAL_BG = '#f0fdfa'
    TEAL_BORDER = '#99f6e4'

    CORAL = '#ea580c'
    CORAL_DARK = '#c2410c'
    CORAL_BG = '#fff7ed'
    CORAL_BORDER = '#fed7aa'

    AMBER_DARK = '#92400e'
    AMBER_BG = '#fef3c7'
    AMBER_BORDER = '#fde68a'

    # -------------------------------------------------------------------------
    # 1. Top Header Banner (y: 0.910 - 0.982, height ~95 px)
    # -------------------------------------------------------------------------
    ax_head = fig.add_axes([0.025, 0.910, 0.950, 0.072])
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)
    ax_head.axis('off')

    title_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.009",
                               mutation_aspect=(0.950 * fig_w) / (0.072 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_head.add_patch(title_box)

    ax_head.text(0.50, 0.66, "PARTICLE HORIZON, HUBBLE RADIUS, AND PERTURBATION SCALES",
                 color=NAVY, fontsize=21.5, fontweight='bold', ha='center', va='center')
    ax_head.text(0.50, 0.28, "Conceptual distinction between causal reach and characteristic perturbation scales",
                 color=SLATE, fontsize=16.5, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 2. Outer Panel Frames (y: 0.098 - 0.895, height ~1052 px)
    # -------------------------------------------------------------------------
    # Frame 1 (Left)
    ax_frame1 = fig.add_axes([0.025, 0.098, 0.465, 0.797])
    ax_frame1.set_facecolor('#ffffff')
    for spine in ax_frame1.spines.values():
        spine.set_edgecolor(BORDER_COLOR)
        spine.set_linewidth(1.4)
    ax_frame1.set_xticks([])
    ax_frame1.set_yticks([])

    # Frame 2 (Right)
    ax_frame2 = fig.add_axes([0.510, 0.098, 0.465, 0.797])
    ax_frame2.set_facecolor('#ffffff')
    for spine in ax_frame2.spines.values():
        spine.set_edgecolor(BORDER_COLOR)
        spine.set_linewidth(1.4)
    ax_frame2.set_xticks([])
    ax_frame2.set_yticks([])

    # -------------------------------------------------------------------------
    # 3. Panel Header Badges (y: 0.822 - 0.887, height ~86 px)
    # -------------------------------------------------------------------------
    # Panel A Header Badge
    ax_top_l = fig.add_axes([0.038, 0.822, 0.439, 0.065])
    ax_top_l.set_xlim(0, 1)
    ax_top_l.set_ylim(0, 1)
    ax_top_l.axis('off')

    head_a = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                            boxstyle="round,pad=0.0,rounding_size=0.014",
                            mutation_aspect=(0.439 * fig_w) / (0.065 * fig_h),
                            clip_on=False,
                            facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.3)
    ax_top_l.add_patch(head_a)
    ax_top_l.text(0.50, 0.67, "A. Particle Horizon",
                  color=BLUE_DARK, fontsize=18.0, fontweight='bold', ha='center', va='center')
    ax_top_l.text(0.50, 0.28, "Maximum causal reach of light since the early universe",
                  color=DARK_SLATE, fontsize=15.5, ha='center', va='center')

    # Panel B Header Badge
    ax_top_r = fig.add_axes([0.523, 0.822, 0.439, 0.065])
    ax_top_r.set_xlim(0, 1)
    ax_top_r.set_ylim(0, 1)
    ax_top_r.axis('off')

    head_b = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                            boxstyle="round,pad=0.0,rounding_size=0.014",
                            mutation_aspect=(0.439 * fig_w) / (0.065 * fig_h),
                            clip_on=False,
                            facecolor=TEAL_BG, edgecolor=TEAL_BORDER, linewidth=1.3)
    ax_top_r.add_patch(head_b)
    ax_top_r.text(0.50, 0.67, "B. Perturbation Scales and the Hubble Radius",
                  color=TEAL_DARK, fontsize=17.5, fontweight='bold', ha='center', va='center')
    ax_top_r.text(0.50, 0.28, r"Comparing perturbation wavelengths with $R_H(t) = c / |H(t)|$",
                  color=DARK_SLATE, fontsize=15.5, ha='center', va='center')

    # -------------------------------------------------------------------------
    # 4. Panel Bottom Summary Notes (y: 0.106 - 0.192, height ~113 px)
    # -------------------------------------------------------------------------
    # Panel A Bottom Note
    ax_bot_l = fig.add_axes([0.038, 0.106, 0.439, 0.086])
    ax_bot_l.set_xlim(0, 1)
    ax_bot_l.set_ylim(0, 1)
    ax_bot_l.axis('off')

    sum_box_l = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.014",
                               mutation_aspect=(0.439 * fig_w) / (0.086 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.2)
    ax_bot_l.add_patch(sum_box_l)
    ax_bot_l.text(0.50, 0.74, r"Causal limit of observation at time $t$",
                  color=DARK_SLATE, fontsize=15.5, fontweight='bold', ha='center', va='center')
    ax_bot_l.text(0.50, 0.33, "Determined by cumulative light propagation\nfrom the cosmic origin ($t = 0$)",
                  color=SLATE, fontsize=15.0, ha='center', va='center', linespacing=1.25)

    # Panel B Bottom Note
    ax_bot_r = fig.add_axes([0.523, 0.106, 0.439, 0.086])
    ax_bot_r.set_xlim(0, 1)
    ax_bot_r.set_ylim(0, 1)
    ax_bot_r.axis('off')

    clarif_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                                boxstyle="round,pad=0.0,rounding_size=0.014",
                                mutation_aspect=(0.439 * fig_w) / (0.086 * fig_h),
                                clip_on=False,
                                facecolor=AMBER_BG, edgecolor=AMBER_BORDER, linewidth=1.2)
    ax_bot_r.add_patch(clarif_box)
    ax_bot_r.text(0.50, 0.74, "The Hubble radius is not generally a causal horizon.",
                  color=AMBER_DARK, fontsize=15.5, fontweight='bold', ha='center', va='center')
    ax_bot_r.text(0.50, 0.33, "Used to compare perturbation wavelengths\nacross cosmic expansion epochs",
                  color='#78350f', fontsize=15.0, ha='center', va='center', linespacing=1.25)

    # -------------------------------------------------------------------------
    # 5. Inner Plot 1: Spacetime Diagram (Panel A)
    # -------------------------------------------------------------------------
    # Position: x: 0.038 to 0.477, y: 0.200 to 0.812 (height 0.612)
    ax_plot1 = fig.add_axes([0.038, 0.200, 0.439, 0.612])
    ax_plot1.set_xlim(-1.80, 1.80)
    ax_plot1.set_ylim(-0.06, 1.16)
    ax_plot1.axis('off')

    # Baseline: Beginning of cosmic expansion (t = 0) at y = 0.10
    y_base = 0.10
    ax_plot1.plot([-1.55, 1.55], [y_base, y_base], color=SLATE, linewidth=2.0, zorder=3)
    ax_plot1.text(0, y_base - 0.065, "Beginning of cosmic expansion  (t = 0)",
                  color=DARK_SLATE, fontsize=15.5, fontweight='bold', ha='center', va='top')

    # Present epoch line (t = 0.98): Prominent, high-contrast observer dotted line
    t_obs = 0.98
    ax_plot1.plot([-1.35, 1.35], [t_obs, t_obs], color='#475569', linewidth=2.4, linestyle=':', zorder=2)

    # Observer worldline
    ax_plot1.plot([0, 0], [y_base, t_obs], color='#94a3b8', linewidth=1.6, linestyle=':', zorder=2)
    ax_plot1.plot(0, t_obs, marker='o', markersize=9, color=BLUE_DARK,
                  markeredgecolor='white', markeredgewidth=2.0, zorder=10)
    ax_plot1.text(0, t_obs + 0.045, r"Observer at time $t$",
                  color=NAVY, fontsize=17.0, fontweight='bold', ha='center', va='bottom', zorder=10)

    # Past Light Cone curves: t in [y_base, t_obs], chi in [-chi_max, chi_max]
    chi_max = 0.80
    chi_pts = np.linspace(-chi_max, chi_max, 300)
    t_pts = y_base + (t_obs - y_base) * (1.0 - np.abs(chi_pts) / chi_max) ** 1.80

    # Fill light cone (unobstructed clean pastel fill representing the causal past)
    ax_plot1.fill_between(chi_pts, y_base, t_pts, color=BLUE_LIGHT, alpha=0.85, zorder=2)

    # Outer regions (signals have not reached observer)
    ax_plot1.fill_between([-1.60, -chi_max], [y_base, y_base], [t_obs, y_base], color='#f8fafc', alpha=0.7, zorder=1)
    ax_plot1.fill_between([chi_max, 1.60], [y_base, y_base], [t_obs, y_base], color='#f8fafc', alpha=0.7, zorder=1)

    # Boundary lines for past light cone (null light rays)
    ax_plot1.plot(chi_pts[chi_pts <= 0], t_pts[chi_pts <= 0], color=BLUE_DARK, linewidth=2.8, zorder=4)
    ax_plot1.plot(chi_pts[chi_pts >= 0], t_pts[chi_pts >= 0], color=BLUE_DARK, linewidth=2.8, zorder=4)

    # External Callout Box for Causal Past (Cleanly separated outside the cone)
    call_x = -1.58
    call_w = 1.20
    call_y = 0.47
    call_h = 0.36
    callout_box = FancyBboxPatch((call_x, call_y), call_w, call_h,
                                 boxstyle="round,pad=0.015,rounding_size=0.06",
                                 facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.4, zorder=7)
    ax_plot1.add_patch(callout_box)
    cx = call_x + call_w / 2
    ax_plot1.text(cx, call_y + 0.260, "Causal Past",
                  color=BLUE_DARK, fontsize=17.0, fontweight='bold', ha='center', va='center', zorder=8)
    ax_plot1.text(cx, call_y + 0.110, "Events able to\ninfluence the\nobserver by time $t$",
                  color=DARK_SLATE, fontsize=15.0, ha='center', va='center', zorder=8, linespacing=1.22)

    # Pointer arrow from callout box into the shaded causal past interior
    ptr_start = (call_x + call_w, call_y + call_h * 0.50)
    ptr_target = (-0.05, call_y + call_h * 0.50)
    ax_plot1.annotate('', xy=ptr_target, xytext=ptr_start,
                      arrowprops=dict(arrowstyle='->', color=BLUE_DARK, lw=2.4), zorder=8)
    ax_plot1.plot(ptr_target[0], ptr_target[1], marker='o', markersize=5.0, color=BLUE_DARK, zorder=9)

    # Particle Horizon Dimension Arrow: ONE-SIDED RADIUS from central observer (x = 0) to horizon boundary (x = chi_max)
    bar_y = 0.175
    # Vertical drop reference lines at x = 0 and x = chi_max
    ax_plot1.plot([0.0, 0.0], [y_base, bar_y + 0.040], color=BLUE_DARK, lw=1.3, linestyle='--', zorder=6)
    ax_plot1.plot([chi_max, chi_max], [y_base, bar_y + 0.040], color=BLUE_DARK, lw=1.3, linestyle='--', zorder=6)

    # One-sided radius arrow from observer (x = 0) to right horizon boundary (x = chi_max)
    ax_plot1.annotate('', xy=(chi_max, bar_y), xytext=(0.0, bar_y),
                      arrowprops=dict(arrowstyle='->', color=BLUE_DARK, lw=2.4), zorder=7)
    # Tick mark at origin (x = 0)
    ax_plot1.plot([0.0, 0.0], [bar_y - 0.030, bar_y + 0.030], color=BLUE_DARK, lw=2.2, zorder=8)

    # Clean label \chi_{ph}(t) directly above the arrow, fully within the light cone
    ax_plot1.text(0.25, bar_y + 0.040, r"$\chi_{\mathrm{ph}}(t)$",
                  color=BLUE_DARK, fontsize=17.5, fontweight='bold', ha='center', va='bottom', zorder=9)

    # Outer region callout on the upper right
    ax_plot1.text(0.95, 0.75, "Signals have not reached\nthe observer by time $t$",
                  color=LIGHT_SLATE, fontsize=15.0, ha='center', va='center', style='italic')

    # Annotation for Past light cone (pointing to right curved boundary halfway between observer and base)
    y_plc = 0.54
    ratio_plc = (y_plc - y_base) / (t_obs - y_base)
    x_plc_target = chi_max * (1.0 - ratio_plc ** (1.0 / 1.80))
    x_plc_text = 0.68

    ax_plot1.text(x_plc_text, y_plc, "Past light cone",
                  color=BLUE_DARK, fontsize=15.5, fontweight='bold', ha='left', va='center', zorder=9)
    ax_plot1.annotate('', xy=(x_plc_target, y_plc), xytext=(x_plc_text - 0.04, y_plc),
                      arrowprops=dict(arrowstyle='->', color=BLUE_DARK, lw=1.6), zorder=9)

    # Axis Labels and Arrows
    ax_plot1.annotate('', xy=(-1.68, 1.05), xytext=(-1.68, y_base + 0.02),
                      arrowprops=dict(arrowstyle='->', color=DARK_SLATE, lw=1.8), zorder=8)
    ax_plot1.text(-1.72, 0.88, "Cosmic time  t",
                  color=DARK_SLATE, fontsize=16.0, fontweight='bold', rotation=90, ha='right', va='center')

    # Comoving distance axis arrow at right end of baseline
    ax_plot1.annotate('', xy=(1.60, y_base), xytext=(1.25, y_base),
                      arrowprops=dict(arrowstyle='->', color=DARK_SLATE, lw=1.6), zorder=8)
    # Comoving axis label: chi shifted slightly left of vertical line, perfectly aligned with (comoving)
    y_com = y_base + 0.032
    ax_plot1.text(0.72, y_com, r"$\chi$",
                  color=DARK_SLATE, fontsize=17.0, ha='center', va='baseline', zorder=9)
    ax_plot1.text(0.86, y_com, "(comoving)",
                  color=DARK_SLATE, fontsize=15.0, fontweight='bold', ha='left', va='baseline', zorder=9)

    # ---------------------------------------------------------
    # 6. Inner Plot 2: Scale Comparison Diagram (Panel B)
    # ---------------------------------------------------------
    # Position: x: 0.523 to 0.962, y: 0.200 to 0.812 (height 0.612)
    # Aspect ratio match: 6.732 / 6.585 = 1.022.
    # With xlim [-1.80, 1.80] (span 3.60), ylim is [-1.84, 1.84] (span 3.68).
    ax_plot2 = fig.add_axes([0.523, 0.200, 0.439, 0.612])
    ax_plot2.set_xlim(-1.80, 1.80)
    ax_plot2.set_ylim(-1.84, 1.84)
    ax_plot2.set_aspect('equal')
    ax_plot2.axis('off')

    # Central Hubble Disc (Radius R_H = 1.05, centered at (0, 0))
    r_h = 1.05
    hubble_circle = patches.Circle((0, 0), r_h, facecolor=TEAL_BG, edgecolor=TEAL,
                                   linewidth=2.4, linestyle='--', zorder=2)
    ax_plot2.add_patch(hubble_circle)

    # Origin crosshair at center (0, 0)
    ax_plot2.plot(0, 0, marker='+', markersize=12, color=TEAL_DARK, mew=2.2, zorder=6)

    # Radius arrow pointing from origin (0, 0) to circle boundary (r_h, 0) on the right
    ax_plot2.annotate('', xy=(r_h, 0), xytext=(0.0, 0),
                      arrowprops=dict(arrowstyle='->', color=TEAL_DARK, lw=2.6), zorder=6)

    # Clean, non-colliding typography directly above the radius vector with generous vertical gap
    ax_plot2.text(r_h * 0.48, 0.28, "Hubble radius",
                  color=TEAL_DARK, fontsize=16.5, fontweight='bold', ha='center', va='center', zorder=8)
    ax_plot2.text(r_h * 0.48, 0.13, r"$R_H(t) = \frac{c}{|H(t)|}$",
                  color=TEAL_DARK, fontsize=17.0, ha='center', va='center', zorder=8)

    # ---------------------------------------------------------
    # Small-Scale Perturbation Mode (Upper Region)
    # ---------------------------------------------------------
    y_sm_base = 0.72
    lam_sm = 0.28
    x_sm = np.linspace(-0.65, 0.65, 500)
    y_sm = y_sm_base + 0.035 * np.cos(2 * np.pi / lam_sm * x_sm)

    # Dotted baseline for small mode
    ax_plot2.plot([-0.70, 0.70], [y_sm_base, y_sm_base], color='#94a3b8', linewidth=1.0, linestyle=':', zorder=3)
    # Sine wave
    ax_plot2.plot(x_sm, y_sm, color=BLUE_DARK, linewidth=2.2, zorder=4)

    # Wavelength bracket for small mode: between adjacent crests (width lam_sm = 0.28)
    w_start, w_end = -lam_sm / 2, lam_sm / 2
    bracket_y_sm = y_sm_base + 0.090
    ax_plot2.annotate('', xy=(w_end, bracket_y_sm), xytext=(w_start, bracket_y_sm),
                      arrowprops=dict(arrowstyle='<->', color=BLUE_DARK, lw=1.8), zorder=5)
    # Label lambda_phys cleanly above bracket arrow with clear vertical gap
    ax_plot2.text(0, bracket_y_sm + 0.070, r"$\lambda_{\mathrm{phys}}$",
                  color=BLUE_DARK, fontsize=16.0, fontweight='bold', ha='center', va='bottom', zorder=6)

    # Card for Small-Scale Perturbation (Non-overlapping, spacious 3-line card)
    yc_sm = 1.54
    card_h = 0.46
    card_w = 3.15
    sm_card = FancyBboxPatch((-card_w / 2, yc_sm - card_h / 2), card_w, card_h,
                             boxstyle="round,pad=0.015,rounding_size=0.06",
                             facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.3, zorder=7)
    ax_plot2.add_patch(sm_card)
    ax_plot2.text(0, yc_sm + 0.130, r"Small-Scale Perturbation  $(\lambda_{\mathrm{phys}} \ll R_H)$",
                  color=BLUE_DARK, fontsize=16.5, fontweight='bold', ha='center', va='center', zorder=8)
    ax_plot2.text(0, yc_sm, "Newtonian approximation often adequate",
                  color=DARK_SLATE, fontsize=15.0, fontweight='bold', ha='center', va='center', zorder=8)
    ax_plot2.text(0, yc_sm - 0.130, "Weak fields and nonrelativistic matter",
                  color=SLATE, fontsize=14.5, ha='center', va='center', zorder=8)

    # ---------------------------------------------------------
    # Large-Scale Perturbation Mode (Lower Region)
    # ---------------------------------------------------------
    y_lg_base = -0.60
    lam_lg = 2.10
    # Spans well outside the circle: from x = -1.60 to x = 1.60
    x_lg = np.linspace(-1.60, 1.60, 400)
    y_lg = y_lg_base + 0.075 * np.cos(2 * np.pi / lam_lg * x_lg)

    # Dotted baseline for large mode
    ax_plot2.plot([-1.65, 1.65], [y_lg_base, y_lg_base], color='#94a3b8', linewidth=1.0, linestyle=':', zorder=3)
    # Wave line
    ax_plot2.plot(x_lg, y_lg, color=CORAL, linewidth=2.4, zorder=4)

    # Wavelength bracket across one full wavelength (dx = lam_lg)
    bracket_y_lg = y_lg_base - 0.150
    ax_plot2.annotate('', xy=(lam_lg / 2, bracket_y_lg), xytext=(-lam_lg / 2, bracket_y_lg),
                      arrowprops=dict(arrowstyle='<->', color=CORAL_DARK, lw=2.0), zorder=5)
    # Label lambda_phys cleanly below bracket arrow with clear vertical gap
    ax_plot2.text(0, bracket_y_lg - 0.075, r"$\lambda_{\mathrm{phys}}$",
                  color=CORAL_DARK, fontsize=16.0, fontweight='bold', ha='center', va='top', zorder=6)

    # Card for Large-Scale Perturbation (Non-overlapping, spacious 3-line card)
    yc_lg = -1.54
    lg_card = FancyBboxPatch((-card_w / 2, yc_lg - card_h / 2), card_w, card_h,
                             boxstyle="round,pad=0.015,rounding_size=0.06",
                             facecolor=CORAL_BG, edgecolor=CORAL_BORDER, linewidth=1.3, zorder=7)
    ax_plot2.add_patch(lg_card)
    ax_plot2.text(0, yc_lg + 0.130, r"Large-Scale Perturbation  $(\lambda_{\mathrm{phys}} \gtrsim R_H)$",
                  color=CORAL_DARK, fontsize=16.5, fontweight='bold', ha='center', va='center', zorder=8)
    ax_plot2.text(0, yc_lg, "Relativistic treatment becomes important",
                  color=DARK_SLATE, fontsize=15.0, fontweight='bold', ha='center', va='center', zorder=8)
    ax_plot2.text(0, yc_lg - 0.130, "Relativistic metric and gauge effects become important",
                  color=SLATE, fontsize=14.5, ha='center', va='center', zorder=8)

    # -------------------------------------------------------------------------
    # 7. Bottom Note Spanning Both Panels (y: 0.020 - 0.090, height ~92 px)
    # -------------------------------------------------------------------------
    ax_foot = fig.add_axes([0.025, 0.020, 0.950, 0.070])
    ax_foot.set_xlim(0, 1)
    ax_foot.set_ylim(0, 1)
    ax_foot.axis('off')

    foot_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                              boxstyle="round,pad=0.0,rounding_size=0.009",
                              mutation_aspect=(0.950 * fig_w) / (0.070 * fig_h),
                              clip_on=False,
                              facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_foot.add_patch(foot_box)

    ax_foot.text(0.50, 0.65,
                 "Particle horizon: causal reach.  Hubble radius: characteristic scale.",
                 color=DARK_SLATE, fontsize=17.0, fontweight='bold', ha='center', va='center')
    ax_foot.text(0.50, 0.28,
                 "Comparison with the Hubble radius helps assess the applicability of the Newtonian approximation.",
                 color=SLATE, fontsize=15.0, ha='center', va='center')

    plt.savefig(output_path, dpi=dpi, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"Figure saved to: {output_path}")


if __name__ == '__main__':
    create_figure()
