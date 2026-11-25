#!/usr/bin/env python3
r"""
generate_integrable_torus_animation.py

Generates the three-panel animated illustration
("From Integrability to Motion on Invariant Tori")
for Section 2.1 ("Integrable Systems and Invariant Tori")
of Article 3: "Order and Chaos: The Road to Modern Dynamics III".

Visual & Mathematical Structure:
  - Panel A (Static): 3D representation of a 2D invariant torus (embedded in 4D
    phase space) with action-angle coordinates: constant actions I_1, I_2
    identifying the torus, and angular coordinates varphi_1 (toroidal),
    varphi_2 (poloidal) specifying position on its surface.
  - Panel B (Animated): Periodic trajectory on the identical torus with rational
    frequency ratio omega_1 / omega_2 = 2 / 3 (omega_1 = 2, omega_2 = 3).
    Closes exactly at t = 2*pi after 2 toroidal and 3 poloidal turns, then
    retraces the identical closed orbit.
  - Panel C (Animated): Quasiperiodic trajectory on the identical torus with
    irrational frequency ratio omega_1 / omega_2 = sqrt(2)
    (omega_1 = 2*sqrt(2), omega_2 = 2). Never closes and winds progressively
    and densely across the surface over finite time without repeating.

Torus Visualization Parametrization (identical across all three panels):
  x = (R + r cos(varphi_2)) cos(varphi_1)
  y = (R + r cos(varphi_2)) sin(varphi_1)
  z = r sin(varphi_2)
  with R = 2.0, r = 0.86, varphi_i(t) = varphi_i(0) + omega_i * t.

Rendering Engine:
  - Custom exact orthographic 3D camera (elev=30 deg, azim=-52 deg) with
    Phong-shaded translucent torus facets and exact ray-torus occlusion testing,
    producing zero z-fighting and crisp front/back depth separation.

Timeline (16.5 s @ 24 fps = 396 frames, 1920 x 1000 px):
  -  0.00 -> 14.00 s: Uniform evolution t_sim in [0, 10*pi]
                      * Panel B closes its 2:3 periodic orbit at t_anim = 2.80 s
                        (t_sim = 2*pi), then retraces 4 more times.
                      * Panel C winds continuously through ~14.14 toroidal and
                        10 poloidal turns without closing.
  - 14.00 -> 16.00 s: Hold (2.0 s) on the completed comparison state.
  - 16.00 -> 16.50 s: Smooth cross-fade reset of Panels B & C to t_sim = 0.

Outputs:
  - Master MP4: images/integrable_torus_motion.mp4 (24 fps, 1920x1000)
  - Web GIF:    images/integrable_torus_motion.gif (14 fps, 1440px, loop=0)
  - Poster PNG: images/integrable_torus_motion.png (t_sim = 10*pi overview)
"""

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
from matplotlib.collections import PolyCollection, LineCollection

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
FRAMES_DIR = Path("/tmp/integrable_torus_motion_frames")

# Torus geometry (shared across all three panels)
R_MAJOR = 2.00
R_MINOR = 0.86

# Camera orientation (shared across all three panels)
ELEV_DEG = 32.0
AZIM_DEG = -54.0

# Frequencies (Panels B and C)
OMEGA_B = (2.0, 3.0)                  # rational ratio 2/3 -> closes at t = 2*pi
OMEGA_C = (2.0 * np.sqrt(2.0), 2.0)   # irrational ratio sqrt(2) -> never closes
T_SIM_MAX = 11.45 * np.pi             # 5.725 periodic cycles in B (ends cleanly off start dot); ~16.2 x 11.45 turns in C
N_SAMPLES = 8000

# Animation timeline (17.5 s @ 24 fps = 420 frames)
FPS_MASTER = 24
T_EVOLVE_END = 15.0
T_HOLD_END = 17.0
TOTAL_DURATION = 17.5
N_TOTAL_FRAMES = int(round(TOTAL_DURATION * FPS_MASTER))

# Visual palette harmonized with kam_invariant_tori_picture.png & kam_poincare_sections.png
NAVY = "#0f172a"
DARK_SLATE = "#1e293b"
SLATE = "#334155"
MUTED_SLATE = "#475569"
BORDER_CARD = "#cbd5e1"
BG_CARD = "#f8fafc"
BG_BOX = "#ffffff"

BLUE_ACCENT = "#2563eb"
BLUE_DARK = "#1d4ed8"
BLUE_LIGHT = "#eff6ff"
BLUE_BORDER = "#93c5fd"

ORANGE_ACCENT = "#ea580c"
ORANGE_DARK = "#c2410c"
ORANGE_LIGHT = "#fff7ed"
ORANGE_BORDER = "#fdba74"

TEAL_ACCENT = "#0d9488"
TEAL_DARK = "#0f766e"
TEAL_LIGHT = "#f0fdfa"
TEAL_BORDER = "#5eead4"

EQ_BG = "#f1f5f9"
EQ_BORDER = "#94a3b8"

G_SCENE = None


def build_camera(elev_deg=ELEV_DEG, azim_deg=AZIM_DEG):
    """Build orthonormal camera basis (right u, up v, view_dir w pointing toward camera)."""
    el = np.deg2rad(elev_deg)
    az = np.deg2rad(azim_deg)
    # Direction from origin toward camera
    w = np.array([
        np.cos(el) * np.cos(az),
        np.cos(el) * np.sin(az),
        np.sin(el),
    ], dtype=float)
    w /= np.linalg.norm(w)
    world_up = np.array([0.0, 0.0, 1.0], dtype=float)
    u = np.cross(world_up, w)
    u /= np.linalg.norm(u)
    v = np.cross(w, u)
    v /= np.linalg.norm(v)
    return u, v, w


def torus_point_and_normal(phi1, phi2):
    """Evaluate 3D coordinates (N, 3) and unit outward normal (N, 3) on the torus."""
    c1, s1 = np.cos(phi1), np.sin(phi1)
    c2, s2 = np.cos(phi2), np.sin(phi2)
    rad = R_MAJOR + R_MINOR * c2
    pts = np.stack([rad * c1, rad * s1, R_MINOR * s2], axis=-1)
    nrm = np.stack([c2 * c1, c2 * s1, s2], axis=-1)
    return pts, nrm


def project_pts(pts, cam):
    """Orthographic projection returning (x2d, y2d, depth) where larger depth is closer to camera."""
    u, v, w = cam
    x2 = pts @ u
    y2 = pts @ v
    z2 = pts @ w
    return x2, y2, z2


def check_torus_visibility(pts, nrm, cam):
    """
    Exact visibility test for points on the torus surface under orthographic view:
    visible iff front-facing (n . w > 0) AND ray p + s*w (s > 0.06) never re-enters the torus.
    """
    _, _, w = cam
    front_facing = (nrm @ w) > -0.02

    # Vectorized ray march along +w from s = 0.07 to 5.5
    s_vals = np.linspace(0.07, 5.5, 56)[None, :, None]  # (1, S, 1)
    ray_pts = pts[:, None, :] + s_vals * w[None, None, :]  # (N, S, 3)
    rho = np.hypot(ray_pts[..., 0], ray_pts[..., 1])
    implicit = (rho - R_MAJOR) ** 2 + ray_pts[..., 2] ** 2 - (R_MINOR ** 2)
    occluded = np.any(implicit < -0.002, axis=1)
    return front_facing & (~occluded)


def build_torus_mesh(cam, nu=88, nv=44):
    """Precompute Phong-shaded back and front torus quad meshes plus subtle grid curves."""
    u_grid = np.linspace(0.0, 2.0 * np.pi, nu + 1)
    v_grid = np.linspace(0.0, 2.0 * np.pi, nv + 1)
    UU, VV = np.meshgrid(u_grid, v_grid, indexing="ij")
    pts, nrm = torus_point_and_normal(UU, VV)
    x2, y2, z2 = project_pts(pts, cam)

    # Soft studio lighting in world space (key light upper-left-front + cool fill)
    u_cam, v_cam, w_cam = cam
    light1 = (-0.42 * u_cam + 0.58 * v_cam + 0.70 * w_cam)
    light1 /= np.linalg.norm(light1)
    light2 = (0.55 * u_cam - 0.25 * v_cam + 0.80 * w_cam)
    light2 /= np.linalg.norm(light2)
    half_vec = light1 + w_cam
    half_vec /= np.linalg.norm(half_vec)

    # Quad vertices, centers, normals, depths
    q_x = np.stack([x2[:-1, :-1], x2[1:, :-1], x2[1:, 1:], x2[:-1, 1:]], axis=-1)
    q_y = np.stack([y2[:-1, :-1], y2[1:, :-1], y2[1:, 1:], y2[:-1, 1:]], axis=-1)
    q_z = 0.25 * (z2[:-1, :-1] + z2[1:, :-1] + z2[1:, 1:] + z2[:-1, 1:])
    q_pts = 0.25 * (pts[:-1, :-1] + pts[1:, :-1] + pts[1:, 1:] + pts[:-1, 1:])
    q_nrm = 0.25 * (nrm[:-1, :-1] + nrm[1:, :-1] + nrm[1:, 1:] + nrm[:-1, 1:])
    q_nrm /= np.linalg.norm(q_nrm, axis=-1, keepdims=True)

    polys = np.stack([q_x, q_y], axis=-1).reshape(-1, 4, 2)
    depths = q_z.reshape(-1)
    c_pts = q_pts.reshape(-1, 3)
    c_nrm = q_nrm.reshape(-1, 3)

    vis = check_torus_visibility(c_pts, c_nrm, cam)

    # Phong shading for pearlescent cool-slate translucent torus
    ndotl1 = np.clip(c_nrm @ light1, 0.0, 1.0)
    ndotl2 = np.clip(c_nrm @ light2, 0.0, 1.0)
    ndoth = np.clip(c_nrm @ half_vec, 0.0, 1.0) ** 22
    ndotv = np.clip(np.abs(c_nrm @ w_cam), 0.0, 1.0)
    rim = (1.0 - ndotv) ** 2.1

    base_rgb = np.array([0.81, 0.87, 0.94])  # cool light slate-blue
    shade = 0.44 + 0.44 * ndotl1 + 0.14 * ndotl2
    rgb = np.clip(base_rgb[None, :] * shade[:, None] + 0.24 * ndoth[:, None] - 0.14 * rim[:, None], 0.0, 1.0)

    # Back surface: soft muted translucent
    back_idx = np.where(~vis)[0]
    back_order = back_idx[np.argsort(depths[back_idx])]
    back_polys = polys[back_order]
    back_rgba = np.column_stack([rgb[back_order] * 0.93, np.full(len(back_order), 0.34)])

    # Front surface: translucent glass-like pearlescent shell so back trajectories remain softly visible
    front_idx = np.where(vis)[0]
    front_order = front_idx[np.argsort(depths[front_idx])]
    front_polys = polys[front_order]
    front_alpha = 0.56 + 0.20 * rim[front_order]
    front_rgba = np.column_stack([rgb[front_order], np.clip(front_alpha, 0.0, 0.82)])

    # Subtle meridian / latitude coordinate mesh lines (front only, very light)
    grid_front_segs = []
    # 12 poloidal circles (meridians)
    v_fine = np.linspace(0.0, 2.0 * np.pi, 120)
    for u0 in np.linspace(0.0, 2.0 * np.pi, 12, endpoint=False):
        p_g, n_g = torus_point_and_normal(np.full_like(v_fine, u0), v_fine)
        vis_g = check_torus_visibility(p_g, n_g, cam)
        gx, gy, _ = project_pts(p_g, cam)
        for i in range(len(v_fine) - 1):
            if vis_g[i] and vis_g[i + 1]:
                grid_front_segs.append([(gx[i], gy[i]), (gx[i + 1], gy[i + 1])])
    # 6 toroidal circles (parallels)
    u_fine = np.linspace(0.0, 2.0 * np.pi, 160)
    for v0 in np.linspace(0.0, 2.0 * np.pi, 6, endpoint=False):
        p_g, n_g = torus_point_and_normal(u_fine, np.full_like(u_fine, v0))
        vis_g = check_torus_visibility(p_g, n_g, cam)
        gx, gy, _ = project_pts(p_g, cam)
        for i in range(len(u_fine) - 1):
            if vis_g[i] and vis_g[i + 1]:
                grid_front_segs.append([(gx[i], gy[i]), (gx[i + 1], gy[i + 1])])

    return {
        "back_polys": back_polys,
        "back_rgba": back_rgba,
        "front_polys": front_polys,
        "front_rgba": front_rgba,
        "grid_front_segs": grid_front_segs,
    }


def precompute_curve(omega1, omega2, cam, t_max=T_SIM_MAX, n_samples=N_SAMPLES, phi1_0=0.0, phi2_0=0.0):
    """Precompute 2D projected curve points and exact front/back visibility mask."""
    t_arr = np.linspace(0.0, t_max, n_samples)
    phi1 = phi1_0 + omega1 * t_arr
    phi2 = phi2_0 + omega2 * t_arr
    pts, nrm = torus_point_and_normal(phi1, phi2)
    x2, y2, z2 = project_pts(pts, cam)
    vis = check_torus_visibility(pts, nrm, cam)
    return {
        "t": t_arr,
        "x2": x2,
        "y2": y2,
        "z2": z2,
        "vis": vis,
    }


def precompute_circle(cam, fixed_axis: str, fixed_val: float, n_pts: int = 360):
    """Precompute a coordinate circle (toroidal or poloidal) for Panel A."""
    ang = np.linspace(0.0, 2.0 * np.pi, n_pts)
    if fixed_axis == "phi2":
        phi1, phi2 = ang, np.full_like(ang, fixed_val)
    else:
        phi1, phi2 = np.full_like(ang, fixed_val), ang
    pts, nrm = torus_point_and_normal(phi1, phi2)
    x2, y2, z2 = project_pts(pts, cam)
    vis = check_torus_visibility(pts, nrm, cam)
    return {"ang": ang, "x2": x2, "y2": y2, "vis": vis}


def build_scene_data():
    """Precompute camera, torus mesh, Panel A coordinate circles, and Panel B/C trajectories."""
    cam = build_camera(ELEV_DEG, AZIM_DEG)
    mesh = build_torus_mesh(cam, nu=96, nv=48)

    # Panel A coordinate circles:
    # - Toroidal circle phi1 at top-outer rim (phi2 = +0.55 rad, super clear from elev=32 deg!)
    # - Poloidal circle phi2 at front-right (phi1 = -0.45 rad, faces camera cleanly!)
    phi2_toroidal = 0.55
    phi1_poloidal = -0.45
    circ_phi1 = precompute_circle(cam, "phi2", phi2_toroidal, n_pts=360)
    circ_phi2 = precompute_circle(cam, "phi1", phi1_poloidal, n_pts=300)
    p_int, _ = torus_point_and_normal(np.array([phi1_poloidal]), np.array([phi2_toroidal]))
    ix, iy, _ = project_pts(p_int, cam)

    # Exact target points directly on the front-visible arcs of circ_phi1 and circ_phi2 for labels
    p_lbl1, _ = torus_point_and_normal(np.array([4.05]), np.array([phi2_toroidal]))
    l1x, l1y, _ = project_pts(p_lbl1, cam)
    p_lbl2, _ = torus_point_and_normal(np.array([phi1_poloidal]), np.array([1.72]))
    l2x, l2y, _ = project_pts(p_lbl2, cam)

    # Panel B (periodic 2:3) and Panel C (quasiperiodic sqrt(2))
    # Start both trajectories on the front-facing outer side (phi1_0 = -0.45, phi2_0 = 0.25)
    # so the starting point and closure are unmistakably visible on the front of the torus!
    phi1_start = -0.45
    phi2_start = 0.25
    traj_b = precompute_curve(OMEGA_B[0], OMEGA_B[1], cam, T_SIM_MAX, N_SAMPLES, phi1_start, phi2_start)
    traj_c = precompute_curve(OMEGA_C[0], OMEGA_C[1], cam, T_SIM_MAX, N_SAMPLES, phi1_start, phi2_start)

    # Verify exact closure of Panel B at t = 2*pi and non-closure of Panel C
    idx_close = int(np.argmin(np.abs(traj_b["t"] - 2.0 * np.pi)))
    p_b0, _ = torus_point_and_normal(np.array([phi1_start]), np.array([phi2_start]))
    p_b1, _ = torus_point_and_normal(
        np.array([phi1_start + OMEGA_B[0] * 2.0 * np.pi]),
        np.array([phi2_start + OMEGA_B[1] * 2.0 * np.pi]),
    )
    assert np.linalg.norm(p_b1 - p_b0) < 1e-12, "Panel B orbit did not close at t = 2*pi"
    p_c1, _ = torus_point_and_normal(
        np.array([phi1_start + OMEGA_C[0] * 2.0 * np.pi]),
        np.array([phi2_start + OMEGA_C[1] * 2.0 * np.pi]),
    )
    assert np.linalg.norm(p_c1 - p_b0) > 0.5, "Panel C orbit unexpectedly close to closure"

    return {
        "cam": cam,
        "mesh": mesh,
        "circ_phi1": circ_phi1,
        "circ_phi2": circ_phi2,
        "p_intersect": (float(ix[0]), float(iy[0])),
        "p_lbl_phi1": (float(l1x[0]), float(l1y[0])),
        "p_lbl_phi2": (float(l2x[0]), float(l2y[0])),
        "traj_b": traj_b,
        "traj_c": traj_c,
        "idx_b_close": idx_close,
    }


def draw_torus_back(ax, mesh):
    """Draw back translucent shell of the torus."""
    pc_back = PolyCollection(
        mesh["back_polys"],
        facecolors=mesh["back_rgba"],
        edgecolors=mesh["back_rgba"],
        linewidths=0.35,
        antialiaseds=True,
        zorder=2,
    )
    ax.add_collection(pc_back)


def draw_torus_front(ax, mesh):
    """Draw front translucent shell and subtle coordinate wireframe of the torus."""
    pc_front = PolyCollection(
        mesh["front_polys"],
        facecolors=mesh["front_rgba"],
        edgecolors=mesh["front_rgba"],
        linewidths=0.35,
        antialiaseds=True,
        zorder=5,
    )
    ax.add_collection(pc_front)

    lc_grid = LineCollection(
        mesh["grid_front_segs"],
        colors="#64748b",
        linewidths=0.55,
        alpha=0.22,
        zorder=6,
    )
    ax.add_collection(lc_grid)


def split_front_back_segments(x2, y2, vis, end_idx):
    """Split a trajectory up to end_idx into contiguous back and front LineCollection segments."""
    if end_idx < 1:
        return [], []
    xs = x2[:end_idx + 1]
    ys = y2[:end_idx + 1]
    vs = vis[:end_idx + 1]
    pts = np.column_stack([xs, ys])
    segs = np.stack([pts[:-1], pts[1:]], axis=1)
    is_front = vs[:-1] & vs[1:]
    return segs[~is_front], segs[is_front]


def draw_split_circle(ax, circ, color, lw_front=3.0, lw_back=1.7, alpha_back=0.30):
    """Draw a Panel A coordinate circle with back/front depth separation."""
    back_s, front_s = split_front_back_segments(circ["x2"], circ["y2"], circ["vis"], len(circ["x2"]) - 1)
    if len(back_s):
        ax.add_collection(LineCollection(back_s, colors=color, linewidths=lw_back,
                                         linestyles="--", alpha=alpha_back, zorder=3))
    if len(front_s):
        ax.add_collection(LineCollection(front_s, colors=color, linewidths=lw_front,
                                         alpha=0.95, capstyle="round", zorder=8))


def draw_arrow_on_circle(ax, circ, target_ang, color, scale=17.0, zorder=10):
    """Place a crisp tangent arrowhead on a Panel A coordinate circle at target_ang."""
    idx = int(np.argmin(np.abs(circ["ang"] - target_ang)))
    i0 = max(0, idx - 3)
    i1 = min(len(circ["x2"]) - 1, idx + 3)
    ax.annotate(
        "",
        xy=(circ["x2"][i1], circ["y2"][i1]),
        xytext=(circ["x2"][i0], circ["y2"][i0]),
        arrowprops=dict(arrowstyle="-|>", mutation_scale=scale, color=color, lw=0.0, shrinkA=0, shrinkB=0),
        zorder=zorder,
    )


def evaluate_timeline(t_anim: float):
    """Map animation wall time (s) to simulation time t_sim and dynamic alpha."""
    if t_anim <= T_EVOLVE_END:
        frac = t_anim / T_EVOLVE_END
        t_sim = frac * T_SIM_MAX
        alpha_dyn = 1.0
    elif t_anim <= T_HOLD_END:
        t_sim = T_SIM_MAX
        alpha_dyn = 1.0
    else:
        fade = (t_anim - T_HOLD_END) / (TOTAL_DURATION - T_HOLD_END)
        t_sim = T_SIM_MAX
        alpha_dyn = max(0.0, 1.0 - fade)
    return {"t_sim": t_sim, "alpha_dyn": alpha_dyn}


def render_frame_to_path(state: dict, scene: dict, output_path: Path, dpi: int = 100):
    """Render one complete 3-panel frame at 19.2 x 10.0 in."""
    fig_w, fig_h = 19.2, 10.0
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor="#ffffff")
    halo = [pe.withStroke(linewidth=3.8, foreground="#ffffff", alpha=0.96)]

    # -------------------------------------------------------------------------
    # Global Title & Subtitle (matching kam_invariant_tori_picture.png hierarchy)
    # -------------------------------------------------------------------------
    fig.text(
        0.50,
        0.964,
        "From Integrability to Motion on Invariant Tori",
        fontsize=28.0,
        weight="bold",
        color=NAVY,
        ha="center",
        va="center",
    )
    fig.text(
        0.50,
        0.922,
        "Action–angle coordinates on a 2D invariant torus (visualized in 3D): periodic vs. quasiperiodic trajectories",
        fontsize=19.0,
        style="italic",
        weight="normal",
        color=DARK_SLATE,
        ha="center",
        va="center",
    )

    ax_bg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=0)
    ax_bg.set_xlim(0.0, 1.0)
    ax_bg.set_ylim(0.0, 1.0)
    ax_bg.axis("off")

    # -------------------------------------------------------------------------
    # Three Equal-Width Parallel Panel Cards (A, B, C)
    # -------------------------------------------------------------------------
    y_card = 0.016
    h_card = 0.878
    x1, w1 = 0.008, 0.319
    x2, w2 = 0.3405, 0.319
    x3, w3 = 0.673, 0.319
    hbar_h = 0.134
    badge_y = y_card + h_card - hbar_h / 2.0

    panels_spec = [
        (
            x1, w1, "A",
            "Invariant torus",
            r"Action–angle ($\boldsymbol{I_1, I_2, \varphi_1, \varphi_2}$)",
            BLUE_ACCENT, BLUE_LIGHT, BLUE_BORDER,
        ),
        (
            x2, w2, "B",
            "Periodic motion",
            "Rational ratio (commensurable)",
            ORANGE_ACCENT, ORANGE_LIGHT, ORANGE_BORDER,
        ),
        (
            x3, w3, "C",
            "Quasiperiodic motion",
            "Irrational ratio (incommensurable)",
            TEAL_ACCENT, TEAL_LIGHT, TEAL_BORDER,
        ),
    ]

    for px, pw, letter, title, subtitle, acc_color, bg_tint, bdr_color in panels_spec:
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px, y_card), pw, h_card,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.4, zorder=1,
        ))
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px, y_card + h_card - hbar_h), pw, hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=bg_tint, edgecolor=bdr_color, linewidth=1.2, zorder=2,
        ))

        badge_x = px + 0.020
        r_x = 0.0135
        r_y = r_x * (fig_w / fig_h)
        ax_bg.add_patch(patches.Ellipse(
            (badge_x, badge_y), width=2.0 * r_x, height=2.0 * r_y,
            facecolor=acc_color, edgecolor="none", zorder=3,
        ))
        ax_bg.text(
            badge_x, badge_y - 0.0005, letter,
            fontsize=19.5, weight="bold", color="#ffffff",
            ha="center", va="center", zorder=4,
        )

        text_x = badge_x + 0.019
        ax_bg.text(
            text_x, badge_y + 0.024, title,
            fontsize=21.5, weight="bold", color=NAVY, va="center", zorder=4,
        )
        ax_bg.text(
            text_x, badge_y - 0.024, subtitle,
            fontsize=17.4, weight="bold", color=MUTED_SLATE, va="center", zorder=4,
        )

    # Plot & aligned bottom explanatory box geometry (matching kam_invariant_tori_picture.png)
    y_box = 0.028
    h_box = 0.136
    y_plot = y_box + h_box + 0.016
    h_plot = (y_card + h_card - hbar_h) - y_plot - 0.015
    w_aligned = w1 - 0.020  # cleanly fills each card horizontally with symmetric 0.010 margins

    bottom_texts = [
        (
            x1, w1, BLUE_BORDER,
            "Constant actions I₁, I₂ identify the torus;\n"
            "angles φ₁, φ₂ specify position and advance\n"
            "uniformly at frequencies ω₁(I), ω₂(I).",
        ),
        (
            x2, w2, ORANGE_BORDER,
            "When ω₁/ω₂ is rational (here 2/3), the\n"
            "trajectory closes after 2 toroidal and\n"
            "3 poloidal turns, repeating identically.",
        ),
        (
            x3, w3, TEAL_BORDER,
            "When ω₁/ω₂ is irrational (here √2), the\n"
            "trajectory never closes and winds densely\n"
            "across the torus without repeating.",
        ),
    ]

    for px, pw, bdr_col, desc in bottom_texts:
        bx = px + (pw - w_aligned) / 2.0
        ax_bg.add_patch(patches.FancyBboxPatch(
            (bx, y_box), w_aligned, h_box,
            boxstyle="round,pad=0.0,rounding_size=0.013",
            facecolor=BG_BOX, edgecolor=bdr_col, linewidth=1.35, zorder=3,
        ))
        ax_bg.text(
            bx + w_aligned / 2.0, y_box + h_box / 2.0,
            desc,
            fontsize=15.2, weight="bold", color=DARK_SLATE,
            ha="center", va="center", linespacing=1.20, zorder=4,
        )

    # Helper to create identical framed 3D-projection axes in each panel
    def make_torus_ax(px, pw):
        ax_left = px + (pw - w_aligned) / 2.0
        ax = fig.add_axes([ax_left, y_plot, w_aligned, h_plot], zorder=5)
        ax.set_facecolor("#ffffff")
        # Physical aspect ratio of plot box:
        box_aspect = (w_aligned * fig_w) / (h_plot * fig_h)
        # Keep torus nicely centered with generous top/bottom bands for large readable pills
        x_half = 3.32
        y_half = x_half / box_aspect
        ax.set_xlim(-x_half, x_half)
        ax.set_ylim(-y_half - 0.14, y_half - 0.14)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER_CARD)
            sp.set_linewidth(1.2)
        return ax

    mesh = scene["mesh"]
    t_sim = state["t_sim"]
    alpha_dyn = state["alpha_dyn"]

    # =========================================================================
    # PANEL A: Static Invariant Torus + Action-Angle Coordinates
    # =========================================================================
    axA = make_torus_ax(x1, w1)
    draw_torus_back(axA, mesh)
    draw_torus_front(axA, mesh)

    draw_split_circle(axA, scene["circ_phi1"], BLUE_ACCENT, lw_front=3.2, lw_back=1.7)
    draw_split_circle(axA, scene["circ_phi2"], TEAL_ACCENT, lw_front=3.2, lw_back=1.7)
    # Tangential directional arrows on visible front sections
    draw_arrow_on_circle(axA, scene["circ_phi1"], 4.45, BLUE_ACCENT, scale=18.0)
    draw_arrow_on_circle(axA, scene["circ_phi2"], 1.35, TEAL_ACCENT, scale=18.0)

    # Intersection point (varphi_1, varphi_2)
    ix, iy = scene["p_intersect"]
    axA.scatter([ix], [iy], s=95, facecolor=NAVY, edgecolor="#ffffff", linewidth=2.0, zorder=11)

    # Top-left math pill: constant actions (not radii!)
    axA.text(
        -3.12, 2.84,
        r"$\boldsymbol{I_1,\, I_2 = \mathrm{const.}}$  (identifies torus)",
        fontsize=18.5, weight="bold", color=NAVY,
        ha="left", va="top",
        bbox=dict(boxstyle="round,pad=0.25", facecolor=EQ_BG, edgecolor=EQ_BORDER, linewidth=1.15, alpha=0.96),
        zorder=12,
    )

    # Clean labels pointing directly to exact points on circ_phi1, circ_phi2, and intersection
    axA.annotate(
        r"$\boldsymbol{\varphi_1}$ (toroidal)",
        xy=scene["p_lbl_phi1"],
        xytext=(-3.12, -2.06),
        fontsize=18.2, weight="bold", color=BLUE_DARK,
        ha="left", va="center", path_effects=halo,
        bbox=dict(boxstyle="round,pad=0.20", facecolor=BLUE_LIGHT, edgecolor=BLUE_BORDER, linewidth=1.15, alpha=0.96),
        arrowprops=dict(arrowstyle="-|>", mutation_scale=14.0, color=BLUE_ACCENT, lw=1.8),
        zorder=12,
    )
    axA.annotate(
        r"$\boldsymbol{\varphi_2}$ (poloidal)",
        xy=scene["p_lbl_phi2"],
        xytext=(3.12, 2.04),
        fontsize=18.2, weight="bold", color=TEAL_DARK,
        ha="right", va="center", path_effects=halo,
        bbox=dict(boxstyle="round,pad=0.20", facecolor=TEAL_LIGHT, edgecolor=TEAL_BORDER, linewidth=1.15, alpha=0.96),
        arrowprops=dict(arrowstyle="-|>", mutation_scale=14.0, color=TEAL_ACCENT, lw=1.8),
        zorder=12,
    )
    axA.annotate(
        r"$(\boldsymbol{\varphi_1, \varphi_2})$",
        xy=(ix, iy),
        xytext=(3.10, -2.06),
        fontsize=18.6, weight="bold", color=NAVY,
        ha="right", va="center", path_effects=halo,
        bbox=dict(boxstyle="round,pad=0.18", facecolor="#ffffff", edgecolor="#94a3b8", linewidth=1.1, alpha=0.96),
        arrowprops=dict(arrowstyle="-|>", mutation_scale=13.0, color=SLATE, lw=1.55),
        zorder=12,
    )

    # Discreet bottom note inside Panel A clarifying 2D manifold in 4D phase space
    axA.text(
        0.0, -2.90,
        "3D view of a 2D invariant manifold\nembedded in 4D phase space",
        fontsize=15.4, style="italic", weight="bold", color=MUTED_SLATE,
        ha="center", va="center", linespacing=1.22, path_effects=halo, zorder=12,
    )

    # =========================================================================
    # PANEL B: Animated Periodic Orbit (omega_1 / omega_2 = 2/3)
    # =========================================================================
    axB = make_torus_ax(x2, w2)
    draw_torus_back(axB, mesh)
    draw_torus_front(axB, mesh)

    tb = scene["traj_b"]
    idx_b_now = int(np.searchsorted(tb["t"], t_sim, side="right")) - 1
    idx_b_now = max(0, min(idx_b_now, len(tb["t"]) - 1))
    # Draw traced path up to min(t_sim, 2*pi) so after closure it stays crisp (no overdraw thickening!)
    idx_b_draw = min(idx_b_now, scene["idx_b_close"])
    is_closed = t_sim >= (2.0 * np.pi - 1e-3)

    if alpha_dyn > 0.01:
        b_back, b_front = split_front_back_segments(tb["x2"], tb["y2"], tb["vis"], idx_b_draw)
        if len(b_back):
            axB.add_collection(LineCollection(
                b_back, colors=ORANGE_ACCENT, linewidths=1.9,
                alpha=0.28 * alpha_dyn, capstyle="round", zorder=3,
            ))
        if len(b_front):
            axB.add_collection(LineCollection(
                b_front, colors=ORANGE_ACCENT, linewidths=3.1,
                alpha=0.95 * alpha_dyn, capstyle="round", zorder=8,
            ))

        # Starting point ring marker
        axB.scatter(
            [tb["x2"][0]], [tb["y2"][0]], s=105,
            facecolor="#ffffff", edgecolor=ORANGE_DARK, linewidth=2.2,
            alpha=0.95 * alpha_dyn, zorder=10,
        )

        # Moving phase point (bright in front, softly muted behind torus)
        pt_vis_b = bool(tb["vis"][idx_b_now])
        axB.scatter(
            [tb["x2"][idx_b_now]], [tb["y2"][idx_b_now]],
            s=115 if pt_vis_b else 75,
            facecolor=ORANGE_ACCENT, edgecolor="#ffffff", linewidth=2.0 if pt_vis_b else 1.2,
            alpha=(0.98 if pt_vis_b else 0.40) * alpha_dyn,
            zorder=11 if pt_vis_b else 4,
        )

    # Top-left math pill
    axB.text(
        -3.12, 2.84,
        r"$\boldsymbol{\omega_1 / \omega_2 = 2/3}$",
        fontsize=20.0, weight="bold", color=ORANGE_DARK,
        ha="left", va="top",
        bbox=dict(boxstyle="round,pad=0.24", facecolor=ORANGE_LIGHT, edgecolor=ORANGE_BORDER, linewidth=1.2, alpha=0.96),
        zorder=12,
    )

    # Top-right live status pill
    status_b = "Orbit closed — retracing" if is_closed else "Tracing periodic orbit..."
    axB.text(
        3.12, 2.84,
        status_b,
        fontsize=16.0, weight="bold", color=ORANGE_DARK if is_closed else MUTED_SLATE,
        ha="right", va="top",
        bbox=dict(
            boxstyle="round,pad=0.24",
            facecolor=ORANGE_LIGHT if is_closed else "#ffffff",
            edgecolor=ORANGE_BORDER if is_closed else BORDER_CARD,
            linewidth=1.15, alpha=0.96,
        ),
        zorder=12,
    )

    # Bottom turns indicator distinguishing cumulative turns from the first 2:3 closure
    turns_b1 = (OMEGA_B[0] * t_sim) / (2.0 * np.pi)
    turns_b2 = (OMEGA_B[1] * t_sim) / (2.0 * np.pi)
    cycles_b = t_sim / (2.0 * np.pi)
    axB.text(
        0.0, -2.67,
        f"Total turns:  Δφ₁/2π = {turns_b1:4.1f} · Δφ₂/2π = {turns_b2:4.1f}",
        fontsize=15.6, weight="bold", color=SLATE,
        ha="center", va="center", path_effects=halo, zorder=12,
    )
    sub_b = (
        f"Closed at 2:3 turns · retracing (cycle {cycles_b:3.1f})"
        if is_closed
        else "First closure at 2:3 turns · tracing cycle 1"
    )
    axB.text(
        0.0, -3.09,
        sub_b,
        fontsize=14.6, style="italic", weight="bold",
        color=ORANGE_DARK if is_closed else MUTED_SLATE,
        ha="center", va="center", path_effects=halo, zorder=12,
    )

    # =========================================================================
    # PANEL C: Animated Quasiperiodic Orbit (omega_1 / omega_2 = sqrt(2))
    # =========================================================================
    axC = make_torus_ax(x3, w3)
    draw_torus_back(axC, mesh)
    draw_torus_front(axC, mesh)

    tc = scene["traj_c"]
    idx_c_now = int(np.searchsorted(tc["t"], t_sim, side="right")) - 1
    idx_c_now = max(0, min(idx_c_now, len(tc["t"]) - 1))

    if alpha_dyn > 0.01:
        c_back, c_front = split_front_back_segments(tc["x2"], tc["y2"], tc["vis"], idx_c_now)
        if len(c_back):
            axC.add_collection(LineCollection(
                c_back, colors=TEAL_ACCENT, linewidths=1.30,
                alpha=0.20 * alpha_dyn, capstyle="round", zorder=3,
            ))
        if len(c_front):
            axC.add_collection(LineCollection(
                c_front, colors=TEAL_ACCENT, linewidths=2.00,
                alpha=0.88 * alpha_dyn, capstyle="round", zorder=8,
            ))

        # Starting point ring marker
        axC.scatter(
            [tc["x2"][0]], [tc["y2"][0]], s=105,
            facecolor="#ffffff", edgecolor=TEAL_DARK, linewidth=2.2,
            alpha=0.95 * alpha_dyn, zorder=10,
        )

        # Moving phase point
        pt_vis_c = bool(tc["vis"][idx_c_now])
        axC.scatter(
            [tc["x2"][idx_c_now]], [tc["y2"][idx_c_now]],
            s=115 if pt_vis_c else 75,
            facecolor=TEAL_ACCENT, edgecolor="#ffffff", linewidth=2.0 if pt_vis_c else 1.2,
            alpha=(0.98 if pt_vis_c else 0.40) * alpha_dyn,
            zorder=11 if pt_vis_c else 4,
        )

    # Top-left math pill
    axC.text(
        -3.12, 2.84,
        r"$\boldsymbol{\omega_1 / \omega_2 = \sqrt{2}}$",
        fontsize=20.0, weight="bold", color=TEAL_DARK,
        ha="left", va="top",
        bbox=dict(boxstyle="round,pad=0.24", facecolor=TEAL_LIGHT, edgecolor=TEAL_BORDER, linewidth=1.2, alpha=0.96),
        zorder=12,
    )

    # Top-right live status pill (two balanced lines so text stays large with generous separation)
    axC.text(
        3.12, 2.84,
        "Never closes —\ndensely winds over time",
        fontsize=15.8, weight="bold", color=TEAL_DARK,
        ha="right", va="top", multialignment="center", linespacing=1.12,
        bbox=dict(boxstyle="round,pad=0.22", facecolor=TEAL_LIGHT, edgecolor=TEAL_BORDER, linewidth=1.15, alpha=0.96),
        zorder=12,
    )

    turns_c1 = (OMEGA_C[0] * t_sim) / (2.0 * np.pi)
    turns_c2 = (OMEGA_C[1] * t_sim) / (2.0 * np.pi)
    axC.text(
        0.0, -2.67,
        f"Total turns:  Δφ₁/2π = {turns_c1:4.1f} · Δφ₂/2π = {turns_c2:4.1f}",
        fontsize=15.6, weight="bold", color=SLATE,
        ha="center", va="center", path_effects=halo, zorder=12,
    )
    axC.text(
        0.0, -3.09,
        "Non-repeating · trajectory dense as t → ∞",
        fontsize=14.6, style="italic", weight="bold", color=TEAL_DARK,
        ha="center", va="center", path_effects=halo, zorder=12,
    )

    fig.savefig(output_path, dpi=dpi, facecolor="#ffffff")
    plt.close(fig)


def init_worker(scene):
    global G_SCENE
    G_SCENE = scene


def render_single_frame(frame_idx: int):
    t_anim = frame_idx / FPS_MASTER
    st = evaluate_timeline(t_anim)
    out_p = FRAMES_DIR / f"frame_{frame_idx:04d}.png"
    render_frame_to_path(st, G_SCENE, out_p, dpi=100)
    return frame_idx


def generate_preview_frames(scene):
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    previews = [
        ("torus_preview_01_early.png", 1.80),
        ("torus_preview_02_closure.png", 2.70),
        ("torus_preview_03_mid.png", 8.50),
        ("torus_preview_04_final.png", 15.00),
    ]
    for fname, t_val in previews:
        st = evaluate_timeline(t_val)
        out_p = SCRATCH_DIR / fname
        render_frame_to_path(st, scene, out_p, dpi=100)
        print(f"  [Preview] {out_p} (t_anim={t_val:.2f}s -> t_sim={st['t_sim']:.2f})")


def main():
    scene = build_scene_data()

    if "--preview-only" in sys.argv:
        generate_preview_frames(scene)
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"--- Rendering {N_TOTAL_FRAMES} frames ({TOTAL_DURATION:.1f} s @ {FPS_MASTER} fps, 1920x1000) ---")
    t0 = time.time()
    num_cpus = max(1, min(14, multiprocessing.cpu_count() - 2))
    print(f"  Using {num_cpus} parallel workers...")

    with multiprocessing.Pool(processes=num_cpus, initializer=init_worker, initargs=(scene,)) as pool:
        for idx in pool.imap_unordered(render_single_frame, range(N_TOTAL_FRAMES), chunksize=4):
            if (idx + 1) % 80 == 0 or idx == N_TOTAL_FRAMES - 1:
                print(f"    Completed frame {idx + 1:3d} / {N_TOTAL_FRAMES}")

    print(f"  Frame rendering finished in {time.time() - t0:.1f} s")

    # 1. Master MP4 (24 fps, 1920x1000)
    mp4_out = OUTPUT_DIR / "integrable_torus_motion.mp4"
    print(f"--- Encoding Master MP4: {mp4_out} ---")
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS_MASTER),
        "-i", str(FRAMES_DIR / "frame_%04d.png"),
        "-c:v", "libx264", "-profile:v", "high", "-crf", "18",
        "-preset", "slow", "-pix_fmt", "yuv420p",
        str(mp4_out),
    ], check=True)
    print(f"  [OK] Master MP4 saved: {mp4_out.stat().st_size / (1024 * 1024):.2f} MB")

    # 2. Animated Web GIF (14 fps, 1440px, custom 256-color palette, loop=0)
    gif_out = OUTPUT_DIR / "integrable_torus_motion.gif"
    print(f"--- Encoding Animated GIF: {gif_out} ---")
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS_MASTER),
        "-i", str(FRAMES_DIR / "frame_%04d.png"),
        "-vf", "fps=14,scale=1440:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256:stats_mode=full[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4",
        "-loop", "0",
        str(gif_out),
    ], check=True)
    print(f"  [OK] Animated GIF saved: {gif_out.stat().st_size / (1024 * 1024):.2f} MB")

    # 3. Poster PNG (final overview frame at t_sim = 10*pi)
    poster_idx = int(round(T_EVOLVE_END * FPS_MASTER))
    poster_out = OUTPUT_DIR / "integrable_torus_motion.png"
    shutil.copyfile(FRAMES_DIR / f"frame_{poster_idx:04d}.png", poster_out)
    print(f"  [OK] Poster PNG saved: {poster_out} ({poster_out.stat().st_size / (1024 * 1024):.2f} MB)")

    # Clean up temporary frame directory
    shutil.rmtree(FRAMES_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()
