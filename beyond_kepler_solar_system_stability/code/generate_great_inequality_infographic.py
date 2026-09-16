#!/usr/bin/env python3
"""
Generate Infographic: Why the 5:2 Near-Commensurability Produces a Slow Variation
Visualizing the Great Inequality of Jupiter and Saturn:
Left Panel: Orbital commensurability (5 P_J ≈ 2 P_S) and phase mismatch.
Right Panel: Slow angular combination phi = 2*lambda_J - 5*lambda_S, rate dphi/dt = 2*n_J - 5*n_S,
             and the resulting ~900-year long-period modulation.

Medium 680px width @ 280 DPI, Dark Astrophysics aesthetic.
"""

from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
import numpy as np

# -------------------------------------------------------------------------
# PALETTE & AESTHETICS (Dark Astrophysics Theme)
# -------------------------------------------------------------------------
BG_COLOR       = "#0a0e17"       # Cosmic deep background
BG_PANEL       = "#111726"       # Panel plot canvas
BG_CARD        = "#0d1422"       # Bottom / callout card
BORDER         = "#1e293b"       # Panel border
BORDER_LIGHT   = "#334155"       # Highlight border
TEXT_TITLE     = "#f8fafc"       # Pure white
TEXT_SUB       = "#94a3b8"       # Cool slate grey
TEXT_BODY      = "#cbd5e1"       # Light body text

SUN_CORE       = "#fef08a"       # Bright yellow
SUN_GLOW       = "#f59e0b"       # Warm amber glow
JUPITER_COLOR  = "#38bdf8"       # Cyan for Jupiter
JUPITER_GLOW   = "#0284c7"       # Cyan glow
SATURN_COLOR   = "#fbbf24"       # Warm Gold for Saturn
SATURN_GLOW    = "#d97706"       # Amber glow
GOLD_ACCENT    = "#fbbf24"       # Warm Gold accent
ROSE_ACCENT    = "#f43f5e"       # Coral Rose for mismatch / beats
EMERALD        = "#10b981"       # Emerald green for period / coherence

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'mathtext.fontset': 'dejavusans',
    'text.color': TEXT_BODY,
    'axes.labelcolor': TEXT_BODY,
    'xtick.color': TEXT_SUB,
    'ytick.color': TEXT_SUB,
})

def generate_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_IMAGES_DIR / "great_inequality_commensurability.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 13.6 x 6.8 inches @ 280 DPI: balanced 2:1 widescreen for Medium 680px display
    fig = plt.figure(figsize=(13.6, 6.8), dpi=280, facecolor=BG_COLOR)
    
    # Header Titles
    fig.text(0.045, 0.952, "Why the 5:2 Near-Commensurability Produces a Slow Variation",
             fontsize=15.8, fontweight='bold', color=TEXT_TITLE, va='top')
    fig.text(0.045, 0.908,
             "How Jupiter and Saturn’s near 5:2 commensurability underlies the ~900-year Great Inequality",
             fontsize=10.2, color=TEXT_SUB, va='top')

    # Panel dimensions: 2 equal panels with comfortable spacing
    p_bottom = 0.075
    p_height = 0.805
    p_width  = 0.435
    p_gap    = 0.040
    p_left1  = 0.045
    p_left2  = p_left1 + p_width + p_gap

    ax1 = fig.add_axes([p_left1, p_bottom, p_width, p_height], facecolor=BG_PANEL)
    ax2 = fig.add_axes([p_left2, p_bottom, p_width, p_height], facecolor=BG_PANEL)

    for ax in [ax1, ax2]:
        for spine in ax.spines.values():
            spine.set_color(BORDER)
            spine.set_linewidth(1.2)

    # =========================================================================
    # LEFT PANEL: ORBITAL COMMENSURABILITY (5 P_J ≈ 2 P_S)
    # =========================================================================
    ax1.set_xlim(-3.0, 3.4)
    ax1.set_ylim(-3.0, 3.1)
    ax1.set_aspect('equal')
    ax1.set_xticks([])
    ax1.set_yticks([])

    # Panel Header
    ax1.text(0.05, 0.95, "(a) Orbital Commensurability: Near 5:2 Ratio",
             transform=ax1.transAxes, fontsize=12.2, fontweight='bold', color=TEXT_TITLE, va='top')
    ax1.text(0.05, 0.895, "5 Jupiter revolutions ≈ 2 Saturn revolutions (small accumulated mismatch)",
             transform=ax1.transAxes, fontsize=9.0, color=TEXT_SUB, va='top')

    # Orbit parameters
    r_j = 1.35
    r_s = 2.30
    theta = np.linspace(0, 2*np.pi, 360)

    # Orbit paths
    ax1.plot(r_j * np.cos(theta), r_j * np.sin(theta), color=JUPITER_GLOW, lw=1.3, ls='--', alpha=0.55)
    ax1.plot(r_s * np.cos(theta), r_s * np.sin(theta), color=SATURN_GLOW, lw=1.3, ls='--', alpha=0.55)

    # Orbit directional arrows
    for r_orb, col, th_arr in [(r_j, JUPITER_COLOR, np.pi * 0.58), (r_s, SATURN_COLOR, np.pi * 0.48)]:
        x_a = r_orb * np.cos(th_arr)
        y_a = r_orb * np.sin(th_arr)
        dx_a = -0.16 * np.sin(th_arr)
        dy_a = 0.16 * np.cos(th_arr)
        ax1.annotate("", xy=(x_a + dx_a, y_a + dy_a), xytext=(x_a, y_a),
                     arrowprops=dict(arrowstyle="->", color=col, lw=1.8, mutation_scale=12))

    # Central Sun with multi-layer glow
    for rad, alph in [(0.32, 0.07), (0.22, 0.16), (0.14, 0.32)]:
        glow = patches.Circle((0, 0), rad, facecolor=SUN_GLOW, edgecolor='none', alpha=alph)
        ax1.add_patch(glow)
    sun = patches.Circle((0, 0), 0.085, facecolor=SUN_CORE, edgecolor=SUN_GLOW, lw=1.1)
    ax1.add_patch(sun)
    ax1.text(0, -0.24, "Sun", color=SUN_CORE, fontsize=8.6, ha='center', fontweight='bold')

    # Reference axis: Initial conjunction line at theta = 0
    ax1.plot([0, 2.75], [0, 0], color="#64748b", lw=1.2, ls=':', alpha=0.75)
    ax1.text(2.80, 0.0, "Initial alignment\n(t = 0)", color="#94a3b8", fontsize=8.2, va='center', ha='left', style='italic')

    # Initial planet positions at t = 0 (ghost markers)
    ax1.plot(r_j, 0, 'o', color=JUPITER_COLOR, ms=6, alpha=0.35)
    ax1.plot(r_s, 0, 'o', color=SATURN_COLOR, ms=7, alpha=0.35)

    # State after ~59 years:
    # After 5 Jupiter revolutions, Saturn has rotated ~725° = 2 * 360° + 5°.
    # We display an angle of ~15° for clear visual communication of the mismatch.
    th_mismatch = np.radians(16.0)

    # Line showing Saturn's position after 5 Jupiter periods
    x_s_new = r_s * np.cos(th_mismatch)
    y_s_new = r_s * np.sin(th_mismatch)
    ax1.plot([0, x_s_new * 1.14], [0, y_s_new * 1.14], color=ROSE_ACCENT, lw=1.2, ls='-', alpha=0.75)

    # Mismatch arc between theta=0 and th_mismatch at Saturn's orbit
    arc_theta = np.linspace(0, th_mismatch, 50)
    r_arc = r_s * 0.86
    ax1.plot(r_arc * np.cos(arc_theta), r_arc * np.sin(arc_theta), color=ROSE_ACCENT, lw=1.5)
    ax1.annotate("", xy=(r_arc * np.cos(th_mismatch), r_arc * np.sin(th_mismatch)),
                 xytext=(r_arc * np.cos(th_mismatch * 0.4), r_arc * np.sin(th_mismatch * 0.4)),
                 arrowprops=dict(arrowstyle="->", color=ROSE_ACCENT, lw=1.3, mutation_scale=10))

    # Callout for mismatch
    ax1.annotate("Small accumulated\nphase mismatch",
                 xy=(r_arc * np.cos(th_mismatch * 0.5), r_arc * np.sin(th_mismatch * 0.5)),
                 xytext=(1.75, 1.40),
                 arrowprops=dict(arrowstyle="->", color=ROSE_ACCENT, lw=1.2, shrinkA=3, shrinkB=4),
                 fontsize=8.4, color=ROSE_ACCENT, ha='left', va='center',
                 bbox=dict(boxstyle='round,pad=0.38', facecolor='#260f16', edgecolor='#9f1239', alpha=0.92, lw=1.0))

    # Planet positions after cycle:
    # Jupiter completed 5 full revs (at theta=0)
    p_j = patches.Circle((r_j, 0), 0.09, facecolor=JUPITER_COLOR, edgecolor="#e0f2fe", lw=1.3, zorder=5)
    ax1.add_patch(p_j)
    ax1.text(r_j - 0.08, -0.32, "Jupiter\n(5 full revs)", color=JUPITER_COLOR, fontsize=8.2,
             ha='center', va='top', fontweight='bold')

    # Saturn after 5 Jupiter revs (at theta = th_mismatch)
    p_s = patches.Circle((x_s_new, y_s_new), 0.105, facecolor=SATURN_COLOR, edgecolor="#fef08a", lw=1.3, zorder=5)
    ax1.add_patch(p_s)
    # Saturn ring schematic
    ring = patches.Ellipse((x_s_new, y_s_new), 0.38, 0.12, angle=24, facecolor='none',
                           edgecolor=SATURN_COLOR, lw=1.2, alpha=0.85, zorder=6)
    ax1.add_patch(ring)
    ax1.text(x_s_new + 0.22, y_s_new + 0.16, "Saturn\n(≈ 2 revs)", color=SATURN_COLOR, fontsize=8.2,
             ha='left', va='center', fontweight='bold')

    # Info card in bottom-left corner
    info_text = (
        "Orbital Periods:\n"
        "• Jupiter:  P_J ≈ 11.86 yr   (5 P_J ≈ 59.3 yr)\n"
        "• Saturn:   P_S ≈ 29.46 yr   (2 P_S ≈ 58.9 yr)\n"
        "• 5 P_J ≈ 2 P_S : Configuration almost repeats,\n"
        "  leaving a small accumulated phase mismatch"
    )
    ax1.text(0.04, 0.04, info_text, transform=ax1.transAxes, fontsize=8.0, color=TEXT_BODY,
             va='bottom', ha='left', family='monospace',
             bbox=dict(boxstyle='round,pad=0.48', facecolor=BG_CARD, edgecolor=BORDER_LIGHT, alpha=0.95, lw=1.0))

    # =========================================================================
    # RIGHT PANEL: SLOW BEAT & THE GREAT INEQUALITY
    # =========================================================================
    ax2.set_xticks([])
    ax2.set_yticks([])

    # Panel Header
    ax2.text(0.05, 0.95, "(b) Slow Beat: The Great Inequality",
             transform=ax2.transAxes, fontsize=12.2, fontweight='bold', color=TEXT_TITLE, va='top')
    ax2.text(0.05, 0.895, "Slow angular combination and centuries-long perturbation",
             transform=ax2.transAxes, fontsize=9.0, color=TEXT_SUB, va='top')

    # Top Box: Mathematical variable representation & note
    math_box_text = (
        "Slow orbital-angle combination:\n"
        r"  $\phi = 2\lambda_J - 5\lambda_S$" + "\n"
        r"Rate of change:  $\dot{\phi} \simeq 2n_J - 5n_S \approx -0.4^\circ / \mathrm{year}$" + "\n"
        "  (schematic slow-angle representation)"
    )
    ax2.text(0.05, 0.835, math_box_text, transform=ax2.transAxes, fontsize=8.8, color=TEXT_BODY,
             va='top', ha='left',
             bbox=dict(boxstyle='round,pad=0.48', facecolor='#0d1726', edgecolor='#0284c7', alpha=0.92, lw=1.1))

    # Flow sequence badge
    flow_text = (
        r"5:2 near-commensurability  $\longrightarrow$  $2n_J - 5n_S$ small  $\longrightarrow$  $\phi$ changes slowly  $\longrightarrow$  centuries-long perturbation"
    )
    ax2.text(0.05, 0.605, flow_text, transform=ax2.transAxes, fontsize=7.8, color=GOLD_ACCENT,
             va='top', ha='left', fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.40', facecolor='#201a09', edgecolor='#b45309', alpha=0.92, lw=1.0))

    # Sub-axis for the long-period modulation curve (bottom portion of right panel)
    sub_ax = ax2.inset_axes([0.08, 0.08, 0.87, 0.44], facecolor='#0a0f1c')
    for spine in sub_ax.spines.values():
        spine.set_color(BORDER_LIGHT)
        spine.set_linewidth(1.0)

    # Time series: 0 to 1800 years (two 900-year cycles)
    t_span = np.linspace(0, 1800, 1000)
    T_beat = 883.0  # ~900 years
    pert_jupiter = np.sin(2 * np.pi * t_span / T_beat)
    pert_saturn  = -np.sin(2 * np.pi * t_span / T_beat)

    sub_ax.axhline(0, color='#334155', lw=0.8, ls=':')
    
    # Curves (explicitly schematic variations)
    sub_ax.plot(t_span, pert_jupiter, color=JUPITER_COLOR, lw=1.8, label="Schematic Jupiter variation")
    sub_ax.plot(t_span, pert_saturn, color=SATURN_COLOR, lw=1.8, ls='--', label="Schematic Saturn variation")

    sub_ax.set_xlim(0, 1800)
    sub_ax.set_ylim(-1.6, 1.65)
    sub_ax.set_xlabel("Time (years)", fontsize=8.8, color=TEXT_SUB, labelpad=4)
    sub_ax.set_ylabel("Schematic perturbation", fontsize=8.4, color=TEXT_SUB, labelpad=4)
    sub_ax.tick_params(colors=TEXT_SUB, labelsize=7.8, length=3)
    sub_ax.set_xticks([0, 300, 600, 900, 1200, 1500, 1800])

    # 900-year period bracket & label
    y_bkt = 1.25
    sub_ax.annotate("", xy=(T_beat, y_bkt), xytext=(0, y_bkt),
                    arrowprops=dict(arrowstyle="<->", color=EMERALD, lw=1.5))
    sub_ax.text(T_beat * 0.5, y_bkt + 0.11, "Long-period modulation: ~900 years",
                color=EMERALD, fontsize=8.4, ha='center', va='bottom', fontweight='bold')

    # Short observational window highlight (mimicking Halley's puzzle)
    t_obs_start = 120
    t_obs_end = 240
    sub_ax.axvspan(t_obs_start, t_obs_end, color='#f43f5e', alpha=0.18)
    sub_ax.annotate("A short segment of the long cycle\ncan resemble a secular drift\n(Halley's historical puzzle)",
                    xy=(180, 0.95), xytext=(500, 0.45),
                    arrowprops=dict(arrowstyle="->", color=ROSE_ACCENT, lw=1.1, shrinkA=3, shrinkB=4),
                    fontsize=7.6, color=ROSE_ACCENT, ha='left', va='center',
                    bbox=dict(boxstyle='round,pad=0.34', facecolor='#260f16', edgecolor='#9f1239', alpha=0.90, lw=0.9))

    # Legend inside sub-axis with schematic note
    leg = sub_ax.legend(loc='lower center', bbox_to_anchor=(0.50, 0.04),
                        ncol=2, fontsize=7.4, framealpha=0.90,
                        facecolor=BG_CARD, edgecolor=BORDER_LIGHT, handlelength=1.4)
    for text in leg.get_texts():
        text.set_color(TEXT_BODY)
    sub_ax.text(0.50, 0.01, "schematic long-period modulation",
                transform=sub_ax.transAxes, fontsize=6.8, color=TEXT_SUB,
                ha='center', va='bottom', style='italic')

    plt.savefig(output_path, dpi=280, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"Saved figure to {output_path}")

    return output_path

generate_great_inequality_infographic = generate_figure

if __name__ == "__main__":
    generate_figure()
