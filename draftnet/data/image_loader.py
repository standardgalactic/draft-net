from __future__ import annotations

from dataclasses import dataclass
from typing import List

import torch
from torch.utils.data import Dataset

from draftnet.encoders.image_encoder import ImageStatsEncoder
from draftnet.trajectories.subdivision import dyadic_targets
from draftnet.types import DraftTrajectory
from draftnet.utils.image_ops import read_image_array


@dataclass
class ImageBridgeExample:
    trajectory_id: str
    t_value: float
    z0: list[float]
    zT: list[float]
    zt: list[float]
    target_index: int


class ImageBridgeDataset(Dataset):
    def __init__(self, trajectories: List[DraftTrajectory], embedding_dim: int = 256, curriculum_level: int = 1, bands: int = 4):
        self.encoder = ImageStatsEncoder(embedding_dim=embedding_dim, bands=bands)
        self.examples: List[ImageBridgeExample] = []
        for trajectory in trajectories:
            if trajectory.modality != 'image' or len(trajectory.states) < 3:
                continue
            images = [read_image_array(state.content_path) for state in trajectory.states]
            latents = [self.encoder.encode(image) for image in images]
            z0 = latents[0]
            zT = latents[-1]
            for t_value, idx in dyadic_targets(len(latents), curriculum_level):
                self.examples.append(
                    ImageBridgeExample(
                        trajectory_id=trajectory.trajectory_id,
                        t_value=t_value,
                        z0=z0,
                        zT=zT,
                        zt=latents[idx],
                        target_index=idx,
                    )
                )

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, index: int):
        ex = self.examples[index]
        return {
            'trajectory_id': ex.trajectory_id,
            't': torch.tensor([ex.t_value], dtype=torch.float32),
            'z0': torch.tensor(ex.z0, dtype=torch.float32),
            'zT': torch.tensor(ex.zT, dtype=torch.float32),
            'zt': torch.tensor(ex.zt, dtype=torch.float32),
            'target_index': ex.target_index,
        }
