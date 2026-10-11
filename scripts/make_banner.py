#!/usr/bin/env python3
"""
Generate a wide banner SVG that spans the top of the README. The banner is a
dotted/ascii-line treatment of the photo subject against a dark backdrop,
inspired by the reference profile style.

It consists of:
  - Three frames: left (subject on the left), center (small terminal window),
    right (subject on the right). The center window shows a code snippet.
  - Dotted/pointillist rendering of the source photo so it matches the
    reference's "dotted art" hero style.
  - Subtle radial vignette and a gradient line at the bottom that animates.

Usage:
    python scripts/make_banner.py            # animated
    STATIC=1 python scripts/make_banner.py   # final frame
"""
import os
import base64
import io
import numpy as np
from PIL import Image, ImageFilter

# ------------------------------------------------------------------ config
PHOTO    = "my-photo.jpg"
OUT      = "banner.svg"
W        = 880            # total banner width
H        = 220            # banner height (compact so it sits above the photo)
PHOTO_W  = 220            # subject frame width
PHOTO_H  = 200            # subject frame height

DOT_PALETTE = [
    "#1e293b",  # primary mode (light slate for low-mid)
    "#475569",  # mid slate
    "#94a3b8",  # upper mid
    "#e2e8f0",  # highlights
    "#ffffff",  # peaks
]

# Center window text
WINDOW_TITLE = "ather-ops@github: ~/profile"
WINDOW_LINES = [
    "$ whoami",
    "Ather Assadullah Peer",
    "$ cat ./.focus",
    "AI/ML · RAG · Agentic AI",
    "$ ./connect.sh --open-to-work",
    "[+] ready. shipping.",
]
# ------------------------------------------------------------------ /config


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ascii_dot_image(img, target_w, target_h, dot_step=4):
    """Convert the photo into a pointillist / dotted line drawing.

    Returns a list of (cx, cy, r, color_idx) ready to render as circles."""
    iw, ih = img.size
    g = img.convert("L")
    a = img.convert("RGBA").split()[-1]

    # fit inside target box
    scale = min(target_w / iw, target_h / ih)
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    g = g.resize((nw, nh), Image.LANCZOS)
    a = a.resize((nw, nh), Image.LANCZOS)
    g_arr = np.asarray(g, dtype=np.float32)
    a_arr = np.asarray(a, dtype=np.float32) / 255.0

    ox = (target_w - nw) // 2
    oy = (target_h - nh) // 2

    out = []
    # Resample: render a small dot at every dot_step pixels. Dot size scales
    # inversely with luminance so bright areas get small dense dots, dark
    # areas get large sparse dots -> produces a "dotted art" look.
    for y in range(0, nh, dot_step):
        for x in range(0, nw, dot_step):
            if x >= nw or y >= nh:
                continue
            lum = g_arr[y, x] / 255.0
            mask = a_arr[y, x]
            if mask < 0.25:
                continue
            # invert: darker (lum low) -> bigger dot
            inv = 1.0 - lum
            inv = pow(inv, 0.8)
            r = max(0.6, inv * (dot_step * 0.55))
            ci = min(len(DOT_PALETTE) - 1, int(lum * (len(DOT_PALETTE) - 0.5)))
            cx = ox + x
            cy = oy + y
            out.append((cx, cy, r, ci))
    return out


def build():
    static = os.environ.get("STATIC", "0") == "1"
    img = Image.open(PHOTO).convert("RGB")

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
               f'font-family="JetBrains Mono, ui-monospace, monospace">')

    # Dark backdrop with subtle radial gradient
    svg.append('<defs>')
    if static:
        bg = (
            '<radialGradient id="bg" cx="50%" cy="40%" r="80%">'
            '<stop offset="0" stop-color="#0f172a"/>'
            '<stop offset="1" stop-color="#020617"/>'
            '</radialGradient>'
        )
    else:
        bg = (
            '<radialGradient id="bg" cx="50%" cy="40%" r="80%">'
            '<stop offset="0" stop-color="#1e293b">'
            '<animate attributeName="stop-color" '
            'values="#1e293b;#1e1b4b;#1e293b" '
            'keyTimes="0;0.5;1" dur="14s" repeatCount="indefinite"/></stop>'
            '<stop offset="1" stop-color="#020617">'
            '<animate attributeName="stop-color" '
            'values="#020617;#0c0a4a;#020617" '
            'keyTimes="0;0.5;1" dur="14s" repeatCount="indefinite"/></stop>'
            '</radialGradient>'
        )
    svg.append(bg)
    svg.append('</defs>')
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bg)"/>')

    # ----- left subject frame ---------------------------------------
    left_x = 30
    dots = ascii_dot_image(img, PHOTO_W, PHOTO_H, dot_step=4)
    # push dots into a centered subject frame on the left
    frame_x = left_x
    frame_y = (H - PHOTO_H) // 2
    svg.append(f'<g transform="translate({frame_x}, {frame_y})">')
    for cx, cy, r, ci in dots:
        col = DOT_PALETTE[ci]
        if not static:
            svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="{col}" '
                       f'opacity="0.6">'
                       f'<animate attributeName="opacity" from="0" to="0.95" '
                       f'begin="{(cx+cy)*0.001:.2f}s" dur="0.6s" '
                       f'fill="freeze"/></circle>')
        else:
            svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="{col}" '
                       f'opacity="0.95"/>')
    svg.append('</g>')

    # ----- right subject frame (mirror) ----------------------------
    right_x = W - PHOTO_W - 30
    svg.append(f'<g transform="translate({right_x}, {frame_y}) scale(-1, 1) translate({-PHOTO_W}, 0)">')
    for cx, cy, r, ci in dots:
        col = DOT_PALETTE[ci]
        if not static:
            svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="{col}" '
                       f'opacity="0.6">'
                       f'<animate attributeName="opacity" from="0" to="0.95" '
                       f'begin="{(cx+cy)*0.001 + 0.4:.2f}s" dur="0.6s" '
                       f'fill="freeze"/></circle>')
        else:
            svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="{col}" '
                       f'opacity="0.95"/>')
    svg.append('</g>')

    # ----- center terminal window ----------------------------------
    win_w = 360
    win_h = PHOTO_H - 20
    win_x = (W - win_w) // 2
    win_y = (H - win_h) // 2

    # outer card
    svg.append(f'<rect x="{win_x}" y="{win_y}" width="{win_w}" height="{win_h}" '
               f'rx="10" fill="#0b1220" stroke="#1e293b" stroke-width="1"/>')

    # title bar
    bar_h = 24
    svg.append(f'<rect x="{win_x}" y="{win_y}" width="{win_w}" height="{bar_h}" '
               f'rx="10" fill="#020617"/>')
    # traffic-light dots
    for i, col in enumerate(["#ef4444", "#f59e0b", "#10b981"]):
        svg.append(f'<circle cx="{win_x + 14 + i*14}" cy="{win_y + bar_h/2}" '
                   f'r="4" fill="{col}"/>')
    # title
    svg.append(f'<text x="{win_x + win_w/2}" y="{win_y + bar_h/2 + 4}" '
               f'font-size="11" fill="#94a3b8" text-anchor="middle">'
               f'{WINDOW_TITLE}</text>')

    # body lines
    by0 = win_y + bar_h + 22
    fs = 12
    line_h = 18
    for i, line in enumerate(WINDOW_LINES):
        # colorize prompts vs output
        if line.startswith("$"):
            svg.append(f'<text x="{win_x + 14}" y="{by0 + i*line_h}" '
                       f'font-size="{fs}" fill="#10b981">{esc(line)}</text>')
        elif line.startswith("[+]"):
            svg.append(f'<text x="{win_x + 14}" y="{by0 + i*line_h}" '
                       f'font-size="{fs}" fill="#06b6d4">{esc(line)}</text>')
        else:
            svg.append(f'<text x="{win_x + 14}" y="{by0 + i*line_h}" '
                       f'font-size="{fs}" fill="#cbd5e1">{esc(line)}</text>')

    # blinking cursor at the end
    if not static:
        last_y = by0 + (len(WINDOW_LINES)-1) * line_h
        svg.append(f'<rect x="{win_x + 14}" y="{last_y - 10}" width="8" height="14" '
                   f'fill="#f59e0b">'
                   f'<animate attributeName="opacity" '
                   f'values="0;0;1;1;0;0" keyTimes="0;0.05;0.5;0.9;1;1" '
                   f'dur="1.1s" repeatCount="indefinite"/></rect>')

    # ----- animated bottom gradient line ----------------------------
    if not static:
        palette = ["#06b6d4", "#7c3aed", "#ec4899", "#f59e0b", "#10b981", "#06b6d4"]
        pal_v = ";".join(palette)
        pal_kt = ";".join(f"{i/(len(palette)-1):.3f}" for i in range(len(palette)))
        svg.append(f'<line x1="0" y1="{H-2}" x2="{W}" y2="{H-2}" '
                   f'stroke="#06b6d4" stroke-width="2" stroke-linecap="round">'
                   f'<animate attributeName="stroke" '
                   f'values="{pal_v}" keyTimes="{pal_kt}" '
                   f'dur="12s" repeatCount="indefinite"/></line>')

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    n_dots = len(dots) * 2
    print(f"wrote {OUT}  ({W}x{H}, {n_dots} dots, "
          + ("[STATIC]" if static else "[animated]") + ")")


if __name__ == "__main__":
    build()