#!/usr/bin/env python3
r"""
Generate portrait panel:
Henri Poincaré and Ivar Bendixson.

Styling strictly harmonized with Part 1:
- the_road_to_modern_dynamics/generate_hamilton_jacobi_portraits.py
- the_road_to_modern_dynamics/images/hamilton_jacobi_portraits.png

Raw, unembellished historical photographs from the epoch of their work:
1. Henri Poincaré (1854–1912), photograph circa 1895–1900 (Cliché Manuel).
2. Ivar Bendixson (1861–1935), photograph circa 1895–1900 (Stockholm University / KTH).
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "poincare_bendixson_portraits.png"


def create_figure(output_path=None, use_young_poincare=False):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sources_dir = SCRIPT_DIR / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)

    bendixson_src = sources_dir / "bendixson.png"
    poincare_manuel_src = sources_dir / "poincare_manuel.jpg"
    poincare_smithsonian_src = sources_dir / "poincare_smithsonian.jpg"

    # Dimensions matching Part 1 (Hamilton & Jacobi: 1124 x 707 px)
    target_w = 560
    portrait_h = 602
    label_h = 105
    total_h = portrait_h + label_h
    divider_w = 4
    total_w = target_w * 2 + divider_w

    # 1. Henri Poincaré
    if use_young_poincare and poincare_smithsonian_src.exists():
        p_raw = Image.open(poincare_smithsonian_src).convert('L')
        # Crop centered on head and shoulders
        px0 = 500
        py0 = 360
        px1 = px0 + 1800
        py1 = py0 + int(1800 * (portrait_h / target_w))
        p_crop = p_raw.crop((px0, py0, px1, py1))
    else:
        p_raw = Image.open(poincare_manuel_src).convert('L')
        # Crop centered on head and shoulders
        mx0 = 220
        my0 = 650
        mx1 = mx0 + 1400
        my1 = my0 + int(1400 * (portrait_h / target_w))
        p_crop = p_raw.crop((mx0, my0, mx1, my1))

    p_rescaled = p_crop.resize((target_w, portrait_h), Image.Resampling.LANCZOS)
    p_rescaled = ImageOps.autocontrast(p_rescaled, cutoff=(1, 1))
    p_rgb = Image.merge('RGB', (p_rescaled, p_rescaled, p_rescaled))

    # 2. Ivar Bendixson
    b_raw = Image.open(bendixson_src).convert('L')
    bw, bh = b_raw.size
    bx0 = 43
    by0 = 100
    bx1 = bx0 + 700
    by1 = by0 + int(700 * (portrait_h / target_w))
    b_crop = b_raw.crop((bx0, by0, min(bw, bx1), min(bh, by1)))
    b_rescaled = b_crop.resize((target_w, portrait_h), Image.Resampling.LANCZOS)
    b_rescaled = ImageOps.autocontrast(b_rescaled, cutoff=(1, 1))
    b_rgb = Image.merge('RGB', (b_rescaled, b_rescaled, b_rescaled))

    # Deep slate navy background matching Part 1
    composite = Image.new('RGB', (total_w, total_h), (15, 23, 42))

    # Paste side-by-side portraits
    composite.paste(p_rgb, (0, 0))
    composite.paste(b_rgb, (target_w + divider_w, 0))

    draw = ImageDraw.Draw(composite)

    # Typography matching Part 1
    font_bold = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf', 33)
    font_italic = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf', 24)

    figures = [
        ('Henri Poincaré', '1854–1912', 0),
        ('Ivar Bendixson', '1861–1935', target_w + divider_w)
    ]

    for name, dates, x_offset in figures:
        # Subtle divider line under portrait
        draw.line([(x_offset, portrait_h), (x_offset + target_w, portrait_h)], fill=(51, 65, 85), width=2)

        # Centered name (33pt bold white)
        name_bbox = draw.textbbox((0, 0), name, font=font_bold)
        name_w = name_bbox[2] - name_bbox[0]
        name_x = x_offset + (target_w - name_w) // 2
        name_y = portrait_h + 16
        draw.text((name_x, name_y), name, font=font_bold, fill=(255, 255, 255))

        # Centered dates (24pt italic light slate)
        dates_bbox = draw.textbbox((0, 0), dates, font=font_italic)
        dates_w = dates_bbox[2] - dates_bbox[0]
        dates_x = x_offset + (target_w - dates_w) // 2
        dates_y = name_y + 42
        draw.text((dates_x, dates_y), dates, font=font_italic, fill=(203, 213, 225))

    composite.save(output_path, "PNG", optimize=True)
    print(f"[OK] Historical portrait panel saved to: {output_path}")


if __name__ == "__main__":
    create_figure()
