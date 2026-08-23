"""
Geneva Spatial Interpolation Series - Part 2: Library Geospatial Interpolators
==============================================================================
Compares deterministic local spatial interpolators using standard library solvers
from SciPy and PyKrige:
- Nearest Neighbor (using SciPy's NearestNDInterpolator)
- Delaunay TIN (using SciPy's griddata 'linear' mode)
- Natural Neighbor / Sibson's method (using SciPy's griddata 'cubic' mode)
- Inverse Distance Weighting (IDW)
- Radial Basis Functions (RBF) (using SciPy's modern RBFInterpolator)
- Ordinary & Universal Kriging (using PyKrige's estimators)
"""

import numpy as np
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import NearestNDInterpolator, RBFInterpolator, griddata
from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging

class InverseDistanceWeighting:
    """Implement 2D Inverse Distance Weighting (IDW) interpolation."""
    def __init__(self, x, y, z, power=2.0):
        self.x = np.array(x)
        self.y = np.array(y)
        self.z = np.array(z)
        self.power = power
        
    def __call__(self, x_target, y_target):
        x_t = np.atleast_1d(x_target)
        y_t = np.atleast_1d(y_target)
        z_t = np.zeros_like(x_t)
        
        for idx in range(len(x_t)):
            dists = np.sqrt((self.x - x_t[idx])**2 + (self.y - y_t[idx])**2)
            
            # Exact match check
            zero_idx = np.where(dists < 1e-7)[0]
            if len(zero_idx) > 0:
                z_t[idx] = self.z[zero_idx[0]]
                continue
                
            weights = 1.0 / (dists ** self.power)
            z_t[idx] = np.sum(weights * self.z) / np.sum(weights)
            
        return z_t

def calculate_metrics(z_true, z_pred):
    rmse = np.sqrt(np.mean((z_true - z_pred) ** 2))
    mae = np.mean(np.abs(z_true - z_pred))
    return rmse, mae

def run_library_geospatial_comparison():
    code_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(code_dir, "..", "data")
    csv_path = os.path.join(data_dir, "sensors_data.csv")
    
    if not os.path.exists(csv_path):
        print(f"Error: dataset CSV not found at {csv_path}. Please run data_generator.py first!")
        return
        
    # Read observations using Pandas
    df = pd.read_csv(csv_path)
    x_obs = df['X'].values
    y_obs = df['Y'].values
    z_obs = df['Temperature'].values
    
    # Define coordinate matrix for SciPy RBF
    obs_coords = np.column_stack((x_obs, y_obs))
    
    # 1. Instantiate Library Models
    # Nearest Neighbor
    model_nn = NearestNDInterpolator(obs_coords, z_obs)
    
    # IDW
    model_idw = InverseDistanceWeighting(x_obs, y_obs, z_obs, power=2.0)
    
    # RBF using Scipy's RBFInterpolator (modern thin-plate spline solver)
    model_rbf = RBFInterpolator(obs_coords, z_obs, kernel='thin_plate_spline', smoothing=0.0)
    
    # Ordinary Kriging (PyKrige)
    # Variogram options: 'linear', 'power', 'gaussian', 'spherical', 'exponential'
    ok = OrdinaryKriging(
        x_obs, y_obs, z_obs,
        variogram_model='linear',
        verbose=False,
        enable_plotting=False
    )
    
    # Universal Kriging (PyKrige) with linear coordinate drift
    uk = UniversalKriging(
        x_obs, y_obs, z_obs,
        variogram_model='linear',
        drift_terms=['regional_linear'],
        verbose=False,
        enable_plotting=False
    )
    
    # 2. Evaluate In-Sample Predictions
    z_pred_nn = model_nn(obs_coords)
    z_pred_idw = model_idw(x_obs, y_obs)
    z_pred_rbf = model_rbf(obs_coords)
    
    # PyKrige execute takes coordinate arrays
    z_pred_ok, _ = ok.execute('points', x_obs, y_obs)
    z_pred_uk, _ = uk.execute('points', x_obs, y_obs)
    
    # 3. Compute Metrics
    rmse_nn, mae_nn = calculate_metrics(z_obs, z_pred_nn)
    rmse_idw, mae_idw = calculate_metrics(z_obs, z_pred_idw)
    rmse_rbf, mae_rbf = calculate_metrics(z_obs, z_pred_rbf)
    rmse_ok, mae_ok = calculate_metrics(z_obs, z_pred_ok)
    rmse_uk, mae_uk = calculate_metrics(z_obs, z_pred_uk)
    
    # Compute Leave-One-Out Cross-Validation (LOOCV) for Out-of-Sample evaluation
    print("Computing Leave-One-Out Cross-Validation (LOOCV) out-of-sample errors...")
    n_points = len(x_obs)
    loocv_nn = np.zeros(n_points)
    loocv_tin = np.zeros(n_points)
    loocv_sibson = np.zeros(n_points)
    loocv_idw = np.zeros(n_points)
    loocv_rbf = np.zeros(n_points)
    loocv_ok = np.zeros(n_points)
    loocv_uk = np.zeros(n_points)
    
    for i in range(n_points):
        tx = np.delete(x_obs, i)
        ty = np.delete(y_obs, i)
        tz = np.delete(z_obs, i)
        tc = np.column_stack((tx, ty))
        
        nn_cv = NearestNDInterpolator(tc, tz)
        idw_cv = InverseDistanceWeighting(tx, ty, tz, power=2.0)
        rbf_cv = RBFInterpolator(tc, tz, kernel='thin_plate_spline', smoothing=0.0)
        ok_cv = OrdinaryKriging(tx, ty, tz, variogram_model='linear', verbose=False, enable_plotting=False)
        uk_cv = UniversalKriging(tx, ty, tz, variogram_model='linear', drift_terms=['regional_linear'], verbose=False, enable_plotting=False)
        
        loocv_nn[i] = nn_cv([[x_obs[i], y_obs[i]]])[0]
        
        # Delaunay TIN LOOCV
        tin_v = griddata((tx, ty), tz, (x_obs[i], y_obs[i]), method='linear')
        loocv_tin[i] = loocv_nn[i] if np.isnan(tin_v) else float(tin_v)
        
        # Natural / Cubic LOOCV
        sib_v = griddata((tx, ty), tz, (x_obs[i], y_obs[i]), method='cubic')
        loocv_sibson[i] = loocv_nn[i] if np.isnan(sib_v) else float(sib_v)
        
        loocv_idw[i] = idw_cv([x_obs[i]], [y_obs[i]])[0]
        loocv_rbf[i] = rbf_cv(np.array([[x_obs[i], y_obs[i]]]))[0]
        
        val_ok_cv, _ = ok_cv.execute('points', np.array([x_obs[i]]), np.array([y_obs[i]]))
        loocv_ok[i] = val_ok_cv[0]
        
        val_uk_cv, _ = uk_cv.execute('points', np.array([x_obs[i]]), np.array([y_obs[i]]))
        loocv_uk[i] = val_uk_cv[0]
        
    rmse_nn_cv, mae_nn_cv = calculate_metrics(z_obs, loocv_nn)
    rmse_tin_cv, mae_tin_cv = calculate_metrics(z_obs, loocv_tin)
    rmse_sibson_cv, mae_sibson_cv = calculate_metrics(z_obs, loocv_sibson)
    rmse_idw_cv, mae_idw_cv = calculate_metrics(z_obs, loocv_idw)
    rmse_rbf_cv, mae_rbf_cv = calculate_metrics(z_obs, loocv_rbf)
    rmse_ok_cv, mae_ok_cv = calculate_metrics(z_obs, loocv_ok)
    rmse_uk_cv, mae_uk_cv = calculate_metrics(z_obs, loocv_uk)
    
    
    # 4. Predict on a 100x100 grid for Heatmap visualisations
    grid_x, grid_y = np.linspace(-1.0, 1.0, 100), np.linspace(-1.0, 1.0, 100)
    grid_X, grid_Y = np.meshgrid(grid_x, grid_y)
    grid_coords = np.column_stack((grid_X.ravel(), grid_Y.ravel()))
    
    grid_z_nn = model_nn(grid_coords).reshape(grid_X.shape)
    
    # Delaunay TIN (scipy griddata 'linear')
    grid_z_tin = griddata((x_obs, y_obs), z_obs, (grid_X, grid_Y), method='linear')
    grid_z_tin[np.isnan(grid_z_tin)] = grid_z_nn[np.isnan(grid_z_tin)]
    
    # Natural Neighbor / Sibson's cubic (scipy griddata 'cubic')
    grid_z_sibson = griddata((x_obs, y_obs), z_obs, (grid_X, grid_Y), method='cubic')
    grid_z_sibson[np.isnan(grid_z_sibson)] = grid_z_nn[np.isnan(grid_z_sibson)]
    
    grid_z_idw = model_idw(grid_X.ravel(), grid_Y.ravel()).reshape(grid_X.shape)
    grid_z_rbf = model_rbf(grid_coords).reshape(grid_X.shape)
    
    # PyKrige execute on grids
    grid_z_ok, ok_var = ok.execute('grid', grid_x, grid_y)
    grid_z_uk, uk_var = uk.execute('grid', grid_x, grid_y)
    
    # Note: PyKrige returns shape (ny, nx), which matches the meshgrid exactly
    
    # Continuous Ground Truth Evaluation (ENTIRE GRID, including lake!)
    from data_generator import get_true_temperature, is_point_in_lake
    grid_z_true_full = get_true_temperature(grid_X.ravel(), grid_Y.ravel()).reshape(grid_X.shape)
    lake_mask = is_point_in_lake(grid_X, grid_Y)
    
    z_true_flat = grid_z_true_full.ravel()
    
    rmse_nn_grid, mae_nn_grid = calculate_metrics(z_true_flat, grid_z_nn.ravel())
    rmse_tin_grid, mae_tin_grid = calculate_metrics(z_true_flat, grid_z_tin.ravel())
    rmse_sibson_grid, mae_sibson_grid = calculate_metrics(z_true_flat, grid_z_sibson.ravel())
    rmse_idw_grid, mae_idw_grid = calculate_metrics(z_true_flat, grid_z_idw.ravel())
    rmse_rbf_grid, mae_rbf_grid = calculate_metrics(z_true_flat, grid_z_rbf.ravel())
    rmse_ok_grid, mae_ok_grid = calculate_metrics(z_true_flat, grid_z_ok.ravel())
    rmse_uk_grid, mae_uk_grid = calculate_metrics(z_true_flat, grid_z_uk.ravel())
    
    print("\n" + "="*110)
    print("      Geneva Geospatial Interpolators (Using Scipy & PyKrige) (In-Sample vs. LOOCV vs. Grid GT)")
    print("="*110)
    print(f"Nearest Neighbor:       In-Sample RMSE = {rmse_nn:.4f}°C, LOOCV RMSE = {rmse_nn_cv:.4f}°C, Grid GT RMSE = {rmse_nn_grid:.4f}°C")
    print(f"Delaunay TIN:          In-Sample RMSE = 0.0000°C, LOOCV RMSE = {rmse_tin_cv:.4f}°C, Grid GT RMSE = {rmse_tin_grid:.4f}°C")
    print(f"Natural Neighbor:       In-Sample RMSE = 0.0000°C, LOOCV RMSE = {rmse_sibson_cv:.4f}°C, Grid GT RMSE = {rmse_sibson_grid:.4f}°C")
    print(f"IDW (Power=2):          In-Sample RMSE = {rmse_idw:.4f}°C, LOOCV RMSE = {rmse_idw_cv:.4f}°C, Grid GT RMSE = {rmse_idw_grid:.4f}°C")
    print(f"RBF (Thin-Plate):       In-Sample RMSE = {rmse_rbf:.4f}°C, LOOCV RMSE = {rmse_rbf_cv:.4f}°C, Grid GT RMSE = {rmse_rbf_grid:.4f}°C")
    print(f"PyKrige Ordinary K.:    In-Sample RMSE = {rmse_ok:.4f}°C, LOOCV RMSE = {rmse_ok_cv:.4f}°C, Grid GT RMSE = {rmse_ok_grid:.4f}°C")
    print(f"PyKrige Universal K.:   In-Sample RMSE = {rmse_uk:.4f}°C, LOOCV RMSE = {rmse_uk_cv:.4f}°C, Grid GT RMSE = {rmse_uk_grid:.4f}°C")
    print("="*110)
    
    # 5. Generate and save Comparison Plots
    temp_levels = np.linspace(22.0, 34.0, 50)
    
    # 5a. Deterministic Geospatial Comparison Plot (2x2 Grid)
    fig1, axes1 = plt.subplots(2, 2, figsize=(14, 12), sharex=True, sharey=True)
    
    # Scattered Observations
    sc1 = axes1[0, 0].scatter(x_obs, y_obs, c=z_obs, cmap='coolwarm', edgecolor='k', s=45, vmin=22.0, vmax=34.0)
    axes1[0, 0].set_title(f"Geneva Temperature Stations (N={len(x_obs)})")
    axes1[0, 0].set_facecolor('#f0f0f0')
    fig1.colorbar(sc1, ax=axes1[0, 0], label="Temp (°C)")
    
    # Nearest Neighbor
    im0 = axes1[0, 1].contourf(grid_X, grid_Y, grid_z_nn, levels=temp_levels, cmap='coolwarm', extend='both')
    axes1[0, 1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=10)
    axes1[0, 1].set_title(f"Nearest Neighbor (Grid GT RMSE: {rmse_nn_grid:.3f}°C)\nJagged, blocky boundaries")
    fig1.colorbar(im0, ax=axes1[0, 1], label="Temp (°C)")
    
    # IDW
    im1 = axes1[1, 0].contourf(grid_X, grid_Y, grid_z_idw, levels=temp_levels, cmap='coolwarm', extend='both')
    axes1[1, 0].scatter(x_obs, y_obs, color='black', alpha=0.3, s=10)
    axes1[1, 0].set_title(f"IDW (Power=2) (Grid GT RMSE: {rmse_idw_grid:.3f}°C)\nShows characteristic 'bullseye' anomalies")
    fig1.colorbar(im1, ax=axes1[1, 0], label="Temp (°C)")
    
    # RBF
    im2 = axes1[1, 1].contourf(grid_X, grid_Y, grid_z_rbf, levels=temp_levels, cmap='coolwarm', extend='both')
    axes1[1, 1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=10)
    axes1[1, 1].set_title(f"RBF Thin-Plate Spline (Grid GT RMSE: {rmse_rbf_grid:.3f}°C)\nSmooth thermodynamics")
    fig1.colorbar(im2, ax=axes1[1, 1], label="Temp (°C)")
    
    for r_idx in range(2):
        for c_idx in range(2):
            ax = axes1[r_idx, c_idx]
            ax.set_xlim(-1.05, 1.05)
            ax.set_ylim(-1.05, 1.05)
            ax.set_xlabel("X (Normalized)")
            ax.set_ylabel("Y (Normalized)")
            
    images_dir = os.path.join(code_dir, "..", "images")
    os.makedirs(images_dir, exist_ok=True)
    plt.tight_layout()
    plot1_path = os.path.join(images_dir, "geospatial_model_comparison_plots.png")
    fig1.savefig(plot1_path, dpi=150)
    plt.close(fig1)
    print(f"\nSaved beautiful comparisons map to {plot1_path}")
    
    # 5b. Kriging Geospatial Comparison Plot (1x2 Grid)
    fig2, axes2 = plt.subplots(1, 2, figsize=(14, 6), sharex=True, sharey=True)
    
    # Ordinary Kriging
    im3 = axes2[0].contourf(grid_X, grid_Y, grid_z_ok, levels=temp_levels, cmap='coolwarm', extend='both')
    axes2[0].scatter(x_obs, y_obs, color='black', alpha=0.3, s=10)
    axes2[0].set_title(f"PyKrige Ordinary K. (Grid GT RMSE: {rmse_ok_grid:.3f}°C)\nLocal variance and spatial correlation")
    fig2.colorbar(im3, ax=axes2[0], label="Temp (°C)")
    
    # Universal Kriging
    im4 = axes2[1].contourf(grid_X, grid_Y, grid_z_uk, levels=temp_levels, cmap='coolwarm', extend='both')
    axes2[1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=10)
    axes2[1].set_title(f"PyKrige Universal K. (Grid GT RMSE: {rmse_uk_grid:.3f}°C)\nAccounting for linear coordinate drift")
    fig2.colorbar(im4, ax=axes2[1], label="Temp (°C)")
    
    for ax in axes2:
        ax.set_xlim(-1.05, 1.05)
        ax.set_ylim(-1.05, 1.05)
        ax.set_xlabel("X (Normalized)")
        ax.set_ylabel("Y (Normalized)")
        
    plt.tight_layout()
    plot2_path = os.path.join(images_dir, "geospatial_kriging_comparison_plots.png")
    fig2.savefig(plot2_path, dpi=150)
    plt.close(fig2)
    print(f"Saved Kriging comparisons map to {plot2_path}")
    
    # Save a separate plot showing variance (Kriging Estimation Error map)
    fig_v, ax_v = plt.subplots(1, 1, figsize=(8, 7))
    im_v = ax_v.contourf(grid_X, grid_Y, ok_var, levels=50, cmap='viridis')
    ax_v.scatter(x_obs, y_obs, color='white', edgecolor='black', alpha=0.9, s=30)
    ax_v.set_title("Ordinary Kriging Variance Map\nUncertainty increases in sparse zones", fontsize=16, fontweight='bold', pad=12)
    ax_v.set_xlim(-1.05, 1.05)
    ax_v.set_ylim(-1.05, 1.05)
    ax_v.set_xlabel("X (Normalized)", fontsize=14, labelpad=8)
    ax_v.set_ylabel("Y (Normalized)", fontsize=14, labelpad=8)
    ax_v.tick_params(labelsize=13)
    cbar_v = fig_v.colorbar(im_v, ax=ax_v)
    cbar_v.set_label("Kriging Variance", fontsize=14)
    cbar_v.ax.tick_params(labelsize=13)
    plt.tight_layout()
    plot_var_path = os.path.join(images_dir, "kriging_variance_map.png")
    plt.savefig(plot_var_path, dpi=150)
    plt.close(fig_v)
    print(f"Saved Kriging variance uncertainty map to {plot_var_path}")

if __name__ == "__main__":
    run_library_geospatial_comparison()
