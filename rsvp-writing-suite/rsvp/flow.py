"""
rsvp.flow
=========
Directional vector flow analysis for Documents.

Measures narrative or argumentative motion between adjacent patches.
Identifies stagnation basins (low |v|) and torsion points (high κ).

Mathematical basis:
    v_i     = E(p_i)                    (patch embedding)
    |v_i|   = ‖E(p_{i+1}) − E(p_i)‖   (flow magnitude)
    κ_i     = ‖v_i − v_{i−1}‖          (curvature / direction change)

Stagnation basin  : |v_i| < low_threshold  → scene not advancing
Torsion point     : κ_i > high_threshold   → abrupt directional pivot
Strong flow       : |v_i| > high_threshold → meaningful progression

In screenplay terms:
  - Low  flow magnitude + low entropy  = possibly static or decorative
  - Low  flow magnitude + high entropy = confused / directionless
  - High flow magnitude                = strong narrative momentum
  - High curvature                     = pivot, reversal, revelation
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


# ── Thresholds ────────────────────────────────────────────────────────────────

STAGNATION_THRESHOLD = 0.15     # |v| below this → stagnation basin
TORSION_THRESHOLD = 0.40        # κ above this → torsion point


# ── Diagnostics ───────────────────────────────────────────────────────────────

@dataclass
class FlowReport:
    patch: Patch
    flow_magnitude: float
    curvature: float
    flag: str           # "stagnation" | "torsion" | "strong" | "ok"
    note: str


def analyse(doc: Document,
            stagnation_threshold: float = STAGNATION_THRESHOLD,
            torsion_threshold: float = TORSION_THRESHOLD) -> List[FlowReport]:
    """Compute flow and curvature for all patches and return FlowReports."""
    m = Metrics()
    embeddings = [m.embed(p.text) for p in doc.patches]
    reports = []

    for i, patch in enumerate(doc.patches):
        if i + 1 < len(embeddings):
            mag = m.displacement(embeddings[i], embeddings[i + 1])
        else:
            mag = 0.0

        if i >= 1:
            cur = m.displacement(embeddings[i], embeddings[i - 1])
        else:
            cur = 0.0

        if mag < stagnation_threshold and patch.kind not in ("character", "parenthetical"):
            flag = "stagnation"
            note = f"low flow ({mag:.3f})"
        elif cur > torsion_threshold:
            flag = "torsion"
            note = f"direction change κ={cur:.3f}"
        elif mag > torsion_threshold:
            flag = "strong"
            note = f"strong flow ({mag:.3f})"
        else:
            flag = "ok"
            note = f"flow={mag:.3f}"

        reports.append(FlowReport(
            patch=patch,
            flow_magnitude=mag,
            curvature=cur,
            flag=flag,
            note=note,
        ))

    return reports


# ── Output formatters ─────────────────────────────────────────────────────────

_SYMBOLS = {
    "stagnation": "─",
    "torsion":    "↻",
    "strong":     "→",
    "ok":         "·",
}


def format_terminal(reports: List[FlowReport]) -> str:
    lines = []
    for r in reports:
        sym = _SYMBOLS.get(r.flag, " ")
        label = r.patch.label or r.patch.text[:50].replace("\n", " ")
        lines.append(
            f"  {sym}  line {r.patch.start + 1:4d}  "
            f"[{r.patch.kind:15s}]  {r.note:30s}  {label[:55]}"
        )
    return "\n".join(lines)


def format_quickfix(reports: List[FlowReport], source: str) -> str:
    lines = []
    for r in reports:
        if r.flag in ("stagnation", "torsion"):
            lines.append(f"{source}:{r.patch.start + 1}:1:{r.flag}: {r.note}")
    return "\n".join(lines)


def format_json(reports: List[FlowReport]) -> str:
    data = [
        {
            "line": r.patch.start + 1,
            "kind": r.patch.kind,
            "label": r.patch.label,
            "flow_magnitude": round(r.flow_magnitude, 4),
            "curvature": round(r.curvature, 4),
            "flag": r.flag,
            "note": r.note,
        }
        for r in reports
    ]
    return json.dumps(data, indent=2)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> None:
    p = argparse.ArgumentParser(
        prog="rsvp-flow",
        description="Measure directional flow and curvature across a document.",
    )
    p.add_argument("file", nargs="?")
    p.add_argument("--fmt", choices=["terminal", "quickfix", "json"], default="terminal")
    p.add_argument("--stagnation", type=float, default=STAGNATION_THRESHOLD)
    p.add_argument("--torsion", type=float, default=TORSION_THRESHOLD)
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
                      stagnation_threshold=args.stagnation,
                      torsion_threshold=args.torsion)

    if args.fmt == "quickfix":
        print(format_quickfix(reports, source))
    elif args.fmt == "json":
        print(format_json(reports))
    else:
        print(format_terminal(reports))


if __name__ == "__main__":
    main()
