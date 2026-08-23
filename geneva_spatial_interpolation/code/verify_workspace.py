import os
import sys

def verify():
    print("--- Running Update Workspace Verification ---")
    code_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Verify files exist
    files = ["data_generator.py", "part1_polynomial.py", "part2_local_solvers.py", "part2_libraries.py", "part3_kriging.py", "part4_spatial_ml.py"]
    for f in files:
        path = os.path.join(code_dir, f)
        if os.path.exists(path):
            print(f"[PASS] {f} exists in workspace.")
        else:
            print(f"[FAIL] {f} is missing.")
            return False
            
    # 2. Run data_generator.py and verify/create output csv
    try:
        from data_generator import generate_geneva_dataset
        data = generate_geneva_dataset(n_sensors=100)
        if len(data) == 100:
            print("[PASS] generate_geneva_dataset returns 100 sensor recordings.")
        else:
            print(f"[FAIL] generate_geneva_dataset returned {len(data)} instead of 100.")
            return False
            
        # Write the CSV if it doesn't exist
        data_dir = os.path.join(code_dir, "..", "data")
        os.makedirs(data_dir, exist_ok=True)
        csv_path = os.path.join(data_dir, "sensors_data.csv")
        if not os.path.exists(csv_path):
            import csv
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['sensor_id', 'X', 'Y', 'Elevation', 'Temperature', 'dist_lake'])
                writer.writeheader()
                writer.writerows(data)
    except Exception as e:
        print(f"[FAIL] Error running data_generator: {e}")
        return False
        
    # 3. Check CSV creation
    if os.path.exists(csv_path):
        print(f"[PASS] sensors_data.csv successfully created at: {csv_path}")
    else:
        print(f"[FAIL] sensors_data.csv was not found at {csv_path}.")
        return False
        
    # 4. Run model evaluations (part1_polynomial.py)
    try:
        from part1_polynomial import run_polynomial_analysis
        run_polynomial_analysis()
        
        # Verify plots were generated in the images directory
        images_dir = os.path.join(code_dir, "..", "images")
        plot1 = os.path.join(images_dir, "polyfit_comparison.png")
        plot2 = os.path.join(images_dir, "polyfit_error_comparison.png")
        if os.path.exists(plot1) and os.path.exists(plot2):
            print("[PASS] Polynomial Analysis ran successfully and generated plots in the images directory.")
        else:
            print("[FAIL] Polynomial Analysis ran but one or more plots are missing from the images directory.")
            return False
    except Exception as e:
        print(f"[FAIL] Error running part1_polynomial verify: {e}")
        return False
        
    # 5. Run custom model evaluations (part2_local_solvers.py)
    try:
        from part2_local_solvers import NearestNeighbor2D, InverseDistanceWeighting, RadialBasisFunctions2D, load_data_from_csv, calculate_metrics
        x, y, elev, z = load_data_from_csv(csv_path)
        
        model_nn = NearestNeighbor2D(x, y, z)
        pred_nn = model_nn(x, y)
        rmse_nn, _ = calculate_metrics(z, pred_nn)
        print(f"[PASS] Custom Nearest Neighbor running. In-sample RMSE={rmse_nn:.4f}")
        
        model_idw = InverseDistanceWeighting(x, y, z, power=2.0)
        pred_idw = model_idw(x, y)
        rmse_idw, _ = calculate_metrics(z, pred_idw)
        print(f"[PASS] Custom IDW (power=2) running. In-sample RMSE={rmse_idw:.4f}")

        model_rbf = RadialBasisFunctions2D(x, y, z, smoothing=0.0)
        pred_rbf = model_rbf(x, y)
        rmse_rbf, _ = calculate_metrics(z, pred_rbf)
        print(f"[PASS] Custom RBF Thin-Plate running. In-sample RMSE={rmse_rbf:.4f}")
        
    except Exception as e:
        print(f"[FAIL] Error running part2_local_solvers verify: {e}")
        return False

    # 6. Run library evaluations (part2_libraries.py)
    try:
        from part2_libraries import run_library_geospatial_comparison
        run_library_geospatial_comparison()
        
        # Verify plots were generated in the images directory
        images_dir = os.path.join(code_dir, "..", "images")
        lib_plots = ["geospatial_model_comparison_plots.png", "geospatial_kriging_comparison_plots.png", "kriging_variance_map.png"]
        for p in lib_plots:
            plot_path = os.path.join(images_dir, p)
            if not os.path.exists(plot_path):
                print(f"[FAIL] Library interpolation plot missing: {plot_path}")
                return False
        print("[PASS] Library Interpolation Analysis ran successfully and generated all comparison plots.")
    except Exception as e:
        print(f"[FAIL] Error running part2_libraries verify: {e}")
        return False

    # 7. Run Kriging evaluations (part3_kriging.py)
    try:
        from part3_kriging import run_kriging_analysis
        run_kriging_analysis()
        
        # Verify plots were generated in the images directory
        images_dir = os.path.join(code_dir, "..", "images")
        kriging_plots = ["kriging_variogram.png", "kriging_comparison.png", "kriging_error_comparison.png"]
        for p in kriging_plots:
            plot_path = os.path.join(images_dir, p)
            if not os.path.exists(plot_path):
                print(f"[FAIL] Kriging Analysis plot missing: {plot_path}")
                return False
        print("[PASS] Geostatistics & Kriging Analysis ran successfully and generated all plots.")
    except Exception as e:
        print(f"[FAIL] Error running part3_kriging verify: {e}")
        return False
        
    # 8. Run ML evaluations (part4_spatial_ml.py)
    try:
        from part4_spatial_ml import run_ml_comparison
        run_ml_comparison()
        
        # Verify plots were generated in the images directory
        images_dir = os.path.join(code_dir, "..", "images")
        ml_plots = ["ml_coordinate_comparison.png", "ml_extrapolation_comparison.png", "ml_feature_fusion_comparison.png", "ml_error_comparison.png"]
        for p in ml_plots:
            plot_path = os.path.join(images_dir, p)
            if not os.path.exists(plot_path):
                print(f"[FAIL] ML Analysis plot missing: {plot_path}")
                return False
        print("[PASS] ML Spatial Regression ran successfully and generated all plots in the images directory.")
    except Exception as e:
        print(f"[FAIL] Error running part4_spatial_ml verify: {e}")
        return False
        
    print("\n[ALL PASS] Updated workspace codes verified successfully.")
    return True

if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
