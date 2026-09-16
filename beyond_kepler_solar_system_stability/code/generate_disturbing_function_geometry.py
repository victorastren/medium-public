#!/usr/bin/env python3
"""
Generate Figure A: Geometry of the Disturbing Function
Standalone full-width visualization for Section 2 (Perturbing a Keplerian Orbit):
Shows the Sun at the origin, perturbed planet r, perturbing planet r', separation Delta,
visibly eccentric orbits with perihelion directions, direct attraction, and acceleration of the Sun.

Optimized for 680px Medium reading width with dark astrophysics aesthetic.
"""

from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# -------------------------------------------------------------------------
# GLOBAL AESTHETICS & PALETTE (Astrophysics Dark Theme)
# -------------------------------------------------------------------------
BG_COLOR      = "#0a0e17"       # Deep cosmic dark
BG_PANEL      = "#111726"       # Panel background
BORDER        = "#1e293b"       # Subtle panel border
BORDER_LIGHT  = "#334155"       # Card border
TEXT_TITLE    = "#f8fafc"       # Bright white
TEXT_SUB      = "#94a3b8"       # Cool slate grey
TEXT_BODY     = "#cbd5e1"       # Light grey text

SUN_COLOR     = "#fef08a"       # Sun core
SUN_GLOW      = "#f59e0b"       # Sun corona
PLANET_COLOR  = "#38bdf8"       # Perturbed planet (cyan)
PERT_COLOR    = "#fbbf24"       # Perturber (Jupiter-gold)
ORBIT_INNER   = "#0284c7"       # Inner orbit path
ORBIT_OUTER   = "#a78bfa"       # Outer orbit path
DELTA_COLOR   = "#f43f5e"       # Separation vector Delta (rose/coral)

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'mathtext.fontset': 'dejavusans',
    'text.color': TEXT_BODY,
    'axes.labelcolor': TEXT_BODY,
    'xtick.color': TEXT_SUB,
    'ytick.color': TEXT_SUB,
})

def get_ellipse_coords(a, e, varpi_rad, num_points=700):
    theta = np.linspace(0, 2 * np.pi, num_points)
    r = a * (1 - e**2) / (1 + e * np.cos(theta - varpi_rad))
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

def get_point_on_orbit(a, e, varpi_rad, true_anomaly_rad):
    r = a * (1 - e**2) / (1 + e * np.cos(true_anomaly_rad))
    theta = varpi_rad + true_anomaly_rad
    return r * np.cos(theta), r * np.sin(theta)

def create_disturbing_function_geometry(output_path=None):
    if output_path is None:
        output_path = DEFAULT_IMAGES_DIR / "disturbing_function_geometry.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(11.5, 7.8), dpi=280, facecolor=BG_COLOR)

    ax = fig.add_axes([0.06, 0.08, 0.88, 0.81], facecolor=BG_PANEL)
    ax.set_aspect('equal')
    for s in ax.spines.values():
        s.set_edgecolor(BORDER)
        s.set_linewidth(1.3)
    ax.set_xticks([])
    ax.set_yticks([])

    # -------------------------------------------------------------------------
    # ORBITS (Visibly, mildly eccentric to define distinct perihelia)
    # -------------------------------------------------------------------------
    # Inner planet (perturbed): a=1.50, e=0.35, perihelion oriented at 22 deg
    a1, e1, varpi1_deg = 1.50, 0.35, 22.0
    varpi1 = np.radians(varpi1_deg)
    x_orb1, y_orb1 = get_ellipse_coords(a1, e1, varpi1)

    # Outer planet (perturber): a=2.80, e=0.26, perihelion oriented at 145 deg
    a2, e2, varpi2_deg = 2.80, 0.26, 145.0
    varpi2 = np.radians(varpi2_deg)
    x_orb2, y_orb2 = get_ellipse_coords(a2, e2, varpi2)

    # Draw elliptical paths
    ax.plot(x_orb1, y_orb1, color=PLANET_COLOR, lw=1.8, ls='--', alpha=0.72, zorder=3,
            label="Inner orbit (perturbed)")
    ax.plot(x_orb2, y_orb2, color=ORBIT_OUTER, lw=1.8, ls='--', alpha=0.68, zorder=3,
            label="Outer orbit (perturber)")

    # -------------------------------------------------------------------------
    # PERIHELION LINES (APSIDES)
    # -------------------------------------------------------------------------
    # Inner orbit perihelion
    r_peri1 = a1 * (1 - e1)
    x_p1, y_p1 = r_peri1 * np.cos(varpi1), r_peri1 * np.sin(varpi1)
    ax.plot([0, x_p1 * 1.35], [0, y_p1 * 1.35], color='#0284c7', ls=':', lw=1.2, alpha=0.75, zorder=2)
    ax.text(x_p1 * 1.38, y_p1 * 1.38, r"Perihelion $\varpi$", color='#38bdf8', fontsize=9.2,
            va='bottom', ha='left', style='italic', fontweight='bold')

    # Outer orbit perihelion
    r_peri2 = a2 * (1 - e2)
    x_p2, y_p2 = r_peri2 * np.cos(varpi2), r_peri2 * np.sin(varpi2)
    ax.plot([0, x_p2 * 1.15], [0, y_p2 * 1.15], color='#8b5cf6', ls=':', lw=1.2, alpha=0.75, zorder=2)
    ax.text(x_p2 * 1.18, y_p2 * 1.18 + 0.12, r"Perihelion $\varpi'$", color='#c084fc', fontsize=9.2,
            va='bottom', ha='right', style='italic', fontweight='bold')

    # -------------------------------------------------------------------------
    # PLANETARY POSITIONS
    # -------------------------------------------------------------------------
    # Planet at true anomaly ~ 50 deg
    xp, yp = get_point_on_orbit(a1, e1, varpi1, np.radians(50.0))
    # Perturber at true anomaly ~ -28 deg relative to varpi2 (in upper left)
    xpert, ypert = get_point_on_orbit(a2, e2, varpi2, np.radians(-28.0))

    # Sun at origin (0, 0)
    for rad, alpha in [(0.32, 0.08), (0.20, 0.18), (0.11, 0.40)]:
        ax.add_patch(plt.Circle((0, 0), rad, color=SUN_GLOW, alpha=alpha, zorder=5))
    ax.add_patch(plt.Circle((0, 0), 0.075, color=SUN_COLOR, zorder=6))
    ax.text(0.0, -0.26, r"Sun ($M_\odot$)", color=SUN_COLOR, fontsize=10.2,
            fontweight='bold', ha='center', va='top', zorder=7)

    # Position vector r (Sun -> planet)
    ax.annotate("", xy=(xp, yp), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=PLANET_COLOR, lw=2.0, mutation_scale=15), zorder=6)
    ax.text(xp * 0.42 - 0.14, yp * 0.42 + 0.08, r"$\mathbf{r}$",
            color=PLANET_COLOR, fontsize=13.0, fontweight='bold', zorder=7)

    # Position vector r' (Sun -> perturber)
    ax.annotate("", xy=(xpert, ypert), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=ORBIT_OUTER, lw=2.0, mutation_scale=15), zorder=6)
    ax.text(xpert * 0.48 - 0.18, ypert * 0.48 - 0.06, r"$\mathbf{r}'$",
            color=ORBIT_OUTER, fontsize=13.0, fontweight='bold', zorder=7)

    # Separation vector Delta = r' - r
    ax.annotate("", xy=(xpert, ypert), xytext=(xp, yp),
                arrowprops=dict(arrowstyle="-|>", color=DELTA_COLOR, lw=2.4, mutation_scale=17, ls='-'), zorder=7)
    mid_x = (xp + xpert) / 2
    mid_y = (yp + ypert) / 2
    ax.text(mid_x + 0.05, mid_y + 0.18, r"$\mathbf{\Delta} = \mathbf{r}' - \mathbf{r}$",
            color=DELTA_COLOR, fontsize=11.2, fontweight='bold', ha='center',
            bbox=dict(boxstyle='round,pad=0.28', facecolor='#18060c', edgecolor=DELTA_COLOR, lw=1.0, alpha=0.95),
            zorder=8)

    # Planet marker & label
    ax.add_patch(plt.Circle((xp, yp), 0.090, color='#0284c7', zorder=8))
    ax.add_patch(plt.Circle((xp, yp), 0.055, color=PLANET_COLOR, zorder=9))
    ax.text(xp + 0.12, yp + 0.22, "Perturbed Planet\n($m$, position $\\mathbf{r}$)",
            color=PLANET_COLOR, fontsize=9.2, fontweight='bold', va='bottom', ha='left', zorder=9)

    # Perturber marker & label
    ax.add_patch(plt.Circle((xpert, ypert), 0.120, color='#b45309', zorder=8))
    ax.add_patch(plt.Circle((xpert, ypert), 0.075, color=PERT_COLOR, zorder=9))
    ax.text(xpert - 0.16, ypert + 0.18, "Perturbing Planet\n($m'$, position $\\mathbf{r}'$)",
            color=PERT_COLOR, fontsize=9.2, fontweight='bold', va='bottom', ha='right', zorder=9)

    # -------------------------------------------------------------------------
    # DIRECT AND INDIRECT GRAVITATIONAL FORCES
    # -------------------------------------------------------------------------
    # Direct force on planet towards perturber
    dir_dx = (xpert - xp)
    dir_dy = (ypert - yp)
    dist = np.hypot(dir_dx, dir_dy)
    u_dx = dir_dx / dist
    u_dy = dir_dy / dist
    ax.annotate("", xy=(xp + u_dx * 0.80, yp + u_dy * 0.80), xytext=(xp, yp),
                arrowprops=dict(arrowstyle="-|>", color='#fb7185', lw=2.6, mutation_scale=14), zorder=8)
    ax.text(xp + u_dx * 0.45 - 0.15, yp + u_dy * 0.45 - 0.16,
            "Direct attraction on $m$\n$\\propto +\\frac{\\mathbf{r}' - \\mathbf{r}}{|\\mathbf{r}' - \\mathbf{r}|^3}$",
            color='#fecdd3', fontsize=8.6, va='top', ha='right',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#200710', edgecolor='#f43f5e', lw=0.9, alpha=0.92),
            zorder=9)

    # Indirect force: acceleration of Sun towards perturber
    s_dx = xpert
    s_dy = ypert
    s_dist = np.hypot(s_dx, s_dy)
    us_dx = s_dx / s_dist
    us_dy = s_dy / s_dist
    ax.annotate("", xy=(us_dx * 0.65, us_dy * 0.65), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color='#f59e0b', lw=2.2, mutation_scale=13), zorder=8)
    ax.text(us_dx * 0.50 - 0.20, us_dy * 0.50 - 0.16,
            "Sun's acceleration\n$\\propto +\\frac{\\mathbf{r}'}{{r'}^3}$",
            color='#fef08a', fontsize=8.6, va='top', ha='right',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#1f1505', edgecolor='#f59e0b', lw=0.9, alpha=0.92),
            zorder=9)

    # -------------------------------------------------------------------------
    # EXPLANATORY BOTTOM CARD (Retaining the physical formula)
    # -------------------------------------------------------------------------
    bot_card = (
        r"$\mathbf{The\ Heliocentric\ Disturbing\ Function}$:" "\n"
        r"$\mathcal{R} = G m' \left( \frac{1}{|\mathbf{r}' - \mathbf{r}|} - \frac{\mathbf{r} \cdot \mathbf{r}'}{{r'}^3} \right) = \mathcal{R}_{\mathrm{direct}} + \mathcal{R}_{\mathrm{indirect}}$" "\n"
        r"• In heliocentric coordinates, the perturbation includes the direct gravitational attraction on the planet" "\n"
        r"  and the indirect term arising from the acceleration of the Sun by the perturber."
    )
    ax.text(0.04, 0.035, bot_card, transform=ax.transAxes,
            fontsize=9.2, color='#e2e8f0', va='bottom', ha='left',
            bbox=dict(boxstyle='round,pad=0.45,rounding_size=0.25',
                      facecolor='#0a1322', edgecolor=BORDER_LIGHT, lw=1.1, alpha=0.95), zorder=10)

    # Coordinate boundaries
    ax.set_xlim(-3.6, 3.4)
    ax.set_ylim(-2.8, 3.5)

    # -------------------------------------------------------------------------
    # GLOBAL HEADER
    # -------------------------------------------------------------------------
    fig.text(0.06, 0.965, "Geometry of the Disturbing Function",
             fontsize=14.5, fontweight='bold', color=TEXT_TITLE, va='top')
    fig.text(0.06, 0.932,
             "Heliocentric coordinates, mutual planetary separation, and differential gravitational attraction",
             fontsize=10.0, color=TEXT_SUB, va='top')

    plt.savefig(output_path, dpi=280, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Successfully created: {output_path}")

    return output_path

generate_disturbing_function_geometry = create_disturbing_function_geometry

if __name__ == "__main__":
    create_disturbing_function_geometry()
