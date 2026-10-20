"""
Generate scientific infographic:
Seven PSF Interpolation Methods.

Key Features:
1. Focused purely on spatial interpolation of PCA coefficient fields:
   - INPUT DATA -> THREE INTERPOLATION FAMILIES -> ESTIMATED COEFFICIENTS (OUTPUT)
   - Excludes later-stage PSF image synthesis/reconstruction equations and stamps.
2. High-legibility doubled typography:
   - Title: 24.0 pt bold
   - Subtitle: 19.0 pt bold
   - Method card titles: 20.0 pt bold
   - Method characteristics: 17.0 pt bold
   - Subplot annotations: 18.0 - 24.0 pt
   - Output coefficients: 32.0 pt bold
3. Clean vertical hierarchy with ample breathing room.

Outputs:
- images/spatial_interpolation_methods_taxonomy.png (1800 x 1400 px)
- images/spatial_interpolation_methods_taxonomy_2x.png (3600 x 2800 px)
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

# Root path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.dataset import load_dataset
from representation.pca import PSFRepresentation


def generate_taxonomy_figure():
    # 1. Load dataset and extract real PCA coefficient samples
    data_dir = PROJECT_ROOT / "data" / "field_g2"
    dataset = load_dataset(str(data_dir))
    
    k_eval = 8
    pca = PSFRepresentation(n_components_max=k_eval)
    pca.fit(dataset.psfs_train_observed)
    tr_coeffs = pca.transform(dataset.psfs_train_observed, n_components=k_eval)
    
    train_pos = dataset.positions_train
    coeff_a1 = tr_coeffs[:, 0]
    
    # Styling configuration - dark text (#0f172a)
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "mathtext.fontset": "dejavusans",
        "axes.edgecolor": "#1e293b",
        "axes.linewidth": 1.25,
        "axes.labelcolor": "#0f172a",
        "xtick.color": "#0f172a",
        "ytick.color": "#0f172a",
    })
    
    # Canvas: 18.0 x 14.0 inches (1800 x 1400 px at 100 dpi)
    fig_w, fig_h = 18.0, 13.68
    
    for scale, suffix in [(1, ""), (2, "_2x")]:
        dpi = 100 * scale
        fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor="#ffffff")
        
        ax_bg = fig.add_axes([0, 0, 1, 1], facecolor="none")
        ax_bg.set_xlim(0, fig_w)
        ax_bg.set_ylim(0, fig_h)
        ax_bg.axis("off")
        
        # =====================================================================
        # MAIN HEADER
        # =====================================================================
        ax_bg.text(
            9.0, 13.26,
            "SEVEN PSF INTERPOLATION METHODS",
            ha="center", va="center",
            fontsize=24.0, fontweight="bold", color="#0f172a"
        )
        ax_bg.text(
            9.0, 12.82,
            "Estimating PCA coefficients at galaxy positions",
            ha="center", va="center",
            fontsize=19.0, fontweight="bold", color="#0f172a"
        )
        
        # =====================================================================
        # 1. INPUT DATA Card: y in [10.55, 12.75] (height 2.20 in)
        # =====================================================================
        card_l1 = FancyBboxPatch(
            (0.40, 10.23), 17.20, 2.20,
            boxstyle="round,pad=0.0,rounding_size=0.18",
            facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.5, zorder=1
        )
        ax_bg.add_patch(card_l1)
        
        pill_l1 = FancyBboxPatch(
            (0.65, 11.93), 2.60, 0.40,
            boxstyle="round,pad=0.0,rounding_size=0.08",
            facecolor="#e2e8f0", edgecolor="#94a3b8", linewidth=1.1, zorder=2
        )
        ax_bg.add_patch(pill_l1)
        ax_bg.text(
            1.95, 12.13, "INPUT DATA",
            ha="center", va="center", fontsize=18.0, fontweight="bold", color="#1e293b", zorder=3
        )
        
        ax_bg.text(
            3.45, 12.13, "—  Stellar positions and measured PCA coefficients",
            ha="left", va="center", fontsize=20.0, fontweight="bold", color="#0f172a", zorder=3
        )
        
        # Subplot: Focal plane with stellar positions
        ax_l1 = fig.add_axes([0.70 / fig_w, 10.38 / fig_h, 2.80 / fig_w, 1.40 / fig_h])
        ax_l1.set_facecolor("#ffffff")
        
        np.random.seed(42)
        star_sub = np.random.choice(len(train_pos), size=24, replace=False)
        pts_x = train_pos[star_sub, 0]
        pts_y = train_pos[star_sub, 1]
        pts_c = coeff_a1[star_sub]
        
        norm_c = Normalize(vmin=np.min(pts_c), vmax=np.max(pts_c))
        ax_l1.scatter(
            pts_x, pts_y, c=pts_c, cmap="coolwarm", norm=norm_c, s=50,
            edgecolor="#0f172a", linewidth=1.2, zorder=4
        )
        
        tg_x, tg_y = 0.72, 0.48
        ax_l1.scatter(
            tg_x, tg_y, s=140, facecolor="none", edgecolor="#dc2626",
            linewidth=2.5, linestyle="--", zorder=5
        )
        ax_l1.set_xlim(-0.05, 1.05)
        ax_l1.set_ylim(-0.05, 1.05)
        ax_l1.set_xticks([])
        ax_l1.set_yticks([])
        for spine in ax_l1.spines.values():
            spine.set_color("#94a3b8")
            spine.set_linewidth(1.0)
            
        # Explanatory lines with integrated legend icons
        dot1 = Circle((3.88, 11.48), 0.12, facecolor="#3b82f6", edgecolor="#0f172a", linewidth=1.2, zorder=4)
        ax_bg.add_patch(dot1)
        ax_bg.text(
            4.15, 11.48,
            r"Stellar samples: PCA coefficients $a_k(\mathbf{r}_i)$ measured directly from isolated reference stars",
            ha="left", va="center", fontsize=21.0, color="#0f172a", zorder=3
        )
        
        dot2 = Circle((3.88, 10.96), 0.14, facecolor="none", edgecolor="#dc2626", linewidth=2.0, linestyle="--", zorder=4)
        ax_bg.add_patch(dot2)
        ax_bg.text(
            4.15, 10.96,
            r"Target position ($\mathbf{r}_g$): Unobserved galaxy coordinate requiring coefficient estimation",
            ha="left", va="center", fontsize=21.0, color="#0f172a", zorder=3
        )
        
        dot3 = Circle((3.88, 10.44), 0.10, facecolor="#0284c7", edgecolor="none", zorder=4)
        ax_bg.add_patch(dot3)
        ax_bg.text(
            4.15, 10.44,
            r"Interpolation task: Estimate $\widehat{a}_k(\mathbf{r}_g)$ for each retained component $k = 1, \dots, K$",
            ha="left", va="center", fontsize=21.0, color="#0f172a", style="italic", zorder=3
        )
        
        # Flow arrow from Input Data to Methods
        arrow_l1_l2 = FancyArrowPatch(
            (9.0, 10.21), (9.0, 9.91),
            arrowstyle="Simple,tail_width=2.5,head_width=8.0,head_length=8.0",
            facecolor="#64748b", edgecolor="#334155", linewidth=0.8, zorder=5
        )
        ax_bg.add_patch(arrow_l1_l2)
        
        # =====================================================================
        # 2. FAMILY 1: DETERMINISTIC METHODS: y in [6.30, 10.10] (height 3.80 in)
        # =====================================================================
        card_fam1 = FancyBboxPatch(
            (0.40, 6.09), 17.20, 3.80,
            boxstyle="round,pad=0.0,rounding_size=0.18",
            facecolor="#f0f9ff", edgecolor="#7dd3fc", linewidth=1.5, zorder=1
        )
        ax_bg.add_patch(card_fam1)
        
        pill_fam1 = FancyBboxPatch(
            (0.65, 9.34), 4.60, 0.40,
            boxstyle="round,pad=0.0,rounding_size=0.08",
            facecolor="#e0f2fe", edgecolor="#38bdf8", linewidth=1.1, zorder=2
        )
        ax_bg.add_patch(pill_fam1)
        ax_bg.text(
            2.95, 9.54, "DETERMINISTIC METHODS",
            ha="center", va="center", fontsize=18.0, fontweight="bold", color="#0369a1", zorder=3
        )
        ax_bg.text(
            5.45, 9.54, "Surface fitting, distance weighting, and radial bases",
            ha="left", va="center", fontsize=19.0, fontweight="bold", color="#0c4a6e", zorder=3
        )
        
        # METHOD 1: POLYNOMIAL REGRESSION
        card_m1 = FancyBboxPatch(
            (0.65, 6.21), 5.30, 3.02,
            boxstyle="round,pad=0.0,rounding_size=0.12",
            facecolor="#ffffff", edgecolor="#bae6fd", linewidth=1.3, zorder=2
        )
        ax_bg.add_patch(card_m1)
        ax_bg.text(3.30, 8.91, "Polynomial Regression", ha="center", va="center", fontsize=20.0, fontweight="bold", color="#0f172a", zorder=3)
        ax_bg.text(3.30, 8.55, "Global polynomial trend", ha="center", va="center", fontsize=17.0, fontweight="bold", color="#0284c7", zorder=3)
        
        ax_m1 = fig.add_axes([0.85 / fig_w, 6.34 / fig_h, 4.90 / fig_w, 2.00 / fig_h])
        px = np.linspace(-1, 1, 50)
        py = np.linspace(-1, 1, 50)
        PX, PY = np.meshgrid(px, py)
        PZ = 0.5 + 0.4 * PX - 0.3 * PY + 0.25 * PX**2 - 0.35 * PX * PY + 0.2 * PY**2
        ax_m1.contourf(PX, PY, PZ, levels=12, cmap="Blues", alpha=0.75)
        ax_m1.contour(PX, PY, PZ, levels=6, colors="#0369a1", linewidths=0.9, alpha=0.8)
        
        np.random.seed(11)
        m1_pts_x = np.random.uniform(-0.8, 0.8, 9)
        m1_pts_y = np.random.uniform(-0.8, 0.8, 9)
        ax_m1.scatter(m1_pts_x, m1_pts_y, s=50, facecolor="#0284c7", edgecolor="#0f172a", linewidth=1.1, zorder=4)
        ax_m1.scatter(0.45, -0.20, s=130, facecolor="none", edgecolor="#dc2626", linewidth=2.4, linestyle="--", zorder=5)
        ax_m1.set_xticks([])
        ax_m1.set_yticks([])
        for spine in ax_m1.spines.values():
            spine.set_color("#94a3b8")
            spine.set_linewidth(0.9)
            
        # METHOD 2: INVERSE DISTANCE WEIGHTING
        card_m2 = FancyBboxPatch(
            (6.35, 6.21), 5.30, 3.02,
            boxstyle="round,pad=0.0,rounding_size=0.12",
            facecolor="#ffffff", edgecolor="#bae6fd", linewidth=1.3, zorder=2
        )
        ax_bg.add_patch(card_m2)
        ax_bg.text(9.00, 8.91, "Inverse Distance Weighting", ha="center", va="center", fontsize=20.0, fontweight="bold", color="#0f172a", zorder=3)
        ax_bg.text(9.00, 8.55, "Distance-weighted average", ha="center", va="center", fontsize=17.0, fontweight="bold", color="#0284c7", zorder=3)
        
        ax_m2 = fig.add_axes([6.55 / fig_w, 6.34 / fig_h, 4.90 / fig_w, 2.00 / fig_h])
        ax_m2.set_facecolor("#f8fafc")
        
        tg_pt = np.array([0.0, 0.0])
        angles = np.array([30, 100, 175, 230, 310]) * np.pi / 180.0
        radii = np.array([0.48, 0.80, 0.58, 0.72, 0.42])
        star_pts = np.column_stack([radii * np.cos(angles), radii * np.sin(angles)])
        
        for idx, (sp, r) in enumerate(zip(star_pts, radii)):
            ax_m2.plot([tg_pt[0], sp[0]], [tg_pt[1], sp[1]], color="#0284c7", linestyle="--", linewidth=1.8, alpha=0.85, zorder=2)
            ax_m2.scatter(sp[0], sp[1], s=55, facecolor="#0284c7", edgecolor="#0f172a", linewidth=1.1, zorder=4)
            mid_pt = 0.52 * sp
            ax_m2.text(mid_pt[0], mid_pt[1] + 0.09, f"$w_{idx+1}$", fontsize=20.0, fontweight="bold", color="#0369a1", ha="center", va="center", zorder=5)
            
        ax_m2.scatter(tg_pt[0], tg_pt[1], s=140, facecolor="none", edgecolor="#dc2626", linewidth=2.5, linestyle="--", zorder=5)
        ax_m2.set_xlim(-1.05, 1.05)
        ax_m2.set_ylim(-1.05, 1.05)
        ax_m2.set_xticks([])
        ax_m2.set_yticks([])
        for spine in ax_m2.spines.values():
            spine.set_color("#94a3b8")
            spine.set_linewidth(0.9)
            
        # METHOD 3: RBF SPLINE
        card_m3 = FancyBboxPatch(
            (12.05, 6.21), 5.30, 3.02,
            boxstyle="round,pad=0.0,rounding_size=0.12",
            facecolor="#ffffff", edgecolor="#bae6fd", linewidth=1.3, zorder=2
        )
        ax_bg.add_patch(card_m3)
        ax_bg.text(14.70, 8.91, "RBF Spline", ha="center", va="center", fontsize=20.0, fontweight="bold", color="#0f172a", zorder=3)
        ax_bg.text(14.70, 8.55, "Smooth radial basis surface", ha="center", va="center", fontsize=17.0, fontweight="bold", color="#0284c7", zorder=3)
        
        ax_m3 = fig.add_axes([12.25 / fig_w, 6.34 / fig_h, 4.90 / fig_w, 2.00 / fig_h])
        rx = np.linspace(-1, 1, 50)
        ry = np.linspace(-1, 1, 50)
        RX, RY = np.meshgrid(rx, ry)
        RZ = (
            0.6 * np.exp(-((RX + 0.4)**2 + (RY + 0.3)**2) / 0.35)
            + 0.5 * np.exp(-((RX - 0.4)**2 + (RY - 0.4)**2) / 0.45)
            - 0.4 * np.exp(-((RX - 0.3)**2 + (RY + 0.5)**2) / 0.30)
        )
        ax_m3.contourf(RX, RY, RZ, levels=12, cmap="YlGnBu", alpha=0.75)
        ax_m3.contour(RX, RY, RZ, levels=6, colors="#0284c7", linewidths=0.9, alpha=0.8)
        ax_m3.scatter([-0.4, 0.4, 0.3, -0.2], [-0.3, 0.4, -0.5, 0.5], s=50, facecolor="#0284c7", edgecolor="#0f172a", linewidth=1.1, zorder=4)
        ax_m3.scatter(0.1, 0.05, s=130, facecolor="none", edgecolor="#dc2626", linewidth=2.4, linestyle="--", zorder=5)
        ax_m3.set_xticks([])
        ax_m3.set_yticks([])
        for spine in ax_m3.spines.values():
            spine.set_color("#94a3b8")
            spine.set_linewidth(0.9)
            
        # =====================================================================
        # 3. ROW 2: GEOSTATISTICAL & MACHINE LEARNING: y in [2.10, 5.95]
        # =====================================================================
        card_fam2 = FancyBboxPatch(
            (0.40, 1.99), 8.45, 3.85,
            boxstyle="round,pad=0.0,rounding_size=0.18",
            facecolor="#f0fdf4", edgecolor="#86efac", linewidth=1.5, zorder=1
        )
        ax_bg.add_patch(card_fam2)
        
        pill_fam2 = FancyBboxPatch(
            (0.65, 5.34), 4.60, 0.40,
            boxstyle="round,pad=0.0,rounding_size=0.08",
            facecolor="#dcfce7", edgecolor="#4ade80", linewidth=1.1, zorder=2
        )
        ax_bg.add_patch(pill_fam2)
        ax_bg.text(
            2.95, 5.54, "GEOSTATISTICAL METHODS",
            ha="center", va="center", fontsize=18.0, fontweight="bold", color="#15803d", zorder=3
        )
        ax_bg.text(
            5.45, 5.54, "Covariance & trend",
            ha="left", va="center", fontsize=19.0, fontweight="bold", color="#166534", zorder=3
        )
        
        # Method 4: Ordinary Kriging
        card_m4 = FancyBboxPatch(
            (0.65, 2.11), 3.95, 3.12,
            boxstyle="round,pad=0.0,rounding_size=0.12",
            facecolor="#ffffff", edgecolor="#bbf7d0", linewidth=1.3, zorder=2
        )
        ax_bg.add_patch(card_m4)
        ax_bg.text(2.62, 4.95, "Ordinary Kriging", ha="center", va="center", fontsize=20.0, fontweight="bold", color="#0f172a", zorder=3)
        ax_bg.text(2.62, 4.65, "Constant mean +", ha="center", va="center", fontsize=17.0, fontweight="bold", color="#16a34a", zorder=3)
        ax_bg.text(2.62, 4.39, "correlated residuals", ha="center", va="center", fontsize=17.0, fontweight="bold", color="#16a34a", zorder=3)
        
        ax_m4 = fig.add_axes([0.85 / fig_w, 2.24 / fig_h, 3.55 / fig_w, 1.95 / fig_h])
        kx = np.linspace(0, 10, 80)
        k_pts_x = np.array([1.5, 3.5, 6.2, 8.8])
        k_pts_y = np.array([0.45, 0.85, 0.35, 0.70])
        mu_const = 0.55
        gp_pred = mu_const + 0.32 * np.sin(0.9 * kx) * np.cos(0.4 * kx)
        
        ax_m4.plot(kx, [mu_const]*len(kx), color="#64748b", linestyle="--", linewidth=1.8)
        ax_m4.plot(kx, gp_pred, color="#16a34a", linewidth=2.4, zorder=3)
        ax_m4.scatter(k_pts_x, k_pts_y, s=55, facecolor="#15803d", edgecolor="#0f172a", linewidth=1.2, zorder=4)
        ax_m4.scatter(5.0, gp_pred[40], s=130, facecolor="none", edgecolor="#dc2626", linewidth=2.4, linestyle="--", zorder=5)
        ax_m4.text(5.0, 0.14, "Constant mean", ha="center", va="center", fontsize=19.0, color="#475569", style="italic")
        ax_m4.set_ylim(-0.02, 1.05)
        ax_m4.set_xticks([])
        ax_m4.set_yticks([])
        for spine in ax_m4.spines.values():
            spine.set_color("#86efac")
            spine.set_linewidth(0.9)
            
        # Method 5: Universal Kriging
        card_m5 = FancyBboxPatch(
            (4.75, 2.11), 3.95, 3.12,
            boxstyle="round,pad=0.0,rounding_size=0.12",
            facecolor="#ffffff", edgecolor="#bbf7d0", linewidth=1.3, zorder=2
        )
        ax_bg.add_patch(card_m5)
        ax_bg.text(6.72, 4.95, "Universal Kriging", ha="center", va="center", fontsize=20.0, fontweight="bold", color="#0f172a", zorder=3)
        ax_bg.text(6.72, 4.65, "Polynomial drift +", ha="center", va="center", fontsize=17.0, fontweight="bold", color="#16a34a", zorder=3)
        ax_bg.text(6.72, 4.39, "correlated residuals", ha="center", va="center", fontsize=17.0, fontweight="bold", color="#16a34a", zorder=3)
        
        ax_m5 = fig.add_axes([4.95 / fig_w, 2.24 / fig_h, 3.55 / fig_w, 1.95 / fig_h])
        drift_curve = 0.25 + 0.08 * kx - 0.003 * kx**2
        uk_pred = drift_curve + 0.22 * np.cos(1.2 * kx)
        
        ax_m5.plot(kx, drift_curve, color="#2563eb", linestyle="--", linewidth=1.8)
        ax_m5.plot(kx, uk_pred, color="#16a34a", linewidth=2.4, zorder=3)
        ax_m5.scatter(k_pts_x, [uk_pred[int(px*7.9)] for px in k_pts_x], s=55, facecolor="#15803d", edgecolor="#0f172a", linewidth=1.2, zorder=4)
        ax_m5.scatter(5.0, uk_pred[40], s=130, facecolor="none", edgecolor="#dc2626", linewidth=2.4, linestyle="--", zorder=5)
        ax_m5.text(5.0, 0.14, "Polynomial drift", ha="center", va="center", fontsize=19.0, color="#2563eb", style="italic")
        ax_m5.set_ylim(-0.02, 1.05)
        ax_m5.set_xticks([])
        ax_m5.set_yticks([])
        for spine in ax_m5.spines.values():
            spine.set_color("#86efac")
            spine.set_linewidth(0.9)
            
        # FAMILY 3: MACHINE LEARNING (Right half)
        card_fam3 = FancyBboxPatch(
            (9.15, 1.99), 8.45, 3.85,
            boxstyle="round,pad=0.0,rounding_size=0.18",
            facecolor="#faf5ff", edgecolor="#d8b4fe", linewidth=1.5, zorder=1
        )
        ax_bg.add_patch(card_fam3)
        
        pill_fam3 = FancyBboxPatch(
            (9.40, 5.34), 4.20, 0.40,
            boxstyle="round,pad=0.0,rounding_size=0.08",
            facecolor="#f3e8ff", edgecolor="#c084fc", linewidth=1.1, zorder=2
        )
        ax_bg.add_patch(pill_fam3)
        ax_bg.text(
            11.50, 5.54, "MACHINE LEARNING",
            ha="center", va="center", fontsize=18.0, fontweight="bold", color="#7e22ce", zorder=3
        )
        ax_bg.text(
            13.80, 5.54, "Learned mappings",
            ha="left", va="center", fontsize=19.0, fontweight="bold", color="#6b21a8", zorder=3
        )
        
        # Method 6: Multilayer Perceptron (MLP)
        card_m6 = FancyBboxPatch(
            (9.40, 2.11), 3.95, 3.12,
            boxstyle="round,pad=0.0,rounding_size=0.12",
            facecolor="#ffffff", edgecolor="#e9d5ff", linewidth=1.3, zorder=2
        )
        ax_bg.add_patch(card_m6)
        ax_bg.text(11.37, 4.95, "Multilayer Perceptron", ha="center", va="center", fontsize=20.0, fontweight="bold", color="#0f172a", zorder=3)
        ax_bg.text(11.37, 4.55, "Learned nonlinear mapping", ha="center", va="center", fontsize=17.0, fontweight="bold", color="#9333ea", zorder=3)
        
        ax_m6 = fig.add_axes([9.60 / fig_w, 2.24 / fig_h, 3.55 / fig_w, 1.95 / fig_h])
        ax_m6.set_facecolor("#ffffff")
        
        l1_y = [0.72, 0.38]
        l2_y = [0.90, 0.67, 0.44, 0.21]
        l3_y = [0.80, 0.54, 0.28]
        l4_y = [0.54]
        
        for y1 in l1_y:
            for y2 in l2_y:
                ax_m6.plot([0.16, 0.42], [y1, y2], color="#cbd5e1", linewidth=1.0, zorder=1)
        for y2 in l2_y:
            for y3 in l3_y:
                ax_m6.plot([0.42, 0.68], [y2, y3], color="#cbd5e1", linewidth=1.0, zorder=1)
        for y3 in l3_y:
            for y4 in l4_y:
                ax_m6.plot([0.68, 0.88], [y3, y4], color="#c084fc", linewidth=1.3, zorder=1)
                
        for y, lbl in zip(l1_y, ["$x$", "$y$"]):
            ax_m6.scatter(0.16, y, s=200, facecolor="#e0e7ff", edgecolor="#4338ca", linewidth=1.3, zorder=3)
            ax_m6.text(0.16, y, lbl, ha="center", va="center", fontsize=18.0, fontweight="bold", color="#312e81", zorder=4)
        for y in l2_y:
            ax_m6.scatter(0.42, y, s=150, facecolor="#f3e8ff", edgecolor="#7e22ce", linewidth=1.3, zorder=3)
        for y in l3_y:
            ax_m6.scatter(0.68, y, s=150, facecolor="#f3e8ff", edgecolor="#7e22ce", linewidth=1.3, zorder=3)
        for y in l4_y:
            ax_m6.scatter(0.88, y, s=220, facecolor="#fae8ff", edgecolor="#a21caf", linewidth=1.5, zorder=3)
            ax_m6.text(0.88, y, r"$\widehat{a}_k$", ha="center", va="center", fontsize=19.0, fontweight="bold", color="#701a75", zorder=4)
            
        ax_m6.text(0.16, 0.05, "Inputs", ha="center", va="center", fontsize=18.0, fontweight="bold", color="#475569")
        ax_m6.text(0.55, 0.05, "Hidden", ha="center", va="center", fontsize=18.0, fontweight="bold", color="#7e22ce")
        ax_m6.text(0.88, 0.05, "Output", ha="center", va="center", fontsize=18.0, fontweight="bold", color="#701a75")
        
        ax_m6.set_xlim(0.02, 1.02)
        ax_m6.set_ylim(-0.06, 0.98)
        ax_m6.set_xticks([])
        ax_m6.set_yticks([])
        for spine in ax_m6.spines.values():
            spine.set_color("#d8b4fe")
            spine.set_linewidth(0.9)
            
        # Method 7: Random Forest
        card_m7 = FancyBboxPatch(
            (13.50, 2.11), 3.95, 3.12,
            boxstyle="round,pad=0.0,rounding_size=0.12",
            facecolor="#ffffff", edgecolor="#e9d5ff", linewidth=1.3, zorder=2
        )
        ax_bg.add_patch(card_m7)
        ax_bg.text(15.47, 4.95, "Random Forest", ha="center", va="center", fontsize=20.0, fontweight="bold", color="#0f172a", zorder=3)
        ax_bg.text(15.47, 4.55, "Ensemble of spatial trees", ha="center", va="center", fontsize=17.0, fontweight="bold", color="#9333ea", zorder=3)
        
        ax_m7 = fig.add_axes([13.70 / fig_w, 2.24 / fig_h, 3.55 / fig_w, 1.95 / fig_h])
        ax_m7.set_facecolor("#ffffff")
        
        tree_x_centers = [0.18, 0.48, 0.78]
        for tc in tree_x_centers:
            ax_m7.scatter(tc, 0.88, s=100, facecolor="#f3e8ff", edgecolor="#7e22ce", linewidth=1.3, zorder=3)
            ax_m7.plot([tc, tc - 0.09], [0.88, 0.58], color="#9333ea", linewidth=1.3, zorder=2)
            ax_m7.plot([tc, tc + 0.09], [0.88, 0.58], color="#9333ea", linewidth=1.3, zorder=2)
            ax_m7.scatter(tc - 0.09, 0.58, s=85, facecolor="#f3e8ff", edgecolor="#7e22ce", linewidth=1.2, zorder=3)
            ax_m7.scatter(tc + 0.09, 0.58, s=85, facecolor="#f3e8ff", edgecolor="#7e22ce", linewidth=1.2, zorder=3)
            for leaf_dx in [-0.045, 0.045]:
                ax_m7.plot([tc - 0.09, tc - 0.09 + leaf_dx], [0.58, 0.28], color="#a855f7", linewidth=1.1, zorder=2)
                ax_m7.scatter(tc - 0.09 + leaf_dx, 0.28, s=55, facecolor="#d8b4fe", edgecolor="#6b21a8", linewidth=1.0, zorder=3)
                ax_m7.plot([tc + 0.09, tc + 0.09 + leaf_dx], [0.58, 0.28], color="#a855f7", linewidth=1.1, zorder=2)
                ax_m7.scatter(tc + 0.09 + leaf_dx, 0.28, s=55, facecolor="#d8b4fe", edgecolor="#6b21a8", linewidth=1.0, zorder=3)
                
        ax_m7.text(0.48, 0.14, "Ensemble average", ha="center", va="center", fontsize=18.0, fontweight="bold", color="#6b21a8")
        ax_m7.text(0.48, -0.01, r"$\to \widehat{a}_k(\mathbf{r}_g)$", ha="center", va="center", fontsize=20.0, fontweight="bold", color="#6b21a8")
        
        ax_m7.set_xlim(0.02, 0.98)
        ax_m7.set_ylim(-0.14, 0.98)
        ax_m7.set_xticks([])
        ax_m7.set_yticks([])
        for spine in ax_m7.spines.values():
            spine.set_color("#d8b4fe")
            spine.set_linewidth(0.9)
            
        # Flow arrow from Methods to Output
        arrow_l2_l3 = FancyArrowPatch(
            (9.0, 1.97), (9.0, 1.67),
            arrowstyle="Simple,tail_width=2.5,head_width=8.0,head_length=8.0",
            facecolor="#64748b", edgecolor="#334155", linewidth=0.8, zorder=5
        )
        ax_bg.add_patch(arrow_l2_l3)
        
        # =====================================================================
        # 4. BOTTOM OUTPUT STRIP: y in [0.25, 1.65] (height 1.40 in)
        # =====================================================================
        card_out = FancyBboxPatch(
            (0.40, 0.25), 17.20, 1.40,
            boxstyle="round,pad=0.0,rounding_size=0.18",
            facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.5, zorder=1
        )
        ax_bg.add_patch(card_out)
        
        pill_out = FancyBboxPatch(
            (0.65, 1.15), 2.20, 0.36,
            boxstyle="round,pad=0.0,rounding_size=0.08",
            facecolor="#e2e8f0", edgecolor="#94a3b8", linewidth=1.1, zorder=2
        )
        ax_bg.add_patch(pill_out)
        ax_bg.text(
            1.75, 1.33, "OUTPUT",
            ha="center", va="center", fontsize=17.0, fontweight="bold", color="#1e293b", zorder=3
        )
        
        ax_bg.text(
            3.05, 1.33, "—  Estimated PCA coefficients at the target position",
            ha="left", va="center", fontsize=19.0, fontweight="bold", color="#0f172a", zorder=3
        )
        
        # Estimated coefficients formula on left, descriptive note on right
        ax_bg.text(
            5.25, 0.70,
            r"$\widehat{a}_1(\mathbf{r}_g),\, \ldots,\, \widehat{a}_K(\mathbf{r}_g)$",
            ha="center", va="center", fontsize=32.0, fontweight="bold", color="#0f172a", zorder=3
        )
        ax_bg.text(
            7.90, 0.70,
            r"Estimated coefficient vector for all $K$ retained" "\n" r"components at galaxy position $\mathbf{r}_g$",
            ha="left", va="center", fontsize=21.0, color="#475569", style="italic", linespacing=1.25, zorder=3
        )
        
        # Save output images
        out_path = PROJECT_ROOT / "images" / f"spatial_interpolation_methods_taxonomy{suffix}.png"
        fig.savefig(out_path, dpi=dpi, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        print(f"[OK] Saved {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    generate_taxonomy_figure()
