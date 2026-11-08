#!/usr/bin/env python3
r"""
Generate editorial timeline for Medium:
"From Zel'dovich to the Cosmic Web: Nonlinear Structure Formation"

Figure for Section "From Linear Perturbations to the Cosmic Web" of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design specifications:
- Canvas: 2000 x 760 px (matching cosmological_perturbations_timeline,
  primordial_fluctuations_timeline, and perturbation_evolution_timeline).
- Single horizontal chronological spine with alternating milestones (below/above).
- Outlined date pills with soft tinted background and color-coded accents.
- Exact typographic & semantic hierarchy of previous timelines:
  1. Scientist(s) (bold Navy #0f172a)
  2. Publication year (23pt bold pill)
  3. Original paper title (24pt italic regular Slate #334155)
  4. Principal scientific contribution (26pt bold Navy #0f172a)
- 7 milestones:
  1. Lynden-Bell (1967) — Below
  2. Zel'dovich (1970) — Above
  3. Gunn & Gott (1972) — Below
  4. Press & Schechter (1974) — Above
  5. Jõeveer / Einasto / Tago (1978) — Below
  6. Davis / Efstathiou / Frenk / White (1985) — Above
  7. Bond / Kofman / Pogosyan (1996) — Below
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "cosmic_web_timeline.png"

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
        "id": "lynden_bell",
        "position": "below",
        "name": "Lynden-Bell",
        "year": "1967",
        "work": "Statistical Mechanics\nof Violent Relaxation\nin Stellar Systems",
        "concept": "Violent Relaxation and\nHalo Equilibration",
        "accent": (30, 64, 175),     # Deep Royal Blue (#1e40af)
        "light": (239, 246, 255),    # #eff6ff
    },
    {
        "id": "zeldovich",
        "position": "above",
        "name": "Zel'dovich",
        "year": "1970",
        "work": "Gravitational Instability:\nAn Approximate Theory for\nLarge Density Perturbations",
        "concept": "Anisotropic Collapse,\nPancakes and Filaments",
        "accent": (14, 116, 144),    # Deep Cyan / Teal (#0e7490)
        "light": (236, 254, 255),    # #ecfeff
    },
    {
        "id": "gunn_gott",
        "position": "below",
        "name": "Gunn & Gott",
        "year": "1972",
        "work": "On the Infall of Matter Into\nClusters of Galaxies and Some\nEffects on Their Evolution",
        "concept": "Spherical Collapse\nand Turnaround",
        "accent": (109, 40, 217),    # Deep Purple / Violet (#6d28d9)
        "light": (245, 243, 255),    # #f5f3ff
    },
    {
        "id": "press_schechter",
        "position": "above",
        "name": "Press & Schechter",
        "year": "1974",
        "work": "Formation of Galaxies and\nClusters of Galaxies by Self-Similar\nGravitational Condensation",
        "concept": "Collapse Threshold and\nStatistical Halo Abundance",
        "accent": (67, 56, 202),     # Deep Indigo (#4338ca)
        "light": (238, 242, 255),    # #eef2ff
    },
    {
        "id": "joeveer_einasto_tago",
        "position": "below",
        "name": "Jõeveer / Einasto / Tago",
        "year": "1978",
        "work": "Spatial Distribution of Galaxies\nand of Clusters of Galaxies in the\nSouthern Galactic Hemisphere",
        "concept": "Early Observational Evidence\nfor Filaments and Voids",
        "accent": (4, 120, 87),      # Deep Emerald (#047857)
        "light": (236, 253, 245),    # #ecfdf5
    },
    {
        "id": "davis_efstathiou_frenk_white",
        "position": "above",
        "name": "Davis / Efstathiou / Frenk / White",
        "year": "1985",
        "work": "The Evolution of Large-Scale\nStructure in a Universe Dominated\nby Cold Dark Matter",
        "concept": "N-Body Simulations of\nCDM Structure Formation",
        "accent": (180, 83, 9),      # Warm Amber / Bronze (#b45309)
        "light": (254, 243, 199),    # #fef3c7
    },
    {
        "id": "bond_kofman_pogosyan",
        "position": "below",
        "name": "Bond / Kofman / Pogosyan",
        "year": "1996",
        "work": "How Filaments of\nGalaxies Are Woven\ninto the Cosmic Web",
        "concept": "Cosmic Web Geometry from\nthe Initial Density Field",
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

    # Typography matching Section 1, 2 & 3 hierarchy
    font_title = get_font(33, bold=True)
    font_name_single = get_font(34, bold=True)
    font_name_group = get_font(31, bold=True)
    font_name_multi = get_font(30, bold=True)
    font_year = get_font(23, bold=True)
    font_work = get_font(24, italic=True)
    font_concept = get_font(26, bold=True)

    # 1. Title in Editorial Badge Box
    title_text = "From Zel'dovich to the Cosmic Web: Nonlinear Structure Formation"
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    tw = title_bbox[2] - title_bbox[0]
    th = title_bbox[3] - title_bbox[1]

    pad_x = 28
    pad_y = 11
    bw = tw + 2 * pad_x
    bh = th + 2 * pad_y
    bx = (W - bw) // 2
    by = 20

    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=TITLE_BG, outline=TITLE_BORDER, width=2)
    draw.text((bx + pad_x, by + pad_y - 2), title_text, font=font_title, fill=NAVY)

    # 2. Timeline Axis Geometry
    # Both upper (3 nodes) and lower (4 nodes) milestones have 1-line headings,
    # 3-line paper titles, and 2-line bold concepts -> place spine_y at 426 for symmetry.
    spine_y = 426
    start_x = 230
    end_x = 1740
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

        name_lines = m["name"].split("\n")
        if len(name_lines) > 1:
            f_name = font_name_multi
        elif "/" in m["name"]:
            f_name = font_name_group
        else:
            f_name = font_name_single

        if is_above:
            # UPPER MILESTONES (Zel'dovich, Press & Schechter, Davis / Efstathiou / Frenk / White)
            cur_y = 88 if len(name_lines) > 1 else 116

            # 1. Scientist / Entity
            for n_idx, n_line in enumerate(name_lines):
                n_bbox = draw.textbbox((0, 0), n_line, font=f_name)
                n_w = n_bbox[2] - n_bbox[0]
                draw.text((cx - n_w / 2, cur_y), n_line, font=f_name, fill=NAVY)
                if len(name_lines) > 1:
                    cur_y += 33 if n_idx < len(name_lines) - 1 else 39
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
            cur_y += 40

            # 3. Original Paper Title (24pt italic Slate)
            work_lines = m["work"].split("\n")
            for w_idx, w_line in enumerate(work_lines):
                w_bbox = draw.textbbox((0, 0), w_line, font=font_work)
                w_w = w_bbox[2] - w_bbox[0]
                draw.text((cx - w_w / 2, cur_y), w_line, font=font_work, fill=PROMINENT_SLATE)
                cur_y += 28 if w_idx < len(work_lines) - 1 else 34

            # 4. Principal Scientific Contribution (26pt bold Navy)
            concept_lines = m["concept"].split("\n")
            for c_idx, c_line in enumerate(concept_lines):
                c_bbox = draw.textbbox((0, 0), c_line, font=font_concept)
                c_w = c_bbox[2] - c_bbox[0]
                draw.text((cx - c_w / 2, cur_y), c_line, font=font_concept, fill=NAVY)
                cur_y += 30 if c_idx < len(concept_lines) - 1 else 31

            # Vertical stem line from bottom of text cluster down to spine node
            stem_top = cur_y + 10
            draw.line([(cx, stem_top), (cx, spine_y - 12)], fill=accent + (255,), width=3)
            # Anchor dot at top of stem
            draw.ellipse([cx - 4, stem_top - 4, cx + 4, stem_top + 4], fill=accent + (255,))

        else:
            # LOWER MILESTONES (Lynden-Bell, Gunn & Gott, Jõeveer / Einasto / Tago, Bond / Kofman / Pogosyan)
            stem_bot = spine_y + 34
            draw.line([(cx, spine_y + 12), (cx, stem_bot)], fill=accent + (255,), width=3)
            # Anchor dot at bottom of stem
            draw.ellipse([cx - 4, stem_bot - 4, cx + 4, stem_bot + 4], fill=accent + (255,))

            # Text content stacked below stem
            cur_y = stem_bot + 14

            # 1. Scientist / Entity
            for n_idx, n_line in enumerate(name_lines):
                n_bbox = draw.textbbox((0, 0), n_line, font=f_name)
                n_w = n_bbox[2] - n_bbox[0]
                draw.text((cx - n_w / 2, cur_y), n_line, font=f_name, fill=NAVY)
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
                cur_y += 28 if w_idx < len(work_lines) - 1 else 34

            # 4. Principal Scientific Contribution (26pt bold Navy)
            concept_lines = m["concept"].split("\n")
            for c_idx, c_line in enumerate(concept_lines):
                c_bbox = draw.textbbox((0, 0), c_line, font=font_concept)
                c_w = c_bbox[2] - c_bbox[0]
                draw.text((cx - c_w / 2, cur_y), c_line, font=font_concept, fill=NAVY)
                cur_y += 30 if c_idx < len(concept_lines) - 1 else 31

    # Subtle outer framing border
    draw.rectangle([0, 0, W - 1, H - 1], outline=(226, 232, 240, 255), width=1)

    img.save(output_path, "PNG", optimize=True)
    print(f"Timeline saved to: {output_path} ({W}x{H} px)")

    # Mirror to public repo if it exists


if __name__ == "__main__":
    create_timeline()
