from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Literal, Optional

Modality = Literal["text", "code", "latex", "image"]


@dataclass
class DraftState:
    step: int
    content_path: str
    content_hash: str
    timestamp: Optional[str] = None
    author: Optional[str] = None
    latent: Optional[List[float]] = None
    diff_from_prev: Optional[Dict[str, Any]] = None
    rsvp: Optional[Dict[str, float]] = None
    spectral: Optional[Dict[str, Any]] = None
    segmentation: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DraftTrajectory:
    trajectory_id: str
    modality: Modality
    source: str
    states: List[DraftState]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trajectory_id": self.trajectory_id,
            "modality": self.modality,
            "source": self.source,
            "states": [s.to_dict() for s in self.states],
            "metadata": self.metadata,
        }
