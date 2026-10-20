"""
Dataset generation and coordinate sampling for simulated PSF fields.

Supports:
- Uniform coordinate sampling with fixed random seeds for train (320), val (80), test (200).
- Nested training subsets: N_train in {100, 200, 320}.
- Deterministic PSF field generator interface: generate_psf(field_x, field_y, field_parameters).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import numpy as np
from simulation.spatial_fields import PolynomialField2D, CorrelatedRandomField2D
from simulation.moffat import generate_moffat_psf


@dataclass
class PSFFieldDataset:
    positions_train: np.ndarray        # (N_train, 2)
    positions_val: np.ndarray          # (N_val, 2)
    positions_test: np.ndarray         # (N_test, 2)
    psfs_train_true: np.ndarray        # (N_train, 48, 48)
    psfs_train_observed: np.ndarray    # (N_train, 48, 48)
    psfs_val_true: np.ndarray          # (N_val, 48, 48)
    psfs_test_true: np.ndarray         # (N_test, 48, 48)
    true_test_e1: np.ndarray           # (N_test,)
    true_test_e2: np.ndarray           # (N_test,)
    true_test_r2: np.ndarray           # (N_test,)
    true_test_e1_unweighted: np.ndarray | None = None
    true_test_e2_unweighted: np.ndarray | None = None
    true_test_r2_unweighted: np.ndarray | None = None
    analytic_test_e1: np.ndarray | None = None
    analytic_test_e2: np.ndarray | None = None
    analytic_test_fwhm: np.ndarray | None = None


def sample_field_positions(
    n_train: int = 320,
    n_val: int = 80,
    n_test: int = 200,
    seed: int = 42,
    margin: float = 0.02
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Sample independent focal-plane coordinates uniformly across [margin, 1 - margin]^2.
    """
    rng = np.random.default_rng(seed)
    span = 1.0 - 2.0 * margin

    pos_train = margin + span * rng.uniform(0.0, 1.0, (n_train, 2))
    pos_val = margin + span * rng.uniform(0.0, 1.0, (n_val, 2))
    pos_test = margin + span * rng.uniform(0.0, 1.0, (n_test, 2))

    return (
        pos_train.astype(np.float64),
        pos_val.astype(np.float64),
        pos_test.astype(np.float64)
    )


class SmoothMoffatFieldGenerator:
    """
    Generates a smoothly varying seeing-dominated Moffat PSF field (Scenario G1-smooth):
    - FWHM(x, y) = 3.5 + smooth variation
    - e1(x, y) = quadratic polynomial field
    - e2(x, y) = quadratic polynomial field
    """

    def __init__(self, seed: int = 100, beta: float = 3.5,
                 base_fwhm: float = 3.5, fwhm_amp: float = 0.3,
                 ellip_amp: float = 0.06):
        self.seed = seed
        self.beta = float(beta)
        self.base_fwhm = float(base_fwhm)

        # Polynomial fields for FWHM, e1, e2
        self.field_fwhm = PolynomialField2D(degree=2, seed=seed + 1, amplitude=fwhm_amp, mean=base_fwhm)
        self.field_e1 = PolynomialField2D(degree=2, seed=seed + 2, amplitude=ellip_amp, mean=0.02)
        self.field_e2 = PolynomialField2D(degree=2, seed=seed + 3, amplitude=ellip_amp, mean=-0.01)

    def eval_parameters(self, positions: np.ndarray) -> dict[str, np.ndarray]:
        """Evaluate parameter fields at coordinate array of shape (N, 2)."""
        pos = np.asarray(positions, dtype=np.float64)
        return {
            "fwhm": np.clip(self.field_fwhm(pos), 2.5, 5.0),
            "e1": np.clip(self.field_e1(pos), -0.2, 0.2),
            "e2": np.clip(self.field_e2(pos), -0.2, 0.2),
            "beta": np.full(len(pos), self.beta, dtype=np.float64),
            "c1": np.zeros(len(pos), dtype=np.float64),
            "c2": np.zeros(len(pos), dtype=np.float64),
        }

    def generate_psf(self, x: float, y: float, stamp_size: int = 48,
                     subpixel_factor: int = 4) -> np.ndarray:
        """Deterministic PSF generation at position (x, y)."""
        pos = np.array([[x, y]], dtype=np.float64)
        fwhm_val = float(np.clip(self.field_fwhm(pos)[0], 2.5, 5.0))
        e1_val = float(np.clip(self.field_e1(pos)[0], -0.2, 0.2))
        e2_val = float(np.clip(self.field_e2(pos)[0], -0.2, 0.2))

        return generate_moffat_psf(
            fwhm=fwhm_val,
            beta=self.beta,
            e1=e1_val,
            e2=e2_val,
            stamp_size=stamp_size,
            subpixel_factor=subpixel_factor
        )

    def generate_psf_batch(self, positions: np.ndarray, stamp_size: int = 48,
                           subpixel_factor: int = 4) -> np.ndarray:
        """Generate batch of PSFs for array of coordinates (N, 2)."""
        n = len(positions)
        stack = np.zeros((n, stamp_size, stamp_size), dtype=np.float64)
        for i in range(n):
            stack[i] = self.generate_psf(
                positions[i, 0], positions[i, 1],
                stamp_size=stamp_size, subpixel_factor=subpixel_factor
            )
        return stack


class ComplexGroundFieldGenerator:
    """
    Generates a realistic ground-based PSF field (Scenario G2):
    Combines optical aberrations across the telescope focal plane with
    spatially correlated turbulent atmospheric fluctuations:

    1. Optical aberrations (deterministic large-scale field variations):
       - Field curvature / defocus: increases FWHM quadratically away from optical axis (0.5, 0.5)
       - Optical astigmatism: Seidel astigmatism (e1 ~ dx^2 - dy^2, e2 ~ 2*dx*dy)
       - Optical coma: Seidel coma increasing radially away from center (c1 ~ dx, c2 ~ dy)

    2. Spatially correlated atmospheric turbulence fluctuations (CorrelatedRandomField2D):
       - delta_FWHM(x, y): Matérn covariance (nu=1.5, ell=0.20, std=0.15 px)
       - delta_e1(x, y): Matérn covariance (nu=1.5, ell=0.20, std=0.02)
       - delta_e2(x, y): Matérn covariance (nu=1.5, ell=0.20, std=0.02)
       - delta_beta(x, y): Matérn covariance (nu=1.5, ell=0.20, std=0.25)
    """

    def __init__(
        self,
        seed: int = 500,
        base_fwhm: float = 3.4,
        defocus_coeff: float = 1.2,
        astig_coeff: float = 0.10,
        coma_coeff: float = 0.08,
        beta_base: float = 3.5,
        correlation_length: float = 0.20
    ):
        self.seed = seed
        self.base_fwhm = float(base_fwhm)
        self.defocus_coeff = float(defocus_coeff)
        self.astig_coeff = float(astig_coeff)
        self.coma_coeff = float(coma_coeff)
        self.beta_base = float(beta_base)
        self.correlation_length = float(correlation_length)

        # Correlated Matérn random fields
        self.crf_fwhm = CorrelatedRandomField2D(
            correlation_length=correlation_length, variance=0.15**2, nu=1.5, seed=seed + 1
        )
        self.crf_e1 = CorrelatedRandomField2D(
            correlation_length=correlation_length, variance=0.02**2, nu=1.5, seed=seed + 2
        )
        self.crf_e2 = CorrelatedRandomField2D(
            correlation_length=correlation_length, variance=0.02**2, nu=1.5, seed=seed + 3
        )
        self.crf_beta = CorrelatedRandomField2D(
            correlation_length=correlation_length, variance=0.25**2, nu=1.5, seed=seed + 4
        )

    def eval_parameters(self, positions: np.ndarray) -> dict[str, np.ndarray]:
        pos = np.asarray(positions, dtype=np.float64)
        dx = pos[:, 0] - 0.5
        dy = pos[:, 1] - 0.5
        r2_field = dx**2 + dy**2

        fwhm_opt = self.base_fwhm + self.defocus_coeff * r2_field
        e1_opt = self.astig_coeff * (dx**2 - dy**2)
        e2_opt = 2.0 * self.astig_coeff * (dx * dy)
        c1_opt = self.coma_coeff * dx
        c2_opt = self.coma_coeff * dy

        fwhm = np.clip(fwhm_opt + self.crf_fwhm(pos), 2.5, 5.0)
        e1 = np.clip(e1_opt + self.crf_e1(pos), -0.25, 0.25)
        e2 = np.clip(e2_opt + self.crf_e2(pos), -0.25, 0.25)
        beta = np.clip(self.beta_base + self.crf_beta(pos), 2.6, 4.6)

        return {
            "fwhm": fwhm,
            "e1": e1,
            "e2": e2,
            "c1": c1_opt,
            "c2": c2_opt,
            "beta": beta
        }

    def generate_psf(self, x: float, y: float, stamp_size: int = 48, subpixel_factor: int = 4) -> np.ndarray:
        p = self.eval_parameters(np.array([[x, y]], dtype=np.float64))
        return generate_moffat_psf(
            fwhm=float(p["fwhm"][0]),
            beta=float(p["beta"][0]),
            e1=float(p["e1"][0]),
            e2=float(p["e2"][0]),
            c1=float(p["c1"][0]),
            c2=float(p["c2"][0]),
            stamp_size=stamp_size,
            subpixel_factor=subpixel_factor
        )

    def generate_psf_batch(self, positions: np.ndarray, stamp_size: int = 48, subpixel_factor: int = 4) -> np.ndarray:
        n = len(positions)
        params = self.eval_parameters(positions)
        stack = np.zeros((n, stamp_size, stamp_size), dtype=np.float64)
        for i in range(n):
            stack[i] = generate_moffat_psf(
                fwhm=float(params["fwhm"][i]),
                beta=float(params["beta"][i]),
                e1=float(params["e1"][i]),
                e2=float(params["e2"][i]),
                c1=float(params["c1"][i]),
                c2=float(params["c2"][i]),
                stamp_size=stamp_size,
                subpixel_factor=subpixel_factor
            )
        return stack


def build_field_dataset(
    generator: Any,
    n_train: int = 320,
    n_val: int = 80,
    n_test: int = 200,
    seed: int = 42,
    stamp_size: int = 48,
    subpixel_factor: int = 4
) -> PSFFieldDataset:
    """Generate complete PSF field dataset across train, validation, and test splits."""
    from validation.moments import measure_psf_batch

    pos_train, pos_val, pos_test = sample_field_positions(
        n_train=n_train, n_val=n_val, n_test=n_test, seed=seed
    )

    psfs_train_true = generator.generate_psf_batch(pos_train, stamp_size=stamp_size, subpixel_factor=subpixel_factor)
    psfs_train_obs = psfs_train_true.copy()  # Baseline is noiseless

    psfs_val_true = generator.generate_psf_batch(pos_val, stamp_size=stamp_size, subpixel_factor=subpixel_factor)
    psfs_test_true = generator.generate_psf_batch(pos_test, stamp_size=stamp_size, subpixel_factor=subpixel_factor)

    # Primary reference: Gaussian-weighted quadrupole moments (GREAT10 convention, sigma_w = 3.5 px)
    e1_test_w, e2_test_w, r2_test_w = measure_psf_batch(psfs_test_true, sigma_w=3.5)

    # Diagnostic reference: unweighted central second moments (sigma_w = None)
    e1_test_unw, e2_test_unw, r2_test_unw = measure_psf_batch(psfs_test_true, sigma_w=None)

    # Analytic generator inputs at test coordinates
    if hasattr(generator, "eval_parameters"):
        analytic_params = generator.eval_parameters(pos_test)
        analytic_fwhm = analytic_params["fwhm"]
        analytic_e1 = analytic_params["e1"]
        analytic_e2 = analytic_params["e2"]
    else:
        analytic_fwhm = np.clip(generator.field_fwhm(pos_test), 2.5, 5.0)
        analytic_e1 = np.clip(generator.field_e1(pos_test), -0.2, 0.2)
        analytic_e2 = np.clip(generator.field_e2(pos_test), -0.2, 0.2)

    return PSFFieldDataset(
        positions_train=pos_train,
        positions_val=pos_val,
        positions_test=pos_test,
        psfs_train_true=psfs_train_true,
        psfs_train_observed=psfs_train_obs,
        psfs_val_true=psfs_val_true,
        psfs_test_true=psfs_test_true,
        true_test_e1=e1_test_w,
        true_test_e2=e2_test_w,
        true_test_r2=r2_test_w,
        true_test_e1_unweighted=e1_test_unw,
        true_test_e2_unweighted=e2_test_unw,
        true_test_r2_unweighted=r2_test_unw,
        analytic_test_e1=analytic_e1,
        analytic_test_e2=analytic_e2,
        analytic_test_fwhm=analytic_fwhm
    )


def save_field_dataset(dataset: PSFFieldDataset, output_dir: str, config: dict | None = None) -> None:
    """
    Save field dataset to disk matching technical specification Section 3.5:
    - config.json
    - positions_train.npy, positions_validation.npy, positions_test.npy
    - psf_train_true.npy, psf_train_observed.npy
    - psf_validation_true.npy, psf_test_true.npy
    - physical_parameters.npz
    """
    import os
    import json

    os.makedirs(output_dir, exist_ok=True)

    # Save coordinate arrays
    np.save(os.path.join(output_dir, "positions_train.npy"), dataset.positions_train)
    np.save(os.path.join(output_dir, "positions_validation.npy"), dataset.positions_val)
    np.save(os.path.join(output_dir, "positions_test.npy"), dataset.positions_test)

    # Save PSF image arrays
    np.save(os.path.join(output_dir, "psf_train_true.npy"), dataset.psfs_train_true)
    np.save(os.path.join(output_dir, "psf_train_observed.npy"), dataset.psfs_train_observed)
    np.save(os.path.join(output_dir, "psf_validation_true.npy"), dataset.psfs_val_true)
    np.save(os.path.join(output_dir, "psf_test_true.npy"), dataset.psfs_test_true)

    # Save physical parameters (weighted, unweighted, and analytic)
    np.savez_compressed(
        os.path.join(output_dir, "physical_parameters.npz"),
        # Primary reference: circular Gaussian-weighted moments (sigma_w = 3.5 px)
        true_test_e1=dataset.true_test_e1,
        true_test_e2=dataset.true_test_e2,
        true_test_r2=dataset.true_test_r2,
        # Diagnostic unweighted moments (sigma_w = None)
        true_test_e1_unweighted=getattr(dataset, "true_test_e1_unweighted", dataset.true_test_e1),
        true_test_e2_unweighted=getattr(dataset, "true_test_e2_unweighted", dataset.true_test_e2),
        true_test_r2_unweighted=getattr(dataset, "true_test_r2_unweighted", dataset.true_test_r2),
        # Analytic generator inputs
        analytic_test_e1=getattr(dataset, "analytic_test_e1", np.zeros_like(dataset.true_test_e1)),
        analytic_test_e2=getattr(dataset, "analytic_test_e2", np.zeros_like(dataset.true_test_e2)),
        analytic_test_fwhm=getattr(dataset, "analytic_test_fwhm", np.zeros_like(dataset.true_test_r2)),
        n_train=len(dataset.positions_train),
        n_val=len(dataset.positions_val),
        n_test=len(dataset.positions_test),
        sigma_w=3.5,
        moment_convention="GREAT10 circular Gaussian-weighted central moments (sigma_w = 3.5 px)"
    )

    # Save config
    cfg = config or {
        "scenario": "G1_smooth",
        "stamp_size": dataset.psfs_train_true.shape[1],
        "n_train": len(dataset.positions_train),
        "n_val": len(dataset.positions_val),
        "n_test": len(dataset.positions_test),
        "subpixel_factor": 4,
        "normalization": "unit_flux",
        "description": "Seeing-dominated smooth Moffat PSF field"
    }
    with open(os.path.join(output_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def load_dataset(dataset_dir: str) -> PSFFieldDataset:
    """
    Load saved PSFFieldDataset from serialized directory.
    """
    d = Path(dataset_dir)
    pos_train = np.load(d / "positions_train.npy")
    pos_val = np.load(d / "positions_validation.npy")
    pos_test = np.load(d / "positions_test.npy")

    psfs_train_true = np.load(d / "psf_train_true.npy")
    psfs_train_obs = np.load(d / "psf_train_observed.npy")
    psfs_val_true = np.load(d / "psf_validation_true.npy")
    psfs_test_true = np.load(d / "psf_test_true.npy")

    params = np.load(d / "physical_parameters.npz")
    true_test_e1 = params["true_test_e1"]
    true_test_e2 = params["true_test_e2"]
    true_test_r2 = params["true_test_r2"]

    return PSFFieldDataset(
        positions_train=pos_train,
        positions_val=pos_val,
        positions_test=pos_test,
        psfs_train_true=psfs_train_true,
        psfs_train_observed=psfs_train_obs,
        psfs_val_true=psfs_val_true,
        psfs_test_true=psfs_test_true,
        true_test_e1=true_test_e1,
        true_test_e2=true_test_e2,
        true_test_r2=true_test_r2,
        true_test_e1_unweighted=params["true_test_e1_unweighted"] if "true_test_e1_unweighted" in params else None,
        true_test_e2_unweighted=params["true_test_e2_unweighted"] if "true_test_e2_unweighted" in params else None,
        true_test_r2_unweighted=params["true_test_r2_unweighted"] if "true_test_r2_unweighted" in params else None,
        analytic_test_e1=params["analytic_test_e1"] if "analytic_test_e1" in params else None,
        analytic_test_e2=params["analytic_test_e2"] if "analytic_test_e2" in params else None,
        analytic_test_fwhm=params["analytic_test_fwhm"] if "analytic_test_fwhm" in params else None
    )

