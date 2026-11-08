#!/usr/bin/env python3
r"""
Generate two-panel scientific figure:
"From Quantum Fluctuations to Primordial Perturbations"

Figure for Section "The Origin of Primordial Fluctuations" of:
"From Primordial Fluctuations to Galaxies and the Cosmic Web"

Design & Scientific Specifications:
- Canvas: 2000 x 1100 px at 140 DPI, matching the exact editorial styling and
  font size hierarchy of `dark_energy_structure_growth.png` and
  `horizon_entry_perturbations.png`:
  - 18.0 pt bold hero main title
  - 14.0 pt bold subtitle
  - 15.5 pt bold single-line panel header badges
  - 14.5 pt bold axis titles
  - 13.5-14.0 pt bold primary curve and region labels
  - 12.5-13.5 pt secondary mathematical annotations
- Panel A ("A  Stretching of quantum fluctuations"):
  - Three successive horizontal snapshots ("Early inflation", "During inflation",
    "Later inflation") of the same comoving perturbation (2 wave cycles) stretched
    to increasing physical widths as inflation proceeds.
  - Double-headed wavelength arrows labeled \lambda_phys(t_1),
    \lambda_phys(t_2) > \lambda_phys(t_1), and \lambda_phys(t_3) > \lambda_phys(t_2).
  - Downward arrow on the left labeled "Inflation proceeds".
  - Bottom formula badge: \lambda_phys(t) = 2\pi a(t) / k.
- Panel B ("B  Hubble exit during inflation"):
  - Schematic logarithmic plot of physical length scale vs progress through inflation.
  - Rising blue line: Mode scale \lambda_phys / (2\pi) = a(t) / k.
  - Nearly constant amber line: Hubble radius R_H(t) = c / H(t).
  - Crossing marker at (0, 0) with compact callout "Hubble exit: k = aH/c".
  - Descriptive regime labels in open whitespace:
    - Left: "Mode scale smaller than Hubble radius" / "Quantum fluctuations"
    - Right: "Mode scale larger than Hubble radius" / "\mathcal{R} approximately conserved"
"""

from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR / "images" / "quantum_fluctuations_primordial_perturbations.png"
PUBLIC_OUT = Path("/home/marc/dev/medium-public/from_primordial_fluctuations_to_cosmic_web/images/quantum_fluctuations_primordial_perturbations.png")


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure mathtext and typography (matching dark_energy_structure_growth.png)
    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 14.0,
    })

    # Canvas: exactly 2000 x 1100 px at 140 DPI
    fig_w, fig_h = 2000.0 / 140.0, 1100.0 / 140.0
    dpi = 140
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    # Curated Editorial Palette
    NAVY = '#0f172a'          # Hero headings, axis titles
    DARK_SLATE = '#1e293b'    # Primary text
    SLATE = '#475569'         # Secondary text
    AXIS_COLOR = '#334155'    # Axis spines and arrowheads
    BORDER_COLOR = '#cbd5e1'  # Card borders
    CARD_BG = '#f8fafc'       # Header & card backgrounds

    # Accents - Mode scale & Inflation (Royal Blue)
    BLUE_DEEP = '#1e3a8a'
    BLUE_DARK = '#1d4ed8'
    BLUE = '#2563eb'
    BLUE_LIGHT = '#bfdbfe'
    BLUE_BG = '#eff6ff'

    # Accents - Hubble Radius & Hubble Exit (Amber / Warm Gold)
    AMBER_DEEP = '#92400e'
    AMBER_DARK = '#b45309'
    AMBER = '#d97706'
    AMBER_LIGHT = '#fde68a'
    AMBER_BG = '#fffbeb'

    # -------------------------------------------------------------------------
    # 1. Top Header Banner (y: 0.894 - 0.980)
    # -------------------------------------------------------------------------
    ax_head = fig.add_axes([0.025, 0.894, 0.950, 0.086])
    ax_head.set_xlim(0, 1)
    ax_head.set_ylim(0, 1)
    ax_head.axis('off')

    title_box = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                               boxstyle="round,pad=0.0,rounding_size=0.009",
                               mutation_aspect=(0.950 * fig_w) / (0.086 * fig_h),
                               clip_on=False,
                               facecolor=CARD_BG, edgecolor=BORDER_COLOR, linewidth=1.4)
    ax_head.add_patch(title_box)
    ax_head.text(0.50, 0.65, "FROM QUANTUM FLUCTUATIONS TO PRIMORDIAL PERTURBATIONS",
                 color=NAVY, fontsize=18.0, fontweight='bold', ha='center', va='center')
    ax_head.text(0.50, 0.26,
                 "During cosmic inflation, the physical scales of quantum fluctuations grow beyond the Hubble radius",
                 color=SLATE, fontsize=14.0, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # 2. Outer Card Frames & Single-Line Panel Header Badges (Panel A & Panel B)
    # -------------------------------------------------------------------------
    card_bottom = 0.030
    card_height = 0.844
    card_w = 0.464
    left_x = 0.025
    right_x = 0.511

    # Left Card Frame (Panel A)
    ax_card_a = fig.add_axes([left_x, card_bottom, card_w, card_height], zorder=0)
    ax_card_a.set_xlim(0, 1)
    ax_card_a.set_ylim(0, 1)
    ax_card_a.axis('off')
    ax_card_a.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0,
                                  facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4))
    hdr_a = FancyBboxPatch((0.026, 0.924), 0.948, 0.054,
                           boxstyle="round,pad=0.0,rounding_size=0.012",
                           mutation_aspect=(card_w * fig_w) / (card_height * fig_h),
                           facecolor=BLUE_BG, edgecolor=BLUE_LIGHT, linewidth=1.3)
    ax_card_a.add_patch(hdr_a)
    ax_card_a.text(0.50, 0.951,
                   "A  Stretching of quantum fluctuations",
                   color=BLUE_DEEP, fontsize=15.5, fontweight='bold', ha='center', va='center')

    # Right Card Frame (Panel B)
    ax_card_b = fig.add_axes([right_x, card_bottom, card_w, card_height], zorder=0)
    ax_card_b.set_xlim(0, 1)
    ax_card_b.set_ylim(0, 1)
    ax_card_b.axis('off')
    ax_card_b.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0,
                                  facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.4))
    hdr_b = FancyBboxPatch((0.026, 0.924), 0.948, 0.054,
                           boxstyle="round,pad=0.0,rounding_size=0.012",
                           mutation_aspect=(card_w * fig_w) / (card_height * fig_h),
                           facecolor=AMBER_BG, edgecolor=AMBER_LIGHT, linewidth=1.3)
    ax_card_b.add_patch(hdr_b)
    ax_card_b.text(0.50, 0.951,
                   "B  Hubble exit during inflation",
                   color=AMBER_DEEP, fontsize=15.5, fontweight='bold', ha='center', va='center')

    # =========================================================================
    # 3. PANEL A: STRETCHING OF QUANTUM FLUCTUATIONS
    # =========================================================================
    ax_a = fig.add_axes([left_x + 0.012, card_bottom + 0.015, card_w - 0.024, card_height - 0.088], zorder=2)
    ax_a.set_xlim(0, 10)
    ax_a.set_ylim(0, 10)
    ax_a.axis('off')

    # Vertical arrow on the left indicating cosmic time / inflation progress
    arrow_t = FancyArrowPatch((0.72, 8.55), (0.72, 1.45),
                              arrowstyle='->,head_length=8,head_width=5',
                              color=AXIS_COLOR, linewidth=2.0)
    ax_a.add_patch(arrow_t)
    ax_a.text(0.32, 5.00, "Inflation proceeds",
              color=DARK_SLATE, fontsize=13.5, fontweight='bold',
              ha='center', va='center', rotation=90)

    def draw_snapshot(y_box_bot, box_w, heading_text, wave_label):
        x_start = 1.32
        box_h = 1.76
        y_box_top = y_box_bot + box_h
        # Place wave baseline in lower part of box so larger 15pt math label has generous headroom
        y_wave_mid = y_box_bot + 0.45

        # Snapshot Heading cleanly ABOVE the box
        ax_a.text(x_start, y_box_top + 0.22, heading_text,
                  color=NAVY, fontsize=14.2, fontweight='bold', ha='left', va='center')

        # Rounded container for the comoving region
        box = FancyBboxPatch((x_start, y_box_bot), box_w, box_h,
                             boxstyle="round,pad=0.0,rounding_size=0.14",
                             clip_on=False,
                             facecolor='#f8fafc', edgecolor=BORDER_COLOR, linewidth=1.3)
        ax_a.add_patch(box)

        # Baseline zero-line
        ax_a.plot([x_start + 0.10, x_start + box_w - 0.10], [y_wave_mid, y_wave_mid],
                  color='#94a3b8', linestyle=':', linewidth=1.1)

        # Smooth sinusoidal wave: 2 complete cycles in each snapshot
        n_pts = 400
        x_wave = np.linspace(x_start, x_start + box_w, n_pts)
        phase = 2.0 * np.pi * 2.0 * (x_wave - x_start) / box_w
        amp = 0.27
        y_wave = y_wave_mid + amp * np.sin(phase)

        # Subtle shading for scalar field variations
        ax_a.fill_between(x_wave, y_wave_mid, y_wave, where=(y_wave >= y_wave_mid),
                          color='#3b82f6', alpha=0.22, interpolate=True)
        ax_a.fill_between(x_wave, y_wave_mid, y_wave, where=(y_wave < y_wave_mid),
                          color='#93c5fd', alpha=0.16, interpolate=True)

        # Wave curve
        ax_a.plot(x_wave, y_wave, color=BLUE_DARK, linewidth=2.7, solid_capstyle='round')

        # Double-headed wavelength arrow between Crest 1 (1/8) and Crest 2 (5/8)
        x_c1 = x_start + 0.125 * box_w
        x_c2 = x_start + 0.625 * box_w
        y_crest = y_wave_mid + amp
        y_arrow = y_crest + 0.13

        # Vertical tick guides at the two crests
        ax_a.plot([x_c1, x_c1], [y_crest + 0.03, y_arrow + 0.07],
                  color=BLUE_DEEP, linestyle='--', linewidth=1.0)
        ax_a.plot([x_c2, x_c2], [y_crest + 0.03, y_arrow + 0.07],
                  color=BLUE_DEEP, linestyle='--', linewidth=1.0)

        arrow_w = FancyArrowPatch((x_c1, y_arrow), (x_c2, y_arrow),
                                  arrowstyle='<->,head_length=5,head_width=3.5',
                                  color=BLUE_DEEP, linewidth=1.5)
        ax_a.add_patch(arrow_w)
        ax_a.text((x_c1 + x_c2) / 2.0, y_arrow + 0.08, wave_label,
                  color=BLUE_DEEP, fontsize=15.2, fontweight='bold', ha='center', va='bottom')

    # Snapshot 1: Early inflation
    draw_snapshot(y_box_bot=7.02, box_w=3.55,
                  heading_text="Early inflation",
                  wave_label=r"$\lambda_{\mathrm{phys}}(t_1)$")

    # Snapshot 2: During inflation
    draw_snapshot(y_box_bot=4.22, box_w=5.85,
                  heading_text="During inflation",
                  wave_label=r"$\lambda_{\mathrm{phys}}(t_2) > \lambda_{\mathrm{phys}}(t_1)$")

    # Snapshot 3: Later inflation
    draw_snapshot(y_box_bot=1.42, box_w=8.38,
                  heading_text="Later inflation",
                  wave_label=r"$\lambda_{\mathrm{phys}}(t_3) > \lambda_{\mathrm{phys}}(t_2)$")

    # Bottom Formula Badge (single display-style formula with full-size \dfrac)
    formula_box = FancyBboxPatch((2.40, 0.06), 6.20, 1.04,
                                 boxstyle="round,pad=0.0,rounding_size=0.12",
                                 clip_on=False,
                                 facecolor=BLUE_BG, edgecolor=BLUE_LIGHT, linewidth=1.3)
    ax_a.add_patch(formula_box)
    ax_a.text(5.50, 0.58,
              r"$\lambda_{\mathrm{phys}}(t) = \dfrac{2\pi\,a(t)}{k}$",
              color=BLUE_DEEP, fontsize=15.5, fontweight='bold', ha='center', va='center')

    # =========================================================================
    # 4. PANEL B: HUBBLE EXIT DURING INFLATION
    # =========================================================================
    plot_rel_left = 0.088
    plot_w = 0.350
    plot_bottom = 0.150
    plot_h = 0.630

    ax_b = fig.add_axes([right_x + plot_rel_left, plot_bottom, plot_w, plot_h], zorder=2)
    ax_b.set_facecolor('#ffffff')

    x_min, x_max = -4.18, 3.60
    y_min, y_max = -3.85, 3.60
    ax_b.set_xlim(x_min, x_max)
    ax_b.set_ylim(y_min, y_max)

    # Shaded Background Regimes (before vs after Hubble exit at x = 0)
    ax_b.axvspan(x_min, 0.0, facecolor='#f0f9ff', alpha=0.55, zorder=0)
    ax_b.axvspan(0.0, x_max, facecolor='#fffbeb', alpha=0.55, zorder=0)

    # Vertical dashed line at Hubble exit (x = 0)
    ax_b.plot([0.0, 0.0], [y_min, y_max],
              color=SLATE, linestyle='--', linewidth=1.8, zorder=2)

    # Curves:
    # 1. Mode scale \lambda_phys / (2\pi) = a(t)/k (rising line with slope +1 in log coordinates)
    x_grid = np.linspace(x_min, x_max, 300)
    y_mode = x_grid.copy()

    # 2. Hubble radius R_H(t) = c/H(t) (quasi-de Sitter slow-roll: very gentle slope ~ 0.035)
    eps_slope = 0.035
    y_hubble = eps_slope * x_grid

    ax_b.plot(x_grid, y_mode, color=BLUE, linewidth=4.0, solid_capstyle='round', zorder=4)
    ax_b.plot(x_grid, y_hubble, color=AMBER, linewidth=4.0, solid_capstyle='round', zorder=4)

    # Crossing Marker at (0, 0)
    ax_b.scatter([0.0], [0.0], s=130, color=AMBER, edgecolor=BLUE_DEEP, linewidth=2.2, zorder=7)

    # Compact Hubble exit callout box above intersection (shifted left so right edge is well clear of blue line)
    ax_b.text(-1.25, 1.02,
              "Hubble exit: " + r"$k = aH/c$",
              color=NAVY, fontsize=14.2, fontweight='bold',
              ha='center', va='center',
              bbox=dict(boxstyle='round,pad=0.28,rounding_size=0.15',
                        facecolor='#ffffff', edgecolor=BORDER_COLOR, linewidth=1.3, alpha=0.98),
              zorder=8)
    ax_b.annotate(
        "",
        xy=(-0.03, 0.14), xytext=(-0.52, 0.66),
        arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.8, shrinkA=0, shrinkB=2),
        zorder=8
    )

    # Curve Label 1: Mode scale \lambda_phys / (2\pi) = a/k (explicit container box strictly above y = x)
    mode_box = FancyBboxPatch((0.16, 2.18), 1.96, 1.32,
                              boxstyle="round,pad=0.0,rounding_size=0.12",
                              facecolor='#ffffff', edgecolor=BLUE_LIGHT, linewidth=1.3, alpha=0.97,
                              zorder=7)
    ax_b.add_patch(mode_box)
    ax_b.text(1.14, 3.20, "Mode scale",
              color=BLUE_DEEP, fontsize=13.8, fontweight='bold', ha='center', va='center', zorder=8)
    ax_b.text(1.14, 2.58, r"$\dfrac{\lambda_{\mathrm{phys}}}{2\pi} = \dfrac{a(t)}{k}$",
              color=BLUE_DEEP, fontsize=14.5, fontweight='bold', ha='center', va='center', zorder=8)
    ax_b.annotate(
        "",
        xy=(2.68, 2.68), xytext=(2.16, 2.74),
        arrowprops=dict(arrowstyle="->", color=BLUE_DARK, lw=1.8,
                        connectionstyle="arc3,rad=-0.08", shrinkA=0, shrinkB=2),
        zorder=8
    )

    # Curve Label 2: Hubble radius R_H = c/H (explicit container box strictly above y = x on the left)
    hubble_box = FancyBboxPatch((-4.04, -1.62), 2.42, 1.24,
                                boxstyle="round,pad=0.0,rounding_size=0.12",
                                facecolor='#ffffff', edgecolor=AMBER_LIGHT, linewidth=1.3, alpha=0.97,
                                zorder=7)
    ax_b.add_patch(hubble_box)
    ax_b.text(-2.83, -0.66, "Hubble radius",
              color=AMBER_DEEP, fontsize=13.8, fontweight='bold', ha='center', va='center', zorder=8)
    ax_b.text(-2.83, -1.22, r"$R_H(t) = \dfrac{c}{H(t)}$",
              color=AMBER_DEEP, fontsize=14.5, fontweight='bold', ha='center', va='center', zorder=8)
    ax_b.annotate(
        "",
        xy=(-2.83, -0.10), xytext=(-2.83, -0.35),
        arrowprops=dict(arrowstyle="->", color=AMBER_DARK, lw=1.8, shrinkA=0, shrinkB=2),
        zorder=8
    )

    # Regime 1 Label (Top-Left Quadrant: unboxed text on shaded background, matching horizon_entry_perturbations.png)
    ax_b.text(-2.10, 2.88,
              "Mode scale smaller\nthan Hubble radius",
              color=BLUE_DEEP, fontsize=13.2, fontweight='bold',
              ha='center', va='center', linespacing=1.32,
              zorder=6)
    ax_b.text(-2.10, 2.12,
              r"$\lambda_{\mathrm{phys}} / (2\pi) < c/H$",
              color=BLUE_DEEP, fontsize=14.8, fontweight='bold',
              ha='center', va='center',
              zorder=6)

    # Regime 2 Label (Bottom-Right Quadrant: unboxed text on shaded background, matching horizon_entry_perturbations.png)
    ax_b.text(1.90, -0.92,
              "Mode scale larger\nthan Hubble radius",
              color=AMBER_DEEP, fontsize=13.2, fontweight='bold',
              ha='center', va='center', linespacing=1.32,
              zorder=6)
    ax_b.text(1.90, -1.62,
              r"$\lambda_{\mathrm{phys}} / (2\pi) > c/H$",
              color=AMBER_DEEP, fontsize=14.8, fontweight='bold',
              ha='center', va='center',
              zorder=6)
    ax_b.text(1.90, -2.76,
              r"$\mathcal{R}$" + " approximately\nconserved\n(adiabatic mode)",
              color=AMBER_DEEP, fontsize=13.2, fontweight='bold',
              ha='center', va='center', linespacing=1.28,
              zorder=6)

    # Panel B Spines, Arrowheads, Ticks & Labels (matching horizon_entry_perturbations.png)
    ax_b.spines['top'].set_visible(False)
    ax_b.spines['right'].set_visible(False)
    ax_b.spines['left'].set_edgecolor(AXIS_COLOR)
    ax_b.spines['left'].set_linewidth(2.0)
    ax_b.spines['bottom'].set_edgecolor(AXIS_COLOR)
    ax_b.spines['bottom'].set_linewidth(2.0)

    ax_b.plot(1.0, 0.0, ">", transform=ax_b.transAxes, color=AXIS_COLOR,
              markersize=9, clip_on=False, zorder=10)
    ax_b.plot(0.0, 1.0, "^", transform=ax_b.transAxes, color=AXIS_COLOR,
              markersize=9, clip_on=False, zorder=10)

    # Schematic transition ticks only (no unexplained numerical ticks)
    ax_b.set_xticks([0.0])
    ax_b.set_xticklabels([r"$a_{\mathrm{exit}}$"],
                         fontsize=15.0, fontweight='bold', color=DARK_SLATE)
    ax_b.set_yticks([0.0])
    ax_b.set_yticklabels([r"$c/H_{\mathrm{exit}}$"],
                         fontsize=15.0, fontweight='bold', color=DARK_SLATE)
    ax_b.tick_params(axis='both', pad=6, length=6, width=1.6, colors=AXIS_COLOR)

    ax_b.set_xlabel("Progress through inflation (logarithmic scale)",
                    fontsize=14.0, fontweight='bold', color=NAVY, labelpad=10)
    ax_b.set_ylabel("Physical length scale (log)",
                    fontsize=14.5, fontweight='bold', color=NAVY, labelpad=10)

    # Save outputs
    plt.savefig(output_path, dpi=dpi, facecolor='#ffffff', edgecolor='none')
    plt.close(fig)
    print(f"[OK] Figure generated successfully: {output_path} ({int(fig_w * dpi)} x {int(fig_h * dpi)} px)")

    # Mirror to public repository when generating default target
    try:
        if output_path.resolve() == DEFAULT_OUT.resolve() and PUBLIC_OUT.parent.exists():
            shutil.copy2(output_path, PUBLIC_OUT)
            print(f"[OK] Mirrored to public destination: {PUBLIC_OUT}")
    except Exception as exc:
        print(f"[WARNING] Could not mirror to public destination: {exc}")


if __name__ == "__main__":
    create_figure()
