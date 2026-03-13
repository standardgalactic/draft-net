"""
rsvp.beats
==========
Beat and scene topology analysis for screenplays and structured prose.

Produces a topology map of the dramatic manifold, identifying:

  Curvature highs   — dramatic turning points, reversals, revelations
  Sink regions      — scenes that absorb tension without release
  Stagnation basins — stretches with minimal scalar/vector change
  Torsion points    — abrupt directional pivots in the narrative field

The output is a compact, terminal-readable topology summary that can be
loaded into Vim split windows for inspection.

Topology map columns:
  # scene index
  Φ  mean scalar density
  S  mean entropy
  |v| mean flow magnitude
  κ  mean curvature
  TYPE  topological classification
"""

from __future__ import annotations
import sys
import json
import argparse
import math
from dataclasses import dataclass
from typing import List, Optional

from .document import Document, Patch
from .metrics import Metrics
from .parser import parse


# ── Beat classification thresholds ───────────────────────────────────────────

CURVATURE_HIGH = 0.35
STAGNATION_MAG = 0.12
SINK_ENTROPY = 2.5
SINK_FLOW = 0.15


@dataclass
class BeatReport:
    index: int
    scene_label: str
    patch_count: int
    mean_scalar: float
    mean_entropy: float
    mean_flow: float
    mean_curvature: float
    beat_type: str          # "pivot" | "sink" | "stagnation" | "drive" | "normal"
    notes: str


def _classify(mean_scalar: float, mean_entropy: float,
              mean_flow: float, mean_curvature: float) -> tuple[str, str]:
    """Return (beat_type, notes)."""
    notes = []
    if mean_curvature > CURVATURE_HIGH:
        return "pivot", f"curvature κ={mean_curvature:.2f}"
    if mean_flow < STAGNATION_MAG:
        notes.append(f"low flow |v|={mean_flow:.2f}")
        if mean_entropy < SINK_ENTROPY:
            return "sink", "; ".join(notes)
        return "stagnation", "; ".join(notes)
    if mean_flow > 0.40:
        return "drive", f"|v|={mean_flow:.2f}"
    notes.append(f"|v|={mean_flow:.2f}")
    return "normal", "; ".join(notes)


def analyse(doc: Document) -> List[BeatReport]:
    """
    Group patches into scene-level beats and compute topology classification.
    """
    m = Metrics()
    reports: List[BeatReport] = []

    # Group patches by scene boundary
    current_scene_label: str = "opening"
    current_scene_patches: List[Patch] = []
    scene_idx = 0

    def flush_scene(label: str, patches: List[Patch], idx: int) -> None:
        if not patches:
            return
        scalars = [m.scalar(p.text) for p in patches]
        entropies = [m.entropy(p.text) for p in patches]
        embeds = [m.embed(p.text) for p in patches]

        flows = []
        for i in range(len(embeds) - 1):
            flows.append(m.displacement(embeds[i], embeds[i + 1]))
        curves = []
        for i in range(1, len(embeds)):
            curves.append(m.displacement(embeds[i], embeds[i - 1]))

        mean_s = sum(scalars) / len(scalars)
        mean_e = sum(entropies) / len(entropies)
        mean_f = sum(flows) / len(flows) if flows else 0.0
        mean_k = sum(curves) / len(curves) if curves else 0.0

        beat_type, notes = _classify(mean_s, mean_e, mean_f, mean_k)
        reports.append(BeatReport(
            index=idx,
            scene_label=label,
            patch_count=len(patches),
            mean_scalar=mean_s,
            mean_entropy=mean_e,
            mean_flow=mean_f,
            mean_curvature=mean_k,
            beat_type=beat_type,
            notes=notes,
        ))

    for patch in doc.patches:
        if patch.kind == "scene_heading":
            flush_scene(current_scene_label, current_scene_patches, scene_idx)
            scene_idx += 1
            current_scene_label = patch.label or patch.text[:60]
            current_scene_patches = []
        else:
            current_scene_patches.append(patch)

    flush_scene(current_scene_label, current_scene_patches, scene_idx)
    return reports


# ── Output formatters ─────────────────────────────────────────────────────────

_TYPE_SYMBOLS = {
    "pivot":      "↻",
    "sink":       "⬇",
    "stagnation": "─",
    "drive":      "→",
    "normal":     "·",
}


def format_terminal(reports: List[BeatReport]) -> str:
    lines = [
        "── BEAT TOPOLOGY MAP ────────────────────────────────────────────────",
        f"  {'#':>3}  {'sym'}  {'Φ':>6}  {'S':>6}  {'|v|':>6}  {'κ':>6}  "
        f"{'TYPE':12}  SCENE",
        "  " + "─" * 80,
    ]
    for r in reports:
        sym = _TYPE_SYMBOLS.get(r.beat_type, " ")
        lines.append(
            f"  {r.index:>3}  {sym}   "
            f"{r.mean_scalar:>6.2f}  {r.mean_entropy:>6.3f}  "
            f"{r.mean_flow:>6.3f}  {r.mean_curvature:>6.3f}  "
            f"{r.beat_type:12}  {r.scene_label[:50]}"
        )
    lines.append("")
    lines.append("Symbols:  → drive   · normal   ↻ pivot   ⬇ sink   ─ stagnation")
    return "\n".join(lines)


def format_json(reports: List[BeatReport]) -> str:
    data = [
        {
            "index": r.index,
            "scene": r.scene_label,
            "patch_count": r.patch_count,
            "mean_scalar": round(r.mean_scalar, 3),
            "mean_entropy": round(r.mean_entropy, 3),
            "mean_flow": round(r.mean_flow, 3),
            "mean_curvature": round(r.mean_curvature, 3),
            "beat_type": r.beat_type,
            "notes": r.notes,
        }
        for r in reports
    ]
    return json.dumps(data, indent=2)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> None:
    p = argparse.ArgumentParser(
        prog="rsvp-beats",
        description="Map beat and scene topology of a screenplay or document.",
    )
    p.add_argument("file", nargs="?")
    p.add_argument("--fmt", choices=["terminal", "json"], default="terminal")
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
    reports = analyse(doc)

    if args.fmt == "json":
        print(format_json(reports))
    else:
        print(format_terminal(reports))


if __name__ == "__main__":
    main()
