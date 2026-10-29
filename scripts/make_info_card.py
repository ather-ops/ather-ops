#!/usr/bin/env python3
"""
Build a neofetch-style info card (monochrome) from a ROWS list.

Usage:
    python scripts/make_info_card.py          # -> info-card.svg

The card is authored to be the SAME height as the portrait (H) so the README
table lines up. Font size auto-fits so no value ever clips off the right edge.

Animation (all SMIL, works inside <img> on GitHub):
    - staggered fade-up reveal of every row (cascade down the card)
    - travelling dashed frame border
    - blinking terminal cursor after the host tag
    - soft glow pulse behind the title
    - a slow vertical scanline sweeping the whole card
    - hover highlight on each row
    - breathing dots beside each row
    - corner brackets in a terminal style

PORTABILITY RULES (learned the hard way, keep them):
    1. Every animated element must carry its FINAL visible state in the base
       attributes, and the <animate> only ENHANCES it. Never start at
       opacity="0" in the base markup, or static renderers (cairosvg, image
       previews, PDF export) show a blank card.
    2. Never use mix-blend-mode: static renderers do not support it and
       paint the element as an opaque block.
    3. Text content goes INSIDE the <text> element, before any <animate>.

Only the config block below should need editing.
"""
import os

# ------------------------------------------------------------------ config
OUT     = "info-card.svg"
W       = 490
H       = 460
FONT    = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
GLYPH   = "#1f2937"
ACCENT  = "#475569"
BG      = "none"

HOST    = "ather@ather-ops"
HOST_TAG = "ML / AI Engineer"
FOOTER  = "Let’s build something thoughtful."

ROWS = [
    ("Name",      "Ather Assadullah Peer"),
    ("Role",      "ML / AI Engineer"),
    ("Focus",     "RAG Systems  ·  Agentic AI  ·  LLMs"),
    ("Stack",     "Python · FAISS · Groq · smolagents"),
    ("Skills",    "RAG · Multi-tool agents · ML from scratch"),
    ("Repos",     "14 public · 917 contributions / yr"),
    ("LeetCode",  "100+ problems · 50 & 100 Days Badges 2026"),
    ("Edu",       "CSE in AI/ML at LPU present"),
    ("Email",     "peerather07@gmail.com"),
]
# ------------------------------------------------------------------ /config

SIDE_PAD = 34
HEAD_H   = 88
GAP_RULE = 20
GAP_FOOT = 26

# animation timings
STAGGER      = 0.09      # seconds between each row's reveal
ROW_FADE     = 0.45      # duration of one row's fade-up
CYCLE        = 6.0       # frame dash travel period
SCAN_PERIOD  = 7.0       # scanline sweep period
CURSOR_BLINK = 1.1


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build():
    lw = max(len(l) for l, _ in ROWS) + 1
    n = len(ROWS)
    longest_val = max(len(v) for _, v in ROWS)
    longest_label = int(lw)
    px_widget = (longest_label + longest_val) * 0.62
    fs = (W - 2 * SIDE_PAD) / px_widget
    fs = min(fs, 21)
    fs = min(fs, (H - HEAD_H - GAP_FOOT - GAP_RULE - 8) / (n + 0.35))

    s = []
    s.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}" fill="{GLYPH}">'
    )

    # ---- defs -----------------------------------------------------------
    s.append(
        '<defs>'
        '<radialGradient id="title-glow" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#cbd5e1"/>'
        '<stop offset="0.55" stop-color="#eef2f7"/>'
        '<stop offset="1" stop-color="#ffffff"/>'
        '</radialGradient>'
        '<linearGradient id="frame-grad" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#1f2937"/>'
        '<stop offset="0.5" stop-color="#94a3b8"/>'
        '<stop offset="1" stop-color="#1f2937"/>'
        f'<animate attributeName="x1" values="0;1;0" dur="{CYCLE}s" repeatCount="indefinite"/>'
        f'<animate attributeName="y1" values="0;1;0" dur="{CYCLE}s" repeatCount="indefinite"/>'
        f'<animate attributeName="x2" values="1;0;1" dur="{CYCLE}s" repeatCount="indefinite"/>'
        f'<animate attributeName="y2" values="1;0;1" dur="{CYCLE}s" repeatCount="indefinite"/>'
        '</linearGradient>'
        '</defs>'
    )

    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

    # ---- glow behind the title -------------------------------------------
    # soft glow behind the title (ellipse, not full-card rect, so it stays a
    # subtle wash instead of a visible block in static renderers)
    s.append(
        f'<ellipse cx="120" cy="34" rx="210" ry="95" '
        f'fill="url(#title-glow)" opacity="0.5">'
        f'<animate attributeName="opacity" values="0.5;0.22;0.5" '
        f'dur="{SCAN_PERIOD}s" repeatCount="indefinite"/>'
        f'</ellipse>'
    )

    # ---- header -----------------------------------------------------------
    head_y = SIDE_PAD + 14
    s.append(
        f'<text x="{SIDE_PAD}" y="{head_y}" font-size="{fs+5:.1f}" '
        f'font-weight="700" fill="{GLYPH}">{esc(HOST)}'
        f'<animate attributeName="opacity" values="1;0.72;1" '
        f'dur="{SCAN_PERIOD}s" begin="0.8s" repeatCount="indefinite"/>'
        f'</text>'
    )
    if HOST_TAG:
        s.append(
            f'<text x="{SIDE_PAD}" y="{head_y + fs*1.2:.1f}" '
            f'font-size="{fs*0.58:.1f}" fill="{ACCENT}">{esc(HOST_TAG)}'
            f'<animate attributeName="opacity" values="1;0.55;1" '
            f'dur="{SCAN_PERIOD}s" begin="1.4s" repeatCount="indefinite"/>'
            f'</text>'
        )
        # blinking terminal cursor
        tag_w = len(HOST_TAG) * fs * 0.58 * 0.58
        s.append(
            f'<rect x="{SIDE_PAD + tag_w + 5:.1f}" '
            f'y="{head_y + fs*1.2 - fs*0.42:.1f}" width="{fs*0.30:.1f}" '
            f'height="{fs*0.52:.1f}" fill="{GLYPH}" opacity="0.9">'
            f'<animate attributeName="opacity" values="1;1;0.15;0.15;1" '
            f'keyTimes="0;0.4;0.5;0.9;1" dur="{CURSOR_BLINK}s" '
            f'begin="1s" repeatCount="indefinite"/>'
            f'</rect>'
        )

    rule_y = head_y + fs * 2.15
    s.append(
        f'<line x1="{SIDE_PAD}" y1="{rule_y}" x2="{W-SIDE_PAD}" y2="{rule_y}" '
        f'stroke="url(#frame-grad)" stroke-width="1.6" stroke-dasharray="3 4" '
        f'opacity="0.7">'
        f'<animate attributeName="stroke-dashoffset" from="0" to="-14" '
        f'dur="1.4s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.55;0.9;0.55" '
        f'dur="{SCAN_PERIOD}s" repeatCount="indefinite"/>'
        f'</line>'
    )
    s.append(
        f'<line x1="{SIDE_PAD}" y1="{rule_y + 3}" x2="{W-SIDE_PAD}" '
        f'y2="{rule_y + 3}" stroke="{GLYPH}" stroke-width="0.9" opacity="0.3">'
        f'<animate attributeName="opacity" values="0.3;0.05;0.3" '
        f'dur="{SCAN_PERIOD}s" begin="0.5s" repeatCount="indefinite"/>'
        f'</line>'
    )

    # ---- rows --------------------------------------------------------------
    vx = SIDE_PAD + lw * fs * 0.62 + 6
    y = rule_y + GAP_RULE
    line_step = (H - HEAD_H - GAP_RULE - GAP_FOOT - 10) / (n + 0.5)
    line_step = max(line_step, fs * 1.35)
    for i, (label, value) in enumerate(ROWS):
        yy = y + i * line_step
        t0 = 0.45 + i * STAGGER
        # hover highlight behind the row
        s.append(
            f'<rect x="{SIDE_PAD-8}" y="{yy-fs*0.78:.1f}" '
            f'width="{W-2*SIDE_PAD+16}" height="{fs*1.18:.1f}" '
            f'rx="6" ry="6" fill="{ACCENT}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="0.13" dur="0.22s" '
            f'begin="mouseover" fill="freeze"/>'
            f'<animate attributeName="opacity" from="0.13" to="0" dur="0.35s" '
            f'begin="mouseout" fill="freeze"/>'
            f'</rect>'
        )
        # label
        s.append(
            f'<text x="{SIDE_PAD}" y="{yy:.1f}" font-size="{fs:.1f}" '
            f'fill="{ACCENT}">{esc(label)}'
            f'<animate attributeName="opacity" values="1;0.55;1" '
            f'dur="{ROW_FADE}s" begin="{t0:.2f}s" fill="freeze"/>'
            f'</text>'
        )
        # value
        s.append(
            f'<text x="{vx:.1f}" y="{yy:.1f}" font-size="{fs:.1f}" '
            f'fill="{GLYPH}">{esc(value)}'
            f'<animate attributeName="opacity" values="1;0.6;1" '
            f'dur="{ROW_FADE}s" begin="{t0+0.05:.2f}s" fill="freeze"/>'
            f'</text>'
        )
        # breathing dot
        s.append(
            f'<circle cx="{SIDE_PAD-13}" cy="{yy-fs*0.26:.1f}" r="1.7" '
            f'fill="{GLYPH}" opacity="0.45">'
            f'<animate attributeName="r" values="1.4;2.3;1.4" '
            f'dur="2.4s" begin="{t0:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.3;0.6;0.3" '
            f'dur="2.4s" begin="{t0:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    # ---- footer ------------------------------------------------------------
    foot_y = y + n * line_step + 16
    s.append(
        f'<text x="{SIDE_PAD}" y="{foot_y:.1f}" font-size="{fs*0.72:.1f}" '
        f'fill="{ACCENT}" opacity="0.85">{esc(FOOTER)}'
        f'<animate attributeName="opacity" values="0.85;0.45;0.85" '
        f'dur="{SCAN_PERIOD}s" begin="{0.45 + n*STAGGER + 0.4:.2f}s" '
        f'repeatCount="indefinite"/>'
        f'</text>'
    )

    # ---- scanline sweep ----------------------------------------------------
    band_h = 170
    s.append(
        f'<rect x="0" y="{-band_h}" width="{W}" height="{band_h}" '
        f'fill="url(#scan-band)" opacity="0.26" pointer-events="none">'
        f'<animate attributeName="y" from="{-band_h}" to="{H}" '
        f'dur="{SCAN_PERIOD}s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    # ---- frame -------------------------------------------------------------
    s.append(
        f'<rect x="4" y="4" width="{W-8}" height="{H-8}" rx="14" ry="14" '
        f'fill="none" stroke="url(#frame-grad)" stroke-width="1.5" '
        f'opacity="0.45" stroke-dasharray="26 14">'
        f'<animate attributeName="stroke-dashoffset" from="40" to="0" '
        f'dur="{CYCLE}s" repeatCount="indefinite"/>'
        f'</rect>'
    )
    s.append(
        f'<rect x="4" y="4" width="{W-8}" height="{H-8}" rx="14" ry="14" '
        f'fill="none" stroke="{ACCENT}" stroke-width="1.2" opacity="0.22">'
        f'<animate attributeName="opacity" values="0.16;0.36;0.16" '
        f'dur="{SCAN_PERIOD}s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    # corner brackets
    for cx, cy, dx, dy in ((4, 4, 1, 1), (W-4, 4, -1, 1),
                           (4, H-4, 1, -1), (W-4, H-4, -1, -1)):
        s.append(
            f'<path d="M {cx} {cy + dy*22} L {cx} {cy} L {cx + dx*22} {cy}" '
            f'fill="none" stroke="{GLYPH}" stroke-width="2.2" '
            f'stroke-linecap="round" opacity="0.5">'
            f'<animate attributeName="opacity" values="0.5;0.18;0.5" '
            f'dur="{SCAN_PERIOD}s" begin="1s" repeatCount="indefinite"/>'
            f'</path>'
        )

    s.append("</svg>")

    with open(OUT, "w") as f:
        f.write("".join(s))
    print(f"wrote {OUT}  ({n} rows, fs={fs:.1f})")


if __name__ == "__main__":
    build()
