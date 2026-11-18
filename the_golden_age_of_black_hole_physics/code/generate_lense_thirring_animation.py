#!/usr/bin/env python3
"""
Generate 7-second looping scientific animation:
"FRAME DRAGGING: THE EFFECT OF ROTATION"
"From static spacetime to stationary, axisymmetric spacetime"

Animation Companion to `generate_lense_thirring_frame_dragging.py` for:
"The Golden Age of Black Hole Physics (1963–1974)"

Scientific & Editorial Specifications:
- Preserves the exact two-panel composition, typography, callouts, and equation
  of the static illustration (`lense_thirring_frame_dragging.png`, 1800 x 900 px).
- What moves vs. what remains fixed:
  - Panel A (J = 0): Central mass and all three gyroscopes remain completely stationary
    at the common reference orientation (theta_0 = 26°, phi_0 = 35°).
  - Panel B (J != 0):
    - Central mass's orange source-rotation arrow animates counter-clockwise around +z
      (moving left-to-right across the front of the sphere).
    - Each gyroscope's spin axis and rotor disk move together as a rigid 3D object
      at constant inclination theta_0 while precessing azimuthally around +z:
        phi_i(t) = phi_0 + Omega_LT(r_i) * t,   Omega_LT(r_i) = -GJ / (c^2 r_i^3)
    - Orange precession arrows and dashed precession ellipses remain fixed as
      directional indicators and trajectory guides.
- Animation Timing (7.0 s total @ 20 fps = 140 frames, Option A single demonstration cycle):
  - 0.0 – 0.5 s (10 frames): All gyroscopes begin with identical orientations (phi_0).
  - 0.5 – 6.5 s (120 frames): Linear-in-time Lense–Thirring precession proportional to r^-3
    (inner gyroscope precesses ~8.3x as much as outermost one), while source-rotation
    arrow animates in the opposite direction.
  - 6.5 – 7.0 s (10 frames): Hold final orientations matching the static illustration,
    then reset cleanly for the next loop cycle.
"""

import os
import shutil
import subprocess
import tempfile
import time
import multiprocessing
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Circle, FancyArrowPatch, Arc, Polygon

SCRIPT_DIR = Path(__file__).resolve().parent
GIF_OUT = SCRIPT_DIR.parent / "images" / "lense_thirring_frame_dragging_animation.gif"
MP4_OUT = SCRIPT_DIR.parent / "images" / "lense_thirring_frame_dragging_animation.mp4"

# Animation timing parameters
FPS = 20
T_PRECESS = 10.0       # 0.0 - 10.0 s: strictly linear precession phi_i(t) = phi_0 + Delta_phi_i * (t / T)
T_HOLD_END = 1.0       # 10.0 - 11.0 s: short hold at final static-figure configuration before reset
T_TOTAL = T_PRECESS + T_HOLD_END  # 11.0 s total
N_FRAMES = int(T_TOTAL * FPS)     # 220 frames


def compute_sphere_rgba(R_sphere=1.05, res=350):
    """Precompute the 3D shaded central sphere RGBA texture once across workers."""
    x_s = np.linspace(-R_sphere, R_sphere, res)
    y_s = np.linspace(-R_sphere, R_sphere, res)
    X_s, Y_s = np.meshgrid(x_s, y_s)
    R2_s = X_s**2 + Y_s**2
    mask_s = R2_s <= R_sphere**2

    Z_s = np.zeros_like(X_s)
    Z_s[mask_s] = np.sqrt(R_sphere**2 - R2_s[mask_s])

    L = np.array([-0.35, 0.45, 0.82])
    L = L / np.linalg.norm(L)

    Nx = np.zeros_like(X_s)
    Ny = np.zeros_like(Y_s)
    Nz = np.zeros_like(Z_s)
    Nx[mask_s] = X_s[mask_s] / R_sphere
    Ny[mask_s] = Y_s[mask_s] / R_sphere
    Nz[mask_s] = Z_s[mask_s] / R_sphere

    diffuse = np.maximum(0.0, Nx * L[0] + Ny * L[1] + Nz * L[2])
    ambient = 0.28
    intensity = ambient + (1.0 - ambient) * diffuse
    H = L + np.array([0.0, 0.0, 1.0])
    H = H / np.linalg.norm(H)
    specular = np.maximum(0.0, Nx * H[0] + Ny * H[1] + Nz * H[2]) ** 18
    intensity = np.clip(intensity + 0.35 * specular, 0.0, 1.0)

    c_dark = np.array([29, 78, 216], dtype=float) / 255.0   # #1d4ed8
    c_mid = np.array([59, 130, 246], dtype=float) / 255.0   # #3b82f6
    c_light = np.array([219, 234, 254], dtype=float) / 255.0 # #dbeafe

    sphere_rgba = np.zeros((res, res, 4))
    for i in range(res):
        for j in range(res):
            if mask_s[i, j]:
                val = intensity[i, j]
                if val < 0.6:
                    t_c = val / 0.6
                    c = (1.0 - t_c) * c_dark + t_c * c_mid
                else:
                    t_c = (val - 0.6) / 0.4
                    c = (1.0 - t_c) * c_mid + t_c * c_light
                sphere_rgba[i, j, :3] = c
                sphere_rgba[i, j, 3] = 1.0
    return sphere_rgba


SPHERE_RGBA = compute_sphere_rgba()


def draw_source_rotation_arrow(ax_inst, frac_motion):
    """
    Draws the orange source-rotation arrow in Panel B.
    - At frac_motion == 0.0 (initial hold 0–0.5 s) and frac_motion == 1.0 (final hold 6.5–7 s),
      renders the exact front-center FancyArrowPatch from the static figure.
    - During 0.5–6.5 s (0 < frac_motion < 1), animates the orange source-rotation arrow
      revolving counter-clockwise around +z (left-to-right across the front of the sphere)
      at constant angular velocity, completing 3 full cycles and landing seamlessly at
      the front-center position at t = 6.5 s.
    """
    if frac_motion <= 0.0 or frac_motion >= 1.0:
        rot_arrow = FancyArrowPatch((-0.92, -0.16), (0.92, -0.16),
                                    connectionstyle="arc3,rad=0.40",
                                    arrowstyle='-|>', mutation_scale=20,
                                    color='#d97706', linewidth=3.4, zorder=6)
        ax_inst.add_patch(rot_arrow)
        return

    # Parameterize the exact quadratic Bezier curve of `connectionstyle="arc3,rad=0.40"`
    # from A=(-0.92, -0.16) to B=(+0.92, -0.16) as the front hemisphere [198°, 342°]
    # of the rotation belt around the sphere.
    # Two antipodal arrows (180° apart) revolve at constant angular velocity:
    # 3 full turns (1080° total = 120°/s over the 9.0 s motion window)
    phi_center_deg = 270.0 + 1080.0 * frac_motion
    span_deg = 124.0  # [-62°, +62°] around 270°
    vis_min, vis_max = 202.0, 338.0

    def belt_xy(phi_deg_arr):
        # Map phi in [202°, 338°] to s in [0, 1] along the exact static curve
        s = (phi_deg_arr - 202.0) / 136.0
        # Exact quadratic Bezier for FancyArrowPatch((-0.92, -0.16), (0.92, -0.16), arc3,rad=0.40)
        # P0 = (-0.92, -0.16), P1 = (0.0, -0.896), P2 = (0.92, -0.16)
        x = (1.0 - s)**2 * (-0.92) + 2.0 * (1.0 - s) * s * 0.0 + s**2 * 0.92
        y = (1.0 - s)**2 * (-0.16) + 2.0 * (1.0 - s) * s * (-0.896) + s**2 * (-0.16)
        return x, y

    # Subtle guide track along the front curve so the arrow path stays visually anchored
    s_track = np.linspace(0.0, 1.0, 50)
    x_tr = (1.0 - s_track)**2 * (-0.92) + s_track**2 * 0.92
    y_tr = (1.0 - s_track)**2 * (-0.16) + 2.0 * (1.0 - s_track) * s_track * (-0.896) + s_track**2 * (-0.16)
    ax_inst.plot(x_tr, y_tr, color='#fde68a', linewidth=2.0, alpha=0.50, solid_capstyle='round', zorder=5)

    for offset_deg in [0.0, 180.0]:
        c_deg = (phi_center_deg + offset_deg) % 360.0
        if c_deg < 90.0:
            c_deg += 360.0
        p_start = c_deg - span_deg * 0.5
        p_end = c_deg + span_deg * 0.5

        v_start = max(p_start, vis_min)
        v_end = min(p_end, vis_max)

        if v_end - v_start > 8.0:
            head_deg = 15.0
            has_head = (p_end >= vis_min + 10.0) and (p_end <= vis_max)
            line_end = (v_end - head_deg * 0.70) if has_head else v_end

            if line_end > v_start:
                angs = np.linspace(v_start, line_end, 40)
                xs, ys = belt_xy(angs)
                ax_inst.plot(xs, ys, color='#d97706', linewidth=3.4, solid_capstyle='round', zorder=6)

            if has_head:
                tx, ty = belt_xy(v_end)
                bx, by = belt_xy(v_end - head_deg)
                tip_pt = np.array([tx, ty])
                base_pt = np.array([bx, by])
                tan_vec = tip_pt - base_pt
                tan_norm = np.linalg.norm(tan_vec)
                if tan_norm > 1e-6:
                    tan_u = tan_vec / tan_norm
                    norm_u = np.array([-tan_u[1], tan_u[0]])
                    hw = 0.082
                    p_l = base_pt + hw * norm_u
                    p_r = base_pt - hw * norm_u
                    notch_pt = base_pt + 0.15 * tan_vec
                    poly = Polygon([tip_pt, p_l, notch_pt, p_r], closed=True,
                                   facecolor='#d97706', edgecolor='#d97706', linewidth=1.0, zorder=7)
                    ax_inst.add_patch(poly)


def render_frame(args):
    frame_idx, frames_dir = args
    t_sec = frame_idx / float(FPS)

    # Strictly linear evolution over 0 <= t <= T_PRECESS (10.0 s), followed by short hold
    if t_sec >= T_PRECESS:
        frac_motion = 1.0
    else:
        frac_motion = t_sec / T_PRECESS

    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    fig_w, fig_h = 1800.0 / 140.0, 900.0 / 140.0
    dpi = 140
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#334155'
    BORDER_COLOR = '#cbd5e1'
    CARD_BG = '#f8fafc'

    BLUE_DARK = '#1d4ed8'
    BLUE_BORDER = '#93c5fd'

    ORANGE_DARK = '#b45309'
    ORANGE_BORDER = '#fde68a'
    ORANGE_BG = '#fffbeb'

    # 1. Top Header Banner (unchanged from static figure)
    title_box = FancyBboxPatch((0.020, 0.865), 0.960, 0.115,
                               boxstyle="round,pad=0.002,rounding_size=0.008",
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax.add_patch(title_box)
    ax.text(0.50, 0.948, "FRAME DRAGGING: THE EFFECT OF ROTATION",
            color=NAVY, fontsize=17.5, fontweight='bold', ha='center', va='center')
    ax.text(0.50, 0.914, "From static spacetime to stationary, axisymmetric spacetime",
            color=SLATE, fontsize=13.5, fontweight='bold', ha='center', va='center')
    ax.text(0.50, 0.880, r"Gyroscopes shown after equal elapsed time $\Delta t$  ·  Precession around $\hat{\mathbf{z}}$ at constant inclination $\theta_0$",
            color=DARK_SLATE, fontsize=10.8, fontweight='bold', ha='center', va='center')

    R_sphere = 1.05
    p_w = 0.472
    p_h = 0.825
    p_y = 0.020

    ax_a = fig.add_axes([0.020, p_y, p_w, p_h])
    ax_b = fig.add_axes([0.508, p_y, p_w, p_h])

    for p_ax, p_letter, p_title, p_sub, is_rotating in [
        (ax_a, "A", "Nonrotating mass", "Static spacetime  (J = 0)", False),
        (ax_b, "B", "Rotating mass", "Stationary, axisymmetric spacetime  (J ≠ 0)", True)
    ]:
        p_ax.set_xlim(-4.9, 4.9)
        p_ax.set_ylim(-4.3, 4.3)
        p_ax.set_aspect('equal')
        p_ax.axis('off')

        card = FancyBboxPatch((-4.75, -4.15), 9.5, 8.3,
                              boxstyle="round,pad=0.02,rounding_size=0.15",
                              facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=0)
        p_ax.add_patch(card)

        hdr_box = FancyBboxPatch((-4.5, 3.25), 9.0, 0.85,
                                 boxstyle="round,pad=0.02,rounding_size=0.08",
                                 facecolor=CARD_BG if not is_rotating else ORANGE_BG,
                                 edgecolor=BORDER_COLOR if not is_rotating else ORANGE_BORDER,
                                 linewidth=1.2, zorder=1)
        p_ax.add_patch(hdr_box)

        p_ax.text(0.0, 3.75, f"{p_letter}  ·  {p_title}",
                  color=NAVY if not is_rotating else ORANGE_DARK,
                  fontsize=15.5, fontweight='bold', ha='center', va='center', zorder=2)
        p_ax.text(0.0, 3.42, p_sub,
                  color=SLATE if not is_rotating else DARK_SLATE,
                  fontsize=13.0, fontweight='bold', ha='center', va='center', zorder=2)

        radii = [1.95, 2.95, 3.95]
        tilt_aspect = 0.38

        # 1. Back half of reference guides
        for r_val in radii:
            e_back = Arc((0, 0), 2 * r_val, 2 * r_val * tilt_aspect,
                         angle=0, theta1=0, theta2=180,
                         edgecolor='#94a3b8', linewidth=1.3, linestyle='--', zorder=1)
            p_ax.add_patch(e_back)

        # 2. Vertical rotation / reference axis (z-axis)
        p_ax.plot([0, 0], [0.8, 2.45], color='#64748b', linewidth=2.0, linestyle='-', zorder=2)
        p_ax.plot([0, 0], [-2.45, -0.8], color='#64748b', linewidth=2.0, linestyle='-', zorder=2)

        if not is_rotating:
            p_ax.text(0.0, 2.65, r"Symmetry axis ($z$)",
                      fontsize=11.4, fontweight='bold', color=DARK_SLATE, ha='center', va='bottom', zorder=10)
        else:
            p_ax.annotate('', xy=(0, 2.55), xytext=(0, 1.70),
                          arrowprops=dict(arrowstyle='-|>', color='#d97706', lw=2.8, mutation_scale=16),
                          zorder=10)
            p_ax.text(0.0, 2.70, r"Rotation axis ($z$), $\mathbf{J}$",
                      fontsize=11.4, fontweight='bold', color='#b45309', ha='center', va='bottom', zorder=10)

        # 3. Central 3D Sphere
        p_ax.imshow(SPHERE_RGBA, extent=[-R_sphere, R_sphere, -R_sphere, R_sphere], origin='lower', zorder=3)
        p_ax.add_patch(Circle((0, 0), R_sphere, fill=False, edgecolor='#1e3a8a', linewidth=1.6, zorder=4))

        # 4. Equator reference arc on sphere
        eq_arc = Arc((0, 0), 2 * R_sphere, 2 * R_sphere * tilt_aspect,
                     angle=0, theta1=180, theta2=360,
                     edgecolor='#bfdbfe', linewidth=1.4, linestyle='-', alpha=0.9, zorder=4)
        p_ax.add_patch(eq_arc)

        # 5. Front half of reference guides
        for r_val in radii:
            e_front = Arc((0, 0), 2 * r_val, 2 * r_val * tilt_aspect,
                          angle=0, theta1=180, theta2=360,
                          edgecolor='#94a3b8', linewidth=1.3, linestyle='--', zorder=5)
            p_ax.add_patch(e_front)

        # 6. Animated Source rotation arrow (Panel B only)
        if is_rotating:
            draw_source_rotation_arrow(p_ax, frac_motion)
            p_ax.text(0.0, -1.25, r"Source rotation, $\mathbf{J}$",
                      fontsize=12.2, fontweight='bold', color='#b45309', ha='center', va='top',
                      bbox=dict(boxstyle='round,pad=0.22', facecolor='#ffffff', edgecolor='#fde68a', linewidth=1.1),
                      zorder=10)

        # 7. Gyroscope Drawing Function
        sin_beta = tilt_aspect
        cos_beta = np.sqrt(1.0 - sin_beta**2)

        def project_3d(vx, vy, vz):
            return np.array([vx, vy * sin_beta + vz * cos_beta])

        def get_rotor_ellipse(s_vec, R_rot):
            ref = np.array([0.0, 0.0, 1.0]) if abs(s_vec[2]) < 0.92 else np.array([1.0, 0.0, 0.0])
            u1 = np.cross(s_vec, ref)
            u1 /= np.linalg.norm(u1)
            u2 = np.cross(s_vec, u1)
            p1 = project_3d(u1[0], u1[1], u1[2])
            p2 = project_3d(u2[0], u2[1], u2[2])
            M = np.column_stack([p1, p2])
            C = (R_rot**2) * (M @ M.T)
            vals, vecs = np.linalg.eigh(C)
            w = 2.0 * np.sqrt(max(1e-6, vals[1]))
            h = 2.0 * np.sqrt(max(1e-6, vals[0]))
            ang = np.degrees(np.arctan2(vecs[1, 1], vecs[0, 1]))
            return w, h, ang

        theta0 = np.radians(26.0)
        phi0 = np.radians(35.0)
        g_rad = 0.35
        p_len = g_rad * 2.05
        cone_z = p_len * np.cos(theta0)
        cone_r = p_len * np.sin(theta0)
        c2d = project_3d(0.0, 0.0, cone_z)

        def draw_gyro_3d_anim(ax_inst, gx, gy, current_dphi_deg, max_dphi_deg, show_arc):
            # Elevate the fixed orange directional arrows so the moving gyroscope arrows
            # sweep cleanly underneath them without collision at any phase
            dy_arc = 0.16 if (show_arc and max_dphi_deg > 100.0) else (0.08 if show_arc else 0.0)

            # 1. Local vertical reference axis (+z direction)
            ax_inst.plot([gx, gx], [gy - 0.32, gy + c2d[1] + dy_arc + 0.22],
                         color='#64748b', linestyle=':', linewidth=1.4, zorder=6)

            # 2. Fixed precession guide ellipse
            ax_inst.add_patch(Ellipse((gx + c2d[0], gy + c2d[1] + dy_arc), 2 * cone_r, 2 * cone_r * sin_beta,
                                      edgecolor='#cbd5e1', facecolor='none', linestyle='--', linewidth=1.1, zorder=6))

            # 3. Outer circular gimbal frame (fixed)
            ax_inst.add_patch(Circle((gx, gy), g_rad, fill=True, facecolor='#ffffff', edgecolor='#475569', linewidth=1.8, zorder=7))

            # Current 3D spin vector s_i(t) at constant inclination theta0 and azimuth phi_i(t)
            current_phi = phi0 - np.radians(current_dphi_deg)
            s_vec = np.array([np.sin(theta0) * np.cos(current_phi),
                              np.sin(theta0) * np.sin(current_phi),
                              np.cos(theta0)])

            # 4. Rotor disk (moves rigidly with spin axis s_vec)
            w_rot, h_rot, ang_rot = get_rotor_ellipse(s_vec, g_rad * 0.85)
            ax_inst.add_patch(Ellipse((gx, gy), w_rot, h_rot, angle=ang_rot,
                                      facecolor='#3b82f6', edgecolor='#1d4ed8', linewidth=1.3, alpha=0.92, zorder=8))

            # 5. Central hub (fixed)
            ax_inst.add_patch(Circle((gx, gy), g_rad * 0.20, facecolor='#ffffff', edgecolor='#0f172a', linewidth=1.2, zorder=9))

            # Fixed initial reference pointer ghost & origin dot
            if show_arc:
                s0_tip3d = np.array([cone_r * np.cos(phi0), cone_r * np.sin(phi0), cone_z])
                p0_tip2d = project_3d(s0_tip3d[0], s0_tip3d[1], s0_tip3d[2])
                ax_inst.plot([gx, gx + p0_tip2d[0]], [gy, gy + p0_tip2d[1] + dy_arc],
                             color='#94a3b8', linestyle=':', linewidth=1.4, zorder=9)
                ax_inst.plot(gx + p0_tip2d[0], gy + p0_tip2d[1] + dy_arc, marker='o', markersize=3.2,
                             color='#64748b', zorder=10)

            # 6. Animated spin pointer arrow (rotates around local +z at constant theta0)
            tip3d = np.array([cone_r * np.cos(current_phi), cone_r * np.sin(current_phi), cone_z])
            tip2d = project_3d(tip3d[0], tip3d[1], tip3d[2])
            base3d = -0.32 * tip3d
            base2d = project_3d(base3d[0], base3d[1], base3d[2])

            arrow = FancyArrowPatch((gx + base2d[0], gy + base2d[1]),
                                    (gx + tip2d[0], gy + tip2d[1]),
                                    arrowstyle='-|>', mutation_scale=12, shrinkA=0, shrinkB=0,
                                    color='#0f172a', linewidth=2.4, zorder=14)
            ax_inst.add_patch(arrow)

            # 7. Fixed orange precession directional arrows (Panel B only)
            if show_arc and max_dphi_deg > 1.0:
                arc_end_phi = phi0 - np.radians(max_dphi_deg)
                end_tip3d = np.array([cone_r * np.cos(arc_end_phi), cone_r * np.sin(arc_end_phi), cone_z])
                end_tip2d = project_3d(end_tip3d[0], end_tip3d[1], end_tip3d[2])

                tan_3d = np.array([np.sin(arc_end_phi), -np.cos(arc_end_phi), 0.0])
                tan_2d = project_3d(tan_3d[0], tan_3d[1], tan_3d[2])
                tan_2d /= np.linalg.norm(tan_2d)
                normal_2d = np.array([-tan_2d[1], tan_2d[0]])

                if max_dphi_deg > 100.0:
                    head_len, head_w, notch = 0.065, 0.052, 0.20
                elif max_dphi_deg > 40.0:
                    head_len, head_w, notch = 0.052, 0.044, 0.18
                else:
                    head_len, head_w, notch = 0.040, 0.035, 0.16

                arrow_color = '#ea580c'
                head_fill = '#0f172a'
                head_edge = '#0f172a'

                d_phi_head = head_len / cone_r
                line_end_phi = arc_end_phi + (1.0 - notch * 0.5) * d_phi_head
                if line_end_phi < phi0:
                    arc_angles_line = np.linspace(phi0, line_end_phi, max(30, int(max_dphi_deg * 1.5)))
                    arc_pts_line = np.array([project_3d(cone_r * np.cos(a), cone_r * np.sin(a), cone_z) for a in arc_angles_line])
                    ax_inst.plot(gx + arc_pts_line[:, 0], gy + arc_pts_line[:, 1] + dy_arc, color='#ffffff', linewidth=5.2, zorder=11, solid_capstyle='butt')
                    ax_inst.plot(gx + arc_pts_line[:, 0], gy + arc_pts_line[:, 1] + dy_arc, color=arrow_color, linewidth=3.2, zorder=12, solid_capstyle='butt')

                tip_pt = end_tip2d + np.array([0.0, dy_arc])
                base_pt = tip_pt - head_len * tan_2d
                p_l = base_pt + head_w * normal_2d
                p_r = base_pt - head_w * normal_2d
                tip_pt_ax = np.array([gx + tip_pt[0], gy + tip_pt[1]])
                p_l_ax = np.array([gx + p_l[0], gy + p_l[1]])
                base_notch_ax = np.array([gx + base_pt[0] - notch * head_len * tan_2d[0], gy + base_pt[1] - notch * head_len * tan_2d[1]])
                p_r_ax = np.array([gx + p_r[0], gy + p_r[1]])

                poly = Polygon([tip_pt_ax, p_l_ax, base_notch_ax, p_r_ax],
                               closed=True, facecolor=head_fill, edgecolor=head_edge, linewidth=1.2, zorder=13)
                ax_inst.add_patch(poly)

        gyro_radii = [1.95, 2.95, 3.95]
        r0 = gyro_radii[0]

        for r_val in gyro_radii:
            gx = r_val
            gy = 0.0

            if not is_rotating:
                draw_gyro_3d_anim(p_ax, gx, gy, current_dphi_deg=0.0, max_dphi_deg=0.0, show_arc=False)
            else:
                prec_strength = (r0 / r_val)**3
                max_delta_phi = 250.0 * prec_strength
                curr_delta_phi = max_delta_phi * frac_motion
                draw_gyro_3d_anim(p_ax, gx, gy, current_dphi_deg=curr_delta_phi, max_dphi_deg=max_delta_phi, show_arc=True)

        # 8. Radial Distance Axis & Labels
        axis_y = -0.48
        p_ax.annotate('', xy=(4.35, axis_y), xytext=(1.05, axis_y),
                      arrowprops=dict(arrowstyle='->', color='#64748b', lw=1.3), zorder=8)

        for r_val, r_lbl in zip(gyro_radii, [r"$r_1$", r"$r_2$", r"$r_3$"]):
            p_ax.plot([r_val, r_val], [axis_y - 0.06, axis_y + 0.06], color='#64748b', lw=1.4, zorder=8)
            p_ax.text(r_val, axis_y - 0.12, r_lbl,
                      fontsize=11.2, fontweight='bold', color=SLATE if not is_rotating else DARK_SLATE,
                      ha='center', va='top',
                      bbox=dict(boxstyle='round,pad=0.15', facecolor='#ffffff', edgecolor='none', alpha=0.92),
                      zorder=10)

        rad_lbl_x = 3.16 if is_rotating else 2.45
        rad_lbl_y = -1.52 if is_rotating else -1.60
        p_ax.text(rad_lbl_x, rad_lbl_y, "Radial distance r\nfrom center of mass",
                  fontsize=11.2, fontstyle='italic', fontweight='bold', color=SLATE, ha='center', va='top',
                  bbox=dict(boxstyle='round,pad=0.22', facecolor='#f8fafc', edgecolor='#cbd5e1', lw=0.8),
                  zorder=10)

        # 9. Callouts & Bottom Summary Boxes (unchanged from static figure)
        if not is_rotating:
            p_ax.annotate("Distant reference axes\n(fixed orientation)",
                          xy=(-2.60, 2.85), xytext=(-2.60, 2.10),
                          arrowprops=dict(arrowstyle="->", color=DARK_SLATE, lw=2.0),
                          fontsize=11.6, fontweight='bold', color=DARK_SLATE, ha='center', va='top',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.0),
                          zorder=10)

            p_ax.annotate("Ideal gyroscope\n(inertial-axis probe)",
                          xy=(2.05, 0.72), xytext=(2.55, 1.80),
                          arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.5, shrinkA=2, shrinkB=4),
                          fontsize=11.2, fontweight='bold', color=BLUE_DARK, ha='center', va='bottom',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor=BLUE_BORDER, linewidth=1.1),
                          zorder=10)

            p_ax.annotate("Equatorial reference guides\n(increasing distance r)",
                          xy=(-1.95, -0.40), xytext=(-2.35, -1.60),
                          arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.4, shrinkA=2, shrinkB=4),
                          fontsize=11.8, fontweight='bold', color=SLATE, ha='center', va='top',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.0),
                          zorder=10)

            box_a = FancyBboxPatch((-4.35, -4.10), 8.70, 1.60,
                                   boxstyle='round,pad=0.04,rounding_size=0.10',
                                   facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.3, zorder=9)
            p_ax.add_patch(box_a)
            p_ax.text(0.0, -2.95, "No rotation-induced frame dragging",
                      fontsize=12.4, fontweight='bold', color=DARK_SLATE, ha='center', va='center', zorder=10)
            p_ax.text(0.0, -3.52, "Gyroscope orientations remain fixed\nrelative to distant reference axes",
                      fontsize=11.2, fontweight='bold', color=SLATE, ha='center', va='center', zorder=10)
        else:
            p_ax.annotate("Distant reference axes\n(fixed orientation)",
                          xy=(-2.60, 2.85), xytext=(-2.60, 2.10),
                          arrowprops=dict(arrowstyle="->", color=DARK_SLATE, lw=2.0),
                          fontsize=11.6, fontweight='bold', color=DARK_SLATE, ha='center', va='top',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.0),
                          zorder=10)

            p_ax.annotate("Frame-dragging precession\nOpposite to body rotation " + r"$\mathbf{J}$",
                          xy=(2.14, 0.94), xytext=(2.50, 1.68),
                          arrowprops=dict(arrowstyle="->", color=ORANGE_DARK, lw=1.5, shrinkA=2, shrinkB=4),
                          fontsize=11.2, fontweight='bold', color=ORANGE_DARK, ha='center', va='bottom',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#fffbeb', edgecolor=ORANGE_BORDER, linewidth=1.1),
                          zorder=10)

            box_b = FancyBboxPatch((-4.35, -4.10), 8.70, 1.60,
                                   boxstyle='round,pad=0.04,rounding_size=0.10',
                                   facecolor='#fffbeb', edgecolor=ORANGE_BORDER, linewidth=1.3, zorder=9)
            p_ax.add_patch(box_b)
            p_ax.text(0.0, -2.72, "Local inertial axes undergo rotation-induced precession",
                      fontsize=11.4, fontweight='bold', color=ORANGE_DARK, ha='center', va='center', zorder=10)
            p_ax.text(0.0, -3.05, "Lense–Thirring angular velocity (equatorial weak-field limit):",
                      fontsize=10.6, fontweight='bold', color='#92400e', ha='center', va='center', zorder=10)
            p_ax.text(0.0, -3.64, r"$\boldsymbol{\Omega}_{\mathrm{LT}} = -\frac{GJ}{c^2 r^3}\,\hat{\mathbf{z}}$",
                      fontsize=18.5, fontweight='bold', color=ORANGE_DARK, ha='center', va='center', zorder=10)

    out_file = os.path.join(frames_dir, f"frame_{frame_idx:04d}.png")
    fig.savefig(out_file, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    return frame_idx


def generate_animation():
    GIF_OUT.parent.mkdir(parents=True, exist_ok=True)
    frames_dir = tempfile.mkdtemp(prefix="lense_thirring_anim_")

    try:
        t0 = time.time()
        n_workers = max(1, min(14, multiprocessing.cpu_count() - 1))
        print(f"[INFO] Rendering {N_FRAMES} frames ({T_TOTAL:.1f} s @ {FPS} fps) using {n_workers} workers...")

        tasks = [(i, frames_dir) for i in range(N_FRAMES)]
        with multiprocessing.Pool(processes=n_workers) as pool:
            for done_idx in pool.imap_unordered(render_frame, tasks, chunksize=4):
                if (done_idx + 1) % 28 == 0 or done_idx == N_FRAMES - 1:
                    print(f"  Rendered frame {done_idx + 1:3d} / {N_FRAMES}")

        dt = time.time() - t0
        print(f"[OK] Rendered {N_FRAMES} frames in {dt:.1f} s ({dt / N_FRAMES:.3f} s/frame)")

        # 1. Encode high-resolution animated GIF (loop=0, split-palette for crisp text and lines)
        cmd_gif = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", os.path.join(frames_dir, "frame_%04d.png"),
            "-vf", f"fps={FPS},scale=1800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=224:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4",
            "-loop", "0",
            str(GIF_OUT),
        ]
        subprocess.run(cmd_gif, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        gif_mb = GIF_OUT.stat().st_size / (1024 * 1024)
        print(f"[OK] Generated GIF: {GIF_OUT} ({gif_mb:.2f} MB)")

        # 2. Encode master MP4 video (1800 x 900 @ 20 fps)
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
        print(f"[OK] Generated MP4: {MP4_OUT} ({mp4_mb:.2f} MB)")


    finally:
        shutil.rmtree(frames_dir, ignore_errors=True)


if __name__ == "__main__":
    generate_animation()
