from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from draftnet.types import DraftState, DraftTrajectory
from draftnet.utils.hashing import hash_file
from draftnet.utils.image_ops import read_image_array, segmentation_mask, spectral_band_energies


def infer_progress_sequence(paths: Iterable[str | Path]) -> List[Path]:
    seq = [Path(p) for p in paths]
    return sorted(seq, key=lambda p: p.name)


def build_image_trajectory(trajectory_id: str, paths: Iterable[str | Path], source: str = 'progress_shots') -> DraftTrajectory:
    ordered = infer_progress_sequence(paths)
    states: List[DraftState] = []
    for step, path in enumerate(ordered):
        image = read_image_array(path)
        mask = segmentation_mask(image)
        spectral = {'band_energies': spectral_band_energies(image, bands=4)}
        segmentation = {
            'foreground_ratio': float(mask.mean()),
        }
        states.append(
            DraftState(
                step=step,
                content_path=str(path),
                content_hash=hash_file(path),
                spectral=spectral,
                segmentation=segmentation,
                metadata={'filename': path.name},
            )
        )
    return DraftTrajectory(
        trajectory_id=trajectory_id,
        modality='image',
        source=source,
        states=states,
        metadata={'num_states': len(states)},
    )
