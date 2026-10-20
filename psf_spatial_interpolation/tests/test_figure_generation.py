#!/usr/bin/env python3
"""
Test Suite: PSF Spatial Interpolation - Article Figure Integrity
Validates that all 13 article figures exist, are valid non-corrupt PNG files,
and meet resolution and visual quality thresholds.
"""

from pathlib import Path
import unittest
from PIL import Image

TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
IMAGES_DIR = PROJECT_DIR / "images"

CORE_IMAGES = [
    ("galaxy_psf_convolution_schematic.png", 1000, 400),
    ("spatial_psf_field_grid.png", 1000, 400),
    ("scenarios_galaxy_convolution_comparison.png", 1000, 400),
    ("simulated_stellar_positions.png", 600, 600),
    ("pca_mean_and_components.png", 800, 600),
    ("pca_representation_vs_k.png", 1000, 600),
    ("spatial_interpolation_methods_taxonomy.png", 1000, 600),
    ("s1_psf_reconstruction_residual.png", 1000, 350),
    ("separating_representation_and_interpolation_errors.png", 1000, 600),
    ("benchmark_ellipticity_breakdown.png", 1000, 600),
    ("benchmark_size_image_breakdown.png", 1000, 600),
    ("table_3.png", 800, 400),
    ("reconstruction_fidelity_g2.png", 1000, 350),
    ("systematic_biases_forest_plot.png", 1000, 600),
]


class TestFigureIntegrity(unittest.TestCase):
    """Validation tests for generated PNG figures and infographics."""

    def test_all_article_figures_exist_and_are_valid(self):
        """Verify each article image exists, has valid PNG magic bytes, and meets size criteria."""
        self.assertTrue(IMAGES_DIR.exists(), f"Images directory does not exist: {IMAGES_DIR}")

        for filename, min_w, min_h in CORE_IMAGES:
            img_path = IMAGES_DIR / filename
            self.assertTrue(img_path.exists(), f"Missing required figure: {filename}")

            # Verify file size > 15 KB
            file_size = img_path.stat().st_size
            self.assertGreater(file_size, 15000, f"File {filename} is suspiciously small ({file_size} bytes)")

            # Check PNG magic bytes
            with open(img_path, "rb") as f:
                header = f.read(8)
                self.assertEqual(header, b"\x89PNG\r\n\x1a\n", f"{filename} is not a valid PNG file.")

            # Validate dimensions with PIL
            with Image.open(img_path) as im:
                self.assertEqual(im.format, "PNG")
                w, h = im.size
                self.assertGreaterEqual(w, min_w, f"{filename} width {w}px < minimum {min_w}px")
                self.assertGreaterEqual(h, min_h, f"{filename} height {h}px < minimum {min_h}px")


if __name__ == "__main__":
    unittest.main()
