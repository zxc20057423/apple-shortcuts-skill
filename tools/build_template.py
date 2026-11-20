#!/usr/bin/env python3
"""
Template for building an unsigned iOS .shortcut file with python-shortcuts.

Usage:
    python3 -m venv .venv && .venv/bin/pip install python-shortcuts
    .venv/bin/python tools/build_template.py "My Shortcut"

The output is UNSIGNED. iOS >= 15 will refuse it until it is signed
(see SKILL.md, Step 4). The file name becomes the shortcut's name on import.
"""
import plistlib
import sys

from shortcuts import Shortcut
from shortcuts.actions import (
    CommentAction,
    ExpandURLAction,
    OpenURLAction,
    SetVariableAction,
    TextAction,
    URLDecodeAction,
    URLEncodeAction,
)
from shortcuts.actions.base import BaseAction, BooleanField, Field


class ReplaceTextAction(BaseAction):
    """Regex find & replace. Missing from python-shortcuts; this is the
    standard serialization Shortcuts expects."""

    itype = "is.workflow.actions.text.replace"
    keyword = "replace_text"

    find = Field("WFReplaceTextFind")
    replace = Field("WFReplaceTextReplace", required=False)
    case_sensitive = BooleanField("WFReplaceTextCaseSensitive", required=False)
    regex = BooleanField("WFReplaceTextRegularExpression", required=False)


def rep(find: str, replace: str) -> ReplaceTextAction:
    return ReplaceTextAction(
        data={"find": find, "replace": replace, "case_sensitive": False, "regex": True}
    )


def build(name: str, actions: list, out_path: str) -> None:
    # plistlib.Data was removed in Python 3.12 and breaks the library's
    # default icon dump; we set the icon in post-processing anyway.
    Shortcut._get_icon = lambda self: {
        "WFWorkflowIconStartColor": 4282601983,
        "WFWorkflowIconGlyphNumber": 61440,
    }

    sc = Shortcut(name=name)
    sc.actions = actions
    with open(out_path, "wb") as f:
        sc.dump(f, file_format="shortcut")

    with open(out_path, "rb") as f:
        data = plistlib.load(f)

    # Share Sheet availability + accepted input types.
    data["WFWorkflowTypes"] = ["ActionExtension"]
    data["WFWorkflowInputContentItemClasses"] = [
        "WFURLContentItem",
        "WFTextContentItem",
        "WFWebPageContentItem",
        "WFSafariWebPageContentItem",
    ]
    data["WFWorkflowIcon"] = {
        "WFWorkflowIconStartColor": 4282601983,
        "WFWorkflowIconEndColor": 4282601983,
        "WFWorkflowIconGlyphNumber": 61440,
    }
    with open(out_path, "wb") as f:
        plistlib.dump(data, f, fmt=plistlib.FMT_BINARY)

    # Verify what we actually wrote.
    with open(out_path, "rb") as f:
        check = plistlib.load(f)
    print(f"{out_path}: {len(check['WFWorkflowActions'])} actions")
    for a in check["WFWorkflowActions"]:
        print(" -", a["WFWorkflowActionIdentifier"])


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "My Shortcut"
    build(
        name,
        actions=[
            CommentAction(data={"text": "Built with the apple-shortcuts-authoring skill."}),
            ExpandURLAction(),
            URLDecodeAction(),
            rep(r"example-pattern", "replacement"),
            URLEncodeAction(),
            SetVariableAction(data={"name": "result"}),
            TextAction(data={"text": "https://example.com/?q={{result}}"}),
            OpenURLAction(),
        ],
        out_path=f"{name}.shortcut",
    )
