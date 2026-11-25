# Article Code Collections

Welcome! This repository hosts code implementations and clean, runnable models supporting technical articles published under the **Stellar Priors** and other publications.

## 📁 Repository Projects

Each folder inside this repository corresponds to a specific publication series:

### [Mastering Spatial Interpolation](geneva_spatial_interpolation/)
A 4-part series covering spatial interpolation methods:
- **Part 1**: Polynomials & B-Splines
- **Part 2**: Local Interpolation Models (NN, IDW & RBF)
- **Part 3**: Geostatistics & Kriging
- **Part 4**: Spatial Machine Learning

For setup and run instructions, please refer to the project [README](geneva_spatial_interpolation/README.md).

### [Validating Spatial Interpolation: Beyond LOOCV](validating_spatial_interpolation/)
Cross-validation protocols and spatial benchmark suite for spatial interpolation:
- Ground truth synthetic Geneva microclimate & irregularly sampled sensor network
- Spatial autocorrelation bias in standard random CV & Leave-One-Out (LOOCV)
- Spatial block holdout & quadrant-based extrapolation benchmarking
- Buffered Leave-One-Out cross-validation across varying exclusion radii
- Point process topology analysis (uniform random, clustered, transects, regular grids)
- First-principles NumPy/SciPy solvers (Polynomial surface, IDW, Thin-Plate Spline RBF, Ordinary Kriging)
- Empirical error degradation vs. distance to nearest observation station

For setup, reproduction benchmarks, and unit tests, please refer to the project [README](validating_spatial_interpolation/README.md).

### [The Discovery of the Hulse-Taylor Binary Pulsar](hulse_taylor_pulsar_discovery/)
First-principles physics models and visualization suite for PSR B1913+16:
- Pulsar lighthouse geometry & orbital Doppler modulation
- Historical 1974 Arecibo discovery logs & orbital turnaround
- 3D Keplerian orbital geometry & radial velocity curves
- Post-Keplerian mass-mass constraints ($\dot{\omega}$, $\gamma$)
- Gravitational radiation & cumulative orbital period decay ($\dot{P}_b$)

For setup, execution, and unit tests, please refer to the project [README](hulse_taylor_pulsar_discovery/README.md).

### [Beyond Kepler: Perturbations and the Stability of the Solar System](beyond_kepler_solar_system_stability/)
Celestial mechanics models and visualization suite for planetary perturbation theory:
- Instantaneous osculating orbit & two-timescale dynamical separation
- Heliocentric disturbing function geometry & 4-stage analytical progression
- Orbital phase averaging & the Solar System timescale hierarchy
- Regularized eccentricity vector $(k, h)$ in the complex plane
- Laplace-Lagrange secular eigenvalue theory & collective normal modes
- Resonant 5:2 commensurability & the Great Inequality of Jupiter and Saturn
- Classical stability criteria vs. nonlinear chaotic diffusion

For setup, execution, and unit tests, please refer to the project [README](beyond_kepler_solar_system_stability/README.md).

### [Navier–Stokes Blow-Up: Fluid Regularity and Vortex Dynamics](navier_stokes_blow_up/)
Mathematical models and visualization suite for fluid mechanics, regularity criteria, and blow-up dynamics:
- Eulerian local vs. Lagrangian convective acceleration & material derivative
- 3D vortex filament stretching, strain alignment, and core thinning
- 2D vorticity conservation & exact vanishing of vortex stretching
- Energy balance, viscous dissipation sink, and $L^2$ global bounds
- Finite kinetic energy concentration with divergent velocity gradients
- Navier–Stokes scaling symmetries, critical spaces, and $L^3$ critical threshold
- Anisotropic core contraction and singular blow-up architecture

For setup, execution, and unit tests, please refer to the project [README](navier_stokes_blow_up/README.md).

### [From Newton to Hamilton: The Road to Modern Dynamics](the_road_to_modern_dynamics/)
First-principles mathematical models and scientific visualization suite for analytical mechanics and Hamiltonian dynamics:
- Cartesian constraints vs. generalized coordinates & reduction of degrees of freedom
- Historical analytical mechanics synthesis (Euler, d'Alembert, and Lagrange)
- Multi-system taxonomy across 1D and 2D holonomic configuration spaces
- Lagrangian configuration space $TQ$ vs. Hamiltonian phase space $T^*Q$ via Legendre transformation
- Nonlinear pendulum phase space $(\theta, p_\theta)$: libration, rotation, and homoclinic separatrix
- Hamilton–Jacobi canonical theory & optical-mechanical wave analogy (Hamilton & Jacobi)
- Celestial perturbation limits and the transition to Poincaré's qualitative dynamics

For setup, execution, and unit tests, please refer to the project [README](the_road_to_modern_dynamics/README.md).

### [From Poincaré to Chaos: The Road to Modern Dynamics II](the_road_to_modern_dynamics_2/)
First-principles mathematical models, numerical simulations, and geometric visualization suite for qualitative dynamics and chaos theory:
- Planar qualitative dynamics: singular points (nodes, saddles, centers, foci) & the Poincaré–Bendixson theorem
- Three-body problem: Euler collinear & Lagrange equilateral configurations, circular restricted 3-body problem (CRTBP), and Jacobi constant
- Poincaré return maps & surfaces of section: reduction of continuous flows, Floquet multipliers, and orbital stability
- Area-preserving twist maps & the Poincaré–Birkhoff theorem: fixed points on an annulus and alternating periodic orbits
- Non-integrability & the homoclinic tangle: transverse invariant manifold intersections and chaotic dynamics
- Conservative double pendulum: Lagrangian derivation, energy conservation, mixed regular/chaotic phase space, and Poincaré sections
- Historical timeline: from Poincaré's prize memoir and Bendixson to Birkhoff, Lorenz, and Smale

For setup, execution, and unit tests, please refer to the project [README](the_road_to_modern_dynamics_2/README.md).

### [Order and Chaos: The Road to Modern Dynamics III](the_road_to_modern_dynamics_3/)
First-principles dynamical systems models, numerical integrations, IMCCE *La2010* orbital reconstructions, and animated visualization suite for Hamiltonian and dissipative chaos:
- Homoclinic tangles, Smale’s horseshoe stretching-and-folding construction, Cantor invariant set ($\Lambda = \bigcap_{n \in \mathbb{Z}} F^n(R)$), and symbolic dynamics (shift map & topological entropy $\ln 2$)
- Periodically forced undamped pendulum ($\ddot{\theta} + \sin\theta = A\cos(\Omega t)$): energy exchange, stroboscopic Poincaré maps, separatrix splitting, and homoclinic chaos
- Integrable Hamiltonian systems, Liouville–Arnold invariant tori, and action–angle motion ($\omega_1/\omega_2 = 2/3$ periodic vs. $\omega_1/\omega_2 = \sqrt{2}$ quasiperiodic)
- Kolmogorov–Arnold–Moser (KAM) theory: small divisors, resonance island chains, and persistence of deformed invariant curves across forcing amplitudes ($A = 0, 0.05, 0.20$)
- Dissipative chaos in the Lorenz system ($\sigma = 10, \rho = 28, \beta = 8/3$): thermal convection origin, phase-space volume contraction ($\nabla \cdot \mathbf{f} = -41/3$), strange attractor, and sensitive dependence from a $10^{-6}$ perturbation
- Secular planetary dynamics & chaos: two-mode linear Lagrange–Laplace oscillations ($e \in [0.06, 0.18]$), Earth–Mars secular resonance libration–circulation transitions, and *La2010a–d* orbital divergence (Laskar et al., 2011)

For setup, execution, and unit tests, please refer to the project [README](the_road_to_modern_dynamics_3/README.md).

### [Dynamical Systems: From Equations to Geometry](dynamical_systems_interpreting_motion/)
Mathematical models and geometric visualization suite for dynamical systems theory and nonlinear mechanics:
- Physical pendulum kinematics mapped into state space and directional vector fields
- Global Hamiltonian phase portrait: libration loops, rotation circulation, and homoclinic separatrix
- Local equilibrium classification via Jacobian eigenvalues: nodes, saddles, centers, and spirals
- Energy dissipation, phase-flow contraction, and emergence of stable attractors
- Poincaré surface of section, continuous flow reduction, and discrete return maps

For setup, execution, and unit tests, please refer to the project [README](dynamical_systems_interpreting_motion/README.md).

### [The 1922 Solar Eclipse: A More Precise Test of General Relativity](1922_solar_eclipse_expedition/)
Astrophysical models and scientific visualization suite for the Wallal light-deflection experiment:
- Gravitational starlight deflection geometry & hyperbolic fall-off ($\delta\theta \propto 1/\rho$)
- Trajectory comparison: Newtonian corpuscular vs. Einstein general-relativistic light deflection
- Wallal astrometric experimental design: Tahiti reference field vs. eclipse totality
- Twin Einstein camera optical architecture: 15-foot and 5-foot polar-axis cameras
- Intermediate-plate differential measurement technique & outer reference boundary ($r > 2^\circ$)
- Empirical solar-limb deflection results: Campbell & Trumpler (1923, 1928) vs. theoretical predictions

For setup, execution, and unit tests, please refer to the project [README](1922_solar_eclipse_expedition/README.md).


### [Interpolating Stars: Reconstructing Telescope Point Spread Functions](psf_spatial_interpolation/)
Astronomical data reduction, spatial statistics, and scientific visualization suite for telescope PSF modeling in weak gravitational lensing:
- Astronomical forward convolution model ($I_{\mathrm{obs}} = G * P_{\mathbf{r}} + N$) & weak lensing cosmic shear systematics
- Three physical observing regimes: smooth seeing-dominated Moffat (G1), optical aberrations + atmospheric turbulence (G2), and space-based diffraction pupil optics (S1)
- Dimensionality reduction via Principal Component Analysis (EigenPSFs) isolating spatial variation from pixel grids
- Benchmark evaluation across 7 spatial interpolation algorithms: Polynomial Regression, IDW, Thin-Plate RBF Splines, Ordinary Kriging, Universal Kriging (drift), MLP, and Random Forest
- Orthogonal error decomposition: separating PCA truncation error from spatial coefficient interpolation error
- Cosmological shape measurement metrics: Gaussian-weighted quadrupole moments ($Q_{ij}$), ellipticity components ($e_1, e_2$), squared size ($R^2$), multiplicative slope biases ($m_1, m_2$), additive offsets ($c_1, c_2$), and mean fractional size bias ($b_{R^2}$)
- Diagnostic visualization suite: focal-plane field grids, reconstruction fidelity scatter, and 21-model forest plots with nominal 95% confidence intervals

For setup, execution, benchmark replication, and unit tests, please refer to the project [README](psf_spatial_interpolation/README.md).

### [From a Nearly Uniform Universe to Galaxies and the Cosmic Web](from_primordial_fluctuations_to_cosmic_web/)
Cosmological perturbation models, power-spectrum calculations, and scientific visualization suite for cosmic structure formation:
- Jeans instability dispersion relation ($\omega^2 = c_s^2 k^2 - 4\pi G\rho_0$) & critical Jeans wavelength ($\lambda_J$)
- Friedmann–Lemaître cosmic expansion in comoving vs. physical coordinates & spatial curvature ($K = +1, 0, -1$)
- Causal structure: particle horizon, comoving Hubble radius $(aH)^{-1}$, and perturbation scale horizon entry
- Cosmic inflation & Hubble exit of quantum fluctuations ($\lambda_{\mathrm{phys}}/(2\pi) = a/k$ crossing $R_H = c/H$), and primordial curvature power spectrum $\mathcal{P}_{\mathcal{R}}(k)$: scale-invariant Harrison–Zel'dovich ($n_s = 1$) vs. Planck 2018 inflationary tilt ($n_s \approx 0.965$)
- Photon–baryon acoustic oscillations, Silk diffusion damping, and Planck 2018 CMB TT angular power spectrum
- Decoupled cold-dark-matter logarithmic Mészáros growth vs. baryon acoustic oscillations, matter transfer function $T(k)$, and linear matter power spectrum $P_m(k, a)$
- Nonlinear anisotropic collapse in the Zel'dovich approximation (sheets, filaments, nodes, and voids) & late-time $\Lambda\mathrm{CDM}$ growth factor $D(a)$ suppression

For setup, execution, and unit tests, please refer to the project [README](from_primordial_fluctuations_to_cosmic_web/README.md).

### [The Golden Age of Black Hole Physics (1963–1974)](the_golden_age_of_black_hole_physics/)
Relativistic numerical models, geodesic integrations, and scientific visualization suite for Kerr black holes and black-hole thermodynamics:
- Oppenheimer–Snyder gravitational collapse ($\tau$ vs. $t$) & Lense–Thirring gravitomagnetic frame dragging ($\propto J/r^3$)
- Petrov Type D classification, Goldberg–Sachs shear-free twisting congruences & Boyer–Lindquist oblate spheroidal geometry
- Kerr black-hole anatomy ($r_+$, $r_-$, ergosphere $r_e(\theta)$, ring singularity) & $(\ell=2, m=2, n=0)$ quasinormal ringdown
- Bound 3D Kerr geodesic orbits & nodal precession computed via `KerrGeoPy` (Schwarzschild vs. $a/m = 0.8$)
- Penrose rotational energy extraction ($E_0 = E_1 + E_2$ with $E_1 < 0$) & Hawking classical area theorem ($dA \ge 0$)
- Bekenstein Generalized Second Law ($\Delta S_{\mathrm{gen}} \ge 0$) & Hawking thermal radiation spectrum with greybody factors $\Gamma_\ell(\omega)$

For setup, execution, and unit tests, please refer to the project [README](the_golden_age_of_black_hole_physics/README.md).

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
