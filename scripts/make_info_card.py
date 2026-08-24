#!/usr/bin/env python3
"""
Build a neofetch-style info card (monochrome) from a ROWS list.

Usage:
    python scripts/make_info_card.py          # -> info-card.svg

The card is authored to be the SAME height as the portrait (H) so the README
table lines up. Font size auto-fits so no value ever clips off the right edge.

Only the config block below should need editing.  (ROWS are your real
experience / stack / highlights -- NOT GitHub stats; the graph covers those.)
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
HOST_TAG = "Machine Learning Engineer"

# (label, value) -- edit freely; label column auto-aligns to the longest.
ROWS = [
    ("Name",      "Ather Assadullah Peer"),
    ("Role",      "Machine Learning Engineer"),
    ("Focus",     "RAG Systems  ·  Agentic AI  ·  LLM Apps"),
    ("Stack",     "Python · PyTorch · LangChain · FAISS"),
    ("Data",      "PostgreSQL · pgvector · Redis · Qdrant"),
    ("Now",       "RAG & agentic AI in production"),
    ("Portfolio", "vercel.app/…"),
    ("LinkedIn",  "/in/ather-assadullah-164492301"),
    ("X",         "@PeerAther47970"),
]
# ------------------------------------------------------------------ /config

SIDE_PAD = 34
HEAD_H   = 88        # space for host line + tag + rule
GAP_RULE = 20        # gap below the rule before rows
GAP_FOOT = 26        # gap between last row and footer


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    # label column width (in characters)
    lw = max(len(l) for l, _ in ROWS) + 1
    n = len(ROWS)

    # longest value length across rows
    longest_val = max(len(v) for _, v in ROWS)
    longest_label = int(lw)

    # monospace char width ~ 0.62 * font-size; solve fs so longest row fits
    #   SIDE_PAD + lw*fs*0.62 + longest_val*fs*0.62 <= W - SIDE_PAD
    px_widget = (longest_label + longest_val) * 0.62
    fs = (W - 2 * SIDE_PAD) / px_widget
    fs = min(fs, 21)          # cap size
    # also ensure vertical fit: HEAD_H + n*line_h + GAP_FOOT <= H
    row_h = 26
    fs = min(fs, (H - HEAD_H - GAP_FOOT - GAP_RULE - 8) / (n + 0.35))

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}" fill="{GLYPH}">'
    )
    svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

    # ---- header: HOST line + tag + dashed rule --------------------
    head_y = SIDE_PAD + 14
    svg.append(
        f'<text x="{SIDE_PAD}" y="{head_y}" font-size="{fs+5:.1f}" '
        f'font-weight="700" fill="{GLYPH}">{esc(HOST)}</text>'
    )
    if HOST_TAG:
        svg.append(
            f'<text x="{SIDE_PAD}" y="{head_y + fs*1.2:.1f}" font-size="{fs*0.58:.1f}" '
            f'fill="{ACCENT}">{esc(HOST_TAG)}</text>'
        )
    rule_y = head_y + fs * 2.15
    svg.append(
        f'<line x1="{SIDE_PAD}" y1="{rule_y}" x2="{W-SIDE_PAD}" y2="{rule_y}" '
        f'stroke="{ACCENT}" stroke-width="1.4" stroke-dasharray="3 4" opacity="0.6"/>'
    )

    # ---- rows -----------------------------------------------------
    vx = SIDE_PAD + lw * fs * 0.62 + 6
    y = rule_y + GAP_RULE
    line_step = (H - HEAD_H - GAP_RULE - GAP_FOOT - 10) / (n + 0.5)
    line_step = max(line_step, fs * 1.35)
    for i, (label, value) in enumerate(ROWS):
        yy = y + i * line_step
        svg.append(
            f'<text x="{SIDE_PAD}" y="{yy:.1f}" font-size="{fs:.1f}" '
            f'fill="{ACCENT}">{esc(label)}</text>'
        )
        svg.append(
            f'<text x="{vx:.1f}" y="{yy:.1f}" font-size="{fs:.1f}" '
            f'fill="{GLYPH}">{esc(value)}</text>'
        )

    # ---- footer -----------------------------------------------------
    foot_y = y + n * line_step + 16
    svg.append(
        f'<text x="{SIDE_PAD}" y="{foot_y:.1f}" font-size="{fs*0.72:.1f}" '
        f'fill="{ACCENT}" opacity="0.85">Let&apos;s build something thoughtful.</text>'
    )

    # ---- clean rounded frame -------------------------------------
    svg.append(
        f'<rect x="4" y="4" width="{W-8}" height="{H-8}" rx="14" ry="14" '
        f'fill="none" stroke="{ACCENT}" stroke-width="1.4" opacity="0.4"/>'
    )
    svg.append("</svg>")

    with open(OUT, "w") as f:
        f.write("".join(svg))
    print(f"wrote {OUT}  ({n} rows, fs={fs:.1f})")


if __name__ == "__main__":
    build()
