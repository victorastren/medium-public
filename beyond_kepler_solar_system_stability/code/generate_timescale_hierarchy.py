#!/usr/bin/env python3
"""
Generate Infographic: The Timescale Gap in the Solar System
Visualizing why orbital averaging works for Section 3:
Contrasting rapid orbital periods (months/years) with long-term secular timescales
(tens to hundreds of thousands of years) across the Solar System.
Optimized for full-width display at 680px Medium reading width.
"""

from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

# -------------------------------------------------------------------------
# GLOBAL AESTHETICS & PALETTE (Astrophysics Dark Theme)
# -------------------------------------------------------------------------
BG_COLOR    = "#0a0e17"       # Deep cosmic dark
BG_PANEL    = "#111726"       # Panel background
BORDER      = "#1e293b"       # Subtle border
BORDER_LIGHT= "#334155"       # Card border
TEXT_TITLE  = "#f8fafc"       # Bright white
TEXT_SUB    = "#94a3b8"       # Cool slate grey
TEXT_BODY   = "#cbd5e1"       # Light grey text

FAST_COLOR  = "#38bdf8"       # Cyan for orbital period
SLOW_COLOR  = "#f43f5e"       # Rose/coral for secular timescale
SLOW_ACCENT = "#fb7185"       # Lighter coral
GOLD_ACCENT = "#fbbf24"       # Highlight gold

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'mathtext.fontset': 'dejavusans',
    'text.color': TEXT_BODY,
    'axes.labelcolor': TEXT_BODY,
    'xtick.color': TEXT_SUB,
    'ytick.color': TEXT_SUB,
})

def create_timescale_hierarchy(output_path=None):
    if output_path is None:
        output_path = DEFAULT_IMAGES_DIR / "timescale_hierarchy.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11.5, 6.6), dpi=280, facecolor=BG_COLOR)
    ax.set_facecolor(BG_PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
        spine.set_linewidth(1.3)

    ax.set_xlim(0.0, 10.0)
    ax.set_ylim(0.0, 10.0)
    ax.set_xticks([])
    ax.set_yticks([])

    # Panel Titles
    ax.text(0.04, 0.95, "The Timescale Hierarchy in the Solar System", transform=ax.transAxes,
            fontsize=15.0, fontweight='bold', color=TEXT_TITLE, va='top')
    ax.text(0.04, 0.88, r"Why orbital averaging works: a $10^3$ to $10^5$ gap between orbital periods and secular evolution",
            transform=ax.transAxes, fontsize=10.5, color=TEXT_SUB, va='top')

    # Three representative planetary cases
    planets_data = [
        {
            "name": "Earth",
            "col": "#38bdf8",
            "context": "Milankovitch climate cycles",
            "p_orb": "1.00 year",
            "p_sec": "~ 112,000 years",
            "ratio": "112,000 ×",
            "log_fast": 0.0,
            "log_slow": 5.05
        },
        {
            "name": "Jupiter",
            "col": "#fbbf24",
            "context": "Dominant gas giant secular mode",
            "p_orb": "11.86 years",
            "p_sec": "~ 306,000 years",
            "ratio": "25,800 ×",
            "log_fast": 1.07,
            "log_slow": 5.48
        },
        {
            "name": "Saturn",
            "col": "#f43f5e",
            "context": "Resonant secular partner to Jupiter",
            "p_orb": "29.46 years",
            "p_sec": "~ 45,700 years",
            "ratio": "1,550 ×",
            "log_fast": 1.47,
            "log_slow": 4.66
        }
    ]

    # Header row
    y_header = 8.05
    ax.text(0.60, y_header, "PLANET", color=TEXT_SUB, fontsize=8.8, fontweight='bold')
    ax.text(3.10, y_header, "ORBITAL REVOLUTION", color=FAST_COLOR, fontsize=8.8, fontweight='bold')
    ax.text(5.50, y_header, "SECULAR TIMESCALE", color=SLOW_ACCENT, fontsize=8.8, fontweight='bold')
    ax.text(7.60, y_header, "TIMESCALE GAP", color=GOLD_ACCENT, fontsize=8.8, fontweight='bold')
    ax.plot([0.45, 9.55], [7.85, 7.85], color=BORDER_LIGHT, lw=1.1)

    y_starts = [6.80, 5.25, 3.70]

    for idx, (p, y_pos) in enumerate(zip(planets_data, y_starts)):
        # Card background
        card_bg = Rectangle((0.45, y_pos - 0.58), 9.10, 1.25,
                            facecolor='#0b111e' if idx % 2 == 0 else '#0e1626',
                            edgecolor=BORDER, linewidth=0.9, zorder=2)
        ax.add_patch(card_bg)

        # Col 1: Planet & Subtitle
        ax.plot(0.80, y_pos + 0.16, marker='o', markersize=7.5, color=p['col'], zorder=4)
        ax.text(1.10, y_pos + 0.10, p['name'], color=TEXT_TITLE, fontsize=11.5, fontweight='bold', zorder=4)
        ax.text(1.10, y_pos - 0.28, p['context'], color=TEXT_SUB, fontsize=8.2, zorder=4)

        # Col 2: Fast orbital period
        ax.text(3.10, y_pos + 0.10, p['p_orb'], color=FAST_COLOR, fontsize=11.0, fontweight='bold', zorder=4)
        ax.text(3.10, y_pos - 0.28, "Fast orbital phase", color='#64748b', fontsize=8.2, zorder=4)

        # Col 3: Slow secular timescale
        ax.text(5.50, y_pos + 0.10, p['p_sec'], color=SLOW_ACCENT, fontsize=11.0, fontweight='bold', zorder=4)
        ax.text(5.50, y_pos - 0.28, "Slow orbital evolution", color='#64748b', fontsize=8.2, zorder=4)

        # Col 4: Ratio Badge
        ratio_box = dict(boxstyle='round,pad=0.32,rounding_size=0.25',
                         facecolor='#271b05', edgecolor=GOLD_ACCENT, lw=1.0)
        ax.text(7.60, y_pos + 0.04, p['ratio'], color=GOLD_ACCENT, fontsize=10.5, fontweight='bold',
                bbox=ratio_box, zorder=4)

        # Visual log-scale indicator (inset on the right: 8.60 to 9.40)
        gx0, gx1 = 8.60, 9.35
        gy = y_pos + 0.04
        def log_to_x(val):
            return gx0 + (val - 0.0) / 6.0 * (gx1 - gx0)

        ax.plot([gx0, gx1], [gy, gy], color='#334155', lw=1.3, zorder=3)
        xf = log_to_x(p['log_fast'])
        xs = log_to_x(p['log_slow'])
        ax.plot([xf, xs], [gy, gy], color='#64748b', lw=2.4, alpha=0.8, zorder=3)
        ax.plot(xf, gy, marker='o', markersize=4.8, color=FAST_COLOR, zorder=4)
        ax.plot(xs, gy, marker='o', markersize=4.8, color=SLOW_ACCENT, zorder=4)

    # Mini axis labels for visual log bar
    ax.text(8.60, 3.00, r"$1\mathrm{yr}$", color='#64748b', fontsize=7.2, ha='center')
    ax.text(9.35, 3.00, r"$10^6\mathrm{yr}$", color='#64748b', fontsize=7.2, ha='center')

    # Bottom Synthesis Box
    synthesis_card = (
        r"$\mathbf{The\ Foundation\ of\ Secular\ Perturbation\ Theory}$:" "\n"
        r"• $\mathbf{Insignificant\ per\ orbit}$: Over a single revolution, mutual planetary perturbations deform the orbit by $\lesssim 10^{-4}$." "\n"
        r"• $\mathbf{The\ Averaging\ Principle}$: Because orbital motion is thousands of times faster than orbital precession, one can" "\n"
        r"  average over orbital phases, effectively smearing planets into interacting gravitational rings (Gauss & Laplace)." "\n"
        r"• $\mathbf{Long\text{-}Term\ Order}$: Isolates the slow exchange of angular momentum and eccentricity without tracking every oscillation."
    )
    box_card_props = dict(boxstyle='round,pad=0.55,rounding_size=0.3',
                          facecolor='#0d1422', edgecolor=BORDER_LIGHT,
                          linewidth=1.2, alpha=0.96)
    ax.text(0.04, 0.04, synthesis_card, transform=ax.transAxes,
            fontsize=8.8, color='#cbd5e1', va='bottom', bbox=box_card_props, zorder=12)

    # Save output
    plt.subplots_adjust(left=0.03, right=0.97, top=0.95, bottom=0.04)
    plt.savefig(output_path, dpi=280, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Successfully created: {output_path}")

    return output_path

generate_timescale_hierarchy = create_timescale_hierarchy

if __name__ == "__main__":
    create_timescale_hierarchy()
