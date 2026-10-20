"""
Fourier optics module for diffraction-based space telescope PSF simulation (Scenario S1).

Implements:
1. Matrix Fourier Transform (MFT, Soummer et al. 2007) for exact, arbitrary-resolution
   Fourier optics without zero-padding or FFT cropping artifacts.
2. Circular telescope pupil with central obscuration and 4 spider support struts.
3. Optical wavefront aberrations expanded in Zernike polynomials:
   - Z4: Defocus (field curvature)
   - Z5, Z6: Oblique and vertical astigmatism
   - Z7, Z8: Horizontal and vertical coma
   - Z11: Primary spherical aberration
4. SpaceDiffractionFieldGenerator: deterministic field-dependent aberration generator.
"""

from dataclasses import dataclass
import numpy as np


class MatrixFourierTransform:
    """
    Matrix Fourier Transform (MFT) between normalized pupil plane and detector plane.
    Computes exact continuous 2D Fourier transform using separable 1D matrix products.
    """

    def __init__(
        self,
        n_pupil: int = 128,
        stamp_size: int = 48,
        subpixel_factor: int = 4,
        sampling_s: float = 2.5
    ):
        self.n_pupil = n_pupil
        self.stamp_size = stamp_size
        self.subpixel_factor = subpixel_factor
        self.sampling_s = float(sampling_s)
        self.n_focal = stamp_size * subpixel_factor  # e.g., 192

        # Pupil 1D coordinate vector in normalized units [-1, 1]
        self.u = np.linspace(-1.0, 1.0, n_pupil, dtype=np.float64)

        # High-resolution focal plane coordinates centered symmetrically about 0
        # In detector pixel units:
        x_det = (np.arange(self.n_focal, dtype=np.float64) + 0.5) / subpixel_factor - (stamp_size / 2.0)
        # Convert detector pixels to diffraction units (lambda / D):
        self.x_lam = x_det / self.sampling_s

        # Precompute 1D kernel matrices E_x and E_y of shape (n_focal, n_pupil)
        # Integral kernel: exp(-i * pi * x_lam * u)
        kernel = -1j * np.pi * np.outer(self.x_lam, self.u)
        self.E_x = np.exp(kernel).astype(np.complex128)
        self.E_y = self.E_x.copy()

    def transform(self, wavefront: np.ndarray) -> np.ndarray:
        """
        Compute focal plane intensity array from pupil complex wavefront.
        Supports single 2D wavefront (n_pupil, n_pupil) or batch (N, n_pupil, n_pupil).
        """
        wf = np.asarray(wavefront, dtype=np.complex128)
        if wf.ndim == 2:
            # psi: (n_focal, n_pupil) @ (n_pupil, n_pupil) @ (n_pupil, n_focal) -> (n_focal, n_focal)
            psi = self.E_y @ wf @ self.E_x.T
            psf_sub = np.abs(psi) ** 2
            # Bin subpixels into detector pixels
            binned = psf_sub.reshape(
                self.stamp_size, self.subpixel_factor,
                self.stamp_size, self.subpixel_factor
            ).mean(axis=(1, 3))
            flux = np.sum(binned)
            return binned / flux if flux > 0.0 else binned
        elif wf.ndim == 3:
            # Batch transformation across N stars
            n_stars = len(wf)
            psi = self.E_y @ wf @ self.E_x.T
            psf_sub = np.abs(psi) ** 2
            binned = psf_sub.reshape(
                n_stars, self.stamp_size, self.subpixel_factor,
                self.stamp_size, self.subpixel_factor
            ).mean(axis=(2, 4))
            fluxes = np.sum(binned, axis=(1, 2), keepdims=True)
            return np.where(fluxes > 0.0, binned / fluxes, binned)
        else:
            raise ValueError(f"Wavefront array must have 2 or 3 dimensions, got {wf.ndim}")


class SpaceOpticsPupil:
    """
    Pupil model for space telescope optics:
    - Circular aperture with clear outer radius rho <= 1.0
    - Central obscuration rho >= obscuration_ratio
    - 4 spider support struts producing orthogonal diffraction spikes
    - Precomputed Zernike aberration modes
    """

    def __init__(
        self,
        n_pupil: int = 128,
        obscuration_ratio: float = 0.30,
        strut_width: float = 0.025
    ):
        self.n_pupil = n_pupil
        self.obscuration_ratio = float(obscuration_ratio)
        self.strut_width = float(strut_width)

        u = np.linspace(-1.0, 1.0, n_pupil, dtype=np.float64)
        U, V = np.meshgrid(u, u, indexing="xy")
        self.U = U
        self.V = V
        self.rho = np.sqrt(U**2 + V**2)
        self.theta = np.arctan2(V, U)

        # Clear annular aperture
        aperture = (self.rho <= 1.0) & (self.rho >= self.obscuration_ratio)
        # 4 spider struts aligned with primary axes
        struts = (np.abs(U) <= self.strut_width / 2.0) | (np.abs(V) <= self.strut_width / 2.0)
        self.mask = aperture & (~struts)

        # Precompute normalized Zernike basis modes
        # Z4: Defocus
        self.Z4 = np.sqrt(3.0) * (2.0 * self.rho**2 - 1.0) * self.mask
        # Z5: Oblique Astigmatism (45 deg)
        self.Z5 = np.sqrt(6.0) * (self.rho**2) * np.sin(2.0 * self.theta) * self.mask
        # Z6: Vertical Astigmatism (0/90 deg)
        self.Z6 = np.sqrt(6.0) * (self.rho**2) * np.cos(2.0 * self.theta) * self.mask
        # Z7: Horizontal Coma
        self.Z7 = np.sqrt(8.0) * (3.0 * self.rho**3 - 2.0 * self.rho) * np.cos(self.theta) * self.mask
        # Z8: Vertical Coma
        self.Z8 = np.sqrt(8.0) * (3.0 * self.rho**3 - 2.0 * self.rho) * np.sin(self.theta) * self.mask
        # Z11: Primary Spherical Aberration
        self.Z11 = np.sqrt(5.0) * (6.0 * self.rho**4 - 6.0 * self.rho**2 + 1.0) * self.mask

    def compute_wavefront(
        self,
        c4: float = 0.0,
        c5: float = 0.0,
        c6: float = 0.0,
        c7: float = 0.0,
        c8: float = 0.0,
        c11: float = 0.0
    ) -> np.ndarray:
        """Compute complex pupil wavefront for given Zernike amplitudes in units of waves lambda."""
        phase = (
            c4 * self.Z4
            + c5 * self.Z5
            + c6 * self.Z6
            + c7 * self.Z7
            + c8 * self.Z8
            + c11 * self.Z11
        )
        return self.mask.astype(np.complex128) * np.exp(1j * 2.0 * np.pi * phase)

    def compute_wavefront_batch(
        self,
        c4: np.ndarray,
        c5: np.ndarray,
        c6: np.ndarray,
        c7: np.ndarray,
        c8: np.ndarray,
        c11: np.ndarray
    ) -> np.ndarray:
        """Compute batch of complex pupil wavefronts for 1D arrays of Zernike amplitudes."""
        phase_stack = (
            c4[:, None, None] * self.Z4[None, :, :]
            + c5[:, None, None] * self.Z5[None, :, :]
            + c6[:, None, None] * self.Z6[None, :, :]
            + c7[:, None, None] * self.Z7[None, :, :]
            + c8[:, None, None] * self.Z8[None, :, :]
            + c11[:, None, None] * self.Z11[None, :, :]
        )
        return self.mask[None, :, :].astype(np.complex128) * np.exp(1j * 2.0 * np.pi * phase_stack)


class SpaceDiffractionFieldGenerator:
    """
    Scenario S1: Diffraction-based optical PSF field with spatially varying aberrations.
    Approximates space telescope observations without atmospheric turbulence.

    Spatial variation:
    - Defocus c4(x, y) = c4_base + a_def * ((x - 0.5)^2 + (y - 0.5)^2)  (field curvature)
    - Astigmatism c5(x, y) = 2 * a_ast * (x - 0.5) * (y - 0.5)
    - Astigmatism c6(x, y) = a_ast * ((x - 0.5)^2 - (y - 0.5)^2)       (Seidel off-axis astigmatism)
    - Coma c7(x, y) = a_coma * (x - 0.5)                                (Seidel coma)
    - Coma c8(x, y) = a_coma * (y - 0.5)
    - Spherical c11(x, y) = c11_base                                    (constant spherical aberration)
    """

    def __init__(
        self,
        c4_base: float = 0.02,
        a_def: float = 0.08,
        a_ast: float = 0.04,
        a_coma: float = 0.05,
        c11_base: float = 0.02,
        n_pupil: int = 128,
        stamp_size: int = 48,
        subpixel_factor: int = 4,
        sampling_s: float = 2.5,
        obscuration_ratio: float = 0.30,
        strut_width: float = 0.025
    ):
        self.c4_base = float(c4_base)
        self.a_def = float(a_def)
        self.a_ast = float(a_ast)
        self.a_coma = float(a_coma)
        self.c11_base = float(c11_base)

        self.stamp_size = stamp_size
        self.subpixel_factor = subpixel_factor
        self.sampling_s = float(sampling_s)

        self.pupil = SpaceOpticsPupil(
            n_pupil=n_pupil,
            obscuration_ratio=obscuration_ratio,
            strut_width=strut_width
        )
        self.mft = MatrixFourierTransform(
            n_pupil=n_pupil,
            stamp_size=stamp_size,
            subpixel_factor=subpixel_factor,
            sampling_s=sampling_s
        )

    def eval_parameters(self, positions: np.ndarray) -> dict[str, np.ndarray]:
        """Evaluate aberration coefficient fields at coordinate array of shape (N, 2)."""
        pos = np.asarray(positions, dtype=np.float64)
        dx = pos[:, 0] - 0.5
        dy = pos[:, 1] - 0.5
        r2 = dx**2 + dy**2

        c4 = self.c4_base + self.a_def * r2
        c5 = 2.0 * self.a_ast * dx * dy
        c6 = self.a_ast * (dx**2 - dy**2)
        c7 = self.a_coma * dx
        c8 = self.a_coma * dy
        c11 = np.full(len(pos), self.c11_base, dtype=np.float64)

        return {
            "c4_defocus": c4,
            "c5_astig_oblique": c5,
            "c6_astig_vertical": c6,
            "c7_coma_x": c7,
            "c8_coma_y": c8,
            "c11_spherical": c11,
            # For compatibility with moment diagnostic loaders
            "fwhm": np.full(len(pos), self.sampling_s, dtype=np.float64),
            "e1": c6 * 0.5,
            "e2": c5 * 0.5
        }

    def generate_psf(
        self,
        x: float,
        y: float,
        stamp_size: int = 48,
        subpixel_factor: int = 4
    ) -> np.ndarray:
        """Deterministic PSF generation at position (x, y)."""
        p = self.eval_parameters(np.array([[x, y]], dtype=np.float64))
        wf = self.pupil.compute_wavefront(
            c4=float(p["c4_defocus"][0]),
            c5=float(p["c5_astig_oblique"][0]),
            c6=float(p["c6_astig_vertical"][0]),
            c7=float(p["c7_coma_x"][0]),
            c8=float(p["c8_coma_y"][0]),
            c11=float(p["c11_spherical"][0])
        )
        return self.mft.transform(wf)

    def generate_psf_batch(
        self,
        positions: np.ndarray,
        stamp_size: int = 48,
        subpixel_factor: int = 4
    ) -> np.ndarray:
        """Vectorized batch generation of PSFs for array of coordinates (N, 2)."""
        p = self.eval_parameters(positions)
        wf_stack = self.pupil.compute_wavefront_batch(
            c4=p["c4_defocus"],
            c5=p["c5_astig_oblique"],
            c6=p["c6_astig_vertical"],
            c7=p["c7_coma_x"],
            c8=p["c8_coma_y"],
            c11=p["c11_spherical"]
        )
        return self.mft.transform(wf_stack)
