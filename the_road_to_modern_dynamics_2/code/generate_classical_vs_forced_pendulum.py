#!/usr/bin/env python3
r"""
Generate infographic for Article 2:
"From the Simple Pendulum to the Forced Pendulum"

Two-panel schematic comparison matching the publication standards of:
- the_road_to_modern_dynamics / generate_pendulum_coordinate_transition.py
- the_road_to_modern_dynamics_2 / generate_three_body_solutions_crtbp.py

Panel A: Classical Simple Pendulum
- Angle theta, length L, weight mg; no forcing or damping.
- Equation: \ddot{\theta} + \omega_0^2 \sin\theta = 0
- Conservative system with constant mechanical energy.
- Constant-energy trajectories in 2D phase space.

Panel B: Periodically Forced and Damped Pendulum
- Same geometry, with damping torque (opposing motion) and periodic forcing A \cos(\Omega t).
- Both forcing and damping depicted as rotational terms around the pivot.
- Equation: \ddot{\theta} + \gamma\dot{\theta} + \omega_0^2 \sin\theta = A\cos(\Omega t)
- Nonconservative system exchanging energy with surroundings.
- Nonautonomous motion in 3D extended phase space.

Revisions:
- External torque labeled as "Periodic forcing: A cos(Ωt)".
- Damping represented as a curved arrow around the pivot opposing the indicated motion \dot{\theta} > 0.
- Compact, aligned badges on left with generous clearance to vertical reference axis.
- Subtitle pill lowered down with generous clearance from the panel titles.
- Weight labeled as "Weight mg" in both panels.
- Bottom explanatory text split into two distinct, uncrowded lines per panel.
- Minimum font size: 14pt across all text elements.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "classical_vs_forced_pendulum.png"


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

    # Dimensions: 17.0 x 8.6 inches at 240 DPI
    fig_w = 17.0
    fig_h = 8.6
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

    AMBER = '#d97706'         # External forcing accent
    AMBER_LIGHT = '#fffbeb'   # Soft amber tint
    AMBER_BORDER = '#fcd34d'  # Amber border

    RED = '#dc2626'           # Damping accent
    RED_LIGHT = '#fef2f2'     # Soft red tint
    RED_BORDER = '#fca5a5'    # Red border

    PURPLE = '#7c3aed'        # Weight accent

    # -------------------------------------------------------------
    # Main Header & Context Banner (>= 15.0 pt)
    # -------------------------------------------------------------
    fig.text(0.5, 0.960,
             "From the Simple Pendulum to the Forced Pendulum",
             fontsize=22.0, weight='bold', color=NAVY, ha='center', va='center')

    fig.text(0.5, 0.922,
             "Comparison of conservative Hamiltonian motion with periodic external forcing and dissipation",
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

    # Shared Geometry Parameters
    px0 = 0.0         # Pivot X
    py0 = 0.67        # Pivot Y
    theta_deg = 32.0  # Angular displacement in degrees
    theta_rad = np.radians(theta_deg)
    L_len = 1.26      # Pendulum length

    # Bob position
    bx = px0 + L_len * np.sin(theta_rad)
    by = py0 - L_len * np.cos(theta_rad)

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

    # Helper function for drawing ceiling support
    def draw_ceiling_mount(ax):
        # Support horizontal bar
        ax.plot([-0.38, 0.38], [py0, py0], color=DARK_SLATE, lw=2.6, zorder=3)
        # Hatching lines above support bar
        for hx in np.linspace(-0.33, 0.33, 8):
            ax.plot([hx, hx + 0.06], [py0, py0 + 0.08], color=DARK_SLATE, lw=1.6, zorder=3)
        # Pivot bearing outer circle
        pivot_outer = patches.Circle((px0, py0), 0.048, facecolor='#e2e8f0', edgecolor=DARK_SLATE, lw=1.8, zorder=12)
        ax.add_patch(pivot_outer)
        # Pivot center pin
        pivot_pin = patches.Circle((px0, py0), 0.018, facecolor=NAVY, edgecolor='none', zorder=13)
        ax.add_patch(pivot_pin)

    # =============================================================
    # PANEL A: CLASSICAL SIMPLE PENDULUM
    # =============================================================
    # Title placed high with generous clearance to the subtitle pill
    ax1.text(0, 1.23, "A. Classical Pendulum",
             fontsize=18.5, weight='bold', color=NAVY, ha='center', va='center')

    # Subtitle pill enlarged to provide ample breathing room
    pill1 = patches.FancyBboxPatch((-1.51, 0.885), 3.02, 0.19,
                                   boxstyle="round,pad=0.02,rounding_size=0.06",
                                   facecolor=BLUE_LIGHT, edgecolor=BLUE_BORDER, lw=1.2, zorder=2)
    ax1.add_patch(pill1)
    ax1.text(0, 0.98,
             r"Angle $\theta$, length $L$, gravity $g$; no forcing or damping",
             fontsize=14.2, weight='bold', color=DARK_SLATE, ha='center', va='center')

    # Ceiling mount
    draw_ceiling_mount(ax1)

    # Vertical reference line (theta = 0)
    ax1.plot([px0, px0], [py0, -0.12], '--', color=LIGHT_SLATE, lw=1.8, zorder=1)
    ax1.text(-0.08, 0.12, r"Vertical" "\n" r"$\theta = 0$",
             fontsize=14.0, color=SLATE, ha='right', va='center', linespacing=1.25)

    # Angular displacement arc (theta)
    r_arc = 0.48
    arc_th = np.linspace(-np.pi/2, -np.pi/2 + theta_rad, 40)
    ax1.plot(px0 + r_arc * np.cos(arc_th), py0 + r_arc * np.sin(arc_th), color=BLUE, lw=2.4, zorder=4)

    # Arrowhead at arc end pointing toward rod
    th_tip = -np.pi/2 + theta_rad
    ax1.annotate('', xy=(px0 + r_arc * np.cos(th_tip), py0 + r_arc * np.sin(th_tip)),
                 xytext=(px0 + r_arc * np.cos(th_tip - 0.07), py0 + r_arc * np.sin(th_tip - 0.07)),
                 arrowprops=dict(arrowstyle="->", color=BLUE, lw=2.4, mutation_scale=15), zorder=4)

    # Theta label with soft badge
    ax1.text(0.44, 0.33, r"Angle $\theta$", fontsize=16.0, weight='bold', color=BLUE, va='center',
             bbox=dict(boxstyle="round,pad=0.22", facecolor='#ffffff', edgecolor=BLUE_BORDER, lw=1.0), zorder=5)

    # Trajectory arc (dashed swing path)
    swing_angles = np.linspace(-np.radians(45), np.radians(50), 100)
    ax1.plot(px0 + L_len * np.sin(swing_angles), py0 - L_len * np.cos(swing_angles),
             '--', color='#cbd5e1', lw=1.8, zorder=1)

    # Rigid rod
    ax1.plot([px0, bx], [py0, by], color=DARK_SLATE, lw=3.6, zorder=3)

    # Length L label placed alongside rod
    ax1.text(0.46, 0.06, r"Length $L$", fontsize=15.5, weight='bold', color=DARK_SLATE, zorder=5)

    # Pendulum Bob
    draw_3d_sphere(ax1, bx, by, radius=0.125, base_color=BLUE, highlight_color='#ffffff', zorder=8)
    ax1.text(bx, by, "$m$", fontsize=15.0, weight='bold', color='#ffffff', ha='center', va='center', zorder=12)

    # Weight vector mg pointing downwards from bob (rigorous physical label)
    g_len = 0.34
    ax1.annotate('', xy=(bx, by - g_len), xytext=(bx, by),
                 arrowprops=dict(arrowstyle="->", color=PURPLE, lw=2.8, mutation_scale=18), zorder=9)
    ax1.text(bx + 0.14, by - g_len * 0.55, r"Weight $mg$",
             fontsize=15.0, weight='bold', color=PURPLE, va='center', zorder=10)

    # Bottom Summary Box: Classical Pendulum (spacious 4-line presentation)
    rect_box1 = patches.FancyBboxPatch((-1.44, -1.58), 2.88, 0.56,
                                       boxstyle="round,pad=0.03,rounding_size=0.08",
                                       facecolor=BG_BOX, edgecolor='#93c5fd', lw=1.4, zorder=3)
    ax1.add_patch(rect_box1)

    ax1.text(0, -1.10, r"Equation of Motion (Conservative)",
             fontsize=16.0, weight='bold', color=NAVY, ha='center', va='center', zorder=4)

    ax1.text(0, -1.24, r"$\ddot{\theta} + \omega_0^2 \sin\theta = 0, \quad \omega_0 = \sqrt{g/L}$",
             fontsize=16.0, weight='bold', color=BLUE, ha='center', va='center', zorder=4)

    ax1.text(0, -1.38, "Energy is strictly conserved",
             fontsize=14.2, weight='normal', color=DARK_SLATE, ha='center', va='center', zorder=4)

    ax1.text(0, -1.50, "Constant-energy trajectories in 2D phase space",
             fontsize=14.2, weight='normal', color=DARK_SLATE, ha='center', va='center', zorder=4)

    # =============================================================
    # PANEL B: FORCED AND DAMPED PENDULUM
    # =============================================================
    # Title placed high with generous clearance to the subtitle pill
    ax2.text(0, 1.23, "B. Forced and Damped Pendulum",
             fontsize=18.5, weight='bold', color=NAVY, ha='center', va='center')

    # Subtitle pill enlarged to provide ample breathing room
    pill2 = patches.FancyBboxPatch((-1.51, 0.885), 3.02, 0.19,
                                   boxstyle="round,pad=0.02,rounding_size=0.06",
                                   facecolor=AMBER_LIGHT, edgecolor=AMBER_BORDER, lw=1.2, zorder=2)
    ax2.add_patch(pill2)
    ax2.text(0, 0.98,
             r"Same geometry, with damping $\gamma$ and periodic forcing $A\cos(\Omega t)$",
             fontsize=14.2, weight='bold', color=DARK_SLATE, ha='center', va='center')

    # Ceiling mount
    draw_ceiling_mount(ax2)

    # Vertical reference line (theta = 0)
    ax2.plot([px0, px0], [py0, -0.12], '--', color=LIGHT_SLATE, lw=1.8, zorder=1)
    ax2.text(-0.08, 0.12, r"Vertical" "\n" r"$\theta = 0$",
             fontsize=14.0, color=SLATE, ha='right', va='center', linespacing=1.25)

    # Angular displacement arc (theta)
    ax2.plot(px0 + r_arc * np.cos(arc_th), py0 + r_arc * np.sin(arc_th), color=BLUE, lw=2.4, zorder=4)
    ax2.annotate('', xy=(px0 + r_arc * np.cos(th_tip), py0 + r_arc * np.sin(th_tip)),
                 xytext=(px0 + r_arc * np.cos(th_tip - 0.07), py0 + r_arc * np.sin(th_tip - 0.07)),
                 arrowprops=dict(arrowstyle="->", color=BLUE, lw=2.4, mutation_scale=15), zorder=4)
    ax2.text(0.44, 0.33, r"Angle $\theta$", fontsize=16.0, weight='bold', color=BLUE, va='center',
             bbox=dict(boxstyle="round,pad=0.22", facecolor='#ffffff', edgecolor=BLUE_BORDER, lw=1.0), zorder=5)

    # Trajectory arc (dashed swing path)
    ax2.plot(px0 + L_len * np.sin(swing_angles), py0 - L_len * np.cos(swing_angles),
             '--', color='#cbd5e1', lw=1.8, zorder=1)

    # Rigid rod
    ax2.plot([px0, bx], [py0, by], color=DARK_SLATE, lw=3.6, zorder=3)

    # Length L label placed alongside rod
    ax2.text(0.46, 0.06, r"Length $L$", fontsize=15.5, weight='bold', color=DARK_SLATE, zorder=5)

    # Pendulum Bob
    draw_3d_sphere(ax2, bx, by, radius=0.125, base_color='#1d4ed8', highlight_color='#ffffff', zorder=8)
    ax2.text(bx, by, "$m$", fontsize=15.0, weight='bold', color='#ffffff', ha='center', va='center', zorder=12)

    # Weight vector mg pointing downwards from bob (rigorous physical label)
    ax2.annotate('', xy=(bx, by - g_len), xytext=(bx, by),
                 arrowprops=dict(arrowstyle="->", color=PURPLE, lw=2.8, mutation_scale=18), zorder=9)
    ax2.text(bx + 0.14, by - g_len * 0.55, r"Weight $mg$",
             fontsize=15.0, weight='bold', color=PURPLE, va='center', zorder=10)

    # Motion direction cue along swing trajectory at bob
    vel_dir_x = np.cos(theta_rad)
    vel_dir_y = np.sin(theta_rad)
    ax2.annotate('', xy=(bx + 0.32 * vel_dir_x, by + 0.32 * vel_dir_y), xytext=(bx, by),
                 arrowprops=dict(arrowstyle="->", color=SLATE, lw=2.0, linestyle="--"), zorder=13)
    ax2.text(bx + 0.36 * vel_dir_x + 0.02, by + 0.36 * vel_dir_y + 0.04,
             r"Motion $\dot{\theta} > 0$", fontsize=13.8, color=SLATE, weight='bold', zorder=13)

    # -------------------------------------------------------------
    # ROTATIONAL TERMS ABOUT PIVOT IN PANEL B
    # -------------------------------------------------------------
    # 1. Periodic Forcing: A cos(Omega t)
    # Encircling pivot at inner radius r = 0.20 (from -165 deg to -75 deg, bidirectional)
    r_trq = 0.20
    trq_angles = np.linspace(-np.radians(165), -np.radians(75), 50)
    ax2.plot(px0 + r_trq * np.cos(trq_angles), py0 + r_trq * np.sin(trq_angles),
             color=AMBER, lw=3.2, zorder=14)

    # Arrowheads on both ends to emphasize oscillating / periodic forcing
    a1_tip = trq_angles[-1]
    ax2.annotate('', xy=(px0 + r_trq * np.cos(a1_tip), py0 + r_trq * np.sin(a1_tip)),
                 xytext=(px0 + r_trq * np.cos(a1_tip - 0.09), py0 + r_trq * np.sin(a1_tip - 0.09)),
                 arrowprops=dict(arrowstyle="->", color=AMBER, lw=3.2, mutation_scale=16), zorder=15)

    a0_tip = trq_angles[0]
    ax2.annotate('', xy=(px0 + r_trq * np.cos(a0_tip), py0 + r_trq * np.sin(a0_tip)),
                 xytext=(px0 + r_trq * np.cos(a0_tip + 0.09), py0 + r_trq * np.sin(a0_tip + 0.09)),
                 arrowprops=dict(arrowstyle="->", color=AMBER, lw=3.2, mutation_scale=16), zorder=15)

    # Callout badge for periodic forcing placed with generous margin to the left
    ax2.text(-0.96, 0.54,
             "Periodic forcing:\n" r"$A\cos(\Omega t)$",
             fontsize=14.5, weight='bold', color=AMBER, ha='center', va='center', linespacing=1.28,
             bbox=dict(boxstyle="round,pad=0.28", facecolor='#ffffff', edgecolor=AMBER_BORDER, lw=1.3),
             zorder=16)

    # Connector line from badge to forcing arrow
    arc_mid_x = px0 + r_trq * np.cos(-np.radians(125))
    arc_mid_y = py0 + r_trq * np.sin(-np.radians(125))
    ax2.annotate('', xy=(arc_mid_x, arc_mid_y), xytext=(-0.58, 0.54),
                 arrowprops=dict(arrowstyle="-", color=AMBER, lw=1.6, linestyle=":"), zorder=14)

    # 2. Damping term: curved arrow around pivot opposing motion (\dot{\theta} > 0 is clockwise)
    # Concentric arc at outer radius r = 0.34, pointing counter-clockwise (from -80 deg to -155 deg)
    r_damp = 0.34
    damp_angles = np.linspace(-np.radians(80), -np.radians(155), 50)
    ax2.plot(px0 + r_damp * np.cos(damp_angles), py0 + r_damp * np.sin(damp_angles),
             color=RED, lw=3.2, zorder=14)

    # Single arrowhead at -155 deg pointing counter-clockwise (opposing clockwise swing)
    damp_tip = damp_angles[-1]
    ax2.annotate('', xy=(px0 + r_damp * np.cos(damp_tip), py0 + r_damp * np.sin(damp_tip)),
                 xytext=(px0 + r_damp * np.cos(damp_tip + 0.09), py0 + r_damp * np.sin(damp_tip + 0.09)),
                 arrowprops=dict(arrowstyle="->", color=RED, lw=3.2, mutation_scale=17), zorder=15)

    # Callout badge for damping: compact, matching width to forcing box, ample clearance to vertical line
    ax2.text(-0.96, 0.26,
             "Damping: " r"$-\gamma\,\dot{\theta}$" "\n(opposes motion)",
             fontsize=14.2, weight='bold', color=RED, ha='center', va='center', linespacing=1.28,
             bbox=dict(boxstyle="round,pad=0.28", facecolor='#ffffff', edgecolor=RED_BORDER, lw=1.3),
             zorder=16)

    # Connector line from badge to damping arrow
    damp_mid_x = px0 + r_damp * np.cos(-np.radians(125))
    damp_mid_y = py0 + r_damp * np.sin(-np.radians(125))
    ax2.annotate('', xy=(damp_mid_x, damp_mid_y), xytext=(-0.50, 0.26),
                 arrowprops=dict(arrowstyle="-", color=RED, lw=1.6, linestyle=":"), zorder=14)

    # Bottom Summary Box: Forced Pendulum (spacious 4-line presentation)
    rect_box2 = patches.FancyBboxPatch((-1.44, -1.58), 2.88, 0.56,
                                       boxstyle="round,pad=0.03,rounding_size=0.08",
                                       facecolor=BG_BOX, edgecolor=AMBER_BORDER, lw=1.4, zorder=3)
    ax2.add_patch(rect_box2)

    ax2.text(0, -1.10, r"Equation of Motion (Nonconservative)",
             fontsize=16.0, weight='bold', color=NAVY, ha='center', va='center', zorder=4)

    ax2.text(0, -1.24, r"$\ddot{\theta} + \gamma\dot{\theta} + \omega_0^2 \sin\theta = A\cos(\Omega t)$",
             fontsize=16.0, weight='bold', color=AMBER, ha='center', va='center', zorder=4)

    ax2.text(0, -1.38, "Energy exchange through forcing and damping",
             fontsize=14.2, weight='normal', color=DARK_SLATE, ha='center', va='center', zorder=4)

    ax2.text(0, -1.50, "Nonautonomous motion in 3D extended phase space",
             fontsize=14.2, weight='normal', color=DARK_SLATE, ha='center', va='center', zorder=4)

    # Save figure
    plt.savefig(output_path, dpi=240, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Generated: {output_path}")


if __name__ == "__main__":
    create_figure()
