"""
Principal Component Analysis (PCA) representation for astronomical PSF images.

Learns the empirical mean PSF and orthogonal eigenPSF basis vectors from training stars:
    P(x; r) = mu(x) + sum_{k=1}^K a_k(r) * phi_k(x)
"""

import numpy as np


class PSFRepresentation:
    """
    Data-driven PCA representation for PSF image stamps.

    Parameters
    ----------
    n_components_max : int
        Maximum number of principal components to extract and retain (default 20).
    """

    def __init__(self, n_components_max: int = 20):
        self.n_components_max = int(n_components_max)
        self.mean_vector: np.ndarray | None = None
        self.components: np.ndarray | None = None          # Shape (K_max, P)
        self.singular_values: np.ndarray | None = None
        self.explained_variance: np.ndarray | None = None
        self.explained_variance_ratio: np.ndarray | None = None
        self.image_shape: tuple[int, int] | None = None

    def _flatten_psfs(self, psfs: np.ndarray) -> np.ndarray:
        """Convert input array of shape (N, H, W) or (N, P) into float64 (N, P)."""
        arr = np.asarray(psfs, dtype=np.float64)
        if arr.ndim == 3:
            self.image_shape = (arr.shape[1], arr.shape[2])
            return arr.reshape(arr.shape[0], -1)
        elif arr.ndim == 2:
            if self.image_shape is None:
                side = int(np.round(np.sqrt(arr.shape[1])))
                self.image_shape = (side, side)
            return arr
        else:
            raise ValueError(f"Expected 2D or 3D array of PSFs, got shape {arr.shape}")

    def fit(self, psfs: np.ndarray) -> "PSFRepresentation":
        """
        Fit PCA basis using training PSF images.

        Parameters
        ----------
        psfs : np.ndarray
            Training PSFs of shape (N_train, H, W) or (N_train, H*W).

        Returns
        -------
        self
        """
        X = self._flatten_psfs(psfs)
        n_samples, n_features = X.shape

        # 1. Compute empirical mean PSF
        self.mean_vector = np.mean(X, axis=0)
        X_centered = X - self.mean_vector

        # 2. Economy SVD on centered matrix: X_centered = U * S * Vt
        # Using full_matrices=False: Vt has shape (min(N, P), P)
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)

        # 3. Retain up to n_components_max components
        k = min(self.n_components_max, len(S))
        self.components = Vt[:k, :]
        self.singular_values = S[:k]

        # Explained variance
        ddof = max(n_samples - 1, 1)
        total_var = np.sum(S ** 2) / ddof
        comp_var = (S[:k] ** 2) / ddof
        self.explained_variance = comp_var
        if total_var > 0.0:
            self.explained_variance_ratio = comp_var / (np.sum(S ** 2) / ddof)
        else:
            self.explained_variance_ratio = np.zeros(k, dtype=np.float64)

        return self

    def transform(self, psfs: np.ndarray, n_components: int | None = None) -> np.ndarray:
        """
        Project PSFs into the PCA coordinate space to obtain coefficient vectors.

        Parameters
        ----------
        psfs : np.ndarray
            Images of shape (N, H, W) or (N, H*W).
        n_components : int, optional
            Number of components K to use (must be <= fitted components).

        Returns
        -------
        np.ndarray
            Coefficient matrix of shape (N, K).
        """
        if self.mean_vector is None or self.components is None:
            raise RuntimeError("PSFRepresentation must be fitted before calling transform.")

        X = self._flatten_psfs(psfs)
        X_centered = X - self.mean_vector

        k = self.components.shape[0] if n_components is None else min(n_components, self.components.shape[0])
        basis_k = self.components[:k, :]  # Shape (K, P)

        # A = X_centered * basis_k^T -> Shape (N, K)
        return np.dot(X_centered, basis_k.T)

    def inverse_transform(self, coefficients: np.ndarray, n_components: int | None = None) -> np.ndarray:
        """
        Reconstruct PSF image vectors from coefficient matrix.

        Parameters
        ----------
        coefficients : np.ndarray
            Matrix of shape (N, K).
        n_components : int, optional
            Number of components used.

        Returns
        -------
        np.ndarray
            Reconstructed flattened PSFs of shape (N, P).
        """
        if self.mean_vector is None or self.components is None:
            raise RuntimeError("PSFRepresentation must be fitted before calling inverse_transform.")

        coeffs = np.asarray(coefficients, dtype=np.float64)
        k = coeffs.shape[1] if n_components is None else min(n_components, coeffs.shape[1])
        basis_k = self.components[:k, :]

        # X_rec = coeffs[:, :k] * basis_k + mean_vector
        return np.dot(coeffs[:, :k], basis_k) + self.mean_vector

    def reconstruct(self, psfs: np.ndarray, n_components: int | None = None,
                    as_images: bool = True) -> np.ndarray:
        """
        Project and reconstruct PSFs directly using K components.

        Parameters
        ----------
        psfs : np.ndarray
            Images of shape (N, H, W) or (N, P).
        n_components : int, optional
            Number of components K.
        as_images : bool
            If True, reshapes output back to 2D image stamps (N, H, W).

        Returns
        -------
        np.ndarray
            Reconstructed images of shape (N, H, W) or (N, P).
        """
        coeffs = self.transform(psfs, n_components=n_components)
        x_rec = self.inverse_transform(coeffs, n_components=n_components)

        if as_images and self.image_shape is not None:
            return x_rec.reshape(-1, self.image_shape[0], self.image_shape[1])
        return x_rec

    def get_mean_image(self) -> np.ndarray:
        """Return the mean PSF as a 2D image."""
        if self.mean_vector is None:
            raise RuntimeError("PSFRepresentation must be fitted first.")
        if self.image_shape is not None:
            return self.mean_vector.reshape(self.image_shape)
        return self.mean_vector

    def get_eigen_psfs(self, n_components: int | None = None) -> np.ndarray:
        """Return the first K eigenPSFs as a 3D array of shape (K, H, W)."""
        if self.components is None or self.image_shape is None:
            raise RuntimeError("PSFRepresentation must be fitted first.")
        k = self.components.shape[0] if n_components is None else min(n_components, self.components.shape[0])
        return self.components[:k, :].reshape(k, self.image_shape[0], self.image_shape[1])
