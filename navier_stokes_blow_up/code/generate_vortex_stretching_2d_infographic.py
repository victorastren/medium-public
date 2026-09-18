from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "vortex_stretching_2d_vanishing.png"

#!/usr/bin/env python3
"""
Generate infographic for section:
"Why Two and Three Dimensions Behave Differently"

Title: Why the Vortex-Stretching Term Vanishes in Two Dimensions
Subtitle: In 2D incompressible flow, vorticity points out of the plane while the velocity field has no variation in that direction.

Layout:
- Two perfectly symmetric panels with matching borders, headers, and bottom bounds.
- Left Panel: Geometry of a 2D Flow (tilted x-y plane with in-plane velocity swirl and perpendicular vorticity omega)
- Right Panel: Algebraic derivation showing step-by-step why (omega . nabla)u = 0, with large focal boxed zero.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

def create_2d_vanishing_stretching_figure(out_path=None):
    if out_path is None:
        out_path = DEFAULT_OUT
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(16, 9.2), dpi=240, facecolor='#070b12')

    # Color Palette (matching dark mathematical analysis theme)
    CANVAS_BG   = '#070b12'
    PANEL_BG    = '#0c1322'
    CARD_BG     = '#101828'
    BORDER_COL  = '#1e293b'
    TEXT_TITLE  = '#f8fafc'
    TEXT_SUB    = '#94a3b8'

    # Feature Accents
    CYAN_COL    = '#38bdf8'  # Velocity in plane
    GOLD_COL    = '#fbbf24'  # Vorticity perpendicular to plane
    EMERALD_COL = '#34d399'  # Vanishing condition (du/dz = 0)
    PURPLE_COL  = '#c084fc'  # Stretching operator

    # -------------------------------------------------------------------------
    # MAIN TITLE BANNER (Normalized coordinates at top)
    # -------------------------------------------------------------------------
    fig.text(0.50, 0.948, "WHY THE VORTEX-STRETCHING TERM VANISHES IN TWO DIMENSIONS",
             fontsize=18.0, fontweight='bold', color=TEXT_TITLE, ha='center', va='center')
    fig.text(0.50, 0.912,
             r"In 2D incompressible flow, vorticity points out of the plane while the velocity field has no variation in that direction.",
             fontsize=12.8, color='#cbd5e1', ha='center', va='center')

    # -------------------------------------------------------------------------
    # TWO SYMMETRIC PANELS: EXACT MATCHING DIMENSIONS & POSITIONS
    # -------------------------------------------------------------------------
    panel_y = 0.050
    panel_h = 0.825
    panel_w = 0.445
    left_x  = 0.040
    right_x = 0.515

    # =========================================================================
    # LEFT PANEL: GEOMETRY OF A 2D FLOW
    # =========================================================================
    ax_left = fig.add_axes([left_x, panel_y, panel_w, panel_h])
    ax_left.set_facecolor(PANEL_BG)
    for s in ax_left.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.4)
    ax_left.set_xlim(-4.2, 4.2)
    ax_left.set_ylim(-3.5, 3.5)
    ax_left.set_xticks([])
    ax_left.set_yticks([])

    # Header
    ax_left.text(0.045, 0.955, "Geometry of a 2D Flow",
                 transform=ax_left.transAxes, fontsize=15.0, fontweight='bold',
                 color=TEXT_TITLE, va='top')
    ax_left.text(0.045, 0.905, r"Velocity $\mathbf{u}$ lies entirely in the plane; vorticity $\boldsymbol{\omega}$ points perpendicular.",
                 transform=ax_left.transAxes, fontsize=11.6,
                 color='#94a3b8', va='top')

    # Oblique 3D projection basis vectors
    ox, oy = -0.25, -0.65
    ux, uy = 2.45, -0.55   # x-direction on screen
    vx, vy = 1.25, 0.85    # y-direction on screen
    wx, wy = 0.0, 2.35     # z-direction on screen (straight up)

    # Draw tilted plane (parallelogram)
    p_bl = (ox - ux - vx, oy - uy - vy)
    p_br = (ox + ux - vx, oy + uy - vy)
    p_tr = (ox + ux + vx, oy + uy + vy)
    p_tl = (ox - ux + vx, oy - uy + vy)

    plane_poly = patches.Polygon([p_bl, p_br, p_tr, p_tl],
                                 closed=True, facecolor='#0b192e', edgecolor='#1e3a5f',
                                 linewidth=1.8, alpha=0.92, zorder=2)
    ax_left.add_patch(plane_poly)

    # Internal grid lines on plane
    n_grid = 6
    for i in range(1, n_grid):
        f = -1.0 + 2.0 * (i / n_grid)
        start_x = (ox - ux + f * vx, oy - uy + f * vy)
        end_x   = (ox + ux + f * vx, oy + uy + f * vy)
        ax_left.plot([start_x[0], end_x[0]], [start_x[1], end_x[1]],
                     color='#172554', linewidth=0.9, linestyle='--', zorder=3)
        start_y = (ox + f * ux - vx, oy + f * uy - vy)
        end_y   = (ox + f * ux + vx, oy + f * uy + vy)
        ax_left.plot([start_y[0], end_y[0]], [start_y[1], end_y[1]],
                     color='#172554', linewidth=0.9, linestyle='--', zorder=3)

    # Axis arrows on the plane
    # x-axis
    ax_left.annotate('', xy=(ox + ux + 0.40, oy + uy - 0.09), xytext=(ox, oy),
                     arrowprops=dict(arrowstyle='->', color='#64748b', lw=1.5), zorder=4)
    ax_left.text(ox + ux + 0.52, oy + uy - 0.12, "x", color='#94a3b8', fontsize=12.5, fontweight='bold', zorder=5)

    # y-axis
    ax_left.annotate('', xy=(ox + vx + 0.25, oy + vy + 0.17), xytext=(ox, oy),
                     arrowprops=dict(arrowstyle='->', color='#64748b', lw=1.5), zorder=4)
    ax_left.text(ox + vx + 0.35, oy + vy + 0.24, "y", color='#94a3b8', fontsize=12.5, fontweight='bold', zorder=5)

    # Plane label at lower edge
    ax_left.text(p_br[0] - 0.2, p_br[1] + 0.25, r"$(x, y)\text{ Flow Plane}$",
                 color='#38bdf8', fontsize=11.4, fontweight='bold', ha='right', zorder=5)

    # Swirling velocity vectors on plane
    radii = [0.45, 0.85]
    n_arrows = [6, 8]
    for r_idx, (r, n_a) in enumerate(zip(radii, n_arrows)):
        angles = np.linspace(0, 2*np.pi, n_a, endpoint=False) + (0.25 if r_idx==1 else 0.0)
        for theta in angles:
            xi = r * np.cos(theta)
            eta = r * np.sin(theta)
            scale = 0.24
            dxi = -np.sin(theta) * scale
            deta = np.cos(theta) * scale

            sx = ox + xi * (ux / 2.0) + eta * (vx / 1.1)
            sy = oy + xi * (uy / 2.0) + eta * (vy / 1.1)
            dsx = dxi * (ux / 2.0) + deta * (vx / 1.1)
            dsy = dxi * (uy / 2.0) + deta * (vy / 1.1)

            arrow = FancyArrowPatch((sx, sy), (sx + dsx, sy + dsy),
                                    arrowstyle='-|>', color=CYAN_COL,
                                    mutation_scale=11, lw=1.8, zorder=6)
            ax_left.add_patch(arrow)

    # Velocity swirl label (placed at upper left of swirl)
    ax_left.text(ox - 1.45, oy + 0.70, r"$\mathbf{u} = (u, v, 0)$" + "\n" + r"(swirling in plane)",
                 color=CYAN_COL, fontsize=11.8, fontweight='bold', ha='center', va='center', zorder=6)

    # Right-angle indicator at base of vertical axis
    sq_size = 0.24
    dx_sq = sq_size * (ux / 2.45)
    dy_sq = sq_size * (uy / 2.45)
    dz_sq = sq_size * 0.95
    sq_x = [ox, ox + dx_sq, ox + dx_sq, ox]
    sq_y = [oy, oy + dy_sq, oy + dy_sq + dz_sq, oy + dz_sq]
    ax_left.plot(sq_x, sq_y, color='#64748b', lw=1.2, zorder=4)

    # Vertical arrow for vorticity omega
    z_arrow = FancyArrowPatch((ox, oy), (ox + wx, oy + wy),
                              arrowstyle='-|>', color=GOLD_COL,
                              mutation_scale=22, lw=3.8, zorder=8)
    ax_left.add_patch(z_arrow)

    # Glow effect for omega arrow
    z_arrow_glow = FancyArrowPatch((ox, oy), (ox + wx, oy + wy),
                                   arrowstyle='-|>', color=GOLD_COL,
                                   mutation_scale=22, lw=7.5, alpha=0.25, zorder=7)
    ax_left.add_patch(z_arrow_glow)

    # z-axis dashed extension below plane
    ax_left.plot([ox, ox], [oy - 0.45, oy], color='#64748b', linestyle=':', lw=1.2, zorder=3)

    # Vorticity Label
    ax_left.text(ox + 0.18, oy + wy - 0.12, r"$\boldsymbol{\omega} = (0, 0, \omega)$",
                 color=GOLD_COL, fontsize=14.0, fontweight='bold', va='bottom', zorder=9)
    ax_left.text(ox + 0.18, oy + wy - 0.42, "(perpendicular to plane)",
                 color='#fde68a', fontsize=11.2, va='top', zorder=9)

    # 3 Summary Cards at bottom of Left Panel with clear gaps and vertical separators
    card_w = 2.26
    card_h = 0.88
    cards_data = [
        (-2.72, -2.82, "Velocity Field", r"$\mathbf{u} = (u, v, 0)$", "Lies strictly in plane", CYAN_COL),
        (0.0,   -2.82, "Vorticity Field", r"$\boldsymbol{\omega} = (0, 0, \omega)$", r"Points purely along $z$", GOLD_COL),
        (2.72,  -2.82, r"No $z$-Dependence", r"$\partial\mathbf{u}/\partial z = \mathbf{0}$", r"Velocity independent of $z$", EMERALD_COL)
    ]
    for cx, cy, title, formula, subtext, col in cards_data:
        box = FancyBboxPatch((cx - card_w/2, cy - card_h/2), card_w, card_h,
                             boxstyle="round,pad=0.04,rounding_size=0.12",
                             facecolor=CARD_BG, edgecolor=col, linewidth=1.3, zorder=10)
        ax_left.add_patch(box)
        ax_left.text(cx, cy + 0.25, title, color=col, fontsize=10.4, fontweight='bold', ha='center', va='center', zorder=11)
        ax_left.text(cx, cy - 0.02, formula, color=TEXT_TITLE, fontsize=11.4, fontweight='bold', ha='center', va='center', zorder=11)
        ax_left.text(cx, cy - 0.27, subtext, color='#cbd5e1', fontsize=9.2, ha='center', va='center', zorder=11)

    # Vertical gap separators between the 3 bottom cards
    sep_y_bot = -2.82 - 0.36
    sep_y_top = -2.82 + 0.36
    ax_left.plot([-1.36, -1.36], [sep_y_bot, sep_y_top], color='#334155', lw=1.5, zorder=9)
    ax_left.plot([1.36, 1.36], [sep_y_bot, sep_y_top], color='#334155', lw=1.5, zorder=9)


    # =========================================================================
    # RIGHT PANEL: THE STRETCHING TERM VANISHES
    # =========================================================================
    ax_right = fig.add_axes([right_x, panel_y, panel_w, panel_h])
    ax_right.set_facecolor(PANEL_BG)
    for s in ax_right.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.4)
    ax_right.set_xlim(0, 100)
    ax_right.set_ylim(0, 100)
    ax_right.set_xticks([])
    ax_right.set_yticks([])

    # Header (matching left panel typography and placement)
    ax_right.text(4.5, 95.5, "The Stretching Term Vanishes",
                  fontsize=15.0, fontweight='bold', color=TEXT_TITLE, va='top')
    ax_right.text(4.5, 90.5, r"Direct evaluation of the directional derivative $(\boldsymbol{\omega}\cdot\nabla)\mathbf{u}$",
                  fontsize=11.6, color='#94a3b8', va='top')

    # Step 1 Card: Starting Term
    s1 = FancyBboxPatch((4.5, 72.5), 91.0, 14.5,
                        boxstyle="round,pad=0.3,rounding_size=1.2",
                        facecolor=CARD_BG, edgecolor='#334155', linewidth=1.2, zorder=2)
    ax_right.add_patch(s1)
    ax_right.text(8.0, 82.5, "1. Stretching Term in the Vorticity Equation:",
                  fontsize=11.5, color='#cbd5e1', fontweight='bold', va='center', zorder=3)
    ax_right.text(50.0, 77.0, r"$(\boldsymbol{\omega}\cdot\nabla)\mathbf{u}$",
                  fontsize=15.5, color=PURPLE_COL, fontweight='bold', ha='center', va='center', zorder=3)

    # Arrow 1
    ax_right.text(50.0, 69.8, "▼", fontsize=12, color='#64748b', ha='center', va='center', zorder=3)

    # Step 2 Card: Expand Directional Derivative
    s2 = FancyBboxPatch((4.5, 50.0), 91.0, 17.5,
                        boxstyle="round,pad=0.3,rounding_size=1.2",
                        facecolor=CARD_BG, edgecolor='#334155', linewidth=1.2, zorder=2)
    ax_right.add_patch(s2)
    ax_right.text(8.0, 63.5, "2. Evaluate in 2D:",
                  fontsize=11.5, color='#cbd5e1', fontweight='bold', va='center', zorder=3)
    ax_right.text(50.0, 55.5,
                  r"$= (0, 0, \omega) \cdot \left( \frac{\partial}{\partial x},\, \frac{\partial}{\partial y},\, \frac{\partial}{\partial z} \right) \mathbf{u} " +
                  r"= \omega\,\frac{\partial\mathbf{u}}{\partial z}$",
                  fontsize=13.8, color=TEXT_TITLE, ha='center', va='center', zorder=3)

    # Arrow 2
    ax_right.text(50.0, 47.3, "▼", fontsize=12, color='#64748b', ha='center', va='center', zorder=3)

    # Step 3 Card: 2D Flow Constraint (du/dz = 0)
    s3 = FancyBboxPatch((4.5, 32.5), 91.0, 13.0,
                        boxstyle="round,pad=0.3,rounding_size=1.2",
                        facecolor='#064e3b', edgecolor=EMERALD_COL, linewidth=1.4, zorder=2)
    ax_right.add_patch(s3)
    ax_right.text(8.0, 41.0, r"3. No variation along $z$:",
                  fontsize=11.5, color='#a7f3d0', fontweight='bold', va='center', zorder=3)
    ax_right.text(50.0, 36.0,
                  r"$\frac{\partial\mathbf{u}}{\partial z} = \mathbf{0} \quad \Longrightarrow \quad \omega\,\frac{\partial\mathbf{u}}{\partial z} = \mathbf{0}$",
                  fontsize=13.5, color='#34d399', fontweight='bold', ha='center', va='center', zorder=3)

    # Arrow 3
    ax_right.text(50.0, 30.0, "▼", fontsize=12, color='#64748b', ha='center', va='center', zorder=3)

    # Step 4: THE FOCAL POINT (Large Boxed Zero)
    s4_glow = FancyBboxPatch((9.0, 12.5), 82.0, 15.5,
                             boxstyle="round,pad=0.4,rounding_size=1.5",
                             facecolor='#0f172a', edgecolor=EMERALD_COL, linewidth=3.2, zorder=3)
    ax_right.add_patch(s4_glow)

    # Inner highlight box
    s4_inner = FancyBboxPatch((9.8, 13.3), 80.4, 13.9,
                              boxstyle="round,pad=0.3,rounding_size=1.3",
                              facecolor='#022c22', edgecolor='#10b981', linewidth=1.5, alpha=0.90, zorder=4)
    ax_right.add_patch(s4_inner)

    ax_right.text(50.0, 20.2,
                  r"$(\boldsymbol{\omega}\cdot\nabla)\mathbf{u} = \mathbf{0}$",
                  fontsize=25.5, color='#6ee7b7', fontweight='bold', ha='center', va='center', zorder=5)

    # Bottom Conclusion Banner
    ax_right.text(50.0, 8.0, "No vortex stretching in 2D",
                  fontsize=13.0, fontweight='bold', color=TEXT_TITLE, ha='center', va='center', zorder=5)
    ax_right.text(50.0, 4.0,
                  r"No self-amplification through vortex stretching $\cdot$ (3D: $(\boldsymbol{\omega}\cdot\nabla)\mathbf{u}$ need not vanish)",
                  fontsize=10.8, color='#cbd5e1', ha='center', va='center', zorder=5)

    # Save output
    # out_path is provided via function argument
    plt.savefig(out_path, dpi=240, bbox_inches='tight', facecolor=CANVAS_BG, edgecolor='none')
    plt.close()
    print(f"[OK] Generated 2D Vanishing Stretching Infographic: {out_path}")
    return out_path

generate_vortex_stretching_2d_infographic = create_2d_vanishing_stretching_figure

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    create_2d_vanishing_stretching_figure(target)
