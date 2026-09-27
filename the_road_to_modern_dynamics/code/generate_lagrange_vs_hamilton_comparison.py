#!/usr/bin/env python3
r"""
Generate figure:
"Lagrangian and Hamiltonian Mechanics: Two Formulations of the Same Dynamics"

Key updates:
1. Exact, clearly non-elliptical nonlinear pendulum phase plane trajectory (amplitude ~118°).
2. Bullet refinement: "Can incorporate geometrical constraints into generalized coordinates".
3. Vertical alignment across both columns (headers, state variables, equations, bullets, and example boxes).
4. Generous vertical space and padding inside "Fundamental Equations" boxes with clean margins above/below formulas.
5. Large, crystal-clear, bold math typography matching publication standards.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "lagrange_vs_hamilton_comparison.png"

def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Clean, robust mathtext configuration with DejaVu Sans & bold weight
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    })

    # 16:9 widescreen canvas, high resolution for Medium readability
    fig_w = 17.6
    fig_h = 10.4
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Editorial Color Palette
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#334155'
    LIGHT_SLATE = '#64748b'
    MUTED_BORDER = '#cbd5e1'
    CARD_BG = '#f8fafc'
    WHITE = '#ffffff'
    
    BLUE = '#2563eb'
    BLUE_LIGHT = '#eff6ff'
    BLUE_BORDER = '#93c5fd'
    
    PURPLE = '#7c3aed'
    PURPLE_LIGHT = '#f5f3ff'
    PURPLE_BORDER = '#c4b5fd'

    # Title badge at top
    fig.text(0.5, 0.952,
             "Lagrangian and Hamiltonian Mechanics: Two Formulations of the Same Dynamics",
             fontsize=21.0, weight='bold', color=NAVY, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.25",
                       facecolor=CARD_BG, edgecolor=MUTED_BORDER, lw=1.3))

    # Column geometry
    col_w = 0.452
    col_h = 0.730
    col_y = 0.180
    col1_x = 0.032
    col2_x = 0.516

    ax_left = fig.add_axes([col1_x, col_y, col_w, col_h])
    ax_right = fig.add_axes([col2_x, col_y, col_w, col_h])

    for ax in (ax_left, ax_right):
        ax.set_facecolor(CARD_BG)
        ax.set_xlim(-0.15, 10.15)
        ax.set_ylim(-0.15, 10.15)
        ax.axis('off')

    # Card background outlines with rounded corners (fully within visible axes bounds)
    card_left = patches.FancyBboxPatch((0.0, 0.0), 10.0, 10.0,
                                       boxstyle="round,pad=0.0,rounding_size=0.25",
                                       facecolor=CARD_BG, edgecolor=BLUE_BORDER, lw=1.8, zorder=0)
    ax_left.add_patch(card_left)

    card_right = patches.FancyBboxPatch((0.0, 0.0), 10.0, 10.0,
                                        boxstyle="round,pad=0.0,rounding_size=0.25",
                                        facecolor=CARD_BG, edgecolor=PURPLE_BORDER, lw=1.8, zorder=0)
    ax_right.add_patch(card_right)

    # =========================================================================
    # ROW 1: HEADER BADGES (y = 8.85, h = 0.95)
    # =========================================================================
    pill_h1 = patches.FancyBboxPatch((0.40, 8.85), 9.20, 0.95,
                                     boxstyle="round,pad=0.03,rounding_size=0.20",
                                     facecolor=BLUE_LIGHT, edgecolor=BLUE, lw=1.5)
    ax_left.add_patch(pill_h1)
    ax_left.text(5.0, 9.46, "LAGRANGIAN MECHANICS", fontsize=18.0, weight='bold', color=BLUE, ha='center', va='center')
    ax_left.text(5.0, 9.06, "Coordinates and Velocities", fontsize=14.0, weight='bold', color=SLATE, ha='center', va='center')

    pill_h2 = patches.FancyBboxPatch((0.40, 8.85), 9.20, 0.95,
                                     boxstyle="round,pad=0.03,rounding_size=0.20",
                                     facecolor=PURPLE_LIGHT, edgecolor=PURPLE, lw=1.5)
    ax_right.add_patch(pill_h2)
    ax_right.text(5.0, 9.46, "HAMILTONIAN MECHANICS", fontsize=18.0, weight='bold', color=PURPLE, ha='center', va='center')
    ax_right.text(5.0, 9.06, "Phase Space • Coordinates and Conjugate Momenta", fontsize=14.0, weight='bold', color=SLATE, ha='center', va='center')

    # =========================================================================
    # ROW 2: STATE VARIABLES BOXES (y = 7.78, h = 0.90)
    # =========================================================================
    pill_var1 = patches.FancyBboxPatch((0.40, 7.78), 9.20, 0.90,
                                       boxstyle="round,pad=0.03,rounding_size=0.18",
                                       facecolor=WHITE, edgecolor=MUTED_BORDER, lw=1.3)
    ax_left.add_patch(pill_var1)
    ax_left.text(1.80, 8.23, "State Variables:", fontsize=14.5, weight='bold', color=DARK_SLATE, ha='center', va='center')
    ax_left.text(5.95, 8.23, r"$(q_1, \ldots, q_n, \; \dot{q}_1, \ldots, \dot{q}_n) \quad \mathbf{or} \quad (q_i, \dot{q}_i)$",
                 fontsize=17.5, weight='bold', color=NAVY, ha='center', va='center')

    pill_var2 = patches.FancyBboxPatch((0.40, 7.78), 9.20, 0.90,
                                       boxstyle="round,pad=0.03,rounding_size=0.18",
                                       facecolor=WHITE, edgecolor=MUTED_BORDER, lw=1.3)
    ax_right.add_patch(pill_var2)
    ax_right.text(1.80, 8.23, "State Variables:", fontsize=14.5, weight='bold', color=DARK_SLATE, ha='center', va='center')
    ax_right.text(5.95, 8.23, r"$(q_1, \ldots, q_n, \; p_1, \ldots, p_n) \quad \mathbf{or} \quad (q_i, p_i)$",
                  fontsize=17.5, weight='bold', color=NAVY, ha='center', va='center')

    # =========================================================================
    # ROW 3: FUNDAMENTAL EQUATIONS BOXES (y = 5.40, h = 2.18)
    # Generous headroom below box to bullets (0.60 units) and balanced inner padding
    # =========================================================================
    box_flow1 = patches.FancyBboxPatch((0.40, 5.40), 9.20, 2.18,
                                       boxstyle="round,pad=0.03,rounding_size=0.18",
                                       facecolor=WHITE, edgecolor=MUTED_BORDER, lw=1.3)
    ax_left.add_patch(box_flow1)
    ax_left.text(0.70, 7.28, "Fundamental Equations:", fontsize=13.5, weight='bold', color=DARK_SLATE)
    
    # Lagrangian & Euler-Lagrange equations
    ax_left.text(5.0, 6.66, r"$L(q_i, \dot{q}_i, t) = T - V$",
                 fontsize=19.0, weight='bold', color=NAVY, ha='center', va='center')
    ax_left.text(5.0, 5.84, r"$\frac{d}{dt}\left(\frac{\partial L}{\partial \dot{q}_i}\right) - \frac{\partial L}{\partial q_i} = 0$",
                 fontsize=20.5, weight='bold', color=BLUE, ha='center', va='center')

    box_flow2 = patches.FancyBboxPatch((0.40, 5.40), 9.20, 2.18,
                                       boxstyle="round,pad=0.03,rounding_size=0.18",
                                       facecolor=WHITE, edgecolor=MUTED_BORDER, lw=1.3)
    ax_right.add_patch(box_flow2)
    ax_right.text(0.70, 7.28, "Fundamental Equations:", fontsize=13.5, weight='bold', color=DARK_SLATE)
    
    # Top line: conjugate momentum and Legendre transform
    ax_right.text(5.0, 6.66, r"$p_i = \frac{\partial L}{\partial \dot{q}_i}, \qquad H(q_i, p_i, t) = \sum_i p_i \dot{q}_i - L$",
                  fontsize=18.0, weight='bold', color=NAVY, ha='center', va='center')
    # Bottom line: Hamilton's canonical equations
    ax_right.text(5.0, 5.84, r"$\dot{q}_i = \frac{\partial H}{\partial p_i}, \qquad \dot{p}_i = -\frac{\partial H}{\partial q_i}$",
                  fontsize=20.5, weight='bold', color=PURPLE, ha='center', va='center')

    # =========================================================================
    # ROW 4: KEY CHARACTERISTICS BULLETS (y = 4.80, 4.24, 3.68)
    # Hanging indent with 100% mathematical vertical alignment between line 1 & line 2
    # Generous 0.60 units headroom beneath Fundamental Equations box
    # =========================================================================
    bullets_left = [
        ("Coordinates and velocities specify the", "instantaneous state of motion"),
        ("Yields one 2nd-order differential equation", "per degree of freedom"),
        ("Can incorporate geometrical constraints", "into generalized coordinates")
    ]

    bullets_right = [
        ("Coordinates and momenta specify a point", "in a 2n-dimensional phase space"),
        ("Yields two coupled 1st-order differential", "equations per degree of freedom"),
        ("Natural for studying trajectories and flows", "in phase space")
    ]

    y_starts = [4.86, 4.30, 3.74]
    dy_line = 0.24

    for (l1, l2), y_top in zip(bullets_left, y_starts):
        ax_left.text(0.60, y_top, "•", fontsize=15.0, weight='bold', color=DARK_SLATE, va='center')
        ax_left.text(0.92, y_top, l1, fontsize=12.5, weight='bold', color=DARK_SLATE, va='center')
        ax_left.text(0.92, y_top - dy_line, l2, fontsize=12.5, weight='bold', color=DARK_SLATE, va='center')

    for (l1, l2), y_top in zip(bullets_right, y_starts):
        ax_right.text(0.60, y_top, "•", fontsize=15.0, weight='bold', color=DARK_SLATE, va='center')
        ax_right.text(0.92, y_top, l1, fontsize=12.5, weight='bold', color=DARK_SLATE, va='center')
        ax_right.text(0.92, y_top - dy_line, l2, fontsize=12.5, weight='bold', color=DARK_SLATE, va='center')

    # =========================================================================
    # ROW 5: PENDULUM MINI-EXAMPLE CARDS (y = 0.16, h = 2.80)
    # Lowered to provide generous headroom (~0.51 units) beneath the bullets
    # =========================================================================
    x_align = 0.75

    # Left Card
    box_ex1 = patches.FancyBboxPatch((0.40, 0.16), 9.20, 2.80,
                                     boxstyle="round,pad=0.03,rounding_size=0.18",
                                     facecolor=WHITE, edgecolor=MUTED_BORDER, lw=1.3)
    ax_left.add_patch(box_ex1)
    ax_left.text(0.70, 2.76, "Example: The Simple Pendulum (1 DOF)", fontsize=13.5, weight='bold', color=DARK_SLATE)

    # Left half: equations (vertically aligned at x_align)
    ax_left.text(x_align, 2.34, r"$\mathbf{Coordinate:}\quad q = \theta$", fontsize=15.5, weight='bold', color=NAVY, ha='left', va='center')
    ax_left.text(x_align, 1.78, r"$L = \frac{1}{2}ml^2\dot{\theta}^2 - mgl(1-\cos\theta)$", fontsize=15.5, weight='bold', color=DARK_SLATE, ha='left', va='center')
    
    # Sleek blue badge
    pill_l = patches.FancyBboxPatch((x_align - 0.14, 0.84), 3.10, 0.60,
                                    boxstyle="round,pad=0.03,rounding_size=0.14",
                                    facecolor=BLUE_LIGHT, edgecolor=BLUE_BORDER, lw=1.2)
    ax_left.add_patch(pill_l)
    ax_left.text(x_align, 1.14, r"$\ddot{\theta} + \frac{g}{l}\sin\theta = 0$", fontsize=18.5, weight='bold', color=BLUE, ha='left', va='center')
    ax_left.text(x_align, 0.44, "One 2nd-order non-linear ODE", fontsize=13.0, weight='bold', color=LIGHT_SLATE, ha='left', va='center')

    # Right half: Inset Pendulum Sketch
    # Pivot at (7.30, 2.26)
    p_x0, p_y0 = 7.30, 2.26
    length = 1.40
    theta_deg = 32.0
    theta_rad = np.radians(theta_deg)
    bob_x = p_x0 + length * np.sin(theta_rad)
    bob_y = p_y0 - length * np.cos(theta_rad)

    # Ceiling bracket
    ax_left.plot([p_x0 - 0.70, p_x0 + 0.70], [p_y0, p_y0], color=SLATE, lw=2.5)
    for hx in np.linspace(p_x0 - 0.60, p_x0 + 0.60, 5):
        ax_left.plot([hx, hx + 0.18], [p_y0, p_y0 + 0.18], color=LIGHT_SLATE, lw=1.2)

    # Vertical reference dashed line
    ax_left.plot([p_x0, p_x0], [p_y0, p_y0 - 1.55], color=LIGHT_SLATE, lw=1.5, ls='--')

    # Angle arc (from vertical -90 deg to rod (-90 + theta_deg))
    arc_rad = 0.78
    arc_ang = np.linspace(-90, -90 + theta_deg, 40)
    ax_left.plot(p_x0 + arc_rad * np.cos(np.radians(arc_ang)),
                 p_y0 + arc_rad * np.sin(np.radians(arc_ang)),
                 color=BLUE, lw=2.0)
    
    # Place theta at the middle of the arc
    mid_theta_deg = -90 + (theta_deg / 2.0)
    mid_theta_rad = np.radians(mid_theta_deg)
    label_rad = arc_rad + 0.25
    th_x = p_x0 + label_rad * np.cos(mid_theta_rad)
    th_y = p_y0 + label_rad * np.sin(mid_theta_rad)
    ax_left.text(th_x, th_y, r"$\theta$", fontsize=17.5, weight='bold', color=BLUE, ha='center', va='center')

    # Rod
    ax_left.plot([p_x0, bob_x], [p_y0, bob_y], color=SLATE, lw=2.8)

    # Pivot pin
    pivot_dot = plt.Circle((p_x0, p_y0), 0.08, facecolor=NAVY, edgecolor=WHITE, lw=1.5, zorder=4)
    ax_left.add_patch(pivot_dot)

    # Pendulum bob
    bob_circ = plt.Circle((bob_x, bob_y), 0.22, facecolor=BLUE, edgecolor=NAVY, lw=1.8, zorder=5)
    ax_left.add_patch(bob_circ)
    ax_left.text(bob_x + 0.36, bob_y, r"$m$", fontsize=15.5, weight='bold', color=DARK_SLATE, va='center')
    ax_left.text(7.30, 0.44, "Configuration: angle $\\theta$", fontsize=13.0, weight='bold', color=DARK_SLATE, ha='center', va='center')

    # Right Card
    box_ex2 = patches.FancyBboxPatch((0.40, 0.16), 9.20, 2.80,
                                     boxstyle="round,pad=0.03,rounding_size=0.18",
                                     facecolor=WHITE, edgecolor=MUTED_BORDER, lw=1.3)
    ax_right.add_patch(box_ex2)
    ax_right.text(0.70, 2.76, "Example: The Simple Pendulum (2D Phase Space)", fontsize=13.5, weight='bold', color=DARK_SLATE)

    # Left half: equations (vertically aligned at x_align)
    ax_right.text(x_align, 2.34, r"$(\theta, \dot{\theta}) \;\longrightarrow\; (\theta, p_\theta), \quad p_\theta = ml^2\dot{\theta}$",
                  fontsize=14.5, weight='bold', color=NAVY, ha='left', va='center')
    ax_right.text(x_align, 1.78, r"$H(\theta, p_\theta) = \frac{p_\theta^2}{2ml^2} + mgl(1-\cos\theta)$",
                  fontsize=14.5, weight='bold', color=DARK_SLATE, ha='left', va='center')
    
    # Sleek purple badge
    pill_r = patches.FancyBboxPatch((x_align - 0.14, 0.84), 4.70, 0.60,
                                    boxstyle="round,pad=0.03,rounding_size=0.14",
                                    facecolor=PURPLE_LIGHT, edgecolor=PURPLE_BORDER, lw=1.2)
    ax_right.add_patch(pill_r)
    ax_right.text(x_align, 1.14, r"$\dot{\theta} = \frac{p_\theta}{ml^2}, \qquad \dot{p}_\theta = -mgl\sin\theta$",
                  fontsize=18.0, weight='bold', color=PURPLE, ha='left', va='center')
    ax_right.text(x_align, 0.44, "Two coupled 1st-order ODEs", fontsize=13.0, weight='bold', color=LIGHT_SLATE, ha='left', va='center')

    # Right half: True Nonlinear Pendulum Phase Plane Trajectory
    # Center of phase plane at (7.30, 1.56)
    pp_x0, pp_y0 = 7.30, 1.56
    pp_w = 1.65
    pp_h_up = 0.82
    pp_h_down = 0.66

    # Axes
    ax_right.annotate('', xy=(pp_x0 + pp_w, pp_y0), xytext=(pp_x0 - pp_w, pp_y0),
                      arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.6))
    ax_right.annotate('', xy=(pp_x0, pp_y0 + pp_h_up), xytext=(pp_x0, pp_y0 - pp_h_down),
                      arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.6))

    ax_right.text(pp_x0 + pp_w + 0.12, pp_y0 - 0.05, r"$\theta$", fontsize=16.0, weight='bold', color=NAVY, va='center')
    ax_right.text(pp_x0 + 0.10, pp_y0 + pp_h_up + 0.08, r"$p_\theta$", fontsize=16.0, weight='bold', color=NAVY, ha='center')

    # Compute exact nonlinear constant-energy contour for pendulum:
    def compute_exact_pendulum_orbit(th_max, n_pts=350):
        th_pts = np.linspace(-th_max, th_max, n_pts)
        p_val = np.sqrt(np.maximum(0.0, 2.0 * (np.cos(th_pts) - np.cos(th_max))))
        # Complete closed loop (clockwise flow)
        x_loop = np.concatenate([th_pts, th_pts[::-1], [th_pts[0]]])
        y_loop = np.concatenate([p_val, -p_val[::-1], [p_val[0]]])
        return x_loop, y_loop

    # Outer nonlinear orbit with large amplitude (theta_max = 2.55 rad ~ 146 deg)
    th_nl, p_nl = compute_exact_pendulum_orbit(2.55)
    
    # Scale to fill schematic box attractively
    scale_x = 1.25 / 2.55
    scale_y = 0.64 / np.max(p_nl)

    # Inner orbit (small amplitude theta_max = 0.60 rad ~ 34 deg, dashed harmonic approximation)
    th_in, p_in = compute_exact_pendulum_orbit(0.60)
    ax_right.plot(pp_x0 + th_in * scale_x, pp_y0 + p_in * scale_y, color='#c4b5fd', lw=1.4, ls='--')

    # Plot prominent outer nonlinear trajectory
    ox = pp_x0 + th_nl * scale_x
    oy = pp_y0 + p_nl * scale_y
    ax_right.plot(ox, oy, color=PURPLE, lw=2.5)

    # Direction arrows on orbit (clockwise flow for pendulum)
    top_idx = np.argmax(oy)
    bot_idx = np.argmin(oy)
    ax_right.annotate('', xy=(pp_x0 + 0.18, oy[top_idx]), xytext=(pp_x0 - 0.15, oy[top_idx]),
                      arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=2.2, mutation_scale=14))
    ax_right.annotate('', xy=(pp_x0 - 0.18, oy[bot_idx]), xytext=(pp_x0 + 0.15, oy[bot_idx]),
                      arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=2.2, mutation_scale=14))

    # Center fixed point (downward equilibrium)
    center_pt = plt.Circle((pp_x0, pp_y0), 0.06, facecolor=NAVY, zorder=5)
    ax_right.add_patch(center_pt)

    ax_right.text(pp_x0, 0.54, "Phase Plane", fontsize=12.5, weight='bold', color=DARK_SLATE, ha='center', va='center')
    ax_right.text(pp_x0, 0.32, "Constant-Energy Trajectory", fontsize=12.0, weight='bold', color=SLATE, ha='center', va='center')

    # =========================================================================
    # COMMON BOTTOM SUMMARY BAND
    # =========================================================================
    band_y = 0.024
    band_h = 0.136
    band_w = 0.936
    band_x = 0.032

    ax_band = fig.add_axes([band_x, band_y, band_w, band_h])
    ax_band.set_facecolor(CARD_BG)
    ax_band.set_xlim(-0.15, 10.15)
    ax_band.set_ylim(-0.15, 10.15)
    ax_band.axis('off')

    band_card = patches.FancyBboxPatch((0.0, 0.0), 10.0, 10.0,
                                       boxstyle="round,pad=0.0,rounding_size=0.25",
                                       facecolor=WHITE, edgecolor='#94a3b8', lw=1.6, zorder=0)
    ax_band.add_patch(band_card)

    ax_band.text(5.0, 7.40,
                 "Same Physical System, Different Mathematical Organization",
                 fontsize=16.0, weight='bold', color=NAVY, ha='center', va='center')

    # Formula comparison with double arrow
    ax_band.text(2.55, 3.50, r"$\mathbf{Lagrangian:}\quad (q_i, \dot{q}_i)$", fontsize=18.5, weight='bold', color=BLUE, ha='center', va='center')
    
    ax_band.annotate('', xy=(5.65, 3.50), xytext=(4.35, 3.50),
                     arrowprops=dict(arrowstyle="<|-|>", color=DARK_SLATE, lw=2.8, mutation_scale=18))
    ax_band.text(5.0, 4.85, "Legendre Transformation", fontsize=12.5, weight='bold', color=LIGHT_SLATE, ha='center', va='center')

    ax_band.text(7.45, 3.50, r"$\mathbf{Hamiltonian:}\quad (q_i, p_i)$", fontsize=18.5, weight='bold', color=PURPLE, ha='center', va='center')

    plt.savefig(output_path, dpi=240, bbox_inches='tight', pad_inches=0.40, facecolor='#ffffff', edgecolor='none')
    plt.close()
    print(f"Generated {output_path}")

if __name__ == "__main__":
    create_figure()

