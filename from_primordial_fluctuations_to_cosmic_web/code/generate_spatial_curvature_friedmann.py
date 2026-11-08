#!/usr/bin/env python3
r"""
Generate editorial figure:
"Spatial Curvature and the Friedmann Equation"

Section 2 figure for:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Scientific & pedagogical specifications:
- Canvas: 1600 x 1300 px (10.0 x 8.125 in at 160 DPI).
- Three side-by-side geometric panels:
  - Panel 1: K = +1, Positive curvature, Spherical surface, Geodesic triangle sum > 180°
  - Panel 2: K = 0, Zero curvature, Euclidean plane, Geodesic triangle sum = 180°
  - Panel 3: K = -1, Negative curvature, Saddle-shaped surface, Geodesic triangle sum < 180°
- Explicit connection to Friedmann equation curvature term (-Kc^2 / a^2):
  - K = +1: -c^2 / a^2 < 0 (negative contribution, lowers H^2 for fixed \rho, \Lambda, a)
  - K = 0: 0 (zero contribution, no curvature contribution to H^2)
  - K = -1: +c^2 / a^2 > 0 (positive contribution, raises H^2 for fixed \rho, \Lambda, a)
- Bottom cards:
  - Card 1: Friedmann equation highlighting -Kc^2/a^2(t) curvature term with authentic LaTeX underbrace.
  - Card 2: Scientific precautions & context (2D visual analogies, spatial curvature and cosmic evolution).
- Accurate hanging indents, uncompressed typography, and generous breathing room.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patheffects as pe
from PIL import Image
import numpy as np
import scipy.optimize as opt
import io

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "spatial_curvature_friedmann.png"


def generate_latex_equation_image():
    """Render the Friedmann equation with genuine LaTeX underbrace to a transparent PNG."""
    orig_usetex = plt.rcParams.get('text.usetex', False)
    orig_preamble = plt.rcParams.get('text.latex.preamble', '')

    plt.rcParams['text.usetex'] = True
    plt.rcParams['text.latex.preamble'] = r'''
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
'''

    # High-res render at 300 DPI for ultra-sharp downsampling
    # Use \displaystyle so all fractions (8piG/3, curvature, Lambda c^2/3) have uniform font size
    fig_tex = plt.figure(figsize=(7.5, 1.8), dpi=300)
    fig_tex.text(
        0.5, 0.55,
        r'$\displaystyle H^2(t) = \frac{8\pi G}{3}\bar\rho(t) + \underbrace{\left(-\frac{Kc^2}{a^2(t)}\right)}_{\text{\footnotesize \textbf{spatial-curvature contribution}}} + \frac{\Lambda c^2}{3}$',
        fontsize=14.0, ha='center', va='center'
    )
    buf = io.BytesIO()
    fig_tex.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.02, transparent=True)
    plt.close(fig_tex)
    buf.seek(0)
    im = Image.open(buf)

    # Restore rcParams immediately to avoid conflicts with Unicode text in main figure
    plt.rcParams['text.usetex'] = orig_usetex
    plt.rcParams['text.latex.preamble'] = orig_preamble

    return im


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Pre-render the LaTeX equation with underbrace
    eq_image = generate_latex_equation_image()

    # Configure mathtext and typography for main figure
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    fig_w, fig_h = 10.0, 8.125
    dpi = 160
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'          # Primary headings
    DARK_SLATE = '#1e293b'    # Main text, panel titles
    SLATE = '#475569'         # Secondary annotations
    BORDER_COLOR = '#cbd5e1'  # Box borders
    CARD_BG = '#f8fafc'       # Card backgrounds

    # Accents for 3 panels
    # Panel 1: Positive curvature / Spherical (Royal Blue)
    BLUE_DARK = '#0369a1'
    BLUE_BG = '#f0f9ff'
    BLUE_BORDER = '#bae6fd'
    BLUE_LINE = '#1d4ed8'
    BLUE_FILL = '#38bdf8'

    # Panel 2: Zero curvature / Flat (Emerald)
    EMERALD_DARK = '#047857'
    EMERALD_BG = '#ecfdf5'
    EMERALD_BORDER = '#a7f3d0'
    EMERALD_LINE = '#059669'
    EMERALD_FILL = '#34d399'

    # Panel 3: Negative curvature / Saddle (Amber / Orange)
    AMBER_DARK = '#b45309'
    AMBER_BG = '#fffbeb'
    AMBER_BORDER = '#fde68a'
    AMBER_LINE = '#c2410c'
    AMBER_FILL = '#fbbf24'

    # -------------------------------------------------------------------------
    # 1. Top Header Banner (y: 0.908 - 0.984, height ~100 px)
    # -------------------------------------------------------------------------
    ax_head = fig.add_axes([0.025, 0.908, 0.950, 0.076])
    ax_head.axis('off')
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)

    title_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.010",
                               mutation_aspect=(0.950 * fig_w) / (0.076 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_head.add_patch(title_box)

    ax_head.text(0.50, 0.68, "SPATIAL CURVATURE AND THE FRIEDMANN EQUATION",
                 color=NAVY, fontsize=14.5, fontweight='bold', ha='center', va='center')
    ax_head.text(0.50, 0.28, "Two-dimensional geometric analogues  •  Geodesic triangles  •  Curvature term in H²(t)",
                 color=SLATE, fontsize=11.8, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 2. Main Three-Panel Cards (y: 0.395 - 0.885, height ~640 px)
    # -------------------------------------------------------------------------
    panel_w = 0.300
    panel_gap = 0.025
    panel_xs = [0.025, 0.025 + panel_w + panel_gap, 0.025 + 2 * (panel_w + panel_gap)]
    panel_y = 0.395
    panel_h = 0.490

    panel_configs = [
        {
            'k_badge': r"$K = +1$",
            'type_title': "POSITIVE CURVATURE",
            'surface_sub': "Spherical surface (2D analogue)",
            'theme_dark': BLUE_DARK,
            'theme_bg': BLUE_BG,
            'theme_border': BLUE_BORDER,
            'sum_val': r"$\alpha + \beta + \gamma > 180^\circ$",
            'sum_desc': "Angles sum to > 180°",
            'curv_label': r"Contribution to $H^2(t)$:",
            'curv_term': r"$-c^2/a^2(t) < 0$  (negative)",
            'curv_effect': r"Lowers $H^2(t)$ for fixed $\bar{\rho},\Lambda,a$",
        },
        {
            'k_badge': r"$K = 0$",
            'type_title': "ZERO CURVATURE",
            'surface_sub': "Euclidean plane (flat model)",
            'theme_dark': EMERALD_DARK,
            'theme_bg': EMERALD_BG,
            'theme_border': EMERALD_BORDER,
            'sum_val': r"$\alpha + \beta + \gamma = 180^\circ$",
            'sum_desc': "Angles sum to exactly 180°",
            'curv_label': r"Contribution to $H^2(t)$:",
            'curv_term': r"$0$  (zero contribution)",
            'curv_effect': r"No curvature contribution to $H^2(t)$",
        },
        {
            'k_badge': r"$K = -1$",
            'type_title': "NEGATIVE CURVATURE",
            'surface_sub': "Saddle surface (hyperbolic)",
            'theme_dark': AMBER_DARK,
            'theme_bg': AMBER_BG,
            'theme_border': AMBER_BORDER,
            'sum_val': r"$\alpha + \beta + \gamma < 180^\circ$",
            'sum_desc': "Angles sum to < 180°",
            'curv_label': r"Contribution to $H^2(t)$:",
            'curv_term': r"$+c^2/a^2(t) > 0$  (positive)",
            'curv_effect': r"Raises $H^2(t)$ for fixed $\bar{\rho},\Lambda,a$",
        },
    ]

    # Card interior layout: raised angle box and curvature box to eliminate empty vertical gap
    sum_y = 0.265
    sum_h = 0.118
    curv_y = 0.025
    curv_h = 0.195

    # Draw 2D background cards and structured text
    for i in range(3):
        px = panel_xs[i]
        cfg = panel_configs[i]

        ax_card = fig.add_axes([px, panel_y, panel_w, panel_h])
        ax_card.axis('off')
        ax_card.set_xlim(0, 1)
        ax_card.set_ylim(0, 1)

        # Outer card container
        card = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                              boxstyle="round,pad=0.0,rounding_size=0.032",
                              mutation_aspect=(panel_w * fig_w) / (panel_h * fig_h),
                              clip_on=False,
                              facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
        ax_card.add_patch(card)

        # 1. Header Pill: K badge
        ax_card.text(0.50, 0.942, cfg['k_badge'],
                     color=cfg['theme_dark'], fontsize=12.2, fontweight='bold', ha='center', va='center',
                     bbox=dict(boxstyle='round,pad=0.20', facecolor=cfg['theme_bg'], edgecolor=cfg['theme_border'], lw=1.2))

        # 2. Curvature Type Title
        ax_card.text(0.50, 0.882, cfg['type_title'],
                     color=NAVY, fontsize=12.2, fontweight='bold', ha='center', va='center')

        # 3. Surface Subtitle
        ax_card.text(0.50, 0.832, cfg['surface_sub'],
                     color=DARK_SLATE, fontsize=11.2, ha='center', va='center')

        # 4. Geodesic Triangle Sum Box
        sum_box = FancyBboxPatch((0.030, sum_y), 0.940, sum_h,
                                 boxstyle="round,pad=0.010,rounding_size=0.04",
                                 facecolor='#ffffff', edgecolor=cfg['theme_border'], linewidth=1.1)
        ax_card.add_patch(sum_box)

        ax_card.text(0.50, sum_y + sum_h * 0.62, cfg['sum_val'],
                     color=cfg['theme_dark'], fontsize=13.0, fontweight='bold', ha='center', va='center')
        ax_card.text(0.50, sum_y + sum_h * 0.22, cfg['sum_desc'],
                     color=DARK_SLATE, fontsize=11.5, ha='center', va='center')

        # 5. Friedmann Curvature Contribution Box
        curv_box = FancyBboxPatch((0.030, curv_y), 0.940, curv_h,
                                  boxstyle="round,pad=0.010,rounding_size=0.04",
                                  facecolor=cfg['theme_bg'], edgecolor=cfg['theme_border'], linewidth=1.1)
        ax_card.add_patch(curv_box)

        # Uncompressed, relaxed interline spacing with comfortable margins
        ax_card.text(0.50, curv_y + curv_h * 0.77, cfg['curv_label'],
                     color=DARK_SLATE, fontsize=11.5, fontweight='bold', ha='center', va='center')
        ax_card.text(0.50, curv_y + curv_h * 0.50, cfg['curv_term'],
                     color=NAVY, fontsize=12.5, fontweight='bold', ha='center', va='center')
        ax_card.text(0.50, curv_y + curv_h * 0.21, cfg['curv_effect'],
                     color=cfg['theme_dark'], fontsize=10.8, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 2.1 3D Geometry Rendering in each panel (y: 0.545 - 0.767)
    # -------------------------------------------------------------------------
    # Lowered slightly to panel_y + 0.150 to close the gap to angle box
    plot_y = panel_y + 0.150
    plot_h = 0.222

    # --- PANEL 1: Spherical Surface (K = +1) ---
    ax1 = fig.add_axes([panel_xs[0] + 0.012, plot_y, panel_w - 0.024, plot_h], projection='3d')
    ax1.set_axis_off()
    ax1.patch.set_alpha(0.0)
    ax1.set_facecolor('none')
    ax1.view_init(elev=26, azim=-48)
    ax1.set_box_aspect([1, 1, 0.70])

    # Spherical cap mesh
    phi = np.linspace(-np.pi * 0.70, np.pi * 0.70, 45)
    theta = np.linspace(0.08, 1.25, 35)
    Phi, Theta = np.meshgrid(phi, theta)
    R = 1.0
    Xs = R * np.sin(Theta) * np.cos(Phi)
    Ys = R * np.sin(Theta) * np.sin(Phi)
    Zs = R * np.cos(Theta)

    ax1.plot_surface(Xs, Ys, Zs, color='#e0f2fe', alpha=0.50, edgecolor='#93c5fd', lw=0.4, rstride=3, cstride=3)

    # Spherical geodesic triangle vertices
    theta_A, phi_A = 0.26, 0.0
    theta_B, phi_B = 1.08, -0.65
    theta_C, phi_C = 1.08, 0.65

    def spherical_to_cart(th, ph):
        return np.array([R * np.sin(th) * np.cos(ph), R * np.sin(th) * np.sin(ph), R * np.cos(th)])

    vA_s = spherical_to_cart(theta_A, phi_A)
    vB_s = spherical_to_cart(theta_B, phi_B)
    vC_s = spherical_to_cart(theta_C, phi_C)

    def slerp(p1, p2, n=40):
        dot = np.clip(np.dot(p1, p2) / (np.linalg.norm(p1) * np.linalg.norm(p2)), -1.0, 1.0)
        omega = np.arccos(dot)
        t = np.linspace(0, 1, n)
        if omega < 1e-6:
            return np.outer(1 - t, p1) + np.outer(t, p2)
        return (np.sin((1 - t) * omega)[:, None] * p1 + np.sin(t * omega)[:, None] * p2) / np.sin(omega)

    arcAB_s = slerp(vA_s, vB_s)
    arcBC_s = slerp(vB_s, vC_s)
    arcCA_s = slerp(vC_s, vA_s)

    for arc in [arcAB_s, arcBC_s, arcCA_s]:
        ax1.plot(arc[:, 0], arc[:, 1], arc[:, 2], color=BLUE_LINE, lw=3.2, zorder=10)

    poly_pts1 = np.vstack([arcAB_s, arcBC_s, arcCA_s])
    ax1.add_collection3d(Poly3DCollection([poly_pts1], color=BLUE_FILL, alpha=0.30))

    for pt in [vA_s, vB_s, vC_s]:
        ax1.scatter([pt[0]], [pt[1]], zs=[pt[2]], color='#1e40af', s=85, edgecolor='#ffffff', lw=2.0, zorder=15)

    # --- PANEL 2: Euclidean Plane (K = 0) ---
    ax2 = fig.add_axes([panel_xs[1] + 0.012, plot_y, panel_w - 0.024, plot_h], projection='3d')
    ax2.set_axis_off()
    ax2.patch.set_alpha(0.0)
    ax2.set_facecolor('none')
    ax2.view_init(elev=26, azim=-48)
    ax2.set_box_aspect([1, 1, 0.70])

    xp = np.linspace(-1.25, 1.25, 15)
    yp = np.linspace(-1.35, 1.05, 15)
    Xp, Yp = np.meshgrid(xp, yp)
    ax2.plot_surface(Xp, Yp, np.zeros_like(Xp), color='#ecfdf5', alpha=0.50, edgecolor='#6ee7b7', lw=0.4)

    pA_flat = np.array([-0.12, 0.65, 0.0])   # top apex
    pB_flat = np.array([-0.80, -0.30, 0.0])  # bottom-left
    pC_flat = np.array([0.65, -0.58, 0.0])   # bottom-right

    for side in [
        np.outer(1 - np.linspace(0, 1, 30), pA_flat) + np.outer(np.linspace(0, 1, 30), pB_flat),
        np.outer(1 - np.linspace(0, 1, 30), pB_flat) + np.outer(np.linspace(0, 1, 30), pC_flat),
        np.outer(1 - np.linspace(0, 1, 30), pC_flat) + np.outer(np.linspace(0, 1, 30), pA_flat),
    ]:
        ax2.plot(side[:, 0], side[:, 1], side[:, 2], color=EMERALD_LINE, lw=3.2, zorder=10)

    ax2.add_collection3d(Poly3DCollection([[pA_flat, pB_flat, pC_flat]], color=EMERALD_FILL, alpha=0.30))

    for pt in [pA_flat, pB_flat, pC_flat]:
        ax2.scatter([pt[0]], [pt[1]], zs=[pt[2]], color='#065f46', s=85, edgecolor='#ffffff', lw=2.0, zorder=15)

    # --- PANEL 3: Saddle Surface (K = -1) - Smooth Circular Hyperbolic Surface ---
    ax3 = fig.add_axes([panel_xs[2] + 0.012, plot_y, panel_w - 0.024, plot_h], projection='3d')
    ax3.set_axis_off()
    ax3.patch.set_alpha(0.0)
    ax3.set_facecolor('none')
    ax3.view_init(elev=28, azim=-65)
    ax3.set_box_aspect([1, 1, 0.65])

    c_sadd = 0.38
    r_sadd = np.linspace(0, 1.0, 25)
    th_sadd = np.linspace(0, 2 * np.pi, 50)
    R_s, Th_s = np.meshgrid(r_sadd, th_sadd)
    Xs_sadd = R_s * np.cos(Th_s)
    Ys_sadd = R_s * np.sin(Th_s)
    Zs_sadd = c_sadd * (Xs_sadd**2 - Ys_sadd**2)

    ax3.plot_surface(Xs_sadd, Ys_sadd, Zs_sadd, color='#fffbeb', alpha=0.55, edgecolor='#d97706', lw=0.35, rstride=2, cstride=2)

    # Smooth saddle rim
    th_rim = np.linspace(0, 2 * np.pi, 100)
    x_rim = np.cos(th_rim)
    y_rim = np.sin(th_rim)
    z_rim = c_sadd * (x_rim**2 - y_rim**2)
    ax3.plot(x_rim, y_rim, z_rim, color='#b45309', lw=1.2)

    def f_saddle(x, y):
        return c_sadd * (x**2 - y**2)

    def compute_saddle_geodesic(p1, p2, N=35):
        t = np.linspace(0, 1, N)
        init_xy = (1 - t[:, None]) * p1 + t[:, None] * p2
        x0 = init_xy[1:-1].flatten()

        def length_obj(vars_flat):
            pts = np.vstack([p1, vars_flat.reshape(-1, 2), p2])
            x, y = pts[:, 0], pts[:, 1]
            z = f_saddle(x, y)
            dist = np.sqrt(np.diff(x)**2 + np.diff(y)**2 + np.diff(z)**2)
            return np.sum(dist)

        res = opt.minimize(length_obj, x0, method='L-BFGS-B')
        opt_pts = np.vstack([p1, res.x.reshape(-1, 2), p2])
        x, y = opt_pts[:, 0], opt_pts[:, 1]
        z = f_saddle(x, y)
        return np.column_stack([x, y, z])

    # Geodesic triangle spanning across saddle:
    # Point A on top-left crest, Point B on top-right crest, Point C in bottom dip
    pA_sadd2D = np.array([-0.45, 0.28])
    pB_sadd2D = np.array([0.40, 0.26])
    pC_sadd2D = np.array([0.0, -0.52])

    vA_sadd = np.array([pA_sadd2D[0], pA_sadd2D[1], f_saddle(pA_sadd2D[0], pA_sadd2D[1])])
    vB_sadd = np.array([pB_sadd2D[0], pB_sadd2D[1], f_saddle(pB_sadd2D[0], pB_sadd2D[1])])
    vC_sadd = np.array([pC_sadd2D[0], pC_sadd2D[1], f_saddle(pC_sadd2D[0], pC_sadd2D[1])])

    arcAB_s = compute_saddle_geodesic(pA_sadd2D, pB_sadd2D)
    arcBC_s = compute_saddle_geodesic(pB_sadd2D, pC_sadd2D)
    arcCA_s = compute_saddle_geodesic(pC_sadd2D, pA_sadd2D)

    for arc in [arcAB_s, arcBC_s, arcCA_s]:
        ax3.plot(arc[:, 0], arc[:, 1], arc[:, 2], color=AMBER_LINE, lw=3.2, zorder=10)

    poly_pts_sadd = np.vstack([arcAB_s, arcBC_s, arcCA_s])
    ax3.add_collection3d(Poly3DCollection([poly_pts_sadd], color=AMBER_FILL, alpha=0.35))

    for pt in [vA_sadd, vB_sadd, vC_sadd]:
        ax3.scatter([pt[0]], [pt[1]], zs=[pt[2]], color='#9a3412', s=85, edgecolor='#ffffff', lw=2.0, zorder=15)

    # Force draw so projection matrices are fully updated
    fig.canvas.draw()

    # -------------------------------------------------------------------------
    # 2.2 Transparent 2D Overlay for Ultra-Crisp, Completely Unoccluded Labels
    # -------------------------------------------------------------------------
    ax_over = fig.add_axes([0, 0, 1, 1], facecolor='none')
    ax_over.axis('off')
    ax_over.set_xlim(0, 1)
    ax_over.set_ylim(0, 1)

    def to_overlay(ax_3d, pt3d):
        x2, y2, _ = proj3d.proj_transform(pt3d[0], pt3d[1], pt3d[2], ax_3d.get_proj())
        disp = ax_3d.transData.transform((x2, y2))
        return ax_over.transAxes.inverted().transform(disp)

    stroke_white = [pe.withStroke(linewidth=3.5, foreground='white')]

    # Panel 1 labels: Sphere
    c1_A = to_overlay(ax1, vA_s)
    c1_B = to_overlay(ax1, vB_s)
    c1_C = to_overlay(ax1, vC_s)
    t1_A = ax_over.text(c1_A[0] - 0.005, c1_A[1] + 0.012, r"$\alpha$", color='#1e40af', fontsize=16.0, fontweight='bold')
    t1_B = ax_over.text(c1_B[0] - 0.022, c1_B[1] - 0.004, r"$\beta$", color='#1e40af', fontsize=16.0, fontweight='bold')
    t1_C = ax_over.text(c1_C[0] + 0.012, c1_C[1] - 0.004, r"$\gamma$", color='#1e40af', fontsize=16.0, fontweight='bold')
    for t in [t1_A, t1_B, t1_C]:
        t.set_path_effects(stroke_white)

    # Panel 2 labels: Euclidean Plane
    c2_A = to_overlay(ax2, pA_flat)
    c2_B = to_overlay(ax2, pB_flat)
    c2_C = to_overlay(ax2, pC_flat)
    t2_A = ax_over.text(c2_A[0] + 0.008, c2_A[1] + 0.008, r"$\alpha$", color='#065f46', fontsize=16.0, fontweight='bold')
    t2_B = ax_over.text(c2_B[0] - 0.022, c2_B[1] - 0.005, r"$\beta$", color='#065f46', fontsize=16.0, fontweight='bold')
    t2_C = ax_over.text(c2_C[0] + 0.010, c2_C[1] - 0.010, r"$\gamma$", color='#065f46', fontsize=16.0, fontweight='bold')
    for t in [t2_A, t2_B, t2_C]:
        t.set_path_effects(stroke_white)

    # Panel 3 labels: Saddle (High-contrast, 100% visible, outside surface occlusion)
    c3_A = to_overlay(ax3, vA_sadd)
    c3_B = to_overlay(ax3, vB_sadd)
    c3_C = to_overlay(ax3, vC_sadd)
    t3_A = ax_over.text(c3_A[0] - 0.012, c3_A[1] + 0.012, r"$\alpha$", color='#7c2d12', fontsize=16.0, fontweight='bold')
    t3_C = ax_over.text(c3_C[0] - 0.022, c3_C[1] - 0.010, r"$\beta$", color='#7c2d12', fontsize=16.0, fontweight='bold')
    t3_B = ax_over.text(c3_B[0] + 0.012, c3_B[1] + 0.010, r"$\gamma$", color='#7c2d12', fontsize=16.0, fontweight='bold')
    for t in [t3_A, t3_B, t3_C]:
        t.set_path_effects(stroke_white)

    # -------------------------------------------------------------------------
    # 3. Bottom Cards Strip: Height ~460 px (y: 0.020 - 0.375)
    # -------------------------------------------------------------------------
    card_bot_y = 0.020
    card_bot_h = 0.355

    # Card 1 (Left: x: 0.025 - 0.485): Friedmann Equation & Curvature Scaling
    ax_bot_left = fig.add_axes([0.025, card_bot_y, 0.460, card_bot_h])
    ax_bot_left.axis('off')
    ax_bot_left.set_xlim(0, 1)
    ax_bot_left.set_ylim(0, 1)

    card_l = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                            boxstyle="round,pad=0.0,rounding_size=0.021",
                            mutation_aspect=(0.460 * fig_w) / (card_bot_h * fig_h),
                            clip_on=False,
                            facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_bot_left.add_patch(card_l)

    ax_bot_left.text(0.040, 0.930, "THE FRIEDMANN CURVATURE TERM",
                     color=NAVY, fontsize=12.0, fontweight='bold', va='center')

    # Embed authentic LaTeX equation with underbrace spanning solely the curvature term
    aspect_eq = eq_image.height / eq_image.width
    w_frac = 0.82
    h_frac = w_frac * aspect_eq * (4.6 / 3.55)
    y_center = 0.74
    x0_eq = 0.50 - w_frac / 2
    x1_eq = 0.50 + w_frac / 2
    y0_eq = y_center - h_frac / 2
    y1_eq = y_center + h_frac / 2
    ax_bot_left.imshow(eq_image, extent=[x0_eq, x1_eq, y0_eq, y1_eq], aspect='auto', zorder=10)

    # Explanatory bullet points with sub-pixel accurate hanging indents
    # Bullet width of '• ' in DejaVu Sans 11.2 pt is 23.0 px
    # 23.0 px / (0.460 * 10.0 in * 160 dpi) = 23.0 / 736.0 = 0.03125 axes fraction
    hang_indent = 23.0 / (0.460 * fig_w * dpi)
    bullet_l_y = [0.525, 0.465, 0.405, 0.345, 0.260, 0.200, 0.115, 0.055]
    lines_l = [
        ("• The magnitude of the curvature term", 0.040, DARK_SLATE),
        ("scales as a⁻², decreasing more slowly", 0.040 + hang_indent, DARK_SLATE),
        ("during cosmic expansion than matter", 0.040 + hang_indent, DARK_SLATE),
        ("density (a⁻³) and radiation density (a⁻⁴).", 0.040 + hang_indent, DARK_SLATE),
        ("• K = +1 contributes negatively to H²(t)", 0.040, DARK_SLATE),
        ("for fixed background terms (ρ̄, Λ, a).", 0.040 + hang_indent, DARK_SLATE),
        ("• K = -1 contributes positively to H²(t)", 0.040, DARK_SLATE),
        ("for the same fixed quantities.", 0.040 + hang_indent, DARK_SLATE),
    ]

    for (txt, x_pos, col), y_pos in zip(lines_l, bullet_l_y):
        ax_bot_left.text(x_pos, y_pos, txt, color=col, fontsize=11.2, va='center')

    # Card 2 (Right: x: 0.515 - 0.975): Scientific Precautions & Interpretation
    ax_bot_right = fig.add_axes([0.515, card_bot_y, 0.460, card_bot_h])
    ax_bot_right.axis('off')
    ax_bot_right.set_xlim(0, 1)
    ax_bot_right.set_ylim(0, 1)

    card_r = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                            boxstyle="round,pad=0.0,rounding_size=0.021",
                            mutation_aspect=(0.460 * fig_w) / (card_bot_h * fig_h),
                            clip_on=False,
                            facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_bot_right.add_patch(card_r)

    ax_bot_right.text(0.040, 0.930, "SCIENTIFIC PRECAUTIONS & CONTEXT",
                      color=NAVY, fontsize=12.0, fontweight='bold', va='center')

    # Bullet 1 (2D analogies) + Bullet 2 (Spatial curvature & cosmic evolution)
    bullet_r_y = [
        0.740, 0.670, 0.600,
        0.430, 0.360, 0.290, 0.220
    ]
    lines_r = [
        ("• 2D visual analogies: Sphere, plane, and", 0.040, DARK_SLATE),
        ("saddle illustrate 3D spatial curvature only", 0.040 + hang_indent, DARK_SLATE),
        ("schematically, not literally.", 0.040 + hang_indent, DARK_SLATE),
        ("• Spatial curvature and cosmic evolution:", 0.040, DARK_SLATE),
        ("In standard cosmology, late-time expansion", 0.040 + hang_indent, DARK_SLATE),
        ("is dominated by the cosmological constant and", 0.040 + hang_indent, DARK_SLATE),
        ("is not determined by spatial curvature alone.", 0.040 + hang_indent, DARK_SLATE),
    ]

    for (txt, x_pos, col), y_pos in zip(lines_r, bullet_r_y):
        ax_bot_right.text(x_pos, y_pos, txt, color=col, fontsize=11.2, va='center')

    plt.savefig(output_path, dpi=dpi, facecolor='#ffffff')
    plt.close(fig)
    print(f"Figure successfully saved to: {output_path}")


if __name__ == "__main__":
    create_figure()
