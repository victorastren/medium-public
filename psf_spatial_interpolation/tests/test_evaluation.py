"""
Unit tests for validation and hyperparameter tuning suite (Phase 2).
"""

import unittest
from pathlib import Path
import numpy as np

from simulation.dataset import load_dataset
from representation.pca import PSFRepresentation
from validation.evaluation import (
    compute_composite_loss,
    tune_and_evaluate_model,
    ModelBenchmarkResult
)
from interpolation.classical import PolynomialInterpolator


class TestEvaluationSuite(unittest.TestCase):
    """Test hyperparameter tuning and evaluation pipeline components."""

    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(__file__).resolve().parent.parent / "data" / "field_000"
        cls.dataset = load_dataset(str(cls.data_dir))
        cls.pca = PSFRepresentation(n_components_max=5).fit(cls.dataset.psfs_train_observed)
        cls.train_coeffs = cls.pca.transform(cls.dataset.psfs_train_observed, n_components=5)

    def test_composite_loss_calculation(self):
        """Zero residuals must yield zero composite loss."""
        e1 = np.array([0.05, -0.02, 0.03])
        e2 = np.array([0.01, 0.04, -0.01])
        r2 = np.array([4.5, 4.8, 5.0])

        loss, e_rmse, r2_rmse = compute_composite_loss(e1, e2, r2, e1, e2, r2)
        self.assertAlmostEqual(loss, 0.0, places=9)
        self.assertAlmostEqual(e_rmse, 0.0, places=9)
        self.assertAlmostEqual(r2_rmse, 0.0, places=9)

    def test_tune_and_evaluate_polynomial(self):
        """Tuning polynomial degree over {1, 2} on validation stars and evaluating on test stars."""
        from validation.moments import measure_psf_batch
        val_e1, val_e2, val_r2 = measure_psf_batch(self.dataset.psfs_val_true, sigma_w=3.5)
        val_moments = {"e1": val_e1, "e2": val_e2, "r2": val_r2}
        test_moments = {
            "e1": self.dataset.true_test_e1,
            "e2": self.dataset.true_test_e2,
            "r2": self.dataset.true_test_r2
        }

        res = tune_and_evaluate_model(
            model_name="Polynomial",
            category="Classical",
            param_grid=[{"degree": 1}, {"degree": 2}],
            model_factory=PolynomialInterpolator,
            train_pos=self.dataset.positions_train,
            train_coeffs=self.train_coeffs,
            val_pos=self.dataset.positions_val,
            val_moments=val_moments,
            test_pos=self.dataset.positions_test,
            test_moments=test_moments,
            test_images=self.dataset.psfs_test_true,
            pca=self.pca,
            sigma_w=3.5
        )

        self.assertIsInstance(res, ModelBenchmarkResult)
        self.assertEqual(res.best_params["degree"], 2)
        self.assertLess(res.test_e_rmse, 1e-3)
        self.assertLess(res.test_r2_rmse, 1e-2)
        self.assertGreater(res.fit_time_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
