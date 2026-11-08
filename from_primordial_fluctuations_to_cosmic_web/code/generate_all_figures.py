#!/usr/bin/env python3
"""
Master runner script to generate all scientific figures, cosmological plots,
and historical timeline infographics for the article:
"From a Nearly Uniform Universe to Galaxies and the Cosmic Web".

Usage:
    python3 code/generate_all_figures.py
or with a custom output directory:
    python3 code/generate_all_figures.py /path/to/images
"""

import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from generate_cmb_to_cosmic_web import create_figure as generate_cmb_web
from generate_jeans_dispersion_relation import create_figure as generate_jeans
from generate_cosmic_expansion_coordinates import create_figure as generate_expansion
from generate_spatial_curvature_friedmann import create_figure as generate_curvature
from generate_horizons_and_perturbation_scales import create_figure as generate_horizons
from generate_cosmological_perturbations_timeline import create_timeline as generate_tl_perturbations
from generate_quantum_fluctuations_inflation import create_figure as generate_quantum_fluctuations
from generate_primordial_power_spectrum import create_figure as generate_primordial_spectrum
from generate_primordial_fluctuations_timeline import create_timeline as generate_tl_primordial
from generate_horizon_entry import create_figure as generate_horizon_entry
from generate_photon_baryon_acoustic_oscillations import create_figure as generate_bao
from generate_cdm_baryon_evolution import create_figure as generate_cdm_baryon
from generate_matter_transfer_power_spectrum import create_figure as generate_transfer_power
from generate_perturbation_evolution_timeline import create_timeline as generate_tl_evolution
from generate_anisotropic_collapse_cosmic_web import create_figure as generate_anisotropic_collapse
from generate_cosmic_web_timeline import create_timeline as generate_tl_cosmic_web
from generate_dark_energy_structure_growth import create_figure as generate_dark_energy
from generate_dark_energy_timeline import create_timeline as generate_tl_dark_energy

FIGURE_GENERATORS = [
    ("1. CMB to Cosmic Web Comparison", "cmb_to_cosmic_web.png", generate_cmb_web),
    ("2. Jeans Instability Dispersion Relation", "jeans_instability_dispersion_relation.png", generate_jeans),
    ("3. Cosmic Expansion in Physical & Comoving Coordinates", "cosmic_expansion_coordinates.png", generate_expansion),
    ("4. Spatial Curvature & Friedmann Geometry", "spatial_curvature_friedmann.png", generate_curvature),
    ("5. Particle Horizon, Hubble Radius & Perturbation Scales", "particle_horizon_hubble_radius.png", generate_horizons),
    ("6. Timeline: From Jeans to Bardeen (1902–1980)", "cosmological_perturbations_timeline.png", generate_tl_perturbations),
    ("7. From Quantum Fluctuations to Primordial Perturbations", "quantum_fluctuations_primordial_perturbations.png", generate_quantum_fluctuations),
    ("8. Primordial Curvature Power Spectrum", "primordial_power_spectrum.png", generate_primordial_spectrum),
    ("9. Timeline: Primordial Fluctuations & Inflation (1970–1982)", "primordial_fluctuations_timeline.png", generate_tl_primordial),
    ("10. Comoving Hubble Radius & Horizon Entry", "horizon_entry_perturbations.png", generate_horizon_entry),
    ("11. Photon–Baryon Acoustic Oscillations & Silk Damping", "photon_baryon_acoustic_oscillations.png", generate_bao),
    ("12. Cold Dark Matter vs. Baryon Perturbation Evolution", "cdm_baryon_perturbation_evolution.png", generate_cdm_baryon),
    ("13. Matter Transfer Function & Linear Matter Power Spectrum", "matter_transfer_function_power_spectrum.png", generate_transfer_power),
    ("14. Timeline: Acoustic Oscillations to Matter Power Spectrum (1965–2005)", "perturbation_evolution_timeline.png", generate_tl_evolution),
    ("15. Anisotropic Gravitational Collapse & Cosmic Web", "anisotropic_collapse_cosmic_web.png", generate_anisotropic_collapse),
    ("16. Timeline: Nonlinear Collapse to the Cosmic Web (1967–1996)", "cosmic_web_timeline.png", generate_tl_cosmic_web),
    ("17. Dark Energy & Suppression of Structure Growth", "dark_energy_structure_growth.png", generate_dark_energy),
    ("18. Timeline: Cosmological Constant & Accelerating Expansion (1977–1999)", "dark_energy_timeline.png", generate_tl_dark_energy),
]


def generate_all(output_dir=None):
    if output_dir is None:
        output_dir = DEFAULT_IMAGES_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" From a Nearly Uniform Universe to Galaxies and the Cosmic Web - Figure Pipeline")
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


if __name__ == "__main__":
    custom_dir = sys.argv[1] if len(sys.argv) > 1 else None
    success = generate_all(custom_dir)
    sys.exit(0 if success else 1)

