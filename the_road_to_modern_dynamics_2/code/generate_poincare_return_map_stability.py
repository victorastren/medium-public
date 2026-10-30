#!/usr/bin/env python3
r"""
Generate infographic for Article 2:
"Periodic Orbits and Stability: The Poincaré Return Map"

Mathematical Assessment & Refinements:
1. Panel 1 (Poincaré Return Map):
   - Transverse section Sigma suspended in 3D with perspective grid.
   - Three labeled points P_0, P_1, P_2 on Sigma, strictly representing successive upward crossings.
   - At each P_n, trajectory visibly crosses Sigma upward, transitioning from dashed below to solid above.
   - Upward flow arrows on the rising dashed segment into P_n, and on the rising solid segment out of P_n.
   - Between P_0 and P_1, solid trajectory arches above Sigma, curves downward with a flow arrow,
     crosses the plane at an unlabeled point (anchored with a subtle surface piercing marker),
     and continues below the plane as a dashed curve returning upward through P_1.
   - Identical consistent geometry between P_1 and P_2, and continuing after P_2.
   - Orange dashed arrows along Sigma connect P_0 -> P_1 -> P_2, representing the discrete return map.
   - "3D Phase Space: \dot{x} = f(x)" rendered in dark slate bold.

2. Panel 2 (Stable Periodic Orbit):
   - Retained |\mu_i| < 1 (\forall i) for all transverse multipliers.
   - Stability badge: Heading "Asymptotic Stability", math |\mu_i| < 1 (\forall i).
   - Fixed point P* shifted to (0, -0.20) providing generous vertical clearance (>0.35) below badge.
   - Clean inward contraction sequence P_0 -> P_1 -> ... -> P_4 toward fixed point P*.

3. Panel 3 (Unstable Periodic Orbit):
   - Parallel panel title: "Unstable Periodic Orbit" with subtitle "Growth of Perturbations".
   - Instability badge: Heading "Instability", math |\mu_i| > 1 (\exists i).
   - Fixed point P* shifted to (0, -0.20) providing generous vertical clearance (>0.30) below badge.
   - Clean outward growth sequence P_0 -> P_1 -> ... -> P_4.
   - Perturbation vector to P_4 explicitly labeled \delta P_4.

4. Layout, Typography & Visual Balance:
   - Raised plot area (y_plot = 0.245) and bottom box (h_box = 0.124 at y_box = 0.040) providing
     ample separation between horizontal axis labels and explanatory boxes.
   - Vertical labels "Section coordinate \xi_2" exactly centered inside the gaps between plot boxes.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "poincare_return_map_stability.png"


def project_3d_table(x, y, z, theta_deg=14.0, phi_deg=22.0):
    r"""
    Project 3D coordinates (x, y, z) where z = 0 is a horizontal section plane (tabletop).
    theta_deg: tilt angle in the horizontal plane.
    phi_deg: elevation angle (looking down onto the table).
    """
    rad_th = np.radians(theta_deg)
    rad_ph = np.radians(phi_deg)

    u = x * np.cos(rad_th) - y * np.sin(rad_th)
    d = x * np.sin(rad_th) + y * np.cos(rad_th)
    v = z * np.cos(rad_ph) + d * np.sin(rad_ph)
    return u, v, d


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
    BORDER_CARD = '#cbd5e1'   # Card border
    BG_CARD = '#f8fafc'       # Light background for panels
    BG_BOX = '#ffffff'        # Pure white for callout cards

    BLUE_ACCENT = '#2563eb'   # Primary blue accent
    BLUE_LIGHT = '#eff6ff'    # Soft blue tint
    BLUE_BORDER = '#93c5fd'   # Blue card border

    EMERALD_ACCENT = '#059669' # Emerald for stable orbit
    EMERALD_LIGHT = '#ecfdf5'  # Soft emerald tint
    EMERALD_BORDER = '#6ee7b7' # Emerald border

    AMBER_ACCENT = '#d97706'  # Amber for unstable orbit
    AMBER_LIGHT = '#fffbeb'   # Soft amber tint
    AMBER_BORDER = '#fcd34d'  # Amber border

    ORANGE_FP = '#ea580c'     # Distinct orange for fixed point P*

    # -------------------------------------------------------------
    # Main Header & Context Banner (>= 16.5 pt)
    # -------------------------------------------------------------
    fig.text(0.5, 0.962,
             "Periodic Orbits and Stability: The Poincaré Return Map",
             fontsize=21.0, weight='bold', color=NAVY, ha='center', va='center')

    fig.text(0.5, 0.925,
             "Reducing continuous phase-space trajectories to discrete surface crossings and Floquet multiplier stability",
             fontsize=16.5, style='italic', color=DARK_SLATE, ha='center', va='center')

    # Background axis for panel cards, headers, badges, and summary boxes
    ax_bg = fig.add_axes([0, 0, 1, 1], zorder=0)
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')

    # Card layout parameters: 3 equal cards of width 0.304 each
    y_card = 0.038
    h_card = 0.858

    x1 = 0.024
    w1 = 0.304

    x2 = 0.346
    w2 = 0.304

    x3 = 0.668
    w3 = 0.304

    panels_spec = [
        (x1, w1, "1", "Poincaré Return Map", "Continuous Flow to Discrete Map",
         BLUE_ACCENT, BLUE_LIGHT, BLUE_BORDER),
        (x2, w2, "2", "Stable Periodic Orbit", "Contraction of Perturbations",
         EMERALD_ACCENT, EMERALD_LIGHT, EMERALD_BORDER),
        (x3, w3, "3", "Unstable Periodic Orbit", "Growth of Perturbations",
         AMBER_ACCENT, AMBER_LIGHT, AMBER_BORDER),
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
        hbar_h = 0.082
        hbar_rect = patches.FancyBboxPatch(
            (px, y_card + h_card - hbar_h), pw, hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=bg_tint, edgecolor=bdr_color, linewidth=1.2,
            zorder=2
        )
        ax_bg.add_patch(hbar_rect)

        # Number Badge circle (1, 2, 3)
        badge_x = px + 0.022
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
        ax_bg.text(badge_x + 0.022, badge_y + 0.015, title,
                   fontsize=17.5, weight='bold', color=NAVY, va='center', zorder=4)
        ax_bg.text(badge_x + 0.022, badge_y - 0.016, subtitle,
                   fontsize=15.0, weight='bold', color='#475569', va='center', zorder=4)

    # Vertical coordinates for plotting areas and bottom boxes
    y_box = 0.040
    h_box = 0.124
    y_plot = 0.245
    h_plot = 0.548

    # =========================================================================
    # PANEL 1: Poincaré Return Map (Single Continuous 3D Trajectory)
    # =========================================================================
    ax1_w = 0.252
    ax1_x = x1 + (w1 - ax1_w) / 2
    ax1 = fig.add_axes([ax1_x, y_plot, ax1_w, h_plot], zorder=5)
    ax1.set_facecolor('#ffffff')

    ax1.set_xticks([])
    ax1.set_yticks([])
    for spine in ax1.spines.values():
        spine.set_color('#cbd5e1')
        spine.set_linewidth(1.0)

    theta_cam = 14.0
    phi_cam = 22.0

    # 1. Section Sigma: bounded rectangle at z = 0
    corners_sigma = np.array([
        [-1.30, -1.20, 0.0],
        [ 1.50, -1.20, 0.0],
        [ 1.50,  0.85, 0.0],
        [-1.30,  0.85, 0.0]
    ])
    su, sv, _ = project_3d_table(corners_sigma[:, 0], corners_sigma[:, 1], corners_sigma[:, 2], theta_cam, phi_cam)

    # Polygon Sigma (semi-transparent plane)
    poly_sigma = patches.Polygon(np.column_stack([su, sv]), closed=True,
                                 facecolor='#f8fafc', edgecolor='#64748b',
                                 lw=1.6, alpha=0.50, zorder=3)
    ax1.add_patch(poly_sigma)

    # Perspective Grid lines on Sigma
    for gx in np.linspace(-1.0, 1.2, 6):
        gu, gv, _ = project_3d_table(np.array([gx, gx]), np.array([-1.20, 0.85]), np.array([0.0, 0.0]), theta_cam, phi_cam)
        ax1.plot(gu, gv, color='#cbd5e1', lw=0.9, linestyle=':', zorder=4)
    for gy in np.linspace(-0.8, 0.6, 4):
        gu, gv, _ = project_3d_table(np.array([-1.30, 1.50]), np.array([gy, gy]), np.array([0.0, 0.0]), theta_cam, phi_cam)
        ax1.plot(gu, gv, color='#cbd5e1', lw=0.9, linestyle=':', zorder=4)

    # Single continuous trajectory parameterization for t in [-0.40, 2.60]
    # Successive upward crossings strictly at t = 0 (P_0), t = 1 (P_1), t = 2 (P_2) with dz/dt > 0
    # Intermediate downward crossings at t = 0.5 (D_0), t = 1.5 (D_1), t = 2.5 (D_2) with dz/dt < 0
    t = np.linspace(-0.40, 2.60, 3000)
    psi = 2 * np.pi * t
    Az_above = 1.08
    Az_below = 0.42
    sin_psi = np.sin(psi)
    traj_z = np.where(sin_psi >= 0, Az_above * sin_psi, Az_below * sin_psi)

    traj_x = -0.32 + 0.58 * t + 0.12 * (1.0 - np.cos(psi))
    traj_y = 0.12 + 0.10 * t - 0.42 * np.cos(psi) + 0.05 * np.sin(psi)

    tu, tv, _ = project_3d_table(traj_x, traj_y, traj_z, theta_cam, phi_cam)

    is_below = traj_z < 0
    split_idx = np.where(np.diff(is_below.astype(int)) != 0)[0] + 1
    chunks_u = np.split(tu, split_idx)
    chunks_v = np.split(tv, split_idx)
    chunks_bel = np.split(is_below, split_idx)

    # Under-table segments (dashed blue, below Sigma, zorder=6 so clearly visible through translucent table!)
    for cu, cv, cb in zip(chunks_u, chunks_v, chunks_bel):
        if cb[0]:
            ax1.plot(cu, cv, color='#2563eb', lw=2.8, linestyle=(0, (4, 3)), alpha=0.95, zorder=6)

    # Above-table segments (solid royal blue, above Sigma, zorder=7)
    for cu, cv, cb in zip(chunks_u, chunks_v, chunks_bel):
        if not cb[0]:
            ax1.plot(cu, cv, color='#1d4ed8', lw=3.2, solid_capstyle='round', zorder=7)

    # Unlabeled downward crossings on Sigma: subtle small dots showing downward piercing
    for k_down in [0.5, 1.5, 2.5]:
        idx_d = np.argmin(np.abs(t - k_down))
        ax1.scatter([tu[idx_d]], [tv[idx_d]], color='#94a3b8', s=40, edgecolor='#475569', lw=1.2, zorder=8)

    # Upward Flow Arrows on rising solid segments right after P_n (dz/dt > 0)
    for t_up in [0.12, 1.12, 2.12]:
        idx_a = np.argmin(np.abs(t - t_up))
        dua = tu[idx_a + 2] - tu[idx_a - 2]
        dva = tv[idx_a + 2] - tv[idx_a - 2]
        na = np.hypot(dua, dva)
        ax1.annotate('', xy=(tu[idx_a] + 0.045*dua/na, tv[idx_a] + 0.045*dva/na),
                     xytext=(tu[idx_a] - 0.045*dua/na, tv[idx_a] - 0.045*dva/na),
                     arrowprops=dict(arrowstyle='-|>', color='#1d4ed8', lw=2.4, mutation_scale=16, shrinkA=0, shrinkB=0),
                     zorder=9)

    # Upward Flow Arrows on rising dashed segments right before P_n (dz/dt > 0, heading up into P_n!)
    for t_rise in [-0.08, 0.92, 1.92]:
        idx_r = np.argmin(np.abs(t - t_rise))
        dua = tu[idx_r + 2] - tu[idx_r - 2]
        dva = tv[idx_r + 2] - tv[idx_r - 2]
        na = np.hypot(dua, dva)
        ax1.annotate('', xy=(tu[idx_r] + 0.04*dua/na, tv[idx_r] + 0.04*dva/na),
                     xytext=(tu[idx_r] - 0.04*dua/na, tv[idx_r] - 0.04*dva/na),
                     arrowprops=dict(arrowstyle='->', color='#2563eb', lw=2.2, mutation_scale=14, shrinkA=0, shrinkB=0),
                     zorder=9)

    # Downward Flow Arrows on descending solid segments before the downward crossing
    for t_dn in [0.38, 1.38, 2.38]:
        idx_dn = np.argmin(np.abs(t - t_dn))
        dua = tu[idx_dn + 2] - tu[idx_dn - 2]
        dva = tv[idx_dn + 2] - tv[idx_dn - 2]
        na = np.hypot(dua, dva)
        ax1.annotate('', xy=(tu[idx_dn] + 0.04*dua/na, tv[idx_dn] + 0.04*dva/na),
                     xytext=(tu[idx_dn] - 0.04*dua/na, tv[idx_dn] - 0.04*dva/na),
                     arrowprops=dict(arrowstyle='-|>', color='#1d4ed8', lw=2.0, mutation_scale=14, shrinkA=0, shrinkB=0),
                     zorder=9)

    # Continuous Flow label placed gracefully above Loop 2
    ax1.text(0.70, 1.38, r"$\mathbf{Continuous\;Flow}\;\boldsymbol{\phi_t}$",
             fontsize=14.5, style='italic', color='#1d4ed8', ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.22", facecolor='#ffffff', edgecolor='#bfdbfe', lw=0.9),
             zorder=8)

    # Transverse Section label placed in lower-right margin of the tabletop
    ax1.text(1.42, -0.55, r"$\mathbf{Section}\;\boldsymbol{\Sigma}$",
             fontsize=15.5, weight='bold', color='#334155', ha='right', va='center',
             bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#94a3b8', lw=1.0),
             zorder=6)

    # Successive upward intersection points P_0, P_1, P_2 on Sigma
    pts_u = []
    pts_v = []
    for k, lbl in enumerate([r"$\boldsymbol{P_0}$", r"$\boldsymbol{P_1}$", r"$\boldsymbol{P_2}$"]):
        idx_k = np.argmin(np.abs(t - k))
        pu = tu[idx_k]
        pv = tv[idx_k]
        pts_u.append(pu)
        pts_v.append(pv)
        ax1.scatter([pu], [pv], color='#1d4ed8', s=160, zorder=11)
        ax1.scatter([pu], [pv], color='#ffffff', s=70, zorder=12)
        # Offset badge to bottom-right so the trajectory arrival path is completely unobstructed
        ax1.text(pu + 0.14, pv - 0.14, lbl,
                 fontsize=16.5, weight='bold', color='#0f172a', ha='center', va='center',
                 bbox=dict(boxstyle="round,pad=0.20", facecolor='#ffffff', edgecolor='#93c5fd', lw=1.0),
                 zorder=13)

    # Discrete map arrows connecting successive upward intersections along Sigma
    ax1.annotate('', xy=(pts_u[1] - 0.06, pts_v[1] + 0.02), xytext=(pts_u[0] + 0.06, pts_v[0] + 0.02),
                 arrowprops=dict(arrowstyle="->", color='#d97706', lw=2.4, linestyle='--',
                                 connectionstyle="arc3,rad=-0.16"),
                 zorder=10)
    ax1.annotate('', xy=(pts_u[2] - 0.06, pts_v[2] + 0.02), xytext=(pts_u[1] + 0.06, pts_v[1] + 0.02),
                 arrowprops=dict(arrowstyle="->", color='#d97706', lw=2.4, linestyle='--',
                                 connectionstyle="arc3,rad=-0.16"),
                 zorder=10)

    # Callout badge in upper-left defining return map
    ax1.text(-1.50, 1.25,
             r"$\mathbf{Return\;Map}$" "\n"
             r"$\boldsymbol{F:\Sigma \to \Sigma}$" "\n"
             r"$\boldsymbol{P_{n+1} = F(P_n)}$",
             fontsize=16.0, weight='bold', color='#b45309', ha='left', va='center',
             bbox=dict(boxstyle="round,pad=0.28", facecolor='#fffbeb', edgecolor='#fcd34d', lw=1.2),
             zorder=13)

    # Phase space label at bottom-left in dark slate bold
    ax1.text(-1.50, -1.45, r"$\mathbf{Three\text{-}dimensional\;phase\;space:}\;\dot{x} = f(x)$",
             fontsize=13.5, weight='bold', color='#1e293b', ha='left', va='center', zorder=6)

    ax1.set_xlim(-1.65, 1.65)
    ax1.set_ylim(-1.65, 1.65)

    # Bottom caption box for Panel 1
    box1 = patches.FancyBboxPatch(
        (x1 + 0.010, y_box), w1 - 0.020, h_box,
        boxstyle="round,pad=0.0,rounding_size=0.016",
        facecolor=BG_BOX, edgecolor=BORDER_CARD, linewidth=1.2,
        zorder=3
    )
    ax_bg.add_patch(box1)

    ax_bg.text(x1 + w1/2, y_box + h_box/2,
               "Successive upward crossings of the section Σ\ndefine the Poincaré return map Pₙ₊₁ = F(Pₙ).",
               fontsize=13.2, weight='bold', color=DARK_SLATE, ha='center', va='center',
               linespacing=1.30, zorder=4)

    # =========================================================================
    # PANEL 2: Stable Periodic Orbit (Face-on 2D section)
    # =========================================================================
    ax2_w = 0.245
    ax2_x = 0.375
    ax2 = fig.add_axes([ax2_x, y_plot, ax2_w, h_plot], zorder=5)
    ax2.set_facecolor('#ffffff')

    # Shift fixed point slightly down to (0, -0.20) to clear space below badge
    fp_y = -0.20
    theta_step = np.radians(34.0)
    contract_factor = 0.60
    r0_stable = 1.35
    phi0_stable = np.radians(24.0)

    num_pts_stable = 5
    pts_stable = []
    for n in range(num_pts_stable):
        rn = r0_stable * (contract_factor ** n)
        phin = phi0_stable + n * theta_step
        pts_stable.append([rn * np.cos(phin), fp_y + rn * np.sin(phin)])
    pts_stable = np.array(pts_stable)

    # Concentric reference contour circles showing contraction centered at (0, fp_y)
    for r_circ in [0.29, 0.49, 0.81, 1.35]:
        c_patch = patches.Circle((0, fp_y), r_circ, facecolor='none', edgecolor='#e2e8f0',
                                 lw=1.0, linestyle='--', zorder=1)
        ax2.add_patch(c_patch)

    # Arrows connecting successive iterations P_n -> P_{n+1} (inward)
    for n in range(num_pts_stable - 1):
        p_curr = pts_stable[n]
        p_next = pts_stable[n+1]
        ax2.annotate('', xy=(p_next[0], p_next[1]), xytext=(p_curr[0], p_curr[1]),
                     arrowprops=dict(arrowstyle="->", color='#059669', lw=2.4,
                                     connectionstyle="arc3,rad=-0.14"),
                     zorder=4)

    # Plot sequence points P_n
    for n, pt in enumerate(pts_stable):
        ax2.scatter([pt[0]], [pt[1]], color='#2563eb', edgecolor='#1e3a8a', s=130, linewidth=2.0, zorder=6)
        lbl = rf"$\boldsymbol{{P_{n}}}$"
        off_x = 0.18 * np.cos(phi0_stable + n * theta_step + 0.35)
        off_y = 0.18 * np.sin(phi0_stable + n * theta_step + 0.35)
        ax2.text(pt[0] + off_x, pt[1] + off_y, lbl,
                 fontsize=16.0, weight='bold', color='#1e3a8a', ha='center', va='center',
                 bbox=dict(boxstyle="round,pad=0.20", facecolor='#ffffff', edgecolor='#93c5fd', lw=0.9),
                 zorder=7)

    # Initial perturbation vector \delta P_0 from P* to P_0
    ax2.annotate('', xy=(pts_stable[0][0], pts_stable[0][1]), xytext=(0, fp_y),
             arrowprops=dict(arrowstyle="<->", color='#b45309', lw=2.2, linestyle=':'),
             zorder=3)
    ax2.text(pts_stable[0][0] * 0.52 - 0.14, fp_y + (pts_stable[0][1] - fp_y) * 0.52 + 0.14,
         r"$\boldsymbol{\delta P_0}$",
         fontsize=16.0, weight='bold', color='#b45309', ha='center', va='center',
         bbox=dict(boxstyle="round,pad=0.20", facecolor='#ffffff', edgecolor='#fcd34d', lw=0.9),
         zorder=8)

    # Fixed point P* in Orange
    ax2.scatter([0], [fp_y], color=ORANGE_FP, edgecolor='#7c2d12', s=160, linewidth=2.4, zorder=10)
    ax2.annotate(
        r"$\mathbf{Fixed\;Point}\;\boldsymbol{P^*}$" "\n" r"(Periodic Orbit)",
        xy=(0, fp_y), xytext=(0.0, fp_y - 0.40),
        fontsize=15.5, weight='bold', color='#9a3412', ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#fdba74', lw=1.0),
        arrowprops=dict(arrowstyle="->", color='#9a3412', lw=1.6),
        zorder=11
    )

    # Asymptotic Stability Badge
    ax2.text(-1.42, 1.25,
             r"$\mathbf{Asymptotic\;Stability}$" "\n"
             r"$\boldsymbol{|\mu_i| < 1}\quad(\forall i)$",
             fontsize=16.5, weight='bold', color='#065f46', ha='left', va='center',
             bbox=dict(boxstyle="round,pad=0.30", facecolor='#ecfdf5', edgecolor='#6ee7b7', lw=1.3),
             zorder=12)

    ax2.set_xlim(-1.65, 1.65)
    ax2.set_ylim(-1.65, 1.65)
    ax2.set_xlabel(r"Section coordinate $\xi_1$", fontsize=16.0, weight='bold', color=DARK_SLATE, labelpad=6)
    ax2.tick_params(labelsize=14.0, colors=SLATE)
    ax2.grid(True, linestyle=':', alpha=0.45, color='#cbd5e1')

    # Bottom caption box for Panel 2
    box2 = patches.FancyBboxPatch(
        (x2 + 0.010, y_box), w2 - 0.020, h_box,
        boxstyle="round,pad=0.0,rounding_size=0.016",
        facecolor=BG_BOX, edgecolor=BORDER_CARD, linewidth=1.2,
        zorder=3
    )
    ax_bg.add_patch(box2)

    ax_bg.text(x2 + w2/2, y_box + h_box/2,
               "Near a stable periodic orbit, successive\nintersections contract toward fixed point P*:\n|μᵢ| < 1 for all transverse Floquet multipliers.",
               fontsize=13.5, weight='bold', color=DARK_SLATE, ha='center', va='center',
               linespacing=1.26, zorder=4)

    # =========================================================================
    # PANEL 3: Unstable Periodic Orbit (Face-on 2D section)
    # =========================================================================
    ax3_w = 0.245
    ax3_x = 0.697
    ax3 = fig.add_axes([ax3_x, y_plot, ax3_w, h_plot], zorder=5)
    ax3.set_facecolor('#ffffff')

    expand_factor = 1.38
    r0_unstable = 0.36
    phi0_unstable = np.radians(24.0)

    num_pts_unstable = 5
    pts_unstable = []
    for n in range(num_pts_unstable):
        rn = r0_unstable * (expand_factor ** n)
        phin = phi0_unstable + n * theta_step
        pts_unstable.append([rn * np.cos(phin), fp_y + rn * np.sin(phin)])
    pts_unstable = np.array(pts_unstable)

    # Concentric reference contour circles showing expansion centered at (0, fp_y)
    for r_circ in [0.36, 0.50, 0.69, 0.95, 1.31]:
        c_patch = patches.Circle((0, fp_y), r_circ, facecolor='none', edgecolor='#e2e8f0',
                                 lw=1.0, linestyle='--', zorder=1)
        ax3.add_patch(c_patch)

    # Arrows connecting successive iterations P_n -> P_{n+1} (outward)
    for n in range(num_pts_unstable - 1):
        p_curr = pts_unstable[n]
        p_next = pts_unstable[n+1]
        ax3.annotate('', xy=(p_next[0], p_next[1]), xytext=(p_curr[0], p_curr[1]),
                     arrowprops=dict(arrowstyle="->", color='#dc2626', lw=2.4,
                                     connectionstyle="arc3,rad=-0.14"),
                     zorder=4)

    # Plot sequence points P_n
    for n, pt in enumerate(pts_unstable):
        ax3.scatter([pt[0]], [pt[1]], color='#2563eb', edgecolor='#1e3a8a', s=130, linewidth=2.0, zorder=6)
        lbl = rf"$\boldsymbol{{P_{n}}}$"
        off_x = 0.18 * np.cos(phi0_unstable + n * theta_step + 0.35)
        off_y = 0.18 * np.sin(phi0_unstable + n * theta_step + 0.35)
        ax3.text(pt[0] + off_x, pt[1] + off_y, lbl,
                 fontsize=16.0, weight='bold', color='#1e3a8a', ha='center', va='center',
                 bbox=dict(boxstyle="round,pad=0.20", facecolor='#ffffff', edgecolor='#93c5fd', lw=0.9),
                 zorder=7)

    # Initial perturbation vector \delta P_0 from P* to P_0
    ax3.annotate('', xy=(pts_unstable[0][0], pts_unstable[0][1]), xytext=(0, fp_y),
                 arrowprops=dict(arrowstyle="<->", color='#b45309', lw=2.2, linestyle=':'),
                 zorder=3)
    ax3.text(pts_unstable[0][0] * 0.50 + 0.16, fp_y + (pts_unstable[0][1] - fp_y) * 0.50 - 0.12,
             r"$\boldsymbol{\delta P_0}$",
             fontsize=16.0, weight='bold', color='#b45309', ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.20", facecolor='#ffffff', edgecolor='#fcd34d', lw=0.9),
             zorder=8)

    # Growing perturbation displacement vector \delta P_4 from P* to P_4
    p4 = pts_unstable[4]
    ax3.annotate('', xy=(p4[0], p4[1]), xytext=(0, fp_y),
                 arrowprops=dict(arrowstyle="<->", color='#dc2626', lw=2.0, linestyle=':'),
                 zorder=3)
    ax3.text(p4[0] * 0.58 + 0.15, fp_y + (p4[1] - fp_y) * 0.58 - 0.16,
             r"$\boldsymbol{\delta P_4}$",
             fontsize=16.0, weight='bold', color='#dc2626', ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.20", facecolor='#ffffff', edgecolor='#fca5a5', lw=0.9),
             zorder=8)

    # Fixed point P* in Orange
    ax3.scatter([0], [fp_y], color=ORANGE_FP, edgecolor='#7c2d12', s=160, linewidth=2.4, zorder=10)
    ax3.annotate(
        r"$\mathbf{Fixed\;Point}\;\boldsymbol{P^*}$" "\n" r"(Periodic Orbit)",
        xy=(0, fp_y), xytext=(0.0, fp_y - 0.40),
        fontsize=15.5, weight='bold', color='#9a3412', ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.25", facecolor='#ffffff', edgecolor='#fdba74', lw=1.0),
        arrowprops=dict(arrowstyle="->", color='#9a3412', lw=1.6),
        zorder=11
    )

    # Instability Badge
    ax3.text(-1.42, 1.25,
             r"$\mathbf{Instability}$" "\n"
             r"$\boldsymbol{|\mu_i| > 1}\quad(\exists i)$",
             fontsize=16.5, weight='bold', color='#991b1b', ha='left', va='center',
             bbox=dict(boxstyle="round,pad=0.30", facecolor='#fef2f2', edgecolor='#fca5a5', lw=1.3),
             zorder=12)

    ax3.set_xlim(-1.65, 1.65)
    ax3.set_ylim(-1.65, 1.65)
    ax3.set_xlabel(r"Section coordinate $\xi_1$", fontsize=16.0, weight='bold', color=DARK_SLATE, labelpad=6)
    ax3.tick_params(labelsize=14.0, colors=SLATE)
    ax3.grid(True, linestyle=':', alpha=0.45, color='#cbd5e1')

    # Bottom caption box for Panel 3
    box3 = patches.FancyBboxPatch(
        (x3 + 0.010, y_box), w3 - 0.020, h_box,
        boxstyle="round,pad=0.0,rounding_size=0.016",
        facecolor=BG_BOX, edgecolor=BORDER_CARD, linewidth=1.2,
        zorder=3
    )
    ax_bg.add_patch(box3)

    ax_bg.text(x3 + w3/2, y_box + h_box/2,
               "Near an unstable periodic orbit, perturbations\ngrow outward along unstable directions:\n|μᵢ| > 1 for at least one transverse multiplier.",
               fontsize=13.5, weight='bold', color=DARK_SLATE, ha='center', va='center',
               linespacing=1.26, zorder=4)

    # =========================================================================
    # Centered vertical labels "Section coordinate \xi_2" in the gaps between plot boxes
    # =========================================================================
    y_center_plot = y_plot + h_plot / 2
    gap12_center = (ax1_x + ax1_w + ax2_x) / 2
    gap23_center = (ax2_x + ax2_w + ax3_x) / 2

    ax_bg.text(gap12_center, y_center_plot, r"$\mathbf{Section\;coordinate}\;\boldsymbol{\xi_2}$",
               fontsize=16.0, color=DARK_SLATE, rotation=90, ha='center', va='center', zorder=10)

    ax_bg.text(gap23_center, y_center_plot, r"$\mathbf{Section\;coordinate}\;\boldsymbol{\xi_2}$",
               fontsize=16.0, color=DARK_SLATE, rotation=90, ha='center', va='center', zorder=10)

    # Save figure
    plt.savefig(output_path, dpi=240, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] Successfully saved: {output_path}")


if __name__ == "__main__":
    create_figure()
