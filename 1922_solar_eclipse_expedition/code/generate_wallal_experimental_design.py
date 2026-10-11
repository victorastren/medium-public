#!/usr/bin/env python3
r"""
Create experimental design schematic for Medium:
"Experimental Design of the Wallal Astrometric Test (1922)"

Designed to accompany the section "Preparing the Wallal Experiment".
Color Palette: Cosmic Dark Slate (#0b0f19) matching the article's
scientific diagrams (deflection_predictions_comparison & light_deflection_geometry).
Visualizes the two separate comparisons:
1. Tahiti reference field vs. Wallal eclipse field (measures gravitational deflection)
2. Wallal check field (tests whether comparable shifts arise from instrumental systematics)
"""

from pathlib import Path
import random
import math
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "wallal_experimental_design.png"

# Color Palette: Cosmic Dark Slate (#0b0f19) matching other scientific diagrams
BG_COLOR = (11, 15, 25, 255)         # #0b0f19
CARD_BG = (15, 23, 42, 255)          # #0f172a (deep midnight slate)
HEADER_BG = (30, 41, 59, 255)        # #1e293b
HEADER_BORDER = (71, 85, 105, 255)   # #475569
TEXT_WHITE = (255, 255, 255, 255)    # #ffffff
TEXT_MUTED = (203, 213, 225, 255)    # #cbd5e1
BORDER_SUBTLE = (51, 65, 85, 255)    # #334155

# Tahiti Accent: Cyan / Sky Blue
CYAN_ACCENT = (56, 189, 248, 255)    # #38bdf8
CYAN_DARK = (3, 105, 161, 255)       # #0369a1
CYAN_LIGHT = (186, 230, 253, 255)    # #bae6fd
CYAN_BORDER = (2, 132, 199, 255)     # #0284c7

# Wallal Eclipse Accent: Mint / Emerald Green
MINT_ACCENT = (52, 211, 153, 255)    # #34d399
MINT_DARK = (6, 95, 70, 255)         # #065f46
MINT_LIGHT = (167, 243, 208, 255)    # #a7f3d0
MINT_BORDER = (5, 150, 105, 255)     # #059669

# Check Field Accent: Lavender / Indigo
INDIGO_ACCENT = (165, 180, 252, 255) # #a5b4fc
INDIGO_DARK = (55, 48, 163, 255)     # #3730a3
INDIGO_LIGHT = (199, 210, 254, 255)  # #c7d2fe
INDIGO_BORDER = (99, 102, 241, 255)  # #6366f1

def get_font(size, bold=False, italic=False):
    """Load robust system fonts with full Unicode math glyph support (DejaVuSans first)."""
    if bold:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    elif italic:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        ]
    else:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def draw_star(draw, cx, cy, r=3, color=(255, 255, 255, 255)):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

def create_schematic(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Canvas dimensions: 2040 x 1130 px (Spacious height to completely eliminate vertical clipping)
    W, H = 2040, 1130
    img = Image.new('RGBA', (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Background subtle starfield matching other diagrams
    random.seed(101)
    for _ in range(130):
        sx = random.randint(10, W - 10)
        sy = random.randint(10, H - 10)
        if (35 <= sx <= 2005) and (95 <= sy <= 1105):
            continue
        sr = random.choice([1, 2, 2, 3])
        s_alpha = random.randint(35, 110)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255, s_alpha))

    # High-legibility typography
    font_main_title = get_font(39, bold=True)
    font_card_title = get_font(32, bold=True)
    font_badge = get_font(23, bold=True)
    font_body_bold = get_font(25, bold=True)
    font_body = get_font(25, bold=False)
    font_banner_title = get_font(26, bold=True)
    font_banner_title_r = get_font(23, bold=True)
    font_banner_body_l = get_font(25.5, bold=False)
    font_banner_body_r = get_font(23, bold=False)
    font_mini_label = get_font(21.5, bold=True)
    font_comp_arrow = get_font(16.5, bold=True)

    # 1. Main Title Badge Box at top
    title_text = "Experimental Design of the Wallal Astrometric Test (1922)"
    tb = draw.textbbox((0, 0), title_text, font=font_main_title)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]
    pad_x, pad_y = 32, 10
    bw = tw + 2 * pad_x
    bh = th + 2 * pad_y
    bx = (W - bw) // 2
    by = 22

    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=HEADER_BG, outline=HEADER_BORDER, width=2)
    draw.text((bx + pad_x, by + pad_y - 2), title_text, font=font_main_title, fill=TEXT_WHITE)

    # 2. Main 3 Column Cards (Height increased to 660px for ample vertical clearance)
    card_top = 110
    card_bottom = 770

    # Layout geometry:
    # Card 1 (Tahiti): 40 to 620 (w = 580)
    # Connector Gap: 620 to 760 (w = 140)
    # Card 2 (Wallal): 760 to 1340 (w = 580)
    # Divider Gap: 1340 to 1400 (w = 60)
    # Card 3 (Check): 1400 to 2000 (w = 600)

    c1_x1, c1_x2 = 40, 620
    c2_x1, c2_x2 = 760, 1340
    c3_x1, c3_x2 = 1400, 2000

    disc_r = 56
    disc_cy = card_top + 175

    star_offsets = [(-38, -28), (-22, 18), (32, -32), (38, 16), (-10, -42), (14, 35), (-42, 0), (26, -8), (-5, 10)]

    # ================= CARD 1: TAHITI REFERENCE FIELD =================
    draw.rounded_rectangle([c1_x1, card_top, c1_x2, card_bottom], radius=12, fill=CARD_BG, outline=CYAN_BORDER, width=2)
    c1_cx = (c1_x1 + c1_x2) // 2

    # Title
    t1 = "Tahiti Reference Field"
    t1_bb = draw.textbbox((0, 0), t1, font=font_card_title)
    draw.text((c1_cx - (t1_bb[2] - t1_bb[0]) // 2, card_top + 18), t1, font=font_card_title, fill=TEXT_WHITE)

    # Pill badge: "Reference field · May 1922"
    b1 = "Reference field · May 1922"
    b1_bb = draw.textbbox((0, 0), b1, font=font_badge)
    b1_w = b1_bb[2] - b1_bb[0] + 28
    draw.rounded_rectangle([c1_cx - b1_w // 2, card_top + 62, c1_cx + b1_w // 2, card_top + 96], radius=17, fill=CYAN_DARK, outline=CYAN_ACCENT, width=2)
    draw.text((c1_cx - (b1_bb[2] - b1_bb[0]) // 2, card_top + 67), b1, font=font_badge, fill=CYAN_LIGHT)

    # Telescope circle illustration
    draw.ellipse([c1_cx - disc_r, disc_cy - disc_r, c1_cx + disc_r, disc_cy + disc_r], fill=(7, 10, 19, 255), outline=CYAN_ACCENT, width=3)
    # Star pattern (unperturbed night sky)
    for ox, oy in star_offsets:
        draw_star(draw, c1_cx + ox, disc_cy + oy, r=3, color=(255, 255, 255, 255))
    draw_star(draw, c1_cx + 38, disc_cy + 16, r=4, color=(254, 240, 138, 255))
    draw_star(draw, c1_cx - 38, disc_cy - 28, r=4, color=(254, 240, 138, 255))

    cap1 = "Sun far from field · Night observation"
    c1_bb = draw.textbbox((0, 0), cap1, font=font_mini_label)
    draw.text((c1_cx - (c1_bb[2] - c1_bb[0]) // 2, disc_cy + disc_r + 10), cap1, font=font_mini_label, fill=CYAN_ACCENT)

    # Separator inside card
    draw.line([(c1_x1 + 35, card_top + 288), (c1_x2 - 35, card_top + 288)], fill=BORDER_SUBTLE, width=1)

    # Bullets with perfectly aligned hanging indent
    # Bullet dot at c1_x1 + 30. Line 1 starts at c1_x1 + 54. Continuation line 2 ALSO starts at c1_x1 + 54!
    cur_y = card_top + 316
    c1_bullets = [
        ("Target: ", "Same stars as the", "eclipse field"),
        ("Timing: ", "Night observations", "in May 1922"),
        ("Control: ", "Similar latitude; matched", "hour angle, zenith dist., and temp."),
        ("Reference: ", "Stellar positions with", "negligible solar deflection"),
    ]
    for lbl, l1, l2 in c1_bullets:
        draw.ellipse([c1_x1 + 30, cur_y + 8, c1_x1 + 38, cur_y + 16], fill=CYAN_ACCENT)
        draw.text((c1_x1 + 54, cur_y), lbl, font=font_body_bold, fill=TEXT_WHITE)
        w_lbl = draw.textbbox((0, 0), lbl, font=font_body_bold)[2]
        draw.text((c1_x1 + 54 + w_lbl, cur_y), l1, font=font_body, fill=TEXT_MUTED)
        draw.text((c1_x1 + 54, cur_y + 30), l2, font=font_body, fill=TEXT_MUTED)
        cur_y += 72

    # ================= CONNECTOR BETWEEN 1 & 2 =================
    arr_cx = (c1_x2 + c2_x1) // 2  # 690
    arr_cy = disc_cy

    draw.line([(c1_x2 + 3, arr_cy), (c1_x2 + 13, arr_cy)], fill=MINT_ACCENT, width=4)
    draw.line([(c2_x1 - 13, arr_cy), (c2_x1 - 3, arr_cy)], fill=MINT_ACCENT, width=4)
    draw.polygon([(c2_x1 - 3, arr_cy), (c2_x1 - 13, arr_cy - 7), (c2_x1 - 13, arr_cy + 7)], fill=MINT_ACCENT)
    draw.polygon([(c1_x2 + 3, arr_cy), (c1_x2 + 13, arr_cy - 7), (c1_x2 + 13, arr_cy + 7)], fill=MINT_ACCENT)

    arr_text = "COMPARED"
    arr_text2 = "WITH"
    at1_bb = draw.textbbox((0, 0), arr_text, font=font_comp_arrow)
    at2_bb = draw.textbbox((0, 0), arr_text2, font=font_comp_arrow)
    box_w = 114
    box_h = 52
    draw.rounded_rectangle([arr_cx - box_w // 2, arr_cy - box_h // 2, arr_cx + box_w // 2, arr_cy + box_h // 2], radius=10, fill=HEADER_BG, outline=MINT_ACCENT, width=2)
    draw.text((arr_cx - (at1_bb[2] - at1_bb[0]) // 2, arr_cy - 19), arr_text, font=font_comp_arrow, fill=MINT_ACCENT)
    draw.text((arr_cx - (at2_bb[2] - at2_bb[0]) // 2, arr_cy + 2), arr_text2, font=font_comp_arrow, fill=MINT_ACCENT)

    # ================= CARD 2: WALLAL ECLIPSE FIELD =================
    c2_x1, c2_x2 = 760, 1340
    draw.rounded_rectangle([c2_x1, card_top, c2_x2, card_bottom], radius=12, fill=CARD_BG, outline=MINT_BORDER, width=2)
    c2_cx = (c2_x1 + c2_x2) // 2

    # Title
    t2 = "Wallal Eclipse Field"
    t2_bb = draw.textbbox((0, 0), t2, font=font_card_title)
    draw.text((c2_cx - (t2_bb[2] - t2_bb[0]) // 2, card_top + 18), t2, font=font_card_title, fill=TEXT_WHITE)

    # Pill badge
    b2 = "Totality Sky · 21 Sept 1922"
    b2_bb = draw.textbbox((0, 0), b2, font=font_badge)
    b2_w = b2_bb[2] - b2_bb[0] + 28
    draw.rounded_rectangle([c2_cx - b2_w // 2, card_top + 62, c2_cx + b2_w // 2, card_top + 96], radius=17, fill=MINT_DARK, outline=MINT_ACCENT, width=2)
    draw.text((c2_cx - (b2_bb[2] - b2_bb[0]) // 2, card_top + 67), b2, font=font_badge, fill=MINT_LIGHT)

    # Telescope circle illustration
    draw.ellipse([c2_cx - disc_r, disc_cy - disc_r, c2_cx + disc_r, disc_cy + disc_r], fill=(7, 10, 19, 255), outline=MINT_ACCENT, width=3)
    # Eclipsed Sun in center
    for cr in range(29, 16, -2):
        alpha = int(90 * (1 - (cr - 16) / 13))
        draw.ellipse([c2_cx - cr, disc_cy - cr, c2_cx + cr, disc_cy + cr], outline=(251, 191, 36, alpha), width=2)
    draw.ellipse([c2_cx - 16, disc_cy - 16, c2_cx + 16, disc_cy + 16], fill=(0, 0, 0, 255), outline=(251, 191, 36, 255), width=2)

    # Radial deflection vectors
    for ox, oy in star_offsets:
        dist = math.hypot(ox, oy)
        if dist > 20:
            scale_out = 1.0 + (11.0 / dist)
            sx = int(ox * scale_out)
            sy = int(oy * scale_out)
            draw.line([(c2_cx + ox, disc_cy + oy), (c2_cx + sx, disc_cy + sy)], fill=(248, 113, 113, 230), width=2)
            draw_star(draw, c2_cx + sx, disc_cy + sy, r=3, color=(254, 240, 138, 255))
        else:
            draw_star(draw, c2_cx + ox, disc_cy + oy, r=3, color=(255, 255, 255, 255))

    cap2 = "Sun Present · Outward Shift (δθ)"
    c2_bb = draw.textbbox((0, 0), cap2, font=font_mini_label)
    draw.text((c2_cx - (c2_bb[2] - c2_bb[0]) // 2, disc_cy + disc_r + 10), cap2, font=font_mini_label, fill=MINT_ACCENT)

    # Separator inside card
    draw.line([(c2_x1 + 35, card_top + 288), (c2_x2 - 35, card_top + 288)], fill=BORDER_SUBTLE, width=1)

    # Bullets with perfectly aligned hanging indent
    cur_y = card_top + 316
    c2_bullets = [
        ("Target: ", "Same stars surrounding", "the Sun observed during totality"),
        ("Timing: ", "Totality on 21 Sept 1922", "(duration > 5 minutes)"),
        ("Cameras: ", "15-foot and 5-foot", "twin camera pairs"),
        ("Deflection: ", "Gravitational shift +", "instrumental systematics"),
    ]
    for lbl, l1, l2 in c2_bullets:
        draw.ellipse([c2_x1 + 30, cur_y + 8, c2_x1 + 38, cur_y + 16], fill=MINT_ACCENT)
        draw.text((c2_x1 + 54, cur_y), lbl, font=font_body_bold, fill=TEXT_WHITE)
        w_lbl = draw.textbbox((0, 0), lbl, font=font_body_bold)[2]
        draw.text((c2_x1 + 54 + w_lbl, cur_y), l1, font=font_body, fill=TEXT_MUTED)
        draw.text((c2_x1 + 54, cur_y + 30), l2, font=font_body, fill=TEXT_MUTED)
        cur_y += 72

    # ================= VERTICAL DIVIDER BETWEEN 2 & 3 =================
    div_x = (c2_x2 + c3_x1) // 2
    for dy in range(card_top + 20, card_bottom - 20, 16):
        draw.line([(div_x, dy), (div_x, dy + 8)], fill=BORDER_SUBTLE, width=3)

    # ================= CARD 3: CHECK FIELD =================
    c3_x1, c3_x2 = 1400, 2000
    draw.rounded_rectangle([c3_x1, card_top, c3_x2, card_bottom], radius=12, fill=CARD_BG, outline=INDIGO_BORDER, width=2)
    c3_cx = (c3_x1 + c3_x2) // 2

    # Title
    t3 = "Auxiliary Check Field"
    t3_bb = draw.textbbox((0, 0), t3, font=font_card_title)
    draw.text((c3_cx - (t3_bb[2] - t3_bb[0]) // 2, card_top + 18), t3, font=font_card_title, fill=TEXT_WHITE)

    # Pill badge
    b3 = "Instrumental Control · 21 Sept 1922"
    b3_bb = draw.textbbox((0, 0), b3, font=font_badge)
    b3_w = b3_bb[2] - b3_bb[0] + 28
    draw.rounded_rectangle([c3_cx - b3_w // 2, card_top + 62, c3_cx + b3_w // 2, card_top + 96], radius=17, fill=INDIGO_DARK, outline=INDIGO_ACCENT, width=2)
    draw.text((c3_cx - (b3_bb[2] - b3_bb[0]) // 2, card_top + 67), b3, font=font_badge, fill=INDIGO_LIGHT)

    # Telescope circle illustration
    draw.ellipse([c3_cx - disc_r, disc_cy - disc_r, c3_cx + disc_r, disc_cy + disc_r], fill=(7, 10, 19, 255), outline=INDIGO_ACCENT, width=3)
    # Check star pattern (>90 deg away)
    check_star_offsets = [(-32, -22), (18, -36), (40, 10), (-14, 32), (-36, 18), (26, -8), (0, -14), (10, 22)]
    for ox, oy in check_star_offsets:
        draw_star(draw, c3_cx + ox, disc_cy + oy, r=3, color=(255, 255, 255, 255))
    draw_star(draw, c3_cx - 14, disc_cy + 32, r=4, color=(199, 210, 254, 255))
    draw_star(draw, c3_cx + 40, disc_cy + 10, r=4, color=(199, 210, 254, 255))

    # Refined 2-line label: "More than 90° from the Sun / (negligible solar deflection)"
    cap3_1 = "More than 90° from the Sun"
    cap3_2 = "(negligible solar deflection)"
    c3_bb1 = draw.textbbox((0, 0), cap3_1, font=font_mini_label)
    c3_bb2 = draw.textbbox((0, 0), cap3_2, font=font_mini_label)
    draw.text((c3_cx - (c3_bb1[2] - c3_bb1[0]) // 2, disc_cy + disc_r + 6), cap3_1, font=font_mini_label, fill=INDIGO_ACCENT)
    draw.text((c3_cx - (c3_bb2[2] - c3_bb2[0]) // 2, disc_cy + disc_r + 28), cap3_2, font=font_mini_label, fill=INDIGO_ACCENT)

    # Separator inside card
    draw.line([(c3_x1 + 35, card_top + 288), (c3_x2 - 35, card_top + 288)], fill=BORDER_SUBTLE, width=1)

    # Bullets with perfectly aligned hanging indent
    cur_y = card_top + 316
    c3_bullets = [
        ("Target: ", "Auxiliary check field", "(matched declination)"),
        ("Position: ", "Located > 90° away", "from the eclipsed Sun"),
        ("Plates: ", "Exposed on the same", "photographic plates"),
        ("Control: ", "Tests residual instrumental", "systematics & plate-scale errors"),
    ]
    for lbl, l1, l2 in c3_bullets:
        draw.ellipse([c3_x1 + 30, cur_y + 8, c3_x1 + 38, cur_y + 16], fill=INDIGO_ACCENT)
        draw.text((c3_x1 + 54, cur_y), lbl, font=font_body_bold, fill=TEXT_WHITE)
        w_lbl = draw.textbbox((0, 0), lbl, font=font_body_bold)[2]
        draw.text((c3_x1 + 54 + w_lbl, cur_y), l1, font=font_body, fill=TEXT_MUTED)
        draw.text((c3_x1 + 54, cur_y + 30), l2, font=font_body, fill=TEXT_MUTED)
        cur_y += 72

    # ================= 3. BOTTOM COMPARISON BANNERS (Height increased to 306px) =================
    banner_top = 794
    banner_bottom = 1100

    # BANNER 1 (Under Cards 1 & 2): Measures Gravitational Deflection
    b1_x1, b1_x2 = 40, 1340
    draw.rounded_rectangle([b1_x1, banner_top, b1_x2, banner_bottom], radius=12, fill=CARD_BG, outline=MINT_BORDER, width=2)
    b1_title = "COMPARISON 1: GRAVITATIONAL LIGHT DEFLECTION (EINSTEIN TEST)"
    draw.text((b1_x1 + 30, banner_top + 24), b1_title, font=font_banner_title, fill=MINT_ACCENT)
    
    # Clean hanging indent for Comparison 1
    b1_p1_txt = "Differential displacement: [Wallal Eclipse Field] − [Tahiti Reference Field]"
    b1_p2_txt = "Measures apparent radial displacement predicted by GR:"
    b1_p2_sub = "δθ ∝ 1/b, reaching 1.75″ at the solar limb."

    draw.text((b1_x1 + 30, banner_top + 76), "•", font=font_banner_body_l, fill=TEXT_WHITE)
    draw.text((b1_x1 + 54, banner_top + 76), b1_p1_txt, font=font_banner_body_l, fill=TEXT_WHITE)

    draw.text((b1_x1 + 30, banner_top + 132), "•", font=font_banner_body_l, fill=TEXT_MUTED)
    draw.text((b1_x1 + 54, banner_top + 132), b1_p2_txt, font=font_banner_body_l, fill=TEXT_MUTED)
    draw.text((b1_x1 + 54, banner_top + 178), b1_p2_sub, font=font_banner_body_l, fill=MINT_ACCENT)

    # BANNER 2 (Under Card 3): Measures Instrumental Control
    b2_x1, b2_x2 = 1400, 2000
    draw.rounded_rectangle([b2_x1, banner_top, b2_x2, banner_bottom], radius=12, fill=CARD_BG, outline=INDIGO_BORDER, width=2)
    b2_title = "COMPARISON 2: INSTRUMENTAL CONTROL"
    draw.text((b2_x1 + 30, banner_top + 24), b2_title, font=font_banner_title_r, fill=INDIGO_ACCENT)
    
    # Clean, large bullets with uniform hanging indent and generous vertical padding (no border collisions!)
    b2_bullets = [
        ("Solar deflection negligible at", "> 90° from the Sun.", True),
        ("Tests for systematic distortion from", "camera lenses, plate tilt, or instruments.", False),
        ("Tests whether comparable shifts arise", "from instrumental systematics.", False),
    ]

    cur_by = banner_top + 76
    for l1, l2, is_lead in b2_bullets:
        col = TEXT_WHITE if is_lead else TEXT_MUTED
        draw.text((b2_x1 + 30, cur_by), "•", font=font_banner_body_r, fill=col)
        draw.text((b2_x1 + 54, cur_by), l1, font=font_banner_body_r, fill=col)
        draw.text((b2_x1 + 54, cur_by + 28), l2, font=font_banner_body_r, fill=col)
        cur_by += 68

    # Subtle outer framing border
    draw.rectangle([0, 0, W - 1, H - 1], outline=BORDER_SUBTLE, width=1)

    img.save(output_path, "PNG", optimize=True)
    print(f"Wallal experimental design schematic saved to: {output_path} ({W}x{H} px)")

if __name__ == "__main__":
    create_schematic()
