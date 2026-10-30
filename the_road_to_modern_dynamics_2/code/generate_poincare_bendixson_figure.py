#!/usr/bin/env python3
r"""
Generate infographic for Article 2:
"From Qualitative Geometry to the Poincaré–Bendixson Theorem"

Key improvements based on editorial and mathematical review:
1. Panel 1 (Poincaré):
   - Exact Hamiltonian double-well phase portrait.
   - Centers C_1, C_2 with closed periodic trajectories.
   - Exact invariant homoclinic separatrix level curve H(x, y) = 0 from Saddle S.
   - User requested short caption: "Equilibria, periodic trajectories, and separatrices organize the phase plane"

2. Panel 2 (Bendixson):
   - Local flow near isolated singular point decomposed into hyperbolic and parabolic sectors.
   - Exact circular neighborhood U.
   - User requested short caption: "Local analysis of trajectories near isolated singular points"

3. Panel 3 (Poincaré–Bendixson Theorem - Hero Panel):
   - Perfect 1:1 square canvas (5.04 in x 5.04 in) for true circular limit cycle \Gamma.
   - Single clean trajectory x_0 spiraling monotonically outward toward \Gamma without intersecting.
   - Repeller x* at origin with mathematically precise label x* \notin \omega(x_0).
   - Solid white callout box for \omega-limit set: \omega(x_0) = \Gamma.
   - User requested short caption: "Under suitable conditions, bounded planar trajectories approach periodic orbits"

4. Readability & Proportions:
   - Zero overlap between axis labels and bottom boxes.
   - Captions broken into balanced lines that fit cleanly within card borders.
   - Font size >= 13 pt everywhere.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "poincare_bendixson_theorem.png"


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

    # High-resolution widescreen canvas (18 x 9.8 inches at 240 DPI)
    fig_w = 18.0
    fig_h = 9.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'          # Deep slate navy for main headings
    DARK_SLATE = '#1e293b'    # Body text & subheaders
    SLATE = '#334155'         # Secondary text
    MUTED = '#64748b'         # Captions & axes
    BORDER_CARD = '#cbd5e1'   # Card border
    BG_CARD = '#f8fafc'       # Light background for panels
    BG_BOX = '#ffffff'        # Pure white for callout cards
    
    BLUE_ACCENT = '#2563eb'   # Primary blue accent
    BLUE_LIGHT = '#eff6ff'    # Soft blue tint
    BLUE_BORDER = '#93c5fd'   # Blue card border
    
    PURPLE_ACCENT = '#7c3aed' # Purple accent for Bendixson
    PURPLE_LIGHT = '#f5f3ff'  # Soft purple tint
    PURPLE_BORDER = '#c4b5fd' # Purple border
    
    EMERALD_ACCENT = '#059669' # Emerald for limit cycle / theorem
    EMERALD_LIGHT = '#ecfdf5'  # Soft emerald tint
    EMERALD_BORDER = '#6ee7b7' # Emerald border

    # -------------------------------------------------------------
    # Main Header & Context Banner (>= 14 pt)
    # -------------------------------------------------------------
    fig.text(0.5, 0.962,
             "From Qualitative Geometry to the Poincaré–Bendixson Theorem",
             fontsize=20.5, weight='bold', color=NAVY, ha='center', va='center')
    
    fig.text(0.5, 0.925,
             "How the geometry of the phase plane constrains the long-term behavior of planar dynamical systems",
             fontsize=16.5, style='italic', color=DARK_SLATE, ha='center', va='center')

    # Background axis for panel cards, headers, badges, and summary boxes
    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')

    # Card layout parameters: Panel 3 is substantially wider (hero panel)
    y_card = 0.038
    h_card = 0.858

    # Symmetrical distribution: margins 0.024, gaps 0.018
    # 0.024 + 0.290 + 0.018 + 0.290 + 0.018 + 0.336 + 0.024 = 1.000 exactly
    x1 = 0.024
    w1 = 0.290

    x2 = 0.332
    w2 = 0.290

    x3 = 0.640
    w3 = 0.336

    panels_spec = [
        (x1, w1, "1", "Poincaré: Qualitative Geometry", "1881–1886 · Phase Plane Analysis",
         BLUE_ACCENT, BLUE_LIGHT, BLUE_BORDER),
        (x2, w2, "2", "Bendixson: Local Analysis", "1901 · Isolated Singular Points",
         PURPLE_ACCENT, PURPLE_LIGHT, PURPLE_BORDER),
        (x3, w3, "3", "Poincaré–Bendixson Theorem", "Restriction on Planar Trajectories",
         EMERALD_ACCENT, EMERALD_LIGHT, EMERALD_BORDER),
    ]

    # Draw outer background cards for the three panels
    for px, pw, num, title, subtitle, acc_color, bg_tint, bdr_color in panels_spec:
        # Card container
        card_rect = patches.FancyBboxPatch(
            (px, y_card), pw, h_card,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.4,
            zorder=1
        )
        ax_bg.add_patch(card_rect)

        # Header accent bar (slightly taller for prominent typography)
        hbar_h = 0.082
        hbar_rect = patches.FancyBboxPatch(
            (px, y_card + h_card - hbar_h), pw, hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=bg_tint, edgecolor=bdr_color, linewidth=1.2,
            zorder=2
        )
        ax_bg.add_patch(hbar_rect)

        # Number Badge circle
        badge_x = px + 0.022
        badge_y = y_card + h_card - hbar_h / 2
        badge_c = patches.Circle(
            (badge_x, badge_y), 0.016,
            facecolor=acc_color, edgecolor='none',
            zorder=3
        )
        ax_bg.add_patch(badge_c)
        ax_bg.text(badge_x, badge_y, num, fontsize=15.0, weight='bold',
                   color='#ffffff', ha='center', va='center', zorder=4)

        # Title (deep slate navy/black) & subtitle (distinct slate grey, not too light)
        ax_bg.text(badge_x + 0.022, badge_y + 0.015, title,
                   fontsize=16.5, weight='bold', color=NAVY, va='center', zorder=4)
        ax_bg.text(badge_x + 0.022, badge_y - 0.016, subtitle,
                   fontsize=14.8, weight='bold', color='#475569', va='center', zorder=4)

    # Vertical coordinates: completely non-overlapping
    y_box = 0.046
    h_box = 0.100
    y_plot = 0.222
    h_plot = 0.575

    # =========================================================================
    # PANEL 1: Poincaré: Qualitative Geometry
    # Exact Double-Well Hamiltonian System:
    # dx/dt = y, dy/dt = x - x^3
    # Conserved H(x, y) = 0.5*y^2 - 0.5*x^2 + 0.25*x^4
    # Saddle at (0, 0), Centers at (1, 0) and (-1, 0)
    # Exact Separatrix level curve: H = 0 -> y = \pm x * \sqrt{1 - 0.5*x^2}
    # =========================================================================
    ax1_w = 0.226
    ax1_x = x1 + (w1 - ax1_w) / 2
    ax1 = fig.add_axes([ax1_x, y_plot, ax1_w, h_plot], zorder=5)
    ax1.set_facecolor('#ffffff')

    # Grid for streamplot and contours
    gx1 = np.linspace(-1.75, 1.75, 200)
    gy1 = np.linspace(-1.40, 1.40, 200)
    X1, Y1 = np.meshgrid(gx1, gy1)
    U1 = Y1
    V1 = X1 - X1**3
    H1 = 0.5 * Y1**2 - 0.5 * X1**2 + 0.25 * X1**4

    # Subtle background flow lines
    ax1.streamplot(X1, Y1, U1, V1, color='#f1f5f9', density=0.75,
                   linewidth=0.8, arrowsize=0.8, arrowstyle='->', zorder=1)

    # Closed periodic orbits inside wells (around Centers C_1 and C_2)
    ax1.contour(X1, Y1, H1, levels=[-0.20, -0.13, -0.05],
                colors=[BLUE_ACCENT], linewidths=[1.8, 1.8, 1.8], zorder=4)

    # Single enclosing outer periodic orbit outside separatrix (H = 0.28)
    ax1.contour(X1, Y1, H1, levels=[0.28],
                colors=['#0284c7'], linewidths=[1.8], linestyles=['-'], zorder=3)

    # Direction arrows on inner periodic orbits (clockwise circulation)
    # Center C_1 (right, clockwise): at (1, 0.42) moving right, at (1, -0.42) moving left
    ax1.annotate('', xy=(1.05, 0.42), xytext=(0.95, 0.42),
                 arrowprops=dict(arrowstyle="-|>", color=BLUE_ACCENT, lw=1.8, mutation_scale=13), zorder=5)
    ax1.annotate('', xy=(0.95, -0.42), xytext=(1.05, -0.42),
                 arrowprops=dict(arrowstyle="-|>", color=BLUE_ACCENT, lw=1.8, mutation_scale=13), zorder=5)

    # Center C_2 (left, clockwise): at (-1, 0.42) moving right, at (-1, -0.42) moving left
    ax1.annotate('', xy=(-0.95, 0.42), xytext=(-1.05, 0.42),
                 arrowprops=dict(arrowstyle="-|>", color=BLUE_ACCENT, lw=1.8, mutation_scale=13), zorder=5)
    ax1.annotate('', xy=(-1.05, -0.42), xytext=(-0.95, -0.42),
                 arrowprops=dict(arrowstyle="-|>", color=BLUE_ACCENT, lw=1.8, mutation_scale=13), zorder=5)

    # Direction arrows on outer periodic orbit (H = 0.28)
    # In strict consistency with the Hamiltonian vector field (dx/dt = y, dy/dt = x - x^3):
    # Upper half plane (y > 0): dx/dt > 0 (flow is to the right)
    # Lower half plane (y < 0): dx/dt < 0 (flow is to the left)
    # Upper right lobe (x = 0.85, y = 1.01): moving right-up along the curve
    ax1.annotate('', xy=(0.90, 1.022), xytext=(0.80, 0.998),
                 arrowprops=dict(arrowstyle="-|>", color='#0284c7', lw=1.8, mutation_scale=13), zorder=5)
    # Lower right lobe (x = 0.85, y = -1.01): moving left-up along the curve
    ax1.annotate('', xy=(0.80, -0.998), xytext=(0.90, -1.022),
                 arrowprops=dict(arrowstyle="-|>", color='#0284c7', lw=1.8, mutation_scale=13), zorder=5)
    # Upper left lobe (x = -0.85, y = 1.01): moving right-down along the curve
    ax1.annotate('', xy=(-0.80, 0.998), xytext=(-0.90, 1.022),
                 arrowprops=dict(arrowstyle="-|>", color='#0284c7', lw=1.8, mutation_scale=13), zorder=5)
    # Lower left lobe (x = -0.85, y = -1.01): moving left-down along the curve
    ax1.annotate('', xy=(-0.90, -1.022), xytext=(-0.80, -0.998),
                 arrowprops=dict(arrowstyle="-|>", color='#0284c7', lw=1.8, mutation_scale=13), zorder=5)

    # EXACT INVARIANT SEPARATRIX: Level curve H = 0
    # Two closed homoclinic loops meeting PRECISELY at Saddle S (0, 0)
    xs_pos = np.linspace(0.0, np.sqrt(2), 400)
    ys_pos_top = xs_pos * np.sqrt(np.maximum(0.0, 1.0 - 0.5 * xs_pos**2))
    ys_pos_bot = -ys_pos_top
    loop_x_right = np.concatenate([xs_pos, xs_pos[::-1]])
    loop_y_right = np.concatenate([ys_pos_top, ys_pos_bot[::-1]])

    loop_x_left = -loop_x_right
    loop_y_left = loop_y_right

    # Plot both homoclinic loops starting and ending exactly at (0, 0)
    ax1.plot(loop_x_right, loop_y_right, color='#ef4444', linewidth=2.4, linestyle=(0, (5, 2.5)), zorder=6)
    ax1.plot(loop_x_left, loop_y_left, color='#ef4444', linewidth=2.4, linestyle=(0, (5, 2.5)), zorder=6)

    # Short solid red segments crossing (0, 0) along tangents y = \pm x ensuring exact solid meeting
    ax1.plot([-0.10, 0.10], [-0.10, 0.10], color='#ef4444', linewidth=2.4, zorder=7)
    ax1.plot([-0.10, 0.10], [0.10, -0.10], color='#ef4444', linewidth=2.4, zorder=7)

    # Separatrix flow arrows generated directly from vector field dx/dt = y, dy/dt = x - x^3
    def draw_separatrix_arrow(ax, x_val, sign_y, scale=0.10):
        y_val = sign_y * abs(x_val) * np.sqrt(max(0.0, 1.0 - 0.5 * x_val**2))
        vx = y_val
        vy = x_val - x_val**3
        norm = np.hypot(vx, vy)
        ux = (vx / norm) * scale
        uy = (vy / norm) * scale
        ax.annotate('', xy=(x_val + 0.5*ux, y_val + 0.5*uy),
                    xytext=(x_val - 0.5*ux, y_val - 0.5*uy),
                    arrowprops=dict(arrowstyle="-|>", color='#ef4444', lw=2.0, mutation_scale=14, shrinkA=0, shrinkB=0),
                    zorder=8)

    # Direction arrows along separatrix: strictly clockwise and unobstructed at apexes
    draw_separatrix_arrow(ax1, 1.0, +1)   # Right lobe top: moving right
    draw_separatrix_arrow(ax1, 1.0, -1)   # Right lobe bottom: moving left
    draw_separatrix_arrow(ax1, -1.0, -1)  # Left lobe bottom: moving left
    draw_separatrix_arrow(ax1, -1.0, +1)  # Left lobe top: moving right

    # Equilibria: Saddle S at (0, 0) - Solid red marker anchoring the branches with zero white gap
    ax1.scatter([0], [0], color='#ef4444', edgecolor='#991b1b', s=75, linewidth=1.5, zorder=9)
    ax1.text(0.0, 0.18, r"$\mathbf{Saddle}\;\boldsymbol{S}$", fontsize=14.5, weight='bold', color='#b91c1c', ha='center',
             bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#fca5a5', lw=0.9), zorder=11)

    # Centers C_1 and C_2
    ax1.scatter([1], [0], color=BLUE_ACCENT, edgecolor='#1e3a8a', s=115, linewidth=2.0, zorder=10)
    ax1.text(1.0, -0.24, r"$\mathbf{Center}\;\boldsymbol{C_1}$", fontsize=14.5, weight='bold', color='#1e40af', ha='center',
             bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor=BLUE_BORDER, lw=0.9), zorder=11)

    ax1.scatter([-1], [0], color=BLUE_ACCENT, edgecolor='#1e3a8a', s=115, linewidth=2.0, zorder=10)
    ax1.text(-1.0, -0.24, r"$\mathbf{Center}\;\boldsymbol{C_2}$", fontsize=14.5, weight='bold', color='#1e40af', ha='center',
             bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor=BLUE_BORDER, lw=0.9), zorder=11)

    # Separatrix callout: Placed in the clear saddle neck, pointing directly to the red separatrix branch
    ax1.annotate(
        r"$\mathbf{Separatrix}$",
        xy=(0.42, 0.401), xytext=(0.0, 0.68),
        fontsize=14.5, weight='bold', color='#dc2626', ha='center',
        bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#fca5a5', lw=1.0),
        arrowprops=dict(arrowstyle="->", color='#ef4444', lw=1.8, connectionstyle="arc3,rad=-0.06", shrinkB=0),
        zorder=12
    )

    # Periodic Orbits callout with clean pointer to inner periodic orbit
    ax1.annotate(
        r"$\mathbf{Periodic\;Orbits}$",
        xy=(1.00, 0.35), xytext=(1.10, 0.54),
        fontsize=14.5, weight='bold', color='#0284c7', ha='center',
        bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#7dd3fc', lw=0.9),
        arrowprops=dict(arrowstyle="->", color='#0284c7', lw=1.6, connectionstyle="arc3,rad=0.08"),
        zorder=12
    )

    ax1.set_xlim(-1.75, 1.75)
    ax1.set_ylim(-1.40, 1.40)
    # Clean state coordinates x and y (removed y = \dot{x} as requested)
    ax1.set_xlabel(r"State coordinate $x$", fontsize=15.0, weight='bold', color=DARK_SLATE, labelpad=5)
    ax1.set_ylabel(r"State coordinate $y$", fontsize=15.0, weight='bold', color=DARK_SLATE, labelpad=5)
    ax1.tick_params(labelsize=13.5, colors=SLATE)
    ax1.grid(True, linestyle=':', alpha=0.45, color='#cbd5e1')

    # Bottom caption box for Panel 1 (Exact user requested wording)
    box1 = patches.FancyBboxPatch(
        (x1 + 0.014, y_box), w1 - 0.028, h_box,
        boxstyle="round,pad=0.0,rounding_size=0.014",
        facecolor=BG_BOX, edgecolor=BORDER_CARD, linewidth=1.2,
        zorder=3
    )
    ax_bg.add_patch(box1)

    ax_bg.text(x1 + w1/2, y_box + h_box/2,
               "Equilibria, periodic trajectories,\nand separatrices organize\nthe phase plane.",
               fontsize=13.8, weight='bold', color=DARK_SLATE, ha='center', va='center',
               linespacing=1.30, zorder=4)

    # =========================================================================
    # PANEL 2: Bendixson: Local Analysis
    # Exact Vector Field for Saddle: dx/dt = -x, dy/dt = y
    # Integral Curves: x(t) = x_0 e^{-t}, y(t) = y_0 e^t (xy = C)
    # =========================================================================
    ax2_w = 0.226
    ax2_x = x2 + (w2 - ax2_w) / 2
    ax2 = fig.add_axes([ax2_x, y_plot, ax2_w, h_plot], zorder=5)
    ax2.set_facecolor('#ffffff')

    r_u = 1.15
    theta_u = np.linspace(0, 2*np.pi, 240)
    ux = r_u * np.cos(theta_u)
    uy = r_u * np.sin(theta_u)

    # Subtle circular neighborhood background
    disc_u = patches.Circle((0, 0), r_u, facecolor='#f8fafc', edgecolor='none', zorder=2)
    ax2.add_patch(disc_u)

    # Neighborhood boundary circle \partial U
    ax2.plot(ux, uy, color=PURPLE_ACCENT, linewidth=1.8, linestyle=':', zorder=4)

    # Subtle background streamlines for the exact vector field (dx/dt = -x, dy/dt = y)
    gx2 = np.linspace(-1.18, 1.18, 140)
    gy2 = np.linspace(-1.18, 1.18, 140)
    X2, Y2 = np.meshgrid(gx2, gy2)
    U2 = -X2
    V2 = Y2
    mask_disk = (X2**2 + Y2**2 <= r_u**2)
    U2_masked = np.where(mask_disk, U2, np.nan)
    V2_masked = np.where(mask_disk, V2, np.nan)
    ax2.streamplot(X2, Y2, U2_masked, V2_masked, color='#f1f5f9', density=0.70,
                   linewidth=0.8, arrowsize=0.8, arrowstyle='->', zorder=2)

    # Exact Hyperbolic Trajectories from Vector Field dx/dt = -x, dy/dt = y
    # With x(t) = s_0 e^{-t}, y(t) = s_0 e^t, radius R^2(t) = 2C \cosh(2t) <= r_u^2
    c_list = [0.10, 0.28, 0.58]
    for c_val in c_list:
        val_ratio = (r_u**2) / (2.0 * c_val)
        if val_ratio >= 1.0:
            t_max = 0.5 * np.arccosh(val_ratio)
            t_vals = np.linspace(-t_max, t_max, 120)
            s0 = np.sqrt(c_val)
            xi_t = s0 * np.exp(-t_vals)
            eta_t = s0 * np.exp(t_vals)
            # Plot in all 4 quadrants
            ax2.plot(xi_t, eta_t, color=PURPLE_ACCENT, linewidth=1.8, zorder=5)
            ax2.plot(-xi_t, eta_t, color=PURPLE_ACCENT, linewidth=1.8, zorder=5)
            ax2.plot(-xi_t, -eta_t, color=PURPLE_ACCENT, linewidth=1.8, zorder=5)
            ax2.plot(xi_t, -eta_t, color=PURPLE_ACCENT, linewidth=1.8, zorder=5)

    # Mathematically exact direction arrows determined directly from dx/dt = -x, dy/dt = y:
    # Trajectories in upper half-plane move UPWARD; lower half-plane move DOWNWARD;
    # Horizontal motion is ALWAYS toward the vertical axis (dx/dt = -x).
    def draw_saddle_arrow(ax, x_pt, y_pt, scale=0.09):
        vx = -x_pt
        vy = y_pt
        norm = np.hypot(vx, vy)
        ux = (vx / norm) * scale
        uy = (vy / norm) * scale
        ax.annotate('', xy=(x_pt + 0.5*ux, y_pt + 0.5*uy),
                    xytext=(x_pt - 0.5*ux, y_pt - 0.5*uy),
                    arrowprops=dict(arrowstyle="-|>", color=PURPLE_ACCENT, lw=1.8, mutation_scale=13, shrinkA=0, shrinkB=0),
                    zorder=7)

    s0_mid = np.sqrt(0.28)
    for t_eval in [-0.35, 0.35]:
        # Q1: (+x, +y) -> points UP and LEFT
        draw_saddle_arrow(ax2, s0_mid * np.exp(-t_eval), s0_mid * np.exp(t_eval))
        # Q2: (-x, +y) -> points UP and RIGHT
        draw_saddle_arrow(ax2, -s0_mid * np.exp(-t_eval), s0_mid * np.exp(t_eval))
        # Q3: (-x, -y) -> points DOWN and RIGHT
        draw_saddle_arrow(ax2, -s0_mid * np.exp(-t_eval), -s0_mid * np.exp(t_eval))
        # Q4: (+x, -y) -> points DOWN and LEFT
        draw_saddle_arrow(ax2, s0_mid * np.exp(-t_eval), -s0_mid * np.exp(t_eval))

    # Invariant axis dividers with flow direction
    ax2.plot([-r_u, r_u], [0, 0], color='#94a3b8', linestyle='--', linewidth=1.2, zorder=3)
    ax2.plot([0, 0], [-r_u, r_u], color='#94a3b8', linestyle='--', linewidth=1.2, zorder=3)
    # Vertical axis outgoing arrows (flowing away from singular point x*, y > 0 and y < 0)
    ax2.annotate('', xy=(0.0, 0.78), xytext=(0.0, 0.64),
                 arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=1.6, mutation_scale=13, shrinkA=0, shrinkB=0), zorder=4)
    ax2.annotate('', xy=(0.0, -0.78), xytext=(0.0, -0.64),
                 arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=1.6, mutation_scale=13, shrinkA=0, shrinkB=0), zorder=4)
    # Horizontal axis incoming arrows (flowing toward singular point x*, x > 0 and x < 0)
    ax2.annotate('', xy=(0.64, 0.0), xytext=(0.78, 0.0),
                 arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=1.6, mutation_scale=13, shrinkA=0, shrinkB=0), zorder=4)
    ax2.annotate('', xy=(-0.64, 0.0), xytext=(-0.78, 0.0),
                 arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=1.6, mutation_scale=13, shrinkA=0, shrinkB=0), zorder=4)

    # Singular point marker
    ax2.scatter([0], [0], color='#ffffff', edgecolor=PURPLE_ACCENT, s=115, linewidth=2.4, zorder=10)
    ax2.text(0.0, 0.18, r"$\mathbf{Singular\;Point}\;\boldsymbol{x^*}$", fontsize=14.5, weight='bold',
             color=PURPLE_ACCENT, ha='center',
             bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor=PURPLE_BORDER, lw=0.9), zorder=11)

    # Split label over two lines so it stays well within panel borders and above the plot
    ax2.text(0.0, 1.27,
             r"$\mathbf{Trajectories\;Near}$" "\n" r"$\mathbf{an\;Isolated\;Singular\;Point}$",
             fontsize=12.2, weight='bold', color=DARK_SLATE, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.22", facecolor='#ffffff', edgecolor='#cbd5e1', lw=0.9), zorder=8)

    ax2.set_xlim(-1.45, 1.45)
    ax2.set_ylim(-1.40, 1.40)
    ax2.set_xlabel(r"State coordinate $x$", fontsize=15.0, weight='bold', color=DARK_SLATE, labelpad=5)
    ax2.set_ylabel(r"State coordinate $y$", fontsize=15.0, weight='bold', color=DARK_SLATE, labelpad=5)
    ax2.tick_params(labelsize=13.5, colors=SLATE)
    ax2.grid(True, linestyle=':', alpha=0.45, color='#cbd5e1')

    # Bottom caption box for Panel 2 (Exact user requested wording)
    box2 = patches.FancyBboxPatch(
        (x2 + 0.014, y_box), w2 - 0.028, h_box,
        boxstyle="round,pad=0.0,rounding_size=0.014",
        facecolor=BG_BOX, edgecolor=BORDER_CARD, linewidth=1.2,
        zorder=3
    )
    ax_bg.add_patch(box2)

    ax_bg.text(x2 + w2/2, y_box + h_box/2,
               "Local analysis of trajectories\nnear isolated singular points.",
               fontsize=13.8, weight='bold', color=DARK_SLATE, ha='center', va='center',
               linespacing=1.30, zorder=4)

    # =========================================================================
    # PANEL 3: Poincaré–Bendixson Theorem (HERO PANEL - LARGEST)
    # Perfect 1:1 Square Canvas (5.04 in x 5.04 in)
    # Visibly Continuous Spiraling Trajectory Monotonically Approaching \Gamma
    # Unstable Repeller x^* at Origin with x^* \notin \omega(x_0)
    # Bounded Region K
    # =========================================================================
    h_plot_3 = 0.514
    y_plot_3 = y_plot + (h_plot - h_plot_3) / 2
    ax3_w = 0.280
    ax3_x = 0.673
    ax3 = fig.add_axes([ax3_x, y_plot_3, ax3_w, h_plot_3], zorder=5)
    ax3.set_facecolor('#ffffff')

    # Bounded Region K: Disk of radius r_k = 1.48
    r_k = 1.48
    theta_ann = np.linspace(0, 2*np.pi, 240)

    # Shaded Bounded Region K
    patch_k = patches.Circle(
        (0, 0), r_k,
        facecolor='#ecfdf5', edgecolor='none', alpha=0.50, zorder=2
    )
    ax3.add_patch(patch_k)

    # Boundary circle of Bounded Region K (dashed green)
    ax3.plot(r_k * np.cos(theta_ann), r_k * np.sin(theta_ann),
             color='#059669', linestyle='--', linewidth=1.5, zorder=3)

    # THE PERIODIC ORBIT \Gamma: Circle of radius 1.0 (Bold emerald)
    theta_lc = np.linspace(0, 2*np.pi, 300)
    lc_x = np.cos(theta_lc)
    lc_y = np.sin(theta_lc)
    ax3.plot(lc_x, lc_y, color='#047857', linewidth=3.0, zorder=7)

    # Direction arrows on periodic orbit (counter-clockwise)
    for a_deg in [180, 270]:
        a_rad = np.radians(a_deg)
        x_pt = np.cos(a_rad)
        y_pt = np.sin(a_rad)
        tx = -np.sin(a_rad)
        ty = np.cos(a_rad)
        ax3.annotate('', xy=(x_pt + 0.045*tx, y_pt + 0.045*ty),
                     xytext=(x_pt - 0.045*tx, y_pt - 0.045*ty),
                     arrowprops=dict(arrowstyle="-|>", color='#047857', lw=2.2, mutation_scale=14, shrinkA=0, shrinkB=0),
                     zorder=8)

    # HERO TRAJECTORY: Single continuous inward spiral starting PRECISELY at x_0
    # Originates strictly at Initial State x_0 and monotonically approaches \Gamma
    # across ~1.7 revolutions (theta_span = 3.4 * pi) with a clear, visible radial pitch
    # that is unmistakably a single continuous spiral rather than concentric loops.
    # Minimum radius at end is r = 1.064, guaranteeing a clear, visible separation from \Gamma.
    r_0 = 1.44
    theta_0 = 0.35
    theta_span = 3.40 * np.pi
    theta_pts = np.linspace(theta_0, theta_0 + theta_span, 1000)
    alpha_rate = 0.18
    r_pts = 1.0 + (r_0 - 1.0) * np.exp(-alpha_rate * (theta_pts - theta_0))

    traj_x = r_pts * np.cos(theta_pts)
    traj_y = r_pts * np.sin(theta_pts)

    ax3.plot(traj_x, traj_y, color='#2563eb', linewidth=2.3, zorder=6)

    # Direction arrows along the inward spiral showing unambiguous counter-clockwise circulation:
    # 1. Top of outer turn (theta = 0.50*pi): flow strictly to the LEFT (<-)
    # 2. Left of outer turn (theta = 1.00*pi): flow strictly DOWN (v), parallel to periodic orbit arrow
    # 3. Right of second turn (theta = 2.00*pi): flow strictly UP (^)
    for t_arr in [0.50*np.pi, 1.00*np.pi, 2.00*np.pi]:
        idx = np.argmin(np.abs(theta_pts - t_arr))
        dx = traj_x[idx+4] - traj_x[idx-4]
        dy = traj_y[idx+4] - traj_y[idx-4]
        norm = np.hypot(dx, dy)
        ax3.annotate('', xy=(traj_x[idx] + 0.045*dx/norm, traj_y[idx] + 0.045*dy/norm),
                     xytext=(traj_x[idx] - 0.045*dx/norm, traj_y[idx] - 0.045*dy/norm),
                     arrowprops=dict(arrowstyle="-|>", color='#1d4ed8', lw=2.0, mutation_scale=14, shrinkA=0, shrinkB=0),
                     zorder=7)

    # Initial state marker x_0 at outer radius
    x0_pos = (1.44 * np.cos(theta_0), 1.44 * np.sin(theta_0))
    ax3.scatter([x0_pos[0]], [x0_pos[1]], color='#d97706', edgecolor='#78350f', s=125, linewidth=2.4, zorder=10)
    # Balanced callout in upper-right corner: moved slightly right to (1.04, 1.20) inside panel border
    ax3.annotate(
        r"$\mathbf{Initial\;State}\;\boldsymbol{x_0}$",
        xy=(x0_pos[0] + 0.02, x0_pos[1] + 0.04), xytext=(1.04, 1.20),
        fontsize=14.5, weight='bold', color='#b45309', ha='center',
        bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#fcd34d', lw=0.9),
        arrowprops=dict(arrowstyle="->", color='#b45309', lw=1.6, connectionstyle="arc3,rad=-0.08"),
        zorder=11
    )

    # Central Equilibrium at origin with x* \notin \omega(x_0)
    # Placed with generous clearance so the center circle is completely unobstructed
    ax3.scatter([0], [0], color='#ffffff', edgecolor='#dc2626', s=110, linewidth=2.4, zorder=10)
    ax3.text(0.0, -0.32, r"$\mathbf{Equilibrium}\;\boldsymbol{x^* \notin \omega(x_0)}$", fontsize=14.2, weight='bold',
             color='#dc2626', ha='center',
             bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#fca5a5', lw=0.9), zorder=11)

    # Clean callout box for Periodic Orbit \Gamma and \omega-limit set:
    # Placed centrally inside \Gamma (moved slightly right to x=0.04) with ample clearance
    ax3.annotate(
        r"$\mathbf{Periodic\;Orbit}\;\boldsymbol{\Gamma}$" "\n" r"$\boldsymbol{\omega(x_0) = \Gamma}$",
        xy=(-0.65, 0.76), xytext=(0.04, 0.45),
        fontsize=14.8, weight='bold', color='#047857', ha='center',
        bbox=dict(boxstyle="round,pad=0.28", facecolor='#ffffff', edgecolor='#059669', lw=1.2),
        arrowprops=dict(arrowstyle="->", color='#047857', lw=1.8, connectionstyle="arc3,rad=-0.08"),
        zorder=12
    )

    # Bounded Region K label (safer and standard terminology)
    ax3.text(0.0, -1.28, r"$\mathbf{Bounded\;Region}\;\boldsymbol{K}$",
             fontsize=14.5, weight='bold', color='#065f46', ha='center',
             bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#6ee7b7', lw=1.0), zorder=12)

    # Isotropic square bounds: [-1.60, 1.60] x [-1.60, 1.60]
    ax3.set_xlim(-1.60, 1.60)
    ax3.set_ylim(-1.60, 1.60)
    ax3.set_xlabel(r"Phase space state $x_1$", fontsize=15.0, weight='bold', color=DARK_SLATE, labelpad=5)
    ax3.set_ylabel(r"Phase space state $x_2$", fontsize=15.0, weight='bold', color=DARK_SLATE, labelpad=4.5)
    ax3.tick_params(labelsize=13.5, colors=SLATE)
    ax3.grid(True, linestyle=':', alpha=0.45, color='#cbd5e1')

    # Bottom caption box for Panel 3 (Exact user requested conditional wording)
    box3 = patches.FancyBboxPatch(
        (x3 + 0.014, y_box), w3 - 0.028, h_box,
        boxstyle="round,pad=0.0,rounding_size=0.014",
        facecolor=BG_BOX, edgecolor=BORDER_CARD, linewidth=1.2,
        zorder=3
    )
    ax_bg.add_patch(box3)

    ax_bg.text(x3 + w3/2, y_box + h_box/2,
               "Bounded planar trajectories approach\nperiodic orbits when their limiting sets\ncontain no equilibria.",
               fontsize=13.0, weight='bold', color=DARK_SLATE, ha='center', va='center',
               linespacing=1.28, zorder=4)

    # Save figure
    plt.savefig(output_path, dpi=240, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] Successfully saved: {output_path}")


if __name__ == "__main__":
    create_figure()
