#!/usr/bin/env python3
"""
Render source-prepped.png as a photo-realistic, MONOCHROME ASCII portrait that
"types itself in" on load. Designed to look as much like the reference photo
as possible while keeping a clean single-tone aesthetic.

Improvements over the basic version:
  - Denser glyph resolution (more cols / rows).
  - Uses both luminance AND alpha of the source for an accurate subject mask.
  - Luminance curve is biased so the lit face stays bright while the dark
    shirt/hair read as solid ink (no black blocks that swallow the face).
  - Smooth sub-cell averaging -> no jaggy square patches.
  - Block + ascii hybrid ramp (10 levels) for fine tonal gradation.

Usage:
    python scripts/make_ascii_svg.py            # -> avi-ascii.svg (animated)
    STATIC=1 python scripts/make_ascii_svg.py   # -> avi-ascii.svg (final frame)

Only the config block below should need editing.
"""
import os
import numpy as np
from PIL import Image, ImageFilter

# ------------------------------------------------------------------ config
SOURCE       = "source-prepped.png"   # output of prep_photo.py
OUT          = "avi-ascii.svg"

W            = 370                    # rendered width  (matches photo cell)
H            = 460                    # rendered height (matches photo cell)

COLS         = 130                    # ASCII columns (very high -> fine detail)
CHAR_ASPECT  = 0.50                   # monospace glyph width:height ratio
TOP_PAD_FRAC = 0.0

GLYPH        = "#1f2937"              # single monochrome glyph color (dark slate)
BG           = "none"                 # transparent

# Animated color cycling for the "live, not static" feel. Glyphs pulse through
# this palette while the typewriter reveal runs. Set ANIMATE_COLOR=0 to use a
# single static GLYPH color instead.
ANIMATE_COLOR  = True
COLOR_PALETTE  = [
    "#1f2937",   # slate   - base
    "#1e3a8a",   # indigo
    "#3730a3",   # deeper indigo
    "#6d28d9",   # violet
    "#9333ea",   # purple
    "#be185d",   # rose    - hot peak
    "#1e40af",   # back through blue
    "#0891b2",   # cyan
    "#0f766e",   # teal
    "#0f172a",   # deep slate (rest)
]
COLOR_CYCLE_S  = 14        # full cycle period in seconds (slow, hypnotic)
COLOR_STAGGER  = 0.06      # seconds of per-row delay so color moves like a wave
ROW_BASE_FILL  = "#1f2937" # shadow rows always sit at this base slate

# luminance / contrast curve
GAMMA           = 0.85                 # <1 brightens shadows
CONTRAST        = 1.30                 # >1 punches highlights/shadows
WHITE_FLOOR     = 0.04                 # below this compresses to dark ink (kills background)
INVERT          = False                # darker pixels -> denser glyphs (photo-realistic)

# Shadow / lit threshold + glyph-band mapping.
# The photo is mostly dark (shirt + hair); only the lit face is bright. We map:
#   subject pixels BELOW SHADOW_THRESH -> densest glyph (solid ink)
#   subject pixels ABOVE SHADOW_THRESH -> ramp[MID_GLYPH_IDX .. n-1] (face detail)
SHADOW_THRESH   = 0.30                 # luminance threshold (0..1) for "is lit?"
SHADOW_GLYPH_IDX = 0                   # densest glyph used for dark shirt / hair
MID_GLYPH_IDX   = 3                    # first glyph used for lit pixels (face highlights)

# auto-crop / composition
AUTO_CROP       = True
CROP_PAD        = 0.04                 # padding fraction of figure size
ALPHA_MIN       = 24                   # pixel alpha considered "part of the subject"
FOCUS_TOP       = 0.66                 # crop top fraction (head + shoulders)
FIT_TO_FRAME    = True                 # crop to W/H aspect so bust fills canvas
EYE_BIAS_Y      = 0.34                 # vertical eye position inside the bust (0..1)

# typing animation
ROW_DUR         = 0.32                 # seconds to "type" a single line
STAGGER         = 0.022                # seconds between each line's start
CURSOR          = True                 # blinking terminal cursor
CURSOR_BLINK    = "1s"

# glyph ramp (dense -> sparse; density = ink).
# Mixed block + ascii gives smooth tonal gradation at 10 levels.
RAMP = "█▓▒░#@%&*+=·. "
# ------------------------------------------------------------------ /config


def autocrop(img):
    """Trim to subject bbox, focus on head+shoulders, fit to frame.

    Centers on the LIT-FACE bbox (bright pixels), not the whole subject bbox,
    so the face sits in the middle of the canvas instead of being biased to
    whichever side has more dark pixels.
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    a = np.asarray(img.getchannel("A"), dtype=np.uint8)
    l = np.asarray(img.convert("L"))
    mask = (a > ALPHA_MIN) & (l > 110)   # lit subject pixels = face
    ys, xs = np.where(mask)
    if len(xs) < 50:
        # fallback to all subject pixels
        ys, xs = np.where(a > ALPHA_MIN)
    if len(xs) == 0:
        return img
    face_cx = float(xs.mean())
    face_cy = float(ys.mean())

    # Full subject bbox for trim boundaries
    ys2, xs2 = np.where(a > ALPHA_MIN)
    y0, y1 = ys2.min(), ys2.max()
    x0, x1 = xs2.min(), xs2.max()
    pad = int(CROP_PAD * max(y1 - y0, x1 - x0))
    y0 = max(0, y0 - pad); y1 = min(a.shape[0] - 1, y1 + pad)
    x0 = max(0, x0 - pad); x1 = min(a.shape[1] - 1, x1 + pad)
    img = img.crop((x0, y0, x1 + 1, y1 + 1))

    # focus on head + shoulders (crop top fraction)
    if FOCUS_TOP < 1.0:
        w2, h2 = img.size
        img = img.crop((0, 0, w2, int(h2 * FOCUS_TOP)))

    # crop to W/H aspect, but center on the FACE not the whole subject
    if FIT_TO_FRAME:
        img = fit_to_frame_on_face(img, face_cx - x0, face_cy - y0)
    return img


def fit_to_frame_on_face(img, face_cx_orig, face_cy_orig):
    """Crop to W/H aspect, centering on the lit face inside the cropped image."""
    target = W / H
    iw, ih = img.size
    curr = iw / ih
    if abs(curr - target) < 0.01:
        return img
    a = np.asarray(img.getchannel("A"), dtype=np.float32)
    l = np.asarray(img.convert("L"))
    # Re-find lit face bbox within the cropped image
    mask = (a > ALPHA_MIN * 2) & (l > 110)
    ys, xs = np.where(mask)
    if len(xs) > 50:
        face_cx = float(xs.mean())
        face_cy = float(ys.min() + (ys.max() - ys.min()) * EYE_BIAS_Y)
    else:
        face_cx = face_cx_orig
        face_cy = face_cy_orig

    if curr > target:
        new_w = int(round(ih * target))
        x0 = int(round(face_cx - new_w / 2))
        x0 = max(0, min(x0, iw - new_w))
        return img.crop((x0, 0, x0 + new_w, ih))
    else:
        new_h = int(round(iw / target))
        y0 = int(round(face_cy - new_h / 2))
        y0 = max(0, min(y0, ih - new_h))
        return img.crop((0, y0, iw, y0 + new_h))


def sample_field(img, rows, cols):
    """Build (rows, cols) luminance & subject mask from the prepped image."""
    # Anti-aliased downsample for smooth glyph values
    alpha = np.asarray(img.getchannel("A"), dtype=np.float32) / 255.0
    rgb = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    iw, ih = img.size

    # Step 1: resize the image to roughly cells*1.5 with LANCZOS to capture
    # sub-pixel detail so the glyph ramps get smooth tonal input.
    super_w = max(cols * 3, 64)
    scale = super_w / iw
    super_h = max(1, int(round(ih * scale)))
    img2 = img.resize((super_w, super_h), Image.LANCZOS)
    a2 = np.asarray(img2.getchannel("A"), dtype=np.float32) / 255.0
    rgb2 = np.asarray(img2.convert("RGB"), dtype=np.float32) / 255.0
    l2 = 0.2126 * rgb2[..., 0] + 0.7152 * rgb2[..., 1] + 0.0722 * rgb2[..., 2]
    # Slight blur to soften sub-pixel noise before averaging
    img2_blur = img2.filter(ImageFilter.GaussianBlur(radius=0.6))
    l3 = np.asarray(img2_blur.convert("L"), dtype=np.float32) / 255.0
    a3 = np.asarray(img2_blur.getchannel("A"), dtype=np.float32) / 255.0

    # Step 2: stretch to canvas W x H, centered
    scale_w = min(W / super_w, H / super_h)
    cw = max(1, int(round(super_w * scale_w)))
    ch = max(1, int(round(super_h * scale_w)))
    canv_l = np.zeros((H, W), dtype=np.float32)
    canv_a = np.zeros((H, W), dtype=np.float32)
    oy, ox = (H - ch) // 2, (W - cw) // 2
    img3_l = Image.fromarray((l3 * 255).astype(np.uint8)).resize((cw, ch), Image.LANCZOS)
    img3_a = Image.fromarray((a3 * 255).astype(np.uint8)).resize((cw, ch), Image.LANCZOS)
    canv_l[oy:oy + ch, ox:ox + cw] = np.asarray(img3_l, dtype=np.float32) / 255.0
    canv_a[oy:oy + ch, ox:ox + cw] = np.asarray(img3_a, dtype=np.float32) / 255.0

    # Step 3: sample center of each cell
    ys = np.clip((np.arange(rows) + 0.5) * H / rows, 0, H - 1).astype(int)
    xs = np.clip((np.arange(cols) + 0.5) * W / cols, 0, W - 1).astype(int)
    cell_l = canv_l[np.ix_(ys, xs)]
    cell_a = canv_a[np.ix_(ys, xs)]
    return cell_l, cell_a


def process(cell_l, cell_a):
    """Map cell luminance to glyph index, using alpha as a subject mask.

    Strategy: the photo is overwhelmingly dark (shirt/hair). We treat anything
    below SHADOW_THRESH as solid ink (densest glyph). The remaining lit pixels
    (mostly the face) get the lighter glyphs. This way the silhouette stays
    crisp and the face details actually read.
    """
    ramp = RAMP
    n = len(ramp)
    space_idx = n - 1
    blank = cell_a < 0.25
    semi  = (cell_a >= 0.25) & (cell_a < 0.75)

    # Normalize only the LIT pixels (above shadow threshold) so the face's
    # tonal range fills the lighter half of the ramp.
    lit = cell_l >= SHADOW_THRESH
    if lit.any():
        # stretch using tighter percentiles so the face's gray range gets the
        # full MID_GLYPH_IDX..n-1 band (otherwise most face pixels end up
        # clustered at the lightest glyph and the face looks washed out).
        lo = np.percentile(cell_l[lit], 15)
        hi = np.percentile(cell_l[lit], 95)
    else:
        lo, hi = 0.0, 1.0
    if hi - lo > 1e-6:
        lit_norm = (cell_l - lo) / (hi - lo)
    else:
        lit_norm = np.zeros_like(cell_l)
    lit_norm = np.clip(lit_norm, 0, 1)
    lit_norm = np.power(lit_norm, GAMMA)
    lit_norm = (lit_norm - 0.5) * CONTRAST + 0.5
    lit_norm = np.clip(lit_norm, 0, 1)

    # Map lit_norm -> [MID_GLYPH_IDX .. n-1) so the face uses the lighter half
    # of the ramp; shadow cells -> 0 (densest glyph).
    idx = np.where(
        lit,
        np.clip(MID_GLYPH_IDX + (lit_norm * (n - 1 - MID_GLYPH_IDX) + 0.5).astype(int), 0, n - 1),
        np.where(cell_a > 0.4, SHADOW_GLYPH_IDX, space_idx),
    )

    # Soft mask -> walk one glyph sparser for anti-aliased edges
    idx = np.where(semi, np.minimum(idx + 1, n - 1), idx)

    # Below WHITE_FLOOR -> solid ink (kill any background noise inside subject)
    idx[(cell_a > 0.4) & (cell_l < WHITE_FLOOR)] = SHADOW_GLYPH_IDX

    idx = idx.astype(int)
    return idx


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    rows = max(10, int(round(COLS * CHAR_ASPECT * (H / W))))
    img = Image.open(SOURCE)
    if AUTO_CROP:
        img = autocrop(img)

    cell_l, cell_a = sample_field(img, rows, COLS)
    idx = process(cell_l, cell_a)

    fh = H / rows
    top = TOP_PAD_FRAC * H
    cols_cw = W / COLS
    font_family = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    lines = []
    for r in range(rows):
        lines.append("".join(RAMP[i] for i in idx[r]))

    static = os.environ.get("STATIC", "0") == "1"

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
               f'viewBox="0 0 {W} {H}" font-family="{font_family}" '
               f'font-size="{fh:.4f}" fill="{GLYPH}">')
    if BG != "none":
        svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

    # Per-line clip-rect animation (typewriter)
    defs = []
    vals = ";".join(f"{i*cols_cw:.2f}" for i in range(COLS + 1))
    for r in range(rows):
        if static:
            defs.append(f'<clipPath id="c{r}"><rect x="0" y="{top + r*fh:.3f}" '
                        f'width="{W}" height="{fh:.3f}"/></clipPath>')
        else:
            defs.append(
                f'<clipPath id="c{r}"><rect x="0" y="{top + r*fh:.3f}" width="0" '
                f'height="{fh:.3f}">'
                f'<animate attributeName="width" calcMode="discrete" '
                f'values="{vals}" begin="{r*STAGGER:.3f}s" dur="{ROW_DUR}" '
                f'fill="freeze"/></rect></clipPath>'
            )
    svg.append("<defs>" + "".join(defs) + "</defs>")

    # One text element per line, clipped by its own clip-path.
    # If ANIMATE_COLOR, each row cycles through COLOR_PALETTE with a stagger
    # so the color sweeps down the portrait like a wave.
    palette = COLOR_PALETTE if ANIMATE_COLOR else [GLYPH]
    # Build a values list of hex colors at 1s steps across the cycle
    pal_vals = ";".join(palette + [palette[0]])
    n_pal = len(palette)

    for r in range(rows):
        y = top + (r + 0.82) * fh
        if ANIMATE_COLOR and not static:
            # Wave-stagger: each row starts the color cycle COLOR_STAGGER*r
            # seconds later so colors cascade down the portrait.
            begin = f"{r*COLOR_STAGGER:.2f}s"
            svg.append(
                f'<text x="0" y="{y:.3f}" textLength="{float(W):.3f}" '
                f'lengthAdjust="spacingAndGlyphs" clip-path="url(#c{r})" '
                f'fill="{palette[r % n_pal]}">'
                f'<animate attributeName="fill" values="{pal_vals}" '
                f'dur="{COLOR_CYCLE_S}s" begin="{begin}" '
                f'repeatCount="indefinite"/>'
                f'{esc(lines[r])}</text>'
            )
        else:
            svg.append(
                f'<text x="0" y="{y:.3f}" textLength="{float(W):.3f}" '
                f'lengthAdjust="spacingAndGlyphs" clip-path="url(#c{r})" '
                f'fill="{GLYPH}">'
                f'{esc(lines[r])}</text>'
            )

    # Blinking terminal cursor at the end of the last typed line
    if CURSOR and not static:
        end_row = rows - 1
        svg.append(
            f'<rect x="0" y="{top + end_row*fh:.3f}" width="0" height="{fh:.3f}" '
            f'fill="{GLYPH}">'
            f'<animate attributeName="width" values="0;0;4;4;0;0" '
            f'keyTimes="0;0.06;0.5;0.9;0.95;1" dur="{CURSOR_BLINK}" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;1;0;0" '
            f'keyTimes="0;0.06;0.5;0.9;0.95;1" dur="{CURSOR_BLINK}" repeatCount="indefinite"/>'
            f'</rect>'
        )

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(svg))
    print(f"wrote {OUT}  ({rows} rows x {COLS} cols, {rows*COLS} glyphs, "
          f"cell={cols_cw:.2f}px)" + ("  [STATIC]" if static else "  [animated]"))


if __name__ == "__main__":
    build()