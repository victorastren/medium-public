#!/usr/bin/env python3
r"""
Generate two-panel static scientific illustration:
"Hawking's Area Theorem"

Figure for Section "Hawking's Area Theorem" of:
"The Golden Age of Black Hole Physics (1963-1974)"

Design & Scientific Specifications:
- Format: Static, two-panel scientific illustration (light scientific style)
- Resolution: 1800 x 900 px at 140 DPI (12.857 x 6.429 in, 2:1 aspect ratio)
- Panel proportions: Equal 50/50 split (left_w = right_w = 0.472)
- Typography & font size hierarchy matching existing figures:
  - 17.8 pt bold main title (dark navy #0f172a)
  - 13.5 pt bold subtitle (slate #475569)
  - 15.5 pt bold single-line panel headers ("A · Horizon Generators and Area",
    "B · Black-Hole Merger")
  - 11.5-12.5 pt bold callouts on pale blue/amber/teal backgrounds
- Panel A (Left): Schematic spacetime world tube of an event horizon on a
  light background with blue/turquoise future-directed null horizon generators,
  blue earlier cross-section A(t_1), amber later cross-section A(t_2), and
  dA/dt >= 0 ==> A(t_2) >= A(t_1).
- Panel B (Right): Schematic merger of two dark-navy shaded black holes (A_1,
  A_2) into a larger final black hole (A_f), with turquoise outgoing
  gravitational-wave ripples and prominent inequality A_f >= A_1 + A_2.
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Arc, Polygon
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = SCRIPT_DIR.parent / "images" / "hawking_area_theorem.png"


def make_bh_RGBA(size=360):
    """Precompute a softly shaded dark 2D RGBA image on the unit disk."""
    y, x = np.ogrid[-1:1:size * 1j, -1:1:size * 1j]
    r2 = x**2 + y**2
    mask = r2 <= 1.0
    img = np.zeros((size, size, 4), dtype=float)
    z = np.sqrt(np.maximum(0.0, 1.0 - r2))
    lx, ly, lz = -0.35, 0.35, 0.87
    dot = np.maximum(0.0, x * lx + y * ly + z * lz) * mask
    base_r, base_g, base_b = 15 / 255, 23 / 255, 42 / 255
    hi_r, hi_g, hi_b = 52 / 255, 74 / 255, 114 / 255
    img[..., 0] = base_r + (hi_r - base_r) * (dot**1.6) * 0.72
    img[..., 1] = base_g + (hi_g - base_g) * (dot**1.6) * 0.72
    img[..., 2] = base_b + (hi_b - base_b) * (dot**1.6) * 0.72
    dist = np.sqrt(r2)
    alpha = np.clip((1.0 - dist) * (size / 3.0), 0.0, 1.0)
    img[..., 3] = alpha
    return img


def draw_bh_disk(ax, cx, cy, radius, bh_img, zorder=6):
    """Render a softly shaded black hole disk centered at (cx, cy)."""
    ax.imshow(
        bh_img,
        extent=[cx - radius, cx + radius, cy - radius, cy + radius],
        origin='lower',
        zorder=zorder,
    )
    theta = np.linspace(0, 2 * np.pi, 240)
    ax.plot(
        cx + radius * np.cos(theta),
        cy + radius * np.sin(theta),
        color='#1e3a8a',
        lw=1.3,
        alpha=0.70,
        zorder=zorder + 1,
    )


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        'text.usetex': False,
        'mathtext.fontset': 'dejavuserif',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 13.5,
    })

    dpi = 140
    fig_w, fig_h = 1800.0 / dpi, 900.0 / dpi
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor='#ffffff')

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Unified Editorial Palette (light scientific style matching Penrose figure)
    NAVY = '#0f172a'
    DARK_SLATE = '#1e293b'
    SLATE = '#475569'
    AXIS_COLOR = '#334155'
    BORDER_COLOR = '#cbd5e1'
    PANEL_BG = '#f8fafc'
    BG_WHITE = '#ffffff'

    BLUE_MAIN = '#1d4ed8'
    BLUE_DARK = '#1e3a8a'
    BLUE_MID = '#3b82f6'
    BLUE_BG = '#eff6ff'
    BLUE_BORDER = '#93c5fd'

    TEAL_MAIN = '#0d9488'
    TEAL_DARK = '#115e59'
    TEAL_BG = '#f0fdfa'
    TEAL_BORDER = '#5eead4'

    ORANGE_MAIN = '#d97706'
    ORANGE_DARK = '#b45309'
    ORANGE_BG = '#fffbeb'
    ORANGE_BORDER = '#fcd34d'

    # =========================================================================
    # 1. TOP HEADER BANNER
    # =========================================================================
    title_box = FancyBboxPatch(
        (0.020, 0.876), 0.960, 0.104,
        boxstyle="round,pad=0.002,rounding_size=0.008",
        facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.4,
    )
    ax.add_patch(title_box)
    ax.text(
        0.50, 0.948, "HAWKING'S AREA THEOREM",
        color=NAVY, fontsize=17.8, fontweight='bold', ha='center', va='center',
    )
    ax.text(
        0.50, 0.898,
        "Horizon geometry and the consequences of black-hole mergers",
        color=SLATE, fontsize=13.5, fontweight='bold', ha='center', va='center',
    )

    # =========================================================================
    # 2. TWO EQUAL PANEL CARDS (Single-line headers, no redundant subtitles)
    # =========================================================================
    p_y = 0.020
    p_h = 0.835
    p_w = 0.472
    left_x = 0.020
    right_x = 0.508

    hdr_h = 0.066
    pad_x = 0.009
    pad_y = 0.012
    vp_h = p_h - hdr_h - 0.032

    for px, p_title, is_right in [
        (left_x, "A  ·  Horizon Generators and Area", False),
        (right_x, "B  ·  Black-Hole Merger", True),
    ]:
        card = FancyBboxPatch(
            (px, p_y), p_w, p_h,
            boxstyle="round,pad=0.002,rounding_size=0.008",
            facecolor=PANEL_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=1,
        )
        ax.add_patch(card)

        viewport = FancyBboxPatch(
            (px + pad_x, p_y + pad_y), p_w - 2 * pad_x, vp_h,
            boxstyle="round,pad=0.002,rounding_size=0.006",
            facecolor=BG_WHITE, edgecolor='#e2e8f0', linewidth=1.0, zorder=1.5,
        )
        ax.add_patch(viewport)

        hdr_y = p_y + p_h - hdr_h - 0.012
        hdr_box = FancyBboxPatch(
            (px + pad_x, hdr_y), p_w - 2 * pad_x, hdr_h,
            boxstyle="round,pad=0.002,rounding_size=0.006",
            facecolor=BG_WHITE if not is_right else ORANGE_BG,
            edgecolor=BORDER_COLOR if not is_right else ORANGE_BORDER,
            linewidth=1.2, zorder=2,
        )
        ax.add_patch(hdr_box)

        ax.text(
            px + 0.5 * p_w, hdr_y + 0.5 * hdr_h, p_title,
            color=NAVY if not is_right else ORANGE_DARK,
            fontsize=15.5, fontweight='bold', ha='center', va='center', zorder=3,
        )

    # =========================================================================
    # 3. PANEL A — EVENT HORIZON WORLD TUBE & GENERATORS (LIGHT STYLE)
    # =========================================================================
    ax_a = fig.add_axes([left_x + pad_x, p_y + pad_y, p_w - 2 * pad_x, vp_h], zorder=3)
    ax_a.set_xlim(-4.6, 4.6)
    ax_a.set_ylim(-4.0, 4.0)
    ax_a.axis('off')

    # Light grey-blue spacetime diagram frame
    st_box = FancyBboxPatch(
        (-4.35, -1.65), 8.70, 5.40,
        boxstyle="round,pad=0.04,rounding_size=0.16",
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.1, zorder=1,
    )
    ax_a.add_patch(st_box)

    # Vertical time axis on the left
    t_ax_x = -3.70
    ax_a.annotate(
        '', xy=(t_ax_x, 3.38), xytext=(t_ax_x, -1.40),
        arrowprops=dict(arrowstyle='-|>,head_length=0.55,head_width=0.30',
                        color=AXIS_COLOR, lw=1.9),
        zorder=4,
    )
    ax_a.text(
        t_ax_x - 0.30, 0.98, "Time $t$",
        color=NAVY, fontsize=12.0, fontweight='bold',
        rotation=90, ha='center', va='center', zorder=4,
    )

    # Smoothly flaring world tube centered at x_c = -0.35
    xc = -0.35
    y_bot, y_top = -1.35, 3.28
    y_vals = np.linspace(y_bot, y_top, 200)
    s = (y_vals - y_bot) / (y_top - y_bot)
    r_vals = 0.92 + 0.92 * (0.28 * s + 0.72 * (3 * s**2 - 2 * s**3))

    x_left = xc - r_vals
    x_right = xc + r_vals
    poly_pts = np.vstack([
        np.column_stack([x_left, y_vals]),
        np.column_stack([x_right[::-1], y_vals[::-1]]),
    ])
    ax_a.add_patch(Polygon(
        poly_pts, closed=True,
        facecolor='#dbeafe', edgecolor='none', alpha=0.62, zorder=2,
    ))

    r_inner = 0.52 * r_vals
    poly_inner = np.vstack([
        np.column_stack([xc - r_inner, y_vals]),
        np.column_stack([(xc + r_inner)[::-1], y_vals[::-1]]),
    ])
    ax_a.add_patch(Polygon(
        poly_inner, closed=True,
        facecolor='#bfdbfe', edgecolor='none', alpha=0.45, zorder=2.2,
    ))

    # Crisp dark-blue outer boundaries of the event horizon world tube
    ax_a.plot(x_left, y_vals, color=BLUE_MAIN, lw=2.3, zorder=5)
    ax_a.plot(x_right, y_vals, color=BLUE_MAIN, lw=2.3, zorder=5)

    # Horizon generators: 5 non-crossing turquoise curves running upward
    fracs = [-0.72, -0.38, 0.0, 0.38, 0.72]
    for frac in fracs:
        gx = xc + frac * r_vals
        ax_a.plot(gx, y_vals, color=TEAL_MAIN, lw=1.8, alpha=0.92, zorder=4)
        idx_arr = 148
        ax_a.annotate(
            '',
            xy=(gx[idx_arr + 5], y_vals[idx_arr + 5]),
            xytext=(gx[idx_arr], y_vals[idx_arr]),
            arrowprops=dict(arrowstyle='-|>,head_length=0.42,head_width=0.22',
                            color=TEAL_MAIN, lw=1.7),
            zorder=5,
        )

    # Earlier cross-section t_1 (blue) and Later cross-section t_2 (amber)
    y_t1 = -0.60
    y_t2 = 2.08
    r_t1 = float(np.interp(y_t1, y_vals, r_vals))
    r_t2 = float(np.interp(y_t2, y_vals, r_vals))

    for y_sl, r_sl, col_fill, col_edge, lw_sl in [
        (y_t1, r_t1, '#3b82f6', BLUE_MAIN, 2.3),
        (y_t2, r_t2, '#f59e0b', ORANGE_MAIN, 2.5),
    ]:
        ell_fill = Ellipse(
            (xc, y_sl), width=2.0 * r_sl, height=0.34 * r_sl,
            facecolor=col_fill, alpha=0.14, edgecolor='none', zorder=6,
        )
        ell_edge = Ellipse(
            (xc, y_sl), width=2.0 * r_sl, height=0.34 * r_sl,
            facecolor='none', edgecolor=col_edge, linewidth=lw_sl, zorder=7,
        )
        ax_a.add_patch(ell_fill)
        ax_a.add_patch(ell_edge)

    # Dashed time-slice guide lines to time axis
    ax_a.plot([t_ax_x, xc - r_t1], [y_t1, y_t1], color='#64748b', lw=1.2, ls=':', zorder=3)
    ax_a.plot([t_ax_x, xc - r_t2], [y_t2, y_t2], color='#64748b', lw=1.2, ls=':', zorder=3)
    ax_a.text(t_ax_x + 0.16, y_t1 + 0.16, r"$t_1$", color=NAVY,
              fontsize=11.8, fontweight='bold', ha='left', va='bottom', zorder=6)
    ax_a.text(t_ax_x + 0.16, y_t2 + 0.16, r"$t_2$", color=NAVY,
              fontsize=11.8, fontweight='bold', ha='left', va='bottom', zorder=6)

    # Light-mode callout boxes on the right of the tube
    # 1. Later cross-section A(t_2)
    ax_a.annotate(
        "Later\n" + r"cross-section $A(t_2)$",
        xy=(xc + r_t2 * 0.96, y_t2),
        xytext=(2.85, 2.62),
        color=ORANGE_DARK, fontsize=11.3, fontweight='bold', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.28', facecolor=ORANGE_BG, edgecolor=ORANGE_MAIN, lw=1.3),
        arrowprops=dict(arrowstyle='-|>,head_length=0.45,head_width=0.25',
                        color=ORANGE_MAIN, lw=1.8, connectionstyle='arc3,rad=-0.10'),
        zorder=9,
    )

    # 2. Horizon generators
    idx_gen = 115
    gx_target = xc + 0.72 * r_vals[idx_gen]
    ax_a.annotate(
        "Horizon generators\n(null geodesics)",
        xy=(gx_target, y_vals[idx_gen]),
        xytext=(2.80, 1.12),
        color=TEAL_DARK, fontsize=11.3, fontweight='bold', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=TEAL_BG, edgecolor=TEAL_MAIN, lw=1.3),
        arrowprops=dict(arrowstyle='-|>,head_length=0.45,head_width=0.25',
                        color=TEAL_MAIN, lw=1.8, connectionstyle='arc3,rad=0.06'),
        zorder=9,
    )

    # 3. Event horizon
    idx_eh = 68
    ax_a.annotate(
        "Event horizon",
        xy=(xc + r_vals[idx_eh], y_vals[idx_eh]),
        xytext=(2.80, -0.08),
        color=BLUE_DARK, fontsize=11.5, fontweight='bold', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.28', facecolor=BLUE_BG, edgecolor=BLUE_MAIN, lw=1.3),
        arrowprops=dict(arrowstyle='-|>,head_length=0.45,head_width=0.25',
                        color=BLUE_MAIN, lw=1.8),
        zorder=9,
    )

    # 4. Earlier cross-section A(t_1)
    ax_a.annotate(
        "Earlier cross-section\n" + r"$A(t_1)$",
        xy=(xc + r_t1 * 0.95, y_t1),
        xytext=(2.80, -1.16),
        color=BLUE_DARK, fontsize=11.5, fontweight='bold', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.30', facecolor=BLUE_BG, edgecolor=BLUE_MID, lw=1.3),
        arrowprops=dict(arrowstyle='-|>,head_length=0.45,head_width=0.25',
                        color=BLUE_MID, lw=1.8, connectionstyle='arc3,rad=0.10'),
        zorder=9,
    )

    # Bottom equation & refined explanatory box in Panel A
    eq_box_a = FancyBboxPatch(
        (-4.35, -3.80), 8.70, 1.88,
        boxstyle="round,pad=0.04,rounding_size=0.16",
        facecolor=BLUE_BG, edgecolor=BLUE_BORDER, linewidth=1.4, zorder=4,
    )
    ax_a.add_patch(eq_box_a)
    ax_a.text(
        0.0, -2.32,
        r"$\frac{\mathrm{d}A}{\mathrm{d}t} \geq 0 \quad \Longrightarrow \quad A(t_2) \geq A(t_1)$",
        color=NAVY, fontsize=16.0, fontweight='bold', ha='center', va='center', zorder=5,
    )
    ax_a.text(
        0.0, -3.26,
        "Under the assumptions of the theorem, the event\n"
        "horizon's cross-sectional area cannot decrease,\n"
        "even as its geometry evolves.",
        color=DARK_SLATE, fontsize=12.6, fontweight='normal', ha='center', va='center',
        linespacing=1.24, zorder=5,
    )

    # =========================================================================
    # 4. PANEL B — BLACK-HOLE MERGER INEQUALITY (LIGHT STYLE)
    # =========================================================================
    ax_b = fig.add_axes([right_x + pad_x, p_y + pad_y, p_w - 2 * pad_x, vp_h], zorder=3)
    # Match axes physical aspect ratio (vp_w / vp_h = 1.232) so set_aspect('equal')
    # fills 100% of the viewport height, aligning st_box_b and eq_box_b with Panel A.
    ax_b.set_xlim(-4.928, 4.928)
    ax_b.set_ylim(-4.0, 4.0)
    ax_b.set_aspect('equal')
    ax_b.axis('off')

    # Light grey-blue diagram frame matching Panel A width and height
    st_box_b = FancyBboxPatch(
        (-4.66, -1.65), 9.32, 5.40,
        boxstyle="round,pad=0.04,rounding_size=0.16",
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.1, zorder=1,
    )
    ax_b.add_patch(st_box_b)

    bh_img = make_bh_RGBA(360)

    # Initial dark-navy shaded black holes A_1 and A_2
    c1_x, c1_y, r1 = -2.65, 2.04, 0.78
    c2_x, c2_y, r2 = -2.65, -0.32, 0.56
    draw_bh_disk(ax_b, c1_x, c1_y, r1, bh_img, zorder=6)
    draw_bh_disk(ax_b, c2_x, c2_y, r2, bh_img, zorder=6)

    ax_b.text(c1_x, c1_y, r"$A_1$", color='#ffffff', fontsize=14.8,
              fontweight='bold', ha='center', va='center', zorder=8)
    ax_b.text(c2_x, c2_y, r"$A_2$", color='#ffffff', fontsize=13.5,
              fontweight='bold', ha='center', va='center', zorder=8)
    ax_b.text(-2.65, 3.28, "Initial black holes", color=NAVY,
              fontsize=12.0, fontweight='bold', ha='center', va='center', zorder=7)

    # Final merged dark-navy black hole A_f
    cf_x, cf_y, rf = 1.85, 0.88, 1.24
    draw_bh_disk(ax_b, cf_x, cf_y, rf, bh_img, zorder=6)
    ax_b.text(cf_x, cf_y, r"$A_f$", color='#ffffff', fontsize=16.8,
              fontweight='bold', ha='center', va='center', zorder=8)
    ax_b.text(cf_x, 3.28, "Final black hole", color=ORANGE_DARK,
              fontsize=12.0, fontweight='bold', ha='center', va='center', zorder=7)

    # Converging merger arrows from A_1 and A_2 toward A_f
    ax_b.annotate(
        '', xy=(cf_x - rf - 0.18, cf_y + 0.25), xytext=(c1_x + r1 + 0.14, c1_y - 0.20),
        arrowprops=dict(arrowstyle='-|>,head_length=0.52,head_width=0.28',
                        color=ORANGE_MAIN, lw=2.5, connectionstyle='arc3,rad=-0.14'),
        zorder=7,
    )
    ax_b.annotate(
        '', xy=(cf_x - rf - 0.18, cf_y - 0.25), xytext=(c2_x + r2 + 0.14, c2_y + 0.20),
        arrowprops=dict(arrowstyle='-|>,head_length=0.52,head_width=0.28',
                        color=ORANGE_MAIN, lw=2.5, connectionstyle='arc3,rad=0.14'),
        zorder=7,
    )
    ax_b.text(-0.52, 0.88, "Merger", color=ORANGE_DARK, fontsize=12.4,
              fontweight='bold', ha='center', va='center', zorder=8)

    # High-contrast turquoise outgoing gravitational-wave ripples on light background
    for w_rad, w_alpha in [(3.25, 0.92), (3.85, 0.72), (4.45, 0.50)]:
        arc_top = Arc(
            (cf_x, cf_y), width=w_rad, height=w_rad * 0.92,
            angle=0, theta1=18, theta2=68,
            color=TEAL_MAIN, lw=2.3, alpha=w_alpha, zorder=5,
        )
        arc_bot = Arc(
            (cf_x, cf_y), width=w_rad, height=w_rad * 0.92,
            angle=0, theta1=-68, theta2=-18,
            color=TEAL_MAIN, lw=2.3, alpha=w_alpha, zorder=5,
        )
        ax_b.add_patch(arc_top)
        ax_b.add_patch(arc_bot)

    # Outgoing gravitational-wave label (no arrow)
    ax_b.text(
        0.72, -1.10,
        "Outgoing\ngravitational waves",
        color=TEAL_DARK, fontsize=11.0, fontweight='bold', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.28', facecolor=TEAL_BG, edgecolor=TEAL_MAIN, lw=1.3),
        zorder=9,
    )

    # Bottom equation & refined explanatory box in Panel B
    eq_box_b = FancyBboxPatch(
        (-4.66, -3.80), 9.32, 1.88,
        boxstyle="round,pad=0.04,rounding_size=0.16",
        facecolor=ORANGE_BG, edgecolor=ORANGE_BORDER, linewidth=1.6, zorder=4,
    )
    ax_b.add_patch(eq_box_b)
    ax_b.text(
        0.0, -2.32,
        r"$A_f \geq A_1 + A_2$",
        color=NAVY, fontsize=18.0, fontweight='bold', ha='center', va='center', zorder=5,
    )
    ax_b.text(
        0.0, -3.26,
        "Although gravitational waves carry energy away\n"
        "during a merger, the final horizon area cannot be\n"
        "smaller than the sum of the initial areas.",
        color=DARK_SLATE, fontsize=12.6, fontweight='normal', ha='center', va='center',
        linespacing=1.24, zorder=5,
    )

    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)
    size_kb = output_path.stat().st_size / 1024.0
    print(f"[OK] Generated Hawking area theorem figure: {output_path} ({size_kb:.1f} KB)")
    return output_path


if __name__ == "__main__":
    create_figure()
