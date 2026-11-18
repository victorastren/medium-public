#!/usr/bin/env python3
r"""
Generate two-panel static scientific illustration:
"Black-Hole Perturbations and Quasinormal Ringdown"

Figure for Section "Black-Hole Perturbations: From Vishveshwara to Teukolsky" of:
"The Golden Age of Black Hole Physics (1963–1974)"

Design & Scientific Specifications:
- Format: Static, two-panel scientific illustration
- Resolution: 1800 x 900 px at 140 DPI (12.857 x 6.429 in, 2:1 aspect ratio)
- Panel proportions: Left 45% (Panel A), Right 55% (Panel B)
- Typography & font size hierarchy matching existing figures:
  - 17.8 pt bold main title (dark navy #0f172a)
  - 13.5 pt bold subtitle (slate #475569)
  - 15.5 pt bold panel headers ("A · Perturbed Kerr spacetime", "B · Quasinormal ringdown")
  - 11.5-12.2 pt bold panel subtitles
  - 14.2 pt bold axis titles
  - 12.6-13.2 pt bold tick labels and callout annotations (optimized for 680-800 px Medium column width)
- Panel A (Left, 45%): "A · Perturbed Kerr spacetime"
  - Schematic curvature disturbance and outgoing radiation around a rotating Kerr black hole (a/m = 0.8)
  - Central dark silhouette (undistorted event horizon) with clearly marked rotation axis and spin direction
  - Exterior gravitational perturbation: weak quadrupolar-shaped deep-blue contours outside the horizon
  - Outgoing gravitational waves: curved wavefronts propagating outward with outward arrow
  - Horizon absorption: small inward arrow crossing the event horizon
  - Labels inside Panel A:
    1. "Spin axis"
    2. "Gravitational perturbation"
    3. "Event horizon"
    4. "Outgoing gravitational waves"
- Panel B (Right, 55%): "B · Quasinormal ringdown"
  - Fundamental gravitational quasinormal mode (\ell, m_\phi, n) = (2, 2, 0) for a/m = 0.8
  - Berti, Cardoso & Will (2006) complex frequency:
      m \omega / c \simeq 0.5855 - 0.0757 i
  - Normalized strain waveform:
      h(t) / h_0 = \exp(-0.0757 \hat{t}) \cos(0.5855 \hat{t}),   \hat{t} = c t / m \in [0, 60]
  - Envelopes: \pm \exp(-0.0757 \hat{t}) (dashed orange) with explicit 1/e marker at \hat{t} = \tau
  - Oscillation period: T = 2\pi / 0.5855 \approx 10.73 m/c
  - Amplitude decay time: \tau = 1 / 0.0757 \approx 13.21 m/c
"""

from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Arc
import numpy as np
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "black_hole_perturbations_ringdown.png"

# Physical parameters for Kerr fundamental (l=2, m=2, n=0) mode at a/m = 0.8
A_SPIN = 0.8
OMEGA_R = 0.5855          # Real part of m * omega / c
OMEGA_I = -0.0757         # Imaginary part of m * omega / c
GAMMA_DECAY = 0.0757      # Damping rate |Im(m * omega / c)|
T_PERIOD = 2.0 * np.pi / OMEGA_R   # ~ 10.7313 m/c
TAU_DECAY = 1.0 / GAMMA_DECAY      # ~ 13.2100 m/c


def compute_ringdown_waveform(t_hat_max=60.0, n_pts=1500):
    """
    Compute the normalized quasinormal-mode ringdown waveform and envelopes
    for the fundamental (l=2, m_phi=2, n=0) Kerr mode at a/m = 0.8.
    """
    t_hat = np.linspace(0.0, t_hat_max, n_pts)
    env_upper = np.exp(-GAMMA_DECAY * t_hat)
    env_lower = -env_upper
    strain = env_upper * np.cos(OMEGA_R * t_hat)
    return t_hat, strain, env_upper, env_lower


def make_bh_RGBA(size=360):
    """Precompute a softly shaded dark 2D RGBA image on the unit disk, stretched by imshow extent."""
    y, x = np.ogrid[-1:1:size*1j, -1:1:size*1j]
    r2 = x**2 + y**2
    mask = r2 <= 1.0
    img = np.zeros((size, size, 4), dtype=float)
    z = np.sqrt(np.maximum(0.0, 1.0 - r2))
    lx, ly, lz = -0.35, 0.35, 0.87
    dot = np.maximum(0.0, x * lx + y * ly + z * lz) * mask
    base_r, base_g, base_b = 15/255, 23/255, 42/255
    hi_r, hi_g, hi_b = 48/255, 68/255, 104/255
    img[..., 0] = base_r + (hi_r - base_r) * (dot**1.6) * 0.70
    img[..., 1] = base_g + (hi_g - base_g) * (dot**1.6) * 0.70
    img[..., 2] = base_b + (hi_b - base_b) * (dot**1.6) * 0.70
    dist = np.sqrt(r2)
    alpha = np.clip((1.0 - dist) * (size / 3.0), 0.0, 1.0)
    img[..., 3] = alpha
    return img


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Typography and font hierarchy matching the rest of the article
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 13.5,
    })

    # Canvas: 1800 x 900 px at 140 DPI (exact 2:1 landscape)
    dpi = 140
    fig_w, fig_h = 1800.0 / dpi, 900.0 / dpi
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Master background axes
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Unified Editorial Palette
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#475569'
    AXIS_COLOR = '#334155'
    BORDER_COLOR = '#cbd5e1'
    PANEL_BG = '#f8fafc'
    BG_WHITE = '#ffffff'

    BLUE_MAIN = '#1d4ed8'
    BLUE_DARK = '#1e3a8a'
    BLUE_MID = '#3b82f6'
    BLUE_LIGHT = '#93c5fd'
    BLUE_BG = '#eff6ff'
    BLUE_BORDER = '#bfdbfe'

    ORANGE_MAIN = '#d97706'
    ORANGE_DARK = '#b45309'
    ORANGE_BG = '#fffbeb'
    ORANGE_BORDER = '#fcd34d'

    # =========================================================================
    # 1. TOP HEADER BANNER
    # =========================================================================
    title_box = FancyBboxPatch((0.020, 0.876), 0.960, 0.104,
                               boxstyle="round,pad=0.002,rounding_size=0.008",
                               facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax.add_patch(title_box)
    ax.text(0.50, 0.948, "BLACK-HOLE PERTURBATIONS AND QUASINORMAL RINGDOWN",
            color=NAVY, fontsize=17.8, fontweight='bold', ha='center', va='center')
    ax.text(0.50, 0.898,
            r"Spacetime curvature disturbances and the fundamental gravitational mode of a rotating Kerr black hole ($a/m = 0.8$)",
            color=SLATE, fontsize=13.5, fontweight='bold', ha='center', va='center')

    # =========================================================================
    # 2. TWO PANEL CARDS (Left 45%, Right 55%)
    # Total width = 0.960, gap = 0.016 -> usable width = 0.944
    # Left width = 0.45 * 0.944 = 0.425 (x: 0.020 to 0.445)
    # Right width = 0.55 * 0.944 = 0.519 (x: 0.461 to 0.980)
    # =========================================================================
    p_y = 0.020
    p_h = 0.835
    left_x, left_w = 0.020, 0.425
    right_x, right_w = 0.461, 0.519

    for px, pw, p_title, p_sub, is_right in [
        (left_x, left_w, "A  ·  Perturbed Kerr spacetime",
         "Schematic curvature disturbance and outgoing radiation", False),
        (right_x, right_w, "B  ·  Quasinormal ringdown",
         "Calculated damped mode with decreasing amplitude", True),
    ]:
        # Outer panel card
        card = FancyBboxPatch((px, p_y), pw, p_h,
                              boxstyle="round,pad=0.002,rounding_size=0.008",
                              facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=1)
        ax.add_patch(card)

        # Inner white viewport card
        pad_x = 0.009
        pad_y = 0.012
        vp_h = p_h - 0.122
        viewport = FancyBboxPatch((px + pad_x, p_y + pad_y), pw - 2 * pad_x, vp_h,
                                  boxstyle="round,pad=0.002,rounding_size=0.006",
                                  facecolor=BG_WHITE, edgecolor='#e2e8f0', linewidth=1.0, zorder=1.5)
        ax.add_patch(viewport)

        # Panel Header Box inside card
        hdr_h = 0.092
        hdr_y = p_y + p_h - hdr_h - 0.012
        hdr_box = FancyBboxPatch((px + pad_x, hdr_y), pw - 2 * pad_x, hdr_h,
                                 boxstyle="round,pad=0.002,rounding_size=0.006",
                                 facecolor=BG_WHITE if not is_right else ORANGE_BG,
                                 edgecolor=BORDER_COLOR if not is_right else ORANGE_BORDER,
                                 linewidth=1.2, zorder=2)
        ax.add_patch(hdr_box)

        ax.text(px + 0.5 * pw, hdr_y + 0.66 * hdr_h, p_title,
                color=NAVY if not is_right else ORANGE_DARK,
                fontsize=15.5, fontweight='bold', ha='center', va='center', zorder=3)
        ax.text(px + 0.5 * pw, hdr_y + 0.25 * hdr_h, p_sub,
                color=SLATE if not is_right else DARK_SLATE,
                fontsize=11.5 if not is_right else 12.2, fontweight='bold', ha='center', va='center', zorder=3)

    # =========================================================================
    # 3. PANEL A — PERTURBED KERR SPACETIME (SCHEMATIC)
    # =========================================================================
    ax_a = fig.add_axes([left_x + 0.009, p_y + 0.012, left_w - 0.018, p_h - 0.122], zorder=3)
    ax_a.set_xlim(-4.55, 4.55)
    ax_a.set_ylim(-4.00, 4.00)
    ax_a.set_aspect('equal')
    ax_a.axis('off')

    # Center of black hole slightly right of center for balanced callout placement
    bh_cx, bh_cy = 0.05, -0.05
    # Horizon semiaxes for a/m = 0.8 (r_+ = 1.6m, equatorial sqrt(1.6^2 + 0.8^2) = 1.789m, ratio = 1.118)
    r_pol = 0.84
    r_eq = r_pol * 1.118

    # 3a. Rotation / spin axis (vertical dashed line + top arrow + spin arc)
    ax_a.plot([bh_cx, bh_cx], [bh_cy - 2.85, bh_cy - r_pol],
              color=AXIS_COLOR, lw=1.7, ls='--', alpha=0.70, zorder=2)
    ax_a.plot([bh_cx, bh_cx], [bh_cy + r_pol, bh_cy + 2.55],
              color=AXIS_COLOR, lw=2.0, ls='--', alpha=0.85, zorder=2)
    ax_a.annotate('', xy=(bh_cx, bh_cy + 2.98), xytext=(bh_cx, bh_cy + 2.45),
                  arrowprops=dict(arrowstyle='-|>,head_length=0.52,head_width=0.30',
                                  color=NAVY, lw=2.2), zorder=10)
    # Curved azimuthal spin arrow around rotation axis at top
    spin_arc = Arc((bh_cx, bh_cy + 2.48), 0.76, 0.23, angle=0, theta1=195, theta2=345,
                   color=ORANGE_MAIN, lw=2.1, zorder=11)
    ax_a.add_patch(spin_arc)
    ax_a.annotate('', xy=(bh_cx + 0.37, bh_cy + 2.45), xytext=(bh_cx + 0.23, bh_cy + 2.39),
                  arrowprops=dict(arrowstyle='-|>,head_length=0.38,head_width=0.23',
                                  color=ORANGE_MAIN, lw=1.9), zorder=11)

    # 3b. Near-zone gravitational perturbation: quadrupolar-shaped contours outside the horizon
    theta_c = np.linspace(0, 2 * np.pi, 360)

    # Soft shaded perturbation halo between r = 1.18 and r = 2.02
    r_inner_halo = 1.18 * (1.0 + 0.08 * np.cos(2.0 * (theta_c - 0.35)))
    r_outer_halo = 2.02 * (1.0 + 0.13 * np.cos(2.0 * (theta_c - 0.55)) + 0.03 * np.sin(3.0 * theta_c))
    x_in_h = bh_cx + r_inner_halo * r_eq * np.cos(theta_c)
    y_in_h = bh_cy + r_inner_halo * r_pol * np.sin(theta_c)
    x_out_h = bh_cx + r_outer_halo * r_eq * np.cos(theta_c)
    y_out_h = bh_cy + r_outer_halo * r_pol * np.sin(theta_c)

    ax_a.fill(np.concatenate([x_out_h, x_in_h[::-1]]),
              np.concatenate([y_out_h, y_in_h[::-1]]),
              facecolor=BLUE_LIGHT, alpha=0.18, edgecolor='none', zorder=2.5)

    # Three displaced quadrupolar perturbation contours in the near zone
    pert_specs = [
        (1.30, 0.11, 0.30, 2.2, 0.88, '-'),
        (1.62, 0.14, 0.48, 2.0, 0.76, '-'),
        (1.94, 0.12, 0.66, 1.7, 0.64, '--'),
    ]
    for scale_r, eps_q, phase_q, lw_p, alpha_p, ls_p in pert_specs:
        mod = 1.0 + eps_q * np.cos(2.0 * (theta_c - phase_q)) + 0.03 * np.cos(3.0 * (theta_c + 0.2))
        xp = bh_cx + scale_r * r_eq * mod * np.cos(theta_c)
        yp = bh_cy + scale_r * r_pol * mod * np.sin(theta_c)
        ax_a.plot(xp, yp, color=BLUE_MAIN, lw=lw_p, ls=ls_p, alpha=alpha_p, zorder=4)

    # 3c. Outgoing gravitational radiation wavefronts (propagating outward into the wave zone)
    wave_radii = [2.35, 2.76, 3.17, 3.58]
    wave_alphas = [0.70, 0.55, 0.41, 0.28]
    wave_lws = [2.0, 1.8, 1.5, 1.3]

    # Draw curved outgoing wavefronts on right and left lobes (kept above y = -2.85 for clean bottom labels)
    for r_w, a_w, lw_w in zip(wave_radii, wave_alphas, wave_lws):
        for th_span in [(-0.36 * np.pi, 0.36 * np.pi), (0.64 * np.pi, 1.34 * np.pi)]:
            th_arc = np.linspace(th_span[0], th_span[1], 120)
            mod_w = 1.0 + 0.06 * np.cos(2.0 * (th_arc - 0.75))
            xw = bh_cx + r_w * 0.96 * mod_w * np.cos(th_arc)
            yw = bh_cy + r_w * 0.92 * mod_w * np.sin(th_arc)
            ax_a.plot(xw, yw, color=BLUE_MID, lw=lw_w, alpha=a_w,
                      solid_capstyle='round', zorder=3.5)

    # Small outward-pointing arrow indicating outgoing wave propagation direction
    th_out = np.radians(18.0)
    r_arr_start = 2.28 * 0.95
    r_arr_end = 3.58 * 0.95
    ax_a.annotate('',
                  xy=(bh_cx + r_arr_end * np.cos(th_out), bh_cy + r_arr_end * np.sin(th_out)),
                  xytext=(bh_cx + r_arr_start * np.cos(th_out), bh_cy + r_arr_start * np.sin(th_out)),
                  arrowprops=dict(arrowstyle='-|>,head_length=0.52,head_width=0.30',
                                  color=ORANGE_MAIN, lw=2.2),
                  zorder=8)

    # Small inward-pointing arrow indicating partial horizon absorption
    th_in = np.radians(150.0)
    r_in_start = 1.54
    r_in_end = 0.98
    ax_a.annotate('',
                  xy=(bh_cx + r_in_end * r_eq * np.cos(th_in), bh_cy + r_in_end * r_pol * np.sin(th_in)),
                  xytext=(bh_cx + r_in_start * r_eq * np.cos(th_in), bh_cy + r_in_start * r_pol * np.sin(th_in)),
                  arrowprops=dict(arrowstyle='-|>,head_length=0.45,head_width=0.26',
                                  color=ORANGE_MAIN, lw=2.0),
                  zorder=9)

    # 3d. Central unperturbed Kerr black-hole silhouette (zorder = 6)
    bh_rgba = make_bh_RGBA(size=360)
    ax_a.imshow(bh_rgba,
                extent=[bh_cx - r_eq, bh_cx + r_eq, bh_cy - r_pol, bh_cy + r_pol],
                origin='lower', zorder=6)
    horizon_rim = Ellipse((bh_cx, bh_cy), 2.0 * r_eq, 2.0 * r_pol,
                          fill=False, edgecolor=NAVY, linewidth=2.0, zorder=6.5)
    ax_a.add_patch(horizon_rim)

    # 3e. Labels Inside Panel A:
    # 1) "Gravitational perturbation" (upper-left)
    th_gp_pt = np.radians(128.0)
    mod_gp = 1.0 + 0.14 * np.cos(2.0 * (th_gp_pt - 0.48))
    ax_a.annotate("Gravitational perturbation",
                  xy=(bh_cx + 1.62 * r_eq * mod_gp * np.cos(th_gp_pt),
                      bh_cy + 1.62 * r_pol * mod_gp * np.sin(th_gp_pt)),
                  xytext=(-2.12, 3.38),
                  arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.6, shrinkA=2, shrinkB=4),
                  fontsize=12.5, fontweight='bold', color=BLUE_DARK, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.25', facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.2),
                  zorder=12)

    # 2) "Spin axis" (upper-right, pointing to the rotation axis & azimuthal spin arrow)
    ax_a.annotate("Spin axis",
                  xy=(bh_cx + 0.34, bh_cy + 2.52),
                  xytext=(1.60, 3.38),
                  arrowprops=dict(arrowstyle="->", color=ORANGE_DARK, lw=1.6, shrinkA=2, shrinkB=4),
                  fontsize=12.5, fontweight='bold', color=ORANGE_DARK, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.25', facecolor=ORANGE_BG, edgecolor=ORANGE_BORDER, linewidth=1.2),
                  zorder=12)

    # 3) "Event horizon" (lower-left)
    th_eh_pt = np.radians(-132.0)
    ax_a.annotate("Event horizon",
                  xy=(bh_cx + r_eq * np.cos(th_eh_pt), bh_cy + r_pol * np.sin(th_eh_pt)),
                  xytext=(-2.75, -3.32),
                  arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.6, shrinkA=2, shrinkB=4),
                  fontsize=12.5, fontweight='bold', color=NAVY, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.25', facecolor=BG_WHITE, edgecolor=BORDER_COLOR, linewidth=1.2),
                  zorder=12)

    # 4) "Outgoing gravitational waves" (lower-right, below wave arcs)
    th_gw_pt = np.radians(-32.0)
    mod_gw = 1.0 + 0.06 * np.cos(2.0 * (th_gw_pt - 0.75))
    ax_a.annotate("Outgoing gravitational waves",
                  xy=(bh_cx + 2.76 * 0.96 * mod_gw * np.cos(th_gw_pt),
                      bh_cy + 2.76 * 0.92 * mod_gw * np.sin(th_gw_pt)),
                  xytext=(1.75, -3.32),
                  arrowprops=dict(arrowstyle="->", color=BLUE_MAIN, lw=1.6, shrinkA=2, shrinkB=4),
                  fontsize=12.5, fontweight='bold', color=BLUE_DARK, ha='center', va='center',
                  bbox=dict(boxstyle='round,pad=0.25', facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.2),
                  zorder=12)

    # =========================================================================
    # 4. PANEL B — QUASINORMAL RINGDOWN (CALCULATED KERR MODE)
    # Shifted slightly right (right_x + 0.094) so the vertical axis label sits
    # comfortably inside the enclosing inner viewport card.
    # =========================================================================
    ax_b = fig.add_axes([right_x + 0.094, p_y + 0.118, right_w - 0.118, p_h - 0.255], zorder=3)
    ax_b.set_facecolor(BG_WHITE)

    t_hat, strain, env_upper, env_lower = compute_ringdown_waveform(t_hat_max=60.0, n_pts=1500)

    ax_b.set_xlim(0.0, 60.0)
    ax_b.set_ylim(-1.22, 1.24)

    # Clean axes styling matching Oppenheimer–Snyder figure
    ax_b.spines['top'].set_visible(False)
    ax_b.spines['right'].set_visible(False)
    ax_b.spines['left'].set_edgecolor(AXIS_COLOR)
    ax_b.spines['left'].set_linewidth(1.8)
    ax_b.spines['bottom'].set_edgecolor(AXIS_COLOR)
    ax_b.spines['bottom'].set_linewidth(1.8)
    ax_b.tick_params(axis='x', pad=6, length=6, width=1.5, colors=AXIS_COLOR)
    ax_b.tick_params(axis='y', pad=6, length=6, width=1.5, colors=AXIS_COLOR)

    # Axis tip arrowheads
    ax_b.plot(1.0, 0.0, ">", transform=ax_b.transAxes, color=AXIS_COLOR,
              markersize=8.5, clip_on=False, zorder=10)
    ax_b.plot(0.0, 1.0, "^", transform=ax_b.transAxes, color=AXIS_COLOR,
              markersize=8.5, clip_on=False, zorder=10)

    # Ticks
    ax_b.set_xticks([0, 10, 20, 30, 40, 50, 60])
    ax_b.set_xticklabels([r"$0$", r"$10$", r"$20$", r"$30$", r"$40$", r"$50$", r"$60$"],
                         fontsize=13.0, fontweight='bold')
    ax_b.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax_b.set_yticklabels([r"$-1.0$", r"$-0.5$", r"$0$", r"$+0.5$", r"$+1.0$"],
                         fontsize=13.0, fontweight='bold')

    ax_b.set_xlabel(r"Normalized time,  $ct/m$", fontsize=14.2, fontweight='bold', color=NAVY, labelpad=8)
    ax_b.set_ylabel(r"Normalized strain,  $h/h_0$", fontsize=14.2, fontweight='bold', color=NAVY, labelpad=7)

    # Thin light-gray zero baseline
    ax_b.axhline(0.0, color='#94a3b8', linewidth=1.3, linestyle='-', zorder=1)

    # Upper & lower exponential envelopes: \pm e^{-0.0757 \hat{t}}
    ax_b.plot(t_hat, env_upper, color=ORANGE_MAIN, linestyle='--', linewidth=2.2, zorder=3)
    ax_b.plot(t_hat, env_lower, color=ORANGE_MAIN, linestyle='--', linewidth=2.2, zorder=3)

    # Calculated QNM strain curve: e^{-0.0757 \hat{t}} \cos(0.5855 \hat{t})
    ax_b.plot(t_hat, strain, color=BLUE_MAIN, linestyle='-', linewidth=3.0, solid_capstyle='round', zorder=4)

    # -------------------------------------------------------------------------
    # Panel B Annotations (3 non-overlapping zones, enlarged for Medium 700-800 px width)
    # -------------------------------------------------------------------------
    # 1. UPPER-MIDDLE/RIGHT: Decay envelope & Amplitude decay time \tau \approx 13.21 m/c (with 1/e marker)
    y_tau = np.exp(-1.0)  # 1/e \approx 0.3679 at t = \tau = 13.21
    ax_b.scatter([TAU_DECAY], [y_tau], s=68, color=ORANGE_MAIN, edgecolors='#ffffff', linewidths=1.5, zorder=7)
    ax_b.plot([TAU_DECAY, TAU_DECAY], [0.0, y_tau], color=ORANGE_MAIN, linestyle=':', linewidth=1.7, zorder=3.5)
    # Horizontal dotted guide to y-axis at 1/e and explicit 1/e badge next to the point
    ax_b.plot([0.0, TAU_DECAY], [y_tau, y_tau], color=ORANGE_MAIN, linestyle=':', linewidth=1.5, alpha=0.80, zorder=3.5)
    ax_b.text(TAU_DECAY + 1.1, y_tau - 0.14, r"$1/e$",
              fontsize=12.4, fontweight='bold', color=ORANGE_DARK, ha='left', va='center',
              bbox=dict(boxstyle='round,pad=0.16', facecolor=ORANGE_BG, edgecolor=ORANGE_BORDER, linewidth=1.0),
              zorder=8)

    ax_b.annotate(
        r"Decay envelope  $\pm e^{-0.0757\,ct/m}$" + "\n"
        + r"Amplitude decay time ($1/e$):  $\tau \approx 13.21\,m/c$",
        xy=(TAU_DECAY, y_tau), xytext=(33.5, 0.86),
        arrowprops=dict(arrowstyle="->", color=ORANGE_DARK, lw=1.7, shrinkA=2, shrinkB=5),
        fontsize=12.6, fontweight='bold', color=ORANGE_DARK, ha='center', va='center',
        linespacing=1.35,
        bbox=dict(boxstyle='round,pad=0.28', facecolor=ORANGE_BG, edgecolor=ORANGE_BORDER, linewidth=1.2),
        zorder=8
    )

    # 2. LOWER-LEFT: Oscillation period T \approx 10.73 m/c between Trough 1 (t = 5.37) and Trough 2 (t = 16.10)
    t_tr1 = 0.5 * T_PERIOD
    t_tr2 = 1.5 * T_PERIOD
    y_tr1 = -np.exp(-GAMMA_DECAY * t_tr1)
    y_tr2 = -np.exp(-GAMMA_DECAY * t_tr2)
    y_brack = -0.74

    ax_b.plot([t_tr1, t_tr1], [y_tr1, y_brack - 0.03], color=BLUE_DARK, linestyle=':', linewidth=1.5, zorder=3.5)
    ax_b.plot([t_tr2, t_tr2], [y_tr2, y_brack - 0.03], color=BLUE_DARK, linestyle=':', linewidth=1.5, zorder=3.5)
    ax_b.scatter([t_tr1, t_tr2], [y_tr1, y_tr2], s=48, color=BLUE_MAIN, edgecolors='#ffffff', linewidths=1.3, zorder=6)

    ax_b.annotate('', xy=(t_tr2, y_brack), xytext=(t_tr1, y_brack),
                  arrowprops=dict(arrowstyle='<->', color=BLUE_DARK, lw=1.9, shrinkA=0, shrinkB=0),
                  zorder=6)
    ax_b.text(10.6, -1.01,
              "Oscillation period\n" + r"$T \approx 10.73\,m/c$",
              fontsize=12.0, fontweight='bold', color=BLUE_DARK, ha='center', va='center',
              linespacing=1.28,
              bbox=dict(boxstyle='round,pad=0.22', facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.1),
              zorder=7)

    # 3. LOWER-RIGHT: Fundamental mode & calculated waveform callout pointing to Trough 3 (t = 26.83)
    t_tr3 = 2.5 * T_PERIOD
    y_tr3 = -np.exp(-GAMMA_DECAY * t_tr3)
    ax_b.scatter([t_tr3], [y_tr3], s=48, color=BLUE_MAIN, edgecolors='#ffffff', linewidths=1.3, zorder=6)

    ax_b.annotate(
        r"Fundamental mode $(\ell, m_\phi, n) = (2, 2, 0)$" + "\n"
        + r"$m\omega/c \simeq 0.5855 - 0.0757i$" + "\n"
        + r"$h(t)/h_0 = e^{-0.0757\,ct/m}\cos(0.5855\,ct/m)$",
        xy=(t_tr3, y_tr3), xytext=(41.8, -0.56),
        arrowprops=dict(arrowstyle="->", color=BLUE_MAIN, lw=1.6, shrinkA=2, shrinkB=5),
        fontsize=11.9, fontweight='bold', color=BLUE_DARK, ha='center', va='center',
        linespacing=1.36,
        bbox=dict(boxstyle='round,pad=0.24', facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.2),
        zorder=8
    )

    # Save figure and normalize to clean 24-bit RGB PNG for maximum Medium compatibility
    fig.savefig(output_path, dpi=dpi, facecolor=BG_WHITE, edgecolor='none')
    plt.close(fig)

    with Image.open(output_path) as im:
        rgb_im = im.convert("RGB")
        rgb_im.save(output_path, format="PNG", optimize=True)

    print(f"[OK] Generated {output_path} ({fig_w * dpi:.0f} x {fig_h * dpi:.0f} px, RGB PNG)")




if __name__ == "__main__":
    create_figure()
