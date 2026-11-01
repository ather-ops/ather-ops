#!/usr/bin/env python3
"""
Shared SVG helpers for the profile graphics.

WHY THIS FILE EXISTS
-------------------
Several earlier animation attempts produced visible "box" artefacts:
hard-edged rectangles from scan bands, smeared white rectangles from
radial "halo" gradients, and chaotic flickering because every element
animated its opacity on its own independent clock.

The helpers here provide the three things that fix those problems:

1. soft_gradient_stops()
   Builds gradient stops that fade to a TRANSPARENT colour rather than to
   white with stop-opacity="0". Browsers handle `stop-color` + a matching
   `stop-opacity` correctly, but when the same gradient is drawn over a
   white page the "transparent white" stop still shows an edge in some
   renderers. Using a fully transparent stop of the SAME colour as the
   band removes the seam.

2. band_masks()
   A soft-edged light band is really a gradient with transparent ends.
   This helper emits the gradient + the rect together so the two can
   never drift apart.

3. wave_begin()
   Computes a begin-time for a travelling wave so that elements in a row
   or column animate in a coherent sweep instead of randomly. The wave
   advances with the element's own index, and every element shares ONE
   period, so the pattern stays stable and readable.

PORTABILITY RULES (keep them):
   1. Animated elements carry their FINAL visible state in the base
      attributes; never base opacity="0" for visible content.
   2. No mix-blend-mode.
   3. Text content goes INSIDE <text>, before any <animate>.
   4. Gradients that must fade out use a transparent stop of the SAME
      colour, not white with stop-opacity="0".
"""
import math

SVG_NS = "http://www.w3.org/2000/svg"


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def soft_band_grad(gid, color="#ffffff", peak=0.55, direction="x"):
    """A gradient that fades smoothly to transparent at BOTH ends.

    direction: "x" -> horizontal band, "y" -> vertical band.
    Uses stop-color with stop-opacity on the outer stops so the band has
    no visible rectangular edge in any renderer.
    """
    if direction == "x":
        x1, y1, x2, y2 = "0", "0", "1", "0"
    else:
        x1, y1, x2, y2 = "0", "0", "0", "1"
    return (
        f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
        f'<stop offset="0" stop-color="{color}" stop-opacity="0"/>'
        f'<stop offset="0.38" stop-color="{color}" stop-opacity="{peak * 0.45:.3f}"/>'
        f'<stop offset="0.5" stop-color="{color}" stop-opacity="{peak:.3f}"/>'
        f'<stop offset="0.62" stop-color="{color}" stop-opacity="{peak * 0.45:.3f}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/>'
        f'</linearGradient>'
    )


def soft_oval_grad(gid, color="#cbd5e1", peak=0.45):
    """A radial wash that fades to transparent at the rim.

    The outer stop is the SAME colour at zero opacity, so the ellipse
    never shows a hard circular or rectangular boundary.
    """
    return (
        f'<radialGradient id="{gid}" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{color}" stop-opacity="{peak:.3f}"/>'
        f'<stop offset="0.55" stop-color="{color}" stop-opacity="{peak * 0.35:.3f}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/>'
        f'</radialGradient>'
    )


def band_rect(x, y, w, h, grad_id, peak_opacity, from_x=None, to_x=None,
              from_y=None, to_y=None, dur=8.0, extra=""):
    """A soft light band that travels across the given rect.

    The band's own opacity animation keeps it subtle so it reads as a
    light sweep, never as a white rectangle.
    """
    if from_x is not None and to_x is not None:
        anim = (f'<animate attributeName="x" from="{from_x}" to="{to_x}" '
                f'dur="{dur}s" repeatCount="indefinite"/>')
    elif from_y is not None and to_y is not None:
        anim = (f'<animate attributeName="y" from="{from_y}" to="{to_y}" '
                f'dur="{dur}s" repeatCount="indefinite"/>')
    else:
        anim = ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
        f'fill="url(#{grad_id})" opacity="{peak_opacity}" '
        f'pointer-events="none"{extra}>'
        f'{anim}'
        f'</rect>'
    )


def wave_begin(index, total, period, span=None, phase=0.0):
    """Begin-time that makes a group animate as a coherent travelling wave.

    index   : position of this element along the wave axis
    total   : number of elements along that axis
    period  : the shared cycle duration (all elements must use the SAME one)
    span    : fraction of the period the wave takes to cross the axis
              (default: the whole period, so the wave is continuous)
    """
    if total <= 1:
        return phase
    frac = index / (total - 1)
    if span is None:
        span = 1.0
    return phase + (frac * span * period) % period


def wave_values(base, peak=None, dip=None):
    """Opacity keyframe values for a breathing wave centred on `base`."""
    peak = peak if peak is not None else min(1.0, base + 0.30)
    dip = dip if dip is not None else base * 0.72
    return f"{base:.3f};{peak:.3f};{base:.3f};{dip:.3f};{base:.3f}"


def wave_keytimes(n=5):
    """Keytimes matching wave_values()."""
    if n == 5:
        return "0;0.25;0.5;0.75;1"
    step = 1.0 / (n - 1)
    return ";".join(f"{i * step:.3f}" for i in range(n))
