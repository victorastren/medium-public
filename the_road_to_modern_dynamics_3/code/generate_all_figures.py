#!/usr/bin/env python3
"""
Master runner script to generate all static scientific figures (and optionally
animations) for the article:
"Order and Chaos: The Road to Modern Dynamics III".

Usage:
    python3 code/generate_all_figures.py
    python3 code/generate_all_figures.py /path/to/images
    python3 code/generate_all_figures.py --include-animations
"""

import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from generate_homoclinic_tangle_to_horseshoe import create_figure as generate_homoclinic_horseshoe
from generate_horseshoe_symbolic_dynamics import create_figure as generate_symbolic_dynamics
from generate_kam_invariant_tori_picture import create_figure as generate_kam_picture
from generate_kam_poincare_sections import create_figure as generate_kam_poincare
from generate_thermal_convection_to_lorenz import create_figure as generate_thermal_lorenz
from generate_lorenz_attractor import create_figure as generate_lorenz_attractor
from generate_secular_planetary_evolution import create_figure as generate_secular_evolution
from generate_earth_mars_secular_resonance import create_figure as generate_earth_mars_resonance
from generate_la2010_orbital_divergence import create_figure as generate_la2010_divergence
from generate_order_chaos_timeline import create_timeline as generate_timeline

FIGURE_GENERATORS = [
    ("1. Homoclinic Tangle to Smale's Horseshoe", "homoclinic_tangle_to_horseshoe.png", generate_homoclinic_horseshoe),
    ("2. Symbolic Dynamics in Smale's Horseshoe", "horseshoe_symbolic_dynamics.png", generate_symbolic_dynamics),
    ("3. KAM Theory: Invariant Tori & Resonances", "kam_invariant_tori_picture.png", generate_kam_picture),
    ("4. KAM Poincaré Sections of Driven Pendulum", "kam_poincare_sections.png", lambda p: generate_kam_poincare(output_path=p)),
    ("5. From Thermal Convection to Lorenz Equations", "thermal_convection_to_lorenz.png", generate_thermal_lorenz),
    ("6. The Lorenz Attractor in 3D Phase Space", "lorenz_attractor.png", generate_lorenz_attractor),
    ("7. Secular Evolution of a Planetary Orbit", "secular_planetary_evolution.png", generate_secular_evolution),
    ("8. Earth–Mars Secular Resonance (La2010a–d)", "earth_mars_secular_resonance.png", generate_earth_mars_resonance),
    ("9. Divergence of La2010 Orbital Solutions", "la2010_orbital_divergence.png", generate_la2010_divergence),
    ("10. Historical Timeline: From Poincaré to Laskar", "order_chaos_predictability_timeline.png", generate_timeline),
]

ANIMATION_SCRIPTS = [
    ("A1. Smale's Horseshoe Stretching & Folding Iterations", "generate_horseshoe_iterations_animation.py"),
    ("A2. Unforced vs. Periodically Forced Pendulum", "generate_unforced_vs_forced_pendulum.py"),
    ("A3. Pendulum Separatrix to Homoclinic Chaos", "generate_pendulum_homoclinic_chaos_animation.py"),
    ("A4. Integrable Systems & Invariant Torus Motion", "generate_integrable_torus_animation.py"),
    ("A5. Sensitive Dependence in the Lorenz System", "generate_lorenz_sensitive_dependence_animation.py"),
]


def generate_all(output_dir=None, include_animations=False):
    if output_dir is None:
        output_dir = DEFAULT_IMAGES_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" Order and Chaos: The Road to Modern Dynamics III — Figure Pipeline")
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

    anim_ok = True
    if include_animations:
        print("\n" + "-" * 80)
        print(" Running Scientific Animation Scripts (requires ffmpeg on PATH)")
        print("-" * 80)
        for title, script_name in ANIMATION_SCRIPTS:
            print(f"\n[Anim] Running: {title} ({script_name})...")
            t0 = time.time()
            try:
                subprocess.run([sys.executable, str(SCRIPT_DIR / script_name)], check=True)
                print(f"       ✓ Completed {script_name} in {time.time() - t0:.2f}s")
            except Exception as e:
                print(f"       ✗ FAILED {script_name}: {e}")
                anim_ok = False

    total_time = time.time() - total_start
    print("\n" + "=" * 80)
    print(f" Pipeline Complete: {success_count}/{len(FIGURE_GENERATORS)} static figures generated in {total_time:.2f}s.")
    print("=" * 80)

    return (success_count == len(FIGURE_GENERATORS)) and anim_ok


if __name__ == "__main__":
    args = sys.argv[1:]
    include_anims = "--include-animations" in args
    pos_args = [a for a in args if not a.startswith("--")]
    custom_dir = pos_args[0] if pos_args else None
    success = generate_all(custom_dir, include_animations=include_anims)
    sys.exit(0 if success else 1)

