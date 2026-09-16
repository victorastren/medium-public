#!/usr/bin/env python3
"""
Generate an infographic illustrating the concept of the Osculating Orbit:
- Panel 1: The instantaneous osculating orbit (tangency at planet position r(t) with velocity v(t)).
- Panel 2: The gradual secular evolution of the osculating ellipse over time (a(t), e(t), ϖ(t)).

Styling strictly adheres to:
- Dark theme matching workspace (#0c1017)
- Professional astrophysics color palette
- No global title, descriptive panel subtitles
- Zero overlapping text / callout boxes / legends
- High-contrast, clean typography (no LaTeX in captions/subtexts)
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_IMAGES_DIR = PROJECT_DIR / "images"

# -------------------------------------------------------------------------
# STYLING & PALETTE
# -------------------------------------------------------------------------
plt.style.use('dark_background')

BG_MAIN = '#0a0e17'
BG_PANEL = '#111726'
BORDER = '#222f46'
BORDER_LIGHT = '#334360'

TEXT_TITLE = '#f8fafc'
TEXT_SUB = '#94a3b8'
TEXT_MUTED = '#64748b'

SUN_CORE = '#fef08a'
SUN_GLOW = '#f59e0b'

TRAJ_COLOR = '#38bdf8'      # True perturbed trajectory (cyan)
OSC_COLOR_0 = '#f43f5e'     # Osculating ellipse at t0 (coral)
OSC_COLOR_1 = '#a78bfa'     # Osculating ellipse at t1 (lavender)
OSC_COLOR_2 = '#34d399'     # Osculating ellipse at t2 (emerald)

VEL_COLOR = '#fbbf24'       # Velocity vector (gold)
POS_COLOR = '#60a5fa'       # Position vector (blue)
APSIS_LINE = '#475569'      # Line of apsides


def get_kepler_ellipse(a, e, varpi, n_points=500):
    theta = np.linspace(0, 2 * np.pi, n_points)
    r = a * (1.0 - e**2) / (1.0 + e * np.cos(theta - varpi))
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y


def generate_osculating_orbit_infographic(output_path=None):
    if output_path is None:
        output_path = DEFAULT_IMAGES_DIR / "osculating_orbit_concept.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(15.4, 7.6), dpi=260)
    fig.patch.set_facecolor(BG_MAIN)

    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.10,
                          left=0.03, right=0.97, top=0.95, bottom=0.05)

    box_card_props = dict(boxstyle='round,pad=0.45', facecolor='#0d1422', edgecolor=BORDER_LIGHT, lw=1.0)

    # =========================================================================
    # PANEL 1: INSTANTANEOUS OSCULATING ORBIT
    # =========================================================================
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(BG_PANEL)
    for s in ax1.spines.values():
        s.set_edgecolor(BORDER)
        s.set_linewidth(1.3)

    ax1.set_xlim(-3.1, 2.7)
    ax1.set_ylim(-2.5, 2.5)
    ax1.set_aspect('equal')
    ax1.set_xticks([])
    ax1.set_yticks([])

    # Panel Titles
    ax1.text(0.04, 0.95, "The Instantaneous Osculating Orbit", transform=ax1.transAxes,
             fontsize=13.5, fontweight='bold', color=TEXT_TITLE, va='top')
    ax1.text(0.04, 0.89, "Tangent Keplerian ellipse matching true position and velocity",
             transform=ax1.transAxes, fontsize=10.0, color=TEXT_SUB, va='top')

    # Parameters at t0
    a0 = 2.0
    e0 = 0.35
    varpi0 = np.radians(25)

    # Keplerian Ellipse
    xe0, ye0 = get_kepler_ellipse(a0, e0, varpi0)
    ax1.plot(xe0, ye0, color=OSC_COLOR_0, lw=2.4, alpha=0.95,
             label=r"Osculating Ellipse $\mathcal{O}(t_0)$", zorder=3)

    # Perturbed trajectory passing through t0
    nu_traj = np.linspace(np.radians(-65), np.radians(110), 400)
    r_traj = a0 * (1.0 - e0**2) / (1.0 + e0 * np.cos(nu_traj))
    theta_traj = varpi0 + nu_traj
    x_pert = r_traj * np.cos(theta_traj) + 0.16 * np.sin(2.2 * nu_traj)
    y_pert = r_traj * np.sin(theta_traj) - 0.12 * np.cos(2.2 * nu_traj)
    ax1.plot(x_pert, y_pert, color=TRAJ_COLOR, lw=2.2, linestyle='--',
             label=r"True Perturbed Trajectory $\mathbf{r}(t)$", zorder=4)

    # Tangency point at t0
    nu0 = np.radians(40)
    r0 = a0 * (1.0 - e0**2) / (1.0 + e0 * np.cos(nu0))
    x0 = r0 * np.cos(varpi0 + nu0)
    y0 = r0 * np.sin(varpi0 + nu0)

    # Velocity vector v(t0)
    vx0 = -np.sin(varpi0 + nu0) - e0 * np.sin(varpi0)
    vy0 = np.cos(varpi0 + nu0) + e0 * np.cos(varpi0)
    v_norm = np.hypot(vx0, vy0)
    scale_v = 0.95
    vx_scaled = (vx0 / v_norm) * scale_v
    vy_scaled = (vy0 / v_norm) * scale_v

    # Position vector r(t0)
    ax1.annotate("", xy=(x0, y0), xytext=(0, 0),
                 arrowprops=dict(arrowstyle="->", color=POS_COLOR, lw=2.0, mutation_scale=14), zorder=8)
    ax1.text(x0 * 0.45 - 0.18, y0 * 0.45 + 0.10, r"$\mathbf{r}(t_0)$",
             color=POS_COLOR, fontsize=11.5, fontweight='bold', zorder=9)

    # Tangent velocity vector v(t0)
    ax1.annotate("", xy=(x0 + vx_scaled, y0 + vy_scaled), xytext=(x0, y0),
                 arrowprops=dict(arrowstyle="->", color=VEL_COLOR, lw=2.6, mutation_scale=16), zorder=8)
    ax1.text(x0 + vx_scaled * 0.55 - 0.35, y0 + vy_scaled * 0.55 + 0.18, r"$\mathbf{v}(t_0)$",
             color=VEL_COLOR, fontsize=12.0, fontweight='bold', zorder=9)

    # Planet marker
    ax1.scatter([x0], [y0], color='#ffffff', edgecolor=TRAJ_COLOR, s=110, lw=2.0, zorder=10)
    ax1.text(x0 + 0.14, y0 - 0.12, "Planet at $t_0$", color='#ffffff', fontsize=10.0,
             fontweight='bold', zorder=10)

    # Line of apsides
    x_peri0 = a0 * (1.0 - e0) * np.cos(varpi0)
    y_peri0 = a0 * (1.0 - e0) * np.sin(varpi0)
    x_apo0 = -a0 * (1.0 + e0) * np.cos(varpi0)
    y_apo0 = -a0 * (1.0 + e0) * np.sin(varpi0)
    ax1.plot([x_apo0, x_peri0], [y_apo0, y_peri0], color=APSIS_LINE, lw=1.2, linestyle=':', zorder=2)
    ax1.text(x_peri0 + 0.12, y_peri0 + 0.08, "Perihelion $\\varpi(t_0)$",
             color=TEXT_MUTED, fontsize=8.8, rotation=np.degrees(varpi0), zorder=5)

    # Sun at origin
    sun_glow = plt.Circle((0, 0), 0.18, color=SUN_GLOW, alpha=0.30, zorder=6)
    sun_core = plt.Circle((0, 0), 0.08, color=SUN_CORE, zorder=7)
    ax1.add_patch(sun_glow)
    ax1.add_patch(sun_core)
    ax1.text(0.0, -0.22, "Sun (Focus)", color=SUN_CORE, fontsize=9.5, ha='center', fontweight='bold', zorder=8)

    # Badge: Osculation condition
    ax1.text(0.04, 0.05,
             "Osculation Condition at $t_0$:\n"
             "• $\\mathbf{r}_{\\mathrm{osc}}(t_0) = \\mathbf{r}(t_0)$\n"
             "• $\\mathbf{v}_{\\mathrm{osc}}(t_0) = \\mathbf{v}(t_0)$\n"
             "Unique matching 2-body orbit",
             transform=ax1.transAxes, fontsize=8.6, color='#cbd5e1',
             fontfamily='monospace', va='bottom', bbox=box_card_props, zorder=12)

    leg1 = ax1.legend(loc='lower right', frameon=True, facecolor='#0d1422',
                      edgecolor=BORDER_LIGHT, fontsize=8.6, framealpha=0.95)

    # =========================================================================
    # PANEL 2: SECULAR EVOLUTION OF THE OSCULATING ORBIT
    # =========================================================================
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor(BG_PANEL)
    for s in ax2.spines.values():
        s.set_edgecolor(BORDER)
        s.set_linewidth(1.3)

    ax2.set_xlim(-3.1, 2.7)
    ax2.set_ylim(-2.5, 2.5)
    ax2.set_aspect('equal')
    ax2.set_xticks([])
    ax2.set_yticks([])

    # Panel Titles
    ax2.text(0.04, 0.95, "Secular Evolution of the Osculating Orbit", transform=ax2.transAxes,
             fontsize=13.5, fontweight='bold', color=TEXT_TITLE, va='top')
    ax2.text(0.04, 0.89, "Slow precession of perihelion and secular variation of shape",
             transform=ax2.transAxes, fontsize=10.0, color=TEXT_SUB, va='top')

    # Epoch 0: t0
    xe0, ye0 = get_kepler_ellipse(a0, e0, varpi0)
    ax2.plot(xe0, ye0, color=OSC_COLOR_0, lw=2.2, alpha=0.90,
             label=r"$\mathcal{O}(t_0)$ : $\varpi = 25^\circ,\ e = 0.35$", zorder=3)

    # Epoch 1: t1 = t0 + Delta t
    a1 = 2.01
    e1 = 0.31
    varpi1 = np.radians(65)
    xe1, ye1 = get_kepler_ellipse(a1, e1, varpi1)
    ax2.plot(xe1, ye1, color=OSC_COLOR_1, lw=2.0, alpha=0.85, linestyle='-',
             label=r"$\mathcal{O}(t_1)$ : $\varpi = 65^\circ,\ e = 0.31$", zorder=3)

    # Epoch 2: t2 = t0 + 2*Delta t
    a2 = 1.99
    e2 = 0.39
    varpi2 = np.radians(105)
    xe2, ye2 = get_kepler_ellipse(a2, e2, varpi2)
    ax2.plot(xe2, ye2, color=OSC_COLOR_2, lw=2.0, alpha=0.85, linestyle='-',
             label=r"$\mathcal{O}(t_2)$ : $\varpi = 105^\circ,\ e = 0.39$", zorder=3)

    # Draw lines of apsides
    for a_val, e_val, varpi_val, col in [(a0, e0, varpi0, OSC_COLOR_0),
                                         (a1, e1, varpi1, OSC_COLOR_1),
                                         (a2, e2, varpi2, OSC_COLOR_2)]:
        xp = a_val * (1.0 - e_val) * np.cos(varpi_val)
        yp = a_val * (1.0 - e_val) * np.sin(varpi_val)
        xa = -a_val * (1.0 + e_val) * np.cos(varpi_val)
        ya = -a_val * (1.0 + e_val) * np.sin(varpi_val)
        ax2.plot([xa, xp], [ya, yp], color=col, lw=1.2, linestyle=':', alpha=0.65, zorder=2)
        ax2.scatter([xp], [yp], color=col, s=36, zorder=5)

    # Precession arc showing d(varpi)/dt > 0
    arc_rad = 1.05
    arc_angles = np.linspace(varpi0, varpi2, 100)
    ax2.plot(arc_rad * np.cos(arc_angles), arc_rad * np.sin(arc_angles),
             color=VEL_COLOR, lw=1.8, linestyle='-', zorder=6)

    # Arrowhead on precession arc
    arrow_tip_x = arc_rad * np.cos(varpi2)
    arrow_tip_y = arc_rad * np.sin(varpi2)
    ax2.annotate("", xy=(arrow_tip_x, arrow_tip_y),
                 xytext=(arc_rad * np.cos(varpi2 - 0.08), arc_rad * np.sin(varpi2 - 0.08)),
                 arrowprops=dict(arrowstyle="->", color=VEL_COLOR, lw=2.0, mutation_scale=14), zorder=7)

    # Perihelion Precession Badge
    ax2.text(1.20, 1.45, "Perihelion Precession\nΔϖ > 0 (Apsidal drift)",
             color=VEL_COLOR, fontsize=9.2, fontweight='bold', ha='center', va='center',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#0d1422', edgecolor=BORDER_LIGHT, lw=0.9), zorder=8)

    # Sun at focus
    sun_glow2 = plt.Circle((0, 0), 0.18, color=SUN_GLOW, alpha=0.30, zorder=6)
    sun_core2 = plt.Circle((0, 0), 0.08, color=SUN_CORE, zorder=7)
    ax2.add_patch(sun_glow2)
    ax2.add_patch(sun_core2)
    ax2.text(0.0, -0.22, "Sun (Focus)", color=SUN_CORE, fontsize=9.5, ha='center', fontweight='bold', zorder=8)

    # Compact explanatory card (bottom left)
    ax2.text(0.04, 0.05,
             "Slowly Evolving Elements:\n"
             "• a(t) : size (nearly constant)\n"
             "• e(t) : shape (bounded variation)\n"
             "• ϖ(t) : orientation (precession)",
             transform=ax2.transAxes, fontsize=8.6, color='#cbd5e1',
             fontfamily='monospace', va='bottom', bbox=box_card_props, zorder=12)

    leg2 = ax2.legend(loc='lower right', frameon=True, facecolor='#0d1422',
                      edgecolor=BORDER_LIGHT, fontsize=8.6, framealpha=0.95)

    plt.savefig(output_path, dpi=260, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()

    print(f"[OK] Successfully saved {output_path}")
    return output_path

create_osculating_orbit_infographic = generate_osculating_orbit_infographic

if __name__ == "__main__":
    generate_osculating_orbit_infographic()
