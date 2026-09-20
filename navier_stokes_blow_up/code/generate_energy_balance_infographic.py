#!/usr/bin/env python3
"""
Generate infographic for section:
"How Viscosity Dissipates Kinetic Energy"

Title: ENERGY BALANCE IN THE NAVIER–STOKES EQUATIONS
Subtitle: A clean flow diagram showing how each term in the momentum equation governs,
redistributes, dissipates, or injects total kinetic energy E(t).
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "navier_stokes_energy_balance.png"


def create_energy_balance_diagram(out_path=None):
    if out_path is None:
        out_path = DEFAULT_OUT
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 16:9 widescreen canvas
    fig = plt.figure(figsize=(16, 9.4), dpi=240, facecolor='#070b12')

    CANVAS_BG   = '#070b12'
    PANEL_BG    = '#0c1322'
    BORDER_COL  = '#1e293b'
    TEXT_TITLE  = '#f8fafc'
    TEXT_MUTED  = '#94a3b8'

    # Accent colors
    CYAN_COL    = '#38bdf8'  # Energy E(t)
    EMERALD_COL = '#34d399'  # Advection (conservative)
    INDIGO_COL  = '#818cf8'  # Pressure (incompressibility)
    ROSE_COL    = '#f43f5e'  # Viscosity (dissipation sink)
    AMBER_COL   = '#fbbf24'  # Forcing (energy source)

    # -------------------------------------------------------------------------
    # MAIN TITLE BANNER
    # -------------------------------------------------------------------------
    fig.text(0.50, 0.956, "ENERGY BALANCE IN THE NAVIER–STOKES EQUATIONS",
             fontsize=19.5, fontweight='bold', color=TEXT_TITLE, ha='center', va='center')
    # Diagram Subtitle (direct and clear)
    fig.text(0.50, 0.920,
             r"How advection, pressure, viscosity, and forcing redistribute, dissipate, and inject kinetic energy $E(t)$",
             fontsize=13.2, color='#cbd5e1', ha='center', va='center')

    # Main diagram coordinate axes [left, bottom, width, height]
    ax = fig.add_axes([0.035, 0.155, 0.930, 0.740])
    ax.set_facecolor(PANEL_BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER_COL)
        spine.set_linewidth(1.4)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xticks([])
    ax.set_yticks([])

    # Helper function to draw rounded cards
    def draw_card(cx, cy, w, h, bg_col, edge_col, lw=1.5, zorder=2):
        rect = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                              boxstyle="round,pad=0.55,rounding_size=2.2",
                              facecolor=bg_col, edgecolor=edge_col,
                              linewidth=lw, zorder=zorder)
        ax.add_patch(rect)
        return rect

    # Helper function for badges
    def draw_badge(cx, cy, text, bg_col, text_col='#ffffff', pad=0.55, fontsize=10.0, zorder=4):
        bbox_props = dict(boxstyle=f"round,pad={pad},rounding_size=1.2",
                          facecolor=bg_col, edgecolor="none", alpha=0.95)
        ax.text(cx, cy, text, fontsize=fontsize, fontweight='bold',
                color=text_col, ha='center', va='center', bbox=bbox_props, zorder=zorder)

    # -------------------------------------------------------------------------
    # 1. CENTRAL HUB: KINETIC ENERGY PER UNIT DENSITY
    # -------------------------------------------------------------------------
    center_x, center_y = 50.0, 50.0
    hub_w, hub_h = 29.5, 28.0

    # Glow underlay
    draw_card(center_x, center_y, hub_w + 1.4, hub_h + 1.2, '#0c1e38', CYAN_COL, lw=1.0, zorder=1)
    # Main hub card
    draw_card(center_x, center_y, hub_w, hub_h, '#0f172a', CYAN_COL, lw=2.2, zorder=2)

    draw_badge(center_x, center_y + hub_h/2 - 2.3, "KINETIC ENERGY PER UNIT DENSITY", '#0284c7', '#ffffff', fontsize=10.2)

    ax.text(center_x, center_y + 6.2, r"$E(t) = \frac{1}{2}\int_{\Omega} |\mathbf{u}(\mathbf{x}, t)|^2\,d\mathbf{x}$",
            fontsize=18.5, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=3)

    ax.text(center_x, center_y - 0.4, r"$\| \mathbf{u}(t) \|_{L^2(\Omega)}^2 = 2\,E(t)$",
            fontsize=14.5, color=CYAN_COL, ha='center', va='center', zorder=3)

    ax.text(center_x, center_y - 7.0,
            r"Rate of change: $\frac{dE}{dt} = \int_{\Omega} \mathbf{u}\cdot\frac{\partial \mathbf{u}}{\partial t}\,d\mathbf{x}$",
            fontsize=12.6, color='#cbd5e1', ha='center', va='center', zorder=3)

    # Dimensions for 4 outer cards (clean, uncluttered 3-line layout)
    corner_w, corner_h = 24.5, 21.0
    left_cx, right_cx  = 14.0, 86.0
    top_cy, bot_cy     = 74.5, 25.5

    # -------------------------------------------------------------------------
    # 2. TOP-LEFT: NONLINEAR ADVECTION (u . nabla)u
    # -------------------------------------------------------------------------
    draw_card(left_cx, top_cy, corner_w, corner_h, '#0c1a24', EMERALD_COL, lw=1.6, zorder=2)
    draw_badge(left_cx, top_cy + corner_h/2 - 2.1, "NONLINEAR ADVECTION", '#059669', fontsize=10.0)

    ax.text(left_cx, top_cy + 4.2, r"$(\mathbf{u}\cdot\nabla)\mathbf{u}$",
            fontsize=20.0, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=3)

    ax.text(left_cx, top_cy - 0.5, "Redistributes kinetic energy",
            fontsize=13.2, fontweight='bold', color=EMERALD_COL, ha='center', va='center', zorder=3)

    ax.text(left_cx, top_cy - 5.0, "Net global contribution = 0",
            fontsize=12.5, color='#f1f5f9', ha='center', va='center', zorder=3)

    # -------------------------------------------------------------------------
    # 3. TOP-RIGHT: PRESSURE GRADIENT nabla p
    # -------------------------------------------------------------------------
    draw_card(right_cx, top_cy, corner_w, corner_h, '#15152a', INDIGO_COL, lw=1.6, zorder=2)
    draw_badge(right_cx, top_cy + corner_h/2 - 2.1, "PRESSURE", '#4f46e5', fontsize=10.0)

    ax.text(right_cx, top_cy + 4.2, r"$\nabla p$",
            fontsize=21.0, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=3)

    ax.text(right_cx, top_cy - 0.5, "Local pressure work",
            fontsize=13.2, fontweight='bold', color=INDIGO_COL, ha='center', va='center', zorder=3)

    ax.text(right_cx, top_cy - 5.0, "Net global contribution = 0",
            fontsize=12.5, color='#f1f5f9', ha='center', va='center', zorder=3)

    # -------------------------------------------------------------------------
    # 4. BOTTOM-RIGHT: VISCOUS DISSIPATION nu Delta u
    # -------------------------------------------------------------------------
    draw_card(right_cx, bot_cy, corner_w, corner_h, '#1f131a', ROSE_COL, lw=1.8, zorder=2)
    draw_badge(right_cx, bot_cy + corner_h/2 - 2.1, "VISCOUS DISSIPATION", '#e11d48', fontsize=10.0)

    ax.text(right_cx, bot_cy + 4.2, r"$\nu\,\Delta\mathbf{u}$",
            fontsize=20.5, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=3)

    ax.text(right_cx, bot_cy - 0.5, "Removes kinetic energy",
            fontsize=13.2, fontweight='bold', color=ROSE_COL, ha='center', va='center', zorder=3)

    ax.text(right_cx, bot_cy - 5.0,
            r"$-\nu\int_{\Omega} |\nabla\mathbf{u}|^2\,d\mathbf{x} \leq 0$",
            fontsize=14.5, fontweight='bold', color='#fecdd3', ha='center', va='center', zorder=3)

    # -------------------------------------------------------------------------
    # 5. BOTTOM-LEFT: EXTERNAL FORCING f
    # -------------------------------------------------------------------------
    draw_card(left_cx, bot_cy, corner_w, corner_h, '#1f190e', AMBER_COL, lw=1.8, zorder=2)
    draw_badge(left_cx, bot_cy + corner_h/2 - 2.1, "EXTERNAL FORCING", '#d97706', fontsize=10.0)

    ax.text(left_cx, bot_cy + 4.2, r"$\mathbf{f}$",
            fontsize=21.0, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=3)

    ax.text(left_cx, bot_cy - 0.5, "Can inject kinetic energy",
            fontsize=13.2, fontweight='bold', color=AMBER_COL, ha='center', va='center', zorder=3)

    ax.text(left_cx, bot_cy - 5.0,
            r"$\int_{\Omega} \mathbf{f}\cdot\mathbf{u}\,d\mathbf{x}$",
            fontsize=14.5, fontweight='bold', color='#fef3c7', ha='center', va='center', zorder=3)

    # -------------------------------------------------------------------------
    # DYNAMIC CONNECTING ARROWS & LABELS
    # -------------------------------------------------------------------------
    # A) Advection Arrow: Top-Left to Center
    arrow_adv = FancyArrowPatch((left_cx + corner_w/2 + 0.2, top_cy - 5.5),
                                (center_x - hub_w/2 - 0.2, center_y + 5.5),
                                connectionstyle="arc3,rad=-0.08",
                                arrowstyle="<|-|>,head_length=6.5,head_width=4.5",
                                color=EMERALD_COL, lw=2.4, zorder=4)
    ax.add_patch(arrow_adv)

    ax.text(31.0, 63.2, "Redistribution\n(Net Rate = 0)", fontsize=10.2, fontweight='bold',
            color=EMERALD_COL, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.40", facecolor='#062817', edgecolor=EMERALD_COL, lw=1.0, alpha=0.95),
            zorder=5)

    # B) Pressure Arrow: Top-Right to Center
    arrow_press = FancyArrowPatch((right_cx - corner_w/2 - 0.2, top_cy - 5.5),
                                  (center_x + hub_w/2 + 0.2, center_y + 5.5),
                                  connectionstyle="arc3,rad=0.08",
                                  arrowstyle="->,head_length=6.5,head_width=4.5",
                                  color=INDIGO_COL, lw=2.4, linestyle='--', zorder=4)
    ax.add_patch(arrow_press)

    ax.text(69.0, 63.2, "Incompressibility\n(Net Contribution = 0)", fontsize=10.2, fontweight='bold',
            color=INDIGO_COL, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.40", facecolor='#19173b', edgecolor=INDIGO_COL, lw=1.0, alpha=0.95),
            zorder=5)

    # C) Viscosity Arrow: Center to Bottom-Right (DISSIPATION DRAIN)
    arrow_visc = FancyArrowPatch((center_x + hub_w/2 + 0.2, center_y - 5.5),
                                 (right_cx - corner_w/2 - 0.2, bot_cy + 5.5),
                                 connectionstyle="arc3,rad=-0.08",
                                 arrowstyle="->,head_length=8.5,head_width=6.0",
                                 color=ROSE_COL, lw=3.2, zorder=4)
    ax.add_patch(arrow_visc)

    ax.text(69.0, 36.8, "Dissipation Drain\n" r"$-\nu\int |\nabla\mathbf{u}|^2\,d\mathbf{x}$",
            fontsize=10.5, fontweight='bold', color=ROSE_COL, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.40", facecolor='#330914', edgecolor=ROSE_COL, lw=1.1, alpha=0.95),
            zorder=5)

    # D) Forcing Arrow: Bottom-Left to Center (ENERGY INJECTION)
    arrow_forc = FancyArrowPatch((left_cx + corner_w/2 + 0.2, bot_cy + 5.5),
                                 (center_x - hub_w/2 - 0.2, center_y - 5.5),
                                 connectionstyle="arc3,rad=0.08",
                                 arrowstyle="->,head_length=8.5,head_width=6.0",
                                 color=AMBER_COL, lw=3.2, zorder=4)
    ax.add_patch(arrow_forc)

    ax.text(31.0, 36.8, "Energy Injection\n" r"$+\int \mathbf{f}\cdot\mathbf{u}\,d\mathbf{x}$",
            fontsize=10.5, fontweight='bold', color=AMBER_COL, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.40", facecolor='#362005', edgecolor=AMBER_COL, lw=1.1, alpha=0.95),
            zorder=5)

    # -------------------------------------------------------------------------
    # 6. BOTTOM HIGHLIGHTED TAKEAWAY BANNER (STREAMLINED & PRECISE)
    # -------------------------------------------------------------------------
    bot_ax = fig.add_axes([0.035, 0.026, 0.930, 0.112])
    bot_ax.set_facecolor('#0d1726')
    for spine in bot_ax.spines.values():
        spine.set_edgecolor('#059669')
        spine.set_linewidth(1.8)
    bot_ax.set_xlim(0, 100)
    bot_ax.set_ylim(0, 100)
    bot_ax.set_xticks([])
    bot_ax.set_yticks([])

    # Left pill icon
    takeaway_pill = FancyBboxPatch((2.0, 18.0), 15.0, 64.0,
                                   boxstyle="round,pad=0.5,rounding_size=1.5",
                                   facecolor='#059669', edgecolor='none', zorder=2)
    bot_ax.add_patch(takeaway_pill)
    bot_ax.text(9.5, 50.0, "KEY TAKEAWAY", fontsize=10.8, fontweight='bold',
                color='#ffffff', ha='center', va='center', zorder=3)

    # Main highlighted statements (concise, exact, and impactful)
    bot_ax.text(19.2, 68.0,
                "Global energy control alone does not imply local regularity.",
                fontsize=14.8, fontweight='bold', color='#34d399', va='center')

    bot_ax.text(19.2, 32.0,
                r"A bounded $L^2$ norm does not by itself prevent large local velocities or gradients.",
                fontsize=13.0, color='#e2e8f0', va='center')

    plt.savefig(out_path, dpi=240, facecolor=CANVAS_BG)
    plt.close()
    print(f"[OK] Generated Energy Balance Infographic: {out_path}")
    return out_path


generate_energy_balance_infographic = create_energy_balance_diagram

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    create_energy_balance_diagram(out_file)
