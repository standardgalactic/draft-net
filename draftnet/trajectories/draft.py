from __future__ import annotations

from pathlib import Path
from typing import Iterable

from draftnet.types import DraftTrajectory
from draftnet.utils.io import read_text


def trajectory_texts(trajectory: DraftTrajectory) -> Iterable[str]:
    for state in trajectory.states:
        yield read_text(state.content_path)


def trajectory_length(trajectory: DraftTrajectory) -> int:
    return len(trajectory.states)


def trajectory_dir(trajectory: DraftTrajectory) -> Path:
    return Path(trajectory.states[0].content_path).parent
