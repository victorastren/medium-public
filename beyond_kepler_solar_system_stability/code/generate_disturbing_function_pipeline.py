#!/usr/bin/env python3
"""
Generate Figure: From the Disturbing Function to Orbital Evolution
Section 2 (Perturbing a Keplerian Orbit):
Illustrates the 4-stage conceptual progression from Cartesian planetary geometry
to orbital elements, harmonic expansion, and orbital rates.

Optimized for 680px Medium reading width with dark astrophysics aesthetic.
"""

from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# -------------------------------------------------------------------------
# GLOBAL AESTHETICS & PALETTE (Astrophysics Dark Theme)
# -------------------------------------------------------------------------
BG_COLOR      = "#0a0e17"       # Deep cosmic dark
BG_PANEL      = "#111726"       # Panel background
BORDER        = "#1e293b"       # Subtle panel border
BORDER_LIGHT  = "#334155"       # Inner card border
TEXT_TITLE    = "#f8fafc"       # Bright white
TEXT_SUB      = "#94a3b8"       # Cool slate grey
TEXT_BODY     = "#cbd5e1"       # Light grey text

CYAN_ACCENT   = "#38bdf8"       # Stage 1: Geometry
GOLD_ACCENT   = "#fbbf24"       # Stage 2: Orbital elements
VIOLET_ACCENT = "#c084fc"       # Stage 3: Harmonic expansion
ROSE_ACCENT   = "#f43f5e"       # Stage 4: Orbital evolution

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'mathtext.fontset': 'dejavusans',
    'text.color': TEXT_BODY,
    'axes.labelcolor': TEXT_BODY,
    'xtick.color': TEXT_SUB,
    'ytick.color': TEXT_SUB,
})

def create_disturbing_function_pipeline(output_path=None):
    if output_path is None:
        output_path = DEFAULT_IMAGES_DIR / "disturbing_function_pipeline.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(10.5, 7.2), dpi=280, facecolor=BG_COLOR)

    ax = fig.add_axes([0.05, 0.07, 0.90, 0.82], facecolor=BG_PANEL)
    for s in ax.spines.values():
        s.set_edgecolor(BORDER)
        s.set_linewidth(1.3)
    ax.set_xticks([])
    ax.set_yticks([])

    # -------------------------------------------------------------------------
    # GLOBAL HEADER
    # -------------------------------------------------------------------------
    fig.text(0.05, 0.963, "From the Disturbing Function to Orbital Evolution",
             fontsize=14.5, fontweight='bold', color=TEXT_TITLE, va='top')
    fig.text(0.05, 0.928,
             "How the disturbing function turns planetary interactions into orbital evolution",
             fontsize=10.0, color=TEXT_SUB, va='top')

    # -------------------------------------------------------------------------
    # FOUR CONCEPTUAL STAGES
    # -------------------------------------------------------------------------
    stages = [
        {
            "num": "Stage 1",
            "title": "Heliocentric Relative Geometry",
            "math": r"$\mathbf{r}, \quad \mathbf{r}'$",
            "acc": CYAN_ACCENT,
            "bg": "#0b192e",
            "bd": "#0284c7"
        },
        {
            "num": "Stage 2",
            "title": "Disturbing Function in Orbital Elements",
            "math": r"$R = R(a, e, i, \lambda, \varpi, \Omega; \ldots)$",
            "acc": GOLD_ACCENT,
            "bg": "#201a08",
            "bd": "#ca8a04"
        },
        {
            "num": "Stage 3",
            "title": "Harmonic Expansion",
            "math": r"$\sum C \, \cos(\mathrm{combinations\ of\ orbital\ angles})$",
            "acc": VIOLET_ACCENT,
            "bg": "#1b0f2e",
            "bd": "#9333ea"
        },
        {
            "num": "Stage 4",
            "title": "Orbital Evolution",
            "math": r"$\dot{a}, \quad \dot{e}, \quad \dot{i}, \quad \dot{\varpi}, \quad \ldots$",
            "acc": ROSE_ACCENT,
            "bg": "#270815",
            "bd": "#e11d48"
        }
    ]

    transitions = [
        ("Express in orbital elements", GOLD_ACCENT, "#1c1708", "#ca8a04"),
        ("Fourier-Taylor series expansion", VIOLET_ACCENT, "#1b0e2b", "#9333ea"),
        ("Lagrange planetary equations", ROSE_ACCENT, "#240713", "#e11d48")
    ]

    card_w = 0.86
    card_x = 0.07
    card_h = 0.145

    y_positions = [0.772, 0.528, 0.284, 0.040]
    y_arrows = [0.706, 0.462, 0.218]

    for i, s in enumerate(stages):
        y = y_positions[i]

        # Single elegant card
        rect = patches.FancyBboxPatch((card_x, y), card_w, card_h,
                                      boxstyle="round,pad=0.015,rounding_size=0.025",
                                      facecolor=s["bg"], edgecolor=s["bd"], lw=1.3,
                                      transform=ax.transAxes, zorder=3)
        ax.add_patch(rect)

        # Stage title
        title_text = f"{s['num']}  ·  {s['title']}"
        ax.text(card_x + card_w / 2, y + card_h - 0.040, title_text,
                transform=ax.transAxes, fontsize=11.2, fontweight='bold', color=s["acc"],
                ha='center', va='center', zorder=5)

        # Math formula centered in card
        fsize = 13.5 if i == 2 else 15.0
        ax.text(card_x + card_w / 2, y + 0.042, s["math"],
                transform=ax.transAxes, fontsize=fsize, color="#ffffff",
                ha='center', va='center', zorder=5)

    # Connecting transitions between stages
    for j, (trans_text, t_color, t_bg, t_bd) in enumerate(transitions):
        ya = y_arrows[j]
        ax.text(0.50, ya, f"↓   {trans_text}   ↓",
                transform=ax.transAxes, fontsize=8.8, fontweight='bold', color=t_color,
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.28,rounding_size=0.2',
                          facecolor=t_bg, edgecolor=t_bd, lw=0.95, alpha=0.95), zorder=6)

    plt.savefig(output_path, dpi=280, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Successfully created: {output_path}")

    return output_path

generate_disturbing_function_pipeline = create_disturbing_function_pipeline

if __name__ == "__main__":
    create_disturbing_function_pipeline()
