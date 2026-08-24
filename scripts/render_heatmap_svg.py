#!/usr/bin/env python3
"""
Render data/contributions.json as a GitHub-style monochrome box grid that
reveals cell by cell (SMIL). Renders a Less->More legend and streak stats.

Usage:
    python scripts/render_heatmap_svg.py          # -> contrib-heatmap.svg
    STATIC=1 python scripts/render_heatmap_svg.py # final frame, no reveal anim

Output height is auto-computed; the README references it by relative URL so it
scales on its own line below the portrait/info table.
"""
import os
import json
import math
import datetime

# ------------------------------------------------------------------ config
OUT     = "contrib-heatmap.svg"
DATA    = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")

CELL    = 11      # box size
GAP     = 3       # gap between boxes
LEFT    = 20
TOP     = 78
FONT    = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
GLYPH   = "#1f2937"
ACCENT  = "#64748b"
LABEL   = "#94a3b8"

# monochrome slate ramp, level 0 (empty) -> level 4 (busy)
RAMP    = ["#eef1f5", "#cbd5e1", "#94a3b8", "#64748b", "#334155"]
# ------------------------------------------------------------------ /config


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load():
    with open(DATA) as f:
        return json.load(f)


def build():
    d = load()
    days = d["days"]

    # map date -> level
    by = {x["date"]: x["level"] for x in days}
    first = datetime.date.fromisoformat(days[0]["date"])
    last = datetime.date.fromisoformat(days[-1]["date"])

    # grid: columns = weeks, rows = 7 (Mon-first like GitHub mobile? use Sun-first)
    # Build from the first day; pad the leading week with empty cells.
    start_weekday = first.weekday()          # 0=Monday
    nweeks = math.ceil((len(days) + start_weekday) / 7)

    grid = []  # (week, row, level or None)
    cursor = first
    idx = 0
    placed = {}
    for day in days:
        placed[day["date"]] = day["level"]
    for week in range(nweeks):
        for row in range(7):
            # day-of-week offset: row 0 = Sunday
            day = first + datetime.timedelta(days=(week * 7 + row - start_weekday))
            if day < first or day > last:
                level = None
            else:
                level = placed.get(day.isoformat(), 0)
            grid.append((week, row, level))

    W = LEFT * 2 + int(nweeks * (CELL + GAP))
    H = TOP + 7 * (CELL + GAP) + 70

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">'
    )
    # background
    svg.append(f'<rect width="{W}" height="{H}" fill="none"/>')

    # header stats
    total = d.get("total", sum(x["level"] for x in days))
    cur = d.get("current_streak", 0)
    longest = d.get("longest_streak", 0)
    svg.append(f'<text x="{LEFT}" y="34" font-size="15" font-weight="700" fill="{GLYPH}">'
               f'{total} contributions in the last year</text>')
    svg.append(f'<text x="{LEFT}" y="60" font-size="13" fill="{ACCENT}">'
               f'current streak {cur}  ·  longest streak {longest}  ·  '
               f'@{esc(d["user"])}</text>')

    # month labels across the top (every ~4 weeks)
    month_lbl = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
    seen = {}
    for week in range(nweeks):
        for row in range(7):
            day = first + datetime.timedelta(days=(week * 7 + row - start_weekday))
            if day < first or day > last:
                continue
            key = (day.year, day.month)
            if key not in seen:
                seen[key] = week
    # place month labels, but only where there is horizontal room (avoid crowding)
    last_x = -99
    min_gap = 26   # pixels of space required between labels
    for (yr, mo), wk in seen.items():
        if wk < nweeks:
            x = LEFT + wk * (CELL + GAP)
            if x - last_x >= min_gap:
                svg.append(f'<text x="{x}" y="70" font-size="10" fill="{LABEL}">'
                           f'{month_lbl[mo]}</text>')
                last_x = x

    # day-of-week labels
    for row, name in [(0, "S"), (2, "M"), (4, "W"), (6, "F")]:
        y = TOP + row * (CELL + GAP) + CELL * 0.8
        svg.append(f'<text x="{LEFT-10}" y="{y:.0f}" font-size="9" fill="{LABEL}">{name}</text>')

    # cells
    static = os.environ.get("STATIC", "0") == "1"
    step = 0.006   # seconds between each cell reveal
    for i, (week, row, level) in enumerate(grid):
        if level is None:
            continue
        x = LEFT + week * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        col = RAMP[level]
        rect = f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{col}"'
        if level == 0:
            rect += ' opacity="0.3"'
        if static:
            rect += '/>'
        else:
            rect += (f'><animate attributeName="opacity" from="0" to="{"0.3" if level==0 else "1"}" '
                     f'begin="{i*step:.3f}s" dur="0.35s" fill="freeze"/></rect>')
        svg.append(rect)

    # legend
    ly = H - 28
    svg.append(f'<text x="{LEFT}" y="{ly}" font-size="11" fill="{ACCENT}">Less</text>')
    lx = LEFT + 44
    for lvl in range(5):
        svg.append(f'<rect x="{lx}" y="{ly-11}" width="{CELL}" height="{CELL}" '
                   f'rx="2.5" fill="{RAMP[lvl]}" opacity="{"0.3" if lvl==0 else "1"}"/>')
        lx += CELL + 5
    svg.append(f'<text x="{lx}" y="{ly}" font-size="11" fill="{ACCENT}">More</text>')

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    print(f"wrote {OUT}  ({W}x{H}, {nweeks} weeks, {len([g for g in grid if g[2] is not None])} cells)"
          + ("  [STATIC]" if static else "  [animated]"))


if __name__ == "__main__":
    build()
