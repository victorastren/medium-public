#!/usr/bin/env python3
r"""
generate_kam_poincare_sections.py

Generates the three-panel KAM Poincaré-section figure for Section 2.2
("The KAM Theorem: Persistence and Resonance") of Article 3:
"Order and Chaos: The Road to Modern Dynamics III"

Mathematical Model — Normalized Undamped Driven Pendulum (consistent with §1.3):
  theta'' + sin(theta) = A cos(Omega * t),   Omega = 0.80,   T = 2*pi/Omega ~ 7.85398
  - Panel A: A = 0     (Integrable system: invariant curves & exact separatrix)
  - Panel B: A = 0.05  (Weak forcing: deformed KAM curves, resonance islands, narrow chaos)
  - Panel C: A = 0.20  (Stronger forcing: extensive chaotic sea + surviving curves & islands)

All three panels use the exact same 205-point initial-condition grid integrated over
450 forcing periods with SciPy DOP853 (rtol=1e-10, atol=1e-12) and variational FTLEs.

Output:
  images/kam_poincare_sections.png (3168 x 1568 px, matching Figure 1's 19.8 x 9.8 scale)
"""

import sys
import time
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
    "axes.linewidth": 1.3,
})

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_PNG = PROJECT_DIR / "images" / "kam_poincare_sections.png"
CACHE_PATH = Path("/tmp/kam_poincare_cache_v1.npz")

OMEGA = 0.80
T_PERIOD = 2.0 * np.pi / OMEGA
N_PERIODS = 450
AMPLITUDES = (0.0, 0.05, 0.20)
FTLE_CHAOS_THRESHOLD = 0.006


def wrap_pi(th):
    return (np.asarray(th) + np.pi) % (2.0 * np.pi) - np.pi


def build_identical_ic_grid():
    """Reproducible 205-point phase-space grid used identically for A = 0, 0.05, 0.20."""
    pts = []
    for th in np.linspace(-3.04, 3.04, 39):
        pts.append((float(th), 0.0))
    for v in np.linspace(-2.55, 2.55, 43):
        if abs(v) > 0.04:
            pts.append((0.0, float(v)))
    for th_s in (-2.40, -1.57, -0.78, 0.78, 1.57, 2.40):
        for v in np.linspace(-2.48, 2.48, 18):
            if abs(v) > 0.08:
                pts.append((float(th_s), float(v)))
    for v in np.linspace(-2.40, 2.40, 16):
        if abs(v) > 0.08:
            pts.append((float(np.pi), float(v)))

    arr = np.array(pts, dtype=float)
    uniq = []
    for p in arr:
        if not uniq or np.min(np.hypot(np.array(uniq)[:, 0] - p[0], np.array(uniq)[:, 1] - p[1])) > 0.05:
            uniq.append(p)
    return np.array(uniq, dtype=float)


def integrate_one_ic(args):
    A_val, th0, v0, n_periods, rtol, atol = args

    def rhs_var(t, y):
        th, v, dth, dv = y
        c = np.cos(th)
        return [v, -np.sin(th) + A_val * np.cos(OMEGA * t), dv, -c * dth]

    th_out = np.empty(n_periods + 1, dtype=float)
    v_out = np.empty(n_periods + 1, dtype=float)
    th_out[0] = th0
    v_out[0] = v0

    chunk = 10
    y = np.array([th0, v0, 1.0, 0.0], dtype=float)
    log_sum = 0.0
    n_done = 0
    while n_done < n_periods:
        step_n = min(chunk, n_periods - n_done)
        t0 = n_done * T_PERIOD
        t_eval = np.arange(n_done + 1, n_done + step_n + 1) * T_PERIOD
        t1 = float(t_eval[-1])
        sol = solve_ivp(rhs_var, (t0, t1), y, t_eval=t_eval, method="DOP853", rtol=rtol, atol=atol)
        if not sol.success:
            raise RuntimeError(sol.message)
        th_out[n_done + 1 : n_done + 1 + step_n] = sol.y[0]
        v_out[n_done + 1 : n_done + 1 + step_n] = sol.y[1]
        y = sol.y[:, -1].copy()
        dn = np.hypot(y[2], y[3])
        if dn > 0.0:
            log_sum += np.log(dn)
            y[2] /= dn
            y[3] /= dn
        n_done += step_n

    ftle = log_sum / (n_periods * T_PERIOD)
    return th_out, v_out, float(ftle)


def load_or_compute_data(force_recompute=False):
    if CACHE_PATH.exists() and not force_recompute:
        print(f"Loaded precomputed KAM Poincaré dataset from {CACHE_PATH}")
        return dict(np.load(CACHE_PATH, allow_pickle=False))

    t0 = time.time()
    ics = build_identical_ic_grid()
    print(f"Computing {len(ics)} identical ICs x {N_PERIODS} periods for A = {AMPLITUDES}...")
    num_cpus = max(1, min(14, multiprocessing.cpu_count() - 2))
    data = {"ics": ics, "omega": OMEGA, "n_periods": N_PERIODS}
    with multiprocessing.Pool(processes=num_cpus) as pool:
        for A_val in AMPLITUDES:
            jobs = [(A_val, ic[0], ic[1], N_PERIODS, 1e-10, 1e-12) for ic in ics]
            results = pool.map(integrate_one_ic, jobs, chunksize=4)
            key = f"A{int(round(A_val * 100)):02d}"
            data[f"th_{key}"] = np.array([r[0] for r in results])
            data[f"v_{key}"] = np.array([r[1] for r in results])
            data[f"ftle_{key}"] = np.array([r[2] for r in results])

    # Validation: unforced energy conservation
    th0_all, v0_all = data["th_A00"], data["v_A00"]
    E0 = 0.5 * v0_all[:, 0:1] ** 2 + 1.0 - np.cos(th0_all[:, 0:1])
    E_all = 0.5 * v0_all ** 2 + 1.0 - np.cos(th0_all)
    assert np.max(np.abs(E_all - E0)) < 1e-7, "A=0 energy conservation failed!"

    np.savez(CACHE_PATH, **data)
    print(f"Saved validated dataset to {CACHE_PATH} in {time.time() - t0:.1f}s")
    return data


def classify_orbits(key: str, th_w: np.ndarray, v_a: np.ndarray, ftle: np.ndarray):
    """
    Classify each trajectory strictly from its numerical FTLE & phase-space topology:
      - 'chaos'   : FTLE > FTLE_CHAOS_THRESHOLD (irregular / scattered)
      - 'island'  : regular (FTLE <= threshold) belonging to prominent resonance islands
                    selectively highlighted in muted amber
      - 'regular' : remaining regular invariant curves / central core (teal)
    """
    n_ic = len(ftle)
    classes = []
    for i in range(n_ic):
        if key == "A00":
            classes.append("regular")
            continue
        if ftle[i] > FTLE_CHAOS_THRESHOLD:
            classes.append("chaos")
            continue

        th_i = th_w[i]
        v_i = v_a[i]
        # Selective highlight of the prominent 1:1 primary resonance island on the left
        # (crescent in A=0.05, D-shaped surviving resonance island in A=0.20)
        if key == "A05":
            in_left_res = (th_i.max() < -0.25) and (th_i.min() > -3.05) and (np.abs(v_i).max() < 1.85)
            classes.append("island" if in_left_res else "regular")
        elif key == "A20":
            in_left_res = (th_i.max() < -0.50) and (np.abs(v_i).max() < 1.35)
            classes.append("island" if in_left_res else "regular")
        else:
            classes.append("regular")
    return classes


def setup_phase_axes(ax, show_ylabel=True):
    SLATE = "#334155"
    NAVY = "#0f172a"
    BORDER_CARD = "#cbd5e1"

    ax.set_facecolor("#ffffff")
    ax.set_xlim(-np.pi, np.pi)
    ax.set_ylim(-2.6, 2.6)
    ax.set_xticks([-np.pi, -np.pi / 2, 0.0, np.pi / 2, np.pi])
    ax.set_xticklabels([r"$-\pi$", r"$-\pi/2$", r"$0$", r"$\pi/2$", r"$\pi$"], fontsize=15.4, weight="bold", color=SLATE)
    ax.set_yticks([-2, -1, 0, 1, 2])
    ax.set_yticklabels(["-2", "-1", "0", "1", "2"], fontsize=15.4, weight="bold", color=SLATE)
    ax.tick_params(axis="both", which="major", length=4.5, width=1.2, colors=SLATE, pad=4)
    ax.set_xlabel(r"$\boldsymbol{\theta}$", fontsize=18.5, weight="bold", color=NAVY, labelpad=1)
    if show_ylabel:
        ax.set_ylabel(r"$\boldsymbol{\dot{\theta}}$", fontsize=18.8, weight="bold", color=NAVY, labelpad=2)
    for g in (-np.pi / 2, 0.0, np.pi / 2):
        ax.axvline(g, color="#f1f5f9", lw=0.9, zorder=1)
    for g in (-2, -1, 0, 1, 2):
        ax.axhline(g, color="#f1f5f9", lw=0.9, zorder=1)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER_CARD)
        sp.set_linewidth(1.3)


def create_figure(data=None, output_path=None):
    if data is None:
        data = load_or_compute_data(force_recompute=False)
    out_path = Path(output_path) if output_path is not None else OUTPUT_PNG
    # Exact 3-panel canvas geometry & typography scale matching Figure 1 (homoclinic_tangle_to_horseshoe.png)
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
    PURPLE_LIGHT = "#eef2ff"
    PURPLE_BORDER = "#a5b4fc"

    # Data colors matching the specification & Article 3 palette
    COL_REGULAR = "#0d9488"       # Teal (regular invariant curves & central core)
    COL_ISLAND = "#c97a16"        # Muted amber (selectively highlighted resonance island)
    COL_ISLAND_TEXT = "#9a5508"   # Darker muted amber for legible annotation
    COL_CHAOS = "#73638f"         # Translucent muted purple for chaotic sea
    COL_CHAOS_TEXT = "#4b3b68"    # Darker muted purple for legible annotation

    HALO = [pe.withStroke(linewidth=4.0, foreground="#ffffff", alpha=0.96)]

    # -------------------------------------------------------------------------
    # Global Title & Subtitle (matching Figure 1: 29.2 pt bold / 21.3 pt italic)
    # -------------------------------------------------------------------------
    fig.text(
        0.5, 0.964,
        "Persistence and Disruption of Invariant Curves",
        fontsize=29.2, weight="bold", color=NAVY, ha="center", va="center",
    )
    fig.text(
        0.5, 0.920,
        "Stroboscopic Poincaré sections of the undamped driven pendulum (Ω = 0.80) under increasing forcing",
        fontsize=21.0, style="italic", weight="normal", color=DARK_SLATE, ha="center", va="center",
    )

    ax_bg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=0)
    ax_bg.set_xlim(0.0, 1.0)
    ax_bg.set_ylim(0.0, 1.0)
    ax_bg.axis("off")

    # -------------------------------------------------------------------------
    # Three Equal-Width Parallel Panel Cards (A, B, C)
    # -------------------------------------------------------------------------
    y_card = 0.044
    h_card = 0.848
    x1, w1 = 0.012, 0.312
    x2, w2 = 0.344, 0.312
    x3, w3 = 0.676, 0.312

    hbar_h = 0.128
    badge_y = y_card + h_card - hbar_h / 2.0

    panels_spec = [
        (
            x1, w1, "A", "Integrable system (A = 0)",
            "Invariant curves and separatrix",
            BLUE_ACCENT, BLUE_LIGHT, BLUE_BORDER,
            "Conserved mechanical energy confines\ntrajectories to fixed energy contours,\nwith the separatrix dividing\noscillations from rotations.",
            "A00",
        ),
        (
            x2, w2, "B", "Weak forcing (A = 0.05)",
            "Surviving curves and islands",
            TEAL_ACCENT, TEAL_LIGHT, TEAL_BORDER,
            "Many invariant curves persist in\ndeformed form, while resonances form\nislands and a narrow chaotic layer.",
            "A05",
        ),
        (
            x3, w3, "C", "Stronger forcing (A = 0.20)",
            "Extensive chaos and islands",
            PURPLE_ACCENT, PURPLE_LIGHT, PURPLE_BORDER,
            "A broad chaotic region surrounds the\nformer separatrix, coexisting with\nsurviving curves and regular islands.",
            "A20",
        ),
    ]

    for px, pw, letter, title, subtitle, acc_color, bg_tint, bdr_color, _, _ in panels_spec:
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

        text_offset_x = badge_x + 0.0205
        ax_bg.text(
            text_offset_x, badge_y + 0.023, title,
            fontsize=20.4, weight="bold", color=NAVY, va="center", zorder=4,
        )
        ax_bg.text(
            text_offset_x, badge_y - 0.023, subtitle,
            fontsize=17.0, weight="bold", color=MUTED_SLATE, va="center", zorder=4,
        )

    # Progression arrows between panel headers (A -> B -> C)
    for gap_x0, gap_x1 in ((x1 + w1 + 0.003, x2 - 0.003), (x2 + w2 + 0.003, x3 - 0.003)):
        ax_bg.add_patch(patches.FancyArrowPatch(
            (gap_x0, badge_y), (gap_x1, badge_y),
            arrowstyle="-|>,head_length=6.5,head_width=4.2",
            color="#64748b", linewidth=2.0, zorder=5,
        ))

    # -------------------------------------------------------------------------
    # Phase-Space Plots & Bottom Summary Boxes
    # -------------------------------------------------------------------------
    y_box = 0.050
    h_box = 0.132
    y_plot = 0.260
    h_plot = 0.486
    w_plot = 0.258

    th_sep = np.linspace(-np.pi, np.pi, 500)
    v_sep = 2.0 * np.cos(th_sep / 2.0)

    axes_list = []
    for idx_p, (px, pw, letter, _, _, _, _, bdr_color, box_txt, key) in enumerate(panels_spec):
        # Bottom box
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px + 0.008, y_box), pw - 0.016, h_box,
            boxstyle="round,pad=0.0,rounding_size=0.014",
            facecolor=BG_BOX, edgecolor=bdr_color, linewidth=1.3, zorder=3,
        ))
        n_lines = box_txt.count("\n") + 1
        ax_bg.text(
            px + pw / 2.0, y_box + h_box / 2.0, box_txt,
            fontsize=16.2,
            weight="bold", color=DARK_SLATE,
            ha="center", va="center",
            linespacing=1.08 if n_lines >= 4 else 1.20,
            zorder=4,
        )

        # Phase-space axes (identical dimensions & scales across all 3 panels)
        ax_left = px + (pw - w_plot) / 2.0 + 0.014
        ax = fig.add_axes([ax_left, y_plot, w_plot, h_plot], zorder=5)
        setup_phase_axes(ax, show_ylabel=True)
        axes_list.append(ax)

        th_w = wrap_pi(data[f"th_{key}"])
        v_a = data[f"v_{key}"]
        ftle = data[f"ftle_{key}"]
        classes = classify_orbits(key, th_w, v_a, ftle)

        # Separate arrays for fast, clean layered plotting: chaos underneath, regular & islands crisp on top
        ch_x, ch_y = [], []
        rg_x, rg_y = [], []
        is_x, is_y = [], []

        for i, cls in enumerate(classes):
            if cls == "chaos":
                ch_x.append(th_w[i])
                ch_y.append(v_a[i])
            elif cls == "island":
                is_x.append(th_w[i])
                is_y.append(v_a[i])
            else:
                rg_x.append(th_w[i])
                rg_y.append(v_a[i])

        if ch_x:
            # Cap chaotic density lightly by keeping every sample in A=0.05 and subsampling evenly in A=0.20
            # so translucent chaotic sea stays airy and never turns muddy
            step_c = 1 if key == "A05" else 2
            cx = np.concatenate([a[::step_c] for a in ch_x])
            cy = np.concatenate([a[::step_c] for a in ch_y])
            ax.scatter(
                cx, cy,
                s=1.20 if key == "A05" else 1.15,
                color=COL_CHAOS,
                alpha=0.31 if key == "A05" else 0.30,
                linewidths=0,
                rasterized=False,
                zorder=2,
            )

        if rg_x:
            rx = np.concatenate(rg_x)
            ry = np.concatenate(rg_y)
            ax.scatter(
                rx, ry,
                s=1.25,
                color=COL_REGULAR,
                alpha=0.78,
                linewidths=0,
                zorder=4,
            )

        if is_x:
            ix = np.concatenate(is_x)
            iy = np.concatenate(is_y)
            ax.scatter(
                ix, iy,
                s=1.45,
                color=COL_ISLAND,
                alpha=0.88,
                linewidths=0,
                zorder=5,
            )

        # Unforced separatrix: solid thin dark curve in A, pale dashed reference in B & C
        if key == "A00":
            ax.plot(th_sep, v_sep, color=NAVY, lw=2.0, ls="-", zorder=6)
            ax.plot(th_sep, -v_sep, color=NAVY, lw=2.0, ls="-", zorder=6)
        else:
            ax.plot(th_sep, v_sep, color="#475569", lw=1.45, ls="--", alpha=0.58, zorder=6)
            ax.plot(th_sep, -v_sep, color="#475569", lw=1.45, ls="--", alpha=0.58, zorder=6)

    # -------------------------------------------------------------------------
    # Restrained, High-Legibility Annotations (crisp even at Medium's 680px width)
    # -------------------------------------------------------------------------
    axA, axB, axC = axes_list
    lbl_pill = dict(boxstyle="round,pad=0.20", facecolor="#ffffff", edgecolor="none", alpha=0.88)

    # Panel A: label an invariant curve and the unforced separatrix
    axA.text(
        0.0, 2.27, "Separatrix",
        fontsize=15.0, weight="bold", color=NAVY,
        ha="center", va="center", bbox=lbl_pill, zorder=9,
    )
    axA.annotate(
        "",
        xy=(0.0, 2.02), xytext=(0.0, 2.15),
        arrowprops=dict(arrowstyle="-|>", mutation_scale=11.5, color=NAVY, lw=1.6),
        zorder=9,
    )
    axA.annotate(
        "Invariant\ncurve",
        xy=(-0.64, -0.78),
        xytext=(-2.12, -1.84),
        fontsize=14.8, weight="bold", color=TEAL_DARK,
        ha="center", va="center", linespacing=1.08,
        bbox=lbl_pill,
        arrowprops=dict(arrowstyle="-|>", mutation_scale=12.5, color=TEAL_DARK, lw=1.9),
        zorder=9,
    )

    # Panel B: label the amber resonance island AND a verified quasiperiodic teal curve
    # (orbit ic=27: FTLE=0.0017, rotation number rho=-0.1550 well away from low-order rationals,
    #  max angular gap 1.85 deg across 450 samples)
    axB.annotate(
        "Resonance\nisland",
        xy=(-1.78, -0.45),
        xytext=(-2.00, -1.88),
        fontsize=15.0, weight="bold", color=COL_ISLAND_TEXT,
        ha="center", va="center", linespacing=1.08,
        bbox=lbl_pill,
        arrowprops=dict(arrowstyle="-|>", mutation_scale=12.5, color=COL_ISLAND_TEXT, lw=1.9),
        zorder=9,
    )
    th_qp = wrap_pi(data["th_A05"][27])
    v_qp = data["v_A05"][27]
    j_qp = int(np.argmin(np.hypot(th_qp - 0.94, v_qp - 0.67)))
    axB.annotate(
        "Quasiperiodic\nmotion",
        xy=(float(th_qp[j_qp]), float(v_qp[j_qp])),
        xytext=(1.76, 1.78),
        fontsize=14.8, weight="bold", color=TEAL_DARK,
        ha="center", va="center", linespacing=1.08,
        bbox=lbl_pill,
        arrowprops=dict(arrowstyle="-|>", mutation_scale=12.5, color=TEAL_DARK, lw=1.9),
        zorder=9,
    )

    # Panel C: label the chaotic region and one surviving regular island
    axC.text(
        0.0, 1.38, "Chaotic region",
        fontsize=15.2, weight="bold", color=COL_CHAOS_TEXT,
        ha="center", va="center", bbox=lbl_pill, zorder=9,
    )
    axC.annotate(
        "Surviving\nregular island",
        xy=(0.74, -0.34),
        xytext=(0.90, -1.36),
        fontsize=15.0, weight="bold", color=TEAL_DARK,
        ha="center", va="center", linespacing=1.08,
        bbox=lbl_pill,
        arrowprops=dict(arrowstyle="-|>", mutation_scale=12.5, color=TEAL_DARK, lw=1.9),
        zorder=9,
    )

    # Shared bottom legend for the dashed reference separatrix in Panels B & C
    leg_y = 0.019
    leg_xc = 0.5 * (x2 + x3 + w3)  # centered cleanly beneath Panels B and C
    ax_bg.plot(
        [leg_xc - 0.198, leg_xc - 0.168], [leg_y, leg_y],
        color="#475569", lw=2.3, ls="--", alpha=0.82, zorder=5,
    )
    ax_bg.text(
        leg_xc - 0.160, leg_y,
        "Dashed gray curve (Panels B & C): unforced separatrix (reference)",
        fontsize=15.6, weight="bold", color=MUTED_SLATE,
        ha="left", va="center", zorder=5,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160, facecolor="#ffffff")
    plt.close(fig)
    print(f"Saved {out_path} ({out_path.stat().st_size / (1024 * 1024):.2f} MB)")


def main():
    force = "--recompute" in sys.argv
    data = load_or_compute_data(force_recompute=force)
    create_figure(data)


if __name__ == "__main__":
    main()
