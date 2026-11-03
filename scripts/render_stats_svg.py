"""
Generates stats.svg from data/contributions.json.
Shows streak, contribution stats, and profile info.
Dimensions: 840x880 (matches caio-ascii.svg for side-by-side layout).
"""

import json
from pathlib import Path

DATA = Path("data/contributions.json")
OUT = Path("stats.svg")

W, H = 840, 880
PAD = 32
FONT = "monospace"

GREEN = "#39d353"
DIM = "#8b949e"
WHITE = "#e6edf3"
YELLOW = "#e3b341"
BLUE = "#79c0ff"
PINK = "#f778ba"
CYAN = "#56d364"
BG = "#0d1117"
CARD = "#161b22"
BORDER = "#30363d"


def bar(value: int, max_value: int, width: int = 600, height: int = 8) -> str:
    filled = int(width * min(value / max(max_value, 1), 1))
    return (
        f'<rect width="{width}" height="{height}" rx="4" fill="{BORDER}"/>'
        f'<rect width="{filled}" height="{height}" rx="4" fill="{GREEN}"/>'
    )


def render(data: dict) -> str:
    streak = data.get("streak", 0)
    max_streak = data.get("max_streak", 0)
    active_days = sum(1 for d in data["days"] if d["count"] > 0)
    total_days = len(data["days"])
    best = data.get("best_day", {})

    # monthly activity for sparkline
    months = list(data.get("monthly", {}).items())[-12:]
    max_month = max((v for _, v in months), default=1)

    lines = []

    def text(x, y, content, color=WHITE, size=14, bold=False, delay=0):
        weight = 'font-weight="bold"' if bold else ""
        anim = (
            f'<animate attributeName="opacity" from="0" to="1" '
            f'dur="80ms" begin="{delay}ms" fill="freeze"/>'
            if delay >= 0 else ""
        )
        op = ' opacity="0"' if delay >= 0 else ""
        lines.append(
            f'<text x="{x}" y="{y}"{op} fill="{color}" font-size="{size}" '
            f'font-family="{FONT}" {weight}>{content}{anim}</text>'
        )

    def label_val(x, y, label, value, lc=YELLOW, vc=WHITE, delay=0):
        op = ' opacity="0"' if delay >= 0 else ""
        anim = (
            f'<animate attributeName="opacity" from="0" to="1" '
            f'dur="80ms" begin="{delay}ms" fill="freeze"/>'
        )
        lines.append(
            f'<g{op}>'
            f'<text x="{x}" y="{y}" fill="{lc}" font-size="13" font-family="{FONT}" font-weight="bold">{label}</text>'
            f'<text x="{x + 160}" y="{y}" fill="{DIM}" font-size="13" font-family="{FONT}">:</text>'
            f'<text x="{x + 172}" y="{y}" fill="{vc}" font-size="13" font-family="{FONT}">{value}</text>'
            f'{anim}'
            f'</g>'
        )

    # background + border
    lines.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    lines.append(f'<rect width="{W}" height="{H}" rx="8" fill="none" stroke="{BORDER}" stroke-width="1"/>')

    # title bar
    lines.append(f'<rect width="{W}" height="36" rx="8" fill="{CARD}"/>')
    lines.append(f'<rect y="24" width="{W}" height="12" fill="{CARD}"/>')
    for i, col in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        lines.append(f'<circle cx="{16 + i * 20}" cy="18" r="6" fill="{col}"/>')
    lines.append(
        f'<text x="{W//2}" y="23" text-anchor="middle" fill="{WHITE}" '
        f'font-size="12" font-family="{FONT}">caioneves05 — stats</text>'
    )

    y = 80
    d = 0  # animation delay counter

    # streak section
    lines.append(f'<text x="{PAD}" y="{y}" fill="{GREEN}" font-size="13" font-family="{FONT}" font-weight="bold" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="80ms" begin="{d}ms" fill="freeze"/>caio@github ~ $ ./streak.sh</text>')
    y += 28; d += 60

    # big streak number
    lines.append(
        f'<text x="{PAD}" y="{y + 60}" fill="{GREEN}" font-size="96" font-family="{FONT}" '
        f'font-weight="bold" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="80ms" begin="{d}ms" fill="freeze"/>'
        f'{streak}</text>'
    )
    lines.append(
        f'<text x="{PAD + 110}" y="{y + 44}" fill="{DIM}" font-size="14" font-family="{FONT}" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="80ms" begin="{d}ms" fill="freeze"/>'
        f'day streak</text>'
    )
    lines.append(
        f'<text x="{PAD + 110}" y="{y + 66}" fill="{DIM}" font-size="12" font-family="{FONT}" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="80ms" begin="{d}ms" fill="freeze"/>'
        f'best: {max_streak} days</text>'
    )
    # streak bar
    bar_w = W - PAD * 2
    filled_w = int(bar_w * min(streak / max(max_streak, 1), 1))
    lines.append(
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="80ms" begin="{d+40}ms" fill="freeze"/>'
        f'<rect x="{PAD}" y="{y + 80}" width="{bar_w}" height="6" rx="3" fill="{BORDER}"/>'
        f'<rect x="{PAD}" y="{y + 80}" width="{filled_w}" height="6" rx="3" fill="{GREEN}"/>'
        f'</g>'
    )
    y += 110; d += 60

    # divider
    lines.append(f'<line x1="{PAD}" y1="{y}" x2="{W - PAD}" y2="{y}" stroke="{BORDER}" stroke-width="1" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="80ms" begin="{d}ms" fill="freeze"/></line>')
    y += 24; d += 40

    # contributions section
    lines.append(f'<text x="{PAD}" y="{y}" fill="{GREEN}" font-size="13" font-family="{FONT}" font-weight="bold" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="80ms" begin="{d}ms" fill="freeze"/>caio@github ~ $ cat activity.txt</text>')
    y += 28; d += 60

    label_val(PAD, y, "active days", f"{active_days} / {total_days}", lc=BLUE, delay=d); y += 22; d += 50
    if best:
        label_val(PAD, y, "best day", f"{best.get('date','')}  (lvl {best.get('count',0)})", lc=BLUE, delay=d)
    y += 28; d += 50

    # monthly sparkline
    lines.append(f'<text x="{PAD}" y="{y}" fill="{DIM}" font-size="11" font-family="{FONT}" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="80ms" begin="{d}ms" fill="freeze"/>monthly activity</text>')
    y += 14; d += 40

    spark_w = (W - PAD * 2) // max(len(months), 1)
    spark_max_h = 48
    for mi, (month, val) in enumerate(months):
        bh = max(2, int(spark_max_h * val / max_month))
        bx = PAD + mi * spark_w
        by = y + spark_max_h - bh
        alpha = 0.4 + 0.6 * (val / max_month)
        lines.append(
            f'<rect x="{bx + 1}" y="{by}" width="{spark_w - 2}" height="{bh}" rx="2" '
            f'fill="{GREEN}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="{alpha:.2f}" '
            f'dur="80ms" begin="{d + mi * 20}ms" fill="freeze"/>'
            f'</rect>'
        )
        label = month[5:]  # MM
        lines.append(
            f'<text x="{bx + spark_w//2}" y="{y + spark_max_h + 14}" text-anchor="middle" '
            f'fill="{DIM}" font-size="9" font-family="{FONT}">{label}</text>'
        )
    y += spark_max_h + 24; d += 60

    # divider
    lines.append(f'<line x1="{PAD}" y1="{y}" x2="{W - PAD}" y2="{y}" stroke="{BORDER}" stroke-width="1" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="80ms" begin="{d}ms" fill="freeze"/></line>')
    y += 24; d += 40

    # profile section
    lines.append(f'<text x="{PAD}" y="{y}" fill="{GREEN}" font-size="13" font-family="{FONT}" font-weight="bold" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="80ms" begin="{d}ms" fill="freeze"/>caio@github ~ $ whoami</text>')
    y += 28; d += 60

    profile = [
        (YELLOW, "os",       WHITE,  "macOS / Linux"),
        (YELLOW, "role",     WHITE,  "Full Stack Engineer"),
        (YELLOW, "location", WHITE,  "Brazil"),
        (DIM,    "",         DIM,    ""),
        (BLUE,   "java",     WHITE,  "Spring Boot · Microservices"),
        (BLUE,   "ts",       WHITE,  "Node.js · NestJS · GraphQL"),
        (BLUE,   "mobile",   WHITE,  "React Native · Expo"),
        (BLUE,   "cloud",    WHITE,  "AWS · Docker · Kubernetes"),
        (DIM,    "",         DIM,    ""),
        (PINK,   "building", WHITE,  "Meu Acerto — CLT app"),
        (CYAN,   "github",   WHITE,  "github.com/caioneves05"),
        (CYAN,   "web",      WHITE,  "caioneves.tech"),
    ]

    for lc, label, vc, value in profile:
        if not label and not value:
            y += 10
            continue
        lx = PAD
        lines.append(
            f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="80ms" begin="{d}ms" fill="freeze"/>'
            f'<text x="{lx}" y="{y}" fill="{lc}" font-size="13" font-family="{FONT}" font-weight="bold">{label}</text>'
            f'<text x="{lx + 76}" y="{y}" fill="{DIM}" font-size="13" font-family="{FONT}">:</text>'
            f'<text x="{lx + 88}" y="{y}" fill="{vc}" font-size="13" font-family="{FONT}">{value}</text>'
            f'</g>'
        )
        y += 22; d += 40

    inner = "\n  ".join(lines)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n  {inner}\n</svg>'


if __name__ == "__main__":
    data = json.loads(DATA.read_text())
    svg = render(data)
    OUT.write_text(svg)
    print(f"Saved → {OUT}")
