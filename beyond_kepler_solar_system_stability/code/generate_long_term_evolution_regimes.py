#!/usr/bin/env python3
"""
Generate Infographic: Different Forms of Long-Term Orbital Evolution
Visualizing three distinct dynamical regimes in celestial mechanics:
(a) Bounded quasiperiodic motion: multi-frequency regular oscillation within finite bounds
(b) Secular growth: persistent long-term drift beyond the initial range
(c) Chaotic but bounded motion: exponential divergence of nearby trajectories within fixed bounds

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
import numpy as np
from scipy.integrate import solve_ivp

# -------------------------------------------------------------------------
# PALETTE & AESTHETICS (Dark Astrophysics Theme)
# -------------------------------------------------------------------------
BG_COLOR       = "#0a0e17"       # Cosmic deep background
BG_PANEL       = "#111726"       # Panel plot canvas
BG_CARD        = "#0d131f"       # Bottom / callout card
BORDER         = "#1e293b"       # Panel border
BORDER_LIGHT   = "#334155"       # Highlight border
TEXT_TITLE     = "#f8fafc"       # Pure white
TEXT_SUB       = "#94a3b8"       # Cool slate grey
TEXT_BODY      = "#cbd5e1"       # Light body text

CYAN_PRIMARY   = "#38bdf8"       # Bright Cyan (Primary trajectory)
CYAN_GLOW      = "#0284c7"       # Cyan glow
ROSE_ACCENT    = "#f43f5e"       # Coral Rose (Diverging chaotic trajectory)
GOLD_ACCENT    = "#fbbf24"       # Warm Gold (Secular drift / highlights)
BOUND_LINE     = "#64748b"       # Slate dashed bound lines

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
        output_path = DEFAULT_IMAGES_DIR / "long_term_orbital_evolution.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 12.0 x 5.8 inches @ 280 DPI gives ideal proportions for desktop & mobile
    fig = plt.figure(figsize=(12.0, 5.8), dpi=280, facecolor=BG_COLOR)
    
    # Header Titles
    fig.text(0.05, 0.952, "Different Forms of Long-Term Orbital Evolution",
             fontsize=16.8, fontweight='bold', color=TEXT_TITLE, va='top')
    fig.text(0.05, 0.908,
             "Distinguishing bounded motion, secular growth, and chaotic sensitivity in planetary dynamics",
             fontsize=10.6, color=TEXT_SUB, va='top')

    # Dimensions: 3 panels side by side with ample spacing
    p_bottom = 0.16
    p_height = 0.67
    p_width  = 0.272
    p_gap    = 0.045
    p_left1  = 0.058
    p_left2  = p_left1 + p_width + p_gap
    p_left3  = p_left2 + p_width + p_gap

    ax_a = fig.add_axes([p_left1, p_bottom, p_width, p_height], facecolor=BG_PANEL)
    ax_b = fig.add_axes([p_left2, p_bottom, p_width, p_height], facecolor=BG_PANEL)
    ax_c = fig.add_axes([p_left3, p_bottom, p_width, p_height], facecolor=BG_PANEL)

    panels = [
        (ax_a, "(a) Bounded quasiperiodic", "Multi-frequency superposition within finite bounds"),
        (ax_b, "(b) Secular growth", "Persistent drift beyond the initial range"),
        (ax_c, "(c) Chaotic but bounded", "Sensitive dependence on initial conditions")
    ]

    t_max = 90.0
    n_pts = 2000
    t = np.linspace(0, t_max, n_pts)

    # Common Y limits across all 3 panels for direct visual comparison
    y_min, y_max = -0.05, 1.15
    y_bound_upper = 0.88
    y_bound_lower = 0.12

    for ax, title_str, subtitle_str in panels:
        ax.set_xlim(0, t_max)
        ax.set_ylim(y_min, y_max)
        
        # Style spines
        for spine_name, spine in ax.spines.items():
            spine.set_color(BORDER)
            spine.set_linewidth(1.2)
        
        ax.tick_params(colors=TEXT_SUB, labelsize=9.0, length=3.5)
        ax.set_xlabel("Time", fontsize=10.5, fontweight='bold', color=TEXT_SUB, labelpad=7)

        # Panel Headers (enlarged for crisp Medium 680px readability)
        ax.text(0.05, 0.93, title_str, transform=ax.transAxes,
                fontsize=12.2, fontweight='bold', color=TEXT_TITLE, va='top')
        ax.text(0.05, 0.865, subtitle_str, transform=ax.transAxes,
                fontsize=9.2, color=TEXT_SUB, va='top')

    # Y-axis labels on panel (a) only
    ax_a.set_ylabel("Orbital variable", fontsize=10.5, fontweight='bold', color=TEXT_SUB, labelpad=6)
    for ax in [ax_b, ax_c]:
        ax.set_yticklabels([])

    # ---------------------------------------------------------------------
    # PANEL (a): Bounded Quasiperiodic
    # ---------------------------------------------------------------------
    f1, f2, f3 = 0.38, 0.89, 1.77
    phi1, phi2, phi3 = 0.5, 2.1, 1.0
    y_a = 0.50 + 0.20 * np.sin(f1 * t + phi1) + 0.11 * np.cos(f2 * t + phi2) + 0.06 * np.sin(f3 * t + phi3)
    
    # Upper & lower bounds (enlarged labels)
    ax_a.axhline(y_bound_upper, color=BOUND_LINE, linestyle='--', linewidth=1.1, alpha=0.75)
    ax_a.axhline(y_bound_lower, color=BOUND_LINE, linestyle='--', linewidth=1.1, alpha=0.75)
    ax_a.text(t_max * 0.96, y_bound_upper + 0.02, "Upper bound", color=BOUND_LINE, fontsize=9.8,
              ha='right', va='bottom', style='italic')
    ax_a.text(t_max * 0.96, y_bound_lower + 0.022, "Lower bound", color=BOUND_LINE, fontsize=9.8,
              ha='right', va='bottom', style='italic')

    # Trajectory with glow
    ax_a.plot(t, y_a, color=CYAN_GLOW, linewidth=3.2, alpha=0.30)
    ax_a.plot(t, y_a, color=CYAN_PRIMARY, linewidth=1.8, label="Quasiperiodic orbit")

    # Key callout badge inside panel (a)
    ax_a.text(0.50, 0.08, "Bounded quasiperiodic evolution", transform=ax_a.transAxes,
              fontsize=9.2, color=CYAN_PRIMARY, ha='center', va='center',
              bbox=dict(boxstyle='round,pad=0.42', facecolor='#0d1f33', edgecolor='#0284c7', alpha=0.85, lw=1.0))

    # ---------------------------------------------------------------------
    # PANEL (b): Secular Growth
    # ---------------------------------------------------------------------
    drift = 0.0088 * t
    y_b = 0.22 + drift + 0.07 * np.sin(0.65 * t + 0.4) + 0.035 * np.cos(1.42 * t)

    # Initial reference band
    ax_b.axhline(0.33, color=BOUND_LINE, linestyle=':', linewidth=1.0, alpha=0.55)
    ax_b.axhline(0.12, color=BOUND_LINE, linestyle=':', linewidth=1.0, alpha=0.55)
    ax_b.fill_between([0, t_max * 0.35], 0.12, 0.33, color="#334155", alpha=0.15)
    ax_b.text(t_max * 0.04, 0.08, "Initial variation range", color=TEXT_SUB, fontsize=8.6,
              ha='left', va='top', style='italic')

    # Trajectory with glow
    ax_b.plot(t, y_b, color="#d97706", linewidth=3.2, alpha=0.30)
    ax_b.plot(t, y_b, color=GOLD_ACCENT, linewidth=1.8, label="Secular drift")

    # Key annotation arrow: Secular drift beyond the initial range
    ax_b.annotate("Secular drift beyond\nthe initial range",
                  xy=(t_max * 0.72, y_b[int(n_pts * 0.72)]),
                  xytext=(t_max * 0.38, 0.85),
                  arrowprops=dict(arrowstyle="->", color=GOLD_ACCENT, lw=1.3, shrinkA=4, shrinkB=4),
                  fontsize=9.2, color=GOLD_ACCENT, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.42', facecolor='#291e0a', edgecolor='#b45309', alpha=0.85, lw=1.0))

    # ---------------------------------------------------------------------
    # PANEL (c): Chaotic but Bounded
    # ---------------------------------------------------------------------
    def duffing(tau, s, delta=0.20, gamma=0.36, omega=1.0):
        return [s[1], s[0] - s[0]**3 - delta * s[1] + gamma * np.cos(omega * tau)]

    s1 = solve_ivp(duffing, (0, t_max), [0.3000, 0.2000], t_eval=t, rtol=1e-9, atol=1e-11)
    s2 = solve_ivp(duffing, (0, t_max), [0.3005, 0.2000], t_eval=t, rtol=1e-9, atol=1e-11)

    x1_raw = s1.y[0]
    x2_raw = s2.y[0]

    # Normalize to [0.18, 0.82] so both trajectories stay within bounds [0.12, 0.88]
    x_all = np.concatenate([x1_raw, x2_raw])
    x_min, x_max = x_all.min(), x_all.max()
    y1_c = 0.18 + (x1_raw - x_min) / (x_max - x_min) * (0.82 - 0.18)
    y2_c = 0.18 + (x2_raw - x_min) / (x_max - x_min) * (0.82 - 0.18)

    # Draw bounds matching panel (a)
    ax_c.axhline(y_bound_upper, color=BOUND_LINE, linestyle='--', linewidth=1.1, alpha=0.75)
    ax_c.axhline(y_bound_lower, color=BOUND_LINE, linestyle='--', linewidth=1.1, alpha=0.75)
    ax_c.text(t_max * 0.96, y_bound_upper + 0.02, "Upper bound", color=BOUND_LINE, fontsize=9.8,
              ha='right', va='bottom', style='italic')
    ax_c.text(t_max * 0.96, y_bound_lower + 0.022, "Lower bound", color=BOUND_LINE, fontsize=9.8,
              ha='right', va='bottom', style='italic')

    # Trajectory 1: Cyan (solid)
    ax_c.plot(t, y1_c, color=CYAN_PRIMARY, linewidth=1.8, alpha=0.92, label="Trajectory 1")
    # Trajectory 2: Coral Rose (dashed)
    ax_c.plot(t, y2_c, color=ROSE_ACCENT, linewidth=1.6, alpha=0.88, linestyle='--', label="Trajectory 2 (nearby initial condition)")

    # Annotation 1: Initially nearly identical
    idx_valley = int(21.0 / t_max * n_pts)
    ax_c.annotate("Initially nearly identical",
                  xy=(21.0, y1_c[idx_valley] + 0.02),
                  xytext=(21.0, 0.52),
                  arrowprops=dict(arrowstyle="->", color=CYAN_PRIMARY, lw=1.1, shrinkA=3, shrinkB=4),
                  fontsize=8.8, color=CYAN_PRIMARY, ha='center', va='bottom',
                  bbox=dict(boxstyle='round,pad=0.38', facecolor='#0d1f33', edgecolor='#0284c7', alpha=0.85, lw=1.0))

    # Annotation 2: Trajectories separate; phases decorrelate
    idx_sep = int(52.0 / t_max * n_pts)
    ax_c.annotate("Trajectories separate;\nphases decorrelate",
                  xy=(52.0, y1_c[idx_sep]),
                  xytext=(50.0, 0.27),
                  arrowprops=dict(arrowstyle="->", color=ROSE_ACCENT, lw=1.1, shrinkA=3, shrinkB=4),
                  fontsize=8.8, color=ROSE_ACCENT, ha='center', va='top',
                  bbox=dict(boxstyle='round,pad=0.38', facecolor='#260f16', edgecolor='#9f1239', alpha=0.85, lw=1.0))

    # Clean horizontal legend in the empty bottom region of panel (c) (enlarged font)
    leg = ax_c.legend(loc='lower center', bbox_to_anchor=(0.50, 0.015),
                      ncol=2, fontsize=8.0, framealpha=0.92, facecolor=BG_CARD,
                      edgecolor=BORDER_LIGHT, handlelength=1.2, columnspacing=0.8,
                      borderpad=0.32, handletextpad=0.4)
    for text in leg.get_texts():
        text.set_color(TEXT_BODY)

    plt.savefig(output_path, dpi=280, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"Saved figure to {output_path}")

    return output_path

generate_long_term_evolution_regimes = generate_figure

if __name__ == "__main__":
    generate_figure()
