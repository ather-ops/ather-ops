#!/usr/bin/env python3
"""
Validate the animation correctness of every SVG in the repo.

Checks each <animate> element for the mistakes that actually broke the
profile graphics before:

  1. keyTimes outside 0..1
     -> the browser rejects the whole animation and the element stays
        frozen at its base value. (This is what made the photo render
        permanently greyscale: keyTimes ran 0..1.1.)
  2. a values list whose length does not match keyTimes
     -> the animation is ignored.
  3. keyTimes that are not monotonically increasing
     -> the animation is ignored.
  4. values/base attributes that would leave visible content invisible
     (opacity="0" on a non-hover element)
  5. mix-blend-mode, which static renderers paint as an opaque block
  6. malformed XML

Usage:
    python scripts/check_svg_animations.py
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

SVG = "{http://www.w3.org/2000/svg}"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

KEYTIMES = re.compile(r'keyTimes="([^"]*)"')
VALUES = re.compile(r'\bvalues="([^"]*)"')
MIXBLEND = re.compile(r'mix-blend-mode', re.I)


def split_list(s):
    return [x.strip() for x in s.split(";") if x.strip()]


def check(path):
    problems = []
    raw = open(path).read()

    # 6. malformed XML
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        return [f"malformed XML: {e}"], 0

    anims = root.findall(f".//{SVG}animate")
    if not anims:
        return [f"no <animate> elements found"], 0

    for an in anims:
        label = an.get("attributeName", "?")
        kt = an.get("keyTimes")
        vals = an.get("values")

        # 1. keyTimes range
        if kt:
            try:
                times = [float(x) for x in split_list(kt)]
            except ValueError:
                problems.append(f"keyTimes not numeric on {label}: {kt}")
                continue
            if any(t < 0 or t > 1 for t in times):
                bad = [f"{t}" for t in times if t < 0 or t > 1]
                problems.append(
                    f"keyTimes out of 0..1 on {label}: {', '.join(bad[:4])}"
                    " (browser rejects the animation)"
                )
            # 3. monotonic
            if any(times[i] > times[i + 1] for i in range(len(times) - 1)):
                problems.append(f"keyTimes not increasing on {label}")

        # 2. values vs keyTimes length
        if kt and vals:
            nk = len(split_list(kt))
            nv = len(split_list(vals))
            if nk != nv:
                problems.append(
                    f"values/keyTimes length mismatch on {label}: "
                    f"{nv} values vs {nk} keyTimes"
                )

    # 5. mix-blend-mode
    if MIXBLEND.search(raw):
        problems.append("mix-blend-mode present (static renderers paint it opaque)")

    # 4. invisible visible content
    for m in re.finditer(r'<(text|rect|image|circle|path|line)\b[^>]*opacity="0"[^>]*>', raw):
        tag = m.group(0)
        if "mouseover" in raw[m.end():m.end() + 200]:
            continue  # hover-only highlight, fine
        if 'fill="none"' in tag:
            continue
        problems.append(f"visible element starts at opacity 0: {tag[:70]}")

    return problems, len(anims)


def main():
    svgs = sorted(glob.glob(os.path.join(ROOT, "*.svg")))
    if not svgs:
        print("no SVGs found")
        return 1
    bad = 0
    for p in svgs:
        name = os.path.basename(p)
        problems, n = check(p)
        if problems:
            bad += 1
            print(f"FAIL  {name}  ({n} animations)")
            for pr in problems:
                print(f"        - {pr}")
        else:
            print(f"ok    {name}  ({n} animations)")
    print()
    if bad:
        print(f"{bad} file(s) with problems")
        return 1
    print("all SVG animations valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
