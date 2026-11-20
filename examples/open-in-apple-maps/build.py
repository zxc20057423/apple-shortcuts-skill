#!/usr/bin/env python3
"""
Build "在 Apple 地圖開啟" (Open in Apple Maps) — a Share Sheet shortcut that
takes a Google Maps link and opens the same place in Apple Maps.

Fixes vs. the common broken version:
  1. Expands short links (maps.app.goo.gl) before parsing.
  2. Prefers the place pin coordinates (!3d<lat>!4d<lng>) over the
     @<lat>,<lng> viewport centre, which is what made the old one open
     "nearby, but not the place".
  3. Falls back to place name / q / query / destination search terms.

Run test_logic.py first — it simulates this exact regex chain in Python.

    python3 -m venv .venv && .venv/bin/pip install python-shortcuts
    .venv/bin/python build.py        # writes the unsigned .shortcut

The output is UNSIGNED: sign it before installing on iOS >= 15 (SKILL.md).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from build_template import build, rep  # noqa: E402

from shortcuts.actions import (  # noqa: E402
    CommentAction,
    ExpandURLAction,
    OpenURLAction,
    SetVariableAction,
    TextAction,
    URLDecodeAction,
    URLEncodeAction,
)

NAME = "在 Apple 地圖開啟"

ACTIONS = [
    CommentAction(
        data={
            "text": "Expand the short link and decode first; coordinates prefer "
            "the place pin (!3d/!4d) over the @ viewport centre; "
            "fall back to name/address search."
        }
    ),
    ExpandURLAction(),
    URLDecodeAction(),
    # --- coordinate extraction, most authoritative first ---
    rep(r".*!3d(-?[0-9.]+)!4d(-?[0-9.]+).*", "$1,$2"),          # place pin
    rep(r".*@(-?[0-9.]+),(-?[0-9.]+).*", "$1,$2"),              # viewport centre
    rep(r".*[?&](ll|center|sll)=(-?[0-9.]+),(-?[0-9.]+).*", "$2,$3"),
    rep(r".*[?&]viewpoint=(-?[0-9.]+),(-?[0-9.]+).*", "$1,$2"),
    rep(r".*[?&]q=loc:(-?[0-9.]+),(-?[0-9.]+).*", "$1,$2"),
    # --- text fallbacks ---
    rep(r".*/place/([^/]+).*", "$1"),                           # place name
    rep(r".*[?&]q=([^&]+).*", "$1"),
    rep(r".*[?&]query=([^&]+).*", "$1"),
    rep(r".*[?&]destination=([^&]+).*", "$1"),
    rep(r"^loc:", ""),
    rep(r"\+", " "),
    # --- open in Apple Maps as a search (works for coords and names) ---
    URLEncodeAction(),
    SetVariableAction(data={"name": "appleQuery"}),
    TextAction(data={"text": "https://maps.apple.com/?q={{appleQuery}}"}),
    OpenURLAction(),
]

if __name__ == "__main__":
    build(NAME, ACTIONS, f"{NAME}.shortcut")
