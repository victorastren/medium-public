#!/usr/bin/env python3
"""
Scientific figure rendering and public-asset integrity tests for Article 3:
"Order and Chaos: The Road to Modern Dynamics III"

Covers:
1. Presence, magic headers, and resolution checks for all 25 shipped scientific
   images/animations (.png, .gif, .mp4) and compiled equation images.
2. Exclusion check confirming no cover, portrait, or private editorial artifacts
   are included in the public repository directory.
3. Isolated regeneration of static scientific figures into a temporary directory.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
CODE_DIR = PROJECT_DIR / "code"
IMAGES_DIR = PROJECT_DIR / "images"

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import generate_homoclinic_tangle_to_horseshoe
import generate_horseshoe_symbolic_dynamics
import generate_kam_invariant_tori_picture
import generate_thermal_convection_to_lorenz
import generate_lorenz_attractor
import generate_secular_planetary_evolution
import generate_earth_mars_secular_resonance
import generate_la2010_orbital_divergence
import generate_order_chaos_timeline


class TestFigureGenerationAndAssets(unittest.TestCase):
    """Verify shipped scientific assets, public-repo hygiene, and isolated static figure rendering."""

    def _verify_png(self, path: Path, min_w: int, min_h: int, min_size_kb: int = 30):
        self.assertTrue(path.exists(), f"Missing image: {path}")
        self.assertGreater(path.stat().st_size, min_size_kb * 1024, f"Too small: {path}")
        with open(path, "rb") as f:
            self.assertEqual(f.read(8), b"\x89PNG\r\n\x1a\n", f"Invalid PNG header: {path}")
        with Image.open(path) as img:
            self.assertEqual(img.format, "PNG")
            w, h = img.size
            self.assertGreaterEqual(w, min_w)
            self.assertGreaterEqual(h, min_h)

    def test_shipped_scientific_assets_and_animations(self):
        """Verify all 25 scientific images/animations and compiled math PNGs exist and are valid."""
        static_pngs = [
            "homoclinic_tangle_to_horseshoe.png",
            "horseshoe_symbolic_dynamics.png",
            "kam_invariant_tori_picture.png",
            "kam_poincare_sections.png",
            "thermal_convection_to_lorenz.png",
            "lorenz_attractor.png",
            "secular_planetary_evolution.png",
            "earth_mars_secular_resonance.png",
            "la2010_orbital_divergence.png",
            "order_chaos_predictability_timeline.png",
        ]
        for fname in static_pngs:
            self._verify_png(IMAGES_DIR / fname, 1200, 600)

        anim_bases = [
            "horseshoe_stretching_folding_iterations",
            "unforced_vs_forced_pendulum",
            "pendulum_separatrix_to_homoclinic_chaos",
            "integrable_torus_motion",
            "lorenz_sensitive_dependence",
        ]
        for base in anim_bases:
            self._verify_png(IMAGES_DIR / f"{base}.png", 1200, 600)
            gif_p = IMAGES_DIR / f"{base}.gif"
            mp4_p = IMAGES_DIR / f"{base}.mp4"
            self.assertTrue(gif_p.exists() and gif_p.stat().st_size > 100_000, f"Invalid GIF: {gif_p}")
            self.assertTrue(mp4_p.exists() and mp4_p.stat().st_size > 100_000, f"Invalid MP4: {mp4_p}")
            with open(gif_p, "rb") as f:
                self.assertIn(f.read(6), (b"GIF87a", b"GIF89a"))

        math_pngs = list((IMAGES_DIR / "math").glob("eq_*.png"))
        self.assertGreaterEqual(len(math_pngs), 23, "Expected at least 23 equation PNGs in images/math/")

    def test_no_private_or_excluded_files_in_public_repo(self):
        """Ensure cover images, portrait images/scripts, and raw sources are excluded."""
        forbidden = [
            p for p in PROJECT_DIR.rglob("*")
            if "__pycache__" not in p.parts
            and any(tok in p.name.lower() for tok in ("portrait", "cover", "table_", "article.md", "raw_drafts"))
        ]
        self.assertEqual(forbidden, [], f"Unexpected excluded files found: {forbidden}")
        self.assertFalse((PROJECT_DIR / "sources").exists(), "sources/ directory should not be present")

    def test_isolated_static_figure_generation(self):
        """Generate static scientific figures into a temporary directory and verify PNG integrity."""
        generators = [
            ("homoclinic_tangle_to_horseshoe.png", generate_homoclinic_tangle_to_horseshoe.create_figure, 1600, 800),
            ("horseshoe_symbolic_dynamics.png", generate_horseshoe_symbolic_dynamics.create_figure, 1600, 800),
            ("kam_invariant_tori_picture.png", generate_kam_invariant_tori_picture.create_figure, 1600, 800),
            ("thermal_convection_to_lorenz.png", generate_thermal_convection_to_lorenz.create_figure, 1600, 800),
            ("lorenz_attractor.png", generate_lorenz_attractor.create_figure, 1600, 800),
            ("secular_planetary_evolution.png", generate_secular_planetary_evolution.create_figure, 1600, 800),
            ("earth_mars_secular_resonance.png", generate_earth_mars_secular_resonance.create_figure, 1600, 800),
            ("la2010_orbital_divergence.png", generate_la2010_orbital_divergence.create_figure, 1600, 800),
            ("order_chaos_predictability_timeline.png", generate_order_chaos_timeline.create_timeline, 1500, 500),
        ]
        with tempfile.TemporaryDirectory() as tmp_dir:
            for fname, func, min_w, min_h in generators:
                out_p = Path(tmp_dir) / fname
                func(out_p)
                self._verify_png(out_p, min_w, min_h)


if __name__ == "__main__":
    unittest.main(verbosity=2)
