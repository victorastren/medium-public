#!/usr/bin/env python3
r"""
generate_lorenz_sensitive_dependence_animation.py

Generates Animation 2 ("Sensitive Dependence in the Lorenz System") for Section 3.3
("Sensitive Dependence and the Limits of Predictability") of Article 3:
"Order and Chaos: The Road to Modern Dynamics III"

Mathematical Model — Classical Chaotic Lorenz-63 Equations:
  dx/dt = 10 * (y - x)
  dy/dt = x * (28 - z) - y
  dz/dt = x * y - (8/3) * z

Two independent solutions integrated with SciPy DOP853 (rtol=1e-11, atol=1e-13):
  x_1(0) = (1, 1, 1)
  x_2(0) = (1 + 1e-6, 1, 1)
  Initial separation: d(0) = ||x_2(0) - x_1(0)|| = 1e-6

Full integration:    0 <= t <= 32,  dt = 0.01
Displayed interval:  20 <= t <= 31.5  (after initial transient 0 <= t < 20)
Reference attractor: Integrated from (1, 1, 1) over 0 <= t <= 110 (discarding 0 <= t < 20),
                     identical to Figure 2.

Timeline (27.0 s @ 24 fps = 648 frames, 1920 x 1080 px):
  -  0.00 -> 24.00 s: Constant-rate evolution t_sim: 20.0 -> 31.5 (~0.4792 units/s)
                      *  0 -> 10 s: Initial agreement (20.0 <= t_sim < 24.8)
                      * 10 -> 18 s: Growing differences (24.8 <= t_sim < 28.6)
                      * 18 -> 24 s: Different evolution (28.6 <= t_sim <= 31.5)
  - 24.00 -> 26.50 s: Extended hold (2.50 s) on separated trajectories at t_sim = 31.5
  - 26.50 -> 27.00 s: Smooth cross-fade back to t_sim = 20.0 for seamless looping

Outputs:
  - Master MP4: images/lorenz_sensitive_dependence.mp4 (24 fps, 1920x1080)
  - Web GIF:    images/lorenz_sensitive_dependence.gif (14 fps, 1440px, loop=0)
  - Poster PNG: images/lorenz_sensitive_dependence.png (t_sim = 31.5 overview)
"""

import sys
import time
import shutil
import subprocess
import multiprocessing
from pathlib import Path
from typing import cast
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.axes3d import Axes3D

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
FRAMES_DIR = Path("/tmp/lorenz_sensitive_dependence_frames")

# Lorenz-63 parameters
SIGMA = 10.0
RHO = 28.0
BETA = 8.0 / 3.0

X1_0 = np.array([1.0, 1.0, 1.0], dtype=float)
X2_0 = np.array([1.0 + 1e-6, 1.0, 1.0], dtype=float)

DT = 0.01
T_INT_END = 32.0
T_DISP_START = 20.0
T_DISP_END = 31.5
TRAIL_UNITS = 4.0  # trailing segment length in model time units

# Animation timeline (27.0 s @ 24 fps = 648 frames)
FPS_MASTER = 24
T_EVOLVE_END = 24.0
T_HOLD_END = 26.5
TOTAL_DURATION = 27.0
N_TOTAL_FRAMES = int(round(TOTAL_DURATION * FPS_MASTER))

# Visual palette consistent with Figure 2 & Article 3
NAVY = "#0f172a"
DARK_SLATE = "#1e293b"
SLATE = "#334155"
MUTED_SLATE = "#475569"
BORDER_CARD = "#cbd5e1"
BG_CARD = "#f8fafc"
BG_BOX = "#ffffff"
GRID_COL = "#e2e8f0"

PURPLE_ACCENT = "#4f46e5"
PURPLE_LIGHT = "#eef2ff"
PURPLE_BORDER = "#a5b4fc"

TEAL_ACCENT = "#0d9488"
TEAL_LIGHT = "#f0fdfa"
TEAL_BORDER = "#5eead4"

COL_TRAJ1 = "#4f46e5"   # Trajectory 1 (purple)
COL_TRAJ2 = "#ea580c"   # Trajectory 2 (orange)
COL_REF = "#cbd5e1"     # Reference attractor (light grey)

G_DATA = None


def lorenz_rhs(_t, state):
    x, y, z = state
    return [
        SIGMA * (y - x),
        x * (RHO - z) - y,
        x * y - BETA * z,
    ]


def compute_trajectories():
    """Integrate Reference Attractor and both nearby Lorenz solutions using DOP853."""
    # Reference attractor matching Figure 2 (t in [0, 110], discard t < 20)
    t_ref_grid = np.round(np.arange(0.0, 110.0 + 0.5 * DT, DT), 6)
    sol_ref = solve_ivp(
        lorenz_rhs, (0.0, 110.0), X1_0, t_eval=t_ref_grid,
        method="DOP853", rtol=1e-10, atol=1e-12,
    )
    assert sol_ref.success
    ref_mask = t_ref_grid >= T_DISP_START - 1e-9
    y_ref = sol_ref.y[:, ref_mask]

    # Paired trajectories integrated identically over [0, 32] with tight tolerances
    t_grid = np.round(np.arange(0.0, T_INT_END + 0.5 * DT, DT), 6)
    sol1 = solve_ivp(
        lorenz_rhs, (0.0, T_INT_END), X1_0, t_eval=t_grid,
        method="DOP853", rtol=1e-11, atol=1e-13,
    )
    sol2 = solve_ivp(
        lorenz_rhs, (0.0, T_INT_END), X2_0, t_eval=t_grid,
        method="DOP853", rtol=1e-11, atol=1e-13,
    )
    assert sol1.success and sol2.success

    # Verification checks
    disp_mask = (t_grid >= T_DISP_START - 1e-9) & (t_grid <= T_DISP_END + 1e-9)
    t_disp = t_grid[disp_mask]
    y1_disp = sol1.y[:, disp_mask]
    y2_disp = sol2.y[:, disp_mask]

    d0 = float(np.linalg.norm(sol2.y[:, 0] - sol1.y[:, 0]))
    d_start = float(np.linalg.norm(y2_disp[:, 0] - y1_disp[:, 0]))
    d_max = float(np.max(np.linalg.norm(y2_disp - y1_disp, axis=0)))
    assert abs(d0 - 1e-6) < 1e-12, f"Unexpected initial separation: {d0}"
    assert d_start < 1e-2, f"Trajectories already diverged before t=20: {d_start}"
    assert d_max > 20.0, f"Trajectories failed to diverge in [20, 31.5]: max d = {d_max}"
    assert np.all(np.abs(y1_disp[0]) < 21.0) and np.all(np.abs(y2_disp[0]) < 21.0)

    print(
        f"Verified DOP853 solutions (dt={DT}): d(0)={d0:.2e}, d(20)={d_start:.4f}, "
        f"max d([20,31.5])={d_max:.2f}, N_disp={len(t_disp)}"
    )
    return {
        "y_ref": y_ref,
        "t_disp": t_disp,
        "y1": y1_disp,
        "y2": y2_disp,
    }


def smoothstep(e0: float, e1: float, x: float) -> float:
    if x <= e0:
        return 0.0
    if x >= e1:
        return 1.0
    u = (x - e0) / (e1 - e0)
    return u * u * (3.0 - 2.0 * u)


def evaluate_timeline(t_anim: float):
    """Map animation clock t_anim in [0, 27.0] to simulation time and clean loop fade alpha."""
    if t_anim <= T_EVOLVE_END:
        frac = t_anim / T_EVOLVE_END
        t_sim = T_DISP_START + frac * (T_DISP_END - T_DISP_START)
        content_alpha = 1.0
    elif t_anim <= T_HOLD_END:
        t_sim = T_DISP_END
        content_alpha = 1.0
    else:
        # Smooth fade out (24.50..24.75) -> reset -> fade in (24.75..25.00)
        t_mid = 0.5 * (T_HOLD_END + TOTAL_DURATION)
        if t_anim < t_mid:
            t_sim = T_DISP_END
            content_alpha = 1.0 - smoothstep(T_HOLD_END, t_mid, t_anim)
        else:
            t_sim = T_DISP_START
            content_alpha = smoothstep(t_mid, TOTAL_DURATION, t_anim)

    # Regime indicator aligned with 0-10s / 10-18s / 18-24s narrative
    if t_anim < 10.0:
        phase_txt = "Initial agreement"
        phase_col = "#0f766e"
        phase_bg = "#f0fdfa"
        phase_bdr = "#5eead4"
    elif t_anim < 18.0:
        phase_txt = "Growing differences"
        phase_col = "#b45309"
        phase_bg = "#fffbeb"
        phase_bdr = "#fcd34d"
    elif t_anim <= T_HOLD_END:
        phase_txt = "Diverged trajectories"
        phase_col = "#c2410c"
        phase_bg = "#fff7ed"
        phase_bdr = "#fdba74"
    else:
        if t_anim < 0.5 * (T_HOLD_END + TOTAL_DURATION):
            phase_txt = "Diverged trajectories"
            phase_col = "#c2410c"
            phase_bg = "#fff7ed"
            phase_bdr = "#fdba74"
        else:
            phase_txt = "Initial agreement"
            phase_col = "#0f766e"
            phase_bg = "#f0fdfa"
            phase_bdr = "#5eead4"

    return {
        "t_sim": float(t_sim),
        "content_alpha": float(content_alpha),
        "phase_txt": phase_txt,
        "phase_col": phase_col,
        "phase_bg": phase_bg,
        "phase_bdr": phase_bdr,
    }


def slice_up_to_time(t_arr, y_arr, t_sim: float):
    """Interpolate exact endpoint at t_sim so motion is silky-smooth even between dt=0.01 samples."""
    if t_sim <= t_arr[0] + 1e-12:
        return t_arr[:1], y_arr[:, :1]
    idx = int(np.searchsorted(t_arr, t_sim, side="right")) - 1
    idx = max(0, min(idx, len(t_arr) - 1))
    if idx < len(t_arr) - 1 and t_sim > t_arr[idx]:
        w = (t_sim - t_arr[idx]) / (t_arr[idx + 1] - t_arr[idx])
        y_end = (1.0 - w) * y_arr[:, idx : idx + 1] + w * y_arr[:, idx + 1 : idx + 2]
        t_out = np.concatenate([t_arr[: idx + 1], [t_sim]])
        y_out = np.hstack([y_arr[:, : idx + 1], y_end])
        return t_out, y_out
    return t_arr[: idx + 1], y_arr[:, : idx + 1]


def render_frame_to_path(st, data, output_path: Path, dpi: int = 120):
    fig_w, fig_h = 16.0, 9.0
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor="#ffffff")

    ax_bg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=0)
    ax_bg.set_xlim(0.0, 1.0)
    ax_bg.set_ylim(0.0, 1.0)
    ax_bg.axis("off")

    # -------------------------------------------------------------------------
    # Global Title, Subtitle & Shared Live Clock Pill
    # -------------------------------------------------------------------------
    fig.text(
        0.50, 0.957,
        "Sensitive Dependence in the Lorenz System",
        fontsize=23.2, weight="bold", color=NAVY, ha="center", va="center",
    )
    fig.text(
        0.50, 0.913,
        r"Two trajectories with an initial difference of $10^{-6}$ in $x$",
        fontsize=17.0, style="italic", weight="normal", color=DARK_SLATE, ha="center", va="center",
    )

    # Shared live simulation clock + regime badge top-right (well clear of centered title)
    ax_bg.add_patch(patches.FancyBboxPatch(
        (0.790, 0.896), 0.196, 0.082,
        boxstyle="round,pad=0.0,rounding_size=0.010",
        facecolor=st["phase_bg"], edgecolor=st["phase_bdr"], linewidth=1.3, zorder=8,
    ))
    ax_bg.text(
        0.888, 0.952,
        f"t = {st['t_sim']:4.1f}",
        fontsize=17.5, weight="bold", color=NAVY,
        ha="center", va="center", alpha=max(0.25, st["content_alpha"]), zorder=9,
    )
    ax_bg.text(
        0.888, 0.916,
        st["phase_txt"],
        fontsize=12.6, weight="bold", color=st["phase_col"],
        ha="center", va="center", alpha=max(0.25, st["content_alpha"]), zorder=9,
    )

    # -------------------------------------------------------------------------
    # Two Balanced Parallel Cards (A left, B right)
    # -------------------------------------------------------------------------
    y_card = 0.084
    h_card = 0.792
    x1, w1 = 0.014, 0.472
    x2, w2 = 0.514, 0.472
    hbar_h = 0.112
    badge_y = y_card + h_card - hbar_h / 2.0

    panels_spec = [
        (
            x1, w1, "A",
            "Trajectories in phase space",
            "Evolving on the same Lorenz attractor",
            PURPLE_ACCENT, PURPLE_LIGHT, PURPLE_BORDER,
        ),
        (
            x2, w2, "B",
            "Evolution of x(t)",
            "Initially superposed, then separating",
            TEAL_ACCENT, TEAL_LIGHT, TEAL_BORDER,
        ),
    ]

    for px, pw, letter, title, subtitle, acc_col, bg_tint, bdr_col in panels_spec:
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px, y_card), pw, h_card,
            boxstyle="round,pad=0.0,rounding_size=0.014",
            facecolor=BG_BOX, edgecolor=BORDER_CARD, linewidth=1.3, zorder=1,
        ))
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px, y_card + h_card - hbar_h), pw, hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.014",
            facecolor=bg_tint, edgecolor=bdr_col, linewidth=1.2, zorder=2,
        ))

        badge_x = px + 0.025
        r_x = 0.0145
        r_y = r_x * (fig_w / fig_h)
        ax_bg.add_patch(patches.Ellipse(
            (badge_x, badge_y), width=2.0 * r_x, height=2.0 * r_y,
            facecolor=acc_col, edgecolor="none", zorder=3,
        ))
        ax_bg.text(
            badge_x, badge_y - 0.0005, letter,
            fontsize=17.5, weight="bold", color="#ffffff",
            ha="center", va="center", zorder=4,
        )

        text_offset_x = badge_x + 0.022
        ax_bg.text(
            text_offset_x, badge_y + 0.018, title,
            fontsize=17.8, weight="bold", color=NAVY, va="center", zorder=4,
        )
        ax_bg.text(
            text_offset_x, badge_y - 0.020, subtitle,
            fontsize=14.4, weight="bold", color=MUTED_SLATE, va="center", zorder=4,
        )

    # Conceptual progression arrow between panel headers
    ax_bg.add_patch(patches.FancyArrowPatch(
        (x1 + w1 + 0.003, badge_y), (x2 - 0.003, badge_y),
        arrowstyle="-|>,head_length=6.8,head_width=4.4",
        color="#64748b", linewidth=2.0, zorder=5,
    ))

    # Extract slices up to t_sim
    t_sim = st["t_sim"]
    alpha_dyn = st["content_alpha"]
    t_sub, y1_sub = slice_up_to_time(data["t_disp"], data["y1"], t_sim)
    _, y2_sub = slice_up_to_time(data["t_disp"], data["y2"], t_sim)

    # Trail slice for Panel A (last TRAIL_UNITS model time units)
    t_trail_min = max(T_DISP_START, t_sim - TRAIL_UNITS)
    trail_mask = t_sub >= t_trail_min - 1e-9
    y1_tr = y1_sub[:, trail_mask]
    y2_tr = y2_sub[:, trail_mask]

    # -------------------------------------------------------------------------
    # PANEL A — 3D Phase-Space Trajectories (identical perspective & bounds to Fig 2)
    # -------------------------------------------------------------------------
    axA = cast(Axes3D, fig.add_axes(
        [x1 - 0.014, y_card + 0.022, w1 + 0.026, h_card - hbar_h - 0.026],
        projection="3d", zorder=5,
    ))
    axA.patch.set_alpha(0.0)
    axA.view_init(elev=21, azim=-54)
    axA.set_proj_type("persp", focal_length=0.58)

    for axis_obj in (axA.xaxis, axA.yaxis, axA.zaxis):
        axis_obj.set_pane_color((0.985, 0.990, 0.996, 1.0))
        axis_obj.line.set_color("#94a3b8")
        axis_obj.line.set_linewidth(1.0)
        axis_obj._axinfo["grid"]["color"] = GRID_COL
        axis_obj._axinfo["grid"]["linewidth"] = 0.7
        axis_obj._axinfo["tick"]["color"] = "#64748b"

    axA.set_xlim(-22.0, 22.0)
    axA.set_ylim(-30.0, 30.0)
    axA.set_zlim(0.0, 55.0)

    axA.set_xticks([-20, 0, 20])
    axA.set_yticks([-20, 0, 20])
    axA.set_zticks([0, 25, 50])
    axA.tick_params(axis="x", labelsize=12.2, colors=MUTED_SLATE, pad=1)
    axA.tick_params(axis="y", labelsize=12.2, colors=MUTED_SLATE, pad=1)
    axA.tick_params(axis="z", labelsize=12.2, colors=MUTED_SLATE, pad=3)

    axA.set_xlabel(r"$x$", fontsize=16.5, weight="bold", color=NAVY, labelpad=6)
    axA.set_ylabel(r"$y$", fontsize=16.5, weight="bold", color=NAVY, labelpad=6)
    axA.set_zlabel(r"$z$", fontsize=16.5, weight="bold", color=NAVY, labelpad=6)
    axA.set_box_aspect((1.16, 1.16, 0.88), zoom=0.96)

    # Faint reference Lorenz attractor (subsampled slightly for crisp fast rendering)
    y_ref = data["y_ref"][:, ::2]
    axA.plot(y_ref[0], y_ref[1], y_ref[2], color=COL_REF, lw=0.85, alpha=0.62, zorder=1)

    # Dynamic 4-unit trailing arcs + depth-ordered moving endpoints (always show nested pair while superposed)
    if alpha_dyn > 0.01:
        if y1_tr.shape[1] >= 2:
            axA.plot(y1_tr[0], y1_tr[1], y1_tr[2], color=COL_TRAJ1, lw=3.2,
                     alpha=0.88 * alpha_dyn, solid_capstyle="round", zorder=4)
            axA.plot(y2_tr[0], y2_tr[1], y2_tr[2], color=COL_TRAJ2, lw=1.9,
                     alpha=0.95 * alpha_dyn, solid_capstyle="round", zorder=5)

    # Shared compact legend cleanly placed in open upper-left inside Panel A
    legend_handles = [
        Line2D([0], [0], color=COL_TRAJ1, lw=3.2, marker="o", markersize=7.8,
               markerfacecolor=COL_TRAJ1, markeredgecolor="#ffffff", markeredgewidth=1.1,
               label=r"Trajectory 1: $\mathbf{x}_1(0) = (1, 1, 1)$"),
        Line2D([0], [0], color=COL_TRAJ2, lw=2.4, marker="o", markersize=6.6,
               markerfacecolor=COL_TRAJ2, markeredgecolor="#ffffff", markeredgewidth=1.0,
               label=r"Trajectory 2: $\mathbf{x}_2(0) = (1 + 10^{-6}, 1, 1)$"),
        Line2D([0], [0], color="#94a3b8", lw=2.0, alpha=0.85,
               label="Reference attractor"),
    ]
    leg = fig.legend(
        handles=legend_handles,
        loc="upper left",
        bbox_to_anchor=(x1 + 0.010, y_card + h_card - hbar_h - 0.008),
        bbox_transform=fig.transFigure,
        frameon=True, facecolor=BG_CARD, edgecolor=BORDER_CARD,
        framealpha=0.96, borderpad=0.46, labelspacing=0.30, handlelength=1.8,
        prop={"weight": "bold", "size": 14.2},
    )
    leg.set_zorder(15)
    for txt in leg.get_texts():
        txt.set_color(DARK_SLATE)

    # -------------------------------------------------------------------------
    # PANEL B — Synchronized x(t) Time Series
    # -------------------------------------------------------------------------
    axB = fig.add_axes([x2 + 0.068, y_card + 0.088, w2 - 0.092, h_card - hbar_h - 0.130], zorder=5)
    axB.set_facecolor("#ffffff")
    axB.set_xlim(T_DISP_START, T_DISP_END + 0.15)
    axB.set_ylim(-22.0, 22.0)

    axB.set_xticks([20, 22, 24, 26, 28, 30])
    axB.set_xticklabels(["20", "22", "24", "26", "28", "30"], fontsize=13.5, weight="bold", color=SLATE)
    axB.set_yticks([-20, -10, 0, 10, 20])
    axB.set_yticklabels(["−20", "−10", "0", "10", "20"], fontsize=13.5, weight="bold", color=SLATE)
    axB.tick_params(axis="both", which="major", length=4.5, width=1.2, colors=SLATE, pad=4)

    axB.set_xlabel(r"$t$  (initialized at $t = 0$; transient $t < 20$ omitted)",
                   fontsize=14.8, weight="bold", color=NAVY, labelpad=6)
    axB.set_ylabel(r"$x(t)$", fontsize=16.5, weight="bold", color=NAVY, labelpad=4)

    axB.grid(True, color="#f1f5f9", linewidth=1.0, zorder=1)
    axB.axhline(0.0, color="#cbd5e1", linewidth=1.1, ls="-", zorder=2)
    for sp in ("top", "right"):
        axB.spines[sp].set_visible(False)
    for sp in ("bottom", "left"):
        axB.spines[sp].set_edgecolor("#94a3b8")
        axB.spines[sp].set_linewidth(1.3)

    if alpha_dyn > 0.01:
        # Plot Trajectory 1 thicker underneath, Trajectory 2 crisply on top so superposition shows both colors
        axB.plot(t_sub, y1_sub[0], color=COL_TRAJ1, lw=3.6, alpha=0.88 * alpha_dyn,
                 solid_capstyle="round", zorder=4)
        axB.plot(t_sub, y2_sub[0], color=COL_TRAJ2, lw=1.9, alpha=0.98 * alpha_dyn,
                 solid_capstyle="round", zorder=5)

        # Vertical synchronized time cursor
        axB.axvline(t_sim, color="#64748b", lw=1.5, ls="--", alpha=0.75 * alpha_dyn, zorder=3)

        # Moving endpoint markers synchronized with Panel A
        axB.scatter([t_sim], [y1_sub[0, -1]], s=110, color=COL_TRAJ1,
                    edgecolor="#ffffff", linewidth=1.6, alpha=alpha_dyn, clip_on=False, zorder=7)
        axB.scatter([t_sim], [y2_sub[0, -1]], s=54, color=COL_TRAJ2,
                    edgecolor="#ffffff", linewidth=1.1, alpha=alpha_dyn, clip_on=False, zorder=8)

        # Draw Panel A moving markers in clean foreground figure overlay so orange core is always visible during overlap
        fig.canvas.draw()
        ax_pts = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=9)
        ax_pts.set_xlim(0.0, 1.0)
        ax_pts.set_ylim(0.0, 1.0)
        ax_pts.axis("off")
        ax_pts.patch.set_alpha(0.0)

        p1_x2, p1_y2, p1_z2 = proj3d.proj_transform(y1_sub[0, -1], y1_sub[1, -1], y1_sub[2, -1], axA.get_proj())
        p2_x2, p2_y2, p2_z2 = proj3d.proj_transform(y2_sub[0, -1], y2_sub[1, -1], y2_sub[2, -1], axA.get_proj())
        f1 = fig.transFigure.inverted().transform(axA.transData.transform((p1_x2, p1_y2)))
        f2 = fig.transFigure.inverted().transform(axA.transData.transform((p2_x2, p2_y2)))
        dist3d = float(np.linalg.norm(y2_sub[:, -1] - y1_sub[:, -1]))
        # Keep orange core on top while superposed (dist3d < 0.8), otherwise depth-sort cleanly
        markers = [
            (f1[0], f1[1], p1_z2, 118, COL_TRAJ1, 1.6, 1),
            (f2[0], f2[1], p2_z2, 56, COL_TRAJ2, 1.1, 2),
        ]
        if dist3d >= 0.8:
            markers.sort(key=lambda item: -item[2])
        for mx, my, _, ms, mcol, mlw, _ in markers:
            ax_pts.scatter([mx], [my], s=ms, color=mcol, edgecolor="#ffffff",
                           linewidth=mlw, alpha=alpha_dyn, zorder=10)

    # -------------------------------------------------------------------------
    # Bottom Explanatory Strip
    # -------------------------------------------------------------------------
    ax_bg.add_patch(patches.FancyBboxPatch(
        (0.014, 0.015), 0.972, 0.054,
        boxstyle="round,pad=0.0,rounding_size=0.010",
        facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.2, zorder=3,
    ))
    ax_bg.text(
        0.50, 0.042,
        "Same equations and parameters  ·  Different initial conditions (Δx₀ = 10⁻⁶ at t = 0)  ·  No stochastic forcing",
        fontsize=16.0, weight="bold", color=DARK_SLATE,
        ha="center", va="center", zorder=4,
    )

    fig.savefig(output_path, dpi=dpi, facecolor="#ffffff")
    plt.close(fig)


def init_worker(data):
    global G_DATA
    G_DATA = data


def render_single_frame(frame_idx: int):
    t_anim = frame_idx / FPS_MASTER
    st = evaluate_timeline(t_anim)
    out_p = FRAMES_DIR / f"frame_{frame_idx:04d}.png"
    render_frame_to_path(st, G_DATA, out_p, dpi=120)
    return frame_idx


def generate_preview_frames(data):
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    # Key storyboard snapshots across 0..24s:
    previews = [
        ("lorenz_anim2_01_agree_t20_5.png", 1.04),
        ("lorenz_anim2_02_grow_t26_5.png", 13.56),
        ("lorenz_anim2_03_diverge_t29_0.png", 18.78),
        ("lorenz_anim2_04_end_t31_5.png", 24.00),
    ]
    for fname, t_val in previews:
        st = evaluate_timeline(t_val)
        out_p = SCRATCH_DIR / fname
        render_frame_to_path(st, data, out_p, dpi=120)
        print(f"  [Preview] {out_p} (t_anim={t_val:.2f}s -> t_sim={st['t_sim']:.2f}, phase={st['phase_txt']})")


def main():
    data = compute_trajectories()

    if "--preview-only" in sys.argv:
        generate_preview_frames(data)
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"--- Rendering {N_TOTAL_FRAMES} frames ({TOTAL_DURATION:.1f} s @ {FPS_MASTER} fps, 1920x1080) ---")
    t0 = time.time()
    num_cpus = max(1, min(14, multiprocessing.cpu_count() - 2))
    print(f"  Using {num_cpus} parallel workers...")

    with multiprocessing.Pool(processes=num_cpus, initializer=init_worker, initargs=(data,)) as pool:
        for idx in pool.imap_unordered(render_single_frame, range(N_TOTAL_FRAMES), chunksize=4):
            if (idx + 1) % 100 == 0 or idx == N_TOTAL_FRAMES - 1:
                print(f"    Completed frame {idx + 1:3d} / {N_TOTAL_FRAMES}")

    print(f"  Frame rendering finished in {time.time() - t0:.1f} s")

    # 1. Master MP4 (24 fps, 1920x1080)
    mp4_out = OUTPUT_DIR / "lorenz_sensitive_dependence.mp4"
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
    gif_out = OUTPUT_DIR / "lorenz_sensitive_dependence.gif"
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

    # 3. Poster PNG (final diverged overview frame at t_sim = 31.5)
    poster_idx = int(round(T_EVOLVE_END * FPS_MASTER))
    poster_out = OUTPUT_DIR / "lorenz_sensitive_dependence.png"
    shutil.copyfile(FRAMES_DIR / f"frame_{poster_idx:04d}.png", poster_out)
    print(f"  [OK] Poster PNG saved: {poster_out} ({poster_out.stat().st_size / (1024 * 1024):.2f} MB)")


if __name__ == "__main__":
    main()
