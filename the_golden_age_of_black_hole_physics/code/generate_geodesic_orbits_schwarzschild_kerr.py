#!/usr/bin/env python3
r"""
Generate scientific illustration & animation:
"BOUND GEODESIC MOTION: SCHWARZSCHILD VS. KERR SPACETIMES"
"From planar rosette precession to three-dimensional nodal precession"

Companion Figure & Animation for Section "Carter and the Integrability of Kerr Geodesics" of:
"The Golden Age of Black Hole Physics (1963–1974)"

Visual & Scientific Specifications:
- Matches the exact light scientific-illustration visual identity of the article
  (1800 x 900 px @ 140 DPI, white background #FFFFFF, light grey panels #F5F7FA,
  thin blue-grey borders #CBD5E1, dark navy typography #172136, saturated blue
  trajectories #2355D5 with progressively lighter older paths, and restrained
  amber/orange accents #D97706 for rotational and precessional features).
- Exact bound timelike geodesics integrated via KerrGeoPy (Black Hole Perturbation
  Toolkit) in Boyer–Lindquist coordinates and mapped to auxiliary Cartesian
  coordinates (x, y, z):
    p/m = 9.0, e = 0.25, inclination \iota = 45.0 deg (r_min = 7.2m, r_max = 12.0m).
- Custom 3D-to-2D camera projection onto each panel axis:
  - Enlarges orbital trajectories by ~30% compared to standard Matplotlib Axes3D boxes.
  - True depth occlusion around softly shaded 3D black-hole silhouettes.
  - All annotations placed in guaranteed clear corner regions with short leader lines.
- Continuous 20-second animation sequence (400 frames @ 20 fps, 10 radial cycles):
  - Fixed camera perspective (elev = 32.0 deg, azim = -138.0 deg) for both panels.
  - Progressive rosette accumulation in Schwarzschild (a = 0) with \Delta\omega \approx +266.8 deg
    (+267 deg) periapsis advance per radial cycle inside a single fixed orbital plane.
  - Three-dimensional prograde nonplanar orbit in Kerr (a = 0.8m) with \Delta\Omega \approx +19.6 deg
    (+19.55 deg) Lense–Thirring ascending-node precession per polar (\theta) cycle across the tilted
    latitude band |\theta - \pi/2| <= 45 deg, governed by Carter's fourth constant Q.

Numerical & Software Reference:
- Park, S., & Nasipak, Z. (2024). KerrGeoPy: A Python Package for Computing
  Timelike Geodesics in Kerr Spacetime. Journal of Open Source Software, 9(98), 6587.
  DOI: https://doi.org/10.21105/joss.06587
  GitHub: https://github.com/BlackHolePerturbationToolkit/KerrGeoPy
  Black Hole Perturbation Toolkit: https://bhptoolkit.org/
"""

import os
import sys
import time
import shutil
import subprocess
import tempfile
import multiprocessing
from pathlib import Path
import numpy as np
import scipy.optimize as opt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, FancyArrowPatch, Polygon
import kerrgeopy

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LOCAL_IMAGES_DIR = SCRIPT_DIR.parent / "images"

STATIC_OUT = LOCAL_IMAGES_DIR / "geodesic_orbits_schwarzschild_kerr.png"
GIF_OUT = LOCAL_IMAGES_DIR / "geodesic_orbits_schwarzschild_kerr_animation.gif"
MP4_OUT = LOCAL_IMAGES_DIR / "geodesic_orbits_schwarzschild_kerr_animation.mp4"

# Exact Canvas Dimensions & Styling matching lense_thirring_frame_dragging.py
CANVAS_W = 1800
CANVAS_H = 900
DPI = 140
FPS = 20
N_CYCLES = 10.0
N_FRAMES = 400

# Unified Light Scientific-Illustration Palette
BG_WHITE = '#ffffff'
PANEL_BG = '#f5f7fa'
CARD_BG = '#f8fafc'
BORDER_COLOR = '#cbd5e1'
GUIDE_COLOR = '#94a3b8'
AXIS_SLATE = '#64748b'

NAVY = '#172136'
DARK_SLATE = '#1e293b'
SLATE = '#334155'

# Trajectory Blues (foreground -> older paths)
BLUE_HEAD = '#1e3a8a'     # Leading tip
BLUE_ACTIVE = '#2355d5'   # Primary saturated blue
BLUE_MID = '#3b82f6'      # Intermediate loops
BLUE_OLD = '#93c5fd'      # Faded older loops
BLUE_BORDER = '#93c5fd'
BLUE_BG = '#eff6ff'

# Rotational & Precession Accents (Restrained Amber/Orange)
ORANGE_MAIN = '#d97706'
ORANGE_DARK = '#b45309'
ORANGE_LIGHT = '#fde68a'
ORANGE_BG = '#fffbeb'

# Projection scale & center offset inside p_ax ([-4.9, 4.9] x [-4.3, 4.3])
PROJ_SCALE = 0.232
PROJ_Y_OFFSET = -0.32
BH_VISUAL_SCALE = 1.30  # Modest 1.3x visual emphasis on central horizon silhouette


def compute_bh_sphere_rgba(rx=1.0, ry=1.0, res=240):
    """Precompute a softly shaded 3D dark charcoal-slate sphere/spheroid RGBA texture."""
    x_s = np.linspace(-rx, rx, res)
    y_s = np.linspace(-ry, ry, res)
    X_s, Y_s = np.meshgrid(x_s, y_s)
    R2_s = (X_s / rx)**2 + (Y_s / ry)**2
    mask_s = R2_s <= 1.0

    Z_s = np.zeros_like(X_s)
    Z_s[mask_s] = np.sqrt(1.0 - R2_s[mask_s])

    # Top-left front light source
    L = np.array([-0.38, 0.48, 0.79])
    L = L / np.linalg.norm(L)

    Nx = np.zeros_like(X_s)
    Ny = np.zeros_like(Y_s)
    Nz = np.zeros_like(Z_s)
    Nx[mask_s] = X_s[mask_s] / rx
    Ny[mask_s] = Y_s[mask_s] / ry
    Nz[mask_s] = Z_s[mask_s]

    diffuse = np.maximum(0.0, Nx * L[0] + Ny * L[1] + Nz * L[2])
    ambient = 0.18
    intensity = ambient + (1.0 - ambient) * diffuse
    H = L + np.array([0.0, 0.0, 1.0])
    H = H / np.linalg.norm(H)
    specular = np.maximum(0.0, Nx * H[0] + Ny * H[1] + Nz * H[2]) ** 22
    intensity = np.clip(intensity + 0.28 * specular, 0.0, 1.0)

    # Rich dark slate-charcoal palette for black-hole silhouette
    c_dark = np.array([11, 17, 32], dtype=float) / 255.0     # #0b1120
    c_mid = np.array([30, 41, 59], dtype=float) / 255.0      # #1e293b
    c_light = np.array([100, 116, 139], dtype=float) / 255.0 # #64748b

    rgba = np.zeros((res, res, 4))
    for i in range(res):
        for j in range(res):
            if mask_s[i, j]:
                val = intensity[i, j]
                if val < 0.65:
                    t_c = val / 0.65
                    c = (1.0 - t_c) * c_dark + t_c * c_mid
                else:
                    t_c = (val - 0.65) / 0.35
                    c = (1.0 - t_c) * c_mid + t_c * c_light
                rgba[i, j, :3] = c
                rgba[i, j, 3] = 1.0
    return rgba


BH_SCHW_RGBA = compute_bh_sphere_rgba(1.0, 1.0, res=240)
BH_KERR_RGBA = compute_bh_sphere_rgba(1.0, 1.0, res=240)


def project_3d(x, y, z, elev_deg, azim_deg, scale=PROJ_SCALE, y_offset=PROJ_Y_OFFSET):
    """
    Orthographic 3D-to-2D camera projection matching Matplotlib's (elev, azim) convention.
    Returns (X_screen, Y_screen, Depth_cam).
    """
    el = np.radians(elev_deg)
    az = np.radians(azim_deg)
    ux = np.array([-np.sin(az), np.cos(az), 0.0])
    uy = np.array([-np.sin(el) * np.cos(az), -np.sin(el) * np.sin(az), np.cos(el)])
    uz = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])

    X_scr = scale * (x * ux[0] + y * ux[1] + z * ux[2])
    Y_scr = scale * (x * uy[0] + y * uy[1] + z * uy[2]) + y_offset
    D_scr = x * uz[0] + y * uz[1] + z * uz[2]
    return X_scr, Y_scr, D_scr


def precompute_orbits():
    """Compute dense trajectories, periapses, and ascending nodes for both spacetimes."""
    p = 9.0
    e = 0.25
    inc = np.radians(45.0)
    x_inc = np.cos(inc)

    orb_s = kerrgeopy.StableOrbit(0.0, p, e, x_inc)
    orb_k = kerrgeopy.StableOrbit(0.8, p, e, x_inc)

    _, r_fn_s, th_fn_s, ph_fn_s = orb_s.trajectory()
    _, r_fn_k, th_fn_k, ph_fn_k = orb_k.trajectory()

    u_r_s, u_th_s, u_ph_s, _ = orb_s.mino_frequencies()
    u_r_k, u_th_k, u_ph_k, _ = orb_k.mino_frequencies()

    T_r_s = 2 * np.pi / u_r_s
    T_r_k = 2 * np.pi / u_r_k

    # Secular periapsis advance (Schwarzschild) and nodal shift (Kerr) from Mino frequencies
    delta_omega_s_deg = np.degrees(2.0 * np.pi * (u_ph_s / u_r_s - 1.0))
    delta_Omega_k_deg = np.degrees(2.0 * np.pi * (u_ph_k / u_th_k - 1.0))

    l_max_s = N_CYCLES * T_r_s
    l_max_k = N_CYCLES * T_r_k

    n_sample = 6000
    l_dense_s = np.linspace(0, l_max_s, n_sample)
    l_dense_k = np.linspace(0, l_max_k, n_sample)

    r_s = r_fn_s(l_dense_s)
    th_s = th_fn_s(l_dense_s)
    ph_s = ph_fn_s(l_dense_s)

    xs = r_s * np.sin(th_s) * np.cos(ph_s)
    ys = r_s * np.sin(th_s) * np.sin(ph_s)
    zs = r_s * np.cos(th_s)

    r_k = r_fn_k(l_dense_k)
    th_k = th_fn_k(l_dense_k)
    ph_k = ph_fn_k(l_dense_k)

    a_k = 0.8
    xk = np.sqrt(r_k**2 + a_k**2) * np.sin(th_k) * np.cos(ph_k)
    yk = np.sqrt(r_k**2 + a_k**2) * np.sin(th_k) * np.sin(ph_k)
    zk = r_k * np.cos(th_k)

    # Schwarzschild Periapses (at lambda = k * T_r_s)
    periapses_s = []
    for k in range(int(N_CYCLES) + 1):
        lp = k * T_r_s
        rp = r_fn_s(lp)
        thp = th_fn_s(lp)
        php = ph_fn_s(lp)
        xp = rp * np.sin(thp) * np.cos(php)
        yp = rp * np.sin(thp) * np.sin(php)
        zp = rp * np.cos(thp)
        periapses_s.append({
            'k': k,
            'lambda': lp,
            'phase': float(k),
            'pos': np.array([xp, yp, zp]),
            'r': rp,
            'phi': php
        })

    # Kerr Ascending Nodes (th crosses pi/2 with dth/dl < 0, moving north)
    ascending_nodes_k = []
    th_k_sample = th_k
    prev_phi_mod = None
    for i in range(len(l_dense_k) - 1):
        if th_k_sample[i] >= np.pi/2 and th_k_sample[i+1] < np.pi/2:
            res = opt.root_scalar(lambda l: th_fn_k(l) - np.pi/2, bracket=[l_dense_k[i], l_dense_k[i+1]])
            l_node = res.root
            r_node = r_fn_k(l_node)
            ph_node = ph_fn_k(l_node)
            xn = np.sqrt(r_node**2 + a_k**2) * np.cos(ph_node)
            yn = np.sqrt(r_node**2 + a_k**2) * np.sin(ph_node)
            zn = 0.0
            if prev_phi_mod is None:
                phi_mod = ph_node % (2.0 * np.pi)
            else:
                dphi = (ph_node - prev_phi_mod) % (2.0 * np.pi)
                phi_mod = prev_phi_mod + dphi
            prev_phi_mod = phi_mod
            ascending_nodes_k.append({
                'idx': len(ascending_nodes_k),
                'lambda': l_node,
                'phase': l_node / T_r_k,
                'pos': np.array([xn, yn, zn]),
                'r': r_node,
                'phi': ph_node,
                'phi_mod': phi_mod
            })

    return {
        'T_r_s': T_r_s,
        'T_r_k': T_r_k,
        'delta_omega_s_deg': delta_omega_s_deg,
        'delta_Omega_k_deg': delta_Omega_k_deg,
        'l_max_s': l_max_s,
        'l_max_k': l_max_k,
        'dense_s': (l_dense_s, xs, ys, zs),
        'dense_k': (l_dense_k, xk, yk, zk),
        'periapses_s': periapses_s,
        'ascending_nodes_k': ascending_nodes_k,
    }


FIXED_ELEV = 32.0
FIXED_AZIM = -138.0


def get_timeline(frame_idx, n_frames=N_FRAMES):
    """
    Fixed-camera 20-second timeline (400 frames at 20 fps) across 10 radial cycles:
    - Both panels use the identical fixed camera angle (elev = 32 deg, azim = -138 deg)
      throughout the entire animation.
    - 0.0 to 17.0 s (Frames 0 to 340): Trace all 10 radial cycles at a strictly uniform
      rate (1.70 s per radial cycle, phase 0.0 -> 10.0) with no mid-animation speedup.
    - 17.0 to 20.0 s (Frames 340 to 400): Hold the completed trajectories (phase = 10.0) for
      3.0 seconds before looping so readers can examine the resulting patterns.
    """
    if frame_idx < 340:
        phase = N_CYCLES * (frame_idx / 340.0)
    else:
        phase = N_CYCLES

    return phase, FIXED_ELEV, FIXED_AZIM


def plot_depth_sorted_segments(ax, X, Y, D, color, lw, alpha, z_back=3, z_front=8):
    """Plot a 2D projected curve split into behind-origin (z_back) and front-of-origin (z_front) segments."""
    if len(X) < 2:
        return
    is_front = D >= 0.0
    # Find contiguous runs of is_front
    changes = np.where(is_front[:-1] != is_front[1:])[0] + 1
    splits = np.split(np.arange(len(X)), changes)
    for seg in splits:
        if len(seg) == 0:
            continue
        # Extend by 1 index on boundaries so segments join seamlessly
        i0 = max(0, seg[0] - 1)
        i1 = min(len(X), seg[-1] + 2)
        z_ord = z_front if is_front[seg[0]] else z_back
        ax.plot(X[i0:i1], Y[i0:i1], color=color, linewidth=lw, alpha=alpha,
                solid_capstyle='round', solid_joinstyle='round', zorder=z_ord)


def plot_tiered_trajectory(ax, l_arr, x, y, z, l_cur, T_r, elev, azim, is_kerr=False):
    """
    Plot multi-tier blue trajectory with depth sorting:
    - Older paths kept visible but relatively light (especially in Schwarzschild so
      12 overlapping rosette loops do not obscure the pattern).
    - Most recent full radial cycle drawn in saturated blue (#2355D5).
    """
    mask = l_arr <= l_cur
    if not np.any(mask):
        return

    l_sub = l_arr[mask]
    x_sub = x[mask]
    y_sub = y[mask]
    z_sub = z[mask]

    X_sub, Y_sub, D_sub = project_3d(x_sub, y_sub, z_sub, elev, azim)
    age = l_cur - l_sub

    # Tier 4: Older accumulated paths (age >= 2.0 Tr, cycles 1..10)
    m4 = age >= 1.98 * T_r
    if np.any(m4):
        c4 = '#7aaef8' if not is_kerr else '#60a5fa'
        lw4 = 1.15 if not is_kerr else 1.25
        al4 = 0.34 if not is_kerr else 0.40
        plot_depth_sorted_segments(ax, X_sub[m4], Y_sub[m4], D_sub[m4],
                                   color=c4, lw=lw4, alpha=al4, z_back=3, z_front=7.5)

    # Tier 3: Preceding cycle (1.0 Tr <= age <= 2.0 Tr)
    m3 = (age <= 2.02 * T_r) & (age >= 0.98 * T_r)
    if np.any(m3):
        c3 = '#60a5fa' if not is_kerr else '#3b82f6'
        lw3 = 1.50 if not is_kerr else 1.65
        al3 = 0.50 if not is_kerr else 0.58
        plot_depth_sorted_segments(ax, X_sub[m3], Y_sub[m3], D_sub[m3],
                                   color=c3, lw=lw3, alpha=al3, z_back=3.2, z_front=8.0)

    # Tier 2: Most recent radial cycle (0.15 Tr <= age <= 1.0 Tr) in saturated blue
    m2 = (age <= 1.02 * T_r) & (age >= 0.13 * T_r)
    if np.any(m2):
        plot_depth_sorted_segments(ax, X_sub[m2], Y_sub[m2], D_sub[m2],
                                   color=BLUE_ACTIVE, lw=2.65, alpha=0.96, z_back=3.4, z_front=8.5)

    # Tier 1: Bright foreground leading trail (age <= 0.15 Tr)
    m1 = age <= 0.17 * T_r
    if np.any(m1):
        plot_depth_sorted_segments(ax, X_sub[m1], Y_sub[m1], D_sub[m1],
                                   color='#60a5fa', lw=5.8, alpha=0.28, z_back=3.5, z_front=8.8)
        plot_depth_sorted_segments(ax, X_sub[m1], Y_sub[m1], D_sub[m1],
                                   color=BLUE_HEAD, lw=3.4, alpha=1.0, z_back=3.6, z_front=9.0)

    # Moving particle marker at leading tip
    px, py, pd = X_sub[-1], Y_sub[-1], D_sub[-1]
    z_part = 14 if pd >= 0 else 4
    ax.scatter([px], [py], color=BLUE_ACTIVE, s=145, alpha=0.28, edgecolors='none', zorder=z_part - 0.1)
    ax.scatter([px], [py], color=BLUE_HEAD, s=64, edgecolors='#ffffff', linewidths=1.5, zorder=z_part)


def draw_frame(data, phase, elev, azim, output_path, is_static=False):
    """Render a complete two-panel frame in the unified light scientific-illustration style."""
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    fig_w, fig_h = CANVAS_W / float(DPI), CANVAS_H / float(DPI)
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=DPI, facecolor=BG_WHITE)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # 1. Clean Two-Line Top Header Banner
    title_box = FancyBboxPatch((0.020, 0.875), 0.960, 0.105,
                               boxstyle="round,pad=0.002,rounding_size=0.008",
                               facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax.add_patch(title_box)
    ax.text(0.50, 0.948, "BOUND GEODESIC MOTION: SCHWARZSCHILD VS. KERR SPACETIMES",
            color=NAVY, fontsize=17.8, fontweight='bold', ha='center', va='center')
    ax.text(0.50, 0.898, "Planar rosette precession vs. three-dimensional nodal precession",
            color=SLATE, fontsize=13.5, fontweight='bold', ha='center', va='center')

    # 2. Two Equal Panel Subplots
    p_w = 0.472
    p_h = 0.835
    p_y = 0.020

    ax_a = fig.add_axes([0.020, p_y, p_w, p_h])
    ax_b = fig.add_axes([0.508, p_y, p_w, p_h])

    for p_ax, p_letter, p_title, p_sub, is_kerr in [
        (ax_a, "A", "Schwarzschild spacetime  (a = 0)", "Fixed orbital plane with periapsis advance", False),
        (ax_b, "B", "Rotating Kerr spacetime  (a = 0.8m)", "Prograde inclined orbit with nodal precession", True)
    ]:
        p_ax.set_xlim(-4.9, 4.9)
        p_ax.set_ylim(-4.3, 4.3)
        p_ax.set_aspect('equal')
        p_ax.axis('off')

        # Panel background card (#F5F7FA with thin blue-grey border #CBD5E1)
        card = FancyBboxPatch((-4.75, -4.15), 9.5, 8.3,
                              boxstyle="round,pad=0.02,rounding_size=0.15",
                              facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=0)
        p_ax.add_patch(card)

        # Expanded inner central viewport card (#FFFFFF)
        viewport = FancyBboxPatch((-4.52, -3.95), 9.04, 6.95,
                                  boxstyle="round,pad=0.02,rounding_size=0.10",
                                  facecolor=BG_WHITE, edgecolor='#e2e8f0', linewidth=1.0, zorder=0.5)
        p_ax.add_patch(viewport)

        # Panel Header Box inside card (with increased interline spacing)
        hdr_box = FancyBboxPatch((-4.52, 3.15), 9.04, 0.96,
                                 boxstyle="round,pad=0.02,rounding_size=0.08",
                                 facecolor=BG_WHITE if not is_kerr else ORANGE_BG,
                                 edgecolor=BORDER_COLOR if not is_kerr else ORANGE_LIGHT,
                                 linewidth=1.2, zorder=1)
        p_ax.add_patch(hdr_box)

        p_ax.text(0.0, 3.84, f"{p_letter}  ·  {p_title}",
                  color=NAVY if not is_kerr else ORANGE_DARK,
                  fontsize=15.5, fontweight='bold', ha='center', va='center', zorder=2)
        p_ax.text(0.0, 3.38, p_sub,
                  color=SLATE if not is_kerr else DARK_SLATE,
                  fontsize=12.8, fontweight='bold', ha='center', va='center', zorder=2)

        # 3. Equatorial Reference Plane & Concentric Guides (z = 0)
        phi_ring = np.linspace(0, 2 * np.pi, 160)
        r_disk = 12.2
        X_eq_d, Y_eq_d, _ = project_3d(r_disk * np.cos(phi_ring), r_disk * np.sin(phi_ring),
                                       np.zeros_like(phi_ring), elev, azim)
        p_ax.fill(X_eq_d, Y_eq_d, facecolor='#f1f5f9', edgecolor='none', alpha=0.55, zorder=1)

        for r_g, lw_g, ls_g in [(6.0, 0.9, ':'), (9.0, 1.0, '--'), (12.0, 1.1, '--')]:
            Xg, Yg, Dg = project_3d(r_g * np.cos(phi_ring), r_g * np.sin(phi_ring),
                                    np.zeros_like(phi_ring), elev, azim)
            plot_depth_sorted_segments(p_ax, Xg, Yg, Dg, color=GUIDE_COLOR, lw=lw_g, alpha=0.60, z_back=1.5, z_front=5.5)

        # Equatorial coordinate axes (x and y axes) — kept behind black-hole silhouette (z <= 4.5)
        for ax_vec in [np.array([12.8, 0, 0]), np.array([0, 12.8, 0])]:
            pts = np.linspace(-1.0, 1.0, 50)
            Xa, Ya, Da = project_3d(pts * ax_vec[0], pts * ax_vec[1], pts * ax_vec[2], elev, azim)
            plot_depth_sorted_segments(p_ax, Xa, Ya, Da, color=GUIDE_COLOR, lw=0.9, alpha=0.50, z_back=1.5, z_front=4.5)

        # 4. Vertical Symmetry / Rotation Axis (z-axis)
        z_neg = np.linspace(-11.2, 0.0, 30)
        Xz_n, Yz_n, _ = project_3d(np.zeros_like(z_neg), np.zeros_like(z_neg), z_neg, elev, azim)
        p_ax.plot(Xz_n, Yz_n, color=AXIS_SLATE if not is_kerr else ORANGE_MAIN,
                  lw=1.6, ls='--', alpha=0.60, zorder=2)

        z_pos = np.linspace(1.8, 12.2, 30)
        Xz_p, Yz_p, _ = project_3d(np.zeros_like(z_pos), np.zeros_like(z_pos), z_pos, elev, azim)
        if not is_kerr:
            p_ax.plot(Xz_p, Yz_p, color=AXIS_SLATE, lw=1.8, ls='-.', alpha=0.80, zorder=10)
        else:
            p_ax.plot(Xz_p[:-4], Yz_p[:-4], color=ORANGE_MAIN, lw=2.5, ls='-', zorder=10)
            p_ax.annotate('', xy=(Xz_p[-1], Yz_p[-1]), xytext=(Xz_p[-6], Yz_p[-6]),
                          arrowprops=dict(arrowstyle='-|>', color=ORANGE_MAIN, lw=2.6, mutation_scale=16),
                          zorder=11)

        # 5. Central Softly Shaded Black-Hole Silhouette (zorder = 5)
        if not is_kerr:
            r_bh = 2.0 * BH_VISUAL_SCALE * PROJ_SCALE
            p_ax.imshow(BH_SCHW_RGBA, extent=[-r_bh, r_bh, PROJ_Y_OFFSET - r_bh, PROJ_Y_OFFSET + r_bh],
                        origin='lower', zorder=5)
            p_ax.add_patch(Circle((0.0, PROJ_Y_OFFSET), r_bh, fill=False, edgecolor=NAVY, linewidth=1.4, zorder=5.2))
        else:
            r_eq_bh = np.sqrt(1.6**2 + 0.8**2) * BH_VISUAL_SCALE * PROJ_SCALE
            r_pol_bh = 1.6 * BH_VISUAL_SCALE * PROJ_SCALE
            r_erg_eq = np.sqrt(2.0**2 + 0.8**2) * BH_VISUAL_SCALE * PROJ_SCALE
            p_ax.add_patch(Ellipse((0.0, PROJ_Y_OFFSET), 2 * r_erg_eq, 2 * r_pol_bh * 1.06,
                                   facecolor='#fef3c7', edgecolor=ORANGE_MAIN, linestyle='--',
                                   linewidth=1.2, alpha=0.58, zorder=4.8))
            p_ax.imshow(BH_KERR_RGBA, extent=[-r_eq_bh, r_eq_bh, PROJ_Y_OFFSET - r_pol_bh, PROJ_Y_OFFSET + r_pol_bh],
                        origin='lower', zorder=5)
            p_ax.add_patch(Ellipse((0.0, PROJ_Y_OFFSET), 2 * r_eq_bh, 2 * r_pol_bh,
                                   fill=False, edgecolor=NAVY, linewidth=1.4, zorder=5.2))
            rot_arc = FancyArrowPatch((-r_eq_bh * 0.85, PROJ_Y_OFFSET - r_pol_bh * 0.22),
                                      (r_eq_bh * 0.85, PROJ_Y_OFFSET - r_pol_bh * 0.22),
                                      connectionstyle="arc3,rad=0.36",
                                      arrowstyle='-|>', mutation_scale=11,
                                      color=ORANGE_MAIN, linewidth=2.0, zorder=5.4)
            p_ax.add_patch(rot_arc)

    # =========================================================================
    # PANEL A SPECIFICS: Schwarzschild Planar Rosette & Periapsis Advance
    # =========================================================================
    u_pl = np.linspace(0, 2 * np.pi, 160)
    r_pl_max = 12.2
    x_pl = (r_pl_max * np.cos(u_pl)) / np.sqrt(2.0)
    y_pl = r_pl_max * np.sin(u_pl)
    z_pl = (r_pl_max * np.cos(u_pl)) / np.sqrt(2.0)
    X_pl, Y_pl, D_pl = project_3d(x_pl, y_pl, z_pl, elev, azim)
    ax_a.fill(X_pl, Y_pl, facecolor='#dbeafe', edgecolor='none', alpha=0.25, zorder=1.8)
    plot_depth_sorted_segments(ax_a, X_pl, Y_pl, D_pl, color='#3b82f6', lw=1.1, alpha=0.55, z_back=2.0, z_front=6.0)

    l_cur_s = phase * data['T_r_s']
    l_dense_s, xs, ys, zs = data['dense_s']
    plot_tiered_trajectory(ax_a, l_dense_s, xs, ys, zs, l_cur_s, data['T_r_s'], elev, azim, is_kerr=False)

    # Periapsis markers & radial spokes (curved arrow omitted so the -93 deg modulo shortcut
    # does not visually suggest retrograde/clockwise precession; the rosette itself shows the +267 deg advance)
    peri_passed = [p for p in data['periapses_s'] if p['phase'] <= phase + 1e-4]
    peri_displayed = peri_passed[:7]
    for peri in peri_displayed:
        px3, py3, pz3 = peri['pos']
        Xp, Yp, Dp = project_3d(px3, py3, pz3, elev, azim)
        z_mk = 12 if Dp >= 0 else 4.3
        ax_a.plot([0.0, Xp], [PROJ_Y_OFFSET, Yp], color=ORANGE_MAIN,
                  linestyle=(0, (3.2, 2.0)), lw=1.75, alpha=0.88, zorder=4.2)
        ax_a.scatter([Xp], [Yp], color=ORANGE_MAIN, s=64, edgecolors='#ffffff', linewidths=1.4, zorder=z_mk)

    # Simplified, Essential Panel A Labels (3 high-legibility labels)
    Xz_top_s, Yz_top_s, _ = project_3d(0.0, 0.0, 11.2, elev, azim)
    ax_a.annotate(r"Symmetry axis ($z$)",
                  xy=(Xz_top_s, Yz_top_s), xytext=(2.90, 2.48),
                  arrowprops=dict(arrowstyle="->", color=AXIS_SLATE, lw=1.4, shrinkA=2, shrinkB=3),
                  fontsize=11.8, fontweight='bold', color=DARK_SLATE, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.24', facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.0),
                  zorder=16)

    idx_pl_tl = int(np.argmin((X_pl - (-2.3))**2 + (Y_pl - 1.55)**2))
    ax_a.annotate("Fixed orbital plane",
                  xy=(X_pl[idx_pl_tl], Y_pl[idx_pl_tl]), xytext=(-2.78, 2.48),
                  arrowprops=dict(arrowstyle="->", color=BLUE_ACTIVE, lw=1.4, shrinkA=2, shrinkB=3),
                  fontsize=11.8, fontweight='bold', color=BLUE_HEAD, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.24', facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.0),
                  zorder=16)

    target_peri = peri_passed[1]['pos'] if len(peri_passed) >= 2 else peri_passed[0]['pos']
    X_tp, Y_tp, _ = project_3d(target_peri[0], target_peri[1], target_peri[2], elev, azim)
    dw_s_round = int(round(data['delta_omega_s_deg']))
    ax_a.annotate(rf"Periapsis advance ($\Delta\omega \approx +{dw_s_round}^\circ$/cycle)",
                  xy=(X_tp, Y_tp), xytext=(1.45, -3.42),
                  arrowprops=dict(arrowstyle="->", color=ORANGE_MAIN, lw=1.5, shrinkA=2, shrinkB=4),
                  fontsize=11.8, fontweight='bold', color=ORANGE_DARK, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.25', facecolor=ORANGE_BG, edgecolor=ORANGE_LIGHT, linewidth=1.1),
                  zorder=16)

    # =========================================================================
    # PANEL B SPECIFICS: Kerr Nonplanar 3D Trajectory & Nodal Precession
    # =========================================================================
    l_cur_k = phase * data['T_r_k']
    l_dense_k, xk, yk, zk = data['dense_k']
    plot_tiered_trajectory(ax_b, l_dense_k, xk, yk, zk, l_cur_k, data['T_r_k'], elev, azim, is_kerr=True)

    nodes_passed = [node for node in data['ascending_nodes_k'] if node['phase'] <= phase + 1e-4]
    nodes_displayed = nodes_passed[:5]
    r_arc_k = 10.6
    r_lbl_k = 11.4
    dOmega_step = round(data['delta_Omega_k_deg'], 1)
    node_cum_labels = ["0°" if i == 0 else f"+{i * dOmega_step:.1f}°" for i in range(5)]
    for idx_n, node in enumerate(nodes_displayed):
        nx3, ny3, nz3 = node['pos']
        Xn, Yn, Dn = project_3d(nx3, ny3, nz3, elev, azim)
        ph_n = node['phi_mod']
        Xa_pt, Ya_pt, _ = project_3d(r_arc_k * np.cos(ph_n), r_arc_k * np.sin(ph_n), 0.0, elev, azim)
        Xl_pt, Yl_pt, _ = project_3d(r_lbl_k * np.cos(ph_n), r_lbl_k * np.sin(ph_n), 0.0, elev, azim)
        z_nd = 12 if Dn >= 0 else 4.3
        # Dashed orange radial line out to the node / arc
        end_x = Xa_pt if np.hypot(Xa_pt, Ya_pt - PROJ_Y_OFFSET) > np.hypot(Xn, Yn - PROJ_Y_OFFSET) else Xn
        end_y = Ya_pt if np.hypot(Xa_pt, Ya_pt - PROJ_Y_OFFSET) > np.hypot(Xn, Yn - PROJ_Y_OFFSET) else Yn
        ax_b.plot([0.0, end_x], [PROJ_Y_OFFSET, end_y], color=ORANGE_MAIN,
                  linestyle=(0, (3.2, 2.0)), lw=1.75, alpha=0.88, zorder=4.2)
        ax_b.scatter([Xn], [Yn], color=ORANGE_MAIN, s=64, edgecolors='#ffffff', linewidths=1.4, zorder=z_nd)
        # Dynamic cumulative nodal shift label next to each ascending node spoke
        lbl_str = node_cum_labels[idx_n]
        ax_b.text(Xl_pt + 0.14, Yl_pt, lbl_str,
                  fontsize=10.2, fontweight='bold', color=ORANGE_DARK,
                  ha='left', va='center',
                  bbox=dict(boxstyle='round,pad=0.16', facecolor=ORANGE_BG, edgecolor=ORANGE_LIGHT, linewidth=0.9, alpha=0.94),
                  zorder=15)

    if len(nodes_displayed) >= 2:
        ph_start = nodes_displayed[0]['phi_mod']
        ph_end = nodes_displayed[-1]['phi_mod']
        ph_arc_k = np.linspace(ph_start, ph_end, 50)
        Xa_k, Ya_k, Da_k = project_3d(r_arc_k * np.cos(ph_arc_k), r_arc_k * np.sin(ph_arc_k),
                                      np.zeros_like(ph_arc_k), elev, azim)
        plot_depth_sorted_segments(ax_b, Xa_k, Ya_k, Da_k, color=ORANGE_MAIN, lw=2.3, alpha=0.92, z_back=4.1, z_front=11.5)
        ax_b.annotate('', xy=(Xa_k[-1], Ya_k[-1]), xytext=(Xa_k[-5], Ya_k[-5]),
                      arrowprops=dict(arrowstyle='-|>', color=ORANGE_MAIN, lw=2.1, mutation_scale=13),
                      zorder=13)

    # Simplified, Essential Panel B Labels (3 high-legibility labels)
    Xz_top_k, Yz_top_k, _ = project_3d(0.0, 0.0, 11.4, elev, azim)
    ax_b.annotate(r"Rotation axis ($z$), $\mathbf{J}$",
                  xy=(Xz_top_k, Yz_top_k), xytext=(2.90, 2.48),
                  arrowprops=dict(arrowstyle="->", color=ORANGE_MAIN, lw=1.5, shrinkA=2, shrinkB=3),
                  fontsize=11.8, fontweight='bold', color=ORANGE_DARK, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.24', facecolor=ORANGE_BG, edgecolor=ORANGE_LIGHT, linewidth=1.1),
                  zorder=16)

    Xk_all, Yk_all, _ = project_3d(xk, yk, zk, elev, azim)
    idx_k_tl = int(np.argmin((Xk_all - (-2.2))**2 + (Yk_all - 1.55)**2))
    ax_b.annotate("Nonplanar 3D orbit",
                  xy=(Xk_all[idx_k_tl], Yk_all[idx_k_tl]), xytext=(-2.78, 2.48),
                  arrowprops=dict(arrowstyle="->", color=BLUE_ACTIVE, lw=1.4, shrinkA=2, shrinkB=3),
                  fontsize=11.8, fontweight='bold', color=BLUE_HEAD, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.24', facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.0),
                  zorder=16)

    tn_pos = nodes_displayed[0]['pos'] if len(nodes_displayed) >= 1 else data['ascending_nodes_k'][0]['pos']
    X_tn, Y_tn, _ = project_3d(tn_pos[0], tn_pos[1], tn_pos[2], elev, azim)
    n_shifts = max(0, len(nodes_displayed) - 1)
    if n_shifts == 0:
        nodal_box_text = rf"Nodal shift ($\Delta\Omega \approx +{dOmega_step:.1f}^\circ$/cycle)"
    else:
        nodal_box_text = rf"Nodal shift: $\Sigma\Delta\Omega = {node_cum_labels[n_shifts]}$ ($+{dOmega_step:.1f}^\circ$/cycle)"
    ax_b.annotate(nodal_box_text,
                  xy=(X_tn, Y_tn), xytext=(1.25, -3.42),
                  arrowprops=dict(arrowstyle="->", color=ORANGE_MAIN, lw=1.5, shrinkA=2, shrinkB=4),
                  fontsize=11.5, fontweight='bold', color=ORANGE_DARK, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.25', facecolor=ORANGE_BG, edgecolor=ORANGE_LIGHT, linewidth=1.1),
                  zorder=16)

    plt.savefig(output_path, dpi=DPI, facecolor=BG_WHITE)
    plt.close()


def render_worker(args):
    """Worker function for multiprocessing."""
    data, phase, elev, azim, out_path = args
    draw_frame(data, phase, elev, azim, out_path, is_static=False)


def generate_assets():
    """Generate static publication figure, MP4, and animated GIF."""
    t0 = time.time()
    print("=== Generating Unified Light-Style Schwarzschild vs. Kerr Geodesic Animation ===")

    LOCAL_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Precompute Orbits
    print("1. Integrating geodesics with KerrGeoPy...")
    data = precompute_orbits()
    print(f"   Schwarzschild: T_r = {data['T_r_s']:.3f} Mino time ({len(data['periapses_s'])} periapses)")
    print(f"   Kerr:          T_r = {data['T_r_k']:.3f} Mino time ({len(data['ascending_nodes_k'])} ascending nodes)")

    # 2. Static Publication Figure (Phase = 6.0, fixed joint perspective: elev=32, azim=-138)
    print("2. Rendering static publication figure...")
    draw_frame(data, phase=N_CYCLES, elev=FIXED_ELEV, azim=FIXED_AZIM, output_path=STATIC_OUT, is_static=True)
    static_size_kb = STATIC_OUT.stat().st_size / 1024
    print(f"[OK] Static figure: {STATIC_OUT} ({static_size_kb:.1f} KB)")

    # 3. Render Animation Frames
    frames_dir = Path(tempfile.mkdtemp(prefix="kerr_geodesic_frames_"))
    print(f"3. Rendering {N_FRAMES} frames in {frames_dir}...")

    tasks = []
    for idx in range(N_FRAMES):
        phase, elev, azim = get_timeline(idx, N_FRAMES)
        frame_file = frames_dir / f"frame_{idx:04d}.png"
        tasks.append((data, phase, elev, azim, str(frame_file)))

    n_workers = max(1, multiprocessing.cpu_count() - 1)
    with multiprocessing.Pool(processes=n_workers) as pool:
        pool.map(render_worker, tasks)

    dt_frames = time.time() - t0
    print(f"[OK] Rendered {N_FRAMES} frames in {dt_frames:.1f} s ({dt_frames/N_FRAMES:.3f} s/frame)")

    # 4. Encode MP4 Video (1800 x 900 px)
    print("4. Encoding MP4 video...")
    cmd_mp4 = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-c:v", "libx264",
        "-profile:v", "high",
        "-crf", "18",
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        str(MP4_OUT),
    ]
    res_mp4 = subprocess.run(cmd_mp4, capture_output=True, text=True)
    if res_mp4.returncode != 0:
        print("[ERROR] FFmpeg MP4 failed:\n", res_mp4.stderr)
        raise RuntimeError("FFmpeg MP4 encoding failed")
    mp4_mb = MP4_OUT.stat().st_size / (1024 * 1024)
    print(f"[OK] Generated MP4: {MP4_OUT} ({mp4_mb:.2f} MB)")

    # 5. Encode Animated GIF (Medium-optimized: 1200 px width, Lanczos + palettegen)
    print("5. Encoding animated GIF...")
    cmd_gif = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-vf", f"fps={FPS},scale=1200:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=224:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4",
        "-loop", "0",
        str(GIF_OUT),
    ]
    res_gif = subprocess.run(cmd_gif, capture_output=True, text=True)
    if res_gif.returncode != 0:
        print("[ERROR] FFmpeg GIF failed:\n", res_gif.stderr)
        raise RuntimeError("FFmpeg GIF encoding failed")
    gif_mb = GIF_OUT.stat().st_size / (1024 * 1024)
    print(f"[OK] Generated GIF: {GIF_OUT} ({gif_mb:.2f} MB)")

    # Clean up frames
    shutil.rmtree(frames_dir, ignore_errors=True)
    print(f"=== Complete in {time.time() - t0:.1f} s ===")


if __name__ == '__main__':
    generate_assets()
