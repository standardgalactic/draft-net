from __future__ import annotations

from pathlib import Path

import numpy as np

from draftnet.data.image_loader import ImageBridgeDataset
from draftnet.types import DraftState, DraftTrajectory


def test_image_bridge_dataset(tmp_path: Path) -> None:
    paths = []
    for i in range(5):
        arr = np.full((8, 8, 3), i / 4.0, dtype=np.float32)
        path = tmp_path / f'{i:04d}.npy'
        np.save(path, arr)
        paths.append(path)
    states = [DraftState(step=i, content_path=str(path), content_hash=str(i)) for i, path in enumerate(paths)]
    traj = DraftTrajectory(trajectory_id='paint_001', modality='image', source='test', states=states)
    ds = ImageBridgeDataset([traj], embedding_dim=32, curriculum_level=2)
    assert len(ds) >= 3
    sample = ds[0]
    assert sample['z0'].shape[0] == 32
