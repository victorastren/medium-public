#!/usr/bin/env python3
r"""
Create geometry diagram for the Gravitational
Deflection of Starlight by the Sun (Einstein's General Relativistic prediction).

Tailored for Medium (680px width) with maximum visual legibility:
- Vibrant, high-contrast palette (replaces low-contrast grey with bright sky blue and warm yellow).
- Large bold typography calibrated for effortless reading at Medium 680px width and mobile screens.
- Two prominent equations side-by-side in lower panel:
    δθ(b) = (4GM☉)/(c²b)   and   δθ(R☉) ≈ 1.75″
- Clear, bright subtitles:
    "General deflection (arbitrary b)" (bright sky-blue #7dd3fc)
    "Solar limb grazing ray (b = R☉)" (bright warm-yellow #fde047)
- Simplified header: "GENERAL-RELATIVISTIC DEFLECTION"
- Explicit labels:
    "Path without gravitational deflection"
    "Back-projected line of sight"
- Prominent apparent-position construction: star displaced radially AWAY from the Sun.
- 2-line schematic disclaimer in bottom-left in bright sky blue:
    "* Schematic diagram (not to scale)"
    "  Deflection angle and curvature exaggerated for clarity"
- Generates standard Medium width (680px) and 2x Retina (2400x1170).
"""

import os
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arc, Rectangle
import matplotlib.patheffects as pe
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT_DIR = PROJECT_DIR / "images"

def generate_deflection_diagram(out_dir=None, filename_prefix="light_deflection_geometry"):
    if out_dir is None:
        out_dir = DEFAULT_OUT_DIR
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_2x = out_dir / f"{filename_prefix}_2x.png"
    out_1x = out_dir / f"{filename_prefix}.png"
    
    # Reduced vertical gaps by half: figsize 12 x 5.85 (output 2400x1170 and 680x331)
    fig = plt.figure(figsize=(12, 5.85), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    
    bg_color = '#0b0f19'  # Cosmic dark slate
    ax.set_facecolor(bg_color)
    fig.patch.set_facecolor(bg_color)
    
    # Coordinate limits with generous margins
    x_min, x_max = -8.2, 8.2
    y_min, y_max = -3.2, 3.8
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Subtle background starfield (avoiding text regions)
    np.random.seed(101)
    bg_x = np.random.uniform(x_min, x_max, 115)
    bg_y = np.random.uniform(y_min, y_max, 115)
    bg_s = np.random.uniform(1.5, 9, 115)
    bg_a = np.random.uniform(0.12, 0.40, 115)
    mask = ~((np.abs(bg_x) < 2.4) & (bg_y < 1.4)) & \
           ~((bg_x > -1.2) & (bg_y < -1.2)) & \
           ~((bg_x < -0.2) & (bg_y > 2.2)) & \
           ~((bg_x < -2.0) & (bg_y < -2.4))  # mask out disclaimer region
    ax.scatter(bg_x[mask], bg_y[mask], s=bg_s[mask], color='#ffffff', alpha=bg_a[mask], zorder=1)
    
    # Path effects for crisp text readability at 680px
    pe_text = [pe.withStroke(linewidth=3.6, foreground='#0b0f19')]
    pe_bold = [pe.withStroke(linewidth=4.4, foreground='#0b0f19')]
    
    # -------------------------------------------------------------------------
    # GEOMETRY DEFINITION
    # -------------------------------------------------------------------------
    sun_x, sun_y = 0.0, -0.45
    r_sun = 1.15
    
    # Exaggerated deflection angle for visual clarity: 9.6 degrees
    alpha_deg = 9.6
    alpha = np.radians(alpha_deg)
    
    x_star = -5.35
    y_star_true = 1.35
    
    d = 2.10
    
    def slope(x):
        return -alpha * 0.5 * (1.0 + x / np.sqrt(x**2 + d**2))
    
    def y_func(x):
        return y_star_true - alpha * 0.5 * ((x - x_star) + np.sqrt(x**2 + d**2) - np.sqrt(x_star**2 + d**2))
    
    x_E = 5.50
    y_E = y_func(x_E)
    m_E = slope(x_E)
    
    x_vals = np.linspace(x_star, x_E, 500)
    y_vals = y_func(x_vals)
    
    y_closest = y_func(0.0)
    b = y_closest - sun_y  # impact parameter
    
    # Back-projected line of sight (straight tangent extending backward from observer)
    y_star_app = y_E + m_E * (x_star - x_E)
    x_app_line = np.linspace(x_star, x_E, 300)
    y_app_line = y_E + m_E * (x_app_line - x_E)
    
    # Undeviated path (continuation of incoming straight ray forward past the Sun)
    x_undev_line = np.linspace(x_star, 4.4, 300)
    y_undev_line = np.full_like(x_undev_line, y_star_true)
    
    # -------------------------------------------------------------------------
    # 1. THE SUN (Glowing celestial disc with corona)
    # -------------------------------------------------------------------------
    for r_scale, alpha_val in [(2.4, 0.04), (1.8, 0.08), (1.4, 0.16), (1.18, 0.25)]:
        corona = Circle((sun_x, sun_y), r_sun * r_scale, facecolor='#f59e0b', edgecolor='none',
                        alpha=alpha_val, zorder=2)
        ax.add_patch(corona)
    
    sun_base = Circle((sun_x, sun_y), r_sun, facecolor='#f59e0b', edgecolor='#fbbf24',
                      linewidth=2.2, zorder=3)
    ax.add_patch(sun_base)
    sun_core = Circle((sun_x, sun_y), r_sun * 0.86, facecolor='#fbbf24', edgecolor='none',
                      alpha=0.7, zorder=4)
    ax.add_patch(sun_core)
    sun_center = Circle((sun_x, sun_y), r_sun * 0.60, facecolor='#fef08a', edgecolor='none',
                        alpha=0.9, zorder=4)
    ax.add_patch(sun_center)
    
    ax.scatter([sun_x], [sun_y], color='#b45309', s=32, zorder=5)
    
    # Sun label: centered cleanly in lower hemisphere of core below center dot (no text collision)
    ax.text(sun_x, sun_y - 0.40, "SUN\nMass M☉", color='#78350f', fontsize=12.2,
            fontweight='bold', ha='center', va='center', zorder=8, linespacing=1.1)
    
    # Radius R_☉ dimension arrow: horizontal East (0 deg) forming orthogonal frame with vertical b
    rx_limb = sun_x + r_sun
    ry_limb = sun_y
    ax.annotate('', xy=(rx_limb, ry_limb), xytext=(sun_x, sun_y),
                arrowprops=dict(arrowstyle='<->', color='#d97706', lw=2.2), zorder=7)
    pe_sun_label = [pe.withStroke(linewidth=2.8, foreground='#fef08a')]
    ax.text((sun_x + rx_limb)/2, sun_y + 0.17, "R☉",
            color='#78350f', fontsize=12.2, fontweight='bold', zorder=9,
            path_effects=pe_sun_label, ha='center', va='center')
    
    # -------------------------------------------------------------------------
    # 2. IMPACT PARAMETER b (Enlarged font & bright accents)
    # -------------------------------------------------------------------------
    ax.plot([sun_x, sun_x], [sun_y, y_closest], color='#7dd3fc', linestyle=':', linewidth=1.6,
            alpha=0.85, zorder=5)
    ax.annotate('', xy=(sun_x, y_closest), xytext=(sun_x, sun_y),
                arrowprops=dict(arrowstyle='<->', color='#38bdf8', lw=2.2), zorder=6)
    ax.scatter([sun_x], [y_closest], color='#38bdf8', s=44, zorder=7, edgecolors='#ffffff', linewidths=1.5)
    
    ax.text(sun_x - 0.24, (sun_y + y_closest)/2 + 0.12, "Impact parameter b",
            color='#38bdf8', fontsize=11.5, fontweight='bold', ha='right', va='bottom',
            zorder=7, path_effects=pe_bold)
    ax.text(sun_x - 0.24, (sun_y + y_closest)/2 - 0.05, "(b ≈ R☉ for limb ray)",
            color='#bae6fd', fontsize=10.2, fontweight='bold', ha='right', va='top',
            zorder=7, path_effects=pe_text)
    
    # -------------------------------------------------------------------------
    # 3. RAYS & LINES OF SIGHT
    # -------------------------------------------------------------------------
    # A. Path without gravitational deflection
    ax.plot(x_undev_line, y_undev_line, color='#94a3b8', linestyle='--', linewidth=1.6,
            alpha=0.80, zorder=4)
    ax.text(3.3, y_star_true + 0.22,
            "Path without gravitational deflection", color='#f8fafc', fontsize=10.8,
            fontweight='bold', ha='center', va='bottom', zorder=5, path_effects=pe_text)
    
    # B. Back-projected line of sight
    ax.plot(x_app_line, y_app_line, color='#fbbf24', linestyle='--', linewidth=1.8,
            alpha=0.92, zorder=5)
    ax.text(-1.8, y_E + m_E * (-1.8 - x_E) + 0.22,
            "Back-projected line of sight", color='#fbbf24',
            fontsize=11.0, fontweight='bold', rotation=np.degrees(m_E), ha='center', va='bottom',
            zorder=6, path_effects=pe_text)
    
    # C. Actual curved light ray
    ax.plot(x_vals, y_vals, color='#38bdf8', linewidth=5.5, alpha=0.30, zorder=7)
    ax.plot(x_vals, y_vals, color='#0284c7', linewidth=2.8, zorder=8)
    ax.plot(x_vals, y_vals, color='#e0f2fe', linewidth=1.3, zorder=9)
    
    for x_arr in [-3.8, -1.8, 2.2, 4.2]:
        idx = np.argmin(np.abs(x_vals - x_arr))
        xa, ya = x_vals[idx], y_vals[idx]
        dx = 0.22
        dy = slope(xa) * dx
        ax.annotate('', xy=(xa + dx, ya + dy), xytext=(xa, ya),
                    arrowprops=dict(arrowstyle='->', color='#38bdf8', lw=2.2, mutation_scale=14),
                    zorder=10)
    
    ax.text(-3.0, y_func(-3.0) - 0.32,
            "Actual curved path of starlight (General Relativity)",
            color='#38bdf8', fontsize=10.5, fontweight='bold', ha='center', va='top',
            zorder=10, path_effects=pe_text)
    
    # -------------------------------------------------------------------------
    # 4. DEFLECTION ANGLE δθ
    # -------------------------------------------------------------------------
    x_int = x_E + (y_star_true - y_E) / m_E
    y_int = y_star_true
    
    arc_rad = 1.70
    theta1 = np.degrees(m_E)
    theta2 = 0.0
    arc = Arc((x_int, y_int), arc_rad*2, arc_rad*2, angle=0, theta1=theta1, theta2=theta2,
              color='#f43f5e', linewidth=2.6, zorder=8)
    ax.add_patch(arc)
    
    arc_mid_x = x_int + arc_rad * np.cos(np.radians((theta1 + theta2) / 2))
    arc_mid_y = y_int + arc_rad * np.sin(np.radians((theta1 + theta2) / 2))
    
    callout_x = x_int + 1.30
    callout_y = y_int + 1.10
    ax.plot([arc_mid_x, callout_x - 0.1], [arc_mid_y, callout_y - 0.18],
            color='#f43f5e', linestyle=':', linewidth=1.4, zorder=9)
    
    ax.text(callout_x, callout_y, "Deflection angle δθ", color='#f43f5e', fontsize=11.5,
            fontweight='bold', ha='left', va='center', zorder=10, path_effects=pe_bold)
    ax.text(callout_x, callout_y - 0.28, "≈ 1.75″ for solar limb ray (b = R☉)", color='#fecdd3',
            fontsize=10.0, fontweight='bold', ha='left', va='center', zorder=10, path_effects=pe_text)
    
    # -------------------------------------------------------------------------
    # 5. STARS: TRUE POSITION & APPARENT POSITION
    # -------------------------------------------------------------------------
    ax.scatter([x_star], [y_star_app], color='#fbbf24', s=300, marker='*', zorder=11,
               edgecolors='#ffffff', linewidths=1.4)
    ax.scatter([x_star], [y_star_app], color='#fbbf24', s=700, marker='o', alpha=0.25, zorder=10)
    
    ax.scatter([x_star], [y_star_true], color='#38bdf8', s=260, marker='*', zorder=11,
               edgecolors='#ffffff', linewidths=1.4)
    ax.scatter([x_star], [y_star_true], color='#38bdf8', s=600, marker='o', alpha=0.25, zorder=10)
    
    ax.text(x_star - 0.35, y_star_app, "APPARENT POSITION\nOF STAR", color='#fbbf24',
            fontsize=11.2, fontweight='bold', ha='right', va='center', zorder=12,
            linespacing=1.1, path_effects=pe_bold)
    
    ax.text(x_star - 0.35, y_star_true, "TRUE POSITION\nOF STAR", color='#38bdf8',
            fontsize=11.2, fontweight='bold', ha='right', va='center', zorder=12,
            linespacing=1.1, path_effects=pe_bold)
    
    ax.annotate('', xy=(x_star + 0.32, y_star_app), xytext=(x_star + 0.32, y_star_true),
                arrowprops=dict(arrowstyle='<->', color='#f43f5e', lw=2.4), zorder=11)
    
    ax.text(x_star + 0.54, (y_star_app + y_star_true)/2,
            "Apparent displacement\nAWAY from Sun (δθ)", color='#f43f5e',
            fontsize=10.5, fontweight='bold', ha='left', va='center', zorder=12,
            linespacing=1.15, path_effects=pe_bold)
    
    # -------------------------------------------------------------------------
    # 6. OBSERVER ON EARTH
    # -------------------------------------------------------------------------
    earth_r = 0.52
    earth_x = x_E + 0.60
    earth_y = y_E - 0.12
    earth = Circle((earth_x, earth_y), earth_r, facecolor='#1e3a8a', edgecolor='#60a5fa',
                   linewidth=2.0, zorder=8)
    ax.add_patch(earth)
    c1 = Circle((earth_x - 0.12, earth_y + 0.10), 0.22, facecolor='#22c55e', alpha=0.6, zorder=9)
    ax.add_patch(c1)
    c2 = Circle((earth_x + 0.14, earth_y - 0.12), 0.18, facecolor='#22c55e', alpha=0.6, zorder=9)
    ax.add_patch(c2)
    
    t_angle = m_E
    t_len = 0.52
    tx1 = x_E - 0.05
    ty1 = y_E
    tx0 = tx1 + t_len * np.cos(t_angle)
    ty0 = ty1 + t_len * np.sin(t_angle)
    ax.plot([tx0, tx1], [ty0, ty1], color='#cbd5e1', linewidth=4.4, zorder=10, solid_capstyle='round')
    ax.plot([tx0, tx1], [ty0, ty1], color='#0f172a', linewidth=1.6, zorder=11)
    
    ax.text(earth_x, earth_y + earth_r + 0.24, "OBSERVER\n(Earth / Wallal)",
            color='#93c5fd', fontsize=10.8, fontweight='bold', ha='center', va='bottom',
            zorder=12, linespacing=1.1, path_effects=pe_bold)
    
    # -------------------------------------------------------------------------
    # 7. LOWER PANEL: PROMINENT & HIGHLY READABLE
    # -------------------------------------------------------------------------
    card_x = -0.60
    card_y = -3.22
    card_w = 8.60
    card_h = 1.50
    
    rect_card = Rectangle((card_x, card_y), card_w, card_h, facecolor='#111827',
                          edgecolor='#374151', linewidth=1.4, alpha=0.96, zorder=8)
    ax.add_patch(rect_card)
    
    banner_h = 0.36
    rect_banner = Rectangle((card_x, card_y + card_h - banner_h), card_w, banner_h,
                            facecolor='#1f2937', edgecolor='#374151', linewidth=1.0, zorder=9)
    ax.add_patch(rect_banner)
    ax.text(card_x + 0.30, card_y + card_h - banner_h/2, "GENERAL-RELATIVISTIC DEFLECTION",
            color='#facc15', fontsize=10.5, fontweight='bold', ha='left', va='center', zorder=10)
    
    # Left column: General relation
    formula_gen = r"$\delta\theta(b) = \frac{4GM_\odot}{c^2 b}$"
    ax.text(card_x + 0.40, card_y + 0.72, formula_gen, color='#38bdf8', fontsize=17.0,
            fontweight='bold', ha='left', va='center', zorder=10)
    ax.text(card_x + 0.42, card_y + 0.26, "General deflection (arbitrary b)",
            color='#7dd3fc', fontsize=10.2, fontweight='bold', ha='left', va='center', zorder=10)
    
    div_x = card_x + 4.30
    ax.plot([div_x, div_x], [card_y + 0.12, card_y + card_h - banner_h - 0.12],
            color='#374151', linewidth=1.3, linestyle='-', zorder=9)
    
    # Right column: Solar limb value
    formula_limb = r"$\delta\theta(R_\odot) \approx 1.75^{\prime\prime}$"
    ax.text(div_x + 0.38, card_y + 0.72, formula_limb, color='#fbbf24', fontsize=17.0,
            fontweight='bold', ha='left', va='center', zorder=10)
    ax.text(div_x + 0.40, card_y + 0.26, "Solar limb grazing ray (b = R☉)",
            color='#fde047', fontsize=10.2, fontweight='bold', ha='left', va='center', zorder=10)
    
    # -------------------------------------------------------------------------
    # 8. TITLE BADGE (Top Left) - EXPANDED BOX & PERFECTLY CONTAINED SUBTITLE
    # -------------------------------------------------------------------------
    title_x = -7.9
    title_y = 3.25
    title_w = 7.60  # Expanded from 7.2 to 7.6 to ensure subtext is 100% inside
    title_h = 0.96
    rect_title = Rectangle((title_x, title_y - 0.58), title_w, title_h,
                           facecolor='#1e293b', edgecolor='#475569', linewidth=1.3,
                           alpha=0.96, zorder=8)
    ax.add_patch(rect_title)
    ax.text(title_x + 0.28, title_y - 0.10, "GRAVITATIONAL DEFLECTION OF STARLIGHT",
            color='#ffffff', fontsize=11.6, fontweight='bold', ha='left', va='center', zorder=10)
    ax.text(title_x + 0.28, title_y - 0.38, "Light bending by the Sun's spacetime curvature in General Relativity",
            color='#7dd3fc', fontsize=9.2, fontweight='bold', ha='left', va='center', zorder=10)
    
    # -------------------------------------------------------------------------
    # 9. SCHEMATIC DISCLAIMER (Bottom Left) - 2 LINES, BRIGHT LIGHT SKY-BLUE
    # -------------------------------------------------------------------------
    ax.text(-7.8, -2.78, "* Schematic diagram (not to scale)",
            color='#7dd3fc', fontsize=9.6, fontweight='bold', ha='left', va='center', zorder=10,
            path_effects=pe_text)
    ax.text(-7.8, -3.02, "  Deflection angle and curvature exaggerated for clarity",
            color='#7dd3fc', fontsize=9.6, fontweight='bold', ha='left', va='center', zorder=10,
            path_effects=pe_text)
    
    # Outer border
    rect_border = Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                            linewidth=1.5, edgecolor='#1e293b', facecolor='none', zorder=20)
    ax.add_patch(rect_border)
    
    # Save high-res 2x
    plt.savefig(out_2x, dpi=200, facecolor=bg_color, edgecolor='none')
    plt.close(fig)
    
    # Generate 680px 1x version for Medium
    with Image.open(out_2x) as img:
        w, h = img.size
        new_h = int(h * (680.0 / w))
        img_680 = img.resize((680, new_h), Image.Resampling.LANCZOS)
        img_680.save(out_1x, optimize=True)
        
    print(f"Generated {out_1x} ({img_680.size}) and {out_2x} ({w}x{h})")

if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else None
    generate_deflection_diagram(out_dir=out_dir)
