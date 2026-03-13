from __future__ import annotations

import torch


def velocity_loss(pred_velocity: torch.Tensor, target_velocity: torch.Tensor) -> torch.Tensor:
    return torch.mean((pred_velocity - target_velocity) ** 2)
