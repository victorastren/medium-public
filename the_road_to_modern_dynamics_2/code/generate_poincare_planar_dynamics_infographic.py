#!/usr/bin/env python3
r"""
Generate infographic for Article 2:
"Poincaré’s qualitative approach to planar dynamical systems"

Adapted to match the exact aesthetic, palette, font hierarchy, and card structure of:
`images/poincare_bendixson_theorem.png`
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "poincare_planar_dynamics_infographic.png"


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Matplotlib styling for publication quality
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'axes.edgecolor': '#94a3b8',
        'axes.linewidth': 1.2,
    })

    # High-resolution widescreen canvas (18 x 9.9 inches at 240 DPI)
    fig_w = 18.0
    fig_h = 9.9
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Curated Editorial Palette matching poincare_bendixson_theorem.png
    NAVY = '#0f172a'          # Deep slate navy for main headings
    DARK_SLATE = '#1e293b'    # Body text & subheaders
    SLATE = '#334155'         # Secondary text
    MUTED = '#64748b'         # Captions & axes
    BORDER_CARD = '#cbd5e1'   # Card border
    BG_CARD = '#f8fafc'       # Light background for panels

    BLUE_ACCENT = '#2563eb'   # Primary blue accent
    BLUE_LIGHT = '#eff6ff'    # Soft blue tint
    BLUE_BORDER = '#93c5fd'   # Blue card border

    EMERALD_ACCENT = '#059669' # Emerald accent
    EMERALD_LIGHT = '#ecfdf5'  # Soft emerald tint
    EMERALD_BORDER = '#6ee7b7' # Emerald border

    PURPLE_ACCENT = '#7c3aed' # Purple accent
    PURPLE_LIGHT = '#f5f3ff'  # Soft purple tint
    PURPLE_BORDER = '#c4b5fd' # Purple border

    RED_ACCENT = '#dc2626'    # Red accent
    RED_LIGHT = '#fef2f2'     # Soft red tint
    RED_BORDER = '#fca5a5'    # Red border

    AMBER_ACCENT = '#d97706'  # Amber accent
    AMBER_LIGHT = '#fffbeb'   # Soft amber tint
    AMBER_BORDER = '#fcd34d'  # Amber border

    # -------------------------------------------------------------
    # Main Header & Context Banner (matching poincare_bendixson_theorem.png)
    # -------------------------------------------------------------
    fig.text(0.5, 0.966,
             "Poincaré’s qualitative approach to planar dynamical systems",
             fontsize=20.5, weight='bold', color=NAVY, ha='center', va='center')

    fig.text(0.5, 0.932,
             "From local analysis near equilibria to the global organization of trajectories",
             fontsize=16.5, style='italic', color=DARK_SLATE, ha='center', va='center')

    # Background axis for panel cards, headers, badges, and subcard containers
    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')

    # =========================================================================
    # ROW 1: Section 1 - Local behavior near singular points (equilibria)
    # =========================================================================
    x_r1 = 0.022
    w_r1 = 0.956
    y_r1 = 0.510
    h_r1 = 0.396

    # Outer Card for Row 1
    card1 = patches.FancyBboxPatch(
        (x_r1, y_r1), w_r1, h_r1,
        boxstyle="round,pad=0.0,rounding_size=0.016",
        facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.4,
        zorder=1
    )
    ax_bg.add_patch(card1)

    # Header accent bar for Row 1
    hbar_h1 = 0.056
    hbar1 = patches.FancyBboxPatch(
        (x_r1, y_r1 + h_r1 - hbar_h1), w_r1, hbar_h1,
        boxstyle="round,pad=0.0,rounding_size=0.016",
        facecolor=BLUE_LIGHT, edgecolor=BLUE_BORDER, linewidth=1.2,
        zorder=2
    )
    ax_bg.add_patch(hbar1)

    # Badge 1 (identical circle in normalized coords -> ellipse on widescreen)
    b1_x = x_r1 + 0.022
    b1_y = y_r1 + h_r1 - hbar_h1 / 2
    b1_c = patches.Circle(
        (b1_x, b1_y), 0.016,
        facecolor=BLUE_ACCENT, edgecolor='none',
        zorder=3
    )
    ax_bg.add_patch(b1_c)
    ax_bg.text(b1_x, b1_y, "1", fontsize=15.0, weight='bold',
               color='#ffffff', ha='center', va='center', zorder=4)

    # Header title & formula
    ax_bg.text(b1_x + 0.022, b1_y, "Local behavior near singular points (equilibria)",
               fontsize=16.5, weight='bold', color=NAVY, va='center', zorder=4)
    ax_bg.text(x_r1 + w_r1 - 0.020, b1_y, r"$\dot x = f(x, y), \quad \dot y = g(x, y)$",
               fontsize=15.5, color=DARK_SLATE, ha='right', va='center', zorder=4)

    # 4 Subcards for Row 1
    margin_sub1 = 0.010
    gap_sub1 = 0.010
    w_sub1 = (w_r1 - 2 * margin_sub1 - 3 * gap_sub1) / 4.0
    h_sub1 = h_r1 - hbar_h1 - 0.018
    y_sub1 = y_r1 + 0.010

    subcards_r1 = [
        ("(a) Stable node", "Nearby trajectories approach\nthe equilibrium as $t \\to \\infty$.",
         BLUE_ACCENT, BLUE_LIGHT, BLUE_BORDER),
        ("(b) Unstable node", "Nearby trajectories move away\nfrom the equilibrium as $t \\to \\infty$.",
         RED_ACCENT, RED_LIGHT, RED_BORDER),
        ("(c) Saddle point", "Two separatrices approach the\nequilibrium and two leave it.",
         EMERALD_ACCENT, EMERALD_LIGHT, EMERALD_BORDER),
        ("(d) Focus (spiral)", "Trajectories spiral toward (stable)\nor away from (unstable) the equilibrium.",
         PURPLE_ACCENT, PURPLE_LIGHT, PURPLE_BORDER),
    ]

    h_sub_bar = 0.038
    h_cap1 = 0.062
    y_plot_sub1 = y_sub1 + h_cap1 + 0.008
    h_plot_sub1 = h_sub1 - h_sub_bar - h_cap1 - 0.016

    axes_r1 = []

    for i, (title, caption, acc_c, bg_t, bdr_c) in enumerate(subcards_r1):
        x_sub = x_r1 + margin_sub1 + i * (w_sub1 + gap_sub1)

        # Subcard outer frame
        sc_box = patches.FancyBboxPatch(
            (x_sub, y_sub1), w_sub1, h_sub1,
            boxstyle="round,pad=0.0,rounding_size=0.012",
            facecolor='#ffffff', edgecolor=BORDER_CARD, linewidth=1.1,
            zorder=2
        )
        ax_bg.add_patch(sc_box)

        # Subcard header bar
        sc_hdr = patches.FancyBboxPatch(
            (x_sub, y_sub1 + h_sub1 - h_sub_bar), w_sub1, h_sub_bar,
            boxstyle="round,pad=0.0,rounding_size=0.012",
            facecolor=bg_t, edgecolor=bdr_c, linewidth=1.0,
            zorder=3
        )
        ax_bg.add_patch(sc_hdr)

        # Header title
        ax_bg.text(x_sub + w_sub1 / 2, y_sub1 + h_sub1 - h_sub_bar / 2, title,
                   fontsize=14.0, weight='bold', color=DARK_SLATE, ha='center', va='center', zorder=4)

        # Caption box at bottom
        sc_cap = patches.FancyBboxPatch(
            (x_sub + 0.004, y_sub1 + 0.004), w_sub1 - 0.008, h_cap1 - 0.004,
            boxstyle="round,pad=0.0,rounding_size=0.010",
            facecolor=bg_t, edgecolor='none',
            zorder=3
        )
        ax_bg.add_patch(sc_cap)

        ax_bg.text(x_sub + w_sub1 / 2, y_sub1 + 0.004 + (h_cap1 - 0.004) / 2, caption,
                   fontsize=11.8, weight='bold', color=DARK_SLATE, ha='center', va='center',
                   linespacing=1.24, zorder=4)

        # Matplotlib axis for the plot
        margin_ax_x = 0.006
        ax = fig.add_axes([x_sub + margin_ax_x, y_plot_sub1, w_sub1 - 2 * margin_ax_x, h_plot_sub1], zorder=5)
        axes_r1.append(ax)

    # -------------------------------------------------------------
    # Plot (a): Stable Node
    # -------------------------------------------------------------
    ax_a = axes_r1[0]
    ax_a.set_facecolor('#ffffff')
    ax_a.set_xlim(-1.45, 1.45)
    ax_a.set_ylim(-1.40, 1.40)
    ax_a.axis('off')

    ax_a.annotate("", xy=(1.38, 0), xytext=(-1.38, 0),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_a.annotate("", xy=(0, 1.35), xytext=(0, -1.35),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_a.text(1.42, 0, r"$x$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='left', va='center', zorder=3)
    ax_a.text(0, 1.38, r"$y$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='center', va='bottom', zorder=3)

    t_vals = np.linspace(0, 3.0, 70)
    ray_angles = np.array([
        16, 36, 56, 76, 104, 124, 144, 164,
        196, 216, 236, 256, 284, 304, 324, 344
    ])
    for th_deg in ray_angles:
        rad = np.radians(th_deg)
        x0 = 1.20 * np.cos(rad)
        y0 = 1.20 * np.sin(rad)
        xt = x0 * np.exp(-0.75 * t_vals)
        yt = y0 * np.exp(-2.10 * t_vals)
        ax_a.plot(xt, yt, color='#2563eb', lw=1.6, zorder=3)

        idx_arr = 14
        ax_a.annotate("", xy=(xt[idx_arr+1], yt[idx_arr+1]), xytext=(xt[idx_arr], yt[idx_arr]),
                      arrowprops=dict(arrowstyle="-|>", color='#2563eb', mutation_scale=9, lw=1.6),
                      zorder=4)

    ax_a.scatter([0], [0], s=65, color='#0f172a', zorder=6)

    # -------------------------------------------------------------
    # Plot (b): Unstable Node
    # -------------------------------------------------------------
    ax_b = axes_r1[1]
    ax_b.set_facecolor('#ffffff')
    ax_b.set_xlim(-1.45, 1.45)
    ax_b.set_ylim(-1.40, 1.40)
    ax_b.axis('off')

    ax_b.annotate("", xy=(1.38, 0), xytext=(-1.38, 0),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_b.annotate("", xy=(0, 1.35), xytext=(0, -1.35),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_b.text(1.42, 0, r"$x$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='left', va='center', zorder=3)
    ax_b.text(0, 1.38, r"$y$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='center', va='bottom', zorder=3)

    for th_deg in ray_angles:
        rad = np.radians(th_deg)
        x_end = 1.20 * np.cos(rad)
        y_end = 1.20 * np.sin(rad)
        xt = x_end * np.exp(-0.75 * (3.0 - t_vals))
        yt = y_end * np.exp(-2.10 * (3.0 - t_vals))
        ax_b.plot(xt, yt, color='#dc2626', lw=1.6, zorder=3)

        idx_arr = 48
        ax_b.annotate("", xy=(xt[idx_arr+1], yt[idx_arr+1]), xytext=(xt[idx_arr], yt[idx_arr]),
                      arrowprops=dict(arrowstyle="-|>", color='#dc2626', mutation_scale=9, lw=1.6),
                      zorder=4)

    ax_b.scatter([0], [0], s=65, color='#0f172a', zorder=6)

    # -------------------------------------------------------------
    # Plot (c): Saddle Point
    # -------------------------------------------------------------
    ax_c = axes_r1[2]
    ax_c.set_facecolor('#ffffff')
    ax_c.set_xlim(-1.45, 1.45)
    ax_c.set_ylim(-1.40, 1.40)
    ax_c.axis('off')

    ax_c.annotate("", xy=(1.38, 0), xytext=(-1.38, 0),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_c.annotate("", xy=(0, 1.35), xytext=(0, -1.35),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_c.text(1.42, 0, r"$x$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='left', va='center', zorder=3)
    ax_c.text(0, 1.38, r"$y$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='center', va='bottom', zorder=3)

    t_saddle = np.linspace(-1.4, 1.4, 70)
    c_levels = [0.08, 0.22, 0.45, 0.78]
    for s_x in [-1, 1]:
        for s_y in [-1, 1]:
            for C in c_levels:
                xt = s_x * np.sqrt(C) * np.exp(t_saddle)
                yt = s_y * np.sqrt(C) * np.exp(-t_saddle)
                mask = (np.abs(xt) <= 1.25) & (np.abs(yt) <= 1.25)
                ax_c.plot(xt[mask], yt[mask], color='#059669', lw=1.5, zorder=3)

                idx_arr = 35
                if idx_arr < len(xt[mask]) - 1:
                    ax_c.annotate("", xy=(xt[mask][idx_arr+1], yt[mask][idx_arr+1]),
                                  xytext=(xt[mask][idx_arr], yt[mask][idx_arr]),
                                  arrowprops=dict(arrowstyle="-|>", color='#059669', mutation_scale=9, lw=1.5),
                                  zorder=4)

    # Separatrices along axes with arrows
    ax_c.plot([0, 0], [0.1, 1.25], color='#059669', lw=2.0, zorder=3)
    ax_c.plot([0, 0], [-1.25, -0.1], color='#059669', lw=2.0, zorder=3)
    ax_c.annotate("", xy=(0, 0.50), xytext=(0, 0.75),
                  arrowprops=dict(arrowstyle="-|>", color='#059669', mutation_scale=10, lw=2.0), zorder=4)
    ax_c.annotate("", xy=(0, -0.50), xytext=(0, -0.75),
                  arrowprops=dict(arrowstyle="-|>", color='#059669', mutation_scale=10, lw=2.0), zorder=4)

    ax_c.plot([0.1, 1.25], [0, 0], color='#059669', lw=2.0, zorder=3)
    ax_c.plot([-1.25, -0.1], [0, 0], color='#059669', lw=2.0, zorder=3)
    ax_c.annotate("", xy=(0.75, 0), xytext=(0.50, 0),
                  arrowprops=dict(arrowstyle="-|>", color='#059669', mutation_scale=10, lw=2.0), zorder=4)
    ax_c.annotate("", xy=(-0.75, 0), xytext=(-0.50, 0),
                  arrowprops=dict(arrowstyle="-|>", color='#059669', mutation_scale=10, lw=2.0), zorder=4)

    ax_c.scatter([0], [0], s=65, color='#0f172a', zorder=6)

    # -------------------------------------------------------------
    # Plot (d): Focus (Spiral)
    # -------------------------------------------------------------
    ax_d = axes_r1[3]
    ax_d.set_facecolor('#ffffff')
    ax_d.set_xlim(-1.45, 1.45)
    ax_d.set_ylim(-1.40, 1.40)
    ax_d.axis('off')

    ax_d.annotate("", xy=(1.38, 0), xytext=(-1.38, 0),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_d.annotate("", xy=(0, 1.35), xytext=(0, -1.35),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_d.text(1.42, 0, r"$x$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='left', va='center', zorder=3)
    ax_d.text(0, 1.38, r"$y$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='center', va='bottom', zorder=3)

    t_sp = np.linspace(0, 9.5, 130)
    for th0_deg in [0, 90, 180, 270]:
        th0 = np.radians(th0_deg)
        r_sp = 1.25 * np.exp(-0.25 * t_sp)
        theta_sp = th0 + 1.25 * t_sp
        xt = r_sp * np.cos(theta_sp)
        yt = r_sp * np.sin(theta_sp)
        mask = (np.abs(xt) <= 1.25) & (np.abs(yt) <= 1.25) & (r_sp >= 0.05)
        ax_d.plot(xt[mask], yt[mask], color='#7c3aed', lw=1.6, zorder=3)

        idx_arr = 20
        if idx_arr < len(xt[mask]) - 1:
            ax_d.annotate("", xy=(xt[mask][idx_arr+1], yt[mask][idx_arr+1]),
                          xytext=(xt[mask][idx_arr], yt[mask][idx_arr]),
                          arrowprops=dict(arrowstyle="-|>", color='#7c3aed', mutation_scale=9, lw=1.6),
                          zorder=4)

    ax_d.scatter([0], [0], s=65, color='#0f172a', zorder=6)

    # =========================================================================
    # ROW 2: Section 2 - Global organization of trajectories in the phase plane
    # =========================================================================
    x_r2 = 0.022
    w_r2 = 0.956
    y_r2 = 0.014
    h_r2 = 0.484

    # Outer Card for Row 2
    card2 = patches.FancyBboxPatch(
        (x_r2, y_r2), w_r2, h_r2,
        boxstyle="round,pad=0.0,rounding_size=0.016",
        facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.4,
        zorder=1
    )
    ax_bg.add_patch(card2)

    # Header accent bar for Row 2
    hbar_h2 = 0.056
    hbar2 = patches.FancyBboxPatch(
        (x_r2, y_r2 + h_r2 - hbar_h2), w_r2, hbar_h2,
        boxstyle="round,pad=0.0,rounding_size=0.016",
        facecolor=EMERALD_LIGHT, edgecolor=EMERALD_BORDER, linewidth=1.2,
        zorder=2
    )
    ax_bg.add_patch(hbar2)

    # Badge 2 (identical circle in normalized coords -> ellipse on widescreen)
    b2_x = x_r2 + 0.022
    b2_y = y_r2 + h_r2 - hbar_h2 / 2
    b2_c = patches.Circle(
        (b2_x, b2_y), 0.016,
        facecolor=EMERALD_ACCENT, edgecolor='none',
        zorder=3
    )
    ax_bg.add_patch(b2_c)
    ax_bg.text(b2_x, b2_y, "2", fontsize=15.0, weight='bold',
               color='#ffffff', ha='center', va='center', zorder=4)

    # Header title
    ax_bg.text(b2_x + 0.022, b2_y, "Global organization of trajectories in the phase plane",
               fontsize=16.5, weight='bold', color=NAVY, va='center', zorder=4)

    # 3 Subcards for Row 2: (e) Separatrices, (f) Periodic orbits, (g) Phase portrait
    margin_sub2 = 0.010
    gap_sub2 = 0.012
    avail_w2 = w_r2 - 2 * margin_sub2 - 2 * gap_sub2  # ~ 0.912

    # Proportions: Card (e) ~ 29.4%, Card (f) ~ 29.8%, Card (g) ~ 40.8%
    w_e = 0.268 * (avail_w2 / 0.912)
    w_f = 0.272 * (avail_w2 / 0.912)
    w_g = 0.372 * (avail_w2 / 0.912)
    w_sub2 = [w_e, w_f, w_g]

    h_sub2 = h_r2 - hbar_h2 - 0.018
    y_sub2 = y_r2 + 0.010

    subcards_r2 = [
        ("(e) Separatrices and invariant manifolds",
         "The stable and unstable manifolds (red) of a saddle\npoint act as separatrices, dividing the phase plane\ninto regions with different trajectory behavior.",
         AMBER_ACCENT, AMBER_LIGHT, AMBER_BORDER),
        ("(f) Periodic orbits around a center",
         "A center is surrounded by a continuous family of\nnested periodic orbits. Each trajectory returns to\nits initial state after a fixed period without\napproaching or moving away from the equilibrium.",
         BLUE_ACCENT, BLUE_LIGHT, BLUE_BORDER),
        ("(g) Phase portrait: combining local and global structure",
         "The phase portrait shows how local behavior near equilibria\n(nodes, saddles, foci) fits into the global geometry of the system,\nincluding separatrices and periodic orbits.",
         RED_ACCENT, RED_LIGHT, RED_BORDER),
    ]

    h_cap2 = 0.098
    y_plot_sub2 = y_sub2 + h_cap2 + 0.008
    h_plot_sub2 = h_sub2 - h_sub_bar - h_cap2 - 0.016

    axes_r2 = []
    x_curr2 = x_r2 + margin_sub2

    for i, (title, caption, acc_c, bg_t, bdr_c) in enumerate(subcards_r2):
        w_curr = w_sub2[i]

        # Subcard outer frame
        sc_box = patches.FancyBboxPatch(
            (x_curr2, y_sub2), w_curr, h_sub2,
            boxstyle="round,pad=0.0,rounding_size=0.012",
            facecolor='#ffffff', edgecolor=BORDER_CARD, linewidth=1.1,
            zorder=2
        )
        ax_bg.add_patch(sc_box)

        # Subcard header bar
        sc_hdr = patches.FancyBboxPatch(
            (x_curr2, y_sub2 + h_sub2 - h_sub_bar), w_curr, h_sub_bar,
            boxstyle="round,pad=0.0,rounding_size=0.012",
            facecolor=bg_t, edgecolor=bdr_c, linewidth=1.0,
            zorder=3
        )
        ax_bg.add_patch(sc_hdr)

        # Header title
        ax_bg.text(x_curr2 + w_curr / 2, y_sub2 + h_sub2 - h_sub_bar / 2, title,
                   fontsize=14.0, weight='bold', color=DARK_SLATE, ha='center', va='center', zorder=4)

        # Caption box at bottom
        sc_cap = patches.FancyBboxPatch(
            (x_curr2 + 0.004, y_sub2 + 0.004), w_curr - 0.008, h_cap2 - 0.004,
            boxstyle="round,pad=0.0,rounding_size=0.007",
            facecolor=bg_t, edgecolor='none',
            zorder=3
        )
        ax_bg.add_patch(sc_cap)

        # Precise font sizing for balanced multi-line text with ample padding
        fs_cap = 10.5 if i == 1 else 11.2
        lsp_cap = 1.16 if i == 1 else 1.20
        ax_bg.text(x_curr2 + w_curr / 2, y_sub2 + 0.004 + (h_cap2 - 0.004) / 2, caption,
                   fontsize=fs_cap, weight='bold', color=DARK_SLATE, ha='center', va='center',
                   linespacing=lsp_cap, zorder=4)

        # Matplotlib axis for the plot
        margin_ax_x = 0.006
        ax = fig.add_axes([x_curr2 + margin_ax_x, y_plot_sub2, w_curr - 2 * margin_ax_x, h_plot_sub2], zorder=5)
        axes_r2.append(ax)

        x_curr2 += w_curr + gap_sub2

    # -------------------------------------------------------------
    # Plot (e): Separatrices and Invariant Manifolds
    # -------------------------------------------------------------
    ax_e = axes_r2[0]
    ax_e.set_facecolor('#ffffff')
    ax_e.set_xlim(-1.50, 1.50)
    ax_e.set_ylim(-1.30, 1.30)
    ax_e.axis('off')

    ax_e.annotate("", xy=(1.45, 0), xytext=(-1.45, 0),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_e.annotate("", xy=(0, 1.25), xytext=(0, -1.25),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_e.text(1.48, 0, r"$x$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='left', va='center', zorder=3)
    ax_e.text(0, 1.28, r"$y$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='center', va='bottom', zorder=3)

    # 45-degree separatrices (Rotated saddle):
    s_line = np.linspace(-1.35, 1.35, 80)
    ax_e.plot(s_line, -0.65 * s_line, color='#dc2626', lw=2.6, zorder=4)
    ax_e.plot(s_line, 0.65 * s_line, color='#dc2626', lw=2.6, zorder=4)

    # Separatrix direction arrows:
    # Unstable: out from origin
    ax_e.annotate("", xy=(-0.95, 0.65*0.95), xytext=(-0.70, 0.65*0.70),
                  arrowprops=dict(arrowstyle="-|>", color='#dc2626', mutation_scale=12, lw=2.6), zorder=5)
    ax_e.annotate("", xy=(0.95, -0.65*0.95), xytext=(0.70, -0.65*0.70),
                  arrowprops=dict(arrowstyle="-|>", color='#dc2626', mutation_scale=12, lw=2.6), zorder=5)

    # Stable: into origin
    ax_e.annotate("", xy=(0.70, 0.65*0.70), xytext=(0.95, 0.65*0.95),
                  arrowprops=dict(arrowstyle="-|>", color='#dc2626', mutation_scale=12, lw=2.6), zorder=5)
    ax_e.annotate("", xy=(-0.70, -0.65*0.70), xytext=(-0.95, -0.65*0.95),
                  arrowprops=dict(arrowstyle="-|>", color='#dc2626', mutation_scale=12, lw=2.6), zorder=5)

    # Hyperbolic flow curves in green:
    th_rot = np.arctan(0.65)
    cos_r = np.cos(th_rot)
    sin_r = np.sin(th_rot)
    for c_val in [0.08, 0.24, 0.52]:
        xi = np.linspace(0.12, 1.45, 60)
        eta = c_val / xi
        for s_x, s_y in [(-1, 1), (1, 1), (-1, -1), (1, -1)]:
            xr = s_x * xi
            yr = s_y * eta
            x_plot = xr * cos_r - yr * sin_r
            y_plot = xr * sin_r + yr * cos_r
            mask = (np.abs(x_plot) <= 1.35) & (np.abs(y_plot) <= 1.15)
            if np.count_nonzero(mask) > 5:
                ax_e.plot(x_plot[mask], y_plot[mask], color='#10b981', lw=1.5, zorder=3)
                idx_m = len(x_plot[mask]) // 2
                ax_e.annotate("", xy=(x_plot[mask][idx_m+1], y_plot[mask][idx_m+1]),
                              xytext=(x_plot[mask][idx_m], y_plot[mask][idx_m]),
                              arrowprops=dict(arrowstyle="-|>", color='#10b981', mutation_scale=8, lw=1.5),
                              zorder=4)

    # Manifold labels with clean background boxes
    ax_e.text(-1.18, 0.98, "Unstable\nmanifold", fontsize=12.2, weight='bold', color='#dc2626',
              ha='center', va='center',
              bbox=dict(boxstyle="round,pad=0.22", facecolor='#ffffff', edgecolor='#fca5a5', lw=1.0), zorder=7)
    ax_e.annotate("", xy=(-0.78, 0.51), xytext=(-1.02, 0.82),
                  arrowprops=dict(arrowstyle="->", color='#dc2626', lw=1.6), zorder=7)

    ax_e.text(1.18, 0.98, "Stable\nmanifold", fontsize=12.2, weight='bold', color='#dc2626',
              ha='center', va='center',
              bbox=dict(boxstyle="round,pad=0.22", facecolor='#ffffff', edgecolor='#fca5a5', lw=1.0), zorder=7)
    ax_e.annotate("", xy=(0.78, 0.51), xytext=(1.02, 0.82),
                  arrowprops=dict(arrowstyle="->", color='#dc2626', lw=1.6), zorder=7)

    ax_e.scatter([0], [0], s=70, color='#0f172a', zorder=8)

    # -------------------------------------------------------------
    # Plot (f): Periodic Orbits (Limit Cycles)
    # -------------------------------------------------------------
    ax_f = axes_r2[1]
    ax_f.set_facecolor('#ffffff')
    ax_f.set_xlim(-1.50, 1.50)
    ax_f.set_ylim(-1.30, 1.30)
    ax_f.axis('off')

    ax_f.annotate("", xy=(1.45, 0), xytext=(-1.45, 0),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_f.annotate("", xy=(0, 1.25), xytext=(0, -1.25),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_f.text(1.48, 0, r"$x$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='left', va='center', zorder=3)
    ax_f.text(0, 1.28, r"$y$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='center', va='bottom', zorder=3)

    ths = np.linspace(0, 2 * np.pi, 120)
    orbit_scales = [0.42, 0.72, 1.02, 1.30]
    for r_sc in orbit_scales:
        xo = r_sc * np.cos(ths)
        yo = 0.65 * r_sc * np.sin(ths)
        ax_f.plot(xo, yo, color='#2563eb', lw=1.8, zorder=3)

        # Counterclockwise circulation arrows
        th_arr = np.pi / 2
        xa = r_sc * np.cos(th_arr)
        ya = 0.65 * r_sc * np.sin(th_arr)
        ax_f.annotate("", xy=(xa - 0.08, ya), xytext=(xa + 0.08, ya),
                      arrowprops=dict(arrowstyle="-|>", color='#2563eb', mutation_scale=10, lw=1.8),
                      zorder=4)
        th_arr2 = 3 * np.pi / 2
        xa2 = r_sc * np.cos(th_arr2)
        ya2 = 0.65 * r_sc * np.sin(th_arr2)
        ax_f.annotate("", xy=(xa2 + 0.08, ya2), xytext=(xa2 - 0.08, ya2),
                      arrowprops=dict(arrowstyle="-|>", color='#2563eb', mutation_scale=10, lw=1.8),
                      zorder=4)

    ax_f.scatter([0], [0], s=65, color='#0f172a', zorder=6)

    # -------------------------------------------------------------
    # Plot (g): Phase Portrait: Combining Local and Global Structure
    # Exact double-well / homoclinic phase portrait:
    # -------------------------------------------------------------
    ax_g = axes_r2[2]
    ax_g.set_facecolor('#ffffff')
    ax_g.set_xlim(-2.45, 2.45)
    ax_g.set_ylim(-1.30, 1.30)
    ax_g.axis('off')

    ax_g.annotate("", xy=(2.40, 0), xytext=(-2.40, 0),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_g.annotate("", xy=(0, 1.25), xytext=(0, -1.25),
                  arrowprops=dict(arrowstyle="->", color='#334155', lw=1.3), zorder=2)
    ax_g.text(2.42, 0, r"$x$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='left', va='center', zorder=3)
    ax_g.text(0, 1.28, r"$y$", fontsize=13.0, style='italic', color=DARK_SLATE, ha='center', va='bottom', zorder=3)

    scale_x = 1.38
    scale_y = 1.05

    # Double-well Homoclinic Separatrix (Red) crossing at (0, 0):
    x_sub_r = np.linspace(0.001, np.sqrt(2) - 0.001, 120)
    y_sub_r = x_sub_r * np.sqrt(1.0 - 0.5 * x_sub_r**2)
    ax_g.plot(scale_x * x_sub_r, scale_y * y_sub_r, color='#dc2626', lw=2.4, zorder=5)
    ax_g.plot(scale_x * x_sub_r, -scale_y * y_sub_r, color='#dc2626', lw=2.4, zorder=5)

    x_sub_l = -x_sub_r
    ax_g.plot(scale_x * x_sub_l, scale_y * y_sub_r, color='#dc2626', lw=2.4, zorder=5)
    ax_g.plot(scale_x * x_sub_l, -scale_y * y_sub_r, color='#dc2626', lw=2.4, zorder=5)

    # Direction arrows on separatrices:
    ax_g.annotate("", xy=(-scale_x * 0.95, scale_y * 0.60), xytext=(-scale_x * 0.85, scale_y * 0.65),
                  arrowprops=dict(arrowstyle="-|>", color='#dc2626', mutation_scale=10, lw=2.4), zorder=6)
    ax_g.annotate("", xy=(scale_x * 0.85, scale_y * 0.65), xytext=(scale_x * 0.95, scale_y * 0.60),
                  arrowprops=dict(arrowstyle="-|>", color='#dc2626', mutation_scale=10, lw=2.4), zorder=6)

    # Left Feature: Stable Focus at x = -scale_x * 1.0
    xf_0 = -scale_x * 1.0
    t_foc = np.linspace(0, 8.5, 120)
    for th_f0 in [0, np.pi/2, np.pi, 3*np.pi/2]:
        r_foc = 0.55 * np.exp(-0.28 * t_foc)
        ang_foc = th_f0 + 1.8 * t_foc
        xf_t = xf_0 + r_foc * np.cos(ang_foc)
        yf_t = 0.82 * r_foc * np.sin(ang_foc)
        ax_g.plot(xf_t, yf_t, color='#2563eb', lw=1.5, zorder=4)

        idx_f = 16
        ax_g.annotate("", xy=(xf_t[idx_f+1], yf_t[idx_f+1]), xytext=(xf_t[idx_f], yf_t[idx_f]),
                      arrowprops=dict(arrowstyle="-|>", color='#2563eb', mutation_scale=8, lw=1.5), zorder=5)

    ax_g.scatter([xf_0], [0], s=65, color='#0f172a', zorder=7)

    # Stable focus label with box
    ax_g.text(xf_0 - 0.28, 1.02, "Stable\nfocus", fontsize=12.2, weight='bold', color='#2563eb',
              ha='center', va='center',
              bbox=dict(boxstyle="round,pad=0.22", facecolor='#ffffff', edgecolor='#93c5fd', lw=1.0), zorder=7)
    ax_g.annotate("", xy=(xf_0 - 0.25, 0.42), xytext=(xf_0 - 0.28, 0.82),
                  arrowprops=dict(arrowstyle="->", color='#2563eb', lw=1.6), zorder=7)

    # Center Feature: Saddle Point at (0, 0)
    ax_g.scatter([0], [0], s=75, color='#0f172a', zorder=8)
    ax_g.text(0, 0.98, "Saddle", fontsize=12.5, weight='bold', color=DARK_SLATE,
              ha='center', va='center',
              bbox=dict(boxstyle="round,pad=0.22", facecolor='#ffffff', edgecolor='#cbd5e1', lw=1.0), zorder=7)
    ax_g.annotate("", xy=(0, 0.12), xytext=(0, 0.82),
                  arrowprops=dict(arrowstyle="->", color=DARK_SLATE, lw=1.5), zorder=7)

    # 4. Right Feature: Attracting Limit Cycle around x = scale_x * 1.0
    xp_0 = scale_x * 1.0
    a_lc = 0.44
    b_lc = 0.32

    # (i) Central repeller (unstable focus equilibrium)
    ax_g.scatter([xp_0], [0], s=65, color='#0f172a', zorder=7)

    # (ii) The Single Prominent Attracting Limit Cycle (thick solid orange closed orbit)
    ths_lc = np.linspace(0, 2 * np.pi, 200)
    ax_g.plot(xp_0 + a_lc * np.cos(ths_lc), b_lc * np.sin(ths_lc), color='#ea580c', lw=3.2, zorder=6)

    # Arrowheads on the limit cycle indicating counterclockwise circulation
    ax_g.annotate("", xy=(xp_0 - 0.06, b_lc), xytext=(xp_0 + 0.06, b_lc),
                  arrowprops=dict(arrowstyle="-|>", color='#ea580c', mutation_scale=11, lw=3.2), zorder=7)
    ax_g.annotate("", xy=(xp_0 + 0.06, -b_lc), xytext=(xp_0 - 0.06, -b_lc),
                  arrowprops=dict(arrowstyle="-|>", color='#ea580c', mutation_scale=11, lw=3.2), zorder=7)

    # (iii) Interior trajectories spiraling OUTWARD from equilibrium toward the limit cycle
    t_in = np.linspace(0, 2.0, 70)
    u0_in = 0.06
    r_in = np.sqrt(u0_in / (u0_in + (1.0 - u0_in) * np.exp(-2.5 * t_in)))

    # Spiral 1: theta from ~15 deg to ~235 deg
    ang_in1 = np.radians(15) + 2.0 * t_in
    xi1 = xp_0 + a_lc * r_in * np.cos(ang_in1)
    yi1 = b_lc * r_in * np.sin(ang_in1)
    ax_g.plot(xi1, yi1, color='#f97316', lw=1.6, zorder=4)
    ax_g.annotate("", xy=(xi1[35], yi1[35]), xytext=(xi1[31], yi1[31]),
                  arrowprops=dict(arrowstyle="-|>", color='#f97316', mutation_scale=8, lw=1.6), zorder=5)

    # Spiral 2: theta from ~195 deg to ~415 deg
    ang_in2 = np.radians(195) + 2.0 * t_in
    xi2 = xp_0 + a_lc * r_in * np.cos(ang_in2)
    yi2 = b_lc * r_in * np.sin(ang_in2)
    ax_g.plot(xi2, yi2, color='#f97316', lw=1.6, zorder=4)
    ax_g.annotate("", xy=(xi2[35], yi2[35]), xytext=(xi2[31], yi2[31]),
                  arrowprops=dict(arrowstyle="-|>", color='#f97316', mutation_scale=8, lw=1.6), zorder=5)

    # (iv) Exterior trajectories spiraling INWARD from within separatrix lobe toward the limit cycle
    # Strictly bounded inside the homoclinic separatrix, respecting invariant manifolds
    t_out = np.linspace(0, 1.8, 65)
    factor_out = 1.0 + 0.44 * np.exp(-2.0 * t_out)

    # Outer spiral 1: starts at upper-left inside lobe, winds to ~280 deg
    ang_out1 = np.radians(130) + 1.8 * t_out
    xo1 = xp_0 + a_lc * factor_out * np.cos(ang_out1)
    yo1 = b_lc * factor_out * np.sin(ang_out1)
    ax_g.plot(xo1, yo1, color='#f97316', lw=1.6, zorder=4)
    ax_g.annotate("", xy=(xo1[28], yo1[28]), xytext=(xo1[24], yo1[24]),
                  arrowprops=dict(arrowstyle="-|>", color='#f97316', mutation_scale=8, lw=1.6), zorder=5)

    # Outer spiral 2: starts at lower-right inside lobe, winds to ~100 deg
    ang_out2 = np.radians(310) + 1.8 * t_out
    xo2 = xp_0 + a_lc * factor_out * np.cos(ang_out2)
    yo2 = b_lc * factor_out * np.sin(ang_out2)
    ax_g.plot(xo2, yo2, color='#f97316', lw=1.6, zorder=4)
    ax_g.annotate("", xy=(xo2[28], yo2[28]), xytext=(xo2[24], yo2[24]),
                  arrowprops=dict(arrowstyle="-|>", color='#f97316', mutation_scale=8, lw=1.6), zorder=5)

    # (v) Periodic orbit / limit cycle callout box shifted cleanly to the right
    # Positioned at x = 1.88, y = 1.04 (completely clear of the red separatrix)
    x_box_lc = 1.88
    y_box_lc = 1.04
    ax_g.text(x_box_lc, y_box_lc, "Periodic orbit\n(limit cycle)", fontsize=12.2, weight='bold', color='#ea580c',
              ha='center', va='center',
              bbox=dict(boxstyle="round,pad=0.22", facecolor='#ffffff', edgecolor='#fed7aa', lw=1.0), zorder=8)

    # Arrow landing directly and unambiguously on the solitary limit cycle curve at theta = 50 degrees
    th_target = np.radians(50.0)
    x_target = xp_0 + a_lc * np.cos(th_target)
    y_target = b_lc * np.sin(th_target)
    ax_g.annotate("", xy=(x_target, y_target), xytext=(x_box_lc - 0.08, y_box_lc - 0.16),
                  arrowprops=dict(arrowstyle="->", color='#ea580c', lw=1.8, mutation_scale=12), zorder=9)

    # Global Outer Connecting Trajectories using smooth Cassini Ovals enclosing both lobes:
    # (x^2 + y^2 + c^2)^2 - 4 c^2 x^2 = a^4
    c_cas = 1.0
    ths_cas = np.linspace(0, 2*np.pi, 160)
    for a_cas in [1.25, 1.48, 1.76]:
        term = c_cas**4 * np.cos(2*ths_cas)**2 + a_cas**4 - c_cas**4
        r_cas = np.sqrt(c_cas**2 * np.cos(2*ths_cas) + np.sqrt(term))
        x_c_out = scale_x * r_cas * np.cos(ths_cas)
        y_c_out = scale_y * 0.78 * r_cas * np.sin(ths_cas)
        ax_g.plot(x_c_out, y_c_out, color='#94a3b8', lw=1.3, alpha=0.85, zorder=2)

        # Arrowhead on top branch
        idx_top = 40  # near pi/2
        ax_g.annotate("", xy=(x_c_out[idx_top+1], y_c_out[idx_top+1]),
                      xytext=(x_c_out[idx_top], y_c_out[idx_top]),
                      arrowprops=dict(arrowstyle="-|>", color='#94a3b8', mutation_scale=8, lw=1.3), zorder=3)

    # Save figure
    plt.savefig(output_path, dpi=240, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] Successfully saved: {output_path}")


if __name__ == "__main__":
    create_figure()
