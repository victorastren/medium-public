#!/usr/bin/env python3
"""
Generate infographic:
"Phase Portrait of the Nonlinear Pendulum: Libration, Separatrix, Rotation"
Visualizing the three dynamical regimes and their physical configurations.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "pendulum_phase_portrait.png"

def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#475569'
    LIGHT_SLATE = '#94a3b8'
    BLUE = '#2563eb'
    RED = '#dc2626'
    EMERALD = '#059669'
    CARD_BG = '#f8fafc'
    BORDER_COLOR = '#cbd5e1'

    fig_w = 18.5
    fig_h = 8.1
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Snug title badge at top matching state_space_transition.png
    fig.text(0.5, 0.942,
             r"Phase Portrait of the Nonlinear Pendulum:   $\mathbf{Libration} \;\cdot\; \mathbf{Separatrix} \;\cdot\; \mathbf{Rotation}$",
             fontsize=17.5, weight='bold', color=NAVY, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.30",
                       facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1.2))

    # Layout geometry: 3 panels with generous vertical card height
    card_h_in = 6.45
    y_bottom_in = 0.52
    y_bottom = y_bottom_in / fig_h
    h_card_norm = card_h_in / fig_h

    w1_in = 4.65
    w2_in = 8.15
    w3_in = 4.65
    gap_in = 0.35

    w1 = w1_in / fig_w
    w2 = w2_in / fig_w
    w3 = w3_in / fig_w
    gap = gap_in / fig_w
    left_m = (1.0 - (w1 + w2 + w3 + 2 * gap)) / 2.0

    x1 = left_m
    x2 = x1 + w1 + gap
    x3 = x2 + w2 + gap

    ax1 = fig.add_axes([x1, y_bottom, w1, h_card_norm])
    ax2_bg = fig.add_axes([x2, y_bottom, w2, h_card_norm])
    ax3 = fig.add_axes([x3, y_bottom, w3, h_card_norm])

    # Aspect scale for circular geometries in side panels
    # x span = 3.3 in 4.65 in; y span = 3.35 in 6.45 in
    # 1 plot x = 4.65 / 3.3 = 1.409 in
    # 1 plot y = 6.45 / 3.35 = 1.925 in
    # aspect_scale = 1.925 / 1.409 = 1.366
    aspect_scale = 1.366

    # =============================================================
    # PANEL 1: LIBRATION REGIME & THETA = 0 CONFIGURATION
    # =============================================================
    ax1.set_facecolor(CARD_BG)
    ax1.set_xlim(-1.65, 1.65)
    ax1.set_ylim(-1.85, 1.55)
    ax1.axis('off')

    card1 = patches.FancyBboxPatch((-1.58, -1.78), 3.16, 3.28,
                                   boxstyle="round,pad=0.03,rounding_size=0.10",
                                   facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.2, zorder=0)
    ax1.add_patch(card1)

    ax1.text(0, 1.30, "1. Libration Regime", fontsize=16.5, weight='bold', color=NAVY, ha='center')
    ax1.text(0, 1.08, r"Oscillations around $\theta = 0$  ($E < 2mg\ell$)", fontsize=13.0, weight='bold', color=BLUE, ha='center')

    # Ceiling mount
    pivot_y = 0.65
    ax1.plot([-0.72, 0.72], [pivot_y, pivot_y], color=NAVY, lw=2.5, zorder=2)
    for x_h in np.linspace(-0.66, 0.66, 12):
        ax1.plot([x_h, x_h + 0.08], [pivot_y, pivot_y + 0.09], color=SLATE, lw=1.2, zorder=2)
    ax1.plot(0, pivot_y, 'o', color=NAVY, markersize=8, zorder=4)

    # Vertical reference line (theta = 0)
    ax1.plot([0, 0], [pivot_y, pivot_y - 1.35], color=LIGHT_SLATE, linestyle='--', lw=1.4, zorder=1)

    # Pendulum arm & bob at equilibrium (theta = 0) - faint ghost
    rod_len_y = 0.96
    ax1.plot([0, 0], [pivot_y, pivot_y - rod_len_y], color=LIGHT_SLATE, lw=1.8, linestyle=':', zorder=2)
    ghost_bob = patches.Circle((0, pivot_y - rod_len_y), 0.12, facecolor='#e2e8f0', edgecolor=LIGHT_SLATE, lw=1.5, linestyle=':', zorder=2)
    ax1.add_patch(ghost_bob)
    ax1.text(0, pivot_y - rod_len_y - 0.19, r"$\theta = 0$ (stable equilibrium, $E = 0$)", fontsize=12.5, color=DARK_SLATE, weight='bold', ha='center')

    # Pendulum arm & bob at max amplitude theta_max = 48 deg (0.84 rad)
    th_max = 0.84
    bob_x = (rod_len_y * np.sin(th_max)) * aspect_scale
    bob_y = pivot_y - rod_len_y * np.cos(th_max)
    bob_x_neg = -bob_x
    bob_y_neg = bob_y

    # Left ghost bob
    ax1.plot([0, bob_x_neg], [pivot_y, bob_y_neg], color='#93c5fd', lw=1.8, linestyle='--', zorder=3)
    bob_left = patches.Circle((bob_x_neg, bob_y_neg), 0.12, facecolor='#dbeafe', edgecolor=BLUE, lw=1.5, zorder=3)
    ax1.add_patch(bob_left)

    # Active arm and bob (right)
    ax1.plot([0, bob_x], [pivot_y, bob_y], color=NAVY, lw=2.8, zorder=4)
    bob_active = patches.Circle((bob_x, bob_y), 0.13, facecolor=BLUE, edgecolor=NAVY, lw=2.0, zorder=5)
    ax1.add_patch(bob_active)

    # Angle arc for theta_max
    arc_th = np.linspace(-np.pi/2, -np.pi/2 + th_max, 30)
    r_th = 0.36
    ax1.plot((r_th * np.cos(arc_th)) * aspect_scale, pivot_y + r_th * np.sin(arc_th), color=BLUE, lw=1.8, zorder=3)
    ax1.text(0.18, pivot_y - 0.40, r"$\theta_{\max}$", fontsize=13.0, color=BLUE, weight='bold')

    # Oscillation arc showing trajectory path
    arc_angles = np.linspace(-np.pi/2 - th_max, -np.pi/2 + th_max, 50)
    ax1.plot((rod_len_y * np.cos(arc_angles)) * aspect_scale, pivot_y + rod_len_y * np.sin(arc_angles),
             color=BLUE, lw=2.2, linestyle='-', zorder=3)

    # Double-headed oscillation curved arrows
    r_arr = 0.70
    arc_arr1 = np.linspace(-np.pi/2 - 0.46, -np.pi/2 + 0.46, 40)
    xs_arr1 = (r_arr * np.cos(arc_arr1)) * aspect_scale
    ys_arr1 = pivot_y + r_arr * np.sin(arc_arr1)
    arr_osc1 = patches.FancyArrowPatch(path=mpath.Path(np.column_stack([xs_arr1, ys_arr1])),
                                       arrowstyle='<->,head_width=4.5,head_length=6.0',
                                       color=BLUE, lw=2.0, zorder=5)
    ax1.add_patch(arr_osc1)
    ax1.text(0, pivot_y - 0.57, "Libration", fontsize=13.0, color=BLUE, weight='bold', ha='center', zorder=6)

    # Turning points annotation
    ax1.text(bob_x + 0.18, bob_y, r"$\omega = 0$", fontsize=12.5, color=BLUE, weight='bold', va='center')
    ax1.text(bob_x_neg - 0.18, bob_y, r"$\omega = 0$", fontsize=12.5, color=BLUE, weight='bold', va='center', ha='right')

    # Energy badge
    ax1.text(0, -0.92, r"$\mathbf{Energy:}\; 0 < E < 2mg\ell$", fontsize=12.5, color=BLUE, weight='bold', ha='center',
             bbox=dict(boxstyle="round,pad=0.25", facecolor="#eff6ff", edgecolor="#bfdbfe", lw=1.1))

    # Prominent bottom text with generous clearance above the card border
    ax1.text(0, -1.40,
             "Periodic oscillation between\n" + r"turning points where $\omega = 0$;" + "\nphase trajectories form closed loops.",
             fontsize=13.0, weight='bold', color=NAVY, ha='center', va='center', linespacing=1.32)

    # =============================================================
    # PANEL 2: FULL PHASE PORTRAIT (LIBRATION + SEPARATRIX + ROTATION)
    # =============================================================
    ax2_bg.set_facecolor(CARD_BG)
    ax2_bg.set_xlim(-4.0, 4.0)
    ax2_bg.set_ylim(-1.85, 1.55)
    ax2_bg.axis('off')

    card2 = patches.FancyBboxPatch((-3.92, -1.78), 7.84, 3.28,
                                   boxstyle="round,pad=0.03,rounding_size=0.10",
                                   facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.2, zorder=0)
    ax2_bg.add_patch(card2)

    # Header on ax2_bg
    ax2_bg.text(0, 1.30, "2. Pendulum Phase Portrait", fontsize=16.5, weight='bold', color=NAVY, ha='center')
    ax2_bg.text(0, 1.08, r"Partition of state space by the separatrix ($E = 2mg\ell$)", fontsize=13.0, weight='bold', color=DARK_SLATE, ha='center')

    # Prominent bottom summary on ax2_bg with generous clearance
    panel2_text = (
        "The separatrix divides closed libration trajectories around (0,0)\n"
        "from rotational trajectories at higher energy."
    )
    ax2_bg.text(0, -1.40, panel2_text,
                fontsize=13.0, weight='bold', color=NAVY, ha='center', va='center', linespacing=1.32)

    # Sub-axes inside card2 for the plot coordinates
    pad_x_left = 1.25 / fig_w
    pad_x_right = 0.71 / fig_w
    pad_b = 1.68 / fig_h
    pad_t = 0.98 / fig_h
    sub_x = x2 + pad_x_left
    sub_y = y_bottom + pad_b
    sub_w = w2 - (pad_x_left + pad_x_right)
    sub_h = h_card_norm - pad_b - pad_t

    ax2_sub = fig.add_axes([sub_x, sub_y, sub_w, sub_h])
    ax2_sub.set_facecolor('#ffffff')
    ax2_sub.grid(True, linestyle='--', color='#e2e8f0', alpha=0.8, zorder=1)

    th_lim = 2.2 * np.pi
    om_lim = 2.70
    ax2_sub.set_xlim(-th_lim, th_lim)
    ax2_sub.set_ylim(-om_lim, om_lim)

    # Subtle background vector field
    th_q = np.linspace(-2.0 * np.pi, 2.0 * np.pi, 25)
    om_q = np.linspace(-2.2, 2.2, 13)
    TH_Q, OM_Q = np.meshgrid(th_q, om_q)
    U_q = OM_Q
    V_q = -np.sin(TH_Q)
    mag_q = np.sqrt(U_q**2 + V_q**2) + 1e-6
    ax2_sub.quiver(TH_Q, OM_Q, U_q / mag_q, V_q / mag_q,
                   color='#cbd5e1', alpha=0.45, width=0.0022, scale=36, headwidth=3.2, headlength=4.0, zorder=2)

    # 1. Libration trajectories (E/E_sep < 1.0)
    e_libr = [0.25, 0.65, 1.15, 1.65]
    for e_val in e_libr:
        th_max_e = np.arccos(1.0 - e_val)
        th_span = np.linspace(-th_max_e, th_max_e, 180)
        om_span = np.sqrt(np.maximum(0, 2 * (e_val - 1 + np.cos(th_span))))

        for shift in [-2 * np.pi, 0, 2 * np.pi]:
            th_loop = np.concatenate([th_span + shift, th_span[::-1] + shift, [th_span[0] + shift]])
            om_loop = np.concatenate([om_span, -om_span[::-1], [om_span[0]]])
            ax2_sub.plot(th_loop, om_loop, color=BLUE, lw=1.6, alpha=0.85, zorder=4)

            # Arrows on libration (clockwise)
            idx_arr = 90
            ax2_sub.annotate('', xy=(th_span[idx_arr + 4] + shift, om_span[idx_arr + 4]),
                             xytext=(th_span[idx_arr] + shift, om_span[idx_arr]),
                             arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.42", color=BLUE, lw=1.6), zorder=5)
            ax2_sub.annotate('', xy=(th_span[idx_arr - 4] + shift, -om_span[idx_arr - 4]),
                             xytext=(th_span[idx_arr] + shift, -om_span[idx_arr]),
                             arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.42", color=BLUE, lw=1.6), zorder=5)

    # 2. Rotation trajectories (E/E_sep > 1.0, e > 2.0)
    e_rot = [2.25, 2.90, 3.85]
    th_rot = np.linspace(-th_lim, th_lim, 400)
    for e_val in e_rot:
        om_rot_p = np.sqrt(2 * (e_val - 1 + np.cos(th_rot)))
        om_rot_m = -om_rot_p
        ax2_sub.plot(th_rot, om_rot_p, color=EMERALD, lw=1.6, alpha=0.9, zorder=4)
        ax2_sub.plot(th_rot, om_rot_m, color=EMERALD, lw=1.6, alpha=0.9, zorder=4)

        # Arrows on rotation
        for x_arr in [- np.pi, np.pi]:
            idx_a = np.argmin(np.abs(th_rot - x_arr))
            ax2_sub.annotate('', xy=(th_rot[idx_a + 4], om_rot_p[idx_a + 4]),
                             xytext=(th_rot[idx_a], om_rot_p[idx_a]),
                             arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.42", color=EMERALD, lw=1.6), zorder=5)
            ax2_sub.annotate('', xy=(th_rot[idx_a - 4], om_rot_m[idx_a - 4]),
                             xytext=(th_rot[idx_a], om_rot_m[idx_a]),
                             arrowprops=dict(arrowstyle="->,head_width=0.28,head_length=0.42", color=EMERALD, lw=1.6), zorder=5)

    # 3. SEPARATRIX (E = 2mg*l)
    th_sep = np.linspace(-th_lim, th_lim, 500)
    ax2_sub.plot(th_sep, 2.0 * np.cos(th_sep / 2.0), color=RED, lw=2.6, zorder=6)
    ax2_sub.plot(th_sep, -2.0 * np.cos(th_sep / 2.0), color=RED, lw=2.6, zorder=6)

    # Arrows on separatrix
    for s_th in [-1.5 * np.pi, -0.5 * np.pi, 0.5 * np.pi, 1.5 * np.pi]:
        ax2_sub.annotate('', xy=(s_th + 0.12, 2.0 * np.cos((s_th + 0.12) / 2.0)),
                         xytext=(s_th, 2.0 * np.cos(s_th / 2.0)),
                         arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.52", color=RED, lw=2.2), zorder=7)
        ax2_sub.annotate('', xy=(s_th - 0.12, -2.0 * np.cos((s_th - 0.12) / 2.0)),
                         xytext=(s_th, -2.0 * np.cos(s_th / 2.0)),
                         arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.52", color=RED, lw=2.2), zorder=7)

    # Mark equilibrium points
    for c_th in [-2 * np.pi, 0, 2 * np.pi]:
        ax2_sub.plot(c_th, 0, 'o', color=BLUE, markersize=8, markeredgecolor=NAVY, markeredgewidth=1.6, zorder=8)

    # Saddle / Critical points (theta = -pi and +pi)
    ax2_sub.plot(-np.pi, 0, 's', color=RED, markersize=8, markeredgecolor=NAVY, markeredgewidth=1.6, zorder=8)
    ax2_sub.text(-np.pi, -0.42, r"$(-\pi, 0)$", fontsize=11.5, color=RED, weight='bold', ha='center',
                 bbox=dict(boxstyle="round,pad=0.18", facecolor="#ffffff", edgecolor="#fecaca", lw=0.8), zorder=9)

    ax2_sub.plot(np.pi, 0, 's', color=RED, markersize=8, markeredgecolor=NAVY, markeredgewidth=1.6, zorder=8)
    ax2_sub.text(np.pi, -0.42, r"$(\pi, 0)$", fontsize=11.5, color=RED, weight='bold', ha='center',
                 bbox=dict(boxstyle="round,pad=0.18", facecolor="#ffffff", edgecolor="#fecaca", lw=0.8), zorder=9)

    # Coordinate ticks
    ax2_sub.set_xticks([-2 * np.pi, -np.pi, 0, np.pi, 2 * np.pi])
    ax2_sub.set_xticklabels([r"$-2\pi$", r"$-\pi$", r"$0$", r"$\pi$", r"$2\pi$"], fontsize=12.5, color=NAVY, weight='bold')
    ax2_sub.set_yticks([-2, -1, 0, 1, 2])
    ax2_sub.set_yticklabels([r"$-2$", r"$-1$", r"$0$", r"$1$", r"$2$"], fontsize=12.5, color=NAVY, weight='bold')
    ax2_sub.set_xlabel(r"$\theta$ (rad)", fontsize=13.5, color=NAVY, weight='bold', labelpad=4)
    # Dimensionless normalized angular velocity label placed horizontally cleanly inside the card panel
    ax2_sub.text(-0.125, 0.50, r"$\frac{\omega}{\sqrt{g/\ell}}$", transform=ax2_sub.transAxes,
                 fontsize=23.0, color=NAVY, weight='bold', ha='center', va='center')

    # In-plot labels for the 3 regimes
    # Rotation badge (upper center)
    ax2_sub.text(0, 2.38, r"$\mathbf{Rotation}\;(E > 2mg\ell)$", fontsize=11.5, color=EMERALD, weight='bold', ha='center',
                 bbox=dict(boxstyle="round,pad=0.25", facecolor="#ecfdf5", edgecolor="#a7f3d0", lw=1.1), zorder=9)

    # Separatrix badge (placed clearly on the separatrix curve at theta = -0.85 pi)
    ax2_sub.text(-0.85 * np.pi, 1.82, r"$\mathbf{Separatrix}\;(E = 2mg\ell)$", fontsize=11.5, color=RED, weight='bold', ha='center',
                 bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor="#fecaca", lw=1.1), zorder=9)

    # Libration badge (center loop)
    ax2_sub.text(0, 0.45, r"$\mathbf{Libration}\;(E < 2mg\ell)$", fontsize=11.5, color=BLUE, weight='bold', ha='center',
                 bbox=dict(boxstyle="round,pad=0.25", facecolor="#eff6ff", edgecolor="#bfdbfe", lw=1.1), zorder=9)

    # =============================================================
    # PANEL 3: SEPARATRIX & ROTATION CONFIGURATIONS (THETA = PI)
    # =============================================================
    ax3.set_facecolor(CARD_BG)
    ax3.set_xlim(-1.65, 1.65)
    ax3.set_ylim(-1.85, 1.55)
    ax3.axis('off')

    card3 = patches.FancyBboxPatch((-1.58, -1.78), 3.16, 3.28,
                                   boxstyle="round,pad=0.03,rounding_size=0.10",
                                   facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.2, zorder=0)
    ax3.add_patch(card3)

    ax3.text(0, 1.30, "3. Separatrix & Rotation", fontsize=16.5, weight='bold', color=NAVY, ha='center')
    ax3.text(0, 1.08, "Inverted Equilibrium & Rotation", fontsize=13.0, weight='bold', color=DARK_SLATE, ha='center')

    # Stand / base for inverted pendulum shifted up
    pivot_y3 = -0.02
    ax3.plot([-0.70, 0.70], [pivot_y3, pivot_y3], color=NAVY, lw=2.5, zorder=2)
    for x_h in np.linspace(-0.64, 0.64, 11):
        ax3.plot([x_h, x_h + 0.08], [pivot_y3, pivot_y3 - 0.09], color=SLATE, lw=1.2, zorder=2)
    ax3.plot(0, pivot_y3, 'o', color=NAVY, markersize=8, zorder=4)

    # Vertical reference line
    ax3.plot([0, 0], [pivot_y3 - 0.45, pivot_y3 + 1.15], color=LIGHT_SLATE, linestyle='--', lw=1.4, zorder=1)

    # Upright inverted pendulum configuration (theta = pi, E = 2mg*l)
    rod_len3_y = 0.82
    bob_x3 = 0
    bob_y3 = pivot_y3 + rod_len3_y
    ax3.plot([0, bob_x3], [pivot_y3, bob_y3], color=RED, lw=3.0, zorder=4)
    bob_upright = patches.Circle((bob_x3, bob_y3), 0.12, facecolor='#f87171', edgecolor=RED, lw=2.0, zorder=5)
    ax3.add_patch(bob_upright)

    ax3.text(0, bob_y3 + 0.16, r"$\mathbf{Inverted\ equilibrium:}\;\theta = \pi,\;\omega = 0$", fontsize=12.0, color=RED, weight='bold', ha='center')
    ax3.text(0.14, pivot_y3 + rod_len3_y/2, r"$\ell$", fontsize=13.5, color=SLATE, style='italic')

    # Circular rotation orbit path (dashed green circle with true Euclidean aspect)
    r_rot_y = rod_len3_y
    circ_angles = np.linspace(0, 2*np.pi, 120)
    ax3.plot((r_rot_y * np.cos(circ_angles)) * aspect_scale, pivot_y3 + r_rot_y * np.sin(circ_angles),
             color='#86efac', lw=1.8, linestyle=':', zorder=2)

    # Curved rotation arrows showing continuous 360 deg motion over the top
    arr_rot_angles = np.linspace(np.pi/4, 3*np.pi/4, 40)
    xs_rot = (r_rot_y * np.cos(arr_rot_angles)) * aspect_scale
    ys_rot = pivot_y3 + r_rot_y * np.sin(arr_rot_angles)
    # Clockwise rotation: from right (x > 0) to left (x < 0) over the top
    arr_rot = patches.FancyArrowPatch(path=mpath.Path(np.column_stack([xs_rot[::-1], ys_rot[::-1]])),
                                       arrowstyle='->,head_width=4.5,head_length=6.5',
                                       color=EMERALD, lw=2.4, zorder=6)
    ax3.add_patch(arr_rot)

    ax3.text(1.08, pivot_y3 + 0.32, "Rotation\n" + r"($E > 2mg\ell$)",
             fontsize=12.0, color=EMERALD, weight='bold', ha='center',
             bbox=dict(boxstyle="round,pad=0.22", facecolor="#ecfdf5", edgecolor="#a7f3d0", lw=1.0), zorder=7)

    # Energy badges
    ax3.text(0, -0.42, r"$\mathbf{Separatrix:}\; E = 2mg\ell$", fontsize=12.5, color=RED, weight='bold', ha='center',
             bbox=dict(boxstyle="round,pad=0.25", facecolor="#fff1f2", edgecolor="#fecaca", lw=1.1))

    ax3.text(0, -0.74, r"$\mathbf{Rotation:}\; E > 2mg\ell$", fontsize=12.5, color=EMERALD, weight='bold', ha='center',
             bbox=dict(boxstyle="round,pad=0.25", facecolor="#ecfdf5", edgecolor="#a7f3d0", lw=1.1))

    # Precise, legible bottom text cleanly inside card
    panel3_text = (
        "At critical energy, the separatrix\n"
        "approaches the inverted equilibrium\n"
        "asymptotically. Above the critical energy,\n"
        "the pendulum rotates continuously."
    )
    ax3.text(0, -1.40, panel3_text,
             fontsize=12.5, weight='bold', color=NAVY, ha='center', va='center', linespacing=1.30)

    plt.savefig(output_path, dpi=240, bbox_inches='tight', pad_inches=0.35, facecolor='#ffffff')
    plt.close()
    print(f"[OK] Generated {output_path}")
    return output_path

if __name__ == "__main__":
    create_figure()
