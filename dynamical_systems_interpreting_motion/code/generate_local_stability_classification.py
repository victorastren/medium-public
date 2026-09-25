#!/usr/bin/env python3
"""
Generate infographic:
"Local Geometry Near Fixed Points: Classification of 2D Dynamical Systems"
2x2 grid showing the four fundamental fixed-point geometries:
Panel A: Stable node (λ1 < 0, λ2 < 0)
Panel B: Saddle (λ1 < 0 < λ2) [Inverted equilibrium of ideal pendulum]
Panel C: Center (λ = ±iβ) [Downward equilibrium of ideal pendulum]
Panel D: Stable spiral (λ = α ± iβ, α < 0)
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "local_stability_classification.png"

def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Color Palette matching editorial identity
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#334155'
    LIGHT_SLATE = '#94a3b8'
    BORDER_COLOR = '#cbd5e1'
    CARD_BG = '#f8fafc'
    PLOT_BG = '#ffffff'

    BLUE = '#1d4ed8'
    BLUE_DARK = '#1e40af'
    RED = '#dc2626'
    RED_DARK = '#991b1b'
    EMERALD = '#047857'
    PURPLE = '#7c3aed'

    PILL_BG_BLUE = '#dbeafe'
    PILL_BORDER_BLUE = '#60a5fa'
    PILL_TEXT_BLUE = '#1e3a8a'

    PILL_BG_RED = '#fee2e2'
    PILL_BORDER_RED = '#f87171'
    PILL_TEXT_RED = '#7f1d1d'

    # Figure dimensions in inches
    fig_w = 15.0
    fig_h = 15.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Top Figure Title Badge (styled consistently with other article diagrams)
    fig.text(0.5, 0.967,
             "Local Geometry Near Fixed Points",
             fontsize=19.5, weight='bold', color=NAVY, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.30",
                       facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1.3))

    # Prominent, darkened, highly legible subtitle
    fig.text(0.5, 0.936,
             "The eigenvalues of the Jacobian characterize the linearized flow near an equilibrium.",
             fontsize=15.0, weight='bold', color=NAVY, ha='center', va='center')

    # Card dimensions
    card_w_in = 6.65
    card_h_in = 6.75
    gap_x_in = 0.50
    gap_y_in = 0.44

    left_margin_in = (fig_w - (2 * card_w_in + gap_x_in)) / 2.0
    col1_x_in = left_margin_in
    col2_x_in = col1_x_in + card_w_in + gap_x_in

    row2_y_in = 0.50
    row1_y_in = row2_y_in + card_h_in + gap_y_in

    card_coords = [
        (col1_x_in, row1_y_in),  # Top-Left: Stable Node
        (col2_x_in, row1_y_in),  # Top-Right: Saddle
        (col1_x_in, row2_y_in),  # Bottom-Left: Center
        (col2_x_in, row2_y_in),  # Bottom-Right: Stable Spiral
    ]

    # Inner plot square dimensions
    plot_side_in = 4.35
    plot_x_offset_in = (card_w_in - plot_side_in) / 2.0
    plot_y_offset_in = 0.74

    plot_axes = []

    for i, (cx, cy) in enumerate(card_coords):
        # 1. Background Card Axis
        card_ax = fig.add_axes([cx / fig_w, cy / fig_h, card_w_in / fig_w, card_h_in / fig_h])
        card_ax.set_facecolor(CARD_BG)
        card_ax.set_xlim(0, card_w_in)
        card_ax.set_ylim(0, card_h_in)
        card_ax.set_xticks([])
        card_ax.set_yticks([])
        for sp in card_ax.spines.values():
            sp.set_color(BORDER_COLOR)
            sp.set_linewidth(1.3)

        # 2. Inner Plot Square Axis
        px = cx + plot_x_offset_in
        py = cy + plot_y_offset_in
        plot_ax = fig.add_axes([px / fig_w, py / fig_h, plot_side_in / fig_w, plot_side_in / fig_h])
        plot_ax.set_facecolor(PLOT_BG)
        plot_ax.set_xlim(-2.05, 2.05)
        plot_ax.set_ylim(-2.05, 2.05)
        plot_ax.set_aspect('equal')
        plot_ax.set_xticks([])
        plot_ax.set_yticks([])
        for sp in plot_ax.spines.values():
            sp.set_color(BORDER_COLOR)
            sp.set_linewidth(1.1)

        # Central crosshairs
        plot_ax.axhline(0, color=LIGHT_SLATE, lw=1.1, ls='--', alpha=0.70, zorder=1)
        plot_ax.axvline(0, color=LIGHT_SLATE, lw=1.1, ls='--', alpha=0.70, zorder=1)
        plot_ax.text(1.92, -0.18, r"$x_1$", fontsize=14.5, color=NAVY, weight='bold', ha='right', va='center',
                     bbox=dict(boxstyle="square,pad=0.10", facecolor='#ffffff', edgecolor='none', alpha=0.85), zorder=7)
        plot_ax.text(0.14, 1.92, r"$x_2$", fontsize=14.5, color=NAVY, weight='bold', ha='left', va='top',
                     bbox=dict(boxstyle="square,pad=0.10", facecolor='#ffffff', edgecolor='none', alpha=0.85), zorder=7)

        plot_axes.append((card_ax, plot_ax))

    # Helper function for card titles, pills, and footer annotations
    def decorate_card(card_ax, title, formula, annotation, pendulum_note=None, emphasis=False):
        # Header title
        card_ax.text(0.35, 6.26, title, fontsize=17.5, weight='bold',
                     color=NAVY if not emphasis else RED_DARK, ha='left', va='center')
        # Prominent eigenvalue formula (enlarged, bold, saturated color)
        card_ax.text(card_w_in - 0.35, 6.26, formula, fontsize=16.5, weight='bold',
                     color=BLUE_DARK if not emphasis else RED_DARK, ha='right', va='center')

        # Secondary note pill badge: bold, enlarged 13pt font, high-contrast colors
        if pendulum_note:
            pill_w = 5.40
            pill_h = 0.46
            pill_x = (card_w_in - pill_w) / 2.0
            pill_y = 5.43
            pill = patches.FancyBboxPatch((pill_x, pill_y), pill_w, pill_h,
                                          boxstyle="round,pad=0.02,rounding_size=0.10",
                                          facecolor=PILL_BG_RED if emphasis else PILL_BG_BLUE,
                                          edgecolor=PILL_BORDER_RED if emphasis else PILL_BORDER_BLUE,
                                          lw=1.3, zorder=3)
            card_ax.add_patch(pill)
            card_ax.text(card_w_in / 2.0, pill_y + pill_h / 2.0, pendulum_note,
                         fontsize=13.0, weight='bold',
                         color=PILL_TEXT_RED if emphasis else PILL_TEXT_BLUE,
                         ha='center', va='center', zorder=4)

        # Bottom panel text: prominent, bold, deep NAVY color, cleanly split across two lines
        card_ax.text(card_w_in / 2.0, 0.37, annotation, fontsize=12.5, weight='bold',
                     color=NAVY, ha='center', va='center', linespacing=1.25)

    # Label bbox helper
    def text_bbox():
        return dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#cbd5e1', lw=0.9, alpha=0.95)

    # =========================================================================
    # PANEL A: STABLE NODE (λ1 < 0, λ2 < 0)
    # =========================================================================
    cardA, axA = plot_axes[0]
    decorate_card(
        cardA,
        title="Stable node",
        formula=r"$\lambda_1 < 0, \quad \lambda_2 < 0$",
        annotation="Perturbations decay\nwithout oscillation."
    )

    # Eigendirections: v1 along 18°, v2 along 128°
    th1 = np.radians(18)
    v1 = np.array([np.cos(th1), np.sin(th1)])
    th2 = np.radians(128)
    v2 = np.array([np.cos(th2), np.sin(th2)])
    lam1 = -1.0
    lam2 = -3.2
    V_mat = np.column_stack([v1, v2])
    V_inv = np.linalg.inv(V_mat)

    # Draw principal eigendirections
    t_span = np.linspace(-1.95, 1.95, 100)
    axA.plot(t_span * v1[0], t_span * v1[1], color=BLUE, lw=2.6, ls='-', alpha=0.95, zorder=3)
    axA.plot(t_span * v2[0], t_span * v2[1], color=PURPLE, lw=2.1, ls='--', alpha=0.85, zorder=3)

    # Inward arrows on eigendirections (both branches pointing toward origin)
    for s in [-1.30, 1.30]:
        p_start = s * v1
        p_end = (s - 0.38 * np.sign(s)) * v1
        axA.annotate('', xy=p_end, xytext=p_start,
                     arrowprops=dict(arrowstyle="->,head_width=0.38,head_length=0.50", color=BLUE, lw=2.5), zorder=5)
    for s in [-1.40, 1.40]:
        p_start = s * v2
        p_end = (s - 0.40 * np.sign(s)) * v2
        axA.annotate('', xy=p_end, xytext=p_start,
                     arrowprops=dict(arrowstyle="->,head_width=0.34,head_length=0.46", color=PURPLE, lw=2.1), zorder=5)

    # Labels for eigendirections (simply v1 and v2, prominent and crisp)
    axA.text(1.62 * v1[0] + 0.08, 1.62 * v1[1] - 0.16, r"$\mathbf{v}_1$",
             fontsize=12.5, color=BLUE_DARK, weight='bold', bbox=text_bbox(), zorder=6)
    axA.text(1.36 * v2[0] - 0.12, 1.36 * v2[1] + 0.10, r"$\mathbf{v}_2$",
             fontsize=12.5, color=PURPLE, weight='bold', bbox=text_bbox(), zorder=6)

    # 16 smooth trajectories starting from perimeter r = 1.90
    t_node = np.linspace(0, 3.5, 200)
    for angle in np.linspace(0, 2*np.pi, 16, endpoint=False):
        x0 = 1.90 * np.cos(angle)
        y0 = 1.90 * np.sin(angle)
        c = V_inv @ np.array([x0, y0])
        xs = c[0] * np.exp(lam1 * t_node) * v1[0] + c[1] * np.exp(lam2 * t_node) * v2[0]
        ys = c[0] * np.exp(lam1 * t_node) * v1[1] + c[1] * np.exp(lam2 * t_node) * v2[1]
        axA.plot(xs, ys, color=SLATE, lw=1.25, alpha=0.65, zorder=2)
        # Inward arrow
        idx = 35
        axA.annotate('', xy=(xs[idx+4], ys[idx+4]), xytext=(xs[idx], ys[idx]),
                     arrowprops=dict(arrowstyle="->,head_width=0.20,head_length=0.28", color=SLATE, lw=1.2), zorder=4)

    # Fixed point marker
    axA.plot(0, 0, 'o', color=NAVY, markersize=9.0, markeredgecolor='#ffffff', markeredgewidth=2.0, zorder=10)
    axA.text(0.12, -0.24, r"$\mathbf{x}_*$", fontsize=13.0, color=NAVY, weight='bold', zorder=10)


    # =========================================================================
    # PANEL B: SADDLE (λ1 < 0 < λ2) [Inverted Equilibrium]
    # =========================================================================
    cardB, axB = plot_axes[1]
    decorate_card(
        cardB,
        title="Saddle",
        formula=r"$\lambda_1 < 0 < \lambda_2$",
        annotation="Stable in one direction,\nunstable in another.",
        pendulum_note="Inverted equilibrium of the ideal pendulum",
        emphasis=True
    )

    # Stable direction along -35°, Unstable direction along +45°
    th_s = np.radians(-35)
    v_s = np.array([np.cos(th_s), np.sin(th_s)])
    th_u = np.radians(45)
    v_u = np.array([np.cos(th_u), np.sin(th_u)])

    # Plot Stable and Unstable Directions
    t_sep = np.linspace(-1.95, 1.95, 100)
    axB.plot(t_sep * v_s[0], t_sep * v_s[1], color=BLUE, lw=2.6, ls='-', alpha=0.95, zorder=4)
    axB.plot(t_sep * v_u[0], t_sep * v_u[1], color=RED, lw=2.6, ls='-', alpha=0.95, zorder=4)

    # Bold, unmistakable arrows on Stable direction: both branches point TOWARD origin x_*
    # Branch 1 (Quadrant 2, s < 0): arrow from s=-1.40 towards s=-0.92 (inward towards origin)
    p_start_s1 = -1.40 * v_s
    p_end_s1 = -0.92 * v_s
    axB.annotate('', xy=p_end_s1, xytext=p_start_s1,
                 arrowprops=dict(arrowstyle="->,head_width=0.45,head_length=0.60", color=BLUE_DARK, lw=2.8), zorder=8)

    # Branch 2 (Quadrant 4, s > 0): arrow from s=+1.40 towards s=+0.92 (inward towards origin)
    p_start_s2 = 1.40 * v_s
    p_end_s2 = 0.92 * v_s
    axB.annotate('', xy=p_end_s2, xytext=p_start_s2,
                 arrowprops=dict(arrowstyle="->,head_width=0.45,head_length=0.60", color=BLUE_DARK, lw=2.8), zorder=8)

    # Bold, unmistakable arrows on Unstable direction: both branches point AWAY from origin x_*
    # Branch 1 (Quadrant 3, s < 0): arrow from s=-0.80 pointing outward towards s=-1.36
    p_start_u1 = -0.80 * v_u
    p_end_u1 = -1.36 * v_u
    axB.annotate('', xy=p_end_u1, xytext=p_start_u1,
                 arrowprops=dict(arrowstyle="->,head_width=0.45,head_length=0.60", color=RED_DARK, lw=2.8), zorder=8)

    # Branch 2 (Quadrant 1, s > 0): arrow from s=+0.80 pointing outward towards s=+1.36
    p_start_u2 = 0.80 * v_u
    p_end_u2 = 1.36 * v_u
    axB.annotate('', xy=p_end_u2, xytext=p_start_u2,
                 arrowprops=dict(arrowstyle="->,head_width=0.45,head_length=0.60", color=RED_DARK, lw=2.8), zorder=8)

    # Labels placed cleanly alongside eigendirections without obscuring arrows
    # "Unstable direction" placed above the line in Quadrant 1, well clear of line and arrow
    axB.text(0.35, 1.54, "Unstable direction",
             fontsize=12.0, color=RED_DARK, weight='bold',
             bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#fca5a5', lw=1.0, alpha=0.95),
             zorder=9)
    # "Stable direction" placed below the line in Quadrant 4, clear of border and arrow
    axB.text(0.90, -1.22, "Stable direction",
             fontsize=12.0, color=BLUE_DARK, weight='bold',
             bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#93c5fd', lw=1.0, alpha=0.95),
             zorder=9)

    # Hyperbolic trajectories
    t_hyp = np.linspace(-2.2, 2.2, 220)
    hyp_pairs = [
        (1.1, 0.16), (1.4, 0.42), (1.7, 0.80),
        (-1.1, 0.16), (-1.4, 0.42), (-1.7, 0.80),
        (1.1, -0.16), (1.4, -0.42), (1.7, -0.80),
        (-1.1, -0.16), (-1.4, -0.42), (-1.7, -0.80),
        (0.18, 1.2), (0.45, 1.5), (-0.18, 1.2), (-0.45, 1.5),
        (0.18, -1.2), (0.45, -1.5), (-0.18, -1.2), (-0.45, -1.5),
    ]
    for cs, cu in hyp_pairs:
        xs = cs * np.exp(-t_hyp) * v_s[0] + cu * np.exp(t_hyp) * v_u[0]
        ys = cs * np.exp(-t_hyp) * v_s[1] + cu * np.exp(t_hyp) * v_u[1]
        mask = (np.abs(xs) <= 1.95) & (np.abs(ys) <= 1.95)
        if np.any(mask):
            xs_m = xs[mask]
            ys_m = ys[mask]
            if len(xs_m) > 12:
                axB.plot(xs_m, ys_m, color=SLATE, lw=1.2, alpha=0.6, zorder=2)
                mid = len(xs_m) // 2
                axB.annotate('', xy=(xs_m[mid+3], ys_m[mid+3]), xytext=(xs_m[mid], ys_m[mid]),
                             arrowprops=dict(arrowstyle="->,head_width=0.18,head_length=0.25", color=SLATE, lw=1.2), zorder=4)

    # Fixed point marker
    axB.plot(0, 0, 'o', color=RED, markersize=9.0, markeredgecolor='#ffffff', markeredgewidth=2.0, zorder=10)
    axB.text(0.12, -0.24, r"$\mathbf{x}_*$", fontsize=13.0, color=RED, weight='bold', zorder=10)


    # =========================================================================
    # PANEL C: CENTER (λ = ±iβ) [Downward Equilibrium]
    # =========================================================================
    cardC, axC = plot_axes[2]
    decorate_card(
        cardC,
        title="Center",
        formula=r"$\lambda = \pm i\beta$",
        annotation="Nearby trajectories form closed orbits\naround the equilibrium.",
        pendulum_note="Downward equilibrium of the ideal pendulum"
    )

    # Concentric ellipses with clockwise circulation
    theta_circ = np.linspace(0, 2*np.pi, 250)
    radii_a = [0.42, 0.82, 1.22, 1.62]
    aspect = 0.85

    for r in radii_a:
        rx = r
        ry = r * aspect
        xs = rx * np.cos(theta_circ)
        ys = -ry * np.sin(theta_circ)  # negative sin for clockwise
        axC.plot(xs, ys, color=EMERALD, lw=1.6, alpha=0.9, zorder=3)

        # 2 circulating arrows per closed orbit
        for angle in [np.pi/4, 5*np.pi/4]:
            x_arr = rx * np.cos(angle)
            y_arr = -ry * np.sin(angle)
            dx = 0.15 * np.sin(angle)
            dy = 0.15 * np.cos(angle)
            axC.annotate('', xy=(x_arr + dx, y_arr + dy), xytext=(x_arr - dx, y_arr - dy),
                         arrowprops=dict(arrowstyle="->,head_width=0.24,head_length=0.32", color=EMERALD, lw=1.6), zorder=5)

    # Fixed point marker
    axC.plot(0, 0, 'o', color=NAVY, markersize=9.0, markeredgecolor='#ffffff', markeredgewidth=2.0, zorder=10)
    axC.text(0.12, -0.24, r"$\mathbf{x}_*$", fontsize=13.0, color=NAVY, weight='bold', zorder=10)


    # =========================================================================
    # PANEL D: STABLE SPIRAL (λ = α ± iβ, α < 0)
    # =========================================================================
    cardD, axD = plot_axes[3]
    decorate_card(
        cardD,
        title="Stable spiral",
        formula=r"$\lambda = \alpha \pm i\beta, \quad \alpha < 0$",
        annotation="Oscillations decay as trajectories\napproach the fixed point."
    )

    # Inward logarithmic spirals: r(t) = r0 * exp(alpha * t), theta(t) = theta0 - beta * t
    alpha = -0.20
    beta = 1.65
    t_spiral = np.linspace(0, 9.5, 300)

    # 4 spiral arms starting from 4 quadrants at r0 = 1.88
    start_angles = [0, np.pi/2, np.pi, 3*np.pi/2]
    r0 = 1.88

    for th0 in start_angles:
        r_t = r0 * np.exp(alpha * t_spiral)
        th_t = th0 - beta * t_spiral
        xs = r_t * np.cos(th_t)
        ys = r_t * np.sin(th_t)
        axD.plot(xs, ys, color=BLUE, lw=1.5, alpha=0.9, zorder=3)

        # Arrows showing inward flow along each spiral arm
        for step in [25, 95, 175]:
            if step + 4 < len(xs) and r_t[step] > 0.22:
                axD.annotate('', xy=(xs[step+4], ys[step+4]), xytext=(xs[step], ys[step]),
                             arrowprops=dict(arrowstyle="->,head_width=0.22,head_length=0.30", color=BLUE, lw=1.4), zorder=5)

    # Fixed point marker
    axD.plot(0, 0, 'o', color=NAVY, markersize=9.0, markeredgecolor='#ffffff', markeredgewidth=2.0, zorder=10)
    axD.text(0.12, -0.24, r"$\mathbf{x}_*$", fontsize=13.0, color=NAVY, weight='bold', zorder=10)

    # Save
    plt.savefig(output_path, dpi=240, bbox_inches='tight', facecolor='#ffffff')
    plt.close()
    print(f"[OK] Generated {output_path}")
    return output_path

if __name__ == "__main__":
    create_figure()
