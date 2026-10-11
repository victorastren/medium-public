#!/usr/bin/env python3
r"""
Create comparative conceptual diagram:
"Two routes to the deflection of starlight" (Newtonian / 1911 vs General Relativity 1915).

Tailored for Medium (680px width) with maximum visual legibility:
- Two-column comparative layout with side-by-side cards.
- Left panel: Newtonian treatment & Einstein 1911 (light as particle at speed c, transverse acceleration, 0.87″).
- Right panel: General Relativity 1915 (time contribution 0.87″ + spatial-curvature contribution +0.87″ = 1.75″).
- Bottom callout: Factor-of-two difference from spatial curvature contribution (0.87″ ──► 1.75″).
- Generates standard Medium width (680px) and 2x Retina (2400x1640).
"""

import os
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arc, Rectangle, FancyBboxPatch
import matplotlib.patheffects as pe
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT_DIR = PROJECT_DIR / "images"

def generate_comparison_diagram(out_dir=None, filename_prefix="deflection_predictions_comparison"):
    if out_dir is None:
        out_dir = DEFAULT_OUT_DIR
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_2x = out_dir / f"{filename_prefix}_2x.png"
    out_1x = out_dir / f"{filename_prefix}.png"
    
    # 12 x 8.2 inches at 200 DPI gives 2400 x 1640 px (downscaled to 680 x 465 px)
    fig = plt.figure(figsize=(12, 8.2), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    
    bg_color = '#0b0f19'  # Cosmic dark slate matching other diagrams
    ax.set_facecolor(bg_color)
    fig.patch.set_facecolor(bg_color)
    
    x_min, x_max = -6.6, 6.6
    y_min, y_max = -4.4, 4.4
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Subtle background starfield (masked out of card content)
    np.random.seed(101)
    bg_x = np.random.uniform(x_min, x_max, 140)
    bg_y = np.random.uniform(y_min, y_max, 140)
    bg_s = np.random.uniform(1.5, 5.5, 140)
    bg_a = np.random.uniform(0.12, 0.35, 140)
    mask = (np.abs(bg_x) > 6.25) | (bg_y > 4.1) | (bg_y < -4.2) | ((np.abs(bg_x) < 0.20) & (bg_y > -2.8) & (bg_y < 2.8))
    ax.scatter(bg_x[mask], bg_y[mask], s=bg_s[mask], color='#ffffff', alpha=bg_a[mask], zorder=1)
    
    pe_text = [pe.withStroke(linewidth=3.5, foreground='#0b0f19')]
    pe_bold = [pe.withStroke(linewidth=4.5, foreground='#0b0f19')]
    
    # =========================================================================
    # TOP HEADER: TITLE BADGE (Enlarged fonts for 680px legibility)
    # =========================================================================
    top_w = 12.4
    top_h = 1.16
    top_x = -top_w / 2.0
    top_y = 3.65 - top_h / 2.0
    
    rect_top = FancyBboxPatch((top_x, top_y), top_w, top_h, boxstyle="round,pad=0.06,rounding_size=0.15",
                              facecolor='#1e293b', edgecolor='#475569', linewidth=1.5, zorder=3)
    ax.add_patch(rect_top)
    
    ax.text(0, 3.96, "TWO ROUTES TO THE DEFLECTION OF STARLIGHT", color='#ffffff',
            fontsize=18.5, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(0, 3.44, "Why the general-relativistic prediction is twice as large",
            color='#7dd3fc', fontsize=15.5, fontweight='bold', ha='center', va='center', zorder=5)
    
    # =========================================================================
    # CARD COORDINATES
    # =========================================================================
    card_w = 6.05
    card_h = 6.22
    card_y = -3.24
    banner_h = 0.86
    banner_y = card_y + card_h - banner_h  # 2.12
    
    left_x = -6.20
    right_x = 0.15
    
    # =========================================================================
    # LEFT PANEL: NEWTONIAN / EINSTEIN 1911
    # =========================================================================
    rect_left = FancyBboxPatch((left_x, card_y), card_w, card_h, boxstyle="round,pad=0.06,rounding_size=0.18",
                               facecolor='#0f172a', edgecolor='#0284c7', linewidth=1.6, zorder=2)
    ax.add_patch(rect_left)
    
    # Banner
    rect_left_ban = FancyBboxPatch((left_x, banner_y), card_w, banner_h, boxstyle="round,pad=0.06,rounding_size=0.18",
                                   facecolor='#0369a1', edgecolor='#38bdf8', linewidth=1.3, zorder=3)
    ax.add_patch(rect_left_ban)
    ax.text(left_x + card_w/2, banner_y + 0.54, "NEWTONIAN TREATMENT / EINSTEIN 1911",
            color='#ffffff', fontsize=15.0, fontweight='bold', ha='center', va='center', zorder=4)
    ax.text(left_x + card_w/2, banner_y + 0.22, "Light treated as a particle moving at speed c",
            color='#bae6fd', fontsize=13.0, fontweight='bold', ha='center', va='center', zorder=4)
    
    # Left Schematic: Sun & Ray (Positioned with optimal clearance)
    sun_L_x = left_x + 1.05
    sun_L_y = 0.82
    r_sun = 0.46
    
    for r_scale, alpha_val in [(1.70, 0.05), (1.35, 0.10), (1.15, 0.20)]:
        ax.add_patch(Circle((sun_L_x, sun_L_y), r_sun * r_scale, facecolor='#f59e0b',
                            edgecolor='none', alpha=alpha_val, zorder=3))
    ax.add_patch(Circle((sun_L_x, sun_L_y), r_sun, facecolor='#f59e0b', edgecolor='#fbbf24',
                        linewidth=1.8, zorder=4))
    ax.add_patch(Circle((sun_L_x, sun_L_y), r_sun * 0.72, facecolor='#fef08a', edgecolor='none',
                        alpha=0.85, zorder=5))
    ax.scatter([sun_L_x], [sun_L_y], color='#b45309', s=30, zorder=6)
    ax.text(sun_L_x, sun_L_y + 0.08, "SUN", color='#78350f', fontsize=13.0,
            fontweight='bold', ha='center', va='center', zorder=7)
    ax.text(sun_L_x, sun_L_y - 0.18, "Mass M☉", color='#78350f', fontsize=11.5,
            fontweight='bold', ha='center', va='center', zorder=7)
    
    # Ray geometry
    ray_L_y0 = sun_L_y + r_sun + 0.35  # y = 1.63
    
    # Impact parameter b arrow
    ax.plot([sun_L_x, sun_L_x], [sun_L_y, ray_L_y0], color='#7dd3fc', linestyle=':', linewidth=1.5, zorder=5)
    ax.annotate('', xy=(sun_L_x, ray_L_y0), xytext=(sun_L_x, sun_L_y),
                arrowprops=dict(arrowstyle='<->', color='#38bdf8', lw=2.0), zorder=6)
    pe_halo_cyan = [pe.withStroke(linewidth=3.2, foreground='#0b0f19')]
    ax.text(sun_L_x + 0.22, (sun_L_y + ray_L_y0)/2, "b", color='#38bdf8', fontsize=15.0,
            fontweight='bold', va='center', zorder=7, path_effects=pe_halo_cyan)
    
    # Trajectory
    x_ray_in = left_x + 0.25
    x_ray_out = left_x + card_w - 0.25
    
    alpha_N_deg = 4.8
    alpha_N = np.radians(alpha_N_deg)
    def y_path_L(x):
        return ray_L_y0 - alpha_N * 0.5 * ((x - x_ray_in) + np.sqrt((x - sun_L_x)**2 + 0.46**2) - np.sqrt((x_ray_in - sun_L_x)**2 + 0.46**2))
    
    x_pts_L = np.linspace(x_ray_in, x_ray_out, 200)
    y_pts_L = y_path_L(x_pts_L)
    
    # Undeviated dashed line
    ax.plot([x_ray_in, x_ray_out], [ray_L_y0, ray_L_y0], color='#64748b', linestyle='--', linewidth=1.3, zorder=4)
    
    # Curved path
    ax.plot(x_pts_L, y_pts_L, color='#38bdf8', linewidth=4.5, alpha=0.30, zorder=6)
    ax.plot(x_pts_L, y_pts_L, color='#38bdf8', linewidth=2.4, zorder=7)
    
    # Arrow along path
    ax.annotate('', xy=(sun_L_x + 1.25, y_path_L(sun_L_x + 1.25) - 0.04),
                xytext=(sun_L_x + 0.85, y_path_L(sun_L_x + 0.85)),
                arrowprops=dict(arrowstyle='->', color='#38bdf8', lw=2.2, mutation_scale=13), zorder=8)
    
    # Incoming label (Enlarged to 13.0 pt)
    ax.text(x_ray_in + 0.10, ray_L_y0 + 0.22, "Incoming starlight (speed c)",
            color='#94a3b8', fontsize=13.0, fontweight='bold', zorder=7)
    
    # Transverse acceleration badge & arrow (Shifted down-right for clear spacing)
    box_acc_x = sun_L_x + 0.68
    box_acc_y = 0.88
    box_acc_w = 2.25
    box_acc_h = 0.54
    
    ax.annotate('', xy=(box_acc_x + 0.25, box_acc_y + box_acc_h + 0.02),
                xytext=(box_acc_x + 0.25, ray_L_y0 - 0.02),
                arrowprops=dict(arrowstyle='->', color='#fb7185', lw=2.2, mutation_scale=13), zorder=8)
    
    rect_acc = FancyBboxPatch((box_acc_x, box_acc_y), box_acc_w, box_acc_h,
                              boxstyle="round,pad=0.04,rounding_size=0.10",
                              facecolor='#1e293b', edgecolor='#fb7185', linewidth=1.4, zorder=8)
    ax.add_patch(rect_acc)
    ax.text(box_acc_x + box_acc_w/2, box_acc_y + box_acc_h/2, "Transverse pull\n$a_\\perp = GM_\\odot b / r^3$",
            color='#fda4af', fontsize=12.2, fontweight='bold', ha='center', va='center', zorder=9, linespacing=1.15)
    
    # Deflection angle exit dimension & label (Enlarged to 14.5 pt)
    y_end_L = y_pts_L[-1]
    ax.annotate('', xy=(x_ray_out - 0.12, y_end_L), xytext=(x_ray_out - 0.12, ray_L_y0),
                arrowprops=dict(arrowstyle='<->', color='#38bdf8', lw=2.0), zorder=8)
    ax.text(x_ray_out - 0.20, 1.94, r"$\delta\theta_{\rm N} \approx 0.87^{\prime\prime}$",
            color='#38bdf8', fontsize=14.5, fontweight='bold', ha='right', va='center', zorder=9,
            path_effects=pe_bold)
    ax.annotate('', xy=(x_ray_out - 0.05, (y_end_L + ray_L_y0)/2),
                xytext=(x_ray_out - 0.20, 1.84),
                arrowprops=dict(arrowstyle='->', color='#38bdf8', lw=1.5, mutation_scale=10), zorder=8)
    
    # Left Formula Card: Height 1.52, perfectly spaced so equations never clip
    res_L_top = -0.08
    res_L_h = 1.52
    res_L_bot = res_L_top - res_L_h  # -1.60
    rect_res_L = FancyBboxPatch((left_x + 0.30, res_L_bot), card_w - 0.60, res_L_h,
                                boxstyle="round,pad=0.05,rounding_size=0.12",
                                facecolor='#0c4a6e', edgecolor='#0284c7', linewidth=1.5, zorder=4)
    ax.add_patch(rect_res_L)
    
    # Header: centered at y = -0.26
    ax.text(left_x + card_w/2, -0.26, "NEWTONIAN PREDICTION",
            color='#7dd3fc', fontsize=13.5, fontweight='bold', ha='center', va='center', zorder=5)
    
    # Display formula: centered at y = -0.66, ample room above and below
    ax.text(left_x + card_w/2, -0.66, r"$\delta\theta_{\rm N} = \frac{2GM_\odot}{bc^2}$",
            color='#ffffff', fontsize=21.0, fontweight='bold', ha='center', va='center', zorder=5)
    
    # Limb value badge: y from -1.50 to -1.04 (height 0.46)
    badge_h = 0.46
    badge_bot = -1.50
    badge_center = badge_bot + badge_h/2  # -1.27
    rect_val_L = FancyBboxPatch((left_x + 0.48, badge_bot), card_w - 0.96, badge_h,
                                boxstyle="round,pad=0.04,rounding_size=0.08",
                                facecolor='#082f49', edgecolor='#38bdf8', linewidth=1.3, zorder=5)
    ax.add_patch(rect_val_L)
    ax.text(left_x + card_w/2, badge_center, r"At solar limb ($b = R_\odot$):   $\delta\theta_{\rm N} \approx 0.87^{\prime\prime}$",
            color='#38bdf8', fontsize=14.2, fontweight='bold', ha='center', va='center', zorder=6)
    
    # Left Short Notes Box: Height 1.48 (from -3.20 to -1.72)
    note_bot = -3.20
    note_h = 1.48
    rect_note_L = FancyBboxPatch((left_x + 0.25, note_bot), card_w - 0.50, note_h,
                                 boxstyle="round,pad=0.04,rounding_size=0.10",
                                 facecolor='#111827', edgecolor='#1f2937', linewidth=1.2, zorder=4)
    ax.add_patch(rect_note_L)
    
    # Bullet 1: Bullet at left_x + 0.44, text lines all perfectly left-aligned at left_x + 0.62
    ax.text(left_x + 0.44, -1.90, "•", color='#cbd5e1', fontsize=12.8, fontweight='bold', ha='left', va='center', zorder=5)
    ax.text(left_x + 0.62, -1.90, "Treating light as a particle in Newtonian gravity",
            color='#cbd5e1', fontsize=12.8, fontweight='bold', ha='left', va='center', zorder=5)
    ax.text(left_x + 0.62, -2.16, "gives the same deflection as Einstein’s 1911",
            color='#7dd3fc', fontsize=12.8, fontweight='bold', ha='left', va='center', zorder=5)
    ax.text(left_x + 0.62, -2.42, "equivalence-principle calculation.",
            color='#7dd3fc', fontsize=12.8, fontweight='bold', ha='left', va='center', zorder=5)
    
    # Bullet 2: Bullet at left_x + 0.44, text lines all perfectly left-aligned at left_x + 0.62
    ax.text(left_x + 0.44, -2.72, "•", color='#94a3b8', fontsize=12.8, fontweight='bold', ha='left', va='center', zorder=5)
    ax.text(left_x + 0.62, -2.72, "Assumes Euclidean (flat) space with no",
            color='#94a3b8', fontsize=12.8, fontweight='bold', ha='left', va='center', zorder=5)
    ax.text(left_x + 0.62, -2.98, "spatial curvature.",
            color='#94a3b8', fontsize=12.8, fontweight='bold', ha='left', va='center', zorder=5)
    
    # =========================================================================
    # RIGHT PANEL: GENERAL RELATIVITY (1915)
    # =========================================================================
    rect_right = FancyBboxPatch((right_x, card_y), card_w, card_h, boxstyle="round,pad=0.06,rounding_size=0.18",
                                facecolor='#0f172a', edgecolor='#d97706', linewidth=1.6, zorder=2)
    ax.add_patch(rect_right)
    
    # Banner
    rect_right_ban = FancyBboxPatch((right_x, banner_y), card_w, banner_h, boxstyle="round,pad=0.06,rounding_size=0.18",
                                    facecolor='#b45309', edgecolor='#fbbf24', linewidth=1.3, zorder=3)
    ax.add_patch(rect_right_ban)
    ax.text(right_x + card_w/2, banner_y + 0.54, "GENERAL RELATIVITY (1915)",
            color='#ffffff', fontsize=15.0, fontweight='bold', ha='center', va='center', zorder=4)
    ax.text(right_x + card_w/2, banner_y + 0.22, "Weak-field spacetime geometry (time + spatial curvature)",
            color='#fef08a', fontsize=11.2, fontweight='bold', ha='center', va='center', zorder=4)
    
    # Right Schematic: Sun & Ray (Positioned symmetrically with left panel)
    sun_R_x = right_x + 1.05
    sun_R_y = 0.82
    
    # Spacetime curvature concentric grid ripples (compact radii)
    for ripple_r, alpha_rip in [(0.56, 0.16), (0.70, 0.08)]:
        ax.add_patch(Circle((sun_R_x, sun_R_y), ripple_r, facecolor='none',
                            edgecolor='#f59e0b', linestyle=':', linewidth=1.2, alpha=alpha_rip, zorder=3))
    
    for r_scale, alpha_val in [(1.70, 0.05), (1.35, 0.10), (1.15, 0.20)]:
        ax.add_patch(Circle((sun_R_x, sun_R_y), r_sun * r_scale, facecolor='#f59e0b',
                            edgecolor='none', alpha=alpha_val, zorder=3))
    ax.add_patch(Circle((sun_R_x, sun_R_y), r_sun, facecolor='#f59e0b', edgecolor='#fbbf24',
                        linewidth=1.8, zorder=4))
    ax.add_patch(Circle((sun_R_x, sun_R_y), r_sun * 0.72, facecolor='#fef08a', edgecolor='none',
                        alpha=0.85, zorder=5))
    ax.scatter([sun_R_x], [sun_R_y], color='#b45309', s=30, zorder=6)
    ax.text(sun_R_x, sun_R_y + 0.08, "SUN", color='#78350f', fontsize=13.0,
            fontweight='bold', ha='center', va='center', zorder=7)
    ax.text(sun_R_x, sun_R_y - 0.18, "Mass M☉", color='#78350f', fontsize=11.5,
            fontweight='bold', ha='center', va='center', zorder=7)
    
    # Ray geometry
    ray_R_y0 = sun_R_y + r_sun + 0.35  # y = 1.63
    
    # Impact parameter b arrow
    ax.plot([sun_R_x, sun_R_x], [sun_R_y, ray_R_y0], color='#fbbf24', linestyle=':', linewidth=1.5, zorder=5)
    ax.annotate('', xy=(sun_R_x, ray_R_y0), xytext=(sun_R_x, sun_R_y),
                arrowprops=dict(arrowstyle='<->', color='#f59e0b', lw=2.0), zorder=6)
    pe_halo_gold = [pe.withStroke(linewidth=3.2, foreground='#0b0f19')]
    ax.text(sun_R_x + 0.22, (sun_R_y + ray_R_y0)/2, "b", color='#fbbf24', fontsize=15.0,
            fontweight='bold', va='center', zorder=7, path_effects=pe_halo_gold)
    
    # Right Trajectories:
    x_ray_R_in = right_x + 0.25
    x_ray_R_out = right_x + card_w - 0.25
    x_pts_R = np.linspace(x_ray_R_in, x_ray_R_out, 200)
    
    # 1. Undeviated line (dashed grey)
    ax.plot([x_ray_R_in, x_ray_R_out], [ray_R_y0, ray_R_y0], color='#64748b', linestyle='--', linewidth=1.3, zorder=4)
    
    # 2. Time-contribution alone path (dashed cyan, alpha_N ~ 4.8 deg)
    def y_path_time(x):
        return ray_R_y0 - alpha_N * 0.5 * ((x - x_ray_R_in) + np.sqrt((x - sun_R_x)**2 + 0.46**2) - np.sqrt((x_ray_R_in - sun_R_x)**2 + 0.46**2))
    
    y_pts_time = y_path_time(x_pts_R)
    ax.plot(x_pts_R, y_pts_time, color='#38bdf8', linestyle=':', linewidth=2.0, alpha=0.90, zorder=5)
    
    # 3. Full GR path (time + space curvature, solid gold, alpha_GR ~ 9.6 deg)
    alpha_GR_deg = 9.6
    alpha_GR = np.radians(alpha_GR_deg)
    def y_path_GR(x):
        return ray_R_y0 - alpha_GR * 0.5 * ((x - x_ray_R_in) + np.sqrt((x - sun_R_x)**2 + 0.46**2) - np.sqrt((x_ray_R_in - sun_R_x)**2 + 0.46**2))
    
    y_pts_GR = y_path_GR(x_pts_R)
    ax.plot(x_pts_R, y_pts_GR, color='#fbbf24', linewidth=4.5, alpha=0.30, zorder=6)
    ax.plot(x_pts_R, y_pts_GR, color='#fbbf24', linewidth=2.4, zorder=7)
    
    # Arrow along path
    ax.annotate('', xy=(sun_R_x + 1.25, y_path_GR(sun_R_x + 1.25) - 0.08),
                xytext=(sun_R_x + 0.85, y_path_GR(sun_R_x + 0.85)),
                arrowprops=dict(arrowstyle='->', color='#fbbf24', lw=2.2, mutation_scale=13), zorder=8)
    
    # TWO CONTRIBUTIONS SHOWN DIRECTLY AT THE DEFLECTION EXIT:
    y_end_undev = ray_R_y0
    y_end_time = y_pts_time[-1]
    y_end_full = y_pts_GR[-1]
    x_dim = x_ray_R_out - 0.12
    
    # Component 1: Time contribution (≈ 0.87″) - Placed clearly above undeviated line with pointer
    ax.annotate('', xy=(x_dim, y_end_time), xytext=(x_dim, y_end_undev),
                arrowprops=dict(arrowstyle='<->', color='#38bdf8', lw=2.0), zorder=8)
    ax.text(x_dim - 0.20, 1.94, "Time contribution: ≈ 0.87″",
            color='#7dd3fc', fontsize=13.5, fontweight='bold', ha='right', va='center', zorder=9,
            path_effects=pe_text)
    ax.annotate('', xy=(x_dim - 0.05, (y_end_undev + y_end_time)/2),
                xytext=(x_dim - 0.20, 1.84),
                arrowprops=dict(arrowstyle='->', color='#38bdf8', lw=1.5, mutation_scale=10), zorder=8)
    
    # Component 2: Spatial-curvature contribution on a single line!
    ax.annotate('', xy=(x_dim, y_end_full), xytext=(x_dim, y_end_time),
                arrowprops=dict(arrowstyle='<->', color='#fbbf24', lw=2.0), zorder=8)
    ax.text(x_dim - 0.10, 0.50, r"Spatial-curvature contribution: $\approx 0.87^{\prime\prime}$",
            color='#fde047', fontsize=11.5, fontweight='bold', ha='right', va='center', zorder=9,
            path_effects=pe_text)
    ax.annotate('', xy=(x_dim - 0.05, (y_end_time + y_end_full)/2),
                xytext=(x_dim - 0.10, 0.62),
                arrowprops=dict(arrowstyle='->', color='#fbbf24', lw=1.5, mutation_scale=10), zorder=8)
    
    # Total combined label below (Prominent and spacious)
    ax.text(x_ray_R_out - 0.08, 0.14, r"Total:  $\delta\theta_{\rm GR} \approx 1.75^{\prime\prime}$",
            color='#fbbf24', fontsize=14.5, fontweight='bold', ha='right', va='center', zorder=8,
            path_effects=pe_bold)
    
    # Right Formula Card: Height 1.52, perfectly spaced so equations never clip
    rect_res_R = FancyBboxPatch((right_x + 0.30, res_L_bot), card_w - 0.60, res_L_h,
                                boxstyle="round,pad=0.05,rounding_size=0.12",
                                facecolor='#78350f', edgecolor='#d97706', linewidth=1.5, zorder=4)
    ax.add_patch(rect_res_R)
    
    # Header: centered at y = -0.26
    ax.text(right_x + card_w/2, -0.26, "GENERAL RELATIVITY PREDICTION",
            color='#fde047', fontsize=13.5, fontweight='bold', ha='center', va='center', zorder=5)
    
    # Display formula: centered at y = -0.66, ample room above and below
    ax.text(right_x + card_w/2, -0.66, r"$\delta\theta_{\rm GR} = \frac{4GM_\odot}{bc^2}$",
            color='#ffffff', fontsize=21.0, fontweight='bold', ha='center', va='center', zorder=5)
    
    # Limb value badge: y from -1.50 to -1.04 (height 0.46)
    rect_val_R = FancyBboxPatch((right_x + 0.48, badge_bot), card_w - 0.96, badge_h,
                                boxstyle="round,pad=0.04,rounding_size=0.08",
                                facecolor='#451a03', edgecolor='#f59e0b', linewidth=1.3, zorder=5)
    ax.add_patch(rect_val_R)
    ax.text(right_x + card_w/2, badge_center, r"At solar limb ($b = R_\odot$):   $\delta\theta_{\rm GR} \approx 1.75^{\prime\prime}$",
            color='#fde047', fontsize=14.2, fontweight='bold', ha='center', va='center', zorder=6)
    
    # Right Short Notes Box: Height 1.48 (from -3.20 to -1.72)
    rect_note_R = FancyBboxPatch((right_x + 0.25, note_bot), card_w - 0.50, note_h,
                                 boxstyle="round,pad=0.04,rounding_size=0.10",
                                 facecolor='#111827', edgecolor='#1f2937', linewidth=1.2, zorder=4)
    ax.add_patch(rect_note_R)
    
    # Bullet: Bullet at right_x + 0.44, text lines all perfectly left-aligned at right_x + 0.62 in uniform yellow (#fde047)
    ax.text(right_x + 0.44, -1.94, "•", color='#fef08a', fontsize=12.8, fontweight='bold', ha='left', va='center', zorder=5)
    ax.text(right_x + 0.62, -1.94, "Spatial curvature adds an equal contribution",
            color='#fef08a', fontsize=12.8, fontweight='bold', ha='left', va='center', zorder=5)
    ax.text(right_x + 0.62, -2.22, "to that already present in the 1911/Newtonian",
            color='#fde047', fontsize=12.8, fontweight='bold', ha='left', va='center', zorder=5)
    ax.text(right_x + 0.62, -2.50, "result, doubling the predicted deflection",
            color='#fde047', fontsize=12.8, fontweight='bold', ha='left', va='center', zorder=5)
    ax.text(right_x + 0.62, -2.78, "of grazing starlight rays.",
            color='#fde047', fontsize=12.8, fontweight='bold', ha='left', va='center', zorder=5)
    
    # =========================================================================
    # BOTTOM CALLOUT: FACTOR OF TWO (Enlarged fonts)
    # =========================================================================
    bot_w = 12.4
    bot_h = 0.96
    bot_x = -bot_w / 2.0
    bot_y = -4.30
    
    rect_bot = FancyBboxPatch((bot_x, bot_y), bot_w, bot_h, boxstyle="round,pad=0.05,rounding_size=0.14",
                              facecolor='#1e1b4b', edgecolor='#6366f1', linewidth=1.5, zorder=3)
    ax.add_patch(rect_bot)
    
    # Left pill: 0.87"
    rect_p1 = FancyBboxPatch((-5.75, bot_y + 0.17), 3.25, 0.62, boxstyle="round,pad=0.04,rounding_size=0.08",
                             facecolor='#0c4a6e', edgecolor='#38bdf8', linewidth=1.3, zorder=4)
    ax.add_patch(rect_p1)
    ax.text(-4.12, bot_y + 0.48, "0.87″ (Newtonian / 1911)", color='#38bdf8',
            fontsize=14.0, fontweight='bold', ha='center', va='center', zorder=5)
    
    # Center connector bridge
    bridge_w = 4.45
    rect_bridge = FancyBboxPatch((-bridge_w/2, bot_y + 0.17), bridge_w, 0.62,
                                  boxstyle="round,pad=0.04,rounding_size=0.08",
                                  facecolor='#312e81', edgecolor='#818cf8', linewidth=1.2, zorder=4)
    ax.add_patch(rect_bridge)
    
    ax.text(0, bot_y + 0.54, "+ SPATIAL CURVATURE CONTRIBUTION",
            color='#fde047', fontsize=12.8, fontweight='bold', ha='center', va='center', zorder=6)
    ax.text(0, bot_y + 0.26, "Doubles the prediction:  0.87″ ──► 1.75″",
            color='#e0e7ff', fontsize=12.2, fontweight='bold', ha='center', va='center', zorder=6)
    
    # Right pill: 1.75"
    rect_p2 = FancyBboxPatch((2.50, bot_y + 0.17), 3.25, 0.62, boxstyle="round,pad=0.04,rounding_size=0.08",
                             facecolor='#78350f', edgecolor='#fbbf24', linewidth=1.3, zorder=4)
    ax.add_patch(rect_p2)
    ax.text(4.12, bot_y + 0.48, "1.75″ (General Relativity)", color='#fde047',
            fontsize=14.0, fontweight='bold', ha='center', va='center', zorder=5)
    
    # Outer border
    rect_border = Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                            linewidth=1.5, edgecolor='#1e293b', facecolor='none', zorder=20)
    ax.add_patch(rect_border)
    
    # Save 2x
    plt.savefig(out_2x, dpi=200, facecolor=bg_color, edgecolor='none')
    plt.close(fig)
    
    # Downscale to 680px 1x
    with Image.open(out_2x) as img:
        w, h = img.size
        new_h = int(h * (680.0 / w))
        img_680 = img.resize((680, new_h), Image.Resampling.LANCZOS)
        img_680.save(out_1x, optimize=True)
        
    print(f"Generated {out_1x} ({img_680.size}) and {out_2x} ({w}x{h})")

if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else None
    generate_comparison_diagram(out_dir=out_dir)
