#!/usr/bin/env python3
r"""
Generate infographic for Article 2:
"From the Simple Pendulum to the Double Pendulum"

Two-panel schematic comparison matching the publication standards of:
- the_road_to_modern_dynamics / generate_pendulum_coordinate_transition.py
- the_road_to_modern_dynamics_2 / generate_three_body_solutions_crtbp.py

Panel A: Classical Simple Pendulum (1 Degree of Freedom)
- Angle theta, length L, gravity g, weight mg; no forcing or damping.
- Equation: \ddot{\theta} + \omega_0^2 \sin\theta = 0, \quad \omega_0 = \sqrt{g/L}
- Conservative system with constant mechanical energy.
- Constant-energy trajectories in 2D phase space.

Panel B: Conservative Double Pendulum (2 Degrees of Freedom)
- Masses m_1, m_2; lengths L_1, L_2; gravity g, weights m_1 g, m_2 g; no forcing or damping.
- Hinged two-link planar pendulum with angles \theta_1 and \theta_2.
- Equation: \frac{d}{dt}\left(\frac{\partial\mathcal{L}}{\partial\dot{\theta}_i}\right) - \frac{\partial\mathcal{L}}{\partial\theta_i} = 0, \quad i = 1, 2
- Total mechanical energy is conserved on 3D energy surfaces.
- Coupled nonlinear motion in 4D phase space.

Strict minimum font size >= 14pt across all text elements.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "simple_vs_double_pendulum.png"
ALT_OUT_1 = SCRIPT_DIR.parent / "images" / "conservative_vs_forced_double_pendulum.png"


def draw_3d_sphere(ax, x, y, radius, base_color='#2563eb', highlight_color='#ffffff', zorder=10):
    """Draw a 2D circle with radial shading to mimic a rich 3D sphere."""
    shadow = patches.Circle((x, y), radius, facecolor=base_color, edgecolor='#0f172a',
                            linewidth=1.4, alpha=0.95, zorder=zorder)
    ax.add_patch(shadow)

    n_layers = 12
    hx = x - 0.32 * radius
    hy = y + 0.32 * radius

    for i in range(n_layers):
        r_i = radius * (1.0 - i / n_layers * 0.85)
        xi = hx + (x - hx) * (i / n_layers) * 0.4
        yi = hy + (y - hy) * (i / n_layers) * 0.4
        alpha_i = 0.05 + 0.07 * (i / n_layers)**1.5
        layer = patches.Circle((xi, yi), r_i, facecolor=highlight_color, edgecolor='none',
                               alpha=alpha_i, zorder=zorder + 1)
        ax.add_patch(layer)


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Matplotlib typography and styling
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'axes.edgecolor': '#94a3b8',
        'axes.linewidth': 1.2,
    })

    # Dimensions: 17.0 x 8.8 inches at 240 DPI
    fig_w = 17.0
    fig_h = 8.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'          # Deep slate navy for main headings
    DARK_SLATE = '#1e293b'    # Body text & subheaders
    SLATE = '#334155'         # Secondary text
    LIGHT_SLATE = '#94a3b8'   # Reference lines & muted text
    BORDER_CARD = '#cbd5e1'   # Card border
    BG_CARD = '#f8fafc'       # Light background for panels
    BG_BOX = '#ffffff'        # Pure white for callout cards

    BLUE = '#2563eb'          # Primary blue accent
    BLUE_LIGHT = '#eff6ff'    # Soft blue tint
    BLUE_BORDER = '#93c5fd'   # Blue border

    PURPLE = '#7c3aed'        # Weight accent

    # -------------------------------------------------------------
    # Main Header & Context Banner (>= 15.0 pt)
    # -------------------------------------------------------------
    fig.text(0.5, 0.962,
             "From the Simple Pendulum to the Double Pendulum",
             fontsize=22.0, weight='bold', color=NAVY, ha='center', va='center')

    fig.text(0.5, 0.925,
             "Comparison of one- and two-degree-of-freedom conservative Hamiltonian systems",
             fontsize=15.0, weight='normal', color=SLATE, ha='center', va='center')

    # -------------------------------------------------------------
    # Panel Layout Setup
    # -------------------------------------------------------------
    w_card = 0.442
    h_card = 0.835
    y_card = 0.045
    x1 = 0.040
    x2 = 0.518

    ax1 = fig.add_axes([x1, y_card, w_card, h_card])
    ax2 = fig.add_axes([x2, y_card, w_card, h_card])

    for ax in (ax1, ax2):
        ax.set_facecolor(BG_CARD)
        ax.axis('off')
        ax.set_xlim(-1.64, 1.64)
        ax.set_ylim(-1.70, 1.36)

        # Outer card frame
        card_rect = patches.FancyBboxPatch((-1.59, -1.64), 3.18, 2.94,
                                           boxstyle="round,pad=0.03,rounding_size=0.14",
                                           facecolor=BG_CARD, edgecolor=BORDER_CARD,
                                           lw=1.5, zorder=0)
        ax.add_patch(card_rect)

    # Shared ceiling mount renderer
    def draw_ceiling_mount(ax, py0=0.67):
        ax.plot([-0.38, 0.38], [py0, py0], color=DARK_SLATE, lw=2.6, zorder=3)
        for hx in np.linspace(-0.33, 0.33, 8):
            ax.plot([hx, hx + 0.06], [py0, py0 + 0.08], color=DARK_SLATE, lw=1.6, zorder=3)
        pivot_outer = patches.Circle((0.0, py0), 0.048, facecolor='#e2e8f0', edgecolor=DARK_SLATE, lw=1.8, zorder=12)
        ax.add_patch(pivot_outer)
        pivot_pin = patches.Circle((0.0, py0), 0.018, facecolor=NAVY, edgecolor='none', zorder=13)
        ax.add_patch(pivot_pin)

    px0 = 0.0
    py0 = 0.67

    # =============================================================
    # PANEL A: CLASSICAL SIMPLE PENDULUM (1 DEGREE OF FREEDOM)
    # =============================================================
    theta_deg = 32.0
    theta_rad = np.radians(theta_deg)
    L_len = 1.26

    # Bob position
    bx = px0 + L_len * np.sin(theta_rad)
    by = py0 - L_len * np.cos(theta_rad)

    # Title
    ax1.text(0, 1.23, "A. Simple Pendulum",
             fontsize=18.5, weight='bold', color=NAVY, ha='center', va='center')

    # Subtitle pill
    pill1 = patches.FancyBboxPatch((-1.51, 0.885), 3.02, 0.19,
                                   boxstyle="round,pad=0.02,rounding_size=0.06",
                                   facecolor=BLUE_LIGHT, edgecolor=BLUE_BORDER, lw=1.2, zorder=2)
    ax1.add_patch(pill1)
    ax1.text(0, 0.98,
             r"Angle $\theta$, length $L$, gravity $g$; no forcing or damping",
             fontsize=14.2, weight='bold', color=DARK_SLATE, ha='center', va='center')

    draw_ceiling_mount(ax1, py0)

    # Vertical reference line (theta = 0)
    ax1.plot([px0, px0], [py0, -0.12], '--', color=LIGHT_SLATE, lw=1.8, zorder=1)
    ax1.text(-0.08, 0.12, r"Vertical" "\n" r"$\theta = 0$",
             fontsize=14.0, color=SLATE, ha='right', va='center', linespacing=1.25)

    # Angular displacement arc (theta)
    r_arc = 0.48
    arc_th = np.linspace(-np.pi/2, -np.pi/2 + theta_rad, 40)
    ax1.plot(px0 + r_arc * np.cos(arc_th), py0 + r_arc * np.sin(arc_th), color=BLUE, lw=2.4, zorder=4)

    th_tip = -np.pi/2 + theta_rad
    ax1.annotate('', xy=(px0 + r_arc * np.cos(th_tip), py0 + r_arc * np.sin(th_tip)),
                 xytext=(px0 + r_arc * np.cos(th_tip - 0.07), py0 + r_arc * np.sin(th_tip - 0.07)),
                 arrowprops=dict(arrowstyle="->", color=BLUE, lw=2.4, mutation_scale=15), zorder=4)

    # Theta label badge
    ax1.text(0.44, 0.33, r"Angle $\theta$", fontsize=15.5, weight='bold', color=BLUE, va='center',
             bbox=dict(boxstyle="round,pad=0.22", facecolor='#ffffff', edgecolor=BLUE_BORDER, lw=1.0), zorder=5)

    # Trajectory arc (dashed swing path)
    swing_angles = np.linspace(-np.radians(45), np.radians(50), 100)
    ax1.plot(px0 + L_len * np.sin(swing_angles), py0 - L_len * np.cos(swing_angles),
             '--', color='#cbd5e1', lw=1.8, zorder=1)

    # Rigid rod
    ax1.plot([px0, bx], [py0, by], color=DARK_SLATE, lw=3.6, zorder=3)
    ax1.text(0.46, 0.06, r"Length $L$", fontsize=15.0, weight='bold', color=DARK_SLATE, zorder=5)

    # Bob
    draw_3d_sphere(ax1, bx, by, radius=0.125, base_color=BLUE, highlight_color='#ffffff', zorder=8)
    ax1.text(bx, by, "$m$", fontsize=15.0, weight='bold', color='#ffffff', ha='center', va='center', zorder=12)

    # Weight vector mg
    g_len = 0.34
    ax1.annotate('', xy=(bx, by - g_len), xytext=(bx, by),
                 arrowprops=dict(arrowstyle="->", color=PURPLE, lw=2.8, mutation_scale=18), zorder=9)
    ax1.text(bx + 0.14, by - g_len * 0.55, r"Weight $mg$",
             fontsize=15.0, weight='bold', color=PURPLE, va='center', zorder=10)

    # Bottom Summary Box: Panel A
    rect_box1 = patches.FancyBboxPatch((-1.44, -1.61), 2.88, 0.65,
                                       boxstyle="round,pad=0.03,rounding_size=0.08",
                                       facecolor=BG_BOX, edgecolor=BLUE_BORDER, lw=1.4, zorder=3)
    ax1.add_patch(rect_box1)

    ax1.text(0, -1.04, r"Equation of Motion (Conservative)",
             fontsize=16.0, weight='bold', color=NAVY, ha='center', va='center', zorder=4)

    ax1.text(0, -1.175, r"$\ddot{\theta} + \omega_0^2 \sin\theta = 0, \quad \omega_0 = \sqrt{g/L}$",
             fontsize=16.0, weight='bold', color=BLUE, ha='center', va='center', zorder=4)

    ax1.text(0, -1.305, "Total mechanical energy is conserved",
             fontsize=14.2, weight='normal', color=DARK_SLATE, ha='center', va='center', zorder=4)

    # Highlighted phase-space dimension pill
    pill_ps1 = patches.FancyBboxPatch((-1.32, -1.575), 2.64, 0.13,
                                      boxstyle="round,pad=0.015,rounding_size=0.04",
                                      facecolor=BLUE_LIGHT, edgecolor=BLUE_BORDER, lw=1.1, zorder=3.5)
    ax1.add_patch(pill_ps1)

    ax1.text(0, -1.51, "2D Phase Space  •  Motion on 1D energy curves",
             fontsize=14.5, weight='bold', color=NAVY, ha='center', va='center', zorder=4)

    # =============================================================
    # PANEL B: CONSERVATIVE DOUBLE PENDULUM (2 DEGREES OF FREEDOM)
    # =============================================================
    ax2.text(0, 1.23, "B. Conservative Double Pendulum",
             fontsize=18.5, weight='bold', color=NAVY, ha='center', va='center')

    pill2 = patches.FancyBboxPatch((-1.51, 0.885), 3.02, 0.19,
                                   boxstyle="round,pad=0.02,rounding_size=0.06",
                                   facecolor=BLUE_LIGHT, edgecolor=BLUE_BORDER, lw=1.2, zorder=2)
    ax2.add_patch(pill2)
    ax2.text(0, 0.98,
             r"Masses $m_1, m_2$; lengths $L_1, L_2$; gravity $g$; no forcing or damping",
             fontsize=14.2, weight='bold', color=DARK_SLATE, ha='center', va='center')

    draw_ceiling_mount(ax2, py0)

    # Double Pendulum Geometry
    L1 = 0.78
    th1_deg = 30.0
    th1_rad = np.radians(th1_deg)
    b1x = px0 + L1 * np.sin(th1_rad)
    b1y = py0 - L1 * np.cos(th1_rad)

    L2 = 0.72
    th2_deg = 46.0
    th2_rad = np.radians(th2_deg)
    b2x = b1x + L2 * np.sin(th2_rad)
    b2y = b1y - L2 * np.cos(th2_rad)

    # 1. Vertical reference line for Link 1 (theta1 = 0)
    ax2.plot([px0, px0], [py0, 0.12], '--', color=LIGHT_SLATE, lw=1.8, zorder=1)
    ax2.text(-0.08, 0.38, r"Vertical" "\n" r"$\theta_1 = 0$",
             fontsize=14.0, color=SLATE, ha='right', va='center', linespacing=1.25)

    # Angle theta1 arc
    r_arc1 = 0.44
    arc_th1 = np.linspace(-np.pi/2, -np.pi/2 + th1_rad, 35)
    ax2.plot(px0 + r_arc1 * np.cos(arc_th1), py0 + r_arc1 * np.sin(arc_th1), color=BLUE, lw=2.4, zorder=4)

    th1_tip = -np.pi/2 + th1_rad
    ax2.annotate('', xy=(px0 + r_arc1 * np.cos(th1_tip), py0 + r_arc1 * np.sin(th1_tip)),
                 xytext=(px0 + r_arc1 * np.cos(th1_tip - 0.08), py0 + r_arc1 * np.sin(th1_tip - 0.08)),
                 arrowprops=dict(arrowstyle="->", color=BLUE, lw=2.4, mutation_scale=15), zorder=4)

    # Angle theta1 badge
    ax2.text(0.38, 0.52, r"Angle $\theta_1$", fontsize=15.0, weight='bold', color=BLUE, va='center',
             bbox=dict(boxstyle="round,pad=0.20", facecolor='#ffffff', edgecolor=BLUE_BORDER, lw=1.0), zorder=5)

    # Rod 1
    ax2.plot([px0, b1x], [py0, b1y], color=DARK_SLATE, lw=3.6, zorder=3)
    ax2.text(0.38, 0.24, r"Length $L_1$", fontsize=14.5, weight='bold', color=DARK_SLATE, zorder=5)

    # 2. Bob 1 (m1)
    draw_3d_sphere(ax2, b1x, b1y, radius=0.12, base_color=BLUE, highlight_color='#ffffff', zorder=8)
    ax2.text(b1x, b1y, "$m_1$", fontsize=14.5, weight='bold', color='#ffffff', ha='center', va='center', zorder=12)

    # Vertical reference line for Link 2 (theta2 = 0) originating from Bob 1
    ax2.plot([b1x, b1x], [b1y - 0.12, b1y - 0.48], '--', color=LIGHT_SLATE, lw=1.8, zorder=1)
    ax2.text(b1x - 0.08, b1y - 0.42, r"Vertical" "\n" r"$\theta_2 = 0$",
             fontsize=14.0, color=SLATE, ha='right', va='center', linespacing=1.2)

    # Weight vector m1 g (placed to the left of Bob 1)
    g1_len = 0.26
    ax2.annotate('', xy=(b1x, b1y - 0.12 - g1_len), xytext=(b1x, b1y - 0.12),
                 arrowprops=dict(arrowstyle="->", color=PURPLE, lw=2.8, mutation_scale=17), zorder=9)
    ax2.text(b1x - 0.10, b1y - 0.20, r"Weight $m_1 g$",
             fontsize=14.0, weight='bold', color=PURPLE, ha='right', va='center', zorder=10)

    # Angle theta2 arc (centered at Bob 1)
    r_arc2 = 0.28
    arc_th2 = np.linspace(-np.pi/2, -np.pi/2 + th2_rad, 35)
    ax2.plot(b1x + r_arc2 * np.cos(arc_th2), b1y + r_arc2 * np.sin(arc_th2), color=BLUE, lw=2.4, zorder=4)

    th2_tip = -np.pi/2 + th2_rad
    ax2.annotate('', xy=(b1x + r_arc2 * np.cos(th2_tip), b1y + r_arc2 * np.sin(th2_tip)),
                 xytext=(b1x + r_arc2 * np.cos(th2_tip - 0.08), b1y + r_arc2 * np.sin(th2_tip - 0.08)),
                 arrowprops=dict(arrowstyle="->", color=BLUE, lw=2.4, mutation_scale=15), zorder=4)

    # Angle theta2 badge placed cleanly to the right of Rod 2
    ax2.text(0.70, -0.10, r"Angle $\theta_2$", fontsize=15.0, weight='bold', color=BLUE, va='center',
             bbox=dict(boxstyle="round,pad=0.20", facecolor='#ffffff', edgecolor=BLUE_BORDER, lw=1.0), zorder=5)

    # Rod 2
    ax2.plot([b1x, b2x], [b1y, b2y], color=DARK_SLATE, lw=3.6, zorder=3)
    ax2.text(0.86, -0.28, r"Length $L_2$", fontsize=14.5, weight='bold', color=DARK_SLATE, zorder=5)

    # 3. Bob 2 (m2)
    draw_3d_sphere(ax2, b2x, b2y, radius=0.12, base_color=BLUE, highlight_color='#ffffff', zorder=8)
    ax2.text(b2x, b2y, "$m_2$", fontsize=14.5, weight='bold', color='#ffffff', ha='center', va='center', zorder=12)

    # Weight vector m2 g
    g2_len = 0.20
    ax2.annotate('', xy=(b2x, b2y - 0.12 - g2_len), xytext=(b2x, b2y - 0.12),
                 arrowprops=dict(arrowstyle="->", color=PURPLE, lw=2.8, mutation_scale=17), zorder=9)
    ax2.text(b2x + 0.14, b2y - 0.12 - g2_len * 0.55, r"Weight $m_2 g$",
             fontsize=14.0, weight='bold', color=PURPLE, va='center', zorder=10)

    # Subtle swing trajectories (dashed path for Bob 2)
    sw2 = np.linspace(np.radians(25), np.radians(65), 60)
    ax2.plot(b1x + L2 * np.sin(sw2), b1y - L2 * np.cos(sw2), '--', color='#cbd5e1', lw=1.8, zorder=1)

    # Bottom Summary Box: Conservative Double Pendulum
    rect_box2 = patches.FancyBboxPatch((-1.44, -1.61), 2.88, 0.65,
                                       boxstyle="round,pad=0.03,rounding_size=0.08",
                                       facecolor=BG_BOX, edgecolor=BLUE_BORDER, lw=1.4, zorder=3)
    ax2.add_patch(rect_box2)

    ax2.text(0, -1.04, r"Equations of Motion (Conservative)",
             fontsize=16.0, weight='bold', color=NAVY, ha='center', va='center', zorder=4)

    ax2.text(0, -1.175,
             r"$\frac{d}{dt}\left(\frac{\partial\mathcal{L}}{\partial\dot{\theta}_i}\right) - \frac{\partial\mathcal{L}}{\partial\theta_i} = 0, \qquad i = 1, 2$",
             fontsize=15.5, weight='bold', color=BLUE, ha='center', va='center', zorder=4)

    ax2.text(0, -1.305,
             r"Derived from Lagrangian $\mathcal{L} = T - V$; energy is conserved",
             fontsize=14.2, weight='normal', color=DARK_SLATE, ha='center', va='center', zorder=4)

    # Highlighted phase-space dimension pill
    pill_ps2 = patches.FancyBboxPatch((-1.32, -1.575), 2.64, 0.13,
                                      boxstyle="round,pad=0.015,rounding_size=0.04",
                                      facecolor=BLUE_LIGHT, edgecolor=BLUE_BORDER, lw=1.1, zorder=3.5)
    ax2.add_patch(pill_ps2)

    ax2.text(0, -1.51, "4D Phase Space  •  Motion on a 3D energy surface",
             fontsize=14.5, weight='bold', color=NAVY, ha='center', va='center', zorder=4)

    # Save to primary and alternate output paths
    plt.savefig(output_path, dpi=240, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    if ALT_OUT_1 != output_path:
        plt.savefig(ALT_OUT_1, dpi=240, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Generated: {output_path}")
    print(f"[OK] Generated: {ALT_OUT_1}")


if __name__ == "__main__":
    create_figure()
