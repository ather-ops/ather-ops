#!/usr/bin/env python3
"""
Turn the prepped portrait (source-prepped.png) into a clean, MONOCHROME ASCII
SVG that "types" itself in like a terminal.

Usage:
    python scripts/make_ascii_svg.py            # -> avi-ascii.svg (animated)
    STATIC=1 python scripts/make_ascii_svg.py   # -> avi-ascii.svg (final frame)

The SVG starts blank at t=0 and each line is typed out left-to-right, line by
line, using a per-row clip mask (SMIL, which GitHub runs inside an <img>).

Only the config block below should need editing.
"""
import os
import sys
import math
import numpy as np
from PIL import Image

# ------------------------------------------------------------------ config
SOURCE   = "source-prepped.png"     # output of prep_photo.py
OUT      = "avi-ascii.svg"

W        = 370    # rendered width of the portrait canvas  (README uses width=370)
H        = 460    # rendered height; keep == info card H so the table matches

COLS     = 104    # ASCII columns of detail (higher = more detail)
CHAR_ASPECT = 0.5 # monospace glyph width:height ratio
TOP      = 0.02   # top padding as a fraction of H
BOTTOM   = 0.04   # bottom padding as a fraction of H

GLYPH    = "#1f2937"  # single monochrome glyph color (dark slate so it reads on white)
BG       = "none"     # transparent background -> blank page around subject

GAMMA     = 0.45   # <1 = brighter midtones; lifts the lit face off the dark shirt
CONTRAST  = 1.20   # 1.0 = neutral; higher punches highlights/shadows
WHITE_FLOOR = 0.10 # luminance below this compresses to black (kills background noise)

# animation
ROW_DUR  = 1.6    # seconds to fully type a single line
STAGGER  = 0.014  # seconds between lines (per-row begin delay)
CURSOR   = True   # blinking block cursor at the end of the last typed line

RAMP     = "@%#*+=-:. "   # dense -> sparse; a single color, density does the shading

# auto-crop: trim transparent margins so the figure fills the canvas
AUTO_CROP  = True
CROP_PAD   = 0.03   # fraction of the subject size to keep around the figure
ALPHA_MIN  = 8      # pixel alpha considered "part of the subject"
# Focus crop: keep the head + upper torso (a readable bust) instead of the whole
# body. 1.0 = full subject, <1 = keep that fraction of the subject from the top.
FOCUS_TOP  = 0.72   # keep top 72% (full head + shoulders) of the subject's height
# Leave the crop as the auto alpha-bbox found it; the subject is already centred.
CENTER_FACE = False
# ------------------------------------------------------------------ /config


def autocrop(img):
    """Crop to the subject's alpha bounding box, then trim to the head+shoulders."""
    if img.mode != "RGBA":
        return img
    a = np.asarray(img.getchannel("A"), dtype=np.uint8)
    ys, xs = np.where(a > ALPHA_MIN)
    if len(xs) == 0:
        return img
    y0, y1 = ys.min(), ys.max()
    x0, x1 = xs.min(), xs.max()
    h = y1 - y0
    w = x1 - x0
    pad = int(CROP_PAD * max(h, w))
    y0 = max(0, y0 - pad); y1 = min(a.shape[0] - 1, y1 + pad)
    x0 = max(0, x0 - pad); x1 = min(a.shape[1] - 1, x1 + pad)
    img = img.crop((x0, y0, x1 + 1, y1 + 1))
    # focus crop on the upper portion (head + shoulders)
    if FOCUS_TOP < 1.0:
        w2, h2 = img.size
        img = img.crop((0, 0, w2, int(h2 * FOCUS_TOP)))
    # re-center horizontally on the face (luminance-weighted center of head)
    if CENTER_FACE and img.size[0] > 0:
        w2, h2 = img.size
        alpha = np.asarray(img.getchannel("A"), dtype=np.float32)
        head = alpha[:h2, :]
        ys, xs = np.where(head > ALPHA_MIN)
        if len(xs):
            com_x = xs.mean()
            # shift the window so the face center lands at image center
            shift = int(round((w2 / 2) - com_x))
            shift = int(np.clip(shift, -int(w2 * 0.35), int(w2 * 0.35)))
            new_x0 = shift
            if new_x0 > 0:
                img = img.crop((new_x0, 0, w2, h2))
            elif shift < 0:
                # pad left so we don't lose the subject
                from PIL import Image as _I
                padded = _I.new("RGBA", (w2, h2), (0, 0, 0, 0))
                padded.paste(img, (-shift, 0))
                img = padded
    return img


def luminance_grid(img, rows, cols):
    """
    Build a (rows, cols) grid of the subject ALPHA MASK (1 = subject, 0 = space)
    and the subject LUMINANCE 0..1 over the W x H box (contain-fit, centered).
    Background cells are luminance 0 so they render blank (space).
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = np.asarray(img.getchannel("A"), dtype=np.float32) / 255.0
    gray = np.asarray(img.convert("RGB").convert("L"), dtype=np.float32) / 255.0
    iw, ih = img.size
    # contain-fit inside the W x H box, preserving aspect ratio
    scale = min(W / iw, H / ih)
    nw, nh = max(1, int(round(iw * scale))), max(1, int(round(ih * scale)))
    # resize alpha and gray together (same fit), then paste centered on a blank canvas
    a_res = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS), dtype=np.float32) / 255.0
    g_res = np.asarray(Image.fromarray((gray * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS), dtype=np.float32) / 255.0

    canv_a = np.zeros((H, W), dtype=np.float32)
    canv_g = np.zeros((H, W), dtype=np.float32)
    oy, ox = (H - nh) // 2, (W - nw) // 2
    canv_a[oy:oy + nh, ox:ox + nw] = a_res
    canv_g[oy:oy + nh, ox:ox + nw] = g_res

    # downsample canvas to rows x cols grid
    ys = np.clip((np.arange(rows) + 0.5) * H / rows, 0, H - 1).astype(int)
    xs = np.clip((np.arange(cols) + 0.5) * W / cols, 0, W - 1).astype(int)
    mask = canv_a[np.ix_(ys, xs)]
    lum = canv_g[np.ix_(ys, xs)]
    # Only keep the subject's luminance; everything outside the mask is blank (0).
    lum = np.where(mask > 0.5, lum, 0.0)
    return lum, (mask > 0.5)


def process(lum):
    """
    Map subject luminance 0..1 to glyph indices into RAMP (dark -> dense ink).
    Cells already flagged as background (lum==0) are set to index = len(RAMP)-1
    so they render as a clean space.
    """
    lo, hi = lum.min(), lum.max()
    if hi - lo > 1e-6:
        lum = (lum - lo) / (hi - lo)
    # keep default = a space glyph for empty/background cells
    space_idx = len(RAMP) - 1
    blank = lum <= 0.0
    lum = np.clip((lum - WHITE_FLOOR) / (1.0 - WHITE_FLOOR), 0, 1)
    lum = np.power(lum, GAMMA)
    lum = (lum - 0.5) * CONTRAST + 0.5
    lum = np.clip(lum, 0, 1)
    idx = (lum * (len(RAMP) - 1) + 0.5).astype(int)
    idx = np.clip(idx, 0, len(RAMP) - 1)
    idx[blank] = space_idx
    return idx, lum


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    rows = int(round(COLS * CHAR_ASPECT * (H / W)))
    rows = max(10, rows)
    img = Image.open(SOURCE)
    if AUTO_CROP:
        img = autocrop(img)
    lum, mask = luminance_grid(img, rows, COLS)
    idx, _ = process(lum)

    fh = H / rows                      # glyph height (font-size)
    top = TOP * H
    text_length = W                    # force every line to exactly fill width
    font_family = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    lines = []
    for r in range(rows):
        line = "".join(RAMP[i] if mask[r][c] else " " for c, i in enumerate(idx[r]))
        lines.append(line)

    # static? then just emit full text, no animation
    static = os.environ.get("STATIC", "0") == "1"

    # build SVG
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
               f'viewBox="0 0 {W} {H}" font-family="{font_family}" '
               f'font-size="{fh:.4f}" fill="{GLYPH}">')
    # background rect (transparent)
    svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

    defs = []
    for r in range(rows):
        defs.append(
            f'<clipPath id="c{r}"><rect x="0" y="{top + r*fh:.3f}" '
            f'width="{text_length}" height="{fh:.3f}" '
            + (f'><animate attributeName="width" from="0" to="{text_length}" '
               f'begin="{r*STAGGER:.3f}s" dur="{ROW_DUR}" fill="freeze"/>'
               if not static else (">")) +
            f'</rect></clipPath>'
        )
    svg.append("<defs>" + "".join(defs) + "</defs>")

    for r in range(rows):
        y = top + (r + 0.82) * fh
        svg.append(f'<text x="0" y="{y:.3f}" textLength="{float(text_length):.3f}" '
                   f'lengthAdjust="spacingAndGlyphs" clip-path="url(#c{r})">'
                   f'{esc(lines[r])}</text>')

    if CURSOR and not static:
        # blinking block cursor at end of last line
        svg.append(
            f'<rect x="0" y="{top + (rows-1)*fh:.3f}" width="0" height="{fh:.3f}" '
            f'fill="{GLYPH}" opacity="0.8">'
            f'<animate attributeName="width" values="0;0;{fh*0.5:.3f};{fh*0.5:.3f};0;0" '
            f'keyTimes="0;0.05;0.5;0.9;0.95;1" dur="1s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;1;0;0" '
            f'keyTimes="0;0.05;0.5;0.9;0.95;1" dur="1s" repeatCount="indefinite"/>'
            f'<animate attributeName="x" from="0" to="0" dur="1s" repeatCount="indefinite"/>'
            f'</rect>'
        )

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    print(f"wrote {OUT}  ({rows} rows x {COLS} cols, {rows*COLS} glyphs)"
          + ("  [STATIC]" if static else "  [animated]"))


if __name__ == "__main__":
    build()
