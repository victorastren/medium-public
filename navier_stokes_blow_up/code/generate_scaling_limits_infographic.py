from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "navier_stokes_scaling_limits.png"

#!/usr/bin/env python3
"""
Generate infographic for:
"Navier-Stokes Scaling and the Limits of Energy Control"
for the Medium article on the 3D Navier-Stokes Millennium Problem.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon
import numpy as np

def draw_mini_vortex(ax, center, scale, col, alpha=0.35, zorder=3):
    """Draws an isometric 3D fluid parcel with vortex rotation lines."""
    cx, cy = center
    dx = scale * 0.45
    dy = scale * 0.20
    dz = scale * 0.50

    # Vertices
    b_bot = (cx, cy - dz - dy)
    b_l   = (cx - dx, cy - dz)
    b_r   = (cx + dx, cy - dz)
    b_top = (cx, cy - dz + dy)

    t_bot = (cx, cy + dz - dy)
    t_l   = (cx - dx, cy + dz)
    t_r   = (cx + dx, cy + dz)
    t_top = (cx, cy + dz + dy)

    # Faces
    left_poly = Polygon([b_l, b_bot, t_bot, t_l], closed=True,
                        facecolor=col, edgecolor=col, linewidth=1.2, alpha=alpha*0.8, zorder=zorder)
    right_poly = Polygon([b_bot, b_r, t_r, t_bot], closed=True,
                         facecolor=col, edgecolor=col, linewidth=1.2, alpha=alpha, zorder=zorder)
    top_poly = Polygon([t_bot, t_r, t_top, t_l], closed=True,
                       facecolor=col, edgecolor=col, linewidth=1.4, alpha=alpha*1.4, zorder=zorder+1)

    ax.add_patch(left_poly)
    ax.add_patch(right_poly)
    ax.add_patch(top_poly)

    # Internal central crease
    ax.plot([b_bot[0], t_bot[0]], [b_bot[1], t_bot[1]], color=col, lw=1.5, zorder=zorder+2)

def create_scaling_infographic(out_path=None):
    if out_path is None:
        out_path = DEFAULT_OUT
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(16, 9.2), dpi=240, facecolor='#070b12')

    CANVAS_BG   = '#070b12'
    PANEL_BG    = '#0c1322'
    CARD_BG     = '#101828'
    BORDER_COL  = '#1e293b'
    TEXT_TITLE  = '#f8fafc'
    TEXT_SUB    = '#94a3b8'

    CYAN_COL    = '#38bdf8'
    AMBER_COL   = '#fbbf24'
    ROSE_COL    = '#f43f5e'
    EMERALD_COL = '#34d399'
    INDIGO_COL  = '#818cf8'

    # -------------------------------------------------------------------------
    # TITLE BANNER
    # -------------------------------------------------------------------------
    fig.text(0.50, 0.955, "NAVIER–STOKES SCALING AND THE LIMITS OF ENERGY CONTROL",
             fontsize=18.0, fontweight='bold', color=TEXT_TITLE, ha='center', va='center')
    fig.text(0.50, 0.918,
             r"Symmetry $\mathbf{u}_\lambda = \lambda\mathbf{u}(\lambda\mathbf{x}, \lambda^2 t)$: kinetic energy shrinks under small-scale zoom, while $L^3$ is scale-critical.",
             fontsize=13.0, color='#e2e8f0', ha='center', va='center')

    # -------------------------------------------------------------------------
    # MAIN AREA: 3 PANELS HORIZONTAL SEQUENCE
    # -------------------------------------------------------------------------
    seq_y = 0.105
    seq_h = 0.775
    panel_w = 0.286
    gap = 0.031
    p1_x = 0.038
    p2_x = p1_x + panel_w + gap
    p3_x = p2_x + panel_w + gap

    # =========================================================================
    # PANEL 1: RESCALING THE FLOW
    # =========================================================================
    ax1 = fig.add_axes([p1_x, seq_y, panel_w, seq_h])
    ax1.set_facecolor(PANEL_BG)
    for s in ax1.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.3)
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 100)
    ax1.set_xticks([])
    ax1.set_yticks([])

    # Header Panel 1
    ax1.text(7.0, 94.5, "1. Rescaling the Flow", fontsize=14.5, fontweight='bold', color=CYAN_COL, va='top')
    ax1.text(7.0, 89.5, "Geometric & dynamical scaling symmetry", fontsize=11.4, color='#94a3b8', va='top')

    # Container Card for Comparison
    card1 = FancyBboxPatch((5.0, 4.0), 90.0, 81.5, boxstyle="round,pad=0.5,rounding_size=1.5",
                           facecolor=CARD_BG, edgecolor='#1e293b', linewidth=1.2, zorder=2)
    ax1.add_patch(card1)

    # Sub-area A: Original Structure (Left)
    ax1.text(25.0, 81.0, "Original Flow", fontsize=12.8, fontweight='bold', color='#cbd5e1', ha='center', zorder=3)
    draw_mini_vortex(ax1, (25.0, 52.0), 22.0, CYAN_COL, alpha=0.35, zorder=4)

    # Velocity arrow for original (moderate)
    arr1 = FancyArrowPatch((25.0, 52.0), (25.0, 68.0), arrowstyle='-|>',
                           color=CYAN_COL, mutation_scale=15, lw=2.6, zorder=6)
    ax1.add_patch(arr1)
    ax1.text(31.0, 61.0, r"$u$", color=CYAN_COL, fontsize=13.5, fontweight='bold', zorder=7)

    # Scale label l
    ax1.annotate('', xy=(15.0, 37.0), xytext=(35.0, 37.0),
                 arrowprops=dict(arrowstyle='<->', color='#64748b', lw=1.3), zorder=5)
    ax1.text(25.0, 32.5, r"Scale $\ell$", color='#e2e8f0', fontsize=11.8, fontweight='bold', ha='center', zorder=5)

    # Sub-area B: Rescaled Structure (Right)
    ax1.text(75.0, 81.0, r"Rescaled ($\lambda > 1$)", fontsize=12.8, fontweight='bold', color=AMBER_COL, ha='center', zorder=3)
    draw_mini_vortex(ax1, (75.0, 48.0), 11.5, AMBER_COL, alpha=0.45, zorder=4)

    # Velocity arrow for rescaled (tall, scaled by lambda)
    arr2 = FancyArrowPatch((75.0, 48.0), (75.0, 74.0), arrowstyle='-|>',
                           color=AMBER_COL, mutation_scale=17, lw=3.2, zorder=6)
    ax1.add_patch(arr2)
    ax1.text(80.5, 62.0, r"$\lambda u$", color=AMBER_COL, fontsize=13.5, fontweight='bold', zorder=7)

    # Scale label l/lambda
    ax1.annotate('', xy=(70.0, 39.0), xytext=(80.0, 39.0),
                 arrowprops=dict(arrowstyle='<->', color='#64748b', lw=1.3), zorder=5)
    ax1.text(75.0, 33.5, r"Scale $\ell / \lambda$", color='#fbbf24', fontsize=11.8, fontweight='bold', ha='center', zorder=5)

    # Transition Arrow between the two structures
    ax1.text(50.0, 55.0, r"$\Longrightarrow$", fontsize=22, color='#64748b', ha='center', va='center', zorder=5)
    ax1.text(50.0, 46.0, r"zoom in" + "\n" + r"$\lambda \to \infty$", fontsize=11.2, color='#cbd5e1', ha='center', va='center', zorder=5)

    # Transformation Rules Box at bottom of Panel 1
    rules_box = FancyBboxPatch((7.0, 6.0), 86.0, 23.5, boxstyle="round,pad=0.4,rounding_size=1.0",
                               facecolor='#0a101d', edgecolor='#1e293b', lw=1.2, zorder=4)
    ax1.add_patch(rules_box)
    ax1.text(50.0, 25.5, "Navier–Stokes Scaling Symmetry:", fontsize=11.8, fontweight='bold', color='#f8fafc', ha='center', zorder=5)
    ax1.text(28.0, 17.5, r"$\mathbf{x} \longrightarrow \lambda \mathbf{x}$" + "\n" + r"$t \longrightarrow \lambda^2 t$",
             fontsize=11.6, color='#e2e8f0', ha='center', va='center', zorder=5)
    ax1.text(72.0, 17.5, r"$\mathbf{u} \longrightarrow \lambda \mathbf{u}$" + "\n" + r"$p \longrightarrow \lambda^2 p$",
             fontsize=11.6, color='#e2e8f0', ha='center', va='center', zorder=5)
    ax1.text(50.0, 9.5, r"$\mathbf{u}_\lambda(\mathbf{x},t) = \lambda\,\mathbf{u}(\lambda\mathbf{x},\lambda^2 t)$",
             fontsize=12.2, fontweight='bold', color=CYAN_COL, ha='center', va='center', zorder=5)

    # =========================================================================
    # PANEL 2: WHAT HAPPENS TO THE NORMS
    # =========================================================================
    ax2 = fig.add_axes([p2_x, seq_y, panel_w, seq_h])
    ax2.set_facecolor(PANEL_BG)
    for s in ax2.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.3)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.set_xticks([])
    ax2.set_yticks([])

    # Header Panel 2
    ax2.text(7.0, 94.5, "2. What Happens to the Norms", fontsize=14.5, fontweight='bold', color=AMBER_COL, va='top')
    ax2.text(7.0, 89.5, r"Behavior under small-scale zoom ($\lambda \to \infty$)", fontsize=11.4, color='#94a3b8', va='top')

    # Card 2 Container
    card2 = FancyBboxPatch((5.0, 4.0), 90.0, 81.5, boxstyle="round,pad=0.5,rounding_size=1.5",
                           facecolor=CARD_BG, edgecolor='#1e293b', linewidth=1.2, zorder=2)
    ax2.add_patch(card2)

    # Row 1: Kinematic scaling variables
    y_pos = 75.0
    r1 = FancyBboxPatch((7.0, y_pos - 4.5), 86.0, 10.5, boxstyle="round,pad=0.3,rounding_size=0.8",
                        facecolor='#0d1526', edgecolor='#1e293b', lw=1.0, zorder=3)
    ax2.add_patch(r1)
    ax2.text(11.0, y_pos + 0.8, "Length Scale:", fontsize=11.8, fontweight='bold', color='#cbd5e1', zorder=4)
    ax2.text(45.0, y_pos + 0.8, r"$\ell \sim \lambda^{-1}$", fontsize=12.4, color='#f1f5f9', zorder=4)
    ax2.text(89.0, y_pos + 0.8, r"$\searrow 0$", fontsize=13.5, fontweight='bold', color='#38bdf8', ha='right', zorder=4)

    y_pos = 62.5
    r2 = FancyBboxPatch((7.0, y_pos - 4.5), 86.0, 10.5, boxstyle="round,pad=0.3,rounding_size=0.8",
                        facecolor='#0d1526', edgecolor='#1e293b', lw=1.0, zorder=3)
    ax2.add_patch(r2)
    ax2.text(11.0, y_pos + 0.8, "Time Scale:", fontsize=11.8, fontweight='bold', color='#cbd5e1', zorder=4)
    ax2.text(45.0, y_pos + 0.8, r"$t \sim \ell^2 \sim \lambda^{-2}$", fontsize=12.4, color='#f1f5f9', zorder=4)
    ax2.text(89.0, y_pos + 0.8, r"$\searrow 0$", fontsize=13.5, fontweight='bold', color='#38bdf8', ha='right', zorder=4)

    y_pos = 50.0
    r3 = FancyBboxPatch((7.0, y_pos - 4.5), 86.0, 10.5, boxstyle="round,pad=0.3,rounding_size=0.8",
                        facecolor='#0d1526', edgecolor='#1e293b', lw=1.0, zorder=3)
    ax2.add_patch(r3)
    ax2.text(11.0, y_pos + 0.8, "Velocity Scale:", fontsize=11.8, fontweight='bold', color='#cbd5e1', zorder=4)
    ax2.text(45.0, y_pos + 0.8, r"$|\mathbf{u}| \sim \ell^{-1} \sim \lambda$", fontsize=12.4, color='#f1f5f9', zorder=4)
    ax2.text(89.0, y_pos + 0.8, r"$\nearrow \infty$", fontsize=13.5, fontweight='bold', color='#fb7185', ha='right', zorder=4)

    # Highlight Card: L^2 Norm (Kinetic Energy) -> Scales Down!
    y_pos = 32.5
    card_l2 = FancyBboxPatch((7.0, y_pos - 8.5), 86.0, 18.5, boxstyle="round,pad=0.4,rounding_size=1.0",
                             facecolor='#1e1528', edgecolor='#be185d', lw=1.5, zorder=4)
    ax2.add_patch(card_l2)
    ax2.text(10.5, y_pos + 5.2, r"Kinetic Energy ($L^2$-Based):",
             fontsize=12.0, fontweight='bold', color='#f472b6', zorder=5)
    ax2.text(10.5, y_pos - 0.5, r"$\|\mathbf{u}_\lambda\|_{L^2}^2 = \lambda^{-1}\|\mathbf{u}\|_{L^2}^2 \longrightarrow 0$",
             fontsize=12.6, fontweight='bold', color='#fbcfe8', zorder=5)
    ax2.text(89.5, y_pos - 0.5, r"SHRINKS $\searrow$", fontsize=12.0, fontweight='bold', color='#f43f5e', ha='right', zorder=5)
    ax2.text(10.5, y_pos - 5.8, "Energy diminishes at smaller scales (supercritical)",
             fontsize=10.8, color='#fecdd3', zorder=5)

    # Highlight Card: L^3 Norm -> Invariant / Scale-Critical!
    y_pos = 11.5
    card_l3 = FancyBboxPatch((7.0, y_pos - 6.0), 86.0, 17.5, boxstyle="round,pad=0.4,rounding_size=1.0",
                             facecolor='#042f2e', edgecolor=EMERALD_COL, lw=1.6, zorder=4)
    ax2.add_patch(card_l3)
    ax2.text(10.5, y_pos + 5.5, r"$L^3$ Critical Norm (Scale-Invariant):",
             fontsize=12.0, fontweight='bold', color='#6ee7b7', zorder=5)
    ax2.text(10.5, y_pos + 0.2, r"$\|\mathbf{u}_\lambda\|_{L^3} = \lambda^{1 - 3/3}\|\mathbf{u}\|_{L^3} \equiv \|\mathbf{u}\|_{L^3}$",
             fontsize=12.4, fontweight='bold', color='#a7f3d0', zorder=5)
    ax2.text(89.5, y_pos + 0.2, r"INVARIANT", fontsize=11.8, fontweight='bold', color='#34d399', ha='right', zorder=5)
    ax2.text(10.5, y_pos - 4.2, "Scale-invariant norm: constant under zooming",
             fontsize=10.8, color='#d1fae5', zorder=5)

    # =========================================================================
    # PANEL 3: CONCEPTUAL INTERPRETATION
    # =========================================================================
    ax3 = fig.add_axes([p3_x, seq_y, panel_w, seq_h])
    ax3.set_facecolor(PANEL_BG)
    for s in ax3.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.3)
    ax3.set_xlim(0, 100)
    ax3.set_ylim(0, 100)
    ax3.set_xticks([])
    ax3.set_yticks([])

    # Header Panel 3
    ax3.text(7.0, 94.5, "3. Conceptual Takeaways", fontsize=14.5, fontweight='bold', color=ROSE_COL, va='top')
    ax3.text(7.0, 89.5, "Why energy control alone is insufficient for regularity", fontsize=11.4, color='#94a3b8', va='top')

    # Card 3 Container
    card3 = FancyBboxPatch((5.0, 4.0), 90.0, 81.5, boxstyle="round,pad=0.5,rounding_size=1.5",
                           facecolor=CARD_BG, edgecolor='#1e293b', linewidth=1.2, zorder=2)
    ax3.add_patch(card3)

    # Pillar 1: Energy Control Weakens
    box_p1 = FancyBboxPatch((7.0, 58.5), 86.0, 24.5, boxstyle="round,pad=0.4,rounding_size=1.0",
                            facecolor='#141926', edgecolor='#334155', lw=1.2, zorder=3)
    ax3.add_patch(box_p1)
    ax3.text(10.5, 78.5, r"• Energy ($L^2$) Weakens at Small Scales",
             fontsize=11.8, fontweight='bold', color='#f8fafc', zorder=4)
    ax3.text(10.5, 66.5,
             r"Because the kinetic energy scales as $\lambda^{-1}$," + "\n"
             r"energy can become small under rescaling" + "\n"
             r"even as velocity gradients blow up.",
             fontsize=11.0, color='#e2e8f0', linespacing=1.35, zorder=4)

    # Pillar 2: L^3 is Scale-Critical
    box_p2 = FancyBboxPatch((7.0, 31.5), 86.0, 24.5, boxstyle="round,pad=0.4,rounding_size=1.0",
                            facecolor='#141926', edgecolor='#334155', lw=1.2, zorder=3)
    ax3.add_patch(box_p2)
    ax3.text(10.5, 51.5, r"• $L^3$ Norm is Scale-Critical",
             fontsize=11.8, fontweight='bold', color=EMERALD_COL, zorder=4)
    ax3.text(10.5, 39.5,
             r"For $p = 3$, the scaling factor $\lambda^{1 - 3/p} = 1$." + "\n"
             r"The $L^3$ norm neither grows nor diminishes," + "\n"
             r"making it the critical gauge for regularity.",
             fontsize=11.0, color='#e2e8f0', linespacing=1.35, zorder=4)

    # Pillar 3: 3D Navier-Stokes is Energy-Supercritical
    box_p3 = FancyBboxPatch((7.0, 6.5), 86.0, 22.5, boxstyle="round,pad=0.4,rounding_size=1.0",
                            facecolor='#260a16', edgecolor=ROSE_COL, lw=1.4, zorder=3)
    ax3.add_patch(box_p3)
    ax3.text(10.5, 24.5, "• 3D Flow is Energy-Supercritical",
             fontsize=11.8, fontweight='bold', color='#fecdd3', zorder=4)
    ax3.text(10.5, 13.5,
             r"The a priori energy estimate ($L^2$) is weaker" + "\n"
             r"than the critical scaling norm ($L^3$). Total" + "\n"
             r"energy cannot prevent local singularity.",
             fontsize=10.8, color='#ffe4e6', linespacing=1.35, zorder=4)

    # -------------------------------------------------------------------------
    # BOTTOM SUMMARY RIBBON
    # -------------------------------------------------------------------------
    fig.text(0.50, 0.045,
             "The L² energy scale decreases under small-scale rescaling, while L³ remains invariant — this is why 3D Navier–Stokes is energy-supercritical.",
             fontsize=12.6, fontweight='bold', color=TEXT_TITLE, ha='center', va='center')

    # out_path is provided via function argument
    plt.savefig(out_path, dpi=240, bbox_inches='tight', facecolor=CANVAS_BG, edgecolor='none')
    plt.close()
    print(f"[OK] Generated Navier-Stokes Scaling Limits Infographic: {out_path}")
    return out_path

generate_scaling_limits_infographic = create_scaling_infographic

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    create_scaling_infographic(target)
