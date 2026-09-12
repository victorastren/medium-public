#!/usr/bin/env python3
"""
Generate an infographic showing the radial velocity Doppler curve
of PSR B1913+16 across its 7.75-hour orbital period.
Demonstrates the non-sinusoidal Doppler signature of the eccentric orbit (e = 0.617)
compared to a circular orbit (e = 0), highlighting Kepler's 2nd law asymmetry and
the periastron reference epoch T_0.
"""

from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "radial_velocity_doppler_curve.png"

# -------------------------------------------------------------------------
# PHYSICAL & ORBITAL PARAMETERS OF PSR B1913+16
# -------------------------------------------------------------------------
Pb_h = 7.751939106       # Orbital period in hours
Pb_sec = Pb_h * 3600.0    # Period in seconds
e = 0.6171334            # Eccentricity
omega_deg = 178.9        # Argument of periastron (discovery era ~179 deg)
omega = np.radians(omega_deg)
K = 200.8                # Radial velocity semi-amplitude in km/s (from timing)
c_light = 299792.458     # Speed of light in km/s


def solve_kepler(M, ecc):
    """Solve Kepler's equation M = E - e*sin(E) for eccentric anomaly E."""
    E = M.copy()
    for _ in range(20):
        f = E - ecc * np.sin(E) - M
        f_prime = 1.0 - ecc * np.cos(E)
        E -= f / f_prime
    return E


def generate_radial_velocity_curve(out_path=None):
    if out_path is None:
        out_path = DEFAULT_OUT
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    plt.style.use('dark_background')
    fig = plt.figure(figsize=(13.6, 7.6), dpi=250)
    fig.patch.set_facecolor('#0d111a')

    # Main Axes coordinates [left, bottom, width, height]
    ax = fig.add_axes([0.08, 0.11, 0.88, 0.80])
    ax.set_facecolor('#131a29')

    for spine in ax.spines.values():
        spine.set_color('#23304a')
        spine.set_linewidth(1.3)

    # High-resolution time array across exactly one orbit
    t = np.linspace(0.0, Pb_h, 1500)
    M = 2 * np.pi * t / Pb_h
    E = solve_kepler(M, e)
    nu = 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2))

    vr_ecc = K * (np.cos(nu + omega) + e * np.cos(omega))
    vr_circ = K * np.cos(M + omega)

    # Background velocity regions shading
    # Receding zone (> 0): warm amber tint
    ax.axhspan(0, 260, facecolor='#f59e0b', alpha=0.04, zorder=1)
    # Approaching zone (< 0): cool cyan tint
    ax.axhspan(-370, 0, facecolor='#38bdf8', alpha=0.04, zorder=1)

    # Systemic barycenter baseline (vr = 0)
    ax.axhline(0, color='#64748b', ls='-', lw=1.5, alpha=0.85, zorder=2)
    ax.text(0.12, 6, r"System Center-of-Mass Velocity Baseline ($v_r = 0$)",
            color='#94a3b8', fontsize=9.2, fontweight='bold', va='bottom', zorder=3)

    # Subtle background grid
    ax.grid(True, color='#1e293b', ls=':', lw=0.9, alpha=0.7, zorder=1)

    # ---------------------------------------------------------------------
    # PLOT CURVES
    # ---------------------------------------------------------------------
    # 1. Circular Reference Orbit (dashed lavender sinusoid)
    ax.plot(t, vr_circ, color='#a78bfa', ls='--', lw=2.4, alpha=0.80,
            label=r'Hypothetical Circular Orbit ($e = 0$): Symmetric Sinusoid ($\pm 201$ km/s)', zorder=3)

    # 2. Eccentric Observed Orbit (solid vibrant cyan)
    ax.plot(t, vr_ecc, color='#38bdf8', lw=3.6, alpha=0.98,
            label=r'Observed Orbit of PSR B1913+16 ($e = 0.617$): Asymmetric Keplerian Curve', zorder=4)
    # Glow layer
    ax.plot(t, vr_ecc, color='#0284c7', lw=7.5, alpha=0.22, zorder=3)

    # ---------------------------------------------------------------------
    # AXES CONFIGURATION & LIMITS
    # ---------------------------------------------------------------------
    ax.set_xlim(0, Pb_h)
    ax.set_ylim(-370, 255)
    ax.set_xlabel(r"Time from Periastron Passage: $t - T_0$ (hours)", color='#f8fafc', fontsize=11.2, labelpad=9)
    ax.set_ylabel(r"Line-of-Sight Radial Velocity $v_r$ (km/s)", color='#f8fafc', fontsize=11.2, labelpad=9)
    ax.tick_params(colors='#94a3b8', labelsize=10.0)
    ax.xaxis.set_major_locator(MultipleLocator(1.0))
    ax.xaxis.set_minor_locator(MultipleLocator(0.5))
    ax.yaxis.set_major_locator(MultipleLocator(100))
    ax.yaxis.set_minor_locator(MultipleLocator(50))

    # Top Phase axis (Phi = 0.0 to 1.0)
    ax_top = ax.twiny()
    ax_top.set_xlim(0, 1.0)
    ax_top.set_xlabel(r"Orbital Phase: $\Phi = (t - T_0) / P_b$", color='#f8fafc', fontsize=10.8, labelpad=9)
    ax_top.tick_params(colors='#94a3b8', labelsize=10.0)
    ax_top.xaxis.set_major_locator(MultipleLocator(0.2))
    ax_top.xaxis.set_minor_locator(MultipleLocator(0.1))
    for spine in ax_top.spines.values():
        spine.set_color('#23304a')

    # ---------------------------------------------------------------------
    # DOPPLER REGION CALLOUT BADGES
    # ---------------------------------------------------------------------
    ax.text(7.62, 215,
            "RECEDING FROM EARTH ($v_r > 0$)\n"
            r"Doppler Redshift $\rightarrow$ Observed Pulse Period Lengthens",
            color='#f59e0b', fontsize=8.8, fontweight='bold', ha='right', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#261b0c', edgecolor='#f59e0b', alpha=0.9, lw=1.1),
            zorder=6)

    ax.text(4.05, -38,
            "APPROACHING EARTH ($v_r < 0$)\n"
            r"Doppler Blueshift $\rightarrow$ Observed Pulse Period Shortens",
            color='#38bdf8', fontsize=8.8, fontweight='bold', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.38', facecolor='#0d233a', edgecolor='#38bdf8', alpha=0.95, lw=1.1),
            zorder=6)

    # ---------------------------------------------------------------------
    # KEY PHYSICAL ANNOTATIONS
    # ---------------------------------------------------------------------
    # 1. PERIASTRON POINTS & CALLOUT (t = 0 & t = Pb)
    vr_peri = vr_ecc[0]  # approx -325 km/s
    ax.plot([0.0, Pb_h], [vr_peri, vr_peri], 'o', color='#f43f5e', ms=9.5, zorder=6)

    peri_card = (
        r"$\mathbf{PERIASTRON\ PASSAGE\ (Epoch\ T_0,\ \Phi = 0.0)}$" "\n"
        r"• Reference epoch $T_0$: closest approach ($t - T_0 = 0$ h)" "\n"
        r"• Maximum approach velocity: $v_r \approx -325$ km/s" "\n"
        r"• Extreme acceleration & peak speed: $\sim 360$ km/s"
    )
    ax.annotate(peri_card, xy=(0.0, vr_peri), xytext=(0.18, -345),
                arrowprops=dict(arrowstyle="->", color='#f43f5e', lw=1.6),
                color='#f8fafc', fontsize=8.2, linespacing=1.30,
                bbox=dict(boxstyle='round,pad=0.35', facecolor='#2c0d1c', edgecolor='#f43f5e', alpha=0.95, lw=1.2),
                zorder=7)

    # 2. APASTRON POINT & CALLOUT (t = 3.88h, vr = +77.4 km/s)
    t_ap = Pb_h / 2.0
    vr_ap = K * (np.cos(np.pi + omega) + e * np.cos(omega))
    ax.plot(t_ap, vr_ap, 'o', color='#34d399', ms=9.5, zorder=6)

    apa_card = (
        r"$\mathbf{APASTRON\ (t - T_0 = 3.88\ h,\ \Phi = 0.5)}$" "\n"
        r"• Recession plateau: $v_r \approx +77$ km/s" "\n"
        r"• Minimum orbital speed: $\sim 85$ km/s"
    )
    ax.annotate(apa_card, xy=(t_ap, vr_ap), xytext=(t_ap, 160),
                arrowprops=dict(arrowstyle="->", color='#34d399', lw=1.5),
                color='#f8fafc', fontsize=8.0, linespacing=1.20, ha='center', va='top',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#0a291f', edgecolor='#34d399', alpha=0.96, lw=1.2),
                zorder=7)

    # Subtle callout for the circular peak (+201 km/s)
    ax.annotate(r"Circular peak: $+201$ km/s", xy=(t_ap, 201), xytext=(t_ap, 230),
                arrowprops=dict(arrowstyle="->", color='#a78bfa', lw=1.2),
                color='#ddd6fe', fontsize=8.2, fontweight='bold', ha='center',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#1e1435', edgecolor='#a78bfa', alpha=0.85, lw=0.9),
                zorder=7)

    # ---------------------------------------------------------------------
    # TIME DWELL SUMMARY & EXPLANATION CARD
    # ---------------------------------------------------------------------
    dwell_text = (
        r"$\mathbf{ORIGIN\ OF\ THE\ DOPPLER\ ASYMMETRY\ (KEPLER'S\ 2ND\ LAW)}$" "\n\n"
        r"• $\mathbf{Orbital\ Speed\ Contrast}$:" "\n"
        r"   Moving $4.2\times$ faster at periastron ($\sim 360$ km/s) than at apastron" "\n"
        r"   ($\sim 85$ km/s), the pulsar sweeps past periastron in a flash." "\n\n"
        r"• $\mathbf{Asymmetric\ Time\ Allocation}$:" "\n"
        r"   Pulsar spends $\mathbf{5.39\ h\ (69.6\%)}$ receding from Earth ($v_r > 0$)," "\n"
        r"   and only $\mathbf{2.36\ h\ (30.4\%)}$ approaching ($v_r < 0$)." "\n\n"
        r"• $\mathbf{Skewed\ Velocity\ Amplitude}$:" "\n"
        r"   Observed $v_r$ spans from $\mathbf{-325}$ to $\mathbf{+77}$ km/s" "\n"
        r"   (ratio $(1+e)/(1-e) \approx 4.2$), ruling out a circular orbit."
    )
    ax.text(4.05, -170, dwell_text, color='#e2e8f0', fontsize=8.0, va='center', ha='center',
            linespacing=1.25,
            bbox=dict(boxstyle='round,pad=0.45,rounding_size=0.15', facecolor='#0f172a', edgecolor='#334155', lw=1.3, alpha=0.96),
            zorder=6)

    # ---------------------------------------------------------------------
    # LEGEND
    # ---------------------------------------------------------------------
    leg = ax.legend(loc='upper left', bbox_to_anchor=(0.02, 0.96),
                    frameon=True, facecolor='#0f172a', edgecolor='#23304a',
                    fontsize=8.8, labelcolor='#f8fafc')
    leg.get_frame().set_alpha(0.95)
    leg.get_frame().set_linewidth(1.2)

    plt.savefig(out_path, dpi=250, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Generated single-panel Doppler curve at: {out_path}")
    return out_path


# Alias for backwards compatibility
generate_single_panel = generate_radial_velocity_curve

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else None
    generate_radial_velocity_curve(target)
