from __future__ import annotations

from pathlib import Path
from typing import List

from draftnet.types import DraftState, DraftTrajectory
from draftnet.utils.io import read_jsonl, write_jsonl


def save_manifest(path: str, trajectories: List[DraftTrajectory]) -> None:
    write_jsonl(path, [t.to_dict() for t in trajectories])


def load_manifest(path: str | Path) -> List[DraftTrajectory]:
    out: List[DraftTrajectory] = []
    for row in read_jsonl(path):
        states = [DraftState(**s) for s in row["states"]]
        out.append(
            DraftTrajectory(
                trajectory_id=row["trajectory_id"],
                modality=row["modality"],
                source=row["source"],
                states=states,
                metadata=row.get("metadata", {}),
            )
        )
    return out
