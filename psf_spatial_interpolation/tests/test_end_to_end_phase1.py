"""
End-to-end integration tests for Phase 1:
1. Synthetic known-basis test (exact mathematical recovery)
2. Smooth Moffat baseline pipeline test (astronomical PSF simulation, PCA, interpolation, reconstruction, moments)
"""

import unittest
import numpy as np
from representation.pca import PSFRepresentation
from interpolation.classical import PolynomialInterpolator
from reconstruction.psf import reconstruct_psfs_from_coefficients
from simulation.dataset import SmoothMoffatFieldGenerator, sample_field_positions
from validation.moments import measure_psf_batch
from validation.metrics import compute_reconstruction_metrics, compute_representation_error


class TestEndToEndPhase1(unittest.TestCase):

    def test_synthetic_known_linear_basis_exact_recovery(self):
        """
        Special synthetic test:
        PSFs generated from a known 3-component orthogonal basis with quadratic spatial coefficients.
        Both PCA and degree-2 polynomial regression have exact solutions.
        The full pipeline must recover test PSFs to near machine precision.
        """
        rng = np.random.default_rng(42)
        n_train, n_test = 50, 20
        h, w = 24, 24
        p = h * w

        # 3 orthogonal patterns
        b1 = np.outer(np.sin(np.linspace(0, np.pi, h)), np.ones(w)).ravel()
        b2 = np.outer(np.ones(h), np.cos(np.linspace(0, np.pi, w))).ravel()
        b3 = np.outer(np.linspace(-1, 1, h), np.linspace(-1, 1, w)).ravel()

        b1 /= np.linalg.norm(b1)
        b2 = b2 - np.dot(b1, b2) * b1
        b2 /= np.linalg.norm(b2)
        b3 = b3 - np.dot(b1, b3) * b1 - np.dot(b2, b3) * b2
        b3 /= np.linalg.norm(b3)

        basis = np.vstack([b1, b2, b3])  # Shape (3, P)
        mean_flat = np.ones(p) / p

        # Quadratic coefficient formulas
        def true_coeffs(pos):
            x, y = pos[:, 0], pos[:, 1]
            a1 = 1.0 + 2.0 * x - 1.5 * y + 0.5 * (x**2)
            a2 = -0.5 + 1.2 * x * y - 0.8 * (y**2)
            a3 = 0.8 - 0.4 * x + 1.1 * y
            return np.column_stack([a1, a2, a3])

        train_pos = rng.uniform(0.05, 0.95, (n_train, 2))
        test_pos = rng.uniform(0.1, 0.9, (n_test, 2))

        train_c = true_coeffs(train_pos)
        test_c = true_coeffs(test_pos)

        train_psfs = (np.dot(train_c, basis) + mean_flat).reshape(n_train, h, w)
        test_psfs = (np.dot(test_c, basis) + mean_flat).reshape(n_test, h, w)

        # 1. Fit PCA with K=3
        pca = PSFRepresentation(n_components_max=3)
        pca.fit(train_psfs)

        # Representation error on test set
        rep_test = pca.reconstruct(test_psfs, n_components=3)
        e_rep = compute_representation_error(test_psfs, rep_test)
        self.assertLess(e_rep, 1e-10)

        # 2. Extract train coefficients and fit degree-2 polynomial interpolator
        train_pca_coeffs = pca.transform(train_psfs, n_components=3)
        poly = PolynomialInterpolator(degree=2)
        poly.fit(train_pos, train_pca_coeffs)

        # 3. Predict test coefficients and reconstruct
        pred_test_coeffs = poly.predict(test_pos)
        rec_test_psfs = reconstruct_psfs_from_coefficients(pred_test_coeffs, pca, physical_adjustment=False)

        # End-to-end reconstruction error must be negligible
        e_total = compute_representation_error(test_psfs, rec_test_psfs)
        self.assertLess(e_total, 1e-9)

    def test_smooth_moffat_baseline_pipeline(self):
        """
        Verify the complete pipeline on the realistic smooth Moffat baseline:
        Simulation -> PCA -> Polynomial Interpolation -> Reconstruction -> Moments & Metrics.
        """
        generator = SmoothMoffatFieldGenerator(seed=42)
        pos_train, pos_val, pos_test = sample_field_positions(n_train=80, n_val=20, n_test=30, seed=123)

        # Generate ground truth PSFs
        train_psfs = generator.generate_psf_batch(pos_train, stamp_size=48)
        test_psfs = generator.generate_psf_batch(pos_test, stamp_size=48)

        # 1. Fit PCA with K=5 components
        pca = PSFRepresentation(n_components_max=5)
        pca.fit(train_psfs)

        # Check representation error on test set
        rep_test = pca.reconstruct(test_psfs, n_components=5)
        e_rep = compute_representation_error(test_psfs, rep_test)
        self.assertLess(e_rep, 0.05, f"Representation error unexpectedly large: {e_rep}")

        # 2. Transform train PSFs and fit PolynomialInterpolator (degree 2)
        train_coeffs = pca.transform(train_psfs, n_components=5)
        interpolator = PolynomialInterpolator(degree=2)
        interpolator.fit(pos_train, train_coeffs)

        # 3. Predict test coefficients
        pred_test_coeffs = interpolator.predict(pos_test)

        # 4. Reconstruct test PSFs (with physical adjustment)
        rec_test_psfs = reconstruct_psfs_from_coefficients(pred_test_coeffs, pca, physical_adjustment=True)

        # 5. Measure moments on true and reconstructed test PSFs
        true_e1, true_e2, true_r2 = measure_psf_batch(test_psfs, sigma_w=3.5)
        rec_e1, rec_e2, rec_r2 = measure_psf_batch(rec_test_psfs, sigma_w=3.5)

        # 6. Evaluate scientific metrics
        metrics = compute_reconstruction_metrics(
            true_e1=true_e1, true_e2=true_e2, true_r2=true_r2,
            pred_e1=rec_e1, pred_e2=rec_e2, pred_r2=rec_r2,
            true_psfs=test_psfs, pred_psfs=rec_test_psfs
        )

        # Verify metrics exist and are within tight bounds for smooth baseline
        self.assertLess(metrics.combined_ellipticity_rmse, 0.015,
                        f"Ellipticity RMSE too large: {metrics.combined_ellipticity_rmse}")
        self.assertLess(metrics.r2_rel_stats.rmse, 0.02,
                        f"Relative size RMSE too large: {metrics.r2_rel_stats.rmse}")


if __name__ == "__main__":
    unittest.main()
