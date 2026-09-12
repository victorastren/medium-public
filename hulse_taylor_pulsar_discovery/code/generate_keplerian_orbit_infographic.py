#!/usr/bin/env python3
"""
Generate a Keplerian orbit infographic for PSR B1913+16,
illustrating the binary orbital geometry and all parameters entering the pulsar timing model:
- Pulsar and Companion stars
- Mutual orbits around the Center of Mass (CM)
- Periastron, Apastron, Line of Apsides
- Semimajor axis a_1
- Argument of periastron omega
- True anomaly nu
- Orbital inclination i relative to Plane of the Sky
- Line of sight direction toward Earth
- Projected radial velocity v_r and velocity scale K
"""

from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "keplerian_orbit_geometry.png"


def generate_keplerian_orbit_infographic(out_path=None):
    if out_path is None:
        out_path = DEFAULT_OUT
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # GLOBAL STYLING & FIGURE SETUP
    # -------------------------------------------------------------------------
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(13.2, 6.8), dpi=250)
    fig.patch.set_facecolor('#0d111a')

    # Two-column layout: Left (In-plane orbital geometry), Right (3D inclination & LOS)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.16, 1.04], wspace=0.08,
                          left=0.03, right=0.97, top=0.96, bottom=0.04)

    # Color Palette
    BG_COLOR = '#0d111a'
    CYAN = '#38bdf8'
    CYAN_GLOW = '#0284c7'
    PURPLE = '#a78bfa'
    PURPLE_DARK = '#6d28d9'
    GOLD = '#facc15'
    AMBER = '#f59e0b'
    GREEN = '#34d399'
    SLATE = '#475569'
    SLATE_LIGHT = '#94a3b8'
    WHITE = '#ffffff'
    CORAL = '#fb7185'

    # =========================================================================
    # LEFT PANEL: IN-PLANE KEPLERIAN ORBIT GEOMETRY
    # =========================================================================
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(BG_COLOR)
    ax1.set_xlim(-4.2, 3.2)
    ax1.set_ylim(-2.8, 2.7)
    ax1.set_aspect('equal')
    ax1.axis('off')

    # Orbital parameters (PSR B1913+16 eccentricity e = 0.617)
    e = 0.617
    a1 = 2.25  # pulsar semimajor axis
    b1 = a1 * np.sqrt(1 - e**2)  # ~1.77
    c1 = a1 * e  # focus shift = 1.388

    # Orientation of periastron: omega_plot = 34 degrees
    omega_deg = 34.0
    omega_rad = np.radians(omega_deg)
    rot_cos = np.cos(omega_rad)
    rot_sin = np.sin(omega_rad)

    # Center of Mass (CM) shifted slightly right to center the ellipse visually
    cm_x, cm_y = 0.45, -0.05

    # Ellipse center is at distance c1 from CM along direction opposite to periastron
    center1_x = cm_x - c1 * rot_cos
    center1_y = cm_y - c1 * rot_sin

    # Generate pulsar ellipse points
    theta_grid = np.linspace(0, 2 * np.pi, 400)
    x_raw = a1 * np.cos(theta_grid)
    y_raw = b1 * np.sin(theta_grid)
    orb1_x = center1_x + x_raw * rot_cos - y_raw * rot_sin
    orb1_y = center1_y + x_raw * rot_sin + y_raw * rot_cos

    # Companion orbit (mass ratio m1/m2 ~ 1.039 -> a2 ~ 1.039 * a1)
    a2 = a1 * 1.039
    b2 = a2 * np.sqrt(1 - e**2)
    c2 = a2 * e
    center2_x = cm_x + c2 * rot_cos
    center2_y = cm_y + c2 * rot_sin

    x2_raw = a2 * np.cos(theta_grid)
    y2_raw = b2 * np.sin(theta_grid)
    orb2_x = center2_x + x2_raw * rot_cos - y2_raw * rot_sin
    orb2_y = center2_y + x2_raw * rot_sin + y2_raw * rot_cos

    # 1. Draw Companion Orbit (subtle dashed purple)
    ax1.plot(orb2_x, orb2_y, color=PURPLE, ls=':', lw=1.3, alpha=0.55)

    # 2. Draw Pulsar Orbit (bright cyan solid)
    ax1.plot(orb1_x, orb1_y, color=CYAN, ls='-', lw=2.2, alpha=0.95)

    # Direction arrow on orbit
    idx_arr = 125
    ax1.annotate("", xy=(orb1_x[idx_arr+6], orb1_y[idx_arr+6]),
                 xytext=(orb1_x[idx_arr], orb1_y[idx_arr]),
                 arrowprops=dict(arrowstyle="->", color=CYAN, lw=2.2))

    # 3. Line of Apsides (Major axis line through CM, Periastron, Apastron)
    peri_r = a1 * (1 - e)
    ap_r = a1 * (1 + e)

    # Stop line of apsides cleanly just beyond periastron and apastron so it does not cut through text
    apsis_fwd = peri_r + 0.28
    apsis_bwd = ap_r + 0.35
    ax1.plot([cm_x - apsis_bwd * rot_cos, cm_x + apsis_fwd * rot_cos],
             [cm_y - apsis_bwd * rot_sin, cm_y + apsis_fwd * rot_sin],
             color=SLATE, ls='--', lw=1.2, alpha=0.75)

    # Periastron point (closest approach)
    peri_x = cm_x + peri_r * rot_cos
    peri_y = cm_y + peri_r * rot_sin
    ax1.plot(peri_x, peri_y, 'o', color=CORAL, ms=6.5, zorder=5)

    # Clean label placed clearly ABOVE and to the right of periastron with dedicated callout pointer
    peri_lbl_x = peri_x + 0.42
    peri_lbl_y = peri_y + 0.48
    ax1.annotate("Periastron\n$r_{\\mathrm{min}} = a_1(1-e)$",
                 xy=(peri_x + 0.04, peri_y + 0.04),
                 xytext=(peri_lbl_x, peri_lbl_y),
                 arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.2),
                 color=CORAL, fontsize=8.2, fontweight='bold', ha='left', va='bottom',
                 bbox=dict(boxstyle='round,pad=0.22', facecolor=BG_COLOR, edgecolor='none', alpha=0.92))

    # Apastron point
    ap_r = a1 * (1 + e)
    ap_x = cm_x - ap_r * rot_cos
    ap_y = cm_y - ap_r * rot_sin
    ax1.plot(ap_x, ap_y, 'o', color=SLATE_LIGHT, ms=4.5, zorder=5)
    ax1.text(ap_x - 0.15, ap_y + 0.15,
             "Apastron\n$r_{\\mathrm{max}} = a_1(1+e)$",
             color=SLATE_LIGHT, fontsize=7.8, ha='right', va='bottom',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.92))

    # 4. Reference Direction (Line of Nodes / X-axis from CM)
    ref_len = 2.3
    ax1.plot([cm_x, cm_x + ref_len], [cm_y, cm_y], color=SLATE_LIGHT, ls='-.', lw=1.4, alpha=0.85)
    ax1.annotate("", xy=(cm_x + ref_len, cm_y), xytext=(cm_x + ref_len - 0.35, cm_y),
                 arrowprops=dict(arrowstyle="->", color=SLATE_LIGHT, lw=1.5))
    ax1.text(cm_x + ref_len - 0.05, cm_y - 0.22, "Reference Line\n(Ascending Node)", color=SLATE_LIGHT,
             fontsize=8.0, fontweight='bold', ha='right', va='top',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # 5. Argument of Periastron omega arc (from Reference Line to Periastron line)
    arc_omega_r = 1.35
    t_omega = np.linspace(0, omega_rad, 50)
    ax1.plot(cm_x + arc_omega_r * np.cos(t_omega), cm_y + arc_omega_r * np.sin(t_omega),
             color=GREEN, lw=2.0)
    ax1.annotate("", xy=(cm_x + arc_omega_r * rot_cos, cm_y + arc_omega_r * rot_sin),
                 xytext=(cm_x + arc_omega_r * np.cos(omega_rad - 0.06),
                         cm_y + arc_omega_r * np.sin(omega_rad - 0.06)),
                 arrowprops=dict(arrowstyle="->", color=GREEN, lw=2.0))
    ax1.text(cm_x + 1.65 * np.cos(omega_rad * 0.5), cm_y + 1.65 * np.sin(omega_rad * 0.5),
             "$\\omega$ (Argument\nof periastron)",
             color=GREEN, fontsize=8.4, fontweight='bold', ha='left', va='center',
             bbox=dict(boxstyle='round,pad=0.22', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # 6. Current Pulsar Position at True Anomaly nu
    nu_deg = 92.0
    nu_rad = np.radians(nu_deg)
    phi_p = omega_rad + nu_rad
    r_pulsar = (a1 * (1 - e**2)) / (1 + e * np.cos(nu_rad))
    pulsar_x = cm_x + r_pulsar * np.cos(phi_p)
    pulsar_y = cm_y + r_pulsar * np.sin(phi_p)

    # Radius vector from CM to Pulsar
    ax1.plot([cm_x, pulsar_x], [cm_y, pulsar_y], color=CYAN, ls='-', lw=1.5, alpha=0.75)

    # True Anomaly nu arc (from Periastron line to Pulsar radius vector)
    arc_nu_r = 0.78
    t_nu = np.linspace(omega_rad, phi_p, 50)
    ax1.plot(cm_x + arc_nu_r * np.cos(t_nu), cm_y + arc_nu_r * np.sin(t_nu),
             color=CYAN, lw=2.0)
    ax1.annotate("", xy=(cm_x + arc_nu_r * np.cos(phi_p), cm_y + arc_nu_r * np.sin(phi_p)),
                 xytext=(cm_x + arc_nu_r * np.cos(phi_p - 0.08),
                         cm_y + arc_nu_r * np.sin(phi_p - 0.08)),
                 arrowprops=dict(arrowstyle="->", color=CYAN, lw=2.0))

    # Clean label for nu nestled perfectly INSIDE the angular wedge (r = 0.42)
    nu_mid_angle = np.radians(80.0)
    nu_lbl_x = cm_x + 0.42 * np.cos(nu_mid_angle)
    nu_lbl_y = cm_y + 0.42 * np.sin(nu_mid_angle)
    ax1.text(nu_lbl_x, nu_lbl_y + 0.04, "$\\nu$", color=CYAN, fontsize=11.0, fontweight='bold',
             ha='center', va='bottom')
    ax1.text(nu_lbl_x, nu_lbl_y - 0.03, "(True anomaly)", color=CYAN, fontsize=7.2, fontweight='bold',
             ha='center', va='top')

    # 7. Companion Position (opposite through CM)
    r_comp = (a2 * (1 - e**2)) / (1 + e * np.cos(nu_rad))
    comp_x = cm_x - r_comp * np.cos(phi_p)
    comp_y = cm_y - r_comp * np.sin(phi_p)
    ax1.plot([cm_x, comp_x], [cm_y, comp_y], color=PURPLE, ls=':', lw=1.3, alpha=0.5)

    # 8. Draw Bodies
    # Center of Mass (CM)
    cm_glow = patches.Circle((cm_x, cm_y), 0.22, facecolor=AMBER, alpha=0.25, edgecolor='none')
    ax1.add_patch(cm_glow)
    ax1.plot([cm_x - 0.12, cm_x + 0.12], [cm_y, cm_y], color=AMBER, lw=2.0)
    ax1.plot([cm_x, cm_x], [cm_y - 0.12, cm_y + 0.12], color=AMBER, lw=2.0)
    ax1.text(cm_x - 0.20, cm_y - 0.38, "Centre of Mass\n(System Barycenter)", color=AMBER,
             fontsize=8.5, fontweight='bold', ha='center', va='top',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # Companion Star
    comp_glow = patches.Circle((comp_x, comp_y), 0.28, facecolor=PURPLE_DARK, alpha=0.35, edgecolor='none')
    comp_body = patches.Circle((comp_x, comp_y), 0.15, facecolor=PURPLE, edgecolor='#c7d2fe', lw=1.5)
    ax1.add_patch(comp_glow)
    ax1.add_patch(comp_body)
    ax1.text(comp_x + 0.22, comp_y - 0.18, "Companion Star",
             color='#ddd6fe', fontsize=8.2, fontweight='bold', ha='left', va='top',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # Pulsar Star
    pul_glow = patches.Circle((pulsar_x, pulsar_y), 0.32, facecolor=CYAN_GLOW, alpha=0.4, edgecolor='none')
    pul_body = patches.Circle((pulsar_x, pulsar_y), 0.16, facecolor=WHITE, edgecolor=CYAN, lw=2.0)
    ax1.add_patch(pul_glow)
    ax1.add_patch(pul_body)
    ax1.text(pulsar_x - 0.10, pulsar_y + 0.42, "Pulsar PSR B1913+16",
             color='#e0f2fe', fontsize=8.8, fontweight='bold', ha='right', va='bottom',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # Pulsar Tangential Velocity Vector v
    dr_dnu = (a1 * (1 - e**2) * e * np.sin(nu_rad)) / ((1 + e * np.cos(nu_rad))**2)
    dx_dnu = dr_dnu * np.cos(phi_p) - r_pulsar * np.sin(phi_p)
    dy_dnu = dr_dnu * np.sin(phi_p) + r_pulsar * np.cos(phi_p)
    v_norm = np.hypot(dx_dnu, dy_dnu)
    v_scale = 0.85
    vx = (dx_dnu / v_norm) * v_scale
    vy = (dy_dnu / v_norm) * v_scale

    ax1.annotate("", xy=(pulsar_x + vx, pulsar_y + vy), xytext=(pulsar_x, pulsar_y),
                 arrowprops=dict(arrowstyle="->", color=WHITE, lw=2.2))
    ax1.text(pulsar_x + vx - 0.12, pulsar_y + vy + 0.04, "Velocity $\\vec{v}$",
             color=WHITE, fontsize=8.5, fontweight='bold', ha='right', va='bottom',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # 9. Orbit Center and Semimajor axis a1 measurement bar
    ax1.plot(center1_x, center1_y, '+', color=SLATE_LIGHT, ms=7, mew=1.6, zorder=4)
    ax1.text(center1_x - 0.12, center1_y + 0.16, "Orbit Center",
             color=SLATE_LIGHT, fontsize=7.5, ha='right', va='bottom',
             bbox=dict(boxstyle='round,pad=0.18', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # Dimension line offset parallel to line of apsides in the lower-left
    p_norm_lower_x = rot_sin * 0.42
    p_norm_lower_y = -rot_cos * 0.42
    bar_start_x = center1_x + p_norm_lower_x
    bar_start_y = center1_y + p_norm_lower_y
    bar_end_x = ap_x + p_norm_lower_x
    bar_end_y = ap_y + p_norm_lower_y

    ax1.annotate("", xy=(bar_end_x, bar_end_y), xytext=(bar_start_x, bar_start_y),
                 arrowprops=dict(arrowstyle="<->", color=CYAN, lw=1.6))
    tlen = 0.12
    ax1.plot([bar_start_x - rot_sin * tlen, bar_start_x + rot_sin * tlen],
             [bar_start_y + rot_cos * tlen, bar_start_y - rot_cos * tlen], color=CYAN, lw=1.4)
    ax1.plot([bar_end_x - rot_sin * tlen, bar_end_x + rot_sin * tlen],
             [bar_end_y + rot_cos * tlen, bar_end_y - rot_cos * tlen], color=CYAN, lw=1.4)

    mid_bar_x = 0.5 * (bar_start_x + bar_end_x)
    mid_bar_y = 0.5 * (bar_start_y + bar_end_y)
    ax1.text(mid_bar_x + p_norm_lower_x * 0.35, mid_bar_y + p_norm_lower_y * 0.35,
             "Semimajor axis $a_1$", color=CYAN, fontsize=8.4, fontweight='bold',
             ha='center', va='center', rotation=omega_deg,
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.92))

    # Subtle panel badge
    ax1.text(-4.0, 2.45, "ORBITAL PLANE GEOMETRY", color=CYAN,
             fontsize=8.5, fontweight='bold',
             bbox=dict(boxstyle='square,pad=0.35', facecolor='#0c4a6e', edgecolor=CYAN, alpha=0.5, lw=1.0))

    # =========================================================================
    # RIGHT PANEL: 3D INCLINATION i & LINE OF SIGHT TO EARTH
    # =========================================================================
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor(BG_COLOR)
    ax2.set_xlim(-3.4, 4.4)
    ax2.set_ylim(-2.8, 2.7)
    ax2.set_aspect('equal')
    ax2.axis('off')

    o3_x, o3_y = -0.9, -0.05
    i_deg = 47.0
    i_rad = np.radians(i_deg)

    def proj(x3, y3, z3):
        sx = o3_x + x3 * 0.80 - y3 * 0.28 + z3 * 1.05
        sy = o3_y + y3 * 0.88 + x3 * 0.16 + z3 * 0.12
        return sx, sy

    # 1. Plane of the Sky (Reference Plane, z3 = 0)
    sky_w = 1.9
    sky_h = 1.9
    sky_poly = np.array([
        proj(-sky_w, -sky_h, 0),
        proj(sky_w, -sky_h, 0),
        proj(sky_w, sky_h, 0),
        proj(-sky_w, sky_h, 0)
    ])
    sky_patch = patches.Polygon(sky_poly, closed=True,
                                facecolor='#1e293b', edgecolor='#475569',
                                lw=1.2, ls='--', alpha=0.30)
    ax2.add_patch(sky_patch)

    sky_label_pt = proj(-sky_w + 0.12, sky_h - 0.15, 0)
    ax2.text(sky_label_pt[0], sky_label_pt[1], "Plane of the Sky\n(Perpendicular to LOS)",
             color='#94a3b8', fontsize=8.0, fontweight='bold', ha='left', va='top')

    # 2. Orbital Plane
    orb_w = 1.9
    orb_h = 1.8
    orb_poly = np.array([
        proj(-orb_w, -orb_h * np.cos(i_rad), -orb_h * np.sin(i_rad)),
        proj(orb_w, -orb_h * np.cos(i_rad), -orb_h * np.sin(i_rad)),
        proj(orb_w, orb_h * np.cos(i_rad), orb_h * np.sin(i_rad)),
        proj(-orb_w, orb_h * np.cos(i_rad), orb_h * np.sin(i_rad))
    ])
    orb_patch = patches.Polygon(orb_poly, closed=True,
                                facecolor='#0369a1', edgecolor=CYAN,
                                lw=1.4, ls='-', alpha=0.20)
    ax2.add_patch(orb_patch)

    orb_label_pt = proj(-0.35, orb_h * np.cos(i_rad), orb_h * np.sin(i_rad))
    ax2.text(orb_label_pt[0], orb_label_pt[1] + 0.16,
             "Orbital Plane ($i \\approx 47^\\circ$)",
             color='#7dd3fc', fontsize=8.2, fontweight='bold', ha='center', va='bottom',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # Line of Nodes
    lon_start = proj(-sky_w * 1.05, 0, 0)
    lon_end = proj(sky_w * 1.05, 0, 0)
    ax2.plot([lon_start[0], lon_end[0]], [lon_start[1], lon_end[1]],
             color=WHITE, ls=':', lw=1.5, alpha=0.7)
    ax2.text(lon_start[0] - 0.12, lon_start[1] - 0.05, "Line of Nodes", color=SLATE_LIGHT,
             fontsize=7.8, ha='right', va='center',
             bbox=dict(boxstyle='round,pad=0.18', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # 3. Inclination Angle arc i
    arc_r_val = 1.15
    t_i = np.linspace(0, i_rad, 30)
    arc_i_pts = [proj(0.80, arc_r_val * np.cos(ti), arc_r_val * np.sin(ti)) for ti in t_i]
    arc_i_x = [pt[0] for pt in arc_i_pts]
    arc_i_y = [pt[1] for pt in arc_i_pts]
    ax2.plot(arc_i_x, arc_i_y, color=GOLD, lw=2.2)
    ax2.annotate("", xy=(arc_i_x[-1], arc_i_y[-1]), xytext=(arc_i_x[-3], arc_i_y[-3]),
                 arrowprops=dict(arrowstyle="->", color=GOLD, lw=2.2))
    mid_i_pt = proj(0.80, arc_r_val * np.cos(i_rad * 0.5), arc_r_val * np.sin(i_rad * 0.5))
    ax2.text(mid_i_pt[0] + 0.16, mid_i_pt[1] + 0.08, "Inclination $i$",
             color=GOLD, fontsize=8.8, fontweight='bold', ha='left', va='center',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # 4. Elliptical Orbit on the Tilted Plane
    scale3 = 0.65
    t_dense = np.linspace(0, 2 * np.pi, 300)
    x_orb_local = (center1_x - cm_x) * scale3 + (a1 * scale3) * np.cos(t_dense)
    y_orb_local = (center1_y - cm_y) * scale3 + (b1 * scale3) * np.sin(t_dense)
    x_rot3 = x_orb_local * rot_cos - y_orb_local * rot_sin
    y_rot3 = x_orb_local * rot_sin + y_orb_local * rot_cos

    x3_dense = x_rot3
    y3_dense = y_rot3 * np.cos(i_rad)
    z3_dense = y_rot3 * np.sin(i_rad)

    orb3_pts = [proj(x, y, z) for x, y, z in zip(x3_dense, y3_dense, z3_dense)]
    orb3_x = [pt[0] for pt in orb3_pts]
    orb3_y = [pt[1] for pt in orb3_pts]
    ax2.plot(orb3_x, orb3_y, color=CYAN, lw=2.2, alpha=0.95)

    # Center of mass marker
    cm3_pt = proj(0, 0, 0)
    ax2.plot(cm3_pt[0], cm3_pt[1], 'o', color=AMBER, ms=4.5, zorder=6)

    # Pulsar on 3D orbit
    idx_p3 = 195
    pul3_pt = (orb3_x[idx_p3], orb3_y[idx_p3])
    pul3_glow = patches.Circle(pul3_pt, 0.22, facecolor=CYAN_GLOW, alpha=0.4, edgecolor='none')
    pul3_body = patches.Circle(pul3_pt, 0.12, facecolor=WHITE, edgecolor=CYAN, lw=1.6)
    ax2.add_patch(pul3_glow)
    ax2.add_patch(pul3_body)
    ax2.text(pul3_pt[0] - 0.18, pul3_pt[1] - 0.20, "Pulsar",
             color='#e0f2fe', fontsize=8.5, fontweight='bold', ha='right', va='top',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # Pulsar 3D Velocity vector v
    v_end = (pul3_pt[0] - 0.48, pul3_pt[1] + 0.38)
    ax2.annotate("", xy=v_end, xytext=pul3_pt,
                 arrowprops=dict(arrowstyle="->", color=WHITE, lw=2.0))
    ax2.text(v_end[0] - 0.06, v_end[1] + 0.05, "Velocity $\\vec{v}$",
             color=WHITE, fontsize=8.2, fontweight='bold', ha='right', va='bottom',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # Radial velocity component along LOS
    vr_end = (pul3_pt[0] + 0.45, pul3_pt[1] + 0.06)
    ax2.annotate("", xy=vr_end, xytext=pul3_pt,
                 arrowprops=dict(arrowstyle="->", color=GOLD, lw=2.0))
    ax2.text(vr_end[0] + 0.08, vr_end[1], "Radial $v_r$\n(Doppler)",
             color=GOLD, fontsize=8.0, fontweight='bold', ha='left', va='center',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.90))

    # Projected extent a1 sin i along Line of Sight
    top_idx = np.argmax(z3_dense)
    top_orb_pt = (orb3_x[top_idx], orb3_y[top_idx])
    proj_sky_pt = proj(x3_dense[top_idx], y3_dense[top_idx], 0)

    ax2.plot([top_orb_pt[0], proj_sky_pt[0]], [top_orb_pt[1], proj_sky_pt[1]],
             color=AMBER, ls='--', lw=1.3)
    ax2.annotate("", xy=top_orb_pt, xytext=proj_sky_pt,
                 arrowprops=dict(arrowstyle="<->", color=AMBER, lw=1.5))
    ax2.text(proj_sky_pt[0] - 0.16, 0.5 * (top_orb_pt[1] + proj_sky_pt[1]) + 0.14,
             "Projected extent\n$a_1\\sin i$", color=AMBER, fontsize=8.0,
             fontweight='bold', ha='right', va='center',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.92))

    # 5. Line of Sight (LOS) Vector pointing toward Earth
    los_start = proj(0, 0, 0)
    earth_target = proj(0, 0, 2.7)
    los_end = proj(0, 0, 2.25)
    ax2.annotate("", xy=los_end, xytext=los_start,
                 arrowprops=dict(arrowstyle="->", color=GOLD, lw=2.4, ls='-'))

    ax2.text(1.48, 0.46,
             "Line of Sight (LOS)", color=GOLD, fontsize=8.8,
             fontweight='bold', ha='center', va='bottom',
             bbox=dict(boxstyle='round,pad=0.20', facecolor=BG_COLOR, edgecolor='none', alpha=0.92))

    # Earth Icon at end of LOS
    earth_x = earth_target[0] + 0.25
    earth_y = earth_target[1] + 0.05
    earth_glow = patches.Circle((earth_x, earth_y), 0.36, facecolor='#1e3a8a', alpha=0.35, edgecolor='none')
    earth_body = patches.Circle((earth_x, earth_y), 0.26, facecolor='#1d4ed8', edgecolor='#60a5fa', lw=1.6)
    ax2.add_patch(earth_glow)
    ax2.add_patch(earth_body)
    ax2.plot([earth_x - 0.09, earth_x + 0.05, earth_x + 0.12],
             [earth_y + 0.09, earth_y + 0.02, earth_y - 0.09],
             color='#34d399', lw=1.8, alpha=0.85)
    ax2.text(earth_x, earth_y - 0.44, "Observer on Earth\n(Arecibo)",
             color=WHITE, fontsize=8.0, fontweight='bold', ha='center', va='top')

    # Bottom formula card
    formula_box = patches.FancyBboxPatch((-3.0, -2.75), 7.0, 0.82,
                                         boxstyle="round,pad=0.12,rounding_size=0.18",
                                         facecolor='#0f172a', edgecolor='#334155', lw=1.2, alpha=0.92)
    ax2.add_patch(formula_box)

    ax2.text(0.5, -2.34,
             "Observable Radial Velocity (Line-of-Sight Projection):\n"
             "$v_r = K \\left[ \\cos(\\omega + \\nu) + e\\cos\\omega \\right], \\qquad "
             "K = \\frac{2\\pi a_1\\sin i}{P_b\\sqrt{1-e^2}}$",
             color='#f1f5f9', fontsize=8.6, ha='center', va='center', linespacing=1.35)

    # Subtle panel badge
    ax2.text(-3.0, 2.45, "3D INCLINATION & LINE OF SIGHT", color=GOLD,
             fontsize=8.5, fontweight='bold',
             bbox=dict(boxstyle='square,pad=0.35', facecolor='#78350f', edgecolor=AMBER, alpha=0.5, lw=1.0))

    # Save image
    plt.savefig(out_path, dpi=250, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Generated Keplerian orbit diagram at: {out_path}")
    return out_path


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else None
    generate_keplerian_orbit_infographic(target)
