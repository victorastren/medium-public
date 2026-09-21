#!/usr/bin/env python3
"""
Master runner script to generate all scientific figures and benchmark visualizations
for the Validating Spatial Interpolation article.

Can be run directly from any directory:
    python3 code/generate_all_figures.py
or from within the code directory:
    python3 generate_all_figures.py
"""

import os
import sys
import time
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
IMAGES_DIR = os.path.join(PROJECT_DIR, 'images')

SCRIPTS = [
    ('1. Validation Schemes (LOOCV vs. Holdout)', 'generate_validation_schemes_plot.py', 'geneva_validation_schemes.png'),
    ('2. Spatial Gap & Buffered Validation', 'generate_spatial_gap_plot.py', 'geneva_spatial_gap_comparison.png'),
    ('3. Four Sampling Strategies Comparison', 'generate_sampling_strategies_plot.py', 'geneva_sampling_strategies_comparison.png'),
    ('4. Benchmark RMSE & Error vs. Distance', 'generate_benchmark_plots.py', 'geneva_validation_benchmark_rmse.png'),
]


def run_all():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print('=' * 76)
    print(' Validating Spatial Interpolation - Figure Generation Pipeline')
    print(f' Output Directory: {IMAGES_DIR}')
    print('=' * 76)

    total_start = time.time()
    success_count = 0

    for idx, (title, script_name, expected_img) in enumerate(SCRIPTS, start=1):
        script_path = os.path.join(SCRIPT_DIR, script_name)
        print(f'\n[{idx}/{len(SCRIPTS)}] Generating: {title}...')
        t0 = time.time()
        res = subprocess.run([sys.executable, script_path], cwd=SCRIPT_DIR, capture_output=True, text=True)
        dt = time.time() - t0

        if res.returncode == 0:
            target_path = os.path.join(IMAGES_DIR, expected_img)
            size_kb = os.path.getsize(target_path) / 1024.0 if os.path.exists(target_path) else 0.0
            print(f'      ✓ Saved ({size_kb:.1f} KB in {dt:.2f}s)')
            success_count += 1
        else:
            print(f'      ✗ FAILED: {script_name}')
            print(res.stderr)

    total_time = time.time() - total_start
    print('\n' + '=' * 76)
    print(f' Pipeline Complete: {success_count}/{len(SCRIPTS)} scripts completed successfully in {total_time:.2f}s.')
    print('=' * 76)
    return success_count == len(SCRIPTS)


if __name__ == '__main__':
    success = run_all()
    sys.exit(0 if success else 1)
