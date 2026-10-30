#!/usr/bin/env python3
r"""
Generate timeline for Medium:
"From Poincaré to Chaos: A Timeline of Dynamical Systems"
Matching the design and visual language of Part I:
the_road_to_modern_dynamics/images/mechanics_conceptual_timeline.png

Features:
- Title styled in an editorial rounded badge box (fill #f8fafc, border #cbd5e1).
- Single horizontal chronological axis with alternating milestones above and below.
- Outlined date capsules with color-coded accents and soft tinted backgrounds.
- High-contrast navy and slate typography matching Part I:
  * Surname (36pt bold Navy #0f172a)
  * Year (23pt bold pill)
  * Work / Reference line (22pt slate #334155; italic for works, roman for topics)
  * Concept line (22pt bold Navy #0f172a)
- Restrained, cohesive editorial palette with visual distinction between Lorenz & Smale.
- Canvas: 1920 x 680 px for 8 milestones with perfectly uniform 4-line stacks and balanced spacing.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "dynamical_systems_timeline.png"

# Color Palette (High-contrast editorial)
BG_COLOR = (255, 255, 255, 255)
NAVY = (15, 23, 42, 255)            # #0f172a (primary names & concepts)
DARK_SLATE = (30, 41, 59, 255)      # #1e293b
PROMINENT_SLATE = (51, 65, 85, 255) # #334155 (high-contrast work/topic line)
SPINE_COLOR = (203, 213, 225, 255)  # #cbd5e1 (rail)
TITLE_BG = (248, 250, 252, 255)     # #f8fafc (editorial title badge background)
TITLE_BORDER = (203, 213, 225, 255) # #cbd5e1 (editorial title badge border)

MILESTONES = [
    {
        "id": "poincare_1",
        "position": "above",
        "name": "Poincaré",
        "year": "1881–1886",
        "work": "On Curves Defined by\nDifferential Equations",
        "work_italic": True,
        "concept": "Qualitative Theory",
        "accent": (225, 29, 72),     # Rose / Crimson (#e11d48)
        "light": (255, 241, 242),    # #fff1f2
    },
    {
        "id": "poincare_2",
        "position": "below",
        "name": "Poincaré",
        "year": "1890",
        "work": "On the Three-Body Problem\nand the Equations of Dynamics",
        "work_italic": True,
        "concept": "Homoclinic Geometry",
        "accent": (190, 18, 60),     # Deep Crimson (#be123c - matches Part 1)
        "light": (255, 241, 242),    # #fff1f2
    },
    {
        "id": "lyapunov",
        "position": "above",
        "name": "Lyapunov",
        "year": "1892",
        "work": "The General Problem of\nthe Stability of Motion",
        "work_italic": True,
        "concept": "Stability Theory",
        "accent": (29, 78, 216),     # Royal Blue (#1d4ed8)
        "light": (239, 246, 255),    # #eff6ff
    },
    {
        "id": "bendixson",
        "position": "below",
        "name": "Bendixson",
        "year": "1901",
        "work": "On Curves Defined by\nDifferential Equations",
        "work_italic": True,
        "concept": "Planar Dynamics",
        "accent": (14, 116, 144),    # Deep Cyan / Teal (#0e7490)
        "light": (236, 254, 255),    # #ecfeff
    },
    {
        "id": "birkhoff_1",
        "position": "above",
        "name": "Birkhoff",
        "year": "1913",
        "work": "Proof of Poincaré's\nGeometric Theorem",
        "work_italic": True,
        "concept": "Existence of Periodic Orbits",
        "accent": (67, 56, 202),     # Deep Indigo (#4338ca)
        "light": (238, 242, 255),    # #eef2ff
    },
    {
        "id": "birkhoff_2",
        "position": "below",
        "name": "Birkhoff",
        "year": "1927",
        "work": "Dynamical Systems",
        "work_italic": True,
        "concept": "Theory of Dynamical Systems",
        "accent": (109, 40, 217),    # Deep Purple (#6d28d9)
        "light": (245, 243, 255),    # #f5f3ff
    },
    {
        "id": "lorenz",
        "position": "above",
        "name": "Lorenz",
        "year": "1963",
        "work": "Deterministic Nonperiodic Flow",
        "work_italic": True,
        "concept": "Sensitive Dependence",
        "accent": (194, 65, 12),     # Burnt Orange (#c2410c - numerical/thermal)
        "light": (255, 247, 237),    # #fff7ed
    },
    {
        "id": "smale",
        "position": "below",
        "name": "Smale",
        "year": "1965–1967",
        "work": "Horseshoe & homoclinic theorem",
        "work_italic": False,
        "concept": "Geometric Foundations of Chaos",
        "accent": (4, 120, 87),      # Deep Emerald (#047857 - topological)
        "light": (236, 253, 245),    # #ecfdf5
    },
]

def get_font(size, bold=False, italic=False):
    """Load robust system fonts."""
    if bold:
        paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    elif italic:
        paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        ]
    else:
        paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def create_timeline(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Canvas dimensions: 1920 x 680 px for 8 milestones
    W, H = 1920, 680
    img = Image.new('RGBA', (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # High-legibility typography matching Part I
    font_title = get_font(33, bold=True)
    font_name = get_font(36, bold=True)
    font_year = get_font(23, bold=True)
    font_work_italic = get_font(22, italic=True)
    font_work_roman = get_font(22, bold=False)
    font_concept = get_font(22, bold=True)

    # 1. Title in Editorial Badge Box (#f8fafc with #cbd5e1 border)
    title_text = "From Poincaré to Chaos: A Timeline of Dynamical Systems"
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    tw = title_bbox[2] - title_bbox[0]
    th = title_bbox[3] - title_bbox[1]
    
    pad_x = 26
    pad_y = 11
    bw = tw + 2 * pad_x
    bh = th + 2 * pad_y
    bx = (W - bw) // 2
    by = 28

    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=TITLE_BG, outline=TITLE_BORDER, width=2)
    draw.text((bx + pad_x, by + pad_y - 2), title_text, font=font_title, fill=NAVY)

    # 2. Timeline Axis Geometry
    spine_y = 392
    start_x = 180
    end_x = 1720
    step_x = (end_x - start_x) / 7  # 7 intervals for 8 milestones (220 px)

    # Draw continuous horizontal rail
    draw.line([(start_x - 60, spine_y), (end_x + 60, spine_y)], fill=SPINE_COLOR, width=5)

    # Terminal arrow pointing right
    draw.polygon([
        (end_x + 80, spine_y),
        (end_x + 60, spine_y - 8),
        (end_x + 60, spine_y + 8)
    ], fill=(100, 116, 139, 255))

    # Render each milestone
    for i, m in enumerate(MILESTONES):
        cx = start_x + i * step_x
        accent = m["accent"]
        is_above = (m["position"] == "above")

        # Spine Node (Circle with colored core)
        draw.ellipse([cx - 12, spine_y - 12, cx + 12, spine_y + 12], fill=(255, 255, 255, 255), outline=accent + (255,), width=4)
        draw.ellipse([cx - 5, spine_y - 5, cx + 5, spine_y + 5], fill=accent + (255,))

        # Choose font for the reference/work line
        font_ref = font_work_italic if m["work_italic"] else font_work_roman

        if is_above:
            # UPPER MILESTONE (Poincaré 1881, Lyapunov 1892, Birkhoff 1913, Lorenz 1963)
            cur_y = 132

            # Surname (36pt bold Navy)
            n_bbox = draw.textbbox((0, 0), m["name"], font=font_name)
            n_w = n_bbox[2] - n_bbox[0]
            draw.text((cx - n_w / 2, cur_y), m["name"], font=font_name, fill=NAVY)
            cur_y += 44

            # Year badge pill (23pt bold)
            y_bbox = draw.textbbox((0, 0), m["year"], font=font_year)
            y_w = y_bbox[2] - y_bbox[0] + 24
            y_h = 30
            y_left = cx - y_w / 2
            draw.rounded_rectangle([y_left, cur_y, y_left + y_w, cur_y + y_h], radius=15, fill=m["light"] + (255,), outline=accent + (220,), width=2)
            draw.text((y_left + 12, cur_y + 3), m["year"], font=font_year, fill=accent + (255,))
            cur_y += 40

            # Work title / Topic line (single or multiline)
            work_lines = m["work"].split("\n")
            for w_idx, w_line in enumerate(work_lines):
                w_bbox = draw.textbbox((0, 0), w_line, font=font_ref)
                w_w = w_bbox[2] - w_bbox[0]
                draw.text((cx - w_w / 2, cur_y), w_line, font=font_ref, fill=PROMINENT_SLATE)
                cur_y += 28 if w_idx < len(work_lines) - 1 else 34

            # Concept line (22pt bold NAVY #0f172a)
            c_bbox = draw.textbbox((0, 0), m["concept"], font=font_concept)
            c_w = c_bbox[2] - c_bbox[0]
            draw.text((cx - c_w / 2, cur_y), m["concept"], font=font_concept, fill=NAVY)
            cur_y += 30

            # Vertical stem line from bottom of text cluster down to spine node
            stem_top = cur_y + 12
            draw.line([(cx, stem_top), (cx, spine_y - 12)], fill=accent + (255,), width=3)
            # Anchor dot at top of stem
            draw.ellipse([cx - 4, stem_top - 4, cx + 4, stem_top + 4], fill=accent + (255,))

        else:
            # LOWER MILESTONE (Poincaré 1890, Bendixson 1901, Birkhoff 1927, Smale 1965–1967)
            stem_bot = spine_y + 45
            draw.line([(cx, spine_y + 12), (cx, stem_bot)], fill=accent + (255,), width=3)
            # Anchor dot at bottom of stem
            draw.ellipse([cx - 4, stem_bot - 4, cx + 4, stem_bot + 4], fill=accent + (255,))

            # Text content stacked below stem
            cur_y = stem_bot + 16

            # Surname (36pt bold Navy)
            n_bbox = draw.textbbox((0, 0), m["name"], font=font_name)
            n_w = n_bbox[2] - n_bbox[0]
            draw.text((cx - n_w / 2, cur_y), m["name"], font=font_name, fill=NAVY)
            cur_y += 44

            # Year badge pill (23pt bold)
            y_bbox = draw.textbbox((0, 0), m["year"], font=font_year)
            y_w = y_bbox[2] - y_bbox[0] + 24
            y_h = 30
            y_left = cx - y_w / 2
            draw.rounded_rectangle([y_left, cur_y, y_left + y_w, cur_y + y_h], radius=15, fill=m["light"] + (255,), outline=accent + (220,), width=2)
            draw.text((y_left + 12, cur_y + 3), m["year"], font=font_year, fill=accent + (255,))
            cur_y += 40

            # Work title / Topic line (single or multiline)
            work_lines = m["work"].split("\n")
            for w_idx, w_line in enumerate(work_lines):
                w_bbox = draw.textbbox((0, 0), w_line, font=font_ref)
                w_w = w_bbox[2] - w_bbox[0]
                draw.text((cx - w_w / 2, cur_y), w_line, font=font_ref, fill=PROMINENT_SLATE)
                cur_y += 28 if w_idx < len(work_lines) - 1 else 34

            # Concept line (22pt bold NAVY #0f172a)
            c_bbox = draw.textbbox((0, 0), m["concept"], font=font_concept)
            c_w = c_bbox[2] - c_bbox[0]
            draw.text((cx - c_w / 2, cur_y), m["concept"], font=font_concept, fill=NAVY)
            cur_y += 30

    # Subtle outer framing border
    draw.rectangle([0, 0, W - 1, H - 1], outline=(226, 232, 240, 255), width=1)

    img.save(output_path, "PNG", optimize=True)
    print(f"Dynamical systems timeline saved to: {output_path} ({W}x{H} px)")

if __name__ == "__main__":
    create_timeline()
