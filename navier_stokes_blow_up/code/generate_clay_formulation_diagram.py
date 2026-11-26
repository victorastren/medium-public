#!/usr/bin/env python3
"""
Generate a clean, compact mathematical flowchart of the Clay Millennium Problem formulation
for the section: "What the Millennium Problem Actually Asked"

Layout:
- Root: Navier-Stokes Millennium Problem
- Left branch: Global Smoothness (f = 0 (unforced)) -> Statements A & B (whole space / periodic)
- Right branch: Finite-Time Breakdown (f in C^inf (including f = 0)) -> Statements C & D (whole space / periodic)
- Level 3:
  - Left (dashed implications): November 2026 — Proposed Result (Alpöge & Buckmaster):
    Would disprove A and B; would also prove C and D.
  - Right (solid connection): September 2026 — Proposed Result (OpenAI):
    Would prove C and D.

Clean, streamlined flowchart design optimized for Medium 680px column width.
"""

from pathlib import Path
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent


def draw_dashed_ortho_arrow(ax, points, color, lw=2.0, head_width=0.30, head_length=0.42, zorder=3):
    """Draw a crisp orthogonal dashed polyline ending in a solid triangular arrowhead."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_prev, y_prev = points[-2]
    x_tip, y_tip = points[-1]
    dx, dy = x_tip - x_prev, y_tip - y_prev
    seg_len = (dx ** 2 + dy ** 2) ** 0.5
    ux, uy = dx / seg_len, dy / seg_len
    if seg_len > 0.16:
        xs[-1] = x_tip - 0.14 * ux
        ys[-1] = y_tip - 0.14 * uy

    ax.plot(
        xs, ys,
        color=color, lw=lw, linestyle=(0, (4.2, 2.6)),
        solid_capstyle="butt", solid_joinstyle="round", zorder=zorder,
    )
    ax.annotate(
        "",
        xy=(x_tip, y_tip),
        xytext=(x_tip - 0.22 * ux, y_tip - 0.22 * uy),
        arrowprops=dict(
            arrowstyle=f"-|>,head_width={head_width},head_length={head_length}",
            color=color, lw=lw, shrinkA=0, shrinkB=0,
        ),
        zorder=zorder + 1,
    )


def create_clay_formulation_diagram(out_path=None):
    if out_path is None:
        out_path = PROJECT_DIR / "images" / "clay_millennium_problem_formulation.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(8.8, 8.0), dpi=240, facecolor="#070b12")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("#070b12")
    ax.set_xlim(0, 8.8)
    ax.set_ylim(0, 8.0)
    ax.axis("off")

    # Color Palette (retained from original diagram)
    CANVAS_BG   = "#070b12"
    CARD_BG     = "#0d1526"
    TEXT_TITLE  = "#f8fafc"
    LINE_COL    = "#475569"

    # Left Branch (Global Smoothness / Regularity)
    BLUE_ACCENT = "#38bdf8"
    BLUE_BG     = "#082f49"
    BLUE_BORDER = "#0284c7"

    # Right Branch (Breakdown / Blow-Up)
    ROSE_ACCENT = "#fb7185"
    ROSE_BG     = "#4c0519"
    ROSE_BORDER = "#e11d48"

    # Proposed Result Highlight
    GOLD_ACCENT = "#fbbf24"
    GREEN_ACC   = "#4ade80"

    # =========================================================================
    # 1. ROOT CARD: NAVIER-STOKES MILLENNIUM PROBLEM
    # =========================================================================
    root_x, root_y, root_w, root_h = 1.40, 6.90, 6.00, 0.85
    root_box = FancyBboxPatch(
        (root_x, root_y), root_w, root_h,
        boxstyle="round,pad=0.06,rounding_size=0.14",
        facecolor="#111c35", edgecolor="#334155", lw=1.6, zorder=4,
    )
    ax.add_patch(root_box)
    ax.text(
        4.40, root_y + root_h / 2,
        "NAVIER–STOKES MILLENNIUM PROBLEM",
        fontsize=14.5, fontweight="bold", color=TEXT_TITLE, ha="center", va="center", zorder=5,
    )

    # Stem & Bifurcation
    stem_bottom = 6.32
    ax.plot([4.40, 4.40], [root_y - 0.06, stem_bottom], color=LINE_COL, lw=2.0, zorder=2)

    left_x_c  = 2.25
    right_x_c = 6.55
    ax.plot([left_x_c, right_x_c], [stem_bottom, stem_bottom], color=LINE_COL, lw=2.0, zorder=2)

    # Downward arrows to Level 1
    ax.annotate(
        "", xy=(left_x_c, 5.82), xytext=(left_x_c, stem_bottom),
        arrowprops=dict(arrowstyle="-|>,head_width=0.30,head_length=0.42",
                        color=BLUE_ACCENT, lw=2.0, shrinkA=0, shrinkB=0),
        zorder=3,
    )
    ax.annotate(
        "", xy=(right_x_c, 5.82), xytext=(right_x_c, stem_bottom),
        arrowprops=dict(arrowstyle="-|>,head_width=0.30,head_length=0.42",
                        color=ROSE_ACCENT, lw=2.0, shrinkA=0, shrinkB=0),
        zorder=3,
    )

    # =========================================================================
    # 2. LEVEL 1: BRANCH HEADERS
    # =========================================================================
    card_w = 3.60
    left_x = left_x_c - card_w / 2
    right_x = right_x_c - card_w / 2
    h_y = 4.66
    h_h = 1.10

    # Left: Global Smoothness
    h_left = FancyBboxPatch(
        (left_x, h_y), card_w, h_h,
        boxstyle="round,pad=0.06,rounding_size=0.12",
        facecolor=BLUE_BG, edgecolor=BLUE_BORDER, lw=1.5, zorder=4,
    )
    ax.add_patch(h_left)
    ax.text(
        left_x_c, h_y + h_h - 0.32, "Global Smoothness",
        fontsize=14.0, fontweight="bold", color="#e0f2fe", ha="center", va="center", zorder=5,
    )
    ax.text(
        left_x_c, h_y + 0.32, r"$\mathbf{f} = \mathbf{0}$  (unforced)",
        fontsize=12.0, fontweight="bold", color=BLUE_ACCENT, ha="center", va="center", zorder=5,
    )

    # Right: Finite-Time Breakdown
    h_right = FancyBboxPatch(
        (right_x, h_y), card_w, h_h,
        boxstyle="round,pad=0.06,rounding_size=0.12",
        facecolor=ROSE_BG, edgecolor=ROSE_BORDER, lw=1.5, zorder=4,
    )
    ax.add_patch(h_right)
    ax.text(
        right_x_c, h_y + h_h - 0.32, "Finite-Time Breakdown",
        fontsize=14.0, fontweight="bold", color="#ffe4e6", ha="center", va="center", zorder=5,
    )
    ax.text(
        right_x_c, h_y + 0.32, r"$\mathbf{f} \in C^\infty$  (including $\mathbf{f} = \mathbf{0}$)",
        fontsize=11.6, fontweight="bold", color=ROSE_ACCENT, ha="center", va="center", zorder=5,
    )

    # Connectors to Level 2
    s_y = 2.70
    s_h = 1.38
    ax.annotate(
        "", xy=(left_x_c, s_y + s_h + 0.06), xytext=(left_x_c, h_y - 0.06),
        arrowprops=dict(arrowstyle="-|>,head_width=0.28,head_length=0.40",
                        color=BLUE_ACCENT, lw=1.8, shrinkA=0, shrinkB=0),
        zorder=3,
    )
    ax.annotate(
        "", xy=(right_x_c, s_y + s_h + 0.06), xytext=(right_x_c, h_y - 0.06),
        arrowprops=dict(arrowstyle="-|>,head_width=0.28,head_length=0.40",
                        color=ROSE_ACCENT, lw=1.8, shrinkA=0, shrinkB=0),
        zorder=3,
    )

    # =========================================================================
    # 3. LEVEL 2: STATEMENTS A & B vs C & D
    # =========================================================================
    s_left = FancyBboxPatch(
        (left_x, s_y), card_w, s_h,
        boxstyle="round,pad=0.06,rounding_size=0.12",
        facecolor=CARD_BG, edgecolor="#1e3a5f", lw=1.4, zorder=4,
    )
    ax.add_patch(s_left)

    s_right = FancyBboxPatch(
        (right_x, s_y), card_w, s_h,
        boxstyle="round,pad=0.06,rounding_size=0.12",
        facecolor=CARD_BG, edgecolor="#64172b", lw=1.4, zorder=4,
    )
    ax.add_patch(s_right)

    ax.text(
        left_x_c, s_y + s_h - 0.29, "Statements A & B",
        fontsize=13.5, fontweight="bold", color=BLUE_ACCENT, ha="center", va="center", zorder=5,
    )
    ax.plot(
        [left_x + 0.35, left_x + card_w - 0.35],
        [s_y + s_h - 0.51, s_y + s_h - 0.51],
        color="#1e293b", lw=1.0, zorder=5,
    )

    ax.text(
        right_x_c, s_y + s_h - 0.29, "Statements C & D",
        fontsize=13.5, fontweight="bold", color=ROSE_ACCENT, ha="center", va="center", zorder=5,
    )
    ax.plot(
        [right_x + 0.35, right_x + card_w - 0.35],
        [s_y + s_h - 0.51, s_y + s_h - 0.51],
        color="#3f1422", lw=1.0, zorder=5,
    )

    bullet_x_left = 1.31
    ax.text(bullet_x_left, s_y + 0.53, r"• A: whole space ($\mathbb{R}^3$)",
            fontsize=12.0, color="#f1f5f9", va="center", zorder=5)
    ax.text(bullet_x_left, s_y + 0.23, r"• B: periodic ($\mathbb{T}^3$)",
            fontsize=12.0, color="#f1f5f9", va="center", zorder=5)

    bullet_x_right = 5.61
    ax.text(bullet_x_right, s_y + 0.53, r"• C: whole space ($\mathbb{R}^3$)",
            fontsize=12.0, color="#f1f5f9", va="center", zorder=5)
    ax.text(bullet_x_right, s_y + 0.23, r"• D: periodic ($\mathbb{T}^3$)",
            fontsize=12.0, color="#f1f5f9", va="center", zorder=5)

    # =========================================================================
    # 4. LEVEL 3: NOVEMBER 2026 (LEFT) & SEPTEMBER 2026 (RIGHT) PROPOSED RESULTS
    # =========================================================================
    res_y = 0.28
    res_h = 1.76
    badge_w = 3.24

    # --- Arrows connecting Level 2 & Level 3 ---
    # Solid gold arrow: Statements C & D -> September 2026 box (x = right_x_c = 6.55)
    ax.annotate(
        "",
        xy=(right_x_c, res_y + res_h + 0.06),
        xytext=(right_x_c, s_y - 0.06),
        arrowprops=dict(arrowstyle="-|>,head_width=0.30,head_length=0.40",
                        color=GOLD_ACCENT, lw=2.0, shrinkA=0, shrinkB=0),
        zorder=3,
    )

    # Dashed rose arrow: November 2026 box -> Statements A & B (would disprove A & B)
    draw_dashed_ortho_arrow(
        ax,
        [(left_x_c, res_y + res_h + 0.06), (left_x_c, s_y - 0.06)],
        color=ROSE_ACCENT,
        lw=2.0,
        head_width=0.30,
        head_length=0.42,
        zorder=3,
    )

    # Dashed gold arrow: November 2026 box -> Statements C & D (would also prove C & D)
    nov_right_edge = left_x + card_w + 0.06
    mid_gap_x = 0.5 * (nov_right_edge + (right_x - 0.06))
    mid_channel_y = 0.5 * ((res_y + res_h + 0.06) + (s_y - 0.06))
    target_cd_x = 5.65  # Well left of the solid September arrow at 6.55
    draw_dashed_ortho_arrow(
        ax,
        [
            (nov_right_edge, res_y + res_h * 0.50),
            (mid_gap_x, res_y + res_h * 0.50),
            (mid_gap_x, mid_channel_y),
            (target_cd_x, mid_channel_y),
            (target_cd_x, s_y - 0.06),
        ],
        color=GOLD_ACCENT,
        lw=2.0,
        head_width=0.30,
        head_length=0.42,
        zorder=3,
    )

    # --- Left Gold Card: November 2026 — Proposed Result ---
    nov_box = FancyBboxPatch(
        (left_x, res_y), card_w, res_h,
        boxstyle="round,pad=0.06,rounding_size=0.12",
        facecolor="#1c1503", edgecolor=GOLD_ACCENT, lw=1.6, zorder=4,
    )
    ax.add_patch(nov_box)

    nov_badge = FancyBboxPatch(
        (left_x_c - badge_w / 2, res_y + res_h - 0.40), badge_w, 0.32,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor="#854d0e", edgecolor="none", zorder=5,
    )
    ax.add_patch(nov_badge)
    ax.text(
        left_x_c, res_y + res_h - 0.24,
        "November 2026 — Proposed Result",
        fontsize=11.4, fontweight="bold", color="#fef08a", ha="center", va="center", zorder=6,
    )

    ax.text(
        left_x_c, res_y + 1.07, "Alpöge & Buckmaster",
        fontsize=11.8, fontweight="bold", color="#fef08a", ha="center", va="center", zorder=5,
    )
    ax.text(
        left_x_c, res_y + 0.80, "Unforced finite-time blow-up",
        fontsize=11.4, color="#fde68a", ha="center", va="center", zorder=5,
    )
    ax.text(
        left_x_c, res_y + 0.45, "Would disprove A and B",
        fontsize=11.5, fontweight="bold", color=ROSE_ACCENT, ha="center", va="center", zorder=5,
    )
    ax.text(
        left_x_c, res_y + 0.19, "Would also prove C and D",
        fontsize=11.5, fontweight="bold", color=GREEN_ACC, ha="center", va="center", zorder=5,
    )

    # --- Right Gold Card: September 2026 — Proposed Result ---
    sep_box = FancyBboxPatch(
        (right_x, res_y), card_w, res_h,
        boxstyle="round,pad=0.06,rounding_size=0.12",
        facecolor="#1c1503", edgecolor=GOLD_ACCENT, lw=1.6, zorder=4,
    )
    ax.add_patch(sep_box)

    sep_badge = FancyBboxPatch(
        (right_x_c - badge_w / 2, res_y + res_h - 0.40), badge_w, 0.32,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor="#854d0e", edgecolor="none", zorder=5,
    )
    ax.add_patch(sep_badge)
    ax.text(
        right_x_c, res_y + res_h - 0.24,
        "September 2026 — Proposed Result",
        fontsize=11.4, fontweight="bold", color="#fef08a", ha="center", va="center", zorder=6,
    )

    ax.text(
        right_x_c, res_y + 1.02, "OpenAI",
        fontsize=11.8, fontweight="bold", color="#fef08a", ha="center", va="center", zorder=5,
    )
    ax.text(
        right_x_c, res_y + 0.72, "Forced finite-time blow-up",
        fontsize=11.4, color="#fde68a", ha="center", va="center", zorder=5,
    )
    ax.text(
        right_x_c, res_y + 0.30, "Would prove C and D",
        fontsize=11.6, fontweight="bold", color=GREEN_ACC, ha="center", va="center", zorder=5,
    )

    plt.savefig(out_path, dpi=240, facecolor=CANVAS_BG, edgecolor="none", bbox_inches="tight")
    plt.close()
    print(f"[OK] Generated {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")
    return out_path


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else None
    create_clay_formulation_diagram(out_file)
