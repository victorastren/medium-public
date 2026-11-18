#!/usr/bin/env python3
"""
Generate two-panel scientific figure:
"FRAME DRAGGING: THE EFFECT OF ROTATION"
"From static spacetime to stationary, axisymmetric spacetime"

Figure for Section "The Discovery of the Kerr Solution" of:
"The Golden Age of Black Hole Physics (1963–1974)"

Editorial & Scientific Specifications:
- Canvas: 1800 x 900 px at 140 DPI (12.857 x 6.429 in), landscape, two equally sized panels
- Typography & hierarchy matching oppenheimer_snyder_collapse.png:
  - 17.5 pt bold main title
  - 13.5 pt bold subtitle
  - 10.8 pt bold elapsed time clarification badge
  - 15.5 pt bold panel headers ("A · Nonrotating mass", "B · Rotating mass")
  - 13.0 pt bold panel subheaders ("Static spacetime (J = 0)", "Stationary, axisymmetric spacetime (J ≠ 0)")
  - 14.5 pt bold enlarged equation for Ω_LT
  - 11.2-12.2 pt primary callouts and annotations
- Physical & Geometric Concepts:
  - Panel A (Nonrotating mass, J = 0):
    - Spherical body with vertical symmetry axis
    - Concentric elliptical reference guides in the equatorial plane (r1, r2, r3)
    - 3 prominent blue gyroscope symbols acting as inertial-axis probes at increasing radial distances
    - Gyroscopes remain strictly aligned with distant reference directions (tilt = 0)
    - Unobtrusive radial distance axis from mass center with compact markers for r1, r2, r3
    - Clearly distinguishes static spacetime from flat spacetime (gravitational field present, zero frame dragging)
  - Panel B (Rotating mass, J ≠ 0):
    - Central sphere with rotation vector J emerging as an arrow above the sphere (+z) and bold orange equator arrow (counterclockwise from above, moving left-to-right in front)
    - Source rotation label placed comfortably below sphere limb
    - Gray rotation axis visible below the sphere without heavy visual dominance
    - 3 gyroscopes at comparable radial locations (r1, r2, r3) shown after equal elapsed time Δt
    - Precession vector in equatorial plane points opposite to source rotation: Ω_LT = -(GJ / c²r³) z
    - Gyroscopes precess clockwise (opposite to body rotation), with orange precession arrows arching right-to-left over the top of the disks
    - Prominently enlarged Lense–Thirring precession formula in bottom-right box: Ω_LT = -(GJ / c²r³) z
    - 2-line non-overlapping radial distance label safely inside panel margins
"""

from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Ellipse, Circle, FancyArrowPatch, Arc, Polygon
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "lense_thirring_frame_dragging.png"


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Matplotlib styling matching oppenheimer_snyder_collapse.py
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    # Exact landscape canvas: 1800 x 900 px at 140 DPI
    fig_w, fig_h = 1800.0 / 140.0, 900.0 / 140.0
    dpi = 140
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Color Palette matching existing figures
    NAVY = '#0f172a'          # Primary headers & bold text
    DARK_SLATE = '#1e293b'    # Body text & primary labels
    SLATE = '#334155'         # Secondary text / annotations (high contrast Slate-700)
    LIGHT_SLATE = '#64748b'   # Muted guides & borders
    BORDER_COLOR = '#cbd5e1'  # Card borders
    CARD_BG = '#f8fafc'       # Subtle card background

    BLUE_DARK = '#1d4ed8'     # Dark blue accent
    BLUE_LINE = '#2563eb'     # Medium blue
    BLUE_BORDER = '#93c5fd'   # Light blue border
    BLUE_BG = '#eff6ff'       # Light blue badge background

    ORANGE_DARK = '#b45309'   # Dark amber / orange
    ORANGE_RS = '#d97706'     # Vibrant rotation orange
    ORANGE_BORDER = '#fde68a' # Soft amber border
    ORANGE_BG = '#fffbeb'     # Warm light amber background

    # 1. Top Header Banner
    title_box = FancyBboxPatch((0.020, 0.865), 0.960, 0.115,
                               boxstyle="round,pad=0.002,rounding_size=0.008",
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax.add_patch(title_box)
    ax.text(0.50, 0.948, "FRAME DRAGGING: THE EFFECT OF ROTATION",
            color=NAVY, fontsize=17.5, fontweight='bold', ha='center', va='center')
    ax.text(0.50, 0.914, "From static spacetime to stationary, axisymmetric spacetime",
            color=SLATE, fontsize=13.5, fontweight='bold', ha='center', va='center')
    ax.text(0.50, 0.880, r"Gyroscopes shown after equal elapsed time $\Delta t$  ·  Precession around $\hat{\mathbf{z}}$ at constant inclination $\theta_0$",
            color=DARK_SLATE, fontsize=10.8, fontweight='bold', ha='center', va='center')

    # 3D Shaded Central Sphere Texture
    R_sphere = 1.05
    res = 350
    x_s = np.linspace(-R_sphere, R_sphere, res)
    y_s = np.linspace(-R_sphere, R_sphere, res)
    X_s, Y_s = np.meshgrid(x_s, y_s)
    R2_s = X_s**2 + Y_s**2
    mask_s = R2_s <= R_sphere**2

    Z_s = np.zeros_like(X_s)
    Z_s[mask_s] = np.sqrt(R_sphere**2 - R2_s[mask_s])

    # Directional light source from upper-left
    L = np.array([-0.35, 0.45, 0.82])
    L = L / np.linalg.norm(L)

    Nx = np.zeros_like(X_s)
    Ny = np.zeros_like(Y_s)
    Nz = np.zeros_like(Z_s)
    Nx[mask_s] = X_s[mask_s] / R_sphere
    Ny[mask_s] = Y_s[mask_s] / R_sphere
    Nz[mask_s] = Z_s[mask_s] / R_sphere

    diffuse = np.maximum(0.0, Nx * L[0] + Ny * L[1] + Nz * L[2])
    ambient = 0.28
    intensity = ambient + (1.0 - ambient) * diffuse
    H = L + np.array([0, 0, 1.0])
    H = H / np.linalg.norm(H)
    specular = np.maximum(0.0, Nx * H[0] + Ny * H[1] + Nz * H[2]) ** 18
    intensity = np.clip(intensity + 0.35 * specular, 0.0, 1.0)

    c_dark = np.array([29, 78, 216], dtype=float) / 255.0   # #1d4ed8
    c_mid = np.array([59, 130, 246], dtype=float) / 255.0   # #3b82f6
    c_light = np.array([219, 234, 254], dtype=float) / 255.0 # #dbeafe

    sphere_rgba = np.zeros((res, res, 4))
    for i in range(res):
        for j in range(res):
            if mask_s[i, j]:
                val = intensity[i, j]
                if val < 0.6:
                    t = val / 0.6
                    c = (1 - t) * c_dark + t * c_mid
                else:
                    t = (val - 0.6) / 0.4
                    c = (1 - t) * c_mid + t * c_light
                sphere_rgba[i, j, :3] = c
                sphere_rgba[i, j, 3] = 1.0

    # Panel Subplots: Panel A left, Panel B right
    p_w = 0.472
    p_h = 0.825
    p_y = 0.020
    
    ax_a = fig.add_axes([0.020, p_y, p_w, p_h])
    ax_b = fig.add_axes([0.508, p_y, p_w, p_h])

    for p_ax, p_letter, p_title, p_sub, is_rotating in [
        (ax_a, "A", "Nonrotating mass", "Static spacetime  (J = 0)", False),
        (ax_b, "B", "Rotating mass", "Stationary, axisymmetric spacetime  (J ≠ 0)", True)
    ]:
        p_ax.set_xlim(-4.9, 4.9)
        p_ax.set_ylim(-4.3, 4.3)
        p_ax.set_aspect('equal')
        p_ax.axis('off')

        # Background card
        card = FancyBboxPatch((-4.75, -4.15), 9.5, 8.3,
                              boxstyle="round,pad=0.02,rounding_size=0.15",
                              facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=0)
        p_ax.add_patch(card)

        # Panel Header Box inside card
        hdr_box = FancyBboxPatch((-4.5, 3.25), 9.0, 0.85,
                                 boxstyle="round,pad=0.02,rounding_size=0.08",
                                 facecolor=CARD_BG if not is_rotating else ORANGE_BG,
                                 edgecolor=BORDER_COLOR if not is_rotating else ORANGE_BORDER,
                                 linewidth=1.2, zorder=1)
        p_ax.add_patch(hdr_box)
        
        p_ax.text(0.0, 3.75, f"{p_letter}  ·  {p_title}",
                  color=NAVY if not is_rotating else ORANGE_DARK,
                  fontsize=15.5, fontweight='bold', ha='center', va='center', zorder=2)
        p_ax.text(0.0, 3.42, p_sub,
                  color=SLATE if not is_rotating else DARK_SLATE,
                  fontsize=13.0, fontweight='bold', ha='center', va='center', zorder=2)

        # Concentric elliptical reference guides (aspect ratio = 0.38)
        radii = [1.95, 2.95, 3.95]
        tilt_aspect = 0.38
        
        # 1. Back half of reference guides (y > 0, behind sphere)
        for r_val in radii:
            e_back = Arc((0, 0), 2 * r_val, 2 * r_val * tilt_aspect,
                         angle=0, theta1=0, theta2=180,
                         edgecolor='#94a3b8', linewidth=1.3, linestyle='--', zorder=1)
            p_ax.add_patch(e_back)

        # 2. Vertical rotation / reference axis (z-axis)
        # Both panels retain the clean gray rotation axis line
        p_ax.plot([0, 0], [0.8, 2.45], color='#64748b', linewidth=2.0, linestyle='-', zorder=2)
        p_ax.plot([0, 0], [-2.45, -0.8], color='#64748b', linewidth=2.0, linestyle='-', zorder=2)
        
        if not is_rotating:
            p_ax.text(0.0, 2.65, r"Symmetry axis ($z$)",
                      fontsize=11.4, fontweight='bold', color=DARK_SLATE, ha='center', va='bottom', zorder=10)
        else:
            # Single orange arrow emerging above the sphere for J, without dominating the lower sphere
            p_ax.annotate('', xy=(0, 2.55), xytext=(0, 1.70),
                          arrowprops=dict(arrowstyle='-|>', color='#d97706', lw=2.8, mutation_scale=16),
                          zorder=10)
            p_ax.text(0.0, 2.70, r"Rotation axis ($z$), $\mathbf{J}$",
                      fontsize=11.4, fontweight='bold', color='#b45309', ha='center', va='bottom', zorder=10)

        # 3. Central 3D Sphere
        p_ax.imshow(sphere_rgba, extent=[-R_sphere, R_sphere, -R_sphere, R_sphere], origin='lower', zorder=3)
        p_ax.add_patch(Circle((0, 0), R_sphere, fill=False, edgecolor='#1e3a8a', linewidth=1.6, zorder=4))
        
        # 4. Equator reference arc on sphere
        eq_arc = Arc((0, 0), 2 * R_sphere, 2 * R_sphere * tilt_aspect,
                     angle=0, theta1=180, theta2=360,
                     edgecolor='#bfdbfe', linewidth=1.4, linestyle='-', alpha=0.9, zorder=4)
        p_ax.add_patch(eq_arc)

        # 5. Front half of reference guides (y < 0, in front of sphere)
        for r_val in radii:
            e_front = Arc((0, 0), 2 * r_val, 2 * r_val * tilt_aspect,
                          angle=0, theta1=180, theta2=360,
                          edgecolor='#94a3b8', linewidth=1.3, linestyle='--', zorder=5)
            p_ax.add_patch(e_front)

        # 6. Source rotation arrow (Panel B only)
        # Positioned cleanly below the sphere limb (y = -1.25) so it never obscures the central sphere
        if is_rotating:
            rot_arrow = FancyArrowPatch((-0.92, -0.16), (0.92, -0.16),
                                        connectionstyle="arc3,rad=0.40",
                                        arrowstyle='-|>', mutation_scale=20,
                                        color='#d97706', linewidth=3.4, zorder=6)
            p_ax.add_patch(rot_arrow)
            p_ax.text(0.0, -1.25, r"Source rotation, $\mathbf{J}$",
                      fontsize=12.2, fontweight='bold', color='#b45309', ha='center', va='top',
                      bbox=dict(boxstyle='round,pad=0.22', facecolor='#ffffff', edgecolor='#fde68a', linewidth=1.1),
                      zorder=10)

        # 7. Gyroscope Drawing Function (3D Precession on Cone of Constant Inclination)
        # Consistent 3D projection matching the equatorial plane tilt (sin_beta = 0.38)
        sin_beta = tilt_aspect
        cos_beta = np.sqrt(1.0 - sin_beta**2)

        def project_3d(vx, vy, vz):
            return np.array([vx, vy * sin_beta + vz * cos_beta])

        def get_rotor_ellipse(s_vec, R_rot):
            ref = np.array([0.0, 0.0, 1.0]) if abs(s_vec[2]) < 0.92 else np.array([1.0, 0.0, 0.0])
            u1 = np.cross(s_vec, ref); u1 /= np.linalg.norm(u1)
            u2 = np.cross(s_vec, u1)
            p1 = project_3d(u1[0], u1[1], u1[2])
            p2 = project_3d(u2[0], u2[1], u2[2])
            M = np.column_stack([p1, p2])
            C = (R_rot**2) * (M @ M.T)
            vals, vecs = np.linalg.eigh(C)
            w = 2.0 * np.sqrt(max(1e-6, vals[1]))
            h = 2.0 * np.sqrt(max(1e-6, vals[0]))
            ang = np.degrees(np.arctan2(vecs[1, 1], vecs[0, 1]))
            return w, h, ang

        # Common physical parameters for all gyroscopes
        theta0 = np.radians(26.0)  # Constant nonzero inclination relative to rotation axis (+z)
        phi0 = np.radians(35.0)    # Common initial reference azimuth (pointing in distant reference direction)
        g_rad = 0.35              # High visibility probe disk radius
        p_len = g_rad * 2.05      # Pointer length (elevated to move precession arrows upper and clear gimbal)
        cone_z = p_len * np.cos(theta0)
        cone_r = p_len * np.sin(theta0)
        c2d = project_3d(0.0, 0.0, cone_z)

        def draw_gyro_3d(ax_inst, gx, gy, delta_phi_deg, show_arc):
            # Elevate the leftmost precession arrow around z (delta_phi > 100°) so it sits
            # cleanly above and away from the black gyroscope arrow tip
            dy_arc = 0.16 if (show_arc and delta_phi_deg > 100.0) else 0.0

            # 1. Local vertical reference axis (+z direction)
            ax_inst.plot([gx, gx], [gy - 0.32, gy + c2d[1] + dy_arc + 0.22],
                         color='#64748b', linestyle=':', linewidth=1.4, zorder=6)

            # 2. Precession guide ellipse (path of constant inclination theta0 around +z)
            ax_inst.add_patch(Ellipse((gx + c2d[0], gy + c2d[1] + dy_arc), 2 * cone_r, 2 * cone_r * sin_beta,
                                      edgecolor='#cbd5e1', facecolor='none', linestyle='--', linewidth=1.1, zorder=6))

            # 3. Outer circular gimbal frame
            ax_inst.add_patch(Circle((gx, gy), g_rad, fill=True, facecolor='#ffffff', edgecolor='#475569', linewidth=1.8, zorder=7))

            # Current 3D spin vector
            current_phi = phi0 - np.radians(delta_phi_deg)
            s_vec = np.array([np.sin(theta0) * np.cos(current_phi),
                              np.sin(theta0) * np.sin(current_phi),
                              np.cos(theta0)])

            # 4. Rotor disk (tilted blue ellipse in 3D plane perpendicular to spin vector)
            w_rot, h_rot, ang_rot = get_rotor_ellipse(s_vec, g_rad * 0.85)
            ax_inst.add_patch(Ellipse((gx, gy), w_rot, h_rot, angle=ang_rot,
                                      facecolor='#3b82f6', edgecolor='#1d4ed8', linewidth=1.3, alpha=0.92, zorder=8))

            # 5. Hub
            ax_inst.add_patch(Circle((gx, gy), g_rad * 0.20, facecolor='#ffffff', edgecolor='#0f172a', linewidth=1.2, zorder=9))

            # Initial reference pointer ghost (Panel B only, showing reference orientation before precession)
            if show_arc:
                s0_tip3d = np.array([cone_r * np.cos(phi0), cone_r * np.sin(phi0), cone_z])
                p0_tip2d = project_3d(s0_tip3d[0], s0_tip3d[1], s0_tip3d[2])
                ax_inst.plot([gx, gx + p0_tip2d[0]], [gy, gy + p0_tip2d[1] + dy_arc],
                             color='#94a3b8', linestyle=':', linewidth=1.4, zorder=9)
                # Origin dot at start of precession arc on guide ellipse
                ax_inst.plot(gx + p0_tip2d[0], gy + p0_tip2d[1] + dy_arc, marker='o', markersize=3.2,
                             color='#64748b', zorder=10)

            # 6. Current spin pointer arrow (inertial-axis probe)
            tip3d = np.array([cone_r * np.cos(current_phi), cone_r * np.sin(current_phi), cone_z])
            tip2d = project_3d(tip3d[0], tip3d[1], tip3d[2])
            base3d = -0.32 * tip3d
            base2d = project_3d(base3d[0], base3d[1], base3d[2])

            arrow = FancyArrowPatch((gx + base2d[0], gy + base2d[1]),
                                    (gx + tip2d[0], gy + tip2d[1]),
                                    arrowstyle='-|>', mutation_scale=12, shrinkA=0, shrinkB=0,
                                    color='#0f172a', linewidth=2.4, zorder=14)
            ax_inst.add_patch(arrow)

            # 7. Extended azimuthal precession arc along the cone guide (Panel B only)
            # Starts at faint gray initial-orientation marker (phi0) and ends at current spin tip (current_phi)
            # Proportional lengths: 250.0°, 72.2°, 30.1° matching weak-field 1/r³ scaling
            # Direction is clockwise across the cone front (right-to-left), opposite to body rotation J
            if show_arc and delta_phi_deg > 1.0:
                # 3D velocity tangent in direction of clockwise precession (d/dt(-phi))
                tan_3d = np.array([np.sin(current_phi), -np.cos(current_phi), 0.0])
                tan_2d = project_3d(tan_3d[0], tan_3d[1], tan_3d[2])
                tan_2d /= np.linalg.norm(tan_2d)
                normal_2d = np.array([-tan_2d[1], tan_2d[0]])

                # Vibrant orange curved arrows with prominent flared arrowhead barbs at the tip
                # Proportioned to ensure every Medium reader clearly sees the sense of rotation
                if delta_phi_deg > 100.0:
                    head_len = 0.065
                    head_w = 0.052
                    notch = 0.20
                elif delta_phi_deg > 40.0:
                    head_len = 0.052
                    head_w = 0.044
                    notch = 0.18
                else:
                    head_len = 0.040
                    head_w = 0.035
                    notch = 0.16

                arrow_color = '#ea580c'
                head_fill = '#0f172a'  # Solid black matching the spin arrow for a clean, prominent tip
                head_edge = '#0f172a'  # Crisp solid black outline

                # End the orange arc line inside the base notch of the arrowhead so ZERO orange peeks past the arrowhead
                d_phi_head = head_len / cone_r
                line_end_phi = current_phi + (1.0 - notch * 0.5) * d_phi_head
                if line_end_phi < phi0:
                    arc_angles_line = np.linspace(phi0, line_end_phi, max(30, int(delta_phi_deg * 1.5)))
                    arc_pts_line = np.array([project_3d(cone_r * np.cos(a), cone_r * np.sin(a), cone_z) for a in arc_angles_line])

                    # White contrast halo under the arc line only (preserves the orange arc line)
                    ax_inst.plot(gx + arc_pts_line[:, 0], gy + arc_pts_line[:, 1] + dy_arc, color='#ffffff', linewidth=5.2, zorder=11, solid_capstyle='butt')
                    # Bold vibrant orange arc curve (3.2 pt for high Medium readability)
                    ax_inst.plot(gx + arc_pts_line[:, 0], gy + arc_pts_line[:, 1] + dy_arc, color=arrow_color, linewidth=3.2, zorder=12, solid_capstyle='butt')

                # Solid black polygon arrowhead terminating cleanly on the elevated precession guide
                tip_pt = tip2d + np.array([0.0, dy_arc])
                base_pt = tip_pt - head_len * tan_2d
                p_l = base_pt + head_w * normal_2d
                p_r = base_pt - head_w * normal_2d
                tip_pt_ax = np.array([gx + tip_pt[0], gy + tip_pt[1]])
                p_l_ax = np.array([gx + p_l[0], gy + p_l[1]])
                base_notch_ax = np.array([gx + base_pt[0] - notch * head_len * tan_2d[0], gy + base_pt[1] - notch * head_len * tan_2d[1]])
                p_r_ax = np.array([gx + p_r[0], gy + p_r[1]])

                poly = Polygon([tip_pt_ax, p_l_ax, base_notch_ax, p_r_ax],
                               closed=True, facecolor=head_fill, edgecolor=head_edge, linewidth=1.2, zorder=13)
                ax_inst.add_patch(poly)
                p_l_ax = np.array([gx + p_l[0], gy + p_l[1]])
                base_notch_ax = np.array([gx + base_pt[0] - notch * head_len * tan_2d[0], gy + base_pt[1] - notch * head_len * tan_2d[1]])
                p_r_ax = np.array([gx + p_r[0], gy + p_r[1]])

                poly = Polygon([tip_pt_ax, p_l_ax, base_notch_ax, p_r_ax],
                               closed=True, facecolor=head_fill, edgecolor=head_edge, linewidth=1.2, zorder=13)
                ax_inst.add_patch(poly)

        # 3 Gyroscopes positioned at equatorial radii r1, r2, r3 (right apex: y = 0)
        gyro_radii = [1.95, 2.95, 3.95]
        r0 = gyro_radii[0]

        for r_val in gyro_radii:
            gx = r_val
            gy = 0.0

            if not is_rotating:
                # Panel A: All gyroscopes retain identical initial inclination theta0 and azimuth phi0
                # Zero rotation-induced frame dragging (delta_phi = 0)
                draw_gyro_3d(p_ax, gx, gy, delta_phi_deg=0.0, show_arc=False)
            else:
                # Panel B: Lense–Thirring precession:
                # Spin axis rotates azimuthally around +z by delta_phi proportional to 1/r³
                # Constant inclination theta0 is strictly preserved!
                prec_strength = (r0 / r_val)**3
                delta_phi = 250.0 * prec_strength
                draw_gyro_3d(p_ax, gx, gy, delta_phi_deg=delta_phi, show_arc=True)

        # 8. Uncluttered Radial Distance Representation
        # Horizontal dimension line placed just beneath the gyroscopes (y = -0.48), from sphere limb outward
        axis_y = -0.48
        p_ax.annotate('', xy=(4.35, axis_y), xytext=(1.05, axis_y),
                      arrowprops=dict(arrowstyle='->', color='#64748b', lw=1.3), zorder=8)

        # Enlarged, legible distance tick labels (11.2 pt bold) with white background padding
        for r_val, r_lbl in zip(gyro_radii, [r"$r_1$", r"$r_2$", r"$r_3$"]):
            p_ax.plot([r_val, r_val], [axis_y - 0.06, axis_y + 0.06], color='#64748b', lw=1.4, zorder=8)
            p_ax.text(r_val, axis_y - 0.12, r_lbl,
                      fontsize=11.2, fontweight='bold', color=SLATE if not is_rotating else DARK_SLATE,
                      ha='center', va='top',
                      bbox=dict(boxstyle='round,pad=0.15', facecolor='#ffffff', edgecolor='none', alpha=0.92),
                      zorder=10)

        # Explanatory text split over 2 lines
        # In Panel B (rotating mass), shifted further right (x = 3.16, y = -1.52) to cleanly clear "Source rotation, J"
        # without touching the dashed reference ellipse above or the summary box below
        rad_lbl_x = 3.16 if is_rotating else 2.45
        rad_lbl_y = -1.52 if is_rotating else -1.60
        p_ax.text(rad_lbl_x, rad_lbl_y, "Radial distance r\nfrom center of mass",
                  fontsize=11.2, fontstyle='italic', fontweight='bold', color=SLATE, ha='center', va='top',
                  bbox=dict(boxstyle='round,pad=0.22', facecolor='#f8fafc', edgecolor='#cbd5e1', lw=0.8),
                  zorder=10)

        # 9. Callouts & Annotations (Zero boundary crossings, zero overlaps)
        if not is_rotating:
            # Distant reference indicator in upper-left (fixed celestial reference frame)
            p_ax.annotate("Distant reference axes\n(fixed orientation)",
                          xy=(-2.60, 2.85), xytext=(-2.60, 2.10),
                          arrowprops=dict(arrowstyle="->", color=DARK_SLATE, lw=2.0),
                          fontsize=11.6, fontweight='bold', color=DARK_SLATE, ha='center', va='top',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.0),
                          zorder=10)

            # Callout to inner gyroscope (inertial-axis probe terminology)
            p_ax.annotate("Ideal gyroscope\n(inertial-axis probe)",
                          xy=(2.05, 0.72), xytext=(2.55, 1.80),
                          arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.5, shrinkA=2, shrinkB=4),
                          fontsize=11.2, fontweight='bold', color=BLUE_DARK, ha='center', va='bottom',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor=BLUE_BORDER, linewidth=1.1),
                          zorder=10)
            
            # Reference guide annotation in lower-left (moved up so it clears the lower summary box cleanly)
            p_ax.annotate("Equatorial reference guides\n(increasing distance r)",
                          xy=(-1.95, -0.40), xytext=(-2.35, -1.60),
                          arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.4, shrinkA=2, shrinkB=4),
                          fontsize=11.8, fontweight='bold', color=SLATE, ha='center', va='top',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.0),
                          zorder=10)

            # 10. Bottom summary box (Panel A)
            box_a = FancyBboxPatch((-4.35, -4.10), 8.70, 1.60,
                                   boxstyle='round,pad=0.04,rounding_size=0.10',
                                   facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.3, zorder=9)
            p_ax.add_patch(box_a)
            p_ax.text(0.0, -2.95, "No rotation-induced frame dragging",
                      fontsize=12.4, fontweight='bold', color=DARK_SLATE, ha='center', va='center', zorder=10)
            p_ax.text(0.0, -3.52, "Gyroscope orientations remain fixed\nrelative to distant reference axes",
                      fontsize=11.2, fontweight='bold', color=SLATE, ha='center', va='center', zorder=10)
        else:
            # Distant reference indicator in upper-left (fixed celestial reference frame)
            p_ax.annotate("Distant reference axes\n(fixed orientation)",
                          xy=(-2.60, 2.85), xytext=(-2.60, 2.10),
                          arrowprops=dict(arrowstyle="->", color=DARK_SLATE, lw=2.0),
                          fontsize=11.6, fontweight='bold', color=DARK_SLATE, ha='center', va='top',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.0),
                          zorder=10)

            # Callout to inner gyroscope explicitly noting precession opposite to body rotation
            p_ax.annotate("Frame-dragging precession\nOpposite to body rotation " + r"$\mathbf{J}$",
                          xy=(2.14, 0.94), xytext=(2.50, 1.68),
                          arrowprops=dict(arrowstyle="->", color=ORANGE_DARK, lw=1.5, shrinkA=2, shrinkB=4),
                          fontsize=11.2, fontweight='bold', color=ORANGE_DARK, ha='center', va='bottom',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#fffbeb', edgecolor=ORANGE_BORDER, linewidth=1.1),
                          zorder=10)

            # 10. Bottom summary box with prominently enlarged equation and clean vertical spacing (Panel B)
            box_b = FancyBboxPatch((-4.35, -4.10), 8.70, 1.60,
                                   boxstyle='round,pad=0.04,rounding_size=0.10',
                                   facecolor='#fffbeb', edgecolor=ORANGE_BORDER, linewidth=1.3, zorder=9)
            p_ax.add_patch(box_b)
            p_ax.text(0.0, -2.72, "Local inertial axes undergo rotation-induced precession",
                      fontsize=11.4, fontweight='bold', color=ORANGE_DARK, ha='center', va='center', zorder=10)
            p_ax.text(0.0, -3.05, "Lense–Thirring angular velocity (equatorial weak-field limit):",
                      fontsize=10.6, fontweight='bold', color='#92400e', ha='center', va='center', zorder=10)
            p_ax.text(0.0, -3.64, r"$\boldsymbol{\Omega}_{\mathrm{LT}} = -\frac{GJ}{c^2 r^3}\,\hat{\mathbf{z}}$",
                      fontsize=18.5, fontweight='bold', color=ORANGE_DARK, ha='center', va='center', zorder=10)

    # Save figure
    fig.savefig(output_path, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    print(f"[OK] Generated {output_path} ({fig_w * dpi:.0f} x {fig_h * dpi:.0f} px)")



if __name__ == '__main__':
    create_figure()
