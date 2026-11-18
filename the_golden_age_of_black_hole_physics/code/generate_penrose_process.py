#!/usr/bin/env python3
r"""
Generate scientific illustration & animation:
"THE PENROSE PROCESS: EXTRACTING ROTATIONAL ENERGY FROM A KERR BLACK HOLE"
"Equatorial geodesic splitting inside the ergosphere (a/m = 0.8) with four-momentum conservation"

Companion Figure & Animation for Section "The Penrose Process: Extracting Rotational Energy" of:
"The Golden Age of Black Hole Physics (1963–1974)"

Visual & Scientific Specifications:
- Unified light scientific-illustration visual identity (1800 x 900 px @ 140 DPI,
  white background #FFFFFF, light grey panels #F5F7FA, thin blue-grey borders #CBD5E1,
  dark navy typography #172136).
- Top-down view of the equatorial plane (\theta = \pi/2, Q = 0) of a rotating Kerr
  black hole with spin parameter a/m = 0.8:
    * Event horizon: r_+ = m + \sqrt{m^2 - a^2} = 1.6m
    * Outer boundary of the ergosphere (equatorial static limit): r_e(\pi/2) = 2.0m
    * Horizon angular velocity: \Omega_H = a / (2m r_+) = 0.25 / m (counterclockwise)
- Numerical Kerr geodesics integrated from the equatorial Kerr geodesic equations
  with an exact four-momentum-conserving two-body splitting event inside the ergosphere
  (p_0^\mu = p_1^\mu + p_2^\mu at r_0 = 1.88m \in (r_+, r_e)):
    * Incoming particle (0, Blue #2355D5): E_0 > 0, L_{z,0} > 0, enters the ergosphere
      from outside and reaches the splitting vertex at r_0 = 1.88m.
    * Captured fragment (1, Orange #D97706): future-directed with positive local ZAMO
      energy (E_{loc,1} > 0), negative conserved energy relative to infinity (E_1 < 0),
      and negative axial angular momentum (L_{z,1} < 0); satisfies the horizon-crossing
      condition E_1 - \Omega_H L_{z,1} > 0 and plunges across r_+ = 1.6m while frame
      dragging forces its coordinate angular motion forward (\dot{\phi} > 0).
    * Escaping fragment (2, Turquoise #0D9488): future-directed with E_{loc,2} > 0 and
      amplified conserved energy E_2 = E_0 - E_1 > E_0, escaping outside the ergosphere.
- Continuous 11-second four-stage animation (220 frames @ 20 fps):
    1. Approach (E_0 > 0)
    2. Splitting inside the ergosphere (p_0^\mu = p_1^\mu + p_2^\mu)
    3. Energy extraction (E_1 < 0 captured across r_+, E_2 > E_0 escaping)
    4. Conclusion (trajectories and energy balance E_0 = E_1 + E_2 held visible to read)
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
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch

SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_IMAGES_DIR = SCRIPT_DIR.parent / "images"

STATIC_OUT = LOCAL_IMAGES_DIR / "penrose_process.png"
GIF_OUT = LOCAL_IMAGES_DIR / "penrose_process_animation.gif"
MP4_OUT = LOCAL_IMAGES_DIR / "penrose_process_animation.mp4"

# Canvas & Animation Settings
CANVAS_W = 1800
CANVAS_H = 900
DPI = 140
FPS = 20
N_FRAMES = 260  # 13.0 seconds @ 20 fps (includes 5.0 s hold on final energy-balance stage)

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
MUTED_SLATE = '#475569'

# Consistently Colored Trajectories (per specification)
# 0. Incoming — Blue
BLUE_MAIN = '#2355d5'
BLUE_DARK = '#1e3a8a'
BLUE_BG = '#eff6ff'
BLUE_BORDER = '#93c5fd'

# 1. Captured — Orange
ORANGE_MAIN = '#d97706'
ORANGE_DARK = '#b45309'
ORANGE_BG = '#fffbeb'
ORANGE_BORDER = '#fcd34d'

# 2. Escaping — Turquoise
TURQ_MAIN = '#0d9488'
TURQ_DARK = '#115e59'
TURQ_BG = '#f0fdfa'
TURQ_BORDER = '#5eead4'

# Ergosphere & Horizon Styling
ERGO_FILL = '#fef3c7'
ERGO_EDGE = '#d97706'
SPLIT_GOLD = '#f59e0b'

# Auxiliary radial coordinate stretch outside r_+ = 1.6m so the ergosphere [1.6m, 2.0m]
# and radial separation of the exact Kerr-Schild geodesics are visually distinct:
R_PLUS_VAL = 1.60
GAMMA_RAD = 3.40


def r_to_aux(r):
    """Map Boyer-Lindquist / Kerr-Schild radial coordinate r/m to auxiliary display radius."""
    return R_PLUS_VAL + GAMMA_RAD * (r - R_PLUS_VAL)


def compute_bh_disk_rgba(radius=1.6, res=260):
    """Precompute a softly shaded 3D dark charcoal-slate sphere RGBA texture for top-down horizon."""
    x_s = np.linspace(-radius, radius, res)
    y_s = np.linspace(-radius, radius, res)
    X_s, Y_s = np.meshgrid(x_s, y_s)
    R2_s = (X_s / radius) ** 2 + (Y_s / radius) ** 2
    mask_s = R2_s <= 1.0

    Z_s = np.zeros_like(X_s)
    Z_s[mask_s] = np.sqrt(1.0 - R2_s[mask_s])

    L = np.array([-0.35, 0.42, 0.84])
    L = L / np.linalg.norm(L)

    Nx = np.zeros_like(X_s)
    Ny = np.zeros_like(Y_s)
    Nz = np.zeros_like(Z_s)
    Nx[mask_s] = X_s[mask_s] / radius
    Ny[mask_s] = Y_s[mask_s] / radius
    Nz[mask_s] = Z_s[mask_s]

    diff = np.clip(Nx * L[0] + Ny * L[1] + Nz * L[2], 0.0, 1.0)
    H = L + np.array([0.0, 0.0, 1.0])
    H = H / np.linalg.norm(H)
    spec = np.clip(Nx * H[0] + Ny * H[1] + Nz * H[2], 0.0, 1.0) ** 28

    base_r, base_g, base_b = 0.09, 0.13, 0.21
    hl_r, hl_g, hl_b = 0.27, 0.34, 0.46

    rgba = np.zeros((res, res, 4), dtype=float)
    rgba[..., 0] = np.clip(base_r + 0.50 * diff * (hl_r - base_r) + 0.16 * spec, 0.0, 1.0)
    rgba[..., 1] = np.clip(base_g + 0.50 * diff * (hl_g - base_g) + 0.16 * spec, 0.0, 1.0)
    rgba[..., 2] = np.clip(base_b + 0.50 * diff * (hl_b - base_b) + 0.18 * spec, 0.0, 1.0)
    rgba[..., 3] = np.where(mask_s, 1.0, 0.0)
    return rgba


BH_DISK_RGBA = compute_bh_disk_rgba(1.6, res=260)


def precompute_penrose_geodesics():
    """
    Construct an exact four-momentum-conserving two-body splitting event in the ZAMO
    orthonormal tetrad at r_0 = 1.88m inside the equatorial ergosphere of a Kerr
    black hole with a/m = 0.8, and integrate the three equatorial Kerr geodesics.
    """
    m = 1.0
    a = 0.8
    r_plus = m + np.sqrt(m ** 2 - a ** 2)  # 1.6m
    r_erg = 2.0 * m                        # 2.0m
    Omega_H = a / (2.0 * m * r_plus)       # 0.25 / m

    # Splitting vertex inside the ergosphere (r_+ = 1.60m < r_0 = 1.88m < r_e = 2.00m)
    r0 = 1.88
    phi0 = -0.35  # radians (~ -20.1 deg, lower-right quadrant of ergosphere)

    Delta0 = r0 ** 2 - 2.0 * m * r0 + a ** 2
    A0 = (r0 ** 2 + a ** 2) ** 2 - a ** 2 * Delta0
    alpha0 = np.sqrt(Delta0 * r0 ** 2 / A0)  # ZAMO lapse
    omega0 = 2.0 * m * a * r0 / A0           # Frame-dragging angular velocity
    varpi0 = np.sqrt(A0 / r0 ** 2)           # Circumferential radius

    # ZAMO 2-velocities at the splitting event:
    # Exact four-momentum conservation p_0^\mu = p_1^\mu + p_2^\mu holds identically when
    # E_{loc,1} = f_1 E_{loc,0}, E_{loc,2} = (1 - f_1) E_{loc,0}, and v_0 = f_1 v_1 + (1 - f_1) v_2.
    v1 = np.array([-0.46, -0.885])     # Retrograde in ZAMO frame (v_1^{(\phi)} < -\alpha_0/(\omega_0\varpi_0)) -> E_1 < 0
    v2 = np.array([+0.010, +0.9994])   # Prograde escaping fragment -> E_2 > E_0
    f1 = 0.028
    v0 = f1 * v1 + (1.0 - f1) * v2     # Incoming particle (v_0^{(r)} < 0, v_0^{(\phi)} > 0)

    def zamo_to_conserved(Eloc, vr, vp):
        v_sq = vr ** 2 + vp ** 2
        mu = Eloc * np.sqrt(1.0 - v_sq)
        E = Eloc * (alpha0 + omega0 * varpi0 * vp)
        Lz = Eloc * varpi0 * vp
        rdot0 = np.sqrt(Delta0 / r0 ** 2) * Eloc * vr  # dr/d\lambda at r_0
        return mu, E, Lz, rdot0

    # Normalize so conserved energy of incoming particle is E_0 = 1.0
    _, E0_raw, _, _ = zamo_to_conserved(1.0, v0[0], v0[1])
    Eloc0 = 1.0 / E0_raw
    Eloc1 = f1 * Eloc0
    Eloc2 = (1.0 - f1) * Eloc0

    mu0, E0, Lz0, rdot0 = zamo_to_conserved(Eloc0, v0[0], v0[1])
    mu1, E1, Lz1, rdot1 = zamo_to_conserved(Eloc1, v1[0], v1[1])
    mu2, E2, Lz2, rdot2 = zamo_to_conserved(Eloc2, v2[0], v2[1])

    # Verify all physical constraints
    assert abs((E1 + E2) - E0) < 1e-14, "Conserved energy not conserved"
    assert abs((Lz1 + Lz2) - Lz0) < 1e-14, "Angular momentum not conserved"
    assert abs((rdot1 + rdot2) - rdot0) < 1e-14, "Radial momentum not conserved"
    assert mu0 > 0 and mu1 > 0 and mu2 > 0, "Mass-shell violated"
    assert Eloc0 > 0 and Eloc1 > 0 and Eloc2 > 0, "Future-directed condition violated"
    assert E1 < 0 and Lz1 < 0, "Captured fragment must have E_1 < 0 and L_{z,1} < 0"
    assert E2 > E0, "Escaping fragment must have E_2 > E_0"
    assert (E1 - Omega_H * Lz1) > 0, "Horizon-crossing inequality violated"

    def R_pot(r, mu, E, Lz):
        Delta = r ** 2 - 2.0 * m * r + a ** 2
        P = E * (r ** 2 + a ** 2) - a * Lz
        return P ** 2 - Delta * (mu ** 2 * r ** 2 + (Lz - a * E) ** 2)

    # Integrate exact equatorial Kerr geodesics in horizon-regular ingoing Kerr-Schild
    # coordinates (r, \tilde{\phi}), where d\tilde{\phi} = d\phi + (a/\Delta) dr.
    # For ingoing segments (dr/d\lambda = -\sqrt{R}), the \Delta denominator cancels identically:
    #   d\tilde{\phi}/dr = -[ a*(\mu^2 r^2 + (L_z - aE)^2)/(P + \sqrt{R}) + (L_z - aE) ] / \sqrt{R}.

    # 1. Incoming trajectory (0) backward from r_0 = 1.88m to r_init = 2.04m (outside r_e = 2.0m)
    r_in = np.linspace(r0, 2.04, 600)
    P_in = E0 * (r_in ** 2 + a ** 2) - a * Lz0
    R_in = R_pot(r_in, mu0, E0, Lz0)
    dphi0_dr = -(a * (mu0 ** 2 * r_in ** 2 + (Lz0 - a * E0) ** 2) / (P_in + np.sqrt(R_in)) + (Lz0 - a * E0)) / np.sqrt(R_in)
    phi_in = np.zeros_like(r_in)
    for i in range(1, len(r_in)):
        phi_in[i] = phi_in[i - 1] + 0.5 * (dphi0_dr[i - 1] + dphi0_dr[i]) * (r_in[i] - r_in[i - 1])
    phi_in_ks = phi0 + phi_in
    r0_arr = r_in[::-1]
    phi0_arr = phi_in_ks[::-1]

    # 2. Escaping trajectory (2) forward from r_0 = 1.88m to r_out = 2.04m (outside r_e = 2.0m)
    r2_arr = np.linspace(r0, 2.04, 600)
    D2 = r2_arr ** 2 - 2.0 * m * r2_arr + a ** 2
    P2 = E2 * (r2_arr ** 2 + a ** 2) - a * Lz2
    R2 = R_pot(r2_arr, mu2, E2, Lz2)
    dphi2_dr = (a * P2 / D2 + (Lz2 - a * E2)) / np.sqrt(R2) + a / D2
    phi2_raw = np.zeros_like(r2_arr)
    for i in range(1, len(r2_arr)):
        phi2_raw[i] = phi2_raw[i - 1] + 0.5 * (dphi2_dr[i - 1] + dphi2_dr[i]) * (r2_arr[i] - r2_arr[i - 1])
    phi2_arr = phi0 + phi2_raw

    # 3. Captured trajectory (1) forward from r_0 = 1.88m across r_+ = 1.60m down to r_end = 1.48m
    #    in exact ingoing Kerr-Schild coordinates (regular across r_+ = 1.60m, no smoothing!)
    r1_arr = np.linspace(r0, 1.48, 600)
    P1 = E1 * (r1_arr ** 2 + a ** 2) - a * Lz1
    R1 = R_pot(r1_arr, mu1, E1, Lz1)
    dphi1_dr = -(a * (mu1 ** 2 * r1_arr ** 2 + (Lz1 - a * E1) ** 2) / (P1 + np.sqrt(R1)) + (Lz1 - a * E1)) / np.sqrt(R1)
    phi1_raw = np.zeros_like(r1_arr)
    for i in range(1, len(r1_arr)):
        phi1_raw[i] = phi1_raw[i - 1] + 0.5 * (dphi1_dr[i - 1] + dphi1_dr[i]) * (r1_arr[i] - r1_arr[i - 1])
    phi1_arr = phi0 + phi1_raw

    # Map to auxiliary spatial coordinates (x_aux, y_aux) = (r_to_aux(r) cos\phi, r_to_aux(r) sin\phi)
    # and resample uniformly by arc length for smooth animation markers
    def resample_by_arclength(r_c, phi_c, n_pts=400):
        r_vis = r_to_aux(r_c)
        x_c = r_vis * np.cos(phi_c)
        y_c = r_vis * np.sin(phi_c)
        ds = np.hypot(np.diff(x_c), np.diff(y_c))
        s = np.concatenate([[0.0], np.cumsum(ds)])
        s_u = np.linspace(0.0, s[-1], n_pts)
        x_u = np.interp(s_u, s, x_c)
        y_u = np.interp(s_u, s, y_c)
        r_u = np.interp(s_u, s, r_c)
        phi_u = np.interp(s_u, s, phi_c)
        return x_u, y_u, r_u, phi_u

    x0, y0, r0_u, phi0_u = resample_by_arclength(r0_arr, phi0_arr, 400)
    x1, y1, r1_u, phi1_u = resample_by_arclength(r1_arr, phi1_arr, 400)
    x2, y2, r2_u, phi2_u = resample_by_arclength(r2_arr, phi2_arr, 400)

    r0_vis = r_to_aux(r0)
    return {
        'm': m, 'a': a, 'r_plus': r_plus, 'r_erg': r_erg, 'Omega_H': Omega_H,
        'r0': r0, 'phi0': phi0,
        'x_split': r0_vis * np.cos(phi0), 'y_split': r0_vis * np.sin(phi0),
        'E0': E0, 'E1': E1, 'E2': E2,
        'Lz0': Lz0, 'Lz1': Lz1, 'Lz2': Lz2,
        'Eloc0': Eloc0, 'Eloc1': Eloc1, 'Eloc2': Eloc2,
        'mu0': mu0, 'mu1': mu1, 'mu2': mu2,
        'horizon_ineq': E1 - Omega_H * Lz1,
        'traj0': (x0, y0, r0_u, phi0_u),
        'traj1': (x1, y1, r1_u, phi1_u),
        'traj2': (x2, y2, r2_u, phi2_u),
    }


def get_stage_state(frame_idx, n_frames=N_FRAMES, is_static=False):
    """
    Map frame index to the four-stage continuous animation timeline:
      Stage 1 (Approach, frames 0..59):     p_in in [0, 1], split=0, p_out=0, concl=0
      Stage 2 (Splitting, frames 60..89):   p_in = 1, split in [0, 1], p_out=0, concl=0
      Stage 3 (Extraction, frames 90..159): p_in = 1, split = 1, p_out in [0, 1], concl=0
      Stage 4 (Conclusion, frames 160..219): p_in = 1, split = 1, p_out = 1, concl in [0, 1]
    """
    if is_static:
        return 4, 1.0, 1.0, 1.0, 1.0

    if frame_idx < 60:
        u = frame_idx / 59.0
        p_in = 0.5 - 0.5 * np.cos(np.pi * u)
        return 1, p_in, 0.0, 0.0, 0.0
    elif frame_idx < 90:
        u = (frame_idx - 60) / 29.0
        return 2, 1.0, u, 0.0, 0.0
    elif frame_idx < 160:
        u = (frame_idx - 90) / 69.0
        p_out = 0.5 - 0.5 * np.cos(np.pi * u)
        return 3, 1.0, 1.0, p_out, 0.0
    else:
        u = min(1.0, (frame_idx - 160) / 25.0)
        return 4, 1.0, 1.0, 1.0, u


def draw_frame(data, frame_idx, output_path, is_static=False):
    """Render a single two-panel frame (or static figure) of the Penrose process."""
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 13.0,
    })

    stage, p_in, p_split, p_out, p_concl = get_stage_state(frame_idx, N_FRAMES, is_static=is_static)

    fig_w, fig_h = CANVAS_W / float(DPI), CANVAS_H / float(DPI)
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=DPI, facecolor=BG_WHITE)

    ax_root = fig.add_axes([0, 0, 1, 1])
    ax_root.set_xlim(0, 1)
    ax_root.set_ylim(0, 1)
    ax_root.axis('off')

    # 1. Top Header Banner
    title_box = FancyBboxPatch((0.020, 0.875), 0.960, 0.105,
                               boxstyle="round,pad=0.002,rounding_size=0.008",
                               facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_root.add_patch(title_box)
    ax_root.text(0.50, 0.948, "THE PENROSE PROCESS: EXTRACTING ROTATIONAL ENERGY",
                 color=NAVY, fontsize=17.8, fontweight='bold', ha='center', va='center')
    ax_root.text(0.50, 0.898,
                 "Particle splitting and rotational energy extraction in Kerr spacetime",
                 color=SLATE, fontsize=13.2, fontweight='bold', ha='center', va='center')

    # 2. Two Equal Panel Subplots
    p_w = 0.472
    p_h = 0.835
    p_y = 0.020

    ax_a = fig.add_axes([0.020, p_y, p_w, p_h])
    ax_b = fig.add_axes([0.508, p_y, p_w, p_h])

    for p_ax, p_letter, p_title, p_sub, is_right in [
        (ax_a, "A", r"Equatorial Kerr Plane  ($a/m = 0.8,\ \theta = \pi/2$)",
         r"Event horizon $r_+ = 1.6m$ and ergosurface $r_{\mathrm{e}}(\pi/2) = 2.0m$", False),
        (ax_b, "B", "The Penrose Process",
         "Staged mechanism and energy balance", True)
    ]:
        p_ax.set_xlim(-4.9, 4.9)
        p_ax.set_ylim(-4.3, 4.3)
        p_ax.set_aspect('equal')
        p_ax.axis('off')

        card = FancyBboxPatch((-4.75, -4.15), 9.5, 8.3,
                              boxstyle="round,pad=0.02,rounding_size=0.15",
                              facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=0)
        p_ax.add_patch(card)

        viewport = FancyBboxPatch((-4.52, -3.95), 9.04, 6.95,
                                  boxstyle="round,pad=0.02,rounding_size=0.10",
                                  facecolor=BG_WHITE, edgecolor='#e2e8f0', linewidth=1.0, zorder=0.5)
        p_ax.add_patch(viewport)

        hdr_box = FancyBboxPatch((-4.52, 3.15), 9.04, 0.96,
                                 boxstyle="round,pad=0.02,rounding_size=0.08",
                                 facecolor=BG_WHITE if not is_right else ORANGE_BG,
                                 edgecolor=BORDER_COLOR if not is_right else ORANGE_BORDER,
                                 linewidth=1.2, zorder=1)
        p_ax.add_patch(hdr_box)

        p_ax.text(0.0, 3.84, f"{p_letter}  ·  {p_title}",
                  color=NAVY if not is_right else ORANGE_DARK,
                  fontsize=14.8, fontweight='bold', ha='center', va='center', zorder=2)
        p_ax.text(0.0, 3.38, p_sub,
                  color=SLATE if not is_right else DARK_SLATE,
                  fontsize=11.6, fontweight='bold', ha='center', va='center', zorder=2)

    # =========================================================================
    # PANEL A: Top-Down Equatorial Kerr Geometry & Geodesic Trajectories
    # =========================================================================
    cx, cy = -0.05, -0.45
    S = 0.92  # Scale in Panel A coordinates

    # Background polar coordinate grid rings & crosshair guides
    phi_full = np.linspace(0, 2.0 * np.pi, 240)
    for r_phys, ls_g, al_g in [(2.06, ':', 0.38), (2.12, '--', 0.30)]:
        r_g = r_to_aux(r_phys)
        ax_a.plot(cx + S * r_g * np.cos(phi_full), cy + S * r_g * np.sin(phi_full),
                  color=GUIDE_COLOR, lw=0.9, ls=ls_g, alpha=al_g, zorder=1.0)

    r_cross = S * r_to_aux(2.14)
    ax_a.plot([cx - r_cross, cx + r_cross], [cy, cy],
              color=GUIDE_COLOR, lw=0.85, ls=':', alpha=0.45, zorder=1.0)
    ax_a.plot([cx, cx], [cy - r_cross, cy + r_cross],
              color=GUIDE_COLOR, lw=0.85, ls=':', alpha=0.45, zorder=1.0)

    # Outer boundary of the ergosphere: r_e(\pi/2) = 2.0m
    R_erg_vis = S * r_to_aux(data['r_erg'])
    ergo_patch = Circle((cx, cy), R_erg_vis,
                        facecolor=ERGO_FILL, edgecolor=ERGO_EDGE,
                        linestyle=(0, (5.5, 3.2)), linewidth=2.0, alpha=0.68, zorder=2.0)
    ax_a.add_patch(ergo_patch)

    # Subtle frame-dragging circulation arrows inside the ergosphere
    for ang_deg in [55.0, 145.0, 225.0]:
        r_fd = S * r_to_aux(1.78)
        a1 = np.deg2rad(ang_deg - 12.0)
        a2 = np.deg2rad(ang_deg + 12.0)
        arc_fd = FancyArrowPatch((cx + r_fd * np.cos(a1), cy + r_fd * np.sin(a1)),
                                 (cx + r_fd * np.cos(a2), cy + r_fd * np.sin(a2)),
                                 connectionstyle="arc3,rad=0.18",
                                 arrowstyle='-|>', mutation_scale=10,
                                 color='#d97706', alpha=0.45, linewidth=1.3, zorder=2.5)
        ax_a.add_patch(arc_fd)

    # Event horizon: r_+ = 1.6m (softly shaded 3D sphere silhouette + crisp ring)
    R_hor_vis = S * r_to_aux(data['r_plus'])
    ax_a.imshow(BH_DISK_RGBA,
                extent=[cx - R_hor_vis, cx + R_hor_vis, cy - R_hor_vis, cy + R_hor_vis],
                origin='lower', zorder=3.0)
    ax_a.add_patch(Circle((cx, cy), R_hor_vis,
                          fill=False, edgecolor=NAVY, linewidth=2.0, zorder=3.2))

    # Central rotation indicator (\Omega_H counterclockwise) inside the horizon disk
    r_rot = R_hor_vis * 0.54
    for base_deg in [25.0, 205.0]:
        a_start = np.deg2rad(base_deg)
        a_end = np.deg2rad(base_deg + 115.0)
        rot_arrow = FancyArrowPatch((cx + r_rot * np.cos(a_start), cy + r_rot * np.sin(a_start)),
                                    (cx + r_rot * np.cos(a_end), cy + r_rot * np.sin(a_end)),
                                    connectionstyle="arc3,rad=0.45",
                                    arrowstyle='-|>', mutation_scale=12,
                                    color='#fbbf24', linewidth=2.0, zorder=3.6)
        ax_a.add_patch(rot_arrow)

    ax_a.text(cx, cy + 0.15, r"Kerr BH ($a = 0.8m$)",
              color='#f8fafc', fontsize=10.5, fontweight='bold', ha='center', va='center', zorder=3.8)
    ax_a.text(cx, cy - 0.19, r"Rotation $\Omega_H$ ($\circlearrowleft$)",
              color='#fde68a', fontsize=9.8, fontweight='bold', ha='center', va='center', zorder=3.8)

    # Geometry boundary labels (bottom-left and bottom-right clear margins)
    ang_erg_lbl = np.deg2rad(-56.0)
    ax_a.annotate(r"Ergosphere boundary $r_{\mathrm{e}}(\pi/2) = 2.0m$",
                  xy=(cx + R_erg_vis * np.cos(ang_erg_lbl), cy + R_erg_vis * np.sin(ang_erg_lbl)),
                  xytext=(2.12, -3.55),
                  arrowprops=dict(arrowstyle="->", color=ORANGE_DARK, lw=1.4, shrinkA=2, shrinkB=3),
                  fontsize=10.5, fontweight='bold', color=ORANGE_DARK, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.22', facecolor=ORANGE_BG, edgecolor=ORANGE_BORDER, linewidth=1.0),
                  zorder=15)

    ang_hor_lbl = np.deg2rad(-132.0)
    ax_a.annotate(r"Event horizon $r_+ = 1.6m$",
                  xy=(cx + R_hor_vis * np.cos(ang_hor_lbl), cy + R_hor_vis * np.sin(ang_hor_lbl)),
                  xytext=(-2.58, -3.55),
                  arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.4, shrinkA=2, shrinkB=3),
                  fontsize=10.5, fontweight='bold', color=NAVY, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.22', facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.0),
                  zorder=15)

    # -------------------------------------------------------------------------
    # Draw Trajectories & Moving Particle Markers according to Stage
    # -------------------------------------------------------------------------
    x0, y0, _, _ = data['traj0']
    x1, y1, _, _ = data['traj1']
    x2, y2, _, _ = data['traj2']

    X0, Y0 = cx + S * x0, cy + S * y0
    X1, Y1 = cx + S * x1, cy + S * y1
    X2, Y2 = cx + S * x2, cy + S * y2
    X_sp, Y_sp = cx + S * data['x_split'], cy + S * data['y_split']

    # Faint guide preview of full incoming path during Stage 1
    ax_a.plot(X0, Y0, color=BLUE_MAIN, lw=1.2, ls=':', alpha=0.28, zorder=4.0)

    # Active incoming trajectory (0 — Blue)
    n0_draw = max(2, int(round(p_in * (len(X0) - 1))) + 1)
    ax_a.plot(X0[:n0_draw], Y0[:n0_draw], color='#93c5fd', lw=5.5, alpha=0.32, zorder=5.0)
    ax_a.plot(X0[:n0_draw], Y0[:n0_draw], color=BLUE_MAIN, lw=2.8, alpha=0.96, zorder=5.2)

    if n0_draw > 170:
        idx_arr0 = 145
        ax_a.annotate('', xy=(X0[idx_arr0 + 10], Y0[idx_arr0 + 10]),
                      xytext=(X0[idx_arr0], Y0[idx_arr0]),
                      arrowprops=dict(arrowstyle='-|>', color=BLUE_MAIN, lw=2.2, mutation_scale=13),
                      zorder=5.5)

    if stage == 1:
        px0, py0 = X0[n0_draw - 1], Y0[n0_draw - 1]
        ax_a.scatter([px0], [py0], color=BLUE_MAIN, s=160, alpha=0.28, edgecolors='none', zorder=8.0)
        ax_a.scatter([px0], [py0], color=BLUE_DARK, s=70, edgecolors=BG_WHITE, linewidths=1.5, zorder=8.2)
    else:
        ax_a.scatter([X0[0]], [Y0[0]], color=BLUE_MAIN, s=50, edgecolors=BG_WHITE, linewidths=1.2, zorder=6.0)

    # Incoming label (E_0 > 0) — top-left clear margin pointing to entry of trajectory 0
    idx_lbl0 = min(15, n0_draw - 1)
    ax_a.annotate(r"1. Incoming particle ($E_0 > 0$)",
                  xy=(X0[idx_lbl0], Y0[idx_lbl0]),
                  xytext=(-2.65, 2.60),
                  arrowprops=dict(arrowstyle="->", color=BLUE_MAIN, lw=1.5, shrinkA=2, shrinkB=4),
                  fontsize=10.8, fontweight='bold', color=BLUE_DARK, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.24', facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.1),
                  zorder=16)

    # Stage 2+: Splitting Vertex inside the ergosphere
    if stage >= 2:
        pulse_r = 165 + 90 * np.sin(np.pi * p_split) if stage == 2 else 145
        ax_a.scatter([X_sp], [Y_sp], color=SPLIT_GOLD, s=pulse_r, alpha=0.40, edgecolors='none', zorder=9.0)
        ax_a.scatter([X_sp], [Y_sp], color='#ffffff', s=74, edgecolors=NAVY, linewidths=2.0, zorder=9.2)
        ax_a.scatter([X_sp], [Y_sp], color=ORANGE_MAIN, s=28, edgecolors='none', zorder=9.4)

        ax_a.annotate(r"2. Split at $r_0 = 1.88m$",
                      xy=(X_sp, Y_sp),
                      xytext=(2.60, -2.35),
                      arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.5, shrinkA=2, shrinkB=5),
                      fontsize=10.8, fontweight='bold', color=NAVY, ha='center', va='center',
                      bbox=dict(boxstyle='round,pad=0.24', facecolor='#fef9c3', edgecolor='#f59e0b', linewidth=1.2),
                      zorder=16)

    # Stage 3+: Captured (1 — Orange) and Escaping (2 — Turquoise) trajectories
    if stage >= 3:
        n_out = max(2, int(round(p_out * (len(X2) - 1))) + 1)

        # Captured trajectory (1 — Orange, crosses r_+ = 1.6m)
        ax_a.plot(X1[:n_out], Y1[:n_out], color='#fcd34d', lw=5.2, alpha=0.35, zorder=6.0)
        ax_a.plot(X1[:n_out], Y1[:n_out], color=ORANGE_MAIN, lw=2.8, alpha=0.98, zorder=6.2)
        if n_out > 190:
            idx_a1 = 165
            ax_a.annotate('', xy=(X1[idx_a1 + 10], Y1[idx_a1 + 10]),
                          xytext=(X1[idx_a1], Y1[idx_a1]),
                          arrowprops=dict(arrowstyle='-|>', color=ORANGE_MAIN, lw=2.1, mutation_scale=12),
                          zorder=6.5)

        px1, py1 = X1[n_out - 1], Y1[n_out - 1]
        ax_a.scatter([px1], [py1], color=ORANGE_MAIN, s=150, alpha=0.30, edgecolors='none', zorder=8.4)
        ax_a.scatter([px1], [py1], color=ORANGE_DARK, s=66, edgecolors=BG_WHITE, linewidths=1.5, zorder=8.6)

        # Escaping trajectory (2 — Turquoise, escapes outside r_e = 2.0m)
        ax_a.plot(X2[:n_out], Y2[:n_out], color='#5eead4', lw=5.2, alpha=0.35, zorder=6.0)
        ax_a.plot(X2[:n_out], Y2[:n_out], color=TURQ_MAIN, lw=2.8, alpha=0.98, zorder=6.2)
        if n_out > 200:
            idx_a2 = 175
            ax_a.annotate('', xy=(X2[idx_a2 + 10], Y2[idx_a2 + 10]),
                          xytext=(X2[idx_a2], Y2[idx_a2]),
                          arrowprops=dict(arrowstyle='-|>', color=TURQ_MAIN, lw=2.1, mutation_scale=12),
                          zorder=6.5)

        px2, py2 = X2[n_out - 1], Y2[n_out - 1]
        ax_a.scatter([px2], [py2], color=TURQ_MAIN, s=150, alpha=0.30, edgecolors='none', zorder=8.4)
        ax_a.scatter([px2], [py2], color=TURQ_DARK, s=66, edgecolors=BG_WHITE, linewidths=1.5, zorder=8.6)

        # Callout for Captured Fragment 1 (E_1 < 0, L_{z,1} < 0)
        idx_lbl1 = min(215, n_out - 1)
        ax_a.annotate(r"3a. Captured ($E_1 < 0,\ L_{z,1} < 0$)",
                      xy=(X1[idx_lbl1], Y1[idx_lbl1]),
                      xytext=(2.55, 1.38),
                      arrowprops=dict(arrowstyle="->", color=ORANGE_MAIN, lw=1.5, shrinkA=2, shrinkB=4),
                      fontsize=10.6, fontweight='bold', color=ORANGE_DARK, ha='center', va='center',
                      bbox=dict(boxstyle='round,pad=0.22', facecolor=ORANGE_BG, edgecolor=ORANGE_BORDER, linewidth=1.1),
                      zorder=16)

        # Callout for Escaping Fragment 2 (E_2 > E_0)
        idx_lbl2 = min(310, n_out - 1)
        ax_a.annotate(r"3b. Escaping ($E_2 > E_0$)",
                      xy=(X2[idx_lbl2], Y2[idx_lbl2]),
                      xytext=(2.35, 2.60),
                      arrowprops=dict(arrowstyle="->", color=TURQ_MAIN, lw=1.5, shrinkA=2, shrinkB=4),
                      fontsize=10.8, fontweight='bold', color=TURQ_DARK, ha='center', va='center',
                      bbox=dict(boxstyle='round,pad=0.24', facecolor=TURQ_BG, edgecolor=TURQ_BORDER, linewidth=1.1),
                      zorder=16)

    # =========================================================================
    # PANEL B: Simplified Medium-Friendly 4-Stage Sequence (No Bottom Legend)
    # =========================================================================
    stages_meta = [
        (1, "1 · Approach",
         BLUE_MAIN, BLUE_DARK, BLUE_BG, BLUE_BORDER,
         r"Incoming particle enters the ergosphere.",
         r"$E_0 > 0$",
         12.8, 13.8, 1.25),

        (2, "2 · Splitting",
         SPLIT_GOLD, ORANGE_DARK, '#fefce8', '#fde047',
         r"At $r_0 = 1.88m$, the particle splits:",
         r"$p_0^\mu = p_1^\mu + p_2^\mu$",
         12.8, 14.2, 1.28),

        (3, "3 · Energy extraction",
         TURQ_MAIN, TURQ_DARK, TURQ_BG, TURQ_BORDER,
         r"Captured:   $E_{\mathrm{loc},1} > 0,\quad E_1 < 0$",
         r"Escaping:   $E_2 > E_0$",
         13.0, 13.2, 1.32),

        (4, "4 · Energy balance",
         NAVY, NAVY, '#f1f5f9', '#64748b',
         r"$E_0 = E_1 + E_2 \quad\Longrightarrow\quad E_2 = E_0 - E_1 > E_0$",
         "",
         14.8, 14.8, 1.38),
    ]

    y_tops = [2.78, 1.38, -0.02, -1.46]

    for (st_num, st_title, c_main, c_dark, c_bg, c_bdr, line1, line2, fs1, fs2, card_h), y_top in zip(stages_meta, y_tops):
        is_active = (stage == st_num) and not is_static
        is_reached = (stage >= st_num) or is_static

        face = c_bg if is_reached else '#f8fafc'
        edge = c_main if (is_active or (is_static and st_num == 4)) else (c_bdr if is_reached else '#e2e8f0')
        lw_c = 2.6 if (is_active or (st_num == 4 and is_reached)) else (1.5 if is_reached else 1.0)
        alpha_txt = 1.0 if is_reached else 0.34

        st_box = FancyBboxPatch((-4.28, y_top - card_h), 8.56, card_h,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor=face, edgecolor=edge, linewidth=lw_c, zorder=2.0)
        ax_b.add_patch(st_box)

        bar_w = 0.24 if st_num == 4 else 0.20
        bar = FancyBboxPatch((-4.28, y_top - card_h), bar_w, card_h,
                             boxstyle="round,pad=0.0,rounding_size=0.04",
                             facecolor=c_main if is_reached else '#cbd5e1',
                             edgecolor='none', zorder=2.5)
        ax_b.add_patch(bar)

        ax_b.text(-3.78, y_top - 0.30, st_title,
                  color=c_dark if is_reached else '#94a3b8',
                  fontsize=14.6 if st_num == 4 else 14.0,
                  fontweight='bold', ha='left', va='center', alpha=alpha_txt, zorder=3.0)

        if st_num == 4:
            # Extra visual emphasis on the single-line final energy-balance equation, left-aligned like cards above
            ax_b.text(-3.78, y_top - 0.88, line1,
                      color=NAVY, fontsize=fs1, fontweight='bold',
                      ha='left', va='center', alpha=alpha_txt,
                      bbox=dict(boxstyle='round,pad=0.28', facecolor=BG_WHITE, edgecolor=NAVY, linewidth=1.4),
                      zorder=3.0)
        else:
            ax_b.text(-3.78, y_top - 0.68, line1,
                      color=DARK_SLATE, fontsize=fs1, ha='left', va='center', alpha=alpha_txt, zorder=3.0)
            ax_b.text(-3.78, y_top - 1.04, line2,
                      color=NAVY, fontsize=fs2, fontweight='bold', ha='left', va='center', alpha=alpha_txt, zorder=3.0)

    # Bottom Color Legend Strip inside Panel B (exact layout from earlier version)
    leg_box = FancyBboxPatch((-4.28, -3.82), 8.56, 0.44,
                             boxstyle="round,pad=0.02,rounding_size=0.08",
                             facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.1, zorder=2.0)
    ax_b.add_patch(leg_box)

    ax_b.scatter([-3.92], [-3.60], color=BLUE_MAIN, s=68, zorder=3.0)
    ax_b.text(-3.68, -3.60, r"Incoming ($E_0 > 0$)", color=BLUE_DARK, fontsize=10.2, fontweight='bold', va='center')

    ax_b.scatter([-1.08], [-3.60], color=ORANGE_MAIN, s=68, zorder=3.0)
    ax_b.text(-0.84, -3.60, r"Captured ($E_1 < 0$)", color=ORANGE_DARK, fontsize=10.2, fontweight='bold', va='center')

    ax_b.scatter([1.62], [-3.60], color=TURQ_MAIN, s=68, zorder=3.0)
    ax_b.text(1.86, -3.60, r"Escaping ($E_2 > E_0$)", color=TURQ_DARK, fontsize=10.2, fontweight='bold', va='center')

    plt.savefig(output_path, dpi=DPI, facecolor=BG_WHITE)
    plt.close(fig)


def render_worker(args):
    """Multiprocessing worker for rendering animation frames."""
    data, frame_idx, out_path = args
    draw_frame(data, frame_idx, out_path, is_static=False)


def generate_assets():
    """Generate static publication figure, MP4, and animated GIF."""
    t0 = time.time()
    print("=== Generating Penrose Process Kerr Geodesic Animation & Static Figure ===")

    LOCAL_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    print("1. Computing exact four-momentum-conserving Kerr geodesics (a/m = 0.8)...")
    data = precompute_penrose_geodesics()
    print(f"   Split radius: r_0 = {data['r0']:.2f}m inside ergosphere [r_+ = {data['r_plus']:.2f}m, r_e = {data['r_erg']:.2f}m]")
    print(f"   Conserved energies: E_0 = {data['E0']:.5f}, E_1 = {data['E1']:.5f} (< 0), E_2 = {data['E2']:.5f} (> E_0)")
    print(f"   Angular momenta:    L_z0 = {data['Lz0']:.5f}, L_z1 = {data['Lz1']:.5f} (< 0), L_z2 = {data['Lz2']:.5f}")
    print(f"   Horizon crossing:   E_1 - Omega_H L_z1 = +{data['horizon_ineq']:.5f} > 0")

    print("2. Rendering static publication figure...")
    draw_frame(data, frame_idx=N_FRAMES - 1, output_path=STATIC_OUT, is_static=True)
    print(f"[OK] Static figure: {STATIC_OUT} ({STATIC_OUT.stat().st_size / 1024:.1f} KB)")

    frames_dir = Path(tempfile.mkdtemp(prefix="penrose_frames_"))
    print(f"3. Rendering {N_FRAMES} animation frames in {frames_dir}...")

    tasks = [(data, idx, str(frames_dir / f"frame_{idx:04d}.png")) for idx in range(N_FRAMES)]
    n_workers = max(1, multiprocessing.cpu_count() - 1)
    with multiprocessing.Pool(processes=n_workers) as pool:
        pool.map(render_worker, tasks)

    dt_render = time.time() - t0
    print(f"[OK] Rendered {N_FRAMES} frames in {dt_render:.1f} s ({dt_render / N_FRAMES:.3f} s/frame)")

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
    print(f"[OK] Generated MP4: {MP4_OUT} ({MP4_OUT.stat().st_size / (1024 * 1024):.2f} MB)")

    print("5. Encoding animated GIF (1200 px width, Lanczos + palettegen)...")
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
    print(f"[OK] Generated GIF: {GIF_OUT} ({GIF_OUT.stat().st_size / (1024 * 1024):.2f} MB)")

    shutil.rmtree(frames_dir, ignore_errors=True)
    print(f"=== Complete in {time.time() - t0:.1f} s ===")


if __name__ == '__main__':
    generate_assets()
