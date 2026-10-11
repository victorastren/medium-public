#!/usr/bin/env python3
r"""
Create schematic for Medium:
"Measuring the Deflection from Photographic Plates (1922)"

Accompanies the section "From Photographic Plates to the Deflection Measurement".
Aesthetic & Design:
- Cosmic dark slate (#0b0f19) matching all other article scientific figures.
- Deep navy/slate panels (#0f172a, #1e293b) with vibrant cyan (#38bdf8), mint (#34d399), and amber (#fbbf24) accents.
- Large, bold typography engineered for Medium 680px width and mobile screens.
- Two-part comprehensive layout:
  1. Intermediate-Plate Comparison Method:
     - Three 17-inch photographic plates (Wallal eclipse, reversed intermediate, Tahiti comparison)
     - Magnified microscope reticle views showing emulsion-to-emulsion contact
     - Differential subtraction canceling the intermediate plate
  2. Plate Reduction & 2° Boundary:
     - 17" plate field with eclipsed Sun at center
     - 2° reference boundary (dashed ring)
     - Inner stars with exaggerated radial outward deflection arrows (δθ ∝ 1/ρ)
     - Outer reference stars used for plate scale and orientation
"""

import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['mathtext.fontset'] = 'dejavusans'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
OUT_IMG = PROJECT_DIR / "images" / "wallal_plate_measurement_method.png"
OUT_IMG_2X = PROJECT_DIR / "images" / "wallal_plate_measurement_method_2x.png"

W, H = 2040, 1420

# Palette
BG_COLOR = (11, 15, 25, 255)         # #0b0f19 Cosmic dark slate
CARD_BG = (15, 23, 42, 255)          # #0f172a Deep navy card fill
CARD_BORDER = (51, 65, 85, 255)      # #334155 Slate card border
CARD_HEADER_BG = (30, 41, 59, 255)   # #1e293b
CARD_HEADER_BORDER = (71, 85, 105, 255)

# Accents
CYAN_BRIGHT = (56, 189, 248, 255)    # #38bdf8 Sky Blue (Tahiti comparison)
CYAN_SOFT = (125, 211, 252, 255)     # #7dd3fc
CYAN_DARK = (3, 105, 161, 255)       # #0369a1
CYAN_BORDER = (2, 132, 199, 255)

MINT_BRIGHT = (52, 211, 153, 255)    # #34d399 Vibrant Mint (Wallal eclipse)
MINT_SOFT = (110, 231, 183, 255)     # #6ee7b7
MINT_DARK = (6, 95, 70, 255)         # #065f46
MINT_BORDER = (5, 150, 105, 255)

AMBER_BRIGHT = (251, 191, 36, 255)   # #fbbf24 Warm yellow/gold (Intermediate plate)
AMBER_WARM = (245, 158, 11, 255)     # #f59e0b
AMBER_DARK = (120, 53, 15, 255)      # #78350f
AMBER_BORDER = (217, 119, 6, 255)

INDIGO_ACCENT = (165, 180, 252, 255) # #a5b4fc
INDIGO_BORDER = (99, 102, 241, 255)  # #6366f1

TEXT_WHITE = (255, 255, 255, 255)
TEXT_MUTED = (203, 213, 225, 255)
TEXT_FAINT = (148, 163, 184, 255)
BORDER_SUBTLE = (51, 65, 85, 255)

def get_font(size, bold=False, italic=False):
    """Load DejaVuSans font with full Unicode and math symbol support."""
    if bold:
        paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
    elif italic:
        paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"]
    else:
        paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def draw_arrow(draw, x1, y1, x2, y2, color, width=3, arrow_size=12):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dy, dx)
    angle1 = angle + math.radians(150)
    angle2 = angle - math.radians(150)
    ax1 = x2 + arrow_size * math.cos(angle1)
    ay1 = y2 + arrow_size * math.sin(angle1)
    ax2 = x2 + arrow_size * math.cos(angle2)
    ay2 = y2 + arrow_size * math.sin(angle2)
    draw.polygon([(x2, y2), (ax1, ay1), (ax2, ay2)], fill=color)

def draw_dashed_circle(draw, cx, cy, r, color, width=2, n_dash=52):
    for i in range(n_dash):
        if i % 2 == 0:
            a1 = 2 * math.pi * i / n_dash
            a2 = 2 * math.pi * (i + 1) / n_dash
            arc_pts = []
            for step in range(5):
                cur_a = a1 + (a2 - a1) * (step / 4.0)
                arc_pts.append((cx + r * math.cos(cur_a), cy + r * math.sin(cur_a)))
            draw.line(arc_pts, fill=color, width=width)

MINT_TEXT_BRIGHT = (165, 255, 220, 255) # High-luminosity mint for maximum legibility
CYAN_TEXT_BRIGHT = (180, 240, 255, 255) # High-luminosity cyan for maximum legibility

def draw_text_centered(draw, cx, cy, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    x = cx - (bbox[0] + bbox[2]) / 2.0
    y = cy - (bbox[1] + bbox[3]) / 2.0
    draw.text((x, y), text, font=font, fill=fill)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def render_math_latex(formula, fontsize=22, color='white', bold=True, supersample=2):
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0)
    fig.text(0, 0, formula, fontsize=fontsize, color=color, weight='bold' if bold else 'normal')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=72 * supersample, transparent=True, bbox_inches='tight', pad_inches=0.01)
    plt.close(fig)
    buf.seek(0)
    im = Image.open(buf)
    if supersample > 1:
        target_w = max(1, int(round(im.width / supersample)))
        target_h = max(1, int(round(im.height / supersample)))
        im = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
    return im

def paste_math_centered(img, cx, cy, formula, fontsize=22, color='white', bold=True, supersample=2):
    math_img = render_math_latex(formula, fontsize=fontsize, color=color, bold=bold, supersample=supersample)
    x = int(round(cx - math_img.width / 2.0))
    y = int(round(cy - math_img.height / 2.0))
    img.paste(math_img, (x, y), math_img)
    return math_img.width, math_img.height

def generate_schematic(output_path=None, output_path_2x=None):
    if output_path is None:
        output_path = OUT_IMG
    if output_path_2x is None:
        output_path_2x = OUT_IMG_2X
    output_path = Path(output_path)
    output_path_2x = Path(output_path_2x)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path_2x.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Ambient subtle starfield outside cards (strictly outside the panel bounds)
    np.random.seed(101)
    for _ in range(160):
        sx = int(np.random.uniform(10, W - 10))
        sy = int(np.random.uniform(10, H - 10))
        if (30 < sx < 2010 and 140 < sy < 1405):
            continue
        sr = float(np.random.uniform(1, 2.5))
        sa = int(np.random.uniform(40, 160))
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255, sa))

    # --- Typography Definitions (Scaled Up for Medium Readability) ---
    font_main_title = get_font(40, bold=True)
    font_subtitle = get_font(24, bold=False)
    font_panel_title = get_font(30, bold=True)
    font_panel_sub = get_font(24, bold=False)
    
    font_card_title = get_font(24, bold=True)
    font_card_sub = get_font(22, bold=False)
    font_plate_tag = get_font(21, bold=True)
    
    font_ret_header = get_font(23, bold=True)
    font_star_label = get_font(18, bold=True)
    font_bracket = get_font(23, bold=True)
    font_eyepiece_cap = get_font(21, bold=True)
    
    font_micro_title = get_font(25, bold=True)
    font_micro_main = get_font(25, bold=True)
    font_micro_body = get_font(24, bold=False)
    font_micro_bold = get_font(24, bold=True)

    font_math = get_font(23, bold=True)
    font_sub_title = get_font(24, bold=True)
    font_sub_bullet = get_font(23, bold=False)

    font_call_title = get_font(23, bold=True)
    font_call_b1 = get_font(20, bold=True)
    font_call_b2 = get_font(23, bold=True)

    font_proc_title = get_font(28, bold=True)
    font_step_title = get_font(26, bold=True)
    font_step_desc = get_font(23, bold=False)

    # =========================================================================
    # 1. HEADER BANNER (y: 25 to 135)
    # =========================================================================
    hdr_x1, hdr_y1, hdr_x2, hdr_y2 = 40, 25, 2000, 135
    draw.rounded_rectangle([hdr_x1, hdr_y1, hdr_x2, hdr_y2], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    
    title_text = "MEASURING THE DEFLECTION FROM PHOTOGRAPHIC PLATES"
    sub_text = "The Intermediate Plate Technique & Outer Reference System · Wallal Expedition (1922)"
    draw.text((hdr_x1 + 35, hdr_y1 + 22), title_text, font=font_main_title, fill=TEXT_WHITE)
    draw.text((hdr_x1 + 35, hdr_y1 + 72), sub_text, font=font_subtitle, fill=CYAN_SOFT)

    # Top right specification badge
    badge_w = 280
    badge_x = hdr_x2 - badge_w - 30
    badge_y = hdr_y1 + 28
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + 54], radius=8, fill=CARD_HEADER_BG, outline=BORDER_SUBTLE, width=1)
    draw_text_centered(draw, badge_x + badge_w // 2, badge_y + 27, "Plate Scale: ≈ 45″/mm", font=get_font(23, bold=True), fill=AMBER_BRIGHT)

    # =========================================================================
    # 2. LEFT PANEL: THE INTERMEDIATE-PLATE COMPARISON METHOD
    # =========================================================================
    p1_x1, p1_y1, p1_x2, p1_y2 = 40, 155, 1225, 1390
    draw.rounded_rectangle([p1_x1, p1_y1, p1_x2, p1_y2], radius=14, fill=CARD_BG, outline=BORDER_SUBTLE, width=2)

    # Panel 1 Header Bar
    hdr_h = 86
    draw.rounded_rectangle([p1_x1, p1_y1, p1_x2, p1_y1 + hdr_h], radius=14, fill=CARD_HEADER_BG, outline=BORDER_SUBTLE, width=1)
    draw.rectangle([p1_x1, p1_y1 + 60, p1_x2, p1_y1 + hdr_h], fill=CARD_HEADER_BG)
    draw.line([(p1_x1, p1_y1 + hdr_h), (p1_x2, p1_y1 + hdr_h)], fill=BORDER_SUBTLE, width=1)
    draw.text((p1_x1 + 25, p1_y1 + 14), "1. THE INTERMEDIATE-PLATE COMPARISON METHOD", font=font_panel_title, fill=MINT_BRIGHT)
    draw.text((p1_x1 + 25, p1_y1 + 50), "Differential comparison of eclipse and reference plates", font=font_panel_sub, fill=TEXT_MUTED)

    # --- ROW 1: THE THREE PLATES (y: 265 to 550) ---
    plate_w = 345
    plate_h = 285
    y_pl = 265

    # Star field coordinates relative to center
    e_stars = [(-90, -40), (-60, 50), (70, -35), (85, 45), (-35, -70), (40, 70), (-110, 20), (105, -15)]

    # Plate 1: Wallal Eclipse Plate
    pl1_x = p1_x1 + 30
    draw.rounded_rectangle([pl1_x, y_pl, pl1_x + plate_w, y_pl + plate_h], radius=10, fill=(13, 23, 38, 255), outline=MINT_BORDER, width=2)
    draw.rounded_rectangle([pl1_x, y_pl, pl1_x + plate_w, y_pl + 44], radius=10, fill=MINT_DARK, outline=MINT_BORDER, width=1)
    draw.rectangle([pl1_x, y_pl + 30, pl1_x + plate_w, y_pl + 44], fill=MINT_DARK)
    draw.text((pl1_x + 18, y_pl + 11), "Wallal Eclipse Plate", font=font_card_title, fill=MINT_SOFT)

    # Plate 1 contents: Eclipsed Sun + Stars
    pl1_cx = pl1_x + plate_w // 2
    pl1_cy = y_pl + 142
    for cr in range(36, 12, -4):
        draw.ellipse([pl1_cx - cr, pl1_cy - cr, pl1_cx + cr, pl1_cy + cr], fill=(255, 240, 200, 25))
    draw.ellipse([pl1_cx - 15, pl1_cy - 15, pl1_cx + 15, pl1_cy + 15], fill=(8, 12, 18, 255), outline=(255, 230, 160, 255), width=2)
    for dx, dy in e_stars:
        draw.ellipse([pl1_cx + dx - 3, pl1_cy + dy - 3, pl1_cx + dx + 3, pl1_cy + dy + 3], fill=MINT_BRIGHT)
    
    draw_text_centered(draw, pl1_cx, y_pl + plate_h - 26, "Direct exposure during eclipse", font=font_card_sub, fill=TEXT_MUTED)

    # Plate 2: Intermediate Plate (Tahiti)
    pl2_x = pl1_x + plate_w + 35
    draw.rounded_rectangle([pl2_x, y_pl, pl2_x + plate_w, y_pl + plate_h], radius=10, fill=(35, 24, 15, 255), outline=AMBER_BORDER, width=2)
    draw.rounded_rectangle([pl2_x, y_pl, pl2_x + plate_w, y_pl + 44], radius=10, fill=AMBER_DARK, outline=AMBER_BORDER, width=1)
    draw.rectangle([pl2_x, y_pl + 30, pl2_x + plate_w, y_pl + 44], fill=AMBER_DARK)
    draw.text((pl2_x + 18, y_pl + 11), "Intermediate Plate", font=font_card_title, fill=AMBER_BRIGHT)

    # Plate 2 contents: Mirrored stars (dashed rings)
    pl2_cx = pl2_x + plate_w // 2
    pl2_cy = y_pl + 142
    for dx, dy in e_stars:
        mdx = -dx
        draw.ellipse([pl2_cx + mdx - 4, pl2_cy + dy - 4, pl2_cx + mdx + 4, pl2_cy + dy + 4], fill=(50, 30, 10, 255), outline=AMBER_BRIGHT, width=2)
    
    # "Reversed" Badge in top-left corner so all stars inside remain visible
    b_x = pl2_x + 14
    b_y = y_pl + 54
    b_w_tag = 130
    b_h_tag = 36
    draw.rounded_rectangle([b_x, b_y, b_x + b_w_tag, b_y + b_h_tag], radius=6, fill=(60, 35, 12, 240), outline=AMBER_WARM, width=2)
    draw_text_centered(draw, b_x + b_w_tag // 2, b_y + b_h_tag // 2, "Reversed", font=font_plate_tag, fill=AMBER_BRIGHT)

    draw_text_centered(draw, pl2_cx, y_pl + plate_h - 26, "Exposed through glass (Tahiti)", font=font_card_sub, fill=AMBER_BRIGHT)

    # Plate 3: Tahiti Comparison Plate
    pl3_x = pl2_x + plate_w + 35
    draw.rounded_rectangle([pl3_x, y_pl, pl3_x + plate_w, y_pl + plate_h], radius=10, fill=(12, 25, 42, 255), outline=CYAN_BORDER, width=2)
    draw.rounded_rectangle([pl3_x, y_pl, pl3_x + plate_w, y_pl + 44], radius=10, fill=CYAN_DARK, outline=CYAN_BORDER, width=1)
    draw.rectangle([pl3_x, y_pl + 30, pl3_x + plate_w, y_pl + 44], fill=CYAN_DARK)
    draw.text((pl3_x + 18, y_pl + 11), "Tahiti Comparison Plate", font=font_card_title, fill=CYAN_SOFT)

    # Plate 3 contents: Night stars (direct, undeflected)
    pl3_cx = pl3_x + plate_w // 2
    pl3_cy = y_pl + 142
    for dx, dy in e_stars:
        draw.ellipse([pl3_cx + dx - 3, pl3_cy + dy - 3, pl3_cx + dx + 3, pl3_cy + dy + 3], fill=CYAN_BRIGHT)
    draw_text_centered(draw, pl3_cx, pl3_cy, "(Night Reference Field)", font=font_plate_tag, fill=CYAN_SOFT)

    draw_text_centered(draw, pl3_cx, y_pl + plate_h - 26, "Direct night exposure (Tahiti)", font=font_card_sub, fill=TEXT_MUTED)

    # Emulsion Contact Arrows
    draw_arrow(draw, pl1_x + plate_w + 4, y_pl + 142, pl2_x - 4, y_pl + 142, MINT_BRIGHT, width=3, arrow_size=10)
    draw_arrow(draw, pl3_x - 4, y_pl + 142, pl2_x + plate_w + 4, y_pl + 142, CYAN_BRIGHT, width=3, arrow_size=10)

    # --- ROW 2: MICROSCOPE RETICLE INSETS (y: 570 to 1010) ---
    y_ret = 570
    draw.rounded_rectangle([p1_x1 + 25, y_ret, p1_x2 - 25, y_ret + 440], radius=12, fill=(10, 16, 28, 255), outline=CARD_BORDER, width=1)
    
    ret_title = "HIGH-MAGNIFICATION MICROMETER INSET (EMULSION-TO-EMULSION CONTACT)"
    draw.text((p1_x1 + 35, y_ret + 18), ret_title, font=font_ret_header, fill=TEXT_WHITE)
    draw.line([(p1_x1 + 35, y_ret + 50), (p1_x2 - 35, y_ret + 50)], fill=BORDER_SUBTLE, width=1)

    # Microscope Eyepiece 1: Wallal on Intermediate
    ep1_cx = 246
    ep1_cy = y_ret + 235
    ep_r = 130

    draw.ellipse([ep1_cx - ep_r - 8, ep1_cy - ep_r - 8, ep1_cx + ep_r + 8, ep1_cy + ep_r + 8], fill=(30, 41, 59, 255), outline=(71, 85, 105, 255), width=2)
    draw.ellipse([ep1_cx - ep_r, ep1_cy - ep_r, ep1_cx + ep_r, ep1_cy + ep_r], fill=(6, 11, 20, 255), outline=MINT_BORDER, width=3)
    # Reticle crosshairs
    draw.line([(ep1_cx - ep_r, ep1_cy), (ep1_cx + ep_r, ep1_cy)], fill=(51, 65, 85, 180), width=1)
    draw.line([(ep1_cx, ep1_cy - ep_r), (ep1_cx, ep1_cy + ep_r)], fill=(51, 65, 85, 180), width=1)

    # Stars in Eyepiece 1:
    s1_x, s1_y = ep1_cx - 65, ep1_cy
    s2_x, s2_y = ep1_cx + 65, ep1_cy

    # Wallal Star (Mint)
    draw.ellipse([s1_x - 10, s1_y - 10, s1_x + 10, s1_y + 10], fill=MINT_BRIGHT, outline=TEXT_WHITE, width=2)
    draw_text_centered(draw, s1_x, s1_y - 48, "Wallal Star", font=font_star_label, fill=MINT_BRIGHT)
    draw.line([(s1_x, s1_y - 30), (s1_x, s1_y - 14)], fill=MINT_BRIGHT, width=1)

    # Intermediate Star (Amber) - staggered higher to prevent text overlap
    draw.ellipse([s2_x - 11, s2_y - 11, s2_x + 11, s2_y + 11], fill=(45, 25, 10, 255), outline=AMBER_BRIGHT, width=3)
    draw_text_centered(draw, s2_x, s2_y - 70, "Intermediate", font=font_star_label, fill=AMBER_BRIGHT)
    draw.line([(s2_x, s2_y - 52), (s2_x, s2_y - 15)], fill=AMBER_BRIGHT, width=1)

    # Micrometer dimension bracket below stars
    brk_y = s1_y + 36
    draw.line([(s1_x, brk_y), (s2_x, brk_y)], fill=TEXT_WHITE, width=2)
    draw.line([(s1_x, brk_y - 8), (s1_x, brk_y + 8)], fill=TEXT_WHITE, width=2)
    draw.line([(s2_x, brk_y - 8), (s2_x, brk_y + 8)], fill=TEXT_WHITE, width=2)
    paste_math_centered(img, ep1_cx, brk_y + 24, r'$\mathbf{d_1 = x_E - x_I}$', fontsize=22, color='white', bold=True)

    # Eyepiece 1 caption below circle
    draw_text_centered(draw, ep1_cx, ep1_cy + ep_r + 28, "Pair A: Wallal on Intermediate (d₁)", font=font_eyepiece_cap, fill=MINT_SOFT)

    # Microscope Eyepiece 2: Tahiti on Intermediate
    ep2_cx = 998
    ep2_cy = y_ret + 235

    draw.ellipse([ep2_cx - ep_r - 8, ep2_cy - ep_r - 8, ep2_cx + ep_r + 8, ep2_cy + ep_r + 8], fill=(30, 41, 59, 255), outline=(71, 85, 105, 255), width=2)
    draw.ellipse([ep2_cx - ep_r, ep2_cy - ep_r, ep2_cx + ep_r, ep2_cy + ep_r], fill=(6, 11, 20, 255), outline=CYAN_BORDER, width=3)
    draw.line([(ep2_cx - ep_r, ep2_cy), (ep2_cx + ep_r, ep2_cy)], fill=(51, 65, 85, 180), width=1)
    draw.line([(ep2_cx, ep2_cy - ep_r), (ep2_cx, ep2_cy + ep_r)], fill=(51, 65, 85, 180), width=1)

    # Stars in Eyepiece 2:
    s3_x, s3_y = ep2_cx - 65, ep2_cy
    s4_x, s4_y = ep2_cx + 65, ep2_cy

    # Tahiti Star (Cyan)
    draw.ellipse([s3_x - 10, s3_y - 10, s3_x + 10, s3_y + 10], fill=CYAN_BRIGHT, outline=TEXT_WHITE, width=2)
    draw_text_centered(draw, s3_x, s3_y - 48, "Tahiti Star", font=font_star_label, fill=CYAN_BRIGHT)
    draw.line([(s3_x, s3_y - 30), (s3_x, s3_y - 14)], fill=CYAN_BRIGHT, width=1)

    # Intermediate Star (Amber) - staggered higher to prevent text overlap
    draw.ellipse([s4_x - 11, s4_y - 11, s4_x + 11, s4_y + 11], fill=(45, 25, 10, 255), outline=AMBER_BRIGHT, width=3)
    draw_text_centered(draw, s4_x, s4_y - 70, "Intermediate", font=font_star_label, fill=AMBER_BRIGHT)
    draw.line([(s4_x, s4_y - 52), (s4_x, s4_y - 15)], fill=AMBER_BRIGHT, width=1)

    # Micrometer dimension bracket below stars
    draw.line([(s3_x, brk_y), (s4_x, brk_y)], fill=TEXT_WHITE, width=2)
    draw.line([(s3_x, brk_y - 8), (s3_x, brk_y + 8)], fill=TEXT_WHITE, width=2)
    draw.line([(s4_x, brk_y - 8), (s4_x, brk_y + 8)], fill=TEXT_WHITE, width=2)
    paste_math_centered(img, ep2_cx, brk_y + 24, r'$\mathbf{d_2 = x_C - x_I}$', fontsize=22, color='white', bold=True)

    # Eyepiece 2 caption below circle
    draw_text_centered(draw, ep2_cx, ep2_cy + ep_r + 28, "Pair B: Tahiti on Intermediate (d₂)", font=font_eyepiece_cap, fill=CYAN_SOFT)

    # Central Technical Instrument Card: MEASURING MICROSCOPE (Clean, High-Contrast Typography)
    b_cx = pl2_cx
    b_cy = y_ret + 235
    b_w = 440
    b_h = 250
    draw.rounded_rectangle([b_cx - b_w//2, b_cy - b_h//2, b_cx + b_w//2, b_cy + b_h//2], radius=10, fill=(18, 28, 48, 255), outline=BORDER_SUBTLE, width=2)
    draw_text_centered(draw, b_cx, b_cy - 88, "MEASURING MICROSCOPE", font=font_micro_title, fill=AMBER_BRIGHT)
    draw.line([(b_cx - 165, b_cy - 66), (b_cx + 165, b_cy - 66)], fill=BORDER_SUBTLE, width=2)
    
    # Point 1 (Emulsions in direct contact)
    draw_text_centered(draw, b_cx, b_cy - 36, "Emulsions in direct contact", font=font_micro_main, fill=TEXT_WHITE)
    
    # Point 2 (Both stellar images viewed together)
    draw_text_centered(draw, b_cx, b_cy + 5, "Both stellar images", font=font_micro_body, fill=TEXT_MUTED)
    draw_text_centered(draw, b_cx, b_cy + 35, "viewed together", font=font_micro_body, fill=TEXT_MUTED)
    
    # Point 3 (Micrometer measures their separation)
    draw_text_centered(draw, b_cx, b_cy + 78, "Micrometer measures", font=font_micro_bold, fill=MINT_BRIGHT)
    draw_text_centered(draw, b_cx, b_cy + 108, "their separation", font=font_micro_bold, fill=MINT_BRIGHT)

    # --- ROW 3: SUBTRACTION RESULT BANNER (y: 1030 to 1365) ---
    res_y = 1030
    draw.rounded_rectangle([p1_x1 + 25, res_y, p1_x2 - 25, res_y + 335], radius=12, fill=(16, 28, 48, 255), outline=CYAN_BORDER, width=2)
    
    draw.text((p1_x1 + 45, res_y + 20), "FINAL STEP: SUBTRACTING THE TWO MEASUREMENTS", font=font_sub_title, fill=CYAN_BRIGHT)
    
    # Formula box
    f_box_x1 = p1_x1 + 32
    f_box_y1 = res_y + 58
    f_box_w = (p1_x2 - p1_x1) - 64
    draw.rounded_rectangle([f_box_x1, f_box_y1, f_box_x1 + f_box_w, f_box_y1 + 72], radius=8, fill=(8, 14, 26, 255), outline=BORDER_SUBTLE, width=1)
    
    paste_math_centered(img, f_box_x1 + f_box_w // 2, f_box_y1 + 36, r'$\mathbf{\Delta x = d_1 - d_2 = (x_{\mathrm{Wallal}} - x_{\mathrm{Inter}}) - (x_{\mathrm{Tahiti}} - x_{\mathrm{Inter}}) = x_{\mathrm{Wallal}} - x_{\mathrm{Tahiti}}}$', fontsize=32, color='white', bold=True)

    # Key takeaways bullets
    sub_bullet1 = "• The intermediate plate coordinates cancel out completely from the subtraction."
    sub_bullet2 = "• Yields relative stellar shifts (Wallal vs Tahiti) without requiring absolute plate coordinates."
    sub_bullet3 = "• At the solar limb, 1.75″ corresponds to ≈ 39 μm on the plate."
    draw.text((p1_x1 + 50, res_y + 152), sub_bullet1, font=font_sub_bullet, fill=AMBER_BRIGHT)
    draw.text((p1_x1 + 50, res_y + 202), sub_bullet2, font=font_sub_bullet, fill=TEXT_MUTED)
    draw.text((p1_x1 + 50, res_y + 252), sub_bullet3, font=font_sub_bullet, fill=MINT_BRIGHT)

    # =========================================================================
    # 3. RIGHT PANEL: PLATE REDUCTION & THE 2° BOUNDARY
    # =========================================================================
    p2_x1, p2_y1, p2_x2, p2_y2 = 1250, 155, 2000, 1390
    draw.rounded_rectangle([p2_x1, p2_y1, p2_x2, p2_y2], radius=14, fill=CARD_BG, outline=BORDER_SUBTLE, width=2)

    # Panel 2 Header Bar
    draw.rounded_rectangle([p2_x1, p2_y1, p2_x2, p2_y1 + hdr_h], radius=14, fill=CARD_HEADER_BG, outline=BORDER_SUBTLE, width=1)
    draw.rectangle([p2_x1, p2_y1 + 60, p2_x2, p2_y1 + hdr_h], fill=CARD_HEADER_BG)
    draw.line([(p2_x1, p2_y1 + hdr_h), (p2_x2, p2_y1 + hdr_h)], fill=BORDER_SUBTLE, width=1)
    draw.text((p2_x1 + 25, p2_y1 + 14), "2. PLATE REDUCTION & 2° BOUNDARY", font=font_panel_title, fill=AMBER_BRIGHT)
    draw.text((p2_x1 + 25, p2_y1 + 50), "Separating plate errors from Einstein deflection", font=font_panel_sub, fill=TEXT_MUTED)

    # --- 17-INCH PLATE VISUALIZATION (y: 260 to 680) ---
    plt_cx = (p2_x1 + p2_x2) // 2
    plt_cy = 470
    plt_size = 420
    plt_half = plt_size // 2

    # Photographic Plate Glass Base
    draw.rounded_rectangle([plt_cx - plt_half, plt_cy - plt_half, plt_cx + plt_half, plt_cy + plt_half], radius=12, fill=(8, 13, 24, 255), outline=CARD_BORDER, width=2)
    
    # Astrometric grid
    for g_off in range(-160, 180, 80):
        draw.line([(plt_cx + g_off, plt_cy - plt_half + 10), (plt_cx + g_off, plt_cy + plt_half - 10)], fill=(18, 28, 48, 120), width=1)
        draw.line([(plt_cx - plt_half + 10, plt_cy + g_off), (plt_cx + plt_half - 10, plt_cy + g_off)], fill=(18, 28, 48, 120), width=1)

    # Plate dimension badge top
    draw.text((plt_cx - plt_half + 16, plt_cy - plt_half + 14), "17\" × 17\" Plate (≈ 5° × 5° Field)", font=font_plate_tag, fill=CYAN_SOFT)

    # Eclipsed Sun at Center
    for cr in range(54, 15, -6):
        draw.ellipse([plt_cx - cr, plt_cy - cr, plt_cx + cr, plt_cy + cr], fill=(255, 235, 180, 22))
    r_moon = 18
    draw.ellipse([plt_cx - r_moon, plt_cy - r_moon, plt_cx + r_moon, plt_cy + r_moon], fill=(4, 7, 12, 255), outline=AMBER_WARM, width=2)
    draw_text_centered(draw, plt_cx, plt_cy, "Sun", font=get_font(18, bold=True), fill=(203, 213, 225, 200))

    # 2° Reference Boundary Circle
    r_boundary = 130
    draw_dashed_circle(draw, plt_cx, plt_cy, r_boundary, AMBER_BRIGHT, width=3, n_dash=44)
    
    # 2° Boundary Label Badge
    bnd_tag_x = plt_cx - 115
    bnd_tag_y = plt_cy - r_boundary - 26
    draw.rounded_rectangle([bnd_tag_x, bnd_tag_y, bnd_tag_x + 230, bnd_tag_y + 26], radius=6, fill=(40, 26, 12, 230), outline=AMBER_BRIGHT, width=1)
    draw_text_centered(draw, plt_cx, bnd_tag_y + 13, "2° Reference Boundary", font=get_font(18, bold=True), fill=AMBER_BRIGHT)

    # Inner Stars (r < 130): Outward radial deflection arrows
    inner_stars = [
        (35, 25), (45, 145), (48, 225), (40, 315),
        (65, 75), (75, 195), (85, 280), (70, 355),
        (100, 45), (105, 120), (110, 215), (105, 320)
    ]

    for r_s, th_deg in inner_stars:
        th = math.radians(th_deg)
        sx = plt_cx + r_s * math.cos(th)
        sy = plt_cy + r_s * math.sin(th)
        
        v_len = max(16, int(55.0 * (35.0 / r_s)))
        vx = sx + v_len * math.cos(th)
        vy = sy + v_len * math.sin(th)
        
        draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(15, 23, 42, 255), outline=(148, 163, 184, 180), width=1)
        draw_arrow(draw, sx, sy, vx, vy, MINT_BRIGHT, width=3, arrow_size=9)
        draw.ellipse([vx - 5, vy - 5, vx + 5, vy + 5], fill=MINT_BRIGHT, outline=TEXT_WHITE, width=1)

    # Outer Stars (r > 130): Fixed reference crosshairs
    outer_stars = [
        (150, 20), (165, 70), (155, 110), (180, 165),
        (160, 200), (175, 255), (165, 290), (185, 345),
        (190, 50), (195, 130), (185, 220), (190, 315)
    ]

    for r_s, th_deg in outer_stars:
        th = math.radians(th_deg)
        sx = plt_cx + r_s * math.cos(th)
        sy = plt_cy + r_s * math.sin(th)
        draw.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=CYAN_BRIGHT, outline=TEXT_WHITE, width=1)
        draw.line([(sx - 7, sy), (sx + 7, sy)], fill=CYAN_SOFT, width=1)
        draw.line([(sx, sy - 7), (sx, sy + 7)], fill=CYAN_SOFT, width=1)

    # --- TWO DEDICATED CALLOUT CARDS (Below plate: y: 694 to 832) ---
    c_y = 694
    c_h = 138
    
    # Card A: Inner Stars (< 2°)
    c1_x1, c1_x2 = p2_x1 + 12, p2_x1 + 370
    draw.rounded_rectangle([c1_x1, c_y, c1_x2, c_y + c_h], radius=8, fill=(10, 24, 20, 235), outline=MINT_BORDER, width=2)
    draw.text((c1_x1 + 14, c_y + 12), "INNER STARS (< 2°)", font=font_call_title, fill=MINT_BRIGHT)
    
    # Precise typographic indentation: bullets at c1_x1 + 14, text column at c1_x1 + 36
    draw.text((c1_x1 + 14, c_y + 44), "•", font=font_call_b2, fill=TEXT_WHITE)
    draw.text((c1_x1 + 36, c_y + 44), "Larger expected deflection", font=font_call_b1, fill=TEXT_WHITE)
    draw.text((c1_x1 + 14, c_y + 74), "•", font=font_call_b2, fill=MINT_TEXT_BRIGHT)
    draw.text((c1_x1 + 36, c_y + 74), "Measured relative to", font=font_call_b2, fill=MINT_TEXT_BRIGHT)
    draw.text((c1_x1 + 36, c_y + 102), "outer reference stars", font=font_call_b2, fill=MINT_TEXT_BRIGHT)

    # Card B: Outer Stars (> 2°)
    c2_x1, c2_x2 = p2_x1 + 380, p2_x2 - 12
    draw.rounded_rectangle([c2_x1, c_y, c2_x2, c_y + c_h], radius=8, fill=(10, 20, 38, 235), outline=CYAN_BORDER, width=2)
    draw.text((c2_x1 + 14, c_y + 12), "OUTER STARS (> 2°)", font=font_call_title, fill=CYAN_BRIGHT)
    
    # Precise typographic indentation: bullets at c2_x1 + 14, text column at c2_x1 + 36
    draw.text((c2_x1 + 14, c_y + 44), "•", font=font_call_b2, fill=TEXT_WHITE)
    draw.text((c2_x1 + 36, c_y + 44), "Small expected deflection", font=font_call_b1, fill=TEXT_WHITE)
    draw.text((c2_x1 + 14, c_y + 74), "•", font=font_call_b2, fill=CYAN_TEXT_BRIGHT)
    draw.text((c2_x1 + 36, c_y + 74), "Used to determine", font=font_call_b2, fill=CYAN_TEXT_BRIGHT)
    draw.text((c2_x1 + 36, c_y + 102), "plate corrections", font=font_call_b2, fill=CYAN_TEXT_BRIGHT)

    # --- PANEL 2 BOTTOM SUMMARY CARD (y: 844 to 1368) ---
    s2_y = 844
    s2_h = 524
    draw.rounded_rectangle([p2_x1 + 18, s2_y, p2_x2 - 18, s2_y + s2_h], radius=12, fill=(16, 24, 38, 255), outline=CARD_BORDER, width=2)
    
    draw.text((p2_x1 + 35, s2_y + 22), "PLATE REDUCTION PROCEDURE", font=font_proc_title, fill=AMBER_BRIGHT)
    draw.line([(p2_x1 + 35, s2_y + 58), (p2_x2 - 35, s2_y + 58)], fill=BORDER_SUBTLE, width=1)

    r2_bullets = [
        ("Step 1 · Outer Reference Frame", "Outer stars determine scale, orientation, and position corrections.", CYAN_BRIGHT),
        ("Step 2 · Inner-Star Displacements", "After applying those corrections, the remaining inner-star shifts are examined for the expected radial pattern.", MINT_BRIGHT),
        ("Step 3 · Least-Squares Solution", "The measured stellar displacements on each plate are combined to estimate the equivalent deflection at the solar limb.", AMBER_BRIGHT),
    ]

    cur_by = s2_y + 76
    for b_title, b_desc, b_col in r2_bullets:
        draw.text((p2_x1 + 35, cur_by), "▸ " + b_title, font=font_step_title, fill=b_col)
        lines = textwrap.wrap(b_desc, width=52)
        for idx, l in enumerate(lines):
            draw.text((p2_x1 + 55, cur_by + 36 + idx * 30), l, font=font_step_desc, fill=TEXT_MUTED)
        cur_by += 138

    # Outer border
    draw.rectangle([0, 0, W - 1, H - 1], outline=BORDER_SUBTLE, width=1)

    output_path_2x.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path_2x, "PNG", optimize=True)
    print(f"Saved 2x image to {output_path_2x}")
    
    # Save standard 1x (680px width)
    img_1x = img.resize((680, int(H * (680.0 / W))), Image.Resampling.LANCZOS)
    img_1x.save(output_path, "PNG", optimize=True)
    print(f"Saved 1x image to {output_path}")

if __name__ == "__main__":
    generate_schematic()
