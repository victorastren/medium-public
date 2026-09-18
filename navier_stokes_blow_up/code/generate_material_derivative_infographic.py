from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "eulerian_vs_lagrangian_derivative.png"

#!/usr/bin/env python3
"""
Generate Infographic: Eulerian vs. Lagrangian Descriptions and the Material Derivative
Publication-grade illustration optimized for Medium's 680px column width:
- High contrast, 35-40% reduced visual clutter.
- Clear two-panel comparison (Eulerian fixed point vs. Lagrangian moving parcel).
- Reduced background streamline/quiver density.
- Acceleration decomposition inset with "Advective (convective)" label.
- Dedicated mathematical synthesis strip across bottom showing:
    Du/Dt = ∂u/∂t (local change) + (u · ∇)u (advective change)
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch

# -------------------------------------------------------------------------
# PALETTE & AESTHETICS (Mathematical Analysis Slate Theme)
# -------------------------------------------------------------------------
BG_COLOR     = "#070b12"       # Deep mathematical slate canvas
PANEL_BG     = "#0c1322"       # Dark mathematical slate panel
GRID_COLOR   = "#162032"       # Subtle gridlines
BORDER_COLOR = "#22314a"       # Crisp panel borders
CARD_BG      = "#10192c"       # Inset card background
CARD_BORDER  = "#2a3d5e"       # Card border

TEXT_TITLE   = "#ffffff"       # Pure white
TEXT_SUB     = "#94a3b8"       # Light slate
TEXT_MUTED   = "#64748b"       # Muted slate

STREAM_COLOR = "#19324f"       # Subtle stream flow lines
VECTOR_COLOR = "#38bdf8"       # Soft cyan for background flow arrows

EULER_ACCENT = "#fbbf24"       # Warm Amber/Gold for Eulerian station
LAGR_ACCENT  = "#f43f5e"       # Vibrant Rose for Lagrangian parcel
LOCAL_COLOR  = "#06b6d4"       # Cyan for local time derivative ∂u/∂t
ADV_COLOR    = "#c084fc"       # Soft Purple for advective transport (u·∇)u
TOTAL_COLOR  = "#10b981"       # Emerald for material derivative Du/Dt

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Helvetica', 'Arial'],
    'mathtext.fontset': 'dejavusans',
    'text.color': TEXT_SUB,
    'axes.labelcolor': TEXT_SUB,
})

def make_infographic(out_path=None):
    if out_path is None:
        out_path = DEFAULT_OUT
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    # Canvas optimized for Medium reading width (high clarity, ~16:9.2 aspect ratio)
    fig = plt.figure(figsize=(16.0, 9.2), dpi=240, facecolor=BG_COLOR)
    
    # 3-row layout:
    # Row 0: Concise Top Title Banner
    # Row 1: The Two Core Comparison Panels (Eulerian vs. Lagrangian)
    # Row 2: Mathematical Synthesis Strip (Du/Dt = local + advective)
    gs = fig.add_gridspec(3, 2, height_ratios=[0.07, 0.72, 0.21],
                          left=0.035, right=0.965, bottom=0.035, top=0.965,
                          wspace=0.055, hspace=0.14)
    
    # -------------------------------------------------------------------------
    # ROW 0: TOP TITLE
    # -------------------------------------------------------------------------
    ax_head = fig.add_subplot(gs[0, :])
    ax_head.set_facecolor(BG_COLOR)
    ax_head.axis('off')
    
    ax_head.text(0.5, 0.52, "EULERIAN vs. LAGRANGIAN: THE ORIGIN OF THE MATERIAL DERIVATIVE",
                 fontsize=15.5, fontweight='bold', color=TEXT_TITLE, ha='center', va='center')

    # -------------------------------------------------------------------------
    # FLOW FIELD MATHEMATICS (Convergent Nozzle + Unsteady Wave)
    # -------------------------------------------------------------------------
    def velocity_field(x, y, t=0.0):
        # Constriction function near x ~ 0
        b = 1.0 + 0.45 * np.exp(-0.35 * x**2)
        db_dx = -0.35 * 2 * x * 0.45 * np.exp(-0.35 * x**2)
        
        # Base convergent velocity
        u_base = 1.60 * b * (1.0 - 0.08 * y**2)
        v_base = 0.75 * y * db_dx + 0.20 * np.sin(0.70 * x - 0.5 * t)
        
        # Unsteady wave
        u_unsteady = 0.22 * np.cos(0.85 * x - 1.3 * t) * (1.0 - 0.08 * y)
        v_unsteady = 0.14 * np.sin(0.85 * x - 1.3 * t)
        
        return u_base + u_unsteady, v_base + v_unsteady

    # Runge-Kutta 4 trajectory integrator
    def trace_parcel(x0, y0, t_span, dt=0.01):
        t_arr = np.arange(t_span[0], t_span[1] + dt, dt)
        x_pts = [x0]
        y_pts = [y0]
        cur_x, cur_y = x0, y0
        for cur_t in t_arr[:-1]:
            k1_u, k1_v = velocity_field(cur_x, cur_y, cur_t)
            k2_u, k2_v = velocity_field(cur_x + 0.5 * dt * k1_u, cur_y + 0.5 * dt * k1_v, cur_t + 0.5 * dt)
            k3_u, k3_v = velocity_field(cur_x + 0.5 * dt * k2_u, cur_y + 0.5 * dt * k2_v, cur_t + 0.5 * dt)
            k4_u, k4_v = velocity_field(cur_x + dt * k3_u, cur_y + dt * k3_v, cur_t + dt)
            
            cur_x += (dt / 6.0) * (k1_u + 2*k2_u + 2*k3_u + k4_u)
            cur_y += (dt / 6.0) * (k1_v + 2*k2_v + 2*k3_v + k4_v)
            x_pts.append(cur_x)
            y_pts.append(cur_y)
        return np.array(x_pts), np.array(y_pts), t_arr

    # Grid for background flow arrows (reduced density for maximum clarity)
    x_grid = np.linspace(-3.2, 3.2, 15)
    y_grid = np.linspace(-2.0, 2.0, 10)
    X, Y = np.meshgrid(x_grid, y_grid)
    U, V = velocity_field(X, Y, t=0.0)
    speed = np.sqrt(U**2 + V**2)
    U_norm = U / speed
    V_norm = V / speed

    # Dense grid for streamlines (reduced density)
    xs_dense = np.linspace(-3.5, 3.5, 55)
    ys_dense = np.linspace(-2.3, 2.3, 40)
    XD, YD = np.meshgrid(xs_dense, ys_dense)
    UD, VD = velocity_field(XD, YD, t=0.0)

    # -------------------------------------------------------------------------
    # ROW 1, PANEL 1: EULERIAN PERSPECTIVE (Fixed Spatial Point)
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[1, 0])
    ax1.set_facecolor(PANEL_BG)
    for spine in ax1.spines.values():
        spine.set_edgecolor(BORDER_COLOR)
        spine.set_linewidth(1.3)
    ax1.set_xlim(-3.4, 3.4)
    ax1.set_ylim(-2.2, 2.2)
    ax1.set_aspect('equal')
    ax1.set_xticks(np.arange(-3, 4, 1))
    ax1.set_yticks(np.arange(-2, 3, 1))
    ax1.grid(True, color=GRID_COLOR, linestyle='--', linewidth=0.7, alpha=0.6)
    ax1.set_xlabel("Spatial coordinate $x_1$", fontsize=10.5, labelpad=4)
    ax1.set_ylabel("Spatial coordinate $x_2$", fontsize=10.5, labelpad=4)

    # Streamlines & quiver (subtle background)
    ax1.streamplot(XD, YD, UD, VD, color=STREAM_COLOR, density=0.45,
                   linewidth=0.85, arrowsize=0.75, arrowstyle='->')
    ax1.quiver(X, Y, U_norm, V_norm, color=VECTOR_COLOR, alpha=0.18,
               scale=24, width=0.0035, headwidth=3.2, headlength=4.0)

    # Panel Header & Guiding Question
    ax1.text(0.04, 0.95, "Eulerian — Fixed Point",
             transform=ax1.transAxes, fontsize=14.0, fontweight='bold',
             color=TEXT_TITLE, va='top')
    ax1.text(0.04, 0.88, r"“How does the velocity at $\mathbf{x}_0$ change with time?”",
             transform=ax1.transAxes, fontsize=11.2, fontstyle='italic',
             color=EULER_ACCENT, va='top')

    # Fixed Spatial Probe at center (x0 = 0.0, y0 = 0.0)
    px0, py0 = 0.0, 0.0
    
    # Target reticle
    reticle_outer = Circle((px0, py0), 0.38, fill=False, edgecolor=EULER_ACCENT,
                           linestyle='--', linewidth=1.6, alpha=0.85, zorder=6)
    reticle_mid   = Circle((px0, py0), 0.18, facecolor=EULER_ACCENT, alpha=0.20,
                           edgecolor=EULER_ACCENT, linewidth=1.5, zorder=6)
    reticle_core  = Circle((px0, py0), 0.06, facecolor='#ffffff', edgecolor=EULER_ACCENT, linewidth=1.3, zorder=7)
    ax1.add_patch(reticle_outer)
    ax1.add_patch(reticle_mid)
    ax1.add_patch(reticle_core)
    
    ax1.plot([px0 - 0.50, px0 + 0.50], [py0, py0], color=EULER_ACCENT, linewidth=1.2, alpha=0.8, zorder=6)
    ax1.plot([px0, px0], [py0 - 0.50, py0 + 0.50], color=EULER_ACCENT, linewidth=1.2, alpha=0.8, zorder=6)

    # Prominent label for probe
    ax1.text(px0, py0 - 0.65, r"Fixed Point $\mathbf{x} = \mathbf{x}_0$",
             fontsize=11.5, fontweight='bold', color=EULER_ACCENT, ha='center',
             bbox=dict(boxstyle='round,pad=0.35', facecolor='#19150a', edgecolor=EULER_ACCENT, linewidth=1.1), zorder=10)

    # 3 Velocity vectors at the fixed probe over time
    sc = 0.62
    u_prev, v_prev = 1.95 * np.cos(-0.26), 1.95 * np.sin(-0.26)  # t1: tilted downward
    u0, v0         = 2.25 * np.cos(0.03),  2.25 * np.sin(0.03)   # t2: primary
    u_next, v_next = 2.05 * np.cos(0.32),  2.05 * np.sin(0.32)   # t3: tilted upward

    # Vector 1 (at t1) - dashed slate
    ax1.annotate('', xy=(px0 + sc * u_prev, py0 + sc * v_prev), xytext=(px0, py0),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.36,head_length=0.60",
                                 color="#94a3b8", lw=2.0, linestyle=':', alpha=0.85), zorder=8)
    ax1.text(px0 + sc * u_prev + 0.12, py0 + sc * v_prev - 0.14,
             r"$\mathbf{u}(\mathbf{x}_0, t_1)$", fontsize=11.0, color="#94a3b8", zorder=9)

    # Vector 2 (at t2) - solid bright amber
    ax1.annotate('', xy=(px0 + sc * u0, py0 + sc * v0), xytext=(px0, py0),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.48,head_length=0.80",
                                 color=EULER_ACCENT, lw=3.6, mutation_scale=15), zorder=8)
    ax1.text(px0 + sc * u0 + 0.14, py0 + sc * v0 - 0.02,
             r"$\mathbf{u}(\mathbf{x}_0, t_2)$", fontsize=13.0, fontweight='bold', color=EULER_ACCENT, zorder=9)

    # Vector 3 (at t3) - dashed light slate
    ax1.annotate('', xy=(px0 + sc * u_next, py0 + sc * v_next), xytext=(px0, py0),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.36,head_length=0.60",
                                 color="#cbd5e1", lw=2.0, linestyle='--', alpha=0.90), zorder=8)
    ax1.text(px0 + sc * u_next + 0.12, py0 + sc * v_next + 0.14,
             r"$\mathbf{u}(\mathbf{x}_0, t_3)$", fontsize=11.0, color="#cbd5e1", zorder=9)

    # Arc illustrating local unsteadiness ∂u/∂t
    arc_ang = np.linspace(-0.24, 0.30, 30)
    r_arc = 1.25
    ax1.plot(px0 + r_arc * np.cos(arc_ang), py0 + r_arc * np.sin(arc_ang),
             color=LOCAL_COLOR, linestyle='-', linewidth=2.4, alpha=0.95, zorder=7)
    
    # Callout pill for ∂u/∂t
    ax1.text(px0 + 0.85, py0 + 1.15,
             r"$\frac{\partial \mathbf{u}}{\partial t}$" + " (Local change)",
             fontsize=11.0, color=LOCAL_COLOR, fontweight='bold', va='center', ha='left',
             bbox=dict(boxstyle='round,pad=0.35', facecolor='#081d28', edgecolor=LOCAL_COLOR, linewidth=1.2), zorder=10)
    ax1.plot([px0 + r_arc * np.cos(0.26), px0 + 0.82], [py0 + r_arc * np.sin(0.26), py0 + 1.12],
             color=LOCAL_COLOR, linestyle=':', linewidth=1.4, zorder=9)

    # -------------------------------------------------------------------------
    # ROW 1, PANEL 2: LAGRANGIAN PERSPECTIVE (Moving Fluid Parcel)
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[1, 1])
    ax2.set_facecolor(PANEL_BG)
    for spine in ax2.spines.values():
        spine.set_edgecolor(BORDER_COLOR)
        spine.set_linewidth(1.3)
    ax2.set_xlim(-3.4, 3.4)
    ax2.set_ylim(-2.2, 2.2)
    ax2.set_aspect('equal')
    ax2.set_xticks(np.arange(-3, 4, 1))
    ax2.set_yticks(np.arange(-2, 3, 1))
    ax2.grid(True, color=GRID_COLOR, linestyle='--', linewidth=0.7, alpha=0.6)
    ax2.set_xlabel("Spatial coordinate $x_1$", fontsize=10.5, labelpad=4)
    ax2.set_ylabel("Spatial coordinate $x_2$", fontsize=10.5, labelpad=4)

    # Streamlines & quiver
    ax2.streamplot(XD, YD, UD, VD, color=STREAM_COLOR, density=0.45,
                   linewidth=0.85, arrowsize=0.75, arrowstyle='->')
    ax2.quiver(X, Y, U_norm, V_norm, color=VECTOR_COLOR, alpha=0.18,
               scale=24, width=0.0035, headwidth=3.2, headlength=4.0)

    # Panel Header & Guiding Question
    ax2.text(0.04, 0.95, "Lagrangian — Moving Parcel",
             transform=ax2.transAxes, fontsize=14.0, fontweight='bold',
             color=TEXT_TITLE, va='top')
    ax2.text(0.04, 0.88, r"“How does the velocity change along the parcel trajectory?”",
             transform=ax2.transAxes, fontsize=11.2, fontstyle='italic',
             color=LAGR_ACCENT, va='top')

    # Trace Lagrangian pathline X(t)
    px, py, pt = trace_parcel(x0=-2.8, y0=-0.50, t_span=(0.0, 2.3), dt=0.01)
    
    # Glowing trajectory path
    ax2.plot(px, py, color=LAGR_ACCENT, linewidth=3.8, alpha=0.95, zorder=6)
    ax2.plot(px, py, color='#ffffff', linewidth=1.3, alpha=0.85, zorder=7)

    # Trajectory path label
    ax2.text(px[15] - 0.25, py[15] + 0.38, r"Parcel Trajectory $\mathbf{X}(t)$",
             fontsize=11.5, fontweight='bold', color=LAGR_ACCENT,
             bbox=dict(boxstyle='round,pad=0.32', facecolor='#20101d', edgecolor=LAGR_ACCENT, linewidth=1.1), zorder=10)

    # 3 Snapshot points along trajectory: t1, t2, t3
    idx1 = 25    # t1 (upstream slow)
    idx2 = 115   # t2 (constriction acceleration)
    idx3 = 205   # t3 (downstream)

    for idx, label, t_val in [(idx1, "$t_1$", pt[idx1]),
                              (idx2, "$t_2$", pt[idx2]),
                              (idx3, "$t_3$", pt[idx3])]:
        cx, cy = px[idx], py[idx]
        
        # Parcel droplet
        parcel_circ = Circle((cx, cy), 0.22, facecolor=LAGR_ACCENT, alpha=0.35,
                             edgecolor=LAGR_ACCENT, linewidth=2.0, zorder=8)
        parcel_core = Circle((cx, cy), 0.07, facecolor='#ffffff', edgecolor=LAGR_ACCENT, linewidth=1.4, zorder=9)
        ax2.add_patch(parcel_circ)
        ax2.add_patch(parcel_core)
        
        # Instantaneous velocity arrow u(X(t), t)
        up, vp = velocity_field(cx, cy, t_val)
        v_sc = 0.46
        ax2.annotate('', xy=(cx + v_sc * up, cy + v_sc * vp), xytext=(cx, cy),
                     arrowprops=dict(arrowstyle="-|>,head_width=0.40,head_length=0.70",
                                     color='#ffffff', lw=2.6, mutation_scale=14), zorder=10)
        
        # Velocity vector label cleanly positioned above arrow
        t_sub = label.replace('$', '')
        ax2.text(cx + 0.5 * v_sc * up, cy + 0.5 * v_sc * vp + 0.22,
                 f"$\\mathbf{{u}}(\\mathbf{{X}}({t_sub}), {t_sub})$",
                 fontsize=10.5, color='#ffffff', fontweight='bold', ha='center', va='bottom', zorder=11)
        
        # Label below parcel
        ax2.text(cx, cy - 0.42, f"Parcel at {label}",
                 fontsize=10.5, fontweight='bold', color=LAGR_ACCENT, ha='center', zorder=10)

    # -------------------------------------------------------------------------
    # ACCELERATION DECOMPOSITION INSET CARD AT t2 (Shifted left from right border)
    # -------------------------------------------------------------------------
    mid_x, mid_y = px[idx2], py[idx2]
    
    card_x, card_y = 0.05, -0.38
    card_w, card_h = 2.60, 1.50
    
    rect_box = FancyBboxPatch((card_x, card_y), card_w, card_h,
                              boxstyle="round,pad=0.08,rounding_size=0.18",
                              facecolor="#101828", edgecolor=CARD_BORDER, linewidth=1.3, alpha=0.96, zorder=11)
    ax2.add_patch(rect_box)
    
    # Card Header
    ax2.text(card_x + 0.5 * card_w, card_y + card_h - 0.18,
             r"$\mathbf{Acceleration\ Decomposition\ at\ t_2}$",
             fontsize=10.2, fontweight='bold', color=TEXT_TITLE, ha='center', zorder=12)
    ax2.text(card_x + 0.5 * card_w, card_y + card_h - 0.38,
             r"$\frac{D\mathbf{u}}{Dt} = \frac{\partial\mathbf{u}}{\partial t} + (\mathbf{u}\cdot\nabla)\mathbf{u}$",
             fontsize=9.6, color=TEXT_SUB, ha='center', zorder=12)

    # Orthogonal Vector Triangle:
    # 1. Local acceleration (Cyan): Vertical upward leg
    # 2. Advective acceleration (Purple): Horizontal rightward leg
    # 3. Total Material acceleration (Emerald): Direct hypotenuse
    ox, oy = card_x + 0.46, card_y + 0.26
    leg_h = 0.54
    leg_w = 1.35
    
    # Cyan Vector (Local Unsteadiness) - Vertical
    ax2.annotate('', xy=(ox, oy + leg_h), xytext=(ox, oy),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.34,head_length=0.55",
                                 color=LOCAL_COLOR, lw=2.6, mutation_scale=13), zorder=13)
    ax2.text(ox - 0.08, oy + 0.5 * leg_h, r"$\frac{\partial\mathbf{u}}{\partial t}$" + "\n(Local)",
             fontsize=8.8, color=LOCAL_COLOR, fontweight='bold', ha='right', va='center', zorder=13)

    # Purple Vector (Advective Acceleration) - Horizontal
    ax2.annotate('', xy=(ox + leg_w, oy + leg_h), xytext=(ox, oy + leg_h),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.34,head_length=0.55",
                                 color=ADV_COLOR, lw=2.6, mutation_scale=13), zorder=13)
    ax2.text(ox + 0.5 * leg_w, oy + leg_h + 0.09,
             r"$+(\mathbf{u}\cdot\nabla)\mathbf{u}$" + " Advective (convective)",
             fontsize=8.5, color=ADV_COLOR, fontweight='bold', ha='center', va='bottom', zorder=13)

    # Emerald Vector (Total Material Acceleration) - Hypotenuse
    ax2.annotate('', xy=(ox + leg_w, oy + leg_h), xytext=(ox, oy),
                 arrowprops=dict(arrowstyle="-|>,head_width=0.44,head_length=0.72",
                                 color=TOTAL_COLOR, lw=3.4, mutation_scale=15), zorder=14)
    hyp_angle = np.degrees(np.arctan2(leg_h, leg_w))
    ax2.text(ox + 0.55 * leg_w + 0.08, oy + 0.5 * leg_h - 0.13,
             r"$\mathbf{a} = \frac{D\mathbf{u}}{Dt}$" + " (Total)",
             fontsize=9.6, color=TOTAL_COLOR, fontweight='bold', ha='center', va='top',
             rotation=hyp_angle, zorder=15)

    # Connecting dashed line from parcel at t2 to decomposition card
    ax2.plot([mid_x + 0.20, card_x], [mid_y + 0.20, card_y + 0.50 * card_h],
             color=CARD_BORDER, linestyle=':', linewidth=1.3, zorder=10)

    # -------------------------------------------------------------------------
    # ROW 2: MATHEMATICAL SYNTHESIS STRIP (Wide, Prominent, Self-Explanatory)
    # -------------------------------------------------------------------------
    ax_bar = fig.add_subplot(gs[2, :])
    ax_bar.set_facecolor(CARD_BG)
    for spine in ax_bar.spines.values():
        spine.set_edgecolor(CARD_BORDER)
        spine.set_linewidth(1.4)
    ax_bar.set_xlim(0, 100)
    ax_bar.set_ylim(0, 100)
    ax_bar.axis('off')

    # Draw rounded background container
    bar_bg = FancyBboxPatch((0.5, 3), 99, 94,
                            boxstyle="round,pad=0.2,rounding_size=1.5",
                            facecolor="#0f172a", edgecolor=CARD_BORDER, linewidth=1.4, zorder=1)
    ax_bar.add_patch(bar_bg)

    # Left Term: Total Material Derivative
    ax_bar.text(17, 70, r"$\frac{D\mathbf{u}}{Dt}$",
                fontsize=26.0, fontweight='bold', color=TOTAL_COLOR, ha='center', va='center', zorder=2)
    ax_bar.text(17, 28, "Total Material Change\n(along moving trajectory)",
                fontsize=11.0, fontweight='bold', color=TOTAL_COLOR, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.45', facecolor='#06231a', edgecolor=TOTAL_COLOR, linewidth=1.2), zorder=2)

    # Equals sign
    ax_bar.text(33, 70, "=", fontsize=26.0, fontweight='bold', color=TEXT_TITLE, ha='center', va='center', zorder=2)

    # Middle Term: Local Unsteadiness (Eulerian)
    ax_bar.text(50, 70, r"$\frac{\partial\mathbf{u}}{\partial t}$",
                fontsize=26.0, fontweight='bold', color=LOCAL_COLOR, ha='center', va='center', zorder=2)
    ax_bar.text(50, 28, "Local Change\n(at fixed position)",
                fontsize=11.0, fontweight='bold', color=LOCAL_COLOR, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.45', facecolor='#07222e', edgecolor=LOCAL_COLOR, linewidth=1.2), zorder=2)

    # Plus sign
    ax_bar.text(67, 70, "+", fontsize=26.0, fontweight='bold', color=TEXT_TITLE, ha='center', va='center', zorder=2)

    # Right Term: Advective Transport (Lagrangian spatial change)
    ax_bar.text(83, 70, r"$(\mathbf{u}\cdot\nabla)\mathbf{u}$",
                fontsize=26.0, fontweight='bold', color=ADV_COLOR, ha='center', va='center', zorder=2)
    ax_bar.text(83, 28, "Advective (convective)\n(from motion across flow)",
                fontsize=11.0, fontweight='bold', color=ADV_COLOR, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.45', facecolor='#201230', edgecolor=ADV_COLOR, linewidth=1.2), zorder=2)

    plt.savefig(out_path, dpi=240, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated Simplified Material Derivative Infographic: {out_path}")
    return out_path

generate_material_derivative_infographic = make_infographic

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    make_infographic(target)
