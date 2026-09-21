"""
Geneva Spatial Interpolation Validation Benchmark
=================================================
Executes the empirical benchmark comparing four spatial interpolation methods:
1. Polynomial Surface (Degree 2)
2. Inverse Distance Weighting (p = 2.0)
3. Radial Basis Functions (Thin-Plate Spline with linear drift)
4. Ordinary Kriging (Spherical semivariogram refitted per split)

Across four validation strategies:
1. Leave-One-Out Cross-Validation (LOOCV)
2. Random 5-Fold Cross-Validation (20 repeated random seeds)
3. Spatial Block Cross-Validation (4 quadrants: NW, NE, SW, SE)
4. Buffered Validation (r = 0.30, with sensitivity at r = 0.20, 0.40)

Evaluated against:
- Continuous 10,000-point full-grid latent temperature field (Domain Reference).
- Observed sensor residuals (observable CV metric).
- Latent temperature residuals (synthetic-data diagnostic).

Outputs:
- benchmark_results.json
"""

import os
import csv
import json
import numpy as np
from data_generator import get_true_temperature, ensure_sensors_data
from solvers import PolynomialSurface, InverseDistanceWeighting, RadialBasisFunctions2D, OrdinaryKriging2D


def load_sensors(csv_path):
    ensure_sensors_data(csv_path)
    sensors = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sensors.append({
                'sensor_id': row['sensor_id'],
                'X': float(row['X']),
                'Y': float(row['Y']),
                'Elevation': float(row['Elevation']),
                'Temperature': float(row['Temperature']),
                'dist_lake': float(row['dist_lake'])
            })
    return sensors


def compute_metrics(errors):
    errors = np.asarray(errors, dtype=float)
    rmse = float(np.sqrt(np.mean(errors ** 2)))
    mae = float(np.mean(np.abs(errors)))
    return rmse, mae


def run_benchmark():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(script_dir, ".."))
    data_dir = os.path.join(project_dir, "data") if os.path.exists(os.path.join(project_dir, "data")) else os.path.join(script_dir, "data")
    csv_path = os.path.join(data_dir, "sensors_data.csv")
    sensors = load_sensors(csv_path)
    n_sensors = len(sensors)
    
    sensor_ids = [s['sensor_id'] for s in sensors]
    x_obs = np.array([s['X'] for s in sensors])
    y_obs = np.array([s['Y'] for s in sensors])
    z_obs = np.array([s['Temperature'] for s in sensors])
    coords = np.column_stack([x_obs, y_obs])
    
    # Noise-free latent temperature at sensor locations
    z_true_sensors = get_true_temperature(x_obs, y_obs)
    
    models = {
        'Polynomial': PolynomialSurface,
        'IDW': InverseDistanceWeighting,
        'RBF': RadialBasisFunctions2D,
        'Kriging': OrdinaryKriging2D
    }
    
    results = {
        'grid_ground_truth': {},
        'loocv': {},
        'random_5fold': {
            'seeds': {},
            'aggregate': {}
        },
        'spatial_block': {},
        'buffered': {
            'r_0.30': {},
            'sensitivity': {}
        },
        'point_predictions': [],
        'kriging_diagnostics': []
    }
    
    print(f"Loaded {n_sensors} sensors from {csv_path}.")
    print("=" * 70)
    print("1. EVALUATING FULL-GRID LATENT-FIELD REFERENCE (10,000 points)")
    print("=" * 70)
    
    # 1. Full-Grid Reference (100x100 = 10,000 points over [-1, 1] x [-1, 1])
    grid_1d = np.linspace(-1.0, 1.0, 100)
    gx, gy = np.meshgrid(grid_1d, grid_1d)
    gx_f = gx.ravel()
    gy_f = gy.ravel()
    z_grid_true = get_true_temperature(gx_f, gy_f)
    
    for name, ModelClass in models.items():
        model = ModelClass(x_obs, y_obs, z_obs)
        z_grid_pred = model(gx_f, gy_f)
        grid_err = z_grid_pred - z_grid_true
        rmse_grid, mae_grid = compute_metrics(grid_err)
        results['grid_ground_truth'][name] = {
            'rmse': rmse_grid,
            'mae': mae_grid
        }
        print(f"  {name:<12}: RMSE_grid = {rmse_grid:.4f}°C | MAE_grid = {mae_grid:.4f}°C")
        
    print("\n" + "=" * 70)
    print("2. EVALUATING LEAVE-ONE-OUT CROSS-VALIDATION (LOOCV: 100 iterations)")
    print("=" * 70)
    
    loocv_preds = {name: np.zeros(n_sensors) for name in models}
    loocv_dmin = np.zeros(n_sensors)
    
    for i in range(n_sensors):
        train_mask = np.ones(n_sensors, dtype=bool)
        train_mask[i] = False
        
        x_tr, y_tr, z_tr = x_obs[train_mask], y_obs[train_mask], z_obs[train_mask]
        tx, ty, tz_obs, tz_latent = x_obs[i], y_obs[i], z_obs[i], z_true_sensors[i]
        
        d_min = float(np.min(np.linalg.norm(coords[train_mask] - coords[i], axis=1)))
        loocv_dmin[i] = d_min
        
        for name, ModelClass in models.items():
            model = ModelClass(x_tr, y_tr, z_tr)
            pred = float(model(tx, ty))
            loocv_preds[name][i] = pred
            
            err_obs = pred - tz_obs
            err_latent = pred - tz_latent
            
            results['point_predictions'].append({
                'model': name,
                'scheme': 'LOOCV',
                'seed': None,
                'fold': i,
                'sensor_id': sensor_ids[i],
                'x': float(tx),
                'y': float(ty),
                'observed_z': float(tz_obs),
                'true_z': float(tz_latent),
                'predicted_z': float(pred),
                'error_observed': float(err_obs),
                'error_latent': float(err_latent),
                'd_min': float(d_min),
                'n_available': int(len(x_tr))
            })
            
            if name == 'Kriging':
                results['kriging_diagnostics'].append({
                    'scheme': 'LOOCV',
                    'fold': i,
                    **model.diagnostics
                })

    for name in models:
        err_obs = loocv_preds[name] - z_obs
        err_latent = loocv_preds[name] - z_true_sensors
        rmse_obs, mae_obs = compute_metrics(err_obs)
        rmse_lat, mae_lat = compute_metrics(err_latent)
        results['loocv'][name] = {
            'rmse_obs': rmse_obs,
            'mae_obs': mae_obs,
            'rmse_latent': rmse_lat,
            'mae_latent': mae_lat
        }
        print(f"  {name:<12}: RMSE_obs = {rmse_obs:.4f}°C | MAE_obs = {mae_obs:.4f}°C (Latent RMSE: {rmse_lat:.4f}°C)")
        
    print("\n" + "=" * 70)
    print("3. EVALUATING RANDOM 5-FOLD CV (20 repeated seeds, 5 folds of 20 sensors)")
    print("=" * 70)
    
    seeds = list(range(42, 62)) # 20 seeds: 42..61
    seed_metrics = {name: {'rmse_obs': [], 'mae_obs': [], 'rmse_latent': [], 'mae_latent': []} for name in models}
    
    for seed in seeds:
        np.random.seed(seed)
        shuffled_idx = np.random.permutation(n_sensors)
        folds = np.array_split(shuffled_idx, 5)
        
        seed_preds = {name: np.zeros(n_sensors) for name in models}
        
        for f_idx, test_idx in enumerate(folds):
            train_mask = np.ones(n_sensors, dtype=bool)
            train_mask[test_idx] = False
            
            x_tr, y_tr, z_tr = x_obs[train_mask], y_obs[train_mask], z_obs[train_mask]
            
            # Fitted models for this fold
            fold_models = {name: ModelClass(x_tr, y_tr, z_tr) for name, ModelClass in models.items()}
            
            if 'Kriging' in fold_models:
                results['kriging_diagnostics'].append({
                    'scheme': 'Random_5fold',
                    'seed': seed,
                    'fold': f_idx,
                    **fold_models['Kriging'].diagnostics
                })
            
            for t_idx in test_idx:
                tx, ty, tz_obs, tz_latent = x_obs[t_idx], y_obs[t_idx], z_obs[t_idx], z_true_sensors[t_idx]
                d_min = float(np.min(np.linalg.norm(coords[train_mask] - coords[t_idx], axis=1)))
                
                for name, model in fold_models.items():
                    pred = float(model(tx, ty))
                    seed_preds[name][t_idx] = pred
                    
                    # Store point-level predictions only for primary seed (42) to keep JSON size clean
                    if seed == 42:
                        results['point_predictions'].append({
                            'model': name,
                            'scheme': 'Random_5fold',
                            'seed': seed,
                            'fold': f_idx,
                            'sensor_id': sensor_ids[t_idx],
                            'x': float(tx),
                            'y': float(ty),
                            'observed_z': float(tz_obs),
                            'true_z': float(tz_latent),
                            'predicted_z': float(pred),
                            'error_observed': float(pred - tz_obs),
                            'error_latent': float(pred - tz_latent),
                            'd_min': float(d_min),
                            'n_available': int(len(x_tr))
                        })
                        
        for name in models:
            err_obs = seed_preds[name] - z_obs
            err_latent = seed_preds[name] - z_true_sensors
            r_obs, m_obs = compute_metrics(err_obs)
            r_lat, m_lat = compute_metrics(err_latent)
            
            seed_metrics[name]['rmse_obs'].append(r_obs)
            seed_metrics[name]['mae_obs'].append(m_obs)
            seed_metrics[name]['rmse_latent'].append(r_lat)
            seed_metrics[name]['mae_latent'].append(m_lat)
            
    for name in models:
        r_mean = float(np.mean(seed_metrics[name]['rmse_obs']))
        r_std = float(np.std(seed_metrics[name]['rmse_obs']))
        m_mean = float(np.mean(seed_metrics[name]['mae_obs']))
        m_std = float(np.std(seed_metrics[name]['mae_obs']))
        
        r_lat_mean = float(np.mean(seed_metrics[name]['rmse_latent']))
        r_lat_std = float(np.std(seed_metrics[name]['rmse_latent']))
        
        results['random_5fold']['aggregate'][name] = {
            'rmse_obs_mean': r_mean,
            'rmse_obs_std': r_std,
            'mae_obs_mean': m_mean,
            'mae_obs_std': m_std,
            'rmse_latent_mean': r_lat_mean,
            'rmse_latent_std': r_lat_std
        }
        print(f"  {name:<12}: RMSE_obs = {r_mean:.4f} ± {r_std:.4f}°C | MAE_obs = {m_mean:.4f} ± {m_std:.4f}°C")
        
    print("\n" + "=" * 70)
    print("4. EVALUATING SPATIAL BLOCK CROSS-VALIDATION (4 Quadrants)")
    print("=" * 70)
    
    # 4 Quadrants:
    # Quadrant 1 (NW): x <= 0.0, y >= 0.0
    # Quadrant 2 (NE): x > 0.0,  y >= 0.0
    # Quadrant 3 (SW): x <= 0.0, y < 0.0
    # Quadrant 4 (SE): x > 0.0,  y < 0.0
    quadrants = [
        ('NW', (x_obs <= 0.0) & (y_obs >= 0.0)),
        ('NE', (x_obs > 0.0) & (y_obs >= 0.0)),
        ('SW', (x_obs <= 0.0) & (y_obs < 0.0)),
        ('SE', (x_obs > 0.0) & (y_obs < 0.0))
    ]
    
    block_preds = {name: np.zeros(n_sensors) for name in models}
    
    for q_name, q_mask in quadrants:
        test_indices = np.where(q_mask)[0]
        train_mask = ~q_mask
        x_tr, y_tr, z_tr = x_obs[train_mask], y_obs[train_mask], z_obs[train_mask]
        
        print(f"  Quadrant {q_name}: {len(test_indices)} test sensors, {len(x_tr)} training sensors.")
        
        block_models = {name: ModelClass(x_tr, y_tr, z_tr) for name, ModelClass in models.items()}
        
        if 'Kriging' in block_models:
            results['kriging_diagnostics'].append({
                'scheme': 'Spatial_Block',
                'block': q_name,
                **block_models['Kriging'].diagnostics
            })
            
        for t_idx in test_indices:
            tx, ty, tz_obs, tz_latent = x_obs[t_idx], y_obs[t_idx], z_obs[t_idx], z_true_sensors[t_idx]
            d_min = float(np.min(np.linalg.norm(coords[train_mask] - coords[t_idx], axis=1)))
            
            for name, model in block_models.items():
                pred = float(model(tx, ty))
                block_preds[name][t_idx] = pred
                
                results['point_predictions'].append({
                    'model': name,
                    'scheme': 'Spatial_Block',
                    'seed': None,
                    'fold': q_name,
                    'sensor_id': sensor_ids[t_idx],
                    'x': float(tx),
                    'y': float(ty),
                    'observed_z': float(tz_obs),
                    'true_z': float(tz_latent),
                    'predicted_z': float(pred),
                    'error_observed': float(pred - tz_obs),
                    'error_latent': float(pred - tz_latent),
                    'd_min': float(d_min),
                    'n_available': int(len(x_tr))
                })

    for name in models:
        err_obs = block_preds[name] - z_obs
        err_latent = block_preds[name] - z_true_sensors
        rmse_obs, mae_obs = compute_metrics(err_obs)
        rmse_lat, mae_lat = compute_metrics(err_latent)
        results['spatial_block'][name] = {
            'rmse_obs': rmse_obs,
            'mae_obs': mae_obs,
            'rmse_latent': rmse_lat,
            'mae_latent': mae_lat
        }
        print(f"  {name:<12}: RMSE_obs = {rmse_obs:.4f}°C | MAE_obs = {mae_obs:.4f}°C (Latent RMSE: {rmse_lat:.4f}°C)")
        
    print("\n" + "=" * 70)
    print("5. EVALUATING BUFFERED VALIDATION (r = 0.30, sensitivity r=0.20, 0.40)")
    print("=" * 70)
    
    # Run primary buffered validation at r = 0.30
    buffer_radii = [0.20, 0.30, 0.40]
    
    for r in buffer_radii:
        r_key = f"r_{r:.2f}"
        buf_preds = {name: np.zeros(n_sensors) for name in models}
        n_avail_list = []
        d_min_list = []
        
        for i in range(n_sensors):
            # Target sensor i
            # Available set: ||x_j - x_i|| > r
            dists_to_i = np.linalg.norm(coords - coords[i], axis=1)
            train_mask = dists_to_i > r
            n_avail = int(np.sum(train_mask))
            n_avail_list.append(n_avail)
            
            x_tr, y_tr, z_tr = x_obs[train_mask], y_obs[train_mask], z_obs[train_mask]
            tx, ty, tz_obs, tz_latent = x_obs[i], y_obs[i], z_obs[i], z_true_sensors[i]
            
            d_min = float(np.min(dists_to_i[train_mask])) if n_avail > 0 else 0.0
            d_min_list.append(d_min)
            
            for name, ModelClass in models.items():
                model = ModelClass(x_tr, y_tr, z_tr)
                pred = float(model(tx, ty))
                buf_preds[name][i] = pred
                
                # Store point predictions for primary radius r = 0.30
                if np.isclose(r, 0.30):
                    results['point_predictions'].append({
                        'model': name,
                        'scheme': 'Buffered',
                        'seed': None,
                        'fold': f"r_{r:.2f}",
                        'sensor_id': sensor_ids[i],
                        'x': float(tx),
                        'y': float(ty),
                        'observed_z': float(tz_obs),
                        'true_z': float(tz_latent),
                        'predicted_z': float(pred),
                        'error_observed': float(pred - tz_obs),
                        'error_latent': float(pred - tz_latent),
                        'd_min': float(d_min),
                        'n_available': int(n_avail)
                    })
                    
                    if name == 'Kriging':
                        results['kriging_diagnostics'].append({
                            'scheme': 'Buffered',
                            'fold': i,
                            **model.diagnostics
                        })
                        
        # Aggregate metrics for this radius
        radius_summary = {}
        for name in models:
            err_obs = buf_preds[name] - z_obs
            err_latent = buf_preds[name] - z_true_sensors
            rmse_obs, mae_obs = compute_metrics(err_obs)
            rmse_lat, mae_lat = compute_metrics(err_latent)
            radius_summary[name] = {
                'rmse_obs': rmse_obs,
                'mae_obs': mae_obs,
                'rmse_latent': rmse_lat,
                'mae_latent': mae_lat
            }
            
        n_avail_stats = {
            'min': int(np.min(n_avail_list)),
            'median': float(np.median(n_avail_list)),
            'max': int(np.max(n_avail_list))
        }
        
        if np.isclose(r, 0.30):
            results['buffered']['r_0.30'] = {
                'metrics': radius_summary,
                'n_avail_stats': n_avail_stats
            }
            print(f"  [r = 0.30] Available sensors: Min = {n_avail_stats['min']}, Median = {n_avail_stats['median']}, Max = {n_avail_stats['max']}")
            for name in models:
                m = radius_summary[name]
                print(f"    {name:<12}: RMSE_obs = {m['rmse_obs']:.4f}°C | MAE_obs = {m['mae_obs']:.4f}°C (Latent RMSE: {m['rmse_latent']:.4f}°C)")
        else:
            results['buffered']['sensitivity'][r_key] = {
                'metrics': radius_summary,
                'n_avail_stats': n_avail_stats
            }
            print(f"  [Sensitivity r = {r:.2f}] Min N_avail = {n_avail_stats['min']}, Median = {n_avail_stats['median']}, Max = {n_avail_stats['max']}")
            for name in models:
                m = radius_summary[name]
                print(f"    {name:<12}: RMSE_obs = {m['rmse_obs']:.4f}°C | MAE_obs = {m['mae_obs']:.4f}°C")

    # Kriging diagnostics summary
    k_fallbacks = sum(1 for d in results['kriging_diagnostics'] if d.get('fallback_used', False))
    print("\n" + "=" * 70)
    print("KRIGING VARIOGRAM DIAGNOSTICS SUMMARY")
    print("=" * 70)
    print(f"Total Kriging variogram fits evaluated: {len(results['kriging_diagnostics'])}")
    print(f"Fallback triggers: {k_fallbacks} ({100 * k_fallbacks / max(1, len(results['kriging_diagnostics'])):.1f}%)")
    
    # Save results to JSON
    json_path = os.path.join(data_dir, "benchmark_results.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    print(f"\nSaved all benchmark metrics and point predictions to:\n  {json_path}")
    return results


if __name__ == "__main__":
    run_benchmark()
