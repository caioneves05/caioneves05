"""
Fetches contribution data from GitHub's public contributions page.
No token required — parses the public HTML endpoint.
Outputs data/contributions.json.
"""

import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "caioneves05"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).parent.parent / "data" / "contributions.json"


def fetch() -> dict:
    resp = requests.get(URL, headers={"Accept": "text/html"}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    for td in soup.select("td[data-date]"):
        raw_date = td["data-date"]
        count_text = td.get("data-level", "0")
        tooltip = td.get("aria-label", "")
        # extract count from aria-label e.g. "3 contributions on January 1st"
        m = re.search(r"(\d+)\s+contribution", tooltip)
        count = int(m.group(1)) if m else 0
        days.append({"date": raw_date, "count": count})

    if not days:
        print("No contribution data found — check the HTML structure.", file=sys.stderr)
        sys.exit(1)

    days.sort(key=lambda d: d["date"])

    # streak
    streak = 0
    max_streak = 0
    cur = 0
    for d in reversed(days):
        if d["count"] > 0:
            cur += 1
            streak = cur
        else:
            if cur > max_streak:
                max_streak = cur
            cur = 0
    if cur > max_streak:
        max_streak = cur

    best = max(days, key=lambda d: d["count"])
    total = sum(d["count"] for d in days)

    # monthly totals
    monthly: dict[str, int] = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + d["count"]

    result = {
        "generated": date.today().isoformat(),
        "username": USERNAME,
        "total": total,
        "streak": streak,
        "max_streak": max_streak,
        "best_day": best,
        "monthly": monthly,
        "days": days,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2))
    print(f"Saved {len(days)} days → {OUT}")
    return result


if __name__ == "__main__":
    fetch()
