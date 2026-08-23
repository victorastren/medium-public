# Mastering Spatial Interpolation: Geneva Temperature Series

This directory contains the complete Python codebase for the 4-part publication series on **Mastering Spatial Interpolation**, published under **Stellar Priors**.

The series guides readers through the mathematical foundations, first-principles implementations, and empirical benchmarks of spatial interpolation—progressing from global polynomials and local neighborhood solvers to geostatistical Kriging and feature-fused spatial machine learning.

---

## 🗺️ Series Roadmap & Code Structure

The project is structured into a 4-part progression matching the publication series:

### [Part 1: Polynomials & B-Splines](code/part1_polynomial.py)
* **Concepts**: Global trend surfaces using Bivariate Polynomials and B-Spline surface fitting.
* **Math Focus**: Least-squares fitting of polynomial surfaces, degrees of freedom, and spline smoothing/regularization parameters (`s`).

### [Part 2: Local Interpolation Models (NN, IDW & RBF)](code/part2_local_solvers.py)
* **Concepts**: Nearest Neighbor, Delaunay TIN, Sibson Natural Neighbor, Inverse Distance Weighting (IDW), and Radial Basis Functions (RBF).
* **Math Focus**: Handling exact-match singularities in IDW ($d=0$), and Thin-Plate Spline (TPS) kernel matrix systems ($Kw = z$) for RBF.
* **Libraries**: Comparison of from-scratch NumPy implementations (`part2_local_solvers.py`) and library-based solutions using SciPy (`part2_libraries.py`).

### [Part 3: Geostatistics & Kriging](code/part3_kriging.py)
* **Concepts**: Spatial Random Fields, empirical semivariogram modeling (linear/spherical/exponential), Ordinary Kriging, Universal Kriging (linear drift), and analytical uncertainty variance mapping.
* **Math Focus**: Enforcing the unbiasedness constraint ($\sum w_i = 1$) via Lagrange multipliers to establish the Best Linear Unbiased Estimator (BLUE).

### [Part 4: Spatial Machine Learning](code/part4_spatial_ml.py)
* **Concepts**: Coordinate-only ML vs. physically informed Multi-Source Feature Fusion (Elevation, Lake Distance).
* **Models**: Random Forest (RF), XGBoost (XGB), Support Vector Regression (SVR), and Multi-Layer Perceptrons (MLP).
* **Key Finding**: Demonstrates **chessboard artifacts** (blocky, axis-aligned step-function splits) in coordinate-only tree models, and how continuous models (RBF SVR, Tanh MLPs) and auxiliary physical features resolve them.

---

## 🧪 Synthetic Dataset Simulation

To model realistic temperature gradients, `data_generator.py` simulates a microclimate in the Geneva basin ($X, Y \in [-1, 1]$) incorporating:
1. **Macro Trend**: Regional cooling towards the north-east.
2. **Elevation Lapse Rate**: Adiabatic lapse rate cooling of $-0.0065^\circ\text{C}$ per meter above the valley floor ($375\text{m}$), using Jura and Salève topography.
3. **Lake Breeze Effect**: Exponentially decaying shoreline cooling up to $-2.5^\circ\text{C}$ centered around Lake Geneva (Lac Léman).
4. **Sensor Voids**: Zero stations placed within the lake boundary (representing physical deployment constraints).
5. **Weather/Instrument Noise**: Random Gaussian fluctuations ($\sigma = 0.15^\circ\text{C}$).

---

## 🚀 Getting Started

### 📋 Prerequisites

Choose one of the options below depending on your active terminal directory to install the packages:

* **Option A: From the repository root directory (`medium-public/`)**
  ```bash
  pip install -r geneva_spatial_interpolation/requirements.txt
  ```

* **Option B: From the `geneva_spatial_interpolation` subdirectory**
  ```bash
  pip install -r requirements.txt
  ```

*Note: Key dependencies include `numpy`, `scipy`, `pandas`, `scikit-learn`, `xgboost`, `pykrige`, and `matplotlib`.*

### 🔍 Running Verification & Analysis

To execute the entire simulation, model training, cross-validation, and plot generation pipeline:

```bash
cd code/
python3 verify_workspace.py
```

The script will verify the integrity of all modules, calculate Leave-One-Out Cross-Validation (LOOCV) metrics, and save output assets to the workspace.

---

## 📊 Outputs & Visualizations

Upon running the scripts, the following outputs are generated:
* **Data**: Sensor readings saved to `data/sensors_data.csv`, ML benchmarks to `data/ml_benchmarks_summary.csv`, and baseline models to `data/model_benchmarks_summary.csv`.
* **Images**: Visual mosaics saved to the `images/` directory:
  * `polyfit_comparison.png` & `polyfit_error_comparison.png` (Part 1)
  * `geospatial_model_comparison_plots.png` & `geospatial_kriging_comparison_plots.png` (Part 2)
  * `kriging_variogram.png`, `kriging_comparison.png`, & `kriging_variance_map.png` (Part 3)
  * `ml_coordinate_comparison.png`, `ml_extrapolation_comparison.png`, & `ml_feature_fusion_comparison.png` (Part 4)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
