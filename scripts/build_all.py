#!/usr/bin/env python3
"""
Build all decorative SVGs in one pass: dividers, section titles, project
accent strips, and tech pills. Run this whenever you add a section, change a
title, or rebrand.

Usage:
    python scripts/build_all.py
"""
import subprocess
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd, env_extra=None):
    print(">>", " ".join(cmd))
    e = os.environ.copy()
    if env_extra:
        e.update(env_extra)
    r = subprocess.run(cmd, cwd=os.path.dirname(HERE), env=e)
    if r.returncode != 0:
        sys.exit(r.returncode)


def main():
    # ---- Dividers (one per section, with matching palette) ---------------
    divider_specs = [
        # filename, env overrides for ACCENT_A/M/B
        ("divider-hero.svg",       {"ACCENT_A": "#1e3a8a", "ACCENT_M": "#7c3aed", "ACCENT_B": "#0891b2"}),
        ("divider-contrib.svg",    {"ACCENT_A": "#1e3a8a", "ACCENT_M": "#7c3aed", "ACCENT_B": "#be185d"}),
        ("divider-about.svg",      {"ACCENT_A": "#0f766e", "ACCENT_M": "#0891b2", "ACCENT_B": "#1e3a8a"}),
        ("divider-education.svg",  {"ACCENT_A": "#b45309", "ACCENT_M": "#d97706", "ACCENT_B": "#9a3412"}),
        ("divider-build.svg",      {"ACCENT_A": "#1e3a8a", "ACCENT_M": "#3730a3", "ACCENT_B": "#6d28d9"}),
        ("divider-featured.svg",   {"ACCENT_A": "#1e40af", "ACCENT_M": "#7c3aed", "ACCENT_B": "#be185d"}),
        ("divider-tech.svg",       {"ACCENT_A": "#0f172a", "ACCENT_M": "#334155", "ACCENT_B": "#475569"}),
        ("divider-key.svg",        {"ACCENT_A": "#9a3412", "ACCENT_M": "#be185d", "ACCENT_B": "#7c3aed"}),
    ]
    for fn, env_extra in divider_specs:
        # Use env to override the divider's accent palette
        env = {f"DIVIDER_OUT_NAME": fn, **env_extra}
        run(["python3", os.path.join(HERE, "make_divider.py")], env_extra=env_extra)
        if os.path.exists("divider.svg"):
            os.replace("divider.svg", fn)

    # ---- Section titles (gradient text, hue cycle) -----------------------
    title_specs = [
        ("title-contrib.svg",  "Contribution"),
        ("title-about.svg",    "About Me"),
        ("title-edu.svg",      "Education"),
        ("title-build.svg",    "What I Build"),
        ("title-featured.svg", "Featured Projects"),
        ("title-tech.svg",     "Tech Stack"),
        ("title-key.svg",      "Key Achievements"),
    ]
    for fn, text in title_specs:
        run(["python3", os.path.join(HERE, "make_section_title.py"), text, fn])

    # ---- Hero (terminal-style code header) -----------------------------
    run(["python3", os.path.join(HERE, "make_hero.py")])

    # ---- Banner (wide dotted-art header) ------------------------------
    run(["python3", os.path.join(HERE, "make_banner.py")])

    # ---- Project accent strips -------------------------------------------
    project_specs = [
        ("accent-xpect.svg",      "Xpect AI",         "xpect-ai"),
        ("accent-amazn.svg",      "Amazn AI",         "amazn-ai"),
        ("accent-pulse.svg",      "PulseMesh",        "pulsemesh"),
        ("accent-atlas.svg",      "Atlas Agent",      "atlas-agent"),
        ("accent-hospital.svg",   "Hospital SQL",     "hospital-sql"),
        ("accent-cafe.svg",       "Cafe Sales",       "cafe-sales"),
        ("accent-ml.svg",         "ML from Scratch",  "ml-from-scratch"),
    ]
    for fn, label, slug in project_specs:
        run(["python3", os.path.join(HERE, "make_project_accent.py"), fn, label, slug])

    # ---- Tech pills (one per technology, color coded) --------------------
    pill_specs = [
        ("pill-python.svg",   "Python",        "#1e3a8a"),
        ("pill-numpy.svg",    "NumPy",         "#3730a3"),
        ("pill-pandas.svg",   "Pandas",        "#1e40af"),
        ("pill-sklearn.svg",  "scikit-learn",  "#7c3aed"),
        ("pill-postgres.svg", "PostgreSQL",    "#0891b2"),
        ("pill-sql.svg",      "SQL",           "#0e7490"),
        ("pill-fastapi.svg",  "FastAPI",       "#15803d"),
        ("pill-streamlit.svg","Streamlit",     "#be185d"),
        ("pill-hf.svg",       "HuggingFace",   "#9a3412"),
        ("pill-langchain.svg","LangChain",     "#b45309"),
        ("pill-aws.svg",      "AWS",           "#d97706"),
        ("pill-git.svg",      "Git",           "#334155"),
        ("pill-chroma.svg",   "ChromaDB",      "#7c3aed"),
        ("pill-faiss.svg",    "FAISS",         "#3730a3"),
        ("pill-smol.svg",     "smolagents",    "#be185d"),
        ("pill-async.svg",    "asyncio",       "#0891b2"),
    ]
    for fn, label, color in pill_specs:
        run(["python3", os.path.join(HERE, "make_tech_pill.py"), fn, label, color])

    print("done.")


if __name__ == "__main__":
    main()