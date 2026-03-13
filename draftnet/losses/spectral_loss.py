from __future__ import annotations

import torch


def spectral_loss(pred: torch.Tensor, target: torch.Tensor, weights: torch.Tensor | None = None) -> torch.Tensor:
    diff = (pred - target) ** 2
    if weights is not None:
        diff = diff * weights
    return diff.mean()
