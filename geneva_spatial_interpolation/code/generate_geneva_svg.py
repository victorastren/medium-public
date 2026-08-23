"""
Geneva Spatial Interpolation Series - Topography SVG Generator
==============================================================
Generates a beautiful topography and weather sensor SVG map representing the physical
simulation domain of Geneva (Jura Mountains, Lac Léman, Mont Salève, and city valley).
"""

import numpy as np
import os
from data_generator import is_point_in_lake, generate_geneva_dataset

def get_elevation(x, y):
    """
    Computes the elevation (in meters) at a given normalized coordinate (x, y).
    Combines two Gaussian peaks (Jura and Salève) with a base valley elevation of 375m.
    """
    elev_jura = 800.0 * np.exp(-((x + 1.0)**2 + (y - 1.0)**2) / 0.8)
    elev_saleve = 900.0 * np.exp(-((x - 1.0)**2 + (y + 1.0)**2) / 0.7)
    return 375.0 + elev_jura + elev_saleve

def get_topo_color(elevation):
    """
    Maps an elevation value to an RGB color hex string representing a topographic ramp.
    Lowlands (375m) -> Green
    Midlands (600m-900m) -> Yellow/Light Brown
    High Peaks (1200m+) -> Dark Grey/White
    """

    # Normalize elevation from 375 to 1300
    norm = (elevation - 375.0) / (1300.0 - 375.0)
    norm = np.clip(norm, 0.0, 1.0)
    
    # Simple color ramp: Low (green) -> Mid (yellow-brown) -> High (grey-white)
    if norm < 0.25:
        # Green to light green
        t = norm / 0.25
        r = int(46 + t * (102 - 46))
        g = int(125 + t * (187 - 125))
        b = int(50 + t * (106 - 50))
    elif norm < 0.6:
        # Light green to light brown
        t = (norm - 0.25) / 0.35
        r = int(102 + t * (215 - 102))
        g = int(187 + t * (180 - 187))
        b = int(106 + t * (120 - 106))
    elif norm < 0.85:
        # Light brown to dark grey-brown
        t = (norm - 0.6) / 0.25
        r = int(215 + t * (120 - 215))
        g = int(180 + t * (110 - 180))
        b = int(120 + t * (100 - 120))
    else:
        # Grey-brown to white/light grey (peaks)
        t = (norm - 0.85) / 0.15
        r = int(120 + t * (240 - 120))
        g = int(110 + t * (240 - 110))
        b = int(100 + t * (240 - 100))
        
    return f"rgb({r},{g},{b})"

def create_svg():
    """
    Renders the Geneva topography and sensor layout as an SVG file.
    Creates a 120x120 cell grid representing elevation gradients and Lake Geneva water,
    superimposes the weather sensor markers, adds geographical text labels, and saves the file.
    """
    # Grid dimensions
    n_cells = 120
    cell_size = 4.5 # SVG pixels per cell
    pad = 40 # padding for margins/legend
    width = int(n_cells * cell_size + pad * 2) # ~620px
    height = int(n_cells * cell_size + pad * 2 - 30) # ~590px
    grid_bound_w = n_cells * cell_size
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" style="background-color: #1e1e1e; font-family: sans-serif; max-width: 650px; display: block; margin: 0 auto;">')
    
    # Title
    svg.append(f'<text x="{width // 2}" y="35" text-anchor="middle" fill="#ffffff" font-size="18" font-weight="bold">Geneva Topographic Simulation &amp; Weather Sensors</text>')
    
    # Draw Background Grid representing elevation and lake
    for r in range(n_cells):
        for c in range(n_cells):
            # Map grid columns/rows to normalized coordinates [-1.1, 1.1]
            gx = -1.1 + (c / (n_cells - 1)) * 2.2
            gy = 1.1 - (r / (n_cells - 1)) * 2.2 # invert y for SVG coordinate system
            
            x_svg = pad + c * cell_size
            y_svg = pad + r * cell_size
            
            if is_point_in_lake(gx, gy):
                # Lake Geneva color
                color = "#2b6cb0"
            else:
                elevation = get_elevation(gx, gy)
                color = get_topo_color(elevation)
                
            svg.append(f'  <rect x="{x_svg}" y="{y_svg}" width="{cell_size}" height="{cell_size}" fill="{color}" stroke="none" />')
            
    # Draw shoreline contour (simple outline for beauty)
    # We'll just draw a boundary indicator box around the whole grid
    grid_bound_w = n_cells * cell_size
    svg.append(f'  <rect x="{pad}" y="{pad}" width="{grid_bound_w}" height="{grid_bound_w}" fill="none" stroke="#4a5568" stroke-width="1.5" />')
    
    # Load and render weather sensors
    sensors = generate_geneva_dataset(n_sensors=100)
    for s in sensors:
        # Convert coordinate from [-1, 1] to grid index
        # [-1.1, 1.1] was the grid bounds, let's map it:
        # x_norm = (s['X'] + 1.1) / 2.2
        # cx = pad + x_norm * grid_bound_w
        cx = pad + ((s['X'] + 1.1) / 2.2) * grid_bound_w
        cy = pad + ((1.1 - s['Y']) / 2.2) * grid_bound_w # invert Y
        
        # Circle marker for sensor
        svg.append(f'  <circle cx="{cx:.2f}" cy="{cy:.2f}" r="3.5" fill="#f56565" stroke="#ffffff" stroke-width="0.8" />')
        
    # Draw geographical labels
    # Jura label in northwest
    jx = pad + 0.15 * grid_bound_w
    jy = pad + 0.15 * grid_bound_w
    svg.append(f'  <text x="{jx}" y="{jy}" fill="#e2e8f0" font-size="10" font-weight="bold" font-style="italic" filter="drop-shadow(0px 1px 2px rgba(0,0,0,0.8))">Jura Mountains</text>')
    
    # Salève label in southeast
    sx = pad + 0.70 * grid_bound_w
    sy = pad + 0.85 * grid_bound_w
    svg.append(f'  <text x="{sx}" y="{sy}" fill="#e2e8f0" font-size="10" font-weight="bold" font-style="italic" filter="drop-shadow(0px 1px 2px rgba(0,0,0,0.8))">Mont Salève</text>')

    # Lac Léman Label
    lx = pad + 0.60 * grid_bound_w
    ly = pad + 0.45 * grid_bound_w
    svg.append(f'  <text x="{lx}" y="{ly}" fill="#ffffff" font-size="11" font-weight="bold" filter="drop-shadow(0px 1px 2px rgba(0,0,0,0.8))">Lac Léman</text>')
    
    # City center Label
    cx = pad + 0.40 * grid_bound_w
    cy = pad + 0.55 * grid_bound_w
    svg.append(f'  <text x="{cx}" y="{cy}" fill="#ffd700" font-size="9" font-weight="bold" filter="drop-shadow(0px 1px 2px rgba(0,0,0,0.8))">Geneva (City)</text>')
    
    # Legend at the bottom
    legend_y = pad + grid_bound_w + 20
    
    # Legend color bars labels
    svg.append(f'  <text x="{pad}" y="{legend_y + 12}" fill="#e2e8f0" font-size="10">Elevation Legend:</text>')
    
    # Colormap values (draw little blocks)
    legend_intervals = [
        ("Lake", "#2b6cb0"),
        ("375m (Valley)", get_topo_color(375.0)),
        ("600m", get_topo_color(600.0)),
        ("900m", get_topo_color(900.0)),
        ("1200m+ (Peaks)", get_topo_color(1200.0)),
    ]
    
    lx_offset = pad + 110
    for label, col in legend_intervals:
        svg.append(f'  <rect x="{lx_offset}" y="{legend_y}" width="15" height="15" fill="{col}" stroke="#718096" stroke-width="0.5" />')
        svg.append(f'  <text x="{lx_offset + 20}" y="{legend_y + 11}" fill="#e2e8f0" font-size="9">{label}</text>')
        lx_offset += 105
        
    # Sensor legend item
    svg.append(f'  <circle cx="{lx_offset}" cy="{legend_y + 7}" r="3.5" fill="#f56565" stroke="#ffffff" stroke-width="0.8" />')
    svg.append(f'  <text x="{lx_offset + 10}" y="{legend_y + 11}" fill="#e2e8f0" font-size="9">Sensor (N=100)</text>')
    
    svg.append('</svg>')
    
    code_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(code_dir, "..", "images")
    os.makedirs(images_dir, exist_ok=True)
    output_path = os.path.join(images_dir, "geneva_topography.svg")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(svg))
    print(f"Generated topography SVG at: {output_path}")

if __name__ == "__main__":
    create_svg()
