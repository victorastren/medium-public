"""
Measurement of PSF weighted quadrupole moments, ellipticity, and size.

Implements the GREAT10 Star Challenge measurement convention:
    Q_ij = sum_x [W(x) * P(x) * (x_i - x_bar_i) * (x_j - x_bar_j)] / sum_x [W(x) * P(x)]
where W(x) is a circular Gaussian window of fixed width sigma_w.

Derived quantities:
    R^2 = Q_11 + Q_22
    e_1 = (Q_11 - Q_22) / (Q_11 + Q_22)
    e_2 = (2 * Q_12) / (Q_11 + Q_22)
    e   = sqrt(e_1^2 + e_2^2)
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class PSFMoments:
    x_bar: float
    y_bar: float
    q11: float
    q22: float
    q12: float
    r2: float
    e1: float
    e2: float
    e_mag: float
    flux_weighted: float


def compute_weighted_moments(
    psf_image: np.ndarray,
    sigma_w: float | None = 3.5,
    fixed_center: tuple[float, float] | None = None,
    max_iter: int = 15,
    tol: float = 1e-4
) -> PSFMoments:
    """
    Compute quadrupole moments, size, and ellipticity for a PSF image.

    Parameters
    ----------
    psf_image : np.ndarray
        2D array of shape (H, W).
    sigma_w : float | None
        Standard deviation of circular Gaussian weighting window (in detector pixels).
        If None, computes unweighted central moments (W(x) = 1).
    fixed_center : tuple of (x0, y0), optional
        If provided, moments are measured relative to this fixed reference point.
        If None, iteratively computes the centroid.
    max_iter : int
        Maximum centroid refinement iterations.
    tol : float
        Centroid convergence tolerance in pixels.

    Returns
    -------
    PSFMoments
        Computed moments, size, and ellipticity parameters.
    """
    img = np.asarray(psf_image, dtype=np.float64)
    h, w = img.shape
    y_indices, x_indices = np.indices((h, w), dtype=np.float64)

    # Initial centroid estimate
    if fixed_center is not None:
        xc, yc = float(fixed_center[0]), float(fixed_center[1])
    else:
        # Initial guess at nominal image center
        xc, yc = (w - 1.0) / 2.0, (h - 1.0) / 2.0
        for _ in range(max_iter):
            dx = x_indices - xc
            dy = y_indices - yc
            r_sq = dx**2 + dy**2
            if sigma_w is not None:
                weight = np.exp(-0.5 * r_sq / (sigma_w**2))
            else:
                weight = np.ones_like(r_sq)
            weighted_img = weight * img
            denom = np.sum(weighted_img)
            if denom <= 0.0:
                break
            new_xc = np.sum(weighted_img * x_indices) / denom
            new_yc = np.sum(weighted_img * y_indices) / denom

            shift = np.sqrt((new_xc - xc)**2 + (new_yc - yc)**2)
            xc, yc = new_xc, new_yc
            if shift < tol:
                break

    # Compute second moments
    dx = x_indices - xc
    dy = y_indices - yc
    r_sq = dx**2 + dy**2
    if sigma_w is not None:
        weight = np.exp(-0.5 * r_sq / (sigma_w**2))
    else:
        weight = np.ones_like(r_sq)
    weighted_img = weight * img

    denom = np.sum(weighted_img)
    if denom <= 0.0:
        return PSFMoments(
            x_bar=xc, y_bar=yc,
            q11=0.0, q22=0.0, q12=0.0,
            r2=0.0, e1=0.0, e2=0.0, e_mag=0.0,
            flux_weighted=0.0
        )

    q11 = float(np.sum(weighted_img * (dx**2)) / denom)
    q22 = float(np.sum(weighted_img * (dy**2)) / denom)
    q12 = float(np.sum(weighted_img * (dx * dy)) / denom)

    trace = q11 + q22
    if trace > 1e-12:
        e1 = float((q11 - q22) / trace)
        e2 = float((2.0 * q12) / trace)
        e_mag = float(np.sqrt(e1**2 + e2**2))
    else:
        e1, e2, e_mag = 0.0, 0.0, 0.0

    return PSFMoments(
        x_bar=float(xc),
        y_bar=float(yc),
        q11=q11,
        q22=q22,
        q12=q12,
        r2=float(trace),
        e1=e1,
        e2=e2,
        e_mag=e_mag,
        flux_weighted=float(denom)
    )


def measure_psf_batch(
    psf_stack: np.ndarray,
    sigma_w: float | None = 3.5,
    fixed_center: tuple[float, float] | None = None
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Measure ellipticity components (e1, e2) and squared size R^2 for a batch of PSFs.

    Parameters
    ----------
    psf_stack : np.ndarray
        Array of shape (N, H, W).
    sigma_w : float
        Gaussian weight window scale.
    fixed_center : tuple of (x0, y0), optional
        Fixed reference center for all images.

    Returns
    -------
    tuple of (e1_arr, e2_arr, r2_arr)
        1D arrays of shape (N,) containing the measured parameters.
    """
    n = len(psf_stack)
    e1_arr = np.zeros(n, dtype=np.float64)
    e2_arr = np.zeros(n, dtype=np.float64)
    r2_arr = np.zeros(n, dtype=np.float64)

    for i in range(n):
        m = compute_weighted_moments(psf_stack[i], sigma_w=sigma_w, fixed_center=fixed_center)
        e1_arr[i] = m.e1
        e2_arr[i] = m.e2
        r2_arr[i] = m.r2

    return e1_arr, e2_arr, r2_arr
