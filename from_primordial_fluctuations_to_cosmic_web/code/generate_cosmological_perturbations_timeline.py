#!/usr/bin/env python3
r"""
Generate editorial timeline for Medium:
"From Jeans to Bardeen: The Development of Cosmological Perturbation Theory"

Figure for Section 1.2 of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design specifications:
- Canvas: 2000 x 760 px (matching the_road_to_modern_dynamics_2 scale).
- Single horizontal chronological spine with alternating milestones above and below.
- Outlined date pills with soft tinted background and color-coded accents.
- High-contrast editorial typography:
  * Surname (36pt bold Navy #0f172a)
  * Year (23pt bold pill)
  * Work / Reference line (27pt prominent slate #334155; italic for publications, roman for topics)
  * Concept line (27pt bold Navy #0f172a)
- Unsplit single-line work titles for Jeans, Friedmann/Lemaître, Milne & McCrea, Gamow & Teller.
- Clean two-line work titles for Lifshitz, Bonnor, Bardeen.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "cosmological_perturbations_timeline.png"

# Color Palette (High-contrast editorial)
BG_COLOR = (255, 255, 255, 255)
NAVY = (15, 23, 42, 255)            # #0f172a (primary names & concepts)
DARK_SLATE = (30, 41, 59, 255)      # #1e293b
PROMINENT_SLATE = (51, 65, 85, 255) # #334155 (work / reference line)
SPINE_COLOR = (203, 213, 225, 255)  # #cbd5e1 (central rail)
TITLE_BG = (248, 250, 252, 255)     # #f8fafc (title badge background)
TITLE_BORDER = (203, 213, 225, 255) # #cbd5e1 (title badge border)

MILESTONES = [
    {
        "id": "jeans",
        "position": "below",
        "name": "Jeans",
        "year": "1902",
        "work": "The Stability of a Spherical Nebula",
        "work_italic": True,
        "concept": "Gravitational Instability in\nSelf-Gravitating Gas",
        "accent": (30, 64, 175),     # Deep Royal Blue (#1e40af)
        "light": (239, 246, 255),    # #eff6ff
    },
    {
        "id": "friedmann_lemaitre",
        "position": "above",
        "name": "Friedmann / Lemaître",
        "year": "1922–1927",
        "work": "On the Curvature of Space\nUn Univers homogène de masse\nconstante et de rayon croissant...",
        "work_italic": True,
        "concept": "Expanding Cosmological\nSolutions",
        "accent": (14, 116, 144),    # Deep Cyan / Teal (#0e7490)
        "light": (236, 254, 255),    # #ecfeff
    },
    {
        "id": "milne_mccrea",
        "position": "below",
        "name": "Milne & McCrea",
        "year": "1934",
        "work": "Newtonian Universes and\nthe Curvature of Space",
        "work_italic": True,
        "concept": "Newtonian Cosmological\nExpansion",
        "accent": (67, 56, 202),     # Deep Indigo (#4338ca)
        "light": (238, 242, 255),    # #eef2ff
    },
    {
        "id": "gamow_teller",
        "position": "above",
        "name": "Gamow & Teller",
        "year": "1939",
        "work": "On the Origin of Great Nebulae",
        "work_italic": True,
        "concept": "Gravitational Instability\nand Galaxy Formation",
        "accent": (109, 40, 217),    # Deep Purple / Violet (#6d28d9)
        "light": (245, 243, 255),    # #f5f3ff
    },
    {
        "id": "lifshitz",
        "position": "below",
        "name": "Lifshitz",
        "year": "1946",
        "work": "On the Gravitational Stability\nof the Expanding Universe",
        "work_italic": True,
        "concept": "Relativistic Cosmological\nPerturbations",
        "accent": (190, 18, 60),     # Deep Crimson / Ruby (#be123c)
        "light": (255, 241, 242),    # #fff1f2
    },
    {
        "id": "bonnor",
        "position": "above",
        "name": "Bonnor",
        "year": "1957",
        "work": "Jeans' Formula for\nGravitational Instability",
        "work_italic": True,
        "concept": "Newtonian Instability Equation\nin an Expanding Universe",
        "accent": (180, 83, 9),      # Warm Amber / Bronze (#b45309)
        "light": (254, 243, 199),    # #fef3c7
    },
    {
        "id": "bardeen",
        "position": "below",
        "name": "Bardeen",
        "year": "1980",
        "work": "Gauge-invariant\nCosmological Perturbations",
        "work_italic": True,
        "concept": "Gauge-Invariant Relativistic\nPerturbation Theory",
        "accent": (4, 120, 87),      # Deep Emerald (#047857)
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

    # Canvas dimensions: 2000 x 760 px
    # Spacious proportions ensure large 27pt descriptions fit comfortably with >100px gaps.
    W, H = 2000, 760
    img = Image.new('RGBA', (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Typography
    font_title = get_font(33, bold=True)
    font_name = get_font(36, bold=True)
    font_year = get_font(23, bold=True)
    font_work_italic = get_font(27, italic=True)
    font_work_roman = get_font(27, bold=False)
    font_concept = get_font(27, bold=True)

    # 1. Title in Editorial Badge Box
    title_text = "From Jeans to Bardeen: The Development of Cosmological Perturbation Theory"
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    tw = title_bbox[2] - title_bbox[0]
    th = title_bbox[3] - title_bbox[1]

    pad_x = 28
    pad_y = 11
    bw = tw + 2 * pad_x
    bh = th + 2 * pad_y
    bx = (W - bw) // 2
    by = 22

    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=TITLE_BG, outline=TITLE_BORDER, width=2)
    draw.text((bx + pad_x, by + pad_y - 2), title_text, font=font_title, fill=NAVY)

    # 2. Timeline Axis Geometry
    spine_y = 422
    start_x = 245
    end_x = 1755
    step_x = (end_x - start_x) / (len(MILESTONES) - 1)  # ~251.7 px between milestones

    # Draw continuous horizontal rail
    draw.line([(start_x - 65, spine_y), (end_x + 65, spine_y)], fill=SPINE_COLOR, width=5)

    # Terminal arrow pointing right
    draw.polygon([
        (end_x + 85, spine_y),
        (end_x + 65, spine_y - 8),
        (end_x + 65, spine_y + 8)
    ], fill=(100, 116, 139, 255))

    # Render each milestone
    for i, m in enumerate(MILESTONES):
        cx = start_x + i * step_x
        accent = m["accent"]
        is_above = (m["position"] == "above")

        # Spine Node (Circle with colored core)
        draw.ellipse([cx - 12, spine_y - 12, cx + 12, spine_y + 12],
                     fill=(255, 255, 255, 255), outline=accent + (255,), width=4)
        draw.ellipse([cx - 5, spine_y - 5, cx + 5, spine_y + 5],
                     fill=accent + (255,))

        font_ref = font_work_italic if m["work_italic"] else font_work_roman

        if is_above:
            # UPPER MILESTONE (Friedmann / Lemaître, Gamow & Teller, Bonnor)
            # Layout starts at y = 112, below title badge
            cur_y = 112

            # Surname
            n_bbox = draw.textbbox((0, 0), m["name"], font=font_name)
            n_w = n_bbox[2] - n_bbox[0]
            draw.text((cx - n_w / 2, cur_y), m["name"], font=font_name, fill=NAVY)
            cur_y += 46

            # Year badge pill
            y_bbox = draw.textbbox((0, 0), m["year"], font=font_year)
            y_w = y_bbox[2] - y_bbox[0] + 24
            y_h = 30
            y_left = cx - y_w / 2
            draw.rounded_rectangle([y_left, cur_y, y_left + y_w, cur_y + y_h],
                                   radius=15, fill=m["light"] + (255,), outline=accent + (220,), width=2)
            draw.text((y_left + 12, cur_y + 3), m["year"], font=font_year, fill=accent + (255,))
            cur_y += 42

            # Work title / Topic line (single or multiline)
            work_lines = m["work"].split("\n")
            for w_idx, w_line in enumerate(work_lines):
                w_bbox = draw.textbbox((0, 0), w_line, font=font_ref)
                w_w = w_bbox[2] - w_bbox[0]
                draw.text((cx - w_w / 2, cur_y), w_line, font=font_ref, fill=PROMINENT_SLATE)
                if m.get("id") == "friedmann_lemaitre" and w_idx == 0:
                    cur_y += 35  # Distinct visual separation between Friedmann (1922) and Lemaître (1927)
                else:
                    cur_y += 30 if w_idx < len(work_lines) - 1 else 36

            # Concept lines
            concept_lines = m["concept"].split("\n")
            for c_idx, c_line in enumerate(concept_lines):
                c_bbox = draw.textbbox((0, 0), c_line, font=font_concept)
                c_w = c_bbox[2] - c_bbox[0]
                draw.text((cx - c_w / 2, cur_y), c_line, font=font_concept, fill=NAVY)
                cur_y += 31 if c_idx < len(concept_lines) - 1 else 32

            # Vertical stem line from bottom of text cluster down to spine node
            stem_top = cur_y + 10
            draw.line([(cx, stem_top), (cx, spine_y - 12)], fill=accent + (255,), width=3)
            # Anchor dot at top of stem
            draw.ellipse([cx - 4, stem_top - 4, cx + 4, stem_top + 4], fill=accent + (255,))

        else:
            # LOWER MILESTONE (Jeans, Milne & McCrea, Lifshitz, Bardeen)
            stem_bot = spine_y + 44
            draw.line([(cx, spine_y + 12), (cx, stem_bot)], fill=accent + (255,), width=3)
            # Anchor dot at bottom of stem
            draw.ellipse([cx - 4, stem_bot - 4, cx + 4, stem_bot + 4], fill=accent + (255,))

            # Text content stacked below stem
            cur_y = stem_bot + 16

            # Surname
            n_bbox = draw.textbbox((0, 0), m["name"], font=font_name)
            n_w = n_bbox[2] - n_bbox[0]
            draw.text((cx - n_w / 2, cur_y), m["name"], font=font_name, fill=NAVY)
            cur_y += 46

            # Year badge pill
            y_bbox = draw.textbbox((0, 0), m["year"], font=font_year)
            y_w = y_bbox[2] - y_bbox[0] + 24
            y_h = 30
            y_left = cx - y_w / 2
            draw.rounded_rectangle([y_left, cur_y, y_left + y_w, cur_y + y_h],
                                   radius=15, fill=m["light"] + (255,), outline=accent + (220,), width=2)
            draw.text((y_left + 12, cur_y + 3), m["year"], font=font_year, fill=accent + (255,))
            cur_y += 42

            # Work title / Topic line (single or multiline)
            work_lines = m["work"].split("\n")
            for w_idx, w_line in enumerate(work_lines):
                w_bbox = draw.textbbox((0, 0), w_line, font=font_ref)
                w_w = w_bbox[2] - w_bbox[0]
                draw.text((cx - w_w / 2, cur_y), w_line, font=font_ref, fill=PROMINENT_SLATE)
                if m.get("id") == "friedmann_lemaitre" and w_idx == 0:
                    cur_y += 35  # Distinct visual separation between Friedmann (1922) and Lemaître (1927)
                else:
                    cur_y += 30 if w_idx < len(work_lines) - 1 else 36

            # Concept lines
            concept_lines = m["concept"].split("\n")
            for c_idx, c_line in enumerate(concept_lines):
                c_bbox = draw.textbbox((0, 0), c_line, font=font_concept)
                c_w = c_bbox[2] - c_bbox[0]
                draw.text((cx - c_w / 2, cur_y), c_line, font=font_concept, fill=NAVY)
                cur_y += 31 if c_idx < len(concept_lines) - 1 else 32

    # Subtle outer framing border
    draw.rectangle([0, 0, W - 1, H - 1], outline=(226, 232, 240, 255), width=1)

    img.save(output_path, "PNG", optimize=True)
    print(f"Refined timeline saved to: {output_path} ({W}x{H} px)")

    # Mirror to public repo if it exists


if __name__ == "__main__":
    create_timeline()
