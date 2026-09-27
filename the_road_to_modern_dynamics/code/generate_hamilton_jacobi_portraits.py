#!/usr/bin/env python3
"""
Generate figure:
William Rowan Hamilton and Carl Gustav Jacob Jacobi.

Styling harmonized with analytical_mechanics_portraits.png,
with full uncropped portraits cleanly rescaled to a more compact
dimension, and refined, smaller name typography.
"""

from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageOps

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "hamilton_jacobi_portraits.png"

def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sources_dir = SCRIPT_DIR / "sources"
    ham_src = sources_dir / "hamilton_lccn_cropped.jpg"
    jac_src = sources_dir / "jacobi_1843.jpg"

    # If raw source files are not locally present, use pre-rendered high-res portrait panel
    if not (ham_src.exists() and jac_src.exists()):
        if DEFAULT_OUT.exists():
            if output_path.resolve() != DEFAULT_OUT.resolve():
                shutil.copyfile(DEFAULT_OUT, output_path)
            return output_path
        # Fallback download if sources and default output do not exist
        sources_dir.mkdir(parents=True, exist_ok=True)
        import urllib.request
        headers = {'User-Agent': 'Mozilla/5.0'}
        url_ham = "https://upload.wikimedia.org/wikipedia/commons/9/97/Sir_William_Rowan_Hamilton%2C_head-and-shoulders_portrait%2C_facing_slightly_right_LCCN90713420_%28cropped%29.jpg"
        req = urllib.request.Request(url_ham, headers=headers)
        with urllib.request.urlopen(req) as resp, open(ham_src, 'wb') as f:
            f.write(resp.read())

        url_jac = "https://upload.wikimedia.org/wikipedia/commons/9/93/Carl_Gustav_Jacob_Jacobi_portrait_1843.jpg"
        req = urllib.request.Request(url_jac, headers=headers)
        with urllib.request.urlopen(req) as resp, open(jac_src, 'wb') as f:
            f.write(resp.read())

    # Compact rescaled dimensions (70% scale: 1124 x 707 px)
    target_w = 560
    portrait_h = 602
    label_h = 105
    total_h = portrait_h + label_h
    divider_w = 4
    total_w = target_w * 2 + divider_w

    # Full portraits without tight cropping (preserving full head, hair, collars, and cravats)
    ham_raw = Image.open(ham_src).convert('L')
    ham_full = ham_raw.crop((2, 30, 1102, 1212))
    ham_rescaled = ham_full.resize((target_w, portrait_h), Image.Resampling.LANCZOS)
    ham_rescaled = ImageOps.autocontrast(ham_rescaled, cutoff=(1, 1))
    ham_rgb = Image.merge('RGB', (ham_rescaled, ham_rescaled, ham_rescaled))

    jac_raw = Image.open(jac_src).crop((125, 120, 1076, 1305)).convert('L')
    jac_full = jac_raw.crop((15, 35, 875, 959))
    jac_rescaled = jac_full.resize((target_w, portrait_h), Image.Resampling.LANCZOS)
    jac_rescaled = ImageOps.autocontrast(jac_rescaled, cutoff=(1, 1))
    jac_rgb = Image.merge('RGB', (jac_rescaled, jac_rescaled, jac_rescaled))

    # Deep slate background matching analytical_mechanics_portraits.png
    composite = Image.new('RGB', (total_w, total_h), (15, 23, 42))

    # Paste rescaled portraits
    composite.paste(ham_rgb, (0, 0))
    composite.paste(jac_rgb, (target_w + divider_w, 0))

    draw = ImageDraw.Draw(composite)

    # Smaller, refined typography for elegant proportions
    font_bold = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf', 33)
    font_italic = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf', 24)

    figures = [
        ('William Rowan Hamilton', '1805–1865', 0),
        ('Carl Gustav Jacob Jacobi', '1804–1851', target_w + divider_w)
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
    print(f"[OK] Compact rescaled portrait panel saved to: {output_path}")

if __name__ == "__main__":
    create_figure()
