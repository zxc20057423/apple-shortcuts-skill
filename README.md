# apple-shortcuts-skill

An AI-agent skill for **writing real, installable Apple Shortcuts without a Mac**.

Most agents can only tell you which buttons to tap in the Shortcuts app. This
skill teaches an agent the full pipeline instead:

1. **Design** the workflow as data — including the trick of using an ordered
   chain of regex Replace Text actions as branch-free if/else logic.
2. **Test the logic** in Python against realistic inputs before building.
3. **Build** an unsigned `.shortcut` with
   [`python-shortcuts`](https://pypi.org/project/python-shortcuts/), including
   the Replace Text action the library is missing and the plist
   post-processing (Share Sheet type, input classes, icon) it doesn't do.
4. **Sign** the file — since iOS 15, unsigned `.shortcut` files are refused
   with a bare "could not load file" error. Signing works via a Mac
   (`shortcuts sign`) or a remote signing service such as
   [Shortcuty Sign](https://sign.shortcuty.app) or RoutineHub HubSign
   (with the user's consent — the agent must ask before uploading).
5. **Deliver** a signed file (verify the `AEA1` magic) that the user taps
   once to install, plus one concrete on-device test.

## Contents

- [`SKILL.md`](SKILL.md) — the skill itself. Drop it into your agent's skills
  directory (Claude Code, Codex, Muse, …) and the agent can follow it.
- [`tools/build_template.py`](tools/build_template.py) — reusable builder:
  custom Replace Text action, plist post-processing, and a self-verifying
  dump of the action list.
- [`examples/open-in-apple-maps/`](examples/open-in-apple-maps/) — a complete
  worked example: a Share Sheet shortcut that opens Google Maps links in
  Apple Maps. The original floating around the internet opens the *wrong
  place* — it parses the `@lat,lng` viewport centre instead of the
  `!3d…!4d…` pin coordinates, and never expands short links. Includes
  `test_logic.py`, a 7-case simulation of the exact regex chain used on
  device.

## Quick start

```bash
cd examples/open-in-apple-maps
python3 test_logic.py                     # 7/7 cases should pass
python3 -m venv .venv
.venv/bin/pip install python-shortcuts
.venv/bin/python build.py                 # writes the unsigned .shortcut
# then sign it (see SKILL.md Step 4) and send it to the iPhone
```

## Requirements

- Python 3.10+
- `python-shortcuts` (pip)
- For signing: a Mac with Shortcuts, **or** an account-free remote signing
  service, **or** an iCloud share from a device that has the shortcut.

## License

MIT — see [`LICENSE`](LICENSE).
