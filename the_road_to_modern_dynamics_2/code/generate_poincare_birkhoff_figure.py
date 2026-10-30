#!/usr/bin/env python3
r"""
Generate infographic for Article 2:
"The Poincaré–Birkhoff Geometric Theorem and its Dynamical Interpretation"

Two-panel landscape layout:
1. Panel A (Opposite Boundary Rotations):
   - Area-preserving twist map of an annulus A = S^1 x [a, b].
   - Outer boundary: counterclockwise rotation (blue curved arrow).
   - Inner boundary: clockwise rotation (orange curved arrow).
   - Radial segment L (dark grey dashed) with endpoints a and b marked.
   - Transformed twisted image F(L) (thick purple solid curve) with endpoints F(a) and F(b) marked.
   - Boundary displacement arrows from a -> F(a) (clockwise) and b -> F(b) (counterclockwise).
   - Clear labels L and F(L) positioned directly alongside their curves.
   - At least two distinct fixed points p_1 and p_2 inside the annulus with clean callout.
   - Generous margins and no bottom boxes.

2. Panel B (Dynamical Interpretation):
   - Transverse Poincaré section Sigma suspended in 3D phase space.
   - Unmistakably closed 3D periodic orbit Gamma:
     * Segment above Sigma (z >= 0) is a solid thick emerald line.
     * Segment below/behind Sigma (z <= 0) is a dashed emerald line smoothly connecting
       from crossing point q back to fixed point p = F(p).
     * Transverse piercing at fixed point p = F(p) with clear flow arrows.
   - Dynamical Equivalence badge placed above section:
     F(p) = p  <===>  phi_T(p) = p (Poincaré first-return map with return time T).
   - Minimum font size >= 14.0 pt everywhere.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "poincare_birkhoff_theorem.png"


def project_3d(x, y, z, theta_deg=20.0, phi_deg=22.0):
    r"""Project 3D coordinates (x, y, z) into 2D view (u, v) with depth d."""
    rad_th = np.radians(theta_deg)
    rad_ph = np.radians(phi_deg)
    u = x * np.cos(rad_th) - y * np.sin(rad_th)
    d = x * np.sin(rad_th) + y * np.cos(rad_th)
    v = z * np.cos(rad_ph) + d * np.sin(rad_ph)
    return u, v, d


def draw_curved_arrow(ax, r, th_start_deg, th_end_deg, color, cx=0.0, cy=0.0, lw=3.2, head_size=0.085, zorder=10):
    r"""Draw a smooth circular arc with a well-proportioned arrowhead in polar coordinates centered at (cx, cy)."""
    ths = np.radians(np.linspace(th_start_deg, th_end_deg, 80))
    xs = cx + r * np.cos(ths)
    ys = cy + r * np.sin(ths)
    ax.plot(xs, ys, color=color, lw=lw, zorder=zorder)

    # Arrowhead tangent at th_end
    th_e = np.radians(th_end_deg)
    direction = np.sign(th_end_deg - th_start_deg)
    th_prev = np.radians(th_end_deg - 3.8 * direction)
    x_tip = cx + r * np.cos(th_e)
    y_tip = cy + r * np.sin(th_e)
    x_base = cx + r * np.cos(th_prev)
    y_base = cy + r * np.sin(th_prev)
    dx = x_tip - x_base
    dy = y_tip - y_base
    length = np.hypot(dx, dy)
    if length > 0:
        dx /= length
        dy /= length

    arrow = patches.FancyArrow(
        x_base, y_base, dx * head_size, dy * head_size,
        width=head_size * 0.40, head_width=head_size * 1.5, head_length=head_size * 1.6,
        length_includes_head=True, color=color, zorder=zorder + 1
    )
    ax.add_patch(arrow)


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

    # High-resolution widescreen canvas (16 x 8.8 inches at 120 DPI -> 1920 x 1056 px)
    fig_w = 16.0
    fig_h = 8.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=120, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#000000'          # Solid black for maximum contrast and legibility
    DARK_SLATE = '#000000'    # Solid black
    SLATE = '#000000'         # Solid black
    BORDER_CARD = '#cbd5e1'   # Card border
    BG_CARD = '#f8fafc'       # Light background for panels

    BLUE_ACCENT = '#2563eb'   # Primary blue accent (outer boundary)
    BLUE_LIGHT = '#eff6ff'    # Soft blue tint
    BLUE_BORDER = '#93c5fd'   # Blue card border

    EMERALD_ACCENT = '#059669' # Emerald for fixed points & periodic orbit
    EMERALD_LIGHT = '#ecfdf5'  # Soft emerald tint
    EMERALD_BORDER = '#6ee7b7' # Emerald border

    ORANGE_ACCENT = '#ea580c'  # Vibrant orange (inner boundary & fixed point marker)
    PURPLE_ACCENT = '#6366f1'  # Purple for twisted image F(L)

    # -------------------------------------------------------------
    # Main Header & Context Banner (>= 16 pt)
    # -------------------------------------------------------------
    fig.text(0.5, 0.965,
             "The Poincaré–Birkhoff Geometric Theorem",
             fontsize=24.0, weight='bold', color=NAVY, ha='center', va='center')

    fig.text(0.5, 0.928,
             "Area-preserving annulus twist maps and their correspondence to periodic orbits",
             fontsize=15.5, weight='normal', color='#334155', ha='center', va='center')

    # Background axis for panel cards and headers
    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')

    # Card layout parameters: full height inside canvas
    y_card = 0.040
    h_card = 0.860

    x1 = 0.026
    w1 = 0.464

    x2 = 0.510
    w2 = 0.464

    panels_spec = [
        (x1, w1, "A", "Opposite Boundary Rotations", "Area-Preserving Twist Map of an Annulus",
         BLUE_ACCENT, BLUE_LIGHT, BLUE_BORDER),
        (x2, w2, "B", "Dynamical Interpretation", "Fixed Points and Periodic Orbits",
         EMERALD_ACCENT, EMERALD_LIGHT, EMERALD_BORDER),
    ]

    for px, pw, letter, title, subtitle, acc_color, bg_tint, bdr_color in panels_spec:
        # Card container
        card_rect = patches.FancyBboxPatch(
            (px, y_card), pw, h_card,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.4,
            zorder=1
        )
        ax_bg.add_patch(card_rect)

        # Header accent bar
        hbar_h = 0.082
        hbar_rect = patches.FancyBboxPatch(
            (px, y_card + h_card - hbar_h), pw, hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=bg_tint, edgecolor=bdr_color, linewidth=1.2,
            zorder=2
        )
        ax_bg.add_patch(hbar_rect)

        # Letter Badge circle (A, B)
        badge_x = px + 0.024
        badge_y = y_card + h_card - hbar_h / 2
        badge_c = patches.Circle(
            (badge_x, badge_y), 0.017,
            facecolor=acc_color, edgecolor='none',
            zorder=3
        )
        ax_bg.add_patch(badge_c)
        ax_bg.text(badge_x, badge_y, letter, fontsize=16.5, weight='bold',
                   color='#ffffff', ha='center', va='center', zorder=4)

        # Title (bold) & subtitle (lighter normal weight for editorial elegance)
        ax_bg.text(badge_x + 0.024, badge_y + 0.015, title,
                   fontsize=17.5, weight='bold', color=NAVY, va='center', zorder=4)
        ax_bg.text(badge_x + 0.024, badge_y - 0.016, subtitle,
                   fontsize=14.5, weight='normal', color='#475569', va='center', zorder=4)

    # Plot coordinates: full height inside card below header bar
    y_plot = 0.055
    h_plot = 0.745

    # =========================================================================
    # PANEL A: Twist Map of an Annulus
    # =========================================================================
    ax1_w = 0.456
    ax1_x = x1 + (w1 - ax1_w) / 2
    ax1 = fig.add_axes([ax1_x, y_plot, ax1_w, h_plot], zorder=5)
    ax1.set_facecolor('#ffffff')
    ax1.set_aspect('equal')
    ax1.axis('off')

    # Centered annulus with generous left margin for editorial callouts
    cx = 0.11
    cy = 0.00

    r1 = 0.44  # Inner radius
    r2 = 1.02  # Outer radius

    # Annulus background shading
    ths = np.linspace(0, 2 * np.pi, 360)
    outer_poly = patches.Circle((cx, cy), r2, facecolor='#eff6ff', edgecolor='none', alpha=0.75, zorder=1)
    inner_poly = patches.Circle((cx, cy), r1, facecolor='#ffffff', edgecolor='none', zorder=2)
    ax1.add_patch(outer_poly)
    ax1.add_patch(inner_poly)

    # Reference circle at intermediate radius (where relative twist is zero)
    r_zero_twist = 0.715
    ax1.plot(cx + r_zero_twist * np.cos(ths), cy + r_zero_twist * np.sin(ths),
             color='#cbd5e1', lw=1.1, ls=':', zorder=2)

    # Outer boundary C2 (Solid Blue)
    ax1.plot(cx + r2 * np.cos(ths), cy + r2 * np.sin(ths), color='#1e40af', lw=2.4, zorder=3)
    # Inner boundary C1 (Solid Orange)
    ax1.plot(cx + r1 * np.cos(ths), cy + r1 * np.sin(ths), color='#c2410c', lw=2.4, zorder=3)

    # Outer boundary rotation arrow: counterclockwise (Blue) - centered at (cx, cy)
    draw_curved_arrow(ax1, r=1.12, th_start_deg=50, th_end_deg=130, color='#2563eb',
                      cx=cx, cy=cy, lw=3.2, head_size=0.085, zorder=10)
    ax1.text(cx, cy + 1.25, "Outer boundary: counterclockwise rotation",
             fontsize=15.0, weight='bold', color='#1e40af', ha='center', va='bottom', zorder=11)

    # Inner boundary rotation arrow: clockwise (Orange) - centered at (cx, cy)
    draw_curved_arrow(ax1, r=0.28, th_start_deg=145, th_end_deg=35, color='#ea580c',
                      cx=cx, cy=cy, lw=2.8, head_size=0.070, zorder=10)
    ax1.text(cx, cy - 0.02, "Inner boundary:\nclockwise\nrotation",
             fontsize=14.5, weight='bold', color='#c2410c', ha='center', va='center', zorder=11)

    # -------------------------------------------------------------
    # Radial Segment L and its Transformed Image F(L)
    # -------------------------------------------------------------
    th0_deg = 180.0             # Horizontal segment on negative x-axis
    th_in_deg = th0_deg - 40.0   # Clockwise displacement by 40 deg on inner boundary (140 deg)
    th_out_deg = th0_deg + 48.0  # Counterclockwise displacement by 48 deg on outer boundary (228 deg)

    # Original endpoints on boundaries
    ax_pt = np.array([cx + r1 * np.cos(np.radians(th0_deg)), cy + r1 * np.sin(np.radians(th0_deg))])
    bx_pt = np.array([cx + r2 * np.cos(np.radians(th0_deg)), cy + r2 * np.sin(np.radians(th0_deg))])

    # Transformed endpoints on boundaries
    Fa_pt = np.array([cx + r1 * np.cos(np.radians(th_in_deg)), cy + r1 * np.sin(np.radians(th_in_deg))])
    Fb_pt = np.array([cx + r2 * np.cos(np.radians(th_out_deg)), cy + r2 * np.sin(np.radians(th_out_deg))])

    # 1. Radial segment L (dark grey dashed line)
    r_pts = np.linspace(r1, r2, 120)
    x_l = cx + r_pts * np.cos(np.radians(th0_deg))
    y_l = cy + r_pts * np.sin(np.radians(th0_deg))
    ax1.plot(x_l, y_l, color='#334155', lw=2.6, ls='--', zorder=4)

    # Mark original endpoints a and b (dark slate dots)
    ax1.scatter([ax_pt[0]], [ax_pt[1]], s=100, color='#1e293b', edgecolor='#ffffff', lw=2.0, zorder=7)
    ax1.scatter([bx_pt[0]], [bx_pt[1]], s=100, color='#1e293b', edgecolor='#ffffff', lw=2.0, zorder=7)

    # Endpoint labels for a and b:
    # 'a' placed cleanly inside white interior circle to the right of the dot (never touching boundary circle)
    ax1.text(ax_pt[0] + 0.065, ax_pt[1], r"$a$",
             fontsize=16.5, weight='bold', color='#000000', ha='left', va='center', zorder=8)
    # 'b' placed cleanly to the left of the outer dot
    ax1.text(bx_pt[0] - 0.065, bx_pt[1], r"$b$",
             fontsize=16.5, weight='bold', color='#000000', ha='right', va='center', zorder=8)

    # Callout for Radial Segment L outside the blue outer circle with dotted leader line
    x_call_L = -1.58
    y_call_L = cy + 0.48
    ax1.text(x_call_L, y_call_L, "Radial\nsegment $L$",
             fontsize=14.5, weight='bold', color='#000000', ha='left', va='center', zorder=9)

    # Dotted leader line with arrow landing directly on segment L at x_land_L
    x_land_L = cx - 0.86
    ax1.annotate("", xy=(x_land_L, cy + 0.01), xytext=(-1.18, y_call_L - 0.07),
                 arrowprops=dict(arrowstyle="->", color='#000000', ls=':', lw=1.8, mutation_scale=14),
                 zorder=7)

    # 2. Twisted image F(L) (purple thick solid curve connecting Fa_pt to Fb_pt)
    th_fl_deg = th_in_deg + (th_out_deg - th_in_deg) * ((r_pts - r1) / (r2 - r1))
    x_fl = cx + r_pts * np.cos(np.radians(th_fl_deg))
    y_fl = cy + r_pts * np.sin(np.radians(th_fl_deg))
    ax1.plot(x_fl, y_fl, color='#7c3aed', lw=3.6, zorder=5)

    # Mark transformed endpoints F(a) and F(b) (purple dots)
    ax1.scatter([Fa_pt[0]], [Fa_pt[1]], s=120, color='#7c3aed', edgecolor='#ffffff', lw=2.0, zorder=8)
    ax1.scatter([Fb_pt[0]], [Fb_pt[1]], s=120, color='#7c3aed', edgecolor='#ffffff', lw=2.0, zorder=8)

    # Endpoint labels for F(a) and F(b):
    # F(a) placed immediately above its endpoint marker dot (solid black per point convention)
    ax1.text(Fa_pt[0], Fa_pt[1] + 0.08, r"$F(a)$",
             fontsize=15.5, weight='bold', color='#000000', ha='center', va='bottom', zorder=9)
    # F(b) placed cleanly below-left of outer dot (solid black per point convention)
    ax1.text(Fb_pt[0] - 0.06, Fb_pt[1] - 0.06, r"$F(b)$",
             fontsize=15.5, weight='bold', color='#000000', ha='right', va='top', zorder=9)

    # Callout for Twisted Image F(L) outside the blue outer circle with dotted leader line
    # Positioned at x = -1.58, y = cy - 0.36 (moved cleanly left, well inside enclosing panel)
    x_call_FL = -1.58
    y_call_FL = cy - 0.36
    ax1.text(x_call_FL, y_call_FL, "Twisted\nimage $F(L)$",
             fontsize=14.5, weight='bold', color='#6d28d9', ha='left', va='center', zorder=9)
    # Dotted leader line directed toward the lower half of the purple curve at index 68
    # Remains strictly at y <= -0.138 (never crosses segment L at y = 0) and passes cleanly
    # above the start of the blue displacement arrow
    idx_mid_fl = 68
    ax1.annotate("", xy=(x_fl[idx_mid_fl], y_fl[idx_mid_fl]), xytext=(-1.12, y_call_FL - 0.01),
                 arrowprops=dict(arrowstyle="->", color='#6d28d9', ls=':', lw=1.8, mutation_scale=14),
                 zorder=7)

    # -------------------------------------------------------------
    # Explicit Endpoint Displacement Arrows: a -> F(a) and b -> F(b)
    # -------------------------------------------------------------
    # 1. Inner boundary displacement: a -> F(a) (clockwise rotation)
    # Follows inner boundary from theta = 176 deg down to 148 deg (stops cleanly before F(a) at 140 deg)
    ths_disp_in = np.radians(np.linspace(176.0, 153.0, 30))
    ax1.plot(cx + r1 * np.cos(ths_disp_in), cy + r1 * np.sin(ths_disp_in),
             color='#ea580c', lw=3.4, zorder=9)
    # Arrowhead at 148 deg pointing clockwise along circle (fully unobscured)
    th_tip_in = np.radians(148.0)
    th_prev_in = np.radians(155.0)
    x_tip_in = cx + r1 * np.cos(th_tip_in)
    y_tip_in = cy + r1 * np.sin(th_tip_in)
    x_prev_in = cx + r1 * np.cos(th_prev_in)
    y_prev_in = cy + r1 * np.sin(th_prev_in)
    dx_in = x_tip_in - x_prev_in
    dy_in = y_tip_in - y_prev_in
    len_in = np.hypot(dx_in, dy_in)
    if len_in > 0:
        arrow_in = patches.FancyArrow(
            x_prev_in, y_prev_in, dx_in, dy_in,
            width=0.024, head_width=0.082, head_length=0.075,
            length_includes_head=True, color='#ea580c', zorder=10
        )
        ax1.add_patch(arrow_in)
    # Explicit endpoint displacement label for inner boundary:
    # Placed horizontally in the upper-left part of the annulus, moved slightly left and upward with visible gap to F(a)
    ax1.text(cx - 0.72, cy + 0.44, r"$a \mapsto F(a)$",
             fontsize=15.0, weight='bold', color='#c2410c', ha='center', va='center', zorder=11)

    # 2. Outer boundary displacement: b -> F(b) (counterclockwise rotation)
    # Drawn outside the outer circle at r = 1.14 from theta = 199.0 deg to 220.0 deg
    # Starts near b (180 deg) safely below the leader line and ends near F(b) (228 deg)
    r_disp_out = 1.14
    ths_disp_out = np.radians(np.linspace(199.0, 220.0, 40))
    ax1.plot(cx + r_disp_out * np.cos(ths_disp_out), cy + r_disp_out * np.sin(ths_disp_out),
             color='#2563eb', lw=3.4, zorder=9)
    # Arrowhead at 224 deg pointing counterclockwise along circular arc (never touches purple curve or F(b))
    th_tip_out = np.radians(224.0)
    th_prev_out = np.radians(217.0)
    x_tip_out = cx + r_disp_out * np.cos(th_tip_out)
    y_tip_out = cy + r_disp_out * np.sin(th_tip_out)
    x_prev_out = cx + r_disp_out * np.cos(th_prev_out)
    y_prev_out = cy + r_disp_out * np.sin(th_prev_out)
    dx_out = x_tip_out - x_prev_out
    dy_out = y_tip_out - y_prev_out
    len_out = np.hypot(dx_out, dy_out)
    if len_out > 0:
        arrow_out = patches.FancyArrow(
            x_prev_out, y_prev_out, dx_out, dy_out,
            width=0.026, head_width=0.088, head_length=0.082,
            length_includes_head=True, color='#2563eb', zorder=10
        )
        ax1.add_patch(arrow_out)
    # Explicit endpoint displacement label for outer boundary
    ax1.text(cx - 1.16, cy - 0.60, r"$b \mapsto F(b)$",
             fontsize=15.5, weight='bold', color='#1e40af', ha='right', va='center', zorder=11)

    # -------------------------------------------------------------
    # Fixed Points p1 and p2 (Illustrative Fixed Points)
    # -------------------------------------------------------------
    # Positioned at distinct angular positions in upper-right and lower-right quadrants
    r_fp = r_zero_twist
    th_p1 = np.radians(35.0)    # Upper-right quadrant
    th_p2 = np.radians(-42.0)   # Lower-right quadrant
    p1 = (cx + r_fp * np.cos(th_p1), cy + r_fp * np.sin(th_p1))
    p2 = (cx + r_fp * np.cos(th_p2), cy + r_fp * np.sin(th_p2))

    # Glow & marker for p1
    ax1.scatter([p1[0]], [p1[1]], s=280, color='#059669', edgecolor='#ffffff', lw=2.8, zorder=8)
    ax1.text(p1[0] - 0.09, p1[1], r"$\mathbf{p_1}$",
             fontsize=18.5, weight='bold', color='#065f46', ha='right', va='center', zorder=9)

    # Glow & marker for p2
    ax1.scatter([p2[0]], [p2[1]], s=280, color='#059669', edgecolor='#ffffff', lw=2.8, zorder=8)
    ax1.text(p2[0] - 0.09, p2[1], r"$\mathbf{p_2}$",
             fontsize=18.5, weight='bold', color='#065f46', ha='right', va='center', zorder=9)

    # Compact fixed-point explanation centered below the annulus (no clutter or right-border spill)
    ax1.text(cx, cy - 1.18, r"$F(\mathbf{p_1}) = \mathbf{p_1}, \qquad F(\mathbf{p_2}) = \mathbf{p_2}$",
             fontsize=17.5, weight='bold', color='#065f46', ha='center', va='center', zorder=9)

    ax1.set_xlim(-1.68, 1.38)
    ax1.set_ylim(-1.32, 1.36)

    # =========================================================================
    # PANEL B: Dynamical Interpretation (Closed Periodic Orbit & Poincaré Section)
    # =========================================================================
    ax2_w = 0.440
    ax2_x = x2 + (w2 - ax2_w) / 2
    ax2 = fig.add_axes([ax2_x, y_plot, ax2_w, h_plot], zorder=5)
    ax2.set_facecolor('#ffffff')
    ax2.axis('off')

    th_cam = 20.0
    ph_cam = 22.0

    # 1. Dynamical Equivalence Banner (Centered at top of Panel B with generous width)
    badge_w = 2.45
    badge_h = 0.46
    badge_b = patches.FancyBboxPatch(
        (-badge_w / 2, 0.84), badge_w, badge_h,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        facecolor='#ffffff', edgecolor='#93c5fd', linewidth=1.4,
        alpha=0.96, zorder=8
    )
    ax2.add_patch(badge_b)
    ax2.text(0.00, 1.18, "Dynamical Equivalence",
             fontsize=16.0, weight='bold', color='#1e40af', ha='center', va='center', zorder=9)
    ax2.text(0.00, 1.04,
             r"$F(\mathbf{p}) = \mathbf{p} \;\;\Longleftrightarrow\;\; \phi_T(\mathbf{p}) = \mathbf{p}$",
             fontsize=18.0, weight='bold', color=NAVY, ha='center', va='center', zorder=9)
    ax2.text(0.00, 0.91,
             r"First-return map $F$ with return time $T$ at point $\mathbf{p}$",
             fontsize=15.0, weight='bold', color=NAVY, ha='center', va='center', zorder=9)

    # 2. Poincaré Section Sigma (Horizontal plane polygon at z = 0)
    corners_sigma = np.array([
        [-1.25, -0.95, 0.0],
        [ 1.25, -0.95, 0.0],
        [ 1.25,  0.95, 0.0],
        [-1.25,  0.95, 0.0]
    ])
    su, sv, _ = project_3d(corners_sigma[:, 0], corners_sigma[:, 1], corners_sigma[:, 2], th_cam, ph_cam)

    poly_sigma = patches.Polygon(np.column_stack([su, sv]), closed=True,
                                 facecolor='#f8fafc', edgecolor='#64748b',
                                 lw=1.8, alpha=0.55, zorder=2)
    ax2.add_patch(poly_sigma)

    # Perspective coordinate grid on Sigma
    for gx in np.linspace(-0.9, 0.9, 5):
        line = np.array([[gx, -0.95, 0.0], [gx, 0.95, 0.0]])
        lu, lv, _ = project_3d(line[:, 0], line[:, 1], line[:, 2], th_cam, ph_cam)
        ax2.plot(lu, lv, color='#e2e8f0', lw=0.9, ls='-', zorder=3)
    for gy in np.linspace(-0.7, 0.7, 5):
        line = np.array([[-1.25, gy, 0.0], [1.25, gy, 0.0]])
        lu, lv, _ = project_3d(line[:, 0], line[:, 1], line[:, 2], th_cam, ph_cam)
        ax2.plot(lu, lv, color='#e2e8f0', lw=0.9, ls='-', zorder=3)

    # Section Sigma Label (bold NAVY below section plane)
    ax2.text(su[0] - 0.08, sv[0] - 0.10, r"Poincaré section $\mathbf{\Sigma}$",
             fontsize=15.5, weight='bold', color=NAVY, ha='left', va='top', zorder=4)

    # 3. Unmistakably Closed 3D Periodic Orbit Gamma
    # Well-proportioned planar 3D loop intersecting Sigma at p (t=0) and q (t=pi):
    center = np.array([0.05, -0.05, 0.0])
    v1 = np.array([0.40, -0.45, 0.0])
    v2 = np.array([-0.28, 0.38, 0.62])

    p_3d = center + v1  # Transverse piercing point at t=0 and t=2*pi
    q_3d = center - v1  # Downward crossing point into lower half-space at t=pi

    t_orb = np.linspace(0, 2 * np.pi, 500)
    xt = center[0] + v1[0] * np.cos(t_orb) + v2[0] * np.sin(t_orb)
    yt = center[1] + v1[1] * np.cos(t_orb) + v2[1] * np.sin(t_orb)
    zt = center[2] + v1[2] * np.cos(t_orb) + v2[2] * np.sin(t_orb)

    ou, ov, od = project_3d(xt, yt, zt, th_cam, ph_cam)

    # Upper segment above Sigma (z >= 0, t from 0 to pi): Solid thick emerald line
    mask_above = (t_orb <= np.pi)
    ax2.plot(ou[mask_above], ov[mask_above], color='#059669', lw=3.4, zorder=6)

    # Lower segment below/behind Sigma (z <= 0, t from pi to 2*pi): Dashed emerald line
    mask_below = (t_orb >= np.pi)
    ax2.plot(ou[mask_below], ov[mask_below], color='#059669', lw=2.6, ls='--', alpha=0.85, zorder=1)

    # Flow arrows on periodic orbit:
    # Arrow 1: Rising upward through Sigma (t = 0.55)
    t_a1 = 0.55
    idx_a1 = int(t_a1 / (2 * np.pi) * len(t_orb))
    dx1 = ou[idx_a1 + 1] - ou[idx_a1]
    dy1 = ov[idx_a1 + 1] - ov[idx_a1]
    norm1 = np.hypot(dx1, dy1)
    if norm1 > 0:
        ax2.annotate("", xy=(ou[idx_a1] + dx1/norm1 * 0.08, ov[idx_a1] + dy1/norm1 * 0.08),
                     xytext=(ou[idx_a1], ov[idx_a1]),
                     arrowprops=dict(arrowstyle="->", color='#059669', lw=2.6, mutation_scale=19),
                     zorder=7)

    # Arrow 2: Arching descent through point q (t = 2.45)
    t_a2 = 2.45
    idx_a2 = int(t_a2 / (2 * np.pi) * len(t_orb))
    dx2 = ou[idx_a2 + 1] - ou[idx_a2]
    dy2 = ov[idx_a2 + 1] - ov[idx_a2]
    norm2 = np.hypot(dx2, dy2)
    if norm2 > 0:
        ax2.annotate("", xy=(ou[idx_a2] + dx2/norm2 * 0.08, ov[idx_a2] + dy2/norm2 * 0.08),
                     xytext=(ou[idx_a2], ov[idx_a2]),
                     arrowprops=dict(arrowstyle="->", color='#059669', lw=2.6, mutation_scale=19),
                     zorder=7)

    # Arrow 3: Curving underneath (t = 4.40)
    t_a3 = 4.40
    idx_a3 = int(t_a3 / (2 * np.pi) * len(t_orb))
    dx3 = ou[idx_a3 + 1] - ou[idx_a3]
    dy3 = ov[idx_a3 + 1] - ov[idx_a3]
    norm3 = np.hypot(dx3, dy3)
    if norm3 > 0:
        ax2.annotate("", xy=(ou[idx_a3] + dx3/norm3 * 0.08, ov[idx_a3] + dy3/norm3 * 0.08),
                     xytext=(ou[idx_a3], ov[idx_a3]),
                     arrowprops=dict(arrowstyle="->", color='#059669', lw=2.2, mutation_scale=17),
                     zorder=2)

    # Arrow 4: Rising upward returning back into point p (t = 5.75)
    t_a4 = 5.75
    idx_a4 = int(t_a4 / (2 * np.pi) * len(t_orb))
    dx4 = ou[idx_a4 + 1] - ou[idx_a4]
    dy4 = ov[idx_a4 + 1] - ov[idx_a4]
    norm4 = np.hypot(dx4, dy4)
    if norm4 > 0:
        ax2.annotate("", xy=(ou[idx_a4] + dx4/norm4 * 0.08, ov[idx_a4] + dy4/norm4 * 0.08),
                     xytext=(ou[idx_a4], ov[idx_a4]),
                     arrowprops=dict(arrowstyle="->", color='#059669', lw=2.4, mutation_scale=18),
                     zorder=2)

    # Highlighted Fixed Point p on Sigma (only p = F(p), no cluttered subtext)
    pu, pv, _ = project_3d(p_3d[0], p_3d[1], p_3d[2], th_cam, ph_cam)
    ax2.scatter([pu], [pv], s=280, color='#ea580c', edgecolor='#ffffff', lw=2.8, zorder=9)
    ax2.text(pu + 0.08, pv + 0.02, r"$\mathbf{p} = F(\mathbf{p})$",
             fontsize=17.5, weight='bold', color='#9a3412', ha='left', va='center', zorder=10)

    # Label for periodic orbit Gamma (moved to the right side of the loop, bold NAVY)
    x_orb_label = 0.42
    y_orb_label = 0.60
    ax2.text(x_orb_label, y_orb_label + 0.05,
             r"Periodic orbit $\mathbf{\Gamma}$",
             fontsize=16.5, weight='bold', color='#065f46', ha='left', va='center', zorder=8)
    ax2.text(x_orb_label, y_orb_label - 0.05,
             r"Closed trajectory $\phi_t(\mathbf{p})$",
             fontsize=14.5, weight='bold', color=NAVY, ha='left', va='center', zorder=8)

    ax2.set_xlim(-1.45, 1.45)
    ax2.set_ylim(-1.18, 1.34)

    plt.savefig(output_path, dpi=120, facecolor='#ffffff')
    plt.close()
    print(f"[OK] Poincaré-Birkhoff theorem figure saved to: {output_path}")


if __name__ == "__main__":
    create_figure()
