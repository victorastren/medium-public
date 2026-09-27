#!/usr/bin/env python3
"""
Master runner script to generate all 6 scientific figures and portrait panels
for the article "From Newton to Hamilton: The Road to Modern Dynamics".

Usage:
    python3 generate_all_figures.py
or with custom output directory:
    python3 generate_all_figures.py /path/to/images
"""

from pathlib import Path
import sys
import time

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

# Import generation routines
from generate_pendulum_coordinate_transition import create_figure as generate_pendulum_transition
from generate_analytical_mechanics_portraits import create_figure as generate_analytical_portraits
from generate_generalized_coordinates import create_figure as generate_generalized_coordinates
from generate_lagrange_vs_hamilton_comparison import create_figure as generate_lagrange_vs_hamilton
from generate_pendulum_phase_portrait import create_figure as generate_pendulum_phase_portrait
from generate_hamilton_jacobi_portraits import create_figure as generate_hamilton_jacobi_portraits

FIGURE_GENERATORS = [
    ("1. Pendulum Coordinate Transition (Cartesian to Generalized)", "pendulum_coordinate_transition.png", generate_pendulum_transition),
    ("2. Pioneers of Analytical Mechanics (Euler, d'Alembert, Lagrange)", "analytical_mechanics_portraits.png", generate_analytical_portraits),
    ("3. Generalized Coordinates & Degrees of Freedom Taxonomy", "generalized_coordinates.png", generate_generalized_coordinates),
    ("4. Lagrangian vs. Hamiltonian Mechanics Comparison", "lagrange_vs_hamilton_comparison.png", generate_lagrange_vs_hamilton),
    ("5. Nonlinear Pendulum Phase Space & Separatrix", "pendulum_phase_portrait.png", generate_pendulum_phase_portrait),
    ("6. Masters of Canonical Dynamics (Hamilton & Jacobi)", "hamilton_jacobi_portraits.png", generate_hamilton_jacobi_portraits),
]


def generate_all(output_dir=None):
    if output_dir is None:
        output_dir = DEFAULT_IMAGES_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 76)
    print(" From Newton to Hamilton: The Road to Modern Dynamics - Figure Pipeline")
    print(f" Target Directory: {output_dir}")
    print("=" * 76)

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
    print("\n" + "=" * 76)
    print(f" Pipeline Complete: {success_count}/{len(FIGURE_GENERATORS)} figures successfully generated in {total_time:.2f}s.")
    print("=" * 76)

    return success_count == len(FIGURE_GENERATORS)


if __name__ == '__main__':
    custom_dir = sys.argv[1] if len(sys.argv) > 1 else None
    success = generate_all(custom_dir)
    sys.exit(0 if success else 1)
