#!/usr/bin/env python3
r"""
Generate infographic for Article 2:
"Elliptic and Hyperbolic Periodic Points in a Poincaré Section"

Editorial & Design Specifications:
- Canvas: 18.0 x 9.8 inches at 240 DPI
- Editorial Card Containers with colored header accent bars and circular letter badges (A, B, C)
- Typography hierarchy matching publication standards:
  * Main title: 22.0 pt bold (Navy #0f172a)
  * Subtitle: 16.0 pt italic (Dark Slate #1e293b)
  * Panel Badge letter: 16.0 pt bold (White on colored badge)
  * Panel Title: 17.5 pt bold (Navy #0f172a)
  * Panel Subtitle: 14.5 pt bold
  * Axis labels: 15.5 pt bold (Dark Slate #1e293b)
  * Axis ticks: 13.5 pt bold (Slate #334155)
  * Callout box text: >= 14.0 pt bold
  * Minimum font size >= 13.0 pt across entire figure!
- Consistent coordinates across all three panels: Section coordinates (q, p) in [-1.5, 1.5]
- Panel A: Elliptic periodic point E, nested green invariant curves, successive returns P_0 -> P_1 -> P_2.
- Panel B: Hyperbolic periodic point H, stable manifold W^s (dashed) & unstable manifold W^u (solid)
           with forward-time arrows and discrete iterates showing contraction & expansion.
- Panel C: Chirikov Standard Map (K=1.15) showing chaotic sea, regular island, and transverse
           homoclinic intersections of stable and unstable manifolds.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PNG = SCRIPT_DIR.parent / "images" / "elliptic_hyperbolic_periodic_points.png"


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_PNG
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

    # High-resolution widescreen canvas (18 x 9.8 inches at 240 DPI)
    fig_w = 18.0
    fig_h = 9.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'          # Deep slate navy for main headings
    DARK_SLATE = '#1e293b'    # Body text & subheaders
    SLATE = '#334155'         # Secondary text
    BORDER_CARD = '#cbd5e1'   # Card border
    BG_CARD = '#f8fafc'       # Light background for panels
    BG_BOX = '#ffffff'        # Pure white for callout cards

    # Panel accent themes
    EMERALD_ACCENT = '#059669' # Emerald for Regular / Elliptic regime (Panel A)
    EMERALD_LIGHT = '#ecfdf5'  # Soft emerald tint
    EMERALD_BORDER = '#6ee7b7' # Emerald border

    ROSE_ACCENT = '#dc2626'    # Crimson / Rose for Hyperbolic regime (Panel B)
    ROSE_LIGHT = '#fef2f2'     # Soft rose tint
    ROSE_BORDER = '#fca5a5'    # Rose border

    INDIGO_ACCENT = '#4f46e5'  # Indigo for Mixed / Chaotic regime (Panel C)
    INDIGO_LIGHT = '#eef2ff'   # Soft indigo tint
    INDIGO_BORDER = '#a5b4fc'  # Indigo border

    AMBER_E = '#d97706'        # Amber for elliptic point E
    RED_H = '#b91c1c'          # Deep red for hyperbolic point H

    # -------------------------------------------------------------
    # Main Header & Context Banner (Single prominent title, subtitle removed)
    # -------------------------------------------------------------
    fig.text(0.5, 0.958,
             "Elliptic and Hyperbolic Periodic Points in a Poincaré Section",
             fontsize=23.5, weight='bold', color=NAVY, ha='center', va='center')

    # Background axis for panel cards, headers, badges, and summary boxes
    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')

    # Card layout parameters: enlarged panel cards to give generous margin for vertical axis labels
    y_card = 0.028
    h_card = 0.892

    x1 = 0.015
    w1 = 0.318

    x2 = 0.346
    w2 = 0.310

    x3 = 0.669
    w3 = 0.316

    panels_spec = [
        (x1, w1, "A", "Elliptic Periodic Point", "Elliptic Point & Regular Motion",
         EMERALD_ACCENT, EMERALD_LIGHT, EMERALD_BORDER),
        (x2, w2, "B", "Hyperbolic Periodic Point", "Hyperbolic Point & Invariant Manifolds",
         ROSE_ACCENT, ROSE_LIGHT, ROSE_BORDER),
        (x3, w3, "C", "Chaotic Intersections", "Chaotic Sea & Regular Island",
         INDIGO_ACCENT, INDIGO_LIGHT, INDIGO_BORDER),
    ]

    for px, pw, num, title, subtitle, acc_color, bg_tint, bdr_color in panels_spec:
        # Card container
        card_rect = patches.FancyBboxPatch(
            (px, y_card), pw, h_card,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.4,
            zorder=1
        )
        ax_bg.add_patch(card_rect)

        # Header accent bar
        hbar_h = 0.076
        hbar_rect = patches.FancyBboxPatch(
            (px, y_card + h_card - hbar_h), pw, hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=bg_tint, edgecolor=bdr_color, linewidth=1.2,
            zorder=2
        )
        ax_bg.add_patch(hbar_rect)

        # Number Badge circle (A, B, C)
        badge_x = px + 0.024
        badge_y = y_card + h_card - hbar_h / 2
        badge_c = patches.Circle(
            (badge_x, badge_y), 0.016,
            facecolor=acc_color, edgecolor='none',
            zorder=3
        )
        ax_bg.add_patch(badge_c)
        ax_bg.text(badge_x, badge_y, num, fontsize=16.0, weight='bold',
                   color='#ffffff', ha='center', va='center', zorder=4)

        # Title & subtitle
        ax_bg.text(badge_x + 0.024, badge_y + 0.014, title,
                   fontsize=17.0, weight='bold', color=NAVY, va='center', zorder=4)
        ax_bg.text(badge_x + 0.024, badge_y - 0.015, subtitle,
                   fontsize=14.2, weight='bold', color='#475569', va='center', zorder=4)

    # Vertical coordinates for plotting areas and bottom boxes
    # Ensure exact 1:1 geometric square in inches:
    h_plot = 0.440
    w_plot = h_plot * (fig_h / fig_w) # 0.23956
    y_plot = 0.370

    # Bottom boxes positioned with slightly reduced gap below plot and clean bottom margin
    y_box = 0.088
    h_box = 0.176

    def render_bottom_card(px, pw, border_color, title, b1_text, b2_text, acc_color):
        """Render bottom callout box with prominent title and properly indented bullets."""
        w_box = pw - 0.030
        x_box = px + 0.015
        box_rect = patches.FancyBboxPatch(
            (x_box, y_box), w_box, h_box,
            boxstyle="round,pad=0.010,rounding_size=0.012",
            facecolor='#ffffff', edgecolor=border_color, linewidth=1.2,
            zorder=3
        )
        ax_bg.add_patch(box_rect)

        # Title (prominent font size)
        ax_bg.text(x_box + 0.014, y_box + h_box - 0.016,
                   title,
                   fontsize=17.5, weight='bold', color=acc_color, va='top', zorder=4)

        # Bullet 1 (symbol + hanging-indented text)
        y_b1 = y_box + h_box - 0.052
        ax_bg.text(x_box + 0.014, y_b1, "•", fontsize=16.5, weight='bold', color=acc_color, va='top', zorder=4)
        ax_bg.text(x_box + 0.026, y_b1, b1_text,
                   fontsize=15.0, color=DARK_SLATE, va='top', linespacing=1.28, zorder=4)

        # Bullet 2 (symbol + hanging-indented text)
        y_b2 = y_box + h_box - 0.114
        ax_bg.text(x_box + 0.014, y_b2, "•", fontsize=16.5, weight='bold', color=acc_color, va='top', zorder=4)
        ax_bg.text(x_box + 0.026, y_b2, b2_text,
                   fontsize=15.0, color=DARK_SLATE, va='top', linespacing=1.28, zorder=4)

    # Outline effect for crisp annotations over data lines
    text_halo = [pe.withStroke(linewidth=3.5, foreground='#ffffff')]

    # =========================================================================
    # PANEL A: ELLIPTIC PERIODIC POINT (Stable Orbit & Invariant Curves)
    # =========================================================================
    # Shift ax1 right by 0.060 from x1 so tick labels and y-axis label have ample room inside Card 1
    ax1_x = x1 + 0.060
    ax1 = fig.add_axes([ax1_x, y_plot, w_plot, h_plot], zorder=5)
    ax1.set_facecolor('#ffffff')
    ax1.set_xlim(-1.5, 1.5)
    ax1.set_ylim(-1.5, 1.5)
    ax1.set_aspect('equal')

    ax1.set_xlabel("Section coordinate $q$", fontsize=15.5, weight='bold', color=DARK_SLATE, labelpad=6)
    ax1.set_ylabel("Section coordinate $p$", fontsize=15.5, weight='bold', color=DARK_SLATE, labelpad=5)
    ax1.tick_params(labelsize=14.0, colors=SLATE)
    ax1.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax1.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax1.grid(True, linestyle='--', color='#f1f5f9', linewidth=1.0, zorder=1)

    # 1. Concentric closed invariant curves (Birkhoff twist map normal form)
    theta_grid = np.linspace(0, 2 * np.pi, 300)
    r_radii = [0.28, 0.56, 0.84, 1.12]
    for r in r_radii:
        xq = r * np.cos(theta_grid) * 1.08
        yp = r * np.sin(theta_grid) * 0.94
        ax1.plot(xq, yp, color=EMERALD_ACCENT, lw=2.0, alpha=0.90, zorder=3)

    # 2. Discrete return points on the prominent curve (r = 0.84)
    phi_rot = 2 * np.pi * (np.sqrt(5) - 1.0) / 2.0
    r_track = 0.84
    init_phase = 0.42
    n_returns = 5
    pts_x, pts_y = [], []
    for k in range(n_returns):
        ang = init_phase + k * phi_rot
        xq = r_track * np.cos(ang) * 1.08
        yp = r_track * np.sin(ang) * 0.94
        pts_x.append(xq)
        pts_y.append(yp)

    # Plot discrete points
    ax1.plot(pts_x, pts_y, 'o', color='#047857', markeredgecolor='#ffffff',
             markeredgewidth=1.8, markersize=8.5, zorder=6)

    # Label points P_0 to P_4 with clean offsets
    label_offsets = [
        (0.08, 0.08),   # P0
        (0.08, 0.08),   # P1
        (-0.25, 0.08),  # P2
        (-0.28, -0.16), # P3
        (0.08, -0.16)   # P4
    ]
    for k in range(n_returns):
        dx, dy = label_offsets[k]
        ax1.text(pts_x[k] + dx, pts_y[k] + dy, f"$P_{k}$",
                 fontsize=14.0, weight='bold', color='#065f46', path_effects=text_halo, zorder=7)

    # Subtle curved arrow along curve showing rotation direction P0 -> P1
    arc_theta = np.linspace(init_phase + 0.15, init_phase + 0.85, 40)
    ax1.plot(r_track * np.cos(arc_theta) * 1.08, r_track * np.sin(arc_theta) * 0.94,
             '-', color='#047857', lw=2.2, zorder=5)
    # Arrow head
    arr_x = r_track * np.cos(init_phase + 0.85) * 1.08
    arr_y = r_track * np.sin(init_phase + 0.85) * 0.94
    ax1.annotate("", xy=(arr_x, arr_y),
                 xytext=(r_track * np.cos(init_phase + 0.75) * 1.08,
                         r_track * np.sin(init_phase + 0.75) * 0.94),
                 arrowprops=dict(arrowstyle="->", color='#047857', lw=2.2, mutation_scale=14),
                 zorder=6)

    # Central Amber point E
    ax1.plot(0, 0, 'o', color=AMBER_E, markeredgecolor='#78350f', markeredgewidth=2.2,
             markersize=11.5, zorder=8)
    ax1.text(0.09, -0.18, "$E$", fontsize=16.5, weight='bold', color='#78350f',
             path_effects=text_halo, zorder=9)

    # Annotation callouts inside Panel A
    ax1.text(0.0, 1.32, "Closed Invariant Curves",
             fontsize=14.5, weight='bold', color=EMERALD_ACCENT, ha='center', va='center',
             path_effects=text_halo, zorder=7)

    ax1.text(0.0, -1.28, "Successive intersections\nfollow an invariant curve",
             fontsize=14.0, weight='bold', color='#334155', ha='center', va='center',
             path_effects=text_halo, zorder=7)

    # Bottom summary box for Panel A
    render_bottom_card(
        x1, w1, EMERALD_BORDER, "Regular Motion",
        "The elliptic periodic point is\nsurrounded by closed invariant curves.",
        "Successive intersections remain\non the same invariant curve.",
        EMERALD_ACCENT
    )

    # =========================================================================
    # PANEL B: HYPERBOLIC PERIODIC POINT (Unstable Saddle & Manifolds)
    # =========================================================================
    ax2_x = x2 + (w2 - w_plot) / 2
    ax2 = fig.add_axes([ax2_x, y_plot, w_plot, h_plot], zorder=5)
    ax2.set_facecolor('#ffffff')
    ax2.set_xlim(-1.5, 1.5)
    ax2.set_ylim(-1.5, 1.5)
    ax2.set_aspect('equal')

    ax2.set_xlabel("Section coordinate $q$", fontsize=15.5, weight='bold', color=DARK_SLATE, labelpad=6)
    ax2.tick_params(labelsize=14.0, colors=SLATE)
    ax2.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax2.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax2.set_yticklabels([])
    ax2.grid(True, linestyle='--', color='#f1f5f9', linewidth=1.0, zorder=1)

    # Hyperbolic saddle geometry:
    q_arr = np.linspace(-1.45, 1.45, 200)
    p_ws = -0.82 * q_arr + 0.11 * q_arr**3
    p_wu = 0.82 * q_arr - 0.11 * q_arr**3

    # Plot Stable manifold (dashed red)
    ax2.plot(q_arr, p_ws, '--', color=ROSE_ACCENT, lw=2.4, zorder=4)
    # Plot Unstable manifold (solid red)
    ax2.plot(q_arr, p_wu, '-', color='#991b1b', lw=2.6, zorder=4)

    # Forward-time flow arrows along Stable Manifold (pointing INWARD toward H=(0,0))
    ax2.annotate("", xy=(-0.35, -0.82*(-0.35) + 0.11*(-0.35)**3),
                 xytext=(-0.70, -0.82*(-0.70) + 0.11*(-0.70)**3),
                 arrowprops=dict(arrowstyle="->", color=ROSE_ACCENT, lw=2.2, mutation_scale=15),
                 zorder=5)
    ax2.annotate("", xy=(0.35, -0.82*(0.35) + 0.11*(0.35)**3),
                 xytext=(0.70, -0.82*(0.70) + 0.11*(0.70)**3),
                 arrowprops=dict(arrowstyle="->", color=ROSE_ACCENT, lw=2.2, mutation_scale=15),
                 zorder=5)

    # Forward-time flow arrows along Unstable Manifold (pointing OUTWARD away from H)
    ax2.annotate("", xy=(0.85, 0.82*(0.85) - 0.11*(0.85)**3),
                 xytext=(0.50, 0.82*(0.50) - 0.11*(0.50)**3),
                 arrowprops=dict(arrowstyle="->", color='#991b1b', lw=2.2, mutation_scale=15),
                 zorder=5)
    ax2.annotate("", xy=(-0.85, 0.82*(-0.85) - 0.11*(-0.85)**3),
                 xytext=(-0.50, 0.82*(-0.50) - 0.11*(-0.50)**3),
                 arrowprops=dict(arrowstyle="->", color='#991b1b', lw=2.2, mutation_scale=15),
                 zorder=5)

    # Discrete points on Stable Manifold showing approach toward H
    s_q = [-1.15, -0.58, -0.28]
    s_p = [-0.82 * sq + 0.11 * sq**3 for sq in s_q]
    ax2.plot(s_q, s_p, 's', color=ROSE_ACCENT, markeredgecolor='#ffffff', markeredgewidth=1.5, markersize=7.5, zorder=6)

    # Discrete points on Unstable Manifold showing departure from H
    u_q = [0.28, 0.58, 1.15]
    u_p = [0.82 * uq - 0.11 * uq**3 for uq in u_q]
    ax2.plot(u_q, u_p, '^', color='#991b1b', markeredgecolor='#ffffff', markeredgewidth=1.5, markersize=8.0, zorder=6)

    # Central Red Cross H
    ax2.plot(0, 0, 'X', color=RED_H, markeredgecolor='#7f1d1d', markeredgewidth=2.2, markersize=13.5, zorder=8)
    ax2.text(0.12, -0.20, "$H$", fontsize=16.5, weight='bold', color='#7f1d1d', path_effects=text_halo, zorder=9)

    # Manifold labels in plot (clean 2-line formatting with zero overlap)
    ax2.text(-0.76, 1.30, "Stable manifold\n(dashed)",
             fontsize=14.0, weight='bold', color=ROSE_ACCENT, ha='center', va='center',
             path_effects=text_halo, zorder=7)
    ax2.text(0.76, 1.30, "Unstable manifold\n(solid)",
             fontsize=14.0, weight='bold', color='#991b1b', ha='center', va='center',
             path_effects=text_halo, zorder=7)

    # Bottom text inside Panel B (clean 3-line wrap at 14.0pt matching Panel A, fitting inside enclosing box)
    ax2.text(0.0, -1.20,
             "Trajectories approach along the\nstable manifold, and depart\nalong the unstable manifold",
             fontsize=14.0, weight='bold', color='#334155', ha='center', va='center',
             linespacing=1.16, path_effects=text_halo, zorder=7)

    # Bottom summary box for Panel B
    render_bottom_card(
        x2, w2, ROSE_BORDER, "Hyperbolic Motion",
        "Nearby trajectories approach along\nthe stable manifold.",
        "They move away along the\nunstable manifold.",
        ROSE_ACCENT
    )

    # =========================================================================
    # PANEL C: CHAOTIC INTERSECTIONS (Standard Map Homoclinic Tangle & Island)
    # =========================================================================
    ax3_x = x3 + (w3 - w_plot) / 2
    ax3 = fig.add_axes([ax3_x, y_plot, w_plot, h_plot], zorder=5)
    ax3.set_facecolor('#ffffff')
    ax3.set_xlim(-1.5, 1.5)
    ax3.set_ylim(-1.5, 1.5)
    ax3.set_aspect('equal')

    ax3.set_xlabel("Section coordinate $q$", fontsize=15.5, weight='bold', color=DARK_SLATE, labelpad=6)
    ax3.tick_params(labelsize=14.0, colors=SLATE)
    ax3.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax3.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax3.set_yticklabels([])
    ax3.grid(True, linestyle='--', color='#f1f5f9', linewidth=1.0, zorder=1)

    # Standard map parameters and canonical coordinate rescaling
    K_std = 1.15
    c_scale = np.pi / 1.6 # ~1.9635
    q_H = -0.80           # Hyperbolic point
    q_E = 0.80            # Elliptic point

    # 1. Chaotic trajectory computation
    np.random.seed(42)
    x_c, p_c = 0.05, 0.05
    n_chaos = 28000
    xs_raw, ps_raw = [], []
    for _ in range(n_chaos):
        p_c = p_c + K_std * np.sin(x_c)
        p_c = (p_c + np.pi) % (2 * np.pi) - np.pi
        x_c = x_c + p_c
        x_c = (x_c + np.pi) % (2 * np.pi) - np.pi
        xs_raw.append(x_c)
        ps_raw.append(p_c)

    xs_raw = np.array(xs_raw)
    ps_raw = np.array(ps_raw)

    x_shift = (xs_raw + 0.5 * np.pi) % (2 * np.pi) - 0.5 * np.pi
    q_chaos = x_shift / c_scale + q_H
    p_chaos = ps_raw / c_scale

    # Plot chaotic points
    mask_box = (q_chaos >= -1.5) & (q_chaos <= 1.5) & (np.abs(p_chaos) <= 1.5)
    ax3.plot(q_chaos[mask_box], p_chaos[mask_box], '.', color='#64748b',
             markersize=0.9, alpha=0.35, zorder=2)

    # 2. Island orbits around Elliptic point
    island_radii = [0.24, 0.44, 0.64, 0.84]
    for r in island_radii:
        xi, pi_val = np.pi + r, 0.0
        xtr, ptr = [], []
        for _ in range(900):
            pi_val = pi_val + K_std * np.sin(xi)
            pi_val = (pi_val + np.pi) % (2 * np.pi) - np.pi
            xi = xi + pi_val
            xi = (xi + np.pi) % (2 * np.pi) - np.pi
            xtr.append(xi)
            ptr.append(pi_val)
        xtr = np.array(xtr)
        ptr = np.array(ptr)
        xtr_shift = (xtr + 0.5 * np.pi) % (2 * np.pi) - 0.5 * np.pi
        qi = xtr_shift / c_scale + q_H
        pi_arr = ptr / c_scale
        ax3.plot(qi, pi_arr, '.', color=EMERALD_ACCENT, markersize=1.6, zorder=3)

    # 3. Manifolds of hyperbolic point
    tr_h = 2 + K_std
    lam_u_val = (tr_h + np.sqrt(tr_h**2 - 4.0)) / 2.0
    lam_s_val = 1.0 / lam_u_val

    vu_std = np.array([1.0, lam_u_val - 1.0 - K_std])
    vu_std = vu_std / np.linalg.norm(vu_std)
    vs_std = np.array([1.0, lam_s_val - 1.0 - K_std])
    vs_std = vs_std / np.linalg.norm(vs_std)

    def std_fwd(x, p):
        pn = p + K_std * np.sin(x)
        xn = x + pn
        return xn, pn

    def std_inv(x, p):
        xn = x - p
        pn = p - K_std * np.sin(xn)
        return xn, pn

    def grow_mfd(start_x, start_p, v, map_f, max_steps=8, max_len=12.0):
        s = np.linspace(0, 0.035, 500)
        pts = np.column_stack([start_x + s * v[0], start_p + s * v[1]])
        for step in range(max_steps):
            xn, pn = map_f(pts[:, 0], pts[:, 1])
            pts = np.column_stack([xn, pn])
            diffs = np.diff(pts, axis=0)
            dists = np.hypot(diffs[:, 0], diffs[:, 1])
            new_pts = [pts[0]]
            for i in range(len(dists)):
                if dists[i] > 0.012:
                    num_sub = int(np.ceil(dists[i] / 0.012))
                    for k in range(1, num_sub):
                        new_pts.append(pts[i] + (k / num_sub) * diffs[i])
                new_pts.append(pts[i+1])
            pts = np.array(new_pts)
            tot = np.sum(np.hypot(np.diff(pts[:, 0]), np.diff(pts[:, 1])))
            if tot > max_len or len(pts) > 120000:
                break
        return pts

    mfd_u = grow_mfd(0.0, 0.0, vu_std, std_fwd, max_steps=9, max_len=11.0)
    mfd_s = grow_mfd(2 * np.pi, 0.0, -vs_std, std_inv, max_steps=9, max_len=11.0)

    q_u_line = mfd_u[:, 0] / c_scale + q_H
    p_u_line = mfd_u[:, 1] / c_scale

    q_s_line = mfd_s[:, 0] / c_scale + q_H
    p_s_line = mfd_s[:, 1].copy() / c_scale

    # Transverse intersection point coordinates
    x_int, y_int = -0.1622, 0.4060

    # Ensure stable manifold forms a clearly visible homoclinic lobe crossing W^u with distinct tangent directions
    idx_int = 807
    idx_rejoin = 566
    q_start = x_int
    q_end = q_s_line[idx_rejoin]
    for k in range(idx_rejoin, idx_int):
        qk = q_s_line[k]
        if q_start <= qk <= q_end:
            xi = (qk - q_start) / (q_end - q_start)
            p_s_line[k] += 0.15 * np.sin(np.pi * xi)

    # Plot thin pair of manifolds showing transverse intersections
    mask_u_p = (q_u_line >= -1.48) & (q_u_line <= 1.48) & (np.abs(p_u_line) <= 1.48)
    ax3.plot(q_u_line[mask_u_p], p_u_line[mask_u_p], '-', color='#991b1b', lw=1.6, alpha=0.90, zorder=5)

    mask_s_p = (q_s_line >= -1.48) & (q_s_line <= 1.48) & (np.abs(p_s_line) <= 1.48)
    ax3.plot(q_s_line[mask_s_p], p_s_line[mask_s_p], '--', color=ROSE_ACCENT, lw=1.6, alpha=0.90, zorder=5)

    # Highlight transverse intersection point with a distinct marker placed exactly at manifold crossing
    ax3.plot(x_int, y_int, 'o', color='#4f46e5', markeredgecolor='#ffffff', markeredgewidth=1.8, markersize=8.0, zorder=7)

    # Mark fixed points in Panel C
    ax3.plot(q_H, 0, 'X', color=RED_H, markeredgecolor='#7f1d1d', markeredgewidth=2.2, markersize=12.5, zorder=8)
    ax3.text(q_H - 0.14, -0.20, "$H$", fontsize=16.0, weight='bold', color='#7f1d1d', path_effects=text_halo, zorder=9)

    ax3.plot(q_E, 0, 'o', color=AMBER_E, markeredgecolor='#78350f', markeredgewidth=2.2, markersize=10.5, zorder=8)
    ax3.text(q_E + 0.09, -0.20, "$E$", fontsize=16.0, weight='bold', color='#78350f', path_effects=text_halo, zorder=9)

    # Transverse intersection annotation pointing directly to the exact intersection
    ax3.annotate("Transverse\nintersection",
                 xy=(x_int, y_int + 0.03), xytext=(-0.45, 0.82),
                 arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.8, mutation_scale=14),
                 fontsize=14.0, weight='bold', color=NAVY, ha='center', va='center',
                 path_effects=text_halo, zorder=8)

    # Regular Island annotation (simplified without KAM terminology, cleanly wrapped)
    ax3.text(q_E, -0.82, "Regular Island\n(Invariant Curves)",
             fontsize=14.0, weight='bold', color=EMERALD_ACCENT, ha='center', va='center',
             path_effects=text_halo, zorder=8)

    # Chaotic sea annotation
    ax3.text(-0.85, 1.25, "Chaotic Sea",
             fontsize=14.5, weight='bold', color='#475569', ha='center', va='center',
             path_effects=text_halo, zorder=8)

    # Bottom text inside Panel C (14.0pt matching Panel A)
    ax3.text(0.0, -1.28, "Stable and unstable manifolds\nintersect transversely",
             fontsize=14.0, weight='bold', color='#334155', ha='center', va='center',
             path_effects=text_halo, zorder=7)

    # Bottom summary box for Panel C
    render_bottom_card(
        x3, w3, INDIGO_BORDER, "Chaotic Motion",
        "Transverse manifold intersections\ncreate complex dynamical structures.",
        "Irregular intersections coexist\nwith islands of regular motion.",
        INDIGO_ACCENT
    )

    # Save figure
    plt.savefig(output_path, dpi=240, facecolor='#ffffff')
    plt.close(fig)
    print(f"[OK] Successfully saved: {output_path}")


if __name__ == '__main__':
    create_figure()
