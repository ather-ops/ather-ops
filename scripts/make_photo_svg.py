#!/usr/bin/env python3
"""
Generate a self-contained, self-hosted SVG that shows the REAL color photo
with a cinematic multi-stage animated reveal and a set of continuous
"living" effects layered on top.

Stages of the reveal:
    0.0s  - 0.7s   blur-in       (image goes from very blurry to sharp)
    0.3s  - 1.4s   saturate-in   (color saturation rises from 0 -> boosted)
    0.7s  - 1.6s   iris-open     (radial clip expands from the face)
    0.9s  - 3.1s   side-wipe     (rect clip wipes left -> right)
    3.1s+          living layer:
                      - rotating light sweep across the photo
                      - drifting monochrome sheen
                      - breathing vignette
                      - film-grain flicker
                      - animated monochrome border + corner brackets

Usage:
    python scripts/make_photo_svg.py                # -> photo-reveal.svg
    STATIC=1 python scripts/make_photo_svg.py       # -> final frame, no animation

PORTABILITY RULES (keep them):
    1. Animated elements carry their FINAL visible state in the base
       attributes. Never base opacity="0", or static renderers show a
       blank frame.
    2. No mix-blend-mode (static renderers paint it as an opaque block).
    3. Text content goes INSIDE <text>, before any <animate>.
    4. Avoid gradient stop-opacity="0" on large fills; static renderers
       can treat it as opaque. Use the shape's own opacity instead.

Only the config block below should need editing.
"""
import os
import base64
import io
import sys
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svg_fx import esc, soft_band_grad, soft_oval_grad  # noqa: E402

# ------------------------------------------------------------------ config
PHOTO        = "my-photo.jpg"
OUT          = "photo-reveal.svg"
W            = 370           # rendered width  (matches the portrait cell in README)
H            = 460           # rendered height (matches the info card H)
EMBED_EDGE   = 1200          # downscale embedded photo to keep SVG small
JPEG_QUALITY = 92            # JPEG quality for embedded photo

# Multi-stage reveal timings
BLUR_FROM     = 20           # starting Gaussian blur radius (px)
BLUR_TO       = 0            # ending blur radius
BLUR_DUR      = 0.7
SATURATE_FROM = 0.0          # starting color saturation multiplier
SATURATE_TO   = 1.25         # ending saturation (>1 = boosted)
SATURATE_DUR  = 1.1
IRIS_DELAY    = 0.7          # radial iris-open start
IRIS_DUR      = 0.9
REVEAL_DELAY  = 0.9          # seconds before the side-wipe starts
REVEAL_DUR    = 2.2          # seconds for the side-wipe

# Continuous "living" effects
SWEEP_PERIOD  = 8.0          # rotating light sweep period
SHEEN_PERIOD  = 11.0         # drifting sheen period
GRAIN_PERIOD  = 0.28         # film-grain flicker step
VIGNETTE_PERIOD = 6.0        # breathing vignette period
BORDER_PERIOD = 5.0          # border dash travel period
GLOW_PERIOD   = 4.5          # portrait glow pulse period
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

    t_blur_end   = BLUR_DUR
    t_iris_start = IRIS_DELAY
    t_iris_end   = IRIS_DELAY + IRIS_DUR
    t_wipe_start = REVEAL_DELAY
    t_wipe_end   = REVEAL_DELAY + REVEAL_DUR

    # ---- clip paths -----------------------------------------------------
    # The photo is revealed by ONE wipe clip. An earlier version nested an
    # iris clip inside the wipe clip, which made the visible region the
    # INTERSECTION of the two - so the photo appeared only as fragments.
    # The iris is now drawn as a glowing ring overlay instead.
    clip_rect = (
        f'<clipPath id="reveal-clip"><rect x="0" y="0" width="{W}" height="{H}">'
        f'<animate attributeName="width" from="0" to="{W}" '
        f'begin="{t_wipe_start}s" dur="{REVEAL_DUR}s" fill="freeze"/>'
        f'</rect></clipPath>'
    )
    # soft glowing ring that expands outwards as the reveal starts
    iris_r = int(H * 0.30)
    clip_iris = (
        f'<clipPath id="iris-clip">'
        f'<circle cx="{W//2}" cy="{int(H*0.42)}" r="{iris_r}">'
        f'<animate attributeName="r" from="0" to="{int(H*0.75)}" '
        f'begin="{t_iris_start}s" dur="{IRIS_DUR}s" fill="freeze"/>'
        f'</circle></clipPath>'
    )

    # ---- saturation filter ---------------------------------------------
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

    sat_stages = []
    n_sat = 24
    for i in range(n_sat + 1):
        t = i / n_sat
        v = SATURATE_FROM + (SATURATE_TO - SATURATE_FROM) * t
        # keyTimes MUST be normalised to 0..1 - the animation duration
        # already controls the real time. Multiplying by SATURATE_DUR here
        # produced keyTimes up to 1.1, which the browser rejects, leaving
        # the filter frozen at saturation 0 (a greyscale photo).
        sat_stages.append((t, v))
    sat_keyTimes = ";".join(f"{t:.3f}" for t, _ in sat_stages)
    sat_values = ";".join(sat_matrix(v) for _, v in sat_stages)

    # ---- build SVG ------------------------------------------------------
    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
    )

    svg.append(
        '<defs>'
        # saturation ramp
        '<filter id="saturate-filter" x="0" y="0" width="100%" height="100%">'
        '<feColorMatrix type="matrix" '
        f'values="{sat_matrix(SATURATE_FROM)}">'
        f'<animate attributeName="values" '
        f'keyTimes="{sat_keyTimes}" values="{sat_values}" '
        f'dur="{SATURATE_DUR}s" begin="0.3s" fill="freeze"/>'
        '</feColorMatrix></filter>'
        # blur filter for the start-frame
        '<filter id="blur-filter" x="-10%" y="-10%" width="120%" height="120%">'
        f'<feGaussianBlur stdDeviation="{BLUR_FROM}">'
        f'<animate attributeName="stdDeviation" from="{BLUR_FROM}" '
        f'to="{BLUR_TO}" dur="{BLUR_DUR}s" begin="0s" fill="freeze"/>'
        '</feGaussianBlur></filter>'
        # light sweep gradient (opaque stops only -> safe for static render)
        + soft_band_grad("sweep-grad", "#ffffff", 0.50, "x")
        # vignette gradient
        + soft_oval_grad("vignette-grad", "#0f172a", 0.26)
        + soft_oval_grad("backdrop-wash", "#f1f5f9", 0.75)
        # frame gradient
        + '<linearGradient id="frame-grad" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#0f172a"/>'
        '<stop offset="0.5" stop-color="#64748b"/>'
        '<stop offset="1" stop-color="#0f172a"/>'
        f'<animate attributeName="x1" values="0;1;0" dur="{BORDER_PERIOD}s" repeatCount="indefinite"/>'
        f'<animate attributeName="y1" values="0;1;0" dur="{BORDER_PERIOD}s" repeatCount="indefinite"/>'
        f'<animate attributeName="x2" values="1;0;1" dur="{BORDER_PERIOD}s" repeatCount="indefinite"/>'
        f'<animate attributeName="y2" values="1;0;1" dur="{BORDER_PERIOD}s" repeatCount="indefinite"/>'
        '</linearGradient>'
        f'{clip_rect}'
        f'{clip_iris}'
        '</defs>'
    )

    # white backdrop
    svg.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

    # A soft neutral wash behind the photo so that, during the iris reveal,
    # the area outside the iris reads as a soft studio backdrop rather than
    # a flat white block.
    svg.append(
        f'<ellipse cx="{W//2}" cy="{int(H*0.42)}" rx="{int(W*0.62)}" '
        f'ry="{int(H*0.52)}" fill="url(#backdrop-wash)" opacity="1">'
        f'<animate attributeName="opacity" values="1;0.75;1" '
        f'dur="{VIGNETTE_PERIOD}s" repeatCount="indefinite"/>'
        f'</ellipse>'
    )

    # ---- Layer 1: blurred start-frame (fades out as the sharp one lands) --
    # The blurred frame is the "pre-reveal" placeholder. It must stay
    # visible until the wipe has finished, otherwise the empty backdrop
    # shows through the wiped area. It cross-fades out across the wipe.
    svg.append(
        f'<image x="{ox}" y="{oy}" width="{nw}" height="{nh}" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'filter="url(#blur-filter)" opacity="1" '
        f'xlink:href="data:image/jpeg;base64,{blur_b64}">'
        f'<animate attributeName="opacity" values="1;1;0" '
        f'keyTimes="0;0.88;1" dur="{REVEAL_DUR + 0.35:.2f}s" '
        f'begin="{t_wipe_start - 0.6:.2f}s" fill="freeze"/>'
        f'</image>'
    )

    if static:
        # static: just the sharp photo
        svg.append(
            f'<image x="{ox}" y="{oy}" width="{nw}" height="{nh}" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'xlink:href="data:image/jpeg;base64,{sharp_b64}"/>'
        )
    else:
        # ---- Layer 2: the sharp photo, revealed by the wipe --------------
        # The photo is drawn ONCE, clipped by the wipe only. (Drawing it
        # twice - once saturated, once plain - is what made the reveal show
        # a grey, desaturated copy outside the iris.)
        svg.append('<g clip-path="url(#reveal-clip)">')
        svg.append(
            f'<image x="{ox}" y="{oy}" width="{nw}" height="{nh}" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'filter="url(#saturate-filter)" '
            f'xlink:href="data:image/jpeg;base64,{sharp_b64}"/>'
        )

        # expanding glow ring, clipped to the revealed area so it never
        # floats over the untouched part of the canvas
        svg.append(
            f'<g clip-path="url(#iris-clip)" opacity="0.55">'
            f'<circle cx="{W//2}" cy="{int(H*0.42)}" r="{iris_r}" '
            f'fill="none" stroke="#ffffff" stroke-width="10">'
            f'<animate attributeName="r" from="0" to="{int(H*0.75)}" '
            f'begin="{t_iris_start}s" dur="{IRIS_DUR}s" fill="freeze"/>'
            f'<animate attributeName="stroke-width" values="14;2;14" '
            f'dur="{IRIS_DUR}s" begin="{t_iris_start}s" fill="freeze"/>'
            f'</circle></g>'
        )
        svg.append('</g>')

        # ---- Layer 3: soft light sweep, sitting ABOVE the photo ----------
        # (it used to live inside the reveal clip, so it painted over the
        #  grey backdrop and left a hard diagonal seam across the frame)
        sweep_w = 230
        svg.append(
            f'<g opacity="0.30">'
            f'<rect x="{-sweep_w}" y="-120" width="{sweep_w}" height="{H+240}" '
            f'fill="url(#sweep-grad)" transform="rotate(16 {W/2} {H/2})">'
            f'<animate attributeName="x" from="{-sweep_w}" to="{W+sweep_w}" '
            f'dur="{SWEEP_PERIOD}s" repeatCount="indefinite"/>'
            f'</rect></g>'
        )

    # ---- vignette (breathing) -------------------------------------------
    svg.append(
        f'<rect x="0" y="0" width="{W}" height="{H}" '
        f'fill="url(#vignette-grad)" opacity="0.45" pointer-events="none">'
        f'<animate attributeName="opacity" values="0.38;0.55;0.38" '
        f'dur="{VIGNETTE_PERIOD}s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    # ---- film grain: a tiled noise layer that flickers ------------------
    rng = np.random.default_rng(7)
    noise = rng.integers(0, 255, size=(96, 96, 3), dtype=np.uint8)
    noise_img = Image.fromarray(noise, "RGB").resize((W, H), Image.NEAREST)
    nbuf = io.BytesIO()
    noise_img.save(nbuf, format="JPEG", quality=30)
    noise_b64 = base64.b64encode(nbuf.getvalue()).decode("ascii")
    svg.append(
        f'<image x="0" y="0" width="{W}" height="{H}" '
        f'preserveAspectRatio="none" opacity="0.07" pointer-events="none" '
        f'xlink:href="data:image/jpeg;base64,{noise_b64}">'
        f'<animate attributeName="opacity" values="0.05;0.10;0.04;0.09;0.05" '
        f'dur="{GRAIN_PERIOD*5:.2f}s" repeatCount="indefinite"/>'
        f'</image>'
    )

    # ---- animated frame + corner brackets --------------------------------
    svg.append(
        f'<rect x="3" y="3" width="{W-6}" height="{H-6}" rx="12" ry="12" '
        f'fill="none" stroke="url(#frame-grad)" stroke-width="2" '
        f'opacity="0.7" stroke-dasharray="30 18">'
        f'<animate attributeName="stroke-dashoffset" from="48" to="0" '
        f'dur="{BORDER_PERIOD}s" repeatCount="indefinite"/>'
        f'</rect>'
    )
    svg.append(
        f'<rect x="3" y="3" width="{W-6}" height="{H-6}" rx="12" ry="12" '
        f'fill="none" stroke="#0f172a" stroke-width="1" opacity="0.2">'
        f'<animate attributeName="opacity" values="0.12;0.3;0.12" '
        f'dur="{GLOW_PERIOD}s" repeatCount="indefinite"/>'
        f'</rect>'
    )
    # corner brackets
    for cx, cy, dx, dy in ((3, 3, 1, 1), (W-3, 3, -1, 1),
                           (3, H-3, 1, -1), (W-3, H-3, -1, -1)):
        svg.append(
            f'<path d="M {cx} {cy + dy*26} L {cx} {cy} L {cx + dx*26} {cy}" '
            f'fill="none" stroke="#0f172a" stroke-width="2.6" '
            f'stroke-linecap="round" opacity="0.75">'
            f'<animate attributeName="opacity" values="0.75;0.3;0.75" '
            f'dur="{GLOW_PERIOD}s" begin="0.5s" repeatCount="indefinite"/>'
            f'</path>'
        )

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    total_kb = (len(sharp_b64) + len(blur_b64) + len(noise_b64)) // 1024
    print(f"wrote {OUT}  ({nw}x{nh} embedded, {total_kb}KB base64, "
          + ("[STATIC]" if static else "[animated]") + ")")


if __name__ == "__main__":
    build()
