"""
Classical spatial interpolation methods for PCA coefficient fields:
1. Polynomial Regression (degrees 1 through 4)
2. Inverse-Distance Weighting (IDW)
3. Radial Basis Functions (Thin-Plate Spline with linear polynomial drift)
"""

import numpy as np
from scipy.spatial.distance import cdist
from interpolation.base import SpatialInterpolator


class PolynomialInterpolator(SpatialInterpolator):
    """
    Bivariate polynomial regression of degree 1 to 4:
        a_k(x, y) = sum_{i+j <= degree} beta_{ij, k} * x^i * y^j
    Solved simultaneously for all K PCA components via linear least squares.
    """

    def __init__(self, degree: int = 2):
        if not 1 <= degree <= 4:
            raise ValueError(f"Degree must be in 1..4, got {degree}")
        self.degree = int(degree)
        self.beta: np.ndarray | None = None  # Shape (n_terms, K)

    def _build_design_matrix(self, positions: np.ndarray) -> np.ndarray:
        x = positions[:, 0]
        y = positions[:, 1]
        cols = []
        for d in range(self.degree + 1):
            for i in range(d + 1):
                j = d - i
                cols.append((x ** i) * (y ** j))
        return np.column_stack(cols)

    def fit(self, positions: np.ndarray, coefficients: np.ndarray) -> "PolynomialInterpolator":
        pos = np.asarray(positions, dtype=np.float64)
        coeffs = np.asarray(coefficients, dtype=np.float64)
        X_design = self._build_design_matrix(pos)
        self.beta, _, _, _ = np.linalg.lstsq(X_design, coeffs, rcond=None)
        return self

    def predict(self, positions: np.ndarray) -> np.ndarray:
        if self.beta is None:
            raise RuntimeError("Model must be fitted before predict.")
        pos = np.asarray(positions, dtype=np.float64)
        X_pred = self._build_design_matrix(pos)
        return np.dot(X_pred, self.beta)


class IDWInterpolator(SpatialInterpolator):
    """
    Inverse-Distance Weighting (IDW) spatial interpolator:
        a_k(x_0) = sum_i [w_i * a_{ik}] / sum_i [w_i],  where w_i = 1 / d_i^p
    Includes exact coincident-point matching.
    """

    def __init__(self, power: float = 2.0, eps: float = 1e-12):
        self.power = float(power)
        self.eps = float(eps)
        self.coords: np.ndarray | None = None
        self.coeffs: np.ndarray | None = None

    def fit(self, positions: np.ndarray, coefficients: np.ndarray) -> "IDWInterpolator":
        self.coords = np.asarray(positions, dtype=np.float64)
        self.coeffs = np.asarray(coefficients, dtype=np.float64)
        return self

    def predict(self, positions: np.ndarray) -> np.ndarray:
        if self.coords is None or self.coeffs is None:
            raise RuntimeError("Model must be fitted before predict.")

        targets = np.asarray(positions, dtype=np.float64)
        m = len(targets)
        k = self.coeffs.shape[1]
        out = np.zeros((m, k), dtype=np.float64)

        dists = cdist(targets, self.coords)
        exact_mask = dists < self.eps

        for i in range(m):
            if np.any(exact_mask[i]):
                nearest_idx = np.argmin(dists[i])
                out[i] = self.coeffs[nearest_idx]
            else:
                w = 1.0 / (dists[i] ** self.power)
                w_sum = np.sum(w)
                out[i] = np.sum(w[:, None] * self.coeffs, axis=0) / w_sum

        return out


class RBFInterpolator(SpatialInterpolator):
    """
    2D Thin-Plate Spline (TPS) with linear polynomial drift:
        a_k(x, y) = sum_{i=1}^N w_{ik} * phi(||x - x_i||) + b_{0k} + b_{1k}*x + b_{2k}*y
    Kernel: phi(r) = r^2 * ln(r) for r > 0, phi(0) = 0.
    Assembles and solves the system matrix once across all K components.
    """

    def __init__(self, smoothing: float = 1e-6):
        self.smoothing = float(smoothing)
        self.coords: np.ndarray | None = None
        self.w: np.ndarray | None = None      # Shape (N, K)
        self.beta: np.ndarray | None = None   # Shape (3, K)

    @staticmethod
    def _tps_kernel(r: np.ndarray) -> np.ndarray:
        r_safe = np.maximum(r, 1e-15)
        k = (r ** 2) * np.log(r_safe)
        k[r == 0.0] = 0.0
        return k

    def fit(self, positions: np.ndarray, coefficients: np.ndarray) -> "RBFInterpolator":
        self.coords = np.asarray(positions, dtype=np.float64)
        coeffs = np.asarray(coefficients, dtype=np.float64)
        n, k_comp = coeffs.shape

        # 1. Kernel matrix Phi
        dists = cdist(self.coords, self.coords)
        Phi = self._tps_kernel(dists)
        if self.smoothing > 0.0:
            Phi += np.eye(n) * self.smoothing

        # 2. Linear drift matrix P: [1, x, y]
        P = np.column_stack([np.ones(n), self.coords[:, 0], self.coords[:, 1]])

        # 3. Assemble full (n + 3, n + 3) system matrix
        A = np.zeros((n + 3, n + 3), dtype=np.float64)
        A[:n, :n] = Phi
        A[:n, n:] = P
        A[n:, :n] = P.T

        # 4. Multi-column RHS: shape (n + 3, K)
        rhs = np.zeros((n + 3, k_comp), dtype=np.float64)
        rhs[:n, :] = coeffs

        # 5. Solve system
        try:
            solution = np.linalg.solve(A, rhs)
        except np.linalg.LinAlgError:
            solution, _, _, _ = np.linalg.lstsq(A, rhs, rcond=None)

        self.w = solution[:n, :]
        self.beta = solution[n:, :]
        return self

    def predict(self, positions: np.ndarray) -> np.ndarray:
        if self.coords is None or self.w is None or self.beta is None:
            raise RuntimeError("Model must be fitted before predict.")

        targets = np.asarray(positions, dtype=np.float64)
        dists = cdist(targets, self.coords)
        Phi_pred = self._tps_kernel(dists)
        P_pred = np.column_stack([np.ones(len(targets)), targets[:, 0], targets[:, 1]])

        return np.dot(Phi_pred, self.w) + np.dot(P_pred, self.beta)
