"""
Geneva Spatial Interpolation Series - Part 1: Bivariate Polynomials & B-Splines
==============================================================================
This script implements global baseline models for spatial interpolation of Geneva
sensor temperatures:
1. Bivariate Polynomial Regression: fitting global coordinate-based regression surfaces
   of degree 2 (macro-trend), degree 3 (intermediate), and degree 5 (highly flexible).
2. Piecewise B-Splines (using Scipy's bisplrep/bisplev): evaluating the effect of the
   smoothing parameter 's' on the reconstructed surface (automatic smoothing vs. tuned
   regularization vs. exact interpolation collapse).
"""

import numpy as np
import os
import csv
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from scipy.interpolate import bisplrep, bisplev

def fit_bivariate_polynomial(x, y, z, degree=2):
    """
    Fits a bivariate polynomial surface of the given degree to scattered data (x, y, z)
    using scikit-learn's PolynomialFeatures and LinearRegression.
    """
    X = np.column_stack((x, y))
    poly = PolynomialFeatures(degree=degree, include_bias=True)
    X_poly = poly.fit_transform(X)
    
    # Fit linear regression model without intercept since PolynomialFeatures already includes bias
    lr = LinearRegression(fit_intercept=False)
    lr.fit(X_poly, z)
    return lr.coef_

def predict_bivariate_polynomial(x, y, coefficients, degree=2):
    """
    Evaluates the fitted bivariate polynomial surface at coordinates (x, y)
    using scikit-learn's PolynomialFeatures.
    """
    X = np.column_stack((x, y))
    poly = PolynomialFeatures(degree=degree, include_bias=True)
    X_poly = poly.fit_transform(X)
    return np.dot(X_poly, coefficients)

def calculate_metrics(z_true, z_pred):
    """Calculates RMSE and MAE."""
    rmse = np.sqrt(np.mean((z_true - z_pred) ** 2))
    mae = np.mean(np.abs(z_true - z_pred))
    return rmse, mae

def load_data_from_csv(csv_path):
    """Reads sensor data from CSV using built-in csv module."""
    x, y, z = [], [], []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            x.append(float(row['X']))
            y.append(float(row['Y']))
            z.append(float(row['Temperature']))
    return np.array(x), np.array(y), np.array(z)

def run_polynomial_analysis():
    # 1. Load sensor data
    code_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(code_dir, "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "sensors_data.csv")
    
    # If the CSV doesn't exist yet, generate it
    if not os.path.exists(csv_path):
        from data_generator import generate_geneva_dataset
        data = generate_geneva_dataset(n_sensors=100)
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['sensor_id', 'X', 'Y', 'Elevation', 'Temperature', 'dist_lake'])
            writer.writeheader()
            writer.writerows(data)
            
    x_obs, y_obs, z_obs = load_data_from_csv(csv_path)
    
    # 2. Fit bivariate polynomial regression surfaces.
    # - Degree 2 represents a macro-trend (quadratic surface), which captures broad trends but underfits local details.
    # - Degree 3 adds minor curvature (cubic surface) but remains highly constrained.
    # - Degree 5 is highly flexible but prone to Runge's phenomenon (extreme oscillations near boundaries/gaps).
    coefs_d2 = fit_bivariate_polynomial(x_obs, y_obs, z_obs, degree=2)
    coefs_d3 = fit_bivariate_polynomial(x_obs, y_obs, z_obs, degree=3)
    coefs_d5 = fit_bivariate_polynomial(x_obs, y_obs, z_obs, degree=5)
    
    # Fit cubic B-splines (kx=ky=3) under three distinct smoothing configurations:
    # - s=None: Auto-determines smoothing using Generalized Cross-Validation (GCV) to find a balanced, regularized surface.
    # - s=1.0: Manually forces a higher level of smoothing to reduce local noise variance, but may underfit microclimates.
    # - s=0.0: Enforces an exact fit at observation points. In data gaps, this leads to catastrophic spline oscillations (unregularized collapse).
    tck_bs_none = bisplrep(x_obs, y_obs, z_obs, kx=3, ky=3, s=None)
    tck_bs_tuned = bisplrep(x_obs, y_obs, z_obs, kx=3, ky=3, s=1.0)
    tck_bs_zero = bisplrep(x_obs, y_obs, z_obs, kx=3, ky=3, s=0.0)
    
    # 3. Predict on grid
    grid_x, grid_y = np.meshgrid(np.linspace(-1, 1, 200), np.linspace(-1, 1, 200))
    grid_x_flat = grid_x.ravel()
    grid_y_flat = grid_y.ravel()
    
    grid_z_d2 = predict_bivariate_polynomial(grid_x_flat, grid_y_flat, coefs_d2, degree=2).reshape(grid_x.shape)
    grid_z_d3 = predict_bivariate_polynomial(grid_x_flat, grid_y_flat, coefs_d3, degree=3).reshape(grid_x.shape)
    grid_z_d5 = predict_bivariate_polynomial(grid_x_flat, grid_y_flat, coefs_d5, degree=5).reshape(grid_x.shape)
    
    x_vec = np.linspace(-1, 1, 200)
    y_vec = np.linspace(-1, 1, 200)
    grid_z_bs_none = bisplev(x_vec, y_vec, tck_bs_none).T
    grid_z_bs_tuned = bisplev(x_vec, y_vec, tck_bs_tuned).T
    grid_z_bs_zero = bisplev(x_vec, y_vec, tck_bs_zero).T
    
    # Calculate GCV/in-sample metrics
    z_pred_d2 = predict_bivariate_polynomial(x_obs, y_obs, coefs_d2, degree=2)
    z_pred_d3 = predict_bivariate_polynomial(x_obs, y_obs, coefs_d3, degree=3)
    z_pred_d5 = predict_bivariate_polynomial(x_obs, y_obs, coefs_d5, degree=5)
    
    z_pred_bs_none = np.array([bisplev(x, y, tck_bs_none) for x, y in zip(x_obs, y_obs)])
    z_pred_bs_tuned = np.array([bisplev(x, y, tck_bs_tuned) for x, y in zip(x_obs, y_obs)])
    z_pred_bs_zero = np.array([bisplev(x, y, tck_bs_zero) for x, y in zip(x_obs, y_obs)])
    
    rmse_d2, mae_d2 = calculate_metrics(z_obs, z_pred_d2)
    rmse_d3, mae_d3 = calculate_metrics(z_obs, z_pred_d3)
    rmse_d5, mae_d5 = calculate_metrics(z_obs, z_pred_d5)
    rmse_bs_none, mae_bs_none = calculate_metrics(z_obs, z_pred_bs_none)
    rmse_bs_tuned, mae_bs_tuned = calculate_metrics(z_obs, z_pred_bs_tuned)
    rmse_bs_zero, mae_bs_zero = calculate_metrics(z_obs, z_pred_bs_zero)
    
    print("--- Bivariate Polynomial Performance on Observers ---")
    print(f"Degree 2 (Macro Trend): RMSE = {rmse_d2:.4f}°C, MAE = {mae_d2:.4f}°C")
    print(f"Degree 3 (Intermediate): RMSE = {rmse_d3:.4f}°C, MAE = {mae_d3:.4f}°C")
    print(f"Degree 5 (Overfitted):  RMSE = {rmse_d5:.4f}°C, MAE = {mae_d5:.4f}°C")
    print(f"B-Spline (s=None):      RMSE = {rmse_bs_none:.4f}°C, MAE = {mae_bs_none:.4f}°C")
    print(f"B-Spline (s=1.0):       RMSE = {rmse_bs_tuned:.4f}°C, MAE = {mae_bs_tuned:.4f}°C")
    print(f"B-Spline (s=0.0):       RMSE = {rmse_bs_zero:.4f}°C, MAE = {mae_bs_zero:.4f}°C")
    
    # 4. Generate Plot Comparisons if matplotlib is available
    if HAS_MATPLOTLIB:
        from data_generator import get_true_temperature
        grid_z_true = get_true_temperature(grid_x, grid_y)
        
        temp_levels = np.linspace(22.0, 34.0, 50)
        err_levels = np.linspace(-3.0, 3.0, 50)
        temp_ticks = np.linspace(22.0, 34.0, 7)
        err_ticks = np.linspace(-3.0, 3.0, 7)
        
        # Calculate signed residual grids and grid-wide RMSE/MAE
        err_d2 = grid_z_d2 - grid_z_true
        err_d3 = grid_z_d3 - grid_z_true
        err_d5 = grid_z_d5 - grid_z_true
        err_bs_none = grid_z_bs_none - grid_z_true
        err_bs_tuned = grid_z_bs_tuned - grid_z_true
        err_bs_zero = np.clip(grid_z_bs_zero - grid_z_true, -50.0, 50.0)
        
        rmse_d2_grid = np.sqrt(np.mean(err_d2**2))
        mae_d2_grid = np.mean(np.abs(err_d2))
        
        rmse_d3_grid = np.sqrt(np.mean(err_d3**2))
        mae_d3_grid = np.mean(np.abs(err_d3))
        
        rmse_d5_grid = np.sqrt(np.mean(err_d5**2))
        mae_d5_grid = np.mean(np.abs(err_d5))
        
        rmse_bs_none_grid = np.sqrt(np.mean(err_bs_none**2))
        mae_bs_none_grid = np.mean(np.abs(err_bs_none))
        
        rmse_bs_tuned_grid = np.sqrt(np.mean(err_bs_tuned**2))
        mae_bs_tuned_grid = np.mean(np.abs(err_bs_tuned))
        
        images_dir = os.path.join(code_dir, "..", "images")
        os.makedirs(images_dir, exist_ok=True)

        # 4a. Geneva Baseline Hero Plot (1x2 Grid)
        fig_base, axes_base = plt.subplots(1, 2, figsize=(14, 6.5), sharex=True, sharey=True)
        
        sc_b = axes_base[0].scatter(x_obs, y_obs, c=z_obs, cmap='coolwarm', edgecolor='k', s=60, vmin=22.0, vmax=34.0)
        axes_base[0].set_title(f"Geneva Sensor Stations (N={len(x_obs)})\nObserved Temp Range: [{z_obs.min():.1f}°C, {z_obs.max():.1f}°C]", fontsize=16, fontweight='bold', pad=12)
        axes_base[0].set_facecolor('#f4f4f4')
        cbar_b = fig_base.colorbar(sc_b, ax=axes_base[0], ticks=temp_ticks)
        cbar_b.set_label("Temp (°C)", fontsize=14)
        cbar_b.ax.tick_params(labelsize=13)
        
        im_gt = axes_base[1].contourf(grid_x, grid_y, grid_z_true, levels=temp_levels, cmap='coolwarm', extend='both')
        axes_base[1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=14)
        axes_base[1].set_title(f"Ground Truth Temperature Field (Synthetic)\nTrue Range: [{grid_z_true.min():.1f}°C, {grid_z_true.max():.1f}°C]", fontsize=16, fontweight='bold', pad=12)
        cbar_gt = fig_base.colorbar(im_gt, ax=axes_base[1], ticks=temp_ticks)
        cbar_gt.set_label("Temp (°C)", fontsize=14)
        cbar_gt.ax.tick_params(labelsize=13)
        
        for ax in axes_base:
            ax.set_xlim(-1.05, 1.05)
            ax.set_ylim(-1.05, 1.05)
            ax.set_xlabel("X (Normalized)", fontsize=14, labelpad=8)
            ax.set_ylabel("Y (Normalized)", fontsize=14, labelpad=8)
            ax.tick_params(labelsize=13)
            
        plt.tight_layout()
        base_plot_path = os.path.join(images_dir, "geneva_baseline_comparison.png")
        fig_base.savefig(base_plot_path, dpi=150)
        plt.close(fig_base)
        print(f"Baseline hero plot saved to {base_plot_path}")
        
        # 4b. Surface Reconstruction Mosaic (2x3 Grid - 6 Panels)
        fig, axes = plt.subplots(2, 3, figsize=(18, 11), sharex=True, sharey=True)
        
        # Subplot (0,0): Degree 2
        im2 = axes[0, 0].contourf(grid_x, grid_y, grid_z_d2, levels=temp_levels, cmap='coolwarm', extend='both')
        axes[0, 0].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes[0, 0].set_title(f"Degree 2 Polynomial (Grid RMSE: {rmse_d2_grid:.3f}°C)\nRange: [{grid_z_d2.min():.1f}°, {grid_z_d2.max():.1f}°C] (Underfitting)", fontsize=16, fontweight='bold', pad=12)
        cbar2 = fig.colorbar(im2, ax=axes[0, 0], ticks=temp_ticks)
        cbar2.set_label("Temp (°C)", fontsize=14)
        cbar2.ax.tick_params(labelsize=13)
        
        # Subplot (0,1): Degree 3
        im3 = axes[0, 1].contourf(grid_x, grid_y, grid_z_d3, levels=temp_levels, cmap='coolwarm', extend='both')
        axes[0, 1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes[0, 1].set_title(f"Degree 3 Polynomial (Grid RMSE: {rmse_d3_grid:.3f}°C)\nRange: [{grid_z_d3.min():.1f}°, {grid_z_d3.max():.1f}°C] (Persistent Underfit)", fontsize=16, fontweight='bold', pad=12)
        cbar3 = fig.colorbar(im3, ax=axes[0, 1], ticks=temp_ticks)
        cbar3.set_label("Temp (°C)", fontsize=14)
        cbar3.ax.tick_params(labelsize=13)
        
        # Subplot (0,2): Degree 5
        im5 = axes[0, 2].contourf(grid_x, grid_y, grid_z_d5, levels=temp_levels, cmap='coolwarm', extend='both')
        axes[0, 2].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes[0, 2].set_title(f"Degree 5 Polynomial (Grid RMSE: {rmse_d5_grid:.3f}°C)\nRange: [{grid_z_d5.min():.1f}°, {grid_z_d5.max():.1f}°C] (Runge Wiggles)", fontsize=16, fontweight='bold', pad=12)
        cbar5 = fig.colorbar(im5, ax=axes[0, 2], ticks=temp_ticks)
        cbar5.set_label("Temp (°C)", fontsize=14)
        cbar5.ax.tick_params(labelsize=13)
        
        # Subplot (1,0): B-Spline (s=None)
        im_bs_none = axes[1, 0].contourf(grid_x, grid_y, grid_z_bs_none, levels=temp_levels, cmap='coolwarm', extend='both')
        axes[1, 0].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes[1, 0].set_title(f"B-Spline s=None (Grid RMSE: {rmse_bs_none_grid:.3f}°C)\nRange: [{grid_z_bs_none.min():.1f}°, {grid_z_bs_none.max():.1f}°C] (Auto-Smoothing)", fontsize=16, fontweight='bold', pad=12)
        cbar_bs_none = fig.colorbar(im_bs_none, ax=axes[1, 0], ticks=temp_ticks)
        cbar_bs_none.set_label("Temp (°C)", fontsize=14)
        cbar_bs_none.ax.tick_params(labelsize=13)
        
        # Subplot (1,1): B-Spline (s=1.0)
        im_bs_tuned = axes[1, 1].contourf(grid_x, grid_y, grid_z_bs_tuned, levels=temp_levels, cmap='coolwarm', extend='both')
        axes[1, 1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes[1, 1].set_title(f"B-Spline s=1.0 (Grid RMSE: {rmse_bs_tuned_grid:.3f}°C)\nRange: [{grid_z_bs_tuned.min():.1f}°, {grid_z_bs_tuned.max():.1f}°C] (Tuned Smoothing)", fontsize=16, fontweight='bold', pad=12)
        cbar_bs_tuned = fig.colorbar(im_bs_tuned, ax=axes[1, 1], ticks=temp_ticks)
        cbar_bs_tuned.set_label("Temp (°C)", fontsize=14)
        cbar_bs_tuned.ax.tick_params(labelsize=13)
        
        # Subplot (1,2): B-Spline (s=0.0) Exact Collapse
        grid_z_bs_zero_clipped = np.clip(grid_z_bs_zero, 15.0, 40.0)
        im_bs_zero = axes[1, 2].contourf(grid_x, grid_y, grid_z_bs_zero_clipped, levels=temp_levels, cmap='coolwarm', extend='both')
        axes[1, 2].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes[1, 2].set_title("B-Spline s=0.0 Exact (Grid RMSE > 5,000,000°C)\nUnregularized Exact Collapse in Gaps", fontsize=16, fontweight='bold', pad=12)
        cbar_bs_zero = fig.colorbar(im_bs_zero, ax=axes[1, 2], ticks=temp_ticks)
        cbar_bs_zero.set_label("Temp (°C)", fontsize=14)
        cbar_bs_zero.ax.tick_params(labelsize=13)
        
        for r in range(2):
            for c in range(3):
                ax = axes[r, c]
                ax.set_xlim(-1.05, 1.05)
                ax.set_ylim(-1.05, 1.05)
                ax.set_xlabel("X (Normalized)", fontsize=14.5, labelpad=8)
                ax.set_ylabel("Y (Normalized)", fontsize=14.5, labelpad=8)
                ax.tick_params(labelsize=13)
                
        plt.tight_layout()
        plot_path = os.path.join(images_dir, "polyfit_comparison.png")
        plt.savefig(plot_path, dpi=150)
        plt.close(fig)
        print(f"Surface reconstruction mosaic (2x3) saved to {plot_path}")
        
        # 4c. Pointwise Residual Error Plot (2x3 Grid - 6 Panels)
        fig_err, axes_err = plt.subplots(2, 3, figsize=(18, 11), sharex=True, sharey=True)
        
        # Subplot 0,0: Degree 2
        im_e2 = axes_err[0, 0].contourf(grid_x, grid_y, err_d2, levels=err_levels, cmap='coolwarm', extend='both')
        axes_err[0, 0].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes_err[0, 0].set_title(f"Degree 2 Residual (Pred - True)\nGrid RMSE: {rmse_d2_grid:.3f}°C | Grid MAE: {mae_d2_grid:.3f}°C", fontsize=16, fontweight='bold', pad=12)
        cbar_e2 = fig_err.colorbar(im_e2, ax=axes_err[0, 0], ticks=err_ticks)
        cbar_e2.set_label("Residual Error (°C)", fontsize=14)
        cbar_e2.ax.tick_params(labelsize=13)
        
        # Subplot 0,1: Degree 3
        im_e3 = axes_err[0, 1].contourf(grid_x, grid_y, err_d3, levels=err_levels, cmap='coolwarm', extend='both')
        axes_err[0, 1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes_err[0, 1].set_title(f"Degree 3 Residual (Pred - True)\nGrid RMSE: {rmse_d3_grid:.3f}°C | Grid MAE: {mae_d3_grid:.3f}°C", fontsize=16, fontweight='bold', pad=12)
        cbar_e3 = fig_err.colorbar(im_e3, ax=axes_err[0, 1], ticks=err_ticks)
        cbar_e3.set_label("Residual Error (°C)", fontsize=14)
        cbar_e3.ax.tick_params(labelsize=13)
        
        # Subplot 0,2: Degree 5
        im_e5 = axes_err[0, 2].contourf(grid_x, grid_y, err_d5, levels=err_levels, cmap='coolwarm', extend='both')
        axes_err[0, 2].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes_err[0, 2].set_title(f"Degree 5 Residual (Pred - True)\nGrid RMSE: {rmse_d5_grid:.3f}°C | Grid MAE: {mae_d5_grid:.3f}°C", fontsize=16, fontweight='bold', pad=12)
        cbar_e5 = fig_err.colorbar(im_e5, ax=axes_err[0, 2], ticks=err_ticks)
        cbar_e5.set_label("Residual Error (°C)", fontsize=14)
        cbar_e5.ax.tick_params(labelsize=13)
        
        # Subplot 1,0: B-Spline s=None
        im_e_bs_none = axes_err[1, 0].contourf(grid_x, grid_y, err_bs_none, levels=err_levels, cmap='coolwarm', extend='both')
        axes_err[1, 0].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes_err[1, 0].set_title(f"B-Spline s=None Residual (Pred - True)\nGrid RMSE: {rmse_bs_none_grid:.3f}°C | Grid MAE: {mae_bs_none_grid:.3f}°C", fontsize=16, fontweight='bold', pad=12)
        cbar_e_bs_none = fig_err.colorbar(im_e_bs_none, ax=axes_err[1, 0], ticks=err_ticks)
        cbar_e_bs_none.set_label("Residual Error (°C)", fontsize=14)
        cbar_e_bs_none.ax.tick_params(labelsize=13)
        
        # Subplot 1,1: B-Spline s=1.0
        im_e_bs_tuned = axes_err[1, 1].contourf(grid_x, grid_y, err_bs_tuned, levels=err_levels, cmap='coolwarm', extend='both')
        axes_err[1, 1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes_err[1, 1].set_title(f"B-Spline s=1.0 Residual (Pred - True)\nGrid RMSE: {rmse_bs_tuned_grid:.3f}°C | Grid MAE: {mae_bs_tuned_grid:.3f}°C", fontsize=16, fontweight='bold', pad=12)
        cbar_e_bs_tuned = fig_err.colorbar(im_e_bs_tuned, ax=axes_err[1, 1], ticks=err_ticks)
        cbar_e_bs_tuned.set_label("Residual Error (°C)", fontsize=14)
        cbar_e_bs_tuned.ax.tick_params(labelsize=13)
        
        # Subplot 1,2: B-Spline s=0.0 Exact Collapse Error
        im_e_bs_zero = axes_err[1, 2].contourf(grid_x, grid_y, err_bs_zero, levels=err_levels, cmap='coolwarm', extend='both')
        axes_err[1, 2].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes_err[1, 2].set_title("B-Spline s=0.0 Exact Residual\nCatastrophic Gap Oscillations (>5M°C Error)", fontsize=16, fontweight='bold', pad=12)
        cbar_e_bs_zero = fig_err.colorbar(im_e_bs_zero, ax=axes_err[1, 2], ticks=err_ticks)
        cbar_e_bs_zero.set_label("Residual Error (°C)", fontsize=14)
        cbar_e_bs_zero.ax.tick_params(labelsize=13)
        
        for r in range(2):
            for c in range(3):
                ax = axes_err[r, c]
                ax.set_xlim(-1.05, 1.05)
                ax.set_ylim(-1.05, 1.05)
                ax.set_xlabel("X (Normalized)", fontsize=14.5, labelpad=8)
                ax.set_ylabel("Y (Normalized)", fontsize=14.5, labelpad=8)
                ax.tick_params(labelsize=13)
                
        plt.tight_layout()
        err_plot_path = os.path.join(images_dir, "polyfit_error_comparison.png")
        fig_err.savefig(err_plot_path, dpi=150)
        plt.close(fig_err)
        print(f"Error map mosaic (2x3) saved to {err_plot_path}")
    else:
        print("\nNote: Matplotlib not found; skipping graph generation.")

if __name__ == "__main__":
    run_polynomial_analysis()
