from __future__ import annotations

import torch
from torch import nn


class BridgeMLP(nn.Module):
    def __init__(self, dim: int, hidden_dim: int = 512, dropout: float = 0.1):
        super().__init__()
        self.time_proj = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
        )
        self.net = nn.Sequential(
            nn.Linear(dim * 2 + hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, dim),
        )

    def forward(self, z0: torch.Tensor, zT: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        if t.dim() == 1:
            t = t.unsqueeze(-1)
        te = self.time_proj(t)
        x = torch.cat([z0, zT, te], dim=-1)
        return self.net(x)
