# Example: Open in Apple Maps

A Share Sheet shortcut: share any Google Maps link (or an address) to it, and
the same place opens in Apple Maps.

## Why the common version is broken

Google Maps place URLs contain **two** coordinate pairs:

| Pair | Meaning |
| --- | --- |
| `@24.1560,120.6630` | the map **viewport centre** when the link was copied — moves with the user's panning |
| `!3d24.1234!4d120.5678` | the **place pin** itself |

Shortcuts floating around parse the `@` pair (or nothing at all, when handed
an unexpanded `maps.app.goo.gl` short link), so Apple Maps opens "nearby but
wrong".

## The fix (17 actions, zero conditionals)

1. **Expand URL** — resolve short links first.
2. **URL Decode** — so `%2C` commas and percent-encoded names parse cleanly.
3. An ordered **Replace Text (regex)** chain; each rule fires only on match:
   pin coords → viewport coords → `ll`/`center`/`sll` → `viewpoint` →
   `q=loc:` coords → `/place/<name>` → `q` → `query` → `destination` →
   strip `loc:` → `+` to space.
4. **URL Encode** the result, build `https://maps.apple.com/?q=<result>`,
   **Open URLs**. A `q=` search works for both coordinates and names, which
   is what makes the branch-free design possible.

## Files

- `build.py` — builds the unsigned `.shortcut` (icon and name match the
  original shortcut this replaces).
- `test_logic.py` — simulates the exact chain in Python; 7 cases covering
  pin vs. viewport, text/coordinate search URLs, directions, `ll`, and a
  plain address. Run it before every build.

## Install

Build, sign (see the repo's `SKILL.md`, Step 4), send the signed file to the
iPhone, tap it, **Add Shortcut**. Share any Google Maps place to it and
check that Apple Maps lands on the place itself.
