#!/usr/bin/env python3
"""
Animated section divider — a horizontal gradient line with a traveling pulse
dot. The gradient cycles through the same aurora palette used elsewhere.

Usage:
    python scripts/make_divider.py            # -> divider.svg (animated)
    STATIC=1 python scripts/make_divider.py   # final frame only
"""
import os

# ------------------------------------------------------------------ config
OUT        = "divider.svg"
W          = 880
H          = 28

ACCENT_A   = os.environ.get("ACCENT_A", "#1e3a8a")
ACCENT_M   = os.environ.get("ACCENT_M", "#7c3aed")
ACCENT_B   = os.environ.get("ACCENT_B", "#0891b2")

DOT_COLOR  = "#ffffff"
DOT_GLOW   = "#a78bfa"

DOT_DUR_S  = 5.0
DOT_GLOW_R = 8
DOT_R      = 3
GRADIENT_S = 8
# ------------------------------------------------------------------ /config


def build():
    static = os.environ.get("STATIC", "0") == "1"

    palette = ["#1e3a8a", "#6d28d9", "#be185d", "#0891b2", "#7c3aed"]
    pal_values = ";".join(palette + [palette[0]])
    pal_kt = ";".join(f"{i/(len(palette)):.3f}" for i in range(len(palette)+1))

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">')

    if static or GRADIENT_S == 0:
        grad_stops = (
            f'<stop offset="0" stop-color="{ACCENT_A}"/>'
            f'<stop offset="0.5" stop-color="{ACCENT_M}"/>'
            f'<stop offset="1" stop-color="{ACCENT_B}"/>'
        )
    else:
        grad_stops = (
            f'<stop offset="0" stop-color="{ACCENT_A}">'
            f'<animate attributeName="stop-color" values="{pal_values}" '
            f'keyTimes="{pal_kt}" dur="{GRADIENT_S}s" repeatCount="indefinite"/>'
            f'</stop>'
            f'<stop offset="0.5" stop-color="{ACCENT_M}">'
            f'<animate attributeName="stop-color" values="{pal_values}" '
            f'keyTimes="{pal_kt}" dur="{GRADIENT_S}s" begin="-2s" '
            f'repeatCount="indefinite"/>'
            f'</stop>'
            f'<stop offset="1" stop-color="{ACCENT_B}">'
            f'<animate attributeName="stop-color" values="{pal_values}" '
            f'keyTimes="{pal_kt}" dur="{GRADIENT_S}s" begin="-4s" '
            f'repeatCount="indefinite"/>'
            f'</stop>'
        )
    svg.append(f'<defs>'
               f'<linearGradient id="grad" x1="0" y1="0" x2="1" y2="0">'
               f'{grad_stops}'
               f'</linearGradient>'
               f'</defs>')

    mid_y = H / 2
    svg.append(f'<line x1="0" y1="{mid_y}" x2="{W}" y2="{mid_y}" '
               f'stroke="url(#grad)" stroke-width="1.5" stroke-linecap="round"/>')

    if not static:
        svg.append(f'<circle cx="0" cy="{mid_y}" r="{DOT_GLOW_R}" '
                   f'fill="{DOT_GLOW}" opacity="0.45">'
                   f'<animate attributeName="cx" from="0" to="{W}" '
                   f'dur="{DOT_DUR_S}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" '
                   f'values="0;0.45;0.45;0" keyTimes="0;0.1;0.9;1" '
                   f'dur="{DOT_DUR_S}s" repeatCount="indefinite"/>'
                   f'</circle>')
        svg.append(f'<circle cx="0" cy="{mid_y}" r="{DOT_R}" fill="{DOT_COLOR}">'
                   f'<animate attributeName="cx" from="0" to="{W}" '
                   f'dur="{DOT_DUR_S}s" repeatCount="indefinite"/>'
                   f'</circle>')

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    print(f"wrote {OUT}  ({W}x{H}, " + ("[STATIC]" if static else "[animated]") + ")")


if __name__ == "__main__":
    build()