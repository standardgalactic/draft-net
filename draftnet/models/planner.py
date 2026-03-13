from __future__ import annotations

from typing import List

import torch


@torch.no_grad()
def replay_bridge(model: torch.nn.Module, z0: torch.Tensor, zT: torch.Tensor, steps: int) -> List[torch.Tensor]:
    outputs: List[torch.Tensor] = []
    for i in range(1, steps):
        t = torch.tensor([[i / steps]], dtype=z0.dtype, device=z0.device)
        outputs.append(model(z0, zT, t))
    return outputs
