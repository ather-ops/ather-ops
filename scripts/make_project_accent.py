#!/usr/bin/env python3
"""
Generate a per-project animated accent: a colored gradient bar that cycles
through the project's signature palette. Used to give each Featured Project a
visual identity without using emojis.

Usage:
    python scripts/make_project_accent.py xpect-ai.svg "Xpect AI" xpect-ai
"""
import os
import sys

OUT      = sys.argv[1] if len(sys.argv) > 1 else "accent.svg"
LABEL    = sys.argv[2] if len(sys.argv) > 2 else "Project"
SLUG     = sys.argv[3] if len(sys.argv) > 3 else "accent1"

W        = 800
H        = 6

PALETTE_MAP = {
    "xpect-ai":      ["#1e3a8a", "#7c3aed", "#0891b2"],
    "amazn-ai":      ["#7c3aed", "#be185d", "#1e40af"],
    "pulsemesh":     ["#0f766e", "#0891b2", "#1e3a8a"],
    "atlas-agent":   ["#be185d", "#7c3aed", "#1e40af"],
    "hospital-sql":  ["#0891b2", "#0e7490", "#1e3a8a"],
    "cafe-sales":    ["#b45309", "#d97706", "#9a3412"],
    "ml-from-scratch":["#14532d", "#15803d", "#84cc16"],
    "accent1":       ["#1e3a8a", "#7c3aed", "#0891b2"],
    "accent2":       ["#7c3aed", "#be185d", "#1e40af"],
    "accent3":       ["#0f766e", "#0891b2", "#1e3a8a"],
}


def build():
    static = os.environ.get("STATIC", "0") == "1"
    palette = PALETTE_MAP.get(SLUG, PALETTE_MAP["accent1"])

    pal_values = ";".join(palette + [palette[0]])
    pal_kt = ";".join(f"{i/len(palette):.3f}" for i in range(len(palette)+1))

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">')

    if static:
        stops = f'<stop offset="0" stop-color="{palette[0]}"/>' \
                f'<stop offset="0.5" stop-color="{palette[len(palette)//2]}"/>' \
                f'<stop offset="1" stop-color="{palette[-1]}"/>'
    else:
        stops = (
            f'<stop offset="0" stop-color="{palette[0]}">'
            f'<animate attributeName="stop-color" values="{pal_values}" '
            f'keyTimes="{pal_kt}" dur="10s" repeatCount="indefinite"/></stop>'
            f'<stop offset="0.5" stop-color="{palette[len(palette)//2]}">'
            f'<animate attributeName="stop-color" values="{pal_values}" '
            f'keyTimes="{pal_kt}" dur="10s" begin="-3s" repeatCount="indefinite"/></stop>'
            f'<stop offset="1" stop-color="{palette[-1]}">'
            f'<animate attributeName="stop-color" values="{pal_values}" '
            f'keyTimes="{pal_kt}" dur="10s" begin="-6s" repeatCount="indefinite"/></stop>'
        )

    svg.append(f'<defs>'
               f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="0">'
               f'{stops}</linearGradient>'
               f'</defs>')

    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" '
               f'fill="url(#g)" rx="{H//2}"/>')

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    print(f"wrote {OUT}  ({LABEL!r})")


if __name__ == "__main__":
    build()