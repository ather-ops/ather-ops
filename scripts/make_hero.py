#!/usr/bin/env python3
"""
Generate a code-style HERO SVG with:
  - Terminal window chrome (dots, title bar)
  - Big monospace name with a per-character hue cycle
  - Animated `>` prompt prefix on the tagline
  - Blinking cursor
  - Live status indicators with pulse dots
  - ASCII-tree version/commit stamp

Usage:
    python scripts/make_hero.py
    STATIC=1 python scripts/make_hero.py
"""
import os

# ------------------------------------------------------------------ config
OUT      = "hero.svg"
W        = 880
H        = 360

NAME        = "Ather Assadullah Peer"
TAGLINE_1   = "AI/ML Engineer"
TAGLINE_2   = "RAG · Agentic AI · LLM Apps"

FONT_MONO   = "'JetBrains Mono','Fira Code','SFMono-Regular',Menlo,Consolas,ui-monospace,monospace"

# hero palette: terminal cyan -> amber -> magenta (vivid, not monochrome)
PALETTE = ["#06b6d4", "#0ea5e9", "#7c3aed", "#ec4899", "#f59e0b", "#10b981", "#06b6d4"]
PAL_CYCLE_S = 9

PROMPT_COLOR = "#06b6d4"
CURSOR_COLOR = "#f59e0b"

VERSION_STAMP = "v2.6.0"
COMMIT_STAMP  = "main@latest"
# ------------------------------------------------------------------ /config


def build():
    static = os.environ.get("STATIC", "0") == "1"

    pal_values = ";".join(PALETTE)
    pal_kt = ";".join(f"{i/(len(PALETTE)-1):.3f}" for i in range(len(PALETTE)))

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
               f'font-family="{FONT_MONO}">')

    # ----- terminal chrome background ----------------------------------
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="14" '
               f'fill="#0f172a"/>')
    # subtle gradient overlay
    svg.append('<defs>')
    svg.append('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">')
    if static:
        bg_stops = (
            f'<stop offset="0" stop-color="#0f172a"/>'
            f'<stop offset="1" stop-color="#1e293b"/>'
        )
    else:
        bg_stops = (
            f'<stop offset="0" stop-color="#0f172a">'
            f'<animate attributeName="stop-color" '
            f'values="#0f172a;#1e1b4b;#0f172a" '
            f'keyTimes="0;0.5;1" dur="12s" repeatCount="indefinite"/></stop>'
            f'<stop offset="1" stop-color="#1e293b">'
            f'<animate attributeName="stop-color" '
            f'values="#1e293b;#0c4a6e;#1e293b" '
            f'keyTimes="0;0.5;1" dur="12s" repeatCount="indefinite"/></stop>'
        )
    svg.append(bg_stops)
    svg.append('</linearGradient>')
    svg.append('</defs>')
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="14" '
               f'fill="url(#bg)" opacity="0.6"/>')

    # ----- title bar ---------------------------------------------------
    bar_h = 30
    svg.append(f'<rect x="0" y="0" width="{W}" height="{bar_h}" '
               f'rx="14" fill="#020617"/>')
    # traffic light dots
    for i, col in enumerate(["#ef4444", "#f59e0b", "#10b981"]):
        cx = 18 + i * 18
        svg.append(f'<circle cx="{cx}" cy="{bar_h/2}" r="5" fill="{col}"/>')
    # title
    svg.append(f'<text x="{W/2}" y="{bar_h/2 + 5}" '
               f'font-size="13" fill="#94a3b8" text-anchor="middle">'
               f'ather-ops@github: ~/profile</text>')
    # right-side version stamp
    svg.append(f'<text x="{W - 16}" y="{bar_h/2 + 4}" '
               f'font-size="11" fill="#64748b" text-anchor="end">'
               f'[{VERSION_STAMP} · {COMMIT_STAMP}]</text>')

    # ----- prompt line -------------------------------------------------
    prompt_y = bar_h + 36
    svg.append(f'<text x="20" y="{prompt_y}" font-size="14" '
               f'fill="{PROMPT_COLOR}">~/ather-ops $</text>')
    # blinking cursor next to prompt
    if not static:
        svg.append(f'<rect x="160" y="{prompt_y - 12}" width="9" height="16" '
                   f'fill="{CURSOR_COLOR}">'
                   f'<animate attributeName="opacity" '
                   f'values="0;0;1;1;0;0" keyTimes="0;0.05;0.5;0.9;1;1" '
                   f'dur="1.1s" repeatCount="indefinite"/></rect>')

    # ----- typed command (cat profile.md) -----------------------------
    cmd_y = prompt_y + 22
    svg.append(f'<text x="160" y="{cmd_y}" font-size="13" fill="#e2e8f0" '
               f'opacity="0.7">cat profile.md</text>')

    # ----- big name (each char tinted from palette) -------------------
    name_y = prompt_y + 80
    fs = 48
    char_w = 28  # monospace char width approx
    # center the name
    total_w = len(NAME) * char_w
    nx = (W - total_w) / 2
    for i, ch in enumerate(NAME):
        col = PALETTE[i % len(PALETTE)] if not static else PALETTE[i % len(PALETTE)]
        # each character cycles through the palette
        if not static:
            cycle_per_char = ";".join(PALETTE)
            char_kt = ";".join(f"{j/(len(PALETTE)-1):.3f}" for j in range(len(PALETTE)))
            svg.append(
                f'<text x="{nx + i*char_w:.1f}" y="{name_y}" '
                f'font-size="{fs}" font-weight="800" fill="{col}">'
                f'<animate attributeName="fill" values="{cycle_per_char}" '
                f'keyTimes="{char_kt}" dur="{PAL_CYCLE_S}s" '
                f'begin="-{i*0.15:.2f}s" repeatCount="indefinite"/>'
                f'{ch}</text>'
            )
        else:
            svg.append(
                f'<text x="{nx + i*char_w:.1f}" y="{name_y}" '
                f'font-size="{fs}" font-weight="800" fill="{col}">{ch}</text>'
            )

    # ----- tagline line (with comment-style '#') ---------------------
    tag_y = name_y + 38
    svg.append(f'<text x="{W/2:.1f}" y="{tag_y}" font-size="15" fill="#06b6d4" '
               f'text-anchor="middle"># {TAGLINE_1} · {TAGLINE_2}</text>')

    # ----- status row -------------------------------------------------
    status_y = tag_y + 36
    status = [
        ("STATUS",  "OPEN_TO_WORK", "#10b981"),
        ("ROLE",    "AI/ML_ENGINEER", "#f59e0b"),
        ("STACK",   "PY_RAG_AGENTS", "#7c3aed"),
        ("LOC",     "BANGALORE_IN", "#06b6d4"),
    ]
    # Render each as a self-contained pill so spacing is uniform and
    # nothing overlaps.
    pill_w = 200
    pill_h = 28
    pill_pad = 12
    total_w = len(status) * pill_w + (len(status) - 1) * pill_pad
    sx = (W - total_w) / 2
    for label, val, col in status:
        # pill background
        svg.append(f'<rect x="{sx:.1f}" y="{status_y - 18}" '
                   f'width="{pill_w}" height="{pill_h}" rx="10" '
                   f'fill="#1e293b" stroke="#334155" stroke-width="1"/>')
        # status dot (pulsing)
        if not static:
            svg.append(f'<circle cx="{sx + 16:.1f}" cy="{status_y - 4}" r="4" '
                       f'fill="{col}">'
                       f'<animate attributeName="opacity" '
                       f'values="0.4;1;0.4" keyTimes="0;0.5;1" '
                       f'dur="1.4s" repeatCount="indefinite"/></circle>')
        else:
            svg.append(f'<circle cx="{sx + 16:.1f}" cy="{status_y - 4}" r="4" '
                       f'fill="{col}"/>')
        # label text
        svg.append(f'<text x="{sx + 30:.1f}" y="{status_y - 1}" font-size="11" '
                   f'fill="#94a3b8">{label}</text>')
        # value text
        svg.append(f'<text x="{sx + 86:.1f}" y="{status_y - 1}" font-size="11" '
                   f'fill="{col}" font-weight="700">{val}</text>')
        sx += pill_w + pill_pad

    # ----- bottom info bar -------------------------------------------
    bot_h = 36
    svg.append(f'<rect x="0" y="{H - bot_h}" width="{W}" height="{bot_h}" '
               f'rx="14" fill="#020617"/>')
    svg.append(f'<text x="20" y="{H - 12}" font-size="11" fill="#64748b">'
               f'build: ather-ops/profile · language: python · '
               f'lines_of_code: 9999+</text>')
    # animated progress bar
    if not static:
        svg.append(f'<rect x="{W - 220}" y="{H - 24}" width="200" height="6" '
                   f'rx="3" fill="#1e293b"/>')
        svg.append(f'<rect x="{W - 220}" y="{H - 24}" width="0" height="6" '
                   f'rx="3" fill="#10b981">'
                   f'<animate attributeName="width" from="0" to="200" '
                   f'dur="3s" fill="freeze"/>'
                   f'<animate attributeName="opacity" '
                   f'values="1;1;0.6;1" keyTimes="0;0.5;0.75;1" '
                   f'dur="2s" repeatCount="indefinite"/></rect>')
        svg.append(f'<text x="{W - 12}" y="{H - 12}" font-size="11" '
                   f'fill="#10b981" text-anchor="end">ready</text>')

    # ----- ambient dot grid (very subtle) ----------------------------
    svg.append('</svg>')
    final = "".join(svg)
    with open(OUT, "w") as f:
        f.write(final)
    print(f"wrote {OUT}  ({W}x{H}, " + ("[STATIC]" if static else "[animated]") + ")")


if __name__ == "__main__":
    build()