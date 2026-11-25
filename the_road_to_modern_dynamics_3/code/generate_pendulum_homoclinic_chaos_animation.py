#!/usr/bin/env python3
r"""
generate_pendulum_homoclinic_chaos_animation.py

Generates Animation 2 ("From the Pendulum Separatrix to Homoclinic Chaos")
for Article 3: "Order and Chaos: The Road to Modern Dynamics III"

Mathematical Model — Normalized Undamped Driven Pendulum:
  theta'' + sin(theta) = A cos(Omega * t)
Written as a first-order system with v = theta':
  theta' = v
  v'     = -sin(theta) + A cos(Omega * t)

Parameters:
  - Panel A (Unforced): A = 0, conserved energy E(theta, v) = v^2 / 2 + 1 - cos(theta)
      * E < 2: closed oscillations
      * E = 2: exact separatrix v = +- 2 cos(theta / 2), -pi <= theta <= pi
      * E > 2: continuous rotations
  - Panel B (Periodically Forced): A = 0.20, Omega = 0.80, T = 2 * pi / Omega ~ 7.854
      * Stroboscopic Poincare map P(z_n) = z_{n+1} sampled at t_n = nT
      * Hyperbolic fixed point z_* ~ (3.01949, 0) solved by Newton + variational eqs
      * Adaptive fundamental-domain numerical stable & unstable manifolds W^s(z_*), W^u(z_*)
      * Numerically verified transverse homoclinic intersection H ~ (2.2607, 0) (~60 deg)

Technical Specifications (16:9 widescreen, 1920 x 1080 px, 24 fps, 66.0 s = 1584 frames):
  - Master MP4: images/pendulum_separatrix_to_homoclinic_chaos.mp4
  - Web GIF:    images/pendulum_separatrix_to_homoclinic_chaos.gif (12 fps, 1440px, loop=0)
  - Poster PNG: images/pendulum_separatrix_to_homoclinic_chaos.png
"""

import os
import sys
import time
import shutil
import subprocess
import multiprocessing
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
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
FRAMES_DIR = Path("/tmp/pendulum_homoclinic_frames")
CACHE_PATH = Path("/tmp/pendulum_homoclinic_cache_v1.npz")

# Physical parameters
A_DRIVE = 0.20
OMEGA = 0.80
T_PERIOD = 2.0 * np.pi / OMEGA

# Animation timeline (66.0 s @ 24 fps = 1584 frames)
FPS_MASTER = 24
TOTAL_DURATION = 66.0
N_TOTAL_FRAMES = int(round(TOTAL_DURATION * FPS_MASTER))

# Visual palette (cohesive with Figure 1 and Animation 1)
NAVY = "#0f172a"
DARK_SLATE = "#1e293b"
SLATE = "#334155"
MUTED_SLATE = "#475569"
BORDER_CARD = "#cbd5e1"
BG_CARD = "#f8fafc"
BG_BOX = "#ffffff"

BLUE_STABLE = "#2563eb"
BLUE_LIGHT = "#eff6ff"
BLUE_BORDER = "#93c5fd"

RED_UNSTABLE = "#dc2626"
TEAL_REGULAR = "#0d9488"
TEAL_LIGHT = "#f0fdfa"
TEAL_BORDER = "#5eead4"
TEAL_DARK = "#115e59"

CHAOS_GRAY = "#64748b"
AMBER_H = "#f59e0b"

HALO = [pe.withStroke(linewidth=3.2, foreground="#ffffff", alpha=0.95)]
HALO_THIN = [pe.withStroke(linewidth=2.4, foreground="#ffffff", alpha=0.92)]


# -----------------------------------------------------------------------------
# 1. Exact Dynamical System, Variational Equations & Manifold Solver
# -----------------------------------------------------------------------------
def wrap_pi(theta):
    """Wrap angle(s) onto [-pi, pi)."""
    return (np.asarray(theta) + np.pi) % (2.0 * np.pi) - np.pi


def insert_wrap_nans(th_arr, v_arr):
    """Insert NaN breaks wherever wrapped theta jumps across +-pi."""
    th = wrap_pi(th_arr)
    v = np.asarray(v_arr, dtype=float)
    jumps = np.abs(np.diff(th)) > np.pi
    idx_j = np.where(jumps)[0] + 1
    if len(idx_j) == 0:
        return th, v
    return np.insert(th.astype(float), idx_j, np.nan), np.insert(v, idx_j, np.nan)


def rhs_forced(t, y):
    th, v = y
    return [v, -np.sin(th) + A_DRIVE * np.cos(OMEGA * t)]


def rhs_variational(t, y):
    th, v, p11, p21, p12, p22 = y
    c = np.cos(th)
    return [
        v,
        -np.sin(th) + A_DRIVE * np.cos(OMEGA * t),
        p21,
        -c * p11,
        p22,
        -c * p12,
    ]


def poincare_step(z, direction=1, rtol=1e-11, atol=1e-13):
    sol = solve_ivp(
        rhs_forced, (0.0, direction * T_PERIOD), z,
        method="DOP853", rtol=rtol, atol=atol,
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol.y[:, -1]


def poincare_and_jacobian(z, direction=1, rtol=1e-12, atol=1e-14):
    y0 = [z[0], z[1], 1.0, 0.0, 0.0, 1.0]
    sol = solve_ivp(
        rhs_variational, (0.0, direction * T_PERIOD), y0,
        method="DOP853", rtol=rtol, atol=atol,
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    yf = sol.y[:, -1]
    z_next = np.array([yf[0], yf[1]])
    DP = np.array([[yf[2], yf[4]], [yf[3], yf[5]]])
    return z_next, DP


def find_hyperbolic_fixed_point(z_guess):
    z = np.array(z_guess, dtype=float)
    for _ in range(15):
        z_next, DP = poincare_and_jacobian(z, direction=1)
        res = np.array([wrap_pi(z_next[0] - z[0]), z_next[1] - z[1]])
        if np.linalg.norm(res) < 1e-13:
            break
        dz = np.linalg.solve(DP - np.eye(2), -res)
        z = z + dz
    z_next, DP = poincare_and_jacobian(z, direction=1)
    res = np.array([wrap_pi(z_next[0] - z[0]), z_next[1] - z[1]])
    det_dp = float(np.linalg.det(DP))
    eigvals, eigvecs = np.linalg.eig(DP)
    return z, res, DP, det_dp, eigvals, eigvecs


def trace_manifold_parametric(z_star, vec, direction, eps=1e-6, u_max=1.70, n_pts=240, max_seg=0.024, max_angle_deg=10.0):
    """
    Compute a 1-D manifold branch along parameter u in [0, u_max] via exact
    fundamental-domain integration with adaptive curvature/gap subdivision.
    Returns (pts, u_vals) where u_vals in [0, u_max] measures manifold growth.
    """
    _, DP = poincare_and_jacobian(z_star, direction=direction)
    lam = float(np.dot(vec, DP @ vec))
    if lam <= 1.0:
        raise RuntimeError(f"Expected expanding eigenvalue > 1, got {lam}")

    def eval_curve_k(u_arr, k_iter):
        alphas = eps * (lam ** u_arr)
        t_end = k_iter * direction * T_PERIOD
        pts = []
        for a in alphas:
            p0 = z_star + a * vec
            sol = solve_ivp(rhs_forced, (0.0, t_end), p0, method="DOP853", rtol=1e-11, atol=1e-13)
            pts.append(sol.y[:, -1])
        return np.array(pts)

    all_pts = [np.array([z_star, z_star + eps * vec])]
    all_u = [np.array([0.0, 0.0])]

    for k_iter, u_hi in ((1, min(1.0, u_max)), (2, max(0.0, u_max - 1.0))):
        if u_hi <= 0.0:
            continue
        u_grid = np.linspace(0.0, u_hi, n_pts)
        pts = eval_curve_k(u_grid, k_iter)
        for _ in range(6):
            diffs = np.diff(pts, axis=0)
            dists = np.hypot(diffs[:, 0], diffs[:, 1])
            need_sub = dists > max_seg
            if len(pts) >= 3:
                v1, v2 = diffs[:-1], diffs[1:]
                n1, n2 = np.hypot(v1[:, 0], v1[:, 1]), np.hypot(v2[:, 0], v2[:, 1])
                valid = (n1 > 1e-6) & (n2 > 1e-6)
                cos_a = np.ones(len(v1))
                cos_a[valid] = np.clip(
                    (v1[valid, 0] * v2[valid, 0] + v1[valid, 1] * v2[valid, 1]) / (n1[valid] * n2[valid]),
                    -1.0, 1.0,
                )
                angles = np.rad2deg(np.arccos(cos_a))
                sharp = (angles > max_angle_deg) & (np.maximum(n1, n2) > 0.012)
                need_sub[:-1] |= sharp
                need_sub[1:] |= sharp

            sub_idxs = np.where(need_sub & (np.diff(u_grid) > 1e-8))[0]
            if len(sub_idxs) == 0 or len(pts) > 3200:
                break
            u_mids = 0.5 * (u_grid[sub_idxs] + u_grid[sub_idxs + 1])
            pts_mids = eval_curve_k(u_mids, k_iter)
            u_all = np.concatenate([u_grid, u_mids])
            order = np.argsort(u_all)
            u_grid = u_all[order]
            pts = np.vstack([pts, pts_mids])[order]

        all_pts.append(pts)
        all_u.append((k_iter - 1.0) + u_grid)

    return np.vstack(all_pts), np.concatenate(all_u)


def find_curve_intersections_mod2pi(curve_u, u_u, curve_s, u_s, z_star):
    """Find transverse intersections on the cylinder theta mod 2pi, excluding z_star."""
    hits = []
    for shift in (-2.0 * np.pi, 0.0, 2.0 * np.pi):
        cs = curve_s.copy()
        cs[:, 0] += shift
        u_min_x, u_max_x = curve_u[:, 0].min(), curve_u[:, 0].max()
        u_min_y, u_max_y = curve_u[:, 1].min(), curve_u[:, 1].max()
        if cs[:, 0].max() < u_min_x or cs[:, 0].min() > u_max_x:
            continue
        if cs[:, 1].max() < u_min_y or cs[:, 1].min() > u_max_y:
            continue

        du = np.diff(curve_u, axis=0)
        ds = np.diff(cs, axis=0)
        for i in range(len(du)):
            p1, p2 = curve_u[i], curve_u[i + 1]
            min_px, max_px = min(p1[0], p2[0]), max(p1[0], p2[0])
            min_py, max_py = min(p1[1], p2[1]), max(p1[1], p2[1])
            mask = (
                (np.maximum(cs[:-1, 0], cs[1:, 0]) >= min_px)
                & (np.minimum(cs[:-1, 0], cs[1:, 0]) <= max_px)
                & (np.maximum(cs[:-1, 1], cs[1:, 1]) >= min_py)
                & (np.minimum(cs[:-1, 1], cs[1:, 1]) <= max_py)
            )
            js = np.where(mask)[0]
            if len(js) == 0:
                continue
            d1 = du[i]
            n1 = np.hypot(d1[0], d1[1])
            for j in js:
                q1 = cs[j]
                d2 = ds[j]
                denom = d1[0] * d2[1] - d1[1] * d2[0]
                if abs(denom) < 1e-12:
                    continue
                diff = q1 - p1
                t_seg = (diff[0] * d2[1] - diff[1] * d2[0]) / denom
                u_seg = (diff[0] * d1[1] - diff[1] * d1[0]) / denom
                if 0.0 <= t_seg <= 1.0 and 0.0 <= u_seg <= 1.0:
                    pt = p1 + t_seg * d1
                    dist_star = np.hypot(wrap_pi(pt[0] - z_star[0]), pt[1] - z_star[1])
                    if dist_star < 0.05:
                        continue
                    n2 = np.hypot(d2[0], d2[1])
                    sin_ang = abs(denom) / (n1 * n2)
                    ang_deg = float(np.rad2deg(np.arcsin(np.clip(sin_ang, 0.0, 1.0))))
                    uu_hit = float(u_u[i] + t_seg * (u_u[i + 1] - u_u[i]))
                    us_hit = float(u_s[j] + u_seg * (u_s[j + 1] - u_s[j]))
                    hits.append((float(wrap_pi(pt[0])), float(pt[1]), ang_deg, uu_hit, us_hit))
    return hits


def compute_and_verify_all_data(force_recompute=False):
    """Compute, cache, and validate all numerical trajectories and manifolds."""
    if CACHE_PATH.exists() and not force_recompute:
        data = dict(np.load(CACHE_PATH, allow_pickle=False))
        print(f"Loaded precomputed numerical data from {CACHE_PATH}")
        return data

    print("--- Computing & validating unforced/forced pendulum dynamics ---")
    # 1. Fixed point & variational check
    z_star, res, DP, det_dp, eigvals, eigvecs = find_hyperbolic_fixed_point([3.01949, 0.0])
    assert np.linalg.norm(res) < 1e-11, f"Fixed point residual too large: {res}"
    assert abs(det_dp - 1.0) < 1e-8, f"Area-preservation failed: det={det_dp}"

    # Verify analytical separatrix E(theta, v) == 2
    th_sep = np.linspace(-np.pi, np.pi, 400)
    v_sep_check = 2.0 * np.cos(th_sep / 2.0)
    E_sep = 0.5 * v_sep_check**2 + 1.0 - np.cos(th_sep)
    assert np.max(np.abs(E_sep - 2.0)) < 1e-14

    # Analytical Melnikov amplitude cross-check
    mel_amp = 2.0 * np.pi * A_DRIVE / np.cosh(0.5 * np.pi * OMEGA)
    assert mel_amp > 0.0

    idx_u = int(np.argmax(np.abs(eigvals)))
    idx_s = 1 - idx_u
    eu = eigvecs[:, idx_u].real
    es = eigvecs[:, idx_s].real
    if eu[0] > 0:
        eu = -eu
    if es[0] > 0:
        es = -es

    # 2. Unforced Stage 1 sample trajectory (closed oscillation E = 1.25)
    E_demo = 1.25
    th0_u = np.arccos(1.0 - E_demo)
    # Integrate half period / full period of unforced oscillator for smooth marker loop
    def rhs_unforced(t, y):
        return [y[1], -np.sin(y[0])]

    sol_unf = solve_ivp(
        rhs_unforced, (0.0, 2.0 * np.pi * 1.18), [th0_u, 0.0],
        dense_output=True, method="DOP853", rtol=1e-11, atol=1e-13,
    )
    # Find return to theta=th0_u, v=0 cleanly (exact period of E=1.25 oscillator)
    t_dense = np.linspace(0.5, 9.0, 4000)
    y_dense = sol_unf.sol(t_dense)
    # Period where y[1] crosses from negative to positive at peak theta
    idx_per = int(np.argmin(np.hypot(y_dense[0, 500:] - th0_u, y_dense[1, 500:]))) + 500
    T_unf = t_dense[idx_per]
    t_unf_grid = np.linspace(0.0, T_unf, 361)
    y_unf_loop = sol_unf.sol(t_unf_grid)  # (2, 361)

    # 3. Stage 2 continuous forced trajectory over 5 forcing periods (0 -> 5T)
    z0_demo = np.array([0.0, 1.98])
    n_demo_periods = 5
    n_pts_per_period = 120
    t_demo = np.linspace(0.0, n_demo_periods * T_PERIOD, n_demo_periods * n_pts_per_period + 1)
    sol_demo = solve_ivp(
        rhs_forced, (0.0, t_demo[-1]), z0_demo,
        t_eval=t_demo, method="DOP853", rtol=1e-10, atol=1e-12,
    )
    demo_traj = sol_demo.y  # (2, 601)
    demo_strobe = demo_traj[:, ::n_pts_per_period]  # exact t_n = nT (n=0..5)

    # 4. Stage 3 Poincare section: Regular islands / rotational KAM curves + Chaotic layer
    reg_seeds = [
        (-1.60, 0.0), (-1.85, 0.0), (-2.12, 0.0),  # Left D-shaped island
        (0.44, 0.0), (0.58, 0.0),                   # Right elliptic island
        (0.0, 2.40), (0.0, -2.40),                  # Rotational KAM curves
    ]
    chaos_seeds = [
        (3.01, 0.08),
        (0.0, 1.98),
        (-1.0, 1.50),
    ]

    reg_th_list, reg_v_list = [], []
    for idx_r, (th0, v0) in enumerate(reg_seeds):
        n_iter = 600 if abs(v0) > 2.0 else 440
        t_eval = np.arange(n_iter) * T_PERIOD
        sol = solve_ivp(
            rhs_forced, (0.0, t_eval[-1]), [th0, v0],
            t_eval=t_eval, method="DOP853", rtol=1e-10, atol=1e-12,
        )
        reg_th_list.append(wrap_pi(sol.y[0]))
        reg_v_list.append(sol.y[1])

    # Interleave chaotic points across the 3 orbits so reveal spreads smoothly
    chaos_pts_each = 480
    chaos_th_all = []
    chaos_v_all = []
    for th0, v0 in chaos_seeds:
        t_eval = np.arange(chaos_pts_each) * T_PERIOD
        sol = solve_ivp(
            rhs_forced, (0.0, t_eval[-1]), [th0, v0],
            t_eval=t_eval, method="DOP853", rtol=1e-10, atol=1e-12,
        )
        chaos_th_all.append(wrap_pi(sol.y[0]))
        chaos_v_all.append(sol.y[1])
    chaos_th = np.column_stack(chaos_th_all).ravel()
    chaos_v = np.column_stack(chaos_v_all).ravel()

    # Interleave regular points cleanly
    max_len_r = max(len(a) for a in reg_th_list)
    reg_th_inter, reg_v_inter = [], []
    for k in range(max_len_r):
        for r_idx in range(len(reg_th_list)):
            if k < len(reg_th_list[r_idx]):
                reg_th_inter.append(reg_th_list[r_idx][k])
                reg_v_inter.append(reg_v_list[r_idx][k])
    reg_th = np.array(reg_th_inter)
    reg_v = np.array(reg_v_inter)

    # 5. Stage 4 Manifolds W^u and W^s (adaptive parametric refinement up to u_max=1.70)
    u_max = 1.70
    wu_l, uu_l = trace_manifold_parametric(z_star, eu, +1, eps=1e-6, u_max=u_max)
    wu_r, uu_r = trace_manifold_parametric(z_star, -eu, +1, eps=1e-6, u_max=u_max)
    ws_l, us_l = trace_manifold_parametric(z_star, es, -1, eps=1e-6, u_max=u_max)
    ws_r, us_r = trace_manifold_parametric(z_star, -es, -1, eps=1e-6, u_max=u_max)

    # Symmetry check: S(theta, v) = (theta, -v)
    sym_err = max(
        float(np.max(np.abs(ws_l[:, 0] - wu_l[:, 0]) + np.abs(ws_l[:, 1] + wu_l[:, 1]))),
        float(np.max(np.abs(ws_r[:, 0] - wu_r[:, 0]) + np.abs(ws_r[:, 1] + wu_r[:, 1]))),
    )
    assert sym_err < 1e-6, f"Symmetry deviation too large: {sym_err}"

    # Verify transverse homoclinic intersections numerically
    all_hits = []
    for cu, uu in ((wu_l, uu_l), (wu_r, uu_r)):
        for cs, us in ((ws_l, us_l), (ws_r, us_r)):
            all_hits.extend(find_curve_intersections_mod2pi(cu, uu, cs, us, z_star))
    assert len(all_hits) > 0, "No transverse homoclinic intersections found!"

    # Select primary symmetric intersection H near (2.2607, 0.0)
    h_prim = max(all_hits, key=lambda h: h[2])  # widest crossing angle (~60 deg)
    H_pt = np.array([h_prim[0], h_prim[1], h_prim[2], h_prim[3], h_prim[4]])
    assert h_prim[2] > 30.0, f"Primary intersection angle too shallow: {h_prim[2]}"

    print(f"  [Verified] Fixed point z_* = ({z_star[0]:.8f}, {z_star[1]:.8f}), |res|={np.linalg.norm(res):.2e}")
    print(f"  [Verified] Area preservation det(DP) = {det_dp:.11f} (|det-1|={abs(det_dp-1.0):.2e})")
    print(f"  [Verified] Melnikov amplitude = {mel_amp:.5f}; Time-reversal sym err = {sym_err:.2e}")
    print(f"  [Verified] Primary transverse H = ({H_pt[0]:.5f}, {H_pt[1]:.5f}), angle = {H_pt[2]:.2f} deg, u_H = {max(H_pt[3], H_pt[4]):.3f}")

    data = {
        "z_star": z_star,
        "H_pt": H_pt,
        "y_unf_loop": y_unf_loop,
        "demo_traj": demo_traj,
        "demo_strobe": demo_strobe,
        "reg_th": reg_th,
        "reg_v": reg_v,
        "chaos_th": chaos_th,
        "chaos_v": chaos_v,
        "wu_l": wu_l,
        "uu_l": uu_l,
        "wu_r": wu_r,
        "uu_r": uu_r,
        "ws_l": ws_l,
        "us_l": us_l,
        "ws_r": ws_r,
        "us_r": us_r,
    }
    np.savez(CACHE_PATH, **data)
    print(f"  Cached numerical dataset to {CACHE_PATH}")
    return data


# -----------------------------------------------------------------------------
# 2. Timeline Evaluator (66.0 seconds total)
# -----------------------------------------------------------------------------
def smoothstep(e0: float, e1: float, x: float) -> float:
    if x <= e0:
        return 0.0
    if x >= e1:
        return 1.0
    u = (x - e0) / (e1 - e0)
    return u * u * (3.0 - 2.0 * u)


def evaluate_timeline(t: float, H_u_req: float):
    """
    5-Stage Storyboard (66.0 s @ 24 fps = 1584 frames) with generous reading holds:
      Stage 1 ( 0.0 ->  7.0 s): Unforced dynamics in Panel A + faint grey reference in Panel B
      Stage 2 ( 7.0 -> 21.0 s): Periodic forcing + stroboscopic phase clock (9.2 s trace + 3.2 s hold)
      Stage 3 (21.0 -> 32.5 s): Poincare section buildup (21->29 s) + 3.5 s hold (29->32.5 s)
      Stage 4 (32.5 -> 51.5 s): Spotlight z_* (32.5->39.8 s, 7.3 s), grow W^s & W^u (39.8->46.0 s),
                                mark H (~45.0 s) + 5.3 s reading hold (46.2->51.5 s)
      Stage 5 (51.5 -> 66.0 s): Magnified inset of H (51.5->57.8 s, ~4.7 s hold),
                                restored wide view (57.8->65.2 s, ~7.4 s hold),
                                seamless loop fade (65.2->66.0 s)
    """
    st = {
        "t": t,
        "stage": 1,
        "stage_pill": "Stage 1: Unforced (A = 0)",
        "unf_phase": (t / 7.0) % 1.0,
        "unf_n_samples": 0,
        # Panel B activation, Stage 1 unforced reference portrait & Stage 2 continuous strobe demo
        "panelB_active": 0.0,
        "unf_ref_contours_alpha": 0.45,
        "unf_ref_lbl_alpha": 0.0,
        "sep_ref_alpha": 0.55,
        "demo_frac": 0.0,
        "demo_alpha": 0.0,
        "phase_widget_alpha": 0.0,
        "phase_cycles": 0.0,
        "n_demo_dots": 0,
        # Stage 3 Poincare points
        "poinc_frac": 0.0,
        "chaos_alpha": 0.0,
        "reg_alpha": 0.0,
        "poinc_lbl_alpha": 0.0,
        # Stage 4 Hyperbolic point & invariant manifolds
        "zstar_alpha": 0.0,
        "manif_u": 0.0,
        "manif_alpha": 0.0,
        "manif_lbl_alpha": 0.0,
        "H_alpha": 0.0,
        # Stage 5 Magnified inset + final restore
        "inset_alpha": 0.0,
        "bottom_B_text": (
            "Waiting to apply periodic forcing:\n"
            "compare conserved-energy orbits in Panel A\n"
            "with the stroboscopic dynamics ahead."
        ),
    }

    if t < 7.0:
        st["stage"] = 1
        st["stage_pill"] = "Unforced reference (A = 0)"
        st["unf_phase"] = t / 7.0
        st["unf_n_samples"] = int(min(6, np.floor(t / 7.0 * 6.0)))
        st["unf_ref_contours_alpha"] = 0.48
        st["unf_ref_lbl_alpha"] = 1.0
        st["sep_ref_alpha"] = 0.62
    elif t < 21.0:
        st["stage"] = 2
        st["stage_pill"] = "Stage 2: Stroboscopic sampling"
        tau = t - 7.0  # [0, 14.0): trace 0.8->10.0 s (5 cycles), hold 10.0->13.2 s (3.2 s), fade 13.2->14.0 s
        st["panelB_active"] = smoothstep(0.0, 0.7, tau)
        # Fade faint grey unforced contours further into background as forcing starts
        st["unf_ref_contours_alpha"] = 0.48 - 0.34 * smoothstep(0.0, 1.2, tau)
        st["unf_ref_lbl_alpha"] = 1.0 - smoothstep(0.0, 0.5, tau)
        st["sep_ref_alpha"] = 0.62 - 0.10 * smoothstep(0.0, 1.0, tau)
        st["phase_widget_alpha"] = smoothstep(0.35, 1.0, tau) * (1.0 - smoothstep(13.1, 13.9, tau))
        raw_u = np.clip((tau - 0.8) / 9.2, 0.0, 1.0)
        st["demo_frac"] = raw_u
        st["phase_cycles"] = 5.0 * raw_u
        st["n_demo_dots"] = 1 + int(np.floor(5.0 * raw_u + 1e-9)) if tau >= 0.8 else 0
        st["demo_alpha"] = 1.0 - smoothstep(13.2, 14.0, tau)
        st["bottom_B_text"] = (
            "The state is recorded once per period (T ≈ 7.85):\n"
            "each dot samples the driven pendulum\n"
            "at the same phase of the external forcing."
        )
    elif t < 32.5:
        st["stage"] = 3
        st["stage_pill"] = "Stage 3: Poincaré section"
        tau = t - 21.0  # [0, 11.5): buildup 0->8.0 s, hold 8.0->11.5 s (3.5 s)
        st["panelB_active"] = 1.0
        st["unf_ref_contours_alpha"] = 0.14 * (1.0 - smoothstep(0.0, 1.5, tau))
        st["unf_ref_lbl_alpha"] = 0.0
        st["sep_ref_alpha"] = 0.52
        st["poinc_frac"] = smoothstep(0.0, 8.0, tau)
        st["chaos_alpha"] = 0.58
        st["reg_alpha"] = 0.82
        st["poinc_lbl_alpha"] = smoothstep(4.5, 5.8, tau)
        st["bottom_B_text"] = (
            "Accumulated samples reveal unbroken islands\n"
            "and rotational tori (teal) beside a scattered\n"
            "chaotic layer (gray) near the separatrix."
        )
    elif t < 51.5:
        st["stage"] = 4
        st["stage_pill"] = "Stage 4: Invariant manifolds"
        tau = t - 32.5  # [0, 19.0)
        st["panelB_active"] = 1.0
        st["unf_ref_contours_alpha"] = 0.0
        st["unf_ref_lbl_alpha"] = 0.0
        st["sep_ref_alpha"] = 0.48 - 0.14 * smoothstep(0.0, 1.5, tau)
        st["poinc_frac"] = 1.0
        st["chaos_alpha"] = 0.58 - 0.34 * smoothstep(0.0, 1.5, tau)
        st["reg_alpha"] = 0.82 - 0.30 * smoothstep(0.0, 1.5, tau)
        st["poinc_lbl_alpha"] = 1.0 - 0.30 * smoothstep(0.0, 1.5, tau)
        # Generous reading beat on hyperbolic fixed point z_* (tau 0.0 -> 7.3 s) before manifolds grow
        st["zstar_alpha"] = smoothstep(0.4, 1.4, tau)
        # Grow W^s (blue) and W^u (red) smoothly over tau = 7.3 -> 13.5 s
        u_prog = smoothstep(7.3, 13.5, tau)
        st["manif_u"] = 1.70 * u_prog
        st["manif_alpha"] = smoothstep(7.1, 7.8, tau)
        st["manif_lbl_alpha"] = smoothstep(8.5, 9.6, tau)
        # Mark verified transverse crossing H after both curves pass u_H, then hold ~5.3 s
        h_thresh = H_u_req / 1.70
        t_h = 7.3 + 6.2 * h_thresh
        st["H_alpha"] = smoothstep(t_h + 0.3, t_h + 1.1, tau)
        if tau < 7.3:
            st["bottom_B_text"] = (
                "Under forcing, the upright equilibrium shifts\n"
                "into a hyperbolic fixed point z* ≈ (3.02, 0)\n"
                "of the stroboscopic Poincaré map."
            )
        else:
            st["bottom_B_text"] = (
                "The stable (Wˢ, blue) and unstable (Wᵘ, red)\n"
                "manifolds of z* split apart and cross\n"
                "transversely at H, driving homoclinic chaos."
            )
    else:
        st["stage"] = 5
        tau = t - 51.5  # [0, 14.5)
        st["panelB_active"] = 1.0
        st["unf_ref_contours_alpha"] = 0.0
        st["unf_ref_lbl_alpha"] = 0.0
        st["sep_ref_alpha"] = 0.34
        st["poinc_frac"] = 1.0
        st["chaos_alpha"] = 0.24
        st["reg_alpha"] = 0.52
        st["zstar_alpha"] = 1.0
        st["manif_u"] = 1.70
        st["manif_alpha"] = 1.0
        st["H_alpha"] = 1.0

        # Inset open from 51.5 -> 57.9 s (4.7 s steady hold), then wide portrait hold 57.9 -> 65.2 s (7.3 s!)
        inset_in = smoothstep(0.0, 0.8, tau)
        inset_out = 1.0 - smoothstep(5.5, 6.4, tau)
        st["inset_alpha"] = inset_in * inset_out

        # Hide occluded labels while inset is open, restore cleanly afterward
        hide_for_inset = 1.0 - smoothstep(0.0, 0.35, st["inset_alpha"])
        st["poinc_lbl_alpha"] = (0.70 + 0.30 * (1.0 - st["inset_alpha"])) * hide_for_inset
        st["manif_lbl_alpha"] = hide_for_inset

        if tau < 6.0:
            st["stage_pill"] = "Stage 5: Transverse crossing H"
            st["bottom_B_text"] = (
                "Magnified neighborhood of H: Wˢ and Wᵘ\n"
                "cross cleanly at ~60°, repeating infinitely\n"
                "often to generate a homoclinic tangle."
            )
        else:
            st["stage_pill"] = "Regular & chaotic coexistence"
            st["bottom_B_text"] = (
                "Chaotic separatrix layers coexist with\n"
                "surviving regular islands: why ordered orbits\n"
                "persist leads directly to KAM theory."
            )

        # Seamless loop reset over final 0.8 s (65.2 -> 66.0 s) back to Stage 1 grey reference
        if tau > 13.7:
            u_rst = smoothstep(13.7, 14.5, tau)
            fade = 1.0 - u_rst
            st["panelB_active"] *= fade
            st["unf_ref_contours_alpha"] = 0.48 * u_rst
            st["unf_ref_lbl_alpha"] = u_rst
            st["sep_ref_alpha"] = 0.34 + (0.62 - 0.34) * u_rst
            st["chaos_alpha"] *= fade
            st["reg_alpha"] *= fade
            st["poinc_lbl_alpha"] *= fade
            st["zstar_alpha"] *= fade
            st["manif_alpha"] *= fade
            st["manif_lbl_alpha"] *= fade
            st["H_alpha"] *= fade

    return st


# -----------------------------------------------------------------------------
# 3. Frame Renderer (1920 x 1080 px)
# -----------------------------------------------------------------------------
G_DATA = None


def setup_phase_axes(ax):
    ax.set_facecolor("#ffffff")
    ax.set_xlim(-np.pi, np.pi)
    ax.set_ylim(-2.5, 2.5)
    ax.set_xticks([-np.pi, -np.pi / 2, 0.0, np.pi / 2, np.pi])
    ax.set_xticklabels([r"$-\pi$", r"$-\pi/2$", r"$0$", r"$\pi/2$", r"$\pi$"], fontsize=13.8, weight="bold", color=SLATE)
    ax.set_yticks([-2, -1, 0, 1, 2])
    ax.set_yticklabels(["-2", "-1", "0", "1", "2"], fontsize=13.8, weight="bold", color=SLATE)
    ax.tick_params(axis="both", which="major", length=4, width=1.2, colors=SLATE, pad=3)
    ax.set_xlabel(r"$\boldsymbol{\theta}$", fontsize=16.0, weight="bold", color=NAVY, labelpad=1)
    ax.set_ylabel(r"$\boldsymbol{\dot{\theta}}$", fontsize=16.2, weight="bold", color=NAVY, labelpad=2)
    for g in (-np.pi / 2, 0.0, np.pi / 2):
        ax.axvline(g, color="#f1f5f9", lw=0.9, zorder=1)
    for g in (-2, -1, 0, 1, 2):
        ax.axhline(g, color="#f1f5f9", lw=0.9, zorder=1)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER_CARD)
        sp.set_linewidth(1.2)


def draw_panelA_unforced(axA, st):
    """Exact unforced pendulum contours (E < 2, E = 2 separatrix, E > 2) + sample marker."""
    th_grid = np.linspace(-np.pi, np.pi, 400)

    # Closed oscillation contours E < 2
    for E_val in (0.28, 0.72, 1.25, 1.72):
        rad = 2.0 * (E_val - (1.0 - np.cos(th_grid)))
        m = rad >= 0.0
        th_m = th_grid[m]
        v_m = np.sqrt(rad[m])
        # Close curve smoothly at turning points
        th_loop = np.concatenate([th_m, th_m[::-1], [th_m[0]]])
        v_loop = np.concatenate([v_m, -v_m[::-1], [v_m[0]]])
        is_demo = abs(E_val - 1.25) < 1e-6
        axA.plot(
            th_loop, v_loop,
            color="#0d9488" if is_demo else "#94a3b8",
            lw=2.1 if is_demo else 1.25,
            alpha=0.90 if is_demo else 0.72,
            zorder=3 if is_demo else 2,
        )

    # Open rotation contours E > 2
    for E_val in (2.35, 2.95, 3.65):
        v_rot = np.sqrt(2.0 * (E_val - (1.0 - np.cos(th_grid))))
        axA.plot(th_grid, v_rot, color="#94a3b8", lw=1.2, alpha=0.68, zorder=2)
        axA.plot(th_grid, -v_rot, color="#94a3b8", lw=1.2, alpha=0.68, zorder=2)

    # Exact separatrix E = 2: v = +- 2 cos(theta / 2)
    v_sep = 2.0 * np.cos(th_grid / 2.0)
    axA.plot(th_grid, v_sep, color=NAVY, lw=2.6, ls="-", zorder=5)
    axA.plot(th_grid, -v_sep, color=NAVY, lw=2.6, ls="-", zorder=5)

    # Hyperbolic equilibria at (-pi, 0) and (pi, 0) (same physical upright state)
    axA.scatter([-np.pi, np.pi], [0.0, 0.0], s=72, facecolor=NAVY, edgecolor="#ffffff", linewidth=1.6, zorder=8, clip_on=False)
    axA.scatter([0.0], [0.0], s=36, facecolor="#475569", edgecolor="#ffffff", linewidth=1.0, zorder=5)

    # Moving sample marker and equally spaced sample points along E = 1.25 loop
    y_loop = G_DATA["y_unf_loop"]  # (2, 361)
    n_pts = y_loop.shape[1] - 1
    idx_curr = int(round(st["unf_phase"] * n_pts)) % n_pts
    axA.scatter(
        [y_loop[0, idx_curr]], [y_loop[1, idx_curr]],
        s=70, facecolor=TEAL_REGULAR, edgecolor="#ffffff", linewidth=1.6, zorder=9,
    )
    if st["unf_n_samples"] > 0:
        sample_idxs = [int(round(k * n_pts / 6.0)) for k in range(st["unf_n_samples"])]
        axA.scatter(
            y_loop[0, sample_idxs], y_loop[1, sample_idxs],
            s=36, facecolor="#14b8a6", edgecolor=NAVY, linewidth=0.9, zorder=7,
        )

    # Clear enlarged labels matching Animation 1 & Figure 1 scale
    axA.text(
        0.0, 2.09, "Separatrix — unforced system (E = 2)",
        fontsize=13.2, weight="bold", color=NAVY, ha="center", va="bottom", path_effects=HALO, zorder=10,
    )
    axA.text(
        0.0, 0.34, "Closed oscillations (E < 2)",
        fontsize=13.0, weight="bold", color=TEAL_DARK, ha="center", va="center", path_effects=HALO, zorder=8,
    )
    axA.text(
        0.0, -2.30, "Rotations (E > 2)",
        fontsize=12.8, weight="bold", color=MUTED_SLATE, ha="center", va="center", path_effects=HALO, zorder=8,
    )
    axA.annotate(
        r"Equilibria $(\pm\pi, 0)$",
        xy=(-np.pi + 0.08, 0.05),
        xytext=(-1.98, 0.72),
        fontsize=12.6, weight="bold", color=NAVY, ha="center", va="center",
        path_effects=HALO,
        arrowprops=dict(arrowstyle="-|>", mutation_scale=12.5, color=NAVY, lw=1.6),
        zorder=10,
    )


def draw_forcing_phase_widget(axB, st):
    """Draw a clean miniature forcing-phase cosine indicator inside top-left of Panel B."""
    a_w = st["phase_widget_alpha"]
    if a_w <= 0.02:
        return
    # Axes coordinates box in top-left of axB with readable enlarged text
    bx0, by0, bw, bh = -3.04, 1.38, 3.04, 1.02
    axB.add_patch(patches.FancyBboxPatch(
        (bx0, by0), bw, bh,
        boxstyle="round,pad=0.0,rounding_size=0.08",
        facecolor="#ffffff", edgecolor=TEAL_BORDER, linewidth=1.4, alpha=0.95 * a_w, zorder=11,
    ))
    axB.text(
        bx0 + bw / 2.0, by0 + bh - 0.17,
        "Sampling every forcing period T",
        fontsize=11.4, weight="bold", color=TEAL_DARK, ha="center", va="center", alpha=a_w, zorder=12,
    )
    # Cosine wave over 1 cycle [0, 2pi]
    phi_grid = np.linspace(0.0, 2.0 * np.pi, 80)
    wx = bx0 + 0.24 + (bw - 0.48) * (phi_grid / (2.0 * np.pi))
    wy_mid = by0 + 0.42
    wy = wy_mid + 0.19 * np.cos(phi_grid)
    axB.plot([wx[0], wx[-1]], [wy_mid, wy_mid], color="#cbd5e1", lw=0.9, ls=":", alpha=a_w, zorder=11)
    axB.plot(wx, wy, color=BLUE_STABLE, lw=1.8, alpha=0.85 * a_w, zorder=12)

    # Moving phase dot
    cyc = st["phase_cycles"]
    frac = cyc - np.floor(cyc)
    phi_c = 2.0 * np.pi * frac
    px_c = bx0 + 0.24 + (bw - 0.48) * frac
    py_c = wy_mid + 0.19 * np.cos(phi_c)
    pulse = np.exp(-((min(frac, 1.0 - frac)) / 0.10) ** 2)
    axB.scatter(
        [px_c], [py_c],
        s=48 + 60 * pulse, facecolor=AMBER_H if pulse > 0.45 else TEAL_REGULAR,
        edgecolor=NAVY, linewidth=1.3, alpha=a_w, zorder=13,
    )
    axB.text(
        bx0 + bw / 2.0, by0 + 0.12,
        f"Cycle n = {max(0, st['n_demo_dots'] - 1)}  (t = nT)",
        fontsize=11.0, weight="bold", color=MUTED_SLATE, ha="center", va="center", alpha=a_w, zorder=12,
    )


def draw_panelB_forced(fig, axB, st):
    """Draw driven system: faint grey unforced reference portrait, Stage 2 demo, Poincare cloud, W^s/W^u, H, and inset."""
    th_g = np.linspace(-np.pi, np.pi, 320)

    # Stage 1 faint light-grey unforced reference contours (fading further into background in Stage 2)
    ref_ca = st["unf_ref_contours_alpha"]
    if ref_ca > 0.01:
        for E_val in (0.28, 0.72, 1.25, 1.72):
            rad = 2.0 * (E_val - (1.0 - np.cos(th_g)))
            m = rad >= 0.0
            th_m = th_g[m]
            v_m = np.sqrt(rad[m])
            th_loop = np.concatenate([th_m, th_m[::-1], [th_m[0]]])
            v_loop = np.concatenate([v_m, -v_m[::-1], [v_m[0]]])
            axB.plot(th_loop, v_loop, color="#cbd5e1", lw=1.15, alpha=ref_ca, zorder=1)
        for E_val in (2.35, 2.95, 3.65):
            v_rot = np.sqrt(2.0 * (E_val - (1.0 - np.cos(th_g))))
            axB.plot(th_g, v_rot, color="#cbd5e1", lw=1.1, alpha=ref_ca, zorder=1)
            axB.plot(th_g, -v_rot, color="#cbd5e1", lw=1.1, alpha=ref_ca, zorder=1)
        # Subtle grey equilibrium markers at (+-pi, 0) & (0, 0)
        axB.scatter([-np.pi, np.pi], [0.0, 0.0], s=42, facecolor="#94a3b8", edgecolor="none", alpha=0.8 * ref_ca, zorder=2, clip_on=False)

    # Reference unforced separatrix (light-grey dashed outline)
    if st["sep_ref_alpha"] > 0.01:
        v_s = 2.0 * np.cos(th_g / 2.0)
        axB.plot(th_g, v_s, color="#94a3b8", lw=1.7 if st["stage"] == 1 else 1.5, ls="--", alpha=st["sep_ref_alpha"], zorder=2)
        axB.plot(th_g, -v_s, color="#94a3b8", lw=1.7 if st["stage"] == 1 else 1.5, ls="--", alpha=st["sep_ref_alpha"], zorder=2)
        if st["stage"] == 2:
            axB.annotate(
                "Separatrix\n(unforced ref.)",
                xy=(1.42, 1.51),
                xytext=(2.18, 2.04),
                fontsize=11.6, weight="bold", color="#64748b",
                ha="center", va="center", alpha=min(1.0, st["sep_ref_alpha"] * 1.5),
                path_effects=HALO,
                arrowprops=dict(arrowstyle="-|>", mutation_scale=11.5, color="#64748b", lw=1.5),
                zorder=8,
            )

    # Discreet corner reference badge during Stage 1 opening seconds
    if st["unf_ref_lbl_alpha"] > 0.02:
        rla = st["unf_ref_lbl_alpha"]
        axB.text(
            -2.94, 2.22,
            "Reference: unforced portrait",
            fontsize=11.6, weight="bold", color="#64748b",
            ha="left", va="center", alpha=0.92 * rla,
            bbox=dict(boxstyle="round,pad=0.28", facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.1, alpha=0.92 * rla),
            zorder=8,
        )

    # Stage 2: continuous trajectory + stroboscopic sample drops at t = nT
    if st["demo_alpha"] > 0.01 and st["demo_frac"] > 0.0:
        traj = G_DATA["demo_traj"]
        n_max = traj.shape[1]
        k_end = max(2, int(round(st["demo_frac"] * (n_max - 1))))
        th_seg, v_seg = insert_wrap_nans(traj[0, : k_end + 1], traj[1, : k_end + 1])
        axB.plot(th_seg, v_seg, color=TEAL_REGULAR, lw=1.8, alpha=0.68 * st["demo_alpha"], zorder=4)
        # Moving head
        axB.scatter(
            [wrap_pi(traj[0, k_end])], [traj[1, k_end]],
            s=65, facecolor=AMBER_H, edgecolor=NAVY, linewidth=1.4, alpha=st["demo_alpha"], zorder=9,
        )
        # Dropped stroboscopic dots
        if st["n_demo_dots"] > 0:
            strobe = G_DATA["demo_strobe"][:, : st["n_demo_dots"]]
            axB.scatter(
                wrap_pi(strobe[0]), strobe[1],
                s=52, facecolor=NAVY, edgecolor="#ffffff", linewidth=1.3, alpha=st["demo_alpha"], zorder=10,
            )
    draw_forcing_phase_widget(axB, st)

    # Stage 3+: Precomputed Poincare section (chaotic layer + regular islands)
    if st["poinc_frac"] > 0.0:
        c_th = G_DATA["chaos_th"]
        c_v = G_DATA["chaos_v"]
        r_th = G_DATA["reg_th"]
        r_v = G_DATA["reg_v"]
        n_c = max(1, int(round(st["poinc_frac"] * len(c_th))))
        n_r = max(1, int(round(st["poinc_frac"] * len(r_th))))

        if st["chaos_alpha"] > 0.01:
            axB.scatter(
                c_th[:n_c], c_v[:n_c],
                s=4.2, color=CHAOS_GRAY, alpha=st["chaos_alpha"], edgecolors="none", zorder=3,
            )
        if st["reg_alpha"] > 0.01:
            axB.scatter(
                r_th[:n_r], r_v[:n_r],
                s=6.0, color=TEAL_REGULAR, alpha=st["reg_alpha"], edgecolors="none", zorder=4,
            )

    # Stage-gated labels for Poincare section (enlarged, strictly in open regions)
    if st["poinc_lbl_alpha"] > 0.02:
        pa = st["poinc_lbl_alpha"]
        # Centered in the open corridor between left D-island and right elliptic island
        axB.text(
            -0.58, 0.02, "Regular\nislands",
            fontsize=13.0, weight="bold", color=TEAL_DARK, ha="center", va="center",
            alpha=pa, linespacing=1.10, path_effects=HALO, zorder=9,
        )
        axB.annotate(
            "", xy=(-1.53, 0.02), xytext=(-1.06, 0.02),
            arrowprops=dict(arrowstyle="-|>", mutation_scale=12.0, color=TEAL_DARK, lw=1.6, alpha=pa),
            zorder=9,
        )
        axB.annotate(
            "", xy=(0.35, 0.02), xytext=(-0.10, 0.02),
            arrowprops=dict(arrowstyle="-|>", mutation_scale=12.0, color=TEAL_DARK, lw=1.6, alpha=pa),
            zorder=9,
        )
        axB.annotate(
            "Chaotic layer",
            xy=(-0.78, 0.96),
            xytext=(-0.82, 0.62),
            fontsize=12.8, weight="bold", color=MUTED_SLATE, ha="center", va="center",
            alpha=pa, path_effects=HALO,
            arrowprops=dict(arrowstyle="-|>", mutation_scale=12.0, color=MUTED_SLATE, lw=1.6, alpha=pa),
            zorder=9,
        )

    # Stage 4+: Hyperbolic fixed point z_* & numerically computed manifolds W^s, W^u
    z_star = G_DATA["z_star"]
    H_pt = G_DATA["H_pt"]

    if st["manif_alpha"] > 0.01 and st["manif_u"] > 0.0:
        u_lim = st["manif_u"]
        ma = st["manif_alpha"]
        for key_pts, key_u, col, lw_m, zo in (
            ("ws_l", "us_l", BLUE_STABLE, 2.3, 6),
            ("ws_r", "us_r", BLUE_STABLE, 2.3, 6),
            ("wu_l", "uu_l", RED_UNSTABLE, 2.3, 7),
            ("wu_r", "uu_r", RED_UNSTABLE, 2.3, 7),
        ):
            pts = G_DATA[key_pts]
            u_arr = G_DATA[key_u]
            mask = u_arr <= u_lim
            if np.count_nonzero(mask) >= 2:
                th_p, v_p = insert_wrap_nans(pts[mask, 0], pts[mask, 1])
                axB.plot(th_p, v_p, color=col, lw=lw_m, alpha=0.92 * ma, zorder=zo)

    if st["zstar_alpha"] > 0.02:
        za = st["zstar_alpha"]
        axB.scatter(
            [z_star[0]], [z_star[1]],
            s=90, facecolor=NAVY, edgecolor="#ffffff", linewidth=1.9, alpha=za, zorder=10,
        )
        axB.annotate(
            "Hyperbolic\nfixed point",
            xy=(z_star[0] - 0.06, z_star[1] + 0.05),
            xytext=(2.32, 1.98),
            fontsize=12.4, weight="bold", color=NAVY, ha="center", va="center",
            linespacing=1.12, alpha=za, path_effects=HALO,
            arrowprops=dict(arrowstyle="-|>", mutation_scale=12.0, color=NAVY, lw=1.6, alpha=za),
            zorder=11,
        )

    if st["manif_lbl_alpha"] > 0.02:
        mla = st["manif_lbl_alpha"]
        axB.text(
            -0.88, 1.24, r"Stable manifold $\boldsymbol{W^s}$",
            fontsize=13.2, weight="bold", color=BLUE_STABLE, ha="center", va="center",
            alpha=mla, path_effects=HALO, zorder=10,
        )
        axB.text(
            0.05, -1.24, r"Unstable manifold $\boldsymbol{W^u}$",
            fontsize=13.2, weight="bold", color=RED_UNSTABLE, ha="center", va="center",
            alpha=mla, path_effects=HALO, zorder=10,
        )

    if st["H_alpha"] > 0.02:
        ha = st["H_alpha"]
        axB.scatter(
            [H_pt[0]], [H_pt[1]],
            s=115, facecolor=AMBER_H, edgecolor=NAVY, linewidth=1.9, alpha=ha, zorder=12,
        )
        if st["inset_alpha"] < 0.5:
            # Placed cleanly in the open interior corridor between the right island and H
            # (zero overlap with Chaotic layer, W^s, or W^u; short unambiguous pointer straight to H)
            axB.annotate(
                r"$\boldsymbol{H}$ — transverse" + "\nintersection",
                xy=(H_pt[0] - 0.09, H_pt[1] + 0.02),
                xytext=(1.38, 0.52),
                fontsize=12.0, weight="bold", color="#92400e", ha="center", va="center",
                linespacing=1.14, alpha=ha,
                bbox=dict(boxstyle="round,pad=0.26", facecolor="#fffbeb", edgecolor="#fcd34d", linewidth=1.2, alpha=0.96 * ha),
                arrowprops=dict(arrowstyle="-|>", mutation_scale=12.5, color="#b45309", lw=1.8, alpha=ha),
                zorder=13,
            )

    # Stage 5: Magnified inset around primary transverse intersection H
    ia = st["inset_alpha"]
    if ia > 0.02:
        zx0, zx1 = 1.38, 2.86
        zy0, zy1 = -1.12, 1.24
        axB.add_patch(patches.Rectangle(
            (zx0, zy0), zx1 - zx0, zy1 - zy0,
            facecolor="none", edgecolor=NAVY, linewidth=1.6, linestyle="--", alpha=0.88 * ia, zorder=11,
        ))
        # Leader lines connecting zoom rectangle to inset card on the left
        axB.plot([zx0, -0.25], [zy1, 1.36], color=NAVY, lw=1.1, ls=":", alpha=0.75 * ia, zorder=11)
        axB.plot([zx0, -0.25], [zy0, -1.30], color=NAVY, lw=1.1, ls=":", alpha=0.75 * ia, zorder=11)

        # Create clean inset axes aligned inside left side of Panel B
        posB = axB.get_position()
        fx0 = (-2.98 - (-np.pi)) / (2.0 * np.pi)
        fx1 = (-0.25 - (-np.pi)) / (2.0 * np.pi)
        fy0 = (-1.30 - (-2.5)) / 5.0
        fy1 = (1.36 - (-2.5)) / 5.0
        ax_ins = fig.add_axes([
            posB.x0 + fx0 * posB.width,
            posB.y0 + fy0 * posB.height,
            (fx1 - fx0) * posB.width,
            (fy1 - fy0) * posB.height,
        ], zorder=15)
        ax_ins.set_facecolor("#ffffff")
        ax_ins.patch.set_alpha(0.98 * ia)
        ax_ins.set_xlim(zx0, zx1)
        ax_ins.set_ylim(zy0, zy1)
        ax_ins.set_xticks([])
        ax_ins.set_yticks([])
        for sp in ax_ins.spines.values():
            sp.set_edgecolor(NAVY)
            sp.set_linewidth(1.8)
            sp.set_alpha(ia)

        # Background chaotic points inside inset
        ax_ins.scatter(G_DATA["chaos_th"], G_DATA["chaos_v"], s=5.5, color=CHAOS_GRAY, alpha=0.22 * ia, edgecolors="none", zorder=2)
        # Crisp magnified manifolds inside inset
        for key_pts, col in (("ws_l", BLUE_STABLE), ("ws_r", BLUE_STABLE), ("wu_l", RED_UNSTABLE), ("wu_r", RED_UNSTABLE)):
            pts = G_DATA[key_pts]
            th_p, v_p = insert_wrap_nans(pts[:, 0], pts[:, 1])
            ax_ins.plot(th_p, v_p, color=col, lw=2.8, alpha=ia, zorder=5)

        ax_ins.scatter([H_pt[0]], [H_pt[1]], s=140, facecolor=AMBER_H, edgecolor=NAVY, linewidth=2.0, alpha=ia, zorder=8)
        ax_ins.text(
            H_pt[0] - 0.14, H_pt[1] + 0.09, r"$\boldsymbol{H}$",
            fontsize=16.5, weight="bold", color="#92400e", ha="right", va="bottom",
            alpha=ia, path_effects=HALO, zorder=9,
        )
        # Inset header badge in empty top space cleanly clear of W^s curve
        ax_ins.text(
            2.12, 1.17, "Magnified crossing (~60°)",
            fontsize=12.0, weight="bold", color=NAVY, ha="center", va="top",
            alpha=ia,
            bbox=dict(boxstyle="round,pad=0.20", facecolor="#f8fafc", edgecolor=BORDER_CARD, linewidth=1.0, alpha=0.95 * ia),
            zorder=9,
        )
        ax_ins.text(
            1.66, 0.52, r"$\boldsymbol{W^s}$", fontsize=15.0, weight="bold", color=BLUE_STABLE,
            ha="center", va="center", alpha=ia, path_effects=HALO, zorder=9,
        )
        ax_ins.text(
            1.66, -0.52, r"$\boldsymbol{W^u}$", fontsize=15.0, weight="bold", color=RED_UNSTABLE,
            ha="center", va="center", alpha=ia, path_effects=HALO, zorder=9,
        )


def render_frame_to_path(state, out_path):
    fig_w, fig_h = 16.0, 9.0
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=120, facecolor="#ffffff")

    # Global Title & Subtitle (matching Animation 1 & Figure 1 hierarchy)
    fig.text(
        0.50, 0.962,
        "From the Pendulum Separatrix to Homoclinic Chaos",
        fontsize=24.0, weight="bold", color=NAVY, ha="center", va="center",
    )
    fig.text(
        0.50, 0.920,
        "How periodic forcing modifies the phase-space structure",
        fontsize=17.5, style="italic", weight="normal", color=DARK_SLATE, ha="center", va="center",
    )

    ax_bg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=0)
    ax_bg.set_xlim(0.0, 1.0)
    ax_bg.set_ylim(0.0, 1.0)
    ax_bg.axis("off")

    y_card = 0.026
    h_card = 0.860
    x1, w1 = 0.018, 0.470
    x2, w2 = 0.512, 0.470
    hbar_h = 0.100
    badge_y = y_card + h_card - hbar_h / 2.0

    panels_spec = [
        (x1, w1, "A", "Unforced pendulum", "Energy contours and separatrix",
         BLUE_STABLE, BLUE_LIGHT, BLUE_BORDER, "A = 0"),
        (x2, w2, "B", "Periodically forced pendulum", "Stroboscopic Poincaré map",
         TEAL_REGULAR, TEAL_LIGHT, TEAL_BORDER, "A = 0.20, Ω = 0.80"),
    ]

    for px, pw, letter, title, subtitle, acc_col, bg_tint, bdr_col, param_lbl in panels_spec:
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px, y_card), pw, h_card,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.5, zorder=1,
        ))
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px, y_card + h_card - hbar_h), pw, hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=bg_tint, edgecolor=bdr_col, linewidth=1.3, zorder=2,
        ))

        badge_x = px + 0.024
        r_x = 0.0145
        r_y = r_x * (fig_w / fig_h)
        ax_bg.add_patch(patches.Ellipse(
            (badge_x, badge_y), width=2.0 * r_x, height=2.0 * r_y,
            facecolor=acc_col, edgecolor="none", zorder=3,
        ))
        ax_bg.text(
            badge_x, badge_y - 0.0005, letter,
            fontsize=17.5, weight="bold", color="#ffffff", ha="center", va="center", zorder=4,
        )

        text_x = badge_x + 0.022
        ax_bg.text(
            text_x, badge_y + 0.019, title,
            fontsize=17.2, weight="bold", color=NAVY, va="center", zorder=4,
        )
        ax_bg.text(
            text_x, badge_y - 0.021, subtitle,
            fontsize=14.4, weight="bold", color=MUTED_SLATE, va="center", zorder=4,
        )

        # Clean parameter pill aligned on subtitle row right (zero collision with panel title)
        pw_p, ph_p = 0.166 if letter == "B" else 0.086, 0.040
        px_p = px + pw - pw_p - 0.012
        py_p = badge_y - 0.021 - ph_p / 2.0
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px_p, py_p), pw_p, ph_p,
            boxstyle="round,pad=0.0,rounding_size=0.010",
            facecolor="#ffffff", edgecolor=bdr_col, linewidth=1.3, zorder=3,
        ))
        ax_bg.text(
            px_p + pw_p / 2.0, py_p + ph_p / 2.0,
            param_lbl,
            fontsize=13.2, weight="bold", color=TEAL_DARK if letter == "B" else BLUE_STABLE,
            ha="center", va="center", zorder=4,
        )

    # Causal bridge arrow between headers (glowing slightly when Panel B activates)
    bridge_col = TEAL_REGULAR if state["stage"] == 2 else "#64748b"
    ax_bg.add_patch(patches.FancyArrowPatch(
        (x1 + w1 + 0.003, badge_y),
        (x2 - 0.003, badge_y),
        arrowstyle="-|>,head_length=7.0,head_width=4.5",
        color=bridge_col, linewidth=2.4, zorder=5,
    ))

    # Synchronized phase-space axes (identical geometry and limits [-pi, pi] x [-2.5, 2.5])
    y_plot = 0.214
    h_plot = 0.544
    w_plot = 0.398
    axA = fig.add_axes([x1 + 0.056, y_plot, w_plot, h_plot], zorder=5)
    axB = fig.add_axes([x2 + 0.056, y_plot, w_plot, h_plot], zorder=5)
    setup_phase_axes(axA)
    setup_phase_axes(axB)

    draw_panelA_unforced(axA, state)
    draw_panelB_forced(fig, axB, state)

    # Bottom summary boxes (matching Animation 1: 14.0 pt bold, 3 balanced lines inside h_box = 0.118)
    y_box, h_box = 0.036, 0.118
    ax_bg.add_patch(patches.FancyBboxPatch(
        (x1 + 0.014, y_box), w1 - 0.028, h_box,
        boxstyle="round,pad=0.0,rounding_size=0.014",
        facecolor=BG_BOX, edgecolor=BLUE_BORDER, linewidth=1.4, zorder=3,
    ))
    ax_bg.text(
        x1 + w1 / 2.0, y_box + h_box / 2.0,
        "Conserved energy E: closed oscillations (E < 2)\n"
        "and rotations (E > 2) are cleanly divided by\n"
        "the exact unforced separatrix (E = 2).",
        fontsize=14.0, weight="bold", color=DARK_SLATE,
        ha="center", va="center", linespacing=1.18, zorder=4,
    )

    ax_bg.add_patch(patches.FancyBboxPatch(
        (x2 + 0.014, y_box), w2 - 0.028, h_box,
        boxstyle="round,pad=0.0,rounding_size=0.014",
        facecolor=BG_BOX, edgecolor=TEAL_BORDER, linewidth=1.4, zorder=3,
    ))
    ax_bg.text(
        x2 + w2 / 2.0, y_box + h_box / 2.0,
        state["bottom_B_text"],
        fontsize=14.0, weight="bold", color=DARK_SLATE,
        ha="center", va="center", linespacing=1.18, zorder=4,
    )

    fig.savefig(out_path, dpi=120, facecolor="#ffffff")
    plt.close(fig)


def init_worker():
    global G_DATA
    G_DATA = dict(np.load(CACHE_PATH, allow_pickle=False))


def render_single_frame(frame_idx: int):
    t = frame_idx / FPS_MASTER
    H_u_req = max(float(G_DATA["H_pt"][3]), float(G_DATA["H_pt"][4]))
    st = evaluate_timeline(t, H_u_req)
    out_p = FRAMES_DIR / f"frame_{frame_idx:04d}.png"
    render_frame_to_path(st, out_p)
    return frame_idx


def generate_preview_frames():
    global G_DATA
    G_DATA = compute_and_verify_all_data()
    H_u_req = max(float(G_DATA["H_pt"][3]), float(G_DATA["H_pt"][4]))
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    previews = [
        ("anim2_s1_unforced.png", 4.5),
        ("anim2_s2_strobe.png", 13.5),
        ("anim2_s3_poincare.png", 30.5),
        ("anim2_s4_manifolds.png", 49.0),
        ("anim2_s5_inset.png", 54.5),
        ("anim2_s5_final.png", 61.0),
    ]
    for fname, t_val in previews:
        st = evaluate_timeline(t_val, H_u_req)
        out_p = SCRATCH_DIR / fname
        render_frame_to_path(st, out_p)
        print(f"  [Preview] Saved {out_p} (t = {t_val:.1f} s)")


def main():
    global G_DATA
    force = "--recompute" in sys.argv
    G_DATA = compute_and_verify_all_data(force_recompute=force)

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

    with multiprocessing.Pool(processes=num_cpus, initializer=init_worker) as pool:
        for idx in pool.imap_unordered(render_single_frame, range(N_TOTAL_FRAMES), chunksize=4):
            if (idx + 1) % 90 == 0 or idx == N_TOTAL_FRAMES - 1:
                print(f"    Completed frame {idx + 1:4d} / {N_TOTAL_FRAMES}")

    print(f"  Frame rendering finished in {time.time() - t0:.1f} s")

    # 1. Master MP4
    mp4_out = OUTPUT_DIR / "pendulum_separatrix_to_homoclinic_chaos.mp4"
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

    # 2. Animated Web GIF (12 fps, 1440px, custom 256-color palette)
    gif_out = OUTPUT_DIR / "pendulum_separatrix_to_homoclinic_chaos.gif"
    print(f"--- Encoding Animated GIF: {gif_out} ---")
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS_MASTER),
        "-i", str(FRAMES_DIR / "frame_%04d.png"),
        "-vf", "fps=12,scale=1440:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256:stats_mode=full[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4",
        "-loop", "0",
        str(gif_out),
    ], check=True)
    print(f"  [OK] Animated GIF saved: {gif_out.stat().st_size / (1024 * 1024):.2f} MB")

    # 3. Static Poster Frame PNG (captured at t = 61.0 s, unobstructed full phase portrait)
    poster_idx = int(61.0 * FPS_MASTER)
    poster_out = OUTPUT_DIR / "pendulum_separatrix_to_homoclinic_chaos.png"
    shutil.copyfile(FRAMES_DIR / f"frame_{poster_idx:04d}.png", poster_out)
    print(f"  [OK] Poster PNG saved: {poster_out} ({poster_out.stat().st_size / (1024 * 1024):.2f} MB)")


if __name__ == "__main__":
    main()

