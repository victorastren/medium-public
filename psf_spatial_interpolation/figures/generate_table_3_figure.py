#!/usr/bin/env python3
"""
Generate Table 3 image: Leading Reconstruction Methods.
Fixes truncation by optimizing column widths, particularly splitting the first
column (Scenario) over two lines as requested by the author.
Renders to images/table_3.png at 2x resolution (Medium 680px width).
"""

import os
import subprocess
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = PROJECT_ROOT / "images"
OUTPUT_PNG = IMAGES_DIR / "table_3.png"

html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {
    margin: 0;
    padding: 24px;
    background: #ffffff;
    display: inline-block;
  }
  table {
    border-collapse: collapse;
    width: 680px;
    font-family: Charter, 'Bitstream Charter', Georgia, Cambria, 'Times New Roman', Times, serif;
    color: #292929;
    font-size: 15px;
    line-height: 1.42;
    background: #ffffff;
    border: 1px solid #d0d0d0;
    box-sizing: border-box;
  }
  th, td {
    border: 1px solid #d0d0d0;
    padding: 10px 12px;
    vertical-align: middle;
  }
  th {
    background-color: #f4f4f4;
    font-weight: bold;
    color: #1a1a1a;
    font-size: 15px;
  }
  .col-scenario {
    width: 31%;
    text-align: left;
  }
  .col-algo {
    width: 21%;
    text-align: left;
  }
  .col-erec {
    width: 14%;
    text-align: center;
  }
  .col-rmse-e {
    width: 17%;
    text-align: center;
  }
  .col-rmse-r2 {
    width: 17%;
    text-align: center;
  }
  .scenario-title {
    font-weight: bold;
    color: #111111;
  }
  .scenario-sub {
    font-size: 13.5px;
    color: #444444;
  }
  .algo-sub {
    font-size: 13.5px;
    color: #555555;
  }
</style>
</head>
<body>
<table>
  <thead>
    <tr>
      <th class="col-scenario">Scenario</th>
      <th class="col-algo">Leading Algorithm</th>
      <th class="col-erec"><em>E</em><sub>rec</sub><br>(%)</th>
      <th class="col-rmse-e">Combined<br>RMSE(<em>e</em>)<br>(×10⁻³)</th>
      <th class="col-rmse-r2">RMSE(<em>R</em>²)<br>(px²)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="col-scenario">
        <span class="scenario-title">G1: Smooth Moffat</span><br>
        <span class="scenario-sub">(<em>K</em> = 5)</span>
      </td>
      <td class="col-algo">Polynomial<br><span class="algo-sub">(deg 2)</span></td>
      <td class="col-erec">0.045%</td>
      <td class="col-rmse-e"><strong>0.063</strong></td>
      <td class="col-rmse-r2">0.0007</td>
    </tr>
    <tr>
      <td class="col-scenario">
        <span class="scenario-title">G1: Smooth Moffat</span><br>
        <span class="scenario-sub">(<em>K</em> = 5)</span>
      </td>
      <td class="col-algo">Universal Kriging<br><span class="algo-sub">(Quad)</span></td>
      <td class="col-erec"><strong>0.016%</strong></td>
      <td class="col-rmse-e">0.218</td>
      <td class="col-rmse-r2"><strong>0.0001</strong></td>
    </tr>
    <tr>
      <td class="col-scenario">
        <span class="scenario-title">G2: Ground-based:</span><br>
        <span class="scenario-sub">optical + atmospheric (<em>K</em> = 8)</span>
      </td>
      <td class="col-algo">Radial Basis<br>Function</td>
      <td class="col-erec"><strong>0.657%</strong></td>
      <td class="col-rmse-e"><strong>2.487</strong></td>
      <td class="col-rmse-r2"><strong>0.0373</strong></td>
    </tr>
    <tr>
      <td class="col-scenario">
        <span class="scenario-title">G2: Ground-based:</span><br>
        <span class="scenario-sub">optical + atmospheric (<em>K</em> = 8)</span>
      </td>
      <td class="col-algo">Universal Kriging<br><span class="algo-sub">(Quad)</span></td>
      <td class="col-erec">0.795%</td>
      <td class="col-rmse-e">3.206</td>
      <td class="col-rmse-r2">0.0450</td>
    </tr>
    <tr>
      <td class="col-scenario">
        <span class="scenario-title">S1: Space Diffraction</span><br>
        <span class="scenario-sub">Optics (<em>K</em> = 9)</span>
      </td>
      <td class="col-algo">Universal Kriging<br><span class="algo-sub">(Quad)</span></td>
      <td class="col-erec">0.136%</td>
      <td class="col-rmse-e"><strong>0.359</strong></td>
      <td class="col-rmse-r2"><strong>0.0018</strong></td>
    </tr>
    <tr>
      <td class="col-scenario">
        <span class="scenario-title">S1: Space Diffraction</span><br>
        <span class="scenario-sub">Optics (<em>K</em> = 9)</span>
      </td>
      <td class="col-algo">Polynomial<br><span class="algo-sub">(deg 4)</span></td>
      <td class="col-erec"><strong>0.111%</strong></td>
      <td class="col-rmse-e">0.368</td>
      <td class="col-rmse-r2">0.0024</td>
    </tr>
  </tbody>
</table>
</body>
</html>
"""

def generate_table():
    temp_html = PROJECT_ROOT / "scratch" / "temp_table_3.html"
    temp_html.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    temp_screenshot = PROJECT_ROOT / "scratch" / "table_3_raw.png"

    cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--force-device-scale-factor=2",
        f"--screenshot={temp_screenshot}",
        "--window-size=1200,1200",
        f"file://{temp_html}"
    ]

    subprocess.run(cmd, check=True, capture_output=True)

    # Crop tightly to non-white pixels
    im = Image.open(temp_screenshot).convert("RGB")
    width, height = im.size
    left, top, right, bottom = width, height, 0, 0
    pixels = im.load()
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if r < 250 or g < 250 or b < 250:
                if x < left: left = x
                if x > right: right = x
                if y < top: top = y
                if y > bottom: bottom = y

    if left < right and top < bottom:
        crop_box = (max(0, left - 1), max(0, top - 1), min(width, right + 2), min(height, bottom + 2))
        cropped = im.crop(crop_box)
        OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(OUTPUT_PNG, "PNG", optimize=True)
        print(f"[OK] Saved cropped Table 3 image to: {OUTPUT_PNG} (Size: {cropped.size})")

    if temp_html.exists():
        temp_html.unlink()
    if temp_screenshot.exists():
        temp_screenshot.unlink()

if __name__ == "__main__":
    generate_table()
