#!/usr/bin/env python3
r"""
generate_horseshoe_symbolic_dynamics.py

Generates Illustration 2 ("From Horseshoe Trajectories to Symbolic Sequences")
for Article 3 ("Order and Chaos: The Road to Modern Dynamics III"):

  - Panel A (Trajectories in phase space):
      Reference square R = [0, 1]^2 with two blue horizontal returning strips:
        Strip 0: 0 <= y <= 1/3
        Strip 1: 2/3 <= y <= 1
      Middle strip (1/3 < y < 2/3) remains pale gray (escapes R in one step).
      Plots exact numerical orbits of the piecewise-affine horseshoe map F:
        - Period-two orbit: z_0 = (9/10, 3/10) <-> z_1 = (3/10, 9/10)
        - Fixed point:      z_* = (3/4, 3/4)  ->  z_*
      with discrete jump arrows labeled F.

  - Panel B (Symbolic coding and the shift):
      1) Compact visit timeline table (n = 0..5) for the period-two orbit.
      2) Visual shift map alignment showing the bi-infinite binary sequence
         ... 1 0 1 | 0 1 0 1 ... shifting left by one position to
         ... 0 1 0 | 1 0 1 0 ... across the present-iteration separator |.
      3) Supplementary fixed-point itinerary (... 1 1 1 | 1 1 1 ...) for z_*.

Visual Specifications:
  - 16:9 widescreen: 16.0 x 9.0 in @ 150 DPI -> exact 2400 x 1350 px
  - Cohesive editorial typography matching Figure 1 and Animation 1
  - Two distinct shades of the same blue family for Strips 0 and 1
"""

from pathlib import Path
import numpy as np
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
DEFAULT_OUT = PROJECT_DIR / "images" / "horseshoe_symbolic_dynamics.png"


def horseshoe_affine_step(z):
    """Apply the piecewise-affine horseshoe map F(x, y) on the two returning strips."""
    x, y = z
    if 0.0 <= y <= 1.0 / 3.0:
        return (x / 3.0, 3.0 * y)
    if 2.0 / 3.0 <= y <= 1.0:
        return (1.0 - x / 3.0, 3.0 * (1.0 - y))
    raise ValueError(f"Point {z} is outside the returning horizontal strips.")


def verify_sample_orbits():
    """Verify period-two orbit z_0 <-> z_1 and fixed point z_* under F."""
    z0 = (0.9, 0.3)
    z1 = (0.3, 0.9)
    fz0 = horseshoe_affine_step(z0)
    fz1 = horseshoe_affine_step(z1)
    assert np.allclose(fz0, z1, atol=1e-12), f"Expected F(z0)=z1, got {fz0}"
    assert np.allclose(fz1, z0, atol=1e-12), f"Expected F(z1)=z0, got {fz1}"

    z_star = (0.75, 0.75)
    fz_star = horseshoe_affine_step(z_star)
    assert np.allclose(fz_star, z_star, atol=1e-12), f"Expected F(z*)=z*, got {fz_star}"
    print("  [Verified] Period-two orbit (0.9, 0.3) <-> (0.3, 0.9) and fixed point (0.75, 0.75) under F.")


def create_figure(output_path=None):
    verify_sample_orbits()
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig_w, fig_h = 16.0, 9.0
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=150, facecolor="#ffffff")

    # Palette — strictly two contrasting shades of the same blue family for Strips 0 and 1
    NAVY = "#0f172a"
    DARK_SLATE = "#1e293b"
    SLATE = "#334155"
    MUTED_SLATE = "#475569"
    BORDER_CARD = "#cbd5e1"
    BG_CARD = "#f8fafc"
    BG_BOX = "#ffffff"

    HEADER_BLUE = "#eff6ff"
    HEADER_BORDER = "#93c5fd"
    BLUE_ACCENT = "#2563eb"
    BLUE_DARK = "#1e3a8a"

    # Strip 0 (light sky blue) vs Strip 1 (richer cobalt blue) — same blue hue family
    S0_FILL = "#dbeafe"
    S0_EDGE = "#60a5fa"
    S0_TEXT = "#1d4ed8"

    S1_FILL = "#93c5fd"
    S1_EDGE = "#1d4ed8"
    S1_TEXT = "#1e3a8a"

    halo = [pe.withStroke(linewidth=3.8, foreground="#ffffff", alpha=0.96)]

    # -------------------------------------------------------------------------
    # Global Title & Subtitle (regular italic subtitle matching Figure 1 & Animation 1)
    # -------------------------------------------------------------------------
    fig.text(
        0.50,
        0.962,
        "From Horseshoe Trajectories to Symbolic Sequences",
        fontsize=24.0,
        weight="bold",
        color=NAVY,
        ha="center",
        va="center",
    )
    fig.text(
        0.50,
        0.920,
        "Encoding successive visits to two regions of phase space",
        fontsize=17.5,
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
    # Two Equal-Width Panel Cards (A and B)
    # -------------------------------------------------------------------------
    y_card = 0.026
    h_card = 0.860
    x1, w1 = 0.018, 0.470
    x2, w2 = 0.512, 0.470
    hbar_h = 0.100
    badge_y = y_card + h_card - hbar_h / 2.0

    panels_spec = [
        (x1, w1, "A", "Trajectories in phase space",
         "Two horizontal regions labeled 0 and 1, with sample orbits",
         BLUE_ACCENT, HEADER_BLUE, HEADER_BORDER),
        (x2, w2, "B", "Symbolic coding and the shift",
         "Successive visits form a shifting binary sequence",
         BLUE_DARK, HEADER_BLUE, HEADER_BORDER),
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

        badge_x = px + 0.025
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

        text_offset_x = badge_x + 0.023
        ax_bg.text(
            text_offset_x, badge_y + 0.019, title,
            fontsize=17.6, weight="bold", color=NAVY, va="center", zorder=4,
        )
        ax_bg.text(
            text_offset_x, badge_y - 0.021, subtitle,
            fontsize=14.4, weight="bold", color=MUTED_SLATE, va="center", zorder=4,
        )

    # Conceptual bridge arrow between Panel A and Panel B headers
    ax_bg.add_patch(patches.FancyArrowPatch(
        (x1 + w1 + 0.003, badge_y),
        (x2 - 0.003, badge_y),
        arrowstyle="-|>,head_length=7.0,head_width=4.5",
        color="#64748b", linewidth=2.2, zorder=5,
    ))

    # =========================================================================
    # PANEL A: TRAJECTORIES IN PHASE SPACE (R = [0, 1]^2)
    # =========================================================================
    y_plot = 0.194
    h_plot = 0.562
    w_plot = h_plot * (fig_h / fig_w)  # exact geometric square (~0.316)

    ax1 = fig.add_axes([x1 + (w1 - w_plot) / 2.0 + 0.010, y_plot, w_plot, h_plot], zorder=5)
    ax1.set_facecolor("#ffffff")
    ax1.set_xlim(-0.08, 1.08)
    ax1.set_ylim(-0.06, 1.12)
    ax1.set_aspect("equal", adjustable="box")

    # Subtle coordinate grid
    for g in np.linspace(0.0, 1.0, 10):
        ax1.axvline(g, color="#f1f5f9", lw=0.9, zorder=1)
        ax1.axhline(g, color="#f1f5f9", lw=0.9, zorder=1)
    for g in (1.0 / 3.0, 2.0 / 3.0):
        ax1.axvline(g, color="#e2e8f0", lw=1.0, ls=":", zorder=2)
        ax1.axhline(g, color="#e2e8f0", lw=1.0, ls=":", zorder=2)

    # Middle third background (points escape R on next step)
    ax1.add_patch(patches.Rectangle(
        (0.0, 0.0), 1.0, 1.0, facecolor="#f8fafc", edgecolor="none", zorder=2,
    ))
    ax1.text(
        0.035, 0.50,
        "Middle third\nescapes R in\none iteration",
        fontsize=13.8, weight="bold", color="#64748b",
        ha="left", va="center", linespacing=1.22, path_effects=halo, zorder=4,
    )

    # Strip 0 (0 <= y <= 1/3) and Strip 1 (2/3 <= y <= 1) in two contrasting blue shades
    ax1.add_patch(patches.Rectangle(
        (0.0, 0.0), 1.0, 1.0 / 3.0,
        facecolor=S0_FILL, edgecolor=S0_EDGE, linewidth=1.6, alpha=0.88, zorder=3,
    ))
    ax1.add_patch(patches.Rectangle(
        (0.0, 2.0 / 3.0), 1.0, 1.0 / 3.0,
        facecolor=S1_FILL, edgecolor=S1_EDGE, linewidth=1.6, alpha=0.82, zorder=3,
    ))

    # Crisp strip badges 0 and 1 cleanly indented inside x = 0 border
    for y_badge, y_rng, sym, fc, ec, tc, rng_txt in (
        (0.218, 0.082, "0", "#ffffff", S0_EDGE, S0_TEXT, "0 ≤ y ≤ 1/3"),
        (0.882, 0.748, "1", "#ffffff", S1_EDGE, S1_TEXT, "2/3 ≤ y ≤ 1"),
    ):
        ax1.text(
            0.135, y_badge, sym,
            fontsize=17.5, weight="bold", color=tc,
            ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.24", facecolor=fc, edgecolor=ec, linewidth=1.8),
            zorder=10,
        )
        ax1.text(
            0.032, y_rng, rng_txt,
            fontsize=13.2, weight="bold", color=tc,
            ha="left", va="center",
            path_effects=[pe.withStroke(linewidth=3.0, foreground="#ffffff", alpha=0.85)],
            zorder=9,
        )

    # Fixed black dashed square border R = [0, 1]^2
    ax1.add_patch(patches.Rectangle(
        (0.0, 0.0), 1.0, 1.0,
        facecolor="none", edgecolor=DARK_SLATE, linewidth=2.5, linestyle="--", zorder=12,
    ))
    ax1.text(
        -0.01, 1.032, r"$\mathbf{Original\;region}\;\boldsymbol{R}$",
        fontsize=14.4, weight="bold", color=DARK_SLATE,
        ha="left", va="bottom", path_effects=halo, zorder=15,
    )
    ax1.text(
        1.01, 1.032, "Strips 0 & 1",
        fontsize=14.4, weight="bold", color=S1_TEXT,
        ha="right", va="bottom", path_effects=halo, zorder=15,
    )

    ax1.set_xticks([0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0])
    ax1.set_xticklabels(["0", "1/3", "2/3", "1"], fontsize=14.2, fontweight="bold", color=SLATE)
    ax1.set_yticks([0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0])
    ax1.set_yticklabels(["0", "1/3", "2/3", "1"], fontsize=14.2, fontweight="bold", color=SLATE)
    ax1.tick_params(axis="both", which="major", length=4, width=1.2, colors=SLATE, pad=4)
    ax1.set_xlabel(r"$\boldsymbol{x}$", fontsize=15.5, fontweight="bold", color=NAVY, labelpad=0)
    ax1.set_ylabel(r"$\boldsymbol{y}$", fontsize=15.5, fontweight="bold", color=NAVY, labelpad=4)

    # Plot exact Period-Two Orbit z_0 = (0.9, 0.3) <-> z_1 = (0.3, 0.9)
    z0 = np.array([0.9, 0.3])
    z1 = np.array([0.3, 0.9])
    for pt in (z0, z1):
        ax1.plot(pt[0], pt[1], "o", color=NAVY, markersize=10.5,
                 markeredgecolor="#ffffff", markeredgewidth=1.6, zorder=15)

    ax1.text(
        0.875, 0.175, r"$\boldsymbol{z}_0 = (0.9,\;0.3)$",
        fontsize=14.0, weight="bold", color=NAVY, ha="right", va="center",
        bbox=dict(boxstyle="round,pad=0.20", facecolor="#ffffff", edgecolor=S0_EDGE, linewidth=1.2),
        zorder=16,
    )
    ax1.text(
        0.365, 0.922, r"$\boldsymbol{z}_1 = (0.3,\;0.9)$",
        fontsize=14.0, weight="bold", color=NAVY, ha="left", va="center",
        bbox=dict(boxstyle="round,pad=0.20", facecolor="#ffffff", edgecolor=S1_EDGE, linewidth=1.2),
        zorder=16,
    )

    # Sleek dashed discrete jump arrows z_0 -> z_1 -> z_0 labeled F (using FancyArrowPatch for exact arrowhead sizing)
    ax1.add_patch(patches.FancyArrowPatch(
        (z0[0] - 0.025, z0[1] + 0.012),
        (z1[0] - 0.008, z1[1] - 0.028),
        connectionstyle="arc3,rad=-0.26",
        arrowstyle="-|>", mutation_scale=17,
        color=NAVY, linewidth=2.1, linestyle="--", zorder=14,
    ))
    ax1.add_patch(patches.FancyArrowPatch(
        (z1[0] + 0.028, z1[1] - 0.010),
        (z0[0] + 0.006, z0[1] + 0.030),
        connectionstyle="arc3,rad=-0.26",
        arrowstyle="-|>", mutation_scale=17,
        color=NAVY, linewidth=2.1, linestyle="--", zorder=14,
    ))
    ax1.text(
        0.415, 0.675, r"$\boldsymbol{F}$",
        fontsize=14.6, weight="bold", color=NAVY, ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.16", facecolor="#ffffff", edgecolor=BORDER_CARD, linewidth=1.0),
        zorder=16,
    )
    ax1.text(
        0.740, 0.560, r"$\boldsymbol{F}$",
        fontsize=14.6, weight="bold", color=NAVY, ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.16", facecolor="#ffffff", edgecolor=BORDER_CARD, linewidth=1.0),
        zorder=16,
    )

    # Optional Fixed Point z_* = (0.75, 0.75) in Strip 1
    z_star = np.array([0.75, 0.75])
    ax1.plot(z_star[0], z_star[1], "D", color=S1_TEXT, markersize=8.5,
             markeredgecolor="#ffffff", markeredgewidth=1.4, zorder=15)
    ax1.add_patch(patches.FancyArrowPatch(
        (z_star[0] + 0.022, z_star[1] - 0.015),
        (z_star[0] + 0.018, z_star[1] + 0.024),
        connectionstyle="arc3,rad=2.2",
        arrowstyle="-|>", mutation_scale=13,
        color=S1_TEXT, linewidth=1.7, linestyle="--", zorder=14,
    ))
    ax1.text(
        0.765, 0.840, r"$\boldsymbol{z}_* = (0.75,\;0.75)$",
        fontsize=13.6, weight="bold", color=S1_TEXT, ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.18", facecolor="#ffffff", edgecolor=S1_EDGE, linewidth=1.1),
        zorder=16,
    )

    # Panel A bottom summary card
    y_box_A, h_box_A = 0.042, 0.098
    ax_bg.add_patch(patches.FancyBboxPatch(
        (x1 + 0.016, y_box_A), w1 - 0.032, h_box_A,
        boxstyle="round,pad=0.0,rounding_size=0.014",
        facecolor=BG_BOX, edgecolor=HEADER_BORDER, linewidth=1.3, zorder=3,
    ))
    ax_bg.text(
        x1 + w1 / 2.0, y_box_A + h_box_A / 2.0,
        r"Period-two orbit under $\boldsymbol{F}$: $\boldsymbol{z}_0 \rightarrow \boldsymbol{z}_1 \rightarrow \boldsymbol{z}_0$ (alternates 0 and 1)"
        + "\n"
        + r"Fixed point under $\boldsymbol{F}$: $\boldsymbol{z}_* \rightarrow \boldsymbol{z}_*$ (stays permanently in strip 1)",
        fontsize=14.0, weight="bold", color=DARK_SLATE,
        ha="center", va="center", linespacing=1.36, zorder=4,
    )

    # =========================================================================
    # PANEL B: SYMBOLIC CODING AND THE SHIFT
    # =========================================================================
    bx_left = x2 + 0.018
    bw_inner = w2 - 0.036
    bx_mid = x2 + w2 / 2.0

    # --- 1) Compact Timeline Table: Example: period-two orbit (n = 0..5) ---
    tbl_y, tbl_h = 0.625, 0.132
    ax_bg.add_patch(patches.FancyBboxPatch(
        (bx_left, tbl_y), bw_inner, tbl_h,
        boxstyle="round,pad=0.0,rounding_size=0.014",
        facecolor=BG_BOX, edgecolor=BORDER_CARD, linewidth=1.3, zorder=2,
    ))
    ax_bg.text(
        bx_left + 0.014, tbl_y + tbl_h - 0.022,
        "Example: period-two orbit (discrete trajectory itinerary)",
        fontsize=14.6, weight="bold", color=NAVY, ha="left", va="center", zorder=4,
    )

    cell_w = 0.058
    cell_gap = 0.010
    total_tbl_w = 6 * cell_w + 5 * cell_gap
    tx_start = bx_mid - total_tbl_w / 2.0
    row_n_y = tbl_y + 0.072
    row_s_y = tbl_y + 0.028

    for k in range(6):
        cx = tx_start + k * (cell_w + cell_gap) + cell_w / 2.0
        sym_val = k % 2
        fc = S0_FILL if sym_val == 0 else S1_FILL
        ec = S0_EDGE if sym_val == 0 else S1_EDGE
        tc = S0_TEXT if sym_val == 0 else S1_TEXT

        ax_bg.text(
            cx, row_n_y, rf"$\boldsymbol{{n}} = \mathbf{{{k}}}$",
            fontsize=13.8, weight="bold", color=MUTED_SLATE,
            ha="center", va="center", zorder=4,
        )
        ax_bg.add_patch(patches.FancyBboxPatch(
            (cx - 0.022, row_s_y - 0.018), 0.044, 0.036,
            boxstyle="round,pad=0.0,rounding_size=0.008",
            facecolor=fc, edgecolor=ec, linewidth=1.5, zorder=3,
        ))
        ax_bg.text(
            cx, row_s_y, str(sym_val),
            fontsize=16.0, weight="bold", color=tc,
            ha="center", va="center", zorder=4,
        )

    # --- 2) Bi-Infinite Sequences & Visual Shift Map Block ---
    sh_y, sh_h = 0.228, 0.374
    ax_bg.add_patch(patches.FancyBboxPatch(
        (bx_left, sh_y), bw_inner, sh_h,
        boxstyle="round,pad=0.0,rounding_size=0.014",
        facecolor=BG_BOX, edgecolor=HEADER_BORDER, linewidth=1.4, zorder=2,
    ))
    ax_bg.text(
        bx_left + 0.014, sh_y + sh_h - 0.024,
        "Advancing F by one iteration shifts the bi-infinite sequence",
        fontsize=14.6, weight="bold", color=NAVY, ha="left", va="center", zorder=4,
    )

    # Past | Present | Present & future headers on the same line with clean spacing
    sep_x = bx_mid - 0.026
    tile_w = 0.038
    tile_h = 0.048
    tile_step = 0.044
    sep_half_gap = 0.021  # generous gap around separator |

    # Compute x-centers of the 7 visible symbol slots: 3 left of separator (past), 4 right (present & future)
    slot_xs = [
        sep_x - sep_half_gap - tile_w / 2.0 - 2 * tile_step,
        sep_x - sep_half_gap - tile_w / 2.0 - 1 * tile_step,
        sep_x - sep_half_gap - tile_w / 2.0,
        sep_x + sep_half_gap + tile_w / 2.0,
        sep_x + sep_half_gap + tile_w / 2.0 + 1 * tile_step,
        sep_x + sep_half_gap + tile_w / 2.0 + 2 * tile_step,
        sep_x + sep_half_gap + tile_w / 2.0 + 3 * tile_step,
    ]

    # All three header labels aligned on the same horizontal line
    y_lbl_pf = sh_y + 0.298
    ax_bg.text(
        bx_left + 0.016, y_lbl_pf, "Past visits (n < 0)",
        fontsize=12.8, weight="bold", color=MUTED_SLATE,
        ha="left", va="center", zorder=4,
    )
    ax_bg.text(
        bx_left + bw_inner - 0.012, y_lbl_pf, "Present & future visits (n ≥ 0)",
        fontsize=12.8, weight="bold", color=BLUE_DARK,
        ha="right", va="center", zorder=4,
    )

    y_row1 = sh_y + 0.238
    y_row2 = sh_y + 0.070

    # Present-iteration separator running vertically across both sequences
    ax_bg.plot(
        [sep_x, sep_x], [y_row2 - 0.040, y_row1 + 0.042],
        color=NAVY, lw=2.8, zorder=5,
    )
    ax_bg.text(
        sep_x, y_lbl_pf, "Present",
        fontsize=12.8, weight="bold", color=NAVY,
        ha="center", va="center", zorder=5,
    )

    seq_row1 = [1, 0, 1, 0, 1, 0, 1]  # ... 1 0 1 | 0 1 0 1 ...
    seq_row2 = [0, 1, 0, 1, 0, 1, 0]  # ... 0 1 0 | 1 0 1 0 ...

    def draw_sequence_row(y_row, seq_vals, is_shifted=False):
        for idx_s, (sx, val) in enumerate(zip(slot_xs, seq_vals)):
            fc = S0_FILL if val == 0 else S1_FILL
            ec = S0_EDGE if val == 0 else S1_EDGE
            tc = S0_TEXT if val == 0 else S1_TEXT
            is_s0_slot = (idx_s == 3)
            ax_bg.add_patch(patches.FancyBboxPatch(
                (sx - tile_w / 2.0, y_row - tile_h / 2.0), tile_w, tile_h,
                boxstyle="round,pad=0.0,rounding_size=0.008",
                facecolor=fc,
                edgecolor=NAVY if is_s0_slot else ec,
                linewidth=2.4 if is_s0_slot else 1.5,
                zorder=4,
            ))
            ax_bg.text(
                sx, y_row, str(val),
                fontsize=17.0, weight="bold", color=tc,
                ha="center", va="center", zorder=5,
            )
        # Ellipses with clean spacing outside symbol row
        ax_bg.text(
            slot_xs[0] - tile_w / 2.0 - 0.018, y_row, "…",
            fontsize=18.0, weight="bold", color=MUTED_SLATE, ha="center", va="center", zorder=4,
        )
        ax_bg.text(
            slot_xs[-1] + tile_w / 2.0 + 0.018, y_row, "…",
            fontsize=18.0, weight="bold", color=MUTED_SLATE, ha="center", va="center", zorder=4,
        )

    draw_sequence_row(y_row1, seq_row1)
    draw_sequence_row(y_row2, seq_row2, is_shifted=True)

    # Row index tags cleanly beneath each s_0 box
    ax_bg.text(
        slot_xs[3], y_row1 - 0.036, r"$\boldsymbol{s}_0$",
        fontsize=14.2, weight="bold", color=NAVY, ha="center", va="center", zorder=6,
    )
    ax_bg.text(
        slot_xs[4], y_row1 - 0.036, r"$\boldsymbol{s}_1$",
        fontsize=14.2, weight="bold", color=MUTED_SLATE, ha="center", va="center", zorder=6,
    )
    ax_bg.text(
        slot_xs[3], y_row2 - 0.038, r"$\mathbf{new}\;\boldsymbol{s}_0$",
        fontsize=13.8, weight="bold", color=NAVY, ha="center", va="center", zorder=6,
    )

    # Subtle diagonal guide arrows showing symbols moving 1 slot left across the separator
    for k_src in range(1, 7):
        k_dst = k_src - 1
        ax_bg.add_patch(patches.FancyArrowPatch(
            (slot_xs[k_src], y_row1 - tile_h / 2.0 - 0.004),
            (slot_xs[k_dst], y_row2 + tile_h / 2.0 + 0.004),
            arrowstyle="-|>,head_length=5.0,head_width=3.2",
            color="#94a3b8", linewidth=1.3, linestyle=":", alpha=0.80, zorder=3,
        ))

    # Prominent horizontal arrow labeled "Shift map" protruding cleanly beyond the box on the left
    y_sh_arr = 0.5 * (y_row1 + y_row2)
    ax_bg.add_patch(patches.FancyArrowPatch(
        (slot_xs[6] + 0.015, y_sh_arr),
        (slot_xs[0] - 0.015, y_sh_arr),
        arrowstyle="-|>,head_length=11.0,head_width=7.0",
        color=BLUE_ACCENT, linewidth=3.2, zorder=7,
    ))
    ax_bg.text(
        0.5 * (slot_xs[0] + slot_xs[6]), y_sh_arr,
        "  Shift map (one iteration forward)  ",
        fontsize=14.2, weight="bold", color=BLUE_DARK,
        ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.22", facecolor=HEADER_BLUE, edgecolor=HEADER_BORDER, linewidth=1.3),
        zorder=8,
    )

    # --- 3) Supplementary Fixed-Point Example Card ---
    fp_y, fp_h = 0.042, 0.162
    ax_bg.add_patch(patches.FancyBboxPatch(
        (bx_left, fp_y), bw_inner, fp_h,
        boxstyle="round,pad=0.0,rounding_size=0.014",
        facecolor=BG_BOX, edgecolor=BORDER_CARD, linewidth=1.3, zorder=2,
    ))
    ax_bg.text(
        bx_left + 0.014, fp_y + fp_h - 0.026,
        r"Fixed point $\boldsymbol{z}_* = (0.75,\;0.75)$ in strip 1",
        fontsize=14.4, weight="bold", color=S1_TEXT, ha="left", va="center", zorder=4,
    )

    y_fp_seq = fp_y + 0.068
    fp_tile_w = 0.036
    fp_tile_h = 0.044
    fp_step = 0.043
    fp_sep_x = bx_mid
    fp_slot_xs = [
        fp_sep_x - 0.020 - fp_tile_w / 2.0 - 2 * fp_step,
        fp_sep_x - 0.020 - fp_tile_w / 2.0 - 1 * fp_step,
        fp_sep_x - 0.020 - fp_tile_w / 2.0,
        fp_sep_x + 0.020 + fp_tile_w / 2.0,
        fp_sep_x + 0.020 + fp_tile_w / 2.0 + 1 * fp_step,
        fp_sep_x + 0.020 + fp_tile_w / 2.0 + 2 * fp_step,
    ]
    ax_bg.plot(
        [fp_sep_x, fp_sep_x], [y_fp_seq - 0.028, y_fp_seq + 0.028],
        color=NAVY, lw=2.5, zorder=5,
    )
    for sx in fp_slot_xs:
        ax_bg.add_patch(patches.FancyBboxPatch(
            (sx - fp_tile_w / 2.0, y_fp_seq - fp_tile_h / 2.0), fp_tile_w, fp_tile_h,
            boxstyle="round,pad=0.0,rounding_size=0.008",
            facecolor=S1_FILL, edgecolor=S1_EDGE, linewidth=1.4, zorder=4,
        ))
        ax_bg.text(
            sx, y_fp_seq, "1",
            fontsize=16.0, weight="bold", color=S1_TEXT, ha="center", va="center", zorder=5,
        )
    ax_bg.text(fp_slot_xs[0] - fp_tile_w / 2.0 - 0.018, y_fp_seq, "…",
               fontsize=17.5, weight="bold", color=MUTED_SLATE, ha="center", va="center", zorder=4)
    ax_bg.text(fp_slot_xs[-1] + fp_tile_w / 2.0 + 0.018, y_fp_seq, "…",
               fontsize=17.5, weight="bold", color=MUTED_SLATE, ha="center", va="center", zorder=4)

    ax_bg.text(
        bx_mid, fp_y + 0.020,
        "Constant sequence of 1s — invariant under the shift map",
        fontsize=13.8, weight="bold", color=MUTED_SLATE, ha="center", va="center", zorder=4,
    )

    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    create_figure()
