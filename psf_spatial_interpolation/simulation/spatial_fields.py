"""
Spatial field generators for PSF parameter variations across the focal plane.
Supports:
1. Low-order smooth bivariate polynomial fields.
2. Stationary correlated Gaussian/Matérn random fields with configurable correlation length.
"""

import numpy as np
from scipy.interpolate import RegularGridInterpolator


class PolynomialField2D:
    """
    Smooth bivariate polynomial field c(x, y) defined over normalized coordinates [0, 1]^2:
        c(x, y) = sum_{i+j <= degree} beta_{i, j} * x^i * y^j
    """

    def __init__(self, degree: int = 2, coefficients: dict[tuple[int, int], float] | None = None,
                 seed: int | None = None, amplitude: float = 1.0, mean: float = 0.0):
        self.degree = degree
        self.coefficients: dict[tuple[int, int], float] = {}

        if coefficients is not None:
            self.coefficients = dict(coefficients)
        elif seed is not None:
            rng = np.random.default_rng(seed)
            # Generate coefficients with higher order terms decaying in amplitude
            self.coefficients[(0, 0)] = mean
            for d in range(1, degree + 1):
                decay = amplitude / (d ** 1.5)
                for i in range(d + 1):
                    j = d - i
                    self.coefficients[(i, j)] = float(rng.normal(0.0, decay))
        else:
            self.coefficients[(0, 0)] = mean

    def evaluate(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Evaluate the polynomial field at coordinates (x, y)."""
        x_arr = np.asarray(x, dtype=np.float64)
        y_arr = np.asarray(y, dtype=np.float64)
        result = np.zeros_like(x_arr, dtype=np.float64)

        for (i, j), coeff in self.coefficients.items():
            if coeff != 0.0:
                result += coeff * (x_arr ** i) * (y_arr ** j)

        return result

    def __call__(self, positions: np.ndarray) -> np.ndarray:
        """Evaluate field at positions array of shape (N, 2)."""
        pos = np.asarray(positions, dtype=np.float64)
        return self.evaluate(pos[:, 0], pos[:, 1])


class CorrelatedRandomField2D:
    """
    2D stationary Gaussian random field on [0, 1]^2 with Matérn/Gaussian covariance:
    Generated via spectral synthesis on a fine regular grid and evaluated at arbitrary
    coordinates using smooth spline interpolation.
    """

    def __init__(self, correlation_length: float = 0.2, variance: float = 1.0,
                 nu: float = 1.5, grid_size: int = 256, seed: int = 42):
        self.correlation_length = max(float(correlation_length), 1e-4)
        self.variance = float(variance)
        self.nu = float(nu)  # nu=1.5 or nu=inf (Gaussian)
        self.grid_size = grid_size
        self.seed = seed

        self._grid_coords = np.linspace(0.0, 1.0, grid_size)
        self._field_grid = self._synthesize_field()
        self._interpolator = RegularGridInterpolator(
            (self._grid_coords, self._grid_coords),
            self._field_grid,
            method="cubic",
            bounds_error=False,
            fill_value=None
        )

    def _synthesize_field(self) -> np.ndarray:
        """Synthesize 2D Gaussian random field using 2D FFT."""
        rng = np.random.default_rng(self.seed)
        N = self.grid_size

        # Spatial frequencies
        freq = np.fft.fftfreq(N, d=1.0 / N)
        kx, ky = np.meshgrid(freq, freq, indexing="ij")
        k_sq = kx**2 + ky**2
        k_mag = np.sqrt(k_sq)

        # Power spectral density
        if np.isinf(self.nu):
            # Gaussian covariance: P(k) ~ exp(-2 * pi^2 * ell^2 * k^2)
            psd = np.exp(-2.0 * (np.pi ** 2) * (self.correlation_length ** 2) * k_sq)
        else:
            # Matérn spectral density: P(k) ~ (1 + (2*pi*ell*k)^2 / (2*nu))^{-(nu + 1)}
            scale_sq = (2.0 * np.pi * self.correlation_length) ** 2
            psd = (1.0 + (scale_sq * k_sq) / (2.0 * self.nu)) ** (-(self.nu + 1.0))

        psd[0, 0] = 0.0  # Zero mean
        amplitude = np.sqrt(psd)

        # Complex Gaussian noise
        white_noise = rng.normal(0.0, 1.0, (N, N)) + 1j * rng.normal(0.0, 1.0, (N, N))
        field_fft = white_noise * amplitude

        # Inverse FFT to real space
        field = np.fft.ifft2(field_fft).real

        # Standardize to target variance
        std_val = np.std(field)
        if std_val > 1e-12:
            field = (field - np.mean(field)) / std_val * np.sqrt(self.variance)
        else:
            field = np.zeros_like(field)

        return field

    def evaluate(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Evaluate field at coordinates (x, y) in [0, 1]."""
        pts = np.column_stack([np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64)])
        return self._interpolator(pts)

    def __call__(self, positions: np.ndarray) -> np.ndarray:
        """Evaluate field at positions array of shape (N, 2)."""
        pos = np.asarray(positions, dtype=np.float64)
        return self._interpolator(pos)
