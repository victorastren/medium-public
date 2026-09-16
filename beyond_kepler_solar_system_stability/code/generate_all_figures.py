#!/usr/bin/env python3
"""
Master runner script to generate all 10 scientific infographics and figures
for the Beyond Kepler: Perturbations and the Stability of the Solar System article.

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
from generate_osculating_orbit_infographic import generate_osculating_orbit_infographic
from generate_two_timescales_orbit import create_two_timescales_orbit
from generate_disturbing_function_geometry import create_disturbing_function_geometry
from generate_disturbing_function_pipeline import create_disturbing_function_pipeline
from generate_orbital_averaging_infographic import create_orbital_averaging_infographic
from generate_timescale_hierarchy import create_timescale_hierarchy
from generate_eccentricity_vector import create_eccentricity_vector_figure
from generate_secular_normal_modes import create_secular_normal_modes_figure
from generate_great_inequality_infographic import generate_figure as generate_great_inequality_figure
from generate_long_term_evolution_regimes import generate_figure as generate_long_term_evolution_figure

FIGURE_GENERATORS = [
    ("1. Instantaneous Osculating Orbit", "osculating_orbit_concept.png", generate_osculating_orbit_infographic),
    ("2. Two Timescales in Planetary Orbit", "two_timescales_orbit.png", create_two_timescales_orbit),
    ("3. Geometry of Disturbing Function", "disturbing_function_geometry.png", create_disturbing_function_geometry),
    ("4. Disturbing Function to Orbital Evolution", "disturbing_function_pipeline.png", create_disturbing_function_pipeline),
    ("5. Orbital Averaging Concept", "orbital_averaging_concept.png", create_orbital_averaging_infographic),
    ("6. Timescale Hierarchy in Solar System", "timescale_hierarchy.png", create_timescale_hierarchy),
    ("7. Eccentricity Vector in (k,h) Plane", "eccentricity_vector.png", create_eccentricity_vector_figure),
    ("8. Secular Normal Modes in Two-Planet System", "secular_normal_modes.png", create_secular_normal_modes_figure),
    ("9. Great Inequality 5:2 Commensurability", "great_inequality_commensurability.png", generate_great_inequality_figure),
    ("10. Long-Term Orbital Evolution Regimes", "long_term_orbital_evolution.png", generate_long_term_evolution_figure),
]


def generate_all(output_dir=None):
    if output_dir is None:
        output_dir = DEFAULT_IMAGES_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 76)
    print(" Beyond Kepler: Solar System Stability - Figure Generation Pipeline")
    print(f" Target Directory: {output_dir}")
    print("=" * 76)

    total_start = time.time()
    success_count = 0

    for idx, (title, filename, func) in enumerate(FIGURE_GENERATORS, start=1):
        target_path = output_dir / filename
        print(f"\n[{idx}/10] Generating: {title}...")
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
