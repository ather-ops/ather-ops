#!/usr/bin/env python3
"""
Generate a single animated tech pill SVG. Each tech gets a unique color and
its own hue cycle.

Usage:
    python scripts/make_tech_pill.py python.svg "Python" "#1e3a8a"
    STATIC=1 python scripts/make_tech_pill.py ...
"""
import os
import sys

OUT      = sys.argv[1] if len(sys.argv) > 1 else "pill.svg"
LABEL    = sys.argv[2] if len(sys.argv) > 2 else "Tech"
COLOR    = sys.argv[3] if len(sys.argv) > 3 else "#1f2937"

W, H     = 130, 30
FONT_FAM = "'Segoe UI', 'Inter', system-ui, -apple-system, sans-serif"
FONT_W   = 600
FONT_SZ  = 12
DOT_R    = 2.5
DOT_DUR  = 1.4

SIBLING_PALETTES = {
    "#1e3a8a": ["#1e3a8a", "#3730a3", "#1e40af"],
    "#3730a3": ["#3730a3", "#1e3a8a", "#6d28d9"],
    "#7c3aed": ["#7c3aed", "#6d28d9", "#9333ea"],
    "#0891b2": ["#0891b2", "#0e7490", "#1e3a8a"],
    "#be185d": ["#be185d", "#9a3412", "#7c3aed"],
    "#9a3412": ["#9a3412", "#b45309", "#be185d"],
    "#b45309": ["#b45309", "#9a3412", "#d97706"],
    "#15803d": ["#15803d", "#14532d", "#166534"],
    "#334155": ["#334155", "#475569", "#1e293b"],
    "#0e7490": ["#0e7490", "#0891b2", "#1e3a8a"],
    "#d97706": ["#d97706", "#b45309", "#ea580c"],
    "#1e40af": ["#1e40af", "#1e3a8a", "#3730a3"],
}


def build():
    static = os.environ.get("STATIC", "0") == "1"
    palette = SIBLING_PALETTES.get(COLOR, [COLOR, COLOR, COLOR])
    pal_values = ";".join(palette + [palette[0]])
    pal_kt = ";".join(f"{i/len(palette):.3f}" for i in range(len(palette)+1))

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">')

    if static:
        stops = f'<stop offset="0" stop-color="{palette[0]}"/>' \
                f'<stop offset="1" stop-color="{palette[-1]}"/>'
    else:
        stops = (
            f'<stop offset="0" stop-color="{palette[0]}">'
            f'<animate attributeName="stop-color" values="{pal_values}" '
            f'keyTimes="{pal_kt}" dur="6s" repeatCount="indefinite"/></stop>'
            f'<stop offset="1" stop-color="{palette[-1]}">'
            f'<animate attributeName="stop-color" values="{pal_values}" '
            f'keyTimes="{pal_kt}" dur="6s" begin="-3s" repeatCount="indefinite"/></stop>'
        )

    svg.append(f'<defs>'
               f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="0">'
               f'{stops}'
               f'</linearGradient>'
               f'</defs>')

    svg.append(f'<rect x="0.75" y="0.75" width="{W-1.5}" height="{H-1.5}" '
               f'rx="6" fill="url(#g)"/>')

    svg.append(f'<text x="{W//2}" y="{H//2 + FONT_SZ//3}" '
               f'font-family="{FONT_FAM}" font-weight="{FONT_W}" '
               f'font-size="{FONT_SZ}" fill="#ffffff" text-anchor="middle">'
               f'{LABEL}</text>')

    if not static:
        svg.append(f'<circle cx="{W-10}" cy="{H//2}" r="{DOT_R}" fill="#ffffff">'
                   f'<animate attributeName="opacity" '
                   f'values="0.4;1;0.4" keyTimes="0;0.5;1" '
                   f'dur="{DOT_DUR}s" repeatCount="indefinite"/>'
                   f'</circle>')

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    print(f"wrote {OUT}  ({LABEL!r})")


if __name__ == "__main__":
    build()