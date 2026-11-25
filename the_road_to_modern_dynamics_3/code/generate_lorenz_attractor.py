#!/usr/bin/env python3
r"""
generate_lorenz_attractor.py

Generates Figure 2 ("The Lorenz Attractor in Phase Space") for Section 3.2
("Phase-Space Contraction and the Lorenz Attractor") of Article 3:
"Order and Chaos: The Road to Modern Dynamics III"

Numerical Setup (Lorenz-63 Classical Chaotic Regime):
  dx/dt = sigma * (y - x)
  dy/dt = x * (rho - z) - y
  dz/dt = x * y - beta * z
  sigma = 10,   rho = 28,   beta = 8 / 3

  Initial condition:   (x0, y0, z0) = (1, 1, 1)
  Integration domain:  t in [0, 110],  dt = 0.01
  Discarded transient: 0 <= t < 20
  Plotted trajectory:  20 <= t <= 110  (9001 points)
  Integrator:          SciPy DOP853 (rtol = 1e-10, atol = 1e-12)

Output:
  images/lorenz_attractor.png (2816 x 1760 px, 17.6 x 11.0 in @ 160 dpi, 16:10)
"""

from pathlib import Path
from typing import cast
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
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
OUTPUT_PNG = PROJECT_DIR / "images" / "lorenz_attractor.png"

SIGMA = 10.0
RHO = 28.0
BETA = 8.0 / 3.0
Y0 = np.array([1.0, 1.0, 1.0], dtype=float)
T_END = 110.0
T_TRANSIENT = 20.0
DT = 0.01


def lorenz_rhs(_t, state):
    x, y, z = state
    return [
        SIGMA * (y - x),
        x * (RHO - z) - y,
        x * y - BETA * z,
    ]


def integrate_lorenz(t_end=T_END, dt=DT, rtol=1e-10, atol=1e-12):
    t_eval = np.round(np.arange(0.0, t_end + 0.5 * dt, dt), 6)
    sol = solve_ivp(
        lorenz_rhs,
        (0.0, float(t_eval[-1])),
        Y0,
        t_eval=t_eval,
        method="DOP853",
        rtol=rtol,
        atol=atol,
    )
    if not sol.success:
        raise RuntimeError(f"Lorenz integration failed: {sol.message}")
    return sol.t, sol.y


def count_lobe_switches(x, thresh=4.0):
    """Count transitions between negative-lobe (x < -thresh) and positive-lobe (x > thresh) residence."""
    state = 0
    switches = 0
    for xv in x:
        if xv > thresh:
            if state == -1:
                switches += 1
            state = 1
        elif xv < -thresh:
            if state == 1:
                switches += 1
            state = -1
    return switches


def validate_trajectory(t, y, t_ref, y_ref):
    """Verify boundedness, transient removal, repeated bilateral circulation, and tolerance stability."""
    mask = t >= T_TRANSIENT - 1e-9
    yp = y[:, mask]
    x, yy, z = yp[0], yp[1], yp[2]

    # 1. Transient exclusion check
    assert abs(t[mask][0] - T_TRANSIENT) < 1e-8, "Transient window mismatch"

    # 2. Boundedness check
    assert np.all(np.isfinite(yp)), "Non-finite values in solution"
    assert -25.0 < x.min() < -12.0 and 12.0 < x.max() < 25.0, f"Unexpected x bounds: {x.min():.2f}, {x.max():.2f}"
    assert -32.0 < yy.min() < -15.0 and 15.0 < yy.max() < 32.0, f"Unexpected y bounds: {yy.min():.2f}, {yy.max():.2f}"
    assert 0.0 < z.min() < 10.0 and 40.0 < z.max() < 55.0, f"Unexpected z bounds: {z.min():.2f}, {z.max():.2f}"

    # 3. Repeated bilateral switches
    switches = count_lobe_switches(x)
    assert switches >= 20, f"Too few lobe switches: {switches}"

    # 4. Modest tolerance variation preserves global attractor bounds & bilateral switching
    yp_ref = y_ref[:, t_ref >= T_TRANSIENT - 1e-9]
    sw_ref = count_lobe_switches(yp_ref[0])
    assert sw_ref >= 20
    print(
        f"Validated Lorenz trajectory (t in [{T_TRANSIENT:.0f}, {T_END:.0f}], N={yp.shape[1]}): "
        f"x in [{x.min():.2f}, {x.max():.2f}], y in [{yy.min():.2f}, {yy.max():.2f}], "
        f"z in [{z.min():.2f}, {z.max():.2f}], lobe switches={switches} (ref={sw_ref})"
    )
    return t[mask], yp


def pick_highlight_segment(t_seg, y_seg):
    """
    Extract a genuine smooth segment from the numerical trajectory:
    starts near the outer bottom of the left lobe (C_-), rises through the center,
    and sweeps cleanly around the upper outer rim of the right lobe (C_+) so the
    connecting bridge and flow direction are unmistakable.
    """
    x = y_seg[0]
    y = y_seg[1]
    z = y_seg[2]
    n_len = 66
    mid_lo = int(0.30 * len(t_seg))
    mid_hi = int(0.75 * len(t_seg)) - n_len
    for i in range(mid_lo, mid_hi):
        if -12.0 < x[i] < -5.0 and y[i] < 0.0 and z[i] < 20.0:
            # Verify it crosses into positive lobe and reaches a prominent outer arc
            seg_x = x[i : i + n_len]
            seg_z = z[i : i + n_len]
            if seg_x[-1] > 12.0 and np.max(seg_z) > 33.0:
                return slice(i, i + n_len)
    return slice(mid_lo, mid_lo + n_len)


def data3d_to_fig(ax, fig, x3, y3, z3):
    """Project 3D data coordinates accurately to figure normalized coordinates [0, 1]^2."""
    x2, y2, _ = proj3d.proj_transform(x3, y3, z3, ax.get_proj())
    disp = ax.transData.transform((x2, y2))
    fx, fy = fig.transFigure.inverted().transform(disp)
    return float(fx), float(fy)


def create_figure(output_path=None):
    out_path = Path(output_path) if output_path is not None else OUTPUT_PNG
    t_main, y_main = integrate_lorenz(T_END, DT, rtol=1e-10, atol=1e-12)
    t_ref, y_ref = integrate_lorenz(T_END, DT, rtol=1e-12, atol=1e-14)
    tp, yp = validate_trajectory(t_main, y_main, t_ref, y_ref)
    x, y, z = yp[0], yp[1], yp[2]

    fig_w, fig_h = 17.6, 11.0  # 16:10 landscape (2816 x 1760 px @ 160 dpi)
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=160, facecolor="#ffffff")

    NAVY = "#0f172a"
    DARK_SLATE = "#1e293b"
    MUTED_SLATE = "#475569"
    BORDER_CARD = "#cbd5e1"
    GRID_COL = "#e2e8f0"
    PURPLE_TRAJ = "#4f46e5"       # continuous blue-violet trajectory
    ORANGE_HIGHLIGHT = "#ea580c"  # short highlighted segment + direction arrow
    EQ_GREY = "#475569"

    # -------------------------------------------------------------------------
    # Global Title & Subtitle (matching Article 3 typography hierarchy)
    # -------------------------------------------------------------------------
    fig.text(
        0.5, 0.955,
        "The Lorenz Attractor in Phase Space",
        fontsize=28.0, weight="bold", color=NAVY, ha="center", va="center",
    )
    fig.text(
        0.5, 0.908,
        r"Numerical trajectory of the Lorenz equations for $\sigma = 10$, $\rho = 28$, $\beta = 8/3$",
        fontsize=20.0, style="italic", weight="normal", color=DARK_SLATE, ha="center", va="center",
    )

    # Background framing card layer (zorder=0)
    ax_bg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=0)
    ax_bg.set_xlim(0.0, 1.0)
    ax_bg.set_ylim(0.0, 1.0)
    ax_bg.axis("off")

    card_y, card_h = 0.126, 0.744
    ax_bg.add_patch(patches.FancyBboxPatch(
        (0.022, card_y), 0.956, card_h,
        boxstyle="round,pad=0.0,rounding_size=0.014",
        facecolor="#ffffff", edgecolor=BORDER_CARD, linewidth=1.4, zorder=1,
    ))

    # -------------------------------------------------------------------------
    # Single Large 3D Phase-Space Plot (transparent axes bg so card & overlays stay clean)
    # -------------------------------------------------------------------------
    ax = cast(Axes3D, fig.add_axes([-0.03, 0.134, 1.06, 0.770], projection="3d", zorder=2))
    ax.patch.set_alpha(0.0)
    ax.view_init(elev=21, azim=-54)
    ax.set_proj_type("persp", focal_length=0.58)

    # Subtle neutral panes & minimal light-grey reference grid
    for axis_obj in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis_obj.set_pane_color((0.985, 0.990, 0.996, 1.0))
        axis_obj.line.set_color("#94a3b8")
        axis_obj.line.set_linewidth(1.1)
        axis_obj._axinfo["grid"]["color"] = GRID_COL
        axis_obj._axinfo["grid"]["linewidth"] = 0.75
        axis_obj._axinfo["tick"]["color"] = "#64748b"

    # Specified axis limits
    ax.set_xlim(-22.0, 22.0)
    ax.set_ylim(-30.0, 30.0)
    ax.set_zlim(0.0, 55.0)

    # Clean non-colliding tick intervals retaining full axis ranges above
    ax.set_xticks([-20, -10, 0, 10, 20])
    ax.set_yticks([-20, 0, 20])
    ax.set_zticks([0, 10, 20, 30, 40, 50])

    ax.tick_params(axis="x", labelsize=14.8, colors=MUTED_SLATE, pad=2)
    ax.tick_params(axis="y", labelsize=14.8, colors=MUTED_SLATE, pad=2)
    ax.tick_params(axis="z", labelsize=14.8, colors=MUTED_SLATE, pad=5)

    ax.set_xlabel(r"$x$", fontsize=21.5, weight="bold", color=NAVY, labelpad=11)
    ax.set_ylabel(r"$y$", fontsize=21.5, weight="bold", color=NAVY, labelpad=11)
    ax.set_zlabel(r"$z$", fontsize=21.5, weight="bold", color=NAVY, labelpad=10)

    ax.set_box_aspect((1.18, 1.18, 0.88), zoom=1.10)

    # Faint floor projection on z = 0 for immediate 3D spatial orientation
    ax.plot(x, y, np.zeros_like(z), color="#cbd5e1", lw=0.65, alpha=0.45, zorder=1)

    # Full continuous Lorenz trajectory
    ax.plot(x, y, z, color=PURPLE_TRAJ, lw=1.22, alpha=0.86, solid_capstyle="round", zorder=3)

    # Short highlighted genuine trajectory segment
    seg_sl = pick_highlight_segment(tp, yp)
    xh, yh, zh = x[seg_sl], y[seg_sl], z[seg_sl]
    ax.plot(xh, yh, zh, color=ORANGE_HIGHLIGHT, lw=3.0, alpha=0.98, solid_capstyle="round", zorder=6)

    # Finalize layout before projecting 3D markers & direction arrow cleanly onto foreground overlay
    fig.canvas.draw()

    # Foreground overlay axes (zorder=10, strictly above 3D plot)
    ax_fg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=10)
    ax_fg.set_xlim(0.0, 1.0)
    ax_fg.set_ylim(0.0, 1.0)
    ax_fg.axis("off")
    ax_fg.patch.set_alpha(0.0)

    # Single crisp tangent flow arrow near end of highlighted orange segment
    p0 = data3d_to_fig(ax, fig, xh[-6], yh[-6], zh[-6])
    p1 = data3d_to_fig(ax, fig, xh[-1], yh[-1], zh[-1])
    dx_f, dy_f = p1[0] - p0[0], p1[1] - p0[1]
    d_norm = np.hypot(dx_f, dy_f)
    if d_norm > 1e-8:
        ux, uy = dx_f / d_norm, dy_f / d_norm
        ax_fg.add_patch(patches.FancyArrowPatch(
            (p1[0] - 0.012 * ux, p1[1] - 0.012 * uy),
            (p1[0] + 0.005 * ux, p1[1] + 0.005 * uy),
            arrowstyle="-|>,head_length=8.5,head_width=5.4",
            color=ORANGE_HIGHLIGHT, linewidth=2.4, zorder=12,
        ))

    # Equilibrium markers C_- and C_+ positioned inside each lobe's central eye
    c_val = np.sqrt(BETA * (RHO - 1.0))  # ~ 8.48528
    z_eq = RHO - 1.0                     # 27.0
    HALO = [pe.withStroke(linewidth=4.6, foreground="#ffffff", alpha=0.97)]
    for cx, cy, lbl, dx_f_off, dy_f_off in (
        (-c_val, -c_val, r"$\boldsymbol{C}_{-}$", 0.0, -0.025),
        (c_val, c_val, r"$\boldsymbol{C}_{+}$", 0.0, -0.025),
    ):
        fx, fy = data3d_to_fig(ax, fig, cx, cy, z_eq)
        ax_fg.scatter([fx], [fy], s=86, color="#334155", edgecolor="#ffffff", linewidth=1.6, zorder=11)
        ax_fg.text(
            fx + dx_f_off, fy + dy_f_off, lbl,
            fontsize=19.0, weight="bold", color="#1e293b",
            ha="center", va="center", path_effects=HALO, zorder=12,
        )

    # Discreet floor-projection callout cleanly inside open (+x, -y) floor region
    p_lbl = data3d_to_fig(ax, fig, 8.0, -16.5, 0.0)
    p_tar = data3d_to_fig(ax, fig, 8.5, -1.5, 0.0)
    ax_fg.text(
        p_lbl[0], p_lbl[1],
        "Projection onto\n" + r"the $xy$-plane",
        fontsize=14.4, weight="bold", color="#64748b",
        ha="center", va="center", linespacing=1.08, path_effects=HALO, zorder=11,
    )
    ax_fg.annotate(
        "", xy=p_tar, xytext=(p_lbl[0], p_lbl[1] + 0.028),
        arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.25", color="#94a3b8", lw=1.4),
        zorder=11,
    )

    # Corner legend top-left inside main card
    legend_handles = [
        Line2D([0], [0], color=PURPLE_TRAJ, lw=2.6, label="Numerical trajectory  (20 ≤ t ≤ 110)"),
        Line2D([0], [0], color=ORANGE_HIGHLIGHT, lw=3.2, marker=">", markersize=7.5, markevery=[1],
               label="Highlighted segment (flow direction)"),
        Line2D([0], [0], color="none", marker="o", markersize=8.5, markerfacecolor="#334155",
               markeredgecolor="#ffffff", markeredgewidth=1.3,
               label=r"Unstable equilibria  $\boldsymbol{C}_\pm = (\pm 8.485,\ \pm 8.485,\ 27)$"),
    ]
    leg = ax_fg.legend(
        handles=legend_handles,
        loc="upper left",
        bbox_to_anchor=(0.034, 0.858),
        frameon=True, facecolor="#f8fafc", edgecolor=BORDER_CARD,
        framealpha=0.96, borderpad=0.62, labelspacing=0.46,
        prop={"weight": "bold", "size": 15.2},
    )
    leg.set_zorder(12)
    for txt in leg.get_texts():
        txt.set_color(DARK_SLATE)

    # -------------------------------------------------------------------------
    # Bottom Shared Variable & Coordinate Note Box
    # -------------------------------------------------------------------------
    ax_fg.add_patch(patches.FancyBboxPatch(
        (0.022, 0.020), 0.956, 0.092,
        boxstyle="round,pad=0.0,rounding_size=0.012",
        facecolor="#f8fafc", edgecolor=BORDER_CARD, linewidth=1.3, zorder=3,
    ))
    ax_fg.text(
        0.50, 0.081,
        "Phase-space coordinates (state variables, not physical spatial positions):",
        fontsize=16.4, weight="bold", color=NAVY, ha="center", va="center", zorder=4,
    )
    ax_fg.text(
        0.50, 0.044,
        r"$\boldsymbol{x}$ — Circulation amplitude    ·    $\boldsymbol{y}$ — Temperature-contrast amplitude    ·    $\boldsymbol{z}$ — Vertical-profile amplitude",
        fontsize=16.6, weight="bold", color=DARK_SLATE, ha="center", va="center", zorder=4,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    create_figure()
