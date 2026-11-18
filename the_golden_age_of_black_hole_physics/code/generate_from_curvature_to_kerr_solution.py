#!/usr/bin/env python3
"""
Generate animated scientific illustration (2000 x 1200 px):
"FROM CURVATURE TO KERR'S SOLUTION"
"Principal null directions, algebraic speciality, and shear-free null congruences"

Implements the full specification for Section "The Discovery of the Kerr Solution":
- Static Upper Section (~40% height):
  - Panel A ("A · Generic Weyl curvature" / "Four distinct PNDs"):
    Celestial sphere S² of future-directed null directions k^a ~ lambda k^a at one event,
    showing 4 distinct roots (z1, z2, z3, z4) of the Newman–Penrose Weyl quartic
      Psi_0 + 4 z Psi_1 + 6 z^2 Psi_2 + 4 z^3 Psi_3 + z^4 Psi_4 = 0,   z in CP^1 ~ S^2.
  - Panel B ("B · Kerr curvature" / "Two double PNDs (2 + 2)"):
    Same celestial-sphere projection showing two antipodal repeated principal null directions
    (z1 = z2 and z3 = z4, each marked with multiplicity 2):
      P(z) propto (z - z_+)^2 (z - z_-)^2.
- Static Middle Bridge:
  - Goldberg–Sachs theorem equivalence in four-dimensional vacuum spacetime:
      Repeated principal null direction <==> Geodesic, shear-free null congruence
- Animated Lower Section (~45% height, Panel C — Optical deformation of null congruences):
  - Displays optical deformation tensor decomposition:
      B_AB = (1/2) theta delta_AB + sigma_AB + omega_AB,   d xi / d lambda = B(lambda) xi
  - Three simultaneous elementary animated subpanels (lambda in [0, 5] over t in [0, 10] s + 1 s hold):
    * C1 — Pure expansion (alpha = 0.10, R(5) = 1.65 R0, 6 markers)
    * C2 — Pure shear (beta = 0.12, a(5) = 1.82 R0, b(5) = 0.55 R0, area preserved, 6 markers)
    * C3 — Pure twist (varpi = 0.15, Delta phi(5) = 0.75 rad ~ 43°, 6 markers + radial line)
  - Prominent fourth combined demonstration (C4 — Kerr-like shear-free congruence):
    * Simultaneous expansion and twist without shear (alpha = 0.08, varpi = 0.20,
      R(5) = 1.49 R0, Delta phi(5) = 1.0 rad ~ 57°, 8 markers + radial line)
    * Boxed condition: sigma_AB = 0,  theta != 0,  omega_AB != 0.
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
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Arc, FancyArrowPatch

SCRIPT_DIR = Path(__file__).resolve().parent
PNG_OUT = SCRIPT_DIR.parent / "images" / "from_curvature_to_kerr_solution.png"
GIF_OUT = SCRIPT_DIR.parent / "images" / "from_curvature_to_kerr_solution_animation.gif"
MP4_OUT = SCRIPT_DIR.parent / "images" / "from_curvature_to_kerr_solution_animation.mp4"

# Animation timing parameters (6 s linear motion + 1 s final hold = 7 s total @ 20 fps)
FPS = 20
N_MOTION_FRAMES = 120   # 6.0 s of linear motion: lambda = 0.0 to lambda = 5.0 inclusive
N_HOLD_FRAMES = 20      # 1.0 s final hold at lambda = 5.0
N_TOTAL_FRAMES = N_MOTION_FRAMES + N_HOLD_FRAMES  # 140 frames (7.0 s total)

# Optical deformation parameters (Specification Sections 4 & 5)
R0 = 1.0
ALPHA_EXP = 0.10
BETA_SHEAR = 0.12
VARPI_TWIST = 0.15
ALPHA_SF = 0.08
VARPI_SF = 0.20


def deformation_matrix(mode, lam):
    """Return the 2x2 transverse evolution matrix M(lambda) = exp(B * lambda)."""
    if mode == "expansion":
        s = np.exp(ALPHA_EXP * lam)
        return np.array([[s, 0.0], [0.0, s]])
    elif mode == "shear":
        return np.array([[np.exp(BETA_SHEAR * lam), 0.0],
                         [0.0, np.exp(-BETA_SHEAR * lam)]])
    elif mode == "twist":
        ang = VARPI_TWIST * lam
        c, s = np.cos(ang), np.sin(ang)
        return np.array([[c, -s], [s, c]])
    elif mode == "shear_free":
        s_exp = np.exp(ALPHA_SF * lam)
        ang = VARPI_SF * lam
        c, s = np.cos(ang), np.sin(ang)
        return s_exp * np.array([[c, -s], [s, c]])
    else:
        raise ValueError(f"Unknown mode: {mode}")


def validate_optical_models():
    """
    Scientific validation checklist (Specification Section 8):
    Verify singular values of each transverse deformation map M(lambda) across lambda in [0, 5].
    """
    for lam in np.linspace(0.0, 5.0, 11):
        # 1. Pure expansion: both singular values equal exp(alpha * lambda)
        sv_exp = np.linalg.svd(deformation_matrix("expansion", lam), compute_uv=False)
        assert np.allclose(sv_exp, np.exp(ALPHA_EXP * lam), atol=1e-12)

        # 2. Pure shear: singular values exp(beta * lambda) and exp(-beta * lambda), det = 1
        M_sh = deformation_matrix("shear", lam)
        sv_sh = np.linalg.svd(M_sh, compute_uv=False)
        assert np.allclose( sorted(sv_sh), [np.exp(-BETA_SHEAR * lam), np.exp(BETA_SHEAR * lam)], atol=1e-12)
        assert np.isclose(np.linalg.det(M_sh), 1.0, atol=1e-12)

        # 3. Pure twist: both singular values equal 1
        sv_tw = np.linalg.svd(deformation_matrix("twist", lam), compute_uv=False)
        assert np.allclose(sv_tw, 1.0, atol=1e-12)

        # 4. Combined shear-free: both singular values equal exp(alpha_sf * lambda)
        sv_sf = np.linalg.svd(deformation_matrix("shear_free", lam), compute_uv=False)
        assert np.allclose(sv_sf, np.exp(ALPHA_SF * lam), atol=1e-12)


def precompute_celestial_sphere_rgba(R_sph=1.0, res=280):
    """Precompute a soft muted-blue shaded celestial sphere RGBA texture."""
    x = np.linspace(-R_sph, R_sph, res)
    y = np.linspace(-R_sph, R_sph, res)
    X, Y = np.meshgrid(x, y)
    R2 = X**2 + Y**2
    mask = R2 <= R_sph**2
    Z = np.zeros_like(X)
    Z[mask] = np.sqrt(R_sph**2 - R2[mask])

    L = np.array([-0.35, 0.42, 0.84])
    L /= np.linalg.norm(L)
    diffuse = np.maximum(0.0, (X * L[0] + Y * L[1] + Z * L[2]) / R_sph)

    # Soft muted slate-blue tint matching the reference specification
    c_edge = np.array([219, 234, 254], dtype=float) / 255.0   # #dbeafe
    c_center = np.array([248, 250, 252], dtype=float) / 255.0 # #f8fafc

    rgba = np.zeros((res, res, 4))
    for i in range(res):
        for j in range(res):
            if mask[i, j]:
                w = 0.25 + 0.75 * diffuse[i, j]
                rgba[i, j, :3] = (1.0 - w) * c_edge + w * c_center
                rgba[i, j, 3] = 0.92
    return rgba


CELESTIAL_RGBA = precompute_celestial_sphere_rgba()


def spherical_to_2d(theta_deg, phi_deg, R_sph=1.0, tilt_deg=18.0):
    """
    Orthographic projection of spherical coordinates (theta, phi) on S^2:
    theta = polar angle from +z (north pole), phi = azimuth in xy-plane from +x (right) toward +y (front).
    Camera is tilted upward by `tilt_deg` so the equatorial circle is an ellipse of aspect sin(tilt_deg).
    """
    th = np.radians(theta_deg)
    ph = np.radians(phi_deg)
    tilt = np.radians(tilt_deg)

    # 3D unit vector n = (nx, ny, nz) where +x is right, +y is toward viewer, +z is up
    nx = np.sin(th) * np.cos(ph)
    ny = np.sin(th) * np.sin(ph)
    nz = np.cos(th)

    # Orthographic projection onto screen (x_2d, y_2d) with camera elevation `tilt`
    x_2d = R_sph * nx
    y_2d = R_sph * (nz * np.cos(tilt) - ny * np.sin(tilt))
    return x_2d, y_2d


def draw_celestial_sphere(ax, cx, cy, R_sph):
    """Draws the celestial sphere S^2 with equatorial circle and two meridians."""
    ax.imshow(CELESTIAL_RGBA, extent=[cx - R_sph, cx + R_sph, cy - R_sph, cy + R_sph],
              origin='lower', zorder=2)

    tilt_aspect = np.sin(np.radians(18.0))  # ~0.309

    # Back half of equator (dashed)
    ax.add_patch(Arc((cx, cy), 2.0 * R_sph, 2.0 * R_sph * tilt_aspect,
                     angle=0, theta1=0, theta2=180,
                     edgecolor='#64748b', linewidth=1.4, linestyle='--', alpha=0.65, zorder=3))
    # Front half of equator (dashed, slightly bolder)
    ax.add_patch(Arc((cx, cy), 2.0 * R_sph, 2.0 * R_sph * tilt_aspect,
                     angle=0, theta1=180, theta2=360,
                     edgecolor='#475569', linewidth=1.6, linestyle='--', alpha=0.85, zorder=4))

    # Faint vertical meridian ellipse for 3D spherical geometry
    ax.add_patch(Ellipse((cx, cy), 2.0 * R_sph * 0.42, 2.0 * R_sph,
                         facecolor='none', edgecolor='#94a3b8', linewidth=1.0, linestyle=':', alpha=0.55, zorder=3))

    # Outer sphere limb in muted blue
    ax.add_patch(Circle((cx, cy), R_sph, fill=False, edgecolor='#4b729f', linewidth=2.6, zorder=5))


def get_lambda_for_frame(frame_idx):
    """Map frame_idx in [0, 219] to lambda in [0.0, 5.0] with 200 motion frames + 20 hold frames."""
    if frame_idx >= N_MOTION_FRAMES - 1:
        return 5.0
    # Exact linear mapping across the 200 motion frames (0 .. 199) so frame 0 -> 0.0 and frame 199 -> 5.0
    u = frame_idx / float(N_MOTION_FRAMES - 1)
    return 5.0 * u


def render_frame(args):
    frame_idx, out_path = args
    lam = get_lambda_for_frame(frame_idx)

    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 13.0,
    })

    # Exact 2000 x 1200 px canvas at 140 DPI
    dpi = 140
    fig_w, fig_h = 2000.0 / dpi, 1200.0 / dpi
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Color Palette (Specification Section 7)
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#334155'
    MUTED_SLATE = '#64748b'
    BORDER_COLOR = '#cbd5e1'
    CARD_BG = '#f8fafc'

    BLUE_PND = '#3b6ea5'
    ORANGE_PND = '#d97706'
    GREEN_PND = '#3d8b6e'
    PURPLE_PND = '#7c5295'

    EXP_BLUE = '#3b6ea5'
    SHEAR_ORANGE = '#d97706'
    TWIST_GREEN = '#3d8b6e'
    SF_TEAL = '#0f766e'

    # Strict horizontal grid constants on master axes [0, 1] x [0, 1]
    X_LEFT = 0.018
    X_RIGHT = 0.982
    W_FULL = X_RIGHT - X_LEFT  # 0.964
    GAP_AB = 0.014
    W_HALF = (W_FULL - GAP_AB) * 0.5  # 0.475
    X_A = X_LEFT                      # 0.018 .. 0.493
    X_B = X_LEFT + W_HALF + GAP_AB    # 0.507 .. 0.982
    PAD_IN = 0.010

    def add_box(x, y, w, h, fc='#ffffff', ec=BORDER_COLOR, lw=1.4, r=0.008, z=1):
        box = FancyBboxPatch((x, y), w, h,
                             boxstyle=f"round,pad=0.0,rounding_size={r}",
                             facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z)
        ax.add_patch(box)
        return box

    # =========================================================================
    # 1. TOP HEADER BANNER (y in [0.928, 0.992], FULL WIDTH = 0.964)
    # =========================================================================
    add_box(X_LEFT, 0.928, W_FULL, 0.064, fc=CARD_BG, ec=BORDER_COLOR, lw=1.4, r=0.008, z=1)
    ax.text(0.50, 0.971, "FROM CURVATURE TO KERR'S SOLUTION",
            color=NAVY, fontsize=18.5, fontweight='bold', ha='center', va='center', zorder=2)
    ax.text(0.50, 0.943, "Principal null directions, algebraic speciality, and shear-free null congruences",
            color=SLATE, fontsize=13.8, fontweight='bold', ha='center', va='center', zorder=2)

    # =========================================================================
    # 2. UPPER SECTION: ALGEBRAIC CLASSIFICATION (y in [0.510, 0.920], FULL WIDTH = 0.964)
    # =========================================================================
    Y_UP_BOT = 0.510
    H_UP = 0.410  # 0.510 .. 0.920
    W_IN_FULL = W_FULL - 2.0 * PAD_IN  # 0.944 (x in [0.028, 0.972])
    add_box(X_LEFT, Y_UP_BOT, W_FULL, H_UP, fc='#ffffff', ec=BORDER_COLOR, lw=1.4, r=0.008, z=1)

    # 2a. Shared label bar above the two celestial spheres (x in [0.028, 0.972], width = 0.944)
    add_box(X_LEFT + PAD_IN, 0.876, W_IN_FULL, 0.036, fc='#eff6ff', ec='#93c5fd', lw=1.2, r=0.006, z=2)
    ax.text(0.50, 0.894,
            "Celestial sphere of null directions (" + r"$S^2$" + ")  —  Highlighted points represent principal null directions selected by the Weyl tensor.",
            color=NAVY, fontsize=12.0, fontweight='bold', ha='center', va='center', zorder=3)

    # 2b. Equal-sized enclosing subpanels for Panel A and Panel B inside Upper Section
    GAP_SUB_AB = 0.012
    W_PANEL_AB = (W_IN_FULL - GAP_SUB_AB) * 0.5  # 0.466
    X_PA = X_LEFT + PAD_IN                       # 0.028 .. 0.494
    X_PB = X_PA + W_PANEL_AB + GAP_SUB_AB        # 0.506 .. 0.972
    Y_PAB_BOT = 0.584
    H_PAB = 0.284  # 0.584 .. 0.868

    add_box(X_PA, Y_PAB_BOT, W_PANEL_AB, H_PAB, fc='#f8fafc', ec=BORDER_COLOR, lw=1.2, r=0.006, z=2)
    add_box(X_PB, Y_PAB_BOT, W_PANEL_AB, H_PAB, fc='#fffbeb', ec='#fde68a', lw=1.2, r=0.006, z=2)

    # Two-line Header Bars inside Panel A and Panel B (matching Lense–Thirring hierarchy)
    W_PAB_HDR = W_PANEL_AB - 0.016
    add_box(X_PA + 0.008, 0.804, W_PAB_HDR, 0.056, fc='#ffffff', ec=BORDER_COLOR, lw=1.1, r=0.005, z=3)
    ax.text(X_PA + W_PANEL_AB * 0.5, 0.844, "A  ·  Generic Weyl curvature",
            color=NAVY, fontsize=14.0, fontweight='bold', ha='center', va='center', zorder=4)
    ax.text(X_PA + W_PANEL_AB * 0.5, 0.818, "Four distinct principal null directions (PNDs)",
            color=SLATE, fontsize=12.0, fontweight='bold', ha='center', va='center', zorder=4)

    add_box(X_PB + 0.008, 0.804, W_PAB_HDR, 0.056, fc='#ffffff', ec='#fde68a', lw=1.1, r=0.005, z=3)
    ax.text(X_PB + W_PANEL_AB * 0.5, 0.844, "B  ·  Kerr curvature",
            color='#b45309', fontsize=14.0, fontweight='bold', ha='center', va='center', zorder=4)
    ax.text(X_PB + W_PANEL_AB * 0.5, 0.818, "Two repeated PNDs (2 + 2)",
            color=DARK_SLATE, fontsize=12.0, fontweight='bold', ha='center', va='center', zorder=4)

    # Celestial spheres on the left of Panel A and Panel B (compact margin so right math box has generous width)
    W_SPH_AX = 0.130
    H_SPH_AX = 0.204
    Y_SPH_AX = 0.592
    for is_b, x_panel in [(False, X_PA), (True, X_PB)]:
        ax_sph = fig.add_axes([x_panel + 0.004, Y_SPH_AX, W_SPH_AX, H_SPH_AX])
        ax_sph.set_xlim(-1.02, 1.02)
        ax_sph.set_ylim(-1.02, 1.02)
        ax_sph.set_aspect('equal')
        ax_sph.axis('off')
        ax_sph.patch.set_alpha(0.0)

        R_sph = 0.88
        draw_celestial_sphere(ax_sph, 0.0, 0.0, R_sph)

        lbl_bbox = dict(boxstyle='round,pad=0.05', facecolor='#f4f8fd', edgecolor='none', alpha=0.90)

        if not is_b:
            # Place the 4 distinct PND markers well inside the sphere limb and place labels inward
            pnds_a = [
                (-0.39,  0.40, ORANGE_PND, r"$z_1$", -0.17,  0.62),
                ( 0.41,  0.34, BLUE_PND,   r"$z_2$",  0.21,  0.57),
                (-0.37, -0.36, GREEN_PND,  r"$z_3$", -0.17, -0.59),
                ( 0.39, -0.40, PURPLE_PND, r"$z_4$",  0.19, -0.62),
            ]
            for px, py, col, lbl, lx, ly in pnds_a:
                ax_sph.add_patch(Circle((px, py), 0.122, facecolor=col, edgecolor='#1e293b', linewidth=1.5, zorder=8))
                ax_sph.text(lx, ly, lbl, fontsize=14.2, fontweight='bold', color=NAVY,
                            ha='center', va='center', bbox=lbl_bbox, zorder=10)
        else:
            # Place the 2 double roots and their labels well inside the sphere limb (r <= 0.64 < 0.88)
            double_pnds = [
                (-0.35,  0.34, ORANGE_PND, r"$z_1 = z_2$", -0.08,  0.61),
                ( 0.35, -0.34, BLUE_PND,   r"$z_3 = z_4$",  0.08, -0.61),
            ]
            for px, py, col, lbl, lx, ly in double_pnds:
                ax_sph.add_patch(Circle((px, py), 0.170, facecolor=col, edgecolor='#ffffff', linewidth=1.8, zorder=8))
                ax_sph.add_patch(Circle((px, py), 0.170, fill=False, edgecolor=NAVY, linewidth=1.3, zorder=9))
                ax_sph.text(px, py, "2", fontsize=13.5, fontweight='bold', color='#ffffff',
                            ha='center', va='center', zorder=10)
                ax_sph.text(lx, ly, lbl, fontsize=13.4, fontweight='bold', color=NAVY,
                            ha='center', va='center', bbox=lbl_bbox, zorder=10)

    # Right-side mathematical description boxes inside Panel A & Panel B (wider: width = 0.322, height = 0.204)
    X_RBOX_OFFSET = 0.136
    W_RBOX = W_PANEL_AB - X_RBOX_OFFSET - 0.008  # 0.322
    Y_RBOX = 0.592
    H_RBOX = 0.204

    add_box(X_PA + X_RBOX_OFFSET, Y_RBOX, W_RBOX, H_RBOX, fc='#ffffff', ec='#cbd5e1', lw=1.0, r=0.005, z=3)
    add_box(X_PB + X_RBOX_OFFSET, Y_RBOX, W_RBOX, H_RBOX, fc='#ffffff', ec='#fde68a', lw=1.0, r=0.005, z=3)

    # Panel A Right Box Content (Bullets strictly left-aligned vertically; generous side margins!)
    X_RA_MID = X_PA + X_RBOX_OFFSET + W_RBOX * 0.5
    X_RA_BULLET = X_PA + X_RBOX_OFFSET + 0.028
    ax.text(X_RA_BULLET, 0.770, "•  Four distinct PNDs",
            color=NAVY, fontsize=12.0, fontweight='bold', ha='left', va='center', zorder=4)
    ax.text(X_RA_BULLET, 0.735, "•  Four roots, each of multiplicity one",
            color=DARK_SLATE, fontsize=11.8, fontweight='bold', ha='left', va='center', zorder=4)
    ax.text(X_RA_MID, 0.691, r"Null condition: $g_{ab}k^a k^b = 0,\; k^{\hat{a}} = (1, \mathbf{n})$",
            color=DARK_SLATE, fontsize=12.8, fontweight='bold', ha='center', va='center', zorder=4)

    W_EQ_IN = W_RBOX - 0.016
    add_box(X_RA_MID - W_EQ_IN * 0.5, 0.601, W_EQ_IN, 0.060, fc='#f8fafc', ec=BORDER_COLOR, lw=1.1, r=0.005, z=4)
    ax.text(X_RA_MID, 0.631,
            r"$\Psi_0 + 4z\Psi_1 + 6z^2\Psi_2 + 4z^3\Psi_3 + z^4\Psi_4 = 0$",
            color=NAVY, fontsize=14.0, fontweight='bold', ha='center', va='center', zorder=5)

    # Panel B Right Box Content (Bullets strictly left-aligned vertically; generous side margins!)
    X_RB_MID = X_PB + X_RBOX_OFFSET + W_RBOX * 0.5
    X_RB_BULLET = X_PB + X_RBOX_OFFSET + 0.052
    ax.text(X_RB_BULLET, 0.770, "•  Two repeated PNDs",
            color='#b45309', fontsize=12.0, fontweight='bold', ha='left', va='center', zorder=4)
    ax.text(X_RB_BULLET, 0.735, "•  Two double roots (2 + 2)",
            color=DARK_SLATE, fontsize=12.0, fontweight='bold', ha='left', va='center', zorder=4)
    ax.text(X_RB_MID, 0.691, r"Coincident pairs: $z_1 = z_2 = z_+,\; z_3 = z_4 = z_-$",
            color=DARK_SLATE, fontsize=12.6, fontweight='bold', ha='center', va='center', zorder=4)

    add_box(X_RB_MID - W_EQ_IN * 0.5, 0.601, W_EQ_IN, 0.060, fc='#fffbeb', ec='#fde68a', lw=1.1, r=0.005, z=4)
    ax.text(X_RB_MID, 0.631,
            r"$P(z) \propto (z - z_+)^2 (z - z_-)^2$",
            color=NAVY, fontsize=15.0, fontweight='bold', ha='center', va='center', zorder=5)

    # 2c. Shared Full-Width S^2 <-> CP^1 Bar inside bottom of Upper Section (y in [0.518, 0.576], height = 0.058)
    add_box(X_LEFT + PAD_IN, 0.518, W_IN_FULL, 0.058, fc=CARD_BG, ec=BORDER_COLOR, lw=1.1, r=0.006, z=2)
    ax.text(0.50, 0.559,
            r"Celestial sphere $S^2$  $\longleftrightarrow$  complex projective line $\mathbb{CP}^1$  (complex parametrization of null directions)",
            color=NAVY, fontsize=12.8, fontweight='bold', ha='center', va='center', zorder=3)
    ax.text(0.50, 0.531,
            "Each root of the Weyl quartic identifies a principal null direction.",
            color=SLATE, fontsize=11.8, fontweight='bold', ha='center', va='center', zorder=3)

    # =========================================================================
    # 3. GOLDBERG–SACHS CONNECTION BRIDGE (y in [0.444, 0.502], FULL WIDTH = 0.964)
    # =========================================================================
    add_box(X_LEFT, 0.444, W_FULL, 0.058, fc='#f8fafc', ec='#94a3b8', lw=1.4, r=0.008, z=2)
    ax.text(0.50, 0.484,
            "Repeated principal null direction   " + r"$\Longleftrightarrow$" + "   Geodesic, shear-free null congruence",
            color=NAVY, fontsize=14.0, fontweight='bold', ha='center', va='center', zorder=3)
    ax.text(0.50, 0.457,
            "Goldberg–Sachs theorem  ·  Four-dimensional vacuum spacetime",
            color=SLATE, fontsize=11.8, fontweight='bold', ha='center', va='center', zorder=3)

    # =========================================================================
    # 4. LOWER SECTION: PANEL C — OPTICAL DEFORMATION (y in [0.008, 0.436], FULL WIDTH = 0.964)
    # =========================================================================
    Y_C_BOT = 0.008
    H_C = 0.428
    add_box(X_LEFT, Y_C_BOT, W_FULL, H_C, fc='#ffffff', ec=BORDER_COLOR, lw=1.4, r=0.008, z=1)

    # Spacious 2-Row Header inside Panel C (x in [0.028, 0.972], y in [0.324, 0.428], height = 0.104)
    W_C_IN = W_FULL - 2.0 * PAD_IN  # 0.944
    add_box(X_LEFT + PAD_IN, 0.324, W_C_IN, 0.104, fc=CARD_BG, ec=BORDER_COLOR, lw=1.2, r=0.006, z=2)

    # Row 1 of Panel C Header (y = 0.408): Title + Enlarged Evolution & Area-Rate Formula + Affine Parameter Badge
    ax.text(X_LEFT + PAD_IN + 0.012, 0.408, "C  ·  Goldberg–Sachs & optical deformation",
            color=NAVY, fontsize=13.6, fontweight='bold', ha='left', va='center', zorder=3)

    ax.text(0.410, 0.408, "Evolution:",
            color=SLATE, fontsize=13.0, fontweight='bold', ha='left', va='center', zorder=3)
    ax.text(0.492, 0.408,
            r"$\frac{d\boldsymbol{\xi}}{d\lambda} = B(\lambda)\boldsymbol{\xi}, \qquad \theta = \frac{1}{A}\frac{dA}{d\lambda}$",
            color=DARK_SLATE, fontsize=16.2, fontweight='bold', ha='left', va='center', zorder=4)

    ax.text(X_RIGHT - PAD_IN - 0.010, 0.408, f"Affine parameter:  λ = {lam:3.2f}",
            color=SF_TEAL, fontsize=12.4, fontweight='bold', ha='right', va='center',
            bbox=dict(boxstyle='round,pad=0.18', facecolor='#f0fdfa', edgecolor='#5eead4', lw=1.2),
            zorder=3)

    # Subtle separator line between Row 1 and Row 2 inside Panel C Header
    ax.plot([X_LEFT + PAD_IN + 0.012, X_RIGHT - PAD_IN - 0.012], [0.388, 0.388],
            color='#e2e8f0', linewidth=1.0, linestyle='-', zorder=3)

    # Row 2 of Panel C Header: Enlarged Term-by-Term Decomposition of B_AB with Curly Underbraces
    def draw_underbrace(x_c, hw, y_top, col):
        t = np.linspace(-1.0, 1.0, 61)
        xs = x_c + hw * t
        ys = y_top - 0.0026 * (1.0 - np.exp(-18.0 * (1.0 - np.abs(t)))) - 0.0026 * np.exp(-28.0 * t**2)
        ax.plot(xs, ys, color=col, linewidth=1.6, solid_capstyle='round', zorder=4)

    Y_EQ_TOP = 0.372
    Y_BRACE_TOP = 0.355
    Y_LBL_BOT = 0.336

    ax.text(0.285, Y_EQ_TOP, r"$B_{AB} \;=$",
            color=NAVY, fontsize=15.2, fontweight='bold', ha='right', va='center', zorder=4)

    # Term 1: Expansion (1/2 theta q_AB)
    X_T1 = 0.368
    ax.text(X_T1, Y_EQ_TOP, r"$\frac{1}{2}\theta\,q_{AB}$",
            color=EXP_BLUE, fontsize=15.8, fontweight='bold', ha='center', va='center', zorder=4)
    draw_underbrace(X_T1, 0.068, Y_BRACE_TOP, EXP_BLUE)
    ax.text(X_T1, Y_LBL_BOT, "Expansion (area change)",
            color=EXP_BLUE, fontsize=10.8, fontweight='bold', ha='center', va='center', zorder=4)

    ax.text(0.464, Y_EQ_TOP, r"$+$",
            color=DARK_SLATE, fontsize=15.0, fontweight='bold', ha='center', va='center', zorder=4)

    # Term 2: Shear (sigma_AB)
    X_T2 = 0.536
    ax.text(X_T2, Y_EQ_TOP, r"$\sigma_{AB}$",
            color='#b45309', fontsize=15.4, fontweight='bold', ha='center', va='center', zorder=4)
    draw_underbrace(X_T2, 0.052, Y_BRACE_TOP, '#b45309')
    ax.text(X_T2, Y_LBL_BOT, "Shear (shape)",
            color='#b45309', fontsize=10.8, fontweight='bold', ha='center', va='center', zorder=4)

    ax.text(0.612, Y_EQ_TOP, r"$+$",
            color=DARK_SLATE, fontsize=15.0, fontweight='bold', ha='center', va='center', zorder=4)

    # Term 3: Twist (omega_AB)
    X_T3 = 0.686
    ax.text(X_T3, Y_EQ_TOP, r"$\omega_{AB}$",
            color=TWIST_GREEN, fontsize=15.4, fontweight='bold', ha='center', va='center', zorder=4)
    draw_underbrace(X_T3, 0.056, Y_BRACE_TOP, TWIST_GREEN)
    ax.text(X_T3, Y_LBL_BOT, "Twist (rotation)",
            color=TWIST_GREEN, fontsize=10.8, fontweight='bold', ha='center', va='center', zorder=4)

    # Precompute smooth initial boundary circle (N = 240 points)
    N_pts = 240
    angles_smooth = np.linspace(0.0, 2.0 * np.pi, N_pts, endpoint=True)
    xi0_smooth = R0 * np.vstack([np.cos(angles_smooth), np.sin(angles_smooth)])

    # Four subpanels inside Panel C spanning [0.028, 0.972] (width = 0.944):
    # give C4 slightly more width so its subtitle fits comfortably at 11.2 pt (matching C1–C3).
    GAP_SUB = 0.012
    W_SUB_123 = 0.217
    W_SUB_C4 = W_C_IN - 3.0 * GAP_SUB - 3.0 * W_SUB_123  # 0.257
    sub_widths = [W_SUB_123, W_SUB_123, W_SUB_123, W_SUB_C4]
    Y_SUB_BOT = 0.080
    H_SUB = 0.234  # y in [0.080, 0.314] (gap to top header = 0.010, gap to bottom green bar = 0.016)

    sub_specs = [
        ("expansion",  0, r"C1 · Expansion ($\theta$)",         "Expansion (area change)",
         r"$\theta \neq 0 \;\; (\sigma_{AB}=\omega_{AB}=0)$", EXP_BLUE, 6, False),
        ("shear",      1, r"C2 · Shear ($\sigma$)",             "Shear (shape)",
         r"$\sigma_{AB}\neq 0 \;\; (\theta=\omega_{AB}=0)$", SHEAR_ORANGE, 6, False),
        ("twist",      2, r"C3 · Twist ($\omega$)",             "Twist (rotation)",
         r"$\omega_{AB}\neq 0 \;\; (\theta=\sigma_{AB}=0)$", TWIST_GREEN, 6, True),
        ("shear_free", 3, r"C4 · Kerr-like ($\sigma_{AB}=0$)",  "Kerr-like: expansion + twist, no shear",
         r"$\theta \neq 0,\;\; \omega_{AB}\neq 0$", SF_TEAL, 8, True),
    ]

    for mode, idx_sub, stitle, ssub, seq, scol, n_markers, show_radial in sub_specs:
        sx = X_LEFT + PAD_IN + sum(sub_widths[:idx_sub]) + idx_sub * GAP_SUB
        cur_w = sub_widths[idx_sub]
        cx_sub = sx + cur_w * 0.5
        is_c4 = (mode == "shear_free")
        sub_bg = '#f0fdfa' if is_c4 else '#f8fafc'
        sub_bdr = '#2dd4bf' if is_c4 else '#cbd5e1'
        add_box(sx, Y_SUB_BOT, cur_w, H_SUB, fc=sub_bg, ec=sub_bdr, lw=1.8 if is_c4 else 1.1, r=0.006, z=2)

        ax.text(cx_sub, Y_SUB_BOT + H_SUB - 0.019, stitle,
                color=scol if not (mode == "shear") else '#b45309',
                fontsize=13.2, fontweight='bold', ha='center', va='center', zorder=3)

        # Dedicated equal-aspect axes for the transverse screen
        ax_s = fig.add_axes([sx + 0.008, Y_SUB_BOT + 0.066, cur_w - 0.016, H_SUB - 0.092])
        lim = 2.08
        ax_s.set_xlim(-lim, lim)
        ax_s.set_ylim(-lim, lim)
        ax_s.set_aspect('equal')
        ax_s.axis('off')
        ax_s.patch.set_alpha(0.0)

        # Faint crosshair axes for transverse screen e_1, e_2
        ax_s.plot([-1.85, 1.85], [0, 0], color='#cbd5e1', linewidth=1.0, linestyle=':', zorder=1)
        ax_s.plot([0, 0], [-1.85, 1.85], color='#cbd5e1', linewidth=1.0, linestyle=':', zorder=1)

        # Initial circular cross-section (light gray, dashed)
        ax_s.plot(xi0_smooth[0], xi0_smooth[1], color='#94a3b8', linewidth=1.9, linestyle='--', zorder=2)

        # Evolving boundary xi(lambda) = exp(B * lambda) xi(0)
        M_lam = deformation_matrix(mode, lam)
        xi_lam = M_lam @ xi0_smooth
        ax_s.plot(xi_lam[0], xi_lam[1], color=scol, linewidth=3.6, zorder=5)

        # Marker points (6 for C1-C3, 8 for C4)
        m_angles = np.linspace(0.0, 2.0 * np.pi, n_markers, endpoint=False) + np.radians(25.0)
        xi0_markers = R0 * np.vstack([np.cos(m_angles), np.sin(m_angles)])
        xi_markers = M_lam @ xi0_markers

        if show_radial:
            ax_s.plot([0.0, xi0_markers[0, 0]], [0.0, xi0_markers[1, 0]],
                      color='#94a3b8', linewidth=1.7, linestyle='--', zorder=3)
            ax_s.plot([0.0, xi_markers[0, 0]], [0.0, xi_markers[1, 0]],
                      color=scol, linewidth=2.8, linestyle='-', zorder=4)

        for k in range(n_markers):
            is_ref = (show_radial and k == 0)
            m_col = '#f59e0b' if is_ref else scol
            m_rad = 0.120 if is_ref else 0.092
            ax_s.add_patch(Circle((xi_markers[0, k], xi_markers[1, k]), m_rad,
                                  facecolor=m_col, edgecolor='#ffffff', linewidth=1.3, zorder=6))

        # Labels below each transverse diagram with consistent 11.2 pt subtitle size
        ax.text(cx_sub, Y_SUB_BOT + 0.049, ssub, color=DARK_SLATE,
                fontsize=11.2, fontweight='bold', ha='center', va='center', zorder=3)
        if is_c4:
            ax.text(cx_sub - 0.035, Y_SUB_BOT + 0.019, r"$\theta \neq 0,\;\; \omega_{AB}\neq 0,$",
                    color=DARK_SLATE, fontsize=13.2, fontweight='bold', ha='center', va='center', zorder=4)
            ax.text(cx_sub + 0.052, Y_SUB_BOT + 0.019, r"$\boldsymbol{\sigma_{AB} = 0}$",
                    color=SF_TEAL, fontsize=13.8, fontweight='bold', ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.11', facecolor='#ffffff', edgecolor='#0f766e', linewidth=1.6),
                    zorder=4)
        else:
            eq_col = '#b45309' if (mode == "shear") else (EXP_BLUE if mode == "expansion" else TWIST_GREEN)
            ax.text(cx_sub, Y_SUB_BOT + 0.019, seq, color=eq_col, fontsize=13.4,
                    fontweight='bold', ha='center', va='center', zorder=3)

    # Bottom summary banner inside Panel C (x in [0.028, 0.972], y in [0.014, 0.064], height = 0.050, gap above = 0.016)
    add_box(X_LEFT + PAD_IN, 0.014, W_C_IN, 0.050, fc='#f0fdfa', ec='#2dd4bf', lw=1.4, r=0.006, z=2)
    ax.text(0.335, 0.039,
            "Shear-free congruence: expansion and twist without shape distortion",
            color=NAVY, fontsize=13.2, fontweight='bold', ha='center', va='center', zorder=3)
    ax.text(0.765, 0.039,
            r"$\boldsymbol{\sigma_{AB} = 0}, \qquad \theta \neq 0, \qquad \omega_{AB} \neq 0$",
            color=SF_TEAL, fontsize=14.8, fontweight='bold', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.16', facecolor='#ffffff', edgecolor='#0f766e', linewidth=1.5),
            zorder=4)

    fig.savefig(out_path, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    return frame_idx


def main():
    validate_optical_models()
    print("[OK] Validated singular values for all 4 optical deformation models (expansion, shear, twist, shear-free).")

    PNG_OUT.parent.mkdir(parents=True, exist_ok=True)

    if "--test-static" in sys.argv:
        render_frame((N_MOTION_FRAMES - 1, str(PNG_OUT)))
        print(f"[OK] Rendered static validation frame at lambda=5: {PNG_OUT}")
        return

    frames_dir = tempfile.mkdtemp(prefix="curvature_kerr_anim_")
    try:
        t0 = time.time()
        n_workers = max(1, min(14, multiprocessing.cpu_count() - 1))
        print(f"[INFO] Rendering {N_TOTAL_FRAMES} frames (2000x1200 @ {FPS} fps) using {n_workers} workers...")

        tasks = [(i, os.path.join(frames_dir, f"frame_{i:04d}.png")) for i in range(N_TOTAL_FRAMES)]
        with multiprocessing.Pool(processes=n_workers) as pool:
            for done_idx in pool.imap_unordered(render_frame, tasks, chunksize=4):
                if (done_idx + 1) % 40 == 0 or done_idx == N_TOTAL_FRAMES - 1:
                    print(f"  Rendered frame {done_idx + 1:3d} / {N_TOTAL_FRAMES}")

        dt = time.time() - t0
        print(f"[OK] Rendered {N_TOTAL_FRAMES} frames in {dt:.1f} s ({dt / N_TOTAL_FRAMES:.3f} s/frame)")

        # Save final hold frame (lambda = 5.0) as static poster PNG
        shutil.copy2(os.path.join(frames_dir, f"frame_{N_MOTION_FRAMES - 1:04d}.png"), PNG_OUT)
        print(f"[OK] Saved static poster PNG: {PNG_OUT}")

        # 1. Master MP4 at full 2000 x 1200 resolution @ 20 fps
        cmd_mp4 = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", os.path.join(frames_dir, "frame_%04d.png"),
            "-c:v", "libx264",
            "-profile:v", "high",
            "-crf", "18",
            "-preset", "slow",
            "-pix_fmt", "yuv420p",
            str(MP4_OUT),
        ]
        subprocess.run(cmd_mp4, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        mp4_mb = MP4_OUT.stat().st_size / (1024 * 1024)
        print(f"[OK] Generated Master MP4: {MP4_OUT} ({mp4_mb:.2f} MB)")

        # 2. Optimized GIF for Medium (1500 x 900 px @ 20 fps, high-contrast 224-color palette)
        cmd_gif = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", os.path.join(frames_dir, "frame_%04d.png"),
            "-vf", "fps=20,scale=1500:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=224:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4",
            "-loop", "0",
            str(GIF_OUT),
        ]
        subprocess.run(cmd_gif, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        gif_mb = GIF_OUT.stat().st_size / (1024 * 1024)
        print(f"[OK] Generated Optimized GIF: {GIF_OUT} ({gif_mb:.2f} MB)")



    finally:
        shutil.rmtree(frames_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
