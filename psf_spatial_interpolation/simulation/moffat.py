"""
Seeing-dominated elliptical Moffat PSF generator with subpixel integration.

Profile:
    P(r) = C * [1 + (r / alpha)^2]^(-beta)
where:
    alpha = FWHM / (2 * sqrt(2^(1 / beta) - 1))
and the transformed elliptical squared distance is:
    r^2 = (1 / (1 - e^2)) * [(1 - e1) * dx^2 - 2 * e2 * dx * dy + (1 + e1) * dy^2]
with e^2 = e1^2 + e2^2 < 1.
"""

import numpy as np


def compute_moffat_alpha(fwhm: float, beta: float) -> float:
    """Calculate Moffat scale parameter alpha from FWHM and power index beta."""
    return float(fwhm / (2.0 * np.sqrt(2.0 ** (1.0 / beta) - 1.0)))


def generate_moffat_psf(fwhm: float = 3.5, beta: float = 3.5,
                        e1: float = 0.0, e2: float = 0.0,
                        c1: float = 0.0, c2: float = 0.0,
                        stamp_size: int = 48, subpixel_factor: int = 4,
                        center: tuple[float, float] | None = None) -> np.ndarray:
    """
    Generate a 2D elliptical Moffat PSF integrated over subpixel detector grid.
    Optionally includes optical coma (c1, c2) as an asymmetric coordinate warp.

    Parameters
    ----------
    fwhm : float
        Full width at half maximum in detector pixels.
    beta : float
        Moffat power index (baseline 3.5).
    e1, e2 : float
        Ellipticity components. Magnitude sqrt(e1^2 + e2^2) must be < 1.
    c1, c2 : float
        Optical coma components (default 0.0).
    stamp_size : int
        PSF stamp dimension (default 48 x 48).
    subpixel_factor : int
        Subpixel oversampling factor (default 4, creating a 192 x 192 high-res grid).
    center : tuple of (x0, y0), optional
        PSF center in 0-indexed pixel coordinates. Defaults to (stamp_size - 1) / 2.

    Returns
    -------
    np.ndarray
        Normalized 2D float64 array of shape (stamp_size, stamp_size) with unit total flux.
    """
    if center is None:
        x0 = (stamp_size - 1) / 2.0
        y0 = (stamp_size - 1) / 2.0
    else:
        x0, y0 = float(center[0]), float(center[1])

    # Guard against unphysical ellipticity
    e_sq = e1 ** 2 + e2 ** 2
    if e_sq >= 0.95:
        scale = np.sqrt(0.95 / e_sq)
        e1 *= scale
        e2 *= scale
        e_sq = 0.95

    alpha = compute_moffat_alpha(fwhm, beta)
    denom = max(1.0 - e_sq, 1e-4)

    # Subpixel grid coordinates
    n_sub = stamp_size * subpixel_factor
    sub_offset = (np.arange(subpixel_factor) + 0.5) / subpixel_factor - 0.5

    # Compute high-resolution subpixel 1D coordinate vectors
    pixel_centers = np.arange(stamp_size, dtype=np.float64)
    x_sub = (pixel_centers[:, None] + sub_offset[None, :]).ravel()
    y_sub = (pixel_centers[:, None] + sub_offset[None, :]).ravel()

    dx = x_sub - x0
    dy = y_sub - y0

    # 2D coordinate meshgrid for high-res grid
    DX, DY = np.meshgrid(dx, dy, indexing="xy")

    # Apply optical coma coordinate warp if present
    if c1 != 0.0 or c2 != 0.0:
        r_sq_sub = DX ** 2 + DY ** 2
        warp_scale = 6.0 * alpha
        DX = DX - c1 * r_sq_sub / warp_scale
        DY = DY - c2 * r_sq_sub / warp_scale

    # Quadratic elliptical distance:
    # r^2 = [(1 - e1)*dx^2 - 2*e2*dx*dy + (1 + e1)*dy^2] / (1 - e^2)
    r_sq = ((1.0 - e1) * (DX ** 2) - 2.0 * e2 * DX * DY + (1.0 + e1) * (DY ** 2)) / denom
    r_sq = np.maximum(r_sq, 0.0)

    # Moffat intensity
    sub_intensity = (1.0 + r_sq / (alpha ** 2)) ** (-beta)

    # Integrate / bin 4x4 subpixels into detector pixels
    # Reshape (stamp_size, subpixel_factor, stamp_size, subpixel_factor) -> sum over subpixel axes
    binned = sub_intensity.reshape(
        stamp_size, subpixel_factor, stamp_size, subpixel_factor
    ).mean(axis=(1, 3))

    # Normalize to unit total flux
    total_flux = np.sum(binned)
    if total_flux > 0.0:
        psf = binned / total_flux
    else:
        psf = np.zeros((stamp_size, stamp_size), dtype=np.float64)
        psf[stamp_size // 2, stamp_size // 2] = 1.0

    return psf.astype(np.float64)
