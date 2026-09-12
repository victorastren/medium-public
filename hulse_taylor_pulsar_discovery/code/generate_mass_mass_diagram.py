#!/usr/bin/env python3
r"""
Generate a Mass-Mass constraint diagram for PSR B1913+16 in the m1 - m2 plane.
Reflects the exact calculations from the first two Post-Keplerian parameters:
1. Periastron advance (\dot{\omega} = 4.2266 deg/yr) -> fixes total mass m1 + m2 = 2.8284 M_sun
2. Einstein delay (\gamma = 4.294 ms) -> non-linear constraint curve
Intersection yields the individual neutron-star masses:
- m1 = 1.4414 M_sun (pulsar)
- m2 = 1.3867 M_sun (companion)
- Inclination i = 47.2 deg
"""

from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.optimize import brentq

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "mass_mass_diagram.png"

# -------------------------------------------------------------------------
# CONSTANTS & PHYSICAL PARAMETERS (PSR B1913+16)
# -------------------------------------------------------------------------
T_sun = 4.925490947e-6  # G*M_sun/c^3 in seconds
Pb_s = 7.751939106 * 3600.0  # Orbital period in seconds
e = 0.6171334  # Eccentricity
x = 2.341774  # Projected semimajor axis (a1*sin(i)/c) in seconds

# Measured PK parameters
om_dot_deg_yr = 4.226598  # deg/yr
om_dot_rad_s = om_dot_deg_yr * (np.pi / 180.0) / (365.25 * 86400.0)
gamma_s = 0.004294  # 4.294 ms

# Total mass from \dot{\omega}
M_tot = (om_dot_rad_s * (1 - e**2) / (3.0 * (T_sun**(2/3)) * ((Pb_s / (2 * np.pi))**(-5/3))))**1.5

# Mass function f(m)
f_m = (4 * np.pi**2 / (Pb_s**2)) * (x**3) / T_sun


def calc_gamma(m1, m2):
    return e * (T_sun**(2/3)) * ((Pb_s / (2 * np.pi))**(1/3)) * m2 * (m1 + 2 * m2) * ((m1 + m2)**(-4/3))


def solve_m2_for_gamma(m1_val, target_gamma=gamma_s):
    def f(m2_val):
        return calc_gamma(m1_val, m2_val) - target_gamma
    return brentq(f, 0.05, 5.0)


def solve_m2_for_sini(m1_val, target_sini=1.0):
    def f(m2_val):
        return target_sini - ((m1_val + m2_val)**(2/3) / m2_val) * (f_m**(1/3))
    return brentq(f, 0.01, 5.0)


def draw_card(ax, x, y, w, h, title, title_color, bullets, border_color='#23304a', bg_color='#131a29'):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.025",
                                  facecolor=bg_color, edgecolor=border_color, linewidth=1.3, zorder=2)
    ax.add_patch(rect)
    ax.text(x + 0.04, y + h - 0.058, title, fontsize=10.2, weight='bold', color=title_color, zorder=3)
    curr_y = y + h - 0.120
    for b in bullets:
        ax.text(x + 0.04, curr_y, b, fontsize=8.8, color='#94a3b8', linespacing=1.35, zorder=3)
        curr_y -= 0.072


def generate_mass_mass_diagram(out_path=None):
    if out_path is None:
        out_path = DEFAULT_OUT
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Intersection point
    m1_intersect = brentq(lambda m1: calc_gamma(m1, M_tot - m1) - gamma_s, 0.5, 2.5)
    m2_intersect = M_tot - m1_intersect
    sin_i = ((m1_intersect + m2_intersect)**(2/3) / m2_intersect) * (f_m**(1/3))

    # Grid for curves
    m1_grid = np.linspace(0.4, 2.4, 350)
    m2_omdot = M_tot - m1_grid
    m2_gamma = np.array([solve_m2_for_gamma(m1) for m1 in m1_grid])
    m2_sini_1 = np.array([solve_m2_for_sini(m1, 1.0) for m1 in m1_grid])
    m2_sini_47 = np.array([solve_m2_for_sini(m1, sin_i) for m1 in m1_grid])

    # -------------------------------------------------------------------------
    # FIGURE SETUP
    # -------------------------------------------------------------------------
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(14.2, 7.0), dpi=250)
    BG_MAIN = '#0d111a'
    fig.patch.set_facecolor(BG_MAIN)

    gs = fig.add_gridspec(1, 2, width_ratios=[1.22, 0.92], wspace=0.18,
                          left=0.06, right=0.96, top=0.95, bottom=0.09)

    BG_CARD = '#131a29'
    BORDER = '#23304a'
    GRID = '#1e293b'
    CYAN = '#38bdf8'
    ROSE = '#f43f5e'
    GOLD = '#facc15'
    TEXT_MAIN = '#f8fafc'
    TEXT_MUTED = '#94a3b8'

    # =========================================================================
    # LEFT PANEL: M1 - M2 MASS CONSTRAINT PLANE
    # =========================================================================
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(BG_CARD)
    for spine in ax1.spines.values():
        spine.set_color(BORDER)
        spine.set_linewidth(1.3)

    ax1.set_xlim(0.6, 2.3)
    ax1.set_ylim(0.6, 2.3)

    ax1.set_title(r'$\mathbf{m_1 - m_2\ \mathrm{Plane}}$', fontsize=12.5, color=TEXT_MAIN, pad=12)
    ax1.grid(True, color=GRID, linestyle='--', linewidth=0.8, alpha=0.7)

    # Physically forbidden region (sin i > 1.0)
    ax1.fill_between(m1_grid, 0, m2_sini_1, color='#1e1b4b', alpha=0.45, hatch='//', zorder=1)
    ax1.plot(m1_grid, m2_sini_1, color='#6366f1', linestyle=':', linewidth=1.6, alpha=0.85, zorder=2)
    ax1.text(1.95, 0.78, r'$\sin i > 1$' + '\n(Forbidden Region)', color='#818cf8', fontsize=9.5,
             ha='center', va='center', style='italic')

    # 1. Plot Periastron Advance Line (\dot{\omega})
    ax1.plot(m1_grid, m2_omdot, color=CYAN, linewidth=3.0,
             label=r'Periastron Advance $\dot{\omega} = 4.2266^\circ\,\mathrm{yr}^{-1}$', zorder=4)

    # 2. Plot Einstein Delay Curve (\gamma)
    ax1.plot(m1_grid, m2_gamma, color=ROSE, linewidth=3.0,
             label=r'Einstein Delay $\gamma = 4.294\,\mathrm{ms}$', zorder=4)

    # 3. Plot Derived Inclination Line (sin i = 0.734)
    ax1.plot(m1_grid, m2_sini_47, color='#94a3b8', linestyle='--', linewidth=1.3, alpha=0.6,
             label=r'Orbital Inclination $i \approx 47.2^\circ$', zorder=3)

    # 4. Highlight Intersection Point
    ax1.scatter([m1_intersect], [m2_intersect], color=GOLD, s=150, edgecolors='#ffffff', linewidths=2.2, zorder=6)
    ax1.scatter([m1_intersect], [m2_intersect], color=GOLD, s=400, alpha=0.22, zorder=5)

    callout_text = (
        r"$\mathbf{Mass\ Intersection}$" + "\n"
        r"$m_1 = 1.4414 \pm 0.0002\,M_\odot$" + "\n"
        r"$m_2 = 1.3867 \pm 0.0002\,M_\odot$" + "\n"
        r"$M_{\mathrm{total}} = 2.8284\,M_\odot$" + "\n"
        r"$\sin i \approx 0.734\ (i \approx 47.2^\circ)$"
    )
    ax1.annotate(callout_text,
                 xy=(m1_intersect, m2_intersect), xycoords='data',
                 xytext=(m1_intersect + 0.16, m2_intersect + 0.22), textcoords='data',
                 fontsize=9.5, color=TEXT_MAIN,
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='#090d16', edgecolor=GOLD, linewidth=1.5),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.12', color=GOLD, lw=1.6),
                 zorder=7)

    ax1.set_xlabel(r'Pulsar Mass $m_1\ (M_\odot)$', fontsize=11, color=TEXT_MAIN, labelpad=8)
    ax1.set_ylabel(r'Companion Mass $m_2\ (M_\odot)$', fontsize=11, color=TEXT_MAIN, labelpad=8)
    ax1.tick_params(colors=TEXT_MUTED, labelsize=10)

    ax1.legend(loc='lower left', frameon=True, facecolor='#090d16', edgecolor=BORDER,
               fontsize=9.2, labelcolor=TEXT_MAIN, framealpha=0.95)

    # =========================================================================
    # RIGHT PANEL: PHYSICAL ANATOMY & CONSTRAINT BREAKDOWN
    # =========================================================================
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor(BG_MAIN)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')

    c1_bullets = [
        r"• Orbit rotates at rate $\dot{\omega} \simeq 4.23^\circ\,\mathrm{yr}^{-1}$.",
        r"• In GR: $\dot{\omega} \propto (m_1 + m_2)^{2/3} \Rightarrow \mathbf{determines\ total\ mass}$.",
        r"• Establishes $m_1 + m_2 = 2.8284\,M_\odot$ (diagonal cyan line)."
    ]
    draw_card(ax2, 0.02, 0.69, 0.96, 0.28, r"Constraint 1: Periastron Advance ($\dot{\omega}$)", CYAN, c1_bullets, border_color='#0284c7')

    c2_bullets = [
        r"• Eccentricity ($e = 0.617$) varies orbital speed and gravity.",
        r"• Dilation + redshift produce $\gamma \simeq 4.29\,\mathrm{ms}$ periodic delay.",
        r"• In GR: $\gamma \propto m_2(m_1 + 2m_2)(m_1 + m_2)^{-4/3}$ (curved rose line)."
    ]
    draw_card(ax2, 0.02, 0.36, 0.96, 0.28, r"Constraint 2: Einstein Delay ($\gamma$)", ROSE, c2_bullets, border_color='#e11d48')

    c3_bullets = [
        r"• Two independent observables solve for two unknown masses.",
        r"• Unique intersection: $m_1 = 1.4414\,M_\odot$, $m_2 = 1.3867\,M_\odot$.",
        r"• Both stars lie near Chandrasekhar limit $\to$ confirms neutron stars."
    ]
    draw_card(ax2, 0.02, 0.03, 0.96, 0.28, r"Result: Weighing the Binary", GOLD, c3_bullets, border_color='#ca8a04')

    plt.savefig(out_path, dpi=250, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"[SUCCESS] Generated {out_path}")
    return out_path


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else None
    generate_mass_mass_diagram(target)
