#!/usr/bin/env python3
r"""
Generate 1800 x 800 px panoramic introductory illustration:
"Cosmic Microwave Background -> Cosmic Web"

Design & Scientific Specifications:
- Canvas: 1800 x 800 px (panoramic 9:4 aspect ratio: 12.85714 x 5.71429 in at 140 DPI).
- No top title or subtitle (avoiding repetition of the article's title and opening paragraph).
- Pure black background (#000000) unifying both scientific visuals.
- Three horizontal zones:
  1. Left panel (~44.5% width): Full-sky Planck 2018 CMB map (`planck_cmb_2018_clean.jpg`),
     preserving its exact elliptical Mollweide projection aspect ratio without stretching.
  2. Central transition zone: Clean, shorter white horizontal right-pointing arrow
     centred between the images, with "Cosmic evolution" in a smaller font above it.
  3. Right panel (~43.5% width): Official NASA SVS 10118 cosmic-web visualization
     (`nasa_svs_10118_cosmic_web.jpg`, `CosmicWeb0013.jpg`), preserving its native 16:9
     aspect ratio without stretching and without a border frame.
- Bottom labels positioned immediately below the vertically centred images:
  - Left: "Cosmic Microwave Background" (15.5 pt bold) / "380,000 years after the Big Bang" (13.8 pt bold)
  - Right: "Cosmic Web" (15.5 pt bold) / "Today" (13.8 pt bold)
"""

from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
CMB_SOURCE = SCRIPT_DIR.parent / "images" / "planck_cmb_2018_clean.jpg"
WEB_SOURCE = SCRIPT_DIR.parent / "images" / "nasa_svs_10118_cosmic_web.jpg"
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "cmb_to_cosmic_web.png"


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure typography to match dark_energy_structure_growth.png & matter_transfer_function_power_spectrum.png
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    # Exact 1800 x 704 px canvas at 140 DPI (preserving exact top/bottom margins with larger panels)
    dpi = 140
    fig_w = 1800.0 / dpi
    fig_h = 704.0 / dpi
    canvas_aspect = fig_w / fig_h

    BG_COLOR = '#000000'
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor=BG_COLOR)

    ax_bg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=0)
    ax_bg.set_xlim(0.0, 1.0)
    ax_bg.set_ylim(0.0, 1.0)
    ax_bg.set_facecolor(BG_COLOR)
    ax_bg.axis('off')

    # Load Planck 2018 CMB map (1600 x 808)
    cmb_img = Image.open(CMB_SOURCE).convert('RGB')
    cmb_arr = np.asarray(cmb_img)
    cmb_h, cmb_w, _ = cmb_arr.shape
    cmb_aspect = cmb_w / cmb_h  # 1.9802

    # Load official NASA SVS 10118 Cosmic Web visualization (CosmicWeb0013.jpg, 1280 x 720)
    web_img = Image.open(WEB_SOURCE).convert('RGB')
    web_arr = np.asarray(web_img)
    web_h, web_w, _ = web_arr.shape
    web_aspect = web_w / web_h  # 1.7778 (native 16:9)

    # -------------------------------------------------------------------------
    # Layout Geometry: Central gap reduced by ~half (0.094 -> 0.046) to reuse space
    # for both scientific images while preserving native aspect ratios
    # -------------------------------------------------------------------------
    left_x = 0.018
    cmb_panel_w = 0.464
    cmb_panel_h = cmb_panel_w * canvas_aspect / cmb_aspect  # ~ 0.599 of canvas height

    web_panel_w = 0.454
    right_x = 1.0 - 0.018 - web_panel_w  # 0.528 (leaving a 0.046 central gap, ~half of 0.094)
    web_panel_h = web_panel_w * canvas_aspect / web_aspect  # ~ 0.653 of canvas height

    # Vertically centre both scientific images preserving the top & bottom margins
    y_center = 0.558
    cmb_bottom = y_center - 0.5 * cmb_panel_h
    web_bottom = y_center - 0.5 * web_panel_h

    # Left Panel: Planck CMB full-sky map
    ax_cmb = fig.add_axes([left_x, cmb_bottom, cmb_panel_w, cmb_panel_h], zorder=2)
    ax_cmb.imshow(cmb_arr, interpolation='lanczos', aspect='equal')
    ax_cmb.axis('off')

    # Right Panel: NASA SVS 10118 Cosmic Web visualization (no border frame)
    ax_web = fig.add_axes([right_x, web_bottom, web_panel_w, web_panel_h], zorder=2)
    ax_web.imshow(web_arr, interpolation='lanczos', aspect='equal')
    ax_web.axis('off')

    # Foreground overlay axis for crisp text annotations
    ax_fg = fig.add_axes([0.0, 0.0, 1.0, 1.0], facecolor='none', zorder=10)
    ax_fg.patch.set_alpha(0.0)
    ax_fg.set_xlim(0.0, 1.0)
    ax_fg.set_ylim(0.0, 1.0)
    ax_fg.axis('off')

    # -------------------------------------------------------------------------
    # Bottom Labels Immediately Below the Images
    # -------------------------------------------------------------------------
    left_cx = left_x + 0.5 * cmb_panel_w
    right_cx = right_x + 0.5 * web_panel_w

    y_label_primary = 0.158
    y_label_secondary = 0.077

    # Left panel labels
    ax_fg.text(
        left_cx, y_label_primary,
        "Cosmic Microwave Background",
        color='#f8fafc',
        fontsize=16.5,
        fontweight='bold',
        ha='center',
        va='center',
        zorder=10,
    )
    ax_fg.text(
        left_cx, y_label_secondary,
        "380,000 years after the Big Bang",
        color='#cbd5e1',
        fontsize=15.0,
        fontweight='bold',
        ha='center',
        va='center',
        zorder=10,
    )

    # Right panel labels
    ax_fg.text(
        right_cx, y_label_primary,
        "Cosmic Web",
        color='#f8fafc',
        fontsize=16.5,
        fontweight='bold',
        ha='center',
        va='center',
        zorder=10,
    )
    ax_fg.text(
        right_cx, y_label_secondary,
        "Today",
        color='#cbd5e1',
        fontsize=15.0,
        fontweight='bold',
        ha='center',
        va='center',
        zorder=10,
    )

    # -------------------------------------------------------------------------
    # Discreet Scientific Annotation Above the Planck CMB Map
    # -------------------------------------------------------------------------
    ax_fg.text(
        left_cx, 0.942,
        "Nearly uniform temperature",
        color='#f8fafc',
        fontsize=13.0,
        fontweight='bold',
        ha='center',
        va='center',
        zorder=10,
    )
    ax_fg.text(
        left_cx, 0.892,
        "Variations \u2248 1 part in 100,000",
        color='#94a3b8',
        fontsize=11.8,
        fontweight='normal',
        ha='center',
        va='center',
        zorder=10,
    )

    # Save output image
    fig.savefig(output_path, dpi=dpi, facecolor=BG_COLOR)
    plt.close(fig)

    print(f"[OK] Generated {output_path}")


if __name__ == "__main__":
    create_figure()
