"""
Machine learning spatial interpolators for PCA coefficient fields:
1. Multi-output Random Forest (piecewise-constant ensemble splits)
2. Continuous Multilayer Perceptron (MLPRegressor with L-BFGS and smooth activations)
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from interpolation.base import SpatialInterpolator


class RandomForestInterpolator(SpatialInterpolator):
    """
    Multi-output Random Forest spatial regressor.
    Maps 2D focal-plane coordinates to K PCA coefficients simultaneously.
    """

    def __init__(self, n_estimators: int = 100, max_depth: int | None = None,
                 min_samples_leaf: int = 2, random_state: int = 42):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=-1
        )

    def fit(self, positions: np.ndarray, coefficients: np.ndarray) -> "RandomForestInterpolator":
        x = np.asarray(positions, dtype=np.float64)
        y = np.asarray(coefficients, dtype=np.float64)
        self.model.fit(x, y)
        return self

    def predict(self, positions: np.ndarray) -> np.ndarray:
        x = np.asarray(positions, dtype=np.float64)
        preds = self.model.predict(x)
        if preds.ndim == 1:
            preds = preds[:, None]
        return preds


class MLPInterpolator(SpatialInterpolator):
    """
    Multi-output Neural Network (MLP) spatial regressor:
        (x, y) in R^2 -> (a_1, ..., a_K) in R^K
    Uses L-BFGS quasi-Newton solver with input and target standard scaling.
    """

    def __init__(
        self,
        hidden_layer_sizes: tuple[int, ...] = (32, 16),
        activation: str = "tanh",
        alpha: float = 0.01,
        max_iter: int = 2000,
        random_state: int = 42
    ):
        self.hidden_layer_sizes = hidden_layer_sizes
        self.activation = activation
        self.alpha = float(alpha)
        self.max_iter = int(max_iter)
        self.random_state = int(random_state)

        self.position_scaler = StandardScaler()
        self.coefficient_scaler = StandardScaler()
        self.model = MLPRegressor(
            hidden_layer_sizes=self.hidden_layer_sizes,
            activation=self.activation,
            solver="lbfgs",
            alpha=self.alpha,
            max_iter=self.max_iter,
            random_state=self.random_state
        )

    def fit(self, positions: np.ndarray, coefficients: np.ndarray) -> "MLPInterpolator":
        pos = np.asarray(positions, dtype=np.float64)
        coeffs = np.asarray(coefficients, dtype=np.float64)

        x_scaled = self.position_scaler.fit_transform(pos)
        y_scaled = self.coefficient_scaler.fit_transform(coeffs)
        self.model.fit(x_scaled, y_scaled)
        return self

    def predict(self, positions: np.ndarray) -> np.ndarray:
        pos = np.asarray(positions, dtype=np.float64)
        x_scaled = self.position_scaler.transform(pos)
        y_scaled = self.model.predict(x_scaled)
        if y_scaled.ndim == 1:
            y_scaled = y_scaled[:, None]
        return self.coefficient_scaler.inverse_transform(y_scaled)
