#!/usr/bin/env python3
"""
Generate figure:
"From Cartesian Coordinates & Constraints to Generalized Coordinates"
Pedagogical comparison for the simple pendulum:
Panel 1: Cartesian formulation (x, y) with constraint circle x^2 + y^2 = l^2 and tension T
Panel 2: Generalized coordinate formulation (theta) with automatic constraint satisfaction
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "pendulum_coordinate_transition.png"

def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 16:9 ratio, ultra-crisp resolution with generous headroom for title
    fig_w = 17.0
    fig_h = 9.4
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Color Palette matching publication standards
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#475569'
    LIGHT_SLATE = '#94a3b8'
    BLUE = '#2563eb'
    RED = '#dc2626'
    EMERALD = '#059669'
    PURPLE = '#7c3aed'
    CARD_BG = '#f8fafc'
    BORDER_COLOR = '#cbd5e1'
    HIGHLIGHT_BG = '#ffffff'

    # Title badge (with plenty of margin from canvas top)
    fig.text(0.5, 0.940,
             "The Pendulum: Cartesian Coordinates and One Degree of Freedom",
             fontsize=20, weight='bold', color=NAVY, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.30",
                       facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1.3))

    w_card = 0.445
    h_card = 0.84
    y_card = 0.040
    x1 = 0.04
    x2 = 0.515

    ax1 = fig.add_axes([x1, y_card, w_card, h_card])
    ax2 = fig.add_axes([x2, y_card, w_card, h_card])

    # Coordinate system setup: Pivot is at (0, 0.35)
    py0 = 0.35
    px0 = 0.0
    theta_deg = 36
    theta_rad = np.radians(theta_deg)
    l_len = 1.30
    bx = px0 + l_len * np.sin(theta_rad)
    by = py0 - l_len * np.cos(theta_rad)

    for ax in (ax1, ax2):
        ax.set_facecolor(CARD_BG)
        ax.axis('off')
        ax.set_xlim(-1.65, 1.65)
        ax.set_ylim(-1.92, 1.38)
        # Outer card frame
        rect = patches.FancyBboxPatch((-1.60, -1.83), 3.20, 3.15,
                                      boxstyle="round,pad=0.03,rounding_size=0.15",
                                      facecolor=CARD_BG, edgecolor=BORDER_COLOR,
                                      lw=1.5, zorder=0)
        ax.add_patch(rect)

    # =============================================================
    # PANEL 1: CARTESIAN FORMULATION
    # =============================================================
    ax1.text(0, 1.21, "1. Cartesian Coordinates & Constraint",
             fontsize=18, weight='bold', color=NAVY, ha='center', va='center')
    ax1.text(0, 1.04,
             r"Two coordinates $(x,y)$ constrained by $x^2 + y^2 = l^2$" "\n"
             r"Tension $T$ is an unknown constraint force",
             fontsize=13.5, weight='bold', color=DARK_SLATE, ha='center', va='center', linespacing=1.28)

    # Cartesian Axes at Origin (0, py0)
    # y-axis terminates at py0 + 0.26 with label at py0 + 0.32, giving >0.35 clearance from subtitle at 1.04
    ax1.annotate('', xy=(1.45, py0), xytext=(-0.55, py0),
                 arrowprops=dict(arrowstyle="->", color=LIGHT_SLATE, lw=1.8))
    ax1.text(1.50, py0, "$x$", fontsize=17, weight='bold', color=DARK_SLATE, va='center')

    ax1.annotate('', xy=(0, py0 + 0.26), xytext=(0, by - 0.45),
                 arrowprops=dict(arrowstyle="->", color=LIGHT_SLATE, lw=1.8))
    ax1.text(0, py0 + 0.32, "$y$", fontsize=17, weight='bold', color=DARK_SLATE, ha='center')
    ax1.text(-0.08, py0 + 0.14, "Pivot $(0,0)$", fontsize=14, color=DARK_SLATE, ha='right', weight='bold')

    # Constraint circle arc
    arc_angles = np.linspace(-np.radians(60), np.radians(65), 100)
    arc_x = px0 + l_len * np.sin(arc_angles)
    arc_y = py0 - l_len * np.cos(arc_angles)
    ax1.plot(arc_x, arc_y, '--', color='#94a3b8', lw=1.8, zorder=1)

    # Constraint Callout Badge (left side, positioned with generous clearance)
    ax1.text(-1.55, -0.65,
             "Cartesian Description\n"
             r"Coordinates $(x, y)$" "\n"
             "plus constraint:\n"
             r"$x^2 + y^2 = l^2$",
             fontsize=13.5, color=DARK_SLATE, va='center', weight='bold', linespacing=1.35,
             bbox=dict(boxstyle="round,pad=0.40", facecolor='#ffffff', edgecolor='#cbd5e1', lw=1.3))

    # Projection lines to x and y axes
    ax1.plot([bx, bx], [py0, by], ':', color=SLATE, lw=1.6)
    ax1.plot([0, bx], [by, by], ':', color=SLATE, lw=1.6)
    ax1.plot(bx, py0, 's', color=SLATE, markersize=5.5)
    ax1.plot(0, by, 's', color=SLATE, markersize=5.5)
    ax1.text(bx, py0 + 0.08, "$x$", fontsize=16.0, color=DARK_SLATE, ha='center', weight='bold')
    ax1.text(-0.08, by, "$y$", fontsize=16.0, color=DARK_SLATE, ha='right', va='center', weight='bold')

    # Ceiling mount
    ax1.plot([-0.35, 0.35], [py0, py0], color=DARK_SLATE, lw=2.5, zorder=3)
    for hx in np.linspace(-0.3, 0.3, 7):
        ax1.plot([hx, hx + 0.06], [py0, py0 + 0.08], color=DARK_SLATE, lw=1.5, zorder=3)

    # Rod
    ax1.plot([px0, bx], [py0, by], color=DARK_SLATE, lw=3.8, zorder=2)
    ax1.plot(px0, py0, 'o', color=DARK_SLATE, markersize=8.0, zorder=4)

    # Fixed length label l (placed to the right of the rod)
    mid_rx = px0 + bx * 0.52 + 0.09
    mid_ry = py0 + (by - py0) * 0.52 + 0.04
    ax1.text(mid_rx, mid_ry, r"Length $l$", fontsize=15.0, weight='bold', color=DARK_SLATE)

    # Bob
    bob1 = patches.Circle((bx, by), 0.13, facecolor=BLUE, edgecolor=DARK_SLATE, lw=2.0, zorder=5)
    ax1.add_patch(bob1)
    ax1.text(bx, by, "$m$", fontsize=15.0, weight='bold', color='#ffffff', ha='center', va='center', zorder=6)
    ax1.text(bx + 0.18, by + 0.04, "$(x, y)$", fontsize=16.0, weight='bold', color=BLUE)

    # Force Vectors on Bob:
    # 1. Tension T (pointing towards pivot along rod)
    t_len = 0.52
    t_dx = -t_len * np.sin(theta_rad)
    t_dy = t_len * np.cos(theta_rad)
    ax1.annotate('', xy=(bx + t_dx, by + t_dy), xytext=(bx, by),
                 arrowprops=dict(arrowstyle="->", color=RED, lw=3.0, mutation_scale=18), zorder=7)
    # Tension label placed clearly to the left of the arrow
    ax1.text(bx + t_dx * 0.6 - 0.10, by + t_dy * 0.6,
             r"Tension $\mathbf{T}$" "\n(Constraint force)",
             fontsize=14.0, weight='bold', color=RED, ha='right', va='center', linespacing=1.25)

    # 2. Gravity F_g = m g (pointing downward)
    g_len = 0.32
    ax1.annotate('', xy=(bx, by - g_len), xytext=(bx, by),
                 arrowprops=dict(arrowstyle="->", color=PURPLE, lw=3.0, mutation_scale=18), zorder=7)
    ax1.text(bx + 0.18, by - g_len * 0.52, r"Gravity" "\n" r"$\mathbf{F}_g = m\,\mathbf{g}$",
             fontsize=14.0, weight='bold', color=PURPLE, va='center', linespacing=1.25)

    # Summary box Panel 1 (at bottom): Dedicated background box with left-aligned bullet items
    rect_box1 = patches.FancyBboxPatch((-1.48, -1.72), 2.96, 0.54,
                                        boxstyle="round,pad=0.02,rounding_size=0.08",
                                        facecolor=HIGHLIGHT_BG, edgecolor='#fca5a5',
                                        lw=1.4, zorder=3)
    ax1.add_patch(rect_box1)
    ax1.text(0, -1.255, "Cartesian Description",
             fontsize=14.5, color=DARK_SLATE, ha='center', va='center', weight='bold', zorder=4)
    bullets1 = (
        r"$\bullet$ 2 Coordinates: $x(t),\; y(t)$ subject to constraint" "\n"
        r"$\bullet$ 1 Algebraic constraint: $x^2 + y^2 = l^2$" "\n"
        r"$\bullet$ Tension $\mathbf{T}$ must be solved as an unknown reaction force"
    )
    ax1.text(-1.38, -1.355, bullets1, fontsize=12.4, color=DARK_SLATE, ha='left', va='top',
             linespacing=1.35, zorder=4)

    # =============================================================
    # PANEL 2: SINGLE ANGULAR COORDINATE
    # =============================================================
    ax2.text(0, 1.21, r"2. Single Angular Coordinate $\theta$",
             fontsize=18, weight='bold', color=NAVY, ha='center', va='center')
    ax2.text(0, 1.04,
             r"Single angular coordinate $\theta$ specifies configuration" "\n"
             r"One degree of freedom: constraint automatically satisfied",
             fontsize=13.5, weight='bold', color=DARK_SLATE, ha='center', va='center', linespacing=1.28)

    # Ceiling mount
    ax2.plot([-0.35, 0.35], [py0, py0], color=DARK_SLATE, lw=2.5, zorder=3)
    for hx in np.linspace(-0.3, 0.3, 7):
        ax2.plot([hx, hx + 0.06], [py0, py0 + 0.08], color=DARK_SLATE, lw=1.5, zorder=3)

    # Downward vertical reference line
    ax2.plot([0, 0], [py0, by - 0.40], '--', color=LIGHT_SLATE, lw=1.8, zorder=1)
    ax2.text(-0.08, py0 - 0.48, r"Vertical" "\n" r"$\theta = 0$", fontsize=13.0, color=SLATE, ha='right', va='center', linespacing=1.25)

    # Angle theta arc
    r_arc = 0.46
    arc_th = np.linspace(-np.pi/2, -np.pi/2 + theta_rad, 40)
    ax2.plot(px0 + r_arc * np.cos(arc_th), py0 + r_arc * np.sin(arc_th), color=BLUE, lw=2.5, zorder=2)
    # Angle arc arrow at rod
    arrow_th = -np.pi/2 + theta_rad
    ax2.annotate('', xy=(px0 + r_arc * np.cos(arrow_th), py0 + r_arc * np.sin(arrow_th)),
                 xytext=(px0 + r_arc * np.cos(arrow_th - 0.08), py0 + r_arc * np.sin(arrow_th - 0.08)),
                 arrowprops=dict(arrowstyle="->", color=BLUE, lw=2.5, mutation_scale=15))

    # Angle theta label: cleanly placed to the RIGHT of the pendulum thread
    # At y = 0.14, thread is at x = 0.15. Placing text at x = 0.36 gives ample clearance to the right
    ax2.text(0.36, 0.14, r"Angle $\theta$", fontsize=16.0, weight='bold', color=BLUE, va='center')

    # Rod
    ax2.plot([px0, bx], [py0, by], color=DARK_SLATE, lw=3.8, zorder=2)
    ax2.plot(px0, py0, 'o', color=DARK_SLATE, markersize=8.0, zorder=4)

    # Fixed length label l (right of the rod)
    ax2.text(mid_rx + 0.04, mid_ry, r"Length $l$", fontsize=15.0, weight='bold', color=DARK_SLATE)

    # Trajectory arc (same physical circular path as Panel 1, without introducing s)
    arc_angles2 = np.linspace(-np.radians(60), np.radians(65), 100)
    arc_x2 = px0 + l_len * np.sin(arc_angles2)
    arc_y2 = py0 - l_len * np.cos(arc_angles2)
    ax2.plot(arc_x2, arc_y2, '--', color='#94a3b8', lw=1.8, zorder=1)

    # Bob
    bob2 = patches.Circle((bx, by), 0.13, facecolor=BLUE, edgecolor=DARK_SLATE, lw=2.0, zorder=5)
    ax2.add_patch(bob2)
    ax2.text(bx, by, "$m$", fontsize=15.0, weight='bold', color='#ffffff', ha='center', va='center', zorder=6)

    # Tangential restoring force F_tan = -m g sin(theta)
    ftan_len = 0.50
    ftan_dx = -ftan_len * np.cos(theta_rad)
    ftan_dy = -ftan_len * np.sin(theta_rad)
    ax2.annotate('', xy=(bx + ftan_dx, by + ftan_dy), xytext=(bx, by),
                 arrowprops=dict(arrowstyle="->", color=EMERALD, lw=3.0, mutation_scale=18), zorder=7)
    # Restoring force label placed cleanly at the tip of the vector arrow
    ax2.text(bx + ftan_dx - 0.06, by + ftan_dy + 0.02,
             "Tangential restoring force:\n" r"$F_\theta = -mg\,\sin\theta$",
             fontsize=13.0, weight='bold', color=EMERALD, ha='right', va='center', linespacing=1.25,
             bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#a7f3d0', lw=1.2), zorder=8)

    # Gravity mg dashed components
    g_len2 = 0.30
    ax2.annotate('', xy=(bx, by - g_len2), xytext=(bx, by),
                 arrowprops=dict(arrowstyle="->", color=PURPLE, lw=1.8, linestyle='--'), zorder=6)
    ax2.text(bx + 0.08, by - g_len2 * 0.55, r"$m\,\mathbf{g}$", fontsize=14.5, color=PURPLE, weight='bold')

    # Direct Parameterization Badge (left side)
    ax2.text(-1.55, -0.65,
             "Single-Coordinate Description\n"
             r"Coordinate: $\theta$" "\n"
             "One degree of freedom",
             fontsize=13.5, color=DARK_SLATE, va='center', weight='bold', linespacing=1.35,
             bbox=dict(boxstyle="round,pad=0.40", facecolor='#ffffff', edgecolor='#93c5fd', lw=1.3))

    # Summary box Panel 2 (at bottom): Dedicated background box with left-aligned bullet items
    rect_box2 = patches.FancyBboxPatch((-1.48, -1.72), 2.96, 0.54,
                                        boxstyle="round,pad=0.02,rounding_size=0.08",
                                        facecolor=HIGHLIGHT_BG, edgecolor='#6ee7b7',
                                        lw=1.4, zorder=3)
    ax2.add_patch(rect_box2)
    ax2.text(0, -1.255, "Single-Coordinate Description",
             fontsize=14.5, color=DARK_SLATE, ha='center', va='center', weight='bold', zorder=4)
    bullets2 = (
        r"$\bullet$ 1 Independent coordinate: $\theta(t)$ (angle from vertical)" "\n"
        r"$\bullet$ Constraint $x^2 + y^2 = l^2$ automatically satisfied" "\n"
        r"$\bullet$ The constraint force $\mathbf{T}$ need not be determined" "\n"
        r"$\phantom{\bullet\ }$for the equation governing $\theta(t)$"
    )
    ax2.text(-1.38, -1.355, bullets2, fontsize=12.1, color=DARK_SLATE, ha='left', va='top',
             linespacing=1.20, zorder=4)

    plt.savefig(output_path, dpi=240, bbox_inches='tight', pad_inches=0.35, facecolor='#ffffff')
    plt.close()
    print(f"[OK] Pendulum coordinate transition infographic generated at: {output_path}")

if __name__ == "__main__":
    create_figure()
