"""
rsvp.rewrite
============
Constrained transformation passes for Documents.

All transforms are named after RSVP-theoretic operations and are
explicitly inspectable. No generative rewriting is performed without
explicit invocation. Each transform returns a modified copy of the
input text together with a diff-compatible annotation.

Available passes:

  lamphrodyne_smooth     — compress entropy spikes by smoothing
                           abrupt vocabulary shifts in action blocks
  redundancy_reduce      — remove exact or near-exact line repetition
                           within a patch (compress_repetition)
  torsion_sharpen        — intensify directional turns by consolidating
                           weak bridging sentences before pivots
  exposition_redistribute— move dense exposition from monologue into
                           shorter interleaved beats
  entropy_bleed_reduce   — normalize unusually heterogeneous vocabulary
                           clusters by replacing rare synonyms with their
                           more locally frequent equivalents

Each pass takes text (str) and keyword parameters, returns (str, str)
where the second element is an annotation describing what changed.
"""

from __future__ import annotations
import re
import sys
import argparse
from typing import Callable, Dict, List, Optional, Tuple
from collections import Counter

from .metrics import entropy as compute_entropy


Transform = Callable[[str], Tuple[str, str]]

WORD = re.compile(r"\w+")
SENTENCE = re.compile(r"(?<=[.!?])\s+")


# ── Individual transforms ─────────────────────────────────────────────────────

def redundancy_reduce(text: str) -> Tuple[str, str]:
    """
    Remove exact duplicate lines from a patch.
    Simplest LamphrodynePass variant.
    """
    lines = text.splitlines()
    seen: set = set()
    result: List[str] = []
    removed = 0
    for line in lines:
        key = line.strip()
        if key and key in seen:
            removed += 1
        else:
            result.append(line)
            if key:
                seen.add(key)
    annotation = f"redundancy_reduce: removed {removed} duplicate line(s)"
    return "\n".join(result), annotation


def lamphrodyne_smooth(text: str, window: int = 3) -> Tuple[str, str]:
    """
    Smooth entropy spikes within a block by merging very short sentences
    with their neighbours. Short dangling clauses often produce high local
    entropy without adding semantic content.

    The 'window' parameter controls minimum sentence word count below which
    a sentence is merged forward.
    """
    sentences = SENTENCE.split(text)
    smoothed: List[str] = []
    changed = 0
    buffer = ""

    for sent in sentences:
        word_count = len(WORD.findall(sent))
        if word_count < window and buffer:
            buffer = buffer.rstrip() + " " + sent.lstrip()
            changed += 1
        else:
            if buffer:
                smoothed.append(buffer)
            buffer = sent

    if buffer:
        smoothed.append(buffer)

    result = " ".join(smoothed)
    annotation = f"lamphrodyne_smooth: merged {changed} short fragment(s)"
    return result, annotation


def entropy_bleed_reduce(text: str,
                          high_freq_floor: int = 2) -> Tuple[str, str]:
    """
    Reduce vocabulary scatter by replacing hapax legomena (words appearing
    only once) with their most frequent synonym-like neighbours (nearest
    token in the local vocabulary by edit distance or frequency class).

    This is a heuristic entropy reduction. In practice a proper
    implementation would use a synonym lexicon or embedding similarity.
    Here we simply flag and optionally strip isolated rare tokens for
    inspection.

    Returns annotated text; actual replacement deferred to caller review.
    """
    tokens = WORD.findall(text.lower())
    counts = Counter(tokens)
    hapaxes = [w for w, c in counts.items() if c == 1 and len(w) > 5]

    annotation = (
        f"entropy_bleed_reduce: found {len(hapaxes)} hapax token(s); "
        f"review: {', '.join(hapaxes[:8])}"
    )
    # Return text unchanged; annotation surfaces candidates for human review
    return text, annotation


def torsion_sharpen(text: str) -> Tuple[str, str]:
    """
    Identify sentences that serve as weak connective tissue before a
    tonal or directional shift, and suggest their removal to sharpen
    the pivot.

    Heuristic: sentences beginning with 'So', 'Well', 'Anyway', 'Look',
    'Right', 'Okay', 'I mean', 'You know' are connective bridges that
    often dilute torsion points.
    """
    HEDGES = re.compile(
        r"^\s*(?:[A-Z ]+:\s*)?"
        r"(So[,\s]|Well[,\s]|Anyway[,\s]|Look[,\s]|Right[,\s]"
        r"|Okay[,\s]|I mean[,\s]|You know[,\s])",
        re.IGNORECASE
    )
    lines = text.splitlines()
    result: List[str] = []
    removed = 0
    for line in lines:
        if HEDGES.match(line):
            removed += 1
        else:
            result.append(line)
    annotation = f"torsion_sharpen: removed {removed} hedging sentence(s)"
    return "\n".join(result), annotation


# ── Transform registry ────────────────────────────────────────────────────────

TRANSFORMS: Dict[str, Transform] = {
    "redundancy_reduce":     redundancy_reduce,
    "lamphrodyne_smooth":    lamphrodyne_smooth,
    "entropy_bleed_reduce":  entropy_bleed_reduce,
    "torsion_sharpen":       torsion_sharpen,
}


def apply_pass(name: str, text: str, **kwargs) -> Tuple[str, str]:
    """Apply a named transform pass to text. Returns (result, annotation)."""
    if name not in TRANSFORMS:
        available = ", ".join(TRANSFORMS.keys())
        raise ValueError(f"Unknown transform {name!r}. Available: {available}")
    fn = TRANSFORMS[name]
    # Pass kwargs only if the function accepts them (simple check)
    try:
        return fn(text, **kwargs)  # type: ignore[call-arg]
    except TypeError:
        return fn(text)


def apply_all(text: str) -> Tuple[str, List[str]]:
    """Apply all transform passes in sequence. Returns (result, [annotations])."""
    annotations: List[str] = []
    result = text
    for name in ["redundancy_reduce", "lamphrodyne_smooth",
                 "torsion_sharpen", "entropy_bleed_reduce"]:
        result, ann = apply_pass(name, result)
        annotations.append(ann)
    return result, annotations


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> None:
    p = argparse.ArgumentParser(
        prog="rsvp-rewrite",
        description="Apply constrained RSVP transform passes to a text passage.",
    )
    p.add_argument("file", nargs="?")
    p.add_argument("--pass", dest="transform",
                   choices=list(TRANSFORMS.keys()) + ["all"],
                   default="all",
                   help="Transform pass to apply")
    p.add_argument("--diff", action="store_true",
                   help="Show diff-style annotation instead of rewritten text")
    args = p.parse_args(argv)

    if args.file:
        with open(args.file) as fh:
            text = fh.read()
    else:
        text = sys.stdin.read()

    if args.transform == "all":
        result, annotations = apply_all(text)
        if args.diff:
            for ann in annotations:
                print(f"  {ann}")
        else:
            print(result)
    else:
        result, annotation = apply_pass(args.transform, text)
        if args.diff:
            print(f"  {annotation}")
        else:
            print(result)


if __name__ == "__main__":
    main()
