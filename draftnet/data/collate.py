from __future__ import annotations

from typing import Any, Dict, List

import torch


def collate_bridge_batch(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "trajectory_id": [item["trajectory_id"] for item in batch],
        "t": torch.stack([item["t"] for item in batch], dim=0).squeeze(1),
        "z0": torch.stack([item["z0"] for item in batch], dim=0),
        "zT": torch.stack([item["zT"] for item in batch], dim=0),
        "zt": torch.stack([item["zt"] for item in batch], dim=0),
        "target_index": [item["target_index"] for item in batch],
    }
