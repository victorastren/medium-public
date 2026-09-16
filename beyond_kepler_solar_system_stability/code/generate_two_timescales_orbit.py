#!/usr/bin/env python3
"""
Generate Infographic: Two Timescales in a Single Orbit (Standalone Full-Width)
Visualizing the fundamental dynamical separation in celestial mechanics for Section 1:
Fast Keplerian revolution (n) vs. Slow Secular Apsidal Precession (g << n).
Optimized for single-panel full-width display at 680px Medium reading width.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images" 

# -------------------------------------------------------------------------
# GLOBAL AESTHETICS & PALETTE (Astrophysics Dark Theme)
# -------------------------------------------------------------------------
BG_COLOR    = "#0a0e17"       # Deep cosmic dark
BG_PANEL    = "#111726"       # Panel background
BORDER      = "#1e293b"       # Subtle border
BORDER_LIGHT= "#334155"       # Card border
TEXT_TITLE  = "#f8fafc"       # Bright white
TEXT_SUB    = "#94a3b8"       # Cool slate grey
TEXT_BODY   = "#cbd5e1"       # Light grey text

SUN_CORE    = "#fbbf24"       # Warm yellow/gold
SUN_GLOW    = "#f59e0b"       # Amber glow
FAST_COLOR  = "#38bdf8"       # Cyan for fast motion (n)
FAST_TRAIL  = "#0284c7"       # Cyan motion trail
SLOW_COLOR  = "#f43f5e"       # Rose / coral for slow precession (g)
SLOW_ACCENT = "#fb7185"       # Lighter coral
GOLD_ACCENT = "#fbbf24"       # Highlight gold

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'mathtext.fontset': 'dejavusans',
    'text.color': TEXT_BODY,
    'axes.labelcolor': TEXT_BODY,
    'xtick.color': TEXT_SUB,
    'ytick.color': TEXT_SUB,
})

def create_two_timescales_orbit(output_path=None):
    if output_path is None:
        output_path = DEFAULT_IMAGES_DIR / "two_timescales_orbit.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = DEFAULT_IMAGES_DIR / "two_timescales_orbit.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # High resolution wide single-panel format: 11.5 x 6.8 inches
    fig, ax = plt.subplots(figsize=(11.5, 6.8), dpi=280, facecolor=BG_COLOR)
    ax.set_facecolor(BG_PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
        spine.set_linewidth(1.3)

    ax.set_xlim(-3.0, 3.0)
    ax.set_ylim(-2.35, 2.15)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])

    # Header Titles (Clear, uncluttered)
    ax.text(0.04, 0.95, "Two Timescales in a Planetary Orbit", transform=ax.transAxes,
            fontsize=15.0, fontweight='bold', color=TEXT_TITLE, va='top')
    ax.text(0.04, 0.88, r"Fast Keplerian revolution ($n$) vs. slow secular precession of the orbit ($g \ll n$)",
            transform=ax.transAxes, fontsize=10.5, color=TEXT_SUB, va='top')

    # Ellipse generator
    def get_ellipse(a, e, varpi, n_pts=360):
        nu = np.linspace(0, 2*np.pi, n_pts)
        r = a * (1.0 - e**2) / (1.0 + e * np.cos(nu))
        phi = nu + varpi
        return r * np.cos(phi), r * np.sin(phi)

    # Scaled parameters so entire orbit family stays comfortably within panel borders
    a = 1.58
    e = 0.42
    varpi_0 = np.radians(12.0)
    varpi_final = np.radians(68.0)

    # 1. Ghost precessed ellipses showing secular apsidal drift
    precessions = [
        (np.radians(28.0), 0.22, SLOW_COLOR, ':'),
        (np.radians(46.0), 0.42, SLOW_COLOR, '--'),
        (varpi_final,      0.75, SLOW_COLOR, '-')
    ]
    for d_varpi, alpha_val, col, ls_val in precessions:
        xg, yg = get_ellipse(a, e, d_varpi)
        ax.plot(xg, yg, color=col, lw=1.3, ls=ls_val, alpha=alpha_val, zorder=3)
        # Perihelion dot
        r_per = a * (1.0 - e)
        ax.plot(r_per * np.cos(d_varpi), r_per * np.sin(d_varpi),
                marker='o', markersize=4.0, color=col, alpha=alpha_val, zorder=4)

    # 2. Base current orbit at t0
    x0, y0 = get_ellipse(a, e, varpi_0)
    ax.plot(x0, y0, color=FAST_COLOR, lw=2.4, ls='-', zorder=5, label=r"Current orbit at $t_0$")

    # Major axes (Lines of Apsides)
    r_per0 = a * (1.0 - e)
    r_apo0 = a * (1.0 + e)
    r_axis_ext = 1.38
    r_axis_ext_0 = 1.22
    ax.plot([-r_apo0 * np.cos(varpi_0), r_axis_ext_0 * np.cos(varpi_0)],
            [-r_apo0 * np.sin(varpi_0), r_axis_ext_0 * np.sin(varpi_0)],
            color='#475569', lw=1.2, ls=':', zorder=3)

    ax.plot([-r_apo0 * np.cos(varpi_final), r_axis_ext * np.cos(varpi_final)],
            [-r_apo0 * np.sin(varpi_final), r_axis_ext * np.sin(varpi_final)],
            color=SLOW_COLOR, lw=1.2, ls=':', alpha=0.75, zorder=3)

    # 3. Sun at Focus
    sun_glow = plt.Circle((0, 0), 0.17, color=SUN_GLOW, alpha=0.30, zorder=7)
    sun_core = plt.Circle((0, 0), 0.075, color=SUN_CORE, zorder=8)
    ax.add_patch(sun_glow)
    ax.add_patch(sun_core)
    ax.text(0.0, -0.20, "Sun (Focus)", color=SUN_CORE, fontsize=9.5, ha='center', fontweight='bold', zorder=9)

    # 4. Fast Motion: Planet & Trajectory Trail
    nu_pl = np.radians(115.0)
    nu_trail = np.linspace(np.radians(50.0), nu_pl, 60)
    r_trail = a * (1.0 - e**2) / (1.0 + e * np.cos(nu_trail))
    phi_trail = nu_trail + varpi_0
    xt = r_trail * np.cos(phi_trail)
    yt = r_trail * np.sin(phi_trail)
    ax.plot(xt, yt, color=FAST_COLOR, lw=4.5, alpha=0.35, zorder=6)

    # Direction arrow on trail
    nu_arr = np.radians(82.0)
    r_arr = a * (1.0 - e**2) / (1.0 + e * np.cos(nu_arr))
    xa = r_arr * np.cos(nu_arr + varpi_0)
    ya = r_arr * np.sin(nu_arr + varpi_0)
    nu_arr_next = nu_arr + 0.06
    r_arr_next = a * (1.0 - e**2) / (1.0 + e * np.cos(nu_arr_next))
    xa_n = r_arr_next * np.cos(nu_arr_next + varpi_0)
    ya_n = r_arr_next * np.sin(nu_arr_next + varpi_0)
    ax.annotate('', xy=(xa_n, ya_n), xytext=(xa, ya),
                arrowprops=dict(arrowstyle='->', color=FAST_COLOR, lw=2.2, mutation_scale=15), zorder=7)

    # Planet coordinates
    r_pl = a * (1.0 - e**2) / (1.0 + e * np.cos(nu_pl))
    phi_pl = nu_pl + varpi_0
    xp = r_pl * np.cos(phi_pl)
    yp = r_pl * np.sin(phi_pl)

    # Velocity Vector
    dr_dnu = a * (1.0 - e**2) * e * np.sin(nu_pl) / (1.0 + e * np.cos(nu_pl))**2
    v_x = dr_dnu * np.cos(phi_pl) - r_pl * np.sin(phi_pl)
    v_y = dr_dnu * np.sin(phi_pl) + r_pl * np.cos(phi_pl)
    v_mag = np.hypot(v_x, v_y)
    vx_u, vy_u = v_x / v_mag, v_y / v_mag

    ax.annotate('', xy=(xp + vx_u * 0.65, yp + vy_u * 0.65), xytext=(xp, yp),
                arrowprops=dict(arrowstyle='->', color=FAST_COLOR, lw=2.5, mutation_scale=16), zorder=9)
    ax.text(xp + vx_u * 0.65 - 0.20, yp + vy_u * 0.65 + 0.12,
            r"$\mathbf{v}_{\mathrm{orb}}$", color=FAST_COLOR,
            fontsize=12.0, fontweight='bold', zorder=10)

    # Planet circle
    pl_glow = plt.Circle((xp, yp), 0.13, color=FAST_COLOR, alpha=0.45, zorder=9)
    pl_core = plt.Circle((xp, yp), 0.065, color='#ffffff', zorder=10)
    ax.add_patch(pl_glow)
    ax.add_patch(pl_core)
    ax.text(xp + 0.14, yp + 0.08, "Planet", color='#ffffff', fontsize=10.5, fontweight='bold', zorder=11)

    # Fast Motion Info Card (Left)
    fast_card = (
        r"$\mathbf{Fast\ Orbital\ Motion}$:" "\n"
        r"• Mean motion: $n = \dot{M} = \frac{2\pi}{P_{\mathrm{orb}}}$" "\n"
        r"• Period: $\tau_{\mathrm{fast}} \sim \text{months to years}$" "\n"
        r"• Rapid cycle along instantaneous ellipse"
    )
    ax.text(-2.80, 0.70, fast_card, color='#e0f2fe', fontsize=9.2, va='top', zorder=11,
            bbox=dict(boxstyle='round,pad=0.50,rounding_size=0.3',
                      facecolor='#06192a', edgecolor=FAST_COLOR, lw=1.2, alpha=0.95))

    # 5. Slow Motion: Perihelion Precession Arc
    arc_rad = 1.18
    arc_th = np.linspace(varpi_0, varpi_final, 50)
    ax.plot(arc_rad * np.cos(arc_th), arc_rad * np.sin(arc_th), color=SLOW_ACCENT, lw=2.2, zorder=6)

    # Precession Arrowhead
    th_tip = varpi_final
    th_base = varpi_final - 0.05
    ax.annotate('', xy=(arc_rad * np.cos(th_tip), arc_rad * np.sin(th_tip)),
                xytext=(arc_rad * np.cos(th_base), arc_rad * np.sin(th_base)),
                arrowprops=dict(arrowstyle='->', color=SLOW_ACCENT, lw=2.5, mutation_scale=16), zorder=7)

    # Slow Precession Info Card (Right)
    slow_card = (
        r"$\mathbf{Slow\ Apsidal\ Precession}$:" "\n"
        r"• Secular frequency: $g = \dot{\varpi} \ll n$" "\n"
        r"• Timescale: $\tau_{\mathrm{sec}} \sim 10^4 - 10^6\ \text{years}$" "\n"
        r"• Slow drift of perihelion $\varpi(t)$"
    )
    ax.text(1.35, 0.45, slow_card, color='#ffe4e6', fontsize=9.2, va='center', zorder=11,
            bbox=dict(boxstyle='round,pad=0.50,rounding_size=0.3',
                      facecolor='#260814', edgecolor=SLOW_ACCENT, lw=1.2, alpha=0.95))

    # Perihelion Angle Labels
    ax.text(r_per0 * np.cos(varpi_0) + 0.05, r_per0 * np.sin(varpi_0) - 0.18,
            r"$\varpi(t_0)$", color=TEXT_SUB, fontsize=9.5, fontweight='bold', zorder=12)
    # Position varpi(t0 + Delta t) nicely above the red arrow/arc
    ax.text(0.68, 1.22, r"$\varpi(t_0 + \Delta t)$",
            color=SLOW_ACCENT, fontsize=9.5, fontweight='bold', ha='center', zorder=12)

    # Bottom Architectural Note (Replaces Hamiltonian box with physical takeaway)
    summary_card = (
        r"$\mathbf{Dynamical\ Timescale\ Separation}$:" r"$\quad \tau_{\mathrm{sec}} \gg \tau_{\mathrm{fast}}\quad (g \ll n)$" "\n"
        r"The planet rapidly orbits the Sun on an ellipse whose orientation and shape drift only over millennia."
    )
    ax.text(0.04, 0.04, summary_card, transform=ax.transAxes,
            fontsize=9.0, color='#cbd5e1', va='bottom',
            bbox=dict(boxstyle='round,pad=0.45,rounding_size=0.3',
                      facecolor='#0d1422', edgecolor=BORDER_LIGHT, lw=1.1, alpha=0.95), zorder=12)

    # Save output
    plt.subplots_adjust(left=0.03, right=0.97, top=0.95, bottom=0.05)
    plt.savefig(output_path, dpi=280, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Successfully created standalone full-width: {output_path}")
    return output_path

generate_two_timescales_orbit = create_two_timescales_orbit

if __name__ == "__main__":
    create_two_timescales_orbit()
