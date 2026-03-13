from __future__ import annotations

import math
import re
from collections import Counter

WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)
VERBISH_RE = re.compile(r"\b(is|are|was|were|be|being|been|have|has|had|do|does|did|make|made|build|built|move|moved|learn|learned|write|wrote|paint|painted)\b", re.I)


def token_entropy(text: str) -> float:
    tokens = WORD_RE.findall(text.lower())
    if not tokens:
        return 0.0
    counts = Counter(tokens)
    total = len(tokens)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def scalar_density(text: str) -> float:
    tokens = WORD_RE.findall(text)
    if not tokens:
        return 0.0
    avg_len = sum(len(t) for t in tokens) / len(tokens)
    unique_ratio = len(set(t.lower() for t in tokens)) / len(tokens)
    return float(avg_len * unique_ratio)


def vector_flow(text: str) -> float:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return 0.0
    verbish = len(VERBISH_RE.findall(text))
    transitions = sum(1 for ln in lines if ln.endswith(":") or ln.lower().startswith(("therefore", "thus", "then", "next")))
    return float((verbish + transitions) / max(len(lines), 1))


def rsvp_features(text: str) -> dict[str, float]:
    return {
        "phi": scalar_density(text),
        "v": vector_flow(text),
        "s": token_entropy(text),
    }
