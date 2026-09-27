#!/usr/bin/env python3
"""
Generate figure:
"Phase Space of the Pendulum: Libration, Rotation, and the Separatrix"
Single-panel phase portrait in the (theta, p_theta) plane.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_IMG = SCRIPT_DIR.parent / "images" / "pendulum_phase_portrait.png"

def create_figure(output_path=None):
    if output_path is None:
        output_path = OUTPUT_IMG
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    })

    # Curated Editorial Palette matching publication
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#475569'
    LIGHT_SLATE = '#64748b'
    BORDER_COLOR = '#cbd5e1'
    CARD_BG = '#f8fafc'
    GRID_COLOR = '#f1f5f9'
    
    BLUE = '#2563eb'
    BLUE_LIGHT = '#eff6ff'
    BLUE_BORDER = '#bfdbfe'
    
    RED = '#dc2626'
    RED_LIGHT = '#fff1f2'
    RED_BORDER = '#fecaca'
    
    EMERALD = '#059669'
    EMERALD_LIGHT = '#ecfdf5'
    EMERALD_BORDER = '#a7f3d0'

    # Dimensions
    fig_w = 15.6
    fig_h = 9.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Top Title Badge
    fig.text(0.5, 0.956,
             r"Phase Space of the Pendulum: $\mathbf{Libration}$, $\mathbf{Rotation}$, and the $\mathbf{Separatrix}$",
             fontsize=20.5, weight='bold', color=NAVY, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.25",
                       facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1.3))

    # Subtitle / Energy note box with enlarged formula and prominent rescaling note
    badge_box = patches.FancyBboxPatch((0.155, 0.844), 0.69, 0.076,
                                       boxstyle="round,pad=0.012,rounding_size=0.016",
                                       transform=fig.transFigure,
                                       facecolor='#ffffff', edgecolor=BORDER_COLOR, lw=1.1, zorder=1)
    fig.patches.append(badge_box)

    fig.text(0.5, 0.896,
             r"$\mathbf{Constant\text{-}Energy\ Trajectories:}\quad H(\theta, p_\theta) = \frac{p_\theta^2}{2} - \cos\theta = E = \mathrm{const.}$",
             fontsize=15.8, weight='bold', color=DARK_SLATE, ha='center', va='center', zorder=2)
    fig.text(0.5, 0.865,
             "Normalized units, with momentum and energy rescaled",
             fontsize=14.5, style='italic', color='#334155', ha='center', va='center', zorder=2)

    # Main plot axes placement
    ax_x = 0.100
    ax_y = 0.115
    ax_w = 0.840
    ax_h = 0.700
    ax = fig.add_axes([ax_x, ax_y, ax_w, ax_h])
    ax.set_facecolor('#ffffff')
    ax.grid(True, linestyle='--', color=GRID_COLOR, alpha=0.9, zorder=1)

    # Domain limits: centered on primary period [-pi, pi] with natural continuation to +/- 1.26 pi
    th_lim = 1.26 * np.pi
    p_lim = 2.55
    ax.set_xlim(-th_lim, th_lim)
    ax.set_ylim(-p_lim, p_lim)

    # Coordinate axes through the origin
    ax.axhline(0, color=LIGHT_SLATE, lw=1.0, linestyle='-', alpha=0.6, zorder=2)
    ax.axvline(0, color=LIGHT_SLATE, lw=1.0, linestyle='-', alpha=0.6, zorder=2)

    # Fundamental period boundaries at theta = -pi and +pi
    ax.axvline(-np.pi, color='#cbd5e1', lw=1.2, linestyle=':', alpha=0.8, zorder=2)
    ax.axvline(np.pi, color='#cbd5e1', lw=1.2, linestyle=':', alpha=0.8, zorder=2)

    # Subtle vector field
    th_q = np.linspace(-th_lim * 0.96, th_lim * 0.96, 23)
    p_q = np.linspace(-p_lim * 0.88, p_lim * 0.88, 13)
    TH_Q, P_Q = np.meshgrid(th_q, p_q)
    U_q = P_Q
    V_q = -np.sin(TH_Q)
    mag_q = np.sqrt(U_q**2 + V_q**2) + 1e-6
    ax.quiver(TH_Q, P_Q, U_q / mag_q, V_q / mag_q,
              color='#cbd5e1', alpha=0.40, width=0.0022, scale=36, headwidth=3.2, headlength=4.0, zorder=2)

    # 1. Libration curves (E < E_sep, where E_sep = 2.0 in (1 - cos theta) / E_sep = 1 in -cos theta)
    e_libr = [0.45, 0.95, 1.45, 1.82]
    for e_val in e_libr:
        th_max_e = np.arccos(1.0 - e_val)
        th_span = np.linspace(-th_max_e, th_max_e, 250)
        p_span = np.sqrt(np.maximum(0, 2 * (e_val - (1 - np.cos(th_span)))))

        th_loop = np.concatenate([th_span, th_span[::-1], [th_span[0]]])
        p_loop = np.concatenate([p_span, -p_span[::-1], [p_span[0]]])
        ax.plot(th_loop, p_loop, color=BLUE, lw=2.1, alpha=0.88, zorder=4)

        # Flow arrows on libration (clockwise)
        # Top branch moving right
        idx_t = 125
        ax.annotate('', xy=(th_span[idx_t + 4], p_span[idx_t + 4]),
                    xytext=(th_span[idx_t], p_span[idx_t]),
                    arrowprops=dict(arrowstyle="->,head_width=0.32,head_length=0.48", color=BLUE, lw=1.9), zorder=5)
        # Bottom branch moving left
        idx_b = 125
        ax.annotate('', xy=(th_span[idx_b - 4], -p_span[idx_b - 4]),
                    xytext=(th_span[idx_b], -p_span[idx_b]),
                    arrowprops=dict(arrowstyle="->,head_width=0.32,head_length=0.48", color=BLUE, lw=1.9), zorder=5)

    # 2. Rotation curves (E > E_sep)
    e_rot = [2.25, 2.80, 3.65]
    th_rot = np.linspace(-th_lim, th_lim, 600)
    for e_val in e_rot:
        p_rot_p = np.sqrt(2 * (e_val - (1 - np.cos(th_rot))))
        p_rot_m = -p_rot_p
        ax.plot(th_rot, p_rot_p, color=EMERALD, lw=2.1, alpha=0.90, zorder=4)
        ax.plot(th_rot, p_rot_m, color=EMERALD, lw=2.1, alpha=0.90, zorder=4)

        # Flow arrows on rotation: offset from center
        for x_arr in [-0.55 * np.pi, 0.55 * np.pi]:
            idx_a = np.argmin(np.abs(th_rot - x_arr))
            # Upper branch moving right
            ax.annotate('', xy=(th_rot[idx_a + 4], p_rot_p[idx_a + 4]),
                        xytext=(th_rot[idx_a], p_rot_p[idx_a]),
                        arrowprops=dict(arrowstyle="->,head_width=0.32,head_length=0.48", color=EMERALD, lw=1.9), zorder=5)
            # Lower branch moving left
            ax.annotate('', xy=(th_rot[idx_a - 4], p_rot_m[idx_a - 4]),
                        xytext=(th_rot[idx_a], p_rot_m[idx_a]),
                        arrowprops=dict(arrowstyle="->,head_width=0.32,head_length=0.48", color=EMERALD, lw=1.9), zorder=5)

    # 3. Separatrix (E = E_sep = 2.0, passing through hyperbolic saddles at +/- pi)
    th_sep = np.linspace(-th_lim, th_lim, 800)
    p_sep_top = 2.0 * np.cos(th_sep / 2.0)
    p_sep_bot = -2.0 * np.cos(th_sep / 2.0)
    ax.plot(th_sep, p_sep_top, color=RED, lw=3.3, zorder=6)
    ax.plot(th_sep, p_sep_bot, color=RED, lw=3.3, zorder=6)

    # Arrows on separatrix
    for s_th in [-0.45 * np.pi, 0.45 * np.pi]:
        # Upper separatrix (moving right from -pi to +pi)
        p_top = 2.0 * np.cos(s_th / 2.0)
        p_top_next = 2.0 * np.cos((s_th + 0.12) / 2.0)
        ax.annotate('', xy=(s_th + 0.12, p_top_next),
                    xytext=(s_th, p_top),
                    arrowprops=dict(arrowstyle="->,head_width=0.38,head_length=0.58", color=RED, lw=2.5), zorder=7)
        # Lower separatrix (moving left from +pi to -pi)
        p_bot = -2.0 * np.cos(s_th / 2.0)
        p_bot_next = -2.0 * np.cos((s_th - 0.12) / 2.0)
        ax.annotate('', xy=(s_th - 0.12, p_bot_next),
                    xytext=(s_th, p_bot),
                    arrowprops=dict(arrowstyle="->,head_width=0.38,head_length=0.58", color=RED, lw=2.5), zorder=7)

    # Equilibria
    # 1. Stable Center at (0, 0)
    ax.plot(0, 0, 'o', color=BLUE, markersize=11.5, markeredgecolor=NAVY, markeredgewidth=2.2, zorder=8)
    ax.text(0, -0.22, r"$\mathbf{Stable\ Center}\ (0, 0)$" + "\n(downward rest)",
            fontsize=12.5, color=BLUE, weight='bold', ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.28", facecolor="#ffffff", edgecolor=BLUE_BORDER, lw=1.2), zorder=9)

    # 2. Unstable Hyperbolic Saddles at (-pi, 0) and (+pi, 0)
    for s_th in [-np.pi, np.pi]:
        ax.plot(s_th, 0, 's', color=RED, markersize=11.5, markeredgecolor=NAVY, markeredgewidth=2.2, zorder=8)
        sgn = "-" if s_th < 0 else ""
        ax.text(s_th, -0.22, rf"$\mathbf{{Unstable\ Saddle}}\ ({sgn}\pi, 0)$" + "\n(inverted upright)",
                fontsize=12.0, color=RED, weight='bold', ha='center', va='top',
                bbox=dict(boxstyle="round,pad=0.28", facecolor="#ffffff", edgecolor=RED_BORDER, lw=1.2), zorder=9)

    # -------------------------------------------------------------
    # Enlarged, High-Contrast Regime Badges with Callouts
    # -------------------------------------------------------------
    # 1. Libration (nestled in center of libration region)
    ax.text(0, 0.72, r"$\mathbf{Libration}\;(E < E_{\mathrm{sep}}):\;\text{Closed periodic loops}$",
            fontsize=14.0, color=BLUE, weight='bold', ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.34", facecolor=BLUE_LIGHT, edgecolor=BLUE_BORDER, lw=1.3), zorder=9)

    # 2. Separatrix: placed in open upper-left quadrant with pointer arrow to the red curve
    sep_pt_th = -0.38 * np.pi
    sep_pt_p = 2.0 * np.cos(sep_pt_th / 2.0)
    ax.annotate(r"$\mathbf{Separatrix}\;(E = E_{\mathrm{sep}}):\;\text{Dividing boundary}$",
                xy=(sep_pt_th, sep_pt_p),
                xytext=(-0.76 * np.pi, 2.18),
                fontsize=14.0, color=RED, weight='bold', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.34", facecolor=RED_LIGHT, edgecolor=RED_BORDER, lw=1.3),
                arrowprops=dict(arrowstyle="->,head_width=0.38,head_length=0.55", color=RED, lw=2.0,
                                connectionstyle="arc3,rad=-0.12"),
                zorder=10)

    # 3. Rotation: updated label "Continuous rotational motion" with pointer arrow to the top rotation curve
    rot_pt_th = 0.50 * np.pi
    rot_pt_p = np.sqrt(2 * (2.80 - (1 - np.cos(rot_pt_th))))
    ax.annotate(r"$\mathbf{Rotation}\;(E > E_{\mathrm{sep}}):\;\text{Continuous rotational motion}$",
                xy=(rot_pt_th, rot_pt_p),
                xytext=(0.76 * np.pi, 2.18),
                fontsize=14.0, color=EMERALD, weight='bold', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.34", facecolor=EMERALD_LIGHT, edgecolor=EMERALD_BORDER, lw=1.3),
                arrowprops=dict(arrowstyle="->,head_width=0.38,head_length=0.55", color=EMERALD, lw=2.0,
                                connectionstyle="arc3,rad=0.12"),
                zorder=10)

    # Ticks & Axes
    th_ticks = [-np.pi, -0.5 * np.pi, 0, 0.5 * np.pi, np.pi]
    th_labels = [r"$-\pi$", r"$-\frac{\pi}{2}$", r"$0$", r"$\frac{\pi}{2}$", r"$\pi$"]
    ax.set_xticks(th_ticks)
    ax.set_xticklabels(th_labels, fontsize=15.5, color=NAVY, weight='bold')
    
    p_ticks = [-2, -1, 0, 1, 2]
    p_labels = [r"$-2$", r"$-1$", r"$0$", r"$1$", r"$2$"]
    ax.set_yticks(p_ticks)
    ax.set_yticklabels(p_labels, fontsize=15.5, color=NAVY, weight='bold')

    ax.set_xlabel(r"$\theta$ (angular position)", fontsize=17.5, color=NAVY, weight='bold', labelpad=9)
    ax.set_ylabel(r"$p_\theta$ (conjugate momentum)", fontsize=17.5, color=NAVY, weight='bold', labelpad=9)

    # Framing spines
    for spine in ax.spines.values():
        spine.set_color(BORDER_COLOR)
        spine.set_linewidth(1.3)

    plt.savefig(output_path, dpi=240, bbox_inches='tight', pad_inches=0.25, facecolor='#ffffff')
    plt.close()
    print(f"[OK] Generated {output_path}")
    return output_path

if __name__ == "__main__":
    create_figure()
