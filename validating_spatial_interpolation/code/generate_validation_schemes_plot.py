"""
Generate Geneva Validation Schemes Illustration (LOOCV vs. Holdout Subset)
==========================================================================
Produces a high-resolution 2-panel schematic map comparing:
Panel A: Leave-One-Out Cross-Validation (LOOCV) - 1 sensor withheld, 99 available.
Panel B: Holdout Validation (Subset H) - 20 sensors withheld, 80 available.

Reuses the exact Geneva coordinate space, normalized domain [-1, 1], lake geometry,
and topographic cues for visual continuity with the rest of the series.
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
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
n_sensors = len(x_obs)

# 2. Define Lake Geneva and Elevation geometry
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

# High-resolution background grid (500x500) for smooth contours
grid_1d = np.linspace(-1.05, 1.05, 500)
gx, gy = np.meshgrid(grid_1d, grid_1d)
elevation_grid = get_elevation(gx, gy)
lake_mask = is_point_in_lake(gx, gy).astype(float)

# 3. Subsets selection
# Panel A: Representative sensor with well-sampled neighborhood (e.g. sensor_057)
# Let's locate sensor_057
target_idx = sensor_ids.index("sensor_057")

# Panel B: Holdout - 20 sensors (20%)
np.random.seed(42)
holdout_indices = np.random.choice(n_sensors, size=20, replace=False)
available_b_mask = np.ones(n_sensors, dtype=bool)
available_b_mask[holdout_indices] = False

# 4. Create 2-panel figure
plt.rcParams['font.family'] = 'DejaVu Sans'
fig, axes = plt.subplots(1, 2, figsize=(13.8, 6.6), sharex=True, sharey=True)

# Path effects for enhanced readability of background geography labels
white_halo = [pe.withStroke(linewidth=2.6, foreground='#ffffff', alpha=0.9)]
lake_halo = [pe.withStroke(linewidth=3.0, foreground='#ffffff', alpha=0.92)]

panel_titles = [
    "Leave-One-Out Cross-Validation (LOOCV)\nSingle Sensor Withheld (Iteration i of N = 100)",
    "Holdout Validation (Example Subset H)\nA Subset of Sensors Withheld Simultaneously (|H| = 20)"
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
                   label=f"Available observations (N − 1 = 99)")
        
        # 1 Withheld sensor
        tx = x_obs[target_idx]
        ty = y_obs[target_idx]
        
        ax.scatter(tx, ty, c='#d62728', s=160, edgecolor='#5c0a0a',
                   linewidth=1.8, marker='o', zorder=5,
                   label=r"Withheld target sensor $x_i$")
        
        # Target indicator ring
        ax.scatter(tx, ty, facecolor='none', edgecolor='#d62728',
                   s=360, linewidth=1.5, linestyle='--', zorder=4)
        
        # Clean, lightweight callout arrow
        ax.annotate("Target sensor x_i withheld",
                    xy=(tx, ty), xytext=(0.14, -0.04),
                    fontsize=10.5, fontweight='bold', color='#991b1b',
                    arrowprops=dict(arrowstyle="->", color='#991b1b', lw=1.8,
                                    shrinkA=3, shrinkB=8,
                                    connectionstyle="arc3,rad=-0.14"),
                    bbox=dict(boxstyle="round,pad=0.4", facecolor='#ffffff',
                              edgecolor='#fca5a5', lw=1.1),
                    zorder=6)
        
    else:
        # Panel B: Holdout Subset H
        # 80 Available observations
        ax.scatter(x_obs[available_b_mask], y_obs[available_b_mask],
                   c='#1f77b4', s=60, edgecolor='#0f3b60',
                   linewidth=1.0, zorder=3,
                   label="Available observations (N − |H| = 80)")
        
        # 20 Withheld holdout sensors (clean solid markers, no buffer-like halos)
        ax.scatter(x_obs[~available_b_mask], y_obs[~available_b_mask],
                   c='#d62728', s=95, edgecolor='#5c0a0a',
                   linewidth=1.5, marker='o', zorder=5,
                   label="Withheld holdout subset H (|H| = 20)")

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
                    edgecolor='#cbd5e1', framealpha=0.96, fontsize=12.8,
                    borderpad=0.40, labelspacing=0.30, handletextpad=0.5)
    leg.set_zorder(10)
    
    # Spines
    for spine in ax.spines.values():
        spine.set_color('#cbd5e1')
        spine.set_linewidth(1.0)

plt.tight_layout()

# Save PNG
output_dir = os.path.join(project_dir, "images") if os.path.exists(os.path.join(project_dir, "images")) else os.path.join(script_dir, "images")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "geneva_validation_schemes.png")
fig.savefig(output_path, dpi=200, bbox_inches='tight')
plt.close(fig)
print(f"[OK] Saved improved schematic plot to {output_path}")
