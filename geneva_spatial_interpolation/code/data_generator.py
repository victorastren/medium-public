"""
Geneva Spatial Interpolation Series - Synthetic Data Generator
==============================================================
Generates a synthetic temperature dataset for a coordinate grid in Geneva to simulate
an Urban Heat Island (UHI) scenario. 

Geographic Features Modeled:
- Coordinate space: normalized to [-1.0, 1.0].
- Lake Geneva (Lac Léman): curved crescent shape in the center/northeast. 
  No physical temperature sensors can be placed inside the water.
- Jura Mountains (Northwest): peak elevation up to ~1200m.
- Mont Salève (Southeast): peak elevation up to ~1300m.
- Base Elevation: 375m in the flat urban valley.

Physical/Thermodynamic Temperature Drivers:
- Macro trend: temperature decreases towards the north/east.
- Lapse rate: adiabatic cooling of -0.0065°C per meter elevation increase above 375m.
- Lake breeze cooling: local cooling effect up to -2.5°C at the shoreline, 
  decaying exponentially as distance from the lake increases.
- Weather noise: random Gaussian fluctuations (std = 0.15°C) to simulate instrument error.
"""

import numpy as np
import csv
import os

def is_point_in_lake(x, y):
    """
    Determines if a point (x, y) is inside Lake Geneva (Lac Léman).
    The lake is modeled as a curved crescent shape extending from southwest to northeast.
    Works for both scalar values and NumPy arrays.
    """
    # Centerline quadratic curve of Lac Léman: y = 0.5 * x^2 + 0.3 * x - 0.15
    y_c = 0.5 * x**2 + 0.3 * x - 0.15
    
    # Normalized position along the lake length (-1 to 1)
    t = (x - 0.25) / 0.65
    
    # Half-width tapers to 0 at the tips (t = -1 and t = 1)
    width = 0.15 * (1.0 - t**2)
    
    in_x_bounds = (x >= -0.4) & (x <= 0.9)
    in_width = np.abs(y - y_c) < width
    
    return in_x_bounds & in_width

def get_lake_distance(x, y):
    """
    Computes an approximation of the distance from any land point (x, y)
    to the shoreline of Lake Geneva. If the point is in the lake, distance is 0.
    Works for both scalar values and NumPy arrays.
    """
    # Convert to arrays to support vector math
    x_arr = np.atleast_1d(x)
    y_arr = np.atleast_1d(y)
    
    # 1. Distances to tips (Southwest tip at (-0.4, -0.19) and Northeast tip at (0.9, 0.525))
    dist_to_sw_tip = np.sqrt((x_arr - (-0.4))**2 + (y_arr - (-0.19))**2)
    dist_to_ne_tip = np.sqrt((x_arr - 0.9)**2 + (y_arr - 0.525)**2)
    
    # 2. Distance within mid-lake x-bounds (using simple vertical distance to boundary to ensure continuity)
    y_c = 0.5 * x_arr**2 + 0.3 * x_arr - 0.15
    t = (x_arr - 0.25) / 0.65
    width = 0.15 * (1.0 - t**2)
    dist_to_shore_mid = np.maximum(0.0, np.abs(y_arr - y_c) - width)
    
    # Combine conditions based on x coordinate
    dist = np.zeros_like(x_arr)
    
    sw_mask = x_arr < -0.4
    ne_mask = x_arr > 0.9
    mid_mask = ~(sw_mask | ne_mask)
    
    dist[sw_mask] = dist_to_sw_tip[sw_mask]
    dist[ne_mask] = dist_to_ne_tip[ne_mask]
    dist[mid_mask] = dist_to_shore_mid[mid_mask]
    
    # Return scalar if input was scalar
    if np.isscalar(x):
        return float(dist[0])
    return dist

def get_true_temperature(x, y):
    """
    Computes the true (noiseless) ground truth temperature at coordinate (x, y).
    Works for both scalar values and NumPy arrays.
    """
    # 1. Elevation Calculation
    # Jura peak in northwest (-1, 1), Salève peak in southeast (1, -1)
    elev_jura = 800.0 * np.exp(-((x + 1.0)**2 + (y - 1.0)**2) / 0.8)
    elev_saleve = 900.0 * np.exp(-((x - 1.0)**2 + (y + 1.0)**2) / 0.7)
    elevation = 375.0 + elev_jura + elev_saleve
    
    # 2. Temperature Components
    T_macro = 32.0 - 2.0 * x + 1.2 * y
    T_lapse = -0.0065 * (elevation - 375.0)
    
    dist_lake = get_lake_distance(x, y)
    T_lake = -2.5 * np.exp(-dist_lake / 0.15)
    
    return T_macro + T_lapse + T_lake

def generate_geneva_dataset(n_sensors=100, seed=42):
    """
    Generates a synthetic temperature dataset for a coordinate grid in Geneva.
    
    X and Y coordinates are normalized between -1.0 and 1.0.
    Geographic Features:
    - Lake Geneva (Lac Léman) in the center-east/northeast (no sensors placed inside).
    - Jura Mountains in the northwest (elevation up to 1200m).
    - Mont Salève in the southeast (elevation up to 1300m).
    - Base elevation for city zones is 375m.
    
    Temperature Effects:
    - Macro gradient: cooler to the North/East.
    - Lapse rate: -0.0065°C per meter elevation increase above base (375m).
    - Lake breeze cooling: up to -2.5°C cooling at the shore, decaying outward.
    - Minor random weather fluctuations (noise).
    """
    np.random.seed(seed)
    
    sensors = []
    attempts = 0
    max_attempts = 10000
    
    while len(sensors) < n_sensors and attempts < max_attempts:
        attempts += 1
        x = np.random.uniform(-1.0, 1.0)
        y = np.random.uniform(-1.0, 1.0)
        
        # We cannot place a physical sensor in the deep lake water
        if is_point_in_lake(x, y):
            continue
            
        # Elevation Calculation for metadata
        elev_jura = 800.0 * np.exp(-((x + 1.0)**2 + (y - 1.0)**2) / 0.8)
        elev_saleve = 900.0 * np.exp(-((x - 1.0)**2 + (y + 1.0)**2) / 0.7)
        elevation = 375.0 + elev_jura + elev_saleve
        
        # Get true ground truth temperature and add noise
        t_true = get_true_temperature(x, y)
        noise = np.random.normal(0, 0.15)
        temp = t_true + noise
        
        dist_lake = get_lake_distance(x, y)
        
        sensors.append({
            'sensor_id': f"sensor_{len(sensors):03d}",
            'X': x,
            'Y': y,
            'Elevation': elevation,
            'Temperature': temp,
            'dist_lake': dist_lake
        })
        
    return sensors

if __name__ == "__main__":
    sensors = generate_geneva_dataset(n_sensors=100)
    code_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(code_dir, "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, "sensors_data.csv")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['sensor_id', 'X', 'Y', 'Elevation', 'Temperature', 'dist_lake'])
        writer.writeheader()
        writer.writerows(sensors)
        
    print(f"Geneva UHI Simulation: successfully generated {len(sensors)} land-based sensors.")
    print(f"Saved dataset to {output_path}")
    
    elevations = [s['Elevation'] for s in sensors]
    temps = [s['Temperature'] for s in sensors]
    
    print("\nSimulation Statistics:")
    print(f"Elevation: Min = {np.min(elevations):.1f}m, Max = {np.max(elevations):.1f}m, Mean = {np.mean(elevations):.1f}m")
    print(f"Temperature: Min = {np.min(temps):.3f}°C, Max = {np.max(temps):.3f}°C, Mean = {np.mean(temps):.3f}°C")
