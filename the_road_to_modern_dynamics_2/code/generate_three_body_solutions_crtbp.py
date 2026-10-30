#!/usr/bin/env python3
r"""
Generate infographic for Article 2:
"Particular Solutions and the Restricted Three-Body Problem"

Three-panel horizontal composite layout matching poincare_return_map_stability.png:
1. Panel 1 (Euler's Collinear Solutions, 1767):
   - Three mutually gravitating bodies (m1, m2, m3) remain collinear while revolving
     around their common center of mass in circular orbits.
   - Short label below plot: "Collinear configuration"

2. Panel 2 (Lagrange's Equilateral Solutions, 1772):
   - In the circular equilateral solution, three mutually gravitating bodies maintain
     an equilateral configuration while rotating about their common center of mass.
   - Short label below plot: "Equilateral configuration"

3. Panel 3 (Circular Restricted Three-Body Problem, CRTBP):
   - Two circular massive primaries (M1, M2), test mass m << M1, M2.
   - Co-rotating frame (x, y) centered at barycenter G.
   - Five stationary Lagrange equilibrium points (L1, L2, L3, L4, L5).
   - Equipotential contours (Roche lobes) in the background.
   - Short label below plot: "Five equilibrium points"

Design refinement:
- Bottom multi-line text boxes removed for clean, uncluttered presentation on Medium.
- Large, spacious plot areas with minimum 14pt typography.
- Concise short labels beneath each diagram.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scipy.optimize import brentq

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "three_body_solutions_crtbp.png"


def draw_3d_sphere(ax, x, y, radius, base_color='#2563eb', highlight_color='#ffffff', zorder=10):
    """Draw a 2D circle with radial shading to mimic a rich 3D celestial sphere."""
    shadow = patches.Circle((x, y), radius, facecolor=base_color, edgecolor='#0f172a',
                            linewidth=1.2, alpha=0.95, zorder=zorder)
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

    # Matplotlib styling for publication quality
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'axes.edgecolor': '#94a3b8',
        'axes.linewidth': 1.2,
    })

    # High-resolution widescreen canvas matching poincare_return_map_stability.png (18 x 9.8 in at 240 DPI)
    fig_w = 18.0
    fig_h = 8.40
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'          # Deep slate navy for main headings
    DARK_SLATE = '#1e293b'    # Body text & subheaders
    SLATE = '#334155'         # Secondary text
    BORDER_CARD = '#cbd5e1'   # Card border
    BG_CARD = '#f8fafc'       # Light background for panels
    BG_BOX = '#ffffff'        # Pure white for callout cards

    BLUE_ACCENT = '#2563eb'   # Primary blue accent
    BLUE_LIGHT = '#eff6ff'    # Soft blue tint
    BLUE_BORDER = '#93c5fd'   # Blue card border

    EMERALD_ACCENT = '#059669' # Emerald for Lagrange equilateral
    EMERALD_LIGHT = '#ecfdf5'  # Soft emerald tint
    EMERALD_BORDER = '#6ee7b7' # Emerald border

    PURPLE_ACCENT = '#7c3aed' # Purple for CRTBP / Lagrange points
    PURPLE_LIGHT = '#f5f3ff'  # Soft purple tint
    PURPLE_BORDER = '#c4b5fd' # Purple border

    # -------------------------------------------------------------
    # Main Header & Context Banner (>= 16.5 pt)
    # -------------------------------------------------------------
    fig.text(0.5, 0.963,
             "Particular Solutions and the Restricted Three-Body Problem",
             fontsize=22.5, weight='bold', color=NAVY, ha='center', va='center')

    fig.text(0.5, 0.925,
             "Euler’s and Lagrange’s particular solutions, followed by the five equilibrium points of the circular restricted problem",
             fontsize=18.5, style='italic', color=DARK_SLATE, ha='center', va='center')

    # Background axis for panel cards, headers, badges, and labels
    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')

    # Card layout parameters: 3 equal cards of width 0.304 each (tightened gaps)
    y_card = 0.024
    h_card = 0.868

    x1 = 0.024
    w1 = 0.304

    x2 = 0.346
    w2 = 0.304

    x3 = 0.668
    w3 = 0.304

    desc_euler = (
        "Three gravitating bodies remain aligned\n"
        "while revolving in circular orbits\n"
        "about their common barycenter."
    )
    desc_lagrange = (
        "Three gravitating bodies maintain\n"
        "an equilateral triangle, rotating rigidly\n"
        "about their common barycenter."
    )
    desc_crtbp = (
        "A negligible-mass third body has five\n"
        "equilibrium positions in the rotating frame:\n"
        "three collinear and two equilateral."
    )

    panels_spec = [
        (x1, w1, "1", "Euler’s Collinear Solutions", "1767 · Circular Configuration",
         BLUE_ACCENT, BLUE_LIGHT, BLUE_BORDER, desc_euler),
        (x2, w2, "2", "Lagrange’s Equilateral Solutions", "1772 · Circular Configuration",
         EMERALD_ACCENT, EMERALD_LIGHT, EMERALD_BORDER, desc_lagrange),
        (x3, w3, "3", "Circular Restricted Problem", "Equilibria in Rotating Frame (μ = 0.20)",
         PURPLE_ACCENT, PURPLE_LIGHT, PURPLE_BORDER, desc_crtbp),
    ]

    for px, pw, num, title, subtitle, acc_color, bg_tint, bdr_color, desc_text in panels_spec:
        # Card container
        card_rect = patches.FancyBboxPatch(
            (px, y_card), pw, h_card,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.4,
            zorder=1
        )
        ax_bg.add_patch(card_rect)

        # Header accent bar
        hbar_h = 0.086
        hbar_rect = patches.FancyBboxPatch(
            (px, y_card + h_card - hbar_h), pw, hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=bg_tint, edgecolor=bdr_color, linewidth=1.2,
            zorder=2
        )
        ax_bg.add_patch(hbar_rect)

        # Number Badge circle (1, 2, 3)
        badge_x = px + 0.022
        badge_y = y_card + h_card - hbar_h / 2
        badge_c = patches.Circle(
            (badge_x, badge_y), 0.016,
            facecolor=acc_color, edgecolor='none',
            zorder=3
        )
        ax_bg.add_patch(badge_c)
        ax_bg.text(badge_x, badge_y, num, fontsize=16.0, weight='bold',
                   color='#ffffff', ha='center', va='center', zorder=4)

        # Title & subtitle
        ax_bg.text(badge_x + 0.022, badge_y + 0.016, title,
                   fontsize=17.5, weight='bold', color=NAVY, va='center', zorder=4)
        ax_bg.text(badge_x + 0.022, badge_y - 0.017, subtitle,
                   fontsize=14.5, weight='bold', color='#475569', va='center', zorder=4)

        # Explanatory bottom plaque with bold 14.0 pt typography
        lbl_box_h = 0.119
        lbl_box_y = y_card + 0.018
        lbl_rect = patches.FancyBboxPatch(
            (px + 0.012, lbl_box_y), pw - 0.024, lbl_box_h,
            boxstyle="round,pad=0.0,rounding_size=0.012",
            facecolor=BG_BOX, edgecolor='#cbd5e1', linewidth=1.2,
            zorder=2
        )
        ax_bg.add_patch(lbl_rect)

        ax_bg.text(px + pw / 2, lbl_box_y + lbl_box_h / 2, desc_text,
                   fontsize=14.0, weight='bold', color='#1e293b',
                   ha='center', va='center', linespacing=1.35, zorder=3)

    # Vertical coordinates for plotting areas (matching square aspect without slack)
    y_plot = 0.187
    h_plot = 0.591

    # Shared badge halo styling for crisp label visibility
    lbl_halo = dict(boxstyle="round,pad=0.18", facecolor="#ffffff", edgecolor="none", alpha=0.88)

    # =========================================================================
    # PANEL 1: Euler's Collinear Solutions (1767)
    # =========================================================================
    ax1_w = 0.276
    ax1_x = x1 + (w1 - ax1_w) / 2
    ax1 = fig.add_axes([ax1_x, y_plot, ax1_w, h_plot], zorder=5)
    ax1.set_facecolor('#ffffff')
    ax1.set_aspect('equal')
    ax1.set_xlim(-1.65, 1.65)
    ax1.set_ylim(-1.65, 1.65)
    ax1.axis('off')

    plot_box1 = patches.FancyBboxPatch(
        (-1.64, -1.64), 3.28, 3.28,
        boxstyle="round,pad=0.0,rounding_size=0.08",
        facecolor='#ffffff', edgecolor='#e2e8f0', linewidth=1.2, zorder=0
    )
    ax1.add_patch(plot_box1)

    # Euler exact circular collinear solution: m1=2.5, m2=1.0, m3=1.8 along line at angle th
    th = np.radians(28.0)
    scale_e = 1.25
    d1 = -0.8352 * scale_e
    d2 = 0.1648 * scale_e
    d3 = 1.0684 * scale_e

    p1 = np.array([d1 * np.cos(th), d1 * np.sin(th)])
    p2 = np.array([d2 * np.cos(th), d2 * np.sin(th)])
    p3 = np.array([d3 * np.cos(th), d3 * np.sin(th)])

    R1 = abs(d1)
    R2 = abs(d2)
    R3 = abs(d3)

    # Draw concentric orbits
    circle_theta = np.linspace(0, 2*np.pi, 250)
    ax1.plot(R1 * np.cos(circle_theta), R1 * np.sin(circle_theta),
             ls='--', color='#3b82f6', lw=1.6, zorder=3)
    ax1.plot(R2 * np.cos(circle_theta), R2 * np.sin(circle_theta),
             ls='--', color='#8b5cf6', lw=1.6, zorder=3)
    ax1.plot(R3 * np.cos(circle_theta), R3 * np.sin(circle_theta),
             ls='--', color='#f59e0b', lw=1.6, zorder=3)

    # Collinear rotating axis
    ax1.plot([-1.55 * np.cos(th), 1.55 * np.cos(th)],
             [-1.55 * np.sin(th), 1.55 * np.sin(th)],
             ls='-', color='#64748b', lw=1.8, alpha=0.75, zorder=3)

    # Tangent velocity arrows (CCW rotation)
    def add_tangent_arrow(ax, R, angle_rad, color):
        cx = R * np.cos(angle_rad)
        cy = R * np.sin(angle_rad)
        vx = -np.sin(angle_rad) * 0.22
        vy = np.cos(angle_rad) * 0.22
        ax.annotate('', xy=(cx + vx, cy + vy), xytext=(cx, cy),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=2.0, mutation_scale=14),
                    zorder=6)

    add_tangent_arrow(ax1, R1, th + np.pi, '#2563eb')
    add_tangent_arrow(ax1, R2, th, '#6366f1')
    add_tangent_arrow(ax1, R3, th, '#d97706')

    # Barycenter G at (0, 0)
    ax1.plot(0, 0, marker='+', markersize=14, markeredgewidth=2.2, color='#0f172a', zorder=8)
    ax1.plot(0, 0, marker='o', markersize=6, markerfacecolor='none', markeredgecolor='#0f172a', markeredgewidth=1.8, zorder=8)
    ax1.text(0.00, -0.28, r"$\mathbf{G}$ (Barycenter)", fontsize=14.5, weight='bold', color='#0f172a',
             ha='center', va='top', bbox=lbl_halo, zorder=9)

    # Draw shaded bodies
    draw_3d_sphere(ax1, p1[0], p1[1], radius=0.14, base_color='#2563eb', zorder=10)
    draw_3d_sphere(ax1, p2[0], p2[1], radius=0.09, base_color='#6366f1', zorder=10)
    draw_3d_sphere(ax1, p3[0], p3[1], radius=0.12, base_color='#d97706', zorder=10)

    # Labels for bodies (font >= 16 pt bold)
    ax1.text(p1[0] - 0.20, p1[1] + 0.12, r"$m_1$", fontsize=17.0, weight='bold', color='#1e3a8a',
             ha='right', va='center', bbox=lbl_halo, zorder=15)
    ax1.text(p2[0] - 0.16, p2[1] + 0.18, r"$m_2$", fontsize=16.0, weight='bold', color='#3730a3',
             ha='right', va='center', bbox=lbl_halo, zorder=15)
    ax1.text(p3[0] + 0.16, p3[1] + 0.16, r"$m_3$", fontsize=17.0, weight='bold', color='#92400e',
             ha='left', va='center', bbox=lbl_halo, zorder=15)

    # Rotation indicator arc around G at radius 0.60
    r_arc1 = 0.60
    rot_arc = patches.Arc((0, 0), 2*r_arc1, 2*r_arc1, angle=0, theta1=np.degrees(th)+15, theta2=np.degrees(th)+75,
                          color='#475569', lw=1.8, ls='-', zorder=4)
    ax1.add_patch(rot_arc)
    tip_th = np.radians(np.degrees(th) + 75)
    ax1.annotate('', xy=(r_arc1 * np.cos(tip_th) - 0.05 * np.sin(tip_th), r_arc1 * np.sin(tip_th) + 0.05 * np.cos(tip_th)),
                 xytext=(r_arc1 * np.cos(tip_th), r_arc1 * np.sin(tip_th)),
                 arrowprops=dict(arrowstyle="-|>", color='#475569', lw=1.8, mutation_scale=13), zorder=4)
    ax1.text(r_arc1 * np.cos(tip_th) + 0.08, r_arc1 * np.sin(tip_th) + 0.06, r"$\omega$",
             fontsize=16.5, weight='bold', color='#334155', zorder=5)


    # =========================================================================
    # PANEL 2: Lagrange's Equilateral Solutions (1772)
    # =========================================================================
    ax2_w = 0.276
    ax2_x = x2 + (w2 - ax2_w) / 2
    ax2 = fig.add_axes([ax2_x, y_plot, ax2_w, h_plot], zorder=5)
    ax2.set_facecolor('#ffffff')
    ax2.set_aspect('equal')
    ax2.set_xlim(-1.65, 1.65)
    ax2.set_ylim(-1.65, 1.65)
    ax2.axis('off')

    plot_box2 = patches.FancyBboxPatch(
        (-1.64, -1.64), 3.28, 3.28,
        boxstyle="round,pad=0.0,rounding_size=0.08",
        facecolor='#ffffff', edgecolor='#e2e8f0', linewidth=1.2, zorder=0
    )
    ax2.add_patch(plot_box2)

    # Equilateral triangle side a = 2.05
    a_side = 2.05
    m1_val, m2_val, m3_val = 2.4, 1.8, 1.2
    P1_orig = np.array([-a_side / 2, -a_side / (2 * np.sqrt(3))])
    P2_orig = np.array([a_side / 2, -a_side / (2 * np.sqrt(3))])
    P3_orig = np.array([0.0, a_side / np.sqrt(3)])

    M_tot2 = m1_val + m2_val + m3_val
    G2 = (m1_val * P1_orig + m2_val * P2_orig + m3_val * P3_orig) / M_tot2

    rot_angle = np.radians(14.0)
    rot_mat = np.array([[np.cos(rot_angle), -np.sin(rot_angle)],
                        [np.sin(rot_angle),  np.cos(rot_angle)]])

    lp1 = rot_mat @ (P1_orig - G2)
    lp2 = rot_mat @ (P2_orig - G2)
    lp3 = rot_mat @ (P3_orig - G2)

    lR1 = np.linalg.norm(lp1)
    lR2 = np.linalg.norm(lp2)
    lR3 = np.linalg.norm(lp3)

    # Equilateral triangle polygon (subtle tint so orbits remain fully visible)
    tri_poly = patches.Polygon([lp1, lp2, lp3], closed=True,
                               facecolor='#ecfdf5', edgecolor='#059669',
                               linewidth=2.2, alpha=0.28, zorder=2)
    ax2.add_patch(tri_poly)

    # Concentric circular orbits (high contrast, zorder=4 on top of triangle fill)
    ax2.plot(lR1 * np.cos(circle_theta), lR1 * np.sin(circle_theta),
             ls='--', color='#3b82f6', lw=1.6, zorder=4)
    ax2.plot(lR2 * np.cos(circle_theta), lR2 * np.sin(circle_theta),
             ls='--', color='#059669', lw=1.7, zorder=4)
    ax2.plot(lR3 * np.cos(circle_theta), lR3 * np.sin(circle_theta),
             ls='--', color='#f59e0b', lw=1.6, zorder=4)

    # Side length annotations "a"
    mid12 = (lp1 + lp2) / 2
    mid23 = (lp2 + lp3) / 2
    mid31 = (lp3 + lp1) / 2

    ax2.text(mid12[0], mid12[1] - 0.16, r"$a$", fontsize=16.0, weight='bold',
             color='#047857', ha='center', va='top', bbox=lbl_halo, zorder=5)
    ax2.text(mid23[0] + 0.15, mid23[1] + 0.05, r"$a$", fontsize=16.0, weight='bold',
             color='#047857', ha='left', va='center', bbox=lbl_halo, zorder=5)
    ax2.text(mid31[0] - 0.15, mid31[1] + 0.05, r"$a$", fontsize=16.0, weight='bold',
             color='#047857', ha='right', va='center', bbox=lbl_halo, zorder=5)

    # Barycenter G at (0, 0)
    ax2.plot(0, 0, marker='+', markersize=14, markeredgewidth=2.2, color='#0f172a', zorder=8)
    ax2.plot(0, 0, marker='o', markersize=6, markerfacecolor='none', markeredgecolor='#0f172a', markeredgewidth=1.8, zorder=8)
    ax2.text(0.00, -0.28, r"$\mathbf{G}$ (Barycenter)", fontsize=14.5, weight='bold', color='#0f172a',
             ha='center', va='top', bbox=lbl_halo, zorder=9)

    # Tangent velocity arrows (CCW rotation)
    ang1 = np.arctan2(lp1[1], lp1[0])
    ang2 = np.arctan2(lp2[1], lp2[0])
    ang3 = np.arctan2(lp3[1], lp3[0])

    add_tangent_arrow(ax2, lR1, ang1, '#2563eb')
    add_tangent_arrow(ax2, lR2, ang2, '#059669')
    add_tangent_arrow(ax2, lR3, ang3, '#d97706')

    # Draw shaded bodies
    draw_3d_sphere(ax2, lp1[0], lp1[1], radius=0.14, base_color='#2563eb', zorder=10)
    draw_3d_sphere(ax2, lp2[0], lp2[1], radius=0.12, base_color='#059669', zorder=10)
    draw_3d_sphere(ax2, lp3[0], lp3[1], radius=0.10, base_color='#d97706', zorder=10)

    # Labels for bodies (font >= 16 pt bold)
    ax2.text(lp1[0] - 0.20, lp1[1] - 0.12, r"$m_1$", fontsize=17.0, weight='bold', color='#1e3a8a',
             ha='right', va='center', bbox=lbl_halo, zorder=15)
    ax2.text(lp2[0] + 0.16, lp2[1] - 0.12, r"$m_2$", fontsize=17.0, weight='bold', color='#065f46',
             ha='left', va='center', bbox=lbl_halo, zorder=15)
    ax2.text(lp3[0], lp3[1] + 0.20, r"$m_3$", fontsize=17.0, weight='bold', color='#92400e',
             ha='center', va='bottom', bbox=lbl_halo, zorder=15)

    # Rotation indicator arc around G at radius 0.55
    r_arc2 = 0.55
    rot_arc2 = patches.Arc((0, 0), 2*r_arc2, 2*r_arc2, angle=0, theta1=65, theta2=125,
                           color='#475569', lw=1.8, ls='-', zorder=4)
    ax2.add_patch(rot_arc2)
    tip_th2 = np.radians(125)
    ax2.annotate('', xy=(r_arc2 * np.cos(tip_th2) - 0.05 * np.sin(tip_th2), r_arc2 * np.sin(tip_th2) + 0.05 * np.cos(tip_th2)),
                 xytext=(r_arc2 * np.cos(tip_th2), r_arc2 * np.sin(tip_th2)),
                 arrowprops=dict(arrowstyle="-|>", color='#475569', lw=1.8, mutation_scale=13), zorder=4)
    ax2.text(r_arc2 * np.cos(tip_th2) - 0.06, r_arc2 * np.sin(tip_th2) + 0.08, r"$\omega$",
             fontsize=16.5, weight='bold', color='#334155', zorder=5)


    # =========================================================================
    # PANEL 3: Circular Restricted Three-Body Problem (CRTBP)
    # =========================================================================
    ax3_w = 0.276
    ax3_x = x3 + (w3 - ax3_w) / 2
    ax3 = fig.add_axes([ax3_x, y_plot, ax3_w, h_plot], zorder=5)
    ax3.set_facecolor('#ffffff')
    ax3.set_aspect('equal')
    ax3.set_xlim(-1.65, 1.65)
    ax3.set_ylim(-1.65, 1.65)
    ax3.axis('off')

    plot_box3 = patches.FancyBboxPatch(
        (-1.64, -1.64), 3.28, 3.28,
        boxstyle="round,pad=0.0,rounding_size=0.08",
        facecolor='#ffffff', edgecolor='#e2e8f0', linewidth=1.2, zorder=0
    )
    ax3.add_patch(plot_box3)

    # Exact physical parameters for mass ratio mu = 0.20
    mu = 0.20
    M1_pos = np.array([-mu, 0.0])
    M2_pos = np.array([1.0 - mu, 0.0])

    def dOmega_dx(x):
        r1 = abs(x + mu)
        r2 = abs(x - (1.0 - mu))
        return x - (1.0 - mu) * (x + mu) / (r1**3) - mu * (x - (1.0 - mu)) / (r2**3)

    x_L1 = brentq(dOmega_dx, -mu + 1e-4, 1.0 - mu - 1e-4)
    x_L2 = brentq(dOmega_dx, 1.0 - mu + 1e-4, 2.5)
    x_L3 = brentq(dOmega_dx, -2.5, -mu - 1e-4)

    L1_pos = np.array([x_L1, 0.0])
    L2_pos = np.array([x_L2, 0.0])
    L3_pos = np.array([x_L3, 0.0])
    L4_pos = np.array([0.5 - mu, np.sqrt(3) / 2])
    L5_pos = np.array([0.5 - mu, -np.sqrt(3) / 2])

    # Effective potential contours in rotating frame
    grid_x = np.linspace(-1.60, 1.60, 260)
    grid_y = np.linspace(-1.60, 1.60, 260)
    GX, GY = np.meshgrid(grid_x, grid_y)
    GR1 = np.sqrt((GX + mu)**2 + GY**2)
    GR2 = np.sqrt((GX - (1.0 - mu))**2 + GY**2)

    # Jacobi effective potential
    Omega = 0.5 * (GX**2 + GY**2) + (1.0 - mu) / np.maximum(GR1, 0.08) + mu / np.maximum(GR2, 0.06)

    C_L1 = 0.5 * x_L1**2 + (1.0 - mu) / abs(x_L1 + mu) + mu / abs(x_L1 - (1.0 - mu))
    C_L2 = 0.5 * x_L2**2 + (1.0 - mu) / abs(x_L2 + mu) + mu / abs(x_L2 - (1.0 - mu))
    C_L3 = 0.5 * x_L3**2 + (1.0 - mu) / abs(x_L3 + mu) + mu / abs(x_L3 - (1.0 - mu))
    C_L4 = 0.5 * (L4_pos[0]**2 + L4_pos[1]**2) + (1.0 - mu) / 1.0 + mu / 1.0

    # Background contours
    bg_levels = [
        C_L4 * 0.94, C_L4 * 0.97, C_L4 * 1.00,
        C_L3, C_L2,
        C_L1 * 1.06, C_L1 * 1.18, C_L1 * 1.35
    ]
    ax3.contour(GX, GY, Omega, levels=bg_levels, colors='#cbd5e1', linewidths=0.85, alpha=0.60, zorder=2)
    # Highlight critical Roche lobe passing through L1
    ax3.contour(GX, GY, Omega, levels=[C_L1], colors='#94a3b8', linewidths=1.2, alpha=0.85, zorder=2)

    # Collinear axis (connecting L3, M1, L1, M2, L2)
    ax3.plot([-1.55, 1.55], [0, 0], ls='--', color='#94a3b8', lw=1.4, zorder=3)

    # Equilateral triangles to L4 and L5 (strictly equilateral with side 1.0)
    ax3.plot([M1_pos[0], L4_pos[0]], [M1_pos[1], L4_pos[1]], ls=':', color='#8b5cf6', lw=1.4, zorder=3)
    ax3.plot([M2_pos[0], L4_pos[0]], [M2_pos[1], L4_pos[1]], ls=':', color='#8b5cf6', lw=1.4, zorder=3)

    ax3.plot([M1_pos[0], L5_pos[0]], [M1_pos[1], L5_pos[1]], ls=':', color='#8b5cf6', lw=1.4, zorder=3)
    ax3.plot([M2_pos[0], L5_pos[0]], [M2_pos[1], L5_pos[1]], ls=':', color='#8b5cf6', lw=1.4, zorder=3)

    # Barycenter G at (0, 0)
    ax3.plot(0, 0, marker='+', markersize=14, markeredgewidth=2.2, color='#0f172a', zorder=8)
    ax3.plot(0, 0, marker='o', markersize=6, markerfacecolor='none', markeredgecolor='#0f172a', markeredgewidth=1.8, zorder=8)
    ax3.text(0.00, -0.28, r"$\mathbf{G}$", fontsize=15.0, weight='bold', color='#0f172a',
             ha='center', va='top', bbox=lbl_halo, zorder=9)

    # Draw massive primaries M1 and M2
    draw_3d_sphere(ax3, M1_pos[0], M1_pos[1], radius=0.16, base_color='#1d4ed8', zorder=10)
    draw_3d_sphere(ax3, M2_pos[0], M2_pos[1], radius=0.10, base_color='#0284c7', zorder=10)

    ax3.text(M1_pos[0], M1_pos[1] + 0.22, r"$M_1$", fontsize=17.0, weight='bold', color='#1e3a8a',
             ha='center', va='bottom', bbox=lbl_halo, zorder=15)
    ax3.text(M2_pos[0], M2_pos[1] + 0.16, r"$M_2$", fontsize=16.0, weight='bold', color='#0369a1',
             ha='center', va='bottom', bbox=lbl_halo, zorder=15)

    # Draw the Five Lagrange Points
    lagrange_pts = [
        (L1_pos, r"$L_1$", (0.00, 0.16), 'center', 'bottom'),
        (L2_pos, r"$L_2$", (0.16, 0.00), 'left', 'center'),
        (L3_pos, r"$L_3$", (-0.16, 0.00), 'right', 'center'),
        (L4_pos, r"$L_4$", (0.00, 0.16), 'center', 'bottom'),
        (L5_pos, r"$L_5$", (0.00, -0.16), 'center', 'top'),
    ]

    for pt, label, offset, ha, va in lagrange_pts:
        ax3.plot(pt[0], pt[1], marker='D', markersize=9.5, markerfacecolor='#7c3aed',
                 markeredgecolor='#ffffff', markeredgewidth=1.6, zorder=12)
        ax3.text(pt[0] + offset[0], pt[1] + offset[1], label,
                 fontsize=16.5, weight='bold', color='#6d28d9', ha=ha, va=va,
                 bbox=lbl_halo, zorder=15)


    # Save final publication-quality image
    plt.savefig(output_path, dpi=240, facecolor='#ffffff', edgecolor='none')
    plt.close()
    print(f"[OK] Refined infographic saved to: {output_path}")


if __name__ == "__main__":
    create_figure()
