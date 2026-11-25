#!/usr/bin/env python3
r"""
generate_order_chaos_timeline.py

Generates the closing historical synopsis timeline for Article 3:
"From Poincaré to Laskar: A Timeline of Order, Chaos, and Predictability"

Reuses the exact visual language, editorial title badge, typography hierarchy,
capsule styling, and alternating horizontal rail of Parts I and II:
  - the_road_to_modern_dynamics/images/mechanics_conceptual_timeline.png
  - the_road_to_modern_dynamics_2/images/dynamical_systems_timeline.png

Typography & Canvas (2000 x 935 px for high legibility at 680px Medium width):
  - Title badge: 35pt bold Navy
  - Milestone name: 34pt bold Navy
  - Date capsule: 26pt bold accented pill
  - Exact English paper title(s): 24pt italic Slate (stacked in chronological order, max 2 lines each)
  - Concept contribution: 24pt bold Navy

Output:
  images/order_chaos_predictability_timeline.png
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "order_chaos_predictability_timeline.png"

# Color Palette matching Parts I & II
BG_COLOR = (255, 255, 255, 255)
NAVY = (15, 23, 42, 255)            # #0f172a
PROMINENT_SLATE = (51, 65, 85, 255) # #334155
SPINE_COLOR = (203, 213, 225, 255)  # #cbd5e1
TITLE_BG = (248, 250, 252, 255)     # #f8fafc
TITLE_BORDER = (203, 213, 225, 255) # #cbd5e1

MILESTONES = [
    {
        "id": "poincare",
        "position": "above",
        "name": "Poincaré",
        "year": "1890",
        "papers": [
            ["On the Three-Body Problem", "and the Equations of Dynamics"],
        ],
        "concept": "Homoclinic Geometry",
        "accent": (190, 24, 93),     # Crimson / Magenta (#be185d)
        "light": (253, 242, 248),    # #fdf2f8
    },
    {
        "id": "birkhoff",
        "position": "below",
        "name": "Birkhoff",
        "year": "1935",
        "papers": [
            ["New Researches on", "Dynamical Systems"],
        ],
        "concept": "Infinitely Many Periodic Orbits\nNear Homoclinic Points",
        "accent": (67, 56, 202),     # Blue-Violet (#4338ca)
        "light": (238, 242, 255),    # #eef2ff
    },
    {
        "id": "kam",
        "position": "above",
        "name": "Kolmogorov–\nArnold–Moser",
        "year": "1954–1963",
        "papers": [
            [
                "1954: On Conservation of Conditionally",
                "Periodic Motions for a Small Change...",
            ],
            [
                "1962: On Invariant Curves of Area-",
                "Preserving Mappings of an Annulus",
            ],
            [
                "1963: Proof of a Theorem of A. N.",
                "Kolmogorov on the Invariance...",
            ],
        ],
        "concept": "Quasiperiodic Motion\nSurvives Perturbations",
        "accent": (3, 105, 161),     # Blue / Cyan (#0369a1)
        "light": (240, 249, 255),    # #f0f9ff
    },
    {
        "id": "lorenz",
        "position": "below",
        "name": "Lorenz",
        "year": "1963",
        "papers": [
            ["Deterministic Nonperiodic Flow"],
        ],
        "concept": "Sensitive Dependence",
        "accent": (194, 65, 12),     # Orange (#c2410c)
        "light": (255, 247, 237),    # #fff7ed
    },
    {
        "id": "smale",
        "position": "above",
        "name": "Smale",
        "year": "1965–1967",
        "papers": [
            ["1965: Diffeomorphisms with", "Many Periodic Points"],
            ["1967: Differentiable Dynamical Systems"],
        ],
        "concept": "Geometric Foundations\nof Chaos",
        "accent": (4, 120, 87),      # Green (#047857)
        "light": (236, 253, 245),    # #ecfdf5
    },
    {
        "id": "laskar_1989",
        "position": "below",
        "name": "Laskar",
        "year": "1989",
        "papers": [
            [
                "A numerical experiment on the chaotic",
                "behaviour of the Solar System",
            ],
        ],
        "concept": "Planetary Chaos",
        "accent": (220, 38, 38),     # Red family (#dc2626)
        "light": (254, 242, 242),    # #fef2f2
    },
    {
        "id": "laskar_1990",
        "position": "above",
        "name": "Laskar",
        "year": "1990",
        "papers": [
            [
                "The chaotic motion of the solar system:",
                "A numerical estimate of the size...",
            ],
        ],
        "concept": "Secular Resonances",
        "accent": (185, 28, 28),     # Deep Red (#b91c1c)
        "light": (254, 242, 242),    # #fef2f2
    },
    {
        "id": "stability_2008_2009",
        "position": "below",
        "name": "Batygin & Laughlin\nLaskar & Gastineau",
        "year": "2008–2009",
        "papers": [
            [
                "2008: On the Dynamical Stability",
                "of the Solar System",
            ],
            [
                "2009: Existence of collisional",
                "trajectories of Mercury, Mars...",
            ],
        ],
        "concept": "Long-Term Planetary Stability",
        "accent": (136, 19, 55),     # Burgundy (#881337)
        "light": (255, 241, 242),    # #fff1f2
    },
]


def get_font(size, bold=False, italic=False):
    """Load system sans-serif fonts matching Parts I & II."""
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


def draw_text_block(draw, cx, start_y, milestone, font_name, font_year, font_paper, font_concept):
    """Render one milestone text block (name, year pill, stacked paper title(s), concept) centered at cx."""
    accent = milestone["accent"]
    cur_y = start_y
    min_x, max_x = cx, cx

    # 1. Name (34pt bold Navy, supporting clean multi-line wrap for long grouped names)
    name_lines = milestone["name"].split("\n")
    for n_idx, n_line in enumerate(name_lines):
        n_bbox = draw.textbbox((0, 0), n_line, font=font_name)
        n_w = n_bbox[2] - n_bbox[0]
        min_x = min(min_x, cx - n_w / 2)
        max_x = max(max_x, cx + n_w / 2)
        draw.text((cx - n_w / 2, cur_y), n_line, font=font_name, fill=NAVY)
        cur_y += 38 if n_idx < len(name_lines) - 1 else 43

    # 2. Year capsule (26pt bold accented pill)
    y_bbox = draw.textbbox((0, 0), milestone["year"], font=font_year)
    y_w = y_bbox[2] - y_bbox[0] + 28
    y_h = 34
    y_left = cx - y_w / 2
    min_x = min(min_x, y_left)
    max_x = max(max_x, y_left + y_w)
    draw.rounded_rectangle(
        [y_left, cur_y, y_left + y_w, cur_y + y_h],
        radius=17,
        fill=milestone["light"] + (255,),
        outline=accent + (220,),
        width=2,
    )
    draw.text((y_left + 14, cur_y + 3), milestone["year"], font=font_year, fill=accent + (255,))
    cur_y += 45

    # 3. Stacked paper title(s) in English (22pt italic slate, max 2 lines per paper)
    papers = milestone["papers"]
    for p_idx, p_lines in enumerate(papers):
        assert len(p_lines) <= 2, f"{milestone['id']} paper {p_idx + 1} exceeds 2 lines!"
        for p_line in p_lines:
            p_bbox = draw.textbbox((0, 0), p_line, font=font_paper)
            p_w = p_bbox[2] - p_bbox[0]
            min_x = min(min_x, cx - p_w / 2)
            max_x = max(max_x, cx + p_w / 2)
            draw.text((cx - p_w / 2, cur_y), p_line, font=font_paper, fill=PROMINENT_SLATE)
            cur_y += 28
        if p_idx < len(papers) - 1:
            cur_y += 8
    cur_y += 9

    # 4. Concept contribution line (24pt bold Navy)
    concept_lines = milestone["concept"].split("\n")
    for c_idx, c_line in enumerate(concept_lines):
        c_bbox = draw.textbbox((0, 0), c_line, font=font_concept)
        c_w = c_bbox[2] - c_bbox[0]
        min_x = min(min_x, cx - c_w / 2)
        max_x = max(max_x, cx + c_w / 2)
        draw.text((cx - c_w / 2, cur_y), c_line, font=font_concept, fill=NAVY)
        cur_y += 29 if c_idx < len(concept_lines) - 1 else 31

    return cur_y, min_x, max_x


def create_timeline(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Matching Part II width (2000px) with 935px height so stacked 24pt paper titles breathe cleanly
    W, H = 2000, 935
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_title = get_font(35, bold=True)
    font_name = get_font(34, bold=True)
    font_year = get_font(26, bold=True)
    font_paper = get_font(24, italic=True)
    font_concept = get_font(24, bold=True)

    # 1. Title in Editorial Badge Box
    title_text = "From Poincaré to Laskar: A Timeline of Order, Chaos, and Predictability"
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    tw = title_bbox[2] - title_bbox[0]
    th = title_bbox[3] - title_bbox[1]

    pad_x = 28
    pad_y = 12
    bw = tw + 2 * pad_x
    bh = th + 2 * pad_y
    bx = (W - bw) // 2
    by = 24

    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=TITLE_BG, outline=TITLE_BORDER, width=2)
    draw.text((bx + pad_x, by + pad_y - 2), title_text, font=font_title, fill=NAVY)

    # 2. Horizontal Spine Geometry
    spine_y = 568
    start_x = 186
    end_x = 1765
    step_x = (end_x - start_x) / (len(MILESTONES) - 1)

    draw.line([(start_x - 80, spine_y), (end_x + 85, spine_y)], fill=SPINE_COLOR, width=5)
    draw.polygon(
        [(end_x + 105, spine_y), (end_x + 85, spine_y - 8), (end_x + 85, spine_y + 8)],
        fill=(100, 116, 139, 255),
    )

    # 3. Render Alternating Milestones & Verify Horizontal Non-Overlap
    row_bounds = {"above": [], "below": []}
    for i, m in enumerate(MILESTONES):
        cx = start_x + i * step_x
        accent = m["accent"]

        # Circle marker on spine
        draw.ellipse([cx - 12, spine_y - 12, cx + 12, spine_y + 12], fill=(255, 255, 255, 255), outline=accent + (255,), width=4)
        draw.ellipse([cx - 5, spine_y - 5, cx + 5, spine_y + 5], fill=accent + (255,))

        if m["position"] == "above":
            # Keep KAM raised (3 stacked papers); lower & horizontally align the remaining upper milestones to Smale's level
            above_start_y = 128 if m["id"] == "kam" else 266
            end_text_y, min_x, max_x = draw_text_block(
                draw, cx, above_start_y, m, font_name, font_year, font_paper, font_concept
            )
            stem_top = end_text_y + 10
            assert stem_top < spine_y - 18, f"{m['id']} collided with spine! ({stem_top} vs {spine_y})"
            draw.line([(cx, stem_top), (cx, spine_y - 12)], fill=accent + (255,), width=3)
            draw.ellipse([cx - 4, stem_top - 4, cx + 4, stem_top + 4], fill=accent + (255,))
        else:
            stem_bot = spine_y + 42
            draw.line([(cx, spine_y + 12), (cx, stem_bot)], fill=accent + (255,), width=3)
            draw.ellipse([cx - 4, stem_bot - 4, cx + 4, stem_bot + 4], fill=accent + (255,))
            end_text_y, min_x, max_x = draw_text_block(
                draw, cx, stem_bot + 14, m, font_name, font_year, font_paper, font_concept
            )
            assert end_text_y < H - 16, f"{m['id']} overflowed bottom! ({end_text_y} >= {H - 16})"

        assert min_x >= 16 and max_x <= W - 16, f"{m['id']} overflowed horizontal canvas: [{min_x:.1f}, {max_x:.1f}]"
        row_bounds[m["position"]].append((m["id"], min_x, max_x))

    # Verify clean horizontal gap on each row
    for row_name, bounds in row_bounds.items():
        for j in range(len(bounds) - 1):
            id1, _, r1 = bounds[j]
            id2, l2, _ = bounds[j + 1]
            gap = l2 - r1
            assert gap >= 18, f"Overlap/tight gap on {row_name} row between {id1} and {id2}: {gap:.1f} px"
            print(f"  [Check {row_name:5s}] {id1} -> {id2}: gap = {gap:.1f} px")

    # Subtle outer frame border
    draw.rectangle([0, 0, W - 1, H - 1], outline=(226, 232, 240, 255), width=1)

    img.save(output_path, "PNG", optimize=True)
    print(f"Timeline saved to: {output_path} ({W}x{H} px, {output_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    create_timeline()
