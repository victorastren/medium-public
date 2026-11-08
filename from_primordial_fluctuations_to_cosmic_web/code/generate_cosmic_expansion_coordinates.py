#!/usr/bin/env python3
r"""
Generate editorial figure:
"Cosmic Expansion: Physical and Comoving Coordinates"

Section 2 main figure for:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Scientific & pedagogical specifications:
- Canvas: 1600 x 1080 px (10.0 x 6.75 in at 160 DPI) for generous vertical breathing room.
- Top banner subtitle: "Grid spacing expands in physical space  •  comoving coordinates remain fixed".
- Main panels:
  - Scale factor normalization: a(t1) = a1, a(t2) = 1.5 a1.
  - Comoving coordinate grid: subordinate reference styling (Delta x = 2 fixed).
  - Physical separation: hero emphasis with bold dark-slate dimension lines.
  - Symmetrical horizontal alignment: both "Physical separation" boxes and arrows are
    locked at the exact same horizontal baseline (phys_y = 1.00, phys_badge_y = 0.20),
    with extended vertical dotted lines in the earlier-time panel.
  - Recession velocity vector on Galaxy B: explicitly labeled v_{B/A} = H(t2) r_{AB}
    to denote velocity of B relative to A across physical separation r_{AB} = 3 a1.
- Bottom strip:
  - Card 1: Key Mathematical Relations (r = a x, H = a_dot / a, v = H r).
  - Card 2: Physical vs. Comoving Distances (invariant comoving interval, physical growth, bound galaxies).
  - Relaxed vertical line spacing (~21 px) and ample bottom padding (>26 px).
- All typography strictly >= 14.0 pt for mobile readability.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "cosmic_expansion_coordinates.png"


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure mathtext and typography (strictly >= 14.0 pt everywhere)
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    # Expanded canvas: 1600 x 1080 px at 160 DPI (10.0 in x 6.75 in)
    fig_w, fig_h = 10.0, 6.75
    dpi = 160
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'          # Primary headings
    DARK_SLATE = '#1e293b'    # Main text, panel titles
    SLATE = '#475569'         # Secondary annotations
    LIGHT_SLATE = '#64748b'   # Grid labels, subtle text
    BORDER_COLOR = '#cbd5e1'  # Box borders
    CARD_BG = '#f8fafc'       # Card backgrounds

    # Accents
    BLUE = '#0284c7'          # Earlier epoch / comoving
    BLUE_BG = '#f0f9ff'
    BLUE_DARK = '#0369a1'
    BLUE_BORDER = '#bae6fd'

    AMBER = '#d97706'         # Later epoch / expansion
    AMBER_BG = '#fffbeb'
    AMBER_DARK = '#b45309'
    AMBER_BORDER = '#fde68a'

    EMERALD_DARK = '#047857'  # Curvature / geometry
    EMERALD_BG = '#ecfdf5'
    EMERALD_BORDER = '#a7f3d0'

    # -------------------------------------------------------------------------
    # 1. Top Header Banner (y: 0.888 - 0.984, height ~104 px)
    # -------------------------------------------------------------------------
    ax_head = fig.add_axes([0.03, 0.888, 0.94, 0.096])
    ax_head.axis('off')
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)

    title_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.010",
                               mutation_aspect=(0.94 * fig_w) / (0.096 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_head.add_patch(title_box)

    ax_head.text(0.50, 0.67, "COSMIC EXPANSION: PHYSICAL AND COMOVING COORDINATES",
                 color=NAVY, fontsize=14.5, fontweight='bold', ha='center', va='center')
    ax_head.text(0.50, 0.27, "Grid spacing expands in physical space  •  Comoving coordinates remain fixed",
                 color=SLATE, fontsize=11.8, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 2. Main Two-Panel Layout (y: 0.290 - 0.865, height ~621 px)
    # -------------------------------------------------------------------------
    ax1 = fig.add_axes([0.03, 0.290, 0.455, 0.575])
    ax2 = fig.add_axes([0.515, 0.290, 0.455, 0.575])

    # Geometry for Panels:
    # Axes aspect ratio = (0.455 * 10) / (0.575 * 6.75) = 4.55 / 3.88125 = 1.1723
    # xlim = (-1.35, 11.25), width = 12.60 units
    # ylim = (-1.20, 9.55), height = 10.75 units
    # aspect ratio = 12.60 / 10.75 = 1.1721 (exact match, preserves spines)
    panels_data = [
        {
            'ax': ax1,
            'title': "EARLIER TIME",
            'subtitle': r"$t = t_1, \quad a(t_1) = a_1$",
            'color': BLUE_DARK,
            'bg': BLUE_BG,
            'border': BLUE_BORDER,
            'xlim': (-1.35, 11.25),
            'ylim': (-1.20, 9.55),
            'w_cell': 1.40,
            'h_cell': 1.40,
            'x0': 2.15,
            'y0': 2.70,
            'nx': 5,
            'ny': 3,
            'com_y': 6.80,
            'com_badge_y': 7.25,
            'phys_y': 1.00,        # Horizontally locked with Panel 2
            'phys_badge_y': 0.20,  # Horizontally locked with Panel 2
            'phys_text': "Physical separation:\n" + r"$r(t_1) = a(t_1)\,\Delta x = 2\,a_1$",
        },
        {
            'ax': ax2,
            'title': "LATER TIME",
            'subtitle': r"$t = t_2, \quad a(t_2) = 1.5\,a_1$",
            'color': AMBER_DARK,
            'bg': AMBER_BG,
            'border': AMBER_BORDER,
            'xlim': (-1.35, 11.25),
            'ylim': (-1.20, 9.55),
            'w_cell': 2.10,        # Exact 1.5x FLRW isotropic expansion of 1.40
            'h_cell': 2.10,        # Exact 1.5x FLRW isotropic expansion of 1.40
            'x0': 0.75,            # Generous >60 px left margin, >40 px right margin
            'y0': 2.00,
            'nx': 4,
            'ny': 3,
            'com_y': 6.80,
            'com_badge_y': 7.25,
            'phys_y': 1.00,        # Horizontally locked with Panel 1
            'phys_badge_y': 0.20,  # Horizontally locked with Panel 1
            'phys_text': "Physical separation:\n" + r"$r(t_2) = a(t_2)\,\Delta x = 3\,a_1$",
        }
    ]

    for p in panels_data:
        ax = p['ax']
        w_c = p['w_cell']
        h_c = p['h_cell']
        x0 = p['x0']
        y0 = p['y0']
        nx = p['nx']
        ny = p['ny']

        ax.set_facecolor('#ffffff')
        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER_COLOR)
            spine.set_linewidth(1.3)

        ax.set_xlim(p['xlim'])
        ax.set_ylim(p['ylim'])
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])

        # Header badge inside panel
        head_rect = FancyBboxPatch((0.025, 0.900), 0.95, 0.082,
                                   transform=ax.transAxes,
                                   boxstyle="round,pad=0.012,rounding_size=0.04",
                                   facecolor=p['bg'], edgecolor=p['border'], linewidth=1.3)
        ax.add_patch(head_rect)
        ax.text(0.05, 0.941, p['title'], transform=ax.transAxes,
                color=p['color'], fontsize=12.5, fontweight='bold', va='center')
        ax.text(0.95, 0.941, p['subtitle'], transform=ax.transAxes,
                color=p['color'], fontsize=12.5, fontweight='bold', ha='right', va='center')

        # Draw Comoving Grid with cleanly scaled tick labels (fontsize 11.5 pt, tight pad)
        grid_top = y0 + (ny - 1) * h_c
        for i in range(nx):
            gx = x0 + i * w_c
            ax.plot([gx, gx], [y0, grid_top],
                    color='#cbd5e1', lw=1.3, ls='-', zorder=1)
            # White-masked tick label so drop lines don't strike through text
            ax.text(gx, y0 - 0.22, f"$x={i}$",
                    color=LIGHT_SLATE, fontsize=11.5, ha='center', va='top', zorder=5,
                    bbox=dict(boxstyle='square,pad=0.08', facecolor='#ffffff', edgecolor='none'))

        grid_right = x0 + (nx - 1) * w_c
        for j in range(ny):
            gy = y0 + j * h_c
            ax.plot([x0, grid_right], [gy, gy],
                    color='#cbd5e1', lw=1.3, ls='-', zorder=1)
            ax.text(x0 - 0.20, gy, f"$y={j}$",
                    color=LIGHT_SLATE, fontsize=11.5, ha='right', va='center', zorder=5)

        # Primary galaxies A and B
        xA = x0 + 1 * w_c
        yA = y0 + 1 * h_c
        xB = x0 + 3 * w_c
        yB = y0 + 1 * h_c

        # Background cosmological galaxies
        bg_points = [(2, 2, 0.42, 30), (0, 2, 0.36, -25)] if ny > 2 else [(2, 0, 0.42, 30)]
        for bi, bj, bs, bang in bg_points:
            if bi < nx and bj < ny:
                bgx = x0 + bi * w_c
                bgy = y0 + bj * h_c
                ell_bg = patches.Ellipse((bgx, bgy), 0.50 * bs, 0.28 * bs, angle=bang,
                                         facecolor='#e2e8f0', edgecolor='#94a3b8', lw=1.1, zorder=2)
                ax.add_patch(ell_bg)
                ax.scatter([bgx], [bgy], color='#64748b', s=30 * bs, zorder=3)

        # Primary Galaxy A (Luminous Blue)
        ell_A = patches.Ellipse((xA, yA), 0.70, 0.40, angle=-25,
                                facecolor='#bfdbfe', edgecolor='#2563eb', lw=2.2, zorder=4)
        ax.add_patch(ell_A)
        ax.scatter([xA], [yA], color='#1d4ed8', s=85, zorder=5)

        # Compact, beautifully proportioned label box for Galaxy A (directly centered at xA)
        ax.text(xA, yA + 0.32, "Galaxy A\n" + r"$(x=1)$",
                color='#1e3a8a', fontsize=12.0, fontweight='bold', ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.12', facecolor='#ffffff', edgecolor='#93c5fd', lw=1.1, alpha=0.96))

        # Primary Galaxy B (Luminous Amber/Orange)
        ell_B = patches.Ellipse((xB, yB), 0.70, 0.40, angle=35,
                                facecolor='#fed7aa', edgecolor='#ea580c', lw=2.2, zorder=4)
        ax.add_patch(ell_B)
        ax.scatter([xB], [yB], color='#c2410c', s=85, zorder=5)

        # Compact, beautifully proportioned label box for Galaxy B (directly centered at xB)
        ax.text(xB, yB + 0.32, "Galaxy B\n" + r"$(x=3)$",
                color='#9a3412', fontsize=12.0, fontweight='bold', ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.12', facecolor='#ffffff', edgecolor='#fdba74', lw=1.1, alpha=0.96))

        # Comoving Interval Dimension Line (ABOVE grid) - subordinate reference styling
        com_y = p['com_y']
        com_badge_y = p['com_badge_y']
        ax.plot([xA, xA], [yA + 1.25, com_y], color='#38bdf8', ls='--', lw=1.3, zorder=2)
        ax.plot([xB, xB], [yB + 1.25, com_y], color='#38bdf8', ls='--', lw=1.3, zorder=2)
        ax.annotate('', xy=(xA, com_y), xytext=(xB, com_y),
                    arrowprops=dict(arrowstyle='<->', color='#0284c7', lw=1.8), zorder=3)
        ax.text((xA + xB) / 2, com_badge_y, r"Comoving separation: $\Delta x = 2$ (fixed)",
                color='#0369a1', fontsize=12.0, fontweight='bold', ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.22', facecolor='#f0f9ff', edgecolor='#bae6fd', lw=1.1))

        # Physical Distance Dimension Line (BELOW grid) - HERO EMPHASIS (horizontally locked at y = 1.00)
        phys_y = p['phys_y']
        phys_badge_y = p['phys_badge_y']
        # Vertical dotted lines extending down to phys_y = 1.00
        ax.plot([xA, xA], [yA - 0.28, phys_y], color='#475569', ls=':', lw=1.6, zorder=2)
        ax.plot([xB, xB], [yB - 0.28, phys_y], color='#475569', ls=':', lw=1.6, zorder=2)
        # Prominent hero arrow
        ax.annotate('', xy=(xA, phys_y), xytext=(xB, phys_y),
                    arrowprops=dict(arrowstyle='<->', color='#0f172a', lw=2.8), zorder=4)

        # Physical distance hero badge (horizontally locked at y = 0.20)
        ax.text((xA + xB) / 2, phys_badge_y, p['phys_text'],
                color='#0f172a', fontsize=12.2, fontweight='bold', ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.24', facecolor='#ffffff', edgecolor='#475569', lw=1.4, alpha=0.98))

        # In Panel 2: add recession velocity arrow and relative velocity label v_{B/A} = H(t2) r_{AB}
        if p['subtitle'].find('1.5') != -1:
            vel_start = xB + 0.35
            vel_end = xB + 1.85
            ax.annotate('', xy=(vel_end, yB), xytext=(vel_start, yB),
                        arrowprops=dict(arrowstyle='->', color='#dc2626', lw=2.6), zorder=6)
            # Position label cleanly under arrow starting outside grid line x=3
            ax.text(xB + 0.05, yB - 0.48, r"$v_{B/A} = H(t_2)\,r_{AB}$",
                    color='#991b1b', fontsize=12.0, fontweight='bold', ha='left', va='top',
                    bbox=dict(boxstyle='round,pad=0.18', facecolor='#fef2f2', edgecolor='#fecaca', lw=1.1))

    # -------------------------------------------------------------------------
    # 3. Bottom Cards Strip: Height ~265 px (y: 0.025 - 0.270)
    # -------------------------------------------------------------------------
    # Card 1 (Left: x: 0.03 - 0.485): Key Mathematical Relations
    ax_bot_left = fig.add_axes([0.03, 0.025, 0.455, 0.245])
    ax_bot_left.axis('off')
    ax_bot_left.set_xlim(0, 1)
    ax_bot_left.set_ylim(0, 1)

    card_l = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                            boxstyle="round,pad=0.0,rounding_size=0.021",
                            mutation_aspect=(0.455 * fig_w) / (0.245 * fig_h),
                            clip_on=False,
                            facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_bot_left.add_patch(card_l)

    ax_bot_left.text(0.035, 0.88, "KEY MATHEMATICAL RELATIONS",
                     color=NAVY, fontsize=12.0, fontweight='bold', va='center')

    # Three formula pills in Card 1: Position, Hubble expansion rate, and Spatial curvature (flat model)
    # Perfectly equal 15 px gaps between Blue-Orange and Orange-Green
    ax_bot_left.text(0.035, 0.65, r"$\mathbf{r}(t) = a(t)\,\mathbf{x}$",
                     color=BLUE_DARK, fontsize=12.5, fontweight='bold', va='center',
                     bbox=dict(boxstyle='round,pad=0.18', facecolor=BLUE_BG, edgecolor=BLUE_BORDER, lw=1.1))

    ax_bot_left.text(0.285, 0.65, r"$H(t) = \frac{\dot{a}(t)}{a(t)}$",
                     color=AMBER_DARK, fontsize=12.5, fontweight='bold', va='center',
                     bbox=dict(boxstyle='round,pad=0.18', facecolor=AMBER_BG, edgecolor=AMBER_BORDER, lw=1.1))

    ax_bot_left.text(0.500, 0.65, r"$K = 0$ (flat model)",
                     color=EMERALD_DARK, fontsize=12.2, fontweight='bold', va='center',
                     bbox=dict(boxstyle='round,pad=0.18', facecolor=EMERALD_BG, edgecolor=EMERALD_BORDER, lw=1.1))

    # Explanations with generous spacing and unclipped margins
    ax_bot_left.text(0.035, 0.38, "•", color=DARK_SLATE, fontsize=12.0, va='center')
    ax_bot_left.text(0.070, 0.38, "Physical position: r(t) = a(t) x (Cartesian slice)",
                     color=DARK_SLATE, fontsize=12.0, va='center')
    ax_bot_left.text(0.035, 0.18, "•", color=DARK_SLATE, fontsize=12.0, va='center')
    ax_bot_left.text(0.070, 0.18, "Recession velocity: v = ȧ x = H(t) r",
                     color=DARK_SLATE, fontsize=12.0, va='center')

    # Card 2 (Right: x: 0.515 - 0.970): Physical vs. Comoving Distances
    ax_bot_right = fig.add_axes([0.515, 0.025, 0.455, 0.245])
    ax_bot_right.axis('off')
    ax_bot_right.set_xlim(0, 1)
    ax_bot_right.set_ylim(0, 1)

    card_r = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                            boxstyle="round,pad=0.0,rounding_size=0.021",
                            mutation_aspect=(0.455 * fig_w) / (0.245 * fig_h),
                            clip_on=False,
                            facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_bot_right.add_patch(card_r)

    ax_bot_right.text(0.035, 0.88, "PHYSICAL VS. COMOVING DISTANCES",
                      color=NAVY, fontsize=12.0, fontweight='bold', va='center')

    # Four clear bullet points with uniform hanging indents and vertical alignment
    bullets_r = [
        ("•", "Invariant comoving separation: Δx = 2", 0.74),
        ("•", "Physical separation: 2 a₁ → 3 a₁ (+50%)", 0.57),
        ("•", "Illustrated geometry: flat Euclidean space (K = 0)", 0.40),
    ]
    for b, txt, y_pos in bullets_r:
        ax_bot_right.text(0.035, y_pos, b, color=DARK_SLATE, fontsize=12.0, va='center')
        ax_bot_right.text(0.070, y_pos, txt, color=DARK_SLATE, fontsize=12.0, va='center')

    # Item 4 with second line vertically aligned with text start
    ax_bot_right.text(0.035, 0.23, "•", color=DARK_SLATE, fontsize=12.0, va='center')
    ax_bot_right.text(0.070, 0.23, "Gravitationally bound systems do not follow",
                      color=DARK_SLATE, fontsize=12.0, va='center')
    ax_bot_right.text(0.070, 0.10, "the general expansion",
                      color=DARK_SLATE, fontsize=12.0, va='center')

    plt.savefig(output_path, dpi=dpi, facecolor='#ffffff')
    plt.close(fig)
    print(f"Figure successfully saved to: {output_path}")


if __name__ == "__main__":
    create_figure()
