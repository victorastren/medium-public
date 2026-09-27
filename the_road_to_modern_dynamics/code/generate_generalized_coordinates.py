#!/usr/bin/env python3
r"""
Generate figure:
"Generalized Coordinates: From Degrees of Freedom to Equations of Motion"

Three-panel horizontal taxonomy + common bottom pipeline band:
Panel 1: Simple Pendulum (1 DOF, q = θ)
Panel 2: Double Pendulum (2 DOF, q1 = θ1, q2 = θ2)
Panel 3: Bead on Curved Track (1 DOF, q = s)
Bottom band: q_1, ..., q_n -> L(q_i, \dot{q}_i, t) -> (d/dt)(∂L/∂\dot{q}_i) - ∂L/∂q_i = 0
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "generalized_coordinates.png"

def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 16:9 ratio, ultra-crisp resolution
    fig_w = 17.6
    fig_h = 10.2
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor='#ffffff')

    # Color Palette matching publication standards
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#475569'
    LIGHT_SLATE = '#94a3b8'
    BORDER_COLOR = '#cbd5e1'
    CARD_BG = '#f8fafc'
    WHITE = '#ffffff'
    
    # Accent colors for the 3 systems
    BLUE = '#2563eb'
    PURPLE = '#7c3aed'
    TEAL = '#0d9488'

    # Title badge at top (with generous headroom)
    fig.text(0.5, 0.942,
             "Generalized Coordinates: From Degrees of Freedom to Equations of Motion",
             fontsize=21.0, weight='bold', color=NAVY, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.25",
                       facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1.3))

    # Top panels geometry: 3 panels side-by-side
    panel_y = 0.254
    panel_h = 0.640
    panel_w = 0.293
    gap_x = 0.027
    x_start = 0.035

    ax_coords = [
        [x_start + 0 * (panel_w + gap_x), panel_y, panel_w, panel_h],
        [x_start + 1 * (panel_w + gap_x), panel_y, panel_w, panel_h],
        [x_start + 2 * (panel_w + gap_x), panel_y, panel_w, panel_h]
    ]

    axes = [fig.add_axes(rect) for rect in ax_coords]

    for ax in axes:
        ax.set_facecolor(CARD_BG)
        ax.axis('off')
        ax.set_xlim(-1.6, 1.6)
        ax.set_ylim(-1.85, 1.45)
        # Background card frame
        card = patches.FancyBboxPatch((-1.56, -1.80), 3.12, 3.20,
                                      boxstyle="round,pad=0.03,rounding_size=0.14",
                                      facecolor=CARD_BG, edgecolor=BORDER_COLOR,
                                      lw=1.4, zorder=0)
        ax.add_patch(card)

    ax1, ax2, ax3 = axes

    # =========================================================================
    # PANEL 1: SIMPLE PENDULUM
    # =========================================================================
    # Header & Badge
    ax1.text(0, 1.30, "Simple Pendulum", fontsize=19.0, weight='bold', color=NAVY, ha='center', va='center')
    ax1.text(0, 1.05, "1 Degree of Freedom", fontsize=13.5, weight='bold', color=BLUE, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.32,rounding_size=0.20", facecolor='#eff6ff', edgecolor='#bfdbfe', lw=1.2))

    # Diagram: Simple Pendulum
    p1_pivot = (0.0, 0.48)
    p1_len = 1.15
    theta1_deg = 32
    theta1_rad = np.radians(theta1_deg)
    b1_x = p1_pivot[0] + p1_len * np.sin(theta1_rad)
    b1_y = p1_pivot[1] - p1_len * np.cos(theta1_rad)

    # Ceiling mount
    ax1.plot([-0.45, 0.45], [p1_pivot[1], p1_pivot[1]], color=DARK_SLATE, lw=2.4, zorder=3)
    for hx in np.linspace(-0.38, 0.38, 7):
        ax1.plot([hx, hx + 0.07], [p1_pivot[1], p1_pivot[1] + 0.08], color=DARK_SLATE, lw=1.4, zorder=3)

    # Vertical reference dashed line
    ax1.plot([p1_pivot[0], p1_pivot[0]], [p1_pivot[1], p1_pivot[1] - p1_len * 1.12],
             '--', color=LIGHT_SLATE, lw=1.6, zorder=1)

    # Angle arc θ
    arc_rad = 0.52
    arc_thetas = np.linspace(-np.pi/2, -np.pi/2 + theta1_rad, 40)
    ax1.plot(p1_pivot[0] + arc_rad * np.cos(arc_thetas),
             p1_pivot[1] + arc_rad * np.sin(arc_thetas),
             color=BLUE, lw=2.2, zorder=2)
    # Theta label placed at half-angle (16°), radius 0.32
    mid_th1 = -np.pi/2 + theta1_rad * 0.48
    ax1.text(p1_pivot[0] + 0.32 * np.cos(mid_th1),
             p1_pivot[1] + 0.32 * np.sin(mid_th1),
             r"$\theta$", fontsize=18.5, weight='bold', color=BLUE, ha='center', va='center')

    # Rod
    ax1.plot([p1_pivot[0], b1_x], [p1_pivot[1], b1_y], color=DARK_SLATE, lw=3.4, zorder=2)
    # Pivot point
    ax1.plot(p1_pivot[0], p1_pivot[1], 'o', color=DARK_SLATE, markersize=7.5, zorder=4)

    # Bob
    bob1 = patches.Circle((b1_x, b1_y), 0.14, facecolor=BLUE, edgecolor=DARK_SLATE, lw=2.0, zorder=5)
    ax1.add_patch(bob1)
    ax1.text(b1_x, b1_y, "$m$", fontsize=14.0, weight='bold', color=WHITE, ha='center', va='center', zorder=6)

    # Length label (to the right of rod)
    ax1.text(b1_x * 0.55 + 0.10, p1_pivot[1] + (b1_y - p1_pivot[1]) * 0.55,
             r"$l$", fontsize=16.0, weight='bold', color=DARK_SLATE)

    # Math card & explanation
    box_p1 = patches.FancyBboxPatch((-1.36, -1.68), 2.72, 0.98,
                                    boxstyle="round,pad=0.03,rounding_size=0.10",
                                    facecolor=WHITE, edgecolor=BORDER_COLOR, lw=1.3, zorder=2)
    ax1.add_patch(box_p1)

    ax1.text(0, -0.88, r"$q = \theta$", fontsize=22.0, weight='bold', color=NAVY, ha='center', va='center')
    ax1.text(0, -1.21, "Fixed-length constraint\nautomatically satisfied",
             fontsize=16.5, weight='bold', color=DARK_SLATE, ha='center', va='center', linespacing=1.28)
    ax1.text(0, -1.53, r"$L(\theta,\dot{\theta}) = T - V$",
             fontsize=17.5, weight='bold', color=NAVY, ha='center', va='center')

    # =========================================================================
    # PANEL 2: DOUBLE PENDULUM
    # =========================================================================
    # Header & Badge
    ax2.text(0, 1.30, "Double Pendulum", fontsize=19.0, weight='bold', color=NAVY, ha='center', va='center')
    ax2.text(0, 1.05, "2 Degrees of Freedom", fontsize=13.5, weight='bold', color=PURPLE, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.32,rounding_size=0.20", facecolor='#f5f3ff', edgecolor='#ddd6fe', lw=1.2))

    # Diagram: Double Pendulum with clearer visible angles
    p2_pivot = (0.0, 0.55)
    l1 = 0.65
    l2 = 0.62
    th1_deg = 32
    th2_deg = 28
    th1_rad = np.radians(th1_deg)
    th2_rad = np.radians(th2_deg)

    j1_x = p2_pivot[0] + l1 * np.sin(th1_rad)
    j1_y = p2_pivot[1] - l1 * np.cos(th1_rad)

    j2_x = j1_x + l2 * np.sin(th2_rad)
    j2_y = j1_y - l2 * np.cos(th2_rad)

    # Ceiling mount
    ax2.plot([-0.45, 0.45], [p2_pivot[1], p2_pivot[1]], color=DARK_SLATE, lw=2.4, zorder=3)
    for hx in np.linspace(-0.38, 0.38, 7):
        ax2.plot([hx, hx + 0.07], [p2_pivot[1], p2_pivot[1] + 0.08], color=DARK_SLATE, lw=1.4, zorder=3)

    # Ref line 1 (vertical from pivot)
    ax2.plot([p2_pivot[0], p2_pivot[0]], [p2_pivot[1], p2_pivot[1] - l1 * 1.15],
             '--', color=LIGHT_SLATE, lw=1.5, zorder=1)

    # Angle arc θ1
    arc1_rad = 0.46
    arc1_thetas = np.linspace(-np.pi/2, -np.pi/2 + th1_rad, 30)
    ax2.plot(p2_pivot[0] + arc1_rad * np.cos(arc1_thetas),
             p2_pivot[1] + arc1_rad * np.sin(arc1_thetas),
             color=PURPLE, lw=2.2, zorder=2)
    # Theta1 label inside the wedge
    mid_arc1 = -np.pi/2 + th1_rad * 0.46
    ax2.text(p2_pivot[0] + 0.28 * np.cos(mid_arc1),
             p2_pivot[1] + 0.28 * np.sin(mid_arc1),
             r"$\theta_1$", fontsize=17.5, weight='bold', color=PURPLE, ha='center', va='center')

    # Rod 1
    ax2.plot([p2_pivot[0], j1_x], [p2_pivot[1], j1_y], color=DARK_SLATE, lw=3.2, zorder=2)
    ax2.plot(p2_pivot[0], p2_pivot[1], 'o', color=DARK_SLATE, markersize=7.0, zorder=4)

    # Bob 1
    bob2_1 = patches.Circle((j1_x, j1_y), 0.13, facecolor=PURPLE, edgecolor=DARK_SLATE, lw=1.8, zorder=5)
    ax2.add_patch(bob2_1)
    ax2.text(j1_x, j1_y, "$m_1$", fontsize=12.0, weight='bold', color=WHITE, ha='center', va='center', zorder=6)

    # Ref line 2 (vertical from joint 1)
    ax2.plot([j1_x, j1_x], [j1_y, j1_y - l2 * 1.15], '--', color=LIGHT_SLATE, lw=1.4, zorder=1)

    # Angle arc θ2 (from vertical at joint 1)
    arc2_rad = 0.44
    arc2_thetas = np.linspace(-np.pi/2, -np.pi/2 + th2_rad, 30)
    ax2.plot(j1_x + arc2_rad * np.cos(arc2_thetas),
             j1_y + arc2_rad * np.sin(arc2_thetas),
             color=PURPLE, lw=2.2, zorder=2)
    
    # Theta2 label placed slightly lower and shifted away from rod 2
    # Moving closer to the dashed line (angle 0.38 * th2_rad) and further down (radius 0.28)
    mid_arc2 = -np.pi/2 + th2_rad * 0.38
    ax2.text(j1_x + 0.28 * np.cos(mid_arc2) - 0.015,
             j1_y + 0.28 * np.sin(mid_arc2) - 0.035,
             r"$\theta_2$", fontsize=17.5, weight='bold', color=PURPLE, ha='center', va='center')

    # Rod 2
    ax2.plot([j1_x, j2_x], [j1_y, j2_y], color=DARK_SLATE, lw=3.0, zorder=2)

    # Bob 2
    bob2_2 = patches.Circle((j2_x, j2_y), 0.13, facecolor=PURPLE, edgecolor=DARK_SLATE, lw=1.8, zorder=5)
    ax2.add_patch(bob2_2)
    ax2.text(j2_x, j2_y, "$m_2$", fontsize=12.0, weight='bold', color=WHITE, ha='center', va='center', zorder=6)

    # Math card & explanation
    box_p2 = patches.FancyBboxPatch((-1.36, -1.68), 2.72, 0.98,
                                    boxstyle="round,pad=0.03,rounding_size=0.10",
                                    facecolor=WHITE, edgecolor=BORDER_COLOR, lw=1.3, zorder=2)
    ax2.add_patch(box_p2)

    ax2.text(0, -0.88, r"$q_1 = \theta_1, \quad q_2 = \theta_2$",
             fontsize=20.5, weight='bold', color=NAVY, ha='center', va='center')
    ax2.text(0, -1.21, "Two independent coordinates\nfor coupled planar motion",
             fontsize=16.5, weight='bold', color=DARK_SLATE, ha='center', va='center', linespacing=1.28)
    ax2.text(0, -1.53, r"$L(\theta_1, \theta_2, \dot{\theta}_1, \dot{\theta}_2) = T - V$",
             fontsize=16.5, weight='bold', color=NAVY, ha='center', va='center')

    # =========================================================================
    # PANEL 3: BEAD ON CURVED TRACK
    # =========================================================================
    # Header & Badge
    ax3.text(0, 1.30, "Bead on Curved Track", fontsize=19.0, weight='bold', color=NAVY, ha='center', va='center')
    ax3.text(0, 1.05, "1 Degree of Freedom", fontsize=13.5, weight='bold', color=TEAL, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.32,rounding_size=0.20", facecolor='#f0fdfa', edgecolor='#99f6e4', lw=1.2))

    # Diagram: Smooth 2D curved wire / track
    wire_x = np.linspace(-1.25, 1.25, 200)
    wire_y = 0.25 * np.cos(1.8 * wire_x) - 0.20 * wire_x + 0.12

    # Draw wire supports at endpoints
    ax3.plot([-1.25, -1.25], [wire_y[0], wire_y[0] - 0.28], color=DARK_SLATE, lw=2.2, zorder=1)
    ax3.plot([1.25, 1.25], [wire_y[-1], wire_y[-1] - 0.28], color=DARK_SLATE, lw=2.2, zorder=1)
    ax3.plot([-1.35, -1.15], [wire_y[0] - 0.28, wire_y[0] - 0.28], color=DARK_SLATE, lw=3.0, zorder=2)
    ax3.plot([1.15, 1.35], [wire_y[-1] - 0.28, wire_y[-1] - 0.28], color=DARK_SLATE, lw=3.0, zorder=2)

    # Curved track itself
    ax3.plot(wire_x, wire_y, color=SLATE, lw=4.2, zorder=2)
    ax3.plot(wire_x, wire_y, color='#e2e8f0', lw=1.4, zorder=3)

    # Origin mark on the wire (s = 0)
    s0_idx = 35
    s0_x = wire_x[s0_idx]
    s0_y = wire_y[s0_idx]
    ax3.plot(s0_x, s0_y, '|', color=DARK_SLATE, markersize=14, markeredgewidth=2.2, zorder=4)
    # Move s = 0 slightly lower or right of mark so it doesn't crowd Arc length
    ax3.text(s0_x - 0.12, s0_y + 0.11, r"$s = 0$", fontsize=13.5, weight='bold', color=DARK_SLATE)

    # Position along curve for the bead
    bead_idx = 135
    bead_x = wire_x[bead_idx]
    bead_y = wire_y[bead_idx]

    # Arc length s path highlighted along the wire
    ax3.plot(wire_x[s0_idx:bead_idx+1], wire_y[s0_idx:bead_idx+1], color=TEAL, lw=4.5, zorder=4)
    
    # Coordinate arrow along the curve positioned well to the left of the bead
    mid_s = 82
    ax3.annotate('', xy=(wire_x[mid_s+5], wire_y[mid_s+5]), xytext=(wire_x[mid_s-5], wire_y[mid_s-5]),
                 arrowprops=dict(arrowstyle="->", color=TEAL, lw=2.4))
    # Place "Arc length s" label shifted to the right (x=0.18) and above the curve peak
    ax3.text(0.18, wire_y[mid_s] + 0.17,
             r"Arc length $s$", fontsize=15.5, weight='bold', color=TEAL, ha='center')

    # Bead on the wire
    bead = patches.Circle((bead_x, bead_y), 0.14, facecolor=TEAL, edgecolor=DARK_SLATE, lw=2.0, zorder=5)
    ax3.add_patch(bead)
    ax3.text(bead_x, bead_y, "$m$", fontsize=14.0, weight='bold', color=WHITE, ha='center', va='center', zorder=6)

    # Math card & explanation
    box_p3 = patches.FancyBboxPatch((-1.36, -1.68), 2.72, 0.98,
                                    boxstyle="round,pad=0.03,rounding_size=0.10",
                                    facecolor=WHITE, edgecolor=BORDER_COLOR, lw=1.3, zorder=2)
    ax3.add_patch(box_p3)

    ax3.text(0, -0.88, r"$q = s$", fontsize=22.0, weight='bold', color=NAVY, ha='center', va='center')
    ax3.text(0, -1.21, "Position along the track\nspecified by $s$",
             fontsize=16.5, weight='bold', color=DARK_SLATE, ha='center', va='center', linespacing=1.28)
    ax3.text(0, -1.53, r"$L(s,\dot{s}) = T - V$",
             fontsize=17.5, weight='bold', color=NAVY, ha='center', va='center')

    # =========================================================================
    # COMMON BOTTOM PIPELINE BAND
    # =========================================================================
    band_y = 0.024
    band_h = 0.200
    band_w = 0.930
    band_x = 0.035

    ax_band = fig.add_axes([band_x, band_y, band_w, band_h])
    ax_band.set_facecolor('#ffffff')
    ax_band.axis('off')
    ax_band.set_xlim(0, 10)
    ax_band.set_ylim(0, 10)

    # Background card for bottom band
    band_card = patches.FancyBboxPatch((0.05, 0.15), 9.90, 9.70,
                                       boxstyle="round,pad=0.04,rounding_size=0.35",
                                       facecolor='#ffffff', edgecolor='#94a3b8',
                                       lw=1.5, zorder=0)
    ax_band.add_patch(band_card)

    # Three-step mathematical pipeline
    # Step 1: Coordinates
    pill_step1 = patches.FancyBboxPatch((0.35, 3.80), 2.55, 5.40,
                                        boxstyle="round,pad=0.03,rounding_size=0.25",
                                        facecolor='#f8fafc', edgecolor=BORDER_COLOR, lw=1.3)
    ax_band.add_patch(pill_step1)
    ax_band.text(1.625, 7.80, "1. Choose Coordinates", fontsize=15.0, weight='bold', color=DARK_SLATE, ha='center')
    ax_band.text(1.625, 5.40, r"$q_1, \ldots, q_n$", fontsize=22.0, weight='bold', color=NAVY, ha='center', va='center')

    # Arrow 1 -> 2
    ax_band.annotate('', xy=(3.30, 6.50), xytext=(2.98, 6.50),
                     arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=3.2, mutation_scale=20))

    # Step 2: Construct the Lagrangian
    pill_step2 = patches.FancyBboxPatch((3.40, 3.80), 2.70, 5.40,
                                        boxstyle="round,pad=0.03,rounding_size=0.25",
                                        facecolor='#f8fafc', edgecolor=BORDER_COLOR, lw=1.3)
    ax_band.add_patch(pill_step2)
    ax_band.text(4.75, 7.80, "2. Construct the Lagrangian", fontsize=15.0, weight='bold', color=DARK_SLATE, ha='center')
    ax_band.text(4.75, 5.40, r"$L(q_i, \dot{q}_i, t) = T - V$", fontsize=19.5, weight='bold', color=NAVY, ha='center', va='center')

    # Arrow 2 -> 3
    ax_band.annotate('', xy=(6.50, 6.50), xytext=(6.18, 6.50),
                     arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=3.2, mutation_scale=20))

    # Step 3: Apply the Euler-Lagrange Equations
    pill_step3 = patches.FancyBboxPatch((6.60, 3.80), 3.05, 5.40,
                                        boxstyle="round,pad=0.03,rounding_size=0.25",
                                        facecolor='#f8fafc', edgecolor=BORDER_COLOR, lw=1.3)
    ax_band.add_patch(pill_step3)
    ax_band.text(8.125, 7.80, "3. Apply the Euler–Lagrange Equations", fontsize=14.5, weight='bold', color=DARK_SLATE, ha='center')
    ax_band.text(8.125, 5.40, r"$\frac{d}{dt}\left(\frac{\partial L}{\partial \dot{q}_i}\right) - \frac{\partial L}{\partial q_i} = 0$",
                 fontsize=21.0, weight='bold', color=NAVY, ha='center', va='center')

    # Summary sentence across the bottom of the band
    ax_band.text(5.0, 1.75,
                 "Choose coordinates that match the independent degrees of freedom, then apply the same Euler–Lagrange equation to each coordinate.",
                 fontsize=14.5, weight='bold', color=DARK_SLATE, ha='center', va='center')

    plt.savefig(output_path, dpi=240, bbox_inches='tight', pad_inches=0.35, facecolor='#ffffff', edgecolor='none')
    plt.close()
    print(f"Generated {output_path}")

if __name__ == "__main__":
    create_figure()
