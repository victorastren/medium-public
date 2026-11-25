#!/usr/bin/env python3
r"""
generate_kam_invariant_tori_picture.py

Generates a static three-panel conceptual illustration for Section 2 of Article 3
("Order and Chaos: The Road to Modern Dynamics III"):
  "Invariant Tori, Resonances, and the KAM Picture"

Schematic Poincaré sections:
  - Panel A: Integrable motion (nested invariant curves as torus cross-sections;
             dense quasiperiodic return points)
  - Panel B: Resonance (k · ω = 0, finite periodic return set, small divisors,
             nondegeneracy det(∂ω/∂I) ≠ 0)
  - Panel C: Small perturbation — the KAM picture (surviving deformed KAM curves,
             resonance island chain, thin chaotic layer, Diophantine condition)

Typography and font-size hierarchy match kam_poincare_sections.png and
homoclinic_tangle_to_horseshoe.png.

Output:
  images/kam_invariant_tori_picture.png
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "kam_invariant_tori_picture.png"


def deformed_radius(theta, r0, eps2=0.055, eps3=0.025, eps5=0.0):
    """Smoothly deformed closed curve representing a surviving KAM torus cross-section."""
    return r0 * (
        1.0
        + eps2 * np.cos(2.0 * theta - 0.55)
        + eps3 * np.cos(3.0 * theta + 0.90)
        + eps5 * np.cos(5.0 * (theta - np.pi / 2.0))
    )


def build_island_contour(theta_center, r_res, dr_half, dth_half, n_pts=160):
    """
    Build a smooth pendulum-like cat's-eye resonance island contour centered at
    (r_res, theta_center) in polar coordinates.
    """
    u = np.linspace(0.0, 2.0 * np.pi, n_pts)
    th = theta_center + dth_half * np.cos(u)
    r = r_res + dr_half * np.sin(u) * (0.92 + 0.08 * np.cos(2.0 * u))
    r_def = deformed_radius(th, r, eps2=0.045, eps3=0.020, eps5=0.0)
    return r_def * np.cos(th), r_def * np.sin(th)


def draw_directional_arrow_on_circle(ax, r, theta_rad, color, cy=0.0, ccw=True, scale=15.0, zorder=8):
    """Place a crisp arrowhead tangent to a circle of radius r centered at (0, cy)."""
    dth = 0.06 if ccw else -0.06
    p0 = (r * np.cos(theta_rad - dth), cy + r * np.sin(theta_rad - dth))
    p1 = (r * np.cos(theta_rad), cy + r * np.sin(theta_rad))
    ax.annotate(
        "",
        xy=p1,
        xytext=p0,
        arrowprops=dict(arrowstyle="-|>", color=color, lw=0.0, mutation_scale=scale, shrinkA=0, shrinkB=0),
        zorder=zorder,
    )


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        "text.usetex": False,
        "mathtext.fontset": "dejavuserif",
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "axes.edgecolor": "#94a3b8",
        "axes.linewidth": 1.3,
    })

    # Matching kam_poincare_sections.png width (19.8 in) with compact balanced height (10.2 in)
    fig_w, fig_h = 19.8, 10.2
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor="#ffffff")

    # Palette harmonized with homoclinic_tangle_to_horseshoe.png & kam_poincare_sections.png
    NAVY = "#0f172a"
    DARK_SLATE = "#1e293b"
    MUTED_SLATE = "#475569"
    BORDER_CARD = "#cbd5e1"
    BG_CARD = "#f8fafc"
    BG_BOX = "#ffffff"

    BLUE_ACCENT = "#2563eb"
    BLUE_DARK = "#1d4ed8"
    BLUE_MID = "#60a5fa"
    BLUE_SOFT = "#93c5fd"
    BLUE_LIGHT = "#eff6ff"
    BLUE_BORDER = "#93c5fd"

    ORANGE_ACCENT = "#ea580c"
    ORANGE_DARK = "#c2410c"
    ORANGE_LIGHT = "#fff7ed"
    ORANGE_FILL = "#ffedd5"
    ORANGE_BORDER = "#fdba74"

    TEAL_ACCENT = "#0d9488"
    TEAL_DARK = "#0f766e"
    TEAL_LIGHT = "#f0fdfa"
    TEAL_BORDER = "#5eead4"

    CHAOS_PURPLE = "#6d28d9"
    CHAOS_DOT = "#7c3aed"
    CHAOS_BAND = "#ddd6fe"

    EQ_BG = "#f1f5f9"
    EQ_BORDER = "#94a3b8"
    EQ_TEXT = "#334155"

    halo = [pe.withStroke(linewidth=4.0, foreground="#ffffff", alpha=0.96)]

    # -------------------------------------------------------------------------
    # Global Title & Subtitle (matching kam_poincare_sections.png: 29.2 / 21.0 pt)
    # -------------------------------------------------------------------------
    fig.text(
        0.5,
        0.966,
        "Invariant Tori, Resonances, and the KAM Picture",
        fontsize=29.2,
        weight="bold",
        color=NAVY,
        ha="center",
        va="center",
    )
    fig.text(
        0.5,
        0.924,
        "Schematic Poincaré sections: surviving regular curves and resonant breakup under perturbation",
        fontsize=20.8,
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
    y_card = 0.018
    h_card = 0.876
    x1, w1 = 0.012, 0.312
    x2, w2 = 0.344, 0.312
    x3, w3 = 0.676, 0.312

    panels_spec = [
        (
            x1, w1, "A",
            "Integrable motion",
            "Invariant tori appear as nested\ncurves in a Poincaré section",
            BLUE_ACCENT, BLUE_LIGHT, BLUE_BORDER, 15.6,
        ),
        (
            x2, w2, "B",
            "Resonance",
            "Commensurable frequencies give periodic\nreturns; small divisors arise near resonance",
            ORANGE_ACCENT, ORANGE_LIGHT, ORANGE_BORDER, 14.0,
        ),
        (
            x3, w3, "C",
            "Small perturbation:\nthe KAM picture",
            "Many nonresonant curves survive,\nwhile resonant ones can break up",
            TEAL_ACCENT, TEAL_LIGHT, TEAL_BORDER, 15.6,
        ),
    ]

    hbar_h = 0.148
    badge_y = y_card + h_card - hbar_h / 2.0

    for px, pw, letter, title, subtitle, acc_color, bg_tint, bdr_color, sub_fs in panels_spec:
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

        badge_x = px + 0.0235
        r_x = 0.0130
        r_y = r_x * (fig_w / fig_h)
        ax_bg.add_patch(patches.Ellipse(
            (badge_x, badge_y), width=2.0 * r_x, height=2.0 * r_y,
            facecolor=acc_color, edgecolor="none", zorder=3,
        ))
        ax_bg.text(
            badge_x, badge_y - 0.0005, letter,
            fontsize=18.5, weight="bold", color="#ffffff",
            ha="center", va="center", zorder=4,
        )

        text_offset_x = badge_x + 0.0200
        header_top = y_card + h_card
        header_bot = header_top - hbar_h
        if "\n" in title:
            ax_bg.text(
                text_offset_x, header_top - 0.010, title,
                fontsize=20.2, weight="bold", color=NAVY,
                va="top", linespacing=1.05, zorder=4,
            )
            ax_bg.text(
                text_offset_x, header_bot + 0.010, subtitle,
                fontsize=sub_fs, weight="bold", color=MUTED_SLATE,
                va="bottom", linespacing=1.08, zorder=4,
            )
        else:
            ax_bg.text(
                text_offset_x, badge_y + 0.030, title,
                fontsize=21.0, weight="bold", color=NAVY,
                va="center", zorder=4,
            )
            ax_bg.text(
                text_offset_x, badge_y - 0.022, subtitle,
                fontsize=sub_fs, weight="bold", color=MUTED_SLATE,
                va="center", linespacing=1.10, zorder=4,
            )

    # Progression arrows between headers (A -> B -> C)
    for gap_x0, gap_x1 in ((x1 + w1 + 0.003, x2 - 0.003), (x2 + w2 + 0.003, x3 - 0.003)):
        ax_bg.add_patch(patches.FancyArrowPatch(
            (gap_x0, badge_y), (gap_x1, badge_y),
            arrowstyle="-|>,head_length=6.5,head_width=4.2",
            color="#64748b", linewidth=2.0, zorder=5,
        ))

    # Compact bottom explanatory boxes whose left/right edges align EXACTLY with the square plots above
    y_box = 0.030
    h_box = 0.164
    y_plot = 0.208
    h_plot = 0.524
    w_aligned = h_plot * (fig_h / fig_w)  # exact rendered square width in figure coordinates (~0.2699)

    def render_bottom_box(px, pw, text_str, fontsize=14.0, linespacing=1.15):
        bx0 = px + (pw - w_aligned) / 2.0
        ax_bg.add_patch(patches.FancyBboxPatch(
            (bx0, y_box), w_aligned, h_box,
            boxstyle="round,pad=0.0,rounding_size=0.012",
            facecolor=BG_BOX, edgecolor=BORDER_CARD, linewidth=1.2, zorder=3,
        ))
        ax_bg.text(
            px + pw / 2.0, y_box + h_box / 2.0,
            text_str,
            fontsize=fontsize, weight="bold", color=DARK_SLATE,
            ha="center", va="center", linespacing=linespacing, zorder=4,
        )

    def setup_plot_axis(px, pw):
        ax = fig.add_axes([px + (pw - w_aligned) / 2.0, y_plot, w_aligned, h_plot], zorder=5)
        ax.set_facecolor("#ffffff")
        ax.set_xlim(-2.25, 2.25)
        ax.set_ylim(-2.25, 2.25)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks([])
        ax.set_yticks([])
        for gx in np.linspace(-1.5, 1.5, 7):
            ax.axvline(gx, color="#f1f5f9", lw=1.0, zorder=1)
        for gy in np.linspace(-1.5, 1.5, 7):
            ax.axhline(gy, color="#f1f5f9", lw=1.0, zorder=1)
        return ax

    th_full = np.linspace(0.0, 2.0 * np.pi, 400)
    radii_base = [0.24, 0.48, 0.72, 0.98, 1.24, 1.46]
    r_focus = 0.98
    cy = 0.02  # Shared vertical center leaving generous top/bottom space for 14-15pt labels

    # =========================================================================
    # PANEL A: Integrable motion on nested invariant curves (cross-sections of tori)
    # =========================================================================
    ax1 = setup_plot_axis(x1, w1)

    ax1.plot(0.0, cy, "o", color="#64748b", markersize=4.8, zorder=5)

    for r in radii_base:
        if abs(r - r_focus) < 1e-6:
            ax1.plot(r * np.cos(th_full), cy + r * np.sin(th_full),
                     color="#dbeafe", lw=8.5, alpha=0.82, zorder=3)
            ax1.plot(r * np.cos(th_full), cy + r * np.sin(th_full),
                     color=BLUE_ACCENT, lw=2.6, zorder=5)
        else:
            ax1.plot(r * np.cos(th_full), cy + r * np.sin(th_full),
                     color=BLUE_SOFT, lw=1.8, alpha=0.92, zorder=3)

    # Dense quasiperiodic iterates (golden-ratio rotation alpha)
    alpha_gold = (np.sqrt(5.0) - 1.0) / 2.0
    n_qp = 54
    th_qp = 0.35 + 2.0 * np.pi * alpha_gold * np.arange(n_qp)
    ax1.scatter(
        r_focus * np.cos(th_qp),
        cy + r_focus * np.sin(th_qp),
        s=22,
        facecolor="#1d4ed8",
        edgecolor="#ffffff",
        linewidth=0.65,
        zorder=7,
    )
    draw_directional_arrow_on_circle(ax1, r_focus, np.deg2rad(42), BLUE_DARK, cy=cy, ccw=True, scale=15.5, zorder=8)
    draw_directional_arrow_on_circle(ax1, r_focus, np.deg2rad(222), BLUE_DARK, cy=cy, ccw=True, scale=15.5, zorder=8)

    # Compact fused mathematical notation chip (upper-left, large crisp bold math)
    ax1.text(
        -2.14, 2.13,
        r"$\boldsymbol{H = H_0(I),\;\omega = \omega(I)}$",
        fontsize=16.6, weight="bold", color=DARK_SLATE,
        ha="left", va="top",
        bbox=dict(boxstyle="round,pad=0.22", facecolor=EQ_BG, edgecolor=EQ_BORDER, linewidth=1.1),
        zorder=11,
    )

    # Label: Invariant curves (tori cross-sections)
    ax1.annotate(
        "Invariant curves\n(tori sections)",
        xy=(1.46 * np.cos(np.deg2rad(44)), cy + 1.46 * np.sin(np.deg2rad(44))),
        xytext=(1.42, 1.82),
        fontsize=14.0, weight="bold", color=BLUE_DARK,
        ha="center", va="center", linespacing=1.08,
        path_effects=halo,
        arrowprops=dict(arrowstyle="->", color=BLUE_ACCENT, lw=1.9, shrinkA=3, shrinkB=3),
        zorder=12,
    )

    # Label: Quasiperiodic orbit (cleanly below the outer curve)
    ax1.annotate(
        "Quasiperiodic orbit\n(dense return points)",
        xy=(r_focus * np.cos(np.deg2rad(-54)), cy + r_focus * np.sin(np.deg2rad(-54))),
        xytext=(0.74, -1.86),
        fontsize=14.2, weight="bold", color=BLUE_DARK,
        ha="center", va="center", linespacing=1.10,
        bbox=dict(boxstyle="round,pad=0.22", facecolor="#ffffff", edgecolor=BLUE_BORDER, linewidth=1.1),
        arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.9, shrinkA=3, shrinkB=4),
        zorder=12,
    )

    render_bottom_box(
        x1, w1,
        "In an integrable system, invariant tori\n"
        "appear as nested closed curves in a\n"
        "Poincaré section. Quasiperiodic orbits\n"
        "fill a curve densely, with frequencies\n"
        "determined by the action variables.",
        fontsize=14.0,
        linespacing=1.16,
    )

    # =========================================================================
    # PANEL B: Resonance, small divisors, and nondegeneracy
    # =========================================================================
    ax2 = setup_plot_axis(x2, w2)

    ax2.plot(0.0, cy, "o", color="#64748b", markersize=4.8, zorder=5)

    for r in radii_base:
        if abs(r - r_focus) < 1e-6:
            ax2.plot(r * np.cos(th_full), cy + r * np.sin(th_full),
                     color=ORANGE_FILL, lw=9.0, alpha=0.85, zorder=3)
            ax2.plot(r * np.cos(th_full), cy + r * np.sin(th_full),
                     color=ORANGE_ACCENT, lw=2.8, zorder=5)
        else:
            ax2.plot(r * np.cos(th_full), cy + r * np.sin(th_full),
                     color=BLUE_SOFT, lw=1.5, alpha=0.68, zorder=3)

    # Closed 2:5 periodic resonance: 5 discrete return points + subtle dashed map jumps
    n_res = 5
    step_jump = 2
    th_nodes = np.pi / 2.0 + 2.0 * np.pi * np.arange(n_res) / n_res
    pts_x = r_focus * np.cos(th_nodes)
    pts_y = cy + r_focus * np.sin(th_nodes)

    for k in range(n_res):
        k_next = (k + step_jump) % n_res
        ax2.add_patch(patches.FancyArrowPatch(
            (pts_x[k], pts_y[k]), (pts_x[k_next], pts_y[k_next]),
            connectionstyle="arc3,rad=0.14",
            arrowstyle="-|>,head_length=6.0,head_width=3.6",
            color=ORANGE_DARK,
            linestyle=(0, (4, 3)),
            linewidth=1.35,
            alpha=0.52,
            shrinkA=8.5,
            shrinkB=9.0,
            zorder=6,
        ))

    ax2.scatter(
        pts_x, pts_y,
        s=112, facecolor=ORANGE_ACCENT, edgecolor="#ffffff", linewidth=1.8, zorder=8,
    )

    # Compact resonance condition chip (upper-left, large bold math)
    ax2.add_patch(patches.FancyBboxPatch(
        (-2.14, 1.50), 1.56, 0.64,
        boxstyle="round,pad=0.0,rounding_size=0.10",
        facecolor=ORANGE_LIGHT, edgecolor=ORANGE_BORDER, linewidth=1.2, zorder=10,
    ))
    ax2.text(
        -1.36, 1.94,
        r"$\boldsymbol{k \cdot \omega = 0}$",
        fontsize=16.8, weight="bold", color=ORANGE_DARK,
        ha="center", va="center", zorder=11,
    )
    ax2.text(
        -1.36, 1.65,
        "rational ratio",
        fontsize=13.4, weight="bold", color=ORANGE_DARK,
        ha="center", va="center", zorder=11,
    )

    # Secondary small-divisor note (upper-right, large bold math)
    ax2.add_patch(patches.FancyBboxPatch(
        (0.56, 1.50), 1.58, 0.64,
        boxstyle="round,pad=0.0,rounding_size=0.10",
        facecolor=EQ_BG, edgecolor=EQ_BORDER, linewidth=1.1, zorder=10,
    ))
    ax2.text(
        1.35, 1.97,
        "Small divisors:",
        fontsize=13.2, weight="bold", color=EQ_TEXT,
        ha="center", va="center", zorder=11,
    )
    ax2.text(
        1.35, 1.67,
        r"$\boldsymbol{k \cdot \omega \approx 0}$",
        fontsize=16.8, weight="bold", color=DARK_SLATE,
        ha="center", va="center", zorder=11,
    )

    # Label: Resonant curve (finite return set)
    ax2.annotate(
        "Resonant curve\n(finite return set)",
        xy=(pts_x[3], pts_y[3]),
        xytext=(1.04, -1.34),
        fontsize=13.8, weight="bold", color=ORANGE_DARK,
        ha="center", va="center", linespacing=1.08,
        bbox=dict(boxstyle="round,pad=0.20", facecolor="#ffffff", edgecolor=ORANGE_BORDER, linewidth=1.1),
        arrowprops=dict(arrowstyle="->", color=ORANGE_ACCENT, lw=1.9, shrinkA=3, shrinkB=6),
        zorder=12,
    )

    # Bottom note inside Panel B for nondegeneracy condition (large crisp bold math)
    ax2.text(
        0.0, -2.11,
        r"Nondegeneracy: $\mathbf{det}(\boldsymbol{\partial\omega / \partial I}) \boldsymbol{\neq 0}$",
        fontsize=15.8, weight="bold", color=DARK_SLATE,
        ha="center", va="bottom",
        bbox=dict(boxstyle="round,pad=0.20", facecolor=EQ_BG, edgecolor=EQ_BORDER, linewidth=1.0),
        zorder=11,
    )

    render_bottom_box(
        x2, w2,
        r"Resonance ($\boldsymbol{k \cdot \omega = 0}$) produces periodic orbits" + "\n"
        "meeting the section in a finite return set.\n"
        "Near resonances, small divisors can amplify\n"
        "perturbative corrections; nondegeneracy\n"
        "ensures a nonsingular frequency derivative.",
        fontsize=14.0,
        linespacing=1.16,
    )

    # =========================================================================
    # PANEL C: Small perturbation — the KAM picture
    # =========================================================================
    ax3 = setup_plot_axis(x3, w3)

    ax3.plot(0.0, cy, "o", color="#64748b", markersize=4.8, zorder=5)

    # 1) Thin chaotic layer enveloping the broken resonant separatrix (r ≈ r_focus = 0.98)
    r_ch_in = deformed_radius(th_full, r_focus - 0.12, eps2=0.045, eps3=0.020)
    r_ch_out = deformed_radius(th_full, r_focus + 0.12, eps2=0.045, eps3=0.020)
    band_x = np.concatenate([r_ch_out * np.cos(th_full), (r_ch_in * np.cos(th_full))[::-1]])
    band_y = cy + np.concatenate([r_ch_out * np.sin(th_full), (r_ch_in * np.sin(th_full))[::-1]])
    ax3.add_patch(patches.Polygon(
        np.column_stack([band_x, band_y]),
        closed=True, facecolor=CHAOS_BAND, edgecolor="none", alpha=0.52, zorder=2,
    ))

    rng = np.random.default_rng(42)
    n_pts_chaos = 460
    th_c = rng.uniform(0.0, 2.0 * np.pi, n_pts_chaos)
    isl_cos = np.cos(5.0 * (th_c - np.pi / 2.0))
    dr_sep = 0.088 * np.sqrt(np.maximum(0.0, 0.5 * (1.0 + isl_cos)))
    sign_side = rng.choice([-1.0, 1.0], size=n_pts_chaos)
    jitter = rng.normal(0.0, 0.022, size=n_pts_chaos)
    dr_c = np.where(isl_cos < -0.35, rng.normal(0.0, 0.044, size=n_pts_chaos), sign_side * dr_sep + jitter)
    dr_c = np.clip(dr_c, -0.125, 0.125)
    r_c = deformed_radius(th_c, r_focus + dr_c, eps2=0.045, eps3=0.020)
    ax3.scatter(
        r_c * np.cos(th_c),
        cy + r_c * np.sin(th_c),
        s=5.4, color=CHAOS_DOT, alpha=0.52, linewidths=0.0, zorder=4,
    )

    # 2) Subtle dotted ghost of the broken resonant curve
    r_ghost = deformed_radius(th_full, r_focus, eps2=0.045, eps3=0.020)
    ax3.plot(
        r_ghost * np.cos(th_full), cy + r_ghost * np.sin(th_full),
        color=ORANGE_ACCENT, lw=1.2, ls=":", alpha=0.65, zorder=3,
    )

    # 3) Five-island Poincaré–Birkhoff chain along the broken resonant curve
    th_isl_centers = np.pi / 2.0 + 2.0 * np.pi * np.arange(5) / 5.0
    for th0 in th_isl_centers:
        ix_out, iy_out = build_island_contour(th0, r_focus, dr_half=0.090, dth_half=0.44)
        ax3.add_patch(patches.Polygon(
            np.column_stack([ix_out, cy + iy_out]),
            closed=True, facecolor="#fff7ed", edgecolor=ORANGE_ACCENT, linewidth=1.7, zorder=5,
        ))
        ix_in, iy_in = build_island_contour(th0, r_focus, dr_half=0.048, dth_half=0.24)
        ax3.plot(ix_in, cy + iy_in, color=ORANGE_DARK, lw=1.25, zorder=6)
        r_ctr = deformed_radius(th0, r_focus, eps2=0.045, eps3=0.020)
        ax3.plot(r_ctr * np.cos(th0), cy + r_ctr * np.sin(th0), "o", color=ORANGE_DARK, markersize=3.2, zorder=7)

    th_xpts = th_isl_centers + np.pi / 5.0
    for thx in th_xpts:
        rx = deformed_radius(thx, r_focus, eps2=0.045, eps3=0.020)
        ax3.plot(rx * np.cos(thx), cy + rx * np.sin(thx), "x", color=CHAOS_PURPLE, markersize=4.6, markeredgewidth=1.4, zorder=7)

    # 4) Surviving deformed KAM curves (smooth unbroken blue/teal curves)
    kam_specs = [
        (0.24, BLUE_MID, 1.8, 0.040, 0.015),
        (0.48, BLUE_ACCENT, 2.1, 0.048, 0.020),
        (0.72, TEAL_ACCENT, 2.5, 0.052, 0.024),
        (1.26, TEAL_ACCENT, 2.5, 0.052, 0.024),
        (1.48, BLUE_ACCENT, 2.2, 0.045, 0.020),
    ]
    for r0, col, lw, e2, e3 in kam_specs:
        rk = deformed_radius(th_full, r0, eps2=e2, eps3=e3)
        ax3.plot(rk * np.cos(th_full), cy + rk * np.sin(th_full), color=col, lw=lw, zorder=6)

    # Diophantine condition chip (upper-left, large crisp bold math)
    ax3.add_patch(patches.FancyBboxPatch(
        (-2.14, 1.48), 2.34, 0.66,
        boxstyle="round,pad=0.0,rounding_size=0.10",
        facecolor=EQ_BG, edgecolor=EQ_BORDER, linewidth=1.1, zorder=10,
    ))
    ax3.text(
        -0.97, 1.98,
        "Diophantine condition",
        fontsize=13.2, weight="bold", color=EQ_TEXT,
        ha="center", va="center", zorder=11,
    )
    ax3.text(
        -0.97, 1.67,
        r"$\boldsymbol{|k \cdot \omega| \geq \gamma |k|^{-\tau}}$",
        fontsize=16.6, weight="bold", color=DARK_SLATE,
        ha="center", va="center", zorder=11,
    )

    # Label 1: Surviving KAM curves (upper-right)
    th_kam_lbl = np.deg2rad(46)
    r_kam_lbl = deformed_radius(th_kam_lbl, 1.26, eps2=0.052, eps3=0.024)
    ax3.annotate(
        "Surviving\nKAM curves",
        xy=(r_kam_lbl * np.cos(th_kam_lbl), cy + r_kam_lbl * np.sin(th_kam_lbl)),
        xytext=(1.46, 1.82),
        fontsize=14.2, weight="bold", color=TEAL_DARK,
        ha="center", va="center", linespacing=1.08,
        path_effects=halo,
        arrowprops=dict(arrowstyle="->", color=TEAL_ACCENT, lw=1.9, shrinkA=3, shrinkB=3),
        zorder=12,
    )

    # Label 2: Resonance island chain (lower-left, cleanly below outer curve)
    th_isl_lbl = th_isl_centers[2]
    r_isl_lbl = deformed_radius(th_isl_lbl, r_focus + 0.07, eps2=0.045, eps3=0.020)
    ax3.annotate(
        "Broken resonance\n(island chain)",
        xy=(r_isl_lbl * np.cos(th_isl_lbl), cy + r_isl_lbl * np.sin(th_isl_lbl)),
        xytext=(-1.06, -1.86),
        fontsize=13.8, weight="bold", color=ORANGE_DARK,
        ha="center", va="center", linespacing=1.08,
        bbox=dict(boxstyle="round,pad=0.20", facecolor="#ffffff", edgecolor=ORANGE_BORDER, linewidth=1.1),
        arrowprops=dict(arrowstyle="->", color=ORANGE_ACCENT, lw=1.9, shrinkA=3, shrinkB=3),
        zorder=12,
    )

    # Label 3: Thin chaotic layer (lower-right, cleanly below outer curve)
    th_ch_lbl = th_xpts[3]
    r_ch_lbl = deformed_radius(th_ch_lbl, r_focus + 0.04, eps2=0.045, eps3=0.020)
    ax3.annotate(
        "Thin chaotic\nlayer",
        xy=(r_ch_lbl * np.cos(th_ch_lbl), cy + r_ch_lbl * np.sin(th_ch_lbl)),
        xytext=(1.36, -1.86),
        fontsize=13.8, weight="bold", color=CHAOS_PURPLE,
        ha="center", va="center", linespacing=1.08,
        bbox=dict(boxstyle="round,pad=0.20", facecolor="#ffffff", edgecolor="#c4b5fd", linewidth=1.1),
        arrowprops=dict(arrowstyle="->", color=CHAOS_PURPLE, lw=1.9, shrinkA=3, shrinkB=3),
        zorder=12,
    )

    render_bottom_box(
        x3, w3,
        "Under a small perturbation, many nonresonant\n"
        "tori survive as deformed KAM curves; resonant\n"
        "tori can produce island chains and thin\n"
        "chaotic layers. The Diophantine condition\n"
        "restricts how closely integer combinations\n"
        "of frequencies approach zero.",
        fontsize=14.0,
        linespacing=1.16,
    )

    fig.savefig(output_path, dpi=240, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    create_figure()
