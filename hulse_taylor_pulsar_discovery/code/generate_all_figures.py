#!/usr/bin/env python3
"""
Master runner script to generate all 7 scientific infographics
for the Hulse-Taylor Binary Pulsar (PSR B1913+16) discovery article.

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
from generate_pulsar_infographic import generate_pulsar_infographic
from generate_doppler_orbit_infographic import generate_doppler_orbit_infographic
from generate_hulse_discovery_evidence import generate_hulse_discovery_evidence
from generate_keplerian_orbit_infographic import generate_keplerian_orbit_infographic
from generate_radial_velocity_curve import generate_radial_velocity_curve
from generate_mass_mass_diagram import generate_mass_mass_diagram
from generate_period_decay_infographic import generate_period_decay_infographic

FIGURE_GENERATORS = [
    ("1. Pulsar Lighthouse Model", "pulsar_lighthouse_infographic.png", generate_pulsar_infographic),
    ("2. Binary Orbit Doppler Effect", "binary_orbit_doppler_infographic.png", generate_doppler_orbit_infographic),
    ("3. Hulse 1974 Discovery Evidence", "hulse_discovery_evidence.png", generate_hulse_discovery_evidence),
    ("4. Keplerian Orbit Geometry", "keplerian_orbit_geometry.png", generate_keplerian_orbit_infographic),
    ("5. Radial Velocity Doppler Curve", "radial_velocity_doppler_curve.png", generate_radial_velocity_curve),
    ("6. Mass-Mass Constraint Plane", "mass_mass_diagram.png", generate_mass_mass_diagram),
    ("7. Cumulative Orbital Period Decay", "psr_period_decay_infographic.png", generate_period_decay_infographic),
]


def generate_all(output_dir=None):
    if output_dir is None:
        output_dir = DEFAULT_IMAGES_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print(" Hulse-Taylor Binary Pulsar (PSR B1913+16) - Figure Generation Pipeline")
    print(f" Target Directory: {output_dir}")
    print("=" * 72)

    total_start = time.time()
    success_count = 0

    for idx, (title, filename, func) in enumerate(FIGURE_GENERATORS, start=1):
        target_path = output_dir / filename
        print(f"\n[{idx}/7] Generating: {title}...")
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
