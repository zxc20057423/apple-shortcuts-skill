#!/usr/bin/env python3
"""
Simulate the shortcut's regex chain in Python before building anything.

The chain mirrors build.py action-for-action: each rule rewrites the value
only if it matches, otherwise the value passes through unchanged — the same
semantics as chained Replace Text actions in Shortcuts.

    python3 test_logic.py
"""
import re
from urllib.parse import unquote

STEPS = [
    (r".*!3d(-?[0-9.]+)!4d(-?[0-9.]+).*", r"\1,\2"),
    (r".*@(-?[0-9.]+),(-?[0-9.]+).*", r"\1,\2"),
    (r".*[?&](?:ll|center|sll)=(-?[0-9.]+),(-?[0-9.]+).*", r"\1,\2"),
    (r".*[?&]viewpoint=(-?[0-9.]+),(-?[0-9.]+).*", r"\1,\2"),
    (r".*[?&]q=loc:(-?[0-9.]+),(-?[0-9.]+).*", r"\1,\2"),
    (r".*/place/([^/]+).*", r"\1"),
    (r".*[?&]q=([^&]+).*", r"\1"),
    (r".*[?&]query=([^&]+).*", r"\1"),
    (r".*[?&]destination=([^&]+).*", r"\1"),
    (r"^loc:", ""),
    (r"\+", " "),
]


def chain(url: str) -> str:
    value = unquote(url)  # the shortcut URL-decodes right after expanding
    for pattern, replacement in STEPS:
        value = re.sub(pattern, replacement, value)
    return value


TESTS = {
    # pin coordinates must win over the viewport centre
    "https://www.google.com/maps/place/%E5%8D%A1%E5%95%A1%E9%82%A3/@24.1560,120.6630,17z/data=!4m6!3m5!1s0x123!8m2!3d24.1234!4d120.5678":
        "24.1234,120.5678",
    # no pin segment -> viewport centre is the best available
    "https://www.google.com/maps/place/Some+Shop/@25.0330,121.5654,18z/data=!4m6":
        "25.0330,121.5654",
    # text search URL
    "https://www.google.com/maps/search/?api=1&query=%E5%8F%B0%E4%B8%AD%E5%B8%82%E5%A4%A7%E9%87%8C%E5%8D%80%E4%BB%81%E7%A6%8F%E8%A1%97":
        "台中市大里區仁福街",
    # coordinate search URL (percent-encoded comma)
    "https://www.google.com/maps/search/?api=1&query=24.08%2C120.67":
        "24.08,120.67",
    # directions URL -> destination name
    "https://www.google.com/maps/dir/?api=1&destination=%E9%84%B0%E9%95%B7%E5%81%9C%E8%BB%8A%E5%A0%B4":
        "鄰長停車場",
    # ll parameter
    "https://maps.google.com/?ll=24.1500,120.6800&z=16":
        "24.1500,120.6800",
    # plain address passes through untouched
    "台中市大里區仁福街100號":
        "台中市大里區仁福街100號",
}

if __name__ == "__main__":
    failed = 0
    for url, expected in TESTS.items():
        got = chain(url)
        ok = got == expected
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {got!r}" + ("" if ok else f"  (expected {expected!r})"))
    raise SystemExit(1 if failed else 0)
