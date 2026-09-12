#!/usr/bin/env python3
"""
Generate an infographic explaining the pulsar 'lighthouse' model.
Depicts the rotating neutron star, tilted magnetic dipole axis, sweeping radio beam,
and the resulting periodic pulse train observed from Earth.
"""

from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "pulsar_lighthouse_infographic.png"


def generate_pulsar_infographic(out_path=None):
    if out_path is None:
        out_path = DEFAULT_OUT
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # SETUP FIGURE
    # -------------------------------------------------------------------------
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(12.5, 6.9), dpi=220)
    fig.patch.set_facecolor('#0d111a')

    # Setup Gridspec without top title and bottom text
    gs = fig.add_gridspec(2, 1, height_ratios=[1.7, 0.85], top=0.96, bottom=0.08, hspace=0.28)

    # -------------------------------------------------------------------------
    # TOP PANEL: The 3D Lighthouse Geometry
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor('#0d111a')
    ax1.set_xlim(-4.2, 4.4)
    ax1.set_ylim(-2.2, 2.3)
    ax1.set_aspect('equal')
    ax1.axis('off')

    # Center of neutron star
    cx, cy = -0.9, -0.15

    # Magnetic tilt angle: 30 degrees to the right
    tilt_deg = 30
    tilt_rad = np.radians(tilt_deg)
    m_dx = np.sin(tilt_rad)
    m_dy = np.cos(tilt_rad)

    # 1. Magnetic Field Lines (Dipole loops)
    for sign in [-1, 1]:
        for scale in [0.75, 1.2, 1.7]:
            t = np.linspace(0.18, np.pi - 0.18, 120)
            r = scale * (np.sin(t)**2)
            xp = sign * r * np.sin(t)
            yp = r * np.cos(t)
            xr = xp * np.cos(-tilt_rad) - yp * np.sin(-tilt_rad)
            yr = xp * np.sin(-tilt_rad) + yp * np.cos(-tilt_rad)
            ax1.plot(xr + cx, yr + cy, color='#0284c7', alpha=0.18, lw=1.2)

    # 2. Radio Beams (Cones emerging from magnetic poles)
    beam_len = 1.95
    beam_hw = 0.48
    tip_x = cx + m_dx * beam_len
    tip_y = cy + m_dy * beam_len
    p_dx = np.cos(tilt_rad)
    p_dy = -np.sin(tilt_rad)

    # Upper Beam (Magnetic North)
    poly_upper = np.array([
        [cx, cy],
        [tip_x - p_dx * beam_hw, tip_y - p_dy * beam_hw],
        [tip_x + p_dx * beam_hw, tip_y + p_dy * beam_hw]
    ])
    beam_upper = patches.Polygon(poly_upper, closed=True,
                                 facecolor='#38bdf8', alpha=0.28,
                                 edgecolor='#7dd3fc', lw=1.4, ls='--')
    ax1.add_patch(beam_upper)
    # Core beam glow line
    ax1.plot([cx, tip_x], [cy, tip_y], color='#ffffff', lw=2.2, alpha=0.9)

    # Lower Beam (Magnetic South)
    poly_lower = np.array([
        [cx, cy],
        [cx - m_dx * beam_len - p_dx * beam_hw * 0.8, cy - m_dy * beam_len - p_dy * beam_hw * 0.8],
        [cx - m_dx * beam_len + p_dx * beam_hw * 0.8, cy - m_dy * beam_len + p_dy * beam_hw * 0.8]
    ])
    beam_lower = patches.Polygon(poly_lower, closed=True,
                                 facecolor='#0284c7', alpha=0.16,
                                 edgecolor='#38bdf8', lw=1.0, ls=':')
    ax1.add_patch(beam_lower)
    ax1.plot([cx, cx - m_dx * beam_len], [cy, cy - m_dy * beam_len], color='#bae6fd', lw=1.3, alpha=0.45)

    # 3. Sweeping Cone (Perspective circle traced by the upper beam)
    t_sweep = np.linspace(0, 2*np.pi, 200)
    sweep_a = 1.02
    sweep_b = 0.30
    sweep_cx = cx
    sweep_cy = cy + beam_len * np.cos(tilt_rad) * 0.92
    sweep_x = sweep_cx + sweep_a * np.cos(t_sweep)
    sweep_y = sweep_cy + sweep_b * np.sin(t_sweep)
    ax1.plot(sweep_x, sweep_y, color='#facc15', ls=(0, (3, 3)), lw=1.4, alpha=0.85)

    # Label for Sweeping Cone (Placed cleanly on upper left)
    ax1.text(sweep_cx - sweep_a - 0.2, sweep_cy + 0.18,
             "Sweeping path\nof radio beam",
             color='#facc15', fontsize=9.5, fontweight='bold', ha='right', va='center')
    ax1.annotate("", xy=(sweep_cx - sweep_a * 0.85, sweep_cy + 0.18),
                 xytext=(sweep_cx - sweep_a - 0.15, sweep_cy + 0.18),
                 arrowprops=dict(arrowstyle="->", color="#facc15", lw=1.3))

    # 4. Rotation Axis (Vertical)
    ax1.plot([cx, cx], [cy - 1.6, cy + 1.8], color='#cbd5e1', ls='--', lw=1.8, alpha=0.8)
    # Rotation spin arrow at top
    rot_arc = patches.Arc((cx, cy + 1.55), 0.65, 0.26, angle=0, theta1=20, theta2=210,
                          color='#cbd5e1', lw=1.8)
    ax1.add_patch(rot_arc)
    ax1.annotate("", xy=(cx - 0.32, cy + 1.56), xytext=(cx - 0.32, cy + 1.62),
                 arrowprops=dict(arrowstyle="->", color="#cbd5e1", lw=1.8))
    ax1.text(cx, cy + 1.95, "Rotation Axis\n(Rapid Spin)", color='#f1f5f9',
             fontsize=10, ha='center', va='bottom', fontweight='bold')

    # 5. Magnetic Axis Line (Tilted)
    ax1.plot([cx - m_dx * 2.2, cx + m_dx * 2.2], [cy - m_dy * 2.2, cy + m_dy * 2.2],
             color='#38bdf8', ls='-.', lw=1.4, alpha=0.75)

    # Label Magnetic Axis in the lower-left, placed well below the neutron star text
    ax1.annotate("Magnetic Axis\n(Tilted by angle $\\alpha$)",
                 xy=(cx - m_dx * 1.4, cy - m_dy * 1.4), xytext=(cx - 0.2, cy - 1.75),
                 arrowprops=dict(arrowstyle="->", color="#38bdf8", lw=1.3),
                 color='#38bdf8', fontsize=9.5, fontweight='bold', ha='right', va='top')

    # Tilt angle arc
    arc_tilt = patches.Arc((cx, cy + 0.7), 0.65, 0.65, angle=90, theta1=-tilt_deg, theta2=0,
                           color='#f59e0b', lw=1.5)
    ax1.add_patch(arc_tilt)
    ax1.text(cx + 0.16, cy + 0.85, "$\\alpha$", color='#f59e0b', fontsize=10, fontweight='bold')

    # 6. Neutron Star Body
    glow1 = patches.Circle((cx, cy), 0.38, facecolor='#38bdf8', alpha=0.15, edgecolor='none')
    glow2 = patches.Circle((cx, cy), 0.26, facecolor='#60a5fa', alpha=0.35, edgecolor='none')
    star = patches.Circle((cx, cy), 0.18, facecolor='#ffffff', edgecolor='#93c5fd', lw=2)
    ax1.add_patch(glow1)
    ax1.add_patch(glow2)
    ax1.add_patch(star)

    ax1.annotate("Neutron Star\n(~20 km across,\n>1 Sun's mass)",
                 xy=(cx - 0.16, cy - 0.05), xytext=(cx - 1.8, cy - 0.45),
                 arrowprops=dict(arrowstyle="->", color="#e2e8f0", lw=1.2),
                 color="#e2e8f0", fontsize=9.5, fontweight='bold', ha='right', va='center')

    # 7. Radio Beam Label
    ax1.annotate("Radio Emission Beam\n(Emitted from magnetic pole)",
                 xy=(cx + m_dx * 1.1, cy + m_dy * 1.1), xytext=(cx - 1.8, cy + 0.6),
                 arrowprops=dict(arrowstyle="->", color="#7dd3fc", lw=1.2),
                 color='#7dd3fc', fontsize=9.5, fontweight='bold', ha='right', va='center')

    # 8. Earth & Line of Sight (Right side)
    sight_start_x = sweep_cx + sweep_a * 0.96
    sight_start_y = sweep_cy
    earth_x = 3.3
    earth_y = sight_start_y

    # Dashed line of sight
    ax1.plot([sight_start_x + 0.1, earth_x - 0.55], [sight_start_y, earth_y],
             color='#facc15', ls='--', lw=2.2, alpha=0.95)
    ax1.annotate("", xy=(earth_x - 0.50, earth_y), xytext=(earth_x - 0.9, earth_y),
                 arrowprops=dict(arrowstyle="->", color="#facc15", lw=2.2))

    # Text along line of sight
    mid_x = (sight_start_x + earth_x - 0.5) / 2
    ax1.text(mid_x, earth_y + 0.28,
             "Line of Sight to Earth", color='#facc15', fontsize=10.5,
             fontweight='bold', ha='center', va='bottom')
    ax1.text(mid_x, earth_y - 0.40,
             "Beam points toward Earth once per rotation",
             color='#cbd5e1', fontsize=9.0, fontstyle='italic', ha='center', va='top')

    # Earth Icon
    earth_glow = patches.Circle((earth_x, earth_y), 0.48, facecolor='#1e3a8a', alpha=0.35, edgecolor='none')
    earth_body = patches.Circle((earth_x, earth_y), 0.38, facecolor='#1d4ed8', edgecolor='#60a5fa', lw=1.8)
    ax1.add_patch(earth_glow)
    ax1.add_patch(earth_body)

    # Continent curve on Earth
    ax1.plot([earth_x - 0.15, earth_x + 0.1, earth_x + 0.2],
             [earth_y + 0.15, earth_y + 0.05, earth_y - 0.15],
             color='#34d399', lw=2.2, alpha=0.85)

    ax1.text(earth_x, earth_y - 0.58, "Observer on Earth\n(Arecibo Radio Telescope)",
             color='#f8fafc', fontsize=9.5, fontweight='bold', ha='center', va='top')

    # -------------------------------------------------------------------------
    # BOTTOM PANEL: The Observed Signal (Pulse Train)
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor('#111827')
    ax2.spines['bottom'].set_color('#475569')
    ax2.spines['left'].set_color('#475569')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.tick_params(colors='#94a3b8', labelsize=8.5)

    # Generate synthetic pulse train with 4 pulses
    np.random.seed(42)
    t_signal = np.linspace(0, 4.0, 1000)
    signal = np.zeros_like(t_signal) + np.random.normal(0.04, 0.015, len(t_signal))

    pulse_times = [0.5, 1.5, 2.5, 3.5]
    for pt in pulse_times:
        signal += 0.95 * np.exp(-((t_signal - pt) / 0.055)**2)

    signal = np.clip(signal, 0, 1.2)

    # Plot signal
    ax2.plot(t_signal, signal, color='#38bdf8', lw=2.0)
    ax2.fill_between(t_signal, signal, color='#38bdf8', alpha=0.25)

    # Formatting
    ax2.set_title("WHAT WE OBSERVE ON EARTH: A TRAIN OF PRECISE RADIO PULSES",
                  fontsize=10.5, fontweight='bold', color='#f1f5f9', pad=10, loc='left')
    ax2.set_xlabel("Time $\\longrightarrow$", fontsize=9.5, color='#94a3b8', labelpad=4)
    ax2.set_ylabel("Radio Intensity", fontsize=9.5, color='#94a3b8')
    ax2.set_xlim(-0.1, 4.1)
    ax2.set_ylim(-0.08, 1.35)

    ax2.set_xticks(pulse_times)
    ax2.set_xticklabels(["Tick 1", "Tick 2", "Tick 3", "Tick 4"], color='#cbd5e1', fontweight='bold')
    ax2.set_yticks([])

    # Arrow showing Period P
    p1, p2 = pulse_times[0], pulse_times[1]
    ax2.annotate("", xy=(p2, 0.65), xytext=(p1, 0.65),
                 arrowprops=dict(arrowstyle="<->", color="#facc15", lw=1.8))
    ax2.text((p1 + p2) / 2, 0.75, "Pulse Period ($P$)\n($59\\text{ ms}$ for PSR B1913+16)",
             color='#facc15', fontsize=8.5, fontweight='bold', ha='center')

    # Annotation for pulse detection peak
    ax2.annotate("Pulse detected!\n(Beam sweeps past Earth)",
                 xy=(pulse_times[2], 1.02), xytext=(pulse_times[2], 1.25),
                 arrowprops=dict(arrowstyle="->", color="#38bdf8", lw=1.4),
                 color='#38bdf8', fontsize=8.5, fontweight='bold', ha='center')

    # Annotation for off-pulse region
    ax2.annotate("Off-pulse quiet\n(Beam pointing away)",
                 xy=((pulse_times[2] + pulse_times[3]) / 2, 0.08),
                 xytext=((pulse_times[2] + pulse_times[3]) / 2, 0.38),
                 arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=1.1),
                 color='#94a3b8', fontsize=8.0, fontstyle='italic', ha='center')

    # Save high-resolution PNG
    plt.savefig(out_path, dpi=250, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Successfully generated clean infographic at: {out_path}")
    return out_path


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else None
    generate_pulsar_infographic(target)
