#!/usr/bin/env python3
"""
Generate a binary-orbit Doppler diagram illustrating how orbital motion
causes the observed pulsar period to shift periodically.
Shows wavefront compression (blueshift / shorter period) during approach,
and wavefront stretching (redshift / longer period) during recession.
"""

from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "binary_orbit_doppler_infographic.png"


def generate_doppler_orbit_infographic(out_path=None):
    if out_path is None:
        out_path = DEFAULT_OUT
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # SETUP FIGURE
    # -------------------------------------------------------------------------
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(12.5, 6.8), dpi=220)
    fig.patch.set_facecolor('#0d111a')

    # Two-column layout: Left (Orbital geometry & Doppler wavefronts, 58%),
    # Right (Observed pulse comparison, 42%)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.3, 0.92], wspace=0.16,
                          left=0.03, right=0.97, top=0.95, bottom=0.06)

    # -------------------------------------------------------------------------
    # LEFT PANEL: Binary Orbit & Doppler Wavefronts
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor('#0d111a')
    ax1.set_xlim(-3.4, 4.4)
    ax1.set_ylim(-2.5, 2.5)
    ax1.set_aspect('equal')
    ax1.axis('off')

    # Center of the binary system
    cx, cy = -0.7, 0.0

    # Orbit parameters (eccentric ellipse)
    a_orb = 1.95
    b_orb = 1.25
    theta_orb = np.linspace(0, 2 * np.pi, 300)
    orbit_x = cx + a_orb * np.cos(theta_orb)
    orbit_y = cy + b_orb * np.sin(theta_orb)

    # Draw orbital path (dashed ellipse)
    ax1.plot(orbit_x, orbit_y, color='#475569', ls='--', lw=1.6, alpha=0.85)

    # Direction of motion arrows on orbit
    ax1.annotate("", xy=(cx, cy - b_orb), xytext=(cx - 0.35, cy - b_orb),
                 arrowprops=dict(arrowstyle="->", color="#38bdf8", lw=2.0))
    ax1.annotate("", xy=(cx, cy + b_orb), xytext=(cx + 0.35, cy + b_orb),
                 arrowprops=dict(arrowstyle="->", color="#f59e0b", lw=2.0))

    # Unseen Companion (Neutron star) at focus
    comp_x = cx - 0.50
    comp_y = cy
    comp_glow = patches.Circle((comp_x, comp_y), 0.32, facecolor='#6366f1', alpha=0.25, edgecolor='none')
    comp_star = patches.Circle((comp_x, comp_y), 0.17, facecolor='#818cf8', edgecolor='#c7d2fe', lw=1.5)
    ax1.add_patch(comp_glow)
    ax1.add_patch(comp_star)
    ax1.text(comp_x, comp_y - 0.44, "Unseen Companion\n(Neutron Star)", color='#cbd5e1',
             fontsize=9.0, ha='center', va='top', fontweight='bold')

    # Center of Mass (Barycenter)
    bary_x, bary_y = cx - 0.22, cy
    ax1.plot([bary_x - 0.08, bary_x + 0.08], [bary_y, bary_y], color='#94a3b8', lw=1.2)
    ax1.plot([bary_x, bary_x], [bary_y - 0.08, bary_y + 0.08], color='#94a3b8', lw=1.2)
    ax1.text(bary_x + 0.12, bary_y + 0.12, "Barycenter", color='#94a3b8', fontsize=7.5, fontstyle='italic')

    # -------------------------------------------------------------------------
    # Position 1: Pulsar Approaching Earth (Bottom branch, moving right)
    p1_x = cx + 0.2
    p1_y = cy - b_orb

    # Pulsar body
    p1_glow = patches.Circle((p1_x, p1_y), 0.32, facecolor='#38bdf8', alpha=0.35, edgecolor='none')
    p1_star = patches.Circle((p1_x, p1_y), 0.16, facecolor='#ffffff', edgecolor='#38bdf8', lw=1.8)
    ax1.add_patch(p1_glow)
    ax1.add_patch(p1_star)

    # Velocity vector toward Earth
    ax1.annotate("", xy=(p1_x + 1.1, p1_y), xytext=(p1_x + 0.18, p1_y),
                 arrowprops=dict(arrowstyle="->", color="#38bdf8", lw=2.5))
    ax1.text(p1_x + 0.65, p1_y - 0.25, "Velocity $\\vec{v}$", color='#38bdf8',
             fontsize=9.0, fontweight='bold', ha='center', va='top')

    # Compressed wavefronts propagating to the right
    for r_wave in [0.45, 0.75, 1.05, 1.35]:
        arc_wave = patches.Arc((p1_x + 0.1, p1_y), r_wave * 2, r_wave * 2, angle=0,
                               theta1=-40, theta2=40, color='#38bdf8', lw=1.5, alpha=0.85 - r_wave*0.35)
        ax1.add_patch(arc_wave)

    # Integrated label for Approaching
    ax1.text(p1_x + 0.2, p1_y - 0.70,
             "PULSAR APPROACHING EARTH\n"
             "Wavefronts compressed in transit\n"
             "$\\rightarrow$ Shorter observed period ($P < 59\\text{ ms}$)",
             color='#38bdf8', fontsize=9.2, fontweight='bold', ha='center', va='top')

    # -------------------------------------------------------------------------
    # Position 2: Pulsar Receding from Earth (Top branch, moving left)
    p2_x = cx - 0.2
    p2_y = cy + b_orb

    # Pulsar body
    p2_glow = patches.Circle((p2_x, p2_y), 0.32, facecolor='#f59e0b', alpha=0.35, edgecolor='none')
    p2_star = patches.Circle((p2_x, p2_y), 0.16, facecolor='#ffffff', edgecolor='#f59e0b', lw=1.8)
    ax1.add_patch(p2_glow)
    ax1.add_patch(p2_star)

    # Velocity vector away from Earth
    ax1.annotate("", xy=(p2_x - 1.1, p2_y), xytext=(p2_x - 0.18, p2_y),
                 arrowprops=dict(arrowstyle="->", color="#f59e0b", lw=2.5))
    ax1.text(p2_x - 0.65, p2_y + 0.25, "Velocity $\\vec{v}$", color='#f59e0b',
             fontsize=9.0, fontweight='bold', ha='center', va='bottom')

    # Stretched wavefronts propagating to the right (toward Earth)
    for r_wave in [0.65, 1.25, 1.85]:
        arc_wave = patches.Arc((p2_x - 0.1, p2_y), r_wave * 2, r_wave * 2, angle=0,
                               theta1=-35, theta2=35, color='#f59e0b', lw=1.5, alpha=0.85 - r_wave*0.25)
        ax1.add_patch(arc_wave)

    # Integrated label for Receding
    ax1.text(p2_x - 0.2, p2_y + 0.70,
             "PULSAR RECEDING FROM EARTH\n"
             "Wavefronts stretched in transit\n"
             "$\\rightarrow$ Longer observed period ($P > 59\\text{ ms}$)",
             color='#f59e0b', fontsize=9.2, fontweight='bold', ha='center', va='bottom')

    # -------------------------------------------------------------------------
    # Earth & Line of Sight (Far Right)
    earth_x = 3.6
    earth_y = 0.0

    # Dashed Line of sight arrow to Earth
    ax1.plot([cx + 1.25, earth_x - 0.45], [earth_y, earth_y],
             color='#facc15', ls='--', lw=2.2, alpha=0.9)
    ax1.annotate("", xy=(earth_x - 0.42, earth_y), xytext=(earth_x - 0.8, earth_y),
                 arrowprops=dict(arrowstyle="->", color="#facc15", lw=2.2))

    ax1.text((cx + 1.25 + earth_x - 0.5) / 2, earth_y + 0.24,
             "Line of Sight to Earth", color='#facc15', fontsize=10,
             fontweight='bold', ha='center')

    # Earth Icon
    earth_glow = patches.Circle((earth_x, earth_y), 0.44, facecolor='#1e3a8a', alpha=0.35, edgecolor='none')
    earth_body = patches.Circle((earth_x, earth_y), 0.35, facecolor='#1d4ed8', edgecolor='#60a5fa', lw=1.8)
    ax1.add_patch(earth_glow)
    ax1.add_patch(earth_body)

    # Continent curve on Earth
    ax1.plot([earth_x - 0.12, earth_x + 0.08, earth_x + 0.18],
             [earth_y + 0.12, earth_y + 0.04, earth_y - 0.12],
             color='#34d399', lw=2.0, alpha=0.85)

    ax1.text(earth_x, earth_y - 0.55, "Observer on Earth\n(Arecibo)",
             color='#f8fafc', fontsize=9.2, fontweight='bold', ha='center', va='top')

    # -------------------------------------------------------------------------
    # RIGHT PANEL: Observed Pulse Spacing at Earth
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor('#0d111a')
    ax2.axis('off')

    # Sub-axis 1: Approaching Pulse Train (Top half of right panel)
    sub1 = fig.add_axes([0.60, 0.54, 0.37, 0.38])
    sub1.set_facecolor('#111827')
    sub1.spines['bottom'].set_color('#334155')
    sub1.spines['left'].set_color('#334155')
    sub1.spines['top'].set_visible(False)
    sub1.spines['right'].set_visible(False)
    sub1.tick_params(colors='#94a3b8', labelsize=8)

    np.random.seed(42)
    t_arr1 = np.linspace(0, 3.2, 500)
    sig1 = np.zeros_like(t_arr1) + 0.03 * np.random.normal(0, 0.1, len(t_arr1))
    for pt in [0.35, 1.15, 1.95, 2.75]:
        sig1 += 0.95 * np.exp(-((t_arr1 - pt) / 0.045)**2)
    sig1 = np.clip(sig1, 0, 1.2)

    sub1.plot(t_arr1, sig1, color='#38bdf8', lw=1.8)
    sub1.fill_between(t_arr1, sig1, color='#38bdf8', alpha=0.25)
    sub1.set_title("Pulsar Approaching: Shorter Observed Period",
                   fontsize=9.5, fontweight='bold', color='#38bdf8', pad=8, loc='left')
    sub1.set_xticks([0.35, 1.15, 1.95, 2.75])
    sub1.set_xticklabels(["Tick", "Tick", "Tick", "Tick"], color='#94a3b8', fontsize=7.5)
    sub1.set_yticks([])
    sub1.set_xlim(0, 3.2)
    sub1.set_ylim(-0.05, 1.45)

    # Arrow showing shorter period placed ABOVE the peaks for zero collision
    sub1.annotate("", xy=(1.15, 1.08), xytext=(0.35, 1.08),
                  arrowprops=dict(arrowstyle="<->", color="#38bdf8", lw=1.6))
    sub1.text(0.75, 1.18, "$P_{\\mathrm{obs}} < 59\\text{ ms}$ (Compressed)",
              color='#38bdf8', fontsize=8.5, fontweight='bold', ha='center')

    # Sub-axis 2: Receding Pulse Train (Bottom half of right panel)
    sub2 = fig.add_axes([0.60, 0.09, 0.37, 0.38])
    sub2.set_facecolor('#111827')
    sub2.spines['bottom'].set_color('#334155')
    sub2.spines['left'].set_color('#334155')
    sub2.spines['top'].set_visible(False)
    sub2.spines['right'].set_visible(False)
    sub2.tick_params(colors='#94a3b8', labelsize=8)

    t_arr2 = np.linspace(0, 3.2, 500)
    sig2 = np.zeros_like(t_arr2) + 0.03 * np.random.normal(0, 0.1, len(t_arr2))
    for pt in [0.45, 1.75, 3.05]:
        sig2 += 0.95 * np.exp(-((t_arr2 - pt) / 0.045)**2)
    sig2 = np.clip(sig2, 0, 1.2)

    sub2.plot(t_arr2, sig2, color='#f59e0b', lw=1.8)
    sub2.fill_between(t_arr2, sig2, color='#f59e0b', alpha=0.25)
    sub2.set_title("Pulsar Receding: Longer Observed Period",
                   fontsize=9.5, fontweight='bold', color='#f59e0b', pad=8, loc='left')
    sub2.set_xlabel("Time $\\longrightarrow$", fontsize=8.5, color='#94a3b8', labelpad=4)
    sub2.set_ylabel("Signal Intensity", fontsize=8.5, color='#94a3b8')
    sub2.set_xticks([0.45, 1.75, 3.05])
    sub2.set_xticklabels(["Tick", "Tick", "Tick"], color='#94a3b8', fontsize=7.5)
    sub2.set_yticks([])
    sub2.set_xlim(0, 3.2)
    sub2.set_ylim(-0.05, 1.45)

    # Arrow showing longer period placed ABOVE the peaks
    sub2.annotate("", xy=(1.75, 1.08), xytext=(0.45, 1.08),
                  arrowprops=dict(arrowstyle="<->", color="#f59e0b", lw=1.6))
    sub2.text(1.10, 1.18, "$P_{\\mathrm{obs}} > 59\\text{ ms}$ (Stretched)",
              color='#f59e0b', fontsize=8.5, fontweight='bold', ha='center')

    # Save high-resolution image
    plt.savefig(out_path, dpi=250, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Successfully generated clean {out_path}")
    return out_path


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else None
    generate_doppler_orbit_infographic(target)
