#!/usr/bin/env python3
r"""
generate_unforced_vs_forced_pendulum.py

Generates the animated two-panel comparison of the unforced and periodically
forced pendulums for Article 3:
"Order and Chaos: The Road to Modern Dynamics III"

Mathematical Model (consistent with Animation 2):
  - Panel A (Unforced):            theta'' + sin(theta) = 0
  - Panel B (Periodically Forced): theta'' + sin(theta) = A cos(Omega * t)
  Parameters: A = 0.20, Omega = 0.80, T = 2*pi/Omega ~ 7.854
  Identical initial conditions: theta(0) = 0.56 rad (~32.09 deg), theta'(0) = 0
  Physical integration window: 0 <= t_phys <= 6T ~ 47.124 (mapped onto 2.0..18.0 s)

Storyboard (21.0 s @ 24 fps = 504 frames, 1920 x 1080 px, 16:9):
  -  0.00 ->  2.00 s: Static opening (full two-panel illustration + +-32 deg markers)
  -  2.00 -> 18.00 s: Simultaneous physical motion (6 forcing periods, energy gain & loss)
  - 18.00 -> 20.30 s: Extended hold on final positions (2.30 s)
  - 20.30 -> 21.00 s: Loop return (Panel A fades out/in from -19.5 deg; Panel B stays solid
                      and glides 0.65 deg from +32.74 deg back to +32.09 deg with torque cross-fade)

Outputs:
  - Master MP4: images/unforced_vs_forced_pendulum.mp4 (24 fps, 1920x1080)
  - Web GIF:    images/unforced_vs_forced_pendulum.gif (15 fps, 1440px, loop=0)
  - Poster PNG: images/unforced_vs_forced_pendulum.png (1920x1080, static opening)
"""

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
FRAMES_DIR = Path("/tmp/unforced_vs_forced_pendulum_frames")

# Physical parameters (identical to Animation 2)
A_DRIVE = 0.20
OMEGA = 0.80
T_PERIOD = 2.0 * np.pi / OMEGA
T_PHYS_END = 6.0 * T_PERIOD
THETA_0 = 0.56  # rad (~32.09 deg)
V_0 = 0.0

# Animation timeline (21.0 s @ 24 fps = 504 frames)
FPS_MASTER = 24
TOTAL_DURATION = 21.0
N_TOTAL_FRAMES = int(round(TOTAL_DURATION * FPS_MASTER))

T_HOLD_START = 2.0
T_MOVE_END = 18.0
T_HOLD_END = 20.30
T_FADEOUT_END = 20.62

# Visual palette (preserved from the static figure)
NAVY = "#0f172a"
DARK_SLATE = "#1e293b"
MUTED_SLATE = "#475569"
BORDER_CARD = "#cbd5e1"
BG_CARD = "#f8fafc"
BG_BOX = "#ffffff"

HEADER_BLUE = "#eff6ff"
HEADER_BORDER = "#93c5fd"
BLUE_ACCENT = "#2563eb"

TEAL_LIGHT = "#f0fdfa"
TEAL_BORDER = "#5eead4"
TEAL_ACCENT = "#0d9488"
TORQ_COLOR = "#dc2626"

HALO = [pe.withStroke(linewidth=3.8, foreground="#ffffff", alpha=0.96)]

# Shared worker state
G_TRAJ = None


def smoothstep(e0: float, e1: float, x: float) -> float:
    if x <= e0:
        return 0.0
    if x >= e1:
        return 1.0
    u = (x - e0) / (e1 - e0)
    return u * u * (3.0 - 2.0 * u)


def compute_trajectories():
    """Integrate unforced and driven pendulum ODEs with DOP853 over [0, 3T]."""
    sol_u = solve_ivp(
        lambda t, y: [y[1], -np.sin(y[0])],
        (0.0, T_PHYS_END),
        [THETA_0, V_0],
        method="DOP853",
        dense_output=True,
        rtol=1e-11,
        atol=1e-13,
    )
    sol_f = solve_ivp(
        lambda t, y: [y[1], -np.sin(y[0]) + A_DRIVE * np.cos(OMEGA * t)],
        (0.0, T_PHYS_END),
        [THETA_0, V_0],
        method="DOP853",
        dense_output=True,
        rtol=1e-11,
        atol=1e-13,
    )
    assert sol_u.success and sol_f.success

    t_check = np.linspace(0.0, T_PHYS_END, 2400)
    yu = sol_u.sol(t_check)
    yf = sol_f.sol(t_check)
    Eu = 0.5 * yu[1] ** 2 + 1.0 - np.cos(yu[0])
    Ef = 0.5 * yf[1] ** 2 + 1.0 - np.cos(yf[0])
    assert np.max(np.abs(Eu - Eu[0])) < 1e-10, "Unforced energy not conserved!"

    return {
        "t_grid": t_check,
        "th_u": yu[0],
        "th_f": yf[0],
        "Eu_0": float(Eu[0]),
        "Ef_min": float(Ef.min()),
        "Ef_max": float(Ef.max()),
    }


def sample_theta(traj, t_phys: float):
    th_u = float(np.interp(t_phys, traj["t_grid"], traj["th_u"]))
    th_f = float(np.interp(t_phys, traj["t_grid"], traj["th_f"]))
    return th_u, th_f


def draw_moving_pendulum_layer(ax, theta_rad: float, layer_alpha: float, show_static_labels_alpha: float):
    """
    Draw the dynamic pendulum elements (rod, bob, angular arc theta, downward gravity arrow)
    with explicit alpha so the loop reset cross-fade is silky smooth.
    """
    if layer_alpha <= 0.01:
        return

    L = 0.94
    bx = L * np.sin(theta_rad)
    by = -L * np.cos(theta_rad)
    theta_deg = np.rad2deg(theta_rad)
    r_bob = 0.088

    # Angular displacement arc theta from downward vertical (-90 deg) to rod (-90 + theta_deg)
    abs_deg = abs(theta_deg)
    arc_alpha = layer_alpha * np.clip((abs_deg - 1.5) / 4.5, 0.0, 1.0)
    if arc_alpha > 0.01:
        r_arc = 0.42
        ang_start = -90.0
        ang_end = -90.0 + theta_deg
        sgn = 1.0 if theta_deg >= 0.0 else -1.0
        trim = min(2.5, abs_deg * 0.35)
        th_arc = np.deg2rad(np.linspace(ang_start, ang_end - sgn * trim, 40))
        ax.plot(
            r_arc * np.cos(th_arc), r_arc * np.sin(th_arc),
            color="#2563eb", lw=2.2, alpha=arc_alpha, zorder=6,
        )
        head_back = min(6.0, abs_deg * 0.65)
        head_tip = min(0.5, abs_deg * 0.08)
        ax.add_patch(patches.FancyArrowPatch(
            (r_arc * np.cos(np.deg2rad(ang_end - sgn * head_back)),
             r_arc * np.sin(np.deg2rad(ang_end - sgn * head_back))),
            (r_arc * np.cos(np.deg2rad(ang_end - sgn * head_tip)),
             r_arc * np.sin(np.deg2rad(ang_end - sgn * head_tip))),
            arrowstyle="-|>",
            mutation_scale=8.5 + 4.0 * np.clip(abs_deg / 12.0, 0.0, 1.0),
            color="#2563eb",
            linewidth=0.0,
            alpha=arc_alpha,
            zorder=7,
        ))
        lbl_arc_alpha = layer_alpha * np.clip((abs_deg - 4.5) / 6.5, 0.0, 1.0)
        if lbl_arc_alpha > 0.01:
            mid_ang = np.deg2rad(0.5 * (ang_start + ang_end))
            ax.text(
                (r_arc + 0.105) * np.cos(mid_ang),
                (r_arc + 0.105) * np.sin(mid_ang),
                r"$\theta$",
                fontsize=16.5,
                weight="bold",
                color="#1d4ed8",
                ha="center",
                va="center",
                alpha=lbl_arc_alpha,
                path_effects=HALO,
                zorder=8,
            )

    # Rigid rod
    ax.plot(
        [0.0, bx], [0.0, by],
        color="#1e293b", lw=4.0, solid_capstyle="round", alpha=layer_alpha, zorder=5,
    )

    # Pendulum bob (deep cobalt blue with inner highlight)
    ax.add_patch(patches.Circle(
        (bx, by), r_bob,
        facecolor="#2563eb", edgecolor="#0f172a", linewidth=2.0, alpha=layer_alpha, zorder=7,
    ))
    ax.add_patch(patches.Circle(
        (bx - 0.026, by + 0.028), 0.022,
        facecolor="#93c5fd", edgecolor="none", alpha=0.85 * layer_alpha, zorder=8,
    ))

    # Downward gravity vector acting on the moving bob (always vertical, constant length)
    g_tip_y = by - 0.36
    ax.add_patch(patches.FancyArrowPatch(
        (bx, by - r_bob - 0.005),
        (bx, g_tip_y),
        arrowstyle="-|>",
        mutation_scale=15.5,
        color="#1e3a8a",
        linewidth=2.8,
        alpha=layer_alpha,
        zorder=9,
    ))

    # Static-hold callout labels ("Pendulum bob", "Gravity") fade away cleanly during motion
    lbl_a = layer_alpha * show_static_labels_alpha
    if lbl_a > 0.01:
        ax.text(
            bx + 0.12, by + 0.02,
            "Pendulum\nbob",
            fontsize=13.2, weight="bold", color="#1e293b",
            ha="left", va="center", linespacing=1.12,
            alpha=lbl_a, path_effects=HALO, zorder=8,
        )
        ax.text(
            bx + 0.055, 0.5 * (by - r_bob + g_tip_y) - 0.01,
            "Gravity",
            fontsize=13.6, weight="bold", color="#1e3a8a",
            ha="left", va="center", alpha=lbl_a, path_effects=HALO, zorder=9,
        )


def draw_torque_indicator(ax, bidir_alpha: float, live_alpha: float, tau_norm: float):
    """
    Draw the Panel B red curved torque indicator around the fixed pivot:
      - Opening / loop-return static state (bidir_alpha > 0): bidirectional red curved arrow.
      - Active motion state (live_alpha > 0): single direction-sensitive red curved arrow
        whose direction follows the figure's positive-angle convention (CCW / upward for tau > 0,
        CW / downward for tau < 0) and whose length/thickness/size scale with |tau(t)|,
        vanishing cleanly at zero crossings.
    """
    r_torq = 0.225
    ang_t0, ang_t1 = np.deg2rad(-38.0), np.deg2rad(16.0)
    ang_mid = 0.5 * (ang_t0 + ang_t1)  # -11 deg (keeps clean clearance above max +42.2 deg rod)

    # 1. Static bidirectional arrow (opening 0..2 s and loop cross-fade return)
    if bidir_alpha > 0.01:
        ts = np.linspace(ang_t0 + 0.12, ang_t1 - 0.12, 60)
        ax.plot(
            r_torq * np.cos(ts), r_torq * np.sin(ts),
            color=TORQ_COLOR, lw=3.2, solid_capstyle="butt", alpha=bidir_alpha, zorder=8,
        )
        ax.add_patch(patches.FancyArrowPatch(
            (r_torq * np.cos(ang_t1 - 0.15), r_torq * np.sin(ang_t1 - 0.15)),
            (r_torq * np.cos(ang_t1 + 0.05), r_torq * np.sin(ang_t1 + 0.05)),
            arrowstyle="-|>", mutation_scale=18.5,
            color=TORQ_COLOR, linewidth=0.0, alpha=bidir_alpha, zorder=9,
        ))
        ax.add_patch(patches.FancyArrowPatch(
            (r_torq * np.cos(ang_t0 + 0.15), r_torq * np.sin(ang_t0 + 0.15)),
            (r_torq * np.cos(ang_t0 - 0.05), r_torq * np.sin(ang_t0 - 0.05)),
            arrowstyle="-|>", mutation_scale=18.5,
            color=TORQ_COLOR, linewidth=0.0, alpha=bidir_alpha, zorder=9,
        ))

    # 2. Live direction-sensitive torque arrow during motion
    mag = abs(tau_norm)
    eff_alpha = live_alpha * np.clip((mag - 0.03) / 0.14, 0.0, 1.0)
    if eff_alpha > 0.01:
        half_span = np.deg2rad(27.0) * (0.28 + 0.72 * mag)
        a_lo = ang_mid - half_span
        a_hi = ang_mid + half_span
        lw_live = 1.8 + 2.2 * mag
        mut_live = 11.5 + 9.5 * mag
        trim_head = min(0.14, half_span * 0.55)

        if tau_norm >= 0.0:
            # Positive torque accelerates +theta (CCW / upward along the right-side arc)
            ts = np.linspace(a_lo, a_hi - trim_head, 50)
            ax.plot(
                r_torq * np.cos(ts), r_torq * np.sin(ts),
                color=TORQ_COLOR, lw=lw_live, solid_capstyle="butt", alpha=eff_alpha, zorder=8,
            )
            ax.add_patch(patches.FancyArrowPatch(
                (r_torq * np.cos(a_hi - trim_head - 0.04), r_torq * np.sin(a_hi - trim_head - 0.04)),
                (r_torq * np.cos(a_hi + 0.05), r_torq * np.sin(a_hi + 0.05)),
                arrowstyle="-|>", mutation_scale=mut_live,
                color=TORQ_COLOR, linewidth=0.0, alpha=eff_alpha, zorder=9,
            ))
        else:
            # Negative torque accelerates -theta (CW / downward along the right-side arc)
            ts = np.linspace(a_lo + trim_head, a_hi, 50)
            ax.plot(
                r_torq * np.cos(ts), r_torq * np.sin(ts),
                color=TORQ_COLOR, lw=lw_live, solid_capstyle="butt", alpha=eff_alpha, zorder=8,
            )
            ax.add_patch(patches.FancyArrowPatch(
                (r_torq * np.cos(a_lo + trim_head + 0.04), r_torq * np.sin(a_lo + trim_head + 0.04)),
                (r_torq * np.cos(a_lo - 0.05), r_torq * np.sin(a_lo - 0.05)),
                arrowstyle="-|>", mutation_scale=mut_live,
                color=TORQ_COLOR, linewidth=0.0, alpha=eff_alpha, zorder=9,
            ))

    # Pointer arrow from "Alternating torque" box toward the pivot torque arc
    ptr_alpha = max(bidir_alpha, live_alpha * (0.35 + 0.65 * np.clip(mag / 0.20, 0.0, 1.0)))
    cbox_x0, cbox_y0 = 0.41, -0.175
    cbox_w, cbox_h = 0.89, 0.295
    cbox_xc = cbox_x0 + cbox_w / 2.0
    ax.add_patch(patches.FancyBboxPatch(
        (cbox_x0, cbox_y0), cbox_w, cbox_h,
        boxstyle="round,pad=0.0,rounding_size=0.04",
        facecolor="#fef2f2", edgecolor="#fca5a5", linewidth=1.4, zorder=8,
    ))
    ax.text(
        cbox_xc, cbox_y0 + cbox_h * 0.77,
        "Alternating torque",
        fontsize=12.8, weight="bold", color="#991b1b",
        ha="center", va="center", zorder=9,
    )
    ax.text(
        cbox_xc, cbox_y0 + cbox_h * 0.31,
        r"$A\,\cos(\Omega t)$",
        fontsize=16.0, weight="bold", color="#991b1b",
        ha="center", va="center", zorder=9,
    )
    ax.add_patch(patches.FancyArrowPatch(
        (cbox_x0 - 0.015, -0.025),
        (r_torq * np.cos(np.deg2rad(-5.0)) + 0.025, r_torq * np.sin(np.deg2rad(-5.0))),
        arrowstyle="-|>",
        mutation_scale=13.5,
        color=TORQ_COLOR,
        linewidth=2.0,
        alpha=ptr_alpha,
        zorder=9,
    ))


def draw_pendulum_panel(ax, show_torque: bool, st: dict):
    """Draw stationary apparatus + animated pendulum/torque elements on ax."""
    ax.set_facecolor("#ffffff")
    ax.set_xlim(-1.20, 1.38)
    ax.set_ylim(-1.44, 0.34)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor("#cbd5e1")
        spine.set_linewidth(1.2)

    # Subtle background grid
    for gx in np.linspace(-1.0, 1.0, 5):
        ax.axvline(gx, color="#f1f5f9", lw=0.9, zorder=1)
    for gy in np.linspace(-1.2, 0.0, 4):
        ax.axhline(gy, color="#f1f5f9", lw=0.9, zorder=1)

    # 1. Fixed rigid ceiling beam with architectural hatching (stationary)
    beam_y0, beam_y1 = 0.09, 0.165
    beam_x0, beam_x1 = -0.34, 0.34
    ax.add_patch(patches.Rectangle(
        (beam_x0, beam_y0), beam_x1 - beam_x0, beam_y1 - beam_y0,
        facecolor="#e2e8f0", edgecolor="none", zorder=2,
    ))
    for hx in np.linspace(beam_x0 + 0.03, beam_x1 - 0.02, 12):
        ax.plot([hx - 0.03, hx + 0.02], [beam_y0, beam_y1], color="#94a3b8", lw=1.0, zorder=3)
    ax.plot([beam_x0, beam_x1], [beam_y0, beam_y0], color="#334155", lw=2.2, zorder=4)

    # Trapezoidal fixed bracket mounting the pivot pin at (0, 0)
    bracket = patches.Polygon(
        [[-0.085, beam_y0], [0.085, beam_y0], [0.042, 0.0], [-0.042, 0.0]],
        closed=True, facecolor="#cbd5e1", edgecolor="#334155", linewidth=1.6, zorder=4,
    )
    ax.add_patch(bracket)

    # Subtle dotted circular swing arc (symmetric, covers full forced amplitude +-42.2 deg)
    L = 0.94
    arc_th = np.linspace(np.deg2rad(-48.0), np.deg2rad(48.0), 100)
    ax.plot(L * np.sin(arc_th), -L * np.cos(arc_th), color="#cbd5e1", lw=1.4, ls=":", zorder=2)

    # Fixed turning-point reference markers at theta = +-0.56 rad (+-32.1 deg)
    if not show_torque:
        # Panel A: solid cobalt-blue turning-point markers (constant unforced excursion)
        mk_line_col = "#2563eb"
        mk_face_col = "#2563eb"
        mk_edge_col = "#ffffff"
        mk_alpha = 0.92
        mk_ls = "-"
    else:
        # Panel B: lighter blue reference markers (initial turning-angle reference)
        mk_line_col = "#60a5fa"
        mk_face_col = "#dbeafe"
        mk_edge_col = "#60a5fa"
        mk_alpha = 0.85
        mk_ls = "--"

    for sgn_m in (-1.0, 1.0):
        th_m = sgn_m * THETA_0
        s_m, c_m = np.sin(th_m), -np.cos(th_m)
        # Radial stop-tick extending just outside bob rim so marker stays clearly visible even at contact
        r_in, r_out = L - 0.105, L + 0.115
        ax.plot(
            [r_in * s_m, r_out * s_m], [r_in * c_m, r_out * c_m],
            color=mk_line_col, lw=2.2, ls=mk_ls, alpha=mk_alpha, solid_capstyle="round", zorder=4,
        )
        # Crisp dot right on the circular trajectory arc
        ax.scatter(
            [L * s_m], [L * c_m],
            s=46, facecolor=mk_face_col, edgecolor=mk_edge_col, linewidth=1.4,
            alpha=mk_alpha, zorder=4,
        )

    # Compact non-overlapping turning-point legend badge in bottom-right corner
    if not show_torque:
        ax.text(
            1.31, -1.345,
            "Turning points: ±32°",
            fontsize=11.0, weight="bold", color="#1d4ed8",
            ha="right", va="center",
            bbox=dict(boxstyle="round,pad=0.26", facecolor="#eff6ff", edgecolor="#93c5fd", linewidth=1.1),
            zorder=8,
        )
    else:
        ax.text(
            1.31, -1.345,
            "Initial angular excursion: ±32°",
            fontsize=10.8, weight="bold", color="#2563eb",
            ha="right", va="center",
            bbox=dict(boxstyle="round,pad=0.26", facecolor="#f8fafc", edgecolor="#93c5fd", linewidth=1.1),
            zorder=8,
        )

    # Downward vertical reference line (theta = 0) — always visible
    ax.plot([0.0, 0.0], [0.0, -1.26], color="#64748b", lw=1.6, ls="--", zorder=3)
    ax.text(
        0.0, -1.355, r"$\theta = 0$",
        fontsize=13.5, weight="bold", color="#475569",
        ha="center", va="center", path_effects=HALO, zorder=6,
    )

    pend_alpha = st["pend_alpha_B"] if show_torque else st["pend_alpha_A"]
    vert_lbl_alpha = st["vert_lbl_alpha_B"] if show_torque else st["vert_lbl_alpha_A"]
    bob_lbl_alpha = st["bob_lbl_alpha_B"] if show_torque else st["bob_lbl_alpha_A"]
    theta_curr = st["theta_B"] if show_torque else st["theta_A"]

    # "Downward vertical" text fades during motion so left-swinging rod never collides with it
    if vert_lbl_alpha > 0.01:
        ax.text(
            -0.055, -0.61, "Downward\nvertical",
            fontsize=12.4, weight="bold", color="#64748b",
            ha="right", va="center", linespacing=1.15,
            alpha=vert_lbl_alpha, path_effects=HALO, zorder=5,
        )

    # Fixed pivot callout (top-left, stationary, outside swing region)
    ax.text(
        -0.50, 0.015,
        "Fixed pivot",
        fontsize=13.4, weight="bold", color="#0f172a",
        ha="right", va="center", path_effects=HALO, zorder=9,
    )
    ax.add_patch(patches.FancyArrowPatch(
        (-0.47, 0.015), (-0.065, 0.005),
        arrowstyle="-|>", mutation_scale=13.0,
        color="#475569", linewidth=1.7, zorder=9,
    ))

    # 2. Moving pendulum layer — Panel A fades out/in across reset; Panel B stays continuously solid
    draw_moving_pendulum_layer(
        ax,
        theta_curr,
        layer_alpha=pend_alpha,
        show_static_labels_alpha=bob_lbl_alpha,
    )

    # Fixed pivot pin at (0, 0) drawn above rod tip (stationary)
    ax.add_patch(patches.Circle((0.0, 0.0), 0.042, facecolor="#334155", edgecolor="#0f172a", lw=1.5, zorder=10))
    ax.add_patch(patches.Circle((0.0, 0.0), 0.017, facecolor="#f8fafc", edgecolor="none", zorder=11))

    # 3. Panel-specific forcing state
    if not show_torque:
        ax.text(
            0.80, -0.02,
            "No external\ndriving torque",
            fontsize=13.2, weight="bold", color="#475569",
            ha="center", va="center", linespacing=1.18,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.2),
            zorder=6,
        )
    else:
        draw_torque_indicator(
            ax,
            bidir_alpha=st["bidir_alpha"],
            live_alpha=st["live_torq_alpha"],
            tau_norm=st["tau_norm"],
        )


def evaluate_timeline(t_anim: float, traj: dict) -> dict:
    """
    Evaluate animation state at t_anim in [0.0, 21.0]:
      -  0.00 ->  2.00 s: Static opening hold (exact initial pose, bidirectional torque arrow)
      -  2.00 -> 18.00 s: Physical motion over 0 <= t_phys <= 6T (~47.124)
      - 18.00 -> 20.30 s: Extended hold on final positions (2.30 s)
      - 20.30 -> 21.00 s: Loop return:
          * Panel A (ends at -19.46 deg): fade out (20.30->20.62 s) then fade in at +32.09 deg
          * Panel B (ends at +32.74 deg): stays solid (pend_alpha_B=1.0), smoothly settles
            0.65 deg back to +32.09 deg while live torque cross-fades to bidirectional arrow
    """
    if t_anim <= T_HOLD_START:
        return {
            "theta_A": THETA_0,
            "theta_B": THETA_0,
            "tau_norm": 1.0,
            "pend_alpha_A": 1.0,
            "pend_alpha_B": 1.0,
            "vert_lbl_alpha_A": 1.0,
            "vert_lbl_alpha_B": 1.0,
            "bob_lbl_alpha_A": 1.0,
            "bob_lbl_alpha_B": 1.0,
            "bidir_alpha": 1.0,
            "live_torq_alpha": 0.0,
        }
    elif t_anim <= T_MOVE_END:
        frac = (t_anim - T_HOLD_START) / (T_MOVE_END - T_HOLD_START)
        t_phys = frac * T_PHYS_END
        th_u, th_f = sample_theta(traj, t_phys)
        tau_norm = float(np.cos(OMEGA * t_phys))
        static_lbl_alpha = 1.0 - smoothstep(T_HOLD_START, T_HOLD_START + 0.40, t_anim)
        morph = smoothstep(T_HOLD_START, T_HOLD_START + 0.30, t_anim)
        return {
            "theta_A": th_u,
            "theta_B": th_f,
            "tau_norm": tau_norm,
            "pend_alpha_A": 1.0,
            "pend_alpha_B": 1.0,
            "vert_lbl_alpha_A": static_lbl_alpha,
            "vert_lbl_alpha_B": static_lbl_alpha,
            "bob_lbl_alpha_A": static_lbl_alpha,
            "bob_lbl_alpha_B": static_lbl_alpha,
            "bidir_alpha": 1.0 - morph,
            "live_torq_alpha": morph,
        }
    elif t_anim <= T_HOLD_END:
        th_u, th_f = sample_theta(traj, T_PHYS_END)
        tau_norm = float(np.cos(OMEGA * T_PHYS_END))
        return {
            "theta_A": th_u,
            "theta_B": th_f,
            "tau_norm": tau_norm,
            "pend_alpha_A": 1.0,
            "pend_alpha_B": 1.0,
            "vert_lbl_alpha_A": 0.0,
            "vert_lbl_alpha_B": 0.0,
            "bob_lbl_alpha_A": 0.0,
            "bob_lbl_alpha_B": 0.0,
            "bidir_alpha": 0.0,
            "live_torq_alpha": 1.0,
        }
    else:
        th_u_end, th_f_end = sample_theta(traj, T_PHYS_END)
        tau_norm_end = float(np.cos(OMEGA * T_PHYS_END))
        u_loop = smoothstep(T_HOLD_END, TOTAL_DURATION, t_anim)

        # Panel B stays continuously visible and glides the 0.65 deg back to THETA_0
        theta_B = th_f_end + u_loop * (THETA_0 - th_f_end)

        if t_anim <= T_FADEOUT_END:
            u_out = smoothstep(T_HOLD_END, T_FADEOUT_END, t_anim)
            theta_A = th_u_end
            pend_alpha_A = 1.0 - u_out
            vert_lbl_alpha_A = 0.0
            bob_lbl_alpha_A = 0.0
        else:
            u_in = smoothstep(T_FADEOUT_END, TOTAL_DURATION, t_anim)
            theta_A = THETA_0
            pend_alpha_A = u_in
            vert_lbl_alpha_A = u_in
            bob_lbl_alpha_A = 1.0  # multiplied by pend_alpha_A inside draw_moving_pendulum_layer

        return {
            "theta_A": theta_A,
            "theta_B": theta_B,
            "tau_norm": tau_norm_end,
            "pend_alpha_A": pend_alpha_A,
            "pend_alpha_B": 1.0,
            "vert_lbl_alpha_A": vert_lbl_alpha_A,
            "vert_lbl_alpha_B": u_loop,
            "bob_lbl_alpha_A": bob_lbl_alpha_A,
            "bob_lbl_alpha_B": u_loop,
            "bidir_alpha": u_loop,
            "live_torq_alpha": 1.0 - u_loop,
        }


def render_frame_to_path(st: dict, output_path: Path, dpi: int = 120):
    """Render a single 16:9 frame (1920 x 1080 px at dpi=120)."""
    fig_w, fig_h = 16.0, 9.0
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor="#ffffff")

    # -------------------------------------------------------------------------
    # Global Title & Subtitle (preserved identically)
    # -------------------------------------------------------------------------
    fig.text(
        0.50, 0.962,
        "Unforced and Periodically Forced Pendulums",
        fontsize=24.0, weight="bold", color=NAVY, ha="center", va="center",
    )
    fig.text(
        0.50, 0.920,
        "Comparing motion with and without periodic driving, in the absence of damping",
        fontsize=17.5, style="italic", weight="normal", color=DARK_SLATE, ha="center", va="center",
    )

    ax_bg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=0)
    ax_bg.set_xlim(0.0, 1.0)
    ax_bg.set_ylim(0.0, 1.0)
    ax_bg.axis("off")

    # -------------------------------------------------------------------------
    # Two Equal-Width Parallel Panel Cards (A and B)
    # -------------------------------------------------------------------------
    y_card = 0.026
    h_card = 0.860
    x1, w1 = 0.018, 0.470
    x2, w2 = 0.512, 0.470
    hbar_h = 0.100
    badge_y = y_card + h_card - hbar_h / 2.0

    panels_spec = [
        (x1, w1, "A", "Unforced pendulum",
         "Fixed pivot and gravity only (no external driving torque)",
         BLUE_ACCENT, HEADER_BLUE, HEADER_BORDER),
        (x2, w2, "B", "Periodically forced pendulum",
         "Same fixed pivot with an additive periodic torque",
         TEAL_ACCENT, TEAL_LIGHT, TEAL_BORDER),
    ]

    for px, pw, letter, title, subtitle, acc_color, bg_tint, bdr_color in panels_spec:
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px, y_card), pw, h_card,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.5, zorder=1,
        ))
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px, y_card + h_card - hbar_h), pw, hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=bg_tint, edgecolor=bdr_color, linewidth=1.3, zorder=2,
        ))

        badge_x = px + 0.024
        r_x = 0.0145
        r_y = r_x * (fig_w / fig_h)
        ax_bg.add_patch(patches.Ellipse(
            (badge_x, badge_y), width=2.0 * r_x, height=2.0 * r_y,
            facecolor=acc_color, edgecolor="none", zorder=3,
        ))
        ax_bg.text(
            badge_x, badge_y - 0.0005, letter,
            fontsize=17.5, weight="bold", color="#ffffff",
            ha="center", va="center", zorder=4,
        )

        text_offset_x = badge_x + 0.022
        ax_bg.text(
            text_offset_x, badge_y + 0.019, title,
            fontsize=17.6, weight="bold", color=NAVY, va="center", zorder=4,
        )
        ax_bg.text(
            text_offset_x, badge_y - 0.021, subtitle,
            fontsize=14.4, weight="bold", color=MUTED_SLATE, va="center", zorder=4,
        )

    # Conceptual progression arrow between Panel A and Panel B headers
    ax_bg.add_patch(patches.FancyArrowPatch(
        (x1 + w1 + 0.003, badge_y),
        (x2 - 0.003, badge_y),
        arrowstyle="-|>,head_length=7.0,head_width=4.5",
        color="#64748b", linewidth=2.2, zorder=5,
    ))

    # -------------------------------------------------------------------------
    # Pendulum Diagrams (Identical geometry & axes dimensions in A and B)
    # -------------------------------------------------------------------------
    y_plot = 0.222
    h_plot = 0.542
    w_plot = w1 - 0.040

    axA = fig.add_axes([x1 + (w1 - w_plot) / 2.0, y_plot, w_plot, h_plot], zorder=5)
    axB = fig.add_axes([x2 + (w2 - w_plot) / 2.0, y_plot, w_plot, h_plot], zorder=5)

    draw_pendulum_panel(axA, show_torque=False, st=st)
    draw_pendulum_panel(axB, show_torque=True, st=st)

    # -------------------------------------------------------------------------
    # Bottom Normalized Equation & Physics Summary Cards (stationary)
    # -------------------------------------------------------------------------
    y_box = 0.036
    h_box = 0.146

    y_norm_lbl = 0.5 * (y_box + h_box + y_plot)
    for px, pw in ((x1, w1), (x2, w2)):
        ax_bg.text(
            px + pw / 2.0, y_norm_lbl,
            "Normalized equation",
            fontsize=11.4, weight="bold", color=MUTED_SLATE,
            ha="center", va="center", zorder=4,
        )

    bottom_specs = [
        (
            x1, w1, HEADER_BORDER, "#1d4ed8",
            r"$\ddot{\theta} + \sin\theta = 0$",
            "Conservative motion with no external torque;\n"
            "total mechanical energy remains conserved.",
            y_box + 0.046,
        ),
        (
            x2, w2, TEAL_BORDER, "#991b1b",
            r"$\ddot{\theta} + \sin\theta = A\cos(\Omega t)$",
            "An external periodic torque, with normalized\n"
            "amplitude A, can increase or decrease the\n"
            "pendulum’s mechanical energy, even without damping.",
            y_box + 0.046,
        ),
    ]

    for px, pw, bdr_col, eq_col, eq_tex, desc, y_desc in bottom_specs:
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px + 0.012, y_box), pw - 0.024, h_box,
            boxstyle="round,pad=0.0,rounding_size=0.014",
            facecolor=BG_BOX, edgecolor=bdr_col, linewidth=1.4, zorder=3,
        ))
        ax_bg.text(
            px + pw / 2.0, y_box + h_box - 0.031,
            eq_tex,
            fontsize=20.0, weight="bold", color=eq_col,
            ha="center", va="center", zorder=4,
        )
        ax_bg.text(
            px + pw / 2.0, y_desc,
            desc,
            fontsize=13.0, weight="bold", color=DARK_SLATE,
            ha="center", va="center", linespacing=1.18, zorder=4,
        )

    fig.savefig(output_path, dpi=dpi, facecolor="#ffffff")
    plt.close(fig)


def init_worker(traj):
    global G_TRAJ
    G_TRAJ = traj


def render_single_frame(frame_idx: int):
    t_anim = frame_idx / FPS_MASTER
    st = evaluate_timeline(t_anim, G_TRAJ)
    out_p = FRAMES_DIR / f"frame_{frame_idx:04d}.png"
    render_frame_to_path(st, out_p, dpi=120)
    return frame_idx


def generate_preview_frames(traj):
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    # Key moments across 6T (t = 2.0 -> 18.0 s):
    # static (0.5s), left peak t/T=2.50 (8.67s), right peak t/T=2.99 (9.97s), return t/T=5.50 (16.67s)
    previews = [
        ("pend_anim6_01_static.png", 0.50),
        ("pend_anim6_02_left_peak.png", 8.67),
        ("pend_anim6_03_right_peak.png", 9.97),
        ("pend_anim6_04_return.png", 16.67),
    ]
    for fname, t_val in previews:
        st = evaluate_timeline(t_val, traj)
        out_p = SCRATCH_DIR / fname
        render_frame_to_path(st, out_p, dpi=120)
        print(f"  [Preview] {out_p} (t={t_val:.2f}s, thA={np.rad2deg(st['theta_A']):+.1f}deg, thB={np.rad2deg(st['theta_B']):+.1f}deg, tau={st['tau_norm']:+.2f})")


def main():
    traj = compute_trajectories()
    print(f"--- Verified DOP853 trajectories (0 <= t_phys <= 6T = {T_PHYS_END:.4f}) ---")
    print(f"  Unforced E_0 = {traj['Eu_0']:.6f} (conserved)")
    print(f"  Forced   E   in [{traj['Ef_min']:.6f}, {traj['Ef_max']:.6f}]")

    if "--preview-only" in sys.argv:
        generate_preview_frames(traj)
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"--- Rendering {N_TOTAL_FRAMES} frames ({TOTAL_DURATION:.1f} s @ {FPS_MASTER} fps, 1920x1080) ---")
    t0 = time.time()
    num_cpus = max(1, min(14, multiprocessing.cpu_count() - 2))
    print(f"  Using {num_cpus} parallel workers...")

    with multiprocessing.Pool(processes=num_cpus, initializer=init_worker, initargs=(traj,)) as pool:
        for idx in pool.imap_unordered(render_single_frame, range(N_TOTAL_FRAMES), chunksize=4):
            if (idx + 1) % 60 == 0 or idx == N_TOTAL_FRAMES - 1:
                print(f"    Completed frame {idx + 1:3d} / {N_TOTAL_FRAMES}")

    print(f"  Frame rendering finished in {time.time() - t0:.1f} s")

    # 1. Master MP4 (24 fps, 1920x1080)
    mp4_out = OUTPUT_DIR / "unforced_vs_forced_pendulum.mp4"
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

    # 2. Animated Web GIF (15 fps, 1440px, custom 256-color palette, loop=0)
    gif_out = OUTPUT_DIR / "unforced_vs_forced_pendulum.gif"
    print(f"--- Encoding Animated GIF: {gif_out} ---")
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS_MASTER),
        "-i", str(FRAMES_DIR / "frame_%04d.png"),
        "-vf", "fps=15,scale=1440:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256:stats_mode=full[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4",
        "-loop", "0",
        str(gif_out),
    ], check=True)
    print(f"  [OK] Animated GIF saved: {gif_out.stat().st_size / (1024 * 1024):.2f} MB")

    # 3. Static Poster PNG (frame 0 = clean static opening pose)
    poster_out = OUTPUT_DIR / "unforced_vs_forced_pendulum.png"
    shutil.copyfile(FRAMES_DIR / "frame_0000.png", poster_out)
    print(f"  [OK] Poster PNG saved: {poster_out} ({poster_out.stat().st_size / (1024 * 1024):.2f} MB)")


if __name__ == "__main__":
    main()
