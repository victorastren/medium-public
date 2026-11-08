#!/usr/bin/env python3
r"""
Generate two-level scientific schematic:
"From Anisotropic Collapse to the Cosmic Web"

Figure 4 for Section "From Linear Perturbations to the Cosmic Web" of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design & Scientific Specifications:
- Canvas: 2000 x 1141 px (14.2857 x 8.15 in at 140 DPI), matching the exact
  typography and font hierarchy of `cdm_baryon_perturbation_evolution.png`
  and `horizon_entry_perturbations.png`:
  - 18.0 pt bold main title
  - 14.0 pt bold subtitle & panel header bands
  - 14.0-14.5 pt bold primary structural labels
  - 13.5-13.8 pt secondary annotations and mathematical labels
- Top row (Panels A, B, C): Three idealized local collapse geometries
  (NOT a chronological time sequence):
  - Panel A (A · ONE DIRECTION): Compression along \mathbf{e}_1 with
    1 - D\lambda_1 \rightarrow 0, producing a flattened Sheet / pancake
    ("compressed along \mathbf{e}_1", "onset of first shell crossing").
  - Panel B (B · TWO DIRECTIONS): Compression along \mathbf{e}_1 and \mathbf{e}_2,
    producing an elongated Filament ("compressed along \mathbf{e}_1 and \mathbf{e}_2").
  - Panel C (C · THREE DIRECTIONS): Compression along \mathbf{e}_1, \mathbf{e}_2,
    and \mathbf{e}_3, producing a compact Node / halo ("compressed along \mathbf{e}_1, \mathbf{e}_2, and \mathbf{e}_3").
- Transition between levels: Subtle bracket and downward arrow labelled
  "Beyond first shell crossing: nonlinear evolution".
- Bottom panel (NONLINEAR EVOLUTION · COSMIC WEB): Continuous wide collisionless
  particle-density network ("multistreaming after shell crossing") showing how
  a coherent 2D tilted sheet, filaments, nodes / halos, and voids (with subtle
  outward velocity arrows) fit together after nonlinear gravitational evolution.
"""

from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as patheffects
from matplotlib.patches import FancyBboxPatch, Polygon
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "anisotropic_collapse_cosmic_web.png"


def project_3d(x, y, z, cx=5.55, cy=5.12, scale=1.05):
    """
    Clean oblique 3D projection onto 2D panel coordinates:
      x -> horizontal axis (e_3)
      y -> oblique depth axis (e_2, receding at 32 deg)
      z -> vertical axis (e_1)
    """
    angle = np.deg2rad(32.0)
    depth_scale = 0.56
    px = cx + scale * (x + depth_scale * np.cos(angle) * y)
    py = cy + scale * (z + depth_scale * np.sin(angle) * y)
    return px, py


def draw_cube_wireframe(ax, cx, cy, scale, half_side=1.56, color='#94a3b8'):
    """Draw a subtle 3D comoving reference cube wireframe."""
    s = half_side
    corners = {}
    for ix in (-1, 1):
        for iy in (-1, 1):
            for iz in (-1, 1):
                corners[(ix, iy, iz)] = project_3d(ix * s, iy * s, iz * s, cx=cx, cy=cy, scale=scale)

    edges = [
        # Back face (iy = +1)
        ((-1, 1, -1), (1, 1, -1)), ((-1, 1, 1), (1, 1, 1)),
        ((-1, 1, -1), (-1, 1, 1)), ((1, 1, -1), (1, 1, 1)),
        # Connecting depth edges
        ((-1, -1, -1), (-1, 1, -1)), ((1, -1, -1), (1, 1, -1)),
        ((-1, -1, 1), (-1, 1, 1)), ((1, -1, 1), (1, 1, 1)),
        # Front face (iy = -1)
        ((-1, -1, -1), (1, -1, -1)), ((-1, -1, 1), (1, -1, 1)),
        ((-1, -1, -1), (-1, -1, 1)), ((1, -1, -1), (1, -1, 1)),
    ]
    for c1, c2 in edges:
        x1, y1 = corners[c1]
        x2, y2 = corners[c2]
        is_back = (c1[1] == 1 and c2[1] == 1) or (c1 == (-1, -1, -1) and c2 == (-1, 1, -1))
        lw = 1.0 if is_back else 1.2
        alpha = 0.42 if is_back else 0.65
        ax.plot([x1, x2], [y1, y2], color=color, linestyle='--', linewidth=lw, alpha=alpha, zorder=1)


def draw_principal_triad(ax, ox, oy):
    """Draw the 3 principal axes triad (e_1 vertical, e_2 oblique depth, e_3 horizontal)."""
    axis_col = '#334155'
    # e_1 (vertical)
    ax.annotate("", xy=(ox, oy + 1.22), xytext=(ox, oy),
                arrowprops=dict(arrowstyle="-|>", color=axis_col, lw=1.6, mutation_scale=11),
                zorder=8)
    ax.text(ox, oy + 1.29, r"$\mathbf{e}_1$", fontsize=13.5, fontweight='bold',
            color='#0f172a', ha='center', va='bottom', zorder=9)

    # e_2 (oblique depth)
    dx2 = 0.86 * np.cos(np.deg2rad(32.0))
    dy2 = 0.86 * np.sin(np.deg2rad(32.0))
    ax.annotate("", xy=(ox + dx2, oy + dy2), xytext=(ox, oy),
                arrowprops=dict(arrowstyle="-|>", color=axis_col, lw=1.6, mutation_scale=11),
                zorder=8)
    ax.text(ox + dx2 + 0.06, oy + dy2 + 0.05, r"$\mathbf{e}_2$", fontsize=13.5, fontweight='bold',
            color='#0f172a', ha='left', va='bottom', zorder=9)

    # e_3 (horizontal)
    ax.annotate("", xy=(ox + 1.22, oy), xytext=(ox, oy),
                arrowprops=dict(arrowstyle="-|>", color=axis_col, lw=1.6, mutation_scale=11),
                zorder=8)
    ax.text(ox + 1.29, oy - 0.04, r"$\mathbf{e}_3$", fontsize=13.5, fontweight='bold',
            color='#0f172a', ha='left', va='center', zorder=9)


def draw_compression_arrow(ax, x1, y1, x2, y2, color='#b91c1c'):
    """Draw a compression arrow with a subtle white halo so it remains crisp over dense particles."""
    arr = ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=2.3, mutation_scale=14.5),
        zorder=8
    )
    arr.arrow_patch.set_path_effects([
        patheffects.Stroke(linewidth=4.2, foreground='#ffffff', alpha=0.85),
        patheffects.Normal()
    ])


def sample_filament_points(rng, p0, p1, ctrl, n_pts, w_env, w_mid, w_core):
    """Sample collisionless particles along a quadratic Bezier filament curve with 3-scale profile."""
    u_raw = rng.uniform(0.0, 1.0, n_pts)
    t = np.where(rng.random(n_pts) < 0.25, rng.beta(0.65, 0.65, n_pts), u_raw)

    bx = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * ctrl[0] + t ** 2 * p1[0]
    by = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * ctrl[1] + t ** 2 * p1[1]

    tx = 2 * (1 - t) * (ctrl[0] - p0[0]) + 2 * t * (p1[0] - ctrl[0])
    ty = 2 * (1 - t) * (ctrl[1] - p0[1]) + 2 * t * (p1[1] - ctrl[1])
    norm = np.hypot(tx, ty) + 1e-9
    nx = -ty / norm
    ny = tx / norm

    r_draw = rng.random(n_pts)
    tier = np.zeros(n_pts, dtype=int)  # 0: env, 1: mid, 2: core
    tier[r_draw >= 0.30] = 1
    tier[r_draw >= 0.68] = 2

    sigma = np.where(tier == 0, w_env, np.where(tier == 1, w_mid, w_core))
    flare = 1.0 + 0.35 * (np.exp(-t / 0.12) + np.exp(-(1.0 - t) / 0.12))
    offset = rng.normal(0.0, sigma * flare)

    px = bx + nx * offset
    py = by + ny * offset
    return px, py, tier


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure mathtext and typography (exact match to cdm_baryon_perturbation_evolution.png)
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    # Canvas: 2000 x 1141 px at 140 DPI (14.2857 x 8.15 in)
    fig_w, fig_h = 2000.0 / 140.0, 1141.0 / 140.0
    dpi = 140
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Curated Editorial Palette (harmonized with previous diagrams)
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#475569'
    LIGHT_SLATE = '#64748b'
    BORDER_COLOR = '#cbd5e1'
    CARD_BG = '#f8fafc'

    # Restrained collisionless density palette (diffuse -> sheet -> filament -> node)
    DIFFUSE_COL = '#94a3b8'
    SHEET_FILL = '#dbeafe'
    SHEET_EDGE = '#3b82f6'
    SHEET_PARTICLE = '#2563eb'
    FILAMENT_ENV = '#60a5fa'
    FILAMENT_MID = '#2563eb'
    FILAMENT_CORE = '#1e3a8a'
    NODE_OUTER = '#1e3a8a'
    NODE_CORE = '#0f172a'

    # Compression arrow color (crisp crimson-rust)
    ARROW_COL = '#b91c1c'

    # Panel header styling
    HDR_BG_TOP = '#eff6ff'
    HDR_BORDER_TOP = '#bfdbfe'
    HDR_TEXT_TOP = '#1e3a8a'

    HDR_BG_BOT = '#f1f5f9'
    HDR_BORDER_BOT = '#cbd5e1'

    # -------------------------------------------------------------------------
    # 1. Top Header Banner (y: 0.904 - 0.982)
    # -------------------------------------------------------------------------
    ax_head = fig.add_axes([0.025, 0.904, 0.950, 0.078])
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)
    ax_head.axis('off')

    title_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.008",
                               mutation_aspect=(0.950 * fig_w) / (0.078 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_head.add_patch(title_box)
    ax_head.text(0.50, 0.65, "FROM ANISOTROPIC COLLAPSE TO THE COSMIC WEB",
                 color=NAVY, fontsize=18.0, fontweight='bold', ha='center', va='center')
    ax_head.text(0.50, 0.26,
                 "Idealized principal-axis compression geometries and the nonlinear emergence of the cosmic web",
                 color=SLATE, fontsize=14.0, fontweight='bold', ha='center', va='center')

    # =========================================================================
    # 2. TOP ROW: THREE IDEALIZED LOCAL COLLAPSE GEOMETRIES (y: 0.498 - 0.890)
    # =========================================================================
    panel_y = 0.498
    panel_h = 0.392
    panel_w = 0.304
    panel_xs = [0.025, 0.348, 0.671]

    rng = np.random.default_rng(42)

    cx_p, cy_p, sc_p = 5.50, 5.15, 1.02
    s_cube = 1.54

    # -------------------------------------------------------------------------
    # PANEL A — ONE DIRECTION -> Sheet / pancake
    # -------------------------------------------------------------------------
    ax_a = fig.add_axes([panel_xs[0], panel_y, panel_w, panel_h])
    ax_a.set_xlim(0, 10)
    ax_a.set_ylim(0, 10)
    ax_a.axis('off')

    box_a = FancyBboxPatch((0.0, 0.0), 10.0, 10.0,
                           boxstyle="round,pad=0.0,rounding_size=0.25",
                           mutation_aspect=(panel_w * fig_w) / (panel_h * fig_h),
                           clip_on=False,
                           facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_a.add_patch(box_a)

    hdr_a = FancyBboxPatch((0.22, 8.72), 9.56, 1.06,
                           boxstyle="round,pad=0.0,rounding_size=0.18",
                           mutation_aspect=(panel_w * fig_w) / (panel_h * fig_h),
                           facecolor=HDR_BG_TOP, edgecolor=HDR_BORDER_TOP, linewidth=1.2)
    ax_a.add_patch(hdr_a)
    ax_a.text(5.0, 9.25, "A · ONE DIRECTION",
              color=HDR_TEXT_TOP, fontsize=14.2, fontweight='bold', ha='center', va='center')

    draw_cube_wireframe(ax_a, cx_p, cy_p, sc_p, half_side=s_cube)
    draw_principal_triad(ax_a, 0.62, 5.95)

    # Equation annotation (top right of Panel A, cleanly above cube)
    ax_a.text(9.60, 8.08, r"$1 - D\lambda_1 \rightarrow 0$",
              color=NAVY, fontsize=13.8, fontweight='bold', ha='right', va='center',
              bbox=dict(boxstyle='round,pad=0.22,rounding_size=0.15',
                        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.1),
              zorder=9)

    # Subtle midplane polygon (sheet / pancake) at z = 0
    sheet_corners_3d = [(-s_cube, -s_cube, 0.0), (s_cube, -s_cube, 0.0),
                        (s_cube, s_cube, 0.0), (-s_cube, s_cube, 0.0)]
    sheet_pts_2d = [project_3d(x, y, z, cx=cx_p, cy=cy_p, scale=sc_p) for x, y, z in sheet_corners_3d]
    sheet_poly = Polygon(sheet_pts_2d, closed=True, facecolor=SHEET_FILL,
                         edgecolor=SHEET_EDGE, linewidth=1.4, alpha=0.68, zorder=3)
    ax_a.add_patch(sheet_poly)

    # Diffuse initial particles in the 3D cube
    n_diff_a = 230
    dx_a = rng.uniform(-1.48, 1.48, n_diff_a)
    dy_a = rng.uniform(-1.48, 1.48, n_diff_a)
    dz_a = rng.uniform(-1.45, 1.45, n_diff_a)
    px_da, py_da = project_3d(dx_a, dy_a, dz_a, cx=cx_p, cy=cy_p, scale=sc_p)
    ax_a.scatter(px_da, py_da, s=6.5, color=DIFFUSE_COL, alpha=0.42, edgecolors='none', zorder=2)

    # Dense sheet particles concentrated near z ~ 0, extended across x (e_3) and y (e_2)
    n_sheet = 1350
    sx_a = rng.uniform(-1.50, 1.50, n_sheet)
    sy_a = rng.uniform(-1.50, 1.50, n_sheet)
    sz_a = rng.normal(0.0, 0.070, n_sheet)
    px_sa, py_sa = project_3d(sx_a, sy_a, sz_a, cx=cx_p, cy=cy_p, scale=sc_p)
    ax_a.scatter(px_sa, py_sa, s=8.0, color=SHEET_PARTICLE, alpha=0.75, edgecolors='none', zorder=4)

    # Compression arrows purely along e_1 (vertical) from above and below
    for x_arr, y_arr in [(-0.98, -0.38), (0.0, 0.0), (0.98, 0.38)]:
        x_t1, y_t1 = project_3d(x_arr, y_arr, 1.52, cx=cx_p, cy=cy_p, scale=sc_p)
        x_t2, y_t2 = project_3d(x_arr, y_arr, 0.22, cx=cx_p, cy=cy_p, scale=sc_p)
        draw_compression_arrow(ax_a, x_t1, y_t1, x_t2, y_t2, color=ARROW_COL)

        x_b1, y_b1 = project_3d(x_arr, y_arr, -1.52, cx=cx_p, cy=cy_p, scale=sc_p)
        x_b2, y_b2 = project_3d(x_arr, y_arr, -0.22, cx=cx_p, cy=cy_p, scale=sc_p)
        draw_compression_arrow(ax_a, x_b1, y_b1, x_b2, y_b2, color=ARROW_COL)

    # Bottom labels in Panel A (aligned with Panels B and C, plus shell-crossing badge)
    ax_a.text(5.0, 2.02, "Sheet / pancake",
              color=NAVY, fontsize=14.5, fontweight='bold', ha='center', va='center', zorder=8)
    ax_a.text(5.0, 1.32, r"compressed along $\mathbf{e}_1$",
              color=SLATE, fontsize=13.5, ha='center', va='center', zorder=8)
    ax_a.text(5.0, 0.54, "onset of first shell crossing",
              color='#9a3412', fontsize=13.2, fontweight='bold', style='italic',
              ha='center', va='center',
              bbox=dict(boxstyle='round,pad=0.18,rounding_size=0.14',
                        facecolor='#fff7ed', edgecolor='#fdba74', linewidth=1.1),
              zorder=8)

    # -------------------------------------------------------------------------
    # PANEL B — TWO DIRECTIONS -> Filament
    # -------------------------------------------------------------------------
    ax_b = fig.add_axes([panel_xs[1], panel_y, panel_w, panel_h])
    ax_b.set_xlim(0, 10)
    ax_b.set_ylim(0, 10)
    ax_b.axis('off')

    box_b = FancyBboxPatch((0.0, 0.0), 10.0, 10.0,
                           boxstyle="round,pad=0.0,rounding_size=0.25",
                           mutation_aspect=(panel_w * fig_w) / (panel_h * fig_h),
                           clip_on=False,
                           facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_b.add_patch(box_b)

    hdr_b = FancyBboxPatch((0.22, 8.72), 9.56, 1.06,
                           boxstyle="round,pad=0.0,rounding_size=0.18",
                           mutation_aspect=(panel_w * fig_w) / (panel_h * fig_h),
                           facecolor=HDR_BG_TOP, edgecolor=HDR_BORDER_TOP, linewidth=1.2)
    ax_b.add_patch(hdr_b)
    ax_b.text(5.0, 9.25, "B · TWO DIRECTIONS",
              color=HDR_TEXT_TOP, fontsize=14.2, fontweight='bold', ha='center', va='center')

    draw_cube_wireframe(ax_b, cx_p, cy_p, sc_p, half_side=s_cube)
    draw_principal_triad(ax_b, 0.62, 5.95)

    # Diffuse initial particles in the 3D cube
    n_diff_b = 230
    dx_b = rng.uniform(-1.48, 1.48, n_diff_b)
    dy_b = rng.uniform(-1.48, 1.48, n_diff_b)
    dz_b = rng.uniform(-1.45, 1.45, n_diff_b)
    px_db, py_db = project_3d(dx_b, dy_b, dz_b, cx=cx_p, cy=cy_p, scale=sc_p)
    ax_b.scatter(px_db, py_db, s=6.5, color=DIFFUSE_COL, alpha=0.40, edgecolors='none', zorder=2)

    # Filament particles extended along x (e_3), compressed along z (e_1) and y (e_2)
    n_fil_env = 700
    fx_env = rng.uniform(-1.52, 1.52, n_fil_env)
    fy_env = rng.normal(0.0, 0.18, n_fil_env)
    fz_env = rng.normal(0.0, 0.16, n_fil_env)
    px_fe, py_fe = project_3d(fx_env, fy_env, fz_env, cx=cx_p, cy=cy_p, scale=sc_p)
    ax_b.scatter(px_fe, py_fe, s=8.0, color=FILAMENT_MID, alpha=0.62, edgecolors='none', zorder=4)

    n_fil_core = 950
    fx_core = rng.uniform(-1.50, 1.50, n_fil_core)
    fy_core = rng.normal(0.0, 0.075, n_fil_core)
    fz_core = rng.normal(0.0, 0.070, n_fil_core)
    px_fc, py_fc = project_3d(fx_core, fy_core, fz_core, cx=cx_p, cy=cy_p, scale=sc_p)
    ax_b.scatter(px_fc, py_fc, s=9.5, color=FILAMENT_CORE, alpha=0.85, edgecolors='none', zorder=5)

    # Compression arrows along e_1 (vertical) at two positions along the filament
    for x_arr in (-0.88, 0.88):
        x_t1, y_t1 = project_3d(x_arr, 0.0, 1.52, cx=cx_p, cy=cy_p, scale=sc_p)
        x_t2, y_t2 = project_3d(x_arr, 0.0, 0.24, cx=cx_p, cy=cy_p, scale=sc_p)
        draw_compression_arrow(ax_b, x_t1, y_t1, x_t2, y_t2, color=ARROW_COL)

        x_b1, y_b1 = project_3d(x_arr, 0.0, -1.52, cx=cx_p, cy=cy_p, scale=sc_p)
        x_b2, y_b2 = project_3d(x_arr, 0.0, -0.24, cx=cx_p, cy=cy_p, scale=sc_p)
        draw_compression_arrow(ax_b, x_b1, y_b1, x_b2, y_b2, color=ARROW_COL)

    # Compression arrows along e_2 (oblique depth) from front-left and back-right
    for x_arr in (0.0,):
        x_f1, y_f1 = project_3d(x_arr, -1.90, 0.0, cx=cx_p, cy=cy_p, scale=sc_p)
        x_f2, y_f2 = project_3d(x_arr, -0.34, 0.0, cx=cx_p, cy=cy_p, scale=sc_p)
        draw_compression_arrow(ax_b, x_f1, y_f1, x_f2, y_f2, color=ARROW_COL)

        x_k1, y_k1 = project_3d(x_arr, 1.90, 0.0, cx=cx_p, cy=cy_p, scale=sc_p)
        x_k2, y_k2 = project_3d(x_arr, 0.34, 0.0, cx=cx_p, cy=cy_p, scale=sc_p)
        draw_compression_arrow(ax_b, x_k1, y_k1, x_k2, y_k2, color=ARROW_COL)

    # Bottom labels in Panel B (horizontally aligned with Panel A and Panel C)
    ax_b.text(5.0, 2.02, "Filament",
              color=NAVY, fontsize=14.5, fontweight='bold', ha='center', va='center', zorder=8)
    ax_b.text(5.0, 1.32, r"compressed along $\mathbf{e}_1$ and $\mathbf{e}_2$",
              color=SLATE, fontsize=13.5, ha='center', va='center', zorder=8)

    # -------------------------------------------------------------------------
    # PANEL C — THREE DIRECTIONS -> Node / halo
    # -------------------------------------------------------------------------
    ax_c = fig.add_axes([panel_xs[2], panel_y, panel_w, panel_h])
    ax_c.set_xlim(0, 10)
    ax_c.set_ylim(0, 10)
    ax_c.axis('off')

    box_c = FancyBboxPatch((0.0, 0.0), 10.0, 10.0,
                           boxstyle="round,pad=0.0,rounding_size=0.25",
                           mutation_aspect=(panel_w * fig_w) / (panel_h * fig_h),
                           clip_on=False,
                           facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_c.add_patch(box_c)

    hdr_c = FancyBboxPatch((0.22, 8.72), 9.56, 1.06,
                           boxstyle="round,pad=0.0,rounding_size=0.18",
                           mutation_aspect=(panel_w * fig_w) / (panel_h * fig_h),
                           facecolor=HDR_BG_TOP, edgecolor=HDR_BORDER_TOP, linewidth=1.2)
    ax_c.add_patch(hdr_c)
    ax_c.text(5.0, 9.25, "C · THREE DIRECTIONS",
              color=HDR_TEXT_TOP, fontsize=14.2, fontweight='bold', ha='center', va='center')

    draw_cube_wireframe(ax_c, cx_p, cy_p, sc_p, half_side=s_cube)
    draw_principal_triad(ax_c, 0.62, 5.95)

    # Diffuse initial particles in the 3D cube
    n_diff_c = 200
    dx_c = rng.uniform(-1.48, 1.48, n_diff_c)
    dy_c = rng.uniform(-1.48, 1.48, n_diff_c)
    dz_c = rng.uniform(-1.45, 1.45, n_diff_c)
    px_dc, py_dc = project_3d(dx_c, dy_c, dz_c, cx=cx_p, cy=cy_p, scale=sc_p)
    ax_c.scatter(px_dc, py_dc, s=6.5, color=DIFFUSE_COL, alpha=0.36, edgecolors='none', zorder=2)

    # Compact, clearly denser collisionless halo concentration at the center
    n_halo_env = 650
    hx_e = rng.normal(0.0, 0.36, n_halo_env)
    hy_e = rng.normal(0.0, 0.36, n_halo_env)
    hz_e = rng.normal(0.0, 0.36, n_halo_env)
    px_he, py_he = project_3d(hx_e, hy_e, hz_e, cx=cx_p, cy=cy_p, scale=sc_p)
    ax_c.scatter(px_he, py_he, s=8.0, color=FILAMENT_MID, alpha=0.58, edgecolors='none', zorder=4)

    n_halo_mid = 850
    hx_m = rng.normal(0.0, 0.19, n_halo_mid)
    hy_m = rng.normal(0.0, 0.19, n_halo_mid)
    hz_m = rng.normal(0.0, 0.19, n_halo_mid)
    px_hm, py_hm = project_3d(hx_m, hy_m, hz_m, cx=cx_p, cy=cy_p, scale=sc_p)
    ax_c.scatter(px_hm, py_hm, s=9.5, color=NODE_OUTER, alpha=0.78, edgecolors='none', zorder=5)

    n_halo_core = 900
    hx_c = rng.normal(0.0, 0.090, n_halo_core)
    hy_c = rng.normal(0.0, 0.090, n_halo_core)
    hz_c = rng.normal(0.0, 0.090, n_halo_core)
    px_hc, py_hc = project_3d(hx_c, hy_c, hz_c, cx=cx_p, cy=cy_p, scale=sc_p)
    ax_c.scatter(px_hc, py_hc, s=11.0, color=NODE_CORE, alpha=0.92, edgecolors='none', zorder=6)

    # Compression arrows along all 3 principal axes (e_1 vertical, e_2 depth, e_3 horizontal)
    for sgn in (-1, 1):
        x1, y1 = project_3d(0.0, 0.0, sgn * 1.52, cx=cx_p, cy=cy_p, scale=sc_p)
        x2, y2 = project_3d(0.0, 0.0, sgn * 0.42, cx=cx_p, cy=cy_p, scale=sc_p)
        draw_compression_arrow(ax_c, x1, y1, x2, y2, color=ARROW_COL)
    for sgn in (-1, 1):
        x1, y1 = project_3d(sgn * 1.54, 0.0, 0.0, cx=cx_p, cy=cy_p, scale=sc_p)
        x2, y2 = project_3d(sgn * 0.44, 0.0, 0.0, cx=cx_p, cy=cy_p, scale=sc_p)
        draw_compression_arrow(ax_c, x1, y1, x2, y2, color=ARROW_COL)
    for sgn in (-1, 1):
        x1, y1 = project_3d(0.0, sgn * 1.92, 0.0, cx=cx_p, cy=cy_p, scale=sc_p)
        x2, y2 = project_3d(0.0, sgn * 0.52, 0.0, cx=cx_p, cy=cy_p, scale=sc_p)
        draw_compression_arrow(ax_c, x1, y1, x2, y2, color=ARROW_COL)

    # Bottom labels in Panel C (horizontally aligned with Panel A and Panel B)
    ax_c.text(5.0, 2.02, "Node / halo",
              color=NAVY, fontsize=14.5, fontweight='bold', ha='center', va='center', zorder=8)
    ax_c.text(5.0, 1.32, r"compressed along $\mathbf{e}_1$, $\mathbf{e}_2$, and $\mathbf{e}_3$",
              color=SLATE, fontsize=13.5, ha='center', va='center', zorder=8)

    # =========================================================================
    # 3. TRANSITION BRACKET & ARROW BETWEEN LEVELS (y: 0.420 - 0.494)
    # =========================================================================
    ax_trans = fig.add_axes([0.025, 0.420, 0.950, 0.074])
    ax_trans.set_xlim(0, 1)
    ax_trans.set_ylim(0, 1)
    ax_trans.axis('off')

    x_left_br = (panel_xs[0] + 0.5 * panel_w - 0.025) / 0.950
    x_right_br = (panel_xs[2] + 0.5 * panel_w - 0.025) / 0.950
    x_mid_br = 0.50

    ax_trans.plot([x_left_br, x_left_br, x_right_br, x_right_br],
                  [0.92, 0.62, 0.62, 0.92],
                  color='#64748b', linewidth=1.8, solid_capstyle='round', zorder=2)
    ax_trans.plot([x_mid_br, x_mid_br], [0.92, 0.62],
                  color='#64748b', linewidth=1.8, zorder=2)

    # Downward arrow into bottom panel
    ax_trans.annotate("", xy=(x_mid_br, 0.02), xytext=(x_mid_br, 0.42),
                      arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2.3, mutation_scale=15),
                      zorder=4)

    # Revised pill label on the transition
    ax_trans.text(x_mid_br, 0.62, "After first shell crossing: nonlinear evolution",
                  color=NAVY, fontsize=13.8, fontweight='bold', ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.22,rounding_size=0.16',
                            facecolor='#f8fafc', edgecolor='#94a3b8', linewidth=1.3),
                  zorder=5)

    # =========================================================================
    # 4. BOTTOM PANEL: NONLINEAR COSMIC WEB (y: 0.020 - 0.416)
    # =========================================================================
    ax_web = fig.add_axes([0.025, 0.020, 0.950, 0.396])
    ax_web.set_xlim(0, 20)
    ax_web.set_ylim(0, 8.5)
    ax_web.axis('off')

    web_aspect = ((0.950 * fig_w) / 20.0) / ((0.396 * fig_h) / 8.5)
    web_box = FancyBboxPatch((0.0, 0.0), 20.0, 8.5,
                             boxstyle="round,pad=0.0,rounding_size=0.16",
                             mutation_aspect=web_aspect,
                             clip_on=False,
                             facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_web.add_patch(web_box)

    # Simplified header band inside bottom panel
    hdr_web = FancyBboxPatch((0.16, 7.36), 19.68, 0.96,
                             boxstyle="round,pad=0.0,rounding_size=0.12",
                             mutation_aspect=web_aspect,
                             facecolor=HDR_BG_BOT, edgecolor=HDR_BORDER_BOT, linewidth=1.2)
    ax_web.add_patch(hdr_web)
    ax_web.text(0.48, 7.84, "NONLINEAR EVOLUTION · COSMIC WEB",
                color=NAVY, fontsize=14.2, fontweight='bold', ha='left', va='center')
    ax_web.text(19.52, 7.84, "multistreaming after shell crossing",
                color=SLATE, fontsize=13.6, fontweight='bold', style='italic', ha='right', va='center')

    # -------------------------------------------------------------------------
    # Construct a natural, multi-scale collisionless cosmic-web network
    # with a coherent, visibly flat 2D sheet facet, filaments, nodes, and voids
    # -------------------------------------------------------------------------
    n1 = (5.45, 5.30)   # Left-central major node (at upper corner of tilted sheet)
    n2 = (12.45, 5.35)  # Right-central major node (3-way hub)
    n3 = (5.95, 1.35)   # Lower-left node (at lower-right corner of tilted sheet)
    n4 = (11.95, 1.30)  # Lower-central node
    n5 = (15.55, 3.35)  # Intermediate right 3-way junction node
    n6 = (18.45, 5.85)  # Upper-right node
    n7 = (18.35, 1.35)  # Lower-right node

    # 1. Sparse background / void particles across the entire field
    n_bg = 1050
    bg_x = rng.uniform(0.35, 19.65, n_bg)
    bg_y = rng.uniform(0.30, 7.10, n_bg)

    # Suppress background density inside the major voids AND to the left of the sheet
    # so the tilted 2D sheet has a crisp, unmistakable boundary against low-density space
    v1_cx, v1_cy, v1_rx, v1_ry = 8.95, 3.30, 2.95, 1.90
    v2_cx, v2_cy, v2_rx, v2_ry = 15.65, 5.25, 2.15, 1.25
    v3_cx, v3_cy, v3_rx, v3_ry = 15.35, 1.85, 2.15, 1.15
    v0_cx, v0_cy, v0_rx, v0_ry = 1.65, 3.35, 1.45, 1.85
    d_v1 = ((bg_x - v1_cx) / v1_rx) ** 2 + ((bg_y - v1_cy) / v1_ry) ** 2
    d_v2 = ((bg_x - v2_cx) / v2_rx) ** 2 + ((bg_y - v2_cy) / v2_ry) ** 2
    d_v3 = ((bg_x - v3_cx) / v3_rx) ** 2 + ((bg_y - v3_cy) / v3_ry) ** 2
    d_v0 = ((bg_x - v0_cx) / v0_rx) ** 2 + ((bg_y - v0_cy) / v0_ry) ** 2
    d_min = np.minimum(np.minimum(d_v1, d_v0), np.minimum(d_v2, d_v3))
    keep_prob = np.clip(0.14 + 0.86 * d_min, 0.14, 1.0)
    keep_mask = rng.random(n_bg) < keep_prob
    ax_web.scatter(bg_x[keep_mask], bg_y[keep_mask], s=5.0, color=DIFFUSE_COL,
                   alpha=0.34, edgecolors='none', zorder=1)

    # 2. Coherent, visibly flat 2D Sheet (planar wall spanning between bounding filaments
    # and feeding into nodes n1 and n3, with a crisp flat oblique edge against the left void)
    sh_tl = np.array([2.10, 5.72])   # Top-left vertex of planar sheet wall
    sh_tr = np.array([n1[0], n1[1]]) # Top-right vertex at Node n1
    sh_br = np.array([n3[0], n3[1]]) # Bottom-right vertex at Node n3
    sh_bl = np.array([2.70, 1.88])   # Bottom-left vertex of planar sheet wall

    sheet_poly_pts = [sh_tl, sh_tr, sh_br, sh_bl]
    web_sheet_patch = Polygon(sheet_poly_pts, closed=True, facecolor='#dbeafe',
                              edgecolor='#3b82f6', linestyle='-', linewidth=1.35,
                              alpha=0.62, zorder=2)
    ax_web.add_patch(web_sheet_patch)

    # Coherent sheet particles arranged in subtle coplanar bands + uniform planar fill
    # so the structure immediately reads as a flat 2D overdense membrane rather than a diffuse cloud
    n_web_sheet = 2500
    u_sh = rng.uniform(0.015, 0.985, n_web_sheet)
    # Mix uniform v with gentle laminar bands parallel to the sheet's principal plane
    v_base = rng.uniform(0.015, 0.985, n_web_sheet)
    v_band = np.clip(v_base + 0.018 * np.sin(9.0 * np.pi * v_base), 0.015, 0.985)
    sh_pts = (np.outer((1 - u_sh) * (1 - v_band), sh_tl) +
              np.outer(u_sh * (1 - v_band), sh_tr) +
              np.outer(u_sh * v_band, sh_br) +
              np.outer((1 - u_sh) * v_band, sh_bl))
    sh_x = sh_pts[:, 0] + rng.normal(0.0, 0.025, n_web_sheet)
    sh_y = sh_pts[:, 1] + rng.normal(0.0, 0.025, n_web_sheet)
    ax_web.scatter(sh_x, sh_y, s=6.2, color=SHEET_PARTICLE, alpha=0.58, edgecolors='none', zorder=3)

    # Crisp linear particle caustic along the flat left boundary (sh_tl -> sh_bl)
    n_ed = 360
    s_ed = rng.uniform(0.0, 1.0, n_ed)
    ed_pts = np.outer(1 - s_ed, sh_tl) + np.outer(s_ed, sh_bl)
    ax_web.scatter(ed_pts[:, 0] + rng.normal(0.0, 0.022, n_ed),
                   ed_pts[:, 1] + rng.normal(0.0, 0.022, n_ed),
                   s=6.8, color='#1d4ed8', alpha=0.75, edgecolors='none', zorder=4)

    # 3. Network of curved primary and secondary filaments (natural 3-way cellular foam)
    filaments = [
        # (start, end, control_point, n_particles, w_env, w_mid, w_core)
        # Main upper arch between n1 and n2 (bounding top of central void)
        (n1, n2, (8.90, 6.08), 2800, 0.29, 0.145, 0.058),
        # Upper-left filament spur into sh_tl, then straight planar boundary ridge into n1
        ((0.65, 6.45), tuple(sh_tl), (1.35, 6.10), 800, 0.22, 0.110, 0.048),
        (tuple(sh_tl), n1, (3.78, 5.51), 1300, 0.21, 0.105, 0.048),
        # Lower-left filament spur into sh_bl, then straight planar boundary ridge into n3
        ((0.85, 0.95), tuple(sh_bl), (1.75, 1.40), 800, 0.22, 0.110, 0.048),
        (tuple(sh_bl), n3, (4.32, 1.61), 1300, 0.21, 0.105, 0.048),
        # Left wall of central void / right spine where the flat sheet meets the filament (n1 to n3)
        (n1, n3, (5.70, 3.32), 2200, 0.25, 0.125, 0.055),
        # Bottom bridge bounding central void (n3 to n4)
        (n3, n4, (8.90, 0.68), 2400, 0.27, 0.135, 0.056),
        # Right wall of central void (n2 to n4, curving slightly inward)
        (n2, n4, (12.60, 3.35), 2100, 0.27, 0.135, 0.056),
        # Curved filament from n2 to n5
        (n2, n5, (14.15, 4.55), 1550, 0.24, 0.120, 0.052),
        # Upper-right arch from n2 to n6 (arching around upper-right void)
        (n2, n6, (15.35, 6.65), 1800, 0.25, 0.125, 0.054),
        # Curved filament from n5 to n6 (closing upper-right cell)
        (n5, n6, (17.45, 4.35), 1450, 0.24, 0.120, 0.052),
        # Curved filament from n4 to n7 (arching along bottom-right)
        (n4, n7, (15.15, 0.68), 1650, 0.24, 0.120, 0.052),
        # Curved filament from n5 to n7 (closing lower-right cell)
        (n5, n7, (17.25, 2.55), 1450, 0.24, 0.120, 0.052),
        # Tenuous sub-filaments / spurs extending toward boundaries
        (n2, (11.20, 6.95), (11.95, 6.25), 650, 0.19, 0.095, 0.042),
        (n6, (19.55, 6.60), (19.05, 6.25), 550, 0.19, 0.095, 0.042),
        (n7, (19.55, 0.85), (18.95, 1.05), 550, 0.19, 0.095, 0.042),
    ]

    for p0, p1, ctrl, n_pts, w_env, w_mid, w_core in filaments:
        px_f, py_f, tier = sample_filament_points(rng, p0, p1, ctrl, n_pts, w_env, w_mid, w_core)
        valid = (px_f > 0.25) & (px_f < 19.75) & (py_f > 0.22) & (py_f < 7.20)
        px_f, py_f, tier = px_f[valid], py_f[valid], tier[valid]

        m0 = tier == 0
        m1 = tier == 1
        m2 = tier == 2
        ax_web.scatter(px_f[m0], py_f[m0], s=5.5, color=FILAMENT_ENV,
                       alpha=0.42, edgecolors='none', zorder=3)
        ax_web.scatter(px_f[m1], py_f[m1], s=6.8, color=FILAMENT_MID,
                       alpha=0.65, edgecolors='none', zorder=4)
        ax_web.scatter(px_f[m2], py_f[m2], s=8.0, color=FILAMENT_CORE,
                       alpha=0.84, edgecolors='none', zorder=5)

    # 4. Dense Nodes / Halos at filament intersections (smooth 3-tier radial profile)
    nodes_spec = [
        (n1[0], n1[1], 1.05, 1750),  # Major Node 1
        (n2[0], n2[1], 1.15, 2000),  # Major Node 2
        (n3[0], n3[1], 0.78, 1050),  # Node 3
        (n4[0], n4[1], 0.82, 1150),  # Node 4
        (n5[0], n5[1], 0.75, 950),   # Node 5
        (n6[0], n6[1], 0.72, 850),   # Node 6
        (n7[0], n7[1], 0.70, 800),   # Node 7
    ]
    for nx_c, ny_c, scale_n, n_pts_n in nodes_spec:
        n_env_n = int(0.38 * n_pts_n)
        n_mid_n = int(0.34 * n_pts_n)
        n_cor_n = n_pts_n - n_env_n - n_mid_n

        ox = rng.normal(nx_c, 0.36 * scale_n, n_env_n)
        oy = rng.normal(ny_c, 0.36 * scale_n, n_env_n)
        ax_web.scatter(ox, oy, s=7.0, color=FILAMENT_MID, alpha=0.55, edgecolors='none', zorder=5)

        mx = rng.normal(nx_c, 0.20 * scale_n, n_mid_n)
        my = rng.normal(ny_c, 0.20 * scale_n, n_mid_n)
        ax_web.scatter(mx, my, s=9.0, color=NODE_OUTER, alpha=0.78, edgecolors='none', zorder=6)

        ix = rng.normal(nx_c, 0.095 * scale_n, n_cor_n)
        iy = rng.normal(ny_c, 0.095 * scale_n, n_cor_n)
        ax_web.scatter(ix, iy, s=11.0, color=NODE_CORE, alpha=0.92, edgecolors='none', zorder=7)

    # -------------------------------------------------------------------------
    # 5. Subtle outward velocity arrows inside the central Void
    # -------------------------------------------------------------------------
    vcx, vcy = 9.05, 3.25
    void_arrows = [
        (0, 1.45, 2.35),     # Right toward right filament
        (42, 1.25, 2.05),    # Up-right
        (90, 0.90, 1.65),    # Up toward upper filament
        (138, 1.25, 2.05),   # Up-left
        (180, 1.45, 2.35),   # Left toward left filament
        (222, 1.25, 1.98),   # Down-left
        (270, 0.90, 1.65),   # Down toward bottom filament
        (318, 1.25, 1.98),   # Down-right
    ]
    for ang_deg, r_in, r_out in void_arrows:
        rad = np.deg2rad(ang_deg)
        x_start = vcx + r_in * np.cos(rad)
        y_start = vcy + r_in * 0.76 * np.sin(rad)
        x_end = vcx + r_out * np.cos(rad)
        y_end = vcy + r_out * 0.76 * np.sin(rad)
        ax_web.annotate("", xy=(x_end, y_end), xytext=(x_start, y_start),
                        arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=1.5,
                                        mutation_scale=11, alpha=0.85),
                        zorder=6)

    # -------------------------------------------------------------------------
    # 6. Crisp, Sparingly Attached Callout Labels in the Cosmic Web
    # -------------------------------------------------------------------------
    label_bbox = dict(boxstyle='round,pad=0.24,rounding_size=0.16',
                      facecolor='#ffffff', edgecolor='#94a3b8', linewidth=1.2, alpha=0.96)

    # Label 1: "sheet" (placed cleanly in the open left space, pointing to the flat 2D sheet wall)
    ax_web.text(1.15, 3.85, "sheet",
                color='#1e40af', fontsize=14.2, fontweight='bold', ha='center', va='center',
                bbox=label_bbox, zorder=9)
    ax_web.annotate("", xy=(3.35, 3.75), xytext=(1.82, 3.82),
                    arrowprops=dict(arrowstyle="-|>", color='#1e40af', lw=1.7, mutation_scale=12),
                    zorder=9)

    # Label 2: "filament" (pointing to the prominent upper filament arch)
    ax_web.text(8.15, 6.62, "filament",
                color=NAVY, fontsize=14.2, fontweight='bold', ha='center', va='center',
                bbox=label_bbox, zorder=9)
    ax_web.annotate("", xy=(9.45, 5.76), xytext=(8.75, 6.32),
                    arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.7, mutation_scale=12),
                    zorder=9)

    # Label 3: "node / halo" (pointing to the major intersection hub n2)
    ax_web.text(15.25, 5.35, "node / halo",
                color=NAVY, fontsize=14.2, fontweight='bold', ha='center', va='center',
                bbox=label_bbox, zorder=9)
    ax_web.annotate("", xy=(13.05, 5.35), xytext=(14.12, 5.35),
                    arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.7, mutation_scale=12),
                    zorder=9)

    # Label 4: "void" (centered inside the large underdense region)
    ax_web.text(vcx, vcy + 0.18, "void",
                color=DARK_SLATE, fontsize=14.5, fontweight='bold', ha='center', va='center',
                zorder=9)
    ax_web.text(vcx, vcy - 0.32, "outward matter flow",
                color=SLATE, fontsize=13.0, style='italic', ha='center', va='center',
                zorder=9)

    # Save figure
    fig.savefig(output_path, dpi=dpi, facecolor='#ffffff')
    plt.close(fig)

    print(f"[OK] Generated {output_path}")


if __name__ == "__main__":
    create_figure()
