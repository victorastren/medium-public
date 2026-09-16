#!/usr/bin/env python3
"""
Generate The Eccentricity Vector in the (k, h) Plane
Visualizing:
- Horizontal axis: k = e cos ϖ
- Vertical axis: h = e sin ϖ
- Point (k, h) with coordinates and dashed projection lines
- Vector from the origin to (k, h) with length e
- Angle from k-axis labelled ϖ
- Complex representation z = k + ih = e e^{iϖ} next to the vector

Tailored for Medium's 680px width with dark astrophysics aesthetic.
"""

from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# -------------------------------------------------------------------------
# PALETTE & AESTHETICS (Dark Astrophysics)
# -------------------------------------------------------------------------
BG_COLOR      = "#0a0e17"       # Cosmic deep black/slate
BG_PANEL      = "#111726"       # Inner plot canvas
BORDER        = "#1e293b"       # Subtle structural border
BORDER_LIGHT  = "#334155"       # Card border
TEXT_TITLE    = "#f8fafc"       # Pure crisp white
TEXT_SUB      = "#94a3b8"       # Cool slate grey
TEXT_BODY     = "#cbd5e1"       # Light body text

CYAN_ACCENT   = "#38bdf8"       # Primary vector color (bright cyan)
CYAN_GLOW     = "#0284c7"       # Cyan glow
GOLD_ACCENT   = "#fbbf24"       # Angle / perihelion color (warm gold)
ROSE_ACCENT   = "#f43f5e"       # Coordinate markers (coral rose)
EMERALD       = "#34d399"       # Formula highlight (emerald green)
AXIS_COLOR    = "#64748b"       # Slate axes

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'mathtext.fontset': 'dejavusans',
    'text.color': TEXT_BODY,
    'axes.labelcolor': TEXT_BODY,
})

def create_eccentricity_vector_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_IMAGES_DIR / "eccentricity_vector.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(9.6, 6.6), dpi=280, facecolor=BG_COLOR)
    
    # Main panel with generous padding
    ax = fig.add_axes([0.08, 0.10, 0.84, 0.77], facecolor=BG_PANEL)
    
    # Coordinate range giving balanced breathing space
    ax.set_xlim(-0.25, 1.25)
    ax.set_ylim(-0.20, 1.05)
    ax.set_aspect('equal')
    
    # Hide default spines & ticks
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Panel border
    panel_rect = patches.FancyBboxPatch((-0.24, -0.19), 1.48, 1.23,
                                        boxstyle="round,pad=0.0,rounding_size=0.03",
                                        edgecolor=BORDER, facecolor="none",
                                        linewidth=1.5, zorder=1)
    ax.add_patch(panel_rect)

    # Subtle concentric rings for eccentricity magnitude e (without distracting numbers)
    for r_val in [0.25, 0.50, 0.75, 1.00]:
        circ = patches.Circle((0, 0), r_val, edgecolor="#1e293b", facecolor="none",
                              linestyle=":", linewidth=1.0, alpha=0.5, zorder=2)
        ax.add_patch(circ)

    # Main coordinate axes with clean arrowheads
    ax.annotate("", xy=(1.18, 0), xytext=(-0.16, 0),
                arrowprops=dict(arrowstyle="-|>", color=AXIS_COLOR, lw=1.8, mutation_scale=16),
                zorder=3)
    ax.annotate("", xy=(0, 0.98), xytext=(0, -0.14),
                arrowprops=dict(arrowstyle="-|>", color=AXIS_COLOR, lw=1.8, mutation_scale=16),
                zorder=3)

    # Origin indicator
    ax.plot(0, 0, 'o', color=TEXT_SUB, markersize=5, zorder=5)
    ax.text(-0.035, -0.045, "0", fontsize=11, color=TEXT_SUB, ha='right', va='top', zorder=5)

    # Axis Labels with proper mathematical spacing
    ax.text(1.20, -0.02, r"$k = e\,\cos\,\varpi$", fontsize=13.5, color=TEXT_TITLE,
            fontweight='bold', ha='left', va='center', zorder=6)
    ax.text(-0.04, 1.01, r"$h = e\,\sin\,\varpi$", fontsize=13.5, color=TEXT_TITLE,
            fontweight='bold', ha='right', va='bottom', zorder=6)

    # Vector parameters
    e_val = 0.85
    varpi_deg = 36.0
    varpi_rad = np.radians(varpi_deg)
    k_val = e_val * np.cos(varpi_rad)
    h_val = e_val * np.sin(varpi_rad)

    # Dashed projections onto axes
    ax.plot([k_val, k_val], [0, h_val], linestyle="--", color="#64748b", linewidth=1.4, alpha=0.8, zorder=3)
    ax.plot([0, k_val], [h_val, h_val], linestyle="--", color="#64748b", linewidth=1.4, alpha=0.8, zorder=3)

    # Tick markers and component labels on axes
    ax.plot(k_val, 0, '|', color=ROSE_ACCENT, markersize=12, markeredgewidth=2.2, zorder=5)
    ax.plot(0, h_val, '_', color=ROSE_ACCENT, markersize=12, markeredgewidth=2.2, zorder=5)
    ax.text(k_val, -0.065, r"$k$", fontsize=13.5, color=ROSE_ACCENT, fontweight='bold', ha='center', va='top', zorder=6)
    ax.text(-0.045, h_val, r"$h$", fontsize=13.5, color=ROSE_ACCENT, fontweight='bold', ha='right', va='center', zorder=6)

    # Angle arc for ϖ
    arc_radius = 0.32
    arc_theta = np.linspace(0, varpi_rad, 60)
    ax.plot(arc_radius * np.cos(arc_theta), arc_radius * np.sin(arc_theta),
            color=GOLD_ACCENT, linewidth=2.0, zorder=4)
    
    # Arrowhead on arc
    ax.annotate("", xy=(arc_radius * np.cos(varpi_rad), arc_radius * np.sin(varpi_rad)),
                xytext=(arc_radius * np.cos(varpi_rad - 0.05), arc_radius * np.sin(varpi_rad - 0.05)),
                arrowprops=dict(arrowstyle="-|>", color=GOLD_ACCENT, lw=1.5, mutation_scale=13),
                zorder=5)
    
    # Angle label ϖ
    angle_mid = varpi_rad * 0.50
    ax.text(0.40 * np.cos(angle_mid), 0.40 * np.sin(angle_mid), r"$\varpi$",
            fontsize=16, color=GOLD_ACCENT, fontweight='bold', ha='center', va='center', zorder=6)

    # Eccentricity Vector (with subtle neon glow underlay)
    ax.annotate("", xy=(k_val, h_val), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=CYAN_GLOW, lw=5.5, alpha=0.35, mutation_scale=22),
                zorder=4)
    ax.annotate("", xy=(k_val, h_val), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=CYAN_ACCENT, lw=2.6, mutation_scale=20),
                zorder=5)

    # Terminal Point (k, h)
    ax.plot(k_val, h_val, 'o', color=CYAN_ACCENT, markersize=8.5, zorder=7)
    ax.plot(k_val, h_val, 'o', color="#ffffff", markersize=4, zorder=8)

    # Badge for point (k, h)
    point_box = dict(boxstyle='round,pad=0.38', facecolor='#1e293b', edgecolor=CYAN_ACCENT, linewidth=1.3)
    ax.text(k_val + 0.04, h_val + 0.035, r"$(k, h)$", fontsize=13.5, color="#ffffff",
            fontweight='bold', bbox=point_box, ha='left', va='bottom', zorder=9)

    # Vector length label 'e'
    vec_mid_x = 0.50 * k_val
    vec_mid_y = 0.50 * h_val
    # Perpendicular offset for 'e' label (above and to the left of vector)
    perp_dx = -0.05
    perp_dy = 0.06
    ax.text(vec_mid_x + perp_dx, vec_mid_y + perp_dy, r"$e$",
            fontsize=17, color=CYAN_ACCENT, fontweight='bold', ha='center', va='center', zorder=9)

    # Complex formulation badge z = k + ih = e e^{iϖ} positioned cleanly above the vector
    complex_box = dict(boxstyle='round,pad=0.6', facecolor='#0f172a', edgecolor=BORDER_LIGHT, linewidth=1.4)
    ax.text(0.24, 0.72, r"$z = k + i\,h = e\ \mathrm{e}^{i\varpi}$",
            fontsize=15, color=EMERALD, fontweight='bold', bbox=complex_box,
            ha='left', va='center', zorder=9)

    # Figure Title and Subtitle
    fig.text(0.08, 0.94, "The Eccentricity Vector in the (k, h) Plane",
             fontsize=17, fontweight='bold', color=TEXT_TITLE, ha='left')
    fig.text(0.08, 0.90, "Combining eccentricity magnitude and perihelion orientation into nonsingular Cartesian variables",
             fontsize=11.5, color=TEXT_SUB, ha='left')

    # Save figure
    plt.savefig(output_path, dpi=280, facecolor=BG_COLOR, edgecolor='none')
    plt.close()
    print(f"[OK] Successfully generated {output_path}")

    return output_path

generate_eccentricity_vector = create_eccentricity_vector_figure

if __name__ == "__main__":
    create_eccentricity_vector_figure()
