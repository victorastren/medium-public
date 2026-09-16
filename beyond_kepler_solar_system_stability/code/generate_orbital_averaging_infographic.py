#!/usr/bin/env python3
"""
Generate Infographic: What Averaging Removes — and What Survives
Two-panel visualization of Orbital Averaging for Section 2:
Top: Instantaneous osculating eccentricity e(t) containing rapid short-period oscillations
     superimposed on slow secular variation.
Bottom: Averaged secular eccentricity e_bar(t) where short-period terms cancel,
        leaving only the long-term dynamical evolution.
Optimized for 680px Medium reading width with dark astrophysics aesthetic.
"""

from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

import matplotlib.pyplot as plt
import numpy as np

# -------------------------------------------------------------------------
# GLOBAL AESTHETICS & PALETTE (Astrophysics Dark Theme)
# -------------------------------------------------------------------------
BG_COLOR     = "#0a0e17"       # Deep cosmic dark
BG_PANEL     = "#111726"       # Panel background
BORDER       = "#1e293b"       # Subtle panel border
BORDER_LIGHT = "#334155"       # Card border
TEXT_TITLE   = "#f8fafc"       # Bright white
TEXT_SUB     = "#94a3b8"       # Cool slate grey
TEXT_BODY    = "#cbd5e1"       # Light grey text

FAST_COLOR   = "#38bdf8"       # Cyan for rapid short-period motion
SLOW_COLOR   = "#f43f5e"       # Rose/coral for secular timescale
SLOW_ACCENT  = "#fb7185"       # Lighter coral
GOLD_ACCENT  = "#fbbf24"       # Highlight gold
GRID_COLOR   = "#1e293b"       # Subtle grid lines

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'mathtext.fontset': 'dejavusans',
    'text.color': TEXT_BODY,
    'axes.labelcolor': TEXT_BODY,
    'xtick.color': TEXT_SUB,
    'ytick.color': TEXT_SUB,
})

def create_orbital_averaging_infographic(output_path=None):
    if output_path is None:
        output_path = DEFAULT_IMAGES_DIR / "orbital_averaging_concept.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(11.5, 7.2), dpi=280, facecolor=BG_COLOR)

    # Main layout: Header at top, Top panel, Middle transition banner, Bottom panel, Footer note
    # Generous margins and breathing room
    ax_top = fig.add_axes([0.08, 0.56, 0.88, 0.29], facecolor=BG_PANEL)
    ax_bot = fig.add_axes([0.08, 0.16, 0.88, 0.29], facecolor=BG_PANEL)

    for ax in [ax_top, ax_bot]:
        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)
            spine.set_linewidth(1.3)
        ax.grid(True, linestyle=':', color=GRID_COLOR, alpha=0.6, lw=0.8)

    # -------------------------------------------------------------------------
    # SYNTHETIC CELESTIAL MECHANICS SIGNAL (0 to 1200 Years)
    # -------------------------------------------------------------------------
    t = np.linspace(0, 1200, 2400)

    # Secular component: smooth long-period modulation (millennia scale)
    e_sec = 0.044 + 0.0085 * np.sin(2 * np.pi * t / 2600 + 0.45) + 0.0020 * np.cos(2 * np.pi * t / 1500)

    # Short-period perturbations: planetary conjunctions and orbital harmonics
    delta_e = (
        0.0032 * np.sin(2 * np.pi * t / 19.8) +
        0.0022 * np.sin(2 * np.pi * t / 11.9 + 1.1) +
        0.0017 * np.cos(2 * np.pi * t / 59.6 + 0.5) +
        0.0011 * np.sin(2 * np.pi * t / 29.5 + 2.2)
    )

    # Full osculating element
    e_osc = e_sec + delta_e

    # -------------------------------------------------------------------------
    # TOP PANEL: INSTANTANEOUS OSCULATING ELEMENT (FULL MOTION)
    # -------------------------------------------------------------------------
    # Underlying secular backbone
    ax_top.plot(t, e_sec, color=SLOW_ACCENT, lw=2.0, ls='--', alpha=0.65, zorder=3)

    # Full osculating signal (cyan)
    ax_top.plot(t, e_osc, color=FAST_COLOR, lw=1.2, alpha=0.92, zorder=4)

    # Top Panel Styling
    ax_top.set_xlim(0, 1200)
    ax_top.set_ylim(0.033, 0.071)
    ax_top.set_ylabel("Eccentricity $e$", fontsize=10.5, fontweight='bold', color=TEXT_TITLE)
    ax_top.tick_params(labelsize=9.5)
    ax_top.set_xticklabels([])  # Share x-scale visually with bottom panel

    # Top Panel Title Badge (Simplified, no Hamiltonian formula)
    ax_top.text(0.02, 0.90, "1. Full Perturbed Motion", transform=ax_top.transAxes,
                fontsize=11.0, fontweight='bold', color=FAST_COLOR, va='top',
                bbox=dict(boxstyle='round,pad=0.35,rounding_size=0.2',
                          facecolor='#06192a', edgecolor=FAST_COLOR, lw=1.1, alpha=0.95), zorder=6)

    # Top Panel Right Annotation: Short-period variations
    top_note = (
        r"$\mathbf{Short\text{-}Period\ Variations}$:" "\n"
        r"• Driven by changing orbital phases and recurring conjunctions" "\n"
        r"• Rapid fluctuations that alternate sign and average to zero over time"
    )
    ax_top.text(0.55, 0.90, top_note, transform=ax_top.transAxes,
                fontsize=8.8, color='#e0f2fe', va='top', ha='left',
                bbox=dict(boxstyle='round,pad=0.45,rounding_size=0.3',
                          facecolor='#071828', edgecolor=BORDER_LIGHT, lw=1.0, alpha=0.92), zorder=6)

    # Conjunction bracket
    ax_top.axvspan(340, 460, color=FAST_COLOR, alpha=0.07, zorder=2)
    ax_top.plot([340, 340, 460, 460], [0.0365, 0.0350, 0.0350, 0.0365], color=FAST_COLOR, lw=1.2, zorder=5)
    ax_top.text(400, 0.0370, "Conjunction cycles\n(cancel over time)", color=FAST_COLOR,
                fontsize=8.0, ha='center', va='bottom', fontweight='bold', zorder=6)

    # -------------------------------------------------------------------------
    # MIDDLE TRANSITION BANNER: THE AVERAGING OPERATION (SIMPLIFIED)
    # -------------------------------------------------------------------------
    trans_text = r"$\mathbf{Average\ over\ fast\ orbital\ phases} \quad \longrightarrow \quad \text{short-period variations cancel, slow secular evolution remains}$"
    fig.text(0.52, 0.505, trans_text, color=GOLD_ACCENT, fontsize=9.4,
             ha='center', va='center', fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.40,rounding_size=0.3',
                       facecolor='#1c1917', edgecolor=GOLD_ACCENT, lw=1.1, alpha=0.95))

    # Downward transition arrows
    fig.text(0.085, 0.505, "↓", color=GOLD_ACCENT, fontsize=14, ha='center', va='center', fontweight='bold')
    fig.text(0.955, 0.505, "↓", color=GOLD_ACCENT, fontsize=14, ha='center', va='center', fontweight='bold')

    # -------------------------------------------------------------------------
    # BOTTOM PANEL: AVERAGED SECULAR EVOLUTION (WHAT SURVIVES)
    # -------------------------------------------------------------------------
    # Shaded stability envelope
    ax_bot.fill_between(t, e_sec - 0.0010, e_sec + 0.0010, color=SLOW_COLOR, alpha=0.18, zorder=2)

    # Pure secular curve
    ax_bot.plot(t, e_sec, color=SLOW_ACCENT, lw=2.8, zorder=4)

    # Bottom Panel Styling
    ax_bot.set_xlim(0, 1200)
    ax_bot.set_ylim(0.033, 0.071)
    ax_bot.set_xlabel("Time (Years)", fontsize=10.5, fontweight='bold', color=TEXT_TITLE)
    ax_bot.set_ylabel(r"Eccentricity $\bar{e}$", fontsize=10.5, fontweight='bold', color=TEXT_TITLE)
    ax_bot.tick_params(labelsize=9.5)

    # Bottom Panel Title Badge (Simplified, no Hamiltonian formula)
    ax_bot.text(0.02, 0.90, "2. Averaged Secular Evolution", transform=ax_bot.transAxes,
                fontsize=11.0, fontweight='bold', color=SLOW_ACCENT, va='top',
                bbox=dict(boxstyle='round,pad=0.35,rounding_size=0.2',
                          facecolor='#260814', edgecolor=SLOW_ACCENT, lw=1.1, alpha=0.95), zorder=6)

    # Bottom Panel Right Annotation: Smooth secular evolution
    bot_note = (
        r"$\mathbf{Smooth\ Secular\ Evolution}$:" "\n"
        r"• Isolates the slow, net gravitational coupling between orbits" "\n"
        r"• Governs whether orbital shapes remain bounded over millennia"
    )
    ax_bot.text(0.55, 0.90, bot_note, transform=ax_bot.transAxes,
                fontsize=8.8, color='#ffe4e6', va='top', ha='left',
                bbox=dict(boxstyle='round,pad=0.45,rounding_size=0.3',
                          facecolor='#240713', edgecolor=BORDER_LIGHT, lw=1.0, alpha=0.92), zorder=6)

    # Subtle label along curve
    ax_bot.plot(450, e_sec[int(450 / 1200 * len(t))], marker='o', markersize=5.0, color=SLOW_ACCENT, zorder=7)
    ax_bot.text(460, 0.0545, "Smooth secular evolution", color=SLOW_ACCENT,
                fontsize=8.8, fontweight='bold', va='bottom', zorder=7)

    # Bounded envelope indicator line
    ax_bot.axhline(0.0555, color='#475569', ls=':', lw=1.1, alpha=0.6, zorder=2)
    ax_bot.text(80, 0.0562, "Bounded secular stability envelope", color='#64748b',
                fontsize=8.0, ha='left', va='bottom', style='italic', zorder=5)

    # -------------------------------------------------------------------------
    # GLOBAL HEADER & FOOTER
    # -------------------------------------------------------------------------
    # Header Titles
    fig.text(0.08, 0.958, "What Orbital Averaging Removes — and What Survives",
             fontsize=14.5, fontweight='bold', color=TEXT_TITLE, va='top')
    fig.text(0.08, 0.920,
             "Separating short-period orbital variations from slow secular evolution",
             fontsize=10.2, color=TEXT_SUB, va='top')

    # Footer Physical Takeaway Note (exact requested wording)
    footer_text = (
        r"Orbital averaging removes short-period variations and isolates the slow secular interactions " "\n"
        r"that govern the long-term evolution of the planetary orbits."
    )
    fig.text(0.50, 0.048, footer_text, fontsize=8.8, color='#cbd5e1', ha='center', va='center',
             bbox=dict(boxstyle='round,pad=0.45,rounding_size=0.3',
                       facecolor='#0d1422', edgecolor=BORDER_LIGHT, lw=1.1, alpha=0.95))

    plt.savefig(output_path, dpi=280, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Successfully created: {output_path}")

    return output_path

generate_orbital_averaging_infographic = create_orbital_averaging_infographic

if __name__ == "__main__":
    create_orbital_averaging_infographic()
