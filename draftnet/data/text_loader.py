from __future__ import annotations

from dataclasses import dataclass
from typing import List

import torch
from torch.utils.data import Dataset

from draftnet.encoders.text_encoder import TextStatsEncoder
from draftnet.trajectories.subdivision import dyadic_targets
from draftnet.types import DraftTrajectory
from draftnet.utils.io import read_text


@dataclass
class BridgeExample:
    trajectory_id: str
    t_value: float
    z0: list[float]
    zT: list[float]
    zt: list[float]
    target_index: int


class TextBridgeDataset(Dataset):
    def __init__(self, trajectories: List[DraftTrajectory], embedding_dim: int = 256, curriculum_level: int = 1):
        self.encoder = TextStatsEncoder(embedding_dim=embedding_dim)
        self.examples: List[BridgeExample] = []
        for trajectory in trajectories:
            if len(trajectory.states) < 3:
                continue
            texts = [read_text(state.content_path) for state in trajectory.states]
            latents = [self.encoder.encode(text) for text in texts]
            z0 = latents[0]
            zT = latents[-1]
            for t_value, idx in dyadic_targets(len(latents), curriculum_level):
                self.examples.append(
                    BridgeExample(
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
            "trajectory_id": ex.trajectory_id,
            "t": torch.tensor([ex.t_value], dtype=torch.float32),
            "z0": torch.tensor(ex.z0, dtype=torch.float32),
            "zT": torch.tensor(ex.zT, dtype=torch.float32),
            "zt": torch.tensor(ex.zt, dtype=torch.float32),
            "target_index": ex.target_index,
        }
