from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "vortex_stretching_mechanism.png"

#!/usr/bin/env python3
"""
Generate infographic for "From Velocity to Vorticity":
The 3D Vortex-Stretching Mechanism in Navier-Stokes.

Visual grammar matches Eulerian vs. Lagrangian infographic:
- Dark mathematical analysis slate theme (#070b12, #0c1322, #101828)
- High-contrast neon vectors & glow styling
- Left: Vortex Tube Before Stretching (wide radius, short length, moderate vorticity)
- Right: Vortex Tube After Stretching (elongated, thin cross-section, amplified vorticity)
- Bottom: 3-pillar mathematical synthesis strip
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Ellipse
import numpy as np

def create_vortex_stretching_figure(out_path=None):
    if out_path is None:
        out_path = DEFAULT_OUT
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(16, 9.2), dpi=240, facecolor='#070b12')
    
    # Grid layout: Title row, Main schematic row, Bottom synthesis row
    gs = fig.add_gridspec(3, 1, height_ratios=[0.11, 0.71, 0.18], hspace=0.16)
    
    # -------------------------------------------------------------------------
    # COLOR PALETTE (matching material derivative infographic)
    # -------------------------------------------------------------------------
    CANVAS_BG   = '#070b12'
    PANEL_BG    = '#0c1322'
    CARD_BG     = '#101828'
    BORDER_COL  = '#1e293b'
    GRID_COL    = '#1e293b'
    TEXT_TITLE  = '#f8fafc'
    TEXT_SUB    = '#94a3b8'
    
    # Feature Accents
    TUBE_EDGE_1 = '#38bdf8'  # Cyan
    OMEGA_COL   = '#fbbf24'  # Gold / Amber for core vorticity
    STRETCH_COL = '#a855f7'  # Purple / Violet for stretching
    SWIRL_COL   = '#38bdf8'  # Cyan for rotational velocity
    AMPLIF_COL  = '#f43f5e'  # Vivid Rose / Coral for intensified vorticity
    EMERALD_COL = '#10b981'  # Green for conservation / volume
    
    # -------------------------------------------------------------------------
    # ROW 0: MAIN TITLE BANNER
    # -------------------------------------------------------------------------
    ax_title = fig.add_subplot(gs[0, 0])
    ax_title.set_facecolor(CANVAS_BG)
    ax_title.axis('off')
    
    ax_title.text(0.5, 0.68, "THE VORTEX-STRETCHING MECHANISM IN THREE DIMENSIONS",
                  fontsize=18.0, fontweight='bold', color=TEXT_TITLE, ha='center', va='center')
    ax_title.text(0.5, 0.18,
                  r"How the stretching term $(\boldsymbol{\omega}\cdot\nabla)\mathbf{u}$ amplifies vorticity by elongating fluid structures",
                  fontsize=12.8, color='#cbd5e1', ha='center', va='center')

    # -------------------------------------------------------------------------
    # ROW 1: TWO PANELS (Before Stretching vs. After Stretching)
    # -------------------------------------------------------------------------
    gs_mid = gs[1].subgridspec(1, 2, wspace=0.08)
    
    # =========================================================================
    # LEFT PANEL: Before Stretching
    # =========================================================================
    ax1 = fig.add_subplot(gs_mid[0, 0])
    ax1.set_facecolor(PANEL_BG)
    for s in ax1.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.3)
    ax1.set_xlim(-3.6, 3.6)
    ax1.set_ylim(-2.5, 2.5)
    ax1.set_aspect('equal')
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.grid(False)
    
    # Header & Question
    ax1.text(0.04, 0.95, "Initial Vortex Tube (t = t₁)",
             transform=ax1.transAxes, fontsize=14.8, fontweight='bold',
             color=TEXT_TITLE, va='top')
    ax1.text(0.04, 0.88, r"“Wider radius, shorter length, moderate vorticity”",
             transform=ax1.transAxes, fontsize=11.8,
             color=TUBE_EDGE_1, va='top')
    # Tube Geometry 1: Wide & Short (Centered at x = 0.0, y = -0.35 with generous breathing room)
    c1_x, c1_y = 0.0, -0.35
    r1 = 1.25      # radius
    h1 = 1.40      # height
    y_bot1 = c1_y - 0.5 * h1
    y_top1 = c1_y + 0.5 * h1
    
    # Draw cylinder 1 body with shading
    n_layers = 30
    for i in range(n_layers):
        frac = i / (n_layers - 1)
        shading_alpha = 0.05 + 0.16 * np.sin(frac * np.pi)
        rect = patches.Rectangle((c1_x - r1 + (2*r1/n_layers)*i, y_bot1), 2*r1/n_layers, h1,
                                 facecolor='#0284c7', edgecolor='none', alpha=shading_alpha, zorder=2)
        ax1.add_patch(rect)
        
    # Cylinder side walls
    ax1.plot([c1_x - r1, c1_x - r1], [y_bot1, y_top1], color=TUBE_EDGE_1, lw=2.2, zorder=4)
    ax1.plot([c1_x + r1, c1_x + r1], [y_bot1, y_top1], color=TUBE_EDGE_1, lw=2.2, zorder=4)
    
    # Bottom elliptical cap
    b_ell_back = patches.Arc((c1_x, y_bot1), 2*r1, 0.48*r1, angle=0, theta1=0, theta2=180,
                             color=TUBE_EDGE_1, lw=1.5, linestyle=':', alpha=0.6, zorder=3)
    b_ell_front = patches.Arc((c1_x, y_bot1), 2*r1, 0.48*r1, angle=0, theta1=180, theta2=360,
                              color=TUBE_EDGE_1, lw=2.2, zorder=4)
    ax1.add_patch(b_ell_back)
    ax1.add_patch(b_ell_front)
    
    # Top elliptical cap (fully visible)
    t_ell = Ellipse((c1_x, y_top1), 2*r1, 0.48*r1, facecolor='#1e293b', edgecolor=TUBE_EDGE_1,
                    lw=2.2, alpha=0.92, zorder=5)
    ax1.add_patch(t_ell)
    
    # Cross section callout at top
    ax1.plot([c1_x, c1_x + r1], [y_top1, y_top1], color='#ffffff', lw=1.5, linestyle='--', zorder=6)
    ax1.plot([c1_x], [y_top1], 'o', color='#ffffff', markersize=4.5, zorder=7)
    ax1.text(c1_x + 0.5*r1, y_top1 + 0.12, r"Radius $R_1$", color='#ffffff', fontsize=11.8, fontweight='bold', ha='center', va='bottom', zorder=8)
    
    # Core vorticity vector (omega_1) along axis
    ax1.annotate('', xy=(c1_x, y_top1 + 0.65), xytext=(c1_x, y_bot1 - 0.20),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.46,head_length=0.72",
                                 color=OMEGA_COL, lw=3.4, mutation_scale=16), zorder=8)
    ax1.text(c1_x - 0.18, y_top1 + 0.68, r"$\boldsymbol{\omega}_1$",
             fontsize=15.0, fontweight='bold', color=OMEGA_COL, ha='right', va='center', zorder=9)
    ax1.text(c1_x - 0.18, y_top1 + 0.44, "(Initial Vorticity)",
             fontsize=10.8, fontweight='bold', color=OMEGA_COL, ha='right', va='center', zorder=9)

    # Moderate swirl rings around cylinder
    swirl_ys_1 = [y_bot1 + 0.32*h1, y_bot1 + 0.72*h1]
    for sy in swirl_ys_1:
        arc_b = patches.Arc((c1_x, sy), 2.15*r1, 0.54*r1, angle=0, theta1=0, theta2=180,
                            color=SWIRL_COL, lw=1.6, linestyle=':', alpha=0.5, zorder=3)
        arc_f = patches.Arc((c1_x, sy), 2.15*r1, 0.54*r1, angle=0, theta1=180, theta2=360,
                            color=SWIRL_COL, lw=2.4, zorder=6)
        ax1.add_patch(arc_b)
        ax1.add_patch(arc_f)
        ax1.annotate('', xy=(c1_x + 0.45*r1, sy - 0.25*r1), xytext=(c1_x - 0.25*r1, sy - 0.26*r1),
                     arrowprops=dict(arrowstyle="-|>,head_width=0.34,head_length=0.54",
                                     color=SWIRL_COL, lw=2.4, mutation_scale=13), zorder=7)
                     
    ax1.text(c1_x + 1.15*r1, swirl_ys_1[1], r"Moderate swirl $\mathbf{u}_\theta$",
             fontsize=11.4, color=SWIRL_COL, fontweight='bold', ha='left', va='center', zorder=8)
             
    # Dimension Callouts: Length L1
    dim_x1 = c1_x - r1 - 0.35
    ax1.plot([dim_x1, dim_x1], [y_bot1, y_top1], color=TEXT_SUB, lw=1.2, linestyle='-', zorder=4)
    ax1.plot([dim_x1 - 0.10, dim_x1 + 0.10], [y_bot1, y_bot1], color=TEXT_SUB, lw=1.2, zorder=4)
    ax1.plot([dim_x1 - 0.10, dim_x1 + 0.10], [y_top1, y_top1], color=TEXT_SUB, lw=1.2, zorder=4)
    ax1.text(dim_x1 - 0.12, c1_y, r"Length $L_1$", fontsize=11.8, color='#cbd5e1',
             fontweight='bold', ha='right', va='center', rotation=90, zorder=5)

    # =========================================================================
    # RIGHT PANEL: After Stretching
    # =========================================================================
    ax2 = fig.add_subplot(gs_mid[0, 1])
    ax2.set_facecolor(PANEL_BG)
    for s in ax2.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.3)
    ax2.set_xlim(-3.6, 3.6)
    ax2.set_ylim(-2.5, 2.5)
    ax2.set_aspect('equal')
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.grid(False)
    
    # Header & Question
    ax2.text(0.04, 0.95, "Stretched Vortex Tube (t = t₂)",
             transform=ax2.transAxes, fontsize=14.8, fontweight='bold',
             color=TEXT_TITLE, va='top')
    ax2.text(0.04, 0.88, r"“Elongated axis, constricted radius, intensified vorticity”",
             transform=ax2.transAxes, fontsize=11.8,
             color=AMPLIF_COL, va='top')

    # Tube Geometry 2: Positioned at x = -1.70 to provide ample room for labels and card
    c2_x, c2_y = -1.70, -0.45
    r2 = 0.50
    h2 = 2.45
    y_bot2 = c2_y - 0.5 * h2
    y_top2 = c2_y + 0.5 * h2
    
    # Draw cylinder 2 body with shading
    for i in range(n_layers):
        frac = i / (n_layers - 1)
        shading_alpha = 0.08 + 0.22 * np.sin(frac * np.pi)
        rect = patches.Rectangle((c2_x - r2 + (2*r2/n_layers)*i, y_bot2), 2*r2/n_layers, h2,
                                 facecolor='#e11d48', edgecolor='none', alpha=shading_alpha, zorder=2)
        ax2.add_patch(rect)
        
    # Side walls
    ax2.plot([c2_x - r2, c2_x - r2], [y_bot2, y_top2], color=AMPLIF_COL, lw=2.4, zorder=4)
    ax2.plot([c2_x + r2, c2_x + r2], [y_bot2, y_top2], color=AMPLIF_COL, lw=2.4, zorder=4)
    
    # Bottom elliptical cap
    b2_ell_back = patches.Arc((c2_x, y_bot2), 2*r2, 0.50*r2, angle=0, theta1=0, theta2=180,
                              color=AMPLIF_COL, lw=1.5, linestyle=':', alpha=0.6, zorder=3)
    b2_ell_front = patches.Arc((c2_x, y_bot2), 2*r2, 0.50*r2, angle=0, theta1=180, theta2=360,
                               color=AMPLIF_COL, lw=2.2, zorder=4)
    ax2.add_patch(b2_ell_back)
    ax2.add_patch(b2_ell_front)
    
    # Top elliptical cap
    t2_ell = Ellipse((c2_x, y_top2), 2*r2, 0.50*r2, facecolor='#25121b', edgecolor=AMPLIF_COL,
                     lw=2.2, alpha=0.94, zorder=5)
    ax2.add_patch(t2_ell)
    
    # Radius callout at top (placed clearly to the right of the cylinder cap)
    ax2.plot([c2_x, c2_x + r2], [y_top2, y_top2], color='#ffffff', lw=1.5, linestyle='--', zorder=6)
    ax2.plot([c2_x], [y_top2], 'o', color='#ffffff', markersize=4.0, zorder=7)
    ax2.text(c2_x + r2 + 0.10, y_top2 + 0.02, r"$R_2 < R_1$", color='#ffffff', fontsize=11.6, fontweight='bold', ha='left', va='center', zorder=8)

    # Core vorticity vector (omega_2) - Clean, intensified solid gold arrow
    ax2.annotate('', xy=(c2_x, y_top2 + 0.48), xytext=(c2_x, y_bot2 - 0.16),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.54,head_length=0.82",
                                 color='#fbbf24', lw=4.6, mutation_scale=18), zorder=8)
    ax2.text(c2_x - 0.18, y_top2 + 0.52, r"$\|\boldsymbol{\omega}_2\| > \|\boldsymbol{\omega}_1\|$",
             fontsize=14.5, fontweight='bold', color='#fbbf24', ha='right', va='center', zorder=9)
    ax2.text(c2_x - 0.18, y_top2 + 0.30, "(Amplified Vorticity)",
             fontsize=10.8, color=AMPLIF_COL, fontweight='bold', ha='right', va='center', zorder=9)

    # Intense Swirl Rings around narrow cylinder (styled with clear cyan arrows)
    swirl_ys_2 = [y_bot2 + 0.22*h2, y_bot2 + 0.50*h2, y_bot2 + 0.78*h2]
    for sy in swirl_ys_2:
        arc_b = patches.Arc((c2_x, sy), 2.2*r2, 0.54*r2, angle=0, theta1=0, theta2=180,
                            color=SWIRL_COL, lw=1.6, linestyle=':', alpha=0.5, zorder=3)
        arc_f = patches.Arc((c2_x, sy), 2.2*r2, 0.54*r2, angle=0, theta1=180, theta2=360,
                            color=SWIRL_COL, lw=2.5, zorder=6)
        ax2.add_patch(arc_b)
        ax2.add_patch(arc_f)
        ax2.annotate('', xy=(c2_x + 0.48*r2, sy - 0.25*r2), xytext=(c2_x - 0.10*r2, sy - 0.27*r2),
                     arrowprops=dict(arrowstyle="-|>,head_width=0.32,head_length=0.50",
                                     color=SWIRL_COL, lw=2.4, mutation_scale=12), zorder=7)
                     
    # Compact two-line swirl label preventing any overlap with right card
    ax2.text(c2_x + 1.25*r2, swirl_ys_2[1] + 0.12, "Intense swirl\n" + r"$\mathbf{u}_\theta \uparrow\uparrow$",
             fontsize=11.0, color=SWIRL_COL, fontweight='bold', ha='left', va='center', zorder=8)

    # AXIAL STRETCHING ARROWS (External strain pulling cylinder ends)
    # Pulling up at top (starts clearly above omega_2 tip)
    ax2.annotate('', xy=(c2_x, y_top2 + 0.90), xytext=(c2_x, y_top2 + 0.62),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.38,head_length=0.55",
                                 color=STRETCH_COL, lw=2.8, mutation_scale=14), zorder=9)
    ax2.text(c2_x + 0.22, y_top2 + 0.76, r"Axial strain $\frac{\partial u_3}{\partial x_3} > 0$",
             fontsize=10.8, color=STRETCH_COL, fontweight='bold', ha='left', va='center', zorder=9)
             
    # Pulling down at bottom (starts clearly below omega_2 tail)
    ax2.annotate('', xy=(c2_x, y_bot2 - 0.54), xytext=(c2_x, y_bot2 - 0.24),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.38,head_length=0.55",
                                 color=STRETCH_COL, lw=2.8, mutation_scale=14), zorder=9)

    # Lateral radial contraction arrows (inward pointing)
    mid_sy = c2_y - 0.32
    # Left arrow
    ax2.annotate('', xy=(c2_x - r2 - 0.05, mid_sy), xytext=(c2_x - r2 - 0.32, mid_sy),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.34,head_length=0.48",
                                 color=EMERALD_COL, lw=2.2, mutation_scale=12), zorder=9)
    # Right arrow & label
    ax2.annotate('', xy=(c2_x + r2 + 0.05, mid_sy), xytext=(c2_x + r2 + 0.32, mid_sy),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.34,head_length=0.48",
                                 color=EMERALD_COL, lw=2.2, mutation_scale=12), zorder=9)
    ax2.text(c2_x + r2 + 0.36, mid_sy, "Radial\nContraction", fontsize=10.2, color=EMERALD_COL,
             fontweight='bold', ha='left', va='center', zorder=10)

    # Dimension line for Length L2 (placed cleanly on the left)
    dim_x2 = c2_x - r2 - 0.42
    ax2.plot([dim_x2, dim_x2], [y_bot2, y_top2], color=TEXT_SUB, lw=1.2, linestyle='-', zorder=4)
    ax2.plot([dim_x2 - 0.10, dim_x2 + 0.10], [y_bot2, y_bot2], color=TEXT_SUB, lw=1.2, zorder=4)
    ax2.plot([dim_x2 - 0.10, dim_x2 + 0.10], [y_top2, y_top2], color=TEXT_SUB, lw=1.2, zorder=4)
    ax2.text(dim_x2 - 0.12, c2_y + 0.35, r"Length $L_2 > L_1$", fontsize=11.8, color='#cbd5e1',
             fontweight='bold', ha='right', va='center', rotation=90, zorder=5)

    # MECHANISM SUMMARY CARD (Right Side inside Panel 2 - Spaced with generous breathing room)
    card_x, card_y = 0.45, -1.45
    card_w, card_h = 3.05, 2.45
    card_box = FancyBboxPatch((card_x, card_y), card_w, card_h,
                              boxstyle="round,pad=0.08,rounding_size=0.16",
                              facecolor=CARD_BG, edgecolor=BORDER_COL, linewidth=1.3, alpha=0.96, zorder=11)
    ax2.add_patch(card_box)
    ax2.text(card_x + 0.15, card_y + card_h - 0.20,
             "Vorticity Equation",
             fontsize=12.5, fontweight='bold', color=TEXT_TITLE, ha='left', va='center', zorder=12)
    ax2.text(card_x + 0.15, card_y + card_h - 0.48,
             r"$\frac{D\boldsymbol{\omega}}{Dt} = (\boldsymbol{\omega}\cdot\nabla)\mathbf{u} + \nu\Delta\boldsymbol{\omega} + \nabla\times\mathbf{f}$",
             fontsize=10.8, color=OMEGA_COL, ha='left', va='center', zorder=12)
             
    ax2.plot([card_x + 0.15, card_x + card_w - 0.15], [card_y + card_h - 0.64, card_y + card_h - 0.64],
             color=BORDER_COL, lw=1.0, zorder=12)

    ax2.text(card_x + 0.15, card_y + card_h - 0.82,
             r"$\mathbf{1.\ Stretching:}$",
             fontsize=11.2, color='#c084fc', fontweight='bold', va='top', zorder=12)
    ax2.text(card_x + 0.15, card_y + card_h - 1.04,
             r"$(\boldsymbol{\omega}\cdot\nabla)\mathbf{u}$ elongates the tube",
             fontsize=10.5, color='#cbd5e1', va='top', zorder=12)

    ax2.text(card_x + 0.15, card_y + card_h - 1.32,
             r"$\mathbf{2.\ Incompressibility:}$",
             fontsize=11.2, color=EMERALD_COL, fontweight='bold', va='top', zorder=12)
    ax2.text(card_x + 0.15, card_y + card_h - 1.54,
             r"$R \downarrow$ as $L \uparrow$  $(\pi R_2^2 L_2 = \pi R_1^2 L_1)$",
             fontsize=10.5, color='#cbd5e1', va='top', zorder=12)

    ax2.text(card_x + 0.15, card_y + card_h - 1.82,
             r"$\mathbf{3.\ Amplification:}$",
             fontsize=11.2, color=AMPLIF_COL, fontweight='bold', va='top', zorder=12)
    ax2.text(card_x + 0.15, card_y + card_h - 2.04,
             r"$\|\boldsymbol{\omega}_2\| > \|\boldsymbol{\omega}_1\|$" + "  " + r"(idealized: $|\boldsymbol{\omega}| \propto 1/R^2$)",
             fontsize=10.2, color=AMPLIF_COL, va='top', zorder=12)

    # -------------------------------------------------------------------------
    # ROW 2: BOTTOM MATHEMATICAL SYNTHESIS STRIP
    # -------------------------------------------------------------------------
    ax_bar = fig.add_subplot(gs[2, 0])
    ax_bar.set_facecolor(CARD_BG)
    for spine in ax_bar.spines.values():
        spine.set_edgecolor(BORDER_COL)
        spine.set_linewidth(1.4)
    ax_bar.set_xlim(0, 100)
    ax_bar.set_ylim(0, 100)
    ax_bar.axis('off')

    # Rounded background container
    bar_bg = FancyBboxPatch((0.5, 3), 99, 94,
                            boxstyle="round,pad=0.2,rounding_size=1.5",
                            facecolor="#0f172a", edgecolor=BORDER_COL, linewidth=1.4, zorder=1)
    ax_bar.add_patch(bar_bg)

    # 3 Synthesis Pillars:
    # 1. Axial Stretching Term
    # 2. Incompressibility & Volume Conservation
    # 3. Axial Stretching Amplifies Vorticity
    
    # Pillar 1: Axial Stretching Term
    b1 = FancyBboxPatch((3.0, 10.0), 28.0, 80.0,
                         boxstyle="round,pad=0.2,rounding_size=1.2",
                         facecolor="#1e1b4b", edgecolor=STRETCH_COL, linewidth=1.4, zorder=2)
    ax_bar.add_patch(b1)
    ax_bar.text(17.0, 74.0, r"$(\boldsymbol{\omega}\cdot\nabla)\mathbf{u}$",
                fontsize=16.0, fontweight='bold', color='#c084fc', ha='center', va='center', zorder=3)
    ax_bar.text(17.0, 51.0, "Axial Stretching by Flow",
                fontsize=11.8, fontweight='bold', color=TEXT_TITLE, ha='center', va='center', zorder=3)
    ax_bar.text(17.0, 28.0, "Velocity gradients stretch fluid\nparcels along the vortex axis",
                fontsize=10.4, color='#e2e8f0', linespacing=1.3, ha='center', va='center', zorder=3)

    # Operator ⟹
    ax_bar.text(33.5, 50.0, "⟹", fontsize=26.0, fontweight='bold', color='#64748b', ha='center', va='center', zorder=3)

    # Pillar 2: Incompressibility & Geometric Thinning
    b2 = FancyBboxPatch((36.0, 10.0), 28.0, 80.0,
                         boxstyle="round,pad=0.2,rounding_size=1.2",
                         facecolor="#064e3b", edgecolor=EMERALD_COL, linewidth=1.4, zorder=2)
    ax_bar.add_patch(b2)
    ax_bar.text(50.0, 74.0, r"$\nabla\cdot\mathbf{u} = 0$",
                fontsize=16.0, fontweight='bold', color='#34d399', ha='center', va='center', zorder=3)
    ax_bar.text(50.0, 51.0, "Volume Conservation",
                fontsize=11.8, fontweight='bold', color=TEXT_TITLE, ha='center', va='center', zorder=3)
    ax_bar.text(50.0, 28.0, "For a material fluid tube, incompressibility forces\nthe cross-section to contract as tube elongates",
                fontsize=10.2, color='#e2e8f0', linespacing=1.3, ha='center', va='center', zorder=3)

    # Operator ⟹
    ax_bar.text(66.5, 50.0, "⟹", fontsize=26.0, fontweight='bold', color='#64748b', ha='center', va='center', zorder=3)

    # Pillar 3: Axial Stretching Amplifies Vorticity
    b3 = FancyBboxPatch((69.0, 10.0), 28.0, 80.0,
                         boxstyle="round,pad=0.2,rounding_size=1.2",
                         facecolor="#4c0519", edgecolor=AMPLIF_COL, linewidth=1.4, zorder=2)
    ax_bar.add_patch(b3)
    ax_bar.text(83.0, 74.0, r"$\|\boldsymbol{\omega}_2\| > \|\boldsymbol{\omega}_1\|$",
                fontsize=16.0, fontweight='bold', color='#fb7185', ha='center', va='center', zorder=3)
    ax_bar.text(83.0, 51.0, "Stretching Amplifies Vorticity",
                fontsize=11.8, fontweight='bold', color=TEXT_TITLE, ha='center', va='center', zorder=3)
    ax_bar.text(83.0, 28.0, "As tube elongates & cross-section contracts,\nstretching increases axial vorticity",
                fontsize=10.4, color='#ffe4e6', linespacing=1.3, ha='center', va='center', zorder=3)

    # out_path is provided via function argument
    plt.savefig(out_path, dpi=240, bbox_inches='tight', facecolor=CANVAS_BG, edgecolor='none')
    plt.close()
    print(f"[OK] Generated Vortex Stretching Infographic: {out_path}")
    return out_path

generate_vortex_stretching_infographic = create_vortex_stretching_figure

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    create_vortex_stretching_figure(target)
