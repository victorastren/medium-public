#!/usr/bin/env python3
"""
Generate figure:
Euler, d'Alembert, and Lagrange (the pioneers of analytical mechanics).
Public domain paintings curated and harmonized:
1. Leonhard Euler (Jakob Emanuel Handmann, 1753, Kunstmuseum Basel)
2. Jean le Rond d'Alembert (Maurice Quentin de La Tour, 1753, Musée du Louvre)
3. Joseph-Louis Lagrange (Smithsonian Institution Libraries)
With large, crisp, high-visibility typography plaques showing names and dates beneath each portrait.
"""

from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "analytical_mechanics_portraits.png"

def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Source images
    sources_dir = SCRIPT_DIR / "sources"
    lagrange_src = SCRIPT_DIR.parent.parent / "beyond_kepler_solar_system_stability" / "images" / "lagrange_laplace_portraits.png"
    euler_src = sources_dir / "euler.jpg"
    dalembert_src = sources_dir / "dalembert_tour.jpg"

    # If raw source files are not locally present, use pre-rendered high-res portrait panel
    if not (euler_src.exists() and dalembert_src.exists() and lagrange_src.exists()):
        if DEFAULT_OUT.exists():
            if output_path.resolve() != DEFAULT_OUT.resolve():
                shutil.copyfile(DEFAULT_OUT, output_path)
            return output_path

    target_w = 800
    portrait_h = 860
    label_h = 150
    total_h = portrait_h + label_h
    divider_w = 4
    total_w = target_w * 3 + divider_w * 2

    # 1. Euler
    euler_orig = Image.open(euler_src)
    euler_crop = euler_orig.crop((750, 500, 3950, 4020)).resize((target_w, portrait_h), Image.Resampling.LANCZOS)

    # 2. d'Alembert
    dalembert_orig = Image.open(dalembert_src)
    dalembert_crop = dalembert_orig.crop((0, 25, 1024, 1150)).resize((target_w, portrait_h), Image.Resampling.LANCZOS)

    # 3. Lagrange
    lagrange_full = Image.open(lagrange_src).crop((0, 0, 808, 960))
    lagrange_crop = lagrange_full.crop((4, 0, 804, 860)).resize((target_w, portrait_h), Image.Resampling.LANCZOS)

    # Deep slate background
    composite = Image.new('RGB', (total_w, total_h), (15, 23, 42))

    # Paste portraits
    composite.paste(euler_crop, (0, 0))
    composite.paste(dalembert_crop, (target_w + divider_w, 0))
    composite.paste(lagrange_crop, (target_w * 2 + divider_w * 2, 0))

    draw = ImageDraw.Draw(composite)

    # Dividers
    draw.rectangle([target_w, 0, target_w + divider_w - 1, portrait_h], fill=(30, 41, 59))
    draw.rectangle([target_w * 2 + divider_w, 0, target_w * 2 + divider_w * 2 - 1, portrait_h], fill=(30, 41, 59))

    # Bottom border
    draw.line([(0, portrait_h), (total_w, portrait_h)], fill=(51, 65, 85), width=2)

    # Fonts
    font_paths_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    font_paths_italic = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
    ]

    font_name = None
    for p in font_paths_bold:
        if Path(p).exists():
            font_name = ImageFont.truetype(p, 42)
            break
    if font_name is None:
        font_name = ImageFont.load_default()

    font_dates = None
    for p in font_paths_italic:
        if Path(p).exists():
            font_dates = ImageFont.truetype(p, 28)
            break
    if font_dates is None:
        font_dates = ImageFont.load_default()

    labels = [
        ("Leonhard Euler", "1707–1783", 0),
        ("Jean le Rond d'Alembert", "1717–1783", target_w + divider_w),
        ("Joseph-Louis Lagrange", "1736–1813", target_w * 2 + divider_w * 2),
    ]

    for name, dates, x_offset in labels:
        cx = x_offset + target_w // 2
        draw.text((cx, portrait_h + 46), name, fill=(255, 255, 255), font=font_name, anchor="mm")
        draw.text((cx, portrait_h + 104), dates, fill=(148, 163, 184), font=font_dates, anchor="mm")

    composite.save(output_path, "PNG", optimize=True)
    return output_path

if __name__ == '__main__':
    create_figure()
