"""
Generate Geneva Spatial Gap Illustration (LOOCV vs. Buffered Spatial Gap)
========================================================================
Produces a high-resolution 2-panel schematic map comparing:
Panel A: Ordinary LOOCV - single station x_i withheld, dense neighborhood intact.
         Shows the small nearest-neighbor distance d_i^{min}.
Panel B: Spatial Gap / Buffered Removal - exclusion buffer B(x_i, r) removes all
         observations within radius r, forcing the interpolator to bridge a genuine
         spatial gap, with a much larger d_i^{min}.

Reuses the exact Geneva coordinate space, normalized domain [-1, 1], lake geometry,
and topographic cues for visual continuity with the rest of the series.
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.patheffects as pe

# 1. Load sensor data
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(script_dir, ".."))
data_dir = os.path.join(project_dir, "data") if os.path.exists(os.path.join(project_dir, "data")) else os.path.join(script_dir, "data")
csv_path = os.path.join(data_dir, "sensors_data.csv")
from data_generator import ensure_sensors_data
ensure_sensors_data(csv_path)

sensors_x = []
sensors_y = []
sensor_ids = []

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sensor_ids.append(row['sensor_id'])
        sensors_x.append(float(row['X']))
        sensors_y.append(float(row['Y']))

x_obs = np.array(sensors_x)
y_obs = np.array(sensors_y)
coords = np.column_stack((x_obs, y_obs))
n_sensors = len(x_obs)

# 2. Geometry helpers: Lake Geneva & Elevation
def is_point_in_lake(x, y):
    y_c = 0.5 * x**2 + 0.3 * x - 0.15
    t = (x - 0.25) / 0.65
    width = 0.15 * (1.0 - t**2)
    in_x_bounds = (x >= -0.4) & (x <= 0.9)
    in_width = np.abs(y - y_c) < width
    return in_x_bounds & in_width

def get_elevation(x, y):
    elev_jura = 800.0 * np.exp(-((x + 1.0)**2 + (y - 1.0)**2) / 0.8)
    elev_saleve = 900.0 * np.exp(-((x - 1.0)**2 + (y + 1.0)**2) / 0.7)
    return 375.0 + elev_jura + elev_saleve

# Background grid
grid_1d = np.linspace(-1.05, 1.05, 500)
gx, gy = np.meshgrid(grid_1d, grid_1d)
elevation_grid = get_elevation(gx, gy)
lake_mask = is_point_in_lake(gx, gy).astype(float)

# 3. Target sensor and distances
# Use sensor_057 (consistent with Figure 1)
target_idx = sensor_ids.index("sensor_057")
target_coord = coords[target_idx]
tx, ty = target_coord

# Pairwise distances from target to all sensors
dists = np.linalg.norm(coords - target_coord, axis=1)
dists[target_idx] = np.inf

# Left panel: Ordinary LOOCV
loocv_nearest_idx = np.argmin(dists)
d_loocv_min = dists[loocv_nearest_idx]
loocv_nearest_coord = coords[loocv_nearest_idx]
nx_loo, ny_loo = loocv_nearest_coord

# Right panel: Buffered exclusion
buffer_radius = 0.30
in_buffer_mask = (dists <= buffer_radius)
out_buffer_mask = (dists > buffer_radius) & (np.arange(n_sensors) != target_idx)

buffered_nearest_idx = np.where(out_buffer_mask)[0][np.argmin(dists[out_buffer_mask])]
d_buffered_min = dists[buffered_nearest_idx]
buffered_nearest_coord = coords[buffered_nearest_idx]
nx_buf, ny_buf = buffered_nearest_coord

# 4. Create 2-panel figure
plt.rcParams['font.family'] = 'DejaVu Sans'
fig, axes = plt.subplots(1, 2, figsize=(13.8, 6.6), sharex=True, sharey=True)

# Path effects for enhanced readability of background geography labels
white_halo = [pe.withStroke(linewidth=2.6, foreground='#ffffff', alpha=0.9)]
lake_halo = [pe.withStroke(linewidth=3.0, foreground='#ffffff', alpha=0.92)]

panel_titles = [
    "Ordinary LOOCV\nNearest observation remains close",
    "Nearby Observations Excluded\nExclusion radius ($r = 0.30$)"
]

for idx, ax in enumerate(axes):
    ax.set_facecolor('#f9fafb')
    
    # Subtle elevation contour lines
    ax.contour(gx, gy, elevation_grid, levels=np.arange(400, 1300, 150),
               colors='#d3dbe3', linewidths=0.85, alpha=0.75, linestyles='solid', zorder=1)
    
    # Lake Geneva fill and outline
    ax.contourf(gx, gy, lake_mask, levels=[0.5, 1.5],
                colors=['#d4e8fa'], alpha=0.9, zorder=2)
    ax.contour(gx, gy, lake_mask, levels=[0.5],
               colors=['#7faecf'], linewidths=1.2, zorder=2)
    
    # Geographic labels (tastefully balanced with halo)
    ax.text(-0.84, 0.88, "Jura Mountains", fontsize=11.5, color='#475569',
            fontstyle='italic', weight='bold', ha='center', zorder=3,
            path_effects=white_halo)
    ax.text(0.84, -0.92, "Mont Salève", fontsize=11.5, color='#475569',
            fontstyle='italic', weight='bold', ha='center', zorder=3,
            path_effects=white_halo)
    ax.text(0.61, 0.330, "Lake Geneva", fontsize=13.0, color='#255d88',
            fontstyle='italic', weight='bold', ha='center', rotation=31, zorder=3,
            path_effects=lake_halo)

    if idx == 0:
        # Panel A: LOOCV
        avail_mask = np.ones(n_sensors, dtype=bool)
        avail_mask[target_idx] = False
        
        # 99 Available sensors
        ax.scatter(x_obs[avail_mask], y_obs[avail_mask],
                   c='#1f77b4', s=60, edgecolor='#0f3b60',
                   linewidth=1.0, zorder=3,
                   label=r"Available observations ($N − 1 = 99$)")
        
        # Target sensor
        ax.scatter(tx, ty, c='#d62728', s=160, edgecolor='#5c0a0a',
                   linewidth=1.8, marker='o', zorder=6,
                   label=r"Withheld target sensor $x_i$")
        
        # Target indicator ring
        ax.scatter(tx, ty, facecolor='none', edgecolor='#d62728',
                   s=360, linewidth=1.5, linestyle='--', zorder=5)
        
        # Distance line to nearest neighbor
        ax.plot([tx, nx_loo], [ty, ny_loo], color='#d62728', lw=2.6,
                linestyle='-', zorder=7)
        
        # Highlight nearest neighbor with red outline ring
        ax.scatter(nx_loo, ny_loo, c='#1f77b4', s=120, edgecolor='#d62728',
                   linewidth=2.4, zorder=8,
                   label=rf"Nearest observation ($d_i^{{\min}} = {d_loocv_min:.3f}$)")
        
        # Distance badge pointing to the short connector line
        mid_x = (tx + nx_loo) / 2
        mid_y = (ty + ny_loo) / 2
        ax.annotate(rf"$d_i^{{\min}} = {d_loocv_min:.3f}$" + "\nNearest observation remains close",
                    xy=(mid_x, mid_y), xytext=(0.02, -0.15),
                    fontsize=10.0, fontweight='bold', color='#991b1b',
                    arrowprops=dict(arrowstyle="->", color='#991b1b', lw=1.8,
                                    shrinkA=4, shrinkB=6,
                                    connectionstyle="arc3,rad=-0.12"),
                    bbox=dict(boxstyle="round,pad=0.45", facecolor='#ffffff',
                              edgecolor='#fca5a5', lw=1.2),
                    zorder=9)
        
    else:
        # Panel B: Spatial Gap / Buffered Removal
        # Draw buffer exclusion circle
        buffer_circle = Circle((tx, ty), buffer_radius,
                               facecolor='#fee2e2', edgecolor='#dc2626',
                               linewidth=1.8, linestyle='--', alpha=0.45, zorder=2)
        ax.add_patch(buffer_circle)
        
        # Available sensors outside buffer (90)
        n_excluded = len(np.where(in_buffer_mask)[0])
        n_avail = len(np.where(out_buffer_mask)[0])
        ax.scatter(x_obs[out_buffer_mask], y_obs[out_buffer_mask],
                   c='#1f77b4', s=60, edgecolor='#0f3b60',
                   linewidth=1.0, zorder=3,
                   label=rf"Available observations ($N − {n_excluded + 1} = {n_avail}$)")
        
        # Withheld sensors inside buffer (excluding target itself) marked with red 'x'
        ax.scatter(x_obs[in_buffer_mask], y_obs[in_buffer_mask],
                   c='#dc2626', s=55, marker='x', linewidths=1.8, zorder=5,
                   label=rf"Excluded within radius $r$ ({n_excluded})")
        
        # Target sensor
        ax.scatter(tx, ty, c='#d62728', s=160, edgecolor='#5c0a0a',
                   linewidth=1.8, marker='o', zorder=6,
                   label=r"Withheld target sensor $x_i$")
        
        # Target indicator ring
        ax.scatter(tx, ty, facecolor='none', edgecolor='#d62728',
                   s=360, linewidth=1.5, linestyle='--', zorder=5)
        
        # Distance line to nearest available observation outside buffer
        ax.plot([tx, nx_buf], [ty, ny_buf], color='#dc2626', lw=2.6,
                linestyle='-', zorder=7)
        
        # Highlight nearest available observation outside buffer
        ax.scatter(nx_buf, ny_buf, c='#1f77b4', s=120, edgecolor='#dc2626',
                   linewidth=2.4, zorder=8,
                   label=rf"Nearest observation ($d_i^{{\min}} = {d_buffered_min:.3f}$)")
        
        # Distance badge pointing to the long connector line
        mid_x = (tx + nx_buf) / 2
        mid_y = (ty + ny_buf) / 2
        ax.annotate(rf"$d_i^{{\min}} = {d_buffered_min:.3f}$" + "\n4.4× larger",
                    xy=(mid_x, mid_y), xytext=(0.04, -0.15),
                    fontsize=10.5, fontweight='bold', color='#991b1b',
                    arrowprops=dict(arrowstyle="->", color='#991b1b', lw=1.8,
                                    shrinkA=4, shrinkB=6,
                                    connectionstyle="arc3,rad=-0.10"),
                    bbox=dict(boxstyle="round,pad=0.45", facecolor='#ffffff',
                              edgecolor='#fca5a5', lw=1.2),
                    zorder=9)
        
        # Buffer radius callout on the left side of the circle (well away from the legend box)
        bx = tx + buffer_radius * np.cos(np.radians(165))  # Point on circle at 165 degrees
        by = ty + buffer_radius * np.sin(np.radians(165))
        ax.annotate("Buffer zone\n($r = 0.30$)",
                    xy=(bx, by), xytext=(-0.85, -0.12),
                    fontsize=9.5, fontweight='bold', color='#b91c1c',
                    ha='center', va='center',
                    arrowprops=dict(arrowstyle="->", color='#b91c1c', lw=1.6,
                                    shrinkA=2, shrinkB=2,
                                    connectionstyle="arc3,rad=-0.10"),
                    bbox=dict(boxstyle="round,pad=0.35", facecolor='#fff5f5',
                              edgecolor='#fca5a5', lw=1.0),
                    zorder=9)

    # Styling and formatting
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_xlabel("X (Normalized)", fontsize=12, labelpad=8)
    if idx == 0:
        ax.set_ylabel("Y (Normalized)", fontsize=12, labelpad=8)
    ax.set_title(panel_titles[idx], fontsize=13, fontweight='bold', pad=12, color='#1f2328')
    ax.tick_params(labelsize=11)
    
    # Grid lines (very faint)
    ax.grid(True, linestyle=':', color='#e2e8f0', alpha=0.8, zorder=1)
    
    # Legend with well-balanced font size
    leg = ax.legend(loc='lower left', frameon=True, facecolor='#ffffff',
                    edgecolor='#cbd5e1', framealpha=0.96, fontsize=12.2,
                    borderpad=0.38, labelspacing=0.26, handletextpad=0.45)
    leg.set_zorder(10)
    
    # Spines
    for spine in ax.spines.values():
        spine.set_color('#cbd5e1')
        spine.set_linewidth(1.0)

plt.tight_layout()

# Save PNG
output_dir = os.path.join(project_dir, "images") if os.path.exists(os.path.join(project_dir, "images")) else os.path.join(script_dir, "images")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "geneva_spatial_gap_comparison.png")
fig.savefig(output_path, dpi=200, bbox_inches='tight')
plt.close(fig)
print(f"[OK] Saved spatial gap plot to {output_path}")
