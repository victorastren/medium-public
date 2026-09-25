#!/usr/bin/env python3
"""
Generate infographic:
"From Continuous Flow to a Poincaré Return Map"
Two-panel conceptual diagram illustrating Poincaré's reduction of dynamics:
- Left Panel: Continuous flow in state space repeatedly crossing a transverse section Sigma.
- Right Panel: Discrete return map on Sigma connecting successive intersections,
              including an inset showing a periodic orbit as a fixed point P(x_*) = x_*.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scipy.interpolate import CubicSpline

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "poincare_return_map.png"


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # EDITORIAL DESIGN SYSTEM & PALETTE
    # -------------------------------------------------------------
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#334155'
    LIGHT_SLATE = '#94a3b8'
    BORDER_COLOR = '#cbd5e1'
    CARD_BG = '#f8fafc'
    PLOT_BG = '#ffffff'

    BLUE = '#2563eb'
    BLUE_DARK = '#1d4ed8'
    BLUE_LIGHT = '#93c5fd'
    TEAL = '#0f766e'
    TEAL_DARK = '#0f766e'
    CRIMSON = '#e11d48'
    PURPLE = '#7c3aed'
    PURPLE_DARK = '#6d28d9'

    PLANE_FACE = '#e0f2fe'
    PLANE_EDGE = '#0284c7'
    GRID_COLOR = '#bae6fd'

    PILL_BG_BLUE = '#dbeafe'
    PILL_BORDER_BLUE = '#60a5fa'
    PILL_TEXT_BLUE = '#1e3a8a'

    PILL_BG_PURPLE = '#ede9fe'
    PILL_BORDER_PURPLE = '#a78bfa'
    PILL_TEXT_PURPLE = '#5b21b6'

    # -------------------------------------------------------------
    # FIGURE CANVAS & TOP HEADER
    # -------------------------------------------------------------
    fig_w = 17.6
    fig_h = 9.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Top Title Badge
    fig.text(0.5, 0.956,
             "From Continuous Flow to a Poincaré Return Map",
             fontsize=21.0, weight='bold', color=NAVY, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.30",
                       facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1.4))

    # Editorial Subtitle
    fig.text(0.5, 0.890,
             "A Poincaré map reduces a continuous flow to successive intersections with a transverse section.",
             fontsize=16.0, weight='bold', color=NAVY, ha='center', va='center')

    # -------------------------------------------------------------
    # CARD CONTAINERS (Side-by-side with central transition bridge)
    # -------------------------------------------------------------
    card_w_in = 7.55
    card_h_in = 7.70
    gap_x_in = 1.80
    bottom_y_in = 0.44

    card_w = card_w_in / fig_w
    card_h = card_h_in / fig_h
    gap_x = gap_x_in / fig_w
    bottom_y = bottom_y_in / fig_h

    left_m = (1.0 - (2 * card_w + gap_x)) / 2.0
    x1 = left_m
    x2 = x1 + card_w + gap_x

    ax1_bg = fig.add_axes([x1, bottom_y, card_w, card_h])
    ax2_bg = fig.add_axes([x2, bottom_y, card_w, card_h])

    for ax in [ax1_bg, ax2_bg]:
        ax.set_facecolor(CARD_BG)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        card_patch = patches.FancyBboxPatch((0.005, 0.005), 0.99, 0.99,
                                            boxstyle="round,pad=0.01,rounding_size=0.04",
                                            facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1.4, zorder=0)
        ax.add_patch(card_patch)

    # Card 1 Header & Metadata
    ax1_bg.text(0.050, 0.940, "Continuous Flow in State Space", fontsize=18.0, weight='bold', color=NAVY, va='center')
    ax1_bg.text(0.950, 0.940, "Continuous", fontsize=14.5, weight='bold', color=PILL_TEXT_BLUE,
                ha='right', va='center',
                bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.25",
                          facecolor=PILL_BG_BLUE, edgecolor=PILL_BORDER_BLUE, lw=1.3))
    ax1_bg.text(0.050, 0.872, r"One continuous trajectory crossing transverse section $\Sigma$",
                fontsize=14.2, weight='bold', color=SLATE, va='center')

    # Card 2 Header & Metadata
    ax2_bg.text(0.050, 0.940, r"Discrete Return Map on $\Sigma$", fontsize=18.0, weight='bold', color=NAVY, va='center')
    ax2_bg.text(0.950, 0.940, "Discrete", fontsize=14.5, weight='bold', color=PILL_TEXT_PURPLE,
                ha='right', va='center',
                bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.25",
                          facecolor=PILL_BG_PURPLE, edgecolor=PILL_BORDER_PURPLE, lw=1.3))
    ax2_bg.text(0.050, 0.872, r"Successive intersections:   $P:\mathbf{x}_n \mapsto \mathbf{x}_{n+1}$",
                fontsize=17.5, weight='bold', color=SLATE, va='center')

    # Subplot Geometry inside Cards (taller plot, snug bottom gap)
    plot_w_in = 5.80
    plot_h_in = 5.25
    plot_w = plot_w_in / fig_w
    plot_h = plot_h_in / fig_h

    plot_pad_left_in = (card_w_in - plot_w_in) / 2.0
    plot_pad_left = plot_pad_left_in / fig_w
    plot_pad_bottom = 0.095 * card_h

    sub1_x = x1 + plot_pad_left
    sub1_y = bottom_y + plot_pad_bottom
    sub2_x = x2 + plot_pad_left
    sub2_y = bottom_y + plot_pad_bottom

    ax1 = fig.add_axes([sub1_x, sub1_y, plot_w, plot_h])
    ax2 = fig.add_axes([sub2_x, sub2_y, plot_w, plot_h])

    for ax in [ax1, ax2]:
        ax.set_facecolor(PLOT_BG)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(BORDER_COLOR)
            spine.set_linewidth(1.3)

    # Bottom Annotations inside Cards (gap minimized directly under inner plot)
    ax1_bg.text(0.5, 0.046, r"Record each crossing of the section $\Sigma$",
                fontsize=16.5, weight='bold', color=NAVY, ha='center', va='center')
    ax2_bg.text(0.5, 0.046, r"Successive states under the return map:   $\mathbf{x}_0 \to \mathbf{x}_1 \to \mathbf{x}_2 \to \mathbf{x}_3$",
                fontsize=16.5, weight='bold', color=NAVY, ha='center', va='center')

    # Central Bridge between Cards
    mid_x = (x1 + card_w + x2) / 2.0
    plot_center_y = sub1_y + plot_h / 2.0
    mid_y_arr = plot_center_y
    mid_y_box = plot_center_y + 0.12

    fig.text(mid_x, mid_y_box, "Sample at successive\ncrossings",
             ha="center", va="center", fontsize=13.5, weight='bold', color=NAVY,
             linespacing=1.30,
             bbox=dict(boxstyle="round,pad=0.40,rounding_size=0.25", facecolor="#ffffff", edgecolor=BORDER_COLOR, lw=1.4))
    fig.text(mid_x, mid_y_arr, r"$\longrightarrow$", ha="center", va="center", fontsize=34, color=DARK_SLATE)

    # -------------------------------------------------------------
    # 3D CAMERA PROJECTION ENGINE
    # -------------------------------------------------------------
    elev_deg = 26
    azim_deg = -40
    elev = np.radians(elev_deg)
    azim = np.radians(azim_deg)

    def project_3d(pts):
        """Axonometric perspective projection from (x, y, z) into (u, v, depth)."""
        Rz = np.array([
            [np.cos(azim), -np.sin(azim), 0],
            [np.sin(azim),  np.cos(azim), 0],
            [0,             0,            1]
        ])
        Rx = np.array([
            [1, 0,             0],
            [0, np.cos(elev), -np.sin(elev)],
            [0, np.sin(elev),  np.cos(elev)]
        ])
        R = Rx @ Rz
        p = pts @ R.T
        return p[..., 0], p[..., 2], p[..., 1]

    # Section Sigma dimensions: plane at z = 0, bounded by [-1.5, 1.5] x [-1.2, 1.2]
    plane_3d = np.array([
        [-1.5, -1.2, 0.0],
        [ 1.5, -1.2, 0.0],
        [ 1.5,  1.2, 0.0],
        [-1.5,  1.2, 0.0]
    ])

    # 4 Crossing points on Sigma (z = 0)
    # Perfectly separated both in 3D projection and in 2D face-on view
    crossings_3d = [
        np.array([-0.95, -0.55, 0.0]),  # x0
        np.array([-0.55,  0.45, 0.0]),  # x1
        np.array([ 0.05,  0.70, 0.0]),  # x2
        np.array([ 0.65,  0.40, 0.0])   # x3
    ]

    # -------------------------------------------------------------
    # 3D TRAJECTORY: SINGLE CONTINUOUS FLOW
    # -------------------------------------------------------------
    # Spline control points: leaves x_k with dz/dt > 0, arches in +z,
    # sweeps around the side outside Sigma, returns underneath in -z,
    # and pierces transversely at x_{k+1} with dz/dt > 0!
    ctrl = []

    # Pre-lead entering x0 from underneath
    ctrl.append(crossings_3d[0] + np.array([-0.25, -0.22, -0.65]))
    ctrl.append(crossings_3d[0] + np.array([-0.08, -0.07, -0.20]))
    ctrl.append(crossings_3d[0])

    # Arch 0: x0 -> x1
    ctrl.append(crossings_3d[0] + np.array([0.05, 0.20, 1.05]))
    ctrl.append(np.array([-0.80, 0.00, 1.30]))
    ctrl.append(np.array([-0.65, 0.80, 0.90]))
    ctrl.append(np.array([-0.35, 1.35, 0.00]))   # outside top edge
    ctrl.append(np.array([-0.40, 1.20, -0.70]))  # under plane
    ctrl.append(crossings_3d[1] + np.array([-0.08, -0.08, -0.55]))
    ctrl.append(crossings_3d[1])

    # Arch 1: x1 -> x2
    ctrl.append(crossings_3d[1] + np.array([0.10, 0.15, 1.05]))
    ctrl.append(np.array([-0.20, 0.70, 1.35]))
    ctrl.append(np.array([ 0.35, 0.95, 0.90]))
    ctrl.append(np.array([ 0.85, 1.35, 0.00]))   # outside top-right edge
    ctrl.append(np.array([ 0.65, 1.15, -0.70]))  # under plane
    ctrl.append(crossings_3d[2] + np.array([-0.06, -0.05, -0.55]))
    ctrl.append(crossings_3d[2])

    # Arch 2: x2 -> x3
    ctrl.append(crossings_3d[2] + np.array([0.15, 0.02, 1.05]))
    ctrl.append(np.array([ 0.50, 0.45, 1.25]))
    ctrl.append(np.array([ 1.05, 0.15, 0.85]))
    ctrl.append(np.array([ 1.45, -0.15, 0.00]))  # outside right edge
    ctrl.append(np.array([ 1.25, -0.50, -0.70])) # under plane
    ctrl.append(crossings_3d[3] + np.array([-0.05, 0.05, -0.55]))
    ctrl.append(crossings_3d[3])

    # Post-lead leaving x3 into space
    ctrl.append(crossings_3d[3] + np.array([0.10, -0.05, 0.85]))
    ctrl.append(crossings_3d[3] + np.array([0.22, -0.10, 1.35]))

    ctrl = np.array(ctrl)
    cs = CubicSpline(np.linspace(0, 1, len(ctrl)), ctrl)
    t_dense = np.linspace(0, 1, 1500)
    dense_pts = cs(t_dense)

    # -------------------------------------------------------------
    # PANEL 1 RENDERING: 3D FLOW ACROSS SECTION SIGMA
    # -------------------------------------------------------------
    ax1.set_xlim(-2.4, 2.4)
    ax1.set_ylim(-2.1, 2.1)

    u_d, v_d, _ = project_3d(dense_pts)
    z_vals = dense_pts[:, 2]

    # Layer 1: Under-plane trajectory segments (z < 0) behind the section
    below_mask = z_vals <= 0.02
    diffs = np.diff(below_mask.astype(int))
    split_idx = np.where(diffs != 0)[0] + 1
    segs = np.split(np.arange(len(dense_pts)), split_idx)

    for s in segs:
        if len(s) < 2:
            continue
        if np.mean(z_vals[s]) < 0:
            ax1.plot(u_d[s], v_d[s], color=BLUE_LIGHT, lw=2.2, linestyle='--', alpha=0.85, zorder=2)

    # Layer 2: Translucent Section Sigma Polygon
    u_pl, v_pl, _ = project_3d(plane_3d)
    plane_poly = patches.Polygon(np.column_stack([u_pl, v_pl]),
                                 closed=True, facecolor=PLANE_FACE, edgecolor=PLANE_EDGE,
                                 lw=2.0, alpha=0.45, zorder=4)
    ax1.add_patch(plane_poly)

    # Subtle internal grid on Sigma
    for gx in np.linspace(-1.5, 1.5, 7):
        gl = np.array([[gx, -1.2, 0.0], [gx, 1.2, 0.0]])
        ug, vg, _ = project_3d(gl)
        ax1.plot(ug, vg, color=GRID_COLOR, lw=0.8, alpha=0.6, zorder=4)
    for gy in np.linspace(-1.2, 1.2, 5):
        gl = np.array([[-1.5, gy, 0.0], [1.5, gy, 0.0]])
        ug, vg, _ = project_3d(gl)
        ax1.plot(ug, vg, color=GRID_COLOR, lw=0.8, alpha=0.6, zorder=4)

    # Watermark Sigma
    u_sig, v_sig, _ = project_3d(np.array([[-1.3, 0.95, 0.0]]))
    ax1.text(u_sig[0], v_sig[0], r"$\Sigma$", fontsize=32.0, weight='bold', color=PLANE_EDGE,
             ha='center', va='center', zorder=5)

    # Layer 3: Above-plane trajectory segments (z >= 0) in front of the section
    for s in segs:
        if len(s) < 2:
            continue
        if np.mean(z_vals[s]) >= 0:
            ax1.plot(u_d[s], v_d[s], color=BLUE_DARK, lw=2.8, alpha=0.95, zorder=6)

            # Directional flow arrows along trajectory
            if len(s) > 150:
                for frac in [0.28, 0.72]:
                    mid_i = s[int(len(s) * frac)]
                    if mid_i + 4 < len(u_d) and mid_i - 4 >= 0:
                        ax1.annotate('', xy=(u_d[mid_i + 4], v_d[mid_i + 4]),
                                     xytext=(u_d[mid_i - 4], v_d[mid_i - 4]),
                                     arrowprops=dict(arrowstyle="->,head_width=0.30,head_length=0.42",
                                                     color=BLUE_DARK, lw=2.0), zorder=7)
            else:
                mid_i = s[len(s) // 2]
                if mid_i + 4 < len(u_d) and mid_i - 4 >= 0:
                    ax1.annotate('', xy=(u_d[mid_i + 4], v_d[mid_i + 4]),
                                 xytext=(u_d[mid_i - 4], v_d[mid_i - 4]),
                                 arrowprops=dict(arrowstyle="->,head_width=0.30,head_length=0.42",
                                                 color=BLUE_DARK, lw=2.0), zorder=7)

    # Layer 4: Crossing Points on Sigma
    crossing_labels = [r"$\mathbf{x}_0$", r"$\mathbf{x}_1$", r"$\mathbf{x}_2$", r"$\mathbf{x}_3$"]
    offsets_3d = [(-0.34, -0.24), (-0.30, 0.30), (0.30, 0.28), (0.34, -0.24)]

    for cp, label, off in zip(crossings_3d, crossing_labels, offsets_3d):
        uc, vc, _ = project_3d(cp.reshape(1, 3))
        ax1.plot(uc[0], vc[0], 'o', color=CRIMSON, markersize=9.5,
                 markeredgecolor='#ffffff', markeredgewidth=2.2, zorder=10)
        ax1.annotate(label, xy=(uc[0], vc[0]), xytext=(uc[0] + off[0], vc[0] + off[1]),
                     fontsize=16.5, weight='bold', color=CRIMSON, ha='center', va='center', zorder=12,
                     bbox=dict(boxstyle="round,pad=0.28,rounding_size=0.2", facecolor="#fff1f2",
                               edgecolor="#fecdd3", alpha=0.96, lw=1.2),
                     arrowprops=dict(arrowstyle="->,head_width=0.24,head_length=0.38", color=CRIMSON, lw=1.4,
                                     shrinkA=3, shrinkB=4))

    # -------------------------------------------------------------
    # PANEL 2 RENDERING: DISCRETE RETURN MAP ON SIGMA
    # -------------------------------------------------------------
    ax2.set_xlim(-1.8, 1.8)
    ax2.set_ylim(-1.5, 1.5)

    # Surface boundary: identical geometry and styling as Sigma in 3D
    rect_sigma = patches.Rectangle((-1.5, -1.2), 3.0, 2.4,
                                   facecolor=PLANE_FACE, edgecolor=PLANE_EDGE, lw=2.0, alpha=0.45, zorder=2)
    ax2.add_patch(rect_sigma)

    # Internal grid matching Sigma
    for gx in np.linspace(-1.5, 1.5, 7):
        ax2.plot([gx, gx], [-1.2, 1.2], color=GRID_COLOR, lw=0.8, alpha=0.6, zorder=3)
    for gy in np.linspace(-1.2, 1.2, 5):
        ax2.plot([-1.5, 1.5], [gy, gy], color=GRID_COLOR, lw=0.8, alpha=0.6, zorder=3)

    # Watermark Sigma
    ax2.text(-1.3, 0.95, r"$\Sigma$", fontsize=34.0, weight='bold', color=PLANE_EDGE,
             ha='center', va='center', zorder=4)

    # 2D coordinates matching the exact 3D crossing points (x, y)
    pts_2d = [c[:2] for c in crossings_3d]

    # Mapping arrows: x0 -> x1 -> x2 -> x3
    for i in range(len(pts_2d) - 1):
        p_start = pts_2d[i]
        p_end = pts_2d[i + 1]

        # Curved connection arrow indicating mapping step P
        rad_curve = -0.14 if i % 2 == 0 else 0.14
        ax2.annotate('', xy=p_end, xytext=p_start,
                     arrowprops=dict(arrowstyle="->,head_width=0.38,head_length=0.55",
                                     color=PURPLE, lw=2.6,
                                     shrinkA=12, shrinkB=12,
                                     connectionstyle=f"arc3,rad={rad_curve}"),
                     zorder=5)

        # Label "P" badge along each mapping step
        mid_pt = 0.5 * (np.array(p_start) + np.array(p_end))
        normal = np.array([-(p_end[1] - p_start[1]), p_end[0] - p_start[0]])
        normal = normal / (np.linalg.norm(normal) + 1e-6)
        label_pos = mid_pt + normal * (0.24 if i % 2 == 0 else -0.24)

        ax2.text(label_pos[0], label_pos[1], r"$P$", fontsize=18.0, weight='bold', color=PURPLE,
                 ha='center', va='center', zorder=6,
                 bbox=dict(boxstyle="circle,pad=0.25", facecolor="#faf5ff", edgecolor="#ddd6fe", lw=1.3))

    # Plot crossing points in 2D
    offsets_2d = [(-0.28, -0.24), (-0.28, 0.24), (0.28, 0.24), (0.28, -0.24)]
    for pt, label, off in zip(pts_2d, crossing_labels, offsets_2d):
        ax2.plot(pt[0], pt[1], 'o', color=CRIMSON, markersize=10.5,
                 markeredgecolor='#ffffff', markeredgewidth=2.4, zorder=8)
        ax2.text(pt[0] + off[0], pt[1] + off[1], label,
                 fontsize=18.0, weight='bold', color=CRIMSON, ha='center', va='center', zorder=9,
                 bbox=dict(boxstyle="round,pad=0.30,rounding_size=0.2", facecolor="#fff1f2",
                           edgecolor="#fecdd3", alpha=0.96, lw=1.3))

    # -------------------------------------------------------------
    # PERIODIC ORBIT INSET (Dedicated Card in Lower Right of Sigma)
    # -------------------------------------------------------------
    inset_x = -0.85
    inset_y = -1.08
    inset_w = 2.26
    inset_h = 0.82

    inset_bg = patches.FancyBboxPatch((inset_x, inset_y), inset_w, inset_h,
                                      boxstyle="round,pad=0.03,rounding_size=0.06",
                                      facecolor='#ffffff', edgecolor='#cbd5e1', lw=1.4, zorder=10)
    ax2.add_patch(inset_bg)

    # Highlighted fixed point x_*
    fp_x = inset_x + 0.38
    fp_y = inset_y + 0.41
    ax2.plot(fp_x, fp_y, 'o', color=TEAL_DARK, markersize=10.5,
             markeredgecolor='#ffffff', markeredgewidth=2.2, zorder=12)

    # Self-returning looped arrow: P(x_*) = x_*
    loop_arc = patches.Arc((fp_x, fp_y + 0.12), 0.22, 0.22, angle=0, theta1=45, theta2=315,
                           color=TEAL_DARK, lw=2.2, zorder=12)
    ax2.add_patch(loop_arc)
    # Arrowhead on loop
    ax2.annotate('', xy=(fp_x + 0.08, fp_y + 0.03), xytext=(fp_x + 0.11, fp_y + 0.07),
                 arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.38", color=TEAL_DARK, lw=2.2),
                 zorder=13)

    # Label x_* with clean inner margin from box left border
    ax2.text(fp_x - 0.10, fp_y, r"$\mathbf{x}_*$", fontsize=17.5, weight='bold', color=TEAL_DARK,
             ha='right', va='center', zorder=14)

    # Inset text description: large prominent math formula (18pt) & cleanly split text
    text_x = fp_x + 0.18
    ax2.text(text_x, fp_y + 0.25, r"If $P(\mathbf{x}_*) = \mathbf{x}_*$:",
             fontsize=18.0, weight='bold', color=TEAL_DARK, ha='left', va='center', zorder=14)
    ax2.text(text_x, fp_y + 0.07, "fixed point of the return map",
             fontsize=11.5, weight='bold', color=SLATE, ha='left', va='center', zorder=14)
    ax2.text(text_x, fp_y - 0.09, "corresponding to a",
             fontsize=11.5, weight='bold', color=SLATE, ha='left', va='center', zorder=14)
    ax2.text(text_x, fp_y - 0.23, "periodic orbit",
             fontsize=11.5, weight='bold', color=SLATE, ha='left', va='center', zorder=14)

    fig.savefig(output_path, dpi=240)
    plt.close(fig)
    print(f"[OK] Generated {output_path}")
    return output_path


if __name__ == '__main__':
    create_figure()
