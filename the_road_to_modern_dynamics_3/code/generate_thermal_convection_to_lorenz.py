#!/usr/bin/env python3
r"""
generate_thermal_convection_to_lorenz.py

Generates the three-panel scientific illustration for Section 3.1
("From Atmospheric Convection to the Lorenz Equations") of Article 3:
"Order and Chaos: The Road to Modern Dynamics III"

Panel progression:
  - Panel A: Conductive state (rho < 1; threshold rho = 1), linear vertical
             temperature gradient, purely diffusive heat transfer, no circulation.
  - Panel B: Convective state (rho > 1), counter-rotating convection rolls using
             the exact lowest-mode Saltzman-Lorenz streamfunction & temperature
             expansion, introducing spatial mode amplitudes x, y, z plus a
             vertical temperature-profile inset comparing conductive vs. convective.
  - Panel C: Lorenz's reduced mathematical model — the three coupled ODEs,
             state-variable key (spatial mode amplitudes), and dimensionless
             parameter definitions (Prandtl number sigma = nu/kappa, relative
             heating rho = Ra/Ra_c, roll geometry beta).

Output:
  images/thermal_convection_to_lorenz.png (3168 x 1568 px, 19.8 x 9.8 in @ 160 dpi)
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap

matplotlib.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "dejavuserif",
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "axes.edgecolor": "#cbd5e1",
    "axes.linewidth": 1.3,
})

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_PNG = PROJECT_DIR / "images" / "thermal_convection_to_lorenz.png"


def make_thermal_cmap():
    """Soft, high-contrast scientific thermal colormap (cool blue -> neutral -> warm coral)."""
    return LinearSegmentedColormap.from_list(
        "soft_thermal",
        [
            (0.00, "#5b9bd5"),  # cool cerulean (top / sinking)
            (0.25, "#a9d1f2"),  # soft sky blue
            (0.50, "#f5f7fa"),  # crisp neutral mid-layer
            (0.75, "#f8c4a4"),  # warm apricot
            (1.00, "#e25845"),  # warm coral-red (bottom / rising)
        ],
    )


def add_contour_arrow(ax, x_arr, y_arr, idx, reverse=False, color="#1e293b", lw=2.0, head_l=7.5, head_w=5.0, zorder=8):
    """Place a tangent arrowhead along a streamline contour."""
    n = len(x_arr)
    i0 = idx % n
    step = -2 if reverse else 2
    i1 = (idx + step) % n
    dx = x_arr[i1] - x_arr[i0]
    dy = y_arr[i1] - y_arr[i0]
    norm = np.hypot(dx, dy)
    if norm < 1e-8:
        return
    # Make a short segment centered at i0 so the arrow head aligns strictly with the tangent
    ux, uy = dx / norm, dy / norm
    seg = 0.055
    p0 = (x_arr[i0] - 0.5 * seg * ux, y_arr[i0] - 0.5 * seg * uy)
    p1 = (x_arr[i0] + 0.5 * seg * ux, y_arr[i0] + 0.5 * seg * uy)
    ax.add_patch(patches.FancyArrowPatch(
        p0, p1,
        arrowstyle=f"-|>,head_length={head_l},head_width={head_w}",
        color=color, linewidth=lw, zorder=zorder,
    ))


def draw_plates(ax, show_heat_arrows=True):
    """Draw the cool upper plate and heated lower plate around fluid domain [0, 2] x [0, 1]."""
    # Cool upper plate: Z in [1.00, 1.11]
    ax.add_patch(patches.Rectangle(
        (0.0, 1.00), 2.0, 0.11,
        facecolor="#dbeafe", edgecolor="#2563eb", linewidth=1.4,
        hatch="///", zorder=6,
    ))
    # Subtle inner border line on top of fluid
    ax.plot([0.0, 2.0], [1.00, 1.00], color="#1d4ed8", lw=1.6, zorder=7)
    ax.text(
        1.0, 1.185, "Cool upper plate",
        fontsize=14.4, weight="bold", color="#1e40af",
        ha="center", va="center", zorder=8,
    )

    # Heated lower plate: Z in [-0.11, 0.00]
    ax.add_patch(patches.Rectangle(
        (0.0, -0.11), 2.0, 0.11,
        facecolor="#fee2e2", edgecolor="#dc2626", linewidth=1.4,
        hatch="///", zorder=6,
    ))
    ax.plot([0.0, 2.0], [0.00, 0.00], color="#b91c1c", lw=1.6, zorder=7)

    # Side walls of the fluid cross-section
    ax.plot([0.0, 0.0], [0.0, 1.0], color="#64748b", lw=1.3, zorder=7)
    ax.plot([2.0, 2.0], [0.0, 1.0], color="#64748b", lw=1.3, zorder=7)

    # Bottom label & subtle heating chevrons
    ax.text(
        1.0, -0.215, "Heated lower plate",
        fontsize=14.4, weight="bold", color="#b91c1c",
        ha="center", va="center", zorder=8,
    )
    if show_heat_arrows:
        for hx in (0.20, 0.40, 1.60, 1.80):
            ax.add_patch(patches.FancyArrowPatch(
                (hx, -0.255), (hx, -0.125),
                arrowstyle="-|>,head_length=5.5,head_width=3.8",
                color="#dc2626", linewidth=1.6, zorder=8,
            ))


def draw_temp_profile_inset(ax, convective=False):
    """Draw a clean vertical temperature profile inset T(height)."""
    NAVY = "#0f172a"
    SLATE = "#475569"

    ax.set_facecolor("#ffffff")
    zeta = np.linspace(0.0, 1.0, 300)
    T_cond = 1.0 - zeta

    ax.set_xlim(-0.04, 1.12)
    ax.set_ylim(0.0, 1.0)
    ax.set_xticks([0.0, 1.0])
    ax.set_xticklabels(["Cool", "Hot"], fontsize=13.5, weight="bold", color=SLATE)
    ax.set_yticks([0.0, 1.0])
    ax.set_yticklabels(["Bottom", "Top"], fontsize=13.2, weight="bold", color=SLATE)
    ax.tick_params(axis="both", which="major", length=3.5, width=1.1, colors=SLATE, pad=3)
    ax.text(
        -0.068, 0.50, "Height",
        transform=ax.transAxes, rotation=90,
        fontsize=13.4, weight="bold", color=NAVY,
        ha="center", va="center", zorder=6,
    )

    # Subtle grid
    ax.axhline(0.5, color="#f1f5f9", lw=1.0, zorder=1)
    ax.axvline(0.5, color="#f1f5f9", lw=1.0, zorder=1)

    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("bottom", "left"):
        ax.spines[sp].set_edgecolor("#94a3b8")
        ax.spines[sp].set_linewidth(1.2)

    if not convective:
        ax.plot(T_cond, zeta, color="#2563eb", lw=2.8, zorder=4)
        ax.scatter([1.0, 0.0], [0.0, 1.0], s=32, color=["#dc2626", "#2563eb"], zorder=5)
        ax.set_title("Vertical temperature profile", fontsize=14.6, weight="bold", color=NAVY, pad=6)
        ax.text(
            0.53, 0.67, "Linear conductive\nprofile",
            fontsize=13.4, weight="bold", color="#1e40af",
            ha="left", va="center", linespacing=1.12,
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#eff6ff", edgecolor="#93c5fd", lw=1.0),
            zorder=6,
        )
        ax.annotate(
            "", xy=(0.39, 0.61), xytext=(0.52, 0.65),
            arrowprops=dict(arrowstyle="-|>,head_length=0.5,head_width=0.28", color="#2563eb", lw=1.5),
            zorder=6,
        )
    else:
        a_z = 0.145
        T_conv = T_cond - a_z * np.sin(2.0 * np.pi * zeta)
        ax.fill_betweenx(zeta, T_cond, T_conv, color="#5eead4", alpha=0.48, zorder=2)
        ax.plot(T_cond, zeta, color="#64748b", lw=1.9, ls="--", zorder=3)
        ax.plot(T_conv, zeta, color="#0f766e", lw=2.8, zorder=4)
        ax.scatter([1.0, 0.0], [0.0, 1.0], s=32, color=["#dc2626", "#2563eb"], zorder=5)
        ax.set_title("Vertical temperature profile (mean)", fontsize=14.6, weight="bold", color=NAVY, pad=6)

        # Label linear conductive reference cleanly below the upper deviation lobe
        ax.text(
            0.015, 0.34, "Conductive\n(dashed)",
            fontsize=12.4, weight="bold", color="#475569",
            ha="left", va="center", linespacing=1.06,
            zorder=6,
        )
        ax.annotate(
            "", xy=(0.41, 0.58), xytext=(0.24, 0.45),
            arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.24", color="#64748b", lw=1.4),
            zorder=6,
        )

        # Double-headed horizontal arrow illustrating separation at representative height z_ref = 0.77
        z_ref = 0.77
        t_cond_ref = 1.0 - z_ref
        t_conv_ref = t_cond_ref - a_z * np.sin(2.0 * np.pi * z_ref)
        ax.add_patch(patches.FancyArrowPatch(
            (t_cond_ref, z_ref), (t_conv_ref, z_ref),
            arrowstyle="<|-|>,head_length=4.6,head_width=3.2",
            color="#c2410c", linewidth=2.1, zorder=8,
        ))

        # Callout connecting z to the highlighted deviation below the double-headed arrow
        ax.text(
            0.50, 0.78,
            r"$\boldsymbol{z}$: amplitude of the" + "\ndeviation from the\nconductive profile",
            fontsize=12.3, weight="bold", color="#0f766e",
            ha="left", va="center", linespacing=1.08,
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#f0fdfa", edgecolor="#14b8a6", lw=1.1),
            zorder=7,
        )
        ax.annotate(
            "", xy=(0.35, 0.67), xytext=(0.49, 0.68),
            arrowprops=dict(arrowstyle="-|>,head_length=0.5,head_width=0.28", color="#0f766e", lw=1.6),
            zorder=9,
        )


def create_figure(output_path=None):
    out_path = Path(output_path) if output_path is not None else OUTPUT_PNG
    fig_w, fig_h = 19.8, 9.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=160, facecolor="#ffffff")

    NAVY = "#0f172a"
    DARK_SLATE = "#1e293b"
    MUTED_SLATE = "#475569"
    BORDER_CARD = "#cbd5e1"
    BG_CARD = "#f8fafc"
    BG_BOX = "#ffffff"

    BLUE_ACCENT = "#2563eb"
    BLUE_LIGHT = "#eff6ff"
    BLUE_BORDER = "#93c5fd"

    TEAL_ACCENT = "#0d9488"
    TEAL_DARK = "#0f766e"
    TEAL_LIGHT = "#f0fdfa"
    TEAL_BORDER = "#5eead4"

    PURPLE_ACCENT = "#6366f1"
    PURPLE_DARK = "#4338ca"
    PURPLE_LIGHT = "#eef2ff"
    PURPLE_BORDER = "#a5b4fc"

    # -------------------------------------------------------------------------
    # Global Title & Subtitle (exact Article 3 3-panel typography hierarchy)
    # -------------------------------------------------------------------------
    fig.text(
        0.5, 0.964,
        "From Thermal Convection to the Lorenz Equations",
        fontsize=29.2, weight="bold", color=NAVY, ha="center", va="center",
    )
    fig.text(
        0.5, 0.920,
        "Physical mechanism, reduced mode variables, and governing differential equations",
        fontsize=21.0, style="italic", weight="normal", color=DARK_SLATE, ha="center", va="center",
    )

    ax_bg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=0)
    ax_bg.set_xlim(0.0, 1.0)
    ax_bg.set_ylim(0.0, 1.0)
    ax_bg.axis("off")

    # -------------------------------------------------------------------------
    # Three Equal-Width Parallel Panel Cards (A, B, C)
    # -------------------------------------------------------------------------
    y_card = 0.022
    h_card = 0.870
    x1, w1 = 0.012, 0.312
    x2, w2 = 0.344, 0.312
    x3, w3 = 0.676, 0.312

    hbar_h = 0.134
    badge_y = y_card + h_card - hbar_h / 2.0

    y_box = 0.032
    h_box = 0.128

    panels_spec = [
        (
            x1, w1, "A", "Conductive state",
            "Temperature difference\nbelow onset threshold",
            BLUE_ACCENT, BLUE_LIGHT, BLUE_BORDER,
            "Heat transfers purely by conduction;\nthe fluid remains motionless with a\nlinear vertical temperature gradient.",
        ),
        (
            x2, w2, "B", "Convective state",
            "Temperature difference\nabove onset threshold",
            TEAL_ACCENT, TEAL_LIGHT, TEAL_BORDER,
            "Warm fluid rises and cool fluid sinks,\nforming rolls whose evolution is tracked\nby spatial mode amplitudes " + r"$\boldsymbol{x}$, $\boldsymbol{y}$, and $\boldsymbol{z}$.",
        ),
        (
            x3, w3, "C", "Lorenz’s reduced model",
            "Coupled ODEs and parameters",
            PURPLE_ACCENT, PURPLE_LIGHT, PURPLE_BORDER,
            "The three coupled equations describe the\nonset of convection and, through nonlinear\ncoupling (" + r"$\boldsymbol{xz}$, $\boldsymbol{xy}$" + "), can produce chaotic\nmotion for suitable parameter values.",
        ),
    ]

    for px, pw, letter, title, subtitle, acc_color, bg_tint, bdr_color, box_txt in panels_spec:
        # Card container
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px, y_card), pw, h_card,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.4, zorder=1,
        ))
        # Header band
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

        text_offset_x = badge_x + 0.0205
        is_sub_two_line = "\n" in subtitle
        ax_bg.text(
            text_offset_x, badge_y + (0.031 if is_sub_two_line else 0.024), title,
            fontsize=20.4, weight="bold", color=NAVY, va="center", zorder=4,
        )
        ax_bg.text(
            text_offset_x,
            badge_y + 0.004 if is_sub_two_line else badge_y - 0.022,
            subtitle,
            fontsize=16.4, weight="bold", color=MUTED_SLATE,
            va="top" if is_sub_two_line else "center",
            linespacing=1.04, zorder=4,
        )

        # Bottom summary box
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px + 0.008, y_box), pw - 0.016, h_box,
            boxstyle="round,pad=0.0,rounding_size=0.014",
            facecolor=BG_BOX, edgecolor=bdr_color, linewidth=1.3, zorder=3,
        ))
        n_lines = box_txt.count("\n") + 1
        ax_bg.text(
            px + pw / 2.0, y_box + h_box / 2.0, box_txt,
            fontsize=14.6 if n_lines >= 4 else 15.6,
            weight="bold", color=DARK_SLATE,
            ha="center", va="center",
            linespacing=1.10 if n_lines >= 4 else 1.16,
            zorder=4,
        )

    # Progression arrows between panel headers (A -> B -> C)
    for gap_x0, gap_x1 in ((x1 + w1 + 0.003, x2 - 0.003), (x2 + w2 + 0.003, x3 - 0.003)):
        ax_bg.add_patch(patches.FancyArrowPatch(
            (gap_x0, badge_y), (gap_x1, badge_y),
            arrowstyle="-|>,head_length=6.5,head_width=4.2",
            color="#64748b", linewidth=2.0, zorder=5,
        ))

    cmap = make_thermal_cmap()

    # =========================================================================
    # PANEL A — Conductive state (rho < 1)
    # =========================================================================
    # Regime pill badge
    ax_bg.add_patch(patches.FancyBboxPatch(
        (x1 + 0.012, 0.706), w1 - 0.024, 0.042,
        boxstyle="round,pad=0.0,rounding_size=0.010",
        facecolor=BLUE_LIGHT, edgecolor=BLUE_BORDER, linewidth=1.1, zorder=3,
    ))
    ax_bg.text(
        x1 + w1 / 2.0, 0.727,
        r"Subcritical: $\boldsymbol{\rho} < 1$  (threshold $\boldsymbol{\rho} = 1$)",
        fontsize=15.6, weight="bold", color="#1e3a8a",
        ha="center", va="center", zorder=4,
    )

    # Fluid layer cross-section (Panel A)
    ax_fa = fig.add_axes([x1 + 0.015, 0.420, w1 - 0.030, 0.274], zorder=5)
    ax_fa.set_xlim(-0.04, 2.04)
    ax_fa.set_ylim(-0.28, 1.26)
    ax_fa.axis("off")

    xi = np.linspace(0.0, 2.0, 320)
    ze = np.linspace(0.0, 1.0, 180)
    XI, ZE = np.meshgrid(xi, ze)
    T_a = 1.0 - ZE
    ax_fa.imshow(
        T_a, extent=[0.0, 2.0, 0.0, 1.0], origin="lower",
        cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto", zorder=2,
    )
    # Flat horizontal isotherms
    for iso_z in (0.25, 0.50, 0.75):
        ax_fa.plot([0.02, 1.98], [iso_z, iso_z], color="#ffffff", lw=1.1, ls=":", alpha=0.80, zorder=3)

    # Straight vertical heat-conduction arrows (distinguishes diffusive flux from fluid circulation)
    for ax_x in (0.11, 0.41, 1.59, 1.89):
        ax_fa.add_patch(patches.FancyArrowPatch(
            (ax_x, 0.09), (ax_x, 0.91),
            arrowstyle="-|>,head_length=7.0,head_width=4.6",
            color="#9a3412", linewidth=2.2, zorder=5,
        ))
    ax_fa.text(
        0.26, 0.26, "Heat\nflux",
        fontsize=13.8, weight="bold", color="#7c2d12",
        ha="center", va="center", linespacing=0.96,
        bbox=dict(boxstyle="round,pad=0.18", facecolor="#ffffff", edgecolor="#fdba74", alpha=0.94, lw=1.0),
        zorder=8,
    )

    # Clean white pill callout inside Panel A fluid
    ax_fa.text(
        1.00, 0.52, "Heat transfer by conduction\n(no fluid circulation)",
        fontsize=13.8, weight="bold", color=NAVY,
        ha="center", va="center", linespacing=1.15,
        bbox=dict(boxstyle="round,pad=0.30", facecolor="#ffffff", edgecolor="#94a3b8", alpha=0.95, lw=1.2),
        zorder=9,
    )
    draw_plates(ax_fa, show_heat_arrows=True)

    # Panel A vertical temperature profile inset
    ax_pa = fig.add_axes([x1 + 0.052, 0.200, w1 - 0.082, 0.172], zorder=5)
    draw_temp_profile_inset(ax_pa, convective=False)

    # =========================================================================
    # PANEL B — Convective state (rho > 1)
    # =========================================================================
    ax_bg.add_patch(patches.FancyBboxPatch(
        (x2 + 0.012, 0.706), w2 - 0.024, 0.042,
        boxstyle="round,pad=0.0,rounding_size=0.010",
        facecolor=TEAL_LIGHT, edgecolor=TEAL_BORDER, linewidth=1.1, zorder=3,
    ))
    ax_bg.text(
        x2 + w2 / 2.0, 0.727,
        r"Supercritical: $\boldsymbol{\rho} > 1$  (mode amplitudes $\boldsymbol{x}, \boldsymbol{y}, \boldsymbol{z}$)",
        fontsize=15.6, weight="bold", color=TEAL_DARK,
        ha="center", va="center", zorder=4,
    )

    # Fluid layer cross-section (Panel B) — exact Saltzman-Lorenz spatial modes
    ax_fb = fig.add_axes([x2 + 0.015, 0.420, w2 - 0.030, 0.274], zorder=5)
    ax_fb.set_xlim(-0.04, 2.04)
    ax_fb.set_ylim(-0.28, 1.26)
    ax_fb.axis("off")

    # Temperature field: T = (1 - z) + a_y * (-cos(pi*xi))*sin(pi*z) - a_z * sin(2*pi*z)
    # Warm rising plume at center (xi = 1.0), cool descending plumes at flanks (xi = 0, 2.0)
    T_b = (1.0 - ZE) + 0.34 * (-np.cos(np.pi * XI)) * np.sin(np.pi * ZE) - 0.11 * np.sin(2.0 * np.pi * ZE)
    T_b = np.clip(T_b, 0.0, 1.0)
    ax_fb.imshow(
        T_b, extent=[0.0, 2.0, 0.0, 1.0], origin="lower",
        cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto", zorder=2,
    )

    # Exact streamfunction psi = -sin(pi*xi)*sin(pi*ze)
    # Left roll (xi in (0, 1)): CCW (rises at xi=1, goes left at top, sinks at xi=0)
    # Right roll (xi in (1, 2)): CW  (rises at xi=1, goes right at top, sinks at xi=2)
    PSI = -np.sin(np.pi * XI) * np.sin(np.pi * ZE)
    levels = [-0.82, -0.55, -0.28, 0.28, 0.55, 0.82]
    cs = ax_fb.contour(
        XI, ZE, PSI, levels=levels,
        colors="#1e293b", linewidths=1.55, linestyles="solid", alpha=0.80, zorder=4,
    )

    # Add clean directional arrowheads along the middle contour of each roll
    # Left roll (psi = -0.55, index 1): CCW -> top goes LEFT, bottom goes RIGHT, inner goes UP, outer goes DOWN
    # Right roll (psi = +0.55, index 4): CW  -> top goes RIGHT, bottom goes LEFT, inner goes UP, outer goes DOWN
    for level_idx, is_left in ((1, True), (4, False)):
        segs = cs.allsegs[level_idx]
        if not segs:
            continue
        seg = max(segs, key=len)
        xs_c, ys_c = seg[:, 0], seg[:, 1]
        area = 0.5 * np.sum(xs_c * np.roll(ys_c, -1) - np.roll(xs_c, -1) * ys_c)
        want_ccw = is_left
        rev = (area < 0) if want_ccw else (area > 0)
        idx_top = int(np.argmax(ys_c))
        idx_bot = int(np.argmin(ys_c))
        idx_in = int(np.argmax(xs_c)) if is_left else int(np.argmin(xs_c))
        idx_out = int(np.argmin(xs_c)) if is_left else int(np.argmax(xs_c))
        add_contour_arrow(ax_fb, xs_c, ys_c, idx_top, reverse=rev, color="#1e293b", lw=1.9)
        add_contour_arrow(ax_fb, xs_c, ys_c, idx_bot, reverse=rev, color="#1e293b", lw=1.9)
        add_contour_arrow(ax_fb, xs_c, ys_c, idx_in, reverse=rev, color="#b91c1c", lw=2.2, head_l=8.0, head_w=5.4)
        add_contour_arrow(ax_fb, xs_c, ys_c, idx_out, reverse=rev, color="#1d4ed8", lw=2.2, head_l=8.0, head_w=5.4)

    # Bold central rising warm plume cue & outer descending cool plume cues
    ax_fb.add_patch(patches.FancyArrowPatch(
        (1.00, 0.12), (1.00, 0.70),
        arrowstyle="-|>,head_length=8.0,head_width=5.4",
        color="#b91c1c", linewidth=2.6, zorder=6,
    ))
    for sx in (0.07, 1.93):
        ax_fb.add_patch(patches.FancyArrowPatch(
            (sx, 0.72), (sx, 0.14),
            arrowstyle="-|>,head_length=7.0,head_width=4.8",
            color="#1d4ed8", linewidth=2.2, zorder=6,
        ))

    # Crisp plume labels clear of streamlines and arrowheads
    HALO = [pe.withStroke(linewidth=3.6, foreground="#ffffff", alpha=0.96)]
    ax_fb.text(
        1.00, 0.958, "Warm\nrising",
        fontsize=13.2, weight="bold", color="#991b1b",
        ha="center", va="top", linespacing=0.94, path_effects=HALO, zorder=9,
    )
    ax_fb.text(
        1.955, 0.962, "Cool\nsinking",
        fontsize=13.2, weight="bold", color="#1e3a8a",
        ha="right", va="top", linespacing=0.94, path_effects=HALO, zorder=9,
    )

    # Mode variable x annotation (circulation intensity near left roll)
    ax_fb.text(
        0.50, 0.50, r"$\boldsymbol{x}$: circulation" + "\nmode",
        fontsize=13.5, weight="bold", color=NAVY,
        ha="center", va="center", linespacing=1.08,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor="#0f766e", alpha=0.95, lw=1.2),
        zorder=10,
    )
    ax_fb.annotate(
        "", xy=(0.50, 0.80), xytext=(0.50, 0.65),
        arrowprops=dict(arrowstyle="-|>,head_length=0.5,head_width=0.28", color="#0f766e", lw=1.6),
        zorder=10,
    )

    # Mode variable y annotation (horizontal temperature contrast between rising & sinking currents)
    ax_fb.text(
        1.48, 0.48, r"$\boldsymbol{y}$: horizontal" + "\n" + r"$\Delta T$ mode",
        fontsize=13.5, weight="bold", color="#9a3412",
        ha="center", va="center", linespacing=1.08,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor="#ea580c", alpha=0.95, lw=1.2),
        zorder=10,
    )
    # Horizontal double-headed arrow illustrating warm-center vs cool-edge contrast
    arr_y = patches.FancyArrowPatch(
        (1.06, 0.21), (1.88, 0.21),
        arrowstyle="<|-|>,head_length=6.2,head_width=3.8",
        color="#c2410c", linewidth=2.2, zorder=10,
    )
    arr_y.set_path_effects([pe.withStroke(linewidth=4.2, foreground="#ffffff", alpha=0.88)])
    ax_fb.add_patch(arr_y)

    draw_plates(ax_fb, show_heat_arrows=True)

    # Panel B vertical temperature profile inset (shows z mode distortion)
    ax_pb = fig.add_axes([x2 + 0.052, 0.200, w2 - 0.082, 0.172], zorder=5)
    draw_temp_profile_inset(ax_pb, convective=True)

    # =========================================================================
    # PANEL C — Lorenz's reduced model (ODEs, mode variables, parameters)
    # =========================================================================
    cx_pad = 0.011
    c_left = x3 + cx_pad
    c_w = w3 - 2.0 * cx_pad

    # --- Sub-card 1: Lorenz differential equations ---
    eq_y, eq_h = 0.600, 0.148
    ax_bg.add_patch(patches.FancyBboxPatch(
        (c_left, eq_y), c_w, eq_h,
        boxstyle="round,pad=0.0,rounding_size=0.012",
        facecolor="#ffffff", edgecolor=PURPLE_BORDER, linewidth=1.4, zorder=3,
    ))
    ax_bg.text(
        c_left + 0.012, eq_y + eq_h - 0.017,
        "LORENZ EQUATIONS",
        fontsize=13.2, weight="bold", color=PURPLE_DARK, ha="left", va="center", zorder=4,
    )

    # Pixel-aligned 3-line ODE system centered visually inside box
    x_eq = x3 + w3 * 0.355
    ode_rows = [
        (eq_y + 0.097, r"$\dot{x}$", r"$\sigma(y - x)$"),
        (eq_y + 0.060, r"$\dot{y}$", r"$x(\rho - z) - y$"),
        (eq_y + 0.023, r"$\dot{z}$", r"$xy - \beta z$"),
    ]
    for ry, lhs, rhs in ode_rows:
        ax_bg.text(x_eq - 0.012, ry, lhs, fontsize=19.6, color=NAVY, ha="right", va="center", zorder=5)
        ax_bg.text(x_eq, ry, r"$=$", fontsize=19.6, color=NAVY, ha="center", va="center", zorder=5)
        ax_bg.text(x_eq + 0.012, ry, rhs, fontsize=19.6, color=NAVY, ha="left", va="center", zorder=5)

    # --- Sub-card 2: State variables (spatial mode amplitudes) ---
    sv_y, sv_h = 0.436, 0.156
    ax_bg.add_patch(patches.FancyBboxPatch(
        (c_left, sv_y), c_w, sv_h,
        boxstyle="round,pad=0.0,rounding_size=0.012",
        facecolor="#ffffff", edgecolor=TEAL_BORDER, linewidth=1.3, zorder=3,
    ))
    ax_bg.text(
        c_left + 0.012, sv_y + sv_h - 0.018,
        "STATE VARIABLES (MODE AMPLITUDES)",
        fontsize=13.0, weight="bold", color=TEAL_DARK, ha="left", va="center", zorder=4,
    )
    sv_rows = [
        (sv_y + 0.107, r"$x$", "Convective circulation intensity"),
        (sv_y + 0.075, r"$y$", "Horizontal temperature contrast"),
        (sv_y + 0.032, r"$z$", "Amplitude of vertical\ntemperature-profile distortion"),
    ]
    for ry, sym, desc in sv_rows:
        two_line = "\n" in desc
        ax_bg.add_patch(patches.FancyBboxPatch(
            (c_left + 0.010, ry - 0.0125), 0.024, 0.025,
            boxstyle="round,pad=0.0,rounding_size=0.005",
            facecolor=TEAL_LIGHT, edgecolor=TEAL_BORDER, linewidth=1.0, zorder=4,
        ))
        ax_bg.text(
            c_left + 0.022, ry + 0.0005, sym,
            fontsize=15.8, weight="bold", color=TEAL_DARK, ha="center", va="center", zorder=5,
        )
        ax_bg.text(
            c_left + 0.042, ry, desc,
            fontsize=14.4 if two_line else 14.8,
            weight="bold", color=DARK_SLATE,
            ha="left", va="center",
            linespacing=1.06, zorder=5,
        )

    # --- Sub-card 3: Dimensionless parameters ---
    pm_y, pm_h = 0.170, 0.256
    ax_bg.add_patch(patches.FancyBboxPatch(
        (c_left, pm_y), c_w, pm_h,
        boxstyle="round,pad=0.0,rounding_size=0.012",
        facecolor="#ffffff", edgecolor=PURPLE_BORDER, linewidth=1.3, zorder=3,
    ))
    ax_bg.text(
        c_left + 0.012, pm_y + pm_h - 0.019,
        "DIMENSIONLESS PARAMETERS",
        fontsize=13.0, weight="bold", color=PURPLE_DARK, ha="left", va="center", zorder=4,
    )

    param_rows = [
        (
            pm_y + 0.189,
            r"$\sigma = \dfrac{\nu}{\kappa}$",
            "Prandtl number",
            "kinematic viscosity " + r"$\nu$ /" + "\nthermal diffusivity " + r"$\kappa$",
            0.000,
        ),
        (
            pm_y + 0.112,
            r"$\rho = \dfrac{\mathrm{Ra}}{\mathrm{Ra}_c}$",
            "Normalized Rayleigh number",
            "Rayleigh number " + r"$\mathrm{Ra}$ / onset $\mathrm{Ra}_c$",
            0.0018,
        ),
        (
            pm_y + 0.045,
            r"$\beta$",
            "Roll geometry",
            "parameter determined by the\naspect ratio of the convection rolls",
            0.000,
        ),
    ]
    pill_x0 = c_left + 0.009
    pill_w = 0.064
    formula_left_x = pill_x0 + 0.0085
    text_left_x = pill_x0 + pill_w + 0.009
    for ry, formula, label, detail, y_nudge in param_rows:
        has_frac = "dfrac" in formula
        pill_h = 0.060 if has_frac else 0.044
        is_two_line = "\n" in detail
        ax_bg.add_patch(patches.FancyBboxPatch(
            (pill_x0, ry - pill_h / 2.0), pill_w, pill_h,
            boxstyle="round,pad=0.0,rounding_size=0.006",
            facecolor=PURPLE_LIGHT, edgecolor=PURPLE_BORDER, linewidth=1.0, zorder=4,
        ))
        ax_bg.text(
            formula_left_x if has_frac else (pill_x0 + pill_w / 2.0),
            ry + y_nudge,
            formula,
            fontsize=14.8 if has_frac else 17.8,
            color=NAVY,
            ha="left" if has_frac else "center",
            va="center",
            zorder=5,
        )
        if is_two_line:
            ax_bg.text(
                text_left_x, ry + 0.022, label,
                fontsize=15.0, weight="bold", color=NAVY, ha="left", va="center", zorder=5,
            )
            ax_bg.text(
                text_left_x, ry + 0.007, detail,
                fontsize=14.6, weight="normal", color=DARK_SLATE,
                ha="left", va="top", linespacing=1.10, zorder=5,
            )
        else:
            ax_bg.text(
                text_left_x, ry + 0.013, label,
                fontsize=15.0, weight="bold", color=NAVY, ha="left", va="center", zorder=5,
            )
            ax_bg.text(
                text_left_x, ry - 0.013, detail,
                fontsize=14.6, weight="normal", color=DARK_SLATE,
                ha="left", va="center", zorder=5,
            )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    create_figure()
