#!/usr/bin/env python3
"""
Master runner script to generate all 5 scientific infographics and figures
for the Dynamical Systems: Interpreting Motion article.

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

# Import individual generation routines
from generate_state_space_transition import create_figure as generate_state_space_transition
from generate_phase_portrait import create_figure as generate_phase_portrait
from generate_local_stability_classification import create_figure as generate_stability_classification
from generate_dissipation_phase_portrait import create_figure as generate_dissipation_phase_portrait
from generate_poincare_return_map import create_figure as generate_poincare_return_map

FIGURE_GENERATORS = [
    ("1. From Physical Motion to State Space", "state_space_transition.png", generate_state_space_transition),
    ("2. Nonlinear Pendulum Phase Portrait", "pendulum_phase_portrait.png", generate_phase_portrait),
    ("3. Local Stability Classification (4-Panel)", "local_stability_classification.png", generate_stability_classification),
    ("4. Dissipation and Attractors (2-Panel)", "dissipation_phase_portrait.png", generate_dissipation_phase_portrait),
    ("5. Poincaré Section & Return Map (2-Panel)", "poincare_return_map.png", generate_poincare_return_map),
]


def generate_all(output_dir=None):
    if output_dir is None:
        output_dir = DEFAULT_IMAGES_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 76)
    print(" Dynamical Systems: Interpreting Motion - Figure Generation Pipeline")
    print(f" Target Directory: {output_dir}")
    print("=" * 76)

    total_start = time.time()
    success_count = 0

    for idx, (title, filename, func) in enumerate(FIGURE_GENERATORS, start=1):
        target_path = output_dir / filename
        print(f"\n[{idx}/{len(FIGURE_GENERATORS)}] Generating: {title} ...")
        start = time.time()
        try:
            func(target_path)
            elapsed = time.time() - start
            size_kb = target_path.stat().st_size / 1024
            print(f"    --> Saved: {target_path.name} ({size_kb:.1f} KB in {elapsed:.2f}s)")
            success_count += 1
        except Exception as e:
            print(f"    --> ERROR generating {filename}: {e}", file=sys.stderr)

    total_elapsed = time.time() - total_start
    print("\n" + "=" * 76)
    print(f" Successfully generated {success_count}/{len(FIGURE_GENERATORS)} figures in {total_elapsed:.2f}s.")
    print("=" * 76)
    return success_count == len(FIGURE_GENERATORS)


if __name__ == "__main__":
    out_arg = sys.argv[1] if len(sys.argv) > 1 else None
    success = generate_all(out_arg)
    sys.exit(0 if success else 1)
