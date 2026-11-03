"""
Converts source-prepped.png to caio-ascii.svg.
Renders each character as a <text> element; each row animates via a
horizontal clip that sweeps left to right (SMIL), staggered top-to-bottom.
Output: caio-ascii.svg (840x880 to match stats.svg dimensions).
"""

from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path("source-prepped.png")
OUT = Path("caio-ascii.svg")

# target SVG canvas
SVG_W, SVG_H = 840, 880

# ascii density ramp: space (bright) → @ (dark)
RAMP = ' .`:-=+*cs#%@'
COLS = 80
FONT_SIZE = 10
CHAR_W = SVG_W / COLS
CHAR_H = CHAR_W * 2.1  # monospace aspect ratio
ROWS = int(SVG_H / CHAR_H)

FG = "#c9d1d9"   # github light gray foreground


def img_to_ascii(img: Image.Image) -> list[str]:
    img = img.convert("L").resize((COLS, ROWS), Image.LANCZOS)
    arr = np.array(img)
    lines = []
    for row in arr:
        chars = "".join(RAMP[int(p / 255 * (len(RAMP) - 1))] for p in row)
        lines.append(chars)
    return lines


def render(lines: list[str]) -> str:
    rows_svg = []
    row_h = SVG_H / len(lines)
    anim_dur = 120  # ms per row

    for i, line in enumerate(lines):
        y = (i + 1) * row_h
        clip_id = f"c{i}"
        delay = i * anim_dur

        # clip rect that sweeps left → right
        clip = (
            f'<clipPath id="{clip_id}">'
            f'<rect x="0" y="{y - row_h:.1f}" width="0" height="{row_h:.1f}">'
            f'<animate attributeName="width" from="0" to="{SVG_W}" '
            f'dur="{anim_dur}ms" begin="{delay}ms" fill="freeze"/>'
            f'</rect>'
            f'</clipPath>'
        )

        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = (
            f'<text x="0" y="{y:.1f}" clip-path="url(#{clip_id})" '
            f'fill="{FG}" font-size="{FONT_SIZE}" font-family="monospace" '
            f'xml:space="preserve">{escaped}</text>'
        )

        rows_svg.append(clip + text)

    defs = "<defs>" + "".join(
        f'<clipPath id="c{i}"><rect x="0" y="{(i+1)*row_h - row_h:.1f}" '
        f'width="0" height="{row_h:.1f}">'
        f'<animate attributeName="width" from="0" to="{SVG_W}" '
        f'dur="{anim_dur}ms" begin="{i * anim_dur}ms" fill="freeze"/>'
        f'</rect></clipPath>'
        for i in range(len(lines))
    ) + "</defs>"

    texts = "".join(
        f'<text x="0" y="{(i+1)*row_h:.1f}" clip-path="url(#c{i})" '
        f'fill="{FG}" font-size="{FONT_SIZE}" font-family="monospace" '
        f'xml:space="preserve">{lines[i].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</text>'
        for i in range(len(lines))
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}">\n'
        f'  <rect width="{SVG_W}" height="{SVG_H}" fill="#0d1117"/>\n'
        f'  {defs}\n'
        f'  {texts}\n'
        f'</svg>'
    )


if __name__ == "__main__":
    img = Image.open(SRC)
    lines = img_to_ascii(img)
    svg = render(lines)
    OUT.write_text(svg)
    print(f"Saved → {OUT}  ({len(lines)} rows)")
