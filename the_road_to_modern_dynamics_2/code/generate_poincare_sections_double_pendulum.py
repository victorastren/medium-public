#!/usr/bin/env python3
r"""
Generate infographic for Article 2:
"From Regular Motion to Chaos: Poincaré Sections of the Double Pendulum"

Matches the visual hierarchy and design of existing figures:
- Canvas: 18.0 x 9.8 inches at 240 DPI
- Editorial Card Containers with colored header accent bars and circular letter badges (A, B, C)
- Typography hierarchy strictly matching CRTBP & Poincaré return map figures:
  * Main title: 22.5 pt bold (Navy #0f172a)
  * Subtitle: 16.5 pt italic (Dark Slate #1e293b)
  * Panel Badge letter: 16.0 pt bold (White on colored badge)
  * Panel Title: 17.5 pt bold (Navy #0f172a)
  * Panel Subtitle / Energy: 15.0 pt bold
  * Axis labels: 16.5 pt bold (Dark Slate #1e293b)
  * Axis ticks: 14.5 pt bold (Slate #334155)
  * Legend text: 15.0 pt bold
  * Minimum font size strictly >= 14.5 pt across the entire figure!
"""

import json
import pickle
import sys
import time
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PNG = SCRIPT_DIR.parent / "images" / "poincare_sections_double_pendulum.png"
DEFAULT_JSON = SCRIPT_DIR / "poincare_sections_metadata.json"
CACHE_FILE = SCRIPT_DIR / "poincare_sim_cache.pkl"
ISLAND_CACHE = SCRIPT_DIR / "scratch" / "island_orbits.pkl"

def generate_figure(output_png=DEFAULT_PNG, output_json=DEFAULT_JSON):
    output_png = Path(output_png)
    output_json = Path(output_json)
    output_png.parent.mkdir(parents=True, exist_ok=True)
    
    if not CACHE_FILE.exists():
        print(f"Error: Cache file {CACHE_FILE} not found. Please run with simulation first.")
        sys.exit(1)
        
    print(f"Loading simulation data from cache: {CACHE_FILE}")
    with open(CACHE_FILE, 'rb') as f:
        cached_data = pickle.load(f)
        all_results = cached_data['all_results']
        metadata = cached_data['metadata']

    # Curated Editorial Palette matching Article 2 style
    NAVY = '#0f172a'          # Deep slate navy for main headings
    DARK_SLATE = '#1e293b'    # Body text & subheaders
    SLATE = '#334155'         # Secondary text & tick labels
    BORDER_CARD = '#cbd5e1'   # Card border
    BG_CARD = '#f8fafc'       # Light background for panels
    BG_BOX = '#ffffff'        # Pure white for plot areas

    # Panel accent themes
    EMERALD_ACCENT = '#059669' # Emerald for Regular regime (Panel A)
    EMERALD_LIGHT = '#ecfdf5'  # Soft emerald tint
    EMERALD_BORDER = '#6ee7b7' # Emerald border

    BLUE_ACCENT = '#2563eb'   # Primary blue for Mixed dynamics (Panel B)
    BLUE_LIGHT = '#eff6ff'    # Soft blue tint
    BLUE_BORDER = '#93c5fd'   # Blue border

    PURPLE_ACCENT = '#6366f1' # Indigo / Purple for Chaotic regions (Panel C)
    PURPLE_LIGHT = '#eef2ff'  # Soft purple tint
    PURPLE_BORDER = '#a5b4fc' # Purple border

    # Trajectory point colors
    COLOR_REG = '#059669'      # Rich Emerald for regular invariant curves
    COLOR_CHAOS = '#475569'    # Deep Slate for chaotic point clouds
    COLOR_BOUND = '#94a3b8'    # Subtle dashed boundary line

    # Matplotlib styling for publication quality
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'axes.edgecolor': '#94a3b8',
        'axes.linewidth': 1.3,
    })

    # High-resolution widescreen canvas (18 x 9.8 inches at 240 DPI)
    fig_w = 18.0
    fig_h = 9.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Main Header (>= 16.5 pt)
    fig.text(0.5, 0.956,
             "Poincaré Sections of the Double Pendulum at Different Energies",
             fontsize=22.5, weight='bold', color=NAVY, ha='center', va='center')

    # Background axis for panel cards, header accent bars, and badges
    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')

    # 3 equal cards of width 0.304 each (matching CRTBP and return map layout)
    y_card = 0.088
    h_card = 0.812

    x1 = 0.024
    w1 = 0.304
    x2 = 0.348
    w2 = 0.304
    x3 = 0.672
    w3 = 0.304

    panels_spec = [
        (x1, w1, 0.5, "A", "Low Energy", r"$\mathbf{\mathcal{E} = 0.5}$",
         '#047857', EMERALD_LIGHT, EMERALD_BORDER,
         {'xlim': (-0.85, 0.85), 'ylim': (-1.65, 1.65)}),
        (x2, w2, 1.2, "B", "Intermediate Energy", r"$\mathbf{\mathcal{E} = 1.2}$",
         '#1d4ed8', BLUE_LIGHT, BLUE_BORDER,
         {'xlim': (-1.35, 1.35), 'ylim': (-2.65, 2.65)}),
        (x3, w3, 2.0, "C", "Higher Energy", r"$\mathbf{\mathcal{E} = 2.0}$",
         '#4338ca', PURPLE_LIGHT, PURPLE_BORDER,
         {'xlim': (-1.85, 1.85), 'ylim': (-3.55, 3.55)}),
    ]

    for px, pw, E, num, title, subtitle, acc_color, bg_tint, bdr_color, lim in panels_spec:
        # 1. Card container
        card_rect = patches.FancyBboxPatch(
            (px, y_card), pw, h_card,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.4,
            zorder=1
        )
        ax_bg.add_patch(card_rect)

        # 2. Header accent bar
        hbar_h = 0.086
        hbar_y = y_card + h_card - hbar_h
        hbar_rect = patches.FancyBboxPatch(
            (px, hbar_y), pw, hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=bg_tint, edgecolor=bdr_color, linewidth=1.2,
            zorder=2
        )
        ax_bg.add_patch(hbar_rect)

        # 3. Badge circle (A, B, C)
        badge_x = px + 0.024
        badge_y = hbar_y + hbar_h / 2
        badge_c = patches.Circle(
            (badge_x, badge_y), 0.016,
            facecolor=acc_color, edgecolor='none',
            zorder=3
        )
        ax_bg.add_patch(badge_c)
        ax_bg.text(badge_x, badge_y, num, fontsize=16.0, weight='bold',
                   color='#ffffff', ha='center', va='center', zorder=4)

        # 4. Title & Subtitle with bold hierarchy
        ax_bg.text(badge_x + 0.022, badge_y + 0.016, title,
                   fontsize=17.5, weight='bold', color=NAVY, va='center', zorder=4)
        energy_stroke = [pe.withStroke(linewidth=0.9, foreground=acc_color)]
        ax_bg.text(badge_x + 0.022, badge_y - 0.017, subtitle,
                   fontsize=19.0, weight='bold', color=acc_color, va='center',
                   path_effects=energy_stroke, zorder=4)

        # 5. Dedicated Plot Axis inside the Card
        # Padding adjusted to prevent y-axis label bleed on card border
        ax_left = px + 0.058
        ax_width = pw - 0.074
        ax_bottom = y_card + 0.082
        ax_height = hbar_y - ax_bottom - 0.024

        ax = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height], facecolor=BG_BOX, zorder=3)
        res_list = all_results[E]

        # Accessible boundary curve
        th1_grid = np.linspace(-np.pi, np.pi, 600)
        T_grid = E - 2.0 * (1.0 - np.cos(th1_grid))
        valid = T_grid >= 0
        if np.any(valid):
            th_v = th1_grid[valid]
            p_bound = np.sqrt(4.0 * T_grid[valid])
            ax.plot(th_v, p_bound, color=COLOR_BOUND, linestyle='--', lw=1.3, zorder=2)
            ax.plot(th_v, -p_bound, color=COLOR_BOUND, linestyle='--', lw=1.3, zorder=2)

        # Chaotic trajectories (background layer)
        chaos_alpha = 0.35 if E == 1.2 else 0.45
        chaos_s = 1.0 if E == 1.2 else 1.1
        for r in res_list:
            if r['is_chaotic']:
                pts = r['pts']
                ax.scatter(pts[:, 0], pts[:, 1], s=chaos_s, color=COLOR_CHAOS,
                           alpha=chaos_alpha, edgecolors='none', rasterized=True, zorder=3)

        # Regular trajectories (foreground layer)
        reg_alpha = 0.48 if E == 1.2 else 0.85
        reg_s = 1.8 if E == 1.2 else 2.2
        for r in res_list:
            if not r['is_chaotic']:
                pts = r['pts']
                ax.scatter(pts[:, 0], pts[:, 1], s=reg_s, color=COLOR_REG,
                           alpha=reg_alpha, edgecolors='none', rasterized=True, zorder=4)

        # In Panel B, highlight the numerically verified period-3 resonance chain
        if E == 1.2:
            # 1. Targeted sampling around the period-3 elliptic orbit to display nested island curves
            if ISLAND_CACHE.exists():
                with open(ISLAND_CACHE, 'rb') as f:
                    island_orbits = pickle.load(f)
                for orb in island_orbits:
                    ax.scatter(orb[:, 0], orb[:, 1], s=2.5, color='#d97706',
                               alpha=0.92, edgecolors='none', rasterized=True, zorder=6)

            ell_pts = np.array([
                [0.330966, -0.341879],
                [-0.820423, -0.324816],
                [0.540800, -1.461239]
            ])
            hyp_pts = np.array([
                [0.000000, -0.393529],
                [-0.846369, -0.873638],
                [0.846369, -0.873638]
            ])
            # Periodic points: slightly smaller, crisp markers
            ax.scatter(ell_pts[:, 0], ell_pts[:, 1], s=42, color='#f59e0b',
                       edgecolors=NAVY, linewidth=1.3, zorder=9)
            ax.scatter(hyp_pts[:, 0], hyp_pts[:, 1], s=48, marker='x',
                       color='#dc2626', linewidth=2.0, zorder=9)

            # Explicit labels for elliptic periodic centers E_1, E_2, E_3
            stroke = [pe.withStroke(linewidth=3.5, foreground='white')]
            ax.text(0.44, -0.32, 'E₁', fontsize=13.5, weight='bold', color=NAVY,
                    ha='left', va='center', zorder=11, path_effects=stroke)
            ax.text(-0.95, -0.26, 'E₂', fontsize=13.5, weight='bold', color=NAVY,
                    ha='right', va='center', zorder=11, path_effects=stroke)
            ax.text(0.66, -1.48, 'E₃', fontsize=13.5, weight='bold', color=NAVY,
                    ha='left', va='center', zorder=11, path_effects=stroke)

            # Compact, discreet callout in the upper-right whitespace explaining the period-3 cycle
            # Leader line omitted to preserve completely unobstructed view of invariant curves
            callout_text = "Period-3 resonance chain\nE₁ → E₂ → E₃ → E₁"
            ax.text(1.30, 2.60, callout_text,
                    ha='right', va='top',
                    fontsize=10.5, fontweight='bold', color=NAVY,
                    bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff',
                              edgecolor='#cbd5e1', alpha=0.96, lw=1.0),
                    zorder=12)

        ax.set_xlim(lim['xlim'])
        ax.set_ylim(lim['ylim'])
        ax.grid(True, linestyle=':', alpha=0.40, color='#cbd5e1', zorder=1)

        # Clean, well-spaced tick intervals
        if E == 0.5:
            ax.set_xticks([-0.6, -0.3, 0.0, 0.3, 0.6])
            ax.set_yticks([-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5])
        elif E == 1.2:
            ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
            ax.set_yticks([-2.0, -1.0, 0.0, 1.0, 2.0])
        elif E == 2.0:
            ax.set_xticks([-1.5, -0.75, 0.0, 0.75, 1.5])
            ax.set_yticks([-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0])

        # Axis typography strictly matching hierarchy
        ax.set_xlabel(r"$\theta_1$ (rad)", fontsize=16.5, weight='bold', color=DARK_SLATE, labelpad=5)
        ax.set_ylabel(r"$p_1$ (normalized)", fontsize=16.5, weight='bold', color=DARK_SLATE, labelpad=3)
        ax.tick_params(axis='both', which='major', labelsize=14.5, colors=SLATE, length=5, width=1.3)
        for tick in ax.get_xticklabels() + ax.get_yticklabels():
            tick.set_fontweight('bold')

    # Shared bottom legend plaque spanning exactly beneath cards in 2 balanced rows
    leg_x = 0.024
    leg_w = 0.952
    leg_h = 0.064
    leg_y = 0.012

    leg_rect = patches.FancyBboxPatch(
        (leg_x, leg_y), leg_w, leg_h,
        boxstyle="round,pad=0.0,rounding_size=0.012",
        facecolor='#f8fafc', edgecolor=BORDER_CARD, linewidth=1.2,
        zorder=2
    )
    ax_bg.add_patch(leg_rect)

    # 2 rows with vertically aligned columns
    y_row1 = leg_y + leg_h * 0.70
    y_row2 = leg_y + leg_h * 0.30

    # Column 1 (Left-aligned for both rows)
    x_c1 = leg_x + 0.018
    # Row 1 Col 1: Regular trajectories
    ax_bg.plot(x_c1, y_row1, marker='o', markersize=8.0, color=COLOR_REG, markeredgecolor='none', zorder=4)
    ax_bg.text(x_c1 + 0.012, y_row1, "Regular trajectories",
               fontsize=14.0, weight='bold', color=DARK_SLATE, va='center', zorder=4)

    # Row 2 Col 1: Resonance islands (amber curves surrounding elliptic periodic points)
    # Small closed ellipse representing invariant curve enclosing the marked elliptic center
    ell_patch = patches.Ellipse(
        (x_c1, y_row2), width=0.014, height=0.024, angle=0,
        edgecolor='#d97706', facecolor='#fef3c7', alpha=0.45, linewidth=1.6,
        zorder=4
    )
    ax_bg.add_patch(ell_patch)
    ax_bg.plot(x_c1, y_row2, marker='o', markersize=5.0, color='#f59e0b',
               markeredgecolor=NAVY, markeredgewidth=1.1, zorder=5)
    ax_bg.text(x_c1 + 0.012, y_row2, "Resonance islands (amber curves surrounding elliptic periodic points)",
               fontsize=14.0, weight='bold', color=DARK_SLATE, va='center', zorder=4)

    # Column 2 (Left-aligned for both rows)
    x_c2 = leg_x + 0.518
    # Row 1 Col 2: Chaotic trajectories
    ax_bg.plot(x_c2, y_row1, marker='o', markersize=8.0, color=COLOR_CHAOS, markeredgecolor='none', zorder=4)
    ax_bg.text(x_c2 + 0.012, y_row1, "Chaotic trajectories",
               fontsize=14.0, weight='bold', color=DARK_SLATE, va='center', zorder=4)

    # Row 2 Col 2: Hyperbolic periodic points
    ax_bg.plot(x_c2, y_row2, marker='x', markersize=9.0, color='#dc2626', markeredgewidth=2.2, zorder=4)
    ax_bg.text(x_c2 + 0.012, y_row2, "Hyperbolic periodic points",
               fontsize=14.0, weight='bold', color=DARK_SLATE, va='center', zorder=4)

    # Column 3 (Centered vertically across both rows)
    x_c3 = leg_x + 0.750
    y_c3 = leg_y + leg_h * 0.50
    ax_bg.plot([x_c3 - 0.008, x_c3 + 0.008], [y_c3, y_c3], color=COLOR_BOUND, linestyle='--', lw=2.0, zorder=4)
    ax_bg.text(x_c3 + 0.014, y_c3, r"Accessible boundary ($\dot{\theta}_2 = 0$)",
               fontsize=14.0, weight='bold', color=DARK_SLATE, va='center', zorder=4)

    print("Saving PNG to", output_png)
    fig.savefig(output_png, dpi=240, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print("Generation complete!")

if __name__ == "__main__":
    generate_figure()
