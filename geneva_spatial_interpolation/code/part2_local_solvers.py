"""
Geneva Spatial Interpolation Series - Part 2: Custom Local Solvers in NumPy
==========================================================================
This script implements custom spatial solvers from scratch using pure Python/NumPy:
1. NearestNeighbor2D: wraps scipy's NearestNDInterpolator for discontinuous baseline comparisons.
2. InverseDistanceWeighting: implements IDW with custom distance calculations and handles 
   the exact-match singularity condition when target points coincide with sensor locations.
3. RadialBasisFunctions2D: sets up and solves a custom 2D Radial Basis Function interpolation
   matrix equation using a Thin-Plate Spline (TPS) kernel (phi(r) = r^2 * ln(r)).
"""

import numpy as np
import os
import csv
from scipy.interpolate import NearestNDInterpolator, griddata
from scipy.spatial.distance import cdist

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# ---------------------------------------------------------
# 1. Custom Local Solvers in Pure Python/NumPy
# ---------------------------------------------------------

class NearestNeighbor2D:
    """Implement 2D Nearest Neighbor interpolation wrapping SciPy's NearestNDInterpolator."""
    def __init__(self, x, y, z):
        self.interpolator = NearestNDInterpolator(np.column_stack((x, y)), z)
        
    def __call__(self, x_target, y_target):
        return self.interpolator(np.column_stack((x_target, y_target)))


class InverseDistanceWeighting:
    """
    Implement 2D Inverse Distance Weighting (IDW) interpolation using SciPy's cdist.
    Calculates weights using distance decay: w_i = 1 / d_i^p.
    """
    def __init__(self, x, y, z, power=2.0):
        self.coords = np.column_stack((x, y))
        self.z = np.array(z)
        self.power = power
        
    def __call__(self, x_target, y_target):
        targets = np.column_stack((x_target, y_target))
        # Compute pairwise Euclidean distances between target points and observed sensors
        dists = cdist(targets, self.coords)
        
        # Singularity check: if target coordinate is exactly at a sensor location (dist < epsilon),
        # the weight (1/dist^p) goes to infinity. We must catch these exact-match points.
        epsilon = 1e-7
        is_close = dists < epsilon
        
        with np.errstate(divide='ignore'):
            weights = 1.0 / (dists ** self.power)
            
        weights_sum = np.sum(weights, axis=1)
        z_t = np.zeros(len(targets))
        
        # Case A: Handle exact sensor overlap points by returning the exact observed temperature
        close_targets_mask = np.any(is_close, axis=1)
        for i in np.where(close_targets_mask)[0]:
            sensor_idx = np.argmin(dists[i])
            z_t[i] = self.z[sensor_idx]
            
        # Case B: Standard IDW weighted average calculation for non-coincident points
        non_close_indices = np.where(~close_targets_mask)[0]
        if len(non_close_indices) > 0:
            z_t[non_close_indices] = np.sum(weights[non_close_indices] * self.z, axis=1) / weights_sum[non_close_indices]
            
        return z_t


class RadialBasisFunctions2D:
    """
    Custom 2D Radial Basis Function (RBF) interpolation with Thin-Plate Spline kernel.
    Thin-Plate Spline Kernel equation: phi(r) = r^2 * ln(r).
    Fits a surface by solving the linear system: K * w = z, where K is the kernel matrix.
    """
    def __init__(self, x, y, z, smoothing=0.0):
        self.coords = np.column_stack((x, y))
        self.z = np.array(z)
        self.smoothing = smoothing
        n = len(z)
        
        # Compute pairwise distance matrix between all observed sensors
        dists = cdist(self.coords, self.coords)
        # Compute the Thin-Plate Spline kernel matrix K
        K = dists**2 * np.log(dists + 1e-10) # 1e-10 prevents ln(0) division/undefined errors
        
        # Incorporate diagonal smoothing regularization: K += smoothing * I
        K += np.eye(n) * smoothing
        
        # Solve the linear system for the RBF weight coefficients: w = K^-1 * z
        self.weights = np.linalg.solve(K, self.z)
        
    def __call__(self, x_target, y_target):
        x_t = np.atleast_1d(x_target)
        y_t = np.atleast_1d(y_target)
        targets = np.column_stack((x_t, y_t))
        
        # Compute distances between target coordinates and observed sensors
        dists = cdist(targets, self.coords)
        # Evaluate kernel on the target distance matrix
        K_pred = dists**2 * np.log(dists + 1e-10)
        
        # Compute predictions as the dot product: z_pred = K_pred * w
        return np.dot(K_pred, self.weights)


# ---------------------------------------------------------
# 2. Main Driver & Analysis for Part 2 Local Solvers
# ---------------------------------------------------------

def load_data_from_csv(csv_path):
    x, y, elev, z = [], [], [], []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            x.append(float(row['X']))
            y.append(float(row['Y']))
            elev.append(float(row['Elevation']))
            z.append(float(row['Temperature']))
    return np.array(x), np.array(y), np.array(elev), np.array(z)

def calculate_metrics(z_true, z_pred):
    rmse = np.sqrt(np.mean((z_true - z_pred) ** 2))
    mae = np.mean(np.abs(z_true - z_pred))
    return rmse, mae

def run_local_solvers_analysis():
    code_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(code_dir, "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "sensors_data.csv")
    
    x_obs, y_obs, elev_obs, z_obs = load_data_from_csv(csv_path)
    
    model_nn = NearestNeighbor2D(x_obs, y_obs, z_obs)
    model_idw = InverseDistanceWeighting(x_obs, y_obs, z_obs, power=2.0)
    model_rbf = RadialBasisFunctions2D(x_obs, y_obs, z_obs, smoothing=0.0)

    z_pred_nn = model_nn(x_obs, y_obs)
    z_pred_idw = model_idw(x_obs, y_obs)
    z_pred_rbf = model_rbf(x_obs, y_obs)
    
    rmse_nn, mae_nn = calculate_metrics(z_obs, z_pred_nn)
    rmse_idw, mae_idw = calculate_metrics(z_obs, z_pred_idw)
    rmse_rbf, mae_rbf = calculate_metrics(z_obs, z_pred_rbf)
    
    print("Computing Leave-One-Out Cross-Validation (LOOCV) out-of-sample errors...")
    n_points = len(x_obs)
    loocv_nn = np.zeros(n_points)
    loocv_tin = np.zeros(n_points)
    loocv_sibson = np.zeros(n_points)
    loocv_idw = np.zeros(n_points)
    loocv_rbf = np.zeros(n_points)
    
    for i in range(n_points):
        tx = np.delete(x_obs, i)
        ty = np.delete(y_obs, i)
        tz = np.delete(z_obs, i)
        
        nn_cv = NearestNeighbor2D(tx, ty, tz)
        idw_cv = InverseDistanceWeighting(tx, ty, tz, power=2.0)
        rbf_cv = RadialBasisFunctions2D(tx, ty, tz, smoothing=0.0)
        
        loocv_nn[i] = nn_cv(x_obs[i], y_obs[i])[0]
        
        tin_val = griddata((tx, ty), tz, (x_obs[i], y_obs[i]), method='linear')
        loocv_tin[i] = loocv_nn[i] if np.isnan(tin_val) else float(tin_val)
        
        sib_val = griddata((tx, ty), tz, (x_obs[i], y_obs[i]), method='cubic')
        loocv_sibson[i] = loocv_nn[i] if np.isnan(sib_val) else float(sib_val)
        
        loocv_idw[i] = idw_cv(x_obs[i], y_obs[i])[0]
        loocv_rbf[i] = rbf_cv(x_obs[i], y_obs[i])[0]
        
    rmse_nn_cv, mae_nn_cv = calculate_metrics(z_obs, loocv_nn)
    rmse_tin_cv, mae_tin_cv = calculate_metrics(z_obs, loocv_tin)
    rmse_sibson_cv, mae_sibson_cv = calculate_metrics(z_obs, loocv_sibson)
    rmse_idw_cv, mae_idw_cv = calculate_metrics(z_obs, loocv_idw)
    rmse_rbf_cv, mae_rbf_cv = calculate_metrics(z_obs, loocv_rbf)
    
    grid_x, grid_y = np.meshgrid(np.linspace(-1, 1, 100), np.linspace(-1, 1, 100))
    grid_x_f = grid_x.ravel()
    grid_y_f = grid_y.ravel()
    
    grid_z_nn = model_nn(grid_x_f, grid_y_f).reshape(grid_x.shape)
    grid_z_tin = griddata((x_obs, y_obs), z_obs, (grid_x, grid_y), method='linear')
    grid_z_tin[np.isnan(grid_z_tin)] = grid_z_nn[np.isnan(grid_z_tin)]
    
    grid_z_sibson = griddata((x_obs, y_obs), z_obs, (grid_x, grid_y), method='cubic')
    grid_z_sibson[np.isnan(grid_z_sibson)] = grid_z_nn[np.isnan(grid_z_sibson)]
    
    grid_z_idw = model_idw(grid_x_f, grid_y_f).reshape(grid_x.shape)
    grid_z_rbf = model_rbf(grid_x_f, grid_y_f).reshape(grid_x.shape)
    
    from data_generator import get_true_temperature
    grid_z_true_full = get_true_temperature(grid_x_f, grid_y_f)
    z_true_flat = grid_z_true_full.ravel()
    
    rmse_nn_grid, mae_nn_grid = calculate_metrics(z_true_flat, grid_z_nn.ravel())
    rmse_tin_grid, mae_tin_grid = calculate_metrics(z_true_flat, grid_z_tin.ravel())
    rmse_sibson_grid, mae_sibson_grid = calculate_metrics(z_true_flat, grid_z_sibson.ravel())
    rmse_idw_grid, mae_idw_grid = calculate_metrics(z_true_flat, grid_z_idw.ravel())
    rmse_rbf_grid, mae_rbf_grid = calculate_metrics(z_true_flat, grid_z_rbf.ravel())
    
    print("\n" + "="*110)
    print("      Geneva Deterministic Local Solvers Benchmarks (In-Sample vs. LOOCV vs. Grid GT)")
    print("="*110)
    print(f"Nearest Neighbor:       In-Sample RMSE = {rmse_nn:.4f}°C, LOOCV RMSE = {rmse_nn_cv:.4f}°C, Grid GT RMSE = {rmse_nn_grid:.4f}°C")
    print(f"Delaunay TIN:          In-Sample RMSE = 0.0000°C, LOOCV RMSE = {rmse_tin_cv:.4f}°C, Grid GT RMSE = {rmse_tin_grid:.4f}°C")
    print(f"Natural Neighbor (Sib): In-Sample RMSE = 0.0000°C, LOOCV RMSE = {rmse_sibson_cv:.4f}°C, Grid GT RMSE = {rmse_sibson_grid:.4f}°C")
    print(f"IDW (Power=2):          In-Sample RMSE = {rmse_idw:.4f}°C, LOOCV RMSE = {rmse_idw_cv:.4f}°C, Grid GT RMSE = {rmse_idw_grid:.4f}°C")
    print(f"RBF (Thin-Plate):       In-Sample RMSE = {rmse_rbf:.4f}°C, LOOCV RMSE = {rmse_rbf_cv:.4f}°C, Grid GT RMSE = {rmse_rbf_grid:.4f}°C")
    print("="*110)
    
    if HAS_MATPLOTLIB:
        temp_levels = np.linspace(22.0, 34.0, 50)
        err_levels = np.linspace(-3.0, 3.0, 50)
        temp_ticks = np.linspace(22.0, 34.0, 7)
        err_ticks = np.linspace(-3.0, 3.0, 7)
        
        # 1a. Discontinuous Geometric Baselines Plot (1x2 Grid)
        fig1_a, axes1_a = plt.subplots(1, 2, figsize=(14, 6), sharex=True, sharey=True)
        
        im0 = axes1_a[0].contourf(grid_x, grid_y, grid_z_nn, levels=temp_levels, cmap='coolwarm', extend='both')
        axes1_a[0].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes1_a[0].set_title(f"Nearest Neighbor (Grid RMSE: {rmse_nn_grid:.3f}°C | MAE: {mae_nn_grid:.3f}°C)\nPredicted Range: [{grid_z_nn.min():.2f}°C, {grid_z_nn.max():.2f}°C]", fontsize=16, fontweight='bold', pad=12)
        cbar0 = fig1_a.colorbar(im0, ax=axes1_a[0], ticks=temp_ticks)
        cbar0.set_label("Temp (°C)", fontsize=14)
        cbar0.ax.tick_params(labelsize=13)
        
        im_tin = axes1_a[1].contourf(grid_x, grid_y, grid_z_tin, levels=temp_levels, cmap='coolwarm', extend='both')
        axes1_a[1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes1_a[1].set_title(f"Delaunay TIN (Grid RMSE: {rmse_tin_grid:.3f}°C | MAE: {mae_tin_grid:.3f}°C)\nPredicted Range: [{grid_z_tin.min():.2f}°C, {grid_z_tin.max():.2f}°C]", fontsize=16, fontweight='bold', pad=12)
        cbar_tin = fig1_a.colorbar(im_tin, ax=axes1_a[1], ticks=temp_ticks)
        cbar_tin.set_label("Temp (°C)", fontsize=14)
        cbar_tin.ax.tick_params(labelsize=13)
        
        for ax in axes1_a:
            ax.set_xlim(-1.05, 1.05)
            ax.set_ylim(-1.05, 1.05)
            ax.set_xlabel("X (Normalized)", fontsize=14, labelpad=8)
            ax.set_ylabel("Y (Normalized)", fontsize=14, labelpad=8)
            ax.tick_params(labelsize=13)
            
        images_dir = os.path.join(code_dir, "..", "images")
        os.makedirs(images_dir, exist_ok=True)
        fig1_a.tight_layout()
        plot1a_path = os.path.join(images_dir, "geospatial_discontinuous_comparison.png")
        fig1_a.savefig(plot1a_path, dpi=150)
        plt.close(fig1_a)
        print(f"Saved discontinuous geometric baselines plot to {plot1a_path}")

        # 1b. Smooth & Advanced Local Interpolators Plot (2x2 Grid)
        fig1_b, axes1_b = plt.subplots(2, 2, figsize=(14, 12), sharex=True, sharey=True)
        
        # Subplot (0,0): Ground Truth Continuous Synthetic Field
        im_gt_b = axes1_b[0, 0].contourf(grid_x, grid_y, grid_z_true_full.reshape(grid_x.shape), levels=temp_levels, cmap='coolwarm', extend='both')
        axes1_b[0, 0].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes1_b[0, 0].set_title(f"Ground Truth Field (Continuous Synthetic)\nTrue Range: [{grid_z_true_full.min():.2f}°C, {grid_z_true_full.max():.2f}°C]", fontsize=14.5, fontweight='bold', pad=10)
        cbar_gt_b = fig1_b.colorbar(im_gt_b, ax=axes1_b[0, 0], ticks=temp_ticks)
        cbar_gt_b.set_label("Temp (°C)", fontsize=14)
        cbar_gt_b.ax.tick_params(labelsize=13)
        
        im_sib = axes1_b[0, 1].contourf(grid_x, grid_y, grid_z_sibson, levels=temp_levels, cmap='coolwarm', extend='both')
        axes1_b[0, 1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes1_b[0, 1].set_title(f"Natural Neighbor (Grid RMSE: {rmse_sibson_grid:.3f}°C | MAE: {mae_sibson_grid:.3f}°C)\nPredicted Range: [{grid_z_sibson.min():.2f}°C, {grid_z_sibson.max():.2f}°C]", fontsize=14.5, fontweight='bold', pad=10)
        cbar_sib = fig1_b.colorbar(im_sib, ax=axes1_b[0, 1], ticks=temp_ticks)
        cbar_sib.set_label("Temp (°C)", fontsize=14)
        cbar_sib.ax.tick_params(labelsize=13)
        
        im1 = axes1_b[1, 0].contourf(grid_x, grid_y, grid_z_idw, levels=temp_levels, cmap='coolwarm', extend='both')
        axes1_b[1, 0].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes1_b[1, 0].set_title(f"IDW (Power=2) (Grid RMSE: {rmse_idw_grid:.3f}°C | MAE: {mae_idw_grid:.3f}°C)\nPredicted Range: [{grid_z_idw.min():.2f}°C, {grid_z_idw.max():.2f}°C]", fontsize=14.5, fontweight='bold', pad=10)
        cbar1 = fig1_b.colorbar(im1, ax=axes1_b[1, 0], ticks=temp_ticks)
        cbar1.set_label("Temp (°C)", fontsize=14)
        cbar1.ax.tick_params(labelsize=13)
        
        im2 = axes1_b[1, 1].contourf(grid_x, grid_y, grid_z_rbf, levels=temp_levels, cmap='coolwarm', extend='both')
        axes1_b[1, 1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes1_b[1, 1].set_title(f"RBF Thin-Plate (Grid RMSE: {rmse_rbf_grid:.3f}°C | MAE: {mae_rbf_grid:.3f}°C)\nPredicted Range: [{grid_z_rbf.min():.2f}°C, {grid_z_rbf.max():.2f}°C]", fontsize=14.5, fontweight='bold', pad=10)
        cbar2 = fig1_b.colorbar(im2, ax=axes1_b[1, 1], ticks=temp_ticks)
        cbar2.set_label("Temp (°C)", fontsize=14)
        cbar2.ax.tick_params(labelsize=13)
        
        for r_idx in range(2):
            for c_idx in range(2):
                ax = axes1_b[r_idx, c_idx]
                ax.set_xlim(-1.05, 1.05)
                ax.set_ylim(-1.05, 1.05)
                ax.set_xlabel("X (Normalized)", fontsize=14, labelpad=8)
                ax.set_ylabel("Y (Normalized)", fontsize=14, labelpad=8)
                ax.tick_params(labelsize=13)
                
        fig1_b.tight_layout()
        plot1b_path = os.path.join(images_dir, "geospatial_smooth_comparison.png")
        fig1_b.savefig(plot1b_path, dpi=150)
        plt.close(fig1_b)
        print(f"Saved smooth interpolators plot to {plot1b_path}")
        
        # 2. Pointwise Residual Error Plot for Key Solvers (2x2 Grid)
        fig3, axes3 = plt.subplots(2, 2, figsize=(14, 12), sharex=True, sharey=True)
        
        err_tin = grid_z_tin - grid_z_true_full.reshape(grid_x.shape)
        mae_tin_grid = np.mean(np.abs(err_tin))
        im_e_tin = axes3[0, 0].contourf(grid_x, grid_y, err_tin, levels=err_levels, cmap='coolwarm', extend='both')
        axes3[0, 0].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes3[0, 0].set_title(f"Delaunay TIN Residual (Pred - True)\nGrid RMSE: {rmse_tin_grid:.3f}°C | Grid MAE: {mae_tin_grid:.3f}°C", fontsize=14.5, fontweight='bold', pad=10)
        cbar_e_tin = fig3.colorbar(im_e_tin, ax=axes3[0, 0], ticks=err_ticks)
        cbar_e_tin.set_label("Residual Error (°C)", fontsize=14)
        cbar_e_tin.ax.tick_params(labelsize=13)
        
        err_sib = grid_z_sibson - grid_z_true_full.reshape(grid_x.shape)
        mae_sibson_grid = np.mean(np.abs(err_sib))
        im_e_sib = axes3[0, 1].contourf(grid_x, grid_y, err_sib, levels=err_levels, cmap='coolwarm', extend='both')
        axes3[0, 1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes3[0, 1].set_title(f"Natural Neighbor Residual (Pred - True)\nGrid RMSE: {rmse_sibson_grid:.3f}°C | Grid MAE: {mae_sibson_grid:.3f}°C", fontsize=14.5, fontweight='bold', pad=10)
        cbar_e_sib = fig3.colorbar(im_e_sib, ax=axes3[0, 1], ticks=err_ticks)
        cbar_e_sib.set_label("Residual Error (°C)", fontsize=14)
        cbar_e_sib.ax.tick_params(labelsize=13)
        
        err_idw = grid_z_idw - grid_z_true_full.reshape(grid_x.shape)
        mae_idw_grid = np.mean(np.abs(err_idw))
        im_e1 = axes3[1, 0].contourf(grid_x, grid_y, err_idw, levels=err_levels, cmap='coolwarm', extend='both')
        axes3[1, 0].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes3[1, 0].set_title(f"IDW (Power=2) Residual (Pred - True)\nGrid RMSE: {rmse_idw_grid:.3f}°C | Grid MAE: {mae_idw_grid:.3f}°C", fontsize=14.5, fontweight='bold', pad=10)
        cbar_e1 = fig3.colorbar(im_e1, ax=axes3[1, 0], ticks=err_ticks)
        cbar_e1.set_label("Residual Error (°C)", fontsize=14)
        cbar_e1.ax.tick_params(labelsize=13)
        
        err_rbf = grid_z_rbf - grid_z_true_full.reshape(grid_x.shape)
        mae_rbf_grid = np.mean(np.abs(err_rbf))
        im_e2 = axes3[1, 1].contourf(grid_x, grid_y, err_rbf, levels=err_levels, cmap='coolwarm', extend='both')
        axes3[1, 1].scatter(x_obs, y_obs, color='black', alpha=0.3, s=12)
        axes3[1, 1].set_title(f"RBF Thin-Plate Residual (Pred - True)\nGrid RMSE: {rmse_rbf_grid:.3f}°C | Grid MAE: {mae_rbf_grid:.3f}°C", fontsize=14.5, fontweight='bold', pad=10)
        cbar_e2 = fig3.colorbar(im_e2, ax=axes3[1, 1], ticks=err_ticks)
        cbar_e2.set_label("Residual Error (°C)", fontsize=14)
        cbar_e2.ax.tick_params(labelsize=13)
        
        for r_idx in range(2):
            for c_idx in range(2):
                ax = axes3[r_idx, c_idx]
                ax.set_xlim(-1.05, 1.05)
                ax.set_ylim(-1.05, 1.05)
                ax.set_xlabel("X (Normalized)", fontsize=14, labelpad=8)
                ax.set_ylabel("Y (Normalized)", fontsize=14, labelpad=8)
                ax.tick_params(labelsize=13)
                
        plt.tight_layout()
        plot3_path = os.path.join(images_dir, "geospatial_error_comparison.png")
        fig3.savefig(plot3_path, dpi=150)
        plt.close(fig3)
        print(f"Saved deterministic error comparison plot to {plot3_path}")
        
if __name__ == "__main__":
    run_local_solvers_analysis()
