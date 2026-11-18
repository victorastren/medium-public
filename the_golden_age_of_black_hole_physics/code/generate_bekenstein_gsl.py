#!/usr/bin/env python3
r"""
Generate animated & static scientific illustration:
"Bekenstein's Generalized Second Law"

Figure for Section "Bekenstein and Black-Hole Entropy" of:
"The Golden Age of Black Hole Physics (1963-1974)"

Design & Scientific Specifications:
- Format: Looping GIF (1200 px width) + MP4 + static final-state PNG (1800 x 900 px)
- Resolution & DPI: 1800 x 900 px at 140 DPI (12.857 x 6.429 in), matching
  generate_penrose_process.py pixel-for-pixel in typography and layout.
- Duration: 10.0 seconds at 20 fps (200 frames)
- Panel A (Left): "A · Matter crossing the event horizon"
  - Simple spherical black hole (dark-navy shaded disk) with blue event horizon
  - Incoming box carrying matter and entropy ("Box with matter and entropy")
  - Box approaches, crosses the event horizon, and disappears from the outside
    region while the horizon grows slightly (schematic thought experiment)
- Panel B (Right): "B · Entropy balance"
  - Staged entropy accounting matching the Penrose-process Panel B cards:
    1. Before crossing: S_gen = S_outside + S_BH
    2. During infall: outside entropy decreases (Delta S_outside < 0) while
       black-hole entropy increases (Delta S_BH > 0)
    3. Final law: Delta S_outside + Delta S_BH >= 0 (Generalized second law)
"""

import multiprocessing
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np

# =============================================================================
# Output Paths & Animation Configuration (matching generate_penrose_process.py)
# =============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
IMAGES_DIR = SCRIPT_DIR.parent / "images"
STATIC_OUT = IMAGES_DIR / "bekenstein_gsl.png"
MP4_OUT = IMAGES_DIR / "bekenstein_gsl_animation.mp4"
GIF_OUT = IMAGES_DIR / "bekenstein_gsl_animation.gif"

CANVAS_W = 1800
CANVAS_H = 900
DPI = 140
FPS = 20
N_FRAMES = 200  # 10.0 seconds @ 20 fps

# Palette (unified light scientific style matching generate_penrose_process.py)
BG_WHITE = '#ffffff'
PANEL_BG = '#f5f7fa'
CARD_BG = '#f8fafc'
BORDER_COLOR = '#cbd5e1'
GUIDE_COLOR = '#94a3b8'

NAVY = '#172136'
DARK_SLATE = '#1e293b'
SLATE = '#334155'
MUTED_SLATE = '#475569'

BLUE_MAIN = '#1d4ed8'
BLUE_DARK = '#1e3a8a'
BLUE_MID = '#3b82f6'
BLUE_BG = '#eff6ff'
BLUE_BORDER = '#93c5fd'

ORANGE_MAIN = '#d97706'
ORANGE_DARK = '#b45309'
ORANGE_BG = '#fffbeb'
ORANGE_BORDER = '#fcd34d'

TURQ_MAIN = '#0d9488'
TURQ_DARK = '#0f766e'
TURQ_BG = '#f0fdfa'
TURQ_BORDER = '#5eead4'

plt.rcParams.update({
    'text.usetex': False,
    'mathtext.fontset': 'dejavuserif',
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'axes.edgecolor': BORDER_COLOR,
    'axes.linewidth': 1.2,
})


def make_bh_RGBA(size=360):
    """Precompute a softly shaded dark 2D spherical black-hole RGBA disk."""
    y, x = np.ogrid[-1:1:size * 1j, -1:1:size * 1j]
    r2 = x**2 + y**2
    mask = r2 <= 1.0
    img = np.zeros((size, size, 4), dtype=float)
    z = np.sqrt(np.maximum(0.0, 1.0 - r2))
    lx, ly, lz = -0.35, 0.35, 0.87
    dot = np.maximum(0.0, x * lx + y * ly + z * lz) * mask
    base_r, base_g, base_b = 15 / 255, 23 / 255, 42 / 255
    hi_r, hi_g, hi_b = 52 / 255, 74 / 255, 114 / 255
    img[..., 0] = base_r + (hi_r - base_r) * (dot**1.6) * 0.72
    img[..., 1] = base_g + (hi_g - base_g) * (dot**1.6) * 0.72
    img[..., 2] = base_b + (hi_b - base_b) * (dot**1.6) * 0.72
    dist = np.sqrt(r2)
    alpha = np.clip((1.0 - dist) * (size / 3.0), 0.0, 1.0)
    img[..., 3] = alpha
    return img


BH_IMG = make_bh_RGBA(360)


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return 3.0 * t**2 - 2.0 * t**3


def compute_frame_state(frame_idx, is_static=False):
    """
    Map frame index [0, 199] to animation state:
      0.0 - 1.5 s (frames 0..29):     Initial hold (box outside, Stage 1)
      1.5 - 4.5 s (frames 30..89):    Box moves inward toward horizon
      4.5 - 6.0 s (frames 90..119):   Box crosses horizon, disappears, horizon grows (Stage 2)
      6.0 - 10.0 s (frames 120..199): Final law hold (Stage 3)
    """
    if is_static:
        t_sec = 8.5
    else:
        t_sec = frame_idx / float(FPS)

    # Box center x-coordinate in Panel A (BH centered at x = -1.42, r_init = 1.85)
    x_start = 2.72
    x_horizon_edge = -1.42 + 1.85  # 0.43
    x_inside = -0.60

    if t_sec < 1.5:
        box_x = x_start
        box_alpha = 1.0
        grow_frac = 0.0
        stage = 1
    elif t_sec < 4.5:
        u = smoothstep((t_sec - 1.5) / 3.0)
        box_x = x_start + u * (x_horizon_edge + 0.65 - x_start)
        box_alpha = 1.0
        grow_frac = 0.0
        stage = 2 if t_sec >= 2.7 else 1
    elif t_sec < 6.0:
        u = smoothstep((t_sec - 4.5) / 1.5)
        box_x = (x_horizon_edge + 0.65) + u * (x_inside - (x_horizon_edge + 0.65))
        box_alpha = float(np.clip(1.0 - smoothstep((u - 0.15) / 0.65), 0.0, 1.0))
        grow_frac = float(smoothstep((u - 0.20) / 0.75))
        stage = 2
    else:
        box_x = x_inside
        box_alpha = 0.0
        grow_frac = 1.0
        stage = 3

    return {
        't_sec': t_sec,
        'box_x': box_x,
        'box_alpha': box_alpha,
        'grow_frac': grow_frac,
        'stage': stage,
    }


def draw_frame(frame_idx, output_path, is_static=False):
    state = compute_frame_state(frame_idx, is_static=is_static)
    t_sec = state['t_sec']
    box_x = state['box_x']
    box_alpha = state['box_alpha']
    grow_frac = state['grow_frac']
    stage = state['stage']

    fig = plt.figure(figsize=(CANVAS_W / DPI, CANVAS_H / DPI), dpi=DPI, facecolor=BG_WHITE)
    ax_root = fig.add_axes([0, 0, 1, 1], facecolor=BG_WHITE)
    ax_root.set_xlim(0, 1)
    ax_root.set_ylim(0, 1)
    ax_root.axis('off')

    # =========================================================================
    # 1. TOP HEADER BANNER (identical to generate_penrose_process.py)
    # =========================================================================
    title_box = FancyBboxPatch(
        (0.020, 0.876), 0.960, 0.104,
        boxstyle="round,pad=0.002,rounding_size=0.008",
        facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.4,
    )
    ax_root.add_patch(title_box)
    ax_root.text(
        0.50, 0.948, "BEKENSTEIN'S GENERALIZED SECOND LAW",
        color=NAVY, fontsize=17.8, fontweight='bold', ha='center', va='center',
    )
    ax_root.text(
        0.50, 0.898,
        "Entropy accounting as matter crosses a black hole's event horizon",
        color=SLATE, fontsize=13.2, fontweight='bold', ha='center', va='center',
    )

    # =========================================================================
    # 2. TWO EQUAL PANEL SUBPLOTS (identical coordinates to generate_penrose_process.py)
    # =========================================================================
    p_w = 0.472
    p_h = 0.835
    p_y = 0.020

    ax_a = fig.add_axes([0.020, p_y, p_w, p_h])
    ax_b = fig.add_axes([0.508, p_y, p_w, p_h])

    for p_ax, p_letter, p_title, p_sub, is_right in [
        (ax_a, "A", "Matter crossing the event horizon",
         "Schematic thought experiment (spherical black hole)", False),
        (ax_b, "B", "Entropy balance",
         "Staged entropy accounting before and after infall", True),
    ]:
        p_ax.set_xlim(-4.9, 4.9)
        p_ax.set_ylim(-4.3, 4.3)
        p_ax.set_aspect('equal')
        p_ax.axis('off')

        card = FancyBboxPatch(
            (-4.75, -4.15), 9.5, 8.3,
            boxstyle="round,pad=0.02,rounding_size=0.15",
            facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=0,
        )
        p_ax.add_patch(card)

        viewport = FancyBboxPatch(
            (-4.52, -3.95), 9.04, 6.95,
            boxstyle="round,pad=0.02,rounding_size=0.10",
            facecolor=BG_WHITE, edgecolor='#e2e8f0', linewidth=1.0, zorder=0.5,
        )
        p_ax.add_patch(viewport)

        hdr_box = FancyBboxPatch(
            (-4.52, 3.15), 9.04, 0.96,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=BG_WHITE if not is_right else ORANGE_BG,
            edgecolor=BORDER_COLOR if not is_right else ORANGE_BORDER,
            linewidth=1.2, zorder=1,
        )
        p_ax.add_patch(hdr_box)

        p_ax.text(
            0.0, 3.84, f"{p_letter}  ·  {p_title}",
            color=NAVY if not is_right else ORANGE_DARK,
            fontsize=14.8, fontweight='bold', ha='center', va='center', zorder=2,
        )
        p_ax.text(
            0.0, 3.38, p_sub,
            color=SLATE if not is_right else DARK_SLATE,
            fontsize=11.6, fontweight='bold', ha='center', va='center', zorder=2,
        )

    # =========================================================================
    # 3. PANEL A — MATTER CROSSING THE EVENT HORIZON
    # =========================================================================
    # Outside region label (top-right inside viewport)
    ax_a.text(
        2.35, 2.40, "Outside region\n" + r"($S_{\mathrm{outside}}$)",
        color=SLATE, fontsize=12.6, fontweight='bold', ha='center', va='center',
        linespacing=1.25, zorder=6,
    )

    # Spherical Black Hole (grows subtly when box crosses horizon)
    bh_cx, bh_cy = -1.42, -0.52
    r_bh_init = 1.85
    r_bh_curr = r_bh_init + 0.38 * grow_frac

    ax_a.imshow(
        BH_IMG,
        extent=[bh_cx - r_bh_curr, bh_cx + r_bh_curr, bh_cy - r_bh_curr, bh_cy + r_bh_curr],
        origin='lower',
        zorder=4,
    )

    # Initial horizon dashed reference once horizon grows
    if grow_frac > 0.05:
        init_ring = Circle(
            (bh_cx, bh_cy), r_bh_init,
            facecolor='none', edgecolor='#93c5fd', linestyle='--', linewidth=1.7,
            alpha=0.80 * grow_frac, zorder=4.5,
        )
        ax_a.add_patch(init_ring)

    # Current Event Horizon circle
    eh_ring = Circle(
        (bh_cx, bh_cy), r_bh_curr,
        facecolor='none', edgecolor=BLUE_MAIN if grow_frac < 0.5 else TURQ_MAIN,
        linewidth=3.0, zorder=5,
    )
    ax_a.add_patch(eh_ring)

    # Black-hole interior entropy label
    if grow_frac < 0.45:
        bh_label = r"$S_{\mathrm{BH}}$"
        bh_col = '#f8fafc'
        bh_fs = 15.2
    else:
        bh_label = r"$S_{\mathrm{BH}}$ increases" + "\n(horizon grows)"
        bh_col = '#99f6e4'
        bh_fs = 12.6
    ax_a.text(
        bh_cx, bh_cy, bh_label,
        color=bh_col, fontsize=bh_fs,
        fontweight='bold', ha='center', va='center', linespacing=1.25, zorder=7,
    )

    # Event horizon callout label
    ax_a.annotate(
        "Event horizon",
        xy=(bh_cx + r_bh_curr * np.cos(np.deg2rad(-54)),
            bh_cy + r_bh_curr * np.sin(np.deg2rad(-54))),
        xytext=(1.15, -3.28),
        color=BLUE_DARK, fontsize=12.2, fontweight='bold', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=BLUE_BG, edgecolor=BLUE_MAIN, lw=1.3),
        arrowprops=dict(arrowstyle='-|>,head_length=0.45,head_width=0.24',
                        color=BLUE_MAIN, lw=1.8, connectionstyle='arc3,rad=-0.12'),
        zorder=9,
    )

    # Incoming Box with matter and entropy
    if box_alpha > 0.01:
        bw, bh_box = 1.52, 1.12
        box_y = bh_cy
        matter_box = FancyBboxPatch(
            (box_x - bw / 2, box_y - bh_box / 2), bw, bh_box,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor=ORANGE_BG, edgecolor=ORANGE_MAIN, linewidth=2.4,
            alpha=box_alpha, zorder=6,
        )
        ax_a.add_patch(matter_box)

        # Schematic matter particles inside the box
        pts_dx = [-0.38, 0.06, 0.40, -0.20, 0.30]
        pts_dy = [0.24, 0.28, -0.06, -0.26, -0.28]
        ax_a.scatter(
            [box_x + dx for dx in pts_dx],
            [box_y + dy for dy in pts_dy],
            color=ORANGE_DARK, s=42, alpha=box_alpha, zorder=6.5,
        )

        # Box label above
        ax_a.text(
            box_x, box_y + 0.98,
            "Box with matter\nand entropy",
            color=ORANGE_DARK, fontsize=12.0, fontweight='bold',
            ha='center', va='bottom', linespacing=1.2, alpha=box_alpha,
            bbox=dict(boxstyle='round,pad=0.28', facecolor=ORANGE_BG,
                      edgecolor=ORANGE_BORDER, lw=1.2, alpha=box_alpha),
            zorder=8,
        )

        # Inward motion arrow
        if t_sec < 5.5:
            ax_a.annotate(
                '',
                xy=(box_x - bw / 2 - 0.96, box_y),
                xytext=(box_x - bw / 2 - 0.18, box_y),
                arrowprops=dict(arrowstyle='-|>,head_length=0.50,head_width=0.28',
                                color=ORANGE_MAIN, lw=2.6, alpha=box_alpha),
                zorder=7,
            )
            ax_a.text(
                box_x - bw / 2 - 0.57, box_y - 0.52,
                "Falls in",
                color=ORANGE_DARK, fontsize=11.6, fontweight='bold',
                ha='center', va='top', alpha=box_alpha, zorder=7,
            )
    else:
        # After crossing: clear summary note in the outside region
        ax_a.text(
            2.42, -0.52,
            "Box has crossed\nthe event horizon\n\n" + r"($\Delta S_{\mathrm{outside}} < 0$)",
            color=DARK_SLATE, fontsize=12.2, fontweight='bold',
            ha='center', va='center', linespacing=1.28,
            bbox=dict(boxstyle='round,pad=0.36', facecolor=PANEL_BG,
                      edgecolor=BORDER_COLOR, lw=1.3),
            zorder=7,
        )

    # =========================================================================
    # 4. PANEL B — STAGED ENTROPY BALANCE (matching Penrose Panel B hierarchy)
    # =========================================================================
    stages_meta = [
        (1, "1 · Before crossing",
         BLUE_MAIN, BLUE_DARK, BLUE_BG, BLUE_BORDER,
         r"Outside: $S_{\mathrm{outside}}$    |    Black hole: $S_{\mathrm{BH}}$",
         r"$S_{\mathrm{gen}} = S_{\mathrm{outside}} + S_{\mathrm{BH}}$",
         12.8, 14.2, 1.88, 2.75),

        (2, "2 · Horizon crossing",
         ORANGE_MAIN, ORANGE_DARK, ORANGE_BG, ORANGE_BORDER,
         r"$\downarrow$  Outside entropy decreases:   $\Delta S_{\mathrm{outside}} < 0$",
         r"$\uparrow$  Black-hole entropy increases:   $\Delta S_{\mathrm{BH}} > 0$",
         12.8, 12.8, 1.92, 0.62),

        (3, "3 · Final law  (Generalized second law)",
         NAVY, NAVY, TURQ_BG, TURQ_MAIN,
         "Generalized entropy does not decrease:",
         r"$\Delta S_{\mathrm{outside}} + \Delta S_{\mathrm{BH}} \geq 0$",
         12.8, 15.6, 2.15, -1.55),
    ]

    for st_num, st_title, c_main, c_dark, c_bg, c_bdr, line1, line2, fs1, fs2, card_h, y_top in stages_meta:
        is_active = (stage == st_num) and not is_static
        is_reached = (stage >= st_num) or is_static

        face = c_bg if is_reached else '#f8fafc'
        edge = c_main if (is_active or (is_static and st_num == 3)) else (c_bdr if is_reached else '#e2e8f0')
        lw_c = 2.6 if (is_active or (st_num == 3 and is_reached)) else (1.5 if is_reached else 1.0)
        alpha_txt = 1.0 if is_reached else 0.36

        st_box = FancyBboxPatch(
            (-4.28, y_top - card_h), 8.56, card_h,
            boxstyle="round,pad=0.02,rounding_size=0.10",
            facecolor=face, edgecolor=edge, linewidth=lw_c, zorder=2.0,
        )
        ax_b.add_patch(st_box)

        bar_w = 0.24 if st_num == 3 else 0.20
        bar_col = TURQ_MAIN if (st_num == 3 and is_reached) else (c_main if is_reached else '#cbd5e1')
        bar = FancyBboxPatch(
            (-4.28, y_top - card_h), bar_w, card_h,
            boxstyle="round,pad=0.0,rounding_size=0.04",
            facecolor=bar_col, edgecolor='none', zorder=2.5,
        )
        ax_b.add_patch(bar)

        ax_b.text(
            -3.78, y_top - 0.36, st_title,
            color=(TURQ_DARK if st_num == 3 else c_dark) if is_reached else '#94a3b8',
            fontsize=14.6 if st_num == 3 else 14.2,
            fontweight='bold', ha='left', va='center', alpha=alpha_txt, zorder=3.0,
        )

        if st_num == 3:
            ax_b.text(
                -3.78, y_top - 0.88, line1,
                color=DARK_SLATE, fontsize=fs1,
                ha='left', va='center', alpha=alpha_txt, zorder=3.0,
            )
            ax_b.text(
                -3.78, y_top - 1.56, line2,
                color=NAVY, fontsize=fs2, fontweight='bold',
                ha='left', va='center', alpha=alpha_txt,
                bbox=dict(boxstyle='round,pad=0.30', facecolor=BG_WHITE,
                          edgecolor=NAVY, linewidth=1.5),
                zorder=3.0,
            )
        elif st_num == 2:
            ax_b.text(
                -3.78, y_top - 0.92, line1,
                color=ORANGE_DARK if is_reached else DARK_SLATE,
                fontsize=fs1, fontweight='bold', ha='left', va='center',
                alpha=alpha_txt, zorder=3.0,
            )
            ax_b.text(
                -3.78, y_top - 1.46, line2,
                color=TURQ_DARK if is_reached else DARK_SLATE,
                fontsize=fs2, fontweight='bold', ha='left', va='center',
                alpha=alpha_txt, zorder=3.0,
            )
        else:
            ax_b.text(
                -3.78, y_top - 0.90, line1,
                color=DARK_SLATE, fontsize=fs1,
                ha='left', va='center', alpha=alpha_txt, zorder=3.0,
            )
            ax_b.text(
                -3.78, y_top - 1.44, line2,
                color=NAVY, fontsize=fs2, fontweight='bold',
                ha='left', va='center', alpha=alpha_txt, zorder=3.0,
            )

    fig.savefig(output_path, dpi=DPI, facecolor=BG_WHITE)
    plt.close(fig)


def render_worker(args):
    frame_idx, out_path = args
    draw_frame(frame_idx, out_path, is_static=False)


def generate_assets():
    t0 = time.time()
    print("=== Generating Bekenstein Generalized Second Law Animation & Static Figure ===")
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    print("1. Rendering static publication figure...")
    draw_frame(N_FRAMES - 1, STATIC_OUT, is_static=True)
    print(f"[OK] Static figure: {STATIC_OUT} ({STATIC_OUT.stat().st_size / 1024:.1f} KB)")

    frames_dir = Path(tempfile.mkdtemp(prefix="bekenstein_gsl_frames_"))
    print(f"2. Rendering {N_FRAMES} animation frames in {frames_dir}...")
    tasks = [(idx, str(frames_dir / f"frame_{idx:04d}.png")) for idx in range(N_FRAMES)]
    n_workers = max(1, multiprocessing.cpu_count() - 1)
    with multiprocessing.Pool(processes=n_workers) as pool:
        pool.map(render_worker, tasks)

    print(f"[OK] Rendered {N_FRAMES} frames in {time.time() - t0:.1f} s")

    print("3. Encoding MP4 video...")
    cmd_mp4 = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-c:v", "libx264",
        "-profile:v", "high",
        "-crf", "18",
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        str(MP4_OUT),
    ]
    res_mp4 = subprocess.run(cmd_mp4, capture_output=True, text=True)
    if res_mp4.returncode != 0:
        raise RuntimeError(f"FFmpeg MP4 encoding failed:\n{res_mp4.stderr}")
    print(f"[OK] Generated MP4: {MP4_OUT} ({MP4_OUT.stat().st_size / (1024 * 1024):.2f} MB)")

    print("4. Encoding animated GIF (1200 px width, Lanczos + palettegen)...")
    cmd_gif = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-vf", f"fps={FPS},scale=1200:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=224:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4",
        "-loop", "0",
        str(GIF_OUT),
    ]
    res_gif = subprocess.run(cmd_gif, capture_output=True, text=True)
    if res_gif.returncode != 0:
        raise RuntimeError(f"FFmpeg GIF encoding failed:\n{res_gif.stderr}")
    print(f"[OK] Generated GIF: {GIF_OUT} ({GIF_OUT.stat().st_size / (1024 * 1024):.2f} MB)")

    shutil.rmtree(frames_dir, ignore_errors=True)
    print(f"=== Complete in {time.time() - t0:.1f} s ===")


if __name__ == "__main__":
    generate_assets()
