"""
Scientific accuracy metrics for PSF reconstruction:
- Bias, RMSE, and SEM for residuals
- Pixel representation error E_rep
- Coefficient interpolation errors
- Ellipticity (e1, e2, e_mag) and size (R^2) errors
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class ResidualStats:
    bias: float
    rmse: float
    sem: float
    std: float
    n_samples: int


def compute_residual_stats(residuals: np.ndarray) -> ResidualStats:
    """
    Calculate Bias, RMSE, and Standard Error of the Mean (SEM) for residual array delta = z_hat - z.

    Parameters
    ----------
    residuals : np.ndarray
        1D array of residuals.

    Returns
    -------
    ResidualStats
    """
    res = np.asarray(residuals, dtype=np.float64).ravel()
    n = len(res)
    if n == 0:
        return ResidualStats(0.0, 0.0, 0.0, 0.0, 0)

    bias = float(np.mean(res))
    rmse = float(np.sqrt(np.mean(res ** 2)))
    ddof = 1 if n > 1 else 0
    std = float(np.std(res, ddof=ddof))
    sem = float(std / np.sqrt(n)) if n > 0 else 0.0

    return ResidualStats(bias=bias, rmse=rmse, sem=sem, std=std, n_samples=n)


def compute_representation_error(true_psfs: np.ndarray, reconstructed_psfs: np.ndarray) -> float:
    """
    Compute normalized L2 pixel representation error E_rep:
        E_rep = sqrt( sum_i ||P_i - P_i^(K)||_2^2 / sum_i ||P_i||_2^2 )
    """
    p_true = np.asarray(true_psfs, dtype=np.float64)
    p_rec = np.asarray(reconstructed_psfs, dtype=np.float64)

    diff_sq = np.sum((p_true - p_rec) ** 2)
    norm_sq = np.sum(p_true ** 2)

    if norm_sq > 0.0:
        return float(np.sqrt(diff_sq / norm_sq))
    return float(np.sqrt(diff_sq))


@dataclass
class ReconstructionMetrics:
    e1_stats: ResidualStats
    e2_stats: ResidualStats
    e_mag_stats: ResidualStats
    r2_stats: ResidualStats
    r2_rel_stats: ResidualStats
    combined_ellipticity_rmse: float
    pixel_rmse: float


def compute_reconstruction_metrics(
    true_e1: np.ndarray,
    true_e2: np.ndarray,
    true_r2: np.ndarray,
    pred_e1: np.ndarray,
    pred_e2: np.ndarray,
    pred_r2: np.ndarray,
    true_psfs: np.ndarray | None = None,
    pred_psfs: np.ndarray | None = None
) -> ReconstructionMetrics:
    """
    Evaluate full scientific reconstruction metrics across test positions.
    """
    delta_e1 = pred_e1 - true_e1
    delta_e2 = pred_e2 - true_e2
    delta_r2 = pred_r2 - true_r2

    true_e_mag = np.sqrt(true_e1 ** 2 + true_e2 ** 2)
    pred_e_mag = np.sqrt(pred_e1 ** 2 + pred_e2 ** 2)
    delta_e_mag = pred_e_mag - true_e_mag

    mean_r2 = float(np.mean(true_r2)) if len(true_r2) > 0 else 1.0
    mean_r2_safe = max(mean_r2, 1e-12)
    delta_r2_rel = delta_r2 / mean_r2_safe

    e1_stats = compute_residual_stats(delta_e1)
    e2_stats = compute_residual_stats(delta_e2)
    e_mag_stats = compute_residual_stats(delta_e_mag)
    r2_stats = compute_residual_stats(delta_r2)
    r2_rel_stats = compute_residual_stats(delta_r2_rel)

    # Combined ellipticity RMSE: sqrt(mean(delta_e1^2 + delta_e2^2))
    combined_e_rmse = float(np.sqrt(np.mean(delta_e1 ** 2 + delta_e2 ** 2)))

    # Pixel RMSE if images are provided
    if true_psfs is not None and pred_psfs is not None:
        pixel_rmse = float(np.sqrt(np.mean((true_psfs - pred_psfs) ** 2)))
    else:
        pixel_rmse = 0.0

    return ReconstructionMetrics(
        e1_stats=e1_stats,
        e2_stats=e2_stats,
        e_mag_stats=e_mag_stats,
        r2_stats=r2_stats,
        r2_rel_stats=r2_rel_stats,
        combined_ellipticity_rmse=combined_e_rmse,
        pixel_rmse=pixel_rmse
    )
