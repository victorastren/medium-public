#!/usr/bin/env python3
r"""
Generate scientific illustration & animation (1920 x 1080 px):
"FROM SPHERICAL TO OBLATE SPHEROIDAL COORDINATES"
"Continuous coordinate deformation at fixed radial coordinate r = m"

Figure & Animation Companion for Section "The Geometry of a Rotating Black Hole" of:
"The Golden Age of Black Hole Physics (1963–1974)"

Scientific Specifications:
- Focuses exclusively on the transition from spherical to oblate spheroidal coordinate surfaces.
- Keeps radial coordinate r fixed at r = m (m = 1.0), while varying rotation parameter a continuously from 0 to 0.8m.
- Transformation equations:
    x = \sqrt{r^2 + a^2} \sin\theta \cos\phi
    y = \sqrt{r^2 + a^2} \sin\theta \sin\phi
    z = r \cos\theta
- Coordinate surface satisfies:
    (x^2 + y^2) / (r^2 + a^2) + z^2 / r^2 = 1
- Key geometric feature:
    At fixed r, the surface expands equatorially from R_eq = r to R_eq = \sqrt{r^2 + a^2}
    (an outward expansion of +28.1% for a = 0.8m), while the polar semiaxis R_polar = r
    remains strictly constant.
- Single 3D perspective plot showing:
    - 3D coordinate axes (x, y, z), with rotation axis aligned with z.
    - Initial spherical state (a = 0, r = m) shown as a fixed reference.
    - Active 3D coordinate surface deforming continuously from sphere to oblate spheroid.
    - Dimension indicators for polar semiaxis (constant) and equatorial semiaxis (expanding).
    - Dynamic telemetry readout badge updating in real time.
    - Smooth forward-and-reverse loop (0 -> 0.8m -> 0).
- Outputs:
  1. Static publication figure: images/boyer_lindquist_coordinates.png (1920 x 1080 px)
  2. Animated GIF: images/boyer_lindquist_coordinates_animation.gif (1800 x 1012 px)
  3. Master MP4: images/boyer_lindquist_coordinates_animation.mp4
"""

import os
import sys
import time
import shutil
import subprocess
import tempfile
import multiprocessing
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Circle, Arc

SCRIPT_DIR = Path(__file__).resolve().parent
PNG_OUT = SCRIPT_DIR.parent / "images" / "boyer_lindquist_coordinates.png"
GIF_OUT = SCRIPT_DIR.parent / "images" / "boyer_lindquist_coordinates_animation.gif"
MP4_OUT = SCRIPT_DIR.parent / "images" / "boyer_lindquist_coordinates_animation.mp4"


# Physical & Geometric Constants
M_VAL = 1.0
R_VAL = 1.0  # Fixed radial coordinate r = m
A_MAX = 0.8  # Maximum spin parameter a = 0.8m

ELEV_DEG = 22.0
ELEV = np.radians(ELEV_DEG)
COS_EL = np.cos(ELEV)
SIN_EL = np.sin(ELEV)

# Palette matching existing article figures
NAVY = '#0f172a'
SLATE = '#334155'
MUTED = '#475569'
LIGHT_SLATE = '#64748b'
CARD_BG = '#f8fafc'
BORDER_COLOR = '#cbd5e1'

# Reference sphere colors (neutral slate/gray)
SPHERE_EDGE = '#94a3b8'
SPHERE_WIRE = '#cbd5e1'

# Active surface colors (luminous blue/cyan)
KERR_EDGE = '#2563eb'
KERR_FILL = '#dbeafe'
KERR_WIRE = '#60a5fa'

# Animation parameters
FPS = 20
DURATION_SEC = 8.0
N_FRAMES = int(FPS * DURATION_SEC)  # 160 frames


def draw_spheroid_3d(ax, r, a, fill=True, alpha=0.32, edge_color=KERR_EDGE, wire_color=KERR_WIRE, lw=2.2, zorder=5):
    """Draw an orthographically projected 3D oblate spheroid at coordinate radius r and spin a."""
    Req = np.sqrt(r**2 + a**2)
    H = np.sqrt(r**2 + (a * SIN_EL)**2)

    if fill:
        sil = Ellipse((0, 0), 2 * Req, 2 * H, facecolor=KERR_FILL, edgecolor=edge_color,
                      linewidth=lw, alpha=alpha, zorder=zorder)
        ax.add_patch(sil)
    else:
        sil = Ellipse((0, 0), 2 * Req, 2 * H, facecolor='none', edgecolor=edge_color,
                      linewidth=lw, ls='--', zorder=zorder)
        ax.add_patch(sil)

    # Equator (z = 0)
    eq_front = Arc((0, 0), 2 * Req, 2 * Req * SIN_EL, angle=0, theta1=180, theta2=360,
                   color=wire_color, lw=lw * 0.9, zorder=zorder + 0.2)
    eq_back = Arc((0, 0), 2 * Req, 2 * Req * SIN_EL, angle=0, theta1=0, theta2=180,
                  color=wire_color, lw=lw * 0.7, ls=':', zorder=zorder - 0.2)
    ax.add_patch(eq_front)
    ax.add_patch(eq_back)

    # Parallels at theta = 45 deg and 135 deg
    for th_deg in [45, 135]:
        th = np.radians(th_deg)
        z0 = r * np.cos(th)
        v0 = z0 * COS_EL
        r_th = Req * np.sin(th)
        par_f = Arc((0, v0), 2 * r_th, 2 * r_th * SIN_EL, angle=0, theta1=180, theta2=360,
                    color=wire_color, lw=lw * 0.7, alpha=0.85, zorder=zorder + 0.1)
        par_b = Arc((0, v0), 2 * r_th, 2 * r_th * SIN_EL, angle=0, theta1=0, theta2=180,
                    color=wire_color, lw=lw * 0.5, ls=':', alpha=0.6, zorder=zorder - 0.1)
        ax.add_patch(par_f)
        ax.add_patch(par_b)

    # Central meridian
    mer_f = Arc((0, 0), 2 * Req * SIN_EL, 2 * r * COS_EL, angle=0, theta1=270, theta2=90,
                color=wire_color, lw=lw * 0.7, alpha=0.85, zorder=zorder + 0.1)
    mer_b = Arc((0, 0), 2 * Req * SIN_EL, 2 * r * COS_EL, angle=0, theta1=90, theta2=270,
                color=wire_color, lw=lw * 0.5, ls=':', alpha=0.6, zorder=zorder - 0.1)
    ax.add_patch(mer_f)
    ax.add_patch(mer_b)


def render_scene(a_val, is_static=False, output_path=None):
    """Render a single frame or the static publication figure."""
    fig_w, fig_h = 1920 / 140, 1080 / 140
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=140, facecolor='#ffffff')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # 1. Header Card (height = 0.208, y0 = 0.776)
    title_box = FancyBboxPatch((0.015, 0.776), 0.970, 0.208,
                               boxstyle="round,pad=0.002,rounding_size=0.008",
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax.add_patch(title_box)

    ax.text(0.50, 0.954, "BOYER–LINDQUIST COORDINATES: FROM SPHERICAL TO OBLATE SPHEROIDAL SURFACES",
            color=NAVY, fontsize=18.5, fontweight='bold', ha='center', va='center')
    ax.text(0.50, 0.916,
            r"Spatial coordinate surfaces at fixed Boyer–Lindquist time $t$   ($t = \mathrm{constant},\quad r = m,\quad 0 \leq a/m \leq 0.8$)",
            color=SLATE, fontsize=14.2, fontweight='bold', ha='center', va='center')

    part1 = r"Auxiliary mapping:   $x = \sqrt{r^2+a^2}\sin\theta\cos\phi,\quad y = \sqrt{r^2+a^2}\sin\theta\sin\phi,\quad z = r\cos\theta$"
    part2 = r"Coordinate surface:   $\frac{x^2+y^2}{r^2+a^2} + \frac{z^2}{r^2} = 1$   (equatorial semiaxis $\sqrt{r^2+a^2}$, polar semiaxis $r$)"

    fs_eq = 13.5
    t1 = ax.text(0.5, 0, part1, fontsize=fs_eq, fontweight='bold')
    t2 = ax.text(0.5, 0, part2, fontsize=fs_eq, fontweight='bold')
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    w1 = t1.get_window_extent(r).width / 1920
    w2 = t2.get_window_extent(r).width / 1920
    t1.remove()
    t2.remove()

    w_max = max(w1, w2)
    x_left = (1.0 - w_max) / 2.0

    ax.text(x_left, 0.864, part1,
            color="#1e293b", fontsize=fs_eq, fontweight='bold', ha='left', va='center')
    ax.text(x_left, 0.806, part2,
            color="#1e293b", fontsize=fs_eq, fontweight='bold', ha='left', va='center')

    # 2. Main Center Card
    panel_y0, panel_h = 0.012, 0.754
    panel_x0, panel_w = 0.015, 0.970

    pcard = FancyBboxPatch((panel_x0, panel_y0), panel_w, panel_h,
                           boxstyle="round,pad=0.002,rounding_size=0.008",
                           facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4)
    ax.add_patch(pcard)

    phead_h = 0.076
    phead = FancyBboxPatch((panel_x0, panel_y0 + panel_h - phead_h), panel_w, phead_h,
                           boxstyle="round,pad=0.002,rounding_size=0.008",
                           facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.2)
    ax.add_patch(phead)

    ax.text(panel_x0 + 0.020, panel_y0 + panel_h - 0.024,
            "Continuous coordinate deformation at fixed radial coordinate r = m",
            color=NAVY, fontsize=15.5, fontweight='bold', ha='left', va='center')
    ax.text(panel_x0 + 0.020, panel_y0 + panel_h - 0.054,
            "Equatorial semiaxis expands from r to √(r² + a²) while polar semiaxis remains fixed at r",
            color=SLATE, fontsize=12.8, fontweight='bold', ha='left', va='center')

    # 3. Main Plotting Axes inside Card
    axes_y0 = 0.096
    axes_h = 0.580
    axes_w = panel_w - 0.040
    ax_plot = fig.add_axes([panel_x0 + 0.020, axes_y0, axes_w, axes_h])

    Y_LIM = 1.35
    aspect_plot = (axes_w * 1920) / (axes_h * 1080)
    X_LIM = Y_LIM * aspect_plot

    ax_plot.set_aspect('equal')
    ax_plot.set_xlim(-X_LIM, X_LIM)
    ax_plot.set_ylim(-Y_LIM, Y_LIM)
    ax_plot.axis('off')

    # Coordinate Axes (x, y, z)
    # +z axis (vertical)
    z_arrow_tip = 1.08
    z_arrow_base = 0.98
    z_label_y = 1.14

    ax_plot.plot([0, 0], [-1.22, z_arrow_tip], color=SLATE, lw=1.6, ls='--', zorder=3)
    ax_plot.annotate("", xy=(0, z_arrow_tip), xytext=(0, z_arrow_base),
                     arrowprops=dict(arrowstyle="-|>,head_length=0.34,head_width=0.20", color=SLATE, lw=1.6), zorder=4)
    ax_plot.text(0, z_label_y, r"Rotation axis ($z$)", color=SLATE, fontsize=13.6, fontweight='bold', ha='center', va='bottom')

    # +x axis (right)
    ax_plot.plot([-2.05, 2.05], [0, 0], color='#94a3b8', lw=1.2, ls=':', zorder=2)
    ax_plot.text(2.10, 0, r"$+x$", color='#475569', fontsize=13.2, fontweight='bold', ha='left', va='center')

    # +y axis (perspective projected towards viewer)
    y_axis_len = 1.60
    u_y_end = -y_axis_len * np.cos(np.radians(35))
    v_y_end = -y_axis_len * np.sin(np.radians(35)) * SIN_EL
    ax_plot.plot([0, u_y_end], [0, v_y_end], color='#94a3b8', lw=1.2, ls=':', zorder=2)
    ax_plot.text(u_y_end - 0.08, v_y_end - 0.05, r"$+y$", color='#475569', fontsize=13.2, fontweight='bold', ha='right', va='top')

    # Fixed Reference Sphere at a = 0 (radius r = 1.0m)
    draw_spheroid_3d(ax_plot, r=R_VAL, a=0.0, fill=False, edge_color=SPHERE_EDGE, wire_color=SPHERE_WIRE, lw=1.4, zorder=3)

    # Label for reference sphere
    ax_plot.annotate(
        "Spherical reference\n" + r"$a = 0,\; r = 1.00m$",
        xy=(-R_VAL * np.cos(np.radians(52)), -R_VAL * np.sin(np.radians(52)) * SIN_EL),
        xytext=(-1.70, -0.65),
        arrowprops=dict(arrowstyle="->", color='#64748b', lw=1.4, shrinkA=0, shrinkB=4, connectionstyle="arc3,rad=-0.12"),
        fontsize=12.5, fontweight='bold', color='#334155', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.28', facecolor='#ffffff', edgecolor='#cbd5e1', lw=1.1, alpha=0.96),
        zorder=16
    )

    # Active oblate spheroid
    Req_active = np.sqrt(R_VAL**2 + a_val**2)

    # Active surface
    draw_spheroid_3d(ax_plot, r=R_VAL, a=a_val, fill=True, alpha=0.32,
                     edge_color=KERR_EDGE, wire_color=KERR_WIRE, lw=2.4, zorder=6)

    # Polar dimension arrow: from (0,0) to (0, R_VAL * cos(el)) — strictly constant
    ax_plot.annotate("", xy=(0, R_VAL * COS_EL), xytext=(0, 0),
                     arrowprops=dict(arrowstyle="<->", color='#0f766e', lw=1.8), zorder=12)

    # Callout badge for Polar Semiaxis (upper left)
    ax_plot.annotate(
        "Polar semiaxis (constant):\n" + r"$R_{\mathrm{polar}} = r = 1.00m$",
        xy=(0, R_VAL * COS_EL * 0.60), xytext=(-1.45, 0.75),
        arrowprops=dict(arrowstyle="->", color='#0f766e', lw=1.5, shrinkA=0, shrinkB=4, connectionstyle="arc3,rad=0.10"),
        fontsize=12.8, fontweight='bold', color='#0f766e', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.28', facecolor='#f0fdfa', edgecolor='#5eead4', lw=1.2, alpha=0.96),
        zorder=16
    )

    # Equatorial dimension arrow: from (0,0) to (Req_active, 0) — dynamically expanding
    ax_plot.annotate("", xy=(Req_active, 0), xytext=(0, 0),
                     arrowprops=dict(arrowstyle="<->", color='#1d4ed8', lw=1.8), zorder=12)

    # Callout badge for Equatorial Semiaxis (upper right)
    ax_plot.annotate(
        "Equatorial semiaxis (expanding):\n" + f"$R_{{\\mathrm{{eq}}}} = \\sqrt{{r^2 + a^2}} = {Req_active:.2f}m$",
        xy=(Req_active * 0.60, 0), xytext=(1.45, 0.75),
        arrowprops=dict(arrowstyle="->", color='#1d4ed8', lw=1.5, shrinkA=0, shrinkB=4, connectionstyle="arc3,rad=-0.10"),
        fontsize=12.8, fontweight='bold', color='#1d4ed8', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.28', facecolor='#eff6ff', edgecolor='#93c5fd', lw=1.2, alpha=0.96),
        zorder=16
    )

    # Lateral expansion arrows at equator showing outward expansion (when a_val > 0.08)
    expansion_pct = (Req_active / R_VAL - 1.0) * 100.0
    if a_val > 0.08:
        ax_plot.annotate("", xy=(Req_active + 0.02, 0), xytext=(R_VAL, 0),
                         arrowprops=dict(arrowstyle="->,head_length=0.30,head_width=0.16", color='#d97706', lw=2.2), zorder=14)
        ax_plot.text(Req_active + 0.08, 0, f"Bulge: +{expansion_pct:.0f}%",
                     color='#b45309', fontsize=12.2, fontweight='bold', ha='left', va='center',
                     bbox=dict(boxstyle='round,pad=0.18', facecolor='#fffbeb', edgecolor='#fcd34d', lw=1.0, alpha=0.96),
                     zorder=15)

        ax_plot.annotate("", xy=(-Req_active - 0.02, 0), xytext=(-R_VAL, 0),
                         arrowprops=dict(arrowstyle="->,head_length=0.30,head_width=0.16", color='#d97706', lw=2.2), zorder=14)

    # Bottom Telemetry Readout Box on Canvas
    readout_y0 = panel_y0 + 0.008
    readout_h = 0.072
    readout_box = FancyBboxPatch((panel_x0 + 0.015, readout_y0), panel_w - 0.030, readout_h,
                                 boxstyle="round,pad=0.002,rounding_size=0.006",
                                 facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.2)
    ax.add_patch(readout_box)

    flat = 1.0 - (R_VAL / Req_active)
    surf_label = f"Oblate spheroid ($a = {a_val:.2f}m$)" if a_val >= 0.02 else "Spherical surface ($a = 0$)"

    line1 = (f"Parameters:  $t = \\mathrm{{const}},\\; r = 1.00m$      |      "
             f"Rotation:  $a = {a_val:.2f}m$  ($a/m = {a_val/M_VAL:.2f}$)      |      "
             f"Current surface:  {surf_label}")
    line2 = (f"Polar semiaxis:  $R_{{\\mathrm{{polar}}}} = r = 1.00m$ (constant)      |      "
             f"Equatorial semiaxis:  $R_{{\\mathrm{{eq}}}} = \\sqrt{{r^2 + a^2}} = {Req_active:.2f}m$ (+{expansion_pct:.1f}%)      |      "
             f"Oblateness:  {flat*100:.1f}%")

    ax.text(panel_x0 + panel_w * 0.50, readout_y0 + 0.046, line1,
            fontsize=12.0, fontweight='bold', color=NAVY, ha='center', va='center')
    ax.text(panel_x0 + panel_w * 0.50, readout_y0 + 0.018, line2,
            fontsize=12.0, fontweight='bold', color='#1e40af', ha='center', va='center')

    if output_path:
        fig.savefig(output_path, dpi=140, facecolor='#ffffff', edgecolor='none')
        plt.close(fig)
    else:
        return fig


def render_frame_worker(args):
    """Worker task for multiprocessing animation frame generation."""
    frame_idx, a_val, frame_path = args
    render_scene(a_val, is_static=False, output_path=frame_path)


def generate_all():
    """Generate static PNG, animated GIF, and MP4 video."""
    t0 = time.time()
    print("=== Generating Boyer–Lindquist Coordinates: Spherical to Oblate Spheroid ===")

    # 1. Generate Static Figure (shows maximum deformation state at a = 0.80m)
    print("1. Rendering static publication figure (a = 0.80m)...")
    render_scene(a_val=A_MAX, is_static=True, output_path=PNG_OUT)
    print(f"[OK] Generated static PNG: {PNG_OUT}")

    # 2. Prepare Animation Frames (160 frames, 8.0 s @ 20 fps)
    print(f"2. Generating {N_FRAMES} animation frames ({FPS} fps, {DURATION_SEC:.1f} s)...")
    frames_dir = Path(tempfile.mkdtemp(prefix="bl_single_frames_"))

    # Trajectory for a(t):
    # - Phase 1: Frames 0..19 (1.0 s): hold at a = 0.0 (sphere)
    # - Phase 2: Frames 20..79 (3.0 s, 60 frames): smooth cosine increase from a = 0.0 to a = 0.80m
    # - Phase 3: Frames 80..99 (1.0 s, 20 frames): hold at a = 0.80m (maximum oblate spheroid)
    # - Phase 4: Frames 100..159 (3.0 s, 60 frames): smooth cosine decrease from a = 0.80m back to a = 0.0
    a_traj = np.zeros(N_FRAMES)
    for f in range(N_FRAMES):
        if f < 20:
            a_traj[f] = 0.0
        elif f < 80:
            tau = (f - 20) / 59.0
            s = 0.5 * (1.0 - np.cos(np.pi * tau))
            a_traj[f] = A_MAX * s
        elif f < 100:
            a_traj[f] = A_MAX
        else:
            tau = (f - 100) / 59.0
            s = 0.5 * (1.0 - np.cos(np.pi * tau))
            a_traj[f] = A_MAX * (1.0 - s)

    tasks = [(i, a_traj[i], str(frames_dir / f"frame_{i:04d}.png")) for i in range(N_FRAMES)]

    n_workers = max(1, multiprocessing.cpu_count() - 1)
    with multiprocessing.Pool(processes=n_workers) as pool:
        pool.map(render_frame_worker, tasks)

    dt_frames = time.time() - t0
    print(f"[OK] Rendered {N_FRAMES} frames in {dt_frames:.1f} s ({dt_frames/N_FRAMES:.3f} s/frame)")

    # 3. Encode High-Resolution GIF
    print("3. Encoding animated GIF with split-palette dithering...")
    cmd_gif = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-vf", f"fps={FPS},scale=1800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=224:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4",
        "-loop", "0",
        str(GIF_OUT),
    ]
    subprocess.run(cmd_gif, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    gif_mb = GIF_OUT.stat().st_size / (1024 * 1024)
    print(f"[OK] Generated GIF: {GIF_OUT} ({gif_mb:.2f} MB)")

    # 4. Encode MP4 Video
    print("4. Encoding MP4 video...")
    cmd_mp4 = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-c:v", "libx264",
        "-profile:v", "high",
        "-crf", "18",
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        str(MP4_OUT),
    ]
    subprocess.run(cmd_mp4, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    mp4_mb = MP4_OUT.stat().st_size / (1024 * 1024)
    print(f"[OK] Generated MP4: {MP4_OUT} ({mp4_mb:.2f} MB)")

    # Clean up temporary frames
    shutil.rmtree(frames_dir, ignore_errors=True)
    total_time = time.time() - t0
    print(f"=== Completed in {total_time:.1f} s ===")


if __name__ == "__main__":
    generate_all()
