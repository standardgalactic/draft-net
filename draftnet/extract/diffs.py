from __future__ import annotations

import difflib
from typing import Dict


def unified_diff(prev_text: str, next_text: str, fromfile: str = "prev", tofile: str = "next") -> str:
    return "".join(
        difflib.unified_diff(
            prev_text.splitlines(keepends=True),
            next_text.splitlines(keepends=True),
            fromfile=fromfile,
            tofile=tofile,
        )
    )


def diff_summary(prev_text: str, next_text: str) -> Dict[str, int | str]:
    matcher = difflib.SequenceMatcher(None, prev_text, next_text)
    inserted = 0
    deleted = 0
    replaced = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            inserted += j2 - j1
        elif tag == "delete":
            deleted += i2 - i1
        elif tag == "replace":
            replaced += max(i2 - i1, j2 - j1)
    return {
        "inserted_chars": inserted,
        "deleted_chars": deleted,
        "replaced_chars": replaced,
        "diff": unified_diff(prev_text, next_text),
    }
