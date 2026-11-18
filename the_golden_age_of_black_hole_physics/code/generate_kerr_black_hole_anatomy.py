#!/usr/bin/env python3
""" Generate two-panel scientific figure:
"Anatomy of a Rotating Kerr Black Hole"
"Horizons, ergosphere, and ring singularity (a/m = 0.8)"

Figure for Section "The Geometry of a Rotating Black Hole" of:
"The Golden Age of Black Hole Physics (1963–1974)"

Refined per review:
- Simplified title ("Anatomy of a Rotating Kerr Black Hole") and subtitle ("Horizons, ergosphere, and ring singularity (a/m = 0.8)")
- Removed coordinate transformation from top header and removed duplicate equation boxes above panels
- Reduced callouts to the 5 core features (Ergosurface, Ergosphere, Outer event horizon, Inner Cauchy horizon, Ring singularity)
- Used closed-region inequality r_+ <= r <= r_e(theta) for the ergosphere
- Enlarged the geometric objects (~32% larger relative to canvas) with generous whitespace for mobile/column readability
- Removed the ambiguous translucent grey-blue fill wall between r_+ and r_- in the 3D cutaway (only the ergosphere cross-section is shaded on the cut planes) and used a wider front cutaway on the inner Cauchy horizon so the bright gold ring singularity stands out unmistakably from the inner horizon.
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Arc
from matplotlib.collections import PolyCollection
import matplotlib.patheffects as pe

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "kerr_black_hole_anatomy.png"

# Adopted Kerr parameters (geometric units m = 1)
M_VAL = 1.0
A_VAL = 0.8
R_PLUS = M_VAL + np.sqrt(M_VAL**2 - A_VAL**2)   # 1.6
R_MINUS = M_VAL - np.sqrt(M_VAL**2 - A_VAL**2)  # 0.4


def r_ergo(theta):
    """Ergosurface Boyer-Lindquist radius r_e(theta)."""
    return M_VAL + np.sqrt(np.maximum(0.0, M_VAL**2 - (A_VAL**2) * (np.cos(theta)**2)))


def kerr_meridional_rz(r_val, theta):
    """Return cylindrical (R, z) in Kerr oblate spheroidal coordinates."""
    R = np.sqrt(r_val**2 + A_VAL**2) * np.sin(theta)
    z = r_val * np.cos(theta)
    return R, z


def kerr_xyz(r_val, theta, phi):
    """Return 3D Cartesian (x, y, z) in Kerr oblate spheroidal coordinates."""
    rho = np.sqrt(r_val**2 + A_VAL**2) * np.sin(theta)
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    z = r_val * np.cos(theta)
    return x, y, z


def project_3d(x, y, z, elev_deg=22.0):
    """
    Orthographic 3D projection onto 2D screen coordinates (u, v) and depth d:
    +x is right, +y is toward viewer, +z is up.
    Camera is elevated by `elev_deg` above the xy-plane.
    """
    el = np.radians(elev_deg)
    u = x
    v = z * np.cos(el) - y * np.sin(el)
    depth = y * np.cos(el) + z * np.sin(el)
    return u, v, depth


def build_surface_quads(r_func, theta_arr, phi_arr, base_rgb_ext, base_rgb_int, alpha_ext, alpha_int, elev_deg=22.0):
    """
    Build depth-sortable 2D projected quads for a 3D axisymmetric surface r(theta).
    Shades exterior vs interior (concave cutaway) faces using directional lighting.
    """
    el = np.radians(elev_deg)
    cam_vec = np.array([0.0, np.cos(el), np.sin(el)])
    light_vec = np.array([-0.38, 0.55, 0.74])
    light_vec /= np.linalg.norm(light_vec)

    TH, PH = np.meshgrid(theta_arr, phi_arr, indexing='ij')
    R_grid = r_func(TH)
    X, Y, Z = kerr_xyz(R_grid, TH, PH)
    U, V, D = project_3d(X, Y, Z, elev_deg=elev_deg)

    n_th = len(theta_arr) - 1
    n_ph = len(phi_arr) - 1
    quads = []

    for i in range(n_th):
        for j in range(n_ph):
            p00 = np.array([X[i, j], Y[i, j], Z[i, j]])
            p10 = np.array([X[i + 1, j], Y[i + 1, j], Z[i + 1, j]])
            p11 = np.array([X[i + 1, j + 1], Y[i + 1, j + 1], Z[i + 1, j + 1]])
            p01 = np.array([X[i, j + 1], Y[i, j + 1], Z[i, j + 1]])

            v_th = 0.5 * ((p10 - p00) + (p11 - p01))
            v_ph = 0.5 * ((p01 - p00) + (p11 - p10))
            n_vec = np.cross(v_th, v_ph)
            norm_len = np.linalg.norm(n_vec)
            if norm_len < 1e-9:
                continue
            n_vec /= norm_len

            facing = np.dot(n_vec, cam_vec)
            if facing >= 0.0:
                diff = max(0.0, np.dot(n_vec, light_vec))
                shade = 0.64 + 0.36 * diff
                rgb = np.clip(np.array(base_rgb_ext) * shade + 0.08 * (diff**3), 0.0, 1.0)
                a_val = alpha_ext
            else:
                diff = max(0.0, np.dot(-n_vec, light_vec))
                shade = 0.54 + 0.36 * diff
                rgb = np.clip(np.array(base_rgb_int) * shade, 0.0, 1.0)
                a_val = alpha_int

            verts_2d = [
                (U[i, j], V[i, j]),
                (U[i + 1, j], V[i + 1, j]),
                (U[i + 1, j + 1], V[i + 1, j + 1]),
                (U[i, j + 1], V[i, j + 1]),
            ]
            d_mean = 0.25 * (D[i, j] + D[i + 1, j] + D[i + 1, j + 1] + D[i, j + 1])
            quads.append((d_mean, verts_2d, (*rgb, a_val)))

    return quads


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.5,
    })

    # Exact 16:9 landscape canvas: 1920 x 1080 px at 140 DPI (13.714 x 7.714 in)
    dpi = 140
    fig_w, fig_h = 1920.0 / dpi, 1080.0 / dpi
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Publication Color Palette matching existing article figures
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#334155'
    BORDER_COLOR = '#cbd5e1'
    CARD_BG = '#f8fafc'

    # Surface Color Palette (Amber Ergosurface, Blue Outer Horizon, Violet Inner Horizon, Gold Singularity)
    ERGO_LINE = '#d97706'      # Vibrant amber outline
    ERGO_DARK = '#b45309'      # Deep amber text
    ERGO_FILL = '#fde68a'      # Warm translucent amber fill
    ERGO_BADGE_BG = '#fffbeb'
    ERGO_BADGE_EC = '#fcd34d'

    OUTER_LINE = '#1d4ed8'     # Crisp royal blue outline
    OUTER_DARK = '#1e40af'     # Deep blue text
    OUTER_FILL = '#bfdbfe'     # Soft blue fill
    OUTER_BADGE_BG = '#eff6ff'
    OUTER_BADGE_EC = '#93c5fd'

    INNER_LINE = '#6d28d9'     # Deep violet outline
    INNER_DARK = '#5b21b6'     # Deep violet text
    INNER_FILL = '#ddd6fe'     # Soft violet fill
    INNER_BADGE_BG = '#f5f3ff'
    INNER_BADGE_EC = '#c4b5fd'

    SING_GOLD = '#fde047'      # Bright pale gold core
    SING_RIM = '#78350f'       # High-contrast dark amber/brown casing
    SING_BADGE_BG = '#fefce8'
    SING_BADGE_EC = '#eab308'

    # =========================================================================
    # 1. TOP HEADER BANNER (TITLE, SUBTITLE, PARAMETERS & COORDINATE MAPPING)
    # Enlarged grey box with generous interlines for maximum legibility
    # =========================================================================
    title_box = FancyBboxPatch((0.020, 0.808), 0.960, 0.176,
                               boxstyle="round,pad=0.002,rounding_size=0.008",
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax.add_patch(title_box)
    ax.text(0.50, 0.957, "ANATOMY OF A ROTATING KERR BLACK HOLE",
            color=NAVY, fontsize=18.5, fontweight='bold', ha='center', va='center')
    ax.text(0.50, 0.914,
            r"Horizons, ergosphere, and ring singularity in auxiliary oblate spheroidal coordinates ($a/m = 0.8$)",
            color=SLATE, fontsize=14.2, fontweight='bold', ha='center', va='center')
    part1 = r"$m = \frac{GM}{c^2},\quad a = \frac{J}{Mc}$   "
    part2 = (r"Mass parameter $m$ and rotation parameter $a$, where $M$ is the black hole's mass "
             r"and $J$ its angular momentum")
    t3 = ax.text(0.50, 0.868, part1 + part2,
                 color='#475569', fontsize=12.2, fontweight='bold', ha='center', va='center')

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    b3 = t3.get_window_extent(renderer)

    t_p1 = ax.text(0, 0, part1, color='#475569', fontsize=12.2, fontweight='bold')
    fig.canvas.draw()
    b_p1 = t_p1.get_window_extent(renderer)
    t_p1.remove()

    x_mass_start = (b3.x0 + b_p1.width) / 1920.0

    ax.text(x_mass_start, 0.832,
            r"Coordinate mapping:   $x = \sqrt{r^2+a^2}\sin\theta\cos\phi,\quad y = \sqrt{r^2+a^2}\sin\theta\sin\phi,\quad z = r\cos\theta$",
            color='#475569', fontsize=12.2, fontweight='bold', ha='left', va='center')

    # =========================================================================
    # 2. TWO PANEL CARDS (PANEL A & PANEL B)
    # =========================================================================
    panel_y0, panel_h = 0.012, 0.784
    panel_w = 0.472
    panel_a_x0 = 0.020
    panel_b_x0 = 0.508

    for px0, ptitle, psub in [
        (panel_a_x0, "A · Meridional cross-section",
         "Plane containing the rotation axis"),
        (panel_b_x0, "B · Three-dimensional cutaway",
         "Perspective cutaway exposing the interior surfaces"),
    ]:
        pcard = FancyBboxPatch((px0, panel_y0), panel_w, panel_h,
                               boxstyle="round,pad=0.002,rounding_size=0.008",
                               facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4)
        ax.add_patch(pcard)
        phead = FancyBboxPatch((px0, panel_y0 + panel_h - 0.074), panel_w, 0.074,
                               boxstyle="round,pad=0.002,rounding_size=0.008",
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.2)
        ax.add_patch(phead)
        ax.text(px0 + 0.018, panel_y0 + panel_h - 0.024, ptitle,
                color=NAVY, fontsize=16.5, fontweight='bold', ha='left', va='center')
        ax.text(px0 + 0.018, panel_y0 + panel_h - 0.052, psub,
                color=SLATE, fontsize=13.2, fontweight='bold', ha='left', va='center')

    # Enlarged geometric objects: smaller coordinate limits zoom the black hole by ~30%
    # Sub-axes dimensions: width = 0.460 * 13.714 = 6.308 in, height = 0.688 * 7.714 = 5.307 in
    # Physical aspect ratio w / h = 1.189 -> xlim(-3.38, 3.38), ylim(-2.98, 2.71) matches 1:1 equal scale
    X_LIM = 3.38
    Y_MIN = -2.98
    Y_MAX = 2.71

    # =========================================================================
    # 3. PANEL A — MERIDIONAL CROSS-SECTION (EQUAL ASPECT)
    # =========================================================================
    ax_a = fig.add_axes([panel_a_x0 + 0.006, panel_y0 + 0.006, panel_w - 0.012, panel_h - 0.096])
    ax_a.set_xlim(-X_LIM, X_LIM)
    ax_a.set_ylim(Y_MIN, Y_MAX)
    ax_a.set_aspect('equal')
    ax_a.axis('off')

    theta_mer = np.linspace(0.0, np.pi, 400)
    Re_mer, ze_mer = kerr_meridional_rz(r_ergo(theta_mer), theta_mer)
    Rp_mer, zp_mer = kerr_meridional_rz(np.full_like(theta_mer, R_PLUS), theta_mer)
    Rm_mer, zm_mer = kerr_meridional_rz(np.full_like(theta_mer, R_MINUS), theta_mer)

    x_ergo_loop = np.concatenate([Re_mer, -Re_mer[::-1]])
    z_ergo_loop = np.concatenate([ze_mer, ze_mer[::-1]])

    x_plus_loop = np.concatenate([Rp_mer, -Rp_mer[::-1]])
    z_plus_loop = np.concatenate([zp_mer, zp_mer[::-1]])

    x_minus_loop = np.concatenate([Rm_mer, -Rm_mer[::-1]])
    z_minus_loop = np.concatenate([zm_mer, zm_mer[::-1]])

    # 3a. Fill shaded Ergoregion (between r_e and r_+)
    ax_a.fill(x_ergo_loop, z_ergo_loop, facecolor=ERGO_FILL, alpha=0.70, zorder=2)
    ax_a.fill(x_ergo_loop, z_ergo_loop, facecolor='none', edgecolor='#f59e0b',
              hatch='///', linewidth=0.0, alpha=0.22, zorder=2.2)

    # 3b. Fill Outer Event Horizon interior
    ax_a.fill(x_plus_loop, z_plus_loop, facecolor='#ffffff', alpha=1.0, zorder=2.5)
    ax_a.fill(x_plus_loop, z_plus_loop, facecolor=OUTER_FILL, alpha=0.64, zorder=3)

    # 3c. Fill Inner Cauchy Horizon interior
    ax_a.fill(x_minus_loop, z_minus_loop, facecolor='#ffffff', alpha=1.0, zorder=3.5)
    ax_a.fill(x_minus_loop, z_minus_loop, facecolor=INNER_FILL, alpha=0.76, zorder=4)

    # 3d. Draw subtle equatorial symmetry plane guide (z = 0)
    ax_a.plot([-2.42, 2.42], [0.0, 0.0], color='#94a3b8', lw=1.15, ls=':', zorder=4.5)
    ax_a.plot([-A_VAL, A_VAL], [0.0, 0.0], color='#92400e', lw=1.7, ls='--', alpha=0.75, zorder=5.5)

    # 3e. Draw crisp surface boundaries
    ax_a.plot(x_ergo_loop, z_ergo_loop, color=ERGO_LINE, lw=3.0, zorder=6)
    ax_a.plot(x_plus_loop, z_plus_loop, color=OUTER_LINE, lw=2.8, zorder=7)
    ax_a.plot(x_minus_loop, z_minus_loop, color=INNER_LINE, lw=2.7, zorder=8)

    # 3f. Rotation axis (z) and angular momentum vector J
    ax_a.plot([0.0, 0.0], [-2.05, 1.76], color=SLATE, lw=1.8, ls='--', zorder=5)
    ax_a.annotate("", xy=(0.0, 2.08), xytext=(0.0, 1.62),
                  arrowprops=dict(arrowstyle="-|>,head_length=0.64,head_width=0.36",
                                  color=NAVY, lw=2.5), zorder=9)
    rot_arc_a = Arc((0.0, 1.84), 0.70, 0.22, angle=0, theta1=195, theta2=345,
                    color=ERGO_LINE, lw=2.2, zorder=10)
    ax_a.add_patch(rot_arc_a)
    ax_a.annotate("", xy=(0.34, 1.81), xytext=(0.22, 1.75),
                  arrowprops=dict(arrowstyle="-|>,head_length=0.44,head_width=0.25",
                                  color=ERGO_LINE, lw=1.9), zorder=10)
    ax_a.text(0.0, 2.32, r"Rotation axis ($z$), $\mathbf{J}$",
              color=NAVY, fontsize=14.0, fontweight='bold', ha='center', va='center', zorder=10)

    # 3g. Pole contact markers (theta = 0, pi: r_e = r_+ = 1.6m)
    ax_a.scatter([0.0, 0.0], [R_PLUS, -R_PLUS], s=52, facecolor='#ffffff',
                 edgecolor=NAVY, linewidth=2.0, zorder=11)

    # 3h. Ring singularity intersection points at (x = ±a, z = 0) = (±0.8m, 0)
    ax_a.scatter([-A_VAL, A_VAL], [0.0, 0.0], s=135, facecolor=SING_GOLD,
                 edgecolor=SING_RIM, linewidth=2.4, zorder=12)

    # 3i. Polar angle theta definition arc and radial reference direction
    th_ray_deg = 48.0
    th_ray = np.radians(th_ray_deg)
    L_ray = 1.35
    x_ray_end = L_ray * np.sin(th_ray)
    z_ray_end = L_ray * np.cos(th_ray)
    ax_a.plot([0.0, x_ray_end], [0.0, z_ray_end], color='#475569', lw=1.35, ls='-.', zorder=9.0)

    # Curved arc for theta from +z axis (90 deg) down to the radial direction (90 - 48 = 42 deg)
    r_arc_th = 0.62
    arc_th = Arc((0.0, 0.0), 2 * r_arc_th, 2 * r_arc_th, angle=0,
                 theta1=90.0 - th_ray_deg, theta2=90.0,
                 color='#1e293b', lw=1.5, zorder=10.0)
    ax_a.add_patch(arc_th)

    # Arrowhead on arc indicating increasing theta (clockwise, downwards toward the ray)
    x_th_arrow = r_arc_th * np.sin(th_ray)
    z_th_arrow = r_arc_th * np.cos(th_ray)
    th_tan_x = np.cos(th_ray)
    th_tan_z = -np.sin(th_ray)
    ax_a.annotate("", xy=(x_th_arrow, z_th_arrow),
                  xytext=(x_th_arrow - 0.06 * th_tan_x, z_th_arrow - 0.06 * th_tan_z),
                  arrowprops=dict(arrowstyle="-|>,head_length=0.34,head_width=0.18",
                                  color='#1e293b', lw=1.4), zorder=10.5)

    # Label theta
    th_mid = np.radians(th_ray_deg / 2.0)
    r_th_lbl = r_arc_th + 0.16
    ax_a.text(r_th_lbl * np.sin(th_mid), r_th_lbl * np.cos(th_mid), r"$\theta$",
              color='#1e293b', fontsize=15.0, fontweight='bold', ha='center', va='center', zorder=11.0)

    # 3j. Clean, Simplified Callout Badges in Panel A (5 core labels, 13.8 pt bold)
    # 1. Top-Left: Outer event horizon r_+ = 1.6m
    th_p_lbl = np.radians(42.0)
    xp_pt = -np.sqrt(R_PLUS**2 + A_VAL**2) * np.sin(th_p_lbl)
    zp_pt = R_PLUS * np.cos(th_p_lbl)
    ax_a.annotate(
        "Outer event horizon\n" + r"$r_+ = 1.6m$",
        xy=(xp_pt, zp_pt), xytext=(-2.14, 1.70),
        arrowprops=dict(arrowstyle="->", color=OUTER_LINE, lw=1.7, shrinkA=0, shrinkB=3,
                        connectionstyle="arc3,rad=-0.08"),
        fontsize=13.8, fontweight='bold', color=OUTER_DARK, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=OUTER_BADGE_BG, edgecolor=OUTER_BADGE_EC, linewidth=1.35),
        zorder=13
    )

    # 2. Bottom-Left: Inner Cauchy horizon r_- = 0.4m
    th_m_lbl = np.radians(135.0)
    xm_pt = -np.sqrt(R_MINUS**2 + A_VAL**2) * np.sin(th_m_lbl)
    zm_pt = R_MINUS * np.cos(th_m_lbl)
    ax_a.annotate(
        "Inner Cauchy horizon\n" + r"$r_- = 0.4m$",
        xy=(xm_pt, zm_pt), xytext=(-2.16, -1.90),
        arrowprops=dict(arrowstyle="->", color=INNER_LINE, lw=1.7, shrinkA=0, shrinkB=3,
                        connectionstyle="arc3,rad=-0.10"),
        fontsize=13.8, fontweight='bold', color=INNER_DARK, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=INNER_BADGE_BG, edgecolor=INNER_BADGE_EC, linewidth=1.35),
        zorder=13
    )

    # 3. Top-Right: Ergosurface r_e(pi/2) = 2.0m
    th_e_lbl = np.radians(40.0)
    re_val_lbl = r_ergo(th_e_lbl)
    xe_pt = np.sqrt(re_val_lbl**2 + A_VAL**2) * np.sin(th_e_lbl)
    ze_pt = re_val_lbl * np.cos(th_e_lbl)
    ax_a.annotate(
        "Ergosurface\n" + r"$r_{\mathrm{e}}(\pi/2) = 2.0m$",
        xy=(xe_pt, ze_pt), xytext=(2.24, 1.95),
        arrowprops=dict(arrowstyle="->", color=ERGO_LINE, lw=1.7, shrinkA=0, shrinkB=3,
                        connectionstyle="arc3,rad=0.10"),
        fontsize=13.8, fontweight='bold', color=ERGO_DARK, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=ERGO_BADGE_BG, edgecolor=ERGO_BADGE_EC, linewidth=1.35),
        zorder=13
    )

    # 4. Lower-Right: Ring singularity (R = a = 0.8m)
    ax_a.annotate(
        "Ring singularity\n" + r"$R = a = 0.8m,\; z = 0$",
        xy=(A_VAL, -0.04), xytext=(2.18, -1.90),
        arrowprops=dict(arrowstyle="->", color=SING_RIM, lw=1.7, shrinkA=0, shrinkB=5,
                        connectionstyle="arc3,rad=0.08"),
        fontsize=13.6, fontweight='bold', color=SING_RIM, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=SING_BADGE_BG, edgecolor=SING_BADGE_EC, linewidth=1.35),
        zorder=13
    )

    # 5. Bottom-Center-Right: Ergosphere (shaded, closed inequality r_+ <= r <= r_e(theta))
    ax_a.annotate(
        "Ergosphere (shaded)\n" + r"$r_+ \leq r \leq r_{\mathrm{e}}(\theta)$",
        xy=(0.88, -1.48), xytext=(0.95, -2.52),
        arrowprops=dict(arrowstyle="->", color=ERGO_DARK, lw=1.7, shrinkA=0, shrinkB=2,
                        connectionstyle="arc3,rad=-0.08"),
        fontsize=13.6, fontweight='bold', color=ERGO_DARK, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=ERGO_BADGE_BG, edgecolor=ERGO_BADGE_EC, linewidth=1.35),
        zorder=13
    )

    # Coordinate scale bar at bottom-left of Panel A (clear of bottom badges)
    scale_y = -2.60
    scale_x0 = -1.85
    ax_a.plot([scale_x0 - 1.0, scale_x0 + 1.0], [scale_y, scale_y], color=SLATE, lw=2.3, zorder=10)
    for sx_rel, slbl in [(-1.0, r"$-1m$"), (0.0, r"$0$"), (1.0, r"$+1m$")]:
        sx = scale_x0 + sx_rel
        ax_a.plot([sx, sx], [scale_y - 0.07, scale_y + 0.07], color=SLATE, lw=2.1, zorder=10)
        ax_a.text(sx, scale_y - 0.18, slbl, color=SLATE, fontsize=12.4, fontweight='bold',
                  ha='center', va='center', zorder=10)

    # =========================================================================
    # 4. PANEL B — THREE-DIMENSIONAL CUTAWAY (PERSPECTIVE VIEW)
    # =========================================================================
    ax_b = fig.add_axes([panel_b_x0 + 0.006, panel_y0 + 0.006, panel_w - 0.012, panel_h - 0.096])
    ax_b.set_xlim(-X_LIM, X_LIM)
    ax_b.set_ylim(Y_MIN, Y_MAX)
    ax_b.set_aspect('equal')
    ax_b.axis('off')

    elev_b = 22.0
    # Outer shells (ergosurface & outer horizon): cutaway front wedge phi in [16 deg, 132 deg]
    phi_cut1_deg = 16.0
    phi_cut2_deg = 132.0
    phi_shell_outer = np.radians(np.linspace(phi_cut2_deg, 360.0 + phi_cut1_deg, 95))
    theta_shell = np.linspace(0.0, np.pi, 55)

    # Inner Cauchy horizon shell: wider front cutaway phi in [-8 deg, 156 deg] (remaining: 156 deg -> 352 deg)
    # This stepped cutaway keeps the inner horizon cutaway edges back so the gold ring singularity is 100% clear!
    phi_in_cut1_deg = -8.0
    phi_in_cut2_deg = 156.0
    phi_shell_inner = np.radians(np.linspace(phi_in_cut2_deg, 360.0 + phi_in_cut1_deg, 80))

    # Build 3D surface quads for the three nested surfaces
    quads_ergo = build_surface_quads(
        r_ergo, theta_shell, phi_shell_outer,
        base_rgb_ext=(0.98, 0.78, 0.32),
        base_rgb_int=(0.94, 0.70, 0.24),
        alpha_ext=0.28, alpha_int=0.18, elev_deg=elev_b
    )
    quads_outer = build_surface_quads(
        lambda th: np.full_like(th, R_PLUS), theta_shell, phi_shell_outer,
        base_rgb_ext=(0.35, 0.62, 0.96),
        base_rgb_int=(0.28, 0.54, 0.90),
        alpha_ext=0.38, alpha_int=0.22, elev_deg=elev_b
    )
    quads_inner = build_surface_quads(
        lambda th: np.full_like(th, R_MINUS), theta_shell, phi_shell_inner,
        base_rgb_ext=(0.62, 0.42, 0.96),
        base_rgb_int=(0.52, 0.32, 0.88),
        alpha_ext=0.58, alpha_int=0.42, elev_deg=elev_b
    )

    all_quads = quads_ergo + quads_outer + quads_inner
    all_quads.sort(key=lambda item: item[0])

    poly_verts = [q[1] for q in all_quads]
    poly_colors = [q[2] for q in all_quads]
    pc = PolyCollection(poly_verts, facecolors=poly_colors, edgecolors='none', antialiased=True, zorder=3)
    ax_b.add_collection(pc)

    # Subtle 3D latitude wireframe rings on the outer shells for 3D shape perception
    for th_lat_deg in [35.0, 62.0, 90.0, 118.0, 145.0]:
        th_lat = np.radians(th_lat_deg)
        re_lat = r_ergo(th_lat)
        xe_l, ye_l, ze_l = kerr_xyz(re_lat, th_lat, phi_shell_outer)
        ue_l, ve_l, _ = project_3d(xe_l, ye_l, ze_l, elev_deg=elev_b)
        lw_lat = 1.3 if th_lat_deg == 90.0 else 0.75
        ax_b.plot(ue_l, ve_l, color=ERGO_LINE, lw=lw_lat, alpha=0.55, zorder=4)

        xp_l, yp_l, zp_l = kerr_xyz(R_PLUS, th_lat, phi_shell_outer)
        up_l, vp_l, _ = project_3d(xp_l, yp_l, zp_l, elev_deg=elev_b)
        ax_b.plot(up_l, vp_l, color=OUTER_LINE, lw=0.9 if th_lat_deg == 90.0 else 0.55,
                  alpha=0.48, zorder=4.2)

    # Draw the two cutaway meridional cross-section faces ONLY for the shaded Ergoregion (between r_e and r_+)
    # No grey/blue fill wall between r_+ and r_- so no ambiguous wedge appears!
    th_face = np.linspace(0.0, np.pi, 300)
    for phi_cut_deg in [phi_cut2_deg, phi_cut1_deg]:
        phi_c = np.radians(phi_cut_deg)
        xe_c, ye_c, ze_c = kerr_xyz(r_ergo(th_face), th_face, phi_c)
        ue_c, ve_c, _ = project_3d(xe_c, ye_c, ze_c, elev_deg=elev_b)

        xp_c, yp_c, zp_c = kerr_xyz(np.full_like(th_face, R_PLUS), th_face, phi_c)
        up_c, vp_c, _ = project_3d(xp_c, yp_c, zp_c, elev_deg=elev_b)

        # Fill Ergoregion cross-section on the cut face (between ergosurface curve and outer horizon curve)
        u_ergo_face = np.concatenate([ue_c, up_c[::-1]])
        v_ergo_face = np.concatenate([ve_c, vp_c[::-1]])
        ax_b.fill(u_ergo_face, v_ergo_face, facecolor=ERGO_FILL, alpha=0.75, zorder=6)

        # Crisp cut-face boundary curves for ergosurface and outer event horizon
        ax_b.plot(ue_c, ve_c, color=ERGO_LINE, lw=2.8, zorder=7.5)
        ax_b.plot(up_c, vp_c, color=OUTER_LINE, lw=2.6, zorder=7.8)

    # Crisp cutaway rim curves for the inner Cauchy horizon at phi_in_cut2 and phi_in_cut1
    for phi_in_deg in [phi_in_cut2_deg, phi_in_cut1_deg]:
        phi_ic = np.radians(phi_in_deg)
        xm_c, ym_c, zm_c = kerr_xyz(np.full_like(th_face, R_MINUS), th_face, phi_ic)
        um_c, vm_c, _ = project_3d(xm_c, ym_c, zm_c, elev_deg=elev_b)
        ax_b.plot(um_c, vm_c, color=INNER_LINE, lw=2.4, zorder=7.2)

    # Also draw the complete equatorial ellipse of the inner Cauchy horizon (dashed in front cutaway)
    # so the viewer clearly sees the separation between the inner horizon equator (R_- = 0.894m) and the ring (a = 0.80m)
    phi_in_front = np.radians(np.linspace(phi_in_cut1_deg, phi_in_cut2_deg, 120))
    xm_eq_f, ym_eq_f, zm_eq_f = kerr_xyz(R_MINUS, np.pi / 2.0, phi_in_front)
    um_eq_f, vm_eq_f, _ = project_3d(xm_eq_f, ym_eq_f, zm_eq_f, elev_deg=elev_b)
    ax_b.plot(um_eq_f, vm_eq_f, color=INNER_LINE, lw=1.6, ls=':', alpha=0.75, zorder=7.3)

    # Outer silhouette limbs of the 3D surfaces
    th_limb = np.linspace(0.0, np.pi, 300)
    for sign_l in [-1.0, 1.0]:
        phi_limb = 0.0 if sign_l > 0 else np.pi
        xe_s, ye_s, ze_s = kerr_xyz(r_ergo(th_limb), th_limb, phi_limb)
        ue_s, ve_s, _ = project_3d(xe_s, ye_s, ze_s, elev_deg=elev_b)
        ax_b.plot(ue_s, ve_s, color=ERGO_LINE, lw=2.3, alpha=0.88, zorder=5.5)

        xp_s, yp_s, zp_s = kerr_xyz(np.full_like(th_limb, R_PLUS), th_limb, phi_limb)
        up_s, vp_s, _ = project_3d(xp_s, yp_s, zp_s, elev_deg=elev_b)
        ax_b.plot(up_s, vp_s, color=OUTER_LINE, lw=1.9, alpha=0.78, zorder=5.6)

    # Vertical Rotation Axis (z) in 3D Cutaway
    _, v_zbot, _ = project_3d(0.0, 0.0, -2.05, elev_deg=elev_b)
    _, v_ztop, _ = project_3d(0.0, 0.0, 1.76, elev_deg=elev_b)
    ax_b.plot([0.0, 0.0], [v_zbot, v_ztop], color=SLATE, lw=1.8, ls='--', zorder=7.0)
    ax_b.annotate("", xy=(0.0, 2.08), xytext=(0.0, 1.62),
                  arrowprops=dict(arrowstyle="-|>,head_length=0.64,head_width=0.36",
                                  color=NAVY, lw=2.5), zorder=10)
    rot_arc_b = Arc((0.0, 1.84), 0.70, 0.22, angle=0, theta1=195, theta2=345,
                    color=ERGO_LINE, lw=2.2, zorder=10)
    ax_b.add_patch(rot_arc_b)
    ax_b.annotate("", xy=(0.34, 1.81), xytext=(0.22, 1.75),
                  arrowprops=dict(arrowstyle="-|>,head_length=0.44,head_width=0.25",
                                  color=ERGO_LINE, lw=1.9), zorder=10)
    ax_b.text(0.0, 2.32, r"Rotation axis ($z$), $\mathbf{J}$",
              color=NAVY, fontsize=14.0, fontweight='bold', ha='center', va='center', zorder=10)

    # 3D Equatorial Ring Singularity: x = a cos(phi), y = a sin(phi), z = 0 (radius a = 0.8m)
    # High-contrast dark amber casing + bright pale-gold core so it stands out sharply from the violet inner horizon
    phi_ring_back = np.radians(np.linspace(phi_in_cut2_deg, 360.0 + phi_in_cut1_deg, 240))
    xr_b = A_VAL * np.cos(phi_ring_back)
    yr_b = A_VAL * np.sin(phi_ring_back)
    ur_b, vr_b, _ = project_3d(xr_b, yr_b, np.zeros_like(xr_b), elev_deg=elev_b)
    ax_b.plot(ur_b, vr_b, color=SING_RIM, lw=4.8, alpha=0.90, zorder=8.4)
    ax_b.plot(ur_b, vr_b, color=SING_GOLD, lw=2.6, alpha=0.98, zorder=8.5)

    phi_ring_front = np.radians(np.linspace(phi_in_cut1_deg, phi_in_cut2_deg, 180))
    xr_f = A_VAL * np.cos(phi_ring_front)
    yr_f = A_VAL * np.sin(phi_ring_front)
    ur_f, vr_f, _ = project_3d(xr_f, yr_f, np.zeros_like(xr_f), elev_deg=elev_b)
    ax_b.plot(ur_f, vr_f, color=SING_RIM, lw=6.2, solid_capstyle='round', zorder=9.2)
    ax_b.plot(ur_f, vr_f, color=SING_GOLD, lw=3.5, solid_capstyle='round', zorder=9.4)

    # 4i. Azimuthal angle phi and +x reference axis in equatorial plane (z = 0)
    x_ref_len = 0.55
    ax_b.plot([0.0, x_ref_len], [0.0, 0.0], color='#475569', lw=1.35, ls='-.', zorder=9.5)
    ax_b.annotate("", xy=(x_ref_len, 0.0), xytext=(x_ref_len - 0.08, 0.0),
                  arrowprops=dict(arrowstyle="-|>,head_length=0.32,head_width=0.17",
                                  color='#475569', lw=1.2), zorder=9.6)
    ax_b.text(0.42, 0.08, r"$+x$", color='#334155', fontsize=12.5, fontweight='bold',
              ha='center', va='bottom', zorder=11.0)

    # Equatorial arc for azimuthal angle phi (from phi = 0 to phi = 58 deg)
    phi_arc_deg = 58.0
    phi_vals = np.radians(np.linspace(0.0, phi_arc_deg, 60))
    r_phi_arc = 0.36
    u_phi_arc = r_phi_arc * np.cos(phi_vals)
    v_phi_arc = -r_phi_arc * np.sin(phi_vals) * np.sin(np.radians(elev_b))
    ax_b.plot(u_phi_arc, v_phi_arc, color='#1e293b', lw=1.5, zorder=9.7)

    # Arrowhead at end of phi arc indicating increasing phi
    phi_end = np.radians(phi_arc_deg)
    u_phi_end = r_phi_arc * np.cos(phi_end)
    v_phi_end = -r_phi_arc * np.sin(phi_end) * np.sin(np.radians(elev_b))
    du_phi = -r_phi_arc * np.sin(phi_end)
    dv_phi = -r_phi_arc * np.cos(phi_end) * np.sin(np.radians(elev_b))
    tan_len = np.hypot(du_phi, dv_phi)
    u_tan = du_phi / tan_len
    v_tan = dv_phi / tan_len
    ax_b.annotate("", xy=(u_phi_end, v_phi_end),
                  xytext=(u_phi_end - 0.06 * u_tan, v_phi_end - 0.06 * v_tan),
                  arrowprops=dict(arrowstyle="-|>,head_length=0.34,head_width=0.18",
                                  color='#1e293b', lw=1.4), zorder=9.8)

    # Label phi
    ax_b.text(0.33, -0.10, r"$\phi$", color='#1e293b', fontsize=14.5, fontweight='bold',
              ha='center', va='center', zorder=11.0)

    # Clean, Simplified Callout Badges in Panel B (5 core labels, 13.8 pt bold)
    # 1. Top-Left: Ergosurface
    u_ergo_lbl, v_ergo_lbl, _ = project_3d(
        *kerr_xyz(r_ergo(np.radians(52.0)), np.radians(52.0), np.radians(160.0)), elev_deg=elev_b
    )
    ax_b.annotate(
        "Ergosurface\n" + r"$r = r_{\mathrm{e}}(\theta)$",
        xy=(u_ergo_lbl, v_ergo_lbl), xytext=(-2.24, 1.95),
        arrowprops=dict(arrowstyle="->", color=ERGO_LINE, lw=1.7, shrinkA=0, shrinkB=3,
                        connectionstyle="arc3,rad=-0.10"),
        fontsize=13.8, fontweight='bold', color=ERGO_DARK, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=ERGO_BADGE_BG, edgecolor=ERGO_BADGE_EC, linewidth=1.35),
        zorder=13
    )

    # 2. Lower-Left: Inner Cauchy horizon
    u_in_pt, v_in_pt, _ = project_3d(
        *kerr_xyz(R_MINUS, np.radians(115.0), np.radians(phi_in_cut2_deg)), elev_deg=elev_b
    )
    ax_b.annotate(
        "Inner Cauchy horizon\n" + r"$r_- = 0.4m$",
        xy=(u_in_pt, v_in_pt), xytext=(-2.16, -1.90),
        arrowprops=dict(arrowstyle="->", color=INNER_LINE, lw=1.7, shrinkA=0, shrinkB=3,
                        connectionstyle="arc3,rad=-0.08"),
        fontsize=13.8, fontweight='bold', color=INNER_DARK, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=INNER_BADGE_BG, edgecolor=INNER_BADGE_EC, linewidth=1.35),
        zorder=13
    )

    # 3. Bottom-Center-Left: Shaded ergosphere on left cutaway face
    th_erg_b = np.radians(145.0)
    r_erg_b = (r_ergo(th_erg_b) + R_PLUS) / 2.0  # Center of the shaded amber cutaway section
    u_erg_face_pt, v_erg_face_pt, _ = project_3d(
        *kerr_xyz(r_erg_b, th_erg_b, np.radians(phi_cut2_deg)), elev_deg=elev_b
    )
    ax_b.annotate(
        "Ergosphere\n(cutaway section)",
        xy=(u_erg_face_pt, v_erg_face_pt), xytext=(-0.55, -2.52),
        arrowprops=dict(arrowstyle="->", color=ERGO_DARK, lw=1.7, shrinkA=0, shrinkB=0,
                        connectionstyle="arc3,rad=-0.10"),
        fontsize=13.6, fontweight='bold', color=ERGO_DARK, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=ERGO_BADGE_BG, edgecolor=ERGO_BADGE_EC, linewidth=1.35),
        zorder=13
    )

    # 4. Top-Right: Outer event horizon r_+
    u_out_pt, v_out_pt, _ = project_3d(
        *kerr_xyz(R_PLUS, np.radians(48.0), np.radians(phi_cut1_deg)), elev_deg=elev_b
    )
    ax_b.annotate(
        "Outer event horizon\n" + r"$r_+ = 1.6m$",
        xy=(u_out_pt, v_out_pt), xytext=(2.14, 1.70),
        arrowprops=dict(arrowstyle="->", color=OUTER_LINE, lw=1.7, shrinkA=0, shrinkB=3,
                        connectionstyle="arc3,rad=0.08"),
        fontsize=13.8, fontweight='bold', color=OUTER_DARK, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=OUTER_BADGE_BG, edgecolor=OUTER_BADGE_EC, linewidth=1.35),
        zorder=13
    )

    # 5. Bottom-Right: Equatorial ring singularity
    phi_ring_lbl = np.radians(55.0)
    u_ring_pt, v_ring_pt, _ = project_3d(
        A_VAL * np.cos(phi_ring_lbl), A_VAL * np.sin(phi_ring_lbl), 0.0, elev_deg=elev_b
    )
    ax_b.annotate(
        "Ring singularity\n" + r"$R = a = 0.8m,\; z = 0$",
        xy=(u_ring_pt, v_ring_pt), xytext=(2.12, -2.10),
        arrowprops=dict(arrowstyle="->", color=SING_RIM, lw=1.7, shrinkA=0, shrinkB=4,
                        connectionstyle="arc3,rad=0.14"),
        fontsize=13.8, fontweight='bold', color=SING_RIM, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=SING_BADGE_BG, edgecolor=SING_BADGE_EC, linewidth=1.35),
        zorder=13
    )

    # Save figure
    fig.savefig(output_path, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    print(f"[OK] Generated {output_path} ({fig_w * dpi:.0f} x {fig_h * dpi:.0f} px)")


if __name__ == "__main__":
    create_figure()
