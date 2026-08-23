"""
Geneva Spatial Interpolation Series - Part 4: Spatial Machine Learning
======================================================================
Implements machine learning spatial regression models:
1. Coordinate-Only Regression: predicting temperature using ONLY (X, Y) coordinates.
2. Multi-Source Feature Fusion Regression: predicting temperature using (X, Y) coordinates PLUS 
   physically informed geographical features (Elevation and Distance to Lake).
   
Evaluates standard ML architectures:
- RandomForestRegressor (ensemble trees)
- XGBRegressor (gradient boosted trees)
- SVR (Support Vector Regression - RBF kernel)
- MLPRegressor (Multi-Layer Perceptron neural network)
"""

import numpy as np
import os
import csv
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from joblib import Parallel, delayed
import xgboost as xgb

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Import geographic formulas from data_generator
from data_generator import get_lake_distance, get_true_temperature

def get_grid_elevation(x, y):
    elev_jura = 800.0 * np.exp(-((x + 1.0)**2 + (y - 1.0)**2) / 0.8)
    elev_saleve = 900.0 * np.exp(-((x - 1.0)**2 + (y + 1.0)**2) / 0.7)
    return 375.0 + elev_jura + elev_saleve

# ---------------------------------------------------------
# 1. Custom ML Model Classes wrapping sklearn/xgboost/mlp
# ---------------------------------------------------------

class RandomForestSpatial2D:
    """
    Coordinate-Only Random Forest Regressor.
    Note: Tree-based models partition coordinate space via axis-aligned, orthogonal splits.
    In coordinate-only mode, this leads to a blocky, step-like output surface (chessboard artifacts)
    rather than a physically continuous thermodynamic gradient.
    """
    def __init__(self, x, y, z):
        self.coords = np.column_stack((x, y))
        self.z = np.array(z)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(self.coords, self.z)
        
    def __call__(self, x_target, y_target):
        x_t = np.atleast_1d(x_target)
        y_t = np.atleast_1d(y_target)
        targets = np.column_stack((x_t, y_t))
        preds = self.model.predict(targets)
        if np.isscalar(x_target):
            return float(preds[0])
        return preds


class XGBoostSpatial2D:
    """
    Coordinate-Only XGBoost Regressor.
    Like Random Forest, gradient boosted trees partition the (X, Y) space using orthogonal step functions,
    which creates visual blockiness and fails to interpolate smooth natural transitions.
    """
    def __init__(self, x, y, z):
        self.coords = np.column_stack((x, y))
        self.z = np.array(z)
        self.model = xgb.XGBRegressor(n_estimators=100, random_state=42, max_depth=6, learning_rate=0.1)
        self.model.fit(self.coords, self.z)
        
    def __call__(self, x_target, y_target):
        x_t = np.atleast_1d(x_target)
        y_t = np.atleast_1d(y_target)
        targets = np.column_stack((x_t, y_t))
        preds = self.model.predict(targets)
        if np.isscalar(x_target):
            return float(preds[0])
        return preds


class SVRSpatial2D:
    """
    Coordinate-Only Support Vector Regression with RBF kernel.
    RBF kernel projects coordinates into an infinite-dimensional feature space,
    resulting in a smooth, continuous, and physically plausible temperature surface.
    """
    def __init__(self, x, y, z):
        self.coords = np.column_stack((x, y))
        self.z = np.array(z)
        self.model = make_pipeline(StandardScaler(), SVR(kernel='rbf', C=10.0, epsilon=0.1))
        self.model.fit(self.coords, self.z)
        
    def __call__(self, x_target, y_target):
        x_t = np.atleast_1d(x_target)
        y_t = np.atleast_1d(y_target)
        targets = np.column_stack((x_t, y_t))
        preds = self.model.predict(targets)
        if np.isscalar(x_target):
            return float(preds[0])
        return preds


class MLPSpatial2D:
    """
    Coordinate-Only Multi-Layer Perceptron neural network.
    Constructs a smooth temperature field using non-linear tanh activation functions.
    Trained using L-BFGS, which is highly efficient and stable for small spatial datasets.
    """
    def __init__(self, x, y, z):
        self.coords = np.column_stack((x, y))
        self.z = np.array(z)
        self.model = make_pipeline(
            StandardScaler(),
            MLPRegressor(hidden_layer_sizes=(128, 64), activation='tanh', solver='lbfgs', alpha=0.1, max_iter=500, random_state=42)
        )
        self.model.fit(self.coords, self.z)
        
    def __call__(self, x_target, y_target):
        x_t = np.atleast_1d(x_target)
        y_t = np.atleast_1d(y_target)
        targets = np.column_stack((x_t, y_t))
        preds = self.model.predict(targets)
        if np.isscalar(x_target):
            return float(preds[0])
        return preds


class RandomForestFeatureFusion2D:
    """
    Feature Fusion Random Forest Regressor.
    Fuses coordinates (X, Y) with physically informed features (Elevation, Lake Distance).
    Helps the tree-based model capture local microclimate trends (like the elevation lapse rate)
    more effectively than coordinates alone.
    """
    def __init__(self, x, y, elev, dist_lake, z):
        self.features = np.column_stack((x, y, elev, dist_lake))
        self.z = np.array(z)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(self.features, self.z)
        
    def __call__(self, x_target, y_target, elev_target, dist_lake_target):
        x_t = np.atleast_1d(x_target)
        y_t = np.atleast_1d(y_target)
        el_t = np.atleast_1d(elev_target)
        dl_t = np.atleast_1d(dist_lake_target)
        targets = np.column_stack((x_t, y_t, el_t, dl_t))
        preds = self.model.predict(targets)
        if np.isscalar(x_target):
            return float(preds[0])
        return preds


class XGBoostFeatureFusion2D:
    """
    Feature Fusion XGBoost Regressor.
    Combines coordinates and spatial covariates to predict temperature gradients.
    """
    def __init__(self, x, y, elev, dist_lake, z):
        self.features = np.column_stack((x, y, elev, dist_lake))
        self.z = np.array(z)
        self.model = xgb.XGBRegressor(n_estimators=100, random_state=42, max_depth=6, learning_rate=0.1)
        self.model.fit(self.features, self.z)
        
    def __call__(self, x_target, y_target, elev_target, dist_lake_target):
        x_t = np.atleast_1d(x_target)
        y_t = np.atleast_1d(y_target)
        el_t = np.atleast_1d(elev_target)
        dl_t = np.atleast_1d(dist_lake_target)
        targets = np.column_stack((x_t, y_t, el_t, dl_t))
        preds = self.model.predict(targets)
        if np.isscalar(x_target):
            return float(preds[0])
        return preds


class SVRFeatureFusion2D:
    """
    Feature Fusion Support Vector Regression.
    Incorporating covariates (Elevation and Lake Distance) directly into the SVR RBF kernel
    results in a highly realistic thermodynamic surface that respects physical boundary conditions.
    """
    def __init__(self, x, y, elev, dist_lake, z):
        self.features = np.column_stack((x, y, elev, dist_lake))
        self.z = np.array(z)
        self.model = make_pipeline(StandardScaler(), SVR(kernel='rbf', C=10.0, epsilon=0.1))
        self.model.fit(self.features, self.z)
        
    def __call__(self, x_target, y_target, elev_target, dist_lake_target):
        x_t = np.atleast_1d(x_target)
        y_t = np.atleast_1d(y_target)
        el_t = np.atleast_1d(elev_target)
        dl_t = np.atleast_1d(dist_lake_target)
        targets = np.column_stack((x_t, y_t, el_t, dl_t))
        preds = self.model.predict(targets)
        if np.isscalar(x_target):
            return float(preds[0])
        return preds


class MLPFeatureFusion2D:
    """
    Feature Fusion Multi-Layer Perceptron neural network.
    Uses RELU activations and L-BFGS solver to blend coordinates and features into a smooth surface.
    """
    def __init__(self, x, y, elev, dist_lake, z):
        self.features = np.column_stack((x, y, elev, dist_lake))
        self.z = np.array(z)
        self.model = make_pipeline(
            StandardScaler(),
            MLPRegressor(hidden_layer_sizes=(64,), activation='relu', solver='lbfgs', alpha=0.001, max_iter=500, random_state=42)
        )
        self.model.fit(self.features, self.z)
        
    def __call__(self, x_target, y_target, elev_target, dist_lake_target):
        x_t = np.atleast_1d(x_target)
        y_t = np.atleast_1d(y_target)
        el_t = np.atleast_1d(elev_target)
        dl_t = np.atleast_1d(dist_lake_target)
        targets = np.column_stack((x_t, y_t, el_t, dl_t))
        preds = self.model.predict(targets)
        if np.isscalar(x_target):
            return float(preds[0])
        return preds


# ---------------------------------------------------------
# 2. Main Driver & Analysis for Part 4 Spatial Machine Learning
# ---------------------------------------------------------

def load_data_from_csv(csv_path):
    x, y, elev, z, dist_lake = [], [], [], [], []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            x.append(float(row['X']))
            y.append(float(row['Y']))
            elev.append(float(row['Elevation']))
            z.append(float(row['Temperature']))
            dist_lake.append(float(row['dist_lake']))
    return np.array(x), np.array(y), np.array(elev), np.array(z), np.array(dist_lake)

def calculate_metrics(z_true, z_pred):
    rmse = np.sqrt(np.mean((z_true - z_pred) ** 2))
    mae = np.mean(np.abs(z_true - z_pred))
    return rmse, mae

def evaluate_loocv_single(i, x_obs, y_obs, elev_obs, dl_obs, z_obs):
    mask = np.ones(len(z_obs), dtype=bool)
    mask[i] = False
    
    x_tr, y_tr, el_tr, dl_tr, z_tr = x_obs[mask], y_obs[mask], elev_obs[mask], dl_obs[mask], z_obs[mask]
    x_val, y_val, el_val, dl_val = x_obs[i], y_obs[i], elev_obs[i], dl_obs[i]
    
    rf_c = RandomForestSpatial2D(x_tr, y_tr, z_tr)(x_val, y_val)
    xgb_c = XGBoostSpatial2D(x_tr, y_tr, z_tr)(x_val, y_val)
    svr_c = SVRSpatial2D(x_tr, y_tr, z_tr)(x_val, y_val)
    mlp_c = MLPSpatial2D(x_tr, y_tr, z_tr)(x_val, y_val)
    
    rf_f = RandomForestFeatureFusion2D(x_tr, y_tr, el_tr, dl_tr, z_tr)(x_val, y_val, el_val, dl_val)
    xgb_f = XGBoostFeatureFusion2D(x_tr, y_tr, el_tr, dl_tr, z_tr)(x_val, y_val, el_val, dl_val)
    svr_f = SVRFeatureFusion2D(x_tr, y_tr, el_tr, dl_tr, z_tr)(x_val, y_val, el_val, dl_val)
    mlp_f = MLPFeatureFusion2D(x_tr, y_tr, el_tr, dl_tr, z_tr)(x_val, y_val, el_val, dl_val)
    
    return rf_c, xgb_c, svr_c, mlp_c, rf_f, xgb_f, svr_f, mlp_f

def run_ml_comparison():
    code_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(code_dir, "..", "data")
    images_dir = os.path.join(code_dir, "..", "images")
    os.makedirs(images_dir, exist_ok=True)
    
    csv_path = os.path.join(data_dir, "sensors_data.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Sensor dataset not found at {csv_path}.")
        
    x_obs, y_obs, elev_obs, z_obs, dl_obs = load_data_from_csv(csv_path)
    
    model_rf_c = RandomForestSpatial2D(x_obs, y_obs, z_obs)
    model_xgb_c = XGBoostSpatial2D(x_obs, y_obs, z_obs)
    model_svr_c = SVRSpatial2D(x_obs, y_obs, z_obs)
    model_mlp_c = MLPSpatial2D(x_obs, y_obs, z_obs)
    
    model_rf_f = RandomForestFeatureFusion2D(x_obs, y_obs, elev_obs, dl_obs, z_obs)
    model_xgb_f = XGBoostFeatureFusion2D(x_obs, y_obs, elev_obs, dl_obs, z_obs)
    model_svr_f = SVRFeatureFusion2D(x_obs, y_obs, elev_obs, dl_obs, z_obs)
    model_mlp_f = MLPFeatureFusion2D(x_obs, y_obs, elev_obs, dl_obs, z_obs)
    
    z_pred_rf_c = model_rf_c(x_obs, y_obs)
    z_pred_xgb_c = model_xgb_c(x_obs, y_obs)
    z_pred_svr_c = model_svr_c(x_obs, y_obs)
    z_pred_mlp_c = model_mlp_c(x_obs, y_obs)
    
    z_pred_rf_f = model_rf_f(x_obs, y_obs, elev_obs, dl_obs)
    z_pred_xgb_f = model_xgb_f(x_obs, y_obs, elev_obs, dl_obs)
    z_pred_svr_f = model_svr_f(x_obs, y_obs, elev_obs, dl_obs)
    z_pred_mlp_f = model_mlp_f(x_obs, y_obs, elev_obs, dl_obs)
    
    rmse_rf_c, mae_rf_c = calculate_metrics(z_obs, z_pred_rf_c)
    rmse_xgb_c, mae_xgb_c = calculate_metrics(z_obs, z_pred_xgb_c)
    rmse_svr_c, mae_svr_c = calculate_metrics(z_obs, z_pred_svr_c)
    rmse_mlp_c, mae_mlp_c = calculate_metrics(z_obs, z_pred_mlp_c)
    
    rmse_rf_f, mae_rf_f = calculate_metrics(z_obs, z_pred_rf_f)
    rmse_xgb_f, mae_xgb_f = calculate_metrics(z_obs, z_pred_xgb_f)
    rmse_svr_f, mae_svr_f = calculate_metrics(z_obs, z_pred_svr_f)
    rmse_mlp_f, mae_mlp_f = calculate_metrics(z_obs, z_pred_mlp_f)
    
    print("Running parallel LOOCV evaluation...")
    n_samples = len(z_obs)
    loocv_results = Parallel(n_jobs=-1)(
        delayed(evaluate_loocv_single)(i, x_obs, y_obs, elev_obs, dl_obs, z_obs)
        for i in range(n_samples)
    )
    
    loocv_rf_c = np.array([r[0] for r in loocv_results])
    loocv_xgb_c = np.array([r[1] for r in loocv_results])
    loocv_svr_c = np.array([r[2] for r in loocv_results])
    loocv_mlp_c = np.array([r[3] for r in loocv_results])
    
    loocv_rf_f = np.array([r[4] for r in loocv_results])
    loocv_xgb_f = np.array([r[5] for r in loocv_results])
    loocv_svr_f = np.array([r[6] for r in loocv_results])
    loocv_mlp_f = np.array([r[7] for r in loocv_results])
    
    rmse_rf_c_cv = np.sqrt(np.mean((z_obs - loocv_rf_c)**2))
    rmse_xgb_c_cv = np.sqrt(np.mean((z_obs - loocv_xgb_c)**2))
    rmse_svr_c_cv = np.sqrt(np.mean((z_obs - loocv_svr_c)**2))
    rmse_mlp_c_cv = np.sqrt(np.mean((z_obs - loocv_mlp_c)**2))
    
    rmse_rf_f_cv = np.sqrt(np.mean((z_obs - loocv_rf_f)**2))
    rmse_xgb_f_cv = np.sqrt(np.mean((z_obs - loocv_xgb_f)**2))
    rmse_svr_f_cv = np.sqrt(np.mean((z_obs - loocv_svr_f)**2))
    rmse_mlp_f_cv = np.sqrt(np.mean((z_obs - loocv_mlp_f)**2))
    
    grid_x, grid_y = np.meshgrid(np.linspace(-1, 1, 100), np.linspace(-1, 1, 100))
    grid_x_f = grid_x.ravel()
    grid_y_f = grid_y.ravel()
    grid_elev = get_grid_elevation(grid_x_f, grid_y_f)
    grid_dl = get_lake_distance(grid_x_f, grid_y_f)
    
    grid_z_rf_c = model_rf_c(grid_x_f, grid_y_f).reshape(grid_x.shape)
    grid_z_xgb_c = model_xgb_c(grid_x_f, grid_y_f).reshape(grid_x.shape)
    grid_z_svr_c = model_svr_c(grid_x_f, grid_y_f).reshape(grid_x.shape)
    grid_z_mlp_c = model_mlp_c(grid_x_f, grid_y_f).reshape(grid_x.shape)
    
    grid_z_rf_f = model_rf_f(grid_x_f, grid_y_f, grid_elev, grid_dl).reshape(grid_x.shape)
    grid_z_xgb_f = model_xgb_f(grid_x_f, grid_y_f, grid_elev, grid_dl).reshape(grid_x.shape)
    grid_z_svr_f = model_svr_f(grid_x_f, grid_y_f, grid_elev, grid_dl).reshape(grid_x.shape)
    grid_z_mlp_f = model_mlp_f(grid_x_f, grid_y_f, grid_elev, grid_dl).reshape(grid_x.shape)
    
    grid_z_true_full = get_true_temperature(grid_x_f, grid_y_f)
    z_true_flat = grid_z_true_full.ravel()
    grid_z_true = grid_z_true_full.reshape(grid_x.shape)
    
    rmse_rf_c_grid, mae_rf_c_grid = calculate_metrics(z_true_flat, grid_z_rf_c.ravel())
    rmse_xgb_c_grid, mae_xgb_c_grid = calculate_metrics(z_true_flat, grid_z_xgb_c.ravel())
    rmse_svr_c_grid, mae_svr_c_grid = calculate_metrics(z_true_flat, grid_z_svr_c.ravel())
    rmse_mlp_c_grid, mae_mlp_c_grid = calculate_metrics(z_true_flat, grid_z_mlp_c.ravel())
    
    rmse_rf_f_grid, mae_rf_f_grid = calculate_metrics(z_true_flat, grid_z_rf_f.ravel())
    rmse_xgb_f_grid, mae_xgb_f_grid = calculate_metrics(z_true_flat, grid_z_xgb_f.ravel())
    rmse_svr_f_grid, mae_svr_f_grid = calculate_metrics(z_true_flat, grid_z_svr_f.ravel())
    rmse_mlp_f_grid, mae_mlp_f_grid = calculate_metrics(z_true_flat, grid_z_mlp_f.ravel())
    
    print("\n" + "="*110)
    print("      Geneva Machine Learning Spatial Regression Benchmarks (Coordinates vs. Multi-Source Feature Fusion)")
    print("="*110)
    print(f"RF (Coords Only):  In-Sample RMSE = {rmse_rf_c:.4f}°C, LOOCV RMSE = {rmse_rf_c_cv:.4f}°C, Grid GT RMSE = {rmse_rf_c_grid:.4f}°C")
    print(f"XGB (Coords Only): In-Sample RMSE = {rmse_xgb_c:.4f}°C, LOOCV RMSE = {rmse_xgb_c_cv:.4f}°C, Grid GT RMSE = {rmse_xgb_c_grid:.4f}°C")
    print(f"SVR (Coords Only): In-Sample RMSE = {rmse_svr_c:.4f}°C, LOOCV RMSE = {rmse_svr_c_cv:.4f}°C, Grid GT RMSE = {rmse_svr_c_grid:.4f}°C")
    print(f"MLP (Coords Only): In-Sample RMSE = {rmse_mlp_c:.4f}°C, LOOCV RMSE = {rmse_mlp_c_cv:.4f}°C, Grid GT RMSE = {rmse_mlp_c_grid:.4f}°C")
    print("-" * 110)
    print(f"RF (Fusion):       In-Sample RMSE = {rmse_rf_f:.4f}°C, LOOCV RMSE = {rmse_rf_f_cv:.4f}°C, Grid GT RMSE = {rmse_rf_f_grid:.4f}°C")
    print(f"XGB (Fusion):      In-Sample RMSE = {rmse_xgb_f:.4f}°C, LOOCV RMSE = {rmse_xgb_f_cv:.4f}°C, Grid GT RMSE = {rmse_xgb_f_grid:.4f}°C")
    print(f"SVR (Fusion):      In-Sample RMSE = {rmse_svr_f:.4f}°C, LOOCV RMSE = {rmse_svr_f_cv:.4f}°C, Grid GT RMSE = {rmse_svr_f_grid:.4f}°C")
    print(f"MLP (Fusion):      In-Sample RMSE = {rmse_mlp_f:.4f}°C, LOOCV RMSE = {rmse_mlp_f_cv:.4f}°C, Grid GT RMSE = {rmse_mlp_f_grid:.4f}°C")
    print("="*110 + "\n")
    
    metrics_csv_path = os.path.join(data_dir, "ml_benchmarks_summary.csv")
    with open(metrics_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Model', 'In-Sample RMSE', 'LOOCV RMSE', 'Grid GT RMSE', 'Grid GT MAE'])
        writer.writerow(['RF (Coords)', f"{rmse_rf_c:.6f}", f"{rmse_rf_c_cv:.6f}", f"{rmse_rf_c_grid:.6f}", f"{mae_rf_c_grid:.6f}"])
        writer.writerow(['XGB (Coords)', f"{rmse_xgb_c:.6f}", f"{rmse_xgb_c_cv:.6f}", f"{rmse_xgb_c_grid:.6f}", f"{mae_xgb_c_grid:.6f}"])
        writer.writerow(['SVR (Coords)', f"{rmse_svr_c:.6f}", f"{rmse_svr_c_cv:.6f}", f"{rmse_svr_c_grid:.6f}", f"{mae_svr_c_grid:.6f}"])
        writer.writerow(['MLP (Coords)', f"{rmse_mlp_c:.6f}", f"{rmse_mlp_c_cv:.6f}", f"{rmse_mlp_c_grid:.6f}", f"{mae_mlp_c_grid:.6f}"])
        writer.writerow(['RF (Fusion)', f"{rmse_rf_f:.6f}", f"{rmse_rf_f_cv:.6f}", f"{rmse_rf_f_grid:.6f}", f"{mae_rf_f_grid:.6f}"])
        writer.writerow(['XGB (Fusion)', f"{rmse_xgb_f:.6f}", f"{rmse_xgb_f_cv:.6f}", f"{rmse_xgb_f_grid:.6f}", f"{mae_xgb_f_grid:.6f}"])
        writer.writerow(['SVR (Fusion)', f"{rmse_svr_f:.6f}", f"{rmse_svr_f_cv:.6f}", f"{rmse_svr_f_grid:.6f}", f"{mae_svr_f_grid:.6f}"])
        writer.writerow(['MLP (Fusion)', f"{rmse_mlp_f:.6f}", f"{rmse_mlp_f_cv:.6f}", f"{rmse_mlp_f_grid:.6f}", f"{mae_mlp_f_grid:.6f}"])
        
    print(f"Saved numerical benchmarks to {metrics_csv_path}")
    
    if not HAS_MATPLOTLIB:
        return
        
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    temp_ticks = np.linspace(22.0, 34.0, 7)
    err_ticks = np.linspace(-3.0, 3.0, 7)

    def add_colorbar(fig, ax, mappable, label="", ticks=None):
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.25)
        if ticks is not None:
            cbar = fig.colorbar(mappable, cax=cax, extend='both', ticks=ticks)
        else:
            cbar = fig.colorbar(mappable, cax=cax, extend='both')
        cbar.set_label(label, fontsize=14)
        cbar.ax.tick_params(labelsize=13)
        return cbar

    # Plot 1: Coordinate-only Comparison (2x3 landscape grid)
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    sc = axes[0, 0].scatter(x_obs, y_obs, c=z_obs, cmap='coolwarm', edgecolor='k', s=60, vmin=22.0, vmax=34.0)
    axes[0, 0].set_title("Observed Sensor Stations", fontsize=12.5, fontweight='bold', pad=8)
    axes[0, 0].set_xlim(-1.05, 1.05)
    axes[0, 0].set_ylim(-1.05, 1.05)
    add_colorbar(fig, axes[0, 0], sc, "Temperature (°C)", temp_ticks)

    im0 = axes[0, 1].imshow(grid_z_true, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[0, 1].set_title("Ground Truth Temperature Field", fontsize=12.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[0, 1], im0, "Temperature (°C)", temp_ticks)
    
    im1 = axes[0, 2].imshow(grid_z_rf_c, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[0, 2].set_title("Random Forest (Coords Only)\nChessboard Step Artifacts", fontsize=12.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[0, 2], im1, "Temperature (°C)", temp_ticks)
    
    im2 = axes[1, 0].imshow(grid_z_xgb_c, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[1, 0].set_title("XGBoost (Coords Only)\nChessboard Step Artifacts", fontsize=12.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[1, 0], im2, "Temperature (°C)", temp_ticks)
    
    im3 = axes[1, 1].imshow(grid_z_svr_c, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[1, 1].set_title("SVR RBF (Coords Only)\nSmooth Continuous Kernel", fontsize=12.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[1, 1], im3, "Temperature (°C)", temp_ticks)
    
    im4 = axes[1, 2].imshow(grid_z_mlp_c, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[1, 2].set_title("MLP Tanh (Coords Only)\nSmooth Sigmoidal Surface", fontsize=12.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[1, 2], im4, "Temperature (°C)", temp_ticks)
    
    for ax in axes.ravel():
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel("X (Normalized)", fontsize=13, labelpad=6)
        ax.set_ylabel("Y (Normalized)", fontsize=13, labelpad=6)
        ax.tick_params(labelsize=12)
        ax.label_outer()
        
    plt.tight_layout()
    plot1_path = os.path.join(images_dir, "ml_coordinate_comparison.png")
    plt.savefig(plot1_path, dpi=150)
    plt.close()
    print(f"Saved coordinate-only comparison plot to {plot1_path}")
    
    # Plot 1b: Coordinate-only Residual Error Comparison (2x2 grid)
    fig, axes = plt.subplots(2, 2, figsize=(11, 10))
    
    err_rf_c = grid_z_rf_c - grid_z_true
    err_xgb_c = grid_z_xgb_c - grid_z_true
    err_svr_c = grid_z_svr_c - grid_z_true
    err_mlp_c = grid_z_mlp_c - grid_z_true
    
    im_ec0 = axes[0, 0].imshow(err_rf_c, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=-3.0, vmax=3.0)
    axes[0, 0].set_title(f"RF Coords Residual (Pred - True)\nGrid RMSE: {rmse_rf_c_grid:.3f}°C | Grid MAE: {mae_rf_c_grid:.3f}°C", fontsize=11.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[0, 0], im_ec0, "Residual (°C)", err_ticks)
    
    im_ec1 = axes[0, 1].imshow(err_xgb_c, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=-3.0, vmax=3.0)
    axes[0, 1].set_title(f"XGB Coords Residual (Pred - True)\nGrid RMSE: {rmse_xgb_c_grid:.3f}°C | Grid MAE: {mae_xgb_c_grid:.3f}°C", fontsize=11.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[0, 1], im_ec1, "Residual (°C)", err_ticks)
    
    im_ec2 = axes[1, 0].imshow(err_svr_c, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=-3.0, vmax=3.0)
    axes[1, 0].set_title(f"SVR Coords Residual (Pred - True)\nGrid RMSE: {rmse_svr_c_grid:.3f}°C | Grid MAE: {mae_svr_c_grid:.3f}°C", fontsize=11.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[1, 0], im_ec2, "Residual (°C)", err_ticks)
    
    im_ec3 = axes[1, 1].imshow(err_mlp_c, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=-3.0, vmax=3.0)
    axes[1, 1].set_title(f"MLP Coords Residual (Pred - True)\nGrid RMSE: {rmse_mlp_c_grid:.3f}°C | Grid MAE: {mae_mlp_c_grid:.3f}°C", fontsize=11.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[1, 1], im_ec3, "Residual (°C)", err_ticks)
    
    for ax in axes.ravel():
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel("X (Normalized)", fontsize=13, labelpad=6)
        ax.set_ylabel("Y (Normalized)", fontsize=13, labelpad=6)
        ax.tick_params(labelsize=12)
        ax.label_outer()
        
    plt.tight_layout()
    plot1b_path = os.path.join(images_dir, "ml_coordinate_error_comparison.png")
    plt.savefig(plot1b_path, dpi=150)
    plt.close()
    print(f"Saved coordinate-only residual error comparison plot to {plot1b_path}")
    
    # Plot 2: Extrapolation Blindspots
    ext_grid_x, ext_grid_y = np.meshgrid(np.linspace(-2, 2, 100), np.linspace(-2, 2, 100))
    ext_grid_x_f = ext_grid_x.ravel()
    ext_grid_y_f = ext_grid_y.ravel()
    
    ext_z_rf = model_rf_c(ext_grid_x_f, ext_grid_y_f).reshape(ext_grid_x.shape)
    ext_z_xgb = model_xgb_c(ext_grid_x_f, ext_grid_y_f).reshape(ext_grid_x.shape)
    ext_z_svr = model_svr_c(ext_grid_x_f, ext_grid_y_f).reshape(ext_grid_x.shape)
    ext_z_mlp = model_mlp_c(ext_grid_x_f, ext_grid_y_f).reshape(ext_grid_x.shape)
    
    fig, axes = plt.subplots(2, 2, figsize=(11, 10))
    
    im_ext_rf = axes[0, 0].imshow(ext_z_rf, extent=[-2, 2, -2, 2], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[0, 0].set_title("Random Forest Extrapolation ([-2, 2])", fontsize=13, fontweight='bold', pad=8)
    axes[0, 0].plot([-1, 1, 1, -1, -1], [-1, -1, 1, 1, -1], 'k--', alpha=0.7, label='Training Bounds [-1,1]')
    axes[0, 0].legend(loc='upper right', fontsize=10.5)
    add_colorbar(fig, axes[0, 0], im_ext_rf, "Temperature (°C)", temp_ticks)
    
    im_ext_xgb = axes[0, 1].imshow(ext_z_xgb, extent=[-2, 2, -2, 2], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[0, 1].set_title("XGBoost Extrapolation ([-2, 2])", fontsize=13, fontweight='bold', pad=8)
    axes[0, 1].plot([-1, 1, 1, -1, -1], [-1, -1, 1, 1, -1], 'k--', alpha=0.7, label='Training Bounds [-1,1]')
    axes[0, 1].legend(loc='upper right', fontsize=10.5)
    add_colorbar(fig, axes[0, 1], im_ext_xgb, "Temperature (°C)", temp_ticks)
    
    im_ext_svr = axes[1, 0].imshow(ext_z_svr, extent=[-2, 2, -2, 2], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[1, 0].set_title("SVR RBF Extrapolation ([-2, 2])", fontsize=13, fontweight='bold', pad=8)
    axes[1, 0].plot([-1, 1, 1, -1, -1], [-1, -1, 1, 1, -1], 'k--', alpha=0.7, label='Training Bounds [-1,1]')
    axes[1, 0].legend(loc='upper right', fontsize=10.5)
    add_colorbar(fig, axes[1, 0], im_ext_svr, "Temperature (°C)", temp_ticks)
    
    im_ext_mlp = axes[1, 1].imshow(ext_z_mlp, extent=[-2, 2, -2, 2], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[1, 1].set_title("MLP Tanh Extrapolation ([-2, 2])", fontsize=13, fontweight='bold', pad=8)
    axes[1, 1].plot([-1, 1, 1, -1, -1], [-1, -1, 1, 1, -1], 'k--', alpha=0.7, label='Training Bounds [-1,1]')
    axes[1, 1].legend(loc='upper right', fontsize=10.5)
    add_colorbar(fig, axes[1, 1], im_ext_mlp, "Temperature (°C)", temp_ticks)
    
    for ax in axes.ravel():
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel("X (Normalized)", fontsize=13, labelpad=6)
        ax.set_ylabel("Y (Normalized)", fontsize=13, labelpad=6)
        ax.tick_params(labelsize=12)
        ax.label_outer()
        
    plt.tight_layout()
    plot2_path = os.path.join(images_dir, "ml_extrapolation_comparison.png")
    plt.savefig(plot2_path, dpi=150)
    plt.close()
    print(f"Saved extrapolation comparison plot to {plot2_path}")
    
    # Plot 3: Feature Fusion Comparison (2x3 landscape grid)
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    sc_f = axes[0, 0].scatter(x_obs, y_obs, c=z_obs, cmap='coolwarm', edgecolor='k', s=60, vmin=22.0, vmax=34.0)
    axes[0, 0].set_title("Observed Sensor Stations", fontsize=12.5, fontweight='bold', pad=8)
    axes[0, 0].set_xlim(-1.05, 1.05)
    axes[0, 0].set_ylim(-1.05, 1.05)
    add_colorbar(fig, axes[0, 0], sc_f, "Temperature (°C)", temp_ticks)

    im0_f = axes[0, 1].imshow(grid_z_true, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[0, 1].set_title("Ground Truth Temperature Field", fontsize=12.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[0, 1], im0_f, "Temperature (°C)", temp_ticks)
    
    im_f_rf = axes[0, 2].imshow(grid_z_rf_f, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[0, 2].set_title("Random Forest (Feature Fusion)", fontsize=12.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[0, 2], im_f_rf, "Temperature (°C)", temp_ticks)
    
    im_f_xgb = axes[1, 0].imshow(grid_z_xgb_f, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[1, 0].set_title("XGBoost (Feature Fusion)", fontsize=12.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[1, 0], im_f_xgb, "Temperature (°C)", temp_ticks)
    
    im_f_svr = axes[1, 1].imshow(grid_z_svr_f, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[1, 1].set_title("SVR (Feature Fusion)", fontsize=12.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[1, 1], im_f_svr, "Temperature (°C)", temp_ticks)
    
    im_f_mlp = axes[1, 2].imshow(grid_z_mlp_f, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=22.0, vmax=34.0)
    axes[1, 2].set_title("MLP (Feature Fusion)", fontsize=12.5, fontweight='bold', pad=8)
    add_colorbar(fig, axes[1, 2], im_f_mlp, "Temperature (°C)", temp_ticks)
    
    for ax in axes.ravel():
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel("X (Normalized)", fontsize=13, labelpad=6)
        ax.set_ylabel("Y (Normalized)", fontsize=13, labelpad=6)
        ax.tick_params(labelsize=12)
        ax.label_outer()
        
    plt.tight_layout()
    plot3_path = os.path.join(images_dir, "ml_feature_fusion_comparison.png")
    plt.savefig(plot3_path, dpi=150)
    plt.close()
    print(f"Saved feature fusion comparison plot to {plot3_path}")
    
    # Plot 4: Residual Error Comparison (4x2 grid)
    fig, axes = plt.subplots(4, 2, figsize=(11, 20))
    
    err_rf_c = grid_z_rf_c - grid_z_true
    err_rf_f = grid_z_rf_f - grid_z_true
    err_xgb_c = grid_z_xgb_c - grid_z_true
    err_xgb_f = grid_z_xgb_f - grid_z_true
    err_svr_c = grid_z_svr_c - grid_z_true
    err_svr_f = grid_z_svr_f - grid_z_true
    err_mlp_c = grid_z_mlp_c - grid_z_true
    err_mlp_f = grid_z_mlp_f - grid_z_true
    
    im_e0 = axes[0, 0].imshow(err_rf_c, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=-3.0, vmax=3.0)
    axes[0, 0].set_title(f"RF Coords Residual (Pred - True)\nGrid RMSE: {rmse_rf_c_grid:.3f}°C | Grid MAE: {mae_rf_c_grid:.3f}°C", fontsize=12, fontweight='bold', pad=7)
    add_colorbar(fig, axes[0, 0], im_e0, "Residual (°C)", err_ticks)
    
    im_e1 = axes[0, 1].imshow(err_rf_f, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=-3.0, vmax=3.0)
    axes[0, 1].set_title(f"RF Fusion Residual (Pred - True)\nGrid RMSE: {rmse_rf_f_grid:.3f}°C | Grid MAE: {mae_rf_f_grid:.3f}°C", fontsize=12, fontweight='bold', pad=7)
    add_colorbar(fig, axes[0, 1], im_e1, "Residual (°C)", err_ticks)
    
    im_e2 = axes[1, 0].imshow(err_xgb_c, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=-3.0, vmax=3.0)
    axes[1, 0].set_title(f"XGB Coords Residual (Pred - True)\nGrid RMSE: {rmse_xgb_c_grid:.3f}°C | Grid MAE: {mae_xgb_c_grid:.3f}°C", fontsize=12, fontweight='bold', pad=7)
    add_colorbar(fig, axes[1, 0], im_e2, "Residual (°C)", err_ticks)
    
    im_e3 = axes[1, 1].imshow(err_xgb_f, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=-3.0, vmax=3.0)
    axes[1, 1].set_title(f"XGB Fusion Residual (Pred - True)\nGrid RMSE: {rmse_xgb_f_grid:.3f}°C | Grid MAE: {mae_xgb_f_grid:.3f}°C", fontsize=12, fontweight='bold', pad=7)
    add_colorbar(fig, axes[1, 1], im_e3, "Residual (°C)", err_ticks)
    
    im_e4 = axes[2, 0].imshow(err_svr_c, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=-3.0, vmax=3.0)
    axes[2, 0].set_title(f"SVR Coords Residual (Pred - True)\nGrid RMSE: {rmse_svr_c_grid:.3f}°C | Grid MAE: {mae_svr_c_grid:.3f}°C", fontsize=12, fontweight='bold', pad=7)
    add_colorbar(fig, axes[2, 0], im_e4, "Residual (°C)", err_ticks)
    
    im_e5 = axes[2, 1].imshow(err_svr_f, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=-3.0, vmax=3.0)
    axes[2, 1].set_title(f"SVR Fusion Residual (Pred - True)\nGrid RMSE: {rmse_svr_f_grid:.3f}°C | Grid MAE: {mae_svr_f_grid:.3f}°C", fontsize=12, fontweight='bold', pad=7)
    add_colorbar(fig, axes[2, 1], im_e5, "Residual (°C)", err_ticks)
    
    im_e6 = axes[3, 0].imshow(err_mlp_c, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=-3.0, vmax=3.0)
    axes[3, 0].set_title(f"MLP Coords Residual (Pred - True)\nGrid RMSE: {rmse_mlp_c_grid:.3f}°C | Grid MAE: {mae_mlp_c_grid:.3f}°C", fontsize=12, fontweight='bold', pad=7)
    add_colorbar(fig, axes[3, 0], im_e6, "Residual (°C)", err_ticks)
    
    im_e7 = axes[3, 1].imshow(err_mlp_f, extent=[-1, 1, -1, 1], origin='lower', cmap='coolwarm', vmin=-3.0, vmax=3.0)
    axes[3, 1].set_title(f"MLP Fusion Residual (Pred - True)\nGrid RMSE: {rmse_mlp_f_grid:.3f}°C | Grid MAE: {mae_mlp_f_grid:.3f}°C", fontsize=12, fontweight='bold', pad=7)
    add_colorbar(fig, axes[3, 1], im_e7, "Residual (°C)", err_ticks)
    
    for ax in axes.ravel():
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel("X (Normalized)", fontsize=13, labelpad=6)
        ax.set_ylabel("Y (Normalized)", fontsize=13, labelpad=6)
        ax.tick_params(labelsize=12)
        ax.label_outer()
        
    plt.tight_layout()
    plot4_path = os.path.join(images_dir, "ml_error_comparison.png")
    plt.savefig(plot4_path, dpi=150)
    plt.close()
    print(f"Saved residual error comparison plot to {plot4_path}")

if __name__ == "__main__":
    run_ml_comparison()
