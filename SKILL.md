---
name: apple-shortcuts-authoring
description: Author real, installable Apple Shortcuts (.shortcut files) from a Linux/Windows machine with no Mac — build the workflow programmatically, test the logic before building, sign the file so iOS will accept it, and deliver it ready to tap-and-install.
---

# Apple Shortcuts Authoring (no Mac required)

Use this skill when the user wants you to **create or fix an iOS Shortcut for them**,
not just describe the taps. The end product is a signed `.shortcut` file the user
can tap on their iPhone and add directly.

## The one fact everything depends on

Since iOS 15, **Shortcuts refuses unsigned `.shortcut` files**. An unsigned file
tapped on a modern iPhone fails with a generic "could not load file" error.
The old advice "enable Settings → Shortcuts → Allow Untrusted Shortcuts" is
**obsolete** — that toggle no longer exists. A file is importable only if it is:

- shared through an iCloud link from a real Shortcuts app, or
- a signed file (AEA1 container) produced by `shortcuts sign` on a Mac, or
- signed by a remote signing service (see Step 4).

So the pipeline is always: **build unsigned → sign → deliver**. Never send the
user an unsigned file and call it done; verify the signed artifact starts with
the `AEA1` magic bytes before delivering.

## Step 1 — Design the workflow as data, not taps

Write the shortcut's logic as an ordered list of actions. Prefer designs that
avoid fragile control flow when a chain of transforms can do the job:

- A chain of "Replace Text (regex)" actions is order-dependent in a useful way:
  each rule rewrites the value only if it matches, otherwise the value passes
  through unchanged. Put the most specific / most authoritative extraction
  first, fallbacks after. This gives you if/else behaviour with zero
  conditional actions to serialize.
- Test the transform chain in plain Python (`re.sub` with the same patterns)
  against a table of realistic inputs **before** building anything. Regex
  dialect differences (ICU on device vs Python) are small for the patterns
  used here; the simulation catches ordering and greediness bugs, which are
  the ones that actually bite.

## Step 2 — Build the unsigned `.shortcut`

Use the `python-shortcuts` package (`pip install python-shortcuts`) to emit a
binary plist `.shortcut`. Practical notes learned the hard way:

- The library covers common actions (Text, Open URL, Expand URL, URL
  Encode/Decode, Set Variable, Comment, …) but **lacks Match/Replace Text**.
  Add it as a custom action class — see `tools/build_template.py`:
  identifier `is.workflow.actions.text.replace`, parameters
  `WFReplaceTextFind`, `WFReplaceTextReplace`, `WFReplaceTextCaseSensitive`,
  `WFReplaceTextRegularExpression`.
- URL Encode/Decode serialize as `is.workflow.actions.urlencode` with
  `WFEncodeMode` = `Encode`/`Decode`. iOS migrates this legacy identifier
  fine.
- Reference a named variable inside a Text action with `{{variableName}}`
  (the library converts it to the object-replacement-character attachment
  format Shortcuts expects).
- `plistlib.Data` was removed in Python 3.12; if the library's icon dump
  crashes, monkey-patch `Shortcut._get_icon` and set the icon yourself in
  post-processing.
- Post-process the plist before saving:
  - `WFWorkflowTypes = ['ActionExtension']` if the shortcut should appear in
    the Share Sheet (the library defaults to widget/watch types).
  - `WFWorkflowInputContentItemClasses` — e.g. `WFURLContentItem`,
    `WFTextContentItem`, `WFWebPageContentItem`, `WFSafariWebPageContentItem`,
    `WFLocationContentItem`, as appropriate.
  - `WFWorkflowIcon` — `WFWorkflowIconStartColor` / `WFWorkflowIconEndColor`
    (ARGB int) and `WFWorkflowIconGlyphNumber`.
- The **file name becomes the shortcut's name** on import. Name the file
  exactly what the shortcut should be called.
- Always reload the produced plist and print the action list to verify count,
  order, and parameters before moving on.

## Step 3 — Inspect an existing shared shortcut (when fixing one)

An iCloud share link `https://www.icloud.com/shortcuts/<id>` exposes metadata:

```
GET https://www.icloud.com/shortcuts/api/records/<ID>
```

The JSON gives the shortcut's `name`, icon glyph/color, `signingStatus`, and a
`downloadURL` for the signed file. The signed file is an AEA1 archive — you
generally **cannot** extract the workflow plist from it without Apple's keys,
and the public share page shows no action list. So when fixing someone else's
shortcut: identify it from the metadata, diagnose from the *symptom* and the
input format (ask the user what they feed it and what goes wrong), and rebuild
a corrected equivalent rather than promising to patch the original binary.

## Step 4 — Sign it (ask the user first)

Signing requires sending the file to a third party if you have no Mac. The
file contains only the generic actions you wrote — but still **tell the user
which service you will upload to and get their OK first**.

Working options (as of 2026-11):

- **Shortcuty Sign** — https://sign.shortcuty.app — upload unsigned file,
  download the signed copy. Files are only kept while being signed.
- **RoutineHub HubSign** — RoutineHub's signing tool, also used by the Cherri
  toolchain (`cherri --hubsign`).
- A Mac you control: `shortcuts sign --mode anyone --input in.shortcut
  --output out.shortcut`.

Verify the result: signed files are visibly larger (signature + certificates)
and start with the bytes `AEA1`.

## Step 5 — Deliver and verify on device

- Deliver the **signed** file as an attachment with the exact final name.
- Warn the user to delete any earlier unsigned copy from Files first, so they
  don't tap the wrong one.
- Give one concrete test: a real input they would actually use, the expected
  result, and "send me a screenshot / the input if it's still wrong" — then
  debug from their actual failing input, not from guesses.

## Worked example

`examples/open-in-apple-maps/` is a complete, real build: a Share Sheet
shortcut that opens Google Maps links in Apple Maps. Its original version
opened the wrong place because it parsed the `@lat,lng` viewport centre from
Google URLs instead of the `!3d<lat>!4d<lng>` pin coordinates, and never
expanded `maps.app.goo.gl` short links. The fixed build is a 17-action
no-conditional chain: expand → decode → pin coords → viewport coords →
ll/center/viewpoint params → place name → q/query/destination params →
cleanup → encode → open `https://maps.apple.com/?q=…`.
