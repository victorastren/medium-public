#!/usr/bin/env python3
r"""
Generate editorial timeline for Medium:
"From Heath to Accelerating Expansion: The Cosmological Constant and Structure Growth"

Figure for Section "Dark Energy and the Slowing of Structure Growth" of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design specifications:
- Canvas: 2000 x 760 px (matching cosmological_perturbations_timeline,
  primordial_fluctuations_timeline, perturbation_evolution_timeline, and
  cosmic_web_timeline).
- Single horizontal chronological spine with alternating milestones (below/above).
- Outlined date pills with soft tinted background and color-coded accents.
- Exact typographic & semantic hierarchy of previous timelines:
  1. Scientist(s) (bold Navy #0f172a)
  2. Publication year (23pt bold pill)
  3. Original paper title (24pt italic regular Slate #334155)
  4. Principal scientific contribution (26pt bold Navy #0f172a)
- 7 milestones:
  1. Heath (1977) — Below
  2. Steinhardt (1990) — Above
  3. Efstathiou, Sutherland & Maddox (1990) — Below
  4. Lahav, Lilje, Primack & Rees (1991) — Above
  5. Ostriker & Steinhardt (1995) — Below
  6. Riess, Schmidt & High-z Supernova Search Team (1998) — Above
  7. Perlmutter & Supernova Cosmology Project (1999) — Below
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "dark_energy_timeline.png"

# Color Palette (High-contrast editorial)
BG_COLOR = (255, 255, 255, 255)
NAVY = (15, 23, 42, 255)            # #0f172a (primary names & concepts)
DARK_SLATE = (30, 41, 59, 255)      # #1e293b
PROMINENT_SLATE = (51, 65, 85, 255) # #334155 (paper title line)
SPINE_COLOR = (203, 213, 225, 255)  # #cbd5e1 (central rail)
TITLE_BG = (248, 250, 252, 255)     # #f8fafc (title badge background)
TITLE_BORDER = (203, 213, 225, 255) # #cbd5e1 (title badge border)

MILESTONES = [
    {
        "id": "heath",
        "position": "below",
        "name": "Heath",
        "year": "1977",
        "work": "The Growth of Density\nPerturbations in Zero Pressure\nFriedmann–Lemaître Universes",
        "concept": "Background-Dependent Growth\nof Density Perturbations",
        "accent": (30, 64, 175),     # Deep Royal Blue (#1e40af)
        "light": (239, 246, 255),    # #eff6ff
    },
    {
        "id": "steinhardt",
        "position": "above",
        "name": "Steinhardt",
        "year": "1990",
        "work": "Inflation and the Ω-Problem",
        "concept": "Low Matter Density vs\nInflationary Flatness",
        "accent": (14, 116, 144),    # Deep Cyan / Teal (#0e7490)
        "light": (236, 254, 255),    # #ecfeff
    },
    {
        "id": "efstathiou_sutherland_maddox",
        "position": "below",
        "name": "Efstathiou, Sutherland\n& Maddox",
        "year": "1990",
        "work": "The Cosmological Constant\nand Cold Dark Matter",
        "concept": "Flat Low-Density\nΛCDM Cosmology",
        "accent": (109, 40, 217),    # Deep Purple / Violet (#6d28d9)
        "light": (245, 243, 255),    # #f5f3ff
    },
    {
        "id": "lahav_lilje_primack_rees",
        "position": "above",
        "name": "Lahav, Lilje,\nPrimack & Rees",
        "year": "1991",
        "work": "Dynamical Effects of the\nCosmological Constant",
        "concept": "Λ Effects on Structure\nGrowth and Collapse",
        "accent": (67, 56, 202),     # Deep Indigo (#4338ca)
        "light": (238, 242, 255),    # #eef2ff
    },
    {
        "id": "ostriker_steinhardt",
        "position": "below",
        "name": "Ostriker & Steinhardt",
        "year": "1995",
        "work": "The Observational Case for a\nLow-Density Universe with a\nNon-Zero Cosmological Constant",
        "concept": "Pre-Supernova Observational\nCase for Λ",
        "accent": (4, 120, 87),      # Deep Emerald (#047857)
        "light": (236, 253, 245),    # #ecfdf5
    },
    {
        "id": "riess_schmidt_highz",
        "position": "above",
        "name": "Riess, Schmidt & High-z\nSupernova Search Team",
        "year": "1998",
        "work": "Observational Evidence from\nSupernovae for an Accelerating Universe\nand a Cosmological Constant",
        "concept": "Accelerating Expansion from\nType Ia Supernovae",
        "accent": (180, 83, 9),      # Warm Amber / Bronze (#b45309)
        "light": (254, 243, 199),    # #fef3c7
    },
    {
        "id": "perlmutter_scp",
        "position": "below",
        "name": "Perlmutter & Supernova\nCosmology Project",
        "year": "1999",
        "work": "Measurements of Ω and Λ from\n42 High-Redshift Supernovae",
        "concept": "Independent Supernova Evidence\nfor Accelerating Expansion",
        "accent": (190, 18, 60),     # Deep Crimson / Ruby (#be123c)
        "light": (255, 241, 242),    # #fff1f2
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
    W, H = 2000, 760
    img = Image.new('RGBA', (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Typography matching Section 1, 2, 3 & 4 timeline hierarchy
    font_title = get_font(31, bold=True)
    font_name_single = get_font(34, bold=True)
    font_name_multi = get_font(29, bold=True)
    font_year = get_font(23, bold=True)
    font_work = get_font(24, italic=True)
    font_concept = get_font(26, bold=True)

    # 1. Title in Editorial Badge Box
    title_text = "From Heath to Accelerating Expansion: The Cosmological Constant and Structure Growth"
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    tw = title_bbox[2] - title_bbox[0]
    th = title_bbox[3] - title_bbox[1]

    pad_x = 26
    pad_y = 11
    bw = tw + 2 * pad_x
    bh = th + 2 * pad_y
    bx = (W - bw) // 2
    by = 18

    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=TITLE_BG, outline=TITLE_BORDER, width=2)
    draw.text((bx + pad_x, by + pad_y - 2), title_text, font=font_title, fill=NAVY)

    # 2. Timeline Axis Geometry
    spine_y = 434
    start_x = 230
    end_x = 1730
    step_x = (end_x - start_x) / (len(MILESTONES) - 1)  # 250.0 px between milestones

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

        name_lines = m["name"].split("\n")
        f_name = font_name_multi if len(name_lines) > 1 else font_name_single

        if is_above:
            # UPPER MILESTONES (Steinhardt, Lahav et al., Riess & Schmidt et al.)
            work_lines = m["work"].split("\n")
            if len(name_lines) > 1 and len(work_lines) >= 3:
                cur_y = 94
            elif len(name_lines) > 1:
                cur_y = 114
            else:
                cur_y = 144

            # 1. Scientist / Entity
            for n_idx, n_line in enumerate(name_lines):
                n_bbox = draw.textbbox((0, 0), n_line, font=f_name)
                n_w = n_bbox[2] - n_bbox[0]
                draw.text((cx - n_w / 2, cur_y), n_line, font=f_name, fill=NAVY)
                if len(name_lines) > 1:
                    cur_y += 32 if n_idx < len(name_lines) - 1 else 37
                else:
                    cur_y += 44

            # 2. Year badge pill (23pt bold)
            y_bbox = draw.textbbox((0, 0), m["year"], font=font_year)
            y_w = y_bbox[2] - y_bbox[0] + 24
            y_h = 30
            y_left = cx - y_w / 2
            draw.rounded_rectangle([y_left, cur_y, y_left + y_w, cur_y + y_h],
                                   radius=15, fill=m["light"] + (255,), outline=accent + (220,), width=2)
            draw.text((y_left + 12, cur_y + 3), m["year"], font=font_year, fill=accent + (255,))
            cur_y += 38

            # 3. Original Paper Title (24pt italic Slate)
            for w_idx, w_line in enumerate(work_lines):
                w_bbox = draw.textbbox((0, 0), w_line, font=font_work)
                w_w = w_bbox[2] - w_bbox[0]
                draw.text((cx - w_w / 2, cur_y), w_line, font=font_work, fill=PROMINENT_SLATE)
                cur_y += 27 if w_idx < len(work_lines) - 1 else 33

            # 4. Principal Scientific Contribution (26pt bold Navy)
            concept_lines = m["concept"].split("\n")
            for c_idx, c_line in enumerate(concept_lines):
                c_bbox = draw.textbbox((0, 0), c_line, font=font_concept)
                c_w = c_bbox[2] - c_bbox[0]
                draw.text((cx - c_w / 2, cur_y), c_line, font=font_concept, fill=NAVY)
                cur_y += 29 if c_idx < len(concept_lines) - 1 else 30

            # Vertical stem line from bottom of text cluster down to spine node
            stem_top = cur_y + 10
            draw.line([(cx, stem_top), (cx, spine_y - 12)], fill=accent + (255,), width=3)
            # Anchor dot at top of stem
            draw.ellipse([cx - 4, stem_top - 4, cx + 4, stem_top + 4], fill=accent + (255,))

        else:
            # LOWER MILESTONES (Heath, Efstathiou et al., Ostriker & Steinhardt, Perlmutter et al.)
            stem_bot = spine_y + 32
            draw.line([(cx, spine_y + 12), (cx, stem_bot)], fill=accent + (255,), width=3)
            # Anchor dot at bottom of stem
            draw.ellipse([cx - 4, stem_bot - 4, cx + 4, stem_bot + 4], fill=accent + (255,))

            # Text content stacked below stem
            cur_y = stem_bot + 12

            # 1. Scientist / Entity
            for n_idx, n_line in enumerate(name_lines):
                n_bbox = draw.textbbox((0, 0), n_line, font=f_name)
                n_w = n_bbox[2] - n_bbox[0]
                draw.text((cx - n_w / 2, cur_y), n_line, font=f_name, fill=NAVY)
                if len(name_lines) > 1:
                    cur_y += 32 if n_idx < len(name_lines) - 1 else 37
                else:
                    cur_y += 43

            # 2. Year badge pill (23pt bold)
            y_bbox = draw.textbbox((0, 0), m["year"], font=font_year)
            y_w = y_bbox[2] - y_bbox[0] + 24
            y_h = 30
            y_left = cx - y_w / 2
            draw.rounded_rectangle([y_left, cur_y, y_left + y_w, cur_y + y_h],
                                   radius=15, fill=m["light"] + (255,), outline=accent + (220,), width=2)
            draw.text((y_left + 12, cur_y + 3), m["year"], font=font_year, fill=accent + (255,))
            cur_y += 38

            # 3. Original Paper Title (24pt italic Slate)
            work_lines = m["work"].split("\n")
            for w_idx, w_line in enumerate(work_lines):
                w_bbox = draw.textbbox((0, 0), w_line, font=font_work)
                w_w = w_bbox[2] - w_bbox[0]
                draw.text((cx - w_w / 2, cur_y), w_line, font=font_work, fill=PROMINENT_SLATE)
                cur_y += 27 if w_idx < len(work_lines) - 1 else 33

            # 4. Principal Scientific Contribution (26pt bold Navy)
            concept_lines = m["concept"].split("\n")
            for c_idx, c_line in enumerate(concept_lines):
                c_bbox = draw.textbbox((0, 0), c_line, font=font_concept)
                c_w = c_bbox[2] - c_bbox[0]
                draw.text((cx - c_w / 2, cur_y), c_line, font=font_concept, fill=NAVY)
                cur_y += 29 if c_idx < len(concept_lines) - 1 else 30

    # Subtle outer framing border
    draw.rectangle([0, 0, W - 1, H - 1], outline=(226, 232, 240, 255), width=1)

    img.save(output_path, "PNG", optimize=True)
    print(f"Timeline saved to: {output_path} ({W}x{H} px)")

    # Mirror to public repo if it exists


if __name__ == "__main__":
    create_timeline()
