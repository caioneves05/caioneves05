"""
Generates constellation.svg — animated particle network, continuous loop.
840x880px, SMIL-only (works in GitHub <img> tags).
"""

import math
import random
from pathlib import Path

OUT = Path("constellation.svg")
SVG_W, SVG_H = 840, 880
N = 28          # number of particles
KF = 10         # keyframe stops per particle path
rng = random.Random(42)


# ── particle paths ────────────────────────────────────────────────────────────

def smooth_loop(seed: int) -> list[tuple[float, float]]:
    """Return KF+1 (x,y) pairs that form a smooth looping drift path."""
    r = random.Random(seed)
    cx = r.uniform(SVG_W * 0.08, SVG_W * 0.92)
    cy = r.uniform(SVG_H * 0.08, SVG_H * 0.92)
    ax = r.uniform(30, 90)
    ay = r.uniform(30, 90)
    phi_x = r.uniform(0, math.tau)
    phi_y = r.uniform(0, math.tau)
    fx = r.choice([1, 2])
    fy = r.choice([1, 2])
    pts = []
    for k in range(KF):
        t = math.tau * k / KF
        x = cx + ax * math.sin(fx * t + phi_x)
        y = cy + ay * math.sin(fy * t + phi_y)
        x = max(12, min(SVG_W - 12, x))
        y = max(12, min(SVG_H - 12, y))
        pts.append((round(x, 1), round(y, 1)))
    pts.append(pts[0])   # close the loop
    return pts


particles = [smooth_loop(i * 31 + 13) for i in range(N)]
durations = [rng.uniform(14, 26) for _ in range(N)]
radii     = [rng.uniform(2.5, 5.0) for _ in range(N)]

# ── edges: connect each particle to its 3–4 nearest neighbours ───────────────

def dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

starts = [p[0] for p in particles]
edges: set[tuple[int, int]] = set()
for i in range(N):
    nbrs = sorted(range(N), key=lambda j: dist2(starts[i], starts[j]) if j != i else 1e18)
    for j in nbrs[:4]:
        edges.add((min(i, j), max(i, j)))

edges_list = sorted(edges)

# ── SVG helpers ───────────────────────────────────────────────────────────────

def vals(pts, attr):
    return ";".join(str(p[0] if attr == "x" else p[1]) for p in pts)


# ── build SVG ─────────────────────────────────────────────────────────────────

defs_parts = []
elems = []

defs_parts.append('''
  <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="softglow" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="6" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
''')

# background
elems.append(f'<rect width="{SVG_W}" height="{SVG_H}" fill="#0d1117"/>')

# subtle grid dots for depth
for gx in range(40, SVG_W, 80):
    for gy in range(40, SVG_H, 80):
        elems.append(f'<circle cx="{gx}" cy="{gy}" r="1" fill="#21262d" opacity="0.5"/>')

# ── lines ──────────────────────────────────────────────────────────────────────
for i, j in edges_list:
    pi, pj = particles[i], particles[j]
    di, dj = durations[i], durations[j]
    dur = (di + dj) / 2
    op_dur = rng.uniform(3, 7)
    op_begin = f"{rng.uniform(0, op_dur):.1f}s"
    op_min = round(rng.uniform(0.12, 0.2), 2)
    op_max = round(rng.uniform(0.4, 0.6), 2)
    op_vals = f"{op_min};{op_max};{op_min}"

    x1v = vals(pi, "x")
    y1v = vals(pi, "y")
    x2v = vals(pj, "x")
    y2v = vals(pj, "y")
    ks  = ";".join(["0.45 0 0.55 1"] * KF)
    kt  = ";".join([f"{k/KF:.2f}" for k in range(KF + 1)])

    elems.append(
        f'<line x1="{pi[0][0]}" y1="{pi[0][1]}" x2="{pj[0][0]}" y2="{pj[0][1]}" '
        f'stroke="#79c0ff" stroke-width="0.8" opacity="{op_min}">'
        f'<animate attributeName="x1" values="{x1v}" dur="{dur:.1f}s" begin="0s" repeatCount="indefinite" calcMode="spline" keySplines="{ks}" keyTimes="{kt}"/>'
        f'<animate attributeName="y1" values="{y1v}" dur="{dur:.1f}s" begin="0s" repeatCount="indefinite" calcMode="spline" keySplines="{ks}" keyTimes="{kt}"/>'
        f'<animate attributeName="x2" values="{x2v}" dur="{dur:.1f}s" begin="0s" repeatCount="indefinite" calcMode="spline" keySplines="{ks}" keyTimes="{kt}"/>'
        f'<animate attributeName="y2" values="{y2v}" dur="{dur:.1f}s" begin="0s" repeatCount="indefinite" calcMode="spline" keySplines="{ks}" keyTimes="{kt}"/>'
        f'<animate attributeName="opacity" values="{op_vals}" dur="{op_dur:.1f}s" begin="{op_begin}" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" keyTimes="0;0.5;1"/>'
        f'</line>'
    )

# ── particles ──────────────────────────────────────────────────────────────────
for idx, (path, dur, r) in enumerate(zip(particles, durations, radii)):
    x0, y0 = path[0]
    xv = vals(path, "x")
    yv = vals(path, "y")
    ks = ";".join(["0.45 0 0.55 1"] * KF)
    kt = ";".join([f"{k/KF:.2f}" for k in range(KF + 1)])
    op_dur = rng.uniform(2, 5)
    op_begin = f"{rng.uniform(0, op_dur):.1f}s"
    brightness = round(rng.uniform(0.55, 0.9), 2)
    # mix blue and green nodes; occasional white accent
    if idx % 5 == 0:
        color = "#c9d1d9"   # white accent
    elif idx % 3 == 0:
        color = "#56d364"   # github green
    else:
        color = "#79c0ff"   # github blue

    # large nodes get a soft outer glow layer
    filter_attr = 'filter="url(#glow)"' if r > 4 else 'filter="url(#glow)"'

    elems.append(
        f'<circle cx="{x0}" cy="{y0}" r="{r:.1f}" fill="{color}" opacity="{brightness}" {filter_attr}>'
        f'<animate attributeName="cx" values="{xv}" dur="{dur:.1f}s" begin="0s" repeatCount="indefinite" calcMode="spline" keySplines="{ks}" keyTimes="{kt}"/>'
        f'<animate attributeName="cy" values="{yv}" dur="{dur:.1f}s" begin="0s" repeatCount="indefinite" calcMode="spline" keySplines="{ks}" keyTimes="{kt}"/>'
        f'<animate attributeName="opacity" values="{brightness};1.0;{brightness}" dur="{op_dur:.1f}s" begin="{op_begin}" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" keyTimes="0;0.5;1"/>'
        f'</circle>'
    )

# ── assemble ──────────────────────────────────────────────────────────────────
defs = f"<defs>{''.join(defs_parts)}</defs>"
body = "\n".join(elems)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}">
{defs}
{body}
</svg>"""

OUT.write_text(svg)
print(f"Saved → {OUT}  ({N} particles, {len(edges_list)} edges)")
