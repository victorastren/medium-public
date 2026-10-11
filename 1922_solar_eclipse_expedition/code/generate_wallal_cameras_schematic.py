#!/usr/bin/env python3
r"""
Create technical schematic for Medium:
"Twin 15-Foot Einstein Cameras · Wallal (1922)"

Accompanies the section "The Eclipse of 21 September 1922".
Aesthetic:
- Cosmic dark slate (#0b0f19) matching light_deflection_geometry and deflection_predictions_comparison
- Deep navy/slate panels (#0f172a, #1e293b) with vibrant cyan (#38bdf8), mint (#34d399), and indigo accents
- Authentic architectural elevation drawing showing:
  1. Two parallel 15-ft camera tubes (Camera No. 1 & No. 2)
  2. Long visual guiding telescope mounted rigidly between them
  3. Hastings–Brashear quadruplet lenses (5-inch apertures) at front end
  4. 17 x 17 inch photographic plates at breech end
  5. Heavy equatorial polar mounting on concrete piers with clock-controlled drive
  6. Human silhouette (~1.8 m) and engineering dimension lines emphasizing physical scale
  7. Inset technical specifications card and bottom key takeaways
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "wallal_twin_cameras_schematic.png"
W, H = 2040, 1240

# --- COLOR PALETTE (Harmonized with light_deflection_geometry & deflection_predictions_comparison) ---
BG_COLOR = (11, 15, 25, 255)         # #0b0f19 Cosmic dark slate
GRID_COLOR = (19, 27, 46, 255)       # #131b2e Subtle cosmic drafting grid

# Cards & Panels
CARD_BG = (15, 23, 42, 255)          # #0f172a Deep navy card fill
CARD_BORDER = (51, 65, 85, 255)      # #334155 Slate card border
CARD_HEADER_BG = (3, 105, 161, 255)  # #0369a1 Blue header banner
CARD_HEADER_BRD = (56, 189, 248, 255)# #38bdf8 Bright sky-blue border

# Accents
CYAN_BRIGHT = (56, 189, 248, 255)    # #38bdf8 Camera optics & plates
CYAN_SOFT = (125, 211, 252, 255)     # #7dd3fc
CYAN_PALE = (186, 230, 253, 255)     # #bae6fd
CYAN_DEEP = (2, 132, 199, 255)       # #0284c7

MINT_BRIGHT = (52, 211, 153, 255)    # #34d399 Vibrant Mint / Emerald (Guiding system)
MINT_SOFT = (110, 231, 183, 255)     # #6ee7b7 Soft Mint
MINT_DEEP = (5, 150, 105, 255)       # #059669 Deep Mint header

AMBER_BRIGHT = (251, 191, 36, 255)   # #fbbf24 Warm yellow/gold
AMBER_WARM = (245, 158, 11, 255)     # #f59e0b
AMBER_DEEP = (180, 83, 9, 255)       # #b45309
AMBER_DARK = (120, 53, 15, 255)      # #78350f Telescope tube

INDIGO_ACCENT = (129, 140, 248, 255) # #818cf8 Soft glowing indigo
INDIGO_LINE = (99, 102, 241, 255)    # #6366f1
INDIGO_SOFT = (199, 210, 254, 255)   # #c7d2fe

# Typography
TEXT_WHITE = (255, 255, 255, 255)    # #ffffff
TEXT_CYAN = (125, 211, 252, 255)     # #7dd3fc
TEXT_PALE_CYAN = (186, 230, 253, 255)# #bae6fd
TEXT_YELLOW = (253, 224, 71, 255)    # #fde047
TEXT_SLATE = (203, 213, 225, 255)    # #cbd5e1
TEXT_MUTED = (148, 163, 184, 255)    # #94a3b8

# Mechanical & Structural Elements
TUBE_TOP = (30, 41, 59, 255)         # #1e293b
TUBE_SHADED = (15, 23, 42, 255)      # #0f172a
RAIL_CYAN = (56, 189, 248, 255)      # #38bdf8
TRUSS_CYAN = (2, 132, 199, 200)      # #0284c7 subtle
TRUSS_BAND = (56, 189, 248, 255)

PIER_FILL = (30, 41, 59, 255)        # #1e293b
PIER_BORDER = (71, 85, 105, 255)     # #475569
GROUND_LINE = (71, 85, 105, 255)

def get_font(size, bold=False, italic=False):
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

def draw_arrow(draw, x1, y1, x2, y2, color, width=2, arrow_size=10):
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

def draw_callout_box(draw, x, y, title, subtitle_lines, accent_color, width=500, font_t=None, font_s=None, align_right=False):
    """Draw a callout box supporting multi-line subtitles with clean padding."""
    if isinstance(subtitle_lines, str):
        lines = [subtitle_lines]
    else:
        lines = list(subtitle_lines)
    
    num_sub = len(lines)
    if num_sub == 0 or (num_sub == 1 and not lines[0]):
        box_h = 52
    elif num_sub == 1:
        box_h = 84
    else:
        box_h = 116
        
    box_w = width
    bx = x - box_w if align_right else x
    by = y - box_h // 2

    # Card glow & body
    draw.rounded_rectangle([bx, by, bx + box_w, by + box_h], radius=8, fill=CARD_BG, outline=CARD_BORDER, width=2)
    bar_x = bx + box_w - 6 if align_right else bx
    draw.rounded_rectangle([bar_x, by + 4, bar_x + 6, by + box_h - 4], radius=3, fill=accent_color)
    tx = bx + 22 if not align_right else bx + 18
    draw.text((tx, by + 12), title, font=font_t, fill=TEXT_WHITE)

    if accent_color == CYAN_BRIGHT:
        sub_col = TEXT_CYAN
    elif accent_color == MINT_BRIGHT:
        sub_col = MINT_SOFT
    elif accent_color == INDIGO_ACCENT:
        sub_col = INDIGO_SOFT
    elif accent_color == AMBER_BRIGHT:
        sub_col = TEXT_YELLOW
    else:
        sub_col = TEXT_SLATE

    sub_y = by + 46
    for sl in lines:
        draw.text((tx, sub_y), sl, font=font_s, fill=sub_col)
        sub_y += 30

    return bx, by, box_w, box_h

def draw_astronomer_figure(draw, base_x, base_y):
    # Wooden observer step platform
    plat_w, plat_h = 95, 26
    plat_x1 = base_x - 35
    plat_y1 = base_y - plat_h
    draw.rectangle([plat_x1, plat_y1, plat_x1 + plat_w, base_y], fill=(69, 26, 3, 255), outline=AMBER_WARM, width=2)
    draw.line([(plat_x1 + 10, plat_y1 + 13), (plat_x1 + plat_w - 10, plat_y1 + 13)], fill=AMBER_DEEP, width=1)
    
    feet_y = plat_y1
    # Scale: height = 205 px (~1.8 m)
    head_cy = feet_y - 175
    head_r = 13
    draw.ellipse([base_x - head_r, head_cy - head_r, base_x + head_r, head_cy + head_r], fill=(148, 163, 184, 255))
    draw.line([(base_x - 18, head_cy - 4), (base_x + 22, head_cy - 4)], fill=TEXT_WHITE, width=4)
    draw.rectangle([base_x - 11, head_cy - 16, base_x + 11, head_cy - 4], fill=TEXT_WHITE)

    neck_y = head_cy + 14
    waist_y = feet_y - 80
    draw.polygon([
        (base_x - 15, neck_y), (base_x + 15, neck_y), (base_x + 18, waist_y), (base_x - 15, waist_y)
    ], fill=(71, 85, 105, 255), outline=TEXT_SLATE, width=1)

    knee_y = feet_y - 40
    draw.polygon([
        (base_x - 15, waist_y), (base_x + 18, waist_y), (base_x + 20, knee_y), (base_x - 13, knee_y)
    ], fill=(71, 85, 105, 255), outline=TEXT_SLATE, width=1)

    # Right arm reaching forward and up directly to slow-motion tangent knob / eyepiece
    sh_r = (base_x + 12, neck_y + 8)
    elb_r = (base_x + 36, neck_y + 30)
    hand_r = (base_x + 58, neck_y + 18)
    draw.line([sh_r, elb_r, hand_r], fill=(148, 163, 184, 255), width=8)
    draw.ellipse([hand_r[0] - 4, hand_r[1] - 4, hand_r[0] + 4, hand_r[1] + 4], fill=TEXT_WHITE)

    # Left arm relaxed
    sh_l = (base_x - 12, neck_y + 8)
    elb_l = (base_x - 18, neck_y + 32)
    hand_l = (base_x - 12, waist_y - 4)
    draw.line([sh_l, elb_l, hand_l], fill=(100, 116, 139, 255), width=7)

    # Trousers & Legs
    draw.line([(base_x - 6, knee_y), (base_x - 8, feet_y)], fill=(100, 116, 139, 255), width=9)
    draw.line([(base_x + 10, knee_y), (base_x + 12, feet_y)], fill=(100, 116, 139, 255), width=9)

    draw.rectangle([base_x - 15, feet_y - 6, base_x - 2, feet_y], fill=(51, 65, 85, 255))
    draw.rectangle([base_x + 5, feet_y - 6, base_x + 20, feet_y], fill=(51, 65, 85, 255))

def create_schematic(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new('RGBA', (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 1. Subtle Cosmic Background Stars (Masked away from all UI cards and text)
    np.random.seed(1922)
    num_stars = 350
    star_x = np.random.uniform(20, W - 20, num_stars)
    star_y = np.random.uniform(20, H - 20, num_stars)
    star_r = np.random.uniform(1.0, 2.8, num_stars)
    star_a = np.random.uniform(35, 110, num_stars)

    def in_mask(px, py):
        if 40 <= px <= W - 40 and 15 <= py <= 130:
            return True
        if py >= 1040:
            return True
        if 40 <= px <= 680 and 130 <= py <= 545:   # Specs Card
            return True
        if 740 <= px <= 1280 and 130 <= py <= 265: # Callout 1 (Objectives) in upper sky
            return True
        if 40 <= px <= 600 and 540 <= py <= 850:   # Left Callouts 4 & 5
            return True
        if 150 <= px <= 515 and 955 <= py <= 1005: # Astronomer label
            return True
        if 480 <= px <= 790 and 720 <= py <= 1040: # South Pier area
            return True
        if 1420 <= px <= W - 40 and 370 <= py <= 730: # Right Callouts 2 & 3
            return True
        if 860 <= px <= 1260 and 460 <= py <= 540:  # Dimension line pill
            return True
        if 910 <= px <= 1190 and 850 <= py <= 910:  # Diurnal tracking text
            return True
        if 1560 <= px <= W - 40 and 50 <= py <= 115: # Starlight text
            return True
        return False

    for i in range(num_stars):
        if in_mask(star_x[i], star_y[i]):
            continue
        alpha = int(star_a[i])
        col = (255, 255, 255, alpha)
        r = star_r[i]
        draw.ellipse([star_x[i] - r, star_y[i] - r, star_x[i] + r, star_y[i] + r], fill=col)

    # 2. Subtle Blueprint Grid
    for gx in range(0, W, 40):
        draw.line([(gx, 0), (gx, H)], fill=GRID_COLOR, width=1)
    for gy in range(0, H, 40):
        draw.line([(0, gy), (W, gy)], fill=GRID_COLOR, width=1)

    # High-legibility typography optimized for Medium 680px rendering
    font_main_title = get_font(40, bold=True)
    font_main_sub = get_font(27, bold=False)
    font_card_title = get_font(25, bold=True)
    font_card_body = get_font(24, bold=False)
    font_card_bold = get_font(23, bold=True)
    font_callout_t = get_font(25, bold=True)
    font_callout_s = get_font(24, bold=False)
    font_dim = get_font(23, bold=True)
    font_label_bold = get_font(24, bold=True)
    font_mini = get_font(20, bold=False)

    # Top Title Header Banner
    head_box_x = 60
    head_box_y = 24
    head_box_w = W - 120
    head_box_h = 96
    draw.rounded_rectangle([head_box_x, head_box_y, head_box_x + head_box_w, head_box_y + head_box_h],
                           radius=10, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.text((head_box_x + 24, head_box_y + 12), "TWIN 15-FOOT EINSTEIN CAMERAS · WALLAL (1922)",
              font=font_main_title, fill=TEXT_WHITE)
    draw.text((head_box_x + 24, head_box_y + 56), "Technical reconstruction of the Lick Observatory cameras used for the light-deflection measurements",
              font=font_main_sub, fill=CYAN_SOFT)

    ground_y = 1010
    draw.line([(40, ground_y), (W - 40, ground_y)], fill=GROUND_LINE, width=3)
    for sx_g in range(50, W - 50, 25):
        draw.line([(sx_g, ground_y + 4), (sx_g - 12, ground_y + 24)], fill=GRID_COLOR, width=2)

    # Cement Piers (Clean architectural representation)
    p1_x1, p1_x2 = 640, 780
    p1_y1, p1_y2 = 760, ground_y
    draw.rectangle([p1_x1, p1_y1, p1_x2, p1_y2], fill=PIER_FILL, outline=PIER_BORDER, width=2)
    draw.line([(p1_x1 + 6, p1_y1), (p1_x1 + 6, p1_y2)], fill=CYAN_BRIGHT, width=2)

    p2_x1, p2_x2 = 1110, 1250
    p2_y1, p2_y2 = 590, ground_y
    draw.rectangle([p2_x1, p2_y1, p2_x2, p2_y2], fill=PIER_FILL, outline=PIER_BORDER, width=2)
    draw.line([(p2_x1 + 6, p2_y1), (p2_x1 + 6, p2_y2)], fill=CYAN_BRIGHT, width=2)

    # Polar Axis Bearings
    b1_pt = (p1_x1 + 70, p1_y1)  # (710, 760)
    b2_pt = (p2_x1 + 70, p2_y1)  # (1180, 590)

    # Polar axis shaft
    draw.line([(b1_pt[0] - 80, b1_pt[1] + 30), (b2_pt[0] + 80, b2_pt[1] - 30)], fill=TEXT_SLATE, width=20)
    draw.line([(b1_pt[0] - 80, b1_pt[1] + 30), (b2_pt[0] + 80, b2_pt[1] - 30)], fill=CYAN_DEEP, width=10)

    # Bearing housings
    draw.rounded_rectangle([b1_pt[0] - 32, b1_pt[1] - 18, b1_pt[0] + 32, b1_pt[1] + 18], radius=4, fill=CARD_BG, outline=CYAN_BRIGHT, width=2)
    draw.rounded_rectangle([b2_pt[0] - 32, b2_pt[1] - 18, b2_pt[0] + 32, b2_pt[1] + 18], radius=4, fill=CARD_BG, outline=CYAN_BRIGHT, width=2)


    # Clock Drive Box placed cleanly between piers in open space
    cd_x1, cd_y1 = 815, ground_y - 130
    cd_x2, cd_y2 = 885, ground_y - 25
    draw.rectangle([cd_x1, cd_y1, cd_x2, cd_y2], fill=CARD_BG, outline=CYAN_BRIGHT, width=2)
    draw.line([(cd_x1 + 25, cd_y1 + 15), (cd_x1 + 25, cd_y2 - 20)], fill=TEXT_SLATE, width=2)
    draw.rectangle([cd_x1 + 16, cd_y2 - 45, cd_x1 + 34, cd_y2 - 20], fill=AMBER_WARM, outline=TEXT_WHITE, width=1)
    draw.text((cd_x1 - 14, cd_y2 + 6), "Clock Drive", font=font_mini, fill=TEXT_WHITE)

    # Worm shaft from clock drive to polar axis
    draw.line([(cd_x1 + 25, cd_y1), (b1_pt[0] + 80, b1_pt[1] + 10)], fill=CYAN_BRIGHT, width=3)

    # Camera geometry
    cradle_cx = (b1_pt[0] + b2_pt[0]) / 2 + 10  # 955
    cradle_cy = (b1_pt[1] + b2_pt[1]) / 2 - 15  # 660

    tube_angle = math.radians(33.5)
    cos_t = math.cos(tube_angle)
    sin_t = math.sin(tube_angle)
    norm_x = -sin_t
    norm_y = -cos_t
    depth_x = 28
    depth_y = -18

    def pt(dist, sky_offset=0, depth_idx=0):
        bx = cradle_cx + dist * cos_t + sky_offset * norm_x + depth_idx * depth_x
        by = cradle_cy - dist * sin_t + sky_offset * norm_y + depth_idx * depth_y
        return bx, by

    breech_dist = -300
    obj_dist = 660
    tube_h = 44
    cam_gap = 18

    # Camera 2 (Background)
    c2_sky_base = cam_gap / 2 + 10
    c2_b_bl = pt(breech_dist, c2_sky_base, depth_idx=1)
    c2_b_tl = pt(breech_dist, c2_sky_base + tube_h, depth_idx=1)
    c2_o_bl = pt(obj_dist, c2_sky_base, depth_idx=1)
    c2_o_tl = pt(obj_dist, c2_sky_base + tube_h, depth_idx=1)

    draw.polygon([c2_b_bl, c2_b_tl, c2_o_tl, c2_o_bl], fill=TUBE_TOP, outline=CYAN_DEEP, width=2)

    # Tube 2 Objective
    c2_obj_c = pt(obj_dist + 26, c2_sky_base + tube_h / 2, depth_idx=1)
    draw.polygon([
        c2_o_bl, c2_o_tl,
        pt(obj_dist + 24, c2_sky_base + tube_h + 4, depth_idx=1),
        pt(obj_dist + 24, c2_sky_base - 4, depth_idx=1)
    ], fill=CYAN_DEEP, outline=CYAN_BRIGHT, width=2)
    draw.ellipse([c2_obj_c[0] - 12, c2_obj_c[1] - 8, c2_obj_c[0] + 12, c2_obj_c[1] + 8], fill=CYAN_PALE, outline=CYAN_BRIGHT, width=2)

    # Tube 2 Plate Holder
    draw.polygon([
        c2_b_bl, c2_b_tl,
        pt(breech_dist - 34, c2_sky_base + tube_h + 12, depth_idx=1),
        pt(breech_dist - 34, c2_sky_base - 12, depth_idx=1)
    ], fill=(30, 41, 59, 255), outline=CYAN_BRIGHT, width=2)

    # Guiding Telescope (Mounted rigidly between girders)
    g_sky = 0
    g_r = 13
    g_breech = breech_dist - 65
    g_obj = obj_dist + 35

    g_bl = pt(g_breech, g_sky - g_r, depth_idx=0.5)
    g_tl = pt(g_breech, g_sky + g_r, depth_idx=0.5)
    g_tr = pt(g_obj, g_sky + g_r, depth_idx=0.5)
    g_br = pt(g_obj, g_sky - g_r, depth_idx=0.5)

    draw.polygon([g_bl, g_tl, g_tr, g_br], fill=(120, 53, 15, 255), outline=AMBER_WARM, width=2)

    for r_d in [-140, 60, 260, 460]:
        r_p = pt(r_d, g_sky, depth_idx=0.5)
        draw.ellipse([r_p[0] - 16, r_p[1] - 16, r_p[0] + 16, r_p[1] + 16], fill=None, outline=AMBER_BRIGHT, width=3)

    g_front = pt(g_obj + 14, g_sky, depth_idx=0.5)
    draw.rounded_rectangle([g_front[0] - 15, g_front[1] - 10, g_front[0] + 15, g_front[1] + 10], radius=3, fill=AMBER_WARM, outline=TEXT_WHITE, width=2)
    draw.ellipse([g_front[0] - 10, g_front[1] - 6, g_front[0] + 10, g_front[1] + 6], fill=CYAN_PALE, outline=CYAN_BRIGHT, width=2)

    g_eye = pt(g_breech - 22, g_sky, depth_idx=0.5)
    draw.rectangle([g_eye[0] - 16, g_eye[1] - 12, g_eye[0] + 16, g_eye[1] + 12], fill=AMBER_WARM, outline=TEXT_WHITE, width=2)
    draw.rectangle([g_eye[0] - 30, g_eye[1] - 6, g_eye[0] - 16, g_eye[1] + 6], fill=(51, 65, 85, 255), outline=TEXT_WHITE, width=2)
    draw.line([(g_eye[0] - 4, g_eye[1] + 12), (g_eye[0] - 4, g_eye[1] + 30)], fill=AMBER_BRIGHT, width=3)
    draw.ellipse([g_eye[0] - 10, g_eye[1] + 26, g_eye[0] + 2, g_eye[1] + 38], fill=AMBER_WARM, outline=TEXT_WHITE, width=2)

    # Camera 1 (Foreground)
    c1_sky_base = -cam_gap / 2 - tube_h - 10
    c1_b_bl = pt(breech_dist, c1_sky_base, depth_idx=0)
    c1_b_tl = pt(breech_dist, c1_sky_base + tube_h, depth_idx=0)
    c1_o_bl = pt(obj_dist, c1_sky_base, depth_idx=0)
    c1_o_tl = pt(obj_dist, c1_sky_base + tube_h, depth_idx=0)

    draw.polygon([c1_b_bl, c1_b_tl, c1_o_tl, c1_o_bl], fill=TUBE_SHADED, outline=CYAN_BRIGHT, width=3)
    draw.line([c1_b_tl, c1_o_tl], fill=CYAN_BRIGHT, width=3)

    # Timber girder cross-bracing
    bands = [-180, -60, 60, 180, 300, 420, 540]
    for b_idx in range(len(bands) - 1):
        bd1, bd2 = bands[b_idx], bands[b_idx + 1]
        bp1_bot = pt(bd1, c1_sky_base, depth_idx=0)
        bp1_top = pt(bd1, c1_sky_base + tube_h, depth_idx=0)
        bp2_bot = pt(bd2, c1_sky_base, depth_idx=0)
        bp2_top = pt(bd2, c1_sky_base + tube_h, depth_idx=0)
        draw.line([bp1_bot, bp2_top], fill=CYAN_DEEP, width=2)
        draw.line([bp1_top, bp2_bot], fill=CYAN_DEEP, width=2)

    for band_d in bands:
        bp1 = pt(band_d, c1_sky_base - 2, depth_idx=0)
        bp2 = pt(band_d, c1_sky_base + tube_h + 2, depth_idx=0)
        draw.line([bp1, bp2], fill=CYAN_BRIGHT, width=3)

    c1_obj_c = pt(obj_dist + 26, c1_sky_base + tube_h / 2, depth_idx=0)
    draw.polygon([
        c1_o_bl, c1_o_tl,
        pt(obj_dist + 24, c1_sky_base + tube_h + 4, depth_idx=0),
        pt(obj_dist + 24, c1_sky_base - 4, depth_idx=0)
    ], fill=CYAN_DEEP, outline=CYAN_BRIGHT, width=3)
    draw.ellipse([c1_obj_c[0] - 14, c1_obj_c[1] - 9, c1_obj_c[0] + 14, c1_obj_c[1] + 9], fill=CYAN_PALE, outline=CYAN_BRIGHT, width=2)

    # Camera 1 Plate Holder
    c1_pl_bl = pt(breech_dist - 34, c1_sky_base - 14, depth_idx=0)
    c1_pl_tl = pt(breech_dist - 34, c1_sky_base + tube_h + 14, depth_idx=0)
    draw.polygon([
        c1_b_bl, c1_b_tl, c1_pl_tl, c1_pl_bl
    ], fill=(30, 41, 59, 255), outline=CYAN_BRIGHT, width=3)
    draw.line([
        pt(breech_dist - 18, c1_sky_base - 10, depth_idx=0),
        pt(breech_dist - 18, c1_sky_base + tube_h + 10, depth_idx=0)
    ], fill=CYAN_PALE, width=3)

    # Cradle crossheads
    crd_p1 = pt(-160, c1_sky_base - 12, depth_idx=0)
    crd_p2 = pt(-160, c2_sky_base + tube_h + 12, depth_idx=1)
    crd_p3 = pt(220, c2_sky_base + tube_h + 12, depth_idx=1)
    crd_p4 = pt(220, c1_sky_base - 12, depth_idx=0)
    draw.line([crd_p1, crd_p2], fill=CYAN_BRIGHT, width=6)
    draw.line([crd_p4, crd_p3], fill=CYAN_BRIGHT, width=6)
    draw.rectangle([cradle_cx - 36, cradle_cy - 24, cradle_cx + 36, cradle_cy + 24], fill=CARD_BG, outline=CYAN_BRIGHT, width=3)

    # 4. INCOMING STARLIGHT BEAM (Completely Unobstructed!)
    # Starlight arrives along the optical axis from the deep cosmos
    ray_len = 340
    r1_start = (c1_obj_c[0] + ray_len * cos_t, c1_obj_c[1] - ray_len * sin_t)
    r2_start = (c2_obj_c[0] + ray_len * cos_t, c2_obj_c[1] - ray_len * sin_t)

    # Soft luminous starlight swath (warm celestial yellow/amber glow)
    beam_mask = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d_beam = ImageDraw.Draw(beam_mask)
    d_beam.polygon([
        (r1_start[0], r1_start[1]),
        (r2_start[0] + 20, r2_start[1] - 12),
        (c2_obj_c[0] + 16 * cos_t, c2_obj_c[1] - 16 * sin_t),
        (c1_obj_c[0] + 16 * cos_t, c1_obj_c[1] - 16 * sin_t),
    ], fill=(251, 191, 36, 26))
    img.alpha_composite(beam_mask)

    # Crisp directional starlight arrows entering apertures (warm celestial yellow)
    draw_arrow(draw, r1_start[0], r1_start[1], c1_obj_c[0] + 14 * cos_t, c1_obj_c[1] - 14 * sin_t, AMBER_BRIGHT, width=3, arrow_size=14)
    draw_arrow(draw, r2_start[0], r2_start[1], c2_obj_c[0] + 14 * cos_t, c2_obj_c[1] - 14 * sin_t, TEXT_YELLOW, width=3, arrow_size=14)

    # Starlight Header in upper-right sky
    draw.text((1580, 75), "Starlight from eclipse field", font=font_label_bold, fill=TEXT_YELLOW)

    # 5. Dimension Line (Cyan glow matching cosmic style)
    dim_sky = c2_sky_base + tube_h + 60
    d_p1 = pt(breech_dist, dim_sky, depth_idx=1)
    d_p2 = pt(obj_dist, dim_sky, depth_idx=1)

    # Witness lines
    draw.line([pt(breech_dist, c2_sky_base + tube_h + 6, depth_idx=1), (d_p1[0] + 6 * norm_x, d_p1[1] + 6 * norm_y)], fill=CARD_BORDER, width=2)
    draw.line([pt(obj_dist, c2_sky_base + tube_h + 6, depth_idx=1), (d_p2[0] + 6 * norm_x, d_p2[1] + 6 * norm_y)], fill=CARD_BORDER, width=2)

    dim_mx = (d_p1[0] + d_p2[0]) / 2
    dim_my = (d_p1[1] + d_p2[1]) / 2
    dim_str = "15 ft (4.57 m) Focal Length"
    dbb = draw.textbbox((0, 0), dim_str, font=font_dim)
    db_w = dbb[2] - dbb[0] + 36
    db_h = 42

    # Continuous cyan dimension line
    draw.line([(d_p1[0], d_p1[1]), (d_p2[0], d_p2[1])], fill=CYAN_BRIGHT, width=2)
    draw_arrow(draw, d_p1[0] + 30 * cos_t, d_p1[1] - 30 * sin_t, d_p1[0], d_p1[1], CYAN_BRIGHT, width=2, arrow_size=10)
    draw_arrow(draw, d_p2[0] - 30 * cos_t, d_p2[1] + 30 * sin_t, d_p2[0], d_p2[1], CYAN_BRIGHT, width=2, arrow_size=10)

    # Dark pill overlay
    draw.rounded_rectangle([dim_mx - db_w / 2, dim_my - db_h / 2, dim_mx + db_w / 2, dim_my + db_h / 2], radius=6, fill=CARD_BG, outline=CYAN_BRIGHT, width=2)
    draw.text((dim_mx - db_w / 2 + 18, dim_my - 14), dim_str, font=font_dim, fill=TEXT_WHITE)

    # 6. Astronomer Figure
    h_x = 570
    h_y = ground_y
    draw_astronomer_figure(draw, h_x, h_y)
    draw.text((160, 965), "Scale figure (~1.8 m / 6 ft)", font=font_card_bold, fill=TEXT_WHITE)

    # 7. Tracking Motion Curved Arrow (Subtle, placed cleanly in open space under cradle)
    tr_cx, tr_cy = 1010, 825
    draw.arc([tr_cx - 36, tr_cy - 36, tr_cx + 36, tr_cy + 36], start=40, end=190, fill=CYAN_BRIGHT, width=3)
    draw_arrow(draw, tr_cx - 34, tr_cy + 8, tr_cx - 32, tr_cy + 20, CYAN_BRIGHT, width=2, arrow_size=8)
    font_track = get_font(22, bold=False)
    draw.text((tr_cx - 93, tr_cy + 42), "Sidereal tracking", font=font_track, fill=TEXT_WHITE)

    # 8. CALLOUT BOXES - HARMONIOUS ZERO-CROSSING ARCHITECTURE

    # --- TOP-CENTER (Objectives Callout placed in open sky, leaving starlight beam and dimension arrow pristine) ---
    c_obj_x, c_obj_y = 750, 196
    draw_callout_box(draw, c_obj_x, c_obj_y, "Twin 5-inch (12.7 cm) Objectives",
                     ["Hastings–Brashear quadruplet lenses", "Photographic objectives (f/36)"],
                     CYAN_BRIGHT, width=520, font_t=font_callout_t, font_s=font_callout_s)
    # Direct straight white arrow pointing directly to the telescope objectives
    tgt_obj = (1532, 265)
    draw_arrow(draw, c_obj_x + 520, c_obj_y, tgt_obj[0], tgt_obj[1], TEXT_WHITE, width=2, arrow_size=11)

    # --- RIGHT SIDE (2 spacious, high-contrast callouts) ---
    # 2. Guiding Scope (Mid right: x = 1460, y = 440) - MINT / EMERALD (Distinct from orange tube!)
    c_guide_x, c_guide_y = 1460, 440
    draw_callout_box(draw, c_guide_x, c_guide_y, "Attached Guiding Telescope",
                     ["Visual refractor with cross wire", "Mounted rigidly between twin girders"],
                     MINT_BRIGHT, width=520, font_t=font_callout_t, font_s=font_callout_s)
    g_tgt = pt(400, g_sky, depth_idx=0.5)
    draw.line([(c_guide_x, c_guide_y), (g_tgt[0] + 10, g_tgt[1])], fill=MINT_BRIGHT, width=2)
    draw.ellipse([g_tgt[0] + 7, g_tgt[1] - 3, g_tgt[0] + 13, g_tgt[1] + 3], fill=MINT_BRIGHT)

    # 3. Polar Mounting (Lower right: x = 1440, y = 660)
    c_mnt_x, c_mnt_y = 1440, 660
    draw_callout_box(draw, c_mnt_x, c_mnt_y, "Redesigned Polar Mounting",
                     ["Rigid timber cradle on concrete piers", "Driven by clock-controlled drive"],
                     INDIGO_ACCENT, width=510, font_t=font_callout_t, font_s=font_callout_s)
    mnt_tgt = (b2_pt[0] + 20, b2_pt[1] + 10)
    draw.line([(c_mnt_x, c_mnt_y), (mnt_tgt[0], mnt_tgt[1])], fill=INDIGO_ACCENT, width=2)
    draw.ellipse([mnt_tgt[0] - 3, mnt_tgt[1] - 3, mnt_tgt[0] + 3, mnt_tgt[1] + 3], fill=INDIGO_ACCENT)

    # --- LEFT SIDE (2 clean callouts below Specifications Card) ---
    # 4. Photographic Plates: placed at x = 40, y = 590
    c_pl_x, c_pl_y = 40, 590
    draw_callout_box(draw, c_pl_x, c_pl_y, "17 × 17 in Photographic Plates",
                     ["Glass photographic plates", "Covering ≈ 5° field (scale ≈ 45″/mm)"],
                     CYAN_BRIGHT, width=480, font_t=font_callout_t, font_s=font_callout_s)
    pl_tgt = (663, 764)
    draw_arrow(draw, c_pl_x + 480, c_pl_y, pl_tgt[0], pl_tgt[1], TEXT_WHITE, width=2, arrow_size=11)

    # 5. Observer Guiding Station: placed at x = 40, y = 745
    c_ret_x, c_ret_y = 40, 745
    draw_callout_box(draw, c_ret_x, c_ret_y, "Guiding Eyepiece & Cross Wire",
                     ["Trumpler held star on cross wire", "Corrected drive drift during exposures"],
                     MINT_BRIGHT, width=480, font_t=font_callout_t, font_s=font_callout_s)
    obs_tgt = (g_eye[0] - 8, g_eye[1] + 12)
    # Dogleg leader line passing cleanly above the scale figure, then angling down in front to the eyepiece
    lead_ret_corner_x = 615
    draw.line([(c_ret_x + 480, c_ret_y), (lead_ret_corner_x, c_ret_y)], fill=MINT_BRIGHT, width=2)
    draw.line([(lead_ret_corner_x, c_ret_y), (obs_tgt[0], obs_tgt[1])], fill=MINT_BRIGHT, width=2)
    draw.ellipse([obs_tgt[0] - 3, obs_tgt[1] - 3, obs_tgt[0] + 3, obs_tgt[1] + 3], fill=MINT_BRIGHT)

    # --- Inset Technical Specifications Card (Top Left) ---
    # Enlarged typography (23px bold labels, 24px regular values) with clean padding
    sp_x1, sp_y1 = 60, 140
    sp_w, sp_h = 615, 390
    draw.rounded_rectangle([sp_x1, sp_y1, sp_x1 + sp_w, sp_y1 + sp_h], radius=10, fill=CARD_BG, outline=CYAN_DEEP, width=2)

    # Card Banner Header
    draw.rounded_rectangle([sp_x1, sp_y1, sp_x1 + sp_w, sp_y1 + 50], radius=10, fill=CARD_HEADER_BG, outline=CARD_HEADER_BRD, width=2)
    draw.text((sp_x1 + 22, sp_y1 + 13), "OPTICAL & MECHANICAL SPECIFICATIONS", font=font_card_title, fill=TEXT_WHITE)

    specs = [
        ("Aperture:", "5.0 in (12.7 cm)"),
        ("Focal Length:", "15 feet (4.57 m), f/36"),
        ("Plate Size:", "17 × 17 in (43 × 43 cm) glass"),
        ("Field of View:", "≈ 5° field (scale ≈ 45″/mm)"),
        ("Configuration:", "Two parallel cameras"),
        ("Guiding Scope:", "Visual refractor with cross wire"),
        ("Mounting:", "Rigid polar mounting"),
        ("Drive System:", "Clock-controlled drive"),
    ]

    sy = sp_y1 + 70
    for lbl, val in specs:
        draw.text((sp_x1 + 22, sy), lbl, font=font_card_bold, fill=CYAN_SOFT)
        draw.text((sp_x1 + 225, sy), val, font=font_card_body, fill=CYAN_PALE)
        sy += 38

    # --- Bottom Summary Strip (3 Shortened, Punchy Takeaway Cards) ---
    b_y1 = 1060
    b_y2 = 1215
    col_w = (W - 120 - 40) // 3

    takeaways = [
        {
            "num": "1",
            "title": "PHYSICAL SCALE (15 FT)",
            "lines": [
                "A 15-ft focal length gave a plate scale of",
                "≈45″/mm. A 1.75″ limb deflection",
                "corresponded to ≈39 μm on the plate.",
            ],
            "accent": CYAN_BRIGHT,
            "hdr_fill": (3, 105, 161, 255),
        },
        {
            "num": "2",
            "title": "TWIN CAMERA PAIR",
            "lines": [
                "Two parallel cameras photographed the same",
                "field simultaneously, producing independent",
                "plates at the same image scale.",
            ],
            "accent": CYAN_DEEP,
            "hdr_fill": (2, 132, 199, 255),
        },
        {
            "num": "3",
            "title": "REAL-TIME GUIDING",
            "lines": [
                "Trumpler kept a guide star on the cross wire,",
                "correcting small clock-drive errors during",
                "each exposure.",
            ],
            "accent": MINT_BRIGHT,
            "hdr_fill": MINT_DEEP,
        },
    ]

    for idx, item in enumerate(takeaways):
        tx1 = 60 + idx * (col_w + 20)
        tx2 = tx1 + col_w
        draw.rounded_rectangle([tx1, b_y1, tx2, b_y2], radius=8, fill=CARD_BG, outline=item["accent"], width=2)
        draw.rounded_rectangle([tx1, b_y1, tx2, b_y1 + 46], radius=8, fill=item["hdr_fill"], outline=item["accent"], width=2)
        
        # Badge number
        draw.rounded_rectangle([tx1 + 12, b_y1 + 8, tx1 + 40, b_y1 + 38], radius=14, fill=CARD_BG, outline=item["accent"], width=2)
        draw.text((tx1 + 20, b_y1 + 10), item["num"], font=font_card_bold, fill=item["accent"])
        draw.text((tx1 + 50, b_y1 + 12), item["title"], font=font_card_title, fill=TEXT_WHITE)
        
        dy = b_y1 + 56
        for dl in item["lines"]:
            draw.text((tx1 + 22, dy), dl, font=font_card_body, fill=TEXT_SLATE)
            dy += 30

    draw.rectangle([0, 0, W - 1, H - 1], outline=CARD_BORDER, width=1)

    img.save(output_path, "PNG", optimize=True)
    print(f"Twin cameras schematic saved to: {output_path} ({W}x{H} px)")

if __name__ == "__main__":
    create_schematic()
