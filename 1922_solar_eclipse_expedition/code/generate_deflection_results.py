#!/usr/bin/env python3
r"""
Create results plot for Medium (680px width):
"WALLAL LIGHT-DEFLECTION RESULTS"
Comparing Wallal eclipse measurements to Newtonian and General Relativistic predictions,
with a compact secondary 1919 context inset panel.

Designed to accompany the section "What the 1922 Measurements Established".
- High contrast cosmic dark theme (#0b0f19 background, #0f172a card)
- Main panel (left ~72%):
    - 4 horizontal rows:
        1. Newtonian / Einstein 1911 (0.87″)
        2. General relativity (1.75″)
        3. Wallal 1923 (15-foot cameras) (1.72″ ± 0.11″)
        4. Wallal final result (1928) (1.75″ ± 0.09″)
    - Vertical reference guides:
        - GR line prominent (sky blue #38bdf8, bold)
        - Newtonian line (amber #f59e0b, dashed)
    - Both Wallal points in same vibrant mint family (#34d399)
    - True astronomical double-prime symbol ($^{\prime\prime}$) throughout
    - Refined x-axis label size (15.0pt bold)
- Inset panel (right ~28%):
    - Positioned higher in the upper-right corner
    - Tight vertical gap between Príncipe and Sobral (4-inch)
    - Compact card dimensions
- Outputs standard 680px (1x) and 2200px (2x / Retina)
"""

import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
OUT_DIR = PROJECT_DIR / "images"

def create_results_plot(out_1x=None, out_2x=None):
    if out_1x is None:
        out_1x = OUT_DIR / "wallal_deflection_results.png"
    if out_2x is None:
        out_2x = OUT_DIR / "wallal_deflection_results_2x.png"
    out_1x = Path(out_1x)
    out_2x = Path(out_2x)
    out_1x.parent.mkdir(parents=True, exist_ok=True)
    out_2x.parent.mkdir(parents=True, exist_ok=True)

    # Matplotlib styling with STIX mathtext for genuine astronomical prime symbols
    plt.rcParams['mathtext.fontset'] = 'stixsans'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.rcParams['font.family'] = 'sans-serif'

    # Canvas dimensions: 11.0 x 7.2 inches (scaled down to 680 x 445 px)
    fig_w, fig_h = 11.0, 7.2
    dpi = 200
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)

    bg_color = '#0b0f19'  # Outer cosmic background
    card_bg = '#0f172a'   # Deep navy card background
    fig.patch.set_facecolor(bg_color)

    # Base axes covering entire canvas for layout and cards
    ax_card = fig.add_axes([0, 0, 1, 1])
    ax_card.set_facecolor(bg_color)
    ax_card.set_xlim(0, fig_w)
    ax_card.set_ylim(0, fig_h)
    ax_card.axis('off')

    # Draw rounded main card
    card_margin_x = 0.20
    card_margin_y = 0.20
    card_w = fig_w - 2 * card_margin_x  # 10.60 in
    card_h = fig_h - 2 * card_margin_y  # 6.80 in

    card = FancyBboxPatch(
        (card_margin_x, card_margin_y), card_w, card_h,
        boxstyle="round,pad=0.04,rounding_size=0.18",
        facecolor=card_bg, edgecolor='#334155', linewidth=1.5, zorder=1
    )
    ax_card.add_patch(card)

    # Header Banner Card
    header_h = 1.48
    header_y = card_margin_y + card_h - header_h
    header_box = FancyBboxPatch(
        (card_margin_x, header_y), card_w, header_h,
        boxstyle="round,pad=0.04,rounding_size=0.18",
        facecolor='#1e293b', edgecolor='#475569', linewidth=1.2, zorder=2
    )
    ax_card.add_patch(header_box)

    # Header Text
    ax_card.text(
        fig_w / 2.0, header_y + 0.92,
        "WALLAL LIGHT-DEFLECTION RESULTS",
        color='#ffffff', fontsize=21.0, fontweight='bold', ha='center', va='center', zorder=3
    )
    ax_card.text(
        fig_w / 2.0, header_y + 0.40,
        "Wallal measurements compared with the Newtonian and general-relativistic predictions",
        color='#7dd3fc', fontsize=14.0, fontweight='bold', ha='center', va='center', zorder=3
    )

    # =========================================================================
    # MAIN ERROR-BAR PLOT (LEFT ~72% OF CONTENT WIDTH)
    # =========================================================================
    plot_left_in = 3.32
    plot_width_in = 3.35
    plot_bottom_in = 1.35
    plot_height_in = 3.70

    plot_left = plot_left_in / fig_w
    plot_width = plot_width_in / fig_w
    plot_bottom = plot_bottom_in / fig_h
    plot_height = plot_height_in / fig_h

    ax = fig.add_axes([plot_left, plot_bottom, plot_width, plot_height])
    ax.patch.set_alpha(0.0)  # Transparent background

    # Data Rows with genuine mathematical double-prime symbols
    mint_color = "#34d399"
    rows = [
        {
            "y": 4,
            "label": "Newtonian / Einstein 1911",
            "val": 0.87,
            "err": None,
            "val_str": r"0.87$^{\prime\prime}$",
            "color": "#f59e0b",  # Warm Amber
            "marker": "D",
            "type": "pred"
        },
        {
            "y": 3,
            "label": "General relativity",
            "val": 1.75,
            "err": None,
            "val_str": r"1.75$^{\prime\prime}$",
            "color": "#38bdf8",  # Sky Blue / Cyan
            "marker": "D",
            "type": "pred"
        },
        {
            "y": 2,
            "label": "Wallal 1923 (15-foot cameras)",
            "val": 1.72,
            "err": 0.11,
            "val_str": r"1.72$^{\prime\prime} \pm 0.11^{\prime\prime}$",
            "color": mint_color,  # Vibrant Mint
            "marker": "o",
            "type": "meas"
        },
        {
            "y": 1,
            "label": "Wallal final result (1928)",
            "val": 1.75,
            "err": 0.09,
            "val_str": r"1.75$^{\prime\prime} \pm 0.09^{\prime\prime}$",
            "color": mint_color,  # Same Mint family
            "marker": "o",
            "type": "meas"
        }
    ]

    x_min, x_max = 0.60, 2.05
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0.4, 4.6)

    # Vertical reference lines
    # 0.87″ Newtonian reference (moderate dashed line)
    ax.axvline(0.87, color='#f59e0b', linestyle='--', linewidth=1.4, alpha=0.45, zorder=2)
    # 1.75″ General Relativity reference (bold, prominent sky blue line)
    ax.axvline(1.75, color='#38bdf8', linestyle='--', linewidth=2.4, alpha=0.88, zorder=2)

    # Horizontal guide lines for each row
    for r in rows:
        y = r["y"]
        ax.axhline(y, color='#1e293b', linestyle='-', linewidth=1.2, zorder=1)

        if r["type"] == "pred":
            ax.plot(
                r["val"], y, marker=r["marker"], markersize=9.5,
                color=r["color"], markeredgecolor='#ffffff', markeredgewidth=1.3,
                zorder=4
            )
        else:
            ax.errorbar(
                r["val"], y, xerr=r["err"], fmt='o',
                color=r["color"], ecolor=r["color"],
                elinewidth=2.8, capsize=6.0, capthick=2.2,
                markersize=9.0, markeredgecolor='#ffffff', markeredgewidth=1.4,
                zorder=5
            )

    # Configure axes spines and ticks
    for spine in ['top', 'left', 'right']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#475569')
    ax.spines['bottom'].set_linewidth(1.4)

    ticks = [0.75, 1.00, 1.25, 1.50, 1.75, 2.00]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:.2f}" + r"$^{\prime\prime}$" for t in ticks],
                       color='#e2e8f0', fontsize=12.5, fontweight='bold')
    ax.tick_params(axis='x', colors='#64748b', length=6, width=1.3)
    ax.set_yticks([])

    # X-axis label - Slightly reduced size (15.0pt bold)
    ax.set_xlabel(
        "Deflection at the solar limb (arcseconds)",
        color='#94a3b8', fontsize=15.0, fontweight='bold', labelpad=12
    )

    # Draw left labels and right values
    col_label_x = 0.38  # Left column start in figure inches
    col_val_x = 6.82    # Right values start in figure inches

    for r in rows:
        disp_y = ax.transData.transform((0, r["y"]))
        fig_y = fig.transFigure.inverted().transform(disp_y)[1] * fig_h

        # Left label: left-aligned
        ax_card.text(
            col_label_x, fig_y, r["label"],
            color='#f8fafc', fontsize=11.8, fontweight='bold',
            ha='left', va='center', zorder=5
        )

        # Right value: left-aligned
        ax_card.text(
            col_val_x, fig_y, r["val_str"],
            color=r["color"], fontsize=12.5, fontweight='bold',
            ha='left', va='center', zorder=5
        )

    # =========================================================================
    # SECONDARY 1919 CONTEXT INSET (MOVED HIGHER, TIGHTER GAPS)
    # =========================================================================
    # Positioned higher up: y from 2.50 to 4.88 in
    inset_x = 8.35
    inset_w = 2.25
    inset_h = 2.38
    inset_y = 2.50

    # Inset background card
    inset_box = FancyBboxPatch(
        (inset_x, inset_y), inset_w, inset_h,
        boxstyle="round,pad=0.04,rounding_size=0.15",
        facecolor='#131d31', edgecolor='#334155', linewidth=1.3, zorder=2
    )
    ax_card.add_patch(inset_box)

    # Inset Title Header Banner
    inset_hdr_h = 0.54
    inset_hdr_y = inset_y + inset_h - inset_hdr_h
    inset_hdr = FancyBboxPatch(
        (inset_x, inset_hdr_y), inset_w, inset_hdr_h,
        boxstyle="round,pad=0.04,rounding_size=0.15",
        facecolor='#1e293b', edgecolor='#475569', linewidth=1.1, zorder=3
    )
    ax_card.add_patch(inset_hdr)

    ax_card.text(
        inset_x + inset_w / 2.0, inset_hdr_y + inset_hdr_h / 2.0,
        "1919 ECLIPSE RESULTS",
        color='#7dd3fc', fontsize=10.6, fontweight='bold', ha='center', va='center', zorder=4
    )

    # Inset Entries (Tighter vertical gap between Príncipe and Sobral)
    # Entry 1: Príncipe
    e1_y = inset_hdr_y - 0.36
    ax_card.text(
        inset_x + 0.16, e1_y, "Príncipe",
        color='#94a3b8', fontsize=12.0, fontweight='bold', ha='left', va='center', zorder=4
    )
    ax_card.text(
        inset_x + 0.16, e1_y - 0.30, r"1.61$^{\prime\prime} \pm 0.30^{\prime\prime}$",
        color='#e2e8f0', fontsize=12.5, fontweight='bold', ha='left', va='center', zorder=4
    )

    # Divider line (narrower spacing)
    div_y = e1_y - 0.50
    div_line = Rectangle(
        (inset_x + 0.16, div_y), inset_w - 0.32, 0.015,
        facecolor='#1e293b', edgecolor='none', zorder=3
    )
    ax_card.add_patch(div_line)

    # Entry 2: Sobral (4-inch)
    e2_y = div_y - 0.30
    ax_card.text(
        inset_x + 0.16, e2_y, "Sobral (4-inch)",
        color='#94a3b8', fontsize=12.0, fontweight='bold', ha='left', va='center', zorder=4
    )
    ax_card.text(
        inset_x + 0.16, e2_y - 0.30, r"1.98$^{\prime\prime} \pm 0.12^{\prime\prime}$",
        color='#e2e8f0', fontsize=12.5, fontweight='bold', ha='left', va='center', zorder=4
    )

    # Save 2x high-resolution version
    plt.savefig(out_2x, dpi=dpi, facecolor=bg_color, edgecolor='none')
    plt.close(fig)

    # Downscale cleanly to 680px width using LANCZOS
    with Image.open(out_2x) as im:
        w_orig, h_orig = im.size
        target_w = 680
        target_h = int(round(h_orig * (target_w / w_orig)))
        im_resized = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
        im_resized.save(out_1x, quality=95, optimize=True)

    print(f"[OK] Generated {out_1x} ({target_w}x{target_h}) & {out_2x} ({w_orig}x{h_orig})")

if __name__ == "__main__":
    create_results_plot()
