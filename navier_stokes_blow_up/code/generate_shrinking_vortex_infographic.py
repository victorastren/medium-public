from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "navier_stokes_shrinking_vortex_blowup.png"

#!/usr/bin/env python3
"""
Generate infographic:
"Shrinking Vortex Approaching the Singular Time"
for the Medium article on the 3D Navier-Stokes Millennium Problem.

Scientific & Presentation Refinements:
- Stage 1: Approaching Blow-Up (larger tau = 1 - t), avoiding tau ~ 1
- Stage 2: Rapid Contraction (smaller tau)
- Stage 3: Finite-Time Singularity (tau -> 0)
- Precise velocity components: dominant |u_theta|, |u_z| ~ tau^(-1/2-h) -> inf
- Core energy: E_core ~ tau^(1/2-3h) -> 0 with actual proof range 0 < h < 1/100
- Restrained, restrained scientific tone without exclamation marks
- High-contrast, large-type bottom synthesis boxes optimized for Medium's 680px column width
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Ellipse, Arc
import numpy as np

def draw_vortex_snapshot(ax, cx, cy, r, h, color, col_glow,
                         lr_label, lz_label, bracket_side='right',
                         arrow_scale=1.0, is_blowup=False):
    """Draws one snapshot of the contracting vortex with inflow, outflow, and dimension markers."""
    y_bot = cy - 0.5 * h
    y_top = cy + 0.5 * h

    # 1. Background core glow
    n_glow = 20
    for g in range(n_glow, 0, -1):
        g_rad = r * (1.0 + 0.55 * (g / n_glow))
        g_h = h * (1.0 + 0.15 * (g / n_glow))
        g_alpha = 0.018 * (1.0 - g / n_glow) if not is_blowup else 0.048 * (1.0 - g / n_glow)
        glow_rect = patches.Rectangle((cx - g_rad, cy - 0.5 * g_h), 2 * g_rad, g_h,
                                      facecolor=col_glow, edgecolor='none', alpha=g_alpha, zorder=1)
        ax.add_patch(glow_rect)

    # 2. Cylinder body shading (3D cylindrical lighting)
    n_layers = 36
    for i in range(n_layers):
        frac = i / (n_layers - 1)
        shading = 0.14 + 0.52 * np.sin(frac * np.pi) ** 1.6
        layer_x = cx - r + (2 * r / n_layers) * i
        layer_w = 2 * r / n_layers
        rect = patches.Rectangle((layer_x, y_bot), layer_w, h,
                                 facecolor=color, edgecolor='none', alpha=shading, zorder=2)
        ax.add_patch(rect)

    # 3. Lateral cylinder edges
    ax.plot([cx - r, cx - r], [y_bot, y_top], color=color, lw=2.2 if not is_blowup else 3.0, zorder=4)
    ax.plot([cx + r, cx + r], [y_bot, y_top], color=color, lw=2.2 if not is_blowup else 3.0, zorder=4)

    # 4. Elliptical caps
    cap_height = max(0.24 * r, 0.07)
    # Bottom cap (back dashed, front solid)
    b_back = Arc((cx, y_bot), 2 * r, cap_height, angle=0, theta1=0, theta2=180,
                 color=color, lw=1.5, linestyle=':', alpha=0.5, zorder=3)
    b_front = Arc((cx, y_bot), 2 * r, cap_height, angle=0, theta1=180, theta2=360,
                  color=color, lw=2.2, zorder=4)
    ax.add_patch(b_back)
    ax.add_patch(b_front)

    # Top cap (illuminated)
    t_cap = Ellipse((cx, y_top), 2 * r, cap_height, facecolor='#101828', edgecolor=color,
                    lw=2.2 if not is_blowup else 2.8, alpha=0.96, zorder=5)
    ax.add_patch(t_cap)

    # Central vortex core axis line
    ax.plot([cx, cx], [y_bot, y_top], color='#ffffff' if is_blowup else col_glow,
            lw=1.8 if not is_blowup else 3.4, linestyle='-' if is_blowup else '--',
            alpha=0.95, zorder=6)

    # 5. Radial Inflow Arrows (pointing inward toward axis from both sides)
    inflow_ys = [cy - 0.28 * h, cy + 0.28 * h]
    inflow_len = max(0.48 * arrow_scale, 0.42)
    for iy in inflow_ys:
        # Left inflow
        ax.annotate('', xy=(cx - r - 0.05, iy), xytext=(cx - r - inflow_len, iy),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.32,head_length=0.48",
                                    color='#38bdf8', lw=2.1 * arrow_scale, mutation_scale=13), zorder=7)
        # Right inflow
        ax.annotate('', xy=(cx + r + 0.05, iy), xytext=(cx + r + inflow_len, iy),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.32,head_length=0.48",
                                    color='#38bdf8', lw=2.1 * arrow_scale, mutation_scale=13), zorder=7)

    # 6. Axial Outflow Arrows (pointing vertically away from center, top and bottom)
    outflow_len = max(0.55 * arrow_scale, 0.48)
    # Top outflow (upward)
    ax.annotate('', xy=(cx, y_top + outflow_len), xytext=(cx, y_top + 0.04),
                arrowprops=dict(arrowstyle="-|>,head_width=0.36,head_length=0.55",
                                color='#c084fc', lw=2.3 * arrow_scale, mutation_scale=14), zorder=7)
    # Bottom outflow (downward)
    ax.annotate('', xy=(cx, y_bot - outflow_len), xytext=(cx, y_bot - 0.04),
                arrowprops=dict(arrowstyle="-|>,head_width=0.36,head_length=0.55",
                                color='#c084fc', lw=2.3 * arrow_scale, mutation_scale=14), zorder=7)

    # 7. Azimuthal Swirl Rings (rotation around vortex tube)
    swirl_ys = [cy - 0.10 * h, cy + 0.10 * h]
    for sy in swirl_ys:
        swirl_w = 2.2 * r
        swirl_h = max(0.38 * r, 0.09)
        s_b = Arc((cx, sy), swirl_w, swirl_h, angle=0, theta1=0, theta2=180,
                  color=col_glow, lw=1.3, linestyle=':', alpha=0.4, zorder=3)
        s_f = Arc((cx, sy), swirl_w, swirl_h, angle=0, theta1=180, theta2=360,
                  color=col_glow, lw=2.2 if not is_blowup else 2.8, zorder=6)
        ax.add_patch(s_b)
        ax.add_patch(s_f)
        # Arrowhead on front swirl
        ax.annotate('', xy=(cx + 0.35 * r, sy - 0.5 * swirl_h),
                    xytext=(cx - 0.25 * r, sy - 0.5 * swirl_h),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.26,head_length=0.40",
                                    color=col_glow, lw=2.1 if not is_blowup else 2.7, mutation_scale=11), zorder=7)

    # 8. Dimension Callouts: ell_r and ell_z
    # Radius dimension on top cap
    callout_y = y_top + 0.03
    ax.plot([cx, cx + r], [callout_y, callout_y], color='#ffffff', lw=1.5, linestyle='-', zorder=8)
    ax.plot([cx], [callout_y], 'o', color='#ffffff', markersize=3.5, zorder=9)
    ax.plot([cx + r], [callout_y], 'o', color='#ffffff', markersize=3.5, zorder=9)
    ax.text(cx + 0.5 * r, callout_y + 0.10, lr_label, color='#ffffff', fontsize=11.4,
            fontweight='bold', ha='center', va='bottom', zorder=10)

    # Axial length bracket
    if bracket_side == 'right':
        bracket_x = cx + r + inflow_len + 0.16
        ax.plot([bracket_x, bracket_x], [y_bot, y_top], color='#94a3b8', lw=1.3, zorder=5)
        ax.plot([bracket_x - 0.07, bracket_x + 0.07], [y_bot, y_bot], color='#94a3b8', lw=1.3, zorder=5)
        ax.plot([bracket_x - 0.07, bracket_x + 0.07], [y_top, y_top], color='#94a3b8', lw=1.3, zorder=5)
        ax.text(bracket_x + 0.09, cy, lz_label, color='#cbd5e1', fontsize=11.2,
                fontweight='bold', ha='left', va='center', rotation=90, zorder=6)
    else:
        bracket_x = cx - r - inflow_len - 0.16
        ax.plot([bracket_x, bracket_x], [y_bot, y_top], color='#94a3b8', lw=1.3, zorder=5)
        ax.plot([bracket_x - 0.07, bracket_x + 0.07], [y_bot, y_bot], color='#94a3b8', lw=1.3, zorder=5)
        ax.plot([bracket_x - 0.07, bracket_x + 0.07], [y_top, y_top], color='#94a3b8', lw=1.3, zorder=5)
        ax.text(bracket_x - 0.09, cy, lz_label, color='#cbd5e1', fontsize=11.2,
                fontweight='bold', ha='right', va='center', rotation=90, zorder=6)


def create_shrinking_vortex_figure(out_path=None):
    if out_path is None:
        out_path = DEFAULT_OUT
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(16, 9.6), dpi=240, facecolor='#070b12')

    CANVAS_BG   = '#070b12'
    PANEL_BG    = '#0c1322'
    CARD_BG     = '#101828'
    BORDER_COL  = '#1e293b'
    TEXT_TITLE  = '#f8fafc'
    TEXT_SUB    = '#94a3b8'

    CYAN_COL    = '#38bdf8'
    AMBER_COL   = '#fbbf24'
    ROSE_COL    = '#f43f5e'
    PURPLE_COL  = '#c084fc'
    EMERALD_COL = '#34d399'

    # -------------------------------------------------------------------------
    # TITLE BANNER
    # -------------------------------------------------------------------------
    tag_box = FancyBboxPatch((0.36, 0.950), 0.28, 0.032,
                             boxstyle="round,pad=0.006,rounding_size=0.015",
                             facecolor='#1e293b', edgecolor=BORDER_COL,
                             transform=fig.transFigure, lw=1.0)
    fig.patches.append(tag_box)
    fig.text(0.50, 0.965, "BLOW-UP GEOMETRY & ASYMPTOTIC SCALING",
             fontsize=10.2, fontweight='bold', color=CYAN_COL,
             ha='center', va='center')

    fig.text(0.50, 0.915, "SHRINKING VORTEX APPROACHING THE SINGULAR TIME",
             fontsize=18.0, fontweight='bold', color=TEXT_TITLE, ha='center', va='center')
    fig.text(0.50, 0.880,
             r"As $\tau = 1 - t \to 0$, the vortex core contracts, the peak velocity becomes unbounded, while the core energy tends to zero",
             fontsize=11.8, fontstyle='italic', color=TEXT_SUB, ha='center', va='center')

    # -------------------------------------------------------------------------
    # MAIN 3-PANEL SEQUENCE (t < 1  -->  closer to t = 1  -->  t -> 1^-)
    # -------------------------------------------------------------------------
    gs = fig.add_gridspec(2, 3, height_ratios=[0.67, 0.22],
                          left=0.04, right=0.96, bottom=0.04, top=0.84,
                          wspace=0.10, hspace=0.18)

    # -------------------------------------------------------------------------
    # PANEL 1: Stage 1: Approaching Blow-Up (larger tau)
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor(PANEL_BG)
    for s in ax1.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.3)
    ax1.set_xlim(-2.7, 2.7)
    ax1.set_ylim(-2.6, 2.6)
    ax1.set_aspect('equal')
    ax1.set_xticks([])
    ax1.set_yticks([])

    # Header Card 1 (Requested: Stage 1: Approaching Blow-Up, larger tau = 1 - t)
    ax1.text(0.06, 0.94, "Stage 1: Approaching Blow-Up", transform=ax1.transAxes,
             fontsize=14.0, fontweight='bold', color=TEXT_TITLE, va='top')
    ax1.text(0.06, 0.87, r"Larger $\tau = 1 - t$", transform=ax1.transAxes,
             fontsize=12.2, fontweight='bold', color=CYAN_COL, va='top')
    ax1.text(0.06, 0.79, "Earlier contracting stage · lower characteristic velocity", transform=ax1.transAxes,
             fontsize=10.4, fontstyle='italic', color=TEXT_SUB, va='top')

    # Tube 1: Wide radius (r=1.05), moderate height (h=1.55)
    draw_vortex_snapshot(ax1, cx=-0.05, cy=-0.22, r=1.05, h=1.55,
                         color='#0284c7', col_glow=CYAN_COL,
                         lr_label=r"$\ell_r \sim \tau^{1/2}$",
                         lz_label=r"$\ell_z \sim \tau^{1/2-h}$",
                         bracket_side='right',
                         arrow_scale=1.0, is_blowup=False)

    # Inflow / Outflow text annotations
    ax1.text(-1.32, 0.35, r"Inflow $u_r < 0$", fontsize=10.2, color=CYAN_COL, fontweight='bold', ha='right', zorder=10)
    ax1.text(-0.22, 0.95, r"Outflow $u_z > 0$", fontsize=10.2, color=PURPLE_COL, fontweight='bold', ha='right', zorder=10)

    # Bottom metric badge for Panel 1
    badge1 = FancyBboxPatch((-2.48, -2.48), 4.96, 0.76,
                            boxstyle="round,pad=0.04,rounding_size=0.10",
                            facecolor=CARD_BG, edgecolor=BORDER_COL, lw=1.2, zorder=8)
    ax1.add_patch(badge1)
    ax1.text(-2.28, -1.94, r"Velocity: bounded across the core",
             fontsize=10.4, color='#e2e8f0', fontweight='bold', va='center', zorder=10)
    ax1.text(-2.28, -2.26, r"Core volume: $V \sim \ell_r^2 \ell_z \sim \tau^{3/2-h}$",
             fontsize=9.8, color=TEXT_SUB, va='center', zorder=10)

    # -------------------------------------------------------------------------
    # PANEL 2: Stage 2: Rapid Contraction (smaller tau)
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor(PANEL_BG)
    for s in ax2.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.3)
    ax2.set_xlim(-2.7, 2.7)
    ax2.set_ylim(-2.6, 2.6)
    ax2.set_aspect('equal')
    ax2.set_xticks([])
    ax2.set_yticks([])

    # Header Card 2 (Requested: Stage 2: Rapid Contraction, smaller tau)
    ax2.text(0.06, 0.94, "Stage 2: Rapid Contraction", transform=ax2.transAxes,
             fontsize=14.0, fontweight='bold', color=TEXT_TITLE, va='top')
    ax2.text(0.06, 0.87, r"Smaller $\tau$", transform=ax2.transAxes,
             fontsize=12.2, fontweight='bold', color=AMBER_COL, va='top')
    ax2.text(0.06, 0.79, "Radial compression faster than axial", transform=ax2.transAxes,
             fontsize=10.4, fontstyle='italic', color=TEXT_SUB, va='top')

    # Tube 2: Thinner radius (r=0.52), elongated height (h=1.90)
    draw_vortex_snapshot(ax2, cx=-0.05, cy=-0.22, r=0.52, h=1.90,
                         color='#d97706', col_glow=AMBER_COL,
                         lr_label=r"$\ell_r \sim \tau^{1/2}$",
                         lz_label=r"$\ell_z \sim \tau^{1/2-h}$",
                         bracket_side='right',
                         arrow_scale=1.20, is_blowup=False)

    # Inflow / Outflow text annotations
    ax2.text(-0.85, 0.45, r"Radial inflow $|u_r| \uparrow$", fontsize=10.2, color=AMBER_COL, fontweight='bold', ha='right', zorder=10)
    ax2.text(-0.22, 1.05, r"Outflow $|u_z| \uparrow$", fontsize=10.2, color=PURPLE_COL, fontweight='bold', ha='right', zorder=10)

    # Bottom metric badge for Panel 2
    badge2 = FancyBboxPatch((-2.48, -2.48), 4.96, 0.76,
                            boxstyle="round,pad=0.04,rounding_size=0.10",
                            facecolor=CARD_BG, edgecolor=BORDER_COL, lw=1.2, zorder=8)
    ax2.add_patch(badge2)
    ax2.text(-2.28, -1.94, r"Velocity: accelerating sharply",
             fontsize=10.4, color='#e2e8f0', fontweight='bold', va='center', zorder=10)
    ax2.text(-2.28, -2.26, r"Aspect ratio: $\ell_z / \ell_r \sim \tau^{-h} \uparrow$ (thinning & elongating)",
             fontsize=9.8, color=AMBER_COL, va='center', zorder=10)

    # -------------------------------------------------------------------------
    # PANEL 3: Stage 3: Finite-Time Singularity (tau -> 0)
    # -------------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_facecolor(PANEL_BG)
    for s in ax3.spines.values():
        s.set_edgecolor('#e11d48')
        s.set_linewidth(1.6)
    ax3.set_xlim(-2.7, 2.7)
    ax3.set_ylim(-2.6, 2.6)
    ax3.set_aspect('equal')
    ax3.set_xticks([])
    ax3.set_yticks([])

    # Header Card 3 (Requested: Stage 3: Finite-Time Singularity, tau -> 0)
    ax3.text(0.06, 0.94, "Stage 3: Finite-Time Singularity", transform=ax3.transAxes,
             fontsize=14.0, fontweight='bold', color='#fda4af', va='top')
    ax3.text(0.06, 0.87, r"$\tau \to 0 \quad (t \to 1^-)$", transform=ax3.transAxes,
             fontsize=12.2, fontweight='bold', color=ROSE_COL, va='top')
    ax3.text(0.06, 0.79, "Needle-like filament · velocity blow-up", transform=ax3.transAxes,
             fontsize=10.4, fontstyle='italic', color='#fecdd3', va='top')

    # Tube 3: Needle-thin radius (r=0.14), slender height (h=2.25)
    draw_vortex_snapshot(ax3, cx=-0.45, cy=-0.22, r=0.14, h=2.25,
                         color='#e11d48', col_glow=ROSE_COL,
                         lr_label=r"$\ell_r \to 0$",
                         lz_label=r"$\ell_z \to 0$",
                         bracket_side='left',
                         arrow_scale=1.45, is_blowup=True)

    # Callout Card: Precise velocity components as requested
    callout_box = FancyBboxPatch((0.08, -0.32), 2.48, 1.05,
                                 boxstyle="round,pad=0.05,rounding_size=0.10",
                                 facecolor='#4c0519', edgecolor=ROSE_COL, lw=1.6, zorder=8)
    ax3.add_patch(callout_box)
    ax3.text(1.32, 0.44, "DOMINANT VELOCITY:",
             fontsize=9.2, color='#fca5a5', fontweight='bold', ha='center', va='center', zorder=9)
    ax3.text(1.32, 0.14, r"$|u_\theta|,\, |u_z| \sim \tau^{-1/2-h} \to \infty$",
             fontsize=11.2, color='#ffffff', fontweight='bold', ha='center', va='center', zorder=9)
    ax3.text(1.32, -0.16, "Peak velocity becomes unbounded",
             fontsize=9.4, color='#fecdd3', fontstyle='italic', ha='center', va='center', zorder=9)

    # Inflow / Outflow text annotations
    ax3.text(-0.80, 0.68, "Radial inflow", fontsize=10.2, color=ROSE_COL, fontweight='bold', ha='right', zorder=10)
    ax3.text(-0.80, 0.49, r"$|u_r| = O(\tau^{-1/2})$", fontsize=10.0, color='#fca5a5', ha='right', zorder=10)
    ax3.text(-0.62, 1.15, r"Axial jets $|u_z| \to \infty$", fontsize=10.2, color=PURPLE_COL, fontweight='bold', ha='right', zorder=10)

    # Bottom metric badge for Panel 3 (Requested: 0 < h < 1/100 and clean unbounded text)
    badge3 = FancyBboxPatch((-2.48, -2.48), 4.96, 0.76,
                            boxstyle="round,pad=0.04,rounding_size=0.10",
                            facecolor=CARD_BG, edgecolor='#e11d48', lw=1.3, zorder=8)
    ax3.add_patch(badge3)
    ax3.text(-2.28, -1.94, r"Peak velocity becomes unbounded as $t \to 1^-$",
             fontsize=10.5, color='#fecdd3', fontweight='bold', va='center', zorder=10)
    ax3.text(-2.28, -2.26, r"Core Energy: $E_{\mathrm{core}} \sim \tau^{1/2-3h} \to 0$  (since $0 < h < 1/100$)",
             fontsize=9.8, color=EMERALD_COL, fontweight='bold', va='center', zorder=10)

    # Transitional indicator badges between panels (in figure coords)
    t1_box = FancyBboxPatch((0.332, 0.49), 0.044, 0.078,
                            boxstyle="round,pad=0.004,rounding_size=0.012",
                            facecolor='#101828', edgecolor=BORDER_COL,
                            transform=fig.transFigure, lw=1.2)
    fig.patches.append(t1_box)
    fig.text(0.354, 0.544, r"$\tau \downarrow$", fontsize=11.6, fontweight='bold', color=CYAN_COL, ha='center', va='center')
    fig.text(0.354, 0.510, r"$\longrightarrow$", fontsize=12.2, fontweight='bold', color=TEXT_SUB, ha='center', va='center')

    t2_box = FancyBboxPatch((0.640, 0.49), 0.044, 0.078,
                            boxstyle="round,pad=0.004,rounding_size=0.012",
                            facecolor='#101828', edgecolor='#881337',
                            transform=fig.transFigure, lw=1.2)
    fig.patches.append(t2_box)
    fig.text(0.662, 0.544, r"$\tau \to 0$", fontsize=11.6, fontweight='bold', color=ROSE_COL, ha='center', va='center')
    fig.text(0.662, 0.510, r"$\longrightarrow$", fontsize=12.2, fontweight='bold', color=ROSE_COL, ha='center', va='center')

    # -------------------------------------------------------------------------
    # BOTTOM SYNTHESIS STRIP (3 SIMPLIFIED HIGH-CONTRAST BOXES FOR MEDIUM 680px)
    # -------------------------------------------------------------------------
    # Pillar 1: Flow Dynamics
    ax_bot1 = fig.add_subplot(gs[1, 0])
    ax_bot1.set_facecolor(CARD_BG)
    for s in ax_bot1.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.3)
    ax_bot1.set_xticks([])
    ax_bot1.set_yticks([])

    ax_bot1.text(0.08, 0.78, "VORTEX DYNAMICS", transform=ax_bot1.transAxes,
                 fontsize=13.6, fontweight='bold', color=CYAN_COL, va='top')
    ax_bot1.text(0.08, 0.46,
                 r"• Inward spiral $\longrightarrow$ azimuthal spin-up" "\n"
                 r"• Incompressibility $\longrightarrow$ axial outflow",
                 transform=ax_bot1.transAxes, fontsize=12.6, color='#e2e8f0', va='top', linespacing=1.50)

    # Pillar 2: Asymptotic Dimensions
    ax_bot2 = fig.add_subplot(gs[1, 1])
    ax_bot2.set_facecolor(CARD_BG)
    for s in ax_bot2.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.3)
    ax_bot2.set_xticks([])
    ax_bot2.set_yticks([])

    ax_bot2.text(0.08, 0.78, "ANISOTROPIC CONTRACTION", transform=ax_bot2.transAxes,
                 fontsize=13.6, fontweight='bold', color=AMBER_COL, va='top')
    ax_bot2.text(0.08, 0.46,
                 r"• $\ell_r \sim \tau^{1/2},\quad \ell_z \sim \tau^{1/2-h}$" "\n"
                 r"• $\ell_z / \ell_r \sim \tau^{-h} \to \infty$",
                 transform=ax_bot2.transAxes, fontsize=12.6, color='#e2e8f0', va='top', linespacing=1.50)

    # Pillar 3: Core Energy
    ax_bot3 = fig.add_subplot(gs[1, 2])
    ax_bot3.set_facecolor(CARD_BG)
    for s in ax_bot3.spines.values():
        s.set_edgecolor(BORDER_COL)
        s.set_linewidth(1.3)
    ax_bot3.set_xticks([])
    ax_bot3.set_yticks([])

    ax_bot3.text(0.08, 0.78, "CORE ENERGY", transform=ax_bot3.transAxes,
                 fontsize=13.6, fontweight='bold', color=EMERALD_COL, va='top')
    ax_bot3.text(0.08, 0.46,
                 r"• $V \sim \tau^{3/2-h},\quad E_{\mathrm{core}} \sim \tau^{1/2-3h} \to 0$" "\n"
                 r"• Total $L^2$ energy remains bounded",
                 transform=ax_bot3.transAxes, fontsize=12.6, color='#e2e8f0', va='top', linespacing=1.50)

    # out_path is provided via function argument
    plt.savefig(out_path, dpi=240, facecolor=CANVAS_BG, edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated {out_path}")
    return out_path

generate_shrinking_vortex_infographic = create_shrinking_vortex_figure

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    create_shrinking_vortex_figure(target)
