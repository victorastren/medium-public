#!/usr/bin/env python3
"""
Master runner script to generate all 7 scientific infographics
for the Navier-Stokes Blow-Up and Regularity article.

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
from generate_material_derivative_infographic import generate_material_derivative_infographic
from generate_vortex_stretching_infographic import generate_vortex_stretching_infographic
from generate_vortex_stretching_2d_infographic import generate_vortex_stretching_2d_infographic
from generate_energy_balance_infographic import generate_energy_balance_infographic
from generate_energy_concentration_infographic import generate_energy_concentration_infographic
from generate_scaling_limits_infographic import generate_scaling_limits_infographic
from generate_shrinking_vortex_infographic import generate_shrinking_vortex_infographic

FIGURE_GENERATORS = [
    ("1. Eulerian vs Lagrangian Derivative", "eulerian_vs_lagrangian_derivative.png", generate_material_derivative_infographic),
    ("2. 3D Vortex Stretching Mechanism", "vortex_stretching_mechanism.png", generate_vortex_stretching_infographic),
    ("3. 2D Vanishing Stretching", "vortex_stretching_2d_vanishing.png", generate_vortex_stretching_2d_infographic),
    ("4. Energy Balance & Viscous Dissipation", "navier_stokes_energy_balance.png", generate_energy_balance_infographic),
    ("5. Finite Energy Concentration", "finite_energy_concentration.png", generate_energy_concentration_infographic),
    ("6. Scaling Limits & Supercriticality", "navier_stokes_scaling_limits.png", generate_scaling_limits_infographic),
    ("7. Shrinking Vortex Blow-Up", "navier_stokes_shrinking_vortex_blowup.png", generate_shrinking_vortex_infographic),
]


def generate_all(output_dir=None):
    if output_dir is None:
        output_dir = DEFAULT_IMAGES_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print(" Navier-Stokes Blow-Up & Regularity - Figure Generation Pipeline")
    print(f" Target Directory: {output_dir}")
    print("=" * 72)

    total_start = time.time()
    success_count = 0

    for idx, (title, filename, func) in enumerate(FIGURE_GENERATORS, start=1):
        target_path = output_dir / filename
        print(f"\n[{idx}/{len(FIGURE_GENERATORS)}] Generating: {title}...")
        t0 = time.time()
        try:
            func(target_path)
            dt = time.time() - t0
            size_kb = target_path.stat().st_size / 1024.0
            print(f"      ✓ Saved to {filename} ({size_kb:.1f} KB in {dt:.2f}s)")
            success_count += 1
        except Exception as e:
            print(f"      ✗ FAILED to generate {filename}: {e}")

    total_time = time.time() - total_start
    print("\n" + "=" * 72)
    print(f" Pipeline Complete: {success_count}/{len(FIGURE_GENERATORS)} figures successfully generated in {total_time:.2f}s.")
    print("=" * 72)

    return success_count == len(FIGURE_GENERATORS)


if __name__ == '__main__':
    custom_dir = sys.argv[1] if len(sys.argv) > 1 else None
    success = generate_all(custom_dir)
    sys.exit(0 if success else 1)
