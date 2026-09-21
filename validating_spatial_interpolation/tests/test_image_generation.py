"""
Unit and integration tests for figure generation scripts and output image integrity:
- generate_validation_schemes_plot.py -> images/geneva_validation_schemes.png
- generate_spatial_gap_plot.py -> images/geneva_spatial_gap_comparison.png
- generate_sampling_strategies_plot.py -> images/geneva_sampling_strategies_comparison.png
- generate_benchmark_plots.py -> images/geneva_validation_benchmark_rmse.png
                                 images/geneva_error_vs_distance.png
"""

import os
import sys
import subprocess
import unittest
from PIL import Image

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CODE_DIR = os.path.join(BASE_DIR, 'code')
IMAGES_DIR = os.path.join(BASE_DIR, 'images')


class TestImageGeneration(unittest.TestCase):

    def _verify_png_image(self, rel_path, min_width=1000, min_height=400):
        img_path = os.path.join(IMAGES_DIR, rel_path)
        self.assertTrue(os.path.exists(img_path), f'Expected image does not exist: {img_path}')

        # Check non-trivial file size (> 15 KB)
        file_size = os.path.getsize(img_path)
        self.assertGreater(file_size, 15000, f'Image {rel_path} size is suspiciously small ({file_size} bytes).')

        # Check PNG magic bytes
        with open(img_path, 'rb') as f:
            header = f.read(8)
            self.assertEqual(header, b'\x89PNG\r\n\x1a\n', f'File {rel_path} is not a valid PNG.')

        # Check resolution with PIL
        with Image.open(img_path) as im:
            self.assertEqual(im.format, 'PNG')
            w, h = im.size
            self.assertGreaterEqual(w, min_width, f'Image width {w}px < {min_width}px for {rel_path}.')
            self.assertGreaterEqual(h, min_height, f'Image height {h}px < {min_height}px for {rel_path}.')

    def test_run_generate_validation_schemes_plot(self):
        script = os.path.join(CODE_DIR, 'generate_validation_schemes_plot.py')
        res = subprocess.run([sys.executable, script], cwd=CODE_DIR, capture_output=True, text=True, timeout=30)
        self.assertEqual(res.returncode, 0, f'Script failed with output:\n{res.stderr}\n{res.stdout}')
        self._verify_png_image('geneva_validation_schemes.png', min_width=1800, min_height=800)

    def test_run_generate_spatial_gap_plot(self):
        script = os.path.join(CODE_DIR, 'generate_spatial_gap_plot.py')
        res = subprocess.run([sys.executable, script], cwd=CODE_DIR, capture_output=True, text=True, timeout=30)
        self.assertEqual(res.returncode, 0, f'Script failed with output:\n{res.stderr}\n{res.stdout}')
        self._verify_png_image('geneva_spatial_gap_comparison.png', min_width=1800, min_height=800)

    def test_run_generate_sampling_strategies_plot(self):
        script = os.path.join(CODE_DIR, 'generate_sampling_strategies_plot.py')
        res = subprocess.run([sys.executable, script], cwd=CODE_DIR, capture_output=True, text=True, timeout=30)
        self.assertEqual(res.returncode, 0, f'Script failed with output:\n{res.stderr}\n{res.stdout}')
        self._verify_png_image('geneva_sampling_strategies_comparison.png', min_width=1800, min_height=600)

    def test_run_generate_benchmark_plots(self):
        script = os.path.join(CODE_DIR, 'generate_benchmark_plots.py')
        res = subprocess.run([sys.executable, script], cwd=CODE_DIR, capture_output=True, text=True, timeout=30)
        self.assertEqual(res.returncode, 0, f'Script failed with output:\n{res.stderr}\n{res.stdout}')
        self._verify_png_image('geneva_validation_benchmark_rmse.png', min_width=1600, min_height=600)
        self._verify_png_image('geneva_error_vs_distance.png', min_width=1600, min_height=600)


if __name__ == '__main__':
    unittest.main()
