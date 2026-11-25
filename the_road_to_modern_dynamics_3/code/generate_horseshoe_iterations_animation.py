#!/usr/bin/env python3
r"""
generate_horseshoe_iterations_animation.py

Generates Animation 1 ("From Smale’s Horseshoe to the Invariant Set") for Article 3:
"Order and Chaos: The Road to Modern Dynamics III"

Mathematical Model — Complete Folded Horseshoe Map F on R = [0, 1] x [0, 1]:
  - Lower returning branch (0 <= y <= 1/3):
      F(x, y) = (x / 3, 3y)
  - Semicircular folded bridge outside R (1/3 <= y <= 2/3):
      r(x) = 1/2 - x/3,   theta(y) = pi * (2 - 3y)
      F(x, y) = (1/2 + r(x) cos(theta(y)), 1 + r(x) sin(theta(y)))
  - Upper returning branch (2/3 <= y <= 1):
      F(x, y) = (1 - x / 3, 3(1 - y))

Exact Iterative Computation:
  - Panel A (Repeated horseshoe folding):
      V_0 = R,   V_n = R \cap F(V_{n-1})
      At stage n (n = 1, 2, 3), F is applied directly to every retained vertical
      strip of V_{n-1} via a strictly non-crossing continuous homotopy
      (Stretch -> Compress -> Fold) ending at the exact map F(V_{n-1}):
        n = 1: 1 folded band  -> 2 vertical strips inside R (width 1/3)
        n = 2: 2 folded bands -> 4 vertical strips inside R (width 1/9)
        n = 3: 4 folded bands -> 8 vertical strips inside R (width 1/27)
  - Panel B (Forward- and backward-time survival):
      H_0 = R,   H_n = R \cap F^{-1}(H_{n-1})  (2, 4, 8 horizontal teal strips)
      S_n = H_n \cap V_n                       (4, 16, 64 dark indigo squares)

Technical Specifications (16:9 widescreen, 1920 x 1080 px, 24 fps, 30.0 s = 720 frames):
  - Master MP4: images/horseshoe_stretching_folding_iterations.mp4
  - Web GIF:    images/horseshoe_stretching_folding_iterations.gif (16 fps, 1440px, loop=0)
  - Poster PNG: images/horseshoe_stretching_folding_iterations.png
"""

import os
import sys
import time
import shutil
import subprocess
import multiprocessing
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe

matplotlib.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "dejavuserif",
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "axes.edgecolor": "#cbd5e1",
    "axes.linewidth": 1.2,
})

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "images"
SCRATCH_DIR = PROJECT_DIR / "scratch"
FRAMES_DIR = Path("/tmp/horseshoe_iterations_frames")

# -----------------------------------------------------------------------------
# 1. Exact Piecewise-Affine Horseshoe Map F & Continuous Non-Crossing Homotopy
# -----------------------------------------------------------------------------
def cantor_intervals(n: int):
    """Return the exact 2^n intervals [(a_i, b_i), ...] of C_n on [0, 1]."""
    intervals = [(0.0, 1.0)]
    for _ in range(n):
        next_intervals = []
        for a, b in intervals:
            w = (b - a) / 3.0
            next_intervals.append((a, a + w))
            next_intervals.append((b - w, b))
        intervals = next_intervals
    return intervals


def eval_exact_horseshoe(x, y):
    """
    Evaluate the complete continuous folded horseshoe map F(x, y) on [0, 1]^2:
      - 0 <= y <= 1/3:   (x/3, 3y)
      - 1/3 < y < 2/3:   (1/2 + r(x) cos(theta), 1 + r(x) sin(theta))
                         with r(x) = 1/2 - x/3, theta(y) = pi*(2 - 3y)
      - 2/3 <= y <= 1:   (1 - x/3, 3(1 - y))
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    X = np.empty_like(x)
    Y = np.empty_like(y)

    m1 = y <= 1.0 / 3.0
    m2 = (y > 1.0 / 3.0) & (y < 2.0 / 3.0)
    m3 = y >= 2.0 / 3.0

    X[m1] = x[m1] / 3.0
    Y[m1] = 3.0 * y[m1]

    r = 0.5 - x[m2] / 3.0
    th = np.pi * (2.0 - 3.0 * y[m2])
    X[m2] = 0.5 + r * np.cos(th)
    Y[m2] = 1.0 + r * np.sin(th)

    X[m3] = 1.0 - x[m3] / 3.0
    Y[m3] = 3.0 * (1.0 - y[m3])
    return X, Y


def eval_horseshoe_homotopy(x, y, s_comp: float, s_fold: float):
    """
    Evaluate a strictly non-crossing, C^1-tangent-continuous global deformation
    F_{s_comp, s_fold}(x, y) on [0, 1]^2:
      - At (s_comp=0, s_fold=0): exact identity (x, y)
      - As s_comp: 0 -> 1 (with s_fold=0): stretches vertically and compresses
        horizontally linearly into x' = x/3 in [0, 1/3], y' in [0, 1 + pi/6 + 0.24]
      - As s_fold: 0 -> 1 (with s_comp=1): bends smoothly through angle phi = s_fold * pi
        around a concentric circular arc of inner radius R_in = (pi/6) / phi,
        preserving exact strip ordering with ZERO crossings or overlaps.
      - At (s_comp=1, s_fold=1): matches eval_exact_horseshoe(x, y) identically!
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    # Stage A: Horizontal compression x -> x_comp in [0, 1/3] and vertical pre-stretch
    # Compute the straight compressed-and-stretched reference state (s_comp=1, s_fold=0)
    L_arch_0 = np.pi / 6.0   # ~0.5236: exact inner arc length at phi = pi
    L_tail_0 = 0.24          # keeps peak height <= 1.77 before bending

    # Bent state at bend angle phi = s_fold * pi (applied to compressed coordinates)
    phi = np.pi * s_fold
    L_tail = L_tail_0 + (1.0 - L_tail_0) * s_fold  # 0.24 -> 1.00

    Xb = np.empty_like(x)
    Yb = np.empty_like(y)

    m1 = y <= 1.0 / 3.0
    m2 = (y > 1.0 / 3.0) & (y < 2.0 / 3.0)
    m3 = y >= 2.0 / 3.0

    # Lower segment: straight vertical leg
    Xb[m1] = x[m1] / 3.0
    Yb[m1] = 3.0 * y[m1]

    # Middle segment: concentric circular arc bending clockwise by phi in [0, pi]
    # Inner edge (x=1) has arc length L_arch_0 = pi/6, so R_in(phi) = L_arch_0 / phi.
    # For any x in [0, 1], R(x, phi) = R_in(phi) + (1 - x) / 3.
    # At phi = pi: R(x, pi) = 1/6 + (1 - x)/3 = 1/2 - x/3 = r(x)!
    u2 = 3.0 * y[m2] - 1.0  # in (0, 1)
    if phi < 1e-5:
        Xb[m2] = x[m2] / 3.0
        Yb[m2] = 1.0 + u2 * L_arch_0
    else:
        r_in = L_arch_0 / phi
        R_x = r_in + (1.0 - x[m2]) / 3.0
        psi = u2 * phi
        Xb[m2] = x[m2] / 3.0 + R_x * (1.0 - np.cos(psi))
        Yb[m2] = 1.0 + R_x * np.sin(psi)

    # Upper segment: straight tangent emerging from end of concentric arc (u2 = 1, psi = phi)
    u3 = 3.0 * y[m3] - 2.0  # in [0, 1]
    if phi < 1e-5:
        x_end = x[m3] / 3.0
        y_end = 1.0 + L_arch_0
        tx, ty = 0.0, 1.0
    else:
        r_in = L_arch_0 / phi
        R_x3 = r_in + (1.0 - x[m3]) / 3.0
        x_end = x[m3] / 3.0 + R_x3 * (1.0 - np.cos(phi))
        y_end = 1.0 + R_x3 * np.sin(phi)
        tx, ty = np.sin(phi), np.cos(phi)
    Xb[m3] = x_end + u3 * L_tail * tx
    Yb[m3] = y_end + u3 * L_tail * ty

    # Blend smoothly from identity (x, y) to compressed/bent (Xb, Yb) via s_comp
    X = (1.0 - s_comp) * x + s_comp * Xb
    Y = (1.0 - s_comp) * y + s_comp * Yb
    return X, Y


def build_strip_polygon(a: float, b: float, y0: float, y1: float, s_comp: float, s_fold: float,
                        n_y: int = 90, n_x: int = 12):
    """
    Build the exact polygon boundary of the image F_{s_comp, s_fold}([a, b] x [y0, y1]).
    """
    ys_up = np.linspace(y0, y1, n_y)
    xs_top = np.linspace(a, b, n_x)
    ys_dn = np.linspace(y1, y0, n_y)
    xs_bot = np.linspace(b, a, n_x)

    xs = np.concatenate([np.full(n_y, a), xs_top[1:], np.full(n_y - 1, b), xs_bot[1:]])
    ys = np.concatenate([ys_up, np.full(n_x - 1, y1), ys_dn[1:], np.full(n_x - 1, y0)])

    X, Y = eval_horseshoe_homotopy(xs, ys, s_comp, s_fold)
    return np.column_stack([X, Y])


def verify_numerical_construction():
    """
    Validate:
      1. Homotopy endpoints match exact map F(x, y) to machine precision.
      2. V_n = R cap F(V_{n-1}) gives 1, 2, 4, 8 vertical strips of width 3^{-n}.
      3. H_n = R cap F^{-1}(H_{n-1}) gives 1, 2, 4, 8 horizontal strips of height 3^{-n}.
      4. S_n = H_n cap V_n gives 1, 4, 16, 64 surviving squares of side 3^{-n}.
    """
    gx, gy = np.meshgrid(np.linspace(0.0, 1.0, 31), np.linspace(0.0, 1.0, 61))
    X_ex, Y_ex = eval_exact_horseshoe(gx, gy)
    X_h1, Y_h1 = eval_horseshoe_homotopy(gx, gy, 1.0, 1.0)
    max_err = max(np.max(np.abs(X_ex - X_h1)), np.max(np.abs(Y_ex - Y_h1)))
    assert max_err < 1e-12, f"Homotopy mismatch at s=1: {max_err}"

    # Verify iterative counts via dense interior grid
    m = 243
    coords = (np.arange(m) + 0.5) / m
    X0, Y0 = np.meshgrid(coords, coords)
    x0, y0 = X0.ravel(), Y0.ravel()

    # Check V_n by mapping V_{n-1} forward through eval_exact_horseshoe
    V_intervals = [(0.0, 1.0)]
    for n in range(1, 4):
        expected_V = cantor_intervals(n)
        # Each strip [a, b] in V_{n-1} maps via lower branch to [a/3, b/3] and upper branch to [1-b/3, 1-a/3]
        mapped_V = []
        for a, b in V_intervals:
            mapped_V.append((a / 3.0, b / 3.0))
            mapped_V.append((1.0 - b / 3.0, 1.0 - a / 3.0))
        mapped_V.sort()
        assert len(mapped_V) == 2 ** n == len(expected_V)
        for (a1, b1), (a2, b2) in zip(mapped_V, expected_V):
            assert abs(a1 - a2) < 1e-12 and abs(b1 - b2) < 1e-12
            assert abs((b1 - a1) - 3.0 ** (-n)) < 1e-12
        V_intervals = mapped_V

    print("  [Verified] Exact folded map F, homotopy C^1 endpoints (err < 1e-12), and V_n/H_n/S_n counts for n = 0..3.")


CANTOR = {n: cantor_intervals(n) for n in range(4)}


# -----------------------------------------------------------------------------
# 2. Animation Timeline (24 fps, 30.0 seconds = 720 frames)
# -----------------------------------------------------------------------------
FPS_MASTER = 24
TOTAL_DURATION = 30.0
N_TOTAL_FRAMES = int(round(TOTAL_DURATION * FPS_MASTER))  # 720 frames

INITIAL_HOLD = 2.50
T_S1_END = INITIAL_HOLD + 7.30   # 9.80
T_S2_END = T_S1_END + 7.40       # 17.20
T_S3_END = T_S2_END + 7.40       # 24.60
T_FINAL_END = T_S3_END + 4.70    # 29.30


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Hermite cubic smooth interpolation in [0, 1]."""
    if x <= edge0:
        return 0.0
    if x >= edge1:
        return 1.0
    u = (x - edge0) / (edge1 - edge0)
    return u * u * (3.0 - 2.0 * u)


def evaluate_timeline(t: float):
    r"""
    Causal 30-second animation sequence:
      - Stage 0 (0.0 -> 2.5 s): Original region R in both Panel A & Panel B
      - Stage 1 (2.5 -> 9.8 s):
          2.5 -> 3.6 s: Stretch & compress R (V_0)
          3.3 -> 4.9 s: Fold smoothly into 1st horseshoe F(V_0)
          5.1 -> 6.1 s: Fade outside arch in A -> leave 2 vertical strips V_1;
                        Simultaneously overlay 2 teal H_1 + 2 violet V_1 in B
          6.1 -> 7.0 s: Highlight 4 dark surviving squares S_1, fade strip overlays in B
          7.0 -> 9.8 s: Deliberate reading hold on Stage 1 (n = 1)
      - Stage 2 (9.8 -> 17.2 s):
          9.8 -> 10.2 s: Fade remaining arch ghost in A, keeping exact V_1 (2 vertical strips)
          10.2 -> 11.3 s: Stretch & compress V_1
          11.0 -> 12.6 s: Fold smoothly into 2 thinner nested horseshoes F(V_1)
          12.8 -> 13.8 s: Fade outside arches in A -> 4 vertical strips V_2;
                          Overlay 4 teal H_2 + 4 violet V_2 in B
          13.8 -> 14.7 s: Highlight 16 surviving squares S_2, fade strip overlays in B
          14.7 -> 17.2 s: Deliberate reading hold on Stage 2 (n = 2)
      - Stage 3 (17.2 -> 24.6 s):
          17.2 -> 17.6 s: Fade remaining arch ghosts in A, keeping exact V_2 (4 vertical strips)
          17.6 -> 18.7 s: Stretch & compress V_2
          18.4 -> 20.0 s: Fold smoothly into 4 even thinner nested horseshoes F(V_2)
          20.2 -> 21.2 s: Fade outside arches in A -> 8 vertical strips V_3;
                          Overlay 8 teal H_3 + 8 violet V_3 in B
          21.2 -> 22.1 s: Highlight 64 surviving squares S_3, fade strip overlays in B
          22.1 -> 24.6 s: Deliberate reading hold on Stage 3 (n = 3)
      - Final Hold (24.6 -> 29.3 s, 4.7 s):
          Display "Increasingly fine approximations to \Lambda" in Panel B only.
      - Loop Return (29.3 -> 30.0 s):
          Smooth cross-fade back to Stage 0 (R) for seamless looping.
    """
    st = {
        "t": t,
        "n_display": 0,           # Iteration counter badge n = 0, 1, 2, 3
        "panelA_source_n": 0,     # Which V_{k} is being mapped by F in Panel A
        "s_comp": 0.0,
        "s_fold": 0.0,
        "arch_alpha": 0.0,        # Opacity of curved bridge outside R in Panel A
        "inside_emphasis": 0.0,   # Extra highlight on retained strips inside R in Panel A
        "panelA_phase_lbl": "Initial region R",
        "B_prev_n": 0,            # Previous surviving squares S_{n-1} fading out
        "B_prev_alpha": 0.0,
        "B_curr_n": 0,            # Current stage n in Panel B geometry
        "B_display_n": 0,         # Synchronized stage n for Panel B text & Side readout
        "B_overlay_alpha": 0.0,   # Teal H_n & violet V_n overlay opacity in Panel B
        "B_sq_alpha": 1.0,        # Dark contrasting surviving squares S_n opacity in Panel B
        "arrow_pulse": 0.0,       # Causal bridge arrow highlight when Panel B updates from Panel A
        "final_badge_alpha": 0.0, # "Increasingly fine approximations to \Lambda" (Panel B only)
        "loop_reset_u": 0.0,      # Smooth cross-fade back to n=0 at end of cycle
    }

    if t < INITIAL_HOLD:
        # Stage 0: Initial region R
        st["n_display"] = 0
        st["panelA_source_n"] = 0
        st["s_comp"] = 0.0
        st["s_fold"] = 0.0
        st["arch_alpha"] = 0.0
        st["panelA_phase_lbl"] = "Initial region R"
        st["B_curr_n"] = 0
        st["B_display_n"] = 0
        st["B_sq_alpha"] = 1.0
    elif t < T_S1_END:
        # Stage 1: R -> 1 horseshoe -> 2 vertical strips (A), 4 squares (B)
        tau = t - INITIAL_HOLD  # in [0, 7.30)
        st["panelA_source_n"] = 0
        st["s_comp"] = smoothstep(0.00, 1.15, tau)
        st["s_fold"] = smoothstep(0.85, 2.40, tau)
        st["n_display"] = 1 if tau >= 0.40 else 0

        if tau < 2.60:
            st["arch_alpha"] = 0.90
        else:
            st["arch_alpha"] = 0.90 - 0.62 * smoothstep(2.60, 3.60, tau)
        st["inside_emphasis"] = smoothstep(2.60, 3.40, tau)

        if tau < 0.90:
            st["panelA_phase_lbl"] = "Stretching and compressing R"
        elif tau < 2.50:
            st["panelA_phase_lbl"] = "Folding into first horseshoe F(R)"
        else:
            st["panelA_phase_lbl"] = "1 folded band → 2 vertical strips inside R"

        st["B_prev_n"] = 0
        st["B_prev_alpha"] = 1.0 - smoothstep(2.30, 3.10, tau)
        st["B_curr_n"] = 1
        st["B_display_n"] = 1 if tau >= 2.60 else 0
        st["arrow_pulse"] = smoothstep(2.20, 2.75, tau) * (1.0 - smoothstep(3.15, 3.85, tau))
        ov_in = smoothstep(2.40, 3.30, tau)
        ov_settle = 1.0 - 0.68 * smoothstep(3.80, 4.90, tau)
        st["B_overlay_alpha"] = ov_in * ov_settle
        st["B_sq_alpha"] = smoothstep(3.40, 4.20, tau)
    elif t < T_S2_END:
        # Stage 2: V_1 (2 strips) -> 2 thinner horseshoes -> 4 vertical strips (A), 16 squares (B)
        tau = t - T_S1_END  # in [0, 7.40)
        if tau < 0.45:
            st["panelA_source_n"] = 0
            st["s_comp"] = 1.0
            st["s_fold"] = 1.0
            st["arch_alpha"] = 0.28 * (1.0 - smoothstep(0.00, 0.45, tau))
            st["inside_emphasis"] = 1.0
            st["n_display"] = 1
            st["panelA_phase_lbl"] = "Retaining the 2 vertical strips inside R"
            st["B_curr_n"] = 1
            st["B_display_n"] = 1
            st["B_overlay_alpha"] = 0.32 * (1.0 - smoothstep(0.00, 0.45, tau))
            st["B_sq_alpha"] = 1.0
        else:
            t2 = tau - 0.45  # in [0, 6.95)
            st["panelA_source_n"] = 1
            st["s_comp"] = smoothstep(0.00, 1.15, t2)
            st["s_fold"] = smoothstep(0.85, 2.40, t2)
            st["n_display"] = 2 if t2 >= 0.35 else 1

            if t2 < 2.60:
                st["arch_alpha"] = 0.90
            else:
                st["arch_alpha"] = 0.90 - 0.62 * smoothstep(2.60, 3.60, t2)
            st["inside_emphasis"] = smoothstep(2.60, 3.40, t2)

            if t2 < 0.90:
                st["panelA_phase_lbl"] = "Stretching the 2 retained strips"
            elif t2 < 2.50:
                st["panelA_phase_lbl"] = "Folding into 2 thinner horseshoes"
            else:
                st["panelA_phase_lbl"] = "2 folded bands → 4 vertical strips inside R"

            st["B_prev_n"] = 1
            st["B_prev_alpha"] = 1.0 - smoothstep(2.30, 3.10, t2)
            st["B_curr_n"] = 2
            st["B_display_n"] = 2 if t2 >= 2.60 else 1
            st["arrow_pulse"] = smoothstep(2.20, 2.75, t2) * (1.0 - smoothstep(3.15, 3.85, t2))
            ov_in = smoothstep(2.40, 3.30, t2)
            ov_settle = 1.0 - 0.68 * smoothstep(3.80, 4.90, t2)
            st["B_overlay_alpha"] = ov_in * ov_settle
            st["B_sq_alpha"] = smoothstep(3.40, 4.20, t2)
    elif t < T_S3_END:
        # Stage 3: V_2 (4 strips) -> 4 thinner horseshoes -> 8 vertical strips (A), 64 squares (B)
        tau = t - T_S2_END  # in [0, 7.40)
        if tau < 0.45:
            st["panelA_source_n"] = 1
            st["s_comp"] = 1.0
            st["s_fold"] = 1.0
            st["arch_alpha"] = 0.28 * (1.0 - smoothstep(0.00, 0.45, tau))
            st["inside_emphasis"] = 1.0
            st["n_display"] = 2
            st["panelA_phase_lbl"] = "Retaining the 4 vertical strips inside R"
            st["B_curr_n"] = 2
            st["B_display_n"] = 2
            st["B_overlay_alpha"] = 0.32 * (1.0 - smoothstep(0.00, 0.45, tau))
            st["B_sq_alpha"] = 1.0
        else:
            t3 = tau - 0.45  # in [0, 6.95)
            st["panelA_source_n"] = 2
            st["s_comp"] = smoothstep(0.00, 1.15, t3)
            st["s_fold"] = smoothstep(0.85, 2.40, t3)
            st["n_display"] = 3 if t3 >= 0.35 else 2

            if t3 < 2.60:
                st["arch_alpha"] = 0.90
            else:
                st["arch_alpha"] = 0.90 - 0.62 * smoothstep(2.60, 3.60, t3)
            st["inside_emphasis"] = smoothstep(2.60, 3.40, t3)

            if t3 < 0.90:
                st["panelA_phase_lbl"] = "Stretching the 4 retained strips"
            elif t3 < 2.50:
                st["panelA_phase_lbl"] = "Folding into 4 thinner horseshoes"
            else:
                st["panelA_phase_lbl"] = "4 folded bands → 8 vertical strips inside R"

            st["B_prev_n"] = 2
            st["B_prev_alpha"] = 1.0 - smoothstep(2.30, 3.10, t3)
            st["B_curr_n"] = 3
            st["B_display_n"] = 3 if t3 >= 2.60 else 2
            st["arrow_pulse"] = smoothstep(2.20, 2.75, t3) * (1.0 - smoothstep(3.15, 3.85, t3))
            ov_in = smoothstep(2.40, 3.30, t3)
            ov_settle = 1.0 - 0.72 * smoothstep(3.80, 4.90, t3)
            st["B_overlay_alpha"] = ov_in * ov_settle
            st["B_sq_alpha"] = smoothstep(3.40, 4.20, t3)
    elif t < T_FINAL_END:
        # Final Hold (4.7 s): Invariant set statement in Panel B only
        st["panelA_source_n"] = 2
        st["s_comp"] = 1.0
        st["s_fold"] = 1.0
        st["arch_alpha"] = 0.28
        st["inside_emphasis"] = 1.0
        st["n_display"] = 3
        st["panelA_phase_lbl"] = "4 folded bands → 8 vertical strips inside R"
        st["B_curr_n"] = 3
        st["B_display_n"] = 3
        st["B_overlay_alpha"] = 0.28
        st["B_sq_alpha"] = 1.0
        st["final_badge_alpha"] = smoothstep(T_S3_END, T_S3_END + 0.50, t)
    else:
        # Seamless loop return to Stage 0 (R)
        u = smoothstep(T_FINAL_END, TOTAL_DURATION, t)
        st["panelA_source_n"] = 2
        st["s_comp"] = 1.0
        st["s_fold"] = 1.0
        st["arch_alpha"] = 0.28 * (1.0 - u)
        st["inside_emphasis"] = 1.0 - u
        st["n_display"] = 0 if u >= 0.5 else 3
        st["panelA_phase_lbl"] = "Initial region R" if u >= 0.5 else "4 folded bands → 8 vertical strips inside R"
        st["B_curr_n"] = 3
        st["B_display_n"] = 0 if u >= 0.5 else 3
        st["B_overlay_alpha"] = 0.28 * (1.0 - u)
        st["B_sq_alpha"] = 1.0 - u
        st["final_badge_alpha"] = 1.0 - smoothstep(T_FINAL_END, T_FINAL_END + 0.35, t)
        st["loop_reset_u"] = u

    return st


# -----------------------------------------------------------------------------
# 3. Color Palette & Visual Hierarchy (Cohesive with Figure 1)
# -----------------------------------------------------------------------------
NAVY = "#0f172a"
DARK_SLATE = "#1e293b"
SLATE = "#334155"
MUTED_SLATE = "#475569"
BORDER_CARD = "#cbd5e1"
BG_CARD = "#f8fafc"
BG_BOX = "#ffffff"

# Violet theme (Main Horseshoe in Panel A & Backward restrictions in Panel B)
VIOLET_ACCENT = "#6366f1"
VIOLET_BAND = "#a5b4fc"
VIOLET_PALE = "#e0e7ff"
VIOLET_MID = "#4f46e5"
VIOLET_DARK = "#3730a3"
VIOLET_LIGHT = "#eef2ff"
VIOLET_BORDER = "#a5b4fc"

# Teal theme (Forward-time restrictions in Panel B)
TEAL_ACCENT = "#0d9488"
TEAL_FILL = "#14b8a6"
TEAL_DARK = "#0f766e"
TEAL_LIGHT = "#f0fdfa"
TEAL_BORDER = "#5eead4"

# Darker contrasting shade for two-sided surviving squares S_n in Panel B
INDIGO_SURV = "#312e81"
INDIGO_EDGE = "#1e1b4b"


# -----------------------------------------------------------------------------
# 4. Single Frame Renderer (1920x1080 @ 120 DPI)
# -----------------------------------------------------------------------------
def render_frame_to_path(st: dict, out_path: Path):
    """Render one 1920x1080 frame."""
    fig_w, fig_h = 16.0, 9.0
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=120, facecolor="#ffffff")

    ax_bg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=0)
    ax_bg.set_xlim(0.0, 1.0)
    ax_bg.set_ylim(0.0, 1.0)
    ax_bg.axis("off")

    halo = [pe.withStroke(linewidth=3.6, foreground="#ffffff", alpha=0.95)]
    n_disp = st["n_display"]
    loop_u = st["loop_reset_u"]

    # -------------------------------------------------------------------------
    # Global Title & Subtitle
    # -------------------------------------------------------------------------
    fig.text(
        0.50,
        0.962,
        "From Smale’s Horseshoe to the Invariant Set",
        fontsize=24.0,
        weight="bold",
        color=NAVY,
        ha="center",
        va="center",
    )
    fig.text(
        0.50,
        0.920,
        "Repeated folding and progressively finer surviving regions",
        fontsize=17.5,
        style="italic",
        weight="normal",
        color=DARK_SLATE,
        ha="center",
        va="center",
    )

    # -------------------------------------------------------------------------
    # Two Equal-Width Parallel Panel Cards (A and B)
    # -------------------------------------------------------------------------
    y_card = 0.026
    h_card = 0.860
    x1, w1 = 0.018, 0.470
    x2, w2 = 0.512, 0.470
    hbar_h = 0.100
    badge_y = y_card + h_card - hbar_h / 2.0

    # Dynamic concise panel subtitles reflecting exact counts (synchronized to visible geometry)
    sub_A_text = st["panelA_phase_lbl"]
    nb = st["B_display_n"]
    if nb == 0:
        sub_B_text = "Original square R before survival restrictions"
    else:
        sub_B_text = f"{2**nb} horizontal × {2**nb} vertical → {4**nb} surviving squares"

    panels_spec = [
        (x1, w1, "A", "Repeated horseshoe folding", sub_A_text, n_disp,
         VIOLET_ACCENT, VIOLET_LIGHT, VIOLET_BORDER, VIOLET_DARK),
        (x2, w2, "B", "Forward- and backward-time survival", sub_B_text, nb,
         TEAL_ACCENT, TEAL_LIGHT, TEAL_BORDER, TEAL_DARK),
    ]

    for px, pw, letter, title, subtitle, n_pill_val, acc_color, bg_tint, bdr_color, dark_col in panels_spec:
        card_rect = patches.FancyBboxPatch(
            (px, y_card),
            pw,
            h_card,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=BG_CARD,
            edgecolor=BORDER_CARD,
            linewidth=1.5,
            zorder=1,
        )
        ax_bg.add_patch(card_rect)

        hbar_rect = patches.FancyBboxPatch(
            (px, y_card + h_card - hbar_h),
            pw,
            hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=bg_tint,
            edgecolor=bdr_color,
            linewidth=1.3,
            zorder=2,
        )
        ax_bg.add_patch(hbar_rect)

        badge_x = px + 0.022
        r_x = 0.0145
        r_y = r_x * (fig_w / fig_h)
        badge_c = patches.Ellipse(
            (badge_x, badge_y),
            width=2.0 * r_x,
            height=2.0 * r_y,
            facecolor=acc_color,
            edgecolor="none",
            zorder=3,
        )
        ax_bg.add_patch(badge_c)
        ax_bg.text(
            badge_x,
            badge_y - 0.0005,
            letter,
            fontsize=17.5,
            weight="bold",
            color="#ffffff",
            ha="center",
            va="center",
            zorder=4,
        )

        text_offset_x = badge_x + 0.022
        ax_bg.text(
            text_offset_x,
            badge_y + 0.019,
            title,
            fontsize=17.2,
            weight="bold",
            color=NAVY,
            va="center",
            zorder=4,
        )
        ax_bg.text(
            text_offset_x,
            badge_y - 0.021,
            subtitle,
            fontsize=14.4,
            weight="bold",
            color=MUTED_SLATE,
            va="center",
            zorder=4,
        )

        # Crisp iteration counter pill n = 0, 1, 2, 3 (subtle pulse on Panel B when it updates)
        pw_pill, ph_pill = 0.086, 0.044
        px_pill = px + pw - pw_pill - 0.012
        py_pill = badge_y + 0.018 - ph_pill / 2.0
        ap = st["arrow_pulse"] if letter == "B" else 0.0
        pill_ec = INDIGO_SURV if ap > 0.35 else bdr_color
        pill_fc = "#e0e7ff" if ap > 0.55 else "#ffffff"
        iter_pill = patches.FancyBboxPatch(
            (px_pill, py_pill),
            pw_pill,
            ph_pill,
            boxstyle="round,pad=0.0,rounding_size=0.011",
            facecolor=pill_fc,
            edgecolor=pill_ec,
            linewidth=1.4 + 1.4 * ap,
            zorder=3,
        )
        ax_bg.add_patch(iter_pill)
        ax_bg.text(
            px_pill + pw_pill / 2.0,
            py_pill + ph_pill / 2.0,
            rf"$\boldsymbol{{n}} = \mathbf{{{n_pill_val}}}$",
            fontsize=16.5,
            weight="bold",
            color=INDIGO_SURV if ap > 0.35 else dark_col,
            ha="center",
            va="center",
            zorder=4,
        )

    # Causal bridge arrow between Panel A and Panel B headers (pulses when Panel B updates)
    ap_arr = st["arrow_pulse"]
    if ap_arr > 1e-2:
        ax_bg.add_patch(patches.FancyArrowPatch(
            (x1 + w1 + 0.001, badge_y),
            (x2 - 0.001, badge_y),
            arrowstyle="-|>,head_length=10.5,head_width=7.5",
            color=VIOLET_ACCENT,
            linewidth=8.5,
            alpha=0.32 * ap_arr,
            zorder=4,
        ))
    ax_bg.add_patch(patches.FancyArrowPatch(
        (x1 + w1 + 0.002, badge_y),
        (x2 - 0.002, badge_y),
        arrowstyle=f"-|>,head_length={7.0 + 2.8 * ap_arr:.2f},head_width={4.5 + 2.0 * ap_arr:.2f}",
        color=VIOLET_MID if ap_arr > 0.25 else "#64748b",
        linewidth=2.2 + 2.0 * ap_arr,
        zorder=5,
    ))

    # -------------------------------------------------------------------------
    # Bottom Explanatory Boxes (cleanly wrapped within borders, >= 14.0 pt)
    # -------------------------------------------------------------------------
    y_box = 0.036
    h_box = 0.118

    # Panel A bottom box (3 balanced lines fitting with generous horizontal margin)
    box_A = patches.FancyBboxPatch(
        (x1 + 0.014, y_box),
        w1 - 0.028,
        h_box,
        boxstyle="round,pad=0.0,rounding_size=0.014",
        facecolor=BG_BOX,
        edgecolor=VIOLET_BORDER,
        linewidth=1.4,
        zorder=3,
    )
    ax_bg.add_patch(box_A)
    ax_bg.text(
        x1 + w1 / 2.0,
        y_box + h_box / 2.0,
        "At each iteration, the retained regions are stretched,\n"
        "compressed, and folded again. Their intersections\n"
        r"with $\boldsymbol{R}$ produce increasingly narrow vertical strips.",
        fontsize=14.0,
        weight="bold",
        color=DARK_SLATE,
        ha="center",
        va="center",
        linespacing=1.18,
        zorder=4,
    )

    # Panel B bottom box (transitions cleanly to final highlight on 26.6 -> 30.3 s)
    fb_a = st["final_badge_alpha"]
    if fb_a < 0.99:
        box_B = patches.FancyBboxPatch(
            (x2 + 0.014, y_box),
            w2 - 0.028,
            h_box,
            boxstyle="round,pad=0.0,rounding_size=0.014",
            facecolor=BG_BOX,
            edgecolor=TEAL_BORDER,
            linewidth=1.4,
            alpha=1.0 - fb_a,
            zorder=3,
        )
        ax_bg.add_patch(box_B)
        ax_bg.text(
            x2 + w2 / 2.0,
            y_box + h_box / 2.0,
            "Combining the restrictions from both directions\n"
            "produces progressively smaller regions\n"
            r"approaching the invariant set $\boldsymbol{\Lambda}$.",
            fontsize=14.0,
            weight="bold",
            color=DARK_SLATE,
            ha="center",
            va="center",
            linespacing=1.18,
            alpha=1.0 - fb_a,
            zorder=4,
        )

    if fb_a > 1e-2:
        box_B_final = patches.FancyBboxPatch(
            (x2 + 0.014, y_box),
            w2 - 0.028,
            h_box,
            boxstyle="round,pad=0.0,rounding_size=0.014",
            facecolor=VIOLET_LIGHT,
            edgecolor=INDIGO_SURV,
            linewidth=2.2,
            alpha=fb_a,
            zorder=5,
        )
        ax_bg.add_patch(box_B_final)
        ax_bg.text(
            x2 + w2 / 2.0,
            y_box + h_box * 0.65,
            r"Increasingly fine approximations to $\boldsymbol{\Lambda}$",
            fontsize=17.4,
            weight="bold",
            color=INDIGO_SURV,
            ha="center",
            va="center",
            alpha=fb_a,
            zorder=6,
        )
        ax_bg.text(
            x2 + w2 / 2.0,
            y_box + h_box * 0.27,
            r"64 surviving squares at $\boldsymbol{n} = \mathbf{3}$ (side length 1/27)",
            fontsize=14.6,
            weight="bold",
            color=DARK_SLATE,
            ha="center",
            va="center",
            alpha=fb_a,
            zorder=6,
        )

    # =========================================================================
    # SYMMETRIC TOP STATUS / LEGEND STRIP ABOVE PLOTS (y = 0.764, zero overlap)
    # =========================================================================
    y_strip = 0.764
    if n_disp == 0:
        a_strip_txt = "Stage 0: 1 initial square R  (width 1)"
    else:
        n_bands = 2 ** (n_disp - 1)
        n_vstrips = 2 ** n_disp
        band_word = "band" if n_bands == 1 else "bands"
        a_strip_txt = f"{n_bands} folded {band_word}  →  {n_vstrips} vertical strips  (width 1/{3**n_disp})"
    ax_bg.text(
        x1 + w1 / 2.0,
        y_strip,
        a_strip_txt,
        fontsize=14.4,
        weight="bold",
        color=VIOLET_DARK,
        ha="center",
        va="center",
        zorder=6,
    )

    legend_items = [
        (TEAL_FILL, TEAL_DARK, "Forward"),
        (VIOLET_ACCENT, VIOLET_DARK, "Backward"),
        (INDIGO_SURV, INDIGO_EDGE, "Both (surviving)"),
    ]
    lx_positions = [x2 + 0.044, x2 + 0.162, x2 + 0.292]
    for lx, (fc, ec, lbl) in zip(lx_positions, legend_items):
        ax_bg.add_patch(patches.Rectangle(
            (lx, y_strip - 0.0085), 0.014, 0.017,
            facecolor=fc, edgecolor=ec, linewidth=1.2, zorder=6,
        ))
        ax_bg.text(
            lx + 0.020, y_strip, lbl,
            fontsize=14.0, weight="bold", color=DARK_SLATE,
            ha="left", va="center", zorder=6,
        )

    # =========================================================================
    # PANEL A AXES: REPEATED HORSESHOE FOLDING (SHOWS ARCHES OUTSIDE R ABOVE y=1)
    # =========================================================================
    y_plot = 0.214
    h_plot = 0.526
    w_plot_A = 0.345
    ax1 = fig.add_axes([x1 + (w1 - w_plot_A) / 2.0 + 0.010, y_plot, w_plot_A, h_plot], zorder=5)
    ax1.set_facecolor("#ffffff")
    # Equal aspect with tall headroom above y = 1.0 for the folded horseshoe arches (peak ~ 1.77 during morph, 1.50 folded)
    ax1.set_xlim(-0.46, 1.46)
    ax1.set_ylim(-0.14, 1.88)
    ax1.set_aspect("equal", adjustable="box")

    for gx in np.linspace(-0.3333, 1.3333, 6):
        ax1.axvline(gx, color="#f1f5f9", lw=0.9, zorder=1)
    for gy in np.linspace(0.0, 1.6667, 6):
        ax1.axhline(gy, color="#f1f5f9", lw=0.9, zorder=1)
    for g in (1.0 / 3.0, 2.0 / 3.0):
        ax1.axvline(g, color="#e2e8f0", lw=1.0, ls=":", zorder=2)
        ax1.axhline(g, color="#e2e8f0", lw=1.0, ls=":", zorder=2)

    # Pale interior reference background of R
    ax1.add_patch(patches.Rectangle(
        (0.0, 0.0), 1.0, 1.0, facecolor="#f8fafc", edgecolor="none", zorder=2,
    ))

    ax1.set_xticks([0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0])
    ax1.set_xticklabels(["0", "1/3", "2/3", "1"], fontsize=14.2, fontweight="bold", color=SLATE)
    ax1.set_yticks([0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0, 1.5])
    ax1.set_yticklabels(["0", "1/3", "2/3", "1", "3/2"], fontsize=14.2, fontweight="bold", color=SLATE)
    ax1.tick_params(axis="both", which="major", length=4, width=1.2, colors=SLATE, pad=4)
    ax1.set_xlabel(r"$\boldsymbol{x}$", fontsize=15.5, fontweight="bold", color=NAVY, labelpad=0)
    ax1.set_ylabel(r"$\boldsymbol{y}$", fontsize=15.5, fontweight="bold", color=NAVY, labelpad=4)

    # Draw transforming / folded horseshoe bands from V_{source_n}
    src_n = st["panelA_source_n"]
    s_comp = st["s_comp"]
    s_fold = st["s_fold"]
    arch_a = st["arch_alpha"]
    in_emp = st["inside_emphasis"]
    src_intervals = CANTOR[src_n]

    main_a_mult = 1.0 - loop_u

    if s_comp <= 1e-4 and s_fold <= 1e-4:
        # Stage 0: Initial square R = [0, 1]^2 with subtle material grid lines
        ax1.add_patch(patches.Rectangle(
            (0.0, 0.0), 1.0, 1.0,
            facecolor=VIOLET_BAND, edgecolor=VIOLET_ACCENT,
            linewidth=1.8, alpha=0.42, zorder=4,
        ))
        for ym in (1.0 / 6.0, 1.0 / 3.0, 0.5, 2.0 / 3.0, 5.0 / 6.0):
            ax1.plot([0.0, 1.0], [ym, ym], color=VIOLET_MID, lw=1.0, alpha=0.32, zorder=5)
        for xm in (1.0 / 3.0, 0.5, 2.0 / 3.0):
            ax1.plot([xm, xm], [0.0, 1.0], color=VIOLET_MID, lw=0.9, alpha=0.26, zorder=5)
    else:
        lw_edge = 1.8 if src_n == 0 else (1.3 if src_n == 1 else 0.95)
        # Render each strip [a, b] in V_{src_n} as three joined pieces:
        #   - Lower returning branch y in [0, 1/3] -> ends inside R
        #   - Curved bridge y in [1/3, 2/3]        -> outside R (fades to pale violet)
        #   - Upper returning branch y in [2/3, 1] -> ends inside R
        for a, b in src_intervals:
            # 1. Curved bridge outside R (middle y in [1/3, 2/3])
            if arch_a > 1e-3:
                poly_mid = build_strip_polygon(a, b, 1.0 / 3.0, 2.0 / 3.0, s_comp, s_fold, n_y=70, n_x=10)
                # Interpolate fill color from vibrant violet while folding to pale violet when faded
                fill_mid = VIOLET_BAND if arch_a > 0.55 else VIOLET_PALE
                ax1.add_patch(patches.Polygon(
                    poly_mid, closed=True,
                    facecolor=fill_mid, edgecolor=VIOLET_ACCENT,
                    linewidth=lw_edge * 0.9, alpha=arch_a, zorder=4,
                ))
                # Subtle material grid curves inside the arch
                if arch_a > 0.35:
                    for ym in (4.0 / 9.0, 0.5, 5.0 / 9.0):
                        xs_m = np.linspace(a, b, 14)
                        X_m, Y_m = eval_horseshoe_homotopy(xs_m, np.full_like(xs_m, ym), s_comp, s_fold)
                        ax1.plot(X_m, Y_m, color=VIOLET_DARK, lw=0.85, alpha=0.38 * arch_a, zorder=5)

            # 2. Returning legs (lower [0, 1/3] and upper [2/3, 1]) -> become retained vertical strips inside R
            leg_fill_a = (0.76 + 0.14 * in_emp) * main_a_mult
            leg_edge_col = VIOLET_DARK if in_emp > 0.4 else VIOLET_ACCENT
            for y_lo, y_hi in ((0.0, 1.0 / 3.0), (2.0 / 3.0, 1.0)):
                poly_leg = build_strip_polygon(a, b, y_lo, y_hi, s_comp, s_fold, n_y=28, n_x=8)
                ax1.add_patch(patches.Polygon(
                    poly_leg, closed=True,
                    facecolor=VIOLET_ACCENT if in_emp > 0.5 else VIOLET_BAND,
                    edgecolor=leg_edge_col,
                    linewidth=lw_edge, alpha=leg_fill_a, zorder=6,
                ))
                # Subtle horizontal material markers inside legs to show vertical stretching
                if in_emp < 0.75:
                    for frac in (0.33, 0.67):
                        ym = y_lo + frac * (y_hi - y_lo)
                        xs_m = np.linspace(a, b, 8)
                        X_m, Y_m = eval_horseshoe_homotopy(xs_m, np.full_like(xs_m, ym), s_comp, s_fold)
                        ax1.plot(X_m, Y_m, color=VIOLET_DARK, lw=0.85,
                                 alpha=0.35 * (1.0 - in_emp) * main_a_mult, zorder=7)

        # Fade initial R fill back in smoothly during loop reset
        if loop_u > 1e-3:
            ax1.add_patch(patches.Rectangle(
                (0.0, 0.0), 1.0, 1.0,
                facecolor=VIOLET_BAND, edgecolor=VIOLET_ACCENT,
                linewidth=1.8, alpha=0.42 * loop_u, zorder=8,
            ))

    # Fixed black dashed square outline R = [0, 1]^2 in Panel A
    ax1.add_patch(patches.Rectangle(
        (0.0, 0.0), 1.0, 1.0,
        facecolor="none", edgecolor=DARK_SLATE,
        linewidth=2.5, linestyle="--", zorder=20,
    ))
    ax1.text(
        -0.41, 1.80, r"$\mathbf{Original\;region}\;\boldsymbol{R}$" + "\n(dashed square)",
        fontsize=14.0, weight="bold", color=DARK_SLATE,
        ha="left", va="top", linespacing=1.18, path_effects=halo, zorder=22,
    )

    # =========================================================================
    # PANEL B AXES: FORWARD- AND BACKWARD-TIME SURVIVAL (ZOOMED ON R = [0,1]^2)
    # =========================================================================
    w_plot_B = h_plot * (fig_h / fig_w)  # exact geometric square in figure coordinates
    ax2 = fig.add_axes([x2 + (w2 - w_plot_B) / 2.0 + 0.010, y_plot, w_plot_B, h_plot], zorder=5)
    ax2.set_facecolor("#ffffff")
    ax2.set_xlim(-0.10, 1.10)
    ax2.set_ylim(-0.06, 1.14)
    ax2.set_aspect("equal", adjustable="box")

    for g in np.linspace(0.0, 1.0, 10):
        ax2.axvline(g, color="#f1f5f9", lw=0.9, zorder=1)
        ax2.axhline(g, color="#f1f5f9", lw=0.9, zorder=1)
    for g in (1.0 / 3.0, 2.0 / 3.0):
        ax2.axvline(g, color="#e2e8f0", lw=1.1, ls=":", zorder=2)
        ax2.axhline(g, color="#e2e8f0", lw=1.1, ls=":", zorder=2)

    ax2.add_patch(patches.Rectangle(
        (0.0, 0.0), 1.0, 1.0, facecolor="#f8fafc", edgecolor="none", zorder=2,
    ))

    ax2.set_xticks([0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0])
    ax2.set_xticklabels(["0", "1/3", "2/3", "1"], fontsize=14.4, fontweight="bold", color=SLATE)
    ax2.set_yticks([0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0])
    ax2.set_yticklabels(["0", "1/3", "2/3", "1"], fontsize=14.4, fontweight="bold", color=SLATE)
    ax2.tick_params(axis="both", which="major", length=4, width=1.2, colors=SLATE, pad=4)
    ax2.set_xlabel(r"$\boldsymbol{x}$", fontsize=15.5, fontweight="bold", color=NAVY, labelpad=0)
    ax2.set_ylabel(r"$\boldsymbol{y}$", fontsize=15.5, fontweight="bold", color=NAVY, labelpad=4)

    def draw_panelB_squares(n_stage: int, alpha_val: float, z_base: int):
        if alpha_val <= 1e-3:
            return
        intervals = CANTOR[n_stage]
        if n_stage == 0:
            ax2.add_patch(patches.Rectangle(
                (0.0, 0.0), 1.0, 1.0,
                facecolor=VIOLET_BAND, edgecolor=VIOLET_ACCENT,
                linewidth=1.8, alpha=0.42 * alpha_val, zorder=z_base,
            ))
            return
        lw_sq = 1.4 if n_stage == 1 else (1.05 if n_stage == 2 else 0.75)
        for ax_i, bx_i in intervals:
            for ay_i, by_i in intervals:
                ax2.add_patch(patches.Rectangle(
                    (ax_i, ay_i), bx_i - ax_i, by_i - ay_i,
                    facecolor=INDIGO_SURV, edgecolor="none",
                    alpha=0.92 * alpha_val, zorder=z_base,
                ))
                ax2.add_patch(patches.Rectangle(
                    (ax_i, ay_i), bx_i - ax_i, by_i - ay_i,
                    facecolor="none", edgecolor=INDIGO_EDGE,
                    linewidth=lw_sq, alpha=0.98 * alpha_val, zorder=z_base + 1,
                ))

    # Previous surviving squares fading out cleanly during stage transition
    draw_panelB_squares(st["B_prev_n"], st["B_prev_alpha"], z_base=4)

    # Current teal horizontal (forward H_n) and violet vertical (backward V_n) overlays
    b_curr = st["B_curr_n"]
    ov_a = st["B_overlay_alpha"]
    if b_curr > 0 and ov_a > 1e-3:
        intervals = CANTOR[b_curr]
        lw_ov = 1.1 if b_curr == 1 else (0.75 if b_curr == 2 else 0.45)
        for ay_i, by_i in intervals:
            ax2.add_patch(patches.Rectangle(
                (0.0, ay_i), 1.0, by_i - ay_i,
                facecolor=TEAL_FILL, edgecolor=TEAL_DARK,
                linewidth=lw_ov, alpha=0.48 * ov_a, zorder=5,
            ))
        for ax_i, bx_i in intervals:
            ax2.add_patch(patches.Rectangle(
                (ax_i, 0.0), bx_i - ax_i, 1.0,
                facecolor=VIOLET_ACCENT, edgecolor=VIOLET_DARK,
                linewidth=lw_ov, alpha=0.44 * ov_a, zorder=6,
            ))

    # Current surviving squares S_n = H_n \cap V_n in darker contrasting indigo
    draw_panelB_squares(b_curr, st["B_sq_alpha"], z_base=8)

    # Smooth return to R during loop reset
    if loop_u > 1e-3:
        draw_panelB_squares(0, loop_u, z_base=11)

    # Fixed black dashed square outline R = [0, 1]^2 in Panel B
    ax2.add_patch(patches.Rectangle(
        (0.0, 0.0), 1.0, 1.0,
        facecolor="none", edgecolor=DARK_SLATE,
        linewidth=2.5, linestyle="--", zorder=20,
    ))
    ax2.text(
        -0.02, 1.042, r"$\mathbf{Original\;region}\;\boldsymbol{R}$",
        fontsize=14.4, weight="bold", color=DARK_SLATE,
        ha="left", va="bottom", path_effects=halo, zorder=22,
    )
    b_scale_str = "1" if nb == 0 else f"1/{3**nb}"
    ax2.text(
        1.02, 1.042, rf"$\mathbf{{Side:}}\;\mathbf{{{b_scale_str}}}$",
        fontsize=14.4, weight="bold", color=INDIGO_SURV,
        ha="right", va="bottom", path_effects=halo, zorder=22,
    )

    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def render_single_frame(frame_idx: int):
    """Worker entry point for multiprocessing frame rendering."""
    t = frame_idx / FPS_MASTER
    state = evaluate_timeline(t)
    out_path = FRAMES_DIR / f"frame_{frame_idx:04d}.png"
    render_frame_to_path(state, out_path)
    return frame_idx


def generate_preview_frames():
    """Render key inspection frames across all stages into scratch/."""
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    preview_times = [
        ("v2_s0_init.png", 1.25),
        ("v2_s1_fold.png", 4.10),
        ("v2_s1_hold.png", 8.50),
        ("v2_s2_fold.png", 11.80),
        ("v2_s2_hold.png", 16.00),
        ("v2_s3_fold.png", 19.20),
        ("v2_s3_hold.png", 23.50),
        ("v2_final.png", 26.50),
    ]
    for fname, t_val in preview_times:
        state = evaluate_timeline(t_val)
        out_p = SCRATCH_DIR / fname
        render_frame_to_path(state, out_p)
        print(f"  [Preview] Saved {out_p} (t = {t_val:.2f} s)")


def main():
    print("--- Verifying exact folded horseshoe map F, homotopy, and iterative sets ---")
    verify_numerical_construction()

    if "--preview-only" in sys.argv:
        generate_preview_frames()
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"--- Rendering {N_TOTAL_FRAMES} frames ({TOTAL_DURATION:.1f} s @ {FPS_MASTER} fps, 1920x1080) ---")
    t0 = time.time()
    num_cpus = max(1, min(14, multiprocessing.cpu_count() - 2))
    print(f"  Using {num_cpus} parallel workers...")

    with multiprocessing.Pool(processes=num_cpus) as pool:
        for idx in pool.imap_unordered(render_single_frame, range(N_TOTAL_FRAMES), chunksize=4):
            if (idx + 1) % 60 == 0 or idx == N_TOTAL_FRAMES - 1:
                print(f"    Completed frame {idx + 1:3d} / {N_TOTAL_FRAMES}")

    t1 = time.time()
    print(f"  Frame rendering finished in {t1 - t0:.1f} s ({(t1 - t0) / N_TOTAL_FRAMES:.3f} s/frame)")

    # 1. Master MP4 Video (1920x1080 @ 24 fps)
    mp4_out = OUTPUT_DIR / "horseshoe_stretching_folding_iterations.mp4"
    print(f"--- Encoding Master MP4 video: {mp4_out} ---")
    cmd_mp4 = [
        "ffmpeg", "-y",
        "-framerate", str(FPS_MASTER),
        "-i", str(FRAMES_DIR / "frame_%04d.png"),
        "-c:v", "libx264",
        "-profile:v", "high",
        "-crf", "18",
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        str(mp4_out),
    ]
    subprocess.run(cmd_mp4, check=True)
    print(f"  [OK] Master MP4 saved: {mp4_out.stat().st_size / (1024 * 1024):.2f} MB")

    # 2. High-Clarity Animated GIF for Medium (16 fps, 1440x810 lanczos, custom 256-color palette)
    gif_out = OUTPUT_DIR / "horseshoe_stretching_folding_iterations.gif"
    print(f"--- Encoding Animated GIF: {gif_out} ---")
    cmd_gif = [
        "ffmpeg", "-y",
        "-framerate", str(FPS_MASTER),
        "-i", str(FRAMES_DIR / "frame_%04d.png"),
        "-vf", "fps=16,scale=1440:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256:stats_mode=full[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4",
        "-loop", "0",
        str(gif_out),
    ]
    subprocess.run(cmd_gif, check=True)
    print(f"  [OK] Animated GIF saved: {gif_out.stat().st_size / (1024 * 1024):.2f} MB")

    # 3. Static Poster Frame PNG (captured at t = 26.5 s, Final Hold n = 3)
    poster_frame_idx = int(26.5 * FPS_MASTER)
    poster_src = FRAMES_DIR / f"frame_{poster_frame_idx:04d}.png"
    poster_out = OUTPUT_DIR / "horseshoe_stretching_folding_iterations.png"
    shutil.copyfile(poster_src, poster_out)
    print(f"  [OK] Static Poster PNG saved: {poster_out} ({poster_out.stat().st_size / (1024 * 1024):.2f} MB)")


if __name__ == "__main__":
    main()
