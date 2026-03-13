"""
rsvp.persona
============
Character field modeling for screenplays.

Each character is treated as a persistent vector source whose influence
decays with distance from their appearances. The module builds character
signatures, measures voice similarity between characters, and computes
influence fields over the document.

Mathematical basis:

    Character influence at position i:
        I_c(i) = Σ_{p_j ∈ P_c}  exp(−λ |i − j|)

    Voice similarity between characters A and B:
        sim(A, B) = cosine( mean_embed(A), mean_embed(B) )

Diagnostics produced:
  - Characters whose voice signatures are too similar
  - Characters with low identity coherence (high intra-character entropy)
  - Characters whose influence field is dominant but who were intended
    as minor (detected by frequency × magnitude mismatch)
"""

from __future__ import annotations
import sys
import math
import json
import argparse
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .document import Document, Patch
from .metrics import Metrics, cosine_similarity
from .parser import parse


DECAY_LAMBDA = 0.1          # influence decay rate
SIMILARITY_THRESHOLD = 0.90  # cosine similarity above this → voices too similar
COHERENCE_THRESHOLD = 3.5    # entropy above this → low voice coherence


# ── Character profile ─────────────────────────────────────────────────────────

@dataclass
class CharacterProfile:
    name: str
    dialogue_patches: List[Patch] = field(default_factory=list)
    action_patches: List[Patch] = field(default_factory=list)

    # Computed quantities
    mean_embedding: List[float] = field(default_factory=list)
    voice_entropy: float = 0.0
    influence_total: float = 0.0
    patch_indices: List[int] = field(default_factory=list)


def build_profiles(doc: Document) -> Dict[str, CharacterProfile]:
    """
    Extract character profiles from a parsed Document.
    Returns a dict mapping character name → CharacterProfile.
    """
    profiles: Dict[str, CharacterProfile] = {}

    for i, patch in enumerate(doc.patches):
        if patch.kind == "dialogue" and patch.speaker:
            name = patch.speaker
            if name not in profiles:
                profiles[name] = CharacterProfile(name=name)
            profiles[name].dialogue_patches.append(patch)
            profiles[name].patch_indices.append(i)

        elif patch.kind == "action":
            # Heuristic: if a character's name appears in action text,
            # record it as an action presence marker.
            for name, prof in profiles.items():
                if name in patch.text.upper():
                    prof.action_patches.append(patch)

    return profiles


def compute_signatures(profiles: Dict[str, CharacterProfile],
                        metrics: Metrics) -> None:
    """Compute embedding signatures and entropy for each profile."""
    from .metrics import entropy
    from collections import Counter

    for prof in profiles.values():
        all_text = " ".join(p.text for p in prof.dialogue_patches)
        if all_text.strip():
            prof.mean_embedding = metrics.embed(all_text)
            prof.voice_entropy = entropy(all_text)
        else:
            prof.mean_embedding = [0.0] * 16
            prof.voice_entropy = 0.0


def influence_field(profiles: Dict[str, CharacterProfile],
                    doc_length: int,
                    decay: float = DECAY_LAMBDA) -> Dict[str, List[float]]:
    """
    Compute the influence field of each character over the document.
    Returns dict: name → list of float values over [0, doc_length).
    """
    fields: Dict[str, List[float]] = {}
    for name, prof in profiles.items():
        vec = [0.0] * doc_length
        for j in prof.patch_indices:
            for i in range(doc_length):
                vec[i] += math.exp(-decay * abs(i - j))
        prof.influence_total = sum(vec)
        fields[name] = vec
    return fields


# ── Diagnostics ───────────────────────────────────────────────────────────────

@dataclass
class PersonaReport:
    character_count: int
    profiles: Dict[str, CharacterProfile]
    similarity_flags: List[Tuple[str, str, float]]
    coherence_flags: List[Tuple[str, float]]
    dominance_flags: List[Tuple[str, float]]


def analyse(doc: Document,
            similarity_threshold: float = SIMILARITY_THRESHOLD,
            coherence_threshold: float = COHERENCE_THRESHOLD) -> PersonaReport:
    m = Metrics()
    profiles = build_profiles(doc)
    compute_signatures(profiles, m)
    fields = influence_field(profiles, len(doc.patches))

    names = list(profiles.keys())

    # Voice similarity flags
    sim_flags: List[Tuple[str, str, float]] = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            sim = cosine_similarity(
                profiles[a].mean_embedding,
                profiles[b].mean_embedding,
            )
            if sim > similarity_threshold:
                sim_flags.append((a, b, sim))

    # Coherence flags (high intra-character entropy)
    coh_flags = [
        (name, prof.voice_entropy)
        for name, prof in profiles.items()
        if prof.voice_entropy > coherence_threshold
    ]

    # Dominance flags (characters with unexpectedly large influence totals)
    if profiles:
        mean_influence = sum(p.influence_total for p in profiles.values()) / len(profiles)
        dom_flags = [
            (name, prof.influence_total)
            for name, prof in profiles.items()
            if prof.influence_total > mean_influence * 2.5
        ]
    else:
        dom_flags = []

    return PersonaReport(
        character_count=len(profiles),
        profiles=profiles,
        similarity_flags=sim_flags,
        coherence_flags=coh_flags,
        dominance_flags=dom_flags,
    )


# ── Output formatters ─────────────────────────────────────────────────────────

def format_terminal(report: PersonaReport, character: Optional[str] = None) -> str:
    lines = ["── CHARACTER FIELD REPORT ──────────────────────────"]

    profiles = report.profiles
    if character:
        names = [n for n in profiles if character.upper() in n.upper()]
    else:
        names = sorted(profiles.keys())

    for name in names:
        prof = profiles[name]
        lines.append(f"\n  {name}")
        lines.append(f"    dialogue patches : {len(prof.dialogue_patches)}")
        lines.append(f"    voice entropy    : {prof.voice_entropy:.3f}")
        lines.append(f"    influence total  : {prof.influence_total:.2f}")

    if report.similarity_flags:
        lines.append("\n── VOICE SIMILARITY FLAGS ──")
        for a, b, sim in report.similarity_flags:
            lines.append(f"  {a} ↔ {b}  similarity={sim:.3f}  [voices converging]")

    if report.coherence_flags:
        lines.append("\n── LOW COHERENCE FLAGS ──")
        for name, ent in report.coherence_flags:
            lines.append(f"  {name}  entropy={ent:.3f}  [inconsistent voice]")

    if report.dominance_flags:
        lines.append("\n── DOMINANCE FLAGS ──")
        for name, inf in report.dominance_flags:
            lines.append(f"  {name}  influence={inf:.1f}  [unusually large field]")

    return "\n".join(lines)


def format_json(report: PersonaReport) -> str:
    data = {
        "character_count": report.character_count,
        "characters": {
            name: {
                "dialogue_patches": len(prof.dialogue_patches),
                "voice_entropy": round(prof.voice_entropy, 4),
                "influence_total": round(prof.influence_total, 4),
            }
            for name, prof in report.profiles.items()
        },
        "similarity_flags": [
            {"a": a, "b": b, "similarity": round(sim, 4)}
            for a, b, sim in report.similarity_flags
        ],
        "coherence_flags": [
            {"character": n, "entropy": round(e, 4)}
            for n, e in report.coherence_flags
        ],
        "dominance_flags": [
            {"character": n, "influence": round(i, 2)}
            for n, i in report.dominance_flags
        ],
    }
    return json.dumps(data, indent=2)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> None:
    p = argparse.ArgumentParser(
        prog="rsvp-persona",
        description="Analyse character voice fields in a screenplay.",
    )
    p.add_argument("file", nargs="?")
    p.add_argument("--character", "-c", help="Focus on a specific character")
    p.add_argument("--fmt", choices=["terminal", "json"], default="terminal")
    p.add_argument("--similarity-threshold", type=float, default=SIMILARITY_THRESHOLD)
    p.add_argument("--coherence-threshold", type=float, default=COHERENCE_THRESHOLD)
    args = p.parse_args(argv)

    if args.file:
        with open(args.file) as fh:
            text = fh.read()
        source = args.file
    else:
        text = sys.stdin.read()
        source = "<stdin>"

    doc = parse(text, source=source)
    report = analyse(doc,
                     similarity_threshold=args.similarity_threshold,
                     coherence_threshold=args.coherence_threshold)

    if args.fmt == "json":
        print(format_json(report))
    else:
        print(format_terminal(report, character=args.character))


if __name__ == "__main__":
    main()
