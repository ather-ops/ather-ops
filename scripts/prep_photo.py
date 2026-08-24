#!/usr/bin/env python3
"""
One-time image prep: rembg background removal + CLAHE local contrast.

Usage:
    python scripts/prep_photo.py <input.jpg> <output.png>

Produces a transparent-background PNG where the subject is isolated and the
local contrast is boosted (CLAHE) so the face is legible instead of a dark blob.
Only the config block below should need editing.
"""
import sys
import os
import numpy as np
from PIL import Image, ImageEnhance
import cv2

# ------------------------------------------------------------------ config
CLIP_LIMIT = 4.5      # CLAHE clip limit: higher = stronger local contrast
GRID_SIZE  = 4        # CLAHE tile grid size (smaller = finer local contrast)
BRIGHTNESS = 1.08     # gentle overall lift after equalization
MODEL      = "u2net"  # lightweight seg model (u2net ~176MB; use bria-rmbg if you have RAM)
# ------------------------------------------------------------------ /config


def prep(input_path: str, output_path: str) -> None:
    img = Image.open(input_path).convert("RGB")

    # --- background removal (rembg / u2net) ---
    from rembg import remove, new_session
    fg = remove(img, session=new_session(MODEL)).convert("RGBA")  # keeps alpha channel

    # --- CLAHE on the L channel of LAB (local contrast) ---
    rgb = fg.convert("RGB")
    lab = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=CLIP_LIMIT, tileGridSize=(GRID_SIZE, GRID_SIZE))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    out = Image.fromarray(rgb).convert("RGBA")
    out.putalpha(fg.getchannel("A"))          # restore the cut-out mask
    out = ImageEnhance.Brightness(out).enhance(BRIGHTNESS)

    d = os.path.dirname(os.path.abspath(output_path))
    if d:
        os.makedirs(d, exist_ok=True)
    out.save(output_path)
    print(f"prepped -> {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python scripts/prep_photo.py <input.jpg> <output.png>")
        sys.exit(1)
    prep(sys.argv[1], sys.argv[2])
