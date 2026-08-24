#!/usr/bin/env python3
"""
Scrape a GitHub user's contribution calendar (zero auth) and save it as JSON.

Usage:
    GH_PROFILE_USER=your_username python scripts/fetch_contributions.py

Writes data/contributions.json:
    {
      "user": "ather-ops",
      "scraped": <iso-timestamp>,
      "first_year": "2025-08-24",
      "last_year": "2026-08-23",
      "total": 514,
      "current_streak": 12,
      "longest_streak": 22,
      "days": [ {"date": "2025-08-24", "level": 0}, ... ]
    }
"""
import os
import re
import json
import datetime
import urllib.request

# ------------------------------------------------------------------ config
USER = os.environ.get("GH_PROFILE_USER")
if not USER:
    USER = "ather-ops"
    print("GH_PROFILE_USER not set; defaulting to ather-ops")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
# ------------------------------------------------------------------ /config

LEVELS = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4}


def fetch_html(user):
    url = f"https://github.com/users/{user}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse(html):
    # each cell: data-date="YYYY-MM-DD" data-level="0..4"
    cells = re.findall(
        r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"', html
    )
    if not cells:
        # some pages put data-level first
        cells = re.findall(
            r'data-level="(\d)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', html
        )
        cells = [(d, l) for l, d in cells]
    days = []
    for date, level in cells:
        days.append({"date": date, "level": LEVELS.get(level, 0)})
    days.sort(key=lambda d: d["date"])
    return days


def streaks(days):
    total = sum(d["level"] for d in days)
    cur = 0
    longest = 0
    run = 0
    for d in days:
        if d["level"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    # current streak: count back from the most recent non-empty day
    # (allow today to be zero; start from the last day with activity)
    seen_none_today = False
    cur = 0
    for d in reversed(days):
        if d["level"] > 0:
            cur += 1
        else:
            # only break if this zero day is not today (today may still be pending)
            if d["date"] != datetime.date.today().isoformat():
                break
    return total, longest, cur


def main():
    html = fetch_html(USER)
    days = parse(html)
    if not days:
        raise SystemExit("could not parse any contribution cells")
    total, longest, cur = streaks(days)
    data = {
        "user": USER,
        "scraped": datetime.datetime.now().isoformat(timespec="seconds"),
        "first_year": days[0]["date"][:4],
        "last_year": days[-1]["date"][:4],
        "total": total,
        "current_streak": cur,
        "longest_streak": longest,
        "days": days,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {OUT}")
    print(f"  user={USER}  days={len(days)}  total={total}  "
          f"current_streak={cur}  longest_streak={longest}  "
          f"range={days[0]['date']}..{days[-1]['date']}")


if __name__ == "__main__":
    main()
