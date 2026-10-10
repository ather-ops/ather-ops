#!/usr/bin/env python3
"""
Generate a self-contained, self-hosted SVG that shows the REAL color photo with
a cinematic multi-stage animated reveal and a continuous color-cycle effect on
top (works loaded as <img> in a README, because all motion is SMIL inside the
SVG and the photo is embedded as a data URI).

Stages of the reveal:
    0.0s  - 0.6s   blur-in       (image goes from very blurry to sharp)
    0.6s  - 1.6s   saturate-in   (color saturation rises from 0 -> 1.2)
    0.8s  - 3.2s   side-wipe     (clip rect wipes from left to right)
    3.2s+          color-cycle   (a colored gradient overlay cycles through
                                  spectrum colors indefinitely via feColorMatrix
                                  + animate, so the SVG is alive, not static)

Usage:
    python scripts/make_photo_svg.py                # -> photo-reveal.svg
    STATIC=1 python scripts/make_photo_svg.py       # -> final frame, no animation

Only the config block below should need editing.
"""
import os
import base64
import io
import numpy as np
from PIL import Image, ImageFilter

# ------------------------------------------------------------------ config
PHOTO        = "my-photo.jpg"
OUT          = "photo-reveal.svg"
W            = 370           # rendered width  (matches the portrait cell in README)
H            = 460           # rendered height (matches the info card H)
EMBED_EDGE   = 1100          # downscale embedded photo to keep SVG small
JPEG_QUALITY = 86            # JPEG quality for embedded photo

# Multi-stage reveal timings
BLUR_FROM    = 18            # starting Gaussian blur radius (px)
BLUR_TO      = 0             # ending blur radius
BLUR_DUR     = 0.6
SATURATE_FROM = 0.0          # starting color saturation multiplier
SATURATE_TO   = 1.25         # ending saturation (>1 = boosted)
SATURATE_DUR  = 1.0
REVEAL_DELAY  = 0.8          # seconds before the side-wipe starts
REVEAL_DUR    = 2.4          # seconds for the side-wipe

# Continuous color-cycle overlay (after reveal completes)
COLOR_CYCLE_S = 12           # full color cycle period in seconds
SHIMMER_OP    = 0.18         # base opacity of the colored overlay (0..1)
# ------------------------------------------------------------------ /config


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    img = Image.open(PHOTO).convert("RGB")
    iw, ih = img.size
    # downscale to EMBED_EDGE keeping aspect
    scale = EMBED_EDGE / max(iw, ih)
    nw, nh = max(1, int(round(iw * scale))), max(1, int(round(ih * scale)))
    embed = img.resize((nw, nh), Image.LANCZOS)

    # Save the original (sharp, color) and a blurred start-frame as JPEGs
    sharp_buf = io.BytesIO()
    embed.save(sharp_buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    sharp_b64 = base64.b64encode(sharp_buf.getvalue()).decode("ascii")

    blurred = embed.filter(ImageFilter.GaussianBlur(radius=BLUR_FROM))
    blur_buf = io.BytesIO()
    blurred.save(blur_buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    blur_b64 = base64.b64encode(blur_buf.getvalue()).decode("ascii")

    # Center the image inside the canvas
    ox = (W - nw) // 2
    oy = (H - nh) // 2

    static = os.environ.get("STATIC", "0") == "1"

    # Build the animated blur radius (separate <feGaussianBlur> + <animate>)
    # Stage timings (seconds from t=0):
    t_blur_end   = BLUR_DUR
    t_sat_end    = BLUR_DUR + SATURATE_DUR
    t_wipe_start = REVEAL_DELAY
    t_wipe_end   = REVEAL_DELAY + REVEAL_DUR

    # Side-wipe clipPath that goes left -> right
    clip_rect = (
        f'<clipPath id="reveal-clip"><rect x="0" y="0" width="0" height="{H}">'
        f'<animate attributeName="width" from="0" to="{W}" '
        f'begin="{t_wipe_start}s" dur="{REVEAL_DUR}s" fill="freeze"/>'
        f'</rect></clipPath>'
    )

    # Build the feColorMatrix for saturation animation. Identity matrix with
    # saturation parameter:  s = 1 means neutral; we interpolate 0 -> SATURATE_TO.
    def sat_matrix(s):
        r1 = (1 - s) * 0.2126 + s
        r2 = (1 - s) * 0.7152
        r3 = (1 - s) * 0.0722
        g1 = (1 - s) * 0.2126
        g2 = (1 - s) * 0.7152 + s
        g3 = (1 - s) * 0.0722
        b1 = (1 - s) * 0.2126
        b2 = (1 - s) * 0.7152
        b3 = (1 - s) * 0.0722 + s
        return (
            f"{r1:.4f} {r2:.4f} {r3:.4f} 0 0   "
            f"{g1:.4f} {g2:.4f} {g3:.4f} 0 0   "
            f"{b1:.4f} {b2:.4f} {b3:.4f} 0 0   "
            f"0       0       0       1 0"
        )

    # Discretize saturation values across stages
    sat_stages = []
    n_sat = 24
    for i in range(n_sat + 1):
        t = i / n_sat
        v = SATURATE_FROM + (SATURATE_TO - SATURATE_FROM) * t
        sat_stages.append((t * SATURATE_DUR, v))
    sat_keyTimes = ";".join(f"{t:.3f}" for t, _ in sat_stages)
    sat_values   = ";".join(sat_matrix(v) for _, v in sat_stages)

    # Holographic color cycle: a colored gradient + animated hue matrix on top.
    # We define a wide horizontal gradient using animated stop-colors and place
    # it as a multiply overlay so the photo tints through spectrum colors.
    color_stops_values = (
        "#1e3a8a;#6d28d9;#be185d;#dc2626;#ea580c;"
        "#ca8a04;#16a34a;#0d9488;#0891b2;#1e3a8a"
    )
    color_keytimes = "0;0.111;0.222;0.333;0.444;0.556;0.667;0.778;0.889;1"

    # Build SVG
    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
    )

    # White background
    svg.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

    # Subtle gradient backdrop (always animating, even before reveal)
    svg.append(
        '<defs>'
        '<linearGradient id="bg-grad" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#f8fafc">'
        f'<animate attributeName="stop-color" values="{color_stops_values}" '
        f'keyTimes="{color_keytimes}" dur="{COLOR_CYCLE_S}s" '
        f'repeatCount="indefinite"/></stop>'
        '<stop offset="1" stop-color="#e2e8f0">'
        f'<animate attributeName="stop-color" values="#1e3a8a;#6d28d9;#be185d;#dc2626;#ea580c;#ca8a04;#16a34a;#0d9488;#0891b2;#1e3a8a" '
        f'keyTimes="{color_keytimes}" dur="{COLOR_CYCLE_S}s" '
        f'repeatCount="indefinite"/></stop>'
        '</linearGradient>'
        # Saturation filter
        '<filter id="saturate-filter" x="0" y="0" width="100%" height="100%">'
        '<feColorMatrix type="matrix" '
        f'values="{sat_matrix(SATURATE_FROM)}">'
        f'<animate attributeName="values" '
        f'keyTimes="{sat_keyTimes}" values="{sat_values}" '
        f'dur="{SATURATE_DUR}s" begin="0s" fill="freeze"/>'
        '</feColorMatrix>'
        '</filter>'
        # Hue-shift filter for the continuous color cycle on the photo itself
        '<filter id="hue-cycle" x="0" y="0" width="100%" height="100%">'
        '<feColorMatrix type="hueRotate" values="0">'
        f'<animate attributeName="values" '
        f'values="0;30;60;90;120;150;180;210;240;270;300;330;360" '
        f'dur="{COLOR_CYCLE_S}s" repeatCount="indefinite"/>'
        '</feColorMatrix>'
        '</filter>'
        # Blur filter for the start-frame
        '<filter id="blur-filter" x="-10%" y="-10%" width="120%" height="120%">'
        f'<feGaussianBlur stdDeviation="{BLUR_FROM}">'
        f'<animate attributeName="stdDeviation" '
        f'from="{BLUR_FROM}" to="{BLUR_TO}" '
        f'dur="{BLUR_DUR}s" begin="0s" fill="freeze"/>'
        '</feGaussianBlur>'
        '</filter>'
        # Side-wipe clipPath
        f'{clip_rect}'
        # Holographic shimmer gradient (animated colors) for overlay
        '<linearGradient id="shimmer-grad" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#1e3a8a" stop-opacity="0">'
        f'<animate attributeName="stop-color" values="{color_stops_values}" '
        f'keyTimes="{color_keytimes}" dur="{COLOR_CYCLE_S}s" '
        f'repeatCount="indefinite"/></stop>'
        '<stop offset="0.5" stop-color="#6d28d9" stop-opacity="1">'
        f'<animate attributeName="stop-color" values="#6d28d9;#9333ea;#be185d;#dc2626;#ea580c;#ca8a04;#16a34a;#0d9488;#0891b2;#6d28d9" '
        f'keyTimes="{color_keytimes}" dur="{COLOR_CYCLE_S}s" '
        f'repeatCount="indefinite"/></stop>'
        '<stop offset="1" stop-color="#0891b2" stop-opacity="0">'
        f'<animate attributeName="stop-color" values="#0891b2;#1e3a8a;#6d28d9;#be185d;#dc2626;#ea580c;#ca8a04;#16a34a;#0d9488;#0891b2" '
        f'keyTimes="{color_keytimes}" dur="{COLOR_CYCLE_S}s" '
        f'repeatCount="indefinite"/></stop>'
        '</linearGradient>'
        '</defs>'
    )

    # Layer 1: blurred start-frame (visible until BLUR_DUR)
    svg.append(
        f'<image x="{ox}" y="{oy}" width="{nw}" height="{nh}" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'filter="url(#blur-filter)" '
        f'xlink:href="data:image/jpeg;base64,{blur_b64}">'
        f'<animate attributeName="opacity" from="1" to="0" '
        f'begin="{BLUR_DUR}s" dur="0.01s" fill="freeze"/>'
        f'</image>'
    )

    # Layer 2: sharp photo with side-wipe clip + saturation animation +
    # continuous hue-cycle on the photo itself
    if static:
        svg.append(
            f'<image x="{ox}" y="{oy}" width="{nw}" height="{nh}" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'xlink:href="data:image/jpeg;base64,{sharp_b64}"/>'
        )
    else:
        # Two stacked copies of the sharp image: bottom one with saturation
        # filter, top one with hue-cycle filter, clipped by reveal-clip
        svg.append(f'<g clip-path="url(#reveal-clip)">')
        # sharp + saturation ramp (rises from 0 -> boosted)
        svg.append(
            f'<image x="{ox}" y="{oy}" width="{nw}" height="{nh}" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'filter="url(#saturate-filter)" '
            f'xlink:href="data:image/jpeg;base64,{sharp_b64}"/>'
        )
        # subtle hue cycle on top (very low opacity so colors shift, not destroy)
        svg.append(
            f'<image x="{ox}" y="{oy}" width="{nw}" height="{nh}" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'filter="url(#hue-cycle)" '
            f'style="mix-blend-mode: overlay" opacity="0.35" '
            f'xlink:href="data:image/jpeg;base64,{sharp_b64}"/>'
        )
        # Holographic shimmer overlay - animated gradient that pans across
        svg.append(
            f'<rect x="0" y="0" width="{W}" height="{H}" '
            f'fill="url(#shimmer-grad)" opacity="{SHIMMER_OP}" '
            f'style="mix-blend-mode: screen">'
            f'<animate attributeName="x" from="-{W}" to="{W}" '
            f'dur="{COLOR_CYCLE_S}s" repeatCount="indefinite"/>'
            f'</rect>'
        )
        svg.append('</g>')

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    total_kb = (len(sharp_b64) + len(blur_b64)) // 1024
    print(f"wrote {OUT}  ({nw}x{nh} embedded, {total_kb}KB base64, "
          + ("[STATIC]" if static else "[animated]") + ")")


if __name__ == "__main__":
    build()