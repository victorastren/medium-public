#!/usr/bin/env python3
"""
Generate publication-quality three-panel infographic:
  "From Discrete Self-Similarity to Finite-Time Blow-Up"
for Section "From Forced to Unforced Blow-Up" of the Navier-Stokes Millennium Problem article.

Panels:
  A. Discrete Self-Similarity in Physical Space: shrinking spatial scales l_n,
     increasing velocity amplitudes A_n, and decreasing cycle durations Delta t_n as t -> T.
  B. Convergence in Self-Similar Variables: periodic profile W(s + S, y) = W(s, y)
     and rescaled solution U(s, y) converging in homogeneous H1 as s -> inf.
  C. Blow-Up Despite Energy Dissipation: diverging velocity gradients
     ||grad u(t)||_{L2} ~ (T - t)^{-1/4} while E(t) decreases to a finite limit E(T^-) < inf
     with integrable dissipation rate ||grad u(t)||_{L2}^2 ~ (T - t)^{-1/2}.

Canvas: 3000 x 1200 px (15.0 x 6.0 in @ 200 DPI), matching the dark editorial palette
and typography hierarchy of the existing Navier-Stokes illustrations.
"""

from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent


def draw_eddy_parcel(ax, cx, cy, scale, col, alpha=0.35, zorder=4):
    """Draw a compact isometric 3D cell whose physical size scales with l_n."""
    dx = scale * 0.56
    dy = scale * 0.25
    dz = scale * 0.58

    b_bot = (cx, cy - dz - dy)
    b_l   = (cx - dx, cy - dz)
    b_r   = (cx + dx, cy - dz)

    t_bot = (cx, cy + dz - dy)
    t_l   = (cx - dx, cy + dz)
    t_r   = (cx + dx, cy + dz)
    t_top = (cx, cy + dz + dy)

    left_poly = Polygon(
        [b_l, b_bot, t_bot, t_l], closed=True,
        facecolor=col, edgecolor=col, linewidth=1.2, alpha=alpha * 0.80, zorder=zorder,
    )
    right_poly = Polygon(
        [b_bot, b_r, t_r, t_bot], closed=True,
        facecolor=col, edgecolor=col, linewidth=1.2, alpha=alpha, zorder=zorder,
    )
    top_poly = Polygon(
        [t_bot, t_r, t_top, t_l], closed=True,
        facecolor=col, edgecolor=col, linewidth=1.35, alpha=alpha * 1.35, zorder=zorder + 1,
    )
    ax.add_patch(left_poly)
    ax.add_patch(right_poly)
    ax.add_patch(top_poly)
    ax.plot([b_bot[0], t_bot[0]], [b_bot[1], t_bot[1]], color=col, lw=1.4, zorder=zorder + 2)


def create_discrete_self_similarity_figure(out_path=None):
    if out_path is None:
        out_path = PROJECT_DIR / "images" / "navier_stokes_discrete_self_similarity.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        "text.usetex": False,
        "mathtext.fontset": "dejavusans",
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    })

    # Exact 3000 x 1200 px canvas
    fig = plt.figure(figsize=(15.0, 6.0), dpi=200, facecolor="#070b12")

    CANVAS_BG   = "#070b12"
    PANEL_BG    = "#0c1322"
    CARD_BG     = "#101828"
    CHIP_BG     = "#0a101d"
    BORDER_COL  = "#1e293b"
    TEXT_TITLE  = "#f8fafc"
    TEXT_MUTED  = "#94a3b8"
    TEXT_LIGHT  = "#e2e8f0"

    CYAN_COL    = "#38bdf8"
    AMBER_COL   = "#fbbf24"
    ROSE_COL    = "#fb7185"
    EMERALD_COL = "#34d399"

    # -------------------------------------------------------------------------
    # Global Title (unchanged size) & Enlarged Subtitle
    # -------------------------------------------------------------------------
    fig.text(
        0.50, 0.948,
        "FROM DISCRETE SELF-SIMILARITY TO FINITE-TIME BLOW-UP",
        fontsize=17.5, fontweight="bold", color=TEXT_TITLE, ha="center", va="center",
    )
    fig.text(
        0.50, 0.896,
        "Proposed Alpöge & Buckmaster (2026) construction: discrete self-similarity, asymptotic convergence in logarithmic time, and finite total energy dissipation",
        fontsize=12.4, color="#cbd5e1", ha="center", va="center",
    )

    # -------------------------------------------------------------------------
    # Three Horizontally Arranged Panel Cards (A, B, C)
    # -------------------------------------------------------------------------
    p_y = 0.072
    p_h = 0.780
    p_w = 0.308
    gap = 0.020
    x_positions = [0.018, 0.018 + p_w + gap, 0.018 + 2 * (p_w + gap)]

    panel_specs = [
        (
            "A. Discrete Self-Similarity\nin Physical Space",
            "Shrinking spatial scales and\nincreasing velocity amplitudes",
            CYAN_COL,
        ),
        (
            "B. Convergence in\nSelf-Similar Variables",
            "Logarithmic time\ns = log(T/(T − t))",
            AMBER_COL,
        ),
        (
            "C. Blow-Up Despite\nEnergy Dissipation",
            "Diverging gradients vs.\ndecreasing kinetic energy",
            ROSE_COL,
        ),
    ]

    panel_axes = []
    for px, (ptitle, psub, pcol) in zip(x_positions, panel_specs):
        ax_p = fig.add_axes([px, p_y, p_w, p_h], facecolor=PANEL_BG, zorder=1)
        for sp in ax_p.spines.values():
            sp.set_edgecolor(BORDER_COL)
            sp.set_linewidth(1.4)
        ax_p.set_xlim(0, 100)
        ax_p.set_ylim(0, 100)
        ax_p.set_xticks([])
        ax_p.set_yticks([])

        ax_p.text(4.8, 97.4, ptitle, fontsize=14.4, fontweight="bold", color=pcol, va="top", linespacing=1.12)
        ax_p.text(4.8, 84.8, psub, fontsize=11.6, color="#cbd5e1", va="top", linespacing=1.12)

        card = FancyBboxPatch(
            (3.0, 2.6), 94.0, 72.8,
            boxstyle="round,pad=0.3,rounding_size=1.8",
            facecolor=CARD_BG, edgecolor=BORDER_COL, linewidth=1.1, zorder=2,
        )
        ax_p.add_patch(card)
        panel_axes.append(ax_p)

    axA, axB, axC = panel_axes

    # =========================================================================
    # PANEL A: Discrete Self-Similarity in Physical Space (exact scaling q = e^{-S/2})
    # =========================================================================
    q_scale = 0.72  # Schematic contraction factor q = e^{-S/2} applied consistently to l_n, A_n, dt_n
    sc_0 = 9.4
    vlen_0 = 13.0
    cy_base = 44.2
    cycle_specs = [
        (18.0, "#38bdf8", r"$\ell_0$", r"$A_0$", "Cycle 0"),
        (45.5, "#fbbf24", r"$\ell_1$", r"$A_1$", "Cycle 1"),
        (68.5, "#fb7185", r"$\ell_2$", r"$A_2$", "Cycle 2"),
    ]
    for n, (cx, col, l_lbl, a_lbl, c_lbl) in enumerate(cycle_specs):
        sc = sc_0 * (q_scale ** n)
        vlen = vlen_0 * (q_scale ** (-n))
        axA.text(cx, 72.5, c_lbl, fontsize=12.6, fontweight="bold", color=TEXT_LIGHT, ha="center", va="center", zorder=6)
        draw_eddy_parcel(axA, cx, cy_base, sc, col, alpha=0.40, zorder=4)

        arr = FancyArrowPatch(
            (cx, cy_base), (cx, cy_base + vlen),
            arrowstyle="-|>", color=col, mutation_scale=14.0, lw=2.5, zorder=6,
        )
        axA.add_patch(arr)
        y_top_diamond = cy_base + 0.85 * sc
        y_lbl = max(cy_base + 0.62 * vlen, y_top_diamond + 3.4)
        axA.text(cx + 3.0, y_lbl, a_lbl, fontsize=15.0, fontweight="bold", color=col, va="center", zorder=7)

        bx_lo, bx_hi = cx - sc * 0.56, cx + sc * 0.56
        by_br = 36.2
        axA.annotate(
            "", xy=(bx_lo, by_br), xytext=(bx_hi, by_br),
            arrowprops=dict(arrowstyle="<->", color="#94a3b8", lw=1.35, shrinkA=0, shrinkB=0), zorder=5,
        )
        axA.text(cx, 32.0, l_lbl, fontsize=14.8, fontweight="bold", color=TEXT_LIGHT, ha="center", va="center", zorder=6)

    for ax0, ax1 in ((27.0, 37.5), (53.0, 61.5)):
        axA.annotate(
            "", xy=(ax1, cy_base), xytext=(ax0, cy_base),
            arrowprops=dict(arrowstyle="-|>", color="#64748b", lw=1.7, mutation_scale=11.5), zorder=5,
        )

    # Singularity marker t -> T and exact geometric-series time ticks dt_n = dt_0 * q^{2n}
    t_start = 7.5
    T_sing = 87.5
    dt_0 = (T_sing - t_start) * (1.0 - q_scale ** 2)
    t_ticks = [t_start]
    for k in range(5):
        t_ticks.append(t_ticks[-1] + dt_0 * (q_scale ** (2 * k)))
    t_ticks.append(T_sing)

    axA.axvline(T_sing, ymin=0.26, ymax=0.69, color=ROSE_COL, ls=":", lw=1.7, alpha=0.85, zorder=4)
    axA.text(85.0, cy_base, r"$\cdots$", fontsize=19.0, fontweight="bold", color=ROSE_COL, ha="right", va="center", zorder=6)
    axA.text(T_sing, 72.5, r"$t \to T$", fontsize=13.6, fontweight="bold", color=ROSE_COL, ha="center", va="center", zorder=6)

    axA.plot([t_ticks[0], t_ticks[-1]], [26.6, 26.6], color="#475569", lw=1.45, zorder=4)
    for tx in t_ticks:
        axA.plot([tx, tx], [25.0, 28.2], color=CYAN_COL if tx < T_sing - 0.1 else ROSE_COL, lw=1.5, zorder=5)
    axA.text(0.5 * (t_ticks[0] + t_ticks[1]), 22.3, r"$\Delta t_0$", fontsize=13.6, fontweight="bold", color="#cbd5e1", ha="center", va="center", zorder=6)
    axA.text(0.5 * (t_ticks[1] + t_ticks[2]), 22.3, r"$\Delta t_1$", fontsize=13.6, fontweight="bold", color="#cbd5e1", ha="center", va="center", zorder=6)
    axA.text(0.5 * (t_ticks[2] + t_ticks[3]), 22.3, r"$\Delta t_2$", fontsize=13.6, fontweight="bold", color="#cbd5e1", ha="center", va="center", zorder=6)
    axA.text(88.8, 22.3, r"$\to 0$", fontsize=13.0, fontweight="bold", color=ROSE_COL, ha="center", va="center", zorder=6)

    # Enlarged 2-line Equation Chip in Panel A
    chipA = FancyBboxPatch(
        (5.0, 3.6), 90.0, 15.6,
        boxstyle="round,pad=0.3,rounding_size=1.2",
        facecolor=CHIP_BG, edgecolor="#1e3a5f", lw=1.2, zorder=4,
    )
    axA.add_patch(chipA)
    axA.text(
        50.0, 14.3,
        r"$\ell_{n+1} = e^{-S/2}\ell_n, \qquad A_{n+1} = e^{S/2}A_n$",
        fontsize=15.4, fontweight="bold", color=CYAN_COL, ha="center", va="center", zorder=5,
    )
    axA.text(
        50.0, 7.2,
        r"$\Delta t_{n+1} = e^{-S}\Delta t_n$",
        fontsize=15.4, fontweight="bold", color="#7dd3fc", ha="center", va="center", zorder=5,
    )

    # =========================================================================
    # PANEL B: Convergence in Self-Similar Variables (logarithmic time s)
    # =========================================================================
    pxB = x_positions[1]
    axB_plot = fig.add_axes(
        [pxB + 0.175 * p_w, p_y + 0.314 * p_h, 0.755 * p_w, 0.408 * p_h],
        facecolor="#080e1a", zorder=5,
    )
    S_per = 1.0
    s_grid = np.linspace(0.0, 3.6, 500)
    W_curve = 0.50 * np.sin(2.0 * np.pi * s_grid / S_per) + 0.18 * np.cos(4.0 * np.pi * s_grid / S_per - 0.6)
    pert = 0.56 * np.exp(-1.12 * s_grid) * np.cos(1.35 * np.pi * s_grid + 0.25)
    U_curve = W_curve + pert

    axB_plot.axhline(0.0, color="#1e293b", lw=0.9, zorder=1)
    for k_per in (1.0, 2.0, 3.0):
        axB_plot.axvline(k_per, color="#1e293b", lw=0.9, ls=":", zorder=1)

    axB_plot.fill_between(s_grid, W_curve, U_curve, color=AMBER_COL, alpha=0.14, zorder=2)
    axB_plot.plot(s_grid, W_curve, color=CYAN_COL, lw=2.3, ls="--", label=r"Periodic profile $\mathbf{W}$", zorder=4)
    axB_plot.plot(s_grid, U_curve, color=AMBER_COL, lw=2.3, ls="-", label=r"Rescaled solution $\mathbf{U}$", zorder=5)

    # Period S arrow placed cleanly on the left (s in [0.18, 1.18]), completely clear of upper-right legend
    s_arr_0 = 0.18
    axB_plot.annotate(
        "", xy=(s_arr_0, 0.90), xytext=(s_arr_0 + 1.0, 0.90),
        arrowprops=dict(arrowstyle="<->", color=CYAN_COL, lw=1.5, shrinkA=0, shrinkB=0), zorder=6,
    )
    axB_plot.text(s_arr_0 + 0.50, 1.00, "period S", fontsize=12.8, fontweight="bold", color=CYAN_COL, ha="center", va="bottom")

    axB_plot.set_xlim(0.0, 3.6)
    axB_plot.set_ylim(-1.02, 1.38)
    axB_plot.set_xticks([0.0, 1.0, 2.0, 3.0])
    axB_plot.set_xticklabels(["0", "S", "2S", "3S"], fontsize=12.0, fontweight="bold", color=TEXT_LIGHT)
    axB_plot.set_yticks([])
    axB_plot.set_xlabel(r"Logarithmic time $s \to \infty$", fontsize=12.6, fontweight="bold", color=TEXT_LIGHT, labelpad=3)
    axB_plot.set_ylabel("Profile observable\n(schematic)", fontsize=11.6, fontweight="bold", color=TEXT_MUTED, labelpad=4, multialignment="center")
    for sp in axB_plot.spines.values():
        sp.set_edgecolor("#334155")
        sp.set_linewidth(1.0)
    axB_plot.tick_params(colors=TEXT_MUTED, length=3)

    legB = axB_plot.legend(
        loc="upper right", frameon=True, facecolor="#0d1526", edgecolor="#334155",
        fontsize=11.0, labelcolor=TEXT_LIGHT, handlelength=1.7, borderpad=0.28, labelspacing=0.24,
    )
    legB.get_frame().set_linewidth(0.9)

    chipB = FancyBboxPatch(
        (5.0, 3.6), 90.0, 15.6,
        boxstyle="round,pad=0.3,rounding_size=1.2",
        facecolor=CHIP_BG, edgecolor="#78350f", lw=1.2, zorder=4,
    )
    axB.add_patch(chipB)
    axB.text(
        50.0, 11.4,
        r"$\|\mathbf{U}(s,\cdot) - \mathbf{W}(s,\cdot)\|_{\dot{H}^1} \longrightarrow 0$",
        fontsize=17.0, fontweight="bold", color=AMBER_COL, ha="center", va="center", zorder=5,
    )

    # =========================================================================
    # PANEL C: Blow-Up Despite Energy Dissipation
    # =========================================================================
    pxC = x_positions[2]
    axC_grad = fig.add_axes(
        [pxC + 0.155 * p_w, p_y + 0.314 * p_h, 0.725 * p_w, 0.408 * p_h],
        facecolor="#080e1a", zorder=5,
    )
    axC_eng = axC_grad.twinx()

    tau_grid = np.linspace(1.0, 0.008, 600)
    t_norm = 1.0 - tau_grid
    grad_norm = tau_grid ** (-0.25)
    energy_norm = 1.0 - 0.34 * (1.0 - np.sqrt(tau_grid))

    l1, = axC_grad.plot(t_norm, grad_norm, color=ROSE_COL, lw=2.4, label=r"$\|\nabla\mathbf{u}(t)\|_{L^2} \asymp (T-t)^{-1/4}$", zorder=6)
    l2, = axC_eng.plot(t_norm, energy_norm, color=EMERALD_COL, lw=2.4, label=r"Kinetic energy $E(t)$", zorder=5)

    axC_grad.axvline(1.0, color=ROSE_COL, lw=1.5, ls="--", alpha=0.85, zorder=4)
    axC_grad.text(0.96, 3.45, r"$t \to T^-$", fontsize=13.2, fontweight="bold", color=ROSE_COL, ha="right", va="top")

    # E(T^-) < infinity cleanly above emerald curve and clear of legend & rose curve
    axC_eng.plot([1.0], [0.66], "o", color=EMERALD_COL, markersize=5.8, zorder=7)
    axC_eng.annotate(
        r"$E(T^-) < \infty$",
        xy=(0.990, 0.675),
        xytext=(0.76, 1.04),
        fontsize=13.2, fontweight="bold", color=EMERALD_COL,
        ha="center", va="center",
        arrowprops=dict(arrowstyle="-|>", color=EMERALD_COL, lw=1.4, shrinkA=3, shrinkB=4),
        zorder=8,
    )

    axC_grad.text(
        0.035, 1.66,
        r"$\int_0^T (T-t)^{-1/2}\,dt = 2\sqrt{T} < \infty$",
        fontsize=12.6, fontweight="bold", color="#fde68a",
        ha="left", va="center",
        bbox=dict(boxstyle="round,pad=0.26", facecolor="#1c1503", edgecolor="#92400e", lw=1.0),
        zorder=8,
    )

    axC_grad.set_xlim(0.0, 1.03)
    axC_grad.set_ylim(0.7, 3.85)
    axC_eng.set_ylim(0.20, 1.62)  # Places E(0)=1.0 at ~56% height so upper-left legend stays completely clear

    axC_grad.set_xticks([0.0, 0.5, 1.0])
    axC_grad.set_xticklabels(["0", "T/2", "T"], fontsize=12.0, fontweight="bold", color=TEXT_LIGHT)
    axC_grad.set_yticks([])
    axC_eng.set_yticks([])
    axC_grad.set_xlabel("Physical time t", fontsize=12.6, fontweight="bold", color=TEXT_LIGHT, labelpad=3)
    axC_grad.set_ylabel(r"$\|\nabla\mathbf{u}\|_{L^2}$", fontsize=14.4, fontweight="bold", color=ROSE_COL, labelpad=4)
    axC_eng.set_ylabel(r"$E(t)$", fontsize=14.4, fontweight="bold", color=EMERALD_COL, labelpad=4)

    for sp in axC_grad.spines.values():
        sp.set_edgecolor("#334155")
        sp.set_linewidth(1.0)
    for sp in axC_eng.spines.values():
        sp.set_edgecolor("#334155")
        sp.set_linewidth(1.0)
    axC_grad.tick_params(colors=TEXT_MUTED, length=3)

    legC = axC_grad.legend(
        handles=[l1, l2], loc="upper left", frameon=True,
        facecolor="#0d1526", edgecolor="#334155",
        fontsize=11.0, labelcolor=TEXT_LIGHT, handlelength=1.6, borderpad=0.25, labelspacing=0.22,
    )
    legC.get_frame().set_linewidth(0.9)

    chipC = FancyBboxPatch(
        (5.0, 3.6), 90.0, 15.6,
        boxstyle="round,pad=0.3,rounding_size=1.2",
        facecolor=CHIP_BG, edgecolor="#881337", lw=1.2, zorder=4,
    )
    axC.add_patch(chipC)
    axC.text(
        50.0, 14.3,
        r"$\|\nabla\mathbf{u}\|_{L^2} \asymp (T-t)^{-1/4}$",
        fontsize=15.2, fontweight="bold", color="#fecdd3", ha="center", va="center", zorder=5,
    )
    axC.text(
        50.0, 7.2,
        r"$dE/dt = -\nu\|\nabla\mathbf{u}\|_{L^2}^2 \leq 0$",
        fontsize=15.0, fontweight="bold", color="#fda4af", ha="center", va="center", zorder=5,
    )

    # -------------------------------------------------------------------------
    # Subtle Footer Disclaimer (significantly enlarged)
    # -------------------------------------------------------------------------
    fig.text(
        0.50, 0.032,
        "Conceptual illustration of scaling, asymptotic profile convergence, and dissipation balance — not numerical data from the Alpöge–Buckmaster construction.",
        fontsize=13.2, style="italic", color=TEXT_MUTED, ha="center", va="center",
    )

    fig.savefig(out_path, dpi=200, facecolor=CANVAS_BG, edgecolor="none")
    plt.close(fig)
    print(f"[OK] Generated {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")
    return out_path


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else None
    create_discrete_self_similarity_figure(out_file)
