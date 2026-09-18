from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "finite_energy_concentration.png"

#!/usr/bin/env python3
"""
Generate infographic for section:
"Why Finite Energy Does Not Guarantee Regularity"

Title: FINITE ENERGY DOES NOT PREVENT LOCAL CONCENTRATION
Subtitle: A 3D fluid structure can concentrate into smaller scales (V ~ l^3) with growing amplitude (A ~ l^-3/2), keeping energy bounded while gradients explode.

Layout:
- Top: Title & conceptual subtitle
- Middle: 3-stage horizontal sequence of 3D fluid structures (Broad -> Intermediate -> Strongly Concentrated)
- Bottom: Side-by-side comparison of Bounded Energy vs. Divergent Gradient, and summary takeaway.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon
import numpy as np

def draw_3d_cube(ax, center, l, face_col, edge_col, alpha=0.35, zorder=2):
    """Draws an isometric 3D rectangular box/cube representing fluid structure."""
    cx, cy = center
    dx = l * 0.50
    dy = l * 0.25
    dz = l * 0.55

    # 8 vertices
    # Bottom face
    b_bot = (cx, cy - dz - dy)
    b_l   = (cx - dx, cy - dz)
    b_r   = (cx + dx, cy - dz)
    b_top = (cx, cy - dz + dy)

    # Top face
    t_bot = (cx, cy + dz - dy)
    t_l   = (cx - dx, cy + dz)
    t_r   = (cx + dx, cy + dz)
    t_top = (cx, cy + dz + dy)

    # Faces: Bottom, Top, Left, Right
    # Left vertical face
    left_poly = Polygon([b_l, b_bot, t_bot, t_l], closed=True,
                        facecolor=face_col, edgecolor=edge_col, linewidth=1.2, alpha=alpha*0.8, zorder=zorder)
    # Right vertical face
    right_poly = Polygon([b_bot, b_r, t_r, t_bot], closed=True,
                         facecolor=face_col, edgecolor=edge_col, linewidth=1.2, alpha=alpha, zorder=zorder)
    # Top face
    top_poly = Polygon([t_bot, t_r, t_top, t_l], closed=True,
                       facecolor=face_col, edgecolor=edge_col, linewidth=1.4, alpha=alpha*1.3, zorder=zorder+1)

    ax.add_patch(left_poly)
    ax.add_patch(right_poly)
    ax.add_patch(top_poly)

    # Subtle internal grid / streamlines
    ax.plot([b_l[0], t_l[0]], [b_l[1], t_l[1]], color=edge_col, lw=1.2, zorder=zorder+2)
    ax.plot([b_r[0], t_r[0]], [b_r[1], t_r[1]], color=edge_col, lw=1.2, zorder=zorder+2)
    ax.plot([b_bot[0], t_bot[0]], [b_bot[1], t_bot[1]], color=edge_col, lw=1.5, zorder=zorder+2)

    return (cx, cy - dz - dy - 0.25, cx, cy + dz + dy)

def create_energy_concentration_figure(out_path=None):
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

    # -------------------------------------------------------------------------
    # TITLE BANNER
    # -------------------------------------------------------------------------
    fig.text(0.50, 0.952, "FINITE ENERGY DOES NOT PREVENT LOCAL CONCENTRATION",
             fontsize=18.0, fontweight='bold', color=TEXT_TITLE, ha='center', va='center')
    fig.text(0.50, 0.916,
             r"As 3D structures shrink ($V \sim \ell^3$), amplitude grows ($A \sim \ell^{-3/2}$): energy stays $\mathcal{O}(1)$ while local gradients diverge.",
             fontsize=12.8, color='#cbd5e1', ha='center', va='center')

    # -------------------------------------------------------------------------
    # MAIN AREA: 3 PANELS HORIZONTAL SEQUENCE (Top Row of Content)
    # -------------------------------------------------------------------------
    seq_y = 0.380
    seq_h = 0.500
    panel_w = 0.270
    gap = 0.050
    p1_x = 0.045
    p2_x = p1_x + panel_w + gap
    p3_x = p2_x + panel_w + gap

    # Container background for entire 3-stage strip
    ax_seq_bg = fig.add_axes([0.040, seq_y, 0.920, seq_h])
    ax_seq_bg.set_facecolor(PANEL_BG)
    for s in ax_seq_bg.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.4)
    ax_seq_bg.set_xticks([])
    ax_seq_bg.set_yticks([])
    ax_seq_bg.set_xlim(0, 100)
    ax_seq_bg.set_ylim(0, 100)

    # -------------------------------------------------------------------------
    # STAGE 1: BROAD STRUCTURE
    # -------------------------------------------------------------------------
    ax1 = fig.add_axes([p1_x + 0.006, seq_y + 0.015, panel_w - 0.012, seq_h - 0.030])
    ax1.set_facecolor(CARD_BG)
    for s in ax1.spines.values():
        s.set_edgecolor('#1e293b')
        s.set_linewidth(1.0)
    ax1.set_xlim(-2.5, 2.5)
    ax1.set_ylim(-2.5, 2.5)
    ax1.set_xticks([])
    ax1.set_yticks([])

    # Header Stage 1
    ax1.text(0.06, 0.935, "1. Broad Structure", transform=ax1.transAxes,
             fontsize=14.5, fontweight='bold', color=CYAN_COL, va='top')
    ax1.text(0.06, 0.845, "Moderate scale, distributed energy", transform=ax1.transAxes,
             fontsize=11.2, color='#94a3b8', va='top')

    # Draw Stage 1 Cube (Large l1 = 2.1)
    c1 = (0.0, -0.45)
    l1 = 2.1
    draw_3d_cube(ax1, c1, l1, face_col='#0369a1', edge_col=CYAN_COL, alpha=0.32, zorder=3)

    # Velocity vector A1 (moderate height)
    arr_a1 = FancyArrowPatch((0.0, -0.45), (0.0, 0.65), arrowstyle='-|>',
                             color=CYAN_COL, mutation_scale=16, lw=3.0, zorder=8)
    ax1.add_patch(arr_a1)
    ax1.text(0.18, 0.20, r"Amplitude $A_1$", color=CYAN_COL, fontsize=12.2, fontweight='bold', zorder=9)

    # Dimension indicator l1
    ax1.annotate('', xy=(-1.05, -1.60), xytext=(1.05, -1.60),
                 arrowprops=dict(arrowstyle='<->', color='#64748b', lw=1.3), zorder=6)
    ax1.text(0.0, -1.92, r"Scale $\ell_1$ (Large)", color='#cbd5e1', fontsize=11.6, fontweight='bold', ha='center', zorder=7)

    # Metrics Card at bottom of Stage 1
    m1 = FancyBboxPatch((-2.38, -2.44), 4.76, 0.44, boxstyle="round,pad=0.04,rounding_size=0.08",
                        facecolor='#0f172a', edgecolor='#1e293b', lw=1.0, zorder=6)
    ax1.add_patch(m1)
    ax1.text(0.0, -2.22, r"Volume: $V_1 \sim \ell_1^3$  |  Gradient: $|\nabla\mathbf{u}|_1$ (Moderate)",
             color='#cbd5e1', fontsize=10.8, ha='center', va='center', zorder=7)

    # Transition Arrow 1 -> 2 on background
    ax_seq_bg.text(32.6, 52.0, "⟹", fontsize=24, color='#64748b', ha='center', va='center', zorder=10)
    ax_seq_bg.text(32.6, 40.0, "Volume\ncontracts", fontsize=10.8, color='#cbd5e1', ha='center', va='center')

    # -------------------------------------------------------------------------
    # STAGE 2: INTERMEDIATE CONCENTRATION
    # -------------------------------------------------------------------------
    ax2 = fig.add_axes([p2_x + 0.006, seq_y + 0.015, panel_w - 0.012, seq_h - 0.030])
    ax2.set_facecolor(CARD_BG)
    for s in ax2.spines.values():
        s.set_edgecolor('#1e293b')
        s.set_linewidth(1.0)
    ax2.set_xlim(-2.5, 2.5)
    ax2.set_ylim(-2.5, 2.5)
    ax2.set_xticks([])
    ax2.set_yticks([])

    # Header Stage 2
    ax2.text(0.06, 0.935, "2. More Concentrated", transform=ax2.transAxes,
             fontsize=14.5, fontweight='bold', color=AMBER_COL, va='top')
    ax2.text(0.06, 0.845, "Smaller scale, elevated amplitude", transform=ax2.transAxes,
             fontsize=11.2, color='#94a3b8', va='top')

    # Draw Stage 2 Cube (Medium l2 = 1.25)
    c2 = (0.0, -0.65)
    l2 = 1.25
    draw_3d_cube(ax2, c2, l2, face_col='#b45309', edge_col=AMBER_COL, alpha=0.38, zorder=3)

    # Velocity vector A2 (larger height)
    arr_a2 = FancyArrowPatch((0.0, -0.65), (0.0, 0.95), arrowstyle='-|>',
                             color=AMBER_COL, mutation_scale=18, lw=3.8, zorder=8)
    ax2.add_patch(arr_a2)
    ax2.text(0.18, 0.35, r"Amplitude $A_2 > A_1$", color=AMBER_COL, fontsize=12.2, fontweight='bold', zorder=9)

    # Dimension indicator l2
    ax2.annotate('', xy=(-0.65, -1.60), xytext=(0.65, -1.60),
                 arrowprops=dict(arrowstyle='<->', color='#64748b', lw=1.3), zorder=6)
    ax2.text(0.0, -1.92, r"Scale $\ell_2 < \ell_1$", color='#fbbf24', fontsize=11.6, fontweight='bold', ha='center', zorder=7)

    # Metrics Card at bottom of Stage 2
    m2 = FancyBboxPatch((-2.38, -2.44), 4.76, 0.44, boxstyle="round,pad=0.04,rounding_size=0.08",
                        facecolor='#0f172a', edgecolor='#1e293b', lw=1.0, zorder=6)
    ax2.add_patch(m2)
    ax2.text(0.0, -2.22, r"Volume: $V_2 \sim \ell_2^3$  |  Gradient: $|\nabla\mathbf{u}|_2$ (Steeper)",
             color='#cbd5e1', fontsize=10.8, ha='center', va='center', zorder=7)

    # Transition Arrow 2 -> 3 on background
    ax_seq_bg.text(67.4, 52.0, "⟹", fontsize=24, color='#64748b', ha='center', va='center', zorder=10)
    ax_seq_bg.text(67.4, 40.0, "Extreme\nfocus", fontsize=10.8, color='#cbd5e1', ha='center', va='center')

    # -------------------------------------------------------------------------
    # STAGE 3: STRONGLY CONCENTRATED
    # -------------------------------------------------------------------------
    ax3 = fig.add_axes([p3_x + 0.006, seq_y + 0.015, panel_w - 0.012, seq_h - 0.030])
    ax3.set_facecolor(CARD_BG)
    for s in ax3.spines.values():
        s.set_edgecolor('#1e293b')
        s.set_linewidth(1.0)
    ax3.set_xlim(-2.5, 2.5)
    ax3.set_ylim(-2.5, 2.5)
    ax3.set_xticks([])
    ax3.set_yticks([])

    # Header Stage 3
    ax3.text(0.06, 0.935, "3. Strongly Concentrated", transform=ax3.transAxes,
             fontsize=14.5, fontweight='bold', color=ROSE_COL, va='top')
    ax3.text(0.06, 0.845, r"Microscopic scale $\ell_3 \to 0$, extreme gradient", transform=ax3.transAxes,
             fontsize=11.2, color='#94a3b8', va='top')

    # Draw Stage 3 Cube (Tiny l3 = 0.55)
    c3 = (0.0, -0.90)
    l3 = 0.55
    draw_3d_cube(ax3, c3, l3, face_col='#be123c', edge_col=ROSE_COL, alpha=0.50, zorder=3)

    # Velocity vector A3 (towering height, radiant glow)
    arr_a3_glow = FancyArrowPatch((0.0, -0.90), (0.0, 1.45), arrowstyle='-|>',
                                  color=ROSE_COL, mutation_scale=22, lw=8.0, alpha=0.25, zorder=7)
    arr_a3 = FancyArrowPatch((0.0, -0.90), (0.0, 1.45), arrowstyle='-|>',
                             color=ROSE_COL, mutation_scale=20, lw=4.2, zorder=8)
    ax3.add_patch(arr_a3_glow)
    ax3.add_patch(arr_a3)
    ax3.text(0.18, 0.55, r"Amplitude $A_3 \gg A_2$", color=ROSE_COL, fontsize=12.2, fontweight='bold', zorder=9)

    # Dimension indicator l3
    ax3.annotate('', xy=(-0.30, -1.60), xytext=(0.30, -1.60),
                 arrowprops=dict(arrowstyle='<->', color='#64748b', lw=1.3), zorder=6)
    ax3.text(0.0, -1.92, r"Scale $\ell_3 \ll \ell_2$ ($\ell_3 \to 0$)", color='#f43f5e', fontsize=11.6, fontweight='bold', ha='center', zorder=7)

    # Metrics Card at bottom of Stage 3
    m3 = FancyBboxPatch((-2.38, -2.44), 4.76, 0.44, boxstyle="round,pad=0.04,rounding_size=0.08",
                        facecolor='#0f172a', edgecolor='#1e293b', lw=1.0, zorder=6)
    ax3.add_patch(m3)
    ax3.text(0.0, -2.22, r"Volume: $V_3 \to 0$  |  Gradient: $|\nabla\mathbf{u}|_3 \to \infty$",
             color='#fca5a5', fontsize=10.8, ha='center', va='center', zorder=7)

    # -------------------------------------------------------------------------
    # BOTTOM ROW: SIDE-BY-SIDE MATHEMATICAL CONTRAST PILLARS
    # -------------------------------------------------------------------------
    bot_y = 0.050
    bot_h = 0.285

    ax_bot = fig.add_axes([0.040, bot_y, 0.920, bot_h])
    ax_bot.set_facecolor(PANEL_BG)
    for s in ax_bot.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.4)
    ax_bot.set_xticks([])
    ax_bot.set_yticks([])
    ax_bot.set_xlim(0, 100)
    ax_bot.set_ylim(0, 100)

    # Pillar 1 (Left): Energy Remains Bounded
    p1 = FancyBboxPatch((2.0, 18.0), 45.0, 75.0,
                        boxstyle="round,pad=0.4,rounding_size=1.2",
                        facecolor='#022c22', edgecolor=EMERALD_COL, linewidth=1.8, zorder=2)
    ax_bot.add_patch(p1)
    ax_bot.text(24.5, 78.0, "Energy Contribution (Bounded)",
                fontsize=13.2, fontweight='bold', color='#a7f3d0', ha='center', va='center', zorder=3)
    ax_bot.text(24.5, 54.0, r"$E_{\mathrm{local}} \sim A^2 \ell^3 \sim 1$",
                fontsize=16.5, fontweight='bold', color='#34d399', ha='center', va='center', zorder=3)
    ax_bot.text(24.5, 30.0,
                r"Volume contracts as $\ell^3$ while amplitude grows as $\ell^{-3/2}$:" + "\n" +
                r"the energy contribution $A^2 V$ remains bounded for all $\ell > 0$.",
                fontsize=11.6, linespacing=1.35, color='#e2e8f0', ha='center', va='center', zorder=3)

    # VS Separator
    ax_bot.text(50.0, 54.0, "VS", fontsize=16.0, fontweight='bold', color='#94a3b8', ha='center', va='center', zorder=3)

    # Pillar 2 (Right): Local Gradient Explodes
    p2 = FancyBboxPatch((53.0, 18.0), 45.0, 75.0,
                        boxstyle="round,pad=0.4,rounding_size=1.2",
                        facecolor='#3b0716', edgecolor=ROSE_COL, linewidth=1.8, zorder=2)
    ax_bot.add_patch(p2)
    ax_bot.text(75.5, 78.0, "Local Velocity Gradient (Grows Without Bound)",
                fontsize=13.0, fontweight='bold', color='#fecdd3', ha='center', va='center', zorder=3)
    ax_bot.text(75.5, 54.0, r"$|\nabla\mathbf{u}| \sim \frac{A}{\ell} \sim \ell^{-5/2} \longrightarrow \infty$",
                fontsize=16.5, fontweight='bold', color='#fb7185', ha='center', va='center', zorder=3)
    ax_bot.text(75.5, 30.0,
                r"Dividing the growing velocity by the shrinking distance $\ell$" + "\n" +
                r"forces the spatial gradient to diverge as $\ell \to 0$.",
                fontsize=11.6, linespacing=1.35, color='#ffe4e6', ha='center', va='center', zorder=3)

    # Bottom Takeaway Ribbon
    ax_bot.text(50.0, 7.5,
                "Takeaway: Bounded energy does not prevent increasingly large local gradients.",
                fontsize=12.6, fontweight='bold', color=TEXT_TITLE, ha='center', va='center', zorder=3)

    # out_path is provided via function argument
    plt.savefig(out_path, dpi=240, bbox_inches='tight', facecolor=CANVAS_BG, edgecolor='none')
    plt.close()
    print(f"[OK] Generated Finite Energy Concentration Infographic: {out_path}")
    return out_path

generate_energy_concentration_infographic = create_energy_concentration_figure

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    create_energy_concentration_figure(target)
