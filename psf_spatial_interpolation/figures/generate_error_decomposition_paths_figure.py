"""
Generate ref conceptual two-path diagram:
Separating PCA Representation and Spatial Interpolation Errors.

Key Updates:
1. Unified font size: Set all secondary annotations ("No spatial interpolation",
   "Isolates PCA truncation", "Thin-plate spline (RBF model)",
   "Representation + interpolation error", "Reference and reconstructed PSFs use...",
   "Zero spatial interpolation error", "Includes spatial interpolation error")
   to exactly match the font size of "Image Residual" (12.5 pt).
2. Increased gap between the decomposition formula and the explanation text in the bottom banner
   (formula at y = 0.60, explanation at y = 0.18; gap = 0.42 in).
3. Preserved generous margins around intensity colorbar label inside Card A.
4. Consistent sign convention (reconstruction minus reference) matching article text.

Outputs:
- images/separating_representation_and_interpolation_errors.png (1600 x 1080 px)
- images/separating_representation_and_interpolation_errors_2x.png (3200 x 2160 px)
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Root path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.dataset import load_dataset
from representation.pca import PSFRepresentation
from reconstruction.psf import reconstruct_psfs_from_coefficients
from interpolation.classical import RBFInterpolator


def generate_error_decomposition_figure(test_idx: int = 162):
    # 1. Load dataset and compute models
    data_dir = PROJECT_ROOT / "data" / "field_g2"
    dataset = load_dataset(str(data_dir))
    
    k_eval = 8
    pca = PSFRepresentation(n_components_max=k_eval)
    pca.fit(dataset.psfs_train_observed)
    
    tr_coeffs = pca.transform(dataset.psfs_train_observed, n_components=k_eval)
    test_coeffs_direct = pca.transform(dataset.psfs_test_true, n_components=k_eval)
    rec_trunc_all = reconstruct_psfs_from_coefficients(test_coeffs_direct, pca, physical_adjustment=True)
    
    # RBF Spline interpolator (top performer in G2)
    rbf = RBFInterpolator(smoothing=1e-8)
    rbf.fit(dataset.positions_train, tr_coeffs)
    pred_rbf = rbf.predict(dataset.positions_test)
    rec_rbf_all = reconstruct_psfs_from_coefficients(pred_rbf, pca, physical_adjustment=True)
    
    # Representative test star
    ref_psf = dataset.psfs_test_true[test_idx]
    trunc_psf = rec_trunc_all[test_idx]
    rec_psf = rec_rbf_all[test_idx]
    
    # Residuals: (reconstructed minus reference, matching article convention)
    res_trunc = trunc_psf - ref_psf  # P_K - P
    res_rec = rec_psf - ref_psf      # P̂_K - P
    
    # Annotation font sizes
    F_BOX = 13.0          # Inside arrow pills / boxes
    F_ANNOT_SEC = 14.0    # Secondary black italic annotations ("No spatial interpolation", etc.)
    
    # Styling configuration - all text in dark black (#0f172a)
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
    
    # Canvas geometry: 16.0 x 10.8 inches (1600 x 1080 px at 100 dpi)
    fig_w, fig_h = 16.0, 10.8
    
    for scale, suffix in [(1, ""), (2, "_2x")]:
        dpi = 100 * scale
        fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor="#ffffff")
        
        # Base canvas axes for coordinates and cards
        ax_bg = fig.add_axes([0, 0, 1, 1], facecolor="none")
        ax_bg.set_xlim(0, fig_w)
        ax_bg.set_ylim(0, fig_h)
        ax_bg.axis("off")
        
        # --- TITLE HEADER ---
        ax_bg.text(
            8.0, 10.38,
            "SEPARATING PCA REPRESENTATION AND SPATIAL INTERPOLATION ERRORS",
            ha="center", va="center",
            fontsize=20.5, fontweight="bold", color="#0f172a"
        )
        ax_bg.text(
            8.0, 10.02,
            r"Scenario G2: Optical Aberrations and Correlated Atmospheric Variations ($K = 8$)",
            ha="center", va="center",
            fontsize=15.5, fontweight="bold", color="#0f172a"
        )
        
        # --- CARD CONTAINERS ---
        # Card A (Top row): y from 5.46 to 9.70 (h = 4.24)
        card_a = FancyBboxPatch(
            (0.35, 5.46), 15.30, 4.24,
            boxstyle="round,pad=0.0,rounding_size=0.18",
            facecolor="#f8fafc", edgecolor="#93c5fd", linewidth=1.6,
            zorder=1
        )
        ax_bg.add_patch(card_a)
        
        # Card B (Bottom row): y from 1.15 to 5.28 (h = 4.13)
        # Clean gap between Card A and Card B: 5.46 - 5.28 = 0.18 inches
        card_b = FancyBboxPatch(
            (0.35, 1.15), 15.30, 4.13,
            boxstyle="round,pad=0.0,rounding_size=0.18",
            facecolor="#faf5ff", edgecolor="#d8b4fe", linewidth=1.6,
            zorder=1
        )
        ax_bg.add_patch(card_b)
        
        # Card Headers (Pills)
        pill_a = FancyBboxPatch(
            (0.65, 9.24), 7.80, 0.36,
            boxstyle="round,pad=0.0,rounding_size=0.10",
            facecolor="#dbeafe", edgecolor="#60a5fa", linewidth=1.3,
            zorder=2
        )
        ax_bg.add_patch(pill_a)
        ax_bg.text(
            4.55, 9.42, "PATH A: DIRECT PCA PROJECTION (REPRESENTATION ERROR)",
            ha="center", va="center", fontsize=12.5, fontweight="bold", color="#1e40af",
            zorder=3
        )
        
        pill_b = FancyBboxPatch(
            (0.65, 4.82), 8.50, 0.36,
            boxstyle="round,pad=0.0,rounding_size=0.10",
            facecolor="#f3e8ff", edgecolor="#c084fc", linewidth=1.3,
            zorder=2
        )
        ax_bg.add_patch(pill_b)
        ax_bg.text(
            4.90, 5.00, "PATH B: PCA + SPATIAL INTERPOLATION (TOTAL RECONSTRUCTION ERROR)",
            ha="center", va="center", fontsize=12.5, fontweight="bold", color="#6b21a8",
            zorder=3
        )
        
        # Common Intensity scaling for PSF images
        psf_norm = LogNorm(vmin=5e-5, vmax=0.05)
        cmap_psf = "magma"
        
        # Image stamp geometry: 2.20 x 2.20 inches
        w_in, h_in = 2.20, 2.20
        w_norm = w_in / fig_w
        h_norm = h_in / fig_h
        
        # Column X coordinates
        x_col1_in = 0.70   # Reference PSF
        x_col2_in = 4.95   # Reconstructed / Truncated PSF
        x_col3_in = 9.20   # Residual Image
        
        # Vertical placement:
        # Row A stamps from y = 6.65 to 8.85 (titles at 8.93, giving 0.31 in gap below Pill A at 9.24)
        y_a_in = 6.65
        y_a_norm = y_a_in / fig_h
        
        # Row B stamps from y = 2.25 to 4.45 (titles at 4.53, giving 0.29 in gap below Pill B at 4.82)
        y_b_in = 2.25
        y_b_norm = y_b_in / fig_h
        
        # Residual color scales (prominently labeled)
        res_a_lim = 2.0e-5  # Representation residual (x10^-5)
        res_b_lim = 4.0e-4  # Total reconstruction residual (x10^-4)
        
        # =====================================================================
        # ROW A: DIRECT PCA PROJECTION
        # =====================================================================
        # 1. Reference PSF
        ax_a_ref = fig.add_axes([x_col1_in / fig_w, y_a_norm, w_norm, h_norm])
        im_ref_a = ax_a_ref.imshow(ref_psf, norm=psf_norm, cmap=cmap_psf, origin="lower")
        ax_a_ref.set_title(r"Reference PSF ($P$)", fontsize=14.0, fontweight="bold", color="#0f172a", pad=7)
        ax_a_ref.set_xticks([0, 24, 48])
        ax_a_ref.set_yticks([0, 24, 48])
        ax_a_ref.tick_params(labelsize=11.0, length=3.5)
        
        # Arrow 1: Ref -> Trunc
        arrow1_a = FancyArrowPatch(
            (3.02, y_a_in + 1.10), (4.85, y_a_in + 1.10),
            arrowstyle="Simple,tail_width=2.8,head_width=8.5,head_length=8.5",
            facecolor="#3b82f6", edgecolor="#1d4ed8", linewidth=0.9, zorder=4
        )
        ax_bg.add_patch(arrow1_a)
        
        box_arr1_a = FancyBboxPatch(
            (3.08, y_a_in + 1.24), 1.70, 0.70,
            boxstyle="round,pad=0.04,rounding_size=0.08",
            facecolor="#ffffff", edgecolor="#bfdbfe", linewidth=1.2, zorder=5
        )
        ax_bg.add_patch(box_arr1_a)
        ax_bg.text(
            3.93, y_a_in + 1.72, "Direct PCA",
            ha="center", va="center", fontsize=F_BOX, fontweight="bold", color="#1e40af", zorder=6
        )
        ax_bg.text(
            3.93, y_a_in + 1.43, "Projection",
            ha="center", va="center", fontsize=F_BOX, fontweight="bold", color="#1e40af", zorder=6
        )
        ax_bg.text(
            3.93, y_a_in + 0.70, "No spatial\ninterpolation",
            ha="center", va="center", fontsize=F_ANNOT_SEC, color="#0f172a", style="italic", linespacing=1.2, zorder=6
        )
        
        # 2. Truncated PSF
        ax_a_trunc = fig.add_axes([x_col2_in / fig_w, y_a_norm, w_norm, h_norm])
        ax_a_trunc.imshow(trunc_psf, norm=psf_norm, cmap=cmap_psf, origin="lower")
        ax_a_trunc.set_title(r"Truncated PSF ($P_K$)", fontsize=14.0, fontweight="bold", color="#0f172a", pad=7)
        ax_a_trunc.set_xticks([0, 24, 48])
        ax_a_trunc.set_yticks([0, 24, 48])
        ax_a_trunc.tick_params(labelsize=11.0, length=3.5, labelleft=False)
        
        # Arrow 2: Trunc -> Residual
        arrow2_a = FancyArrowPatch(
            (7.28, y_a_in + 1.10), (9.10, y_a_in + 1.10),
            arrowstyle="Simple,tail_width=2.8,head_width=8.5,head_length=8.5",
            facecolor="#3b82f6", edgecolor="#1d4ed8", linewidth=0.9, zorder=4
        )
        ax_bg.add_patch(arrow2_a)
        
        box_arr2_a = FancyBboxPatch(
            (7.34, y_a_in + 1.24), 1.70, 0.70,
            boxstyle="round,pad=0.04,rounding_size=0.08",
            facecolor="#ffffff", edgecolor="#bfdbfe", linewidth=1.2, zorder=5
        )
        ax_bg.add_patch(box_arr2_a)
        ax_bg.text(
            8.19, y_a_in + 1.72, "Image",
            ha="center", va="center", fontsize=F_BOX, fontweight="bold", color="#1e40af", zorder=6
        )
        ax_bg.text(
            8.19, y_a_in + 1.43, "Residual",
            ha="center", va="center", fontsize=F_BOX, fontweight="bold", color="#1e40af", zorder=6
        )
        ax_bg.text(
            8.19, y_a_in + 0.70, "Isolates PCA\ntruncation",
            ha="center", va="center", fontsize=F_ANNOT_SEC, color="#0f172a", style="italic", linespacing=1.2, zorder=6
        )
        
        # 3. Representation Residual Image
        ax_a_res = fig.add_axes([x_col3_in / fig_w, y_a_norm, w_norm, h_norm])
        im_res_a = ax_a_res.imshow(res_trunc, cmap="bwr", vmin=-res_a_lim, vmax=res_a_lim, origin="lower")
        ax_a_res.set_title("Representation Residual", fontsize=14.0, fontweight="bold", color="#0f172a", pad=7)
        ax_a_res.set_xticks([0, 24, 48])
        ax_a_res.set_yticks([0, 24, 48])
        ax_a_res.tick_params(labelsize=11.0, length=3.5, labelleft=False)
        
        # Colorbar A (Vertical, right of residual stamp)
        cax_a = fig.add_axes([(x_col3_in + w_in + 0.16) / fig_w, y_a_norm, 0.18 / fig_w, h_norm])
        cb_a = fig.colorbar(im_res_a, cax=cax_a, orientation="vertical")
        cb_a.set_label(r"$\Delta P$ ($\times 10^{-5}$)", fontsize=13.0, fontweight="bold", color="#1e40af", labelpad=7)
        cb_a.set_ticks([-2e-5, -1e-5, 0, 1e-5, 2e-5])
        cb_a.set_ticklabels(["−2", "−1", "0", "+1", "+2"])
        cb_a.ax.tick_params(labelsize=11.0, length=3.5, color="#0f172a")
        
        # Shared intensity colorbar for Reference and Reconstructed PSFs in Row A
        # Placed at y = 6.20, height 0.12 (label at y = 5.76, Card A bottom = 5.46)
        cax_psf = fig.add_axes([x_col1_in / fig_w, 6.20 / fig_h, (x_col2_in + w_in - x_col1_in) / fig_w, 0.12 / fig_h])
        cb_psf = fig.colorbar(im_ref_a, cax=cax_psf, orientation="horizontal")
        cb_psf.set_label(r"Normalized PSF Intensity (Logarithmic scale: $5 \times 10^{-5}$ to $0.05$)", fontsize=13.5, fontweight="bold", color="#0f172a", labelpad=5)
        cb_psf.ax.tick_params(labelsize=11.5, length=3.5, color="#0f172a")
        
        # Prominent single statement card on right of Row A
        desc_box_a = FancyBboxPatch(
            (12.60, 5.65), 2.80, 3.50,
            boxstyle="round,pad=0.06,rounding_size=0.12",
            facecolor="#ffffff", edgecolor="#93c5fd", linewidth=1.5, zorder=2
        )
        ax_bg.add_patch(desc_box_a)
        
        pill_prop_a = FancyBboxPatch(
            (12.88, 8.65), 2.25, 0.34,
            boxstyle="round,pad=0.0,rounding_size=0.08",
            facecolor="#dbeafe", edgecolor="#93c5fd", linewidth=1.1, zorder=3
        )
        ax_bg.add_patch(pill_prop_a)
        ax_bg.text(
            14.00, 8.82, "PATH A KEY PROPERTY",
            ha="center", va="center", fontsize=11.5, fontweight="bold", color="#1e40af", zorder=4
        )
        
        txt_a = (
            "Coefficients\n"
            "calculated directly\n"
            "from the reference\n"
            "PSF image"
        )
        ax_bg.text(
            14.00, 7.45, txt_a,
            ha="center", va="center", fontsize=13.5, fontweight="bold", color="#0c4a6e", linespacing=1.35, zorder=3
        )
        ax_bg.text(
            14.00, 6.10, "Zero spatial\ninterpolation error",
            ha="center", va="center", fontsize=F_ANNOT_SEC, color="#0f172a", style="italic", linespacing=1.2, zorder=3
        )
        
        # =====================================================================
        # ROW B: PCA + SPATIAL INTERPOLATION
        # =====================================================================
        # 1. Reference PSF (Same reference)
        ax_b_ref = fig.add_axes([x_col1_in / fig_w, y_b_norm, w_norm, h_norm])
        ax_b_ref.imshow(ref_psf, norm=psf_norm, cmap=cmap_psf, origin="lower")
        ax_b_ref.set_title(r"Reference PSF ($P$)", fontsize=14.0, fontweight="bold", color="#0f172a", pad=7)
        ax_b_ref.set_xticks([0, 24, 48])
        ax_b_ref.set_yticks([0, 24, 48])
        ax_b_ref.tick_params(labelsize=11.0, length=3.5)
        
        # Arrow 1: Ref -> Interp
        arrow1_b = FancyArrowPatch(
            (3.02, y_b_in + 1.10), (4.85, y_b_in + 1.10),
            arrowstyle="Simple,tail_width=2.8,head_width=8.5,head_length=8.5",
            facecolor="#9333ea", edgecolor="#6b21a8", linewidth=0.9, zorder=4
        )
        ax_bg.add_patch(arrow1_b)
        
        box_arr1_b = FancyBboxPatch(
            (3.08, y_b_in + 1.24), 1.70, 0.70,
            boxstyle="round,pad=0.04,rounding_size=0.08",
            facecolor="#ffffff", edgecolor="#e9d5ff", linewidth=1.2, zorder=5
        )
        ax_bg.add_patch(box_arr1_b)
        ax_bg.text(
            3.93, y_b_in + 1.72, "Spatial",
            ha="center", va="center", fontsize=F_BOX, fontweight="bold", color="#7e22ce", zorder=6
        )
        ax_bg.text(
            3.93, y_b_in + 1.43, "Interpolation",
            ha="center", va="center", fontsize=F_BOX, fontweight="bold", color="#7e22ce", zorder=6
        )
        ax_bg.text(
            3.93, y_b_in + 0.70, "Thin-plate spline\n(RBF model)",
            ha="center", va="center", fontsize=F_ANNOT_SEC, color="#0f172a", style="italic", linespacing=1.2, zorder=6
        )
        
        # 2. Interpolated Reconstruction PSF
        ax_b_rec = fig.add_axes([x_col2_in / fig_w, y_b_norm, w_norm, h_norm])
        ax_b_rec.imshow(rec_psf, norm=psf_norm, cmap=cmap_psf, origin="lower")
        ax_b_rec.set_title(r"Interpolated PSF ($\hat{P}_K$)", fontsize=14.0, fontweight="bold", color="#0f172a", pad=7)
        ax_b_rec.set_xticks([0, 24, 48])
        ax_b_rec.set_yticks([0, 24, 48])
        ax_b_rec.tick_params(labelsize=11.0, length=3.5, labelleft=False)
        
        # Arrow 2: Interp -> Residual
        arrow2_b = FancyArrowPatch(
            (7.28, y_b_in + 1.10), (9.10, y_b_in + 1.10),
            arrowstyle="Simple,tail_width=2.8,head_width=8.5,head_length=8.5",
            facecolor="#9333ea", edgecolor="#6b21a8", linewidth=0.9, zorder=4
        )
        ax_bg.add_patch(arrow2_b)
        
        box_arr2_b = FancyBboxPatch(
            (7.34, y_b_in + 1.24), 1.70, 0.70,
            boxstyle="round,pad=0.04,rounding_size=0.08",
            facecolor="#ffffff", edgecolor="#e9d5ff", linewidth=1.2, zorder=5
        )
        ax_bg.add_patch(box_arr2_b)
        ax_bg.text(
            8.19, y_b_in + 1.72, "Image",
            ha="center", va="center", fontsize=F_BOX, fontweight="bold", color="#7e22ce", zorder=6
        )
        ax_bg.text(
            8.19, y_b_in + 1.43, "Residual",
            ha="center", va="center", fontsize=F_BOX, fontweight="bold", color="#7e22ce", zorder=6
        )
        ax_bg.text(
            8.19, y_b_in + 0.70, "Representation +\ninterpolation error",
            ha="center", va="center", fontsize=F_ANNOT_SEC, color="#0f172a", style="italic", linespacing=1.2, zorder=6
        )
        
        # 3. Total Reconstruction Residual Image
        ax_b_res = fig.add_axes([x_col3_in / fig_w, y_b_norm, w_norm, h_norm])
        im_res_b = ax_b_res.imshow(res_rec, cmap="bwr", vmin=-res_b_lim, vmax=res_b_lim, origin="lower")
        ax_b_res.set_title("Total Residual", fontsize=14.0, fontweight="bold", color="#0f172a", pad=7)
        ax_b_res.set_xticks([0, 24, 48])
        ax_b_res.set_yticks([0, 24, 48])
        ax_b_res.tick_params(labelsize=11.0, length=3.5, labelleft=False)
        
        # Colorbar B (Vertical, right of residual stamp)
        cax_b = fig.add_axes([(x_col3_in + w_in + 0.16) / fig_w, y_b_norm, 0.18 / fig_w, h_norm])
        cb_b = fig.colorbar(im_res_b, cax=cax_b, orientation="vertical")
        cb_b.set_label(r"$\Delta P$ ($\times 10^{-4}$)", fontsize=13.0, fontweight="bold", color="#7e22ce", labelpad=7)
        cb_b.set_ticks([-4e-4, -2e-4, 0, 2e-4, 4e-4])
        cb_b.set_ticklabels(["−4", "−2", "0", "+2", "+4"])
        cb_b.ax.tick_params(labelsize=11.0, length=3.5, color="#0f172a")
        
        # Clean scale annotation centered beneath the reconstruction workflow (x = 5.25)
        ax_bg.text(
            5.25, 1.68,
            "Reference and reconstructed PSFs use the same logarithmic intensity scale.",
            ha="center", va="center", fontsize=F_ANNOT_SEC, color="#0f172a", style="italic", zorder=3
        )
        
        # Prominent single statement card on right of Row B
        desc_box_b = FancyBboxPatch(
            (12.60, 1.25), 2.80, 3.50,
            boxstyle="round,pad=0.06,rounding_size=0.12",
            facecolor="#ffffff", edgecolor="#d8b4fe", linewidth=1.5, zorder=2
        )
        ax_bg.add_patch(desc_box_b)
        
        pill_prop_b = FancyBboxPatch(
            (12.88, 4.25), 2.25, 0.34,
            boxstyle="round,pad=0.0,rounding_size=0.08",
            facecolor="#f3e8ff", edgecolor="#d8b4fe", linewidth=1.1, zorder=3
        )
        ax_bg.add_patch(pill_prop_b)
        ax_bg.text(
            14.00, 4.42, "PATH B KEY PROPERTY",
            ha="center", va="center", fontsize=11.5, fontweight="bold", color="#6b21a8", zorder=4
        )
        
        txt_b = (
            "Coefficients\n"
            "interpolated from\n"
            "training stars\n"
            "across the field"
        )
        ax_bg.text(
            14.00, 3.10, txt_b,
            ha="center", va="center", fontsize=13.5, fontweight="bold", color="#581c87", linespacing=1.35, zorder=3
        )
        ax_bg.text(
            14.00, 1.75, "Includes spatial\ninterpolation error",
            ha="center", va="center", fontsize=F_ANNOT_SEC, color="#0f172a", style="italic", linespacing=1.2, zorder=3
        )
        
        # --- BOTTOM MATHEMATICAL DECOMPOSITION BANNER ---
        # Height 0.96 in: y from 0.06 to 1.02
        banner_rect = FancyBboxPatch(
            (0.35, 0.06), 15.30, 0.96,
            boxstyle="round,pad=0.0,rounding_size=0.14",
            facecolor="#f1f5f9", edgecolor="#cbd5e1", linewidth=1.4, zorder=2
        )
        ax_bg.add_patch(banner_rect)
        
        ax_bg.text(
            8.0, 0.86,
            "ORTHOGONAL DECOMPOSITION OF RECONSTRUCTION RESIDUALS",
            ha="center", va="center", fontsize=13.0, fontweight="bold", color="#0f172a", zorder=3
        )
        
        decomp_formula = r"$\hat{P}_K - P \;=\; (P_K - P) \;+\; (\hat{P}_K - P_K)$"
        ax_bg.text(
            8.0, 0.58,
            decomp_formula,
            ha="center", va="center", fontsize=17.5, fontweight="bold", color="#0f172a",
            zorder=3
        )
        
        decomp_sub = "Total Residual  =  Representation Residual  +  Interpolation Residual"
        ax_bg.text(
            8.0, 0.20,
            decomp_sub,
            ha="center", va="center", fontsize=14.5, color="#0f172a", style="italic", zorder=3
        )
        
        # Save figure
        out_path = PROJECT_ROOT / "images" / f"separating_representation_and_interpolation_errors{suffix}.png"
        fig.savefig(out_path, dpi=dpi, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        print(f"[OK] Saved {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    generate_error_decomposition_figure(test_idx=162)
