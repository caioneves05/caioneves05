"""
Generates info-card.svg — neofetch-style terminal card with Caio's info.
Animated: each line fades in with a staggered delay.
Set STATIC=1 env var to skip animation (for previews).
"""

import os
from pathlib import Path

OUT = Path(__file__).parent.parent / "info-card.svg"
STATIC = os.getenv("STATIC") == "1"

WIDTH = 640
LINE_H = 22
PADDING_X = 20
PADDING_Y = 16
FONT = "monospace"

ACCENT = "#39d353"
DIM = "#8b949e"
WHITE = "#e6edf3"
YELLOW = "#e3b341"
BLUE = "#79c0ff"
PINK = "#f778ba"
CYAN = "#56d364"

# (label_color, label, value_color, value)
LINES = [
    (ACCENT,  "caio",        WHITE,  "@github"),
    (DIM,     "─" * 20,      DIM,    ""),
    (YELLOW,  "role",        WHITE,  "Full Stack Engineer · Mobile Developer"),
    (YELLOW,  "location",    WHITE,  "Brazil 🇧🇷"),
    (YELLOW,  "experience",  WHITE,  "4+ years"),
    (DIM,     "",            DIM,    ""),
    (BLUE,    "stack",       WHITE,  "Java · TypeScript · Node.js · React Native"),
    (BLUE,    "",            WHITE,  "NestJS · GraphQL · Prisma · AWS"),
    (DIM,     "",            DIM,    ""),
    (PINK,    "building",    WHITE,  "Meu Acerto — CLT workers rights app"),
    (PINK,    "open source", WHITE,  "simba-core — NestJS/GraphQL boilerplate"),
    (DIM,     "",            DIM,    ""),
    (CYAN,    "github",      WHITE,  "github.com/caioneves05"),
    (CYAN,    "linkedin",    WHITE,  "linkedin.com/in/caioneves05"),
    (CYAN,    "portfolio",   WHITE,  "caioneves.tech"),
    (DIM,     "",            DIM,    ""),
    (DIM,     "palette",     DIM,    ""),  # color dots row
]

COLOR_DOTS = ["#ff6b6b", "#ffa94d", "#ffd43b", "#69db7c", "#4dabf7", "#cc5de8", "#f783ac", "#a9e34b"]

TITLE_H = 32
HEIGHT = PADDING_Y * 2 + TITLE_H + len(LINES) * LINE_H + 8


def anim(i: int) -> str:
    if STATIC:
        return ""
    delay = i * 60
    return (
        f' opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="80ms" '
        f'begin="{delay}ms" fill="freeze"/>'
        f'</g'
    )


def render() -> str:
    parts = []

    # background
    parts.append(
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="8" fill="#0d1117"/>'
    )

    # title bar
    parts.append(
        f'<rect width="{WIDTH}" height="{TITLE_H}" rx="8" fill="#161b22"/>'
        f'<rect y="20" width="{WIDTH}" height="12" fill="#161b22"/>'
    )
    # traffic lights
    for i, col in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        cx = 16 + i * 20
        parts.append(f'<circle cx="{cx}" cy="16" r="6" fill="{col}"/>')

    # title text
    parts.append(
        f'<text x="{WIDTH // 2}" y="20" text-anchor="middle" fill="{WHITE}" '
        f'font-size="12" font-family="{FONT}">caioneves05 — zsh</text>'
    )

    # lines
    for i, (lc, label, vc, value) in enumerate(LINES):
        y = PADDING_Y + TITLE_H + i * LINE_H + LINE_H

        if label == "palette":
            # color dots
            dot_x = PADDING_X
            for dot_color in COLOR_DOTS:
                parts.append(
                    f'<rect x="{dot_x}" y="{y - 12}" width="16" height="16" '
                    f'rx="3" fill="{dot_color}"/>'
                )
                dot_x += 22
            continue

        # separator line
        if set(label) == {"─"}:
            parts.append(
                f'<text x="{PADDING_X}" y="{y}" fill="{DIM}" font-size="12" '
                f'font-family="{FONT}">{label}</text>'
            )
            continue

        if label:
            parts.append(
                f'<text x="{PADDING_X}" y="{y}" fill="{lc}" font-size="13" '
                f'font-weight="bold" font-family="{FONT}">{label}</text>'
            )
            # colon
            parts.append(
                f'<text x="{PADDING_X + 88}" y="{y}" fill="{DIM}" font-size="13" '
                f'font-family="{FONT}">:</text>'
            )
        if value:
            vx = PADDING_X + (100 if label else 108)
            parts.append(
                f'<text x="{vx}" y="{y}" fill="{vc}" font-size="13" '
                f'font-family="{FONT}">{value}</text>'
            )

    if not STATIC:
        # wrap each text group in animated g tags — simpler: animate the whole card
        # use a single fade-in-lines approach via CSS keyframes inside SVG
        pass

    # stagger animation via individual opacity on each text line
    # rebuild with animation wrappers
    animated_parts = [parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]]  # bg + titlebar + dots + title
    text_parts = parts[6:]

    delay_step = 50
    wrapped = []
    for idx, p in enumerate(text_parts):
        if STATIC:
            wrapped.append(f'<g>{p}</g>')
        else:
            delay = idx * delay_step
            wrapped.append(
                f'<g opacity="0">'
                f'{p}'
                f'<animate attributeName="opacity" from="0" to="1" dur="80ms" '
                f'begin="{delay}ms" fill="freeze"/>'
                f'</g>'
            )

    all_parts = animated_parts + wrapped
    inner = "\n  ".join(all_parts)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  {inner}
</svg>'''


if __name__ == "__main__":
    svg = render()
    OUT.write_text(svg)
    print(f"Saved → {OUT}")
