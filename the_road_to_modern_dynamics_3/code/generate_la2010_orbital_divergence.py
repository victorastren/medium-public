#!/usr/bin/env python3
r"""
generate_la2010_orbital_divergence.py

Generates the two-panel figure ("Divergence of Long-Term Orbital Solutions")
for Section 4.3 ("Chaos and the Long-Term Stability of the Solar System")
of Article 3: "Order and Chaos: The Road to Modern Dynamics III".

Data Source:
  Published IMCCE 1-kyr orbital eccentricity datasets from Laskar et al. (2011),
  "La2010: A new orbital solution for the long-term motion of the Earth",
  Astronomy & Astrophysics, 532, A89:
    - data/La2010a_ecc3L.dat
    - data/La2010b_ecc3L.dat
    - data/La2010c_ecc3L.dat
    - data/La2010d_ecc3L.dat

  Each file stores (t_kyr, e) at 1-kyr sampling relative to J2000.
  Age before J2000 in millions of years is:
    T_Ma = -t_kyr / 1000.0
  Plotted directly at full published resolution (no smoothing):
    - Panel A: 45 <= T_Ma <= 50  (closely aligned orbital solutions)
    - Panel B: 60 <= T_Ma <= 65  (substantial phase and amplitude divergence)
  Identical y-axis range 0 <= e <= 0.07 and shared legend for La2010a-d.

Visual Specifications:
  - ~2:1 scientific two-panel layout: 16.0 x 8.2 in @ 160 DPI -> 2560 x 1312 px
  - Reuses the exact typography hierarchy and card styling of
    pendulum_separatrix_to_homoclinic_chaos.png, kam_poincare_sections.png,
    and unforced_vs_forced_pendulum.png.

Output:
  images/la2010_orbital_divergence.png
"""

from pathlib import Path
import urllib.request
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D

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
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_PNG = PROJECT_DIR / "images" / "la2010_orbital_divergence.png"
IMCCE_BASE = "https://ssp.imcce.fr/insola/earth/online/earth/La2010"

SOLUTIONS = [
    ("La2010a", "La2010a_ecc3L.dat", "#0f172a", "-", 1.25, 6),
    ("La2010b", "La2010b_ecc3L.dat", "#2563eb", "-", 1.18, 4),
    ("La2010c", "La2010c_ecc3L.dat", "#059669", "-", 1.18, 5),
    ("La2010d", "La2010d_ecc3L.dat", "#dc2626", "-", 1.18, 3),
]

WINDOW_A = (45.0, 50.0)
WINDOW_B = (60.0, 65.0)


def load_la2010_datasets():
    """Load all four IMCCE La2010 1-kyr eccentricity datasets and verify sampling/windows."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    datasets = {}

    for label, fname, _, _, _, _ in SOLUTIONS:
        fpath = DATA_DIR / fname
        if not fpath.exists():
            url = f"{IMCCE_BASE}/{fname}"
            print(f"  [Fetch] Downloading {url} -> {fpath}")
            urllib.request.urlretrieve(url, fpath)

        arr = np.loadtxt(fpath, dtype=float)
        assert arr.ndim == 2 and arr.shape[1] == 2, f"Unexpected shape {arr.shape} in {fname}"
        t_kyr = arr[:, 0]
        ecc = arr[:, 1]
        t_ma = -t_kyr / 1000.0

        # Ensure strictly ascending T_Ma for plotting and verify 1-kyr step
        order = np.argsort(t_ma)
        t_ma = t_ma[order]
        ecc = ecc[order]
        dt_kyr = np.diff(t_ma * 1000.0)
        assert np.allclose(dt_kyr, 1.0, atol=1e-9), f"{fname} does not have uniform 1-kyr sampling"

        datasets[label] = (t_ma, ecc)

    # Quantitative verification of agreement vs divergence
    ta, ea = datasets["La2010a"]
    m_a = (ta >= WINDOW_A[0]) & (ta <= WINDOW_A[1])
    m_b = (ta >= WINDOW_B[0]) & (ta <= WINDOW_B[1])
    assert m_a.sum() == 5001 and m_b.sum() == 5001, "Expected 5001 points per 5-Myr window"

    rms_a = []
    rms_b = []
    for label, _, _, _, _, _ in SOLUTIONS[1:]:
        _, e_other = datasets[label]
        rms_a.append(float(np.sqrt(np.mean((e_other[m_a] - ea[m_a]) ** 2))))
        rms_b.append(float(np.sqrt(np.mean((e_other[m_b] - ea[m_b]) ** 2))))
    assert max(rms_b) > 2.5 * max(rms_a), "Expected clear divergence growth from 45-50 Ma to 60-65 Ma"
    print(f"  [Verified] Loaded La2010a-d (1-kyr sampling): RMS diff 45-50 Ma = {[round(x, 4) for x in rms_a]}, "
          f"60-65 Ma = {[round(x, 4) for x in rms_b]}")
    return datasets


def create_figure(output_path=None):
    datasets = load_la2010_datasets()
    if output_path is None:
        output_path = OUTPUT_PNG
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 2:1 two-panel scientific layout matching Article 3 visual system
    fig_w, fig_h = 16.0, 8.2
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=160, facecolor="#ffffff")

    NAVY = "#0f172a"
    DARK_SLATE = "#1e293b"
    SLATE = "#334155"
    MUTED_SLATE = "#475569"
    BORDER_CARD = "#cbd5e1"
    BG_CARD = "#f8fafc"

    HEADER_BLUE = "#eff6ff"
    HEADER_BORDER = "#93c5fd"
    BLUE_ACCENT = "#2563eb"

    TEAL_LIGHT = "#f0fdfa"
    TEAL_BORDER = "#5eead4"
    TEAL_ACCENT = "#0d9488"

    # -------------------------------------------------------------------------
    # Global Title & Subtitle (matching Article 3 typography hierarchy)
    # -------------------------------------------------------------------------
    fig.text(
        0.50,
        0.958,
        "Divergence of Long-Term Orbital Solutions",
        fontsize=24.0,
        weight="bold",
        color=NAVY,
        ha="center",
        va="center",
    )
    fig.text(
        0.50,
        0.913,
        "Earth's orbital eccentricity in the four La2010 numerical solutions (Laskar et al., 2011)",
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
    y_card = 0.118
    h_card = 0.758
    x1, w1 = 0.016, 0.472
    x2, w2 = 0.512, 0.472
    hbar_h = 0.106
    badge_y = y_card + h_card - hbar_h / 2.0

    panels_spec = [
        (
            x1, w1, "A", "Agreement (45–50 million years ago)",
            "All four solutions remain closely aligned",
            BLUE_ACCENT, HEADER_BLUE, HEADER_BORDER, WINDOW_A,
        ),
        (
            x2, w2, "B", "Divergence (60–65 million years ago)",
            "Substantial phase and amplitude differences emerge",
            TEAL_ACCENT, TEAL_LIGHT, TEAL_BORDER, WINDOW_B,
        ),
    ]

    for px, pw, letter, title, subtitle, acc_color, bg_tint, bdr_color, win in panels_spec:
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
            fontsize=17.4, weight="bold", color=NAVY, va="center", zorder=4,
        )
        ax_bg.text(
            text_offset_x, badge_y - 0.022, subtitle,
            fontsize=14.2, weight="bold", color=MUTED_SLATE, va="center", zorder=4,
        )

        # Plot axes inside panel card (identical 5-Myr width and 0 <= e <= 0.07 height)
        ax_left = px + 0.068
        ax_w = pw - 0.088
        ax_bottom = y_card + 0.090
        ax_h = h_card - hbar_h - 0.118
        ax = fig.add_axes([ax_left, ax_bottom, ax_w, ax_h], zorder=5)
        ax.set_facecolor("#ffffff")

        x0, x1_w = win
        ax.set_xlim(x0, x1_w)
        ax.set_ylim(0.0, 0.07)

        xticks = np.arange(x0, x1_w + 0.5, 1.0)
        ax.set_xticks(xticks)
        ax.set_xticklabels([f"{int(v)}" for v in xticks], fontsize=13.8, weight="bold", color=SLATE)
        yticks = [0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07]
        ax.set_yticks(yticks)
        ax.set_yticklabels(["0.00", "0.01", "0.02", "0.03", "0.04", "0.05", "0.06", "0.07"],
                           fontsize=13.4, weight="bold", color=SLATE)
        ax.tick_params(axis="both", which="major", length=4, width=1.2, colors=SLATE, pad=3)

        ax.set_xlabel("Time before present (millions of years)", fontsize=15.4, weight="bold", color=NAVY, labelpad=5)
        ax.set_ylabel(r"Orbital eccentricity $e$", fontsize=15.8, weight="bold", color=NAVY, labelpad=5)

        for gx in xticks[1:-1]:
            ax.axvline(gx, color="#f1f5f9", lw=0.9, zorder=1)
        for gy in yticks[1:-1]:
            ax.axhline(gy, color="#f1f5f9", lw=0.9, zorder=1)
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER_CARD)
            sp.set_linewidth(1.2)

        for label, _, color, ls, lw, z in SOLUTIONS:
            t_ma, ecc = datasets[label]
            mask = (t_ma >= x0) & (t_ma <= x1_w)
            ax.plot(
                t_ma[mask],
                ecc[mask],
                color=color,
                linestyle=ls,
                linewidth=lw,
                alpha=0.90,
                zorder=z,
                rasterized=False,
            )

    # -------------------------------------------------------------------------
    # Shared Legend Strip Centered Beneath Both Panels
    # -------------------------------------------------------------------------
    legend_handles = [
        Line2D([0], [0], color=color, linestyle=ls, linewidth=2.6, label=label)
        for label, _, color, ls, _, _ in SOLUTIONS
    ]
    leg = fig.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.50, 0.022),
        ncol=4,
        frameon=True,
        facecolor="#ffffff",
        edgecolor=BORDER_CARD,
        framealpha=1.0,
        handlelength=2.4,
        handletextpad=0.7,
        columnspacing=2.2,
        borderpad=0.55,
        prop={"size": 14.4, "weight": "bold"},
    )
    leg.get_frame().set_linewidth(1.3)
    for txt, (_, _, color, _, _, _) in zip(leg.get_texts(), SOLUTIONS):
        txt.set_color(DARK_SLATE)

    fig.savefig(output_path, dpi=160, facecolor="#ffffff")
    plt.close(fig)
    print(f"  [OK] Saved {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    create_figure()
