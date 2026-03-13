"""
rsvp.entropy
============
Structural entropy analysis for Documents.

Produces per-patch entropy scores and quickfix-compatible output for Vim.
Identifies EntropyPockets — regions of high disorder that are candidates
for revision.

Mathematical basis:
    S_i = −Σ_{w∈V} p(w) log₂ p(w)
    ∇S_i = S_{i+1} − S_i       (entropy gradient)

High S_i: heterogeneous vocabulary, fragmented structure
Low  S_i: repetition, strong thematic unity (can also indicate monotony)
High ∇S_i: abrupt coherence break — prime revision candidate
"""

from __future__ import annotations
import sys
import json
import argparse
from dataclasses import dataclass
from typing import List, Optional

from .document import Document, Patch
from .metrics import Metrics
from .parser import parse


# ── Diagnostics ───────────────────────────────────────────────────────────────

@dataclass
class EntropyReport:
    patch: Patch
    score: float
    gradient: Optional[float]
    flagged: bool
    reason: str


ENTROPY_THRESHOLD = 4.0        # S > this → potentially high disorder
GRADIENT_THRESHOLD = 1.5       # |∇S| > this → abrupt coherence break


def analyse(doc: Document,
            entropy_threshold: float = ENTROPY_THRESHOLD,
            gradient_threshold: float = GRADIENT_THRESHOLD) -> List[EntropyReport]:
    """
    Compute entropy scores for all patches and return a list of reports.
    Patches are flagged if their entropy exceeds the threshold or if the
    entropy gradient to the following patch is large.
    """
    m = Metrics()
    scores = [m.entropy(p.text) for p in doc.patches]
    reports = []

    for i, (patch, score) in enumerate(zip(doc.patches, scores)):
        gradient = None
        flagged = False
        reasons = []

        if score > entropy_threshold:
            flagged = True
            reasons.append(f"high entropy ({score:.2f})")

        if i + 1 < len(scores):
            gradient = scores[i + 1] - score
            if abs(gradient) > gradient_threshold:
                flagged = True
                reasons.append(f"entropy gradient {gradient:+.2f}")

        reports.append(EntropyReport(
            patch=patch,
            score=score,
            gradient=gradient,
            flagged=flagged,
            reason="; ".join(reasons) if reasons else "ok",
        ))

    return reports


# ── Output formatters ─────────────────────────────────────────────────────────

def format_terminal(reports: List[EntropyReport], source: str = "") -> str:
    """Human-readable columnar output with flag markers."""
    lines = []
    for r in reports:
        kind = r.patch.kind
        label = r.patch.label or r.patch.text[:40].replace("\n", " ")
        flag = " *" if r.flagged else "  "
        grad_str = f"  ∇S={r.gradient:+.2f}" if r.gradient is not None else ""
        lines.append(
            f"{flag}  line {r.patch.start + 1:4d}  [{kind:15s}]  "
            f"S={r.score:.3f}{grad_str}  {label[:60]}"
        )
    return "\n".join(lines)


def format_quickfix(reports: List[EntropyReport], source: str) -> str:
    """
    Vim quickfix format:  filename:line:col:message
    Load with :cfile or :cexpr system('rsvp-entropy file.fountain')
    """
    lines = []
    for r in reports:
        if r.flagged:
            lines.append(
                f"{source}:{r.patch.start + 1}:1:{r.reason}"
            )
    return "\n".join(lines)


def format_json(reports: List[EntropyReport]) -> str:
    data = [
        {
            "line": r.patch.start + 1,
            "kind": r.patch.kind,
            "label": r.patch.label,
            "entropy": round(r.score, 4),
            "gradient": round(r.gradient, 4) if r.gradient is not None else None,
            "flagged": r.flagged,
            "reason": r.reason,
        }
        for r in reports
    ]
    return json.dumps(data, indent=2)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> None:
    p = argparse.ArgumentParser(
        prog="rsvp-entropy",
        description="Compute structural entropy over a screenplay or prose document.",
    )
    p.add_argument("file", nargs="?", help="Input file (default: stdin)")
    p.add_argument("--fmt", choices=["terminal", "quickfix", "json"],
                   default="terminal", help="Output format")
    p.add_argument("--threshold", type=float, default=ENTROPY_THRESHOLD,
                   help="Entropy threshold for flagging patches")
    p.add_argument("--gradient-threshold", type=float, default=GRADIENT_THRESHOLD,
                   help="Gradient threshold for flagging transitions")
    p.add_argument("--format", choices=["fountain", "prose", "auto"],
                   default="auto", dest="docfmt")
    args = p.parse_args(argv)

    if args.file:
        with open(args.file) as fh:
            text = fh.read()
        source = args.file
    else:
        text = sys.stdin.read()
        source = "<stdin>"

    doc = parse(text, source=source, fmt=args.docfmt)
    reports = analyse(doc,
                      entropy_threshold=args.threshold,
                      gradient_threshold=args.gradient_threshold)

    if args.fmt == "quickfix":
        print(format_quickfix(reports, source))
    elif args.fmt == "json":
        print(format_json(reports))
    else:
        print(format_terminal(reports, source))


if __name__ == "__main__":
    main()
