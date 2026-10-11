#!/usr/bin/env python3
"""
Master runner script to generate all 6 core scientific figures and infographics
for the 1922 Wallal Solar Eclipse light-deflection experiment article.

Can be run directly from any directory:
    python3 generate_all_figures.py
or with a custom output directory:
    python3 generate_all_figures.py /path/to/output_dir
"""

from pathlib import Path
import sys
import time

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

# Import generation routines
from generate_light_deflection_diagram import generate_deflection_diagram
from generate_predictions_comparison import generate_comparison_diagram
from generate_wallal_experimental_design import create_schematic as create_experimental_design
from generate_wallal_cameras_schematic import create_schematic as create_cameras_schematic
from generate_plate_measurement_schematic import generate_schematic as generate_plate_schematic
from generate_deflection_results import create_results_plot

FIGURE_GENERATORS = [
    (
        "1. Gravitational Light Deflection Geometry",
        "light_deflection_geometry.png",
        lambda out_dir: generate_deflection_diagram(out_dir=out_dir, filename_prefix="light_deflection_geometry"),
    ),
    (
        "2. Light Deflection Predictions Comparison",
        "deflection_predictions_comparison.png",
        lambda out_dir: generate_comparison_diagram(out_dir=out_dir, filename_prefix="deflection_predictions_comparison"),
    ),
    (
        "3. Wallal Astrometric Experimental Design",
        "wallal_experimental_design.png",
        lambda out_dir: create_experimental_design(output_path=out_dir / "wallal_experimental_design.png"),
    ),
    (
        "4. Twin 15-Foot Einstein Cameras Schematic",
        "wallal_twin_cameras_schematic.png",
        lambda out_dir: create_cameras_schematic(output_path=out_dir / "wallal_twin_cameras_schematic.png"),
    ),
    (
        "5. Photographic Plate Differential Reduction Method",
        "wallal_plate_measurement_method.png",
        lambda out_dir: generate_plate_schematic(
            output_path=out_dir / "wallal_plate_measurement_method.png",
            output_path_2x=out_dir / "wallal_plate_measurement_method_2x.png",
        ),
    ),
    (
        "6. Wallal Deflection Results & Theoretical Predictions",
        "wallal_deflection_results.png",
        lambda out_dir: create_results_plot(
            out_1x=out_dir / "wallal_deflection_results.png",
            out_2x=out_dir / "wallal_deflection_results_2x.png",
        ),
    ),
]


def generate_all(output_dir=None):
    if output_dir is None:
        output_dir = DEFAULT_IMAGES_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 76)
    print(" 1922 Solar Eclipse (Wallal Experiment) - Figure Generation Pipeline")
    print(f" Target Directory: {output_dir}")
    print("=" * 76)

    total_start = time.time()
    success_count = 0

    for idx, (title, filename, func) in enumerate(FIGURE_GENERATORS, start=1):
        target_path = output_dir / filename
        print(f"\n[{idx}/{len(FIGURE_GENERATORS)}] Generating: {title}...")
        t0 = time.time()
        try:
            func(output_dir)
            dt = time.time() - t0
            size_kb = target_path.stat().st_size / 1024.0
            print(f"      ✓ Saved to {filename} ({size_kb:.1f} KB in {dt:.2f}s)")
            success_count += 1
        except Exception as e:
            print(f"      ✗ FAILED to generate {filename}: {e}")

    total_time = time.time() - total_start
    print("\n" + "=" * 76)
    print(f" Pipeline Complete: {success_count}/{len(FIGURE_GENERATORS)} figures successfully generated in {total_time:.2f}s.")
    print("=" * 76)

    return success_count == len(FIGURE_GENERATORS)


if __name__ == '__main__':
    custom_dir = sys.argv[1] if len(sys.argv) > 1 else None
    success = generate_all(custom_dir)
    sys.exit(0 if success else 1)
