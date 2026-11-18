#!/usr/bin/env python3
r"""
Generate two-panel scientific figure:
"Gravitational Collapse: Two Descriptions of the Same Event"

Figure for Section "The Road to the Golden Age" of:
"The Golden Age of Black Hole Physics (1963–1974)"

Design & Scientific Specifications:
- Canvas: 1890 x 1050 px at 140 DPI (13.5 x 7.50 in), landscape, two equally sized panels
- Typography & hierarchy matching dark_energy_structure_growth.png and matter_transfer_function_power_spectrum.png:
  - 17.5 pt bold main title
  - 13.8 pt bold subtitle
  - 15.5 pt bold panel headers ("A   Proper time", "B   Schwarzschild coordinate time")
  - 14.5 pt bold axis titles
  - 14.0-14.2 pt bold primary labels
  - 13.5-13.8 pt secondary annotations and tick labels
- Physical model:
  - Exact Oppenheimer–Snyder (1939) homogeneous, spherically symmetric dust star
  - Released from rest at initial areal radius R_0 = 3.0 r_s
  - Conserved specific energy E = (1 - r_s / R_0)^{1/2} = (2/3)^{1/2}
  - Exact equations integrated numerically:
      (dR / d\tau)^2 = c^2 r_s (1/R - 1/R_0)
      dt / d\tau = E / (1 - r_s / R)
- Panel A (Proper time \tau):
  - Horizon crossing R = r_s at finite proper time \tau_h \approx 7.41 (r_s/c)
  - Small blue marker at horizon crossing (\tau_h, r_s)
  - Continues below r_s to R = 0
  - Annotation: "Curvature singularity at R = 0 reached at finite \tau_0 \approx 8.2 (r_s/c)"
    with clean thin leader line pointing to the endpoint
- Panel B (Schwarzschild coordinate time t):
  - Upper area: initial radius R_0 = 3.0 r_s
  - Middle-right: "Asymptotic approach: t \to \infty as R \to r_s^+" with arrow to trajectory
  - Lower-right: "Schwarzschild coordinate singularity: dt/d\tau \to +\infty as R \to r_s^+"
    placed below the dashed horizon line
  - Schwarzschild radius label placed below the dashed horizon line on the left
  - Horizontal axis spanning 0 to 20 r_s/c
"""

from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
from scipy import integrate

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "oppenheimer_snyder_collapse.png"


def compute_oppenheimer_snyder_trajectories(y0=3.0, n_tau=800, n_t=800):
    r"""
    Compute exact Oppenheimer-Snyder collapse trajectories for dimensionless radius
    y = R / r_s:
      1. Panel A: Proper time tau (in units of r_s / c) from y0 down to 0
      2. Panel B: Coordinate time t (in units of r_s / c) from y0 down to 1 + epsilon
    """
    E = np.sqrt(1.0 - 1.0 / y0)

    # 1. Panel A: Proper time trajectory via cycloid parameter eta in [0, pi]
    eta = np.linspace(0.0, np.pi, n_tau)
    y_tau = 0.5 * y0 * (1.0 + np.cos(eta))
    tau = 0.5 * (y0 ** 1.5) * (eta + np.sin(eta))

    # Horizon crossing at y = 1.0:
    cos_eta_h = np.clip(2.0 / y0 - 1.0, -1.0, 1.0)
    eta_h = np.arccos(cos_eta_h)
    tau_h = 0.5 * (y0 ** 1.5) * (eta_h + np.sin(eta_h))
    tau_sing = 0.5 * (y0 ** 1.5) * np.pi

    # 2. Panel B: Schwarzschild coordinate time t
    # Substitute u = sqrt(y0 - y) => dy = -2u du:
    # dt/du = 2 * E * y^{1.5} * sqrt(y0) / (y - 1) where y = y0 - u^2
    def integrand_u(u):
        y_val = y0 - u ** 2
        return 2.0 * E * (y_val ** 1.5) * np.sqrt(y0) / (y_val - 1.0)

    # Resolve close to y = 1 down to delta = 1e-5 so t reaches ~ 20 r_s / c
    # Note: y_t is strictly greater than 1.0 everywhere (never artificially clamped to 1.0)
    delta_y = np.logspace(np.log10(1e-5), np.log10(y0 - 1.0001), n_t)
    y_t = np.sort(np.concatenate([[y0], 1.0 + delta_y]))
    u_max = np.sqrt(np.maximum(0.0, y0 - y_t))

    t = np.zeros_like(y_t)
    for i, u_m in enumerate(u_max):
        if u_m > 0:
            val, _ = integrate.quad(integrand_u, 0, u_m, limit=150)
            t[i] = val
        else:
            t[i] = 0.0

    return tau, y_tau, tau_h, tau_sing, t, y_t


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure mathtext and typography (matching editorial standards)
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    # Canvas: 1890 x 1050 px at 140 DPI (13.5 x 7.50 in), landscape
    fig_w, fig_h = 13.5, 7.50
    dpi = 140
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'          # Hero headings, axis titles
    DARK_SLATE = '#1e293b'    # Primary text & labels
    SLATE = '#475569'         # Secondary text
    AXIS_COLOR = '#334155'    # Axis spines and arrowheads
    BORDER_COLOR = '#cbd5e1'  # Card borders
    CARD_BG = '#f8fafc'       # Header background

    # User Specs:
    # Collapse trajectory: Dark blue, solid
    BLUE_LINE = '#1d4ed8'     # Dark vibrant blue
    BLUE_DARK = '#1e3a8a'     # Deep navy blue for markers/headings
    BLUE_BG = '#eff6ff'       # Light blue badge background
    BLUE_BORDER = '#bfdbfe'

    # Schwarzschild radius: Muted orange, dashed
    ORANGE_RS = '#d97706'     # Muted orange
    ORANGE_DARK = '#b45309'
    ORANGE_BG = '#fffbeb'
    ORANGE_BORDER = '#fde68a'

    # Initial radius R0 & grid: Thin grey
    GREY_R0 = '#94a3b8'

    # -------------------------------------------------------------------------
    # 1. Top Header Banner
    # -------------------------------------------------------------------------
    ax_head = fig.add_axes([0.025, 0.902, 0.950, 0.076])
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)
    ax_head.axis('off')

    title_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.009",
                               mutation_aspect=(0.950 * fig_w) / (0.076 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_head.add_patch(title_box)
    ax_head.text(0.50, 0.65, "GRAVITATIONAL COLLAPSE: TWO DESCRIPTIONS OF THE SAME EVENT",
                 color=NAVY, fontsize=17.5, fontweight='bold', ha='center', va='center')
    ax_head.text(0.50, 0.25,
                 "Oppenheimer–Snyder collapse in proper time and Schwarzschild coordinate time",
                 color=SLATE, fontsize=13.8, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 2. Outer Card Frames & Panel Header Badges (Panel A & Panel B)
    # -------------------------------------------------------------------------
    card_bottom = 0.034
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
    hdr_a = FancyBboxPatch((0.026, 0.922), 0.948, 0.056,
                           boxstyle="round,pad=0.0,rounding_size=0.012",
                           mutation_aspect=(card_w * fig_w) / (card_height * fig_h),
                           facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.3)
    ax_card_a.add_patch(hdr_a)
    ax_card_a.text(0.50, 0.950,
                   r"A   Proper time $\tau$ of collapsing matter",
                   color=BLUE_DARK, fontsize=15.5, fontweight='bold', ha='center', va='center')

    # Right Card Frame (Panel B)
    ax_card_b = fig.add_axes([right_x, card_bottom, card_w, card_height], zorder=0)
    ax_card_b.set_xlim(0, 1)
    ax_card_b.set_ylim(0, 1)
    ax_card_b.axis('off')
    ax_card_b.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0,
                                  facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4))
    hdr_b = FancyBboxPatch((0.026, 0.922), 0.948, 0.056,
                           boxstyle="round,pad=0.0,rounding_size=0.012",
                           mutation_aspect=(card_w * fig_w) / (card_height * fig_h),
                           facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.3)
    ax_card_b.add_patch(hdr_b)
    ax_card_b.text(0.50, 0.950,
                   r"B   Schwarzschild coordinate time $t$",
                   color=NAVY, fontsize=15.5, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 3. Physics Calculations (Oppenheimer–Snyder with R_0 = 3.0 r_s)
    # -------------------------------------------------------------------------
    y0 = 3.0
    tau, y_tau, tau_h, tau_sing, t, y_t = compute_oppenheimer_snyder_trajectories(y0=y0)

    # Identical plotting geometry inside each card
    plot_rel_left = 0.088
    plot_w = 0.352
    plot_bottom = 0.134
    plot_h = 0.596

    ax_a = fig.add_axes([left_x + plot_rel_left, plot_bottom, plot_w, plot_h], zorder=2)
    ax_b = fig.add_axes([right_x + plot_rel_left, plot_bottom, plot_w, plot_h], zorder=2)

    # Shared vertical limits
    y_min, y_max = 0.0, 3.45

    for ax_curr in [ax_a, ax_b]:
        ax_curr.set_facecolor('#ffffff')
        ax_curr.set_ylim(y_min, y_max)
        ax_curr.spines['top'].set_visible(False)
        ax_curr.spines['right'].set_visible(False)
        ax_curr.spines['left'].set_edgecolor(AXIS_COLOR)
        ax_curr.spines['left'].set_linewidth(1.8)
        ax_curr.spines['bottom'].set_edgecolor(AXIS_COLOR)
        ax_curr.spines['bottom'].set_linewidth(1.8)
        ax_curr.tick_params(axis='x', pad=7, length=6, width=1.5, colors=AXIS_COLOR)
        ax_curr.tick_params(axis='y', pad=7, length=6, width=1.5, colors=AXIS_COLOR)

        # Arrowheads at tips
        ax_curr.plot(1.0, 0.0, ">", transform=ax_curr.transAxes, color=AXIS_COLOR,
                     markersize=9, clip_on=False, zorder=10)
        ax_curr.plot(0.0, 1.0, "^", transform=ax_curr.transAxes, color=AXIS_COLOR,
                     markersize=9, clip_on=False, zorder=10)

        # Vertical axis ticks: 0, r_s, 2 r_s, R_0 = 3 r_s
        ax_curr.set_yticks([0.0, 1.0, 2.0, 3.0])
        ax_curr.set_yticklabels([
            r"$0$",
            r"$r_s$",
            r"$2\,r_s$",
            r"$R_0$",
        ], fontsize=13.5, fontweight='bold')

    # Y-tick label colors
    for tick_label, col in zip(ax_a.get_yticklabels(), [DARK_SLATE, ORANGE_DARK, DARK_SLATE, DARK_SLATE]):
        tick_label.set_color(col)
    for tick_label, col in zip(ax_b.get_yticklabels(), [DARK_SLATE, ORANGE_DARK, DARK_SLATE, DARK_SLATE]):
        tick_label.set_color(col)

    # Vertical axis titles on both panels ("R" alone on both axes, since Panel A annotation defines it)
    ax_a.set_ylabel(r"$R$", fontsize=15.5, fontweight='bold', color=NAVY, labelpad=12, rotation=0, va='center')
    ax_b.set_ylabel(r"$R$", fontsize=15.5, fontweight='bold', color=NAVY, labelpad=12, rotation=0, va='center')

    # Self-contained annotation above the graph in Panel A (centered in Panel A card) defining R in terms of A
    ax_card_a.text(0.50, 0.880,
                   r"Areal radius:  $R = \sqrt{\frac{A}{4\pi}}$,  where $A$ is the stellar surface area",
                   fontsize=12.6, fontweight='bold', color=DARK_SLATE,
                   ha='center', va='center', zorder=10)

    # =========================================================================
    # PANEL A: PROPER TIME (\tau)
    # =========================================================================
    tau_max = 9.20
    ax_a.set_xlim(0.0, tau_max)

    # Initial radius R_0: Thin grey dotted line
    ax_a.axhline(y0, color=GREY_R0, linestyle=':', linewidth=1.5, zorder=1)
    ax_a.text(0.20, y0 + 0.08, r"Initial radius $R_0 = 3.0\,r_s$",
              fontsize=13.5, color=SLATE, ha='left', va='bottom', zorder=5)

    # Schwarzschild radius r_s: Muted orange, dashed
    ax_a.axhline(1.0, color=ORANGE_RS, linestyle='--', linewidth=2.4, zorder=2)
    # Place label cleanly below dashed line
    ax_a.text(0.20, 0.88, r"Schwarzschild radius $R = r_s$",
              fontsize=13.8, fontweight='bold', color=ORANGE_DARK, ha='left', va='top', zorder=5)

    # Dark blue solid collapse trajectory
    ax_a.plot(tau, y_tau, color=BLUE_LINE, linewidth=4.2, solid_capstyle='round', zorder=4)

    # Small blue marker at horizon crossing (\tau_h, 1.0)
    ax_a.scatter([tau_h], [1.0], s=140, color=BLUE_LINE, edgecolor='#ffffff', linewidth=2.2, zorder=8)

    # Dotted drop line to x-axis at \tau_h
    ax_a.plot([tau_h, tau_h], [0.0, 1.0], color=BLUE_LINE, linestyle=':', linewidth=1.6, alpha=0.80, zorder=3)

    # Small marker at singularity (\tau_sing, 0.0)
    ax_a.scatter([tau_sing], [0.0], s=120, color=DARK_SLATE, edgecolor='#ffffff', linewidth=2.0, zorder=8)

    # Horizon crossing callout (upper right of Panel A)
    ax_a.annotate(
        "Crossing at finite proper time\n" + r"$\tau_h \approx 7.4\,(r_s/c)$",
        xy=(tau_h, 1.0), xytext=(6.50, 2.25),
        arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.8, shrinkA=2, shrinkB=6),
        fontsize=13.6, fontweight='bold', color=BLUE_DARK, ha='center', va='bottom',
        bbox=dict(boxstyle='round,pad=0.32', facecolor='#ffffff', edgecolor=BLUE_BORDER, linewidth=1.2),
        zorder=7
    )

    # Singularity label in lower-left: "Curvature singularity at R = 0" with thin leader line
    ax_a.annotate(
        r"Curvature singularity at $R = 0$" + "\n" + r"reached at finite $\tau_0 \approx 8.2\,(r_s/c)$",
        xy=(tau_sing, 0.0), xytext=(3.30, 0.42),
        arrowprops=dict(arrowstyle="->", color=DARK_SLATE, lw=1.5, shrinkA=2, shrinkB=6),
        fontsize=13.2, fontweight='bold', color=DARK_SLATE, ha='center', va='center',
        linespacing=1.26,
        bbox=dict(boxstyle='round,pad=0.30', facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.2),
        zorder=7
    )

    # Panel A X-axis ticks & labels
    ax_a.set_xticks([0.0, 2.0, 4.0, 6.0, tau_h])
    ax_a.set_xticklabels([
        r"$0$",
        r"$2$",
        r"$4$",
        r"$6$",
        r"$\tau_h$",
    ], fontsize=13.5, fontweight='bold')
    ax_a.get_xticklabels()[4].set_color(BLUE_DARK)

    ax_a.set_xlabel(r"Proper time $\tau\ [r_s/c]$", fontsize=14.5, fontweight='bold', color=NAVY, labelpad=8)

    # =========================================================================
    # PANEL B: SCHWARZSCHILD TIME (t)
    # =========================================================================
    t_max = 20.0
    ax_b.set_xlim(0.0, t_max)

    # 1. Upper area: Initial radius R_0: Thin grey dotted line only
    ax_b.axhline(y0, color=GREY_R0, linestyle=':', linewidth=1.5, zorder=1)
    ax_b.text(0.50, y0 + 0.08, r"Initial radius $R_0 = 3.0\,r_s$",
              fontsize=13.5, color=SLATE, ha='left', va='bottom', zorder=5)

    # 2. Schwarzschild radius r_s: Muted orange, dashed
    ax_b.axhline(1.0, color=ORANGE_RS, linestyle='--', linewidth=2.4, zorder=2)
    # Placed cleanly below the dashed line on the left side
    ax_b.text(0.50, 0.88, r"Schwarzschild radius $R = r_s$",
              fontsize=13.8, fontweight='bold', color=ORANGE_DARK, ha='left', va='top', zorder=5)

    # 3. Collapse trajectory: Strictly calculated numerically (y_t > 1.0 everywhere)
    mask_t = t <= t_max
    ax_b.plot(t[mask_t], y_t[mask_t], color=BLUE_LINE, linewidth=4.2, solid_capstyle='round', zorder=4)

    # Asymptotic arrow at the right end of the trajectory along R -> rs+ communicating continued coordinate time
    ax_b.annotate("",
                  xy=(t_max - 0.35, 1.012), xytext=(t_max - 2.2, 1.012),
                  arrowprops=dict(arrowstyle="->", color=BLUE_LINE, lw=2.6, shrinkA=0, shrinkB=0),
                  zorder=7)

    # 4. Middle-right: "Asymptotic approach" callout box with arrow pointing to the blue trajectory near R = r_s
    ax_b.annotate(
        "Asymptotic approach:\n" + r"$t \to \infty$ as $R \to r_s^+$",
        xy=(16.8, 1.04), xytext=(15.0, 1.85),
        arrowprops=dict(arrowstyle="->", color=ORANGE_DARK, lw=1.8, shrinkA=2, shrinkB=6),
        fontsize=13.6, fontweight='bold', color=ORANGE_DARK, ha='center', va='bottom',
        bbox=dict(boxstyle='round,pad=0.30', facecolor='#ffffff', edgecolor=ORANGE_BORDER, linewidth=1.2),
        zorder=7
    )

    # 5. Lower area: Schwarzschild coordinate singularity box relocated below the horizon label
    ax_b.text(11.2, 0.36,
              "Schwarzschild coordinate singularity\n"
              + r"$\dfrac{dt}{d\tau} \longrightarrow +\infty\quad\mathrm{as}\quad R \longrightarrow r_s^+$",
              fontsize=13.4, color=DARK_SLATE, ha='center', va='center',
              linespacing=1.75,
              bbox=dict(boxstyle='round,pad=0.36', facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.2),
              zorder=6)

    # Panel B X-axis ticks & labels
    ax_b.set_xticks([0.0, 5.0, 10.0, 15.0, 20.0])
    ax_b.set_xticklabels([
        r"$0$",
        r"$5$",
        r"$10$",
        r"$15$",
        r"$20$",
    ], fontsize=13.5, fontweight='bold')

    ax_b.set_xlabel(r"Schwarzschild coordinate time $t\ [r_s/c]$", fontsize=14.5, fontweight='bold', color=NAVY, labelpad=8)

    # Save figure
    fig.savefig(output_path, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    print(f"[OK] Generated {output_path} ({fig_w * dpi:.0f} x {fig_h * dpi:.0f} px)")



if __name__ == "__main__":
    create_figure()
