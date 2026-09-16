#!/usr/bin/env python3
"""
Generate Infographic: Secular Normal Modes of the Planetary System
Visualizing Lagrange-Laplace Secular Theory:
- Panel A: Mode 1 (Aligned Perihelia, joint precession at frequency g1)
- Panel B: Mode 2 (Anti-aligned Perihelia, joint precession at frequency g2)
- Bottom Strip: Compact mathematical bridge from dz/dt = iAz to collective eigenmodes.

Tailored for Medium's 680px width (rendered at 280 DPI) with dark astrophysics aesthetic.
"""

from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# -------------------------------------------------------------------------
# PALETTE & AESTHETICS (Astrophysics Dark Theme)
# -------------------------------------------------------------------------
BG_COLOR       = "#0a0e17"       # Deep cosmic dark
BG_PANEL       = "#111726"       # Panel background
BG_CARD        = "#0d131f"       # Bottom card background
BORDER         = "#1e293b"       # Subtle border
BORDER_LIGHT   = "#334155"       # Card border highlight
TEXT_TITLE     = "#f8fafc"       # Bright white
TEXT_SUB       = "#94a3b8"       # Cool slate grey
TEXT_BODY      = "#cbd5e1"       # Light grey text

SUN_CORE       = "#fbbf24"       # Warm yellow/gold
SUN_GLOW       = "#f59e0b"       # Amber glow

INNER_ORBIT    = "#38bdf8"       # Bright Cyan (Inner Planet)
INNER_GLOW     = "#0284c7"       # Deep Cyan
OUTER_ORBIT    = "#f43f5e"       # Bright Coral/Rose (Outer Planet)
OUTER_GLOW     = "#e11d48"       # Deep Coral

GOLD_ACCENT    = "#fbbf24"       # Highlight gold (angles, labels)
EMERALD_ACCENT = "#34d399"       # Emerald green highlight

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'mathtext.fontset': 'dejavusans',
    'text.color': TEXT_BODY,
    'axes.labelcolor': TEXT_BODY,
    'xtick.color': TEXT_SUB,
    'ytick.color': TEXT_SUB,
})

def get_ellipse_coords(a, e, varpi, n_pts=400):
    """Return (x, y) coordinates of an ellipse with focus at the origin."""
    nu = np.linspace(0, 2 * np.pi, n_pts)
    r = a * (1.0 - e**2) / (1.0 + e * np.cos(nu))
    phi = nu + varpi
    return r * np.cos(phi), r * np.sin(phi)

def get_perihelion_pos(a, e, varpi):
    """Return coordinates of perihelion (closest approach to focus)."""
    r_peri = a * (1.0 - e)
    return r_peri * np.cos(varpi), r_peri * np.sin(varpi)

def create_secular_normal_modes_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_IMAGES_DIR / "secular_normal_modes.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 12 x 7.8 inches @ 280 DPI gives a high-resolution, beautifully proportioned image
    fig = plt.figure(figsize=(12.0, 7.8), dpi=280, facecolor=BG_COLOR)
    
    # Header Titles (Overall Figure)
    fig.text(0.05, 0.952, "Secular Normal Modes of the Planetary System",
             fontsize=16.5, fontweight='bold', color=TEXT_TITLE, va='top')
    fig.text(0.05, 0.910,
             "Planetary orbits do not evolve independently; gravitational coupling organizes their long-term variation into collective precessing modes",
             fontsize=10.2, color=TEXT_SUB, va='top')

    # Balanced dimensions so orbits sit with comfortable breathing room
    a1 = 0.78
    e1 = 0.32
    a2 = 1.45
    e2 = 0.28
    
    # Panel setup: [left, bottom, width, height]
    # Panel A: Aligned Mode (Left)
    ax_a = fig.add_axes([0.05, 0.205, 0.435, 0.665], facecolor=BG_PANEL)
    # Panel B: Anti-Aligned Mode (Right)
    ax_b = fig.add_axes([0.515, 0.205, 0.435, 0.665], facecolor=BG_PANEL)
    
    panels = [
        (ax_a, "Mode 1: Aligned Secular Mode",
         np.radians(28.0), np.radians(28.0),
         r"$g_1$"),
        (ax_b, "Mode 2: Anti-Aligned Secular Mode",
         np.radians(28.0), np.radians(28.0 + 180.0),
         r"$g_2$")
    ]
    
    for ax, title_str, varpi1, varpi2, g_sym in panels:
        ax.set_aspect('equal')
        # Centered coordinate frame with generous margin around aphelion (max r ≈ 1.86)
        ax.set_xlim(-2.55, 2.55)
        ax.set_ylim(-2.50, 2.50)
        ax.set_xticks([])
        ax.set_yticks([])
        
        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)
            spine.set_linewidth(1.3)
            
        # Subtle reference circular guides
        for r_grid in [0.78, 1.45]:
            grid_c = plt.Circle((0, 0), r_grid, color=BORDER, fill=False,
                                linestyle=':', linewidth=0.7, alpha=0.5, zorder=1)
            ax.add_patch(grid_c)

        # Panel Header: Clean, uncluttered title and precession rate badge
        ax.text(0.045, 0.950, title_str, transform=ax.transAxes,
                fontsize=12.5, fontweight='bold', color=TEXT_TITLE, va='top')
        
        ax.text(0.955, 0.950, f"Precession: {g_sym}", transform=ax.transAxes,
                fontsize=10.5, fontweight='bold', color=GOLD_ACCENT,
                ha='right', va='top')

        # -----------------------------------------------------------------
        # 1. ORBIT 1 (Inner Planet - Cyan)
        # -----------------------------------------------------------------
        x1, y1 = get_ellipse_coords(a1, e1, varpi1)
        ax.plot(x1, y1, color=INNER_GLOW, lw=3.0, alpha=0.30, zorder=2)
        ax.plot(x1, y1, color=INNER_ORBIT, lw=1.6, alpha=0.95, zorder=3)
        
        # -----------------------------------------------------------------
        # 2. ORBIT 2 (Outer Planet - Coral)
        # -----------------------------------------------------------------
        x2, y2 = get_ellipse_coords(a2, e2, varpi2)
        ax.plot(x2, y2, color=OUTER_GLOW, lw=3.0, alpha=0.30, zorder=2)
        ax.plot(x2, y2, color=OUTER_ORBIT, lw=1.6, alpha=0.95, zorder=3)

        # -----------------------------------------------------------------
        # 3. ECCENTRICITY VECTORS & APSE LINES
        # -----------------------------------------------------------------
        # Inner eccentricity vector
        px1, py1 = get_perihelion_pos(a1, e1, varpi1)
        ax.plot([0, px1 * 1.10], [0, py1 * 1.10], color=INNER_ORBIT,
                linestyle='--', lw=1.0, alpha=0.6, zorder=4)
        ax.annotate('', xy=(px1, py1), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=INNER_ORBIT,
                                    lw=1.6, mutation_scale=11), zorder=5)
        ax.scatter([px1], [py1], color=INNER_ORBIT, s=28, zorder=6)
        
        # Outer eccentricity vector
        px2, py2 = get_perihelion_pos(a2, e2, varpi2)
        ax.plot([0, px2 * 1.08], [0, py2 * 1.08], color=OUTER_ORBIT,
                linestyle='--', lw=1.0, alpha=0.6, zorder=4)
        ax.annotate('', xy=(px2, py2), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=OUTER_ORBIT,
                                    lw=1.6, mutation_scale=11), zorder=5)
        ax.scatter([px2], [py2], color=OUTER_ORBIT, s=28, zorder=6)
        
        # Explicit labeling as eccentricity vectors e1 and e2 with background bbox for crisp readability
        bbox_style = dict(boxstyle="round,pad=0.20", facecolor=BG_PANEL, edgecolor="none", alpha=0.90)
        if ax == ax_a:
            # Mode 1: Both vectors in same quadrant (~28 deg)
            # e1 label: safely inside top half of inner ellipse
            ax.text(0.00, 0.38, r"$\mathbf{e}_1$ — eccentricity vector",
                    fontsize=7.8, color=INNER_ORBIT, fontweight='bold',
                    ha='center', va='center', zorder=12, bbox=bbox_style)
            # e2 label: balanced placement clear of red dot and panel border
            ax.text(1.02, 0.54, r"$\mathbf{e}_2$ — eccentricity vector",
                    fontsize=7.4, color=OUTER_ORBIT, fontweight='bold',
                    ha='left', va='center', zorder=12, bbox=bbox_style)
        else:
            # Mode 2: Opposed vectors
            # e1 label: safely inside top half of inner ellipse
            ax.text(0.00, 0.38, r"$\mathbf{e}_1$ — eccentricity vector",
                    fontsize=7.8, color=INNER_ORBIT, fontweight='bold',
                    ha='center', va='center', zorder=12, bbox=bbox_style)
            # e2 label: balanced placement clear of red dot and panel border
            ax.text(-1.02, -0.54, r"$\mathbf{e}_2$ — eccentricity vector",
                    fontsize=7.4, color=OUTER_ORBIT, fontweight='bold',
                    ha='right', va='center', zorder=12, bbox=bbox_style)

        # -----------------------------------------------------------------
        # 4. PLANET POSITION MARKERS
        # -----------------------------------------------------------------
        # Inner planet
        nu_p1 = np.radians(88.0)
        r_p1 = a1 * (1.0 - e1**2) / (1.0 + e1 * np.cos(nu_p1))
        phi_p1 = nu_p1 + varpi1
        pl1_x, pl1_y = r_p1 * np.cos(phi_p1), r_p1 * np.sin(phi_p1)
        ax.scatter([pl1_x], [pl1_y], color=INNER_ORBIT, s=38, edgecolors=BG_PANEL, lw=1.0, zorder=8)
        ax.text(pl1_x + 0.08, pl1_y + 0.08, "Planet 1", fontsize=7.6, color=TEXT_BODY, zorder=9)

        # Outer planet
        nu_p2 = np.radians(142.0)
        r_p2 = a2 * (1.0 - e2**2) / (1.0 + e2 * np.cos(nu_p2))
        phi_p2 = nu_p2 + varpi2
        pl2_x, pl2_y = r_p2 * np.cos(phi_p2), r_p2 * np.sin(phi_p2)
        ax.scatter([pl2_x], [pl2_y], color=OUTER_ORBIT, s=48, edgecolors=BG_PANEL, lw=1.0, zorder=8)
        ax.text(pl2_x + 0.08, pl2_y + 0.08, "Planet 2", fontsize=7.6, color=TEXT_BODY, zorder=9)

        # -----------------------------------------------------------------
        # 5. SUN AT FOCUS
        # -----------------------------------------------------------------
        sun_glow = plt.Circle((0, 0), 0.16, color=SUN_GLOW, alpha=0.22, zorder=10)
        sun_mid  = plt.Circle((0, 0), 0.09, color=SUN_CORE, alpha=0.65, zorder=11)
        sun_core = plt.Circle((0, 0), 0.045, color='#ffffff', zorder=12)
        ax.add_patch(sun_glow)
        ax.add_patch(sun_mid)
        ax.add_patch(sun_core)
        ax.text(0.0, -0.20, "Sun", fontsize=7.8, color=GOLD_ACCENT,
                ha='center', va='top', fontweight='bold', zorder=13)

        # -----------------------------------------------------------------
        # 6. JOINT PRECESSION ARROW (In upper-right quadrant)
        # -----------------------------------------------------------------
        arc_radius = 2.08
        theta1 = np.radians(14.0)
        theta2 = np.radians(46.0)
        arc_angles = np.linspace(theta1, theta2, 35)
        arc_x = arc_radius * np.cos(arc_angles)
        arc_y = arc_radius * np.sin(arc_angles)
        ax.plot(arc_x, arc_y, color=GOLD_ACCENT, lw=1.4, linestyle='-', alpha=0.90, zorder=6)
        
        arr_tip_x = arc_radius * np.cos(theta2)
        arr_tip_y = arc_radius * np.sin(theta2)
        arr_dx = -np.sin(theta2) * 0.08
        arr_dy =  np.cos(theta2) * 0.08
        ax.annotate('', xy=(arr_tip_x + arr_dx, arr_tip_y + arr_dy),
                    xytext=(arr_tip_x, arr_tip_y),
                    arrowprops=dict(arrowstyle="-|>", color=GOLD_ACCENT,
                                    lw=1.4, mutation_scale=9), zorder=7)
        
        ax.text(1.88, 1.05, "Precession",
                fontsize=7.8, color=GOLD_ACCENT, fontweight='bold',
                ha='left', va='center', zorder=8)

        # -----------------------------------------------------------------
        # 7. SIMPLIFIED DESCRIPTIVE BADGE (Clear, non-redundant)
        # -----------------------------------------------------------------
        if ax == ax_a:
            badge_line1 = r"$\varpi_1 - \varpi_2 = 0$"
            badge_line2 = r"Both eccentricity vectors precess together at $g_1$"
        else:
            badge_line1 = r"$\varpi_1 - \varpi_2 = \pi$"
            badge_line2 = r"Both eccentricity vectors precess together at $g_2$"
            
        badge_box = patches.FancyBboxPatch((-1.90, -2.35), 3.80, 0.40,
                                           boxstyle="round,pad=0.03,rounding_size=0.08",
                                           edgecolor=BORDER_LIGHT, facecolor="#0f172a",
                                           linewidth=0.9, alpha=0.92, zorder=14)
        ax.add_patch(badge_box)
        
        ax.text(0.0, -2.06, badge_line1, fontsize=9.2, fontweight='bold', color=TEXT_TITLE,
                ha='center', va='center', zorder=15)
        ax.text(0.0, -2.24, badge_line2, fontsize=7.8, color=TEXT_SUB,
                ha='center', va='center', zorder=15)

    # -------------------------------------------------------------------------
    # BOTTOM MATHEMATICAL STRIP: General N-planet Secular Normal Mode Progression
    # Enlarged and clarified for high readability at Medium's 680px width
    # -------------------------------------------------------------------------
    ax_strip = fig.add_axes([0.05, 0.035, 0.90, 0.145], facecolor=BG_CARD)
    for spine in ax_strip.spines.values():
        spine.set_edgecolor(BORDER_LIGHT)
        spine.set_linewidth(1.1)
    ax_strip.set_xticks([])
    ax_strip.set_yticks([])
    ax_strip.set_xlim(0, 1)
    ax_strip.set_ylim(0, 1)

    # Block 1: Coupled secular system
    ax_strip.text(0.030, 0.74, "Coupled System",
                  fontsize=9.5, fontweight='bold', color=TEXT_SUB, va='center')
    ax_strip.text(0.030, 0.32, r"$\frac{d\mathbf{z}}{dt} = i A \mathbf{z}$",
                  fontsize=13.5, color=INNER_ORBIT,
                  fontweight='bold', va='center')

    # Arrow 1: Diagonalize A
    ax_strip.annotate('', xy=(0.285, 0.48), xytext=(0.170, 0.48),
                      arrowprops=dict(arrowstyle="->", color=TEXT_SUB, lw=1.4, mutation_scale=12))
    ax_strip.text(0.228, 0.74, "Diagonalize A", fontsize=8.6, color=GOLD_ACCENT,
                  fontweight='bold', ha='center', va='center')

    # Block 2: Collective eigenmodes (General N-planet formulation)
    ax_strip.text(0.515, 0.74, "Collective Normal Modes",
                  fontsize=9.5, fontweight='bold', color=TEXT_SUB, va='center', ha='center')
    ax_strip.text(0.515, 0.32,
                  r"$\text{Eigenvalues } g_1, g_2, \ldots \quad \longleftrightarrow \quad \text{Eigenmodes } \mathbf{v}_1, \mathbf{v}_2, \ldots$",
                  fontsize=11.2, color=TEXT_TITLE, va='center', ha='center')

    # Arrow 2: Superposition
    ax_strip.annotate('', xy=(0.815, 0.48), xytext=(0.745, 0.48),
                      arrowprops=dict(arrowstyle="->", color=TEXT_SUB, lw=1.4, mutation_scale=12))
    ax_strip.text(0.780, 0.74, "Superposition", fontsize=8.6, color=GOLD_ACCENT,
                  fontweight='bold', ha='center', va='center')

    # Block 3: General solution
    ax_strip.text(0.845, 0.74, "General Evolution",
                  fontsize=9.5, fontweight='bold', color=TEXT_SUB, va='center')
    ax_strip.text(0.845, 0.32,
                  r"$\mathbf{z}_j(t) = \sum_p \mathbf{C}_{jp} e^{i g_p t}$",
                  fontsize=13.0, color=EMERALD_ACCENT, fontweight='bold', va='center')

    # Save figure
    plt.savefig(output_path, facecolor=BG_COLOR, edgecolor='none', dpi=280)
    plt.close()
    print(f"[OK] Successfully created {output_path}")

    return output_path

generate_secular_normal_modes = create_secular_normal_modes_figure

if __name__ == "__main__":
    create_secular_normal_modes_figure()
