#!/usr/bin/env python3
r"""
Generate editorial timeline for Medium:
"From Sakharov to BAO: The Evolution of Cosmological Perturbations"

Figure for Section 3 of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design specifications:
- Canvas: 2000 x 760 px (matching cosmological_perturbations_timeline & primordial_fluctuations_timeline).
- Single horizontal chronological spine with alternating milestones (above/below).
- Outlined date pills with soft tinted background and color-coded accents.
- Exact Section 1 & 2 typographic & semantic hierarchy:
  1. Scientist(s) (bold Navy #0f172a)
  2. Publication year (23pt bold pill)
  3. Original paper title (24-25pt italic regular Slate #334155)
  4. Principal scientific contribution (26-27pt bold Navy #0f172a)
- 7 milestones:
  1. Sakharov (1965–1966) — Above
  2. Silk (1968) — Below
  3. Peebles & Yu / Sunyaev & Zel'dovich (1970) — Above
  4. Mészáros (1974) — Below
  5. Peebles / Bond, Szalay & Turner / Blumenthal et al. (1982–1984) — Above
  6. Eisenstein & Hu (1998) — Below
  7. WMAP / Eisenstein et al. (2003–2005) — Above
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "perturbation_evolution_timeline.png"

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
        "id": "sakharov",
        "position": "above",
        "name": "Sakharov",
        "year": "1965–1966",
        "work": "The Initial Stage of an Expanding\nUniverse and the Appearance of a\nNonuniform Distribution of Matter",
        "concept": "Acoustic Imprints in the\nPerturbation Spectrum",
        "accent": (30, 64, 175),     # Deep Royal Blue (#1e40af)
        "light": (239, 246, 255),    # #eff6ff
    },
    {
        "id": "silk",
        "position": "below",
        "name": "Silk",
        "year": "1968",
        "work": "Cosmic Black-Body Radiation\nand Galaxy Formation",
        "concept": "Photon Diffusion and\nSmall-Scale Damping",
        "accent": (14, 116, 144),    # Deep Cyan / Teal (#0e7490)
        "light": (236, 254, 255),    # #ecfeff
    },
    {
        "id": "peebles_sunyaev",
        "position": "above",
        "name": "Peebles & Yu /\nSunyaev & Zel'dovich",
        "year": "1970",
        "work": "Primeval Adiabatic Perturbation\nin an Expanding Universe\nSmall-Scale Fluctuations of Relic Radiation",
        "concept": "Photon–Baryon\nAcoustic Evolution",
        "accent": (109, 40, 217),    # Deep Purple / Violet (#6d28d9)
        "light": (245, 243, 255),    # #f5f3ff
    },
    {
        "id": "meszaros",
        "position": "below",
        "name": "Mészáros",
        "year": "1974",
        "work": "The Behaviour of Point Masses in an\nExpanding Cosmological Substratum",
        "concept": "Radiation-Era Suppression\nof Matter Growth",
        "accent": (67, 56, 202),     # Deep Indigo (#4338ca)
        "light": (238, 242, 255),    # #eef2ff
    },
    {
        "id": "cdm_1982_1984",
        "position": "above",
        "name": "Peebles / Bond, Szalay &\nTurner / Blumenthal et al.",
        "year": "1982–1984",
        "work": "Formation of Galaxies and\nLarge-Scale Structure with\nCold Dark Matter",
        "concept": "Cold Dark Matter and\nHierarchical Structure Formation",
        "accent": (4, 120, 87),      # Deep Emerald (#047857)
        "light": (236, 253, 245),    # #ecfdf5
    },
    {
        "id": "eisenstein_hu",
        "position": "below",
        "name": "Eisenstein & Hu",
        "year": "1998",
        "work": "Baryonic Features in the\nMatter Transfer Function",
        "concept": "Baryonic Features in the\nTransfer Function",
        "accent": (180, 83, 9),      # Warm Amber / Bronze (#b45309)
        "light": (254, 243, 199),    # #fef3c7
    },
    {
        "id": "wmap_bao",
        "position": "above",
        "name": "WMAP / Eisenstein et al.",
        "year": "2003–2005",
        "work": "First-Year WMAP Observations:\nThe Angular Power Spectrum\nDetection of the Baryon Acoustic Peak...",
        "concept": "Acoustic Signatures in the\nCMB and Galaxy Clustering",
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

    # Typography matching Section 1 & 2 hierarchy
    font_title = get_font(33, bold=True)
    font_name_single = get_font(35, bold=True)
    font_name_multi = get_font(30, bold=True)
    font_year = get_font(23, bold=True)
    font_work = get_font(24, italic=True)
    font_concept = get_font(26, bold=True)

    # 1. Title in Editorial Badge Box
    title_text = "From Sakharov to BAO: The Evolution of Cosmological Perturbations"
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
    # Since 4 nodes are above (0, 2, 4, 6) and 3 nodes are below (1, 3, 5),
    # place spine_y at 452 to balance top and bottom margins symmetrically.
    spine_y = 452
    start_x = 235
    end_x = 1745
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
        f_name = font_name_multi if len(name_lines) > 1 else font_name_single

        if is_above:
            # UPPER MILESTONES (Sakharov, Peebles & Yu / Sunyaev & Zel'dovich, 1982-1984 CDM, WMAP / Eisenstein et al.)
            cur_y = 96 if len(name_lines) > 1 else 112

            # 1. Scientist / Entity
            for n_idx, n_line in enumerate(name_lines):
                n_bbox = draw.textbbox((0, 0), n_line, font=f_name)
                n_w = n_bbox[2] - n_bbox[0]
                draw.text((cx - n_w / 2, cur_y), n_line, font=f_name, fill=NAVY)
                if len(name_lines) > 1:
                    cur_y += 34 if n_idx < len(name_lines) - 1 else 40
                else:
                    cur_y += 45

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
                if m.get("id") in ("peebles_sunyaev", "wmap_bao") and w_idx == 1:
                    cur_y += 33  # Extra breathing room between the two paired paper titles
                else:
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
            # LOWER MILESTONES (Silk, Mészáros, Eisenstein & Hu)
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
                cur_y += 45

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

    # Subtle outer framing border
    draw.rectangle([0, 0, W - 1, H - 1], outline=(226, 232, 240, 255), width=1)

    img.save(output_path, "PNG", optimize=True)
    print(f"Timeline saved to: {output_path} ({W}x{H} px)")

    # Mirror to public repo if it exists


if __name__ == "__main__":
    create_timeline()
