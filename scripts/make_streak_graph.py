#!/usr/bin/env python3
"""
Render data/contributions.json as a DAY STREAK bar chart (one bar per day with
contributions) in monochrome slate. Highlights the longest streak and the
current streak so the user can see progress at a glance.

Usage:
    python scripts/make_streak_graph.py          # -> streak-graph.svg (animated)
    STATIC=1 python scripts/make_streak_graph.py # final frame, no reveal anim
"""
import os
import json
import math
import datetime

# ------------------------------------------------------------------ config
OUT     = "streak-graph.svg"
DATA    = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")

# canvas
W           = 880
H           = 280
PAD_L       = 40
PAD_R       = 40
PAD_T       = 78
PAD_B       = 44

FONT    = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
GLYPH   = "#1f2937"
ACCENT  = "#475569"
LABEL   = "#94a3b8"
CUR_HL  = "#1f2937"     # current-streak bar color
LONG_HL = "#475569"     # longest-streak bar color (slightly lighter)

# monochrome ramp (level 0..4 -> fill color)
RAMP    = ["#eef1f5", "#cbd5e1", "#94a3b8", "#64748b", "#334155"]
# ------------------------------------------------------------------ /config


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load():
    with open(DATA) as f:
        return json.load(f)


def daily_streak_runs(days):
    """Return list of (start_date, end_date, length) for every active run."""
    runs = []
    cur_start = None
    cur_len = 0
    prev = None
    for d in days:
        if d["level"] > 0 or d.get("count", 0) > 0:
            if cur_start is None:
                cur_start = d["date"]
                cur_len = 1
            else:
                cur_len += 1
        else:
            if cur_start is not None:
                runs.append((cur_start, prev, cur_len))
                cur_start = None
                cur_len = 0
        prev = d["date"]
    if cur_start is not None:
        runs.append((cur_start, prev, cur_len))
    return runs


def build():
    d = load()
    days = d["days"]

    runs = daily_streak_runs(days)
    # active day list: only days that have count > 0 (or level > 0)
    active = [d for d in days if d.get("count", 0) > 0 or d["level"] > 0]
    counts = [d.get("count", 0) for d in active]

    if not active:
        raise SystemExit("no active contribution days")

    longest_run = max(runs, key=lambda r: r[2]) if runs else (None, None, 0)
    # current streak = the last run if it includes today or yesterday
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cur_run = runs[-1] if runs else (None, None, 0)
    if cur_run[1] not in (today.isoformat(), yesterday.isoformat()):
        cur_run = (None, None, 0)

    total = d.get("total", 0)
    cur = d.get("current_streak", 0)
    longest = d.get("longest_streak", 0)

    # Chart layout: one bar per active day
    n = len(active)
    max_count = max(counts) or 1
    plot_w = W - PAD_L - PAD_R
    plot_h = H - PAD_T - PAD_B
    bw = max(1.0, min(8.0, plot_w / max(n, 1)))
    inner_w = bw * n
    if inner_w > plot_w:
        bw = plot_w / n
        inner_w = plot_w
    x0 = PAD_L + (plot_w - inner_w) / 2

    static = os.environ.get("STATIC", "0") == "1"

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
               f'viewBox="0 0 {W} {H}" font-family="{FONT}">')

    # Title
    svg.append(f'<text x="{PAD_L}" y="32" font-size="16" font-weight="700" fill="{GLYPH}">'
               f'Day Streak Graph</text>')
    svg.append(f'<text x="{PAD_L}" y="56" font-size="13" fill="{ACCENT}">'
               f'{total} contributions in the last year  ·  current streak {cur} days  ·  '
               f'longest streak {longest} days</text>')

    # Y axis (0, max) labels and gridlines
    y_max = max_count
    y_ticks = 4
    for i in range(y_ticks + 1):
        v = round(y_max * i / y_ticks)
        y = PAD_T + plot_h - (v / y_max) * plot_h
        svg.append(f'<line x1="{PAD_L}" y1="{y:.1f}" x2="{W - PAD_R}" y2="{y:.1f}" '
                   f'stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{PAD_L - 6}" y="{y + 4:.1f}" font-size="9" fill="{LABEL}" '
                   f'text-anchor="end">{v}</text>')

    # X axis baseline
    svg.append(f'<line x1="{PAD_L}" y1="{PAD_T + plot_h:.1f}" '
               f'x2="{W - PAD_R}" y2="{PAD_T + plot_h:.1f}" stroke="{GLYPH}" stroke-width="1"/>')

    # Build set of dates in longest / current streak so we can color them
    longest_dates = set()
    if longest_run[0]:
        s = datetime.date.fromisoformat(longest_run[0])
        for i in range(longest_run[2]):
            longest_dates.add((s + datetime.timedelta(days=i)).isoformat())
    cur_dates = set()
    if cur_run[0]:
        s = datetime.date.fromisoformat(cur_run[0])
        for i in range(cur_run[2]):
            cur_dates.add((s + datetime.timedelta(days=i)).isoformat())

    step = 0.004
    for i, day in enumerate(active):
        c = day.get("count", 0)
        lvl = day.get("level", 0)
        bh = (c / y_max) * plot_h
        x = x0 + i * bw
        y = PAD_T + plot_h - bh
        col = RAMP[min(lvl, 4)]
        if day["date"] in cur_dates:
            col = CUR_HL
        elif day["date"] in longest_dates:
            col = LONG_HL
        rect = (f'<rect x="{x:.2f}" y="{y:.1f}" width="{max(bw - 1.5, 0.6):.2f}" '
                f'height="{bh:.1f}" fill="{col}" rx="1.2"')
        if static:
            rect += '/>'
        else:
            rect += (f'><animate attributeName="opacity" from="0" to="1" '
                     f'begin="{i*step:.3f}s" dur="0.25s" fill="freeze"/></rect>')
        svg.append(rect)

    # Legend
    ly = H - 14
    svg.append(f'<text x="{PAD_L}" y="{ly}" font-size="11" fill="{ACCENT}">'
               f'Each bar = one active day</text>')
    lx = W - PAD_R - 220
    svg.append(f'<rect x="{lx}" y="{ly-10}" width="10" height="10" rx="2" fill="{RAMP[4]}"/>')
    svg.append(f'<text x="{lx+15}" y="{ly}" font-size="11" fill="{ACCENT}">busy</text>')
    svg.append(f'<rect x="{lx+65}" y="{ly-10}" width="10" height="10" rx="2" fill="{LONG_HL}"/>')
    svg.append(f'<text x="{lx+80}" y="{ly}" font-size="11" fill="{ACCENT}">longest streak</text>')
    svg.append(f'<rect x="{lx+185}" y="{ly-10}" width="10" height="10" rx="2" fill="{CUR_HL}"/>')
    svg.append(f'<text x="{lx+200}" y="{ly}" font-size="11" fill="{ACCENT}">current streak</text>')

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    print(f"wrote {OUT}  ({W}x{H}, {n} active days, max={y_max}, "
          f"cur={cur_run[2]}, longest={longest_run[2]})"
          + ("  [STATIC]" if static else "  [animated]"))


if __name__ == "__main__":
    build()