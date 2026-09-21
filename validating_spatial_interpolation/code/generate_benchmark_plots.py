"""
Generate Publication Benchmark Plots
====================================
Generates the two empirical figures for the Geneva Validation Benchmark:
1. Figure 4: images/geneva_validation_benchmark_rmse.png
   Four panels comparing validation RMSE across LOOCV, Random 5-fold, Spatial Block,
   and Buffered (r = 0.30), with horizontal reference lines for full-grid latent-field RMSE.
2. Figure 5: images/geneva_error_vs_distance.png
   Four panels showing absolute validation error |e_i| against distance to the nearest
   available observation d_i^min, with adaptive binned medians, interquartile ranges (IQR),
   and unified figure legend.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe


def load_benchmark_data(json_path):
    if not os.path.exists(json_path):
        from run_validation_benchmark import run_benchmark
        return run_benchmark()
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def plot_figure_4(data, output_path):
    """
    Figure 4: 2x2 comparison of RMSE across validation schemes with full-grid reference lines.
    Optimized for high legibility on 680px container widths with collision-free badge placement.
    """
    plt.rcParams['font.family'] = 'DejaVu Sans'
    fig, axes = plt.subplots(2, 2, figsize=(14.0, 11.5), dpi=200)
    
    models = ['Polynomial', 'IDW', 'RBF', 'Kriging']
    model_titles = {
        'Polynomial': 'A: Global Polynomial Surface (Degree 2)',
        'IDW': 'B: Inverse Distance Weighting (IDW, p = 2.0)',
        'RBF': 'C: Radial Basis Functions (Thin-Plate Spline)',
        'Kriging': 'D: Ordinary Kriging (Spherical Variogram)'
    }
    
    # Multi-line strategy labels to eliminate horizontal text collisions
    strategies_labels = ['LOOCV', 'Random\n5-fold', 'Spatial\nBlock', 'Buffered\n(r = 0.30)']
    strategy_colors = ['#1d3557', '#2a9d8f', '#e76f51', '#c1121f']
    
    for idx, model_name in enumerate(models):
        ax = axes[idx // 2, idx % 2]
        
        # Grid ground truth reference
        rmse_grid = data['grid_ground_truth'][model_name]['rmse']
        
        # Validation RMSE values
        rmse_loocv = data['loocv'][model_name]['rmse_obs']
        rmse_5fold = data['random_5fold']['aggregate'][model_name]['rmse_obs_mean']
        std_5fold = data['random_5fold']['aggregate'][model_name]['rmse_obs_std']
        rmse_block = data['spatial_block'][model_name]['rmse_obs']
        rmse_buf = data['buffered']['r_0.30']['metrics'][model_name]['rmse_obs']
        
        rmse_values = [rmse_loocv, rmse_5fold, rmse_block, rmse_buf]
        y_errs = [0.0, std_5fold, 0.0, 0.0]
        
        # Generous vertical headroom to prevent badges from touching top spine or legend
        max_val = max(max(rmse_values), rmse_grid)
        y_limit = max_val * 1.36
        ax.set_ylim(0, y_limit)
        
        x_pos = np.arange(len(strategies_labels))
        bars = ax.bar(
            x_pos, rmse_values, yerr=y_errs, capsize=6,
            color=strategy_colors, edgecolor='#1b263b', linewidth=1.4,
            width=0.52, zorder=3
        )
        
        # Horizontal reference line for full-grid latent RMSE
        ax.axhline(
            rmse_grid, color='#2563eb', linestyle='--', linewidth=2.2,
            label=f'Full-grid latent-field RMSE: {rmse_grid:.3f}°C', zorder=2
        )
        
        # Numeric labels above bars with collision avoidance against reference line
        badge_half_h = 0.038 * y_limit
        for b_idx, bar in enumerate(bars):
            h = bar.get_height()
            err = y_errs[b_idx]
            top_of_bar = h + err
            nominal_y = top_of_bar + 0.038 * y_limit
            
            # If nominal position collides with reference line, place badge above line with clear spacing
            if abs(nominal_y - rmse_grid) < (badge_half_h + 0.018 * y_limit):
                label_y = rmse_grid + badge_half_h + 0.018 * y_limit
            else:
                label_y = nominal_y
                
            label_txt = f"{h:.2f} ± {err:.2f}" if err > 0 else f"{h:.2f}°C"
            ax.text(
                bar.get_x() + bar.get_width() / 2.0, label_y,
                label_txt, ha='center', va='center',
                fontsize=13.0, fontweight='bold', color='#0f172a',
                bbox=dict(boxstyle='round,pad=0.28', facecolor='white', edgecolor='#cbd5e1', linewidth=1.0, alpha=0.98),
                zorder=6
            )
            
        ax.set_title(model_titles[model_name], fontsize=15.5, fontweight='bold', pad=14, color='#1b263b')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(strategies_labels, fontsize=13.0, fontweight='bold')
        ax.set_ylabel('Validation RMSE (°C)', fontsize=14.0, fontweight='bold', labelpad=10)
        ax.tick_params(axis='y', labelsize=12.5)
        
        ax.grid(axis='y', linestyle=':', alpha=0.6, zorder=0)
        ax.set_axisbelow(True)
        ax.legend(loc='upper left', framealpha=0.96, fontsize=12.5, edgecolor='#cbd5e1')
        
        # Subtle border styling
        for spine in ax.spines.values():
            spine.set_color('#94a3b8')
            spine.set_linewidth(1.2)
            
    plt.tight_layout(pad=3.2)
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Saved Figure 4 to {output_path}")


def plot_figure_5(data, output_path):
    """
    Figure 5: 2x2 scatter of |e_i| vs d_i^min with adaptive binned medians, IQR ribbons,
    and a unified figure legend.
    Optimized for high legibility on 680px container widths with collision-free layout.
    """
    plt.rcParams['font.family'] = 'DejaVu Sans'
    fig, axes = plt.subplots(2, 2, figsize=(14.4, 12.0), dpi=200)
    
    models = ['Polynomial', 'IDW', 'RBF', 'Kriging']
    model_titles = {
        'Polynomial': 'A: Global Polynomial Surface (Degree 2)',
        'IDW': 'B: Inverse Distance Weighting (IDW, p = 2.0)',
        'RBF': 'C: Radial Basis Functions (Thin-Plate Spline)',
        'Kriging': 'D: Ordinary Kriging (Spherical Variogram)'
    }
    
    scheme_styles = {
        'LOOCV': {'color': '#1d3557', 'marker': 'o', 'size': 58, 'alpha': 0.75, 'label': 'LOOCV (N=99)'},
        'Random_5fold': {'color': '#2a9d8f', 'marker': 's', 'size': 60, 'alpha': 0.80, 'label': 'Random 5-fold (N=80)'},
        'Spatial_Block': {'color': '#e76f51', 'marker': '^', 'size': 68, 'alpha': 0.85, 'label': 'Spatial Block (N≈75)'},
        'Buffered': {'color': '#c1121f', 'marker': 'D', 'size': 54, 'alpha': 0.80, 'label': 'Buffered (N: 85–98)'}
    }
    
    pts = data['point_predictions']
    bin_edges = [0.0, 0.10, 0.20, 0.30, 0.45, 0.65, 1.05]
    
    legend_handles = []
    legend_labels = []
    
    for idx, model_name in enumerate(models):
        ax = axes[idx // 2, idx % 2]
        
        # Filter points for this model
        model_pts = [p for p in pts if p['model'] == model_name]
        
        all_d = []
        all_abs_err = []
        
        for scheme_key, style in scheme_styles.items():
            sch_pts = [p for p in model_pts if p['scheme'] == scheme_key]
            if not sch_pts:
                continue
            d_vals = np.array([p['d_min'] for p in sch_pts])
            err_vals = np.array([abs(p['error_observed']) for p in sch_pts])
            
            all_d.extend(d_vals)
            all_abs_err.extend(err_vals)
            
            h_scat = ax.scatter(
                d_vals, err_vals,
                c=style['color'], marker=style['marker'], s=style['size'],
                alpha=style['alpha'], edgecolor='#0f172a', linewidth=0.7,
                zorder=3
            )
            if idx == 0:
                legend_handles.append(h_scat)
                legend_labels.append(style['label'])
                
        all_d = np.array(all_d)
        all_abs_err = np.array(all_abs_err)
        
        # Compute binned statistics across distance bins
        bin_centers = []
        bin_medians = []
        bin_q25 = []
        bin_q75 = []
        
        for b in range(len(bin_edges) - 1):
            mask = (all_d >= bin_edges[b]) & (all_d < bin_edges[b + 1])
            if np.sum(mask) >= 10:
                bin_centers.append(float(np.median(all_d[mask])))
                bin_medians.append(float(np.median(all_abs_err[mask])))
                bin_q25.append(float(np.percentile(all_abs_err[mask], 25)))
                bin_q75.append(float(np.percentile(all_abs_err[mask], 75)))
                
        bin_centers = np.array(bin_centers)
        bin_medians = np.array(bin_medians)
        bin_q25 = np.array(bin_q25)
        bin_q75 = np.array(bin_q75)
        
        # Plot IQR shaded band
        h_iqr = ax.fill_between(
            bin_centers, bin_q25, bin_q75,
            color='#64748b', alpha=0.22, zorder=4
        )
        if idx == 0:
            legend_handles.append(h_iqr)
            legend_labels.append('Binned IQR (25th–75th %ile)')
        
        # Plot median trend line
        h_line, = ax.plot(
            bin_centers, bin_medians,
            color='#0f172a', linewidth=3.4, linestyle='-',
            marker='o', markersize=7.5, zorder=5,
            path_effects=[pe.Stroke(linewidth=4.8, foreground='white'), pe.Normal()]
        )
        if idx == 0:
            legend_handles.append(h_line)
            legend_labels.append('Binned Median Trend')
            
        ax.set_title(model_titles[model_name], fontsize=15.5, fontweight='bold', pad=14, color='#1b263b')
        ax.set_xlabel(r'Nearest Available Observation Distance $d_i^{\min}$', fontsize=13.5, fontweight='bold')
        ax.set_ylabel(r'Absolute Observed Error $|e_i^{\mathrm{obs}}|$ (°C)', fontsize=13.5, fontweight='bold')
        ax.tick_params(axis='both', labelsize=12.5)
        
        # Set tailored y-limits to ensure no visual clipping
        if model_name == 'Polynomial':
            ax.set_ylim(-0.10, 2.10)
        elif model_name == 'IDW':
            ax.set_ylim(-0.25, 7.80)
        elif model_name == 'RBF':
            ax.set_ylim(-0.15, 5.20)
        elif model_name == 'Kriging':
            ax.set_ylim(-0.25, 7.60)
            
        y_top = ax.get_ylim()[1]
        
        # Clean buffer boundary indicator at d = 0.30
        ax.axvline(0.30, color='#c1121f', linestyle='--', linewidth=2.0, alpha=0.85, zorder=2)
        
        # Buffer cutoff annotation centered directly above the line
        ax.text(
            0.30, y_top * 0.93, 'Buffer cutoff (r = 0.30)',
            ha='center', va='center',
            fontsize=12.0, fontweight='bold', color='#991b1b',
            bbox=dict(boxstyle='round,pad=0.28', facecolor='#fef2f2', edgecolor='#f87171', linewidth=1.1, alpha=0.96),
            zorder=6
        )
        
        ax.grid(True, linestyle=':', alpha=0.55, zorder=0)
        ax.set_axisbelow(True)
        
        for spine in ax.spines.values():
            spine.set_color('#94a3b8')
            spine.set_linewidth(1.2)
            
    # Unified figure legend placed prominently at top center
    fig.legend(
        legend_handles, legend_labels,
        loc='upper center', bbox_to_anchor=(0.5, 0.995),
        ncol=3, fontsize=13.0, frameon=True, facecolor='#ffffff',
        edgecolor='#cbd5e1', framealpha=0.98, borderpad=0.5, handletextpad=0.6, columnspacing=1.5
    )
    
    plt.tight_layout(rect=[0, 0, 1, 0.94], pad=3.0)
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Saved Figure 5 to {output_path}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(script_dir, ".."))
    data_dir = os.path.join(project_dir, "data") if os.path.exists(os.path.join(project_dir, "data")) else os.path.join(script_dir, "data")
    json_path = os.path.join(data_dir, "benchmark_results.json") if os.path.exists(os.path.join(data_dir, "benchmark_results.json")) else os.path.join(script_dir, "benchmark_results.json")
    images_dir = os.path.join(project_dir, "images") if os.path.exists(os.path.join(project_dir, "images")) else os.path.join(script_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    fig4_path = os.path.join(images_dir, "geneva_validation_benchmark_rmse.png")
    fig5_path = os.path.join(images_dir, "geneva_error_vs_distance.png")
    data = load_benchmark_data(json_path)
    
    plot_figure_4(data, fig4_path)
    plot_figure_5(data, fig5_path)
