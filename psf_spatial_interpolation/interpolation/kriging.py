"""
Ordinary and Universal Kriging spatial interpolators for multi-component PCA coefficient fields.

Supports:
- Ordinary Kriging (OK): unknown constant mean m(r) = mu
- Universal Kriging (UK): polynomial spatial drift m(r) = sum_l beta_l f_l(r)
  - Linear drift: m(x, y) = beta_0 + beta_1 * x + beta_2 * y
  - Quadratic drift: m(x, y) = beta_0 + beta_1 * x + beta_2 * y + beta_3 * x^2 + beta_4 * x*y + beta_5 * y^2
"""

import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import curve_fit
from interpolation.base import SpatialInterpolator


def spherical_variogram(h: np.ndarray, c0: float, c: float, a: float) -> np.ndarray:
    """
    Spherical semivariogram model:
        gamma(h) = 0                                       for h = 0
        gamma(h) = c0 + c * (1.5 * (h/a) - 0.5 * (h/a)^3)  for 0 < h <= a
        gamma(h) = c0 + c                                  for h > a
    """
    h_arr = np.asarray(h, dtype=np.float64)
    gamma = np.zeros_like(h_arr)

    pos_mask = h_arr > 0.0
    within_range = pos_mask & (h_arr <= a)
    beyond_range = pos_mask & (h_arr > a)

    h_rel = h_arr[within_range] / a
    gamma[within_range] = c0 + c * (1.5 * h_rel - 0.5 * (h_rel ** 3))
    gamma[beyond_range] = c0 + c
    return gamma


def build_trend_matrix(coords: np.ndarray, trend: str = "constant") -> np.ndarray:
    """
    Construct spatial drift matrix F of shape (N, P).

    Parameters
    ----------
    coords : np.ndarray
        Array of (x, y) coordinates of shape (N, 2).
    trend : str
        'constant' (P=1), 'linear' (P=3), or 'quadratic' (P=6).

    Returns
    -------
    np.ndarray
        Drift design matrix F of shape (N, P).
    """
    x = coords[:, 0]
    y = coords[:, 1]
    n = len(coords)

    if trend == "constant":
        return np.ones((n, 1), dtype=np.float64)
    elif trend == "linear":
        return np.column_stack([np.ones(n, dtype=np.float64), x, y])
    elif trend == "quadratic":
        return np.column_stack([
            np.ones(n, dtype=np.float64),
            x, y,
            x ** 2, x * y, y ** 2
        ])
    else:
        raise ValueError(f"Unknown trend '{trend}'. Expected 'constant', 'linear', or 'quadratic'.")


class KrigingInterpolator(SpatialInterpolator):
    """
    Multi-component Kriging interpolator with customizable spatial trend (drift).

    Parameters
    ----------
    trend : str
        Spatial trend specification: 'constant' (Ordinary Kriging), 'linear', or 'quadratic' (Universal Kriging).
    variogram_range_init : float
        Initial guess for variogram spatial correlation range (default 0.35).
    """

    def __init__(self, trend: str = "constant", variogram_range_init: float = 0.35):
        self.trend = trend.lower()
        self.variogram_range_init = float(variogram_range_init)
        self.coords: np.ndarray | None = None
        self.coeffs: np.ndarray | None = None
        self.c0: float = 0.0
        self.c: float = 1.0
        self.a: float = self.variogram_range_init
        self.A_inv: np.ndarray | None = None
        self.P: int = 1

    def _fit_variogram(self, coords: np.ndarray, z: np.ndarray) -> tuple[float, float, float]:
        """Fit empirical variogram from training pairwise differences on residuals."""
        n = len(z)
        var_z = float(np.var(z, ddof=1)) if n > 1 else 1.0

        # If residual variance is negligible, the trend accounts for all variation
        if var_z < 1e-12:
            return 0.0, 1.0, self.variogram_range_init

        dists = cdist(coords, coords)
        upper_idx = np.triu_indices(n, k=1)
        h_pairs = dists[upper_idx]
        gamma_pairs = 0.5 * (z[upper_idx[0]] - z[upper_idx[1]]) ** 2

        max_h = np.max(h_pairs) if len(h_pairs) > 0 else 1.0
        cutoff = max_h * 0.5
        n_bins = 15
        bin_edges = np.linspace(0.0, cutoff, n_bins + 1)

        bin_h, bin_gamma, bin_counts = [], [], []
        for k in range(n_bins):
            mask = (h_pairs > bin_edges[k]) & (h_pairs <= bin_edges[k + 1])
            count = np.sum(mask)
            if count >= 5:
                bin_h.append(np.mean(h_pairs[mask]))
                bin_gamma.append(np.mean(gamma_pairs[mask]))
                bin_counts.append(count)

        fallback = (0.01 * var_z, max(var_z, 1e-6), self.variogram_range_init)
        if len(bin_h) < 4:
            return fallback

        bin_h_arr = np.array(bin_h)
        bin_gamma_arr = np.array(bin_gamma)
        sigmas = 1.0 / np.sqrt(np.array(bin_counts))

        bounds_lower = [0.0, 0.01 * var_z, 0.05]
        bounds_upper = [var_z, 5.0 * var_z, 2.5]
        p0 = [0.05 * var_z, max(var_z, 1e-5), self.variogram_range_init]

        try:
            popt, _ = curve_fit(
                spherical_variogram, bin_h_arr, bin_gamma_arr,
                p0=p0, bounds=(bounds_lower, bounds_upper),
                sigma=sigmas, absolute_sigma=False, maxfev=2000
            )
            return float(popt[0]), float(popt[1]), float(popt[2])
        except Exception:
            return fallback

    def fit(self, positions: np.ndarray, coefficients: np.ndarray) -> "KrigingInterpolator":
        self.coords = np.asarray(positions, dtype=np.float64)
        self.coeffs = np.asarray(coefficients, dtype=np.float64)
        n = len(self.coords)

        # 1. Build trend design matrix F of shape (n, P)
        F = build_trend_matrix(self.coords, self.trend)
        self.P = F.shape[1]

        # 2. Detrend dominant component to estimate residual variogram
        z0 = self.coeffs[:, 0]
        beta = np.linalg.lstsq(F, z0, rcond=None)[0]
        res0 = z0 - F @ beta
        self.c0, self.c, self.a = self._fit_variogram(self.coords, res0)

        # 3. Assemble (n + P, n + P) Kriging system matrix:
        # [ Gamma   F   ]
        # [ F^T     0   ]
        dists = cdist(self.coords, self.coords)
        Gamma = spherical_variogram(dists, self.c0, self.c, self.a)
        np.fill_diagonal(Gamma, 0.0)

        A = np.zeros((n + self.P, n + self.P), dtype=np.float64)
        A[:n, :n] = Gamma
        A[:n, n:] = F
        A[n:, :n] = F.T
        A[n:, n:] = 0.0

        # Pseudo-inverse for numerically stable solution
        self.A_inv = np.linalg.pinv(A)
        return self

    def predict(self, positions: np.ndarray) -> np.ndarray:
        if self.coords is None or self.coeffs is None or self.A_inv is None:
            raise RuntimeError("Model must be fitted before predict.")

        targets = np.asarray(positions, dtype=np.float64)
        m = len(targets)
        n = len(self.coords)

        # 1. Distance and semivariogram between training points and query targets
        dists_pred = cdist(self.coords, targets)
        gamma_pred = spherical_variogram(dists_pred, self.c0, self.c, self.a)

        # 2. Query drift matrix F0 of shape (m, P)
        F0 = build_trend_matrix(targets, self.trend)

        # 3. Assemble RHS matrix B of shape (n + P, m):
        # [ gamma_pred ]
        # [ F0^T       ]
        B = np.zeros((n + self.P, m), dtype=np.float64)
        B[:n, :] = gamma_pred
        B[n:, :] = F0.T

        # 4. Kriging weights W = A_inv * B of shape (n + P, m)
        W = np.dot(self.A_inv, B)

        # 5. Multi-component prediction: pred = coeffs^T * W[:n, :] -> shape (K, m) -> transpose to (m, K)
        return np.dot(self.coeffs.T, W[:n, :]).T


class OrdinaryKrigingInterpolator(KrigingInterpolator):
    """
    Ordinary Kriging (OK) spatial interpolator assuming an unknown constant local mean.
    """

    def __init__(self, variogram_range_init: float = 0.35):
        super().__init__(trend="constant", variogram_range_init=variogram_range_init)


class UniversalKrigingInterpolator(KrigingInterpolator):
    """
    Universal Kriging (UK) spatial interpolator modeling a polynomial spatial trend (linear or quadratic).
    """

    def __init__(self, trend: str = "quadratic", variogram_range_init: float = 0.35):
        super().__init__(trend=trend, variogram_range_init=variogram_range_init)
