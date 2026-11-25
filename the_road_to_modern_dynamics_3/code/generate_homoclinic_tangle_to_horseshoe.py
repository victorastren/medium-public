#!/usr/bin/env python3
r"""
Generate Figure 1 for Article 3 ("Order and Chaos: The Road to Modern Dynamics III"):
"From a Homoclinic Tangle to Smale’s Horseshoe"

Three-panel horizontal figure (18.0 x 9.8 in @ 240 DPI -> 4320 x 2352 px)
matching the exact font-size hierarchy and bold editorial style of
poincare_bendixson_theorem.png from Part II (all font sizes >= 14.0 pt).

Logical chain:
  Panel A (Homoclinic tangle)
    -> [Visual bridge from local neighborhood of H: "Repeated returns near the homoclinic orbit"]
  Panel B (Return dynamics near the intersection: "Stretching and folding under repeated returns")
    ->
  Panel C (Smale horseshoe: "An idealized model of the same mechanism")
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = PROJECT_DIR / "images" / "homoclinic_tangle_to_horseshoe.png"


def build_homoclinic_tangle():
    r"""
    Construct smooth, non-self-intersecting invariant manifolds W^u(p) and W^s(p)
    passing strictly through p = (-1.18, 0) along distinct +/- 45 deg tangents,
    with transverse homoclinic oscillations concentrated toward the right.
    """
    p = np.array([-1.18, 0.0])
    A = 2.78
    B = 2.78

    taus = np.linspace(-5.8, 2.75, 2800)
    sech = 1.0 / np.cosh(taus)
    tanh = np.tanh(taus)

    u_sep = p[0] + A * sech
    v_sep = -B * sech * tanh

    du = -A * sech * tanh
    dv = -B * sech * (1.0 - 2.0 * tanh**2)
    speed = np.hypot(du, dv)
    tx, ty = du / speed, dv / speed
    nx, ny = -ty, tx

    tau_on = -0.20
    env = np.where(taus > tau_on, 1.0 - np.exp(-((taus - tau_on) / 0.25) ** 2), 0.0)

    omega_tau = 8.2
    tau_H = 0.0
    osc = np.sin(omega_tau * (taus - tau_H))

    end_taper = 1.0 - 0.30 * np.exp(-((2.75 - taus) / 0.25) ** 2)
    amp = 0.35 * env * (1.0 + 0.44 * np.maximum(0.0, taus)) * end_taper

    u_dir = np.array([1.0, B / A])
    u_dir = u_dir / np.linalg.norm(u_dir)
    lean = np.where(taus > 0.50, 0.60 * np.tanh((taus - 0.50) / 0.70), 0.0)

    dx = amp * osc * ((1.0 - lean) * nx + lean * u_dir[0])
    dy = amp * osc * ((1.0 - lean) * ny + lean * u_dir[1])

    wu_loop = np.column_stack([u_sep + dx, v_sep + dy])

    s_leg = np.linspace(0.82, 0.0, 220, endpoint=False)
    slope = B / A
    norm_s = np.hypot(1.0, slope)
    leg_u = p[0] - s_leg / norm_s * 1.05 - 0.05 * s_leg**2
    leg_v = p[1] - s_leg * slope / norm_s * 1.05 + 0.03 * s_leg**2
    wu_leg = np.column_stack([leg_u, leg_v])

    wu = np.vstack([wu_leg, [p], wu_loop])
    ws = wu.copy()
    ws[:, 1] = -ws[:, 1]
    return p, wu, ws, len(wu_leg)


def count_self_intersections(pts):
    """Verify a manifold curve has zero self-intersections."""
    sub = pts[::4]
    n = len(sub) - 1
    cnt = 0
    for i in range(n):
        p1, p2 = sub[i], sub[i + 1]
        d1 = p2 - p1
        for j in range(i + 3, n):
            q1, q2 = sub[j], sub[j + 1]
            if max(p1[0], p2[0]) < min(q1[0], q2[0]) or min(p1[0], p2[0]) > max(q1[0], q2[0]):
                continue
            if max(p1[1], p2[1]) < min(q1[1], q2[1]) or min(p1[1], p2[1]) > max(q1[1], q2[1]):
                continue
            d2 = q2 - q1
            denom = d1[0] * d2[1] - d1[1] * d2[0]
            if abs(denom) < 1e-12:
                continue
            diff = q1 - p1
            t = (diff[0] * d2[1] - diff[1] * d2[0]) / denom
            u = (diff[0] * d1[1] - diff[1] * d1[0]) / denom
            if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
                cnt += 1
    return cnt


def find_crossing_near(wu, ws, target_u, target_v):
    """Find the exact segment-segment crossing between wu and ws closest to (target_u, target_v)."""
    best_pt = None
    best_dist = float("inf")
    m_u = (np.abs(wu[:, 0] - target_u) < 0.45) & (np.abs(wu[:, 1] - target_v) < 0.45)
    m_s = (np.abs(ws[:, 0] - target_u) < 0.45) & (np.abs(ws[:, 1] - target_v) < 0.45)
    iu = np.where(m_u[:-1] & m_u[1:])[0]
    is_ = np.where(m_s[:-1] & m_s[1:])[0]

    for i in iu:
        p1, p2 = wu[i], wu[i + 1]
        d1 = p2 - p1
        for j in is_:
            q1, q2 = ws[j], ws[j + 1]
            if max(p1[0], p2[0]) < min(q1[0], q2[0]) or min(p1[0], p2[0]) > max(q1[0], q2[0]):
                continue
            if max(p1[1], p2[1]) < min(q1[1], q2[1]) or min(p1[1], p2[1]) > max(q1[1], q2[1]):
                continue
            d2 = q2 - q1
            denom = d1[0] * d2[1] - d1[1] * d2[0]
            if abs(denom) < 1e-12:
                continue
            diff = q1 - p1
            t = (diff[0] * d2[1] - diff[1] * d2[0]) / denom
            u = (diff[0] * d1[1] - diff[1] * d1[0]) / denom
            if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
                pt = p1 + t * d1
                dist = np.hypot(pt[0] - target_u, pt[1] - target_v)
                if dist < best_dist:
                    best_dist = dist
                    best_pt = pt
    return best_pt


def add_arrow_at_point(ax, pts, u_target, v_target, color, direction=1, scale=17, zorder=7):
    """Place a crisp arrowhead along curve pts closest to (u_target, v_target)."""
    idx = int(np.argmin(np.hypot(pts[:, 0] - u_target, pts[:, 1] - v_target)))
    idx = max(1, min(len(pts) - 2, idx))
    if direction >= 0:
        p_start, p_end = pts[idx], pts[idx + 1]
    else:
        p_start, p_end = pts[idx + 1], pts[idx]
    d = p_end - p_start
    norm = np.hypot(d[0], d[1])
    if norm == 0:
        return
    d = d / norm
    p_tail = p_end - 0.05 * d
    ax.annotate(
        "",
        xy=(p_end[0], p_end[1]),
        xytext=(p_tail[0], p_tail[1]),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=0.0,
            mutation_scale=scale,
            shrinkA=0,
            shrinkB=0,
        ),
        zorder=zorder,
    )


def clip_polygon_to_rect(poly, x0, y0, x1, y1):
    """Exact Sutherland-Hodgman polygon clipping against axis-aligned rectangle [x0, x1] x [y0, y1]."""
    def clip_edge(pts, inside_fn, intersect_fn):
        if len(pts) == 0:
            return pts
        out = []
        prev = pts[-1]
        prev_in = inside_fn(prev)
        for curr in pts:
            curr_in = inside_fn(curr)
            if curr_in:
                if not prev_in:
                    out.append(intersect_fn(prev, curr))
                out.append(curr)
            elif prev_in:
                out.append(intersect_fn(prev, curr))
            prev, prev_in = curr, curr_in
        return np.array(out) if out else np.empty((0, 2))

    pts = np.asarray(poly, dtype=float)
    pts = clip_edge(pts, lambda p: p[0] >= x0,
                    lambda a, b: np.array([x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0])]))
    pts = clip_edge(pts, lambda p: p[0] <= x1,
                    lambda a, b: np.array([x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0])]))
    pts = clip_edge(pts, lambda p: p[1] >= y0,
                    lambda a, b: np.array([a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0]))
    pts = clip_edge(pts, lambda p: p[1] <= y1,
                    lambda a, b: np.array([a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1]))
    return pts


def build_ribbon_from_centerline(cx, cy, half_w_arr):
    """Build a closed 2D polygon ribbon and unit normals from centerline (cx, cy) and half-width array."""
    dx = np.gradient(cx)
    dy = np.gradient(cy)
    ds = np.hypot(dx, dy)
    tx = dx / ds
    ty = dy / ds
    nx = -ty
    ny = tx

    upper_x = cx + half_w_arr * nx
    upper_y = cy + half_w_arr * ny
    lower_x = cx - half_w_arr * nx
    lower_y = cy - half_w_arr * ny

    poly = np.column_stack([
        np.concatenate([upper_x, lower_x[::-1]]),
        np.concatenate([upper_y, lower_y[::-1]]),
    ])
    center = np.column_stack([cx, cy])
    normals = np.column_stack([nx, ny])
    return poly, center, normals, upper_x, upper_y, lower_x, lower_y


def build_local_deformation_bands():
    """
    Build two geometric stages in Panel B to emphasize the deformation mechanism:
    1) The elongated, transversely compressed strip rising diagonally at 52 deg
       through the local region R, with a dotted ghost extension continuing straight
       up-right to show pure elongation before folding.
    2) The partially folded / hooked returned strip F(R), which bends clockwise
       away from the straight elongated tangent and sweeps back down across the
       right side of R — visually distinct from the completed vertical horseshoe in Panel C.
    """
    ang_rise = np.radians(52.0)
    dir_rise = np.array([np.cos(ang_rise), np.sin(ang_rise)])
    p_start = np.array([-1.14, -1.24])

    # 1) Ghost continuation of the straight elongated strip (from before the bend up to upper-right)
    u_g = np.linspace(1.30, 2.48, 120)
    cx_g = p_start[0] + u_g * dir_rise[0]
    cy_g = p_start[1] + u_g * dir_rise[1]
    hw_g = np.full_like(u_g, 0.115)
    ghost_poly, ghost_center, ghost_normals, *_ = build_ribbon_from_centerline(cx_g, cy_g, hw_g)

    # 2) Partially folded strip F(R) built as a smooth cubic Bezier-blended curve:
    #    - Segment 1 (rising straight through R along dir_rise): p_start -> p_bend_in
    #    - Segment 2 (smooth clockwise hook): p_bend_in -> apex -> p_bend_out
    #    - Segment 3 (folded arm sweeping back down across right half of R): p_bend_out -> p_end
    p0 = p_start
    p1 = p_start + 1.63 * dir_rise
    p2 = p_start + 2.38 * dir_rise
    p3 = np.array([0.84, 0.56])                     # outer hook control
    p4 = np.array([0.44, -0.10])                    # entering right side of R
    p5 = np.array([-0.16, -1.24])                   # exiting bottom-right of R

    # Evaluate smooth composite B-spline / De Casteljau curve
    t1 = np.linspace(0.0, 1.0, 140, endpoint=False)
    seg1 = np.outer(1.0 - t1, p0) + np.outer(t1, p1)

    t2 = np.linspace(0.0, 1.0, 140, endpoint=False)
    # Quartic Bezier through p1, p2, p3, p4 for C^1 join with seg1 and seg3
    b0 = (1.0 - t2) ** 3
    b1 = 3.0 * ((1.0 - t2) ** 2) * t2
    b2 = 3.0 * (1.0 - t2) * (t2**2)
    b3 = t2**3
    seg2 = np.outer(b0, p1) + np.outer(b1, p2) + np.outer(b2, p3) + np.outer(b3, p4)

    t3 = np.linspace(0.0, 1.0, 120)
    # Direction from p3 -> p4 is (-0.40, -0.66), and p4 -> p5 is (-0.62, -1.16) — nearly collinear!
    q_mid = p4 + 0.45 * (p4 - p3)
    c0 = (1.0 - t3) ** 2
    c1 = 2.0 * (1.0 - t3) * t3
    c2 = t3**2
    seg3 = np.outer(c0, p4) + np.outer(c1, q_mid) + np.outer(c2, p5)

    pts_all = np.vstack([seg1, seg2, seg3])
    # Re-parameterize uniformly by arc length for smooth normal calculation
    ds_raw = np.hypot(np.diff(pts_all[:, 0]), np.diff(pts_all[:, 1]))
    s_cum = np.concatenate([[0.0], np.cumsum(ds_raw)])
    s_uni = np.linspace(0.0, s_cum[-1], 360)
    cx = np.interp(s_uni, s_cum, pts_all[:, 0])
    cy = np.interp(s_uni, s_cum, pts_all[:, 1])

    half_w = np.full_like(s_uni, 0.115)
    poly, center, normals, ux, uy, lx, ly = build_ribbon_from_centerline(cx, cy, half_w)
    return (poly, center, normals, half_w, ux, uy, lx, ly), (ghost_poly, ghost_center, ghost_normals)


def create_figure(output_path=None):
    if output_path is None:
        output_path = DEFAULT_OUT
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        "text.usetex": False,
        "mathtext.fontset": "dejavuserif",
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "axes.edgecolor": "#94a3b8",
        "axes.linewidth": 1.3,
    })

    # Canvas dimensions with generous width for larger bold headers and wider badge-to-title gap
    fig_w, fig_h = 19.8, 9.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=240, facecolor="#ffffff")

    # Part II Editorial Palette
    NAVY = "#0f172a"
    DARK_SLATE = "#1e293b"
    SLATE = "#334155"
    BORDER_CARD = "#cbd5e1"
    BG_CARD = "#f8fafc"
    BG_BOX = "#ffffff"

    BLUE_ACCENT = "#2563eb"
    BLUE_LIGHT = "#eff6ff"
    BLUE_BORDER = "#93c5fd"

    TEAL_ACCENT = "#0d9488"
    TEAL_DARK = "#0f766e"
    TEAL_LIGHT = "#f0fdfa"
    TEAL_BORDER = "#5eead4"

    PURPLE_ACCENT = "#6366f1"
    PURPLE_DARK = "#4338ca"
    PURPLE_FILL = "#e0e7ff"
    PURPLE_STRIP = "#a5b4fc"
    PURPLE_LIGHT = "#eef2ff"
    PURPLE_BORDER = "#a5b4fc"

    RED_ACCENT = "#dc2626"

    halo = [pe.withStroke(linewidth=4.0, foreground="#ffffff", alpha=0.96)]

    # -------------------------------------------------------------------------
    # Global Title & Subtitle (scaled to match Animation 1's visual size at 680px)
    # -------------------------------------------------------------------------
    fig.text(
        0.5,
        0.964,
        "From a Homoclinic Tangle to Smale’s Horseshoe",
        fontsize=29.2,
        weight="bold",
        color=NAVY,
        ha="center",
        va="center",
    )
    fig.text(
        0.5,
        0.920,
        "How transverse homoclinic intersections lead to an idealized model of stretching and folding",
        fontsize=21.3,
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

    # Three equal-width parallel panel cards with clean inter-panel gaps for progression arrows
    y_card = 0.024
    h_card = 0.868
    x1, w1 = 0.012, 0.312
    x2, w2 = 0.344, 0.312
    x3, w3 = 0.676, 0.312

    panels_spec = [
        (x1, w1, "A", "Homoclinic tangle",
         "Manifolds intersect transversely",
         BLUE_ACCENT, BLUE_LIGHT, BLUE_BORDER),
        (x2, w2, "B", "Return dynamics associated\nwith the homoclinic tangle",
         "Stretching and folding\nunder repeated returns",
         TEAL_ACCENT, TEAL_LIGHT, TEAL_BORDER),
        (x3, w3, "C", "Smale horseshoe",
         "An idealized model\nof the same mechanism",
         PURPLE_ACCENT, PURPLE_LIGHT, PURPLE_BORDER),
    ]

    hbar_h = 0.154
    badge_y = y_card + h_card - hbar_h / 2.0

    for px, pw, letter, title, subtitle, acc_color, bg_tint, bdr_color in panels_spec:
        card_rect = patches.FancyBboxPatch(
            (px, y_card),
            pw,
            h_card,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=BG_CARD,
            edgecolor=BORDER_CARD,
            linewidth=1.4,
            zorder=1,
        )
        ax_bg.add_patch(card_rect)

        hbar_rect = patches.FancyBboxPatch(
            (px, y_card + h_card - hbar_h),
            pw,
            hbar_h,
            boxstyle="round,pad=0.0,rounding_size=0.016",
            facecolor=bg_tint,
            edgecolor=bdr_color,
            linewidth=1.2,
            zorder=2,
        )
        ax_bg.add_patch(hbar_rect)

        badge_x = px + 0.0235
        r_x = 0.0130
        r_y = r_x * (fig_w / fig_h)
        badge_c = patches.Ellipse(
            (badge_x, badge_y),
            width=2.0 * r_x,
            height=2.0 * r_y,
            facecolor=acc_color,
            edgecolor="none",
            zorder=3,
        )
        ax_bg.add_patch(badge_c)
        ax_bg.text(
            badge_x,
            badge_y - 0.0005,
            letter,
            fontsize=18.5,
            weight="bold",
            color="#ffffff",
            ha="center",
            va="center",
            zorder=4,
        )

        # Panel title (21.2 pt) & subtitle (17.6 pt), scaled identically to Animation 1
        text_offset_x = badge_x + 0.0210
        header_top = y_card + h_card
        header_bot = header_top - hbar_h
        if "\n" in title and "\n" in subtitle:
            ax_bg.text(
                text_offset_x,
                header_top - 0.011,
                title,
                fontsize=21.2,
                weight="bold",
                color=NAVY,
                va="top",
                linespacing=1.06,
                zorder=4,
            )
            ax_bg.text(
                text_offset_x,
                header_bot + 0.011,
                subtitle,
                fontsize=17.6,
                weight="bold",
                color="#475569",
                va="bottom",
                linespacing=1.08,
                zorder=4,
            )
        elif "\n" not in title and "\n" in subtitle:
            ax_bg.text(
                text_offset_x,
                badge_y + 0.027,
                title,
                fontsize=21.2,
                weight="bold",
                color=NAVY,
                va="center",
                zorder=4,
            )
            ax_bg.text(
                text_offset_x,
                badge_y - 0.025,
                subtitle,
                fontsize=17.6,
                weight="bold",
                color="#475569",
                va="center",
                linespacing=1.12,
                zorder=4,
            )
        else:
            ax_bg.text(
                text_offset_x,
                badge_y + 0.022,
                title,
                fontsize=21.2,
                weight="bold",
                color=NAVY,
                va="center",
                zorder=4,
            )
            ax_bg.text(
                text_offset_x,
                badge_y - 0.024,
                subtitle,
                fontsize=17.6,
                weight="bold",
                color="#475569",
                va="center",
                zorder=4,
            )

    # Small conceptual progression arrows between panel headers (A -> B -> C)
    for gap_x0, gap_x1 in ((x1 + w1 + 0.003, x2 - 0.003), (x2 + w2 + 0.003, x3 - 0.003)):
        prog_arrow = patches.FancyArrowPatch(
            (gap_x0, badge_y),
            (gap_x1, badge_y),
            arrowstyle="-|>,head_length=6.5,head_width=4.2",
            color="#64748b",
            linewidth=2.0,
            zorder=5,
        )
        ax_bg.add_patch(prog_arrow)

    # Vertical coordinates (clean bottom padding between y_box and y_card)
    y_box = 0.038
    h_box = 0.158
    h_plot = 0.492
    w_plot = 0.260
    y_plot = 0.214

    def render_bottom_caption_box(px, pw, text_str, fontsize=15.5, linespacing=1.22):
        """Render bold centered bottom summary box matching the screenshot style."""
        box = patches.FancyBboxPatch(
            (px + 0.008, y_box),
            pw - 0.016,
            h_box,
            boxstyle="round,pad=0.0,rounding_size=0.014",
            facecolor=BG_BOX,
            edgecolor=BORDER_CARD,
            linewidth=1.2,
            zorder=3,
        )
        ax_bg.add_patch(box)
        ax_bg.text(
            px + pw / 2.0,
            y_box + h_box / 2.0,
            text_str,
            fontsize=fontsize,
            weight="bold",
            color=DARK_SLATE,
            ha="center",
            va="center",
            linespacing=linespacing,
            zorder=4,
        )

    def render_bottom_bullet_box(px, pw, bullets, y_positions=None, fontsize=13.5, linespacing=1.14):
        """Render left-indented, vertically aligned bullet points inside Panel A's bottom box."""
        box = patches.FancyBboxPatch(
            (px + 0.008, y_box),
            pw - 0.016,
            h_box,
            boxstyle="round,pad=0.0,rounding_size=0.014",
            facecolor=BG_BOX,
            edgecolor=BORDER_CARD,
            linewidth=1.2,
            zorder=3,
        )
        ax_bg.add_patch(box)

        x_bul = px + 0.015
        x_txt = px + 0.025
        if y_positions is None:
            y_positions = [y_box + h_box - 0.014, y_box + 0.090]
        for y_b, txt in zip(y_positions, bullets):
            ax_bg.text(
                x_bul,
                y_b,
                "•",
                fontsize=fontsize + 1.4,
                weight="bold",
                color=BLUE_ACCENT,
                ha="left",
                va="top",
                zorder=4,
            )
            ax_bg.text(
                x_txt,
                y_b,
                txt,
                fontsize=fontsize,
                weight="bold",
                color=DARK_SLATE,
                ha="left",
                va="top",
                linespacing=linespacing,
                zorder=4,
            )
    ax1 = fig.add_axes([x1 + (w1 - w_plot) / 2.0, y_plot, w_plot, h_plot], zorder=5)
    ax1.set_facecolor("#ffffff")
    ax1.set_xlim(-2.05, 2.05)
    ax1.set_ylim(-2.05, 2.05)
    ax1.set_aspect("equal", adjustable="box")
    ax1.set_xticks([])
    ax1.set_yticks([])

    for gx in np.linspace(-1.5, 1.5, 7):
        ax1.axvline(gx, color="#f1f5f9", lw=1.0, zorder=1)
    for gy in np.linspace(-1.5, 1.5, 7):
        ax1.axhline(gy, color="#f1f5f9", lw=1.0, zorder=1)

    p, wu, ws, p_idx = build_homoclinic_tangle()
    assert count_self_intersections(wu) == 0, "W^u(p) must not self-intersect"
    assert count_self_intersections(ws) == 0, "W^s(p) must not self-intersect"

    ax1.plot(ws[:, 0], ws[:, 1], color=BLUE_ACCENT, lw=2.6, solid_capstyle="round", zorder=4)
    ax1.plot(wu[:, 0], wu[:, 1], color=RED_ACCENT, lw=2.6, solid_capstyle="round", zorder=5)

    # Forward-time arrows on unobstructed saddle branches near p
    add_arrow_at_point(ax1, wu[:p_idx], -1.62, -0.44, RED_ACCENT, direction=-1, scale=16, zorder=7)
    add_arrow_at_point(ax1, wu[p_idx:], -0.90, 0.25, RED_ACCENT, direction=1, scale=16, zorder=7)
    add_arrow_at_point(ax1, ws[:p_idx], -1.62, 0.44, BLUE_ACCENT, direction=1, scale=16, zorder=7)
    add_arrow_at_point(ax1, ws[p_idx:], -0.90, -0.25, BLUE_ACCENT, direction=-1, scale=16, zorder=7)

    # Transverse homoclinic intersection H (upper-right wide crossing)
    H_pt = find_crossing_near(wu, ws, 1.15, 1.32)
    if H_pt is not None:
        # Highlight local neighborhood around H in Panel A (teal dashed square)
        nb_half = 0.34
        nb_rect = patches.Rectangle(
            (H_pt[0] - nb_half, H_pt[1] - nb_half),
            2.0 * nb_half,
            2.0 * nb_half,
            facecolor=TEAL_LIGHT,
            edgecolor=TEAL_ACCENT,
            linewidth=2.0,
            linestyle="--",
            alpha=0.72,
            zorder=3,
        )
        ax1.add_patch(nb_rect)
        nb_border = patches.Rectangle(
            (H_pt[0] - nb_half, H_pt[1] - nb_half),
            2.0 * nb_half,
            2.0 * nb_half,
            facecolor="none",
            edgecolor=TEAL_ACCENT,
            linewidth=2.0,
            linestyle="--",
            zorder=9,
        )
        ax1.add_patch(nb_border)

        ax1.plot(
            H_pt[0],
            H_pt[1],
            "o",
            markerfacecolor="none",
            markeredgecolor=NAVY,
            markeredgewidth=2.2,
            markersize=13.5,
            zorder=10,
        )
        ax1.plot(H_pt[0], H_pt[1], "o", color=NAVY, markersize=4.2, zorder=11)

        ax1.annotate(
            r"$\mathbf{Homoclinic\;Point}\;\boldsymbol{H}$",
            xy=(H_pt[0], H_pt[1]),
            xytext=(-0.82, 1.36),
            fontsize=14.2,
            weight="bold",
            color=NAVY,
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.24", facecolor="#ffffff", edgecolor=BORDER_CARD, linewidth=1.1),
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.7, shrinkA=3, shrinkB=7),
            zorder=12,
        )

        # Direct label for the dashed teal neighborhood box around H (right-aligned inside frame)
        ax1.text(
            1.96,
            H_pt[1] + nb_half + 0.13,
            r"Neighborhood of $\boldsymbol{H}$",
            fontsize=13.2,
            weight="bold",
            color=TEAL_DARK,
            ha="right",
            va="bottom",
            path_effects=halo,
            zorder=12,
        )

    # Discreet callout introducing the Poincaré return map P (upper-left, no arrow)
    ax1.text(
        -1.95,
        1.94,
        r"$\boldsymbol{P}$: Poincaré return map",
        fontsize=12.6,
        weight="bold",
        color=NAVY,
        ha="left",
        va="top",
        bbox=dict(boxstyle="round,pad=0.22", facecolor="#f8fafc", edgecolor=BORDER_CARD, linewidth=1.1),
        zorder=12,
    )

    # Small transparent pale-teal dashed square enclosing fixed point p ("Selected region R")
    # ~17% of plotting width (2 * 0.35 / 4.10 = 17.1%), keeping manifolds and p unobstructed
    r_p_half = 0.35
    r_p_border = patches.Rectangle(
        (p[0] - r_p_half, p[1] - r_p_half),
        2.0 * r_p_half,
        2.0 * r_p_half,
        facecolor="none",
        edgecolor="#14b8a6",
        linewidth=2.0,
        linestyle="--",
        zorder=9,
    )
    ax1.add_patch(r_p_border)
    ax1.annotate(
        r"Selected region $\boldsymbol{R}$",
        xy=(p[0] + r_p_half + 0.03, p[1]),
        xytext=(0.24, 0.02),
        fontsize=13.2,
        weight="bold",
        color=TEAL_DARK,
        ha="center",
        va="center",
        path_effects=halo,
        arrowprops=dict(arrowstyle="->", color="#14b8a6", lw=1.7, shrinkA=6, shrinkB=2),
        zorder=12,
    )

    # Hyperbolic fixed point p (black) with local in-panel label p inside R and external boxed call-out
    ax1.plot(p[0], p[1], "o", color="#000000", markersize=8.2, zorder=11)
    ax1.text(
        p[0] - 0.20,
        p[1] - 0.01,
        r"$\boldsymbol{p}$",
        fontsize=13.6,
        weight="bold",
        color=NAVY,
        ha="center",
        va="center",
        path_effects=halo,
        zorder=12,
    )
    ax1.annotate(
        r"$\mathbf{Fixed\;Point}\;\boldsymbol{p}$",
        xy=(p[0] - 0.03, p[1] - 0.08),
        xytext=(-1.02, -1.66),
        fontsize=14.5,
        weight="bold",
        color=NAVY,
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor=BORDER_CARD, linewidth=1.1),
        arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.7, shrinkA=3, shrinkB=7),
        zorder=12,
    )

    # Direct manifold labels on curves
    ax1.text(
        -0.46,
        0.96,
        r"$\boldsymbol{W^u(p)}$",
        fontsize=16.5,
        weight="bold",
        color=RED_ACCENT,
        ha="center",
        va="bottom",
        path_effects=halo,
        zorder=11,
    )
    ax1.text(
        -0.26,
        -1.25,
        r"$\boldsymbol{W^s(p)}$",
        fontsize=16.5,
        weight="bold",
        color=BLUE_ACCENT,
        ha="center",
        va="top",
        path_effects=halo,
        zorder=11,
    )

    render_bottom_bullet_box(
        x1, w1,
        [
            r"$\boldsymbol{P}$: Poincaré return map.",
            r"$\boldsymbol{p}$: hyperbolic saddle fixed point of $\boldsymbol{P}$, corresponding" + "\n" + "to an unstable periodic orbit of the underlying flow.",
            r"$\boldsymbol{H}$: transverse homoclinic intersection" + "\n" + r"of $\boldsymbol{W^s(p)}$ and $\boldsymbol{W^u(p)}$.",
            r"$\boldsymbol{R}$: suitably chosen region near $\boldsymbol{p}$.",
        ],
        y_positions=[
            y_box + h_box - 0.010,
            y_box + h_box - 0.036,
            y_box + h_box - 0.083,
            y_box + h_box - 0.130,
        ],
        fontsize=12.1,
        linespacing=1.10,
    )

    # =========================================================================
    # PANEL B: Return dynamics associated with the homoclinic tangle
    # Emphasizes the deformation mechanism: elongated compressed strip + folding action
    # =========================================================================
    ax2 = fig.add_axes([x2 + (w2 - w_plot) / 2.0, y_plot, w_plot, h_plot], zorder=5)
    ax2.set_facecolor("#ffffff")
    ax2.set_xlim(-2.05, 2.05)
    ax2.set_ylim(-2.05, 2.05)
    ax2.set_aspect("equal", adjustable="box")
    ax2.set_xticks([])
    ax2.set_yticks([])

    for gx in np.linspace(-1.5, 1.5, 7):
        ax2.axvline(gx, color="#f1f5f9", lw=1.0, zorder=1)
    for gy in np.linspace(-1.5, 1.5, 7):
        ax2.axhline(gy, color="#f1f5f9", lw=1.0, zorder=1)

    # Local region R positioned in lower-left/center-left with generous clearance on lower-left corner
    R_x0, R_y0, R_w, R_h = -1.42, -1.04, 1.78, 1.24
    r_local = patches.Rectangle(
        (R_x0, R_y0),
        R_w,
        R_h,
        facecolor="#f8fafc",
        edgecolor="none",
        alpha=0.82,
        zorder=2,
    )
    ax2.add_patch(r_local)

    (poly_pts, center_pts, normals_pts, half_w, ux, uy, lx, ly), (ghost_poly, ghost_center, ghost_normals) = (
        build_local_deformation_bands()
    )

    # 1) Ghost extension of pure elongated & compressed strip before folding (dashed lavender outline)
    ghost_patch = patches.Polygon(
        ghost_poly,
        closed=True,
        facecolor="#eef2ff",
        edgecolor="#818cf8",
        linewidth=1.9,
        linestyle="--",
        alpha=0.85,
        zorder=2,
    )
    ax2.add_patch(ghost_patch)

    # 2) Oblique partially-folded / curling returned strip F(R)
    band_b = patches.Polygon(
        poly_pts,
        closed=True,
        facecolor=PURPLE_FILL,
        edgecolor=PURPLE_ACCENT,
        linewidth=2.4,
        alpha=0.92,
        zorder=3,
    )
    ax2.add_patch(band_b)

    # Highlight the two intersection strips where F(R) overlaps R (split at apex outside R
    # so each arm is clipped independently to R without any artificial edge bridge)
    apex_idx = int(np.argmax(center_pts[:, 1]))
    for sl in (slice(0, apex_idx + 1), slice(apex_idx, len(ux))):
        arm_poly = np.column_stack([
            np.concatenate([ux[sl], lx[sl][::-1]]),
            np.concatenate([uy[sl], ly[sl][::-1]]),
        ])
        clipped = clip_polygon_to_rect(arm_poly, R_x0, R_y0, R_x0 + R_w, R_y0 + R_h)
        if len(clipped) >= 3:
            overlap_patch = patches.Polygon(
                clipped,
                closed=True,
                facecolor=PURPLE_STRIP,
                edgecolor=PURPLE_DARK,
                linewidth=1.8,
                alpha=0.80,
                zorder=4,
            )
            ax2.add_patch(overlap_patch)

    # Dashed boundary of R drawn on top
    r_border = patches.Rectangle(
        (R_x0, R_y0),
        R_w,
        R_h,
        facecolor="none",
        edgecolor=DARK_SLATE,
        linewidth=2.5,
        linestyle="--",
        zorder=6,
    )
    ax2.add_patch(r_border)

    # Deformation Mechanism Arrows:
    # (a) Longitudinal STRETCHING arrow along the diagonal elongated strip (cleanly above R)
    idx_s = 128
    c_pt = center_pts[idx_s]
    n_pt = normals_pts[idx_s]
    t_vec = np.array([n_pt[1], -n_pt[0]])
    ax2.annotate(
        "",
        xy=(c_pt[0] + 0.48 * t_vec[0] + 0.25 * n_pt[0], c_pt[1] + 0.48 * t_vec[1] + 0.25 * n_pt[1]),
        xytext=(c_pt[0] - 0.48 * t_vec[0] + 0.25 * n_pt[0], c_pt[1] - 0.48 * t_vec[1] + 0.25 * n_pt[1]),
        arrowprops=dict(arrowstyle="<->", color=DARK_SLATE, lw=2.2, mutation_scale=15),
        zorder=9,
    )
    ax2.text(
        -0.44,
        0.42,
        "Stretching",
        fontsize=14.8,
        weight="bold",
        color=DARK_SLATE,
        ha="right",
        va="center",
        path_effects=halo,
        zorder=10,
    )

    # (b) Transverse COMPRESSION inward arrows squeezing the strip perpendicular to its length
    idx_c = 290
    cc = center_pts[idx_c]
    nn = normals_pts[idx_c]
    hw_c = half_w[idx_c]
    ax2.annotate(
        "",
        xy=(cc[0] + hw_c * nn[0], cc[1] + hw_c * nn[1]),
        xytext=(cc[0] + (hw_c + 0.32) * nn[0], cc[1] + (hw_c + 0.32) * nn[1]),
        arrowprops=dict(arrowstyle="-|>", color=DARK_SLATE, lw=1.9, mutation_scale=14, shrinkA=0, shrinkB=1),
        zorder=9,
    )
    ax2.annotate(
        "",
        xy=(cc[0] - hw_c * nn[0], cc[1] - hw_c * nn[1]),
        xytext=(cc[0] - (hw_c + 0.32) * nn[0], cc[1] - (hw_c + 0.32) * nn[1]),
        arrowprops=dict(arrowstyle="-|>", color=DARK_SLATE, lw=1.9, mutation_scale=14, shrinkA=0, shrinkB=1),
        zorder=9,
    )
    ax2.text(
        0.58,
        -0.52,
        "Compression",
        fontsize=14.8,
        weight="bold",
        color=DARK_SLATE,
        ha="left",
        va="center",
        path_effects=halo,
        zorder=10,
    )

    # (c) FOLDING curved arrow bending the ghost strip clockwise into the folded arm
    ax2.annotate(
        "",
        xy=(0.74, 0.12),
        xytext=(0.60, 0.76),
        arrowprops=dict(
            arrowstyle="-|>",
            connectionstyle="arc3,rad=-0.38",
            color=PURPLE_DARK,
            lw=2.5,
            mutation_scale=18,
        ),
        zorder=9,
    )
    ax2.text(
        0.96,
        0.42,
        "Folding",
        fontsize=15.0,
        weight="bold",
        color=PURPLE_DARK,
        ha="left",
        va="center",
        path_effects=halo,
        zorder=10,
    )

    # Bold boxed label: Selected region R (schematic enlargement) — arrow points directly
    # to the lower-left corner of R without crossing or touching the violet band
    ax2.annotate(
        r"Selected region $\boldsymbol{R}$" + "\n(schematic enlargement)",
        xy=(R_x0, R_y0),
        xytext=(-0.86, -1.66),
        fontsize=13.0,
        weight="bold",
        color=DARK_SLATE,
        ha="center",
        va="center",
        linespacing=1.14,
        bbox=dict(boxstyle="round,pad=0.23", facecolor="#ffffff", edgecolor=BORDER_CARD, linewidth=1.1),
        arrowprops=dict(arrowstyle="->", color=DARK_SLATE, lw=1.8, shrinkA=3, shrinkB=2),
        zorder=10,
    )

    # Upper-right callout: F = P^N ("suitable iterate"), clear of F(R) and right border
    ax2.text(
        1.25,
        1.68,
        r"$\boldsymbol{F = P^N}$" + "\nsuitable iterate",
        fontsize=13.0,
        weight="bold",
        color=NAVY,
        ha="center",
        va="center",
        linespacing=1.14,
        bbox=dict(boxstyle="round,pad=0.22", facecolor="#f8fafc", edgecolor=PURPLE_BORDER, linewidth=1.2),
        zorder=12,
    )

    # Bold boxed label: Returned image F(R) below the F = P^N callout,
    # pointing directly to the outer curved arch of the violet band
    ax2.annotate(
        r"Returned image $\boldsymbol{F(R)}$",
        xy=(0.52, 0.56),
        xytext=(0.94, 1.02),
        fontsize=13.6,
        weight="bold",
        color=PURPLE_DARK,
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.22", facecolor="#ffffff", edgecolor=PURPLE_BORDER, linewidth=1.1),
        arrowprops=dict(arrowstyle="->", color=PURPLE_ACCENT, lw=1.8, shrinkA=3, shrinkB=2),
        zorder=10,
    )

    render_bottom_caption_box(
        x2, w2,
        r"A suitable iterate $\boldsymbol{F = P^N}$ stretches, compresses," + "\n"
        r"and folds a selected region $\boldsymbol{R}$ near $\boldsymbol{p}$. The returned" + "\n"
        r"image overlaps $\boldsymbol{R}$ in two strips, represented" + "\n"
        "in idealized form in Panel C.",
        fontsize=14.6,
        linespacing=1.16,
    )

    # =========================================================================
    # VISUAL BRIDGE FROM PANEL A (LIGHT-GREY MARGIN) TO PANEL B
    # =========================================================================
    if H_pt is not None:
        # Start in the light-grey margin of Panel A, lowered cleanly below the Panel B callout box
        disp_start = ax1.transData.transform((2.23, H_pt[1] - 0.28))
        fig_start = fig.transFigure.inverted().transform(disp_start)
        # Curve smoothly into Panel B well clear below the badge, pointing toward the local folded dynamics
        disp_end = ax2.transData.transform((-0.65, 0.85))
        fig_end = fig.transFigure.inverted().transform(disp_end)

        bridge_arrow = patches.FancyArrowPatch(
            (fig_start[0], fig_start[1]),
            (fig_end[0], fig_end[1]),
            transform=fig.transFigure,
            connectionstyle="arc3,rad=-0.12",
            arrowstyle="-|>,head_length=9,head_width=5.5",
            color=TEAL_ACCENT,
            linewidth=2.5,
            zorder=20,
        )
        fig.patches.append(bridge_arrow)

        # Crisp 3-line badge shifted left to leave generous upper-right room for F = P^N
        ax2.text(
            -0.92,
            1.63,
            r"Return dynamics near $\boldsymbol{p}$" + "\nassociated with the\nhomoclinic orbit",
            fontsize=11.8,
            weight="bold",
            color=TEAL_DARK,
            ha="center",
            va="center",
            linespacing=1.10,
            bbox=dict(boxstyle="round,pad=0.20", facecolor=TEAL_LIGHT, edgecolor=TEAL_ACCENT, linewidth=1.4),
            zorder=15,
        )

    # =========================================================================
    # PANEL C: Smale horseshoe (idealized model)
    # =========================================================================
    ax3 = fig.add_axes([x3 + (w3 - w_plot) / 2.0, y_plot, w_plot, h_plot], zorder=5)
    ax3.set_facecolor("#ffffff")
    ax3.set_xlim(-2.05, 2.05)
    ax3.set_ylim(-2.05, 2.05)
    ax3.set_aspect("equal", adjustable="box")
    ax3.set_xticks([])
    ax3.set_yticks([])

    for gx in np.linspace(-1.5, 1.5, 7):
        ax3.axvline(gx, color="#f1f5f9", lw=1.0, zorder=1)
    for gy in np.linspace(-1.5, 1.5, 7):
        ax3.axhline(gy, color="#f1f5f9", lw=1.0, zorder=1)

    y_shift = 0.02
    R_min_x, R_max_x = -1.12, 1.12
    R_min_y, R_max_y = -1.08 + y_shift, 1.08 + y_shift

    x_mid = 0.68
    w_half = 0.165
    r_in = x_mid - w_half   # 0.515 -> central gap width 1.03
    r_out = x_mid + w_half  # 0.845
    y_bot = -1.50 + y_shift
    y_arch = 1.08 + y_shift

    th = np.linspace(np.pi, 0.0, 160)
    x_outer = np.concatenate([
        np.array([-r_out, -r_out]),
        r_out * np.cos(th),
        np.array([r_out, r_out]),
    ])
    y_outer = np.concatenate([
        np.array([y_bot, y_arch]),
        y_arch + r_out * np.sin(th),
        np.array([y_arch, y_bot]),
    ])
    th_rev = np.linspace(0.0, np.pi, 160)
    x_inner = np.concatenate([
        np.array([r_in, r_in]),
        r_in * np.cos(th_rev),
        np.array([-r_in, -r_in]),
    ])
    y_inner = np.concatenate([
        np.array([y_bot, y_arch]),
        y_arch + r_in * np.sin(th_rev),
        np.array([y_arch, y_bot]),
    ])

    band_poly_pts = np.column_stack([
        np.concatenate([x_outer, x_inner]),
        np.concatenate([y_outer, y_inner]),
    ])

    band_patch = patches.Polygon(
        band_poly_pts,
        closed=True,
        facecolor=PURPLE_FILL,
        edgecolor=PURPLE_ACCENT,
        linewidth=2.4,
        zorder=3,
    )
    ax3.add_patch(band_patch)

    for sign in (-1.0, 1.0):
        x_left = sign * x_mid - w_half
        strip_rect = patches.Rectangle(
            (x_left, R_min_y),
            2.0 * w_half,
            R_max_y - R_min_y,
            facecolor=PURPLE_STRIP,
            edgecolor=PURPLE_DARK,
            linewidth=2.0,
            alpha=0.78,
            zorder=4,
        )
        ax3.add_patch(strip_rect)

    r_square = patches.Rectangle(
        (R_min_x, R_min_y),
        R_max_x - R_min_x,
        R_max_y - R_min_y,
        facecolor="none",
        edgecolor=DARK_SLATE,
        linewidth=2.5,
        linestyle="--",
        zorder=7,
    )
    ax3.add_patch(r_square)

    ax3.text(
        -1.22,
        R_min_y + 0.04,
        r"$\boldsymbol{R}$",
        fontsize=18.5,
        weight="bold",
        color=DARK_SLATE,
        ha="right",
        va="bottom",
        path_effects=halo,
        zorder=9,
    )

    ax3.annotate(
        r"$\boldsymbol{F(R)}$",
        xy=(r_out * np.cos(np.pi / 4.0), y_arch + r_out * np.sin(np.pi / 4.0)),
        xytext=(1.14, y_arch + 0.62),
        fontsize=18.0,
        weight="bold",
        color=PURPLE_ACCENT,
        ha="left",
        va="center",
        path_effects=halo,
        arrowprops=dict(arrowstyle="->", color=PURPLE_ACCENT, lw=1.9, shrinkA=3, shrinkB=4),
        zorder=9,
    )

    arrow_f = patches.FancyArrowPatch(
        (-1.32, 0.35 + y_shift),
        (-0.96, 1.48 + y_shift),
        connectionstyle="arc3,rad=-0.26",
        arrowstyle="-|>,head_length=8,head_width=5",
        color=DARK_SLATE,
        linewidth=2.2,
        zorder=9,
    )
    ax3.add_patch(arrow_f)
    ax3.text(
        -1.45,
        0.96 + y_shift,
        r"$\boldsymbol{F}$",
        fontsize=18.5,
        weight="bold",
        color=DARK_SLATE,
        ha="right",
        va="center",
        path_effects=halo,
        zorder=10,
    )

    ax3.text(
        0.0,
        0.10 + y_shift,
        r"$\boldsymbol{R\!\cap\!F(R)}$",
        fontsize=14.2,
        weight="bold",
        color=PURPLE_DARK,
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.18", facecolor="#ffffff", edgecolor=PURPLE_DARK, linewidth=1.2),
        zorder=10,
    )
    ax3.annotate(
        "",
        xy=(-r_in + 0.01, -0.24 + y_shift),
        xytext=(-0.15, -0.04 + y_shift),
        arrowprops=dict(arrowstyle="->", color=PURPLE_DARK, lw=1.9, shrinkA=2, shrinkB=2),
        zorder=9,
    )
    ax3.annotate(
        "",
        xy=(r_in - 0.01, -0.24 + y_shift),
        xytext=(0.15, -0.04 + y_shift),
        arrowprops=dict(arrowstyle="->", color=PURPLE_DARK, lw=1.9, shrinkA=2, shrinkB=2),
        zorder=9,
    )

    render_bottom_caption_box(
        x3, w3,
        r"The image $\boldsymbol{F(R)}$ overlaps $\boldsymbol{R}$ in two strips," + "\n"
        "remaining a continuous, non-self-intersecting\n"
        "band under the smooth invertible map.",
        fontsize=15.4,
        linespacing=1.22,
    )

    fig.savefig(output_path, dpi=240, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    create_figure()
