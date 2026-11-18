#!/usr/bin/env python3
"""
Master runner script to generate all scientific figures and animations for:
"The Golden Age of Black Hole Physics (1963–1974)".

Usage:
    python3 code/generate_all_figures.py
    python3 code/generate_all_figures.py --static-only
or with a custom output directory:
    python3 code/generate_all_figures.py /path/to/images
"""

import argparse
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_bekenstein_gsl
import generate_black_hole_perturbations_ringdown
import generate_boyer_lindquist_coordinates
import generate_from_curvature_to_kerr_solution
import generate_geodesic_orbits_schwarzschild_kerr
import generate_hawking_area_theorem
import generate_hawking_radiation_collapse_spectrum
import generate_kerr_black_hole_anatomy
import generate_lense_thirring_animation
import generate_lense_thirring_frame_dragging
import generate_oppenheimer_snyder_collapse
import generate_penrose_process


STATIC_GENERATORS = [
    (
        "1. Oppenheimer–Snyder Gravitational Collapse",
        "oppenheimer_snyder_collapse.png",
        generate_oppenheimer_snyder_collapse.create_figure,
    ),
    (
        "2. Lense–Thirring Frame Dragging",
        "lense_thirring_frame_dragging.png",
        generate_lense_thirring_frame_dragging.create_figure,
    ),
    (
        "3. Kerr Black Hole Anatomy",
        "kerr_black_hole_anatomy.png",
        generate_kerr_black_hole_anatomy.create_figure,
    ),
    (
        "4. Black Hole Perturbations & Ringdown",
        "black_hole_perturbations_ringdown.png",
        generate_black_hole_perturbations_ringdown.create_figure,
    ),
    (
        "5. Hawking Area Theorem",
        "hawking_area_theorem.png",
        generate_hawking_area_theorem.create_figure,
    ),
    (
        "6. Hawking Radiation & Collapse Spectrum",
        "hawking_radiation_collapse_spectrum.png",
        generate_hawking_radiation_collapse_spectrum.create_figure,
    ),
]


def _run_curvature_to_kerr(output_dir: Path, static_only: bool) -> Path:
    mod = generate_from_curvature_to_kerr_solution
    png_out = output_dir / "from_curvature_to_kerr_solution.png"
    mod.PNG_OUT = png_out
    mod.GIF_OUT = output_dir / "from_curvature_to_kerr_solution_animation.gif"
    mod.MP4_OUT = output_dir / "from_curvature_to_kerr_solution_animation.mp4"
    if static_only:
        mod.validate_optical_models()
        mod.render_frame((mod.N_MOTION_FRAMES - 1, str(png_out)))
    else:
        mod.main()
    return png_out


def _run_boyer_lindquist(output_dir: Path, static_only: bool) -> Path:
    mod = generate_boyer_lindquist_coordinates
    png_out = output_dir / "boyer_lindquist_coordinates.png"
    mod.PNG_OUT = png_out
    mod.GIF_OUT = output_dir / "boyer_lindquist_coordinates_animation.gif"
    mod.MP4_OUT = output_dir / "boyer_lindquist_coordinates_animation.mp4"
    if static_only:
        mod.render_scene(a_val=mod.A_MAX, is_static=True, output_path=png_out)
    else:
        mod.generate_all()
    return png_out


def _run_geodesic_orbits(output_dir: Path, static_only: bool) -> Path:
    mod = generate_geodesic_orbits_schwarzschild_kerr
    png_out = output_dir / "geodesic_orbits_schwarzschild_kerr.png"
    mod.LOCAL_IMAGES_DIR = output_dir
    mod.STATIC_OUT = png_out
    mod.GIF_OUT = output_dir / "geodesic_orbits_schwarzschild_kerr_animation.gif"
    mod.MP4_OUT = output_dir / "geodesic_orbits_schwarzschild_kerr_animation.mp4"
    if static_only:
        data = mod.precompute_orbits()
        mod.draw_frame(data, phase=mod.N_CYCLES, elev=mod.FIXED_ELEV, azim=mod.FIXED_AZIM, output_path=png_out, is_static=True)
    else:
        mod.generate_assets()
    return png_out


def _run_penrose_process(output_dir: Path, static_only: bool) -> Path:
    mod = generate_penrose_process
    png_out = output_dir / "penrose_process.png"
    mod.LOCAL_IMAGES_DIR = output_dir
    mod.STATIC_OUT = png_out
    mod.GIF_OUT = output_dir / "penrose_process_animation.gif"
    mod.MP4_OUT = output_dir / "penrose_process_animation.mp4"
    if static_only:
        data = mod.precompute_penrose_geodesics()
        mod.draw_frame(data, frame_idx=mod.N_FRAMES - 1, output_path=png_out, is_static=True)
    else:
        mod.generate_assets()
    return png_out


def _run_bekenstein_gsl(output_dir: Path, static_only: bool) -> Path:
    mod = generate_bekenstein_gsl
    png_out = output_dir / "bekenstein_gsl.png"
    mod.IMAGES_DIR = output_dir
    mod.STATIC_OUT = png_out
    mod.GIF_OUT = output_dir / "bekenstein_gsl_animation.gif"
    mod.MP4_OUT = output_dir / "bekenstein_gsl_animation.mp4"
    if static_only:
        mod.draw_frame(mod.N_FRAMES - 1, png_out, is_static=True)
    else:
        mod.generate_assets()
    return png_out


def _run_lense_thirring_anim(output_dir: Path, static_only: bool) -> Path:
    mod = generate_lense_thirring_animation
    gif_out = output_dir / "lense_thirring_frame_dragging_animation.gif"
    mod.GIF_OUT = gif_out
    mod.MP4_OUT = output_dir / "lense_thirring_frame_dragging_animation.mp4"
    if not static_only:
        mod.generate_animation()
    return gif_out


def generate_all(output_dir=None, static_only: bool = False) -> bool:
    """Run all scientific figure and animation generators into output_dir."""
    if output_dir is None:
        output_dir = DEFAULT_IMAGES_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" The Golden Age of Black Hole Physics (1963–1974) - Scientific Figure Pipeline")
    print(f" Target Directory: {output_dir}")
    print(f" Mode: {'static-only' if static_only else 'full (static + GIF/MP4 animations)'}")
    print("=" * 80)

    tasks = []
    for title, filename, func in STATIC_GENERATORS:
        tasks.append((title, lambda out, fn=func, fn_name=filename: _invoke_static(fn, out / fn_name)))

    tasks.extend([
        ("7. From Curvature to the Kerr Solution (Poster & Animation)", lambda out: _run_curvature_to_kerr(out, static_only)),
        ("8. Boyer–Lindquist Coordinates (Poster & Animation)", lambda out: _run_boyer_lindquist(out, static_only)),
        ("9. Bound Geodesic Orbits in Schwarzschild & Kerr (Poster & Animation)", lambda out: _run_geodesic_orbits(out, static_only)),
        ("10. Penrose Rotational Energy Extraction (Poster & Animation)", lambda out: _run_penrose_process(out, static_only)),
        ("11. Bekenstein Generalized Second Law (Poster & Animation)", lambda out: _run_bekenstein_gsl(out, static_only)),
    ])
    if not static_only:
        tasks.append(("12. Lense–Thirring Frame Dragging (Animation)", lambda out: _run_lense_thirring_anim(out, False)))

    total_start = time.time()
    success_count = 0

    for idx, (title, runner) in enumerate(tasks, start=1):
        print(f"\n[{idx:2d}/{len(tasks)}] Generating: {title}...")
        t0 = time.time()
        try:
            target_path = runner(output_dir)
            dt = time.time() - t0
            size_kb = target_path.stat().st_size / 1024.0
            print(f"       ✓ Saved {target_path.name} ({size_kb:.1f} KB in {dt:.2f}s)")
            success_count += 1
        except Exception as e:
            print(f"       ✗ FAILED {title}: {e}")

    total_time = time.time() - total_start
    print("\n" + "=" * 80)
    print(f" Pipeline Complete: {success_count}/{len(tasks)} tasks succeeded in {total_time:.2f}s.")
    print("=" * 80)

    return success_count == len(tasks)


def _invoke_static(func, target_path: Path) -> Path:
    func(target_path)
    return target_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate scientific figures and animations.")
    parser.add_argument("output_dir", nargs="?", default=None, help="Optional custom output directory for generated assets.")
    parser.add_argument("--static-only", action="store_true", help="Render only static figures and poster PNGs (skip MP4/GIF rendering).")
    args = parser.parse_args()
    success = generate_all(args.output_dir, static_only=args.static_only)
    sys.exit(0 if success else 1)

