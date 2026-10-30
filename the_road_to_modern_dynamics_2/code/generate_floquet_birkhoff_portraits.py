#!/usr/bin/env python3
r"""
Generate portrait panel:
Gaston Floquet and George David Birkhoff.

Styling strictly harmonized with:
- the_road_to_modern_dynamics_2/generate_poincare_bendixson_portraits.py
- the_road_to_modern_dynamics_2/images/poincare_bendixson_portraits.png
- the_road_to_modern_dynamics/images/hamilton_jacobi_portraits.png

Raw, unembellished historical photographs:
1. Gaston Floquet (1847–1920): Archival photograph from the Faculté des Sciences
   de Nancy (Université de Lorraine institutional history collection).
2. George David Birkhoff (1884–1944): Archival frontispiece portrait from the
   National Academy of Sciences Biographical Memoirs (Photograph by Bachrach).
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "floquet_birkhoff_portraits.png"


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sources_dir = SCRIPT_DIR / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)

    floquet_src = sources_dir / "floquet.jpg"
    birkhoff_src = sources_dir / "birkhoff_nas.jpg"

    # Dimensions matching Poincaré & Bendixson (1124 x 707 px)
    target_w = 560
    portrait_h = 602
    label_h = 105
    total_h = portrait_h + label_h
    divider_w = 4
    total_w = target_w * 2 + divider_w

    # 1. Gaston Floquet
    f_raw = Image.open(floquet_src).convert('L')
    fx0 = 300
    fy0 = 20
    crop_w = 450
    crop_h = int(crop_w * portrait_h / target_w)  # 484
    f_crop = f_raw.crop((fx0, fy0, fx0 + crop_w, fy0 + crop_h))
    f_rescaled = f_crop.resize((target_w, portrait_h), Image.Resampling.LANCZOS)
    f_rescaled = ImageOps.autocontrast(f_rescaled, cutoff=(1, 1))
    f_rgb = Image.merge('RGB', (f_rescaled, f_rescaled, f_rescaled))

    # 2. George David Birkhoff
    b_raw = Image.open(birkhoff_src).convert('L')
    # Photo rectangle in NAS scan: x=4..363, y=25..411 (aspect ratio 560:602)
    bx0 = 4
    by0 = 25
    b_crop_w = 359
    b_crop_h = int(b_crop_w * portrait_h / target_w)  # 386
    b_crop = b_raw.crop((bx0, by0, bx0 + b_crop_w, by0 + b_crop_h))
    b_rescaled = b_crop.resize((target_w, portrait_h), Image.Resampling.LANCZOS)
    b_rescaled = ImageOps.autocontrast(b_rescaled, cutoff=(1, 1))
    b_rgb = Image.merge('RGB', (b_rescaled, b_rescaled, b_rescaled))

    # Deep slate navy background matching existing portrait panels
    composite = Image.new('RGB', (total_w, total_h), (15, 23, 42))

    # Paste side-by-side portraits
    composite.paste(f_rgb, (0, 0))
    composite.paste(b_rgb, (target_w + divider_w, 0))

    draw = ImageDraw.Draw(composite)

    # Typography matching Part 1 and Poincaré–Bendixson
    font_bold = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf', 33)
    font_italic = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf', 24)

    figures = [
        ('Gaston Floquet', '1847–1920', 0),
        ('George David Birkhoff', '1884–1944', target_w + divider_w)
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
