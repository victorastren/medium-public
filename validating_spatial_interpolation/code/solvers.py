"""
Geneva Spatial Interpolation Solvers
====================================
Pure NumPy / SciPy implementations of four representative spatial interpolation models:
1. PolynomialSurface: Bivariate quadratic polynomial surface (Degree 2) via least squares.
2. InverseDistanceWeighting: IDW with inverse-square distance decay (p = 2.0).
3. RadialBasisFunctions2D: Classical 2D Thin-Plate Spline (TPS) with linear drift and constraints.
4. OrdinaryKriging2D: Ordinary Kriging with a spherical semivariogram dynamically refitted
   per validation split using weighted non-linear least squares, with deterministic fallback.
"""

import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import curve_fit


class PolynomialSurface:
    """
    Bivariate polynomial surface of degree 2 (quadratic trend):
        z_hat(x, y) = beta_0 + beta_1*x + beta_2*y + beta_3*x^2 + beta_4*x*y + beta_5*y^2
    Coefficients are estimated by linear least squares (np.linalg.lstsq).
    """
    def __init__(self, x, y, z, degree=2):
        self.degree = degree
        X_design = self._build_design_matrix(x, y)
        self.beta, _, _, _ = np.linalg.lstsq(X_design, z, rcond=None)

    def _build_design_matrix(self, x, y):
        x = np.asarray(x, dtype=float).ravel()
        y = np.asarray(y, dtype=float).ravel()
        # Columns: 1, x, y, x^2, x*y, y^2
        return np.column_stack([
            np.ones_like(x),
            x,
            y,
            x**2,
            x * y,
            y**2
        ])

    def __call__(self, x_target, y_target):
        x_t = np.asarray(x_target, dtype=float)
        y_t = np.asarray(y_target, dtype=float)
        orig_shape = x_t.shape
        X_pred = self._build_design_matrix(x_t.ravel(), y_t.ravel())
        z_pred = np.dot(X_pred, self.beta)
        return z_pred.reshape(orig_shape)


class InverseDistanceWeighting:
    """
    Inverse Distance Weighting (IDW) interpolation:
        z_hat(x_0) = sum(w_i * z_i) / sum(w_i),  where w_i = 1 / d_i^p
    Uses Euclidean distance decay with power p = 2.0 and exact match handling.
    """
    def __init__(self, x, y, z, power=2.0):
        self.coords = np.column_stack([np.asarray(x, dtype=float), np.asarray(y, dtype=float)])
        self.z = np.asarray(z, dtype=float)
        self.power = float(power)

    def __call__(self, x_target, y_target):
        x_t = np.asarray(x_target, dtype=float).ravel()
        y_t = np.asarray(y_target, dtype=float).ravel()
        targets = np.column_stack([x_t, y_t])
        
        dists = cdist(targets, self.coords)
        eps = 1e-12
        is_exact = dists < eps
        
        with np.errstate(divide='ignore'):
            weights = 1.0 / (dists ** self.power)
        
        # Coincident point detection
        exact_mask = np.any(is_exact, axis=1)
        z_pred = np.zeros(len(targets), dtype=float)
        
        # For coincident points, return observed sensor value directly
        for idx in np.where(exact_mask)[0]:
            match_sensor_idx = np.argmin(dists[idx])
            z_pred[idx] = self.z[match_sensor_idx]
            
        # For non-coincident points, apply weighted average
        non_exact_indices = np.where(~exact_mask)[0]
        if len(non_exact_indices) > 0:
            w_sub = weights[non_exact_indices]
            w_sum = np.sum(w_sub, axis=1)
            z_pred[non_exact_indices] = np.sum(w_sub * self.z, axis=1) / w_sum
            
        if np.isscalar(x_target):
            return float(z_pred[0])
        return z_pred.reshape(np.asarray(x_target).shape)


class RadialBasisFunctions2D:
    """
    Classical 2D Thin-Plate Spline (TPS) with linear polynomial drift:
        z_hat(x, y) = sum_{i=1}^N w_i * phi(||x - x_i||) + beta_0 + beta_1*x + beta_2*y
    Kernel: phi(r) = r^2 * ln(r) for r > 0, phi(0) = 0.
    Linear system:
        [ Phi + lambda*I   P ] [ w ]   [ z ]
        [      P^T         0 ] [ b ] = [ 0 ]
    where P has columns [1, x, y], and constraints P^T * w = 0 are satisfied.
    """
    def __init__(self, x, y, z, smoothing=0.0):
        self.coords = np.column_stack([np.asarray(x, dtype=float), np.asarray(y, dtype=float)])
        self.z = np.asarray(z, dtype=float)
        self.smoothing = float(smoothing)
        n = len(self.z)
        
        # 1. Compute kernel matrix Phi
        dists = cdist(self.coords, self.coords)
        Phi = self._tps_kernel(dists)
        if self.smoothing > 0:
            Phi += np.eye(n) * self.smoothing
            
        # 2. Linear polynomial drift matrix P: [1, x, y]
        P = np.column_stack([np.ones(n), self.coords[:, 0], self.coords[:, 1]])
        
        # 3. Assemble full system matrix of shape (n + 3, n + 3)
        A = np.zeros((n + 3, n + 3), dtype=float)
        A[:n, :n] = Phi
        A[:n, n:] = P
        A[n:, :n] = P.T
        
        # 4. RHS vector
        rhs = np.zeros(n + 3, dtype=float)
        rhs[:n] = self.z
        
        # 5. Solve system
        solution = np.linalg.solve(A, rhs)
        self.w = solution[:n]
        self.beta = solution[n:]

    @staticmethod
    def _tps_kernel(r):
        # phi(r) = r^2 * ln(r) if r > 0, else 0
        r_safe = np.maximum(r, 1e-15)
        k = r**2 * np.log(r_safe)
        k[r == 0] = 0.0
        return k

    def __call__(self, x_target, y_target):
        x_t = np.asarray(x_target, dtype=float).ravel()
        y_t = np.asarray(y_target, dtype=float).ravel()
        targets = np.column_stack([x_t, y_t])
        
        # Distance to training observations
        dists = cdist(targets, self.coords)
        Phi_pred = self._tps_kernel(dists)
        
        # Drift matrix for targets
        P_pred = np.column_stack([np.ones(len(targets)), x_t, y_t])
        
        # Predict: Phi_pred * w + P_pred * beta
        z_pred = np.dot(Phi_pred, self.w) + np.dot(P_pred, self.beta)
        
        if np.isscalar(x_target):
            return float(z_pred[0])
        return z_pred.reshape(np.asarray(x_target).shape)


def spherical_variogram(h, c0, c, a):
    """
    Spherical semivariogram model:
        gamma(h) = 0                                       for h = 0
        gamma(h) = c0 + c * [1.5*(h/a) - 0.5*(h/a)^3]     for 0 < h <= a
        gamma(h) = c0 + c                                  for h > a
    """
    h = np.asarray(h, dtype=float)
    gamma = np.zeros_like(h)
    
    # Positive distance mask
    pos_mask = h > 0.0
    within_range = pos_mask & (h <= a)
    beyond_range = pos_mask & (h > a)
    
    h_rel = h[within_range] / a
    gamma[within_range] = c0 + c * (1.5 * h_rel - 0.5 * (h_rel ** 3))
    gamma[beyond_range] = c0 + c
    return gamma


class OrdinaryKriging2D:
    """
    2D Ordinary Kriging with a Spherical semivariogram.
    The semivariogram parameters (nugget c0, partial sill c, range a) are refitted
    from the available training observations using weighted non-linear least squares.
    """
    def __init__(self, x, y, z):
        self.coords = np.column_stack([np.asarray(x, dtype=float), np.asarray(y, dtype=float)])
        self.z = np.asarray(z, dtype=float)
        self.n_avail = len(self.z)
        
        # 1. Fit empirical variogram and estimate (c0, c, a)
        self.diagnostics = self._fit_variogram()
        self.c0 = self.diagnostics['c0']
        self.c = self.diagnostics['c']
        self.a = self.diagnostics['a']
        
        # 2. Build Ordinary Kriging system:
        # [ Gamma  1 ] [ lambda ] = [ gamma_0 ]
        # [ 1^T    0 ] [   mu   ]   [    1    ]
        dists = cdist(self.coords, self.coords)
        Gamma = spherical_variogram(dists, self.c0, self.c, self.a)
        np.fill_diagonal(Gamma, 0.0)
        
        n = self.n_avail
        self.A = np.zeros((n + 1, n + 1), dtype=float)
        self.A[:n, :n] = Gamma
        self.A[:n, n] = 1.0
        self.A[n, :n] = 1.0
        self.A[n, n] = 0.0
        
        # Solve or precompute inverse for efficiency
        self.A_inv = np.linalg.pinv(self.A)

    def _fit_variogram(self):
        """
        Estimates spherical variogram parameters from pairwise differences.
        Weights bins by pair count: sigma_k = 1 / sqrt(N_k).
        Uses deterministic fallback if curve_fit fails or hits bounds.
        """
        n = self.n_avail
        var_z = float(np.var(self.z, ddof=1)) if n > 1 else 1.0
        
        # Compute pairwise distances and squared differences
        dists = cdist(self.coords, self.coords)
        upper_idx = np.triu_indices(n, k=1)
        h_pairs = dists[upper_idx]
        gamma_pairs = 0.5 * (self.z[upper_idx[0]] - self.z[upper_idx[1]]) ** 2
        
        max_h = np.max(h_pairs) if len(h_pairs) > 0 else 1.0
        cutoff = max_h * 0.5
        n_bins = 15
        bin_edges = np.linspace(0.0, cutoff, n_bins + 1)
        
        bin_h = []
        bin_gamma = []
        bin_counts = []
        
        for k in range(n_bins):
            mask = (h_pairs > bin_edges[k]) & (h_pairs <= bin_edges[k + 1])
            count = np.sum(mask)
            if count >= 5:
                bin_h.append(np.mean(h_pairs[mask]))
                bin_gamma.append(np.mean(gamma_pairs[mask]))
                bin_counts.append(count)
                
        bin_h = np.array(bin_h)
        bin_gamma = np.array(bin_gamma)
        bin_counts = np.array(bin_counts)
        
        # Default / Fallback parameters
        fallback_params = {
            'c0': 0.10 * var_z,
            'c': 0.90 * var_z,
            'a': 0.35,
            'fallback_used': True,
            'n_bins': len(bin_h),
            'n_avail': n
        }
        
        if len(bin_h) < 4:
            return fallback_params
            
        # Optimization bounds & initial guess:
        # c0 in [0, var_z], c in [0.05*var_z, 5.0*var_z], a in [0.05, 2.50]
        bounds_lower = [0.0, 0.05 * var_z, 0.05]
        bounds_upper = [var_z, 5.00 * var_z, 2.50]
        p0 = [0.05 * var_z, 1.50 * var_z, 1.20]
        
        # Weights: sigma_k = 1 / sqrt(N_k) to minimize sum(N_k * residual^2)
        sigmas = 1.0 / np.sqrt(bin_counts)
        
        try:
            popt, _ = curve_fit(
                spherical_variogram,
                bin_h,
                bin_gamma,
                p0=p0,
                bounds=(bounds_lower, bounds_upper),
                sigma=sigmas,
                absolute_sigma=False,
                maxfev=2000
            )
            c0_fit, c_fit, a_fit = popt
            
            # Check for degenerate collapse against lower bounds (near zero sill or zero range)
            rtol = 1e-3
            near_c_lower = c_fit <= bounds_lower[1] * (1.0 + rtol)
            near_a_lower = a_fit <= bounds_lower[2] * (1.0 + rtol)
            
            if near_c_lower or near_a_lower:
                return fallback_params
                
            return {
                'c0': float(c0_fit),
                'c': float(c_fit),
                'a': float(a_fit),
                'fallback_used': False,
                'n_bins': len(bin_h),
                'n_avail': n
            }
        except Exception:
            return fallback_params

    def __call__(self, x_target, y_target):
        x_t = np.asarray(x_target, dtype=float).ravel()
        y_t = np.asarray(y_target, dtype=float).ravel()
        targets = np.column_stack([x_t, y_t])
        m = len(targets)
        n = self.n_avail
        
        # Pairwise distance between targets and training points
        dists_pred = cdist(self.coords, targets)
        gamma_pred = spherical_variogram(dists_pred, self.c0, self.c, self.a)
        
        # Build RHS B: shape (n + 1, m)
        B = np.ones((n + 1, m), dtype=float)
        B[:n, :] = gamma_pred
        
        # Solve weights: W = A_inv * B
        W = np.dot(self.A_inv, B)
        
        # Prediction: sum(w_i * z_i)
        z_pred = np.dot(self.z, W[:n, :])
        
        if np.isscalar(x_target):
            return float(z_pred[0])
        return z_pred.reshape(np.asarray(x_target).shape)
