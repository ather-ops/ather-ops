#!/usr/bin/env python3
"""
Generate an SVG section title with an animated gradient text fill. The text
color cycles through a per-section palette so each section feels distinct
while still being part of one cohesive look.

Usage:
    python scripts/make_section_title.py "About Me"      about-me.svg
    STATIC=1 python scripts/make_section_title.py "..."   out.svg
"""
import os
import sys

OUT      = sys.argv[2] if len(sys.argv) > 2 else "title.svg"
TEXT     = sys.argv[1] if len(sys.argv) > 1 else "Section"

W        = 540
H        = 64
FONT_FAM = "'Segoe UI', 'Inter', system-ui, -apple-system, sans-serif"
FONT_W   = 700
FONT_SZ  = 36

DEFAULT_PALETTE = ["#1e3a8a", "#6d28d9", "#be185d", "#0891b2", "#7c3aed"]
PALETTE_CYCLE_S = 10

SECTION_PALETTES = {
    "about-me":      ["#0f766e", "#0891b2", "#1e3a8a", "#0f766e"],
    "education":     ["#b45309", "#d97706", "#f59e0b", "#b45309"],
    "what-i-build":  ["#1e3a8a", "#3730a3", "#6d28d9", "#1e3a8a"],
    "featured":      ["#1e40af", "#7c3aed", "#be185d", "#1e40af"],
    "tech-stack":    ["#0f172a", "#1f2937", "#475569", "#0f172a"],
    "key-achv":      ["#9a3412", "#b45309", "#be185d", "#9a3412"],
    "contribution":  ["#1e3a8a", "#6d28d9", "#be185d", "#1e3a8a"],
    "edu":           ["#b45309", "#d97706", "#f59e0b", "#b45309"],
    "build":         ["#1e3a8a", "#3730a3", "#6d28d9", "#1e3a8a"],
    "tech":          ["#0f172a", "#1f2937", "#475569", "#0f172a"],
    "key":           ["#9a3412", "#b45309", "#be185d", "#9a3412"],
}


def slug_from_text(t):
    return t.lower().replace(" ", "-")


def build():
    static = os.environ.get("STATIC", "0") == "1"
    slug = slug_from_text(OUT.replace(".svg", ""))
    palette = SECTION_PALETTES.get(slug, DEFAULT_PALETTE)
    pal_values = ";".join(palette + [palette[0]])
    pal_kt = ";".join(f"{i/len(palette):.3f}" for i in range(len(palette)+1))

    pad_x = 24
    est_w = pad_x * 2 + int(len(TEXT) * FONT_SZ * 0.55)
    canvas_w = max(W, est_w)

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'width="{canvas_w}" height="{H}" viewBox="0 0 {canvas_w} {H}">')

    if static or PALETTE_CYCLE_S == 0:
        grad_stops = (
            f'<stop offset="0" stop-color="{palette[0]}"/>'
            f'<stop offset="0.5" stop-color="{palette[len(palette)//2]}"/>'
            f'<stop offset="1" stop-color="{palette[-1]}"/>'
        )
    else:
        grad_stops = (
            f'<stop offset="0" stop-color="{palette[0]}">'
            f'<animate attributeName="stop-color" values="{pal_values}" '
            f'keyTimes="{pal_kt}" dur="{PALETTE_CYCLE_S}s" repeatCount="indefinite"/>'
            f'</stop>'
            f'<stop offset="0.5" stop-color="{palette[len(palette)//2]}">'
            f'<animate attributeName="stop-color" values="{pal_values}" '
            f'keyTimes="{pal_kt}" dur="{PALETTE_CYCLE_S}s" begin="-3s" '
            f'repeatCount="indefinite"/>'
            f'</stop>'
            f'<stop offset="1" stop-color="{palette[-1]}">'
            f'<animate attributeName="stop-color" values="{pal_values}" '
            f'keyTimes="{pal_kt}" dur="{PALETTE_CYCLE_S}s" begin="-6s" '
            f'repeatCount="indefinite"/>'
            f'</stop>'
        )
    svg.append(f'<defs>'
               f'<linearGradient id="grad" x1="0" y1="0" x2="1" y2="0">'
               f'{grad_stops}'
               f'</linearGradient>'
               f'</defs>')

    svg.append(f'<text x="{pad_x}" y="{H//2 + FONT_SZ//3}" '
               f'font-family="{FONT_FAM}" font-weight="{FONT_W}" '
               f'font-size="{FONT_SZ}" fill="url(#grad)">{TEXT}</text>')

    if not static:
        svg.append(f'<circle cx="{canvas_w - 16}" cy="{H//2}" r="4" '
                   f'fill="{palette[0]}">'
                   f'<animate attributeName="fill" values="{pal_values}" '
                   f'keyTimes="{pal_kt}" dur="{PALETTE_CYCLE_S}s" '
                   f'repeatCount="indefinite"/>'
                   f'<animate attributeName="r" values="3;5;3" '
                   f'dur="2s" repeatCount="indefinite"/>'
                   f'</circle>')

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    print(f"wrote {OUT}  ({TEXT!r}, palette={slug})")


if __name__ == "__main__":
    build()