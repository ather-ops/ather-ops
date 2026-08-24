#!/usr/bin/env python3
"""
Turn the prepped portrait (source-prepped.png) into a clean, MONOCHROME ASCII
portrait that "types" itself in like a terminal.

Usage:
    python scripts/make_ascii_svg.py            # -> avi-ascii.svg (animated)
    STATIC=1 python scripts/make_ascii_svg.py   # -> avi-ascii.svg (final frame)

Strict single-tone: every glyph uses one color (GLYPH); only density/shape draws
the subject. Animation = character-by-character typewriter reveal (per-line clip
that advances one monospace cell at a time) plus a blinking terminal cursor.

Only the config block below should need editing.
"""
import os
import numpy as np
from PIL import Image

# ------------------------------------------------------------------ config
SOURCE   = "source-prepped.png"     # output of prep_photo.py
OUT      = "avi-ascii.svg"

W        = 370    # rendered width of the portrait canvas  (README uses width=370)
H        = 460    # rendered height; keep == info card H so the table matches

COLS     = 120    # ASCII columns of detail (higher = finer/more detail)
CHAR_ASPECT = 0.5 # monospace glyph width:height ratio
TOP      = 0.0    # top padding as a fraction of H

GLYPH    = "#1f2937"  # single monochrome glyph color (dark slate on white)
BG       = "none"     # transparent background -> blank page around subject

GAMMA     = 0.45   # <1 = brighter midtones; lifts the lit face off the dark shirt
CONTRAST  = 1.20   # 1.0 = neutral; higher punches highlights/shadows
WHITE_FLOOR = 0.10 # luminance below this compresses to black (kills background noise)

# typing animation
ROW_DUR    = 0.55   # seconds to type a single line
STAGGER    = 0.045  # seconds between each line's start (creates a cascade)
CURSOR     = True   # blinking terminal cursor that rides the last typed line

RAMP     = "@%#*+=-:. "   # dense -> sparse a single color; density does the shading

# auto-crop / composition
AUTO_CROP  = True
CROP_PAD   = 0.03   # fraction of the subject size to keep around the figure
ALPHA_MIN  = 8      # pixel alpha considered "part of the subject"
FOCUS_TOP  = 0.72   # keep top 72% (full head + shoulders) of the subject's height
FIT_TO_FRAME = True # crop to W/H aspect so the figure fills the whole canvas
# ------------------------------------------------------------------ /config


def autocrop(img):
    """Trim to the subject's alpha bbox, focus on head+shoulders, fit to frame."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    a = np.asarray(img.getchannel("A"), dtype=np.uint8)
    ys, xs = np.where(a > ALPHA_MIN)
    if len(xs) == 0:
        return img
    y0, y1 = ys.min(), ys.max()
    x0, x1 = xs.min(), xs.max()
    pad = int(CROP_PAD * max(y1 - y0, x1 - x0))
    y0 = max(0, y0 - pad); y1 = min(a.shape[0] - 1, y1 + pad)
    x0 = max(0, x0 - pad); x1 = min(a.shape[1] - 1, x1 + pad)
    img = img.crop((x0, y0, x1 + 1, y1 + 1))
    # focus on head + shoulders
    if FOCUS_TOP < 1.0:
        w2, h2 = img.size
        img = img.crop((0, 0, w2, int(h2 * FOCUS_TOP)))
    # crop to the exact W/H aspect so the bust fills the canvas
    if FIT_TO_FRAME:
        img = fit_to_frame(img)
    return img


def fit_to_frame(img):
    """Crop (center on the subject's head) so the image matches the W/H aspect."""
    target = W / H
    iw, ih = img.size
    curr = iw / ih
    if abs(curr - target) < 0.01:
        return img
    a = np.asarray(img.getchannel("A"), dtype=np.float32)
    ys, xs = np.where(a > ALPHA_MIN)
    if len(xs) == 0:
        return img
    if curr > target:
        # image too wide -> crop width, centered on the head
        new_w = int(round(ih * target))
        cx = xs.mean()                      # face is roughly centred
        x0 = int(round(cx - new_w / 2))
        x0 = max(0, min(x0, iw - new_w))
        return img.crop((x0, 0, x0 + new_w, ih))
    else:
        # image too tall -> crop height, biased toward the head (top)
        new_h = int(round(iw / target))
        cy = ys.min() + (ys.max() - ys.min()) * 0.28
        y0 = int(round(cy - new_h / 2))
        y0 = max(0, min(y0, ih - new_h))
        return img.crop((0, y0, iw, y0 + new_h))


def luminance_grid(img, rows, cols):
    """Build (rows, cols) mask (1 = subject) and luminance 0..1 over the W x H box."""
    alpha = np.asarray(img.getchannel("A"), dtype=np.float32) / 255.0
    gray = np.asarray(img.convert("RGB").convert("L"), dtype=np.float32) / 255.0
    iw, ih = img.size
    scale = min(W / iw, H / ih)
    nw, nh = max(1, int(round(iw * scale))), max(1, int(round(ih * scale)))
    a_res = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS), dtype=np.float32) / 255.0
    g_res = np.asarray(Image.fromarray((gray * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS), dtype=np.float32) / 255.0
    canv_a = np.zeros((H, W), dtype=np.float32)
    canv_g = np.zeros((H, W), dtype=np.float32)
    oy, ox = (H - nh) // 2, (W - nw) // 2
    canv_a[oy:oy + nh, ox:ox + nw] = a_res
    canv_g[oy:oy + nh, ox:ox + nw] = g_res
    ys = np.clip((np.arange(rows) + 0.5) * H / rows, 0, H - 1).astype(int)
    xs = np.clip((np.arange(cols) + 0.5) * W / cols, 0, W - 1).astype(int)
    mask = canv_a[np.ix_(ys, xs)]
    lum = canv_g[np.ix_(ys, xs)]
    lum = np.where(mask > 0.5, lum, 0.0)
    return lum, (mask > 0.5)


def process(lum):
    """Map subject luminance 0..1 to glyph indices (dark -> dense ink)."""
    lo, hi = lum.min(), lum.max()
    if hi - lo > 1e-6:
        lum = (lum - lo) / (hi - lo)
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
    rows = max(10, int(round(COLS * CHAR_ASPECT * (H / W))))
    img = Image.open(SOURCE)
    if AUTO_CROP:
        img = autocrop(img)
    lum, mask = luminance_grid(img, rows, COLS)
    idx, _ = process(lum)

    fh = H / rows
    top = TOP * H
    cols_cw = W / COLS            # width of one monospace cell
    font_family = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    lines = []
    for r in range(rows):
        lines.append("".join(RAMP[i] if mask[r][c] else " " for c, i in enumerate(idx[r])))

    static = os.environ.get("STATIC", "0") == "1"

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
               f'viewBox="0 0 {W} {H}" font-family="{font_family}" '
               f'font-size="{fh:.4f}" fill="{GLYPH}">')
    svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

    # ---- per-line, per-character typewriter clip reveal -------------------
    defs = []
    # discrete values reveal one monospace cell at a time
    vals = ";".join(f"{i*cols_cw:.2f}" for i in range(COLS + 1))
    for r in range(rows):
        if static:
            open_rect = f'<clipPath id="c{r}"><rect x="0" y="{top + r*fh:.3f}" width="{W}" height="{fh:.3f}"/>'
            defs.append(open_rect + "</clipPath>")
        else:
            defs.append(
                f'<clipPath id="c{r}"><rect x="0" y="{top + r*fh:.3f}" width="0" height="{fh:.3f}">'
                f'<animate attributeName="width" calcMode="discrete" '
                f'values="{vals}" begin="{r*STAGGER:.3f}s" dur="{ROW_DUR}" '
                f'fill="freeze"/></rect></clipPath>'
            )
    svg.append("<defs>" + "".join(defs) + "</defs>")

    # clean up: the static variant keeps a plain rect width=W; animated adds animate
    for r in range(rows):
        y = top + (r + 0.82) * fh
        svg.append(f'<text x="0" y="{y:.3f}" textLength="{float(W):.3f}" '
                   f'lengthAdjust="spacingAndGlyphs" clip-path="url(#c{r})">'
                   f'{esc(lines[r])}</text>')

    # ---- blinking terminal cursor at the end of the last typed line ------
    if CURSOR and not static:
        end_row = rows - 1
        svg.append(
            f'<rect x="0" y="{top + end_row*fh:.3f}" width="0" height="{fh:.3f}" '
            f'fill="{GLYPH}">'
            f'<animate attributeName="width" values="0;0;4;4;0;0" '
            f'keyTimes="0;0.06;0.5;0.9;0.95;1" dur="1s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;1;0;0" '
            f'keyTimes="0;0.06;0.5;0.9;0.95;1" dur="1s" repeatCount="indefinite"/>'
            f'</rect>'
        )

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    print(f"wrote {OUT}  ({rows} rows x {COLS} cols, {rows*COLS} glyphs, "
          f"cell={cols_cw:.2f}px)" + ("  [STATIC]" if static else "  [animated]"))


if __name__ == "__main__":
    build()
