#!/usr/bin/env python3
r"""
generate_secular_planetary_evolution.py

Generates the two-panel illustration ("Secular Evolution of a Planetary Orbit")
for Section 4.1 ("From Lagrange-Laplace Theory to Modern Celestial Mechanics")
of Article 3: "Order and Chaos: The Road to Modern Dynamics III".

Mathematical Model - Two-Mode Linear Lagrange-Laplace Secular Approximation:
  Complex eccentricity variable: z(u) = e(u) * exp(i * varpi(u))
  Linear superposition of two secular modes:
    z(u) = C_1 * exp(i * g_1 * u) + C_2 * exp(i * g_2 * u)
  Illustrative parameters:
    C_1 = 0.12,  C_2 = 0.06,  g_1 = 1.0,  g_2 = 1.3,  a = 1.0
  Beat period:
    T_beat = 2 * pi / |g_2 - g_1| = 2 * pi / 0.3 ~ 20.9440
  Bounded eccentricity bounds:
    e_min = |C_1 - C_2| = 0.06,   e_max = C_1 + C_2 = 0.18

  Three sampled secular epochs (common colors across Panels A and B):
    - Epoch 1: u = 0             -> e = 0.18, varpi =    0 deg
    - Epoch 2: u = T_beat / 2    -> e = 0.06, varpi = -120 deg (240 deg)
    - Epoch 3: u = T_beat        -> e = 0.18, varpi = +120 deg

  Polar ellipse equation around common focus (Sun at origin):
    r(psi, u) = a * (1 - e(u)^2) / (1 + e(u) * cos(psi - varpi(u)))

Visual Specifications:
  - ~2:1 scientific two-panel layout: 16.0 x 8.2 in @ 160 DPI -> 2560 x 1312 px
  - Reuses the exact typography, font-size hierarchy, and card system of
    pendulum_separatrix_to_homoclinic_chaos.png, kam_poincare_sections.png,
    and unforced_vs_forced_pendulum.png.

Output:
  images/secular_planetary_evolution.png
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
OUTPUT_PNG = PROJECT_DIR / "images" / "secular_planetary_evolution.png"

# Secular two-mode model parameters
C1 = 0.12
C2 = 0.06
G1 = 1.0
G2 = 1.3
A_SEMI = 1.0
T_BEAT = 2.0 * np.pi / abs(G2 - G1)


def secular_state(u):
    """Evaluate complex eccentricity z(u), eccentricity e(u), and perihelion longitude varpi(u)."""
    u_arr = np.asarray(u, dtype=float)
    z = C1 * np.exp(1j * G1 * u_arr) + C2 * np.exp(1j * G2 * u_arr)
    e = np.abs(z)
    varpi = np.angle(z)
    return z, e, varpi


def orbit_xy(e_val: float, varpi_val: float, n_pts: int = 500):
    """Compute Cartesian coordinates (x, y) of a Keplerian ellipse with focus at (0, 0)."""
    psi = np.linspace(0.0, 2.0 * np.pi, n_pts)
    r = A_SEMI * (1.0 - e_val ** 2) / (1.0 + e_val * np.cos(psi - varpi_val))
    return r * np.cos(psi), r * np.sin(psi)


def verify_model():
    """Verify analytical bounds and three epoch states."""
    u_dense = np.linspace(0.0, 2.0 * T_BEAT, 10000)
    _, e_dense, _ = secular_state(u_dense)
    assert abs(float(e_dense.min()) - 0.06) < 1e-5, f"Expected e_min=0.06, got {e_dense.min()}"
    assert abs(float(e_dense.max()) - 0.18) < 1e-5, f"Expected e_max=0.18, got {e_dense.max()}"

    epochs = [
        ("u=0", 0.0, 0.18, 0.0),
        ("u=T_beat/2", 0.5 * T_BEAT, 0.06, -2.0 * np.pi / 3.0),
        ("u=T_beat", T_BEAT, 0.18, 2.0 * np.pi / 3.0),
    ]
    for name, u_val, e_exp, w_exp in epochs:
        _, e_val, w_val = secular_state(u_val)
        assert abs(float(e_val) - e_exp) < 1e-12, f"{name}: expected e={e_exp}, got {e_val}"
        ang_diff = np.angle(np.exp(1j * (float(w_val) - w_exp)))
        assert abs(ang_diff) < 1e-12, f"{name}: expected varpi={w_exp}, got {w_val}"
    print(f"  [Verified] Two-mode secular model: e in [0.06, 0.18], T_beat = {T_BEAT:.4f}")


def create_figure(output_path=None):
    verify_model()
    if output_path is None:
        output_path = OUTPUT_PNG
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 2:1 two-panel layout matching Article 3 visual design & typography
    fig_w, fig_h = 16.0, 8.2
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=160, facecolor="#ffffff")

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

    TEAL_LIGHT = "#f0fdfa"
    TEAL_BORDER = "#5eead4"
    TEAL_ACCENT = "#0d9488"

    PURPLE_ACCENT = "#7c3aed"

    # Common epoch styles across Panel A and Panel B
    EPOCH_SPECS = [
        {
            "label": r"$u = 0$",
            "short": r"$u = 0$" + "\n(e = 0.18)",
            "u": 0.0,
            "color": BLUE_ACCENT,
            "lw": 2.6,
            "z": 6,
        },
        {
            "label": r"$u = T_{\mathrm{beat}}/2$",
            "short": r"$u = T_{\mathrm{beat}}/2$" + " (e = 0.06)",
            "u": 0.5 * T_BEAT,
            "color": TEAL_ACCENT,
            "lw": 2.6,
            "z": 7,
        },
        {
            "label": r"$u = T_{\mathrm{beat}}$",
            "short": r"$u = T_{\mathrm{beat}}$" + " (e = 0.18)",
            "u": T_BEAT,
            "color": PURPLE_ACCENT,
            "lw": 2.6,
            "z": 8,
        },
    ]

    halo = [pe.withStroke(linewidth=3.6, foreground="#ffffff", alpha=0.96)]

    # -------------------------------------------------------------------------
    # Global Title & Subtitle (matching Article 3 typography hierarchy)
    # -------------------------------------------------------------------------
    fig.text(
        0.50,
        0.958,
        "Secular Evolution of a Planetary Orbit",
        fontsize=24.0,
        weight="bold",
        color=NAVY,
        ha="center",
        va="center",
    )
    fig.text(
        0.50,
        0.913,
        "Precessing osculating ellipses and bounded eccentricity oscillations in a linear two-mode model",
        fontsize=17.2,
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
    # Two Equal-Width Parallel Panel Cards (A and B)
    # -------------------------------------------------------------------------
    y_card = 0.026
    h_card = 0.850
    x1, w1 = 0.016, 0.472
    x2, w2 = 0.512, 0.472
    hbar_h = 0.106
    badge_y = y_card + h_card - hbar_h / 2.0

    panels_spec = [
        (
            x1, w1, "A", "Secular evolution of an orbit",
            "Three epochs around the Sun (constant a = 1)",
            BLUE_ACCENT, HEADER_BLUE, HEADER_BORDER,
        ),
        (
            x2, w2, "B", "Bounded eccentricity variations",
            "Illustrative two-mode Lagrange–Laplace model",
            TEAL_ACCENT, TEAL_LIGHT, TEAL_BORDER,
        ),
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
            text_offset_x, badge_y + 0.020, title,
            fontsize=18.2, weight="bold", color=NAVY, va="center", zorder=4,
        )
        ax_bg.text(
            text_offset_x, badge_y - 0.022, subtitle,
            fontsize=14.2, weight="bold", color=MUTED_SLATE, va="center", zorder=4,
        )

    # -------------------------------------------------------------------------
    # Compact Bottom Summary Cards (larger readable font, more plot height)
    # -------------------------------------------------------------------------
    y_box = 0.036
    h_box = 0.098

    bottom_specs = [
        (
            x1, w1, HEADER_BORDER,
            "Constant semimajor axis a = 1 around the Sun;\n"
            "eccentricity e(u) and perihelion ϖ(u) evolve slowly.",
        ),
        (
            x2, w2, TEAL_BORDER,
            "Beating between frequencies g₁ = 1 and g₂ = 1.3\n"
            "keeps the eccentricity bounded between 0.06 and 0.18.",
        ),
    ]

    for px, pw, bdr_col, desc in bottom_specs:
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px + 0.012, y_box), pw - 0.024, h_box,
            boxstyle="round,pad=0.0,rounding_size=0.014",
            facecolor=BG_BOX, edgecolor=bdr_col, linewidth=1.4, zorder=3,
        ))
        ax_bg.text(
            px + pw / 2.0, y_box + h_box / 2.0,
            desc,
            fontsize=14.4, weight="bold", color=DARK_SLATE,
            ha="center", va="center", linespacing=1.18, zorder=4,
        )

    # -------------------------------------------------------------------------
    # Plot Geometry (expanded vertically with larger axes & interior fonts)
    # -------------------------------------------------------------------------
    y_plot = 0.204
    h_plot = 0.548

    # Panel A Axes (equal-aspect orbital plane with clean margins for larger callouts)
    w_plot_A = w1 - 0.052
    axA = fig.add_axes([x1 + (w1 - w_plot_A) / 2.0 + 0.014, y_plot, w_plot_A, h_plot], zorder=5)
    axA.set_facecolor("#ffffff")
    axA.set_xlim(-1.58, 1.88)
    axA.set_ylim(-1.46, 1.46)
    axA.set_aspect("equal", adjustable="box")
    axA.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0, 1.5])
    axA.set_xticklabels(["-1.0", "-0.5", "0", "0.5", "1.0", "1.5"], fontsize=13.8, weight="bold", color=SLATE)
    axA.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    axA.set_yticklabels(["-1.0", "-0.5", "0", "0.5", "1.0"], fontsize=13.8, weight="bold", color=SLATE)
    axA.tick_params(axis="both", which="major", length=4, width=1.2, colors=SLATE, pad=3)
    axA.set_xlabel(r"$x\ /\ a$", fontsize=16.4, weight="bold", color=NAVY, labelpad=2)
    axA.set_ylabel(r"$y\ /\ a$", fontsize=16.4, weight="bold", color=NAVY, labelpad=2)
    for g in (-1.0, -0.5, 0.5, 1.0, 1.5):
        axA.axvline(g, color="#f1f5f9", lw=0.9, zorder=1)
    for g in (-1.0, -0.5, 0.5, 1.0):
        axA.axhline(g, color="#f1f5f9", lw=0.9, zorder=1)
    # Fixed reference plane axes through the Sun (focus)
    axA.axhline(0.0, color="#e2e8f0", lw=1.1, ls="-", zorder=2)
    axA.axvline(0.0, color="#e2e8f0", lw=1.1, ls="-", zorder=2)
    for sp in axA.spines.values():
        sp.set_edgecolor(BORDER_CARD)
        sp.set_linewidth(1.2)

    # Subtle circular reference circle r = a = 1 centered at focus
    th_circ = np.linspace(0.0, 2.0 * np.pi, 300)
    axA.plot(np.cos(th_circ), np.sin(th_circ), color="#cbd5e1", lw=1.2, ls=":", zorder=2)

    # Fixed reference direction psi = 0 cleanly outside all ellipses
    axA.text(
        1.78, 0.06, r"$\psi = 0$",
        fontsize=15.4, weight="bold", color=MUTED_SLATE,
        ha="right", va="bottom", path_effects=halo, zorder=8,
    )

    # Draw the three osculating ellipses and their light perihelion directions
    peri_pts = []
    for spec in EPOCH_SPECS:
        _, e_val, w_val = secular_state(spec["u"])
        ex, ey = orbit_xy(float(e_val), float(w_val))
        axA.plot(
            ex, ey,
            color=spec["color"], lw=spec["lw"], alpha=0.95, zorder=spec["z"],
        )

        # Perihelion point and light radial line from the focus
        r_peri = A_SEMI * (1.0 - float(e_val))
        px_p = r_peri * np.cos(float(w_val))
        py_p = r_peri * np.sin(float(w_val))
        peri_pts.append((px_p, py_p, spec))
        axA.plot(
            [0.0, px_p], [0.0, py_p],
            color=spec["color"], lw=1.8, ls="--", alpha=0.78, zorder=spec["z"] - 1,
        )
        axA.scatter(
            [px_p], [py_p],
            s=72, facecolor=spec["color"], edgecolor="#ffffff", linewidth=1.6, zorder=10,
        )

    # Non-overlapping callout placement in clean exterior corners / right margin
    callout_layout = [
        # u = 0: compact two-line right-margin box cleanly outside all ellipses
        (peri_pts[0], (1.82, -0.34), "right", "top"),
        # u = T_beat/2: clean bottom-left corner pointing to perihelion (-0.47, -0.81)
        (peri_pts[1], (-1.52, -1.39), "left", "bottom"),
        # u = T_beat: clean top-left corner pointing to perihelion (-0.41, +0.71)
        (peri_pts[2], (-1.52, 1.39), "left", "top"),
    ]
    for (px_p, py_p, spec), txt_xy, ha_v, va_v in callout_layout:
        axA.annotate(
            spec["short"],
            xy=(px_p, py_p),
            xytext=txt_xy,
            fontsize=15.4, weight="bold", color=spec["color"],
            ha=ha_v, va=va_v, multialignment="center", linespacing=1.12, path_effects=halo,
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#ffffff", edgecolor=spec["color"], linewidth=1.15, alpha=0.95),
            arrowprops=dict(arrowstyle="-|>", mutation_scale=12.5, color=spec["color"], lw=1.6, shrinkA=2, shrinkB=4),
            zorder=11,
        )

    # Sun at the common focus (0, 0)
    axA.scatter([0.0], [0.0], s=340, facecolor="#fef3c7", edgecolor="none", alpha=0.90, zorder=9)
    axA.scatter([0.0], [0.0], s=145, facecolor="#f59e0b", edgecolor="#b45309", linewidth=1.6, zorder=11)
    axA.text(
        0.04, 0.13, "Sun\n(focus)",
        fontsize=13.4, weight="bold", color="#92400e",
        ha="left", va="bottom", linespacing=1.05, path_effects=halo, zorder=12,
    )

    # Top-right note identifying perihelion rays/dots cleanly outside all ellipses
    axA.text(
        1.80, 1.37,
        "Dots & dashed rays:\nperihelion direction ϖ",
        fontsize=12.6, weight="bold", color=MUTED_SLATE,
        ha="right", va="top", linespacing=1.14, path_effects=halo,
        bbox=dict(boxstyle="round,pad=0.22", facecolor="#f8fafc", edgecolor=BORDER_CARD, linewidth=1.0, alpha=0.95),
        zorder=11,
    )

    # -------------------------------------------------------------------------
    # Panel B Axes (Eccentricity e(u) vs normalized secular time u)
    # -------------------------------------------------------------------------
    w_plot_B = w2 - 0.092
    axB = fig.add_axes([x2 + 0.072, y_plot, w_plot_B, h_plot], zorder=5)
    axB.set_facecolor("#ffffff")

    u_max = 1.38 * T_BEAT  # ~28.90 (displays full beat cycle 0 -> T_beat plus continuation)
    axB.set_xlim(-1.5, u_max)
    axB.set_ylim(0.024, 0.232)

    axB.set_xticks([0.0, 5.0, 10.0, 15.0, 20.0, 25.0])
    axB.set_xticklabels(["0", "5", "10", "15", "20", "25"], fontsize=13.8, weight="bold", color=SLATE)
    axB.set_yticks([0.06, 0.10, 0.14, 0.18])
    axB.set_yticklabels(["0.06", "0.10", "0.14", "0.18"], fontsize=13.8, weight="bold", color=SLATE)
    axB.tick_params(axis="both", which="major", length=4, width=1.2, colors=SLATE, pad=3)
    axB.set_xlabel(r"Normalized secular time $u$", fontsize=16.0, weight="bold", color=NAVY, labelpad=3)
    axB.set_ylabel(r"Eccentricity $e(u)$", fontsize=16.2, weight="bold", color=NAVY, labelpad=4)

    for gx in (0.0, 5.0, 10.0, 15.0, 20.0, 25.0):
        axB.axvline(gx, color="#f1f5f9", lw=0.9, zorder=1)
    for gy in (0.06, 0.10, 0.14, 0.18):
        axB.axhline(gy, color="#f1f5f9", lw=0.9, zorder=1)
    for sp in axB.spines.values():
        sp.set_edgecolor(BORDER_CARD)
        sp.set_linewidth(1.2)

    # Analytical oscillation bounds e_min = 0.06 and e_max = 0.18 in clear regions
    axB.axhline(0.18, color="#94a3b8", lw=1.3, ls="--", zorder=2)
    axB.axhline(0.06, color="#94a3b8", lw=1.3, ls="--", zorder=2)
    axB.text(
        10.472, 0.184, r"$e_{\max} = C_1 + C_2 = 0.18$",
        fontsize=15.8, weight="bold", color=MUTED_SLATE,
        ha="center", va="bottom", path_effects=halo, zorder=5,
    )
    axB.text(
        28.3, 0.054, r"$e_{\min} = C_1 - C_2 = 0.06$",
        fontsize=15.8, weight="bold", color=MUTED_SLATE,
        ha="right", va="top", path_effects=halo, zorder=5,
    )

    # Full e(u) curve
    u_grid = np.linspace(0.0, u_max, 600)
    _, e_grid, _ = secular_state(u_grid)
    axB.plot(u_grid, e_grid, color=DARK_SLATE, lw=2.9, zorder=4)

    # Mark the three epochs from Panel A with matching colors
    epoch_callouts = [
        (EPOCH_SPECS[0], (1.5, 0.204), "left", "bottom", (0.0, 0.18)),
        (EPOCH_SPECS[1], (10.472, 0.083), "center", "bottom", (10.472, 0.06)),
        (EPOCH_SPECS[2], (20.944, 0.204), "center", "bottom", (20.944, 0.18)),
    ]
    for spec, txt_xy, ha_v, va_v, pt_xy in epoch_callouts:
        ux = spec["u"]
        _, ev, _ = secular_state(ux)
        axB.axvline(ux, color=spec["color"], lw=1.6, ls=":", alpha=0.68, zorder=3)
        axB.scatter(
            [ux], [float(ev)],
            s=120, facecolor=spec["color"], edgecolor="#ffffff", linewidth=2.0, zorder=8,
        )
        axB.annotate(
            spec["label"],
            xy=pt_xy,
            xytext=txt_xy,
            fontsize=16.5, weight="bold", color=spec["color"],
            ha=ha_v, va=va_v, path_effects=halo,
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#ffffff", edgecolor=spec["color"], linewidth=1.15, alpha=0.95),
            arrowprops=dict(arrowstyle="-|>", mutation_scale=12.5, color=spec["color"], lw=1.6),
            zorder=9,
        )

    # Beat period double arrow between u = 0 and u = T_beat
    y_beat = 0.123
    axB.annotate(
        "",
        xy=(T_BEAT, y_beat),
        xytext=(0.0, y_beat),
        arrowprops=dict(arrowstyle="<|-|>", mutation_scale=13.5, color=SLATE, lw=1.8),
        zorder=6,
    )
    axB.text(
        0.5 * T_BEAT, y_beat + 0.0055,
        r"Beat period  $T_{\mathrm{beat}} = \dfrac{2\pi}{|g_2 - g_1|} \approx 20.94$",
        fontsize=15.6, weight="bold", color=NAVY,
        ha="center", va="bottom", path_effects=halo,
        bbox=dict(boxstyle="round,pad=0.22", facecolor="#ffffff", edgecolor=BORDER_CARD, linewidth=1.05, alpha=0.96),
        zorder=7,
    )

    fig.savefig(output_path, dpi=160, facecolor="#ffffff")
    plt.close(fig)
    print(f"  [OK] Saved {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    create_figure()
