#!/usr/bin/env python3
"""
Render data/contributions.json as a GitHub-style box grid with a cinematic
cell-by-cell reveal and several continuous "living" effects.

Usage:
    python scripts/render_heatmap_svg.py          # -> contrib-heatmap.svg
    STATIC=1 python scripts/render_heatmap_svg.py # final frame, no reveal anim

Output height is auto-computed; the README references it by relative URL so it
scales on its own line below the portrait/info table.

PORTABILITY RULES (keep them):
    1. Animated elements carry their FINAL visible state in the base
       attributes; never base opacity="0" or static renderers show a blank
       grid.
    2. No mix-blend-mode.
    3. Text content goes INSIDE <text>, before any <animate>.
    4. Avoid gradient stop-opacity="0" on large fills.
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
# from level 0 (empty) -> level 4 (busy).
COLOR_SCHEMES = {
    "sunset":  ["#fff7ed", "#fed7aa", "#fb923c", "#ea580c", "#9a3412"],
    "ocean":   ["#f0fdfa", "#99f6e4", "#2dd4bf", "#0e7490", "#0c4a6e"],
    "forest":  ["#f7fee7", "#bef264", "#84cc16", "#15803d", "#14532d"],
    "candy":   ["#fdf2f8", "#f9a8d4", "#f472b6", "#be185d", "#831843"],
    "spectrum":["#fef3c7", "#fde68a", "#a78bfa", "#7c3aed", "#4338ca"],
    "aurora":  ["#ecfeff", "#a5f3fc", "#818cf8", "#7c3aed", "#be185d"],
}

HEATMAP_SCHEME    = "aurora"
ANIMATE_HUE_CYCLE = True
HUE_CYCLE_S       = 18   # seconds for full hue cycle on level-3/4 cells

# next-level timings
REVEAL_STEP   = 0.004   # seconds between each cell reveal
WAVE_PERIOD   = 4.2     # diagonal "breathing wave" across the grid
SCAN_PERIOD   = 9.0     # horizontal scan highlight sweep
# ------------------------------------------------------------------ /config


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load():
    with open(DATA) as f:
        return json.load(f)


def build():
    d = load()
    days = d["days"]

    scheme_name = os.environ.get("HEATMAP_SCHEME", HEATMAP_SCHEME)
    if scheme_name not in COLOR_SCHEMES:
        scheme_name = "aurora"
    ramp = COLOR_SCHEMES[scheme_name]

    by = {x["date"]: x["level"] for x in days}
    first = datetime.date.fromisoformat(days[0]["date"])
    last = datetime.date.fromisoformat(days[-1]["date"])

    start_weekday = first.weekday()          # 0=Monday
    nweeks = math.ceil((len(days) + start_weekday) / 7)

    grid = []
    placed = {x["date"]: x["level"] for x in days}
    for week in range(nweeks):
        for row in range(7):
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
    svg.append(f'<rect width="{W}" height="{H}" fill="none"/>')

    # ---- defs -------------------------------------------------------------
    svg.append(
        '<defs>'
        '<radialGradient id="stat-halo" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#a5f3fc"/>'
        '<stop offset="0.55" stop-color="#ecfeff"/>'
        '<stop offset="1" stop-color="#ffffff"/>'
        '</radialGradient>'
        '<linearGradient id="scan-grad" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="#ffffff" stop-opacity="0.85"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
        '</linearGradient>'
        '</defs>'
    )

    # ---- header stats ------------------------------------------------------
    total = d.get("total", sum(x["level"] for x in days))
    cur = d.get("current_streak", 0)
    longest = d.get("longest_streak", 0)

    # pulsing halo behind the headline number
    svg.append(
        f'<ellipse cx="{LEFT+92}" cy="27" rx="150" ry="30" '
        f'fill="url(#stat-halo)" opacity="0.45">'
        f'<animate attributeName="opacity" values="0.45;0.18;0.45" '
        f'dur="{WAVE_PERIOD}s" repeatCount="indefinite"/>'
        f'</ellipse>'
    )
    svg.append(
        f'<text x="{LEFT}" y="34" font-size="15" font-weight="700" fill="{TITLE}">'
        f'{total} contributions in the last year'
        f'<animate attributeName="opacity" values="1;0.6;1" '
        f'dur="{WAVE_PERIOD}s" repeatCount="indefinite"/>'
        f'</text>'
    )
    svg.append(
        f'<text x="{LEFT}" y="60" font-size="13" fill="{ACCENT}">'
        f'current streak {cur}  ·  longest streak {longest}  ·  @{esc(d["user"])}'
        f'</text>'
    )

    # ---- month labels ------------------------------------------------------
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
    last_x = -99
    min_gap = 26
    for (yr, mo), wk in seen.items():
        if wk < nweeks:
            x = LEFT + wk * (CELL + GAP)
            if x - last_x >= min_gap:
                svg.append(
                    f'<text x="{x}" y="70" font-size="10" fill="{LABEL}">'
                    f'{month_lbl[mo]}'
                    f'<animate attributeName="opacity" values="1;0.45;1" '
                    f'dur="{WAVE_PERIOD}s" repeatCount="indefinite"/>'
                    f'</text>'
                )
                last_x = x

    # ---- day-of-week labels -------------------------------------------------
    for row, name in [(0, "S"), (2, "M"), (4, "W"), (6, "F")]:
        y = TOP + row * (CELL + GAP) + CELL * 0.8
        svg.append(f'<text x="{LEFT-10}" y="{y:.0f}" font-size="9" fill="{LABEL}">{name}</text>')

    # ---- cells --------------------------------------------------------------
    static = os.environ.get("STATIC", "0") == "1"
    step = REVEAL_STEP

    if ANIMATE_HUE_CYCLE and not static:
        hue_palette = [
            "#7c3aed", "#9333ea", "#be185d", "#dc2626",
            "#ea580c", "#0891b2", "#1e3a8a", "#7c3aed",
        ]
        hue_values = ";".join(hue_palette)
        hue_keytimes = ";".join(
            f"{i/(len(hue_palette)-1):.3f}" for i in range(len(hue_palette))
        )
        col_stagger = 0.05

    for i, (week, row, level) in enumerate(grid):
        if level is None:
            continue
        x = LEFT + week * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        col = ramp[level]
        op = "0.3" if level == 0 else "1"

        # hover: cell lifts and brightens
        svg.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{ACCENT}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="0.28" dur="0.15s" '
            f'begin="mouseover" fill="freeze"/>'
            f'<animate attributeName="opacity" from="0.28" to="0" dur="0.3s" '
            f'begin="mouseout" fill="freeze"/>'
            f'</rect>'
        )

        if (ANIMATE_HUE_CYCLE and not static and level >= 3):
            cell_begin = (i * step) + (week * col_stagger)
            rect = (
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{col}" opacity="{op}">'
                f'<animate attributeName="opacity" from="0" to="{op}" '
                f'begin="{cell_begin:.3f}s" dur="0.35s" fill="freeze"/>'
                f'<animate attributeName="fill" '
                f'values="{hue_values}" keyTimes="{hue_keytimes}" '
                f'begin="{cell_begin + HUE_CYCLE_S*0.6:.3f}s" '
                f'dur="{HUE_CYCLE_S}s" repeatCount="indefinite"/>'
                # gentle scale pulse on the busiest cells
                f'<animate attributeName="rx" values="2.5;4;2.5" '
                f'dur="3.1s" begin="{cell_begin:.3f}s" repeatCount="indefinite"/>'
                f'</rect>'
            )
        elif static:
            rect = (f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                    f'rx="2.5" fill="{col}" opacity="{op}"/>')
        else:
            # base state is fully visible (safe for static renderers);
            # the reveal animation fades it in on load.
            rect = (
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{col}" opacity="{op}">'
                f'<animate attributeName="opacity" from="0" to="{op}" '
                f'begin="{i*step:.3f}s" dur="0.35s" fill="freeze"/>'
                # diagonal breathing wave across the whole grid
                f'<animate attributeName="opacity" '
                f'values="{op};{min(1.0, float(op)+0.35)};{op}" '
                f'dur="{WAVE_PERIOD}s" '
                f'begin="{(i*step) + (week+row)*0.12:.3f}s" repeatCount="indefinite"/>'
                f'</rect>'
            )
        svg.append(rect)

    # ---- horizontal scan highlight sweeping the grid -----------------------
    band_w = 180
    grid_top = TOP - 6
    grid_bot = TOP + 7 * (CELL + GAP) + 6
    svg.append(
        f'<rect x="{-band_w}" y="{grid_top}" width="{band_w}" '
        f'height="{grid_bot-grid_top}" fill="url(#scan-grad)" opacity="0.5" '
        f'pointer-events="none">'
        f'<animate attributeName="x" from="{-band_w}" to="{W}" '
        f'dur="{SCAN_PERIOD}s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    # ---- legend -------------------------------------------------------------
    ly = H - 28
    svg.append(f'<text x="{LEFT}" y="{ly}" font-size="11" fill="{ACCENT}">Less</text>')
    lx = LEFT + 44
    for lvl in range(5):
        svg.append(
            f'<rect x="{lx}" y="{ly-11}" width="{CELL}" height="{CELL}" '
            f'rx="2.5" fill="{ramp[lvl]}" opacity="{"0.3" if lvl==0 else "1"}">'
            f'<animate attributeName="opacity" '
            f'values="{"0.3" if lvl==0 else "1"};'
            f'{min(1.0, (0.3 if lvl==0 else 1.0)+0.35)};'
            f'{"0.3" if lvl==0 else "1"}" '
            f'dur="{WAVE_PERIOD}s" begin="{lvl*0.12:.2f}s" repeatCount="indefinite"/>'
            f'</rect>'
        )
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
