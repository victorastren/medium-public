#!/usr/bin/env python3
"""
Master runner script to generate all scientific figures and infographic panels
for the article "From Poincaré to Chaos: The Road to Modern Dynamics II".

Usage:
    python3 generate_all_figures.py
or with a custom output directory:
    python3 generate_all_figures.py /path/to/images
"""

import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

# Import generation routines
from generate_poincare_planar_dynamics_infographic import create_figure as generate_planar_infographic
from generate_poincare_bendixson_portraits import create_figure as generate_pb_portraits
from generate_poincare_bendixson_figure import create_figure as generate_pb_theorem
from generate_three_body_solutions_crtbp import create_figure as generate_crtbp
from generate_poincare_return_map_stability import create_figure as generate_return_map
from generate_simple_vs_double_pendulum import create_figure as generate_pendulum_comparison
from generate_classical_vs_forced_pendulum import create_figure as generate_classical_forced
from generate_poincare_sections_double_pendulum import generate_figure as generate_sections
from generate_elliptic_hyperbolic_periodic_points import create_figure as generate_periodic_points
from generate_floquet_birkhoff_portraits import create_figure as generate_fb_portraits
from generate_poincare_birkhoff_figure import create_figure as generate_poincare_birkhoff
from generate_dynamical_systems_timeline import create_timeline as generate_timeline

FIGURE_GENERATORS = [
    ("1. Poincaré Planar Dynamics Infographic", "poincare_planar_dynamics_infographic.png", generate_planar_infographic),
    ("2. Historical Portraits: Poincaré & Bendixson", "poincare_bendixson_portraits.png", generate_pb_portraits),
    ("3. Poincaré–Bendixson Theorem & Limit Cycles", "poincare_bendixson_theorem.png", generate_pb_theorem),
    ("4. Three-Body Problem & CRTBP Equilibria", "three_body_solutions_crtbp.png", generate_crtbp),
    ("5. Poincaré Return Map & Orbit Stability", "poincare_return_map_stability.png", generate_return_map),
    ("6. Simple vs. Double Pendulum Configuration", "simple_vs_double_pendulum.png", generate_pendulum_comparison),
    ("7. Classical vs. Forced Dissipative Pendulum", "classical_vs_forced_pendulum.png", generate_classical_forced),
    ("8. Poincaré Sections of Conservative Double Pendulum", "poincare_sections_double_pendulum.png", lambda p: generate_sections(output_png=p)),
    ("9. Elliptic & Hyperbolic Periodic Points", "elliptic_hyperbolic_periodic_points.png", generate_periodic_points),
    ("10. Historical Portraits: Floquet & Birkhoff", "floquet_birkhoff_portraits.png", generate_fb_portraits),
    ("11. Poincaré–Birkhoff Twist Theorem", "poincare_birkhoff_theorem.png", generate_poincare_birkhoff),
    ("12. Historical Timeline of Dynamical Systems", "dynamical_systems_timeline.png", generate_timeline),
]


def generate_all(output_dir=None):
    if output_dir is None:
        output_dir = DEFAULT_IMAGES_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" From Poincaré to Chaos: The Road to Modern Dynamics II - Figure Pipeline")
    print(f" Target Directory: {output_dir}")
    print("=" * 80)

    total_start = time.time()
    success_count = 0

    for idx, (title, filename, func) in enumerate(FIGURE_GENERATORS, start=1):
        target_path = output_dir / filename
        print(f"\n[{idx:2d}/{len(FIGURE_GENERATORS)}] Generating: {title}...")
        t0 = time.time()
        try:
            func(target_path)
            dt = time.time() - t0
            size_kb = target_path.stat().st_size / 1024.0
            print(f"       ✓ Saved to {filename} ({size_kb:.1f} KB in {dt:.2f}s)")
            success_count += 1
        except Exception as e:
            print(f"       ✗ FAILED to generate {filename}: {e}")

    total_time = time.time() - total_start
    print("\n" + "=" * 80)
    print(f" Pipeline Complete: {success_count}/{len(FIGURE_GENERATORS)} figures successfully generated in {total_time:.2f}s.")
    print("=" * 80)

    return success_count == len(FIGURE_GENERATORS)


if __name__ == '__main__':
    custom_dir = sys.argv[1] if len(sys.argv) > 1 else None
    success = generate_all(custom_dir)
    sys.exit(0 if success else 1)
