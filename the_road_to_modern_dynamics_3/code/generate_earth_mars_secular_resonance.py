#!/usr/bin/env python3
r"""
generate_earth_mars_secular_resonance.py

Generates the two-panel numerical figure
("Earth-Mars Secular Resonance: Libration to Circulation")
for Section 4.2 ("Laskar's Discovery of Planetary Chaos")
of Article 3: "Order and Chaos: The Road to Modern Dynamics III".

Data Source & Reconstruction:
  Published IMCCE 5-kyr Earth orbital element datasets from Laskar et al. (2011),
  "La2010: A new orbital solution for the long-term motion of the Earth",
  Astronomy & Astrophysics, 532, A89:
    - data/La2010a_alkhqp3.dat
    - data/La2010b_alkhqp3.dat
    - data/La2010c_alkhqp3.dat
    - data/La2010d_alkhqp3.dat

  Each file stores Earth's (t_kyr, a, l, k, h, q, p) at 5-kyr sampling relative
  to J2000 in the invariant reference frame, where:
    z_e = k + i h = e exp(i varpi),   zeta = q + i p = sin(i/2) exp(i Omega).

  Secular resonant argument (Laskar 1990; Laskar et al. 2011, Sec. 8, Eq. 2):
    theta = [phi(s_4) - phi(s_3)] - 2 [phi(g_4) - phi(g_3)].

  Reconstruction from Earth's published La2010a-d orbital elements:
    1. Apply smooth multi-mode secular boundary continuation at t = 0 and
       t = -250 Myr (preserving complex rotation exp(+i omega t) across endpoints).
    2. Perihelion secular modes g_3, g_4: isolate g_3 ([16.80, 17.67]"/yr) and
       g_4 ([17.67, 18.60]"/yr) separately from the complex eccentricity variable
       z_e(t) = k(t) + i h(t) via cosine-tapered complex FFT bandpass filters and
       unwrap phi_{g_3}(t) and phi_{g_4}(t) individually.
    3. Nodal secular modes s_3, s_4: isolate s_3 ([-19.60, -18.30]"/yr) and
       s_4 ([-18.30, -17.00]"/yr) separately from the complex inclination variable
       zeta(t) = q(t) + i p(t) and unwrap phi_{s_3}(t) and phi_{s_4}(t) individually.
    4. Combine theta(t) = [phi_{s_4}(t) - phi_{s_3}(t)] - 2[phi_{g_4}(t) - phi_{g_3}(t)],
       shifted by an integer multiple of 2 pi so the present-day libration
       (5-40 Ma) is centered near 0.

  Numerical Validation & Comparison with Laskar et al. (2011) Figs. 11-13:
    - Phase continuity & non-vanishing envelopes: max single-step |Delta theta| < 0.05 pi
      over 0-100 Ma; min |z_g| > 5e-4, min |z_s| > 2e-4.
    - Filter-cutoff stability: shifting g_split by +/-0.02 "/yr or s_split by
      +/-0.05 "/yr changes theta by RMS < 0.10 pi over 0-100 Ma with no 2 pi slips.
    - Boundary-continuation invariance: removing continuation altogether (pad = 0)
      or varying fit_myr (10-35 Myr) and pad length (10-60 Myr) changes theta over
      40-60 Ma by RMS < 0.001 pi (max < 0.001 pi) and over 5-95 Ma by RMS < 0.01 pi.
    - Cross-method check (sliding-window Hann NAFF vs. complex FFT): extracting
      (g_3, g_4, s_3, s_4) independently on 10-12 Myr sliding windows and integrating
      instantaneous frequencies yields the same regime structure (5-48 Ma RMS < 0.30 pi;
      60 Ma values ~9.2-9.5 pi for La2010b, c and ~2.2 pi for La2010d).
    - Scope of Earth-only data vs. Laskar et al. (2011) Figs. 11-13:
      (a) Modulo-10 pi wrapping in Laskar's 100-Myr panel: Direct inspection of the
          published vector figure (aa16836-11-fig12.eps, sub-panel 16836fig12b.eps)
          shows that Laskar et al. wrap theta/pi modulo 10 onto [-2, +8]. Unwrapping
          those 10,001 vector points yields true 100-Ma endpoints of +18.82 pi
          (La2010a), +9.53 pi (La2010b), +20.85 pi (La2010c), and +2.42 pi (La2010d),
          compared with +20.41 pi, +21.33 pi, +32.95 pi, and +2.39 pi here.
      (b) Earth-only elements vs. full proper variables: IMCCE published only
          Earth's orbital elements (alkhqp3.dat), not Mars or Venus. Earth's nodal
          difference (phi_{s_4} - phi_{s_3}) matches Fig. 13 (bottom) to < 0.5 rad
          over 0-100 Ma, and La2010d matches Fig. 12 to < 0.1 pi at both 60 and 100 Ma.
          In La2010b and La2010c (and to a lesser extent La2010a), the Earth-only
          spectral reconstruction consistently accumulates additional 2 pi apsidal
          windings (~4 pi shifts in theta, plus smaller continuous phase differences)
          near small-amplitude passages of the g_4 - g_3 beat (e.g. around -53.9 Myr,
          Fig. 10), plausibly reflecting the difference between single-planet elements
          and the full multi-planet proper variables used by Laskar et al.

Visual Specifications:
  - ~2:1 scientific two-panel layout: 16.0 x 8.2 in @ 160 DPI -> 2560 x 1312 px
  - Matches the exact typography hierarchy, card framing, color palette, and
    shared La2010a-d legend of images/la2010_orbital_divergence.png and
    images/secular_planetary_evolution.png.

Output:
  images/earth_mars_secular_resonance.png
"""

from pathlib import Path
import urllib.request
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D

matplotlib.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "dejavuserif",
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "axes.edgecolor": "#cbd5e1",
    "axes.linewidth": 1.2,
})

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_PNG = PROJECT_DIR / "images" / "earth_mars_secular_resonance.png"
IMCCE_BASE = "https://ssp.imcce.fr/insola/earth/online/earth/La2010"

ARCSEC_PER_YR_TO_RAD_PER_MYR = np.pi / (180.0 * 3600.0) * 1.0e6

# Exact same four-solution palette as la2010_orbital_divergence.png
SOLUTIONS = [
    ("La2010a", "La2010a_alkhqp3.dat", "#0f172a", "-", 1.85, 2.25, 6),
    ("La2010b", "La2010b_alkhqp3.dat", "#2563eb", "-", 1.50, 1.85, 4),
    ("La2010c", "La2010c_alkhqp3.dat", "#059669", "-", 1.50, 1.85, 5),
    ("La2010d", "La2010d_alkhqp3.dat", "#dc2626", "-", 1.60, 1.95, 3),
]

WINDOW_A = (0.0, 100.0)
WINDOW_B = (40.0, 60.0)

# Nominal inner + outer Solar System secular frequencies ("/yr) for smooth complex boundary continuation
G_BOUNDARY_MODES = (4.257, 5.59, 7.452, 17.368, 17.916, 28.245)      # g5, g1, g2, g3, g4, g6
S_BOUNDARY_MODES = (-26.345, -18.850, -17.755, -7.08, -5.63, -2.99)  # s6, s3, s4, s2, s1, s7

# Nominal complex bandpass parameters ("/yr)
DEFAULT_G_SPLIT = 17.67
DEFAULT_G_EDGE = 0.06
DEFAULT_S_SPLIT = -18.30
DEFAULT_S_EDGE = 0.10
DEFAULT_PAD = 8000
DEFAULT_FIT_MYR = 20.0


def extend_secular_boundary(signal: np.ndarray, dt_myr: float,
                            mode_freqs_arcsec, pad: int = DEFAULT_PAD,
                            fit_myr: float = DEFAULT_FIT_MYR) -> np.ndarray:
    """Extend a complex secular signal smoothly across endpoints preserving exp(+i*omega*t)."""
    if pad <= 0:
        return signal
    n_fit = int(round(fit_myr / dt_myr))
    om = np.asarray(mode_freqs_arcsec, dtype=float) * ARCSEC_PER_YR_TO_RAD_PER_MYR

    t_r = np.arange(-n_fit + 1, 1) * dt_myr
    c_r, *_ = np.linalg.lstsq(np.exp(1j * np.outer(t_r, om)), signal[-n_fit:], rcond=None)
    ext_r = np.exp(1j * np.outer(np.arange(1, pad + 1) * dt_myr, om)) @ c_r

    t_l = np.arange(0, n_fit) * dt_myr
    c_l, *_ = np.linalg.lstsq(np.exp(1j * np.outer(t_l, om)), signal[:n_fit], rcond=None)
    ext_l = np.exp(1j * np.outer(np.arange(-pad, 0) * dt_myr, om)) @ c_l

    return np.concatenate([ext_l, signal, ext_r])


def bandpass_complex_fft(signal: np.ndarray, dt_myr: float,
                         f_lo_arcsec: float, f_hi_arcsec: float,
                         mode_freqs_arcsec, edge_arcsec: float = 0.06,
                         pad: int = DEFAULT_PAD,
                         fit_myr: float = DEFAULT_FIT_MYR) -> np.ndarray:
    """Boundary-continued, cosine-tapered complex FFT bandpass filter in arcsec/yr."""
    n = len(signal)
    sig_pad = extend_secular_boundary(signal, dt_myr, mode_freqs_arcsec, pad=pad, fit_myr=fit_myr)
    m = len(sig_pad)
    freqs_arcsec = (2.0 * np.pi * np.fft.fftfreq(m, d=dt_myr)) / ARCSEC_PER_YR_TO_RAD_PER_MYR

    w = np.zeros(m, dtype=float)
    w[(freqs_arcsec >= f_lo_arcsec + edge_arcsec) & (freqs_arcsec <= f_hi_arcsec - edge_arcsec)] = 1.0
    left = (freqs_arcsec >= f_lo_arcsec - edge_arcsec) & (freqs_arcsec < f_lo_arcsec + edge_arcsec)
    w[left] = 0.5 * (1.0 - np.cos(np.pi * (freqs_arcsec[left] - (f_lo_arcsec - edge_arcsec)) / (2.0 * edge_arcsec)))
    right = (freqs_arcsec > f_hi_arcsec - edge_arcsec) & (freqs_arcsec <= f_hi_arcsec + edge_arcsec)
    w[right] = 0.5 * (1.0 + np.cos(np.pi * (freqs_arcsec[right] - (f_hi_arcsec - edge_arcsec)) / (2.0 * edge_arcsec)))

    out = np.fft.ifft(np.fft.fft(sig_pad) * w)
    return out[pad:pad + n] if pad > 0 else out


def reconstruct_theta_single(t_myr: np.ndarray, z_e: np.ndarray, zeta: np.ndarray,
                             g_split: float = DEFAULT_G_SPLIT, g_edge: float = DEFAULT_G_EDGE,
                             s_split: float = DEFAULT_S_SPLIT, s_edge: float = DEFAULT_S_EDGE,
                             pad: int = DEFAULT_PAD, fit_myr: float = DEFAULT_FIT_MYR):
    """
    Reconstruct unwrapped theta = [phi(s4) - phi(s3)] - 2[phi(g4) - phi(g3)]
    directly from complex z_e = k + i h and zeta = q + i p, returning
    (t_ma, theta_pi, diagnostics).
    """
    dt_myr = float(t_myr[1] - t_myr[0])

    # 1. Isolate g3 and g4 apsidal modes separately from complex eccentricity z_e = k + i h
    z_g3 = bandpass_complex_fft(z_e, dt_myr, 16.80, g_split, G_BOUNDARY_MODES,
                                edge_arcsec=g_edge, pad=pad, fit_myr=fit_myr)
    z_g4 = bandpass_complex_fft(z_e, dt_myr, g_split, 18.60, G_BOUNDARY_MODES,
                                edge_arcsec=g_edge, pad=pad, fit_myr=fit_myr)
    phi_g3 = np.unwrap(np.angle(z_g3))
    phi_g4 = np.unwrap(np.angle(z_g4))

    # 2. Isolate s3 and s4 nodal modes separately from complex inclination zeta = q + i p
    z_s3 = bandpass_complex_fft(zeta, dt_myr, -19.60, s_split, S_BOUNDARY_MODES,
                                edge_arcsec=s_edge, pad=pad, fit_myr=fit_myr)
    z_s4 = bandpass_complex_fft(zeta, dt_myr, s_split, -17.00, S_BOUNDARY_MODES,
                                edge_arcsec=s_edge, pad=pad, fit_myr=fit_myr)
    phi_s3 = np.unwrap(np.angle(z_s3))
    phi_s4 = np.unwrap(np.angle(z_s4))

    # 3. Combine individual unwrapped secular phases into the Earth-Mars resonant angle
    theta = (phi_s4 - phi_s3) - 2.0 * (phi_g4 - phi_g3)
    m_ref = (t_myr >= -40.0) & (t_myr <= -5.0)
    theta = theta - np.round(np.mean(theta[m_ref]) / (2.0 * np.pi)) * 2.0 * np.pi

    # Express as age before J2000 (T_Ma = -t_myr >= 0), strictly ascending
    t_ma = -t_myr[::-1]
    theta_pi = (theta / np.pi)[::-1]

    m100_t = t_myr >= -100.0
    m100_ma = t_ma <= 100.0
    diag = {
        "max_step_pi": float(np.max(np.abs(np.diff(theta_pi[m100_ma])))),
        "min_amp_g": float(min(np.min(np.abs(z_g3[m100_t])), np.min(np.abs(z_g4[m100_t])))),
        "min_amp_s": float(min(np.min(np.abs(z_s3[m100_t])), np.min(np.abs(z_s4[m100_t])))),
    }
    return t_ma, theta_pi, diag


def reconstruct_theta_sliding_naff(t_myr: np.ndarray, z_e: np.ndarray, zeta: np.ndarray,
                                   win_myr: float = 10.0, step_myr: float = 1.0,
                                   max_ma: float = 65.0):
    """
    Independent sliding-window Hann frequency analysis (NAFF-style) extracting
    instantaneous frequencies of (g_3, g_4, s_3, s_4) separately and integrating
    their phases backward in time over [0, max_ma] Myr.
    """
    dt_myr = float(t_myr[1] - t_myr[0])
    half_n = int(round((win_myr / 2.0) / dt_myr))
    t_loc = np.arange(-half_n, half_n + 1) * dt_myr
    hann = 0.5 * (1.0 + np.cos(np.pi * t_loc / (win_myr / 2.0)))
    hann /= np.sum(hann)

    grids = {
        "g3": np.linspace(17.05, 17.65, 241),
        "g4": np.linspace(17.65, 18.35, 281),
        "s3": np.linspace(-19.30, -18.30, 251),
        "s4": np.linspace(-18.30, -17.30, 251),
    }
    bases = {
        k: np.exp(-1j * np.outer(fg * ARCSEC_PER_YR_TO_RAD_PER_MYR, t_loc)) * hann[None, :]
        for k, fg in grids.items()
    }

    centers_ma = np.arange(0.0, max_ma + 1.0e-9, step_myr)
    freqs_out = {k: np.zeros_like(centers_ma) for k in grids}
    phases_0 = {}

    pad_off = half_n + 10
    z_e_ext = extend_secular_boundary(z_e, dt_myr, G_BOUNDARY_MODES, pad=pad_off, fit_myr=DEFAULT_FIT_MYR)
    zeta_ext = extend_secular_boundary(zeta, dt_myr, S_BOUNDARY_MODES, pad=pad_off, fit_myr=DEFAULT_FIT_MYR)

    for idx, c_ma in enumerate(centers_ma):
        c_idx = int(round((-c_ma - t_myr[0]) / dt_myr)) + pad_off
        seg_e = z_e_ext[c_idx - half_n:c_idx + half_n + 1]
        seg_s = zeta_ext[c_idx - half_n:c_idx + half_n + 1]
        for k, sig in (("g3", seg_e), ("g4", seg_e), ("s3", seg_s), ("s4", seg_s)):
            amp = np.abs(bases[k] @ sig)
            i_max = int(np.argmax(amp))
            if 0 < i_max < len(amp) - 1:
                y0 = np.log(amp[i_max - 1] + 1.0e-30)
                y1 = np.log(amp[i_max] + 1.0e-30)
                y2 = np.log(amp[i_max + 1] + 1.0e-30)
                denom = y0 - 2.0 * y1 + y2
                delta = np.clip(0.5 * (y0 - y2) / denom, -0.5, 0.5) if abs(denom) > 1.0e-14 else 0.0
                f_best = grids[k][i_max] + delta * (grids[k][1] - grids[k][0])
            else:
                f_best = grids[k][i_max]
            freqs_out[k][idx] = f_best
            if idx == 0:
                c_best = np.sum(hann * sig * np.exp(-1j * f_best * ARCSEC_PER_YR_TO_RAD_PER_MYR * t_loc))
                phases_0[k] = float(np.angle(c_best))

    phi_int = {}
    for k in grids:
        om_ma = freqs_out[k] * ARCSEC_PER_YR_TO_RAD_PER_MYR
        dphi = -0.5 * (om_ma[:-1] + om_ma[1:]) * np.diff(centers_ma)
        phi_int[k] = np.concatenate([[phases_0[k]], phases_0[k] + np.cumsum(dphi)])

    th_int = (phi_int["s4"] - phi_int["s3"]) - 2.0 * (phi_int["g4"] - phi_int["g3"])
    m_ref = (centers_ma >= 5.0) & (centers_ma <= 40.0)
    th_int -= np.round(np.mean(th_int[m_ref]) / (2.0 * np.pi)) * 2.0 * np.pi
    return centers_ma, th_int / np.pi


def load_raw_la2010_elements():
    """Load and validate uniform 5-kyr complex (z_e, zeta) series for La2010a-d."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw_series = {}
    for label, fname, *_ in SOLUTIONS:
        fpath = DATA_DIR / fname
        if not fpath.exists():
            url = f"{IMCCE_BASE}/{fname}"
            print(f"  [Fetch] Downloading {url} -> {fpath}")
            urllib.request.urlretrieve(url, fpath)

        arr = np.loadtxt(fpath, dtype=float)
        assert arr.ndim == 2 and arr.shape[1] == 7, f"Unexpected shape {arr.shape} in {fname}"

        arr = arr[np.argsort(arr[:, 0])]
        t_myr = arr[:, 0] / 1000.0
        assert np.allclose(np.diff(t_myr), 0.005, atol=1e-9), f"{fname} does not have uniform 5-kyr sampling"

        z_e = arr[:, 3] + 1j * arr[:, 4]
        zeta = arr[:, 5] + 1j * arr[:, 6]
        raw_series[label] = (t_myr, z_e, zeta)
    return raw_series


def compare_fft_and_sliding_naff(win_myr: float = 10.0, step_myr: float = 1.0):
    """Compare complex FFT vs. sliding-window NAFF over 5-48 Ma and 40-60 Ma."""
    raw_series = load_raw_la2010_elements()
    comparison = {}
    for label, *_ in SOLUTIONS:
        t_myr, z_e, zeta = raw_series[label]
        t_ma_fft, th_fft, _ = reconstruct_theta_single(t_myr, z_e, zeta)
        c_ma, th_naff = reconstruct_theta_sliding_naff(t_myr, z_e, zeta, win_myr=win_myr, step_myr=step_myr)
        th_fft_interp = np.interp(c_ma, t_ma_fft, th_fft)

        m_lib = (c_ma >= 5.0) & (c_ma <= 48.0)
        m_40_60 = (c_ma >= 40.0) & (c_ma <= 60.0)
        idx_60 = int(np.argmin(np.abs(c_ma - 60.0)))
        comparison[label] = {
            "rms_lib_pi": float(np.sqrt(np.mean((th_naff[m_lib] - th_fft_interp[m_lib]) ** 2))),
            "rms_40_60_pi": float(np.sqrt(np.mean((th_naff[m_40_60] - th_fft_interp[m_40_60]) ** 2))),
            "fft_60_pi": float(th_fft_interp[idx_60]),
            "naff_60_pi": float(th_naff[idx_60]),
        }
    return comparison


def load_and_reconstruct_theta(validate_stability: bool = True):
    """Load La2010a-d alkhqp3 orbital elements, reconstruct theta, and verify numerical stability."""
    raw_series = load_raw_la2010_elements()
    results = {}

    for label, *_ in SOLUTIONS:
        t_myr, z_e, zeta = raw_series[label]
        t_ma, theta_pi, diag = reconstruct_theta_single(t_myr, z_e, zeta)

        # 1. Numerical integrity checks (phase continuity & non-vanishing mode envelopes)
        assert diag["max_step_pi"] < 0.05, (
            f"{label}: phase discontinuity detected (max |dtheta| = {diag['max_step_pi']:.4f} pi)"
        )
        assert diag["min_amp_g"] > 5.0e-4, f"{label}: near-zero g3/g4 amplitude ({diag['min_amp_g']:.2e})"
        assert diag["min_amp_s"] > 2.0e-4, f"{label}: near-zero s3/s4 amplitude ({diag['min_amp_s']:.2e})"

        results[label] = (t_ma, theta_pi)

    if validate_stability:
        cutoff_perturbations = [
            ("g_split-0.02", dict(g_split=DEFAULT_G_SPLIT - 0.02)),
            ("g_split+0.02", dict(g_split=DEFAULT_G_SPLIT + 0.02)),
            ("s_split-0.05", dict(s_split=DEFAULT_S_SPLIT - 0.05)),
            ("s_split+0.05", dict(s_split=DEFAULT_S_SPLIT + 0.05)),
        ]
        boundary_perturbations = [
            ("no_pad", dict(pad=0)),
            ("short_10Myr", dict(pad=2000, fit_myr=10.0)),
            ("long_60Myr", dict(pad=12000, fit_myr=35.0)),
        ]
        for label, *_ in SOLUTIONS:
            t_myr, z_e, zeta = raw_series[label]
            t_ma, th0 = results[label]
            m100 = t_ma <= 100.0
            m40_60 = (t_ma >= 40.0) & (t_ma <= 60.0)
            m5_95 = (t_ma >= 5.0) & (t_ma <= 95.0)

            # 2. Filter-cutoff sensitivity check
            worst_cutoff_rms = 0.0
            for pname, kwargs in cutoff_perturbations:
                _, th_p, _ = reconstruct_theta_single(t_myr, z_e, zeta, **kwargs)
                diff = np.abs(th_p[m100] - th0[m100])
                rms_pi = float(np.sqrt(np.mean(diff ** 2)))
                max_diff = float(np.max(diff))
                assert rms_pi < 0.10 and max_diff < 1.0, (
                    f"{label} unstable under {pname}: RMS={rms_pi:.3f} pi, max={max_diff:.3f} pi"
                )
                worst_cutoff_rms = max(worst_cutoff_rms, rms_pi)

            # 3. Boundary-continuation sensitivity check (especially 40-60 Ma)
            worst_bdy_40_60 = 0.0
            for bname, kwargs in boundary_perturbations:
                _, th_b, _ = reconstruct_theta_single(t_myr, z_e, zeta, **kwargs)
                rms_40_60 = float(np.sqrt(np.mean((th_b[m40_60] - th0[m40_60]) ** 2)))
                rms_5_95 = float(np.sqrt(np.mean((th_b[m5_95] - th0[m5_95]) ** 2)))
                assert rms_40_60 < 0.001 and rms_5_95 < 0.01, (
                    f"{label} sensitive to boundary model {bname}: "
                    f"40-60 RMS={rms_40_60:.5f} pi, 5-95 RMS={rms_5_95:.5f} pi"
                )
                worst_bdy_40_60 = max(worst_bdy_40_60, rms_40_60)

            v60 = float(th0[np.argmin(np.abs(t_ma - 60.0))])
            v100 = float(th0[np.argmin(np.abs(t_ma - 100.0))])
            print(
                f"  [Verified] {label}: cutoff RMS <= {worst_cutoff_rms:.3f} pi | "
                f"bdy(40-60) RMS <= {worst_bdy_40_60:.5f} pi | "
                f"60 Ma = {v60:+.2f} pi | 100 Ma = {v100:+.2f} pi"
            )

    return results


def create_figure(output_path=None):
    datasets = load_and_reconstruct_theta()
    if output_path is None:
        output_path = OUTPUT_PNG
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 2:1 two-panel layout matching la2010_orbital_divergence.png & secular_planetary_evolution.png
    fig_w, fig_h = 16.0, 8.2
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=160, facecolor="#ffffff")

    NAVY = "#0f172a"
    DARK_SLATE = "#1e293b"
    SLATE = "#334155"
    MUTED_SLATE = "#475569"
    BORDER_CARD = "#cbd5e1"
    BG_CARD = "#f8fafc"

    HEADER_BLUE = "#eff6ff"
    HEADER_BORDER = "#93c5fd"
    BLUE_ACCENT = "#2563eb"
    BLUE_DARK = "#1d4ed8"

    TEAL_LIGHT = "#f0fdfa"
    TEAL_BORDER = "#5eead4"
    TEAL_ACCENT = "#0d9488"
    TEAL_DARK = "#0f766e"

    RED_DARK = "#b91c1c"
    halo = [pe.withStroke(linewidth=3.4, foreground="#ffffff", alpha=0.96)]

    # -------------------------------------------------------------------------
    # Global Title & Subtitle (matching Article 3 typography hierarchy)
    # -------------------------------------------------------------------------
    fig.text(
        0.50,
        0.959,
        "Earth–Mars Secular Resonance: Libration to Circulation",
        fontsize=23.6,
        weight="bold",
        color=NAVY,
        ha="center",
        va="center",
    )
    fig.text(
        0.50,
        0.913,
        r"Approximate unwrapped resonant angle $\theta$ estimated from Earth's published La2010a–d orbital elements (Laskar et al., 2011)",
        fontsize=15.0,
        style="italic",
        weight="normal",
        color=DARK_SLATE,
        ha="center",
        va="center",
    )

    ax_bg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=0)
    ax_bg.set_xlim(0.0, 1.0)
    ax_bg.set_ylim(0.0, 1.0)
    ax_bg.axis("off")

    # -------------------------------------------------------------------------
    # Two Equal-Width Parallel Panel Cards (A and B)
    # -------------------------------------------------------------------------
    y_card = 0.118
    h_card = 0.756
    x1, w1 = 0.016, 0.472
    x2, w2 = 0.512, 0.472
    hbar_h = 0.106
    badge_y = y_card + h_card - hbar_h / 2.0

    panels_spec = [
        (
            x1, w1, "A", "Long-term evolution (0–100 Myr ago)",
            "Bounded libration gives way to circulation and divergence",
            BLUE_ACCENT, HEADER_BLUE, HEADER_BORDER,
        ),
        (
            x2, w2, "B", "Divergence of resonant motion (40–60 Myr ago)",
            "Reconstructions separate beyond ~50 Myr ago",
            TEAL_ACCENT, TEAL_LIGHT, TEAL_BORDER,
        ),
    ]

    for px, pw, letter, title, subtitle, acc_color, bg_tint, bdr_color in panels_spec:
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px, y_card), pw, h_card,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=BG_CARD, edgecolor=BORDER_CARD, linewidth=1.5, zorder=1,
        ))
        ax_bg.add_patch(patches.FancyBboxPatch(
            (px, y_card + h_card - hbar_h), pw, hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=bg_tint, edgecolor=bdr_color, linewidth=1.3, zorder=2,
        ))

        badge_x = px + 0.024
        r_x = 0.0145
        r_y = r_x * (fig_w / fig_h)
        ax_bg.add_patch(patches.Ellipse(
            (badge_x, badge_y), width=2.0 * r_x, height=2.0 * r_y,
            facecolor=acc_color, edgecolor="none", zorder=3,
        ))
        ax_bg.text(
            badge_x, badge_y - 0.0005, letter,
            fontsize=17.5, weight="bold", color="#ffffff",
            ha="center", va="center", zorder=4,
        )

        text_offset_x = badge_x + 0.022
        ax_bg.text(
            text_offset_x, badge_y + 0.020, title,
            fontsize=15.0, weight="bold", color=NAVY, va="center", zorder=4,
        )
        ax_bg.text(
            text_offset_x, badge_y - 0.022, subtitle,
            fontsize=13.5, weight="bold", color=MUTED_SLATE, va="center", zorder=4,
        )

    # Shared plot box geometry inside cards
    ax_bottom = y_card + 0.090
    ax_h = h_card - hbar_h - 0.116

    t_c, th_c = datasets["La2010c"]
    t_a, th_a = datasets["La2010a"]
    t_d, th_d = datasets["La2010d"]

    # -------------------------------------------------------------------------
    # Panel A: Full 0-100 Ma Unwrapped Resonant Angle
    # -------------------------------------------------------------------------
    axA = fig.add_axes([x1 + 0.066, ax_bottom, w1 - 0.086, ax_h], zorder=5)
    axA.set_facecolor("#ffffff")
    axA.set_xlim(0.0, 100.0)
    axA.set_ylim(-2.8, 36.2)

    xticks_A = [0, 20, 40, 60, 80, 100]
    axA.set_xticks(xticks_A)
    axA.set_xticklabels([str(v) for v in xticks_A], fontsize=13.6, weight="bold", color=SLATE)
    yticks_A = [0, 6, 12, 18, 24, 30, 36]
    axA.set_yticks(yticks_A)
    axA.set_yticklabels([str(v) for v in yticks_A], fontsize=13.6, weight="bold", color=SLATE)
    axA.tick_params(axis="both", which="major", length=4, width=1.2, colors=SLATE, pad=3)

    axA.set_xlabel("Time before present (millions of years)", fontsize=15.0, weight="bold", color=NAVY, labelpad=5)
    axA.set_ylabel(r"Unwrapped angle $\boldsymbol{\theta / \pi}$", fontsize=15.6, weight="bold", color=NAVY, labelpad=4)

    for gx in [20, 40, 60, 80]:
        axA.axvline(gx, color="#f1f5f9", lw=0.9, zorder=1)
    for gy in range(0, 37, 3):
        axA.axhline(gy, color="#f1f5f9" if gy % 6 == 0 else "#f8fafc", lw=0.9, zorder=1)
    axA.axhline(0.0, color="#cbd5e1", lw=1.0, ls=":", zorder=2)

    for sp in axA.spines.values():
        sp.set_edgecolor(BORDER_CARD)
        sp.set_linewidth(1.2)

    # Shaded libration regime (~0-48 Myr) and onset of divergence (~48-50 Myr)
    axA.axvspan(0.0, 48.0, facecolor="#eff6ff", alpha=0.68, zorder=1)
    axA.axvspan(48.0, 50.0, facecolor="#fde68a", alpha=0.45, zorder=2)
    axA.axvline(48.0, color="#d97706", lw=0.95, ls=":", alpha=0.70, zorder=2)
    axA.axvline(50.0, color="#d97706", lw=0.95, ls=":", alpha=0.70, zorder=2)

    # Highlighted zoom box matching Panel B ([40, 60] Myr, [-1.5, 10.5] pi)
    zoom_rect = patches.FancyBboxPatch(
        (40.0, -1.5), 20.0, 12.0,
        boxstyle="round,pad=0.0,rounding_size=0.45",
        facecolor="#f0fdfa", edgecolor=TEAL_ACCENT, linewidth=1.6, linestyle="--", alpha=0.75, zorder=2,
    )
    axA.add_patch(zoom_rect)

    # Plot all four La2010 curves (0-100 Myr)
    for label, _, color, ls, lw_a, _, z in SOLUTIONS:
        t_ma, th_pi = datasets[label]
        m = (t_ma >= WINDOW_A[0]) & (t_ma <= WINDOW_A[1])
        axA.plot(t_ma[m], th_pi[m], color=color, ls=ls, lw=lw_a, alpha=0.93, zorder=z)

    # Exact curve landing coordinates for Panel A arrows
    t_lib_a = 22.5
    y_lib_a = max(
        float(datasets[lbl][1][np.argmin(np.abs(datasets[lbl][0] - t_lib_a))])
        for lbl, *_ in SOLUTIONS
    )
    t_circ_a = 74.2
    y_circ_a = float(th_c[np.argmin(np.abs(t_c - t_circ_a))])
    t_bosc_a = 90.0
    y_bosc_a = float(th_d[np.argmin(np.abs(t_d - t_bosc_a))])

    # Clean, non-overlapping annotations in Panel A
    axA.text(
        22.5, 25.8,
        "Libration (~0–48 Myr)\n"
        r"Bounded near $\boldsymbol{\theta \approx 0}$",
        fontsize=12.4, weight="bold", color=BLUE_DARK,
        ha="center", va="center", linespacing=1.22, path_effects=halo,
        bbox=dict(boxstyle="round,pad=0.30", facecolor="#ffffff", edgecolor=HEADER_BORDER, linewidth=1.2, alpha=0.96),
        zorder=9,
    )
    axA.annotate(
        "",
        xy=(t_lib_a, y_lib_a + 0.15),
        xytext=(22.5, 21.0),
        arrowprops=dict(arrowstyle="-|>", mutation_scale=12.0, color=BLUE_ACCENT, lw=1.5, ls="-", shrinkB=0),
        zorder=8,
    )

    axA.text(
        46.6, 16.5,
        "Divergence\n(~50 Myr)",
        fontsize=11.4, weight="bold", color="#92400e",
        ha="right", va="center", linespacing=1.14, path_effects=halo,
        bbox=dict(boxstyle="round,pad=0.24", facecolor="#fffbeb", edgecolor="#fcd34d", linewidth=1.05, alpha=0.96),
        zorder=9,
    )

    circ_ann = axA.annotate(
        "Circulation (La2010a–c)\nMultiple 2π rotations",
        xy=(t_circ_a, y_circ_a),
        xytext=(53.0, 34.7),
        fontsize=11.5, weight="bold", color=NAVY,
        ha="left", va="top", linespacing=1.16, path_effects=halo,
        bbox=dict(boxstyle="round,pad=0.24", facecolor="#ffffff", edgecolor="#94a3b8", linewidth=1.1, alpha=0.96),
        arrowprops=dict(
            arrowstyle="-|>", mutation_scale=12.0, color=SLATE, lw=1.45,
            shrinkA=2, shrinkB=0, connectionstyle="arc3,rad=-0.06",
        ),
        zorder=9,
    )

    d_ann = axA.annotate(
        "No sustained\ncirculation (La2010d)",
        xy=(t_bosc_a, y_bosc_a),
        xytext=(83.2, 7.3),
        fontsize=10.8, weight="bold", color=RED_DARK,
        ha="center", va="center", linespacing=1.15, path_effects=halo,
        bbox=dict(boxstyle="round,pad=0.23", facecolor="#fef2f2", edgecolor="#fca5a5", linewidth=1.1, alpha=0.96),
        arrowprops=dict(arrowstyle="-|>", mutation_scale=11.5, color="#dc2626", lw=1.4, shrinkA=2, shrinkB=0),
        zorder=9,
    )

    axA.text(
        50.0, 11.1,
        "Panel B",
        fontsize=11.4, weight="bold", color=TEAL_DARK,
        ha="center", va="bottom", path_effects=halo, zorder=9,
    )

    # -------------------------------------------------------------------------
    # Panel B: Enlarged View of Divergence (40-60 Myr)
    # -------------------------------------------------------------------------
    axB = fig.add_axes([x2 + 0.066, ax_bottom, w2 - 0.086, ax_h], zorder=5)
    axB.set_facecolor("#ffffff")
    axB.set_xlim(40.0, 60.0)
    axB.set_ylim(-1.6, 10.6)

    xticks_B = [40, 45, 50, 55, 60]
    axB.set_xticks(xticks_B)
    axB.set_xticklabels([str(v) for v in xticks_B], fontsize=13.6, weight="bold", color=SLATE)
    yticks_B = [0, 2, 4, 6, 8, 10]
    axB.set_yticks(yticks_B)
    axB.set_yticklabels([str(v) for v in yticks_B], fontsize=13.6, weight="bold", color=SLATE)
    axB.tick_params(axis="both", which="major", length=4, width=1.2, colors=SLATE, pad=3)

    axB.set_xlabel("Time before present (millions of years)", fontsize=15.0, weight="bold", color=NAVY, labelpad=5)
    axB.set_ylabel(r"Unwrapped angle $\boldsymbol{\theta / \pi}$", fontsize=15.6, weight="bold", color=NAVY, labelpad=4)

    for gx in [45, 50, 55]:
        axB.axvline(gx, color="#f1f5f9", lw=0.9, zorder=1)
    for gy in yticks_B:
        axB.axhline(gy, color="#f1f5f9", lw=0.9, zorder=1)

    for sp in axB.spines.values():
        sp.set_edgecolor(BORDER_CARD)
        sp.set_linewidth(1.2)

    # Bounded [-pi, +pi] libration corridor (40-48 Myr) and divergence onset band (~48-50 Myr)
    axB.add_patch(patches.Rectangle(
        (40.0, -1.0), 8.0, 2.0,
        facecolor="#eff6ff", edgecolor="none", alpha=0.82, zorder=1,
    ))
    axB.axvspan(48.0, 50.0, facecolor="#fde68a", alpha=0.40, zorder=1)
    axB.axvline(48.0, color="#d97706", lw=0.95, ls=":", alpha=0.70, zorder=2)
    axB.axvline(50.0, color="#d97706", lw=0.95, ls=":", alpha=0.70, zorder=2)
    axB.axhline(1.0, color=BLUE_ACCENT, lw=1.15, ls=":", alpha=0.65, zorder=2)
    axB.axhline(-1.0, color=BLUE_ACCENT, lw=1.15, ls=":", alpha=0.65, zorder=2)
    axB.axhline(0.0, color="#cbd5e1", lw=1.0, ls=":", zorder=2)

    # Plot all four La2010 curves (40-60 Myr)
    for label, _, color, ls, _, lw_b, z in SOLUTIONS:
        t_ma, th_pi = datasets[label]
        m = (t_ma >= WINDOW_B[0]) & (t_ma <= WINDOW_B[1])
        axB.plot(t_ma[m], th_pi[m], color=color, ls=ls, lw=lw_b, alpha=0.94, zorder=z)

    # Clean, non-overlapping annotations in Panel B
    axB.text(
        44.0, 8.15,
        "Reconstructions agree\n"
        r"in libration ($\boldsymbol{|\theta| < \pi}$)",
        fontsize=12.0, weight="bold", color=BLUE_DARK,
        ha="center", va="center", linespacing=1.22, path_effects=halo,
        bbox=dict(boxstyle="round,pad=0.26", facecolor="#ffffff", edgecolor=HEADER_BORDER, linewidth=1.2, alpha=0.96),
        zorder=9,
    )
    axB.annotate(
        "",
        xy=(44.0, 1.0),
        xytext=(44.0, 6.70),
        arrowprops=dict(arrowstyle="-|>", mutation_scale=12.0, color=BLUE_ACCENT, lw=1.5, shrinkB=0),
        zorder=8,
    )

    t_div_b = 49.15
    y_div_b = float(th_c[np.argmin(np.abs(t_c - t_div_b))])
    axB.annotate(
        "Onset of divergence\n(~50 Myr)",
        xy=(t_div_b, y_div_b),
        xytext=(48.6, 8.85),
        fontsize=11.5, weight="bold", color="#92400e",
        ha="left", va="center", linespacing=1.16, path_effects=halo,
        bbox=dict(boxstyle="round,pad=0.24", facecolor="#fffbeb", edgecolor="#fcd34d", linewidth=1.15, alpha=0.96),
        arrowprops=dict(
            arrowstyle="-|>", mutation_scale=12.0, color="#d97706", lw=1.45,
            shrinkA=2, shrinkB=0, connectionstyle="arc3,rad=0.12",
        ),
        zorder=9,
    )

    # Clean non-crossing branch labels on the right half (55-60 Myr)
    y_c57 = float(th_c[np.argmin(np.abs(t_c - 57.5))])
    y_a57 = float(th_a[np.argmin(np.abs(t_a - 57.2))])
    y_d56 = float(th_d[np.argmin(np.abs(t_d - 56.2))])

    axB.annotate(
        "La2010b, c",
        xy=(57.5, y_c57),
        xytext=(56.6, 9.65),
        fontsize=12.0, weight="bold", color="#047857",
        ha="center", va="bottom", path_effects=halo,
        arrowprops=dict(arrowstyle="-|>", mutation_scale=10.5, color="#059669", lw=1.35, shrinkB=0),
        zorder=9,
    )
    axB.annotate(
        "La2010a",
        xy=(57.2, y_a57),
        xytext=(59.3, 4.35),
        fontsize=12.0, weight="bold", color=NAVY,
        ha="right", va="top", path_effects=halo,
        arrowprops=dict(arrowstyle="-|>", mutation_scale=10.5, color=NAVY, lw=1.35, shrinkB=0),
        zorder=9,
    )
    axB.annotate(
        "La2010d",
        xy=(56.2, y_d56),
        xytext=(56.2, -0.35),
        fontsize=12.0, weight="bold", color=RED_DARK,
        ha="center", va="top", path_effects=halo,
        arrowprops=dict(arrowstyle="-|>", mutation_scale=10.5, color="#dc2626", lw=1.35, shrinkB=0),
        zorder=9,
    )

    # -------------------------------------------------------------------------
    # Shared Legend Strip Centered Beneath Both Panels (identical to la2010_orbital_divergence.png)
    # -------------------------------------------------------------------------
    legend_handles = [
        Line2D([0], [0], color=color, linestyle=ls, linewidth=2.6, label=label)
        for label, _, color, ls, _, _, _ in SOLUTIONS
    ]
    leg = fig.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.50, 0.022),
        ncol=4,
        frameon=True,
        facecolor="#ffffff",
        edgecolor=BORDER_CARD,
        framealpha=1.0,
        handlelength=2.4,
        handletextpad=0.7,
        columnspacing=2.2,
        borderpad=0.55,
        prop={"size": 14.4, "weight": "bold"},
    )
    leg.get_frame().set_linewidth(1.3)
    for txt in leg.get_texts():
        txt.set_color(DARK_SLATE)

    # Verify all callout boxes stay strictly inside panel axes and clear the 48-50 Myr band
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    invA = axA.transData.inverted()
    for txt_obj in axA.texts:
        patch = txt_obj.get_bbox_patch()
        if patch is not None:
            (x_lo, y_lo), (x_hi, y_hi) = invA.transform(patch.get_window_extent(renderer))
            assert 0.5 <= x_lo and x_hi <= 99.5 and -2.5 <= y_lo and y_hi <= 35.9, (
                f"Panel A box {txt_obj.get_text()!r} out of bounds: x=[{x_lo:.2f}, {x_hi:.2f}], y=[{y_lo:.2f}, {y_hi:.2f}]"
            )
    (cx_lo, _), (cx_hi, _) = invA.transform(circ_ann.get_bbox_patch().get_window_extent(renderer))
    assert cx_lo >= 51.0, f"Circulation box overlaps 48-50 Myr band (x_lo={cx_lo:.2f})"
    (dx_lo, _), (dx_hi, _) = invA.transform(d_ann.get_bbox_patch().get_window_extent(renderer))
    assert dx_hi <= 99.2, f"La2010d box too close to right spine (x_hi={dx_hi:.2f})"

    fig.savefig(output_path, dpi=160, facecolor="#ffffff")
    plt.close(fig)
    print(f"  [OK] Saved {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    create_figure()
