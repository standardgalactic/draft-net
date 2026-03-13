from __future__ import annotations

from typing import Iterable

from draftnet.trajectories.path_metrics import path_error


def path_fidelity(predicted_latents: Iterable[Iterable[float]], target_latents: Iterable[Iterable[float]]) -> dict[str, float]:
    pe = path_error(predicted_latents, target_latents)
    return {"path_error": pe, "path_fidelity": 1.0 / (1.0 + pe)}
