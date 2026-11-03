"""
Renders contrib-heatmap.svg from data/contributions.json.
Grid: 53 weeks x 7 days, diagonal reveal animation.
"""

import json
import math
from datetime import date, timedelta
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "contributions.json"
OUT = Path(__file__).parent.parent / "contrib-heatmap.svg"

# 5-level palette matching GitHub's data-level 0-4
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL = 13
GAP = 3
STEP = CELL + GAP
COLS = 53
ROWS = 7
MARGIN_LEFT = 28
MARGIN_TOP = 28
MARGIN_BOTTOM = 36
LABEL_H = 18
WIDTH = MARGIN_LEFT + COLS * STEP + 10
HEIGHT = MARGIN_TOP + ROWS * STEP + MARGIN_BOTTOM + LABEL_H


def level(count: int) -> int:
    if count == 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    if count <= 14:
        return 4
    return 5


def build_grid(days: list[dict]) -> dict[str, int]:
    return {d["date"]: d["count"] for d in days}


def render(data: dict) -> str:
    grid = build_grid(data["days"])
    today = date.fromisoformat(data["days"][-1]["date"])
    # start from 52 weeks ago, aligned to Sunday
    start = today - timedelta(weeks=52, days=today.weekday() + 1)
    if start.weekday() != 6:  # Sunday = 6
        start -= timedelta(days=(start.weekday() + 1) % 7)

    cells = []
    for col in range(COLS):
        for row in range(ROWS):
            d = start + timedelta(days=col * 7 + row)
            if d > today:
                continue
            ds = d.isoformat()
            cnt = grid.get(ds, 0)
            lv = min(cnt, len(PALETTE) - 1)  # data-level is already 0-4
            color = PALETTE[lv]
            x = MARGIN_LEFT + col * STEP
            y = MARGIN_TOP + LABEL_H + row * STEP
            # diagonal delay: col + row, normalised
            delay = (col + row) * 18
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" '
                f'fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" dur="120ms" '
                f'begin="{delay}ms" fill="freeze"/>'
                f'</rect>'
            )

    # month labels
    month_labels = []
    seen = set()
    for col in range(COLS):
        d = start + timedelta(days=col * 7)
        key = (d.year, d.month)
        if key not in seen:
            seen.add(key)
            x = MARGIN_LEFT + col * STEP
            month_labels.append(
                f'<text x="{x}" y="{MARGIN_TOP + 10}" fill="#8b949e" '
                f'font-size="10" font-family="monospace">{d.strftime("%b")}</text>'
            )

    # day labels (Mon, Wed, Fri)
    day_labels = []
    for row, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = MARGIN_TOP + LABEL_H + row * STEP + CELL - 2
        day_labels.append(
            f'<text x="0" y="{y}" fill="#8b949e" font-size="10" '
            f'font-family="monospace">{label}</text>'
        )

    # legend
    n = len(PALETTE)
    leg_x = WIDTH - n * (CELL + 2) - 50
    leg_y = HEIGHT - 14
    legend_cells = "".join(
        f'<rect x="{leg_x + i * (CELL + 2)}" y="{leg_y}" width="{CELL}" height="{CELL}" '
        f'rx="2" fill="{PALETTE[i]}"/>'
        for i in range(n)
    )
    legend = (
        f'<text x="{leg_x - 28}" y="{leg_y + 10}" fill="#8b949e" font-size="10" '
        f'font-family="monospace">Less</text>'
        f'{legend_cells}'
        f'<text x="{leg_x + n * (CELL + 2) + 2}" y="{leg_y + 10}" fill="#8b949e" '
        f'font-size="10" font-family="monospace">More</text>'
    )

    # footer
    active_days = sum(1 for d in data["days"] if d["count"] > 0)
    footer = (
        f'<text x="{MARGIN_LEFT}" y="{HEIGHT - 14}" fill="#8b949e" font-size="10" '
        f'font-family="monospace">{active_days} active days in the last year</text>'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect width="{WIDTH}" height="{HEIGHT}" rx="6" fill="#0d1117"/>
  {"".join(month_labels)}
  {"".join(day_labels)}
  {"".join(cells)}
  {legend}
  {footer}
</svg>'''
    return svg


if __name__ == "__main__":
    data = json.loads(DATA.read_text())
    svg = render(data)
    OUT.write_text(svg)
    print(f"Saved → {OUT}")
