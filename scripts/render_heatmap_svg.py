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
TITLE   = "#1e293b"
ACCENT  = "#475569"
LABEL   = "#94a3b8"

# Multiple color schemes available for the heatmap. Each is a 5-step ramp
# from level 0 (empty) -> level 4 (busy). Schemes use vivid spectrum colors
# (not just grey) so the heatmap reads as colorful like the streak graph.
# Set HEATMAP_SCHEME to one of the keys below.
COLOR_SCHEMES = {
    # Sunset: warm orange -> red
    "sunset":  ["#fff7ed", "#fed7aa", "#fb923c", "#ea580c", "#9a3412"],
    # Ocean: teal -> deep blue
    "ocean":   ["#f0fdfa", "#99f6e4", "#2dd4bf", "#0e7490", "#0c4a6e"],
    # Forest: lime -> deep green
    "forest":  ["#f7fee7", "#bef264", "#84cc16", "#15803d", "#14532d"],
    # Candy: pink -> magenta
    "candy":   ["#fdf2f8", "#f9a8d4", "#f472b6", "#be185d", "#831843"],
    # Spectrum: full rainbow (most colorful)
    "spectrum":["#fef3c7", "#fde68a", "#a78bfa", "#7c3aed", "#4338ca"],
    # Aurora: blue -> violet -> rose (matches the photo-reveal cycle)
    "aurora":  ["#ecfeff", "#a5f3fc", "#818cf8", "#7c3aed", "#be185d"],
}

HEATMAP_SCHEME     = "aurora"
ANIMATE_HUE_CYCLE  = True
HUE_CYCLE_S        = 18   # seconds for full hue cycle on level-3/4 cells
# ------------------------------------------------------------------ /config


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load():
    with open(DATA) as f:
        return json.load(f)


def build():
    d = load()
    days = d["days"]

    # resolve color scheme (env override for quick testing)
    scheme_name = os.environ.get("HEATMAP_SCHEME", HEATMAP_SCHEME)
    if scheme_name not in COLOR_SCHEMES:
        scheme_name = "aurora"
    ramp = COLOR_SCHEMES[scheme_name]

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
    svg.append(f'<text x="{LEFT}" y="34" font-size="15" font-weight="700" fill="{TITLE}">'
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

    # Animated hue cycle for level-3 and level-4 cells. We rotate each cell's
    # hue through the full spectrum slowly so the heatmap feels alive without
    # being distracting. Levels 0-2 stay static (they're background-ish).
    if ANIMATE_HUE_CYCLE and not static:
        # Cycle: 8 stops sampled from the same color spectrum used by the photo
        # reveal so the two animations feel like one continuous "look".
        hue_palette = [
            "#7c3aed",   # violet
            "#9333ea",   # purple
            "#be185d",   # rose
            "#dc2626",   # red
            "#ea580c",   # orange
            "#0891b2",   # cyan
            "#1e3a8a",   # indigo
            "#7c3aed",   # violet (loop)
        ]
        hue_values = ";".join(hue_palette)
        hue_keytimes = ";".join(f"{i/(len(hue_palette)-1):.3f}" for i in range(len(hue_palette)))
        # small stagger so the wave moves across the canvas
        col_stagger = 0.05

    for i, (week, row, level) in enumerate(grid):
        if level is None:
            continue
        x = LEFT + week * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        col = ramp[level]
        op = "0.3" if level == 0 else "1"

        # Hue cycle only on the busiest cells (level 3, 4) so the eye is drawn
        # to active contributions, not the empty space.
        if (ANIMATE_HUE_CYCLE and not static
                and level >= 3):
            cell_begin = (i * step) + (week * col_stagger)
            rect = (
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{col}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="{op}" '
                f'begin="{cell_begin:.3f}s" dur="0.35s" fill="freeze"/>'
                f'<animate attributeName="fill" '
                f'values="{hue_values}" keyTimes="{hue_keytimes}" '
                f'begin="{cell_begin + HUE_CYCLE_S*0.6:.3f}s" '
                f'dur="{HUE_CYCLE_S}s" repeatCount="indefinite"/>'
                f'</rect>'
            )
        else:
            rect = f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{col}"'
            if level == 0:
                rect += ' opacity="0.3"'
            if static:
                rect += '/>'
            else:
                rect += (f'><animate attributeName="opacity" from="0" to="{op}" '
                         f'begin="{i*step:.3f}s" dur="0.35s" fill="freeze"/></rect>')
        svg.append(rect)

    # legend (uses the active scheme)
    ly = H - 28
    svg.append(f'<text x="{LEFT}" y="{ly}" font-size="11" fill="{ACCENT}">Less</text>')
    lx = LEFT + 44
    for lvl in range(5):
        svg.append(f'<rect x="{lx}" y="{ly-11}" width="{CELL}" height="{CELL}" '
                   f'rx="2.5" fill="{ramp[lvl]}" opacity="{"0.3" if lvl==0 else "1"}"/>')
        lx += CELL + 5
    svg.append(f'<text x="{lx}" y="{ly}" font-size="11" fill="{ACCENT}">More</text>')

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    print(f"wrote {OUT}  ({W}x{H}, {nweeks} weeks, "
          f"{len([g for g in grid if g[2] is not None])} cells, scheme={scheme_name})"
          + ("  [STATIC]" if static else "  [animated]"))


if __name__ == "__main__":
    build()
