#!/usr/bin/env python3
"""
Generate infographic:
"How Dissipation Changes the Local Phase Portrait"
Two-panel comparison of the local dynamics near the downward equilibrium:
- Left Panel: Undamped pendulum (center, conservative closed energy orbits, dE/dt = 0)
- Right Panel: Damped pendulum (stable spiral, dissipative inward trajectories, dE/dt <= 0)
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scipy.integrate import solve_ivp

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "dissipation_phase_portrait.png"

def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Color Palette matching editorial identity
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#334155'
    LIGHT_SLATE = '#94a3b8'
    BORDER_COLOR = '#cbd5e1'
    CARD_BG = '#f8fafc'
    PLOT_BG = '#ffffff'

    BLUE = '#1d4ed8'
    BLUE_DARK = '#1e40af'
    RED = '#dc2626'
    EMERALD = '#047857'
    TEAL = '#0f766e'

    PILL_BG_BLUE = '#dbeafe'
    PILL_BORDER_BLUE = '#60a5fa'
    PILL_TEXT_BLUE = '#1e3a8a'

    PILL_BG_GREEN = '#dcfce7'
    PILL_BORDER_GREEN = '#4ade80'
    PILL_TEXT_GREEN = '#14532d'

    # Dimensions in inches: generous height to ensure perfect vertical clearance and legibility
    fig_w = 17.6
    fig_h = 9.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Top Figure Title Badge (prominent, bold, dark navy)
    fig.text(0.5, 0.956,
             "How Dissipation Changes the Local Phase Portrait",
             fontsize=21.0, weight='bold', color=NAVY, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.30",
                       facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1.4))

    # Prominent, darkened subtitle (centered vertically with balanced clearance)
    fig.text(0.5, 0.887,
             "Without dissipation, trajectories remain on closed energy curves; with weak damping, they spiral toward an attractor.",
             fontsize=16.0, weight='bold', color=NAVY, ha='center', va='center')

    # Layout geometry: 2 cards side by side with transition bridge between them
    card_w_in = 7.10
    card_h_in = 7.70
    gap_x_in = 2.50
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

    # -------------------------------------------------------------
    # CARD 1: UNDAMPED PENDULUM (CONSERVATIVE)
    # -------------------------------------------------------------
    # Panel Header: Title + Descriptor
    ax1_bg.text(0.065, 0.940, "Undamped Pendulum", fontsize=19.5, weight='bold', color=NAVY, va='center')
    ax1_bg.text(0.935, 0.940, "Center", fontsize=15.5, weight='bold', color=BLUE_DARK,
                ha='right', va='center',
                bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.25",
                          facecolor=PILL_BG_BLUE, edgecolor=PILL_BORDER_BLUE, lw=1.3))

    # Math Note: dE/dt = 0 (prominent, bold, large)
    ax1_bg.text(0.065, 0.875, r"Conservative:   $\dfrac{dE}{dt} = 0$",
                fontsize=16.5, weight='bold', color=NAVY, va='center')

    # -------------------------------------------------------------
    # CARD 2: WEAKLY DAMPED PENDULUM (DISSIPATIVE)
    # -------------------------------------------------------------
    # Panel Header: Title + Descriptor
    ax2_bg.text(0.065, 0.940, "Weakly Damped Pendulum", fontsize=19.5, weight='bold', color=NAVY, va='center')
    ax2_bg.text(0.935, 0.940, "Stable Spiral", fontsize=15.5, weight='bold', color=PILL_TEXT_GREEN,
                ha='right', va='center',
                bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.25",
                          facecolor=PILL_BG_GREEN, edgecolor=PILL_BORDER_GREEN, lw=1.3))

    # Math Note: dE/dt <= 0 (prominent, bold, large)
    ax2_bg.text(0.065, 0.875, r"Dissipative:   $\dfrac{dE}{dt} \leq 0$",
                fontsize=16.5, weight='bold', color=NAVY, va='center')

    # -------------------------------------------------------------
    # INNER SUB-PLOTS (Identical Axes & Coordinate Ranges)
    # -------------------------------------------------------------
    # Plot geometry: 5.40 in wide with 1.15 in left pad guarantees 100+ px clearance inside the card for horizontal omega
    plot_w_in = 5.40
    plot_h_in = 4.75
    plot_w = plot_w_in / fig_w
    plot_h = plot_h_in / fig_h

    plot_pad_left_in = 1.15
    plot_pad_left = plot_pad_left_in / fig_w
    plot_pad_bottom = 0.170 * card_h

    sub1_x = x1 + plot_pad_left
    sub1_y = bottom_y + plot_pad_bottom

    sub2_x = x2 + plot_pad_left
    sub2_y = bottom_y + plot_pad_bottom

    ax1 = fig.add_axes([sub1_x, sub1_y, plot_w, plot_h])
    ax2 = fig.add_axes([sub2_x, sub2_y, plot_w, plot_h])

    # Bottom Annotations inside Cards (centered exactly under the plot area, enlarged to 15.5pt bold NAVY)
    center_plot_in_card = (plot_pad_left_in + plot_w_in / 2.0) / card_w_in
    ax1_bg.text(center_plot_in_card, 0.052, "Nearby trajectories remain\non closed energy curves.",
                fontsize=15.5, weight='bold', color=NAVY, ha='center', va='center', linespacing=1.28)
    ax2_bg.text(center_plot_in_card, 0.052, "Nearby trajectories lose energy\nand converge to the equilibrium.",
                fontsize=15.5, weight='bold', color=NAVY, ha='center', va='center', linespacing=1.28)

    # -------------------------------------------------------------
    # CENTRAL TRANSITION BADGE (Between Cards)
    # -------------------------------------------------------------
    # Align arrow precisely with the plot centerline (omega = 0 axis)
    mid_x = (x1 + card_w + x2) / 2.0
    plot_center_y = sub1_y + plot_h / 2.0
    mid_y_arr = plot_center_y
    mid_y_box = plot_center_y + 0.12

    fig.text(mid_x, mid_y_box, "Add Weak Damping\n" + r"$0 < \gamma < 2\sqrt{\frac{g}{\ell}}$",
             ha="center", va="center", fontsize=13.0, weight='bold', color=NAVY,
             linespacing=1.45,
             bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.25", facecolor="#ffffff", edgecolor=BORDER_COLOR, lw=1.4))
    fig.text(mid_x, mid_y_arr, r"$\longrightarrow$", ha="center", va="center", fontsize=34, color=DARK_SLATE)

    # Coordinate domain: Local window near origin
    th_lim = 1.35
    om_lim = 1.35

    for ax in [ax1, ax2]:
        ax.set_facecolor(PLOT_BG)
        ax.set_xlim(-th_lim, th_lim)
        ax.set_ylim(-om_lim, om_lim)
        ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
        ax.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])
        ax.tick_params(colors=NAVY, width=1.4, length=5.0)
        for tick_label in ax.get_xticklabels() + ax.get_yticklabels():
            tick_label.set_fontsize(14.0)
            tick_label.set_fontweight('bold')
            tick_label.set_color(NAVY)

        ax.grid(True, linestyle='--', color='#e2e8f0', alpha=0.85, zorder=1)
        for spine in ax.spines.values():
            spine.set_color(BORDER_COLOR)
            spine.set_linewidth(1.3)

        # Prominent, darkened, enlarged axis labels: horizontal upright omega for effortless legibility
        ax.set_xlabel(r"$\theta$", fontsize=20.0, color=NAVY, labelpad=7, weight='bold')
        ax.set_ylabel(r"$\omega$", fontsize=22.0, color=NAVY, labelpad=12, weight='bold', rotation=0, va='center')

        # Neutral center lines
        ax.axhline(0, color='#94a3b8', lw=1.1, linestyle=':', zorder=2)
        ax.axvline(0, color='#94a3b8', lw=1.1, linestyle=':', zorder=2)

    # -------------------------------------------------------------
    # PLOT 1: UNDAMPED TRAJECTORIES (CLOSED ENERGY CONTOURS)
    # -------------------------------------------------------------
    # Subtle background vector field
    grid_pts = 17
    TH, OM = np.meshgrid(np.linspace(-1.25, 1.25, grid_pts), np.linspace(-1.25, 1.25, grid_pts))
    U1 = OM
    V1 = -np.sin(TH)
    M1 = np.hypot(U1, V1) + 1e-6
    ax1.quiver(TH, OM, U1 / M1, V1 / M1, color='#cbd5e1', alpha=0.45,
               width=0.0028, scale=32, headwidth=3.2, headlength=4.0, zorder=2)

    # Exact energy contours: e = 0.5 * om^2 + (1 - cos(th))
    e_levels = [0.06, 0.18, 0.38, 0.65]
    for e_val in e_levels:
        th_max = np.arccos(1.0 - e_val)
        th_pts = np.linspace(-th_max, th_max, 150)
        om_pts = np.sqrt(np.maximum(0, 2.0 * (e_val - (1.0 - np.cos(th_pts)))))

        # Full closed loop
        th_loop = np.concatenate([th_pts, th_pts[::-1], [th_pts[0]]])
        om_loop = np.concatenate([om_pts, -om_pts[::-1], [om_pts[0]]])

        ax1.plot(th_loop, om_loop, color=BLUE, lw=2.0, alpha=0.90, zorder=4)

        # Clockwise flow arrows
        idx_top = 75
        ax1.annotate('', xy=(th_pts[idx_top + 4], om_pts[idx_top + 4]),
                     xytext=(th_pts[idx_top], om_pts[idx_top]),
                     arrowprops=dict(arrowstyle="->,head_width=0.34,head_length=0.48", color=BLUE, lw=2.0), zorder=5)
        ax1.annotate('', xy=(th_pts[idx_top - 4], -om_pts[idx_top - 4]),
                     xytext=(th_pts[idx_top], -om_pts[idx_top]),
                     arrowprops=dict(arrowstyle="->,head_width=0.34,head_length=0.48", color=BLUE, lw=2.0), zorder=5)

    # Fixed point marker in Panel 1 (clear, prominent label with pointer)
    ax1.plot(0, 0, 'o', color=NAVY, markersize=9.5, markeredgecolor='#ffffff', markeredgewidth=2.2, zorder=10)
    ax1.annotate(
        r"$(\theta,\omega) = (0,0)$" + "\n" + r"$\mathbf{Center}$",
        xy=(0.02, 0.02), xytext=(0.34, 0.28),
        fontsize=14.5, color=BLUE_DARK, weight='bold',
        linespacing=1.22, ha='left', va='center', zorder=15,
        bbox=dict(boxstyle="round,pad=0.32", facecolor="#eff6ff", edgecolor="#bfdbfe", alpha=0.96, lw=1.2),
        arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.42", color=BLUE_DARK, lw=1.4,
                        shrinkA=4, shrinkB=4, connectionstyle="arc3,rad=-0.1")
    )

    # -------------------------------------------------------------
    # PLOT 2: DAMPED TRAJECTORIES (INWARD SPIRALS TO ATTRACTOR)
    # -------------------------------------------------------------
    gamma = 0.35  # Weak damping parameter (gamma^2 = 0.1225 < 4.0)

    # Subtle damped background vector field
    U2 = OM
    V2 = -gamma * OM - np.sin(TH)
    M2 = np.hypot(U2, V2) + 1e-6
    ax2.quiver(TH, OM, U2 / M2, V2 / M2, color='#cbd5e1', alpha=0.45,
               width=0.0028, scale=32, headwidth=3.2, headlength=4.0, zorder=2)

    def damped_pendulum_ode(t, y):
        th, om = y
        return [om, -gamma * om - np.sin(th)]

    # Spiral trajectories from 6 distributed initial points
    initial_conditions = [
        (1.10, 0.0),
        (-1.10, 0.0),
        (0.0, 1.15),
        (0.0, -1.15),
        (0.85, 0.70),
        (-0.85, -0.70),
    ]

    t_span = (0, 22)
    t_eval = np.linspace(0, 22, 900)

    for i, ic in enumerate(initial_conditions):
        sol = solve_ivp(damped_pendulum_ode, t_span, ic, t_eval=t_eval, rtol=1e-8, atol=1e-9)
        th_traj = sol.y[0]
        om_traj = sol.y[1]

        # Truncate when very close to origin to keep center clean and legible
        r_dist = np.hypot(th_traj, om_traj)
        stop_mask = r_dist > 0.055
        if np.any(~stop_mask):
            first_in = np.argmax(~stop_mask)
            th_traj = th_traj[:first_in]
            om_traj = om_traj[:first_in]

        # Plot spiral arm
        ax2.plot(th_traj, om_traj, color=TEAL, lw=1.9, alpha=0.90, zorder=4)

        # Place inward-pointing flow arrows along the spiral
        arrow_indices = [50, 180, 380]
        for a_idx in arrow_indices:
            if a_idx + 6 < len(th_traj) and np.hypot(th_traj[a_idx], om_traj[a_idx]) > 0.22:
                ax2.annotate('', xy=(th_traj[a_idx + 6], om_traj[a_idx + 6]),
                             xytext=(th_traj[a_idx], om_traj[a_idx]),
                             arrowprops=dict(arrowstyle="->,head_width=0.30,head_length=0.44", color=TEAL, lw=1.9), zorder=5)

    # Fixed point marker in Panel 2 (Attractor)
    ax2.plot(0, 0, 'o', color=RED, markersize=9.5, markeredgecolor='#ffffff', markeredgewidth=2.2, zorder=10)

    # Attractor badge with elegant offset callout and prominent 14.5pt bold text
    callout_x = 0.34
    callout_y = 0.28
    ax2.annotate(
        r"$(\theta,\omega) = (0,0)$" + "\n" + r"$\mathbf{Attractor}$",
        xy=(0.02, 0.02), xytext=(callout_x, callout_y),
        fontsize=14.5, color=RED, weight='bold',
        linespacing=1.22, ha='left', va='center', zorder=15,
        bbox=dict(boxstyle="round,pad=0.32", facecolor="#fff1f2", edgecolor="#fecdd3", alpha=0.96, lw=1.2),
        arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.42", color=RED, lw=1.4,
                        shrinkA=4, shrinkB=4, connectionstyle="arc3,rad=-0.1")
    )

    # Save
    plt.savefig(output_path, dpi=240, bbox_inches='tight', pad_inches=0.35, facecolor='#ffffff')
    plt.close()
    print(f"[OK] Generated {output_path}")
    return output_path

if __name__ == "__main__":
    create_figure()
