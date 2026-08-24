#!/usr/bin/env python3
"""
Generate a self-contained, self-hosted SVG that shows the REAL photo with a
cinematic animated reveal (works loaded as <img> in a README, because all motion
is SMIL inside the SVG and the photo is embedded as a data URI).

Usage:
    python scripts/make_photo_svg.py                # -> photo-reveal.svg (color)
    MONO=1 python scripts/make_photo_svg.py         # -> photo-reveal.svg (grayscale)
    STATIC=1 python scripts/make_photo_svg.py       # -> final frame (no reveal)

Only the config block below should need editing.
"""
import os
import base64
import io
import numpy as np
from PIL import Image

# ------------------------------------------------------------------ config
PHOTO      = "my-photo.jpg"
OUT        = "photo-reveal.svg"
W          = 370          # rendered width  (matches the portrait cell in the README)
H          = 460          # rendered height (matches the info card H)
MAX_EDGE   = 900          # downscale the embedded photo to keep the SVG small

REVEAL_DIR = "left"       # "left", "right", "down", "up"  -- which edge the wipe starts from
REVEAL_DUR = 2.4          # seconds for the whole reveal
REVEAL_DELAY = 0.2        # seconds before the reveal starts
# ------------------------------------------------------------------ /config


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    img = Image.open(PHOTO).convert("RGB")
    # fit (contain) inside W x H, centered, letterboxed -- the box is portrait
    iw, ih = img.size
    scale = min(W / iw, H / ih)
    nw, nh = max(1, int(round(iw * scale))), max(1, int(round(ih * scale)))
    # keep the embedded copy small but not blurry at the render size
    embed = img.resize((nw, nh), Image.LANCZOS)

    mono = os.environ.get("MONO", "0") == "1"
    if mono:
        g = embed.convert("L")
        embed = Image.merge("RGB", (g, g, g))
        # tint to the same dark-slate GLYPH tone for the monochrome look
        tint = np.asarray(embed, dtype=np.float32)
        tint = tint / 255.0
        # gentle cool slate tint
        tint[..., 0] *= 0.92
        tint[..., 1] *= 0.97
        tint[..., 2] *= 1.06
        embed = Image.fromarray((np.clip(tint, 0, 1) * 255).astype(np.uint8))

    buf = io.BytesIO()
    embed.save(buf, format="PNG")       # PNG keeps it crisp; still small at this size
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    ox = (W - nw) // 2
    oy = (H - nh) // 2
    static = os.environ.get("STATIC", "0") == "1"

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
               f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    svg.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

    # clip path reveal
    if REVEAL_DIR == "left":
        clip = (f'<clipPath id="r"><rect x="0" y="0" width="0" height="{H}">'
                f'<animate attributeName="width" from="0" to="{W}" '
                f'begin="{REVEAL_DELAY}s" dur="{REVEAL_DUR}" fill="freeze"/></rect></clipPath>')
    elif REVEAL_DIR == "right":
        clip = (f'<clipPath id="r"><rect x="{W}" y="0" width="0" height="{H}">'
                f'<animate attributeName="x" from="{W}" to="0" '
                f'begin="{REVEAL_DELAY}s" dur="{REVEAL_DUR}" fill="freeze"/>'
                f'<animate attributeName="width" from="0" to="{W}" '
                f'begin="{REVEAL_DELAY}s" dur="{REVEAL_DUR}" fill="freeze"/></rect></clipPath>')
    elif REVEAL_DIR == "down":
        clip = (f'<clipPath id="r"><rect x="0" y="0" width="{W}" height="0">'
                f'<animate attributeName="height" from="0" to="{H}" '
                f'begin="{REVEAL_DELAY}s" dur="{REVEAL_DUR}" fill="freeze"/></rect></clipPath>')
    else:  # up
        clip = (f'<clipPath id="r"><rect x="0" y="{H}" width="{W}" height="0">'
                f'<animate attributeName="y" from="{H}" to="0" '
                f'begin="{REVEAL_DELAY}s" dur="{REVEAL_DUR}" fill="freeze"/>'
                f'<animate attributeName="height" from="0" to="{H}" '
                f'begin="{REVEAL_DELAY}s" dur="{REVEAL_DUR}" fill="freeze"/></rect></clipPath>')

    if static:
        # static: no clip animation -> full frame
        svg.append(f'<image x="{ox}" y="{oy}" width="{nw}" height="{nh}" '
                   f'preserveAspectRatio="xMidYMid meet" '
                   f'xlink:href="data:image/png;base64,{b64}"/>')
    else:
        svg.append(clip)
        svg.append(f'<g clip-path="url(#r)">'
                   f'<image x="{ox}" y="{oy}" width="{nw}" height="{nh}" '
                   f'preserveAspectRatio="xMidYMid meet" '
                   f'xlink:href="data:image/png;base64,{b64}"/></g>')

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    kind = "MONO" if mono else "color"
    print(f"wrote {OUT}  ({nw}x{nh} embedded, {len(b64)//1024}KB base64, {kind})"
          + ("  [STATIC]" if static else "  [anim]"))


if __name__ == "__main__":
    build()
