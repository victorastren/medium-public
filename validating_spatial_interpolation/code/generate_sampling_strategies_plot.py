"""
Generate Geneva 4-Panel Sampling Strategies Illustration
========================================================
Produces a publication-quality 2x2 comparison map:
Panel A: Leave-One-Out Cross-Validation (LOOCV)
Panel B: Random K-Fold Cross-Validation
Panel C: Spatial Block Cross-Validation
Panel D: Buffered Validation

All panels share:
- Identical Geneva sensor locations (100 stations)
- Identical coordinate space [-1.05, 1.05]
- Identical elevation contours and Lake Geneva geometry
- Enhanced font sizes for terrain labels (Jura Mountains, Mont Salève, Lake Geneva)
- Enhanced font sizes for callout boxes and legends
- High legibility and contrast across Retina and mobile displays
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
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

# Background grid (500x500)
grid_1d = np.linspace(-1.05, 1.05, 500)
gx, gy = np.meshgrid(grid_1d, grid_1d)
elevation_grid = get_elevation(gx, gy)
lake_mask = is_point_in_lake(gx, gy).astype(float)

# 3. Strategy Partitioning
# Target sensor for LOOCV and Buffered: sensor_057
target_idx = sensor_ids.index("sensor_057")
tx, ty = coords[target_idx]

# Panel B: Random K=5 folds (20 sensors per fold)
np.random.seed(42)
shuffled_indices = np.random.permutation(n_sensors)
fold_size = 20
random_val_indices = shuffled_indices[:fold_size]
random_val_mask = np.zeros(n_sensors, dtype=bool)
random_val_mask[random_val_indices] = True

# Panel C: Spatial Block (Quadrant NW: x in [-1.05, 0.0], y in [0.0, 1.05])
block_val_mask = (x_obs <= 0.0) & (y_obs >= 0.0)
n_block_sensors = np.sum(block_val_mask)

# Panel D: Buffered Validation (radius r = 0.30)
buffer_radius = 0.30
dists_target = np.linalg.norm(coords - coords[target_idx], axis=1)
in_buffer_mask = (dists_target <= buffer_radius) & (np.arange(n_sensors) != target_idx)
out_buffer_mask = (dists_target > buffer_radius)
n_buffer_neighbors = np.sum(in_buffer_mask)

# 4. Create 2x2 Figure
plt.rcParams['font.family'] = 'DejaVu Sans'
fig, axes = plt.subplots(2, 2, figsize=(15.2, 15.2), sharex=True, sharey=True)

panel_configs = [
    {
        "ax": axes[0, 0],
        "title": "A. Leave-One-Out Cross-Validation (LOOCV)",
        "subtitle": "One sensor withheld · $N - 1 = 99$ observations available",
    },
    {
        "ax": axes[0, 1],
        "title": "B. Random $K$-Fold Cross-Validation ($K = 5$)",
        "subtitle": "One random fold withheld (20 sensors) · Spatially dispersed across domain",
    },
    {
        "ax": axes[1, 0],
        "title": "C. Spatial Block Cross-Validation",
        "subtitle": f"One block withheld ({n_block_sensors} sensors) · Contiguous unsampled region",
    },
    {
        "ax": axes[1, 1],
        "title": "D. Buffered Validation ($r = 0.30$)",
        "subtitle": f"Target + {n_buffer_neighbors} nearby observations excluded · Prescribed spatial buffer",
    },
]

# Path effects for background labels
white_halo = [pe.withStroke(linewidth=2.6, foreground='#ffffff', alpha=0.9)]
lake_halo = [pe.withStroke(linewidth=3.0, foreground='#ffffff', alpha=0.92)]

for p_idx, p in enumerate(panel_configs):
    ax = p["ax"]
    ax.set_facecolor('#f9fafb')
    
    # Subtle elevation contours
    ax.contour(gx, gy, elevation_grid, levels=np.arange(400, 1300, 150),
               colors='#d3dbe3', linewidths=0.9, alpha=0.75, linestyles='solid', zorder=1)
    
    # Lake Geneva fill and outline
    ax.contourf(gx, gy, lake_mask, levels=[0.5, 1.5],
                colors=['#d4e8fa'], alpha=0.9, zorder=2)
    ax.contour(gx, gy, lake_mask, levels=[0.5],
               colors=['#7faecf'], linewidths=1.3, zorder=2)
    
    # Tastefully balanced background geography labels with subtle halo
    ax.text(-0.84, 0.88, "Jura Mountains", fontsize=11.5, color='#475569',
            fontstyle='italic', weight='bold', ha='center', zorder=3,
            path_effects=white_halo)
    ax.text(0.84, -0.92, "Mont Salève", fontsize=11.5, color='#475569',
            fontstyle='italic', weight='bold', ha='center', zorder=3,
            path_effects=white_halo)
    ax.text(0.61, 0.330, "Lake Geneva", fontsize=13.0, color='#255d88',
            fontstyle='italic', weight='bold', ha='center', rotation=31, zorder=3,
            path_effects=lake_halo)
    
    # Plot content according to strategy
    if p_idx == 0:
        # --- PANEL A: LOOCV ---
        avail_mask = np.ones(n_sensors, dtype=bool)
        avail_mask[target_idx] = False
        
        # 99 Available sensors (Blue)
        ax.scatter(x_obs[avail_mask], y_obs[avail_mask],
                   c='#1f77b4', s=62, edgecolor='#0f3b60',
                   linewidth=1.1, zorder=4,
                   label="Available observations (99)")
        
        # 1 Withheld target sensor (Red)
        ax.scatter(tx, ty, c='#d62728', s=155, edgecolor='#5c0a0a',
                   linewidth=2.0, marker='o', zorder=6,
                   label=r"Withheld target $\mathbf{x}_i$")
        
        # Target dashed ring
        ax.scatter(tx, ty, facecolor='none', edgecolor='#d62728',
                   s=360, linewidth=1.6, linestyle='--', zorder=5)
        
        # Shortened punchy callout in Lake Geneva pointing to target
        ax.annotate("Target sensor withheld",
                    xy=(tx, ty), xytext=(0.04, -0.06),
                    fontsize=13.5, fontweight='bold', color='#991b1b',
                    arrowprops=dict(arrowstyle="->", color='#991b1b', lw=2.2,
                                    shrinkA=3, shrinkB=7,
                                    connectionstyle="arc3,rad=-0.12"),
                    bbox=dict(boxstyle="round,pad=0.45", facecolor='#ffffff',
                              edgecolor='#fca5a5', lw=1.3, alpha=0.98),
                    zorder=8)

    elif p_idx == 1:
        # --- PANEL B: Random K-fold ---
        # 80 Available observations (Blue)
        ax.scatter(x_obs[~random_val_mask], y_obs[~random_val_mask],
                   c='#1f77b4', s=62, edgecolor='#0f3b60',
                   linewidth=1.1, zorder=4,
                   label="Available observations (80)")
        
        # 20 Withheld fold sensors (Red)
        ax.scatter(x_obs[random_val_mask], y_obs[random_val_mask],
                   c='#d62728', s=85, edgecolor='#5c0a0a',
                   linewidth=1.6, marker='o', zorder=5,
                   label=r"Withheld fold $H_k$ (20)")

        # Shortened punchy callout badge in Lake Geneva
        ax.text(0.24, 0.04, "One random fold withheld",
                fontsize=13.5, fontweight='bold', color='#991b1b',
                ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.45", facecolor='#ffffff',
                          edgecolor='#fca5a5', lw=1.3, alpha=0.98),
                zorder=8)

    elif p_idx == 2:
        # --- PANEL C: Spatial Blocking ---
        # Draw 2x2 block grid lines across domain
        ax.axvline(0.0, color='#94a3b8', linestyle=':', linewidth=1.4, zorder=3)
        ax.axhline(0.0, color='#94a3b8', linestyle=':', linewidth=1.4, zorder=3)
        
        # Shaded background for the withheld block (NW quadrant)
        rect = Rectangle((-1.05, 0.0), 1.05, 1.05,
                         facecolor='#fee2e2', edgecolor='#dc2626',
                         linewidth=2.0, linestyle='--', alpha=0.45, zorder=2)
        ax.add_patch(rect)
        
        # Block labels
        ax.text(-0.62, 0.58, "Withheld block $H_b$\n(22 sensors)", fontsize=13.5, fontweight='bold',
                color='#b91c1c', ha='center', va='center', alpha=0.98, zorder=3,
                bbox=dict(boxstyle="round,pad=0.44", facecolor='#ffffff', edgecolor='#fca5a5', lw=1.2, alpha=0.96))
        ax.text(-0.20, 0.84, "Block 1", fontsize=13.0, fontstyle='italic', weight='bold',
                color='#64748b', ha='center', va='center', zorder=3, path_effects=white_halo)
        ax.text(0.20, 0.84, "Block 2", fontsize=13.0, fontstyle='italic', weight='bold',
                color='#64748b', ha='center', va='center', zorder=3, path_effects=white_halo)
        ax.text(-0.25, -0.15, "Block 3", fontsize=13.0, fontstyle='italic', weight='bold',
                color='#64748b', ha='center', va='center', zorder=3, path_effects=white_halo)
        ax.text(0.48, -0.34, "Block 4", fontsize=13.0, fontstyle='italic', weight='bold',
                color='#64748b', ha='center', va='center', zorder=3, path_effects=white_halo)
        
        # 78 Available observations (Blue)
        ax.scatter(x_obs[~block_val_mask], y_obs[~block_val_mask],
                   c='#1f77b4', s=62, edgecolor='#0f3b60',
                   linewidth=1.1, zorder=4,
                   label="Available observations (78)")
        
        # 22 Withheld block observations (Red)
        ax.scatter(x_obs[block_val_mask], y_obs[block_val_mask],
                   c='#d62728', s=85, edgecolor='#5c0a0a',
                   linewidth=1.6, marker='o', zorder=5,
                   label=r"Withheld block $H_b$ (22)")

        # Shortened punchy callout badge in Lake Geneva
        ax.text(0.24, 0.04, "One geographic block withheld",
                fontsize=13.5, fontweight='bold', color='#991b1b',
                ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.45", facecolor='#ffffff',
                          edgecolor='#fca5a5', lw=1.3, alpha=0.98),
                zorder=8)

    elif p_idx == 3:
        # --- PANEL D: Buffered Validation ---
        # Draw exclusion buffer circle B(x_i, r)
        buf_circle = Circle((tx, ty), buffer_radius,
                            facecolor='#fee2e2', edgecolor='#dc2626',
                            linewidth=2.0, linestyle='--', alpha=0.45, zorder=2)
        ax.add_patch(buf_circle)
        
        # Radius annotation arrow inside buffer
        rad_angle = np.deg2rad(40)
        rx = tx + buffer_radius * np.cos(rad_angle)
        ry = ty + buffer_radius * np.sin(rad_angle)
        ax.annotate("", xy=(rx, ry), xytext=(tx, ty),
                    arrowprops=dict(arrowstyle="<->", color='#b91c1c', lw=1.8),
                    zorder=6)
        ax.text((tx + rx)/2 + 0.02, (ty + ry)/2 - 0.02, "$r = 0.30$",
                fontsize=13.5, fontweight='bold', color='#b91c1c', zorder=7,
                bbox=dict(boxstyle="round,pad=0.26", facecolor='#ffffff', edgecolor='#fca5a5', lw=1.0, alpha=0.94))
        
        # Available observations outside buffer (Blue)
        ax.scatter(x_obs[out_buffer_mask], y_obs[out_buffer_mask],
                   c='#1f77b4', s=62, edgecolor='#0f3b60',
                   linewidth=1.1, zorder=4,
                   label="Available observations (90)")
        
        # Excluded buffer neighbor sensors (Muted Red Crosses)
        ax.scatter(x_obs[in_buffer_mask], y_obs[in_buffer_mask],
                   c='#b91c1c', s=82, linewidth=2.6, marker='x', zorder=5,
                   label=r"Buffer excluded sensors (9)")
        
        # Withheld target sensor (Red circle with dashed halo)
        ax.scatter(tx, ty, c='#d62728', s=155, edgecolor='#5c0a0a',
                   linewidth=2.0, marker='o', zorder=6,
                   label=r"Withheld target $\mathbf{x}_i$")
        ax.scatter(tx, ty, facecolor='none', edgecolor='#d62728',
                   s=360, linewidth=1.6, linestyle='--', zorder=5)

        # Shortened punchy callout badge in Lake Geneva
        ax.text(0.24, 0.04, r"Target + observations within $r$ excluded",
                fontsize=13.5, fontweight='bold', color='#991b1b',
                ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.45", facecolor='#ffffff',
                          edgecolor='#fca5a5', lw=1.3, alpha=0.98),
                zorder=8)

    # Styling and formatting
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    
    # Titles
    full_title = f"{p['title']}\n{p['subtitle']}"
    ax.set_title(full_title, fontsize=13.8, fontweight='bold', pad=12, color='#1f2328')
    
    # Axis labels
    if p_idx in [2, 3]:
        ax.set_xlabel("X (Normalized)", fontsize=12.5, labelpad=8)
    if p_idx in [0, 2]:
        ax.set_ylabel("Y (Normalized)", fontsize=12.5, labelpad=8)
    ax.tick_params(labelsize=11.5)
    
    # Grid
    ax.grid(True, linestyle=':', color='#e2e8f0', alpha=0.8, zorder=1)
    
    # Prominently enlarged Legend Font Size at lower left (15.0pt)
    leg = ax.legend(loc='lower left', frameon=True, facecolor='#ffffff',
                    edgecolor='#cbd5e1', framealpha=0.97, fontsize=15.0,
                    borderpad=0.32, labelspacing=0.20, handletextpad=0.35)
    leg.set_zorder(10)
    
    # Spines
    for spine in ax.spines.values():
        spine.set_color('#cbd5e1')
        spine.set_linewidth(1.0)

plt.tight_layout(h_pad=3.2, w_pad=3.2)

# Save PNG
output_dir = os.path.join(project_dir, "images") if os.path.exists(os.path.join(project_dir, "images")) else os.path.join(script_dir, "images")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "geneva_sampling_strategies_comparison.png")
fig.savefig(output_path, dpi=200, bbox_inches='tight')
plt.close(fig)
print(f"[OK] Successfully saved 4-panel comparison plot with increased font sizes to: {output_path}")
