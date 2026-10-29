#!/usr/bin/env python3
"""
Render data/contributions.json as a DAY STREAK bar chart (one bar per day
with contributions). Highlights the longest streak and the current streak.

Next-level additions:
    - staggered bar reveal with a grow-up animation
    - travelling gradient sheen across the bar field
    - pulsing glow on the current-streak and longest-streak bars
    - hover highlight on every bar
    - an animated "today" marker at the right edge
    - a soft halo behind the headline stats
    - a scanline sweeping the plot

Usage:
    python scripts/make_streak_graph.py          # -> streak-graph.svg (animated)
    STATIC=1 python scripts/make_streak_graph.py # final frame, no reveal anim

PORTABILITY RULES (keep them):
    1. Animated elements carry their FINAL visible state in the base
       attributes; never base opacity="0" or static renderers show a blank
       chart.
    2. No mix-blend-mode.
    3. Text content goes INSIDE <text>, before any <animate>.
    4. Avoid gradient stop-opacity="0" on large fills.
"""
import os
import json
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
TITLE   = "#1e293b"
ACCENT  = "#475569"
LABEL   = "#94a3b8"
CUR_HL  = "#2563eb"     # current-streak bar color
LONG_HL = "#7c3aed"     # longest-streak bar color

# indigo -> violet ramp (level 0..4 -> fill color)
RAMP    = ["#eef2ff", "#c7d2fe", "#818cf8", "#6366f1", "#4338ca"]

# next-level timings
REVEAL_STEP = 0.0035   # seconds between each bar's reveal
SHEEN_PERIOD = 10.0    # travelling sheen sweep period
PULSE_PERIOD = 3.0     # glow pulse on highlighted bars
SCAN_PERIOD = 8.0      # scanline sweep period
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
    active = [x for x in days if x.get("count", 0) > 0 or x["level"] > 0]
    counts = [x.get("count", 0) for x in active]

    if not active:
        raise SystemExit("no active contribution days")

    longest_run = max(runs, key=lambda r: r[2]) if runs else (None, None, 0)
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cur_run = runs[-1] if runs else (None, None, 0)
    if cur_run[1] not in (today.isoformat(), yesterday.isoformat()):
        cur_run = (None, None, 0)

    total = d.get("total", 0)
    cur = d.get("current_streak", 0)
    longest = d.get("longest_streak", 0)

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

    # ---- defs -------------------------------------------------------------
    svg.append(
        '<defs>'
        '<linearGradient id="sheen-grad" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="#ffffff" stop-opacity="0.75"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
        '</linearGradient>'
        '<linearGradient id="scan-grad" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="#e0e7ff" stop-opacity="0.6"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
        '</linearGradient>'
        '<radialGradient id="stat-halo" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#c7d2fe"/>'
        '<stop offset="0.55" stop-color="#eef2ff"/>'
        '<stop offset="1" stop-color="#ffffff"/>'
        '</radialGradient>'
        '</defs>'
    )

    # ---- header ------------------------------------------------------------
    svg.append(
        f'<ellipse cx="{PAD_L+80}" cy="26" rx="150" ry="28" '
        f'fill="url(#stat-halo)" opacity="0.5">'
        f'<animate attributeName="opacity" values="0.5;0.2;0.5" '
        f'dur="{PULSE_PERIOD+1}s" repeatCount="indefinite"/>'
        f'</ellipse>'
    )
    svg.append(
        f'<text x="{PAD_L}" y="32" font-size="16" font-weight="700" fill="{TITLE}">'
        f'Day Streak Graph'
        f'<animate attributeName="opacity" values="1;0.62;1" '
        f'dur="{PULSE_PERIOD+1}s" repeatCount="indefinite"/>'
        f'</text>'
    )
    svg.append(
        f'<text x="{PAD_L}" y="56" font-size="13" fill="{ACCENT}">'
        f'{total} contributions in the last year  ·  current streak {cur} days  ·  '
        f'longest streak {longest} days'
        f'</text>'
    )

    # ---- axes --------------------------------------------------------------
    y_max = max_count
    y_ticks = 4
    for i in range(y_ticks + 1):
        v = round(y_max * i / y_ticks)
        y = PAD_T + plot_h - (v / y_max) * plot_h
        svg.append(f'<line x1="{PAD_L}" y1="{y:.1f}" x2="{W - PAD_R}" y2="{y:.1f}" '
                   f'stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{PAD_L - 6}" y="{y + 4:.1f}" font-size="9" fill="{LABEL}" '
                   f'text-anchor="end">{v}</text>')

    svg.append(f'<line x1="{PAD_L}" y1="{PAD_T + plot_h:.1f}" '
               f'x2="{W - PAD_R}" y2="{PAD_T + plot_h:.1f}" stroke="{TITLE}" stroke-width="1"/>')

    # ---- streak date sets ---------------------------------------------------
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

    # ---- bars ---------------------------------------------------------------
    step = REVEAL_STEP
    bar_w = max(bw - 1.5, 0.6)
    for i, day in enumerate(active):
        c = day.get("count", 0)
        lvl = day.get("level", 0)
        bh = (c / y_max) * plot_h
        x = x0 + i * bw
        y = PAD_T + plot_h - bh
        col = RAMP[min(lvl, 4)]
        is_cur = day["date"] in cur_dates
        is_long = day["date"] in longest_dates
        if is_cur:
            col = CUR_HL
        elif is_long:
            col = LONG_HL

        # hover highlight behind the bar
        svg.append(
            f'<rect x="{x-1:.2f}" y="{PAD_T}" width="{bar_w+2:.2f}" '
            f'height="{plot_h:.1f}" fill="{ACCENT}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="0.12" dur="0.15s" '
            f'begin="mouseover" fill="freeze"/>'
            f'<animate attributeName="opacity" from="0.12" to="0" dur="0.3s" '
            f'begin="mouseout" fill="freeze"/>'
            f'</rect>'
        )

        if static:
            svg.append(f'<rect x="{x:.2f}" y="{y:.1f}" width="{bar_w:.2f}" '
                       f'height="{bh:.1f}" fill="{col}" rx="1.2"/>')
            continue

        # bar: grows up from the baseline, then breathes
        anim = (
            f'<animate attributeName="y" from="{PAD_T + plot_h:.1f}" to="{y:.1f}" '
            f'dur="0.45s" begin="{i*step:.3f}s" fill="freeze"/>'
            f'<animate attributeName="height" from="0" to="{bh:.1f}" '
            f'dur="0.45s" begin="{i*step:.3f}s" fill="freeze"/>'
        )
        if is_cur or is_long:
            hl = CUR_HL if is_cur else LONG_HL
            # glow behind the highlighted bar
            svg.append(
                f'<rect x="{x-1.2:.2f}" y="{y-1.2:.1f}" '
                f'width="{bar_w+2.4:.2f}" height="{bh+2.4:.1f}" '
                f'fill="{hl}" opacity="0.22" rx="2.4">'
                f'<animate attributeName="opacity" values="0.18;0.42;0.18" '
                f'dur="{PULSE_PERIOD}s" begin="{i*step:.3f}s" repeatCount="indefinite"/>'
                f'</rect>'
            )
            anim += (
                f'<animate attributeName="opacity" values="1;0.72;1" '
                f'dur="{PULSE_PERIOD}s" begin="{i*step:.3f}s" repeatCount="indefinite"/>'
            )
        else:
            anim += (
                f'<animate attributeName="opacity" values="1;0.82;1" '
                f'dur="5.5s" begin="{i*step:.3f}s" repeatCount="indefinite"/>'
            )
        svg.append(f'<rect x="{x:.2f}" y="{y:.1f}" width="{bar_w:.2f}" '
                   f'height="{bh:.1f}" fill="{col}" rx="1.2">{anim}</rect>')

    # ---- travelling sheen across the bar field ------------------------------
    sheen_w = 220
    svg.append(
        f'<rect x="{-sheen_w}" y="{PAD_T}" width="{sheen_w}" height="{plot_h:.1f}" '
        f'fill="url(#sheen-grad)" opacity="0.35" pointer-events="none">'
        f'<animate attributeName="x" from="{-sheen_w}" to="{W}" '
        f'dur="{SHEEN_PERIOD}s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    # ---- vertical scanline --------------------------------------------------
    scan_h = 120
    svg.append(
        f'<rect x="{PAD_L}" y="{-scan_h}" width="{plot_w:.1f}" height="{scan_h}" '
        f'fill="url(#scan-grad)" opacity="0.35" pointer-events="none">'
        f'<animate attributeName="y" from="{-scan_h}" to="{PAD_T+plot_h:.1f}" '
        f'dur="{SCAN_PERIOD}s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    # ---- "latest activity" marker at the right edge -------------------------
    last_x = x0 + (n - 1) * bw
    svg.append(
        f'<line x1="{last_x + bar_w/2:.2f}" y1="{PAD_T - 8}" '
        f'x2="{last_x + bar_w/2:.2f}" y2="{PAD_T + plot_h:.1f}" '
        f'stroke="{TITLE}" stroke-width="1" stroke-dasharray="2 3" opacity="0.4">'
        f'<animate attributeName="opacity" values="0.2;0.55;0.2" '
        f'dur="{PULSE_PERIOD}s" repeatCount="indefinite"/>'
        f'</line>'
    )

    # ---- legend -------------------------------------------------------------
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
