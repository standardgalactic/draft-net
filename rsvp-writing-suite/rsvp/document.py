"""
rsvp.document
=============
Core document model. A text is represented as a sequence of Patches
forming a Document. Each Patch is a discrete sample of the RSVP field:
scalar density Φ, directional flow v, and entropy S.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Patch:
    """
    A contiguous span of text treated as a local region of the RSVP field.

    Attributes
    ----------
    text        : raw text content of the patch
    start       : line index where the patch begins
    end         : line index where the patch ends (exclusive)
    kind        : semantic role — scene_heading, action, dialogue,
                  character, parenthetical, transition, paragraph, etc.
    label       : optional human-readable identifier (e.g. scene slug)
    speaker     : character name, if kind == 'dialogue'

    RSVP field values (populated by metrics.compute_fields):
    scalar_density  : Φ — semantic weight / information concentration
    vector_flow     : v — embedding displacement to next patch (list of floats)
    entropy         : S — structural disorder (Shannon entropy over tokens)
    flow_magnitude  : |v| — scalar norm of vector_flow
    curvature       : κ — change in flow vector direction from previous patch
    """
    text: str
    start: int
    end: int
    kind: str = "paragraph"
    label: str = ""
    speaker: Optional[str] = None

    scalar_density: Optional[float] = None
    vector_flow: Optional[List[float]] = None
    entropy: Optional[float] = None
    flow_magnitude: Optional[float] = None
    curvature: Optional[float] = None

    def __repr__(self) -> str:
        tag = f"[{self.kind}:{self.label}]" if self.label else f"[{self.kind}]"
        preview = self.text[:60].replace("\n", " ")
        return f"Patch{tag}({preview!r})"


@dataclass
class Document:
    """
    A sequence of Patches representing the full RSVP field of a text.

    Attributes
    ----------
    patches  : ordered list of Patch objects
    source   : original filename or identifier
    metadata : arbitrary key-value metadata (format, title, author, etc.)
    """
    patches: List[Patch]
    source: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def compute_fields(self, metrics) -> None:
        """Populate RSVP field values on all patches using a Metrics object."""
        for patch in self.patches:
            patch.scalar_density = metrics.scalar(patch.text)
            patch.entropy = metrics.entropy(patch.text)

        embeddings = [metrics.embed(p.text) for p in self.patches]
        for i, patch in enumerate(self.patches):
            patch.vector_flow = embeddings[i]
            if i + 1 < len(self.patches):
                patch.flow_magnitude = metrics.displacement(
                    embeddings[i], embeddings[i + 1]
                )
            else:
                patch.flow_magnitude = 0.0

            if i >= 1 and self.patches[i - 1].vector_flow is not None:
                patch.curvature = metrics.displacement(
                    embeddings[i],
                    self.patches[i - 1].vector_flow or [],
                )
            else:
                patch.curvature = 0.0

    def scenes(self) -> List[Patch]:
        return [p for p in self.patches if p.kind == "scene_heading"]

    def dialogue_by_character(self) -> Dict[str, List[Patch]]:
        result: Dict[str, List[Patch]] = {}
        for p in self.patches:
            if p.kind == "dialogue" and p.speaker:
                result.setdefault(p.speaker, []).append(p)
        return result

    def high_entropy_patches(self, threshold: float = 4.0) -> List[Patch]:
        return [p for p in self.patches
                if p.entropy is not None and p.entropy > threshold]

    def weak_flow_patches(self, threshold: float = 0.1) -> List[Patch]:
        return [p for p in self.patches
                if p.flow_magnitude is not None and p.flow_magnitude < threshold]
