"""
Unit tests for PSF PCA representation.
"""

import unittest
import numpy as np
from representation.pca import PSFRepresentation


class TestPSFRepresentation(unittest.TestCase):

    def setUp(self):
        # Generate synthetic orthogonal patterns
        rng = np.random.default_rng(42)
        self.n_samples = 40
        self.h, self.w = 24, 24
        # Linear combination of 3 base patterns + small noise
        b1 = np.outer(np.sin(np.linspace(0, np.pi, self.h)), np.ones(self.w))
        b2 = np.outer(np.ones(self.h), np.cos(np.linspace(0, np.pi, self.w)))
        b3 = np.outer(np.linspace(-1, 1, self.h), np.linspace(-1, 1, self.w))

        self.psfs = np.zeros((self.n_samples, self.h, self.w))
        for i in range(self.n_samples):
            w1, w2, w3 = rng.normal(0, 1, 3)
            img = 1.0 + w1 * b1 + w2 * b2 + w3 * b3 + rng.normal(0, 0.01, (self.h, self.w))
            self.psfs[i] = img / np.sum(img)

    def test_pca_exact_reconstruction_identity(self):
        """Full-rank PCA should reconstruct training images to numerical precision."""
        pca = PSFRepresentation(n_components_max=self.n_samples)
        pca.fit(self.psfs)
        rec = pca.reconstruct(self.psfs, n_components=self.n_samples)
        np.testing.assert_allclose(rec, self.psfs, rtol=1e-10, atol=1e-10)

    def test_pca_basis_orthonormality(self):
        """EigenPSF vectors must be orthonormal: V_K * V_K^T = I_K."""
        pca = PSFRepresentation(n_components_max=10)
        pca.fit(self.psfs)
        v = pca.components
        vvt = np.dot(v, v.T)
        np.testing.assert_allclose(vvt, np.eye(len(v)), atol=1e-12)

    def test_pca_component_shapes(self):
        """Transform and inverse_transform must respect component truncation K."""
        pca = PSFRepresentation(n_components_max=15)
        pca.fit(self.psfs)

        coeffs_5 = pca.transform(self.psfs, n_components=5)
        self.assertEqual(coeffs_5.shape, (self.n_samples, 5))

        rec_5 = pca.inverse_transform(coeffs_5, n_components=5)
        self.assertEqual(rec_5.shape, (self.n_samples, self.h * self.w))

    def test_pca_explained_variance_monotonic(self):
        """Singular values and explained variances must be strictly descending."""
        pca = PSFRepresentation(n_components_max=10)
        pca.fit(self.psfs)
        ev = pca.explained_variance
        for i in range(len(ev) - 1):
            self.assertGreaterEqual(ev[i], ev[i + 1])


if __name__ == "__main__":
    unittest.main()
