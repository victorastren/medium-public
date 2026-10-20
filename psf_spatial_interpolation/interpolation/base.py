"""
Base class for spatial interpolators predicting PCA coefficient fields across the focal plane.
"""

from abc import ABC, abstractmethod
import numpy as np


class SpatialInterpolator(ABC):
    """
    Abstract base class for all 2D spatial interpolators.

    All subclasses map 2D focal-plane positions (N, 2) in [0, 1]^2
    to multi-component PCA coefficient vectors (N, K).
    """

    @abstractmethod
    def fit(self, positions: np.ndarray, coefficients: np.ndarray) -> "SpatialInterpolator":
        """
        Fit spatial interpolation model.

        Parameters
        ----------
        positions : np.ndarray
            Focal-plane coordinates of shape (N, 2).
        coefficients : np.ndarray
            PCA coefficient matrix of shape (N, K).

        Returns
        -------
        self
        """
        pass

    @abstractmethod
    def predict(self, positions: np.ndarray) -> np.ndarray:
        """
        Predict PCA coefficients at query coordinates.

        Parameters
        ----------
        positions : np.ndarray
            Focal-plane coordinates of shape (M, 2).

        Returns
        -------
        np.ndarray
            Predicted coefficient matrix of shape (M, K).
        """
        pass
