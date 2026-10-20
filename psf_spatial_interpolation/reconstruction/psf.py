"""
PSF reconstruction module from predicted PCA coefficients.

Supports:
1. Raw linear PCA reconstruction: P_hat = mu + sum_k a_k * phi_k
2. Physically adjusted reconstruction: non-negative thresholding and flux re-normalization.
"""

import numpy as np
from representation.pca import PSFRepresentation


def reconstruct_psfs_from_coefficients(
    coefficients: np.ndarray,
    pca: PSFRepresentation,
    physical_adjustment: bool = False
) -> np.ndarray:
    """
    Reconstruct 2D PSF images from a predicted coefficient matrix.

    Parameters
    ----------
    coefficients : np.ndarray
        Array of shape (N, K).
    pca : PSFRepresentation
        Fitted PCA representation basis.
    physical_adjustment : bool
        If True, clips negative pixel values to zero and renormalizes each image to unit flux.

    Returns
    -------
    np.ndarray
        Reconstructed PSF images of shape (N, H, W).
    """
    # 1. Linear PCA inverse transform: (N, H*W)
    raw_flat = pca.inverse_transform(coefficients)

    # 2. Reshape to (N, H, W)
    if pca.image_shape is not None:
        h, w = pca.image_shape
    else:
        side = int(np.round(np.sqrt(raw_flat.shape[1])))
        h, w = side, side

    reconstructed = raw_flat.reshape(-1, h, w)

    if not physical_adjustment:
        return reconstructed

    # 3. Apply physical constraints
    adjusted = np.maximum(reconstructed, 0.0)
    # Sum over spatial axes (1, 2)
    fluxes = np.sum(adjusted, axis=(1, 2), keepdims=True)

    # Renormalize images with positive flux
    valid_mask = fluxes > 1e-12
    adjusted = np.where(valid_mask, adjusted / np.maximum(fluxes, 1e-12), adjusted)

    return adjusted
