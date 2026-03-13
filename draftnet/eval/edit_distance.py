from __future__ import annotations

import difflib


def edit_distance(a: str, b: str) -> float:
    matcher = difflib.SequenceMatcher(None, a, b)
    return 1.0 - matcher.ratio()
