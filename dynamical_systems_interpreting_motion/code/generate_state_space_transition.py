#!/usr/bin/env python3
"""
Generate infographic:
"From Physical Motion to State Space and Vector Fields"
Three-stage conceptual diagram:
1. Physical Pendulum (θ, ω)
2. State Point in Phase Plane (θ, ω)
3. Local Vector Field and Trajectory Evolution
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "state_space_transition.png"

def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Wide figure with 3 panels and generous inter-panel clearance
    fig_w = 18.5
    fig_h = 6.85
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    card_in = 5.00
    w_card = card_in / fig_w
    h_card = card_in / fig_h
    y_bottom = 0.065

    left_m = 0.40 / fig_w
    gap = 1.35 / fig_w

    x1 = left_m
    x2 = x1 + w_card + gap
    x3 = x2 + w_card + gap
    c_gap1 = x1 + w_card + gap / 2.0
    c_gap2 = x2 + w_card + gap / 2.0

    # Styling colors
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#475569'
    LIGHT_SLATE = '#94a3b8'
    BLUE = '#2563eb'
    RED = '#dc2626'
    EMERALD = '#059669'
    CARD_BG = '#f8fafc'
    BORDER_COLOR = '#cbd5e1'

    # Title badge snugly wrapping just the title text with same background as panels
    fig.text(0.5, 0.895,
             r"From Physical Motion to State Space:   $\mathbf{Physical\ State} \;\longrightarrow\; (\theta, \omega) \;\longrightarrow\; \mathbf{Trajectory\ in\ State\ Space}$",
             fontsize=17.5, weight='bold', color=NAVY, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.30",
                       facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1.2))

    ax1 = fig.add_axes([x1, y_bottom, w_card, h_card])
    ax2 = fig.add_axes([x2, y_bottom, w_card, h_card])
    ax3 = fig.add_axes([x3, y_bottom, w_card, h_card])

    # Pendulum state parameters: theta = 0.78 rad (~45 deg), omega = 0.70 rad/s
    theta_val = 0.78
    omega_val = 0.70
    g_over_l = 1.0

    # =============================================================
    # PANEL 1: PHYSICAL PENDULUM
    # =============================================================
    ax1.set_facecolor(CARD_BG)
    ax1.set_xlim(-1.5, 1.5)
    ax1.set_ylim(-1.6, 1.4)
    ax1.axis('off')

    # Card background
    card1 = patches.FancyBboxPatch((-1.45, -1.55), 2.9, 2.9,
                                   boxstyle="round,pad=0.03,rounding_size=0.08",
                                   facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.2, zorder=0)
    ax1.add_patch(card1)

    # Panel header
    ax1.text(0, 1.18, "1. Physical System", fontsize=16.5, weight='bold', color=NAVY, ha='center')
    ax1.text(0, 0.95, r"Angle $\theta$, angular velocity $\omega$", fontsize=13.0, weight='bold', color=DARK_SLATE, ha='center')

    # Ceiling mount
    pivot_y = 0.55
    ax1.plot([-0.65, 0.65], [pivot_y, pivot_y], color=NAVY, lw=2.5, zorder=2)
    for x_h in np.linspace(-0.6, 0.6, 11):
        ax1.plot([x_h, x_h + 0.08], [pivot_y, pivot_y + 0.10], color=SLATE, lw=1.2, zorder=2)

    # Pivot point
    ax1.plot(0, pivot_y, 'o', color=NAVY, markersize=8, zorder=4)

    # Vertical reference line
    ax1.plot([0, 0], [pivot_y, pivot_y - 1.45], color=LIGHT_SLATE, linestyle='--', lw=1.4, zorder=1)

    # Pendulum arm
    rod_len = 1.15
    bob_x = rod_len * np.sin(theta_val)
    bob_y = pivot_y - rod_len * np.cos(theta_val)
    ax1.plot([0, bob_x], [pivot_y, bob_y], color=NAVY, lw=3.0, zorder=3)

    # Angle arc
    arc_angles = np.linspace(-np.pi/2, -np.pi/2 + theta_val, 40)
    r_arc = 0.42
    ax1.plot(r_arc * np.cos(arc_angles), pivot_y + r_arc * np.sin(arc_angles), color=BLUE, lw=2.0, zorder=3)
    ax1.text(0.18, pivot_y - 0.48, r"$\theta$", fontsize=16, color=BLUE, weight='bold', zorder=5)

    # Bob mass
    bob_patch = patches.Circle((bob_x, bob_y), 0.14, facecolor=BLUE, edgecolor=NAVY, lw=2.0, zorder=5)
    ax1.add_patch(bob_patch)
    ax1.text(bob_x + 0.20, bob_y - 0.02, r"$m$", fontsize=14, color=NAVY, weight='bold', zorder=5)

    # Curved arrow for angular velocity omega = dot(theta) around pivot
    r_om = 0.72
    a_start = -np.pi/2 + 0.45
    a_end = -np.pi/2 + theta_val + 0.30
    angles_om = np.linspace(a_start, a_end, 50)
    xs_om = r_om * np.cos(angles_om)
    ys_om = pivot_y + r_om * np.sin(angles_om)
    arrow_om = patches.FancyArrowPatch(path=mpath.Path(np.column_stack([xs_om, ys_om])),
                                       arrowstyle='->,head_width=5.5,head_length=8.0',
                                       color=RED, lw=2.6, zorder=6)
    ax1.add_patch(arrow_om)

    # Angular velocity label placed at tip of curved arrow
    ax1.text(xs_om[-1] + 0.08, ys_om[-1] + 0.06, r"$\omega = \dot{\theta}$",
             fontsize=14, color=RED, weight='bold', zorder=6)

    # Arm length symbol
    ax1.text(bob_x/2 - 0.18, (pivot_y + bob_y)/2 + 0.04, r"$\ell$", fontsize=15, color=SLATE, style='italic', zorder=5)

    # Gravity symbol
    ax1.annotate('', xy=(-0.95, pivot_y - 0.7), xytext=(-0.95, pivot_y - 0.3),
                 arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.4",
                                 color=SLATE, lw=2.0), zorder=4)
    ax1.text(-0.95, pivot_y - 0.85, r"$\mathbf{g}$", fontsize=14, color=SLATE, weight='bold', ha='center', zorder=4)

    ax1.text(0, -1.38, "Physical state of the pendulum", fontsize=13.5, weight='bold', color=NAVY, ha='center')

    # =============================================================
    # PANEL 2: STATE POINT IN PHASE PLANE
    # =============================================================
    ax2.set_facecolor(CARD_BG)
    ax2.set_xlim(-1.5, 1.5)
    ax2.set_ylim(-1.6, 1.4)
    ax2.axis('off')

    card2 = patches.FancyBboxPatch((-1.45, -1.55), 2.9, 2.9,
                                   boxstyle="round,pad=0.03,rounding_size=0.08",
                                   facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.2, zorder=0)
    ax2.add_patch(card2)

    # Panel header
    ax2.text(0, 1.18, "2. State Space (Phase Plane)", fontsize=16.5, weight='bold', color=NAVY, ha='center')
    ax2.text(0, 0.95, r"Every state is a single point $(\theta, \omega)$", fontsize=13.0, weight='bold', color=DARK_SLATE, ha='center')

    # Axes shifted to lower-center
    ax2.annotate('', xy=(1.25, -0.1), xytext=(-1.25, -0.1),
                 arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", color=SLATE, lw=1.6), zorder=1)
    ax2.annotate('', xy=(0, 0.82), xytext=(0, -1.1),
                 arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", color=SLATE, lw=1.6), zorder=1)

    ax2.text(1.28, -0.22, r"$\theta$", fontsize=15, color=NAVY, weight='bold')
    ax2.text(0.10, 0.82, r"$\omega$", fontsize=15, color=NAVY, weight='bold')
    ax2.text(-0.14, -0.24, r"$0$", fontsize=12, color=SLATE)

    # Origin equilibrium point
    ax2.plot(0, -0.1, 'o', color=SLATE, markersize=5, zorder=2)

    # State point coordinates
    pt_x = theta_val * 1.05
    pt_y = -0.1 + omega_val * 0.95

    # Dashed projections
    ax2.plot([pt_x, pt_x], [-0.1, pt_y], color=LIGHT_SLATE, linestyle=':', lw=1.8, zorder=2)
    ax2.plot([0, pt_x], [pt_y, pt_y], color=LIGHT_SLATE, linestyle=':', lw=1.8, zorder=2)

    # Axis tick callouts
    ax2.text(pt_x, -0.32, r"$\theta$", fontsize=14, color=BLUE, weight='bold', ha='center')
    ax2.text(-0.20, pt_y, r"$\omega$", fontsize=14, color=RED, weight='bold', va='center', ha='right')

    # State point
    ax2.plot(pt_x, pt_y, 'o', color=BLUE, markersize=10, markeredgecolor=NAVY, markeredgewidth=1.8, zorder=5)

    # Point label box
    ax2.text(pt_x + 0.12, pt_y + 0.16, r"$\mathbf{x} = (\theta, \omega)$",
             fontsize=14, color=NAVY, weight='bold',
             bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor="#cbd5e1", lw=1.0),
             zorder=6)

    ax2.text(0, -1.38, "Uniquely specifies the instantaneous state", fontsize=13.0, weight='bold', color=NAVY, ha='center')

    # =============================================================
    # PANEL 3: VECTOR FIELD & TRAJECTORY
    # =============================================================
    ax3.set_facecolor(CARD_BG)
    ax3.set_xlim(-1.5, 1.5)
    ax3.set_ylim(-1.6, 1.4)
    ax3.axis('off')

    card3 = patches.FancyBboxPatch((-1.45, -1.55), 2.9, 2.9,
                                   boxstyle="round,pad=0.03,rounding_size=0.08",
                                   facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.2, zorder=0)
    ax3.add_patch(card3)

    # Panel header
    ax3.text(0, 1.18, "3. Vector Field & Flow", fontsize=16.5, weight='bold', color=NAVY, ha='center')
    ax3.text(0, 0.95, r"Equations prescribe state-space velocity $(\dot{\theta}, \dot{\omega})$", fontsize=13.0, weight='bold', color=DARK_SLATE, ha='center')

    # Coordinate axes
    ax3.annotate('', xy=(1.25, -0.1), xytext=(-1.25, -0.1),
                 arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", color=SLATE, lw=1.6), zorder=1)
    ax3.annotate('', xy=(0, 0.82), xytext=(0, -1.1),
                 arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", color=SLATE, lw=1.6), zorder=1)

    ax3.text(1.28, -0.22, r"$\theta$", fontsize=15, color=NAVY, weight='bold')
    ax3.text(0.10, 0.82, r"$\omega$", fontsize=15, color=NAVY, weight='bold')

    # Background vector field arrows
    grid_th = np.linspace(-1.15, 1.15, 9)
    grid_om = np.linspace(-0.95, 0.75, 8)
    TH, OM = np.meshgrid(grid_th, grid_om)
    U_f = OM
    V_f = -g_over_l * np.sin(TH)
    mag = np.sqrt(U_f**2 + V_f**2) + 1e-6

    # Plot arrows scaled
    ax3.quiver(TH, OM - 0.1, U_f / mag, V_f / mag,
               color='#94a3b8', alpha=0.45, width=0.0042, scale=24,
               headwidth=3.2, headlength=4.0, zorder=2)

    # Local trajectory through (theta_val, omega_val)
    from scipy.integrate import odeint
    def pend_ode(state, t):
        th, om = state
        return [om, -g_over_l * np.sin(th)]

    t_tr = np.linspace(-0.65, 1.1, 200)
    sol_tr = odeint(pend_ode, [theta_val, omega_val], t_tr)

    # Plot green trajectory
    ax3.plot(sol_tr[:, 0] * 1.05, -0.1 + sol_tr[:, 1] * 0.95, color=EMERALD, lw=3.0, alpha=0.9, zorder=4)

    # Arrow on trajectory
    idx_a = 135
    ax3.annotate('', xy=(sol_tr[idx_a+3, 0] * 1.05, -0.1 + sol_tr[idx_a+3, 1] * 0.95),
                 xytext=(sol_tr[idx_a, 0] * 1.05, -0.1 + sol_tr[idx_a, 1] * 0.95),
                 arrowprops=dict(arrowstyle="->,head_width=0.45,head_length=0.6", color=EMERALD, lw=2.5),
                 zorder=5)

    # State point
    ax3.plot(pt_x, pt_y, 'o', color=BLUE, markersize=10, markeredgecolor=NAVY, markeredgewidth=1.8, zorder=6)

    # Tangent vector f(x) = (omega, -sin(theta))
    f_u = omega_val * 1.05
    f_v = -g_over_l * np.sin(theta_val) * 0.95
    norm_f = np.sqrt(f_u**2 + f_v**2)
    f_scale = 0.38 / norm_f

    ax3.annotate('', xy=(pt_x + f_u * f_scale, pt_y + f_v * f_scale),
                 xytext=(pt_x, pt_y),
                 arrowprops=dict(arrowstyle="->,head_width=0.42,head_length=0.65", color=RED, lw=3.2),
                 zorder=10)

    # Vector label callout (placed with clean clearance below the red arrow tip)
    ax3.text(1.39, 0.05,
             r"$(\dot{\theta}, \dot{\omega}) = \left(\omega, -\frac{g}{\ell}\sin\theta\right)$",
             fontsize=14.5, color=RED, weight='bold', ha='right', va='center',
             bbox=dict(boxstyle="round,pad=0.28", facecolor="#ffffff", edgecolor="#fecaca", lw=1.2),
             zorder=8)



    # Trajectory text
    ax3.text(sol_tr[0, 0] * 1.05 - 0.05, -0.1 + sol_tr[0, 1] * 0.95 + 0.12, "Trajectory",
             fontsize=12, color=EMERALD, weight='bold', zorder=8)

    ax3.text(0, -1.38, "Vector field guides the trajectory", fontsize=13.5, weight='bold', color=NAVY, ha='center')

    # =============================================================
    # INTER-PANEL TRANSITION BRIDGES
    # =============================================================
    y_box = y_bottom + h_card * 0.52
    y_arr = y_bottom + h_card * 0.38

    # Bridge 1: Between Panel 1 & Panel 2
    fig.text(c_gap1, y_box, "Map\nCoordinates", ha="center", va="center", fontsize=12.5,
             color='#1e293b', weight='bold',
             bbox=dict(boxstyle="round,pad=0.38", facecolor="#ffffff", edgecolor="#cbd5e1", lw=1.2))
    fig.text(c_gap1, y_arr, r"$\longrightarrow$", ha="center", va="center", fontsize=22, color=SLATE)

    # Bridge 2: Between Panel 2 & Panel 3
    fig.text(c_gap2, y_box, "Differential\nEquations", ha="center", va="center", fontsize=12.5,
             color='#1e293b', weight='bold',
             bbox=dict(boxstyle="round,pad=0.38", facecolor="#ffffff", edgecolor="#cbd5e1", lw=1.2))
    fig.text(c_gap2, y_arr, r"$\longrightarrow$", ha="center", va="center", fontsize=22, color=SLATE)

    plt.savefig(output_path, dpi=240, bbox_inches='tight', pad_inches=0.35, facecolor='#ffffff')
    plt.close()
    print(f"[OK] Generated {output_path}")
    return output_path

if __name__ == "__main__":
    create_figure()
